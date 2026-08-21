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
COMPLEMENT = REPO / "runs" / "m4_range2" / "frontier_grid_complement" / "summary.json"
SEED1 = REPO / "runs" / "m4_range2" / "frontier_grid_degaug_seed1" / "summary.json"
SEED2 = REPO / "runs" / "m4_range2" / "frontier_grid_degaug_seed2" / "summary.json"
SEEDREP = REPO / "runs" / "m4_range2" / "reference_rescore_seedrep" / "summary.json"
RESCORE = REPO / "runs" / "m4_range2" / "reference_rescore" / "summary.json"
EQUIV = REPO / "runs" / "m4_range2" / "paired_equivalence" / "summary.json"
EQUIV_ECA = REPO / "runs" / "lever_a_local" / "paired_equivalence" / "summary.json"
DECOMP = REPO / "runs" / "m4_range2" / "panel_decomposition" / "summary.json"
PERDIAG = REPO / "runs" / "m4_range2" / "per_diagram_audit" / "summary.json"
DEPLOY = REPO / "runs" / "m4_range2" / "deployment_stack" / "summary.json"
ROUND6 = REPO / "runs" / "analysis" / "round6_metrics" / "summary.json"
ROUND6_SEL = REPO / "runs" / "analysis" / "round6_metrics_sel" / "summary.json"
RETRIEVAL_R2 = REPO / "runs" / "m4_range2" / "retrieval_sel" / "summary.json"
RETRIEVAL_ECA = REPO / "runs" / "lever_a_local" / "retrieval_sel" / "summary.json"
GLIDER_T30 = REPO / "runs" / "analysis" / "glider_validation_T30" / "summary_r1.json"
STRAT = REPO / "runs" / "m4_range2_strat" / "control" / "summary.json"
RHOVAR = REPO / "runs" / "analysis" / "rho_variability" / "summary.json"
FULLTABLE_SEL = REPO / "runs" / "m4_range2" / "full_table_sel" / "summary.json"
FULLTABLE_SEL_ECA = REPO / "runs" / "lever_a_local" / "full_table_sel" / "summary.json"
FULLTABLE = REPO / "runs" / "m4_range2" / "full_table" / "summary.json"
FULLTABLE_ECA = REPO / "runs" / "lever_a_local" / "full_table" / "summary.json"
DECOMP_SEL = REPO / "runs" / "m4_range2" / "panel_decomposition_sel" / "summary.json"
STACK_SEL = REPO / "runs" / "m4_range2" / "stacking_sel" / "summary.json"
STACK_GBM_SEL = REPO / "runs" / "m4_range2" / "stacking_gbm_base_sel" / "summary.json"
DEPLOY_SEL = REPO / "runs" / "m4_range2" / "deployment_stack_sel" / "summary.json"
PROBE_R2_SEL = REPO / "runs" / "m4_range2" / "rule_probe_sel" / "summary.json"
PROBE_ECA_SEL = REPO / "runs" / "lever_a_local" / "rule_probe_sel" / "summary.json"
RESCORE_SEL = REPO / "runs" / "m4_range2" / "reference_rescore_sel" / "summary.json"
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


