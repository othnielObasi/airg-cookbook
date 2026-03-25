#!/usr/bin/env python3
"""
Recipe 12 — Real-Time SSE Monitoring
======================================
Connect to the Governor's Server-Sent Events stream to get live
governance decisions as they happen. Useful for building custom
dashboards, alerting pipelines, or audit feeds.

    pip install airg-client httpx-sse
    python 12_realtime_sse_monitoring.py
"""
from __future__ import annotations

import json
import os
import signal
import sys

import httpx

GOVERNOR_URL = os.getenv("GOVERNOR_URL", "http://localhost:8000")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")


def stream_events(max_events: int = 50):
    """Connect to the SSE stream and print governance events live."""
    url = f"{GOVERNOR_URL}/actions/stream"
    headers = {"X-API-Key": API_KEY} if API_KEY else {}

    print(f"🔴 Connecting to {url}")
    print(f"   Watching for up to {max_events} events (Ctrl+C to stop)\n")

    count = 0

    with httpx.stream("GET", url, headers=headers, timeout=None) as response:
        response.raise_for_status()
        buffer = ""

        for chunk in response.iter_text():
            buffer += chunk
            while "\n\n" in buffer:
                raw, buffer = buffer.split("\n\n", 1)
                event = parse_sse(raw)
                if not event:
                    continue

                count += 1
                display_event(count, event)

                if count >= max_events:
                    print(f"\n── Reached {max_events} events, stopping. ──")
                    return


def parse_sse(raw: str) -> dict | None:
    """Parse a raw SSE frame into a dict."""
    data_lines = []
    event_type = "message"

    for line in raw.strip().split("\n"):
        if line.startswith("data: "):
            data_lines.append(line[6:])
        elif line.startswith("event: "):
            event_type = line[7:]

    if not data_lines:
        return None

    try:
        payload = json.loads("".join(data_lines))
        payload["_event_type"] = event_type
        return payload
    except json.JSONDecodeError:
        return None


def display_event(n: int, event: dict):
    """Pretty-print a governance event."""
    decision = event.get("decision", "?")
    tool = event.get("tool", "?")
    risk = event.get("risk_score", "?")
    agent = event.get("agent_id", "?")

    icon = {
        "allow": "✅",
        "block": "🛑",
        "review": "⚠️",
    }.get(decision, "❔")

    print(f"  {icon} [{n:03d}] {decision:8s} │ {tool:25s} │ "
          f"risk={risk:>3} │ agent={agent}")

    # Extra detail for blocks
    if decision == "block":
        explanation = event.get("explanation", "")
        if explanation:
            print(f"           └─ {explanation[:80]}")


# ── Run ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Graceful Ctrl+C
    signal.signal(signal.SIGINT, lambda *_: (print("\n👋 Disconnected."), sys.exit(0)))

    try:
        stream_events(max_events=50)
    except httpx.ConnectError:
        print(f"❌ Could not connect to {GOVERNOR_URL}")
        print("   Is the Governor service running?")
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP {e.response.status_code}: {e.response.text[:200]}")
