"""
phase-4-productionize/03-benchmark-eval/01_benchmark_intro.py

Benchmark Evaluation — Introduction to the paper's four benchmarks.

The paper uses four benchmarks to validate the PPAS framework (§8):

  ┌─────────────────┬──────────────────────────────────────────────────────┐
  │ Benchmark       │ What it measures                                     │
  ├─────────────────┼──────────────────────────────────────────────────────┤
  │ SWE-Bench       │ Coding: resolve real GitHub issues in large codebases│
  │ WebArena        │ Web navigation: complete tasks on live websites       │
  │ GAIA            │ General assistants: multi-step real-world Q&A         │
  │ BrowseComp      │ Browsing: find obscure facts requiring deep search    │
  └─────────────────┴──────────────────────────────────────────────────────┘

This file:
  1. Describes each benchmark and how to access it
  2. Implements a micro-benchmark you can run right now
     (a scaled-down GAIA-style multi-step reasoning task)
  3. Shows how to log benchmark results for §8 of the paper

Paper reference: §8 Empirical Evaluation

Run:
    cd publications/01-agentic-ai/dev
    python phase-4-productionize/03-benchmark-eval/01_benchmark_intro.py
"""

import json
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.utils.llm_client import get_openai_client
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.rule import Rule

console = Console()
client, model = get_openai_client()


# ── Benchmark descriptions ─────────────────────────────────────────────
BENCHMARKS = {
    "SWE-Bench Verified": {
        "url":         "https://www.swebench.com/",
        "tasks":       500,
        "metric":      "% issues resolved",
        "state_of_art": "Claude Opus 4.5 + scaffolding: ~70%",
        "what_it_tests": "Code editing, debugging, understanding large repos",
        "how_to_run":  "pip install swebench; run eval harness on Docker",
    },
    "WebArena": {
        "url":         "https://webarena.dev/",
        "tasks":       812,
        "metric":      "Task success rate",
        "state_of_art": "~35–45% (GPT-4o + browser agent)",
        "what_it_tests": "Web navigation, form filling, multi-step web tasks",
        "how_to_run":  "Requires local web server setup; see webarena.dev",
    },
    "GAIA": {
        "url":         "https://huggingface.co/datasets/gaia-benchmark/GAIA",
        "tasks":       450,
        "metric":      "Exact match accuracy",
        "state_of_art": "~65% (Level 1); ~15% (Level 3)",
        "what_it_tests": "Multi-step reasoning with tools (search, calculator, file reading)",
        "how_to_run":  "pip install datasets; load via HuggingFace",
    },
    "BrowseComp": {
        "url":         "https://openai.com/index/browsecomp/",
        "tasks":       1266,
        "metric":      "Exact answer accuracy",
        "state_of_art": "~50% (o3 + deep research)",
        "what_it_tests": "Finding obscure facts that require many web searches",
        "how_to_run":  "Available via OpenAI Evals framework",
    },
}


def show_benchmark_overview():
    console.print(Rule("[bold]Paper §8 Benchmark Overview[/bold]"))
    table = Table("Benchmark", "Tasks", "Metric", "State of Art (2026)", "Tests")
    for name, info in BENCHMARKS.items():
        table.add_row(
            name,
            str(info["tasks"]),
            info["metric"],
            info["state_of_art"],
            info["what_it_tests"][:55],
        )
    console.print(table)


# ── Micro-benchmark: GAIA-style multi-step questions ──────────────────
@dataclass
class BenchmarkTask:
    task_id: str
    question: str
    expected_answer: str         # for exact-match scoring
    level: int = 1               # 1 = easy, 3 = hard (GAIA levels)


@dataclass
class BenchmarkResult:
    task_id: str
    question: str
    agent_answer: str
    expected: str
    correct: bool
    latency_s: float
    tokens_used: int


