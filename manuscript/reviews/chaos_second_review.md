# Second review: **major revision required**

**Manuscript:** *Reading the rule beats learning it: interpretable estimators dominate deep networks for the finite-horizon damage response of cellular automata*  
**Recommendation:** Major revision before the work can be considered for publication. The revision is substantially stronger than the prior version and now contains the core of a potentially valuable paper, but several central claims remain unsupported, internally inconsistent, or stated too broadly.

## Overall assessment

This is a markedly improved manuscript. The authors have addressed several of the most consequential weaknesses of the earlier version:

- They now use the correct language of **finite-horizon, protocol-dependent damage-response statistics**, rather than calling these quantities invariants.
- They introduce the most important missing comparator: a mechanistic estimator that reconstructs the deterministic local rule from the observed diagram and simulates the stipulated perturbation experiment.
- They attempt a meaningful reliability analysis using repeated target estimates.
- They test whether the CNN representation contains rule information, and appropriately acknowledge that the proposed “anti-shortcut” architecture does not actually prevent rule recovery.
- They move beyond a four-target median by discussing target-specific behavior and add paired comparisons and a cross-fitted stacking analysis.
- They make the radius-two “complexity” claim substantially more cautious and now acknowledge that their independent glider detector agrees poorly with the damage-signature criterion in the large rule space.
- They improve the spatial-map experiment by introducing a composed-system perturbation ground truth and by stating that the handcrafted window is selected on validation data rather than per test pair.

These are real advances. The best version of this work is no longer “five hand-crafted features rival a CNN.” It is instead a much sharper and more interesting claim:

> Under a fully observed, deterministic, synchronous, binary one-dimensional CA model with known neighborhood radius, a typical finite space–time diagram identifies nearly all entries of the local rule table. Once that system-identification problem has been solved, direct simulation provides an essentially optimal estimator of the stipulated finite-horizon response statistic.

That result is useful, interpretable, and relevant to the shortcut-learning literature. It also provides a strong warning about benchmark design: a nominally “single-diagram amortization” task can be nearly solved by reconstructing the generator encoded in the observation.

Unfortunately, the present paper still overstates what its experiments establish. The central comparison between the CNN and the five-statistic baseline is internally contradictory; the reliability “ceiling” is not applied correctly to an estimator based on an *independent finite Monte Carlo simulation*; several statistical claims lack the necessary tables, intervals, and split-level information; and the main conclusion continues to generalize from one deliberately constrained CNN and one extremely favorable observation regime to “deep networks” more broadly.

I would encourage a substantial revision rather than abandonment. With a clearer scope, correct statistical treatment, and a more explicit identifiability study, this could become a strong paper.

---

## 1. The central narrative is internally inconsistent

The manuscript repeatedly states that the deep CNN “never beats” the five cheap statistics, that the methods form “three tiers, one ordering,” and that the learned model has only a “modest” edge on survival. The numerical tables do not support these formulations.

In Table I:

- On radius-two global prediction, the CNN median $R^2$ is **0.864**, versus **0.845** for the five statistics.
- On the held-out radius-two complex subset, the CNN median $R^2$ is **0.832**, versus **0.795** for the five statistics.

Thus, at the reported median-summary level, the CNN *does* outperform the five-statistic baseline in two of the three rows. The Table I caption’s assertion that the CNN “never beats five cheap statistics” is simply false as written.

More importantly, Table III reports that adding CNN predictions to the five-statistic model yields an incremental $R^2$ of **+0.32 for damage survival**, with smaller positive increments for fraction and spreading rate. This is not evidence that the CNN adds nothing. It is evidence of material complementarity, at least for survival. Conversely, the five statistics add essentially nothing beyond the CNN in the reported stacking analysis. That is a scientifically interesting finding and should not be rhetorically minimized.

The defensible conclusion is more nuanced:

- **Rule reconstruction plus simulation dominates the direct estimators under the stated observation model.**
- **The five-statistic and direct-CNN estimators do not admit a stable global ranking.**
- **The CNN appears to add information beyond the five statistics, especially for damage survival, even if it does not independently approach the mechanistic estimator’s accuracy.**

