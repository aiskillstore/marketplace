# Data Presentation in Clinical Reports

## Clinical Data Tables

### Table Design Principles

**General Guidelines:**
- Titles should be clear, concise, and describe the table content.
- Column headers must include units.
- Row labels should be left-aligned; data should be appropriately aligned (numbers right-aligned, text left-aligned).
- Footnotes are used to explain abbreviations, statistical symbols, and special cases.
- Maintain consistent decimal places (usually 1-2 for percentages, 1-3 for continuous variables).
- Formatting should be consistent throughout the document.

**Title Placement:**
- Place above the table.
- Number sequentially (Table 1, Table 2, etc.).
- Should be sufficiently descriptive to stand alone from the text.

**Footnote Symbols (in order):**
- *, †, ‡, §, ||, ¶, #
- Or use superscript letters (a, b, c...).
- Superscript numbers may be used if they do not conflict with references.

### Demographic and Baseline Characteristics Table

**Purpose:** To describe the study population at baseline.

**Standard Format:**

```
Table 1. Baseline Demographics and Clinical Characteristics

Characteristic                  Treatment Group    Control Group    Total
                               (N=150)            (N=145)          (N=295)
─────────────────────────────────────────────────────────────────────────
Age, years
  Mean (SD)                    64.2 (8.5)         63.8 (9.1)       64.0 (8.8)
  Median (IQR)                 65 (58-71)         64 (57-70)       64 (58-71)
  Range                        45-82              43-85            43-85

Sex, n (%)
  Male                         95 (63.3)          88 (60.7)        183 (62.0)
  Female                       55 (36.7)          57 (39.3)        112 (38.0)

Race, n (%)
  White                        110 (73.3)         105 (72.4)       215 (72.9)
  Black/African American       25 (16.7)          28 (19.3)        53 (18.0)
  Asian                        10 (6.7)           8 (5.5)          18 (6.1)
  Other                        5 (3.3)            4 (2.8)          9 (3.0)

BMI, kg/m²
  Mean (SD)                    28.5 (4.2)         28.1 (4.5)       28.3 (4.4)

Baseline HbA1c, %
  Mean (SD)                    8.9 (1.2)          9.0 (1.3)        9.0 (1.2)

Disease duration, years
  Median (IQR)                 6 (3-10)           5 (3-9)          6 (3-10)

Prior medications, n (%)
  Metformin                    135 (90.0)         130 (89.7)       265 (89.8)
  Sulfonylurea                 45 (30.0)          42 (29.0)        87 (29.5)
  Insulin                      20 (13.3)          18 (12.4)        38 (12.9)
─────────────────────────────────────────────────────────────────────────
SD = standard deviation; IQR = interquartile range; BMI = body mass index;
HbA1c = hemoglobin A1c
```

**Key Elements:**
- Sample size for each group (N=).
- Continuous variables: Mean (SD), Median (IQR), Range.
- Categorical variables: n (%).
- P-values are typically not provided for baseline comparisons (controversial, but generally not recommended).

### Efficacy Outcome Tables

**Purpose:** To present primary and secondary endpoint results.

**Example:**

```
Table 2. Primary and Secondary Efficacy Endpoints at Week 24

Endpoint                           Treatment      Control        Difference    P-value
                                   (N=150)        (N=145)        (95% CI)
──────────────────────────────────────────────────────────────────────────────────
Primary Endpoint
Change in HbA1c from baseline, %
  Mean (SE)                        -1.8 (0.1)     -0.6 (0.1)     -1.2          <0.001
  95% CI                           (-2.0, -1.6)   (-0.8, -0.4)   (-1.5, -0.9)

Secondary Endpoints
Change in FPG, mg/dL
  Mean (SE)                        -42.5 (3.2)    -15.2 (3.4)    -27.3         <0.001
  95% CI                           (-48.8, -36.2) (-21.9, -8.5)  (-36.4, -18.2)

% achieving HbA1c <7%
  n (%)                            78 (52.0)      25 (17.2)      -              <0.001
  95% CI                           (43.9, 60.1)   (11.4, 24.5)   

Change in body weight, kg
  Mean (SE)                        -3.2 (0.4)     -0.5 (0.4)     -2.7          <0.001
  95% CI                           (-4.0, -2.4)   (-1.3, 0.3)    (-3.8, -1.6)
──────────────────────────────────────────────────────────────────────────────
SE = standard error; CI = confidence interval; HbA1c = hemoglobin A1c; 
FPG = fasting plasma glucose
```

**Statistical Presentation:**
- Point estimates with measures of precision (SE or CI).
- P-values (considering multiplicity adjustments).
- Effect sizes (differences or ratios) and their 95% CIs.
- Note significance levels (e.g., p<0.05, p<0.01, p<0.001).

