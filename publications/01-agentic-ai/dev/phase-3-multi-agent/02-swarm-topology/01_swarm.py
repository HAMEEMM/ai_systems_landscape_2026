"""
phase-3-multi-agent/02-swarm-topology/01_swarm.py

Multi-Agent — Swarm Topology.

In a swarm, agents hand off directly to each other — no central
supervisor. Each agent decides independently whether to handle the
request itself or pass it to a better-suited peer.

Architecture:
    User → [Triage Agent]
               ├──→ [Math Agent]     (if calculation needed)
               ├──→ [Research Agent] (if fact-finding needed)
               └──→ [Code Agent]     (if code generation needed)
                         ↕  (agents can hand off to each other)

Contrast with Supervisor: here routing intelligence is distributed
across the agents, not centralised. This makes swarms more resilient
but harder to audit.

Paper reference: §5 Design Patterns — Multi-Agent Topologies (Swarm)

Run:
    cd publications/01-agentic-ai/dev
    python phase-3-multi-agent/02-swarm-topology/01_swarm.py
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
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command

llm = ChatOpenAI(model="gpt-4o", api_key=get_env("OPENAI_API_KEY"), temperature=0)

AgentName = Literal["math_agent", "research_agent", "code_agent", "__end__"]


def make_handoff_tool(target: str):
    """
    Create a tool that lets an agent hand off to a specific peer.
    This is the swarm coordination mechanism — no supervisor needed.
    """
    @tool(name=f"handoff_to_{target}")
    def handoff() -> str:
        f"""Transfer this conversation to the {target}. Use when the task requires that agent's specialty."""
        return f"Transferring to {target}."
    return handoff


# ── Specialist Agents ──────────────────────────────────────────────────
def math_agent(state: MessagesState) -> Command[AgentName]:
    """Handles calculations and quantitative analysis."""
    @tool
    def calculator(expression: str) -> str:
        """Evaluate a Python arithmetic expression."""
        try:
            return str(eval(expression, {"__builtins__": {}}, {}))  # nosec
        except Exception as exc:
            return f"Error: {exc}"

    tools = [calculator, make_handoff_tool("research_agent"), make_handoff_tool("code_agent")]
    agent_llm = llm.bind_tools(tools)

    response = agent_llm.invoke([
        SystemMessage(
            "You are a math agent specialising in calculations. "
            "Use the calculator tool for all arithmetic. "
            "If the task needs research or code generation instead, use a handoff tool."
        ),
        *state["messages"],
    ])

    if response.tool_calls:
        tc = response.tool_calls[0]
        if tc["name"].startswith("handoff_to_"):
            target = tc["name"].replace("handoff_to_", "")
            return Command(goto=target, update={"messages": [response]})

    return Command(goto=END, update={"messages": [response]})


def research_agent(state: MessagesState) -> Command[AgentName]:
    """Handles factual questions and analysis tasks."""
    tools = [make_handoff_tool("math_agent"), make_handoff_tool("code_agent")]
    agent_llm = llm.bind_tools(tools)

    response = agent_llm.invoke([
        SystemMessage(
            "You are a research agent. Answer factual questions with precision. "
            "If the task requires math calculations, hand off to math_agent. "
            "If it requires code, hand off to code_agent."
        ),
        *state["messages"],
    ])

    if response.tool_calls:
        tc = response.tool_calls[0]
        if tc["name"].startswith("handoff_to_"):
            target = tc["name"].replace("handoff_to_", "")
            return Command(goto=target, update={"messages": [response]})

    return Command(goto=END, update={"messages": [response]})


def code_agent(state: MessagesState) -> Command[AgentName]:
    """Handles code generation and technical implementation."""
    tools = [make_handoff_tool("math_agent"), make_handoff_tool("research_agent")]
    agent_llm = llm.bind_tools(tools)

    response = agent_llm.invoke([
        SystemMessage(
            "You are a code agent. Write clean, well-commented Python code. "
            "If the task is primarily mathematical, hand off to math_agent."
        ),
        *state["messages"],
    ])

    if response.tool_calls:
        tc = response.tool_calls[0]
        if tc["name"].startswith("handoff_to_"):
            target = tc["name"].replace("handoff_to_", "")
            return Command(goto=target, update={"messages": [response]})

    return Command(goto=END, update={"messages": [response]})


def triage_agent(state: MessagesState) -> Command[AgentName]:
    """Entry point: routes the user request to the right specialist."""
    response = llm.invoke([
        SystemMessage(
            "You are a triage agent. Read the user request and decide which specialist to route to.\n"
            "  - math_agent:     calculations, numbers, formulas\n"
            "  - research_agent: facts, explanations, analysis\n"
            "  - code_agent:     writing Python or other code\n\n"
            "Output ONLY one of: math_agent | research_agent | code_agent"
        ),
        *state["messages"],
    ])
    decision = response.content.strip().lower()

    for agent in ["math_agent", "research_agent", "code_agent"]:
        if agent in decision:
            console.print(f"[dim]Triage → [yellow]{agent}[/yellow][/dim]")
            return Command(goto=agent)

    return Command(goto="research_agent")  # safe default


# ── Build the swarm graph ──────────────────────────────────────────────
def build_swarm():
    builder = StateGraph(MessagesState)
    builder.add_node("triage_agent",   triage_agent)
    builder.add_node("math_agent",     math_agent)
    builder.add_node("research_agent", research_agent)
    builder.add_node("code_agent",     code_agent)
    builder.add_edge(START, "triage_agent")
    return builder.compile()


if __name__ == "__main__":
    swarm = build_swarm()

    tasks = [
        "What is $50,000 invested at 8% annually for 20 years using compound interest?",
        "Explain the difference between MCP and A2A protocols in Agentic AI.",
        "Write a Python function that implements the PPAS agent loop with a max_iterations parameter.",
    ]

    for task in tasks:
        console.print(Panel(f"[bold cyan]{task}[/bold cyan]", title="Swarm Agent"))
        result = swarm.invoke({"messages": [HumanMessage(content=task)]})
        final = result["messages"][-1].content
        console.print(Panel(f"[green]{final}[/green]", title="Answer"))
        console.print(Rule())
