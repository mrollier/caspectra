# RESULTS.md — measured record & decision gates

Running log of *measured* outcomes (predictions and critique live in
`SELF_CRITICISM.md`; pass/fail thresholds in `EVALUATION_CRITERIA.md`).

---

## 2026-07-01 — v1 full evaluation, finally with labels (`runs/default/eval_v2/`)

The original eval (2026-06-25, `runs/default/eval/`) ran 11 minutes *before*
`rule_labels.csv` was created, so every LP/Wolfram metric in it is `null`. The
run was re-evaluated on the unchanged checkpoint with the completed, verified
label table (`rule_labels_PROVENANCE.md`; LP labels transcribed from Li &
Packard 1990 Table 2 — note 6 corrections to the old best-effort labels,
incl. 54/110 = chaotic under LP).

### Probes (held-out ICs)

| probe | embedding | 4-scalar baseline |
|---|---|---|
| rule/orbit (88-way) | **0.967** | 0.721 |
| Li–Packard (5-way) | 0.966 | 0.838 |
| Wolfram (4-way) | 0.999 | 0.971 |
| **gap** (LP − rule) | **−0.002** | **+0.117** |

The first-ever measurement of the project's headline metric: the gap is zero —
the embedding knows the exact rule as well as it knows the class. The cheap
hand-crafted baseline **beats the SSL embedding on the project's own success
metric**.

### Clustering (UMAP+HDBSCAN, 95 clusters)

- purity vs Wolfram 0.997 / vs LP 0.937 — trivially high (clusters ≈ rules);
  ARI 0.041 / 0.087 — near-zero partition agreement.
- Excess genotype info `MI(cluster; orbit | LP)` = **2.55 nats** (want ≈ 0).
- Excess genotype **fraction** `MI(cluster;orbit|wolfram)/H(orbit|wolfram)`
  = **0.81** (criterion 2: success ≤ 0.25, failure ≥ 0.5 → **fail**).
- Per-Wolfram-class cluster recall ≈ 1.0 for all classes — meaningless alone
  (rule-pure clusters are class-pure); read jointly with criterion 2.

### Geometry

- Participation ratio **8.3 / 64** dims — heavily anisotropic.
- R²(embedding → folded density) = **0.946**, raw = 0.915: the density nuisance
  is almost fully encoded, and folded > raw confirms the invert augmentation
  *did* produce the intended complementation invariance (the encoder sees
  `min(d, 1−d)`).

---

## 2026-07-01 — M2 salience experiments (no retraining; `notebooks/03_salience.ipynb`)

### Experiment 1 — project out density + activity, re-cluster

Excess genotype fraction 0.81 → **0.89**; more clusters, more noise, no
behavioural macro-structure. **Negative:** the salience defect is not repaired
by removing the nuisance axes — the residual geometry is still per-rule texture
fingerprints. Geometry repair alone is insufficient; the objective must change.

### Experiment 2 — orbit-averaged embeddings (best case for the SSL encoder)

88 orbit means, agglomerative clustering, k ∈ {4, 6, 8, 10, 14}:
**class-IV recall = 0.00 at every k.** Rules 54 and 110 are not even co-clustered
beyond k=4, and 54 sits among periodic rules. Full IC-denoising does not help.

### Experiment 3 — physics baseline: damage spreading (`eval/dynamics.py`)

Four label-free scalars per rule (damage survival, damage fraction, spreading
rate, cone fill), same clustering protocol:

| k | class-IV recall | 54's cluster |
|---|---|---|
| 4–10 | 0.00 | {54, 110} + chaotic rules (always together) |
| 14 | **1.00** | **{54, 106, 110}** (chaotic recall still 0.92) |

The features are interpretable and stratify exactly as theory says: class 1
damage dies; class 2 frozen/slow cones (rate ≤ 0.25); class 3 ballistic
(rate 0.43–0.99); class 4 intermediate (rate ≈ 0.4, survival 1.0). The three LP
locally-chaotic rules (26, 73, 154) get their own signature (survival ≈ 1, rate
0.03–0.11). Borderline cases: rule 106 (chaotic, rate 0.43 — the one class-IV
contaminant) and rule 41 (Wolfram 2 with a chaotic-looking cone).

### Decision (pre-registered gate, EVALUATION_CRITERIA.md)

**The physics baseline beats the SSL embedding on class-IV recall, 1.00 vs
0.00.** Texture-BYOL as built detects no computation that four damage-spreading
scalars don't detect better — while also losing to the texture baseline on the
gap. Consequences for v2 training (Milestone 3):

1. The **complexity prior is mandatory, not optional**: v2's first training
   lever is the auxiliary damage-spreading target (plan 3.2), with
   temporal-window positives (3.1) as the accompanying data-side fix.
2. Pure re-augmentation of the texture pipeline is **not** worth a long run —
   Experiment 1 shows the problem is objective content, not geometry.
