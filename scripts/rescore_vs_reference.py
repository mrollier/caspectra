#!/usr/bin/env python3
"""M1 (EVALUATION_CRITERIA.md rev 11): rescore every estimator against theta.

The third review (C1/Q8) asks whether the direct estimators merely lose to a
noisy comparison target or genuinely fall short of the latent mean: a
fresh-simulation estimator scored against the near-noise-free reference should
rise from the replicate-agreement benchmark toward ICC, while a direct
estimator rises only to the extent it estimates the latent mean theta rather
than fitting the cached draw. This script scores every cached held-out
prediction against BOTH targets — the production cache (n_pairs from the
config) and the rev-8 C2.3 large-simulation reference (``--reference-n-pairs``,
seed offset +224737, identical to ``validate_mechanistic_baseline.py``) — in
one table per panel. Reporting only; no pass/fail gate (rev-11 M1).

Rev-10 control checkpoints (degradation-trained / unconstrained CNNs) can be
added with ``--extra-cnn NAME=CKPT``; they are frozen forward passes averaged
within rule, exactly like the primary CNN.

Usage::

    python scripts/rescore_vs_reference.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt \
        --extra-cnn degaug_cnn=runs/m4_range2_degaug/checkpoint_final.pt \
        --extra-cnn resnet_cnn=runs/m4_range2_resnet/checkpoint_final.pt
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.method_predictions import collect_held_out_predictions
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="M1 reference rescoring (rev 11).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--reference-n-pairs", type=int, default=4096)
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument(
        "--extra-cnn",
        action="append",
        default=[],
        metavar="NAME=CKPT",
        help="Rev-10 control checkpoint, evaluated as a frozen forward pass.",
    )
    p.add_argument(
        "--output-dir", default=None, help="Default <train.output_dir>/reference_rescore."
    )
    return p.parse_args()


def _extra_cnn_rule_preds(spec: str, cfg, device_pref: str) -> tuple[str, np.ndarray, list[int]]:
    """Rule-averaged held-out predictions of a control checkpoint (own scaler)."""
    import torch

    from caspectra.factory import build_dataloader, build_dataset, build_model
    from caspectra.utils import select_device

    name, ckpt = spec.split("=", 1)
    state = torch.load(ckpt, map_location="cpu", weights_only=False)
    e_cfg = ExperimentConfig.from_yaml(str(Path(ckpt).parent / "config.yaml"))
    model = build_model(e_cfg.model)
    model.load_state_dict(state["model_state"])
    device = select_device(prefer=device_pref)
    model = model.to(device).eval()
    ds = build_dataset(cfg.data, training=False)
    reps = np.asarray(ds.equiv_reps)
    loader = build_dataloader(
        ds, batch_size=cfg.eval.batch_size, shuffle=False, num_workers=cfg.train.num_workers
    )
    with torch.no_grad():
        pred_diag = np.concatenate([model(img.to(device)).cpu().numpy() for img, _ in loader])
    pred_diag = pred_diag * state["scaler_std"] + state["scaler_mean"]
    held = [int(r) for r in state["holdout_rules"] if int(r) in {int(x) for x in reps}]
    ho = np.isin(reps, held)
    reps_ho = reps[ho]
    rule_pred = np.stack([pred_diag[ho][reps_ho == r].mean(axis=0) for r in held])
    return name, rule_pred, held


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/reference_rescore")
    set_seed(cfg.seed)
    radius = cfg.data.radius

    hop = collect_held_out_predictions(cfg, args.checkpoint, device=args.device)
    held = hop.held
    print(f"[m1] radius={radius}  {len(held)} held-out rules")

    # Reference targets: identical call signature to validate_mechanistic_baseline
    # --reference-n-pairs, so the rev-8 cache is reused verbatim (no new sims).
    ref = np.stack(
        load_or_compute_invariant_targets(
            held,
            width=cfg.data.grid_size,
            ic_density=cfg.targets.ic_density,
            n_pairs=args.reference_n_pairs,
            seed=int(cfg.targets.seed) + 224737,
            cache_dir=cfg.data.cache_dir,
            radius=radius,
        )
    )
    cache = hop.true

    preds = dict(hop.preds)
    for spec in args.extra_cnn:
        name, rule_pred, e_held = _extra_cnn_rule_preds(spec, cfg, args.device)
        if e_held != held:
            raise SystemExit(f"control {name!r} holdout differs from the primary split")
        preds[name] = rule_pred

    rng = np.random.default_rng(0)
    boot = rng.integers(0, len(held), size=(args.n_boot, len(held)))

    def _median_ci(pred: np.ndarray, truth: np.ndarray) -> list[float]:
        meds = np.nanmedian(
            1.0
            - np.sum((truth[boot] - pred[boot]) ** 2, axis=1)
            / np.sum((truth[boot] - truth[boot].mean(axis=1, keepdims=True)) ** 2, axis=1),
            axis=1,
        )
        return [
            round(float(np.nanpercentile(meds, 2.5)), 4),
            round(float(np.nanpercentile(meds, 97.5)), 4),
        ]

    table: dict[str, dict] = {}
    for name, pred in preds.items():
        row = {}
        for label, truth in (("vs_cache", cache), ("vs_reference", ref)):
            per = r2_per_feature(pred, truth)
            row[label] = {
                "per_target_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
                "median_r2": round(float(np.nanmedian(per)), 4),
                "median_ci95": _median_ci(pred, truth),
            }
        row["median_shift"] = round(
            row["vs_reference"]["median_r2"] - row["vs_cache"]["median_r2"], 4
        )
        table[name] = row

    summary = {
        "radius": radius,
        "n_held_out": len(held),
        "n_pairs_cache": cfg.targets.n_pairs,
        "n_pairs_reference": args.reference_n_pairs,
        "cnn_note": "cnn is the seed-0 checkpoint (the pickle of record), not the 5-seed mean",
        "methods": table,
    }
    save_json(summary, out / "summary.json")
    for name, row in table.items():
        print(
            f"[m1] {name:>16}: cache {row['vs_cache']['median_r2']:+.4f}  "
            f"reference {row['vs_reference']['median_r2']:+.4f}  "
            f"shift {row['median_shift']:+.4f}"
        )
    print(f"[m1] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