The title, abstract, Results heading “Three tiers, one ordering,” Table I caption, Discussion, and final recommendation should be revised accordingly. The current claim that readers should “compute the cheap features and skip the network” is not supported by the paper’s own stacking result. Where direct rule reconstruction is unavailable or unreliable, the natural practical recommendation is to test a **statistics + CNN hybrid**, particularly for survival-like rare-event targets.

A more accurate title would emphasize the demonstrated result rather than an overbroad contrast with learning, for example:

> **Rule reconstruction reaches the simulation-limited accuracy for finite-horizon damage-response prediction in deterministic cellular automata**

The direct CNN can then be presented as a complementary but inferior estimator under the tested protocol.

---

## 2. The reliability ceiling is not the correct ceiling for the stated mechanistic estimator

This is the most important technical issue in the revision.

The manuscript estimates an ICC from repeated Monte Carlo target estimates and treats this ICC as the achievable-$R^2$ ceiling. That interpretation is appropriate only for a predictor that estimates the *latent, noise-free target mean* sufficiently accurately. It is not automatically the appropriate benchmark for the mechanistic estimator as described.

The mechanistic estimator reconstructs a rule and then estimates the damage-response statistic by running an **independent finite Monte Carlo simulation** under the same protocol. Let

\[
Y_1 = \theta + \varepsilon_1
\]

be the cached target estimate and

\[
Y_2 = \theta + \varepsilon_2
\]

be an independent mechanistic estimate, with equal independent Monte Carlo error variances. Under the usual additive-noise approximation, the expected direct predictive $R^2$ of using $Y_2$ to predict $Y_1$ is not the ICC. It is approximately

\[
1 - \frac{2\sigma_e^2}{\sigma_\theta^2+\sigma_e^2} = 2\,\mathrm{ICC}-1.
\]

By contrast:

- A hypothetical predictor that returns the latent $\theta$ has a ceiling of approximately $\mathrm{ICC}$.
- An independently simulated finite-sample estimate has a lower replicate-agreement ceiling.
- A calibrated predictor based on another noisy replicate can have still another expected $R^2$, depending on the regression/calibration convention.

The exact expression depends on the evaluation $R^2$ definition, heteroscedasticity, conditional targets, and the number of Monte Carlo pairs used in the mechanistic simulator. But the present presentation conflates these distinct quantities.

This matters because the reported numbers are consistent with this concern. For example, an ICC of 0.994 implies a same-precision independent-replicate benchmark of approximately $2(0.994)-1 = 0.988$, which is much closer to the reported mechanistic survival score of 0.985 than the manuscript’s stated ICC ceiling of 0.994.

### Required revision

The authors should replace the current single “reliability ceiling” with three explicitly distinguished quantities:

1. **Latent-target reliability:** the proportion of observed target variance attributable to between-rule variation.
2. **Independent-simulation agreement:** the expected performance of a second Monte Carlo estimate using the same number of perturbation pairs as the mechanistic estimator.
3. **Large-simulation reference ceiling:** the performance relative to a near-noise-free reference target estimated with many more pairs, if computationally feasible.

The cleanest empirical solution is to use the existing $K=20$ replicates to report an empirical replicate-versus-replicate benchmark for every target and rule space. Then compare the mechanistic estimator directly against that benchmark. If the mechanistic estimator uses a different number of pairs than the cached target, report the corresponding simulation-precision curve.

The paper should also report uncertainty in the ICC and in each ceiling estimate. Survival and the conditional-on-survival targets are likely heteroscedastic and non-Gaussian; a one-way Gaussian random-effects model may be only an approximation. A hierarchical binomial/Beta-binomial or bootstrap-based reliability analysis would be more defensible for survival, while conditional statistics need explicit treatment of the varying number of surviving trials.

Until this issue is corrected, the phrase “reaches the Monte-Carlo reliability ceiling” is too strong and potentially mathematically incorrect.

---

## 3. The mechanistic estimator is highly informative, but its privileged assumptions must be made explicit

The mechanistic estimator is the paper’s strongest contribution. It should also be described honestly as a **matched-model system-identification estimator**, not as a generic transparent baseline.

It assumes that the observer knows, or is supplied with:

