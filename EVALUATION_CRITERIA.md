# EVALUATION_CRITERIA.md — pre-registered success/failure criteria (v2)

Fixed **before** any v2 run (2026-07-01), so that success is not defined after
seeing the results (SELF_CRITICISM: "no pre-registered success criterion").
Changing these thresholds after a run requires saying so explicitly wherever the
run is reported.

## Revision 7 (2026-07-04) — changelog

Added **before any of the review-response experiments is measured**, in response
to a detailed referee report on the first manuscript submission
(`manuscript/reviews/chaos_review.md`). These are **reported controls with
pre-registered decision rules**, not new pass/fail gates on criteria 1–9; they
harden the negative benchmark into an equivalence-grade result, add the
interpretable positive result (mechanistic rule-inference estimator), and
validate the two descriptive claims (glider landscape, spatial maps) against
independent ground truth. Numbers-free; auditable via git history. The margins
fixed below (δ, the incremental-value margin, K) are pre-registered bars, not
measured outcomes, and are **not to be edited after a number is seen** — claim
corrections go to `RESULTS.md`/manuscript text only.

1. **New "Review-response controls" section** (below) fixing R1 equivalence &
   per-target inference (§2), R2 incremental-value/stacking (§5), R3
   reliability-adjusted ceiling (§3), R4 mechanistic rule-inference estimator
   (§5), R5 rule-recovery probes (§1), R6 independent glider validation (§8),
   R7 nuCA local-perturbation map ground truth (§9), R8 distribution-shift &
   finite-size (§7). Section numbers in parentheses are the referee's concerns.
2. **Scope of claims tightened, pre-registered:** "no advantage of the deep net"
   may be asserted only where the R1 equivalence test (TOST) passes or where the
   baseline is superior; the "structural" language is bounded to the R8-tested
   regime; "glider-supporting prevalence" is replaced by "fraction satisfying the
   pre-registered damage-signature criterion" except on the R6 detector-validated
   subset.
3. **No change to criteria 1–9, to rev-6 controls S1–S3, or to any existing
   threshold.** The rev-6 S1 superiority rule (median ΔR² ≥ 0.10 on ≥ 3 features)
   is retained and *supplemented* by R1's equivalence test — S1 asks "is the net
   better?", R1 asks "are they equivalent, or is the baseline better?".

## Revision 6 (2026-07-04) — changelog

Added **before any baseline-regression fit, any multi-seed retraining, and any
set-dependence measurement** — the manuscript-solidification controls, fixed here
so their outcomes cannot be defined after seeing them (same hygiene as rev 2–5;
auditable via git history):

1. **New "Baseline & robustness controls" section** (below) fixing three
   pre-measurement specs for the manuscript: **S1** the single-diagram feature
   baseline the CNN amortizer is compared against, **S2** the multi-seed
   robustness protocol, **S3** the RNG set-dependence bound.
2. These are **reported controls with pre-registered interpretation rules**, not
   new pass/fail gates on criteria 1–9: they error-bar and contextualize the
   existing criteria; the spatially-resolved-map contribution stands independent
   of S1's outcome.
3. No change to criteria 1–9 or to any existing threshold.

## Revision 5 (2026-07-04) — changelog

Added **before any range-2 (M4) model is trained and before any sampled rule is
held out** — the simulator, sampler, radius-aware targets and the complex
signature ship in the same change set, and the leave-complex-out split is a
deterministic function of the pre-registered signature (auditable via git
history):

1. **Criterion 6 extended to the range-2 rule space** (M4) — same bars,
   evaluated on sampled range-2 rules; the point of M4 is to test amortization
   where the intermediate/complex regime is *populated*, not a two-member club.
2. **New criterion 9 (complex-regime placement)** — the direct test of the
   §6 caveat: hold out a *set* of complex rules and require unbiased placement.
3. The **complex signature** thresholds are fixed here (calibrated on the ECA
   reference and the a-priori embedded-ECA anchors, `caspectra/eval/regimes.py`).
4. No change to criteria 1–8 or to any existing threshold.

## Revision 4 (2026-07-03) — changelog

Added **before any map has been evaluated on a striped-mask diagram beyond the
qualitative period-32 figure of criterion 7's secondary diagnostics, and before
any composed-system invariant has been measured directly** (the harness ships
in the same change set; auditable via git history):

1. **New criterion 8 (stripe resolution + alloy transfer)** — characterizes
   the phenotype maps' spatial resolution and gates their behaviour *below*
   that resolution, with the full measurement spec fixed below.
2. No change to criteria 1–7 or to any existing threshold.

## Revision 3 (2026-07-03) — changelog

