# RESULTS.md — measured record & decision gates

Running log of *measured* outcomes (predictions and critique live in
`SELF_CRITICISM.md`; pass/fail thresholds in `EVALUATION_CRITERIA.md`).

---

## 2026-08-21 — Round-6 review-response results (rev 14; M13 + rho variability)

Decision and reporting rules registered numbers-free in EVALUATION_CRITERIA.md
rev 14 (commit 56f6936) **before** any number below. Fifth review
(`manuscript/reviews/review_deepseekv4pro_20aug26.md`, major revision).

### Finite-replicate variability of the rho references (rev-14 re-expression)

The fifth review objected that the rho reference values (√2 / 1) are called
"exact" while the pooled denominator rests on K = 20 replicates per rule.
Delta-method decomposition under a Gaussian working model
(`scripts/analyze_rho_variability.py`, artifact
`runs/analysis/rho_variability/summary.json`), per target and space, of the
SD of an exactly-matched resimulator's observed rho around √2:

| source | worst case over all 8 target×space cells |
|---|---|
| finite-K denominator (the reviewer's point) | **0.14 rho-units** (ECA fraction) |
| total incl. finite-panel numerator | **0.65 rho-units** (ECA fraction; radius-2 worst 0.58, cone fill) |

Numerator and denominator are *independent* by the seeding design (prime seed
offsets on per-rule SeedSequences), which is the half of the objection we
rebut. The finite-panel share is what the manuscript's rule-bootstrap CIs
already carry; the mechanistic rho spread in Table III (0.7–1.8, every CI
covering √2) is exactly this scatter — the ECA spreading-rate value 0.7 is
~1 SD below √2, not an anomaly. Manuscript wording downgraded to
"exact in expectation" everywhere (abstract, Sec. II C, Table III caption).

### Mode-assignment accuracies promoted to exact values

Sec. IV A now quotes per-estimator ordered/chaotic mode accuracy from the A5
artifact (was "89–100%"): ECA gbm 0.89 / CNN 0.94; radius-2 gbm 0.99 / CNN 1.00.

### M13 — matched-regime CNN with checkpoint selection (registered)

(placeholder — filled after the five-seed runs and full-table scoring)

### Round-6 manuscript restructure (fifth review, length)

17 pp (after round-6 statistical additions) → 16 pp: abstract 255→~200 words
in plain language (no ICC/√2 symbols); all revision-number tags removed from
the main body (registration record stays in Appendix A); Tables II+III merged
into one per-target table; cost subsection 43→~30 lines (GPU/batched timings,
32-pair point → repo record only); by-products compressed to two paragraphs
with the landscape figure, coordinate caveats, ECA validation and detector
null moved to new Appendix D; Table I gains the M10 stratified-split row
(enriched panel stays the registered primary). Nothing deleted from the repo;
audit exit 0 throughout.

## 2026-08-20 — Round-5 review-response results (rev 13; M9–M12 + re-expressions)

Decision and reporting rules registered numbers-free in EVALUATION_CRITERIA.md
rev 13 (commit 1cd55b7) **before** any number below. Fourth review
(`manuscript/reviews/review_opus5_20aug26.md`, major revision).

### M10 — stratified split without force-holding (registered)

The canonical panel force-holds all 57 signature-complex rules, leaving **zero**
of them in training where a representative split would hold ~7%. The CNN was
retrained (3 seeds) on a stratified leave-rules-out split with force-holding
disabled — 52 of the 57 signature-complex rules in training, 5 (3.1%) held out —
and every family rescored on that panel.

| family | stratified panel | enriched panel |
|---|---|---|
| mechanistic | **0.992** | 0.991 |
| 5 statistics (GBM) | 0.780 | 0.845 |
| deep CNN | **0.778** (seeds 0.74–0.78) | 0.859 |

Registered rule: downgrade the family-gap claim to the stratified number if any
target's gap shrinks by more than 0.10 median R² against the post-stratified
gap. **No downgrade** — the largest shrink over both direct estimators is 0.07
(GBM cone fill), while two of the CNN's gaps *widen*: survival by 0.16 and cone
fill by 0.34. Representative training does not close the gap; the enrichment
was flattering the network, not handicapping it.

Counter-observation, on 5 rules and therefore weak: with 52 complex rules in
training the CNN still scores −0.81 on the 5 held-out complex rules against 0.78
on the rest, reversing the direction seen on the enriched panel (0.832 complex
vs 0.821 random). Artifact: `runs/m4_range2_strat/control/`.

Implementation note worth recording: `HeldOutPredictions.complex_mask` derives
membership from `cfg.train.force_holdout_rules`, which this control empties by
design, so it is identically False here. The scorer reads the signature set from
the canonical config instead — the first run reported "0 signature-complex" and
was wrong for that reason.

### M11 — retrieval baseline (registered). The most uncomfortable number.

Nearest-training-rule lookup: no training, no simulation, return the cached
target of the nearest training rule; predictions averaged within rule as for
every direct estimator.

| metric space | radius-2 median R² | ECA median R² |
|---|---|---|
| five statistics | 0.821 | 0.828 |
| **CNN bottleneck** | **0.862** | **0.881** |
| *(trained CNN, for comparison)* | *0.864* | *0.852* |

Retrieval in the network's own bottleneck is level with its regression head on
radius two and **exceeds** it on ECA. Under the registered interpretation rule
this is evidence that the direct estimators' accuracy on this benchmark is
substantially rule recognition rather than extrapolation to unseen tables.
Consistent with the rev-8 identity probes (0.95 balanced accuracy from the same
bottleneck). Artifacts: `runs/{m4_range2,lever_a_local}/retrieval/`.

### M12 — horizon-matched cross-space prevalence (registered)

The horizon ⌊w/2r⌋−1 is 62 for ECA and 30 for radius two at w = 127, so the
manuscript's "7.8% vs 3/88" compared two different experiments.

| ECA horizon | prevalence | signature set | precision vs class IV |
|---|---|---|---|
| T = 62 (as published) | 3/88 = 3.4% | {54, 106, 110} | 2/3 |
| **T = 30 (matched)** | **6/88 = 6.8%** | {37, 45, 54, 60, 106, 110} | **1/3** |

Radius two is 7.8% (Wilson [6.9, 8.8]%). **At matched horizon the cross-space
gap essentially closes.** Per the registered reporting rule the confounded form
is withdrawn from the manuscript. Artifact:
`runs/analysis/glider_validation_T30/`.

### Zero-simulation re-expressions (post-hoc confirmatory; rules fixed in rev 13)

`scripts/analyze_round6_metrics.py` → `runs/analysis/round6_metrics/summary.json`.

**(a) ρ = RMSE/σ̂_e, per-rule σ̂_e, pooled as √(Σeᵢ²/Σσ̂ₑ²(i)).** √2 is the
simulation-limited benchmark and 1 the latent ceiling, exactly.

| target | ECA mech / stats / CNN | radius-2 mech / stats / CNN |
|---|---|---|
| survival | 1.4 / 6.0 / 6.4 | 1.4 / 4.0 / 3.0 |
| fraction | 1.2 / 20 / 33 | 1.4 / 7.2 / 8.7 |
| rate | 0.7 / 27 / 27 | 1.5 / 9.5 / 11 |
| cone fill | 1.8 / 13 / 15 | 1.0 / 5.2 / 6.4 |

Every mechanistic CI covers √2; every direct-estimator CI is far above it. The
pooled form (not an average of per-rule ratios) is what makes both reference
values exact and what survives the rules with σ̂_e = 0 — the fully ordered ones,
3/18 on ECA and 1/160 on radius two, on which the mechanistic error is also
exactly zero.

**(b) Per-panel reliability.** ICC recomputed inside each decomposition; the
post-stratified row reweights strata to the 7.1% universe prevalence. Median
2·ICC−1: enriched 0.985, random 0.988, post-stratified 0.987, complex 0.979.
**Max |ICC shift| vs the universe sample: 0.010** — the referee's objection is
structurally valid but small in magnitude.

**(c) Target dependence.** fill vs (w/2rT)·fraction/rate: **R² = 0.637**
(3000-rule landscape), **0.702** (160-rule panel), Pearson r = 0.857. The
registered threshold for declaring cone fill a derived coordinate was R² > 0.95.
**Not met** — cone fill carries independent information.

**(d) Frontier ceilings.** The grid scores an estimator simulating at n against
the **256-pair production cache**, so the read-then-simulate ceiling is
1 − (1 + 256/n)(1 − ICC): median 0.963 at n = 64 (Fig. 1), 0.953 at n = 48
(Fig. 2); a direct estimator keeps the ICC ceiling, 0.993. *Not* 2·ICC−1
evaluated at reduced budget.

**(e) Survival-band stratification.** Restricted to survival ∈ [0.1, 0.9]
(14/18 ECA orbits, 40/160 radius-two rules):

| | ECA full → band | radius-2 full → band |
|---|---|---|
| mechanistic | 0.985 → 0.895 | 0.977 → 0.939 |
| 5 statistics | 0.708 → **−0.871** | 0.809 → 0.409 |
| CNN | 0.667 → **−1.255** | 0.888 → 0.664 |

Mode accuracy stays 0.89–1.00 throughout. **The direct estimators' survival
skill is mode assignment**: within the band they are worse than the band mean on
ECA.

**(f) Reconstruction-failure analysis.** The four radius-two rules with
incomplete first-diagram coverage miss one entry of 32 each; mean |error| is
0.017 vs 0.016 (survival) and 0.008 vs 0.009 (cone fill) against fully covered
rules, and *smaller* on fraction (0.0009 vs 0.0041) and rate (0.0017 vs 0.0084).
The failures are dynamically benign: an entry the diagram never exercises is one
the dynamics rarely reaches.

**(g) Fig. 3 decorrelation.** Signature rules span 1.5× in damage fraction vs
2.6× for the bulk, and in decorrelated coordinates (rate vs N/2rT) the tightest
box containing all 234 of them also contains 732 ordinary rules (F1 = 0.39). The
red region is a **threshold region, not a discovered cluster**; the caption now
says so.

---

## 2026-07-06 — Round-4 review-response analyses (rev 11; M1–M7)

Decision rules pre-registered numbers-free in EVALUATION_CRITERIA.md rev 11
(commit a4ffef7) **before** any number below. Third review
(`manuscript/reviews/paper_third_review.md`): C1 budget-indexed dominance
claim, C2 evaluation unit, C3 enriched panel, C5 paired equivalence, C6/C8
seed + panel stability, C7 stacking status.

### M1 — reference-rescoring of every estimator
(`runs/m4_range2/reference_rescore/summary.json`,
`runs/lever_a_local/reference_rescore/summary.json`; cache vs the rev-8
4096-pair reference, zero new simulation)

| estimator (radius 2) | vs cache | vs reference | shift |
|---|---|---|---|
| mechanistic | 0.9907 | **0.9952** | +0.0045 |
| deep CNN (seed 0) | 0.8589 | 0.8586 | −0.0003 |
| boosted baseline | 0.8445 | 0.8518 | +0.0073 |
| ridge | 0.7092 | 0.7100 | +0.0008 |
| degaug CNN | 0.7864 | 0.7879 | +0.0015 |
| resnet18 | 0.8325 | 0.8346 | +0.0021 |

ECA: mechanistic 0.9991→0.9996; CNN 0.8495→0.8507; gbm 0.9266→0.9246.
**Reading (registered rule):** the fresh-simulation estimator rises to the
ICC ceiling; every direct estimator's score is unchanged within ~0.007 — the
direct shortfall is estimator error, not label noise. Answers reviewer Q8;
empirically closes the C1 headroom scenario for the estimators tested.

### M2 — paired equivalence for "simulation-limited"
(`runs/*/paired_equivalence/summary.json`; K=20 replicates regenerated
bit-exactly from registered seeds on the exact held-out panels; margin_t =
max(0.01, 1−ICC_t))

| target | panel | paired diff | CI95 | margin | equivalent |
|---|---|---|---|---|---|
| survival | r2 | +0.0007 | [−0.0081, +0.0093] | ±0.0130 | **yes** |
| fraction | r2 | −0.0000 | [−0.0009, +0.0008] | ±0.0100 | **yes** |
| rate | r2 | −0.0004 | [−0.0014, +0.0004] | ±0.0100 | **yes** |
| cone fill | r2 | +0.0059 | [−0.0086, +0.0217] | ±0.0204 | no (favourable side) |
| survival | ECA | +0.0003 | [−0.0157, +0.0151] | ±0.0100 | no (N=18 resolution) |
| fraction | ECA | +0.0002 | [−0.0000, +0.0035] | ±0.0100 | **yes** |
| rate | ECA | +0.0001 | [−0.0000, +0.0045] | ±0.0100 | **yes** |
| cone fill | ECA | −0.0004 | [−0.0045, +0.0015] | ±0.0100 | **yes** |

**Registered wording rule applied:** 6/8 formally equivalent;
"statistically indistinguishable" replaced by the precise per-target
statement in §IV.A; the two failures are CI-width failures (ECA survival:
18 rules; r2 cone fill: overshoot only on the side where the mechanistic
estimator *beats* the replicate).

### M3 — enriched-panel decomposition
(`runs/m4_range2/panel_decomposition/summary.json`; 57 forced signature +
103 stratified-random; universe share 57/800 = 7.1%, panel share 35.6%)

| method | signature | random | enriched (published) | post-stratified |
|---|---|---|---|---|
| mechanistic | 0.9823 | 0.9948 | 0.9907 | **0.9940** |
| deep CNN (seed 0) | 0.8663 | 0.8212 | 0.8589 | 0.8296 |
| boosted | 0.7946 | 0.8489 | 0.8445 | 0.8488 |
| ridge | 0.6768 | 0.7094 | 0.7092 | 0.7100 |

**Reading:** the enrichment is *conservative* for the paper's claim —
representative reweighting raises the mechanistic median and lowers the
CNN's, widening the gap (0.132 → 0.164). Disclosure attached in the artifact:
signature membership derives from the same seed-0 target cache used for
evaluation labels (registered criterion-9 thresholds; forced rules never
trained on).

### M4 — per-diagram reconstruction audit
(`runs/*/per_diagram_audit/summary.json`)

- Radius 2, all 10,240 held-out diagrams: per-diagram exact reconstruction
  **0.9904**, full-coverage share 0.9696, median coverage 1.0; per rule:
  first-diagram full coverage 0.9750 (= the published 156/160), union
  coverage 1.0000, all-64-diagrams-exact share 0.8125.
- ECA, all 4,608 held-out diagrams: every rate 1.0000.

### M6 — deployment-style stack (train-rules-fitted ridge over stats+CNN)
(`runs/m4_range2/deployment_stack/summary.json`)

Stack median 0.8835 CI[0.779, 0.910] vs CNN alone 0.8589. Stack-over-CNN:
survival **+0.0005** [−0.013, +0.019] n.s.; fraction +0.021 (adds value);
rate +0.030 (adds value); cone fill +0.044 n.s. **Reading:** the rev-7
cross-fitted survival complementarity (+0.32 diagnostic) does *not* deploy
via a train-once linear meta-model — the reviewer's C7 distinction is
empirically real and now stated in §IV.C.

### M7 — complement-panel replication of the frontier noise axis
(`runs/m4_range2/frontier_grid_complement/summary.json`; the 80 held-out
rules the canonical subsample excluded; identical budgets/estimators)

| noise | det | F1(est) | F2-s | frozen CNN | degaug CNN |
|---|---|---|---|---|---|
| 0% | 0.978 | 0.996 | 0.02 | 0.845 | 0.681 |
| 2% | 0.744 | 0.757 | 0.03 | 0.466 | 0.704 |
| 3% | 0.737 | **0.792** | 0.09 | 0.415 | 0.705 |
| 5% | 0.665 | 0.700 | 0.20 | 0.340 | **0.710** |
| 7.5% | 0.587 | 0.611 | 0.14 | 0.202 | **0.695** |
| 10% | 0.329 | 0.365 | 0.20 | 0.049 | **0.641** |
| 15% | −0.294 | −0.185 | 0.22 | −0.262 | **0.351** |
| 20% | −1.124 | −0.994 | 0.08 | −0.495 | 0.090 (CI spans 0) |

**Registered verdict rule:** no cell winner re-stated (no alternative's
CI_low clears the original winner's CI_high anywhere). Family structure
replicates; two measured panel sensitivities: (a) degaug band 0.35–0.71 here
vs 0.51–0.62 canonical; (b) the pseudo-posterior's collapse point moves
(holds 0.79/0.70/0.61 at 3/5/7.5% here vs collapsed by 5% canonically) — the
posterior→network crossover is a panel-dependent band ~3–7.5%, now stated as
such in §IV.F and Table V. Registered dead-zone extension rule on this
panel: met at 3–10%; at 15% narrowly not (degaug CI_low 0.210 vs reader
point 0.218; met canonically).

### M5 — seed replication of the degradation-trained control
(gated; 63 px smoke passed; seeds 1, 2 trained with `--seed`, all else
identical; noise-axis evals `runs/m4_range2/frontier_grid_degaug_seed{1,2}/`,
clean-panel `runs/m4_range2/reference_rescore_seedrep/`)

Canonical-panel noise cells, median held-out R² (seed-0 CI from rev-10):

| noise | seed 0 [CI] | seed 1 | seed 2 | in seed-0 CI? (s1/s2) | best read point |
|---|---|---|---|---|---|
| 3% | 0.554 [0.36, 0.65] | 0.296 | 0.486 | ✗ / ✓ | 0.377 |
| 5% | 0.585 [0.38, 0.68] | 0.271 | 0.548 | ✗ / ✓ | −0.019 |
| 7.5% | 0.610 [0.41, 0.70] | 0.264 | 0.545 | ✗ / ✓ | 0.024 |
| 10% | 0.619 [0.44, 0.70] | 0.240 | 0.548 | ✗ / ✓ | 0.166 |
| 15% | 0.511 [0.34, 0.60] | 0.331 | 0.557 | ✗ / ✓ | −0.036 |
| 20% | 0.169 [−0.05, 0.37] | **0.307** [0.06, 0.43] | **0.428** [0.25, 0.52] | — | 0.122 |

Clean 160-rule panel (rule-level median): seed 0 **0.786**, seed 1 **0.590**,
seed 2 **0.730** (clean-trained CNN 0.859). Grid clean cell: 0.510 / 0.288 /
0.368 (frozen CNN 0.654) → robustness tax 0.14–0.37 across seeds.

**Registered stability rule: FAILS** (seed 2 passes every band cell; seed 1
falls below the seed-0 CI at every band cell, at 15% by 0.012). Training
converged identically (train MSE
0.61→0.31 both seeds); epoch-to-epoch validation swings of ±0.2 under
augmentation implicate final-epoch selection variance. Per the registered
rule the manuscript now reports the band as a **per-seed range**: 0.24–0.62
(two of three seeds: 0.49–0.62).

**What is seed-stable:** at every cell 5–20% noise, *every* seed's point
median exceeds the best read-then-simulate estimator's; rev-10 CI extension
rule met by seed 0 at 3–15%, seed 2 at 5–15%, seed 1 at 15% only. At 20%
noise reliability itself is seed-dependent: seeds 1 and 2 clear zero
(0.31/0.43) where seed 0 (0.17, CI spans 0) and the complement-panel
evaluation (0.09) do not — Table V's 20% row re-worded accordingly. The
corruption-adaptation conclusion (rev-10) stands at the family level; the
level a practitioner gets from one training run at this budget varies by
~2×. Reviewer C6's single-seed concern is thereby *vindicated and priced*.

---

## 2026-07-05 — Round-3 fairness controls + reporting completions (rev 10)

Decision rules pre-registered numbers-free in EVALUATION_CRITERIA.md rev 10
(commit c16cc2b) **before** any number below. Questions: (C-i) does the
degraded-regime guidance survive when the direct family receives exactly the
adaptation the rev-9 reader received, and (C-ii) is the matched-regime
negative result an artifact of the anti-shortcut constraint? Plus two
registered reporting completions (F1 interval calibration; stacking under the
headline base).

### Training (gated; 63 px smokes first; single seed 0, disclosed)
- **C-i degaug CNN**: canonical architecture (31,524 params), rev-9 registered
  degradation augmentation on training batches (`caspectra/degradation.py`),
  60 epochs; wall-clock 30:03 (vs ~22 min clean — augmentation overhead).
  `runs/m4_range2_degaug/`.
- **C-ii resnet18**: 11,172,292 params (354× the constrained CNN),
  clean-trained, identical data/split/targets/epochs/batch/optimizer;
  wall-clock 1:29:09. `runs/m4_range2_resnet/`.

### Frontier (same 80-rule panel and cells as the rev-9 grid, regenerated from
the same seeds; controls evaluated as frozen forwards via `--direct-only`;
`runs/m4_range2/frontier_grid_controls/summary.json`, verdicts joined against
the canonical grid)

Noise axis, median held-out R² [CI95] (reference columns from the rev-9 grid):

| noise | C-i degaug | C-ii resnet | best rev-9 estimator |
|---|---|---|---|
| 0% | 0.51 [0.25, 0.64] | 0.55 [0.40, 0.69] | F1 0.99 |
| 2% | 0.52 [0.31, 0.63] | 0.59 [0.45, 0.74] | F1 **0.55** |
| 3% | **0.55** [0.36, 0.65] | 0.59 [0.46, 0.73] | F1 0.27 |
| 5% | **0.59** [0.38, 0.68] | 0.54 [0.42, 0.64] | CNN 0.15 |
| 7.5% | **0.61** [0.41, 0.70] | 0.48 | F2-s 0.02 |
| 10% | **0.62** [0.44, 0.70] | 0.25 | F2-s 0.17 |
| 15% | **0.51** [0.34, 0.60] | −0.19 | F2-s −0.04 |
| 20% | 0.17 [−0.05, 0.37] | −0.60 | F2-s 0.12 |

- **The noise dead zone was an adaptation artifact, not an estimator-family
  boundary.** C-i holds median R² 0.51–0.62 from 3% to 15% noise — where the
  best previously tested estimator (F2-sampled) never exceeded 0.17 — and
  satisfies the registered dead-zone rule (CI_low > F2-sampled point) at every
  noise cell up to 15% (not at 20%, where they are comparable: 0.17 vs 0.12).
  Rev-9's "learned system identification is the only estimator class that
  retains signal beyond ~5%" is **overturned as an estimator-class claim**: it
  was true only among degradation-naive direct estimators. What decides the
  noise band is *training for the corruption*, not the estimator family.
- **Robustness tax**: C-i pays ~0.14 on clean diagrams (0.51 vs the canonical
  constrained CNN's 0.65) and is nowhere near simulation-limited anywhere.
- **Masking/density: the Bayesian posterior still owns the intermediate
  band** — 0.85/0.59 at 40/50% masking vs C-i 0.48/0.48; density 0.1
  posterior 0.77 vs C-ii 0.46 / C-i 0.20. Beyond 50% masking every estimator
  fails (≤ −1.0). Polarity: read family exactly invariant, unchanged.
- **Hypothesis (iii) re-test with both controls in the direct family: 0
  violations** — at every high-table-recovery cell (per-bit ≥ 0.95) the best
  read-then-simulate estimator remains unbeaten. The matched-regime
  recommendation stands, now against a 354×-larger unconstrained control and
  a degradation-trained control.
- **C-ii does not rescue direct amortization**: on clean cells the
  unconstrained resnet18 is no better than the 31k constrained CNN (0.55
  [0.40, 0.69] vs canonical 0.65 [0.51, 0.76]) and degrades much faster under
  noise (−0.60 at 20%). The matched-regime negative result is not an artifact
  of the anti-shortcut constraint.

### Clean-protocol (160-rule panel, registered Table-III machinery reapplied
via `analyze_paired_stats.py` on each control's checkpoint; same split)

Per-target held-out R² (rule-level means):

| method | survival | fraction | rate | cone fill | median |
|---|---|---|---|---|---|
| constrained CNN (canonical ref) | 0.888 | 0.869 | 0.849 | 0.384 | 0.859 |
| **C-i degaug CNN** | 0.793 | 0.799 | 0.780 | 0.373 | 0.786 |
| **C-ii resnet18** | 0.850 | 0.846 | 0.819 | 0.696 | 0.833 |
| GBM (ref) | 0.809 | 0.909 | 0.880 | 0.596 | 0.845 |
| mechanistic (ref) | 0.977 | 0.997 | 0.997 | 0.985 | 0.991 |

- **Matched-regime verdict unchanged** (registered rule: a control changes
  the verdict only if its per-target CI reaches the replicate-agreement
  band — survival 0.974, fraction/rate 0.997, cone 0.959): the mechanistic
  estimator is A_superior over C-ii on **all four** targets (ΔR² +0.13
  [+0.06,+0.36] … +0.29 [+0.18,+0.48]) and over C-i on all four (+0.18 …
  +0.61). Neither control approaches the band anywhere.
- **C-ii trades targets rather than winning**: cone fill up (0.696 vs 0.384),
  survival/fraction/rate down, median 0.833 vs 0.859; against the GBM all
  four paired contrasts are *inconclusive*. 354× the parameters at the same
  budget changes no verdict.
- **C-i clean cost** on this panel: ~0.07–0.09 per target (median 0.786);
  vs GBM: fraction/rate/cone B_superior, survival inconclusive — the
  robustness that wins the noise band is paid for on clean diagrams.
- Artifacts: `runs/m4_range2_{degaug,resnet}/paired_stats/summary.json`.

### Reporting completions
- **F1 1σ predictive-interval calibration** (rev-9 outstanding item;
  `runs/m4_range2/frontier_grid_calibration/`): empirical coverage vs the
  nominal ~68.3% — **at or above nominal across the recommended masking band**
  (0.86 clean → 0.79 at 25% → 0.77 at 40% → 0.74 at 50%), conservative on
  clean diagrams, **degrading along the noise axis** (0.67 at 1%, 0.58 at 2%,
  0.45 at 5%, 0.13 at 20%): beyond its ~3% range the posterior is not merely
  inaccurate, its intervals are overconfident. The recomputation reproduced
  all 17 released grid medians **bit-exactly** (identical RNG tags) — a
  by-product reproduction audit of the released artifact.
- **Stacking under the headline base** (post-hoc confirmatory;
  `runs/m4_range2/stacking_gbm_base/`): CNN-over-GBM survival increment
  **+0.080 CI[+0.019, +0.176]** (clears the registered 0.02 margin; base
  0.802 → 0.883); fraction +0.010, rate +0.017, cone fill +0.123 — all n.s.
  Mechanistic-over-GBM adds value on all four targets (+0.089 … +0.526,
  stacked 0.976–0.995). The rev-7 headline +0.32 is therefore specific to the
  cross-fitted five-statistic ridge base; under the headline protocol the
  survival increment is +0.08 — still real, much smaller.

---

## 2026-07-05 — Identifiability frontier (rev 9; F1–F3)

Decision rules pre-registered numbers-free in EVALUATION_CRITERIA.md rev 9
(commit 8f5cb56) **before** any number below. Question: where exact rule
reading fails (rev-8 C4), do a Bayesian rule-posterior simulator (F1) and a
learned rule-reader→simulator (F2) restore simulation-limited accuracy?
Primary panel = the rev-8 identifiability panel (80 held-out range-2 rules,
fixed seed); grid at n_pairs=48, n_samples=8 (`runs/m4_range2/frontier_grid/`).

### F1 — Bayesian rule-posterior simulator (post-hoc confirmatory axes)
Median held-out R², F1(ε-estimated) vs deterministic inverter vs frozen CNN:

| axis | F1 | det | CNN | reading |
|---|---|---|---|---|
| noise 0.5% | **0.86** | 0.79 | 0.61 | F1 > det everywhere on 0–3% |
| noise 2% | **0.55** | 0.38 | 0.44 | hypothesis (i) confirmed |
| noise 3% | 0.27 (ε-known **0.38**) | 0.09 | 0.25 | F1's last stand |
| noise ≥5% | ≤ −0.84 | ≤ −1.07 | **0.15 → −0.93** | crossover: nothing works well — F2's target zone |
| mask 40% | **0.85** | 0.24 | −0.03 | F1 extends masking tolerance ~2× |
| mask 50% | **0.59** | −0.77 | −0.03 | |
| density 0.1 | **0.77** | 0.08 | 0.38 | posterior rescues under-exercised tables |
| label flips 100% | **0.99** | 0.94 | 0.59 | mechanistic family polarity-invariant, as predicted; GBM exactly invariant (0.75) |

ε self-consistency estimation ≈ matches ε-known (within ~0.1 R² everywhere;
sometimes better — it captures the *effective* corruption incl. input-side
flips). **Unknown-radius axis:** parsimony selection costs ~0.12 R² at zero
noise (det-selected 0.83 vs det-known 0.95) and degrades under noise (0.37 vs
0.41 at 2%) — radius knowledge is a real, now-quantified assumption.
**Verdict per registered rule:** F1 "restores identification" on the
intermediate band (noise ≲3%, mask ≲50%, density extremes); above ~5% noise
no read-then-simulate estimator survives and the frozen CNN is merely least
bad (negative R²) — the open slot F2 addresses.

### F2 — learned rule-reader→simulator (exploratory)
Training approved (user, 2026-07-05; range-2, 1 seed, 15 epochs, 29,664
params, train-split rules only, registered degradation augmentation;
`runs/m4_range2/rule_reader_seed0.pt`). Training: BCE 0.664→0.527, monitor
bit-acc 0.759 (train-split tail). On the 80-rule held-out panel (clean
diagrams): **per-bit accuracy 0.734, exact-table rate 0.000** — at this
capacity the reader never reconstructs a full 32-bit table.

Grid, noise axis (median held-out R²; F2-sampled = averaging simulations of
8 tables drawn from the predicted per-bit probabilities):

| noise | best F1 | F2-MAP | F2-sampled [CI95] | frozen CNN | det |
|---|---|---|---|---|---|
| 3% | **0.38** | −3.62 | 0.09 [−0.45, 0.36] | 0.25 | 0.09 |
| 5% | −0.84 | −3.46 | −0.02 [−0.57, 0.28] | **0.15** (stack 0.10) | −1.07 |
| 7.5% | −1.46 | −3.75 | **0.02** [−0.50, 0.27] | −0.13 | −1.60 |
| 10% | −2.11 | −3.86 | **0.17** [−0.35, 0.37] | −0.25 | −2.02 |
| 15% | −3.42 | −3.60 | **−0.04** [−0.46, 0.15] | −0.57 | −3.42 |
| 20% | −5.33 | −2.59 | **0.12** [−0.22, 0.27] | −0.93 | −5.61 |

- **F2-MAP fails everywhere** (median R² −2.2 … −24.9 across all axes; exact
  0.000): thresholding 0.73-accurate bit probabilities into a single table
  concentrates the errors. All the salvageable signal is in the *sampled*
  variant — posterior averaging over the reader's uncertainty.
- **F2-sampled is the only estimator that does not collapse in the dead
  zone**: it beats F1 at every noise cell ≥5% (Δ vs best-F1 +0.8 to +5.5),
  is the best of *all* estimators from 7.5% on (at 5% the direct family is
  still marginally positive: CNN 0.15, stack 0.10), and satisfies the
  registered beats-the-inverter rule at every cell ≥5% (bootstrap CI_low >
  det point value). But its absolute level (median ≤0.17, CI spanning 0)
  is nowhere near simulation-limited — it holds the line at ~zero, flat in
  noise (bit-acc 0.73→0.70 from 0→20%: the augmentation made it corruption-
  robust at a low ceiling).
- **On masking F2 adds nothing**: F1 holds to 50% (0.59); F2-sampled never
  rises above 0.09 anywhere and is −1.8/−2.4 at 75/90%. Same on density
  (≤ −0.09) and label flips (−0.49 at 100%; read-then-simulate stays 0.99).

### F3 — registered hypothesis verdicts (rev 9)
- **(i) confirmed** (see F1 above): the Bayesian posterior dominates the
  deterministic inverter across the intermediate band and degrades gracefully.
- **(ii) split verdict, reported as registered**: F2 *does* extend further
  into the degraded regime than F1 on the noise axis (beats F1 at every cell
  ≥5%, best overall from 7.5%, registered rule satisfied) — but only in the
  weak sense of moving the frontier, not restoring identification (median
  ≤0.17). On the masking axis the hypothesis is **refuted**: F1 extends
  further, F2 never leaves zero.
- **(iii) confirmed, 0 violations**: at no grid cell where read-family table
  recovery is high (bit accuracy ≥0.95) does any direct amortizer (CNN, GBM,
  stack) beat the best read-then-simulate estimator (point above its CI_high).

**Provenance note.** The first F2-inclusive grid run was launched with a
non-canonical direct-CNN checkpoint (`runs/m4_range2/checkpoint_final.pt`
instead of the rev-8 canonical `runs/m4_range2_seed0/checkpoint_final.pt`);
its cnn/stack columns were therefore inconsistent with every committed rev-8/9
number. The run was discarded and fully re-measured with the canonical
checkpoint. Audit: the F1-only grid summary is preserved as
`runs/m4_range2/frontier_grid/summary_f1only.json`; the final run reproduces
every shared estimator column bit-exactly (checked programmatically), incl.
cnn/stack. Figure: `runs/m4_range2/frontier_grid/frontier.pdf` =
`manuscript/figures/identifiability_v2.pdf`.

**Correction (2026-07-05, round-3 revision).** The F2 noise table above and
its 5%-cell bullet were first written from the discarded run's cnn/stack
cells (cnn 0.36 / 0.13 / −0.09 / −0.34 / −0.73 / −1.09; stack 0.14 at 5%) —
the in-session reproduction audit covered the shared F1 columns but not these
six cells, and the manuscript inherited "−1.1" from here. Found by the
internal ARS review (`manuscript/reviews/simulated/r1_methodology.md` W1);
re-derived from the canonical `summary.json` (cnn 0.25 / 0.15 / −0.13 /
−0.25 / −0.57 / −0.93; stack 0.10 at 5%). Conclusion-preserving: no bolded
best-of-row cell and no registered verdict changes.
`scripts/audit_manuscript_numbers.py` now re-derives every §IV.E prose
number and these table cells from the artifact and fails on mismatch.

---

## 2026-07-04 — Round-2 review-response results (rev 8; C1–C8)

Measured after the second referee report returned **major revision**
(`manuscript/reviews/chaos_second_review.md`); decision/reporting rules
pre-registered numbers-free in EVALUATION_CRITERIA.md rev 8 (commit 75e1d42)
**before** any number below. Two integrity fixes drove the round: (A) the
"dominates / never beats" narrative contradicted our own tables — retired; (B)
the ICC "ceiling" is the wrong benchmark for the mechanistic estimator
(an independent MC draw ⇒ expected R² = **2·ICC−1**, not ICC) — corrected.

### C2 — three reliability benchmarks, distinguished (K=20, rule-bootstrap CIs)
ECA (88 rules): ICC 0.9936/0.9988/0.9995/0.9992 (survival/fraction/rate/fill);
**independent-replicate agreement** 0.9871/0.9975/0.9991/0.9984 (matches
2·ICC−1 to 4 decimals). Range-2 (250 rules): ICC 0.987/0.998/0.998/0.980;
agreement 0.974/0.997/0.997/0.959. The two benchmarks differ by 2–7× the
margins at stake on the noisy targets — which one you cite matters.

**Mechanistic vs the right benchmarks:** vs noisy cache — ECA survival 0.985
(agreement benchmark 0.987 CI[0.978,0.992]); range-2 survival 0.9765
(benchmark 0.9739), fill 0.9849 (0.9594 CI[0.900,0.987]) — **at benchmark on
every target, both spaces**. vs 4096-pair near-noise-free reference — ECA
survival 0.9943 (ICC 0.9936), range-2 survival 0.9877 (ICC 0.987) — **at the
ICC ceiling**: the old "shortfall" was comparison-target noise. The corrected
statement is *stronger* than the erroneous one.

### C3 — coverage & completion-policy sensitivity
ECA: 18/18 held-out tables fully covered → policies identical. Range-2:
156/160 fully covered; 4 rules miss 1 entry each (coverage min 0.969);
default-0/default-1/empirical median R² 0.9907/0.9908/0.9905 (< 0.001 apart).
Posterior-averaged variant gives predictive intervals on the 4 under-covered
rules (1σ coverage 0.25–1.0 per target; n=4, indicative only). "Parameter-free"
retired; estimator described as matched-model system identification with a
weak, testable completion prior.

### C4 — identifiability phase diagram (exploratory; no training)
Range-2, 80 held-out rules, frozen CNN. **Rows**: mechanistic ≥0.95 from as few
as 4 observed rows. **Bit-flip noise**: mechanistic 0.96 → 0.61 (1%) → 0.30
(2%) → −0.92 (5%); frozen CNN 0.65 → 0.58 → 0.43 → 0.09 — **crossover at
~2–5% noise** (deterministic tables have no noise model; one corrupted
transition flips an entry). **Masking**: mechanistic robust to 25% (0.90),
collapses by 50% (−0.20); CNN degrades gracefully — crossover ~40%.
**IC density**: mechanistic flat at benchmark for p∈[0.25,0.75] (it
re-simulates under the reference protocol regardless of observed density) but
0.12 at p=0.1 (table not exercised); CNN/baseline degrade off training density.
Figure: `manuscript/figures/identifiability.pdf`. This is the paper's scope
statement in graphical form.

### C5 — complete per-target tables (rule-bootstrap 95% CIs; 5 CNN seeds)
Range-2 (N=160): survival mech 0.977 [0.930,0.989] | 5-stat 0.809 [0.554,0.906]
| CNN 0.874±0.009; fraction 0.997 | 0.909 | 0.880±0.020; rate 0.997 | 0.880 |
0.865±0.020; fill 0.985 [0.969,0.992] | 0.596 [0.320,0.775] | **0.337±0.109**.
ECA (N=18): survival 0.985 | 0.708 [−0.54,0.92] | 0.700±0.018; fraction 1.000 |
0.924 | 0.789±0.038; rate 1.000 | 0.965 | 0.956±0.015; fill 0.999 | 0.929 |
0.916±0.019 (wide baseline CIs = honest under-power).
**Verdicts (δ=0.05):** CNN−GBM: survival +0.079 CI[0.00,0.20] (sub-margin CNN
edge), fill −0.212 **B_superior**, fraction/rate inconclusive (equivalent only
at δ=0.10) — *no stable ordering*. Mech−GBM: A_superior on survival/rate/fill;
mech−CNN: A_superior on fraction/rate/fill; the 2 remaining contrasts have CIs
excluding 0 in mech's favour, points just below 0.10. Margin sensitivity: at
δ=0.02 ECA-rate equivalence reverts to inconclusive; at δ=0.10 range-2
fraction/rate become equivalent; no superiority verdict changes.
**Split uncertainty:** baseline leave-one-orbit-out (88 ECA orbits)
0.73/0.85/0.95/0.93 — consistent with the registered split; range-2 over 20
outer splits: survival 0.76 (0.56–0.84), fraction 0.92, rate 0.90, fill 0.68
(0.55–0.75). Mechanistic is split-invariant (no trained parameters).

### C5b — stacking with full stacked-model R²
CNN over 5 stats: survival +0.320 CI[0.23,0.48], **base 0.556 → stacked
0.876**; fraction +0.034 (0.851→0.885); rate +0.030 (0.839→0.869); fill n.s.
5 stats over CNN: nothing (survival −0.009). Mechanistic over 5 stats: +0.14 to
+0.84, stacked 0.97–0.995 everywhere. The net's survival information is real
and large; it is also strictly dominated by reading the rule.

### C6 — confusion matrices (raw agreement retired as headline)
ECA damage signature vs literature class-IV truth {54,110}: sensitivity 1.0,
specificity 0.988, precision 2/3 (the 1 FP = borderline 106), balanced acc
0.994 — **the signature is near-perfect where ground truth exists**. The
independent localized-seed detector is the weak instrument: vs literature
sensitivity 0.5 (misses 54, light-speed ether), precision 0.17, BA 0.71.
Range-2 (300 rules): signature fraction 8.3%; detector vs signature BA 0.39,
precision 0.05 (n=231) — single-observable glider detection unreliable in the
large space; landscape stays "damage-signature landscape", no glider census
claimed.

### C7 — nuCA map verdict corrected
Resampling unit = composed system (rule pair; was already pair-level, now
stated). CNN 0.673 vs val-selected handcrafted 0.605 (oracle 0.638);
Δ=+0.047, CI95[−0.002,+0.102], CI90[+0.005,+0.092] ⇒ **inconclusive** under
the registered TOST framework (not "tie": the 90% CI is not inside ±0.05; not
superiority: point < 0.10). Honest summary: small, statistically unresolved
edge for the learned map.

### C8 — accuracy–compute Pareto (range-2)
Mechanistic per diagram: 17 ms @16 pairs (median R² **0.924** — already above
both direct estimators), 32 ms @32 (0.966), 283 ms @256 (0.991); single CPU
core, embarrassingly parallel. CNN forward 2.2 ms (Metal); 5-stat 1.4 ms.
One-time: CNN training ≈22 min/seed; GBM fit 15 s. Break-even ≈4700 queries.
The mechanistic curve is one-sided: most accurate at every measured budget.

### Net round-2 reframe
Title/spine: *rule reconstruction from a single diagram yields
simulation-limited prediction* (system identification is the baseline to
beat). Retired: "dominates deep networks", "never beats", "three tiers",
"skip the network", "tie", "smooth function of the rule", "parameter-free",
ICC-as-mechanistic-ceiling. Manuscript rewritten (8 pp), all analyses labelled
registered / post-hoc confirmatory / exploratory; Vispoel refs completed with
DOIs (10.1016/j.chaos.2024.114989; 10.1016/j.physd.2021.133074).

---

## 2026-07-04 — Review-response experiments (rev 7; R1–R8)

Measured after a referee recommended reject-in-current-form
(`manuscript/reviews/chaos_review.md`); decision rules pre-registered
numbers-free in EVALUATION_CRITERIA.md rev 7 (commit a809b2a) **before** any
number below. These reframe the paper around a **three-tier** result.

### R4 — mechanistic rule-inference estimator (the positive result)
Read the local rule off one diagram (`infer_rule`, exact for a fully-covered
table), then simulate the damage response with an independent RNG. Same
leave-rules-out splits as the CNN/baseline (seed-0):

| task | mechanistic | GBM baseline | CNN amortiser | reliability ceiling (R3) |
|---|---|---|---|---|
| ECA global (median R²) | **0.999** | 0.927 | 0.850 | 0.999 |
| range-2 global | **0.991** | 0.845 | 0.859 | 0.993 |
| range-2 complex | **0.982** | 0.795 | 0.866 | ≈0.98 |

Exact rule inference 1.00 (ECA) / 0.975 (range-2); coverage ≈1.0. The
interpretable estimator sits **at the reliability ceiling** and dominates both
the cheap statistics and the deep net. Per-feature ECA R²: survival 0.985,
fraction 0.9997, rate 1.0, fill 0.9985 — note survival, where CNN=0.667 and
GBM=0.708 both fall far short of the 0.994 ceiling.

### R3 — reliability-adjusted R² ceilings (ICC(1), K=20 replicates)
ECA (88 rules): survival 0.994, fraction 0.999, rate 0.9995, fill 0.999;
MC-noise std 0.022 / 0.004 / 0.006 / 0.009 (refines the old 0.006–0.014 claim,
which under-stated survival noise). Range-2 (250-rule subsample): survival
0.987, fraction 0.998, rate 0.998, fill 0.980; median 0.993. Read every method's
R² against these, not against 1.0.

### R1 — per-target paired inference (rule-cluster bootstrap, TOST δ=0.05)
Range-2 (N=160, powered): **mechanistic − GBM** A_superior on survival (+0.167),
rate (+0.117), fill (+0.389); **mechanistic − CNN** A_superior on fraction,
rate, fill. **CNN − GBM**: they trade — CNN a hair up on survival (+0.079, CI
excl 0), GBM clearly up on cone_fill (−0.212, B_superior); the rest wash. Neither
net/baseline dominates; both are far below the mechanistic estimator. ECA (N=18)
is underpowered per target (wide CIs) — mechanistic survival dominance still
A_superior; report ECA at the median level.

### R2 — incremental value / stacking (cross-fit, margin 0.02)
Range-2 (N=160). **Honest nuance:** the CNN *does* add incremental R² beyond the
five statistics — damage_survival **+0.320** (CI [+0.23,+0.48]), plus small
significant fraction/rate — but **not** cone_fill. The five statistics add
~nothing beyond the CNN (all False). The mechanistic estimator adds far more
everywhere (+0.14…+0.84). So the deep net carries real, mostly-survival
incremental information (exactly where texture is weakest — cf. referee §7), yet
is dominated by the interpretable estimator and never nears the ceiling. The
headline is therefore *not* "deep learning adds nothing," but "interpretable
rule-reading dominates; the net's only edge is modest survival signal."

### R5 — rule recoverability by representation
Raw diagram exact inference **1.0** (ECA) / **0.975** (range-2), R4. CNN 64-d
bottleneck rule-identity balanced acc **0.88** (ECA) / **0.95** (range-2);
truth-table-bit BA (leave-rules-out) 0.78 / 0.61. Five handcrafted stats: ECA
0.65 / 0.69, range-2 0.30 / 0.55 (texture reads range-2 rule bits barely above
the 0.5 chance level; majority-identity baseline ≈0.01). The 2×2 "anti-shortcut"
bottleneck does **not** prevent rule recovery (identity 0.88–0.95) — the readable
rule is the mechanism behind the null, and the "anti-shortcut" claim is dropped.

### R6 — independent glider validation (concern 8 circularity)
Localized-seed / periodic-localization detector — a *different* observable from
the twin-run damage signature. ECA: damage set = **{54, 106, 110}** (matches the
literature class-IV anchors {54, 110}); independent detector agrees **92.2%** on
the 64 applicable rules (FP 6.2%, FN 1.6% = rule 54, the disclosed ether-front
case). Range-2 (300 rules): damage-signature complex **8.3%**, but the
independent detector agrees only **47%** — so range-2 "complex" is reported
strictly as "fraction satisfying the pre-registered damage-signature criterion,"
not "glider-supporting prevalence." Single-observable glider detection is itself
unreliable in the large space, consistent with the referee's caution.

### R7 — maps vs an independent local ground truth (concern 9)
Location-resolved ground truth by local perturbation *in* the composed system
(short local horizon), replacing the stripe-contrast proxy; hand-crafted window
selected on a validation split (not oracle). Shallow map (m=15), full 16-rule
panel: mean Spearman to the local GT — CNN **0.673**, hand-crafted (val-selected
w=32) **0.605**, oracle 0.638; CNN − val-selected (test) **+0.047**,
CI95[−0.002,+0.102], **cnn_resolves_finer = False** (CI includes 0). Against a
fair, independent local ground truth the learned map shows **no statistically
significant localisation advantage** over a validation-selected cheap window —
they are a tie, the CNN marginally (not significantly) higher.

### Net reframe
An interpretable read-the-rule-and-simulate estimator reaches the reliability
ceiling and dominates both cheap statistics and a deep amortiser, for a proven
mechanism (the rule is fully readable). The amortiser's only measurable edge over
five cheap numbers is modest survival signal; it never approaches the ceiling and
buys no spatial-resolution advantage. Recommendation for this task: read the rule.

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
