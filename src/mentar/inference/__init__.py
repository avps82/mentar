"""Pluggable LLM backend abstraction: generate(prompt, grounding_passages, constraints) -> text.

Default backend: local Ollama. Opt-in: own vLLM cluster, Gemini API, Claude API (parent owns key).
Spec: docs/SPEC.md §20.1.
"""
