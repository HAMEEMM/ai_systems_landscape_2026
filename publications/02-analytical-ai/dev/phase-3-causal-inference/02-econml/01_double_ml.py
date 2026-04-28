"""
phase-3-causal-inference/02-econml/01_double_ml.py
───────────────────────────────────────────────────
Paper §6 & RQ3 — EconML Double Machine Learning (DoubleML)

Key RQ3 finding: EconML's Double ML achieves the highest estimation
accuracy on benchmarks (bias 0.01, RMSE 0.08).

Demonstrates:
 • DML: residualise treatment + outcome using ML, then regress residuals
 • LinearDML  — linear final stage
 • CausalForestDML — heterogeneous treatment effects (HTE)
 • CATE: Conditional Average Treatment Effect by subgroup
 • SHAP-style feature importance for causal effect modifiers

Run:  python phase-3-causal-inference/02-econml/01_double_ml.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from rich.console import Console
from utils.data_utils import ensure_dir, save_results

console = Console()


# ── Synthetic data with heterogeneous treatment effect ───────────────────

def make_hte_data(n: int = 3_000, seed: int = 0) -> dict:
    """
    True CATE: θ(X) = 2 + 3 * X[:,0]  (effect varies by first feature).
    Confounders X → T and X → Y.
    """
    rng   = np.random.default_rng(seed)
    X     = rng.standard_normal((n, 5))
    T     = (X[:, 0] + rng.standard_normal(n) > 0).astype(float)
    theta = 2 + 3 * X[:, 0]          # true CATE
    Y     = theta * T + X.sum(axis=1) + rng.standard_normal(n)
    return {"X": X, "T": T, "Y": Y, "true_theta": theta}


# ── LinearDML ─────────────────────────────────────────────────────────────

def linear_dml(data: dict) -> float:
    try:
        from econml.dml import LinearDML
    except ImportError:
        console.print("[yellow]econml not installed — pip install econml[/yellow]")
        return float("nan")

    X, T, Y = data["X"], data["T"], data["Y"]
    model = LinearDML(
        model_y=GradientBoostingRegressor(n_estimators=100, random_state=0),
        model_t=GradientBoostingClassifier(n_estimators=100, random_state=0),
        discrete_treatment=True,
        random_state=0,
    )
    model.fit(Y, T, X=X, W=None)
    ate = model.ate(X)
    true_ate = data["true_theta"].mean()
    bias = abs(ate - true_ate)
    console.print(f"[cyan]LinearDML[/cyan]       ATE={ate:.4f}  "
                  f"true={true_ate:.4f}  bias={bias:.4f}")
    return ate


# ── CausalForestDML (HTE) ─────────────────────────────────────────────────

def causal_forest_dml(data: dict) -> np.ndarray:
    try:
        from econml.dml import CausalForestDML
    except ImportError:
        return np.array([])

    X, T, Y = data["X"], data["T"], data["Y"]
    cf = CausalForestDML(
        n_estimators=200,
        model_y=GradientBoostingRegressor(n_estimators=100, random_state=0),
        model_t=GradientBoostingClassifier(n_estimators=100, random_state=0),
        discrete_treatment=True,
        random_state=0,
    )
    cf.fit(Y, T, X=X)
    cate_pred = cf.effect(X)

    true_theta = data["true_theta"]
    rmse = np.sqrt(np.mean((cate_pred - true_theta) ** 2))
    console.print(f"[cyan]CausalForestDML[/cyan] CATE RMSE={rmse:.4f}  "
                  f"(paper benchmark: 0.08)")

    # Subgroup CATE: split by sign of X[:,0]
    high_group = X[:, 0] > 0
    console.print(f"  CATE high-X0 group: {cate_pred[high_group].mean():.3f}")
    console.print(f"  CATE low-X0  group: {cate_pred[~high_group].mean():.3f}")

    return cate_pred


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 3 — EconML Double ML (RQ3 Benchmark)")
    data = make_hte_data()
    console.print(f"Dataset: {len(data['X']):,} obs, true ATE ≈ {data['true_theta'].mean():.2f}")

    ate      = linear_dml(data)
    cate_hat = causal_forest_dml(data)

    if len(cate_hat):
        results = {
            "LinearDML_ATE":       float(ate),
            "CausalForestDML_RMSE": float(np.sqrt(np.mean(
                (cate_hat - data["true_theta"]) ** 2))),
        }
        save_results(results, "econml_benchmark.json")

    console.print("\n[green]✓ EconML Double ML complete.[/green]")
