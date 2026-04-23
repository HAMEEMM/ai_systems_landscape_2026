"""
phase-2-agent-core/02-tool-integration/01_tool_calling.py

Layer 4 — Tools & Integration: Advanced tool patterns.

Demonstrates:
  1. Web search via Tavily (real external tool — requires TAVILY_API_KEY)
  2. Parallel tool calls (LLM calls multiple tools in a single response)
  3. Tool error handling with graceful degradation
  4. A tool registry pattern for clean dispatch

Paper reference: §4 Layer 4 — Tools & Integration

Run:
    cd publications/01-agentic-ai/dev
    python phase-2-agent-core/02-tool-integration/01_tool_calling.py

Note: Web search requires TAVILY_API_KEY in shared/config/.env.
      Without it, a mock result is returned so the rest of the demo still runs.
"""

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_openai_client, get_env
from rich.console import Console
from rich.rule import Rule

console = Console()
client, model = get_openai_client()


# ── Tool implementations ───────────────────────────────────────────────
def _web_search(query: str, max_results: int = 3) -> list[dict]:
    """Call Tavily search API. Falls back to a mock if key is not set."""
    api_key = get_env("TAVILY_API_KEY", required=False)
    if not api_key or "your-tavily" in api_key:
        return [{"title": "Mock result", "content": f"[MOCK] Top result for: {query}", "url": ""}]
    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=api_key)
        response = tavily.search(query=query, max_results=max_results)
        return response.get("results", [])
    except Exception as exc:
        return [{"title": "Error", "content": str(exc), "url": ""}]


def _calculator(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))  # nosec
    except Exception as exc:
        return f"Error: {exc}"


# ── Tool registry (clean dispatch without a long if/elif chain) ────────
TOOL_REGISTRY: dict[str, Any] = {
    "web_search": lambda a: json.dumps(_web_search(a["query"])),
    "calculator": lambda a: _calculator(a["expression"]),
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use for facts, news, and data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a Python arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                },
                "required": ["expression"],
            },
        },
    },
]


# ── Agent loop with tool dispatch ─────────────────────────────────────
def run_with_tools(goal: str, max_iterations: int = 8) -> str:
    """
    A simple tool-calling agent loop.
    Shows parallel tool calls — the LLM may call multiple tools
    in a single response when it can answer faster that way.
    """
    messages = [
        {"role": "system", "content": "Use tools to answer precisely. Show your work."},
        {"role": "user", "content": goal},
    ]

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS
        )
        msg = response.choices[0].message

        # No tool calls → final answer
        if not msg.tool_calls:
            return msg.content

        messages.append(msg)

        # Handle parallel tool calls (LLM may call multiple tools at once)
        console.print(f"\n[dim]Iteration {iteration + 1}:[/dim]")
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            console.print(f"  [yellow]→ {name}[/yellow]({args})")

            handler = TOOL_REGISTRY.get(name)
            result = handler(args) if handler else f"Unknown tool: {name}"
            console.print(f"  [green]← {str(result)[:150]}[/green]")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return "Max iterations reached."


if __name__ == "__main__":
    console.print(Rule("[bold]Tool Integration — Web Search + Calculator[/bold]"))

    result = run_with_tools(
        "Search for the Agentic AI market size in 2025, then calculate what the "
        "market size would be in 2030 assuming a 39% compound annual growth rate."
    )
    console.print(f"\n[bold]Final Answer:[/bold]\n{result}")
