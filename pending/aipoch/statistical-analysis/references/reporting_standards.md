# Statistical Reporting Standards

This document provides guidelines for reporting statistical analyses according to APA (American Psychological Association) style, as well as general best practices for academic publishing.

## Basic Principles

1. **Transparency**: Report enough detail for others to replicate.
2. **Completeness**: Include all planned analyses and results.
3. **Honesty**: Report non-significant findings and violations of assumptions.
4. **Clarity**: Write for the audience; define technical terms.
5. **Reproducibility**: Provide code, data, or supplementary materials whenever possible.

---

## Preregistration and Planning

### What to Report (Ideally before data collection)

1. **Hypotheses**: Clearly stated, specifying directionality where appropriate.
2. **Sample Size Justification**: Power analysis or other basis.
3. **Data Collection Stopping Rules**: When will data collection stop?
4. **Variables**: All variables collected (not limited to those analyzed).
5. **Exclusion Criteria**: Rules for excluding participants/data points.
6. **Statistical Analyses**: Planned tests, including:
   - Primary analyses
   - Secondary analyses
   - Exploratory analyses (must be clearly labeled)
   - Missing data handling
   - Multiple comparison corrections
   - Assumption checks

**Why Preregister?**
- Prevents HARKing (Hypothesizing After Results are Known).
- Distinguishes confirmatory analyses from exploratory analyses.
- Increases credibility and reproducibility.

**Platforms**: OSF, AsPredicted, ClinicalTrials.gov

---

## Method Section

### Participants

**What to Report**:
- Total sample size N, including excluded participants.
- Relevant demographic information (age, gender, etc.).
- Recruitment methods.
- Inclusion/exclusion criteria.
- Attrition/dropout rates and reasons.

**Example**:
> "Participants were 150 undergraduate students (98 female, 52 male; M_age = 19.4 years, SD = 1.2, range 18-24) recruited from psychology courses in exchange for course credit. Five participants were excluded due to incomplete data (n = 3) or failing attention checks (n = 2), resulting in a final sample of 145."

### Design

**What to Report**:
- Study design (between-subjects, within-subjects, mixed design).
- Independent variables and their levels.
- Dependent variables.
- Control variables/covariates.
- Randomization procedures.
- Blinding (single-blind, double-blind).

**Example**:
> "A 2 (feedback: positive vs. negative) × 2 (timing: immediate vs. delayed) between-subjects factorial design was used. Participants were randomly assigned to conditions using a computer-generated randomization sequence. The primary outcome was task performance measured as number of correct responses (0-20 scale)."

### Measures

