"""Inference backend — the single place Mentar turns config into an ``llm_call``.

Thin owned wrapper over a focused lib (the OpenAI-compatible ``openai`` client),
swappable in one file.  Same architectural shape as the libzim grounding reader and
the planned ``serde`` wrapper: import the lib that does the hard thing, own only the
thin glue, and route the whole codebase through one module so the backend swaps in a
single place.

Public API
----------
    load_inference_config(path=None) -> dict | None
    make_llm_call(cfg) -> Callable[[list[dict]], str]

The returned callable matches ``SessionController(llm_call=...)`` exactly:
it takes OpenAI-style ``messages`` and returns the assistant text.

Backends (``cfg["backend"]``)
-----------------------------
    llamacpp (mode="server") | vllm | ollama  -> OpenAI-compatible HTTP (openai client)
    llamacpp (mode="in_process")              -> llama-cpp-python (lazy optional import)
    gemini | claude                           -> opt-in cloud (not wired for the local pilot)

All three HTTP backends share ONE provider path — only ``base_url`` / ``api_key`` /
``model`` differ.  That is the same OpenAI-compatible path used by the NIAH eval and
the eval-host proxy.

Spec: docs/SPEC.md §20.1.  Config schema: config/inference.example.yaml.
"""

from __future__ import annotations

import logging
import os
import re
import time
from collections.abc import Callable
from pathlib import Path

from mentar.paths import config_path

logger = logging.getLogger(__name__)

LLMCall = Callable[[list[dict]], str]

# Tutoring generation defaults (overridable via cfg["generation"]).
_DEFAULT_TEMPERATURE = 0.3
# 400 -> 1200 (2026-08-19): the Help templates legitimately produce long output
# -- a story, then per-choice analysis -- and 400 truncated a real science
# explanation MID-LIST on the maintainer's machine ("2." was the final line a
# child saw). The verifier, not brevity, is the safety mechanism; the cap only
# needs to bound runaway generation, not shape the prose.
DEFAULT_MAX_TOKENS = 1200


class ReasoningOnlyReply(RuntimeError):
    """The server returned a reasoning model's chain-of-thought and NO answer.

    Ollama's OpenAI-compatible /v1 puts hidden reasoning in a non-standard
    `reasoning` field, leaves `content` empty, and IGNORES think=false -- so the
    setting meant to suppress it does nothing. Deterministic, so never retried.
    """
_DEFAULT_TIMEOUT_S = 120.0
# A flat 120s is a REMOTE-API assumption. Local throughput is bounded by memory
# bandwidth, not the network: measured 7.25 tok/s for a 12B on a base M1 (8.0 GB
# resident, ~58 GB/s achieved, 100% GPU -- i.e. the hardware ceiling, nothing
# misconfigured). At that rate the 1200-token budget needs ~166s, so EVERY
# full-length reply timed out, then retried twice: ~6 min of waiting to fail.
# So derive the floor from the budget we actually allow, at a conservative
# tokens/sec. An explicit generation.timeout still wins.
_SLOW_LOCAL_TOKENS_PER_S = 5.0
_TIMEOUT_OVERHEAD_S = 30.0        # prompt eval + first-token latency + load
_DEFAULT_RETRIES = 2          # total attempts = retries + 1
_RETRY_BACKOFF_S = 1.5

_ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


# ── Config loading ──────────────────────────────────────────────────────────────

def _expand_env(obj):
    """Recursively expand ``${VAR}`` references using the process environment.

    Unset variables expand to the empty string (matching shell ``${VAR}`` semantics
    when unset), so a missing optional token never crashes startup.
    """
    if isinstance(obj, str):
        return _ENV_RE.sub(lambda m: os.environ.get(m.group(1), ""), obj)
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(v) for v in obj]
    return obj


def _default_config_path() -> Path:
    # Written by `mentar setup` and the backend switch, so it follows data_dir():
    # the repo root from a checkout, the user's data directory in a packaged build.
    return config_path()


