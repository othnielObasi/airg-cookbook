#!/usr/bin/env python3
"""
Recipe 13 — Policy as Code
============================
Create, manage, and version governance policies programmatically.
Useful for CI/CD pipelines that deploy policies alongside code.

    pip install airg-client httpx
    python 13_policy_as_code.py
"""
from __future__ import annotations

import json
import os

import httpx

GOVERNOR_URL = os.getenv("GOVERNOR_URL", "http://localhost:8000")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def api(method: str, path: str, body: dict | None = None) -> dict:
    """Make an authenticated API call."""
    url = f"{GOVERNOR_URL}{path}"
    resp = httpx.request(method, url, headers=HEADERS, json=body, timeout=10)
    resp.raise_for_status()
    return resp.json() if resp.content else {}


# ── Step 1: Create a policy ─────────────────────────────────────
def create_policy():
    print("── Creating policy: block-destructive-shell ──")
    policy = api("POST", "/policies", {
        "policy_id": "block-destructive-shell",
        "description": "Prevent rm -rf, dd, mkfs, and similar destructive commands.",
        "action": "block",
        "severity": "critical",
        "match_json": {
            "tool": "shell_exec",
            "regex": r"(rm\s+-rf|dd\s+if=|mkfs|format\s+[A-Z]:)",
        },
    })
    policy_id = policy.get("policy_id") or policy.get("id")
    print(f"   Created: {policy_id}")
    print(f"   Version: {policy.get('version', 1)}")
    return policy_id


# ── Step 2: List policies ───────────────────────────────────────
def list_policies():
    print("\n── Active policies ──")
    policies = api("GET", "/policies/all")
    items = policies if isinstance(policies, list) else policies.get("policies", [])
    for p in items[:10]:
        active = "✅" if p.get("is_active") else "⬜"
        print(f"   {active} {p.get('name', '?'):40s} → {p.get('action', '?')}")
    print(f"   ... {len(items)} total")


# ── Step 3: Update a policy ─────────────────────────────────────
def update_policy(policy_id: str):
    print(f"\n── Updating policy {policy_id} ──")
    updated = api("PATCH", f"/policies/{policy_id}", {
        "description": "Block destructive shell + format commands. Updated via cookbook.",
        "match_json": {
            "tool": "shell_exec",
            "regex": r"(rm\s+-rf|dd\s+if=|mkfs|format\s+[A-Z]:|shred\s)",
        },
    })
    print(f"   Version: {updated.get('version', '?')}")


# ── Step 4: View version history ────────────────────────────────
def view_versions(policy_id: str):
    print(f"\n── Version history for {policy_id} ──")
    versions = api("GET", f"/policies/{policy_id}/versions")
    items = versions if isinstance(versions, list) else versions.get("versions", [])
    for v in items:
        print(f"   v{v.get('version', '?')} — {v.get('changed_at', '?')[:19]} "
              f"by {v.get('changed_by', '?')}")


# ── Step 5: Deactivate a policy ─────────────────────────────────
def deactivate_policy(policy_id: str):
    print(f"\n── Deactivating policy {policy_id} ──")
    result = api("PATCH", f"/policies/{policy_id}", {"is_active": False})
    print(f"   Active: {result.get('is_active', '?')}")


# ── Step 6: Export all policies (for backup / CI) ───────────────
def export_policies():
    print("\n── Exporting all policies ──")
    data = api("GET", "/policies/export/all")
    filename = "policies_backup.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"   Saved to {filename}")


# ── Step 7: Audit trail ────────────────────────────────────────
def audit_trail(policy_id: str):
    print(f"\n── Audit trail for {policy_id} ──")
    trail = api("GET", f"/policies/{policy_id}/audit")
    items = trail if isinstance(trail, list) else trail.get("entries", [])
    for entry in items[:5]:
        print(f"   {entry.get('timestamp', entry.get('changed_at', '?'))[:19]} │ "
              f"{entry.get('action', entry.get('change_type', '?')):10s} │ "
              f"{entry.get('policy_id', '?')}")


# ── Run ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Policy as Code Demo")
    print("=" * 60)

    list_policies()

    policy_id = create_policy()
    if policy_id:
        update_policy(policy_id)
        view_versions(policy_id)
        deactivate_policy(policy_id)
        export_policies()
        audit_trail(policy_id)

    print("\n💡 Use this pattern in CI/CD: export policies from staging,")
    print("   review the diff, then import into production.")
