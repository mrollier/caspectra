#!/usr/bin/env python3
"""F3 (EVALUATION_CRITERIA.md rev 9): the identifiability-frontier grid.

Compares every registered estimator on degraded observations of the rev-8
identifiability panel: the deterministic inverter, the F1 Bayesian
rule-posterior simulator (eps known / eps self-consistency-estimated), the
frozen direct CNN, the five-statistic GBM, a train-rule-fitted stats+CNN stack,
and (when ``--reader-checkpoint`` is given) the F2 learned rule-reader ->
simulator in MAP and sampled variants. Axes: bit-flip noise (dense), masking,
IC density, state-label (polarity) noise, and unknown radius. Per cell: median
held-out R^2 per estimator (with rule-bootstrap CIs on the leaders), exact
reconstruction / per-bit accuracy, and for the radius axis the selected-radius
distribution.

Numbers only after the rev-9 registration commit; no training happens here.

Usage::

    python scripts/build_frontier_grid.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt --max-rules 80
"""

from __future__ import annotations

import argparse
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from caspectra.ca.eca import ECASimulator
from caspectra.ca.range_ca import RangeCA, embed_eca
from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.baselines import compute_baseline_features
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.identifiability import (
    degrade_diagram,
    masked_transition_counts,
    project_table_radius3_to_2,
    select_radius,
)
from caspectra.eval.rule_inference import (
    complete_table,
    noisy_table_posterior,
    table_to_rule,
)
from caspectra.factory import build_dataset, build_model
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, select_device, set_seed

warnings.filterwarnings("ignore", message=".*encountered in matmul")

NOISE = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20]
MASK = [0.0, 0.10, 0.25, 0.40, 0.50, 0.75, 0.90]
DENSITY = [0.1, 0.25, 0.5, 0.75, 0.9]
LABEL_FLIP = [0.0, 0.5, 1.0]
RADIUS_NOISE = [0.0, 0.01, 0.02, 0.05]  # unknown-radius axis, at these noise levels


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="F3 identifiability-frontier grid (rev 9).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True, help="Frozen direct-CNN checkpoint.")
    p.add_argument("--reader-checkpoint", default=None, help="F2 rule-reader checkpoint.")
    p.add_argument("--device", default="mps")
    p.add_argument("--n-pairs", type=int, default=48, help="MC pairs per simulation.")
    p.add_argument("--n-samples", type=int, default=8, help="Posterior table samples (F1/F2).")
    p.add_argument("--max-rules", type=int, default=80)
    p.add_argument("--n-boot", type=int, default=2000)
    p.add_argument("--axes", nargs="*", default=["noise", "mask", "density", "label", "radius"])
    p.add_argument("--output-dir", default=None)
    p.add_argument("--write-figure", action="store_true", help="Write manuscript figure.")
    return p.parse_args()


