#!/usr/bin/env python3
"""
Brand Extraction Script
Extracts brand data (colors, fonts) from WordPress theme files
"""

import re
import json
import argparse
from pathlib import Path

def extract_colors_from_css(css_content: str) -> dict:
    """Extract color definitions from CSS"""
    colors = {}

    # Look for CSS custom properties (--color-name: #hex)
    custom_props = re.findall(r'--([a-zA-Z-]+):\s*(#[0-9A-Fa-f]{3,6})', css_content)
    for name, hex_val in custom_props:
        colors[name] = {"hex": hex_val, "source": "css-variable"}

    # Look for Tailwind-style color definitions in comments
    # bg-csr-cream, text-csr-darkBlue etc
    tailwind_colors = re.findall(r'\.(?:bg|text|border)-([a-zA-Z-]+)\s*\{\s*(?:background-)?color:\s*(#[0-9A-Fa-f]{3,6})', css_content)
    for name, hex_val in tailwind_colors:
        colors[name] = {"hex": hex_val, "source": "tailwind"}

    # Look for direct hex colors in inline styles
    inline_hex = re.findall(r'(?:color|background(?:-color)?|border-color):\s*(#[0-9A-Fa-f]{6})', css_content)
    for i, hex_val in enumerate(set(inline_hex)):
        if hex_val.upper() not in [c.get("hex", "").upper() for c in colors.values()]:
            colors[f"color-{i}"] = {"hex": hex_val, "source": "inline"}

    return colors

def extract_colors_from_php(php_content: str) -> dict:
    """Extract color definitions from PHP/HTML"""
    colors = {}

    # Look for hex colors in style attributes
    hex_matches = re.findall(r'(?:color|background(?:-color)?|fill):\s*(#[0-9A-Fa-f]{6})', php_content)

    # Look for Tailwind classes with color hints
    tailwind_classes = re.findall(r'(?:bg|text|border)-\[#([0-9A-Fa-f]{6})\]', php_content)

    # Common CSR colors from classes
    if 'bg-csr-cream' in php_content or 'csr-cream' in php_content:
        colors['csr-cream'] = {"hex": "#EDEAE3", "source": "tailwind-class"}
    if 'text-csr-darkBlue' in php_content or 'csr-darkBlue' in php_content:
        colors['csr-darkBlue'] = {"hex": "#07254B", "source": "tailwind-class"}
    if 'text-csr-lightBlue' in php_content or 'csr-lightBlue' in php_content:
        colors['csr-lightBlue'] = {"hex": "#B4C1D1", "source": "tailwind-class"}

    for hex_val in set(hex_matches + ['#' + h for h in tailwind_classes]):
        if hex_val.upper() not in [c.get("hex", "").upper() for c in colors.values()]:
            colors[f"extracted-{len(colors)}"] = {"hex": hex_val, "source": "php"}

    return colors

def extract_fonts(content: str) -> list:
    """Extract font family references"""
    fonts = []

    # Google Fonts links
    google_fonts = re.findall(r'fonts\.googleapis\.com/css2?\?family=([^&"\']+)', content)
    for font in google_fonts:
        font_name = font.replace('+', ' ').split(':')[0]
        if font_name not in fonts:
            fonts.append(font_name)

    # Font-family CSS
    font_families = re.findall(r'font-family:\s*["\']?([^;"\',]+)', content)
    for font in font_families:
        font = font.strip()
        if font not in fonts and font not in ['inherit', 'sans-serif', 'serif', 'monospace']:
            fonts.append(font)

    return fonts

def analyze_theme(theme_path: str) -> dict:
    """Analyze a WordPress theme directory"""
    theme_dir = Path(theme_path)

    if not theme_dir.exists():
        return {"error": f"Theme directory not found: {theme_path}"}

    brand_data = {
        "colors": {},
        "fonts": [],
        "files_analyzed": []
    }

    # Files to analyze
    files_to_check = [
        "style.css",
        "header.php",
        "footer.php",
        "index.php",
        "functions.php",
        "front-page.php"
    ]

    for filename in files_to_check:
        filepath = theme_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            brand_data["files_analyzed"].append(filename)

            # Extract colors
            if filename.endswith('.css'):
                colors = extract_colors_from_css(content)
            else:
                colors = extract_colors_from_php(content)
            brand_data["colors"].update(colors)

            # Extract fonts
            fonts = extract_fonts(content)
            for font in fonts:
                if font not in brand_data["fonts"]:
                    brand_data["fonts"].append(font)

    # Check style.css for theme metadata
    style_path = theme_dir / "style.css"
    if style_path.exists():
        style_content = style_path.read_text(encoding='utf-8', errors='ignore')

        # Theme name
        theme_name = re.search(r'Theme Name:\s*(.+)', style_content)
        if theme_name:
            brand_data["theme_name"] = theme_name.group(1).strip()

        # Description
        description = re.search(r'Description:\s*(.+)', style_content)
        if description:
            brand_data["description"] = description.group(1).strip()

    return brand_data

def hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB string"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgb({r}, {g}, {b})"

def main():
    parser = argparse.ArgumentParser(description='Extract brand data from WordPress theme')
    parser.add_argument('--theme-path', required=True, help='Path to WordPress theme directory')
    parser.add_argument('--output', help='Output file (JSON)', default=None)
    parser.add_argument('--format', choices=['json', 'yaml', 'markdown'], default='json')

    args = parser.parse_args()

    brand_data = analyze_theme(args.theme_path)

    # Add RGB values
    for name, color in brand_data.get("colors", {}).items():
        if "hex" in color:
            color["rgb"] = hex_to_rgb(color["hex"])

    if args.format == 'json':
        output = json.dumps(brand_data, indent=2)
    elif args.format == 'markdown':
        output = f"# Brand Data\n\n"
        output += f"**Theme:** {brand_data.get('theme_name', 'Unknown')}\n\n"
        output += "## Colors\n\n"
        output += "| Name | Hex | RGB |\n|------|-----|-----|\n"
        for name, color in brand_data.get("colors", {}).items():
            output += f"| {name} | {color.get('hex', '')} | {color.get('rgb', '')} |\n"
        output += "\n## Fonts\n\n"
        for font in brand_data.get("fonts", []):
            output += f"- {font}\n"
    else:
        output = json.dumps(brand_data, indent=2)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Saved to {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
