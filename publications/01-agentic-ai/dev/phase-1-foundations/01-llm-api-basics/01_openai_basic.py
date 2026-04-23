"""
phase-1-foundations/01-llm-api-basics/01_openai_basic.py

Layer 1 — Foundation Models: OpenAI API basics.

Covers four patterns every agent builder must know:
  1. Basic chat completion
  2. Multi-turn conversation (simulated short-term memory)
  3. Structured output (JSON mode)
  4. Streaming

Paper reference: §4 Layer 1 — Foundation Models

Run:
    cd publications/01-agentic-ai/dev
    python phase-1-foundations/01-llm-api-basics/01_openai_basic.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_openai_client
from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel

console = Console()
client, model = get_openai_client()


# ── 1. Basic Chat Completion ───────────────────────────────────────────
def demo_basic():
    console.print(Rule("[bold]1. Basic Chat Completion[/bold]"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a concise AI assistant."},
            {"role": "user",   "content": "In one sentence, what is Agentic AI?"},
        ],
    )
    answer = response.choices[0].message.content
    tokens = response.usage.total_tokens
    console.print(f"Answer: [green]{answer}[/green]")
    console.print(f"Tokens used: [yellow]{tokens}[/yellow]\n")


# ── 2. Multi-turn conversation ─────────────────────────────────────────
def demo_multi_turn():
    console.print(Rule("[bold]2. Multi-Turn Conversation[/bold]"))
    messages = [{"role": "system", "content": "You are a concise AI tutor."}]
    turns = [
        "What is the Perceive step in the PPAS agent loop?",
        "What comes after Perceive?",
        "And after that?",
    ]
    for user_msg in turns:
        messages.append({"role": "user", "content": user_msg})
        response = client.chat.completions.create(model=model, messages=messages)
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        console.print(f"[bold]You:[/bold] {user_msg}")
        console.print(f"[green]GPT:[/green] {reply}\n")


# ── 3. Structured Output (JSON mode) ──────────────────────────────────
def demo_structured_output():
    console.print(Rule("[bold]3. Structured Output (JSON mode)[/bold]"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    'Respond ONLY with valid JSON. '
                    'Schema: {"layer_number": int, "layer_name": str, "example_tools": list[str]}'
                ),
            },
            {"role": "user", "content": "Describe Layer 4 of the Agentic AI 8-layer stack."},
        ],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    console.print(data)
    console.print()


# ── 4. Streaming ───────────────────────────────────────────────────────
def demo_streaming():
    console.print(Rule("[bold]4. Streaming Response[/bold]"))
    console.print("[dim]Streaming token by token:[/dim] ", end="")
    with client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "List the 8 layers of the Agentic AI stack in order, one per line."},
        ],
        stream=True,
    ) as stream:
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            console.print(delta, end="")
    console.print("\n")


if __name__ == "__main__":
    demo_basic()
    demo_multi_turn()
    demo_structured_output()
    demo_streaming()
