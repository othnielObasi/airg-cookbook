# AIRG Cookbook

Implementation recipes for integrating the **AI Runtime Governor** into
agent applications, tool-calling frameworks, and operational governance
workflows.

The examples show where AIRG belongs in modern agent architecture:
immediately before a tool, function, API call, file operation, model gateway
request, agent-to-agent delegation, or other external action is executed.
Each recipe is self-contained and uses account-specific credentials from
environment variables.

```bash
export GOVERNOR_URL=https://api.airg.nov-tia.com   # or http://localhost:8000
export GOVERNOR_API_KEY="<your AIRG account API key>"
export AIRG_GATEWAY_URL=https://gateway.airg.nov-tia.com
```

## Current AIRG Surfaces Covered

| Surface | Cookbook Coverage |
|---------|-------------------|
| SDK/direct `/actions/evaluate` governance | Recipes 1-23 |
| Post-execution `/actions/verify` | Recipe 7 |
| Gateway mode for tools/APIs/MCP-style traffic | Recipe 24 |
| OpenAI-compatible LLM gateway | Recipe 25 |
| Controlled agent mesh and `call_agent` governance | Recipe 26 |
| Multi-hop supervisor -> specialist delegation | Recipe 27 |
| Canary health and context isolation | Recipe 28 |

---

## Recipes

Recipes 1-23 have both script and Google Colab notebook versions. Recipes
24-28 cover the newest production AIRG surfaces and are currently script-first
so they can track the live gateway, mesh, delegation, and canary APIs quickly.
Use scripts for local development and notebooks when you want a browser
runnable walkthrough.

### Getting Started

| # | Recipe | Notebook | Language | Description |
|---|--------|----------|----------|-------------|
| 1 | [Quick Start](01_quick_start.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/01_quick_start.ipynb) | Python | Create an AIRG client and evaluate safe vs blocked tool calls |
| 2 | [Quick Start (TypeScript)](02_quick_start.ts) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/02_quick_start.ipynb) | TypeScript | Same client pattern using the TypeScript SDK |

### Agent Framework Integrations

| # | Recipe | Notebook | Language | Description |
|---|--------|----------|----------|-------------|
| 3 | [LangChain Tool Wrapper](03_langchain_tool_wrapper.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/03_langchain_tool_wrapper.ipynb) | Python | Wrap sync/async LangChain tools; stop on `block` and pause on `review` |
| 4 | [OpenAI Responses Tool Calling](04_openai_function_calling.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/04_openai_function_calling.ipynb) | Python | Govern OpenAI Responses API function calls before execution |
| 5 | [CrewAI Governed Agent](05_crewai_governed_agent.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/05_crewai_governed_agent.ipynb) | Python | CrewAI BaseTool pattern with AIRG pre-execution checks |
| 6 | [Anthropic Tool Use](06_anthropic_tool_use.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/06_anthropic_tool_use.ipynb) | Python | Govern Claude's tool_use blocks |

### Safety & Compliance

| # | Recipe | Notebook | Language | Description |
|---|--------|----------|----------|-------------|
| 7 | [Output Verification](07_output_verification.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/07_output_verification.ipynb) | Python | Verify tool results post-execution |
| 8 | [PII & Content Scanning](08_pii_content_scanning.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/08_pii_content_scanning.ipynb) | Python | Scan user input and agent output |
| 9 | [Human-in-the-Loop Review](09_human_in_the_loop.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/09_human_in_the_loop.ipynb) | Python | Hold execution for human approval |
| 10 | [Budget & Rate Controls](10_budget_rate_controls.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/10_budget_rate_controls.ipynb) | Python | Per-agent spending guardrails |

### Observability & Operations

| # | Recipe | Notebook | Language | Description |
|---|--------|----------|----------|-------------|
| 11 | [Trace Observability](11_trace_observability.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/11_trace_observability.ipynb) | Python | Ingest spans, query traces, correlate governance |
| 12 | [Real-Time SSE Monitoring](12_realtime_sse_monitoring.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/12_realtime_sse_monitoring.ipynb) | Python | Live dashboard feed from the event stream |
| 13 | [Policy as Code](13_policy_as_code.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/13_policy_as_code.ipynb) | Python | Create, version, and manage policies programmatically |
| 14 | [Kill Switch & Emergencies](14_kill_switch_emergencies.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/14_kill_switch_emergencies.ipynb) | Python | Automated kill switch patterns |

