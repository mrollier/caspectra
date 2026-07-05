"""Audit manuscript and RESULTS.md numbers against the canonical frontier artifact.

WHY: the rev-9 review round found that prose/table numbers can silently retain
values from a discarded run even when the released artifact is correct (the
frozen-CNN "-1.1 at 20% noise" incident; see RESULTS.md rev-9 provenance
note and manuscript/reviews/simulated/r1_methodology.md). Table-generation is
already programmatic; this script extends the audit to *quoted prose* in
Sec. IV E of the manuscript and to the hand-written rev-9 tables in
RESULTS.md, by re-deriving every quoted value from
``runs/m4_range2/frontier_grid/summary.json`` and failing loudly on mismatch.

Usage: ``python scripts/audit_manuscript_numbers.py`` (exit 0 = all checks
pass). Tolerance is half a unit in the last quoted decimal place, so a check
fails exactly when the artifact would round to a different printed value.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUMMARY = REPO / "runs" / "m4_range2" / "frontier_grid" / "summary.json"
CONTROLS = REPO / "runs" / "m4_range2" / "frontier_grid_controls" / "summary.json"
CALIBRATION = REPO / "runs" / "m4_range2" / "frontier_grid_calibration" / "summary.json"
MAIN_TEX = REPO / "manuscript" / "main.tex"
RESULTS = REPO / "RESULTS.md"


@dataclass
class Check:
    """One quoted number: where it is quoted, and how to re-derive it."""

    label: str
    quoted: float
    derived: float

    @property
    def ok(self) -> bool:
        # Half-ULP tolerance on the quoted precision: "0.85" passes for any
        # artifact value in [0.845, 0.855] (ties included, hence the 1e-9).
        decimals = len(str(self.quoted).split(".")[-1]) if "." in str(self.quoted) else 0
        return abs(self.quoted - self.derived) <= 0.5 * 10**-decimals + 1e-9


def _cell(grid: dict, axis: str, value: float, estimator: str) -> dict:
    for cell in grid[axis]:
        if cell["value"] == value:
            return cell["estimators"][estimator]
    raise KeyError(f"no cell {axis}={value}")


def _median(grid: dict, axis: str, value: float, estimator: str) -> float:
    return _cell(grid, axis, value, estimator)["median_r2"]


def _best_f1(grid: dict, axis: str, value: float) -> float:
    return max(
        _median(grid, axis, value, "f1_eps_estimated"),
        _median(grid, axis, value, "f1_eps_known"),
    )


def build_checks(grid: dict) -> list[Check]:
    """Every number quoted in Sec. IV E prose / the RESULTS.md rev-9 tables."""
    dead_zone = [0.075, 0.1, 0.15, 0.2]
    sampled = [_median(grid, "noise", v, "f2_sampled") for v in dead_zone]
    map_worst_case = max(
        _median(grid, ax, c["value"], "f2_map")
        for ax in grid
        for c in grid[ax]
        if "f2_map" in c["estimators"]
    )
    radius_cost = _median(grid, "radius", 0.0, "det_radius_known") - _median(
        grid, "radius", 0.0, "det_radius_selected"
    )
    return [
        # -- manuscript Sec. IV E, "Estimators for the degraded regime" prose --
        Check("mask 40%: posterior", 0.85, _best_f1(grid, "mask", 0.4)),
        Check("mask 40%: det inverter", 0.24, _median(grid, "mask", 0.4, "det")),
        Check("mask 50%: posterior", 0.59, _best_f1(grid, "mask", 0.5)),
        Check("mask 50%: det inverter", -0.77, _median(grid, "mask", 0.5, "det")),
        Check("density 0.1: posterior", 0.77, _median(grid, "density", 0.1, "f1_eps_estimated")),
        Check("density 0.1: det inverter", 0.08, _median(grid, "density", 0.1, "det")),
        Check("label flip: posterior", 0.99, _best_f1(grid, "label", 1.0)),
        Check("label flip: frozen CNN", 0.59, _median(grid, "label", 1.0, "cnn")),
        Check("noise 2%: posterior", 0.55, _median(grid, "noise", 0.02, "f1_eps_estimated")),
        Check("noise 2%: det inverter", 0.38, _median(grid, "noise", 0.02, "det")),
        Check("radius-selection cost (clean)", 0.12, radius_cost),
        Check(
            "reader bit accuracy (clean)",
            0.73,
            _cell(grid, "noise", 0.0, "f2_sampled")["bit_accuracy"],
        ),
        Check(
            "reader bit accuracy (20% noise)",
            0.70,
            _cell(grid, "noise", 0.2, "f2_sampled")["bit_accuracy"],
        ),
        Check("F2-MAP everywhere below", -2.2, map_worst_case),
        Check("dead-zone sampled band, low edge", -0.04, min(sampled)),
        Check("dead-zone sampled band, high edge", 0.17, max(sampled)),
        Check("noise 20%: det inverter", -5.6, _median(grid, "noise", 0.2, "det")),
        Check("noise 20%: frozen CNN", -0.93, _median(grid, "noise", 0.2, "cnn")),
        # -- RESULTS.md rev-9 F2 noise table, cnn/stack columns (the cells the
        #    discarded run had corrupted) --
        Check("F2 table, 3% cnn", 0.25, _median(grid, "noise", 0.03, "cnn")),
        Check("F2 table, 5% cnn", 0.15, _median(grid, "noise", 0.05, "cnn")),
        Check("F2 table, 5% stack", 0.10, _median(grid, "noise", 0.05, "stack")),
        Check("F2 table, 7.5% cnn", -0.13, _median(grid, "noise", 0.075, "cnn")),
        Check("F2 table, 10% cnn", -0.25, _median(grid, "noise", 0.1, "cnn")),
        Check("F2 table, 15% cnn", -0.57, _median(grid, "noise", 0.15, "cnn")),
        Check("F2 table, 20% cnn", -0.93, _median(grid, "noise", 0.2, "cnn")),
    ]


def build_rev10_checks(controls: dict, calibration: dict) -> list[Check]:
    """Numbers quoted from the rev-10 controls and the F1 calibration report."""
    band = [_median(controls, "noise", v, "degaug_cnn") for v in (0.03, 0.05, 0.075, 0.1, 0.15)]

    def _cov(axis: str, value: float) -> float:
        return _cell(calibration, axis, value, "f1_eps_estimated")["interval_coverage_1sigma"]

    return [
        Check("degaug band low edge (3-15% noise)", 0.51, min(band)),
        Check("degaug band high edge (3-15% noise)", 0.62, max(band)),
        Check("degaug at 20% noise", 0.17, _median(controls, "noise", 0.2, "degaug_cnn")),
        Check("degaug at 40% masking", 0.48, _median(controls, "mask", 0.4, "degaug_cnn")),
        Check("degaug at density 0.1", 0.20, _median(controls, "density", 0.1, "degaug_cnn")),
        Check("resnet clean grid cell", 0.55, _median(controls, "noise", 0.0, "resnet_cnn")),
        Check("resnet at 20% noise", -0.60, _median(controls, "noise", 0.2, "resnet_cnn")),
        Check("calibration: clean coverage", 0.86, _cov("mask", 0.0)),
        Check("calibration: 50% masking coverage", 0.74, _cov("mask", 0.5)),
        Check("calibration: 2% noise coverage", 0.58, _cov("noise", 0.02)),
        Check("calibration: 5% noise coverage", 0.45, _cov("noise", 0.05)),
        Check("calibration: 20% noise coverage", 0.13, _cov("noise", 0.2)),
    ]


def text_guards() -> list[tuple[str, bool]]:
    """Literal-string guards: the corrected values are present, stale ones gone."""
    tex = MAIN_TEX.read_text()
    results = RESULTS.read_text()
    return [
        ("main.tex quotes the canonical frozen-CNN value (-0.93)", "frozen CNN to $-0.93$" in tex),
        (
            "main.tex no longer quotes the discarded-run value (-1.1)",
            "frozen CNN to $-1.1$" not in tex,
        ),
        (
            "RESULTS.md F2 table has no discarded-run cnn cell",
            not re.search(r"\|\s*-1\.09\s*\|", results),
        ),
    ]


def main() -> int:
    grid = json.loads(SUMMARY.read_text())["grid"]
    checks = build_checks(grid)
    if CONTROLS.exists() and CALIBRATION.exists():
        checks += build_rev10_checks(
            json.loads(CONTROLS.read_text())["grid"],
            json.loads(CALIBRATION.read_text())["grid"],
        )
    failures = 0
    for check in checks:
        status = "ok " if check.ok else "FAIL"
        if not check.ok:
            failures += 1
        print(
            f"[{status}] {check.label}: quoted {check.quoted:+.3g}, artifact {check.derived:+.4f}"
        )
    for label, ok in text_guards():
        print(f"[{'ok ' if ok else 'FAIL'}] {label}")
        failures += 0 if ok else 1
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
