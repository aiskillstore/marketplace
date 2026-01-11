# Editing Existing Presentations

Examples for modifying and updating existing PowerPoint files.

## Open and Inspect Presentation

```python
from pptx import Presentation

# Open existing presentation
prs = Presentation('existing_presentation.pptx')

# Access slides
print(f"Total slides: {len(prs.slides)}")

# Iterate through slides
for idx, slide in enumerate(prs.slides):
    print(f"Slide {idx}: {slide.slide_layout.name}")

    # Access shapes
    for shape in slide.shapes:
        if hasattr(shape, "text"):
            print(f"  - {shape.text[:50]}...")
```

## Find and Replace Text

```python
from pptx import Presentation

prs = Presentation('existing.pptx')

# Find and update text across all slides
old_text = "Old Company Name"
new_text = "New Company Name"

for slide in prs.slides:
    for shape in slide.shapes:
        if hasattr(shape, "text_frame"):
            if old_text in shape.text:
                # Replace in all paragraphs and runs
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if old_text in run.text:
                            run.text = run.text.replace(old_text, new_text)

prs.save('updated.pptx')
print(f"✅ Replaced '{old_text}' with '{new_text}'")
```

## Update Specific Slide

```python
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

prs = Presentation('presentation.pptx')

# Modify specific slide (e.g., slide 3)
slide = prs.slides[2]  # 0-indexed

# Update title
title = slide.shapes.title
title.text = "Updated Title"
title.text_frame.paragraphs[0].font.size = Pt(44)
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

# Find and update specific shape by name
for shape in slide.shapes:
    if shape.name == "TextBox 1":
        shape.text = "Updated content"

prs.save('updated.pptx')
```

## Add Slides to Existing Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt

# Open existing presentation
prs = Presentation('existing.pptx')

# Add new slide at the end
new_slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title and Content
new_slide.shapes.title.text = "New Slide Added"

# Add content
body = new_slide.placeholders[1]
tf = body.text_frame
tf.text = "This slide was added programmatically"

prs.save('updated_with_new_slide.pptx')
```

## Delete Slides

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation('presentation.pptx')

# Delete specific slide by index
def delete_slide(prs, index):
    """Delete slide at given index."""
    rId = prs.slides._sldIdLst[index].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[index]

# Delete slide 3 (index 2)
delete_slide(prs, 2)

prs.save('presentation_with_deleted_slide.pptx')
```

## Copy Slide Within Presentation

```python
from pptx import Presentation
import copy

def duplicate_slide(prs, slide_index):
    """Duplicate slide at given index."""
    source_slide = prs.slides[slide_index]

    # Get slide layout
    slide_layout = prs.slide_layouts[source_slide.slide_layout.slide_layout_index]

    # Add new slide
    new_slide = prs.slides.add_slide(slide_layout)

    # Copy shapes
    for shape in source_slide.shapes:
        el = shape.element
        newel = copy.deepcopy(el)
        new_slide.shapes._spTree.insert_element_before(newel, 'p:extLst')

    return new_slide

# Usage
prs = Presentation('presentation.pptx')
duplicate_slide(prs, 0)  # Duplicate first slide
prs.save('presentation_with_duplicate.pptx')
```

## Copy Slide from Another Presentation

```python
from pptx import Presentation
import copy

def copy_slide_between_presentations(source_prs, target_prs, slide_index):
    """Copy slide from source to target presentation."""
    source_slide = source_prs.slides[slide_index]

    # Get or create matching layout in target
    try:
        slide_layout = target_prs.slide_layouts[source_slide.slide_layout.slide_layout_index]
    except IndexError:
        # Use blank layout if exact match not found
        slide_layout = target_prs.slide_layouts[6]

    # Add new slide
    new_slide = target_prs.slides.add_slide(slide_layout)

    # Copy shapes
    for shape in source_slide.shapes:
        el = shape.element
        newel = copy.deepcopy(el)
        new_slide.shapes._spTree.insert_element_before(newel, 'p:extLst')

    return new_slide

# Usage
source_prs = Presentation('source.pptx')
target_prs = Presentation('target.pptx')

copy_slide_between_presentations(source_prs, target_prs, 0)
target_prs.save('target_with_copied_slide.pptx')
```

## Update Images

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation('presentation.pptx')

# Find and replace images
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.shape_type == 13:  # Picture
            # Get position and size
            left = shape.left
            top = shape.top
            width = shape.width
            height = shape.height

            # Remove old image
            sp = shape.element
            sp.getparent().remove(sp)

            # Add new image in same position
            slide.shapes.add_picture('new_image.png', left, top, width, height)

prs.save('presentation_with_updated_images.pptx')
```

## Update Chart Data

```python
from pptx import Presentation
from pptx.chart.data import CategoryChartData

prs = Presentation('presentation.pptx')

# Find chart and update data
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_chart:
            chart = shape.chart

            # Create new chart data
            chart_data = CategoryChartData()
            chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
            chart_data.add_series('2025', (12, 15, 18, 22))

            # Replace chart data
            chart.replace_data(chart_data)

prs.save('presentation_with_updated_charts.pptx')
```

## Batch Update Metadata

```python
from pptx import Presentation

def update_presentation_metadata(pptx_file, title=None, author=None, subject=None):
    """Update presentation metadata."""
    prs = Presentation(pptx_file)

    core_props = prs.core_properties

    if title:
        core_props.title = title
    if author:
        core_props.author = author
    if subject:
        core_props.subject = subject

    prs.save(pptx_file)
    print(f"✅ Updated metadata for {pptx_file}")

# Usage
update_presentation_metadata(
    'presentation.pptx',
    title="Q4 2025 Report",
    author="Jane Doe",
    subject="Quarterly Review"
)
```

## Extract Text from Presentation

```python
from pptx import Presentation

def extract_text_from_presentation(pptx_file):
    """Extract all text from presentation."""
    prs = Presentation(pptx_file)

    all_text = []

    for slide_num, slide in enumerate(prs.slides, start=1):
        slide_text = f"\n--- Slide {slide_num} ---\n"

        for shape in slide.shapes:
            if hasattr(shape, "text"):
                slide_text += shape.text + "\n"

        all_text.append(slide_text)

    return "".join(all_text)

# Usage
text = extract_text_from_presentation('presentation.pptx')
print(text)

# Save to file
with open('extracted_text.txt', 'w') as f:
    f.write(text)
```

## Reorder Slides

```python
from pptx import Presentation

def move_slide(prs, old_index, new_index):
    """Move slide from old_index to new_index."""
    slides = list(prs.slides._sldIdLst)
    slides.insert(new_index, slides.pop(old_index))
    prs.slides._sldIdLst[:] = slides

# Usage
prs = Presentation('presentation.pptx')

# Move slide from position 0 to position 3
move_slide(prs, 0, 3)

prs.save('reordered_presentation.pptx')
```

## Update Speaker Notes

```python
from pptx import Presentation

prs = Presentation('presentation.pptx')

# Add/update speaker notes for each slide
notes_content = [
    "Introduction - mention key achievements",
    "Financial data - emphasize growth metrics",
    "Market analysis - reference competitor data",
    "Conclusion - summarize action items"
]

for slide, notes in zip(prs.slides, notes_content):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.clear()
    text_frame.text = notes

prs.save('presentation_with_notes.pptx')
```
