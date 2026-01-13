# BioGeoBEARS Biogeographic Analysis Skill

A Claude skill for setting up and executing phylogenetic biogeographic analyses using BioGeoBEARS in R.

## Overview

This skill automates the complete workflow for biogeographic analysis on phylogenetic trees, from raw data validation to publication-ready visualizations. It helps users reconstruct ancestral geographic ranges by:

- Validating and reformatting input files (phylogenetic tree + geographic distribution data)
- Setting up organized analysis folder structures
- Generating customized RMarkdown analysis scripts
- Guiding parameter selection (maximum range size, model choices)
- Producing visualizations with pie charts and text labels showing ancestral ranges
- Comparing multiple biogeographic models with statistical tests

## When to Use

Use this skill when you need to:
- Reconstruct ancestral geographic ranges on a phylogeny
- Test different biogeographic models (DEC, DIVALIKE, BAYAREALIKE)
- Analyze how species distributions evolved over time
- Determine whether founder-event speciation (+J parameter) is important
- Generate publication-ready biogeographic visualizations

## Required Inputs

Users must provide:

1. **Phylogenetic tree** (Newick format: .nwk, .tre, or .tree)
   - Must be rooted
   - Tip labels must match species in geography file
   - Branch lengths required

2. **Geographic distribution data** (any tabular format)
   - Species names matching tree tips
   - Presence/absence data for different geographic areas
   - Accepts CSV, TSV, Excel, or PHYLIP format

## What the Skill Does

### 1. Data Validation and Reformatting

The skill includes a Python script (`validate_geography_file.py`) that:
- Validates geography file format (PHYLIP-like with specific tab/spacing requirements)
- Checks for common errors (spaces in species names, tab delimiters, binary code length)
- Reformats CSV/TSV files to proper BioGeoBEARS format
- Cross-validates species names against tree tip labels

### 2. Analysis Setup

Creates an organized directory structure:
```
biogeobears_analysis/
├── input/
│   ├── tree.nwk                    # Phylogenetic tree
│   ├── geography.data              # Validated geography file
│   └── original_data/              # Original input files
├── scripts/
│   └── run_biogeobears.Rmd         # Customized RMarkdown script
├── results/                        # Analysis outputs
│   ├── [MODEL]_result.Rdata        # Saved model results
│   └── plots/                      # Visualizations
│       ├── [MODEL]_pie.pdf
│       └── [MODEL]_text.pdf
└── README.md                       # Documentation
```

### 3. RMarkdown Analysis Template

Generates a complete RMarkdown script that:
- Loads and validates input data
- Fits 6 biogeographic models:
  - DEC (Dispersal-Extinction-Cladogenesis)
  - DEC+J (DEC with founder-event speciation)
  - DIVALIKE (vicariance-focused)
  - DIVALIKE+J
  - BAYAREALIKE (sympatry-focused)
  - BAYAREALIKE+J
- Compares models using AIC, AICc, and AIC weights
- Performs likelihood ratio tests for nested models
- Estimates parameters (d=dispersal, e=extinction, j=founder-event rates)
- Generates visualizations on the phylogeny
- Creates HTML report with all results

### 4. Visualization

Produces two types of plots:
- **Pie charts**: Show probability distributions for ancestral ranges (conveys uncertainty)
- **Text labels**: Show maximum likelihood ancestral states (cleaner, easier to read)

Colors represent geographic areas:
- Single areas: Bright primary colors
- Multi-area ranges: Blended colors
- All areas: White

## Workflow

1. **Gather information**: Ask user for tree file, geography file, and parameters
2. **Validate tree**: Check if rooted and extract tip labels
3. **Validate/reformat geography file**: Use validation script to check format or convert from CSV/TSV
4. **Set up analysis folder**: Create organized directory structure
5. **Generate RMarkdown script**: Customize template with user parameters
6. **Create documentation**: Generate README and run scripts
7. **Provide instructions**: Clear steps for running the analysis

