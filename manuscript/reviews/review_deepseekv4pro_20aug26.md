Peer review: “Rule reconstruction from a single spacetime diagram yields simulation-limited prediction of the finite-horizon damage response of cellular automata”
Summary of the manuscript

The paper addresses an important benchmark-design question for data-driven analysis of cellular automata: when a single clean spacetime diagram is observed, can a learned model predict perturbation-defined damage statistics directly, or should one simply reconstruct the local rule and re-simulate the target? The authors formalize this as a comparison between an exact system-identification baseline and two direct amortized estimators. They introduce reliability ceilings based on independent replicate agreement and latent-target reliability, report errors in Monte-Carlo noise units, map identifiability failures under noise/masking/density changes, and test probabilistic and learned rule readers in degraded regimes.

The central empirical result is credible and useful: under matched, clean, complete observations, exact rule reconstruction is nearly perfect, and the reconstructed-rule simulator reaches the replicate-agreement benchmark by construction. The direct estimators, in contrast, fall well short, and much of their apparent skill on damage survival is mode assignment rather than within-band resolution. The paper is transparent about many limitations, pre-registration status, and post-hoc additions.

I think the work has the potential to be a valuable methods/baseline contribution. However, the manuscript is too long, sometimes overstates statistical exactness, and carries too much revision-history and secondary material. I recommend major revision.
Overall assessment

The strongest contributions are:

    The calibrated statement that read-then-simulate is exchangeable with an independent Monte-Carlo replicate under exact rule recovery.

    The distinction between the replicate-agreement ceiling and the latent reliability ceiling.

    The empirical demonstration that direct learned estimators are far from the simulation-limited baseline and partly behave as mode classifiers / nearest-training-rule lookup models.

    The identifiability frontier, showing where exact reconstruction stops and which estimator families dominate under degradation.

The weakest parts are:

    The main text is overloaded with revision labels (rev. 8, rev. 9, rev. 10, rev. 13) and response-to-reviewer language.

    Some secondary analyses—cost/break-even, annealed approximation, phenotype maps, localized-seed detector—add length but little to the core claim.

    A few statistical claims need qualification, particularly the “exact” ceilings for the proposed error metric.

    The main direct-estimator results appear not to use the improved checkpoint-selection protocol that later analyses recommend, which may handicap the learned baselines.

    The correctly specified decoder for noise is not implemented, so some noise-axis conclusions about the read-then-simulate family remain weaker than the abstract suggests.

Major comments
1. Clarify the observation model and diagram size in the main text

The abstract and Introduction repeatedly refer to a “single 127-cell diagram,” which is ambiguous. A single row of 127 cells would not identify a radius-two rule table. From the Appendix it becomes clear that the diagrams are actually 127×127127×127 spacetime diagrams: 127 time steps on a 127-cell ring.

Action: Replace “single 127-cell diagram” with “single 127×127127×127 spacetime diagram” or “single diagram of a 127-cell ring evolved for 127 time steps.” State the diagram height explicitly in the Benchmark section, not only in the Appendix.
2. The “exact” ρρ ceilings should be qualified

The paper defines
ρt=∑i(Y^ti−Y1,ti)2∑iσ^e2(t,i)
ρt​=∑i​σ^e2​(t,i)∑i​(Y^ti​−Y1,ti​)2​
​

and repeatedly states that the fresh-simulation reference is exactly 22
​ and the latent-mean reference exactly 11. This is true in expectation under an idealized additive-noise model if the denominator is known without error. Here the denominator is estimated from K=20K=20 replicates per rule, so σ^e2σ^e2​ is noisy, and the numerator and denominator are not strictly independent in all cases. The observed ρρ is therefore a ratio of random quantities; its sampling distribution need not be concentrated exactly at 22
​.

The mechanistic estimator’s bootstrap CI covering 22
​ is consistent with the claim, but the wording “exact” should be softened.

