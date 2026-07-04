"""Reliability benchmarks for the damage-response targets (R3; rev-8 C2).

Each cached target is a **single** Monte-Carlo estimate (``n_pairs`` twin runs)
of a rule's latent damage statistic. Drawing ``K`` independent replicates per
rule and fitting a one-way random-effects model
``x_{ik} = mu + a_i + e_{ik}`` (rule effect ``a_i ~ N(0, sigma_a^2)``, MC noise
``e_{ik} ~ N(0, sigma_e^2)``) gives the **reliability of a single measurement**,

    ICC(1) = sigma_a^2 / (sigma_a^2 + sigma_e^2).

The second referee (concern 2) correctly noted that ICC is **not** the right
benchmark for every estimator. Two distinct quantities must be kept apart:

* **Latent-target reliability** ``ICC``: the largest unfitted R^2 a predictor of
  the *noise-free* target mean ``theta`` can score against the noisy cached
  target. This is the ceiling for an estimator that recovers ``theta`` itself.

* **Independent-replicate agreement**: the expected unfitted R^2 of one MC
  estimate predicting an *independent* MC estimate of the same rules. For
  ``Y1 = theta + e1`` and ``Y2 = theta + e2`` with equal, independent noise
  variance, ``R^2 = 1 - 2 sigma_e^2 / (sigma_a^2 + sigma_e^2) = 2*ICC - 1``.
  This is the correct benchmark for the **mechanistic estimator**, which returns
  a *fresh, independent* finite-``n_pairs`` simulation rather than ``theta``.

The old docstring conflated the two (it claimed ICC "equally" bounds the
independent-estimate agreement); it does not. :func:`replicate_agreement`
measures the second quantity empirically from the same ``K`` replicates, so the
mechanistic estimator can be scored against the benchmark it actually targets. A
third, near-noise-free **large-simulation reference** (targets at a much larger
``n_pairs``) is computed by ``scripts/validate_reliability.py`` to show the
mechanistic estimator approaches ``ICC`` as its own MC budget grows.
"""

from __future__ import annotations

import numpy as np

from caspectra.eval.dynamics import DYNAMICS_FEATURE_NAMES, dynamics_feature_matrix

__all__ = [
    "target_replicates",
    "icc_ceilings",
    "replicate_agreement",
    "reliability_benchmarks",
]


def target_replicates(
    rules: list[int] | np.ndarray,
    *,
    n_replicates: int = 20,
    width: int = 127,
    n_pairs: int = 256,
    ic_density: float = 0.5,
    radius: int = 1,
    base_seed: int = 1000,
) -> np.ndarray:
    """``(n_replicates, n_rules, n_features)`` independent MC target estimates.

    Replicate ``k`` uses ``dynamics_feature_matrix(seed=base_seed + k)``, whose
    per-rule RNG is ``SeedSequence([seed, rule, radius])`` — so the replicates are
    mutually independent and independent of the cache seed and the mechanistic
    estimator's own seed offset.
    """
    return np.stack(
        [
            dynamics_feature_matrix(
                list(rules),
                width=width,
                n_pairs=n_pairs,
                ic_density=ic_density,
                seed=base_seed + k,
                radius=radius,
            )
            for k in range(n_replicates)
        ]
    )


def _r2_columns(pred: np.ndarray, truth: np.ndarray) -> float:
    """Unfitted R^2 = 1 - SS_res/SS_tot of ``pred`` against ``truth`` over rules.

    Matches ``caspectra.train.regression_trainer.r2_per_feature`` (the convention
    every method is scored with), returning ``nan`` for a constant target.
    """
    total = float(np.sum((truth - truth.mean()) ** 2))
    if total <= 0:
        return float("nan")
    residual = float(np.sum((truth - pred) ** 2))
    return 1.0 - residual / total


def _icc_from_matrix(x: np.ndarray) -> float:
    """ICC(1) for a single feature's ``(K, N)`` replicate matrix."""
    K, N = x.shape
    if K < 2 or N < 2:
        return float("nan")
    rule_means = x.mean(axis=0)
    grand = x.mean()
    msw = float(np.mean(np.var(x, axis=0, ddof=1)))  # -> sigma_e^2
    msb = float(K * np.sum((rule_means - grand) ** 2) / (N - 1))  # -> K sigma_a^2 + sigma_e^2
    sigma_e2 = msw
    sigma_a2 = max((msb - msw) / K, 0.0)
    denom = sigma_a2 + sigma_e2
    return float(sigma_a2 / denom) if denom > 0 else float("nan")


def _mean_pairwise_agreement(x: np.ndarray) -> float:
    """Mean off-diagonal unfitted R^2 over all ordered replicate pairs.

    ``x`` is ``(K, N)`` for one feature. Vectorised: for replicates ``a`` (as the
    predictor) and ``b`` (as the truth), ``SS_res[a,b] = ss[a] + ss[b] - 2 G[a,b]``
    with ``G = x x^T`` and ``ss[a] = sum_n x[a,n]^2``; ``SS_tot[b]`` depends only on
    ``b``. ``R^2[a,b] = 1 - SS_res[a,b] / SS_tot[b]``; average the off-diagonal.
    """
    K, N = x.shape
    if K < 2 or N < 2:
        return float("nan")
    x = np.ascontiguousarray(x)  # BLAS matmul on a non-contiguous slice warns spuriously
    ss = np.sum(x**2, axis=1)  # (K,)
    gram = x @ x.T  # (K, K)
    ss_res = ss[:, None] + ss[None, :] - 2.0 * gram  # (K, K): pred a vs truth b
    ss_tot = np.sum((x - x.mean(axis=1, keepdims=True)) ** 2, axis=1)  # (K,) over truth b
    with np.errstate(divide="ignore", invalid="ignore"):
        r2 = 1.0 - ss_res / ss_tot[None, :]
    off = ~np.eye(K, dtype=bool)
    vals = r2[off]
    vals = vals[np.isfinite(vals)]
    return float(np.mean(vals)) if vals.size else float("nan")