- that the process is a deterministic cellular automaton;
- that updates are synchronous and time-oriented in the observed direction;
- the binary state coding;
- the neighborhood radius;
- the neighborhood geometry;
- full, noiseless states at every observed cell and time;
- the update rule is spatially uniform;
- the target protocol, including width, boundaries, perturbation model, and initial-condition distribution.

Under those conditions, a $127 \times 30$ or $127 \times 62$ diagram contains thousands of local transitions. Recovering a 32-bit rule table should often be easy. This is not a weakness; it is the central scientific point. But it means the manuscript should frame the method as **system identification under matched structural assumptions**, rather than implying that it is a generally available alternative whenever one has a space–time image.

### The default-zero completion is an unacknowledged prior

For unobserved neighborhood transitions, the method defaults the rule-table entry to zero. This is not parameter-free or neutral. It is a strong prior over unobserved transitions, and it can bias the reconstructed rule and the simulated response. The fact that only 2.5% of sampled radius-two rules are not recovered exactly does not remove the issue, because the failures may be systematically concentrated among low-activity, complex, or otherwise atypical rules.

The authors should:

- report the distribution of observed rule-table coverage, separately by rule space, target stratum, and outcome class;
- report the number of missing entries for every failed reconstruction;
- compare default-zero, default-one, empirical-prior, and posterior-averaged completions;
- avoid calling the estimator parameter-free unless the completion rule is eliminated or fully justified;
- preferably treat unobserved entries as unknown and propagate the resulting uncertainty through simulation.

For radius two, a Bayesian completion is feasible. If $k$ entries are unobserved, there are $2^k$ possible completions; for small $k$ they can be enumerated exactly, and for larger $k$ they can be sampled. This would turn an arbitrary default into an uncertainty-aware mechanistic estimator. It would also yield calibrated confidence intervals, which are especially valuable in precisely the cases where rule reconstruction fails.

### Required experiment: an identifiability curve

The manuscript should quantify the rule-identification regime rather than merely report a single recovery percentage. Vary:

- diagram width;
- number of time steps;
- initial-condition density;
- initial-condition correlation length;
- partial observation rate;
- observation noise;
- state-label noise;
- unknown versus known radius;
- spatially uniform versus weakly nonuniform rules.

For each setting, report rule-table coverage, exact-reconstruction rate, mechanistic target accuracy, CNN accuracy, and five-statistic accuracy. This would produce the paper’s most informative figure: an **identifiability phase diagram** showing when “read the rule” is possible, when a rule-posterior simulator is needed, and when direct amortization may have an advantage.

That analysis would transform the work from a narrow benchmark into a general lesson about observability and shortcut structure in dynamical-system learning.

---

## 4. The paper does not “prove” why the CNN fails

The paper says that it “proves the mechanism” and attributes the CNN’s limitations to rule readability. The current evidence is suggestive but not a proof.

The linear probes establish that rule information is recoverable from the bottleneck. They do **not** establish:

- that the CNN uses this information in the direct regression head;
- that rule information causes its performance pattern;
- that its inferior performance is not partly due to architecture, capacity, optimization, training duration, or data scale;
- that an alternative learned system-identification architecture could not approach the mechanistic estimator.

Similarly, the fact that a deterministic rule-reconstruction route exists does not entail that “any statistic that is a smooth function of the rule” is recovered by the cheapest available representation. Damage-response functions on a discrete rule space need not be smooth, and the relevant fact here is simpler and stronger: once the exact rule is known, the finite-horizon target can be directly simulated.

The manuscript should replace “prove” with language such as “demonstrate,” “identify a sufficient mechanistic explanation,” or “provide evidence that rule identifiability is the dominant factor under this protocol.”

### Stronger causal tests

The authors can substantially strengthen this section with interventions:

1. **Rule-scrubbing experiment.** Train a representation with an adversarial or information-bottleneck objective that suppresses decodable truth-table information, then test whether direct damage-response prediction changes.

2. **Rule-provision experiment.** Provide an inferred rule table explicitly to a small neural predictor or differentiable simulator. This separates the ability to identify the rule from the ability to map rule to response.

3. **Learned rule-reader + simulator.** Train a model to predict the local rule table from a diagram, then simulate from the predicted rule. Compare this hybrid to both direct CNN regression and deterministic table reconstruction.

