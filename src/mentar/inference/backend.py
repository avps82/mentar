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
    openai | claude (opt-in cloud, parent-consent-gated) -> same client, provider hosts
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


# The top-level keys a setup write OWNS: the selector and every backend block.
# Anything else in an existing file was put there by the user and is none of
# setup's business — see write_inference_config. _CLOUD_BACKENDS is defined
# further down, so it is unioned in at call time rather than here.
_LOCAL_BACKEND_KEYS = frozenset({"llamacpp", "vllm", "ollama", "gemini"})


def write_inference_config(cfg: dict, path: str | Path | None = None) -> Path:
    """Write an inference config (the inverse of load_inference_config).

    Used by `mentar setup` to materialise the chosen backend/model. Does NOT expand
    ${VAR} — values are written verbatim. Returns the path written.

    MERGES rather than overwrites (2026-09-03). This used to be a plain write of
    whatever the caller passed, and callers pass exactly {backend, <one block>} --
    so every pass through /setup, the Settings backend switch, or `mentar setup`
    silently deleted the rest of the file. Two blocks that really live there:

      * ``grounding:`` -- without its ``sources:`` map resolve_grounding returns
        "" even with zim_dir set, so ZIM grounding just stopped working, quietly.
      * ``generation:`` -- max_tokens fell back to DEFAULT_MAX_TOKENS (1200) from
        a configured 512, so explanations more than doubled in length.

    Neither failure says anything in a log. Measured by changing the model in the
    web form and watching both blocks disappear.

    Backend blocks are still replaced, not merged: setup asks the family to pick
    ONE, so leaving the previous backend's settings behind would be the surprise.
    """
    import yaml
    out = Path(path) if path else _default_config_path()
    out.parent.mkdir(parents=True, exist_ok=True)

    merged = dict(cfg)
    if out.exists():
        # RAW read, deliberately NOT load_inference_config: that expands ${VAR},
        # and writing the result back would bake a real API key into a file whose
        # whole convention is that secrets stay in .env as references.
        try:
            existing = yaml.safe_load(out.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001 — an unreadable config must not block setup
            existing = {}
        if isinstance(existing, dict):
            owned = _LOCAL_BACKEND_KEYS | _CLOUD_BACKENDS | {"backend"}
            for key, value in existing.items():
                if key in owned:
                    continue
                merged.setdefault(key, value)

    out.write_text(yaml.safe_dump(merged, sort_keys=False, default_flow_style=False), encoding="utf-8")
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
    # This file holds live API keys. The default 0644 lets any other account on
    # a shared family computer read them (measured 2026-08-28) -- 0600 it.
    # Best-effort: some filesystems (Windows/FAT/network mounts) do not support
    # POSIX modes, and failing to write the key there would be the worse bug.
    try:
        os.chmod(env_path, 0o600)
    except OSError:  # pragma: no cover - platform/filesystem dependent
        logger.debug("could not chmod %s to 0600 (filesystem may not support it)", env_path)


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


# Opt-in cloud backends (SPEC §20.1, SAFETY §4.5). Both speak OpenAI-style
# chat completions: `claude` rides Anthropic's OpenAI-compatible surface, so no
# second protocol path exists. Gated on a recorded parent acknowledgment — see
# mentar.consent — because turns leave the device under the PARENT's account.
_CLOUD_DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "claude": "https://api.anthropic.com/v1/",
}
# openai_chatgpt is cloud (so: consent-gated) but speaks its OWN protocol at a
# fixed host -- no base_url to resolve, and it never reaches _make_openai_call.
_CLOUD_BACKENDS = frozenset({*_CLOUD_DEFAULT_BASE_URLS, "openai_chatgpt"})