def build_rev11_checks() -> list[Check]:
    """Numbers quoted from the rev-11 review-response analyses (M1-M7)."""
    checks: list[Check] = []
    if RESCORE.exists():
        m = json.loads(RESCORE.read_text())["methods"]
        checks += [
            Check("M1 cnn vs cache", 0.859, m["cnn"]["vs_cache"]["median_r2"]),
            Check("M1 cnn reference shift", -0.000, m["cnn"]["median_shift"]),
            Check("M1 gbm vs cache", 0.845, m["gbm"]["vs_cache"]["median_r2"]),
            Check("M1 gbm reference shift", 0.007, m["gbm"]["median_shift"]),
            Check("M1 mech vs reference", 0.995, m["mechanistic"]["vs_reference"]["median_r2"]),
        ]
    if EQUIV.exists():
        e = json.loads(EQUIV.read_text())["per_target"]
        checks += [
            Check("M2 r2 survival diff", 0.001, e["damage_survival"]["paired_diff"]),
            Check("M2 r2 survival CI low", -0.008, e["damage_survival"]["diff_ci95"][0]),
            Check("M2 r2 survival CI high", 0.009, e["damage_survival"]["diff_ci95"][1]),
            Check("M2 r2 survival margin", 0.013, e["damage_survival"]["margin"]),
            Check("M2 r2 cone diff", 0.006, e["cone_fill"]["paired_diff"]),
            Check("M2 r2 cone CI high", 0.022, e["cone_fill"]["diff_ci95"][1]),
            Check("M2 r2 cone margin", 0.020, e["cone_fill"]["margin"]),
        ]
    if EQUIV_ECA.exists():
        e = json.loads(EQUIV_ECA.read_text())["per_target"]
        checks += [
            Check("M2 eca survival diff", 0.0003, e["damage_survival"]["paired_diff"]),
            Check("M2 eca survival CI high", 0.015, e["damage_survival"]["diff_ci95"][1]),
        ]
    if DECOMP.exists():
        d = json.loads(DECOMP.read_text())
        mm = d["methods"]["mechanistic"]
        mc = d["methods"]["cnn"]
        checks += [
            Check("M3 mech random subpanel", 0.995, mm["random_subpanel"]["median_r2"]),
            Check("M3 mech signature subpanel", 0.982, mm["signature_subpanel"]["median_r2"]),
            Check("M3 mech post-stratified", 0.994, mm["post_stratified"]["median_r2"]),
            Check("M3 cnn random subpanel", 0.821, mc["random_subpanel"]["median_r2"]),
            Check("M3 cnn post-stratified", 0.830, mc["post_stratified"]["median_r2"]),
            Check("M3 signature panel share", 0.356, d["signature_share_panel"]),
            Check("M3 signature universe share", 0.071, d["signature_share_universe"]),
        ]
    if PERDIAG.exists():
        p = json.loads(PERDIAG.read_text())
        checks += [
            Check("M4 per-diagram exact", 0.990, p["per_diagram"]["exact_reconstruction_rate"]),
            Check(
                "M4 first-diagram coverage",
                0.975,
                p["per_rule"]["first_diagram_full_coverage_share"],
            ),
        ]
    if DEPLOY.exists():
        d = json.loads(DEPLOY.read_text())
        checks += [
            Check("M6 stack median", 0.88, d["stack"]["median_r2"]),
            Check(
                "M6 survival increment",
                0.001,
                d["stack_over_cnn"]["damage_survival"]["incremental_r2_over_cnn"],
            ),
        ]
    if SEED1.exists() and SEED2.exists() and CONTROLS.exists():
        band_cells = (0.03, 0.05, 0.075, 0.1, 0.15)
        g1 = json.loads(SEED1.read_text())["grid"]
        g2 = json.loads(SEED2.read_text())["grid"]
        g0 = json.loads(CONTROLS.read_text())["grid"]
        b1 = [_median(g1, "noise", v, "degaug_seed1") for v in band_cells]
        b2 = [_median(g2, "noise", v, "degaug_seed2") for v in band_cells]
        b0 = [_median(g0, "noise", v, "degaug_cnn") for v in band_cells]
        clean0 = _median(g0, "noise", 0.0, "degaug_cnn")
        clean1 = _median(g1, "noise", 0.0, "degaug_seed1")
        clean2 = _median(g2, "noise", 0.0, "degaug_seed2")
        frozen_clean = _median(json.loads(SUMMARY.read_text())["grid"], "noise", 0.0, "cnn")
        checks += [
            Check("M5 per-seed band low (all seeds)", 0.24, min(b0 + b1 + b2)),
            Check("M5 per-seed band high (all seeds)", 0.62, max(b0 + b1 + b2)),
            Check("M5 two-of-three band low", 0.49, min(b0 + b2)),
            Check("M5 two-of-three band high", 0.62, max(b0 + b2)),
            Check("M5 seed1 band low", 0.24, min(b1)),
            Check("M5 seed1 band high", 0.33, max(b1)),
            Check("M5 seed1 at 20%", 0.31, _median(g1, "noise", 0.2, "degaug_seed1")),
            Check("M5 seed2 at 20%", 0.43, _median(g2, "noise", 0.2, "degaug_seed2")),
            Check("M5 tax low edge", 0.14, frozen_clean - max(clean0, clean1, clean2)),
            Check("M5 tax high edge", 0.37, frozen_clean - min(clean0, clean1, clean2)),
        ]
    if SEEDREP.exists():
        m = json.loads(SEEDREP.read_text())["methods"]
        checks += [
            Check("M5 seed1 clean panel", 0.59, m["degaug_seed1"]["vs_cache"]["median_r2"]),
            Check("M5 seed2 clean panel", 0.73, m["degaug_seed2"]["vs_cache"]["median_r2"]),
        ]
    if COMPLEMENT.exists():
        grid = json.loads(COMPLEMENT.read_text())["grid"]
        band = [_median(grid, "noise", v, "degaug_cnn") for v in (0.03, 0.05, 0.075, 0.1, 0.15)]
        checks += [
            Check("M7 degaug 7.5%", 0.70, _median(grid, "noise", 0.075, "degaug_cnn")),
            Check("M7 degaug 10%", 0.64, _median(grid, "noise", 0.1, "degaug_cnn")),
            Check("M7 degaug 15%", 0.35, _median(grid, "noise", 0.15, "degaug_cnn")),
            Check("M7 f1est 3%", 0.79, _median(grid, "noise", 0.03, "f1_eps_estimated")),
            Check("M7 f1est 5%", 0.70, _median(grid, "noise", 0.05, "f1_eps_estimated")),
            Check("M7 f1est 7.5%", 0.61, _median(grid, "noise", 0.075, "f1_eps_estimated")),
            Check("M7 f1est 10%", 0.37, _median(grid, "noise", 0.1, "f1_eps_estimated")),
            Check("M7 f1est 15%", -0.19, _median(grid, "noise", 0.15, "f1_eps_estimated")),
            Check("M7 complement band low", 0.35, min(band)),
            Check("M7 complement band high", 0.71, max(band)),
        ]
    return checks


