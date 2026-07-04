#!/usr/bin/env python3
"""R3 (rev 7) + C2 (rev 8): reliability benchmarks, correctly distinguished.

Draws ``K`` independent Monte-Carlo target replicates per rule and reports, per
target, **two** distinguished quantities with rule-bootstrap CIs (rev-8 C2):

* the **latent-target reliability** ICC(1) — the ceiling for a predictor of the
  noise-free target mean; and
* the **independent-replicate agreement** (expectation ``2*ICC-1``) — the ceiling
  for an estimator that returns a *fresh independent* MC draw, which is exactly
  what the mechanistic estimator does.

The second referee (concern 2) showed the old code conflated these: the
mechanistic estimator must be judged against the replicate agreement, not ICC.
This replaces the "MC noise 0.006-0.014 upper-bounds R^2" claim with a proper
signal-vs-noise decomposition and the correct estimator-specific benchmark.

Usage::

    python scripts/validate_reliability.py --config configs/lever_a_local.yaml
    python scripts/validate_reliability.py --config configs/m4_range2.yaml --n-replicates 20
"""

from __future__ import annotations

import argparse

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.eval.reliability import reliability_benchmarks, target_replicates
from caspectra.factory import build_dataset
from caspectra.utils import ensure_dir, save_json, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R3/C2 reliability benchmarks (rev 7/8).")
    p.add_argument("--config", required=True, help="Path to the YAML ExperimentConfig.")
    p.add_argument("--n-replicates", type=int, default=20, help="K independent MC replicates.")
    p.add_argument("--max-rules", type=int, default=None, help="Subsample rules (ICC is stable).")
    p.add_argument("--n-boot", type=int, default=2000, help="Rule-bootstrap resamples for CIs.")
    p.add_argument("--output-dir", default=None, help="Default <train.output_dir>/reliability.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/reliability")
    set_seed(cfg.seed)
    radius = cfg.data.radius

    dataset = build_dataset(cfg.data, training=False)
    rules = sorted({int(r) for r in np.asarray(dataset.equiv_reps)})
    if args.max_rules is not None and len(rules) > args.max_rules:
        # Representative subsample: the ICC ratio is stable across rules spanning
        # the full behaviour landscape (fixed RNG so the subset is reproducible).
        rules = sorted(
            np.random.default_rng(0).choice(rules, args.max_rules, replace=False).tolist()
        )
    print(
        f"[r3] radius={radius}  {len(rules)} rules  K={args.n_replicates} replicates  "
        f"n_pairs={cfg.targets.n_pairs}"
    )

    reps = target_replicates(
        rules,
        n_replicates=args.n_replicates,
        width=cfg.data.grid_size,
        n_pairs=cfg.targets.n_pairs,
        ic_density=cfg.targets.ic_density,
        radius=radius,
    )
    bench = reliability_benchmarks(reps, n_boot=args.n_boot)

    median_icc = float(np.nanmedian([v["icc"] for v in bench.values()]))
    median_agreement = float(np.nanmedian([v["agreement_r2"] for v in bench.values()]))
    summary = {
        "radius": radius,
        "n_rules": len(rules),
        "n_replicates": args.n_replicates,
        "n_pairs": cfg.targets.n_pairs,
        "n_boot": args.n_boot,
        "per_feature": bench,
        "median_icc_ceiling": round(median_icc, 4),
        "median_replicate_agreement": round(median_agreement, 4),
    }
    save_json(summary, out / "summary.json")

    for name, v in bench.items():
        print(
            f"[c2] {name:>16}: ICC {v['icc']:.4f} CI{v['icc_ci']}  "
            f"| indep-replicate agreement {v['agreement_r2']:.4f} CI{v['agreement_ci']} "
            f"(2*ICC-1={v['two_icc_minus_one']:.4f}; MC-noise std {v['mc_noise_std']:.4f})"
        )
    print(
        f"[c2] median: ICC ceiling {median_icc:.4f}  |  "
        f"replicate-agreement benchmark {median_agreement:.4f}"
    )
    print(f"[c2] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
