> **SIMULATED REVIEW** — ARS panel, 2026-07-05, Peer Reviewer 1 (Methodology). Not a real referee report.

## Contract Paraphrase

**D1 — methodology_rigor (mandatory).** The study's design, data handling, statistical reporting, and reproducibility affordances must meet the peer-review bar of the intersecting fields (nonlinear dynamics benchmark work reviewed at an ML-evaluation standard). For a paper claiming "simulation-limited prediction" from a benchmark of estimators, this means: decision rules and thresholds committed before measurement and honestly labelled as such; correct construction and interpretation of reliability ceilings, bootstrap confidence intervals, and any equivalence-style claims; clean seed handling and train/holdout separation; and code/data affordances sufficient for independent re-execution. This is my primary dimension and it is mandatory: a failure here cannot be offset by strengths elsewhere.

**D2 — domain_accuracy (mandatory).** Claims must align with current evidence and prior work must be represented correctly, with no factual errors in domain terminology or reported results. Within my remit I evaluate D2 for the statistics/ML-evaluation domain — whether ICC, bootstrap, reliability, and benchmark-methodology concepts are used and cited correctly, and whether reported numbers are internally consistent and consistent with the supplementary records. Cellular-automata literature coverage belongs to Reviewer 2 and I will not score it.

**D3 — argumentative_coherence (mandatory).** The core thesis — that rule reconstruction from one diagram yields prediction of the finite-horizon damage response limited only by simulation/measurement noise — must be internally consistent, and every headline claim must be actually supported by the reported measurements rather than by rhetorical framing. I will check that negative or borderline results are not quietly converted into positives, and that scope qualifiers (finite horizon, specific protocol) are maintained wherever the claim is stated.

**D4 — cross_disciplinary_relevance (high priority).** The paper sits at the junction of nonlinear dynamics (Chaos readership) and ML benchmark methodology. Definitions (e.g., reliability ceilings, estimator classes) must be accessible to physicists, and dynamics concepts must be stated precisely enough for ML readers; any claim that the benchmark generalises across communities must be substantiated, not asserted.

**D5 — writing_and_structure (normal priority).** A ~8,500-word, 9-page two-column REVTeX manuscript for Chaos must be well organised, with clear exposition, publication-quality figures/tables, and adherence to AIP/Chaos conventions (abstract, lead paragraph, sectioning, data-availability statement).

## Scoring Plan

### D1: methodology_rigor
- **what_to_look_for:** explicit statement of which analyses/thresholds were committed in advance vs post hoc, with verifiable provenance; correct derivation and use of any reliability ceiling (an ICC-based benchmark such as a 2·ICC−1 attenuation bound must be algebraically justified and applied to the right quantity); bootstrap CI methodology (resampling unit, number of replicates, percentile vs BCa); per-cell/per-condition verdict rules stated before results; seed handling (how many seeds, whether seed selection could cherry-pick); train/holdout hygiene (no leakage between rule sets or initial conditions used for fitting and evaluation); reproducibility affordances (pinned environment, seeds recorded, canonical artifacts, tests).
- **what_triggers_block:** pre-registration claims contradicted by provenance (thresholds relaxed after seeing data without disclosure); a statistically invalid headline benchmark (e.g., ceiling mis-derived so the "simulation-limited" verdict is an artifact); demonstrable train/test leakage affecting headline results; headline numbers that cannot be traced to any measured record.
- **what_triggers_warn:** pre-registration labelling that is honest but incomplete (some post-hoc analyses not clearly flagged); CIs reported without methodology details; single-seed headline results without sensitivity checks; reproducibility gaps (missing pins, unclear canonical artifact) that impede but do not preclude replication.

### D2: domain_accuracy
- **what_to_look_for:** correct definitions and citations for ICC/reliability theory, bootstrap inference, equivalence-testing logic; benchmark-methodology claims consistent with the ML-evaluation literature; numerical results in text/tables/figures mutually consistent and consistent with supplementary records.
- **what_triggers_block:** a factual error in statistical machinery that invalidates a mandatory conclusion; misrepresentation of a cited statistical method; manuscript numbers contradicting the measured records they claim to report.
- **what_triggers_warn:** imprecise statistical terminology, minor numeric discrepancies (rounding-level), or missing citations for non-standard statistical constructions.

### D3: argumentative_coherence
- **what_to_look_for:** the chain from experiments → measurements → verdicts → title claim; whether "simulation-limited" is defined operationally and every use matches that definition; whether limitations (finite horizon, single protocol, estimator families tested) are acknowledged where they constrain the thesis; absence of circularity (e.g., defining the ceiling using the same data that is then declared to reach it, without correction).
- **what_triggers_block:** the central claim does not follow from the reported evidence, or a circular/self-fulfilling construction underlies the headline verdict.
- **what_triggers_warn:** overgeneralised phrasing in abstract/conclusions relative to the measured scope; selective emphasis that a careful reader can still see through.

### D4: cross_disciplinary_relevance
- **what_to_look_for:** whether a Chaos reader can follow the ML-evaluation apparatus (ceilings, estimators, verdict tables) from the definitions given; whether ML readers get precise dynamics definitions (damage spreading, finite horizon); whether the benchmark's claimed utility to both communities is demonstrated.
- **what_triggers_block:** the methodological apparatus is unintelligible to the target venue's readership, or an interdisciplinary claim is unsubstantiated and load-bearing.
- **what_triggers_warn:** jargon from one field used without definition; accessibility gaps fixable with a paragraph or notation table.

