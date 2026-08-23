# Devil's Advocate Report — Round-8 Re-Review

**Manuscript:** Rollier & Baetens, "Rule reconstruction from a single spacetime diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata"
**Reviewed artifact:** `/Users/michielrollier/Developer/GitHub/ssl-ecas/manuscript/main.tex` on `review-round8-gemini` (working tree as of 2026-08-23 14:0x; commits `main..HEAD` = `ca523a7`…`2040c01`), compiled `main.pdf` (18 pp) and `manuscript/figures/{twin_run,signature_exemplars,landscape}.pdf`.
**Prior report answered:** `reviews/review_gemini_21aug26.md` (Accept with Major Revisions; R1 figures, R2 de-jargon/paragraphs/captions/so-what, R3 neural boundary, R4 promote missing-decoder admission).

---

## 1. Strongest Counter-Argument (against "this revision fixes the presentation complaints")

The revision answers R1–R4 by **addition**, and the prior report's core complaint was about **density**. Measured on the source: the pre-round-8 manuscript compiles to 16 pages, this one to 18. Main-text prose excluding floats went from 8,106 to 8,195 words (+89). The Results section — the one commit `9f07c6e` calls "condensed" — fell 4,170 → 3,944 words, but 327 of those words merely relocated (a 524-word cost/by-products block became a 197-word pointer plus a 332-word Appendix F; 529 words preserved, five gained). Net of the move, the surviving Results prose *grew* by roughly 100 words; the Introduction grew 120, the Discussion 176, the abstract 263 → 281. Nothing was cut; things were carried to the back of the book and new things were written in front.

The caption diet has the same shape. Five existing captions lost 307 words; two new captions immediately spent 289. Aggregate caption text: 1,222 → 1,204 words. The longest caption in the paper is now Fig. 1's — the one added this round to satisfy R1.

Worse, the diet was not cost-free. Fig. 2's caption now asserts that "every curve is bounded by the reduced-budget ceiling … median 0.963", which is false for the frozen-CNN and five-statistic curves the same caption names; the sentence that used to say so correctly was deleted. And the R1 request to "visualize the actual gliders or structures in that 7.8% region" is answered on page 16 of 18, at 5-point type, by three rules selected through a detector the paper says "validates nothing either way".

*(≈290 words)*

---

## 2. Issue List

### CRITICAL

**C1. Fig. 2 caption states a single ceiling that is false for half the curves it plots — and the correct statement was deleted this round.**
*Location:* `\caption{Identifiability of the local rule…}` for `fig:ident` (main.tex ≈ ll. 754–758): "the estimator simulates at $n_{\mathrm{pairs}}=64$, so **every curve is bounded by** the reduced-budget ceiling of Appendix B---median $0.963$, *not* $1$."
*Why wrong:* the same caption plots "the frozen CNN (blue)" (panel b) and "the frozen CNN and the statistics" (panel d). Appendix B, *Reduced-budget scoring ceilings*, says explicitly: "a direct estimator predicting the latent mean **keeps the ICC ceiling (0.993)**." So the two families in these panels are scored against ceilings 0.963 and 0.993, and the caption now tells the reader they share one. The pre-round-8 caption carried exactly the missing sentence ("A direct estimator predicting the latent mean keeps the ICC ceiling (0.993)"); the caption diet removed it. Fig. 3's caption ("curves must be read against the reduced-budget ceilings … median 0.953") inherits the same ambiguity for the eight-estimator panel. A previous referee (Opus-5, 20 Aug) had asked for the opposite move: "**Draw the panel-specific benchmark as a horizontal reference on every frontier figure**."
*Fix:* restore one sentence to both captions — "read-then-simulate curves against 0.963/0.953; the frozen CNN and statistics against the 0.993 ICC ceiling" — or, better, draw the two reference lines in `build_identifiability_diagram.py` / `build_frontier_grid.py`.

