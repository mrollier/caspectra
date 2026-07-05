# Peer review: *Rule reconstruction from a single space-time diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata*

## A. Executive summary

This paper asks whether a learned model should predict finite-horizon damage-response statistics of a cellular automaton (CA) directly from one space-time diagram when that diagram may already reveal the local update rule. The paper studies binary, deterministic, synchronous one-dimensional CAs on a ring, with known radius, complete noiseless observations, and a fixed Bernoulli(1/2) initial-condition protocol. It considers all 88 elementary-CA symmetry representatives and a sampled radius-two rule panel.

The main contribution is a benchmark-design argument supported by experiments. The paper reconstructs a CA rule by tabulating observed neighbourhood-to-next-cell transitions and then estimates four perturbation-defined targets by re-running twin simulations: damage survival, conditional damage fraction, conditional spreading rate, and conditional cone fill. It compares this identification-then-simulation route with a five-feature regressor and a constrained CNN. The paper also introduces three reliability quantities: an ICC intended to quantify latent-target reliability, the agreement expected between two independent Monte-Carlo target replicates, stated as \(2\mathrm{ICC}-1\), and a larger-simulation reference.

Under the matched observation model, the paper reports exact reconstruction for all elementary hold-out rules and for 156/160 radius-two hold-out rules, with the mechanistic estimator attaining approximately the independent-replicate benchmark in Tables II–III. It then maps degradation by observation noise, masking, initial-condition-density shift, label flips, and unknown radius. In this exploratory frontier, it reports that a Bayesian rule-posterior method is strongest in several moderate-degradation regimes, while a degradation-trained direct CNN is strongest for 3–15% observation noise. Secondary analyses probe rule information in the learned representation and present a damage-signature landscape.

The paper is strongest when it frames rule reconstruction as a necessary baseline for this tightly controlled observational regime, distinguishes a fresh-simulation benchmark from a latent-target ceiling, and reports limitations of its neural architectures. The central contribution is clear from the abstract and introduction. However, the abstract and several later passages overstate what identification implies: reconstructing the generator removes an information disadvantage, but it does **not** by itself prove that no direct estimator can outperform a particular finite-Monte-Carlo identification-then-simulation implementation. Several evaluation and method details also need to be made explicit before the central empirical claims can be fully assessed.

This is an empirical methods/benchmark paper, not a formal complexity or proof paper. Its main technical burden is therefore precise specification of estimands, prediction units, sampling distributions, stochastic procedures, and uncertainty calculations.

## B. Strengths

- **The paper isolates a real benchmark-design issue.** The distinction between a diagram’s phenotype and the local transition rule is relevant and well motivated. Section I correctly makes the matched observation assumptions explicit rather than presenting the learned prediction task as assumption-free.

- **The target protocol is unusually concrete.** Sections II.A–II.B specify the ring width, radius-aware horizon, initial-condition distribution, perturbation mechanism, and four target statistics. This is much better than treating a broad “CA class” as a single intrinsic label.

- **The reliability discussion is valuable.** Section II.C usefully distinguishes agreement with a noisy cached Monte-Carlo target from agreement with a near-noise-free target. The paper is right to warn that these two standards should not be conflated.

- **The paper compares against an interpretable, strong baseline.** The reconstruction procedure is transparent, has a clear connection to established CA-identification work, and directly addresses the target-generating mechanism. This is a meaningful contribution to experimental methodology even though the inverter itself is not claimed as new.

- **Important negative results are scoped more carefully than usual.** Section III acknowledges that the constrained CNN and training budget do not represent all neural architectures. Section IV.D also retracts the stronger anti-shortcut interpretation after the probes show that rule information remains decodable.

- **The degradation study is conceptually well chosen.** Noise, partial observation, poor excitation through extreme initial-condition density, label polarity, and unknown radius are sensible axes along which identifiability can fail. Figures 1–2 provide an intuitive organizing picture.