def icc_ceilings(replicates: np.ndarray) -> dict[str, dict[str, float]]:
    """Per-target latent-target reliability ICC(1) and its noise decomposition.

    ``replicates`` has shape ``(K, N, F)``. Returns, per feature name, the
    ``ceiling_r2`` (= ICC(1), the ceiling for a predictor of the noise-free target
    mean) and the MC-noise / between-rule standard deviations. This is **not** the
    benchmark for the mechanistic estimator (see :func:`replicate_agreement`).
    """
    K, N, F = replicates.shape
    if K < 2 or N < 2:
        raise ValueError("need >= 2 replicates and >= 2 rules for an ICC")
    out: dict[str, dict[str, float]] = {}
    for j, name in enumerate(DYNAMICS_FEATURE_NAMES):
        x = replicates[:, :, j]  # (K, N)
        rule_means = x.mean(axis=0)
        grand = x.mean()
        msw = float(np.mean(np.var(x, axis=0, ddof=1)))
        msb = float(K * np.sum((rule_means - grand) ** 2) / (N - 1))
        sigma_e2 = msw
        sigma_a2 = max((msb - msw) / K, 0.0)
        denom = sigma_a2 + sigma_e2
        icc = float(sigma_a2 / denom) if denom > 0 else float("nan")
        out[name] = {
            "ceiling_r2": round(icc, 4),
            "mc_noise_std": round(float(np.sqrt(sigma_e2)), 4),
            "between_rule_std": round(float(np.sqrt(sigma_a2)), 4),
        }
    return out


def replicate_agreement(replicates: np.ndarray) -> dict[str, dict[str, float]]:
    """Per-target empirical independent-replicate agreement (the 2*ICC-1 benchmark).

    ``replicates`` has shape ``(K, N, F)``. For each feature, returns the mean
    unfitted R^2 over all ordered replicate pairs (``agreement_r2``) — the correct
    ceiling for the mechanistic estimator, which returns a fresh independent MC
    draw at the same ``n_pairs`` — alongside the Gaussian prediction ``2*ICC-1``
    for cross-checking.
    """
    K, N, F = replicates.shape
    if K < 2 or N < 2:
        raise ValueError("need >= 2 replicates and >= 2 rules for an agreement estimate")
    out: dict[str, dict[str, float]] = {}
    for j, name in enumerate(DYNAMICS_FEATURE_NAMES):
        x = replicates[:, :, j]
        agr = _mean_pairwise_agreement(x)
        icc = _icc_from_matrix(x)
        out[name] = {
            "agreement_r2": round(agr, 4),
            "two_icc_minus_one": round(2.0 * icc - 1.0, 4),
        }
    return out


def reliability_benchmarks(
    replicates: np.ndarray,
    *,
    n_boot: int = 2000,
    seed: int = 0,
) -> dict[str, dict[str, float | list[float]]]:
    """Per-target ICC and independent-replicate agreement with rule-bootstrap CIs.

    Resamples **rules** (columns) with replacement ``n_boot`` times to get a 95%
    CI for both the latent-target reliability ICC(1) and the independent-replicate
    agreement. Survival is heteroscedastic/non-Gaussian, so the bootstrap CI (not
    a Gaussian random-effects SE) is the reported uncertainty. Returns, per
    feature: ``icc``, ``icc_ci``, ``agreement_r2``, ``agreement_ci``,
    ``two_icc_minus_one``, ``mc_noise_std``, ``between_rule_std``.
    """
    K, N, F = replicates.shape
    if K < 2 or N < 2:
        raise ValueError("need >= 2 replicates and >= 2 rules")
    rng = np.random.default_rng(seed)
    boot_idx = [rng.integers(0, N, N) for _ in range(n_boot)]
    out: dict[str, dict[str, float | list[float]]] = {}
    for j, name in enumerate(DYNAMICS_FEATURE_NAMES):
        x = replicates[:, :, j]  # (K, N)
        icc = _icc_from_matrix(x)
        agr = _mean_pairwise_agreement(x)
        iccs = np.array([_icc_from_matrix(x[:, idx]) for idx in boot_idx])
        agrs = np.array([_mean_pairwise_agreement(x[:, idx]) for idx in boot_idx])
        iccs = iccs[np.isfinite(iccs)]
        agrs = agrs[np.isfinite(agrs)]
        sigma_e = float(np.sqrt(np.mean(np.var(x, axis=0, ddof=1))))
        rule_means = x.mean(axis=0)
        msb = float(K * np.sum((rule_means - x.mean()) ** 2) / (N - 1))
        sigma_a = float(np.sqrt(max((msb - sigma_e**2) / K, 0.0)))
        out[name] = {
            "icc": round(icc, 4),
            "icc_ci": [
                round(float(np.percentile(iccs, 2.5)), 4),
                round(float(np.percentile(iccs, 97.5)), 4),
            ],
            "agreement_r2": round(agr, 4),
            "agreement_ci": [
                round(float(np.percentile(agrs, 2.5)), 4),
                round(float(np.percentile(agrs, 97.5)), 4),
            ],
            "two_icc_minus_one": round(2.0 * icc - 1.0, 4),
            "mc_noise_std": round(sigma_e, 4),
            "between_rule_std": round(sigma_a, 4),
        }
    return out
