# ESM3 API Reference

## Overview

ESM3 is a frontier multimodal generative language model capable of reasoning about the sequence, structure, and function of proteins. It uses Iterative Masked Language Modeling to simultaneously generate content across these three modalities.

## Model Architecture

**ESM3 Model Series:**

| Model ID | Parameters | Availability | Use Case |
|----------|-----------|--------------|----------|
| `esm3-sm-open-v1` | 1.4B | Open weights (local) | Development, testing, learning |
| `esm3-medium-2024-08` | 7B | Forge API only | Production, balancing quality and speed |
| `esm3-large-2024-03` | 98B | Forge API only | Highest quality, scientific research |
| `esm3-medium-multimer-2024-09` | 7B | Forge API only | Protein complexes (experimental) |

**Core Features:**
- Simultaneous reasoning on sequence, structure, and function
- Step-controlled iterative generation
- Support for cross-modal partial prompting
- Chain-of-thought generation for complex designs
- Temperature control for managing generation diversity

## Core API Components

### ESMProtein Class

Represents the core data structure for a protein, containing optional sequence, structure, and functional information.

**Constructor:**

```python
from esm.sdk.api import ESMProtein

protein = ESMProtein(
    sequence="MPRTKEINDAGLIVHSP",           # Amino acid sequence (optional)
    coordinates=coordinates_array,          # 3D structure (optional)
    function_annotations=[...],             # Functional annotations (optional)
    secondary_structure="HHHEEEECCC",       # Secondary structure annotations (optional)
    sasa=sasa_array                        # Solvent accessibility (optional)
)
```

**Key Methods:**

```python
# Load from PDB file
protein = ESMProtein.from_pdb("protein.pdb")

# Export to PDB format
pdb_string = protein.to_pdb()

# Save to file
with open("output.pdb", "w") as f:
    f.write(protein.to_pdb())
```

**Masking Rules:**

Use `_` (underscore) to represent positions masked during the generation process:

```python
# Mask positions 5-10 for generation
protein = ESMProtein(sequence="MPRT______AGLIVHSP")

# Fully masked sequence (de novo generation)
protein = ESMProtein(sequence="_" * 200)

# Partial structure (some coordinates can be None)
protein = ESMProtein(
    sequence="MPRTKEIND",
    coordinates=partial_coords  # Some positions can be None
)
```

### GenerationConfig Class

Controls generation behavior and parameters.

**Basic Configuration:**

```python
from esm.sdk.api import GenerationConfig

config = GenerationConfig(
    track="sequence",              # Track to generate: "sequence", "structure", or "function"
    num_steps=8,                  # Number of unmasking iteration steps
    temperature=0.7,              # Sampling temperature (0.0-1.0)
    top_p=None,                   # Nucleus sampling threshold
    condition_on_coordinates_only=False  # Used for structural conditioning
)
```

**Parameter Details:**

- **track**: Which modality to generate
  - `"sequence"`: Generate amino acid sequence
  - `"structure"`: Generate 3D coordinates
  - `"function"`: Generate functional annotations

- **num_steps**: Number of iterative unmasking steps
  - Higher steps = slower speed, but potentially better quality
  - Typical range: 8-100, depending on sequence length
  - For full sequence generation: suggested approx sequence_length / 2

- **temperature**: Controls randomness
  - 0.0: Fully deterministic (greedy decoding)
  - 0.5-0.7: Balanced exploration
  - 1.0: Maximum diversity
  - Higher values increase novelty but may decrease quality

- **top_p**: Nucleus sampling parameter
  - Limits sampling to the top cumulative probability range
  - Value: 0.0-1.0 (e.g., 0.9 means sampling from the top 90% probability mass)
  - Used to control diversity without extreme sampling

- **condition_on_coordinates_only**: Structural conditioning mode
  - `True`: Constrain only based on backbone coordinates (ignore sequence)
  - Suitable for Inverse Folding tasks

### ESM3InferenceClient Interface

A unified interface for local and remote inference.

