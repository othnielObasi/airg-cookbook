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
import uuid
from pprint import pprint

import httpx


GATEWAY_URL = os.getenv("AIRG_GATEWAY_URL", "https://gateway.airg.nov-tia.com").rstrip("/")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")
AGENT_ID = os.getenv("AIRG_AGENT_ID", "cookbook-gateway-agent")
SESSION_ID = os.getenv("AIRG_SESSION_ID", "cookbook-gateway-session")
ORG_ID = os.getenv("AIRG_ORG_ID", "demo-org")
WORKSPACE_ID = os.getenv("AIRG_WORKSPACE_ID", "demo-workspace")
APP_ID = os.getenv("AIRG_APP_ID", "gateway-cookbook")
ENVIRONMENT = os.getenv("AIRG_ENVIRONMENT", "production")
USER_ID = os.getenv("AIRG_USER_ID", "demo-user")
WORKFLOW_ID = os.getenv("AIRG_WORKFLOW_ID", "cloud-ops-change")


def headers() -> dict[str, str]:
    if not API_KEY:
        raise SystemExit("Set GOVERNOR_API_KEY before running this recipe.")
    return {
        "X-API-Key": API_KEY,
        "X-Request-Id": str(uuid.uuid4()),
        "X-AIRG-Org-Id": ORG_ID,
        "X-AIRG-Workspace-Id": WORKSPACE_ID,
        "X-AIRG-App-Id": APP_ID,
        "X-AIRG-Environment": ENVIRONMENT,
        "X-AIRG-User-Id": USER_ID,
        "X-AIRG-Workflow-Id": WORKFLOW_ID,
        "X-AIRG-Agent-Id": AGENT_ID,
        "X-AIRG-Session-Id": SESSION_ID,
        "Content-Type": "application/json",
    }


def show_gateway_response(resp: httpx.Response) -> None:
    print(f"HTTP {resp.status_code}")
    decision = resp.headers.get("x-airg-decision", "unknown").lower()
    if decision == "allow":
        print("Outcome: approved by AIRG and forwarded to upstream.")
    elif decision == "review":
        print("Outcome: AIRG requires human review; request was not forwarded.")
    elif decision in {"block", "deny", "denied"}:
        print("Outcome: blocked by AIRG policy; request was not forwarded.")
    elif resp.status_code in {401, 403}:
        print("Outcome: gateway authentication or authorization failed.")
    elif resp.status_code >= 500:
        print("Outcome: gateway or upstream error.")
    else:
        print("Outcome: no AIRG decision header found.")

    print("AIRG headers:")
    for name in (
        "x-airg-gateway",
        "x-airg-gateway-request-id",
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

    print("\n4) Blocked dangerous operation")
    blocked = httpx.post(
        f"{GATEWAY_URL}/proxy/cloud-ops/execute-operation",
        headers=headers(),
        json={
            "provider": "aws",
            "resource": "prod-cluster",
            "operation": "delete_cluster",
            "region": "us-east-1",
        },
        timeout=20,
    )
    show_gateway_response(blocked)

    print("\nWhy this matters:")
    print("- Gateway mode reduces integration friction for enterprise adoption.")
    print("- Approved routes prevent AIRG from becoming an open proxy.")
    print("- Upstream services only receive requests after AIRG approval.")
    print("- Request IDs connect client logs, gateway logs, AIRG decisions, and upstream logs.")


if __name__ == "__main__":
    main()