### Advanced

| # | Recipe | Notebook | Language | Description |
|---|--------|----------|----------|-------------|
| 15 | [MCP Server Integration](15_mcp_integration.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/15_mcp_integration.ipynb) | Python | Use AIRG via the Model Context Protocol |
| 16 | [Multi-Agent Governance](16_multi_agent_governance.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/16_multi_agent_governance.ipynb) | Python | Chain detection across cooperating agents |
| 17 | [Compliance Reporting](17_compliance_reporting.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/17_compliance_reporting.ipynb) | Python | Export EU AI Act & NIST compliance reports |

### Enterprise Gateway & Multi-Agent Governance

| # | Recipe | Notebook | Language | Description |
|---|--------|----------|----------|-------------|
| 24 | [Gateway Mode](24_gateway_mode.py) | Script first | Python | Call approved enterprise upstream routes through AIRG Gateway |
| 25 | [OpenAI-Compatible Gateway](25_openai_compatible_gateway.py) | Script first | Python | Use AIRG's `/v1/chat/completions` compatible gateway surface |
| 26 | [Controlled Agent Mesh](26_controlled_agent_mesh.py) | Script first | Python | Register agents and govern `call_agent` with mesh policies |
| 27 | [Multi-Hop Delegation](27_multi_hop_delegation.py) | Script first | Python | Validate supervisor -> specialist -> tool chains with `parent_action_id` |
| 28 | [Canary Health & Context Isolation](28_canary_and_context_isolation.py) | Script first | Python | Check detector canaries and pass stable tenant-safe context |

### Security Deep Dives

| # | Recipe | Notebook | Language | Description |
|---|--------|----------|----------|-------------|
| 18 | [Injection Firewall](18_injection_firewall.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/18_injection_firewall.ipynb) | Python | Test 6 attack vectors: DAN, unicode, encoded payloads |
| 19 | [PII Scanner & Redaction](19_pii_scanner.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/19_pii_scanner.ipynb) | Python | Field-level PII detection with confidence scores |
| 20 | [Agent Fingerprinting & Drift](20_fingerprinting_drift.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/20_fingerprinting_drift.ipynb) | Python | Behavioural baselines and drift detection |
| 21 | [SURGE Receipt Verification](21_receipt_verification.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/21_receipt_verification.ipynb) | Python | Ed25519-signed receipts and chain integrity |
| 22 | [Chain Analysis & Patterns](22_chain_analysis.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/22_chain_analysis.ipynb) | Python | Multi-step attack chain detection |
| 23 | [Impact Assessment & Reporting](23_impact_assessment.py) | [Colab](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/23_impact_assessment.ipynb) | Python | 30-day risk reports with percentiles |

---

## Use Case Notebooks (Google Colab)

Runnable end-to-end scenarios — click the badge to open in Colab.

| # | Use Case | Notebook |
|---|----------|----------|
| 1 | Governed Customer Support Agent | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/01_customer_support_agent.ipynb) |
| 2 | Research Agent Kill Switch | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/02_research_agent_killswitch.ipynb) |
| 3 | Multi-Agent Chain Detection | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/03_multi_agent_chain_detection.ipynb) |
| 4 | Codegen Agent Verification | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/04_codegen_agent_verification.ipynb) |
| 5 | Prompt Injection Red Team | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/05_prompt_injection_red_team.ipynb) |
| 6 | Credential Exfiltration | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/06_credential_exfiltration.ipynb) |
| 7 | Privilege Escalation Chain | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/07_privilege_escalation_chain.ipynb) |
| 8 | Budget Exhaustion DoS | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/08_budget_exhaustion_dos.ipynb) |
| 9 | HIPAA/GDPR Compliance | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/09_hipaa_gdpr_compliance.ipynb) |
| 10 | Scope Jailbreak | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/10_scope_jailbreak.ipynb) |
| 19 | PII Scanner & Redaction | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/19_pii_scanner_redaction.ipynb) |
| 20 | Agent Fingerprinting & Drift | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/20_fingerprinting_drift.ipynb) |
| 21 | SURGE Receipt Verification | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/21_surge_receipt_verification.ipynb) |
| 22 | Chain Analysis & Patterns | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/22_chain_analysis.ipynb) |
| 23 | Impact Assessment & Reporting | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/23_impact_assessment.ipynb) |

