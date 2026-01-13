"""
PowerPoint Helper Utilities

Comprehensive helper functions for creating, editing, and automating PowerPoint
presentations using python-pptx.

Author: Claude (Anthropic)
License: MIT
Requirements: python-pptx, Pillow (optional for image processing)
"""

from typing import List, Tuple, Optional, Union, Dict, Any
import os
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Cm
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
    from pptx.chart.data import CategoryChartData
    from pptx.dml.color import RGBColor
except ImportError:
    raise ImportError(
        "python-pptx is required. Install with: pip install python-pptx"
    )

# Optional PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ==================== Color Schemes ====================

BRAND_COLORS = {
    'corporate': {
        'primary': RGBColor(0, 51, 102),      # Navy Blue
        'secondary': RGBColor(240, 243, 245), # Light Gray
        'accent': RGBColor(0, 153, 204),      # Sky Blue
        'text': RGBColor(51, 51, 51),         # Dark Gray
        'background': RGBColor(255, 255, 255) # White
    },
    'tech': {
        'primary': RGBColor(34, 139, 34),     # Forest Green
        'secondary': RGBColor(245, 245, 245), # Off-white
        'accent': RGBColor(255, 165, 0),      # Orange
        'text': RGBColor(51, 51, 51),
        'background': RGBColor(255, 255, 255)
    },
    'creative': {
        'primary': RGBColor(106, 27, 154),    # Deep Purple
        'secondary': RGBColor(238, 238, 238), # Light Gray
        'accent': RGBColor(255, 215, 0),      # Gold
        'text': RGBColor(51, 51, 51),
        'background': RGBColor(255, 255, 255)
    },
    'modern': {
        'primary': RGBColor(41, 128, 185),    # Modern Blue
        'secondary': RGBColor(236, 240, 241), # Light Blue-Gray
        'accent': RGBColor(231, 76, 60),      # Red
        'text': RGBColor(44, 62, 80),
        'background': RGBColor(255, 255, 255)
    }
}


# ==================== Presentation Creation ====================

def create_presentation(
    title: Optional[str] = None,
    author: Optional[str] = None,
    subject: Optional[str] = None,
    aspect_ratio: str = "16:9",
    template_path: Optional[str] = None
) -> Presentation:
    """
    Create a new PowerPoint presentation with metadata.

    Args:
        title: Presentation title (metadata)
        author: Author name (metadata)
        subject: Subject/topic (metadata)
        aspect_ratio: "16:9" (widescreen) or "4:3" (standard)
        template_path: Path to .pptx template file (optional)

    Returns:
        Presentation object

    Example:
        >>> prs = create_presentation(
        ...     title="Q4 Business Review",
        ...     author="Jane Doe",
        ...     aspect_ratio="16:9"
        ... )
    """
    # Load template or create blank
    if template_path and os.path.exists(template_path):
        prs = Presentation(template_path)
    else:
        prs = Presentation()

    # Set aspect ratio
    if aspect_ratio == "16:9":
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
    elif aspect_ratio == "4:3":
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
    else:
        raise ValueError("aspect_ratio must be '16:9' or '4:3'")

    # Set metadata
    core_props = prs.core_properties
    if title:
        core_props.title = title
    if author:
        core_props.author = author
    if subject:
        core_props.subject = subject

    return prs


# ==================== Slide Creation ====================

def add_title_slide(
    prs: Presentation,
    title: str,
    subtitle: str = "",
    title_size: int = 54,
    subtitle_size: int = 24,
    title_color: Optional[RGBColor] = None,
    layout_index: int = 0
) -> Any:
    """
    Add a title slide to the presentation.

    Args:
        prs: Presentation object
        title: Main title text
        subtitle: Subtitle text
        title_size: Title font size in points
        subtitle_size: Subtitle font size in points
        title_color: RGB color for title (optional)
        layout_index: Slide layout index (default: 0 = Title Slide)

    Returns:
        Slide object

    Example:
        >>> add_title_slide(
        ...     prs,
        ...     "Annual Report 2025",
        ...     "Prepared by: Finance Team"
        ... )
    """
    slide_layout = prs.slide_layouts[layout_index]
    slide = prs.slides.add_slide(slide_layout)

    # Title
    title_shape = slide.shapes.title
    title_shape.text = title
    title_shape.text_frame.paragraphs[0].font.size = Pt(title_size)
    title_shape.text_frame.paragraphs[0].font.bold = True

    if title_color:
        title_shape.text_frame.paragraphs[0].font.color.rgb = title_color

    # Subtitle
    if subtitle and len(slide.placeholders) > 1:
        subtitle_shape = slide.placeholders[1]
        subtitle_shape.text = subtitle
        subtitle_shape.text_frame.paragraphs[0].font.size = Pt(subtitle_size)

    return slide


