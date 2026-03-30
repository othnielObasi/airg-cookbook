#!/usr/bin/env python3
"""
Recipe 21 — SURGE Receipt Verification
========================================
Cryptographic proof of governance. Every evaluation produces an
Ed25519-signed receipt with a hash chain. Verify individual receipts,
check chain integrity, and export compliance bundles.

    pip install httpx
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY=airg_...
    python 21_receipt_verification.py
"""
from __future__ import annotations
import os, httpx

url = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com")
headers = {"X-API-Key": os.environ["GOVERNOR_API_KEY"]}

# ── 1. Check SURGE V2 chain status ─────────────────────────────
print("🔐 SURGE V2 — Chain Status\n")

status = httpx.get(f"{url}/surge/v2/status", headers=headers).json()
print(f"  Chain length     : {status['chain_length']}")
print(f"  Signing algorithm: {status.get('signing_algorithm', 'Ed25519')}")

# ── 2. Verify the entire chain ─────────────────────────────────
print(f"\n{'─'*60}")
print("🔗 Chain Integrity Verification\n")

verify = httpx.get(f"{url}/surge/v2/verify", headers=headers).json()
print(f"  Chain intact     : {'✅' if verify['valid'] else '❌'} {verify['valid']}")
print(f"  Receipts checked : {verify['receipts_checked']}")
print(f"  Broken links     : {verify['broken_links']}")

# ── 3. Get latest receipt and verify individually ───────────────
print(f"\n{'─'*60}")
print("📜 Single Receipt Verification\n")

receipts = httpx.get(f"{url}/surge/v2/receipts?limit=1",
                     headers=headers).json()

if receipts:
    rid = receipts[0]["id"]
    rv = httpx.get(f"{url}/surge/v2/receipt/{rid}/verify",
                   headers=headers).json()
    print(f"  Receipt ID       : {rid}")
    print(f"  Digest valid     : {'✅' if rv['digest_valid'] else '❌'}")
    print(f"  Chain link valid : {'✅' if rv['chain_link_valid'] else '❌'}")
    print(f"  Signature valid  : {'✅' if rv['signature_valid'] else '❌'}")
    print(f"  Compliance tags  : {receipts[0].get('compliance_tags', [])}")
else:
    print("  No receipts yet — run some evaluations first.")

# ── 4. Export compliance bundle ─────────────────────────────────
print(f"\n{'─'*60}")
print("📦 Compliance Export Bundle\n")

export = httpx.get(f"{url}/surge/v2/export", headers=headers).json()
print(f"  Total receipts: {export['total_receipts']}")
print(f"  Block rate    : {export['summary']['block_rate_pct']}%")
print(f"  Export format : JSON (ready for SOC2 / ISO 27001)")
