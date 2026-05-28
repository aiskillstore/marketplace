#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Continuous data forest plot drawing script (Python version)
Used to supplement after R execution failure
Usage: python forest_continuous.py <csv_path> [outcome_name] [output_dir]"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import warnings
import math

warnings.filterwarnings('ignore')

# Set Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MetaAnalysis:
    """Meta analysis class"""
    
    def __init__(self, data_df):
        """Initialize Meta-Analysis"""
        self.data = data_df.copy()
        self.validate_data()
        self.prepare_data()
        self.calculate_effects()
        self.calculate_pooled()
    
    @staticmethod
    def norm_cdf(z):
        """Calculate the CDF of the standard normal distribution"""
        return (1.0 + math.erf(z / math.sqrt(2.0))) / 2.0
    
    @staticmethod
    def chi2_sf(x, df):
        """Calculate the survival function (1 - CDF) of the chi-square distribution - approximate implementation"""
        if x <= 0:
            return 1.0
        if x > 1000:
            return 0.0
        # Use simple approximations
        return 1.0 - MetaAnalysis._chi2_cdf_approx(x, df)
    
    @staticmethod
    def _chi2_cdf_approx(x, df):
        """Approximation of chi-square distribution CDF"""
        # Use simple approximation for case df >= 1
        if df == 1:
            z = math.sqrt(x)
            return 2 * MetaAnalysis.norm_cdf(z) - 1
        else:
            # Use Wilson-Hilferty Transform
            z = (x / df) ** (1/3) - (1 - 2/(9*df))
            z = z / math.sqrt(2/(9*df))
            return MetaAnalysis.norm_cdf(z)
        
    def validate_data(self):
        """Validate required columns"""
        # Supports two column name formats
        has_format1 = all(col in self.data.columns for col in 
                         ["study", "group1_sample_size", "group1_Mean", "group1_SD",
                          "group2_sample_size", "group2_Mean", "group2_SD"])
        
        has_format2 = all(col in self.data.columns for col in 
                         ["Study", "Mean.e", "SD.e", "Total.e", "Mean.c", "SD.c", "Total.c"])
        
        if not (has_format1 or has_format2):
            raise ValueError("Required column is missing. One of the following columns is required:"
                           "Format 1: study, group1_sample_size, group1_Mean, group1_SD,"
                           "group2_sample_size, group2_Mean, group2_SD\n"
                           "Format 2: Study, Mean.e, SD.e, Total.e, Mean.c, SD.c, Total.c")
        
        # Tag data format
        self.format_type = 'format2' if has_format2 else 'format1'
        
        # Keep only non-Model rows for analysis
        if 'Study' in self.data.columns:
            self.data = self.data[self.data['Study'] != 'Model'].reset_index(drop=True)
        
        if len(self.data) < 2:
            raise ValueError("At least 2 studies are required to conduct a meta-analysis")
    
    def prepare_data(self):
        """Data preparation and type conversion"""
        if self.format_type == 'format2':
            # Support format 2 column names
            self.study = self.data['Study'].astype(str)
            self.n_e = pd.to_numeric(self.data['Total.e'], errors='coerce')
            self.mean_e = pd.to_numeric(self.data['Mean.e'], errors='coerce')
            self.sd_e = pd.to_numeric(self.data['SD.e'], errors='coerce')
            self.n_c = pd.to_numeric(self.data['Total.c'], errors='coerce')
            self.mean_c = pd.to_numeric(self.data['Mean.c'], errors='coerce')
            self.sd_c = pd.to_numeric(self.data['SD.c'], errors='coerce')
        else:
            # Supports format 1 column names
            self.study = self.data['study'].astype(str)
            self.n_e = pd.to_numeric(self.data['group1_sample_size'], errors='coerce')
            self.mean_e = pd.to_numeric(self.data['group1_Mean'], errors='coerce')
            self.sd_e = pd.to_numeric(self.data['group1_SD'], errors='coerce')
            self.n_c = pd.to_numeric(self.data['group2_sample_size'], errors='coerce')
            self.mean_c = pd.to_numeric(self.data['group2_Mean'], errors='coerce')
            self.sd_c = pd.to_numeric(self.data['group2_SD'], errors='coerce')
        
        # Check for invalid data
        if (self.n_e <= 0).any() or (self.n_c <= 0).any():
            raise ValueError("Sample size must be a positive number")
    
    def calculate_effects(self):
        """Calculate effect size (SMD) for each study"""
        # Calculate combined SD
        numerator = (self.n_e - 1) * self.sd_e**2 + (self.n_c - 1) * self.sd_c**2
        denominator = self.n_e + self.n_c - 2
        self.sd_pooled = np.sqrt(numerator / denominator)
        
        # Calculate SMD (Cohen's d)
        self.smd = (self.mean_e - self.mean_c) / self.sd_pooled
        
        # Calculate standard error
        self.se_smd = np.sqrt(1/self.n_e + 1/self.n_c + (self.smd**2)/(2*(self.n_e + self.n_c)))
        
        # Calculate 95% CI
        z_critical = 1.96
        self.ci_lower = self.smd - z_critical * self.se_smd
        self.ci_upper = self.smd + z_critical * self.se_smd
    
    def calculate_pooled(self):
        """Calculate pooled effect size (DerSimonian-Laird)"""
        # Fixed effects model
        w_fixed = 1 / (self.se_smd ** 2)
        self.te_fixed = np.sum(w_fixed * self.smd) / np.sum(w_fixed)
        self.se_fixed = np.sqrt(1 / np.sum(w_fixed))
        
        # Q statistics
        self.Q = np.sum(w_fixed * (self.smd - self.te_fixed) ** 2)
        k = len(self.smd)  # studies count
        self.pval_Q = self.chi2_sf(self.Q, df=k - 1)
        
        # I² Heterogeneity
        self.I2 = max(0, (self.Q - (k - 1)) / self.Q) if self.Q > 0 else 0
        
        # Tau²（DerSimonian-Laird）
        if self.Q > (k - 1):
            c = np.sum(w_fixed) - np.sum(w_fixed**2) / np.sum(w_fixed)
            self.tau2 = (self.Q - (k - 1)) / c if c > 0 else 0
        else:
            self.tau2 = 0
        
        # random effects model
        w_random = 1 / (self.se_smd ** 2 + self.tau2)
        self.te_random = np.sum(w_random * self.smd) / np.sum(w_random)
        self.se_random = np.sqrt(1 / np.sum(w_random))
        
        z_critical = 1.96
        self.lower_random = self.te_random - z_critical * self.se_random
        self.upper_random = self.te_random + z_critical * self.se_random
        
        # Combined P value
        z_stat = abs(self.te_random / self.se_random)
        self.pval_random = 2 * (1 - self.norm_cdf(z_stat))
        
        # Weight (random effect)
        self.w_random = w_random / np.sum(w_random) * 100