def add_bullet_slide(
    prs: Presentation,
    title: str,
    bullets: List[Union[str, Tuple[str, int]]],
    layout_index: int = 1,
    bullet_size: int = 20
) -> Any:
    """
    Add a slide with bullet points.

    Args:
        prs: Presentation object
        title: Slide title
        bullets: List of bullet text or tuples of (text, level)
                 Level 0 = main bullet, Level 1 = sub-bullet
        layout_index: Slide layout index (default: 1 = Title and Content)
        bullet_size: Font size for bullets in points

    Returns:
        Slide object

    Example:
        >>> add_bullet_slide(
        ...     prs,
        ...     "Key Points",
        ...     [
        ...         "Main point 1",
        ...         ("Sub-point 1a", 1),
        ...         ("Sub-point 1b", 1),
        ...         "Main point 2"
        ...     ]
        ... )
    """
    slide_layout = prs.slide_layouts[layout_index]
    slide = prs.slides.add_slide(slide_layout)

    # Title
    title_shape = slide.shapes.title
    title_shape.text = title

    # Body
    body_shape = slide.placeholders[1]
    text_frame = body_shape.text_frame
    text_frame.clear()

    for item in bullets:
        if isinstance(item, tuple):
            text, level = item
        else:
            text = item
            level = 0

        p = text_frame.add_paragraph()
        p.text = text
        p.level = level
        p.font.size = Pt(bullet_size - (level * 2))  # Smaller for sub-bullets
        p.space_before = Pt(8) if level == 0 else Pt(4)

    return slide