---

## Prerequisites

```bash
pip install airg-client httpx          # Python recipes
npm install @othnielobasi/airg-client  # TypeScript recipes
```

Some recipes use additional libraries (noted in each file):
- `langchain` / `langchain-openai` — Recipe 3
- `openai` — Recipe 4
- `crewai` — Recipe 5
- `anthropic` — Recipe 6

## AIRG Client Initialization

In Python examples, `AIRG()` is the SDK client from the `airg-client` package:

```python
from airg import AIRG

client = AIRG()
```

By default, `AIRG()` reads:

| Variable | Purpose |
|----------|---------|
| `GOVERNOR_URL` | AIRG API base URL, for example `https://api.airg.nov-tia.com` |
| `GOVERNOR_API_KEY` | API key from your registered AIRG account |
| `AIRG_GATEWAY_URL` | AIRG Gateway base URL, for example `https://gateway.airg.nov-tia.com` |
| `AIRG_TOKEN` | Optional JWT/API key for admin/operator API recipes |

The client sends evaluation requests to AIRG. The most important method is:

```python
decision = client.evaluate(
    tool="read_file",
    args={"path": "/tmp/report.csv"},
    context={"agent_id": "example-agent", "session_id": "session-123"},
)
```

`decision` contains the runtime governance result: `allow`, `review`, or
`block`, plus the risk score and explanation fields.

## Framework Integration Pattern

For OpenAI, LangChain, CrewAI, Anthropic, or any other agent framework, AIRG
should sit directly before tool execution:

```text
model / agent proposes tool call
        ↓
AIRG evaluates tool + args + context
        ↓
allow  → execute the tool
review → pause, queue, or return a needs-approval tool result
block  → do not execute the tool
```

Use `injection_categories` only for injection-specific explanations. For all
runtime risks, read `categories` / `risk_categories` and `risk_factors`.

Always pass useful context:

```python
context={
    "agent_id": "my-agent",
    "session_id": "session-123",
    "framework": "openai_responses",  # or langchain, crewai, anthropic
    "allowed_tools": ["search_web", "write_file"],
}
```

This gives AIRG enough information for per-agent policy, traces, chain
detection, drift, and review workflows.

For multi-hop delegation recipes, child actions should also carry parent
correlation fields:

```python
context={
    "agent_id": "database-specialist",
    "session_id": "case-123",
    "parent_action_id": parent_decision["action_id"],
    "parent_trace_id": "trace-123",
    "parent_span_id": "supervisor-delegation",
}
```

For controlled mesh recipes, register agents through `/agent-mesh/agents`
before using `tool="call_agent"`. AIRG blocks unregistered, inactive, or
unapproved peer calls by default.

## Running a Recipe

```bash
cd cookbook
python 01_quick_start.py
```

Each recipe prints clear output showing the governance decision, risk score,
and any policy matches — so you can see exactly what AIRG is doing.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOVERNOR_URL` | Yes | Governor API base URL |
| `GOVERNOR_API_KEY` | Yes | Your API key from your registered AIRG account |
| `AIRG_GATEWAY_URL` | Recipes 24-25 | Gateway base URL |
| `AIRG_TOKEN` | Recipes 26 and 28 | JWT or API key with operator/admin permissions |
| `OPENAI_API_KEY` | Recipe 4 only | For OpenAI function calling |
| `ANTHROPIC_API_KEY` | Recipe 6 only | For Claude tool use |

## Contributing a Recipe

1. Name it `NN_descriptive_name.py`
2. Keep it self-contained — one file, minimal deps
3. Include a docstring explaining what it demonstrates
4. Print governance decisions so the output is educational
5. Add it to the table above
