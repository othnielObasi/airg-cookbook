#!/usr/bin/env python3
"""
Recipe 23 — Impact Assessment & Reporting
==========================================
Generate 30-day impact reports with risk distribution, percentiles
(p50/p90/p95/p99), chain pattern detection, and decision breakdowns
across all agents and tools.

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY=airg_...
    python 23_impact_assessment.py
"""
from __future__ import annotations
import os, httpx

url = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com")
headers = {"X-API-Key": os.environ["GOVERNOR_API_KEY"]}

# ── 1. Full impact assessment ──────────────────────────────────
print("📊 Impact Assessment — 30-Day Report\n")

report = httpx.get(f"{url}/impact/assess", headers=headers).json()
print(f"  Period          : {report.get('period', '30d')} days")
print(f"  Total evals     : {report['total_evaluations']}")
print(f"  Unique agents   : {report['unique_agents']}")
print(f"  Unique tools    : {report['unique_tools']}")

# ── 2. Risk distribution ───────────────────────────────────────
rd = report["risk_distribution"]
print(f"\n{'─'*60}")
print("📈 Risk Percentiles\n")
print(f"  p50 (median) : {rd.get('median', rd.get('p50', 'N/A'))}")
print(f"  p90          : {rd['p90']}")
print(f"  p95          : {rd.get('p95', 'N/A')}")
print(f"  p99          : {rd['p99']}")

# ── 3. Decision breakdown ──────────────────────────────────────
dec = report.get("decision_breakdown", {})
total = sum(dec.values()) or 1
print(f"\n{'─'*60}")
print("📋 Decision Breakdown\n")
for d, c in dec.items():
    bar = "█" * int(c / total * 40)
    print(f"  {d:8s}: {bar} {c} ({c/total*100:.1f}%)")

# ── 4. Per-agent assessment ────────────────────────────────────
print(f"\n{'─'*60}")
print("🤖 Per-Agent Assessment\n")

# Use an agent_id from the report if available
agent_ids = report.get("top_agents", [])
if agent_ids:
    aid = agent_ids[0] if isinstance(agent_ids[0], str) else agent_ids[0].get("agent_id", "my-agent")
else:
    aid = "my-agent"

agent_report = httpx.get(f"{url}/impact/assess/agent/{aid}",
                         headers=headers).json()
print(f"  Agent         : {aid}")
print(f"  Evaluations   : {agent_report.get('total_evaluations', 'N/A')}")
print(f"  Avg risk      : {agent_report.get('risk_level', 'N/A')}")

# ── 5. Per-tool assessment ─────────────────────────────────────
print(f"\n{'─'*60}")
print("🔧 Per-Tool Assessment — shell_exec\n")

tool_report = httpx.get(f"{url}/impact/assess/tool/shell_exec",
                        headers=headers).json()
print(f"  Tool          : shell_exec")
print(f"  Evaluations   : {tool_report.get('total_evaluations', 'N/A')}")
print(f"  Avg risk      : {tool_report.get('risk_level', 'N/A')}")
print(f"  Block rate    : {tool_report.get('block_rate_pct', 'N/A')}%")
