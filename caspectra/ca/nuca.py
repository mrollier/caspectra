"""Non-uniform cellular automata (nuCA): two ECA rules mixed across the lattice.

A non-uniform CA assigns each lattice cell its *own* update rule: here, one of
two ECA rules according to a per-cell ``rule_mask`` (e.g. rule 110 on the left
half of the ring, rule 54 on the right). These composed systems are the reason
the project's per-patch phenotype maps exist — a single observed history of a
spatially varying system admits no global twin-run experiment, so behaviour
must be *estimated* locally (EVALUATION_CRITERIA.md criterion 7).

The class mirrors :class:`caspectra.ca.eca.ECASimulator`'s ``evolve`` /
``random_diagram`` surface so the rest of the pipeline (dataset, evaluation)
can treat it as a drop-in source of spacetime diagrams. The update is the same
vectorised table lookup as the ECA, with the table gathered per-cell from the
mask — a cell *reads* its neighbours' states regardless of which rule those
neighbours follow; only the output map differs per cell.
"""

from __future__ import annotations

import numpy as np

from caspectra.ca.eca import _validate_rule

__all__ = ["NonUniformCA", "half_mask", "striped_mask"]


def half_mask(width: int) -> np.ndarray:
    """A two-region mask: ``rule_a`` on ``[0, width//2)``, ``rule_b`` on the rest.

    On a ring this creates exactly two rule interfaces (at ``width//2`` and at
    the wrap-around ``0``) — the geometry criterion 7's interface-exclusion
    band is specified against.
    """
    mask = np.zeros(width, dtype=np.uint8)
    mask[width // 2 :] = 1
    return mask


def striped_mask(width: int, period: int) -> np.ndarray:
    """Alternating stripes of ``period`` cells (``rule_a`` first).

    Used as a *qualitative* secondary diagnostic only: for periods at or below
    the map's receptive field no interface-free patch exists by construction.
    """
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    return ((np.arange(width) // period) % 2).astype(np.uint8)


class NonUniformCA:
    """A two-rule non-uniform CA under periodic boundary conditions.

    Convention matches :class:`caspectra.ca.eca.ECASimulator`: row 0 of a
    diagram is the initial condition at the top, time increases downward.

    Parameters
    ----------
    rule_a, rule_b:
        The two Wolfram rule numbers (0-255) to mix.
    rule_mask:
        A 1-D array assigning each cell to a rule: ``0`` -> ``rule_a``,
        ``1`` -> ``rule_b``. Its length fixes the lattice width.
    """

    def __init__(self, rule_a: int, rule_b: int, rule_mask: np.ndarray) -> None:
        _validate_rule(rule_a)
        _validate_rule(rule_b)
        self.rule_a = rule_a
        self.rule_b = rule_b
        mask = np.asarray(rule_mask, dtype=np.uint8).ravel()
        if mask.ndim != 1 or mask.size < 3:
            raise ValueError(f"rule_mask must be 1-D with width >= 3, got shape {mask.shape}")
        if not np.isin(mask, (0, 1)).all():
            raise ValueError("rule_mask entries must be 0 (rule_a) or 1 (rule_b)")
        self.rule_mask = mask
        # Per-cell lookup table (width, 8): row i is cell i's 8-entry rule
        # table, so one fancy-index gathers the whole next row at once.
        tables = np.array(
            [[(rule >> i) & 1 for i in range(8)] for rule in (rule_a, rule_b)],
            dtype=np.uint8,
        )
        self._cell_tables: np.ndarray = tables[mask]

    @property
    def width(self) -> int:
        """Lattice width, fixed by the mask length."""
        return int(self.rule_mask.size)

    def step(self, row: np.ndarray) -> np.ndarray:
        """Advance one time step; each cell applies its own rule table."""
        left = np.roll(row, 1)
        right = np.roll(row, -1)
        index = (left << 2) | (row << 1) | right
        return self._cell_tables[np.arange(row.shape[0]), index]

    def evolve(self, initial_row: np.ndarray, n_steps: int) -> np.ndarray:
        """Evolve ``initial_row`` into an ``(n_steps, width)`` uint8 diagram.

        Row 0 is the initial condition, matching ``ECASimulator.evolve``.
        """
        if n_steps < 1:
            raise ValueError(f"n_steps must be >= 1, got {n_steps}")
        row = np.asarray(initial_row, dtype=np.uint8).ravel()
        if row.shape[0] != self.width:
            raise ValueError(f"initial_row width {row.shape[0]} != rule_mask width {self.width}")
        diagram = np.empty((n_steps, self.width), dtype=np.uint8)
        diagram[0] = row
        for t in range(1, n_steps):
            row = self.step(row)
            diagram[t] = row
        return diagram

    def random_diagram(self, width: int, n_steps: int, rng: np.random.Generator) -> np.ndarray:
        """Evolve from a random binary initial row (reproducible via ``rng``)."""
        if width != self.width:
            raise ValueError(f"width {width} != rule_mask width {self.width}")
        ic = rng.integers(0, 2, size=width, dtype=np.uint8)
        return self.evolve(ic, n_steps)
