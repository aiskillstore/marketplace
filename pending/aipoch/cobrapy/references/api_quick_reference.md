# COBRApy API Quick Reference

This document provides a quick reference for commonly used COBRApy functions, signatures, and usage patterns.

## Model I/O

### Loading Models

```python
from cobra.io import load_model, read_sbml_model, load_json_model, load_yaml_model, load_matlab_model

# Built-in test models
model = load_model("textbook")   # E. coli core metabolism
model = load_model("ecoli")      # Full E. coli iJO1366
model = load_model("salmonella") # Salmonella LT2

# Loading from files
model = read_sbml_model(filename, f_replace={}, **kwargs)
model = load_json_model(filename)
model = load_yaml_model(filename)
model = load_matlab_model(filename, variable_name=None)
```

### Saving Models

```python
from cobra.io import write_sbml_model, save_json_model, save_yaml_model, save_matlab_model

write_sbml_model(model, filename, f_replace={}, **kwargs)
save_json_model(model, filename, pretty=False, **kwargs)
save_yaml_model(model, filename, **kwargs)
save_matlab_model(model, filename, **kwargs)
```

## Model Structure

### Core Classes

```python
from cobra import Model, Reaction, Metabolite, Gene

# Create model
model = Model(id_or_model=None, name=None)

# Create metabolite
metabolite = Metabolite(
    id=None,
    formula=None,
    name="",
    charge=None,
    compartment=None
)

# Create reaction
reaction = Reaction(
    id=None,
    name="",
    subsystem="",
    lower_bound=0.0,
    upper_bound=None
)

# Create gene
gene = Gene(id=None, name="", functional=True)
```

### Model Attributes

```python
# Component access (DictList objects)
model.reactions       # DictList of Reaction objects
model.metabolites     # DictList of Metabolite objects
model.genes          # DictList of Gene objects

# Special reaction lists
model.exchanges      # Exchange reactions (external transport)
model.demands        # Demand reactions (metabolite sinks)
model.sinks          # Sink reactions (sink)
model.boundary       # All boundary reactions

# Model properties
model.objective      # Current objective function (read/write)
model.objective_direction  # "max" or "min"
model.medium         # Medium (dictionary of exchange: bound)
model.solver         # Optimization solver
```

### DictList Methods

```python
# Access by index
item = model.reactions[0]

# Access by ID
item = model.reactions.get_by_id("PFK")

# Query by string (substring matching)
items = model.reactions.query("atp")      # Case-insensitive search
items = model.reactions.query(lambda x: x.subsystem == "Glycolysis")

# List comprehension
items = [r for r in model.reactions if r.lower_bound < 0]

# Check membership
"PFK" in model.reactions
```

## Optimization

### Basic Optimization

```python
# Full optimization (returns a Solution object)
solution = model.optimize()

# Attributes of the Solution object
solution.objective_value   # Objective function value
solution.status           # Optimization status ("optimal", "infeasible", etc.)
solution.fluxes          # Pandas Series of reaction fluxes
solution.shadow_prices   # Pandas Series of metabolite shadow prices
solution.reduced_costs   # Pandas Series of reduced costs

# Slim optimization (returns only the float value)
objective_value = model.slim_optimize()

# Change objective function
model.objective = "ATPM"
model.objective = model.reactions.ATPM
model.objective = {model.reactions.ATPM: 1.0}

# Change optimization direction
model.objective_direction = "max"  # or "min"
```

### Solver Configuration

```python
# Check available solvers
from cobra.util.solver import solvers
print(solvers)

# Change solver
model.solver = "glpk"  # or "cplex", "gurobi", etc.

# Specific solver configuration
model.solver.configuration.timeout = 60  # seconds
model.solver.configuration.verbosity = 1
model.solver.configuration.tolerances.feasibility = 1e-9
```

## Flux Analysis

### Flux Balance Analysis (FBA)

```python
from cobra.flux_analysis import pfba, geometric_fba

# Parsimonious FBA (pFBA)
solution = pfba(model, fraction_of_optimum=1.0, **kwargs)

# Geometric FBA
solution = geometric_fba(model, epsilon=1e-06, max_tries=200)
```

