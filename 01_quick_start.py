#!/usr/bin/env python3
"""
Recipe 01 - Quick Start
=======================
Create an AIRG SDK client and evaluate two tool calls.

`AIRG()` is the Python client from the `airg-client` package. By default it
reads:

    GOVERNOR_URL      AIRG API base URL
    GOVERNOR_API_KEY  API key from your registered AIRG account

Install and run:

    pip install airg-client
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY="<your AIRG account API key>"
    python 01_quick_start.py
"""
from __future__ import annotations

from airg import AIRG, BlockedError


client = AIRG()


def show_decision(label: str, decision: dict) -> None:
    print(f"\n{label}")
    print(f"  Decision   : {decision['decision']}")
    print(f"  Risk       : {decision['risk_score']}/100")
    print(f"  Explanation: {decision.get('explanation', 'No explanation returned')}")
    categories = decision.get("categories") or decision.get("risk_categories") or []
    if categories:
        print(f"  Categories : {', '.join(categories)}")


# 1. Evaluate a low-risk tool call.
safe = client.evaluate(
    tool="read_file",
    args={"path": "/tmp/report.csv"},
    context={"agent_id": "quickstart-agent", "session_id": "quickstart-demo"},
)
show_decision("Safe tool call", safe)


# 2. Evaluate a high-risk tool call. The SDK raises BlockedError for block.
try:
    risky = client.evaluate(
        tool="shell_exec",
        args={"command": "rm -rf /"},
        context={"agent_id": "quickstart-agent", "session_id": "quickstart-demo"},
    )
    show_decision("High-risk tool call", risky)
except BlockedError as exc:
    print("\nHigh-risk tool call")
    print(f"  Decision   : block")
    print(f"  Result     : AIRG prevented execution")
    print(f"  Detail     : {exc}")