MICRO_BENCHMARK_TASKS = [
    BenchmarkTask(
        task_id="G-001",
        question=(
            "What is the DOI of the paper 'Perceive, Plan, Act, Self-Correct' "
            "by Hameem M Mahdi, and on which preprint server was it published?"
        ),
        expected_answer="10.31224/6738",
        level=1,
    ),
    BenchmarkTask(
        task_id="G-002",
        question=(
            "How many layers are in the Agentic AI technology stack described in "
            "the PPAS framework paper, and what is Layer 5 called?"
        ),
        expected_answer="8 layers; Layer 5 is Inter-Agent Protocols",
        level=1,
    ),
    BenchmarkTask(
        task_id="G-003",
        question=(
            "If the Agentic AI market is $7.3 billion in 2025 and grows at 39% CAGR, "
            "what is the market size (in billions, rounded to 1 decimal place) in 2030?"
        ),
        expected_answer="$38.8 billion",
        level=2,
    ),
]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a Python arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    }
]


def run_agent_on_task(task: BenchmarkTask) -> BenchmarkResult:
    """Run a simple PPAS agent on one benchmark task and score it."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise research agent. Answer the question exactly. "
                "Use the calculator tool for any arithmetic."
            ),
        },
        {"role": "user", "content": task.question},
    ]

    start = time.perf_counter()
    total_tokens = 0

    for _ in range(6):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS
        )
        total_tokens += response.usage.total_tokens
        msg = response.choices[0].message

        if not msg.tool_calls:
            answer = msg.content
            break

        messages.append(msg)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            try:
                result = str(eval(args["expression"], {"__builtins__": {}}, {}))  # nosec
            except Exception as exc:
                result = f"Error: {exc}"
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    else:
        answer = "Did not finish within iteration limit."

    latency = time.perf_counter() - start

    # Exact-match scoring (case-insensitive substring match)
    correct = task.expected_answer.lower() in answer.lower()

    return BenchmarkResult(
        task_id=task.task_id,
        question=task.question,
        agent_answer=answer,
        expected=task.expected_answer,
        correct=correct,
        latency_s=round(latency, 2),
        tokens_used=total_tokens,
    )


def run_micro_benchmark():
    console.print(Rule("[bold]Micro-Benchmark Run (GAIA-style)[/bold]"))
    results = []
    for task in MICRO_BENCHMARK_TASKS:
        console.print(f"\n[dim]Task {task.task_id} (Level {task.level}):[/dim] {task.question[:80]}...")
        result = run_agent_on_task(task)
        results.append(result)
        status = "[green]CORRECT[/green]" if result.correct else "[red]WRONG[/red]"
        console.print(f"  Status: {status} | Latency: {result.latency_s}s | Tokens: {result.tokens_used}")
        console.print(f"  Expected: {result.expected}")
        console.print(f"  Got:      {result.agent_answer[:120]}")

    # Summary table
    console.print(Rule("[bold]Results Summary[/bold]"))
    n_correct = sum(r.correct for r in results)
    table = Table("Task", "Level", "Correct", "Latency", "Tokens")
    for r in results:
        task = next(t for t in MICRO_BENCHMARK_TASKS if t.task_id == r.task_id)
        table.add_row(
            r.task_id,
            str(task.level),
            "[green]✓[/green]" if r.correct else "[red]✗[/red]",
            f"{r.latency_s}s",
            str(r.tokens_used),
        )
    console.print(table)
    console.print(f"\n[bold]Score: {n_correct}/{len(results)} ({n_correct/len(results):.0%})[/bold]")

    # Save results to JSON for §8 data
    output_path = Path(__file__).parent / "micro_benchmark_results.json"
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "score": f"{n_correct}/{len(results)}",
        "results": [
            {
                "task_id": r.task_id,
                "correct": r.correct,
                "latency_s": r.latency_s,
                "tokens": r.tokens_used,
            }
            for r in results
        ],
    }
    output_path.write_text(json.dumps(output, indent=2))
    console.print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    show_benchmark_overview()
    console.print()
    run_micro_benchmark()
