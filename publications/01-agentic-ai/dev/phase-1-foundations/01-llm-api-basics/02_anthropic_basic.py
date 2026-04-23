"""
phase-1-foundations/01-llm-api-basics/02_anthropic_basic.py

Layer 1 — Foundation Models: Anthropic Claude API basics.

Covers the same patterns as 01_openai_basic.py but using Claude,
so you can compare API styles side-by-side. OpenAI and Anthropic
use slightly different message schemas — knowing both matters when
building agents that can swap models.

Paper reference: §4 Layer 1 — Foundation Models

Run:
    cd publications/01-agentic-ai/dev
    python phase-1-foundations/01-llm-api-basics/02_anthropic_basic.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_anthropic_client
from rich.console import Console
from rich.rule import Rule

console = Console()
client, model = get_anthropic_client()


# ── 1. Basic Message ───────────────────────────────────────────────────
def demo_basic():
    console.print(Rule("[bold]1. Basic Message (Claude)[/bold]"))
    # Note: Anthropic puts the system prompt as a top-level parameter,
    # NOT inside the messages list — key difference from OpenAI.
    message = client.messages.create(
        model=model,
        max_tokens=256,
        system="You are a concise AI assistant.",
        messages=[
            {"role": "user", "content": "In one sentence, what is the Self-Correct step of the PPAS loop?"},
        ],
    )
    console.print(f"[green]{message.content[0].text}[/green]")
    console.print(
        f"Input tokens: [yellow]{message.usage.input_tokens}[/yellow]  "
        f"Output tokens: [yellow]{message.usage.output_tokens}[/yellow]\n"
    )


# ── 2. Multi-turn conversation ─────────────────────────────────────────
def demo_multi_turn():
    console.print(Rule("[bold]2. Multi-Turn Conversation (Claude)[/bold]"))
    conversation = []
    turns = [
        "What is ReAct as a design pattern for AI agents?",
        "How does it relate to the Plan step in the PPAS loop?",
    ]
    for user_msg in turns:
        conversation.append({"role": "user", "content": user_msg})
        response = client.messages.create(
            model=model,
            max_tokens=300,
            system="You are a concise AI tutor specialising in Agentic AI.",
            messages=conversation,
        )
        reply = response.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        console.print(f"[bold]You:[/bold] {user_msg}")
        console.print(f"[green]Claude:[/green] {reply}\n")


# ── 3. Streaming ───────────────────────────────────────────────────────
def demo_streaming():
    console.print(Rule("[bold]3. Streaming Response (Claude)[/bold]"))
    console.print("[dim]Streaming:[/dim] ", end="")
    with client.messages.stream(
        model=model,
        max_tokens=512,
        messages=[
            {"role": "user", "content": "Explain the ReAct design pattern for AI agents in 3 bullet points."},
        ],
    ) as stream:
        for text in stream.text_stream:
            console.print(text, end="")
    console.print("\n")


if __name__ == "__main__":
    demo_basic()
    demo_multi_turn()
    demo_streaming()
