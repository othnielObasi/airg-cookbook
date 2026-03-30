#!/usr/bin/env python3
"""
Recipe 19 — PII Scanner & Redaction
====================================
Scan tool arguments and outputs for PII — emails, SSNs, credit cards,
phone numbers. Get field-level detection with confidence scores and
see how PII findings boost risk in the evaluation pipeline.

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY=airg_...
    python 19_pii_scanner.py
"""
from __future__ import annotations
import os, httpx

url = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com")
headers = {"X-API-Key": os.environ["GOVERNOR_API_KEY"]}

# ── 1. Scan tool arguments for PII ─────────────────────────────
print("🔍 PII Scan — Detecting sensitive data in tool arguments\n")

r = httpx.post(f"{url}/pii/scan", headers=headers, json={
    "tool": "send_email",
    "args": {
        "to": "john.doe@example.com",
        "body": "SSN: 123-45-6789, CC: 4111-1111-1111-1111",
    },
})
scan = r.json()
print(f"  PII detected  : {scan['has_pii']}")
print(f"  Total findings: {scan['total_findings']}")
print(f"  Risk boost    : +{scan['risk_boost']} points\n")

for f in scan["input_scan"]["findings"]:
    print(f"  📌 {f['entity_type']}: {f['value_redacted']}")
    print(f"     Confidence: {f['confidence']}  Field: {f['field_path']}")

# ── 2. PII integrated into evaluation pipeline ─────────────────
print(f"\n{'─'*60}")
print("📊 PII + Evaluation Pipeline — Risk Boosting\n")

r = httpx.post(f"{url}/actions/evaluate", headers=headers, json={
    "agent_id": "support-bot",
    "tool": "send_message",
    "args": {"text": "Your SSN 123-45-6789 has been verified"},
})
d = r.json()
print(f"  Decision  : {d['decision']}")
print(f"  Risk score: {d['risk_score']}  (boosted by PII detection)")

# ── 3. Clean text — no PII ─────────────────────────────────────
print(f"\n{'─'*60}")
print("✅ Clean Text — No PII\n")

r = httpx.post(f"{url}/pii/scan", headers=headers, json={
    "tool": "search",
    "args": {"query": "weather in Tokyo"},
})
clean = r.json()
print(f"  PII detected  : {clean['has_pii']}")
print(f"  Total findings: {clean['total_findings']}")
print(f"  Risk boost    : +{clean['risk_boost']} points")
