#!/usr/bin/env python3
"""Survival Curve Risk Table Generator
Automatically align and add "Number at risk" table below Kaplan-Meier survival curve
Comply with clinical oncology journal standards (NEJM, Lancet, JCO, etc.)

Author:OpenClaw
Version: 1.0.0"""

import argparse
import sys
import warnings
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Union
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# Try importing optional dependencies
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    warnings.warn("PIL not installed. Image combining features disabled.")

try:
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test
    HAS_LIFELINES = True
except ImportError:
    HAS_LIFELINES = False
    warnings.warn("lifelines not installed. Survival analysis features limited.")


class RiskTableGenerator:
    """Survival Curve Risk Table Generator
    
    Main functions:
    1. Calculate the number of people at risk at each time point from survival data
    2. Generate tables that comply with journal standards
    3. Combine with KM curve to generate publication-level images"""
    
    # Predefined journal style configurations
    JOURNAL_STYLES = {
        "NEJM": {
            "font_family": "Helvetica",
            "font_size": 8,
            "table_height_ratio": 0.15,
            "show_grid": False,
            "separator_lines": True,
            "header_bold": True,
            "time_label": "mo",
        },
        "Lancet": {
            "font_family": "Times New Roman",
            "font_size": 9,
            "table_height_ratio": 0.18,
            "show_grid": True,
            "separator_lines": True,
            "header_bold": True,
            "time_label": "months",
        },
        "JCO": {
            "font_family": "Arial",
            "font_size": 8,
            "table_height_ratio": 0.16,
            "show_grid": False,
            "separator_lines": False,
            "header_bold": False,
            "time_label": "mo",
            "show_censored": True,
            "censor_symbol": "+",
        },
        "custom": {
            "font_family": "Arial",
            "font_size": 8,
            "table_height_ratio": 0.15,
            "show_grid": False,
            "separator_lines": True,
            "header_bold": True,
            "time_label": "mo",
        }
    }
    
    def __init__(
        self,
        style: str = "NEJM",
        time_points: Optional[List[float]] = None,
        figure_size: Tuple[float, float] = (8, 6),
        dpi: int = 300,
        custom_style: Optional[Dict] = None
    ):
        """Initialize risk table generator
        
        Args:
            style: journal style (NEJM, Lancet, JCO, custom)
            time_points: Custom time point list
            figure_size: image size (width, height) inches
            dpi: image resolution
            custom_style: Custom style configuration (used when style='custom')"""
        self.style_name = style
        self.style = self.JOURNAL_STYLES.get(style, self.JOURNAL_STYLES["NEJM"]).copy()
        
        if custom_style and style == "custom":
            self.style.update(custom_style)
        
        self.time_points = time_points
        self.figure_size = figure_size
        self.dpi = dpi
        
        self.data = None
        self.time_col = None
        self.event_col = None
        self.group_col = None
        self.groups = None
        
    def load_data(
        self,
        df: pd.DataFrame,
        time_col: str,
        event_col: str,
        group_col: Optional[str] = None
    ) -> None:
        """Load survival data
        
        Args:
            df: survival data DataFrame
            time_col: time column name
            event_col: event column name (1=event, 0=censored)
            group_col: grouping column name (optional)"""
        self.data = df.copy()
        self.time_col = time_col
        self.event_col = event_col
        self.group_col = group_col
        
        # Validate required columns
        required_cols = [time_col, event_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        if group_col and group_col not in df.columns:
            raise ValueError(f"Group column '{group_col}' not found in data")
        
        # Extract group information
        if group_col:
            self.groups = df[group_col].unique().tolist()
        else:
            self.groups = ["All"]
            self.data["__group__"] = "All"
            self.group_col = "__group__"
        
        # Data type checking
        if not pd.api.types.is_numeric_dtype(self.data[time_col]):
            raise ValueError(f"Time column '{time_col}' must be numeric")
        
        # Make sure the event column is numeric
        self.data[event_col] = pd.to_numeric(self.data[event_col], errors='coerce')
        
        # Automatically determine time point (if not specified)
        if self.time_points is None:
            self._auto_select_time_points()
    
    def load_data_from_file(
        self,
        file_path: str,
        time_col: str,
        event_col: str,
        group_col: Optional[str] = None
    ) -> None:
        """Load survival data from file
        
        Supported formats: CSV, Excel, SAS, pickle"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == '.csv':
            df = pd.read_csv(file_path)
        elif suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif suffix == '.sas7bdat':
            df = pd.read_sas(file_path)
        elif suffix in ['.pkl', '.pickle']:
            df = pd.read_pickle(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
        
        self.load_data(df, time_col, event_col, group_col)
    
    def _auto_select_time_points(self, n_points: int = 7) -> None:
        """Automatically select time points
        
        Strategy: Use equally spaced time points to cover the 0 to maximum follow-up time of the data"""
        if self.data is None:
            raise ValueError("No data loaded")
        
        max_time = self.data[self.time_col].max()
        
        # Generate equidistant time points (containing 0 and maximum values)
        self.time_points = np.linspace(0, max_time, n_points).tolist()
        self.time_points = [round(t, 1) for t in self.time_points]
    
    def calculate_number_at_risk(self) -> pd.DataFrame:
        """Calculate the number of people at risk at each time point
        
        Returns:
            DataFrame, columns are time points, behavior grouping, value is the number of people at risk"""
        if self.data is None:
            raise ValueError("No data loaded")
        
        results = []
        
        for group in self.groups:
            group_data = self.data[self.data[self.group_col] == group]
            n_total = len(group_data)
            
            row = {"Group": group}
            for t in self.time_points:
                # The number of people at risk = the total number of people - the number of people who had the incident before time t - the number of people who were censored before time t
                events_before = len(group_data[
                    (group_data[self.time_col] <= t) & 
                    (group_data[self.event_col] == 1)
                ])
                censored_before = len(group_data[
                    (group_data[self.time_col] < t) & 
                    (group_data[self.event_col] == 0)
                ])
                
                n_at_risk = n_total - events_before - censored_before
                row[f"t_{t}"] = max(0, n_at_risk)
            
            results.append(row)
        
        return pd.DataFrame(results)
    
    def calculate_censored_counts(self) -> pd.DataFrame:
        """Calculate the censored number of people in each time interval (for JCO style)"""
        if self.data is None:
            raise ValueError("No data loaded")
        
        results = []
        
        for group in self.groups:
            group_data = self.data[self.data[self.group_col] == group]
            row = {"Group": group}
            
            for i, t in enumerate(self.time_points):
                if i == 0:
                    censored_in_interval = 0
                else:
                    t_prev = self.time_points[i - 1]
                    censored_in_interval = len(group_data[
                        (group_data[self.time_col] > t_prev) &
                        (group_data[self.time_col] <= t) &
                        (group_data[self.event_col] == 0)
                    ])
                row[f"t_{t}"] = censored_in_interval
            
            results.append(row)
        
        return pd.DataFrame(results)
    
    def generate_risk_table(
        self,
        output_path: str,
        show_censored: Optional[bool] = None,
        show_events: bool = False,
        title: Optional[str] = None
    ) -> None:
        """Generate independent risk table images
        
        Args:
            output_path: output file path
            show_censored: whether to display the censored number of people (default is read from the style configuration)
            show_events: whether to display the number of events
            title: table title"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if show_censored is None:
            show_censored = self.style.get("show_censored", False)
        
        # Calculated data
        risk_df = self.calculate_number_at_risk()
        
        # Set font
        plt.rcParams['font.family'] = self.style.get("font_family", "Arial")
        
        # Create graphics
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        ax.axis('off')
        
        # Prepare tabular data
        table_data = self._prepare_table_data(risk_df, show_censored)
        
        # draw table
        self._draw_risk_table(ax, table_data, title)
        
        # save
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"Risk table saved to: {output_path}")
    
    def _prepare_table_data(
        self,
        risk_df: pd.DataFrame,
        show_censored: bool
    ) -> List[List[str]]:
        """Prepare tabular data"""
        # Header
        time_label = self.style.get("time_label", "mo")
        headers = ["Number at risk"]
        for t in self.time_points:
            if t == self.time_points[-1]:
                headers.append(f"{int(t)} ({time_label})")
            else:
                headers.append(str(int(t)))
        
        # data row
        rows = []
        for _, row in risk_df.iterrows():
            group_name = row["Group"]
            data_row = [group_name]
            for t in self.time_points:
                data_row.append(str(int(row[f"t_{t}"])))
            rows.append(data_row)
        
        # If you need to display the censored number of people (JCO style)
        if show_censored:
            censored_df = self.calculate_censored_counts()
            for _, row in censored_df.iterrows():
                group_name = row["Group"]
                data_row = [f"  ({self.style.get('censor_symbol', '+')})"]
                for t in self.time_points:
                    count = int(row[f"t_{t}"])
                    data_row.append(str(count) if count > 0 else "")
                rows.append(data_row)
        
        return [headers] + rows
    
    def _draw_risk_table(
        self,
        ax,
        table_data: List[List[str]],
        title: Optional[str] = None
    ) -> None:
        """Draw a risk table"""
        font_size = self.style.get("font_size", 8)
        show_grid = self.style.get("show_grid", False)
        header_bold = self.style.get("header_bold", True)
        
        # Create table
        table = ax.table(
            cellText=table_data[1:],
            colLabels=table_data[0],
            loc='center',
            cellLoc='center'
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(font_size)
        table.scale(1, 2)
        
        # Set style
        for i, key in enumerate(table.get_celld().keys()):
            cell = table.get_celld()[key]
            row, col = key
            
            # Header style
            if row == 0:
                cell.set_text_props(fontweight='bold' if header_bold else 'normal')
                cell.set_facecolor('#f0f0f0')
                cell.set_edgecolor('black' if show_grid else 'none')
            else:
                # Data row style
                cell.set_edgecolor('black' if show_grid else 'none')
                
                # The first column (group name) is left aligned
                if col == 0:
                    cell.set_text_props(ha='left')
                    cell._loc = 'left'
        
        # Add title
        if title:
            ax.set_title(title, fontsize=font_size + 2, fontweight='bold', pad=10)
    
    def generate_combined_plot(
        self,
        km_plot_path: Optional[str] = None,
        output_path: str = "combined_survival_plot.png",
        km_ax: Optional[matplotlib.axes.Axes] = None,
        show_km_plot: bool = True,
        km_title: Optional[str] = None
    ) -> None:
        """Generate a combined graph of KM curve and risk table
        
        Args:
            km_plot_path: external KM curve image path (optional)
            output_path: output file path
            km_ax: pre-generated KM curve axes (optional)
            show_km_plot: whether to display KM curve
            km_title: KM curve title"""
        if not HAS_LIFELINES and km_ax is None and km_plot_path is None:
            raise ImportError("lifelines is required for generating KM plots. "
                            "Install with: pip install lifelines")
        
        # Set font
        plt.rcParams['font.family'] = self.style.get("font_family", "Arial")
        
        # Create a graphic layout
        fig_height = self.figure_size[1]
        table_height_ratio = self.style.get("table_height_ratio", 0.15)
        
        if show_km_plot:
            fig = plt.figure(figsize=(self.figure_size[0], fig_height), dpi=self.dpi)
            gs = GridSpec(2, 1, height_ratios=[1 - table_height_ratio, table_height_ratio],
                         hspace=0.05)
            
            # Upper part: KM curve
            ax_km = fig.add_subplot(gs[0])
            
            if km_plot_path and Path(km_plot_path).exists():
                # Use external images
                img = plt.imread(km_plot_path)
                ax_km.imshow(img)
                ax_km.axis('off')
            elif km_ax is not None:
                # Use the provided axes (complicated, not implemented yet)
                pass
            else:
                # Automatically generate KM curve
                self._plot_km_curve(ax_km, km_title)
            
            # Lower part: risk table
            ax_table = fig.add_subplot(gs[1])
            ax_table.axis('off')
            
            # Prepare and draw tables
            risk_df = self.calculate_number_at_risk()
            show_censored = self.style.get("show_censored", False)
            table_data = self._prepare_table_data(risk_df, show_censored)
            self._draw_risk_table(ax_table, table_data)
            
            # Align X axis
            if hasattr(self, '_km_xlim'):
                ax_table.set_xlim(self._km_xlim)
        else:
            # Generate risk table only
            self.generate_risk_table(output_path)
            return
        
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"Combined plot saved to: {output_path}")
    
    def _plot_km_curve(
        self,
        ax: matplotlib.axes.Axes,
        title: Optional[str] = None
    ) -> None:
        """Use lifelines to draw KM curve"""
        if not HAS_LIFELINES:
            raise ImportError("lifelines is required for generating KM plots")
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.groups)))
        
        for i, group in enumerate(self.groups):
            group_data = self.data[self.data[self.group_col] == group]
            
            kmf = KaplanMeierFitter()
            kmf.fit(
                durations=group_data[self.time_col],
                event_observed=group_data[self.event_col],
                label=group
            )
            
            kmf.plot_survival_function(
                ax=ax,
                ci_show=False,
                color=colors[i],
                linewidth=2
            )
        
        ax.set_xlabel(f"Time ({self.style.get('time_label', 'months')})", fontsize=10)
        ax.set_ylabel("Survival Probability", fontsize=10)
        ax.set_ylim(0, 1.05)
        ax.legend(loc='lower left', frameon=False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        if title:
            ax.set_title(title, fontsize=12, fontweight='bold')
        
        # Save X-axis range for alignment
        self._km_xlim = ax.get_xlim()
    
    def export_risk_table_data(self, output_path: str) -> None:
        """Export risk table data to CSV"""
        risk_df = self.calculate_number_at_risk()
        
        # Rename columns to more friendly names
        time_label = self.style.get("time_label", "mo")
        col_map = {"Group": "Group"}
        for t in self.time_points:
            col_map[f"t_{t}"] = f"{int(t)} {time_label}"
        
        risk_df = risk_df.rename(columns=col_map)
        risk_df.to_csv(output_path, index=False)
        print(f"Risk table data exported to: {output_path}")


def create_sample_data(output_path: str, n_patients: int = 300, seed: int = 42) -> None:
    """Create sample survival data for testing"""
    np.random.seed(seed)
    
    # Generate two sets of data
    n_per_group = n_patients // 2
    
    # Experimental Group: Better Survival
    exp_times = np.random.exponential(scale=36, size=n_per_group)
    exp_events = np.random.binomial(1, 0.6, n_per_group)
    
    # control group
    ctrl_times = np.random.exponential(scale=24, size=n_per_group)
    ctrl_events = np.random.binomial(1, 0.7, n_per_group)
    
    # Combined data
    df = pd.DataFrame({
        'time': np.concatenate([exp_times, ctrl_times]),
        'event': np.concatenate([exp_events, ctrl_events]),
        'treatment': ['Experimental'] * n_per_group + ['Control'] * n_per_group
    })
    
    # Censored for more than 60 months
    df.loc[df['time'] > 60, 'event'] = 0
    df.loc[df['time'] > 60, 'time'] = 60
    
    df.to_csv(output_path, index=False)
    print(f"Sample data created: {output_path}")


def main():
    """Command line entry"""
    parser = argparse.ArgumentParser(
        description="Generate Number at Risk table for Kaplan-Meier survival curves",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  #Basic usage
  python main.py --input data.csv --time-col time --event-col event --output risk_table.png
  
  #Specify journal style
  python main.py --input data.csv --time-col time --event-col event --style NEJM --output figure.pdf
  
  # Combination chart (automatically generate KM curve)
  python main.py --input data.csv --time-col time --event-col event --combine --output combined.png
  
  #Specify time point
  python main.py --input data.csv --time-col time --event-col event --time-points 0,6,12,18,24,30,36
  
  #Create sample data
  python main.py --create-sample-data sample.csv"""
    )
    
    # input parameters
    parser.add_argument('--input', '-i', type=str, help='Input data file path')
    parser.add_argument('--time-col', type=str, help='Time column name')
    parser.add_argument('--event-col', type=str, help='Event column name (1=event, 0=censored)')
    parser.add_argument('--group-col', type=str, help='Group column name (optional)')
    
    # Output parameters
    parser.add_argument('--output', '-o', type=str, default='risk_table.png',
                       help='Output file path (default: risk_table.png)')
    parser.add_argument('--output-dir', type=str, help='Output directory for batch processing')
    
    # style parameters
    parser.add_argument('--style', type=str, default='NEJM',
                       choices=['NEJM', 'Lancet', 'JCO', 'custom'],
                       help='Journal style (default: NEJM)')
    parser.add_argument('--time-points', type=str,
                       help='Comma-separated time points (e.g., 0,6,12,18,24)')
    
    # Image parameters
    parser.add_argument('--width', type=float, default=8, help='Figure width in inches (default: 8)')
    parser.add_argument('--height', type=float, default=6, help='Figure height in inches (default: 6)')
    parser.add_argument('--dpi', type=int, default=300, help='DPI resolution (default: 300)')
    parser.add_argument('--font-size', type=int, help='Font size (overrides style default)')
    
    # Function switch
    parser.add_argument('--combine', action='store_true',
                       help='Generate combined KM plot with risk table')
    parser.add_argument('--km-plot', type=str, help='Path to existing KM plot image')
    parser.add_argument('--show-censored', action='store_true',
                       help='Show censored counts in table')
    parser.add_argument('--show-events', action='store_true',
                       help='Show event counts in table')
    parser.add_argument('--export-data', action='store_true',
                       help='Export risk table data as CSV')
    
    # tool
    parser.add_argument('--create-sample-data', type=str, metavar='PATH',
                       help='Create sample survival data for testing')
    
    args = parser.parse_args()
    
    # Create sample data
    if args.create_sample_data:
        create_sample_data(args.create_sample_data)
        return
    
    # Validate required parameters
    if not args.input:
        parser.error("--input is required (or use --create-sample-data to generate test data)")
    
    if not args.time_col or not args.event_col:
        parser.error("--time-col and --event-col are required")
    
    # Analysis time point
    time_points = None
    if args.time_points:
        time_points = [float(x.strip()) for x in args.time_points.split(',')]
    
    # Custom style
    custom_style = {}
    if args.font_size:
        custom_style['font_size'] = args.font_size
    
    # Initialization generator
    generator = RiskTableGenerator(
        style=args.style,
        time_points=time_points,
        figure_size=(args.width, args.height),
        dpi=args.dpi,
        custom_style=custom_style if custom_style else None
    )
    
    # Load data
    print(f"Loading data from: {args.input}")
    generator.load_data_from_file(
        args.input,
        args.time_col,
        args.event_col,
        args.group_col
    )
    print(f"Loaded {len(generator.data)} records")
    print(f"Groups: {generator.groups}")
    print(f"Time points: {generator.time_points}")
    
    # Export data
    if args.export_data:
        data_output = args.output.replace('.png', '.csv').replace('.pdf', '.csv')
        generator.export_risk_table_data(data_output)
    
    # generate image
    if args.combine:
        print("Generating combined plot...")
        generator.generate_combined_plot(
            km_plot_path=args.km_plot,
            output_path=args.output
        )
    else:
        print("Generating risk table...")
        generator.generate_risk_table(
            output_path=args.output,
            show_censored=args.show_censored,
            show_events=args.show_events
        )
    
    print("Done!")


if __name__ == "__main__":
    main()
