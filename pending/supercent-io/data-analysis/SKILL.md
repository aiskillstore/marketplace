---
name: data-analysis
description: Analyze datasets to extract insights, identify patterns, and generate reports. Use when exploring data, creating visualizations, or performing statistical analysis. Handles CSV, JSON, SQL queries, and Python pandas operations.
allowed-tools: Read Grep Glob Bash
metadata:
  tags: data, analysis, pandas, statistics, visualization, csv, sql
  platforms: Claude, ChatGPT, Gemini
---


# Data Analysis


## When to use this skill

- **Data exploration**: Understand a new dataset
- **Report generation**: Derive data-driven insights
- **Quality validation**: Check data consistency
- **Decision support**: Make data-driven recommendations

## Instructions

### Step 1: Load and explore data

**Python (Pandas)**:
```python
import pandas as pd
import numpy as np

# Load CSV
df = pd.read_csv('data.csv')

# Basic info
print(df.info())
print(df.describe())
print(df.head(10))

# Check missing values
print(df.isnull().sum())

# Data types
print(df.dtypes)
```

**SQL**:
```sql
-- Inspect table schema
DESCRIBE table_name;

-- Sample data
SELECT * FROM table_name LIMIT 10;

-- Basic stats
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT column_name) as unique_values,
    MIN(numeric_column) as min_val,
    MAX(numeric_column) as max_val,
    AVG(numeric_column) as avg_val
FROM table_name;
```

### Step 2: Data cleaning

```python
# Handle missing values
df['column'].fillna(df['column'].mean(), inplace=True)
df.dropna(subset=['required_column'], inplace=True)

# Remove duplicates
df.drop_duplicates(inplace=True)

# Type conversions
df['date'] = pd.to_datetime(df['date'])
df['category'] = df['category'].astype('category')

# Remove outliers (IQR method)
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['value'] >= Q1 - 1.5*IQR) & (df['value'] <= Q3 + 1.5*IQR)]
```

### Step 3: Statistical analysis

```python
# Descriptive statistics
print(df['numeric_column'].describe())

# Grouped analysis
grouped = df.groupby('category').agg({
    'value': ['mean', 'sum', 'count'],
    'other': 'nunique'
})
print(grouped)

# Correlation
correlation = df[['col1', 'col2', 'col3']].corr()
print(correlation)

# Pivot table
pivot = pd.pivot_table(df,
    values='sales',
    index='region',
    columns='month',
    aggfunc='sum'
)
```

### Step 4: Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Histogram
plt.figure(figsize=(10, 6))
df['value'].hist(bins=30)
plt.title('Distribution of Values')
plt.savefig('histogram.png')

# Boxplot
plt.figure(figsize=(10, 6))
sns.boxplot(x='category', y='value', data=df)
plt.title('Value by Category')
plt.savefig('boxplot.png')

# Heatmap (correlation)
plt.figure(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.savefig('heatmap.png')

# Time series
plt.figure(figsize=(12, 6))
df.groupby('date')['value'].sum().plot()
plt.title('Time Series of Values')
plt.savefig('timeseries.png')
```

### Step 5: Derive insights

```python
# Top/bottom analysis
top_10 = df.nlargest(10, 'value')
bottom_10 = df.nsmallest(10, 'value')

# Trend analysis
df['month'] = df['date'].dt.to_period('M')
monthly_trend = df.groupby('month')['value'].sum()
growth = monthly_trend.pct_change() * 100

# Segment analysis
segments = df.groupby('segment').agg({
    'revenue': 'sum',
    'customers': 'nunique',
    'orders': 'count'
})
segments['avg_order_value'] = segments['revenue'] / segments['orders']
```

## Output format

### Analysis report structure

```markdown
# Data Analysis Report

## 1. Dataset overview
- Dataset: [name]
- Records: X,XXX
- Columns: XX
- Date range: YYYY-MM-DD ~ YYYY-MM-DD

## 2. Key findings
- Insight 1
- Insight 2
- Insight 3

## 3. Statistical summary
| Metric | Value |
|------|-----|
| Mean | X.XX |
| Median | X.XX |
| Std dev | X.XX |

## 4. Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
```

## Best practices

1. **Understand the data first**: Learn structure and meaning before analysis
2. **Incremental analysis**: Move from simple to complex analyses
3. **Use visualization**: Use a variety of charts to spot patterns
4. **Validate assumptions**: Always verify assumptions about the data
5. **Reproducibility**: Document analysis code and results

## Constraints

### Required rules (MUST)
1. Preserve raw data (work on a copy)
2. Document the analysis process
3. Validate results

### Prohibited (MUST NOT)
1. Do not expose sensitive personal data
2. Do not draw unsupported conclusions

## References

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
