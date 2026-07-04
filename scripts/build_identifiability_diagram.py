#!/usr/bin/env python3
"""C4 (EVALUATION_CRITERIA.md rev 8): the identifiability phase diagram.

The second referee's highest-value experiment (concerns 3, 4, 7): rather than a
single rule-recovery percentage, chart *when* the local rule is readable and when
a direct (learned) estimator might help. We degrade the observation along four
axes and, per setting, report rule-table coverage, exact-reconstruction rate, and
the held-out R^2 of the mechanistic inverter, the five-statistic baseline, and the
**frozen** CNN checkpoint. No neural training happens here: the CNN is evaluated
only on axes that preserve its fixed input geometry (observation noise, masking,
IC-density shift); on the row-count axis, which changes the input shape, it is
omitted (and this is stated).

Story the figure tells: with clean, full observation the inverter reconstructs the
rule and reaches the reliability-limited accuracy; as observation is shortened,
masked, corrupted, or drawn off the training IC density, exact reconstruction
falls, the mechanistic estimate degrades, and the frozen CNN degrades more
gracefully — the regime where amortised direct prediction has a rationale.

Usage::

    python scripts/build_identifiability_diagram.py --config configs/lever_a_local.yaml \
        --checkpoint runs/lever_a_local_seed0/checkpoint_final.pt --n-pairs 96
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

from caspectra.ca.eca import ECASimulator
from caspectra.ca.range_ca import RangeCA
from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.baselines import compute_baseline_features
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.identifiability import degrade_diagram, masked_infer_table
from caspectra.eval.rule_inference import complete_table, table_to_rule
from caspectra.factory import build_dataset, build_model
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, select_device, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="C4 identifiability phase diagram (rev 8).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--n-pairs", type=int, default=96, help="MC pairs for sweep simulation.")
    p.add_argument("--max-rules", type=int, default=None, help="Cap held-out rules for speed.")
    p.add_argument("--output-dir", default=None)
    p.add_argument(
        "--write-manuscript-figure",
        action="store_true",
        help="Also write manuscript/figures/identifiability.pdf (primary run only).",
    )
    return p.parse_args()


def _simulate(rule: int, radius: int, width: int, n_pairs: float, density: float, rng):
    if radius == 1:
        return damage_spreading_features(
            rule, width=width, n_pairs=n_pairs, ic_density=density, rng=rng
        )
    return damage_spreading_features(
        simulator=RangeCA(rule, radius), width=width, n_pairs=n_pairs, ic_density=density, rng=rng
    )


def _evolve(rule: int, radius: int, ic: np.ndarray, steps: int) -> np.ndarray:
    sim = ECASimulator(rule) if radius == 1 else RangeCA(rule, radius)
    return sim.evolve(ic, steps)


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/identifiability")
    set_seed(cfg.seed)
    radius, width = cfg.data.radius, cfg.data.grid_size
    density0 = cfg.targets.ic_density

    ds = build_dataset(cfg.data, training=False)
    reps = np.asarray(ds.equiv_reps)
    images = ds.images
    rules = sorted({int(r) for r in reps})
    horizon = images.shape[1]

    targets = load_or_compute_invariant_targets(
        rules,
        width=width,
        ic_density=density0,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=radius,
    )
    true_by_rule = {r: targets[i] for i, r in enumerate(rules)}

    state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    held = [int(r) for r in state["holdout_rules"] if int(r) in set(rules)]
    train_rules = [r for r in rules if r not in set(held)]
    if args.max_rules and len(held) > args.max_rules:
        held = sorted(np.random.default_rng(0).choice(held, args.max_rules, replace=False).tolist())
    print(
        f"[c4] radius={radius} width={width} horizon={horizon} "
        f"held={len(held)} n_pairs={args.n_pairs}"
    )

    # Frozen CNN + fitted five-statistic baseline (trained on clean train rules).
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    device = select_device(prefer=args.device)
    model = model.to(device).eval()
    s_mean, s_std = state["scaler_mean"], state["scaler_std"]

    feats_all = compute_baseline_features(images, radius=radius)
    tr = np.isin(reps, train_rules)
    scaler = StandardScaler().fit(feats_all[tr])
    y = np.stack([true_by_rule[int(r)] for r in reps])
    gbms = [
        GradientBoostingRegressor(random_state=0).fit(scaler.transform(feats_all[tr]), y[tr, j])
        for j in range(len(TARGET_NAMES))
    ]

    held_diag = {r: images[np.flatnonzero(reps == r)[0]] for r in held}
    true_held = np.stack([true_by_rule[r] for r in held])

    def _rng(r, tag):
        return np.random.default_rng(
            np.random.SeedSequence([int(cfg.targets.seed) + 104729, int(r), tag])
        )

    @torch.no_grad()
    def _cnn_r2(degraded: dict[int, np.ndarray]) -> float:
        preds = []
        for r in held:
            b = (
                torch.from_numpy(degraded[r].astype(np.float32))
                .unsqueeze(0)
                .unsqueeze(0)
                .to(device)
            )
            preds.append(model(b).cpu().numpy()[0] * s_std + s_mean)
        return float(np.nanmedian(r2_per_feature(np.stack(preds), true_held)))

    def _baseline_r2(degraded: dict[int, np.ndarray]) -> float:
        f = scaler.transform(
            compute_baseline_features(np.stack([degraded[r] for r in held]), radius=radius)
        )
        preds = np.stack([g.predict(f) for g in gbms], axis=1)
        return float(np.nanmedian(r2_per_feature(preds, true_held)))

    def _mech(degraded, observed_masks, tag):
        """Coverage, exact-reconstruction rate, mechanistic median R^2."""
        preds, covs, exact = [], [], []
        for r in held:
            table, obs = masked_infer_table(degraded[r], radius, observed_masks.get(r))
            rule = table_to_rule(complete_table(table, obs, "zero"))
            preds.append(_simulate(rule, radius, width, args.n_pairs, density0, _rng(r, tag)))
            covs.append(float(obs.mean()))
            exact.append(rule == r)
        r2 = float(np.nanmedian(r2_per_feature(np.stack(preds), true_held)))
        return r2, float(np.mean(covs)), float(np.mean(exact))

    sweeps: dict[str, dict] = {}

    # Axis 1: number of observed rows (CNN omitted: variable input geometry).
    rows = [r for r in [4, 6, 8, 12, 16, 24, horizon] if r <= horizon]
    rec = {"values": rows, "coverage": [], "exact": [], "mechanistic": []}
    for h in rows:
        deg = {r: held_diag[r][:h] for r in held}
        r2, cov, ex = _mech(deg, {}, tag=100 + h)
        rec["coverage"].append(round(cov, 4))
        rec["exact"].append(round(ex, 4))
        rec["mechanistic"].append(round(r2, 4))
    sweeps["rows"] = rec

    # Axis 2: observation (bit-flip) noise. Geometry preserved -> all three methods.
    noise = [0.0, 0.01, 0.02, 0.05, 0.10, 0.20]
    rec = {
        "values": noise,
        "coverage": [],
        "exact": [],
        "mechanistic": [],
        "baseline": [],
        "cnn": [],
    }
    for p in noise:
        deg = {r: degrade_diagram(held_diag[r], flip_p=p, rng=_rng(r, 200))[0] for r in held}
        r2, cov, ex = _mech(deg, {}, tag=200)
        rec["coverage"].append(round(cov, 4))
        rec["exact"].append(round(ex, 4))
        rec["mechanistic"].append(round(r2, 4))
        rec["baseline"].append(round(_baseline_r2(deg), 4))
        rec["cnn"].append(round(_cnn_r2(deg), 4))
    sweeps["noise"] = rec

    # Axis 3: partial observation (masking). Geometry preserved -> all three methods.
    masks = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9]
    rec = {
        "values": masks,
        "coverage": [],
        "exact": [],
        "mechanistic": [],
        "baseline": [],
        "cnn": [],
    }
    for p in masks:
        deg, obsm = {}, {}
        for r in held:
            d, o = degrade_diagram(held_diag[r], mask_p=p, rng=_rng(r, 300))
            deg[r] = (
                d if o is None else (d * o).astype(np.uint8)
            )  # CNN sees zero-filled masked cells
            if o is not None:
                obsm[r] = o
        r2, cov, ex = _mech(deg, obsm, tag=300)
        rec["coverage"].append(round(cov, 4))
        rec["exact"].append(round(ex, 4))
        rec["mechanistic"].append(round(r2, 4))
        rec["baseline"].append(round(_baseline_r2(deg), 4))
        rec["cnn"].append(round(_cnn_r2(deg), 4))
    sweeps["mask"] = rec

    # Axis 4: IC-density shift. Regenerate diagrams at density p (CNN trained at density0).
    dens = [0.1, 0.25, density0, 0.75, 0.9]
    rec = {
        "values": dens,
        "coverage": [],
        "exact": [],
        "mechanistic": [],
        "baseline": [],
        "cnn": [],
    }
    for p in dens:
        deg = {}
        for r in held:
            ic = (_rng(r, 400).random(width) < p).astype(np.uint8)
            deg[r] = _evolve(r, radius, ic, horizon)
        r2, cov, ex = _mech(deg, {}, tag=401)
        rec["coverage"].append(round(cov, 4))
        rec["exact"].append(round(ex, 4))
        rec["mechanistic"].append(round(r2, 4))
        rec["baseline"].append(round(_baseline_r2(deg), 4))
        rec["cnn"].append(round(_cnn_r2(deg), 4))
    sweeps["density"] = rec

    save_json(
        {
            "radius": radius,
            "width": width,
            "horizon": horizon,
            "n_held": len(held),
            "n_pairs": args.n_pairs,
            "sweeps": sweeps,
        },
        out / "summary.json",
    )

    # Figure: four panels.
    fig, ax = plt.subplots(2, 2, figsize=(9.5, 7.0))
    a = ax[0, 0]
    a.plot(
        rows := sweeps["rows"]["values"],
        sweeps["rows"]["exact"],
        "o-",
        label="exact reconstruction",
    )
    a.plot(rows, sweeps["rows"]["coverage"], "s--", color="gray", label="table coverage")
    a.plot(rows, sweeps["rows"]["mechanistic"], "^-", color="C2", label="mechanistic $R^2$")
    a.set_xlabel("observed rows (time steps)")
    a.set_ylabel("value")
    a.set_title("(a) observation length")
    a.legend(fontsize=7)
    a.set_ylim(-0.05, 1.05)

    for key, panel, xlabel, title in [
        ("noise", ax[0, 1], "bit-flip observation noise", "(b) observation noise"),
        ("mask", ax[1, 0], "masked-cell fraction", "(c) partial observation"),
        ("density", ax[1, 1], "IC density", "(d) IC-density shift"),
    ]:
        s = sweeps[key]
        panel.plot(s["values"], s["mechanistic"], "^-", color="C2", label="mechanistic")
        panel.plot(s["values"], s["baseline"], "s-", color="C1", label="5 statistics")
        panel.plot(s["values"], s["cnn"], "o-", color="C0", label="frozen CNN")
        panel.plot(s["values"], s["exact"], ":", color="gray", label="exact recon.")
        panel.set_xlabel(xlabel)
        panel.set_ylabel("median held-out $R^2$")
        panel.set_title(title)
        panel.legend(fontsize=7)
        panel.set_ylim(-0.05, 1.05)
        if key == "density":
            panel.axvline(density0, color="k", lw=0.6, ls=":")

    fig.suptitle(f"Identifiability of the local rule (radius {radius})", fontsize=11)
    fig.tight_layout()
    fig.savefig(out / "identifiability.pdf")
    if args.write_manuscript_figure:
        fig.savefig("manuscript/figures/identifiability.pdf")
    print(f"[c4] wrote {out}/summary.json and {out}/identifiability.pdf")
    for k, s in sweeps.items():
        print(f"[c4] {k:>8}: mechanistic {s['mechanistic']}")
        if "cnn" in s:
            print(f"[c4] {'':>8}  cnn        {s['cnn']}  baseline {s['baseline']}")


if __name__ == "__main__":
    main()