4. **Controlled observability degradation.** As diagram length, noise, or partial observability increase, test whether the direct CNN becomes relatively more useful precisely when exact rule reconstruction becomes unreliable.

These experiments would support a causal story rather than a post hoc interpretive one.

---

## 5. The representation-probe results need far more definition

The probe claims are potentially important but presently ambiguous.

The manuscript states that a linear probe recovers rule “identity” from the 64-dimensional bottleneck at balanced accuracy 0.88 for ECA and 0.95 for radius two, and recovers individual truth-table entries of unseen rules at 0.78/0.61. Several details are indispensable:

- What is the number of classes in the rule-identity probe?
- Are the probe’s train and test rules disjoint?
- Is the CNN itself trained on the same rule identities used by the probe?
- Are probe data independent diagrams from the same rules, or diagrams from previously unseen rules?
- What exactly does “identity of unseen rules” mean when the identity classifier has not seen those classes during training?
- What is the chance and majority-class performance for each probe?
- Are truth-table bits evaluated separately, jointly, or averaged?
- Are confidence intervals computed over rules, bits, diagrams, or probe resamples?
- How does performance compare to the deterministic tabulation method under the same partial-observation settings?

The reported radius-two “identity” performance is particularly difficult to interpret without this information. A linear classifier cannot classify genuinely unseen identities unless the task is actually a different property-prediction problem. The paper should distinguish clearly between **within-rule decoding across new diagrams** and **out-of-rule generalization to truth-table entries**.

A useful figure would show, for raw diagrams, CNN bottlenecks, and five statistics:

- exact rule-table recovery probability;
- per-bit balanced accuracy;
- fraction of rule-table entries observed;
- target-prediction performance.

This would connect representational accessibility to the actual task in an interpretable way.

---

## 6. The statistical analysis is improved but still incomplete and occasionally misused

The move toward rule-level bootstrap comparisons and TOST-style equivalence is welcome. However, the manuscript does not yet provide enough information for a reader to verify the conclusions.

### Per-target results are required for all tasks

Table II reports per-target values only for ECA and only for a single “reference seed” CNN. The central claims about radius-two global prediction, complex-rule placement, survival, and stacking require the corresponding raw per-target radius-two results. The paper needs a complete table, for every task and target, containing:

- held-out rule count;
- $R^2$ for each method;
- bootstrap confidence interval;
- CNN mean and distribution across seeds;
- paired $\Delta R^2$ and interval;
- superiority/equivalence/inconclusive classification;
- relevant reliability or replicate-agreement benchmark.

The current Table I medians obscure exactly the differences that the revised manuscript now argues are important.

### Fixed split plus bootstrap is not enough

The manuscript appears to rely on one preregistered split, with 18 held-out ECA rules and 160 held-out radius-two rules. A bootstrap over the held-out rules quantifies uncertainty conditional on that split and the trained models. It does not quantify variation due to:

- the training-rule panel;
- validation/hyperparameter selection;
- the particular holdout split;
- CNN initialization and optimization;
- sampled radius-two rule panel.

For ECA, the obvious solution is repeated orbit-respecting cross-validation or leave-one-orbit-out prediction over all 88 representatives. For radius two, use repeated outer splits or repeated independently sampled panels, with all tuning nested within each training set. The unit of statistical inference should be the held-out rule, but the resampling hierarchy should include the outer split and the CNN seed.

Five seeds are currently shown mainly as a standard deviation in Table I. That is not sufficient. Seed effects should be incorporated into the uncertainty analysis or reported as a distribution across independently trained models, not reduced to a decorative $\pm$ value.

### TOST and “tie” language must be used consistently

The manuscript defines practical equivalence as a 90% interval entirely contained in $(-0.05,+0.05)$. Yet the spatial-map result is called a “tie” despite reporting a 95% interval of $[-0.002,+0.10]$ for the difference. That is not evidence of equivalence under the manuscript’s own criterion; at best it is **inconclusive**. The 90% interval may also exceed +0.05, but it is not reported.

The authors should reserve “equivalent” or “tie” for cases that pass the preregistered equivalence test. Otherwise write “no statistically resolved difference under the available sample size.”

### The practical margin needs justification

