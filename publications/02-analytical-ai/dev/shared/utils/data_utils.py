"""
shared/utils/data_utils.py
──────────────────────────
Lightweight helpers used across all phases of the Analytical AI dev workspace.
No API keys required.
"""

from __future__ import annotations

import os
import json
import pathlib
import textwrap
from typing import Any

import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

# ── Directory helpers ──────────────────────────────────────────────────────

ROOT = pathlib.Path(__file__).resolve().parents[2]   # dev/
DATA_DIR = ROOT.parent / "data"
RESULTS_DIR = ROOT / "phase-5-experiments" / "01-benchmark-results"


def ensure_dir(path: pathlib.Path | str) -> pathlib.Path:
    p = pathlib.Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── Synthetic dataset generators ─────────────────────────────────────────

def make_sales_df(n_rows: int = 2_000, seed: int = 42) -> pd.DataFrame:
    """Synthetic e-commerce sales dataset used by Phase 1 and Phase 2 examples."""
    rng = np.random.default_rng(seed)
    products = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard"]
    regions  = ["North", "South", "East", "West", "Central"]

    df = pd.DataFrame({
        "date":     pd.date_range("2023-01-01", periods=n_rows, freq="h"),
        "product":  rng.choice(products, n_rows),
        "region":   rng.choice(regions, n_rows),
        "units":    rng.integers(1, 20, n_rows),
        "price":    rng.uniform(50, 2000, n_rows).round(2),
        "discount": rng.uniform(0, 0.30, n_rows).round(3),
    })
    df["revenue"] = (df["price"] * df["units"] * (1 - df["discount"])).round(2)
    return df


def make_customer_df(n_rows: int = 500, seed: int = 7) -> pd.DataFrame:
    """Synthetic customer feature dataset for clustering examples."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "recency_days":      rng.integers(1, 365, n_rows),
        "frequency":         rng.integers(1, 50, n_rows),
        "monetary":          rng.exponential(500, n_rows).round(2),
        "support_tickets":   rng.integers(0, 10, n_rows),
        "nps_score":         rng.integers(-10, 11, n_rows),
    })
    return df


def make_time_series(n_points: int = 365, seed: int = 0) -> pd.Series:
    """Synthetic daily revenue time series with a planted change-point at day 200."""
    rng = np.random.default_rng(seed)
    base = np.linspace(1000, 1500, n_points)
    noise = rng.normal(0, 80, n_points)
    spike = np.zeros(n_points)
    spike[200:] += 400           # planted structural break
    series = pd.Series(
        base + noise + spike,
        index=pd.date_range("2023-01-01", periods=n_points, freq="D"),
        name="daily_revenue",
    )
    return series


# ── Pretty-print helpers ──────────────────────────────────────────────────

def print_df(df: pd.DataFrame, title: str = "", max_rows: int = 10) -> None:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for col in df.columns:
        table.add_column(str(col), overflow="fold")
    for _, row in df.head(max_rows).iterrows():
        table.add_row(*[str(v) for v in row])
    console.print(table)


def print_json(data: Any, title: str = "") -> None:
    if title:
        console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print_json(json.dumps(data, indent=2, default=str))


def save_results(data: Any, filename: str) -> pathlib.Path:
    ensure_dir(RESULTS_DIR)
    path = RESULTS_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    console.print(f"[green]Results saved → {path}[/green]")
    return path
