"""Visualisation of the embedding space and clusters (BUILD_BRIEF.md §3.8).

Two outputs:

* a 2-D UMAP scatter rendered three times side-by-side, coloured by (a) rule
  identity, (b) LP class, (c) discovered HDBSCAN cluster;
* per-cluster grids of representative diagrams (those nearest the cluster's
  densest core) for manual inspection.

These functions take already-computed 2-D coordinates / embeddings and do not
run UMAP themselves, so they are fast and side-effect-free apart from writing
PNGs.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

__all__ = ["scatter_three_panel", "save_per_cluster_samples"]


def _scatter(ax, coords: np.ndarray, labels: np.ndarray, title: str) -> None:
    ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap="tab20", s=8, alpha=0.8)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])


def scatter_three_panel(
    coords: np.ndarray,
    rules: np.ndarray,
    lp_labels: np.ndarray | None,
    cluster_labels: np.ndarray,
    path: str | Path,
) -> Path:
    """Save a 3-panel 2-D scatter coloured by rule, LP class, and cluster.

    When ``lp_labels`` is ``None`` (no external table) the middle panel says so.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    _scatter(axes[0], coords, rules, "by rule identity")
    if lp_labels is None:
        axes[1].text(0.5, 0.5, "LP labels\nunavailable", ha="center", va="center")
        axes[1].set_xticks([])
        axes[1].set_yticks([])
        axes[1].set_title("by LP class")
    else:
        _scatter(axes[1], coords, lp_labels, "by LP class")
    _scatter(axes[2], coords, cluster_labels, "by discovered cluster")
    fig.tight_layout()
    out = Path(path)
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def save_per_cluster_samples(
    images: np.ndarray,
    cluster_labels: np.ndarray,
    embeddings: np.ndarray,
    out_dir: str | Path,
    n_per_cluster: int = 16,
) -> list[Path]:
    """Save one grid PNG per (non-noise) cluster of its most-central diagrams.

    For each cluster, the centroid of its members in embedding space is the
    "densest core" proxy; the ``n_per_cluster`` members nearest the centroid are
    rendered in a square grid.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    images = np.asarray(images)
    paths: list[Path] = []

    for cluster in sorted(set(cluster_labels.tolist())):
        if cluster == -1:  # skip noise
            continue
        member_idx = np.where(cluster_labels == cluster)[0]
        centroid = embeddings[member_idx].mean(axis=0)
        distances = np.linalg.norm(embeddings[member_idx] - centroid, axis=1)
        chosen = member_idx[np.argsort(distances)[:n_per_cluster]]
        paths.append(_save_grid(images[chosen], out_dir / f"cluster_{cluster}.png", cluster))
    return paths


def _save_grid(samples: np.ndarray, path: Path, cluster: int) -> Path:
    n = len(samples)
    cols = max(1, int(math.ceil(math.sqrt(n))))
    rows = max(1, int(math.ceil(n / cols)))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.3, rows * 1.3))
    axes = np.atleast_1d(axes).ravel()
    for ax in axes:
        ax.axis("off")
    for ax, img in zip(axes, samples):
        ax.imshow(np.squeeze(img), cmap="binary", interpolation="nearest")
    fig.suptitle(f"cluster {cluster} (n={n})")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path
