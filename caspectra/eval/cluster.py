"""Clustering + the genotype/phenotype diagnostic (BUILD_BRIEF.md §3.7).

Pipeline: extract embeddings -> L2-normalise -> UMAP (cosine metric) -> HDBSCAN
(cluster count emerges; outliers are labelled noise). HDBSCAN is also run
directly on the L2-normalised embeddings as a cross-check, because UMAP can
distort densities.

The scalar **genotype/phenotype diagnostic** is the *excess rule information*
``MI(cluster; rule | LP) = MI(cluster; rule) - MI(cluster; LP)`` — the information
the clusters carry about the *exact rule* beyond the coarse behavioural class. It is
>= 0 by the data-processing inequality and we want it **near zero** (clusters track
behaviour, not the rule). It complements the rule-identity probe and the rule-vs-class
probe *gap*.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import umap
from hdbscan import HDBSCAN
from sklearn.metrics import (
    adjusted_rand_score,
    mutual_info_score,
    normalized_mutual_info_score,
)

from caspectra.eval.labels import RuleLabels

__all__ = [
    "l2_normalize",
    "umap_project",
    "hdbscan_labels",
    "purity",
    "contingency_table",
    "cluster_metrics",
    "mutual_information",
    "genotype_phenotype_diagnostic",
    "cluster_pipeline",
    "cluster_count_stability",
    "ClusterReport",
]

# Known reference class counts (for "discovered vs known" reporting).
N_LP_CLASSES = 5
N_WOLFRAM_CLASSES = 4


def l2_normalize(X: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Row-wise L2 normalisation."""
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.maximum(norms, eps)


def umap_project(
    X: np.ndarray,
    n_components: int = 10,
    metric: str = "cosine",
    n_neighbors: int = 15,
    seed: int = 0,
) -> np.ndarray:
    """Project ``X`` to ``n_components`` dims with UMAP.

    ``n_neighbors`` is clamped below the sample count so small inputs (and the
    test suite) do not error.
    """
    n_neighbors = min(n_neighbors, max(2, X.shape[0] - 1))
    reducer = umap.UMAP(
        n_components=n_components,
        metric=metric,
        n_neighbors=n_neighbors,
        random_state=seed,
    )
    return reducer.fit_transform(X)


def hdbscan_labels(X: np.ndarray, min_cluster_size: int = 15, min_samples: int = 5) -> np.ndarray:
    """HDBSCAN cluster labels (noise = -1)."""
    clusterer = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples)
    return clusterer.fit_predict(X)


def purity(cluster_labels: np.ndarray, class_labels: np.ndarray) -> float:
    """Cluster purity against reference classes (noise counts as a cluster)."""
    total = 0
    for c in np.unique(cluster_labels):
        members = class_labels[cluster_labels == c]
        if members.size:
            _, counts = np.unique(members, return_counts=True)
            total += counts.max()
    return float(total / len(class_labels))


