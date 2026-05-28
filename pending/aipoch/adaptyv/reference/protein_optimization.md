# Protein Sequence Optimization

## Overview

Before submitting protein sequences for experimental testing, it is recommended to optimize them using computational tools to improve expression, solubility, and stability. This pre-screening reduces experimental costs and increases success rates.

## Common Protein Expression Issues

### 1. Unpaired Cysteines

**Problem:**
- Unpaired cysteines can form unwanted disulfide bonds
- Leads to protein aggregation and misfolding
- Reduces expression yield and stability

**Solution:**
- Remove unpaired cysteines unless functionally required
- Pair cysteines appropriately for structural disulfides
- Replace with Serine or Alanine at non-critical positions

**Example:**
```python
# Check cysteine pairing
from Bio.Seq import Seq

def check_cysteines(sequence):
    cys_count = sequence.count('C')
    if cys_count % 2 != 0:
        print(f"Warning: Odd number of cysteines ({cys_count})")
    return cys_count
```

### 2. Excessive Hydrophobicity

**Problem:**
- Long hydrophobic patches promote aggregation
- Exposed hydrophobic residues lead to clumping
- Poor solubility in aqueous buffers

**Solution:**
- Maintain balanced hydropathy profiles
- Use short, flexible linkers between domains
- Reduce surface-exposed hydrophobic residues

**Metrics:**
- Kyte-Doolittle hydropathy plot
- GRAVY score (Grand Average of Hydropathy)
- pSAE (percentage of Solvent Accessible hydrophobic Exposure)

### 3. Low Solubility

**Problem:**
- Protein precipitates during expression or purification
- Formation of inclusion bodies
- Difficult downstream processing

**Solution:**
- Pre-screen using solubility prediction tools
- Apply sequence optimization algorithms
- Add solubility-enhancing tags if necessary

## Computational Optimization Tools

### NetSolP - Initial Solubility Screening

**Purpose:** Rapid solubility prediction for filtering sequences.

**Method:** Machine learning model trained on *E. coli* expression data.

**Usage:**
```python
# Install: uv pip install requests
import requests

def predict_solubility_netsolp(sequence):
    """Predict protein solubility using NetSolP web service"""
    url = "https://services.healthtech.dtu.dk/services/NetSolP-1.0/api/predict"

    data = {
        "sequence": sequence,
        "format": "fasta"
    }

    response = requests.post(url, data=data)
    return response.json()

# Example
sequence = "MKVLWAALLGLLGAAA..."
result = predict_solubility_netsolp(sequence)
print(f"Solubility score: {result['score']}")
```

**Interpretation:**
- Score > 0.5: Likely soluble
- Score < 0.5: Likely insoluble
- Use for initial filtering before more expensive predictions

**When to Use:**
- First pass on large libraries
- Quick validation of designs
- Prioritizing sequences for experimental testing

### SoluProt - Comprehensive Solubility Prediction

**Purpose:** Advanced solubility prediction with higher accuracy.

**Method:** Deep learning model combining sequence and structural features.

**Usage:**
```python
# Install: uv pip install soluprot
from soluprot import predict_solubility

def screen_variants_soluprot(sequences):
    """Screen solubility for multiple sequences"""
    results = []
    for name, seq in sequences.items():
        score = predict_solubility(seq)
        results.append({
            'name': name,
            'sequence': seq,
            'solubility_score': score,
            'predicted_soluble': score > 0.6
        })
    return results

# Example
sequences = {
    'variant_1': 'MKVLW...',
    'variant_2': 'MATGV...'
}

results = screen_variants_soluprot(sequences)
soluble_variants = [r for r in results if r['predicted_soluble']]
```

**Interpretation:**
- Score > 0.6: High confidence in solubility
- Score 0.4-0.6: Uncertain, may need optimization
- Score < 0.4: Likely problematic

**When to Use:**
- After initial NetSolP filtering
- When higher prediction accuracy is needed
- Before committing to expensive synthesis/testing

### SolubleMPNN - Sequence Redesign

**Purpose:** Redesign protein sequences to improve solubility while maintaining function.

**Method:** Graph neural network that suggests mutations to increase solubility.

