# Peer Review Report

## Manuscript Information
- **Title**: Rule reconstruction from a single spacetime diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata
- **Manuscript ID**: branch `review-round8-gemini` (HEAD `489cee7`)
- **Review Date**: 23 Aug 2026
- **Review Round**: Round 8 (re-review of a presentation-only revision)

**Basis of review.** I reviewed `manuscript/main.tex` and `manuscript/main.pdf` (18 pp, compiled 21 Aug 19:23) at commit `489cee7`, the five figure PDFs as committed at that hash, the change record (`git log main..HEAD`, `trimmed_material.md` §§ round-8), and — because figure fidelity is my remit — the generating code (`manuscript/make_figures.py`, `caspectra/eval/dynamics.py`, `caspectra/ca/eca.py`). Note for the editor: the working tree moved *during* this review (all three regenerated figure PDFs at 13:52, `main.tex` at 13:58, both uncommitted). One of my findings (W1) is already repaired in that uncommitted state; I report it against the committed/compiled artifact and say so.

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 2 — Domain expert

### Reviewer Identity
Cellular automata and complex systems: damage spreading and Boolean derivatives, Wolfram/Li–Packard classification and its limits, CA identification and inverse problems, spacetime-diagram conventions.

### Review Focus
Whether the three new/changed figures are faithful to the field's rendering and light-cone conventions and to the paper's own protocol-tuple discipline; whether the exemplar figure overclaims gliderhood or promotes the signature region; whether the de-jargoned Introduction retains technical precision (genotype/phenotype, protocol tuple, undecidability, damage-spreading lineage); and whether any domain claim drifted during the rewrite.

---

## Overall Assessment

### Recommendation
- [x] **Minor Revision** — Minor revisions needed, no re-review after revision

### Confidence Score
**5** — CA dynamics, damage spreading and CA identification are my primary area; I was able to verify the figures against the generating code and against analytic expectations for the depicted rules.

### Summary Assessment
The manuscript benchmarks amortized prediction of finite-horizon damage-response statistics against the transparent alternative of reading the rule table off a single spacetime diagram and re-running the perturbation experiment, and maps the identifiability frontier where that reading fails. Round 8 was presentation-only, and on my axes it succeeded: the paper now has the spacetime and damage-cone figure the field expects (Fig. 1), an exemplar figure for the signature region (Fig. 5), a stated rationale for the convolutional neural boundary, and the missing-decoder admission at the head of Sec. IV F. I checked for the failure mode that matters most in a rewrite of this kind — a hedge quietly disappearing — and found the opposite: commit `489cee7` restores hedges the compression had dropped, and no registered number, verdict, margin, or refusal-to-promote changed. Fig. 1 is domain-faithful in the details that are easy to get wrong (square pixels, standard 1 = black rendering, ±r cells/step cone, and a rule-30 damage cone whose fast side is correctly the one forced by ∂f/∂L ≡ 1). The remaining problems are production-level rather than scientific: the *shipped* Fig. 4 carries an axis gloss ("low = gliders") that asserts exactly the promotion the text refuses; Fig. 5 prints damage coordinates from a different protocol than the picture it labels; the new R3 paragraph states two claims more strongly than the cited work supports; and Fig. 1 never actually shows the initial condition or the flipped cell. All are caption-, code-, or sentence-level fixes requiring no new measurement, which is why I recommend Minor Revision rather than another major round.

---

## Strengths

### S1: Fig. 1 is a correct damage-cone figure, not a decorative one
The panel geometry is faithful in the ways a CA referee checks first. Pixels are square (`imshow` default aspect; 127 × 62 array in a 2.05 aspect panel), so slopes read directly as velocities; the state panels use `cmap="binary"`, i.e. the standard 1 = black convention; the cone is drawn at exactly ±1 cell per step from the flip (`make_figures.py` L178–185), which is the correct light speed for r = 1; and the neighbourhood indexing behind it (App. C, `k = Σ s_{t,i+o} 2^{r−o}`, leftmost most significant) is the conventional Wolfram ordering.

