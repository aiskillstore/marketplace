# -*- coding: utf-8 -*-
"""Layout calculation utilities for converting HTML pixels to PowerPoint inches

Support dynamic flow layout:
- Multiple elements of the same step stacked vertically
- Use FlowLayout to track current vertical position"""

import re
from pptx.util import Inches, Pt
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional


# Design dimensions (matching HTML framework)
DESIGN = {
    'width_px': 1280,
    'height_px': 720,
    'width_inch': 10.0,
    'height_inch': 5.625,
    'padding_px': 44,
    'gap_px': 14,
    'gap_small_px': 11,
    'radius_lg_px': 16,
    'radius_md_px': 12,
}

# Calculated values
PX_TO_INCH_RATIO = DESIGN['width_inch'] / DESIGN['width_px']

# vmin/vmax unit conversion (1vmin = 1% of min(width, height))
VMIN_PX = min(DESIGN['width_px'], DESIGN['height_px']) / 100  # 7.2px per vmin
VMAX_PX = max(DESIGN['width_px'], DESIGN['height_px']) / 100  # 12.8px per vmax


@dataclass
class StyleMargins:
    """Parsed margins from style attribute"""
    top: float = 0.0      # in inches
    bottom: float = 0.0   # in inches
    left: float = 0.0     # in inches
    right: float = 0.0    # in inches
    width: Optional[float] = None  # in inches, None means auto


def parse_css_value(value_str: str) -> float:
    """Parse CSS values and convert to pixels
    Support: px, vmin, vmax, %"""
    value_str = value_str.strip()
    
    # Match values ​​and units
    match = re.match(r'^([\d.]+)(px|vmin|vmax|%)?$', value_str)
    if not match:
        return 0.0
    
    num = float(match.group(1))
    unit = match.group(2) or 'px'
    
    if unit == 'px':
        return num
    elif unit == 'vmin':
        return num * VMIN_PX
    elif unit == 'vmax':
        return num * VMAX_PX
    elif unit == '%':
        # Percentage relative to content area width
        return num / 100 * (DESIGN['width_px'] - 2 * DESIGN['padding_px'])
    
    return num


def parse_style(style_str: str) -> StyleMargins:
    """Parse the style attribute string and extract margin and width information
    For example: "margin-top: 10vmin; margin-bottom: 1.5vmin; width: 85%;""""
    margins = StyleMargins()
    
    if not style_str:
        return margins
    
    # Parse each CSS property
    for prop in style_str.split(';'):
        prop = prop.strip()
        if not prop or ':' not in prop:
            continue
        
        key, value = prop.split(':', 1)
        key = key.strip().lower()
        value = value.strip()
        
        px_value = parse_css_value(value)
        inch_value = px_value * PX_TO_INCH_RATIO
        
        if key == 'margin-top':
            margins.top = inch_value
        elif key == 'margin-bottom':
            margins.bottom = inch_value
        elif key == 'margin-left':
            margins.left = inch_value
        elif key == 'margin-right':
            margins.right = inch_value
        elif key == 'margin':
            # Abbreviated form, unified setting
            margins.top = margins.bottom = margins.left = margins.right = inch_value
        elif key == 'width':
            margins.width = inch_value
    
    return margins


@dataclass
class Rect:
    """Rectangle with position and size"""
    x: float
    y: float
    width: float
    height: float
    
    def to_inches(self) -> Tuple:
        """Return as (Inches(x), Inches(y), Inches(w), Inches(h))"""
        return (Inches(self.x), Inches(self.y), 
                Inches(self.width), Inches(self.height))
    
    def offset_y(self, dy: float) -> 'Rect':
        """Return a new Rect with y offset"""
        return Rect(self.x, self.y + dy, self.width, self.height)


class FlowLayoutContext:
    """Tracks the current vertical position in a fluid layout.
    Used for vertical stacking of multiple elements in the same step."""
    
    def __init__(self, start_y: float = None):
        self.current_y = start_y or px_to_inch(130)  # Default content area top
        self.gap = px_to_inch(20)  # Element spacing (increased to 20px)
    
    def reset(self, start_y: float = None):
        """Reset to specified location"""
        self.current_y = start_y or px_to_inch(130)
    
    def advance(self, height: float, extra_gap: float = 0):
        """Move down the specified height + spacing"""
        self.current_y += height + self.gap + extra_gap
    
    def get_y(self) -> float:
        """Get the current Y position"""
        return self.current_y


