# Bayesian Statistical Analysis

This document provides a guide for conducting and interpreting Bayesian statistical analysis, which offers an alternative framework to frequentist (classical) statistics.

## Bayesian vs. Frequentist Philosophy

### Fundamental Differences

| Dimension | Frequentist | Bayesian |
|-----------|-------------|----------|
| **Interpretation of Probability** | Long-run frequency of events | Degree of belief / Uncertainty |
| **Parameters** | Fixed but unknown | Random variables with distributions |
| **Inference** | Based on sampling distributions | Based on posterior distributions |
| **Main Outputs** | p-values, Confidence Intervals | Posterior probabilities, Credible Intervals |
| **Prior Information** | Not formally incorporated | Explicitly incorporated via prior distributions |
| **Hypothesis Testing** | Reject/Fail to reject null hypothesis | Probability of hypothesis given the data |
| **Sample Size** | Usually requires a minimum size | Applicable to any sample size |
| **Interpretation** | Indirect (Prob. of data given H₀) | Direct (Prob. of hypothesis given data) |

### Difference in Core Questions

**Frequentist**: "If the null hypothesis is true, what is the probability of observing data this extreme or more extreme?"

**Bayesian**: "Given the observed data, what is the probability that the hypothesis is true?"

The Bayesian question is more intuitive and directly answers what researchers want to know.

---

## Bayes' Theorem

**Formula**:
```
P(θ|D) = P(D|θ) × P(θ) / P(D)
```

**Mnemonic**:
```
Posterior = Likelihood × Prior / Evidence
```

Where:
- **θ (theta)**: Parameter of interest (e.g., mean difference, correlation)
- **D**: Observed data
- **P(θ|D)**: Posterior distribution (belief about θ after seeing the data)
- **P(D|θ)**: Likelihood (probability of the data given θ)
- **P(θ)**: Prior distribution (belief about θ before seeing the data)
- **P(D)**: Marginal likelihood / Evidence (normalizing constant)

---

## Prior Distributions

### Types of Priors

#### 1. Informative Priors

**When to use**: When you have substantial prior knowledge from:
- Previous studies
- Expert knowledge
- Theory
- Pilot data

**Example**: A meta-analysis shows an effect size d ≈ 0.40, Standard Deviation (SD) = 0.15
- Prior: Normal(0.40, 0.15)

**Pros**:
- Incorporates existing knowledge
- More efficient (requires smaller samples)
- Stabilizes estimates when data is sparse

**Cons**:
- Subjective (though subjectivity can be an advantage)
- Must be justified and transparent
- Can be controversial if a strong prior conflicts with the data

---

#### 2. Weakly Informative Priors

**When to use**: The default choice for most applications.

**Characteristics**:
- Regularizes estimates (prevents extreme values)
- Minimal impact on the posterior when data volume is moderate
- Prevents computational issues

**Example Priors**:
- Effect size: Normal(0, 1) or Cauchy(0, 0.707)
- Variance: Half-Cauchy(0, 1)
- Correlation: Uniform(-1, 1) or Beta(2, 2)

**Pros**:
- Balances objectivity with regularization
- Computationally stable
- Widely accepted

---

#### 3. Non-Informative (Flat/Uniform) Priors

**When to use**: When trying to remain "objective."

**Example**: Uniform(-∞, ∞) for any value.

**⚠️ Note**:
- Can lead to improper posterior distributions
- Can produce nonsensical conclusions
- Not truly "uninformative" (still contains assumptions)
- Generally not recommended in modern Bayesian practice

**Better Alternative**: Use weakly informative priors.

---

### Prior Sensitivity Analysis

**Essential**: Test how results change with different priors.

**Process**:
1. Fit the model with the default/planned prior.
2. Fit the model with a more diffuse (wider) prior.
3. Fit the model with a more concentrated (narrower) prior.
4. Compare the posterior distributions.

**Reporting**:
- If results are similar: The evidence is robust.
- If results differ significantly: The data is insufficient to overwhelm the prior influence.

