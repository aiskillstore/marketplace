# Report Automation Example

Complete example of automated report generation with data visualization.

## Monthly Report Generator

```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Image)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import pandas as pd
from datetime import datetime

def create_monthly_report(output_path, report_data):
    """
    Generate comprehensive monthly report.

    Args:
        report_data: Dict with sections, metrics, charts
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor('#1F4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    # Title page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(report_data['title'], title_style))
    story.append(Paragraph(report_data['subtitle'], subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Report Period: {report_data['period']}", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))

    for paragraph in report_data['executive_summary']:
        story.append(Paragraph(paragraph, styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))

    story.append(Spacer(1, 0.3*inch))

    # Key Metrics Table
    story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    metrics_data = [['Metric', 'Current', 'Previous', 'Change']]
    for metric in report_data['metrics']:
        change = metric['current'] - metric['previous']
        change_pct = (change / metric['previous'] * 100) if metric['previous'] != 0 else 0
        change_str = f"{change:+.1f} ({change_pct:+.1f}%)"

        metrics_data.append([
            metric['name'],
            f"{metric['current']:.1f}",
            f"{metric['previous']:.1f}",
            change_str
        ])

    metrics_table = Table(metrics_data, colWidths=[3*inch, 1.25*inch, 1.25*inch, 1.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E7E6E6')])
    ]))

    story.append(metrics_table)
    story.append(Spacer(1, 0.4*inch))

    # Detailed Sections
    for section in report_data['sections']:
        story.append(Paragraph(section['title'], styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        for paragraph in section['content']:
            story.append(Paragraph(paragraph, styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))

        # Add chart if provided
        if 'chart' in section:
            story.append(Spacer(1, 0.2*inch))
            img = Image(section['chart'], width=5*inch, height=3*inch)
            story.append(img)
            story.append(Paragraph(f"<i>{section.get('chart_caption', '')}</i>",
                                 styles['Normal']))

        story.append(Spacer(1, 0.4*inch))

    # Build PDF
    doc.build(story)

# Usage
report_data = {
    'title': 'Q4 2025 Business Performance Report',
    'subtitle': 'Quarterly Analysis and Insights',
    'period': 'October - December 2025',
    'executive_summary': [
        'This quarter showed strong growth across all key metrics, with revenue '
        'increasing 15% year-over-year and customer acquisition exceeding targets by 20%.',
        'Operational efficiency improvements contributed to a 5% reduction in costs, '
        'while maintaining high customer satisfaction scores.',
        'Looking ahead, we anticipate continued growth driven by new product launches '
        'and expanded market presence.'
    ],
    'metrics': [
        {'name': 'Revenue ($M)', 'current': 45.2, 'previous': 39.3},
        {'name': 'New Customers', 'current': 1250, 'previous': 980},
        {'name': 'Customer Retention (%)', 'current': 94.5, 'previous': 92.1},
        {'name': 'Avg. Deal Size ($K)', 'current': 36.2, 'previous': 34.8}
    ],
    'sections': [
        {
            'title': 'Revenue Analysis',
            'content': [
                'Q4 revenue reached $45.2M, representing a 15% increase over Q3 and '
                'exceeding our quarterly target by 8%.',
                'Growth was driven primarily by enterprise sales, which increased 25% '
                'quarter-over-quarter. SMB segment showed steady 10% growth.',
                'Recurring revenue now accounts for 75% of total revenue, up from '
                '68% in the previous quarter, indicating strong business model health.'
            ]
        },
        {
            'title': 'Customer Acquisition',
            'content': [
                'We acquired 1,250 new customers this quarter, surpassing our target '
                'of 1,000 by 25%.',
                'Cost per acquisition decreased 12% due to improved marketing efficiency '
                'and increased word-of-mouth referrals.',
                'Customer onboarding time reduced from 14 days to 9 days through '
                'process improvements and automation.'
            ]
        },
        {
            'title': 'Operational Efficiency',
            'content': [
                'Operational costs decreased 5% while maintaining service quality, '
                'driven by automation initiatives and process optimization.',
                'Team productivity increased 18% measured by output per employee, '
                'attributed to new tools and training programs.',
                'Customer support response time improved by 30%, with average '
                'first-response time now under 2 hours.'
            ]
        }
    ]
}

create_monthly_report("q4_2025_report.pdf", report_data)
print("Report generated: q4_2025_report.pdf")
```

