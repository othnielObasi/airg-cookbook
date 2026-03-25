#!/usr/bin/env python3
"""
Recipe 04 — OpenAI Function Calling with Governance
====================================================
Intercept OpenAI tool_calls from ChatCompletion, run each through
AIRG governance, execute only approved calls, then feed results back.

    pip install airg-client openai
    export OPENAI_API_KEY=sk-...
    python 04_openai_function_calling.py
"""
from __future__ import annotations

import json
import os

from airg import AIRG, BlockedError
from openai import OpenAI

gov = AIRG()
oai = OpenAI()

# ── Define tools for OpenAI ─────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": "Execute an SQL query on the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
]


# ── Simulated tool executors ────────────────────────────────────
def execute_tool(name: str, args: dict) -> str:
    if name == "get_weather":
        return json.dumps({"city": args["city"], "temp_f": 72, "condition": "sunny"})
    if name == "run_sql":
        return json.dumps({"rows": [{"id": 1, "name": "example"}]})
    return json.dumps({"error": f"Unknown tool: {name}"})


# ── Governed agent loop ─────────────────────────────────────────
def run_agent(user_message: str):
    print(f"\n{'='*60}")
    print(f"User: {user_message}")
    print("="*60)

    messages = [{"role": "user", "content": user_message}]

    response = oai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )

    choice = response.choices[0]

    if choice.finish_reason != "tool_calls":
        print(f"\nAssistant: {choice.message.content}")
        return

    # Process each tool call through governance
    tool_results = []
    for tool_call in choice.message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        print(f"\n── Tool call: {name}({json.dumps(args)}) ──")

        # ★ AIRG governance gate ★
        try:
            decision = gov.evaluate(tool=name, args=args)
            print(f"   Governor: {decision['decision']} "
                  f"(risk: {decision['risk_score']})")

            if decision["decision"] == "block":
                result = json.dumps({"error": "Governance blocked this action."})
            else:
                result = execute_tool(name, args)
                print(f"   Result:   {result[:100]}")

        except BlockedError as e:
            print(f"   Governor: 🛑 BLOCKED — {e}")
            result = json.dumps({"error": str(e)})

        tool_results.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

    # Feed results back to get the final response
    messages.append(choice.message)
    messages.extend(tool_results)

    final = oai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )
    print(f"\nAssistant: {final.choices[0].message.content}")


# ── Run examples ───────────────────────────────────────────
if __name__ == "__main__":
    # Safe — weather lookup
    run_agent("What's the weather in Tokyo?")

    # Risky — SQL query (may trigger policy)
    run_agent("Run this query: DROP TABLE users;")