**Python Example**:
```python
import pymc as pm

# Models with different priors
priors = [
    ('weakly_informative', pm.Normal.dist(0, 1)),
    ('diffuse', pm.Normal.dist(0, 10)),
    ('informative', pm.Normal.dist(0.5, 0.3))
]

results = {}
for name, prior in priors:
    with pm.Model():
        effect = pm.Normal('effect', mu=prior.mu, sigma=prior.sigma)
        # ... rest of the model
        trace = pm.sample()
        results[name] = trace
```

---

## Bayesian Hypothesis Testing

### Bayes Factor (BF)

**Definition**: The ratio of evidence between two competing hypotheses.

**Formula**:
```
BF₁₀ = P(D|H₁) / P(D|H₀)
```

**Interpretation**:

| BF₁₀ | Strength of Evidence |
|------|----------------------|
| >100 | Decisive evidence for H₁ |
| 30-100 | Very strong evidence for H₁ |
| 10-30 | Strong evidence for H₁ |
| 3-10 | Moderate evidence for H₁ |
| 1-3 | Anecdotal evidence (weak) for H₁ |
| 1 | No evidence |
| 1/3-1 | Anecdotal evidence (weak) for H₀ |
| 1/10-1/3 | Moderate evidence for H₀ |
| 1/30-1/10 | Strong evidence for H₀ |
| 1/100-1/30 | Very strong evidence for H₀ |
| <1/100 | Decisive evidence for H₀ |

**Advantages over p-values**:
1. Can provide evidence for the null hypothesis.
2. Not dependent on sampling intentions (no "peeking" problem).
3. Directly quantifies evidence.
4. Can be updated continuously as data increases.

**Python Calculation**:
```python
import pingouin as pg

# Note: Python support for BF is limited
# Better options: R packages (BayesFactor), JASP software

# Estimate BF from t-statistic
# Using Jeffreys-Zellner-Siow prior
from scipy import stats

def bf_from_t(t, n1, n2, r_scale=0.707):
    """
    Approximate Bayes Factor from t-statistic
    r_scale: Cauchy prior scale (default 0.707 for medium effect)
    """
    # This is a simplified illustration; use specialized packages for accuracy
    df = n1 + n2 - 2
    # Implementation requires numerical integration
    pass
```

---

### Region of Practical Equivalence (ROPE)

**Purpose**: To define a range of effect sizes that are considered negligible.

**Process**:
1. Define the ROPE (e.g., d ∈ [-0.1, 0.1] is considered negligible).
2. Calculate the percentage of the posterior distribution falling within the ROPE.
3. Make a decision:
   - >95% in ROPE: Accept practical equivalence.
   - >95% outside ROPE: Reject equivalence.
   - Otherwise: Undecided.

**Advantage**: Directly tests for practical significance.

**Python Example**:
```python
# Define ROPE
rope_lower, rope_upper = -0.1, 0.1

# Calculate % of posterior in ROPE
in_rope = np.mean((posterior_samples > rope_lower) &
                  (posterior_samples < rope_upper))

print(f"Percentage of posterior in ROPE: {in_rope*100:.1f}%")
```

---

## Bayesian Estimation

### Credible Intervals

**Definition**: An interval in which a parameter falls with X% probability.

**Interpretation of a 95% Credible Interval**:
> "There is a 95% probability that the true parameter lies within this interval."

**This is exactly what people "mistakenly" think frequentist confidence intervals represent** (but they do not in a frequentist framework).

**Types**:

#### Equal-Tailed Interval (ETI)
- 2.5th to 97.5th percentiles.
- Simple to calculate.
- For skewed distributions, it may not include the mode.

#### Highest Density Interval (HDI)
- The narrowest interval containing 95% of the distribution.
- Always includes the mode.
- Better for skewed distributions.

