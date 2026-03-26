#!/usr/bin/env python3
"""
Recipe 11 — Trace Observability
================================
Ingest OpenTelemetry-style spans from your agent, then query
traces with governance decisions correlated inline.

This is how you get the Trace Viewer waterfall in the dashboard.

    pip install airg-client
    python 11_trace_observability.py
"""
from __future__ import annotations

import secrets
import time
from datetime import datetime, timezone

from airg import AIRG

client = AIRG()

AGENT_ID = "cookbook-agent"
SESSION_ID = f"session-{secrets.token_hex(4)}"
TRACE_ID = f"trace-{secrets.token_hex(8)}"


# ── Step 1: Ingest spans ────────────────────────────────────────
def ingest_demo_spans():
    """Create a realistic span tree: agent → tool calls → sub-steps."""
    now = datetime.now(timezone.utc)
    base_ts = now.isoformat()

    spans = [
        # Root span — the agent session
        {
            "trace_id": TRACE_ID,
            "span_id": f"span-{secrets.token_hex(4)}",
            "name": "agent.run",
            "kind": "internal",
            "agent_id": AGENT_ID,
            "session_id": SESSION_ID,
            "start_time": base_ts,
            "attributes": {"agent.type": "research", "agent.model": "gpt-4o"},
        },
        # Tool call 1 — safe
        {
            "trace_id": TRACE_ID,
            "span_id": f"span-{secrets.token_hex(4)}",
            "parent_span_id": "span-root",
            "name": "tool.read_file",
            "kind": "tool",
            "agent_id": AGENT_ID,
            "session_id": SESSION_ID,
            "start_time": base_ts,
            "end_time": base_ts,
            "attributes": {
                "tool.name": "read_file",
                "tool.args": '{"path": "/data/report.csv"}',
                "governance.decision": "allow",
                "governance.risk_score": 5,
            },
        },
        # Tool call 2 — elevated risk
        {
            "trace_id": TRACE_ID,
            "span_id": f"span-{secrets.token_hex(4)}",
            "parent_span_id": "span-root",
            "name": "tool.shell_exec",
            "kind": "tool",
            "agent_id": AGENT_ID,
            "session_id": SESSION_ID,
            "start_time": base_ts,
            "end_time": base_ts,
            "attributes": {
                "tool.name": "shell_exec",
                "tool.args": '{"command": "curl https://api.example.com/data"}',
                "governance.decision": "review",
                "governance.risk_score": 62,
            },
        },
        # Tool call 3 — blocked
        {
            "trace_id": TRACE_ID,
            "span_id": f"span-{secrets.token_hex(4)}",
            "parent_span_id": "span-root",
            "name": "tool.deploy_contract",
            "kind": "tool",
            "agent_id": AGENT_ID,
            "session_id": SESSION_ID,
            "start_time": base_ts,
            "end_time": base_ts,
            "attributes": {
                "tool.name": "deploy_contract",
                "tool.args": '{"bytecode": "0x60806040..."}',
                "governance.decision": "block",
                "governance.risk_score": 95,
            },
        },
    ]

    print(f"── Ingesting {len(spans)} spans (trace: {TRACE_ID}) ──")
    result = client.ingest_spans(spans)
    print(f"   Inserted: {result.get('inserted', '?')} spans")
    print(f"   Skipped : {result.get('skipped', 0)} spans")
    return result


# ── Step 2: Query traces ────────────────────────────────────────
def query_traces():
    """List and retrieve traces, showing governance correlation."""
    print(f"\n── Querying traces for agent '{AGENT_ID}' ──")

    traces = client.list_traces(agent_id=AGENT_ID, limit=5)
    print(f"   Found {len(traces)} traces")

    for t in traces[:3]:
        print(f"   • {t.get('trace_id', '?')[:20]}... "
              f"spans={t.get('span_count', '?')} "
              f"gov_decisions={t.get('governance_count', 0)} "
              f"has_blocks={t.get('has_blocks', False)}")

    # Fetch full detail for our trace
    if traces:
        trace_id = traces[0].get("trace_id", TRACE_ID)
        print(f"\n── Full trace detail: {trace_id} ──")
        detail = client.get_trace(trace_id)

        for span in detail.get("spans", []):
            decision = span.get("attributes", {}).get("governance.decision", "—")
            risk = span.get("attributes", {}).get("governance.risk_score", "—")
            icon = {"allow": "✅", "review": "⚠️", "block": "🛑"}.get(decision, "  ")
            print(f"   {icon} {span.get('name', '?'):30s} "
                  f"decision={decision:8s} risk={risk}")


# ── Run ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    ingest_demo_spans()
    time.sleep(0.5)  # let the server index
    query_traces()

    print(f"\n💡 Open the AIRG dashboard → Traces tab to see the")
    print(f"   waterfall visualization with governance decisions inline.")
