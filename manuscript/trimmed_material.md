# Material removed in the post-round-4 condensation pass

The manuscript was condensed from 15 to 14 pages (~700 words of prose)
after the round-4 revision (reviewer minor m11: rhetorical tightening),
with **no change to any registered number, verdict, margin, or
disclosure**. The pass stopped at 14 pages rather than the ~13 initially
targeted because the remaining text is almost entirely reviewer-mandated
content (C1–C8, m1–m14, Q1–Q10 anchors across rounds 2–4) that the
condensation rules protect; the un-cut duplications listed below were the
whole reducible surplus. This file logs every *substantive* cut: content
(sentences carrying numbers, caveats, examples, or expositions) that was
removed rather than merely reworded. Pure wording tightenings are not
logged. The full pre-trim manuscript is recoverable at commit `269f444`
(`git show 269f444:manuscript/main.tex`).

Format per entry: **location** (pre-trim section), *what was removed*
(verbatim LaTeX or a faithful summary), why, and where the surviving claim
now lives.

---

## Abstract

*Removed:* the qualifiers "deterministic, synchronous" from the
observation-model list ("fully observed, noiseless, deterministic,
synchronous, binary diagrams of known radius" → "complete, noiseless, binary
diagrams of known radius"), and the appositive "a family whose accuracy is
set by simulation budget, not training" reworded into the closing sentence.
*Why:* the full observation model is stated and flagged as load-bearing in
Sec. II A; the abstract keeps the defining subset.
*Survives in:* Sec. II A ("complete, noiseless, binary, synchronous in the
observed time direction, spatially uniform in the rule, and of known
radius").

## Sec. I, budget-indexed-family exposition (pre-trim ll. 148–166)

*Removed (verbatim):*
> A direct estimator can in principle exceed the family's matched-budget
> member on the noisy score---by at most that same $1-\mathrm{ICC}$
> headroom, which identification also claims simply by buying more
> simulation---but it cannot beat the family: […]
plus the sentence fragment "with its scope made precise" and the standalone
sentence split of the family claim.
*Why:* the same mechanism is stated in full in Sec. II C (the headroom
paragraph); the Introduction keeps a one-parenthetical statement of the
$1-\mathrm{ICC}$ gap with a pointer.
*Survives in:* Sec. II C ("The gap between the two ceilings … identification
claims it by raising its own $n_{\mathrm{pairs}}$, a direct model only by
actually estimating $\theta$."); Intro parenthetical.

## Sec. I, "three results" paragraph (pre-trim ll. 168–198)

*Removed (verbatim):*
> (median \rtwo{} ${\approx}0.5$--$0.6$ out to $15\%$ noise for two of three
> training seeds; the third trains far weaker, a measured seed sensitivity we
> report alongside a replication of the whole axis on an independent rule
> panel)
and "two standards that are easily conflated and that we separate
explicitly", "with matched adaptation budgets".
*Why:* the seed-band numbers appear in Sec. IV F (iii), Table V, and the
Discussion; the Introduction now says "with measured seed sensitivity and an
independent-panel replication reported alongside".
*Survives in:* Sec. IV F (iii) seed-replication paragraph (band 0.24–0.62,
two of three seeds 0.49–0.62); Table V; abstract ordering/level sentence.

## Sec. II C, measured reliability listing (pre-trim ll. 283–287)

*Removed (verbatim):*
> On ECA the four targets give ICC $0.994/0.999/0.9995/0.999$ (survival is
> the noisiest, Monte-Carlo std $0.022$) and replicate agreement
> $0.987/0.998/0.999/0.998$; on radius two, ICC $0.987/0.998/0.998/0.980$
> and agreement $0.974/0.997/0.997/0.959$.
*Why:* these sixteen values are exactly the two rightmost columns of
Tables II and III; the prose now points there and keeps only the
survival-noise aside (std 0.022).
*Survives in:* Tables II and III, "replicate agreement" and "ICC" columns.

## Sec. III (i), coverage numbers (pre-trim ll. 313–320)

*Removed:* the full per-rule and per-diagram coverage/exact-reconstruction
listing (156/160, <0.001 completion sensitivity, 10,240-diagram rate 0.990,
median coverage 1.0, 4,608 ECA diagrams both 1.0), which appeared again in
Sec. IV A's completion-prior paragraph.
*Why:* stated twice; Sec. III keeps the estimator/policy *definition* and a
pointer, Sec. IV A now carries all coverage *results* once (per-rule and
per-diagram units combined).
*Survives in:* Sec. IV A completion-prior paragraph (verbatim numbers,
including the rev-11 per-diagram audit).

## Fig. 2 (frontier) caption

*Removed:* "the sampled reader alone holds near zero out to $20\%$" and the
qualifier "of cells hidden" on the masking sentence.
*Why:* the sampled-reader result is stated with its numbers in
Sec. IV F (ii) ($[-0.04, 0.17]$ from 7.5 to 20% noise).
*Survives in:* Sec. IV F (ii).

## Sec. IV G, framing sentences

*Removed (verbatim):*
> Accuracy is not the only utility criterion. […] What follows is a
> deployment vignette on one machine, not a hardware-neutral cost study; […]
> The choice is therefore workload-dependent in the ordinary way; what the
> Pareto view adds is that […]
*Why:* framing/meta-commentary; "deployment vignette on one machine" and the
same-core timing condition are retained, which carry the scope limitation.
All timing numbers, the break-even, and the one-sided-Pareto conclusion are
unchanged.
*Survives in:* Sec. IV G (condensed).

## Fig. 3 (landscape) caption

*Removed:* the prevalence numbers ("met by $7.8\%$ (Wilson $95\%$ CI
$[6.9,8.8]\%$) of the sample versus $3/88$ elementary orbits") and the ECA
validation nuance ("matches the literature class-IV set exactly up to the
borderline rule $106$, but the independent detector available at radius two
is itself unreliable there").
*Why:* stated in full, with the same numbers, in the Sec. IV H text
immediately adjacent; the caption now points there.
*Survives in:* Sec. IV H, second paragraph.

## Sec. V (Discussion), duplicated frontier numbers

*Removed:* from the neural-results paragraph, the parenthetical
"(median \rtwo{} ${\approx}0.5$--$0.6$ to $15\%$ noise for two of three
seeds, with large run-to-run training variance)" and "holds … to $20\%$";
from the same paragraph, the rev-10 control detail "it trades cone fill up
for survival down at a slightly lower median, and the mechanistic estimator
stays superior on all four targets".
*Why:* the Discussion stated the frontier numbers twice (once mid-discussion,
once in the closing guidance). The closing guidance now carries them once,
updated to the registered per-seed range (0.24–0.62, two of three
0.49–0.62); the control detail lives in Sec. IV F (iii).
*Survives in:* Discussion closing-guidance sentence; Sec. IV F (iii).

## Appendix A, three-hypotheses paragraph

*Removed:* the full verbatim restatement of the three rev-9 hypothesis
verdicts (~60 words of duplicated verdict prose).
*Why:* the same verdicts, with the same wording of record, appear in
Sec. IV F ("Verdicts"); Appendix A keeps the registration-status one-liner
per hypothesis and points there.
*Survives in:* Sec. IV F Verdicts paragraph; Appendix A (compressed list).

## Appendix C, worked example

*Removed:* the scene-setting sentence "Suppose noise corrupts a diagram so
that neighbourhood $011$ is observed…" (the neighbourhood label $011$ was
dropped; counts kept) and the redundant intermediate factor "(4-3)" in
$\ell=(4-3)\log 19$.
*Why:* compression; the arithmetic and the design point (sampled tables
disagree exactly where the diagram is uninformative) are unchanged.
*Survives in:* Appendix C (condensed example).



---

# Material moved or removed in the round-8 revision (sixth report, 21 Aug 2026)

Presentation-only pass responding to `reviews/review_gemini_21aug26.md`
(figures, de-jargon, restructure); **no change to any registered number,
verdict, margin, or disclosure**. The full pre-revision manuscript is
recoverable at commit `a403c0a` (`git show a403c0a:manuscript/main.tex`).

## Sec. IV G (Cost) + IV H (Descriptive by-products) → Appendix "Cost and phenotype maps"

*Moved, not removed:* the full cost analysis (283 ms / 1.0 ms / 1.4 ms,
break-even ≈4700 → ≈50, 16-pair 0.924, annealed −2.15 paragraph) and the
phenotype-map paragraph (Spearman 0.67 vs 0.61, CI [−0.002,+0.102],
inconclusive verdict verbatim) now live in the new final appendix
(`app:secondary`). The main text keeps a pointer subsection
(`sec:constructive`) with the one-sentence cost conclusion and the full
landscape-prevalence paragraph (7.8 %, Wilson CI, 3/88 → 6/88 horizon
caveat, refusal to promote the region).
*Removed in the move:* the clause "a $127$-cell ring fits in two
\texttt{uint64} words" (wording detail of the bit-packing sketch); the
label `sec:compute` (its one incoming reference now points to
`app:secondary`).
*Relocated:* "the criterion's precision against literature class IV falls
from $2/3$ to $1/3$" moved from the prevalence paragraph into the
Appendix D horizon-matching paragraph, where the matched-$T$ rule set it
refers to is stated.

## Sec. IV F, seed-variance and panel-replication paragraphs

*Removed:* narrative connective tissue only ("That diagnosis was testable,
so we tested it: …", "which would be selection on the test set", "We
therefore no longer report … as a property of this estimator family", "in
its own right", "not as a sharp boundary"). Every number retained
(0.24–0.62, 0.24–0.33, 0.46–0.64, 0.46–0.56, 0.43–0.55 vs 0.29–0.51,
2×→1.4×, 0.18–0.36; 0.39–0.81, 0.79/0.70/0.61, 3–7.5 % band,
masking/density-not-replicated caveat).

## Sec. IV A, panel-decomposition paragraphs

*Removed:* "We disclose that" framing (disclosure itself retained verbatim),
"Decomposing the panel shows", "so the comparison is in principle
handicapped. The measured direction agrees with the concern". All numbers
and the "conservative for the headline claim" logic retained.

## Sec. IV C, stacking/retrieval

*Removed:* "Whether that information is harvestable has a measured answer:"
(merged into the following sentence) and "so the practical order of
preference under the matched observation model is clear" (restatement; the
+0.14 to +0.84 increments stay).

## Round-8 caption pass (five mini-essay captions → ≤ half length)

*Moved:* the reduced-budget ceiling arithmetic from the Fig. 2 (identifiability)
and Fig. 3 (frontier) captions, and the per-panel reliability-recomputation
note from the Table I caption, into Appendix B (new convention (7) and the
new "Reduced-budget scoring ceilings" paragraph); the checkpoint-selection
practitioner advice from the Table IV caption into the Sec. IV F
seed-variance paragraph; the coordinate-effect quantification (1.058
relation, 1.5x vs 2.6x, 234/732 box) from the Fig. 4 caption into the App. D
body; the coupon-collection detail (127 draws vs 32H32≈130) from the Fig. 2
caption into the Sec. IV E body; the polarity-axis description and the
eight-posterior-samples detail from the Fig. 3 caption into Sec. IV F(i).
*Removed as body duplicates:* the Fig. 3 caption's fairness-controls
cross-reference sentence; the Table IV caption's CI-in-artifact and
clipping-convention parentheticals (App. B (3) states the convention); the
Table I dagger note's "3.1% signature-complex" (stated in Sec. IV F(iv));
"re-simulates under the reference protocol" (Fig. 2 caption; stated in
Sec. IV E body).

## Round-8 abstract and introduction

*Removed:* from the Introduction's budget-indexed-family exposition, the
clause "; a parallel cost hierarchy is known on the rule-table
side~\cite{vispoel2026structure}" (citation survives in the new App. F) and
"with simulation budget now part of the cost" (stated in App. F). The
Discussion's stochastic-CA passage lost two mechanism clauses ("with the
$\varepsilon$ apparatus dropping out…", "…only input-side window overlap
remains") and "so the determinism axis is also a line through a known
critical phenomenon" (the directed-percolation fact stays).
*Added (no new claims):* abstract glosses for "amortization" and
"exchangeable"; one explicit so-what sentence per Introduction result,
restating measured facts (0.98/twenty-times, lookup, frontier succession)
qualitatively with section pointers.

## Round-8 claim-drift audit (post-pass corrections)

An adversarial old-vs-new audit of every reworded region was run after the
presentation pass; it flagged dropped hedges/disclosures and over-strong new
phrasings, all restored or softened in the same round:
- restored: abstract "for those rules" scope; intro "simulation budget now
  part of the cost" and the vispoel2026structure parallel-cost-hierarchy
  clause; "comparison is in principle handicapped" (IV A); "practical order
  of preference" (IV C); "should be read as a band … not as a sharp
  boundary" (IV F); the stack in the label-polarity degradation claim; the
  Fig. frontier unplotted-fairness-controls disclosure (round-5 mandated);
  Fig. ident (d) "re-simulates under the reference protocol"; Table IV
  per-cell-CI availability; Table I dagger "CNN median over"; App. F
  "two uint64 words"; Discussion stochastic-CA support clauses and
  "three conditional probabilities … exactly at the corners".
- softened (new R3 paragraph): "maximally aligned" → "natural inductive
  bias"; "task-structural, not architectural" → incentive set by the task;
  retrieval claim split into its two measured variants; binding-constraint
  diagnosis rephrased to leave the registered open question open.
- abstract opener now reuses the registered phrasing "not a function of any
  single observed diagram" instead of the new "no formula reads" claim.
Two flags were judged intentional/incorrect: the exemplar-figure content is
the referee-required R1 addition (derived from released validation
artifacts), and the Gibbs/EM factor-graph characterization already existed
in the old Discussion.
