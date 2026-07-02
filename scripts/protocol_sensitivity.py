#!/usr/bin/env python3
"""Measure how sensitive the dynamical taxonomy is to the observation protocol.

FOUNDATIONS.md §1: what this repo classifies is a *(rule orbit, IC measure,
lattice, horizon)* tuple — the literature (Gilman 1987; Culik & Yu 1988) shows
"the class of a rule" is not defined without fixing those. This script measures
that dependence for our damage-spreading features (EVALUATION_CRITERIA.md
criterion 5) instead of assuming it away:

* **IC-density sweep** p ∈ {0.1, 0.25, 0.5, 0.75, 0.9} at width 127;
* **width sweep** {63, 127, 255} at p = 0.5 (horizon scales as width//2 − 1);
* per-feature Spearman ρ and cluster-assignment ARI vs the reference protocol
  (p = 0.5, width 127), with the criterion-5 gate evaluated on p ∈ {0.25, 0.75};
* the list of rules whose *assigned Wolfram class* (majority class of their
  cluster) flips across protocols — density-dependent behaviour (e.g. rule 184)
  is a finding to report, never to hide;
* a **seed control**: the reference protocol recomputed with a different RNG
  seed, reported first — it is the *sampling floor* every cross-protocol ARI
  must be read against (at n_pairs = 32 the floor was ≈ 0.4, which is why the
  default is now 128: fine partitions need well-estimated features);
* a **bootstrap** of the borderline calls (rules 41 and 106): mean ± std of the
  features over 10 seeds at n_pairs = 256, to separate signal from small-sample
  noise.

Outputs: ``features.csv``, ``stability_summary.txt`` and ``sensitivity.png`` in
``runs/analysis/protocol_sensitivity/``. Pure CPU simulation; no model needed.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.cluster import AgglomerativeClustering  # noqa: E402
from sklearn.metrics import adjusted_rand_score  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from caspectra.ca.eca import independent_rules  # noqa: E402
from caspectra.eval.dynamics import (  # noqa: E402
    DYNAMICS_FEATURE_NAMES,
    damage_spreading_features,
    dynamics_feature_matrix,
)
from caspectra.eval.labels import load_rule_labels  # noqa: E402
from caspectra.utils import ensure_dir  # noqa: E402

REFERENCE = ("p=0.5", 0.5, 127)
DENSITY_SWEEP = [0.1, 0.25, 0.5, 0.75, 0.9]
WIDTH_SWEEP = [63, 127, 255]
GATED_DENSITIES = {0.25, 0.75}  # criterion-5 gate; extremes are context only
K_CLUSTERS = 14  # granularity at which the reference protocol isolates {54,106,110}
BOOTSTRAP_RULES = [54, 110, 106, 41, 30, 60]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n-pairs", type=int, default=128, help="IC pairs per rule/protocol.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-dir", default="runs/analysis/protocol_sensitivity")
    parser.add_argument(
        "--skip-bootstrap", action="store_true", help="Skip the borderline bootstrap (faster)."
    )
    return parser.parse_args()


def assigned_class(features: np.ndarray, wolfram: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Cluster the standardized features; return (cluster labels, per-rule majority class)."""
    z = StandardScaler().fit_transform(features)
    lab = AgglomerativeClustering(n_clusters=K_CLUSTERS).fit_predict(z)
    owner = {}
    for c in np.unique(lab):
        vals, counts = np.unique(wolfram[lab == c], return_counts=True)
        owner[int(c)] = int(vals[np.argmax(counts)])
    return lab, np.array([owner[int(c)] for c in lab])


