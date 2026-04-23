"""
phase-1-foundations/03-agent-loop-scratch/01_ppas_loop.py

PERCEIVE → PLAN → ACT → SELF-CORRECT — implemented from scratch.

This file builds the agent loop described in the paper using ONLY the
raw OpenAI API — no LangGraph, no LangChain. Every line is explicit so
you can see exactly what each step does before adding a framework on top.

After understanding this file, open phase-2-agent-core/01-langgraph-react/
to see the same logic expressed with LangGraph, and compare what the
framework buys you (state management, checkpointing, observability).

Paper reference:
  §3 — The Agent Loop Framework (Perceive → Plan → Act → Self-Correct)
  §4 Layer 2 — Runtime & Orchestration
  §4 Layer 4 — Tools & Integration

Run:
    cd publications/01-agentic-ai/dev
    python phase-1-foundations/03-agent-loop-scratch/01_ppas_loop.py

    # Or pass a goal index (0, 1, or 2):
    python phase-1-foundations/03-agent-loop-scratch/01_ppas_loop.py 1
"""

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.utils.llm_client import get_openai_client
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()

# ─────────────────────────────────────────────────────────────────────
# TOOL DEFINITIONS (Layer 4 — Tools & Integration)
# Each tool is declared to the LLM as a JSON schema, then executed
# locally when the LLM calls it.
# ─────────────────────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a Python arithmetic expression. Use for any math.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A valid Python expression, e.g. '2 ** 10' or '10000 * (1.07**5)'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_today",
            "description": "Returns today's date in ISO 8601 format (YYYY-MM-DD).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": (
                "Call this when the goal is fully achieved. "
                "Provide the complete, final answer to deliver to the user."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The complete final answer.",
                    }
                },
                "required": ["answer"],
            },
        },
    },
]


# ─────────────────────────────────────────────────────────────────────
# ACT STEP — execute the tool the LLM selected
# ─────────────────────────────────────────────────────────────────────
def execute_tool(name: str, args: dict[str, Any]) -> str:
    """
    Run the tool locally and return a string result.
    The result feeds back into PERCEIVE as the next observation.
    """
    if name == "calculator":
        try:
            # Safe eval: no builtins, only math operators/values
            result = eval(args["expression"], {"__builtins__": {}}, {})  # nosec
            return str(result)
        except Exception as exc:
            return f"Error evaluating expression: {exc}"

    if name == "get_today":
        return date.today().isoformat()

    if name == "finish":
        return args["answer"]

    return f"Unknown tool: {name}"


# ─────────────────────────────────────────────────────────────────────
# THE PPAS AGENT
# ─────────────────────────────────────────────────────────────────────
class PPASAgent:
    """
    Minimal Agentic AI running the canonical loop:

        PERCEIVE → PLAN → ACT → SELF-CORRECT → (repeat until done)

    State:
        self.messages — the full conversation history.
        This IS the agent's working memory (Layer 3, short-term).
        Every tool result gets appended so the LLM always sees
        the complete picture of what has happened so far.
    """

    SYSTEM_PROMPT = (
        "You are a goal-directed agent. Follow the PPAS loop:\n"
        "  1. PERCEIVE  — read the goal and all previous tool results\n"
        "  2. PLAN      — decide the single best next action\n"
        "  3. ACT       — call exactly one tool\n"
        "  4. SELF-CORRECT — the result comes back; reassess and loop\n\n"
        "Rules:\n"
        "  - Always use a tool. Never answer in plain text until you call 'finish'.\n"
        "  - If a calculation result looks wrong, call 'calculator' again with a corrected expression.\n"
        "  - When the goal is fully achieved, call 'finish' with the complete answer."
    )

    def __init__(self, goal: str, max_iterations: int = 10):
        self.goal = goal
        self.max_iterations = max_iterations
        self.client, self.model = get_openai_client()

        # Working memory: the full message history sent to the LLM each call
        self.messages: list[dict] = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user",   "content": f"GOAL: {goal}"},
        ]
        self.iteration = 0

    # ── PERCEIVE ──────────────────────────────────────────────────────
    def perceive(self) -> str:
        """
        The agent's perception IS the message history.
        The LLM reads the entire history on every call —
        that's how it knows what has already happened.
        """
        return (
            f"Iteration {self.iteration} | "
            f"{len(self.messages)} messages in working memory"
        )

    # ── PLAN + ACT ────────────────────────────────────────────────────
    def plan_and_act(self) -> tuple[str, dict, str]:
        """
        PLAN:  Call the LLM — it reads the history and decides on a tool.
        ACT:   Execute that tool locally.
        Returns: (tool_name, tool_args, tool_result)
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=TOOLS,
            tool_choice="required",   # force a tool call; no free-text replies
        )
        msg = response.choices[0].message

        # Append the assistant's decision to working memory
        self.messages.append(msg)

        # Extract the tool call
        tool_call = msg.tool_calls[0]
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        # Execute the tool
        result = execute_tool(name, args)

        # SELF-CORRECT: feed the result back into memory so the agent can evaluate it
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

        return name, args, result

    # ── SELF-CORRECT ──────────────────────────────────────────────────
    def self_correct(self, tool_name: str) -> bool:
        """
        Assess whether the loop is complete.
        The LLM decides to call 'finish' when it is satisfied with its answer.
        If it calls any other tool, the loop continues.
        Returns True when the goal is achieved.
        """
        return tool_name == "finish"

    # ── FULL LOOP ─────────────────────────────────────────────────────
    def run(self) -> str:
        console.print(Panel(f"[bold cyan]GOAL:[/bold cyan] {self.goal}", title="PPAS Agent — From Scratch"))

        while self.iteration < self.max_iterations:
            self.iteration += 1

            # PERCEIVE
            status = self.perceive()
            console.print(f"\n[dim]PERCEIVE:[/dim]     {status}")

            # PLAN + ACT
            name, args, result = self.plan_and_act()
            console.print(f"[yellow]PLAN/ACT:[/yellow]     tool=[bold]{name}[/bold]  args={args}")
            console.print(f"[green]RESULT:[/green]       {result[:200]}")

            # SELF-CORRECT
            if self.self_correct(name):
                console.print(
                    Panel(
                        f"[bold green]{result}[/bold green]",
                        title=f"[bold]Goal Achieved — {self.iteration} iteration(s)[/bold]",
                    )
                )
                return result

        console.print(Rule("[red]Max iterations reached without finishing[/red]"))
        return "Agent did not reach a conclusion within the iteration limit."


# ─────────────────────────────────────────────────────────────────────
# DEMO GOALS — try all three to see different loop behaviours
# ─────────────────────────────────────────────────────────────────────
DEMO_GOALS = [
    # Goal 0 — single-step (one tool call then finish)
    "What is 2 raised to the power of 10?",

    # Goal 1 — two-step: date lookup then arithmetic
    (
        "If today is the starting date, what calendar date is exactly 90 days from now? "
        "First get today's date, then calculate by adding 90 to the day-of-year."
    ),

    # Goal 2 — multi-step with self-correction opportunity
    (
        "Calculate the compound interest earned on $10,000 invested at 7% annual rate "
        "for 5 years. Formula: principal * (1 + rate)^years - principal. "
        "Show only the interest earned, not the total balance."
    ),
]

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    goal = DEMO_GOALS[idx % len(DEMO_GOALS)]
    agent = PPASAgent(goal=goal)
    agent.run()
