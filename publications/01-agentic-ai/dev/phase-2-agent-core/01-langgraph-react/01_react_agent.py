"""
phase-2-agent-core/01-langgraph-react/01_react_agent.py

Layer 2 — Runtime & Orchestration: LangGraph ReAct agent.

This is the same PPAS loop from phase-1/03 but now built with
LangGraph — the leading production framework for agentic systems.
Compare the two files side-by-side to see what the framework adds:

  Raw API (phase-1/03)       LangGraph (this file)
  ─────────────────────      ──────────────────────────────────────
  Manual message list        TypedDict state graph
  Manual loop with while     Conditional edges (should_loop / END)
  Manual tool dispatch       Built-in tool node
  No checkpointing           Checkpointer → pause/resume/HITL
  No streaming hooks         Native .stream() support
  No tracing                 LangSmith integration out-of-the-box

Paper reference:
  §4 Layer 2 — Runtime & Orchestration (LangGraph)
  §5 Design Patterns — ReAct

Run:
    cd publications/01-agentic-ai/dev
    python phase-2-agent-core/01-langgraph-react/01_react_agent.py
"""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_env
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent


# ── Tool definitions (Layer 4) ─────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """Evaluate a Python arithmetic expression. Use for any math calculation."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # nosec
        return str(result)
    except Exception as exc:
        return f"Error: {exc}"


@tool
def get_today() -> str:
    """Returns today's date in ISO 8601 format (YYYY-MM-DD)."""
    return date.today().isoformat()


@tool
def word_count(text: str) -> str:
    """Count the number of words in a text string."""
    return str(len(text.split()))


# ── Build the agent ────────────────────────────────────────────────────
def build_agent():
    """
    create_react_agent builds a LangGraph StateGraph that implements
    the ReAct loop:

        [llm] → decides on a tool → [tools node] → executes it
          ↑                                               |
          └───────── loops until llm says 'done' ─────────┘

    The graph's state is a MessagesState (list of messages),
    equivalent to self.messages in the raw version.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=get_env("OPENAI_API_KEY"),
        temperature=0,
    )
    return create_react_agent(llm, tools=[calculator, get_today, word_count])


def run_goal(agent, goal: str):
    console.print(Panel(f"[bold cyan]GOAL:[/bold cyan] {goal}", title="LangGraph ReAct Agent"))

    # Stream the agent's steps so you can watch the loop in real time
    for step in agent.stream(
        {"messages": [HumanMessage(content=goal)]},
        stream_mode="updates",
    ):
        node_name = list(step.keys())[0]
        msgs = step[node_name].get("messages", [])
        for msg in msgs:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    console.print(
                        f"[yellow]  PLAN/ACT:[/yellow] {tc['name']}({tc['args']})"
                    )
            elif hasattr(msg, "content") and msg.content and node_name == "tools":
                console.print(f"[green]  RESULT:[/green]   {msg.content[:120]}")

    # Final answer is the last message
    result = agent.invoke({"messages": [HumanMessage(content=goal)]})
    final = result["messages"][-1].content
    console.print(Panel(f"[bold green]{final}[/bold green]", title="Final Answer"))
    return final


if __name__ == "__main__":
    agent = build_agent()

    goals = [
        "What is 7% compound interest on $25,000 over 10 years? Use the calculator.",
        "How many days have passed since January 1, 2026? Get today's date first, then calculate.",
        "How many words are in the phrase: 'Perceive Plan Act Self-Correct'?",
    ]

    for goal in goals:
        run_goal(agent, goal)
        console.print(Rule())
