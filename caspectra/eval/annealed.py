"""Annealed (mean-field) damage-response estimator — the zero-budget family member.

The mechanistic estimator (:mod:`caspectra.eval.rule_inference`) reads the rule
table off a diagram and then *simulates* twin runs; its cost is indexed by the
Monte-Carlo pair budget. This module supplies the analytic tier below it: the
same four damage-response statistics (:data:`~caspectra.eval.dynamics.DYNAMICS_FEATURE_NAMES`)
computed **directly from the table**, with no simulation at all — the
Derrida–Pomeau annealed approximation applied to a specific rule table rather
than an ensemble (Derrida & Pomeau 1986; Bagnoli, Rechtman & Ruffo 1992;
Vispoel, Daly & Baetens 2026; see docs/literature/readthrough_2026-07-07_NOTES.md
§3.1 for the derivation and the identity chain ĝ′(0) = (2r+1)·s̄ ⇔ mean-field
λ = log((2r+1)μ) > 0 ⇔ annealed instability).

Model: a defect density ``y`` on an infinite well-mixed lattice maps to
``ĝ(y) = Σ_S y^|S| (1-y)^(n-|S|) d_S`` one step later, where ``d_S`` is the
exact Bernoulli(1/2) probability that flipping the input bits in mask ``S``
changes the output. The four estimates follow:

* ``damage_survival`` — extinction of a Galton–Watson process whose offspring
  are the ``2r+1`` downstream cells, each flipped independently with the
  single-bit sensitivity ``p_k``;
* ``cone_fill`` — the stable fixed point ``y*`` of ``ĝ`` (defect density inside
  the cone once mixing has occurred);
* ``spreading_rate`` — branching-random-walk front speeds from the per-offset
  sensitivities, converted to a cone extent under the *identical* horizon and
  normalization as :func:`caspectra.eval.dynamics.damage_spreading_features`;
* ``damage_fraction`` — ``y*`` times the fraction of the ring the cone covers.

What the approximation ignores — spatial correlation between neighbouring
defects, defect annihilation, and the drift of the row distribution away from
Bernoulli(1/2) — is exactly the pre-declared failure surface (marginal and
near-critical rules; docs/research_directions_2026-07-07.md §2). The estimator
is a *descriptive, post-hoc* addition to the accuracy-vs-budget family and
plays no role in any registered criterion.
"""

from __future__ import annotations

import numpy as np

from caspectra.eval.dynamics import DYNAMICS_FEATURE_NAMES
from caspectra.eval.rule_inference import complete_table, infer_rule_table

__all__ = [
    "damage_map",
    "single_bit_sensitivities",
    "mean_boolean_derivative",
    "annealed_damage_map",
    "annealed_damage_slope",
    "gw_survival",
    "cone_fill_fixed_point",
    "front_speeds",
    "spreading_rate",
    "annealed_horizon",
    "annealed_features",
    "annealed_estimate_from_diagram",
]

# Survival below this is treated as extinction when gating the conditional
# features (dynamics.py reports the conditional features as 0 when no pair
# survives; the analytic analogue of "no survivors at any realistic n_pairs").
_EXTINCT = 1e-6
# Slack for the marginal ĝ′(0) = 1 case (identity-like rules): the fixed-point
# iteration cannot leave y0, and the true mean-field answer is "no mixing".
_MARGINAL_TOL = 1e-9


def _n_bits(radius: int) -> int:
    return 2 * radius + 1


def damage_map(table: np.ndarray, radius: int) -> np.ndarray:
    """Exact disagreement probability ``d_S`` for every flip-mask ``S``.

    ``d_S = P_x[f(x) != f(x XOR S)]`` under ``x ~ Bernoulli(1/2)^(2r+1)`` —
    brute force over all ``(x, S)`` pairs, which is trivial for r <= 2
    (``32 x 32`` lookups). ``d[0] == 0`` by construction. The Bernoulli(1/2)
    measure is the *protocol's* IC measure; after transients the row
    distribution drifts to the rule's invariant measure, a known bias of this
    estimator (pre-declared).
    """
    size = 1 << _n_bits(radius)
    t = np.asarray(table, dtype=np.uint8)
    if t.shape != (size,):
        raise ValueError(f"table must have {size} entries for radius {radius}, got {t.shape}")
    idx = np.arange(size)
    xor = idx[:, None] ^ idx[None, :]  # [x, S] -> x XOR S
    return (t[:, None] != t[xor]).mean(axis=0).astype(np.float64)


def single_bit_sensitivities(
    table: np.ndarray, radius: int, *, d: np.ndarray | None = None
) -> np.ndarray:
    """Boolean-derivative profile ``p_k`` indexed by offset ``-r..+r``.

    ``p[radius + k]`` is the probability that flipping the input at offset
    ``k`` alone changes the output. The bit position follows the simulator
    convention ``bit = radius - offset`` (leftmost neighbour = MSB), so the
    profile lines up with tables from :class:`~caspectra.ca.range_ca.RangeCA`,
    :class:`~caspectra.ca.eca.ECASimulator` and the inverter.
    """
    if d is None:
        d = damage_map(table, radius)
    return np.array([d[1 << (radius - k)] for k in range(-radius, radius + 1)], dtype=np.float64)


