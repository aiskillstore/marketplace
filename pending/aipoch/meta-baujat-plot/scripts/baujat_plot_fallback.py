#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baujat diagram drawing script (Python supplementary solution)
Use this script to plot when R execution fails
Usage: python baujat_plot_fallback.py <csv_path> <type> [outcome_name] [output_dir]"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# Set Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def parse_args():
    """Parse command line parameters"""
    if len(sys.argv) < 3:
        print("Usage: python baujat_plot_fallback.py <csv_path> <type> [outcome_name] [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    data_type = sys.argv[2]
    outcome_name = sys.argv[3] if len(sys.argv) >= 4 and sys.argv[3] else ""
    output_dir = sys.argv[4] if len(sys.argv) >= 5 else os.path.dirname(csv_path)
    
    if data_type not in ["Binary", "Continuity", "Survival"]:
        print("Error: type must be Binary, Continuity or Survival")
        sys.exit(1)
    
    return csv_path, data_type, outcome_name, output_dir


def load_data(csv_path, data_type):
    """Load and validate data"""
    if not os.path.exists(csv_path):
        print(f"mistake: File does not exist: {csv_path}")
        sys.exit(1)
    
    df = pd.read_csv(csv_path)
    
    if df.shape[0] < 3:
        print("Wrong: At least 3 studies are required for valid heterogeneity analysis")
        sys.exit(1)
    
    return df


def or_from_binary(events_e, n_e, events_c, n_c):
    """Calculate the OR value and 95% CI of binary data"""
    # Mantel-Haenszel OR
    p_e = (events_e + 1) / (n_e + 2)  # Add smoothing
    p_c = (events_c + 1) / (n_c + 2)
    
    or_val = (p_e / (1 - p_e)) / (p_c / (1 - p_c))
    
    # standard error
    se_log_or = np.sqrt(1/(events_e+0.5) + 1/(n_e-events_e+0.5) + 
                        1/(events_c+0.5) + 1/(n_c-events_c+0.5))
    
    ci_lower = np.exp(np.log(or_val) - 1.96 * se_log_or)
    ci_upper = np.exp(np.log(or_val) + 1.96 * se_log_or)
    
    return or_val, se_log_or, ci_lower, ci_upper


def calculate_baujat_binary(df):
    """Calculate Baujat data for Binary data"""
    studies = df['study'].tolist()
    n = len(studies)
    
    # Extract data
    events_e = df['group1_Events'].astype(float).values
    n_e = df['group1_sample_size'].astype(float).values
    events_c = df['group2_Events'].astype(float).values
    n_c = df['group2_sample_size'].astype(float).values
    
    # Calculate OR for all studies
    all_or = []
    all_se = []
    for i in range(n):
        or_val, se, _, _ = or_from_binary(events_e[i], n_e[i], events_c[i], n_c[i])
        all_or.append(np.log(or_val))
        all_se.append(se)
    
    all_or = np.array(all_or)
    all_se = np.array(all_se)
    
    # Calculate summary effect size (random effects)
    weights = 1 / (all_se ** 2)
    te_pool = np.sum(weights * all_or) / np.sum(weights)
    
    # Calculate the Q statistic
    q_total = np.sum(weights * (all_or - te_pool) ** 2)
    
    # Baujat data
    x_vals = []  # Contribution to results
    y_vals = []  # Contributions to Q
    
    for i in range(n):
        # Leave-one-out analysis
        idx = np.array([j for j in range(n) if j != i])
        w_loo = weights[idx]
        te_loo = np.sum(w_loo * all_or[idx]) / np.sum(w_loo)
        q_loo = np.sum(w_loo * (all_or[idx] - te_loo) ** 2)
        
        # Contribution to results
        x = (te_pool - te_loo) ** 2
        x_vals.append(x)
        
        # Contributions to Q
        y = q_total - q_loo
        y_vals.append(y)
    
    # Calculate I² and Tau²
    q_df = n - 1
    c = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (q_total - q_df) / c)
    
    i2 = max(0, 100 * (q_total - q_df) / q_total)
    
    return {
        'studies': studies,
        'x': np.array(x_vals),
        'y': np.array(y_vals),
        'q_total': q_total,
        'q_df': q_df,
        'i2': i2,
        'tau2': tau2,
        'p_value': 1 - stats.chi2.cdf(q_total, q_df)
    }