### Flux Variability Analysis (FVA)

```python
from cobra.flux_analysis import flux_variability_analysis

fva_result = flux_variability_analysis(
    model,
    reaction_list=None,        # List of reaction IDs, None for all
    loopless=False,            # Eliminate thermodynamically infeasible loops
    fraction_of_optimum=1.0,   # Fraction of optimum (0.0-1.0)
    pfba_factor=None,          # Optional pFBA constraints
    processes=1                # Number of parallel processes
)

# Returns a DataFrame with minimum and maximum columns
```

### Gene and Reaction Deletion Analysis

```python
from cobra.flux_analysis import (
    single_gene_deletion,
    single_reaction_deletion,
    double_gene_deletion,
    double_reaction_deletion
)

# Single deletion analysis
results = single_gene_deletion(
    model,
    gene_list=None,     # None for all genes
    processes=1,
    **kwargs
)

results = single_reaction_deletion(
    model,
    reaction_list=None,  # None for all reactions
    processes=1,
    **kwargs
)

# Double deletion analysis
results = double_gene_deletion(
    model,
    gene_list1=None,
    gene_list2=None,
    processes=1,
    **kwargs
)

results = double_reaction_deletion(
    model,
    reaction_list1=None,
    reaction_list2=None,
    processes=1,
    **kwargs
)

# Returns a DataFrame with ids, growth, and status columns
# For double deletions, the index is a MultiIndex of gene/reaction pairs
```

### Flux Sampling

```python
from cobra.sampling import sample, OptGPSampler, ACHRSampler

# Simple interface
samples = sample(
    model,
    n,                  # Number of samples
    method="optgp",     # or "achr"
    thinning=100,       # Thinning factor (sample every n iterations)
    processes=1,        # Parallel processes (OptGP only)
    seed=None          # Random seed
)

# Advanced interface using sampler objects
sampler = OptGPSampler(model, processes=4, thinning=100)
sampler = ACHRSampler(model, thinning=100)

# Generate samples
samples = sampler.sample(n)

# Validate samples
validation = sampler.validate(sampler.samples)
# Returns an array: 'v' (valid), 'l' (lower bound violation),
# 'u' (upper bound violation), 'e' (equality constraint violation)

# Batch sampling
sampler.batch(n_samples, n_batches)
```

### Production Envelopes

```python
from cobra.flux_analysis import production_envelope

envelope = production_envelope(
    model,
    reactions,              # List of 1-2 reaction IDs
    objective=None,         # Objective reaction ID (None uses current model objective)
    carbon_sources=None,    # Carbon sources for yield calculation
    points=20,              # Number of points to calculate
    threshold=0.01          # Minimum objective value threshold
)

# Returns a DataFrame containing:
# - First reaction flux
# - Second reaction flux (if provided)
# - objective_minimum, objective_maximum
# - carbon_yield_minimum, carbon_yield_maximum (if carbon sources are specified)
# - mass_yield_minimum, mass_yield_maximum
```

### Gapfilling

```python
from cobra.flux_analysis import gapfill

# Basic gapfilling
solution = gapfill(
    model,
    universal=None,         # Universal model containing candidate reactions
    lower_bound=0.05,       # Minimum objective flux
    penalties=None,         # Dictionary of reaction: penalty
    demand_reactions=True,  # Add demand reactions if needed
    exchange_reactions=False,
    iterations=1
)

# Returns a list of Reaction objects to be added

# Obtain multiple solutions
solutions = []
for i in range(5):
    sol = gapfill(model, universal, iterations=1)
    solutions.append(sol)
    # Prevent finding the same solution by increasing penalties
```

### Other Analysis Methods

```python
from cobra.flux_analysis import (
    find_blocked_reactions,
    find_essential_genes,
    find_essential_reactions
)

# Blocked reactions (reactions that cannot carry flux)
blocked = find_blocked_reactions(
    model,
    reaction_list=None,
    zero_cutoff=1e-9,
    open_exchanges=False
)

# Essential genes/reactions
essential_genes = find_essential_genes(model, threshold=0.01)
essential_reactions = find_essential_reactions(model, threshold=0.01)
```

