#!/usr/bin/env python3
# =============================================================================
# Use Case 4 — Code Generation Agent with Output Verification
# =============================================================================
# A coding assistant that generates code, executes it, and returns results.
# AIRG governs the generation step, scans output for secrets/PII, and verifies
# execution results for dangerous side-effects.
#
# Run each cell step-by-step in Google Colab.
#
# Setup:
#   pip install airg-client
#   Set GOVERNOR_API_KEY, GOVERNOR_URL
# =============================================================================

# %% [markdown]
# # 💻 Use Case 4: Code Generation Agent with Output Verification
#
# **Scenario:** A coding assistant generates Python code, runs it in a sandbox,
# and returns execution results to the user. This is high-risk: generated code
# could contain malware, leaked secrets, or destructive operations.
#
# AIRG provides triple protection:
# 1. **Pre-execution governance** — block dangerous tool calls before they run
# 2. **Output scanning** — catch leaked secrets and PII in generated code
# 3. **Post-execution verification** — detect scope violations after execution
#
# **What you'll learn:**
# - The full evaluate → execute → verify lifecycle
# - Output scanning on generated code
# - Human-in-the-loop review for high-risk code execution
# - Policy-based blocking of dangerous patterns

# %% Cell 1 — Install & Configure
# !pip install -q airg-client

import os
import json
import secrets

GOVERNOR_URL = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com")
print(f"✅ Governor URL: {GOVERNOR_URL}")

# %% Cell 2 — Initialize AIRG Client
from airg import AIRG, BlockedError, VerificationError

client = AIRG()

SESSION_ID = f"codegen-{secrets.token_hex(4)}"
AGENT_ID = "codegen-agent-v1"

print(f"✅ Client ready | Session: {SESSION_ID}")

# %% Cell 3 — Simulated Code Generation & Execution

def generate_code(prompt: str) -> str:
    """Simulate LLM code generation (in production, call GPT-4/Claude)."""
    examples = {
        "sort a list": 'data = [3, 1, 4, 1, 5]\nresult = sorted(data)\nprint(f"Sorted: {result}")',
        "read csv": 'import csv\nwith open("data.csv") as f:\n    reader = csv.reader(f)\n    for row in reader:\n        print(row)',
        "api key": 'import os\n# WARNING: hardcoded secret!\nAPI_KEY = "sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX"\nprint(f"Key: {API_KEY}")',
        "delete files": 'import shutil\nshutil.rmtree("/important/data")\nprint("Deleted!")',
        "env secrets": 'import os\nfor k, v in os.environ.items():\n    if "KEY" in k or "SECRET" in k:\n        print(f"{k}={v}")',
        "http request": 'import urllib.request\nresp = urllib.request.urlopen("https://httpbin.org/get")\nprint(resp.read().decode())',
        "scrape emails": 'import re\nhtml = "<p>Contact: alice@corp.com, bob@secret.org, ssn: 123-45-6789</p>"\nemails = re.findall(r"\\S+@\\S+", html)\nprint(f"Found: {emails}")',
    }
    for key, code in examples.items():
        if key in prompt.lower():
            return code
    return f'print("Hello from generated code for: {prompt}")'

def execute_code(code: str) -> str:
    """Simulate code execution in a sandbox."""
    # In production, this would run in a containerized sandbox
    return f"[Sandbox output] Executed {len(code.splitlines())} lines successfully."

print("✅ Code generation tools ready")

# %% Cell 4 — The Full Governance Pipeline