The rule-30 panel is the strongest evidence that the figure was computed rather than assembled. Rule 30 is f(L,C,R) = L ⊕ (C ∨ R), so ∂f/∂L ≡ 1 and damage propagates *rightward* at speed exactly 1 every step, while ∂f/∂R = 1 only when C = 0, giving a stochastic, sub-light leftward front. The rendered damage cone shows precisely that asymmetry — right edge pinned to the dashed cone, left edge ragged and shallower — and the printed rate 0.65 = (1 + v_L)/2 implies v_L ≈ 0.3, in line with the literature's left/right difference-pattern velocities for rule 30. The printed statistics are computed from the depicted pair in the figure script (L187–196), not copied from a cache, so caption and picture cannot drift apart.

### S2: The fill = 1 degeneracy is now visible instead of merely asserted
Sec. II B's sparse-end degeneracy ("a single surviving damaged cell has extent 1 and hence fill 1", lines 282–285) was previously a sentence a reader had to take on trust; it now cross-references the rule-204 panel, where a one-column damage stripe prints `fill 1.00` alongside `fraction 0.01`. This is the single best pedagogical gain of the round, and it directly serves the coordinate caveat that Fig. 4 and App. D depend on. Choosing rule 204 (identity) rather than a more photogenic class-II rule was the right trade: it earns its column twice.

### S3: The exemplar figure does not overclaim, and the region is not promoted
I looked specifically for gliderhood creep and did not find it. The Fig. 5 caption (lines 1515–1524) refuses a glider census and refuses promotion to "complex"; it discloses in the same breath that the corroborating localized-seed detector "performs at or below chance over the region as a whole"; App. D (lines 1548–1552) repeats that the detector "validates nothing either way"; Fig. 4's caption still calls the red set "a registered *threshold region*, not a discovered cluster and not a validated glider region"; and Sec. IV I still declines to call the 7.8 % region "complex" or "glider-supporting". A figure of localized structures is the classic place where a damage-signature criterion gets silently upgraded into a class label, and this one does not do it.

### S4: The de-jargoned Introduction kept every domain-critical qualification
Comparing line by line against the pre-round-8 text, the Introduction's changes are paragraph breaks, one figure reference, and added so-what sentences; the load-bearing precision is untouched. Specifically retained: the genotype/phenotype framing with its correct attributions; undecidability scoped to the asymptotic formalization and not to finite protocols ("the obstruction applies to that asymptotic formalization, not to every finite protocol", `culikyu1988`); measure-dependence of the observed class (`gilman1987`); the protocol tuple as the object of study; the damage lineage from Kauffman through Derrida–Pomeau's annealed treatment to the Bagnoli–Rechtman–Ruffo / Baetens formalization via Boolean derivatives; and the deliberate refusal to call the targets "invariants". The bibliography entries for all of these are correct and apt, and the Domany–Kinzel characterization in the Discussion ("three conditional probabilities, deterministic rules exactly at the corners of that cube, and one face equivalent to generalized directed percolation") is a precise description of that model's parameter space.

### S5: The caption diet improved App. D rather than thinning it
Moving "its precision against literature class IV falls from 2/3 to 1/3" next to the matched-T rule set it refers to (App. D, lines 1540–1544) makes the number checkable for the first time: the matched-T set is {37, 45, 54, 60, 106, 110}, of which the literature class-IV members are {54, 110}, i.e. 2/6 = 1/3, against {54, 106, 110} → 2/3 at T = 62. This is the one place where the round-8 compression strengthened a domain claim's auditability.

---

## Weaknesses

