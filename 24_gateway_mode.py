#!/usr/bin/env python3
"""
Recipe 24 - AIRG Gateway Mode
=============================
Use AIRG as a production gateway in front of enterprise tools/APIs.

Gateway mode is the drop-in adoption path:

    client -> AIRG Gateway -> AIRG /actions/evaluate -> approved upstream

This recipe calls the production gateway health endpoint, lists an approved
route catalog, and shows how decision headers come back from the gateway.

    pip install httpx
    export GOVERNOR_API_KEY="<your AIRG account API key>"
    export AIRG_GATEWAY_URL=https://gateway.airg.nov-tia.com
    python 24_gateway_mode.py
"""
from __future__ import annotations

import os
from pprint import pprint

import httpx


GATEWAY_URL = os.getenv("AIRG_GATEWAY_URL", "https://gateway.airg.nov-tia.com").rstrip("/")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")
AGENT_ID = os.getenv("AIRG_AGENT_ID", "cookbook-gateway-agent")
SESSION_ID = os.getenv("AIRG_SESSION_ID", "cookbook-gateway-session")


def headers() -> dict[str, str]:
    if not API_KEY:
        raise SystemExit("Set GOVERNOR_API_KEY before running this recipe.")
    return {
        "X-API-Key": API_KEY,
        "X-AIRG-Agent-Id": AGENT_ID,
        "X-AIRG-Session-Id": SESSION_ID,
        "Content-Type": "application/json",
    }


def show_gateway_response(resp: httpx.Response) -> None:
    print(f"HTTP {resp.status_code}")
    print("AIRG headers:")
    for name in (
        "x-airg-gateway",
        "x-airg-decision",
        "x-airg-risk-score",
        "x-airg-policy-ids",
        "x-airg-decision-tags",
        "x-airg-action-id",
        "x-airg-evidence-hash",
    ):
        if name in resp.headers:
            print(f"  {name}: {resp.headers[name]}")
    try:
        pprint(resp.json())
    except Exception:
        print(resp.text[:500])


def main() -> None:
    print("AIRG Gateway Mode")
    print("=" * 72)

    health = httpx.get(f"{GATEWAY_URL}/healthz", timeout=10)
    health.raise_for_status()
    print("\nGateway health:")
    pprint(health.json())

    print("\n1) Approved route catalog through gateway")
    catalog = httpx.get(
        f"{GATEWAY_URL}/proxy/enterprise-tools/catalog",
        headers=headers(),
        timeout=20,
    )
    show_gateway_response(catalog)

    print("\n2) Safe enterprise tool request")
    safe = httpx.post(
        f"{GATEWAY_URL}/proxy/enterprise-tools/kb/search",
        headers=headers(),
        json={"query": "AIRG gateway enterprise adoption", "limit": 2},
        timeout=20,
    )
    show_gateway_response(safe)

    print("\n3) Higher-risk route still passes through AIRG before upstream")
    risky = httpx.post(
        f"{GATEWAY_URL}/proxy/cloud-ops/plan-operation",
        headers=headers(),
        json={
            "provider": "aws",
            "resource": "prod-cluster",
            "operation": "plan_restart",
            "region": "us-east-1",
        },
        timeout=20,
    )
    show_gateway_response(risky)

    print("\nWhy this matters:")
    print("- Gateway mode reduces integration friction for enterprise adoption.")
    print("- Approved routes prevent AIRG from becoming an open proxy.")
    print("- Every forwarded request is still governed and visible in AIRG logs.")


if __name__ == "__main__":
    main()
