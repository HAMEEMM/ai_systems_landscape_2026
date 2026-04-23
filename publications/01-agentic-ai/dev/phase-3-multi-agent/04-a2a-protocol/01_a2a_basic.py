"""
phase-3-multi-agent/04-a2a-protocol/01_a2a_basic.py

Layer 5 — Inter-Agent Protocols: A2A (Agent-to-Agent).

A2A is the protocol for how agents talk to OTHER AGENTS.
While MCP connects agents to tools, A2A connects agents to agents —
enabling you to build systems where a Claude agent can delegate a
sub-task to a LangGraph agent or a Google ADK agent transparently.

A2A concepts:
  Agent Card  — a JSON manifest that advertises an agent's capabilities
  Task        — a unit of work delegated from one agent to another
  Artifact    — the output an agent returns when a task is complete

This file:
  1. Defines two agents with A2A-style Agent Cards
  2. Simulates task delegation between them
  3. Shows how a coordinator routes tasks based on capability declarations

Paper reference: §7 Inter-Agent Protocols — A2A (agent→agent)
A2A spec: https://google.github.io/A2A/

Run:
    cd publications/01-agentic-ai/dev
    python phase-3-multi-agent/04-a2a-protocol/01_a2a_basic.py
"""

import sys
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_openai_client
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

console = Console()
client, model = get_openai_client()


# ── A2A Data Structures ────────────────────────────────────────────────
@dataclass
class AgentCapability:
    name: str
    description: str
    input_schema: dict


@dataclass
class AgentCard:
    """
    An Agent Card is the A2A equivalent of an API's OpenAPI spec.
    Agents publish their cards so other agents can discover their capabilities.
    """
    agent_id: str
    name: str
    description: str
    capabilities: list[AgentCapability]
    provider: str = "local"
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        return {
            "agent_id":    self.agent_id,
            "name":        self.name,
            "description": self.description,
            "version":     self.version,
            "provider":    self.provider,
            "capabilities": [
                {"name": c.name, "description": c.description}
                for c in self.capabilities
            ],
        }


