"""Range-``r`` binary cellular automata: the M4 larger rule space.

Elementary CAs (:class:`caspectra.ca.eca.ECASimulator`) are the range-1 case of
a two-state CA whose cell reads the ``2r+1`` neighbours ``(c-r, …, c, …, c+r)``.
Raising ``r`` to 2 enlarges the rule space from 256 to ``2**32`` and — crucially
for M4 (FOUNDATIONS.md §4; the criterion-6 "two-member complex club" caveat in
RESULTS.md) — makes glider-supporting / complex rules *plentiful* rather than a
two-member curiosity, so the amortizer's placement of complex behaviour can be
tested with a held-out **set** instead of ``n = 1``.

Everything downstream reuses unchanged: the update is the same vectorised table
lookup as the ECA (just a wider neighbourhood index), the diagrams are still
binary images, and left-right reflection + 0↔1 complementation are still the two
generating symmetries of the rule space — so the flip/invert augmentations
remain the *exact* orbit symmetries (``caspectra.data.augmentations``). The
class mirrors ``ECASimulator``'s ``evolve`` / ``random_diagram`` surface, and
additionally exposes ``max_speed = radius`` so damage-spreading measurement can
size its light cone correctly (``caspectra.eval.dynamics``).
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "RangeCA",
    "reflect",
    "complement",
    "orbit",
    "canonical",
    "sample_rules",
    "embed_eca",
    "n_rules",
    "table_size",
]


def table_size(radius: int) -> int:
    """Number of neighbourhood configurations: ``2**(2*radius+1)``."""
    if radius < 1:
        raise ValueError(f"radius must be >= 1, got {radius}")
    return 1 << (2 * radius + 1)


def n_rules(radius: int) -> int:
    """Size of the rule space: ``2**table_size(radius)`` (256 for ECAs)."""
    return 1 << table_size(radius)


def _validate_rule(rule: int, radius: int) -> None:
    if not (0 <= rule < n_rules(radius)):
        raise ValueError(f"range-{radius} rule must be in 0..{n_rules(radius) - 1}, got {rule}")


def reflect(rule: int, radius: int) -> int:
    """Left-right mirror image of ``rule``.

    Reflection reverses the neighbourhood, so the reflected rule's output for
    configuration ``i`` is the original rule's output for the bit-reversed
    configuration. The ``2r+1`` bits are reversed as a group; for ``radius = 1``
    this is exactly :func:`caspectra.ca.eca.reflect`.
    """
    _validate_rule(rule, radius)
    width = 2 * radius + 1
    reflected = 0
    for i in range(table_size(radius)):
        mirror = 0
        for b in range(width):
            mirror |= ((i >> b) & 1) << (width - 1 - b)
        reflected |= ((rule >> mirror) & 1) << i
    return reflected


def complement(rule: int, radius: int) -> int:
    """0↔1 complement of ``rule``.

    Complementation inverts every cell on both input and output: the
    complemented rule's output for configuration ``i`` is the inverse of the
    original output for the fully bit-flipped configuration ``i XOR all-ones``.
    For ``radius = 1`` this is exactly :func:`caspectra.ca.eca.complement`.
    """
    _validate_rule(rule, radius)
    all_ones = table_size(radius) - 1
    complemented = 0
    for i in range(table_size(radius)):
        complemented |= (1 - ((rule >> (i ^ all_ones)) & 1)) << i
    return complemented


def orbit(rule: int, radius: int) -> frozenset[int]:
    """The reflect+complement equivalence class (order ≤ 4) of ``rule``."""
    c = complement(rule, radius)
    return frozenset({rule, reflect(rule, radius), c, reflect(c, radius)})


def canonical(rule: int, radius: int) -> int:
    """The canonical representative (orbit minimum) of ``rule``."""
    return min(orbit(rule, radius))


def sample_rules(n: int, radius: int, rng: np.random.Generator) -> list[int]:
    """Sample ``n`` distinct canonical range-``radius`` rules, uniformly.

    Rules are drawn uniformly from the full space, folded to their orbit
    representative, and de-duplicated — so the returned list has no two rules
    that are reflections/complements of each other (mirroring
    ``independent_rules`` for ECAs, but by sampling since ``2**32`` cannot be
    enumerated). Raises if the space is too small to yield ``n`` distinct reps.
    """
    space = n_rules(radius)
    reps: dict[int, None] = {}
    # Draw in batches; fold and dedup until we have n. Bounded attempts guard
    # against an impossible request on a tiny space (e.g. radius small, n huge).
    attempts = 0
    max_attempts = 100 * n + 1000
    while len(reps) < n and attempts < max_attempts:
        draw = int(rng.integers(0, space))
        reps.setdefault(canonical(draw, radius), None)
        attempts += 1
    if len(reps) < n:
        raise ValueError(f"could not sample {n} distinct canonical rules for radius {radius}")
    return list(reps)[:n]


def embed_eca(eca_rule: int, radius: int = 2) -> int:
    """Embed an ECA (range-1) rule as a range-``radius`` rule ignoring the outer
    neighbours.

    The returned rule's output depends only on the central ``(c-1, c, c+1)``
    triple, so its dynamics — and hence its damage-spreading invariants —
    reproduce the ECA exactly. This gives named literature anchors (the famous
    complex rules 54/110, etc.) inside the range-2 space *and* a continuity
    control: the embedded rule's cached invariants must equal the ECA cache
    (``scripts`` / ``tests``).
    """
    if not (0 <= eca_rule <= 255):
        raise ValueError(f"eca_rule must be in 0..255, got {eca_rule}")
    if radius < 1:
        raise ValueError(f"radius must be >= 1, got {radius}")
    embedded = 0
    for i in range(table_size(radius)):
        # The central triple sits at shifts (radius-(-1), radius-0, radius-1) =
        # (radius+1, radius, radius-1); extracting those three bits, MSB first,
        # reconstructs the ECA neighbourhood index (left<<2 | centre<<1 | right).
        eca_index = (i >> (radius - 1)) & 0b111
        embedded |= ((eca_rule >> eca_index) & 1) << i
    return embedded


class RangeCA:
    """A two-state range-``radius`` cellular automaton under periodic boundaries.

    Convention matches :class:`caspectra.ca.eca.ECASimulator`: row 0 of a
    diagram is the initial condition at the top, time increases downward. The
    neighbourhood is ``(c-radius, …, c, …, c+radius)`` and the rule's ``2r+1``-bit
    table is indexed with the leftmost neighbour as the most-significant bit
    (so ``RangeCA(rule, 1)`` is bit-for-bit identical to ``ECASimulator(rule)``).

    Parameters
    ----------
    rule:
        Rule number in ``0..2**(2**(2*radius+1)) - 1``.
    radius:
        Neighbourhood radius (``r``); ``1`` recovers the ECA.
    """

    def __init__(self, rule: int, radius: int) -> None:
        _validate_rule(rule, radius)
        self.rule = rule
        self.radius = radius
        self.max_speed = radius  # light-cone speed: one cell per radius per step
        self.table: np.ndarray = np.array(
            [(rule >> i) & 1 for i in range(table_size(radius))], dtype=np.uint8
        )

    def _neighbourhood_index(self, row: np.ndarray) -> np.ndarray:
        index = np.zeros(row.shape[0], dtype=np.int64)
        for offset in range(-self.radius, self.radius + 1):
            neighbour = np.roll(row, -offset)  # neighbour[i] = row[i + offset]
            index |= neighbour.astype(np.int64) << (self.radius - offset)
        return index

    def step(self, row: np.ndarray) -> np.ndarray:
        """Advance a single row one time step (vectorised, periodic boundaries)."""
        return self.table[self._neighbourhood_index(row)]

    def evolve(self, initial_row: np.ndarray, n_steps: int) -> np.ndarray:
        """Evolve ``initial_row`` into an ``(n_steps, width)`` uint8 diagram.

        Row 0 is the initial condition, matching ``ECASimulator.evolve``.
        """
        if n_steps < 1:
            raise ValueError(f"n_steps must be >= 1, got {n_steps}")
        row = np.asarray(initial_row, dtype=np.uint8).ravel()
        width = row.shape[0]
        diagram = np.empty((n_steps, width), dtype=np.uint8)
        diagram[0] = row
        for t in range(1, n_steps):
            row = self.step(row)
            diagram[t] = row
        return diagram

    def random_diagram(self, width: int, n_steps: int, rng: np.random.Generator) -> np.ndarray:
        """Evolve from a random binary initial row (reproducible via ``rng``)."""
        ic = rng.integers(0, 2, size=width, dtype=np.uint8)
        return self.evolve(ic, n_steps)
