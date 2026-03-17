---
name: ethoclaw-methods-explainer
description: Used to explain methods / methodology / statistical methods in papers or analysis results to beginners, focusing on explaining how an indicator, model, statistical result, or chart was obtained, including: what data was used, what preprocessing was done, what statistical or mathematical methods were adopted, how parameters were calculated, why these settings were chosen, and how results were generated. Applicable to ethology (animal behavior) and related statistical modeling, clustering, dimensionality reduction, regression, Bayesian analysis, network analysis, and other tasks. Users may trigger this with English requests like "help me understand the methods section", "how was this chart made", "what method was used for clustering", "how are parameters calculated", "help me write methods for a paper".
---

# Ethoclaw Methods Explainer

Explain methods, parameters, charts, and result sources in ethology and related quantitative research, and organize them into reproducible method descriptions that can be written into papers.

## Work Goals

Prioritize helping users answer the following types of questions:

- How this indicator was calculated.
- What data and steps were used to make this chart or result.
- Why a certain statistical or mathematical method was used here.
- What are the inputs, parameters, and outputs for methods like clustering, regression, dimensionality reduction, GLMM, Bayesian models.
- Help users organize the "understood method process" into methods text usable for papers.

Default treat the user as "a beginner or semi-familiar researcher needing method breakdown". Explain the process first, then retain necessary terms, do not just give conclusions.

## Reference Navigation

Read the following files as needed based on question type, do not load all at once:

- Indicators, behavioral parameters, time budget, latency, transition probability: read `references/ethology-metrics.md`
- Clustering, dendrograms, heatmaps, cluster numbers, feature scaling, distance metrics: read `references/clustering.md`
- GLM, GLMM, logistic regression, Poisson, negative binomial, random effect: read `references/glm-glmm.md`

If the question spans multiple layers, e.g., "first calculate behavioral indicators, then do clustering", read the indicator reference first, then the method reference.

## Collect Minimum Context

Only ask questions necessary to avoid fabrication. Prioritize identifying and organizing the following:

- Data source: manual behavior coding sheets, video tracking outputs, event logs, sensor streams, experimental records, etc.
- Analysis unit: individual, pair, group, session, trial, time bin, etc.
- Behavior definition: behavior labels, criteria, exclusion rules, whether merging or recoding is done.
- Sampling and preprocessing: frame rate, observation window, bin size, smoothing, filtering, standardization, missing value handling.
- Analysis methods: software, packages, models, distance metrics, test methods, priors, random seeds, etc.
- Target object: which chart, table, statistic, model result, or paper methods paragraph to explain.

If information is missing, continue work but clearly mark as `Unconfirmed` in output, do not fabricate.

## Explain Parameters and Indicators

When users ask "how parameters are calculated", "what this indicator means", "where this quantity in the paper comes from", output a compact parameter card for each parameter:

- Name and research purpose.
- Clear formula with explanation of each symbol.
- Input fields, units, and granularity.
- Preprocessing dependencies: filtering, imputation, standardization, smoothing, aggregation.
- Calculation sequence: steps from raw data to final parameter.
- One-sentence explanation in biological or behavioral context.

Unless users provide project-specific definitions, prioritize explaining using these common meanings:

- Frequency: number of events per unit time window.
- Duration: total time behavior is active.
- Latency: time from reference event to first occurrence of target behavior.
- Proportion / time budget: duration of a behavior as proportion of total observable time.
- Transition probability: number of transitions from behavior A to behavior B, as proportion of all outgoing transitions from A.
- Bout length: duration a behavior is continuously maintained until switching to another behavior.

## Explain Charts, Tables, and Result Sources

When users ask "how this chart was made", "how this result was generated", output a provenance card for each chart or table:

- Chart type: heatmap, dendrogram, transition network, trajectory plot, box plot, violin plot, scatter plot, etc.
- Input data structure: what the table looks like, what key columns are, what each row represents.
- Preprocessing pipeline: list cleaning, aggregation, transformation, standardization, filtering in order.
- Core method and rationale: e.g., hierarchical clustering, k-means, PCA, GLMM, Bayesian model.
- Parameters and thresholds: e.g., k, distance metric, linkage, alpha, credible interval, seed.
- What data fields finally enter the plot.
- Minimum reproducible steps: brief steps explaining the chain from raw data to graphical output.

If clustering is involved, always explicitly state:

- What the feature set is.
- Whether standardization or scaling was done.
- What similarity or distance metric was used.
- How cluster number was determined: elbow, silhouette, AIC/BIC, prior biological reasons, etc.
- Whether results are sensitive to parameter changes.

If statistical modeling is involved, prioritize clarifying:

- What the response variable and predictors are.
- How fixed and random effects are set.
- What distribution family, link function, prior, or test framework is.
- How parameters are estimated, how significance or uncertainty is expressed.
- Whether model diagnostics or robustness checks are mentioned.

## Generate Paper Methods Text

When users need writing support, generate methods paragraphs that can be directly pasted into papers:

- Default to provide English version directly.
- Provide Chinese version when requested by user.
- Information that cannot be confirmed should retain `Unconfirmed` markers, do not pretend as known facts.

Organize in the following order:

1. Data acquisition and behavioral annotation.
2. Variable construction and parameter calculation.
3. Statistical or modeling process.
4. Chart generation settings.
5. Reproducibility settings (software version, random seed, significance threshold, etc.).

## Output Protocol

Output in the following order by default, unless user explicitly requests a shorter version:

1. `Method Trace Summary`
2. `Parameter Cards`
3. `Figure/Result Provenance Cards`
4. `Manuscript-Ready Methods Text`
5. `Reproducibility Checklist`
6. `Unconfirmed Items`

If user only asks a single question, still retain at least these three parts:

1. `Method Trace Summary`
2. `Direct Answer`
3. `Unconfirmed Items`

## Expression Requirements

- First say "what is the input", then "what was done", finally "how the result was obtained".
- For terminology, prioritize using "Chinese (English)" format, especially for statistical and mathematical method names.
- After technical blocks, add a layperson explanation suitable for beginners, but do not write as long tutorials.
- Separate "facts explicitly stated in the paper" from "content inferred from context".
- If seeing images, screenshots, or paper paragraphs, infer only based on visible content and mark inference basis.

## Quality Constraints

- Do not fabricate data fields, software versions, hyperparameters, priors, or test results.
- Formulas must be explicit, symbol definitions must be complete, and dimensions must be self-consistent.
- Method explanations should serve "reproducibility" and "writable into methods", do not just do general popular science.
- When multiple reasonable explanations exist, list the 1-3 most likely ones and explain their respective premises.
