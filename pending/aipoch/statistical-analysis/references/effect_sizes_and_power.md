# Effect Size and Power Analysis

This document provides guidelines for calculating, interpreting, and reporting effect sizes, as well as guidance on power analysis for research planning.

## Why Effect Size Matters

1.  **Statistical Significance ≠ Practical Significance**: The p-value only indicates whether an effect exists, not how large the effect is.
2.  **Sample Size Dependency**: In large samples, even trivial effects can become "significant."
3.  **Interpretative Value**: Effect sizes provide the magnitude and practical importance of an effect.
4.  **Meta-analysis**: Effect sizes make it possible to combine results across different studies.
5.  **Power Analysis**: It is a necessary prerequisite for determining sample size.

**Golden Rule**: Always report effect sizes alongside p-values.

---

## Effect Sizes by Analysis Type

### T-tests and Mean Differences

#### Cohen's d (Standardized Mean Difference)

**Formula**:
- Independent groups: d = (M₁ - M₂) / SD_pooled
- Paired groups: d = M_diff / SD_diff

**Interpretation** (Cohen, 1988):
- Small: |d| = 0.20
- Medium: |d| = 0.50
- Large: |d| = 0.80

**Context-based Interpretation**:
- In Education: d = 0.40 is a typical value for a successful intervention.
- In Psychology: d = 0.40 is considered meaningful.
- In Medicine: Even smaller effect sizes may have clinical importance.

**Python Calculation**:
```python
import pingouin as pg
import numpy as np

# Independent samples t-test with effect size
result = pg.ttest(group1, group2, correction=False)
cohens_d = result['cohen-d'].values[0]

# Manual calculation
mean_diff = np.mean(group1) - np.mean(group2)
pooled_std = np.sqrt((np.var(group1, ddof=1) + np.var(group2, ddof=1)) / 2)
cohens_d = mean_diff / pooled_std

# Paired samples t-test
result = pg.ttest(pre, post, paired=True)
cohens_d = result['cohen-d'].values[0]
```

**Confidence Intervals for d**:
```python
from pingouin import compute_effsize_from_t

d, ci = compute_effsize_from_t(t_statistic, nx=n1, ny=n2, eftype='cohen')
```

---

#### Hedges' g (Bias-corrected d)

**Reason for use**: Cohen's d has a slight upward bias in small samples (n < 20).

**Formula**: g = d × correction_factor, where correction_factor = 1 - 3/(4df - 1)

**Python Calculation**:
```python
result = pg.ttest(group1, group2, correction=False)
hedges_g = result['hedges'].values[0]
```

**When to use Hedges' g**:
- Small sample sizes (n < 20 per group).
- When conducting meta-analyses (standard practice in meta-analysis).

---

#### Glass's Δ (Delta)

**When to use**: When one group is a control group with known variability.

**Formula**: Δ = (M₁ - M₂) / SD_control

**Application Scenarios**:
- Clinical trials (using the standard deviation of the control group).
- When the treatment affects variability.

---

### Analysis of Variance (ANOVA)

#### Eta-squared (η²)

**Measure**: The proportion of total variance explained by the factor.

**Formula**: η² = SS_effect / SS_total

**Interpretation**:
- Small: η² = 0.01 (explains 1% of variance)
- Medium: η² = 0.06 (explains 6% of variance)
- Large: η² = 0.14 (explains 14% of variance)

**Limitations**: Biased in multi-factor models (sums can exceed 1.0).

**Python Calculation**:
```python
import pingouin as pg

# One-way ANOVA
aov = pg.anova(dv='value', between='group', data=df)
eta_squared = aov['SS'][0] / aov['SS'].sum()

# Or use pingouin directly
aov = pg.anova(dv='value', between='group', data=df, detailed=True)
eta_squared = aov['np2'][0]  # Note: pingouin reports partial eta-squared
```

---

#### Partial Eta-squared (η²_p)

**Measure**: The proportion of variance explained by the factor after excluding other factors.

**Formula**: η²_p = SS_effect / (SS_effect + SS_error)

**Interpretation**: Benchmarks are the same as η².

**When to use**: Multi-factor ANOVA (standard practice for factorial designs).

**Python Calculation**:
```python
aov = pg.anova(dv='value', between=['factor1', 'factor2'], data=df)
# pingouin reports partial eta-squared by default
partial_eta_sq = aov['np2']
```

