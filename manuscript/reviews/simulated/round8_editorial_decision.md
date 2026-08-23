# Editorial Decision

## Manuscript Information
- **Title**: Rule reconstruction from a single spacetime diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata
- **Manuscript ID**: ssl-ecas — branch `review-round8-gemini` (reviewed range `ca523a7`…`ccfc4ba`; merge base `65d5a81`)
- **Venue**: *Chaos: An Interdisciplinary Journal of Nonlinear Science* (AIP), REVTeX 4.2 `cha`, 18 pp
- **Decision Date**: 2026-08-23
- **Review Round**: Round 8 — re-review (verification mode) of a presentation-only revision
- **Prior decision**: Accept with Major Revisions, 4 required actions (`manuscript/reviews/review_gemini_21aug26.md`)

---

## Decision *

### Minor Revision — no further external review required

Verification of the two CRITICAL items (below) is to be performed by the handling editor on the revised source; no reviewer will be re-engaged.

**Binding constraint applied:** the Devil's Advocate reported two CRITICAL issues (C1, C2), both of which I confirmed as still present in the working tree at `ccfc4ba` (`main.tex` ll. 756–758, 800–802, 1376–1378; l. 1575). Under panel rules an Accept is therefore unavailable this round regardless of the rubric scores, four of which fall in the Accept band (EIC 86, Methodology 84.6, Domain 84.5, Perspective 83.7).

---

## Reviewer Summary

| Reviewer | Role / identity | Recommendation | Confidence | Weighted score |
|----------|-----------------|----------------|------------|----------------|
| EIC | Editor-in-Chief (journal fit, traceability, verification of the four required actions) | Minor Revision | 5 | 86 |
| Reviewer 1 | Methodology — statistician, ML-benchmark evaluation, calibration, pre-registration | Minor Revision | 5 | 84.6 |
| Reviewer 2 | Domain — cellular automata, damage spreading, CA identification, diagram conventions | Minor Revision | 5 | 84.5 |
| Reviewer 3 | Perspective — ML-for-science / simulation-based inference practitioner | Minor Revision | 4 | 83.7 |
| Devil's Advocate | Adversarial audit of the revision's own claims | *(no formal recommendation)* — 2 CRITICAL, 9 MAJOR, 10 MINOR; explicitly states the criticals are "two caption/appendix sentences rather than a claim change" | — | — |

---

## Version Reconciliation (read before acting on any reviewer line number)

The reviewers did not see the same file. EIC and Reviewer 2 reviewed `489ce7`/`489ce7`-era state; Reviewer 3 reviewed `489ce7` plus uncommitted edits; Reviewer 1 re-verified against `0b3cef9`; the Devil's Advocate saw commits through `2040c01` and flagged the mid-review churn itself (m21). I verified every disputed item against the current tree (`ccfc4ba`). Findings **already repaired** and requiring no author action:

| Finding | Raised by | Status at `ccfc4ba` | Evidence |
|---|---|---|---|
| Fig. 4 y-axis label clipped (`NEW-1`) | EIC | **Fixed** | `make_figures.py` l. 135 `bbox_inches="tight"`; MediaBox 380.31 × 265.35 pt |
| In-figure title clipped, "Range-2" terminology (`NEW-3`, R2 W1) | EIC, Domain | **Fixed** | no `set_title` on the landscape axes |
| Axis gloss "low = gliders" contradicting the text's refusal (R2 W1, R3 minor) | Domain, Perspective | **Fixed** | `make_figures.py` l. 130 now "low = sparse damage"; l. 126 carries the rationale comment |
| Fig. 1 caption "the four statistics" (`NEW-5`, R3 minor) | EIC, Perspective | **Fixed** | l. 261 "the three conditional statistics of *this single pair*" |
| Fig. 6 caption printing unattributed rate/fill (`NEW-4`, R1 draft, R3 minor) | EIC, Methodology, Perspective | **Fixed** | ll. 1543–1546 "…*twin-run* damage coordinates … not measurements of the seeded run drawn here" |
| Attention / graph architectures never named (EIC R3 minor, R3 W3-iii) | EIC, Perspective | **Fixed** | ll. 1133–1134 name attention-based sequence models and graph networks |
| Change-record anchor wrong (`NEW-6`) | EIC | **Fixed** | `trimmed_material.md` l. 163 now `65d5a81` |
| Sec. II C delta-method monolith; Intro budget-family sentence (EIC R2 sites 1–2) | EIC | **Fixed** | R1 verified the II C split at `0b3cef9`; ll. 155–166 are now four short sentences |

Everything else in this letter is open at `ccfc4ba` and was confirmed by me in-source.

---

## Consolidated Verification Checklist — Prior Required Actions R1–R4

EIC's matrix, adjusted by the other four reports and by my own check of `ccfc4ba`.

| # | Prior required action | EIC verdict | Adjusted verdict | Corroboration | Adjustment rationale | Residual work |
|---|---|---|---|---|---|---|
| **R1** | Add ≥2 figures showing spacetime diagrams, the twin-run protocol, and the damage-metric geometry | FULLY_ADDRESSED | **FULLY_ADDRESSED** (substance) — production-defective | All five: EIC ("exactly the requested triptych"), R1 S2 (formulas match `caspectra/eval/dynamics.py:125–127`), R2 S1 (square pixels, 1 = black, ±r cone, rule-30 ∂f/∂L asymmetry correct), R3 S2, DA O1 | No dissent on substance. Two independent legibility failures (DA M4/M5; R1 minors; R3 W4) and one pedagogical gap (R2 W4: the IC and flipped cell are invisible) are **new issues**, not non-compliance | P1-7, P2-3, P2-4 |
| **R2** | De-jargon; migrate plain-language clarity into the body; break monolithic paragraphs; caption diet with explicit so-whats | PARTIALLY_ADDRESSED (3 named sites) | **PARTIALLY_ADDRESSED** — 2 of 3 sites now closed, but the diet **overshot** | R1 (delivered; cost = W1), R3 (measured: paragraph median 147→128 words, max 465→279, longest caption 220→159), R2 S5 (App. D strengthened), DA M3 (no net shortening: body +89 words, 16→18 pp, captions 1,222→1,204), DA M10 (floats lost standalone readability) | Upgraded on EIC's own sites (II C and the Intro sentence are split at `ccfc4ba`); held at PARTIAL because the diet **created** C1 by deleting a true sentence, and because the change record calls the round "condensed" when the paper grew | P1-1, P1-8 |
| **R3** | Justify the CNN/ResNet neural boundary; discuss whether attention could bypass the shortcut | FULLY_ADDRESSED (attention unnamed — minor) | **FULLY_ADDRESSED** (substance) — **required precision fixes** | EIC, R1 ("a good answer to a fair challenge"), R2 ("the right one in outline"), R3 ("three of four moves I endorse"), DA (M11 concedes the conjecture is labelled) — but **four of five** demand sentence-level calibration: R2 W3, R3 W3, R1 W9, DA M11 | Both halves of the action are now present (attention/graph named at l. 1133). The four reviewers converge on *overstatement inside compliant text* — handled as a required new-issue fix, not as a failed action | P1-6 |
| **R4** | Move the missing-decoder admission into the results section where the noise frontier is presented | FULLY_ADDRESSED ("exceeds the letter") | **FULLY_ADDRESSED** | EIC, R1 S3 (coverage 0.5781/0.1344 verified against `frontier_grid_calibration/summary.json`), R2, R3 S5, DA O2 | Sole dissent is DA M7 — *placement*, not content: §IV E asserts the noise crossover one subsection **before** the scope paragraph. Arbitrated as a P2 one-clause addition, not a status change | P2-2 |

