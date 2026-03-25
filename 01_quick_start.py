#!/usr/bin/env python3
"""
Recipe 01 — Quick Start
=======================
Your first AIRG governance call in 10 lines.

Evaluates a shell command and prints the decision.

    pip install airg-client
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY=airg_...
    python 01_quick_start.py
"""
from airg import AIRG, BlockedError

client = AIRG()

# ── 1. Evaluate a low-risk tool call ────────────────────────────
decision = client.evaluate(
    tool="read_file",
    args={"path": "/tmp/report.csv"},
)
print(f"✅  Decision : {decision['decision']}")
print(f"    Risk     : {decision['risk_score']}")
print(f"    Reason   : {decision['explanation']}")

# ── 2. Evaluate a high-risk tool call ───────────────────────────
try:
    decision = client.evaluate(
        tool="shell_exec",
        args={"command": "rm -rf /"},
    )
    print(f"\n⚠️  Decision : {decision['decision']}")
    print(f"    Risk     : {decision['risk_score']}")
except BlockedError as e:
    print(f"\n🛑  BLOCKED  : {e}")
    print("    The Governor prevented a dangerous operation.")
