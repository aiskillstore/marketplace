#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Radial Plot / Galbraith Plot backup drawing script (Python version)
Purpose: Use Python for backup drawing when R execution fails
Usage: python radial_plot_backup.py <csv_path> <type> [outcome_name] [output_dir]"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy import stats
from pathlib import Path

# Set Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RadialPlotGenerator:
    """Star chart generator"""
    
    def __init__(self, csv_path, data_type, outcome_name=None, output_dir=None):
        self.csv_path = csv_path
        self.data_type = data_type
        self.outcome_name = outcome_name or "Outcome"
        self.output_dir = output_dir or os.path.dirname(csv_path) or "."
        
        # Verify file
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"File does not exist: {csv_path}")
        
        # Verification type
        if data_type not in ["Binary", "Continuity", "Survival"]:
            raise ValueError("data_type must be Binary, Continuity or Survival")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.data = None
        self.radial_data = None
        self.meta_results = {}
        
    def load_data(self):
        """Load CSV data"""
        self.data = pd.read_csv(self.csv_path)
        
        if len(self.data) < 3:
            raise ValueError("At least 3 studies are required for valid heterogeneity analysis")
        
        print(f"✓ Loaded {len(self.data)} research data")
        
    def validate_columns(self):
        """Validate necessary columns"""
        if self.data_type == "Binary":
            required = ["study", "group1_Events", "group1_sample_size",
                       "group2_Events", "group2_sample_size"]
        elif self.data_type == "Continuity":
            required = ["study", "group1_sample_size", "group1_Mean", "group1_SD",
                       "group2_sample_size", "group2_Mean", "group2_SD"]
        elif self.data_type == "Survival":
            required = ["study", "group1_HR", "group1_95%Lower CI", "group1_95%Upper CI"]
        
        missing = [col for col in required if col not in self.data.columns]
        if missing:
            raise ValueError(f"Missing required column: {', '.join(missing)}")
        
        print(f"✓ Data column verification passed")
        
    def calculate_binary(self):
        """Binary classification data analysis"""
        data = self.data
        
        # Extract data
        a1 = data['group1_Events'].astype(float)  # Number of events in treatment group
        n1 = data['group1_sample_size'].astype(float)  # Treatment group sample size
        a0 = data['group2_Events'].astype(float)  # Number of events in the control group
        n0 = data['group2_sample_size'].astype(float)  # Control sample size
        
        # Calculate Mantel-Haenszel type effect size (log OR) and SE
        # OR = (a1*b0) / (a0*b1), where b1 = n1-a1, b0 = n0-a0
        b1 = n1 - a1
        b0 = n0 - a0
        
        or_values = (a1 * b0) / (a0 * b1)
        log_or = np.log(or_values)
        
        # Calculate standard error
        se = np.sqrt(1/a1 + 1/b1 + 1/a0 + 1/b0)
        
        # Calculate 95% CI
        z_crit = 1.96
        ci_lower = np.exp(log_or - z_crit * se)
        ci_upper = np.exp(log_or + z_crit * se)
        
        self.radial_data = pd.DataFrame({
            'study': data['study'],
            'effect': log_or,
            'se': se,
            'or_value': or_values
        })
        
        self.meta_results['effect_name'] = 'log(OR)'
        self.meta_results['display_name'] = 'OR'
        self.meta_results['ci_lower'] = ci_lower
        self.meta_results['ci_upper'] = ci_upper
        
    def calculate_continuity(self):
        """continuous data analysis"""
        data = self.data
        
        # Extract data
        n1 = data['group1_sample_size'].astype(float)
        m1 = data['group1_Mean'].astype(float)
        s1 = data['group1_SD'].astype(float)
        
        n0 = data['group2_sample_size'].astype(float)
        m0 = data['group2_Mean'].astype(float)
        s0 = data['group2_SD'].astype(float)
        
        # Calculate pooling standard deviation
        s_pool = np.sqrt(((n1-1)*s1**2 + (n0-1)*s0**2) / (n1 + n0 - 2))
        
        # Calculate SMD (Cohen's d)
        smd = (m1 - m0) / s_pool
        
        # Calculate standard error
        se = np.sqrt(1/n1 + 1/n0 + s_pool**2 / (2 * (n1 + n0)))
        
        # Calculate 95% CI
        z_crit = 1.96
        ci_lower = smd - z_crit * se
        ci_upper = smd + z_crit * se
        
        self.radial_data = pd.DataFrame({
            'study': data['study'],
            'effect': smd,
            'se': se
        })
        
        self.meta_results['effect_name'] = 'SMD'
        self.meta_results['display_name'] = 'SMD'
        self.meta_results['ci_lower'] = ci_lower
        self.meta_results['ci_upper'] = ci_upper
        
    def calculate_survival(self):
        """Survival analysis data"""
        data = self.data
        
        try:
            hr = data['group1_HR'].astype(float)
            # Try 2 column name formats
            if 'group1_95%Lower CI' in data.columns:
                lower_ci = data['group1_95%Lower CI'].astype(float)
                upper_ci = data['group1_95%Upper CI'].astype(float)
            else:
                lower_ci = data['group1_95.Lower.CI'].astype(float)
                upper_ci = data['group1_95.Upper.CI'].astype(float)
        except:
            raise ValueError("Required columns are missing or data is in the wrong format")
        
        # Validate data
        valid_mask = ~(np.isnan(hr) | np.isnan(lower_ci) | np.isnan(upper_ci)) & \
                     (hr > 0) & (lower_ci > 0) & (upper_ci > 0)
        
        if valid_mask.sum() < 3:
            raise ValueError("There are less than 3 valid data items and heterogeneity analysis cannot be performed.")
        
        log_hr = np.log(hr[valid_mask])
        
        # Calculate SE from CI
        se = (np.log(upper_ci[valid_mask]) - np.log(lower_ci[valid_mask])) / (2 * 1.96)
        
        self.radial_data = pd.DataFrame({
            'study': data['study'][valid_mask].values,
            'effect': log_hr,
            'se': se,
            'hr_value': hr[valid_mask]
        })
        
        self.meta_results['effect_name'] = 'log(HR)'
        self.meta_results['display_name'] = 'HR'
        self.meta_results['ci_lower'] = np.exp(log_hr - 1.96 * se)
        self.meta_results['ci_upper'] = np.exp(log_hr + 1.96 * se)
        
    def calculate_heterogeneity(self):
        """Calculate heterogeneity index"""
        effects = self.radial_data['effect'].values
        ses = self.radial_data['se'].values
        k = len(effects)
        
        # Random effects model: using inverse variance weighting
        weights = 1 / (ses ** 2)
        pooled_effect = np.sum(weights * effects) / np.sum(weights)
        
        # Q statistics
        q_stat = np.sum(weights * (effects - pooled_effect) ** 2)
        p_value = 1 - stats.chi2.cdf(q_stat, k - 1)
        
        # I² statistic
        c = np.sum(weights) - np.sum(weights**2) / np.sum(weights)
        i_squared = max(0, (q_stat - (k - 1)) / q_stat)
        
        # Tau²
        if q_stat > k - 1:
            tau_squared = (q_stat - (k - 1)) / c
        else:
            tau_squared = 0
        
        # random effects weighting
        re_weights = 1 / (ses**2 + tau_squared)
        re_effect = np.sum(re_weights * effects) / np.sum(re_weights)
        re_se = 1 / np.sqrt(np.sum(re_weights))
        re_ci_lower = re_effect - 1.96 * re_se
        re_ci_upper = re_effect + 1.96 * re_se
        
        self.meta_results['pooled_effect'] = re_effect
        self.meta_results['pooled_se'] = re_se
        self.meta_results['pooled_ci_lower'] = re_ci_lower
        self.meta_results['pooled_ci_upper'] = re_ci_upper
        self.meta_results['q_stat'] = q_stat
        self.meta_results['p_value'] = p_value
        self.meta_results['i_squared'] = i_squared
        self.meta_results['tau_squared'] = tau_squared
        self.meta_results['k'] = k
        
    def prepare_radial_data(self):
        """Prepare star chart data"""
        precision = 1 / self.radial_data['se']
        z_value = self.radial_data['effect'] / self.radial_data['se']
        
        pooled_effect = self.meta_results['pooled_effect']
        expected_z = pooled_effect * precision
        
        # Determine whether it is within the confidence band
        in_ci = np.abs(z_value - expected_z) <= 1.96
        deviation = np.where(z_value > expected_z, 'On the high side', 'On the low side')
        
        self.radial_data['precision'] = precision
        self.radial_data['z_value'] = z_value
        self.radial_data['expected_z'] = expected_z
        self.radial_data['in_ci'] = in_ci
        self.radial_data['deviation'] = deviation
        
    def plot_radial(self):
        """Draw a star diagram"""
        fig, ax = plt.subplots(figsize=(12, 9), dpi=100)
        
        precision = self.radial_data['precision']
        z_value = self.radial_data['z_value']
        in_ci = self.radial_data['in_ci']
        
        pooled_effect = self.meta_results['pooled_effect']
        max_precision = precision.max() * 1.1
        
        # Draw 95% confidence bands
        x_band = np.linspace(0, max_precision, 100)
        z_upper = pooled_effect * x_band + 1.96
        z_lower = pooled_effect * x_band - 1.96
        
        # fill confidence band
        ax.fill_between(x_band, z_lower, z_upper, alpha=0.25, color='lightblue', label='95% confidence band')
        
        # Draw a regression line
        ax.plot(x_band, pooled_effect * x_band, 'b-', linewidth=2, label='merge effect line')
        
        # Draw confidence band boundaries
        ax.plot(x_band, z_upper, 'b--', linewidth=1, alpha=0.7)
        ax.plot(x_band, z_lower, 'b--', linewidth=1, alpha=0.7)
        
        # Draw reference line y=0
        ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
        
        # Plot scatter points
        colors = np.where(in_ci, '#2166ac', '#b2182b')
        labels_dict = {True: 'within confidence band', False: 'outside the confidence band'}
        
        for i in [True, False]:
            mask = in_ci == i
            ax.scatter(precision[mask], z_value[mask], c=colors[mask], 
                      s=100, label=labels_dict[i], alpha=0.8, zorder=3)
        
        # Add tag
        for idx, row in self.radial_data.iterrows():
            ax.annotate(row['study'], 
                       xy=(row['precision'], row['z_value']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.8)
        
        # Set labels and titles
        ax.set_xlabel('Precision (1/SE)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Standardized Effect (z = Effect/SE)', fontsize=12, fontweight='bold')
        ax.set_title(f"Radial Plot (Galbraith Plot) - {self.outcome_name}", 
                    fontsize=14, fontweight='bold')
        
        ax.set_xlim(0, max_precision)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # save file
        plot_file = os.path.join(self.output_dir, 
                                f"{self.data_type}_radial_{self.outcome_name}.png")
        fig.savefig(plot_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Star chart saved: {plot_file}")
        return plot_file
        
    def save_results(self):
        """Save results"""
        csv_file = os.path.join(self.output_dir,
                               f"{self.data_type}_radial_{self.outcome_name}.csv")
        self.radial_data.to_csv(csv_file, index=False)
        print(f"✓ Data table has been saved: {csv_file}")
        return csv_file
        
    def print_summary(self):
        """Print result summary"""
        k = self.meta_results['k']
        n_in = self.radial_data['in_ci'].sum()
        n_out = k - n_in
        
        print("\n" + "═" * 50)
        print("The Radial Plot is drawn")
        print("═" * 50 + "\n")
        
        print(f"【Outcome indicators】{self.outcome_name}")
        print(f"【data type】{self.data_type}")
        print(f"【Included studies】{k} item\n")
        
        print("【Heterogeneity Statistics】")
        print(f"• I² = {self.meta_results['i_squared']*100:.2f}%")
        print(f"• Tau² = {self.meta_results['tau_squared']:.4f}")
        print(f"• Q = {self.meta_results['q_stat']:.2f}, df = {k-1}, P = {self.meta_results['p_value']:.4f}\n")
        
        print("[Combined effect size]")
        display_name = self.meta_results['display_name']
        if display_name in ['OR', 'HR']:
            effect_val = np.exp(self.meta_results['pooled_effect'])
            ci_lower = np.exp(self.meta_results['pooled_ci_lower'])
            ci_upper = np.exp(self.meta_results['pooled_ci_upper'])
        else:
            effect_val = self.meta_results['pooled_effect']
            ci_lower = self.meta_results['pooled_ci_lower']
            ci_upper = self.meta_results['pooled_ci_upper']
        
        print(f"• {display_name} = {effect_val:.2f} [{ci_lower:.2f}; {ci_upper:.2f}]\n")
        
        print("【Output file】")
        plot_file = os.path.join(self.output_dir,
                                f"{self.data_type}_radial_{self.outcome_name}.png")
        csv_file = os.path.join(self.output_dir,
                               f"{self.data_type}_radial_{self.outcome_name}.csv")
        print(f"• star diagram：{plot_file}")
        print(f"• data sheet：{csv_file}\n")
        
        print("【Heterogeneity Analysis】")
        pct_in = round(n_in / k * 100, 1)
        pct_out = round(n_out / k * 100, 1)
        print(f"• fall on95%Research within the confidence band：{n_in} item ({pct_in}%)")
        print(f"• fall on95%Research outside the confidence band：{n_out} item ({pct_out}%)\n")
        
        if n_out > 0:
            print("[List of out-of-confidence band studies]")
            print(f"{'Research':<22} {'Accuracy':<12} {'z value':<12} {'Departure':<10}")
            print("─" * 56)
            
            outliers = self.radial_data[~self.radial_data['in_ci']].copy()
            outliers['deviation_error'] = np.abs(outliers['z_value'] - outliers['expected_z'])
            outliers = outliers.sort_values('deviation_error', ascending=False)
            
            for _, row in outliers.iterrows():
                study_name = row['study'][:19] + '...' if len(row['study']) > 19 else row['study']
                print(f"{study_name:<22} {row['precision']:<12.2f} "
                      f"{row['z_value']:<12.2f} {row['deviation']:<10}")
            print()
        
        print("【in conclusion】")
        if pct_out <= 5:
            print("• Almost all studies fall within the 95% confidence band, with low heterogeneity and good consistency in research results.")
        elif pct_out <= 20:
            print("• Most studies fall within the 95% confidence band and have mild heterogeneity.")
            print("• Studies outside the confidence band may require further analysis.")
        elif pct_out <= 40:
            print("• A considerable proportion of studies fall outside the 95% confidence band and have moderate heterogeneity.")
            print("• Subgroup analysis or sensitivity analysis is recommended to explore sources of heterogeneity.")
        else:
            print("• A large number of studies fall outside the 95% confidence band and have significant heterogeneity.")
            print("• It is recommended to interpret the pooled results with caution and conduct in-depth analysis of the sources of heterogeneity.")
        
        if self.meta_results['i_squared'] > 0.75:
            print("• I² > 75%, indicating high heterogeneity and requiring special attention.")
        elif self.meta_results['i_squared'] > 0.5:
            print("• I² between 50%-75%, indicating moderate heterogeneity.")
        
        print("═" * 50 + "\n")
        
    def generate(self):
        """Execute the complete build process"""
        try:
            self.load_data()
            self.validate_columns()
            
            if self.data_type == "Binary":
                self.calculate_binary()
            elif self.data_type == "Continuity":
                self.calculate_continuity()
            elif self.data_type == "Survival":
                self.calculate_survival()
            
            self.calculate_heterogeneity()
            self.prepare_radial_data()
            self.plot_radial()
            self.save_results()
            self.print_summary()
            
            return True
        except Exception as e:
            print(f"\n✗ mistake: {str(e)}", file=sys.stderr)
            return False


def main():
    """main function"""
    if len(sys.argv) < 3:
        print("Usage: python radial_plot_backup.py <csv_path> <type> [outcome_name] [output_dir]")
        print("<csv_path>: CSV file path")
        print("<type>: Binary, Continuity or Survival")
        print("[outcome_name]: Outcome indicator name (optional)")
        print("[output_dir]: output directory (optional)")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    data_type = sys.argv[2]
    outcome_name = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None
    output_dir = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else None
    
    generator = RadialPlotGenerator(csv_path, data_type, outcome_name, output_dir)
    success = generator.generate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
