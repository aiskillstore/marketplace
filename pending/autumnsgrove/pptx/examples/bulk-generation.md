# Bulk Slide Generation Examples

Examples for automatically generating multiple slides from structured data.

## Generate from pandas DataFrame

```python
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt

def create_slides_from_dataframe(csv_file, output_file="output.pptx"):
    """Generate presentation from CSV data."""
    # Load data
    df = pd.read_csv(csv_file)

    # Create presentation
    prs = Presentation()

    # Add title slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "Employee Directory"
    title_slide.placeholders[1].text = f"{len(df)} Employees"

    # Create one slide per employee
    for _, row in df.iterrows():
        slide = prs.slides.add_slide(prs.slide_layouts[1])

        # Title: Employee name
        title = slide.shapes.title
        title.text = row['Name']

        # Content: Employee details
        body_shape = slide.placeholders[1]
        tf = body_shape.text_frame
        tf.clear()

        details = [
            f"Position: {row['Position']}",
            f"Department: {row['Department']}",
            f"Email: {row['Email']}",
            f"Phone: {row['Phone']}"
        ]

        for detail in details:
            p = tf.add_paragraph()
            p.text = detail
            p.level = 0
            p.font.size = Pt(18)

    prs.save(output_file)
    print(f"✅ Created {output_file} with {len(df)} employee slides")

# Usage
create_slides_from_dataframe('employees.csv', 'employee_directory.pptx')
```

## Generate from JSON Data

```python
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

def create_slides_from_json(json_file, output_file="output.pptx"):
    """Generate presentation from JSON data."""
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    prs = Presentation()

    # Generate slides for each region
    for region_data in data['regions']:
        slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only

        title = slide.shapes.title
        title.text = f"{region_data['name']} - Sales Performance"

        # Add chart
        chart_data = CategoryChartData()
        chart_data.categories = [m['month'] for m in region_data['monthly_sales']]
        chart_data.add_series('Sales', [m['amount'] for m in region_data['monthly_sales']])

        x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4)
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
        ).chart

        # Add summary text
        text_box = slide.shapes.add_textbox(Inches(1), Inches(6.5), Inches(8), Inches(0.5))
        tf = text_box.text_frame
        tf.text = f"Total Sales: ${region_data['total']:,.2f} | Growth: {region_data['growth']}%"
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].font.bold = True

    prs.save(output_file)
    print(f"✅ Created {output_file} with {len(data['regions'])} region slides")

# Usage
create_slides_from_json('sales_data.json', 'regional_sales.pptx')
```

## Generate from Database Query

```python
import sqlite3
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def create_slides_from_database(db_file, query, output_file="output.pptx"):
    """Generate presentation from database query."""
    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute query
    cursor.execute(query)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    # Create presentation
    prs = Presentation()

    # Title slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "Database Report"
    title_slide.placeholders[1].text = f"{len(rows)} records"

    # Create slide for each record
    for row in rows:
        slide = prs.slides.add_slide(prs.slide_layouts[1])

        # Title from first column
        title = slide.shapes.title
        title.text = str(row[0])

        # Content from remaining columns
        body = slide.placeholders[1]
        tf = body.text_frame
        tf.clear()

        for col, value in zip(columns[1:], row[1:]):
            p = tf.add_paragraph()
            p.text = f"{col}: {value}"
            p.level = 0
            p.font.size = Pt(16)

    conn.close()
    prs.save(output_file)
    print(f"✅ Created {output_file} with {len(rows)} slides")

# Usage
create_slides_from_database(
    'company.db',
    'SELECT name, position, department, hire_date FROM employees',
    'employee_report.pptx'
)
```

## Generate Report with Summary Statistics

