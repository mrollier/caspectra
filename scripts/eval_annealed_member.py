#!/usr/bin/env python3
"""Evaluate the annealed (mean-field) zero-budget member of the estimator family.

Two variants of :mod:`caspectra.eval.annealed` are scored against the cached
Monte-Carlo damage-response targets on a full rule panel:

* ``annealed_true`` — computed from the ground-truth rule table (the diagnostic
  ceiling of the analytic tier: how much of the damage response the mean-field
  approximation captures at all);
* ``annealed`` — computed from a table reconstructed from ONE observed diagram
  (the actual pipeline member: diagram -> inverter -> annealed map, zero
  simulation).

A 16-pair mechanistic estimate on the same diagrams is computed as the smallest
Monte-Carlo comparison anchor. Everything here is descriptive/post-hoc (the
pre-declared expectations and decision rule live in
``docs/research_directions_2026-07-07.md`` §2); no registered criterion is
involved.

Usage::

    python scripts/eval_annealed_member.py --config configs/default.yaml
    python scripts/eval_annealed_member.py --config configs/m4_range2.yaml
    python scripts/eval_annealed_member.py --config configs/default.yaml --smoke
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from caspectra.ca.eca import ECASimulator
from caspectra.ca.range_ca import RangeCA
from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.annealed import (
    annealed_damage_slope,
    annealed_estimate_from_diagram,
    annealed_features,
    single_bit_sensitivities,
)
from caspectra.eval.rule_inference import mechanistic_estimate
from caspectra.factory import build_dataset
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, set_seed

SURVIVAL = TARGET_NAMES.index("damage_survival")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Annealed zero-budget family member evaluation.")
    p.add_argument("--config", required=True)
    p.add_argument("--smoke", action="store_true", help="63px grid, 32-pair targets, cache_smoke.")
    p.add_argument("--completion", default="zero", help="Unobserved-entry policy (rev-7 default).")
    p.add_argument("--mech-pairs", type=int, default=16, help="MC anchor budget (0 disables).")
    p.add_argument("--output-dir", default=None)
    return p.parse_args()


def _true_table(rule: int, radius: int) -> np.ndarray:
    return ECASimulator(rule).table if radius == 1 else RangeCA(rule, radius).table


def _score(preds: np.ndarray, true: np.ndarray) -> dict:
    per = r2_per_feature(preds, true)
    return {
        "median_r2": round(float(np.nanmedian(per)), 4),
        "per_target_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
    }


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    panel = Path(args.config).stem + ("_smoke" if args.smoke else "")
    if args.smoke:
        cfg.data.grid_size = 63
        cfg.data.cache_dir = "cache_smoke"
        cfg.targets.n_pairs = 32
    out = ensure_dir(args.output_dir or f"runs/analysis/annealed_member/{panel}")
    set_seed(cfg.seed)
    radius, width = cfg.data.radius, cfg.data.grid_size

    ds = build_dataset(cfg.data, training=False)
    reps = np.asarray(ds.equiv_reps)
    images = ds.images
    rules = sorted({int(r) for r in reps})
    diag_by_rule = {r: images[np.flatnonzero(reps == r)[0]] for r in rules}
    targets = load_or_compute_invariant_targets(
        rules,
        width=width,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=radius,
    )
    print(f"[annealed] panel={panel} radius={radius} width={width} n_rules={len(rules)}")

    # --- The two annealed variants (analytic; latency is the whole budget). ----
    truth = np.stack(
        [annealed_features(_true_table(r, radius), radius, width=width) for r in rules]
    )
    t0 = time.perf_counter()
    from_diag, coverage = [], []
    for r in rules:
        feats, cov = annealed_estimate_from_diagram(
            diag_by_rule[r], radius, width=width, completion=args.completion
        )
        from_diag.append(feats)
        coverage.append(cov)
    latency = (time.perf_counter() - t0) / len(rules)
    from_diag = np.stack(from_diag)
    coverage = np.asarray(coverage)

    # Genotype-side diagnostics that come for free (wishlist item 2, s̄ part).
    slopes = np.array(
        [
            annealed_damage_slope(single_bit_sensitivities(_true_table(r, radius), radius))
            for r in rules
        ]
    )
    s_bar = slopes / (2 * radius + 1)
    # The identity-chain criterion: does sign(ĝ'(0) - 1) predict MC survival?
    sign_agree = float(np.mean((slopes > 1.0) == (targets[:, SURVIVAL] > 0.5)))

    # --- Smallest Monte-Carlo anchor on the same diagrams. ---------------------
    mech = None
    if args.mech_pairs > 0:
        preds = []
        t0 = time.perf_counter()
        for r in rules:
            rng = np.random.default_rng(
                np.random.SeedSequence(
                    [int(cfg.targets.seed) + 104729, int(r), int(radius), args.mech_pairs]
                )
            )
            feats, _, _ = mechanistic_estimate(
                diag_by_rule[r],
                radius,
                width=width,
                n_pairs=args.mech_pairs,
                ic_density=cfg.targets.ic_density,
                completion=args.completion,
                rng=rng,
            )
            preds.append(feats)
        mech_latency = (time.perf_counter() - t0) / len(rules)
        mech = {
            **_score(np.stack(preds), targets),
            "n_pairs": args.mech_pairs,
            "latency_s_per_diagram": round(mech_latency, 5),
        }

    summary = {
        "panel": panel,
        "radius": radius,
        "width": width,
        "n_rules": len(rules),
        "completion": args.completion,
        "target_n_pairs": cfg.targets.n_pairs,
        "annealed_true": _score(truth, targets),
        "annealed": {
            **_score(from_diag, targets),
            "latency_s_per_diagram": round(latency, 6),
            "coverage_mean": round(float(coverage.mean()), 4),
            "coverage_p10": round(float(np.percentile(coverage, 10)), 4),
        },
        "mechanistic_anchor": mech,
        "survival_sign_agreement": round(sign_agree, 4),
        "note": "descriptive post-hoc analysis; pre-declared expectations in "
        "docs/research_directions_2026-07-07.md §2",
    }
    save_json(summary, out / "summary.json")

    with open(out / "per_rule.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["rule", "coverage", "slope", "s_bar"]
            + [f"true_{n}" for n in TARGET_NAMES]
            + [f"annealed_{n}" for n in TARGET_NAMES]
            + [f"annealed_true_{n}" for n in TARGET_NAMES]
        )
        for i, r in enumerate(rules):
            w.writerow(
                [
                    r,
                    round(float(coverage[i]), 4),
                    round(float(slopes[i]), 4),
                    round(float(s_bar[i]), 4),
                ]
                + [round(float(v), 5) for v in targets[i]]
                + [round(float(v), 5) for v in from_diag[i]]
                + [round(float(v), 5) for v in truth[i]]
            )

    fig, axes = plt.subplots(2, 2, figsize=(8, 8))
    for j, (ax, name) in enumerate(zip(axes.ravel(), TARGET_NAMES)):
        ax.scatter(targets[:, j], truth[:, j], s=8, alpha=0.5, label="annealed (true table)")
        ax.scatter(targets[:, j], from_diag[:, j], s=8, alpha=0.5, label="annealed (from diagram)")
        ax.plot([0, 1], [0, 1], "k--", lw=0.8)
        ax.set_xlabel(f"MC target: {name}")
        ax.set_ylabel("annealed estimate")
        if j == 0:
            ax.legend(fontsize=8)
    fig.suptitle(f"Annealed member vs {cfg.targets.n_pairs}-pair MC targets — {panel}")
    fig.tight_layout()
    fig.savefig(out / "scatter.png", dpi=150)
    plt.close(fig)

    print(f"[annealed] annealed_true : {summary['annealed_true']}")
    print(f"[annealed] annealed      : {summary['annealed']}")
    if mech is not None:
        print(f"[annealed] mech@{args.mech_pairs:<3}     : {mech}")
    print(f"[annealed] survival-sign agreement (ĝ'(0)>1 vs MC survival>0.5): {sign_agree:.3f}")
    print(f"[annealed] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