def build_rev13_checks() -> list[Check]:
    """Round-5 review-response numbers (EVALUATION_CRITERIA rev 13)."""
    checks: list[Check] = []
    if ROUND6_SEL.exists():
        # M13 (rev 14): the CNN of record is the selected checkpoint, so every
        # CNN-dependent re-expression is audited against the _sel artifact;
        # the mech/gbm cells are identical in both artifacts by construction.
        d = json.loads(ROUND6_SEL.read_text())
        r2, eca = d["radius2"], d["eca"]
        rho2, rhoe = r2["A1_rho"], eca["A1_rho"]
        # Table IV (rho), rounded to one decimal in the manuscript.
        for tgt, mech, gbm, cnn in [
            ("damage_survival", 1.4, 4.0, 3.0),
            ("damage_fraction", 1.4, 7.2, 8.2),
            ("spreading_rate", 1.5, 9.5, 10),
            ("cone_fill", 1.0, 5.2, 6.0),
        ]:
            checks += [
                Check(f"rho r2 {tgt} mech", mech, rho2["mechanistic"][tgt]["rho"]),
                Check(f"rho r2 {tgt} gbm", gbm, rho2["gbm"][tgt]["rho"]),
                Check(f"rho r2 {tgt} cnn", cnn, rho2["cnn"][tgt]["rho"]),
            ]
        for tgt, mech, gbm, cnn in [
            ("damage_survival", 1.4, 6.0, 6.1),
            ("damage_fraction", 1.2, 20, 35),
            ("spreading_rate", 0.7, 27, 20),
            ("cone_fill", 1.8, 13, 12),
        ]:
            checks += [
                Check(f"rho eca {tgt} mech", mech, rhoe["mechanistic"][tgt]["rho"]),
                Check(f"rho eca {tgt} gbm", gbm, rhoe["gbm"][tgt]["rho"]),
                Check(f"rho eca {tgt} cnn", cnn, rhoe["cnn"][tgt]["rho"]),
            ]
        # A2 per-panel replicate benchmarks quoted in Table I.
        a2 = r2["A2_per_panel_reliability"]
        checks += [
            Check("panel bench enriched", 0.985, a2["enriched_panel"]["median_two_icc_minus_one"]),
            Check("panel ICC enriched", 0.993, a2["enriched_panel"]["median_icc"]),
            Check("panel bench random", 0.988, a2["random_subpanel"]["median_two_icc_minus_one"]),
            Check("panel ICC random", 0.994, a2["random_subpanel"]["median_icc"]),
            Check(
                "panel bench poststrat", 0.987, a2["post_stratified"]["median_two_icc_minus_one"]
            ),
            Check("panel ICC poststrat", 0.994, a2["post_stratified"]["median_icc"]),
            Check(
                "panel bench complex", 0.979, a2["signature_subpanel"]["median_two_icc_minus_one"]
            ),
            Check("panel ICC complex", 0.990, a2["signature_subpanel"]["median_icc"]),
            Check("max ICC shift vs universe", 0.010, a2["_max_abs_icc_shift"]),
        ]
        # A3 target dependence (Appendix B).
        by_label = {p["label"].split("_n")[0]: p for p in r2["A3_target_dependence"]["panels"]}
        checks += [
            Check("fill-vs-ratio R2 landscape", 0.64, by_label["landscape"]["r2_fill_vs_ratio"]),
            Check("fill-vs-ratio R2 panel", 0.70, by_label["held_out_panel"]["r2_fill_vs_ratio"]),
            Check("fill-vs-ratio pearson", 0.86, by_label["landscape"]["pearson_r"]),
        ]
        # A4 frontier ceilings quoted in the Fig. 1/2 captions and Table V.
        a4 = r2["A4_frontier_ceilings"]
        checks += [
            Check(
                "ceiling n=64 median",
                0.963,
                a4["identifiability_fig"]["median_read_then_simulate_ceiling"],
            ),
            Check(
                "ceiling n=64 survival",
                0.935,
                a4["identifiability_fig"]["damage_survival"]["read_then_simulate_ceiling"],
            ),
            Check(
                "ceiling n=64 cone fill",
                0.900,
                a4["identifiability_fig"]["cone_fill"]["read_then_simulate_ceiling"],
            ),
            Check(
                "ceiling n=48 median",
                0.953,
                a4["frontier_fig"]["median_read_then_simulate_ceiling"],
            ),
            Check(
                "ceiling n=48 survival",
                0.918,
                a4["frontier_fig"]["damage_survival"]["read_then_simulate_ceiling"],
            ),
            Check(
                "ceiling n=48 cone fill",
                0.871,
                a4["frontier_fig"]["cone_fill"]["read_then_simulate_ceiling"],
            ),
            Check("direct ICC ceiling", 0.993, a4["frontier_fig"]["median_icc_ceiling"]),
        ]
        # A5 survival-band stratification.
        for space, blk, mech, gbm, cnn in [
            ("r2", r2["A5_survival_band"], 0.94, 0.41, 0.75),
            ("eca", eca["A5_survival_band"], 0.90, -0.87, -1.05),
        ]:
            b = blk["damage_survival"]
            checks += [
                Check(f"band {space} mech", mech, b["mechanistic"]["r2_in_band"]),
                Check(f"band {space} gbm", gbm, b["gbm"]["r2_in_band"]),
                Check(f"band {space} cnn", cnn, b["cnn"]["r2_in_band"]),
            ]
        checks += [
            Check("band n r2", 40, r2["A5_survival_band"]["n_in_band"]),
            Check("band n eca", 14, eca["A5_survival_band"]["n_in_band"]),
        ]
    # M11 retrieval baseline.
    for path, space, stats5, bottleneck in [
        (RETRIEVAL_R2, "r2", 0.821, 0.864),
        (RETRIEVAL_ECA, "eca", 0.828, 0.883),
    ]:
        if path.exists():
            r = json.loads(path.read_text())["retrieval"]
            checks += [
                Check(f"retrieval {space} stats5", stats5, r["stats5"]["median_r2"]),
                Check(f"retrieval {space} bottleneck", bottleneck, r["bottleneck"]["median_r2"]),
            ]
    # M12 horizon-matched ECA signature.
    if GLIDER_T30.exists():
        g = json.loads(GLIDER_T30.read_text())
        checks.append(
            Check("M12 matched-horizon ECA count", 6, g["damage_signature_complex_count"])
        )
        checks.append(
            Check(
                "M12 matched-horizon ECA prevalence",
                0.068,
                g["damage_signature_complex_fraction"],
            )
        )
        checks.append(
            Check(
                "M12 matched-horizon precision vs class IV",
                0.333,
                g["damage_signature_vs_literature_confusion"]["precision"],
            )
        )
    return checks