```python
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.dml.color import RGBColor

def create_data_report(csv_file, output_file="data_report.pptx"):
    """Create presentation with data tables and summary statistics."""
    # Load data
    df = pd.read_csv(csv_file)

    prs = Presentation()

    # 1. Title slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "Data Report"
    title_slide.placeholders[1].text = f"Dataset: {csv_file}\n{len(df)} records"

    # 2. Summary slide
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    title.text = "Dataset Overview"

    body = slide.placeholders[1]
    tf = body.text_frame
    tf.clear()

    summary_items = [
        f"Total Records: {len(df)}",
        f"Columns: {len(df.columns)}",
        f"Numeric Columns: {len(df.select_dtypes(include=['number']).columns)}",
        f"Missing Values: {df.isnull().sum().sum()}"
    ]

    for item in summary_items:
        p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(20)

    # 3. Data table (first 10 rows)
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = "Sample Data (First 10 Rows)"

    # Determine table size
    rows = min(11, len(df) + 1)  # +1 for header, max 10 data rows
    cols = min(len(df.columns), 6)  # Max 6 columns

    # Add table
    left = Inches(0.5)
    top = Inches(2)
    width = Inches(9)
    height = Inches(4)

    table = slide.shapes.add_table(rows, cols, left, top, width, height).table

    # Set column widths
    col_width = width / cols
    for col in range(cols):
        table.columns[col].width = col_width

    # Headers
    for col_idx in range(cols):
        cell = table.cell(0, col_idx)
        cell.text = str(df.columns[col_idx])
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(11)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
        cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    # Data
    for row_idx in range(min(10, len(df))):
        for col_idx in range(cols):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = str(df.iloc[row_idx, col_idx])
            cell.text_frame.paragraphs[0].font.size = Pt(10)

    # 4. Statistics slide (if numeric columns exist)
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = slide.shapes.title
        title.text = "Summary Statistics"

        body = slide.placeholders[1]
        tf = body.text_frame
        tf.clear()

        for col in numeric_cols[:5]:  # First 5 numeric columns
            p = tf.add_paragraph()
            p.text = f"{col}:"
            p.level = 0
            p.font.bold = True
            p.font.size = Pt(16)

            stats = [
                f"Mean: {df[col].mean():.2f}",
                f"Median: {df[col].median():.2f}",
                f"Std Dev: {df[col].std():.2f}"
            ]

            for stat in stats:
                p = tf.add_paragraph()
                p.text = stat
                p.level = 1
                p.font.size = Pt(14)

    prs.save(output_file)
    print(f"✅ Report created: {output_file}")

# Usage
create_data_report('sales_data.csv', 'sales_report.pptx')
```

## Batch Generate Individual Presentations

```python
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt

def generate_individual_presentations(csv_file, output_dir="presentations"):
    """Generate one presentation per record."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(csv_file)

    for idx, row in df.iterrows():
        prs = Presentation()

        # Title slide
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = row['Name']
        slide.placeholders[1].text = row['Department']

        # Content slide
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Details"

        body = slide.placeholders[1]
        tf = body.text_frame
        tf.clear()

        for col in df.columns:
            if col not in ['Name', 'Department']:
                p = tf.add_paragraph()
                p.text = f"{col}: {row[col]}"
                p.level = 0
                p.font.size = Pt(16)

        # Save individual file
        filename = f"{row['Name'].replace(' ', '_')}.pptx"
        filepath = os.path.join(output_dir, filename)
        prs.save(filepath)

    print(f"✅ Generated {len(df)} individual presentations in {output_dir}/")

# Usage
generate_individual_presentations('employees.csv')
```

## Generate from API Response

```python
import requests
from pptx import Presentation
from pptx.util import Inches, Pt

def create_slides_from_api(api_url, output_file="api_report.pptx"):
    """Generate presentation from API data."""
    # Fetch data from API
    response = requests.get(api_url)
    data = response.json()

    prs = Presentation()

    # Title slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "API Data Report"
    title_slide.placeholders[1].text = f"{len(data)} items"

    # Create slide for each item
    for item in data:
        slide = prs.slides.add_slide(prs.slide_layouts[1])

        # Title
        title = slide.shapes.title
        title.text = item.get('title', 'Untitled')

        # Content
        body = slide.placeholders[1]
        tf = body.text_frame
        tf.clear()

        # Add all key-value pairs
        for key, value in item.items():
            if key != 'title':
                p = tf.add_paragraph()
                p.text = f"{key}: {value}"
                p.level = 0
                p.font.size = Pt(14)

    prs.save(output_file)
    print(f"✅ Created {output_file} from API data")

# Usage
create_slides_from_api('https://api.example.com/data', 'api_report.pptx')
```

## Template-Based Bulk Generation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
import pandas as pd

def generate_from_template(template_file, data_file, output_file="output.pptx"):
    """Generate presentation using template and data."""
    # Load template
    template_prs = Presentation(template_file)

    # Load data
    df = pd.read_csv(data_file)

    # Create new presentation
    prs = Presentation(template_file)

    # Keep only title slide
    while len(prs.slides) > 1:
        rId = prs.slides._sldIdLst[1].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[1]

    # Generate slides from data
    for _, row in df.iterrows():
        # Use template layout
        slide = prs.slides.add_slide(prs.slide_layouts[1])

        # Populate with data
        slide.shapes.title.text = row['Title']

        body = slide.placeholders[1]
        tf = body.text_frame
        tf.clear()

        for col in df.columns:
            if col != 'Title':
                p = tf.add_paragraph()
                p.text = f"{col}: {row[col]}"
                p.font.size = Pt(16)

    prs.save(output_file)
    print(f"✅ Generated {output_file} using template")

# Usage
generate_from_template('template.pptx', 'data.csv', 'output.pptx')
```