### W1: The shipped Fig. 4 axis label asserts the promotion the paper refuses
**Problem**: The committed `figures/landscape.pdf` at HEAD — and therefore p. 16 of the compiled 18-pp `main.pdf` — carries the y-axis gloss "cone fill (low = gliders; 1 = solid cone OR single cell)". Sec. IV I states "we do not promote the $7.8\%$ region to ``complex'' or ``glider-supporting''", and the figure's own caption calls it "not a validated glider region". The same shipped PDF also carries an in-figure title, "Range-2 damage-signature landscape (stars: embedded ECAs)", which duplicates the REVTeX caption and is clipped at the canvas edge (the string runs past the MediaBox; the y-label is clipped at the top for the same reason). Since the round-8 figure regeneration is what put the exemplar markers a–c into this figure, this is a defect in an artifact this round touched.
**Why it matters**: Axis furniture is read as an assertion, and it is read *before* the caption. A referee or reader who takes "low = gliders" at face value will conclude that the paper claims the low-fill part of the red region contains gliders — the exact claim App. D spends a paragraph disowning. A clipped title in a submitted figure also invites a production desk-reject.
**Suggestion**: Regenerate and commit. I note that an uncommitted working-tree version of `make_figures.py` already makes both fixes — "low = sparse damage; 1 = solid cone or single cell", no in-figure title, `bbox_inches="tight"` — with a code comment stating the reason. Commit that script and the regenerated PDF, and recompile `main.pdf`; nothing else is needed. Until then the reproduction entry point advertised in Data availability (lines 1210–1217) produces a *different* figure than the one printed, which is itself a reproducibility defect.
**Severity**: Major (as shipped); trivial to close.

### W2: Fig. 5 prints numbers from one protocol on top of a picture from another
**Problem**: The panel titles read "(a) rule 1322117304: rate 0.19, fill 0.54". Those are `t[i, RATE]`, `t[i, FILL]` from `cache/s4_landscape.npz` (`make_figures.py` L278) — the rule's *damage* coordinates under the benchmark tuple: ring 127, Bernoulli(1/2) twin runs, T = 30. The picture beneath is a *localized-seed* evolution: ring 255, quiescent background, five-cell random seed, 62 rows (L238–281) — the App. E detector's protocol. The caption states the seed but not the ring, the horizon, or the fact that the numbers describe a different experiment.
**Why it matters**: Fig. 1 explicitly teaches the reader that in-panel numbers are "the statistics of *this single pair*". Fig. 5 uses the same visual grammar for the opposite meaning. The mismatch is visible: in panel (b) the left front hugs the drawn light cone, i.e. an extent growth of roughly half the r = 2 maximum, while the title says 0.19. A reader trying to reconcile the two will conclude either that the figure is wrong or that "rate" means something different here. More importantly, a paper whose central methodological insistence is that every quantity is indexed by a protocol tuple should not print an appendix figure under an unstated second tuple.
**Suggestion**: One clause: "Localized-seed protocol of App. E (ring 255, quiescent background, 62 steps); the printed rate and fill are the rule's Fig. 4 damage coordinates (ring 127, Bernoulli(1/2) twin runs, T = 30), not statistics of the diagram shown."
**Severity**: Major.

### W3: The new neural-boundary paragraph overstates two domain claims
**Problem**: Lines 1105–1121. (a) "A synchronous CA update *is* a local convolution — CA and convolutional networks are formally close [gilpin2019]". A CA update is a shift-equivariant map of a bounded neighbourhood into a finite alphabet; it is a convolution *composed with a pointwise nonlinearity or lookup*, which is what Gilpin constructs. The italicized "is" claims an identity the cited work does not assert. (b) "the constrained network and the $354\times$ larger unconstrained one bracket that family from both ends at this budget". Those two points do not bracket the convolutional family in any ordering a CA reader will accept, because the member closest to the mechanism under discussion is missing by design: a network whose first-layer kernel spans the (2r+1)-cell neighbourhood *together with its output cell* — i.e. the architecture that can implement tabulation directly, and the one Ref. `rollier2024cnn` used to reach 99.9 %. The paper's constrained CNN uses 2 × 2 kernels *specifically so that it cannot*, and `resnet18` is a generic ImageNet backbone, not the CA-shaped member. So the bracket runs from "deliberately handicapped" to "off-the-shelf", with the natural candidate outside it. A minor third instance: "it is what lets a network read the elementary rule off one clean diagram at 99.9 %" attributes that result causally to the convolutional inductive bias, which no experiment here or in the cited paper isolates.
**Why it matters**: R3 asked *why* a CNN/ResNet marks the neural boundary. The answer given is the right one in outline — convolution is the matched inductive bias, and the shortcut incentive is set by the task — but it is stated as a bracketing argument that a CA-literate reader can puncture in one sentence, which weakens an otherwise well-scoped paragraph. The paper's own scoping sentence ("Architecture classes beyond this family are untested here") covers the transformer/GNN question but not the missing *convolutional* member.
**Suggestion**: Change "*is* a local convolution" to "is a shift-equivariant map of a bounded neighbourhood — a convolution followed by a pointwise nonlinearity, the construction that makes CA and CNNs formally close [gilpin2019]". Replace "bracket that family from both ends" with an honest statement plus the named omission: e.g. "span a constrained and an unconstrained backbone at this budget; the member we did not run is the one whose first layer matches the $(2r+1)$-cell neighbourhood and its output cell — the architecture closest to the tabulating inverter, and the one Ref. [rollier2024cnn] used." That turns a puncturable claim into a disclosed gap, consistent with how the paper handles the missing decoder.
**Severity**: Major.