def build_m10_checks() -> list[Check]:
    """M10 stratified-split control (rev 13): every number quoted in Sec. IV F(iv)."""
    checks: list[Check] = []
    if not STRAT.exists():
        return checks
    d = json.loads(STRAT.read_text())
    per = d["per_method_r2"]
    checks += [
        Check("M10 held-out rules", 160, d["n_held_out"]),
        Check("M10 signature-complex held out", 5, d["n_signature_complex"]),
        Check("M10 complex prevalence", 0.031, d["complex_prevalence"]),
        Check("M10 signature-complex in training", 52, d["n_signature_complex_in_training"]),
        Check("M10 mechanistic median", 0.992, per["mechanistic"]["median"]),
        Check("M10 gbm median", 0.780, per["gbm"]["median"]),
        Check("M10 cnn median", 0.778, per["cnn"]["median"]),
        Check("M10 cnn seed min", 0.74, min(d["cnn_seed_medians"])),
        Check("M10 cnn seed max", 0.78, max(d["cnn_seed_medians"])),
    ]
    # The enriched-panel values Sec. IV F(iv) puts next to the control.
    if DECOMP.exists():
        enr = json.loads(DECOMP.read_text())["methods"]
        checks += [
            Check(
                "M10 enriched mechanistic", 0.991, enr["mechanistic"]["enriched_panel"]["median_r2"]
            ),
            Check("M10 enriched gbm", 0.845, enr["gbm"]["enriched_panel"]["median_r2"]),
            Check("M10 enriched cnn", 0.859, enr["cnn"]["enriched_panel"]["median_r2"]),
        ]
    sub = d.get("cnn_subgroup", {})
    if sub:
        checks += [
            Check("M10 cnn complex subgroup", -0.81, sub["complex"]["median"]),
            Check("M10 cnn rest subgroup", 0.78, sub["rest"]["median"]),
        ]
    # The registered rule: the family gap must not shrink by >0.10 on any target
    # relative to the post-stratified gap, or the claim is downgraded.
    if DECOMP.exists():
        dec = json.loads(DECOMP.read_text())["methods"]
        worst = 0.0
        for direct in ("cnn", "gbm"):
            for target, strat_gap in d["family_gap"][f"mechanistic_minus_{direct}"].items():
                ps = (
                    dec["mechanistic"]["post_stratified"]["per_target_r2"][target]
                    - dec[direct]["post_stratified"]["per_target_r2"][target]
                )
                worst = max(worst, ps - strat_gap)
        checks.append(Check("M10 largest gap shrink (rule: <0.10)", 0.07, worst))
    return checks


