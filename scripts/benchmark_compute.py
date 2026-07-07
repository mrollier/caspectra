#!/usr/bin/env python3
"""C8 (EVALUATION_CRITERIA.md rev 8): the accuracy-compute Pareto analysis.

The second referee (concern 11): "read the rule" is recommended without reporting
what it costs. This script measures, on the checkpoint's held-out rules:

* per-diagram wall-clock latency of the mechanistic estimator (rule inference +
  twin-run Monte-Carlo simulation) as a function of its MC budget ``n_pairs``,
  together with the accuracy (median held-out R^2) at each budget — the
  accuracy-vs-compute curve;
* per-diagram latency of the CNN forward pass (single-image and batched) and of
  the five-statistic baseline (feature computation + GBM predict);
* the **break-even query count**: how many deployment queries amortise the CNN's
  one-time training cost (supplied via ``--train-seconds``, measured from the
  training checkpoints' timestamps) given the per-query latency difference.

Usage::

    python scripts/benchmark_compute.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt --train-seconds 1330
"""

from __future__ import annotations

import argparse
import time

import numpy as np
import torch
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.annealed import annealed_estimate_from_diagram
from caspectra.eval.baselines import compute_baseline_features
from caspectra.eval.rule_inference import mechanistic_estimate
from caspectra.factory import build_dataset, build_model
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, select_device, set_seed