### W4: Fig. 1 never shows the initial condition or the flipped cell
**Problem**: The caption promises "run A from a random initial row" and "run B from the same row with one cell flipped (marker)". At 62 rows per panel the t = 0 row is thinner than the axis frame: in the rule-0 column, run A and run B are *entirely white* boxes (I verified this on a 3200-px render), the random IC is invisible, the flipped cell is invisible in run B for all four rules, and the single differing cell at t = 0 is invisible in the damage row. The marker triangle sits outside the image and points at a cell the reader cannot see.
**Why it matters**: This is the one thing R1 asked the figure to make concrete — the twin-run perturbation. A reader meeting the rule-0 column sees two blank rectangles and a black rectangle and has to reconstruct the entire construction from the caption anyway, which is the situation the figure was added to end.
**Suggestion**: Any of: (i) a small zoom inset of the top ~5 rows of each column, at exaggerated row height, with the flipped cell boxed; (ii) a 1-pt coloured box around the flipped cell in run B and around the apex cell of the damage panel; (iii) render the t = 0 row as a separate strip above each panel. Option (ii) is a two-line change and would also make the rule-0 column say "the flip existed and died" rather than "nothing happened here".
**Severity**: Major (pedagogical, since it is the point of the figure); cheap to fix.

### W5: Each column of Fig. 1 uses a different initial condition
**Problem**: `rng` is created once and `ic` is drawn *inside* the rule loop (`make_figures.py` L153–157), so rules 0, 204, 30 and 110 each get a different Bernoulli(1/2) row.
**Why it matters**: The field's convention for a four-behaviour plate — Wolfram's class plates, Li–Packard's figures — is a common initial condition across rules, precisely so the reader attributes the visual difference to the rule and not to the draw. With four different ICs, the rule-204 column's stripe pattern and the rule-110 column's ether are not comparable, and a careful reader cannot tell whether rule 0's blank panel is the rule or an unlucky row (it is the rule, but the figure does not let them verify it).
**Suggestion**: Hoist `ic = (rng.random(TWIN_WIDTH) < 0.5)` above the loop and note in the caption that all four columns share one initial row. One line, and it makes the plate do what plates do.
**Severity**: Minor.

---

## Detailed Comments

### Title & Abstract
The title is accurate and appropriately scoped ("finite-horizon", "from a single spacetime diagram"). The abstract's plain-register rewrite is a real improvement — "train a model once, then predict per observation at almost no cost", "sorting ``dies out'' from ``spreads''" — and I checked each gloss against the body: both are faithful, and the "statistically indistinguishable from" gloss on *exchangeable* under-claims rather than over-claims what Eq. (1) establishes.