def add_two_column_slide(
    prs: Presentation,
    title: str,
    left_content: Union[str, List[str]],
    right_content: Union[str, List[str]],
    left_title: str = "",
    right_title: str = "",
    content_size: int = 18
) -> Any:
    """
    Add a slide with two columns of content.

    Args:
        prs: Presentation object
        title: Slide title
        left_content: Content for left column (string or list of strings)
        right_content: Content for right column (string or list of strings)
        left_title: Optional title for left column
        right_title: Optional title for right column
        content_size: Font size for content in points

    Returns:
        Slide object

    Example:
        >>> add_two_column_slide(
        ...     prs,
        ...     "Comparison",
        ...     left_content=["Point 1", "Point 2"],
        ...     right_content=["Point A", "Point B"],
        ...     left_title="Before",
        ...     right_title="After"
        ... )
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    # Title
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.5), Inches(9), Inches(0.8)
    )
    title_frame = title_box.text_frame
    title_frame.text = title
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True

    # Left column
    left_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(1.5), Inches(4.5), Inches(5)
    )
    _populate_text_box(left_box.text_frame, left_title, left_content, content_size)

    # Right column
    right_box = slide.shapes.add_textbox(
        Inches(5.5), Inches(1.5), Inches(4), Inches(5)
    )
    _populate_text_box(right_box.text_frame, right_title, right_content, content_size)

    return slide


def _populate_text_box(
    text_frame: Any,
    title: str,
    content: Union[str, List[str]],
    size: int
) -> None:
    """Helper function to populate a text box."""
    if title:
        text_frame.text = title
        text_frame.paragraphs[0].font.size = Pt(size + 4)
        text_frame.paragraphs[0].font.bold = True

    if isinstance(content, str):
        p = text_frame.add_paragraph() if title else text_frame.paragraphs[0]
        p.text = content
        p.font.size = Pt(size)
    elif isinstance(content, list):
        for i, item in enumerate(content):
            if i == 0 and not title:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(size)
            p.level = 0 if not title else 1


# ==================== Chart Creation ====================

def add_chart_slide(
    prs: Presentation,
    title: str,
    chart_type: str,
    categories: List[str],
    series_data: Union[List[float], Dict[str, List[float]]],
    chart_position: Optional[Tuple[float, float, float, float]] = None,
    show_legend: bool = True,
    show_data_labels: bool = False,
    layout_index: int = 5
) -> Any:
    """
    Add a slide with a chart.

    Args:
        prs: Presentation object
        title: Slide title
        chart_type: Chart type ('bar', 'line', 'pie', 'column', 'area')
        categories: List of category labels
        series_data: Single series (list of values) or multiple series (dict)
                    Example single: [10, 20, 30]
                    Example multi: {'Series 1': [10, 20, 30], 'Series 2': [15, 25, 35]}
        chart_position: Optional tuple of (left, top, width, height) in inches
        show_legend: Display chart legend
        show_data_labels: Display data labels on chart
        layout_index: Slide layout index (default: 5 = Title Only)

    Returns:
        Slide object

    Example:
        >>> add_chart_slide(
        ...     prs,
        ...     "Sales Data",
        ...     chart_type='bar',
        ...     categories=['Q1', 'Q2', 'Q3', 'Q4'],
        ...     series_data={'2024': [10, 12, 11, 15], '2025': [12, 15, 14, 18]}
        ... )
    """
    slide_layout = prs.slide_layouts[layout_index]
    slide = prs.slides.add_slide(slide_layout)

    # Title
    title_shape = slide.shapes.title
    title_shape.text = title

    # Chart type mapping
    chart_types = {
        'bar': XL_CHART_TYPE.BAR_CLUSTERED,
        'column': XL_CHART_TYPE.COLUMN_CLUSTERED,
        'line': XL_CHART_TYPE.LINE,
        'pie': XL_CHART_TYPE.PIE,
        'area': XL_CHART_TYPE.AREA
    }

    if chart_type.lower() not in chart_types:
        raise ValueError(f"chart_type must be one of: {list(chart_types.keys())}")

    xl_chart_type = chart_types[chart_type.lower()]

    # Prepare chart data
    chart_data = CategoryChartData()
    chart_data.categories = categories

    if isinstance(series_data, dict):
        # Multiple series
        for series_name, values in series_data.items():
            chart_data.add_series(series_name, values)
    else:
        # Single series
        chart_data.add_series('Series 1', series_data)

    # Chart position
    if chart_position:
        x, y, cx, cy = [Inches(v) for v in chart_position]
    else:
        x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)

    # Add chart
    chart = slide.shapes.add_chart(
        xl_chart_type, x, y, cx, cy, chart_data
    ).chart

    # Configure chart
    chart.has_legend = show_legend
    if show_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False

    # Data labels
    if show_data_labels and chart_type.lower() != 'pie':
        chart.plots[0].has_data_labels = True

    # Pie chart specific
    if chart_type.lower() == 'pie':
        chart.plots[0].has_data_labels = True
        data_labels = chart.plots[0].data_labels
        data_labels.show_percentage = True

    return slide


# ==================== Image Handling ====================

def add_image_slide(
    prs: Presentation,
    title: str,
    image_path: str,
    caption: str = "",
    center: bool = True,
    max_width: Optional[float] = None,
    max_height: Optional[float] = None,
    layout_index: int = 6
) -> Any:
    """
    Add a slide with an image.

    Args:
        prs: Presentation object
        title: Slide title
        image_path: Path to image file
        caption: Optional caption below image
        center: Center the image on slide
        max_width: Maximum image width in inches (optional)
        max_height: Maximum image height in inches (optional)
        layout_index: Slide layout index (default: 6 = Blank)

    Returns:
        Slide object

    Example:
        >>> add_image_slide(
        ...     prs,
        ...     "Product Photo",
        ...     "product.jpg",
        ...     caption="New Widget 2025",
        ...     center=True
        ... )
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    slide_layout = prs.slide_layouts[layout_index]
    slide = prs.slides.add_slide(slide_layout)

    # Title
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3), Inches(9), Inches(0.6)
    )
    title_frame = title_box.text_frame
    title_frame.text = title
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True

    # Calculate image size
    if max_width is None:
        max_width = 9.0
    if max_height is None:
        max_height = 5.5 if caption else 6.0

    # Add image
    pic = slide.shapes.add_picture(
        image_path,
        Inches(0.5),
        Inches(1.2),
        height=Inches(max_height)
    )

    # Ensure width constraint
    if pic.width > Inches(max_width):
        aspect_ratio = pic.height / pic.width
        pic.width = Inches(max_width)
        pic.height = int(pic.width * aspect_ratio)

    # Center if requested
    if center:
        pic.left = int((prs.slide_width - pic.width) / 2)

    # Caption
    if caption:
        caption_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(6.8), Inches(9), Inches(0.5)
        )
        tf = caption_box.text_frame
        tf.text = caption
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    return slide