### D5: writing_and_structure
- **what_to_look_for:** logical section order; figures/tables that carry the argument with complete captions; consistent notation; venue conventions (REVTeX, data-availability statement, ~length fit).
- **what_triggers_block:** structure so disorganised that the argument cannot be evaluated (unlikely at this maturity).
- **what_triggers_warn:** missing/incomplete captions, inconsistent notation, sections that duplicate or misplace content, convention violations.

## Dimension Scores

### D1 — methodology_rigor: **warn**
The registration machinery, inference design (rule-level cluster bootstrap, TOST with margin sensitivity, pre-fixed seeds), and reproducibility affordances are exceptional and were verified against git history and run artifacts. The score is warn, not pass, because verification found (i) one manuscript number in Sec. V.E ("the frozen CNN to −1.1", main.tex line ~526) that is not supported by the canonical released artifact (`runs/m4_range2/frontier_grid/summary.json` gives −0.93), apparently inherited from a run the repo's own provenance note says was discarded, and (ii) undisclosed reduced Monte-Carlo budgets (n_pairs = 48/64 vs the production 256) for the two degraded-observation figures — reproducibility gaps that impede exact replication, matching my committed warn trigger.

### D2 — domain_accuracy: **warn**
The statistical machinery (ICC(1), the 2·ICC−1 replicate-agreement benchmark, TOST logic) is correct and even empirically self-validating (agreement 0.9871 vs 2·0.9936−1 = 0.9872 in the ECA reliability artifact). Warn is triggered by two numeric inconsistencies: the −1.1 vs −0.93 discrepancy above (0.17 in median R², beyond rounding, though in an exploratory subsection and not conclusion-flipping), and the "2/88 elementary orbits" count (Sec. V.G and Fig. 8 caption) which is inconsistent with the same paragraph's statement that the signature selects {54, 106, 110} on ECA (3/88).

### D3 — argumentative_coherence: **pass**
The chain from measurement to claim is tight: "simulation-limited" is operationally defined (Sec. III), the mechanistic estimator's headline is checked against the correct benchmark and independently falsification-tested against a 16×-larger reference (Sec. V.A), inconclusive and refuted results are reported as such (map verdict, Sec. V.G; the reader hypothesis "confirmed only in a weak sense … refuted under masking", Sec. V.E), and every claim carries the protocol-tuple scope.

### D4 — cross_disciplinary_relevance: **pass**
The three-benchmark distinction is derived inline with the exact estimator-type conditions (Sec. III), damage statistics are defined with formulas (Appendix B), and the closing lesson for benchmark designers ("when the observation encodes the generator, system identification is the baseline to beat") is substantiated by the measurements rather than asserted.