def draw_forest_plot(meta_analysis, outcome_name, output_file):
    """Draw a forest map"""
    
    fig, ax = plt.subplots(figsize=(12, 3 + len(meta_analysis.study) * 0.4))
    
    # Prepare data
    y_positions = np.arange(len(meta_analysis.study), 0, -1)
    
    # Plot point estimates and CIs for each study
    for i, y in enumerate(y_positions):
        # Draw CI line
        ax.plot([meta_analysis.ci_lower.iloc[i], meta_analysis.ci_upper.iloc[i]], 
               [y, y], 'k-', linewidth=1)
        # plot point estimate
        ax.plot(meta_analysis.smd.iloc[i], y, 'ro', markersize=8, 
               markeredgecolor='red', markeredgewidth=1)
    
    # Plot merge effects
    y_pooled = 0.5
    ax.plot([meta_analysis.lower_random, meta_analysis.upper_random], 
           [y_pooled, y_pooled], 'k-', linewidth=2)
    diamond_size = 0.3
    ax.add_patch(mpatches.Polygon(
        [[meta_analysis.te_random, y_pooled - diamond_size],
         [meta_analysis.lower_random, y_pooled],
         [meta_analysis.te_random, y_pooled + diamond_size],
         [meta_analysis.upper_random, y_pooled]],
        closed=True, fill=True, facecolor='black', edgecolor='black'
    ))
    
    # Draw the zero effect line
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    
    # Set y-axis labels
    y_labels = list(meta_analysis.study) + ['Total(95% CI)']
    ax.set_yticks(list(y_positions) + [y_pooled])
    ax.set_yticklabels(y_labels, fontsize=10)
    
    # Set x-axis
    ax.set_xlabel('SMD [95% CI]', fontsize=11, fontweight='bold')
    ax.set_xlim(min(meta_analysis.ci_lower.min(), meta_analysis.lower_random) - 0.5,
                max(meta_analysis.ci_upper.max(), meta_analysis.upper_random) + 0.5)
    
    # Add title
    ax.set_title(f'Forest map - {outcome_name}', fontsize=13, fontweight='bold', pad=20)
    
    # beautify
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def generate_forest_data(meta_analysis, outcome_name):
    """Generate forest plot data table"""
    
    # Create rows of data for each study
    forest_data = []
    
    for i in range(len(meta_analysis.study)):
        if meta_analysis.format_type == 'format2':
            row = {
                'Study': meta_analysis.study.iloc[i],
                'Mean.e': meta_analysis.mean_e.iloc[i],
                'SD.e': meta_analysis.sd_e.iloc[i],
                'Total.e': int(meta_analysis.n_e.iloc[i]),
                'Mean.c': meta_analysis.mean_c.iloc[i],
                'SD.c': meta_analysis.sd_c.iloc[i],
                'Total.c': int(meta_analysis.n_c.iloc[i]),
                'SMD': round(meta_analysis.smd.iloc[i], 4),
                '95% CI': f"[{round(meta_analysis.ci_lower.iloc[i], 4)}; {round(meta_analysis.ci_upper.iloc[i], 4)}]",
                '%W(Random)': round(meta_analysis.w_random.iloc[i], 1),
                'P value (pooled)': np.nan
            }
        else:
            row = {
                'study': meta_analysis.study.iloc[i],
                'group1_Mean': meta_analysis.mean_e.iloc[i],
                'group1_SD': meta_analysis.sd_e.iloc[i],
                'group1_sample_size': int(meta_analysis.n_e.iloc[i]),
                'group2_Mean': meta_analysis.mean_c.iloc[i],
                'group2_SD': meta_analysis.sd_c.iloc[i],
                'group2_sample_size': int(meta_analysis.n_c.iloc[i]),
                'SMD': round(meta_analysis.smd.iloc[i], 4),
                '95% CI': f"[{round(meta_analysis.ci_lower.iloc[i], 4)}; {round(meta_analysis.ci_upper.iloc[i], 4)}]",
                '%W(Random)': round(meta_analysis.w_random.iloc[i], 1),
                'P value (pooled)': np.nan
            }
        forest_data.append(row)
    
    # Add merge row
    if meta_analysis.format_type == 'format2':
        pooled_row = {
            'Study': 'Model',
            'Mean.e': np.nan,
            'SD.e': np.nan,
            'Total.e': int(meta_analysis.n_e.sum()),
            'Mean.c': np.nan,
            'SD.c': np.nan,
            'Total.c': int(meta_analysis.n_c.sum()),
            'SMD': round(meta_analysis.te_random, 4),
            '95% CI': f"[{round(meta_analysis.lower_random, 4)}; {round(meta_analysis.upper_random, 4)}]",
            '%W(Random)': 100.0,
            'P value (pooled)': round(meta_analysis.pval_random, 4)
        }
        col_order = ['Study', 'Mean.e', 'SD.e', 'Total.e', 'Mean.c', 'SD.c', 'Total.c', 
                     'SMD', '95% CI', '%W(Random)', 'P value (pooled)']
    else:
        pooled_row = {
            'study': 'Model',
            'group1_Mean': np.nan,
            'group1_SD': np.nan,
            'group1_sample_size': int(meta_analysis.n_e.sum()),
            'group2_Mean': np.nan,
            'group2_SD': np.nan,
            'group2_sample_size': int(meta_analysis.n_c.sum()),
            'SMD': round(meta_analysis.te_random, 4),
            '95% CI': f"[{round(meta_analysis.lower_random, 4)}; {round(meta_analysis.upper_random, 4)}]",
            '%W(Random)': 100.0,
            'P value (pooled)': round(meta_analysis.pval_random, 4)
        }
        col_order = ['study', 'group1_Mean', 'group1_SD', 'group1_sample_size', 'group2_Mean', 
                     'group2_SD', 'group2_sample_size', 'SMD', '95% CI', '%W(Random)', 'P value (pooled)']
    
    forest_data.append(pooled_row)
    
    # Adjust column order
    df = pd.DataFrame(forest_data)
    df = df[col_order]
    
    return df


