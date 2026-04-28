"""
phase-2-core-techniques/01-clustering/01_customer_clustering.py
───────────────────────────────────────────────────────────────
Paper §5 — Clustering Algorithms: K-Means, DBSCAN, HDBSCAN

Demonstrates:
 • K-Means (§5.1 — centroid-based)
 • DBSCAN (§5.1 — density-based, noise-tolerant)
 • HDBSCAN (§5.1 — hierarchical density, soft clusters)
 • UMAP 2-D projection for visualisation

Run:  python phase-2-core-techniques/01-clustering/01_customer_clustering.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
import hdbscan
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from utils.data_utils import make_customer_df, print_df, ensure_dir
from rich.console import Console

console = Console()
ASSETS = pathlib.Path(__file__).resolve().parents[3] / "assets" / "diagrams"


def load_and_scale() -> tuple[pd.DataFrame, np.ndarray]:
    df = make_customer_df(n_rows=500)
    scaler = StandardScaler()
    X = scaler.fit_transform(df)
    console.print(f"[cyan]Dataset:[/cyan] {X.shape[0]} customers × {X.shape[1]} features")
    return df, X


def run_kmeans(X: np.ndarray, k: int = 4) -> np.ndarray:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    inertia = km.inertia_
    console.print(f"[cyan]K-Means[/cyan] k={k}: inertia={inertia:,.1f}, "
                  f"cluster sizes={np.bincount(labels)}")
    return labels


def run_dbscan(X: np.ndarray, eps: float = 0.8, min_samples: int = 10) -> np.ndarray:
    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(X)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise    = (labels == -1).sum()
    console.print(f"[cyan]DBSCAN[/cyan] eps={eps}: {n_clusters} clusters, {n_noise} noise points")
    return labels


def run_hdbscan(X: np.ndarray, min_cluster_size: int = 20) -> np.ndarray:
    hdb = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)
    labels = hdb.fit_predict(X)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise    = (labels == -1).sum()
    console.print(f"[cyan]HDBSCAN[/cyan] min_size={min_cluster_size}: "
                  f"{n_clusters} clusters, {n_noise} soft-noise")
    return labels


def umap_plot(X: np.ndarray, labels: np.ndarray, title: str, fname: str) -> None:
    """Project to 2-D with UMAP and colour by cluster label."""
    try:
        import umap
        reducer = umap.UMAP(n_components=2, random_state=42)
        emb = reducer.fit_transform(X)
    except ImportError:
        # Fallback: PCA projection
        from sklearn.decomposition import PCA
        emb = PCA(n_components=2, random_state=42).fit_transform(X)
        console.print("[yellow]UMAP not installed — using PCA fallback[/yellow]")

    ensure_dir(ASSETS)
    fig, ax = plt.subplots(figsize=(7, 5))
    unique = sorted(set(labels))
    cmap = cm.get_cmap("tab10", len(unique))
    for i, lbl in enumerate(unique):
        mask = labels == lbl
        ax.scatter(emb[mask, 0], emb[mask, 1], s=18, alpha=0.6,
                   color=cmap(i), label=f"Cluster {lbl}" if lbl != -1 else "Noise")
    ax.set_title(title)
    ax.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    out = ASSETS / fname
    plt.savefig(out, dpi=120)
    plt.close()
    console.print(f"[green]Saved →[/green] {out}")


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 2 — Customer Clustering")
    df, X = load_and_scale()

    km_labels  = run_kmeans(X)
    db_labels  = run_dbscan(X)
    hdb_labels = run_hdbscan(X)

    umap_plot(X, km_labels,  "K-Means (k=4)",    "kmeans_umap.png")
    umap_plot(X, hdb_labels, "HDBSCAN clusters", "hdbscan_umap.png")

    # Attach best labels back to dataframe
    df["cluster"] = km_labels
    print_df(df.groupby("cluster").mean().round(2).reset_index(), title="Cluster Profiles (K-Means)")
    console.print("\n[green]✓ Clustering complete.[/green]")