BUDGETS = [16, 32, 64, 128, 256]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="C8 accuracy-compute Pareto (rev 8).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument(
        "--train-seconds",
        type=float,
        default=None,
        help="One-time CNN training wall-clock (from checkpoint timestamps).",
    )
    p.add_argument("--timing-rules", type=int, default=24, help="Rules used for latency timing.")
    p.add_argument("--output-dir", default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/compute_pareto")
    set_seed(cfg.seed)
    radius, width = cfg.data.radius, cfg.data.grid_size

    ds = build_dataset(cfg.data, training=False)
    reps = np.asarray(ds.equiv_reps)
    images = ds.images
    rules = sorted({int(r) for r in reps})
    targets = load_or_compute_invariant_targets(
        rules,
        width=width,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=radius,
    )
    true_by_rule = {r: targets[i] for i, r in enumerate(rules)}

    state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    held = [int(r) for r in state["holdout_rules"] if int(r) in set(rules)]
    held_diag = {r: images[np.flatnonzero(reps == r)[0]] for r in held}
    true_held = np.stack([true_by_rule[r] for r in held])
    timing_rules = held[: args.timing_rules]
    print(f"[c8] radius={radius}  {len(held)} held-out rules ({len(timing_rules)} for timing)")

    def _rng(r, tag):
        return np.random.default_rng(
            np.random.SeedSequence([int(cfg.targets.seed) + 104729, int(r), int(radius), tag])
        )

    # --- Mechanistic: accuracy + latency per MC budget. -----------------------
    mech_curve = []
    for budget in BUDGETS:
        preds = []
        t0 = time.perf_counter()
        for r in held:
            feats, _, _ = mechanistic_estimate(
                held_diag[r],
                radius,
                width=width,
                n_pairs=budget,
                ic_density=cfg.targets.ic_density,
                rng=_rng(r, budget),
            )
            preds.append(feats)
        elapsed = time.perf_counter() - t0
        per = r2_per_feature(np.stack(preds), true_held)
        mech_curve.append(
            {
                "n_pairs": budget,
                "latency_s_per_diagram": round(elapsed / len(held), 4),
                "median_r2": round(float(np.nanmedian(per)), 4),
                "per_target_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
            }
        )
        print(
            f"[c8] mechanistic n_pairs={budget:>4}: {mech_curve[-1]['latency_s_per_diagram']:.3f}"
            f" s/diagram  median R² {mech_curve[-1]['median_r2']:.4f}"
        )

    # --- Annealed analytic member: the zero-budget point of the curve. --------
    # Must be routed to the analytic estimator: mechanistic_estimate with
    # n_pairs=0 would average an empty pair set (NaN). Descriptive/post-hoc; the
    # analytic tier is the family's *negative* anchor (see
    # scripts/eval_annealed_member.py and docs/research_directions_2026-07-07.md §4).
    t0 = time.perf_counter()
    preds0 = [annealed_estimate_from_diagram(held_diag[r], radius, width=width)[0] for r in held]
    elapsed0 = time.perf_counter() - t0
    per0 = r2_per_feature(np.stack(preds0), true_held)
    mech_curve.insert(
        0,
        {
            "n_pairs": 0,
            "latency_s_per_diagram": round(elapsed0 / len(held), 4),
            "median_r2": round(float(np.nanmedian(per0)), 4),
            "per_target_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per0)},
        },
    )
    print(
        f"[c8] annealed  n_pairs=   0: {mech_curve[0]['latency_s_per_diagram']:.3f}"
        f" s/diagram  median R² {mech_curve[0]['median_r2']:.4f}"
    )

    # --- CNN: forward-pass latency (single and batched). ----------------------
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    device = select_device(prefer=args.device)
    model = model.to(device).eval()
    imgs = np.stack([held_diag[r] for r in timing_rules]).astype(np.float32)
    with torch.no_grad():
        single = torch.from_numpy(imgs[0]).unsqueeze(0).unsqueeze(0).to(device)
        model(single)  # warm-up (kernel compilation)
        t0 = time.perf_counter()
        for i in range(len(imgs)):
            b = torch.from_numpy(imgs[i]).unsqueeze(0).unsqueeze(0).to(device)
            _ = model(b).cpu()
        cnn_single = (time.perf_counter() - t0) / len(imgs)
        batch = torch.from_numpy(imgs).unsqueeze(1).to(device)
        t0 = time.perf_counter()
        _ = model(batch).cpu()
        cnn_batched = (time.perf_counter() - t0) / len(imgs)

    # --- Five-statistic baseline: features + GBM predict latency. -------------
    train_rules = [r for r in rules if r not in set(held)]
    tr = np.isin(reps, train_rules)
    feats_all = compute_baseline_features(images, radius=radius)
    scaler = StandardScaler().fit(feats_all[tr])
    y = np.stack([true_by_rule[int(r)] for r in reps])
    t0 = time.perf_counter()
    gbms = [
        GradientBoostingRegressor(random_state=0).fit(scaler.transform(feats_all[tr]), y[tr, j])
        for j in range(len(TARGET_NAMES))
    ]
    gbm_fit_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    f = scaler.transform(compute_baseline_features(imgs.astype(np.uint8), radius=radius))
    _ = np.stack([g.predict(f) for g in gbms], axis=1)
    stat_latency = (time.perf_counter() - t0) / len(imgs)

    # --- Break-even. -----------------------------------------------------------
    mech_prod = next(c for c in mech_curve if c["n_pairs"] == cfg.targets.n_pairs)
    breakeven = None
    if args.train_seconds is not None:
        gap = mech_prod["latency_s_per_diagram"] - cnn_single
        breakeven = int(np.ceil(args.train_seconds / gap)) if gap > 0 else None

    summary = {
        "radius": radius,
        "n_held_out": len(held),
        "mechanistic_curve": mech_curve,
        "cnn_latency_s_single": round(cnn_single, 5),
        "cnn_latency_s_batched": round(cnn_batched, 5),
        "five_stat_latency_s_per_diagram": round(stat_latency, 5),
        "five_stat_one_time_fit_s": round(gbm_fit_s, 2),
        "cnn_one_time_train_s": args.train_seconds,
        "breakeven_queries_vs_mechanistic": breakeven,
        "note": "mechanistic latency is CPU-only and embarrassingly parallel over "
        "diagrams; CNN latency measured on the Metal device with warm cache",
    }
    save_json(summary, out / "summary.json")
    print(
        f"[c8] CNN forward: {cnn_single * 1e3:.1f} ms single / {cnn_batched * 1e3:.2f} ms batched"
    )
    print(f"[c8] 5-stat predict: {stat_latency * 1e3:.1f} ms (one-time fit {gbm_fit_s:.1f} s)")
    if breakeven is not None:
        print(
            f"[c8] break-even vs mechanistic@{cfg.targets.n_pairs}: {breakeven} queries "
            f"(training {args.train_seconds:.0f} s)"
        )
    print(f"[c8] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
