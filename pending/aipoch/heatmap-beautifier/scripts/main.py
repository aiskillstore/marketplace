#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heatmap Beautifier - Gene Expression Heatmap Visualization Tool

A professional beautification tool for gene expression heat maps that automatically adds cluster trees and color annotation strips.
And intelligently optimize label layout to avoid overlap.

Author: Bioinformatics Visualization Team"""

import argparse
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.font_manager import FontProperties

# Set Chinese font support
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


class HeatmapBeautifier:
    """Gene Expression Heatmap Beautifier
    
    Function:
    - Automatically add hierarchical clustering trees
    - Supports multiple sets of color annotation strips
    - Smart label font size optimization
    - Professional scientific research color scheme"""
    
    # Built-in color scheme
    COLOR_PALETTES = {
        "RdBu_r": "Red and blue color matching (classic differential expression)",
        "viridis": "Yellow and purple color matching (continuous data)",
        "RdYlBu_r": "Red, yellow and blue color scheme",
        "coolwarm": "Warm and cold colors",
        "seismic": "Seismic map color matching",
        "bwr": "Blue, white and red color scheme",
        "Spectral_r": "Spectral color matching",
        "BrBG_r": "Brown and green color"
    }
    
    # Default annotation color
    DEFAULT_COLORS = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#e91e63", "#795548", "#607d8b", "#ff5722"
    ]
    
    def __init__(self, style: str = "white"):
        """Initialize HeatmapBeautifier
        
        Args:
            style: seaborn style ("white", "dark", "whitegrid", "darkgrid", "ticks")"""
        sns.set_style(style)
        self.fig = None
        self.ax = None
        
    def load_data(self, data_path: str) -> pd.DataFrame:
        """Load expression matrix data
        
        Args:
            data_path: CSV file path
            
        Returns:
            DataFrame: expression matrix (gene x sample)"""
        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"Data file does not exist: {data_path}")
            
        # Supports multiple delimiters
        try:
            df = pd.read_csv(data_path, index_col=0)
        except:
            try:
                df = pd.read_csv(data_path, index_col=0, sep='\t')
            except:
                df = pd.read_csv(data_path, index_col=0, sep=';')
                
        # Make sure the data is numeric
        df = df.apply(pd.to_numeric, errors='coerce')
        
        print(f"✓ Load data: {df.shape[0]} Gene × {df.shape[1]} sample")
        return df
    
    def calculate_optimal_fontsizes(self, 
                                     n_rows: int, 
                                     n_cols: int, 
                                     figsize: Tuple[int, int],
                                     max_row_fontsize: float = 10,
                                     max_col_fontsize: float = 10) -> Tuple[float, float]:
        """Calculate optimal label font size to avoid overlap
        
        Args:
            n_rows: number of rows
            n_cols: number of columns
            figsize: graphic size
            max_row_fontsize: Maximum row label font size
            max_col_fontsize: Maximum column label font size
            
        Returns:
            (row_fontsize, col_fontsize): optimal font size tuple"""
        # Calculated based on graphic size and number of elements
        fig_width, fig_height = figsize
        
        # Estimate available space (consider space occupied by cluster tree and annotation bars)
        available_width = fig_width * 0.6  # The main heatmap takes up about 60% of the width
        available_height = fig_height * 0.6  # The main heatmap takes up about 60% of the height
        
        # Calculate the average size of each cell in inches
        cell_width = available_width / max(n_cols, 1)
        cell_height = available_height / max(n_rows, 1)
        
        # Convert to font size (approximate conversion: 1 inch ≈ 72 points)
        points_per_inch = 72
        
        # Row labels: calculated based on cell height
        row_fontsize = min(cell_height * points_per_inch * 0.8, max_row_fontsize)
        row_fontsize = max(row_fontsize, 4)  # Minimum font size 4
        
        # Column labels: calculated based on cell width
        col_fontsize = min(cell_width * points_per_inch * 0.8, max_col_fontsize)
        col_fontsize = max(col_fontsize, 4)  # Minimum font size 4
        
        # Further limitations when using large data sets
        if n_rows > 100:
            row_fontsize = min(row_fontsize, 6)
        if n_cols > 50:
            col_fontsize = min(col_fontsize, 6)
            
        return row_fontsize, col_fontsize
    
    def prepare_annotations(self,
                           data: pd.DataFrame,
                           annotations: Optional[Dict[str, Dict[str, str]]],
                           axis: str = "row") -> Optional[pd.DataFrame]:
        """Prepare annotation data
        
        Args:
            data: master data matrix
            annotations: annotation dictionary {annotation name: {entry: value}}
            axis: "row" or "col"
            
        Returns:
            Annotation DataFrame or None"""
        if annotations is None:
            return None
            
        indices = data.index if axis == "row" else data.columns
        annot_data = {}
        
        for annot_name, annot_dict in annotations.items():
            annot_values = [annot_dict.get(str(idx), "Unknown") for idx in indices]
            annot_data[annot_name] = annot_values
            
        return pd.DataFrame(annot_data, index=indices)
    
    def generate_annotation_colors(self,
                                   annotations: pd.DataFrame,
                                   custom_colors: Optional[Dict[str, Dict[str, str]]] = None
                                   ) -> Dict[str, Dict[str, str]]:
        """Generate annotation colormap
        
        Args:
            annotations: annotations DataFrame
            custom_colors: user-defined colors {comment name: {category: color}}
            
        Returns:
            color map dictionary"""
        color_maps = {}
        
        for i, col in enumerate(annotations.columns):
            unique_vals = annotations[col].unique()
            
            # Use custom colors or automatically generate
            if custom_colors and col in custom_colors:
                color_maps[col] = custom_colors[col]
            else:
                colors = self.DEFAULT_COLORS[i % len(self.DEFAULT_COLORS):]
                colors = colors + self.DEFAULT_COLORS[:max(0, len(unique_vals) - len(colors))]
                color_maps[col] = {val: colors[j % len(colors)] 
                                   for j, val in enumerate(unique_vals)}
                
        return color_maps
    
    def create_heatmap(self,
                      data_path: str,
                      output_path: str,
                      title: str = "Gene Expression Heatmap",
                      cmap: str = "RdBu_r",
                      center: Optional[float] = 0,
                      vmin: Optional[float] = None,
                      vmax: Optional[float] = None,
                      row_cluster: bool = True,
                      col_cluster: bool = True,
                      standard_scale: Optional[str] = None,
                      z_score: Optional[int] = None,
                      row_annotations: Optional[Dict[str, Dict[str, str]]] = None,
                      col_annotations: Optional[Dict[str, Dict[str, str]]] = None,
                      annotation_colors: Optional[Dict[str, Dict[str, str]]] = None,
                      max_row_label_fontsize: float = 10,
                      max_col_label_fontsize: float = 10,
                      rotate_col_labels: float = 45,
                      rotate_row_labels: float = 0,
                      hide_row_labels: bool = False,
                      hide_col_labels: bool = False,
                      figsize: Optional[Tuple[int, int]] = None,
                      dpi: int = 300,
                      linewidths: float = 0.5,
                      linecolor: str = "white",
                      cbar_label: str = "Expression",
                      show_plot: bool = False) -> None:
        """Create beautification heatmaps
        
        Args:
            data_path: input data file path
            output_path: output image path
            title: chart title
            cmap: color map name
            center: color center value
            vmin: minimum value
            vmax: maximum value
            row_cluster: whether to perform row clustering
            col_cluster: whether to perform column clustering
            standard_scale: standardization method ("row", "col", None)
            z_score: Z-score normalization (0=row, 1=column, None=no normalization)
            row_annotations: row annotations dictionary
            col_annotations: column annotations dictionary
            annotation_colors: Custom annotation colors
            max_row_label_fontsize: Maximum row label font size
            max_col_label_fontsize: Maximum column label font size
            rotate_col_labels: Column label rotation angle
            rotate_row_labels: row label rotation angle
            hide_row_labels: whether to hide row labels
            hide_col_labels: whether to hide column labels
            figsize: figure size (width, height)
            dpi: output resolution
            linewidths: cell border width
            linecolor: cell border color
            cbar_label: color bar label
            show_plot: whether to display graphics (for debugging)"""
        # Load data
        data = self.load_data(data_path)
        n_rows, n_cols = data.shape
        
        # Automatically determine graphic size
        if figsize is None:
            # Calculate appropriate size based on data volume
            base_width = 10
            base_height = 8
            width_per_col = 0.3
            height_per_row = 0.15
            
            # Consider space for comment strips
            annot_height = 1.5 if col_annotations else 0
            annot_width = 2.0 if row_annotations else 0
            
            fig_width = max(base_width, n_cols * width_per_col + annot_width + 4)
            fig_height = max(base_height, n_rows * height_per_row + annot_height + 3)
            
            # Limit maximum size
            fig_width = min(fig_width, 24)
            fig_height = min(fig_height, 20)
            
            figsize = (fig_width, fig_height)
        
        print(f"✓ Graphic size: {figsize[0]:.1f} × {figsize[1]:.1f} inch")
        
        # Calculate optimal font size
        row_fontsize, col_fontsize = self.calculate_optimal_fontsizes(
            n_rows, n_cols, figsize,
            max_row_label_fontsize, max_col_label_fontsize
        )
        print(f"✓ Font size: Row labels {row_fontsize:.1f}pt, Column labels {col_fontsize:.1f}pt")
        
        # Prepare annotation data
        row_colors = None
        col_colors = None
        
        if row_annotations:
            row_annot_df = self.prepare_annotations(data, row_annotations, axis="row")
            row_color_map = self.generate_annotation_colors(row_annot_df, annotation_colors)
            row_colors = pd.DataFrame({k: v.map(row_color_map[k]) 
                                       for k, v in row_annot_df.items()})
            print(f"✓ Line comments: {list(row_annot_df.columns)}")
            
        if col_annotations:
            col_annot_df = self.prepare_annotations(data, col_annotations, axis="col")
            col_color_map = self.generate_annotation_colors(col_annot_df, annotation_colors)
            col_colors = pd.DataFrame({k: v.map(col_color_map[k]) 
                                       for k, v in col_annot_df.items()})
            print(f"✓ Column comments: {list(col_annot_df.columns)}")
        
        # Create a heat map
        print("✓ Generating heatmap...")
        
        # Adjust layout parameters
        g = sns.clustermap(
            data,
            cmap=cmap,
            center=center,
            vmin=vmin,
            vmax=vmax,
            row_cluster=row_cluster,
            col_cluster=col_cluster,
            standard_scale=standard_scale,
            z_score=z_score,
            row_colors=row_colors,
            col_colors=col_colors,
            figsize=figsize,
            linewidths=linewidths,
            linecolor=linecolor,
            dendrogram_ratio=0.15,
            colors_ratio=0.03,
            cbar_pos=(0.02, 0.8, 0.03, 0.15),
            cbar_kws={"label": cbar_label},
            yticklabels=not hide_row_labels,
            xticklabels=not hide_col_labels
        )
        
        # Set label
        if not hide_row_labels and n_rows <= 200:
            g.ax_heatmap.set_yticklabels(
                g.ax_heatmap.get_ymajorticklabels(),
                fontsize=row_fontsize,
                rotation=rotate_row_labels
            )
        else:
            g.ax_heatmap.set_yticks([])
            
        if not hide_col_labels and n_cols <= 100:
            g.ax_heatmap.set_xticklabels(
                g.ax_heatmap.get_xmajorticklabels(),
                fontsize=col_fontsize,
                rotation=rotate_col_labels,
                ha='right'
            )
        else:
            g.ax_heatmap.set_xticks([])
        
        # Set title
        plt.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
        
        # Adjust layout
        plt.tight_layout()
        
        # save graph
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Support multiple formats
        supported_formats = ['pdf', 'png', 'svg', 'eps', 'tiff']
        file_format = output_path.suffix.lstrip('.').lower()
        if file_format not in supported_formats:
            file_format = 'pdf'
            output_path = output_path.with_suffix('.pdf')
        
        g.savefig(output_path, dpi=dpi, bbox_inches='tight', format=file_format)
        print(f"✓ saved: {output_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def quick_heatmap(self,
                     data_path: str,
                     output_path: str,
                     **kwargs) -> None:
        """Quickly generate heatmaps (using default parameters)
        
        Args:
            data_path: input data path
            output_path: output path
            **kwargs: Optional parameter override"""
        defaults = {
            'title': 'Gene Expression Heatmap',
            'cmap': 'RdBu_r',
            'center': 0,
            'row_cluster': True,
            'col_cluster': True,
            'dpi': 300
        }
        defaults.update(kwargs)
        
        self.create_heatmap(data_path, output_path, **defaults)


def load_annotations_from_json(path: str) -> Dict[str, Dict[str, str]]:
    """Load comments from JSON file"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Command line entry"""
    parser = argparse.ArgumentParser(
        description='Heatmap Beautifier - Gene expression heatmap beautification tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  %(prog)s -i expression.csv -o heatmap.pdf
  %(prog)s -i expression.csv -o heatmap.png --row-cluster --col-cluster
  %(prog)s -i expression.csv -o heatmap.pdf --row-annot row.json --col-annot col.json"""
    )
    
    parser.add_argument('-i', '--input', required=True, 
                       help='Input expression matrix (CSV format)')
    parser.add_argument('-o', '--output', required=True,
                       help='Output image path')
    parser.add_argument('-t', '--title', default='Gene Expression Heatmap',
                       help='Chart title')
    parser.add_argument('--cmap', default='RdBu_r',
                       help='Colormap (default: RdBu_r)')
    parser.add_argument('--center', type=float, default=0,
                       help='Color center value (default: 0)')
    parser.add_argument('--vmin', type=float,
                       help='minimum value')
    parser.add_argument('--vmax', type=float,
                       help='maximum value')
    parser.add_argument('--row-cluster', action='store_true',
                       help='Enable row clustering')
    parser.add_argument('--col-cluster', action='store_true',
                       help='Enable column clustering')
    parser.add_argument('--row-annot', 
                       help='Line comment JSON file path')
    parser.add_argument('--col-annot',
                       help='Column annotation JSON file path')
    parser.add_argument('--z-score', type=int, choices=[0, 1],
                       help='Z-score normalized (0=row, 1=column)')
    parser.add_argument('--standard-scale', choices=['row', 'col'],
                       help='Normalization method (row or col)')
    parser.add_argument('--figsize', nargs=2, type=float,
                       help='Graphic size (width height)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='Output resolution (default: 300)')
    parser.add_argument('--hide-row-labels', action='store_true',
                       help='Hide row labels')
    parser.add_argument('--hide-col-labels', action='store_true',
                       help='Hide column labels')
    parser.add_argument('--rotate-col', type=float, default=45,
                       help='Column label rotation angle (default: 45)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Load annotations
    row_annotations = None
    col_annotations = None
    
    if args.row_annot:
        row_annotations = load_annotations_from_json(args.row_annot)
    if args.col_annot:
        col_annotations = load_annotations_from_json(args.col_annot)
    
    # Build parameters
    kwargs = {
        'title': args.title,
        'cmap': args.cmap,
        'center': args.center,
        'vmin': args.vmin,
        'vmax': args.vmax,
        'row_cluster': args.row_cluster,
        'col_cluster': args.col_cluster,
        'row_annotations': row_annotations,
        'col_annotations': col_annotations,
        'z_score': args.z_score,
        'standard_scale': args.standard_scale,
        'dpi': args.dpi,
        'hide_row_labels': args.hide_row_labels,
        'hide_col_labels': args.hide_col_labels,
        'rotate_col_labels': args.rotate_col
    }
    
    if args.figsize:
        kwargs['figsize'] = tuple(args.figsize)
    
    # Remove None values
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    # implement
    hb = HeatmapBeautifier()
    hb.create_heatmap(args.input, args.output, **kwargs)
    print("✓ Done!")


if __name__ == '__main__':
    main()
