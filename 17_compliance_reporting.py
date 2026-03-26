#!/usr/bin/env python3
"""
Recipe 17 — Compliance Reporting
==================================
Export regulatory compliance reports mapped to:
- EU AI Act
- NIST AI RMF
- NIST AI 600-1
- OWASP LLM Top 10 (2025)

Each governance decision is auto-tagged with relevant clauses.

    pip install airg-client httpx
    python 17_compliance_reporting.py
"""
from __future__ import annotations

import json
import os

import httpx

GOVERNOR_URL = os.getenv("GOVERNOR_URL", "http://localhost:8000")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")
HEADERS = {"X-API-Key": API_KEY}


def api(path: str, params: dict | None = None) -> dict | list:
    resp = httpx.get(f"{GOVERNOR_URL}{path}", headers=HEADERS,
                     params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ── 1. List available regulatory frameworks ─────────────────────
def list_frameworks():
    print("── Available regulatory frameworks ──")
    clauses = api("/compliance/clauses")
    items = clauses if isinstance(clauses, list) else clauses.get("clauses", [])

    frameworks = set()
    for c in items:
        fw = c.get("framework", "")
        if fw:
            frameworks.add(fw)

    for fw in sorted(frameworks):
        count = sum(1 for c in items if c.get("framework") == fw)
        print(f"   📜 {fw}: {count} clauses")

    return items


# ── 2. Show clauses for one framework ──────────────────────────
def show_framework(framework: str):
    print(f"\n── Clauses for {framework} ──")
    clauses = api(f"/compliance/clauses/{framework}")
    items = clauses if isinstance(clauses, list) else clauses.get("clauses", [])

    for c in items[:10]:
        cid = c.get("clause_id", "?")
        title = c.get("title", c.get("description", "?"))[:60]
        print(f"   {cid:15s} │ {title}")

    if len(items) > 10:
        print(f"   ... and {len(items) - 10} more")


# ── 3. Generate compliance report ──────────────────────────────
def generate_report(clauses):
    """Generate a compliance summary from local clause data and action history."""
    print("\n── Generating compliance summary ──")

    # Fetch recent actions to cross-reference
    actions = api("/actions", {"limit": 100})
    items = actions if isinstance(actions, list) else actions.get("items", [])
    total = len(items)
    blocked = sum(1 for a in items if a.get("decision") == "block")

    print(f"   Total evaluations : {total}")
    print(f"   Blocked actions   : {blocked}")

    # Per-framework clause coverage
    if clauses:
        frameworks: dict = {}
        for c in clauses:
            fw = c.get("framework", "unknown")
            frameworks.setdefault(fw, []).append(c)

        print(f"\n   Framework coverage:")
        for fw, fw_clauses in sorted(frameworks.items()):
            count = len(fw_clauses)
            print(f"   📜 {fw:20s} │ {count} clauses tracked")


# ── 4. Show moderation categories ──────────────────────────────
def show_moderation():
    print("\n── Content moderation categories ──")
    cats = api("/moderation/categories")
    items = cats if isinstance(cats, list) else cats.get("categories", [])

    for cat in items:
        name = cat if isinstance(cat, str) else cat.get("name", "?")
        print(f"   • {name}")


# ── Run ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Compliance Reporting")
    print("=" * 60)

    clauses = list_frameworks()

    if clauses:
        frameworks = {c.get("framework") for c in clauses if c.get("framework")}
        for fw in sorted(frameworks)[:2]:
            show_framework(fw)

    generate_report(clauses)
    show_moderation()

    print("\n💡 Schedule this script in CI to generate compliance reports")
    print("   after each deployment. Attach to audit workflows or feed")
    print("   into GRC platforms (Vanta, Drata, OneTrust).")
