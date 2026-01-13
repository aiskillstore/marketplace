---
name: report-generator
description: Generate professional markdown and HTML reports from data with charts, tables, and analysis.
---

# Report Generator Skill

Generate professional markdown and HTML reports from data with charts, tables, and analysis.

## Instructions

You are a report generation expert. When invoked:

1. **Analyze Data**:
   - Understand data structure and content
   - Identify key metrics and insights
   - Calculate statistics and trends
   - Detect patterns and anomalies
   - Generate executive summaries

2. **Create Report Structure**:
   - Design clear, logical sections
   - Create table of contents
   - Add executive summary
   - Include detailed analysis
   - Provide recommendations

3. **Generate Visualizations**:
   - Create tables for structured data
   - Generate charts (bar, line, pie, scatter)
   - Add badges and indicators
   - Include code blocks and examples
   - Format numbers and percentages

4. **Format Output**:
   - Generate markdown reports
   - Create HTML reports with styling
   - Export to PDF
   - Add branding and customization
   - Ensure responsive design

## Usage Examples

```
@report-generator data.csv
@report-generator --format html
@report-generator --template executive-summary
@report-generator --charts --pdf
@report-generator --compare baseline.json current.json
```

## Report Types

### Executive Summary Report

```python
def generate_executive_summary(data, title="Executive Summary"):
    """
    Generate high-level executive summary report
    """
    from datetime import datetime

    report = f"""# {title}
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## Key Highlights

"""

    # Calculate key metrics
    metrics = calculate_key_metrics(data)

    for metric in metrics:
        icon = "✅" if metric['status'] == 'good' else "⚠️" if metric['status'] == 'warning' else "❌"
        report += f"{icon} **{metric['name']}**: {metric['value']}\n"

    report += f"""

---

## Performance Overview

| Metric | Current | Previous | Change |
|--------|---------|----------|--------|
"""

    for metric in metrics:
        if 'previous' in metric:
            change = calculate_change(metric['current'], metric['previous'])
            arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
            color = "green" if change > 0 else "red" if change < 0 else "gray"

            report += f"| {metric['name']} | {metric['current']:,} | {metric['previous']:,} | {arrow} {abs(change):.1f}% |\n"

    report += """

---

## Recommendations

"""

    recommendations = generate_recommendations(metrics)
    for i, rec in enumerate(recommendations, 1):
        priority = rec.get('priority', 'medium')
        emoji = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"

        report += f"{i}. {emoji} **{rec['title']}**\n"
        report += f"   {rec['description']}\n\n"

    return report
```

### Data Analysis Report

