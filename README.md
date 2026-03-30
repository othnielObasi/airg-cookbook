# AIRG Cookbook

Practical, runnable recipes showing how to integrate the **AI Runtime Governor**
into real-world agent systems.

Every recipe is self-contained — copy it, set two env vars, and run.

```bash
export GOVERNOR_URL=https://api.airg.nov-tia.com   # or http://localhost:8000
export GOVERNOR_API_KEY=airg_your_key_here
```

---

## Recipes

### Getting Started

| # | Recipe | Language | Description |
|---|--------|----------|-------------|
| 1 | [Quick Start](01_quick_start.py) | Python | Your first `evaluate()` call in 10 lines |
| 2 | [Quick Start (TypeScript)](02_quick_start.ts) | TypeScript | Same thing, TypeScript edition |

### Agent Framework Integrations

| # | Recipe | Language | Description |
|---|--------|----------|-------------|
| 3 | [LangChain Tool Wrapper](03_langchain_tool_wrapper.py) | Python | Wrap any LangChain tool with governance |
| 4 | [OpenAI Function Calling](04_openai_function_calling.py) | Python | Govern OpenAI tool_calls before execution |
| 5 | [CrewAI Governed Agent](05_crewai_governed_agent.py) | Python | Drop-in AIRG middleware for CrewAI |
| 6 | [Anthropic Tool Use](06_anthropic_tool_use.py) | Python | Govern Claude's tool_use blocks |

### Safety & Compliance

| # | Recipe | Language | Description |
|---|--------|----------|-------------|
| 7 | [Output Verification](07_output_verification.py) | Python | Verify tool results post-execution |
| 8 | [PII & Content Scanning](08_pii_content_scanning.py) | Python | Scan user input and agent output |
| 9 | [Human-in-the-Loop Review](09_human_in_the_loop.py) | Python | Hold execution for human approval |
| 10 | [Budget & Rate Controls](10_budget_rate_controls.py) | Python | Per-agent spending guardrails |

### Observability & Operations

| # | Recipe | Language | Description |
|---|--------|----------|-------------|
| 11 | [Trace Observability](11_trace_observability.py) | Python | Ingest spans, query traces, correlate governance |
| 12 | [Real-Time SSE Monitoring](12_realtime_sse_monitoring.py) | Python | Live dashboard feed from the event stream |
| 13 | [Policy as Code](13_policy_as_code.py) | Python | Create, version, and manage policies programmatically |
| 14 | [Kill Switch & Emergencies](14_kill_switch_emergencies.py) | Python | Automated kill switch patterns |

### Advanced

| # | Recipe | Language | Description |
|---|--------|----------|-------------|
| 15 | [MCP Server Integration](15_mcp_integration.py) | Python | Use AIRG via the Model Context Protocol |
| 16 | [Multi-Agent Governance](16_multi_agent_governance.py) | Python | Chain detection across cooperating agents |
| 17 | [Compliance Reporting](17_compliance_reporting.py) | Python | Export EU AI Act & NIST compliance reports |

### Security Deep Dives

| # | Recipe | Language | Description |
|---|--------|----------|-------------|
| 18 | [Injection Firewall](18_injection_firewall.py) | Python | Test 6 attack vectors: DAN, unicode, encoded payloads |
| 19 | [PII Scanner & Redaction](19_pii_scanner.py) | Python | Field-level PII detection with confidence scores |
| 20 | [Agent Fingerprinting & Drift](20_fingerprinting_drift.py) | Python | Behavioural baselines and drift detection |
| 21 | [SURGE Receipt Verification](21_receipt_verification.py) | Python | Ed25519-signed receipts and chain integrity |
| 22 | [Chain Analysis & Patterns](22_chain_analysis.py) | Python | Multi-step attack chain detection |
| 23 | [Impact Assessment & Reporting](23_impact_assessment.py) | Python | 30-day risk reports with percentiles |

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
| `GOVERNOR_API_KEY` | Yes | Your API key (`airg_…`) |
| `OPENAI_API_KEY` | Recipe 4 only | For OpenAI function calling |
| `ANTHROPIC_API_KEY` | Recipe 6 only | For Claude tool use |

## Contributing a Recipe

1. Name it `NN_descriptive_name.py`
2. Keep it self-contained — one file, minimal deps
3. Include a docstring explaining what it demonstrates
4. Print governance decisions so the output is educational
5. Add it to the table above