**C2. The exemplar figure's licensing sentence is refuted by the sentence before it.**
*Location:* Appendix D final sentence (≈ ll. 1572–1576) and the `fig:exemplars` caption.
Appendix D: "The localized-seed detector … performs at or below chance on radius two (balanced accuracy 0.39) **and validates nothing either way**. Figure 6 shows the three rules on which the two criteria nevertheless agree---**the only rules in the region for which a picture illustrates rather than overclaims**."
*Why wrong:* agreement with an instrument the paper has just declared anti-informative (bal. acc. 0.39, precision 0.05 over 231 applicable rules, App. E) confers no evidential status on the three rules it happens to co-flag; the selection is a filter on noise, and calling the survivors "the only rules … for which a picture illustrates rather than overclaims" is precisely the overclaim it disavows. Two aggravating facts: (i) Fig. 4 shows exemplars *a–c* clustered in one corner (rate 0.19–0.23, fill 0.54–0.58) of a region spanning roughly rate 0.15–0.28 and fill 0.30–0.62, so they are not even descriptively representative — the sparse-fill lower half of the region is unillustrated; (ii) `make_figures.py` ll. 34–41 records a fourth agreeing rule (345313848) dropped because it "sits at rate 0.288 in the S4 replicate — just outside the registered 0.28 window", i.e. the registered criterion's membership is replicate-unstable at the boundary — a fact that exists only in a code comment. This is a *new* evidential claim in a revision whose own record (`trimmed_material.md`) says "no change to any registered number, verdict, margin, or disclosure".
*Fix:* replace the licensing clause with a neutral one — "three rules drawn to span the region's fill range; the localized-seed detector also fires on them, but at balanced accuracy 0.39 that agreement carries no validation weight" — and add one sentence disclosing the boundary instability. Or drop the figure and keep the honest statement that the region cannot yet be illustrated.

### MAJOR

