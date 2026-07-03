"""Operational behaviour regimes from damage-spreading invariants (M4).

For the range-2 rule space there are no Li–Packard / Wolfram reference labels,
so "which rules are complex?" must be answered from the invariants themselves —
consistent with the project's committed stance that behaviour is defined by the
protocol-conditioned dynamical invariants, not by a human class label
(FOUNDATIONS.md, CLAUDE.md). This module fixes that operational definition.

The complex signature is a **shape** in invariant space — damage persists,
spreads *sub-ballistically* (well below the light-cone speed), in a *sparse,
localized* cone: gliders, not dense chaos and not order. Because the invariants
are protocol-dependent (the whole finding of criterion 5), the numeric
thresholds instantiating that shape must be calibrated *per protocol*; a fixed
threshold across protocols would be wrong.

Two calibrations are recorded. ``COMPLEX_SIGNATURE_ECA`` (horizon
``width // 2``) recovers exactly ``{54, 106, 110}`` across the 88 ECA orbit
representatives — the provenance that the shape-based method works. The primary
one, ``COMPLEX_SIGNATURE`` (= the range-2 calibration, horizon ``width // 4``),
is what M4 uses: calibrated on the **embedded-ECA anchors** (a fixed, a-priori
named set — the range-2 rules that reproduce the famous ECAs) so that it
includes the class-IV cluster ``{54, 110, 106}``; the additive-adjacent rule 60
also falls in (a known, reported contaminant — the additive confound seen on
ECAs too). On uniformly sampled range-2 rules it flags ≈ 7 % as complex — a
genuinely *populated* regime, versus the two-member ECA club that motivates M4.
The thresholds are **pre-registered** (EVALUATION_CRITERIA.md revision 5,
criterion 9) before any sampled rule is held out.
"""

from __future__ import annotations

import numpy as np

from caspectra.ca.range_ca import embed_eca
from caspectra.eval.dynamics import DYNAMICS_FEATURE_NAMES

__all__ = [
    "COMPLEX_SIGNATURE",
    "COMPLEX_SIGNATURE_ECA",
    "is_complex",
    "complex_mask",
    "curated_anchors",
]

_SURV = DYNAMICS_FEATURE_NAMES.index("damage_survival")
_FRAC = DYNAMICS_FEATURE_NAMES.index("damage_fraction")
_RATE = DYNAMICS_FEATURE_NAMES.index("spreading_rate")
_FILL = DYNAMICS_FEATURE_NAMES.index("cone_fill")

# Pre-registered thresholds (do not edit without an EVALUATION_CRITERIA revision).
# Provenance calibration on ECAs (horizon width//2): selects exactly {54,106,110}.
COMPLEX_SIGNATURE_ECA = {
    "survival_min": 0.5,
    "rate_lo": 0.15,
    "rate_hi": 0.6,
    "fill_max": 0.6,
    "fraction_max": 0.22,
}
# M4 primary calibration on the range-2 protocol (width 127, horizon width//4):
# calibrated on the embedded-ECA anchors to include the class-IV cluster.
COMPLEX_SIGNATURE = {
    "survival_min": 0.85,  # damage persists strongly to the (shorter) horizon
    "rate_lo": 0.15,  # propagates (rules out ordered/frozen)
    "rate_hi": 0.28,  # sub-ballistic (rules out the chaotic/ballistic bulk)
    "fill_max": 0.6,  # sparse cone (gliders leave gaps)
    "fraction_max": 0.15,  # localized structures, not space-filling
}


def is_complex(vector: np.ndarray, signature: dict | None = None) -> bool:
    """Whether one invariant vector matches a complex signature.

    ``signature`` defaults to the M4 range-2 calibration
    (:data:`COMPLEX_SIGNATURE`); pass :data:`COMPLEX_SIGNATURE_ECA` to apply the
    ECA-protocol provenance calibration.
    """
    s = signature or COMPLEX_SIGNATURE
    surv, frac, rate, fill = (
        float(vector[_SURV]),
        float(vector[_FRAC]),
        float(vector[_RATE]),
        float(vector[_FILL]),
    )
    return (
        surv > s["survival_min"]
        and s["rate_lo"] <= rate <= s["rate_hi"]
        and fill < s["fill_max"]
        and frac < s["fraction_max"]
    )


def complex_mask(targets: np.ndarray, signature: dict | None = None) -> np.ndarray:
    """Boolean mask over rows of a ``(n_rules, 4)`` target matrix."""
    targets = np.asarray(targets)
    return np.array([is_complex(row, signature) for row in targets], dtype=bool)


def curated_anchors(radius: int = 2) -> dict[str, int]:
    """Named literature anchors embedded into the range-``radius`` space.

    The famous ECAs embedded as range-2 rules that ignore their outer
    neighbours: they reproduce the ECA dynamics exactly (a continuity control)
    and give interpretable reference points on the range-2 invariant landscape —
    the complex pair {54, 110} plus one exemplar per other regime. Range-2
    *totalistic* class-IV codes may be appended once confirmed against Wolfram's
    tables (tracked separately; not asserted from memory here).
    """
    eca_anchors = {
        "eca0_dead": 0,
        "eca204_fixed": 204,
        "eca184_traffic": 184,
        "eca30_chaotic": 30,
        "eca90_additive": 90,
        "eca54_complex": 54,
        "eca110_complex": 110,
    }
    return {name: embed_eca(rule, radius) for name, rule in eca_anchors.items()}
