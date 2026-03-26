#!/usr/bin/env python3
"""
Recipe 07 — Output Verification
================================
After a tool executes, verify the result to catch credential leaks,
destructive side-effects, and scope violations that pre-execution
governance can't predict.

    pip install airg-client
    python 07_output_verification.py
"""
from __future__ import annotations

from airg import AIRG, BlockedError, VerificationError

client = AIRG()


def run_tool(name: str, args: dict) -> str:
    """Simulate tool execution and return output."""
    if name == "read_file":
        return "user_id,email,ssn\n1,alice@corp.com,123-45-6789\n"
    if name == "query_db":
        return '{"rows": [{"api_key": "sk-proj-XXXX..."}]}'
    if name == "shell_exec":
        return "total 0\ndrwxr-xr-x  2 root root 40 Jan  1 00:00 tmp"
    return "OK"


# ── Governed tool call with post-execution verification ─────────
def governed_execute(tool: str, args: dict):
    print(f"\n── {tool}({args}) ──")

    # Step 1: Pre-execution governance
    try:
        pre = client.evaluate(tool=tool, args=args)
        print(f"   Pre-eval : {pre['decision']} (risk: {pre['risk_score']})")
        action_id = pre.get("action_id")
    except BlockedError as e:
        print(f"   Pre-eval : 🛑 BLOCKED — {e}")
        return None

    if not action_id:
        print("   Skipping verification (no action_id in response).")
        return None

    # Step 2: Execute the tool
    output = run_tool(tool, args)
    print(f"   Output   : {output[:80]}...")

    # Step 3: Post-execution verification
    try:
        post = client.verify(
            action_id=action_id,
            tool=tool,
            result={"output": output},
        )
        checks = post.get("findings", [])
        passed = sum(1 for f in checks if f.get("result") == "pass")
        print(f"   Verify   : ✅ PASS — {passed}/{len(checks)} checks passed")
        return output

    except VerificationError as e:
        print(f"   Verify   : ⚠️ VIOLATION — {e}")
        print("   Action   : Output quarantined, not sent to user.")
        return None


# ── Run examples ────────────────────────────────────────────────
if __name__ == "__main__":
    # Safe output
    governed_execute("shell_exec", {"command": "ls -la /tmp"})

    # Output contains PII (SSN) — verification should flag it
    governed_execute("read_file", {"path": "users.csv"})

    # Output contains leaked API key — verification should catch it
    governed_execute("query_db", {"query": "SELECT * FROM config"})
