"""
phase-4-nlq-bi-layer/02-data-quality/01_great_expectations.py
──────────────────────────────────────────────────────────────
Paper §8 — Data Quality & Observability

RQ5 finding: Each 1% drop in completeness/accuracy degrades insight
reliability non-linearly. Orgs with <95% quality score have 3× higher
rates of incorrect analytical conclusions.

Demonstrates:
 • Manual expectation suite (no GX context required)
 • Completeness, range, uniqueness, referential integrity checks
 • Data quality score calculation
 • Simulated degradation curve (illustrating non-linear impact)

Run:  python phase-4-nlq-bi-layer/02-data-quality/01_great_expectations.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from utils.data_utils import make_sales_df, ensure_dir

console = Console()
ASSETS = pathlib.Path(__file__).resolve().parents[3] / "assets" / "diagrams"


# ── Expectation suite ─────────────────────────────────────────────────────

def run_expectations(df: pd.DataFrame) -> dict:
    """
    Manual expectation suite — equivalent to Great Expectations checks.
    Returns a results dict with pass/fail per check.
    """
    checks = {}

    # Completeness
    for col in df.columns:
        n_null = df[col].isna().sum()
        checks[f"completeness_{col}"] = {
            "passed": n_null == 0,
            "detail": f"{n_null} nulls in '{col}'",
        }

    # Range checks
    checks["units_positive"]    = {"passed": (df["units"] > 0).all(),
                                    "detail": f"min={df['units'].min()}"}
    checks["discount_range"]    = {"passed": df["discount"].between(0, 1).all(),
                                    "detail": f"range=[{df['discount'].min():.3f},{df['discount'].max():.3f}]"}
    checks["revenue_positive"]  = {"passed": (df["revenue"] > 0).all(),
                                    "detail": f"min={df['revenue'].min():.2f}"}

    # Uniqueness: no duplicate (date, product, region) rows in a keyed warehouse
    n_dupe = df.duplicated(subset=["date", "product", "region"]).sum()
    checks["no_duplicate_keys"] = {"passed": n_dupe == 0,
                                    "detail": f"{n_dupe} duplicates"}

    # Referential integrity
    valid_products = {"Laptop", "Phone", "Tablet", "Monitor", "Keyboard"}
    invalid_prods  = set(df["product"].unique()) - valid_products
    checks["valid_product_codes"] = {"passed": len(invalid_prods) == 0,
                                      "detail": f"unexpected: {invalid_prods or 'none'}"}

    return checks


def print_results(checks: dict) -> float:
    table = Table(title="Data Quality Expectation Results", header_style="bold cyan")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")

    passed = 0
    for name, res in checks.items():
        status = "[green]PASS[/green]" if res["passed"] else "[red]FAIL[/red]"
        table.add_row(name, status, res["detail"])
        passed += int(res["passed"])

    console.print(table)
    score = passed / len(checks)
    console.print(f"\n[bold]Data Quality Score:[/bold] {score:.2%} ({passed}/{len(checks)} checks passed)")
    return score


# ── Non-linear degradation curve (paper §8 insight) ──────────────────────

def plot_degradation_curve() -> None:
    """
    Illustrates RQ5: error rate increases non-linearly as data quality drops
    below 95% (exponential tail).
    """
    quality = np.linspace(0.6, 1.0, 200)
    # Empirical-style: error rate doubles every 5% quality drop below 95%
    error_rate = np.where(quality >= 0.95,
                          0.05 * (1 - quality) / 0.05,
                          0.05 * np.exp(8 * (0.95 - quality)))

    ensure_dir(ASSETS)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(quality * 100, error_rate * 100, color="crimson", lw=2)
    ax.axvline(95, color="orange", linestyle="--", lw=1.5, label="95% threshold")
    ax.fill_between(quality * 100, error_rate * 100,
                    where=(quality < 0.95), alpha=0.15, color="red", label="Danger zone")
    ax.set_xlabel("Data Quality Score (%)")
    ax.set_ylabel("Analytical Error Rate (%)")
    ax.set_title("RQ5 — Non-linear Impact of Data Quality on Insight Reliability")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = ASSETS / "data_quality_degradation.png"
    plt.savefig(out, dpi=120)
    plt.close()
    console.print(f"[green]Saved →[/green] {out}")


# ── Introduce deliberate data quality issues ──────────────────────────────

def inject_issues(df: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(99)
    dirty = df.copy()
    # 2% nulls in revenue
    idx = rng.choice(len(dirty), size=int(0.02 * len(dirty)), replace=False)
    dirty.loc[idx, "revenue"] = np.nan
    # 1% invalid discount
    idx2 = rng.choice(len(dirty), size=int(0.01 * len(dirty)), replace=False)
    dirty.loc[idx2, "discount"] = rng.uniform(1.1, 2.0, len(idx2))
    return dirty


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 4 — Data Quality Checks (Great Expectations style)")

    df_clean = make_sales_df()
    df_dirty = inject_issues(df_clean)

    console.rule("Clean dataset")
    run_expectations(df_clean)

    console.rule("Dataset with injected issues (2% null revenue, 1% bad discount)")
    run_expectations(df_dirty)

    plot_degradation_curve()
    console.print("\n[green]✓ Data quality checks complete.[/green]")