## Medium and Boundary Conditions

### Medium Management

```python
# Get current medium (returns a dictionary)
medium = model.medium

# Set medium (must reassign the entire dictionary)
medium = model.medium
medium["EX_glc__D_e"] = 10.0
medium["EX_o2_e"] = 20.0
model.medium = medium

# Alternative method: modify a single reaction
with model:
    model.reactions.EX_glc__D_e.lower_bound = -10.0
```

### Minimal Medium

```python
from cobra.medium import minimal_medium

min_medium = minimal_medium(
    model,
    min_objective_value=0.1,  # Minimum growth rate
    minimize_components=False, # If True, use MILP (slower)
    open_exchanges=False,      # Open all exchange reactions before optimization
    exports=False,             # Allow metabolite exports
    penalties=None             # Dictionary of exchange reaction: penalty
)

# Returns a Series of exchange reactions with fluxes
```

### Boundary Reactions

```python
# Add boundary reaction
model.add_boundary(
    metabolite,
    type="exchange",    # or "demand", "sink"
    reaction_id=None,   # Automatically generated if None
    lb=None,
    ub=None,
    sbo_term=None
)

# Access boundary reactions
exchanges = model.exchanges     # System boundaries
demands = model.demands         # Intracellular removal
sinks = model.sinks            # Intracellular exchange
boundaries = model.boundary    # All boundary reactions
```

## Model Manipulation

### Adding Components

```python
# Add reactions
model.add_reactions([reaction1, reaction2, ...])
model.add_reaction(reaction)

# Add metabolites
reaction.add_metabolites({
    metabolite1: -1.0,  # Consumption (negative stoichiometry)
    metabolite2: 1.0    # Production (positive stoichiometry)
})

# Add metabolites to the model
model.add_metabolites([metabolite1, metabolite2, ...])

# Add genes (usually automated via gene_reaction_rule)
model.genes += [gene1, gene2, ...]
```

### Removing Components

```python
# Remove reactions
model.remove_reactions([reaction1, reaction2, ...])
model.remove_reactions(["PFK", "FBA"])

# Remove metabolites (also removes from associated reactions)
model.remove_metabolites([metabolite1, metabolite2, ...])

# Remove genes (usually removed via gene_reaction_rule)
model.genes.remove(gene)
```

### Modifying Reactions

```python
# Set bounds
reaction.bounds = (lower, upper)
reaction.lower_bound = 0.0
reaction.upper_bound = 1000.0

# Modify stoichiometry
reaction.add_metabolites({metabolite: 1.0})
reaction.subtract_metabolites({metabolite: 1.0})

# Change Gene-Reaction Rule (GPR)
reaction.gene_reaction_rule = "(gene1 and gene2) or gene3"

# Knockout
reaction.knock_out()
gene.knock_out()
```

### Model Copying

```python
# Deep copy (independent model)
model_copy = model.copy()

# Copy specific reactions
new_model = Model("subset")
reactions_to_copy = [model.reactions.PFK, model.reactions.FBA]
new_model.add_reactions(reactions_to_copy)
```

## Context Management

Use context managers for temporary modifications:

```python
# Changes are automatically reverted after the with block ends
with model:
    model.objective = "ATPM"
    model.reactions.EX_glc__D_e.lower_bound = -5.0
    model.genes.b0008.knock_out()
    solution = model.optimize()

# Model state is restored here

# Multiple nested contexts
with model:
    model.objective = "ATPM"
    with model:
        model.genes.b0008.knock_out()
        # Both modifications take effect
    # Only the objective change takes effect

# Context management for reactions
with model:
    model.reactions.PFK.knock_out()
    # Equivalent to: reaction.lower_bound = reaction.upper_bound = 0
```

## Reaction and Metabolite Attributes

### Reaction Attributes

