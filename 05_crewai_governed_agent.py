#!/usr/bin/env python3
"""
Recipe 05 — CrewAI Governed Agent
==================================
Drop-in governance middleware for CrewAI agents. Wraps CrewAI's
tool execution so every tool call is evaluated by AIRG.

    pip install airg-client crewai crewai-tools
    python 05_crewai_governed_agent.py
"""
from __future__ import annotations

from airg import AIRG, BlockedError
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool


# ── Governed base tool ──────────────────────────────────────────
class GovernedBaseTool(BaseTool):
    """A CrewAI tool that passes through AIRG governance before running."""

    name: str = ""
    description: str = ""
    _governor: AIRG = None
    _execute_fn = None

    def __init__(self, name: str, description: str, execute_fn, governor: AIRG):
        super().__init__(name=name, description=description)
        self._governor = governor
        self._execute_fn = execute_fn

    def _run(self, **kwargs) -> str:
        # ★ Governance gate ★
        try:
            decision = self._governor.evaluate(
                tool=self.name,
                args=kwargs,
                context={"framework": "crewai"},
            )
            print(f"  ✅ {self.name} → {decision['decision']} (risk: {decision['risk_score']})")
        except BlockedError as e:
            print(f"  🛑 {self.name} → BLOCKED")
            return f"Error: Governance blocked this tool call — {e}"

        return self._execute_fn(**kwargs)


# ── Example tools ───────────────────────────────────────────────
def search_web(query: str = "") -> str:
    return f"Search results for: {query}"

def write_file(path: str = "", content: str = "") -> str:
    return f"Wrote {len(content)} bytes to {path}"

def delete_file(path: str = "") -> str:
    return f"Deleted {path}"


# ── Build governed crew ────────────────────────────────────────
if __name__ == "__main__":
    gov = AIRG()

    tools = [
        GovernedBaseTool("search_web", "Search the web", search_web, gov),
        GovernedBaseTool("write_file", "Write a file", write_file, gov),
        GovernedBaseTool("delete_file", "Delete a file", delete_file, gov),
    ]

    researcher = Agent(
        role="Research Analyst",
        goal="Research and write a summary about AI safety",
        backstory="You're a diligent researcher.",
        tools=tools,
        verbose=True,
    )

    task = Task(
        description="Research AI safety trends and write a brief summary.",
        expected_output="A short summary of AI safety trends.",
        agent=researcher,
    )

    crew = Crew(agents=[researcher], tasks=[task], verbose=True)

    print("\n🚀 Running governed CrewAI agent...\n")
    result = crew.kickoff()
    print(f"\n📝 Result:\n{result}")
