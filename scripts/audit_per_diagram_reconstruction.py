#!/usr/bin/env python3
"""M4 (EVALUATION_CRITERIA.md rev 11): per-diagram reconstruction audit.

The third review (C2/Q1) asks at which unit the "single diagram" claim holds:
the published coverage and exact-reconstruction rates use one (the first)
diagram per held-out rule, with a small cross-diagram agreement check. This
script makes the claim auditable at both units by running the deterministic
inverter on EVERY held-out diagram: per-diagram table-coverage histogram and
exact-reconstruction rate, next to the per-rule numbers (first-diagram
coverage, union coverage over the rule's diagrams, and the share of rules
whose every diagram reconstructs exactly). Descriptive; no gate (rev-11 M4).

Usage::

    python scripts/audit_per_diagram_reconstruction.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.eval.rule_inference import infer_rule, infer_rule_table
from caspectra.factory import build_dataset
from caspectra.utils import ensure_dir, save_json, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="M4 per-diagram reconstruction audit (rev 11).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", default=None, help="Use this CNN's stored held-out split.")
    p.add_argument(
        "--output-dir", default=None, help="Default <train.output_dir>/per_diagram_audit."
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/per_diagram_audit")
    set_seed(cfg.seed)
    radius = cfg.data.radius

    dataset = build_dataset(cfg.data, training=False)
    reps = np.asarray(dataset.equiv_reps)
    images = dataset.images

    if args.checkpoint:
        import torch

        state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
        held = [int(r) for r in state["holdout_rules"] if int(r) in {int(x) for x in reps}]
    else:
        held = sorted({int(r) for r in reps})

    coverages, exacts = [], []
    per_rule = []
    for r in held:
        idx = np.flatnonzero(reps == r)
        covs, exs, union = [], [], None
        for i in idx:
            rule, cov, _ = infer_rule(images[i], radius)
            covs.append(cov)
            exs.append(rule == int(r))
            _, observed, _ = infer_rule_table(images[i], radius)
            union = observed if union is None else (union | observed)
        coverages.extend(covs)
        exacts.extend(exs)
        per_rule.append(
            {
                "rule": int(r),
                "n_diagrams": int(len(idx)),
                "first_diagram_coverage": round(float(covs[0]), 4),
                "mean_coverage": round(float(np.mean(covs)), 4),
                "union_coverage": round(float(union.mean()), 4),
                "exact_rate": round(float(np.mean(exs)), 4),
            }
        )

    coverages = np.asarray(coverages)
    exacts = np.asarray(exacts, dtype=bool)
    hist_edges = [0.0, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999999, 1.0000001]
    hist, _ = np.histogram(coverages, bins=hist_edges)

    summary = {
        "radius": radius,
        "n_rules": len(held),
        "n_diagrams": int(coverages.size),
        "per_diagram": {
            "exact_reconstruction_rate": round(float(exacts.mean()), 4),
            "coverage_quantiles": {
                q: round(float(np.quantile(coverages, float(q))), 4)
                for q in ("0.01", "0.05", "0.25", "0.5", "0.75", "0.95")
            },
            "full_coverage_share": round(float(np.mean(coverages >= 1.0)), 4),
            "coverage_histogram": {
                f"[{lo},{hi})": int(n) for lo, hi, n in zip(hist_edges[:-1], hist_edges[1:], hist)
            },
        },
        "per_rule": {
            "all_diagrams_exact_share": round(
                float(np.mean([pr["exact_rate"] == 1.0 for pr in per_rule])), 4
            ),
            "first_diagram_full_coverage_share": round(
                float(np.mean([pr["first_diagram_coverage"] >= 1.0 for pr in per_rule])), 4
            ),
            "union_full_coverage_share": round(
                float(np.mean([pr["union_coverage"] >= 1.0 for pr in per_rule])), 4
            ),
            "rules": per_rule,
        },
    }
    save_json(summary, out / "summary.json")
    pd = summary["per_diagram"]
    print(
        f"[m4] {coverages.size} diagrams over {len(held)} rules: "
        f"per-diagram exact {pd['exact_reconstruction_rate']:.4f}, "
        f"full-coverage share {pd['full_coverage_share']:.4f}, "
        f"median coverage {pd['coverage_quantiles']['0.5']:.4f}"
    )
    pr = summary["per_rule"]
    print(
        f"[m4] per-rule: all-diagrams-exact {pr['all_diagrams_exact_share']:.4f}, "
        f"first-diagram-full-coverage {pr['first_diagram_full_coverage_share']:.4f}, "
        f"union-full-coverage {pr['union_full_coverage_share']:.4f}"
    )
    print(f"[m4] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