**Python Calculation**:
```python
import arviz as az

# Equal-Tailed Interval
eti = np.percentile(posterior_samples, [2.5, 97.5])

# HDI
hdi = az.hdi(posterior_samples, hdi_prob=0.95)
```

---

### Posterior Distribution

**Interpreting the Posterior**:

1. **Central Tendency**:
   - Mean: Posterior average.
   - Median: 50th percentile.
   - Mode: Most likely value (MAP - Maximum A Posteriori).

2. **Uncertainty**:
   - Standard Deviation (SD): The spread of the posterior.
   - Credible Intervals: Quantifying uncertainty.

3. **Shape**:
   - Symmetric: Similar to a Normal distribution.
   - Skewed: Asymmetry in uncertainty.
   - Multimodal: Multiple likely regions for the value.

**Visualization**:
```python
import matplotlib.pyplot as plt
import arviz as az

# Posterior plot with HDI
az.plot_posterior(trace, hdi_prob=0.95)

# Trace plot (to check convergence)
az.plot_trace(trace)

# Forest plot (for multiple parameters)
az.plot_forest(trace)
```

---

## Common Bayesian Analyses

### Bayesian T-Test

**Purpose**: Compare two groups (Bayesian alternative to the t-test).

**Outputs**:
1. Posterior distribution of the mean difference.
2. 95% Credible Interval.
3. Bayes Factor (BF₁₀).
4. Probability of a directional hypothesis (e.g., P(μ₁ > μ₂)).

**Python Implementation**:
```python
import pymc as pm
import arviz as az

# Bayesian independent samples t-test
with pm.Model() as model:
    # Priors for group means
    mu1 = pm.Normal('mu1', mu=0, sigma=10)
    mu2 = pm.Normal('mu2', mu=0, sigma=10)

    # Prior for pooled standard deviation
    sigma = pm.HalfNormal('sigma', sigma=10)

    # Likelihood
    y1 = pm.Normal('y1', mu=mu1, sigma=sigma, observed=group1)
    y2 = pm.Normal('y2', mu=mu2, sigma=sigma, observed=group2)

    # Derived variable: mean difference
    diff = pm.Deterministic('diff', mu1 - mu2)

    # Posterior sampling
    trace = pm.sample(2000, tune=1000, return_inferencedata=True)

# Analyze results
print(az.summary(trace, var_names=['mu1', 'mu2', 'diff']))

# Probability that group1 > group2
prob_greater = np.mean(trace.posterior['diff'].values > 0)
print(f"P(μ₁ > μ₂) = {prob_greater:.3f}")

# Plot posterior
az.plot_posterior(trace, var_names=['diff'], ref_val=0)
```

---

### Bayesian ANOVA

**Purpose**: Compare three or more groups.

**Model**:
```python
import pymc as pm

with pm.Model() as anova_model:
    # Hyperpriors
    mu_global = pm.Normal('mu_global', mu=0, sigma=10)
    sigma_between = pm.HalfNormal('sigma_between', sigma=5)
    sigma_within = pm.HalfNormal('sigma_within', sigma=5)

    # Group means (hierarchical)
    group_means = pm.Normal('group_means',
                            mu=mu_global,
                            sigma=sigma_between,
                            shape=n_groups)

    # Likelihood
    y = pm.Normal('y',
                  mu=group_means[group_idx],
                  sigma=sigma_within,
                  observed=data)

    trace = pm.sample(2000, tune=1000, return_inferencedata=True)

# Posterior contrasts
contrast_1_2 = trace.posterior['group_means'][:,:,0] - trace.posterior['group_means'][:,:,1]
```

---

### Bayesian Correlation Analysis

**Purpose**: Estimate the correlation between two variables.

**Advantage**: Provides a distribution of the correlation coefficient.

