#!/usr/bin/env python3
"""
Recipe 03 - LangChain Tool Wrapper
==================================
Wrap LangChain tools with AIRG so every invocation is evaluated before the
underlying tool runs.

    pip install airg-client langchain langchain-community
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY="<your AIRG account API key>"
    python 03_langchain_tool_wrapper.py
"""
from __future__ import annotations

import secrets
from typing import Any

from airg import AIRG, BlockedError
from langchain_core.tools import BaseTool, ToolException


SESSION_ID = f"langchain-tools-{secrets.token_hex(4)}"


def explain(decision: dict[str, Any]) -> str:
    categories = decision.get("categories") or decision.get("risk_categories") or []
    label = f"{decision['decision']} risk={decision['risk_score']}/100"
    if categories:
        label += f" categories={','.join(categories)}"
    return label


class GovernedTool(BaseTool):
    """A LangChain BaseTool wrapper with pre-execution AIRG governance."""

    inner_tool: BaseTool
    governor: AIRG
    agent_id: str = "langchain-agent"
    session_id: str = SESSION_ID
    name: str = ""
    description: str = ""

    def __init__(self, inner_tool: BaseTool, governor: AIRG, **kwargs: Any):
        super().__init__(
            inner_tool=inner_tool,
            governor=governor,
            name=inner_tool.name,
            description=inner_tool.description,
            **kwargs,
        )

    def _evaluate(self, tool_input: Any) -> dict[str, Any]:
        args = tool_input if isinstance(tool_input, dict) else {"input": tool_input}
        try:
            decision = self.governor.evaluate(
                tool=self.inner_tool.name,
                args=args,
                context={
                    "agent_id": self.agent_id,
                    "session_id": self.session_id,
                    "framework": "langchain",
                    "allowed_tools": [self.inner_tool.name],
                },
            )
        except BlockedError as exc:
            raise ToolException(f"AIRG blocked {self.inner_tool.name}: {exc}") from exc

        print(f"  AIRG {self.inner_tool.name}: {explain(decision)}")

        if decision["decision"] == "block":
            raise ToolException("AIRG blocked this tool call. Do not execute it.")
        if decision["decision"] == "review":
            raise ToolException("AIRG requires human review before this tool can run.")

        return decision

    def _run(self, *args: Any, **kwargs: Any) -> str:
        tool_input = kwargs or (args[0] if args else {})
        self._evaluate(tool_input)
        return self.inner_tool._run(*args, **kwargs)

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        tool_input = kwargs or (args[0] if args else {})
        self._evaluate(tool_input)
        if hasattr(self.inner_tool, "_arun"):
            return await self.inner_tool._arun(*args, **kwargs)
        return self.inner_tool._run(*args, **kwargs)


if __name__ == "__main__":
    from langchain_community.tools import ShellTool

    gov = AIRG()
    shell = GovernedTool(
        inner_tool=ShellTool(),
        governor=gov,
        agent_id="langchain-shell-agent",
    )

    for label, command in [
        ("safe command", "echo hello"),
        ("secret access", "cat ~/.env"),
        ("destructive command", "rm -rf /"),
    ]:
        print(f"\n--- {label} ---")
        try:
            result = shell.run({"commands": command})
            print(f"  Output: {result}")
        except ToolException as exc:
            print(f"  Not executed: {exc}")