3. If SSL + prior still fails criterion 1&2 jointly, the honest headline is the
   negative result already written into `EVALUATION_CRITERIA.md`, and effort
   moves to the larger rule space (Milestone 4).

*(Superseded in part on 2026-07-02: temporal-window positives were dropped as a
standalone lever after the foundations review — see the next entry.)*

---

## 2026-07-02 — Foundations consolidation (literature review → decisions + measurements)

A commissioned deep-research report
(`docs/literature/2026-07-02_deep_research_report.md`, distilled in
`FOUNDATIONS.md`) concluded that the original mission — "discover a label-free
behavioural taxonomy" — is ill-posed as stated (undecidability, measure/protocol
dependence, no bias-free clustering) but salvageable as: an **invariant-based
taxonomy of protocol tuples** + **amortized, spatially-resolved invariant
estimation** for the nuCA target.

### Decision record

- **Mission reframed** (README/CLAUDE.md/FOUNDATIONS.md §3); texture-SSL is the
  frozen negative baseline; remaining levers: **A** = invariant-regression
  amortizer (primary), **B** = predictive SSL; **temporal-window positives
  dropped** (still instance discrimination; same shortcut incentives).
- **EVALUATION_CRITERIA.md revision 2** (before any v2 run): the classified
  object is the explicit protocol tuple; Wolfram/LP demoted to touchstones with
  `borderline` flags (40, 41, 42, 106) and dual class-IV reporting; new
  criteria 5 (protocol stability) and 6 (amortization transfer, gates Lever A);
  kill criteria for the learning component.