**Local Model Loading:**

```python
from esm.models.esm3 import ESM3

# Load and automatically assign device
model = ESM3.from_pretrained("esm3-sm-open-v1").to("cuda")

# Or explicitly specify device
model = ESM3.from_pretrained("esm3-sm-open-v1").to("cpu")
```

**Generation Methods:**

```python
# Basic generation
protein_output = model.generate(protein_input, config)

# With explicit track specification
protein_output = model.generate(
    protein_input,
    GenerationConfig(track="sequence", num_steps=16, temperature=0.6)
)
```

**Forward Pass (Advanced):**

```python
# Get raw model logits for custom sampling
protein_tensor = model.encode(protein)
output = model.forward(protein_tensor)
logits = model.decode(output)
```

## Common Usage Patterns

### 1. Sequence Completion

Fill masked regions of a protein sequence:

```python
# Define partial sequence
protein = ESMProtein(sequence="MPRTK____LIVHSP____END")

# Generate missing positions
config = GenerationConfig(track="sequence", num_steps=12, temperature=0.5)
completed = model.generate(protein, config)

print(f"Original:  {protein.sequence}")
print(f"Completed: {completed.sequence}")
```

### 2. Structure Prediction

Predict 3D structure from a sequence:

```python
# Input: sequence only
protein = ESMProtein(sequence="MPRTKEINDAGLIVHSPQWFYK")

# Generate structure
config = GenerationConfig(track="structure", num_steps=len(protein.sequence))
protein_with_structure = model.generate(protein, config)

# Save as PDB
with open("predicted_structure.pdb", "w") as f:
    f.write(protein_with_structure.to_pdb())
```

### 3. Inverse Folding

Design a sequence for a target structure:

```python
# Load target structure
target = ESMProtein.from_pdb("target.pdb")

# Remove sequence, keep structure
target.sequence = None

# Generate sequence folding into this structure
config = GenerationConfig(
    track="sequence",
    num_steps=50,
    temperature=0.7,
    condition_on_coordinates_only=True
)
designed = model.generate(target, config)

print(f"Designed sequence: {designed.sequence}")
```

### 4. Function-Conditioned Generation

Generate proteins with specific functions:

```python
from esm.sdk.api import FunctionAnnotation

# Specify desired function
protein = ESMProtein(
    sequence="_" * 150,
    function_annotations=[
        FunctionAnnotation(
            label="enzymatic_activity",
            start=30,
            end=90
        )
    ]
)

# Generate sequence with this function
config = GenerationConfig(track="sequence", num_steps=75, temperature=0.6)
functional_protein = model.generate(protein, config)
```

### 5. Multi-track Generation (Chain-of-thought)

Iteratively generate across multiple tracks:

```python
# Start from partial sequence
protein = ESMProtein(sequence="MPRT" + "_" * 100)

# Step 1: Complete sequence
protein = model.generate(
    protein,
    GenerationConfig(track="sequence", num_steps=50, temperature=0.6)
)

# Step 2: Predict structure for the completed sequence
protein = model.generate(
    protein,
    GenerationConfig(track="structure", num_steps=50)
)

# Step 3: Predict function
protein = model.generate(
    protein,
    GenerationConfig(track="function", num_steps=20)
)

print(f"Final sequence: {protein.sequence}")
print(f"Functions: {protein.function_annotations}")
```

### 6. Variant Generation

Generate multiple variants of a protein:

```python
import numpy as np

base_sequence = "MPRTKEINDAGLIVHSPQWFYK"
variants = []

for i in range(10):
    # Randomly mask positions
    seq_list = list(base_sequence)
    mask_indices = np.random.choice(len(seq_list), size=5, replace=False)
    for idx in mask_indices:
        seq_list[idx] = '_'

    protein = ESMProtein(sequence=''.join(seq_list))

    # Generate variant
    variant = model.generate(
        protein,
        GenerationConfig(track="sequence", num_steps=8, temperature=0.8)
    )
    variants.append(variant.sequence)

print(f"Generated {len(variants)} variants")
```