**Usage:**
```python
# Install: uv pip install soluble-mpnn
from soluble_mpnn import optimize_sequence

def optimize_for_solubility(sequence, structure_pdb=None):
    """
    Redesign sequence for improved solubility

    Args:
        sequence: Original amino acid sequence
        structure_pdb: Optional PDB file for structure-aware design

    Returns:
        Optimized sequence variants sorted by predicted solubility
    """

    variants = optimize_sequence(
        sequence=sequence,
        structure=structure_pdb,
        num_variants=10,
        temperature=0.1  # Lower = more conservative mutations
    )

    return variants

# Example
original_seq = "MKVLWAALLGLLGAAA..."
optimized_variants = optimize_for_solubility(original_seq)

for i, variant in enumerate(optimized_variants):
    print(f"Variant {i+1}:")
    print(f"  Sequence: {variant['sequence']}")
    print(f"  Solubility score: {variant['solubility_score']}")
    print(f"  Mutations: {variant['mutations']}")
```

**Design Strategy:**
- **Conservative** (temperature=0.1): Minimal changes, safest
- **Moderate** (temperature=0.3): Balance of change and safety
- **Aggressive** (temperature=0.5): More mutations, higher risk

**When to Use:**
- Primary tool for sequence optimization
- Improving problematic sequences by default
- Generating diverse soluble variants

**Best Practices:**
- Generate 10-50 variants per sequence
- Use structural information whenever possible (improves accuracy)
- Verify critical functional residues are preserved
- Test multiple temperature settings

### ESM (Evolutionary Scale Modeling) - Sequence Likelihood

**Purpose:** Assess "naturalness" of protein sequences based on evolutionary patterns.

**Method:** Protein language model trained on millions of natural sequences.

**Usage:**
```python
# Install: uv pip install fair-esm
import torch
from esm import pretrained

def score_sequence_esm(sequence):
    """
    Calculate ESM likelihood score for a sequence
    Higher score indicates more natural/stable sequence
    """

    model, alphabet = pretrained.esm2_t33_650M_UR50D()
    batch_converter = alphabet.get_batch_converter()

    data = [("protein", sequence)]
    _, _, batch_tokens = batch_converter(data)

    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33])
        token_logprobs = results["logits"].log_softmax(dim=-1)

    # Calculate perplexity (or mean log-likelihood) as quality metric
    sequence_score = token_logprobs.mean().item()

    return sequence_score

# Example - Compare variants
sequences = {
    'original': 'MKVLW...',
    'optimized_1': 'MKVLS...',
    'optimized_2': 'MKVLA...'
}

for name, seq in sequences.items():
    score = score_sequence_esm(seq)
    print(f"{name}: ESM score = {score:.3f}")
```

**Interpretation:**
- Higher score → Sequence is more "natural"
- Use to avoid unlikely mutations
- Balance with functional requirements

**When to Use:**
- Filtering synthetic designs
- Comparing SolubleMPNN variants
- Ensuring sequences are not overly artificial
- Avoiding expression bottlenecks

**Combining with Design:**
```python
def rank_variants_by_esm(variants):
    """Rank protein variants by ESM likelihood"""
    scored = []
    for v in variants:
        esm_score = score_sequence_esm(v['sequence'])
        v['esm_score'] = esm_score
        scored.append(v)

    # Sort by combined score of solubility and ESM
    scored.sort(
        key=lambda x: x['solubility_score'] * x['esm_score'],
        reverse=True
    )

    return scored
```

### ipTM - Interface Stability (AlphaFold-Multimer)

**Purpose:** Assess protein-protein interface stability and binding confidence.

**Method:** Interface predicted TM-score from AlphaFold-Multimer predictions.

**Usage:**
```python
# Requires AlphaFold-Multimer installation
# Or use ColabFold for easier access

def predict_interface_stability(protein_a_seq, protein_b_seq):
    """
    Predict interface stability using AlphaFold-Multimer

    Returns ipTM score: Higher = more stable interface
    """
    from colabfold import run_alphafold_multimer

    sequences = {
        'chainA': protein_a_seq,
        'chainB': protein_b_seq
    }

    result = run_alphafold_multimer(sequences)

    return {
        'ipTM': result['iptm'],
        'pTM': result['ptm'],
        'pLDDT': result['plddt']
    }

# Example for Antibody-Antigen binding
antibody_seq = "EVQLVESGGGLVQPGG..."
antigen_seq = "MKVLWAALLGLLGAAA..."

stability = predict_interface_stability(antibody_seq, antigen_seq)
print(f"Interface pTM: {stability['ipTM']:.3f}")

# Interpretation
if stability['ipTM'] > 0.7:
    print("High confidence interface")
elif stability['ipTM'] > 0.5:
    print("Medium confidence interface")
else:
    print("Low confidence interface - Consider redesign")
```