- **The manuscript makes a serious reproducibility effort.** Appendix A distinguishes registered, post-hoc confirmatory, and exploratory analyses instead of treating all analyses as equally preregistered. It also discloses a corrected seeding problem. This is good scholarly practice.

- **The discussion usually states limits.** For example, Sections IV.H and V do not convert the radius-two damage-signature region into a validated glider census, and the direct-model claims are partly bounded to the architecture and training budget.

## C. Major concerns

### C1. The paper’s central “no direct method can beat reading the rule” claim is too strong for the stated finite-Monte-Carlo evaluation.

**Classification:** Critical correctness concern  
**Location:** Section I, especially p. 2 (“direct amortization can never beat it on accuracy in the matched regime”); Abstract, p. 1; Sections II.C and IV.A; Discussion, pp. 9–10.

**Why it matters:** The central conclusion should distinguish an information argument from an accuracy-dominance claim about a particular estimator and simulation budget.

**Evidence or reasoning:** Let the cached evaluation target be \(Y=\theta+\varepsilon\), where \(\theta\) is the protocol-defined latent mean for a rule and \(\varepsilon\) is Monte-Carlo error. A correctly reconstructed rule followed by an independent simulation of the same size yields \(Y'=\theta+\varepsilon'\). Under the paper’s additive equal-variance model, scoring \(Y'\) against \(Y\) gives the \(2\mathrm{ICC}-1\) benchmark. But a direct predictor that estimates \(\theta\), or an identification-based estimator that uses a much larger simulation budget, can have lower error against \(Y\) than \(Y'\) does and can approach the ICC benchmark. Thus exact identification establishes that the observation need not lose rule information; it does not prove that a direct estimator cannot outperform a **fresh, finite-budget** simulator on the chosen noisy score.

The manuscript partly recognizes this point in Section II.C through the large-simulation reference, but the stronger wording elsewhere conflicts with that distinction. The empirical result that the tested direct methods do not surpass the tested reconstruction-and-simulation implementation is supported by the reported tables; the universal or near-universal claim is not.

**What would resolve it:** Reframe the contribution as follows: exact rule reconstruction provides an information-preserving route and a transparent oracle family whose accuracy improves with the downstream simulation budget. State that the reported direct estimators do not beat the implemented reconstruction-and-simulation baselines under the evaluated budgets and protocols. Report all direct estimators against both the noisy-cache score and the large-simulation reference, and avoid “can never beat” unless a formal decision-theoretic statement, estimator class, loss, and compute constraint are supplied.

### C2. The unit of prediction and the computation of held-out \(R^2\) are not specified clearly enough to support the “single diagram” claim.

**Classification:** Major missing justification  
**Location:** Sections II.A–II.C, III, IV.A; Tables I–III; Appendix B, p. 11.

**Why it matters:** The manuscript’s central claim is about reconstructing a rule from one diagram, while Appendix B states that there are 256 diagrams per elementary rule and 64 diagrams per radius-two rule. The reader cannot determine whether each test prediction uses one diagram, whether predictions are averaged over diagrams of the same rule, or whether exact-reconstruction and coverage rates are computed per diagram, per rule after aggregation, or by a selected representative diagram.

**Evidence or reasoning:** The paper says “every ECA held-out table and 156/160 radius-two tables are fully covered” (p. 4), but a transition table is inferred from a diagram. At the same time, all uncertainty is resampled at the rule level and the targets are rule-level Monte-Carlo quantities. The definition of the reported \(R^2\) is therefore ambiguous: it could be computed over rules after aggregation, over rule-diagram pairs with correlated labels, or through another procedure. These alternatives answer different scientific questions and yield different effective sample sizes.

**What would resolve it:** Add a compact evaluation protocol box that specifies:
1. the observational test instance, including whether it is a \((\text{rule},\text{diagram})\) pair;
2. how many diagrams per held-out rule contribute to each reported number;
3. whether method predictions are averaged within rule before scoring;
4. whether coverage and exact-reconstruction percentages are per diagram or per rule;
5. the exact formula for every reported \(R^2\), including the denominator and aggregation order; and
6. how bootstrap resampling preserves the diagram-within-rule structure.