def contingency_table(
    cluster_labels: np.ndarray, class_labels: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(table, cluster_ids, class_ids)`` counts of cluster vs class."""
    clusters = np.unique(cluster_labels)
    classes = np.unique(class_labels)
    table = np.zeros((len(clusters), len(classes)), dtype=np.int64)
    for i, c in enumerate(clusters):
        for j, k in enumerate(classes):
            table[i, j] = np.sum((cluster_labels == c) & (class_labels == k))
    return table, clusters, classes


def cluster_metrics(cluster_labels: np.ndarray, class_labels: np.ndarray) -> dict:
    """ARI, NMI and purity of a clustering against reference classes."""
    return {
        "ari": float(adjusted_rand_score(class_labels, cluster_labels)),
        "nmi": float(normalized_mutual_info_score(class_labels, cluster_labels)),
        "purity": purity(cluster_labels, class_labels),
    }


def mutual_information(a: np.ndarray, b: np.ndarray) -> float:
    """Mutual information (nats) between two label assignments."""
    return float(mutual_info_score(a, b))


def genotype_phenotype_diagnostic(
    cluster_labels: np.ndarray,
    rules: np.ndarray,
    lp_labels: np.ndarray | None,
) -> dict:
    """Excess rule information carried by the clusters beyond the LP class.

    The headline number is ``mi_rule_given_lp`` = the conditional mutual
    information ``MI(cluster; rule | LP)``. Because the LP class is a deterministic
    function of the rule, this equals ``MI(cluster; rule) - MI(cluster; LP)`` and is
    **always >= 0** by the data-processing inequality. **We want it near zero:** that
    means the clustering carries no information about the *exact rule* beyond what the
    coarse behavioural class already implies (phenotype, not genotype). A large value
    is genotype leakage — the failure mode.

    (This replaces the earlier "want MI(cluster;rule) low, MI(cluster;LP) high" framing
    from SELF_CRITICISM.md Level 0, which is impossible: MI(cluster;rule) can never be
    below MI(cluster;LP).)
    """
    mi_rule = mutual_information(cluster_labels, rules)
    diag: dict = {"mi_rule": mi_rule, "mi_lp": None, "mi_rule_given_lp": None}
    if lp_labels is not None:
        mask = lp_labels >= 0
        if mask.sum() > 0:
            # MI(cluster;LP) must be measured on the same masked subset as the
            # conditional term, so the subtraction is consistent.
            mi_lp = mutual_information(cluster_labels[mask], lp_labels[mask])
            mi_rule_masked = mutual_information(cluster_labels[mask], rules[mask])
            diag["mi_lp"] = mi_lp
            diag["mi_rule_given_lp"] = max(0.0, mi_rule_masked - mi_lp)
    return diag


@dataclass
class ClusterReport:
    """Results of the clustering pipeline."""

    umap_labels: np.ndarray  # HDBSCAN on the UMAP projection
    direct_labels: np.ndarray  # HDBSCAN on L2-normalised embeddings (cross-check)
    umap_coords: np.ndarray  # the UMAP projection used for clustering
    n_clusters: int
    n_noise: int
    metrics_lp: dict | None = None
    metrics_wolfram: dict | None = None
    mi_rule: float | None = None
    mi_lp: float | None = None
    mi_rule_given_lp: float | None = None  # excess rule info (want ~0)

    def summary(self) -> str:
        lines = [
            f"Discovered clusters: {self.n_clusters} "
            f"(noise points: {self.n_noise}); "
            f"reference: {N_LP_CLASSES} LP, {N_WOLFRAM_CLASSES} Wolfram",
        ]
        if self.metrics_lp is not None:
            m = self.metrics_lp
            lines.append(
                f"vs LP:      ARI={m['ari']:.3f} NMI={m['nmi']:.3f} purity={m['purity']:.3f}"
            )
        if self.metrics_wolfram is not None:
            m = self.metrics_wolfram
            lines.append(
                f"vs Wolfram: ARI={m['ari']:.3f} NMI={m['nmi']:.3f} purity={m['purity']:.3f}"
            )
        if self.mi_rule_given_lp is not None:
            lines.append(
                "Genotype leakage: excess rule info MI(cluster;rule|LP)="
                f"{self.mi_rule_given_lp:.3f} nats (want ~0; large = leakage). "
                f"[MI rule={self.mi_rule:.3f}, LP={self.mi_lp:.3f}]"
            )
        elif self.mi_rule is not None:
            lines.append(
                f"MI(cluster;rule)={self.mi_rule:.3f} nats "
                "(no LP labels -> excess-rule-info diagnostic unavailable)"
            )
        return "\n".join(lines)


def cluster_pipeline(
    embeddings: np.ndarray,
    *,
    umap_components: int = 10,
    umap_metric: str = "cosine",
    min_cluster_size: int = 15,
    min_samples: int = 5,
    seed: int = 0,
    rules: np.ndarray | None = None,
    labels: RuleLabels | None = None,
) -> ClusterReport:
    """Run the full clustering pipeline and assemble a :class:`ClusterReport`.

    If ``rules`` (and optionally ``labels``) are supplied, the report also
    carries cluster-quality metrics and the genotype/phenotype MI diagnostic.
    """
    normed = l2_normalize(embeddings)
    coords = umap_project(normed, umap_components, umap_metric, seed=seed)
    umap_labels = hdbscan_labels(coords, min_cluster_size, min_samples)
    direct_labels = hdbscan_labels(normed, min_cluster_size, min_samples)

    n_clusters = int(len(set(umap_labels.tolist()) - {-1}))
    n_noise = int(np.sum(umap_labels == -1))
    report = ClusterReport(
        umap_labels=umap_labels,
        direct_labels=direct_labels,
        umap_coords=coords,
        n_clusters=n_clusters,
        n_noise=n_noise,
    )

    if rules is not None:
        lp_array = labels.lp_array(rules) if (labels and labels.has_lp) else None
        wolfram_array = labels.wolfram_array(rules) if (labels and labels.has_wolfram) else None
        if lp_array is not None:
            mask = lp_array >= 0
            report.metrics_lp = cluster_metrics(umap_labels[mask], lp_array[mask])
        if wolfram_array is not None:
            mask = wolfram_array >= 0
            report.metrics_wolfram = cluster_metrics(umap_labels[mask], wolfram_array[mask])
        diag = genotype_phenotype_diagnostic(umap_labels, rules, lp_array)
        report.mi_rule = diag["mi_rule"]
        report.mi_lp = diag["mi_lp"]
        report.mi_rule_given_lp = diag["mi_rule_given_lp"]

    return report


def cluster_count_stability(
    embeddings: np.ndarray,
    min_cluster_sizes: list[int],
    *,
    umap_components: int = 10,
    umap_metric: str = "cosine",
    min_samples: int = 5,
    seed: int = 0,
) -> list[tuple[int, int]]:
    """Return ``[(min_cluster_size, n_clusters), ...]`` over a sweep.

    The "discovered cluster count" is *not* an emergent constant — it depends on
    HDBSCAN's ``min_cluster_size`` (SELF_CRITICISM.md v2 roadmap #6). Reporting how
    the count varies over a sweep is more honest than headlining a single number.
    The UMAP projection is computed once and reused for all sizes.
    """
    coords = umap_project(l2_normalize(embeddings), umap_components, umap_metric, seed=seed)
    out: list[tuple[int, int]] = []
    for mcs in min_cluster_sizes:
        labels = hdbscan_labels(coords, mcs, min_samples)
        out.append((mcs, int(len(set(labels.tolist()) - {-1}))))
    return out