**Interpretation:**
- ipTM > 0.7: Strong predicted interface
- ipTM 0.5-0.7: Moderate interface confidence
- ipTM < 0.5: Weak interface, consider redesign

**When to Use:**
- Antibody-antigen design
- Protein-protein interaction engineering
- Validating binding interfaces
- Comparing interface variants

### pSAE - Solvent Accessible Hydrophobic Exposure

**Purpose:** Quantify exposed hydrophobic residues that promote aggregation.

**Method:** Calculate percentage of Solvent Accessible Surface Area (SASA) occupied by hydrophobic residues.

**Usage:**
```python
# Requires structure (PDB file or AlphaFold prediction)
# Install: uv pip install biopython

from Bio.PDB import PDBParser, DSSP
import numpy as np

def calculate_psae(pdb_file):
    """
    Calculate percentage of Solvent Accessible Hydrophobic Exposure (pSAE)

    Lower pSAE = Better solubility
    """

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('protein', pdb_file)

    # Run DSSP for solvent accessibility
    model = structure[0]
    dssp = DSSP(model, pdb_file, acc_array='Wilke')

    hydrophobic = ['ALA', 'VAL', 'ILE', 'LEU', 'MET', 'PHE', 'TRP', 'PRO']

    total_sasa = 0
    hydrophobic_sasa = 0

    for residue in dssp:
        res_name = residue[1]
        rel_accessibility = residue[3]

        total_sasa += rel_accessibility
        if res_name in hydrophobic:
            hydrophobic_sasa += rel_accessibility

    psae = (hydrophobic_sasa / total_sasa) * 100

    return psae

# Example
pdb_file = "protein_structure.pdb"
psae_score = calculate_psae(pdb_file)
print(f"pSAE: {psae_score:.2f}%")

# Interpretation
if psae_score < 25:
    print("Good solubility expected")
elif psae_score < 35:
    print("Moderate solubility")
else:
    print("High aggregation risk")
```

**Interpretation:**
- pSAE < 25%: Low aggregation risk
- pSAE 25-35%: Moderate risk
- pSAE > 35%: High aggregation risk

**When to Use:**
- Analyzing designed structures
- Validating AlphaFold predictions
- Identifying aggregation hotspots
- Guiding surface mutations

## Recommended Optimization Workflow

### Step 1: Initial Screening (Fast)

```python
def initial_screening(sequences):
    """
    Quick first pass using NetSolP
    Filter out obviously problematic sequences
    """
    passed = []
    for name, seq in sequences.items():
        netsolp_score = predict_solubility_netsolp(seq)
        if netsolp_score > 0.5:
            passed.append((name, seq))

    return passed
```

### Step 2: Detailed Assessment (Medium)

```python
def detailed_assessment(filtered_sequences):
    """
    More thorough analysis using SoluProt and ESM
    Rank sequences by multiple criteria
    """
    results = []
    for name, seq in filtered_sequences:
        soluprot_score = predict_solubility(seq)
        esm_score = score_sequence_esm(seq)

        combined_score = soluprot_score * 0.7 + esm_score * 0.3

        results.append({
            'name': name,
            'sequence': seq,
            'soluprot': soluprot_score,
            'esm': esm_score,
            'combined': combined_score
        })

    results.sort(key=lambda x: x['combined'], reverse=True)
    return results
```

### Step 3: Sequence Optimization (If Needed)

```python
def optimize_problematic_sequences(sequences_needing_optimization):
    """
    Redesign problematic sequences using SolubleMPNN
    Returns improved variants
    """
    optimized = []
    for name, seq in sequences_needing_optimization:
        # Generate multiple variants
        variants = optimize_sequence(
            sequence=seq,
            num_variants=10,
            temperature=0.2
        )

        # Score variants with ESM
        for variant in variants:
            variant['esm_score'] = score_sequence_esm(variant['sequence'])

        # Keep best variants
        variants.sort(
            key=lambda x: x['solubility_score'] * x['esm_score'],
            reverse=True
        )

        optimized.extend(variants[:3])  # Top 3 variants per sequence

    return optimized
```

### Step 4: Structure-Based Validation (For Key Sequences)

