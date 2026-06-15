"""Pluggable LLM backend abstraction: generate(prompt, grounding_passages, constraints) -> text.

Primary local backend: llama.cpp (GGUF) — lightest, broadest hardware support (2026-06-15).
Also: vLLM (capable-GPU tier), Ollama (wrapper), Gemini/Claude API (opt-in, parent owns key).
llama.cpp + vLLM both expose OpenAI-compatible endpoints → one provider path (base_url swap).
Spec: docs/SPEC.md §20.1.
"""