**Python Implementation**:
```python
import pymc as pm

with pm.Model() as corr_model:
    # Prior for correlation coefficient
    rho = pm.Uniform('rho', lower=-1, upper=1)

    # Transform to covariance matrix
    cov_matrix = pm.math.stack([[1, rho],
                                [rho, 1]])

    # Likelihood (Bivariate Normal)
    obs = pm.MvNormal('obs',
                     mu=[0, 0],
                     cov=cov_matrix,
                     observed=np.column_stack([x, y]))

    trace = pm.sample(2000, tune=1000, return_inferencedata=True)

# Summary of correlation
print(az.summary(trace, var_names=['rho']))

# Probability that correlation is positive
prob_positive = np.mean(trace.posterior['rho'].values > 0)
```

---

### Bayesian Linear Regression

**Purpose**: Model the relationship between predictors and an outcome.

**Advantages**:
- Uncertainty for all parameters.
- Natural regularization (via priors).
- Can incorporate prior knowledge.
- Credible intervals for predicted values.

**Python Implementation**:
```python
import pymc as pm

with pm.Model() as regression_model:
    # Priors for coefficients
    alpha = pm.Normal('alpha', mu=0, sigma=10)  # Intercept
    beta = pm.Normal('beta', mu=0, sigma=10, shape=n_predictors)
    sigma = pm.HalfNormal('sigma', sigma=10)

    # Expected value
    mu = alpha + pm.math.dot(X, beta)

    # Likelihood
    y_obs = pm.Normal('y_obs', mu=mu, sigma=sigma, observed=y)

    trace = pm.sample(2000, tune=1000, return_inferencedata=True)

# Posterior Predictive Check (PPC)
with regression_model:
    ppc = pm.sample_posterior_predictive(trace)

az.plot_ppc(ppc)

# Predictions with uncertainty
with regression_model:
    pm.set_data({'X': X_new})
    posterior_pred = pm.sample_posterior_predictive(trace)
```

---

## Hierarchical (Multilevel) Models

**When to use**:
- Nested/clustered data (e.g., students within schools).
- Repeated measures.
- Meta-analysis.
- Effects that vary across groups.

**Core Concept**: Partial Pooling
- Complete Pooling: Ignore grouping (biased).
- No Pooling: Analyze groups separately (high variance).
- Partial Pooling: "Borrow" strength across groups (Bayesian approach).

**Example: Varying Intercept Model**:
```python
with pm.Model() as hierarchical_model:
    # Hyperpriors
    mu_global = pm.Normal('mu_global', mu=0, sigma=10)
    sigma_between = pm.HalfNormal('sigma_between', sigma=5)
    sigma_within = pm.HalfNormal('sigma_within', sigma=5)

    # Group-level intercepts
    alpha = pm.Normal('alpha',
                     mu=mu_global,
                     sigma=sigma_between,
                     shape=n_groups)

    # Likelihood
    y_obs = pm.Normal('y_obs',
                     mu=alpha[group_idx],
                     sigma=sigma_within,
                     observed=y)

    trace = pm.sample()
```

---

## Model Comparison

### Methods

#### 1. Bayes Factor
- Directly compares model evidence.
- Highly sensitive to prior specifications.
- Can be computationally intensive.

#### 2. Information Criteria

**WAIC (Widely Applicable Information Criterion)**:
- Bayesian analog of AIC.
- Lower is better.
- Accounts for the effective number of parameters.

**LOO (Leave-One-Out Cross-Validation)**:
- Estimates out-of-sample predictive error.
- Lower is better.
- More robust than WAIC.

**Python Calculation**:
```python
import arviz as az

# Calculate WAIC and LOO
waic = az.waic(trace)
loo = az.loo(trace)

print(f"WAIC: {waic.elpd_waic:.2f}")
print(f"LOO: {loo.elpd_loo:.2f}")

# Compare multiple models
comparison = az.compare({
    'model1': trace1,
    'model2': trace2,
    'model3': trace3
})
print(comparison)
```

---

## Checking Bayesian Models

### 1. Convergence Diagnostics

**R-hat (Gelman-Rubin statistic)**:
- Compares within-chain variance to between-chain variance.
- Approaching 1.0 indicates convergence.
- R-hat < 1.01: Good.
- R-hat > 1.05: Poor convergence.