class LayoutCalculator:
    """Calculates positions and sizes for PowerPoint elements.
    Uses the same layout logic as the HTML framework.
    
    Two modes are supported:
    1. Fixed layout: use predefined positions
    2. Flow layout: use FlowLayoutContext to dynamically calculate"""
    
    def __init__(self):
        self.slide_width = DESIGN['width_inch']
        self.slide_height = DESIGN['height_inch']
        self.padding = px_to_inch(DESIGN['padding_px'])
        self.gap = px_to_inch(DESIGN['gap_px'])
        self.gap_small = px_to_inch(DESIGN['gap_small_px'])
        
        # Content area (excluding padding)
        self.content_width = self.slide_width - 2 * self.padding
        self.content_height = self.slide_height - 2 * self.padding
        self.content_left = self.padding
        self.content_top = self.padding
        
        # Fluid layout context
        self.flow = FlowLayoutContext()
    
    # ===== Hero Mode Layout (Step 0) =====
    
    def hero_badge(self) -> Rect:
        """Badge position in Hero mode (centered, upper portion)"""
        width = px_to_inch(180)
        height = px_to_inch(28)
        return Rect(
            x=center_x(width),
            y=px_to_inch(200),  # Upper part of center area
            width=width,
            height=height
        )
    
    def hero_title(self) -> Rect:
        """Title position in Hero mode (large, centered)"""
        width = self.content_width
        height = px_to_inch(60)
        return Rect(
            x=self.content_left,
            y=px_to_inch(240),
            width=width,
            height=height
        )
    
    def hero_subtitle(self) -> Rect:
        """Subtitle position in Hero mode"""
        width = self.content_width - px_to_inch(200)
        height = px_to_inch(30)
        return Rect(
            x=center_x(width),
            y=px_to_inch(310),
            width=width,
            height=height
        )
    
    def hero_author(self) -> Rect:
        """Author position in Hero mode (below subtitle)"""
        width = px_to_inch(300)
        height = px_to_inch(24)
        return Rect(
            x=center_x(width),
            y=px_to_inch(360),
            width=width,
            height=height
        )
    
    def hero_click_hint(self) -> Rect:
        """Click hint position at bottom of Hero mode"""
        width = px_to_inch(200)
        height = px_to_inch(40)
        return Rect(
            x=center_x(width),
            y=px_to_inch(480),
            width=width,
            height=height
        )
    
    # ===== Content Mode Layout (Step 1+) =====
    
    def content_badge(self) -> Rect:
        """Badge position in Content mode (smaller, top)"""
        width = px_to_inch(160)
        height = px_to_inch(24)
        return Rect(
            x=center_x(width),
            y=px_to_inch(24),
            width=width,
            height=height
        )
    
    def content_title(self) -> Rect:
        """Title position in Content mode (smaller, top)"""
        width = self.content_width
        height = px_to_inch(40)
        return Rect(
            x=self.content_left,
            y=px_to_inch(52),
            width=width,
            height=height
        )
    
    def content_subtitle(self) -> Rect:
        """Subtitle position in Content mode"""
        width = self.content_width - px_to_inch(200)
        height = px_to_inch(24)
        return Rect(
            x=center_x(width),
            y=px_to_inch(96),
            width=width,
            height=height
        )
    
    def content_area_top(self) -> float:
        """Top of the content area (below header)"""
        return px_to_inch(130)
    
    def reset_flow(self, start_y: float = None):
        """Reset flow layout to top of content area"""
        self.flow.reset(start_y or self.content_area_top())
    
    # ===== Component Layouts (supports fluid layout) =====
    # The dimensions are referenced from components.css and remain visually consistent with the HTML version.
    
    def comparison_cards(self, y_offset: float = None, custom_width: float = None, 
                         left_items: int = 3, right_items: int = 3) -> Tuple[Rect, Rect, float]:
        """Layout for comparison cards (left and right)
        CSS: .comparison-card { flex: 0 1 45%; padding: 16px 18px; }
        CSS: .comparison-card h4 { margin-bottom: 10px; padding-bottom: 8px; }
        CSS: .comparison-list li { padding: 6px 0; }
        
        Dynamic height based on items count (increasing the height of each item supports wrapping of long text):
        - padding top/bottom: 16px each = 32px
        - title + divider: ~30px
        - each item: 36px height (supports 2 rows) + 6px gap = 42px"""
        gap = px_to_inch(16)  # CSS gap: 16px
        
        # Calculate card height based on items
        # CSS: padding: 16px 18px -> vertical padding = 16px * 2 = 32px
        # Title area: ~30px (22px title + 8px padding-bottom)
        # Each item: 36px height (supports long text wrapping) + 6px padding = 42px
        base_height = 32 + 30  # padding + title area
        item_height = 42  # per item (increased from 24px to 42px, supports 2 lines of text)
        
        max_items = max(left_items, right_items, 1)
        card_height = px_to_inch(base_height + max_items * item_height)
        
        # If a custom total width is specified, it is divided proportionally between the two cards.
        if custom_width:
            total_width = custom_width
        else:
            # CSS: flex: 0 1 45% per card, total about 90% + gap
            total_width = self.content_width * 0.90
        
        card_width = (total_width - gap) / 2
        start_x = center_x(total_width)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        left = Rect(start_x, y, card_width, card_height)
        right = Rect(start_x + card_width + gap, y, card_width, card_height)
        
        return left, right, card_height
    
    def terminal(self, y_offset: float = None, custom_width: float = None, 
                 content_lines: int = 3) -> Tuple[Rect, float]:
        """Layout for terminal block
        CSS: .terminal { width: 90%; max-width: 600px; }
        CSS: .terminal-body { line-height: 2; font-size: 13px; }
        
        content_lines: Number of content lines, used to dynamically calculate height"""
        width = custom_width or px_to_inch(600)  # max-width: 600px
        # Dynamically calculate height:
        # - header: 36px (padding 12px * 2 + dots 12px)
        # - body padding: 32px (16px * 2)
        # - Approximately 26px per line (font 13px * line-height 2)
        # Minimum height 110px
        base_height = 110
        line_height = 26
        height = px_to_inch(base_height + max(0, content_lines - 2) * line_height)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        return Rect(
            x=center_x(width),
            y=y,
            width=width,
            height=height
        ), height
    
    def quote(self, y_offset: float = None, multiline: bool = False) -> Tuple[Rect, float]:
        """Layout for quote block
        CSS: .quote-block { max-width: 75%; padding: 20px 28px; }
        
        multiline: If True, use a larger height to support multi-line references"""
        width = self.content_width * 0.75  # max-width: 75%
        # Increased height to support multi-line quotes (from 80px to 100px, use 120px for multi-line)
        height = px_to_inch(120 if multiline else 100)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        return Rect(
            x=center_x(width),
            y=y,
            width=width,
            height=height
        ), height
    
    def assumptions_grid(self, count: int = 4, y_offset: float = None) -> Tuple[list, float]:
        """Layout for assumption grid (2x2)
        CSS: .assumption-grid { grid-template-columns: repeat(2, 1fr); gap: 14px; max-width: 85%; }
        
        Internal size calculation (increased height to support wrapping of long text):
        - pad_y: 14px
        - text_height: 22px (old text)
        - gap: 8px
        - text_height: 44px (new text - supports 2 lines)
        - pad_y: 14px (bottom)
        Total = 14 + 22 + 8 + 44 + 14 = 102px -> use 120px to allow more space"""
        total_width = self.content_width * 0.85  # max-width: 85%
        gap = px_to_inch(14)  # CSS gap: 14px
        card_width = (total_width - gap) / 2
        card_height = px_to_inch(120)  # Increased height to accommodate long text wrapping (from 82px to 120px)
        
        start_x = center_x(total_width)
        start_y = y_offset if y_offset is not None else self.flow.get_y()
        
        rows = (count + 1) // 2
        total_height = rows * card_height + (rows - 1) * gap
        
        rects = []
        for i in range(count):
            row = i // 2
            col = i % 2
            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)
            rects.append(Rect(x, y, card_width, card_height))
        
        return rects, total_height
    
    def timeline_items(self, count: int = 4, y_offset: float = None) -> Tuple[list, float]:
        """Layout for timeline items (horizontal row)
        CSS: .timeline { display: flex; gap: 12px; width: 90%; }
        CSS: .timeline-item { flex: 1; padding: 14px; }
        
        Internal size calculation (increase case height to support long text):
        - pad: 14px * 2 = 28px
        - badge: 22px + gap: 8px = 30px
        - icon: 28px + gap: 8px = 36px
        - title: 18px + gap: 4px = 22px
        - desc: 16px + gap: 4px = 20px
        - case: 36px (added to support line wrapping for long text)
        Total = 28 + 30 + 36 + 22 + 20 + 36 = 172px -> use 190px"""
        total_width = self.content_width * 0.90  # width: 90%
        gap = px_to_inch(12)  # CSS gap: 12px
        
        # flex: 1 equal width
        item_width = (total_width - (count - 1) * gap) / count
        item_height = px_to_inch(190)  # Increased height to accommodate case long text wrapping (from 170px to 190px)
        
        start_x = center_x(total_width)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        rects = []
        for i in range(count):
            x = start_x + i * (item_width + gap)
            rects.append(Rect(x, y, item_width, item_height))
        
        return rects, item_height
    
    def stats_items(self, count: int = 3, y_offset: float = None) -> Tuple[list, float]:
        """Layout for stats row
        CSS: .stats-row { display: flex; gap: 20px; }
        CSS: .stat-item { padding: 16px 20px; min-width: 120px; }
        
        Internal size calculation (increase label height to support long text):
        - pad: 16px
        - icon_wrapper: 40px + gap: 10px = 50px
        - value: 28px + gap: 4px = 32px
        - label: 36px (supports 2 lines of label text)
        - pad: 16px (bottom)
        Total = 16 + 50 + 32 + 36 + 16 = 150px -> use 155px"""
        item_width = px_to_inch(140)  # min-width: 120px + padding
        item_height = px_to_inch(155)  # Increased height to accommodate long label text (from 140px to 155px)
        gap = px_to_inch(20)  # CSS gap: 20px
        
        total_width = count * item_width + (count - 1) * gap
        start_x = center_x(total_width)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        rects = []
        for i in range(count):
            x = start_x + i * (item_width + gap)
            rects.append(Rect(x, y, item_width, item_height))
        
        return rects, item_height
    
    def value_cards(self, count: int = 3, y_offset: float = None) -> Tuple[list, float]:
        """Layout for value cards (horizontal row)
        CSS: .value-cards { display: flex; gap: 14px; width: 85%; }
        CSS: .value-card { flex: 1; padding: 16px 12px; }
        
        Internal size calculation (increase desc height to support long text):
        - pad_y: 16px
        - icon_size: 44px + gap: 8px = 52px
        - title_h: 20px + gap: 8px = 28px
        - desc_h: 48px (supports 2 lines of description text)
        - pad_y: 16px (bottom)
        Total = 16 + 52 + 28 + 48 + 16 = 160px -> use 168px"""
        total_width = self.content_width * 0.85  # width: 85%
        gap = px_to_inch(14)  # CSS gap: 14px
        
        # flex: 1 equal width
        card_width = (total_width - (count - 1) * gap) / count
        card_height = px_to_inch(168)  # Increased height to accommodate long description text (from 150px to 168px)
        
        start_x = center_x(total_width)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        rects = []
        for i in range(count):
            x = start_x + i * (card_width + gap)
            rects.append(Rect(x, y, card_width, card_height))
        
        return rects, card_height
    
    def competition_box(self, y_offset: float = None) -> Tuple[Rect, float]:
        """Layout for competition analysis box
        CSS: .competition-box { max-width: 60%; padding: 16px 26px; }
        
        Internal size calculation:
        - pad_y: 16px
        - title_height: 20px + gap: 10px = 30px
        - items_height: 28px + gap: 10px = 38px
        - conclusion_height: 22px
        - pad_y: 16px (bottom)
        Total = 16 + 30 + 38 + 22 + 16 = 122px"""
        width = self.content_width * 0.65  # Slightly larger than 60% to accommodate content
        height = px_to_inch(125)  # Increase height to accommodate all content
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        return Rect(
            x=center_x(width),
            y=y,
            width=width,
            height=height
        ), height
    
    def strategy_box(self, y_offset: float = None, items_count: int = 3) -> Tuple[Rect, float]:
        """Layout for strategy box
        CSS: .strategy-box { max-width: 60%; padding: 18px 26px; }
        
        Internal size calculation:
        - pad_y: 18px
        - title_height: 22px + gap: 14px = 36px
        - each item: 28px + 8px gap = 36px
        - final_height: 24px
        - pad_y: 18px (bottom)
        Total = 18 + 36 + (items * 36) + 24 + 18 = 96 + items * 36"""
        width = self.content_width * 0.65
        # Dynamically calculate height
        base_height = 96  # padding + title + final
        item_height = 36  # per item
        height = px_to_inch(base_height + items_count * item_height)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        return Rect(
            x=center_x(width),
            y=y,
            width=width,
            height=height
        ), height
    
    def ending_layout(self, y_offset: float = None) -> Tuple[dict, float]:
        """Layout for ending slide elements"""
        y = y_offset if y_offset is not None else self.flow.get_y()
        height = px_to_inch(160)
        
        return {
            'icon': Rect(0, y, self.slide_width, px_to_inch(50)),
            'message': Rect(0, y + px_to_inch(60), self.slide_width, px_to_inch(50)),
            'thanks': Rect(0, y + px_to_inch(120), self.slide_width, px_to_inch(40)),
        }, height
    
    # ===== Image Component Layouts =====
    
    def image_single(self, has_caption: bool = False, y_offset: float = None) -> Tuple[dict, float]:
        """Layout for single image display"""
        img_width = px_to_inch(450)
        img_height = px_to_inch(150)  # compact height
        caption_height = px_to_inch(20) if has_caption else 0
        
        total_height = img_height + caption_height + (px_to_inch(6) if has_caption else 0)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        return {
            'image': Rect(center_x(img_width), y, img_width, img_height),
            'caption': Rect(center_x(img_width), y + img_height + px_to_inch(6), 
                          img_width, caption_height) if has_caption else None
        }, total_height
    
    def image_grid(self, count: int, columns: int = None, y_offset: float = None) -> Tuple[list, float]:
        """Layout for image grid - new style: images are spread all over the place, titles are covered at the bottom"""
        if columns is None:
            columns = min(count, 4)
        rows = (count + columns - 1) // columns
        
        # Dynamically calculate the item width based on the number of columns to maximize the use of content area
        max_total_width = self.content_width * 0.92  # Use 92% of content area width
        gap = px_to_inch(12)  # 12px gap
        
        # Calculate the width of a single item
        item_width = (max_total_width - (columns - 1) * gap) / columns
        # Calculate the height according to the aspect ratio of 16:10 (consistent with HTML aspect-ratio: 16/10)
        item_height = item_width * (10 / 16)
        
        # Title coverage area (at the bottom of the image)
        title_height = px_to_inch(32)  # title area height
        
        total_width = columns * item_width + (columns - 1) * gap
        total_height = rows * item_height + (rows - 1) * gap
        start_x = center_x(total_width)
        start_y = y_offset if y_offset is not None else self.flow.get_y()
        
        rects = []
        for i in range(count):
            row = i // columns
            col = i % columns
            x = start_x + col * (item_width + gap)
            y = start_y + row * (item_height + gap)
            rects.append({
                # Pictures cover the entire project area
                'image': Rect(x, y, item_width, item_height),
                # Title overlaid at bottom of image
                'title_overlay': Rect(x, y + item_height - title_height, item_width, title_height)
            })
        
        return rects, total_height
    
    def image_side(self, img_position: str = 'left', y_offset: float = None) -> Tuple[dict, float]:
        """Layout for side-by-side image and content"""
        total_width = px_to_inch(900)
        img_width = px_to_inch(400)
        content_width = px_to_inch(450)
        height = px_to_inch(200)
        gap = self.gap
        
        start_x = center_x(total_width)
        y = y_offset if y_offset is not None else self.flow.get_y()
        
        if img_position == 'left':
            return {
                'image': Rect(start_x, y, img_width, height),
                'content': Rect(start_x + img_width + gap, y, content_width, height)
            }, height
        else:
            return {
                'content': Rect(start_x, y, content_width, height),
                'image': Rect(start_x + content_width + gap, y, img_width, height)
            }, height


# ===== Utility Functions =====

def px_to_inch(px: float) -> float:
    """Convert pixels to inches based on design width"""
    return px * PX_TO_INCH_RATIO


def inch_to_px(inch: float) -> float:
    """Convert inches to pixels"""
    return inch / PX_TO_INCH_RATIO


def center_x(element_width: float) -> float:
    """Calculate x position to center an element horizontally"""
    return (DESIGN['width_inch'] - element_width) / 2


def center_y(element_height: float) -> float:
    """Calculate y position to center an element vertically"""
    return (DESIGN['height_inch'] - element_height) / 2


def pt_to_inch(pt: float) -> float:
    """Convert points to inches (72 points = 1 inch)"""
    return pt / 72


def inch_to_pt(inch: float) -> float:
    """Convert inches to points"""
    return inch * 72
