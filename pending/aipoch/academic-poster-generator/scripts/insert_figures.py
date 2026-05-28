#!/usr/bin/env python3
"""
Figure Inserter
Automatically inserts figures into LaTeX poster templates.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional


class FigureInserter:
    """Insert figures into LaTeX documents."""
    
    def __init__(self, tex_file: str):
        self.tex_file = Path(tex_file)
        self.tex_content = ""
        self._read_tex_file()
    
    def _read_tex_file(self):
        """Read LaTeX file content."""
        if not self.tex_file.exists():
            raise FileNotFoundError(f"LaTeX file not found: {self.tex_file}")
        
        with open(self.tex_file, 'r', encoding='utf-8') as f:
            self.tex_content = f.read()
    
    def detect_package(self) -> str:
        """Detect which LaTeX package is being used."""
        if re.search(r'\\usepackage(\[[^\]]*\])?\{beamerposter\}', self.tex_content):
            return 'beamerposter'
        if re.search(r'\\documentclass(\[[^\]]*\])?\{tikzposter\}', self.tex_content):
            return 'tikzposter'
        if re.search(r'\\documentclass(\[[^\]]*\])?\{baposter\}', self.tex_content):
            return 'baposter'
        return 'beamerposter'
    
    def find_figure_placeholders(self) -> List[Dict]:
        """Find figure placeholders in LaTeX document."""
        placeholders = []
        
        # Pattern for figure placeholders
        # Format: <!-- FIGURE: description, position -->
        pattern = r'%\s*FIGURE:\s*([^,]+),\s*([^%\n]+)'
        
        for match in re.finditer(pattern, self.tex_content):
            placeholders.append({
                'description': match.group(1).strip(),
                'position': match.group(2).strip(),
                'start': match.start(),
                'end': match.end()
            })
        
        return placeholders
    
    def create_figure_code(self, package: str, figure_path: str, 
                          caption: str, label: Optional[str] = None) -> str:
        """
        Create LaTeX code for figure insertion based on package.
        
        Args:
            package: LaTeX package type (beamerposter/tikzposter/baposter)
            figure_path: Path to figure file
            caption: Figure caption
            label: Optional label for referencing
        """
        figure_path_obj = Path(figure_path)
        
        # Determine the correct path to use in LaTeX
        if figure_path_obj.is_absolute():
            # If absolute path, compute relative path from .tex file's directory
            try:
                filename = str(figure_path_obj.relative_to(self.tex_file.parent))
            except ValueError:
                # If can't compute relative path, use the file name only
                filename = figure_path_obj.name
        else:
            # If relative path, try to resolve it and compute relative path to .tex file
            try:
                # Resolve the relative path to get the absolute path
                absolute_path = figure_path_obj.resolve()
                # Compute relative path from .tex file's directory
                filename = str(absolute_path.relative_to(self.tex_file.parent.resolve()))
            except (ValueError, RuntimeError):
                # If can't compute relative path, use the path as-is or file name
                # Check if the file exists relative to .tex file
                tex_dir = self.tex_file.parent
                if (tex_dir / figure_path_obj).exists():
                    filename = str(figure_path_obj)
                else:
                    # Fallback to file name
                    filename = figure_path_obj.name
        
        # Convert backslashes to forward slashes for LaTeX compatibility
        filename = filename.replace('\\', '/')
        
        if package == 'beamerposter':
            code = f"""\\begin{{figure}}
  \\centering
  \\includegraphics[width=0.9\\linewidth]{{{filename}}}
  \\caption{{{caption}}}
  {f"\\label{{fig:{label}}}" if label else ""}
\\end{{figure}}"""
        
        elif package == 'tikzposter':
            code = f"""\\begin{{tikzfigure}}
  \\includegraphics[width=\\linewidth]{{{filename}}}
  \\caption{{{caption}}}
\\end{{tikzfigure}}"""
        
        elif package == 'baposter':
            code = f"""\\headerbox{{{caption}}}{{name=figure_{label},column=0,row=0}}{{
  \\begin{{center}}
    \\includegraphics[width=0.9\\linewidth]{{{filename}}}
  \\end{{center}}
}}"""
        
        else:
            code = f"""\\begin{{figure}}
  \\centering
  \\includegraphics[width=0.8\\linewidth]{{{filename}}}
  \\caption{{{caption}}}
