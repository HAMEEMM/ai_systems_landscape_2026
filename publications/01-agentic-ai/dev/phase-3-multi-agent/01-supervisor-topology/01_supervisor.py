"""
phase-3-multi-agent/01-supervisor-topology/01_supervisor.py

Multi-Agent — Supervisor Topology with LangGraph.

Architecture:
    User → [Supervisor]
                ├── [Research Agent]   gathers facts
                ├── [Analyst Agent]    interprets data
                └── [Writer Agent]     drafts final output

The Supervisor reads the conversation history and decides which
specialist to route to next — or signals END when done.
Each specialist appends its output and returns control to the Supervisor.

This is the most common enterprise multi-agent pattern because it is
easy to audit: every routing decision is visible in the trace.

Paper reference: §5 Design Patterns — Multi-Agent Topologies (Supervisor)

Run:
    cd publications/01-agentic-ai/dev
    python phase-3-multi-agent/01-supervisor-topology/01_supervisor.py
"""

import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_env
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command

llm = ChatOpenAI(model="gpt-4o", api_key=get_env("OPENAI_API_KEY"), temperature=0)

SPECIALISTS = ["research_agent", "analyst_agent", "writer_agent"]
Route = Literal["research_agent", "analyst_agent", "writer_agent", "__end__"]


# ── Specialist Agents ──────────────────────────────────────────────────
def research_agent(state: MessagesState) -> Command:
    """Gathers factual information relevant to the task."""
    response = llm.invoke([
        SystemMessage(
            "You are a research agent. Gather relevant facts, data, and evidence. "
            "Be concise and factual. Prefix every response with [RESEARCH]."
        ),
        *state["messages"],
    ])
    return Command(goto="supervisor", update={"messages": [response]})


def analyst_agent(state: MessagesState) -> Command:
    """Interprets the research and draws conclusions."""
    response = llm.invoke([
        SystemMessage(
            "You are an analyst. Interpret the research, identify patterns, "
            "compare options, and draw conclusions. Prefix every response with [ANALYSIS]."
        ),
        *state["messages"],
    ])
    return Command(goto="supervisor", update={"messages": [response]})


def writer_agent(state: MessagesState) -> Command:
    """Synthesises research and analysis into a final polished answer."""
    response = llm.invoke([
        SystemMessage(
            "You are a technical writer. Synthesise the research and analysis into a "
            "clear, well-structured final answer. Prefix your response with [FINAL]."
        ),
        *state["messages"],
    ])
    return Command(goto="supervisor", update={"messages": [response]})


# ── Supervisor ─────────────────────────────────────────────────────────
def supervisor(state: MessagesState) -> Command[Route]:
    """
    Reads the full conversation and decides which specialist acts next.
    Outputs one of: research_agent | analyst_agent | writer_agent | FINISH
    """
    last_contents = [m.content for m in state["messages"] if hasattr(m, "content")]
    already_have = {
        "research": any("[RESEARCH]" in c for c in last_contents),
        "analysis": any("[ANALYSIS]" in c for c in last_contents),
        "final":    any("[FINAL]"    in c for c in last_contents),
    }

    response = llm.invoke([
        SystemMessage(
            "You are a supervisor managing: research_agent, analyst_agent, writer_agent.\n"
            "Review the conversation and decide who acts next.\n"
            "Workflow order: research_agent → analyst_agent → writer_agent → FINISH.\n"
            "Once writer_agent has produced a [FINAL] response, output exactly: FINISH.\n"
            "Output ONLY the agent name or FINISH — nothing else."
        ),
        *state["messages"],
    ])

    decision = response.content.strip().lower()

    if "finish" in decision or already_have["final"]:
        return Command(goto=END)

    for agent in SPECIALISTS:
        if agent in decision:
            return Command(goto=agent)

    # Default progression if parsing fails
    if not already_have["research"]:
        return Command(goto="research_agent")
    if not already_have["analysis"]:
        return Command(goto="analyst_agent")
    if not already_have["final"]:
        return Command(goto="writer_agent")

    return Command(goto=END)


# ── Build and run the graph ────────────────────────────────────────────
def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("supervisor",     supervisor)
    builder.add_node("research_agent", research_agent)
    builder.add_node("analyst_agent",  analyst_agent)
    builder.add_node("writer_agent",   writer_agent)
    builder.add_edge(START, "supervisor")
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    task = (
        "Compare the three leading Agentic AI runtime frameworks in 2026: "
        "LangGraph, OpenAI Agents SDK, and Google ADK. "
        "Which is best suited for enterprise production deployments?"
    )
    console.print(Panel(f"[bold cyan]Task:[/bold cyan] {task}", title="Supervisor Multi-Agent System"))

    result = graph.invoke({"messages": [HumanMessage(content=task)]})

    for msg in result["messages"]:
        content = msg.content
        if "[FINAL]" in content:
            console.print(Panel(content, title="[bold green]Final Output (Writer Agent)[/bold green]"))
        elif "[RESEARCH]" in content:
            console.print(Rule("[dim]Research Agent Output[/dim]"))
            console.print(f"[dim]{content[:400]}[/dim]")
        elif "[ANALYSIS]" in content:
            console.print(Rule("[dim]Analyst Agent Output[/dim]"))
            console.print(f"[dim]{content[:400]}[/dim]")
