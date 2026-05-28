# Machine Learning Conference Writing Style Guide

This guide provides comprehensive writing instructions for NeurIPS, ICML, ICLR, CVPR, ECCV, ICCV, and other major machine learning and computer vision conferences.

**Last Updated**: 2024

---

## Overview

Machine Learning (ML) conferences prioritize **novelty**, **rigorous empirical evaluation**, and **reproducibility**. Papers are reviewed based on the clarity of contributions, the strength of baselines, the comprehensiveness of ablation studies, and an honest discussion of limitations.

### Core Philosophy

> "Facts speak louder than words—your experiments should prove your arguments, not just your prose."

**Primary Goal**: To advance the current state-of-the-art (SOTA) through innovative methods validated by rigorous experimentation.

---

## Audience and Tone

### Target Audience

- Machine learning researchers and practitioners
- Experts in specific sub-fields
- Individuals familiar with recent literature
- Readers expecting technical depth and precision

### Tone Characteristics

| Feature | Description |
|---------------|-------------|
| **Technical** | Rich in methodological details |
| **Precise** | Accurate terminology, no ambiguity |
| **Empirical** | Arguments are supported by experiments |
| **Direct** | Clearly stated contributions |
| **Honest** | Acknowledgment of limitations |

### Narrative Voice

- **First-person plural ("We")**: "We propose...", "Our method..."
- **Active voice**: "We introduce a novel architecture..."
- **Confident but restrained**: Strong arguments require strong evidence.

---

## Abstract

### Style Requirements

- **Dense and data-focused**
- **150-250 words** (varies by conference)
- **Results-first**: Include specific performance metrics
- **Fluid paragraphs** (not structured lists)

### Abstract Structure

1. **Problem** (1 sentence): What problem are you solving?
2. **Limitations of Existing Work** (1 sentence): Why are current methods insufficient?
3. **Your Method** (1-2 sentences): What is your approach?
4. **Key Results** (2-3 sentences): Specific numbers on benchmarks.
5. **Significance** (Optional, 1 sentence): Why does this matter?

### Abstract Example (NeurIPS Style)

```
Transformers have achieved remarkable success in sequence modeling but 
suffer from quadratic computational complexity, limiting their application 
to long sequences. We introduce FlashAttention-2, an IO-aware exact 
attention algorithm that achieves 2x speedup over FlashAttention and up 
to 9x speedup over standard attention on sequences up to 16K tokens. Our 
key insight is to reduce memory reads/writes by tiling and recomputation, 
achieving optimal IO complexity. On the Long Range Arena benchmark, 
FlashAttention-2 enables training with 8x longer sequences while matching 
standard attention accuracy. Combined with sequence parallelism, we train 
GPT-style models on sequences of 64K tokens at near-linear cost. We 
release optimized CUDA kernels achieving 80% of theoretical peak FLOPS 
on A100 GPUs. Code is available at [anonymous URL].
```

### Abstract Don'ts

❌ "We propose a novel method for X" (Too vague, no results)
❌ "Our method outperforms baselines" (No specific numbers)
❌ "This is an important problem" (Self-evident statement)

✅ Include specific metrics: "achieves 94.5% accuracy, 3.2% improvement"
✅ Include scale: "on 1M samples" or "16K token sequences"
✅ Include comparisons: "2x faster than previous SOTA"

---

## Introduction

### Structure (2-3 Pages)

ML paper introductions have a unique structure, often featuring a **numbered list of contributions**.

### Paragraph-by-Paragraph Guide

**Para 1: Problem Motivation**
- Why is this problem important?
- What are the application scenarios?
- Set the technical challenge.

```
"Large language models have demonstrated remarkable capabilities in 
natural language understanding and generation. However, their quadratic 
attention complexity presents a fundamental bottleneck for processing 
long documents, multi-turn conversations, and reasoning over extended 
contexts. As models scale to billions of parameters and context lengths 
extend to tens of thousands of tokens, efficient attention mechanisms 
become critical for practical deployment."
```

**Para 2: Limitations of Existing Work**
- What methods exist?
- Why are they not good enough?
- Technical analysis of limitations.

```
"Prior work has addressed this through sparse attention patterns, 
linear attention approximations, and low-rank factorizations. While 
these methods reduce theoretical complexity, they often sacrifice 
accuracy, require specialized hardware, or introduce approximation 
errors that compound in deep networks. Exact attention remains 
preferable when computational resources permit."
```

