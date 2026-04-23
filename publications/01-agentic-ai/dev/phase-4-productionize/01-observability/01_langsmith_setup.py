"""
phase-4-productionize/01-observability/01_langsmith_setup.py

Layer 8 — Observability & Safety: LangSmith tracing.

LangSmith gives you a web UI showing every LLM call, tool call,
and agent step — with token counts, latency, and cost per run.
This is essential for debugging and evaluating agent systems.

Setup (one time):
  1. Create account at https://smith.langchain.com (free tier available)
  2. Get your API key from Settings → API Keys
  3. Add LANGSMITH_API_KEY and LANGSMITH_PROJECT to shared/config/.env
  4. Run this file — then open https://smith.langchain.com to see the trace

Paper reference: §4 Layer 8 — Observability & Safety

Run:
    cd publications/01-agentic-ai/dev
    python phase-4-productionize/01-observability/01_langsmith_setup.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_env
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()


# ── Configure LangSmith tracing ────────────────────────────────────────
def configure_langsmith() -> bool:
    """
    Enable LangSmith tracing by setting the required env variables.
    Returns True if tracing is active, False if key is not configured.
    """
    api_key = os.getenv("LANGSMITH_API_KEY", "")
    project = os.getenv("LANGSMITH_PROJECT", "agentic-ai-ppas")

    if not api_key or "your-langsmith" in api_key:
        console.print(Panel(
            "[yellow]LangSmith not configured.[/yellow]\n\n"
            "To enable tracing:\n"
            "  1. Sign up free at https://smith.langchain.com\n"
            "  2. Go to Settings → API Keys → Create Key\n"
            "  3. Add to shared/config/.env:\n"
            "       LANGSMITH_API_KEY=ls__...\n"
            "       LANGSMITH_PROJECT=agentic-ai-ppas\n\n"
            "Running without tracing for now.",
            title="LangSmith Setup",
        ))
        return False

    # These env vars activate automatic tracing for all LangChain/LangGraph calls
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"]    = api_key
    os.environ["LANGCHAIN_PROJECT"]    = project

    console.print(Panel(
        f"[green]LangSmith tracing enabled[/green]\n"
        f"Project: [cyan]{project}[/cyan]\n"
        f"View traces at: [link=https://smith.langchain.com]https://smith.langchain.com[/link]",
        title="Observability Active",
    ))
    return True


# ── Run a traced agent ─────────────────────────────────────────────────
def run_traced_agent():
    """
    Any LangGraph/LangChain call made while LANGCHAIN_TRACING_V2=true
    is automatically captured in LangSmith — no code changes needed.
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage
    from langgraph.prebuilt import create_react_agent

    @tool
    def calculator(expression: str) -> str:
        """Evaluate a Python arithmetic expression."""
        try:
            return str(eval(expression, {"__builtins__": {}}, {}))  # nosec
        except Exception as exc:
            return f"Error: {exc}"

    llm = ChatOpenAI(model="gpt-4o", api_key=get_env("OPENAI_API_KEY"), temperature=0)
    agent = create_react_agent(llm, [calculator])

    goal = (
        "The Agentic AI market is $7.3B in 2025 with a 39% CAGR. "
        "Calculate the projected market size in 2030 and 2034."
    )
    console.print(Panel(f"[bold cyan]{goal}[/bold cyan]", title="Traced Agent Run"))

    result = agent.invoke({"messages": [HumanMessage(content=goal)]})
    final = result["messages"][-1].content
    console.print(Panel(f"[green]{final}[/green]", title="Result"))


# ── What you'll see in LangSmith ───────────────────────────────────────
def show_tracing_overview():
    console.print(Rule("[bold]What LangSmith Shows You[/bold]"))
    items = [
        ("Run Tree",          "Hierarchical view of every LLM call and tool call"),
        ("Inputs / Outputs",  "Full messages sent to and from the LLM"),
        ("Latency",           "Time per step — identify slow nodes"),
        ("Token usage",       "Input + output tokens per call → cost estimation"),
        ("Feedback",          "Thumbs up/down or custom scores on runs"),
        ("Datasets",          "Capture runs as test cases for regression eval"),
        ("Playground",        "Re-run any trace with modified inputs"),
    ]
    for name, desc in items:
        console.print(f"  [yellow]{name:<20}[/yellow] {desc}")


if __name__ == "__main__":
    show_tracing_overview()
    console.print()
    tracing_active = configure_langsmith()
    run_traced_agent()

    if tracing_active:
        console.print(
            "\n[bold]Check your LangSmith project for the trace.[/bold] "
            "You'll see the ReAct loop steps, tool calls, and token counts."
        )
