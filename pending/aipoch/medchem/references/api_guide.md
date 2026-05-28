# Medchem API Reference

Comprehensive reference for all medchem modules and functions.

## Module: medchem.rules

### Class: RuleFilters

Filter molecules based on various medicinal chemistry rules.

**Constructor:**
```python
RuleFilters(rule_list: List[str])
```

**Parameters:**
- `rule_list`: List of rule names to apply. See available rules below.

**Methods:**

```python
__call__(mols: List[Chem.Mol], n_jobs: int = 1, progress: bool = False) -> Dict
```
- `mols`: List of RDKit molecule objects
- `n_jobs`: Number of parallel jobs (-1 to use all cores)
- `progress`: Show progress bar
- **Returns**: A dictionary containing results for each rule

**Example:**
```python
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_five", "rule_of_cns"])
results = rfilter(mols=mol_list, n_jobs=-1, progress=True)
```

### Module: medchem.rules.basic_rules

Independent rule functions that can be applied to a single molecule.

#### rule_of_five()

```python
rule_of_five(mol: Union[str, Chem.Mol]) -> bool
```

Lipinski's Rule of Five for evaluating oral bioavailability.

**Criteria:**
- Molecular Weight ≤ 500 Da
- LogP ≤ 5
- Hydrogen Bond Donors ≤ 5
- Hydrogen Bond Acceptors ≤ 10

**Parameters:**
- `mol`: SMILES string or RDKit molecule object

**Returns**: True if the molecule meets all criteria

#### rule_of_three()

```python
rule_of_three(mol: Union[str, Chem.Mol]) -> bool
```

Rule of Three for fragment screening libraries.

**Criteria:**
- Molecular Weight ≤ 300 Da
- LogP ≤ 3
- Hydrogen Bond Donors ≤ 3
- Hydrogen Bond Acceptors ≤ 3
- Rotatable Bonds ≤ 3
- Polar Surface Area ≤ 60 Å²

#### rule_of_oprea()

```python
rule_of_oprea(mol: Union[str, Chem.Mol]) -> bool
```

Oprea lead-like criteria for lead optimization.

**Criteria:**
- Molecular Weight: 200-350 Da
- LogP: -2 to 4
- Rotatable Bonds ≤ 7
- Number of Rings ≤ 4

#### rule_of_cns()

```python
rule_of_cns(mol: Union[str, Chem.Mol]) -> bool
```

Central Nervous System (CNS) drug-likeness rules.

**Criteria:**
- Molecular Weight ≤ 450 Da
- LogP: -1 to 5
- Hydrogen Bond Donors ≤ 2
- TPSA ≤ 90 Å²

#### rule_of_leadlike_soft()

```python
rule_of_leadlike_soft(mol: Union[str, Chem.Mol]) -> bool
```

Soft lead-like criteria (more tolerant).

**Criteria:**
- Molecular Weight: 250-450 Da
- LogP: -3 to 4
- Rotatable Bonds ≤ 10

#### rule_of_leadlike_strict()

```python
rule_of_leadlike_strict(mol: Union[str, Chem.Mol]) -> bool
```

Strict lead-like criteria (more restrictive).

**Criteria:**
- Molecular Weight: 200-350 Da
- LogP: -2 to 3.5
- Rotatable Bonds ≤ 7
- Number of Rings: 1-3

#### rule_of_veber()

```python
rule_of_veber(mol: Union[str, Chem.Mol]) -> bool
```

Veber rules for evaluating oral bioavailability.

**Criteria:**
- Rotatable Bonds ≤ 10
- TPSA ≤ 140 Å²

#### rule_of_reos()

```python
rule_of_reos(mol: Union[str, Chem.Mol]) -> bool
```

Rapid Elimination of Swill (REOS) filter.

**Criteria:**
- Molecular Weight: 200-500 Da
- LogP: -5 to 5
- Hydrogen Bond Donors: 0-5
- Hydrogen Bond Acceptors: 0-10

#### rule_of_drug()

```python
rule_of_drug(mol: Union[str, Chem.Mol]) -> bool
```

Comprehensive drug-likeness criteria.

**Criteria:**
- Passes Rule of Five
- Passes Veber rules
- No PAINS substructures

#### golden_triangle()

```python
golden_triangle(mol: Union[str, Chem.Mol]) -> bool
```

"Golden Triangle" criteria for drug-likeness balance.

**Criteria:**
- 200 ≤ MW ≤ 50×LogP + 400
- LogP: -2 to 5

#### pains_filter()

```python
pains_filter(mol: Union[str, Chem.Mol]) -> bool
```

Pan-Assay Interference Compounds (PAINS) filter.

**Returns**: True if the molecule **does not contain** PAINS substructures

---

## Module: medchem.structural

### Class: CommonAlertsFilters

