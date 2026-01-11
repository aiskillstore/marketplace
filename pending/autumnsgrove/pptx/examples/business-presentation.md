# Complete Business Presentation Example

This example demonstrates creating a professional business presentation from scratch.

## Complete Implementation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

def create_professional_presentation():
    """Create a complete professional business presentation."""

    # Initialize
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # Brand colors
    PRIMARY = RGBColor(0, 51, 102)
    SECONDARY = RGBColor(0, 153, 204)
    ACCENT = RGBColor(255, 102, 0)

    # 1. Title Slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = "Annual Report 2025"
    title.text_frame.paragraphs[0].font.size = Pt(54)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].font.color.rgb = PRIMARY

    subtitle.text = "Innovation • Growth • Excellence\nPresented by: Leadership Team"

    # 2. Agenda Slide
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    title.text = "Agenda"

    body = slide.placeholders[1]
    tf = body.text_frame
    tf.clear()

    agenda_items = [
        "Executive Summary",
        "Financial Highlights",
        "Market Position",
        "Innovation & R&D",
        "2026 Strategic Goals"
    ]

    for item in agenda_items:
        p = tf.add_paragraph()
        p.text = item
        p.level = 0
        p.font.size = Pt(24)
        p.space_before = Pt(14)

    # 3. Executive Summary
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    title.text = "Executive Summary"

    body = slide.placeholders[1]
    tf = body.text_frame
    tf.clear()

    summary = [
        ("Record Revenue", "Achieved $500M in annual revenue, 35% YoY growth"),
        ("Market Expansion", "Entered 12 new markets across Asia and Europe"),
        ("Customer Growth", "2M+ active customers, 92% satisfaction rate"),
        ("Product Innovation", "Launched 5 major products, 15+ features")
    ]

    for heading, detail in summary:
        p = tf.add_paragraph()
        p.text = heading
        p.level = 0
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = PRIMARY

        p = tf.add_paragraph()
        p.text = detail
        p.level = 1
        p.font.size = Pt(16)

    # 4. Financial Chart
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = "Revenue Growth (2020-2025)"

    chart_data = CategoryChartData()
    chart_data.categories = ['2020', '2021', '2022', '2023', '2024', '2025']
    chart_data.add_series('Revenue ($M)', (250, 285, 320, 370, 430, 500))

    x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
    ).chart

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.plots[0].has_data_labels = True

    # 5. Market Position - Pie Chart
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = "Market Share by Region"

    chart_data = CategoryChartData()
    chart_data.categories = ['North America', 'Europe', 'Asia Pacific', 'Other']
    chart_data.add_series('Market Share', (42, 28, 23, 7))

    x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.PIE, x, y, cx, cy, chart_data
    ).chart

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.RIGHT
    chart.plots[0].has_data_labels = True

    # 6. Thank You Slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    text_box = slide.shapes.add_textbox(
        Inches(2), Inches(2.5), Inches(6), Inches(2)
    )
    tf = text_box.text_frame
    tf.text = "Thank You"

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(60)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    p = tf.add_paragraph()
    p.text = "Questions?"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(32)
    p.font.color.rgb = SECONDARY

    # Save
    prs.save('annual_report_2025.pptx')
    print("✅ Presentation created: annual_report_2025.pptx")

if __name__ == "__main__":
    create_professional_presentation()
```

## Output

This script creates a 6-slide presentation:
1. Title slide with formatted title and subtitle
2. Agenda slide with bullet points
3. Executive summary with hierarchical text
4. Revenue growth bar chart
5. Market share pie chart
6. Thank you slide with centered text

## Customization

Modify these elements to match your brand:
- Brand colors (PRIMARY, SECONDARY, ACCENT)
- Company name and data
- Chart values and categories
- Slide layouts (change indices if using custom template)