def optimize_image_for_ppt(
    image_path: str,
    output_path: Optional[str] = None,
    max_size: Tuple[int, int] = (1920, 1080),
    quality: int = 85
) -> str:
    """
    Optimize an image for PowerPoint (reduce size, maintain quality).

    Args:
        image_path: Path to input image
        output_path: Path for optimized image (optional, defaults to input_optimized.ext)
        max_size: Maximum dimensions (width, height) in pixels
        quality: JPEG quality (1-100)

    Returns:
        Path to optimized image

    Example:
        >>> optimized = optimize_image_for_ppt(
        ...     "large_photo.jpg",
        ...     max_size=(1920, 1080),
        ...     quality=85
        ... )
    """
    if not PIL_AVAILABLE:
        raise ImportError("Pillow is required for image optimization. Install with: pip install Pillow")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Default output path
    if output_path is None:
        path = Path(image_path)
        output_path = str(path.parent / f"{path.stem}_optimized{path.suffix}")

    # Open and optimize
    with Image.open(image_path) as img:
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Resize if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save with optimization
        img.save(output_path, optimize=True, quality=quality)

    print(f"Image optimized: {output_path}")
    print(f"  Original: {os.path.getsize(image_path) / 1024:.1f} KB")
    print(f"  Optimized: {os.path.getsize(output_path) / 1024:.1f} KB")

    return output_path


# ==================== Table Creation ====================

def add_table_slide(
    prs: Presentation,
    title: str,
    headers: List[str],
    data: List[List[str]],
    col_widths: Optional[List[float]] = None,
    header_color: Optional[RGBColor] = None,
    header_text_color: Optional[RGBColor] = None,
    layout_index: int = 5
) -> Any:
    """
    Add a slide with a formatted table.

    Args:
        prs: Presentation object
        title: Slide title
        headers: List of column headers
        data: List of rows (each row is a list of cell values)
        col_widths: Optional list of column widths in inches
        header_color: Background color for header row
        header_text_color: Text color for header row
        layout_index: Slide layout index (default: 5 = Title Only)

    Returns:
        Slide object

    Example:
        >>> add_table_slide(
        ...     prs,
        ...     "Sales Report",
        ...     headers=['Product', 'Q1', 'Q2', 'Q3', 'Q4'],
        ...     data=[
        ...         ['Widget A', '$100', '$120', '$110', '$130'],
        ...         ['Widget B', '$200', '$220', '$210', '$240']
        ...     ]
        ... )
    """
    slide_layout = prs.slide_layouts[layout_index]
    slide = prs.slides.add_slide(slide_layout)

    # Title
    title_shape = slide.shapes.title
    title_shape.text = title

    # Table dimensions
    rows = len(data) + 1  # +1 for header
    cols = len(headers)

    # Default positioning
    left = Inches(1)
    top = Inches(2)
    width = Inches(8)
    height = Inches(4)

    # Create table
    table = slide.shapes.add_table(rows, cols, left, top, width, height).table

    # Set column widths
    if col_widths:
        for col_idx, col_width in enumerate(col_widths):
            table.columns[col_idx].width = Inches(col_width)
    else:
        # Equal widths
        col_width = width / cols
        for col in range(cols):
            table.columns[col].width = col_width

    # Default colors
    if header_color is None:
        header_color = RGBColor(0, 51, 102)
    if header_text_color is None:
        header_text_color = RGBColor(255, 255, 255)

    # Populate headers
    for col_idx, header in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = header
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(12)
        cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

        # Header styling
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_color
        cell.text_frame.paragraphs[0].font.color.rgb = header_text_color

    # Populate data
    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, value in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.text = str(value)
            cell.text_frame.paragraphs[0].font.size = Pt(11)
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    return slide