A per-diagram coverage histogram and a per-rule aggregate summary would make the “single diagram” statement auditable.

### C3. “Radius-two global” performance is evaluated on a deliberately enriched, nonrepresentative test panel.

**Classification:** Major missing justification  
**Location:** Table I, p. 5; Table III, p. 6; Appendix B “Splits,” p. 11; Figure 3, p. 9.

**Why it matters:** The claimed global radius-two performance may not estimate performance under the paper’s own stated uniform rule-sampling distribution.

**Evidence or reasoning:** Appendix B says that 57 signature-complex rules are force-held out. Table III then evaluates 160 held-out rules, 57 of which are signature-complex. Figure 3 reports that the signature comprises 7.8% of the 3000-rule landscape sample. Thus approximately 35.6% of the 160-rule test panel is signature-complex, far above the stated landscape prevalence. This is a reasonable stress-test design, but it is not a distributionally representative “global” hold-out estimate unless appropriate reweighting or a separate random test panel is used.

This also matters for comparisons among direct estimators, because Section IV.B shows performance varies substantially by target and Table I reports a separate complex subset. A test mixture enriched for difficult or unusual rules can change the summary ranking.

**What would resolve it:** Rename the current result as an “enriched radius-two evaluation panel,” report the sampling weights, and add either:
- a genuinely random rule-level test panel from the stated canonical-orbit distribution, or
- reweighted estimates with clearly stated target distribution and uncertainty.

Report results separately for the force-held signature panel and the remaining random hold-out rules. Also explain whether signature membership was computed from quantities independent of the target cache used for evaluation.

### C4. The degraded-observation reconstruction methods are insufficiently specified, especially under bit-flip noise.

**Classification:** Major missing justification  
**Location:** Sections III(i), IV.E–IV.F, pp. 5–7; Figure 2, p. 8; Appendix B, p. 11.

**Why it matters:** The identifiability frontier and Table V are a major part of the paper’s practical message. Their validity depends on the exact corruption model and on how contradictory observed transitions are handled.

**Evidence or reasoning:** Under cellwise observation noise, an observed neighbourhood can be corrupted in its input cells, its output cell, or both. Consequently, a simple per-entry Binomial likelihood over observed neighbourhood-to-next-cell counts is not obviously the likelihood induced by the stated cell-flip process: observed transitions are mis-binned, and overlapping space-time neighbourhoods are dependent. The paper may intentionally use a tractable approximation, but it currently calls the result a “Bayesian rule-posterior” without stating the generative model, prior, conditional-independence approximation, epsilon grid, self-consistency criterion, or posterior sampling procedure.

Similarly, the deterministic tabulation inverter is defined for noiseless consistent transitions, but its policy in the presence of contradictory transition observations is not stated. A majority vote, first observation, last observation, rejection, or a likelihood-based tie-break can materially change the rapid-noise-collapse curves.

**What would resolve it:** Provide pseudocode and notation for every degraded reconstruction method. Explicitly state:
- whether bit flips and masks are independent across cells and time, including treatment of the \(t=0\) row;
- whether masking removes transitions touching a missing cell;
- the deterministic inverter’s conflict-resolution rule;
- the prior over truth-table bits;
- the exact likelihood or pseudo-likelihood;
- how input-side noise is modelled;
- the epsilon prior/grid and the self-consistency objective;
- the number of posterior samples, random seeds, and transition counts used at each grid cell.

If the likelihood is an approximation rather than the exact observation model, call the method a pseudo-posterior or approximate Bayesian decoder and assess sensitivity to plausible alternatives.

### C5. The claim of being “statistically indistinguishable” from the replicate benchmark is not established by the reported intervals alone.

