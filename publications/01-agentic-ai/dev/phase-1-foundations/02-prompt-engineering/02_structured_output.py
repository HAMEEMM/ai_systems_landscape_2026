"""
phase-1-foundations/02-prompt-engineering/02_structured_output.py

Prompt Engineering: Structured Output with Pydantic.

Why this matters for agents: the PLAN step needs to emit a structured
decision (which tool to call, with what arguments), not free text.
Structured output makes agent decisions reliable and machine-parseable.

This uses OpenAI's `response_format` with a Pydantic model — the
same technique LangGraph uses internally when routing agent decisions.

Paper reference: §4 Layer 1 — Foundation Models (tool-calling APIs)

Run:
    cd publications/01-agentic-ai/dev
    python phase-1-foundations/02-prompt-engineering/02_structured_output.py
"""

import sys
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_openai_client
from rich.console import Console
from rich.rule import Rule
from rich.table import Table

console = Console()
client, model = get_openai_client()


# ── Define schemas the agent should output ─────────────────────────────
class AgentAction(BaseModel):
    """The structured decision produced by the PLAN step."""
    reasoning: str = Field(description="Chain-of-thought before deciding")
    action: Literal["search", "calculate", "summarise", "finish"]
    action_input: str = Field(description="Argument for the chosen action")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0–1")


class AgentState(BaseModel):
    """A snapshot of agent state after one PPAS iteration."""
    iteration: int
    goal_achieved: bool
    next_action: AgentAction
    estimated_iterations_remaining: int


# ── Demo 1: parse a planning decision ─────────────────────────────────
def demo_planning_decision():
    console.print(Rule("[bold]1. Structured Agent Planning Decision[/bold]"))

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an agent planner. Given a goal and current state, "
                    "output a structured AgentState JSON following the schema exactly."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Goal: Find the current population of Tokyo and calculate how many "
                    "times larger it is than New York City.\n"
                    "Current state: Iteration 1, no tools called yet."
                ),
            },
        ],
        response_format=AgentState,
    )

    state: AgentState = response.choices[0].message.parsed

    table = Table("Field", "Value")
    table.add_row("Iteration",                str(state.iteration))
    table.add_row("Goal achieved",            str(state.goal_achieved))
    table.add_row("Next action",              state.next_action.action)
    table.add_row("Action input",             state.next_action.action_input)
    table.add_row("Confidence",               f"{state.next_action.confidence:.0%}")
    table.add_row("Iterations remaining",     str(state.estimated_iterations_remaining))
    table.add_row("Reasoning",                state.next_action.reasoning[:120] + "...")
    console.print(table)


# ── Demo 2: classify a user intent (routing) ──────────────────────────
class UserIntent(BaseModel):
    intent: Literal["research_query", "calculation", "code_task", "general_question"]
    urgency: Literal["low", "medium", "high"]
    requires_external_tool: bool
    summary: str


def demo_intent_classification():
    console.print(Rule("[bold]2. Intent Classification for Agent Routing[/bold]"))

    queries = [
        "What is 15% of $47,500?",
        "Find the latest papers on multi-agent LLM coordination published in 2026.",
        "Write a Python function to parse a JSON response from the OpenAI API.",
    ]

    for query in queries:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Classify the user's request for agent routing. Follow the schema exactly.",
                },
                {"role": "user", "content": query},
            ],
            response_format=UserIntent,
        )
        intent: UserIntent = response.choices[0].message.parsed
        console.print(f"[bold]Query:[/bold] {query}")
        console.print(
            f"  intent=[cyan]{intent.intent}[/cyan]  "
            f"urgency=[yellow]{intent.urgency}[/yellow]  "
            f"needs_tool=[green]{intent.requires_external_tool}[/green]"
        )
        console.print(f"  summary: {intent.summary}\n")


if __name__ == "__main__":
    demo_planning_decision()
    demo_intent_classification()