One precision problem, in the new opening sentence (lines 31–34): "these damage-response statistics are not a function of any single observed diagram". Under the paper's own matched observation model they *are* — that is the thesis: diagram → rule table → θ is a composition of functions, and it is exact for 100 % of ECA orbits. In the Introduction (lines 124–127) the premise clause "Because damage-response statistics require *two* runs of the simulator" makes the intended reading available; standing alone in the abstract, three sentences before "a single diagram identifies the rule table for $100\%$", the sentence contradicts the sentence that follows it. Suggested rewording that preserves the registered meaning: "are defined by running the simulator twice, not read off one diagram by any direct formula". I flag this as precision, not drift: the phrasing is the pre-existing registered one, moved.

### Introduction
Technically precise after de-jargoning — see S4. The added so-what sentences ("a conventional $R^2$ here can read $0.98$ and still sit twenty times above the target's own noise floor") restate measured facts qualitatively with section pointers and introduce nothing new. The new paragraph breaks land at genuine argumentative seams. The forward reference to Fig. 1 at the definition of damage spreading (line 113) is exactly the right place for it — but see the layout note below about where the figure actually lands.

### Literature Review / Theoretical Framework
Coverage of the damage-spreading and CA-identification lineages is appropriate and the positioning is precise. Table VI (App. E) remains the right instrument for the novelty boundary: it is unusual and creditable for a paper to tabulate the prior art that makes its own baseline unoriginal. One opportunity, not a defect: Fig. 1 now *displays* the left/right damage-velocity asymmetry of rule 30, which is a documented quantity in this literature; a single citation at the caption or at Sec. II B would let a reader check the picture against a published number rather than against their own derivative calculation.

### Methodology / Research Design
Out of my primary remit and reviewed by R1, but two domain-facing conventions deserve a check.

*Horizon and light speed.* `evolve(ic, n)` returns `n` rows, i.e. the rule is applied `n − 1` times (`caspectra/ca/eca.py` L144–160), and `damage_spreading_features` normalizes the rate by `2 · max_speed · n_steps` with `n_steps = ⌊w/2r⌋ − 1` (`caspectra/eval/dynamics.py` L96–116). The achievable maximum is therefore (2r(T−1)+1)/(2rT) = 0.992 at r = 1 and 0.975 at r = 2 — not the $(2rT+1)/(2rT) = 1.008$ stated in Sec. II B (lines 278–282), repeated in App. B(i) (lines 1372–1374), and printed on the Fig. 4 x-axis as "light speed = 1.008 here". Nothing in the paper depends on it (the maximum observed anywhere is 0.816, and the misstatement is conservative), but Fig. 1 now *draws* the cone at half-width T − 1 = 61 over 62 rows, which makes the convention visible and the discrepancy checkable for the first time. Please either state the convention explicitly ("T rows, T − 1 updates") and correct the ceiling, or normalize by updates.

*Protocol discipline.* The observation protocol is stated with unusual care, including the non-power-of-two ring choice; the exception is Fig. 5's undisclosed second protocol (W2).

### Results / Findings
The figure and table quality is otherwise good, and the round-8 restructure (cost and by-products to App. F, condensed Results) reads better without losing numbers — I spot-checked the moved cost paragraph, the annealed −2.15 member, and the phenotype-map "inconclusive" verdict against the pre-round-8 text and they are verbatim. The R4 response — the "Scope of the noise-axis verdicts, stated first" paragraph at the head of Sec. IV F (lines 808–816) — is exactly what the previous reviewer asked for: the unbuilt latent-diagram decoder, the measured miscalibration (0.58 at 2 %, 0.13 at 20 %), and the scoping sentence are now the first thing a reader of the noise results encounters, and the Discussion correctly demotes itself to a pointer.

### Discussion
The neural-boundary paragraph is the round's weakest new prose (W3); everything else is well scoped. The stochastic-CA passage survived compression with its content intact, including the Domany–Kinzel corner/face geometry. The protocol-tuple bounding paragraph and the closing guidance are unchanged.

### Conclusion
No over-inference. The refusals ("we do not name a published benchmark this invalidates", "we do not conclude that deep networks cannot close the gap", "not a validated glider census") are all still present and, per the drift-audit commit, several were explicitly restored after the compression pass removed them.

