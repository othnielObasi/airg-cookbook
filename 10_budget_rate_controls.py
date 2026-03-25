#!/usr/bin/env python3
"""
Recipe 10 — Budget & Rate Controls
====================================
Demonstrate per-agent budget enforcement. The Governor tracks
cumulative spend per agent/session and blocks when limits are hit.

Budget tiers (defaults):
  - 500 actions per session
  - 1,000 actions per hour
  - 10,000 actions per day

When an agent exceeds limits, a circuit breaker activates
(10 consecutive blocks → 5-minute cooldown).

    pip install airg-client
    python 10_budget_rate_controls.py
"""
from __future__ import annotations

import secrets
import time

from airg import AIRG, BlockedError

client = AIRG()
session_id = f"budget-demo-{secrets.token_hex(4)}"


def batch_evaluate(count: int, tool: str, args: dict):
    """Fire N evaluations and track allow/block/review rates."""
    print(f"\n── Firing {count} × {tool}() ──")

    stats = {"allow": 0, "block": 0, "review": 0, "error": 0}

    for i in range(count):
        try:
            decision = client.evaluate(
                tool=tool,
                args=args,
                context={
                    "agent_id": "budget-test-agent",
                    "session_id": session_id,
                },
            )
            status = decision["decision"]
            stats[status] = stats.get(status, 0) + 1

            if (i + 1) % 50 == 0:
                print(f"   [{i+1}/{count}] allow={stats['allow']} "
                      f"block={stats['block']} review={stats['review']}")

        except BlockedError:
            stats["block"] += 1
            if stats["block"] == 1:
                print(f"   [{i+1}/{count}] ← first block (budget limit hit)")

    print(f"\n   Results: {stats}")
    return stats


# ── Check budget status ─────────────────────────────────────────
def check_budget():
    """Check the budget enforcer status via admin endpoint."""
    import httpx
    import os

    url = os.getenv("GOVERNOR_URL", "http://localhost:8000")
    key = os.getenv("GOVERNOR_API_KEY", "")

    resp = httpx.get(
        f"{url}/admin/budget/status",
        headers={"X-API-Key": key},
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"\n── Budget Status ──")
        print(f"   Active agents  : {data.get('active_agents', '?')}")
        print(f"   Circuit breaker: {data.get('circuit_breaker', '?')}")
    else:
        print(f"   Budget endpoint returned {resp.status_code}")


# ── Run demo ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Budget & Rate Control Demo")
    print("=" * 60)

    # Fire a burst of safe evaluations
    stats = batch_evaluate(
        count=20,
        tool="read_file",
        args={"path": "/tmp/data.csv"},
    )

    # Check budget status
    check_budget()

    print("\n💡 In production, budget limits prevent runaway agents from")
    print("   exhausting resources. The circuit breaker auto-triggers")
    print("   after consecutive blocks for a 5-minute cooldown.")
