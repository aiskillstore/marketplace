#!/usr/bin/env python3
"""ROB2 Risk of Bias Assessment Plot (Alternate Python Implementation)
Usage: python scripts/rob2_plot.py <csv_path> [save_name] [output_dir]
Dependencies: pandas, matplotlib"""
import sys
import os
import math
import pandas as pd
import matplotlib.pyplot as plt


def read_data(csv_path):
    df = pd.read_csv(csv_path, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    # Unify lowercase column names to be compatible with different data sources
    df.columns = [c.lower() for c in df.columns]
    required = ['study', 'd1', 'd2', 'd3', 'd4', 'd5', 'overall']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column: {', '.join(missing)}")
    # Fill missing values ​​with 'No information'
    df = df[required].fillna('No information')
    return df


def traffic_light_plot(df, save_path):
    vars_order = ['d1', 'd2', 'd3', 'd4', 'd5', 'overall']
    colors = {
        'Low': '#4daf4a',
        'Some concerns': '#ff7f00',
        'High': '#e41a1c',
        'No information': '#999999'
    }

    n = len(df)
    fig_h = max(2.5, 0.5 * n)
    fig, ax = plt.subplots(figsize=(8, fig_h))

    for i in range(n):
        for j, var in enumerate(vars_order):
            val = df.iloc[i][var]
            color = colors.get(val, '#999999')
            # Draw a large dot with a border
            ax.scatter(j, n - 1 - i, s=1500, facecolor=color, edgecolor='black', zorder=3)

    ax.set_xticks(range(len(vars_order)))
    ax.set_xticklabels([v.upper() if v.startswith('d') else v.capitalize() for v in vars_order], fontsize=12)
    ax.set_yticks(list(range(n)))
    ax.set_yticklabels(list(df['study'][::-1]), fontsize=10)
    ax.set_xlim(-0.5, len(vars_order) - 0.5)
    ax.set_ylim(-0.5, n - 0.5)
    ax.invert_yaxis()
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.grid(False)
    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def summary_bar_plot(df, save_path):
    vars_order = ['d1', 'd2', 'd3', 'd4', 'd5', 'overall']
    categories = ['Low', 'Some concerns', 'High', 'No information']
    colors = {
        'Low': '#4daf4a',
        'Some concerns': '#ff7f00',
        'High': '#e41a1c',
        'No information': '#999999'
    }

    counts = {var: [0] * len(categories) for var in vars_order}
    for var in vars_order:
        c = df[var].value_counts()
        total = len(df)
        for i, cat in enumerate(categories):
            counts[var][i] = c.get(cat, 0)

    # Draw a horizontally stacked bar chart
    fig, ax = plt.subplots(figsize=(8, 4))
    y_positions = range(len(vars_order))
    left = [0] * len(vars_order)
    for i, cat in enumerate(categories):
        values = [counts[var][i] / float(len(df)) for var in vars_order]
        ax.barh(y_positions, values, left=left, color=colors[cat], label=cat)
        left = [l + v for l, v in zip(left, values)]

    ax.set_yticks(y_positions)
    ax.set_yticklabels([v.upper() if v.startswith('d') else v.capitalize() for v in vars_order], fontsize=12)
    ax.set_xlim(0, 1)
    ax.set_xlabel('Proportion')
    ax.legend(loc='center right')
    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def print_summary(df, save_light, save_bar):
    n = len(df)
    print('\n' + '═' * 43)
    print('The ROB2 risk of bias assessment chart is drawn')
    print('═' * 43 + '\n')
    print(f'【Included studies】{n} item\n')
    print('【Output file】')
    print(f'• traffic light diagram：{os.path.abspath(save_light)}')
    print(f'• Summary strip chart：{os.path.abspath(save_bar)}\n')

    def count_risk(col):
        return {
            'Low': int((df[col] == 'Low').sum()),
            'Some concerns': int((df[col] == 'Some concerns').sum()),
            'High': int((df[col] == 'High').sum()),
            'No info': int((df[col] == 'No information').sum())
        }

    print('[Summary of risk of bias]')
    print(f"{'Domain':<20} {'Low':<6} {'Some concerns':<16} {'High':<6} {'No info':<8}")
    print('─' * 60)
    domain_labels = {
        'd1': 'D1 (randomized)',
        'd2': 'D2 (intervention deviation)',
        'd3': 'D3 (missing data)',
        'd4': 'D4 (outcome measure)',
        'd5': 'D5 (optional reporting)',
        'overall': 'Overall'
    }
    for col in ['d1', 'd2', 'd3', 'd4', 'd5', 'overall']:
        c = count_risk(col)
        print(f"{domain_labels[col]:<20} {c['Low']:<6} {c['Some concerns']:<16} {c['High']:<6} {c['No info']:<8}")

    overall = count_risk('overall')
    n_low = overall['Low']
    n_some = overall['Some concerns']
    n_high = overall['High']
    pct = lambda x: round(x / n * 100, 1) if n > 0 else 0.0

    print('【Overall evaluation】')
    print(f'• low risk research：{n_low} item ({pct(n_low)}%)')
    print(f'• There are concerns：{n_some} item ({pct(n_some)}%)')
    print(f'• high risk research：{n_high} item ({pct(n_high)}%)')
    print('═' * 43)


def main(argv):
    if len(argv) < 2:
        print('Usage: python scripts/rob2_plot.py <csv_path> [save_name] [output_dir]')
        sys.exit(1)
    csv_path = argv[1]
    save_name = argv[2] if len(argv) >= 3 and argv[2] != '' else 'rob2'
    output_dir = argv[3] if len(argv) >= 4 and argv[3] != '' else os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    df = read_data(csv_path)
    light_file = os.path.join(output_dir, f"{save_name}_rob2_light_plot.png")
    bar_file = os.path.join(output_dir, f"{save_name}_rob2_bar_plot.png")
    traffic_light_plot(df, light_file)
    summary_bar_plot(df, bar_file)
    print_summary(df, light_file, bar_file)


if __name__ == '__main__':
    main(sys.argv)
