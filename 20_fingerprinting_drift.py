#!/usr/bin/env python3
"""
Recipe 20 — Agent Fingerprinting & Drift Detection
====================================================
Monitor agent behavioural baselines and detect drift.
The fingerprinting engine learns tool distributions, call velocity,
risk profiles, and sequence patterns — then alerts when behaviour diverges.

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY=airg_...
    python 20_fingerprinting_drift.py
"""
from __future__ import annotations
import os, httpx

url = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com")
headers = {"X-API-Key": os.environ["GOVERNOR_API_KEY"]}

# ── 1. List all fingerprinted agents ───────────────────────────
print("🧬 Agent Fingerprinting — Tracked Agents\n")

agents = httpx.get(f"{url}/fingerprint/agents", headers=headers).json()
print(f"  Tracking {agents['agent_count']} agents "
      f"({agents['total_evaluations']} total evaluations)\n")

for a in agents["agents"][:5]:
    print(f"  🤖 {a['agent_id']}")
    print(f"     Maturity   : {a['maturity']}")
    print(f"     Unique tools: {a['unique_tools']}")
    print(f"     Block rate  : {a['block_rate_pct']}%")
    print()

# ── 2. Check drift for a specific agent ────────────────────────
if agents["agents"]:
    agent_id = agents["agents"][0]["agent_id"]
    print(f"{'─'*60}")
    print(f"📈 Drift Analysis — {agent_id}\n")

    drift = httpx.get(f"{url}/fingerprint/agents/{agent_id}/drift",
                      headers=headers).json()
    print(f"  Drift score: {drift['drift_score']}/100")
    print(f"  Level      : {drift['drift_level']}")
    print(f"  Alert      : {drift['alert']}\n")

    for dim in drift.get("dimensions", []):
        print(f"  [{dim['dimension']}] score={dim['score']}")
        print(f"    {dim['details']}\n")

# ── 3. Generate some evaluations to build a fingerprint ────────
print(f"{'─'*60}")
print("🔄 Building fingerprint with 5 evaluations...\n")

tools = ["read_file", "write_file", "shell_exec", "http_request", "read_file"]
for tool in tools:
    r = httpx.post(f"{url}/actions/evaluate", headers=headers, json={
        "agent_id": "drift-demo-agent",
        "tool": tool,
        "args": {"path": "/tmp/test.txt"},
    })
    d = r.json()
    print(f"  {tool}: {d['decision']} (risk={d['risk_score']})")

# Check the new agent's fingerprint
print(f"\n  Checking fingerprint for drift-demo-agent...")
drift2 = httpx.get(f"{url}/fingerprint/agents/drift-demo-agent/drift",
                   headers=headers).json()
print(f"  Drift score: {drift2['drift_score']}/100  Level: {drift2['drift_level']}")
