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
    surface — e.g. :class:`caspectra.ca.nuca.NonUniformCA` or
    :class:`caspectra.ca.range_ca.RangeCA` (M4) — measured under the *identical*
    twin-run protocol, so composed-system ("alloy") and larger-neighbourhood
    invariants are directly comparable to the pure-rule cache. Exactly one of
    ``rule`` / ``simulator`` must be given; with the same ``rng`` a ``(r, r)``
    composed simulator reproduces the pure rule ``r`` bit-for-bit (the standing
    control in ``scripts/validate_stripes.py``). A simulator may expose
    ``max_speed`` (the light-cone speed, = neighbourhood radius); it defaults to
    1 (ECA), and both the horizon and the rate normalization scale with it so
    the four features keep their meaning across radii.
    """
    if (rule is None) == (simulator is None):
        raise ValueError("pass exactly one of rule= or simulator=")
    rng = rng or np.random.default_rng(0)
    sim = ECASimulator(rule) if simulator is None else simulator
    sim_width = getattr(sim, "width", None)
    if sim_width is not None and sim_width != width:
        raise ValueError(f"simulator width {sim_width} != requested width {width}")
    # Light-cone speed is one cell per step for ECAs, ``radius`` for range-r CAs
    # (M4). Cap the horizon so the cone of a single flipped cell cannot wrap the
    # ring, and normalize the spreading rate by that speed so "1 = light speed"
    # holds for any radius. radius=1 reproduces the ECA formulas exactly.
    max_speed = int(getattr(sim, "max_speed", 1))
    n_steps = width // (2 * max_speed) - 1
    if n_steps < 1:
        raise ValueError(f"width {width} too small for radius {max_speed}: horizon < 1 step")

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
        rates.append(float(extent / (2.0 * max_speed * n_steps)))
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
    radius: int = 1,
) -> np.ndarray:
    """Damage-spreading feature matrix, one row per rule.

    Each rule is assigned an RNG keyed on its **identity** — a
    ``SeedSequence([seed, rule, radius])`` — so its row is independent of the
    rule's position in the list *and* of which other rules share the list. The
    damage target of a rule is therefore a well-defined function of ``(rule,
    protocol)`` alone, not of the panel it happened to be computed in.

    (Revisions through 2026-07-04 spawned child generators by list *position*
    instead, which coupled a rule's value to the set it was measured in. S3 in
    ``EVALUATION_CRITERIA.md`` rev 6 measured that coupling at up to ≈0.05–0.08
    for borderline-survival rules — pure resampling noise, but set-dependent.
    Identity seeding removes it exactly, and mirrors the per-alloy seeding
    already used by ``load_or_compute_alloy_targets``.)

    ``radius`` selects the rule space: 1 (default) uses ``ECASimulator``; 2+
    uses :class:`caspectra.ca.range_ca.RangeCA` (M4 larger space), with the
    horizon and rate normalization scaled by the radius so the four features
    keep their meaning.
    """

    def _rng(rule: int) -> np.random.Generator:
        return np.random.default_rng(np.random.SeedSequence([int(seed), int(rule), int(radius)]))

    if radius == 1:
        return np.stack(
            [
                damage_spreading_features(
                    int(r), width=width, n_pairs=n_pairs, ic_density=ic_density, rng=_rng(r)
                )
                for r in rules
            ]
        )
    from caspectra.ca.range_ca import RangeCA

    return np.stack(
        [
            damage_spreading_features(
                simulator=RangeCA(int(r), radius),
                width=width,
                n_pairs=n_pairs,
                ic_density=ic_density,
                rng=_rng(r),
            )
            for r in rules
        ]
    )