def mean_boolean_derivative(p_by_offset: np.ndarray) -> float:
    """Mean Boolean derivative s̄ — Vispoel's table-side µ-sensitivity."""
    return float(np.mean(p_by_offset))


def annealed_damage_map(d: np.ndarray, radius: int, y: float | np.ndarray) -> float | np.ndarray:
    """The per-table Derrida–Pomeau map ``ĝ(y) = Σ_S y^|S| (1-y)^(n-|S|) d_S``.

    This is the one-step defect-density map under the annealed assumption that
    each input bit of each cell is flipped independently with probability
    ``y`` — exact at t = 0 for the protocol's single-flip Bernoulli(1/2) twins,
    an approximation afterwards.
    """
    n = _n_bits(radius)
    size = 1 << n
    pop = np.array([bin(s).count("1") for s in range(size)], dtype=np.int64)
    y_arr = np.asarray(y, dtype=np.float64)
    w = y_arr[..., None] ** pop * (1.0 - y_arr[..., None]) ** (n - pop)
    out = (w * np.asarray(d, dtype=np.float64)).sum(axis=-1)
    return float(out) if np.isscalar(y) or y_arr.ndim == 0 else out


def annealed_damage_slope(p_by_offset: np.ndarray) -> float:
    """``ĝ'(0) = Σ_k p_k = (2r+1)·s̄`` — the mean-field survival criterion.

    ``> 1`` is simultaneously Derrida–Pomeau instability of y = 0, Bagnoli's
    mean-field λ = log((2r+1)μ) > 0, and supercriticality of the branching
    process behind :func:`gw_survival`.
    """
    return float(np.sum(p_by_offset))


def gw_survival(p_by_offset: np.ndarray, horizon: int) -> float:
    """Finite-horizon survival of the defect branching process.

    Offspring pgf ``G(q) = Π_k (1 - p_k + p_k q)`` (each downstream cell is an
    independent potential defect); ``q_{t+1} = G(q_t)`` from ``q_0 = 0`` gives
    the probability the line is extinct after ``horizon`` generations. Ignores
    defect *interaction* (annihilation) — Bagnoli's replica-counting caveat —
    so it upper-bounds survival for marginal rules.
    """
    p = np.asarray(p_by_offset, dtype=np.float64)
    q = 0.0
    for _ in range(int(horizon)):
        q = float(np.prod(1.0 - p + p * q))
    return 1.0 - q


def cone_fill_fixed_point(
    d: np.ndarray,
    radius: int,
    *,
    width: int,
    n_iter: int = 500,
    p_by_offset: np.ndarray | None = None,
) -> float:
    """Stable fixed point ``y*`` of ``ĝ`` — the mean-field in-cone defect density.

    Returns 0 when ``ĝ'(0) <= 1`` (sub- or exactly critical): the iteration
    cannot leave ``y0`` and the mean-field prediction is "no mixed damage".
    This deliberately gives 0 for identity-like marginal rules whose frozen
    single defect has an *MC* cone_fill of 1 — the pre-declared marginal miss.
    Iterates with 0.5 damping because ``ĝ`` need not be monotone (rule 90's
    ``2y(1-y)`` peaks at 1/2), which would otherwise allow 2-cycles.
    """
    if p_by_offset is None:
        p_by_offset = np.array(
            [d[1 << (radius - k)] for k in range(-radius, radius + 1)], dtype=np.float64
        )
    if annealed_damage_slope(p_by_offset) <= 1.0 + _MARGINAL_TOL:
        return 0.0
    y = 1.0 / width
    for _ in range(n_iter):
        y_new = float(annealed_damage_map(d, radius, y))
        if abs(y_new - y) < 1e-12:
            return y_new
        y = 0.5 * (y + y_new)
    return y


def front_speeds(p_by_offset: np.ndarray, radius: int) -> tuple[float, float]:
    """Branching-random-walk edge speeds ``(v_right, v_left)`` of the damage cone.

    A defect at offset ``o`` in a cell's neighbourhood is a *parent* displaced
    by ``m = -o`` from its child, so the offspring intensity at displacement
    ``m`` is ``p_{-m}``. The classical BRW speed is
    ``v = inf_θ (1/θ)·ln Σ_m I(m) e^{θm}`` (rightward; mirror for leftward),
    evaluated on a wide log-θ grid with a stable logsumexp — the infimum sits
    at θ→∞ for ballistic rules, so no interior minimizer can be assumed.
    Speeds may be negative (drift: rule 170's cone "right edge" moves left);
    each is capped at the light-cone speed ``radius``. Returns ``(0, 0)`` when
    ``Σ p_k < 1`` (strictly subcritical: h(θ)/θ → -∞ as θ→0 and no front
    exists); at Σ p_k = 1 exactly the formula still yields the deterministic
    drift (rule 170: (-1, +1), net extent growth 0), so marginal rules keep
    their directionality.
    """
    p = np.asarray(p_by_offset, dtype=np.float64)
    if p.sum() < 1.0 - _MARGINAL_TOL:
        return 0.0, 0.0
    offsets = np.arange(-radius, radius + 1)
    active = p > 0.0
    logp = np.log(p[active])
    disp = -offsets[active]  # child displacement m = -offset
    thetas = np.logspace(-3.0, 3.0, 601)

    def edge(sign: float) -> float:
        a = logp[None, :] + sign * thetas[:, None] * disp[None, :]
        amax = a.max(axis=1)
        h = amax + np.log(np.exp(a - amax[:, None]).sum(axis=1))
        return float(np.min(h / thetas))

    return min(edge(+1.0), float(radius)), min(edge(-1.0), float(radius))


