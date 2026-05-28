#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os

# Read raw data
input_file = "Forest plot_continuity_test data_1.txt"
output_file = "forest_data_input.csv"

# Read txt file (tab delimited)
df = pd.read_csv(input_file, sep='\t', dtype=str)

# Convert column names to format expected by R script
df_converted = pd.DataFrame()
df_converted['study'] = df['Study']
df_converted['group1_sample_size'] = df['Total.e']
df_converted['group1_Mean'] = df['Mean.e']
df_converted['group1_SD'] = df['SD.e']
df_converted['group2_sample_size'] = df['Total.c']
df_converted['group2_Mean'] = df['Mean.c']
df_converted['group2_SD'] = df['SD.c']

# Save as CSV format
df_converted.to_csv(output_file, index=False)
print(f"Data conversion completed，saved to: {output_file}")
print(f"English: {len(df_converted)}")
print("Converted data preview:")
print(df_converted)
