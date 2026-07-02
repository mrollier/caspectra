"""Load the external Li-Packard / Wolfram class table (BUILD_BRIEF.md §3.6, §8).

``rule_labels.csv`` (columns ``rule, lp_class, wolfram_class``) is supplied by
the user from the Li-Packard publication. These are *empirical behavioural*
classes and are intentionally kept out of :mod:`caspectra.ca.eca`. If the file
is absent, evaluation skips the LP/Wolfram parts but still runs the
rule-identity probe (the rule is always known).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

__all__ = ["RuleLabels", "load_rule_labels"]


@dataclass
class RuleLabels:
    """Mapping from ECA rule number to LP and Wolfram class labels.

    ``borderline`` flags rules whose class is unstable across published
    schemes or sits between classes in invariant space (40, 41, 42, 106 — see
    ``rule_labels_PROVENANCE.md``). Per EVALUATION_CRITERIA.md rev 2, class-IV
    metrics are reported both with and without these rules, so an ambiguous
    labelling can never silently decide pass/fail.
    """

    lp: dict[int, int]
    wolfram: dict[int, int]
    borderline: set[int] = field(default_factory=set)

    @property
    def has_lp(self) -> bool:
        return len(self.lp) > 0

    @property
    def has_wolfram(self) -> bool:
        return len(self.wolfram) > 0

    def lp_array(self, rules: list[int] | np.ndarray) -> np.ndarray:
        """LP class per rule; ``-1`` where a rule is missing from the table."""
        return np.array([self.lp.get(int(r), -1) for r in rules], dtype=np.int64)

    def wolfram_array(self, rules: list[int] | np.ndarray) -> np.ndarray:
        """Wolfram class per rule; ``-1`` where a rule is missing."""
        return np.array([self.wolfram.get(int(r), -1) for r in rules], dtype=np.int64)


def load_rule_labels(path: str | Path) -> RuleLabels | None:
    """Load ``rule_labels.csv`` or return ``None`` if the file does not exist.

    Rows with an empty/blank class cell are simply omitted from that mapping.
    """
    path = Path(path)
    if not path.exists():
        return None
    lp: dict[int, int] = {}
    wolfram: dict[int, int] = {}
    borderline: set[int] = set()
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule = int(row["rule"])
            if row.get("lp_class", "").strip():
                lp[rule] = int(row["lp_class"])
            if row.get("wolfram_class", "").strip():
                wolfram[rule] = int(row["wolfram_class"])
            if (row.get("borderline") or "").strip():
                borderline.add(rule)
    return RuleLabels(lp=lp, wolfram=wolfram, borderline=borderline)
