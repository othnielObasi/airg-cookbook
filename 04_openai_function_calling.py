#!/usr/bin/env python3
"""
Recipe 04 - OpenAI Responses API Tool Calling with AIRG
======================================================
Govern OpenAI tool calls before your application executes them.

This is the important placement:

    model proposes tool call -> AIRG evaluates tool + args -> app executes only if allowed

    pip install airg-client openai
    export GOVERNOR_URL=https://api.airg.nov-tia.com
    export GOVERNOR_API_KEY="<your AIRG account API key>"
    export OPENAI_API_KEY="<your OpenAI API key>"
    python 04_openai_function_calling.py
"""
from __future__ import annotations

import json
import os
import secrets
from typing import Any

from airg import AIRG, BlockedError
from openai import OpenAI


AGENT_ID = "openai-responses-agent"
SESSION_ID = f"openai-tools-{secrets.token_hex(4)}"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

gov = AIRG()
client = OpenAI()


TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_sql",
        "description": "Execute an SQL query on the application database.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
]


def print_decision(tool: str, decision: dict[str, Any]) -> None:
    categories = decision.get("categories") or decision.get("risk_categories") or []
    print(f"   AIRG: {decision['decision']} | risk={decision['risk_score']}/100")
    if categories:
        print(f"   Risk categories: {', '.join(categories)}")
    for factor in decision.get("risk_factors", []):
        print(
            f"     - {factor.get('category')} | {factor.get('severity')} | "
            f"{factor.get('message')}"
        )
    print(f"   Tool: {tool}")


def execute_tool(name: str, args: dict[str, Any]) -> str:
    """Simulated tool executors. Replace with your real application code."""
    if name == "get_weather":
        return json.dumps(
            {"city": args["city"], "temp_f": 72, "condition": "sunny"}
        )
    if name == "run_sql":
        return json.dumps({"rows": [{"id": 1, "name": "example"}]})
    return json.dumps({"error": f"Unknown tool: {name}"})


def governed_tool_output(tool_call: Any) -> dict[str, Any]:
    name = tool_call.name
    args = json.loads(tool_call.arguments or "{}")
    print(f"\nTool call requested: {name}({json.dumps(args)})")

    try:
        decision = gov.evaluate(
            tool=name,
            args=args,
            context={
                "agent_id": AGENT_ID,
                "session_id": SESSION_ID,
                "framework": "openai_responses",
                "allowed_tools": ["get_weather", "run_sql"],
            },
        )
        print_decision(name, decision)
    except BlockedError as exc:
        return {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps({"error": f"Blocked by AIRG: {exc}"}),
        }

    if decision["decision"] == "block":
        output = {"error": "Blocked by AIRG. Do not execute this tool."}
    elif decision["decision"] == "review":
        output = {
            "error": "AIRG requires human review before this tool can run.",
            "risk_score": decision["risk_score"],
            "risk_categories": decision.get("categories", []),
        }
    else:
        output = {"result": execute_tool(name, args)}

    return {
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": json.dumps(output),
    }


def run_agent(user_message: str) -> None:
    print("\n" + "=" * 72)
    print(f"User: {user_message}")
    print("=" * 72)

    response = client.responses.create(
        model=MODEL,
        input=user_message,
        tools=TOOLS,
    )

    for _ in range(4):
        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            print(f"\nAssistant:\n{response.output_text}")
            return

        tool_outputs = [governed_tool_output(call) for call in tool_calls]
        response = client.responses.create(
            model=MODEL,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS,
        )

    print("\nStopped after 4 tool-call rounds to avoid an infinite loop.")


if __name__ == "__main__":
    run_agent("What is the weather in Tokyo?")
    run_agent("Run this database query: DROP TABLE users;")