def main() -> None:  # noqa: C901 - one orchestration function, sectioned below
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/frontier_grid")
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
        # Same subsample rule as the rev-8 identifiability run (fixed seed 0).
        held = sorted(np.random.default_rng(0).choice(held, args.max_rules, replace=False).tolist())
    held_diag = {r: images[np.flatnonzero(reps == r)[0]] for r in held}
    true_held = np.stack([true_by_rule[r] for r in held])
    true_tables = {r: np.array([(r >> k) & 1 for k in range(1 << (2 * radius + 1))]) for r in held}
    print(
        f"[f3] radius={radius} width={width} held={len(held)} "
        f"n_pairs={args.n_pairs} n_samples={args.n_samples} axes={args.axes}"
    )

    # --- Frozen direct CNN + train-fitted baseline & stack. --------------------
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

    @torch.no_grad()
    def cnn_preds(diagrams: dict[int, np.ndarray]) -> np.ndarray:
        outp = []
        for r in held:
            b = torch.from_numpy(diagrams[r].astype(np.float32))[None, None].to(device)
            outp.append(model(b).cpu().numpy()[0] * s_std + s_mean)
        return np.stack(outp)

    def gbm_preds(diagrams: dict[int, np.ndarray]) -> np.ndarray:
        f = scaler.transform(
            compute_baseline_features(np.stack([diagrams[r] for r in held]), radius=radius)
        )
        return np.stack([g.predict(f) for g in gbms], axis=1)

    # Stats+CNN stack, fitted on TRAIN rules' clean diagrams only (deployable hybrid).
    with torch.no_grad():
        cnn_tr = []
        for i in np.flatnonzero(tr):
            b = torch.from_numpy(images[i].astype(np.float32))[None, None].to(device)
            cnn_tr.append(model(b).cpu().numpy()[0] * s_std + s_mean)
    stack_X_tr = np.hstack([scaler.transform(feats_all[tr]), np.stack(cnn_tr)])
    stack_models = [Ridge(alpha=1.0).fit(stack_X_tr, y[tr, j]) for j in range(len(TARGET_NAMES))]

    def stack_preds(diagrams: dict[int, np.ndarray]) -> np.ndarray:
        f = scaler.transform(
            compute_baseline_features(np.stack([diagrams[r] for r in held]), radius=radius)
        )
        X = np.hstack([f, cnn_preds(diagrams)])
        return np.stack([m.predict(X) for m in stack_models], axis=1)

    # --- Optional F2 learned rule-reader. --------------------------------------
    reader = None
    if args.reader_checkpoint:
        from caspectra.models.rule_reader import load_rule_reader

        reader = load_rule_reader(args.reader_checkpoint, device)

    def _rng(r: int, tag: int) -> np.random.Generator:
        return np.random.default_rng(
            np.random.SeedSequence([int(cfg.targets.seed) + 224747, int(r), tag])
        )

    def simulate(rule_number: int, rr: int, gen) -> np.ndarray:
        if rr == 1:
            return damage_spreading_features(
                rule_number, width=width, n_pairs=args.n_pairs, ic_density=density0, rng=gen
            )
        return damage_spreading_features(
            simulator=RangeCA(rule_number, rr),
            width=width,
            n_pairs=args.n_pairs,
            ic_density=density0,
            rng=gen,
        )

    # --- Estimators (each returns preds (N,4) + diagnostics). ------------------
    def det_estimate(diagrams, masks, tag):
        preds, exact = [], []
        for r in held:
            ones, total = masked_transition_counts(diagrams[r], radius, masks.get(r))
            obs = total > 0
            table = (2 * ones > total).astype(np.uint8)
            rule = table_to_rule(complete_table(table, obs, "zero"))
            exact.append(rule == r)
            preds.append(simulate(rule, radius, _rng(r, tag)))
        return np.stack(preds), {"exact": float(np.mean(exact))}

    def f1_estimate(diagrams, masks, tag, eps=None):
        preds, exact, bitacc = [], [], []
        for r in held:
            ones, total = masked_transition_counts(diagrams[r], radius, masks.get(r))
            if eps is None:
                seen = total > 0
                if seen.any():
                    minority = np.minimum(ones[seen], total[seen] - ones[seen])
                    disagree = float(minority.sum() / total[seen].sum())
                else:
                    disagree = 0.0
                from caspectra.eval.rule_inference import EPS_GRID

                e = float(min(EPS_GRID, key=lambda v: abs(v - disagree)))
            else:
                e = float(eps)
            p_bits = noisy_table_posterior(ones, total, e)
            map_table = (p_bits >= 0.5).astype(np.uint8)
            exact.append(table_to_rule(map_table) == r)
            bitacc.append(float(np.mean(map_table == true_tables[r])))
            gen = _rng(r, tag)
            sims = []
            for _ in range(args.n_samples):
                tbl = (gen.random(p_bits.shape[0]) < p_bits).astype(np.uint8)
                sims.append(simulate(table_to_rule(tbl), radius, gen))
            preds.append(np.mean(sims, axis=0))
        return np.stack(preds), {
            "exact": float(np.mean(exact)),
            "bit_accuracy": float(np.mean(bitacc)),
        }

    def f2_estimate(diagrams, tag, sampled: bool):
        assert reader is not None
        preds, exact, bitacc = [], [], []
        for r in held:
            p_bits = reader.predict_bits(diagrams[r])
            map_table = (p_bits >= 0.5).astype(np.uint8)
            exact.append(table_to_rule(map_table) == r)
            bitacc.append(float(np.mean(map_table == true_tables[r])))
            gen = _rng(r, tag)
            if sampled:
                sims = []
                for _ in range(args.n_samples):
                    tbl = (gen.random(p_bits.shape[0]) < p_bits).astype(np.uint8)
                    sims.append(simulate(table_to_rule(tbl), radius, gen))
                preds.append(np.mean(sims, axis=0))
            else:
                preds.append(simulate(table_to_rule(map_table), radius, gen))
        return np.stack(preds), {
            "exact": float(np.mean(exact)),
            "bit_accuracy": float(np.mean(bitacc)),
        }

    def radius_selecting_estimate(diagrams, tag, bayes_eps=None):
        """Deterministic (or F1) estimate with the radius chosen by consistency."""
        preds, sel = [], []
        for r in held:
            r_hat, _ = select_radius(diagrams[r])
            sel.append(r_hat)
            from caspectra.eval.rule_inference import transition_counts

            ones, total = transition_counts(diagrams[r], r_hat)
            if bayes_eps is not None:
                p_bits = noisy_table_posterior(ones, total, bayes_eps)
                table = (p_bits >= 0.5).astype(np.uint8)
            else:
                obs = total > 0
                table = complete_table((2 * ones > total).astype(np.uint8), obs, "zero")
            # Lift/project to the panel radius (2) so the simulated protocol matches.
            if r_hat == radius:
                rule = table_to_rule(table)
            elif r_hat < radius:
                rule = embed_eca(table_to_rule(table), radius)
            else:
                rule = table_to_rule(project_table_radius3_to_2(table, total))
            preds.append(simulate(rule, radius, _rng(r, tag)))
        hist = {int(k): int(v) for k, v in zip(*np.unique(sel, return_counts=True))}
        return np.stack(preds), {"selected_radius_hist": hist}

    # --- Scoring. ---------------------------------------------------------------
    boot_rng = np.random.default_rng(0)
    boot_idx = boot_rng.integers(0, len(held), size=(args.n_boot, len(held)))

    def score(preds: np.ndarray) -> dict:
        per = r2_per_feature(preds, true_held)
        med_boot = np.nanmedian(
            np.clip(
                1.0
                - np.sum((true_held[boot_idx] - preds[boot_idx]) ** 2, axis=1)
                / np.sum(
                    (true_held[boot_idx] - true_held[boot_idx].mean(axis=1, keepdims=True)) ** 2,
                    axis=1,
                ),
                -1.0,
                1.0,
            ),
            axis=1,
        )
        return {
            "median_r2": round(float(np.nanmedian(per)), 4),
            "median_ci95": [
                round(float(np.nanpercentile(med_boot, 2.5)), 4),
                round(float(np.nanpercentile(med_boot, 97.5)), 4),
            ],
            "per_target_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
        }

    grid: dict[str, list] = {}

    def run_cell(axis, value, diagrams, masks, cell_tag, include_direct=True, radius_axis=False):
        cell = {"value": value, "estimators": {}}
        if radius_axis:
            preds, diag = radius_selecting_estimate(diagrams, cell_tag)
            cell["estimators"]["det_radius_selected"] = {**score(preds), **diag}
            preds, diag = radius_selecting_estimate(diagrams, cell_tag + 1, bayes_eps=value)
            cell["estimators"]["f1_radius_selected"] = {**score(preds), **diag}
            preds, diag = det_estimate(diagrams, masks, cell_tag + 2)
            cell["estimators"]["det_radius_known"] = {**score(preds), **diag}
        else:
            preds, diag = det_estimate(diagrams, masks, cell_tag)
            cell["estimators"]["det"] = {**score(preds), **diag}
            eps_known = value if axis in ("noise",) else 0.0
            preds, diag = f1_estimate(diagrams, masks, cell_tag + 1, eps=eps_known)
            cell["estimators"]["f1_eps_known"] = {**score(preds), **diag}
            preds, diag = f1_estimate(diagrams, masks, cell_tag + 2, eps=None)
            cell["estimators"]["f1_eps_estimated"] = {**score(preds), **diag}
            if reader is not None:
                preds, diag = f2_estimate(diagrams, cell_tag + 3, sampled=False)
                cell["estimators"]["f2_map"] = {**score(preds), **diag}
                preds, diag = f2_estimate(diagrams, cell_tag + 4, sampled=True)
                cell["estimators"]["f2_sampled"] = {**score(preds), **diag}
        if include_direct:
            cell["estimators"]["cnn"] = score(cnn_preds(diagrams))
            cell["estimators"]["gbm"] = score(gbm_preds(diagrams))
            cell["estimators"]["stack"] = score(stack_preds(diagrams))
        best = max(cell["estimators"].items(), key=lambda kv: kv[1]["median_r2"])
        cell["best"] = best[0]
        print(
            f"[f3] {axis}={value}: best={best[0]} ({best[1]['median_r2']:.3f})  "
            + "  ".join(f"{k}={v['median_r2']:.3f}" for k, v in cell["estimators"].items())
        )
        return cell

    tag = 0
    if "noise" in args.axes:
        grid["noise"] = []
        for p in NOISE:
            deg = {r: degrade_diagram(held_diag[r], flip_p=p, rng=_rng(r, 9000))[0] for r in held}
            grid["noise"].append(run_cell("noise", p, deg, {}, tag))
            tag += 10
    if "mask" in args.axes:
        grid["mask"] = []
        for p in MASK:
            deg, masks = {}, {}
            for r in held:
                d, o = degrade_diagram(held_diag[r], mask_p=p, rng=_rng(r, 9100))
                deg[r] = d if o is None else (d * o).astype(np.uint8)
                if o is not None:
                    masks[r] = o
            grid["mask"].append(run_cell("mask", p, deg, masks, tag))
            tag += 10
    if "density" in args.axes:
        grid["density"] = []
        for p in DENSITY:
            deg = {}
            for r in held:
                ic = (_rng(r, 9200).random(width) < p).astype(np.uint8)
                sim = ECASimulator(r) if radius == 1 else RangeCA(r, radius)
                deg[r] = sim.evolve(ic, horizon)
            grid["density"].append(run_cell("density", p, deg, {}, tag))
            tag += 10
    if "label" in args.axes:
        grid["label"] = []
        for p in LABEL_FLIP:
            flip_rng = np.random.default_rng(93)
            deg = {
                r: (1 - held_diag[r]).astype(np.uint8) if flip_rng.random() < p else held_diag[r]
                for r in held
            }
            grid["label"].append(run_cell("label", p, deg, {}, tag))
            tag += 10
    if "radius" in args.axes:
        grid["radius"] = []
        for p in RADIUS_NOISE:
            deg = {r: degrade_diagram(held_diag[r], flip_p=p, rng=_rng(r, 9300))[0] for r in held}
            grid["radius"].append(
                run_cell("radius", p, deg, {}, tag, include_direct=False, radius_axis=True)
            )
            tag += 10

    summary = {
        "radius": radius,
        "width": width,
        "n_held": len(held),
        "n_pairs": args.n_pairs,
        "n_samples": args.n_samples,
        "reader_checkpoint": args.reader_checkpoint,
        "grid": grid,
    }
    save_json(summary, out / "summary.json")

    # Figure: one panel per continuous axis, one curve per estimator.
    panels = [a for a in ("noise", "mask", "density", "label") if a in grid]
    if panels:
        ncol = 2
        nrow = int(np.ceil(len(panels) / ncol))
        fig, axes_arr = plt.subplots(nrow, ncol, figsize=(9.5, 3.4 * nrow), squeeze=False)
        styles = {
            "det": ("^-", "C2"),
            "f1_eps_known": ("v-", "C3"),
            "f1_eps_estimated": ("v--", "C3"),
            "f2_map": ("D-", "C4"),
            "f2_sampled": ("D--", "C4"),
            "cnn": ("o-", "C0"),
            "gbm": ("s-", "C1"),
            "stack": ("*-", "C5"),
        }
        for i, axis_name in enumerate(panels):
            ax = axes_arr[i // ncol][i % ncol]
            cells = grid[axis_name]
            xs = [c["value"] for c in cells]
            for est, (fmt, col) in styles.items():
                ys = [c["estimators"].get(est, {}).get("median_r2") for c in cells]
                if any(v is not None for v in ys):
                    ax.plot(xs, ys, fmt, color=col, label=est, ms=4)
            ax.set_xlabel(axis_name)
            ax.set_ylabel("median held-out $R^2$")
            ax.set_ylim(-0.05, 1.05)
            ax.legend(fontsize=6)
        fig.suptitle(f"Identifiability frontier (radius {radius})")
        fig.tight_layout()
        fig.savefig(out / "frontier.pdf")
        if args.write_figure:
            fig.savefig("manuscript/figures/identifiability_v2.pdf")
    print(f"[f3] wrote {out}/summary.json and {out}/frontier.pdf")


if __name__ == "__main__":
    main()