def write_inference_config(cfg: dict, path: str | Path | None = None) -> Path:
    """Write an inference config (the inverse of load_inference_config).

    Used by `mentar setup` to materialise the chosen backend/model. Does NOT expand
    ${VAR} — values are written verbatim. Returns the path written.
    """
    import yaml
    out = Path(path) if path else _default_config_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False), encoding="utf-8")
    return out


def upsert_dotenv_value(env_path: str | Path, key: str, value: str) -> None:
    """Write/replace ONE KEY=VALUE line in a gitignored .env file -- never
    touches any other line, creates the file if it doesn't exist yet.
    Write-side counterpart to _load_dotenv above. Shared by the web /setup
    route and the `mentar setup` CLI's remote-API path (R9) -- one place
    for anything that touches a credential file, not two independently-
    maintained copies."""
    env_path = Path(env_path)
    # A newline in the value used to write a TWO-line entry, and the second line
    # then survived every later upsert: the replace step drops only the line
    # starting with "KEY=", so the continuation was stranded in .env forever
    # (found 2026-08-18). Two consequences, the second worse than the first:
    # _load_dotenv read the key back TRUNCATED at the newline, so the backend
    # failed to authenticate and looked like a broken gateway; and a fragment of
    # the old SECRET stayed in the file even after the key was rotated.
    #
    # Rejected rather than silently trimmed at the newline -- writing a
    # half-secret that reads back as a plausible-looking key is the failure mode
    # worth preventing, and both callers pass a value a human just pasted.
    value = str(value).strip()
    if "\n" in value or "\r" in value:
        raise ValueError(
            f"{key} contains a line break — paste the value on one line "
            f"(a multi-line value corrupts the .env file)"
        )
    # The directory may not exist yet. From a source checkout `config/` is in the
    # repo so this never came up; in a packaged build the data directory starts
    # empty, and /setup crashed with FileNotFoundError on a real Windows machine.
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    prefix = f"{key}="
    kept = [line for line in lines if not line.strip().startswith(prefix)]
    kept.append(f'{key}="{value}"')
    env_path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def load_inference_config(path: str | Path | None = None) -> dict | None:
    """Load and ``${VAR}``-expand the inference config.

    - explicit ``path`` that is missing -> FileNotFoundError (caller asked for it).
    - ``path=None`` -> try ``<repo>/config/inference.yaml``; return ``None`` if absent
      so callers can fall back to environment defaults.
    """
    explicit = path is not None
    cfg_path = Path(path) if explicit else _default_config_path()
    if not cfg_path.exists():
        if explicit:
            raise FileNotFoundError(f"inference config not found: {cfg_path}")
        return None

    import yaml  # local import: only needed when a config file exists

    # Load a gitignored .env next to the config FIRST, so ${VAR} references in the
    # config resolve from it — secrets persist in a local file, not a shell export.
    _load_dotenv(cfg_path.parent / ".env")

    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"inference config must be a mapping, got {type(raw).__name__}")
    return _expand_env(raw)


def _load_dotenv(env_path: Path) -> None:
    """Load ``KEY=VALUE`` lines from a gitignored ``.env`` into the process env.

    Persists secrets (e.g. ``MENTAR_VLLM_API_KEY``) in a local file rather than a
    shell ``export`` that dies with the terminal. Does NOT override variables that
    are already set, so a real environment value still wins. Tolerant format:
    blank lines and ``#`` comments skipped; an optional ``export`` prefix and
    surrounding quotes are stripped.
    """
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, sep, val = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, val)


# ── Endpoint resolution ───────────────────────────────────────────────────────

def _normalize_base_url(url: str) -> str:
    """Ollama's native port serves OpenAI-compat under /v1; tolerate a bare base."""
    url = url.rstrip("/")
    if not url.endswith("/v1"):
        url = url + "/v1"
    return url


