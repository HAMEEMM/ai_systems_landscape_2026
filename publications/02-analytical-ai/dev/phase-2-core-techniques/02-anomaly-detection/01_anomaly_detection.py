"""
phase-2-core-techniques/02-anomaly-detection/01_anomaly_detection.py
─────────────────────────────────────────────────────────────────────
Paper §5 — Anomaly Detection: Isolation Forest, HBOS, and t-SNE visualisation

Demonstrates:
 • Isolation Forest (§5.2 — tree-based ensemble)
 • HBOS — Histogram-Based Outlier Score (§5.2 — fast, unsupervised)
 • Ensembling both scores for robust detection
 • t-SNE 2-D projection coloured by anomaly score

Run:  python phase-2-core-techniques/02-anomaly-detection/01_anomaly_detection.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.manifold import TSNE
from pyod.models.hbos import HBOS
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from utils.data_utils import make_customer_df, ensure_dir
from rich.console import Console

console = Console()
ASSETS = pathlib.Path(__file__).resolve().parents[3] / "assets" / "diagrams"


def load_data() -> tuple[pd.DataFrame, np.ndarray]:
    df = make_customer_df(n_rows=500)
    scaler = StandardScaler()
    X = scaler.fit_transform(df)
    return df, X


def isolation_forest(X: np.ndarray, contamination: float = 0.05) -> np.ndarray:
    model = IsolationForest(contamination=contamination, random_state=42)
    labels = model.fit_predict(X)          # -1 = anomaly, 1 = normal
    scores = -model.score_samples(X)       # higher = more anomalous
    n_anom = (labels == -1).sum()
    console.print(f"[cyan]IsolationForest[/cyan] contamination={contamination}: "
                  f"{n_anom} anomalies detected")
    return scores


def hbos_scores(X: np.ndarray, contamination: float = 0.05) -> np.ndarray:
    model = HBOS(contamination=contamination)
    model.fit(X)
    scores = model.decision_scores_       # higher = more anomalous
    n_anom = (model.labels_ == 1).sum()
    console.print(f"[cyan]HBOS[/cyan] contamination={contamination}: "
                  f"{n_anom} anomalies detected")
    return scores


def ensemble_and_plot(X: np.ndarray, if_scores: np.ndarray, hbos_scr: np.ndarray) -> None:
    # Normalise both to [0,1] and average
    def norm(s):
        return (s - s.min()) / (s.max() - s.min() + 1e-9)
    ensemble = (norm(if_scores) + norm(hbos_scr)) / 2

    # t-SNE projection
    tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=300)
    emb  = tsne.fit_transform(X)

    ensure_dir(ASSETS)
    fig, ax = plt.subplots(figsize=(8, 5))
    sc = ax.scatter(emb[:, 0], emb[:, 1], c=ensemble, cmap="YlOrRd", s=20, alpha=0.8)
    plt.colorbar(sc, ax=ax, label="Ensemble Anomaly Score")
    # Mark top-5% anomalies
    threshold = np.percentile(ensemble, 95)
    mask = ensemble >= threshold
    ax.scatter(emb[mask, 0], emb[mask, 1], edgecolors="red", facecolors="none",
               s=60, linewidths=1.2, label="Top-5% anomalies")
    ax.set_title("Anomaly Detection — t-SNE projection (ensemble score)")
    ax.legend()
    plt.tight_layout()
    out = ASSETS / "anomaly_tsne.png"
    plt.savefig(out, dpi=120)
    plt.close()
    console.print(f"[green]Saved →[/green] {out}")


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 2 — Anomaly Detection")
    df, X = load_data()

    if_scores   = isolation_forest(X)
    hbos_scr    = hbos_scores(X)
    ensemble_and_plot(X, if_scores, hbos_scr)

    console.print("\n[green]✓ Anomaly detection complete.[/green]")