**What to Report**:
- Full name of measures/instruments.
- Number of items.
- Scale/scoring format.
- Scoring method.
- Reliability (Cronbach's α, ICC, etc.).
- Validity evidence (if applicable).

**Example**:
> "Depression was assessed using the Beck Depression Inventory-II (BDI-II; Beck et al., 1996), a 21-item self-report measure rated on a 4-point scale (0-3). Total scores range from 0 to 63, with higher scores indicating greater depression severity. The BDI-II demonstrated excellent internal consistency in this sample (α = .91)."

### Procedure

**What to Report**:
- Step-by-step description of participant tasks.
- Timing and duration.
- Instructions given.
- Any experimental manipulations or interventions.

**Example**:
> "Participants completed the study online via Qualtrics. After providing informed consent, they completed demographic questions, were randomly assigned to one of four conditions, completed the experimental task (approximately 15 minutes), and finished with the outcome measures and debriefing. The entire session lasted approximately 30 minutes."

### Data Analysis

**What to Report**:
- Software used (including version).
- Significance level (α).
- Tails of the test (one-tailed or two-tailed).
- Assumption checks performed.
- Missing data handling.
- Outlier handling.
- Multiple comparison corrections.
- Effect size measures used.

**Example**:
> "All analyses were conducted using Python 3.10 with scipy 1.11 and statsmodels 0.14. An alpha level of .05 was used for all significance tests. Assumptions of normality and homogeneity of variance were assessed using Shapiro-Wilk and Levene's tests, respectively. Missing data (< 2% for all variables) were handled using listwise deletion. Outliers beyond 3 SD from the mean were winsorized. For the primary ANOVA, partial eta-squared (η²_p) is reported as the effect size measure. Post hoc comparisons used Tukey's HSD to control family-wise error rate."

---

## Results Section

### Descriptive Statistics

**What to Report**:
- Sample size (report per group if applicable).
- Measures of central tendency (M, Mdn).
- Measures of dispersion (SD, IQR, range).
- Confidence intervals (where appropriate).

**Example (Continuous outcomes)**:
> "Group A (n = 48) had a mean score of 75.2 (SD = 8.5, 95% CI [72.7, 77.7]), while Group B (n = 52) scored 68.3 (SD = 9.2, 95% CI [65.7, 70.9])."

**Example (Categorical outcomes)**:
> "Of the 145 participants, 89 (61.4%) chose Option A, 42 (29.0%) chose Option B, and 14 (9.7%) chose Option C."

**Descriptive Statistics Tables**:
- Use tables for multiple variables or groups.
- Include M, SD, and n (minimum).
- Include range, skewness, and kurtosis if relevant.

---

### Assumption Checks

**What to Report**:
- Which assumptions were tested.
- Results of diagnostic tests.
- Whether assumptions were met.
- Actions taken if assumptions were violated.

**Example**:
> "Normality was assessed using Shapiro-Wilk tests. Data for Group A (W = 0.97, p = .18) and Group B (W = 0.96, p = .12) did not significantly deviate from normality. Levene's test indicated homogeneity of variance, F(1, 98) = 1.23, p = .27. Therefore, assumptions for the independent samples t-test were satisfied."

**Example (Violation of assumptions)**:
> "Shapiro-Wilk tests indicated significant departure from normality for Group C (W = 0.89, p = .003). Therefore, the non-parametric Mann-Whitney U test was used instead of the independent samples t-test."

---

### Inferential Statistics

#### T-tests

**What to Report**:
- Test statistic (t).
- Degrees of freedom.
- p-value (report exact value if p > .001, otherwise p < .001).
- Effect size (Cohen's d or Hedges' g) and its confidence interval.
- Direction of effect.
- One-tailed or two-tailed test.

**Format**: t(df) = value, p = value, d = value, 95% CI [lower, upper]

**Example (Independent samples t-test)**:
> "Group A (M = 75.2, SD = 8.5) scored significantly higher than Group B (M = 68.3, SD = 9.2), t(98) = 3.82, p < .001, d = 0.77, 95% CI [0.36, 1.18], two-tailed."

**Example (Paired samples t-test)**:
> "Scores increased significantly from pretest (M = 65.4, SD = 10.2) to posttest (M = 71.8, SD = 9.7), t(49) = 4.21, p < .001, d = 0.64, 95% CI [0.33, 0.95]."

**Example (Welch's t-test)**:
> "Due to unequal variances, Welch's t-test was used. Group A scored significantly higher than Group B, t(94.3) = 3.65, p < .001, d = 0.74."

**Example (Non-significant)**:
> "There was no significant difference between Group A (M = 72.1, SD = 8.3) and Group B (M = 70.5, SD = 8.9), t(98) = 0.91, p = .36, d = 0.18, 95% CI [-0.21, 0.57]."

---

#### Analysis of Variance (ANOVA)

**What to Report**:
- F-statistic.
- Degrees of freedom (effect, error).
- p-value.
- Effect size (η², η²_p, or ω²).
- Means and standard deviations for all groups.
- Post hoc test results (if significant).

**Format**: F(df_effect, df_error) = value, p = value, η²_p = value

**Example (One-way ANOVA)**:
> "There was a significant main effect of treatment condition on test scores, F(2, 147) = 8.45, p < .001, η²_p = .10. Post hoc comparisons using Tukey's HSD revealed that Condition A (M = 78.2, SD = 7.3) scored significantly higher than Condition B (M = 71.5, SD = 8.1, p = .002, d = 0.87) and Condition C (M = 70.1, SD = 7.9, p < .001, d = 1.07). Conditions B and C did not differ significantly (p = .52, d = 0.18)."

**Example (Factorial ANOVA)**:
> "A 2 (feedback: positive vs. negative) × 2 (timing: immediate vs. delayed) between-subjects ANOVA revealed a significant main effect of feedback, F(1, 146) = 12.34, p < .001, η²_p = .08, but no significant main effect of timing, F(1, 146) = 2.10, p = .15, η²_p = .01. Critically, the interaction was significant, F(1, 146) = 6.78, p = .01, η²_p = .04. Simple effects analysis showed that positive feedback improved performance for immediate timing (M_diff = 8.2, p < .001) but not for delayed timing (M_diff = 1.3, p = .42)."

**Example (Repeated measures ANOVA)**:
> "A one-way repeated measures ANOVA revealed a significant effect of time point on anxiety scores, F(2, 98) = 15.67, p < .001, η²_p = .24. Mauchly's test indicated that the assumption of sphericity was violated, χ²(2) = 8.45, p = .01, therefore Greenhouse-Geisser corrected values are reported (ε = 0.87). Pairwise comparisons with Bonferroni correction showed..."

---

#### Correlations

**What to Report**:
- Correlation coefficient (r or ρ).
- Sample size.
- p-value.
- Direction and strength.
- Confidence intervals.
- Coefficient of determination (r², if relevant).

**Format**: r(df) = value, p = value, 95% CI [lower, upper]

**Example (Pearson correlation)**:
> "There was a moderate positive correlation between study time and exam score, r(148) = .42, p < .001, 95% CI [.27, .55], indicating that 18% of the variance in exam scores was shared with study time (r² = .18)."

**Example (Spearman correlation)**:
> "A Spearman rank-order correlation revealed a significant positive association between class rank and motivation, ρ(118) = .38, p < .001, 95% CI [.21, .52]."

**Example (Non-significant)**:
> "There was no significant correlation between age and reaction time, r(98) = -.12, p = .23, 95% CI [-.31, .08]."

---

#### Regression

**What to Report**:
- Overall model fit (R², adjusted R², F-test).
- Coefficients for each predictor (B, SE, β, t, p).
- Effect size.
- Confidence intervals for coefficients.
- Variance Inflation Factor (if assessing multicollinearity).

**Format**: B = value, SE = value, β = value, t = value, p = value, 95% CI [lower, upper]

**Example (Simple regression)**:
> "Simple linear regression showed that study hours significantly predicted exam scores, F(1, 148) = 42.5, p < .001, R² = .22. Specifically, each additional hour of study was associated with a 2.4-point increase in exam score (B = 2.40, SE = 0.37, β = .47, t = 6.52, p < .001, 95% CI [1.67, 3.13])."

**Example (Multiple regression)**:
> "Multiple linear regression was conducted to predict exam scores from study hours, prior GPA, and attendance. The overall model was significant, F(3, 146) = 45.2, p < .001, R² = .48, adjusted R² = .47. Study hours (B = 1.80, SE = 0.31, β = .35, t = 5.78, p < .001, 95% CI [1.18, 2.42]) and prior GPA (B = 8.52, SE = 1.95, β = .28, t = 4.37, p < .001, 95% CI [4.66, 12.38]) were significant predictors, but attendance was not (B = 0.15, SE = 0.12, β = .08, t = 1.25, p = .21, 95% CI [-0.09, 0.39]). Multicollinearity was not a concern, as all VIF values were below 1.5."

**Example (Logistic Regression)**:
> "Logistic regression was conducted to predict pass/fail status from study hours. The overall model was significant, χ²(1) = 28.7, p < .001, Nagelkerke R² = .31. Each additional study hour increased the odds of passing by 1.35 times (OR = 1.35, 95% CI [1.18, 1.54], p < .001). The model correctly classified 76% of cases (sensitivity = 81%, specificity = 68%)."

---

#### Chi-Square Tests

**What to Report**:
- χ² statistic.
- Degrees of freedom.
- p-value.
- Effect size (Cramér's V or φ).
- Observed and expected frequencies (or percentages).

**Format**: χ²(df, N = total) = value, p = value, Cramér's V = value

**Example (2×2)**:
> "A chi-square test of independence revealed a significant association between treatment group and outcome, χ²(1, N = 150) = 8.45, p = .004, φ = .24. Specifically, 72% of participants in the treatment group improved compared to 48% in the control group."

**Example (Larger tables)**:
> "A chi-square test examined the relationship between education level (high school, bachelor's, graduate) and political affiliation (liberal, moderate, conservative). The association was significant, χ²(4, N = 300) = 18.7, p = .001, Cramér's V = .18, indicating a small to moderate association."

**Example (Fisher's Exact Test)**:
> "Due to expected cell counts below 5, Fisher's exact test was used. The association between treatment and outcome was significant, p = .018 (two-tailed), OR = 3.42, 95% CI [1.21, 9.64]."

---

#### Non-parametric Tests

**Mann-Whitney U Test**:
> "A Mann-Whitney U test indicated that Group A (Mdn = 75, IQR = 10) had significantly higher scores than Group B (Mdn = 68, IQR = 12), U = 845, z = 3.21, p = .001, r = .32."

**Wilcoxon Signed-Rank Test**:
> "A Wilcoxon signed-rank test showed that scores increased significantly from pretest (Mdn = 65, IQR = 15) to posttest (Mdn = 72, IQR = 14), z = 3.89, p < .001, r = .39."

**Kruskal-Wallis Test**:
> "A Kruskal-Wallis test revealed significant differences among the three conditions, H(2) = 15.7, p < .001, η² = .09. Follow-up pairwise comparisons with Bonferroni correction showed..."

---

#### Bayesian Statistics

**What to Report**:
- Priors used.
- Posterior estimates (mean/median, credible intervals).
- Bayes Factor (if hypothesis testing).
- Convergence diagnostics (R-hat, ESS).
- Posterior predictive checks.

**Example (Bayesian t-test)**:
> "A Bayesian independent samples t-test was conducted using weakly informative priors (Normal(0, 1) for mean difference). The posterior distribution of the mean difference had a mean of 6.8 (95% credible interval [3.2, 10.4]), indicating that Group A scored higher than Group B. The Bayes Factor BF₁₀ = 45.3 provided very strong evidence for a difference between groups. There was a 99.8% posterior probability that Group A's mean exceeded Group B's mean."

**Example (Bayesian regression)**:
> "A Bayesian linear regression was fitted with weakly informative priors (Normal(0, 10) for coefficients, Half-Cauchy(0, 5) for residual SD). The model showed that study hours credibly predicted exam scores (β = 0.52, 95% CI [0.38, 0.66]; 0 not included in interval). All convergence diagnostics were satisfactory (R-hat < 1.01, ESS > 1000 for all parameters). Posterior predictive checks indicated adequate model fit."

---

## Effect Sizes

### Always Report

**Reasons**:
- p-values do not reflect the magnitude of the effect.
- Required by APA and most journals.
- Necessary for meta-analysis.
- Provides context for practical significance.

**Which Effect Size Should You Choose?**
- T-tests: Cohen's d or Hedges' g
- ANOVA: η², η²_p, or ω²
- Correlations: r (is an effect size itself)
- Regression: β (standardized coefficient), R², f²
- Chi-square: Cramér's V or φ

**Include Confidence Intervals**:
- Report CIs for effect sizes whenever possible.
- Shows the precision of the estimate.
- More informative than point estimates alone.

---

## Tables and Figures

### When to Use Tables vs. Figures

**Tables**:
- When precise values are needed.
- When there are many variables/conditions.
- Descriptive statistics.
- Regression coefficients.
- Correlation matrices.

**Figures**:
- To show patterns and trends.
- Distributions.
- Interactions.
- Comparisons across groups.
- Time series.

### Figure Guidelines

**General Requirements**:
- Clear, legible labels.
- Adequate font size (≥ 10pt).
- High resolution (≥ 300 dpi for publication).
- Suitable for black and white printing (consider colorblind safety).
- Error bars (SE or 95% CI; always specify which!).
- Include legends where necessary.

**Common Figure Types**:
- Bar charts: Group comparisons (with error bars).
- Box plots: Distributions, outliers.
- Scatter plots: Correlations, relationships.
- Line graphs: Changes over time, interactions.
- Violin plots: Distributions (superior to box plots).

**Figure Caption Example**:
> "Figure 1. Mean exam scores by study condition. Error bars represent 95% confidence intervals. * p < .05, ** p < .01, *** p < .001."

### Table Guidelines

**General Requirements**:
- Clear row and column labels.
- Consistent decimal places (usually 2).
- Use horizontal lines only (no vertical lines).
- Include notes below the table for explanation.
- Italicize statistical symbols (p, M, SD, F, t, r).

**Table Example**:

**Table 1**
*Descriptive Statistics and Intercorrelations*

| Variable | M | SD | 1 | 2 | 3 |
|----------|---|----|----|----|----|
| 1. Study hours | 5.2 | 2.1 | — | | |
| 2. Prior GPA | 3.1 | 0.5 | .42** | — | |
| 3. Exam score | 75.3 | 10.2 | .47*** | .52*** | — |

*Note*. N = 150. ** p < .01. *** p < .001.

---

## Common Errors to Avoid

1. **Reporting p = .000**: Report p < .001 instead.
2. **Omitting effect sizes**: Always include them.
3. **Not reporting assumption checks**: Describe the tests and their results.
4. **Confusing statistical significance with practical significance**: Discuss both.
5. **Reporting only significant results**: Report all planned analyses.
6. **Using “prove” or “confirm”**: Use “support” or “consistent with.”
7. **Using “marginally significant” for .05 < p < .10**: It is either significant or not.
8. **Reporting p-values to only one decimal place**: Keep two (e.g., p = .03, not p = .0).
9. **Not specifying one-tailed vs. two-tailed**: Always be clear.
10. **Inconsistent rounding**: Be consistent throughout the text.

---

## Null Results

### How to Report Non-significant Findings

**Don't say**:
- "There was no effect"
- "X and Y are unrelated"
- "Groups are equivalent"

**Should say**:
- "There was no significant difference"
- "The effect was not statistically significant"
- "We did not find evidence for a relationship"

**Include the Following**:
- Exact p-values (not just "ns" or "p > .05").
- Effect sizes (show the magnitude even if not significant).
- Confidence intervals (may contain meaningful values).
- Power analysis (was the study sufficiently powered?).

**Example**:
> "Contrary to our hypothesis, there was no significant difference in creativity scores between the music (M = 72.1, SD = 8.3) and silence (M = 70.5, SD = 8.9) conditions, t(98) = 0.91, p = .36, d = 0.18, 95% CI [-0.21, 0.57]. A post hoc sensitivity analysis revealed that the study had 80% power to detect an effect of d = 0.57 or larger, suggesting the null finding may reflect insufficient power to detect small effects."

---

## Reproducibility

### Materials to Share

1. **Data**: De-identified raw data (or summary data if sensitive).
2. **Code**: Analysis scripts.
3. **Materials**: Stimuli, scales, protocols.
4. **Supplementary Materials**: Extra analyses, tables.

**Where to Share**:
- Open Science Framework (OSF)
- GitHub (for hosting code)
- Journal supplementary materials
- Institutional repositories

**Statement in the Paper**:
> "Data, analysis code, and materials are available at https://osf.io/xxxxx/"

---

## Statistical Reporting Checklist

- [ ] Sample size and demographics
- [ ] Clear description of study design
- [ ] Description of all measures and their reliability
- [ ] Detailed experimental procedure
- [ ] Specify software and version
- [ ] State Alpha level
- [ ] Report assumption checks
- [ ] Descriptive statistics (M, SD, n)
- [ ] Test statistics with degrees of freedom and p-values
- [ ] Effect sizes with confidence intervals
- [ ] Report all planned analyses (including non-significant ones)
- [ ] Correct figure/table formatting and clear labeling
- [ ] Describe multiple comparison correction methods
- [ ] Explain handling of missing data
- [ ] Discuss limitations
- [ ] Data/code availability statement

---

## Extra Resources

- APA Publication Manual (7th ed.)
- CONSORT guidelines (for RCTs)
- STROBE guidelines (for observational studies)
- PRISMA guidelines (for systematic reviews/meta-analyses)
- Wilkinson & Task Force on Statistical Inference (1999). Statistical methods in psychology journals.