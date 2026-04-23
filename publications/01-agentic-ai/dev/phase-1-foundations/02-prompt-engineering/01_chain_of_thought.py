"""
phase-1-foundations/02-prompt-engineering/01_chain_of_thought.py

Prompt Engineering: Chain-of-Thought (CoT) vs. direct prompting.

CoT is the prompt-level mechanism behind the PLAN step. When you ask
the LLM to "think step by step" before deciding on an action, you are
implementing CoT — the same technique that enables the agent to
decompose complex goals into sub-tasks before acting.

Demonstrates:
  1. Direct answer — LLM responds immediately, no reasoning shown
  2. Explicit CoT  — "Think step by step" appended to the prompt
  3. Zero-shot CoT — seed the assistant turn with "Let's think step by step"

Paper reference: §5 Design Patterns — Tree-of-Thought, Plan-and-Execute

Run:
    cd publications/01-agentic-ai/dev
    python phase-1-foundations/02-prompt-engineering/01_chain_of_thought.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_openai_client
from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel

console = Console()
client, model = get_openai_client()

PROBLEM = (
    "An agent is running a research task. It has already used 3 of its 10 allowed tool calls. "
    "Each search costs 2 calls and each summarisation costs 1 call. "
    "The agent needs to do 2 more searches and 3 summarisations to finish. "
    "Will it have enough tool calls left? If not, by how many is it short?"
)


def direct_answer():
    """Standard prompt — LLM answers immediately without showing reasoning."""
    console.print(Rule("[bold]1. Direct Answer (no CoT)[/bold]"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROBLEM}],
    )
    console.print(Panel(response.choices[0].message.content, title="Direct"))


def explicit_cot():
    """Append 'Think step by step' — forces reasoning before conclusion."""
    console.print(Rule("[bold]2. Explicit Chain-of-Thought[/bold]"))
    prompt = PROBLEM + "\n\nThink step by step before giving your final answer."
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    console.print(Panel(response.choices[0].message.content, title="Explicit CoT"))


def zero_shot_cot():
    """
    Zero-shot CoT: seed the assistant turn with 'Let's think step by step.'
    The model continues from that seed, reasoning before concluding.
    """
    console.print(Rule("[bold]3. Zero-Shot CoT (seeded assistant turn)[/bold]"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user",      "content": PROBLEM},
            {"role": "assistant", "content": "Let's think step by step."},
        ],
    )
    console.print(Panel(response.choices[0].message.content, title="Zero-Shot CoT"))


if __name__ == "__main__":
    direct_answer()
    explicit_cot()
    zero_shot_cot()
