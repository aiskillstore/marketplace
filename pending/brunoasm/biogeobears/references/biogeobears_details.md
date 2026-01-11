# BioGeoBEARS Detailed Reference

## Overview

BioGeoBEARS (BioGeography with Bayesian and Likelihood Evolutionary Analysis in R Scripts) is an R package for probabilistic inference of historical biogeography on phylogenetic trees. It implements various models of range evolution and allows statistical comparison between them.

## Installation

```r
# Install dependencies
install.packages("rexpokit")
install.packages("cladoRcpp")

# Install from GitHub
library(devtools)
devtools::install_github(repo="nmatzke/BioGeoBEARS")
```

## Biogeographic Models

BioGeoBEARS implements several models that differ in their assumptions about how species ranges evolve:

### DEC (Dispersal-Extinction-Cladogenesis)

The DEC model is based on LAGRANGE and includes:

- **Anagenetic changes** (along branches):
  - `d` (dispersal): Rate of range expansion into adjacent areas
  - `e` (extinction): Rate of local extinction in an area

- **Cladogenetic events** (at speciation nodes):
  - Vicariance: Ancestral range splits between daughter lineages
  - Subset sympatry: One daughter inherits full range, other subset
  - Range copying: Both daughters inherit full ancestral range

**Parameters**: 2 (d, e)
**Best for**: General-purpose biogeographic inference

### DIVALIKE (Vicariance-focused)

Similar to DIVA (Dispersal-Vicariance Analysis):

- Emphasizes vicariance at speciation events
- Fixes subset sympatry probability to 0
- Only allows vicariance and range copying at nodes

**Parameters**: 2 (d, e)
**Best for**: Systems where vicariance is the primary speciation mode

### BAYAREALIKE (Sympatry-focused)

Based on the BayArea model:

- Emphasizes sympatric speciation
- Fixes vicariance probability to 0
- Only allows subset sympatry and range copying

**Parameters**: 2 (d, e)
**Best for**: Systems where dispersal and sympatric speciation dominate

### +J Extension (Founder-event speciation)

Any of the above models can include a "+J" parameter:

