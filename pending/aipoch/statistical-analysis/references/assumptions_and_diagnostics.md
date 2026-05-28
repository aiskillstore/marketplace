# Statistical Assumptions and Diagnostic Procedures

This document provides comprehensive guidance for checking and validating statistical assumptions for various analyses.

## General Principles

1. **Always check assumptions before interpreting test results**
2. **Use multiple diagnostic methods** (Visualizations + Formal tests)
3. **Consider robustness**: Certain tests are robust to violations of assumptions under specific conditions
4. **Document all assumption checking processes in the analysis report**
5. **Report violations and the remedial measures taken**

## Common Assumptions Across Tests

### 1. Independence of Observations

**Meaning**: Each observation is independent; the measurement of one subject does not influence the measurement of another.

**How to check**:
- Review study design and data collection procedures
- For time series: Check autocorrelation (ACF/PACF plots, Durbin-Watson test)
- For clustered data: Consider the Intraclass Correlation Coefficient (ICC)

**If violated**:
- Use mixed-effects models for clustered/stratified data
- Use time series methods for time-dependent data
- Use Generalized Estimating Equations (GEE) for correlated data

**Severity**: High — Violation of this assumption severely inflates Type I error.

---

### 2. Normality

**Meaning**: Data or residuals follow a normal (Gaussian) distribution.

**When needed**:
- t-tests (for small samples; robust when n > 30 per group)
- ANOVA (for small samples; robust when n > 30 per group)
- Linear regression (specifically for residuals)
- Certain correlation tests (Pearson)

**How to check**:

**Visual methods** (Preferred):
- Q-Q (Quantile-Quantile) plot: Points should fall on the diagonal line
- Histograms with overlaid normal curves
- Kernel density plots

**Formal tests** (Secondary):
- Shapiro-Wilk test (Recommended for n < 50)
- Kolmogorov-Smirnov test
- Anderson-Darling test

**Python Implementation**:
```python
from scipy import stats
import matplotlib.pyplot as plt

# Shapiro-Wilk test
statistic, p_value = stats.shapiro(data)

# Q-Q plot
stats.probplot(data, dist="norm", plot=plt)
```

**Interpretation Guide**:
- When n < 30: Both visualizations and formal tests are important
- When 30 ≤ n < 100: Rely primarily on visual checks, supplemented by formal tests
- When n ≥ 100: Formal tests are often too sensitive; rely on visual checks
- Check for severe skewness, outliers, or bimodal distributions

**If violated**:
- **Mild violation** (slight skew): Proceed if n > 30 per group
- **Moderate violation**: Use non-parametric alternatives (Mann-Whitney, Kruskal-Wallis, Wilcoxon)
- **Severe violation**:
  - Data transformation (Log, Square Root, Box-Cox)
  - Use non-parametric methods
  - Use robust regression methods
  - Consider Bootstrapping

**Severity**: Medium — Parametric tests are often robust to mild violations if sample sizes are sufficient.

---

### 3. Homogeneity of Variance (Homoscedasticity)

**Meaning**: The variance is equal across groups or across the range of predictor variables.

**When needed**:
- Independent samples t-test
- ANOVA
- Linear regression (constant variance of residuals)

**How to check**:

**Visual methods** (Preferred):
- Boxplots by group (for t-tests/ANOVA)
- Residuals vs. Fitted values plot (for regression) — should show random scatter
- Scale-location plot (Square root of standardized residuals vs. fitted values)

