# Medicinal Chemistry Rules and Filters Catalog

This document provides a comprehensive catalog of all available rules, structural alerts, and filters in medicinal chemistry.

## Table of Contents

1. [Drug-likeness Rules](#drug-likeness-rules)
2. [Lead-likeness Rules](#lead-likeness-rules)
3. [Fragment Rules](#fragment-rules)
4. [Central Nervous System (CNS) Rules](#cns-rules)
5. [Structural Alert Filters](#structural-alert-filters)
6. [Chemical Group Patterns](#chemical-group-patterns)

---

## Drug-likeness Rules

### Lipinski Rule of Five

**References:** Lipinski et al., Adv Drug Deliv Rev (1997) 23:3-25

**Purpose:** Predicting oral bioavailability

**Criteria:**
- Molecular Weight ≤ 500 Da
- LogP ≤ 5
- Number of Hydrogen Bond Donors ≤ 5
- Number of Hydrogen Bond Acceptors ≤ 10

**Usage:**
```python
mc.rules.basic_rules.rule_of_five(mol)
```

**Notes:**
- One of the most widely used filters in drug discovery
- Approximately 90% of orally active drugs comply with these rules
- Exceptions exist, particularly for natural products and antibiotics

---

### Veber Rule

**References:** Veber et al., J Med Chem (2002) 45:2615-2623

**Purpose:** Supplementary criteria for oral bioavailability

**Criteria:**
- Number of Rotatable Bonds ≤ 10
- Topological Polar Surface Area (TPSA) ≤ 140 Å²

**Usage:**
```python
mc.rules.basic_rules.rule_of_veber(mol)
```

**Notes:**
- Complementary to the Rule of Five
- TPSA correlates with cell permeability
- Rotatable bonds affect molecular flexibility

---

### Rule of Drug

**Purpose:** Comprehensive drug-likeness assessment

**Criteria:**
- Pass Rule of Five
- Pass Veber Rule
- No PAINS substructures

**Usage:**
```python
mc.rules.basic_rules.rule_of_drug(mol)
```

---

### REOS (Rapid Elimination of Swill)

**References:** Walters & Murcko, Adv Drug Deliv Rev (2002) 54:255-271

**Purpose:** Filter out compounds unlikely to be drug-like

**Criteria:**
- Molecular Weight: 200-500 Da
- LogP: -5 to 5
- Number of Hydrogen Bond Donors: 0-5
- Number of Hydrogen Bond Acceptors: 0-10

**Usage:**
```python
mc.rules.basic_rules.rule_of_reos(mol)
```

---

### Golden Triangle

**References:** Johnson et al., J Med Chem (2009) 52:5487-5500

**Purpose:** Balancing lipophilicity and molecular weight

**Criteria:**
- 200 ≤ MW ≤ 50 × LogP + 400
- LogP: -2 to 5

**Usage:**
```python
mc.rules.basic_rules.golden_triangle(mol)
```

**Notes:**
- Defines the optimal physicochemical space
- Visual representation on an MW vs LogP plot resembles a triangle

---

## Lead-likeness Rules

### Oprea Rule

**References:** Oprea et al., J Chem Inf Comput Sci (2001) 41:1308-1315

**Purpose:** Identifying lead-like compounds for optimization

**Criteria:**
- Molecular Weight: 200-350 Da
- LogP: -2 to 4
- Number of Rotatable Bonds ≤ 7
- Number of Rings ≤ 4

**Usage:**
```python
mc.rules.basic_rules.rule_of_oprea(mol)
```

**Rationale:** Lead compounds should leave "room for growth" during optimization

---

### Lead-like Rule (Soft)

**Purpose:** Permissive lead-like criteria

**Criteria:**
- Molecular Weight: 250-450 Da
- LogP: -3 to 4
- Number of Rotatable Bonds ≤ 10

**Usage:**
```python
mc.rules.basic_rules.rule_of_leadlike_soft(mol)
```

---

### Lead-like Rule (Strict)

**Purpose:** Restrictive lead-like criteria

**Criteria:**
- Molecular Weight: 200-350 Da
- LogP: -2 to 3.5
- Number of Rotatable Bonds ≤ 7
- Number of Rings: 1-3

**Usage:**
```python
mc.rules.basic_rules.rule_of_leadlike_strict(mol)
```

---

## Fragment Rules

### Rule of Three

**References:** Congreve et al., Drug Discov Today (2003) 8:876-877

**Purpose:** Screening fragment libraries for Fragment-Based Drug Discovery (FBDD)

**Criteria:**
- Molecular Weight ≤ 300 Da
- LogP ≤ 3
- Number of Hydrogen Bond Donors ≤ 3
- Number of Hydrogen Bond Acceptors ≤ 3
- Number of Rotatable Bonds ≤ 3
- Polar Surface Area ≤ 60 Å²

**Usage:**
```python
mc.rules.basic_rules.rule_of_three(mol)
```

**Notes:**
- Fragments grow into lead compounds during optimization
- Lower complexity allows for more starting points

---

## CNS Rules

### CNS Rule

**Purpose:** Drug-likeness for Central Nervous System drugs

**Criteria:**
- Molecular Weight ≤ 450 Da
- LogP: -1 to 5
- Number of Hydrogen Bond Donors ≤ 2
- TPSA ≤ 90 Å²

**Usage:**
```python
mc.rules.basic_rules.rule_of_cns(mol)
```

**Rationale:**
- Blood-Brain Barrier (BBB) penetration requires specific properties
- Lower TPSA and HBD counts improve BBB permeability
- Strict limits reflect the challenges of CNS R&D

---

## Structural Alert Filters

### PAINS (Pan-Assay Interference Compounds)

**References:** Baell & Holloway, J Med Chem (2010) 53:2719-2740

**Purpose:** Identifying compounds that interfere with biological assays

**Categories:**
- Catechols
- Quinones
- Rhodanines
- Hydroxyphenylhydrazones
- Alkyl/aryl aldehydes
- Michael acceptors (specific patterns)

**Usage:**
```python
mc.rules.basic_rules.pains_filter(mol)
# Returns True if no PAINS are found
```

**Notes:**
- PAINS compounds show activity in multiple assays via non-specific mechanisms
- Common false positives in screening campaigns
- Should be deprioritized during lead selection

---

### Common Alerts Filters

**Source:** Derived from ChEMBL curation and medicinal chemistry literature

**Purpose:** Flagging common problematic structural patterns

**Alert Categories:**
1. **Reactive Groups**
   - Epoxides
   - Aziridines
   - Acid halides
   - Isocyanates

2. **Metabolic Liability**
   - Hydrazines
   - Thioureas
   - Anilines (specific patterns)

3. **Aggregators**
   - Polycyclic aromatic systems
   - Long aliphatic chains

4. **Toxicophores**
   - Nitroaromatics
   - Aromatic N-oxides
   - Specific heterocycles

**Usage:**
```python
alert_filter = mc.structural.CommonAlertsFilters()
has_alerts, details = alert_filter.check_mol(mol)
```

**Return Format:**
```python
{
    "has_alerts": True,
    "alert_details": ["reactive_epoxide", "metabolic_hydrazine"],
    "num_alerts": 2
}
```

---

### NIBR Filters

**Source:** Novartis Institutes for BioMedical Research

**Purpose:** Industrial medicinal chemistry screening rules

**Features:**
- Proprietary screening sets developed based on Novartis experience
- Balances drug-likeness with practical medicinal chemistry needs
- Includes structural alerts and property filters

**Usage:**
```python
nibr_filter = mc.structural.NIBRFilters()
results = nibr_filter(mols=mol_list, n_jobs=-1)
```

**Return Format:** Boolean list (True = Pass)

---

### Lilly Demerits Filter

**References:** Based on Eli Lilly medicinal chemistry rules

**Source:** 275 structural patterns accumulated over 18 years

**Purpose:** Identifying assay interference and problematic functional groups

**Mechanism:**
- Each matched pattern increases demerits
- Molecules exceeding 100 points are rejected
- Some patterns add 10-50 points, others add 100+ (immediate rejection)

**Demerit Categories:**

1. **High Demerits (>50):**
   - Known toxic groups
   - Highly reactive functional groups
   - Strong metal chelators

2. **Medium Demerits (20-50):**
   - Metabolic liability
   - Aggregation-prone structures
   - Frequent hitters

3. **Low Demerits (5-20):**
   - Minor concerns
   - Context-dependent issues

**Usage:**
```python
lilly_filter = mc.structural.LillyDemeritsFilters()
results = lilly_filter(mols=mol_list, n_jobs=-1)
```

**Return Format:**
```python
{
    "demerits": 35,
    "passes": True,  # (demerits ≤ 100)
    "matched_patterns": [
        {"pattern": "phenolic_ester", "demerits": 20},
        {"pattern": "aniline_derivative", "demerits": 15}
    ]
}
```

---

## Chemical Group Patterns

### Hinge Binders

**Purpose:** Identifying kinase hinge-binding motifs

**Common Patterns:**
- Aminopyridines
- Aminopyrimidines
- Indazoles
- Benzimidazoles

**Usage:**
```python
group = mc.groups.ChemicalGroup(groups=["hinge_binders"])
has_hinge = group.has_match(mol_list)
```

**Application:** Kinase inhibitor design

---

### Phosphate Binders

**Purpose:** Identifying phosphate-binding groups

**Common Patterns:**
- Basic amines with specific geometries
- Guanidines
- Arginine mimetics

**Usage:**
```python
group = mc.groups.ChemicalGroup(groups=["phosphate_binders"])
```

**Application:** Kinase inhibitors, phosphatase inhibitors

---

### Michael Acceptors

**Purpose:** Identifying electrophilic Michael acceptor groups

**Common Patterns:**
- α,β-unsaturated carbonyls
- α,β-unsaturated nitriles
- Vinyl sulfones
- Acrylamides

**Usage:**
```python
group = mc.groups.ChemicalGroup(groups=["michael_acceptors"])
```

**Notes:**
- May be desirable for covalent inhibitors
- Often flagged as reactive alerts in screening

---

### Reactive Groups

**Purpose:** Identifying general reactive functional groups

**Common Patterns:**
- Epoxides
- Aziridines
- Acid halides
- Isocyanates
- Sulfonyl chlorides

**Usage:**
```python
group = mc.groups.ChemicalGroup(groups=["reactive_groups"])
```

---

## Custom SMARTS Patterns

Define custom structural patterns using SMARTS:

```python
custom_patterns = {
    "my_warhead": "[C;H0](=O)C(F)(F)F",  # Trifluoromethyl ketone
    "my_scaffold": "c1ccc2c(c1)ncc(n2)N",  # Aminobenzimidazole
}

group = mc.groups.ChemicalGroup(
    groups=["hinge_binders"],
    custom_smarts=custom_patterns
)
```

---

## Filter Selection Guide

### Initial Screening (High-Throughput)

Recommended filters:
- Rule of Five
- PAINS Filter
- Common Alerts (Soft settings)

```python
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_five", "pains_filter"])
alert_filter = mc.structural.CommonAlertsFilters()
```

---

### Hit-to-Lead

Recommended filters:
- Oprea Rule or Lead-like Rule (Soft)
- NIBR Filters
- Lilly Demerits

```python
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_oprea"])
nibr_filter = mc.structural.NIBRFilters()
lilly_filter = mc.structural.LillyDemeritsFilters()
```

---

### Lead Optimization

Recommended filters:
- Rule of Drug
- Lead-like Rule (Strict)
- Comprehensive structural alert analysis
- Complexity filters

```python
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_drug", "rule_of_leadlike_strict"])
alert_filter = mc.structural.CommonAlertsFilters()
complexity_filter = mc.complexity.ComplexityFilter(max_complexity=400)
```

---

### CNS Targets

Recommended filters:
- CNS Rule
- Simplified PAINS criteria (for CNS)
- BBB permeability constraints

```python
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_cns"])
constraints = mc.constraints.Constraints(
    tpsa_max=90,
    hbd_max=2,
    mw_range=(300, 450)
)
```

---

### Fragment-Based Drug Discovery (FBDD)

Recommended filters:
- Rule of Three
- Minimum complexity
- Basic reactive group checks

```python
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_three"])
complexity_filter = mc.complexity.ComplexityFilter(max_complexity=250)
```

---

## Important Notes

### False Positives and False Negatives

**Filters are guidelines, not absolute standards:**

1. **False Positives** (Good drugs flagged):
   - ~10% of marketed drugs do not comply with the Rule of Five
   - Natural products often violate standard rules
   - Prodrugs often intentionally break rules
   - Antibiotics and antivirals often fall outside the norms

2. **False Negatives** (Poor compounds pass):
   - Passing does not guarantee success
   - Cannot capture target-specific issues
   - Cannot fully predict in vivo properties

### Context-Specific Application

**Different research contexts require different standards:**

- **Target Class:** Kinases, GPCRs, and ion channels have different optimal property spaces
- **Mode of Action:** Small molecules vs PROTACs vs Molecular glues
- **Route of Administration:** Oral vs Intravenous (IV) vs Topical
- **Disease Area:** CNS vs Oncology vs Infectious diseases
- **Stage:** Screening vs Hit-to-Lead vs Lead Optimization

### Augmenting with Machine Learning

Modern approaches combine rules with Machine Learning (ML):

```python
# Rule-based pre-screening
rule_results = mc.rules.RuleFilters(rule_list=["rule_of_five"])(mols)
filtered_mols = [mol for mol, r in zip(mols, rule_results) if r["passes"]]

# ML model scoring on the filtered set
ml_scores = ml_model.predict(filtered_mols)

# Integrated decision making
final_candidates = [
    mol for mol, score in zip(filtered_mols, ml_scores)
    if score > threshold
]
```

---

## References

1. Lipinski CA et al. Adv Drug Deliv Rev (1997) 23:3-25
2. Veber DF et al. J Med Chem (2002) 45:2615-2623
3. Oprea TI et al. J Chem Inf Comput Sci (2001) 41:1308-1315
4. Congreve M et al. Drug Discov Today (2003) 8:876-877
5. Baell JB & Holloway GA. J Med Chem (2010) 53:2719-2740
6. Johnson TW et al. J Med Chem (2009) 52:5487-5500
7. Walters WP & Murcko MA. Adv Drug Deliv Rev (2002) 54:255-271
8. Hann MM & Oprea TI. Curr Opin Chem Biol (2004) 8:255-263
9. Rishton GM. Drug Discov Today (1997) 2:382-384