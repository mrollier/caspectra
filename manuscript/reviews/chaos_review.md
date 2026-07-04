# Review of “Simple single-diagram statistics rival deep networks for estimating the dynamical invariants of cellular automata: a pre-registered benchmark”

## Recommendation: Reject in current form

This review concerns the submitted manuscript, *“Simple single-diagram statistics rival deep networks for estimating the dynamical invariants of cellular automata: a pre-registered benchmark.”*

The question is worthwhile: whether learned representations genuinely outperform transparent, low-dimensional descriptors for CA dynamics is important, and negative results can be valuable. The manuscript also makes several sensible methodological choices, including rule-level holdout, an explicit finite observation protocol, a simple-feature benchmark, symmetry considerations, and an attempt to quantify target-estimation noise.

However, the paper’s central conclusion is far stronger than its evidence permits. At most, the presented results suggest that one narrowly constrained CNN does not surpass one carefully selected five-feature baseline for four finite-horizon, protocol-dependent damage-response statistics under a single random-initial-condition distribution. They do not establish that “deep networks” add no value, that the result is structural, that shortcut learning has been prevented, or that complex/glider-supporting behavior occupies 7.8% of the radius-two rule space. The manuscript is currently too under-specified, statistically incomplete, and conceptually overclaimed for publication in *Chaos*.

## Major concerns

### 1. The claimed “anti-shortcut” architecture is not demonstrated to prevent rule recovery.

The key methodological assertion is that a 2 × 2 first-layer kernel cannot directly read an ECA transition, unlike a 3 × 2 patch. But this does not establish that the full network cannot recover the rule. Stacked 2 × 2 layers rapidly acquire a receptive field spanning the required neighborhood-time structure; subsequent layers, pooling, nonlinearities, and the 64-dimensional bottleneck may still encode rule-table information. The argument addresses one direct first-layer mechanism, not shortcut access in the actual model.

This omission is central because the manuscript’s own interpretation depends on rule readability. The authors must empirically test it. At minimum, they should train probes on frozen representations to predict ECA rule identities, individual radius-two truth-table entries, and rule-family properties. They should compare rule recoverability from raw diagrams, intermediate CNN layers, the bottleneck, and the five handcrafted features. Without this, the model cannot credibly be described as “anti-shortcut,” and the causal interpretation of the benchmark collapses.

A stronger design would include an explicit adversarial objective that removes recoverable rule information, followed by independent probing to verify that the representation is actually rule-invariant.

### 2. The paper confuses failure to clear an arbitrary superiority threshold with evidence of equivalence.

The preregistered condition requires a median held-out R² advantage of at least 0.10 on at least three of four targets. Failure to meet that condition does not demonstrate “no advantage,” “rivalry,” or equivalence. It only demonstrates that this particular superiority criterion was not met.

The manuscript needs a proper equivalence or non-inferiority analysis. This requires a justified practical-equivalence margin, paired uncertainty intervals for the performance difference, and a clearly defined unit of resampling. Reporting the CNN’s seed-to-seed standard deviation while treating the baseline as deterministic is inadequate. The relevant uncertainty includes held-out rules, outer splits, finite target-estimation noise, sampling of radius-two rules, and model fitting.

Table I is especially insufficient. It reports a single summary score, apparently a median across four targets, but omits each target’s performance, confidence intervals, test-set size, split composition, and paired differences. A model could improve substantially on one scientifically important invariant while losing slightly on others; the current summary would obscure that outcome.

### 3. The statement that Monte Carlo noise “upper-bounds achievable R²” is not justified as written.

A per-feature target-estimation noise range of approximately 0.006–0.014 does not by itself yield an R² ceiling. The ceiling depends on the signal variance of each target across rules, the distribution and heteroscedasticity of the error, and whether the reported targets are conditional quantities. Reliability-adjusted performance requires repeated independent target estimates per rule and an explicit variance decomposition or intraclass-correlation analysis.

This is particularly important for damage survival and conditional-on-survival quantities. Rare survival events can generate highly non-Gaussian, heteroscedastic uncertainty, which cannot be summarized convincingly by a single residual-noise range. The authors should generate independent Monte Carlo target replicates, quantify reliability separately for each invariant, and report reliability-adjusted performance with uncertainty.