Filter common structural alerts derived from ChEMBL and literature.

**Constructor:**
```python
CommonAlertsFilters()
```

**Methods:**

```python
__call__(mols: List[Chem.Mol], n_jobs: int = 1, progress: bool = False) -> List[Dict]
```

Apply common alerts filters to a list of molecules.

**Returns**: A list of dictionaries containing:
- `has_alerts`: Boolean indicating if the molecule has alerts
- `alert_details`: List of matched alert patterns
- `num_alerts`: Number of alerts found

```python
check_mol(mol: Chem.Mol) -> Tuple[bool, List[str]]
```

Check structural alerts for a single molecule.

**Returns**: (has_alerts, list_of_alert_names) tuple

### Class: NIBRFilters

Novartis NIBR medicinal chemistry filters.

**Constructor:**
```python
NIBRFilters()
```

**Methods:**

```python
__call__(mols: List[Chem.Mol], n_jobs: int = 1, progress: bool = False) -> List[bool]
```

Apply NIBR filters to molecules.

**Returns**: List of booleans (True if passed)

### Class: LillyDemeritsFilters

Eli Lilly demerit-based structural alert system (275 rules).

**Constructor:**
```python
LillyDemeritsFilters()
```

**Methods:**

```python
__call__(mols: List[Chem.Mol], n_jobs: int = 1, progress: bool = False) -> List[Dict]
```

Calculate Lilly demerits for molecules.

**Returns**: A list of dictionaries containing:
- `demerits`: Total demerit score
- `passes`: Boolean (True if demerits ≤ 100)
- `matched_patterns`: List of matched patterns and their scores

---

## Module: medchem.functional

High-level functional API for common operations.

### nibr_filter()

```python
nibr_filter(mols: List[Chem.Mol], n_jobs: int = 1) -> List[bool]
```

Apply NIBR filters using the functional API.

**Parameters:**
- `mols`: List of molecules
- `n_jobs`: Parallelization level

**Returns**: List of pass/fail booleans

### common_alerts_filter()

```python
common_alerts_filter(mols: List[Chem.Mol], n_jobs: int = 1) -> List[Dict]
```

Apply common alerts filters using the functional API.

**Returns**: List of result dictionaries

### lilly_demerits_filter()

```python
lilly_demerits_filter(mols: List[Chem.Mol], n_jobs: int = 1) -> List[Dict]
```

Calculate Lilly demerits using the functional API.

---

## Module: medchem.groups

### Class: ChemicalGroup

Detect specific chemical groups in molecules.

**Constructor:**
```python
ChemicalGroup(groups: List[str], custom_smarts: Optional[Dict[str, str]] = None)
```

**Parameters:**
- `groups`: List of predefined group names
- `custom_smarts`: Dictionary mapping custom group names to SMARTS patterns

**Predefined groups:**
- `"hinge_binders"`: Kinase hinge-binding motifs
- `"phosphate_binders"`: Phosphate binding groups
- `"michael_acceptors"`: Michael acceptor electrophiles
- `"reactive_groups"`: General reactive functional groups

**Methods:**

```python
has_match(mols: List[Chem.Mol]) -> List[bool]
```

Check if molecules contain any of the specified groups.

```python
get_matches(mol: Chem.Mol) -> Dict[str, List[Tuple]]
```

Get detailed match information for a single molecule.

**Returns**: Dictionary mapping group names to lists of atom indices

```python
get_all_matches(mols: List[Chem.Mol]) -> List[Dict]
```

Get match information for all molecules.

**Example:**
```python
group = mc.groups.ChemicalGroup(groups=["hinge_binders", "phosphate_binders"])
matches = group.get_all_matches(mol_list)
```

---

## Module: medchem.catalogs

### Class: NamedCatalogs

Access curated chemical catalogs.

**Available catalogs:**
- `"functional_groups"`: Common functional groups
- `"protecting_groups"`: Protecting group structures
- `"reagents"`: Common reagents
- `"fragments"`: Standard fragments

**Usage:**
```python
catalog = mc.catalogs.NamedCatalogs.get("functional_groups")
matches = catalog.get_matches(mol)
```

---

## Module: medchem.complexity

Calculate molecular complexity metrics.

### calculate_complexity()

```python
calculate_complexity(mol: Chem.Mol, method: str = "bertz") -> float
```

Calculate the complexity score of a molecule.

**Parameters:**
- `mol`: RDKit molecule
- `method`: Complexity metric ("bertz", "whitlock", "barone")

**Returns**: Complexity score (higher is more complex)

### Class: ComplexityFilter

Filter molecules by complexity thresholds.

**Constructor:**
```python
ComplexityFilter(max_complexity: float, method: str = "bertz")
```

**Methods:**

```python
__call__(mols: List[Chem.Mol], n_jobs: int = 1) -> List[bool]
```