def print_summary(meta_analysis, outcome_name, study_count, forest_file, csv_file):
    """Summary of output results"""
    
    print("\n" + "═" * 45)
    print("The continuity forest diagram is drawn")
    print("═" * 45 + "\n")
    
    print(f"【Outcome indicators】{outcome_name}")
    print(f"【Included studies】{study_count} item\n")
    
    print("【Output file】")
    print(f"• Forest map：{forest_file}")
    print(f"• data sheet：{csv_file}\n")
    
    print("[Combined effect size]")
    print(f"• SMD = {round(meta_analysis.te_random, 2)} "
          f"[{round(meta_analysis.lower_random, 2)}; "
          f"{round(meta_analysis.upper_random, 2)}]")
    print(f"• Pvalue = {round(meta_analysis.pval_random, 4)}\n")
    
    print("【Heterogeneity】")
    print(f"• I² = {round(meta_analysis.I2 * 100, 2)}%")
    print(f"• Tau² = {round(meta_analysis.tau2, 4)}")
    print(f"• Qtest Pvalue = {round(meta_analysis.pval_Q, 4)}")
    print("═" * 45 + "\n")


def main():
    """main function"""
    
    # Parse command line parameters
    if len(sys.argv) < 2:
        print("Usage: python forest_continuous.py <csv_path> [outcome_name] [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    outcome_name = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[2] else None
    output_dir = sys.argv[3] if len(sys.argv) >= 4 and sys.argv[3] else os.path.dirname(csv_path)
    
    # Verify file exists
    if not os.path.exists(csv_path):
        print(f"mistake: File does not exist: {csv_path}")
        sys.exit(1)
    
    try:
        # Read data
        data_df = pd.read_csv(csv_path)
        
        # Get the outcome indicator name
        if outcome_name is None:
            if 'outcome_new' in data_df.columns:
                outcome_name = data_df['outcome_new'].iloc[0]
            else:
                outcome_name = 'Outcome'
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Meta-analysis
        meta_analysis = MetaAnalysis(data_df)
        
        # Generate output file path
        forest_file = os.path.join(output_dir, f"Continuity_forest_{outcome_name}.png")
        csv_file = os.path.join(output_dir, f"Continuity_forest_{outcome_name}.csv")
        
        # Draw a forest map
        draw_forest_plot(meta_analysis, outcome_name, forest_file)
        
        # Generate data table
        forest_data = generate_forest_data(meta_analysis, outcome_name)
        forest_data.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # Output summary
        print_summary(meta_analysis, outcome_name, len(meta_analysis.study), 
                     forest_file, csv_file)
        
    except Exception as e:
        print(f"mistake: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
