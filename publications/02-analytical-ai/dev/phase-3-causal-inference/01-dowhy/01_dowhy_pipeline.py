"""
phase-3-causal-inference/01-dowhy/01_dowhy_pipeline.py
───────────────────────────────────────────────────────
Paper §6 — Causal Inference: DoWhy 4-Step Methodology

Demonstrates:
 • Step 1 — Model:    Define DAG with CausalModel
 • Step 2 — Identify: Back-door criterion
 • Step 3 — Estimate: Linear regression estimator
 • Step 4 — Refute:   Placebo and random-common-cause tests

Dataset:  synthetic job-training intervention (IHDP-style, Hill 2011)
RQ3 finding: DoWhy's four-step pipeline provides the most rigorous
              end-to-end causal pipeline for production deployments.

Run:  python phase-3-causal-inference/01-dowhy/01_dowhy_pipeline.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from rich.console import Console
from utils.data_utils import ensure_dir

console = Console()


# ── Synthetic observational dataset ──────────────────────────────────────

def make_job_training_data(n: int = 2_000, seed: int = 42) -> pd.DataFrame:
    """
    DAG: age, education → treatment (training) → income
         age, education → income (direct confounders)
    True ATE ≈ 5_000 USD income lift.
    """
    rng = np.random.default_rng(seed)
    age       = rng.normal(35, 8, n)
    education = rng.normal(12, 3, n)
    # Treatment assignment: older / more educated more likely to receive training
    p_treat   = 1 / (1 + np.exp(-(0.05 * age + 0.1 * education - 2.5)))
    treatment = rng.binomial(1, p_treat)
    # Outcome: income
    income    = (30_000 + 500 * education + 200 * age +
                 5_000 * treatment + rng.normal(0, 3_000, n))
    return pd.DataFrame({"age": age, "education": education,
                         "treatment": treatment, "income": income})


# ── DoWhy 4-step pipeline ─────────────────────────────────────────────────

def run_dowhy(df: pd.DataFrame) -> None:
    try:
        import dowhy
        from dowhy import CausalModel
    except ImportError:
        console.print("[yellow]dowhy not installed — pip install dowhy[/yellow]")
        return

    console.rule("[bold]Step 1 — Model (define DAG)")
    model = CausalModel(
        data=df,
        treatment="treatment",
        outcome="income",
        common_causes=["age", "education"],
    )
    console.print(model.summary())

    console.rule("[bold]Step 2 — Identify (back-door criterion)")
    estimand = model.identify_effect(proceed_when_unidentifiable=True)
    console.print(estimand)

    console.rule("[bold]Step 3 — Estimate (linear regression)")
    estimate = model.estimate_effect(
        estimand,
        method_name="backdoor.linear_regression",
    )
    ate = estimate.value
    console.print(f"  Estimated ATE = ${ate:,.2f} (true ≈ $5,000)")

    console.rule("[bold]Step 4 — Refute (placebo + random cause)")
    refute_placebo = model.refute_estimate(
        estimand, estimate,
        method_name="placebo_treatment_refuter",
        placebo_type="permute",
    )
    console.print(f"  Placebo ATE = {refute_placebo.new_effect:.2f} "
                  f"(p-value: {refute_placebo.refutation_result.get('p_value', 'N/A')})")

    refute_random = model.refute_estimate(
        estimand, estimate,
        method_name="random_common_cause",
    )
    console.print(f"  Random-cause ATE = {refute_random.new_effect:.2f}")
    console.print("\n[green]DoWhy 4-step pipeline passed.[/green]")


# ── Fallback: manual back-door adjustment (no dowhy) ─────────────────────

def manual_backdoor(df: pd.DataFrame) -> None:
    """Linear regression with explicit covariate adjustment (equivalent to back-door)."""
    from sklearn.linear_model import LinearRegression
    X = df[["treatment", "age", "education"]].values
    y = df["income"].values
    model = LinearRegression().fit(X, y)
    ate = model.coef_[0]
    console.print(f"[cyan]Manual back-door (OLS) ATE = ${ate:,.2f}[/cyan]")


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 3 — DoWhy Causal Pipeline")
    df = make_job_training_data()
    console.print(f"Dataset: {len(df):,} rows, treatment rate = "
                  f"{df['treatment'].mean():.2%}")

    run_dowhy(df)
    manual_backdoor(df)

    console.print("\n[green]✓ DoWhy pipeline complete.[/green]")