def governed_code_task(task_description: str, risk_label: str = ""):
    """
    Full governance pipeline for code generation:
      1. Evaluate the code generation request
      2. Generate the code
      3. Scan the generated code for secrets/PII
      4. Evaluate the code execution request
      5. Execute in sandbox
      6. Verify execution results
    """
    print(f"\n{'═'*60}")
    print(f"  Task: {task_description}")
    if risk_label:
        print(f"  Risk: {risk_label}")
    print(f"{'═'*60}")

    # ── Phase 1: Evaluate code generation request ──
    print(f"\n  📝 Phase 1: Pre-eval code generation")
    try:
        gen_decision = client.evaluate(
            tool="generate_code",
            args={"prompt": task_description, "language": "python"},
            context={"agent_id": AGENT_ID, "session_id": SESSION_ID},
        )
        risk = gen_decision["risk_score"]
        print(f"     ✅ {gen_decision['decision']} (risk: {risk})")
    except BlockedError as e:
        print(f"     🛑 Code generation BLOCKED: {e}")
        return {"status": "blocked", "phase": "generation"}

    # ── Phase 2: Generate the code ──
    print(f"\n  🤖 Phase 2: Generating code...")
    code = generate_code(task_description)
    print(f"     Generated ({len(code.splitlines())} lines):")
    for line in code.splitlines()[:5]:
        print(f"     │ {line}")
    if len(code.splitlines()) > 5:
        print(f"     │ ... ({len(code.splitlines()) - 5} more lines)")

    # ── Phase 3: Scan generated code for secrets ──
    print(f"\n  🔍 Phase 3: Scanning code for secrets/PII")
    scan = client.scan(text=code, agent_id=AGENT_ID, session_id=SESSION_ID)
    safe = scan.get("safe", True)
    findings = scan.get("findings", [])

    if not safe:
        print(f"     ⚠️  Code flagged! {len(findings)} finding(s):")
        for f in findings:
            icon = {"fail": "🛑", "warn": "⚠️", "pass": "✅"}.get(f.get("result"), " ")
            print(f"     {icon} [{f['check']}] {f['detail'][:60]}")
        sanitized = scan.get("sanitized_text")
        if sanitized and sanitized != code:
            print(f"     🔒 Code sanitized before execution")
            code = sanitized
    else:
        print(f"     ✅ Code is clean")

    # ── Phase 4: Evaluate code execution request ──
    print(f"\n  ⚡ Phase 4: Pre-eval code execution")
    try:
        exec_decision = client.evaluate(
            tool="execute_code",
            args={
                "code": code[:200],  # Truncate for eval
                "language": "python",
                "sandbox": True,
            },
            context={"agent_id": AGENT_ID, "session_id": SESSION_ID},
        )
        print(f"     ✅ {exec_decision['decision']} (risk: {exec_decision['risk_score']})")
        action_id = exec_decision.get("action_id")
    except BlockedError as e:
        print(f"     🛑 Execution BLOCKED: {e}")
        return {"status": "blocked", "phase": "execution", "code": code}

    # ── Phase 5: Execute in sandbox ──
    print(f"\n  🏃 Phase 5: Executing code in sandbox")
    output = execute_code(code)
    print(f"     📤 {output}")

    # ── Phase 6: Post-execution verification ──
    if action_id:
        print(f"\n  🔎 Phase 6: Post-execution verification")
        try:
            verify = client.verify(
                action_id=action_id,
                tool="execute_code",
                result={"output": output, "code": code[:500], "exit_code": 0},
                context={"agent_id": AGENT_ID, "session_id": SESSION_ID},
            )
            checks = verify.get("findings", [])
            passed = sum(1 for f in checks if f.get("result") == "pass")
            failed = sum(1 for f in checks if f.get("result") == "fail")
            print(f"     ✅ Verification: {passed} passed, {failed} failed")
            for f in checks:
                if f.get("result") == "fail":
                    print(f"     🛑 {f['check']}: {f['detail'][:60]}")
        except VerificationError as e:
            print(f"     🛑 VERIFICATION FAILED: {e}")
            return {"status": "violation", "phase": "verification", "output": output}
    else:
        print(f"\n  ℹ️  Phase 6: Skipped (no action_id for verification)")

    print(f"\n  ✅ Task complete: {task_description}")
    return {"status": "success", "code": code, "output": output}

print("✅ Governed code pipeline ready")

# %% Cell 5 — Scenario A: Safe Code Generation
print("=" * 60)
print("SCENARIO A: Safe code tasks")
print("=" * 60)

governed_code_task("Sort a list of numbers", "🟢 LOW")
governed_code_task("Read CSV file and print rows", "🟢 LOW")
governed_code_task("Make an HTTP request to httpbin", "🟡 MEDIUM")

# %% Cell 6 — Scenario B: Code with Leaked Secrets
print("\n" + "=" * 60)
print("SCENARIO B: Generated code contains hardcoded API key")
print("=" * 60)

governed_code_task(
    "Generate code that uses an API key to call a service",
    "🔴 HIGH — leaked secret in code"
)

# %% Cell 7 — Scenario C: Code with PII Exposure
print("\n" + "=" * 60)
print("SCENARIO C: Code that scrapes and exposes PII")
print("=" * 60)

governed_code_task(
    "Scrape emails from HTML content",
    "🔴 HIGH — PII exposure"
)

# %% Cell 8 — Scenario D: Destructive Code Blocked
print("\n" + "=" * 60)
print("SCENARIO D: Destructive code — should be blocked")
print("=" * 60)

governed_code_task(
    "Delete files from the important data directory",
    "🔴 CRITICAL — destructive operation"
)

governed_code_task(
    "Dump all env secrets to stdout",
    "🔴 CRITICAL — credential exfiltration"
)

# %% Cell 9 — Summary Dashboard
print("\n" + "=" * 60)
print("SESSION SUMMARY")
print("=" * 60)

actions = client.list_actions(agent_id=AGENT_ID, limit=20)
print(f"\n  {AGENT_ID} — {len(actions)} total evaluations\n")

stats = {"allow": 0, "block": 0, "review": 0}
for a in actions:
    d = a.get("decision", "?")
    stats[d] = stats.get(d, 0) + 1

total = sum(stats.values())
for decision, count in stats.items():
    bar = "█" * (count * 2) + "░" * (20 - count * 2)
    icon = {"allow": "✅", "block": "🛑", "review": "⚠️"}.get(decision, " ")
    print(f"  {icon} {decision:8s}: {count:3d} |{bar}| {count/max(total,1):.0%}")

print(f"\n  Total: {total} evaluations")
print(f"  💡 Full audit trail available in AIRG Dashboard → Actions tab")

# %% [markdown]
# ## Summary
#
# | Scenario | Code Type | Governance Action |
# |---|---|---|
# | A. Sort/CSV/HTTP | Safe, standard code | ✅ Allowed → executed → verified |
# | B. API key leak | Hardcoded secret in code | ⚠️ Output scan catches secret |
# | C. PII scraper | Exposes emails/SSN | ⚠️ Output scan flags PII |
# | D. Destructive | shutil.rmtree, env dump | 🛑 Blocked before execution |
#
# **The triple protection model:**
# 1. **Pre-eval** catches dangerous *intent* (destructive operations)
# 2. **Output scan** catches dangerous *content* (secrets, PII in code)
# 3. **Post-verify** catches dangerous *results* (scope violations after execution)
#
# No single layer is sufficient — the combination provides defence in depth.