### Adverse Event Tables

**Purpose:** To summarize safety data.

**Example:**

```
Table 3. Summary of Adverse Events

Event Category                        Treatment     Control       P-value
                                      (N=150)       (N=145)
                                      n (%)         n (%)
──────────────────────────────────────────────────────────────────────────
Any adverse event                     120 (80.0)    95 (65.5)     0.004

Treatment-related adverse events       85 (56.7)    42 (29.0)     <0.001

Serious adverse events                 12 (8.0)     8 (5.5)       0.412

Adverse events leading to              8 (5.3)      4 (2.8)       0.257
discontinuation

Deaths                                 0 (0.0)      1 (0.7)       0.492

Common adverse events (≥5% in any group)
  Nausea                              45 (30.0)     12 (8.3)      <0.001
  Diarrhea                            38 (25.3)     10 (6.9)      <0.001
  Headache                            22 (14.7)     18 (12.4)     0.568
  Hypoglycemia                        18 (12.0)     5 (3.4)       0.007
  Dizziness                           12 (8.0)      8 (5.5)       0.412
──────────────────────────────────────────────────────────────────────────
Adverse events coded using MedDRA version 24.0
```

**Key Elements:**
- Overall AE summary.
- Highlight serious AEs (SAEs).
- Report deaths.
- Common AEs (usually setting a threshold of ≥5% or ≥10%).
- Specify the MedDRA coding version.

### Laboratory Abnormality Tables

**Shift table showing changes from baseline:**

```
Table 4. Laboratory Values Meeting Predefined Criteria for Abnormality

Laboratory Parameter                 Treatment      Control
                                     (N=150)        (N=145)
                                     n (%)          n (%)
──────────────────────────────────────────────────────────────────────────
ALT >3× ULN                          8 (5.3)        3 (2.1)
AST >3× ULN                          5 (3.3)        2 (1.4)
Total bilirubin >2× ULN              2 (1.3)        1 (0.7)
Creatinine >1.5× baseline            12 (8.0)       5 (3.4)
Hemoglobin <10 g/dL                  3 (2.0)        2 (1.4)
Platelets <100 × 10³/μL              1 (0.7)        0 (0.0)
──────────────────────────────────────────────────────────────────────────
ULN = upper limit of normal; ALT = alanine aminotransferase; 
AST = aspartate aminotransferase
```

### Patient Disposition Table (CONSORT Format)

```
Table 5. Patient Disposition

Disposition                              Treatment     Control       Total
                                         (N=150)       (N=145)       (N=295)
────────────────────────────────────────────────────────────────────────────
Screened                                 -             -             425

Randomized                               150           145           295

Completed study                          135 (90.0)    130 (89.7)    265 (89.8)

Discontinued, n (%)                      15 (10.0)     15 (10.3)     30 (10.2)
  Adverse event                          8 (5.3)       4 (2.8)       12 (4.1)
  Lack of efficacy                       2 (1.3)       5 (3.4)       7 (2.4)
  Lost to follow-up                      3 (2.0)       4 (2.8)       7 (2.4)
  Withdrawal of consent                  2 (1.3)       2 (1.4)       4 (1.4)

Included in efficacy analysis
  ITT population                         150 (100)     145 (100)     295 (100)
  Per-protocol population                142 (94.7)    138 (95.2)    280 (94.9)

Included in safety analysis              150 (100)     145 (100)     295 (100)
────────────────────────────────────────────────────────────────────────────
ITT = intent-to-treat
```

## Clinical Data Figures

### Figure Design Principles

**General Guidelines:**
- Clear, concise captions/legends should be placed below the figure.
- Number sequentially (Figure 1, Figure 2, etc.).
- Axis labels must include units.
- Font size should be legible (minimum 8-10 points).
- High resolution (300 dpi for print, 150 dpi for web).
- Use colorblind-friendly color schemes.
- Compatible with black and white printing (use different symbols/patterns).

**Figure Captions:**
- Describe the figure content.
- Explain symbols, error bars, and statistical annotations.
- Define abbreviations.
- Provide interpretive context.

### CONSORT Flow Diagram

**Purpose:** To show the flow of patients through a randomized trial.