**Formal tests** (Secondary):
- Levene's test (Robust to non-normality)
- Bartlett's test (Sensitive to non-normality, not recommended)
- Brown-Forsythe test (A variant of Levene's based on the median)
- Breusch-Pagan test (For regression)

**Python Implementation**:
```python
from scipy import stats
import pingouin as pg

# Levene's test
statistic, p_value = stats.levene(group1, group2, group3)

# For regression
# Breusch-Pagan test
from statsmodels.stats.diagnostic import het_breuschpagan
_, p_value, _, _ = het_breuschpagan(residuals, exog)
```

**Interpretation Guide**:
- Variance ratio (Max/Min) < 2-3: Generally acceptable
- For ANOVA: The test is robust if sample sizes are equal across groups
- For regression: Check for "funnel" shapes in residual plots

**If violated**:
- **t-test**: Use Welch's t-test (does not assume equal variances)
- **ANOVA**: Use Welch's ANOVA or Brown-Forsythe ANOVA
- **Regression**:
  - Transform the dependent variable (Log, Square Root)
  - Use Weighted Least Squares (WLS)
  - Use robust standard errors (HC3)
  - Use Generalized Linear Models (GLM) with an appropriate variance function

**Severity**: Medium — Tests can remain robust in the case of equal sample sizes.

---

## Assumptions for Specific Tests

### T-Tests

**Assumptions**:
1. Independence of observations
2. Normality (Independent t-test requires normality for each group; Paired t-test requires normality for the differences)
3. Homogeneity of variance (Independent t-test only)

**Diagnostic Workflow**:
```python
import scipy.stats as stats
import pingouin as pg

# Check normality for each group
stats.shapiro(group1)
stats.shapiro(group2)

# Check homogeneity of variance
stats.levene(group1, group2)

# If assumptions violated:
# Option 1: Welch's t-test (unequal variances)
pg.ttest(group1, group2, correction=False)  # Welch's

# Option 2: Non-parametric alternative
pg.mwu(group1, group2)  # Mann-Whitney U
```

---

### ANOVA

**Assumptions**:
1. Independence of observations within and between groups
2. Normality of data within each group
3. Homogeneity of variance across groups

**Extra Considerations**:
- For Repeated Measures ANOVA: Sphericity assumption (Mauchly's test)

**Diagnostic Workflow**:
```python
import pingouin as pg

# Check normality per group
for group in df['group'].unique():
    data = df[df['group'] == group]['value']
    stats.shapiro(data)

# Check homogeneity of variance
pg.homoscedasticity(df, dv='value', group='group')

# For repeated measures: Check sphericity
# Automatically tested in pingouin's rm_anova
```

**If Sphericity is violated** (Repeated Measures):
- Greenhouse-Geisser correction (ε < 0.75)
- Huynh-Feldt correction (ε > 0.75)
- Use multivariate methods (MANOVA)

---

### Linear Regression

**Assumptions**:
1. **Linearity**: The relationship between X and Y is linear
2. **Independence**: Residuals are independent of each other
3. **Homoscedasticity**: Constant variance of residuals
4. **Normality**: Residuals are normally distributed
5. **No Multicollinearity**: Predictors are not highly correlated (for multiple regression)

**Diagnostic Workflow**:

**1. Linearity**:
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Scatter plots of Y vs each X
# Residuals vs. fitted values (should be randomly scattered)
plt.scatter(fitted_values, residuals)
plt.axhline(y=0, color='r', linestyle='--')
```

**2. Independence**:
```python
from statsmodels.stats.stattools import durbin_watson

# Durbin-Watson test (for time series)
dw_statistic = durbin_watson(residuals)
# Values between 1.5-2.5 suggest independence
```

**3. Homoscedasticity**:
```python
# Breusch-Pagan test
from statsmodels.stats.diagnostic import het_breuschpagan
_, p_value, _, _ = het_breuschpagan(residuals, exog)

# Visual: Scale-location plot
plt.scatter(fitted_values, np.sqrt(np.abs(std_residuals)))
```

**4. Normality of Residuals**:
```python
# Q-Q plot of residuals
stats.probplot(residuals, dist="norm", plot=plt)

# Shapiro-Wilk test
stats.shapiro(residuals)
```

**5. Multicollinearity**:
```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Calculate VIF for each predictor
vif_data = pd.DataFrame()
vif_data["feature"] = X.columns
vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(len(X.columns))]

# VIF > 10 indicates severe multicollinearity
# VIF > 5 indicates moderate multicollinearity
```

**If violated**:
- **Non-linearity**: Add polynomial terms, use GAM, or transform variables
- **Heteroscedasticity**: Transform Y, use WLS, use robust standard errors (SE)
- **Non-normal residuals**: Transform Y, use robust methods, check for outliers
- **Multicollinearity**: Remove correlated predictors, use PCA, or Ridge regression

---

### Logistic Regression

**Assumptions**:
1. **Independence**: Observations are independent
2. **Linearity in Logit**: Linear relationship between log-odds and continuous predictors
3. **No Perfect Multicollinearity**: Predictors are not perfectly correlated
4. **Large Sample Size**: At least 10-20 events per predictor variable

**Diagnostic Workflow**:

**1. Linearity in Logit**:
```python
# Box-Tidwell test: Add interaction with log of continuous predictor
# If interaction is significant, linearity violated
```

**2. Multicollinearity**:
```python
# Use VIF as in linear regression
```

**3. Influential Observations**:
```python
# Cook's distance, DFBetas, leverage
from statsmodels.stats.outliers_influence import OLSInfluence

influence = OLSInfluence(model)
cooks_d = influence.cooks_distance
```

**4. Model Fit**:
```python
# Hosmer-Lemeshow test
# Pseudo R-squared
# Classification metrics (accuracy, AUC-ROC)
```

---

## Outlier Detection

**Methods**:
1. **Visualization**: Boxplots, Scatter plots
2. **Statistical**:
   - Z-scores: |z| > 3 indicates an outlier
   - IQR Method: Values < Q1 - 1.5×IQR or > Q3 + 1.5×IQR
   - Modified Z-score using Median Absolute Deviation (MAD) (robust to outliers)

**For Regression Analysis**:
- **Leverage**: High leverage points (hat values)
- **Influence**: Cook's distance > 4/n indicates influential points
- **Outliers**: Studentized residuals > ±3

**Actions**:
1. Investigate if there are data entry errors
2. Consider if the outlier is a valid observation
3. Report sensitivity analysis (results with and without outliers)
4. Use robust methods if outliers are legitimate

---

## Sample Size Considerations

### Minimum Sample Sizes (Rules of Thumb)

- **T-tests**: n ≥ 30 per group for robustness to non-normality
- **ANOVA**: n ≥ 30 per group
- **Correlation**: n ≥ 30 for sufficient power
- **Simple Regression**: n ≥ 50
- **Multiple Regression**: n ≥ 10-20 per predictor (minimum 10 + k predictors)
- **Logistic Regression**: At least 10-20 events per predictor

### Small Sample Considerations

For small samples:
- Assumptions become much more critical
- Use exact tests whenever possible (Fisher's exact, exact logistic regression)
- Consider non-parametric alternatives
- Use Permutation tests or Bootstrapping
- Be conservative in interpreting results

---

## Reporting Assumption Checks

When reporting analysis results, include:

1. **Assumption Statement**: List all assumptions that were tested
2. **Methods Used**: Describe the visualizations and formal tests employed
3. **Diagnostic Results**: Report test statistics and p-values
4. **Assessment**: State whether assumptions were met or violated
5. **Actions Taken**: If violated, describe remedial measures (transformations, alternative tests, robust methods)

**Example Reporting Statement**:
> "Normality was assessed via Shapiro-Wilk tests and Q-Q plots. Data for Group A (W = 0.97, p = .18) and Group B (W = 0.96, p = .12) did not show significant deviations from normality. Homogeneity of variance was assessed using Levene's test and was non-significant (F(1, 58) = 1.23, p = .27), indicating equal variances between groups. Thus, assumptions for the independent samples t-test were met."