A fixed $\delta=0.05$ in $R^2$ may be reasonable, but the manuscript should justify why it is practically meaningful for all four targets, including survival with a lower effective reliability. A more interpretable sensitivity analysis would repeat conclusions across several plausible margins, for example 0.02, 0.05, and 0.10.

---

## 7. The direct CNN is not shown to represent “deep networks” generally

The paper evaluates one deliberately constrained convolutional amortizer, trained for 60 epochs, with a specific first-layer kernel, bottleneck, BatchNorm choice, and linear head. Five random seeds do not turn this into evidence about deep networks as a class.

This limitation is particularly important because the architecture was intentionally designed to impede one route to local-rule recovery. The probe results then show that it does not fully impede that route, but the manuscript never establishes that this model is reasonably optimized for direct response prediction.

The paper should either:

1. narrow all claims to **this anti-shortcut CNN configuration**, or  
2. include a modest but credible model suite.

A useful suite need not be extravagant. It could include:

- a standard CNN with a receptive field explicitly large enough to read local transitions;
- a multiscale/dilated temporal CNN;
- a recurrent or causal temporal convolutional model;
- a learned rule-table predictor followed by simulation;
- a rule-table-input MLP or neural simulator;
- the existing direct CNN;
- the five-statistic ridge and GBM baselines;
- the deterministic rule-inference simulator.

This would identify whether the relevant distinction is **direct regression versus generator reconstruction**, not simply “deep versus simple.” It may also reveal that a learned system-identification pipeline approaches the deterministic estimator when exact table extraction is made difficult.

At a minimum, provide architecture diagrams, parameter counts, receptive fields by layer, optimization details, validation selection, learning curves, and ablations over training length and bottleneck dimension.

---

## 8. The spatial-map result remains promising but does not yet establish the stated conclusion

The revised local perturbation ground truth is a major improvement. However, the spatial claim is still too strong.

First, the quoted result, Spearman 0.67 versus 0.61 with $\Delta=+0.05$ and 95% CI $[-0.002,+0.10]$, is not an equivalence finding. It is compatible with no difference, but also with a potentially meaningful CNN advantage. The manuscript’s own equivalence framework would label it inconclusive unless the appropriate 90% interval lies wholly within the prespecified margin.

Second, the text calls the sliding handcrafted regressor “training-free,” while the method has previously been described as a trained ridge/GBM regressor on five statistics. A pretrained regressor may require no additional training at deployment, but it is not training-free. This terminology should be corrected.

Third, the experiment needs enough detail to evaluate whether the comparison is fair:

- How many mosaics, rule pairs, stripe periods, and replicates are evaluated?
- Are rule pairs and mosaics disjoint across training, validation, and test?
- Is the window width selected globally on validation data, separately by target, or separately by architecture?
- Are correlations computed over all columns, only stripe interiors, or also interfaces?
- How are spatially correlated columns handled statistically?
- Is the local ground truth computed with independent random streams?
- What happens for random mosaics, graded mixtures, irregular interfaces, and weakly nonuniform rule fields?

The appropriate unit of resampling is likely the **mosaic/composed system**, not individual columns. Bootstrap intervals based on columns would be severely anti-conservative because adjacent outputs share local dynamics.

Finally, the mechanistic contribution should be extended to the spatial setting. In a nonuniform CA, it may be possible to infer a local rule table from local transitions, construct a local posterior over rules, and simulate local perturbations. Comparing such a **local system-identification map** to the direct CNN and feature-window maps would be much more aligned with the paper’s central thesis.

---

## 9. The radius-two “complex behavior landscape” should be framed as a damage-signature landscape, not a complexity map

The revision deserves credit for explicitly acknowledging that the independent localized-seed glider detector agrees with the damage signature on only 47% of radius-two rules, and for withdrawing the claim that 7.8% of radius-two rules are validated glider-supporting rules.

Nevertheless, the abstract and Discussion still describe a “map of where complex behaviour lives.” That language is not defensible given the reported disagreement. The 7.8% number should be called exactly what it is:

> the estimated prevalence of a preregistered **finite-horizon damage-signature criterion** under the stated radius-two sampling distribution.

The figure can remain useful, but its title and caption should use “damage-response landscape” or “damage-signature landscape.” The red region should not be presented as a glider or class-IV region without independent validation.