```python
import pandas as pd
import numpy as np
from datetime import datetime

def generate_data_analysis_report(df, title="Data Analysis Report"):
    """
    Generate comprehensive data analysis report
    """

    report = f"""# {title}
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Dataset:** {len(df):,} rows × {len(df.columns)} columns

---

## Table of Contents
1. [Dataset Overview](#dataset-overview)
2. [Data Quality](#data-quality)
3. [Statistical Summary](#statistical-summary)
4. [Distributions](#distributions)
5. [Correlations](#correlations)
6. [Insights](#insights)

---

## Dataset Overview

### Basic Information
- **Total Rows:** {len(df):,}
- **Total Columns:** {len(df.columns)}
- **Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB
- **Duplicate Rows:** {df.duplicated().sum():,}

### Column Information

| Column | Type | Non-Null | Unique | Sample Values |
|--------|------|----------|--------|---------------|
"""

    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].count()
        unique = df[col].nunique()
        samples = df[col].dropna().head(3).tolist()
        sample_str = ", ".join(str(s) for s in samples)

        report += f"| {col} | {dtype} | {non_null:,} | {unique:,} | {sample_str} |\n"

    report += """

---

## Data Quality

### Missing Values

"""

    missing = df.isnull().sum()
    if missing.sum() > 0:
        report += "| Column | Missing Count | Missing % |\n"
        report += "|--------|---------------|----------|\n"

        for col in missing[missing > 0].index:
            count = missing[col]
            pct = (count / len(df)) * 100
            report += f"| {col} | {count:,} | {pct:.1f}% |\n"
    else:
        report += "✅ No missing values detected.\n"

    report += "\n### Data Type Issues\n\n"

    # Check for potential type issues
    type_issues = []

    for col in df.select_dtypes(include=['object']):
        # Check if column should be numeric
        try:
            pd.to_numeric(df[col], errors='raise')
            type_issues.append(f"- `{col}` appears to be numeric but stored as string")
        except:
            pass

        # Check if column should be datetime
        try:
            pd.to_datetime(df[col], errors='raise')
            if df[col].str.contains(r'\d{4}-\d{2}-\d{2}').any():
                type_issues.append(f"- `{col}` appears to be datetime but stored as string")
        except:
            pass

    if type_issues:
        report += "\n".join(type_issues) + "\n"
    else:
        report += "✅ No data type issues detected.\n"

    report += """

---

## Statistical Summary

### Numeric Columns

"""

    # Add statistics for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) > 0:
        stats = df[numeric_cols].describe()
        report += stats.to_markdown() + "\n"

        # Add additional statistics
        report += "\n### Additional Statistics\n\n"
        report += "| Column | Median | Mode | Std Dev | Variance |\n"
        report += "|--------|--------|------|---------|----------|\n"

        for col in numeric_cols:
            median = df[col].median()
            mode = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
            std = df[col].std()
            var = df[col].var()

            report += f"| {col} | {median:.2f} | {mode} | {std:.2f} | {var:.2f} |\n"

    report += """

### Categorical Columns

"""

    categorical_cols = df.select_dtypes(include=['object']).columns

    if len(categorical_cols) > 0:
        for col in categorical_cols[:5]:  # Limit to first 5
            report += f"\n#### {col}\n\n"

            value_counts = df[col].value_counts().head(10)

            report += "| Value | Count | Percentage |\n"
            report += "|-------|-------|------------|\n"

            for value, count in value_counts.items():
                pct = (count / len(df)) * 100
                report += f"| {value} | {count:,} | {pct:.1f}% |\n"

    report += """

---

## Distributions

"""

    # Analyze distributions of numeric columns
    for col in numeric_cols[:5]:  # Limit to first 5
        report += f"\n### {col} Distribution\n\n"

        q1 = df[col].quantile(0.25)
        q2 = df[col].quantile(0.50)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        # Detect outliers
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

        report += f"""
**Quartiles:**
- Q1 (25%): {q1:.2f}
- Q2 (50%, Median): {q2:.2f}
- Q3 (75%): {q3:.2f}
- IQR: {iqr:.2f}

**Outliers:** {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)
- Lower bound: {lower_bound:.2f}
- Upper bound: {upper_bound:.2f}

"""

    report += """

---

## Correlations

"""

    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()

        report += "\n### Correlation Matrix\n\n"
        report += corr_matrix.to_markdown() + "\n"

        # Find strong correlations
        report += "\n### Strong Correlations (|r| > 0.7)\n\n"

        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    strong_corr.append((col1, col2, corr_val))

        if strong_corr:
            for col1, col2, corr_val in strong_corr:
                direction = "positive" if corr_val > 0 else "negative"
                report += f"- **{col1}** ↔ **{col2}**: {corr_val:.3f} ({direction})\n"
        else:
            report += "No strong correlations found.\n"

    report += """

---

## Insights

"""

    # Generate insights
    insights = generate_insights(df)

    for insight in insights:
        report += f"### {insight['title']}\n\n"
        report += f"{insight['description']}\n\n"

        if 'details' in insight:
            for detail in insight['details']:
                report += f"- {detail}\n"

        report += "\n"

    return report

def generate_insights(df):
    """Generate data insights"""
    insights = []

    # Insight: Completeness
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100

    if missing_pct < 1:
        status = "excellent"
        emoji = "✅"
    elif missing_pct < 5:
        status = "good"
        emoji = "👍"
    else:
        status = "needs attention"
        emoji = "⚠️"

    insights.append({
        "title": f"{emoji} Data Completeness: {status.title()}",
        "description": f"Overall data completeness is {100-missing_pct:.1f}% with {missing_pct:.1f}% missing values.",
        "details": [
            f"Total cells: {len(df) * len(df.columns):,}",
            f"Missing cells: {df.isnull().sum().sum():,}"
        ]
    })

    # Insight: Duplicates
    dup_count = df.duplicated().sum()

    if dup_count > 0:
        insights.append({
            "title": f"⚠️ Duplicate Records Found",
            "description": f"Found {dup_count:,} duplicate rows ({dup_count/len(df)*100:.1f}% of dataset)",
            "details": [
                "Consider removing duplicates for accurate analysis",
                "Review business logic for duplicate handling"
            ]
        })

    return insights
```

### Performance Report