# ==================== Styling & Formatting ====================

def apply_brand_colors(
    shape: Any,
    brand: str = 'corporate',
    element_type: str = 'text'
) -> None:
    """
    Apply brand color scheme to a shape.

    Args:
        shape: Shape object to style
        brand: Brand name ('corporate', 'tech', 'creative', 'modern')
        element_type: Type of element ('text', 'title', 'fill', 'accent')

    Example:
        >>> title = slide.shapes.title
        >>> apply_brand_colors(title, brand='corporate', element_type='title')
    """
    if brand not in BRAND_COLORS:
        raise ValueError(f"Brand must be one of: {list(BRAND_COLORS.keys())}")

    colors = BRAND_COLORS[brand]

    if element_type == 'title':
        if hasattr(shape, 'text_frame'):
            shape.text_frame.paragraphs[0].font.color.rgb = colors['primary']
    elif element_type == 'text':
        if hasattr(shape, 'text_frame'):
            shape.text_frame.paragraphs[0].font.color.rgb = colors['text']
    elif element_type == 'fill':
        shape.fill.solid()
        shape.fill.fore_color.rgb = colors['primary']
    elif element_type == 'accent':
        if hasattr(shape, 'text_frame'):
            shape.text_frame.paragraphs[0].font.color.rgb = colors['accent']
        else:
            shape.fill.solid()
            shape.fill.fore_color.rgb = colors['accent']


def set_text_format(
    text_frame: Any,
    size: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    color: Optional[RGBColor] = None,
    alignment: Optional[PP_ALIGN] = None
) -> None:
    """
    Apply text formatting to a text frame.

    Args:
        text_frame: TextFrame object
        size: Font size in points
        bold: Bold text
        italic: Italic text
        color: RGB color
        alignment: Text alignment (PP_ALIGN.LEFT, CENTER, RIGHT)

    Example:
        >>> set_text_format(
        ...     shape.text_frame,
        ...     size=24,
        ...     bold=True,
        ...     color=RGBColor(0, 51, 102)
        ... )
    """
    for paragraph in text_frame.paragraphs:
        if size is not None:
            paragraph.font.size = Pt(size)
        if bold is not None:
            paragraph.font.bold = bold
        if italic is not None:
            paragraph.font.italic = italic
        if color is not None:
            paragraph.font.color.rgb = color
        if alignment is not None:
            paragraph.alignment = alignment


# ==================== Utility Functions ====================

def get_layout_info(prs: Presentation) -> Dict[int, str]:
    """
    Get information about available slide layouts.

    Args:
        prs: Presentation object

    Returns:
        Dictionary mapping layout index to layout name

    Example:
        >>> layouts = get_layout_info(prs)
        >>> print(layouts)
        {0: 'Title Slide', 1: 'Title and Content', ...}
    """
    layouts = {}
    for idx, layout in enumerate(prs.slide_layouts):
        layouts[idx] = layout.name
    return layouts


def add_footer(
    slide: Any,
    text: str,
    position: str = 'center',
    font_size: int = 10
) -> None:
    """
    Add footer text to a slide.

    Args:
        slide: Slide object
        text: Footer text
        position: Position ('left', 'center', 'right')
        font_size: Font size in points

    Example:
        >>> add_footer(slide, "© 2025 Company Name", position='right')
    """
    if position == 'left':
        left = Inches(0.5)
    elif position == 'center':
        left = Inches(3.5)
    else:  # right
        left = Inches(7)

    footer_box = slide.shapes.add_textbox(
        left, Inches(7), Inches(2), Inches(0.3)
    )
    tf = footer_box.text_frame
    tf.text = text
    tf.paragraphs[0].font.size = Pt(font_size)

    if position == 'center':
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    elif position == 'right':
        tf.paragraphs[0].alignment = PP_ALIGN.RIGHT


