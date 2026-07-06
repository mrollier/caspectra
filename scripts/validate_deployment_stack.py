#!/usr/bin/env python3
"""M6 (EVALUATION_CRITERIA.md rev 11): deployment-style stacked estimator.

The third review (C7/Q9) correctly distinguishes the rev-7 stacking analysis —
a cross-fitted complementarity diagnostic computed *within* the held-out panel
— from a deployable stacked predictor. This script evaluates the latter: a
ridge meta-model per target over [five single-diagram statistics + the frozen
CNN's four predictions], fit ONLY on training rules (rule-averaged inputs,
cached targets), then applied once to the untouched held-out rules. It is the
same construction the frontier grid already deploys per cell
(``build_frontier_grid.py`` "stack"), evaluated here on the clean protocol at
the Table-III unit. The registered rev-7 adds-value margin (0.02, CI excluding
0) is reused for interpretation; the rev-7 diagnostic keeps its own label
(rev-11 M6).

Usage::

    python scripts/validate_deployment_stack.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse

import numpy as np
import torch
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.baselines import compute_baseline_features
from caspectra.factory import build_dataloader, build_dataset, build_model
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, select_device, set_seed

MARGIN = 0.02  # the registered rev-7 adds-value margin, reused for interpretation


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="M6 deployment-style stack (rev 11).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument(
        "--output-dir", default=None, help="Default <train.output_dir>/deployment_stack."
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/deployment_stack")
    set_seed(cfg.seed)
    radius = cfg.data.radius

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

    state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    held = [int(r) for r in state["holdout_rules"] if int(r) in set(rules)]
    train_rules = [r for r in rules if r not in set(held)]

    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    device = select_device(prefer=args.device)
    model = model.to(device).eval()
    loader = build_dataloader(
        dataset, batch_size=cfg.eval.batch_size, shuffle=False, num_workers=cfg.train.num_workers
    )
    with torch.no_grad():
        cnn_diag = np.concatenate([model(img.to(device)).cpu().numpy() for img, _ in loader])
    cnn_diag = cnn_diag * state["scaler_std"] + state["scaler_mean"]

    feats = compute_baseline_features(images, radius=radius)
    tr_mask = np.isin(reps, train_rules)
    scaler = StandardScaler().fit(feats[tr_mask])
    feats = scaler.transform(feats)

    def _rule_means(values: np.ndarray, rule_list: list[int]) -> np.ndarray:
        return np.stack([values[reps == r].mean(axis=0) for r in rule_list])

    X_tr = np.hstack([_rule_means(feats, train_rules), _rule_means(cnn_diag, train_rules)])
    X_ho = np.hstack([_rule_means(feats, held), _rule_means(cnn_diag, held)])
    y_tr = np.stack([true_by_rule[r] for r in train_rules])
    y_ho = np.stack([true_by_rule[r] for r in held])

    stack_pred = np.stack(
        [Ridge(alpha=1.0).fit(X_tr, y_tr[:, j]).predict(X_ho) for j in range(len(TARGET_NAMES))],
        axis=1,
    )
    cnn_pred = _rule_means(cnn_diag, held)

    rng = np.random.default_rng(0)
    boot = rng.integers(0, len(held), size=(args.n_boot, len(held)))

    def _scores(pred: np.ndarray) -> dict:
        per = r2_per_feature(pred, y_ho)
        meds = np.nanmedian(
            1.0
            - np.sum((y_ho[boot] - pred[boot]) ** 2, axis=1)
            / np.sum((y_ho[boot] - y_ho[boot].mean(axis=1, keepdims=True)) ** 2, axis=1),
            axis=1,
        )
        return {
            "per_target_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
            "median_r2": round(float(np.nanmedian(per)), 4),
            "median_ci95": [
                round(float(np.nanpercentile(meds, 2.5)), 4),
                round(float(np.nanpercentile(meds, 97.5)), 4),
            ],
        }

    # Per-target increment of the stack over the CNN alone, rule-bootstrapped.
    increments = {}
    for j, name in enumerate(TARGET_NAMES):
        yb = y_ho[boot, j]
        tot = np.sum((yb - yb.mean(axis=1, keepdims=True)) ** 2, axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            inc = (
                np.sum((yb - cnn_pred[boot, j]) ** 2, axis=1)
                - np.sum((yb - stack_pred[boot, j]) ** 2, axis=1)
            ) / tot
        inc = inc[np.isfinite(inc)]
        point = float(np.median(inc))
        ci = [float(np.percentile(inc, 2.5)), float(np.percentile(inc, 97.5))]
        increments[name] = {
            "incremental_r2_over_cnn": round(point, 4),
            "ci95": [round(ci[0], 4), round(ci[1], 4)],
            "adds_value": bool(point > MARGIN and ci[0] > 0),
        }

    summary = {
        "radius": radius,
        "n_train_rules": len(train_rules),
        "n_held_out": len(held),
        "margin": MARGIN,
        "stack": _scores(stack_pred),
        "cnn_alone": _scores(cnn_pred),
        "stack_over_cnn": increments,
        "note": (
            "deployment-style: ridge meta-model fit on training rules only, evaluated "
            "once on the untouched held-out panel (same construction as the frontier "
            "grid's 'stack' estimator, clean protocol, Table-III unit)"
        ),
    }
    save_json(summary, out / "summary.json")
    print(
        f"[m6] stack median {summary['stack']['median_r2']:+.4f} "
        f"CI{summary['stack']['median_ci95']}  vs cnn {summary['cnn_alone']['median_r2']:+.4f}"
    )
    for name, v in increments.items():
        print(
            f"[m6] {name:>16}: stack-over-cnn {v['incremental_r2_over_cnn']:+.4f} "
            f"CI[{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}]  adds_value={v['adds_value']}"
        )
    print(f"[m6] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