def annealed_horizon(width: int, radius: int) -> int:
    """Effective rule applications behind the cached targets.

    :func:`~caspectra.eval.dynamics.damage_spreading_features` evolves
    ``n_steps = width // (2*radius) - 1`` *rows*, of which row 0 is the IC, and
    reads damage at the last row — i.e. after ``n_steps - 1`` applications.
    The analytic member must count generations the same way or it aims one
    step past the target it is scored against.
    """
    n_steps = width // (2 * radius) - 1
    if n_steps < 2:
        raise ValueError(f"width {width} too small for radius {radius}")
    return n_steps - 1


def _extent(p_by_offset: np.ndarray, radius: int, width: int) -> float:
    """Predicted cone extent (cells) at the horizon, capped at the ring size."""
    v_r, v_l = front_speeds(p_by_offset, radius)
    growth = max(0.0, v_r + v_l)
    return min(float(width), growth * annealed_horizon(width, radius) + 1.0)


def spreading_rate(p_by_offset: np.ndarray, radius: int, *, width: int = 127) -> float:
    """Conditional-on-survival spreading rate under the dynamics.py normalization.

    ``extent / (2*radius*n_steps)`` with ``extent`` from the BRW front speeds —
    so a light-speed rule scores ``(2rT+1)/(2r*n_steps)`` (~0.99), matching what
    the Monte-Carlo target itself reports, and a surviving frozen defect scores
    ``1/(2r*n_steps)`` (~0.008), not 0. Rules that die entirely are zeroed by
    the survival gate in :func:`annealed_features`, mirroring the conditional
    semantics of the target.
    """
    n_steps = width // (2 * radius) - 1
    return min(1.0, _extent(p_by_offset, radius, width) / (2.0 * radius * n_steps))


def annealed_features(table: np.ndarray, radius: int, *, width: int = 127) -> np.ndarray:
    """All four damage-response estimates, aligned to ``DYNAMICS_FEATURE_NAMES``.

    Pure table computation — no simulation, no RNG; the "budget" of this family
    member is a few thousand float operations. The conditional features
    (fraction / rate / fill) are zeroed when predicted survival is below
    ``1e-6``, matching the target convention that conditionals are 0 when no
    pair survives.
    """
    d = damage_map(table, radius)
    p = single_bit_sensitivities(table, radius, d=d)
    horizon = annealed_horizon(width, radius)

    survival = gw_survival(p, horizon)
    y_star = cone_fill_fixed_point(d, radius, width=width, p_by_offset=p)
    extent = _extent(p, radius, width)
    rate = spreading_rate(p, radius, width=width)
    fill = y_star
    fraction = y_star * extent / width
    if survival < _EXTINCT:
        fraction = rate = fill = 0.0

    feats = np.zeros(len(DYNAMICS_FEATURE_NAMES), dtype=np.float64)
    feats[DYNAMICS_FEATURE_NAMES.index("damage_survival")] = survival
    feats[DYNAMICS_FEATURE_NAMES.index("damage_fraction")] = fraction
    feats[DYNAMICS_FEATURE_NAMES.index("spreading_rate")] = rate
    feats[DYNAMICS_FEATURE_NAMES.index("cone_fill")] = fill
    return feats


def annealed_estimate_from_diagram(
    diagram: np.ndarray,
    radius: int = 1,
    *,
    width: int = 127,
    completion: str = "zero",
) -> tuple[np.ndarray, float]:
    """The pipeline member: reconstruct the table from ONE diagram, then annealed.

    Same inverter and completion policy as the mechanistic estimator
    (:func:`~caspectra.eval.rule_inference.mechanistic_estimate`), so the two
    differ only in what happens *after* the table is read: simulate twins
    (budget ∝ n_pairs) versus iterate the annealed map (budget ~ 0). Returns
    ``(features, coverage)``; low coverage means the estimate leans on the
    completion prior — the tabulation exercise-dependence the manuscript
    measures.
    """
    table, observed, _ = infer_rule_table(diagram, radius)
    completed = complete_table(table, observed, completion)
    return annealed_features(completed, radius, width=width), float(observed.mean())
