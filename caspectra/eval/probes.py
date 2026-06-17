"""Linear probes — the lead evaluation (BUILD_BRIEF.md §3.6).

We freeze the encoder, extract embeddings, and fit logistic-regression probes:

* **embedding -> rule identity**: we *want this clearly below 100%*. Near-perfect
  accuracy means the encoder learned the update rule (the genotype) — the known
  failure mode — so this is reported prominently.
* **embedding -> Li-Packard class** and **embedding -> Wolfram class**: we want
  these *well above* the majority-class baseline.

The headline success signal is the **gap** = behaviour-class accuracy − exact-rule
accuracy (the prior supervised paper's metric; large positive = phenotype, not
genotype). Because the classes are severely imbalanced, we also report
**balanced accuracy** and **macro-F1**, not just raw accuracy. LP/Wolfram probes
can optionally use a **leave-rules-out** split (hold out whole rules) to test
transfer to *unseen* rules of a known class (SELF_CRITICISM.md v2 roadmap #6).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from caspectra.eval.labels import RuleLabels

__all__ = ["ProbeResult", "ProbeReport", "run_probes"]


@dataclass
class ProbeResult:
    """Outcome of one linear probe."""

    name: str
    accuracy: float
    balanced_accuracy: float
    macro_f1: float
    baseline: float  # majority-class accuracy on the held-out set
    n_classes: int

    def __str__(self) -> str:
        return (
            f"{self.name:>8}: acc={self.accuracy:.3f} "
            f"bal_acc={self.balanced_accuracy:.3f} macroF1={self.macro_f1:.3f} "
            f"baseline={self.baseline:.3f} ({self.n_classes} classes)"
        )


@dataclass
class ProbeReport:
    """Bundle of probe results (rule always present; LP/Wolfram optional)."""

    rule: ProbeResult
    lp: ProbeResult | None = None
    wolfram: ProbeResult | None = None

    @property
    def gap(self) -> float | None:
        """Behaviour-class accuracy − exact-rule accuracy (want large, positive).

        Uses the LP probe as the behavioural side. ``None`` if LP labels are
        absent. This is the direct analogue of the supervised paper's success
        metric: high class accuracy *with* low rule accuracy.
        """
        if self.lp is None:
            return None
        return self.lp.accuracy - self.rule.accuracy

    def _results(self) -> list[ProbeResult]:
        return [r for r in (self.rule, self.lp, self.wolfram) if r is not None]

    def summary(self) -> str:
        header = "Linear probes (rule identity should be WELL BELOW 1.0):"
        lines = [header, *(str(r) for r in self._results())]
        if self.gap is not None:
            lines.append(
                f"    gap = LP_acc − rule_acc = {self.gap:+.3f} "
                "(want large & positive: behaviour learned, rule suppressed)"
            )
        return "\n".join(lines)

    def to_csv(self, path: str | Path) -> None:
        with Path(path).open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["probe", "accuracy", "balanced_accuracy", "macro_f1", "baseline", "n_classes"]
            )
            for r in self._results():
                writer.writerow(
                    [r.name, r.accuracy, r.balanced_accuracy, r.macro_f1, r.baseline, r.n_classes]
                )


def _make_classifier(max_iter: int, seed: int):
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=max_iter, random_state=seed),
    )


def _split(
    embeddings: np.ndarray,
    targets: np.ndarray,
    groups: np.ndarray | None,
    *,
    test_size: float,
    seed: int,
):
    """Train/test split — stratified by class, or grouped (leave-rules-out)."""
    if groups is not None:
        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
        train_idx, test_idx = next(splitter.split(embeddings, targets, groups))
        return (
            embeddings[train_idx],
            embeddings[test_idx],
            targets[train_idx],
            targets[test_idx],
        )
    return train_test_split(
        embeddings, targets, test_size=test_size, random_state=seed, stratify=targets
    )


def _fit_probe(
    name: str,
    embeddings: np.ndarray,
    targets: np.ndarray,
    *,
    test_size: float,
    seed: int,
    max_iter: int,
    groups: np.ndarray | None = None,
) -> ProbeResult:
    """Fit a logistic-regression probe and report held-out metrics."""
    # Keep only classes with at least two members so a stratified split works.
    classes, counts = np.unique(targets, return_counts=True)
    keep = np.isin(targets, classes[counts >= 2])
    embeddings, targets = embeddings[keep], targets[keep]
    groups = groups[keep] if groups is not None else None

    x_train, x_test, y_train, y_test = _split(
        embeddings, targets, groups, test_size=test_size, seed=seed
    )
    pipeline = _make_classifier(max_iter, seed)
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)

    accuracy = float(np.mean(y_pred == y_test))
    bal_acc = float(balanced_accuracy_score(y_test, y_pred))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro"))

    # Majority-class baseline on the held-out set.
    _, test_counts = np.unique(y_test, return_counts=True)
    baseline = float(test_counts.max() / test_counts.sum())
    return ProbeResult(name, accuracy, bal_acc, macro_f1, baseline, int(len(np.unique(targets))))


def run_probes(
    embeddings: np.ndarray,
    rules: np.ndarray,
    labels: RuleLabels | None,
    *,
    test_size: float = 0.3,
    seed: int = 0,
    max_iter: int = 1000,
    lp_split: str = "ic",
) -> ProbeReport:
    """Fit the rule probe and (if labels present) the LP and Wolfram probes.

    ``lp_split`` selects how the LP/Wolfram probes split data: ``"ic"`` (default)
    holds out initial conditions (every rule seen in training); ``"rules"`` holds
    out *entire rules* (leave-rules-out — tests transfer to unseen rules). The rule
    probe always uses the ``"ic"`` split (you cannot predict a held-out rule).
    """
    rule_result = _fit_probe(
        "rule", embeddings, rules, test_size=test_size, seed=seed, max_iter=max_iter
    )
    groups = rules if lp_split == "rules" else None
    lp_result = _label_probe("lp", embeddings, rules, labels, test_size, seed, max_iter, groups)
    wolfram_result = _label_probe(
        "wolfram", embeddings, rules, labels, test_size, seed, max_iter, groups
    )
    return ProbeReport(rule=rule_result, lp=lp_result, wolfram=wolfram_result)


def _label_probe(
    name: str,
    embeddings: np.ndarray,
    rules: np.ndarray,
    labels: RuleLabels | None,
    test_size: float,
    seed: int,
    max_iter: int,
    groups: np.ndarray | None,
) -> ProbeResult | None:
    """Fit one of the external-label probes (LP or Wolfram), if available."""
    if labels is None:
        return None
    targets = labels.lp_array(rules) if name == "lp" else labels.wolfram_array(rules)
    has = labels.has_lp if name == "lp" else labels.has_wolfram
    if not has:
        return None
    mask = targets >= 0
    if mask.sum() == 0:
        return None
    return _fit_probe(
        name,
        embeddings[mask],
        targets[mask],
        test_size=test_size,
        seed=seed,
        max_iter=max_iter,
        groups=groups[mask] if groups is not None else None,
    )
