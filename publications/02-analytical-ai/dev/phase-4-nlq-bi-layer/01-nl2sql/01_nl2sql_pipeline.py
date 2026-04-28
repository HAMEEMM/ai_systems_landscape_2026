"""
phase-4-nlq-bi-layer/01-nl2sql/01_nl2sql_pipeline.py
──────────────────────────────────────────────────────
Paper §7 — NL2SQL: 5-Level NLQ Maturity Model

Demonstrates:
 • Level 1 — Template-based (no LLM, deterministic)
 • Level 2 — Schema-aware few-shot prompting (OpenAI GPT-4o)
 • Level 3 — Chain-of-thought decomposition (DIN-SQL style)
 • Semantic layer integration (metric catalog → SQL template)
 • Common failure modes: schema hallucination, semantic mismatch

RQ4 finding: Production NL2SQL accuracy 65–85% depends on semantic layer.

Requires:  OPENAI_API_KEY in shared/config/.env
Run:       python phase-4-nlq-bi-layer/01-nl2sql/01_nl2sql_pipeline.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import os
import json
import duckdb
import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from utils.data_utils import make_sales_df

load_dotenv(pathlib.Path(__file__).resolve().parents[2] / "shared" / "config" / ".env")
console = Console()


# ── Shared in-memory DuckDB ───────────────────────────────────────────────

def build_db() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    df  = make_sales_df(n_rows=5_000)
    con.register("sales", df)
    return con, df


# ── Schema catalog (semantic layer) ──────────────────────────────────────

SCHEMA = """
Table: sales
Columns:
  date       DATE        -- transaction timestamp
  product    VARCHAR     -- product category
  region     VARCHAR     -- sales region
  units      INTEGER     -- units sold
  price      FLOAT       -- unit price (USD)
  discount   FLOAT       -- discount fraction [0,1]
  revenue    FLOAT       -- units * price * (1 - discount)
"""

# ── Level 1: Template-based NLQ ──────────────────────────────────────────

TEMPLATE_MAP = {
    "total revenue":           "SELECT SUM(revenue) AS total_revenue FROM sales",
    "revenue by product":      "SELECT product, SUM(revenue) FROM sales GROUP BY product ORDER BY 2 DESC",
    "revenue by region":       "SELECT region, SUM(revenue) FROM sales GROUP BY region ORDER BY 2 DESC",
    "top product":             "SELECT product, SUM(revenue) AS rev FROM sales GROUP BY product ORDER BY rev DESC LIMIT 1",
    "average order value":     "SELECT AVG(revenue) AS avg_order_value FROM sales",
}

def level1_template(question: str, con: duckdb.DuckDBPyConnection) -> str:
    q = question.lower().strip().rstrip("?")
    for key, sql in TEMPLATE_MAP.items():
        if key in q:
            result = con.execute(sql).df()
            return f"Level-1 Template → SQL: {sql}\nResult:\n{result.to_string(index=False)}"
    return f"Level-1: No template match for '{question}'"


# ── Level 2: LLM few-shot ─────────────────────────────────────────────────

FEW_SHOT = """You are a SQL expert. Given the schema below, write a single valid DuckDB SQL query.
Return ONLY the SQL — no explanation, no markdown fences.

Schema:
{schema}

Examples:
Q: What is the total revenue?
A: SELECT SUM(revenue) AS total_revenue FROM sales

Q: Which region had the most units sold last month?
A: SELECT region, SUM(units) AS units FROM sales WHERE date >= date_trunc('month', current_date - INTERVAL '1 month') GROUP BY region ORDER BY units DESC LIMIT 1

Q: {question}
A:"""

def level2_llm(question: str, con: duckdb.DuckDBPyConnection) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-..."):
        return "Level-2: OPENAI_API_KEY not set — skipping LLM call."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = FEW_SHOT.format(schema=SCHEMA, question=question)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200,
        )
        sql = resp.choices[0].message.content.strip()
        try:
            result = con.execute(sql).df()
            return f"Level-2 LLM SQL: {sql}\nResult:\n{result.head(5).to_string(index=False)}"
        except Exception as e:
            return f"Level-2 LLM SQL: {sql}\nExecution error: {e}"
    except Exception as e:
        return f"Level-2 LLM error: {e}"


# ── Level 3: Chain-of-Thought decomposition ───────────────────────────────

def level3_cot(question: str, con: duckdb.DuckDBPyConnection) -> str:
    """
    DIN-SQL style: decompose → sub-schema linking → SQL generation.
    Simulated here without LLM to show the structural pattern.
    """
    steps = [
        f"1. Parse question: '{question}'",
        "2. Link entities: 'product' → sales.product, 'revenue' → SUM(revenue)",
        "3. Detect aggregation: TOP-N → ORDER BY ... LIMIT N",
        "4. Detect filter: 'last quarter' → WHERE date >= ...",
        "5. Generate SQL: SELECT product, SUM(revenue) FROM sales "
           "WHERE date >= date_trunc('quarter', current_date - INTERVAL '3 months') "
           "GROUP BY product ORDER BY 2 DESC LIMIT 5",
    ]
    sql = ("SELECT product, ROUND(SUM(revenue),2) AS revenue FROM sales "
           "GROUP BY product ORDER BY revenue DESC LIMIT 5")
    result = con.execute(sql).df()
    output = "\n".join(steps) + f"\nResult:\n{result.to_string(index=False)}"
    return f"Level-3 CoT:\n{output}"


# ── Failure mode demonstration ────────────────────────────────────────────

def show_failure_modes() -> None:
    console.rule("[bold]RQ4 — NL2SQL Failure Modes")
    failures = {
        "Schema hallucination":
            "LLM generates column 'customer_id' that doesn't exist in the schema.",
        "Semantic mismatch":
            "'Best-selling product' interpreted as MAX(units) instead of MAX(revenue).",
        "Ambiguous aggregation":
            "'Monthly revenue' — unclear if SUM per month or most recent month.",
        "Missing semantic layer":
            "Without a certified 'revenue' metric definition, "
            "LLM may compute price*units ignoring discount.",
    }
    for mode, desc in failures.items():
        console.print(f"  [red]✗[/red] [bold]{mode}:[/bold] {desc}")


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 4 — NL2SQL (5-Level NLQ Maturity)")
    con, df = build_db()

    questions = [
        "What is the total revenue?",
        "Show revenue by product",
        "Which is the top product by revenue?",
    ]

    for q in questions:
        console.rule(f"[dim]Q: {q}[/dim]")
        console.print(f"[green]Level 1:[/green] {level1_template(q, con)}")
        console.print(f"[green]Level 2:[/green] {level2_llm(q, con)}")
        console.print(f"[green]Level 3:[/green]\n{level3_cot(q, con)}")

    show_failure_modes()
    console.print("\n[green]✓ NL2SQL pipeline complete.[/green]")
