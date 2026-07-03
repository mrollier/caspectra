# EVALUATION_CRITERIA.md — pre-registered success/failure criteria (v2)

Fixed **before** any v2 run (2026-07-01), so that success is not defined after
seeing the results (SELF_CRITICISM: "no pre-registered success criterion").
Changing these thresholds after a run requires saying so explicitly wherever the
run is reported.

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