- **j**: Jump dispersal / founder-event speciation rate
- Allows instantaneous dispersal to a new area at speciation
- Often significantly improves model fit
- Can be controversial (some argue it's biologically unrealistic)

**Examples**: DEC+J, DIVALIKE+J, BAYAREALIKE+J
**Additional parameters**: +1 (j)

## Model Comparison

### AIC (Akaike Information Criterion)

```
AIC = -2 × ln(L) + 2k
```

Where:
- ln(L) = log-likelihood
- k = number of parameters

**Lower AIC = better model**

### AICc (Corrected AIC)

Used when sample size is small relative to parameters:

```
AICc = AIC + (2k² + 2k)/(n - k - 1)
```

### AIC Weights

Probability that a model is the best among the set:

```
w_i = exp(-0.5 × Δ_i) / Σ exp(-0.5 × Δ_j)
```

Where Δ_i = AIC_i - AIC_min

### Likelihood Ratio Test (LRT)

For nested models (e.g., DEC vs DEC+J):

```
LRT = 2 × (ln(L_complex) - ln(L_simple))
```

- Test statistic follows χ² distribution
- df = difference in number of parameters
- p < 0.05 suggests complex model significantly better

## Input File Formats

### Phylogenetic Tree (Newick format)

Standard Newick format with:
- Branch lengths required
- Tip labels must match geography file
- Should be rooted and ultrametric (for time-stratified analyses)

Example:
```
((A:1.0,B:1.0):0.5,C:1.5);
```

### Geography File (PHYLIP-like format)

**Format structure:**
```
n_species [TAB] n_areas [TAB] (area1 area2 area3 ...)
species1 [TAB] 011
species2 [TAB] 110
species3 [TAB] 001
```

**Important formatting rules:**

1. **Line 1 (Header)**:
   - Number of species (integer)
   - TAB character
   - Number of areas (integer)
   - TAB character
   - Area names in parentheses, separated by spaces

2. **Subsequent lines (Species data)**:
   - Species name (must match tree tip label)
   - TAB character
   - Binary presence/absence code (1=present, 0=absent)
   - NO SPACES in the binary code
   - NO SPACES in species names (use underscores)

3. **Common errors to avoid**:
   - Using spaces instead of tabs
   - Spaces within binary codes
   - Species names with spaces
   - Mismatch between species names in tree and geography file
   - Wrong number of digits in binary code

**Example file:**
```
5	3	(A B C)
Sp_alpha	011
Sp_beta	010
Sp_gamma	111
Sp_delta	100
Sp_epsilon	001
```

## Key Parameters and Settings

### max_range_size

Maximum number of areas a species can occupy simultaneously.

- **Default**: Often set to number of areas, or number of areas - 1
- **Impact**: Larger values = more possible states = longer computation
- **Recommendation**: Set based on biological realism

### include_null_range

Whether to include the "null range" (species extinct everywhere).

- **Default**: TRUE
- **Purpose**: Allows extinction along branches
- **Recommendation**: Usually keep TRUE

### force_sparse

Use sparse matrix operations for speed.

- **Default**: FALSE
- **When to use**: Large state spaces (many areas)
- **Note**: May cause numerical issues

### speedup

Various speedup options.

- **Default**: TRUE
- **Recommendation**: Usually keep TRUE

### use_optimx

Use optimx for parameter optimization.

- **Default**: TRUE
- **Benefit**: More robust optimization
- **Recommendation**: Keep TRUE

### calc_ancprobs

Calculate ancestral state probabilities.

- **Default**: FALSE
- **Must set to TRUE** if you want ancestral range estimates
- **Impact**: Adds computational time

## Plotting Functions

### plot_BioGeoBEARS_results()

Main function for visualizing results.

**Key parameters:**

- `plotwhat`: "pie" (probability distributions) or "text" (ML states)
- `tipcex`: Tip label text size
- `statecex`: Node state text/pie chart size
- `splitcex`: Split state text/pie size (at corners)
- `titlecex`: Title text size
- `plotsplits`: Show cladogenetic events (TRUE/FALSE)
- `include_null_range`: Match analysis setting
- `label.offset`: Distance of tip labels from tree
- `cornercoords_loc`: Directory with corner coordinate files

**Color scheme:**

- Single areas: Bright primary colors
- Multi-area ranges: Blended colors
- All areas: White
- Colors automatically assigned and mixed

## Biogeographical Stochastic Mapping (BSM)

Extension of BioGeoBEARS that simulates stochastic histories:

- Generates multiple possible biogeographic histories
- Accounts for uncertainty in ancestral ranges
- Allows visualization of range evolution dynamics
- More computationally intensive

Not covered in basic workflow but available in package.

## Common Analysis Workflow

1. **Prepare inputs**
   - Phylogenetic tree (Newick)
   - Geography file (PHYLIP format)
   - Validate both files

2. **Setup analysis**
   - Define max_range_size
   - Load tree and geography data
   - Create state space

3. **Fit models**
   - DEC, DIVALIKE, BAYAREALIKE
   - With and without +J
   - 6 models total is standard

4. **Compare models**
   - AIC/AICc scores
   - AIC weights
   - LRT for nested comparisons

5. **Visualize best model**
   - Pie charts for probabilities
   - Text labels for ML states
   - Annotate with split events

6. **Interpret results**
   - Ancestral ranges
   - Dispersal patterns
   - Speciation modes (if using +J)

## Interpretation Guidelines

### Dispersal rate (d)

- **High d**: Frequent range expansions
- **Low d**: Species mostly stay in current ranges
- **Units**: Expected dispersal events per lineage per time unit

### Extinction rate (e)

- **High e**: Ranges frequently contract
- **Low e**: Stable occupancy once established
- **Relative to d**: d/e ratio indicates dispersal vs. contraction tendency

### Founder-event rate (j)

- **High j**: Jump dispersal important in clade evolution
- **Low j** (but model still better): Minor role but statistically supported
- **j = 0** (in +J model): Founder events not supported

### Model selection insights

- **DEC favored**: Balanced dispersal, extinction, and vicariance
- **DIVALIKE favored**: Vicariance-driven diversification
- **BAYAREALIKE favored**: Sympatric speciation and dispersal
- **+J improves fit**: Founder-event speciation may be important

## Computational Considerations

### Runtime factors

- **Number of tips**: Polynomial scaling
- **Number of areas**: Exponential scaling in state space
- **max_range_size**: Major impact (reduces state space)
- **Tree depth**: Linear scaling

### Memory usage

- Large trees + many areas can require substantial RAM
- Sparse matrices help but have trade-offs

### Optimization issues

- Complex likelihood surfaces
- Multiple local optima possible
- May need multiple optimization runs
- Check parameter estimates for sensibility

## Citations

**Main BioGeoBEARS reference:**
Matzke, N. J. (2013). Probabilistic historical biogeography: new models for founder-event speciation, imperfect detection, and fossils allow improved accuracy and model-testing. *Frontiers of Biogeography*, 5(4), 242-248.

**LAGRANGE (DEC model origin):**
Ree, R. H., & Smith, S. A. (2008). Maximum likelihood inference of geographic range evolution by dispersal, local extinction, and cladogenesis. *Systematic Biology*, 57(1), 4-14.

**+J parameter discussion:**
Ree, R. H., & Sanmartín, I. (2018). Conceptual and statistical problems with the DEC+J model of founder-event speciation and its comparison with DEC via model selection. *Journal of Biogeography*, 45(4), 741-749.

**Model comparison best practices:**
Burnham, K. P., & Anderson, D. R. (2002). *Model Selection and Multimodel Inference: A Practical Information-Theoretic Approach* (2nd ed.). Springer.

## Further Resources

- **BioGeoBEARS wiki**: http://phylo.wikidot.com/biogeobears
- **GitHub repository**: https://github.com/nmatzke/BioGeoBEARS
- **Google Group**: biogeobears@googlegroups.com
- **Tutorial scripts**: Available in package `inst/extdata/examples/`
