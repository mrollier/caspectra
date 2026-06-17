#!/usr/bin/env python3
"""Evaluate a trained checkpoint (BUILD_BRIEF.md §3.6-3.8, §6).

Loads a checkpoint, extracts frozen-encoder embeddings for the dataset, then
runs: the linear probes (rule / LP / Wolfram), the UMAP+HDBSCAN clustering with
ARI/NMI/purity and the genotype/phenotype MI diagnostic, and the visualisations
(3-panel UMAP scatter + per-cluster sample grids).

Example
-------
    PYTORCH_ENABLE_MPS_FALLBACK=1 python scripts/evaluate.py \
        --config configs/smoke.yaml --checkpoint runs/smoke/checkpoint_final.pt
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import torch

from caspectra.config import ExperimentConfig
from caspectra.eval.baselines import FEATURE_NAMES, compute_baseline_features
from caspectra.eval.cluster import (
    cluster_count_stability,
    cluster_pipeline,
    contingency_table,
    umap_project,
)
from caspectra.eval.embed import extract_embeddings
from caspectra.eval.labels import load_rule_labels
from caspectra.eval.probes import run_probes
from caspectra.eval.visualize import save_per_cluster_samples, scatter_three_panel
from caspectra.factory import build_dataloader, build_dataset, build_model
from caspectra.utils import ensure_dir, save_json, select_device, set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained checkpoint.")
    parser.add_argument("--config", required=True, help="Path to a YAML ExperimentConfig.")
    parser.add_argument("--checkpoint", default=None, help="Override eval.checkpoint.")
    parser.add_argument("--device", default="mps", help="Preferred device (mps/cpu/cuda).")
    parser.add_argument("--output-dir", default=None, help="Override eval.output_dir.")
    return parser.parse_args()


def _write_contingency(path: Path, table, rows, cols, row_name: str) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([row_name, *[f"class_{c}" for c in cols]])
        for r, counts in zip(rows, table):
            writer.writerow([f"cluster_{r}", *counts.tolist()])


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    checkpoint = args.checkpoint or cfg.eval.checkpoint
    output_dir = ensure_dir(args.output_dir or cfg.eval.output_dir)

    set_seed(cfg.seed)
    device = select_device(prefer=args.device)
    print(f"[eval] device={device} checkpoint={checkpoint}")

    # Dataset for embedding extraction: no augmentation (raw images).
    dataset = build_dataset(cfg.data, training=False)
    loader = build_dataloader(
        dataset,
        batch_size=cfg.eval.batch_size,
        shuffle=False,
        num_workers=cfg.train.num_workers,
    )

    model = build_model(cfg.model)
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model.load_state_dict(state["model_state"])

    embeddings, rules, _reps = extract_embeddings(model, loader, device)
    np.savez_compressed(output_dir / "embeddings.npz", embeddings=embeddings, rules=rules)
    print(f"[eval] extracted {embeddings.shape[0]} embeddings of dim {embeddings.shape[1]}")

    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    if labels is None:
        print(
            f"[eval] WARNING: {cfg.eval.rule_labels_csv} not found; "
            "skipping LP/Wolfram probes & metrics (rule probe still runs)."
        )

    # --- Linear probes (lead evaluation) ---
    probe_report = run_probes(embeddings, rules, labels, seed=cfg.seed)
    probe_report.to_csv(output_dir / "probes.csv")
    print(probe_report.summary())

    # --- Hand-crafted baseline: the embedding must beat cheap descriptors ---
    baseline_features = compute_baseline_features(dataset.images)
    baseline_report = run_probes(baseline_features, rules, labels, seed=cfg.seed)
    baseline_report.to_csv(output_dir / "probes_baseline.csv")
    print("[eval] hand-crafted baseline (" + ", ".join(FEATURE_NAMES) + "):")
    print(baseline_report.summary())
    if probe_report.gap is not None and baseline_report.gap is not None:
        verdict = "beats" if probe_report.gap > baseline_report.gap else "does NOT beat"
        print(
            f"[eval] gap — embedding {probe_report.gap:+.3f} vs baseline "
            f"{baseline_report.gap:+.3f}: embedding {verdict} the baseline."
        )

    # --- Clustering + diagnostic ---
    cluster_report = cluster_pipeline(
        embeddings,
        umap_components=cfg.eval.umap_components,
        umap_metric=cfg.eval.umap_metric,
        min_cluster_size=cfg.eval.hdbscan_min_cluster_size,
        min_samples=cfg.eval.hdbscan_min_samples,
        seed=cfg.seed,
        rules=rules,
        labels=labels,
    )
    print(cluster_report.summary())
    (output_dir / "cluster_summary.txt").write_text(cluster_report.summary())

    # Cluster-count stability: the count is a hyperparameter, not a constant.
    base_mcs = cfg.eval.hdbscan_min_cluster_size
    sweep = cluster_count_stability(
        embeddings,
        sorted({max(2, base_mcs // 2), base_mcs, base_mcs * 2}),
        umap_components=cfg.eval.umap_components,
        umap_metric=cfg.eval.umap_metric,
        min_samples=cfg.eval.hdbscan_min_samples,
        seed=cfg.seed,
    )
    print("[eval] cluster-count stability (min_cluster_size -> n_clusters): " + str(sweep))

    # Contingency tables (when labels available).
    if labels is not None and labels.has_lp:
        lp = labels.lp_array(rules)
        mask = lp >= 0
        table, crows, ccols = contingency_table(cluster_report.umap_labels[mask], lp[mask])
        _write_contingency(output_dir / "contingency_lp.csv", table, crows, ccols, "cluster")

    # --- Visualisation ---
    coords2d = umap_project(embeddings, n_components=2, metric=cfg.eval.umap_metric, seed=cfg.seed)
    lp_array = labels.lp_array(rules) if (labels and labels.has_lp) else None
    scatter_three_panel(
        coords2d, rules, lp_array, cluster_report.umap_labels, output_dir / "umap_scatter.png"
    )
    grid_paths = save_per_cluster_samples(
        dataset.images,
        cluster_report.umap_labels,
        embeddings,
        out_dir=output_dir / "cluster_samples",
    )

    save_json(
        {
            "rule_probe_acc": probe_report.rule.accuracy,
            "rule_probe_balanced_acc": probe_report.rule.balanced_accuracy,
            "rule_probe_baseline": probe_report.rule.baseline,
            "lp_probe_acc": probe_report.lp.accuracy if probe_report.lp else None,
            "wolfram_probe_acc": probe_report.wolfram.accuracy if probe_report.wolfram else None,
            "probe_gap": probe_report.gap,
            "baseline_probe_gap": baseline_report.gap,
            "n_clusters": cluster_report.n_clusters,
            "n_noise": cluster_report.n_noise,
            "cluster_count_stability": sweep,
            "mi_rule": cluster_report.mi_rule,
            "mi_lp": cluster_report.mi_lp,
            "excess_rule_info_mi_cluster_rule_given_lp": cluster_report.mi_rule_given_lp,
            "metrics_lp": cluster_report.metrics_lp,
            "metrics_wolfram": cluster_report.metrics_wolfram,
        },
        output_dir / "summary.json",
    )
    print(f"[eval] wrote {len(grid_paths)} cluster sample grids")
    print(f"[eval] artifacts in {output_dir.resolve()}")


if __name__ == "__main__":
    main()