**Classification:** Major missing justification  
**Location:** Section IV.A, p. 4; Tables II–III, pp. 5–6; Section II.C, p. 3.

**Why it matters:** “Simulation-limited” is the paper’s headline calibration claim.

**Evidence or reasoning:** The text compares a point estimate for the mechanistic estimator with a point estimate for replicate agreement and observes that the mechanistic confidence interval contains the latter. Overlap or inclusion of a separately estimated benchmark is not an equivalence test, and it does not propagate uncertainty in the reliability estimate. The issue is more important because \(R^2\) is nonlinear and because survival and cone fill are explicitly described as heteroscedastic.

The identity \(2\mathrm{ICC}-1\) is appropriate only under the stated additive, independent, equal-noise-variance idealization. The manuscript should explain precisely how the reported empirical replicate agreement is estimated when rule-specific Monte-Carlo variances differ and conditional statistics have variable surviving-trial counts.

**What would resolve it:** For each target, bootstrap the paired difference
\[
R^2_{\mathrm{mechanistic}}-R^2_{\mathrm{independent\ replicate}}
\]
using the same resampled rules and independent replicate draws, and report a pre-specified equivalence margin or at least a confidence interval for that difference. Separately document the variance-component estimator, the role of heteroscedasticity, and why the empirical replicate-agreement computation is the operative benchmark even where the random-effects identity is only approximate. Replace “statistically indistinguishable” with “consistent with” unless an equivalence analysis is provided.

### C6. Several neural comparison claims do not include split and training uncertainty commensurate with their wording.

**Classification:** Major missing justification  
**Location:** Section III “Statistical protocol,” p. 4; Sections IV.B and IV.F(iii), pp. 4, 6–7; Tables II–IV; Appendix B, p. 11.

**Why it matters:** The paper correctly notes that the CNN was not retrained across outer splits, but later makes broad conclusions about direct methods, the 354x larger ResNet18, and the frontier winner.

**Evidence or reasoning:** The main CNN has five seeds but only one registered train/test rule split. The degradation-trained direct CNN, learned reader, and ResNet18 control are stated to use one seed in key frontier comparisons. Rule-level bootstrap intervals quantify test-rule sampling conditional on a trained model; they do not automatically include variation from model initialization, training stochasticity, hyperparameter choice, or the selected split. This is most consequential for close comparisons, the “no stable ordering” conclusion, and claims that the direct CNN is strongest from 3–15% noise.

**What would resolve it:** Retrain the main CNN and the relevant degradation controls over repeated outer rule splits and multiple seeds. Report a hierarchical uncertainty analysis or a transparent sensitivity table separating test-rule, split, and seed variation. At minimum, qualify all one-split or one-seed statements as provisional, including in the abstract and Table V. The main matched-regime conclusion may remain robust, but it should not be generalized beyond the tested direct estimators without this analysis.

### C7. The cross-fitted stacking result is a diagnostic of complementarity, not yet a held-out deployable stacked estimator.

**Classification:** Likely correct but needs clearer exposition  
**Location:** Section IV.C, p. 4; Table IV, p. 6.

**Why it matters:** The paper uses the result to support the claim that the CNN carries survival information missing from the five statistics.

**Evidence or reasoning:** The text says that the stacking base is refit “within the held-out panel.” Cross-fitting can provide a valid diagnostic of out-of-fold incremental association if folds, preprocessing, and all predictions are handled correctly. However, this does not by itself evaluate a meta-model trained only on the original training rules and then deployed on an untouched test set. The reported 0.56 to 0.88 survival improvement should therefore not be read as the expected performance of a train-once stacked predictor unless that separate evaluation is also performed.

**What would resolve it:** State explicitly that Table IV is a cross-fitted diagnostic conducted within the held-out rule panel. Specify whether the folds are grouped by rule, whether all transformations are fit inside folds, and whether CNN predictions are generated without using held-out labels. Add a deployment-style stack trained on training rules and evaluated on the untouched held-out rules, or limit the conclusion to residual complementarity rather than prospective stacked-model performance.