```python
def structure_validation(top_candidates):
    """
    Predict structure and calculate pSAE for top candidates
    Final check before experimental testing
    """
    validated = []
    for candidate in top_candidates:
        # Predict structure with AlphaFold
        structure_pdb = predict_structure_alphafold(candidate['sequence'])

        # Calculate pSAE
        psae = calculate_psae(structure_pdb)

        candidate['psae'] = psae
        candidate['pass_structure_check'] = psae < 30

        validated.append(candidate)

    return validated
```

### Complete Workflow Example

```python
def complete_optimization_pipeline(initial_sequences):
    """
    End-to-end optimization pipeline

    Input: Dict of {name: sequence}
    Output: Sorted list of optimized and validated sequences
    """

    print("Step 1: Initial screening with NetSolP...")
    filtered = initial_screening(initial_sequences)
    print(f"  Passed: {len(filtered)}/{len(initial_sequences)}")

    print("Step 2: Detailed assessment with SoluProt & ESM...")
    assessed = detailed_assessment(filtered)

    # Split into good and needing optimization
    good_sequences = [s for s in assessed if s['soluprot'] > 0.6]
    needs_optimization = [s for s in assessed if s['soluprot'] <= 0.6]

    print(f"  Good sequences: {len(good_sequences)}")
    print(f"  Need optimization: {len(needs_optimization)}")

    if needs_optimization:
        print("Step 3: Optimizing problematic sequences with SolubleMPNN...")
        optimized = optimize_problematic_sequences(needs_optimization)
        all_sequences = good_sequences + optimized
    else:
        all_sequences = good_sequences

    print("Step 4: Structure-based validation for top candidates...")
    top_20 = all_sequences[:20]
    final_validated = structure_validation(top_20)

    # Final ranking
    final_validated.sort(
        key=lambda x: (
            x['pass_structure_check'],
            x['combined'],
            -x['psae']
        ),
        reverse=True
    )

    return final_validated

# Usage
initial_library = {
    'variant_1': 'MKVLWAALLGLLGAAA...',
    'variant_2': 'MATGVLWAALLGLLGA...',
    # ... more sequences
}

optimized_library = complete_optimization_pipeline(initial_library)

# Submit top sequences to Adaptyv
top_sequences_for_testing = optimized_library[:50]
```

## Best Practices Summary

1. **Always pre-screen** before experimental testing
2. **Use NetSolP first** to quickly filter large libraries
3. **Use SolubleMPNN** as the default tool for optimization
4. **Validate with ESM** to avoid unnatural sequences
5. **Calculate pSAE** for structure-based verification
6. **Test multiple variants** per design to account for prediction uncertainty
7. **Keep controls** - include wild-type or known good sequences
8. **Iterate** - use experimental results to improve prediction models

## Integration with Adaptyv

Submit sequences to Adaptyv after computational optimization:

```python
# After optimization pipeline runs
optimized_sequences = complete_optimization_pipeline(initial_library)

# Prepare FASTA format
fasta_content = ""
for seq_data in optimized_sequences[:50]:  # Top 50
    fasta_content += f">{seq_data['name']}\n{seq_data['sequence']}\n"

# Submit to Adaptyv
import requests
response = requests.post(
    "https://kq5jp7qj7wdqklhsxmovkzn4l40obksv.lambda-url.eu-central-1.on.aws/experiments",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "sequences": fasta_content,
        "experiment_type": "expression",
        "metadata": {
            "optimization_method": "SolubleMPNN_ESM_pipeline",
            "computational_scores": [s['combined'] for s in optimized_sequences[:50]]
        }
    }
)
```

## Troubleshooting Common Issues

**Issue: All sequences score low on solubility**
- Check for unusual amino acids
- Verify FASTA format
- Consider if the protein family is naturally insoluble
- May still require experimental validation despite poor predictions

**Issue: SolubleMPNN changes functionally important residues**
- Provide structure file to preserve spatial constraints
- Mask critical residues to prevent mutation
- Lower temperature parameter for conservative changes
- Manually revert problematic mutations

**Issue: Low ESM scores after optimization**
- Optimization may be too aggressive
- Try lower temperature in SolubleMPNN
- Balance solubility vs. naturalness
- Consider that some optimization may require unnatural mutations

**Issue: Predictions don't match experimental results**
- Predictions are probabilistic, not deterministic
- Host system and conditions affect expression
- Some proteins may defy prediction models
- Use predictions as enrichment, not absolute filters