**Para 3: Your Method (High-level Overview)**
- What is your core insight?
- How does your method work conceptually?
- Why will it succeed?

```
"We observe that the primary bottleneck in attention is not computation 
but rather memory bandwidth—reading and writing the large N×N attention 
matrix dominates runtime on modern GPUs. We propose FlashAttention-2, 
which eliminates this bottleneck through a novel tiling strategy that 
computes attention block-by-block without materializing the full matrix."
```

**Para 4: List of Contributions (Crucial)**

This is a **mandatory and highly characteristic** part of ML conference papers:

```
Our contributions are as follows:

• We propose FlashAttention-2, an IO-aware exact attention algorithm 
  that achieves optimal memory complexity O(N²d/M) where M is GPU 
  SRAM size.

• We provide theoretical analysis showing that our algorithm achieves 
  2-4x fewer HBM accesses than FlashAttention on typical GPU 
  configurations.

• We demonstrate 2x speedup over FlashAttention and up to 9x over 
  standard PyTorch attention across sequence lengths from 256 to 64K 
  tokens.

• We show that FlashAttention-2 enables training with 8x longer 
  contexts on the same hardware, unlocking new capabilities for 
  long-range modeling.

• We release optimized CUDA kernels and PyTorch bindings at 
  [anonymous URL].
```

### Contribution Guidelines

| Good Contribution Item | Poor Contribution Item |
|--------------------------|-------------------------|
| Specific and quantifiable | Vague claims |
| Self-contained (readable alone) | Requires reading the whole paper to understand |
| Clearly distinct from other items | Repetitive or overlapping content |
| Emphasizes novelty | States obvious facts |

### Placement of Related Work

- **In Introduction**: Brief positioning (1-2 paragraphs).
- **Standalone Section**: Detailed comparison (placed at the end or before conclusion).
- **Appendix**: Extended discussion when space is limited.

---

## Method

### Structure (2-3 Pages)

```
METHOD
├── Problem Formulation
├── Method Overview / Architecture
├── Key Technical Components
│   ├── Component 1 (with equations)
│   ├── Component 2 (with equations)
│   └── Component 3 (with equations)
├── Theoretical Analysis (if applicable)
└── Implementation Details
```

### Mathematical Notation

- **Define all symbols**: "Let X ∈ ℝ^{N×d} denote the input sequence..."
- **Symbol consistency**: Use the same symbol for the same meaning throughout.
- **Number important equations**: For later reference.

### Algorithm Pseudocode

Include clear pseudocode to improve reproducibility:

```
Algorithm 1: FlashAttention-2 Forward Pass
─────────────────────────────────────────
Input: Q, K, V ∈ ℝ^{N×d}, block size B_r, B_c
Output: O ∈ ℝ^{N×d}

1:  Divide Q into T_r = ⌈N/B_r⌉ blocks
2:  Divide K, V into T_c = ⌈N/B_c⌉ blocks
3:  Initialize O = 0, ℓ = 0, m = -∞
4:  for i = 1 to T_r do
5:    Load Q_i from HBM to SRAM
6:    for j = 1 to T_c do
7:      Load K_j, V_j from HBM to SRAM
8:      Compute S_ij = Q_i K_j^T
9:      Update running max and sum
10:     Update O_i incrementally
11:   end for
12:   Write O_i to HBM
13: end for
14: return O
```

### Architecture Diagrams

- **Clear, publication-quality diagrams**
- **Label all components**
- **Show data flow with arrows**
- **Use consistent visual language**

---

## Experiments

### Structure (2-3 Pages)

```
EXPERIMENTS
├── Experimental Setup
│   ├── Datasets and Benchmarks
│   ├── Baselines
│   ├── Implementation Details
│   └── Evaluation Metrics
├── Main Results
│   └── Table/Figure with primary comparisons
├── Ablation Studies
│   └── Component-wise analysis
├── Analysis
│   ├── Scaling behavior
│   ├── Qualitative examples
│   └── Error analysis
└── Computational Efficiency
```

### Datasets and Benchmarks

- **Use standard benchmarks**: Establish comparability.
- **Report dataset statistics**: Size, splits, preprocessing.
- **Justify non-standard choices**: Explain why if using custom data.

### Baselines

