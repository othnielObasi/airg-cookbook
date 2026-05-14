#!/usr/bin/env python3
"""
Recipe 26 - Controlled Agent Mesh Governance
============================================
Register agents, approve a peer relationship, and govern call_agent as a
first-class AIRG action.

This demonstrates the new controlled mesh model:

    source agent -> call_agent -> AIRG checks agent registry + mesh policies

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export AIRG_TOKEN="<admin/operator JWT or API key with mesh permissions>"
    python 26_controlled_agent_mesh.py
"""
from __future__ import annotations

import os
import secrets
from pprint import pprint

import httpx


GOVERNOR_URL = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com").rstrip("/")
TOKEN = os.getenv("AIRG_TOKEN") or os.getenv("GOVERNOR_API_KEY", "")
RUN_ID = secrets.token_hex(4)
SOURCE = f"cookbook-support-{RUN_ID}"
TARGET = f"cookbook-billing-{RUN_ID}"


def headers() -> dict[str, str]:
    if not TOKEN:
        raise SystemExit("Set AIRG_TOKEN or GOVERNOR_API_KEY before running this recipe.")
    if TOKEN.startswith("airg_"):
        return {"X-API-Key": TOKEN, "Content-Type": "application/json"}
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def api(method: str, path: str, body: dict | None = None) -> dict:
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
    if resp.status_code >= 400:
        pprint(data)
        resp.raise_for_status()
    return data


def evaluate(tool: str, args: dict, context: dict) -> dict:
    decision = api("POST", "/actions/evaluate", {
        "tool": tool,
        "args": args,
        "context": context,
    })
    pprint({
        "decision": decision.get("decision"),
        "risk_score": decision.get("risk_score"),
        "policy_ids": decision.get("policy_ids"),
        "explanation": decision.get("explanation"),
    })
    return decision


def main() -> None:
    print("Controlled Agent Mesh Governance")
    print("=" * 72)

    print("\n1) Register source and target agents")
    api("POST", "/agent-mesh/agents", {
        "agent_id": SOURCE,
        "name": "Cookbook Support Agent",
        "agent_type": "support",
        "allowed_peers": [TARGET],
        "allowed_tools": ["call_agent"],
    })
    api("POST", "/agent-mesh/agents", {
        "agent_id": TARGET,
        "name": "Cookbook Billing Agent",
        "agent_type": "billing",
        "allowed_tools": ["lookup_invoice"],
    })

    print("\n2) Allowed peer call")
    evaluate(
        "call_agent",
        {
            "target_agent_id": TARGET,
            "requested_action": "lookup_invoice",
            "message": "Please check invoice INV-1024.",
        },
        {
            "agent_id": SOURCE,
            "session_id": f"mesh-{RUN_ID}",
            "allowed_tools": ["call_agent"],
        },
    )

    print("\n3) Explicit mesh policy blocking a dangerous delegated action")
    policy_id = f"cookbook-block-refund-{RUN_ID}"
    api("POST", "/agent-mesh/policies", {
        "policy_id": policy_id,
        "source_agent_id": SOURCE,
        "target_agent_id": TARGET,
        "allowed_actions": ["lookup_invoice"],
        "blocked_actions": ["issue_refund"],
        "decision": "allow",
        "severity": 90,
        "reason": "Support may inspect invoices but cannot request refunds.",
    })

    evaluate(
        "call_agent",
        {
            "target_agent_id": TARGET,
            "requested_action": "issue_refund",
            "message": "Refund invoice INV-1024 immediately.",
        },
        {
            "agent_id": SOURCE,
            "session_id": f"mesh-{RUN_ID}",
            "allowed_tools": ["call_agent"],
        },
    )

    print("\nWhy this matters:")
    print("- AIRG blocks unregistered or inactive peer calls by default.")
    print("- Agent-to-agent communication becomes explicit and auditable.")
    print("- Enterprises can prevent lateral movement across agent roles.")


if __name__ == "__main__":
    main()