def _resolve_http(backend: str, block: dict) -> dict:
    """Return {base_url, api_key, model} for an OpenAI-compatible backend."""
    if backend == "ollama":
        base_url = _normalize_base_url(block.get("base_url") or "http://localhost:11434")
    else:  # llamacpp(server) / vllm — already include /v1 in the example config
        base_url = block.get("base_url") or "http://localhost:8080/v1"
    return {
        "base_url": base_url,
        "api_key": block.get("api_key") or "no-key",   # local servers accept any token
        "model": block.get("model") or "local-model",
    }


def resolve_http_endpoint(cfg: dict) -> dict | None:
    """{base_url, api_key, model} for the HTTP endpoint ``make_llm_call(cfg)``
    would actually hit -- ONE source of truth for "which server is my model
    on", whether the config points local or remote (used by the web settings
    page's reachability check, so it always tests the endpoint the app really
    calls, never a parallel set of defaults). Returns None for the in-process
    llamacpp mode (no HTTP endpoint to probe) and for unknown/cloud backends."""
    backend = (cfg.get("backend") or "llamacpp").lower()
    block = cfg.get(backend) or {}
    if not isinstance(block, dict):
        return None
    if backend == "llamacpp" and block.get("mode", "server") == "in_process":
        return None
    if backend in ("llamacpp", "vllm", "ollama"):
        return _resolve_http(backend, block)
    return None


def _timeout_for(max_tokens: int) -> float:
    """Enough wall-clock for `max_tokens` to actually be produced on slow local
    hardware, never below the old remote default."""
    return max(_DEFAULT_TIMEOUT_S,
               max_tokens / _SLOW_LOCAL_TOKENS_PER_S + _TIMEOUT_OVERHEAD_S)


def _gen_params(cfg: dict) -> dict:
    gen = cfg.get("generation") or {}
    max_tokens = int(gen.get("max_tokens", DEFAULT_MAX_TOKENS))
    return {
        "temperature": float(gen.get("temperature", _DEFAULT_TEMPERATURE)),
        "max_tokens": max_tokens,
        "timeout": float(gen.get("timeout", _timeout_for(max_tokens))),
        "retries": int(gen.get("retries", _DEFAULT_RETRIES)),
        # Passthrough for non-standard request fields (e.g. {"think": false} to disable
        # a reasoning model's hidden chain-of-thought — see config/inference.example.yaml).
        "extra_body": dict(gen.get("extra_body") or {}),
    }


# ── Backend factories ─────────────────────────────────────────────────────────