### D5 — writing_and_structure: **pass**
Well-organised REVTeX manuscript with per-target tables carrying CIs and honest captions; minor convention gaps remain (unresolved ORCID/email TODOs at lines 19–21, no formal AIP data-availability/acknowledgments section, figure captions missing the grids' MC budgets) — all fixable without re-review.

## Failure Condition Checks

- **F1** (any mandatory dimension scores block; severity 90): **fired: false** — no mandatory dimension scored block.
- **F2** (two or more mandatory dimensions score warn or worse; severity 70): **fired: true** — D1 = warn and D2 = warn.
- **F3** (any high-priority dimension scores block; severity 60): **fired: false** — D4 = pass.
- **F0** (every mandatory dimension scores pass; severity 10): **fired: false** — D1, D2 = warn.

Highest-severity fired condition: F2 → editorial_decision = major_revision (per contract; I note below that the required changes are small and this sits at the minor/major boundary).

---

# Peer Review Report

## Manuscript Information
- **Title**: Rule reconstruction from a single space–time diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata
- **Manuscript ID**: n/a (simulated panel; repo `ssl-ecas`, `manuscript/main.tex`, 774 lines)
- **Review Date**: 2026-07-05
- **Review Round**: Simulated round-3 readiness check (paper is a revised, round-3-ready draft for Chaos/AIP)

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 1 (Methodology)

### Reviewer Identity
Statistician / ML-evaluation methodologist; NeurIPS Datasets & Benchmarks reviewer and registered-reports advocate; expertise in bootstrap inference, reliability theory (ICC), equivalence testing (TOST), and reproducibility auditing. Sole panel member with access to the code repository as supplementary material.

### Review Focus
(1) Whether the "decision rules committed in advance" were actually followed and whether the registration-status labelling is honest; (2) statistical correctness — the 2·ICC−1 "simulation-limited" benchmark vs the ICC ceiling, bootstrap CIs, per-cell verdict rules, seed handling, train/holdout hygiene; (3) reproducibility affordances, verified directly against the repository.

---

## Overall Assessment

### Recommendation
**Major Revision** — driven by the contract's F2 condition (two mandatory warns). Substantively this is a *borderline-minor* major: the required changes are one corrected number, one corrected count, three disclosure sentences, and a re-run of the authors' own numbers audit extended to prose and tables; but because the paper's central credibility device is its audit trail, I want the corrected audit re-checked before acceptance.

### Confidence Score
**5** — the paper's methodology (reliability theory, bootstrap/TOST inference, registration auditing) is squarely my area, and I verified the claims against the released code and artifacts directly.

### Summary Assessment

This manuscript benchmarks three estimator families for predicting four twin-run damage-response statistics of cellular automata from a single space–time diagram, and shows that transparent rule reconstruction plus re-simulation is "simulation-limited": it matches the accuracy of an independent Monte-Carlo replicate of the ground truth itself. Methodologically this is one of the most disciplined benchmark papers I have reviewed: decision rules, margins, and panels were demonstrably committed to the repository before measurement (verified in git: registration commits a809b2a, 75e1d42, 8f5cb56 each precede their measurement commits), the three-way distinction between the ICC ceiling, the 2·ICC−1 replicate-agreement benchmark, and the large-simulation reference is statistically correct and empirically confirmed by the released reliability artifacts, and inference uses the right resampling unit (held-out rules) with pre-registered verdict vocabulary that the tables respect. Of roughly 46 numbers I traced from the manuscript to measured records, 44 match exactly. The two exceptions — a frozen-CNN median R² of −1.1 in Sec. V.E that the canonical frontier artifact records as −0.93 (apparently inherited from a run the repo itself documents as discarded), and an internally inconsistent "2/88" count in Sec. V.G — plus undisclosed reduced MC budgets in the two degraded-observation figures, are what hold this at warn on both mandatory dimensions. All are quickly fixable; none flips a conclusion.

---

## Strengths

### S1: The three-benchmark distinction is correct, novel in this context, and self-validating
Sec. III (main.tex lines 169–203) derives the independent-replicate agreement benchmark 1 − 2σ²ₑ/(σ²ₐ+σ²ₑ) = 2·ICC−1 and argues it, not ICC, is the right yardstick for an estimator that returns a fresh finite-MC simulation. The algebra is right, and the released artifacts confirm it empirically: `runs/lever_a_local/reliability/summary.json` reports ECA survival agreement 0.9871 against 2·ICC−1 = 0.9872, and the "two_icc_minus_one" field matches the measured agreement to 3–4 decimals on every target in both spaces. The Sec. V.A falsification test — the same predictions rising to the ICC ceiling against a 4096-pair reference (0.9943 vs 0.9936; `mechanistic_eval/summary.json`) — is exactly the check that separates "estimator error" from "comparison-target noise". Benchmark authors in ML would do well to copy this section.

### S2: Registration discipline is verifiable and honestly labelled
The appendix (lines 667–691) refuses the word "pre-registered" for an in-review private repo and instead labels every analysis registered / post-hoc confirmatory / exploratory. I verified the ordering in git: EVALUATION_CRITERIA.md rev 7 (a809b2a, 2026-07-04 14:27) precedes the first R-control measurement commit (ff47ca5, 14:49); rev 8 (75e1d42, 20:40) precedes the C-control measurements (fa994da, 00:52 next day); rev 9 (8f5cb56, 2026-07-05 01:43) precedes the frontier machinery and measurements (717c297 01:58; 111e3df; 0f8e691). The registered margins (δ = 0.05, superiority 0.10, stacking 0.02) appear in rev 7/8 unchanged through the results. A registration deviation (panel-position vs rule-identity seeding) is disclosed rather than buried (lines 687–691).

### S3: Inference machinery is appropriate and the verdict vocabulary is used only as earned
Rule-level cluster bootstrap (the correct exchangeable unit), 10⁴ resamples, TOST with pre-registered δ and sensitivity at 0.02/0.10, and a three-way superiority/equivalence/inconclusive classification (lines 245–259). I checked the verdicts in `runs/m4_range2/paired_stats/summary.json` against the prose: the CNN's survival edge (+0.0787, CI [0.0019, 0.2008]) is correctly reported as sub-margin rather than superiority; mechanistic-vs-GBM damage fraction (point 0.0877, CI excluding 0) is correctly *not* claimed as superiority (lines 366–371). This is rare discipline.

### S4: Reproducibility affordances are real, not performative
Pinned core dependencies (`pyproject.toml`: numpy==2.2.5, torch==2.12.0, …), identity-keyed per-rule RNG (`caspectra/eval/dynamics.py` line 152: `SeedSequence([seed, rule, radius])`), the claimed independence of the mechanistic estimator's streams from the target cache implemented as stated (prime offsets 104729/224737 in `scripts/validate_mechanistic_baseline.py` lines 158, 194), a 21-file test suite including `test_feature_matrix_is_set_independent`-style guards, and per-analysis `summary.json` artifacts under `runs/` from which I could reproduce nearly every table cell. Fig. 7 is bit-identical to the run artifact (md5 of `manuscript/figures/identifiability_v2.pdf` = `runs/m4_range2/frontier_grid/frontier.pdf`).

### S5: Negative, inconclusive, and refuted results are reported at their measured strength
The composed-map advantage is reported as inconclusive with both CIs shown (lines 570–578); the F2 reader hypothesis is reported as "confirmed … only in a weak sense" on noise and "refuted" under masking (lines 526–533); the "anti-shortcut" architecture claim is explicitly retired (lines 429–430). The paper's conclusions would survive an adversarial reading.

---

## Weaknesses

### W1: One Sec. V.E number is not supported by the canonical released artifact
**Problem**: Sec. V.E states "the inverter falls to −5.6 and the frozen CNN to −1.1" at 20% noise. The canonical frontier artifact (`runs/m4_range2/frontier_grid/summary.json`, mtime 13:55, pre-dating the results commit 0f8e691) gives frozen-CNN median R² **−0.93** at 20% noise, and the preserved F1-only summary (`summary_f1only.json`) agrees bit-exactly (−0.93). The −1.1 matches only the F2 table in RESULTS.md (−1.09), whose entire cnn/stack column (0.36/0.13/−0.09/−0.34/−0.73/−1.09 at 3–20% noise) disagrees with both stored artifacts (0.25/0.15/−0.13/−0.25/−0.57/−0.93). The repo's own provenance note states the first F2-inclusive run used a non-canonical CNN checkpoint and "was discarded and fully re-measured … the final run reproduces every shared estimator column bit-exactly (checked programmatically)". The evidence is consistent with the discarded run's cnn/stack numbers surviving into the RESULTS.md prose table and from there into the manuscript.
**Why it matters**: The paper's central credibility device is its audit trail; a number that contradicts the released artifact — in the one place the repo explicitly claims a programmatic consistency check — undermines exactly the claim the appendix stakes ("the full history is released with the article"). It also means the programmatic audit covered JSON artifacts but not the human-written records derived from them.
**Suggestion**: Regenerate every number in Sec. V.E and the RESULTS.md F2 table from `frontier_grid/summary.json`; extend the consistency check to a numbers manifest that the manuscript build validates against (a script emitting every quoted value from the artifacts would close this class of error permanently).
**Severity**: Major (localized, conclusion-preserving — the frozen CNN collapses to ≈ −1 either way and F2-sampled remains best at ≥7.5% — but integrity-relevant).

### W2: The degraded-observation grids' reduced Monte-Carlo budgets are not disclosed
**Problem**: The rev-9 frontier grid was run at n_pairs = 48 with 8 posterior samples (`frontier_grid/summary.json`: "n_pairs": 48, "n_samples": 8) and the rev-8 phase diagram at n_pairs = 64 (`identifiability/summary.json`), versus the production budget of 256 used everywhere else. Neither Sec. V.E nor the Fig. 6/7 captions states this.
**Why it matters**: The read-then-simulate estimators' attainable R² depends on their simulation budget (the paper's own Sec. V.F shows median 0.924 at 16 pairs vs 0.991 at 256), so grid cells are not directly comparable to the matched-regime benchmark numbers without this disclosure; a reader attempting replication at 256 pairs will get systematically different levels.
**Suggestion**: State the budgets in the Fig. 6 and Fig. 7 captions and Appendix B, and add one sentence on how the reduced budget deflates the read-then-simulate family relative to Sec. V.A.
**Severity**: Major (reporting, not validity).

