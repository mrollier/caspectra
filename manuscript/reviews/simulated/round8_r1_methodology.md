# Peer Review Report

## Manuscript Information
- **Title**: Rule reconstruction from a single spacetime diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata
- **Manuscript ID**: ssl-ecas / branch `review-round8-gemini`, commit `0b3cef9` (18 pp, REVTeX `aip,cha`)
- **Review Date**: 2026-08-23
- **Review Round**: Round 8 re-review (presentation-only revision responding to the 21 Aug 2026 report)

*All line numbers below refer to `manuscript/main.tex` at commit `0b3cef9`. The file changed under me mid-review (`489cee7` → `0b3cef9`); every finding here was re-verified against `0b3cef9`, which is the version behind the 18 pp PDF. Two findings I had drafted (the twin-run caption's "four statistics", and the exemplar caption's unattributed rate/fill) were fixed in `0b3cef9` and are withdrawn.*

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 1 (Methodology)

### Reviewer Identity
Statistician working on ML-benchmark evaluation, calibration, and pre-registration; my competence is in whether reported quantities mean what they are said to mean, whether uncertainty travels with point estimates, and whether a revision has silently moved a claim.

### Review Focus
Three questions only: (1) did the presentation pass preserve the statistical claims exactly — numbers, hedges, scope conditions — against their stated locations; (2) are the two new figures methodologically sound, in particular the single-pair-vs-256-pair distinction, the light-cone geometry, and the honesty of an exemplar-selection rule that leans on a detector performing at chance; (3) do the relocated decoder admission and the trimmed captions still let a reader read the tables and figures correctly, now that the reduced-budget ceilings live in Appendix B. I did **not** re-litigate the registered design (panel composition, margins, protocol tuple).

---

## Overall Assessment

### Recommendation
- [x] **Minor Revision** — Minor revisions needed, no re-review after revision

### Confidence Score
**5** — the claims at issue are calibration, reliability-benchmark, and reporting questions, and every one of them was checkable against the released artifacts, which I re-ran.

### Summary Assessment

