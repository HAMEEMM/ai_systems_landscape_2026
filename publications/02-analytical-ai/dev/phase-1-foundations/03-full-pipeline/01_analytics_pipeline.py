"""
phase-1-foundations/03-full-pipeline/01_analytics_pipeline.py
──────────────────────────────────────────────────────────────
Paper §2 — All 7 Pipeline Stages end-to-end in one script.

Demonstrates the complete loop:
  Ingest → Prepare → Analyse → Surface → Explain → Distribute → Feedback

Run:  python phase-1-foundations/03-full-pipeline/01_analytics_pipeline.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import json
import pandas as pd
import numpy as np
import duckdb
from rich.console import Console
from utils.data_utils import make_sales_df, save_results

console = Console()


# ── Stage 1: INGEST ───────────────────────────────────────────────────────
def stage_ingest() -> pd.DataFrame:
    df = make_sales_df(n_rows=3_000)
    console.print(f"[1/7] [cyan]INGEST[/cyan]   {len(df):,} rows loaded")
    return df


# ── Stage 2: PREPARE ─────────────────────────────────────────────────────
def stage_prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna()
    df = df[df["revenue"] > 0]
    df["month"]      = df["date"].dt.to_period("M").astype(str)
    df["revenue_log"] = np.log1p(df["revenue"])
    console.print(f"[2/7] [cyan]PREPARE[/cyan]  {len(df):,} clean rows, 2 features added")
    return df


# ── Stage 3: ANALYSE ─────────────────────────────────────────────────────
def stage_analyse(df: pd.DataFrame) -> dict:
    con = duckdb.connect()
    con.register("df", df)

    top_products = con.execute("""
        SELECT product, ROUND(SUM(revenue),2) AS total_rev
        FROM df GROUP BY product ORDER BY total_rev DESC LIMIT 3
    """).df().to_dict("records")

    monthly_trend = con.execute("""
        SELECT month, ROUND(SUM(revenue),2) AS monthly_rev
        FROM df GROUP BY month ORDER BY month
    """).df().to_dict("records")

    console.print(f"[3/7] [cyan]ANALYSE[/cyan]  Top 3 products: "
                  f"{[p['product'] for p in top_products]}")
    return {"top_products": top_products, "monthly_trend": monthly_trend}


# ── Stage 4: SURFACE ─────────────────────────────────────────────────────
def stage_surface(analysis: dict) -> str:
    kpis = {
        "top_product":   analysis["top_products"][0]["product"],
        "top_revenue":   analysis["top_products"][0]["total_rev"],
        "months_tracked": len(analysis["monthly_trend"]),
    }
    console.print(f"[4/7] [cyan]SURFACE[/cyan]  KPIs: {kpis}")
    return json.dumps(kpis)


# ── Stage 5: EXPLAIN ─────────────────────────────────────────────────────
def stage_explain(kpis_json: str) -> str:
    kpis = json.loads(kpis_json)
    narrative = (
        f"In the analysis period ({kpis['months_tracked']} months), "
        f"{kpis['top_product']} led all categories with "
        f"${kpis['top_revenue']:,.2f} in total revenue. "
        "Consider prioritising inventory and marketing spend on this category."
    )
    console.print(f"[5/7] [cyan]EXPLAIN[/cyan]  {narrative}")
    return narrative


# ── Stage 6: DISTRIBUTE ───────────────────────────────────────────────────
def stage_distribute(narrative: str, kpis_json: str) -> None:
    # In production: push to Slack, email, BI tool
    payload = {"channel": "#bi-alerts", "message": narrative, "kpis": json.loads(kpis_json)}
    # Simulated — print the payload that would be POSTed
    console.print(f"[6/7] [cyan]DISTRIBUTE[/cyan] [dim](simulated) Slack payload ready[/dim]")
    save_results(payload, "pipeline_distribute_output.json")


# ── Stage 7: FEEDBACK ────────────────────────────────────────────────────
def stage_feedback(df: pd.DataFrame) -> None:
    # Simulate feedback loop: measure action taken, log quality metric
    quality_score = round(1 - df.isna().sum().sum() / df.size, 4)
    feedback = {
        "pipeline_run":    "2026-04-26",
        "data_quality":    quality_score,
        "rows_processed":  len(df),
        "action_taken":    "dashboard_updated",
    }
    console.print(f"[7/7] [cyan]FEEDBACK[/cyan] Data quality score: {quality_score:.4f}")
    save_results(feedback, "pipeline_feedback.json")


# ── MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    console.rule("[bold]Analytical AI — 7-Stage Pipeline (End-to-End)")

    raw       = stage_ingest()
    clean     = stage_prepare(raw)
    analysis  = stage_analyse(clean)
    kpis_json = stage_surface(analysis)
    narrative = stage_explain(kpis_json)
    stage_distribute(narrative, kpis_json)
    stage_feedback(clean)

    console.print("\n[green]✓ All 7 pipeline stages complete.[/green]")