Added **before any non-uniform-CA measurement exists** (the `NonUniformCA`
simulator is implemented in the same change set; no map has been evaluated on
composed diagrams at the time of writing — auditable via git history):

1. **New criterion 7 (compositional map transfer)** — gates the per-patch
   phenotype-map payoff of Lever A on non-uniform CA diagrams, with the full
   measurement spec (rule panel, masks, interface exclusion) fixed below.
2. Housekeeping: the label spot-check note under "Reference labels" updated —
   closed by decision on 2026-07-02 (`rule_labels_PROVENANCE.md`).
3. No change to criteria 1–6 or to any threshold.

## Revision 2 (2026-07-02) — changelog

Revised after the foundations literature review (`FOUNDATIONS.md`,
`docs/literature/2026-07-02_deep_research_report.md`), **before any v2 training
run**, so no run outcome motivated these changes:

1. The classified object is now explicit: the **protocol tuple** *(orbit,
   Bernoulli(1/2) IC measure, ring 127, horizon 127)* — not "the rule"
   (undecidability, measure-dependence; FOUNDATIONS.md §1).
2. Criterion 1: Wolfram agreement demoted from ground truth to **reference
   touchstone**; class-IV reference set fixed at **{54, 110}**; borderline rules
   **40, 41, 42, 106** flagged in `rule_labels.csv`, and class-IV recall is
   reported **both with and without rule 106 in the chaotic pool**.
3. Criterion 3 reinterpreted: the physics baseline is now also the **auxiliary
   training target** (Lever A), so the comparison becomes "match the direct
   invariant out-of-sample and add spatial resolution", not "beat it".
4. **New criterion 5 (protocol stability)** and **new criterion 6 (amortization
   transfer)** added; both pre-registered before being measured on any learned
   model.
5. Lever change: temporal-window positives dropped as a standalone lever
   (instance discrimination — same shortcut incentives as v1); levers are now
   A = invariant-regression amortizer (primary), B = predictive SSL
   (FOUNDATIONS.md §4, incl. kill criteria).

## Why the criterion moved (decision record)

v1 (`runs/default/`) showed that **rule identifiability is not the right pass/fail
bar**: every ECA rule produces a statistically distinctive texture, so any
expressive encoder identifies rules from mesoscopic statistics alone — no
rule-table ("T-tetromino") reading required — and instance-discrimination SSL
actively rewards per-diagram (hence per-rule) distinctiveness. The v1 rule probe
hit 0.967 *through* an anti-cheat architecture; the supervised paper only reached
rule ≈ 61% because label pressure pushed the other way. Demanding "rule probe well
below 100%" of an unsupervised embedding is therefore likely unachievable and,
more importantly, mis-aimed: v1's real failure was that **behavioural structure was
present but not salient** — density dominated the geometry (PC1 ≈ density), and
clustering followed it.

**Success is therefore defined at the geometry/cluster level** (what the
unsupervised pipeline makes salient), not at the embedding-decodability level.
The rule probe stays prominently reported as a diagnostic.

## The classified object (rev 2)

Every criterion below is a statement about the **protocol tuple**

> *(rule orbit under reflection/complement, Bernoulli(1/2) IC measure, ring of
> 127 cells with periodic boundaries, horizon of 127 rows from t = 0)*

— not about "the rule" in the abstract. The literature (Gilman; Culik–Yu; see
FOUNDATIONS.md §1) shows the observed class can change with the IC measure,
lattice, and horizon; criterion 5 measures that sensitivity instead of assuming
it away.

## Reference labels

- `rule_labels.csv` (provenance: `rule_labels_PROVENANCE.md`; automated checks
  accepted by decision 2026-07-02, transcribed class lists kept for re-verification).
- **Class-IV metrics use the `wolfram_class` column (4 = {54, 110})** — under
  Li–Packard, complex rules are folded into "chaotic", so LP cannot score class IV.
- Wolfram/LP agreement is a **reference touchstone, not ground truth** (rev 2):
  formalized class membership is undecidable and borderline rules are unstable
  across published schemes. The `borderline` column flags **40, 41, 42, 106**
  (published chaotic substructure for 40/42; intermediate damage signatures for
  41/106 — see provenance file).
- Genotype = the **orbit** (equivalence-class representative), as in v1.

## Primary criteria (pass/fail, per run)