---

#### Omega-squared (ω²)

**Measure**: A less biased estimate of the proportion of variance explained in the population.

**Reason for use**: η² tends to overestimate effect size; ω² provides a better population estimate.

**Formula**: ω² = (SS_effect - df_effect × MS_error) / (SS_total + MS_error)

**Interpretation**: Benchmarks are the same as η², but values are typically smaller.

**Python Calculation**:
```python
def omega_squared(aov_table):
    ss_effect = aov_table.loc[0, 'SS']
    ss_total = aov_table['SS'].sum()
    ms_error = aov_table.loc[aov_table.index[-1], 'MS']  # Mean Square Residual
    df_effect = aov_table.loc[0, 'DF']

    omega_sq = (ss_effect - df_effect * ms_error) / (ss_total + ms_error)
    return omega_sq
```

---

#### Cohen's f

**Measure**: Effect size for ANOVA (analogous to Cohen's d).

**Formula**: f = √(η² / (1 - η²))

**Interpretation**:
- Small: f = 0.10
- Medium: f = 0.25
- Large: f = 0.40

**Python Calculation**:
```python
eta_squared = 0.06  # Derived from ANOVA
cohens_f = np.sqrt(eta_squared / (1 - eta_squared))
```

**Application in Power Analysis**: Required parameter for conducting ANOVA power calculations.

---

### Correlation Analysis

#### Pearson's r / Spearman's ρ

**Interpretation**:
- Small: |r| = 0.10
- Medium: |r| = 0.30
- Large: |r| = 0.50

**Important Notes**:
- r² = Coefficient of Determination (proportion of shared variance).
- r = 0.30 means 9% shared variance (0.30² = 0.09).
- Consider directionality (positive/negative) and research context.

**Python Calculation**:
```python
import pingouin as pg

# Pearson correlation with confidence intervals
result = pg.corr(x, y, method='pearson')
r = result['r'].values[0]
ci = [result['CI95%'][0][0], result['CI95%'][0][1]]

# Spearman rank correlation
result = pg.corr(x, y, method='spearman')
rho = result['r'].values[0]
```

---

### Regression Analysis

#### R² (Coefficient of Determination)

**Measure**: The proportion of variance in the dependent variable Y explained by the model.

**Interpretation**:
- Small: R² = 0.02
- Medium: R² = 0.13
- Large: R² = 0.26

**Context-based**:
- Physical Sciences: Expected R² > 0.90.
- Social Sciences: R² > 0.30 is considered good.
- Behavior Prediction: R² > 0.10 may be meaningful.

**Python Calculation**:
```python
from sklearn.metrics import r2_score
from statsmodels.api import OLS

# Using statsmodels
model = OLS(y, X).fit()
r_squared = model.rsquared
adjusted_r_squared = model.rsquared_adj

# Manual calculation
r_squared = 1 - (SS_residual / SS_total)
```

---

#### Adjusted R²

**Reason for use**: R² increases artificially when adding predictors; Adjusted R² penalizes model complexity.

**Formula**: R²_adj = 1 - (1 - R²) × (n - 1) / (n - k - 1)

**When to use**: Should always be reported alongside R² in multiple regression.

---

#### Standardized Regression Coefficients (β)

**Measure**: The impact of a one standard deviation change in a predictor on the outcome (in standard deviation units).

**Interpretation**: Similar to Cohen's d
- Small: |β| = 0.10
- Medium: |β| = 0.30
- Large: |β| = 0.50

**Python Calculation**:
```python
from scipy import stats

# Standardize variables first
X_std = (X - X.mean()) / X.std()
y_std = (y - y.mean()) / y.std()

model = OLS(y_std, X_std).fit()
beta = model.params
```

---

#### f² (Cohen's f-squared in Regression)

**Measure**: Effect size for individual predictors or model comparisons.

**Formula**: f² = (R²_AB - R²_A) / (1 - R²_AB)

Where:
- R²_AB = R² of the full model including the predictor
- R²_A = R² of the reduced model without the predictor

**Interpretation**:
- Small: f² = 0.02
- Medium: f² = 0.15
- Large: f² = 0.35

**Python Calculation**:
```python
# Comparing two nested models
model_full = OLS(y, X_full).fit()
model_reduced = OLS(y, X_reduced).fit()

r2_full = model_full.rsquared
r2_reduced = model_reduced.rsquared

f_squared = (r2_full - r2_reduced) / (1 - r2_full)
```

---

### Categorical Data Analysis

#### Cramér's V

**Measure**: Strength of association for χ² tests (suitable for tables of any size).

**Formula**: V = √(χ² / (n × (k - 1)))

Where k = min(number of rows, number of columns)

**Interpretation** (for k > 2):
- Small: V = 0.07
- Medium: V = 0.21
- Large: V = 0.35

**For 2×2 Tables**: Use the phi coefficient (φ).

**Python Calculation**:
```python
from scipy.stats.contingency import association

# Cramér's V
cramers_v = association(contingency_table, method='cramer')

# Phi coefficient (for 2x2)
phi = association(contingency_table, method='pearson')
```

---

#### Odds Ratio (OR) and Relative Risk (RR)

**For 2×2 Contingency Tables**:

|           | Outcome + | Outcome - |
|-----------|-----------|-----------|
| Exposed   | a         | b         |
| Unexposed | c         | d         |

**Odds Ratio**: OR = (a/b) / (c/d) = ad / bc

**Interpretation**:
- OR = 1: No association
- OR > 1: Positive association (increased odds)
- OR < 1: Negative association (decreased odds)
- OR = 2: Double the odds
- OR = 0.5: Half the odds

**Relative Risk**: RR = (a/(a+b)) / (c/(c+d))

**When to use**:
- Cohort Studies: Use RR (more interpretable).
- Case-Control Studies: Use OR (RR cannot be obtained).
- Logistic Regression: OR is the natural output.

**Python Calculation**:
```python
import statsmodels.api as sm

# Calculation from contingency table
odds_ratio = (a * d) / (b * c)

# Confidence interval
table = np.array([[a, b], [c, d]])
oddsratio, pvalue = stats.fisher_exact(table)

# Calculation from logistic regression
model = sm.Logit(y, X).fit()
odds_ratios = np.exp(model.params)  # Exponentiate coefficients
ci = np.exp(model.conf_int())  # Exponentiate confidence intervals
```

---

### Bayesian Effect Sizes

#### Bayes Factor (BF)

**Measure**: The ratio of evidence between the alternative hypothesis and the null hypothesis.

**Interpretation**:
- BF₁₀ = 1: Equal evidence for H₁ and H₀.
- BF₁₀ = 3: H₁ is 3 times more likely than H₀ (moderate evidence).
- BF₁₀ = 10: H₁ is 10 times more likely than H₀ (strong evidence).
- BF₁₀ = 100: H₁ is 100 times more likely than H₀ (extreme evidence).
- BF₁₀ = 0.33: H₀ is 3 times more likely than H₁.
- BF₁₀ = 0.10: H₀ is 10 times more likely than H₁.

**Classification** (Jeffreys, 1961):
- 1-3: Anecdotal evidence
- 3-10: Moderate evidence
- 10-30: Strong evidence
- 30-100: Very strong evidence
- >100: Decisive evidence

**Python Calculation**:
```python
import pingouin as pg

# Bayesian t-test
result = pg.ttest(group1, group2, correction=False)
# Note: pingouin does not directly include BF; use other packages

# Use JASP or R's BayesFactor package via rpy2
# Or implement via numerical integration
```

---

## Power Analysis

### Concepts

**Statistical Power**: The probability of detecting an effect if it exists (1 - β).

**Conventional Standards**:
- Power = 0.80 (80% chance of detecting the effect).
- α = 0.05 (5% Type I error rate).

**Four Interrelated Parameters** (given any 3, the 4th can be solved):
1. Sample size (n)
2. Effect size (d, f, etc.)
3. Significance level (α)
4. Power (1 - β)

---

### A Priori Power Analysis (Research Planning)

**Purpose**: To determine the required sample size before starting a study.

**Steps**:
1. Specify the expected effect size (from literature, pilot data, or minimum meaningful effect).
2. Set the α level (usually 0.05).
3. Set the desired power (usually 0.80).
4. Calculate the required n.

**Python Implementation**:
```python
from statsmodels.stats.power import (
    tt_ind_solve_power,
    zt_ind_solve_power,
    FTestAnovaPower,
    NormalIndPower
)

# T-test power analysis
n_required = tt_ind_solve_power(
    effect_size=0.5,  # Cohen's d
    alpha=0.05,
    power=0.80,
    ratio=1.0,  # Equal sample sizes
    alternative='two-sided'
)

# ANOVA power analysis
anova_power = FTestAnovaPower()
n_per_group = anova_power.solve_power(
    effect_size=0.25,  # Cohen's f
    ngroups=3,
    alpha=0.05,
    power=0.80
)

# Correlation power analysis
from pingouin import power_corr
n_required = power_corr(r=0.30, power=0.80, alpha=0.05)
```

---

### Post Hoc Power Analysis (After Study)

**⚠️ Warning**: Post hoc power is controversial and generally not recommended.

**Why it is problematic**:
- Observed power is a direct function of the p-value.
- If p > 0.05, power is always low.
- It provides no additional information beyond the p-value.
- It can be misleading.

**When it might be acceptable**:
- Planning for future studies.
- Using effect sizes from multiple studies (not just your own).
- When the explicit goal is to determine sample size for a replication study.

**Better Alternatives**:
- Report confidence intervals for effect sizes.
- Conduct sensitivity analysis.
- Report the minimum detectable effect size.

---

### Sensitivity Analysis

**Purpose**: To determine the minimum detectable effect size given the research parameters.

**When to use**: After a study is completed, to understand the study's detection capability.

**Python Implementation**:
```python
# With n=50 per group, what effect size can we detect?
detectable_effect = tt_ind_solve_power(
    effect_size=None,  # Solve for this
    nobs1=50,
    alpha=0.05,
    power=0.80,
    ratio=1.0,
    alternative='two-sided'
)

print(f"With n=50 per group, we can detect d ≥ {detectable_effect:.2f}")
```

---

## Reporting Effect Sizes

### APA Style Guidelines

**T-test Example**:
> "Group A (M = 75.2, SD = 8.5) scored significantly higher than Group B (M = 68.3, SD = 9.2), t(98) = 3.82, p < .001, d = 0.77, 95% CI [0.36, 1.18]."

**ANOVA Example**:
> "There was a significant main effect of treatment condition on test scores, F(2, 87) = 8.45, p < .001, η²p = .16. Post hoc comparisons using Tukey's HSD indicated..."

**Correlation Example**:
> "There was a moderate positive correlation between study time and exam scores, r(148) = .42, p < .001, 95% CI [.27, .55]."

**Regression Example**:
> "The regression model significantly predicted exam scores, F(3, 146) = 45.2, p < .001, R² = .48. Study duration (β = .52, p < .001) and prior GPA (β = .31, p < .001) were significant predictors."

**Bayesian Example**:
> "A Bayesian independent samples t-test provided strong evidence for a difference between groups, BF₁₀ = 23.5, indicating that the data were 23.5 times more likely under H₁ than H₀."

---

## Common Pitfalls in Effect Sizes

1.  **Don't rely solely on benchmarks**: Context matters; small effects can have profound implications.
2.  **Report confidence intervals**: CIs show the precision of the effect size estimate.
3.  **Distinguish statistical vs. practical significance**: Large n makes trivial effects "significant."
4.  **Consider cost-benefit**: If intervention costs are low, even tiny effects may be valuable.
5.  **Multiple outcome variables**: Effect sizes may vary across outcomes; report all of them.
6.  **Avoid "cherry-picking"**: Report effects for all pre-specified analyses.
7.  **Publication bias**: Published effect sizes tend to be overestimated.

---

## Quick Reference Table

| Analysis Type | Effect Size Metric | Small | Medium | Large |
|---------------|--------------------|-------|--------|-------|
| T-test        | Cohen's d          | 0.20  | 0.50   | 0.80  |
| ANOVA         | η², ω²             | 0.01  | 0.06   | 0.14  |
| ANOVA         | Cohen's f          | 0.10  | 0.25   | 0.40  |
| Correlation   | r, ρ               | 0.10  | 0.30   | 0.50  |
| Regression    | R²                 | 0.02  | 0.13   | 0.26  |
| Regression    | f²                 | 0.02  | 0.15   | 0.35  |
| Chi-square    | Cramér's V         | 0.07  | 0.21   | 0.35  |
| Chi-square (2x2)| φ                | 0.10  | 0.30   | 0.50  |

---

## Resources

- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.)
- Lakens, D. (2013). Calculating and reporting effect sizes
- Ellis, P. D. (2010). *The Essential Guide to Effect Sizes*