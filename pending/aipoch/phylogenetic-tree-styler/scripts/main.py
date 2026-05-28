#!/usr/bin/env python3
"""Phylogenetic Tree Styler
Beautify the evolutionary tree, add species classification color blocks, Bootstrap values and timeline"""

import argparse
import sys
from pathlib import Path

try:
    from ete3 import Tree, TreeStyle, NodeStyle, TextFace, RectFace, CircleFace
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"mistake: Missing dependencies - {e}")
    print("Please install dependencies: pip install ete3 matplotlib numpy pandas")
    sys.exit(1)


# Predefined color schemes
TAXONOMY_COLORS = {
    'domain': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'],
    'phylum': ['#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d3', '#c7c7c7'],
    'class': ['#9edae5', '#dbdb8d', '#bcbd22', '#17becf', '#e6550d', '#fd8d3c', '#31a354', '#74c476'],
}


def parse_args():
    """Parse command line parameters"""
    parser = argparse.ArgumentParser(
        description='Phylogenetic Tree Styler - Beautify evolutionary tree visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  %(prog)s -i tree.nwk -o output.png
  %(prog)s -i tree.nwk --show-bootstrap --taxonomy-file taxo.csv
  %(prog)s -i tree.nwk --show-timeline --root-age 500"""
    )
    
    parser.add_argument('-i', '--input', required=True, help='Input Newick format evolutionary tree file')
    parser.add_argument('-o', '--output', default='tree_styled.png', help='Output image file path')
    parser.add_argument('-f', '--format', choices=['png', 'pdf', 'svg'], default='png', help='Output format')
    parser.add_argument('--width', type=int, default=1200, help='Image width (pixels)')
    parser.add_argument('--height', type=int, default=800, help='Image height (pixels)')
    parser.add_argument('--show-bootstrap', action='store_true', help='Show Bootstrap values')
    parser.add_argument('--bootstrap-threshold', type=float, default=50, help='Only show Bootstrap values ​​above this threshold')
    parser.add_argument('--taxonomy-file', help='Species classification information file (CSV format)')
    parser.add_argument('--show-timeline', action='store_true', help='Show timeline')
    parser.add_argument('--root-age', type=float, help='Root node age (millions of years ago)')
    parser.add_argument('--branch-color', default='black', help='branch color')
    parser.add_argument('--leaf-color', default='black', help='Leaf node label color')
    parser.add_argument('--dpi', type=int, default=150, help='Output DPI')
    
    return parser.parse_args()


def load_tree(tree_file):
    """Load evolutionary tree file"""
    try:
        tree = Tree(tree_file, format=1)
        return tree
    except Exception as e:
        print(f"mistake: Unable to parse evolutionary tree file - {e}")
        sys.exit(1)


def load_taxonomy(taxonomy_file):
    """Load classification information file"""
    if not taxonomy_file:
        return None
    
    try:
        df = pd.read_csv(taxonomy_file)
        required_cols = ['name']
        if not all(col in df.columns for col in required_cols):
            print(f"mistake: Classification files must contain 'name' List")
            return None
        
        # Create a mapping of species to taxonomic information
        taxonomy_map = {}
        for _, row in df.iterrows():
            taxonomy_map[row['name']] = row.to_dict()
        
        return taxonomy_map
    except Exception as e:
        print(f"warn: Unable to load category file - {e}")
        return None


def assign_taxonomy_colors(taxonomy_map, level='domain'):
    """Assign colors to classification levels"""
    if not taxonomy_map:
        return {}
    
    # Collect all unique categorical values
    values = set()
    for taxo in taxonomy_map.values():
        if level in taxo and pd.notna(taxo[level]):
            values.add(taxo[level])
    
    values = sorted(list(values))
    colors = TAXONOMY_COLORS.get(level, TAXONOMY_COLORS['domain'])
    
    color_map = {}
    for i, value in enumerate(values):
        color_map[value] = colors[i % len(colors)]
    
    return color_map


def style_tree(tree, args, taxonomy_map=None):
    """Set the style of the tree"""
    # Create a tree style
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.mode = 'r'  # Radial mode, can be changed to 'c' for circular mode
    ts.optimal_scale_level = 'full'
    ts.scale = 200
    
    # If there is a timeline, adjust the layout
    if args.show_timeline:
        ts.mode = 'r'
        ts.show_scale = True
        ts.scale_length = 0.1
    
    # Assign colors to classification levels
    domain_colors = {}
    phylum_colors = {}
    if taxonomy_map:
        domain_colors = assign_taxonomy_colors(taxonomy_map, 'domain')
        phylum_colors = assign_taxonomy_colors(taxonomy_map, 'phylum')
    
    # Set styles for each node
    for node in tree.traverse():
        nstyle = NodeStyle()
        nstyle['size'] = 0
        nstyle['fgcolor'] = args.branch_color
        nstyle['hz_line_color'] = args.branch_color
        nstyle['vt_line_color'] = args.branch_color
        nstyle['hz_line_width'] = 2
        nstyle['vt_line_width'] = 2
        
        # Leaf node style
        if node.is_leaf():
            nstyle['size'] = 8
            nstyle['fgcolor'] = args.leaf_color
            
            # Add classified color blocks
            if taxonomy_map and node.name in taxonomy_map:
                taxo = taxonomy_map[node.name]
                
                # Add domain color block
                if 'domain' in taxo and pd.notna(taxo['domain']):
                    domain = taxo['domain']
                    color = domain_colors.get(domain, '#999999')
                    domain_face = RectFace(15, 15, color, color)
                    domain_face.margin_right = 5
                    node.add_face(domain_face, column=0, position='aligned')
                    
                    # Add domain tag
                    domain_text = TextFace(f" {domain}", fsize=10, fgcolor=color)
                    node.add_face(domain_text, column=1, position='aligned')
                
                # Add phylum color block
                if 'phylum' in taxo and pd.notna(taxo['phylum']):
                    phylum = taxo['phylum']
                    color = phylum_colors.get(phylum, '#cccccc')
                    phylum_face = RectFace(15, 15, color, color)
                    phylum_face.margin_right = 5
                    node.add_face(phylum_face, column=2, position='aligned')
                    
                    # Add phylum tag
                    phylum_text = TextFace(f" {phylum}", fsize=10, fgcolor='#666666')
                    node.add_face(phylum_text, column=3, position='aligned')
        
        # Internal Node - Display Bootstrap Value
        else:
            # Try to get bootstrap value
            bootstrap = None
            
            # Parsed from node name (common format: (A,B)95:0.1)
            if node.name and node.name.replace('.', '').replace('-', '').isdigit():
                try:
                    bootstrap = float(node.name)
                except:
                    pass
            
            # Get from support attribute
            if bootstrap is None and hasattr(node, 'support') and node.support is not None:
                try:
                    bootstrap = float(node.support)
                except:
                    pass
            
            # Show Bootstrap values
            if args.show_bootstrap and bootstrap is not None and bootstrap >= args.bootstrap_threshold:
                # Set color intensity based on bootstrap value
                intensity = min(1.0, bootstrap / 100)
                if bootstrap >= 90:
                    color = '#2166ac'  # Dark blue - high confidence
                elif bootstrap >= 70:
                    color = '#4393c3'  # medium blue
                else:
                    color = '#92c5de'  # light blue
                
                bootstrap_face = TextFace(f"{int(bootstrap)}", fsize=9, fgcolor=color, bold=True)
                node.add_face(bootstrap_face, column=0, position='branch-top')
                
                # Node size reflects bootstrap value
                nstyle['size'] = 4 + (bootstrap / 100) * 6
                nstyle['fgcolor'] = color
        
        node.set_style(nstyle)
    
    return ts


def add_timeline(tree, ts, root_age):
    """Add timeline"""
    if not root_age:
        return
    
    # Calculate tree height
    tree_height = tree.get_farthest_leaf()[1]
    
    # Add time scale
    ts.show_scale = True
    ts.scale_length = tree_height / 5
    
    # Add title description
    ts.title.add_face(TextFace(f"Time Scale: {root_age} Mya", fsize=12, bold=True), column=0)


def render_tree(tree, ts, output_file, args):
    """Render tree to image file"""
    try:
        # Set image size
        tree.render(output_file, tree_style=ts, w=args.width, h=args.height, dpi=args.dpi)
        print(f"success: Image saved to {output_file}")
        return True
    except Exception as e:
        print(f"mistake: Rendering failed - {e}")
        return False


def main():
    args = parse_args()
    
    # Check input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"mistake: Input file does not exist: {args.input}")
        sys.exit(1)
    
    # Load evolutionary tree
    print(f"Loading evolutionary tree: {args.input}")
    tree = load_tree(args.input)
    print(f"tree information: {len(tree)} leaf nodes")
    
    # Load classification information
    taxonomy_map = None
    if args.taxonomy_file:
        print(f"Loading category information: {args.taxonomy_file}")
        taxonomy_map = load_taxonomy(args.taxonomy_file)
        if taxonomy_map:
            print(f"Loaded {len(taxonomy_map)} taxonomic information for each species")
    
    # Set tree style
    print("Setting style...")
    ts = style_tree(tree, args, taxonomy_map)
    
    # Add timeline
    if args.show_timeline:
        print("Adding timeline...")
        add_timeline(tree, ts, args.root_age)
    
    # Set output path
    output_path = Path(args.output)
    if output_path.suffix != f'.{args.format}':
        output_path = output_path.with_suffix(f'.{args.format}')
    
    # render image
    print(f"Rendering image...")
    if render_tree(tree, ts, str(output_path), args):
        print(f"Finish! output file: {output_path}")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
