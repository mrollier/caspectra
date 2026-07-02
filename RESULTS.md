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