\\end{{figure}}"""
        
        return code
    
    def insert_figure(self, figure_path: str, caption: str, 
                   position: str, label: Optional[str] = None) -> bool:
        """
        Insert a single figure at specified position.
        
        Args:
            figure_path: Path to figure file
            caption: Figure caption
            position: Position marker or placeholder description
            label: Optional label for referencing
        """
        package = self.detect_package()
        figure_code = self.create_figure_code(package, figure_path, caption, label)
        position_value = (position or "").strip()
        if not position_value:
            position_value = "end"
        position_lower = position_value.lower()
        
        # Try to find position by description
        if position_lower not in ("end", "append"):
            placeholders = self.find_figure_placeholders()
            
            for placeholder in placeholders:
                if position_lower in placeholder['description'].lower():
                    # Replace placeholder with figure code
                    self.tex_content = (
                        self.tex_content[:placeholder['start']] +
                        figure_code +
                        self.tex_content[placeholder['end']:]
                    )
                    print(f"[*] Inserted figure at position: {placeholder['description']}")
                    return True
        
        # If no placeholder found, insert at specific line
        if position_value.isdigit():
            lines = self.tex_content.split('\n')
            insert_line = int(position_value)
            if 0 < insert_line <= len(lines):
                lines.insert(insert_line - 1, figure_code)
                self.tex_content = '\n'.join(lines)
                print(f"[*] Inserted figure at line {insert_line}")
                return True

        # Fallback: insert before \end{document}
        end_marker = "\\end{document}"
        end_index = self.tex_content.rfind(end_marker)
        if end_index != -1:
            self.tex_content = (
                self.tex_content[:end_index]
                + figure_code
                + "\n"
                + self.tex_content[end_index:]
            )
        else:
            self.tex_content = self.tex_content + "\n" + figure_code + "\n"
        print("[*] Inserted figure at document end")
        return True
    
    def insert_figures_from_config(self, config_file: str) -> bool:
        """
        Insert multiple figures from a configuration file.
        
        Config format:
        {
            "figures": [
                {
                    "path": "figures/schematic.png",
                    "caption": "Mechanism diagram",
                    "position": "results",
                    "label": "mech1"
                }
            ]
        }
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Inserting {len(config['figures'])} figures from config")
        
        success_count = 0
        for figure in config['figures']:
            try:
                if self.insert_figure(
                    figure.get('path', ''),
                    figure.get('caption', ''),
                    figure.get('position', ''),
                    figure.get('label')
                ):
                    success_count += 1
            except Exception as e:
                print(f"Error inserting figure: {e}")
        
        print(f"[*] Inserted {success_count}/{len(config['figures'])} figures")
        return success_count > 0
    
    def insert_all_figures(self, figures_dir: str = "figures") -> bool:
        """
        Insert all figures from a directory.
        Figures are inserted in alphabetical order.
        """
        figures_path = Path(figures_dir)
        if not figures_path.exists():
            print(f"Warning: Figures directory not found: {figures_dir}")
            return False
        
        # Get all image files
        image_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.svg']
        figure_files = sorted([
            f for f in figures_path.iterdir()
            if f.suffix.lower() in image_extensions
        ])
        
        if not figure_files:
            print(f"No image files found in {figures_dir}")
            return False
        
        print(f"Found {len(figure_files)} figure(s) in {figures_dir}")
        
        # Insert figures at placeholders
        placeholders = self.find_figure_placeholders()
        
        if not placeholders:
            print("Warning: No figure placeholders found in LaTeX file")
            print("Inserting at document end...")
        
        success_count = 0
        for i, figure_file in enumerate(figure_files):
            caption = f"Figure {i+1}: {figure_file.stem}"
            label = f"fig{figure_file.stem}"
            
            # Try to find matching placeholder
            position = placeholders[i]['description'] if i < len(placeholders) else "end"
            
            if self.insert_figure(str(figure_file), caption, position, label):
                success_count += 1
        
        print(f"[*] Inserted {success_count}/{len(figure_files)} figures")
        return success_count > 0
    
    def save(self, output_file: Optional[str] = None):
        """Save modified LaTeX content."""
        if output_file is None:
            output_file = str(self.tex_file)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.tex_content)
        
        print(f"[*] Saved modified LaTeX to: {output_file}")


