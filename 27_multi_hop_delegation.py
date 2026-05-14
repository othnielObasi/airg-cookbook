#!/usr/bin/env python3
"""
Recipe 27 - Multi-Hop Delegation Governance
===========================================
Govern a supervisor -> specialist -> tool chain and prove that the child
agent stays inside the delegated boundary.

This is different from generic chain analysis. AIRG now validates that the
child action matches the parent delegation's target agent and allowed tool set.

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY="<your AIRG account API key>"
    python 27_multi_hop_delegation.py
"""
from __future__ import annotations

import os
import secrets
from pprint import pprint

import httpx


GOVERNOR_URL = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com").rstrip("/")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")
RUN_ID = secrets.token_hex(4)
SESSION_ID = f"delegation-{RUN_ID}"
TRACE_ID = f"trace-delegation-{RUN_ID}"


def headers() -> dict[str, str]:
    if not API_KEY:
        raise SystemExit("Set GOVERNOR_API_KEY before running this recipe.")
    return {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def evaluate(tool: str, args: dict, context: dict) -> dict:
    resp = httpx.post(
        f"{GOVERNOR_URL}/actions/evaluate",
        headers=headers(),
        json={"tool": tool, "args": args, "context": context},
        timeout=20,
    )
    print(f"{tool} -> HTTP {resp.status_code}")
    data = resp.json()
    pprint({
        "action_id": data.get("action_id"),
        "decision": data.get("decision"),
        "risk_score": data.get("risk_score"),
        "policy_ids": data.get("policy_ids"),
        "explanation": data.get("explanation"),
    })
    return data


def main() -> None:
    print("Multi-Hop Delegation Governance")
    print("=" * 72)

    print("\n1) Supervisor delegates a bounded database task")
    parent = evaluate(
        "delegate_to_specialist",
        {
            "target_agent_id": "database-specialist",
            "task": "Count active users for the weekly operations report.",
            "allowed_tools": ["execute_sql"],
        },
        {
            "agent_id": "supervisor-agent",
            "session_id": SESSION_ID,
            "trace_id": TRACE_ID,
            "span_id": "supervisor-delegation",
            "allowed_tools": ["delegate_to_specialist"],
        },
    )
    parent_action_id = parent.get("action_id")
    if not parent_action_id:
        raise SystemExit("Parent action did not return action_id; cannot continue.")

    print("\n2) Specialist performs the delegated tool action")
    evaluate(
        "execute_sql",
        {"query": "SELECT count(*) FROM users WHERE active = true"},
        {
            "agent_id": "database-specialist",
            "session_id": SESSION_ID,
            "trace_id": TRACE_ID,
            "parent_action_id": parent_action_id,
            "allowed_tools": ["execute_sql"],
        },
    )

    print("\n3) Specialist attempts a tool outside the delegation boundary")
    evaluate(
        "shell",
        {"command": "echo weekly-report"},
        {
            "agent_id": "database-specialist",
            "session_id": SESSION_ID,
            "trace_id": TRACE_ID,
            "parent_action_id": parent_action_id,
            "allowed_tools": ["shell"],
        },
    )

    print("\n4) Wrong child agent attempts to reuse the parent delegation")
    evaluate(
        "execute_sql",
        {"query": "SELECT count(*) FROM users WHERE active = true"},
        {
            "agent_id": "finance-specialist",
            "session_id": SESSION_ID,
            "trace_id": TRACE_ID,
            "parent_action_id": parent_action_id,
            "allowed_tools": ["execute_sql"],
        },
    )

    print("\nWhy this matters:")
    print("- AIRG checks that child agents obey the supervisor's delegated intent.")
    print("- Missing parents, wrong target agents, and wrong child tools are blocked.")
    print("- This is the enterprise bridge between simple SDK governance and mesh.")


if __name__ == "__main__":
    main()
