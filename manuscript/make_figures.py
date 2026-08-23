"""Regenerate the manuscript figures from committed results.

Run from the repo root in the ssl-ecas env (the twin-run and exemplar
figures simulate diagrams via caspectra, so the package must be importable):
    python manuscript/make_figures.py
Reads cache/s4_landscape.npz (S4), writes manuscript/figures/*.pdf.

History: a second figure (map_benchmark.pdf, "the learned map has no
advantage") was removed in the round-3 revision — it was never included by
main.tex and its title carried the retired rev-7 claim (the registered
verdict is *inconclusive*; RESULTS.md rev-8 C6). The twin-run pedagogy
figure and the signature-exemplar figure were added in the round-8 revision
(sixth report: "not a single image of a spacetime diagram or a damage cone").
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from caspectra.ca.eca import ECASimulator  # noqa: E402
from caspectra.ca.range_ca import RangeCA  # noqa: E402
from caspectra.eval.gliders import quiescent_background  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "manuscript" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
RATE, FILL = 2, 3

# The three plotted-signature rules on which the independent localized-seed
# detector (App. E) also fires: the intersection of mask=True in
# cache/s4_landscape.npz and detector_glider=True in
# runs/analysis/glider_validation/summary_r2.json. (A fourth candidate,
# 345313848, fires the detector but sits at rate 0.288 in the S4 replicate —
# just outside the registered 0.28 window — so it is red only in the
# validation replicate and would be inconsistent with the plotted set.)
EXEMPLAR_RULES = [1322117304, 2464084674, 148590960]  # sorted by S4 rate

# ---- Figure 1: the range-2 damage-signature landscape (S4) ----------------
d = np.load(ROOT / "cache" / "s4_landscape.npz")
t, mask = d["targets"], d["mask"].astype(bool)
anchors = {  # embedded-ECA (rate, fill), from the S4 run
    "204": (0.008, 1.0),
    "184": (0.048, 1.0),
    "30": (0.307, 0.529),
    "90": (0.492, 0.271),
    "54": (0.225, 0.494),
    "110": (0.214, 0.569),
}
fig, ax = plt.subplots(figsize=(5.4, 3.8))

# Iso-damage-fraction contours (referee 4, §3.6). fill = E[N/ext] and
# (w/2rT)*fraction/rate agree up to Jensen, so at fixed damage fraction the two
# plotted coordinates trace a hyperbola. Drawing the family lets the reader see
# how much of the red region's shape is the coordinate choice -- and the honest
# answer is: a lot. The signature rules span only 1.5x in damage fraction
# (IQR 0.084-0.124) against 2.6x for the bulk, so the region lies largely
# BETWEEN two contours rather than cutting across them. In decorrelated
# coordinates (rate vs N/(2rT) = fill*rate, not mechanically tied to extent)
# the same rules do not separate from the bulk: the best axis-aligned box
# containing all 234 of them also contains 732 ordinary rules (F1 = 0.39).
# The red set is a registered THRESHOLD REGION, not a discovered cluster, and
# the caption says so.
W, R, T = 127, 2, 30
K = W / (2 * R * T)
rate_grid = np.linspace(0.02, 0.9, 200)
for frac in (0.02, 0.05, 0.1, 0.2, 0.4):
    ax.plot(
        rate_grid,
        np.clip(K * frac / rate_grid, 0, 1.05),
        color="gray",
        lw=0.6,
        ls=":",
        alpha=0.55,
        zorder=0,
    )
ax.plot([], [], color="gray", lw=0.6, ls=":", label="iso damage-fraction")

ax.scatter(t[~mask, RATE], t[~mask, FILL], s=7, alpha=0.25, c="steelblue", label="ordinary")
# "damage signature", not "complex": the registered criterion is a
# finite-horizon damage signature, deliberately not promoted to a class label
# (manuscript Sec. IV G; rule_labels_PROVENANCE.md).
ax.scatter(
    t[mask, RATE],
    t[mask, FILL],
    s=14,
    alpha=0.7,
    c="crimson",
    label=f"damage signature ({mask.sum()}/{len(mask)} = {mask.mean():.1%})",
)
ax.scatter([], [], marker="*", s=150, c="gold", edgecolor="k", label="embedded ECA")
# 204 and 184 both sit at fill = 1.0 (a single surviving damaged cell has
# extent 1, so fill is 1 by construction -- the sparse-end degeneracy noted in
# Sec. II B); offset their labels so they do not collide.
offsets = {"204": (4, -10), "184": (4, 4), "110": (-9, 10), "54": (6, -10)}
for name, (r, f) in anchors.items():
    ax.scatter([r], [f], marker="*", s=150, c="gold", edgecolor="k", zorder=5)
    ax.annotate(
        name,
        (r, f),
        textcoords="offset points",
        xytext=offsets.get(name, (4, 3)),
        fontsize=8,
    )
# Mark the three detector-agreement exemplars (rendered in the companion
# exemplar figure) so they are locatable inside the signature region.
rules_arr = d["rules"]
exemplar_offsets = {"a": (-12, -5), "b": (-13, 1), "c": (7, 0)}  # dodge star labels
for lbl, rule in zip("abc", EXEMPLAR_RULES):
    (i,) = np.flatnonzero(rules_arr == rule)
    ax.scatter([t[i, RATE]], [t[i, FILL]], s=70, facecolor="none", edgecolor="k", lw=1.0, zorder=6)
    ax.annotate(
        lbl,
        (t[i, RATE], t[i, FILL]),
        textcoords="offset points",
        xytext=exemplar_offsets[lbl],
        fontsize=8,
        fontstyle="italic",
    )
ax.set_xlim(-0.02, 0.88)
ax.set_ylim(-0.02, 1.08)
# Axis glosses stay DESCRIPTIVE: an in-figure "low = gliders" would assert
# exactly the promotion the registered criterion refuses (Sec. IV G, App. D).
# Attainable maximum, not the naive light-cone bound: the final row follows
# T-1 rule applications, so rate <= (2r(T-1)+1)/(2rT) = 0.975 at r=2, T=30.
ax.set_xlabel("spreading rate  (0 = frozen; attainable maximum 0.975 here)", fontsize=9)
# Two lines: a single-line gloss is longer than the axis and gets clipped.
ax.set_ylabel("cone fill\n(low = sparse damage; 1 = solid cone or single cell)", fontsize=9)
# No in-figure title: the REVTeX caption carries it, and the internal one
# clipped at the canvas edge.
ax.legend(fontsize=7, loc="upper right", framealpha=0.9)
fig.tight_layout()
fig.savefig(FIG / "landscape.pdf", bbox_inches="tight")
plt.close(fig)
print("wrote landscape.pdf")

# ---- Figure 0: the twin-run protocol, drawn (round-8, referee R1) ----------
# One deterministic pair per rule, mirroring caspectra.eval.dynamics
# (damage_spreading_features) except that the flipped cell is the CENTRE cell
# rather than a random one — visually clearer, and the metric formulas are
# invariant to the flip position (positions are re-centred on the flip there).
# The printed per-panel values are computed HERE from the rendered pair, so
# they are self-consistent with the picture by construction; the benchmark
# targets average n_pairs = 256 such pairs, which the caption states.
TWIN_RULES = [(0, "dies out"), (204, "frozen"), (30, "chaotic"), (110, "complex")]
TWIN_WIDTH = 127
TWIN_STEPS = TWIN_WIDTH // 2 - 1  # = 62 rows; the rule is applied 61 times
FLIP = TWIN_WIDTH // 2

rng = np.random.default_rng(0)
fig, axes = plt.subplots(3, len(TWIN_RULES), figsize=(7.1, 3.3))
for j, (rule, regime) in enumerate(TWIN_RULES):
    sim = ECASimulator(rule)
    ic = (rng.random(TWIN_WIDTH) < 0.5).astype(np.uint8)
    ic_flipped = ic.copy()
    ic_flipped[FLIP] ^= 1
    a = sim.evolve(ic, TWIN_STEPS)
    b = sim.evolve(ic_flipped, TWIN_STEPS)
    damage = a != b

    axes[0, j].imshow(a, cmap="binary", interpolation="nearest")
    axes[1, j].imshow(b, cmap="binary", interpolation="nearest")
    axes[2, j].imshow(damage, cmap="inferno", interpolation="nearest", vmin=0, vmax=1)
    axes[0, j].set_title(f"rule {rule} ({regime})", fontsize=8)

    # Flip marker above run B and the damage panel. The marker sits outside
    # the image, so re-pin the limits afterwards (scatter widens data limits,
    # which would otherwise squeeze a white band above these panels).
    for ax in (axes[1, j], axes[2, j]):
        ax.scatter([FLIP], [-4.5], marker="v", s=14, color="crimson", clip_on=False, zorder=6)
        ax.set_xlim(-0.5, TWIN_WIDTH - 0.5)
        ax.set_ylim(TWIN_STEPS - 0.5, -0.5)

    # Light cone through the flipped cell: row t is the state after t rule
    # applications, so the reachable half-width at the final row is
    # TWIN_STEPS - 1 = 61 cells (speed 1 for ECAs).
    tmax = TWIN_STEPS - 1
    for sgn in (-1, 1):
        axes[2, j].plot([FLIP, FLIP + sgn * tmax], [0, tmax], color="w", lw=0.7, ls="--", alpha=0.9)

    # The four statistics of THIS pair, final-row quantities as in dynamics.py.
    final = damage[-1]
    if final.any():
        pos = np.flatnonzero(final)  # no wrap: cone half-width 61 < FLIP
        extent = int(pos.max() - pos.min()) + 1
        frac = float(final.mean())
        rate = extent / (2.0 * TWIN_STEPS)
        fill = float(final.sum() / extent)
        axes[2, j].set_xlabel(
            f"fraction {frac:.2f}  rate {rate:.2g}  fill {fill:.2f}", fontsize=7, labelpad=14
        )
        if rule == 110:
            # Extent bracket BELOW the panel in black: drawn inside, over the
            # inferno background, it is unreadable at column scale in print.
            y = TWIN_STEPS + 2.5
            axes[2, j].plot(
                [pos.min(), pos.max()], [y, y], color="k", lw=1.0, clip_on=False, zorder=7
            )
            for x in (pos.min(), pos.max()):
                axes[2, j].plot([x, x], [y - 2.5, y], color="k", lw=1.0, clip_on=False, zorder=7)
            axes[2, j].annotate(
                "extent",
                ((pos.min() + pos.max()) / 2, y + 1.5),
                ha="center",
                va="top",
                fontsize=7,
                annotation_clip=False,
            )
    else:
        axes[2, j].set_xlabel("no damage at the horizon", fontsize=7, labelpad=14)

for ax in axes.ravel():
    ax.set_xticks([])
    ax.set_yticks([])
axes[0, 0].set_ylabel("run A", fontsize=8)
axes[1, 0].set_ylabel("run B\n(one cell flipped)", fontsize=8)
axes[2, 0].set_ylabel("damage\n(A $\\neq$ B)", fontsize=8)

fig.tight_layout(w_pad=1.4, h_pad=0.5)
fig.savefig(FIG / "twin_run.pdf")
plt.close(fig)
print("wrote twin_run.pdf")

# ---- Figure: signature-region exemplars (round-8, referee on Fig. 3) -------
# For each exemplar rule, the localized-seed protocol of
# caspectra.eval.gliders.localized_seed_metrics (ring 255, radius 2, 5-cell
# random seed on the quiescent background, same rng stream: default_rng(0)
# per rule), keeping the first surviving diagram instead of only its scalars.
# All three rules have alive = 1.0 in the validation run, so seed 0 survives.
EX_WIDTH, EX_RADIUS = 255, 2
EX_STEPS = EX_WIDTH // (2 * EX_RADIUS) - 1  # = 62
EX_SEED_WIDTH = 5

# Full text width: at \columnwidth the 255-cell strips print at ~5 pt and the
# structures the figure exists to show are not resolvable.
fig, ex_axes = plt.subplots(len(EXEMPLAR_RULES), 1, figsize=(7.1, 3.0))
for ax, lbl, rule in zip(ex_axes, "abc", EXEMPLAR_RULES):
    background = quiescent_background(rule, EX_RADIUS)
    ex_rng = np.random.default_rng(0)
    sim = RangeCA(rule, EX_RADIUS)
    centre = EX_WIDTH // 2
    diagram = None
    for _ in range(24):
        row = np.full(EX_WIDTH, background, dtype=np.uint8)
        seed_bits = ex_rng.integers(0, 2, size=EX_SEED_WIDTH, dtype=np.uint8)
        if not np.any(seed_bits != background):
            seed_bits[0] = 1 - background
        row[centre - EX_SEED_WIDTH // 2 : centre + EX_SEED_WIDTH // 2 + 1] = seed_bits
        candidate = sim.evolve(row, EX_STEPS)
        if np.any(candidate[-1] != background):
            diagram = candidate
            break
    assert diagram is not None, f"no surviving seed for rule {rule}"

    (i,) = np.flatnonzero(d["rules"] == rule)
    ax.imshow(diagram, cmap="binary", interpolation="nearest")
    # Light cone of the seed (speed = radius cells per step): the structures
    # stay well inside it — sub-ballistic growth, the detector's criterion.
    ex_tmax = EX_STEPS - 1  # rule applied EX_STEPS - 1 times
    for sgn in (-1, 1):
        ax.plot(
            [centre, centre + sgn * EX_RADIUS * ex_tmax],
            [0, ex_tmax],
            color="crimson",
            lw=0.6,
            ls="--",
            alpha=0.7,
        )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(
        f"({lbl}) rule {rule}:  rate {t[i, RATE]:.2f},  fill {t[i, FILL]:.2f}",
        fontsize=8,
        loc="left",
    )

fig.tight_layout()
fig.savefig(FIG / "signature_exemplars.pdf")
plt.close(fig)
print("wrote signature_exemplars.pdf")
