# PDF Creation Reference

## Basic PDF Creation

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_simple_pdf(output_path, content):
    """Create a simple PDF with text content."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Set font
    c.setFont("Helvetica", 12)

    # Add text
    y_position = height - 50
    for line in content:
        c.drawString(50, y_position, line)
        y_position -= 20

    c.save()

# Usage
content = [
    "This is the first line",
    "This is the second line",
    "This is the third line"
]
create_simple_pdf("output.pdf", content)
```

## Create Styled Report

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

def create_styled_report(output_path, title, sections):
    """
    Create a professionally styled PDF report.

    Args:
        output_path: Output file path
        title: Document title
        sections: List of dicts with 'heading' and 'content' keys
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        alignment=TA_CENTER,
        spaceAfter=30
    )

    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.5*inch))

    # Add sections
    for section in sections:
        # Section heading
        story.append(Paragraph(section['heading'], styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        # Section content
        for paragraph in section['content']:
            p = Paragraph(paragraph, styles['BodyText'])
            story.append(p)
            story.append(Spacer(1, 0.1*inch))

        story.append(Spacer(1, 0.3*inch))

    doc.build(story)

# Usage
sections = [
    {
        'heading': 'Introduction',
        'content': [
            'This is the introduction paragraph.',
            'It contains important information about the topic.'
        ]
    },
    {
        'heading': 'Methods',
        'content': [
            'We used various methods to conduct this research.',
            'The methodology was carefully designed.'
        ]
    }
]
create_styled_report("report.pdf", "Research Report", sections)
```

## Create PDF with Tables

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf_with_table(output_path, title, table_data):
    """Create PDF with formatted table."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Add title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Create table
    table = Table(table_data)

    # Add style to table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)

# Usage
data = [
    ['Product', 'Quantity', 'Price'],
    ['Widget A', '10', '$50'],
    ['Widget B', '5', '$75'],
    ['Widget C', '20', '$30']
]
create_pdf_with_table("invoice.pdf", "Sales Invoice", data)
```

## Create PDF with Images

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def create_pdf_with_images(output_path, title, image_paths, captions=None):
    """Create PDF with images and captions."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Add title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 0.5*inch))

    if captions is None:
        captions = [f"Image {i+1}" for i in range(len(image_paths))]

    for img_path, caption in zip(image_paths, captions):
        # Add image
        img = Image(img_path, width=4*inch, height=3*inch)
        elements.append(img)

        # Add caption
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(caption, styles['Italic']))
        elements.append(Spacer(1, 0.3*inch))

    doc.build(elements)

# Usage
images = ["chart1.png", "chart2.png", "chart3.png"]
captions = ["Sales Chart", "Revenue Chart", "Growth Chart"]
create_pdf_with_images("visual_report.pdf", "Analytics Report", images, captions)
```

## Create Multi-Column Layout

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def create_multicolumn_pdf(output_path, content):
    """Create PDF with multiple columns."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Define frames for columns
    frame_width = (letter[0] - 2*inch) / 2
    frame_height = letter[1] - 2*inch

    frame1 = Frame(0.5*inch, 0.5*inch, frame_width, frame_height)
    frame2 = Frame(frame_width + inch, 0.5*inch, frame_width, frame_height)

    # Create page template
    template = PageTemplate(frames=[frame1, frame2])
    doc.addPageTemplates([template])

    # Build story
    story = [Paragraph(p, styles['Normal']) for p in content]
    doc.build(story)

# Usage
content = ["Paragraph " + str(i) for i in range(1, 21)]
create_multicolumn_pdf("columns.pdf", content)
```

## Create PDF with Custom Fonts

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_pdf_custom_font(output_path, font_path, font_name, text):
    """Create PDF with custom font."""
    # Register custom font
    pdfmetrics.registerFont(TTFont(font_name, font_path))

    c = canvas.Canvas(output_path, pagesize=letter)

    # Use custom font
    c.setFont(font_name, 16)
    c.drawString(50, 750, text)

    c.save()

# Usage
create_pdf_custom_font(
    "custom_font.pdf",
    "/path/to/font.ttf",
    "CustomFont",
    "Text in custom font"
)
```

## Create Invoice Template

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def create_invoice(output_path, invoice_data):
    """
    Create professional invoice.

    Args:
        invoice_data: Dict with 'company', 'client', 'items', 'total'
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Company header
    elements.append(Paragraph(invoice_data['company'], styles['Title']))
    elements.append(Spacer(1, 0.2*inch))

    # Invoice details
    elements.append(Paragraph(f"Invoice To: {invoice_data['client']}", styles['Normal']))
    elements.append(Paragraph(f"Date: {invoice_data['date']}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Items table
    table_data = [['Description', 'Quantity', 'Price', 'Total']]
    table_data.extend(invoice_data['items'])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))

    # Total
    elements.append(Paragraph(f"Total: ${invoice_data['total']}", styles['Heading2']))

    doc.build(elements)

# Usage
invoice = {
    'company': 'Acme Corporation',
    'client': 'John Smith',
    'date': '2025-10-25',
    'items': [
        ['Service A', '2', '$100', '$200'],
        ['Service B', '1', '$150', '$150']
    ],
    'total': 350
}
create_invoice("invoice.pdf", invoice)
```