def _make_openai_call(endpoint: dict, gen: dict) -> LLMCall:
    from openai import OpenAI  # already a hard dependency

    client = OpenAI(
        base_url=endpoint["base_url"],
        api_key=endpoint["api_key"],
        timeout=gen["timeout"],
    )
    model = endpoint["model"]
    temperature = gen["temperature"]
    max_tokens = gen["max_tokens"]
    retries = gen["retries"]
    extra_body = gen["extra_body"] or None

    def call(messages: list[dict]) -> str:
        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_body=extra_body,
                )
                choice = resp.choices[0]
                # finish_reason == "length" is the backend saying, definitively,
                # "I was cut off by max_tokens". Discarding it is how a stump
                # like "Because a" reached a child with every heuristic
                # downstream guessing (2026-08-19). Named loudly here; the
                # controller's _trim_truncated_tail cleans the visible text.
                if getattr(choice, "finish_reason", None) == "length":
                    logger.warning(
                        "llm_call: output TRUNCATED at max_tokens=%d — raise "
                        "generation.max_tokens in the inference config", max_tokens,
                    )
                content = choice.message.content or ""
                if not content:
                    # A reasoning model emits hidden reasoning FIRST, then the
                    # answer. Ollama's /v1 puts that reasoning in a non-standard
                    # field and leaves `content` empty, so `or ""` handed the
                    # child silence. The reasoning text is the model's
                    # scratchpad, NOT an answer, so it is never shown -- but its
                    # presence, plus finish_reason, names which fault this is:
                    #
                    #   length -> reasoning was CUT OFF before the answer began.
                    #             More budget can genuinely fix this.
                    #   stop   -> the model finished and still said nothing.
                    #             Budget will not help; the model is unusable here.
                    #
                    # Measured 2026-08-25 (gemma4:12b, Ollama /v1): think=false
                    # and think=true were identical, so the flag that is supposed
                    # to prevent all of this is ignored on that server.
                    reasoning = (getattr(choice.message, "reasoning", None)
                                 or getattr(choice.message, "reasoning_content", None))
                    if reasoning:
                        why = getattr(choice, "finish_reason", None)
                        if why == "length":
                            raise ReasoningOnlyReply(
                                f"model {model!r} spent all {max_tokens} tokens on hidden "
                                f"reasoning ({len(reasoning)} chars) and was cut off before "
                                "writing an answer. Raise generation.max_tokens, or use a "
                                "non-reasoning model (mentar setup --model gemma2-9b). "
                                "think=false does not help: Ollama's /v1 ignores it."
                            )
                        raise ReasoningOnlyReply(
                            f"model {model!r} finished (finish_reason={why!r}) having written "
                            f"{len(reasoning)} chars of hidden reasoning and an EMPTY answer. "
                            "More tokens will NOT help. Use a non-reasoning model "
                            "(mentar setup --model gemma2-9b)."
                        )
                return content
            except ReasoningOnlyReply:
                raise  # deterministic — retrying just burns another slow call
            except Exception as exc:  # network/5xx/timeout — retry a couple times
                last_exc = exc
                if attempt < retries:
                    time.sleep(_RETRY_BACKOFF_S * (attempt + 1))
                    logger.warning("llm_call retry %d/%d: %s", attempt + 1, retries, exc)
        raise RuntimeError(
            f"LLM endpoint {endpoint['base_url']} (model={model}) unreachable after "
            f"{retries + 1} attempt(s): {last_exc}"
        ) from last_exc

    return call


def _make_in_process_call(block: dict, gen: dict) -> LLMCall:
    try:
        from llama_cpp import Llama  # optional dependency
    except ImportError as exc:  # pragma: no cover - env-dependent
        raise RuntimeError(
            "llamacpp mode='in_process' needs llama-cpp-python "
            "(pip install llama-cpp-python)"
        ) from exc

    model_path = block.get("model_path")
    if not model_path:
        raise ValueError("llamacpp in_process requires 'model_path' (the .gguf file)")

    llm = Llama(
        model_path=model_path,
        n_ctx=int(block.get("n_ctx", 8192)),
        n_gpu_layers=int(block.get("n_gpu_layers", 0)),
        verbose=False,
    )
    temperature = gen["temperature"]
    max_tokens = gen["max_tokens"]

    def call(messages: list[dict]) -> str:
        resp = llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = resp["choices"][0]
        if choice.get("finish_reason") == "length":
            logger.warning(
                "llm_call: output TRUNCATED at max_tokens=%d — raise "
                "generation.max_tokens in the inference config", max_tokens,
            )
        return choice["message"]["content"] or ""

    return call


def make_llm_call(cfg: dict) -> LLMCall:
    """Build the ``llm_call`` callable the SessionController expects, from config.

    ``cfg`` is the parsed inference config (see config/inference.example.yaml).
    Dispatches on ``cfg["backend"]``.
    """
    backend = (cfg.get("backend") or "llamacpp").lower()
    block = cfg.get(backend) or {}
    if not isinstance(block, dict):
        raise ValueError(f"config block for backend '{backend}' must be a mapping")
    gen = _gen_params(cfg)

    if backend == "llamacpp" and block.get("mode", "server") == "in_process":
        return _make_in_process_call(block, gen)

    if backend in ("llamacpp", "vllm", "ollama"):
        return _make_openai_call(_resolve_http(backend, block), gen)

    if backend in ("gemini", "claude"):
        raise NotImplementedError(
            f"backend '{backend}' is opt-in cloud and not wired for the local pilot; "
            "use llamacpp / vllm / ollama"
        )

    raise ValueError(f"unknown inference backend: {backend!r}")
