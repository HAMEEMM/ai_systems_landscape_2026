"""
phase-5-experiments/01-benchmark-results/run_benchmarks.py
────────────────────────────────────────────────────────────
Paper §9 — Full Benchmark Suite

Runs all five phases sequentially, collects results, and produces a
consolidated JSON report + markdown summary.

Covers:
 • Pipeline throughput (rows/sec) — Section 2
 • Clustering silhouette / Davies-Bouldin — Section 5
 • Anomaly detection precision/recall at 5% contamination — Section 5
 • Causal inference bias/RMSE (manual OLS) — Section 6
 • Data quality score — Section 8
 • NL2SQL template coverage — Section 7

Run:  python phase-5-experiments/01-benchmark-results/run_benchmarks.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import time
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score
from sklearn.linear_model import LinearRegression
from rich.console import Console
from rich.table import Table
from utils.data_utils import (make_sales_df, make_customer_df,
                               make_time_series, save_results, ensure_dir)

console = Console()


# ── 1. Pipeline throughput ────────────────────────────────────────────────

def bench_pipeline() -> dict:
    start = time.perf_counter()
    df = make_sales_df(n_rows=10_000)
    df = df.dropna()
    df["revenue_log"] = np.log1p(df["revenue"])
    elapsed = time.perf_counter() - start
    return {"rows_per_sec": round(10_000 / elapsed, 1),
            "total_rows": len(df)}


# ── 2. Clustering quality ─────────────────────────────────────────────────

def bench_clustering() -> dict:
    df = make_customer_df(n_rows=1_000)
    X  = StandardScaler().fit_transform(df)
    km = KMeans(n_clusters=4, random_state=42, n_init=10).fit(X)
    return {
        "silhouette":      round(silhouette_score(X, km.labels_), 4),
        "davies_bouldin":  round(davies_bouldin_score(X, km.labels_), 4),
        "n_clusters":      4,
    }


# ── 3. Anomaly detection precision/recall ────────────────────────────────

def bench_anomaly() -> dict:
    rng  = np.random.default_rng(7)
    n    = 1_000
    X    = rng.standard_normal((n, 5))
    # Plant 50 true anomalies
    X[:50] += rng.uniform(3, 6, (50, 5))
    true_labels = np.zeros(n, dtype=int)
    true_labels[:50] = 1

    model  = IsolationForest(contamination=0.05, random_state=42)
    preds  = (model.fit_predict(X) == -1).astype(int)

    return {
        "precision": round(precision_score(true_labels, preds, zero_division=0), 4),
        "recall":    round(recall_score(true_labels, preds, zero_division=0), 4),
    }


# ── 4. Causal inference bias ──────────────────────────────────────────────

def bench_causal() -> dict:
    rng = np.random.default_rng(0)
    n   = 2_000
    age = rng.normal(35, 8, n)
    edu = rng.normal(12, 3, n)
    p   = 1 / (1 + np.exp(-(0.05 * age + 0.1 * edu - 2.5)))
    T   = rng.binomial(1, p)
    Y   = 30_000 + 500 * edu + 200 * age + 5_000 * T + rng.normal(0, 3_000, n)
    X   = np.column_stack([T, age, edu])
    ate_hat = LinearRegression().fit(X, Y).coef_[0]
    bias    = abs(ate_hat - 5_000)
    return {"OLS_ATE": round(float(ate_hat), 2),
            "bias":    round(float(bias), 2),
            "true_ATE": 5_000}


# ── 5. Data quality score ─────────────────────────────────────────────────

def bench_data_quality() -> dict:
    df = make_sales_df(n_rows=2_000)
    checks = {
        "no_null_revenue":   df["revenue"].isna().sum() == 0,
        "positive_units":    (df["units"] > 0).all(),
        "discount_range":    df["discount"].between(0, 1).all(),
        "positive_price":    (df["price"] > 0).all(),
        "date_not_null":     df["date"].isna().sum() == 0,
    }
    score = sum(checks.values()) / len(checks)
    return {"quality_score": round(score, 4), "checks": checks}


# ── 6. NL2SQL template coverage ───────────────────────────────────────────

def bench_nl2sql() -> dict:
    templates = ["total revenue", "revenue by product", "revenue by region",
                 "top product", "average order value"]
    questions = [
        "What is the total revenue?",
        "Show revenue by product",
        "Revenue by region please",
        "Which is the top product?",
        "What is the average order value?",
        "How many products sold today?",      # no template
        "List all customers with >$1000 LTV", # no template
    ]
    matched = sum(1 for q in questions if any(t in q.lower() for t in templates))
    return {"coverage": round(matched / len(questions), 4),
            "matched": matched, "total": len(questions)}


# ── Consolidated report ───────────────────────────────────────────────────

def print_summary(results: dict) -> None:
    table = Table(title="Analytical AI — Benchmark Results", header_style="bold cyan")
    table.add_column("Benchmark")
    table.add_column("Metric")
    table.add_column("Value")

    rows = [
        ("Pipeline",        "rows/sec",              results["pipeline"]["rows_per_sec"]),
        ("Clustering",      "silhouette",             results["clustering"]["silhouette"]),
        ("Clustering",      "Davies-Bouldin",         results["clustering"]["davies_bouldin"]),
        ("Anomaly Det.",    "precision@5%",           results["anomaly"]["precision"]),
        ("Anomaly Det.",    "recall@5%",              results["anomaly"]["recall"]),
        ("Causal (OLS)",    "ATE bias ($)",           results["causal"]["bias"]),
        ("Data Quality",    "quality score",          results["data_quality"]["quality_score"]),
        ("NL2SQL",          "template coverage",      results["nl2sql"]["coverage"]),
    ]
    for bench, metric, value in rows:
        table.add_row(bench, metric, str(value))
    console.print(table)


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 5 — Full Benchmark Suite")

    results = {
        "pipeline":     bench_pipeline(),
        "clustering":   bench_clustering(),
        "anomaly":      bench_anomaly(),
        "causal":       bench_causal(),
        "data_quality": bench_data_quality(),
        "nl2sql":       bench_nl2sql(),
    }

    print_summary(results)
    save_results(results, "full_benchmark_report.json")
    console.print("\n[green]✓ All benchmarks complete.[/green]")
