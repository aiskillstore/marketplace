---
name: data-analysis
version: 1.0.0
description: A skill for analyzing data using Python (pandas) and generating professional visualizations (matplotlib/seaborn).
tags:
  - data-analysis
  - visualization
  - python
  - pandas
---

# Data Analysis & Visualization Skill

This skill empowers the agent to perform data analysis and generate visualizations using Python libraries. It is designed to be used in conjunction with a sandbox environment.

## Capabilities

### 1. Data Processing
- **Pandas**: Clean, filter, and aggregate data.
- **NumPy**: Numerical computations.

### 2. Visualization
- **Matplotlib/Seaborn**: Generate high-quality charts (bar, line, scatter, pie, heatmap).
- **Theme Matching**: Apply color palettes consistent with the document theme.

## Usage

The skill provides utility functions to generate Python code that can be executed in the sandbox.

### Scripts
- `code_generator.py`: Generates Python scripts for analysis and plotting.
- `visualizer.py`: Helper library (injected into sandbox) to ensure consistent styling.

## Dependencies (Sandbox Environment)
- pandas
- numpy
- matplotlib
- seaborn
