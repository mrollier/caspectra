#!/usr/bin/env python3
"""M3 (EVALUATION_CRITERIA.md rev 11): decompose the enriched radius-two panel.

The third review (C3/Q3) observes that the 160-rule held-out panel force-holds
every signature-complex rule, so the "global" summary is computed on a panel
enriched for the difficult subclass far above its prevalence in the sampling
universe. This script reports, per method and per target: (a) the forced
signature subpanel alone, (b) the stratified-random remainder alone, (c) the
full enriched panel (the published number), and (d) a post-stratified pooled
estimate — group-weighted SS_res/SS_tot with each group's weight matching its
prevalence in the rule universe the panel was drawn from, rather than its share
of the enriched panel. Stratified rule-bootstrap CIs preserve the group
composition. Descriptive; no gate (rev-11 M3).

Provenance disclosure carried with the numbers (rev-11 M3): signature
membership was computed by the registered criterion-9 thresholds from the same
seed-0 target cache later used for evaluation labels; the forced rules were
never trained on.

Usage::

    python scripts/analyze_panel_decomposition.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES
from caspectra.eval.method_predictions import collect_held_out_predictions
from caspectra.utils import ensure_dir, save_json, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="M3 enriched-panel decomposition (rev 11).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument(
        "--output-dir", default=None, help="Default <train.output_dir>/panel_decomposition."
    )
    return p.parse_args()


def _weighted_r2(pred: np.ndarray, truth: np.ndarray, w: np.ndarray) -> float:
    mean_w = float(np.sum(w * truth) / np.sum(w))
    total = float(np.sum(w * (truth - mean_w) ** 2))
    if total <= 0:
        return float("nan")
    return 1.0 - float(np.sum(w * (truth - pred) ** 2)) / total


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/panel_decomposition")
    set_seed(cfg.seed)

    hop = collect_held_out_predictions(cfg, args.checkpoint, device=args.device)
    cx = hop.complex_mask
    n_cx, n_rand = int(cx.sum()), int((~cx).sum())

    # Universe prevalence: the signature rules are ALL force-held, so their
    # universe count equals the panel count; the universe size is the full
    # deduplicated rule sample the split was drawn from.
    from caspectra.factory import build_dataset

    ds = build_dataset(cfg.data, training=False)
    all_rules = sorted({int(r) for r in np.asarray(ds.equiv_reps)})
    n_universe = len(all_rules)
    share_cx_universe = n_cx / n_universe
    share_cx_panel = n_cx / len(hop.held)
    # Per-rule post-stratification weights (normalized within group).
    w = np.where(
        cx, share_cx_universe / share_cx_panel, (1 - share_cx_universe) / (1 - share_cx_panel)
    )

    rng = np.random.default_rng(0)
    idx_cx, idx_rand = np.flatnonzero(cx), np.flatnonzero(~cx)
    # Stratified bootstrap: resample within each group to preserve composition.
    boot = [
        np.concatenate(
            [rng.choice(idx_cx, n_cx, replace=True), rng.choice(idx_rand, n_rand, replace=True)]
        )
        for _ in range(args.n_boot)
    ]

    def _panel_scores(pred: np.ndarray, truth: np.ndarray, sel: np.ndarray, wts=None) -> dict:
        wts = np.ones(len(truth)) if wts is None else wts
        per = [
            _weighted_r2(pred[sel, j], truth[sel, j], wts[sel]) for j in range(len(TARGET_NAMES))
        ]
        meds = []
        for idx in boot:
            s = idx[np.isin(idx, np.flatnonzero(sel))] if sel.dtype == bool else idx
            per_b = [
                _weighted_r2(pred[s, j], truth[s, j], wts[s]) for j in range(len(TARGET_NAMES))
            ]
            meds.append(np.nanmedian(per_b))
        meds = np.asarray(meds)
        return {
            "per_target_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
            "median_r2": round(float(np.nanmedian(per)), 4),
            "median_ci95": [
                round(float(np.nanpercentile(meds, 2.5)), 4),
                round(float(np.nanpercentile(meds, 97.5)), 4),
            ],
        }

    all_sel = np.ones(len(hop.held), dtype=bool)
    methods = {}
    for name, pred in hop.preds.items():
        methods[name] = {
            "signature_subpanel": _panel_scores(pred, hop.true, cx),
            "random_subpanel": _panel_scores(pred, hop.true, ~cx),
            "enriched_panel": _panel_scores(pred, hop.true, all_sel),
            "post_stratified": _panel_scores(pred, hop.true, all_sel, wts=w),
        }

    summary = {
        "radius": hop.radius,
        "n_held_out": len(hop.held),
        "n_signature": n_cx,
        "n_random": n_rand,
        "n_universe": n_universe,
        "signature_share_universe": round(share_cx_universe, 4),
        "signature_share_panel": round(share_cx_panel, 4),
        "provenance_disclosure": (
            "signature membership computed by the registered criterion-9 thresholds "
            "from the seed-0 target cache also used for evaluation labels; the forced "
            "rules were never trained on"
        ),
        "methods": methods,
    }
    save_json(summary, out / "summary.json")
    for name, m in methods.items():
        print(
            f"[m3] {name:>12}: signature {m['signature_subpanel']['median_r2']:+.4f}  "
            f"random {m['random_subpanel']['median_r2']:+.4f}  "
            f"enriched {m['enriched_panel']['median_r2']:+.4f}  "
            f"post-stratified {m['post_stratified']['median_r2']:+.4f}"
        )
    print(f"[m3] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