Action: State that 22
​ and 11 are expected/limiting reference values under the additive-noise idealization, and that finite-KK estimation of σ^e2σ^e2​ introduces additional variability. Alternatively, demonstrate via simulation or bootstrap that this variability is negligible for the panels used.
3. Main CNN results should use the improved checkpoint-selection protocol

The main matched-regime CNN results appear to be based on the original 60-epoch final-epoch weights. Later revision material reports that replacing final-epoch selection with validation-loss checkpoint selection substantially reduces seed variance and raises scores on degraded cells:

    “Clean-cell scores rise in step (0.43–0.55 against 0.29–0.51)…”

If checkpoint selection improves the CNN on the noise grid, it may also change the clean matched-regime numbers in Tables II–IV. The paper currently leaves the main direct-estimator results on the weaker training protocol while later using the improved protocol to make robustness claims.

Action: Re-run the main clean matched-regime CNN with the same checkpoint-selection protocol used in the revision-13 controls, and report those numbers. If the original final-epoch results are retained, justify why the improved protocol should not be used for the central comparison.
4. The noise-axis decoder is acknowledged to be misspecified; the claims should match that limitation

The pseudo-posterior decoder models output-side flips only. The authors explicitly state that input-side corruption is not modelled and that the correct decoder should marginalize over the latent clean diagram. This is an important limitation, especially because the paper argues that baselines must be constructed carefully.

Yet the abstract and some guidance statements may be read as stronger conclusions about the read-then-simulate family than the implemented decoder supports. The noise-band result—“beyond belongs to whichever estimator was trained for the corruption”—is really a property of the tested estimators and the misspecified pseudo-posterior, not necessarily of all read-then-simulate variants.

Action: Either implement a correctly specified latent-diagram decoder for bit-flip noise (e.g., a small factor graph with Gibbs sampling or EM), or explicitly downgrade the noise-axis claims. At minimum, add a prominent statement in the Discussion that the correct decoder remains untested and that the observed crossover should be interpreted as a bound for the evaluated estimators.
5. Panel construction and outcome-dependent force-holding need cleaner presentation

The radius-two test panel force-holds all signature-complex rules. The signature membership is computed from the same seed-0 target cache that supplies evaluation labels. This is not training leakage, because those rules are excluded from training, but it is outcome-dependent test-set selection. The authors partly address this with a stratified split and post-stratification, but the main tables still foreground the enriched panel.

For a paper whose contribution is methodological, the primary estimator comparison should perhaps use a representative split, with the enriched panel as a secondary analysis. The post-stratified rows are informative but currently buried in Table I.

Action: Make the representative or stratified split the primary result, and report the enriched panel as a sensitivity analysis. If the signature criterion depends on the evaluation target labels, state this limitation clearly in the main text and explain why it does not invalidate the mechanistic comparison.
6. The ρρ-metric statement “invariant to panel composition” is not correct

The text claims that ρρ is invariant to panel composition. It is independent of the between-rule signal strength that determines R2R2 ceilings, but it is not invariant to which rules are included: both numerator and denominator are sums over the selected rules, and the distribution of errors and Monte-Carlo variances can change with panel composition.

Action: Rephrase as “does not depend on the between-rule reliability/ICC in the way R2R2 does” or “has reference values independent of the panel’s between-rule variance,” rather than “invariant to panel composition.”
Secondary material that could be trimmed or removed

The manuscript is too long. The following sections are secondary and could be moved to supplementary material or shortened substantially:

    Cost/compute section (Sec. “Cost: accuracy versus compute”)
    The break-even analysis is interesting but not central. The exact runtime numbers on a single CPU/GPU are implementation-specific and quickly dated. A short paragraph is enough.

    Annealed approximation
    The result is negative and expected. It could be a brief remark in the Discussion.

    Phenotype maps for non-uniform CA
    The result is statistically inconclusive. It does not support the main thesis and could be removed from the main text.

    Damage-signature landscape and localized-seed detector
    The landscape is descriptive and not independently validated; the detector performs at chance. These are not needed for the main benchmark/frontier contribution. If kept, they should be in an Appendix, with the main text only summarizing the prevalence claim with its horizon caveat.

    Revision-history and reviewer-response language
    Phrases like “rev. 8,” “rev. 9,” “the fourth review,” and “revisions 7–13” belong in a response letter, not a journal manuscript. The pre-registration status can be described once in the Appendix without internal revision numbers.