**Effective Sample Size (ESS)**:
- The number of independent samples.
- Higher is better.
- Recommended ESS > 400 per chain.

**Trace plots**:
- Should look like "fuzzy caterpillars."
- No obvious trends, no stuck chains.

**Python Check**:
```python
# Automatic summary with diagnostics
print(az.summary(trace, var_names=['parameter']))

# Visual diagnostics
az.plot_trace(trace)
az.plot_rank(trace)  # Rank plots
```

---

### 2. Posterior Predictive Checks (PPC)

**Purpose**: Does the data generated by the model look like the observed data?

**Process**:
1. Generate predictions from the posterior distribution.
2. Compare them with the actual data.
3. Look for systematic discrepancies.

**Python Implementation**:
```python
with model:
    ppc = pm.sample_posterior_predictive(trace)

# Visual check
az.plot_ppc(ppc, num_pp_samples=100)

# Quantitative check
obs_mean = np.mean(observed_data)
pred_means = [np.mean(sample) for sample in ppc.posterior_predictive['y_obs']]
p_value = np.mean(pred_means >= obs_mean)  # Bayesian p-value
```

---

## Reporting Bayesian Results

### T-Test Reporting Example

> "We conducted a Bayesian independent samples t-test to compare Group A and Group B. Weakly informative priors were used: Normal(0, 1) for the mean difference and Half-Cauchy(0, 1) for the pooled standard deviation. The posterior distribution for the mean difference had a mean of 5.2 (95% CI [2.3, 8.1]), indicating higher scores for Group A. A Bayes Factor of BF₁₀ = 23.5 provided strong evidence for a difference between groups, and the probability that the Group A mean exceeds the Group B mean was 99.7%."

### Regression Reporting Example

> "A Bayesian linear regression was fitted using weakly informative priors (Normal(0, 10) for coefficients, Half-Cauchy(0, 5) for residual SD). The model explained a substantial portion of the variance (R² = 0.47, 95% CI [0.38, 0.55]). Study hours (β = 0.52, 95% CI [0.38, 0.66]) and previous GPA (β = 0.31, 95% CI [0.17, 0.45]) were credible predictors (95% CIs did not contain zero). Posterior predictive checks indicated a good model fit. Convergence diagnostics were satisfactory (all R-hat < 1.01, ESS > 1000)."

---

## Advantages & Limitations

### Advantages

1. **Intuitive Interpretation**: Direct probability statements about parameters.
2. **Incorporates Prior Knowledge**: Utilizes all available information.
3. **Flexible**: Easily handles complex models.
4. **No p-hacking**: You can look at the data as it arrives.
5. **Quantifies Uncertainty**: Provides the full posterior distribution.
6. **Small Sample Friendly**: Works with any sample size.

### Limitations

1. **Computational Cost**: Requires MCMC sampling (can be slow).
2. **Prior Specification**: Requires careful thought and justification.
3. **Complexity**: Steeper learning curve.
4. **Software Support**: Fewer tools than frequentist methods.
5. **Communication Cost**: May require educating reviewers/readers.

---

## Core Python Libraries

- **PyMC**: Full Bayesian modeling framework.
- **ArviZ**: Visualization and diagnostic tools.
- **Bambi**: High-level interface for regression models.
- **PyStan**: Python interface for Stan.
- **TensorFlow Probability**: Bayesian inference on top of TensorFlow.

---

## When to Use Bayesian Methods

**Use Bayesian when**:
- You have prior information to incorporate.
- You want direct probability statements.
- Your sample size is small.
- Your model is complex (hierarchical, missing data, etc.).
- You want to update analysis in real-time as data arrives.

**Frequentist may suffice when**:
- You have a standard analysis with a large sample.
- You have no prior information.
- Computational resources are limited.
- Your audience/reviewers are unfamiliar with Bayesian methods.