### References
Correct and apt for the domain claims I checked: `lipackard1990`, `culikyu1988`, `gilman1987`, `kauffman1969`, `derridapomeau1986`, `derridaweisbuch1986`, `bagnoli1992`, `baetens2010`, `domanykinzel1984`, `richards1990`, `adamatzky1994`, `yangbillings2000`, `gilpin2019`. No citation was orphaned by the restructure — `vispoel2026structure` survives in App. F as the change record states, and `derridaweisbuch1986` with it.

---

## Questions for Authors

1. **Fig. 5 numbers.** Do the printed `rate`/`fill` come from the S4 damage cache (ring 127, Bernoulli(1/2), T = 30) rather than from the depicted ring-255 localized-seed run? If so, will you name both protocols in the caption — and does the near-light-speed left front visible in panel (b) not deserve an explicit "this front is at the cone; the printed rate is a different measurement"?
2. **Horizon convention.** Does `n_steps` count rows (T − 1 updates) or updates? If rows, will you correct the 1.008 light-cone ceiling in Sec. II B, App. B(i), and the Fig. 4 axis gloss, and state the row/update convention where the horizon is defined?
3. **Neural boundary.** Would you be willing to name the untested convolutional member — a first layer matching the (2r+1)-cell neighbourhood and its output cell — in the R3 paragraph, given that Ref. [rollier2024cnn] used exactly that to reach 99.9 %? A named omission is stronger than a bracketing claim here, and it costs no measurement.
4. **Figure provenance.** Will the corrected `landscape.pdf` (axis gloss, no in-figure title) be committed and `main.pdf` recompiled before submission, so that `make_figures.py` reproduces the printed figure as Data availability promises?

---

## Minor Issues