def main() -> None:
    args = parse_args()
    out = ensure_dir(args.output_dir)
    rules = np.array(independent_rules())
    labels = load_rule_labels("rule_labels.csv")
    if labels is None:
        raise SystemExit("rule_labels.csv not found — run from the repository root.")
    wolfram = labels.wolfram_array(rules)

    protocols = [(f"p={p}", p, 127) for p in DENSITY_SWEEP]
    protocols += [(f"w={w}", 0.5, w) for w in WIDTH_SWEEP if w != 127]

    features: dict[str, np.ndarray] = {}
    for name, p, width in protocols:
        features[name] = dynamics_feature_matrix(
            rules, width=width, n_pairs=args.n_pairs, ic_density=p, seed=args.seed
        )
        print(f"[protocol] computed {name} (width={width})")

    ref = features[REFERENCE[0]]
    ref_lab, ref_class = assigned_class(ref, wolfram)

    # Long-format CSV: one row per (protocol, rule).
    with (out / "features.csv").open("w") as f:
        f.write("protocol,rule,wolfram," + ",".join(DYNAMICS_FEATURE_NAMES) + "\n")
        for name, _, _ in protocols:
            for i, r in enumerate(rules):
                vals = ",".join(f"{v:.6f}" for v in features[name][i])
                f.write(f"{name},{r},{wolfram[i]},{vals}\n")

    lines: list[str] = []

    def report(msg: str) -> None:
        print(msg)
        lines.append(msg)

    report(f"reference protocol: {REFERENCE[0]}, width {REFERENCE[2]}, n_pairs={args.n_pairs}")
    report(
        "criterion 5 gate (EVALUATION_CRITERIA.md rev 2): Spearman rho >= 0.8 per feature "
        "and ARI >= 0.6, on p in {0.25, 0.75}"
    )

    # Seed control: same protocol, different seed = the sampling floor for ARI.
    control = dynamics_feature_matrix(
        rules,
        width=REFERENCE[2],
        n_pairs=args.n_pairs,
        ic_density=REFERENCE[1],
        seed=args.seed + 1,
    )
    ctrl_lab, _ = assigned_class(control, wolfram)
    ctrl_ari = adjusted_rand_score(ref_lab, ctrl_lab)
    report(
        f"seed control (same protocol, seed {args.seed + 1}): ARI={ctrl_ari:.2f} — "
        "cross-protocol ARIs below must be read against this sampling floor"
    )

    gate_ok = True
    rho_table: dict[str, list[float]] = {}
    for name, p, width in protocols:
        if name == REFERENCE[0]:
            continue
        rhos = []
        for j, feat in enumerate(DYNAMICS_FEATURE_NAMES):
            rho = spearmanr(ref[:, j], features[name][:, j]).statistic
            rhos.append(float(rho) if np.isfinite(rho) else float("nan"))
        rho_table[name] = rhos
        lab, cls = assigned_class(features[name], wolfram)
        ari = adjusted_rand_score(ref_lab, lab)
        flips = rules[cls != ref_class]
        gated = p in GATED_DENSITIES and width == 127
        gate_str = ""
        if gated:
            ok = all(r >= 0.8 for r in rhos if np.isfinite(r)) and ari >= 0.6
            gate_ok &= ok
            gate_str = f"  [criterion 5: {'PASS' if ok else 'FAIL'}]"
        report(
            f"{name:>7}: rho="
            + "/".join(f"{r:.2f}" for r in rhos)
            + f"  ARI vs ref={ari:.2f}  class-flips={flips.tolist()}"
            + gate_str
        )
        iv_members = rules[lab == lab[int(np.where(rules == 54)[0][0])]]
        report(f"         rule 54's cluster: {iv_members.tolist()}")
    report(f"criterion 5 overall (gated protocols only): {'PASS' if gate_ok else 'FAIL'}")

    # Bootstrap of the borderline calls at the reference protocol.
    if not args.skip_bootstrap:
        report("\nbootstrap at reference protocol (10 seeds x n_pairs=256):")
        for r in BOOTSTRAP_RULES:
            samples = np.stack(
                [
                    damage_spreading_features(
                        r,
                        width=127,
                        n_pairs=256,
                        ic_density=0.5,
                        rng=np.random.default_rng(1000 + s),
                    )
                    for s in range(10)
                ]
            )
            mean, std = samples.mean(axis=0), samples.std(axis=0)
            report(
                f"  rule {r:>3}: "
                + "  ".join(
                    f"{n}={m:.3f}+/-{s:.3f}" for n, m, s in zip(DYNAMICS_FEATURE_NAMES, mean, std)
                )
            )

    (out / "stability_summary.txt").write_text("\n".join(lines) + "\n")

    # Figure: rho heatmap + rate-vs-fill scatter across gated densities.
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    names = [n for n, _, _ in protocols if n != REFERENCE[0]]
    mat = np.array([rho_table[n] for n in names])
    im = axes[0].imshow(mat, vmin=0, vmax=1, cmap="viridis", aspect="auto")
    axes[0].set_xticks(range(len(DYNAMICS_FEATURE_NAMES)), DYNAMICS_FEATURE_NAMES, rotation=30)
    axes[0].set_yticks(range(len(names)), names)
    axes[0].set_title(f"Spearman rho vs reference ({REFERENCE[0]}, w=127)")
    fig.colorbar(im, ax=axes[0])
    markers = {0.25: "o", 0.5: "s", 0.75: "^"}
    for p, m in markers.items():
        feats = features[f"p={p}"]
        chaotic = wolfram == 3
        axes[1].scatter(
            feats[chaotic, 2],
            feats[chaotic, 3],
            marker=m,
            s=25,
            alpha=0.5,
            color="#C8651B",
            label=f"chaotic p={p}",
        )
        for r, col in ((54, "#C0392B"), (110, "#8E44AD"), (106, "#2C3E50")):
            i = int(np.where(rules == r)[0][0])
            axes[1].scatter(
                feats[i, 2], feats[i, 3], marker=m, s=90, color=col, edgecolors="k", zorder=3
            )
            axes[1].annotate(
                f"{r}",
                (feats[i, 2], feats[i, 3]),
                fontsize=7,
                xytext=(4, 3),
                textcoords="offset points",
            )
    axes[1].set_xlabel("spreading rate")
    axes[1].set_ylabel("cone fill")
    axes[1].set_title("{54, 110, 106} vs chaotic rules across IC densities")
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "sensitivity.png", dpi=120)
    print(f"[protocol] artifacts in {out.resolve()}")


if __name__ == "__main__":
    main()