def _resolve_http(backend: str, block: dict) -> dict:
    """Return {base_url, api_key, model} for an OpenAI-compatible backend."""
    if backend in _CLOUD_BACKENDS:
        # No forgiving defaults here, unlike the local branches below: a wrong
        # fallback model would silently BILL the parent's account, and a
        # missing key expands to "" (unset ${VAR} -- _expand_env) which would
        # only fail later with a bare 401.  Fail at resolve time, by name.
        model = block.get("model")
        if not model:
            raise ValueError(
                f"cloud backend '{backend}' needs an explicit model: in its config "
                "block — there is no safe default for a billed account"
            )
        env_var = "OPENAI_API_KEY" if backend == "openai" else "ANTHROPIC_API_KEY"
        api_key = block.get("api_key")
        if not api_key:
            raise ValueError(
                f"cloud backend '{backend}' has no api_key — set {env_var} in "
                "config/.env (re-run setup), or the provider will reject every call"
            )
        return {
            "base_url": block.get("base_url") or _CLOUD_DEFAULT_BASE_URLS[backend],
            "api_key": api_key,
            "model": model,
        }
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
    llamacpp mode (no HTTP endpoint to probe) and for unknown backends."""
    backend = (cfg.get("backend") or "llamacpp").lower()
    block = cfg.get(backend) or {}
    if not isinstance(block, dict):
        return None
    if backend == "llamacpp" and block.get("mode", "server") == "in_process":
        return None
    if backend == "openai_chatgpt":
        return None  # its own protocol at a fixed host — nothing OpenAI-compat to probe
    if backend in _CLOUD_BACKENDS:
        # A misconfigured cloud block (missing model/key) raises in
        # _resolve_http where a CALL is being built; here the caller is a
        # status page asking "is there an endpoint to probe" — for that
        # question a block that cannot resolve is honestly "no".
        try:
            return _resolve_http(backend, block)
        except ValueError:
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
    from openai import APITimeoutError, AuthenticationError, OpenAI  # hard dependency

    # Credential-provider seam: a static key builds the client exactly once (the
    # provider always returns the same string), while a rotating credential (a
    # future subscription token) transparently gets a fresh client the moment
    # its provider returns a new value.  Token-keyed, so we never rebuild per
    # call and never hold a stale credential.
    provider = endpoint.get("api_key_provider") or (lambda: endpoint["api_key"])
    _cache: dict = {"token": None, "client": None}

    def _client() -> OpenAI:
        tok = provider()
        if tok != _cache["token"]:
            _cache["client"] = OpenAI(
                base_url=endpoint["base_url"], api_key=tok, timeout=gen["timeout"],
            )
            _cache["token"] = tok
        return _cache["client"]

    _client()  # build eagerly: config errors fail at factory time, as before

    model = endpoint["model"]
    temperature = gen["temperature"]
    max_tokens = gen["max_tokens"]
    retries = gen["retries"]
    extra_body = gen["extra_body"] or None

    def call(messages: list[dict]) -> str:
        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            try:
                resp = _client().chat.completions.create(
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
            except AuthenticationError as exc:
                # 401 is deterministic: the credential is wrong/expired and a
                # retry sends the identical credential again.  Name the remedy —
                # this surfaces on /setup, /settings/llm-status and `mentar
                # setup` verify (the child-facing path degrades to "" upstream).
                raise RuntimeError(
                    f"the credential for {endpoint['base_url']} was rejected "
                    f"(model={model}). Re-run setup (/setup or `mentar setup`) "
                    "with a valid key."
                ) from exc
            except APITimeoutError as exc:
                # A timeout is NOT transient on a local backend: the model is
                # simply slower than the deadline, so a retry spends the same
                # minutes over again for the same outcome.
                #
                # It also breaks a guarantee elsewhere. Retrying makes one turn
                # take timeout x (retries+1) -- up to 22 min at max_tokens=2048 --
                # while a child's stop waits only timeout+5s
                # (web/app.py:_stop_wait_seconds). The stop would be silently
                # dropped again, which is the exact bug that derivation was added
                # to fix. Failing on the first timeout keeps a turn bounded by the
                # timeout, which is what the stop is derived from.
                raise RuntimeError(
                    f"LLM endpoint {endpoint['base_url']} (model={model}) did not answer "
                    f"within {gen['timeout']:.0f}s. Not retried: a timeout here means the "
                    "model is slower than the budget, not that the call was unlucky. Use a "
                    "smaller model (mentar setup --model gemma2-9b) or lower "
                    "generation.max_tokens."
                ) from exc
            except Exception as exc:  # network/5xx — retry a couple times
                last_exc = exc
                if attempt < retries:
                    time.sleep(_RETRY_BACKOFF_S * (attempt + 1))
                    logger.warning("llm_call retry %d/%d: %s", attempt + 1, retries, exc)
        # A 429 on a cloud account is not "unreachable" — it is the PARENT's
        # plan hitting its usage cap, and saying "unreachable" sends them
        # debugging their network instead of their subscription.
        from openai import RateLimitError
        if isinstance(last_exc, RateLimitError):
            raise RuntimeError(
                f"the provider at {endpoint['base_url']} rate-limited this account "
                f"(model={model}). This is a usage/rate cap on the account's plan, "
                "not a Mentar fault — wait a while, or raise the plan's limits."
            ) from last_exc
        raise RuntimeError(
            f"LLM endpoint {endpoint['base_url']} (model={model}) unreachable after "
            f"{retries + 1} attempt(s): {last_exc}"
        ) from last_exc

    return call


def fold_system_messages(messages: list[dict]) -> list[dict]:
    """Merge system content into the first user turn.

    gemma-2's embedded chat template (and others) raises ValueError("System role
    not supported") at PROMPT-RENDER time — so via the in-process llama-cpp path
    every real tutoring turn failed while Ollama, which rewrites the system turn
    itself, hid the same limitation (found 2026-08-26, fresh-install run: the
    child only ever saw the deterministic fallback scaffolds). Folding is what
    Ollama effectively does; doing it here makes the shipped prompts work on any
    template.
    """
    sys_text = "\n\n".join(
        m.get("content") or "" for m in messages if m.get("role") == "system"
    ).strip()
    rest = [dict(m) for m in messages if m.get("role") != "system"]
    if not sys_text:
        return rest
    for m in rest:
        if m.get("role") == "user":
            m["content"] = f"{sys_text}\n\n{m.get('content') or ''}"
            break
    else:
        rest.insert(0, {"role": "user", "content": sys_text})
    return rest


def _chat_with_system_fold(create, messages: list[dict], state: dict, **kw):
    """Call ``create`` (create_chat_completion-shaped); if the model's template
    rejects the system role, fold and retry ONCE, then keep folding for the rest
    of the process. The rejection happens during template rendering — before any
    generation — so the retry costs milliseconds, not a second generation."""
    msgs = fold_system_messages(messages) if state.get("fold") else messages
    try:
        return create(messages=msgs, **kw)
    except ValueError as exc:
        if state.get("fold") or "system role" not in str(exc).lower():
            raise
        state["fold"] = True
        logger.warning(
            "llm_call: this model's chat template rejects the system role — "
            "folding system text into the first user turn from now on"
        )
        return create(messages=fold_system_messages(messages), **kw)


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

    state: dict = {"fold": False}

    def call(messages: list[dict]) -> str:
        resp = _chat_with_system_fold(
            llm.create_chat_completion,
            messages,
            state,
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

    if backend in _CLOUD_BACKENDS:
        # Enforced HERE, at the one chokepoint every path funnels through, so a
        # hand-edited yaml cannot switch a child's sessions to the cloud without
        # the SAFETY §4.5 parent acknowledgment ever having been made.
        from mentar.consent import has_cloud_consent

        def _require_consent() -> None:
            if not has_cloud_consent(backend):
                raise RuntimeError(
                    f"cloud backend '{backend}' is configured but no parent "
                    "acknowledgment is recorded — open /setup (or run `mentar "
                    "setup`) and complete the cloud consent step"
                )

        _require_consent()          # fail fast at setup/verify time
        if backend == "openai_chatgpt":
            from mentar.inference.codex_backend import make_codex_call
            inner = make_codex_call(block, gen)
        else:
            inner = _make_openai_call(_resolve_http(backend, block), gen)

        # ...and again on EVERY call. Checking only here would make the gate
        # one-directional: enabling a cloud backend is gated, but a parent who
        # REVOKES mid-session would keep sending their child's turns to the
        # provider, because a live SessionController holds this callable for the
        # whole session (measured 2026-08-29). Re-reading a small local YAML per
        # turn is free next to a multi-second model call.
        def gated(messages: list[dict]) -> str:
            _require_consent()
            return inner(messages)

        return gated

    if backend in ("llamacpp", "vllm", "ollama"):
        return _make_openai_call(_resolve_http(backend, block), gen)

    if backend == "gemini":
        raise NotImplementedError(
            "backend 'gemini' is not wired; use openai / claude (opt-in cloud) "
            "or llamacpp / vllm / ollama (local)"
        )

    raise ValueError(f"unknown inference backend: {backend!r}")
