"""
phase-1-foundations/02-statistical-analysis/01_descriptive_inferential.py
──────────────────────────────────────────────────────────────────────────
Paper §3 — Stage 3 (Analyse): Descriptive & Inferential Statistics

Demonstrates:
 • Descriptive statistics: mean, std, skew, kurtosis, IQR
 • Groupby aggregation and pivot analysis
 • A/B test with t-test and Mann-Whitney U
 • Correlation heatmap (saved to assets/)

Run:  python phase-1-foundations/02-statistical-analysis/01_descriptive_inferential.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rich.console import Console
from utils.data_utils import make_sales_df, print_df, ensure_dir

console = Console()
ASSETS = pathlib.Path(__file__).resolve().parents[3] / "assets" / "diagrams"


# ── Descriptive statistics ────────────────────────────────────────────────

def describe_revenue(df: pd.DataFrame) -> None:
    console.rule("[bold]Descriptive Statistics — Revenue")
    r = df["revenue"]
    stats_dict = {
        "n":        len(r),
        "mean":     r.mean(),
        "median":   r.median(),
        "std":      r.std(),
        "skewness": r.skew(),
        "kurtosis": r.kurtosis(),
        "IQR":      r.quantile(0.75) - r.quantile(0.25),
        "p5":       r.quantile(0.05),
        "p95":      r.quantile(0.95),
    }
    for k, v in stats_dict.items():
        console.print(f"  {k:<12} {v:.4f}")


def regional_pivot(df: pd.DataFrame) -> None:
    console.rule("[bold]Regional Revenue Pivot")
    pivot = (
        df.groupby(["region", "product"])["revenue"]
        .sum()
        .unstack(fill_value=0)
        .round(0)
    )
    console.print(pivot.to_string())


# ── A/B Test ─────────────────────────────────────────────────────────────

def ab_test(df: pd.DataFrame) -> None:
    """
    Business question: Does a discount > 15% lead to higher per-transaction revenue?
    H0: no difference in revenue between high-discount and low-discount groups.
    """
    console.rule("[bold]A/B Test — Discount Impact on Revenue")
    high = df.loc[df["discount"] > 0.15, "revenue"]
    low  = df.loc[df["discount"] <= 0.15, "revenue"]

    t_stat, p_ttest = stats.ttest_ind(high, low, equal_var=False)
    u_stat, p_mwu   = stats.mannwhitneyu(high, low, alternative="two-sided")

    console.print(f"  High-discount group (n={len(high):,}): mean = {high.mean():.2f}")
    console.print(f"  Low-discount  group (n={len(low):,}): mean = {low.mean():.2f}")
    console.print(f"  Welch t-test:          t={t_stat:.4f}, p={p_ttest:.4f}")
    console.print(f"  Mann-Whitney U:         U={u_stat:.0f}, p={p_mwu:.4f}")

    alpha = 0.05
    verdict = "REJECT H0" if p_ttest < alpha else "FAIL TO REJECT H0"
    console.print(f"  [bold yellow]Decision (α={alpha}):[/bold yellow] {verdict}")


# ── Correlation heatmap ───────────────────────────────────────────────────

def save_corr_heatmap(df: pd.DataFrame) -> None:
    ensure_dir(ASSETS)
    numeric = df[["units", "price", "discount", "revenue"]]
    corr = numeric.corr()

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    plt.colorbar(im, ax=ax)
    for i in range(len(corr)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("Feature Correlation Matrix")
    plt.tight_layout()
    out = ASSETS / "correlation_heatmap.png"
    plt.savefig(out, dpi=120)
    console.print(f"[green]Saved heatmap →[/green] {out}")
    plt.close()


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = make_sales_df()
    describe_revenue(df)
    regional_pivot(df)
    ab_test(df)
    save_corr_heatmap(df)
    console.print("\n[green]✓ Statistical analysis complete.[/green]")
