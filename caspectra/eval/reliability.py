"""Reliability-adjusted R^2 ceilings for the damage-response targets (R3).

EVALUATION_CRITERIA.md rev 7, R3. The referee correctly objects that a
per-feature Monte-Carlo noise *range* does not by itself bound achievable R^2:
the ceiling depends on how that noise compares to the between-rule signal
variance, target by target. We estimate it properly.

Each cached target is a **single** Monte-Carlo estimate (``n_pairs`` twin runs)
of a rule's latent damage statistic. Drawing ``K`` independent replicates per
rule and fitting a one-way random-effects model
``x_{ik} = mu + a_i + e_{ik}`` (rule effect ``a_i ~ N(0, sigma_a^2)``, MC noise
``e_{ik} ~ N(0, sigma_e^2)``) gives the **reliability of a single measurement**,

    ICC(1) = sigma_a^2 / (sigma_a^2 + sigma_e^2),

which is exactly the attenuation bound: the largest R^2 any predictor can score
against the noisy cached target, and equally the expected R^2 between two
independent estimates (the cached target vs. the mechanistic estimator's fresh
simulation). Reported per target so the CNN/baseline shortfall is read against
what is *achievable*, not against 1.0.
"""

from __future__ import annotations

import numpy as np

from caspectra.eval.dynamics import DYNAMICS_FEATURE_NAMES, dynamics_feature_matrix

__all__ = ["target_replicates", "icc_ceilings"]


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


def icc_ceilings(replicates: np.ndarray) -> dict[str, dict[str, float]]:
    """Per-target reliability (ICC(1)) = achievable-R^2 ceiling.

    ``replicates`` has shape ``(K, N, F)``. Returns, per feature name, the
    ceiling ``ICC(1)`` and the MC-noise / between-rule standard deviations that
    produced it (the noise std is the honest replacement for the old
    ``0.006--0.014`` band).
    """
    K, N, F = replicates.shape
    if K < 2 or N < 2:
        raise ValueError("need >= 2 replicates and >= 2 rules for an ICC")
    out: dict[str, dict[str, float]] = {}
    for j, name in enumerate(DYNAMICS_FEATURE_NAMES):
        x = replicates[:, :, j]  # (K, N)
        rule_means = x.mean(axis=0)
        grand = x.mean()
        msw = float(np.mean(np.var(x, axis=0, ddof=1)))  # -> sigma_e^2
        msb = float(K * np.sum((rule_means - grand) ** 2) / (N - 1))  # -> K sigma_a^2 + sigma_e^2
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