**Critical for paper acceptance.** Should include:
- **Recent SOTA**: Don't just compare against outdated methods.
- **Fair comparison**: Same compute budget, hyperparameter tuning.
- **Ablated versions**: Your own method with key components removed.
- **Strong baselines**: Do not cherry-pick weak competitors.

### Main Results Table

Clear and comprehensive formatting:

```
Table 1: Results on Long Range Arena Benchmark (accuracy %)
──────────────────────────────────────────────────────────
Method          | ListOps | Text  | Retrieval | Image | Path  | Avg
──────────────────────────────────────────────────────────
Transformer     |  36.4   | 64.3  |   57.5    | 42.4  | 71.4  | 54.4
Performer       |  18.0   | 65.4  |   53.8    | 42.8  | 77.1  | 51.4
Linear Attn     |  16.1   | 65.9  |   53.1    | 42.3  | 75.3  | 50.5
FlashAttention  |  37.1   | 64.5  |   57.8    | 42.7  | 71.2  | 54.7
FlashAttn-2     |  37.4   | 64.7  |   58.2    | 42.9  | 71.8  | 55.0
──────────────────────────────────────────────────────────
```

### Ablation Studies (Mandatory)

Show what factors in your method are actually working:

```
Table 2: Ablation Study on FlashAttention-2 Components
──────────────────────────────────────────────────────
Variant                              | Speedup | Memory
──────────────────────────────────────────────────────
Full FlashAttention-2                |   2.0x  |  1.0x
  - without sequence parallelism     |   1.7x  |  1.0x
  - without recomputation            |   1.3x  |  2.4x
  - without block tiling             |   1.0x  |  4.0x
FlashAttention-1 (baseline)          |   1.0x  |  1.0x
──────────────────────────────────────────────────────
```

### What Ablations Should Show

- **Every component matters**: Removing it hurts performance.
- **Justification of design choices**: Why this architecture/hyperparameter?
- **Failure modes**: When does the method not work?
- **Sensitivity analysis**: Robustness to hyperparameters.

---

## Related Work

### Placement Options

1. **After Introduction**: Common in Computer Vision (CV) papers.
2. **Before Conclusion**: Common in NeurIPS/ICML.
3. **Appendix**: When space is extremely tight.

### Writing Style

- **Organize by theme**: Not chronologically.
- **Position your work**: How you differ from each branch of work.
- **Fair descriptions**: Do not misrepresent previous work.
- **Recent citations**: Include papers from 2023-2024.

### Example Structure

```
**Efficient Attention Mechanisms.** Prior work on efficient attention 
falls into three categories: sparse patterns (Beltagy et al., 2020; 
Zaheer et al., 2020), linear approximations (Katharopoulos et al., 2020; 
Choromanski et al., 2021), and low-rank factorizations (Wang et al., 
2020). Our work differs in that we focus on IO-efficient exact 
attention rather than approximations.

**Memory-Efficient Training.** Gradient checkpointing (Chen et al., 2016) 
and activation recomputation (Korthikanti et al., 2022) reduce memory 
by trading compute. We adopt similar ideas but apply them within the 
attention operator itself.
```

---

## Limitations Section

### Why It Matters

NeurIPS, ICML, and ICLR **increasingly require** this. An honest limitation analysis:
- Shows scientific maturity.
- Guides future work.
- Prevents overclaiming.

### What to Include

1. **Methodological limitations**: When does it fail?
2. **Experimental limitations**: What wasn't tested?
3. **Scope limitations**: What is outside the discussion?
4. **Computational limitations**: Resource requirements.

### Limitations Section Example

```
**Limitations.** While FlashAttention-2 provides substantial speedups, 
several limitations remain. First, our implementation is optimized for 
NVIDIA GPUs and does not support AMD or other hardware. Second, the 
speedup is most pronounced for medium to long sequences; for very short 
sequences (<256 tokens), the overhead of our kernel launch dominates. 
Third, we focus on dense attention; extending our approach to sparse 
attention patterns remains future work. Finally, our theoretical 
analysis assumes specific GPU memory hierarchy parameters that may not 
hold for future hardware generations.
```

---

## Reproducibility

### Reproducibility Checklist (NeurIPS/ICML)

Most ML conferences require a checklist covering:

- [ ] Code availability
- [ ] Dataset availability
- [ ] Specification of hyperparameters
- [ ] Reporting of random seeds
- [ ] Description of compute resources
- [ ] Reporting of number of runs and variance
- [ ] Statistical significance tests