## Analysis Parameters

The skill helps users choose:

### Maximum Range Size
- How many areas can a species occupy simultaneously?
- Options: Conservative (# areas - 1), Permissive (all areas), Data-driven (max observed)
- Larger values increase computation time exponentially

### Models to Compare
- Default: All 6 models (recommended for comprehensive comparison)
- Alternative: Only base models or only +J models
- Rationale: Model comparison is key to biogeographic inference

### Visualization Type
- Pie charts (show probabilities and uncertainty)
- Text labels (show most likely states, cleaner)
- Both (default in template)

## Bundled Resources

### scripts/

**validate_geography_file.py**
- Validates BioGeoBEARS geography file format
- Reformats from CSV/TSV to PHYLIP
- Cross-validates with tree tip labels
- Usage: `python validate_geography_file.py --help`

**biogeobears_analysis_template.Rmd**
- Complete RMarkdown analysis template
- Parameterized via YAML header
- Fits all models, compares, and visualizes
- Generates self-contained HTML report

### references/

**biogeobears_details.md**
- Detailed model descriptions (DEC, DIVALIKE, BAYAREALIKE, +J parameter)
- Input file format specifications with examples
- Parameter interpretation guidelines
- Plotting options and customization
- Complete citations for publications
- Computational considerations and troubleshooting

## Example Output

The analysis produces:
- `biogeobears_report.html` - Interactive HTML report with all results
- `[MODEL]_result.Rdata` - Saved R objects for each model
- `plots/[MODEL]_pie.pdf` - Ancestral ranges shown as pie charts on tree
- `plots/[MODEL]_text.pdf` - Ancestral ranges shown as text labels on tree

## Interpretation Guidance

The skill helps users understand:

### Model Selection
- **AIC weights**: Probability each model is best
- **ΔAIC thresholds**: <2 (equivalent), 2-7 (less support), >10 (no support)

### Parameter Estimates
- **d (dispersal)**: Rate of range expansion
- **e (extinction)**: Rate of local extinction
- **j (founder-event)**: Rate of jump dispersal at speciation
- **d/e ratio**: >1 favors expansion, <1 favors contraction

### Statistical Tests
- **LRT p < 0.05**: +J parameter significantly improves fit
- Model uncertainty: Report results from multiple models if weights similar

## Installation Requirements

Users must have:
- R (≥4.0)
- BioGeoBEARS R package
- Supporting R packages: ape, rmarkdown, knitr, kableExtra
- Python 3 (for validation script)

Installation instructions are included in generated README.md files.

## Expected Runtime

**Skill setup time**: 5-10 minutes (file validation and directory setup)

**Analysis runtime** (separate from skill execution):
- Small datasets (<50 tips, ≤5 areas): 10-30 minutes
- Medium datasets (50-100 tips, 5-6 areas): 30-90 minutes
- Large datasets (>100 tips, >5 areas): 1-6 hours

## Common Issues Handled

The skill troubleshoots:
- Species name mismatches between tree and geography file
- Unrooted trees (guides user to root with outgroup)
- Geography file formatting errors (tabs, spaces, binary codes)
- Optimization convergence failures
- Slow runtime with many areas/tips

## Citations

Based on:
- **BioGeoBEARS** package by Nicholas Matzke
- Tutorial resources from http://phylo.wikidot.com/biogeobears
- Example workflows from BioGeoBEARS GitHub repository

## Skill Details

- **Skill Type**: Workflow-based bioinformatics skill
- **Domain**: Phylogenetic biogeography, historical biogeography
- **Output**: Complete analysis setup with scripts, documentation, and ready-to-run workflow
- **Automation Level**: High (validates, reformats, generates all scripts)
- **User Input Required**: File paths and parameter choices via guided questions

## See Also

- [phylo_from_buscos](../phylo_from_buscos/README.md) - Complementary skill for generating phylogenies from genomes
