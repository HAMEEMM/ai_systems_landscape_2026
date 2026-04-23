"""
phase-2-agent-core/03-memory-systems/01_working_memory.py

Layer 3 — Memory Systems: Working and short-term memory.

The paper identifies six memory types (§6):
  1. Working memory    — the current context window (in-tokens)
  2. Short-term memory — in-process key-value store (survives turns, not restarts)
  3. Long-term memory  — persistent storage (Mem0, Redis, vector DB)
  4. Episodic memory   — specific past interactions
  5. Semantic memory   — world-knowledge facts
  6. Procedural memory — how-to-do-things (skills)

This file demonstrates types 1 and 2 without any external service,
so you can run it immediately with just an API key.

Paper reference: §6 — Memory Architectures

Run:
    cd publications/01-agentic-ai/dev
    python phase-2-agent-core/03-memory-systems/01_working_memory.py
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_openai_client
from rich.console import Console
from rich.rule import Rule
from rich.table import Table

console = Console()
client, model = get_openai_client()


# ── 1. Working Memory — the LLM context window ────────────────────────
@dataclass
class WorkingMemory:
    """
    Working memory = the messages list sent to the LLM on every API call.
    It is bounded by the context window (128K tokens for GPT-4o).

    This class adds a trim policy: drop the oldest user/assistant pairs
    when the history grows beyond max_messages, simulating a sliding window.
    """
    system_prompt: str
    messages: list[dict] = field(default_factory=list)
    max_messages: int = 20

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Keep the most recent messages when over the limit
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def to_api_format(self) -> list[dict]:
        """Return messages in the format the OpenAI API expects."""
        return [{"role": "system", "content": self.system_prompt}] + self.messages

    @property
    def token_estimate(self) -> int:
        """Rough estimate: 1 token ≈ 4 characters."""
        total_chars = sum(len(m["content"]) for m in self.to_api_format())
        return total_chars // 4


# ── 2. Short-Term Memory — in-process key-value store ─────────────────
class ShortTermMemory:
    """
    Short-term memory = a dict that persists within a session (one process run).
    The agent explicitly writes facts here by calling remember(); they are available
    for the rest of the session but vanish when the process exits.

    For persistence across restarts, graduate to long-term memory (Mem0/Redis).
    """

    def __init__(self):
        self._store: dict[str, Any] = {}

    def remember(self, key: str, value: Any):
        self._store[key] = value
        console.print(f"  [blue]STM ← stored:[/blue] {key!r} = {value!r}")

    def recall(self, key: str, default: Any = None) -> Any:
        value = self._store.get(key, default)
        console.print(f"  [cyan]STM → recall:[/cyan] {key!r} = {value!r}")
        return value

    def all_facts(self) -> dict:
        return dict(self._store)


# ── Demo: multi-turn agent with both memory layers ────────────────────
def memory_demo():
    console.print(Rule("[bold]Memory Systems Demo[/bold]"))

    working = WorkingMemory(
        system_prompt=(
            "You are a helpful research agent with memory.\n"
            "When you learn a new fact worth remembering, output it as:\n"
            "  REMEMBER: {\"key\": \"value\"}\n"
            "Otherwise respond normally."
        )
    )
    stm = ShortTermMemory()

    conversation_turns = [
        "My paper is titled 'Perceive, Plan, Act, Self-Correct'. It covers Agentic AI.",
        "What was the title of my paper again?",
        "The paper was submitted to Artificial Intelligence journal (Elsevier) in April 2026.",
        "Which journal and when?",
        "The preprint DOI is 10.31224/6738.",
        "Summarise everything you know about my paper in 3 bullet points.",
    ]

    for user_msg in conversation_turns:
        working.add("user", user_msg)
        console.print(f"\n[bold]You:[/bold] {user_msg}")
        console.print(f"[dim](Working memory: ~{working.token_estimate} tokens)[/dim]")

        response = client.chat.completions.create(
            model=model,
            messages=working.to_api_format(),
        )
        reply = response.choices[0].message.content
        working.add("assistant", reply)

        # Parse any REMEMBER commands out of the reply
        for line in reply.splitlines():
            if line.strip().startswith("REMEMBER:"):
                raw = line.split("REMEMBER:", 1)[1].strip()
                try:
                    facts = json.loads(raw)
                    for k, v in facts.items():
                        stm.remember(k, v)
                except json.JSONDecodeError:
                    pass

        console.print(f"[green]Agent:[/green] {reply}")

    # Show short-term memory contents
    console.print(Rule("[bold]Short-Term Memory at End of Session[/bold]"))
    table = Table("Key", "Value", title="Facts the agent chose to remember")
    for k, v in stm.all_facts().items():
        table.add_row(k, str(v))
    console.print(table)


if __name__ == "__main__":
    memory_demo()
