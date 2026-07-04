#!/usr/bin/env python3
"""R4 (EVALUATION_CRITERIA.md rev 7): the mechanistic rule-inference estimator.

The interpretable reference method of the benchmark. Because the local rule is
readable from a single diagram, an estimator that simply *reads the rule and
simulates* should recover the damage-response target up to Monte-Carlo noise —
i.e. reach the reliability ceiling (R3) with **no learned parameters**. This
script evaluates it on the **same** leave-rules-out split as the CNN amortiser
and the single-diagram baseline (``validate_baseline_regression.py``), so the
three methods are scored on the same held-out rules and the same cached truth.

For each held-out rule it infers the rule from one diagram, verifies the
inference is stable across a few of the rule's diagrams, then simulates the four
damage statistics under the identical protocol with an **independent** RNG (so a
correct inference gives an independent MC estimate, not a trivially identical
one). Reports per-target and median held-out-rule R², exact-inference rate, mean
table coverage, and (``--identifiability``) inference accuracy vs diagram height.

Usage::

    python scripts/validate_mechanistic_baseline.py --config configs/lever_a_local.yaml \
        --checkpoint runs/lever_a_local_seed0/checkpoint_final.pt --identifiability
"""

from __future__ import annotations

import argparse

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.data.splits import leave_rules_out_split
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.labels import load_rule_labels
from caspectra.eval.rule_inference import infer_rule, mechanistic_estimate
from caspectra.factory import build_dataset
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R4 mechanistic rule-inference estimator (rev 7).")
    p.add_argument("--config", required=True, help="Path to the YAML ExperimentConfig.")
    p.add_argument("--checkpoint", default=None, help="Use this CNN's stored held-out split.")
    p.add_argument(
        "--output-dir", default=None, help="Default <train.output_dir>/mechanistic_eval."
    )
    p.add_argument(
        "--n-pairs", type=int, default=None, help="Twin-run pairs (default targets.n_pairs)."
    )
    p.add_argument(
        "--identifiability", action="store_true", help="Sweep accuracy vs diagram height."
    )
    return p.parse_args()


def _config_split(cfg, rules):
    """Reproduce scripts/train_regressor.py's leave-rules-out split from config."""
    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    if labels and labels.has_wolfram:
        strata = np.array([int(labels.wolfram.get(int(r), -1)) for r in rules])
    else:
        strata = np.zeros(len(rules))
    return leave_rules_out_split(
        rules,
        strata,
        holdout_fraction=cfg.train.holdout_fraction,
        seed=cfg.train.holdout_seed,
        force_holdout=cfg.train.force_holdout_rules,
        force_train=cfg.train.force_train_rules,
    )


def _holdout_from_checkpoint(path: str) -> list[int]:
    import torch  # local import: only needed with --checkpoint

    state = torch.load(path, map_location="cpu", weights_only=False)
    return [int(r) for r in state["holdout_rules"]]


def _first_diagram(images, reps, rule):
    return images[np.flatnonzero(reps == rule)[0]]


def _inference_agreement(images, reps, rule, radius, k=8):
    """Fraction of up to ``k`` of the rule's diagrams whose inferred rule agrees
    with the first — a cheap check that a single diagram suffices."""
    idx = np.flatnonzero(reps == rule)[:k]
    inferred = [infer_rule(images[i], radius)[0] for i in idx]
    return float(np.mean([v == inferred[0] for v in inferred])), inferred[0]