def create_config_example():
    """Create example configuration file."""
    config = {
        "figures": [
            {
                "path": "figures/mechanism.png",
                "caption": "Proposed mechanism of action",
                "position": "introduction",
                "label": "mechanism"
            },
            {
                "path": "figures/methodology.png",
                "caption": "Experimental design and methodology",
                "position": "methods",
                "label": "methods"
            },
            {
                "path": "figures/results.png",
                "caption": "Main experimental results",
                "position": "results",
                "label": "results1"
            },
            {
                "path": "figures/comparison.png",
                "caption": "Comparison with existing methods",
                "position": "results",
                "label": "results2"
            }
        ]
    }
    
    with open('figures_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("[*] Created example config file: figures_config.json")


def add_placeholders_to_template(tex_file: str):
    """
    Add figure placeholders to a LaTeX template.
    Finds section headers and adds placeholders after them.
    """
    tex_path = Path(tex_file)
    
    if not tex_path.exists():
        print(f"Error: File not found: {tex_file}")
        return False
    
    with open(tex_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find common section patterns and add placeholders
    sections = [
        'Introduction',
        'Methods',
        'Results',
        'Discussion',
        'Conclusion'
    ]
    
    modified = False
    for section in sections:
        placeholder = f"% FIGURE: {section.lower()}, {section.lower()}"
        if placeholder in content:
            continue
        # Pattern for section headers
        patterns = [
            rf'\\section\*?{{{section}}}',
            rf'\\begin{{block}}{{{section}}}',
            rf'\\block{{{section}}}',
            rf'% {section}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                insert_pos = match.end()
                content = (
                    content[:insert_pos]
                    + "\n"
                    + placeholder
                    + "\n"
                    + content[insert_pos:]
                )
                modified = True
                print(f"[*] Added placeholder for section: {section}")
                break
    
    if modified:
        # Save with new filename
        output_file = tex_path.parent / f"{tex_path.stem}_with_placeholders.tex"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[*] Saved template with placeholders: {output_file}")
        return True
    else:
        print("Warning: Could not find section headers to add placeholders")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Insert figures into LaTeX poster templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Insert all figures from figures/ directory
  python scripts/insert_figures.py poster.tex --all
  
  # Insert figures from config file
  python scripts/insert_figures.py poster.tex --config figures_config.json
  
  # Insert single figure at specific position
  python scripts/insert_figures.py poster.tex --figure figures/mech.png --caption "Mechanism" --position introduction
  
  # Add figure placeholders to template
  python scripts/insert_figures.py template.tex --add-placeholders
  
  # Create example config file
  python scripts/insert_figures.py --create-config
        """
    )
    
    parser.add_argument(
        "tex_file",
        nargs='?',
        help="LaTeX template file"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Insert all figures from figures/ directory"
    )
    
    parser.add_argument(
        "--config",
        help="Configuration JSON file"
    )
    
    parser.add_argument(
        "--figure",
        help="Single figure file path"
    )
    
    parser.add_argument(
        "--caption",
        help="Figure caption"
    )
    
    parser.add_argument(
        "--position",
        help="Position (placeholder name or line number)"
    )
    
    parser.add_argument(
        "--label",
        help="Figure label for referencing"
    )
    
    parser.add_argument(
        "--output",
        help="Output file (default: overwrite input)"
    )
    
    parser.add_argument(
        "--add-placeholders",
        action="store_true",
        help="Add figure placeholders to template"
    )
    
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create example configuration file"
    )
    
    args = parser.parse_args()
    
    # Create config example
    if args.create_config:
        create_config_example()
        sys.exit(0)
    
    # Add placeholders to template
    if args.add_placeholders:
        if not args.tex_file:
            print("Error: LaTeX file required")
            sys.exit(1)
        success = add_placeholders_to_template(args.tex_file)
        sys.exit(0 if success else 1)
    
    # Validate input file
    if not args.tex_file:
        print("Error: LaTeX file required")
        sys.exit(1)
    
    inserter = FigureInserter(args.tex_file)
    
    try:
        if args.all:
            inserter.insert_all_figures()
        elif args.config:
            inserter.insert_figures_from_config(args.config)
        elif args.figure:
            if not args.caption:
                print("Error: Caption required for single figure")
                sys.exit(1)
            inserter.insert_figure(
                args.figure,
                args.caption,
                args.position or "end",
                args.label
            )
        else:
            print("Error: Please specify --all, --config, or --figure")
            sys.exit(1)
        
        # Save modified file
        inserter.save(args.output)
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
