#!/usr/bin/env python3
"""
Recipe 21 - SURGE Receipt Verification
======================================
Cryptographic proof of governance. Every evaluation produces an
Ed25519-signed receipt with a hash chain. Verify individual receipts,
check chain integrity, and export compliance bundles.

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY="<your AIRG account API key>"
    python 21_receipt_verification.py
"""
from __future__ import annotations

import os

import httpx


url = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com")
headers = {"X-API-Key": os.environ["GOVERNOR_API_KEY"]}


def response_items(raw, *keys):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in keys + ("items", "receipts", "data", "results"):
            value = raw.get(key)
            if isinstance(value, list):
                return value
    return []


def response_dict(raw):
    return raw if isinstance(raw, dict) else {}


print("SURGE V2 - Chain Status\n")

status = response_dict(httpx.get(f"{url}/surge/v2/status", headers=headers).json())
print(f"  Chain length     : {status.get('chain_length', 'N/A')}")
print(f"  Signing algorithm: {status.get('signing_algorithm', 'Ed25519')}")

print(f"\n{'-' * 60}")
print("Chain Integrity Verification\n")

verify = response_dict(httpx.get(f"{url}/surge/v2/verify", headers=headers).json())
valid = bool(verify.get("valid"))
print(f"  Chain intact     : {valid}")
print(f"  Receipts checked : {verify.get('receipts_checked', 'N/A')}")
print(f"  Broken links     : {verify.get('first_broken_at', 'None')}")

print(f"\n{'-' * 60}")
print("Single Receipt Verification\n")

raw_receipts = httpx.get(
    f"{url}/surge/v2/receipts?limit=1",
    headers=headers,
).json()
receipts = response_items(raw_receipts, "receipts")

if receipts:
    receipt = receipts[0]
    rid = receipt.get("id") or receipt.get("receipt_id")
    rv = response_dict(
        httpx.get(f"{url}/surge/v2/receipts/{rid}/verify", headers=headers).json()
    )
    print(f"  Receipt ID       : {rid}")
    print(f"  Digest valid     : {rv.get('digest_valid', 'N/A')}")
    print(f"  Chain link valid : {rv.get('chain_link_valid', 'N/A')}")
    print(f"  Signature valid  : {rv.get('signature_valid', 'N/A')}")
    print(f"  Compliance tags  : {receipt.get('compliance_tags', [])}")
else:
    print("  No receipts yet - run some evaluations first.")
    if raw_receipts:
        print(f"  Response: {str(raw_receipts)[:300]}")

print(f"\n{'-' * 60}")
print("Compliance Export Bundle\n")

export = response_dict(httpx.get(f"{url}/surge/v2/export", headers=headers).json())
summary = export.get("summary", {}) if isinstance(export.get("summary"), dict) else {}
print(f"  Total receipts: {export.get('total_receipts', 'N/A')}")
print(f"  Block rate    : {summary.get('block_rate_pct', 'N/A')}%")
print("  Export format : JSON (ready for SOC2 / ISO 27001)")