def build_round7_checks() -> list[Check]:
    """Rev-14 numbers quoted after the fifth review: rho variability, mode
    accuracies, and (once scored) the M13 selection-protocol comparison."""
    checks: list[Check] = []
    if RHOVAR.exists():
        d = json.loads(RHOVAR.read_text())
        checks += [
            Check(
                "rev14 rho denominator sd (worst case, quoted 0.14)",
                0.14,
                d["worst_case_denominator_sd_of_rho"],
            ),
            # quoted as "up to ~0.6" -- the worst case must round to 0.6.
            Check(
                "rev14 rho total sampling sd (worst case, quoted ~0.6)",
                0.6,
                round(d["worst_case_total_sd_of_rho"], 1),
            ),
        ]
    if ROUND6_SEL.exists():
        d = json.loads(ROUND6_SEL.read_text())
        eca = d["eca"]["A5_survival_band"]["damage_survival"]
        r2 = d["radius2"]["A5_survival_band"]["damage_survival"]
        checks += [
            Check("mode accuracy ECA gbm", 0.89, eca["gbm"]["mode_accuracy_full_panel"]),
            Check("mode accuracy ECA cnn", 0.94, eca["cnn"]["mode_accuracy_full_panel"]),
            Check("mode accuracy r2 gbm", 0.99, r2["gbm"]["mode_accuracy_full_panel"]),
            Check("mode accuracy r2 cnn", 1.00, r2["cnn"]["mode_accuracy_full_panel"]),
        ]
    # M13 (rev 14): the switch-rule record and every selection-protocol number
    # quoted in the manuscript.
    if FULLTABLE_SEL.exists() and FULLTABLE.exists():
        sel = json.loads(FULLTABLE_SEL.read_text())
        fin = json.loads(FULLTABLE.read_text())
        s, f = sel["cnn_seed_spread"], fin["cnn_seed_spread"]
        worst_r2 = max(s[tt]["mean"] - f[tt]["mean"] for tt in f)
        checks += [
            Check("M13 r2 largest gain (App B: rule >+0.02, triggered)", 0.069, worst_r2),
            Check("M13 r2 cone fill final-epoch mean", 0.337, f["cone_fill"]["mean"]),
            Check("M13 r2 cone fill selected mean", 0.406, s["cone_fill"]["mean"]),
            Check("M13 r2 cone fill final-epoch sd", 0.109, f["cone_fill"]["std"]),
            Check("M13 r2 cone fill selected sd", 0.036, s["cone_fill"]["std"]),
            # Table II radius-two CNN column (mean +- sd over five seeds).
            Check("Table II r2 cnn survival", 0.887, s["damage_survival"]["mean"]),
            Check("Table II r2 cnn fraction", 0.891, s["damage_fraction"]["mean"]),
            Check("Table II r2 cnn rate", 0.875, s["spreading_rate"]["mean"]),
            Check("Table II r2 cnn fill", 0.406, s["cone_fill"]["mean"]),
        ]
        pairs = sel["pairs"]
        checks += [
            Check(
                "paired r2 cnn-gbm survival delta",
                0.08,
                pairs["cnn_minus_gbm"]["damage_survival"]["delta_r2"],
            ),
            Check(
                "paired r2 cnn-gbm fill delta",
                -0.14,
                pairs["cnn_minus_gbm"]["cone_fill"]["delta_r2"],
            ),
            Check(
                "paired r2 mech-cnn max superiority",
                0.53,
                max(v["delta_r2"] for v in pairs["mechanistic_minus_cnn"].values()),
            ),
            Check(
                "paired r2 mech-gbm max superiority",
                0.39,
                max(v["delta_r2"] for v in pairs["mechanistic_minus_gbm"].values()),
            ),
        ]
    if FULLTABLE_SEL_ECA.exists() and FULLTABLE_ECA.exists():
        sel = json.loads(FULLTABLE_SEL_ECA.read_text())["cnn_seed_spread"]
        fin = json.loads(FULLTABLE_ECA.read_text())["cnn_seed_spread"]
        worst_eca = max(sel[tt]["mean"] - fin[tt]["mean"] for tt in fin)
        checks += [
            Check("M13 eca largest gain (App B: below +0.02)", 0.015, worst_eca),
            Check(
                "M13 eca fraction delta (App B)",
                -0.027,
                sel["damage_fraction"]["mean"] - fin["damage_fraction"]["mean"],
            ),
            # Table II ECA CNN column.
            Check("Table II eca cnn survival", 0.695, sel["damage_survival"]["mean"]),
            Check("Table II eca cnn fraction", 0.762, sel["damage_fraction"]["mean"]),
            Check("Table II eca cnn rate", 0.960, sel["spreading_rate"]["mean"]),
            Check("Table II eca cnn fill", 0.931, sel["cone_fill"]["mean"]),
        ]
    # Table I five-seed CNN entries (median over the four targets, per seed),
    # recomputed from the per-seed prediction pickles of record.
    import pickle

    def _seed_medians(base: str, complex_only: bool = False) -> list[float]:
        import numpy as np

        out = []
        sig: set[int] = set()
        if complex_only:
            import yaml

            cfg = yaml.safe_load((REPO / "configs" / "m4_range2.yaml").read_text())
            sig = {int(r) for r in cfg["train"]["force_holdout_rules"]}
        for sd in range(5):
            name = "held_out_preds_np256_mech.pkl" if sd == 0 else "held_out_preds_np256_nomech.pkl"
            path = REPO / f"{base}{sd}" / name
            if not path.exists():
                return []
            with path.open("rb") as fh:
                hop = pickle.load(fh)
            true, pred = hop.true, hop.preds["cnn"]
            if complex_only:
                mask = np.array([r in sig for r in hop.held])
                true, pred = true[mask], pred[mask]
            ss = ((true - pred) ** 2).sum(0)
            tot = ((true - true.mean(0)) ** 2).sum(0)
            out.append(float(np.median(1 - ss / tot)))
        return out

    import numpy as np

    m_r2 = _seed_medians("runs/m4_range2_sel_seed")
    m_eca = _seed_medians("runs/lever_a_local_sel_seed")
    m_cx = _seed_medians("runs/m4_range2_sel_seed", complex_only=True)
    if m_r2 and m_eca and m_cx:
        checks += [
            Check("Table I r2 enriched cnn mean", 0.880, float(np.mean(m_r2))),
            Check("Table I r2 enriched cnn sd", 0.004, float(np.std(m_r2))),
            Check("Table I eca global cnn mean", 0.847, float(np.mean(m_eca))),
            Check("Table I eca global cnn sd", 0.006, float(np.std(m_eca))),
            Check("Table I r2 complex cnn mean", 0.837, float(np.mean(m_cx))),
            Check("Table I r2 complex cnn sd", 0.009, float(np.std(m_cx))),
        ]
    if DECOMP_SEL.exists():
        dec = json.loads(DECOMP_SEL.read_text())["methods"]["cnn"]
        checks += [
            Check(
                "decomp sel cnn enriched (prose 0.876)", 0.876, dec["enriched_panel"]["median_r2"]
            ),
            Check("Table I r2 random cnn (seed-0)", 0.862, dec["random_subpanel"]["median_r2"]),
            Check("Table I r2 poststrat cnn (seed-0)", 0.865, dec["post_stratified"]["median_r2"]),
            Check(
                "prose complex-vs-random direction", 0.843, dec["signature_subpanel"]["median_r2"]
            ),
        ]
    if STACK_SEL.exists():
        sv = json.loads(STACK_SEL.read_text())["increments"]["cnn_over_features"]["damage_survival"]
        checks += [
            Check("stacking survival increment", 0.33, sv["incremental_r2"]),
            Check("stacking survival ci low", 0.24, sv["ci95"][0]),
            Check("stacking survival ci high", 0.50, sv["ci95"][1]),
            Check("stacking survival base", 0.56, sv["base_model_r2"]),
            Check("stacking survival stacked", 0.89, sv["stacked_model_r2"]),
        ]
    if STACK_GBM_SEL.exists():
        sv = json.loads(STACK_GBM_SEL.read_text())["increments"]["cnn_over_gbm"]["damage_survival"]
        checks += [
            Check("gbm-base survival increment", 0.09, sv["incremental_r2"]),
            Check("gbm-base survival ci low", 0.02, sv["ci95"][0]),
            Check("gbm-base survival ci high", 0.19, sv["ci95"][1]),
        ]
    if DEPLOY_SEL.exists():
        dep = json.loads(DEPLOY_SEL.read_text())["stack_over_cnn"]
        checks += [
            Check(
                "deploy survival increment",
                0.001,
                dep["damage_survival"]["incremental_r2_over_cnn"],
            ),
            Check("deploy rate increment", 0.02, dep["spreading_rate"]["incremental_r2_over_cnn"]),
        ]
    for path, space, ident, bits in (
        (PROBE_ECA_SEL, "eca", 0.87, 0.79),
        (PROBE_R2_SEL, "r2", 0.95, 0.61),
    ):
        if path.exists():
            src = json.loads(path.read_text())["sources"]["cnn_bottleneck"]
            checks += [
                Check(f"probe {space} identity", ident, src["rule_identity_balanced_acc"]),
                Check(
                    f"probe {space} table bits",
                    bits,
                    src["truth_table_bit_balanced_acc_leave_rules_out"],
                ),
            ]
    if RESCORE_SEL.exists():
        cnn = json.loads(RESCORE_SEL.read_text())["methods"]["cnn"]
        checks += [
            Check("rescore sel cnn shift", 0.000, cnn["median_shift"]),
            Check("rescore sel cnn from-value", 0.876, cnn["vs_cache"]["median_r2"]),
        ]
    return checks


