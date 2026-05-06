#!/usr/bin/env python3
"""
Recipe 05 - CrewAI Governed Agent
=================================
Create CrewAI tools that pass through AIRG before execution.

    pip install airg-client crewai pydantic
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY="<your AIRG account API key>"
    export OPENAI_API_KEY="<your LLM provider key if CrewAI uses OpenAI>"
    python 05_crewai_governed_agent.py
"""
from __future__ import annotations

import secrets
from typing import Any, Callable

from airg import AIRG, BlockedError
from crewai import Agent, Crew, Task
from crewai.tools import BaseTool
from pydantic import PrivateAttr


AGENT_ID = "crewai-research-agent"
SESSION_ID = f"crewai-tools-{secrets.token_hex(4)}"


def explain(decision: dict[str, Any]) -> str:
    categories = decision.get("categories") or decision.get("risk_categories") or []
    label = f"{decision['decision']} risk={decision['risk_score']}/100"
    if categories:
        label += f" categories={','.join(categories)}"
    return label


class GovernedCrewTool(BaseTool):
    """CrewAI BaseTool that evaluates every run through AIRG."""

    _governor: AIRG = PrivateAttr()
    _execute_fn: Callable[..., str] = PrivateAttr()
    _agent_id: str = PrivateAttr(default=AGENT_ID)
    _session_id: str = PrivateAttr(default=SESSION_ID)

    def __init__(
        self,
        name: str,
        description: str,
        execute_fn: Callable[..., str],
        governor: AIRG,
        agent_id: str = AGENT_ID,
        session_id: str = SESSION_ID,
    ):
        super().__init__(name=name, description=description)
        self._governor = governor
        self._execute_fn = execute_fn
        self._agent_id = agent_id
        self._session_id = session_id

    def _run(self, **kwargs: Any) -> str:
        try:
            decision = self._governor.evaluate(
                tool=self.name,
                args=kwargs,
                context={
                    "agent_id": self._agent_id,
                    "session_id": self._session_id,
                    "framework": "crewai",
                    "allowed_tools": ["search_web", "write_file", "delete_file"],
                },
            )
        except BlockedError as exc:
            return f"AIRG blocked {self.name}. Tool was not executed. {exc}"

        print(f"  AIRG {self.name}: {explain(decision)}")

        if decision["decision"] == "block":
            return "AIRG blocked this tool call. Tool was not executed."
        if decision["decision"] == "review":
            return "AIRG requires human review before this tool can run."

        return self._execute_fn(**kwargs)


def search_web(query: str = "") -> str:
    return f"Search results for: {query}"


def write_file(path: str = "", content: str = "") -> str:
    return f"Wrote {len(content)} bytes to {path}"


def delete_file(path: str = "") -> str:
    return f"Deleted {path}"


if __name__ == "__main__":
    gov = AIRG()

    tools = [
        GovernedCrewTool("search_web", "Search the web", search_web, gov),
        GovernedCrewTool("write_file", "Write a local file", write_file, gov),
        GovernedCrewTool("delete_file", "Delete a local file", delete_file, gov),
    ]

    researcher = Agent(
        role="Research Analyst",
        goal="Research AI safety and write only approved outputs.",
        backstory="You are careful, auditable, and always respect governance.",
        tools=tools,
        verbose=True,
    )

    task = Task(
        description=(
            "Research AI safety trends. If you need a tool, use the available "
            "tools and respect any AIRG block or review response."
        ),
        expected_output="A short summary of AI safety trends.",
        agent=researcher,
    )

    crew = Crew(agents=[researcher], tasks=[task], verbose=True)

    print("\nRunning governed CrewAI agent...\n")
    print(crew.kickoff())

    print("\nManual high-risk tool check:")
    print(tools[2]._run(path="/production/customer-data"))