1. **Behavioural salience of clusters.** Per-Wolfram-class cluster recall — the
   fraction of a class's diagrams that land in clusters where that class is the
   majority. Success: recall ≥ 0.5 for **each** of the four Wolfram classes,
   including class IV. Failure: class-IV recall < 0.2 after the M3 levers.
   **Criteria 1 and 2 are one joint criterion**: rule-pure clusters are trivially
   class-pure, so a one-cluster-per-rule solution scores recall 1.0 while
   failing criterion 2 (measured on v1: recall ≈ 1.0 everywhere with excess
   genotype fraction 0.81). Neither number means anything alone.
   *(Rev 2)* Class-IV recall is reported **twice**: with rule 106 counted as
   chaotic (published labelling) and with 106 excluded from the chaotic pool
   (our damage-space borderline). Borderline rules (40, 41, 42, 106) are
   flagged in all per-class tables; a pass/fail that flips depending on
   borderline placement is reported as **ambiguous**, not as a pass.
2. **No excess genotype information in clusters.**
   `MI(cluster; orbit | wolfram_class) / H(orbit | wolfram_class)` — the fraction
   of within-class rule information the clustering resolves. Success ≤ 0.25;
   failure ≥ 0.5. (v1: clusters ≈ orbits, so this is ≈ 1 by construction; measure
   to confirm.)
3. **Beat the physics baseline where it counts.** Class-IV recall of the
   SSL-embedding clustering ≥ that of clustering on the damage-spreading /
   dynamics features alone (`caspectra/eval/dynamics.py`, M2.3). If the cheap
   physics baseline wins, the honest headline is "texture SSL does not detect
   computation beyond label-free dynamical statistics" — reportable, not tunable
   away.
   *(Rev 2 — measured outcome + reinterpretation.)* This gate was measured on
   2026-07-01: the physics baseline won, 1.00 vs 0.00 (`RESULTS.md`). The
   dynamics features consequently become the **auxiliary training target** of
   Lever A, so for learned models this criterion now reads: the amortized
   estimate must *match the direct invariant out-of-sample* (criterion 6) and
   *add what the scalar invariant cannot* (spatial resolution / per-patch maps)
   — not "beat" its own supervision signal.
4. **Stability.** The macro-structure must survive clustering hyperparameters:
   ARI ≥ 0.6 between cluster assignments across the `min_cluster_size` sweep and
   across 3 UMAP seeds. A class-IV island that appears at one seed only does not
   count.
5. **Protocol stability (rev 2).** Any claimed taxonomy must be stable across
   the observation protocol: over IC densities p ∈ {0.25, 0.5, 0.75} (width
   127), each dynamics feature keeps Spearman ρ ≥ 0.8 against the p = 0.5
   reference, and cluster assignments (agglomerative, k = 14, standardized
   features) keep ARI ≥ 0.6 against the reference. Rules that flip cluster
   membership across protocols are listed explicitly wherever the taxonomy is
   reported (density-dependent behaviour, e.g. rule 184, is a *finding* about
   the protocol tuple, never hidden). Measured by
   `scripts/protocol_sensitivity.py`; extreme densities (0.1, 0.9) and other
   widths are reported as context, not gated.
   *Measurement spec + first outcome (2026-07-02, documented — not a threshold
   change):* the gate must be measured with **n_pairs ≥ 128** and read against
   a same-protocol **seed control** — at n_pairs = 32 the sampling floor alone
   is ARI ≈ 0.4, which would conflate noise with protocol dependence. First
   measurement (n_pairs = 128, seed control ARI = 0.70): the feature-ρ half
   **passes** (ρ ≥ 0.90 at gated densities); the ARI half **fails** (0.33 at
   p = 0.25, 0.37 at p = 0.75) — the *fine hard partition* is genuinely
   IC-measure-dependent, while width barely matters (w = 255: ARI 0.78, no
   class flips), class-level flips at gated densities are single rules (106,
   168), and the {54, 110} co-membership holds across the whole gated range
   (`RESULTS.md`). Consequence: v2 taxonomy claims must be made at the level of
   protocol-robust structures (invariant feature space, coarse/class-level
   groups, specific co-memberships), never as a fine partition of rule space.
6. **Amortization transfer (rev 2; gates Lever A).** A learned encoder must
   predict the dynamics feature vector from a **single diagram** with
   leave-rules-out validation: success = median held-out-rule R² ≥ 0.5 per
   feature; failure = R² < 0.2. This is pre-registered now, before any Lever-A
   model exists. Passing it is what earns the learning component its place;
   the payoff claim (per-patch phenotype maps for nuCA) is only credible if
   this holds.
   *(Measured 2026-07-02: PASS in both split variants, median rule-level R²
   0.863 / 0.836 — `RESULTS.md`.)*