def text_guards() -> list[tuple[str, bool]]:
    """Literal-string guards: the corrected values are present, stale ones gone.

    Whitespace is collapsed first: LaTeX source wraps freely, so a guard phrase
    that happens to straddle a line break is a false alarm about the audit, not
    about the manuscript.
    """
    tex = re.sub(r"\s+", " ", MAIN_TEX.read_text())
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
        # Rev-13: the confounded cross-space prevalence comparison must not
        # return, and the identity framing must be present.
        (
            "main.tex no longer quotes the horizon-confounded 3/88 comparison",
            "versus $3/88$ elementary orbits" not in tex,
        ),
        (
            "main.tex states the matched-regime exchangeability identity",
            "eq:exchangeable" in tex,
        ),
        (
            "main.tex defines rho against its two reference ceilings",
            "eq:rho" in tex and "simulation-limited benchmark" in tex,
        ),
        # Rev-14 (fifth review): expectation-level exactness, explicit diagram
        # dimensions, no bare "invariant to panel composition" claim, and no
        # revision-number tags in the main-text body.
        (
            "main.tex qualifies the rho ceilings as expectation-level",
            "in expectation} under the additive-noise idealization" in tex,
        ),
        (
            "main.tex abstract states the 127x127 diagram dimensions",
            "$127\\times127$ spacetime diagrams of known radius" in tex,
        ),
        (
            "main.tex no longer claims rho is invariant to panel composition",
            "invariant to panel composition" not in tex,
        ),
        (
            "main.tex main body carries no revision-number tags",
            not re.search(r"rev[.\s~-]{0,2}\d", tex[: tex.index("Author declarations")]),
        ),
        (
            "main.tex conditions Eq. (1) on exact recovery in the equation",
            "conditional on exact recovery)" in tex,
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
    checks += build_rev11_checks()
    checks += build_rev13_checks()
    checks += build_m10_checks()
    checks += build_round7_checks()
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