def add_page_numbers(prs: Presentation, start_slide: int = 1) -> None:
    """
    Add page numbers to slides (starting from specified slide).

    Args:
        prs: Presentation object
        start_slide: Slide index to start numbering (0-indexed)

    Example:
        >>> add_page_numbers(prs, start_slide=1)  # Skip title slide
    """
    for idx, slide in enumerate(prs.slides):
        if idx >= start_slide:
            page_num = idx - start_slide + 1
            add_footer(slide, str(page_num), position='right', font_size=10)


def duplicate_slide(prs: Presentation, slide_index: int) -> Any:
    """
    Duplicate a slide at the specified index.

    Args:
        prs: Presentation object
        slide_index: Index of slide to duplicate (0-indexed)

    Returns:
        New slide object

    Example:
        >>> new_slide = duplicate_slide(prs, 2)  # Duplicate 3rd slide
    """
    import copy

    source_slide = prs.slides[slide_index]
    blank_slide_layout = prs.slide_layouts[6]

    dest_slide = prs.slides.add_slide(blank_slide_layout)

    for shape in source_slide.shapes:
        el = shape.element
        newel = copy.deepcopy(el)
        dest_slide.shapes._spTree.insert_element_before(newel, 'p:extLst')

    return dest_slide


def save_presentation(
    prs: Presentation,
    filename: str,
    verbose: bool = True
) -> str:
    """
    Save presentation with validation.

    Args:
        prs: Presentation object
        filename: Output filename
        verbose: Print confirmation message

    Returns:
        Absolute path to saved file

    Example:
        >>> save_presentation(prs, "output.pptx")
    """
    # Ensure .pptx extension
    if not filename.endswith('.pptx'):
        filename += '.pptx'

    # Save
    prs.save(filename)

    # Get absolute path
    abs_path = os.path.abspath(filename)

    if verbose:
        file_size = os.path.getsize(abs_path) / (1024 * 1024)  # MB
        print(f"Presentation saved: {abs_path}")
        print(f"  Slides: {len(prs.slides)}")
        print(f"  Size: {file_size:.2f} MB")

    return abs_path


# ==================== Example Usage ====================

def create_example_presentation():
    """Create a complete example presentation demonstrating all features."""

    # Create presentation
    prs = create_presentation(
        title="Example Presentation",
        author="PowerPoint Helper",
        aspect_ratio="16:9"
    )

    # 1. Title slide
    add_title_slide(
        prs,
        "PowerPoint Helper Demo",
        "Comprehensive Example Presentation",
        title_color=BRAND_COLORS['corporate']['primary']
    )

    # 2. Bullet slide
    add_bullet_slide(
        prs,
        "Features",
        [
            "Easy slide creation",
            ("Bullet points", 0),
            ("Sub-bullets", 1),
            ("Multi-level support", 1),
            "Charts and graphs",
            "Images and tables"
        ]
    )

    # 3. Two-column slide
    add_two_column_slide(
        prs,
        "Comparison",
        left_content=["Simple API", "Type hints", "Documentation"],
        right_content=["Professional output", "Brand colors", "Automation"],
        left_title="Developer Experience",
        right_title="Results"
    )

    # 4. Chart slide
    add_chart_slide(
        prs,
        "Revenue Growth",
        chart_type='column',
        categories=['Q1', 'Q2', 'Q3', 'Q4'],
        series_data={
            '2024': [100, 120, 115, 140],
            '2025': [130, 150, 145, 170]
        },
        show_legend=True,
        show_data_labels=True
    )

    # 5. Table slide
    add_table_slide(
        prs,
        "Product Comparison",
        headers=['Product', 'Price', 'Rating', 'Sales'],
        data=[
            ['Widget A', '$299', '4.5★', '1,234'],
            ['Widget B', '$399', '4.7★', '2,456'],
            ['Widget C', '$499', '4.9★', '3,789']
        ],
        header_color=BRAND_COLORS['corporate']['primary']
    )

    # Add page numbers (skip title slide)
    add_page_numbers(prs, start_slide=1)

    # Save
    output_path = save_presentation(prs, "example_presentation.pptx")

    return output_path


if __name__ == "__main__":
    print("PowerPoint Helper Module")
    print("=" * 50)
    print("\nCreating example presentation...")

    try:
        output = create_example_presentation()
        print(f"\nExample created successfully!")
        print(f"Open: {output}")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure python-pptx is installed:")
        print("  pip install python-pptx")
