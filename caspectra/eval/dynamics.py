"""Label-free *dynamical* features per rule — the physics baseline.

Motivation (SELF_CRITICISM.md Level 5; EVALUATION_CRITERIA.md criterion 3): a
static texture encoder has no notion of computation, but the order/chaos axis
has canonical label-free estimators. The central one is **damage spreading**
(difference-pattern propagation): flip one cell of the initial condition,
evolve both copies, and watch the damage cone.

* class 1/2 (uniform/periodic): the damage dies out or stays bounded;
* class 3 (chaotic): the damage spreads ballistically (≈ light speed) and
  fills its cone densely;
* class 4 (complex): the damage *persists* but propagates along localized
  structures — slower and much sparser than chaos.

These are **rule-level** features (they require running the simulator, not just
looking at one diagram). They serve two purposes: (a) a baseline the SSL
embedding must beat on class-IV recall — if clustering on these few scalars
finds class IV better than the learned embedding, the deep pipeline is not
earning its keep; (b) a label-free auxiliary target for v2 training.

The evolution horizon is capped at ``width // 2 − 1`` steps so the light cone
of a single flipped cell cannot wrap around the periodic boundary; extent
measurements therefore never self-interfere.
"""

from __future__ import annotations

import numpy as np

from caspectra.ca.eca import ECASimulator

__all__ = ["DYNAMICS_FEATURE_NAMES", "damage_spreading_features", "dynamics_feature_matrix"]

DYNAMICS_FEATURE_NAMES = [
    "damage_survival",  # P(damage still alive at the horizon)
    "damage_fraction",  # E[damaged fraction of the ring at the horizon | survived]
    "spreading_rate",  # E[cone extent / (2·t) at the horizon | survived]; 1 = light speed
    "cone_fill",  # E[damaged cells / cone extent | survived]; dense = chaos, sparse = gliders
]


def damage_spreading_features(
    rule: int | None = None,
    *,
    width: int = 127,
    n_pairs: int = 32,
    ic_density: float = 0.5,
    rng: np.random.Generator | None = None,
    simulator: object | None = None,
) -> np.ndarray:
    """Average damage-spreading statistics for one system over ``n_pairs`` ICs.

    Returns a vector aligned with :data:`DYNAMICS_FEATURE_NAMES`. Conditional
    features (fraction/rate/fill) are 0 when no damage survives, which is itself
    the informative signature of ordered rules.

    ``ic_density`` (Bernoulli parameter of the random IC) and ``width`` are part
    of the **observation protocol** the features are conditioned on — the class
    of a rule is only defined relative to that protocol (FOUNDATIONS.md §1).
    ``scripts/protocol_sensitivity.py`` sweeps them.

    ``simulator`` (criterion 8): any object with ``ECASimulator``'s ``evolve``
    surface — e.g. :class:`caspectra.ca.nuca.NonUniformCA` — measured under the
    *identical* twin-run protocol, so composed-system ("alloy") invariants are
    directly comparable to the pure-rule cache. Exactly one of ``rule`` /
    ``simulator`` must be given; with the same ``rng`` a ``(r, r)`` composed
    simulator reproduces the pure rule ``r`` bit-for-bit (the standing control
    in ``scripts/validate_stripes.py``).
    """
    if (rule is None) == (simulator is None):
        raise ValueError("pass exactly one of rule= or simulator=")
    rng = rng or np.random.default_rng(0)
    sim = ECASimulator(rule) if simulator is None else simulator
    sim_width = getattr(sim, "width", None)
    if sim_width is not None and sim_width != width:
        raise ValueError(f"simulator width {sim_width} != requested width {width}")
    n_steps = width // 2 - 1  # keep the light cone from wrapping (see module docstring)

    survived, fractions, rates, fills = [], [], [], []
    for _ in range(n_pairs):
        ic = (rng.random(width) < ic_density).astype(np.uint8)
        flip_at = int(rng.integers(width))
        ic_flipped = ic.copy()
        ic_flipped[flip_at] ^= 1

        a = sim.evolve(ic, n_steps)
        b = sim.evolve(ic_flipped, n_steps)
        damage = a[-1] != b[-1]
        alive = bool(damage.any())
        survived.append(alive)
        if not alive:
            continue

        fractions.append(float(damage.mean()))
        # Cone extent: positions re-centred on the flipped cell; no wrap by construction.
        pos = (np.flatnonzero(damage) - flip_at + width // 2) % width
        extent = int(pos.max() - pos.min()) + 1
        rates.append(float(extent / (2.0 * n_steps)))
        fills.append(float(damage.sum() / extent))

    def _mean(xs: list[float]) -> float:
        return float(np.mean(xs)) if xs else 0.0

    return np.array(
        [float(np.mean(survived)), _mean(fractions), _mean(rates), _mean(fills)],
        dtype=np.float64,
    )


def dynamics_feature_matrix(
    rules: list[int] | np.ndarray,
    *,
    width: int = 127,
    n_pairs: int = 32,
    ic_density: float = 0.5,
    seed: int = 0,
) -> np.ndarray:
    """Damage-spreading feature matrix, one row per rule.

    A fresh child generator per rule keeps rows independent of the list order.
    """
    root = np.random.default_rng(seed)
    return np.stack(
        [
            damage_spreading_features(
                int(r), width=width, n_pairs=n_pairs, ic_density=ic_density, rng=child
            )
            for r, child in zip(rules, root.spawn(len(rules)))
        ]
    )
