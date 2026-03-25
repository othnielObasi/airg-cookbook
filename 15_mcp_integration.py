#!/usr/bin/env python3
"""
Recipe 15 — MCP Server Integration
====================================
Use AIRG governance via the Model Context Protocol (MCP).
This shows how to connect to AIRG's MCP server from any
MCP-compatible client (Claude Desktop, Cursor, etc.).

    pip install mcp httpx-sse
    python 15_mcp_integration.py
"""
from __future__ import annotations

import asyncio
import json
import os

from mcp import ClientSession
from mcp.client.sse import sse_client

GOVERNOR_URL = os.getenv("GOVERNOR_URL", "http://localhost:8000")
API_KEY = os.getenv("GOVERNOR_API_KEY", "")


async def main():
    # ── Connect to AIRG MCP server ────────────────────────────
    mcp_url = f"{GOVERNOR_URL}/mcp/sse"
    headers = {"X-API-Key": API_KEY} if API_KEY else {}

    print(f"🔌 Connecting to MCP server at {mcp_url}")

    async with sse_client(mcp_url, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ── List available tools ──────────────────────────
            tools = await session.list_tools()
            print(f"\n📋 Available governance tools ({len(tools.tools)}):")
            for tool in tools.tools:
                print(f"   • {tool.name:25s} — {tool.description[:60]}")

            # ── 1. Evaluate a tool call ───────────────────────
            print("\n── evaluate_action ──")
            result = await session.call_tool("evaluate_action", {
                "tool": "shell_exec",
                "parameters": {"command": "ls -la /tmp"},
                "agent_id": "mcp-cookbook-agent",
            })
            data = json.loads(result.content[0].text)
            print(f"   Decision : {data.get('decision')}")
            print(f"   Risk     : {data.get('risk_score')}")

            # ── 2. Scan text for PII ─────────────────────────
            print("\n── scan_pii ──")
            result = await session.call_tool("scan_pii", {
                "text": "My SSN is 123-45-6789 and email is alice@example.com",
            })
            data = json.loads(result.content[0].text)
            entities = data.get("entities", [])
            print(f"   Found {len(entities)} PII entities:")
            for e in entities:
                print(f"   • {e.get('type')}: {e.get('value', '?')[:20]}...")

            # ── 3. Check policies for a tool ─────────────────
            print("\n── check_policy ──")
            result = await session.call_tool("check_policy", {
                "tool": "deploy_contract",
            })
            data = json.loads(result.content[0].text)
            print(f"   Matching policies: {data.get('policy_count', 0)}")
            for p in data.get("matching_policies", []):
                print(f"   • {p.get('name')}: {p.get('action')}")

            # ── 4. Get governance status ─────────────────────
            print("\n── get_governance_status ──")
            result = await session.call_tool("get_governance_status", {})
            data = json.loads(result.content[0].text)
            print(f"   Kill switch : {data.get('kill_switch_engaged')}")
            print(f"   Policies    : {data.get('active_policies')}")
            print(f"   Modules     : {list(data.get('modules', {}).keys())}")

    print("\n✅ MCP session complete.")
    print("\n💡 To use AIRG in Claude Desktop, add this to your config:")
    print(f"""
    {{
      "mcpServers": {{
        "airg": {{
          "url": "{GOVERNOR_URL}/mcp/sse",
          "headers": {{"X-API-Key": "{API_KEY[:8]}..."}}
        }}
      }}
    }}
    """)


if __name__ == "__main__":
    asyncio.run(main())