### 4. The experimental design is far too incompletely described to be reproducible or interpretable.

Critical information is absent:

- Number of training, validation, and test rules in each task.
- Number of diagrams per rule and whether diagrams are independent of the IC streams used to estimate targets.
- Exact outer/inner splitting procedure and whether model choice or hyperparameter tuning used test information.
- CNN architecture beyond the first layer and bottleneck.
- Optimizer, learning rate, batch size, regularization, data augmentations, stopping rule, and validation criterion.
- Ridge and GBM hyperparameters, feature preprocessing, tuning protocol, and baseline-selection procedure.
- Exact definitions of cone extent, cone fill, damage fraction, perturbation location, and conditional aggregation.
- Exact formula for the spatial contrast statistic C(p).

A four-page paper can delegate details to a supplement, but it cannot omit them. The authors are making a methodological benchmark claim; methodology must be auditable.

### 5. The baseline is selectively strong, while the neural comparison is selectively weak.

The paper repeatedly argues that the comparison is “asymmetric in the network’s favour” because the CNN has more parameters. This is not a sound argument. Parameter count is not a proxy for effective capacity, optimization quality, appropriate receptive field, or sample efficiency. The network is deliberately constrained to block one hypothesized shortcut, trained for only 60 epochs, and evaluated without evidence of adequate architecture selection, optimization, or scaling.

The study compares only one CNN design against a feature set that includes a specialized glider-screen statistic and a nonlinear GBM readout. That is a legitimate narrow comparison, but it does not support the title or broad conclusion about deep learning.

The paper needs a factorial baseline analysis:

- Raw diagram plus linear, kernel, tree-based, and neural readouts.
- Five statistics plus linear and nonlinear readouts.
- Larger/multiscale CNNs, temporal CNNs, recurrent models, and models with different receptive fields.
- A transparent mechanistic baseline that infers the rule table from observed transitions and then simulates it to estimate the target invariants.
- A stacked model testing whether the CNN provides incremental predictive value beyond the five features.

The final item is particularly important. Regress the targets on the five features, then test whether CNN predictions explain held-out residual variation under cross-fitting. That directly answers whether learned representations add information beyond the handcrafted statistics.

### 6. “Dynamical invariants” is misleading terminology for the actual targets.

The targets are finite-size, finite-horizon, IC-measure-dependent observables. The manuscript acknowledges this by defining a protocol tuple, but then continues to call the resulting quantities invariants. They are not invariant under changes in lattice size, horizon, perturbation protocol, boundary conditions, or initial-condition measure.

The authors should consistently call them protocol-specific damage-spreading observables or finite-horizon response statistics. This is not merely semantic: the entire interpretation rests on behavior measured at width 127, Bernoulli(1/2) initialization, and horizons of roughly 62 steps for ECA and 30 steps for radius-two rules. These are short observations for claims about complex dynamics, gliders, and structural limits of representation learning.

### 7. The conclusion is limited to one observation regime, but the manuscript treats it as structural.

The paper tests Bernoulli(1/2) initial conditions, a single width, a single short horizon, one perturbation form, and a small number of rule spaces. It should not infer that texture and rule-readability are “a fundamental obstacle” to deep learning for CA.

The most informative experiments would train and test under systematic distribution shifts:

- Initial densities below and above 1/2.
- Correlated, blocky, periodic, and low-entropy initial conditions.
- Different widths and horizons with finite-size scaling.
- Different perturbations: one-bit, multi-bit, localized blocks, and density perturbations.
- Cropped, noisy, partially observed, and time-offset diagrams.
- Rule-family holdouts rather than only random leave-rules-out splits.

A learned model might plausibly fail to beat summary statistics in the iid Bernoulli short-horizon regime yet become useful when rare particles, long transients, or nonlocal interactions matter. The manuscript itself hints at this possibility, but its title and conclusions do not respect it.

### 8. The “complex/glider-supporting” classification is inadequately validated and potentially circular.

The manuscript labels radius-two rules “complex (glider-supporting)” using thresholds calibrated on famous complex ECAs and then presents a red band in the plane of spreading rate and cone fill. This is not an independent discovery of a glider-supporting region. The same damage-based signature appears to define the labels and generate the plot on which the alleged distinct band is displayed.