```
                    Assessed for eligibility (n=425)
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
    Excluded (n=130)                                │
    • Did not meet inclusion criteria (n=85)        │
    • Declined to participate (n=32)                │
    • Other reasons (n=13)                          │
                                                    │
                                           Randomized (n=295)
                                                    │
                    ┌───────────────────────────────┴───────────────────────────────┐
                    │                                                               │
        Allocated to treatment group (n=150)                         Allocated to control group (n=145)
        • Received allocated intervention (n=148)                    • Received allocated intervention (n=143)
        • Did not receive allocated intervention (n=2)                • Did not receive allocated intervention (n=2)
          Reason: Withdrawal of consent prior to treatment             Reason: Withdrawal of consent prior to treatment
                    │                                                               │
        ┌───────────┴────────────┐                                  ┌──────────────┴─────────────┐
        │                        │                                  │                            │
    Lost to follow-up (n=3)  Discontinued (n=12)             Lost to follow-up (n=4)  Discontinued (n=11)
                             • Adverse event (n=8)                                   • Adverse event (n=4)
                             • Lack of efficacy (n=2)                                • Lack of efficacy (n=5)
                             • Withdrawal of consent (n=2)                           • Withdrawal of consent (n=2)
                    │                                                               │
            Analyzed (n=150)                                               Analyzed (n=145)
            • ITT analysis (n=150)                                         • ITT analysis (n=145)
            • Per-protocol analysis (n=142)                                • Per-protocol analysis (n=138)
            • Excluded from analysis (n=0)                                 • Excluded from analysis (n=0)
```

### Kaplan-Meier Survival Curves

**Purpose:** To present time-to-event data.

**Elements:**
- X-axis: Time (weeks, months, years).
- Y-axis: Event-free survival probability (0 to 1 or 0% to 100%).
- Separate curves for each treatment group.
- Mark censored observations (usually with vertical ticks).
- Include a table of numbers at risk below the graph.
- Indicate median survival time.
- Log-rank p-value.
- Hazard ratio (HR) and its 95% CI.

**Figure Caption Example:**
```
Figure 1. Kaplan-Meier Curves for Overall Survival

Kaplan-Meier estimates of overall survival for the treatment and control groups.
Ticks represent censored observations. Numbers at risk are shown below the graph.
Log-rank p<0.001. Median survival: treatment group 24.5 months (95% CI: 22.1-26.8),
control group 18.2 months (95% CI: 16.5-20.1). Hazard ratio 0.68 (95% CI: 0.55-0.84).
```

### Forest Plot

**Purpose:** To present results of subgroup analyses or meta-analyses.

**Elements:**
- Point estimates (squares or diamonds).
- Symbol size proportional to precision (inverse of variance) or sample size.
- Horizontal lines represent 95% CIs.
- Vertical line represents the null effect (HR=1.0, OR=1.0, or difference=0).
- Subgroup labels on the left.
- Effect size values on the right.
- Overall estimate (if a meta-analysis).
- Heterogeneity statistics (I², p-value).

**Figure Caption Example:**
```
Figure 2. Forest Plot of Treatment Effect by Subgroup

Effect of treatment vs. control on the primary endpoint by prespecified subgroups.
Squares represent point estimates; horizontal lines represent 95% confidence intervals.
Square size is proportional to the subgroup sample size. The overall effect is represented by a diamond.
Interaction p-values are used to test for heterogeneity of treatment effects across subgroups.
```

### Box Plots

**Purpose:** To show the distribution of continuous variables.

**Elements:**
- Box: IQR (25th to 75th percentiles).
- Line within the box: Median.
- Whiskers: Extend to the most extreme data points within 1.5 × IQR.
- Outliers: Points beyond the whiskers (usually shown as circles).
- X-axis: Groups or time points.
- Y-axis: Continuous variable with units.

### Scatter Plots with Regression Lines

**Purpose:** To show the relationship between two continuous variables.

**Elements:**
- X-axis: Independent variable.
- Y-axis: Dependent variable.
- Individual data points.
- Regression line (if applicable).
- Regression equation.
- R² value.
- P-value for the slope.
- 95% confidence interval for the regression line (optional, shown as a shaded area).

### Spaghetti Plots

**Purpose:** To show individual trajectories over time.

**Elements:**
- X-axis: Time.
- Y-axis: Outcome variable.
- Individual patient lines (often semi-transparent).
- Mean trajectory (bold line).
- Different colors for different treatment groups.

### Bar Charts

**Purpose:** To compare proportions or means across groups.

**Elements:**
- Clear gaps between bars.
- Error bars (SEM or 95% CI).
- Y-axis starts at 0 (never truncate the axis in bar charts).
- X-axis: Group labels.
- Y-axis: Numerical labels with units.
- Annotate statistical significance (p-values or asterisks).

**Avoid:**
- 3D bar charts (distorts perception).
- Excessive decoration.
- Truncating the Y-axis.

### Line Graphs

**Purpose:** To show changes over time.

**Elements:**
- X-axis: Time (intervals should be consistent).
- Y-axis: Outcome variable.
- Separate lines for each group (different colors/patterns).
- Mark data points (circles, squares, triangles).
- Error bars at each time point (SE or 95% CI).
- Legend identifying groups.
- Gridlines (optional, light gray).

### Histograms

