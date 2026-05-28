---
name: buffer-calculator
description: Calculate precise buffer recipes with accurate mass and volume measurements for molecular biology and biochemistry. Supports PBS, RIPA, and TAE with concentration scaling, stock solution preparation, pH adjustment guidance, and step-by-step protocols.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Buffer Calculator

Calculate precise buffer formulations with accurate mass and volume measurements for molecular biology, biochemistry, and cell culture applications. Supports predefined common buffers and customizable calculations with pH adjustment guidance.

**Key Capabilities:**
- **Predefined Buffer Library**: PBS, RIPA, TAE with accurate molecular weights
- **Precise Mass Calculations**: Component masses to milligram precision
- **Volume-Based Components**: Handle liquid components (detergents, acids)
- **Concentration Scaling**: Scale from stock solutions (10X, 20X) to working concentrations
- **Step-by-Step Protocols**: Detailed preparation instructions with safety notes

---

## Input Validation

This skill accepts: a buffer type (PBS, RIPA, TAE), final volume in mL, and optional concentration multiplier (default 1X).

If the request does not involve calculating a laboratory buffer recipe — for example, asking to design a drug formulation, interpret pH meter readings, or perform chemical synthesis — do not proceed. Instead respond:
> "Buffer Calculator is designed to calculate precise buffer recipes for molecular biology and biochemistry. Please provide a buffer type (PBS, RIPA, or TAE) and target volume. For other formulation tasks, use a more appropriate tool."

---

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm buffer type, final volume, and concentration multiplier.
2. Validate that the buffer type is in the supported library; stop if unsupported without guessing.
3. Run the calculation script or apply the documented formula path.
4. Return a structured result separating assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

**Fallback:** If buffer type is missing or unrecognized, respond: "Buffer type not specified or not in library. Available buffers: PBS, RIPA, TAE. Use `--list` to see all options. Cannot calculate without a valid buffer type."

---

## Core Capabilities

### 1. Predefined Buffer Library

```python
from scripts.main import BufferCalculator
calc = BufferCalculator()
# List available buffers
for buf in calc.BUFFER_RECIPES.keys():
    print(f"  {buf}: pH {calc.BUFFER_RECIPES[buf].get('pH', 'N/A')}")
```

| Buffer | Application | pH | Key Components |
|--------|-------------|-----|----------------|
| **PBS** | Cell washing, immunostaining | 7.4 | NaCl, KCl, Phosphates |
| **RIPA** | Cell lysis, protein extraction | 7.4 | Tris, NaCl, Detergents |
| **TAE** | DNA electrophoresis | ~8.0 | Tris, Acetate, EDTA |
| **HEPES** | Cell culture, pH-sensitive assays | 7.0–7.6 | HEPES, NaCl |
| **Tris-HCl (pH 7.4)** | Protein buffers, Western blot | 7.4 | Tris, HCl |
| **Tris-HCl (pH 8.0)** | DNA/RNA work, enzyme reactions | 8.0 | Tris, HCl |
| **MOPS** | RNA electrophoresis, cell culture | 7.0–7.5 | MOPS, NaCl |

### 2. Mass Calculations

```python
result = calc.calculate("PBS", final_volume_ml=500, concentration_x=1.0)
for comp in result['components']:
    if 'amount_mg' in comp:
        print(f"{comp['component']}: {comp['amount_mg']:.2f} mg")
```

**Formula:** `mass (mg) = concentration (mM) × volume (mL) × MW (g/mol) / 1000`

### 3. Stock Solution Scaling

```python
# 10X PBS stock (500 mL)
stock_result = calc.calculate("PBS", final_volume_ml=500, concentration_x=10.0)
```

| Concentration | Storage Stability | Use Case |
|---------------|-------------------|----------|
| **1X** | 1–2 weeks at 4°C | Immediate use |
| **10X** | 3–6 months at 4°C | Regular daily use |
| **20X–50X** | 6–12 months frozen | Long-term storage |

---

## CLI Usage

```text
# Calculate PBS buffer (1X, 500 mL)
python scripts/main.py PBS --volume 500

# Calculate 10X PBS
python scripts/main.py PBS --volume 500 --concentration 10

# List all available buffers
python scripts/main.py --list
```

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `buffer` | string | **Yes** | Buffer type (PBS, RIPA, TAE) |
| `--volume`, `-v` | float | No | Final volume in mL |
| `--concentration`, `-c` | float | No (default 1.0) | Concentration multiplier (X) |
| `--list`, `-l` | flag | No | List available buffers |

---

## Output Requirements

Every final response must make these explicit:

- Objective or requested deliverable
- Inputs used (buffer type, volume, concentration) and assumptions introduced
- Calculation formula applied
- Core result: component masses/volumes with units
- Constraints and risks (verify MW for hydrates; check pH after preparation)
- Unresolved items and next-step checks (pH verification, sterile filtration if needed)

---

## Error Handling

- If buffer type is missing or unrecognized, list available options and request clarification. If the user provides component names, concentrations, and molecular weights, offer to calculate a custom recipe using the formula: `mass (mg) = concentration (mM) × volume (mL) × MW (g/mol) / 1000`.
- If volume is not provided, use a sensible default (500 mL) and state the assumption explicitly.
- If `scripts/main.py` fails, report the failure point and provide manual calculation fallback using the formula above.
- Do not fabricate molecular weights or component amounts.

---

## Quick Verification

Expected output for PBS 1X 500 mL:
- NaCl: 4,000 mg (137 mM × 500 mL × 58.44 g/mol / 1000)
- KCl: 100 mg (2.7 mM × 500 mL × 74.55 g/mol / 1000)
- Na₂HPO₄: 720 mg (10.1 mM × 500 mL × 141.96 g/mol / 1000)
- KH₂PO₄: 120 mg (1.76 mM × 500 mL × 136.09 g/mol / 1000)

---

## Common Pitfalls

- **Confusing mM and M**: 1000-fold concentration error — always verify units
- **Wrong molecular weight**: Account for hydrates (e.g., Na₂HPO₄·7H₂O vs anhydrous)
- **Adding water to acid**: Always add acid to water, never reverse
- **Incomplete dissolution**: Dissolve each component completely before adding next
- **pH drift during storage**: Check pH before each use for critical applications

---

## Molecular Weight Reference

| Compound | Formula | MW (g/mol) |
|----------|---------|------------|
| NaCl | NaCl | 58.44 |
| KCl | KCl | 74.55 |
| Tris base | C₄H₁₁NO₃ | 121.14 |
| EDTA (disodium) | C₁₀H₁₄N₂Na₂O₈·2H₂O | 372.24 |
| Na₂HPO₄ (anhydrous) | Na₂HPO₄ | 141.96 |
| KH₂PO₄ | KH₂PO₄ | 136.09 |

---

## References

- Cold Spring Harbor Protocols: https://cshprotocols.org
- Thermo Fisher Buffer Reference: https://www.thermofisher.com/buffers

→ Full troubleshooting: [references/troubleshooting.md](references/troubleshooting.md) (if available)