Filter molecules exceeding the complexity threshold.

---

## Module: medchem.constraints

### Class: Constraints

Apply custom property-based constraints.

**Constructor:**
```python
Constraints(
    mw_range: Optional[Tuple[float, float]] = None,
    logp_range: Optional[Tuple[float, float]] = None,
    tpsa_max: Optional[float] = None,
    tpsa_range: Optional[Tuple[float, float]] = None,
    hbd_max: Optional[int] = None,
    hba_max: Optional[int] = None,
    rotatable_bonds_max: Optional[int] = None,
    rings_range: Optional[Tuple[int, int]] = None,
    aromatic_rings_max: Optional[int] = None,
)
```

**Parameters:** All parameters are optional. Specify only the constraints you need.

**Methods:**

```python
__call__(mols: List[Chem.Mol], n_jobs: int = 1) -> List[Dict]
```

Apply constraints to molecules.

**Returns**: A list of dictionaries containing:
- `passes`: Boolean indicating if all constraints are met
- `violations`: List of names of failed constraints

**Example:**
```python
constraints = mc.constraints.Constraints(
    mw_range=(200, 500),
    logp_range=(-2, 5),
    tpsa_max=140
)
results = constraints(mols=mol_list, n_jobs=-1)
```

---

## Module: medchem.query

Query language for complex filtering.

### parse()

```python
parse(query: str) -> Query
```

Parse a medchem query string into a Query object.

**Query Syntax:**
- Operators: `AND`, `OR`, `NOT`
- Comparisons: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Properties: `complexity`, `lilly_demerits`, `mw`, `logp`, `tpsa`
- Rules: `rule_of_five`, `rule_of_cns`, etc.
- Filters: `common_alerts`, `nibr_filter`, `pains_filter`

**Query Examples:**
```python
"rule_of_five AND NOT common_alerts"
"rule_of_cns AND complexity < 400"
"mw > 200 AND mw < 500 AND logp < 5"
"(rule_of_five OR rule_of_oprea) AND NOT pains_filter"
```

### Class: Query

**Methods:**

```python
apply(mols: List[Chem.Mol], n_jobs: int = 1) -> List[bool]
```

Apply the parsed query to molecules.

**Example:**
```python
query = mc.query.parse("rule_of_five AND NOT common_alerts")
results = query.apply(mols=mol_list, n_jobs=-1)
passing_mols = [mol for mol, passes in zip(mol_list, results) if passes]
```

---

## Module: medchem.utils

Helper functions for handling molecules.

### batch_process()

```python
batch_process(
    mols: List[Chem.Mol],
    func: Callable,
    n_jobs: int = 1,
    progress: bool = False,
    batch_size: Optional[int] = None
) -> List
```

Process molecules in parallel batches.

**Parameters:**
- `mols`: List of molecules
- `func`: Function to apply to each molecule
- `n_jobs`: Number of parallel worker processes
- `progress`: Show progress bar
- `batch_size`: Size of processing batches

### standardize_mol()

```python
standardize_mol(mol: Chem.Mol) -> Chem.Mol
```

Standardize molecular representation (cleanup, neutralize charges, etc.).

---

## Common Patterns

### Pattern: Parallel Processing

All filters support parallelization:

```python
# Use all CPU cores
results = filter_object(mols=mol_list, n_jobs=-1, progress=True)

# Use a specific number of cores
results = filter_object(mols=mol_list, n_jobs=4, progress=True)
```

### Pattern: Combining Multiple Filters

```python
import medchem as mc

# Apply multiple filters
rule_filter = mc.rules.RuleFilters(rule_list=["rule_of_five"])
alert_filter = mc.structural.CommonAlertsFilters()
lilly_filter = mc.structural.LillyDemeritsFilters()

# Get results
rule_results = rule_filter(mols=mol_list, n_jobs=-1)
alert_results = alert_filter(mols=mol_list, n_jobs=-1)
lilly_results = lilly_filter(mols=mol_list, n_jobs=-1)

# Combine criteria
passing_mols = [
    mol for i, mol in enumerate(mol_list)
    if rule_results[i]["passes"]
    and not alert_results[i]["has_alerts"]
    and lilly_results[i]["passes"]
]
```

### Pattern: Using DataFrames

```python
import pandas as pd
import datamol as dm
import medchem as mc

# Load data
df = pd.read_csv("molecules.csv")
df["mol"] = df["smiles"].apply(dm.to_mol)

# Apply filters
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_five", "rule_of_cns"])
results = rfilter(mols=df["mol"].tolist(), n_jobs=-1)

# Add results to dataframe
df["passes_ro5"] = [r["rule_of_five"] for r in results]
df["passes_cns"] = [r["rule_of_cns"] for r in results]

# Filter dataframe
filtered_df = df[df["passes_ro5"] & df["passes_cns"]]
```