7. **Compositional map transfer (rev 3; gates the phenotype-map payoff).**
   The per-patch maps must recover *where* behaviour differs, not merely echo
   the global prediction. Measured on **two-region half/half non-uniform CA
   diagrams** (`caspectra/ca/nuca.py`): left half evolves under rule A, right
   half under rule B, standard protocol otherwise (Bernoulli(1/2) ICs, ring
   127, horizon 127, transient kept).
   - **Model under test:** the frozen `runs/lever_a/checkpoint_final.pt` (no
     retraining, no nuCA data in training) for the primary measurement;
     retrained variants (e.g. a shallower encoder) are additionally reported
     against the same spec.
   - **Primary panel (gated):** the 16 rules {0, 4, 204, 184, 26, 73, 154, 90,
     60, 30, 18, 45, 22, 41, 106, 54} — all orbit representatives in the main
     run's TRAIN split (so criterion 7 isolates *compositional* generalization
     from the rule transfer already gated by criterion 6), stratified across
     damage regimes: dead (0), fixed-point (4, 204), traffic (184), locally
     chaotic (26, 73, 154), additive/ballistic (90, 60), chaotic (30, 18, 45,
     22), borderline (41, 106), complex (54). All 120 unordered pairs, ≥ 8
     ICs per pair with the rule-to-side assignment alternated.
   - **Statistic:** per region, the mean un-standardized `predict_map` output
     over map patches whose receptive field lies entirely inside the region
     (patches within ±16 px of either rule interface are excluded — the
     4-block encoder's receptive-field half-width; the ring has two
     interfaces). Ground truth per region = the pure rule's direct invariant
     vector (`load_or_compute_invariant_targets`, n_pairs = 256, reference
     protocol). Per-feature R² across all (pair, IC, region) region-means,
     then the **median across the 4 features** is gated.
   - **Bars:** success ≥ 0.5; failure < 0.2 (mirrors criterion 6).
   - **Mandatory control (validity, not a gate):** rule_a == rule_b diagrams
     must reproduce the uniform-diagram predictions exactly (same simulator
     output, same map) — if the control fails, the harness is broken and no
     panel number may be reported.
   - **Secondary diagnostics (reported, not gated):** pairs of each main-run
     held-out rule with anchors {0, 204, 30, 54} (rule transfer and
     composition jointly, incl. 110); spreading-rate **ordering accuracy**
     (fraction of pairs with distinct true rates where the predicted
     region ranking matches); striped masks (period 32, qualitative — below
     the interface-exclusion resolution by construction); interface-band
     predictions vs the two flanking regions.

