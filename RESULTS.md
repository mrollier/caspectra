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
