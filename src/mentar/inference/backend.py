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

logger = logging.getLogger(__name__)

LLMCall = Callable[[list[dict]], str]

# Tutoring generation defaults (overridable via cfg["generation"]).
_DEFAULT_TEMPERATURE = 0.3
_DEFAULT_MAX_TOKENS = 400
_DEFAULT_TIMEOUT_S = 120.0
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
    # src/mentar/inference/backend.py -> src -> repo root -> config/inference.yaml
    return Path(__file__).resolve().parents[3] / "config" / "inference.yaml"


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

    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"inference config must be a mapping, got {type(raw).__name__}")
    return _expand_env(raw)


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


def _gen_params(cfg: dict) -> dict:
    gen = cfg.get("generation") or {}
    return {
        "temperature": float(gen.get("temperature", _DEFAULT_TEMPERATURE)),
        "max_tokens": int(gen.get("max_tokens", _DEFAULT_MAX_TOKENS)),
        "timeout": float(gen.get("timeout", _DEFAULT_TIMEOUT_S)),
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
                return resp.choices[0].message.content or ""
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
        return resp["choices"][0]["message"]["content"] or ""

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