@dataclass
class A2ATask:
    """A unit of work sent from one agent to another."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    from_agent: str = ""
    to_agent: str = ""
    capability: str = ""
    input_data: dict = field(default_factory=dict)
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class A2AArtifact:
    """The output returned by an agent when it completes a task."""
    task_id: str
    agent_id: str
    result: Any
    status: str = "completed"


# ── Agent implementations ──────────────────────────────────────────────
class MathAgent:
    """Specialist agent that handles quantitative analysis."""

    CARD = AgentCard(
        agent_id="math-agent-001",
        name="Math Agent",
        description="Handles arithmetic, statistics, and quantitative analysis.",
        capabilities=[
            AgentCapability(
                name="calculate",
                description="Evaluate a mathematical expression or formula.",
                input_schema={"expression": "string"},
            ),
            AgentCapability(
                name="statistical_summary",
                description="Compute mean, median, and std of a list of numbers.",
                input_schema={"numbers": "list[float]"},
            ),
        ],
    )

    def handle(self, task: A2ATask) -> A2AArtifact:
        if task.capability == "calculate":
            expr = task.input_data.get("expression", "")
            try:
                result = str(eval(expr, {"__builtins__": {}}, {}))  # nosec
            except Exception as exc:
                result = f"Error: {exc}"

        elif task.capability == "statistical_summary":
            nums = task.input_data.get("numbers", [])
            n = len(nums)
            if n == 0:
                result = "No numbers provided."
            else:
                mean = sum(nums) / n
                sorted_n = sorted(nums)
                median = sorted_n[n // 2] if n % 2 else (sorted_n[n // 2 - 1] + sorted_n[n // 2]) / 2
                variance = sum((x - mean) ** 2 for x in nums) / n
                std = variance ** 0.5
                result = f"n={n}, mean={mean:.2f}, median={median:.2f}, std={std:.2f}"
        else:
            result = f"Unknown capability: {task.capability}"

        return A2AArtifact(task_id=task.task_id, agent_id=self.CARD.agent_id, result=result)


class ResearchAgent:
    """Specialist agent that handles natural language research tasks."""

    CARD = AgentCard(
        agent_id="research-agent-001",
        name="Research Agent",
        description="Handles factual questions, summarisation, and analysis using an LLM.",
        capabilities=[
            AgentCapability(
                name="answer_question",
                description="Answer a factual question using background knowledge.",
                input_schema={"question": "string"},
            ),
            AgentCapability(
                name="summarise",
                description="Summarise a provided text passage.",
                input_schema={"text": "string", "max_words": "int"},
            ),
        ],
    )

    def handle(self, task: A2ATask) -> A2AArtifact:
        if task.capability == "answer_question":
            question = task.input_data.get("question", "")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Answer concisely and accurately."},
                    {"role": "user", "content": question},
                ],
                max_tokens=200,
            )
            result = response.choices[0].message.content

        elif task.capability == "summarise":
            text = task.input_data.get("text", "")
            max_words = task.input_data.get("max_words", 50)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"Summarise in at most {max_words} words."},
                    {"role": "user", "content": text},
                ],
                max_tokens=150,
            )
            result = response.choices[0].message.content
        else:
            result = f"Unknown capability: {task.capability}"

        return A2AArtifact(task_id=task.task_id, agent_id=self.CARD.agent_id, result=result)


# ── Coordinator: discovers agents and routes tasks ─────────────────────
class A2ACoordinator:
    """
    Maintains a registry of agent cards and routes tasks to the right agent.
    This simulates what an A2A-compatible orchestrator does.
    """

    def __init__(self):
        self._registry: dict[str, Any] = {}
        self._agents: dict[str, Any] = {}

    def register(self, agent):
        self._registry[agent.CARD.agent_id] = agent.CARD
        self._agents[agent.CARD.agent_id]   = agent
        console.print(f"[blue]Registered:[/blue] {agent.CARD.name} ({agent.CARD.agent_id})")

    def discover(self, needed_capability: str) -> AgentCard | None:
        """Find an agent that has the requested capability."""
        for card in self._registry.values():
            if any(c.name == needed_capability for c in card.capabilities):
                return card
        return None

    def delegate(self, task: A2ATask) -> A2AArtifact:
        """Route a task to the appropriate agent and return the artifact."""
        card = self.discover(task.capability)
        if not card:
            return A2AArtifact(
                task_id=task.task_id, agent_id="coordinator",
                result=f"No agent found for capability: {task.capability}", status="failed"
            )
        task.to_agent = card.agent_id
        agent = self._agents[card.agent_id]
        console.print(f"  [yellow]→ Delegating[/yellow] task {task.task_id} "
                      f"to [bold]{card.name}[/bold] (capability: {task.capability})")
        artifact = agent.handle(task)
        console.print(f"  [green]← Artifact received[/green]: {str(artifact.result)[:100]}")
        return artifact


# ── Demo ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    coordinator = A2ACoordinator()
    coordinator.register(MathAgent())
    coordinator.register(ResearchAgent())

    console.print(Rule("[bold]A2A Agent Registry[/bold]"))
    table = Table("Agent ID", "Name", "Capabilities")
    for card in [MathAgent.CARD, ResearchAgent.CARD]:
        table.add_row(
            card.agent_id,
            card.name,
            ", ".join(c.name for c in card.capabilities),
        )
    console.print(table)

    console.print(Rule("[bold]A2A Task Delegation Demo[/bold]"))
    tasks = [
        A2ATask(
            from_agent="orchestrator",
            capability="calculate",
            input_data={"expression": "7300 * (1.39 ** 9)"},
        ),
        A2ATask(
            from_agent="orchestrator",
            capability="answer_question",
            input_data={"question": "What is the MCP protocol used for in Agentic AI?"},
        ),
        A2ATask(
            from_agent="orchestrator",
            capability="statistical_summary",
            input_data={"numbers": [72.1, 68.4, 85.3, 91.2, 79.8, 88.5]},
        ),
    ]

    for task in tasks:
        console.print(f"\n[bold]Task:[/bold] capability={task.capability}, input={task.input_data}")
        artifact = coordinator.delegate(task)
        console.print(Panel(str(artifact.result), title=f"Result (task {artifact.task_id})"))
