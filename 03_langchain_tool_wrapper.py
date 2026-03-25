#!/usr/bin/env python3
"""
Recipe 03 — LangChain Tool Wrapper
===================================
Wrap any LangChain tool with AIRG governance so every invocation is
evaluated before execution.

    pip install airg-client langchain langchain-community
    python 03_langchain_tool_wrapper.py
"""
from __future__ import annotations

import json
from typing import Any, Callable

from airg import AIRG, BlockedError
from langchain_core.tools import BaseTool, ToolException


# ── Governed wrapper ────────────────────────────────────────────
class GovernedTool(BaseTool):
    """Wraps any LangChain tool with AIRG pre-execution governance."""

    inner_tool: BaseTool
    governor: AIRG
    agent_id: str = "langchain-agent"

    name: str = ""
    description: str = ""

    def __init__(self, inner_tool: BaseTool, governor: AIRG, **kwargs):
        super().__init__(
            inner_tool=inner_tool,
            governor=governor,
            name=inner_tool.name,
            description=inner_tool.description,
            **kwargs,
        )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        tool_input = kwargs or (args[0] if args else {})

        # ── Pre-execution governance ──
        try:
            decision = self.governor.evaluate(
                tool=self.inner_tool.name,
                args=tool_input if isinstance(tool_input, dict) else {"input": tool_input},
                context={"agent_id": self.agent_id, "framework": "langchain"},
            )
            print(f"  ✅ {self.inner_tool.name} → {decision['decision']} "
                  f"(risk: {decision['risk_score']})")
        except BlockedError as e:
            print(f"  🛑 {self.inner_tool.name} → BLOCKED")
            raise ToolException(f"Governance blocked: {e}")

        # ── Execute the real tool ──
        return self.inner_tool._run(*args, **kwargs)


# ── Demo ────────────────────────────────────────────────────────
if __name__ == "__main__":
    from langchain_community.tools import ShellTool

    gov = AIRG()

    # Wrap the shell tool
    safe_shell = GovernedTool(inner_tool=ShellTool(), governor=gov)

    # Safe command
    print("─── Safe command ───")
    try:
        result = safe_shell.run({"commands": "echo hello"})
        print(f"  Output: {result}")
    except ToolException as e:
        print(f"  Blocked: {e}")

    # Dangerous command
    print("\n─── Dangerous command ───")
    try:
        result = safe_shell.run({"commands": "rm -rf /"})
        print(f"  Output: {result}")
    except ToolException as e:
        print(f"  Blocked: {e}")
