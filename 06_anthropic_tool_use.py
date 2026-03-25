#!/usr/bin/env python3
"""
Recipe 06 — Anthropic Tool Use with Governance
================================================
Govern Claude's tool_use blocks before executing them,
then return tool_result with governance metadata.

    pip install airg-client anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python 06_anthropic_tool_use.py
"""
from __future__ import annotations

import json

from airg import AIRG, BlockedError
from anthropic import Anthropic

gov = AIRG()
claude = Anthropic()

# ── Define tools for Claude ─────────────────────────────────────
TOOLS = [
    {
        "name": "lookup_stock",
        "description": "Look up stock price by ticker symbol.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "execute_trade",
        "description": "Execute a stock trade.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "action": {"type": "string", "enum": ["buy", "sell"]},
                "shares": {"type": "integer"},
            },
            "required": ["ticker", "action", "shares"],
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    if name == "lookup_stock":
        return json.dumps({"ticker": args["ticker"], "price": 182.50, "change": "+1.2%"})
    if name == "execute_trade":
        return json.dumps({"status": "filled", "ticker": args["ticker"],
                           "shares": args["shares"], "price": 182.50})
    return json.dumps({"error": "Unknown tool"})


# ── Governed conversation ───────────────────────────────────────
def run_agent(user_message: str):
    print(f"\n{'='*60}")
    print(f"User: {user_message}")
    print("="*60)

    messages = [{"role": "user", "content": user_message}]

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )

    # Process tool_use blocks
    while response.stop_reason == "tool_use":
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        tool_results = []

        for block in tool_use_blocks:
            name = block.name
            args = block.input
            print(f"\n── Tool call: {name}({json.dumps(args)}) ──")

            # ★ AIRG governance gate ★
            try:
                decision = gov.evaluate(tool=name, args=args)
                status = decision["decision"]
                print(f"   Governor: {status} (risk: {decision['risk_score']})")

                if status == "block":
                    content = json.dumps({"error": "Blocked by governance policy."})
                    is_error = True
                else:
                    content = execute_tool(name, args)
                    is_error = False
                    print(f"   Result:   {content[:100]}")

            except BlockedError as e:
                print(f"   Governor: 🛑 BLOCKED — {e}")
                content = json.dumps({"error": str(e)})
                is_error = True

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": content,
                "is_error": is_error,
            })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

    # Final text response
    text = "".join(b.text for b in response.content if hasattr(b, "text"))
    print(f"\nAssistant: {text}")


if __name__ == "__main__":
    # Safe — stock lookup
    run_agent("What's the current price of AAPL?")

    # Risky — large trade
    run_agent("Buy 10,000 shares of AAPL right now.")