```python
def generate_performance_report(metrics, baseline=None):
    """
    Generate performance comparison report
    """

    report = f"""# Performance Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

"""

    if baseline:
        report += "### Comparison with Baseline\n\n"

        report += "| Metric | Current | Baseline | Change | Status |\n"
        report += "|--------|---------|----------|--------|--------|\n"

        for metric_name, current_value in metrics.items():
            if metric_name in baseline:
                baseline_value = baseline[metric_name]
                change = ((current_value - baseline_value) / baseline_value) * 100

                if abs(change) < 5:
                    status = "🟢 Stable"
                elif change > 0:
                    status = "🟢 Improved" if is_improvement(metric_name, change) else "🔴 Degraded"
                else:
                    status = "🔴 Degraded" if is_improvement(metric_name, change) else "🟢 Improved"

                report += f"| {metric_name} | {current_value:.2f} | {baseline_value:.2f} | {change:+.1f}% | {status} |\n"

    else:
        report += "### Current Metrics\n\n"

        report += "| Metric | Value | Status |\n"
        report += "|--------|-------|--------|\n"

        for metric_name, value in metrics.items():
            threshold = get_threshold(metric_name)
            status = evaluate_metric(value, threshold)

            report += f"| {metric_name} | {value:.2f} | {status} |\n"

    report += """

---

## Detailed Analysis

"""

    for metric_name, value in metrics.items():
        report += f"### {metric_name}\n\n"

        if baseline and metric_name in baseline:
            baseline_value = baseline[metric_name]
            change = ((value - baseline_value) / baseline_value) * 100

            report += f"- **Current:** {value:.2f}\n"
            report += f"- **Baseline:** {baseline_value:.2f}\n"
            report += f"- **Change:** {change:+.1f}%\n\n"

            if abs(change) > 10:
                report += f"⚠️ Significant change detected. "
                report += "Review recent changes that may have impacted this metric.\n\n"

        else:
            report += f"- **Value:** {value:.2f}\n\n"

    return report

def is_improvement(metric_name, change):
    """Determine if change is improvement based on metric type"""
    # Lower is better for these metrics
    lower_is_better = ['response_time', 'error_rate', 'latency', 'load_time']

    for pattern in lower_is_better:
        if pattern in metric_name.lower():
            return change < 0

    return change > 0
```

## HTML Report Generation

```python
def generate_html_report(data, title="Report", template="default"):
    """
    Generate styled HTML report
    """

    # CSS styles
    css = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }

        .report-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }

        h2 {
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }

        h3 {
            color: #7f8c8d;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        th {
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }

        tr:hover {
            background: #f8f9fa;
        }

        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .metric-value {
            font-size: 2em;
            font-weight: bold;
        }

        .metric-label {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .badge-success {
            background: #2ecc71;
            color: white;
        }

        .badge-warning {
            background: #f39c12;
            color: white;
        }

        .badge-danger {
            background: #e74c3c;
            color: white;
        }

        .chart-container {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }

        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }

        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }

        .timestamp {
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
    """

    # Generate HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {css}
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="report-container">
            <h1>{title}</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>

            {generate_html_content(data)}
        </div>
    </body>
    </html>
    """

    return html

def generate_html_content(data):
    """Generate HTML content from data"""

    html = ""

    # Key metrics section
    if 'metrics' in data:
        html += "<h2>Key Metrics</h2>"
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">'

        for metric in data['metrics']:
            html += f"""
            <div class="metric-card">
                <div class="metric-label">{metric['name']}</div>
                <div class="metric-value">{metric['value']}</div>
            </div>
            """

        html += "</div>"

    # Table data
    if 'table' in data:
        html += "<h2>Data Table</h2>"
        html += generate_html_table(data['table'])

    # Charts
    if 'charts' in data:
        for chart in data['charts']:
            html += f'<h2>{chart["title"]}</h2>'
            html += '<div class="chart-container">'
            html += generate_chart_html(chart)
            html += '</div>'

    return html

def generate_html_table(table_data):
    """Generate HTML table from data"""

    html = "<table>"

    # Header
    if 'headers' in table_data:
        html += "<thead><tr>"
        for header in table_data['headers']:
            html += f"<th>{header}</th>"
        html += "</tr></thead>"

    # Rows
    html += "<tbody>"
    for row in table_data.get('rows', []):
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</tbody>"

    html += "</table>"
    return html

def generate_chart_html(chart_data):
    """Generate Chart.js chart"""

    chart_id = f"chart_{abs(hash(chart_data['title']))}"

    html = f'<canvas id="{chart_id}" width="400" height="200"></canvas>'
    html += f"""
    <script>
        var ctx = document.getElementById('{chart_id}').getContext('2d');
        var chart = new Chart(ctx, {{
            type: '{chart_data.get('type', 'bar')}',
            data: {{
                labels: {chart_data['labels']},
                datasets: [{{
                    label: '{chart_data['title']}',
                    data: {chart_data['data']},
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
    """

    return html
```