### C8. Table V gives practitioner guidance from a limited, partly exploratory 80-rule frontier panel.

**Classification:** Major missing justification  
**Location:** Sections IV.E–IV.F, pp. 5–7; Figure 2, p. 8; Table V, p. 9; Appendix A, pp. 10–11.

**Why it matters:** The table presents categorical advice (“use,” “none reliable”) that readers may treat as broadly established.

**Evidence or reasoning:** The frontier uses a fixed 80-rule subsample of the 160-rule radius-two hold-out panel, reduced simulation budgets, and several exploratory analyses. The learned reader and fairness controls include single-seed runs. The paper is commendably transparent about these restrictions, but the recommendation table is more categorical than the evidence warrants.

**What would resolve it:** Mark Table V as “exploratory guidance for the evaluated protocol and 80-rule panel.” Add uncertainty bands or confidence intervals at the grid-cell level, replicate the grid on an independent rule panel and across seeds, and distinguish “no estimator tested was reliable” from “no estimator is reliable.” Do not extrapolate the 3–15% noise recommendation beyond the exact corruption distribution, architecture, and training augmentation tested.

## D. Minor concerns and clarity issues

### Technical and statistical clarifications

1. **Define the four targets completely in the main text or a boxed notation block.** Section II.B and Appendix B use `ext(d)` and a recentered cone without giving a fully unambiguous formula for the left/right extent, the treatment of a single damaged cell, and the ring-coordinate convention. State why the denominators are nonzero after conditioning on survival. This is a **minor gap or ambiguity**.

2. **Avoid calling finite-horizon survival “the finite-horizon sign” of a maximal Lyapunov exponent.** On p. 3, damage survival is a finite-horizon protocol statistic and may be related to damage-spreading notions of Lyapunov behaviour, but it is not literally the sign of an asymptotic exponent without additional assumptions. Use “finite-horizon survival proxy” or a similarly qualified phrase. This is a **minor technical-language issue**.

3. **Specify the \(R^2\) convention.** State whether it is the standard \(1-\mathrm{SSE}/\mathrm{SST}\) score, whether the test-set mean is used in the denominator, how negative values are handled, and whether all four targets are standardized only for training or also for scoring. This is particularly important for the negative frontier values and median-over-target summaries.

4. **Clarify the ICC estimator under heteroscedasticity.** Section II.C acknowledges heteroscedasticity but still presents a one-way random-effects ICC formula. Explain whether the ICC is used descriptively despite a misspecified homoscedastic model, whether it is estimated by ANOVA or another method, and why its interpretation remains appropriate. This is a **likely correct but needs clearer exposition** issue.

5. **State the rule-orbit sampling measure precisely.** “Uniformly sampled canonical rules after orbit deduplication” (p. 2; Appendix B) can mean uniform over raw rule encodings followed by deduplication or uniform over symmetry orbits. These differ whenever orbit sizes differ. State the exact sampling algorithm and use the corresponding measure in the 7.8% prevalence claim. This is a **minor gap with implications for Figure 3**.

6. **Disentangle target noise from model uncertainty.** The paper reports CNN means and standard deviations over five seeds in Tables I–III, while several confidence intervals are rule-bootstrap intervals. Use labels that say which uncertainty source each interval includes. The current presentation makes it difficult to compare an interval with “mean ± s.d.” values.

7. **The compute comparison is not hardware-neutral.** Section IV.G compares a single-core CPU simulation time with a Metal-GPU forward-pass time. This is informative as a deployment vignette, but it is not a controlled cost comparison. Report batched CPU and GPU timings for both methods, batch size, timing variability, implementation language, and whether compilation/warm-up is excluded. Also distinguish the cost of training data generation from model fitting.

8. **Unknown-radius selection needs a procedure.** Section IV.F(i) states a “smallest-consistent rule” selection and reports an approximately 0.12 median-\(R^2\) cost. Give the candidate radius set, consistency criterion, tie-breaking rule, and behavior with contradictions under noise.

