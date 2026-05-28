# -*- coding: utf-8 -*-
"""PPTX Converter Entry Point

Converts HTML presentation to PowerPoint format with animations.

Usage:
    python convert_to_pptx.py # Use default data file
    python convert_to_pptx.py projects/helixlife-20260130.js #Specify the project file path
    python convert_to_pptx.py helixlife-20260130 # Abbreviation (automatically found under projects/)
    python convert_to_pptx.py helixlife-20260130 -o my-ppt # Specify the output name"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Configure stdout encoding for Chinese characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add current directory to path for imports
SCRIPT_DIR = Path(__file__).parent
FRAMEWORK_DIR = SCRIPT_DIR / 'framework'
PROJECTS_DIR = SCRIPT_DIR / 'projects'
sys.path.insert(0, str(FRAMEWORK_DIR))


def resolve_data_file(data_arg: str) -> Path:
    """Parse the data file path and support multiple input methods:
    - Full path: projects/helixlife-20260130.js
    - Project name: helixlife-20260130 (automatically search under projects/)
    - Use default when no parameters: framework/content/slides-data.js"""
    if not data_arg:
        return FRAMEWORK_DIR / 'content' / 'slides-data.js'
    
    data_path = Path(data_arg)
    
    # If it is an absolute path, use it directly
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


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert HTML presentation to PowerPoint',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python convert_to_pptx.py # Use default data file
  python convert_to_pptx.py projects/helixlife-20260130.js #Specify the project file path
  python convert_to_pptx.py helixlife-20260130 # Abbreviation (automatically found under projects/)
  python convert_to_pptx.py helixlife-20260130 -o my-ppt # Specify the output name"""
    )
    parser.add_argument(
        'data',
        nargs='?',
        default=None,
        help='Data file path or project name (default: framework/content/slides-data.js)'
    )
    parser.add_argument(
        '--html', '-H',
        default='framework/index.html',
        help='Path to index.html (default: framework/index.html)'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output PPTX filename (default: automatically inferred from data file name)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    html_path = SCRIPT_DIR / args.html
    data_path = resolve_data_file(args.data)
    
    # Create output directory
    output_dir = SCRIPT_DIR / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # Generate output filename
    if args.output:
        output_filename = args.output
        if not output_filename.endswith('.pptx'):
            output_filename += '.pptx'
    else:
        # Infer output file name from data file name
        output_filename = f'{data_path.stem}.pptx'
    
    output_path = output_dir / output_filename
    
    # Validate inputs
    if not html_path.exists():
        print(f"Error: HTML file not found: {html_path}")
        sys.exit(1)
    
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}")
        sys.exit(1)
    
    # Import and run converter
    try:
        from converter.renderer import create_presentation
        
        print("=" * 50)
        print("PPTX Converter")
        print("=" * 50)
        print(f"HTML Source: {html_path}")
        print(f"Data Source: {data_path}")
        print(f"Output: {output_path}")
        print("=" * 50)
        
        create_presentation(
            str(html_path),
            str(data_path),
            str(output_path)
        )
        
        print("=" * 50)
        print("Conversion complete!")
        print(f"Open {output_path} in PowerPoint to view the result.")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nPlease install dependencies:")
        print("  pip install python-pptx lxml")
        sys.exit(1)
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
