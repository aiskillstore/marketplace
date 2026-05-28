#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Survival data forest plot drawing script (Python version)
Usage: python forest_survival.py <csv_path> [outcome_name] [output_dir]"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from datetime import datetime

# Set Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def get_column(df, candidates):
    """Get columns (supports multiple column name formats)"""
    for col in candidates:
        if col in df.columns:
            return df[col]
    return None

def read_data(csv_path):
    """Read CSV file"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File does not exist: {csv_path}")
    
    data_df = pd.read_csv(csv_path)
    
    # Check required columns
    if "study" not in data_df.columns:
        raise ValueError("Missing required column: study")
    
    # Trying to read the HR column
    hr_col = get_column(data_df, ["group1_HR", "HR"])
    if hr_col is None:
        raise ValueError("Missing required column: group1_HR or HR")
    
    # Try to read lower bound column
    lower_col = get_column(data_df, [
        "group1_95%Lower CI", "group1_95.Lower.CI", "lower"
    ])
    if lower_col is None:
        raise ValueError("Missing required column: group1_95%Lower CI or group1_95.Lower.CI")
    
    # Try to read upper bound column
    upper_col = get_column(data_df, [
        "group1_95%Upper CI", "group1_95.Upper.CI", "upper"
    ])
    if upper_col is None:
        raise ValueError("Missing required column: group1_95%Upper CI or group1_95.Upper.CI")
    
    # Get the outcome indicator name
    outcome_name = None
    if "outcome_new" in data_df.columns:
        outcome_name = data_df["outcome_new"].iloc[0]
    
    return data_df, hr_col, lower_col, upper_col, outcome_name

def calculate_meta_analysis(study, hr, lower, upper):
    """Compute meta-analysis statistics"""
    # Logarithmic transformation
    log_hr = np.log(hr)
    
    # Calculate standard error
    se = (np.log(upper) - np.log(lower)) / (2 * 1.96)
    
    # Calculate weight (inverse variance)
    weights = 1 / (se ** 2)
    weights = weights / weights.sum()  # standardization
    
    # Pooled effect size (fixed effects)
    pooled_log_hr = np.sum(weights * log_hr)
    pooled_hr = np.exp(pooled_log_hr)
    
    # Combined confidence intervals
    var_pooled = 1 / np.sum(1 / (se ** 2))
    se_pooled = np.sqrt(var_pooled)
    pooled_lower = np.exp(pooled_log_hr - 1.96 * se_pooled)
    pooled_upper = np.exp(pooled_log_hr + 1.96 * se_pooled)
    
    # P value (pooled effect size)
    z_score = pooled_log_hr / se_pooled
    p_value = 2 * (1 - stats.norm.cdf(np.abs(z_score)))
    
    # I² Heterogeneity
    q_value = np.sum((1 / (se ** 2)) * (log_hr - pooled_log_hr) ** 2)
    df = len(study) - 1
    p_value_q = 1 - stats.chi2.cdf(q_value, df)
    
    if q_value > df:
        i2 = (q_value - df) / q_value * 100
    else:
        i2 = 0
    
    # Tau²
    if i2 > 0:
        tau2 = (q_value - df) / (np.sum(1 / (se ** 2)) - np.sum((1 / (se ** 2)) ** 2) / np.sum(1 / (se ** 2)))
        tau2 = max(0, tau2)  # cannot be negative
    else:
        tau2 = 0
    
    return {
        'pooled_hr': pooled_hr,
        'pooled_lower': pooled_lower,
        'pooled_upper': pooled_upper,
        'p_value': p_value,
        'i2': i2,
        'tau2': tau2,
        'p_value_q': p_value_q,
        'weights': weights * 100,
        'log_hr': log_hr,
        'se': se
    }

def draw_forest_plot(study, hr, lower, upper, meta_stats, outcome_name, output_file):
    """Draw a forest map"""
    n_studies = len(study)
    
    # drawing parameters
    fig, ax = plt.subplots(figsize=(12, 4 + n_studies * 0.6))
    
    # Y coordinate
    y_positions = np.arange(n_studies, 0, -1)
    pooled_y = 0
    
    # Plot HR and confidence intervals for each study
    for i, (s, h, l, u) in enumerate(zip(study, hr, lower, upper)):
        y = y_positions[i]
        
        # Confidence interval line
        ax.plot([l, u], [y, y], 'k-', linewidth=1.5, zorder=2)
        
        # HR point
        ax.plot(h, y, 'o', color='red', markersize=8, zorder=3)
    
    # Plot pooled effect size
    pooled_hr = meta_stats['pooled_hr']
    pooled_lower = meta_stats['pooled_lower']
    pooled_upper = meta_stats['pooled_upper']
    
    ax.plot([pooled_lower, pooled_upper], [pooled_y, pooled_y], 'k-', linewidth=2.5, zorder=2)
    ax.plot(pooled_hr, pooled_y, 's', color='black', markersize=10, zorder=3)
    
    # Add dashed line (reference line HR=1)
    ax.axvline(x=1, color='gray', linestyle='--', linewidth=1, alpha=0.7, zorder=1)
    
    # Set Y-axis labels
    y_labels = list(study) + ['merger effect']
    ax.set_yticks(list(y_positions) + [pooled_y])
    ax.set_yticklabels(y_labels, fontsize=10)
    
    # Set X-axis
    ax.set_xlabel('Hazard ratio (HR) [log scale]', fontsize=11, fontweight='bold')
    ax.set_xscale('log')
    
    # Set X-axis limits and scale
    x_min = min(np.min(lower), pooled_lower) * 0.6
    x_max = max(np.max(upper), pooled_upper) * 1.5
    ax.set_xlim(x_min, x_max)
    
    # Titles and tags
    title = f"Survival Data Forest Chart - {outcome_name}"
    ax.set_title(title, fontsize=13, fontweight='bold', pad=20)
    
    # Hide top and right borders
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # Add grid
    ax.grid(axis='x', alpha=0.3, linestyle=':', zorder=0)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Forest map saved: {output_file}")
    plt.close()

def save_results_csv(study, hr, lower, upper, meta_stats, outcome_name, output_file):
    """Save results as CSV"""
    results = {
        'Study': list(study) + ['Model'],
        'HR': list(hr) + [f"{meta_stats['pooled_hr']:.2f}"],
        '95% CI': [f"[{l:.2f}; {u:.2f}]" for l, u in zip(lower, upper)] + 
                  [f"[{meta_stats['pooled_lower']:.2f}; {meta_stats['pooled_upper']:.2f}]"],
        '%W(Random)': list(meta_stats['weights']) + [100],
        'P value (pooled)': [np.nan] * len(study) + [meta_stats['p_value']],
        'logHR': list(meta_stats['log_hr']) + [np.nan],
        'SE': list(meta_stats['se']) + [np.nan]
    }
    
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data table saved: {output_file}")

def main():
    """main program"""
    # Parse command line parameters
    if len(sys.argv) < 2:
        print("Usage: python forest_survival.py <csv_path> [outcome_name] [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    outcome_name = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[2] else None
    output_dir = sys.argv[3] if len(sys.argv) >= 4 and sys.argv[3] else os.path.dirname(csv_path) or "."
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read data
        print(f"Read data: {csv_path}")
        data_df, hr_col, lower_col, upper_col, outcome_from_data = read_data(csv_path)
        
        # Set outcome indicator name
        if outcome_name is None:
            outcome_name = outcome_from_data or "Survival"
        
        # Extract data
        study = data_df['study'].values
        hr = pd.to_numeric(hr_col, errors='coerce').values
        lower = pd.to_numeric(lower_col, errors='coerce').values
        upper = pd.to_numeric(upper_col, errors='coerce').values
        
        # Validate data
        valid_idx = ~(np.isnan(hr) | np.isnan(lower) | np.isnan(upper)) & (hr > 0) & (lower > 0) & (upper > 0)
        
        if np.sum(valid_idx) < 2:
            raise ValueError(f"{outcome_name} Insufficient valid data on outcome variables，Unable to merge！")
        
        # Filter valid data
        study = study[valid_idx]
        hr = hr[valid_idx]
        lower = lower[valid_idx]
        upper = upper[valid_idx]
        
        # Compute meta-analysis statistics
        print(f"Compute meta-analysis statistics...")
        meta_stats = calculate_meta_analysis(study, hr, lower, upper)
        
        # Generate output file path
        safe_outcome = outcome_name.replace(" ", "_").replace("/", "_")
        forest_file = os.path.join(output_dir, f"Survival_forest_{safe_outcome}.png")
        csv_file = os.path.join(output_dir, f"Survival_forest_{safe_outcome}.csv")
        
        # Draw a forest map
        print(f"Draw a forest map...")
        draw_forest_plot(study, hr, lower, upper, meta_stats, outcome_name, forest_file)
        
        # Save results CSV
        print(f"Save result data...")
        save_results_csv(study, hr, lower, upper, meta_stats, outcome_name, csv_file)
        
        # Summary of output results
        print("\n" + "=" * 43)
        print("The survival forest map is drawn")
        print("=" * 43 + "\n")
        print(f"【Outcome indicators】{outcome_name}")
        print(f"【Included studies】{len(study)} item\n")
        print("【Output file】")
        print(f"• Forest map：{forest_file}")
        print(f"• data sheet：{csv_file}\n")
        print("[Combined effect size]")
        print(f"• HR = {meta_stats['pooled_hr']:.2f} [{meta_stats['pooled_lower']:.2f}; {meta_stats['pooled_upper']:.2f}]")
        print(f"• Pvalue = {meta_stats['p_value']:.4f}\n")
        print("【Heterogeneity】")
        print(f"• I² = {meta_stats['i2']:.2f}%")
        print(f"• Tau² = {meta_stats['tau2']:.4f}")
        print(f"• Qtest Pvalue = {meta_stats['p_value_q']:.4f}")
        print("=" * 43 + "\n")
        
    except Exception as e:
        print(f"mistake: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
