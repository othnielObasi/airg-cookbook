# AIRG Agentic Use Cases

Four production-grade agentic scenarios with step-by-step governance.  
**Run them directly in Google Colab** — click the badge to launch.

## Quick Launch

| # | Use Case | Open in Colab |
|---|----------|:---:|
| 1 | **Governed Customer Support Agent** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/01_customer_support_agent.ipynb) |
| 2 | **Research Agent with Kill Switch** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/02_research_agent_killswitch.ipynb) |
| 3 | **Multi-Agent Chain Detection** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/03_multi_agent_chain_detection.ipynb) |
| 4 | **Code Gen Agent + Verification** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/othnielObasi/airg-cookbook/blob/main/use_cases/04_codegen_agent_verification.ipynb) |

## Setup (all use cases)

```bash
pip install airg-client httpx
```

Set your environment variables (or use Colab Secrets 🔑):

```python
import os
os.environ["GOVERNOR_API_KEY"] = "your-api-key"
os.environ["GOVERNOR_URL"]     = "https://api.airg.nov-tia.com"
```

---

## Use Cases

### 1. Governed Customer Support Agent
A support chatbot that looks up users, searches a knowledge base, and drafts emails — governed to prevent PII leakage and prompt injection.

| Scenario | What Happens |
|---|---|
| Normal flow | Lookup → search → email reply ✅ |
| PII leakage | SSN in output → flagged by scan ⚠️ |
| Prompt injection | Malicious query → blocked 🛑 |
| Dangerous tool | Shell exec → blocked by policy 🛑 |

### 2. Research Agent with Kill Switch
An autonomous research agent that crawls the web unsupervised. When it goes rogue, the automated kill switch halts all operations.

| Phase | What Happens |
|---|---|
| Normal research | Browse, read, write ✅ |
| Recon attack | /etc/passwd, cloud metadata ⚠️ |
| Auto kill switch | Block rate ≥ 40% → all halted 🔴 |
| Resume | Admin resumes operations 🟢 |

### 3. Multi-Agent Pipeline with Chain Detection
Three agents (Planner → Executor → Reporter) collaborate on tasks. AIRG detects attack chains across agent boundaries.

| Pipeline | Agents | Chain Detected |
|---|---|---|
| Benign research | 3 agents cooperating | No chain ✅ |
| Attack chain | recon → pivot → exfil | Detected & blocked 🔗🛑 |

### 4. Code Generation Agent with Verification
A coding assistant that generates, scans, executes, and verifies code — demonstrating the full evaluate → execute → verify lifecycle.

| Layer | Protection |
|---|---|
| Pre-eval | Blocks dangerous intent (rm -rf, env dump) |
| Output scan | Catches secrets & PII in generated code |
| Post-verify | Detects scope violations after execution |
