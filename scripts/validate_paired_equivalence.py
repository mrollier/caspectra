#!/usr/bin/env python3
"""M2 (EVALUATION_CRITERIA.md rev 11): paired equivalence for "simulation-limited".

The third review (C5/Q7) correctly notes that CI *inclusion* of a separately
estimated benchmark is not an equivalence test. This script performs the
registered paired analysis: on the exact held-out panel, regenerate the
K-replicate target matrix bit-exactly from its registered seed protocol
(``reliability.target_replicates``: base_seed 1000+k, per-rule
``SeedSequence([seed, rule, radius])``), then rule-bootstrap the *same*
resampled rules through both quantities and report, per target, the 95% CI of

    diff = R^2(mechanistic vs cache) - mean_k R^2(replicate_k vs cache).

Both terms are scored against the same cached target vector on the same rules,
so the comparison is paired in both the rules and the truth. The registered
margin is ``margin_t = max(0.01, 1 - ICC_t)`` with ICC_t the published rev-8
latent reliability (read from the run's reliability summary): 1 - ICC is the
maximal noisy-score headroom *any* estimator has over the replicate benchmark,
so differences inside it are scientifically negligible. Wording rule (fixed in
rev 11): "statistically indistinguishable" survives per target iff the 95% CI
lies within +/- margin_t; otherwise the manuscript downgrades to "consistent
with" and prints the CI.

Usage::

    python scripts/validate_paired_equivalence.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES
from caspectra.eval.method_predictions import collect_held_out_predictions
from caspectra.eval.reliability import target_replicates
from caspectra.utils import ensure_dir, save_json, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="M2 paired equivalence (rev 11).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--n-replicates", type=int, default=20)
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument(
        "--reliability-summary",
        default=None,
        help="reliability/summary.json supplying the published ICC_t for the margins "
        "(default <train.output_dir>/reliability/summary.json).",
    )
    p.add_argument(
        "--output-dir", default=None, help="Default <train.output_dir>/paired_equivalence."
    )
    return p.parse_args()


def _r2(pred: np.ndarray, truth: np.ndarray) -> float:
    total = float(np.sum((truth - truth.mean()) ** 2))
    if total <= 0:
        return float("nan")
    return 1.0 - float(np.sum((truth - pred) ** 2)) / total


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/paired_equivalence")
    set_seed(cfg.seed)
    radius = cfg.data.radius

    rel_path = Path(args.reliability_summary or f"{cfg.train.output_dir}/reliability/summary.json")
    icc = {
        name: float(v["icc"]) for name, v in json.loads(rel_path.read_text())["per_feature"].items()
    }
    margins = {name: max(0.01, 1.0 - icc[name]) for name in TARGET_NAMES}

    hop = collect_held_out_predictions(cfg, args.checkpoint, device=args.device)
    held, mech, cache = hop.held, hop.preds["mechanistic"], hop.true
    print(f"[m2] radius={radius}  {len(held)} held-out rules  K={args.n_replicates}")
    print("[m2] regenerating replicate matrix (registered seeds, bit-exact) ...")

    reps = target_replicates(
        held,
        n_replicates=args.n_replicates,
        width=cfg.data.grid_size,
        n_pairs=cfg.targets.n_pairs,
        ic_density=cfg.targets.ic_density,
        radius=radius,
    )  # (K, N, 4)

    rng = np.random.default_rng(0)
    boot = rng.integers(0, len(held), size=(args.n_boot, len(held)))

    results: dict[str, dict] = {}
    for j, name in enumerate(TARGET_NAMES):
        y, m, rk = cache[:, j], mech[:, j], reps[:, :, j]  # rk: (K, N)
        point_mech = _r2(m, y)
        point_rep = float(np.mean([_r2(rk[k], y) for k in range(rk.shape[0])]))
        diffs = np.empty(args.n_boot)
        for b, idx in enumerate(boot):
            yb, mb, rb = y[idx], m[idx], rk[:, idx]
            tot = float(np.sum((yb - yb.mean()) ** 2))
            if tot <= 0:
                diffs[b] = np.nan
                continue
            r2_mech = 1.0 - float(np.sum((yb - mb) ** 2)) / tot
            r2_rep = 1.0 - float(np.mean(np.sum((yb[None, :] - rb) ** 2, axis=1))) / tot
            diffs[b] = r2_mech - r2_rep
        diffs = diffs[np.isfinite(diffs)]
        ci = [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]
        margin = margins[name]
        results[name] = {
            "r2_mechanistic": round(point_mech, 4),
            "r2_replicate_vs_cache": round(point_rep, 4),
            "paired_diff": round(point_mech - point_rep, 4),
            "diff_ci95": [round(ci[0], 4), round(ci[1], 4)],
            "margin": round(margin, 4),
            "icc": round(icc[name], 4),
            "equivalent": bool(-margin <= ci[0] and ci[1] <= margin),
        }

    summary = {
        "radius": radius,
        "n_held_out": len(held),
        "n_replicates": args.n_replicates,
        "n_pairs": cfg.targets.n_pairs,
        "n_boot": args.n_boot,
        "margin_rule": "max(0.01, 1 - ICC_t), ICC_t from the published rev-8 reliability run",
        "per_target": results,
        "all_equivalent": bool(all(v["equivalent"] for v in results.values())),
    }
    save_json(summary, out / "summary.json")
    for name, v in results.items():
        print(
            f"[m2] {name:>16}: mech {v['r2_mechanistic']:+.4f}  "
            f"replicate {v['r2_replicate_vs_cache']:+.4f}  "
            f"diff {v['paired_diff']:+.4f} CI[{v['diff_ci95'][0]:+.4f},{v['diff_ci95'][1]:+.4f}]  "
            f"margin ±{v['margin']:.4f}  equivalent={v['equivalent']}"
        )
    print(f"[m2] all_equivalent={summary['all_equivalent']}   wrote {out}/summary.json")


if __name__ == "__main__":
    main()