### What to Report

**Hyperparameters**:
```
"We train with Adam (β₁=0.9, β₂=0.999, ε=1e-8) and learning rate 3e-4 
with linear warmup over 1000 steps and cosine decay. Batch size is 256 
across 8 A100 GPUs. We train for 100K steps (approximately 24 hours)."
```

**Random Seeds**:
```
"All experiments are averaged over 3 random seeds (0, 1, 2) with 
standard deviation reported in parentheses."
```

**Compute Resources**:
```
"Experiments were conducted on 8 NVIDIA A100-80GB GPUs. Total training 
time was approximately 500 GPU-hours."
```

---

## Figures

### Figure Quality

- **Prefer vector graphics**: PDF, SVG
- **High resolution for bitmaps**: 300+ dpi
- **Legible at publication size**: Test at actual column width.
- **Colorblind friendly**: Use different textures/shapes in addition to color.

### Common Figure Types

1. **Architecture Diagrams**: Visualize your method.
2. **Performance Plots**: Learning curves, scaling behavior.
3. **Comparison Tables**: Main results.
4. **Ablation Plots**: Contribution of components.
5. **Qualitative Examples**: Input/output samples.

### Captions

Captions should be self-explanatory:
- What is shown.
- How to read the plot.
- The core takeaway.

---

## References

### Citation Style

- **Numbered [1]** or **Author-Year (Smith et al., 2023)**.
- Check specific conference requirements.
- Be consistent throughout.

### Citation Guidelines

- **Cite recent work**: Usually requires 2022-2024 papers.
- **Avoid excessive self-citation**: Can raise bias concerns.
- **Cite arXiv properly**: If a formal version exists, cite the published one.
- **Include all relevant prior work**: Missing citations hurt reviews.

---

## Conference Specific Notes

### NeurIPS

- **8 pages** of main text + unlimited appendix/references.
- Sometimes requires a **Broader Impact** section.
- **Reproducibility Checklist** is mandatory.
- Uses OpenReview; reviews are public.

### ICML

- **8 pages** of main text + unlimited appendix/references.
- Emphasis on **Theory + Experiments** balance.
- Encourages reproducibility statements.

### ICLR

- **8 pages** of main text (can exceed in final version).
- OpenReview platform with **public reviews and discussion**.
- Interactive author response period.
- Extremely high emphasis on **novelty and insight**.

### CVPR/ICCV/ECCV

- **8 pages** of main text (including references).
- Encourages **supplementary videos**.
- Heavy emphasis on **visual results**.
- Benchmark performance is critical.

---

## Common Mistakes

1. **Weak Baselines**: Not comparing against recent SOTA.
2. **Missing Ablations**: Not showing the contribution of each component.
3. **Overpromising**: Claiming "We solve X" when you only solved a part of it.
4. **Vague Contributions**: "We propose a novel method".
5. **Poor Reproducibility**: Missing hyperparameters, seeds.
6. **Template Errors**: Using last year's style files.
7. **Anonymity Violations**: Leaking identity in blind review.
8. **Missing Limitation Analysis**: Not acknowledging failure modes.

---

## Rebuttal Tips

ML conferences have an author response period. Tips:
- **Prioritize core concerns**: Address the key issues raised by reviewers first.
- **Run requested experiments**: If time permits.
- **Be concise**: Reviewers have many rebuttals to read.
- **Be professional**: Even in the face of unfair reviews.
- **Cite specific line numbers**: "As stated in L127...".

---

## Pre-Submission Checklist

### Content
- [ ] Problem motivation is clear
- [ ] Contribution list is explicit
- [ ] Method description is complete
- [ ] Experiments are comprehensive
- [ ] Strong baselines are included
- [ ] Ablation studies are included
- [ ] Limitations are acknowledged

### Technical
- [ ] Correct conference style file used (current year version)
- [ ] Anonymized (no author names, no identifying URLs)
- [ ] Fits within page limits
- [ ] References are complete
- [ ] Supplementary material is organized

### Reproducibility
- [ ] Hyperparameters listed
- [ ] Random seeds specified
- [ ] Compute requirements stated
- [ ] Code/data availability noted
- [ ] Reproducibility checklist completed

---

## See Also

- `venue_writing_styles.md` - Overview of styles by conference
- `conferences_formatting.md` - Technical typesetting requirements
- `reviewer_expectations.md` - What ML reviewers look for