# Experiment Types and Workflows

## Overview

Adaptyv provides multiple experiment assay types for comprehensive protein characterization. Each experiment type has specific use cases, workflows, and data outputs.

## Binding Assays

### Description

Measures interactions between proteins and targets using Bio-Layer Interferometry (BLI). This is a label-free technology that monitors biomolecular binding in real-time.

### Use Cases

- Antibody-antigen binding characterization
- Receptor-ligand interaction analysis
- Protein-protein interaction studies
- Affinity maturation screening
- Epitope binning experiments

### Technology: Bio-Layer Interferometry (BLI)

BLI works by measuring the interference pattern of reflected light from two surfaces:
- **Reference Layer** - The biosensor tip surface
- **Bio-Layer** - The accumulated bound molecules

As molecules bind, the optical thickness increases, causing a wavelength shift proportional to the amount of binding.

**Advantages:**
- Label-free detection
- Real-time kinetic data
- High-throughput compatible
- Can run in crude samples
- Minimal sample consumption

### Measured Parameters

**Kinetic Constants:**
- **KD** - Equilibrium dissociation constant (binding affinity)
- **kon** - Association rate constant (on-rate)
- **koff** - Dissociation rate constant (off-rate)

**Typical Ranges:**
- Strong binders: KD < 1 nM
- Moderate binders: KD = 1-100 nM
- Weak binders: KD > 100 nM

### Workflow

1. **Sequence Submission** - Provide protein sequences in FASTA format
2. **Expression** - Protein expression in appropriate host system
3. **Purification** - Automated purification protocols
4. **BLI Assay** - Real-time binding measurement against specified target
5. **Analysis** - Kinetic curve fitting and quality assessment
6. **Results Delivery** - Binding parameters with confidence metrics

### Sample Requirements

- Protein sequence (standard amino acid codes)
- Target specifications (catalog or custom request)
- Buffer conditions (standard or custom)
- Expected concentration range (optional, helps optimize assay design)

### Results Format

```json
{
  "sequence_id": "antibody_variant_1",
  "target": "Human PD-L1",
  "measurements": {
    "kd": 2.5e-9,
    "kd_error": 0.3e-9,
    "kon": 1.8e5,
    "kon_error": 0.2e5,
    "koff": 4.5e-4,
    "koff_error": 0.5e-4
  },
  "quality_metrics": {
    "confidence": "high|medium|low",
    "r_squared": 0.97,
    "chi_squared": 0.02,
    "flags": []
  },
  "raw_data_url": "https://..."
}
```

## Expression Testing

### Description

Quantifies protein expression levels in various host systems to assess production feasibility and optimize sequences for manufacturing.

### Use Cases

- Screening for high-expression variants
- Codon usage optimization
- Identifying expression bottlenecks
- Selecting candidates for scale-up
- Comparing different expression systems

### Host Systems

Available expression platforms:
- **E. coli** - Fast, economical, high-efficiency prokaryotic system
- **Mammalian Cells** - Native post-translational modifications
- **Yeast** - Eukaryotic system with simpler growth requirements
- **Insect Cells** - Alternative eukaryotic platform

### Measured Parameters

- **Total Yield** (mg/L culture)
- **Soluble Fraction** (percentage)
- **Purity** (after initial purification)
- **Expression Time Course** (optional)

### Workflow

1. **Sequence Submission** - Provide protein sequences
2. **Construct Generation** - Cloning into expression vectors
3. **Expression** - Cultivation in specified host system
4. **Quantification** - Protein measurement via multiple methods
5. **Analysis** - Expression level comparison and ranking
6. **Results Delivery** - Yield data and recommendations

### Results Format

```json
{
  "sequence_id": "variant_1",
  "host_system": "E. coli",
  "measurements": {
    "total_yield_mg_per_l": 25.5,
    "soluble_fraction_percent": 78,
    "purity_percent": 92
  },
  "ranking": {
    "percentile": 85,
    "notes": "High expression, good solubility"
  }
}
```

## Thermostability Testing

### Description

Measures protein thermal stability to assess structural integrity, predict shelf-life, and identify stabilizing mutations.

### Use Cases

- Selecting thermostable variants
- Formulation development
- Shelf-life prediction
- Stability-driven protein engineering
- Quality control screening

### Measurement Techniques

**Differential Scanning Fluorimetry (DSF):**
- Monitors protein unfolding via fluorescent dye binding
- Determines melting temperature (Tm)
- High-throughput capability

**Circular Dichroism (CD):**
- Secondary structure analysis
- Thermal unfolding curves
- Reversibility assessment

### Measured Parameters

- **Tm** - Melting temperature (midpoint of unfolding)
- **ΔH** - Enthalpy of unfolding
- **Aggregation Temperature** (Tagg)
- **Reversibility** - Ability to refold after heating

### Workflow

1. **Sequence Submission** - Provide protein sequences
2. **Expression & Purification** - Standard protocols
3. **Thermostability Assay** - Temperature gradient analysis
4. **Data Analysis** - Curve fitting and parameter extraction
5. **Results Delivery** - Stability metrics and ranking

