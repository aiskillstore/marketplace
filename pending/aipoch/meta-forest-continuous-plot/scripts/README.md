# Continuous Data Forest Plot Generation Tool

## Overview

This repository contains two scripts for generating forest plots for meta-analysis of continuous data:
- **R Version** (`forest_continuous.R`): Written in R, based on meta and metafor packages
- **Python Version** (`forest_continuous.py`): Written in Python, serves as a fallback when R execution fails

## Python Script (forest_continuous.py)

### Features
- Reads continuous data in CSV format
- Calculates standardized mean difference (SMD) and 95% confidence intervals for each study
- Performs meta-analysis using fixed-effects and random-effects models
- Computes heterogeneity indices (I², Q-test)
- Generates forest plot in PNG format
- Exports results as a CSV data table with statistical findings

### System Requirements
- Python 3.7+
- Required packages:
  - pandas
  - numpy
  - matplotlib

### Installing Dependencies

```bash
pip install pandas numpy matplotlib
```

### Usage

Basic usage:
```bash
python forest_continuous.py <csv_path> [outcome_name] [output_dir]
```

Parameter descriptions:
- `csv_path`: Path to the input CSV file (required)
- `outcome_name`: Name of the outcome measure (optional, defaults to "Outcome" or the outcome_new column from CSV)
- `output_dir`: Output directory (optional, defaults to the CSV file's directory)

### Examples

```bash
# Basic usage
python forest_continuous.py data.csv

# Specify outcome name
python forest_continuous.py data.csv "Quality of Life"

# Specify output directory
python forest_continuous.py data.csv "Quality of Life" "./output"
```

### Input Data Format

The script supports two CSV column name formats:

#### Format 1 (R script compatible)
```
study, group1_sample_size, group1_Mean, group1_SD, 
group2_sample_size, group2_Mean, group2_SD
```

#### Format 2 (Recommended)
```
Study, Mean.e, SD.e, Total.e, Mean.c, SD.c, Total.c
```

Example CSV:
```csv
Study,Mean.e,SD.e,Total.e,Mean.c,SD.c,Total.c
Study A,66.79,19.39,762,68.26,17.82,383
Study B,72.76,18.14,762,72.76,18.14,384
Study C,80.58,14.86,539,79.62,19.64,308
```

**Column Descriptions:**
- `Study`: Study identifier/name
- `Mean.e`: Mean of the intervention group
- `SD.e`: Standard deviation of the intervention group
- `Total.e`: Sample size of the intervention group
- `Mean.c`: Mean of the control group
- `SD.c`: Standard deviation of the control group
- `Total.c`: Sample size of the control group

### Output Files

The script generates two output files:

1. **Forest Plot** (`Continuity_forest_{outcome_name}.png`)
   - Displays point estimates and 95% confidence intervals for each study
   - Shows the pooled effect size (black diamond)
   - Includes a reference line at zero effect

2. **Data Table** (`Continuity_forest_{outcome_name}.csv`)
   - Contains original data for each study
   - Contains effect size and 95% confidence intervals for each study
   - Includes study weights and p-values
   - Final row contains pooled results

### Output Summary Information

Upon execution, the script displays the following summary:
- Outcome measure name
- Number of included studies
- Output file paths
- Pooled effect size (SMD), 95% confidence interval, and p-value
- Heterogeneity indices (I², Tau², Q-test p-value)

Example output:
```
═══════════════════════════════════════════
Forest Plot Generation Completed
═══════════════════════════════════════════

【Outcome Measure】Quality of Life
【Number of Studies】4

【Output Files】
• Forest Plot: ./Continuity_forest_Quality of Life.png
• Data Table: ./Continuity_forest_Quality of Life.csv

【Pooled Effect Size】
• SMD = -0.01 [-0.08; 0.05]
• P-value = 0.6539

【Heterogeneity】
• I² = 0%
• Tau² = 0
• Q-test P-value = 0.5542
═══════════════════════════════════════════
```

## Meta-Analysis Methods

### Effect Size
- **Metric**: Standardized Mean Difference (SMD)
- **Computation**: Standardized using pooled standard deviation
- **Model**: Random-effects model (DerSimonian-Laird method)

### Heterogeneity Assessment
- **I² Index**: Represents the percentage of heterogeneity
  - 0-25%: Low heterogeneity
  - 25-50%: Moderate heterogeneity
  - 50-75%: High heterogeneity
  - >75%: Very high heterogeneity
- **Tau²**: Variance component of random effects
- **Q-test**: Assesses whether significant heterogeneity exists between studies

## Troubleshooting

### Common Issues

1. **"Missing required columns" error**
   - Ensure the CSV file contains all required columns
   - Verify that column names match exactly (case-sensitive)

2. **"At least 2 studies are required" error**
   - Input data contains fewer than 2 valid studies
   - Check if a "Model" row was incorrectly included

3. **Font display issues**
   - On Windows, ensure SimHei font is installed on your system
   - On Linux/Mac, you may need to modify `plt.rcParams['font.sans-serif']` to use an available font

4. **Output directory creation failure**
   - Ensure you have appropriate permissions for the target directory
   - Check that the path contains no invalid characters

## Differences Between R and Python Scripts

### Similarities
- Use the same meta-analysis method (DerSimonian-Laird random-effects model)
- Generate forest plots and data tables in the same format
- Support the same command-line arguments

### Differences
- **Programming language**: R vs Python
- **Plotting library**: ggplot2/grid vs matplotlib
- **Appearance**: May have minor visual differences

## Version Information

- Python version: 3.7+
- pandas: ≥1.0
- numpy: ≥1.0
- matplotlib: ≥3.0

## License

Consistent with the R script

## Technical Support

If you encounter issues, please check:
1. Input data format is correct
2. All required Python packages are installed
3. Output directory is writable
4. CSV file encoding is UTF-8