```python
reaction.id                      # Unique identifier
reaction.name                    # Human-readable name
reaction.subsystem               # Pathway/Subsystem
reaction.bounds                  # (lower_bound, upper_bound)
reaction.lower_bound
reaction.upper_bound
reaction.reversibility          # Boolean (lower_bound < 0)
reaction.gene_reaction_rule     # GPR string
reaction.genes                  # Set of associated Gene objects
reaction.metabolites            # {metabolite: stoichiometry} dictionary

# Methods
reaction.reaction               # Stoichiometric equation string
reaction.build_reaction_string() # Same as above
reaction.check_mass_balance()   # Returns unbalanced terms or an empty dictionary
reaction.get_coefficient(metabolite_id)
reaction.add_metabolites({metabolite: coeff})
reaction.subtract_metabolites({metabolite: coeff})
reaction.knock_out()
```

### Metabolite Attributes

```python
metabolite.id                   # Unique identifier
metabolite.name                 # Human-readable name
metabolite.formula              # Formula
metabolite.charge               # Charge
metabolite.compartment          # Compartment ID
metabolite.reactions            # FrozenSet of associated reactions

# Methods
metabolite.summary()            # Print production/consumption summary
metabolite.copy()
```

### Gene Attributes

```python
gene.id                         # Unique identifier
gene.name                       # Human-readable name
gene.functional                 # Boolean, active status
gene.reactions                  # FrozenSet of associated reactions

# Methods
gene.knock_out()
```

## Model Validation

### Consistency Checks

```python
from cobra.manipulation import check_mass_balance, check_metabolite_compartment_formula

# Check mass balance for all reactions
unbalanced = {}
for reaction in model.reactions:
    balance = reaction.check_mass_balance()
    if balance:
        unbalanced[reaction.id] = balance

# Check if metabolite formulas are valid
check_metabolite_compartment_formula(model)
```

### Model Statistics

```python
# Basic statistics
print(f"Reactions: {len(model.reactions)}")
print(f"Metabolites: {len(model.metabolites)}")
print(f"Genes: {len(model.genes)}")

# Advanced statistics
print(f"Exchanges: {len(model.exchanges)}")
print(f"Demands: {len(model.demands)}")

# Blocked reactions
from cobra.flux_analysis import find_blocked_reactions
blocked = find_blocked_reactions(model)
print(f"Blocked reactions: {len(blocked)}")

# Essential genes
from cobra.flux_analysis import find_essential_genes
essential = find_essential_genes(model)
print(f"Essential genes: {len(essential)}")
```

## Summary Methods

```python
# Model summary
model.summary()                  # Overall model information

# Metabolite summary
model.metabolites.atp_c.summary()

# Reaction summary
model.reactions.PFK.summary()

# Summary combined with FVA
model.summary(fva=0.95)         # Includes FVA at 95% optimality
```

## Common Patterns

### Batch Analysis Pattern

```python
results = []
for condition in conditions:
    with model:
        # Apply conditions
        setup_condition(model, condition)

        # Analysis
        solution = model.optimize()

        # Store results
        results.append({
            "condition": condition,
            "growth": solution.objective_value,
            "status": solution.status
        })

df = pd.DataFrame(results)
```

### Systematic Knockout Pattern

```python
knockout_results = []
for gene in model.genes:
    with model:
        gene.knock_out()

        solution = model.optimize()

        knockout_results.append({
            "gene": gene.id,
            "growth": solution.objective_value if solution.status == "optimal" else 0,
            "status": solution.status
        })

df = pd.DataFrame(knockout_results)
```

### Parameter Sweep Pattern

```python
parameter_values = np.linspace(0, 20, 21)
results = []

for value in parameter_values:
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -value

        solution = model.optimize()

        results.append({
            "glucose_uptake": value,
            "growth": solution.objective_value,
            "acetate_secretion": solution.fluxes["EX_ac_e"]
        })

df = pd.DataFrame(results)
```

This quick reference covers the most commonly used COBRApy functions and patterns. For full API documentation, please refer to https://cobrapy.readthedocs.io/