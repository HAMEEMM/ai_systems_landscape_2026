"""
phase-2-core-techniques/04-change-point-detection/01_changepoint.py
────────────────────────────────────────────────────────────────────
Paper §5 — Change-Point Detection: PELT (ruptures) & BOCPD

Demonstrates:
 • PELT algorithm — exact, O(n) on piecewise-constant signal
 • BOCPD (Bayesian Online) — real-time posterior over run-length
 • Marketing use-case: detect structural breaks in daily revenue

Run:  python phase-2-core-techniques/04-change-point-detection/01_changepoint.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import numpy as np
import pandas as pd
import ruptures as rpt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rich.console import Console
from utils.data_utils import make_time_series, ensure_dir

console = Console()
ASSETS = pathlib.Path(__file__).resolve().parents[3] / "assets" / "diagrams"


# ── PELT ─────────────────────────────────────────────────────────────────

def pelt_detection(signal: np.ndarray, pen: float = 10.0) -> list[int]:
    algo = rpt.Pelt(model="rbf").fit(signal.reshape(-1, 1))
    breakpoints = algo.predict(pen=pen)
    console.print(f"[cyan]PELT[/cyan] pen={pen}: breakpoints at indices {breakpoints[:-1]}")
    return breakpoints


# ── Simple BOCPD (hazard-rate variant, no external library) ───────────────

def bocpd_simple(signal: np.ndarray, hazard: float = 1/50,
                 mean0: float = 0, var0: float = 1e4,
                 obs_noise: float = 1.0) -> np.ndarray:
    """
    Online Bayesian change-point detection.
    Returns run-length probability P(r_t | x_{1:t}) for each time step.
    Reference: Adams & MacKay (2007).
    """
    n = len(signal)
    R = np.zeros((n + 1, n + 1))
    R[0, 0] = 1.0

    muT  = np.array([mean0])
    varT = np.array([var0])
    maxprob = np.zeros(n)

    for t in range(1, n + 1):
        x = signal[t - 1]

        # Predictive probability (Gaussian)
        pred_mean = muT
        pred_var  = varT + obs_noise
        pred_prob = (1 / np.sqrt(2 * np.pi * pred_var) *
                     np.exp(-0.5 * (x - pred_mean) ** 2 / pred_var))

        # Update run-length distribution
        R[t, 1:t + 1] = R[t - 1, :t] * pred_prob * (1 - hazard)
        R[t, 0]       = np.sum(R[t - 1, :t] * pred_prob) * hazard
        R[t]         /= R[t].sum() + 1e-300

        # Posterior update (conjugate Gaussian-Normal)
        varT  = 1.0 / (1.0 / varT + 1.0 / obs_noise)
        muT   = varT * (pred_mean / varT + x / obs_noise)
        varT  = np.append(var0, varT)
        muT   = np.append(mean0, muT)

        maxprob[t - 1] = R[t, 1:].argmax()    # most likely run-length

    return maxprob


# ── Plotting ─────────────────────────────────────────────────────────────

def plot_changepoints(series: pd.Series, pelt_bps: list[int], bocpd_rl: np.ndarray) -> None:
    ensure_dir(ASSETS)
    signal = series.values
    dates  = series.index

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    # PELT
    ax1.plot(dates, signal, color="steelblue", lw=1, label="Revenue")
    for bp in pelt_bps[:-1]:
        ax1.axvline(dates[bp - 1], color="red", lw=1.5, linestyle="--", alpha=0.8)
    ax1.set_ylabel("Daily Revenue")
    ax1.set_title("PELT Change-Point Detection")
    ax1.legend(fontsize=8)

    # BOCPD run-length
    ax2.plot(dates, bocpd_rl, color="darkorange", lw=1)
    ax2.set_ylabel("Run-Length (BOCPD)")
    ax2.set_title("Bayesian Online CPD — Most-Likely Run-Length")

    plt.tight_layout()
    out = ASSETS / "changepoint_pelt_bocpd.png"
    plt.savefig(out, dpi=120)
    plt.close()
    console.print(f"[green]Saved →[/green] {out}")


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 2 — Change-Point Detection")

    series  = make_time_series(n_points=365)
    signal  = series.values

    pelt_bps = pelt_detection(signal)
    bocpd_rl = bocpd_simple(signal)
    plot_changepoints(series, pelt_bps, bocpd_rl)

    console.print(f"\nPlanted break at day 200 — PELT detected: {pelt_bps[:-1]}")
    console.print("\n[green]✓ Change-point detection complete.[/green]")