9. **The descriptor “independently validated” overstates the composed-system-map evidence.** Section IV.H uses independent random streams for local ground truth, which is good, but the 16-rule panel, validation-selected window, and inconclusive difference do not establish external validation. Rename this subsection to something like “descriptive by-products with independent ground-truth evaluation.”

10. **Avoid circular terminology around “signature-complex.”** The signature is a registered damage criterion, not independently established complexity. Calling a held-out group “signature-complex” is acceptable as shorthand only after defining it explicitly as a criterion label rather than a ground-truth behavioural class.

11. **Tighten several rhetorical claims.** Examples include “the best-posed of these” (p. 2), “a textbook instance” (p. 1), “almost always possible” (p. 1), “nothing direct beats reading it” (p. 1), and “the practical order of preference ... is unambiguous” (p. 4). These should be restricted to the observed protocol and tested methods.

12. **Clarify the status of prior-work claims.** The introduction correctly says it claims no novelty for the inverter. Still, the novelty argument depends on the breadth of the related-work search. The paper should distinguish (i) classic rule-identification algorithms, (ii) noisy/unknown-neighbourhood identification, (iii) modern learned inverse-CA or neural-CA identification, and (iv) benchmark papers that predict perturbation-defined behaviour directly from trajectories. A more systematic related-work table would support the claimed gap.

13. **Scope the undecidability statement.** The p. 1 wording should say that the cited work concerns a formalization of CA classification, not that every informal or finite-protocol behavioural classification problem is undecidable. The paper’s later move to protocol-indexed finite-horizon targets is sensible; the sentence should make that distinction explicit.

14. **Add immutable reproducibility metadata.** The Data Availability statement (p. 10) promises a timestamped archive, but the manuscript should provide an archival DOI/version, software environment, commit hash, license, expected hardware constraints, and a minimal script that regenerates Tables I–V and Figures 1–3. The current appendix helps, but reproducibility cannot be independently assessed from the manuscript alone.

### Proof and exposition review

The paper has a useful high-level roadmap in Section I, but its most technical arguments would benefit from visible “claim–assumptions–consequence” structure. There are no formal theorem/proof blocks, so the paper should not imply theorem-level necessity where it has an empirical observation or a conditional statistical identity.

The three places where readers are most likely to get lost are:

