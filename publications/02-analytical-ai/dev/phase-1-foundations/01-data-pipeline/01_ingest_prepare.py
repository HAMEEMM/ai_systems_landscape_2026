"""
phase-1-foundations/01-data-pipeline/01_ingest_prepare.py
──────────────────────────────────────────────────────────
Paper §2 — 7-Stage Analytics Pipeline: Stages 1 (Ingest) & 2 (Prepare)

Demonstrates:
 • Loading data from CSV, DuckDB in-memory, and a REST API simulation
 • Schema validation (dtypes, nulls, ranges)
 • Normalisation, join, and feature engineering
 • Building a semantic layer (metric definitions)

Run:  python phase-1-foundations/01-data-pipeline/01_ingest_prepare.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import io
import pandas as pd
import numpy as np
import duckdb
from rich.console import Console
from utils.data_utils import make_sales_df, make_customer_df, print_df

console = Console()

# ── 1. INGEST ─────────────────────────────────────────────────────────────

def ingest_csv() -> pd.DataFrame:
    """Simulate CSV ingestion (e.g. exported from Salesforce / ERP)."""
    df = make_sales_df(n_rows=2_000)
    console.print(f"[cyan]Ingested CSV:[/cyan] {len(df):,} rows × {len(df.columns)} cols")
    return df


def ingest_duckdb(df: pd.DataFrame) -> pd.DataFrame:
    """Persist to DuckDB (in-memory OLAP engine) and query back via SQL."""
    con = duckdb.connect()
    con.register("sales_raw", df)
    result = con.execute("""
        SELECT
            date_trunc('day', date)          AS day,
            product,
            region,
            SUM(units)                       AS total_units,
            ROUND(SUM(revenue), 2)           AS total_revenue,
            COUNT(*)                         AS txn_count
        FROM sales_raw
        GROUP BY 1, 2, 3
        ORDER BY 1
    """).df()
    console.print(f"[cyan]DuckDB aggregate:[/cyan] {len(result):,} rows")
    return result


# ── 2. PREPARE ────────────────────────────────────────────────────────────

def validate_schema(df: pd.DataFrame) -> None:
    """Basic schema/quality checks — mirrors Great Expectations logic."""
    checks = {
        "no_null_revenue":    df["revenue"].isna().sum() == 0,
        "positive_units":     (df["units"] > 0).all(),
        "discount_in_range":  df["discount"].between(0, 1).all(),
        "date_monotonic":     df["date"].is_monotonic_increasing,
    }
    for name, passed in checks.items():
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        console.print(f"  {status} — {name}")


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering: day-of-week, revenue buckets, discount flag."""
    df = df.copy()
    df["dow"]           = df["date"].dt.day_name()
    df["revenue_tier"]  = pd.cut(
        df["revenue"],
        bins=[0, 100, 500, 2_000, np.inf],
        labels=["micro", "small", "medium", "large"],
    )
    df["is_discounted"] = df["discount"] > 0.05
    return df


# ── 3. SEMANTIC LAYER (metric definitions) ────────────────────────────────

METRIC_CATALOG = {
    "total_revenue":     "SUM(revenue)",
    "avg_order_value":   "AVG(revenue)",
    "discount_rate":     "AVG(discount)",
    "conversion_units":  "SUM(units)",
}

def resolve_metric(name: str, df: pd.DataFrame) -> float:
    """Mimic a semantic layer: translate metric name → SQL expression."""
    if name not in METRIC_CATALOG:
        raise KeyError(f"Unknown metric: {name!r}. Known: {list(METRIC_CATALOG)}")
    expr = METRIC_CATALOG[name]
    return duckdb.query(f"SELECT {expr} FROM df").fetchone()[0]


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Stage 1: Ingest")
    raw = ingest_csv()
    daily = ingest_duckdb(raw)

    console.rule("[bold]Stage 2: Prepare — Validation")
    validate_schema(raw)

    console.rule("[bold]Stage 2: Prepare — Enrichment")
    enriched = enrich(raw)
    print_df(enriched[["date", "product", "region", "revenue", "revenue_tier",
                        "is_discounted", "dow"]], title="Enriched Sample")

    console.rule("[bold]Semantic Layer — Metric Resolution")
    for metric in METRIC_CATALOG:
        val = resolve_metric(metric, raw)
        console.print(f"  [yellow]{metric}[/yellow] = {val:,.4f}")

    console.print("\n[green]✓ Ingest → Prepare pipeline complete.[/green]")