The revision is a presentation pass over a benchmark study that constructs an exact system-identification baseline for a perturbation-defined target, calibrates every estimator against replicate reliability and a noise-unit statistic ρ, and maps the frontier where identification fails. On my central question the answer is clean: the pass did **not** move a claim. I re-ran `scripts/audit_manuscript_numbers.py` (0 failures), independently recomputed the ρ table from the released seed-0 predictions and per-rule σ̂_e (ECA CNN reproduces as 6.07 / 35.45 / 20.48 / 12.49 against Table IV's 6.1 / 35 / 20 / 12), reproduced the selected-checkpoint bands on both frontier panels (0.458–0.639 canonical, 0.388–0.813 complement, quoted as 0.46–0.64 and 0.39–0.81), and diffed the numeric tokens of the old and new sources: every deletion is a duplicate, every addition belongs to a new figure or the new Appendix F. The relocated decoder admission (Sec. IV F head, ll. 817–826) is accurate and its coverage figures verify against `frontier_grid_calibration/summary.json`. The new twin-run figure is the honest kind: it says "this single pair", and its printed statistics really are computed by the benchmark's own formulas.

The weaknesses are all in the printed text rather than the analysis, but three of them are factual errors that a careful reader can catch, and one of them (W3) is newly catchable *because* of the new figure. The caption diet cost Figs. 2 and 4 the distinction between two different scoring ceilings; Table IV's caption asserts a drop-out property that holds only for the mechanistic estimator; and Sec. II B's reassurance that "nothing in this paper sits near" the light-cone boundary is contradicted by held-out rule 150. All fixes are sentence-level and verifiable, hence Minor Revision.

---

## Strengths

### S1: The presentation pass is verifiably claim-preserving — I checked, rather than took it on trust
With no response letter this round, I reconstructed the change record from `git log main..HEAD` and the round-8 section of `trimmed_material.md`, and then tested it three ways. (i) `PYTHONPATH=. python scripts/audit_manuscript_numbers.py` → `0 failure(s)`, covering ~200 quoted values including the whole ρ table, the per-panel reliability columns, the calibration coverages, the seed bands and the survival-band cells. (ii) A numeric-token diff of `main:manuscript/main.tex` against the current file: the only tokens that lost an occurrence are `0.993`, `0.99`, `0.59`, `3.1`, `1.4`, `80`, `256`, `2`, and I traced each to a *duplicate* removal where the value survives elsewhere — except `0.993` and `256`, which is W1. (iii) Independent recomputation from artifacts of the numbers the audit does *not* cover: the complement selected-checkpoint band (`frontier_grid_degaug_sel_seed{0,1,2}_complement`) gives min 0.388 / max 0.813 against the quoted 0.39–0.81, and the canonical panel 0.458 / 0.639 against 0.46–0.64. `trimmed_material.md`'s round-8 entry, which itemises every removed clause and every restored hedge including its own adversarial drift audit, is a better artifact than most response letters I receive.

### S2: Fig. 1 (twin_run) handles the single-pair / 256-pair distinction correctly, and its numbers are the benchmark's own
The caption (ll. 262–267) says the printed values are "the three conditional statistics of *this single pair* … The targets average n_pairs = 256 such pairs per rule", and reports survival in words because for one pair it is a binary event — that is the right call, and it is the distinction the whole benchmark rests on. I checked the generator against the target code: `make_figures.py` computes `rate = extent/(2·TWIN_STEPS)` and `fill = final.sum()/extent` with `extent = pos.max()−pos.min()+1`, which is exactly `caspectra/eval/dynamics.py:125–127` (`extent/(2·max_speed·n_steps)`). The one deviation — centre flip instead of a uniform flip — is disclosed in the caption and is exactly invariant, because the benchmark re-centres positions on the flip. Rule 204's panel (rate 0.0081, fill 1.00) reproduces the sparse-end degeneracy the text cites it for, and the drawn light cone (half-width 61 at the final of 62 rows) matches the diagram's actual causal cone.

### S3: The relocated decoder admission (R4) is statistically accurate, correctly scoped, and quantitatively checkable
Section IV F now opens with "*Scope of the noise-axis verdicts, stated first*" (ll. 817–826). Its two coverage numbers verify exactly: `runs/m4_range2/frontier_grid_calibration/summary.json` gives `interval_coverage_1sigma` = 0.5781 at 2 % noise and 0.1344 at 20 %, quoted as 0.58 and 0.13. More importantly the inferential statement is the correct one — "Every noise-band verdict in this section therefore bounds *the estimators evaluated*, not the read-then-simulate family" — which is precisely the right scope for a missing-model-class limitation and is echoed in the abstract (l. 54) and Discussion (ll. 1148–1151). Promoting this from the Discussion to the head of the results section was the correct editorial decision and it was executed without weakening the admission.

### S4: ρ, and the insistence on reporting it beside R², remains the paper's best methodological contribution
Equation (2) with per-rule σ̂_e, pooled over rules rather than averaged as per-rule ratios, is the right construction — the docstring's justification (pooling makes √2 and 1 exact references) is sound, and Sec. II C's delta-method account of the finite-K and finite-panel fluctuation (0.14 and ~0.6 ρ-units) is the kind of second-order honesty most benchmark papers omit entirely. The rule-level bootstrap everywhere, the refusal to lean on the Gaussian ICC identity for heteroscedastic targets, and Appendix A's framing of the matched-regime equivalence test as an *implementation audit* rather than a hypothesis test are all correct and rare.

### S5: The reduced-budget pointer chain resolves
Appendix B's new "*Reduced-budget scoring ceilings*" paragraph (ll. 1367–1378) holds the full arithmetic, and all three consumers — Fig. 2 (l. 758), Fig. 4 (l. 802), Table VII (l. 1021) — restate the median ceiling *inline* rather than only pointing. A reader never has to turn the page to know the curves are bounded by 0.963 / 0.953 and not 1. The chain is sound; W1 is about what the compressed sentence now says, not about the pointer.

---

## Weaknesses

### W1: The trimmed Fig. 2 and Fig. 4 captions now assert one ceiling for curves that have two
**Problem**: Fig. 2's caption reads "the estimator simulates at n_pairs = 64, so **every curve** is bounded by the reduced-budget ceiling of Appendix B — median 0.963, *not* 1" (ll. 756–758). Fig. 4's reads "curves must be read against the reduced-budget ceilings of Appendix B (median 0.953), not against 1" (ll. 801–802). Both panels plot the frozen CNN and the five statistics alongside the resimulating estimators, and Appendix B itself says the opposite of the caption: "a direct estimator predicting the latent mean keeps the ICC ceiling (0.993)" (ll. 1370–1372). The pre-revision captions carried this ("A direct estimator predicting the latent mean keeps the ICC ceiling (0.993)"; "…median 0.953 …, against 0.993 for a direct estimator"); the diet dropped it, and my token diff shows `0.993` lost exactly one occurrence and `256` one.
**Why it matters**: Fig. 2's own caption then makes a cross-family comparison — "the mechanistic estimate (green) falls below the frozen CNN (blue) beyond ~2–5 %" (ll. 761–762) — between two curves the caption has just told the reader share a ceiling of 0.963 when in fact one is capped at 0.963 and the other at 0.993. The error runs *against* the paper's thesis (it flatters the direct estimators), so it is not self-serving, but the crossover in Fig. 2(b) is a headline of Sec. IV E and Table VII, and it is read off exactly these two curves.
**Suggestion**: Restore ~15 words to each caption: in Fig. 2, "…so the resimulating curves are bounded by the reduced-budget ceiling of Appendix B (median 0.963); the frozen CNN and the five statistics predict the latent mean and keep the ICC ceiling, 0.993." Same clause in Fig. 4.
**Severity**: Major

### W2: Table IV's caption claims zero-noise rules "drop out" of ρ; they drop out of the denominator only
**Problem**: The caption (ll. 618–621) states: "Rules whose target carries no Monte-Carlo noise (the fully ordered ones, 3 of 18 on ECA, 1 of 160 on radius two) contribute zero to both sums and so drop out; the mechanistic estimator's error on them is exactly zero." In `scripts/analyze_round6_metrics.py:_rho`, `err2` is summed over **all** rules while `var` is summed over all rules, so a rule with σ̂_e = 0 contributes a positive numerator against a zero denominator for any estimator whose error there is non-zero. Reproducing the published cells from `runs/lever_a_local_sel_seed0/held_out_preds_np256_mech.pkl` and `runs/lever_a_local/reliability_heldout/per_rule_sigma_e.npz`:

| | published ρ (ECA cone fill) | ρ excluding σ̂_e = 0 rules from *both* sums | share of numerator from those rules |
|---|---|---|---|
| mechanistic | 1.82 | 1.82 | 0.000 |
| 5 statistics | 12.62 (Table IV: 13) | **4.84** | **0.853** |
| deep CNN | 12.49 (Table IV: 12) | **9.00** | **0.482** |

Two further inaccuracies in the same parenthetical: the count is target-specific — the ECA zero-σ̂_e counts are 3 / 2 / 2 / **9** for survival / fraction / rate / fill, and "3 of 18" is the survival column only; and the rules concerned are not "the fully ordered ones" — rule 150 (additive, survival 1.000) is deterministic on all four targets, and seven rules with survival between 0.47 and 0.81 (1, 3, 12, 19, 156, 200, 232) have σ̂_e = 0 on fill alone, because fill is pinned at exactly 1 by the sparse-end degeneracy the paper documents in Sec. II B.
**Why it matters**: On ECA cone fill, ρ is not "error in units of replicate noise" — 85 % of the boosted baseline's numerator is contributed by rules whose noise unit is zero. The headline range "3–35" survives untouched (the 35 is ECA fraction, 0.2 % affected; the 20 is ECA rate, 0.7 %), and radius two is affected by ≤ 11 %, so no verdict moves — but the caption asserts an invariance the statistic does not have, in a table the revision has just promoted into the Introduction. This is pre-existing (rev. 13/14), not a product of this round's pass.
**Suggestion**: Either implement the caption (mask σ̂_e = 0 rules out of both sums, which changes only the two ECA cone-fill cells) or correct the caption: give the per-target counts (3/2/2/9 on ECA, 1 on radius two), say that such rules leave the denominator but not the numerator for estimators with non-zero error there, and report the ECA cone-fill share. One sentence either way.
**Severity**: Major

### W3: "The largest rate we observe anywhere is 0.816" is false, and there is a one-cell off-by-one in the rate definition that the new figure now exposes
**Problem**: Sec. II B (ll. 283–286) and Appendix B (ll. 1393–1395) both state that extent counts endpoints, so `rate ≤ (2rT+1)/(2rT) = 1.008`, "and the largest rate we observe anywhere is 0.816, so nothing in this paper sits near that boundary." Both halves are wrong. (i) 0.8155 is the maximum over the 3000-rule radius-two landscape sample (`cache/targets_42ad0aa3f2ac1221.npz`). Over the 88 ECA orbits the maximum is **0.9919** (rules 90 and 150; `cache/targets_1cab053a4c60559c.npz`), and rule **150 is in the 18-rule held-out panel** behind Tables II and IV at rate 0.9919. (ii) 0.9919 is not an accident: `ECASimulator.evolve(ic, n_steps)` returns `n_steps` rows with the rule applied `n_steps − 1` times, while `damage_spreading_features` normalises by `2·max_speed·n_steps`. So at T = 62 the extent is measured after 61 applications, `ext ≤ 2r(T−1)+1 = 123`, and the attainable maximum is `123/124 = 0.9919`, not 1.008. I verified this directly: a lone flip under rule 90 gives extent 123 and rate 0.99194, exactly the cached value.
**Why it matters**: Three consequences. The reassurance "nothing in this paper sits near that boundary" is exactly backwards on the elementary panel, where the additive rules sit *at* the ceiling — a saturation at the top of a regression target on a panel of 18 rules. The stated bound 1.008 is unattainable, so the axis label of Fig. 5 ("light speed = 1.008 here") and the II B convention paragraph both mis-state the target's range. And the new Fig. 1 makes it checkable for the first time: it draws the cone at half-width 61 and normalises by 124, so a reader who measures the picture gets 0.992 where the text promises 1.008. Nothing downstream changes — targets and predictions share the normaliser and it is a monotone rescaling — which is why this is a correction, not a re-analysis.
**Suggestion**: In Appendix B (i): "ext ≤ 2r(T−1)+1, so rate ≤ 1 − 1/(2rT) = 0.992 — attained by the additive rules." In Sec. II B: "the largest rate we observe on the radius-two panels is 0.816; on the elementary panel the additive rules 90 and 150 sit at that attainable maximum, 0.992." Update Fig. 5's axis label to 0.992.
**Severity**: Major

### W4: The Introduction's new headline illustration is drawn from the paper's most degenerate target–panel cell, and its "0.98" is in no table
**Problem**: The new so-what sentence (ll. 182–185) reads "a conventional R² here can read 0.98 and still sit twenty times above the target's own noise floor (Sec. IV A)". Following the pointer, Sec. IV A (l. 494) gives 0.979 and Table IV's caption gives 0.98 with ρ = 20 — but Table II's corresponding cell is **0.960 ± 0.019** (five-seed mean ± s.d.). The 0.979 is the seed-0 selected checkpoint (`runs/analysis/round6_metrics_sel/summary.json` → `eca.A1_rho.cnn.spreading_rate.r2 = 0.9793`); Table IV is *entirely* a seed-0 artefact (`analyze_round6_metrics.py` defaults to `runs/*_seed0/held_out_preds…`) and its caption never says so, although Table I already uses the `$^\ast$seed-0 checkpoint` convention for exactly this. Separately, the ECA held-out spreading-rate targets are 0.992, 0.905, 0.376, 0.111, 0.026 and thirteen values ≤ 0.017 — a two-cluster target on which any ordered/chaotic separator scores ≈ 0.98.
**Why it matters**: The sentence is now the abstract-adjacent framing of the paper's central methodological device, and a reader who checks it against the obvious table finds a different number. Worse, the chosen cell is the one where R²'s inflation has a second explanation the paper itself supplies two paragraphs later: the between-rule variance is carried by two rules, so this R² is mode assignment in exactly the sense Sec. IV A diagnoses for survival — which weakens the illustration rather than strengthening it. The equivalent radius-two cell (R² 0.875, ρ = 10, 160 rules) carries the same lesson on a well-populated panel.
**Suggestion**: (a) Add `$^\ast$seed-0 checkpoint` to Table IV's caption, matching Table I. (b) Either move the Introduction illustration to radius two, or add five words in Sec. IV A noting that the ECA rate panel is strongly bimodal (two of eighteen rules above 0.9, thirteen below 0.02), so that ρ and the mode-assignment reading are pointing at the same fact.
**Severity**: Major

### W5: The exemplar-selection rule is presented as exhaustive over the signature region, but the agreement test could reach at most ~11 % of it, and the agreeing set is replicate-dependent
**Problem**: Appendix D (ll. 1574–1576) says Fig. 6 shows "the three rules on which the two criteria nevertheless agree — **the only rules in the region** for which a picture illustrates rather than overclaims." From `runs/analysis/glider_validation/summary_r2.json`: the detector was run on a **300-rule subsample** (231 applicable), of which 25 met the damage signature; it flagged 54 positives with tp = 6, precision 0.053, balanced accuracy 0.394. The plotted signature region contains **234** rules. So ~209 of the 234 were never eligible for the agreement test at all, and "the only rules" describes a search over ≈ 11 % of the region. Furthermore the agreeing set is not stable across target replicates: in the validation replicate the detector ∧ signature set is {345313848, 148590960, 2464084674}, whereas the plotted set gives {1322117304, 148590960, 2464084674} — `make_figures.py` documents the reason (rule 345313848 sits at rate 0.288 against the registered 0.28 window in the S4 replicate), but the manuscript does not. Finally, all three exemplars sit at (rate, fill) = (0.19, 0.54), (0.19, 0.58), (0.23, 0.58), i.e. in the high-fill upper edge of a region spanning roughly rate 0.15–0.28 and fill 0.31–0.62; the sparse-cone lower half — the part the criterion name most directly describes — is not illustrated.
**Why it matters**: This paper's discipline about what a threshold region is and is not is one of its best features; an exhaustiveness claim ("the only rules") over an untested majority is the one place that discipline slips. And a selection rule whose membership flips between two Monte-Carlo replicates of the same criterion is precisely the sensitivity the paper elsewhere insists on disclosing (σ̂_e per rule, ICC, replicate benchmarks).
**Suggestion**: Replace with "the three rules, of the 25 signature rules inside the detector's 300-rule validation subsample, on which both criteria fire"; add one clause on the boundary case ("a fourth rule fires the detector and meets the criterion in the validation replicate but sits at rate 0.288 in the plotted one — the criterion is replicate-sensitive at its rate edge"); and note in the caption that all three lie in the region's high-fill edge.
**Severity**: Major

### W6: Fig. 6 prints twin-run coordinates but is defended by localized-seed properties whose measured values are never shown
**Problem**: After the `0b3cef9` fix the caption correctly says the printed rate and fill are twin-run coordinates "not measurements of the seeded run drawn here" (ll. 1544–1546) — good. But the descriptive claim the figure is *for* — "persistent, non-space-filling structures whose total extent grows sub-ballistically" (ll. 1541–1543) — is a statement about the localized-seed experiment, and its measured values are in the artifact and not on the page: alive = 1.0 / 1.0 / 1.0, growth = 0.629 / 0.230 / 0.456, fill = 0.461 / 0.286 / 0.425 for panels a / b / c. Two further omissions: "sub-ballistic" here means growth ≤ 0.9 of light speed (the registered `GLIDER_SIGNATURE` threshold), which is why one front can hug the dashed cone in every panel without violating the criterion; and the drawn diagram is the **first surviving seed of 24** (`make_figures.py` keeps `candidate` from the first iteration), whereas the detector's growth and fill are *medians over 24 seeds* — the exact analogue of the single-pair caveat that Fig. 1 handles so well.
**Why it matters**: As printed, a reader cannot verify the caption's descriptive claim from the figure, and the visual impression (a dense striped wedge with a light-speed front) argues against "non-space-filling, sub-ballistic" unless the thresholds are stated.
**Suggestion**: Print `alive / growth / fill` per panel in place of, or beside, the twin-run coordinates; state "sub-ballistic = growth ≤ 0.9 (App. E thresholds)"; add "one of the 24 seeds the detector medians over".
**Severity**: Minor

### W7: The pseudo-posterior's interval calibration is measured on two axes but recommended on three
**Problem**: The new scope paragraph (ll. 817–826) prices the noise axis, and Sec. IV F(i) reports masking coverage (0.86 clean → 0.74 at 50 %) and noise coverage (0.58 at 2 %, 0.13 at 20 %). `runs/m4_range2/frontier_grid_calibration/summary.json` contains exactly two axes — `mask` and `noise`. Table VII nevertheless recommends the decoder for "extreme IC density" on the strength of a point R² (0.77 vs det 0.08 at density 0.1, l. 1012), with no interval calibration anywhere, and Appendix A (l. 1288) reports "the one outstanding rev.-9 reporting item, the posterior-interval calibration, completed here."
**Why it matters**: The head-of-section paragraph now reads as the section's complete scope statement — that is what promoting it was for — so the unmeasured third axis becomes invisible. The density axis is also where the mechanism should bite hardest: at density 0.1 the table is barely exercised, so per-entry counts are smallest and the entrywise independence approximation least tested.
**Suggestion**: One clause at the end of the scope paragraph: "Interval calibration was measured on the masking and noise axes only; the density-axis recommendation rests on point accuracy." Mirror it in Table VII's density row and soften "completed here" in Appendix A.
**Severity**: Minor

### W8: The intermediate-survival-band claims are quoted as point estimates although the artifact carries their intervals, and the revision promoted them into the Introduction
**Problem**: Sec. IV A (ll. 496–503) states that in the band the boosted baseline and the CNN "fall to −0.87 and −1.05 on ECA … worse than predicting the band mean on the elementary panel". `round6_metrics_sel/summary.json → eca.A5_survival_band` gives the intervals: boosted −0.871, 95 % CI [−2.338, −0.118]; **CNN −1.045, 95 % CI [−4.088, +0.553]**, on n = 14 rules. The "worse than the band mean" reading is earned for the boosted baseline and not for the CNN, whose interval covers values well above zero. The presentation pass promoted the conclusion phrase "classifiers that had been read as regressors" from Sec. IV A into the Introduction (ll. 190–191), so the point estimates now travel further than before while the hedge stays behind.
**Why it matters**: This paper reports a rule-bootstrap interval for essentially every other comparison and explicitly declines to read a ranking off the underpowered 18-rule ECA panel in Sec. IV B ("that panel is underpowered for tight per-target intervals and we do not read a ranking into it"). Applying that standard unevenly here is the one internal inconsistency in an otherwise scrupulous inferential scheme.
**Suggestion**: Quote the two ECA intervals inline and attribute the "worse than the band mean" reading to the boosted baseline; let the radius-two band (0.41 and 0.75 on 40 rules) carry the CNN half of the claim.
**Severity**: Minor

### W9: The new Discussion paragraph extends "level with" to a comparison that the paper's own margin would not call
**Problem**: The neural-boundary paragraph (ll. 1126–1130) argues that "a nearest-neighbour lookup in the raw five-statistic space already sits level with the trained estimators and, run inside the network's own bottleneck, reproduces its score". Sec. IV C's numbers: raw five-statistic retrieval 0.821 (radius two) and 0.828 (ECA); bottleneck retrieval 0.864 and 0.883; CNN 0.880 and 0.847. The "level with" verdict in Sec. IV C is carried by the bottleneck pair (0.864 vs 0.880; 0.883 > 0.847). For the *raw* five-statistic retrieval on radius two the gap is 0.059 median R² — larger than the paper's own δ = 0.05 practical-equivalence margin — and no interval is reported for any retrieval-versus-trained comparison anywhere in the paper.
**Why it matters**: This is the single place where the presentation pass comes closest to strengthening a claim, and it does so inside the paragraph added to answer the referee's R3. The retrieval diagnostic is one of the paper's two transferable contributions (the Discussion says so at ll. 1071–1075), so it is worth stating at exactly its measured strength.
**Suggestion**: Use the bottleneck numbers for the "level with" clause, or write "within 0.02–0.06 median R² of the trained estimators". Ideally add a paired rule-bootstrap CI for (retrieval − CNN) per panel — the machinery is already in place and the folds are already grouped by rule.
**Severity**: Minor

### W10: "Statistically indistinguishable from" invites exactly the reading Sec. IV A forbids
**Problem**: The abstract's new gloss (ll. 42–43): "*exchangeable* with — statistically indistinguishable from — an independent Monte-Carlo replicate". Equation (1) states equality *in distribution* of the pair (Ŷ, Y₁) with (Y₂, Y₁), and Sec. IV A is emphatic that "there is no hypothesis to test, only an implementation to audit" (ll. 451–452). In ML/statistics usage "statistically indistinguishable" almost always means "a test failed to reject", which is a claim about power, not about distributional identity — and the paper does report a 6-of-8 equivalence audit in Appendix A that a reader could easily fuse with this phrase.
**Why it matters**: The distinction between "this is an identity" and "we tested and found no difference" is the paper's single most important framing move; the plain-language gloss should not blur it.
**Suggestion**: "— identical in distribution to —".
**Severity**: Minor

---

## Detailed Comments

### Title & Abstract
The title is accurate and the "simulation-limited" qualifier does real work. The abstract's plain-register rewrite is a clear improvement: the opening now states the structural fact (damage statistics "are not a function of any single observed diagram") rather than asserting a stronger non-existence claim, and the drift audit's restoration of "for those rules" (l. 44) correctly re-attaches the scope condition to the exchangeability sentence. One residual: W10.

### Introduction
The paragraph breaks are a genuine readability gain and I found no claim moved by them. The three so-what sentences are the right idea; the second (ll. 190–194) chains two findings of different scope — the mode-assignment result is survival-specific, while the retrieval result is a four-target median — so "with much of the remaining score reproduced by a training-set lookup" reads as though the lookup explains the residual *survival* skill. A four-word scope marker ("across the four targets") fixes it. The first so-what is W4.

### Methodology / Research Design
Section II C remains the strongest part of the paper. The three-benchmark distinction, the measured-rather-than-derived replicate agreement, the refusal to lean on the Gaussian identity under heteroscedasticity, and the delta-method pricing of ρ's own sampling variability are all correct and correctly stated; the `0b3cef9` split of that paragraph improved it without touching a number. Section III's statistical protocol (superiority / TOST-equivalence / inconclusive, with only the earned label used) is exemplary and unchanged. Sections II B and Appendix B (i) carry W3. The evaluation-protocol conventions (1)–(7) in Appendix B are the right place for convention (7) and the reduced-budget ceilings; my only objection is what the captions now say about them (W1).

### Results / Findings
Table I and Table II are unchanged and reproduce. Table IV carries W2 and needs the seed-0 footnote (W4). Table VII survived the diet with its scope caveats intact — "'none reliably recommendable' is a claim about these estimators, not all estimators" and the non-composition warning both remain — but it lost the pointer to the bootstrap clipping convention (now only at Appendix B, l. 1349), and the "noise 20 %" row is precisely a collapsed-cell row where clipping binds; restore four words. Sec. IV F(iv)'s new inline note distinguishing the 0.859 final-epoch number from Table I's 0.880 selected-checkpoint number (ll. 960–963) is a real improvement and resolves what would otherwise have been a table/text conflict. Figures: W1, W5, W6.

### Discussion
The R3 neural-boundary paragraph is a good answer to a fair challenge and its central claim — that the shortcut incentive is set by the task rather than the backbone — is the right one. Two calibration notes. The "bracket that family from both ends at this budget" argument leans on the `resnet18` control, which Sec. IV F(iii) discloses as "a single seed on the identical grid cells" (l. 903) while the constrained CNN elsewhere carries a five-seed spread of up to ±0.036; add "(single seed)" to the Discussion clause. And the new attention/graph-network conjecture (ll. 1133–1141) is correctly labelled — "That is a conjecture from the diagnostics above, not a result" — but its supporting claim, that a global receptive field makes generator-matching easier, is not measured anywhere in the paper: the retrieval diagnostic was run in a 64-d convolutional bottleneck and in the five-statistic space. Consider converting the conjecture into a testable prescription, which is stronger and costs nothing: whoever tries an attention or graph model should run the retrieval diagnostic inside its own embedding as a required control. The remainder (W9 aside) is well scoped, and the stochastic-CA / Domany–Kinzel passage correctly states what has not been run.

### Conclusion
No over-inference that I could find. The final guidance paragraph correctly re-attaches the protocol tuple and the price tag, and the redirect from `sec:compute` to Appendix F is intact.

### References
Outside my remit; I note only that the round-8 restructure preserved the `vispoel2026structure` citation in the Introduction after the drift audit flagged its loss, and that `derridaweisbuch1986` survives in the new Appendix F.

---

## Questions for Authors

1. **ρ and zero-noise rules (W2).** Was the pooled form intended to include rules with σ̂_e = 0 in the numerator? If yes, please correct the caption and report the ECA cone-fill numerator share (0.85 / 0.48); if no, masking those rules out changes only the two ECA cone-fill cells (13 → 4.8, 12 → 9.0). Which do you intend, and does the choice need an EVALUATION_CRITERIA note given ρ was registered at rev. 13/14?

2. **The rate ceiling (W3).** Do you agree that `evolve(ic, n_steps)` applies the rule `n_steps − 1` times, so the attainable maximum rate is 123/124 = 0.992 rather than 1.008, and that held-out rule 150 sits exactly there? If so, is any statement other than the two sentences I identified (Sec. II B, Appendix B (i)) and Fig. 5's axis label affected?

3. **Exemplar exhaustiveness (W5).** How many of the 234 plotted signature rules were inside the detector's 300-rule validation subsample, and can the four-versus-three boundary case at rate 0.288 be stated in the caption? I would rather see "three of the 25 signature rules the detector was ever run on" than "the only rules in the region".

4. **Figure-to-artifact traceability.** `manuscript/make_figures.py` now simulates its own diagrams rather than reading a cache. Will the released archive pin the `caspectra` commit and the RNG streams used for Figs. 1 and 6, so that the audit script's exit-0 guarantee extends to the figures as well as the numbers?

---

## Minor Issues

### Language / Precision
- l. 944: "The practical corollary, echoed in Table VII" — Table VII now echoes only "validation-selected checkpoint" (l. 1008); the "validate the trained seed on held-out corrupted diagrams" half is no longer in the table. Either restore it to the caption or soften "echoed" to "partly reflected in".
- ll. 671–676: after the trim, "realizes essentially none of *that* increment" has a slightly ambiguous antecedent (the +0.09 boosted-base survival increment, not the +0.33 headline). "…none of that survival increment" restores it.

### Figures and Tables
- **Fig. 1 caption**: the panels are drawn to the damage horizon (62 rows for ECA), not the 127-row observed diagram of Sec. II A. Since the observation/experiment distinction is the paper's central conceptual move, the figure teaching it should label its own time extent: "…time running downward to the damage horizon T = 62; the observed diagram the estimators see is the full 127 rows."
- **Fig. 1, rule-110 panel**: the "extent" annotation is 6 pt white-on-black-stroke drawn *inside* the bright damaged region and is close to illegible at print size. Move it below the bracket into the black background, or into the x-label.
- **Fig. 6**: generated at `figsize=(5.4, 3.3)` but included at `\columnwidth` (≈ 3.42 in), a 0.63× reduction that renders its 8 pt panel titles at ≈ 5 pt. Regenerate at column width, or use `figure*`.
- **Table IV**: add the seed-0 marker (W4) and, if W2 is resolved by exclusion, a note that the excluded-rule counts are per target.
- **Table VII caption**: restore the four-word pointer to the bootstrap clipping convention (Appendix B, l. 1349).
- **Sec. II B, l. 289**: "this degeneracy affects 0.13 % of the sampled radius-two rules" verifies exactly (4/3000), but the elementary rate is never given and is much higher: **24 of 88 orbits** have cone fill exactly 1, seven of them in the 18-rule held-out panel. Since Fig. 1's rule-204 panel is cited right there and ECA cone fill appears in Tables II and IV, one clause is warranted.

### Layout
- `main.log`: 18 pp, no overfull boxes; 7 underfull-hbox warnings, all in table cells and the guidance table's `p{}` columns. Cosmetic.

---

## Dimension Scores

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 84 | Strong | Unchanged by a presentation pass; the calibrated identification baseline plus the frontier map remains a genuine contribution, and the novelty boundary is auditable in Table VIII. |
| Methodological Rigor (25%) | 82 | Strong | Design and inference are near-exceptional (pre-registration, reliability benchmarks, ρ, symmetric fairness controls, an audit script that exits 0). Docked for W2 (a statistic that does not have the invariance its caption claims) and W3 (a definitional off-by-one, twice stated as fact). |
| Evidence Sufficiency (25%) | 87 | Strong | Every quoted number I tested reproduced from released artifacts. Docked for intervals that exist in the artifacts but not on the page (W8, W9) and one recommendation axis with no calibration measurement (W7). |
| Argument Coherence (15%) | 88 | Strong | The three-result Introduction now maps cleanly onto Secs. IV A / IV C / IV F, and the new scope-first paragraph improves the frontier section's logic. Minor scope-chaining slip in the second so-what. |
| Writing Quality (15%) | 80 | Strong | The de-jargon and paragraph-breaking pass genuinely worked. Docked because the caption diet cut past the fat in two places (W1) and one exhaustiveness phrase overstates (W5). |
| **Weighted Average** | **84.6** | **Minor Revision** | The rubric maps 84.6 to "Accept". I recommend **Minor Revision** instead, deliberately: three statements now in print are factually incorrect (W1, W2, W3) and one headline illustration is untraceable to any table (W4). All four are sentence-level corrections requiring no new computation, so no re-review is needed — but they should not appear in the published version. |

### On the four required actions from the previous report
**R1 (visualizations)** — delivered, and Fig. 1 is methodologically the better of the two: the single-pair caveat, the benchmark-identical formulas, and the disclosed centre flip are all correct. Fig. 6 is honest about the detector's chance performance but overstates the exhaustiveness of its selection rule (W5) and does not show the measurements that justify its own description (W6). **R2 (de-jargon, break paragraphs, shrink captions, explicit so-whats)** — delivered; the cost is W1 and the Table VII clipping pointer, and the benefit is real. **R3 (neural boundary)** — delivered and correctly scoped, with the single-seed `resnet18` disclosure and the retrieval-strength calibration to tighten (W9). **R4 (promote the decoder admission)** — delivered, accurate, and verifiable (S3), with one symmetric gap on the density axis (W7). No response letter was filed this round; `git log` plus the round-8 section of `trimmed_material.md` — which itemises every moved clause, every removed connective, and the authors' own adversarial drift audit — was sufficient for me to verify the pass, and I would rather have that artifact than a conventional letter. A one-page mapping from the four required actions to their new locations would still help the editor.