## Advanced Topics

### Temperature Scheduling

Change temperature during the generation process for better control:

```python
def generate_with_temperature_schedule(model, protein, temperatures):
    """Annealed generation by lowering temperature."""
    current = protein
    steps_per_temp = 10

    for temp in temperatures:
        config = GenerationConfig(
            track="sequence",
            num_steps=steps_per_temp,
            temperature=temp
        )
        current = model.generate(current, config)

    return current

# Example: maintain diversity at start, converge to certainty at end
result = generate_with_temperature_schedule(
    model,
    protein,
    temperatures=[1.0, 0.8, 0.6, 0.4, 0.2]
)
```

### Constrained Generation

Keep specific regions fixed during generation:

```python
# Keep active site residues fixed
def mask_except_active_site(sequence, active_site_positions):
    """Mask all positions except specified ones."""
    seq_list = ['_'] * len(sequence)
    for pos in active_site_positions:
        seq_list[pos] = sequence[pos]
    return ''.join(seq_list)

# Define active site
active_site = [23, 24, 25, 45, 46, 89]
constrained_seq = mask_except_active_site(original_sequence, active_site)

protein = ESMProtein(sequence=constrained_seq)
result = model.generate(protein, GenerationConfig(track="sequence", num_steps=50))
```

### Secondary Structure Conditioning

Use secondary structure information in generation:

```python
# Define secondary structure (H=Helix, E=Sheet, C=Coil)
protein = ESMProtein(
    sequence="_" * 80,
    secondary_structure="CCHHHHHHHEEEEECCCHHHHHHCC" + "C" * 55
)

# Generate sequence with this structure
result = model.generate(
    protein,
    GenerationConfig(track="sequence", num_steps=40, temperature=0.6)
)
```

## Performance Optimization

### VRAM Management

For long proteins or batch processing:

```python
import torch

# Clear CUDA cache between generations
torch.cuda.empty_cache()

# Use half precision for VRAM efficiency
model = ESM3.from_pretrained("esm3-sm-open-v1").to("cuda").half()

# Segmented generation for ultra-long sequences
def chunk_generate(model, long_sequence, chunk_size=500):
    chunks = [long_sequence[i:i+chunk_size]
              for i in range(0, len(long_sequence), chunk_size)]
    results = []

    for chunk in chunks:
        protein = ESMProtein(sequence=chunk)
        result = model.generate(protein, GenerationConfig(track="sequence"))
        results.append(result.sequence)

    return ''.join(results)
```

### Batching Tips

When processing multiple proteins:

1. Sort by sequence length for efficient batching
2. Use padding for sequences of similar lengths
3. Process on GPU whenever possible
4. Implement checkpointing for long-running tasks
5. Use Forge API for large-scale processing (see `forge-api.md`)

## Error Handling

```python
try:
    protein = model.generate(protein_input, config)
except ValueError as e:
    print(f"Invalid input: {e}")
    # Handle invalid sequence or structure
except RuntimeError as e:
    print(f"Generation failed: {e}")
    # Handle model error
except torch.cuda.OutOfMemoryError:
    print("GPU out of memory - try a smaller model or CPU")
    # Degrade to CPU or smaller model
```

## Model-Specific Notes

**esm3-sm-open-v1:**
- Suitable for development and testing
- Lower quality than larger models
- Fast inference on consumer-grade GPUs
- Open weights allow for fine-tuning

**esm3-medium-2024-08:**
- Production-grade quality
- Good balance of speed and accuracy
- Requires Forge API access
- Recommended for most application scenarios

**esm3-large-2024-03:**
- State-of-the-art quality
- Slowest inference speed
- Used for mission-critical applications
- Best for novel protein design

## Citation

If using ESM3 in research, please cite:

```
Hayes, T. et al. (2025). Simulating 500 million years of evolution with a language model.
Science. DOI: 10.1126/science.ads0018
```