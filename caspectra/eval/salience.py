"""Salience diagnostics — is behavioural structure *geometrically dominant*?

Motivation (SELF_CRITICISM.md Level 5; thresholds in EVALUATION_CRITERIA.md):
the first full run showed the failure mode is not missing information but
missing *salience* — complexity was linearly decodable from the embedding, yet
the high-variance directions (and hence UMAP+HDBSCAN) followed density. These
diagnostics quantify that, so success/failure is judged at the geometry/cluster
level rather than by embedding decodability alone.

All functions are NumPy-only so they can run on saved ``embeddings.npz``
artifacts without touching torch.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mutual_info_score, r2_score
from sklearn.model_selection import train_test_split

__all__ = [
    "participation_ratio",
    "per_class_cluster_recall",
    "excess_genotype_fraction",
    "density_invariance_r2",
    "regress_out",
]


def regress_out(embeddings: np.ndarray, covariates: np.ndarray) -> np.ndarray:
    """Return the embedding with the linear span of ``covariates`` removed.

    The v1 salience test (SELF_CRITICISM.md 5.4 #1): density/activity dominate the
    embedding geometry, so we remove their best linear reconstruction (including an
    intercept) and re-cluster the residual. If behavioural structure appears, the
    problem was geometry (salience), not missing content. Linear-only on purpose:
    it matches how the density axis was diagnosed (PC1/linear R²), and a stronger
    nonlinear removal could silently delete behaviour along with the nuisance.
    """
    emb = np.asarray(embeddings, dtype=np.float64)
    cov = np.asarray(covariates, dtype=np.float64)
    if cov.ndim == 1:
        cov = cov[:, None]
    design = np.concatenate([np.ones((len(cov), 1)), cov], axis=1)
    coef, *_ = np.linalg.lstsq(design, emb, rcond=None)
    return emb - design @ coef


def participation_ratio(X: np.ndarray) -> float:
    """Effective dimensionality ``(Σλ)² / Σλ²`` of the embedding covariance.

    λ are the covariance eigenvalues of the (row-wise L2-normalised) embeddings.
    Ranges from 1 (all variance on one axis — e.g. a single density direction,
    or full collapse) to D (isotropic spread). Complements ``collapse_std``:
    std can stay > 0 while the geometry is effectively one-dimensional, which is
    exactly the v1 pathology (PC1 ≈ density).
    """
    X = np.asarray(X, dtype=np.float64)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    X = X / np.maximum(norms, 1e-8)
    Xc = X - X.mean(axis=0, keepdims=True)
    # Eigenvalues via singular values: λ_i = s_i² / (n − 1).
    s = np.linalg.svd(Xc, compute_uv=False)
    lam = s**2
    total = lam.sum()
    if total <= 0:
        return 1.0
    return float(total**2 / np.square(lam).sum())


def per_class_cluster_recall(
    cluster_labels: np.ndarray, class_labels: np.ndarray
) -> dict[int, float]:
    """Fraction of each class's points that land in clusters *owned* by that class.

    A cluster is owned by its majority class; HDBSCAN noise (−1) owns nothing, so
    noise points count against recall. This is EVALUATION_CRITERIA.md criterion 1:
    purity alone rewards the v1 outcome (95 rule-pure clusters), whereas recall of
    a *class* additionally requires the class's diagrams to end up in clusters that
    are behaviourally, not just locally, coherent. Reported per class because the
    interesting classes (Wolfram 4) are rare and vanish from aggregate scores.
    """
    cluster_labels = np.asarray(cluster_labels)
    class_labels = np.asarray(class_labels)
    owner: dict[int, int] = {}
    for c in np.unique(cluster_labels):
        if c == -1:
            continue
        members = class_labels[cluster_labels == c]
        vals, counts = np.unique(members, return_counts=True)
        owner[int(c)] = int(vals[np.argmax(counts)])
    recall: dict[int, float] = {}
    for k in np.unique(class_labels):
        in_class = class_labels == k
        hit = np.array([owner.get(int(c), None) == k for c in cluster_labels[in_class]], dtype=bool)
        recall[int(k)] = float(hit.mean()) if in_class.any() else float("nan")
    return recall


def excess_genotype_fraction(
    cluster_labels: np.ndarray,
    orbits: np.ndarray,
    class_labels: np.ndarray,
) -> dict[str, float]:
    """Normalised excess genotype information: ``MI(cluster; orbit | class) / H(orbit | class)``.

    The numerator is the within-behaviour-class rule information the clustering
    resolves; the denominator is the total resolvable within-class rule
    information, so the ratio is 0 (clusters say nothing about the rule beyond
    its behaviour class — the goal) to 1 (clusters fully identify the rule — the
    v1 outcome). Conditioning is computed properly per class (not by the
    ``MI(cluster;orbit) − MI(cluster;class)`` shortcut) so it stays valid even if
    a future reference labelling is not a deterministic function of the orbit.

    EVALUATION_CRITERIA.md criterion 2: success ≤ 0.25, failure ≥ 0.5.
    """
    cluster_labels = np.asarray(cluster_labels)
    orbits = np.asarray(orbits)
    class_labels = np.asarray(class_labels)
    n = len(class_labels)
    mi_cond = 0.0
    h_cond = 0.0
    for k in np.unique(class_labels):
        m = class_labels == k
        w = m.sum() / n
        if m.sum() < 2:
            continue
        mi_cond += w * float(mutual_info_score(cluster_labels[m], orbits[m]))
        _, counts = np.unique(orbits[m], return_counts=True)
        p = counts / counts.sum()
        h_cond += w * float(-(p * np.log(p)).sum())
    fraction = mi_cond / h_cond if h_cond > 0 else 0.0
    return {
        "mi_cluster_orbit_given_class": mi_cond,
        "h_orbit_given_class": h_cond,
        "excess_genotype_fraction": float(fraction),
    }


def density_invariance_r2(
    embeddings: np.ndarray,
    images: np.ndarray,
    *,
    seed: int = 0,
    test_size: float = 0.3,
) -> dict[str, float]:
    """Held-out R² of ridge regressions embedding → raw and → folded density.

    The encoder is trained with the ``Invert`` augmentation, so it should be
    invariant to 0↔1 complementation — i.e. it may encode the *folded* density
    ``min(d, 1−d)`` but should NOT decode the raw density ``d`` much better than
    the folded one. ``r2_raw ≫ r2_folded``-implied headroom (raw decodable beyond
    what folding explains) is a concrete signal that the invert invariance did
    not take during training. Also reports how density-laden the embedding is at
    all (the v1 salience problem: R² ≈ 0.95).
    """
    imgs = np.asarray(images)
    if imgs.ndim == 4:
        imgs = imgs[:, 0]
    d_raw = imgs.reshape(len(imgs), -1).mean(axis=1).astype(np.float64)
    d_folded = np.minimum(d_raw, 1.0 - d_raw)

    out: dict[str, float] = {}
    for name, target in (("r2_density_raw", d_raw), ("r2_density_folded", d_folded)):
        x_tr, x_te, y_tr, y_te = train_test_split(
            embeddings, target, test_size=test_size, random_state=seed
        )
        model = Ridge(alpha=1.0).fit(x_tr, y_tr)
        out[name] = float(r2_score(y_te, model.predict(x_te)))
    return out
