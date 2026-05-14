#!/usr/bin/env python3
"""
Recipe 28 - Canary Health and Context Isolation
===============================================
Check AIRG detector canaries and use stable context fields correctly.

Canaries help operators prove that key detectors are still catching synthetic
attacks. Context isolation ensures two organizations can reuse common names
like "support-agent" and "session-1" without sharing runtime state.

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export AIRG_TOKEN="<operator/admin JWT or API key>"
    python 28_canary_and_context_isolation.py
"""
from __future__ import annotations

import os
from pprint import pprint

import httpx


GOVERNOR_URL = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com").rstrip("/")
TOKEN = os.getenv("AIRG_TOKEN") or os.getenv("GOVERNOR_API_KEY", "")


def headers() -> dict[str, str]:
    if not TOKEN:
        raise SystemExit("Set AIRG_TOKEN or GOVERNOR_API_KEY before running this recipe.")
    if TOKEN.startswith("airg_"):
        return {"X-API-Key": TOKEN, "Content-Type": "application/json"}
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def request(method: str, path: str, body: dict | None = None) -> dict:
    resp = httpx.request(
        method,
        f"{GOVERNOR_URL}{path}",
        headers=headers(),
        json=body,
        timeout=20,
    )
    print(f"{method} {path} -> HTTP {resp.status_code}")
    try:
        data = resp.json()
    except Exception:
        data = {"text": resp.text}
    pprint(data)
    return data


def evaluate(tool: str, args: dict, context: dict) -> dict:
    return request("POST", "/actions/evaluate", {
        "tool": tool,
        "args": args,
        "context": context,
    })


def main() -> None:
    print("Canary Health and Context Isolation")
    print("=" * 72)

    print("\n1) View canary health")
    request("GET", "/admin/canary/status")

    print("\n2) Run an immediate canary self-test")
    request("POST", "/admin/canary/run")

    print("\n3) Evaluate with stable context fields")
    evaluate(
        "search_kb",
        {"query": "enterprise AI governance"},
        {
            "agent_id": "support-agent",
            "session_id": "case-1001",
            "user_id": "alice@example.com",
            "channel": "cookbook",
            "allowed_tools": ["search_kb"],
        },
    )

    print("\n4) Reuse the same visible agent/session safely")
    evaluate(
        "search_kb",
        {"query": "runtime policy controls"},
        {
            "agent_id": "support-agent",
            "session_id": "case-1001",
            "user_id": "alice@example.com",
            "channel": "cookbook",
            "allowed_tools": ["search_kb"],
        },
    )

    print("\nWhy this matters:")
    print("- Canary status tells operators whether guardrails are healthy.")
    print("- Stable agent_id/session_id improves chain analysis and audit search.")
    print("- AIRG scopes runtime memory by organization, not by client-controlled IDs alone.")


if __name__ == "__main__":
    main()
