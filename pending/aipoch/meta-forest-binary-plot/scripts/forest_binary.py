#!/usr/bin/env python3
"""Binary classification data forest plot drawing script
Usage: python forest_binary.py <csv_path> [outcome_name] [output_dir]"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

def parse_args():
    parser = argparse.ArgumentParser(description='Binary classification data forest plot drawing script')
    parser.add_argument('csv_path', help='CSV file path')
    parser.add_argument('--outcome', '-o', default=None, help='Outcome indicator name')
    parser.add_argument('--output_dir', '-d', default=None, help='Output directory')
    return parser.parse_args()


def load_data(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File does not exist: {csv_path}")
    data_df = pd.read_csv(csv_path, sep=None, engine='python')
    required_cols = ['study', 'group1_Events', 'group1_sample_size',
                    'group2_Events', 'group2_sample_size']
    missing_cols = [col for col in required_cols if col not in data_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required column: {', '.join(missing_cols)}")
    return data_df


def calculate_meta_analysis(data_df):
    studies = data_df['study'].values
    events_e = data_df['group1_Events'].values.astype(float)
    total_e = data_df['group1_sample_size'].values.astype(float)
    events_c = data_df['group2_Events'].values.astype(float)
    total_c = data_df['group2_sample_size'].values.astype(float)

    n_studies = len(studies)

    log_or = []
    se_log_or = []
    weights = []

    tau2 = 0
    for i in range(n_studies):
        e = events_e[i]
        n_e = total_e[i]
        c = events_c[i]
        n_c = total_c[i]

        if e == 0 or c == 0 or n_e == e or n_c == c:
            or_val = (e + 0.5) * (n_c - c + 0.5) / ((c + 0.5) * (n_e - e + 0.5))
        else:
            or_val = (e * (n_c - c)) / (c * (n_e - e))

        log_or_i = np.log(or_val)

        var_log_or = 1/(e+0.5) + 1/(c+0.5) + 1/(n_e-e+0.5) + 1/(n_c-c+0.5)
        se_log_or_i = np.sqrt(var_log_or)

        log_or.append(log_or_i)
        se_log_or.append(se_log_or_i)
        weight_i = 1 / var_log_or
        weights.append(weight_i)

    weights = np.array(weights)
    sum_weights = np.sum(weights)

    pooled_log_or = np.sum(weights * log_or) / sum_weights
    pooled_se = np.sqrt(1 / sum_weights)

    tau2_estimator = np.sum(weights) / (np.sum(weights**2)) * max(0,
        (np.sum(weights * (log_or - pooled_log_or)**2) - (n_studies - 1)) / np.sum(weights))

    tau2 = max(0, tau2_estimator)

    if tau2 > 0:
        random_weights = 1 / (np.array(se_log_or)**2 + tau2)
    else:
        random_weights = weights

    sum_random_weights = np.sum(random_weights)
    random_pooled_log_or = np.sum(random_weights * log_or) / sum_random_weights
    random_pooled_se = np.sqrt(1 / sum_random_weights)

    pooled_or = np.exp(random_pooled_log_or)
    pooled_ci_lower = np.exp(random_pooled_log_or - 1.96 * random_pooled_se)
    pooled_ci_upper = np.exp(random_pooled_log_or + 1.96 * random_pooled_se)

    or_values = np.exp(log_or)
    ci_lower = np.exp(log_or - 1.96 * np.array(se_log_or))
    ci_upper = np.exp(log_or + 1.96 * np.array(se_log_or))

    or_df = pd.DataFrame({
        'Study': studies,
        'Events_E': events_e,
        'Total_E': total_e,
        'Events_C': events_c,
        'Total_C': total_c,
        'OR': or_values,
        'CI_lower': ci_lower,
        'CI_upper': ci_upper,
        'Weight': random_weights / sum_random_weights * 100
    })

    total_row = pd.DataFrame([{
        'Study': 'Total',
        'Events_E': np.sum(events_e),
        'Total_E': np.sum(total_e),
        'Events_C': np.sum(events_c),
        'Total_C': np.sum(total_c),
        'OR': pooled_or,
        'CI_lower': pooled_ci_lower,
        'CI_upper': pooled_ci_upper,
        'Weight': 100.0
    }])
    or_df = pd.concat([or_df, total_row], ignore_index=True)

    het_I2 = (tau2 / (tau2 + 2.564)) * 100 if (tau2 + 2.564) > 0 else 0

    q_stat = np.sum(random_weights * (log_or - random_pooled_log_or)**2)
    q_df = n_studies - 1
    q_pval = 1 - (q_stat ** (1/2)) if q_stat > 0 else 1

    return or_df, {
        'pooled_or': pooled_or,
        'pooled_ci_lower': pooled_ci_lower,
        'pooled_ci_upper': pooled_ci_upper,
        'tau2': tau2,
        'I2': het_I2,
        'q_stat': q_stat,
        'q_pval': q_pval
    }


def draw_forest_plot(or_df, meta_info, outcome_name, output_path):
    n_rows = len(or_df)

    fig, ax = plt.subplots(figsize=(14, n_rows * 0.4 + 2))

    ax.set_xlim(-3, 5)
    ax.set_ylim(-1, n_rows + 1)

    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)

    or_values = or_df['OR'].values
    ci_lower = or_df['CI_lower'].values
    ci_upper = or_df['CI_upper'].values
    weights = or_df['Weight'].values

    for i in range(n_rows - 1):
        y = n_rows - i - 1

        weight_norm = weights[i] / 100 * 1.5 + 0.3

        ci_low = np.clip(np.log(ci_lower[i]), -2, 4)
        ci_high = np.clip(np.log(ci_upper[i]), -2, 4)
        or_log = np.clip(np.log(or_values[i]), -2, 4)

        ax.plot([ci_low, ci_high], [y, y], color='blue', linewidth=1.5)

        ax.plot(or_log, y, 's', color='blue', markersize=4 + weight_norm * 3)

    diamond_y = 0 - 0.5
    pooled_or_log = np.log(meta_info['pooled_or'])
    pooled_ci_low = np.clip(np.log(meta_info['pooled_ci_lower']), -2, 4)
    pooled_ci_high = np.clip(np.log(meta_info['pooled_ci_upper']), -2, 4)

    diamond_width = pooled_ci_high - pooled_ci_low
    diamond_x = pooled_ci_low + diamond_width / 2

    diamond = mpatches.FancyBboxPatch(
        (pooled_ci_low, diamond_y - 0.15),
        diamond_width, 0.3,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor='black', edgecolor='none'
    )
    ax.add_patch(diamond)
    ax.plot([pooled_ci_low, pooled_ci_high], [diamond_y, diamond_y], color='black', linewidth=1.5)

    ax.set_xlim(-2, 4)
    ax.get_xaxis().set_visible(False)

    ax.set_ylim(-1, n_rows + 0.5)
    ax.set_yticks([])
    ax.set_ylim(-1, n_rows + 0.5)

    col1_x = -2.8
    col2_x = -1.8
    col3_x = -0.8
    col4_x = 0.2
    col5_x = 1.2
    col6_x = 2.5
    col7_x = 3.5

    ax.text(col1_x, n_rows + 0.3, 'Study', fontsize=9, ha='center', va='bottom', fontweight='bold')
    ax.text(col2_x, n_rows + 0.3, 'Events E', fontsize=9, ha='center', va='bottom', fontweight='bold')
    ax.text(col3_x, n_rows + 0.3, 'Total E', fontsize=9, ha='center', va='bottom', fontweight='bold')
    ax.text(col4_x, n_rows + 0.3, 'Events C', fontsize=9, ha='center', va='bottom', fontweight='bold')
    ax.text(col5_x, n_rows + 0.3, 'Total C', fontsize=9, ha='center', va='bottom', fontweight='bold')
    ax.text(col6_x, n_rows + 0.3, 'OR [95% CI]', fontsize=9, ha='center', va='bottom', fontweight='bold')
    ax.text(col7_x, n_rows + 0.3, '%W(Random)', fontsize=9, ha='center', va='bottom', fontweight='bold')

    for i in range(n_rows):
        y = n_rows - i - 1

        study_name = or_df.iloc[i]['Study']
        events_e = or_df.iloc[i]['Events_E']
        total_e = or_df.iloc[i]['Total_E']
        events_c = or_df.iloc[i]['Events_C']
        total_c = or_df.iloc[i]['Total_C']
        weight = or_df.iloc[i]['Weight']

        ax.text(col1_x, y, str(study_name), fontsize=8, ha='center', va='center')

        if i < n_rows - 1:
            ax.text(col2_x, y, f'{int(events_e)}', fontsize=8, ha='center', va='center')
            ax.text(col3_x, y, f'{int(total_e)}', fontsize=8, ha='center', va='center')
            ax.text(col4_x, y, f'{int(events_c)}', fontsize=8, ha='center', va='center')
            ax.text(col5_x, y, f'{int(total_c)}', fontsize=8, ha='center', va='center')

            or_val = or_df.iloc[i]['OR']
            ci_l = or_df.iloc[i]['CI_lower']
            ci_u = or_df.iloc[i]['CI_upper']

            if np.isnan(or_val) or np.isinf(or_val):
                ax.text(col6_x, y, 'NA', fontsize=8, ha='center', va='center')
            else:
                ax.text(col6_x, y, f'{or_val:.2f} [{ci_l:.2f}, {ci_u:.2f}]', fontsize=8, ha='center', va='center')

            ax.text(col7_x, y, f'{weight:.1f}', fontsize=8, ha='center', va='center')

    ax.text(col1_x, -0.5, 'Total', fontsize=9, ha='center', va='center', fontweight='bold')
    ax.text(col2_x, -0.5, f'{int(or_df.iloc[-1]["Events_E"])}', fontsize=9, ha='center', va='center', fontweight='bold')
    ax.text(col3_x, -0.5, f'{int(or_df.iloc[-1]["Total_E"])}', fontsize=9, ha='center', va='center', fontweight='bold')
    ax.text(col4_x, -0.5, f'{int(or_df.iloc[-1]["Events_C"])}', fontsize=9, ha='center', va='center', fontweight='bold')
    ax.text(col5_x, -0.5, f'{int(or_df.iloc[-1]["Total_C"])}', fontsize=9, ha='center', va='center', fontweight='bold')

    pooled_or = meta_info['pooled_or']
    pooled_ci_l = meta_info['pooled_ci_lower']
    pooled_ci_u = meta_info['pooled_ci_upper']
    ax.text(col6_x, -0.5, f'{pooled_or:.2f} [{pooled_ci_l:.2f}, {pooled_ci_u:.2f}]',
            fontsize=9, ha='center', va='center', fontweight='bold')
    ax.text(col7_x, -0.5, '100.0', fontsize=9, ha='center', va='center', fontweight='bold')

    ax.text(0.02, 0.98, f'Outcome: {outcome_name}', transform=ax.transAxes,
            fontsize=12, fontweight='bold', va='top')

    ax.text(0.02, 0.93, f'OR = {pooled_or:.2f} [{pooled_ci_l:.2f}, {pooled_ci_u:.2f}]',
            transform=ax.transAxes, fontsize=10, va='top')
    ax.text(0.02, 0.89, f'I² = {meta_info["I2"]:.1f}%, Tau² = {meta_info["tau2"]:.4f}',
            transform=ax.transAxes, fontsize=10, va='top')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"The forest map has been saved to: {output_path}")


def main():
    args = parse_args()

    csv_path = args.csv_path
    outcome_name = args.outcome
    output_dir = args.output_dir

    if output_dir is None:
        output_dir = os.path.dirname(csv_path)
        if not output_dir:
            output_dir = '.'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    data_df = load_data(csv_path)

    if len(data_df) < 2:
        raise ValueError("At least 2 studies are required to conduct a meta-analysis")

    if outcome_name is None:
        if 'outcome_new' in data_df.columns:
            outcome_name = str(data_df['outcome_new'].iloc[0])
        else:
            outcome_name = 'Outcome'

    or_df, meta_info = calculate_meta_analysis(data_df)

    forest_file = os.path.join(output_dir, f"Binary_forest_{outcome_name}.png")
    draw_forest_plot(or_df, meta_info, outcome_name, forest_file)

    csv_file = os.path.join(output_dir, f"Binary_forest_{outcome_name}.csv")
    or_df.to_csv(csv_file, index=False)
    print(f"The data table has been saved to: {csv_file}")

    print("\n" + "="*50)
    print("The two-class forest diagram is drawn")
    print("="*50)
    print(f"\n【Outcome indicators】{outcome_name}")
    print(f"【Included studies】{len(data_df)} item\n")
    print("【Output file】")
    print(f"• Forest map：{forest_file}")
    print(f"• data sheet：{csv_file}\n")
    print("[Combined effect size]")
    print(f"• OR = {meta_info['pooled_or']:.2f} [{meta_info['pooled_ci_lower']:.2f}; {meta_info['pooled_ci_upper']:.2f}]\n")
    print("【Heterogeneity】")
    print(f"• I² = {meta_info['I2']:.2f}%")
    print(f"• Tau² = {meta_info['tau2']:.4f}")
    print(f"• Qtest = {meta_info['q_stat']:.4f}")
    print("="*50)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"mistake: {e}")
        sys.exit(1)