## Data-Driven Report with Pandas Integration

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
import pandas as pd

def create_data_report(output_path, df, title, analysis):
    """
    Create report from pandas DataFrame.

    Args:
        df: pandas DataFrame with data
        title: Report title
        analysis: Dict with analysis sections
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 0.3*inch))

    # Summary statistics
    story.append(Paragraph("Summary Statistics", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    # Convert DataFrame describe() to table
    summary = df.describe()
    table_data = [[''] + list(summary.columns)]
    for idx in summary.index:
        row = [idx] + [f"{val:.2f}" for val in summary.loc[idx]]
        table_data.append(row)

    summary_table = Table(table_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.4*inch))

    # Detailed data table (first 20 rows)
    story.append(Paragraph("Detailed Data (First 20 Rows)", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    data_subset = df.head(20)
    table_data = [list(data_subset.columns)]
    for _, row in data_subset.iterrows():
        table_data.append([str(val) for val in row])

    data_table = Table(table_data)
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    story.append(data_table)
    story.append(Spacer(1, 0.4*inch))

    # Analysis sections
    for section in analysis:
        story.append(Paragraph(section['title'], styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        for paragraph in section['content']:
            story.append(Paragraph(paragraph, styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))

        story.append(Spacer(1, 0.3*inch))

    doc.build(story)

# Usage
# Create sample data
data = {
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Revenue': [120000, 135000, 142000, 156000, 168000, 175000],
    'Expenses': [85000, 88000, 92000, 95000, 98000, 101000],
    'Customers': [450, 485, 510, 548, 580, 612]
}
df = pd.DataFrame(data)

analysis = [
    {
        'title': 'Revenue Trend',
        'content': [
            'Revenue showed consistent growth over the 6-month period, increasing '
            'from $120K in January to $175K in June, representing a 46% growth.',
            'Average month-over-month growth rate was 7.8%, indicating strong business momentum.'
        ]
    },
    {
        'title': 'Profitability',
        'content': [
            'Profit margins improved from 29% in January to 42% in June as revenue '
            'growth outpaced expense growth.',
            'Expense control remained effective with only 19% increase over the period '
            'while revenue grew 46%.'
        ]
    }
]

create_data_report("data_analysis_report.pdf", df, "6-Month Business Analysis", analysis)
print("Data report generated: data_analysis_report.pdf")
```

## Automated Weekly Report

```python
def create_weekly_report(week_number, data):
    """Generate automated weekly report."""
    output_path = f"weekly_report_week{week_number}.pdf"

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    story.append(Paragraph(f"Weekly Report - Week {week_number}", styles['Title']))
    story.append(Paragraph(data['date_range'], styles['Normal']))
    story.append(Spacer(1, 0.5*inch))

    # Highlights
    story.append(Paragraph("Week Highlights", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    highlights_data = [['Category', 'Metric', 'Value', 'vs Last Week']]
    for item in data['highlights']:
        highlights_data.append([
            item['category'],
            item['metric'],
            str(item['value']),
            f"{item['change']:+.1f}%"
        ])

    table = Table(highlights_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))

    story.append(table)
    story.append(Spacer(1, 0.4*inch))

    # Action Items
    story.append(Paragraph("Action Items", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    for item in data['action_items']:
        story.append(Paragraph(f"• {item}", styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))

    doc.build(story)
    return output_path

# Usage
week_data = {
    'date_range': 'October 21-27, 2025',
    'highlights': [
        {'category': 'Sales', 'metric': 'New Deals', 'value': 12, 'change': 20},
        {'category': 'Marketing', 'metric': 'Leads', 'value': 145, 'change': -5},
        {'category': 'Support', 'metric': 'Tickets Closed', 'value': 89, 'change': 15}
    ],
    'action_items': [
        'Follow up with 3 high-value prospects from this week',
        'Review and optimize underperforming marketing campaigns',
        'Schedule training session for new support tool'
    ]
}

report_path = create_weekly_report(43, week_data)
print(f"Weekly report generated: {report_path}")
```
