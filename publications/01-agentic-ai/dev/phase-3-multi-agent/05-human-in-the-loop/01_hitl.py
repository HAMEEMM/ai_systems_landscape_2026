"""
phase-3-multi-agent/05-human-in-the-loop/01_hitl.py

Human-in-the-Loop (HITL) with LangGraph interrupt().

The paper identifies HITL as a critical design pattern (§5) and a
regulatory requirement for high-risk AI deployments (§11, EU AI Act).

LangGraph implements HITL through interrupt() — a node can pause
execution, surface a decision to a human, and resume with the human's
input. The agent's state is checkpointed so nothing is lost during the wait.

HITL patterns covered:
  1. Approval gate   — agent proposes an action; human approves/rejects
  2. Input injection — agent requests information it cannot obtain itself
  3. Error correction — human corrects a wrong intermediate result

Paper reference: §5 Design Patterns — HITL

Run:
    cd publications/01-agentic-ai/dev
    python phase-3-multi-agent/05-human-in-the-loop/01_hitl.py
"""

import sys
from pathlib import Path
from typing import TypedDict, Annotated
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_env
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.prompt import Confirm, Prompt

console = Console()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

llm = ChatOpenAI(model="gpt-4o", api_key=get_env("OPENAI_API_KEY"), temperature=0)


# ── State ──────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    goal: str
    plan: str
    human_approved: bool
    result: str
    human_correction: str


# ── Nodes ──────────────────────────────────────────────────────────────
def plan_node(state: AgentState) -> AgentState:
    """Agent generates a plan before taking any action."""
    response = llm.invoke([
        SystemMessage("You are a careful planning agent. Generate a concise step-by-step plan."),
        HumanMessage(content=f"Goal: {state['goal']}\n\nGenerate a plan to achieve this goal."),
    ])
    plan = response.content
    console.print(Panel(f"[cyan]{plan}[/cyan]", title="Agent's Proposed Plan"))
    return {**state, "plan": plan}


def approval_gate(state: AgentState) -> Command:
    """
    HITL Pattern 1 — Approval Gate.
    The agent PAUSES here and waits for human approval.
    """
    console.print(Rule("[bold yellow]⏸  HUMAN APPROVAL REQUIRED[/bold yellow]"))

    # interrupt() checkpoints the state and returns control to the caller.
    # The caller must provide a human response to resume execution.
    human_input = interrupt({
        "message": "Please review the agent's plan above. Approve to proceed.",
        "plan": state["plan"],
    })

    approved = str(human_input).lower() in ("yes", "y", "approve", "ok", "true")
    return Command(
        goto="execute_node" if approved else END,
        update={**state, "human_approved": approved},
    )


def execute_node(state: AgentState) -> AgentState:
    """Execute the approved plan and produce a result."""
    response = llm.invoke([
        SystemMessage("You are an execution agent. Follow the plan precisely."),
        HumanMessage(
            content=f"Goal: {state['goal']}\n\nApproved plan:\n{state['plan']}\n\nExecute this plan now."
        ),
    ])
    result = response.content
    console.print(Panel(f"[green]{result[:400]}[/green]", title="Execution Result"))
    return {**state, "result": result}


def correction_gate(state: AgentState) -> Command:
    """
    HITL Pattern 2 — Human Correction.
    If the result needs fixing, the human can provide a correction.
    """
    console.print(Rule("[bold yellow]⏸  REVIEW RESULT[/bold yellow]"))

    human_input = interrupt({
        "message": "Review the result. Type a correction if needed, or 'ok' to accept.",
        "result": state["result"],
    })

    if str(human_input).lower() in ("ok", "yes", "good", "accept", ""):
        return Command(goto=END, update=state)

    # Apply the human's correction
    corrected = f"{state['result']}\n\n[Human correction]: {human_input}"
    return Command(goto=END, update={**state, "result": corrected, "human_correction": str(human_input)})


# ── Build graph ────────────────────────────────────────────────────────
def build_hitl_graph():
    builder = StateGraph(AgentState)
    builder.add_node("plan_node",       plan_node)
    builder.add_node("approval_gate",   approval_gate)
    builder.add_node("execute_node",    execute_node)
    builder.add_node("correction_gate", correction_gate)

    builder.add_edge(START,            "plan_node")
    builder.add_edge("plan_node",      "approval_gate")
    builder.add_edge("execute_node",   "correction_gate")

    # MemorySaver checkpoints the state between interrupts
    return builder.compile(checkpointer=MemorySaver())


# ── Interactive runner ─────────────────────────────────────────────────
def run_hitl(goal: str):
    graph = build_hitl_graph()
    config = {"configurable": {"thread_id": "hitl-demo-01"}}

    console.print(Panel(f"[bold cyan]{goal}[/bold cyan]", title="HITL Agent"))

    # --- Run until first interrupt (approval gate) ---
    state = {"goal": goal, "plan": "", "human_approved": False, "result": "", "human_correction": ""}
    for event in graph.stream(state, config=config):
        pass  # stream drives execution up to the interrupt

    # --- Collect human approval ---
    approved = Confirm.ask("Approve this plan?", default=True)

    # --- Resume with the human's decision ---
    for event in graph.stream(Command(resume="yes" if approved else "no"), config=config):
        pass

    if not approved:
        console.print("[red]Plan rejected. Agent stopped.[/red]")
        return

    # --- Collect human review of the result ---
    correction = Prompt.ask(
        "Enter a correction (or press Enter to accept the result)",
        default="ok",
    )

    # --- Resume with the correction ---
    for event in graph.stream(Command(resume=correction), config=config):
        pass

    final_state = graph.get_state(config).values
    console.print(Panel(
        f"[bold green]{final_state.get('result', 'No result')}[/bold green]",
        title="Final Result (Human-Approved)",
    ))


if __name__ == "__main__":
    run_hitl(
        "Research the top 3 Agentic AI benchmarks mentioned in the PPAS paper "
        "(SWE-Bench, GAIA, WebArena) and summarise what each measures."
    )
