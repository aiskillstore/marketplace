# -*- coding: utf-8 -*-
"""Static HTML Builder

Based on the modular code in the ppt/ directory, build a static demonstration file that can be run independently.

Generate results:
  - presentation.html: HTML file with all frame code inline
  - slides-data.js: independent slide data file (optional)

Usage:
    python build_html.py #Default build
    python build_html.py projects/helixlife-20260130.js #Specify project file
    python build_html.py helixlife-20260130 # Abbreviation (automatically search projects/)
    python build_html.py helixlife-20260130 -o my-ppt # Specify the output name
    python build_html.py --separate-data # Data is independent as slides-data.js
    python build_html.py --minify # Compress output"""

import sys
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
FRAMEWORK_DIR = SCRIPT_DIR / 'framework'
PROJECTS_DIR = SCRIPT_DIR / 'projects'


def resolve_data_file(data_arg: str) -> Path:
    """Parse the data file path and support multiple input methods:
    - Full path: projects/helixlife-20260130.js
    - Project name: helixlife-20260130 (automatically search under projects/)
    - Use default when no parameters: framework/content/slides-data.js"""
    if not data_arg:
        return FRAMEWORK_DIR / 'content' / 'slides-data.js'
    
    data_path = Path(data_arg)
    
    # If the absolute path or relative path exists, use it directly
    if data_path.is_absolute():
        return data_path
    
    # Path relative to script directory
    full_path = SCRIPT_DIR / data_path
    if full_path.exists():
        return full_path
    
    # Try looking under projects/ as project name
    project_name = data_arg
    if not project_name.endswith('.js'):
        project_name += '.js'
    
    project_path = PROJECTS_DIR / project_name
    if project_path.exists():
        return project_path
    
    # If none are found, return to the original path (an error will be reported later)
    return full_path


def read_file(path: Path) -> str:
    """Read file contents"""
    if not path.exists():
        print(f"Warning: File not found: {path}")
        return ""
    return path.read_text(encoding='utf-8')


def inline_css(html: str, base_dir: Path) -> str:
    """Replace <link rel="stylesheet"> with inline <style>"""
    
    def replace_link(match):
        href = match.group(1)
        # Skip external CDN links
        if href.startswith('http://') or href.startswith('https://'):
            return match.group(0)
        
        css_path = base_dir / href
        css_content = read_file(css_path)
        if css_content:
            print(f"  Inlining CSS: {href}")
            return f'<style>\n/* {href} */\n{css_content}\n</style>'
        return match.group(0)
    
    # Matches <link rel="stylesheet" href="...">
    pattern = r'<link\s+rel=["\']stylesheet["\']\s+href=["\']([^"\']+)["\']>'
    html = re.sub(pattern, replace_link, html)
    
    # Also handles the case where href comes first
    pattern2 = r'<link\s+href=["\']([^"\']+)["\']\s+rel=["\']stylesheet["\']>'
    html = re.sub(pattern2, replace_link, html)
    
    return html


def inline_js_framework(html: str, base_dir: Path, exclude_data: bool = False, custom_data_path: Path = None) -> str:
    """Inline frame JS file, optionally excluding slides-data.js
    
    Args:
        html: HTML content
        base_dir: base directory
        exclude_data: whether to exclude slides-data.js (keep external references)
        custom_data_path: Custom data file path (replaces the default slides-data.js)"""
    # Collect all JS content that needs to be inlined
    js_contents = []
    scripts_to_remove = []
    data_script_tag = None
    
    # Matches <script src="..."></script>
    pattern = r'<script\s+src=["\']([^"\']+)["\']>\s*</script>'
    
    for match in re.finditer(pattern, html):
        src = match.group(1)
        # Skip external CDN links
        if src.startswith('http://') or src.startswith('https://'):
            continue
        
        # Check if it is slides-data.js
        is_data_file = 'slides-data.js' in src
        
        if is_data_file and exclude_data:
            # Keep the reference to the data file, but change the path to a relative path
            data_script_tag = match.group(0)
            continue
        
        # If there is a custom data file, use a custom path
        if is_data_file and custom_data_path:
            js_path = custom_data_path
            print(f"  Inlining JS: {custom_data_path.name} (from {custom_data_path.parent})")
        else:
            js_path = base_dir / src
            
        js_content = read_file(js_path)
        if js_content:
            if not (is_data_file and custom_data_path):
                print(f"  Inlining JS: {src}")
            js_contents.append(f'// ========== {src} ==========\n{js_content}')
            scripts_to_remove.append(match.group(0))
    
    # Remove all script tags that need to be inline
    for script_tag in scripts_to_remove:
        html = html.replace(script_tag, '', 1)
    
    # If excluding data, replace data script path
    if exclude_data and data_script_tag:
        html = html.replace(data_script_tag, '<script src="slides-data.js"></script>')
    
    # Extract initialization script content
    init_script_pattern = '<!-- ========== initialization ========== -->\\s*<script>(.*?)</script>'
    init_match = re.search(init_script_pattern, html, re.DOTALL)
    init_script_content = ''
    if init_match:
        init_script_content = init_match.group(1).strip()
        # Remove original initialization script
        html = re.sub(init_script_pattern, '', html, flags=re.DOTALL)
    
    # Combine all JS into one script tag
    if js_contents:
        combined_js = '\n\n'.join(js_contents)
        
        # Add initialization code
        if init_script_content:
            combined_js += f'\n\n// ========== initialization ==========\n{init_script_content}'
        
        # Clean empty comment lines in HTML
        html = re.sub('\\n\\s*<!-- ========== core framework ========== -->\\s*\\n\\s*\\n', '\n', html)
        html = re.sub('\\n\\s*<!-- ========== animation presets ========== -->\\s*\\n\\s*\\n', '\n', html)
        html = re.sub('\\n\\s*<!-- ========== components ========== -->\\s*\\n\\s*\\n', '\n', html)
        html = re.sub('\\n\\s*<!-- ========== User Content ========== -->\\s*\\n', '\n', html)
        html = re.sub(r'\n\s*\n\s*\n+', '\n\n', html)  # Multiple blank lines become two
        
        # Determine insertion position
        if exclude_data:
            # Data independence: Insert framework code before slides-data.js reference
            html = html.replace(
                '<script src="slides-data.js"></script>',
                f'<script>\n{combined_js}\n    </script>\n    <script src="slides-data.js"></script>'
            )
        else:
            # Data inlining: Insert merged script before </body>
            html = html.replace(
                '</body>',
                f'    <script>\n{combined_js}\n    </script>\n</body>'
            )
    
    return html