**Overall compliance**: 3 of 4 fully addressed and independently verified by ≥4 reviewers; R2 partial. Two new CRITICAL and nine MAJOR issues, all text-, caption-, or figure-production-level.

---

## Consensus Analysis *

### Points of Agreement (Consensus)

**[CONSENSUS-5]** (all five reviewers):

1. **The presentation-only contract was honored — no claim drift.** EIC ran an adversarial numeric diff against `65d5a81` ("every removed number relocated exactly where the change record says"); R1 re-ran `scripts/audit_manuscript_numbers.py` (0 failures), independently recomputed the ρ table (6.07/35.45/20.48/12.49 vs Table IV's 6.1/35/20/12) and the selected-checkpoint bands (0.458–0.639, 0.388–0.813); R2 diffed `main..HEAD` in full ("no registered number, verdict, margin, threshold, or disclosure changed"); R3 traced every relocated hedge; DA O4 ("the bodies of Tables I–IV and VI are byte-identical"). All five independently note that the drift-audit commit `489ce7` *restored* hedges the compression had dropped. **DA records this as "the single most creditable part of this round."**
2. **Fig. 1 (twin run) is the right figure and is drawn honestly.** EIC ("the pedagogical anchor the paper lacked"), R1 S2, R2 S1, R3 S2, DA O1. The rule-204 panel making the fill = 1 degeneracy *visible* is singled out by R2 (S2), R3 (S2) and DA (O1).
3. **The R4 admission is substantively exemplary** — quantitative, unhedged, placed before the numbers it bounds (EIC, R1 S3, R2, R3 S5, DA O2).
4. **The verdict is Minor Revision.** Four explicit recommendations plus DA's own characterization of its criticals as two sentences.

**[CONSENSUS-4]** (four reviewers; the fifth silent, not dissenting):

5. **The new neural-boundary paragraph overstates at sentence level** (R1 W9, R2 W3, R3 W3, DA M11; EIC silent — EIC reviewed before some of this text settled and flagged only the missing "attention"). Sub-points: "bracket that family from both ends" is unsupported (R2, R3, and R1's single-seed `resnet18` disclosure); "a synchronous CA update *is* a local convolution" claims an identity `gilpin2019` does not assert (R2); "sits level with the trained estimators" uses the *raw* five-statistic retrieval whose radius-two gap (0.059) exceeds the paper's own δ = 0.05 margin (R1); the directional conjecture that attention would *sharpen* recognition-over-estimation is mechanism-free (DA, R3).
6. **The Fig. 1 "extent" bracket — the annotation the caption points the reader to — is illegible at print size** (R1 minor, R2 minor, R3 W4, DA m16); three of the four independently prescribe moving it below the panel frame.

**[CONSENSUS-3]**:

7. **The ceiling statement in the frontier captions is wrong for half the plotted curves** (DA **C1**, R1 **W1**; R3 minor asks for in-panel ceiling lines, the structural version of the same fix). EIC and R2 silent. *Confirmed by me at `ccfc4ba`*: Fig. 2's caption (ll. 756–758) says "every curve is bounded by … median 0.963, *not* 1" while App. B (ll. 1371–1372) says "a direct estimator predicting the latent mean keeps the ICC ceiling (0.993)" — and App. B then contradicts itself at ll. 1376–1378 ("Every curve … must be read against these ceilings"). Both reviewers trace the deletion to this round's caption diet.
8. **The exemplar figure's exhaustiveness clause is an overclaim** (DA **C2**, R1 W5, R2 minors). *Confirmed at l. 1575*: "the only rules in the region for which a picture illustrates rather than overclaims", after the preceding sentence has declared the corroborating detector anti-informative (balanced accuracy 0.39). R1 supplies the denominator: 234 rules in the plotted region, but only a 300-rule subsample (231 applicable, 25 signature-meeting) was ever tested — an exhaustiveness claim over ≈11 % of the region. R2 and DA both surface the undisclosed fourth agreeing rule (345313848, excluded at rate 0.288 against the registered 0.28 window) that exists only in a code comment.
9. **The light-cone ceiling 1.008 is unattainable; the true maximum is 0.992 (r = 1)** (R1 W3 Major, R2 methodology note, DA O7). All three derive it from the same code path: `evolve(ic, n_steps)` applies the rule `n_steps − 1` times while the rate normalizes by `2rT`.
10. **The two new column-width figures are too small to do their job** (DA M4/M5 with computed final-size type: 8 pt → 5.0 pt, legend 7 pt → 4.5 pt; R1 minor; R3 minor). *Confirmed*: `signature_exemplars.pdf` is 388.8 pt wide and `landscape.pdf` 380.3 pt, both included at `\columnwidth` ≈ 246 pt.
11. **Fig. 1's unhedged class words ("chaotic", "complex") sit oddly in a paper that refuses class assignment** (R2, R3, DA m17).
12. **Figure reproducibility needs pinning** (R1 Q4: `caspectra` commit + RNG streams; R2 W1/Q4: script-vs-shipped divergence; DA: the undocumented 24-attempt seed-retry loop in the released figure code).
13. **A one-page R1–R4 mapping should accompany the revision** (R1 "would still help the editor"; DA "shifts the entire verification burden onto the referee"; EIC had to reconstruct compliance from `git log`).

**[CONSENSUS-2]**:

14. **The flagship calibration number is untraceable to its own table** (R1 W4, R3 W2): 0.979 (Sec. IV A, l. 494), 0.98 (Table IV caption, l. 1120-area; Intro l. 182) vs Table II's 0.960 ± 0.019, with no reconciling note and no `$^\ast$seed-0` marker on Table IV although Table I uses that convention.
15. **The abstract's opening premise reads as the negation of its own result** (R3 W1 Major, R2 precision note). The `2040c01` edit added the "Because they are defined by *twin* simulations" premise clause (l. 32–33), which is R2's suggested repair; R3's requested *resolving* clause is still absent.
16. **"Statistically indistinguishable from" invites a failed-test reading of an identity** (R1 W10, DA m14).
17. **Fig. 1 lands two–three pages after its first citation** (R2 layout, DA M6).
18. **Fig. 4's caption cross-reference is circular** (R2 minor, DA m13).

### Points of Disagreement

**Disagreement 1: Did R2 (de-jargon / density) actually happen?**
- **DA view (M3)**: No. 16 → 18 pp; main-text prose +89 words; Results −226 words of which −327 is relocation, so surviving Results prose *grew*; aggregate caption text 1,222 → 1,204 words with the longest caption now being the one added this round. "Nothing was cut; things were carried to the back of the book."
- **R3 view**: Yes, measurably — paragraph median 147 → 128 words, max 465 → 279, p90 264 → 209, longest caption 220 → 159, at essentially unchanged body length.
- **EIC view**: Materially clearer for the readership; 18 pp acceptable at *Chaos*; growth is "entirely the referee-required figures plus the appendix restructure, not new claims."
- **R1 view**: Delivered; the cost is W1.
- **Type**: Direction disagreement (both measurements are correct; they measure different things — DA measures volume, R3 measures density).
- **Editor's Resolution**: Both are upheld and neither is decisive. **Density improved; volume did not shrink.** I accept the page count on EIC's venue judgment and impose no deletions. I **reject** DA's specific deletion candidates — the ρ delta-method paragraph, §IV B, and Table I — because R1 names that same delta-method passage as "the kind of second-order honesty most benchmark papers omit entirely" and R3 calls the reliability apparatus "exemplary and rarely seen." Deleting content two reviewers cite as a strength to satisfy a page-count objection no venue rule imposes is the wrong trade. I **do** require the change record stop describing the round as condensation (P1-8).
- **Rationale**: Conservative principle — when one reviewer's remedy destroys another's named strength and no venue constraint forces the choice, the strength survives and the framing is corrected instead.

**Disagreement 2: Severity of the 1.008 → 0.992 rate ceiling**
- **R1 (W3, Major)**: Two printed sentences are false. Beyond the ceiling arithmetic, "the largest rate we observe anywhere is 0.816" (l. 285) is wrong: over the 88 ECA orbits the maximum is 0.9919 (rules 90 and 150, `cache/targets_1cab053a4c60559c.npz`), and **rule 150 is in the 18-rule held-out panel** behind Tables II and IV — i.e. a target saturating at its attainable maximum on the elementary panel, the opposite of "nothing in this paper sits near that boundary."
- **R2**: Agrees on the arithmetic (0.992 at r = 1, 0.975 at r = 2) but reports "nothing in the paper depends on it… the misstatement is conservative."
- **DA (O7)**: Explicitly filed as a non-defect and "out of scope for a presentation re-review."
- **Type**: Severity disagreement, with an embedded existence disagreement (R1 alone claims the 0.816 sentence is *false*, not merely incomplete; R2 and DA both repeat 0.816 as if correct).
- **Editor's Resolution**: **Required (P1-3)**, at R1's severity, subject to author verification of the 0.9919 figure. R1's claim is the most specific and the only one accompanied by an independent reproduction (a lone flip under rule 90 giving extent 123, rate 0.99194) and a named cache file; R2 and DA both assessed only the arithmetic, not the empirical maximum, so their "harmless" verdicts do not reach R1's finding. No re-analysis follows (targets and predictions share the normalizer), but a false factual sentence printed three times — Sec. II B l. 285, App. B l. 1394, and the Fig. 4 x-axis label (`make_figures.py` l. 128, still "light speed = 1.008 here" at `ccfc4ba`) — cannot go to press in a paper whose standing rests on arithmetic hygiene. **If the author's check contradicts R1, report the check; do not silently retain 0.816.**

**Disagreement 3: Keep or cut the exemplar figure (Fig. 6)?**
- **DA (C2)**: Offers "drop the figure and keep the honest statement that the region cannot yet be illustrated" as an acceptable resolution; also proposes replacing agreement-selection with a stratified random draw.
- **R3 (S3)**: The figure *raised* trust — "being handed a figure whose caption tells me why it is *not* representative raised my trust in the rest of the manuscript measurably."
- **R2 (S3)**: Checked specifically for gliderhood creep and "did not find it."
- **R1 (W5)**: Neither keep-nor-cut; supplies the precise replacement wording.
- **Type**: Direction disagreement.
- **Editor's Resolution**: **Keep the figure; fix the licensing clause.** Three reviewers judge the figure's disclosure discipline a strength; only its final clause is defective, and R1 has already written the repair ("three of the 25 signature rules the detector was ever run on"). Cutting the figure would also re-open R1-of-the-prior-round (the "show me the structures" mandate). DA's stratified-random alternative is recorded as a P3 option the authors may adopt instead.

**Disagreement 4: Is R4 complete?**
- **EIC / R1 / R2 / R3**: Fully addressed; EIC calls it "exemplary… exceeds the letter of the request."
- **DA (M7)**: Half-executed — the *first* noise verdict a reader meets is §IV E's "at 5 % bit-flip noise the mechanistic median R² falls below zero" plus Fig. 2's crossover claim, both one subsection ahead of the scope paragraph.
- **Type**: Existence disagreement about the scope of the original mandate ("readers should know *immediately*").
- **Editor's Resolution**: **R4 stands as FULLY_ADDRESSED**; DA's fix is adopted as **P2-2** (one clause in §IV E and in Fig. 2's caption). Four reviewers verified the content and its coverage numbers; DA itself frames M7 as "about placement, not content" (O2). The clause is nearly free and lands in the same caption C1 already requires editing.

**Disagreement 5: Does the retrieval result over- or under-state?**
- **R1 (W9)**: The Discussion **overstates** — "level with the trained estimators" is carried by the *bottleneck* pair (0.864 vs 0.880; 0.883 > 0.847), while the *raw* five-statistic retrieval trails by 0.059 on radius two, beyond the paper's own δ = 0.05 margin.
- **DA (m19)**: The Introduction **understates** — "much of the remaining score reproduced by a training-set lookup" versus §IV C, where retrieval is level with and on ECA exceeds the regression head.
- **Type**: Apparent direction disagreement; on inspection, not a conflict.
- **Editor's Resolution**: Both are correct about different sites and different comparisons (Discussion/raw vs Introduction/bottleneck). Required fix: **use the bottleneck pair for any "level with" claim at both sites, and state the raw-space gap explicitly where the raw numbers are invoked.** R1's suggested paired rule-bootstrap CI for (retrieval − CNN) is recorded as P2 (machinery already exists, folds already grouped by rule) and would settle both readings at once.

**Disagreement 6: Add a picture of a *result*?**
- **R3 ("the one presentation change I would make")**: Add a two-panel predicted-vs-true damage-survival scatter with the [0.1, 0.9] band shaded — no new computation, the predictions are already released.
- **DA (Ignored Alternative 4)**: The round's error was adding rather than cutting.
- **Editor's Resolution**: **P3, optional.** It is the single highest-leverage remaining change for the ML audience (R3's own dimension), and EIC's page-count judgment permits it — but a fifth figure is not a condition of acceptance in a round already carrying two CRITICAL text fixes.

---

## Decision Rationale *

Three of the four prior required actions are fully delivered and were independently verified by at least four reviewers each, against released artifacts rather than on trust: R1's figures (R2 checked the rule-30 ∂f/∂L asymmetry against theory; R1 checked the printed statistics against `caspectra/eval/dynamics.py`), R4's decoder admission (R1 reproduced coverage 0.5781/0.1344 from `frontier_grid_calibration/summary.json`), and R3's neural-boundary paragraph, whose missing "attention" clause EIC flagged and which is now present at ll. 1133–1134. R2 remains partial, though two of EIC's three named sites closed mid-review.

Most importantly, the round's one existential risk — a presentation pass that quietly moves a claim — did not materialize. Five reviewers tested for it by five different methods and all five cleared it; DA, whose brief is to find exactly that, records "no drift in any pre-registered quantity" and credits the authors' own adversarial audit (`489ce7`) for restoring twelve hedges the compression had dropped.

What blocks acceptance is narrow and concrete. DA's C1 and R1's W1 independently identify the same sentence — deleted by *this round's* caption diet — whose absence leaves Fig. 2's caption asserting one scoring ceiling (0.963) for curves scored against two (0.963 and 0.993), directly beneath a cross-family comparison the caption then makes. DA's C2 and R1's W5 identify an exhaustiveness clause ("the only rules in the region") licensed by agreement with an instrument the previous sentence declares anti-informative. Both are in print at `ccfc4ba`; both are single sentences. Alongside them, R1 and R3 converge on a headline number (0.98/0.979 vs Table II's 0.960 ± 0.019) that a reader will look up and fail to reconcile, and R1, R2 and DA converge on a light-cone ceiling stated three times and unattainable.

Minor rather than Major because nothing requires new computation, no registered claim is at risk, and no reviewer asks for re-analysis. Minor rather than Accept because the Devil's Advocate's criticals stand unrepaired and, by panel rule, foreclose acceptance — a rule that here coincides with editorial judgment: two false statements in figure captions are exactly the defect this manuscript's credibility can least afford.

---

## Required Revisions * (Must Fix)

| # | Revision item | Source | Severity | Location (`main.tex` @ `ccfc4ba`) | Effort |
|---|---|---|---|---|---|
| **P1-1** | Restore the two-ceiling statement to both frontier captions and repair App. B's self-contradiction | DA **C1**, R1 W1, DA M10, R3 minor | **Critical** | ll. 756–758; ll. 800–802; ll. 1371–1378; Table VII l. 1021 | 0.5 d |
| **P1-2** | Replace the exemplar exhaustiveness clause; disclose the tested denominator and the replicate-unstable fourth rule | DA **C2**, R1 W5, R2 minors | **Critical** | l. 1575 (App. D); `fig:exemplars` caption ll. 1535–1547 | 0.5 d |
| **P1-3** | Correct the light-cone rate ceiling to 0.992 (r = 1) / 0.975 (r = 2); correct or qualify "the largest rate we observe anywhere is 0.816" | R1 W3, R2, (DA O7 dissenting on severity) | Major | ll. 283–285; ll. 1393–1395; `make_figures.py` l. 128 (Fig. 4 x-label) | 0.5 d |
| **P1-4** | Reconcile 0.979 / 0.98 against Table II's 0.960 ± 0.019 at all three sites; add the `$^\ast$seed-0 checkpoint` marker to Table IV; add an audit check | R1 W4, R3 W2 | Major | l. 494; Table IV caption ll. 1113–1124; Intro ll. 182–185; `scripts/audit_manuscript_numbers.py` | 0.5 d |
| **P1-5** | Correct — or implement — Table IV's claim that zero-noise rules "drop out" of ρ | R1 W2 | Major | Table IV caption ll. 1121–1124 | 0.5 d |
| **P1-6** | Calibrate four claims in the neural-boundary paragraph to their measured strength | R2 W3, R3 W3, R1 W9, DA M11 | Major | ll. 1118–1141 | 0.5 d |
| **P1-7** | Figure production pass: regenerate the two column-width figures at final size; move the Fig. 1 extent bracket out of the damage field | DA M4/M5/m16, R1 minors, R3 W4, R2 minors, EIC NEW-2 | Major | `figures/{signature_exemplars,landscape}.pdf`; `make_figures.py` ll. 54, 205, 234 | 1 d |
| **P1-8** | Finish R2: trim the Fig. 3 caption to a pointer; correct the change record's "condensed" framing | EIC (R2 partial), DA M3, DA M10 | Major | Fig. 3 caption; `trimmed_material.md` round-8 header | 0.5 d |
| **P1-9** | Submission readiness: resolve `% TODO(user)` markers; recompile `main.pdf` against the regenerated figures; re-run the drift audit over everything committed after `489ce7` | EIC, DA (production, m21) | Major | ll. 19, 21, 1209, 1220, 1239 | user-gated |
| **P1-10** | Supply a one-page R1–R4 → location mapping with the revision | R1, DA, EIC | Major | new cover document | 0.25 d |

### Required Item Details

**P1-1: The frontier captions state one ceiling for curves that have two**
- **Problem**: Fig. 2's caption reads "the estimator simulates at n_pairs = 64, so **every curve** is bounded by the reduced-budget ceiling of Appendix B — median 0.963, *not* 1" (ll. 756–758), yet the same caption plots "the frozen CNN (blue)" and "the frozen CNN and the statistics" — direct estimators which App. B says explicitly "keep the ICC ceiling (0.993)" (ll. 1371–1372). Fig. 3's caption (ll. 800–802) inherits the ambiguity for the eight-estimator panel. App. B is itself now self-contradictory: ll. 1376–1378 close with "Every curve in Figs. 2 and 3 must be read against these ceilings, not against 1." The pre-round-8 captions carried the correct sentence; R1's numeric-token diff shows `0.993` lost exactly one occurrence in the diet.
- **Source**: DA C1 ("false for half the curves it plots — and the correct statement was deleted this round"); R1 W1 ("Fig. 2's own caption then makes a cross-family comparison … between two curves the caption has just told the reader share a ceiling"); DA M10; R3 minor.
- **Requirement**: Restore ~15 words to each caption — resimulating curves against 0.963/0.953, frozen CNN and five statistics against the 0.993 ICC ceiling — **and** repair the App. B closing sentence so it does not overrule its own preceding sentence. Preferred structural fix (R3, DA): draw both reference lines inside each panel in `build_identifiability_diagram.py` / `build_frontier_grid.py`.
- **Acceptance criteria**: No caption or appendix sentence attributes a single ceiling to both estimator families; the Fig. 2(b) crossover claim (ll. 761–762) names the ceiling applying to each of the two curves it compares.

**P1-2: The exemplar figure's licensing clause is refuted by the sentence before it**
- **Problem**: App. D, l. 1575: "…the three rules on which the two criteria nevertheless agree — **the only rules in the region for which a picture illustrates rather than overclaims**", immediately after "The localized-seed detector … performs at or below chance … and validates nothing either way."
- **Source**: DA C2 ("agreement with an instrument the paper has just declared anti-informative confers no evidential status… the selection is a filter on noise"); R1 W5 (234 rules in the region; detector run on a 300-rule subsample, 231 applicable, 25 signature-meeting, 54 positives, precision 0.053 — "the only rules" describes a search over ≈11 %); R2 minors.
- **Requirement**: (a) Replace the clause with R1's formulation or DA's neutral one — e.g. "three of the 25 signature rules inside the detector's 300-rule validation subsample, on which both criteria fire; at balanced accuracy 0.39 that agreement carries no validation weight". (b) Disclose the boundary case now living only in `make_figures.py` ll. 34–41: rule 345313848 fires the detector and meets the criterion in the validation replicate but sits at rate 0.288 against the registered 0.28 window in the plotted one — the criterion is replicate-sensitive at its rate edge. (c) Note that all three exemplars sit in the region's high-fill upper edge ((0.19, 0.54), (0.19, 0.58), (0.23, 0.58) within a region spanning ≈ rate 0.15–0.28, fill 0.31–0.62) and that the sparse-fill lower half is unillustrated; R2 suggests retitling to "Three signature-region rules on which two criteria agree", which discharges this and the representativeness reading at once.
- **Acceptance criteria**: No sentence in the manuscript claims exhaustiveness over the signature region; the selection rule's denominator and its replicate instability are both in print, not only in code comments.

**P1-3: The light-cone rate ceiling**
- **Problem**: `evolve(ic, n_steps)` returns `n_steps` rows with the rule applied `n_steps − 1` times, while `damage_spreading_features` normalizes by `2·max_speed·n_steps`. The attainable maximum is (2r(T−1)+1)/(2rT) = 0.992 at r = 1, T = 62 (and 0.975 at r = 2), not the 1.008 printed at ll. 283, 1394 and on the Fig. 4 x-axis. R1 further reports that "the largest rate we observe anywhere is 0.816" is the radius-two landscape maximum only: over the 88 ECA orbits the maximum is 0.9919 (rules 90 and 150), and **rule 150 is in the 18-rule held-out panel**, sitting at the attainable ceiling.
- **Source**: R1 W3 (with an independent reproduction: rule 90, lone flip, extent 123, rate 0.99194); R2 methodology note (same derivation, both radii); DA O7 (arithmetic agreed, severity disputed — see Disagreement 2).
- **Requirement**: State the row/update convention where the horizon is defined ("T rows, T − 1 updates"); correct the ceiling in Sec. II B and App. B (i); correct or scope the 0.816 sentence per the author's own verification; regenerate Fig. 4's x-axis label.
- **Acceptance criteria**: The ceiling is stated identically in Sec. II B, App. B and the figure; the sentence about how close the data sit to it is true for both the radius-two and the elementary panel, or is explicitly scoped to one of them.

**P1-4: The flagship calibration number does not match its own table**
- **Problem**: Sec. IV A l. 494 gives 0.979, Table IV's caption gives 0.98 with ρ = 20, and the Introduction's first so-what (ll. 182–185) gives 0.98 — while Table II's corresponding cell reads 0.960 ± 0.019, with no reconciling note. R1 traces 0.979 to the seed-0 selected checkpoint (`runs/analysis/round6_metrics_sel/summary.json`) and reports that Table IV is *entirely* a seed-0 artifact whose caption never says so, although Table I already carries the `$^\ast$seed-0 checkpoint` convention.
- **Source**: R1 W4; R3 W2 ("converts the paper's best rhetorical asset into a bookkeeping doubt").
- **Requirement**: One clause at each of the three sites (R3's wording: "reads 0.979 for the seed-0 checkpoint scored in Table IV — five-seed mean 0.960 ± 0.019, Table II"); add the seed-0 marker to Table IV; add a `Check` for the quoted value to `scripts/audit_manuscript_numbers.py` so the two aggregations cannot drift apart again. R1 additionally asks for five words in Sec. IV A noting the ECA rate panel's bimodality (two of eighteen rules above 0.9, thirteen below 0.02), or moving the Introduction illustration to the radius-two cell (R² 0.875, ρ = 10, 160 rules).
- **Acceptance criteria**: `audit_manuscript_numbers.py` exits 0 *with* a check covering the quoted 0.979/0.98; a reader following the Introduction's pointer reaches a number the manuscript reconciles.

**P1-5: ρ and the zero-noise rules**
- **Problem**: Table IV's caption states that rules with no Monte-Carlo noise "contribute zero to both sums and so drop out". In `scripts/analyze_round6_metrics.py:_rho`, `err2` sums over all rules while `var` sums over all rules, so a σ̂_e = 0 rule contributes a positive numerator against a zero denominator for any estimator with non-zero error there. R1's reproduction on ECA cone fill: five statistics 12.62 published → 4.84 with those rules excluded from both sums (85.3 % of the numerator); deep CNN 12.49 → 9.00 (48.2 %). Two further caption inaccuracies: the count is target-specific (ECA 3/2/2/**9** for survival/fraction/rate/fill; "3 of 18" is the survival column), and the affected rules are not "the fully ordered ones" — seven rules with survival 0.47–0.81 have σ̂_e = 0 on fill alone through the sparse-end degeneracy.
- **Source**: R1 W2 (single-reviewer, but reproduced from `held_out_preds_np256_mech.pkl` and `per_rule_sigma_e.npz`; R3 quotes the same caveat approvingly, i.e. as a reader who believed it).
- **Requirement**: Either implement the caption (mask those rules from both sums — changes only the two ECA cone-fill cells) or correct it with per-target counts and the ECA cone-fill numerator share. **Headline range 3–35 is unaffected either way** (ECA fraction 0.2 %, ECA rate 0.7 %, radius two ≤ 11 %). Answer R1's registration question: does the choice need an `EVALUATION_CRITERIA.md` note, given ρ was registered at rev. 13/14?
- **Acceptance criteria**: The caption describes the statistic as implemented, or the implementation matches the caption; no verdict changes, and the change is logged.

**P1-6: Calibrate the neural-boundary paragraph**
- **Problem** (four convergent findings on ll. 1118–1141): (a) "A synchronous CA update *is* a local convolution" claims an identity `gilpin2019` does not assert — it is a convolution *composed with a pointwise nonlinearity or lookup* (R2). (b) "the constrained network and the 354× larger unconstrained one bracket that family from both ends" — R2: the member closest to the mechanism is missing by design (a first layer spanning the (2r+1)-cell neighbourhood *and* its output cell, the architecture `rollier2024cnn` used to reach 99.9 %; the paper's 2 × 2 kernels are chosen specifically so it cannot tabulate); R3: "both endpoints are convnets, same objective, same 60-epoch budget, no architecture search, ResNet18 a single seed — that samples a capacity axis, it does not bracket a family"; R1: add "(single seed)". (c) "a nearest-neighbour lookup in the raw five-statistic space already sits level with the trained estimators" — the "level with" verdict is carried by the bottleneck pair (0.864 vs 0.880; 0.883 > 0.847); the raw radius-two gap is 0.059, beyond the paper's own δ = 0.05 margin (R1 W9). (d) "the probes show the rule information is accessible there" does not distinguish the identity probe (0.87/0.95, shared rule classes) from the out-of-rule table-bit probe (0.79 ECA / **0.61** radius two against chance 0.5), and the out-of-rule probe is the regime the benchmark scores (R3). (e) The conjecture that a global receptive field would make recognition *sharpen* rather than be bypassed is mechanism-free and is the first sentence an ML referee will contest (DA M11, R3, R1).
- **Requirement**: R3's three sentence-level edits, plus R2's named-omission substitution for the bracket clause, plus R1's and R3's conversion of the conjecture into a testable prescription — "the diagnostic that would decide the question for any of them is the one we report for this family (bottleneck retrieval versus the regression head), not a higher R²". No new experiments, no claim change.
- **Acceptance criteria**: Every clause in the paragraph is either a measured number with its scope, a cited claim stated as the cited work states it, or an explicitly named untested gap; the paragraph contains no directional prediction unaccompanied by the experiment that would test it.

**P1-7: Figure production pass**
- **Problem**: `signature_exemplars.pdf` (388.8 × 237.6 pt) and `landscape.pdf` (380.3 × 265.4 pt) are both included at `\columnwidth` ≈ 246 pt, i.e. downscaled 0.63× and 0.65×: 8 pt panel titles print at ≈5.0 pt, the landscape legend at ≈4.5 pt, exemplar labels a/b/c at ≈5.2 pt (DA M4/M5, with EIC NEW-2 reporting that "c" occludes the rule-110 star label). DA: "the three diagrams read as grey hatching; no individual structure is resolvable — exactly the demand the figure exists to meet." Separately, Fig. 1's "extent" annotation is 6 pt white-on-stroke drawn inside the brightest damage speckle (`make_figures.py` l. 205) and is unreadable at 1:1 (R1, R2, R3 W4, DA m16).
- **Requirement**: Promote `signature_exemplars` to `figure*` or regenerate at column width with ≥8 pt final-size type and cropping to the active cone; regenerate `landscape` at `figsize ≈ (3.4, 2.6)` so no downscaling occurs, with leader lines for a/b/c out of the dense region and matched label sizes; move Fig. 1's bracket and label below the panel frame, anchored on the final row, in the crimson of the flip marker at ≥7 pt.
- **Acceptance criteria**: No type below 8 pt at final printed size in any figure; the a/b/c markers do not occlude the ECA star labels; `main.pdf` recompiled against the regenerated PDFs.

**P1-8: Complete R2 and correct the change-record framing**
- **Requirement**: Trim the Fig. 3 caption (EIC: "still ~130 words … it could point rather than restate", subject to P1-1 restoring the ceiling clause — point, do not restate the disclosure text). In `trimmed_material.md`, state plainly that the manuscript grew from 16 to 18 pp because of the two referee-mandated figures and the appendix restructure, rather than describing the round as condensation (DA M3).
- **Acceptance criteria**: The change record's description of the round matches DA's word counts; no float's mandated disclosure is lost in the trim (re-run the `489ce7`-style drift audit afterwards, per P1-9).

**P1-9 / P1-10** are administrative: `% TODO(user)` markers at ll. 19, 21, 1209, 1220, 1239 (ORCIDs, corresponding address, funding, archive DOI, CRediT — user-gated per project policy); a clean recompile with the float-stuck warnings R2 reports resolved; a re-run of the round-8 drift audit over `0b3cef9`, `2040c01`, `ccfc4ba` and the revision commits (DA m21, which documents defects repaired mid-review without a change-record entry); and a one-page R1–R4 → location mapping to accompany the resubmission, since three reviewers note that compliance this round was verifiable only from `git log`.

---

## Suggested Revisions (Should Fix)

| # | Revision item | Source | Priority | Location |
|---|---|---|---|---|
| S1 | Abstract: add the clause resolving "not a function of any single observed diagram" against the identification result; name the reference value (√2); gloss "orbits"; change "statistically indistinguishable from" → "identical in distribution to"; bring 281 words toward the ~250 AIP norm | R3 W1, R2, R1 W10, DA m14 | P2 | ll. 31–60 |
| S2 | One clause in §IV E and Fig. 2's caption noting that the mechanistic estimator in the noise regime is the entrywise pseudo-posterior, not the unbuilt latent-diagram decoder | DA M7 | P2 | §IV E; Fig. 2 caption |
| S3 | Fig. 1: label the time extent (T = 62 to the damage horizon vs the 127-row observed diagram); share one initial row across all four columns; make the IC and flipped cell visible (inset or 1-pt box); hedge the class parentheticals; state the greyscale-polarity switch; unify cone styling with Fig. 6; trim the caption toward ~85 words | R1 minors, R2 W4/W5 + minors, R3 W5, DA m15/m17/M8 | P2 | ll. 253–271; `make_figures.py` ll. 153–217 |
| S4 | Fig. 6: name both protocols with numbers (ring 255, quiescent background, 62 steps vs ring 127, Bernoulli(1/2), T = 30); print alive/growth/fill; state "sub-ballistic = growth ≤ 0.9 (App. E)"; note the drawn run is one of 24 seeds the detector medians over | R2 W2, R1 W6 | P2 | ll. 1535–1547 |
| S5 | Quote the ECA survival-band intervals inline (boosted −0.871 [−2.338, −0.118]; CNN −1.045 [−4.088, +0.553], n = 14) and attribute the "worse than the band mean" reading to the boosted baseline | R1 W8 | P2 | ll. 496–503 |
| S6 | One clause scoping interval calibration to the masking and noise axes; mirror it in Table VII's density row; soften "completed here" in App. A | R1 W7 | P2 | ll. 817–826; Table VII; App. A l. 1288 |
| S7 | Add a paired rule-bootstrap CI for (retrieval − CNN) per panel | R1 W9 | P2 | §IV C |
| S8 | Replace App. A's internal revision ordinals ("rev.-13 measurements answering the fourth review") with registration dates or a single "registered before measurement" tag | DA M9 | P2 | `app:repro` |
| S9 | Move Fig. 1's float so it lands at or before its first citation; clear the "float is stuck" warnings | R2 layout, DA M6 | P2 | float placement |
| S10 | Data availability: pin the `caspectra` commit and the RNG streams for Figs. 1 and 6; document the 24-attempt seed-retry loop as a selection mechanism | R1 Q4, R2 Q4, DA | P2 | ll. 1209–1220; `make_figures.py` |
| S11 | Disambiguate the two "(i)–(iv)" enumerations by naming them at cross-reference sites | R3 | P2 | §III, §IV F |
| S12 | Sec. II B: give the elementary fill = 1 rate (24 of 88 orbits; 7 in the held-out panel) beside the 0.13 % radius-two figure | R1 minor | P2 | l. 289 |
| S13 | Intro so-whats: add "across the four targets" scope marker; "a training-set lookup matches it"; "is the part that might transfer" | R1, DA m19/m20 | P2 | ll. 182–209 |
| S14 | Table VII: restore the four-word pointer to the bootstrap clipping convention; soften "echoed in Table VII" at l. 944 | R1 minors | P2 | Table VII; l. 944 |
| S15 | Sec. IV F(iv): inline "(final-epoch; selected-checkpoint 0.876, Sec. IV A)" at the 0.859 comparison | EIC NEW-7 | P3 | l. 949 |
| S16 | Fig. 4 caption: "Prevalence: Sec. IV I; ECA validation: below" (currently circular) | R2 minor, DA m13 | P3 | Fig. 4 caption |
| S17 | Restore "vertical" to Fig. 2's "dotted line"; fix the "that increment" antecedent; "eight posterior tables per diagram" | DA m12, R1 minor, R2 minor | P3 | Fig. 2 caption; ll. 671–676; §IV F(i) |
| S18 | Add a two-panel predicted-vs-true damage-survival scatter with the [0.1, 0.9] band shaded and ρ annotated | R3 ("the one presentation change I would make") | P3 | §IV A |
| S19 | Promote the two portable diagnostics to a named, numbered recipe; give the retrieval baseline its own paragraph heading; add a "how to read the tables" box; consider a ρ portable-definition callout | R3, DA (Ignored Alternative 5) | P3 | §V, §IV C |
| S20 | Cite a published source for the left/right damage velocities Fig. 1 now displays for rule 30 | R2 | P3 | Fig. 1 caption or §II B |
| S21 | Colour-vision and greyscale robustness (crimson vs steelblue as the sole categorical cue in Fig. 4; colour-only pairing across eight curves in Fig. 3); Table VI reference column to point at the released grid artifact | DA, R3 | P3 | Figs. 3–4; Table VI |
| S22 | Consider a radius-two column in Fig. 1, or a corruption-axis illustration (clean vs 5 % noise vs 40 % masking with the recovered table's error highlighted) | DA (Ignored Alternatives 1–2) | P3 | §II B / §IV F |

---

## Revision Roadmap *

### Priority 1 — Required before acceptance (est. 4–5 days)
- [ ] **P1-1** Two-ceiling restoration in Fig. 2 and Fig. 3 captions + App. B closing sentence (`main.tex` ll. 756–758, 800–802, 1371–1378); preferred: in-panel reference lines — **CRITICAL, DA C1 / R1 W1**
- [ ] **P1-2** Exemplar exhaustiveness clause + subsample denominator + fourth-rule boundary case + high-fill-edge note (l. 1575; caption ll. 1535–1547) — **CRITICAL, DA C2 / R1 W5**
- [ ] **P1-3** Rate ceiling 1.008 → 0.992/0.975 and the 0.816 sentence (ll. 283–285, 1393–1395, `make_figures.py` l. 128) — R1 W3 / R2
- [ ] **P1-4** 0.979 vs 0.960 ± 0.019 at three sites + Table IV seed-0 marker + audit check (l. 494; Table IV caption; ll. 182–185) — R1 W4 / R3 W2
- [ ] **P1-5** Table IV ρ zero-noise caption: correct or implement — R1 W2
- [ ] **P1-6** Neural-boundary paragraph, five calibrations (ll. 1118–1141) — R2 W3 / R3 W3 / R1 W9 / DA M11
- [ ] **P1-7** Figure production: regenerate `signature_exemplars.pdf` and `landscape.pdf` at final size; relocate Fig. 1's extent bracket — DA M4/M5/m16 + 3 others
- [ ] **P1-8** Fig. 3 caption trim; correct the change record's "condensed" framing — EIC / DA M3
- [ ] **P1-9** TODO markers, clean recompile, drift audit over post-`489ce7` commits — EIC / DA m21 *(user-gated items excepted)*
- [ ] **P1-10** One-page R1–R4 → location mapping — R1 / DA / EIC

### Priority 2 — Strongly suggested (est. 2–3 days)
- [ ] S1 Abstract: resolving clause, √2, "orbits", "identical in distribution to", length
- [ ] S2 §IV E scope clause (completes R4's reach per DA M7)
- [ ] S3 Fig. 1 package: horizon label, shared IC, visible flip, hedged class words, polarity, cone styling, caption trim
- [ ] S4 Fig. 6 protocol disclosure and measured localized-seed values
- [ ] S5–S7 Survival-band intervals; density-axis calibration clause; paired retrieval bootstrap CI
- [ ] S8–S12 App. A register; float placement; figure provenance pinning; enumeration collision; ECA fill = 1 rate
- [ ] S13–S14 Intro so-what wording; Table VII pointers

### Priority 3 — Polish and optional (est. 1–2 days)
- [ ] S15–S17 Cross-section number note; Fig. 4 caption cross-reference; "vertical dotted"; antecedent; "eight posterior tables"
- [ ] S18 Optional new results figure (predicted vs true survival) — R3's highest-leverage suggestion, explicitly not required
- [ ] S19 Portable-diagnostics recipe; retrieval paragraph heading; "how to read the tables" box
- [ ] S20–S22 Rule-30 velocity citation; accessibility of colour encodings; radius-two or corruption-axis illustration

### Total Estimated Effort
**Minor Revision: 7–10 working days**, of which the two CRITICAL items are ~1 day. No new computation is required by any P1 item; P1-5 offers an implementation option that would change exactly two published cells (ECA cone fill: 13 → 4.8, 12 → 9.0) with no verdict movement.

---

## Explicit Consensus / Disputed Register

**Consensus (2+ reviewers) — act on all:**

| Point | Reviewers | Status |
|---|---|---|
| No claim drift; presentation-only contract honored | EIC, R1, R2, R3, DA (5) | Verified — no action |
| Fig. 1 delivers R1 and is methodologically honest | EIC, R1, R2, R3, DA (5) | Verified — no action |
| R4 admission substantively exemplary | EIC, R1, R2, R3, DA (5) | Verified — S2 only |
| Neural-boundary paragraph overstates at sentence level | R1, R2, R3, DA (4) | **P1-6** |
| Fig. 1 extent bracket illegible | R1, R2, R3, DA (4) | **P1-7** |
| Frontier captions state one ceiling for two families | R1, R3, DA (3) | **P1-1 (CRITICAL)** |
| Exemplar exhaustiveness overclaim / undisclosed selection | R1, R2, DA (3) | **P1-2 (CRITICAL)** |
| Light-cone ceiling 1.008 is wrong | R1, R2, DA (3) | **P1-3** |
| Column-width figures illegible at final size | R1, R3, DA (3) | **P1-7** |
| Fig. 1 class words unhedged | R2, R3, DA (3) | S3 |
| Figure provenance / reproducibility pinning | R1, R2, DA (3) | S10 |
| One-page R1–R4 mapping wanted | EIC, R1, DA (3) | **P1-10** |
| 0.979/0.98 vs Table II 0.960 ± 0.019 | R1, R3 (2) | **P1-4** |
| Abstract premise reads as negation of the result | R2, R3 (2) | S1 |
| "Statistically indistinguishable" gloss | R1, DA (2) | S1 |
| Fig. 1 float placement | R2, DA (2) | S9 |
| Fig. 4 caption circular cross-reference | R2, DA (2) | S16 |

**Single-reviewer (adopted on evidence, not on count):**
- ρ zero-noise caption (R1 W2) — **adopted as P1-5**: sole source, but accompanied by a reproduction from named artifacts, and R3's report shows a reader taking the caption at face value.
- Survival-band CIs (R1 W8), density-axis calibration (R1 W7), retrieval CI (R1 W9) — P2.
- App. A revision ordinals (DA M9), §IV E placement clause (DA M7) — P2.
- Fig. 1 per-column ICs (R2 W5), Fig. 6 measured values (R1 W6) — P2/S3–S4.
- New results figure (R3), portable-diagnostics recipe (R3), radius-two column (DA) — P3, optional.

**Disputed and arbitrated** (full reasoning above): D1 R2 status / page growth — *density improved, volume did not; no deletions imposed*. D2 rate-ceiling severity — *required, at R1's severity, subject to author verification*. D3 keep or cut the exemplar figure — *keep, fix the clause*. D4 R4 completeness — *fully addressed; DA's clause adopted as P2*. D5 retrieval over- vs under-statement — *not a conflict; use the bottleneck pair at both sites*. D6 add a results figure — *optional*.

---

## Revision Deadline

- **Recommended deadline**: 2026-09-20 (4 weeks)
- **Basis**: Minor Revision, 2–4 weeks; the upper bound is used because P1-7 requires figure regeneration and a clean recompile, and because P1-9 contains user-gated administrative items (ORCIDs, funding, archive DOI) outside the authors' drafting control.
- **Extension policy**: notify the handling editor one week before the deadline.

---

## Response Letter Instructions

A point-by-point response is **required** this round. Three reviewers (R1, DA, EIC) independently note that round-8 compliance was verifiable only from the repository — DA lists "the referee being answered" as a missing stakeholder, since a real referee "cannot read `git log`". `manuscript/trimmed_material.md` is an excellent artifact (R1: "a better artifact than most response letters I receive") and should be retained, but it does not substitute for a mapping the reviewers can read.

**Must include:**
1. A response to every P1 item, with the new line/section location of each fix.
2. A response to every P2 item — adopted, or the reason for not adopting.
3. Explicit answers to the four author questions carried forward: R1 Q1 (ρ's intended treatment of σ̂_e = 0 rules, and whether an `EVALUATION_CRITERIA.md` note is required given registration at rev. 13/14); R1 Q2 / R2 Q2 (the row-vs-update horizon convention and every statement it touches); R1 Q3 / R2 Q1 (exemplar denominators and the second protocol's parameters); R3 Q4 (whether the out-of-rule table-bit probe at 0.61 supports the "capacity is unlikely to be what binds" clause).
4. The one-page R1–R4 → location mapping (P1-10), and a re-run of the `489ce7`-style drift audit covering everything committed after it.
5. Change markup in the revised manuscript.

---

## Closing

We invite you to submit a revised version addressing the points above. The panel is unanimous that the scientific content of this manuscript is ready: five independent checks, including an adversarial one, confirm that a substantial presentation rewrite moved no registered number, verdict, margin or disclosure, and the authors' own drift audit *restored* hedges their compression pass had dropped — a discipline the Devil's Advocate calls "the single most creditable part of this round". Figure 1 does what three rounds of prose could not, and the promotion of the missing-decoder admission to the head of Section IV F exceeds what was asked.

What stands between this manuscript and acceptance is two sentences that say things the paper's own appendices contradict, one arithmetic ceiling stated three times and unattainable, one headline number that does not match its own table, and a set of figures that need to be regenerated at the size they will be printed. None of it requires new computation. We look forward to receiving your revision by 2026-09-20; no further external review is planned.

---

## Appendix: Full Reviewer Reports

All five reports (EIC verification review; Reviewer 1 — Methodology; Reviewer 2 — Domain; Reviewer 3 — Perspective; Devil's Advocate) are transmitted to the authors in full and unedited, and are the authoritative source for every item above.