### W3: Internal inconsistency in the ECA prevalence count ("2/88")
**Problem**: Sec. V.G and the Fig. 8 caption say the damage-signature criterion is met by 7.8% of radius-two rules "versus 2/88 elementary orbits", while the same paragraph states the signature selects {54, 106, 110} on ECA — i.e. 3/88 (and the registered range-2 signature's embedded-ECA matches include rule 60 per EVALUATION_CRITERIA rev 5).
**Why it matters**: The sentence compares the *criterion's* prevalence across spaces, so the number must be the criterion's ECA count, not the literature class-IV count; as written the comparison is not like-for-like and a careful reader cannot tell which quantity 2/88 is.
**Suggestion**: Either write 3/88 (criterion prevalence under the ECA-protocol signature) or rephrase to "versus the two literature class-IV orbits among 88".
**Severity**: Minor.

### W4: Two registered reporting items are in the repo but not in the manuscript
**Problem**: (i) The rule-reader was trained with a single seed (RESULTS.md: "range-2, 1 seed, 15 epochs"; rev 9 F2 registers "one seed per rule space initially (seed variance noted as a limitation)"), but Sec. V.E never states the seed count. (ii) Rev-8 C3 requires the posterior-averaged variant's interval calibration to be reported; the measured calibration (1σ coverage 0.25–1.0 per target, n = 4; `completion_policies/summary.json`) appears in the repo but not in the manuscript, which says only that the variant "supplies predictive intervals precisely for those rules" (line 349).
**Why it matters**: Both were pre-registered reporting commitments; the paper's own standard is that such commitments are met in the text, and the single-seed reader qualifies every F2 curve in Fig. 7.
**Suggestion**: Add "one training seed; seed variance untested" to the reader description and the calibration numbers (with the n = 4 caveat) to Sec. V.A or Appendix B.
**Severity**: Minor.

### W5: The registration audit trail is self-hosted; no external timestamp
**Problem**: All registration claims rest on the git history of a private repository released with the article (acknowledged at lines 676–679). Commit timestamps in a self-controlled repo are technically rewritable; there is no OSF/AsPredicted-style external timestamp. (I also note the earliest gates had coarser hygiene — criterion 7's registration and measurement landed in a single commit, c2b99cb — though every analysis this manuscript relies on, revs 7–9, has clean registration-before-measurement ordering.)
**Why it matters**: The paper leans on "committed in advance" for its interpretive weight; an external anchor would make the claim independently auditable rather than trust-the-authors.
**Suggestion**: For round 3, push a signed tag of the registration commits to a public timestamping service or register the rev 7–9 documents on OSF retroactively-dated-as-now, with the git hashes embedded.
**Severity**: Minor.

---

## Detailed Comments

### Title & Abstract
Accurate and appropriately scoped: the abstract states the observation model, distinguishes the 2·ICC−1 benchmark from the ICC ceiling, quotes verified numbers (0.985 vs 0.987; +0.32 stacking; ~2% noise collapse), and pre-announces the conservative language of the by-products. No overclaim detected.

### Introduction
The three organizing results (lines 109–126) are each traceable to a measured record. The commitment paragraph (lines 128–131) is honest about what "registered" means here. Good.

### Benchmark (Sec. II) and reliability (Sec. III)
The protocol tuple is fully specified (IC measure, ring 127, radius-aware horizon, n_pairs = 256, identity-keyed streams). The three-benchmark section is the paper's methodological core and is correct; see S1. One request: state explicitly that the equal-variance additive-noise assumption behind 2·ICC−1 is itself checked by the empirical agreement matching (it is, in the artifacts — surface that one-line fact, since survival's heteroscedasticity is acknowledged two sentences later and a reader may wonder whether it breaks the identity).

### Estimators (Sec. IV)
The mechanistic estimator's completion prior is exposed with a sensitivity analysis rather than hidden (verified: policy medians 0.9905/0.9907/0.9908 in `completion_policies/summary.json`); the CNN's scope disclaimer ("this architecture under this training budget", lines 239–242) is exactly the right epistemic size; the statistical protocol paragraph (lines 245–259) pre-states the verdict rules. Hyperparameters tuned only on training rules; the complex panel force-held-out; probes correctly split (stratified for identity, GroupKFold leave-rules-out for table bits). I found no leakage pathway: dataset seeds, target seeds, reliability replicates, and mechanistic simulation streams are demonstrably disjoint (prime-offset SeedSequences, verified in code).

### Results (Sec. V)
Tables I–IV: every cell I checked matches the artifacts (see verification subsection). The paired-comparison prose respects the registered verdicts, including declining superiority where the point estimate is sub-margin despite a CI excluding zero — commendable. Sec. V.E (identifiability/frontier) is the weak spot: the −1.1 mismatch (W1), the undisclosed n_pairs = 48/64 (W2), and the single-seed reader (W4). Sec. V.F compute numbers all match `compute_pareto/summary.json`. Sec. V.G is appropriately conservative; fix the 2/88 count (W3).

### Discussion
Conclusions stay inside the tested regime; the open problems (larger reader, differentiable simulator, rule-scrubbing interventions) are named as untested rather than insinuated as likely outcomes. The "benchmark designers must break the encoding or accept they are benchmarking identification" lesson follows from the evidence.

### Methods supplement (Appendices A–B)
Appendix A's registered/post-hoc/exploratory census matches the EVALUATION_CRITERIA rev 7–9 labels I checked, and the disclosed seeding deviation is real (it is the rev-6 S3 episode in the repo record, measured, bounded, and fixed with a guard test). Appendix B gives formulas, split construction, architecture, and split-sensitivity numbers that all match the artifacts. Add the grid MC budgets here (W2).

### Reproducibility
Strong overall: pinned core deps (note scikit-learn is only lower-bounded — pin it, since `GradientBoostingRegressor` *defaults* are the baseline of record and its behaviour can drift across versions), dedicated env instructions, 21 test files, canonical per-analysis JSON artifacts, deterministic seed derivations. Two gaps: the human-readable records (RESULTS.md, manuscript prose) sit outside the programmatic consistency check (W1), and `manuscript/figures/identifiability.pdf` is not byte-identical to `runs/m4_range2/identifiability/identifiability.pdf` (md5 differ; presumably a re-render — confirm both derive from the same `summary.json`).

### Methodological fallacies checklist
Checked: no p-hacking surface (estimation-based inference, pre-registered margins); no HARKing (hypotheses in rev 9 are stated numbers-free before measurement, and one is reported as refuted); no selective reporting detected (inconclusive/negative verdicts retained); no train/test leakage found; survivorship/overfitting controlled by leave-rules-out and repeated splits. One residual note: ~12 paired contrasts per space are run at 95% without multiplicity correction; because the framework is pre-registered estimation with margins (not significance-hunting) and the load-bearing CIs are nowhere near their thresholds, this is acceptable, but a sentence acknowledging it would be proper.

### Supplementary-material verification

Legend: ✓ = match; ✗ = mismatch; (~) = partial/ambiguous. Sources: `runs/lever_a_local/*` (ECA), `runs/m4_range2/*` (radius-2), RESULTS.md, EVALUATION_CRITERIA.md, git history.

| # | Manuscript value (location) | Source record | Verdict |
|---|---|---|---|
| 1 | ECA mech survival 0.985 [0.893, 0.997] (Table II) | lever_a_local/full_table: 0.985 [0.8927, 0.9965] | ✓ |
| 2 | ECA mech fraction 1.000 [0.997, 1.000] | 0.9997 [0.9969, 1.0] | ✓ |
| 3 | ECA mech rate 1.000 [0.998, 1.000] | 1.0 [0.998, 1.0] | ✓ |
| 4 | ECA mech fill 0.999 [0.991, 1.000] | 0.9985 [0.9905, 0.9999] | ✓ |
| 5 | ECA 5-stat survival 0.708 [−0.537, 0.924] | 0.7083 [−0.5371, 0.9244] | ✓ |
| 6 | ECA 5-stat fraction 0.924 [−0.840, 0.959] | 0.9244 [−0.84, 0.9588] | ✓ |
| 7 | ECA 5-stat rate 0.965 [−0.517, 0.998]; fill 0.929 [0.849, 0.994] | 0.965 [−0.5172, 0.9979]; 0.9288 [0.8489, 0.9938] | ✓ |
| 8 | ECA CNN 0.700±0.018 / 0.789±0.038 / 0.956±0.015 / 0.916±0.019 (Table II) | cnn_seed_spread: 0.6998±0.0181 / 0.789±0.0381 / 0.956±0.015 / 0.9156±0.0191 | ✓ |
| 9 | ECA ICC 0.994/0.999/0.9995/0.999 (Sec. III) | reliability: 0.9936/0.9988/0.9995/0.9992 | ✓ |
| 10 | ECA agreement 0.987/0.998/0.999/0.998; survival CI [0.978, 0.992] | 0.9871 [0.978, 0.9918] / 0.9975 / 0.9991 / 0.9984 | ✓ |
| 11 | Survival MC std 0.022 (Sec. III) | mc_noise_std 0.0222 | ✓ |
| 12 | 2·ICC−1 identity holds empirically (Sec. III) | two_icc_minus_one 0.9872 vs agreement 0.9871 (ECA survival); 0.974 vs 0.9739 (r2) | ✓ |
| 13 | ECA exact reconstruction 100% (abstract, V.A) | mechanistic_eval exact_inference_rate 1.0, coverage 1.0 | ✓ |
| 14 | Large-sim: ECA survival 0.994 vs ICC 0.994 (V.A) | r2_vs_reference 0.9943 vs ICC 0.9936; reference_n_pairs 4096 (=16×256) | ✓ |
| 15 | ECA baseline LOO 0.73/0.85/0.95/0.93 (App. B) | baseline_loo_orbit_r2 0.7305/0.8502/0.9533/0.9341 | ✓ |
| 16 | Table I ECA row: mech 0.999 / GBM 0.927 / CNN 0.852±0.015 / agree 0.998 / ICC 0.999 | mech median 0.9991; GBM per-target median 0.9266; RESULTS S2 0.852±0.015; reliability medians 0.998/0.999 | ✓ |
| 17 | R2 mech survival 0.977 [0.930, 0.989] (Table III) | m4_range2/full_table: 0.9765 [0.9297, 0.9885] | ✓ |
| 18 | R2 mech fraction 0.997 [0.995, 0.998]; rate 0.997 [0.996, 0.998]; fill 0.985 [0.969, 0.992] | 0.9966 [0.9953, 0.9976]; 0.997 [0.9956, 0.9979]; 0.9849 [0.9693, 0.992] | ✓ |
| 19 | R2 5-stat survival 0.809 [0.554, 0.906]; fraction 0.909 [0.878, 0.932]; rate 0.880 [0.839, 0.912]; fill 0.596 [0.320, 0.775] | 0.8092 [0.5535, 0.906]; 0.9089 [0.8782, 0.9321]; 0.8799 [0.8387, 0.9122]; 0.596 [0.3201, 0.7752] | ✓ |
| 20 | R2 CNN 0.874±0.009 / 0.880±0.020 / 0.865±0.020 / 0.337±0.109 | cnn_seed_spread 0.8743±0.0091 / 0.8799±0.0202 / 0.8646±0.0198 / 0.3367±0.1094 | ✓ |
| 21 | R2 ICC 0.987/0.998/0.998/0.980; agreement 0.974/0.997/0.997/0.959; survival CI [0.945, 0.984]; fill CI [0.900, 0.987] | reliability: exact match incl. [0.9449, 0.9842] and [0.8996, 0.9865] | ✓ |
| 22 | R2 exact reconstruction 97.5% (abstract, V.A) | rule_probe raw_diagram_exact_inference_rate 0.975 | ✓ |
| 23 | Large-sim: R2 survival 0.988 vs ICC 0.987 (V.A) | RESULTS C2: 0.9877 vs 0.987 | ✓ |
| 24 | Table I R2 row: mech 0.991 / agree 0.985 / ICC 0.993 | paired_stats median 0.9907; reliability medians 0.9852 / 0.9927 | ✓ |
| 25 | Coverage 156/160; 4 rules × 1 missing entry; completion medians 0.9905–0.9908 (V.A) | completion_policies: n_fully_covered 156, max missing 1, min coverage 0.9688; zero/one/empirical 0.9907/0.9908/0.9905 | ✓ |
| 26 | CNN−GBM: survival +0.08 [+0.00, +0.20]; fill −0.21 [−0.38, −0.07] superior; fraction CI [−0.09, −0.00], equivalent only at δ=0.10; rate inconclusive (V.B) | paired_stats: 0.0787 [0.0019, 0.2008]; −0.2122 [−0.3836, −0.0737] B_superior; −0.0396 [−0.085, −0.0016] eq. at 0.10; −0.0313 inconclusive/eq. at 0.10 | ✓ |
| 27 | Mech−GBM superior on survival/rate/fill, up to +0.39; fraction CI excl. 0, point below margin (V.B) | 0.1673/0.1171/0.3888 A_superior; fraction 0.0877 [0.0647, 0.1177] inconclusive | ✓ |
| 28 | Mech−CNN superior on fraction/rate/fill, up to +0.60; survival CI excl. 0, point below margin | 0.1273/0.1484/0.601 A_superior; survival 0.0886 [0.0408, 0.2588] | ✓ |
| 29 | Stacking CNN-over-stats: survival +0.32 [0.23, 0.48] (0.56→0.88); fraction +0.03 [0.01, 0.06]; rate +0.03 [0.01, 0.06]; fill +0.08 n.s. (Table IV) | stacking: 0.3204 [0.2322, 0.4787] (0.5563→0.8756); 0.0342 [0.0108, 0.0579]; 0.0301 [0.0058, 0.0557]; 0.0797 CI incl. 0 | ✓ |
| 30 | Stats-over-CNN survival −0.01 [−0.03, −0.00] | −0.0088 [−0.0272, −0.002] | ✓ |
| 31 | Mech-over-stats +0.42 [0.33, 0.71]; +0.14 [0.11, 0.18]; +0.16 [0.12, 0.20]; +0.84 [0.66, 1.00] (0.14→0.98) | 0.4187 [0.3264, 0.712]; 0.1423 [0.1073, 0.1831]; 0.1562 [0.1201, 0.2006]; 0.8422 [0.6604, 1.0056] (0.1363→0.9813) — upper CI 1.0056 silently truncated to 1.00 | ✓ (~ note truncation) |
| 32 | Baseline 20-split spread 0.76 (0.56–0.84) / 0.92 (0.90–0.93) / 0.90 (0.87–0.91) / 0.68 (0.55–0.75) (App. B) | full_table repeated_splits: 0.761 (0.5563, 0.8449) / 0.9195 / 0.8952 / 0.6773 (0.5451, 0.7472) | ✓ |
| 33 | Probes: identity 0.88/0.95 (CNN), 0.65/0.30 (stats); table bits 0.78/0.61 vs 0.69/0.55; majority 0.011/0.001 (V.D) | rule_probe: 0.8778/0.946; 0.6539/0.2965; 0.781/0.6101 vs 0.6923/0.5453; 0.0114/0.0013 | ✓ |
| 34 | Compute: 283 ms @256, 2.2 ms CNN, 1.4 ms stats, ≈22 min training, 15 s GBM, break-even ≈4700, 0.924 @16 pairs (17 ms), 0.966 @32 (32 ms) (V.F) | compute_pareto: 0.2835 s; 0.00223 s; 0.00137 s; 1330 s; 15.27 s; 4729; 0.9244/0.0174 s; 0.9659/0.0323 s | ✓ |
| 35 | Rev-8 sweep: CNN retains 0.43 (2%) → 0.09 (5%); mech robust to 25% mask (0.90), collapses by 50%; density 0.1 mech ≈0.12 (V.E, Fig. 6) | identifiability/summary.json: cnn 0.4294/0.0878; mech mask 0.9006/−0.2013; density 0.1219 | ✓ |
| 36 | F1: mask 40% 0.85 vs 0.24; mask 50% 0.59 vs −0.77; density 0.1 0.77 vs 0.08; label flips 0.99 vs CNN 0.59; noise 2% 0.55 vs 0.38; ε-known 0.38 at 3% (V.E) | frontier_grid/summary.json: all exact | ✓ |
| 37 | Radius-selection cost ≈0.12 (V.E) | 0.83 vs 0.95 at zero noise (grid radius axis / RESULTS) | ✓ |
| 38 | Reader: bit acc 0.73, exact table never; MAP ≤ −2.2 everywhere; sampled best over 7.5–20%, median in [−0.04, 0.17]; inverter −5.6 at 20%; bit acc 0.73→0.70 (V.E) | grid: 0.734, exact 0.0; MAP −2.59…−24.9; sampled 0.02/0.17/−0.04/0.12; det −5.61; RESULTS | ✓ |
| 39 | **"the frozen CNN to −1.1"** at 20% noise (V.E) | frontier_grid/summary.json: **−0.93**; summary_f1only.json: **−0.93** (bit-identical). −1.1 matches only RESULTS.md's F2 table (−1.09), whose cnn/stack column (0.36/0.13/−0.09/−0.34/−0.73/−1.09) disagrees with both artifacts (0.25/0.15/−0.13/−0.25/−0.57/−0.93) — consistent with the documented discarded non-canonical-checkpoint run | ✗ |
| 40 | Landscape 7.8%, Wilson 95% CI [6.9, 8.8]% (V.G, Fig. 8) | RESULTS S4: 234/3000 = 7.80%, CI [6.9, 8.8] | ✓ |
| 41 | ECA confusion: sensitivity 1.0, specificity 0.99, precision 2/3, BA 0.99; detector sensitivity 0.5, precision 0.17; radius-2 detector BA 0.39, precision 0.05, n=231 (V.G) | RESULTS C6: 1.0 / 0.988 / 2/3 / 0.994; 0.5 / 0.17; 0.39 / 0.05 / 231 | ✓ |
| 42 | Map: Spearman 0.67 vs 0.61, Δ=+0.047, CI95 [−0.002, +0.102], CI90 [+0.005, +0.092]; oracle 0.638 (V.G, App. B) | RESULTS C7/R7: 0.673 / 0.605 / 0.638 / identical CIs | ✓ |
| 43 | "versus 2/88 elementary orbits" (V.G, Fig. 8 caption) | Signature-on-ECA selects {54, 106, 110} = 3/88 (RESULTS C6, EVALUATION_CRITERIA rev 5); 2/88 is the literature class-IV count — comparison as written is not like-for-like | ✗ (internal inconsistency) |
| 44 | Reader ≈3×10⁴ parameters (V.E) | RESULTS: 29,664 | ✓ |
| 45 | Registration ordering claims (App. A) | git: rev 7 a809b2a 14:27 < ff47ca5 14:49; rev 8 75e1d42 20:40 < fa994da 00:52(+1d); rev 9 8f5cb56 01:43 < 717c297 01:58 < 111e3df/0f8e691 | ✓ |
| 46 | Fig. 7 = released artifact | md5(identifiability_v2.pdf) = md5(frontier_grid/frontier.pdf); but md5(identifiability.pdf) ≠ md5(runs/…/identifiability/identifiability.pdf) — presumably re-rendered; unverified | ✓ / (~) |

**Totals: 46 traces; 44 match; 1 manuscript↔artifact mismatch (#39); 1 internal inconsistency (#43); 2 annotations (#31 CI truncation, #46 figure provenance).**

---

## Questions for Authors

1. What is the source artifact for "the frozen CNN to −1.1" in Sec. V.E and for the cnn/stack column of the RESULTS.md F2 table? Both released grid summaries record −0.93 at 20% noise. If these values came from the discarded non-canonical-checkpoint run, please state the scope of the re-audit that will catch derived prose/tables, not only JSON artifacts.
2. Please confirm the Monte-Carlo budgets for Fig. 6 (n_pairs = 64) and Fig. 7 (n_pairs = 48, 8 posterior samples) and add them to the captions. How much of the read-then-simulate family's level in the grids is budget deflation relative to the 256-pair benchmark of Sec. V.A?
3. In "7.8% … versus 2/88 elementary orbits", is 2/88 the literature class-IV count or the criterion's ECA prevalence? The signature selects {54, 106, 110} on ECA (3/88), and the registered range-2 signature's embedded-ECA matches also include rule 60.
4. `manuscript/figures/identifiability.pdf` is not byte-identical to `runs/m4_range2/identifiability/identifiability.pdf`. Can you confirm both are rendered from the same `summary.json`, and regenerate the manuscript figure from the canonical artifact in the same build step as Fig. 7?

---

## Minor Issues

### Language / Grammar
- Line 624: "That is the central, positive, and--- we believe---generalizable finding" — stray spacing around the em-dashes.

### Citation Format
- The 2·ICC−1 replicate-agreement construction and ICC(1) would benefit from a standard reliability-theory citation (e.g., Shrout & Fleiss 1979; McGraw & Wong 1996) — currently the derivation is self-contained but uncited.
- TOST equivalence testing likewise deserves a citation (e.g., Schuirmann 1987; Lakens 2017).

### Figures and Tables
- Table IV: the mech-over-stats cone-fill upper CI is 1.0056 in the artifact but printed as 1.00 — state that bootstrap incremental-R² CIs can exceed 1 and are truncated, or report untruncated.
- Fig. 6/7 captions: add rule-panel size construction (80 = subsample of the 160 held-out rules; state the fixed seed) and MC budgets (W2).
- Table I caption: good that the complex-row ICC is flagged as approximate with no separate reliability panel; consider adding the same flag inline in the abstract's "0.98" if quoted there in future revisions.

### Layout / Conventions
- Lines 19–21: TODO comments for ORCIDs and corresponding email remain in the source.
- No formal AIP "Data Availability" and "Acknowledgments" sections; Chaos requires a Data Availability statement — the repository-release sentence in Appendix A should be duplicated there in the journal's format.
- `pyproject.toml`: pin scikit-learn exactly (the GBM baseline of record uses library defaults, which can change across versions).

---

## Dimension Scores (rubric, 0–100)

| Dimension | Score (0–100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 82 | Strong | Novel benchmark framing (system identification as the baseline to beat; three-benchmark distinction); not a new method class |
| Methodological Rigor (25%) | 80 | Strong | Registration + inference design near-exemplary; deductions for the traced mismatch (#39) and disclosure gaps (W2, W4) |
| Evidence Sufficiency (25%) | 85 | Strong | Every load-bearing claim carries a CI and traces to a released artifact; negative/inconclusive results retained |
| Argument Coherence (15%) | 88 | Strong | Tight evidence→claim chain; scope statements exemplary; one count inconsistency (W3) |
| Writing Quality (15%) | 82 | Strong | Dense but precise two-column REVTeX; minor convention gaps (TODOs, data-availability section) |
| **Weighted Average** | **83.0** | — | Ordinally accept-range per the rubric mapping; however the contract's failure conditions govern the decision, and F2 fired (two mandatory warns) → **Major Revision** |

---

## Editorial Decision

Major Revision (contract F2: D1 = warn, D2 = warn; severity 70) — the substantive fixes are small (correct the Sec. V.E number and RESULTS F2 table from the canonical artifact, fix the 2/88 count, disclose grid MC budgets and the reader's single seed, extend the numbers audit to prose), but re-review is warranted to confirm the corrected audit before acceptance.