**M3. "Shorten the main text" did not happen; the paper grew by two pages.**
*Location:* whole manuscript; commit `9f07c6e` ("results condensed"), `sec:constructive`, `app:secondary`.
Evidence as in §1 above (16 → 18 pp; main body +89 words; abstract +18 words; Results −226 of which −327 is relocation). The move is defensible on its own terms — a previous referee (DeepSeek, 20 Aug, §"If kept, they should be in an Appendix") asked for it — but it should not be presented as condensation.
*Fix:* either state plainly that the paper grew and why (two referee-mandated figures), or make real deletions. Concrete candidates, all self-identified as redundant by the paper: the ρ delta-method paragraph (§II C, ~180 words, whose conclusion is one clause of Table III's caption); §IV B ("no stable ordering"), whose verdict is one sentence; Table I, which the paper's own caption says must never be read alone.

**M4. Fig. 5 cannot show what it was added to show.**
*Location:* `fig:exemplars`, included at `\columnwidth` from a 388.8 × 237.6 pt canvas saved without `bbox_inches`.
At final size each panel prints ≈1.75 × 0.45 in for a 255 × 62 cell array (≈145 cells/inch), and the panel titles are 8 pt in a 5.4 in canvas scaled by 0.63 → **5.0 pt**. In the compiled p. 16 the three diagrams read as grey hatching; no individual structure is resolvable, which is exactly the demand ("visualize the actual gliders or structures") the figure exists to meet.
*Fix:* promote to `figure*`, crop to the active cone (the left half of panel (b) is empty background), give each panel ≥1.5 in of height, save with `bbox_inches="tight"`, and set fonts so that final-size type is ≥8 pt.

**M5. Fig. 4's new annotations are illegible and collide.**
*Location:* `fig:landscape`; `make_figures.py` ll. 109–125.
Scaled 380.3 pt → 246 pt (0.647): legend 7 pt → 4.5 pt, exemplar labels *a/b/c* 8 pt → 5.2 pt, tick labels → 6.5 pt. The three open circles overlap one another and the gold "110" star, and their italic labels sit on top of red points; on the compiled page the a/b/c labels are indistinguishable.
*Fix:* regenerate at `figsize≈(3.4, 2.6)` so no downscaling occurs, use leader lines out of the dense region, and raise all font sizes to ≥8 pt at final size.

**M6. Fig. 1 is cited two pages before it prints.**
*Location:* cited in §I (p. 2, "measure how the difference grows (Fig. 1)") and §II B (p. 3, "compare final rows (Fig. 1)"); printed on p. 4 as a `figure*[t]`.
A pedagogy figure that arrives after the definitions it illustrates does not do pedagogy.
*Fix:* make it a single-column `figure` anchored in §II B, or hoist the float declaration into §I so it lands on p. 2–3.

**M7. R4 is half-executed: the first noise verdict a reader meets is still unqualified.**
*Location:* §IV E, "Three regimes emerge…": "at 5% bit-flip noise the mechanistic median $R^2$ falls below zero while the frozen CNN retains 0.09–0.43"; Fig. 2 caption (b): "the mechanistic estimate (green) falls below the frozen CNN (blue) beyond ~2–5%."
The referee asked that readers "know **immediately**" the mechanistic baseline is handicapped in the noise regime. The new scope paragraph sits at the head of §IV F — one subsection *after* the noise crossover is first shown and asserted.
*Fix:* one clause in §IV E ("…the mechanistic estimate here is the entrywise pseudo-posterior/deterministic inverter, not the correctly specified latent-diagram decoder, which we did not build; see §IV F") and the same in Fig. 2's caption.

**M8. Cross-figure number collision for rule 110, with no reconciling note.**
*Location:* Fig. 1 prints "fraction 0.15 rate 0.28 fill 0.54" for rule 110 (ECA horizon $T=62$); Fig. 4 plots the "110" star at (0.214, 0.569) (embedded-ECA anchor at the radius-two horizon $T=30$).
A reader who compares the two figures sees the same rule at two different coordinates. This is the concrete realization of the risk the Fig. 1 caption tries to manage: the printed single-pair numbers *are* close enough to real benchmark numbers to be mistaken for them.
*Fix:* state the horizon in Fig. 1's caption ("ring 127, $T=62$ steps"), and add to Fig. 4's caption that the embedded-ECA anchors are computed at the radius-two horizon $T=30$ (the mechanism is already explained in App. D's body).

**M9. Appendix A still reads as a response letter — untouched by the de-jargon pass.**
*Location:* `app:repro`: "the **rev.-13 measurements M9--M12 answering the fourth review**", "the seven **rev.-11 review-response analyses**", "(rev. 9)", "(rev. 10)", "(rev. 12)", "[rev. 11]", "the rev.-14 matched-regime … run (M13)".
R2 asked for a register a wider audience can read; this is the least readable page in the paper, and a prior referee already flagged it verbatim (DeepSeek, 20 Aug: "Phrases like 'rev. 8,' 'rev. 9,' … belong in a response letter, not a journal manuscript"). The round-8 diff touches Appendix A only to reword one tolerance sentence.
*Fix:* replace internal revision ordinals with registration dates or a single "registered before measurement" tag per item, and delete "answering the fourth review".

**M10. The caption diet cost three floats their standalone readability, which an earlier Chaos referee explicitly required.**
*Location:* Table I caption ("Reliability columns are recomputed within each panel (**convention (7), Appendix B**)"), Fig. 2 and Fig. 3 captions (per-target reduced-budget ceilings now "Appendix B"), Fig. 4 caption ("quantified in the text below").
The first Chaos report states: "the paper does not provide sufficient captions or methods for Figures 1–2 to stand independently." The revision moved in the opposite direction: the per-target ceilings (survival 0.918, cone fill 0.871) that determine how far each frontier curve *can* rise now require a page flip.
*Fix:* restore one sentence per float; buy the space back from the deletions proposed in M3.

**M11. A new, unmeasured directional conjecture about untested architectures was added.**
*Location:* §V neural-boundary paragraph (≈ ll. 1132–1140): "a global receptive field makes matching a diagram to a familiar generator easier rather than harder, so **we would expect the substitution of recognition for estimation to sharpen, not to be bypassed**."
R3 asked whether attention might bypass the observed shortcut; the answer given is a mechanism-free prediction that it would not, resting only on this paper's CNN diagnostics. It is labelled a conjecture — but it is a claim added in a revision recorded as adding none, and it is the first sentence an ML referee will contest (permutation-equivariant/attention models are the standard argument *for* compositional generalization). Note: this is an *addition*, not an alteration of a pre-registered claim; I found no pre-registered number, margin, or verdict changed by round 8 (see Observation O4).
*Fix:* replace the prediction with what is defensible — the two diagnostics (intermediate-band stratification, bottleneck retrieval) are backbone-agnostic and can be re-run on any architecture — and name the one experiment that would settle it.

### MINOR

**m12.** Fig. 2 caption uses "dotted" for two different objects: "(b) … exact reconstruction (**dotted**)" and "(d) … training density (**dotted line**, 0.5)". The disambiguating word "vertical" was deleted in the diet. *Fix:* restore "vertical dotted line".

**m13.** Fig. 4 caption: "Prevalence and **the ECA validation: Sec. IV G**." §IV G contains prevalence and the horizon caveat; the ECA validation ({54,106,110}, sensitivity 1.0, balanced accuracy 0.99) is in the Appendix D body directly beneath the figure. *Fix:* "Prevalence: Sec. IV G; ECA validation: below."

**m14.** Abstract is 281 words (was 263) — longer after a "plain-register" pass, and above the ~250-word ceiling AIP applies. Unglossed terms remain ("pseudo-posterior decoder", "identifiability frontier"). Separately, the new gloss "*exchangeable* with---**statistically indistinguishable from**---an independent Monte-Carlo replicate" risks being read as an empirical non-significance result, which is exactly what Eq. (2) and App. A insist it is *not* ("there is no hypothesis to test"; the audit is resolution-limited on 2 of 8 comparisons). *Fix:* gloss as "has the same distribution as" and drop one of the two duplicated magnitudes (3–35, 354×).

**m15.** Fig. 1: two of twelve panels (rule 0, runs A and B) are blank, and the caption must explain in words that "rule 0 erases its random initial row in one step" — because the $t=0$ row is 1/62 of the panel height and invisible. The figure cannot show its own initial condition. *Fix:* draw the first 3–4 rows at enlarged scale as an inset, or substitute a rule whose damage dies after several steps.

**m16.** Fig. 1's "extent" bracket — the annotation the caption singles out ("The bracket on the rule-110 panel marks the final-row *extent*") — prints as a ~6 pt white-with-black-stroke smudge over yellow damage and is unreadable at final size. *Fix:* move the bracket and label below the panel frame, in black on white.

**m17.** Fig. 1 column headers assert "rule 30 (**chaotic**)" and "rule 110 (**complex**)" without citation, in a paper whose §I explains that such class assignment is undecidable and measure-dependent and whose App. D refuses to promote a region to "complex". *Fix:* cite the classical schemes in the caption or drop the parentheticals in favour of protocol-level descriptions ("damage spreads", "damage persists in sparse structures").

**m18.** §IV G keeps the cost *conclusion* ("most accurate at every budget we measured") but exports the numbers that qualify it (283 ms/query, break-even ≈4700 queries) to App. F. The main text now states an advantage without its price. *Fix:* carry the break-even figure into the pointer sentence.

**m19.** Intro so-what: "much of the remaining score reproduced by a training-set lookup" understates §IV C, where retrieval is *level with* the trained estimators (0.864 vs CNN 0.880 on radius two) and *exceeds* the regression head on ECA (0.883 vs 0.847). *Fix:* "a training-set lookup matches it".

**m20.** Intro so-what: "The frontier, not the matched-regime verdict, **is what transfers**: … measured on CA and **conjectured** beyond it" asserts and withdraws transfer in one sentence; §V says "every *transfer* is conjectured". *Fix:* "is the part that might transfer".

**m21 (process).** During this review the working tree carried edits to `main.tex`, `landscape.pdf` and `make_figures.py` that no commit or `trimmed_material.md` entry described, and two further commits (`0b3cef9`, `2040c01`, labelled "panel fixes") landed mid-review. Several defects I verified in the reviewed state (e.g. Fig. 1's caption claiming "the four statistics" when three are printed; App. E describing the detector as "a single seeded cell" when the code uses a five-cell random block) were repaired in-flight. *Fix:* re-run the round-8 drift audit (`489cee7`) over everything committed after it, and regenerate `main.pdf` before submission — the build I first inspected embedded a superseded `landscape.pdf` whose y-axis read "low = gliders" and whose in-figure title was clipped.

---

## 3. Ignored Alternatives

1. **Illustrate the transferable result, not only the definitions.** R1 asked for "a minimum of two figures". Both new figures illustrate targets (Fig. 1) and a descriptive appendix artefact (Fig. 5). Nothing illustrates the corruption axes — a clean diagram beside the same diagram at 5% bit-flip and 40% masking, with the recovered table's error highlighted, would show *why* one corrupted transition flips an entry and would carry the frontier, which §V calls the part that transfers.
2. **Show a radius-two damage cone.** Fig. 1 is entirely ECA. The paper's primary panel, force-holding, enrichment analysis, frontier and landscape are all radius-two, where the cone opens at speed 2 and the horizon is 30. One radius-two column would connect the pedagogy to the evidence.
3. **Random exemplars over agreement exemplars.** A stratified random draw of three signature rules (low/median/high fill) with the sentence "these were drawn at random, not selected" is a *stronger* honesty move than intersecting with a chance-level detector, and would cover the region rather than one corner.
4. **Cut instead of move.** Relocating §IV G/H changed the reading order but not the page count. Deleting the ρ delta-method paragraph, §IV B, or Table I would have shortened the paper; the revision considered neither.
5. **A "how to read the tables" box** (one column, four sentences: what $R^2$ ceiling applies to which family, what ρ = 1 and √2 mean) would have done more for R2's ML audience than 120 extra Introduction words, and would have prevented C1 structurally.
6. **Engage the neural-CA literature for R3.** The Discussion argues from inductive bias and cites `gilpin2019`/`mordvintsev2020` only in passing; it never engages published attention or graph models on CA dynamics, which is what an ML referee means by "closes the book".
7. **Response letter.** The decision to ship no point-by-point response shifts the entire verification burden onto the referee, who cannot read `git log` (see §4).

---

## 4. Missing Stakeholder Perspectives

- **The referee being answered.** With no response letter, compliance with R1–R4 must be reconstructed from an unpublished git history. The referee cannot see `trimmed_material.md` or commit `489cee7`. Every claim I could check about "no numbers changed" was checkable only because I had the repository; a real referee would have to take it on trust.
- **The ML reader R1 wants converted.** The paper still opens with a 281-word abstract, then a 158-word lead paragraph, then a 1,090-word Introduction, before any picture. There is no takeaway box, no "what to do differently when designing a benchmark" list; the benchmark-design prescription is a single Discussion sentence ("Benchmark designers who intend to test representation learning must break that encoding…").
- **Print and colour-vision readers.** Fig. 4 encodes its only categorical distinction as crimson vs steelblue (collapses in greyscale, marginal in deuteranopia) at a 4.5 pt legend; Fig. 3's caption says "Solid/dashed pairs **share a colour**", making colour the sole grouping cue across eight curves.
- **AIP production.** 18 pp, a 281-word abstract, and four figure elements below 6 pt at final size are all things production will bounce; `\hypersetup{colorlinks}` and the remaining `% TODO(user)` markers (ORCIDs, corresponding address, funding, DOI, CRediT) are still in the file.
- **Replicators.** `Data availability` says `make_figures.py` regenerates Figs. 1, 4 and 5, but the script needs `cache/s4_landscape.npz` *and* an importable `caspectra`; the exemplar block also contains a 24-attempt retry loop that silently searches for a surviving seed — harmless where alive = 1.0, but it is a selection mechanism in the released figure code and is undocumented in the paper.
- **The reader of Fig. 5 who wants the region, not three rules.** The 234-rule signature region is now represented in print by three rules from one corner; a reader asking "what does the *rest* of it look like" is given nothing, and the answer ("we cannot show it honestly") is never stated as such.

---

## 5. Observations (Non-Defects)

**O1. Fig. 1 does the job R1 asked for, and does it well.** The twin-run protocol, the light cone, the flip marker and the damage panel are exactly the three-panel construction the referee specified, and the rule-204 column makes the fill-degeneracy ("a single surviving damaged column has extent 1 and hence fill 1") visible in a way three rounds of prose did not. Whatever else this round did or did not shorten, this figure is a genuine gain.

**O2. R4's promotion is well executed where it lands.** The new "*Scope of the noise-axis verdicts, stated first*" paragraph at the head of §IV F is unhedged, quantitative (coverage 0.58 at 2%, 0.13 at 20%), and names the estimator that was not built. My M7 is about placement, not content.

**O3. Paragraph breaking is real.** The Introduction gained three breaks, §II C two, §IV A/F/(i) and §V several more; the pages I inspected no longer show 25-line monoliths in the Introduction (§II B remains one). This is measurable, not cosmetic.

**O4. I found no drift in any pre-registered quantity.** The bodies of Tables I–IV and VI are byte-identical between `main` and `HEAD`; the ρ values, reliability benchmarks, verdict language, TOST margins, force-holding disclosure, the outcome-dependent-panel disclosure, the enrichment decomposition and the "handicapped comparison" concession all survive the rewording. The adversarial old-vs-new audit recorded in `489cee7` restored at least twelve hedges the presentation pass had dropped (including the abstract's "for those rules" scope and the frontier caption's unplotted-controls disclosure, itself a round-5 mandate). That audit is the single most creditable part of this round, and it is why my CRITICAL findings are two caption/appendix sentences rather than a claim change.

**O5. The caption diet did cut the worst offenders.** Fig. 3's caption 227 → 155 words, Fig. 2's 201 → 132, Table I's 194 → 139, Table VI's 191 → 131, Fig. 4's 165 → 114. The complaint in §1 is that the savings were immediately re-spent on the two new captions (164 + 125), not that no cutting occurred.

**O6. The appendix relocation is defensible on the record.** The 20 Aug DeepSeek report asked for exactly this ("the landscape … and detector … should be in an Appendix, with the main text only summarizing the prevalence claim with its horizon caveat"), and the round-8 pointer subsection does keep the 7.8%, the Wilson CI, the 3/88 → 6/88 horizon caveat and the refusal to promote the region. The tension is that R1's request to *visualize* that region was then satisfied inside the appendix another referee asked to minimize — a genuine conflict between two reports, not a unilateral burial.

**O7. Not a defect, but worth knowing:** the benchmark's `evolve(ic, n_steps)` returns `n_steps` rows with `n_steps − 1` rule applications, while the rate is normalized by $2rT$ with $T = n_{\text{steps}}$. The maximum achievable rate is therefore $(2r(T{-}1)+1)/(2rT) = 0.992$ at $r{=}1, T{=}62$, not the $1.008$ stated in §II B and printed on Fig. 4's $x$-axis. Nothing in the paper depends on it (the largest observed rate is 0.816), and it predates round 8 — so it is out of scope for a presentation re-review. I flag it only because the new Fig. 1, by printing per-pair rates next to a drawn light cone, is the first artefact in the paper that makes it auditable.