8. **Stripe resolution & alloy transfer (rev 4; characterizes and gates the
   maps below the half/half geometry).** Criterion 7 used half/half masks,
   where even a 7-column map has interface-free columns; no measurement so far
   supports the finer claim that a higher-resolution map buys finer *spatial*
   discrimination. Criterion 8 measures that directly, on striped masks
   (`striped_mask(127, p)` — alternating stripes of `p` cells; the last stripe
   truncates since 127 is not divisible by `p`). Each striped mask is
   **cyclically rolled by a per-IC random offset** (seeded) so stripe phase is
   not accidentally aligned with the fixed patch grid. Applies to **both**
   certified checkpoints (`runs/lever_a_local`, 7×7 map, patch ≈ 18 cells;
   `runs/lever_a_shallow`, 15×15 map, patch ≈ 8.5 cells), each measured and
   gated independently against the same spec.

   **8a — stripe resolution (minimal gate + reported characterization).**
   - *Systems:* periods p ∈ {32, 16, 8, 4, 2}; pairs = all criterion-7
     primary-panel pairs whose cached pure-rule spreading rates differ by
     ≥ 0.25 (n_pairs = 256 reference cache — 78 pairs; derived from public
     cached truth, fixed before any map is rendered). 16 ICs per (pair, p),
     random mask offset per IC; plus 16 half/half ICs per pair for the
     normalizer.
   - *Statistic:* time-averaged per-column spreading-rate reading of the map;
     per-diagram contrast C = mean over columns whose centre cell runs the
     hotter rule (by cached pure-rule rate) − mean over the colder columns,
     **no interface exclusion** (degradation is the measurement). Per pair:
     mean over ICs → C(p) and C(half). Relative contrast R(p) = C(p)/C(half).
     Pairs with measured C(half) < 0.05 are excluded from R(p) aggregation
     (unstable ratios) and reported as excluded. **Resolution limit** =
     smallest p with median-over-pairs R(p) ≥ 0.5.
   - *Gate (deliberately minimal):* at p = 32, the mean-over-pairs R(32) must
     be positive with a 95% bootstrap CI (over pairs, 10 000 resamples)
     excluding 0. A checkpoint failing this cannot claim any spatial
     resolution finer than half/half, and the published "pick 15×15 for
     spatial detail" guidance must be corrected wherever it appears.
     The full R(p) curves and the 7×7-vs-15×15 comparison are **reported
     characterization, not pass/fail** — no bar is set on the resolution
     limit itself.

   **8b — alloy transfer (gated; bars mirror criteria 6/7).** Below the map's
   resolution a fine-striped composed system is effectively a *new* homogeneous
   system — an "alloy" of two rules — and its own invariants are directly
   measurable by the same twin-run protocol run on the composed simulator.
   - *Systems:* all 120 criterion-7 primary-panel pairs × p ∈ {2, 4}
     (240 alloys; both periods are below both checkpoints' patch sizes),
     8 ICs each with random mask offset per IC.
   - *Truth:* `damage_spreading_features` computed **on the composed
     simulator** (n_pairs = 256, width 127, horizon 62, Bernoulli(1/2) —
     identical protocol to the pure-rule reference cache), at mask offset 0
     only (Bernoulli ICs are translation-invariant on the ring, so alloy
     invariants do not depend on the offset).
   - *Statistic:* per (alloy, IC), the global map mean (≡ the global
     prediction, by the GAP∘linear identity) vs the alloy truth; per-feature
     R² over all records; the **median across features is gated**: success
     ≥ 0.5, failure < 0.2. *Degeneracy rule (fixed now):* a feature whose
     alloy-truth std across the 240 alloys is < 0.05 is reported but excluded
     from the gated median.
   - *Mandatory control (abort, not gate):* for r ∈ {0, 30, 54, 204} and both
     periods, the (r, r) "alloy" truth must equal the pure-rule truth exactly
     (same rng path) — otherwise the truth harness is broken and no panel
     number may be reported.
   - *Pre-registered interpretation baseline (reported, NOT gated):* the
     **constituent-mixture baseline** — the mask-area-weighted mean of the two
     pure rules' cached invariant vectors — scored against the same alloy
     truth. If the map beats the mixture, the network reads *emergent* alloy
     behaviour; if not, the maps do texture-mixing below their resolution.
     Both outcomes are reportable findings; neither changes the 8b verdict.

9. **Complex-regime placement in the range-2 space (rev 5; M4; the §6
   repair).** Criterion 6 passed on ECAs but the complex regime there is a
   two-member club ({54, 110}); held out, either is mispredicted, *pulled*
   toward the nearest populated regime (RESULTS.md 2026-07-02: 110's rate read
   0.54 vs true 0.37; 54's 0.18 vs true 0.44). ECAs cannot fix this — ~2
   complex rules in 88. Criterion 9 tests whether **populating** the regime
   (range-2 binary CAs, `caspectra/ca/range_ca.py`) lets the amortizer place
   complex behaviour *without systematic bias*.
   - **Space & protocol:** two-state, radius-2 CAs (2^32 rules), **sampled**
     and de-duplicated by the reflect+complement orbit. Standard protocol
     otherwise: Bernoulli(1/2) ICs, ring width 127, horizon **radius-aware**
     (`width // (2·radius) − 1`, so the light cone cannot wrap; the spreading
     rate is normalized by the cone speed so the four features keep their
     meaning across radii). The panel is a fixed sample: `sample_rules(N, 2,
     seed=0)`; `N` (target 600–1000) is fixed in the training config generated
     by `scripts/analyze_range2_landscape.py` **before** training.
   - **Complex signature (pre-registered, `regimes.COMPLEX_SIGNATURE`):** a
     rule is *complex* iff `damage_survival > 0.85` **and** `0.15 ≤
     spreading_rate ≤ 0.28` **and** `cone_fill < 0.6` **and** `damage_fraction
     < 0.15` (the range-2-protocol calibration: damage persists, spreads
     sub-ballistically, in a sparse localized cone). Calibrated on the
     embedded-ECA anchors so it includes the class-IV cluster {54, 110, 106};
     the additive-adjacent rule 60 also matches (a known, reported contaminant).
     The ECA-protocol sibling (`COMPLEX_SIGNATURE_ECA`) selects exactly
     {54, 106, 110} across the 88 ECA reps — the provenance the method works.
   - **Split:** leave-complex-out — **all** signature-complex sampled rules go
     to the hold-out set (`force_holdout`), plus a stratum-free 20 % random
     hold-out of the rest for the general criterion-6 number. Training never
     sees a complex rule.
   - **Gates (mirror criteria 6/7):** (a) **criterion-6 median R²** on the
     complex hold-out ≥ 0.5 (fail < 0.2); and (b) **no systematic regime pull**
     — the mean *signed* spreading-rate error over the complex hold-out has
     `|mean| ≤ 0.10` (the ECA baseline was strongly signed, ±0.15–0.26). Both
     must hold to pass.
   - **Mandatory control (validity, not a gate):** embedded-ECA continuity —
     the range-2 rules embedding the ECAs reproduce the ECA *diagrams*
     bit-for-bit (`tests/test_range_ca.py`); a break voids the harness.
   - **Reported (not gated):** the complex-regime count/fraction under uniform
     sampling (is it actually populated?); the 4-D invariant landscape vs the
     ECA landscape; curated-anchor placements; per-feature R² and signed bias
     on the complex hold-out vs the general hold-out.
   - **Pre-registered fallback (named now, not post hoc):** if uniform sampling
     yields < 15 complex rules, re-sample with a targeted sampler — Hamming-1
     perturbations of the embedded-complex rule tables and rules with high
     input-entropy variance (Wuensche 1999) — and report both the uniform
     density and the enriched panel. (The measured density is itself a reported
     criterion-9 outcome, above.)

## Baseline & robustness controls (rev 6)

Manuscript-grade controls fixed before measurement. Each carries a
pre-registered interpretation rule; none is a new pass/fail gate on criteria 1–9.

**S1 — single-diagram baseline (does the amortizer beat cheap statistics?).**
The criterion-6/9 claim is that the damage-spreading invariants — *defined* by
twin runs — are non-trivial to recover from a **single** diagram. The null
alternative is that a handful of cheap single-diagram statistics already recover
them (the "the encoder just reads density" objection). Control: fit regressors
from the label-free single-diagram features of `caspectra/eval/baselines.py` —
mean (polarity-folded) density, temporal activity, compression ratio, 2×2 block
entropy, and a **radius-aware** input-entropy variance (Wuensche 1999;
width-(2r+1) neighbourhood codes) — onto the four damage invariants, using the
**identical leave-rules-out split** as the CNN it is compared to (criterion 6 on
ECAs; criterion 9's leave-complex-out on range-2). Regressors: ridge and
gradient-boosted trees (the stronger is the baseline of record). Report
per-feature and median held-out-rule R² for baseline vs CNN on the same truth.
  - *Pre-registered interpretation:* the amortizer is "meaningfully better" iff
    its held-out median R² exceeds the best baseline's by ≥ **0.10** absolute on
    the same split (and, secondarily, beats it on ≥ 3 of the 4 features). If the
    margin is smaller, the manuscript **softens the global-amortization claim**
    and foregrounds the per-patch phenotype map — which the scalar baseline
    cannot produce at all (an architectural fact, not a measured one) — as the
    contribution. Both outcomes are honest and reportable; S1 changes emphasis,
    not the validity of criteria 6–9.

**S2 — multi-seed robustness (error bars on every headline number).** The
certified checkpoints were each a single training run. Retrain the headline
models with **5 seeds** (seeds fixed as {0, 1, 2, 3, 4} before running; each
seed sets both weight init and the IC-stream seed; identical data split and
protocol otherwise): `lever_a_local` (criteria 6/7), `lever_a_shallow`
(criterion 8a), and `m4_range2` (criteria 6/9). Report **mean ± std** of each
gated median R² and of the criterion-9 signed spreading-rate bias.
  - *Pre-registered interpretation:* a gate is robust iff it holds at **mean − 1
    std** (equivalently, at all 5 seeds). A gate that passes only at some seeds
    is reported as **seed-fragile**, not as a pass.

**S3 — RNG set-dependence bound.** `dynamics_feature_matrix` seeds one RNG per
rule by sorted-list position, so a rule's target depends on the set it is
computed in (documented in `targets.py`). Bound it: for ~10 rules spanning the
regimes, recompute the four invariants as members of **3 different rule sets**
(varying size and composition) and report the maximum |Δ| per feature.
  - *Pre-registered interpretation:* if max |Δ| ≤ **0.01** (the documented
    bootstrap precision at n_pairs = 256), the coupling is declared immaterial
    and disclosed as such. If any feature exceeds 0.01, the per-rule RNG is
    re-seeded by **rule identity** (not list position) and the affected caches
    and criteria are recomputed before the manuscript reports them.

## Review-response controls (rev 7)

Fixed before measurement, each with a pre-registered decision rule; none is a new
pass/fail gate on criteria 1–9. All results below are reported **per target**
(the four damage-response statistics: survival, fraction, spreading rate, cone
fill), never only as the 4-target median.

**R1 — Equivalence & per-target inference (§2: "failed superiority ≠
equivalence").** The unit of resampling is the **held-out rule** (rule-level
cluster bootstrap). For each ordered method pair (A, B) and each target, the
paired difference ΔR² = R²_A − R²_B is computed on the *same* held-out rules, and
its interval is estimated by a nested resample: cluster bootstrap over held-out
rules (**10 000 resamples**) within **≥ 10 repeated leave-rules-out outer
splits**, propagating the **K target replicates** of R3 (rules × splits × target
noise). Decisions per target:
  - **Superiority** (retains the rev-6 S1 rule): A is meaningfully better iff the
    median ΔR² ≥ **0.10** *and* the 95% paired CI excludes 0 in A's favour.
  - **Practical equivalence (TOST):** with a pre-registered margin **δ = 0.05**
    absolute R², A and B are practically equivalent on a target iff the **90% CI
    of ΔR² lies entirely within (−δ, +δ)**. δ is chosen a priori as a negligible
    R² gap and is cross-checked against the R3 noise floor (a gap below 1 −
    reliability is meaningless regardless of δ).
  - *Reporting rule:* "the deep net has no advantage" is written as **equivalence
    only where TOST passes**; where B's (baseline's) CI lies entirely above +δ,
    it is written as **baseline superiority** (expected on ECA global); elsewhere
    it is **inconclusive/underpowered**, never "equivalent." Every headline
    number carries its per-target paired CI and TOST verdict.

**R2 — Incremental value / stacking (§5: "does the representation add
information beyond the five statistics?").** Cross-fitted, rule-level: on each
outer fold, fit the baseline (5 features → target) on the training rules and the
CNN separately; on the held-out rules, compute the **incremental R²** of adding
the CNN's prediction to the 5 features (nested-model cross-fit R², equivalently
the variance of the held-out baseline residual explained by the CNN prediction).
Decision per target: the learned representation **adds value** iff incremental
ΔR² > **0.02** with a rule-bootstrap 95% CI excluding 0. The symmetric complement
(does the baseline add value beyond the CNN?) and the oracle-vs-both stack are
reported alongside. This is the rigorous form of the paper's central claim.

**R3 — Reliability-adjusted ceiling (§3: "MC noise does not by itself bound
R²").** Draw **K = 20** independent Monte-Carlo target replicates per rule via
`dynamics_feature_matrix(seed=k)` at the production `n_pairs`. Per target,
decompose the across-rule variance into between-rule (signal) and
between-replicate/within-rule (noise) components; the **reliability** is
ICC(1) = σ²_signal / (σ²_signal + σ²_noise), and the **reliability-adjusted R²
ceiling** is this ICC (classical attenuation bound). Report per target, with the
conditional-on-survival quantities (fraction, rate, fill) and the survival
probability handled separately because their noise is heteroscedastic and
non-Gaussian. This **replaces** the "0.006–0.014 upper-bounds R²" sentence;
observed R² for every method is read against the per-target ceiling.

**R4 — Mechanistic rule-inference estimator (§5: the interpretable reference
method).** `caspectra/eval/rule_inference.py:infer_rule(diagram, radius)`
tabulates observed neighbourhood→next-cell transitions and returns the inferred
table plus its **coverage** (fraction of the 2^(2r+1) entries observed).
Pre-registered handling of unobserved entries: **default to 0**, with coverage
reported and the sensitivity to the default reported (majority-fill as the
alternative). `mechanistic_estimate(diagram)` = infer → build the simulator
(`caspectra/ca/{eca,range_ca}.py`) → `damage_spreading_features` at the
production protocol → the four targets, evaluated on the **same** leave-rules-out
split as every other method. Reported (no pass/fail bar — it is the interpretable
reference): per-target R² vs the R3 ceiling; an **identifiability curve**
(exact-table-match rate and per-entry accuracy vs number of observed rows /
width). Pre-registered expectation (stated so it cannot be reframed post hoc): on
rules whose table is fully covered the estimator should approach the ceiling;
under-covered rules are where it should degrade, and that degradation is a
reported finding.

**R5 — Rule-recovery probes (§1: is the rule actually recoverable from the
representation?).** Extend `caspectra/eval/probes.py` to fit probes from each
source S ∈ {raw-diagram summary statistics, an intermediate encoder feature map,
the 64-d bottleneck, the 5 handcrafted baseline features} predicting (a) rule /
orbit identity and (b) each individual truth-table entry. Identity probes use a
stratified split (identity cannot transfer to unseen rules); truth-table-entry
probes use a **leave-rules-out** split (tests transfer of the *reading*
mechanism). Report balanced accuracy vs the majority baseline for all sources
side by side. Pre-registered reporting rule: this **replaces** the unsupported
"the 2×2 first-layer kernel prevents rule recovery" assertion — if the bottleneck
(or any layer) probe recovers the rule well above chance, the architecture is
**not** described as "anti-shortcut"; the readability of the rule is instead
reported as the mechanism behind the null result.

**R6 — Independent glider validation (§8: the complex label must not be defined
by, and validated on, the same damage signature).** A detector **independent of
the damage signature**: from long-horizon evolution (production ring 127 plus a
ring-255 confirmation so structures are not wrap-limited), estimate and subtract
the dominant temporally-periodic background, then detect **persistent localized
propagating structures** (connected components of the background-subtracted field
that persist ≥ a fixed number of rows and translate at finite, sub-ballistic
velocity), and/or apply a **periodic-localization test** (a single localized seed
on a quiescent background yields a bounded, comoving-eventually-periodic
structure). `caspectra/eval/gliders.py`; a rule is **detector-complex** iff such
a structure is found in ≥ a fixed fraction of trials (threshold fixed in the
module before range-2 application). The detector is first **validated to recover
{54, 110, 106} and reject ordered {0, 4, 204} and chaotic {30, 90, 22}**.
Reported on a held-out range-2 sample: **agreement, false-positive and
false-negative rates** of the damage signature vs the detector. Pre-registered
language rule: landscape prevalence is reported as the "**fraction satisfying the
pre-registered damage-signature criterion**"; only the detector-validated subset
is called "glider-supporting," and both numbers appear side by side with FP/FN.

**R7 — nuCA local-perturbation map ground truth (§9: the map needs an
independently computed local ground truth).** For a mosaic
(`caspectra/ca/nuca.py:NonUniformCA`, `striped_mask`), flip the initial cell at
position x0, evolve twin copies, and measure the four damage statistics on the
**local comoving cone** around x0 → a per-location target vector (averaged over
ICs). This location-resolved target does **not** assume a stripe carries a
uniform rule's phenotype (it measures the composed system in place). Compare
`predict_map` (CNN) and the handcrafted patch-map to this ground truth on
**localization error** (offset of predicted regime boundaries), **spatial
correlation** (per-column predicted vs true invariant), and **calibration**
(predicted vs true value), across ≥ a fixed set of rule pairs, both stripe
orientations, random mosaics, and interface regions analysed explicitly. Window
selection is **fixed from validation data** for the primary comparison; the
per-period best window is reported only as a labelled sensitivity. Verdict rule:
"CNN resolves finer" is asserted only if the CNN map beats the
validation-selected handcrafted map on localization error with a bootstrap 95% CI
excluding 0; ties and losses are reported as such.

**R8 — Distribution shift & finite-size (§7: the conclusion is one regime, not
structural in general).** Train the amortiser and fit the baseline and the R4
oracle on the reference regime, then **evaluate under shift**: IC densities
p ∈ {0.25, 0.75} (extremes 0.1/0.9 as context), widths/horizons {63, 127, 255}
(finite-size scaling; horizon stays radius-aware), perturbation types {1-bit,
multi-bit, 3-cell block}, and a **rule-family holdout** (hold out an entire
additive/other family rather than random rules). Report **degradation curves**
(R² vs shift) for oracle, baseline, and net. Pre-registered interpretation: the
"structural / no-advantage" claim is asserted **only within the tested regime**;
where the R2 incremental value of the net rises above the 0.02 margin (CI
excluding 0) under any shift, that regime is reported as one where representation
learning begins to help — a finding, never suppressed.

## Reported diagnostics (not gated)

- Rule(orbit)-identity probe accuracy/balanced accuracy + the LP/Wolfram probe
  **gap** (kept for continuity with the supervised paper; no longer pass/fail).
- Collapse: `embedding_std`, plus **effective rank / participation ratio** of the
  embedding covariance (v1: std ≈ 0.018 vs ≈ 0.125 isotropic — heavy anisotropy).
- **Invert-invariance check:** R²(embedding → raw density) vs R²(embedding →
  folded density `min(d, 1−d)`). If raw density is decodable well beyond folded,
  the invert augmentation did not produce the intended invariance (training bug
  signal, since only the 88 min-representatives are simulated).
- Hand-crafted feature baseline comparison (`eval/baselines.py`), per class.

## Explicit failure conditions

- Any run where the collapse diagnostics fire (embedding_std → 0 or effective
  rank ≈ 1) is void regardless of other numbers.
- *(Rev 2 — kill criteria, FOUNDATIONS.md §4.)* If Lever A (invariant-regression
  amortizer) fails criterion 6 **and** Lever B (predictive SSL) separates
  {54, 110} (106 reported both ways) no better than the direct damage features,
  the learning component concludes as a negative result — "SSL adds nothing over
  direct invariants on ECAs" — and effort moves to the larger rule space (M4).
  No further texture-SSL (instance-discrimination) tuning runs on 88 ECAs under
  any outcome: that question was answered on 2026-07-01 (`RESULTS.md`).