The ECA validation also needs a proper confusion matrix. Reporting 92% agreement on a dataset with only a few positive rules is potentially misleading because raw agreement is dominated by negatives. Report:

- number of positives and negatives;
- sensitivity/recall;
- specificity;
- precision;
- balanced accuracy;
- F1 score;
- exact detector settings;
- detector failure modes.

The statement that rule 54 is missed because its ether front propagates at light speed is scientifically interesting. It should motivate a more robust detector that combines localized propagation, periodicity, localization, persistence, and collision behavior rather than relying on a single observable.

For radius-two rules, consider a smaller but carefully curated validation sample: long-horizon simulations, multiple initial conditions, blinded expert scoring, and at least two independent automated detectors. That would allow the paper to characterize the damage-signature criterion’s precision and recall rather than merely its apparent frequency.

---

## 10. The preregistration and reproducibility claims remain unauditable during review

The manuscript continues to rely heavily on preregistration as a warrant for the interpretation of negative or mixed findings, while stating that code, data, and the repository will be released only upon publication.

That is insufficient for a paper whose central methodological claim is preregistration. The preregistration should be available to editors and reviewers now, ideally as an anonymized immutable archive with a timestamp and commit history. It should include:

- the original analysis plan;
- exact planned rule panels and splits;
- thresholds and decision rules;
- all changes and deviations;
- the date at which the mechanistic estimator, ICC analysis, probes, stacking test, glider detector, and spatial ground truth were added;
- code and configuration files sufficient to reproduce all tables and figures;
- cached predictions and targets, not only final summaries.

This is especially important because many of the most valuable additions in the revision were absent from the prior version. They may be entirely legitimate additions, but they cannot automatically be described as preregistered primary analyses. The paper should label analyses as **registered**, **post hoc but confirmatory on new data**, or **exploratory**. Transparency here will increase, not diminish, the paper’s credibility.

---

## 11. Accuracy is not the only utility criterion: report the compute and deployment trade-off

The mechanistic estimator is likely preferable on accuracy under the matched model. But it must reconstruct the rule and run a Monte Carlo perturbation simulation for each new observation, whereas a trained CNN may produce an approximate answer in one forward pass.

The manuscript recommends “read the rule” without reporting the cost of doing so. A fair practical comparison should report:

- wall-clock latency per diagram;
- CPU/GPU requirements;
- number of Monte Carlo pairs used by the mechanistic estimator;
- memory use;
- one-time CNN training cost;
- break-even number of deployment queries;
- accuracy versus compute curves as the mechanistic simulation budget varies.

This matters especially if the intended use is rapid large-scale screening of many diagrams. It may turn out that the mechanistic method remains both faster and more accurate, which would strengthen the paper. But that should be demonstrated rather than assumed.

---

## 12. Missing methodological detail still prevents full assessment

The main text or a detailed supplement must provide the following:

- exact number of diagrams per rule for training, validation, and testing;
- independence of observed diagrams and target-estimation streams;
- whether target simulations share any random numbers across methods;
- full CNN architecture, including all layers, strides, channels, activations, pooling, parameter count, and receptive field;
- optimizer, learning-rate schedule, batch size, regularization, augmentation, model selection, and early-stopping policy;
- ridge and GBM hyperparameters and the procedure used to select the “baseline of record”;
- the exact outer/inner split protocol;
- the number and identity of radius-two rules in every panel;
- whether the 800-rule estimator panel and 3,000-rule landscape panel overlap;
- exact formulas for damage fraction, cone extent, cone fill, and conditional aggregation;
- perturbation-cell selection;
- treatment of cases with no surviving damage in conditional targets;
- exact definition of the glider detector;
- exact construction of the spatial composed systems;
- all confidence intervals and significance/equivalence decisions.

The paper is currently too short to contain all of this. A comprehensive supplement and public repository are necessary.

---

# Recommended experiments and analyses, in priority order

## Essential before the main conclusion can be accepted

1. **Correct the reliability benchmark.**  
   Report latent reliability, empirical independent-replicate agreement, and method accuracy against a large-simulation reference where possible.