Damage signatures may correlate with particle-like dynamics, but they are not a validated glider detector. The manuscript needs an independent criterion: direct long-horizon space-time inspection, automated particle-tracking, collision tests, periodic-localization tests, or blinded expert annotation on a held-out sample. False-positive and false-negative rates must be reported.

Until then, the 7.8% result should be described conservatively as the fraction of sampled rules satisfying a predefined damage-signature criterion, not the prevalence of glider-supporting complexity in the full radius-two space.

### 9. The spatial-mapping experiment is not a fair or sufficiently grounded resolution test.

The claim that learned maps offer “no spatial resolution advantage” rests on striped two-rule diagrams and relative contrast versus stripe period. This is a limited synthetic probe, not a demonstrated phenotype-mapping benchmark.

There are several problems:

- The local ground truth is not independently defined through local perturbation experiments in the non-uniform CA.
- Rule interfaces can create mixed dynamics, so assigning a stripe a uniform-rule phenotype is questionable.
- The handcrafted map is allowed to use its “best window width per period,” which is an oracle-style selection unless window choice is fixed from validation data.
- The figure lacks uncertainty bands, rule-pair diversity, and raw replicate distributions.
- The two CNN map variants have fixed receptive fields, while the handcrafted method appears to optimize its local scale separately.

The appropriate experiment is to compute a location-specific damage-response ground truth in non-uniform CA, using local perturbations and multiple rule mosaics, then compare fixed and validation-selected methods on localization error, calibration, boundary resolution, and spatial correlation. Include random mosaics, multiple stripe orientations, varied rule pairs, and explicit interface analyses.

### 10. The pre-registration claim is currently unverifiable.

The repository is stated to be private until publication. Yet the paper invokes preregistration as a central warrant for the interpretation of its negative result. Private version-control history is not an independently auditable preregistration. Moreover, Appendix A reports an earlier panel-dependent random-seeding implementation that was changed after identifying drift.

Correcting a bug is appropriate. But the authors must provide a public immutable archive containing the preregistration, commit hashes, dated release history, all deviations, raw sampled rules, all target estimates, all cached diagrams, and scripts to regenerate every table and figure. Otherwise “pre-registered benchmark” is an assertion, not evidence.

### 11. Presentation and citation quality are not publication-ready.

The manuscript contains placeholder authors and affiliations, an inaccessible repository, and references with “TODO: verify venue,” “TODO: verify volume/pages/DOI.” These are unacceptable in a submitted article. Table I also appears visually clipped in the rightmost margin column, and the paper does not provide sufficient captions or methods for Figures 1–2 to stand independently.

## Experiments required for a credible revision

A viable revision would need, at minimum:

1. A public, immutable preregistration and complete reproducibility package.
2. Full architecture, data-generation, splitting, tuning, and evaluation details.
3. Repeated outer splits and paired bootstrap confidence intervals for all four targets.
4. Per-target results, not only a median summary.
5. Reliability-adjusted target ceilings based on repeated independent target simulations.
6. Direct probes of rule information in the CNN representation.
7. A rule-inference-and-simulate mechanistic baseline.
8. Residual/stacking analyses testing incremental value beyond the five statistics.
9. Broader neural and non-neural model suites, with tuning restricted to training/validation data.
10. Distribution-shift and finite-size/horizon experiments.
11. Independent validation of the claimed complex/glider-supporting rule set.
12. A spatial experiment with independently computed local ground truth and non-oracular baseline selection.

## Positive aspects

The basic question is good, and the authors are correct to challenge simplistic claims that deep learning automatically provides scientific value over transparent baselines. The explicit protocol, emphasis on rule-level separation, concern about shortcut learning, and attempt to report a negative result are all promising. But these strengths are outweighed by the mismatch between the narrow evidence and the sweeping claims.

In its present form, the manuscript should not be accepted. A substantially redesigned and fully documented study could become useful, but it would need to frame its conclusion much more narrowly: not “skip the network,” but rather that under a specified CA protocol, a transparent handcrafted baseline can match one tested CNN configuration.
