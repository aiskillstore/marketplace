#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sensitivity analysis script (one-by-one elimination method) - Python alternative version
Usage: python sensitivity_analysis.py <csv_path> <type> [outcome_name] [output_dir]

When the R script drawing fails, use this Python script as a backup solution for sensitivity analysis and drawing."""

import sys
import os
import argparse
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from datetime import datetime

warnings.filterwarnings('ignore')

# Set Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MetaAnalyzer:
    """Meta-analysis sensitivity analyzer"""
    
    def __init__(self, data_df, data_type, outcome_name="Outcome"):
        self.data_df = data_df
        self.data_type = data_type
        self.outcome_name = outcome_name
        self.n_studies = len(data_df)
        
        if self.n_studies < 3:
            raise ValueError("At least 3 studies are required to conduct sensitivity analysis")
    
    def validate_data(self):
        """Verify data integrity"""
        required_cols = {
            'Binary': ['study', 'group1_Events', 'group1_sample_size', 
                      'group2_Events', 'group2_sample_size'],
            'Continuity': ['study', 'group1_sample_size', 'group1_Mean', 'group1_SD',
                          'group2_sample_size', 'group2_Mean', 'group2_SD'],
            'Survival': ['study', 'group1_HR', 'group1_95%Lower CI', 'group1_95%Upper CI']
        }
        
        cols = required_cols.get(self.data_type, [])
        missing = [c for c in cols if c not in self.data_df.columns]
        
        if missing:
            raise ValueError(f"Missing required column: {', '.join(missing)}")
        
        return True
    
    def calculate_ci(self, te, se, level=0.95):
        """Calculate confidence intervals"""
        z = stats.norm.ppf((1 + level) / 2)
        return te - z * se, te + z * se
    
    def meta_binary(self):
        """Two-category meta-analysis"""
        data = self.data_df.copy()
        data['e1'] = pd.to_numeric(data['group1_Events'], errors='coerce')
        data['n1'] = pd.to_numeric(data['group1_sample_size'], errors='coerce')
        data['e2'] = pd.to_numeric(data['group2_Events'], errors='coerce')
        data['n2'] = pd.to_numeric(data['group2_sample_size'], errors='coerce')
        
        # Mantel-Haenszel estimate
        results = []
        for idx, row in data.iterrows():
            if pd.isna([row['e1'], row['n1'], row['e2'], row['n2']]).any():
                continue
            
            # Use log OR
            p1 = (row['e1'] + 0.5) / (row['n1'] + 1)
            p2 = (row['e2'] + 0.5) / (row['n2'] + 1)
            te = np.log(p1 / p2 * (1 - p2) / (1 - p1))
            se = np.sqrt(1 / (row['e1'] + 0.5) + 1 / (row['n1'] - row['e1'] + 0.5) +
                        1 / (row['e2'] + 0.5) + 1 / (row['n2'] - row['e2'] + 0.5))
            
            results.append({
                'study': row['study'],
                'te': te,
                'se': se,
                'n': row['n1'] + row['n2']
            })
        
        return pd.DataFrame(results), 'OR'
    
    def meta_continuity(self):
        """Continuous variable meta-analysis"""
        data = self.data_df.copy()
        
        results = []
        for idx, row in data.iterrows():
            n1 = pd.to_numeric(row['group1_sample_size'], errors='coerce')
            m1 = pd.to_numeric(row['group1_Mean'], errors='coerce')
            sd1 = pd.to_numeric(row['group1_SD'], errors='coerce')
            n2 = pd.to_numeric(row['group2_sample_size'], errors='coerce')
            m2 = pd.to_numeric(row['group2_Mean'], errors='coerce')
            sd2 = pd.to_numeric(row['group2_SD'], errors='coerce')
            
            if pd.isna([n1, m1, sd1, n2, m2, sd2]).any():
                continue
            
            # Calculate the standardized mean difference (SMD)
            pooled_sd = np.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2))
            te = (m1 - m2) / pooled_sd if pooled_sd > 0 else 0
            se = np.sqrt(1/n1 + 1/n2 + te**2 / (2 * (n1 + n2)))
            
            results.append({
                'study': row['study'],
                'te': te,
                'se': se,
                'n': n1 + n2
            })
        
        return pd.DataFrame(results), 'SMD'
    
    def meta_survival(self):
        """Survival meta-analysis"""
        data = self.data_df.copy()
        
        results = []
        for idx, row in data.iterrows():
            hr = pd.to_numeric(row['group1_HR'], errors='coerce')
            lower_ci = pd.to_numeric(row.get('group1_95%Lower CI', None) or 
                                    row.get('group1_95.Lower.CI', None), errors='coerce')
            upper_ci = pd.to_numeric(row.get('group1_95%Upper CI', None) or 
                                    row.get('group1_95.Upper.CI', None), errors='coerce')
            
            if pd.isna([hr, lower_ci, upper_ci]).any() or hr <= 0 or lower_ci <= 0 or upper_ci <= 0:
                continue
            
            # Log conversion
            te = np.log(hr)
            se = (np.log(upper_ci) - np.log(lower_ci)) / (2 * 1.96)
            
            results.append({
                'study': row['study'],
                'te': te,
                'se': se,
                'n': 100  # Assuming sample size
            })
        
        if len(results) < 3:
            raise ValueError("There are less than 3 valid data items and sensitivity analysis cannot be performed.")
        
        return pd.DataFrame(results), 'HR'
    
    def inverse_variance_meta(self, meta_df):
        """Meta-analysis using inverse variance pooling method"""
        meta_df = meta_df.copy()
        meta_df['weight'] = 1 / (meta_df['se'] ** 2)
        total_weight = meta_df['weight'].sum()
        
        te_pooled = (meta_df['te'] * meta_df['weight']).sum() / total_weight
        se_pooled = 1 / np.sqrt(total_weight)
        
        # Compute heterogeneity
        q = ((meta_df['te'] - te_pooled) ** 2 / (meta_df['se'] ** 2)).sum()
        df = len(meta_df) - 1
        i2 = max(0, (q - df) / q) if q > df else 0
        
        return {
            'te': te_pooled,
            'se': se_pooled,
            'q': q,
            'i2': i2,
            'p_value': 1 - stats.chi2.cdf(q, df) if df > 0 else 1.0
        }
    
    def sensitivity_analysis(self, meta_results, effect_label):
        """Perform sensitivity analysis (one-by-one elimination method)"""
        sensitivity_list = []
        
        for leave_out_idx in range(len(meta_results)):
            # Construct a dataset with the i-th study removed
            subset = meta_results.drop(leave_out_idx).reset_index(drop=True)
            
            if len(subset) < 2:
                continue
            
            # Meta-analysis
            pooled = self.inverse_variance_meta(subset)
            
            study_name = meta_results.iloc[leave_out_idx]['study']
            study_name = study_name[:18] + '...' if len(study_name) > 18 else study_name
            
            sensitivity_list.append({
                'study_leave_out': study_name,
                'te': pooled['te'],
                'se': pooled['se'],
                'i2': pooled['i2'],
                'p_value': pooled['p_value'],
                'q': pooled['q']
            })
        
        return pd.DataFrame(sensitivity_list)
    
    def format_effect(self, te, effect_label):
        """Formatting effect sizes based on effect metric type"""
        if effect_label in ['OR', 'HR']:
            return np.exp(te)
        return te
    
    def analyze(self):
        """Perform a complete sensitivity analysis"""
        self.validate_data()
        
        # Select analysis method based on type
        if self.data_type == 'Binary':
            meta_results, effect_label = self.meta_binary()
        elif self.data_type == 'Continuity':
            meta_results, effect_label = self.meta_continuity()
        elif self.data_type == 'Survival':
            meta_results, effect_label = self.meta_survival()
        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")
        
        if len(meta_results) < 3:
            raise ValueError("There are less than 3 valid data items and sensitivity analysis cannot be performed.")
        
        # Meta-analysis of all studies
        pooled_all = self.inverse_variance_meta(meta_results)
        
        # sensitivity analysis
        sensitivity_df = self.sensitivity_analysis(meta_results, effect_label)
        
        # Format results for output
        te_display = self.format_effect(sensitivity_df['te'], effect_label)
        lower, upper = self.calculate_ci(sensitivity_df['te'], sensitivity_df['se'])
        lower_display = self.format_effect(lower, effect_label)
        upper_display = self.format_effect(upper, effect_label)
        
        pooled_display = self.format_effect(pooled_all['te'], effect_label)
        pooled_lower, pooled_upper = self.calculate_ci(pooled_all['te'], pooled_all['se'])
        pooled_lower = self.format_effect(pooled_lower, effect_label)
        pooled_upper = self.format_effect(pooled_upper, effect_label)
        
        return {
            'meta_results': meta_results,
            'sensitivity_df': sensitivity_df,
            'te_display': te_display,
            'lower_display': lower_display,
            'upper_display': upper_display,
            'pooled_display': pooled_display,
            'pooled_lower': pooled_lower,
            'pooled_upper': pooled_upper,
            'pooled_all': pooled_all,
            'effect_label': effect_label
        }


def plot_forest(sensitivity_df, meta_results, effect_label, outcome_name, output_file):
    """Plot a sensitivity analysis forest plot"""
    n_studies = len(sensitivity_df)
    plot_height = max(6, 3 + n_studies * 0.3)
    
    fig, ax = plt.subplots(figsize=(10, plot_height))
    
    # Extract data
    studies = sensitivity_df['study_leave_out'].values
    te = sensitivity_df['te'].values
    se = sensitivity_df['se'].values
    
    # Convert display value
    if effect_label in ['OR', 'HR']:
        display_te = np.exp(te)
        ci_lower, ci_upper = np.exp(te - 1.96 * se), np.exp(te + 1.96 * se)
    else:
        display_te = te
        ci_lower, ci_upper = te - 1.96 * se, te + 1.96 * se
    
    # draw
    y_pos = np.arange(n_studies, 0, -1)
    
    for i, (y, te_val, lower, upper) in enumerate(zip(y_pos, display_te, ci_lower, ci_upper)):
        # caliber line
        ax.plot([lower, upper], [y, y], 'b-', linewidth=1.5)
        # point of effect
        ax.plot(te_val, y, 'o', color='darkblue', markersize=8)
    
    # reference line
    if effect_label in ['OR', 'HR']:
        ax.axvline(x=1, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    else:
        ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(studies)
    ax.set_xlabel(effect_label, fontsize=12)
    ax.set_title(f'Leave-one-out {effect_label} ({outcome_name})', fontsize=14, fontweight='bold')
    ax.set_ylim(0, n_studies + 1)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    try:
        plt.savefig(output_file, dpi=100, bbox_inches='tight', encoding='utf-8')
        print(f"✓ Sensitivity analysis forest plot: {output_file}")
    except Exception as e:
        print(f"✗ Forest map failed to save: {e}")
    plt.close()


def plot_funnel(meta_results, effect_label, outcome_name, output_file):
    """Draw a funnel chart"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    te = meta_results['te'].values
    se = meta_results['se'].values
    
    # Convert display value
    if effect_label in ['OR', 'HR']:
        display_te = np.exp(te)
    else:
        display_te = te
    
    ax.scatter(display_te, se, alpha=0.6, s=100, color='darkblue')
    
    # Draw lines of symmetry
    max_se = se.max() * 1.1
    if effect_label in ['OR', 'HR']:
        reference = 1
    else:
        reference = 0
    
    se_line = np.linspace(0, max_se, 100)
    for z in [1.96, 3.29]:
        ax.plot(reference + z * se_line, se_line, 'k--', alpha=0.3, linewidth=1)
        ax.plot(reference - z * se_line, se_line, 'k--', alpha=0.3, linewidth=1)
    
    ax.axvline(x=reference, color='red', linestyle='-', linewidth=2, alpha=0.5)
    ax.set_xlabel(effect_label, fontsize=12)
    ax.set_ylabel('Standard Error', fontsize=12)
    ax.set_title(f'Funnel Plot ({outcome_name})', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(alpha=0.3)
    
    # Add tag
    for i, (x, y) in enumerate(zip(display_te, se)):
        study_name = meta_results.iloc[i]['study']
        if len(study_name) > 10:
            study_name = study_name[:7] + '...'
        ax.annotate(study_name, (x, y), fontsize=8, alpha=0.7, 
                   xytext=(5, 5), textcoords='offset points')
    
    plt.tight_layout()
    try:
        plt.savefig(output_file, dpi=100, bbox_inches='tight', encoding='utf-8')
        print(f"✓ funnel chart: {output_file}")
    except Exception as e:
        print(f"✗ Funnel chart saving failed: {e}")
    plt.close()


def save_results_csv(results, output_file):
    """Save sensitivity analysis results to CSV"""
    output_df = pd.DataFrame({
        'study': results['sensitivity_df']['study_leave_out'],
        'value': results['te_display'].round(2),
        'lower_95': results['lower_display'].round(2),
        'upper_95': results['upper_display'].round(2),
        'I2': (results['sensitivity_df']['i2'] * 100).round(1),
        'p_value': results['sensitivity_df']['p_value'].round(4),
        'Q_statistic': results['sensitivity_df']['q'].round(2)
    })
    
    output_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Sensitivity Analysis Data Sheet: {output_file}")


def print_summary(results, data_type, outcome_name, n_studies):
    """Print result summary"""
    effect_label = results['effect_label']
    
    # Judgment Robustness
    effect_values = results['te_display'].values
    pooled_val = results['pooled_display']
    
    if effect_label in ['OR', 'HR']:
        all_greater = np.all(effect_values > 1)
        all_smaller = np.all(effect_values < 1)
    else:
        all_greater = np.all(effect_values > 0)
        all_smaller = np.all(effect_values < 0)
    
    robustness = 'steady' if (all_greater or all_smaller) else 'Not robust (the direction of the effect size changes after removing some studies)'
    
    effect_range = [np.nanmin(effect_values), np.nanmax(effect_values)]
    effect_variation = abs((effect_range[1] - effect_range[0]) / pooled_val * 100) if pooled_val != 0 else 0
    
    # output
    print("\n" + "="*50)
    print("Sensitivity analysis completed")
    print("="*50 + "\n")
    print(f"【Outcome indicators】{outcome_name}")
    print(f"【data type】{data_type}")
    print(f"【Included studies】{n_studies} item\n")
    
    print("[Pooled effect size (all studies)]")
    print(f"• {effect_label} = {results['pooled_display']:.2f} " +
          f"[{results['pooled_lower']:.2f}; {results['pooled_upper']:.2f}]\n")
    
    print("[Summary of sensitivity analysis results]")
    print(f"{'Eliminate studies':<20} {effect_label:<10} {'95% CI':<20} {'I²':<8}")
    print("-"*50)
    
    for i, row in results['sensitivity_df'].iterrows():
        study = row['study_leave_out']
        value = f"{results['te_display'].iloc[i]:.2f}"
        ci = f"[{results['lower_display'].iloc[i]:.2f}; {results['upper_display'].iloc[i]:.2f}]"
        i2 = f"{row['i2']*100:.1f}%" if not np.isnan(row['i2']) else "NA"
        print(f"{study:<20} {value:<10} {ci:<20} {i2:<8}")
    
    print("【Effect size change analysis】")
    print(f"• effect size range：{effect_range[0]:.2f} ~ {effect_range[1]:.2f}")
    print(f"• Relative change amplitude：{effect_variation:.1f}%\n")
    
    print("【in conclusion】")
    print(f"• Effect size robustness：{robustness}")
    
    if effect_variation < 10:
        print("• The effect size change is small (<10%) after excluding any single study, and the results are robust.")
    elif effect_variation < 20:
        print("• After excluding some studies, the effect size will change to a certain extent (10-20%), so attention should be paid to studies with greater impact.")
    else:
        print("• The effect size varies greatly (>20%), and some studies have a significant impact on the results. Further analysis is recommended.")
    
    print("="*50 + "\n")


def main():
    # Parse command line parameters
    parser = argparse.ArgumentParser(description='Meta-analysis sensitivity analysis (Python alternative version)')
    parser.add_argument('csv_path', help='Enter CSV file path')
    parser.add_argument('type', choices=['Binary', 'Continuity', 'Survival'],
                       help='data type')
    parser.add_argument('outcome_name', nargs='?', default='Outcome',
                       help='Outcome indicator name (optional)')
    parser.add_argument('output_dir', nargs='?', default=None,
                       help='Output directory (optional)')
    
    args = parser.parse_args()
    
    csv_path = args.csv_path
    data_type = args.type
    outcome_name = args.outcome_name if args.outcome_name else 'Outcome'
    output_dir = args.output_dir if args.output_dir else os.path.dirname(csv_path)
    
    # Validate input files
    if not os.path.exists(csv_path):
        print(f"✗ File does not exist: {csv_path}")
        sys.exit(1)
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Read data
    try:
        data_df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"✗ Unable to readCSVdocument: {e}")
        sys.exit(1)
    
    # Perform analysis
    try:
        analyzer = MetaAnalyzer(data_df, data_type, outcome_name)
        results = analyzer.analyze()
        
        # Save results
        csv_output = os.path.join(output_dir, f"{data_type}_sensitive_{outcome_name}.csv")
        forest_output = os.path.join(output_dir, f"{data_type}_sensitive_forest_{outcome_name}.png")
        funnel_output = os.path.join(output_dir, f"{data_type}_funnel_{outcome_name}.png")
        
        save_results_csv(results, csv_output)
        plot_forest(results['sensitivity_df'], results['meta_results'], 
                   results['effect_label'], outcome_name, forest_output)
        plot_funnel(results['meta_results'], results['effect_label'], 
                   outcome_name, funnel_output)
        
        # Print summary
        print_summary(results, data_type, outcome_name, len(data_df))
        
        print("✓ Python sensitivity analysis (alternative plan) was executed successfully!")
        
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