1. **The three reliability benchmarks (Section II.C, p. 3).**  
   The manuscript moves quickly from the random-effects decomposition to \(2\mathrm{ICC}-1\), then to a large-simulation reference. Add a one-panel schematic showing \(\theta\), cached target \(Y\), fresh simulation \(Y'\), and near-noise-free reference. State exactly which estimator is compared to which ceiling and why. Include the assumptions needed for the identity.

2. **The transition from exact tabulation to noisy Bayesian reconstruction (Sections III(i) and IV.F, pp. 3 and 5–6).**  
   A reader cannot reconstruct the likelihood or tell how conflicting transitions are resolved. Add pseudocode for clean tabulation, noisy deterministic decoding, and posterior simulation; then include a short worked radius-one example with one corrupted transition.

3. **The interpretation of Figures 1–2 and Table V (pp. 5–9).**  
   The figures combine different rule subsets, different Monte-Carlo budgets, frozen versus retrained networks, exact versus approximate reconstruction, and exploratory versus registered analyses. Add a table with one row per curve: rule panel, corruption mechanism, target simulation budget, model training distribution, number of seeds, and registration status. This would make the frontier substantially easier to trust and reproduce.

### Structure and narrative

The overall order—motivation, benchmark, estimators, results, discussion—is sensible. The main structural weakness is that Sections IV.G–IV.H introduce substantial secondary contributions after the central frontier result. The paper would read more coherently if it separated “primary benchmark evidence” from “secondary descriptive analyses.”

A revised section-level outline is recommended:

1. Introduction and precise scope of the claim.  
2. Protocol, estimands, reliability benchmarks, and evaluation unit.  
3. Estimators and exact algorithms.  
4. Primary matched-observation results.  
5. Degraded-observation frontier, with a complete corruption/method matrix.  
6. Robustness, compute, and sensitivity analyses.  
7. Secondary descriptive analyses: composed-system maps and signature landscape.  
8. Discussion, limitations, and reproducibility statement.

### Targeted line-level edits

- **Abstract, p. 1:** Replace “direct amortization can never beat it” with “in the matched regime, exact reconstruction removes the information advantage ordinarily claimed for direct amortization; whether a direct predictor is competitive then depends on simulation budget, training, and robustness.”

- **Introduction, p. 1:** Replace “which is almost always possible” with “which can be possible when the observed diagram exercises all local neighbourhoods under the assumed deterministic, synchronous model.”

- **Section II.C, p. 3:** Replace “This is the correct benchmark for the mechanistic estimator” with “This is the appropriate benchmark for a correctly identified rule followed by an independent simulation at the same Monte-Carlo budget, under the stated independent-additive-noise model.”

- **Section IV.A, p. 4:** Replace “statistically indistinguishable from having re-measured the ground truth itself” with “consistent, within the reported uncertainty, with an independent remeasurement at the same Monte-Carlo budget.” Retain the stronger wording only after a formal equivalence analysis.

- **Section IV.F(iii), pp. 6–7:** Replace “The result overturns one rev-9 conclusion” with “On this fixed 80-rule panel and single-seed control, the result reverses one rev-9 conclusion.” This preserves the substantive finding while matching the design.

- **Table V, p. 9:** Change “none reliable” to “no tested estimator was reliable on this grid under the stated reliability criterion.” This avoids a universal negative claim.

### Citations and scholarly practice

The bibliography is internally coherent at a high level and includes the classic identification and damage-spreading literature needed for the paper’s main framing. The following claims should nevertheless be checked against primary sources and, where needed, narrowed:

- The scope of the formal undecidability claim associated with Ref. [8].
- The precise task, data regime, and “99.9%” figure attributed to Ref. [6].
- The broad characterization of weak baselines in machine-learning-for-dynamics work attributed to Ref. [17].
- The claim that the present benchmark gap has not previously been measured; this requires a systematic search beyond the cited historical CA-identification references.
- The relationship between the proposed Bayesian decoder and prior noisy/probabilistic CA-identification methods, especially whether “Bayesian rule posterior” is genuinely a new formulation or a new empirical comparison.
- The literature ground truth used for the class-IV discussion of elementary rules and the wording around rule 106.

Do not rely only on a narrative related-work paragraph. A compact table of prior work—observation assumptions, known radius/neighbourhood, deterministic versus noisy CA, inference method, and target task—would make the novelty claim much more auditable.

### Reproducibility and empirical material

This section is applicable. The manuscript provides unusually useful seeds, architecture details, target budgets, and registration labels. However, the empirical work remains insufficiently reproducible from the paper alone because the prediction unit, noisy/masked data-generation process, degraded decoder algorithms, posterior approximation, CNN augmentation distribution, split construction, and several uncertainty calculations are not specified fully. The repository may resolve these issues, but it is not available for audit in the submitted manuscript. The paper should be self-contained enough that an independent group can implement the methods and reproduce the qualitative conclusions without reverse-engineering code.

## E. Questions for the authors

1. What exactly is one evaluation observation? Is each prediction made from one diagram, and if so, how are the 64 or 256 diagrams per rule used in Tables I–III and in the reconstruction-coverage percentages?

2. Are reported \(R^2\) values computed after averaging predictions across diagrams for each rule, or across rule-diagram observations? Please give the exact scoring formula and the bootstrap resampling unit.

3. How were the 57 signature-complex radius-two rules selected for force-holdout? Was membership determined independently of the target simulations and labels used to train or evaluate predictors?

4. What distribution does “uniformly sampled canonical rules” mean operationally: uniform over raw rules, uniform over symmetry orbits, or another procedure? How is the 7.8% prevalence estimate weighted?

5. Under bit-flip noise, how does the deterministic inverter choose a truth-table output when the same observed neighbourhood maps to both output values? What is the exact noise model at the diagram boundary and at \(t=0\)?

6. Is the Bayesian likelihood intended as the exact likelihood of the observed noisy space-time diagram, or as an entrywise pseudo-likelihood? What are the prior, epsilon-estimation criterion, and posterior-sampling details?

7. Was the reliability comparison between the mechanistic estimator and independent replicate agreement tested with a paired equivalence analysis? If not, can the authors provide one?

8. Can the authors report the direct estimators’ performance against the large-simulation reference, not only against the cached 256-pair target? This would clarify whether the learned models estimate the latent mean or are merely scored against noisy labels.

9. In Table IV, are folds grouped at the rule level and is the meta-model trained entirely within each cross-fitting fold? Is the 0.88 survival value intended as a deployable stacked-model result or as a diagnostic of complementary residual information?

10. How stable are the frontier conclusions over independent 80-rule panels and multiple random seeds for the degradation-trained CNN, learned reader, and ResNet18 control?

## F. Prioritized revision plan

1. **Essential before submission**
   - Correct the conceptual claim that direct amortization cannot beat a finite-budget identification-then-simulation estimator. Recast identification as an information-preserving baseline family, and distinguish fresh-simulation and latent-target comparisons throughout the abstract, introduction, results, and discussion.
   - Specify the prediction unit, diagram aggregation, \(R^2\) computation, coverage computation, split construction, and bootstrap procedure. These are necessary to evaluate the central “single diagram” result.
   - Fully define the noisy/masked reconstruction methods, including deterministic conflict resolution and the Bayesian likelihood or pseudo-likelihood. Add pseudocode and a worked example.
   - Reanalyse or relabel the radius-two “global” results to account for the force-held signature-complex rules. Provide representative and enriched-panel results separately.
   - Replace the informal “statistically indistinguishable” comparison with a paired, uncertainty-propagating benchmark comparison or weaken the language.

2. **Strongly recommended**
   - Repeat the main direct-model and frontier comparisons across outer rule splits and multiple training seeds. Present uncertainty that includes model-training as well as rule-sampling variability.
   - Evaluate direct estimators against the large-simulation reference and report both relevant ceilings in one table.
   - Clarify that Table IV is a complementarity diagnostic unless a stack trained only on the training rules is evaluated on untouched test rules.
   - Make Table V explicitly exploratory and protocol-bounded; add grid-cell intervals and replication on an independent rule panel.
   - Expand related work into a structured comparison table, with a focused literature check for recent inverse-CA and benchmark-design work.
   - Move the composed-system maps and damage-signature landscape into a clearly labelled secondary-results section or supplement.

3. **Optional polish**
   - Add a visual reliability schematic, a degradation-method matrix, and a one-page notation table.
   - Tighten rhetorical phrasing and qualify absolute statements.
   - Standardize terminology for “amortizer/amortiser,” “rule reader,” “mechanistic estimator,” and “signature-complex.”
   - Improve the compute section with hardware-neutral measurements and implementation details.
   - Add an archival repository DOI, pinned software environment, and a minimal reproduction command.

## G. Overall assessment

- **Technical soundness:** Uncertain  
- **Clarity:** Needs revision  
- **Novelty support:** Plausible but needs verification  
- **Completeness of proofs:** Gaps remain  
- **Submission readiness:** Needs major revision  
- **Confidence level in this review:** Medium  

The matched-observation empirical finding is plausible and potentially useful, and the reliability framing is promising. However, the strongest conceptual claim needs correction, while several indispensable details of the evaluation protocol and degraded reconstruction methods are missing. These are remediable, but they should be resolved before the paper is evaluated as a strong general benchmark-design contribution.