### Results Format

```json
{
  "sequence_id": "variant_1",
  "measurements": {
    "tm_celsius": 68.5,
    "tm_error": 0.5,
    "tagg_celsius": 72.0,
    "reversibility_percent": 85
  },
  "quality_metrics": {
    "curve_quality": "excellent",
    "cooperativity": "two-state"
  }
}
```

## Enzyme Activity Assays

### Description

Measures enzyme function, including substrate turnover, catalytic efficiency, and inhibitor sensitivity.

### Use Cases

- Screening for improved enzyme variants
- Substrate specificity profiling
- Inhibitor testing
- pH and temperature optimization
- Mechanistic studies

### Assay Types

**Continuous Assays:**
- Chromogenic substrates
- Fluorogenic substrates
- Real-time monitoring

**Endpoint Assays:**
- HPLC quantification
- Mass spectrometry
- Colorimetric detection

### Measured Parameters

**Kinetic Parameters:**
- **kcat** - Turnover number (catalytic rate constant)
- **KM** - Michaelis constant (substrate affinity)
- **kcat/KM** - Catalytic efficiency
- **IC50** - Inhibitor concentration for 50% effect

**Activity Metrics:**
- Specific Activity (units/mg protein)
- Relative Activity vs. Reference
- Substrate Specificity Profile

### Workflow

1. **Sequence Submission** - Provide enzyme sequences
2. **Expression & Purification** - Optimized for activity retention
3. **Activity Assay** - Substrate turnover measurement
4. **Kinetic Analysis** - Michaelis-Menten fitting
5. **Results Delivery** - Kinetic parameters and ranking

### Results Format

```json
{
  "sequence_id": "enzyme_variant_1",
  "substrate": "substrate_name",
  "measurements": {
    "kcat_per_second": 125,
    "km_micromolar": 45,
    "kcat_km": 2.8,
    "specific_activity": 180
  },
  "quality_metrics": {
    "confidence": "high",
    "r_squared": 0.99
  },
  "ranking": {
    "relative_activity": 1.8,
    "improvement_vs_wildtype": "80%"
  }
}
```

## Experiment Design Best Practices

### Sequence Submission

1. **Use Clear Identifiers** - Name sequences descriptively
2. **Include Controls** - Submit wild-type or reference sequences
3. **Batch Similar Variants** - Group related sequences in a single submission
4. **Validate Sequences** - Check for errors before submission

### Sample Size

- **Pilot Studies** - 5-10 sequences to test feasibility
- **Library Screening** - 50-500 sequences for variant exploration
- **Directed Evolution** - 10-50 sequences for fine-tuning
- **Large-Scale Campaigns** - 500+ sequences for ML-driven design

### Quality Control

Adaptyv includes automated QC steps:
- Expression verification before assays
- Replicate measurements for reliability
- Positive/negative controls in every batch
- Statistical validation of results

### Timeline Expectations

**Standard Turnaround:** ~21 days from submission to results

**Timeline Breakdown:**
- Construct Generation: 3-5 days
- Expression: 5-7 days
- Purification: 2-3 days
- Assay Execution: 3-5 days
- Analysis & QC: 2-3 days

**Factors Affecting Timeline:**
- Custom targets (+1-2 weeks)
- New assay development (+2-4 weeks)
- Large batches (may add 1 week)

### Cost Optimization

1. **Batch Submissions** - Lower average cost per sequence
2. **Standard Targets** - Catalog antigens are faster and cheaper
3. **Standard Conditions** - Custom buffers increase cost
4. **Computational Pre-screening** - Submit only promising candidates

## Combining Experiment Types

To characterize proteins comprehensively, multiple experiments can be combined:

**Therapeutic Antibody Development:**
1. Binding Assay → Identify high-affinity binders
2. Expression Test → Select manufacturable candidates
3. Thermostability → Ensure formulation stability

**Enzyme Engineering:**
1. Activity Assay → Screen for improved catalysis
2. Expression Test → Ensure producibility
3. Thermostability → Verify industrial robustness

**Serial vs. Parallel:**
- **Serial** - Use results from early assays to filter candidates
- **Parallel** - Run all assays simultaneously for faster results

## Data Integration

Experiment results can be integrated with computational workflows:

1. **Download Raw Data** via API
2. **Parse** results into standardized formats
3. **Feed into ML Models** for next round of design
4. **Track Experiments** using metadata tags
5. **Visualize** trends across design iterations

## Support and Troubleshooting

**Common Issues:**
- Low Expression → Consider sequence optimization (see protein_optimization.md)
- Poor Binding → Verify target specifications and expected range
- Variable Results → Check sequence quality and controls
- Incomplete Data → Contact support with experiment ID

**Getting Help:**
- Email: support@adaptyvbio.com
- Please include Experiment ID and specific questions
- Provide context (design goals, expected outcomes)
- Response time: Within 24 hours for active experiments
