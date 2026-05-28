#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Funnel plot drawing and publication bias test script (Python version)
Usage: python funnel_plot.py <csv_path> <type> [outcome_name] [output_dir]"""

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
        print("Usage: python funnel_plot.py <csv_path> <type> [outcome_name] [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    data_type = sys.argv[2]
    outcome_name = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else "Outcome"
    output_dir = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else os.path.dirname(csv_path)
    
    if data_type not in ["Binary", "Continuity", "Survival"]:
        print("type must be Binary, Continuity or Survival")
        sys.exit(1)
    
    return csv_path, data_type, outcome_name, output_dir

def read_data(csv_path):
    """Read CSV data"""
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Failed to read file: {e}")
        sys.exit(1)

def calculate_binary_effect(group1_events, group1_n, group2_events, group2_n):
    """Calculate odds ratios and standard errors for binary data"""
    group1_n_events = group1_n - group1_events
    group2_n_events = group2_n - group2_events
    
    # Calculate OR and 95%CI
    or_value = (group1_events * group2_n_events) / (group1_n_events * group2_events)
    se_log_or = np.sqrt(1/group1_events + 1/group1_n_events + 1/group2_events + 1/group2_n_events)
    
    log_or = np.log(or_value)
    se = se_log_or
    
    return log_or, se, or_value

def calculate_continuity_effect(n1, mean1, sd1, n2, mean2, sd2):
    """Calculate the standardized mean difference for continuous data"""
    pooled_sd = np.sqrt(((n1-1)*sd1**2 + (n2-1)*sd2**2) / (n1 + n2 - 2))
    smd = (mean1 - mean2) / pooled_sd
    se = np.sqrt(1/n1 + 1/n2 + smd**2 / (2*(n1+n2)))
    
    return smd, se

def calculate_survival_effect(hr, ci_lower, ci_upper):
    """Processing survival data"""
    log_hr = np.log(hr)
    se_log_hr = (np.log(ci_upper) - np.log(ci_lower)) / (2 * 1.96)
    
    return log_hr, se_log_hr

def egger_test(log_effects, ses):
    """Egger linear regression test"""
    precision = 1 / np.array(ses)
    
    # linear regression
    x = precision
    y = np.array(log_effects) * precision
    
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean)**2)
    intercept = y_mean - slope * x_mean
    
    # Calculate residuals and standard errors
    y_pred = intercept + slope * x
    residuals = y - y_pred
    mse = np.sum(residuals**2) / (n - 2)
    se_intercept = np.sqrt(mse * (1/n + x_mean**2 / np.sum((x - x_mean)**2)))
    
    # t-test
    t_stat = intercept / se_intercept
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
    
    return intercept, se_intercept, t_stat, p_value

def begg_test(log_effects, ses):
    """Begg rank correlation test"""
    try:
        from scipy.stats import kendalltau
        
        # Calculate Kendall's tau
        tau, p_value = kendalltau(log_effects, ses)
        
        # Calculate z value
        n = len(log_effects)
        z_stat = tau * np.sqrt(2 * (2*n + 5) / (9*n*(n-1)))
        
        return tau, z_stat, p_value
    except:
        return 0, 0, 1.0

def trim_and_fill(log_effects, ses):
    """Cut and complement analysis"""
    n = len(log_effects)
    sorted_effects = np.sort(log_effects)
    
    # A simple estimate of the number of imputed studies
    if n > 2:
        center = np.median(log_effects)
        filled_studies = sum(1 for e in log_effects if e < center) - sum(1 for e in log_effects if e > center)
        filled_studies = max(0, filled_studies)
    else:
        filled_studies = 0
    
    # Calculate pooled effect size (simple weighted average)
    weights = 1 / np.array(ses)**2
    pooled_effect_before = np.sum(np.array(log_effects) * weights) / np.sum(weights)
    
    if filled_studies > 0:
        # Add filled studies
        augmented_effects = list(log_effects) + [np.median(log_effects)] * filled_studies
        augmented_ses = list(ses) + [np.median(ses)] * filled_studies
        weights_after = 1 / np.array(augmented_ses)**2
        pooled_effect_after = np.sum(np.array(augmented_effects) * weights_after) / np.sum(weights_after)
    else:
        pooled_effect_after = pooled_effect_before
    
    return pooled_effect_before, pooled_effect_after, filled_studies

def plot_funnel(log_effects, ses, outcome_name, output_path, data_type):
    """Draw a funnel chart"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Calculate 95% and 97.5% confidence interval bounds
    x_max = max(1/np.array(ses)) * 1.1
    x = np.linspace(0, x_max, 100)
    y_95 = 1.96 * x
    y_975 = 1.96 * x
    
    # Draw confidence intervals
    ax.fill_between(x, -y_95, y_95, alpha=0.1, color='blue', label='95% CI')
    ax.plot(x, y_95, 'b--', alpha=0.5, linewidth=1)
    ax.plot(x, -y_95, 'b--', alpha=0.5, linewidth=1)
    
    # Draw study points
    colors = ['red' if se > np.median(ses) else 'blue' for se in ses]
    ax.scatter(1/np.array(ses), log_effects, alpha=0.6, s=100, c=colors)
    
    # Draw merged effect lines
    pooled = np.sum(np.array(log_effects) / np.array(ses)**2) / np.sum(1 / np.array(ses)**2)
    ax.axvline(pooled, color='red', linestyle='-', linewidth=2, label='Pooled Effect')
    ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
    
    # Set labels and titles
    ax.set_xlabel('1 / Standard Error (Precision)', fontsize=12)
    ax.set_ylabel('log(Effect Size)', fontsize=12)
    ax.set_title(f'Funnel Plot - {outcome_name}', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """main program"""
    csv_path, data_type, outcome_name, output_dir = parse_args()
    
    # Verify file exists
    if not os.path.exists(csv_path):
        print(f"File does not exist: {csv_path}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read data
    df = read_data(csv_path)
    
    # Verification data volume
    if len(df) < 2:
        print("At least 2 studies are required to draw a funnel plot")
        sys.exit(1)
    
    # Process data according to type
    log_effects = []
    ses = []
    study_names = df['study'].tolist()
    
    try:
        if data_type == "Binary":
            required_cols = ['group1_Events', 'group1_sample_size', 'group2_Events', 'group2_sample_size']
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                print(f"Missing required column: {', '.join(missing)}")
                sys.exit(1)
            
            for idx, row in df.iterrows():
                log_or, se, or_value = calculate_binary_effect(
                    row['group1_Events'], row['group1_sample_size'],
                    row['group2_Events'], row['group2_sample_size']
                )
                log_effects.append(log_or)
                ses.append(se)
        
        elif data_type == "Continuity":
            required_cols = ['group1_sample_size', 'group1_Mean', 'group1_SD', 
                           'group2_sample_size', 'group2_Mean', 'group2_SD']
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                print(f"Missing required column: {', '.join(missing)}")
                sys.exit(1)
            
            for idx, row in df.iterrows():
                smd, se = calculate_continuity_effect(
                    row['group1_sample_size'], row['group1_Mean'], row['group1_SD'],
                    row['group2_sample_size'], row['group2_Mean'], row['group2_SD']
                )
                log_effects.append(smd)
                ses.append(se)
        
        elif data_type == "Survival":
            required_cols = ['group1_HR', 'group1_95%Lower CI', 'group1_95%Upper CI']
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                print(f"Missing required column: {', '.join(missing)}")
                sys.exit(1)
            
            for idx, row in df.iterrows():
                log_hr, se_log_hr = calculate_survival_effect(
                    row['group1_HR'], row['group1_95%Lower CI'], row['group1_95%Upper CI']
                )
                log_effects.append(log_hr)
                ses.append(se_log_hr)
    
    except Exception as e:
        print(f"Data processing failed: {e}")
        sys.exit(1)
    
    log_effects = np.array(log_effects)
    ses = np.array(ses)
    
    # Perform statistical tests
    egger_intercept, egger_se, egger_t, egger_p = egger_test(log_effects, ses)
    begg_tau, begg_z, begg_p = begg_test(log_effects, ses)
    pooled_before, pooled_after, filled_n = trim_and_fill(log_effects, ses)
    
    # Convert back to original effect size
    if data_type == "Binary":
        or_before = np.exp(pooled_before)
        or_after = np.exp(pooled_after)
        ci_before = (np.exp(pooled_before - 1.96 * np.sqrt(np.sum(1/ses**2))**-1), 
                    np.exp(pooled_before + 1.96 * np.sqrt(np.sum(1/ses**2))**-1))
        ci_after = (np.exp(pooled_after - 1.96 * np.sqrt(np.sum(1/ses**2))**-1),
                   np.exp(pooled_after + 1.96 * np.sqrt(np.sum(1/ses**2))**-1))
    else:
        or_before = or_after = ci_before = ci_after = None
    
    # Save results
    base_name = f"{data_type}_funnel_{outcome_name}"
    
    # Draw a funnel chart
    plot_funnel(log_effects, ses, outcome_name, os.path.join(output_dir, f"{base_name}.png"), data_type)
    
    # Save funnel chart data
    funnel_data = pd.DataFrame({
        'study': study_names,
        'log_effect': log_effects,
        'se': ses,
        'precision': 1/ses
    })
    funnel_data.to_csv(os.path.join(output_dir, f"{base_name}.csv"), index=False)
    
    # Save Egger test results
    egger_data = pd.DataFrame({
        'Test': ['Egger Linear Regression'],
        'Intercept': [egger_intercept],
        'SE': [egger_se],
        't_value': [egger_t],
        'p_value': [egger_p]
    })
    egger_data.to_csv(os.path.join(output_dir, f"{data_type}_Egger_{outcome_name}.csv"), index=False)
    
    # Save Begg test results
    begg_data = pd.DataFrame({
        'Test': ['Begg Rank Correlation'],
        'Kendall_tau': [begg_tau],
        'z_value': [begg_z],
        'p_value': [begg_p]
    })
    begg_data.to_csv(os.path.join(output_dir, f"{data_type}_Begg_{outcome_name}.csv"), index=False)
    
    # Output results
    print("\n" + "═"*50)
    print("Funnel plot drawing and publication bias test completed")
    print("═"*50 + "\n")
    
    print(f"【Outcome indicators】{outcome_name}")
    print(f"【data type】{data_type}")
    print(f"【Included studies】{len(df)} item\n")
    
    print("【Output file】")
    print(f"• funnel chart：{os.path.join(output_dir, f'{base_name}.png')}")
    print(f"• funnel data：{os.path.join(output_dir, f'{base_name}.csv')}")
    print(f"• Eggertest：{os.path.join(output_dir, f'{data_type}_Egger_{outcome_name}.csv')}")
    print(f"• Beggtest：{os.path.join(output_dir, f'{data_type}_Begg_{outcome_name}.csv')}\n")
    
    print("[Publication bias test results]")
    print("Egger linear regression test:")
    print(f"• intercept = {egger_intercept:.4f} (SE = {egger_se:.4f})")
    print(f"• tvalue = {egger_t:.4f}")
    print(f"• Pvalue = {egger_p:.4f}")
    print(f"• in conclusion：{'Significant publication bias' if egger_p < 0.05 else 'No significant publication bias'}\n")
    
    print("Begg rank correlation test:")
    print(f"• Kendall's tau = {begg_tau:.4f}")
    print(f"• zvalue = {begg_z:.4f}")
    print(f"• Pvalue = {begg_p:.4f}")
    print(f"• in conclusion：{'Significant publication bias' if begg_p < 0.05 else 'No significant publication bias'}\n")
    
    if data_type == "Binary" and or_before and or_after:
        print("[Analysis of cut and fill method]")
        print(f"• Before trimming：{or_before:.2f} [{ci_before[0]:.2f}; {ci_before[1]:.2f}]")
        print(f"• After trimming：{or_after:.2f} [{ci_after[0]:.2f}; {ci_after[1]:.2f}]")
        print(f"• Fill in the number of studies：{filled_n}\n")
    
    print("═"*50)

if __name__ == "__main__":
    main()
