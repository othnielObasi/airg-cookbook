# AIRG Agentic Use Cases

Four production-grade agentic scenarios with step-by-step governance.  
**Run them in Google Colab** — each file is structured as Colab-ready cells.

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

### 1. [Customer Support Agent](01_customer_support_agent.py)
A support chatbot that looks up users, searches a knowledge base, and drafts emails — governed to prevent PII leakage and prompt injection.

| Scenario | What Happens |
|---|---|
| Normal flow | Lookup → search → email reply ✅ |
| PII leakage | SSN in output → flagged by scan ⚠️ |
| Prompt injection | Malicious query → blocked 🛑 |
| Dangerous tool | Shell exec → blocked by policy 🛑 |

### 2. [Research Agent with Kill Switch](02_research_agent_killswitch.py)
An autonomous research agent that crawls the web unsupervised. When it goes rogue, the automated kill switch halts all operations.

| Phase | What Happens |
|---|---|
| Normal research | Browse, read, write ✅ |
| Recon attack | /etc/passwd, cloud metadata ⚠️ |
| Auto kill switch | Block rate ≥ 40% → all halted 🔴 |
| Resume | Admin resumes operations 🟢 |

### 3. [Multi-Agent Pipeline with Chain Detection](03_multi_agent_chain_detection.py)
Three agents (Planner → Executor → Reporter) collaborate on tasks. AIRG detects attack chains across agent boundaries.

| Pipeline | Agents | Chain Detected |
|---|---|---|
| Benign research | 3 agents cooperating | No chain ✅ |
| Attack chain | recon → pivot → exfil | Detected & blocked 🔗🛑 |

### 4. [Code Generation Agent with Verification](04_codegen_agent_verification.py)
A coding assistant that generates, scans, executes, and verifies code — demonstrating the full evaluate → execute → verify lifecycle.

| Layer | Protection |
|---|---|
| Pre-eval | Blocks dangerous intent (rm -rf, env dump) |
| Output scan | Catches secrets & PII in generated code |
| Post-verify | Detects scope violations after execution |

---

## Running in Google Colab

1. Open [colab.research.google.com](https://colab.research.google.com)
2. File → Upload notebook → Upload the `.py` file
3. Colab auto-detects `# %%` cell markers
4. Run cells top-to-bottom with Shift+Enter
5. Set your API keys in Cell 1

Each use case is self-contained — no dependencies between them.
