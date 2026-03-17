# GLM and GLMM Reference

Read this file when users ask about GLM, GLMM, logistic regression, Poisson regression, mixed model, random effect, link function.

## One-Sentence Positioning

- GLM: Generalized Linear Model, used for non-normal response variables.
- GLMM: Generalized Linear Mixed Model, adds random effects on top of GLM, suitable for repeated measures, hierarchical structures, or data with obvious individual differences.

## When to Prioritize These Models

If the response variable is not "approximately normal, independent, continuous" ordinary data, prioritize GLM/GLMM. For example:

- Whether a behavior occurs: binary, commonly binomial/logistic.
- Number of behavior occurrences: count data, commonly Poisson or negative binomial.
- Success count / total count: proportion, commonly binomial.
- Same animal repeatedly observed: usually needs mixed model to handle within-individual correlation.
- Data from different cages, groups, batches, observers: may need random effects.

## Explanation Order

When explaining GLM/GLMM, prioritize outputting in this order:

1. What is the response variable.
2. What is the data type of response variable.
3. What are fixed effects.
4. What are random effects.
5. What are distribution family and link function.
6. Why the model is suitable for this problem.
7. How to interpret parameters.
8. What are common diagnostics or limitations.

## Core Concepts

### Response Variable

The result variable the model tries to explain or predict, for example:

- Whether a behavior occurs.
- Number of calls within a certain time window.
- Proportion of behavior duration.

### Fixed Effects

Variables the researcher mainly cares about, for example:

- Treatment group
- Gender
- Age
- Time phase
- Environmental conditions

Fixed effects answer: "What is the systematic relationship between these variables and the result?"

### Random Effects

Used to represent hierarchical structure or repeated measurement sources, for example:

- individual ID
- group ID
- session ID
- observer ID
- batch

Random effects answer: "Do baseline differences between different individuals or groups need to be modeled separately rather than forcibly put into error terms?"

## Common Families and Typical Scenarios

### Gaussian

- Suitable for: approximately continuous normal response variables.
- Common examples: some continuous measurement with approximately normal residuals.
- Note: In this case, the model is closer to ordinary linear model.

### Binomial with logit link

- Suitable for: binary results or success count / total count.
- Common examples: whether a behavior occurs, whether successfully selects a certain food.
- Interpretation: Coefficients are on log-odds scale, need to explain whether converted to odds ratio or predicted probability.

### Poisson with log link

- Suitable for: count data.
- Common examples: attack frequency, call frequency, contact frequency.
- Note: If variance is significantly greater than mean, there may be overdispersion.

### Negative Binomial

- Suitable for: overdispersed count data.
- Common examples: data with large number of zeros and high individual variation in behavior frequency.
- Interpretation: Usually an alternative when Poisson is not flexible enough.

## Why Use GLMM Instead of Just GLM

When data has repeated measures or hierarchical structure, using just GLM often treats inherently correlated observations as independent samples, causing standard errors to be underestimated and significance to be exaggerated.

Typical scenarios:

- Same animal repeatedly observed in multiple trials.
- Multiple individuals from same group or cage.
- Same observer scores multiple videos.

Common phrasing:

- Fixed effects: treatment, time, gender, etc.
- Random effects: individual ID, group ID, etc.

## Parameter Interpretation Reminders

### Logistic Regression

- Coefficient increase of 1 does not mean probability directly increases by a fixed value.
- Coefficients first act on log-odds.
- If needing to explain to beginners, prioritize converting to "more likely / less likely" or give predicted probability examples.

### Poisson / Negative Binomial

- Coefficients usually act on log count or log rate.
- When interpreting, can convert to multiplicative changes, e.g., exp(beta).

### Random Effect

- Do not interpret random effect coefficient as main effect with same meaning as fixed effect.
- More accurate statement: It reflects the variation structure between different individuals or groups.

## Common Diagnostics and Limitations

When explaining models, prioritize checking whether the paper mentions:

- overdispersion
- zero inflation
- convergence warning
- singular fit
- residual diagnostics
- collinearity
- model comparison

If the paper does not write, do not pretend diagnostics were done, can only write `Unconfirmed`.

## Common Pitfalls

- Treating repeated measures data as independent samples.
- Using ordinary linear regression for count data.
- Only reporting p-values without explaining family, link, and random effect.
- Miswriting odds ratio as probability difference.
- Not explaining offset, e.g., directly comparing counts when observation durations are different.

## Recommended Output Sentence Patterns

### Model Card Minimum Template

- Response variable:
- Data type:
- Fixed effects:
- Random effects:
- Family / link:
- Selection rationale:
- Parameter interpretation:
- Diagnostics or limitations:

### Methods Writing Tips

In English:

"We fitted a generalized linear mixed model (GLMM) with ... as the response variable, ... as fixed effects, and individual ID as a random effect, using a ... family with a ... link function based on the data distribution of the response variable."