Action: Remove or move these analyses, and remove all revision-number references from the main text. This would substantially reduce length and improve readability.
Minor comments and technical points

    Abstract is too dense.
    It tries to state all key results with notation and quantitative claims. Rewrite it in plainer language, introducing ρρ, ICC, and the ceilings only after defining them.

    Equation for exchangeability
    Equation (1) is correct conditional on exact recovery and stream independence. The paper should state the conditioning explicitly in the equation or immediately before it.

    “Agreement at the replicate benchmark follows by construction”
    This is true only for the exactly recovered subpopulation. For the 2.5%2.5% radius-two failures, the estimator is not exchangeable. The paper says the failures are benign, but the main statement should read “conditional on exact recovery.”

    Negative R2R2 values and medians
    The use of unfitted R2R2 is reasonable for held-out evaluation, but negative values can make medians and bootstrap CIs unstable. The paper handles this for some frontier cells but not consistently in all tables. State clearly when negative values are clipped or excluded.

    TOST audit of mechanistic equivalence
    The Appendix correctly notes this is an implementation audit, not a scientific test. The main text should not describe it as a substantive equivalence result.

    “Mode assignment” evidence
    The claim that survival skill is mode assignment is important. The main text reports intermediate-band R2R2, but the classification rates are only mentioned. Include the confusion-matrix numbers in the main text or a table, since this supports one of the central claims.

    Known-radius assumption
    The main matched model assumes known radius. The unknown-radius analysis is exploratory and shows a cost. This should be stated clearly in the Introduction and Discussion, because in real applications radius is often unknown.

    Use of “signature-complex” label
    The term is defined, but it is not a validated behavioural class. Avoid suggesting otherwise in figure captions or section titles.

    Pseudo-posterior calibration
    The paper reports empirical coverage of the posterior intervals, which is good. But the noise-axis calibration collapse is strong evidence that the posterior is overconfident. Make this more prominent in the main text rather than only in the frontier section.

    Replication panel
    The noise-axis replication on the complementary 80 rules is valuable. The masking/density axes were not replicated. This should be explicitly stated as a limitation.

Suggested future work

The Discussion already identifies the most important future direction: stochastic cellular automata such as Domany–Kinzel, where the generator is probabilistic and exact identification becomes estimation. That would test how far the read-then-simulate baseline extends along the determinism axis.

Other useful directions:

    Correctly specified Bayesian decoder for clean latent diagrams under observation noise. This is directly motivated by the current limitation and would strengthen the noise-axis conclusions.

    Learned system-identification pipelines with differentiable simulators in the loop. The paper shows that a small learned reader is weak; a jointly trained reader–simulator or table-posterior network would be a stronger direct baseline.

    Rule-scrubbing and rule-provision causal probes. The identity probes show rule information is present in the CNN bottleneck, but not whether the regression head uses it causally. Intervening on the bottleneck would be informative.

    A λλ-stratified or density-stratified radius-two sample. The authors already note that uniform sampling over encodings is a poor dynamical measure. A stratified sample would make prevalence and benchmark statements more relevant to interesting rules.

Recommendation

I recommend major revision.

The core idea is sound, the reliability-aware benchmark is a genuine contribution, and the matched-regime conclusion is convincing within its stated assumptions. However, the manuscript needs:

    clarification of observation dimensions;

    qualification of “exact” statistical ceilings;

    re-evaluation of the main CNN with the improved checkpoint-selection protocol;

    a stronger or explicitly weaker treatment of the noise decoder;

    removal of revision-history language and substantial trimming of secondary material;

    a clearer primary panel and more careful wording about outcome-dependent selection.

If these are addressed, the paper could become a useful, calibrated reference for fair baselines in data-driven CA analysis.