def _identifiability_curve(images, reps, held, radius, heights):
    """Exact-inference rate and mean coverage vs diagram height, over held rules."""
    curve = []
    for h in heights:
        exact, covs = [], []
        for r in held:
            diag = _first_diagram(images, reps, r)
            if h > diag.shape[0]:
                continue
            inf, cov, _ = infer_rule(diag[:h], radius)
            exact.append(inf == int(r))
            covs.append(cov)
        if exact:
            curve.append(
                {
                    "height": int(h),
                    "exact_rate": round(float(np.mean(exact)), 4),
                    "mean_coverage": round(float(np.mean(covs)), 4),
                }
            )
    return curve


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/mechanistic_eval")
    set_seed(cfg.seed)
    radius = cfg.data.radius
    n_pairs = args.n_pairs if args.n_pairs is not None else cfg.targets.n_pairs

    dataset = build_dataset(cfg.data, training=False)
    reps = np.asarray(dataset.equiv_reps)
    images = dataset.images
    rules = sorted({int(r) for r in reps})

    targets = load_or_compute_invariant_targets(
        rules,
        width=cfg.data.grid_size,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=radius,
    )
    true_by_rule = {r: targets[i] for i, r in enumerate(rules)}

    if args.checkpoint:
        holdout_rules = _holdout_from_checkpoint(args.checkpoint)
    else:
        _, holdout_rules = _config_split(cfg, rules)
    held = [r for r in holdout_rules if r in set(rules)]
    print(f"[r4] radius={radius}  n_pairs={n_pairs}  {len(held)} held-out rules")

    # Independent RNG per rule: decorrelated from the target-cache seed so a
    # correct inference yields an *independent* MC estimate (offset is a prime).
    def _rng(rule: int) -> np.random.Generator:
        return np.random.default_rng(
            np.random.SeedSequence([int(cfg.targets.seed) + 104729, int(rule), int(radius)])
        )

    preds, exact, coverages, agree = [], [], [], []
    for r in held:
        agr, inferred = _inference_agreement(images, reps, r, radius)
        agree.append(agr)
        diagram = _first_diagram(images, reps, r)
        feats, inf_rule, cov = mechanistic_estimate(
            diagram,
            radius,
            width=cfg.data.grid_size,
            n_pairs=n_pairs,
            ic_density=cfg.targets.ic_density,
            rng=_rng(r),
        )
        preds.append(feats)
        exact.append(inf_rule == int(r))
        coverages.append(cov)

    pred_rule = np.stack(preds)
    true_rule = np.stack([true_by_rule[r] for r in held])
    per = r2_per_feature(pred_rule, true_rule)
    median = float(np.nanmedian(per))

    complex_set = {int(r) for r in cfg.train.force_holdout_rules} if radius > 1 else set()
    held_complex_idx = [i for i, r in enumerate(held) if r in complex_set]

    summary = {
        "radius": radius,
        "n_pairs": n_pairs,
        "n_held_out": len(held),
        "method": "mechanistic_rule_inference",
        "per_feature_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
        "median_r2": round(median, 4),
        "exact_inference_rate": round(float(np.mean(exact)), 4),
        "mean_coverage": round(float(np.mean(coverages)), 4),
        "mean_single_diagram_agreement": round(float(np.mean(agree)), 4),
    }
    if held_complex_idx:
        per_cx = r2_per_feature(pred_rule[held_complex_idx], true_rule[held_complex_idx])
        summary["complex_median_r2"] = round(float(np.nanmedian(per_cx)), 4)
        summary["complex_exact_inference_rate"] = round(
            float(np.mean([exact[i] for i in held_complex_idx])), 4
        )

    if args.identifiability:
        heights = [5, 10, 15, 20, 30, 45, 63, 95, 127]
        heights = [h for h in heights if h <= cfg.data.grid_size]
        summary["identifiability_curve"] = _identifiability_curve(
            images, reps, held, radius, heights
        )

    save_json(summary, out / "summary.json")
    print(f"[r4] median R² {median:.4f}   per-feature " f"{summary['per_feature_r2']}")
    print(
        f"[r4] exact-inference {summary['exact_inference_rate']:.3f}  "
        f"mean coverage {summary['mean_coverage']:.3f}  "
        f"single-diagram agreement {summary['mean_single_diagram_agreement']:.3f}"
    )
    if "complex_median_r2" in summary:
        print(
            f"[r4] complex-subset median R² {summary['complex_median_r2']:.4f}  "
            f"(exact-inference {summary['complex_exact_inference_rate']:.3f})"
        )
    print(f"[r4] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