## Markdown Tables

```python
def generate_markdown_table(data, headers=None, alignment=None):
    """
    Generate markdown table from data

    alignment: list of 'left', 'center', 'right'
    """

    if not data:
        return ""

    # Auto-detect headers if not provided
    if headers is None:
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
        else:
            headers = [f"Column {i+1}" for i in range(len(data[0]))]

    # Generate header row
    table = "| " + " | ".join(str(h) for h in headers) + " |\n"

    # Generate alignment row
    if alignment is None:
        alignment = ['left'] * len(headers)

    align_chars = {
        'left': ':--',
        'center': ':-:',
        'right': '--:'
    }

    table += "| " + " | ".join(align_chars.get(a, ':--') for a in alignment) + " |\n"

    # Generate data rows
    for row in data:
        if isinstance(row, dict):
            row_data = [str(row.get(h, '')) for h in headers]
        else:
            row_data = [str(cell) for cell in row]

        table += "| " + " | ".join(row_data) + " |\n"

    return table

# Example usage
data = [
    {"name": "John", "age": 30, "city": "New York"},
    {"name": "Jane", "age": 25, "city": "San Francisco"},
    {"name": "Bob", "age": 35, "city": "Chicago"}
]

table = generate_markdown_table(
    data,
    headers=['Name', 'Age', 'City'],
    alignment=['left', 'right', 'left']
)
```

## Charts and Visualizations

```python
import matplotlib.pyplot as plt
import seaborn as sns

def generate_chart(data, chart_type='bar', title='Chart', output='chart.png'):
    """
    Generate chart from data
    """

    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-darkgrid')

    if chart_type == 'bar':
        plt.bar(data['labels'], data['values'])

    elif chart_type == 'line':
        plt.plot(data['labels'], data['values'], marker='o', linewidth=2)

    elif chart_type == 'pie':
        plt.pie(data['values'], labels=data['labels'], autopct='%1.1f%%')

    elif chart_type == 'scatter':
        plt.scatter(data['x'], data['y'], alpha=0.6)

    plt.title(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()

    return output

# For markdown reports
def embed_chart_in_markdown(chart_path, alt_text="Chart"):
    """Generate markdown image embed"""
    return f"![{alt_text}]({chart_path})\n"
```

## PDF Export

```python
from markdown import markdown
from weasyprint import HTML

def markdown_to_pdf(markdown_text, output_path='report.pdf', css=None):
    """
    Convert markdown to PDF
    """

    # Convert markdown to HTML
    html_content = markdown(markdown_text, extensions=['tables', 'fenced_code'])

    # Wrap in HTML document
    html_doc = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {css if css else get_default_pdf_css()}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert to PDF
    HTML(string=html_doc).write_pdf(output_path)

def get_default_pdf_css():
    """Default CSS for PDF export"""
    return """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }

        th {
            background-color: #3498db;
            color: white;
        }

        code {
            background: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }

        pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    """
```

## Report Templates

```python
TEMPLATES = {
    'executive': {
        'sections': ['summary', 'key_metrics', 'recommendations'],
        'style': 'concise'
    },
    'technical': {
        'sections': ['overview', 'detailed_analysis', 'code_examples', 'metrics'],
        'style': 'comprehensive'
    },
    'comparison': {
        'sections': ['baseline', 'current', 'differences', 'trends'],
        'style': 'comparative'
    }
}

def generate_from_template(data, template_name='executive'):
    """Generate report from template"""

    template = TEMPLATES.get(template_name, TEMPLATES['executive'])

    report = f"# {template_name.title()} Report\n\n"

    for section in template['sections']:
        report += generate_section(data, section, template['style'])

    return report
```

## Best Practices

1. **Structure reports clearly** with table of contents
2. **Use visual hierarchy** (headings, tables, charts)
3. **Include timestamps** for all reports
4. **Add executive summary** for long reports
5. **Use consistent formatting** throughout
6. **Include data sources** and methodology
7. **Add actionable recommendations**
8. **Use charts for trends**, tables for detailed data
9. **Export to multiple formats** (MD, HTML, PDF)
10. **Automate report generation** where possible

## Notes

- Keep reports focused and actionable
- Use appropriate visualizations for data types
- Include both summary and detailed views
- Version control report templates
- Test PDF export with different data sizes
- Consider accessibility in HTML reports
- Use responsive design for HTML reports
- Cache generated charts for performance