### Figures and Tables
- **Fig. 4 caption cross-reference is circular.** "Prevalence and the ECA validation: Sec. IV I" — but Sec. IV I says the ECA validation is in App. D, and it is: the {54, 106, 110}, balanced-accuracy-0.99 sentences sit in the App. D paragraph directly below the figure. Point the caption to App. D for the validation and to Sec. IV I for prevalence only. (Casualty of the caption diet.)
- **Fig. 1 damage panels invert the greyscale polarity.** State panels use 1 = black on white (`cmap="binary"`); damage panels use yellow on black (`cmap="inferno"`). Defensible, but say so in one clause — the field's default for a difference pattern is the same black-on-white as the states.
- **Cone styling is inconsistent across the two new figures**: white dashed in Fig. 1, crimson dashed in Fig. 5. Unify, so "dashed = light cone" is one visual vocabulary item.
- **Fig. 1's extent bracket is drawn five rows above the row it measures** (`make_figures.py` L198–207) while the caption correctly says "final-row extent". Add a leader to the last row, or move the bracket below the panel.
- **"rule 110 (complex)"** is the paper's only unhedged use of a class word as a rule descriptor. Rule 110's class-IV status is about as consensual as CA classification gets, but given how carefully the rest of the paper avoids this vocabulary, add "conventional labels" to the caption.
- **Fig. 5: disclose the fourth candidate.** `make_figures.py` L37–40 records that rule 345313848 fires the detector but sits at rate 0.288 in the S4 replicate, just outside the registered 0.28 window, and was therefore excluded. The paper discloses every other selection of this kind (including the outcome-dependent panel enrichment); one clause here would keep the standard uniform.
- **Fig. 5: say that the three exemplars are not spread over the region.** All three sit within ≈0.03 in rate and ≈0.04 in fill of the embedded rule-110 anchor (0.214, 0.569), while the red region spans roughly rate 0.15–0.28 and fill 0.32–0.62; none samples the lower-fill half. Under a title reading "What the signature region contains", a reader will take three near-110 points as representative. Retitling to something like "Three signature-region rules on which two criteria agree" plus one clause would fix both at once.
- **Fig. 5: "sparse".** The panels look dense (fill 0.54–0.58); "sparse" here is a criterion word (the detector's threshold is fill ≤ 0.75). Write "non-space-filling by the registered criterion" so the word is not read as a visual claim the picture contradicts.
- **Fig. 1 caption: "computed exactly as in the benchmark".** The benchmark flips a uniformly random cell; this figure flips the centre (stated earlier in the same caption) and averages nothing. "Same formulas as the benchmark" is the accurate phrase.

### Layout
- **Fig. 1 is three pages from its first citation.** `main.log` places `twin_run.pdf` on p. 4; it is cited in the Introduction (p. 1) and again at the definition of the targets (Sec. II B, ≈p. 3). As a full-width `figure*[t]` in two-column REVTeX it cannot land where it is needed. Consider moving the float earlier in the source, using `[!t]`, or rendering it single-column so it can sit beside Sec. II B.
- **Float congestion is new this round.** The log records two "A float is stuck (cannot be placed)" warnings plus "Deferred float stuck during \clearpage processing" (around the identifiability figure). A previous round reported a clean 0-warning build; worth restoring before submission.

### Language
- Abstract, opening sentence: see the precision note under Title & Abstract.
- Sec. IV F(i): "Simulating tables sampled from it (eight per diagram)" — the relocated detail reads as an aside; consider "eight posterior tables per diagram".

---

## Dimension Scores

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 82 | Strong | The identification-vs-amortization framing is a genuine contribution at the CA/ML boundary; the inverter itself is stipulated prior art and Table VI makes that boundary auditable rather than hiding it. |
| Methodological Rigor (25%) | 88 | Strong | Protocol-tuple discipline, registered decision rules, three distinguished reliability benchmarks, ρ in noise units. Deductions: the self-disclosed unbuilt latent-diagram decoder, and the shipped-figure/script divergence (W1), which is a reproducibility defect in an advertised entry point. |
| Evidence Sufficiency (25%) | 86 | Strong | Claims are matched to evidence target by target, with panel decompositions, fairness controls and a complement-panel replication. Deduction: Fig. 5's evidence base is three rules selected by agreement with a below-chance detector — honestly disclosed, but thin for a figure titled as it is. |
| Argument Coherence (15%) | 84 | Strong | The new figures and explicit so-whats improved the through-line. Deductions: the abstract's opening tension with the identifiability result, and Fig. 5's number/picture mismatch. |
| Writing Quality (15%) | 80 | Strong | Register is markedly plainer and paragraphs now breathe; captions are roughly half their former length. Deductions: some sentences still run long, and the caption diet left one circular cross-reference and one over-compressed claim (W3). |
| Literature Integration (optional) | 88 | Strong | Damage-spreading lineage (Kauffman → Derrida–Pomeau → Bagnoli/Baetens) and identification lineage (Richards, Adamatzky, Yang–Billings, Sun, Elser) both correctly cited and correctly characterized; Domany–Kinzel described precisely. Opportunity: cite a source for the left/right damage velocities Fig. 1 now displays. |
| **Weighted Average** | **84.5** | **Accept band by rubric** | |

**Note on the divergence between score and recommendation.** The weighted average falls in the rubric's Accept band, and on scientific content I agree with it: nothing in the science needs another round. I nonetheless recommend **Minor Revision** because W1 and W2 are defects in artifacts that *ship with the paper* — a printed axis gloss that contradicts the text's central refusal, and a figure whose numbers and picture come from different protocols — and because W3 is a new claim, introduced this round, that a domain referee will contest. All are fixable without new measurement and without re-review.

**On claim drift, explicitly.** I checked the full `main..HEAD` diff for the failure mode this re-review exists to catch. No registered number, verdict, margin, threshold, or disclosure changed; the panel-enrichment disclosure, the "in principle handicapped" concession, the crossover-is-a-band caveat, the unplotted-controls disclosure, and the refusal to promote the signature region were all *restored* by the drift-audit commit after the compression pass had dropped them. The only claim strengthening I found is in the new R3 paragraph (W3), and it is at sentence level, not at the level of a registered result.