def plot_baujat(baujat_data, output_path, outcome_name=""):
    """Draw a Baujat diagram"""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    x = baujat_data['x']
    y = baujat_data['y']
    studies = baujat_data['studies']
    
    # Plot scatter points
    colors = ['#e74c3c' if (y_val > np.percentile(y, 75) and x_val > np.percentile(x, 75)) 
              else '#3498db' for x_val, y_val in zip(x, y)]
    
    ax.scatter(x, y, s=150, alpha=0.6, c=colors, edgecolors='black', linewidth=1)
    
    # Add tag
    for i, study in enumerate(studies):
        ax.annotate(study, (x[i], y[i]), 
                   textcoords="offset points", xytext=(0,10),
                   ha='center', fontsize=9, fontweight='bold')
    
    # Add midline
    x_med = np.median(x)
    y_med = np.median(y)
    ax.axvline(x_med, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.axhline(y_med, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    # Tags and titles
    ax.set_xlabel('Contribution to Overall Result (Squared Pearson Residuals)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Contribution to Heterogeneity (Q Statistic)', fontsize=11, fontweight='bold')
    
    if outcome_name:
        ax.set_title(f'Baujat Plot for Heterogeneity Analysis\n({outcome_name})', 
                    fontsize=12, fontweight='bold', pad=20)
    else:
        ax.set_title('Baujat Plot for Heterogeneity Analysis', 
                    fontsize=12, fontweight='bold', pad=20)
    
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Chart saved: {output_path}")


def save_baujat_data(baujat_data, output_path):
    """Save Baujat contribution data"""
    df_out = pd.DataFrame({
        'study': baujat_data['studies'],
        'contribution_to_result': baujat_data['x'],
        'contribution_to_heterogeneity': baujat_data['y']
    })
    
    # Sort by heterogeneity contribution
    df_out = df_out.sort_values('contribution_to_heterogeneity', ascending=False).reset_index(drop=True)
    df_out['rank'] = range(1, len(df_out) + 1)
    
    df_out.to_csv(output_path, index=False)
    print(f"Data saved: {output_path}")


def print_summary(baujat_data, data_type, outcome_name=""):
    """Print analysis summary"""
    print("\n" + "=" * 51)
    print("Baujat diagram is drawn")
    print("=" * 51)
    print(f"\n【Outcome indicators】{outcome_name if outcome_name else '.'}")
    print(f"【data type】{data_type}")
    print(f"【Included studies】{len(baujat_data['studies'])} item")
    print("【Heterogeneity Statistics】")
    print(f"• I² = {baujat_data['i2']:.2f}%")
    print(f"• Tau² = {baujat_data['tau2']:.4f}")
    print(f"• Q = {baujat_data['q_total']:.2f}, df = {baujat_data['q_df']}, P = {baujat_data['p_value']:.4f}")
    
    # Print ranking
    print("[Ranking of heterogeneity contribution] (in descending order of contribution to Q)")
    print("Ranking Research Result Contribution Q Contribution Judgment")
    print("─" * 55)
    
    y_threshold = np.percentile(baujat_data['y'], 75)
    x_threshold = np.percentile(baujat_data['x'], 75)
    
    sorted_idx = np.argsort(-baujat_data['y'])
    for rank, idx in enumerate(sorted_idx, 1):
        study = baujat_data['studies'][idx]
        x_val = baujat_data['x'][idx]
        y_val = baujat_data['y'][idx]
        
        is_outlier = y_val > y_threshold and x_val > x_threshold
        marker = "⚠️ Outlier" if is_outlier else "normal"
        
        study_short = study[:18] if len(study) > 18 else study
        print(f"{rank}     {study_short:18s}   {x_val:7.4f}       {y_val:7.4f}     {marker}")
    
    print("【suggestion】")
    outlier_studies = []
    for idx in sorted_idx:
        if baujat_data['y'][idx] > y_threshold and baujat_data['x'][idx] > x_threshold:
            outlier_studies.append(baujat_data['studies'][idx])
    
    if outlier_studies:
        print(f"• Discover{len(outlier_studies)}potential outlier studies：{', '.join(outlier_studies[:3])}")
        print("• It is recommended to conduct a sensitivity analysis to assess whether the results are robust after excluding this study.")
    else:
        print("• No obvious outlier studies were found, and the data quality is good.")
    
    print("=" * 51 + "\n")


def main():
    csv_path, data_type, outcome_name, output_dir = parse_args()
    
    # Process output directory
    if output_dir == "." or output_dir == "":
        output_dir = os.getcwd()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    df = load_data(csv_path, data_type)
    
    # Calculate Baujat data
    if data_type == "Binary":
        baujat_data = calculate_baujat_binary(df)
    else:
        print(f"mistake: PythonSupplementary plans are not supported yet {data_type} type")
        sys.exit(1)
    
    # Generate output file name
    filename_base = f"{data_type}_baujat_{outcome_name if outcome_name else '.'}"
    png_path = os.path.join(output_dir, f"{filename_base}.png")
    csv_path_out = os.path.join(output_dir, f"{filename_base}.csv")
    
    # Draw charts
    plot_baujat(baujat_data, png_path, outcome_name)
    
    # save data
    save_baujat_data(baujat_data, csv_path_out)
    
    # Print summary
    print_summary(baujat_data, data_type, outcome_name)


if __name__ == "__main__":
    main()