**Purpose:** To show the distribution of a continuous variable.

**Elements:**
- X-axis: Variable (divided into bins).
- Y-axis: Frequency or density.
- Appropriate bin width (not too few or too many).
- Overlay a normal distribution curve (if testing for normality).

## Special Considerations for Clinical Data

### Reporting Proportions

**Numerator and Denominator:**
- Always provide both: 25/100 (25%).
- Do not provide only the percentage (25%).

**Percentages:**
- If n < 100, do not use decimal places.
- If n ≥ 100, use 1 decimal place.
- Percentages should never be reported with more than 1 decimal place.

**Confidence Intervals for Proportions:**
- Use Wilson score intervals or exact binomial (preferred over Wald for small samples).
- Always report alongside the percentage.

### Reporting Continuous Data

**Measures of Central Tendency:**
- Use mean for normally distributed data.
- Use median for skewed or ordinal data.
- Report both if the distribution is unknown.

**Measures of Dispersion:**
- **Standard Deviation (SD)**: Describes data variability.
- **Standard Error (SE)**: Describes the precision of the mean estimate.
- **95% Confidence Interval**: Preferred for inferential statistics.
- **Interquartile Range (IQR)**: Used with the median for skewed data.
- **Range**: Minimum to maximum.

**When to Use:**
- Descriptive statistics → Mean (SD) or Median (IQR).
- Inferential statistics → Mean (95% CI) or Mean (SE).
- Never use ± without specifying whether it is SD, SE, or CI.

### Reporting P-values

**Reporting Guidelines:**
- Report exact p-values to 2-3 decimal places (p=0.042).
- For very small p-values, use p<0.001 (not p=0.000).
- Do not report as "NS" or "p=NS".
- For non-significant results, report the exact p-value (p=0.18, not p>0.05).
- Specify two-sided tests unless a one-sided test was prespecified.
- Correct for multiple comparisons when appropriate.
- Report the significance threshold used (standard is α=0.05).

**Avoid:**
- p<0.05 (exact values should be reported).
- p=0.00 (impossible).
- Too many decimal places (p=0.04235891).

### Indicators of Statistical Significance

**Options:**
1. Report p-values in tables.
2. Use asterisks with a legend:
   - *p<0.05
   - **p<0.01
   - ***p<0.001
3. Use confidence intervals (preferred).

### Confidence Intervals

**Reporting:**
- 95% CI is the standard format.
- Format: (lower limit, upper limit).
- Or: lower limit to upper limit.
- Or: lower limit-upper limit.

**Interpretation:**
- Significant if the CI for a difference does not include 0.
- Significant if the CI for a ratio does not include 1.
- The width of the CI reflects precision.

### Missing Data

**Clearly Mark:**
- Use footnotes to explain missing data.
- Specify if the analysis is a complete-case analysis.
- Describe the specific method if imputation was used.
- Report the amount of missing data for each variable.

### Decimal Places and Rounding

**General Rules:**
- Reporting should match the precision of measurement.
- Maintain consistent decimal places within tables.
- P-values to 2-3 decimal places.
- Percentages to 0-1 decimal places.
- Means/medians to 1-2 decimal places.
- Include appropriate significant figures.

## Graphing Software

**Statistical Software:**
- R (ggplot2) - Highly customizable.
- GraphPad Prism - User-friendly for biomedicine.
- SAS, Stata, SPSS - Comprehensive statistical packages.
- Python (matplotlib, seaborn) - Flexible and powerful.

**General Graphics Software:**
- Adobe Illustrator - Professional publication quality.
- Inkscape - Free vector graphics editor.
- PowerPoint - Basic charts, easy to use.
- BioRender - Biological schematics and illustrations.

## Color Schemes

**Colorblind-Friendly Palettes:**
- Avoid red-green combinations.
- Use blue-orange or blue-yellow combinations.
- Combine with shape/pattern differences.
- Test charts in grayscale.

**Recommended Palettes:**
- ColorBrewer (specifically designed for data visualization).
- Viridis (perceptually uniform).
- IBM colorblind-safe palette.

## Image Quality Standards

**Resolution:**
- 300 dpi for print publication.
- 150 dpi for web/screen.
- Vector graphics (PDF, SVG) are preferred for charts.

**File Formats:**
- TIFF or EPS for print.
- PNG for web.
- PDF for vector graphics.
- JPEG (high quality) is acceptable for photographs.

**Image Editing:**
- Data manipulation is strictly prohibited.
- Only global adjustments to brightness, contrast, and color balance are allowed.
- Document all adjustments.
- Provide raw images if requested.

---

This reference document provides comprehensive guidance for presenting clinical data in tables and figures, following best practices and publication standards. Use these guidelines to create clear, accurate, and professional clinical data presentations.