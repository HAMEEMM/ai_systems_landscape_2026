"""
phase-2-agent-core/04-planning-reflection/01_tree_of_thought.py

Layer 6 — Planning & Reflection: Tree-of-Thought (ToT).

Tree-of-Thought extends Chain-of-Thought by generating MULTIPLE
reasoning branches in parallel and then selecting the best one.
This directly implements the PLAN step with explicit self-evaluation.

Flow:
    Goal
     ├── Branch A: reasoning path A → evaluate
     ├── Branch B: reasoning path B → evaluate
     └── Branch C: reasoning path C → evaluate
              ↓
         Best branch → execute

This is how agents handle ambiguous goals where a single greedy
reasoning chain might go wrong — they explore alternatives first.

Paper reference: §5 Design Patterns — Tree-of-Thought

Run:
    cd publications/01-agentic-ai/dev
    python phase-2-agent-core/04-planning-reflection/01_tree_of_thought.py
"""

import sys
from pathlib import Path
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_openai_client
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

console = Console()
client, model = get_openai_client()


@dataclass
class ReasoningBranch:
    branch_id: str
    reasoning: str
    proposed_action: str
    score: float        # 0.0–1.0 from the evaluator
    explanation: str    # why the evaluator gave that score


# ── Step 1: Generate multiple reasoning branches ───────────────────────
def generate_branches(goal: str, n_branches: int = 3) -> list[ReasoningBranch]:
    """Ask the LLM to produce N distinct reasoning paths for the goal."""
    prompt = (
        f"Goal: {goal}\n\n"
        f"Generate {n_branches} DISTINCT reasoning approaches to achieve this goal. "
        f"For each approach:\n"
        f"  - Think through the problem differently\n"
        f"  - Propose a specific first action\n"
        f"  - Consider edge cases\n\n"
        f"Format each approach as:\n"
        f"BRANCH [letter]:\n"
        f"Reasoning: <step-by-step thinking>\n"
        f"Proposed action: <specific first action to take>\n"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a strategic planning agent."},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.choices[0].message.content

    # Parse branches from the response
    branches = []
    raw_blocks = [b for b in text.split("BRANCH") if b.strip()]
    for i, block in enumerate(raw_blocks[:n_branches]):
        lines = block.strip().splitlines()
        letter = chr(65 + i)  # A, B, C
        reasoning_lines, action = [], ""
        mode = "reasoning"
        for line in lines:
            if "Proposed action:" in line:
                mode = "action"
                action = line.split("Proposed action:", 1)[-1].strip()
            elif mode == "reasoning" and line.strip() and not line.startswith("["):
                reasoning_lines.append(line.strip())
        branches.append(ReasoningBranch(
            branch_id=letter,
            reasoning=" ".join(reasoning_lines),
            proposed_action=action or "(see reasoning)",
            score=0.0,
            explanation="",
        ))

    return branches


# ── Step 2: Evaluate each branch ───────────────────────────────────────
def evaluate_branches(goal: str, branches: list[ReasoningBranch]) -> list[ReasoningBranch]:
    """Ask the LLM to score each branch on feasibility and effectiveness."""
    branch_text = "\n\n".join(
        f"Branch {b.branch_id}:\n{b.reasoning}\nAction: {b.proposed_action}"
        for b in branches
    )
    prompt = (
        f"Goal: {goal}\n\n"
        f"Evaluate each reasoning branch below. "
        f"For each, give a score from 0.0 to 1.0 and a one-sentence explanation.\n\n"
        f"{branch_text}\n\n"
        f"Format:\n"
        f"Branch A: score=0.X | <explanation>\n"
        f"Branch B: score=0.X | <explanation>\n"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a critical evaluator of reasoning approaches."},
            {"role": "user", "content": prompt},
        ],
    )
    eval_text = response.choices[0].message.content

    for line in eval_text.splitlines():
        for branch in branches:
            if f"Branch {branch.branch_id}:" in line and "score=" in line:
                try:
                    score_part = line.split("score=")[1].split("|")[0].strip()
                    branch.score = float(score_part)
                    if "|" in line:
                        branch.explanation = line.split("|", 1)[1].strip()
                except (ValueError, IndexError):
                    pass

    return sorted(branches, key=lambda b: b.score, reverse=True)


# ── Step 3: Execute the best branch ───────────────────────────────────
def execute_best_branch(goal: str, best: ReasoningBranch) -> str:
    """Execute the highest-scoring reasoning path."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an execution agent. Follow the given reasoning and complete the goal.",
            },
            {
                "role": "user",
                "content": (
                    f"Goal: {goal}\n\n"
                    f"Selected reasoning approach:\n{best.reasoning}\n\n"
                    f"Now execute this approach and provide the complete answer."
                ),
            },
        ],
    )
    return response.choices[0].message.content


# ── Full ToT pipeline ──────────────────────────────────────────────────
def tree_of_thought(goal: str) -> str:
    console.print(Panel(f"[bold cyan]{goal}[/bold cyan]", title="Tree-of-Thought Planning"))

    # 1. Generate
    console.print(Rule("[dim]Step 1: Generating reasoning branches[/dim]"))
    branches = generate_branches(goal, n_branches=3)

    # 2. Evaluate
    console.print(Rule("[dim]Step 2: Evaluating branches[/dim]"))
    branches = evaluate_branches(goal, branches)

    table = Table("Branch", "Score", "Action", "Evaluation")
    for b in branches:
        table.add_row(
            b.branch_id,
            f"{b.score:.2f}",
            b.proposed_action[:60],
            b.explanation[:80],
        )
    console.print(table)

    best = branches[0]
    console.print(f"\nSelected: [bold green]Branch {best.branch_id}[/bold green] (score={best.score:.2f})")

    # 3. Execute
    console.print(Rule("[dim]Step 3: Executing best branch[/dim]"))
    result = execute_best_branch(goal, best)
    console.print(Panel(result, title="[bold green]Final Answer[/bold green]"))
    return result


if __name__ == "__main__":
    goal = (
        "Design a strategy for evaluating whether a new multi-agent AI system "
        "is ready for production deployment. What are the key criteria and tests?"
    )
    tree_of_thought(goal)
