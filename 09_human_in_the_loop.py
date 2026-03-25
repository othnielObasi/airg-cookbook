#!/usr/bin/env python3
"""
Recipe 09 — Human-in-the-Loop Review
======================================
When the Governor returns a "review" decision, the agent can hold
execution and wait for a human approver. This recipe demonstrates:

1. Triggering a review decision (medium-risk action)
2. Holding with a timeout while a human decides
3. Handling approved, rejected, and expired outcomes

    pip install airg-client
    python 09_human_in_the_loop.py
"""
from __future__ import annotations

from airg import AIRG, BlockedError, ReviewRejectedError, ReviewExpiredError

client = AIRG()


def governed_execute(tool: str, args: dict, hold_timeout: int = 30):
    """Execute a tool with human-in-the-loop review support."""
    print(f"\n── {tool}({args}) ──")

    try:
        decision = client.evaluate(
            tool=tool,
            args=args,
            review_mode="hold",        # ← tell Governor to hold for approval
            hold_timeout=hold_timeout,  # ← seconds to wait for human
        )

        status = decision["decision"]
        print(f"   Decision     : {status}")
        print(f"   Risk score   : {decision['risk_score']}")

        if status == "allow":
            print("   ✅ Approved — executing tool")
            return simulate_execution(tool, args)

        elif status == "review":
            print("   ⏳ Held for review — waiting for human approver...")
            print(f"   Review URL   : {decision.get('review_url', 'see dashboard')}")
            print("   (In production, the SDK long-polls until a human decides)")
            return None

    except BlockedError as e:
        print(f"   🛑 BLOCKED: {e}")
        return None

    except ReviewRejectedError as e:
        print(f"   ❌ Reviewer REJECTED: {e}")
        print("   The human reviewer determined this action is not safe.")
        return None

    except ReviewExpiredError as e:
        print(f"   ⏱️ Review EXPIRED: {e}")
        print("   No human responded within the timeout. Action not executed.")
        return None


def simulate_execution(tool: str, args: dict) -> str:
    return f"[simulated] {tool} executed with {args}"


# ── Run examples ────────────────────────────────────────────────
if __name__ == "__main__":
    # Low risk — auto-approved
    governed_execute("read_file", {"path": "/tmp/report.txt"})

    # Medium risk — likely triggers review
    governed_execute("send_email", {
        "to": "external@partner.com",
        "subject": "Quarterly Report",
        "body": "Attached is the financial summary.",
    })

    # High risk — likely blocked outright
    governed_execute("transfer_funds", {
        "from": "company_treasury",
        "to": "0xDEAD...BEEF",
        "amount": 50000,
        "currency": "USDC",
    })
