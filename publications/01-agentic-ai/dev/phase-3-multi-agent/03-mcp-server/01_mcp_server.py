"""
phase-3-multi-agent/03-mcp-server/01_mcp_server.py

Layer 5 — Inter-Agent Protocols: MCP (Model Context Protocol).

MCP is the standardised protocol for how agents talk to TOOLS.
Instead of hardcoding tool implementations inside your agent,
you expose them as an MCP server — any MCP-compatible agent can
then discover and call them via a standard interface.

Think of MCP as "USB for AI tools":
  Without MCP: each agent has custom tool integrations (n × m problem)
  With MCP:    tools speak one protocol; any agent connects to any tool

This file:
  1. Defines an MCP server with three tools using the official 'mcp' SDK
  2. Shows the server schema (what a client agent would discover)
  3. Demonstrates a conceptual client call

Paper reference: §7 Inter-Agent Protocols — MCP (agent→tool)
MCP spec: https://modelcontextprotocol.io/

Run:
    cd publications/01-agentic-ai/dev
    python phase-3-multi-agent/03-mcp-server/01_mcp_server.py

Note: This runs the MCP server in stdio transport mode (local process).
For a network-accessible server, swap to SSE transport.
"""

import sys
import json
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()

# ── Check MCP SDK availability ─────────────────────────────────────────
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types as mcp_types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    console.print(
        "[yellow]mcp package not installed. Run: pip install mcp[/yellow]\n"
        "Showing conceptual demo instead."
    )


# ── Tool implementations (the actual logic) ────────────────────────────
def _calculator(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))  # nosec
    except Exception as exc:
        return f"Error: {exc}"


def _get_today() -> str:
    return date.today().isoformat()


def _paper_info(query: str) -> str:
    facts = {
        "title":   "Perceive, Plan, Act, Self-Correct: An Architectural Framework for Goal-Directed Agentic AI Systems",
        "author":  "Hameem M Mahdi",
        "doi":     "10.31224/6738",
        "journal": "Artificial Intelligence (Elsevier, IF ~14.4)",
        "status":  "Preprint accepted March 2026; peer review April 2026",
    }
    q = query.lower()
    for key, value in facts.items():
        if key in q or key[:4] in q:
            return f"{key}: {value}"
    return json.dumps(facts)


# ── MCP Server definition ──────────────────────────────────────────────
def create_mcp_server():
    """Build and return an MCP server exposing three research tools."""
    server = Server("agentic-ai-research-tools")

    @server.list_tools()
    async def list_tools() -> list[mcp_types.Tool]:
        """Advertise available tools to any connecting MCP client."""
        return [
            mcp_types.Tool(
                name="calculator",
                description="Evaluate a Python arithmetic expression.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Python math expression"},
                    },
                    "required": ["expression"],
                },
            ),
            mcp_types.Tool(
                name="get_today",
                description="Returns today's date in ISO 8601 format.",
                inputSchema={"type": "object", "properties": {}},
            ),
            mcp_types.Tool(
                name="paper_info",
                description="Look up facts about the PPAS paper (title, author, doi, journal, status).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What to look up (e.g. 'doi', 'title')"},
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[mcp_types.TextContent]:
        """Route an incoming tool call to the correct implementation."""
        if name == "calculator":
            result = _calculator(arguments["expression"])
        elif name == "get_today":
            result = _get_today()
        elif name == "paper_info":
            result = _paper_info(arguments.get("query", ""))
        else:
            result = f"Unknown tool: {name}"

        return [mcp_types.TextContent(type="text", text=result)]

    return server


# ── Conceptual client demo (shown when running directly) ───────────────
def show_conceptual_demo():
    """
    Illustrate what MCP looks like from a client's perspective
    without needing a running server connection.
    """
    console.print(Rule("[bold]MCP Protocol — Conceptual Demo[/bold]"))

    console.print(Panel(
        "[bold]What the MCP server advertises to connecting agents:[/bold]\n\n"
        '  Tool: calculator\n'
        '    input: {"expression": "string"}\n\n'
        '  Tool: get_today\n'
        '    input: {}\n\n'
        '  Tool: paper_info\n'
        '    input: {"query": "string"}',
        title="Server Schema (list_tools response)",
    ))

    # Simulate tool calls
    calls = [
        ("calculator",  {"expression": "7300 * (1.39 ** 9)"}),
        ("get_today",   {}),
        ("paper_info",  {"query": "doi"}),
    ]

    console.print(Rule("[dim]Simulated tool calls[/dim]"))
    for tool_name, args in calls:
        if tool_name == "calculator":
            result = _calculator(args["expression"])
        elif tool_name == "get_today":
            result = _get_today()
        else:
            result = _paper_info(args.get("query", ""))

        console.print(f"  [yellow]call_tool[/yellow]({tool_name!r}, {args})")
        console.print(f"  [green]→ {result}[/green]\n")


async def run_server():
    """Run the MCP server over stdio (for use with an MCP client)."""
    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    show_conceptual_demo()

    if MCP_AVAILABLE:
        console.print(
            "\n[bold]To run as a real MCP server (stdio transport):[/bold]\n"
            "  import asyncio; asyncio.run(run_server())\n\n"
            "Then connect any MCP-compatible client (e.g. Claude Desktop, or a LangChain MCP client)."
        )