2. **Repair the CNN-versus-statistics narrative.**  
   Provide complete per-target radius-two results and intervals. Replace “never beats,” “three tiers,” “only modest edge,” and “skip the network” with conclusions consistent with Tables I and III.

3. **Make the mechanistic estimator uncertainty-aware.**  
   Report coverage and missing-entry distributions; test completion policies; ideally propagate uncertainty over unobserved rule-table entries.

4. **Provide repeated outer-split evaluation.**  
   Use orbit-respecting cross-validation for ECA and repeated independently sampled radius-two panels or outer splits. Include seed uncertainty in the inference.

5. **Release a review-accessible preregistration and reproducibility archive.**  
   Clearly distinguish original preregistered analyses from revised or exploratory analyses.

## High-value experiments that would make the paper much stronger

6. **Build an identifiability phase diagram.**  
   Vary observation length, width, noise, partial observability, initial-condition distribution, and knowledge of radius. Compare all estimators across this grid.

7. **Compare direct regression with learned system identification.**  
   Add a learned rule-table predictor followed by a simulator, and compare it with deterministic table reconstruction and direct CNN regression.

8. **Test whether rule information causally explains CNN behavior.**  
   Use rule-scrubbing, explicit rule provision, or controlled observation degradation.

9. **Report an accuracy–compute Pareto analysis.**  
   This is needed to justify a practical recommendation in favor of the mechanistic estimator.

10. **Strengthen the spatial benchmark.**  
    Use composed-system-level resampling, additional mosaic types, detailed protocols, and a local mechanistic estimator. Do not call the current result a tie unless it passes the declared equivalence test.

11. **Recast and validate the landscape analysis.**  
    Rename it a damage-signature landscape; provide confusion matrices for ECA; use a curated long-horizon radius-two validation set if the manuscript wishes to discuss glider-like complexity.

---

# Minor and editorial comments

1. The abstract’s slash notation for performance values, for example “0.93/0.85” and “0.85/0.86,” is difficult to parse without immediately stating which value corresponds to which rule space.

2. Table I should not describe the CNN as never beating the five statistics when its reported medians are higher in the two radius-two rows.

3. Table II should not report a single “reference seed” CNN unless all seeds are displayed in a supplement and the reason for selecting that seed is justified. Use seed means, intervals, or a hierarchical analysis.

4. Table III needs confidence intervals, corrected significance annotations, and a precise definition of incremental $R^2$. The reader should see the performance of the full stacked model, not only the increment.

5. Avoid saying that the mechanistic estimator is deterministic “given the protocol” if it uses a finite pseudorandom simulation stream. It is reproducible under a fixed seed, but its scientific estimate remains Monte Carlo limited.

6. Replace the phrase “smooth function of the rule.” No smoothness assumption is needed for the mechanistic argument and the claim is not established.

7. The companion sensitivity analysis mentioned in the Scope paragraph should either be included, cited, and accessible, or removed from the main claim.

8. The title and text should make “known radius” and “fully observed deterministic binary CA” visible earlier. These assumptions are essential to the result.

9. The citations to the two damage-spreading papers remain incomplete. Provide full bibliographic information and stable identifiers.

10. Figure 1 should display uncertainty or sampling-density information, define all labeled rules in the caption, and avoid any visual implication that the red band is an independently verified glider region.

11. The manuscript should consistently distinguish “no evidence of superiority,” “practical equivalence,” and “inconclusive.” These are not interchangeable.

---

# Final recommendation

The revised work is materially better and contains a potentially strong contribution. The mechanistic estimator is the right idea, and the paper’s most important scientific message is the observability of the local generator from a nominally single observation. That message could be valuable to readers of *Chaos* and to researchers building machine-learning benchmarks for deterministic dynamical systems.

However, the present version is not ready for acceptance. The reliability analysis requires correction, the CNN-versus-statistics conclusions must be rewritten to match the results, the mechanistic method’s structural assumptions and arbitrary completion policy need to be exposed and tested, and the preregistration/reproducibility claims must become auditable. The spatial and landscape claims also need more careful statistical language.

A thoroughly revised manuscript centered on **rule identifiability, simulation-limited prediction, and the regimes in which that shortcut breaks down** would be much stronger than the current broad claim that interpretable estimators “dominate deep networks.”