def remove_comments(html: str) -> str:
    """Remove HTML comments (optional, keep file simple)"""
    # Keep conditional comments
    pattern = r'<!--(?!\[if)(?!\[endif).*?-->'
    return re.sub(pattern, '', html, flags=re.DOTALL)


def minify_whitespace(html: str) -> str:
    """Compress extra whitespace (optional)"""
    # Change multiple blank lines into one
    html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)
    return html


def build_static_html(
    output_name: str = None, 
    minify: bool = False, 
    separate_data: bool = False,
    data_file: str = None
) -> Path:
    """Build static HTML files based on ppt/ directory
    
    Args:
        output_name: output file name (without path and extension)
        minify: whether to compress the output
        separate_data: whether to output slides-data.js independently
        data_file: Custom data file path (such as projects/helixlife-20260130.js)
    
    Returns:
        Output HTML file path"""
    print("=" * 50)
    print("Static HTML Builder")
    print("=" * 50)
    
    # Parse data file path
    data_path = resolve_data_file(data_file)
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}")
        sys.exit(1)
    
    # Use framework/ subdirectory as source
    source_path = FRAMEWORK_DIR / 'index.html'
    base_dir = FRAMEWORK_DIR
    
    # Determine whether to use a custom data file
    default_data_path = FRAMEWORK_DIR / 'content' / 'slides-data.js'
    use_custom_data = data_path != default_data_path
    
    mode_desc = "Data independence" if separate_data else "Data inlining"
    print(f"Mode: {mode_desc}")
    print(f"Data: {data_path}")
    
    html = read_file(source_path)
    
    if not html:
        print(f"Error: Cannot read {source_path}")
        sys.exit(1)
    
    print(f"Source: {source_path}")
    print()
    print("Processing...")
    
    # Inline CSS
    html = inline_css(html, base_dir)
    
    # Inline JS (optionally excludes data files)
    custom_data = data_path if use_custom_data else None
    html = inline_js_framework(html, base_dir, exclude_data=separate_data, custom_data_path=custom_data)
    
    # Optional: compression
    if minify:
        print("  Minifying...")
        html = remove_comments(html)
        html = minify_whitespace(html)
    
    # Add build information annotation
    build_info = f"""
<!--
  Static HTML Presentation
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Source: ppt/ (Modular version)
  Data: {'external slides-data.js' if separate_data else 'inline'}
-->
"""
    html = html.replace('<!DOCTYPE html>', '<!DOCTYPE html>' + build_info)
    
    # Determine output path
    output_dir = SCRIPT_DIR / 'output'
    output_dir.mkdir(exist_ok=True)
    
    if not output_name:
        output_name = 'presentation'
    
    html_output_path = output_dir / f'{output_name}.html'
    
    # Write HTML file
    html_output_path.write_text(html, encoding='utf-8')
    
    # If the data is independent, copy the data file
    if separate_data:
        data_output = output_dir / 'slides-data.js'
        data_content = read_file(data_path)
        if data_content:
            data_output.write_text(data_content, encoding='utf-8')
            print(f"  Copied: {data_path.name} -> slides-data.js")
    
    # statistics
    file_size = html_output_path.stat().st_size
    size_kb = file_size / 1024
    
    print()
    print("=" * 50)
    print(f"Output: {html_output_path}")
    if separate_data:
        print(f"        {output_dir / 'slides-data.js'}")
    print(f"Size: {size_kb:.1f} KB")
    print("=" * 50)
    print()
    
    if separate_data:
        print("Done! Edit slides-data.js to modify content, then open HTML file in browser.")
    else:
        print("Done! Open HTML file in browser to start presentation.")
    
    return html_output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Build static HTML presentation files based on ppt/ directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python build_html.py # Use default data file
  python build_html.py projects/helixlife-20260130.js #Specify the project file path
  python build_html.py helixlife-20260130 # Abbreviation (automatically found under projects/)
  python build_html.py helixlife-20260130 -o my-ppt # Specify the output name"""
    )
    parser.add_argument(
        'data',
        nargs='?',
        default=None,
        help='Data file path or project name (default: framework/content/slides-data.js)'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output file name without extension (default: automatically inferred from data file name)'
    )
    parser.add_argument(
        '--minify', '-m',
        action='store_true',
        help='Compress output (remove comments, compress whitespace)'
    )
    parser.add_argument(
        '--separate-data', '-s',
        action='store_true',
        help='Output slides-data.js independently (easy to edit)'
    )
    
    args = parser.parse_args()
    
    # If no output name is specified, it is inferred from the data file name
    output_name = args.output
    if not output_name and args.data:
        data_path = resolve_data_file(args.data)
        output_name = data_path.stem  # Remove the .js extension
    
    build_static_html(output_name, args.minify, args.separate_data, args.data)


if __name__ == '__main__':
    main()
