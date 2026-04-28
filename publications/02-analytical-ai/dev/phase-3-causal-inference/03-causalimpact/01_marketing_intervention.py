"""
phase-3-causal-inference/03-causalimpact/01_marketing_intervention.py
──────────────────────────────────────────────────────────────────────
Paper §6 — CausalImpact: Bayesian Structural Time-Series for Marketing

Key RQ3 finding: CausalImpact is preferred for time-series marketing
interventions due to its Bayesian structural approach.

Demonstrates:
 • Pre/post campaign split
 • CausalImpact Bayesian structural time-series model
 • Inferring absolute and relative lift
 • Fallback: manual pre/post difference-in-differences

Run:  python phase-3-causal-inference/03-causalimpact/01_marketing_intervention.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rich.console import Console
from utils.data_utils import ensure_dir

console = Console()
ASSETS = pathlib.Path(__file__).resolve().parents[3] / "assets" / "diagrams"


# ── Synthetic marketing time-series ──────────────────────────────────────

def make_campaign_data(n_pre: int = 60, n_post: int = 30, seed: int = 1) -> pd.DataFrame:
    """
    Simulate daily conversions before and after a marketing campaign.
    True lift: +25 conversions/day in the post period.
    """
    rng    = np.random.default_rng(seed)
    dates  = pd.date_range("2025-01-01", periods=n_pre + n_post, freq="D")
    trend  = np.linspace(100, 120, n_pre + n_post)
    noise  = rng.normal(0, 8, n_pre + n_post)
    lift   = np.zeros(n_pre + n_post)
    lift[n_pre:] = 25          # planted campaign lift

    # Control series (unaffected by campaign, correlated)
    control = trend * 0.6 + rng.normal(0, 5, n_pre + n_post)

    df = pd.DataFrame({
        "date":        dates,
        "conversions": trend + noise + lift,
        "control":     control,
    }).set_index("date")
    return df


# ── CausalImpact ─────────────────────────────────────────────────────────

def run_causalimpact(df: pd.DataFrame, n_pre: int = 60) -> None:
    try:
        from causalimpact import CausalImpact
    except ImportError:
        console.print("[yellow]causalimpact not installed — pip install causalimpact[/yellow]")
        console.print("[dim]Falling back to manual DiD...[/dim]")
        manual_did(df, n_pre)
        return

    pre_period  = [df.index[0].strftime("%Y-%m-%d"),
                   df.index[n_pre - 1].strftime("%Y-%m-%d")]
    post_period = [df.index[n_pre].strftime("%Y-%m-%d"),
                   df.index[-1].strftime("%Y-%m-%d")]

    ci = CausalImpact(df[["conversions", "control"]], pre_period, post_period)

    summary = ci.summary()
    console.print(summary)

    # Plot
    ensure_dir(ASSETS)
    fig = ci.plot(figsize=(12, 7))
    out = ASSETS / "causalimpact_campaign.png"
    plt.savefig(out, dpi=120, bbox_inches="tight")
    plt.close()
    console.print(f"[green]Saved CausalImpact plot →[/green] {out}")


# ── Manual DiD fallback ───────────────────────────────────────────────────

def manual_did(df: pd.DataFrame, n_pre: int = 60) -> None:
    """Difference-in-Differences: simple pre/post mean comparison."""
    pre_mean  = df["conversions"].iloc[:n_pre].mean()
    post_mean = df["conversions"].iloc[n_pre:].mean()
    ctrl_pre  = df["control"].iloc[:n_pre].mean()
    ctrl_post = df["control"].iloc[n_pre:].mean()

    did = (post_mean - pre_mean) - (ctrl_post - ctrl_pre)
    console.print(f"[cyan]Manual DiD[/cyan] estimated lift = {did:.2f} conv/day (true ≈ 25)")


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 3 — CausalImpact Marketing Intervention")
    N_PRE = 60
    df = make_campaign_data(n_pre=N_PRE)
    console.print(f"Pre: {N_PRE} days | Post: {len(df) - N_PRE} days | "
                  f"True lift: +25 conv/day")

    run_causalimpact(df, n_pre=N_PRE)
    console.print("\n[green]✓ CausalImpact analysis complete.[/green]")
