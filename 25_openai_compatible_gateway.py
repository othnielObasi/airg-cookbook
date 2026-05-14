#!/usr/bin/env python3
"""
Recipe 25 - OpenAI-Compatible AIRG Gateway
=========================================
Call AIRG's OpenAI-compatible gateway surface instead of calling a model
provider directly.

This governs model traffic before it reaches the upstream provider. It is
useful when an enterprise wants a drop-in /v1/chat/completions path while
keeping AIRG receipts, traces, decision headers, and model allowlists.

    pip install httpx
    export GOVERNOR_API_KEY="<your AIRG account API key>"
    export AIRG_GATEWAY_URL=https://gateway.airg.nov-tia.com
    python 25_openai_compatible_gateway.py
"""
from __future__ import annotations

import os
from pprint import pprint

import httpx


GATEWAY_URL = os.getenv("AIRG_GATEWAY_URL", "https://gateway.airg.nov-tia.com").rstrip("/")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")
MODEL = os.getenv("AIRG_LLM_MODEL", "airg-governed-demo")


def headers() -> dict[str, str]:
    if not API_KEY:
        raise SystemExit("Set GOVERNOR_API_KEY before running this recipe.")
    return {
        "Authorization": f"Bearer {API_KEY}",
        "X-API-Key": API_KEY,
        "X-AIRG-Agent-Id": "cookbook-llm-gateway-agent",
        "X-AIRG-Session-Id": "cookbook-llm-gateway-session",
        "Content-Type": "application/json",
    }


def show(resp: httpx.Response) -> None:
    print(f"HTTP {resp.status_code}")
    for name in (
        "x-airg-decision",
        "x-airg-risk-score",
        "x-airg-policy-ids",
        "x-airg-action-id",
        "x-airg-evidence-hash",
    ):
        if name in resp.headers:
            print(f"  {name}: {resp.headers[name]}")
    try:
        pprint(resp.json())
    except Exception:
        print(resp.text[:1000])


def main() -> None:
    print("OpenAI-Compatible AIRG Gateway")
    print("=" * 72)

    print("\n1) List allowed models")
    models = httpx.get(f"{GATEWAY_URL}/v1/models", headers=headers(), timeout=20)
    show(models)

    print("\n2) Govern a chat completion request")
    completion = httpx.post(
        f"{GATEWAY_URL}/v1/chat/completions",
        headers=headers(),
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful enterprise assistant.",
                },
                {
                    "role": "user",
                    "content": "Summarize why runtime governance matters for AI agents.",
                },
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    show(completion)

    print("\nWhy this matters:")
    print("- App code can use an OpenAI-compatible base URL.")
    print("- AIRG can inspect model traffic and still correlate it with tool calls.")
    print("- Provider credentials stay server-side in the gateway deployment.")


if __name__ == "__main__":
    main()
