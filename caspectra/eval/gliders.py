"""An independent glider detector (EVALUATION_CRITERIA.md rev 7, R6).

The referee objects (concern 8) that the "complex / glider-supporting" label is
*defined by* the damage signature and then *validated on* the same damage
signature — circular. This module provides an independent criterion via a
**localized-seed / periodic-localization test**, a different observable from the
twin-run damage-from-random-ICs signature.

A rule with a uniform quiescent state (all-0 or all-1 is a fixed point) is seeded
with a small random block on that background on a large ring, and evolved without
wrap. We then ask whether the perturbation (i) *persists*, (ii) propagates
*sub-ballistically* (slower than the light cone — chaos fills the cone, gliders
crawl), and (iii) stays *sparse / localized* within its extent (dense chaos vs.
thin gliders). A rule is ``detector-complex`` iff all three hold. Thresholds are
calibrated on the famous ECA anchors {54, 110, 106} (complex), {0, 4, 204}
(ordered) and {30, 90, 22} (chaotic) and then frozen — exactly the anchors the
damage signature used, but through a different experiment, so agreement is
non-trivial evidence rather than a tautology.
"""

from __future__ import annotations

import numpy as np

from caspectra.ca.eca import ECASimulator
from caspectra.ca.range_ca import RangeCA

__all__ = ["GLIDER_SIGNATURE", "quiescent_background", "localized_seed_metrics", "is_glider"]

# Frozen thresholds (calibrated on the ECA anchors; see module docstring).
GLIDER_SIGNATURE = {
    "alive_min": 0.5,  # the seed must survive to the horizon
    "growth_min": 0.05,  # ... and actually move (not a frozen blob)
    "growth_max": 0.9,  # ... but sub-ballistically (chaos fills the cone)
    "fill_max": 0.75,  # ... in a not-fully-dense structure
}
# Known limitation, disclosed rather than tuned away: rules whose *ether* (a
# periodic domain, not chaos) advances at the light speed — e.g. ECA 54 — are
# false negatives of this single-envelope test, because the envelope growth hits
# 1 even though gliders live inside the ether. Reported in the FP/FN accounting.


def _table(rule: int, radius: int) -> np.ndarray:
    size = 1 << (2 * radius + 1)
    return np.array([(rule >> i) & 1 for i in range(size)], dtype=np.uint8)


def quiescent_background(rule: int, radius: int) -> int | None:
    """The uniform fixed-point background (0 or 1), or ``None`` if neither is."""
    table = _table(rule, radius)
    if table[0] == 0:
        return 0
    if table[-1] == 1:
        return 1
    return None


def _simulator(rule: int, radius: int):
    return ECASimulator(rule) if radius == 1 else RangeCA(rule, radius)


def localized_seed_metrics(
    rule: int,
    radius: int = 1,
    *,
    width: int = 255,
    n_steps: int | None = None,
    n_seeds: int = 24,
    seed_width: int = 5,
    rng: np.random.Generator | None = None,
) -> dict[str, float | None]:
    """Persistence / growth / fill of a localized seed on the quiescent background.

    Returns ``alive`` (fraction of seeds whose perturbation survives to the
    horizon), and, conditional on survival, the median normalised ``growth`` (cone
    extent / light-cone extent; 1 = light speed) and median ``fill`` (occupied
    fraction of the structure's extent). ``background`` is the quiescent state or
    ``None`` (in which case the test does not apply).
    """
    rng = rng or np.random.default_rng(0)
    background = quiescent_background(rule, radius)
    if background is None:
        return {"background": None, "alive": None, "growth": None, "fill": None}

    max_speed = radius
    # Long horizon, but the cone of a central seed must not wrap the ring.
    n_steps = n_steps or (width // (2 * max_speed) - 1)
    sim = _simulator(rule, radius)
    centre = width // 2

    alive, growths, fills = [], [], []
    for _ in range(n_seeds):
        row = np.full(width, background, dtype=np.uint8)
        block = slice(centre - seed_width // 2, centre + seed_width // 2 + 1)
        seed_bits = rng.integers(0, 2, size=seed_width, dtype=np.uint8)
        if not np.any(seed_bits != background):
            seed_bits[0] = 1 - background  # ensure a genuine perturbation
        row[block] = seed_bits

        final = sim.evolve(row, n_steps)[-1]
        defect = np.flatnonzero(final != background)
        survived = defect.size > 0
        alive.append(survived)
        if not survived:
            continue
        extent = int(defect.max() - defect.min()) + 1
        growths.append(extent / (2.0 * max_speed * n_steps))
        fills.append(defect.size / extent)

    return {
        "background": int(background),
        "alive": float(np.mean(alive)),
        "growth": float(np.median(growths)) if growths else 0.0,
        "fill": float(np.median(fills)) if fills else 0.0,
    }


def is_glider(metrics: dict, signature: dict | None = None) -> bool | None:
    """Whether the localized-seed metrics match the glider signature.

    ``None`` when the test does not apply (no quiescent background).
    """
    sig = signature or GLIDER_SIGNATURE
    if metrics.get("background") is None or metrics.get("alive") is None:
        return None
    return bool(
        metrics["alive"] >= sig["alive_min"]
        and sig["growth_min"] <= metrics["growth"] <= sig["growth_max"]
        and metrics["fill"] <= sig["fill_max"]
    )