- `input_entropy_variance` (Wuensche's class-IV screen) added as a 5th baseline
  feature — future eval runs report a 5-feature baseline (the 2026-07-01 record
  above used 4).

### Protocol sensitivity (criterion 5, first measurement — `runs/analysis/protocol_sensitivity/`)

n_pairs = 128, reference = (p = 0.5, width 127), same-protocol **seed-control
floor ARI = 0.70**:

| protocol | feature Spearman ρ (surv/frac/rate/fill) | ARI vs ref | class flips |
|---|---|---|---|
| p = 0.25 (gated) | 0.90 / 0.97 / 0.96 / 0.97 | **0.33** | {106} |
| p = 0.75 (gated) | 0.90 / 0.94 / 0.92 / 0.94 | **0.37** | {168} |
| p = 0.1 / 0.9 (context) | ≥ 0.79 | 0.30 / 0.18 | incl. 54, 110 |
| w = 63 / 255 (context) | ≥ 0.96 | 0.58 / **0.78** | {54,106,110} / ∅ |

**Verdict: criterion 5 fails on the ARI half, passes the feature half — and the
failure is a finding, exactly as the foundations literature predicts.** The
*fine* hard partition of rule space is genuinely **IC-measure-dependent**
(cross-density ARI ≈ half the seed floor), while lattice width barely matters,
class-level assignments flip for only one rule per gated density, and the
{54, 110} co-membership is stable across the whole gated range (it degrades
only at extreme densities 0.1/0.9, where "complex" behaviour genuinely changes
character). Consequence (recorded in criterion 5): taxonomy claims are made at
the level of protocol-robust structures — the invariant feature space, coarse
groups, and specific co-memberships — never as a fine partition.

### Borderline bootstrap (10 seeds × n_pairs = 256, reference protocol)

- **106 is real, not noise**: spreading rate 0.433 ± 0.012 vs rule 54's
  0.428 ± 0.006 — statistically inseparable from class IV in damage space.
- **41 is real, not noise**: rate 0.586 ± 0.010, firmly chaotic-range (rule 30:
  0.621 ± 0.003) despite Wolfram-2/LP-periodic labels; Wuensche's input-entropy
  variance *also* flags 41 as the most glider-like non-trivial rule
  (0.018 ± 0.010) — 41 is genuinely ambiguous under every lens we have.
- Additive rules (60/90/105/150) have **exactly zero** feature variance —
  damage evolves independently of the background for linear rules (a clean
  internal consistency check).
- Wuensche-screen caveats measured: rule 110's variance signal is weak at 127px
  from random ICs (transient-dominated; supports `discard_transient > 0` for
  Lever-A targets) and rule 0's high variance is a pure transient artifact —
  the feature is only meaningful jointly with the others.

---

## 2026-07-02 — Lever A: criterion 6 measured (both split variants)

First training of the invariant-regression amortizer (`configs/lever_a.yaml` +
swapped variant; AntiCheatCNN 64-d + linear head, 60 epochs, 127px, coarse-grain
OFF; targets = damage features at n_pairs = 256; 18 rules held out,
Wolfram-stratified).

### Criterion 6 — **PASS in both variants** (gate: median rule-level R² ≥ 0.5)

| feature (rule-level R², 18 unseen rules) | main (110 out) | swap (54 out) |
|---|---|---|
| damage_survival | 0.694 | 0.700 |
| damage_fraction | 0.797 | 0.808 |
| spreading_rate | **0.970** | **0.956** |
| cone_fill | 0.929 | 0.863 |
| **median** | **0.863 → PASS** | **0.836 → PASS** |

The invariants are amortizable from single diagrams, and robustly so across the
class-IV split. Signal appeared essentially immediately (epoch-1 median R²
0.875), so the diagram texture encodes the damage response far more directly
than it encodes the reference class labels. Diagnostics: participation ratio
4.1–4.2/64 (the embedding organizes along ≈ the 4 targets); rule probe 0.94
(reported, not gated); LP/Wolfram probes ≈ 1.0.

### The class-IV corner: a mirror-image failure, and the honest caveat

Both variants misplace the **unseen** complex rule, in opposite directions:

- main: rule 110 predicted spreading_rate 0.536 (true 0.372) — pulled **up
  toward chaotic**; amortized taxonomy breaks the class-IV island
  ({54, 106} only; class-IV recall 0.0 vs 1.0 for direct invariants).
- swap: rule 54 predicted 0.185 (true 0.436) — pulled **down toward locally
  chaotic**; its amortized cluster is {26, 37, 54, 73}.

Interpretation: the intermediate damage regime is underdetermined from **one**
training exemplar — the amortizer interpolates unseen complex rules toward
whichever neighbouring regime it knows. Criterion 6 passes (amortization
works), but a class-IV *detector* for genuinely unseen complex rules needs more
complex training exemplars than ECAs can provide — direct, quantitative
strengthening of Milestone 4 (larger rule space, where glider rules are
plentiful per Wuensche).

### Per-patch phenotype maps (qualitative preview)

`runs/lever_a/eval/phenotype_maps.png`: rule 0's predicted spreading-rate map is
≈ 0 everywhere **except the IC-transient top row** (correct spatial
localization of activity); rule 204 reads ≈ 0 with stripes tracking its frozen
columns; rule 30's patches read systematically hotter than 110's, matching the
true rates. Resolution is coarse (≈ 8×8 patches at 127px — set by the encoder's
four pooling stages); a shallower-head variant is the known next step before
quantitative nuCA validation.

---

## 2026-07-03 — Criterion 7 measured: compositional map transfer on nuCAs (frozen `runs/lever_a`)

`NonUniformCA` implemented (`caspectra/ca/nuca.py`; uniform-mask ≡ ECA exactly,
tested); criterion 7 pre-registered in EVALUATION_CRITERIA.md **rev 3** before
any composed diagram was evaluated (16-rule train-split panel, 120 pairs × 8
ICs, half/half masks, ±16 px interface exclusion → map columns {1,2} / {4,5} of
7). Harness: `scripts/validate_nuca.py`; artifacts in `runs/lever_a/nuca_eval/`.

**Control:** rule_a == rule_b composed diagrams reproduce the uniform diagrams
and maps *exactly* (max |map diff| = 0.0) — the harness is sound.

### Criterion 7 — **INCONCLUSIVE** (median region-level R² 0.433; bars: ≥ 0.5 / < 0.2)

| feature (region-level R²) | primary (train pairs) | secondary (held-out × anchors) |
|---|---|---|
| damage_survival | 0.278 | 0.294 |
| damage_fraction | **0.619** | **0.681** |
| spreading_rate | **0.588** | **0.728** |
| cone_fill | 0.138 | 0.024 |
| **median** | **0.433** | 0.488 |

Spreading-rate **ordering accuracy** (which region is hotter): 0.83 primary /
0.92 secondary — the maps usually get the *ranking* of the two regions right;
what fails is region-level calibration, feature-dependently.

### Diagnosis — the maps are not local (context leakage, mechanism isolated)

The scatter (`criterion7_scatter.png`) shows the failure concentrated where a
dead/frozen region is composed with an active partner. Decisive probe (16 ICs,
rule 0's interface-free region, true survival = 0.0):

| context | predicted damage_survival of the rule-0 region |
|---|---|
| uniform rule 0 | **0.011 ± 0.003** (correct) |
| 0 \| 204 (frozen partner) | 0.642 ± 0.045 |
| 0 \| 184 | 0.471 ± 0.015 |
| 0 \| 26 | 0.739 ± 0.032 |
| 0 \| 54 | 0.701 ± 0.043 |
| 0 \| 30 (chaotic partner) | 0.755 ± 0.013 |

The identical dead region, with no interface overlap by construction, is
re-scored by up to +0.74 purely by what the *other half* of the image contains
— even a static rule-204 partner shifts it massively. `predict_map` is exactly
linear in the pre-GAP feature map, so the leak is *inside the encoder*: the
prime suspect is **GroupNorm normalizing over the whole image** (every patch's
activations are scaled by global statistics), compounded by training that only
ever saw spatially uniform diagrams — nothing ever penalized global shortcuts.
Interface-band means themselves are unremarkable (≈ midway between regions).

### Consequences

1. The nuCA payoff claim is **not yet earned**: amortized invariants compose
   only partially (extensive-ish features and rankings survive; survival/fill
   calibration does not). Criterion 7 stays open — no threshold change.
2. The bottleneck is **locality, not resolution**: a shallower head (finer
   patches) does not by itself remove per-image normalization. Candidate fixes,
   in increasing cost: (a) local-only normalization (or norm-free encoder),
   (b) nuCA-composed diagrams *in training* (targets = per-region invariants —
   makes locality pay), (c) both. Any of these is a new training run.
3. The probe protocol above (partner sweep on an interface-free dead region) is
   the cheap regression test any future "fixed" model must pass: uniform-0 and
   composed-0 predictions must agree.

---

## 2026-07-03 — Local-norm variant: criterion 7 PASS, leakage mechanism confirmed (`runs/lever_a_local`)

One variable changed vs `lever_a` (user decision after the entry above):
`norm_layer: batch` — BatchNorm's inference-time running statistics make the
network genuinely local, whereas GroupNorm scales every patch by whole-image
statistics. Same recipe otherwise (60 epochs, 127px, 110 held out / 54 trained;
smoke passed first).

### Both gates, side by side (same registered specs)

| gate | GroupNorm (`lever_a`) | **BatchNorm (`lever_a_local`)** |
|---|---|---|
| criterion 6 median rule-level R² | 0.863 PASS | **0.856 PASS** |
| criterion 7 median region R² (primary) | 0.433 INCONCLUSIVE | **0.831 PASS** |
| criterion 7 per feature (surv/frac/rate/fill) | 0.28 / 0.62 / 0.59 / 0.14 | **0.53 / 0.88 / 0.88 / 0.79** |
| criterion 7 secondary (held-out × anchors) | 0.488 | **0.863** |
| spreading-rate ordering accuracy | 0.83 / 0.92 | **0.95 / 0.96** |
| rule-0 region, uniform → composed (survival) | 0.011 → 0.47–0.76 | **−0.032 → −0.031 (partner-independent)** |

The partner probe is now flat to the third decimal across all five partners —
the context leak is *eliminated*, not merely reduced, and criterion 7 passes
with margin. Criterion 6 is statistically unchanged (survival actually improves,
0.694 → 0.738), so locality cost nothing on the global gate. Control exact
(map diff 0.0); harness identical to the entry above.

**Conclusion: the criterion-7 failure was entirely an architecture artifact
(GroupNorm's per-image spatial statistics), not a limitation of invariant
amortization.** Composed out-of-distribution diagrams — including compositions
of *never-seen* rules with anchors (secondary median 0.863) — are now read
region-by-region with accuracy comparable to the global criterion-6 transfer.
The nuCA payoff claim is earned at 7×7 resolution.

Bonus observation: the amortized taxonomy's class-IV island is partially
restored ({54, 110} co-membership TRUE again, cluster {54, 60, 106, 110}),
though class-IV recall at k = 14 remains 0.0 — the one-complex-exemplar
limitation (M4 motivation) is unchanged.

Follow-ups now unblocked, in order of value: the **shallow local-norm variant**
(15×15 maps; `configs/lever_a_shallow.yaml` + `norm_layer: batch`) for finer
spatial detail; striped/irregular masks *below* the current patch size as the
stress test; M4. Default encoder guidance for regression models: **BatchNorm,
not GroupNorm** — the batch<256 GroupNorm rule was BYOL/SimSiam advice and
actively harms map locality here.

## 2026-07-03 — Shallow local-norm variant: both gates PASS at 15×15 (`runs/lever_a_shallow`)

The follow-up flagged above: 3 encoder blocks instead of 4
(`encoder_channels: [16, 32, 64]`), BatchNorm per the new rule, otherwise the
`lever_a` recipe unchanged (60 epochs, 127px, 110 held out / 54 trained; 63px
smoke passed first). Map resolution rises 7×7 → **15×15** (patch ≈ 8.5 cells
across vs ≈ 18), and the criterion-7 interface exclusion now keeps **4 columns
per region instead of 2** (kept {2,3,4,5} / {9,10,11,12}).

### Both gates, side by side with the 7×7 local-norm run (same registered specs)

| gate | `lever_a_local` (7×7) | `lever_a_shallow` (15×15) |
|---|---|---|
| criterion 6 median rule-level R² | 0.856 PASS | **0.803 PASS** |
| criterion 6 per feature (surv/frac/rate/fill) | 0.74 / 0.80 / 0.97 / 0.91 | 0.76 / 0.79 / 0.97 / 0.82 |
| criterion 7 median region R² (primary) | 0.831 PASS | **0.764 PASS** |
| criterion 7 per feature (surv/frac/rate/fill) | 0.53 / 0.88 / 0.88 / 0.79 | 0.39 / 0.86 / 0.85 / 0.67 |
| criterion 7 secondary (held-out × anchors) | 0.863 | 0.821 |
| spreading-rate ordering accuracy (primary/secondary) | 0.95 / 0.96 | **0.97 / 0.98** |
| rule-0 partner probe (survival, uniform → 5 partners) | −0.032 → −0.031 flat | **0.001 → 0.001 flat** |
| control (rule_a == rule_b max map diff) | 0.0 | 0.0 |

Reading: everything still passes with margin and **locality holds exactly at
the finer resolution** (probe flat at 0.001 ± 0.001 for all partners). The
shallower encoder pays a modest, consistent accuracy tax — criterion 6
0.856 → 0.803, criterion 7 0.831 → 0.764 — concentrated in `damage_survival`
(region-level 0.53 → 0.39 on the primary panel; note it remains 0.81 on the
held-out×anchor secondary, so the weakness is calibration on the extreme
all-or-nothing panel rules, not transfer). Rate *ordering* is actually the
best measured yet (0.97/0.98). Rule 110's spreading rate is again over-read
(0.47 vs true 0.37) — the one-complex-exemplar bias is architecture-independent,
as expected. Taxonomy diagnostics match the 7×7 run ({54,110} co-membership
TRUE, cluster {54, 60, 106, 110}; class-IV recall at k=14 still 0.0;
participation ratio 4.9/64; rule probe 0.925).

**Verdict: the depth/resolution trade is real but cheap.** Use `lever_a_local`
(7×7) when the global numbers matter most; `lever_a_shallow` (15×15) when
spatial detail does — both are certified by the same pre-registered gates. The
natural next stress test is unchanged: masks with stripes at or below the patch
size (period ≤ 8 at 15×15), where interface-free patches stop existing.

## 2026-07-03 — Criterion 8 measured: stripe resolution + alloy transfer (both checkpoints)

Pre-registered as **EVALUATION_CRITERIA.md revision 4** (commit `ead0fcf`,
before any striped measurement beyond criterion 7's qualitative figure and
before any composed-system invariant existed). Harness:
`scripts/validate_stripes.py`; outputs in `runs/<run>/stripe_eval/`.
Controls passed on both runs: (r, r) striped diagrams identical to the pure
ECA, and (r, r) "alloy" twin-run features bit-for-bit equal to the pure rule
under the same rng. Registered spec throughout (78 contrast pairs, 16 ICs;
120 alloy pairs × periods {2, 4}, 8 ICs, truth from 256 twin runs each).

### 8a — spatial resolution (point-spread function of the maps)

Median relative contrast R(p) = C(stripes period p) / C(half/half), 78 pairs:

| period p | 7×7 `lever_a_local` | 15×15 `lever_a_shallow` |
|---|---|---|
| 32 px | **0.761** | **0.873** |
| 16 px | 0.302 | **0.648** |
| 8 px | 0.003 | 0.230 |
| 4 px | −0.002 | 0.000 |
| 2 px | 0.001 | −0.003 |
| gate at p=32 (CI95 > 0) | **PASS** (0.724, CI [0.69, 0.75]) | **PASS** (0.813, CI [0.77, 0.85]) |
| **resolution limit** (R ≥ 0.5) | **32 px** | **16 px** |

The previously *unverified* "pick 15×15 for spatial detail" claim is now
measured and holds: the shallow checkpoint's resolution limit is exactly one
octave finer (16 vs 32 px), matching its 2× map resolution, and it retains
partial contrast at 8 px (0.23) where the 7×7 map is stone blind (0.00).
Neither map sees anything at 4 px and below — as geometry demands.

### 8b — alloy transfer (gated): reading systems that are not ECAs at all

Below the resolution limit a fine-striped composed system is a *new*
homogeneous system. Truth = twin-run invariants measured directly on the
composed simulator; the registered degeneracy rule fired for no feature
(truth std 0.12–0.27). Per-feature R², 240 alloys × 8 ICs:

| feature | 7×7 map | 15×15 map | mixture baseline |
|---|---|---|---|
| damage_survival | 0.623 | 0.328 | 0.320 |
| damage_fraction | 0.610 | 0.704 | 0.339 |
| spreading_rate | 0.478 | 0.408 | 0.233 |
| cone_fill | 0.258 | 0.064 | −0.539 |
| **gated median** | **0.544 → PASS** | **0.368 → INCONCLUSIVE** | 0.277 (not gated) |

The alloys are strongly **non-additive** — e.g. rule 30 diluted with rule-0
stripes at period 2 has true spreading rate 0.009 where the mixture predicts
0.311 (damage freezes in place but survives, 0.72): an emergent frozen phase.
The **7×7 map tracks this emergent behaviour** (beats the mixture on every
feature and passes the registered gate) despite training only on 70 uniform
ECAs. The 15×15 map still beats the mixture overall but lands INCONCLUSIVE
under the registered bars — its weakness concentrates in `damage_survival`
and `cone_fill`, consistent with its already-documented survival calibration
tax.

**Verdict and guidance correction.** The depth/resolution trade now has both
sides measured: the shallow checkpoint genuinely *sees finer* (8a, one octave),
but the deep checkpoint *reads emergent out-of-distribution dynamics better*
(8b, PASS vs INCONCLUSIVE). "Pick by use case" survives with sharper content:
7×7 for trustworthy readings of novel/mixed dynamics, 15×15 for localizing
*where* behaviour changes. Caveats stated plainly: `cone_fill` is weakly read
on alloys by both checkpoints (0.26 / 0.06), and the 7×7 pass at 0.544 clears
the bar without headroom.

## 2026-07-04 — M4 measured: range-2 rule space repairs the §6 complex caveat (`runs/m4_range2`)

Pre-registered as **EVALUATION_CRITERIA.md revision 5** (commit `e2dd185`,
before any range-2 model was trained and before any rule was held out).
Motivation: criterion 6 passed on ECAs but the complex regime there is a
two-member club ({54, 110}); held out, either is *pulled* toward the nearest
populated regime (§6, 2026-07-02: 110's rate read 0.54 vs true 0.37, i.e.
**+0.17**; 54's 0.18 vs 0.44, **−0.26**). ECAs cannot fix this. M4 enlarges the
space to two-state **radius-2** CAs (2^32 rules; `caspectra/ca/range_ca.py`),
sampled and orbit-deduped, with a radius-aware damage horizon (`width//(2r)`)
and rate normalization so the four invariants keep their meaning.

### Landscape (the substrate fix, `runs/m4_range2/landscape`)

800 uniformly-sampled canonical range-2 rules, invariants under the range-2
protocol (width 127, n_pairs 256). Under the pre-registered complex signature
(`regimes.COMPLEX_SIGNATURE`: survival > 0.85, 0.15 ≤ rate ≤ 0.28, fill < 0.6,
fraction < 0.15), **57/800 = 7.1 % are complex** — a genuinely populated
cluster, versus ~2/88 for ECAs. In the rate×fill plane the sample separates
into an ordered arm, a dense chaotic bulk (rate 0.4–0.8), and a distinct
complex band where the embedded rule-54/110 anchors land (both correctly
flagged; the order/chaos/additive anchors correctly excluded). The
embedded-ECA continuity control (range-2 rules reproducing ECA diagrams
bit-for-bit) passes in the test suite. Uniform sampling far exceeds the
pre-registered fallback threshold (15), so no targeted resampling was needed.

### Training + criteria 6 and 9 (`runs/m4_range2`)

800 rules × 64 ICs at 127 px, BatchNorm regressor, 60 epochs; **all 57
signature-complex rules held out** (leave-complex-out) plus a 103-rule general
hold-out. Train MSE 0.343 → 0.123.

| hold-out | rules | median R² | survival | fraction | rate | cone_fill | signed rate bias |
|---|---|---|---|---|---|---|---|
| general (criterion 6) | 103 | **0.849** | — | — | — | — | −0.015 |
| complex (criterion 9) | 57 | **0.822** | 0.739 | 0.914 | 0.906 | 0.410 | **+0.012** |

- **Criterion 6 PASS** on the range-2 space (general median 0.849 ≥ 0.5).
- **Criterion 9 PASS** (both gates): complex median R² 0.822 ≥ 0.5, **and** the
  mean signed spreading-rate error is **+0.012** (bar |·| ≤ 0.10) — versus the
  ECA §6 baseline of **+0.17 / −0.26**. Populating the regime collapsed the
  systematic pull by ≈ 20×: 57 never-trained complex rules are placed on the
  diagonal, not rounded toward a neighbour.
- `cone_fill` is again the weak feature (0.41 on complex, 0.385 overall) — the
  glider/chaos discriminator remains the hardest to amortize, architecture- and
  space-independent. Median clears the bar with room regardless.

**Verdict: the §6 two-member-club caveat is repaired.** The amortizer's
mis-placement of complex rules was a data-population artifact, not a limit of
invariant amortization: given a populated intermediate regime, held-out complex
behaviour is recovered without bias. This is the strongest evidence yet that the
learned estimator tracks *behaviour*, not a memorized small-rule lookup.

**Methods note (target set-dependence, fixed in the evaluator, deferred in the
core):** `dynamics_feature_matrix` seeds one RNG per rule *by sorted-list
position*, so target values depend on the rule *set*, not just the rule — a
subset gives slightly different (equally valid) invariants. Every criterion
compares predictions against truth from the *same* set the model trained on
(`validate_complex_placement.py` loads the full 800-rule panel, not the held-out
subset); an early run that recomputed truth on the 160-subset produced a
spurious complex R² of −2.1 before this was corrected. A rule-identity RNG seed
would remove the coupling; deferred because it would shift all cached values.

---

## 2026-07-04 — Manuscript solidification (EVALUATION_CRITERIA.md rev 6 controls)

Pre-registered as **rev 6** (commit `516866b`, numbers-free) before any of these
controls was measured. Purpose: close the three solidity gaps a Q1 (*Chaos*)
referee would hit — a single-diagram baseline (S1), seed error bars (S2), and the
RNG set-dependence (S3) — before drafting the manuscript.

### S3 — RNG set-dependence: measured, then fixed (no longer deferred)

The deferred coupling above is now **resolved, not worked around**. Measured the
drift directly: 10 probe rules spanning the regimes, each rule's four invariants
recomputed as a member of **3 rule sets of different composition** (n_pairs = 256,
the reference protocol), max |Δ| per feature:

| | damage_survival | damage_fraction | spreading_rate | cone_fill |
|---|---|---|---|---|
| ECA (r=1), position-seeded | 0.047 | 0.015 | 0.015 | 0.022 |
| range-2 (r=2), position-seeded | 0.082 | 0.017 | 0.037 | 0.074 |
| **either, identity-seeded (fixed)** | **0.000** | **0.000** | **0.000** | **0.000** |

The drift is pure Monte-Carlo resampling noise (different IC streams), largest on
borderline-*survival* rules where the n_pairs = 256 binomial SE peaks (~0.03 near
p = 0.5) — but it exceeded the pre-registered 0.01 immateriality bar, so per rev-6
S3 the fix triggered: `dynamics_feature_matrix` now seeds each rule's RNG by
**identity** (`SeedSequence([seed, rule, radius])`) instead of sorted-list
position, mirroring `load_or_compute_alloy_targets`. Cross-set drift is now
exactly 0 — a rule's target is a well-defined function of `(rule, protocol)`,
independent of the panel. The cache key carries `seed_scheme` so
position-seeded files are never silently reused; `test_feature_matrix_is_set_independent`
guards it. Disclosed alongside: the *intrinsic* target precision (SD of one
n_pairs = 256 estimate across seeds) is ≈0.006 (ECA) / ≈0.008–0.014 (range-2),
which is the irreducible noise floor that caps achievable amortization R².

**Consequence for the manuscript pipeline:** because the fix shifts every cached
target value (unbiased, but different realizations), the headline models are
**retrained under the corrected seeding (S2)** and the baseline comparison (S1)
is computed against those fresh S2 checkpoints and truth — so training truth and
evaluation truth always match. The original single-seed runs above stand as
computed; the manuscript reports the S2 error-barred numbers throughout.

### S4 — range-2 complex density, tightened

3000 uniformly-sampled canonical range-2 rules (identity-seeded targets,
n_pairs = 256): **234/3000 = 7.80% complex**, Wilson 95% CI **[6.9%, 8.8%]** —
the M4 800-rule estimate (7.1%) sits inside the interval; the "≈7%, vs ~2% for
ECAs" claim is now referee-proof. Embedded-ECA anchors place correctly (54/110
complex; order/chaos/additive excluded). Cached to `cache/s4_landscape.npz` for
the manuscript figure.

### S1 — single-diagram baseline: the amortizer does NOT beat cheap features

The decisive control, and the reason it was pre-registered before drafting. A
ridge and a gradient-boosted-tree regressor were fit from **five label-free
single-diagram statistics** (folded density, temporal activity, compression
ratio, 2×2 block entropy, radius-aware input-entropy variance;
`caspectra/eval/baselines.py`) onto the four damage invariants, under the
**identical leave-rules-out split** as the CNN.

| task | best baseline (GBM) median R² | CNN median R² | margin (CNN − baseline) |
|---|---|---|---|
| ECA global (18 held out) | **0.927** | 0.843 | **−0.084** (baseline wins) |
| range-2 global (103 held out) | 0.845 | 0.849 | +0.004 (tie) |
| range-2 **complex** (57 held out) | 0.795 | 0.822 | +0.027 (within noise) |

Per-feature, the GBM baseline reaches spreading_rate R² 0.965 (ECA) / 0.880
(range-2), damage_fraction 0.924 / 0.909 — i.e. the damage-spreading invariants
are **largely texture-predictable from a single diagram**. The pre-registered
"meaningfully better" bar (CNN median − best baseline ≥ 0.10 **and** beats it on
≥ 3/4 features) is **not met on any task** — indeed the baseline *wins* on ECAs.

*Caveat (honest, resolved by S2):* the CNN numbers here are from the original
single-seed runs (trained on the pre-fix targets), while the baseline is on the
identity-seeded targets — so the +0.03 range-2-complex edge is within the target
resampling noise and the comparison is not yet strictly matched. S2 retrains the
CNN on the corrected targets and re-runs S1 with `--checkpoint` for a matched
head-to-head. But the ECA gap (−0.08, baseline ahead) is far larger than the
~0.01–0.03 target noise and will not reverse.

**Consequence (pre-registered softening rule, rev 6 S1 fired):** the
**global/scalar amortization is not a contribution** — cheap hand-crafted
features match or beat the deep model at predicting the damage invariants,
including the complex-regime placement that criterion 9 was built to showcase.
Populating the complex regime (M4) repairs the §6 bias for *any* competent
regressor, not specifically the CNN. The only contribution the scalar baseline
**cannot** provide is the **spatially-resolved phenotype map** — measured next.

### Map control — the CNN map has no resolution advantage over hand-crafting

The decisive test of the one remaining possible contribution
(`scripts/validate_map_vs_baseline.py`): does the CNN's learned per-patch map
resolve behaviour *more finely* than a patch-wise hand-crafted map? Maximally
fair, matched design — same striped diagrams, same `stripe_contrast` metric, a
hand-crafted per-column map built at the CNN map's own column resolution from a
GBM (`spreading_rate`) trained on the full uniform training diagrams (mirroring
the CNN's train-global/apply-local recipe), best window width reported. Registered
8a panel (78 pairs), periods {32, 16, 8, 4}, 16 ICs.

| checkpoint | CNN resolution limit | best hand-crafted limit | R(16): CNN vs best hc | verdict |
|---|---|---|---|---|
| 7×7 `lever_a_local` | 32 px | **16 px** (8px window) | 0.27 vs **0.62** | hand-crafted **finer** |
| 15×15 `lever_a_shallow` | 16 px | 16 px (8px window) | 0.63 vs 0.57 | **tie** |

At the CNN's best resolution (15×15) it merely **ties** an 8-pixel hand-crafted
window; at 7×7 the hand-crafted map resolves *finer*. Both are blind at period 8
(R(8) ≈ 0.2 for both). So the learned spatial map buys **no** resolution the
cheap sliding window doesn't already provide, and the deep encoder — trained only
on uniform diagrams and applied locally — is *not* what makes the maps work: a
GBM on five statistics, likewise trained on uniform diagrams and applied locally,
does the same.

### S2 — error bars (5+5+3 seeds, corrected targets, matched comparison)

Retrained the headline checkpoints varying only `cfg.seed` (weight init +
optimisation order; split/targets fixed), on the identity-seeded targets, and
re-ran the matched CNN-vs-baseline comparison per seed. Mean ± s.d.:

| task | baseline (GBM) | amortiser (seeds) | margin |
|---|---|---|---|
| ECA global | 0.927 | **0.852 ± 0.015** | −0.074 ± 0.015 (baseline wins, all seeds) |
| range-2 global | 0.845 | **0.864 ± 0.014** | +0.019 ± 0.014 (tie) |
| range-2 complex | 0.795 | **0.832 ± 0.022** | +0.037 ± 0.022 (tie) |

Complex signed spreading-rate bias (CNN): **0.014 ± 0.020** (unbiased; vs the
ECA §6 pull +0.17 / −0.26). Map resolution limit: **7×7 → hand-crafted finer at
all 5 seeds** (CNN 32 px vs 16 px); **15×15 → tie at all 3 seeds** (16 vs 16).
The deep amortiser never clears the pre-registered +0.10 advantage margin on any
task, and is beaten outright on the elementary space — the negative is robust to
the training seed, not a single-run artefact. These are the numbers reported in
the manuscript (`manuscript/`, Chaos/AIP format).

**Bottom line (all four controls + map control).** For estimating CA
damage-spreading invariants under this protocol — globally, for novel complex
rules in the enlarged range-2 space, *and* as spatially-resolved maps — a deep
CNN provides **no advantage** over cheap hand-crafted single-diagram statistics.
The damage invariants are texture-predictable and the maps are cheaply
computable. This is a clean, pre-registered **negative result for deep
amortization**. What remains genuinely positive and publishable: (i) the
protocol-tuple framing; (ii) the range-2 landscape (complex ≈ 7.8%,
CI [6.9, 8.8]% vs ~2% for ECAs); (iii) a **training-free, interpretable spatial
phenotype-map method** for non-uniform CA (the hand-crafted patch map,
resolving to ≈16 px); and (iv) the benchmark/negative itself. Per the standing
decision to write only on a clear positive *deep-learning* result, the
CNN-centric manuscript is **not** written; direction (honest cheap-method +
benchmark paper vs. pivot to a predictive/forecasting objective where the
literature expects learning to add value — FOUNDATIONS §4 Lever B) is a user
call.
