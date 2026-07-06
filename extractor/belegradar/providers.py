"""Swappable LLM providers, the same pattern that carried JobRadar and
CareerRAG: whichever key is present is used, and no provider is ever a hard
dependency of the surrounding code."""

from __future__ import annotations

import json
import os

import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

TIMEOUT = 60


class ProviderError(RuntimeError):
    pass


def complete_json(system: str, user: str) -> tuple[dict, int]:
    """Run a JSON-mode completion on the first configured provider.
    Returns (parsed_json, total_tokens)."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise ProviderError("GROQ_API_KEY is not set")

    last_status = None
    for model in GROQ_MODELS:
        resp = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=TIMEOUT,
        )
        if resp.status_code == 429:
            last_status = 429
            continue  # per-model limits: try the next one
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        try:
            return json.loads(content), tokens
        except json.JSONDecodeError as exc:
            raise ProviderError(f"{model} returned invalid JSON: {exc}") from exc
    raise ProviderError(f"all providers rate limited (last status {last_status})")
