---
name: bmi-bsa-calculator
description: Calculate Body Mass Index (BMI) and Body Surface Area (BSA) for clinical assessment, obesity screening, and chemotherapy dosing. Supports multiple BSA formulas (DuBois, Mosteller, Haycock), WHO weight classification, pediatric calculations, and metric/imperial input.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# BMI & BSA Calculator

Clinical calculator for anthropometric measurements used in health assessment, obesity screening, and chemotherapy dosing calculations.

**Key Capabilities:**
- **BMI Calculation**: Standard and adjusted BMI formulas with WHO classification
- **BSA Estimation**: Multiple validated formulas (DuBois, Mosteller, Haycock, Gehan-George)
- **Weight Classification**: WHO and CDC category assignment
- **Dosing Support**: Chemotherapy and medication dose calculations
- **Pediatric Support**: Age-appropriate norms and percentile calculations
- **Unit Flexibility**: Metric and imperial input support

---

## Input Validation

This skill accepts: weight (kg or lbs), height (cm or inches), and optional parameters (age, sex, drug dose per m², output format). All values must be physiologically plausible.

Valid ranges: weight 2–300 kg, height 50–250 cm.

If the request does not involve calculating BMI or BSA — for example, asking to diagnose a condition, interpret lab results, or provide dietary advice — do not proceed. Instead respond:
> "BMI & BSA Calculator is designed to calculate Body Mass Index and Body Surface Area for clinical screening and dosing support. Please provide weight and height values. For clinical diagnosis or treatment decisions, consult a qualified healthcare professional."

---

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm weight, height, and any optional parameters (age, sex, drug dose).
2. Validate inputs are within physiologically plausible ranges; stop if values are outside bounds.
3. Run the script or apply the documented calculation path.
4. Return a structured result separating assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

**Fallback:** If `--weight` or `--height` is missing, respond: "Required parameters missing. Please provide `--weight` (kg) and `--height` (cm). Cannot calculate BMI or BSA without both values."

---

## Core Capabilities

### 1. BMI Calculation

```python
from scripts.calculator import BMIBSACalculator
calc = BMIBSACalculator()
result = calc.calculate_bmi(weight_kg=70, height_cm=175, age=45, sex="male")
print(f"BMI: {result.bmi:.1f} kg/m²")
print(f"Category: {result.category}")
```

**BMI Categories (WHO):**

| Category | BMI Range | Clinical Significance |
|----------|-----------|----------------------|
| Underweight | < 18.5 | Malnutrition risk |
| Normal | 18.5–24.9 | Healthy range |
| Overweight | 25.0–29.9 | Increased risk |
| Obese I | 30.0–34.9 | High risk |
| Obese II | 35.0–39.9 | Very high risk |
| Obese III | ≥ 40.0 | Extremely high risk |

### 2. BSA Calculation

```python
bsa_results = calc.calculate_bsa(
    weight_kg=70, height_cm=175,
    formulas=["dubois", "mosteller", "haycock", "gehan_george"]
)
```

**BSA Formulas:**

| Formula | Best For |
|---------|----------|
| **DuBois** | Adults (most common) |
| **Mosteller** | Adults (simplified) |
| **Haycock** | Pediatrics |
| **Gehan-George** | Oncology |
| **Yu** | Asian populations |

### 3. Drug Dosing

```python
dose = calc.calculate_dose(bsa=1.79, drug="carboplatin", dose_per_m2=400, max_dose=800)
```

Common BSA-based doses: Carboplatin (Calvert formula), 5-FU 400–600 mg/m², Doxorubicin 60–75 mg/m², Paclitaxel 135–175 mg/m².

### 4. Pediatric Calculations

```python
pediatric = calc.pediatric_mode(weight_kg=25, height_cm=120, age_years=8, sex="female")
print(f"BMI-for-age percentile: {pediatric.bmi_percentile}%")
```

---

## CLI Usage

```text
# Calculate BMI and BSA
python scripts/main.py --weight 70 --height 175

# Calculate with drug dosing
python scripts/main.py --weight 70 --height 175 --dose 100

# Output as JSON
python scripts/main.py --weight 70 --height 175 --format json --output results.json
```

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--weight`, `-w` | float | **Yes** | Weight in kilograms |
| `--height`, `-H` | float | **Yes** | Height in centimeters |
| `--dose`, `-d` | float | No | Drug dose per m² in mg |
| `--format`, `-f` | string | No | Output format (text, json) |
| `--output`, `-o` | string | No | Output file path |

---

## Output Requirements

Every final response must make these explicit:

- Objective or requested deliverable
- Inputs used (weight, height, age, sex) and assumptions introduced
- Formula(s) selected and rationale
- Core result: BMI value + category, BSA value + formula used, dose if applicable
- Constraints and risks (BMI is screening only; not diagnostic)
- Unresolved items and next-step checks

---

## Error Handling

- If `--weight` or `--height` is missing, state the missing parameter and request it.
- If values are outside valid ranges (weight <2 or >300 kg; height <50 or >250 cm), flag as implausible and request correction.
- If `scripts/main.py` fails, report the failure point and provide manual calculation fallback.
- Do not fabricate results or clinical interpretations.

---

## Common Pitfalls

- **Unit confusion**: Always verify kg vs lbs, cm vs inches
- **Wrong formula**: Use Haycock for children < 12 years
- **BMI over-interpretation**: BMI is a screening tool; clinical correlation required
- **Athletes misclassified**: Consider waist circumference or body fat %
- **BSA rounding**: Use precise values for chemotherapy dosing

---

## Limitations

- BMI does not distinguish fat from muscle; varies by ethnicity
- All BSA formulas are approximations (10–15% variation normal)
- Not for diagnosis — BMI/BSA are tools, not clinical diagnoses
- Standard formulas inaccurate for amputees; special considerations for pregnancy

> ⚕️ **Clinical Note**: BMI and BSA are screening and calculation tools, not substitutes for clinical judgment. Always correlate with physical examination and patient history. Double-check all chemotherapy calculations independently.

---

## References

- `references/bsa_formulas_comparison.md` — Formula accuracy by population
- `references/pediatric_norms.md` — Growth charts and percentiles
- `references/chemotherapy_dosing.md` — BSA-based drug calculations
- `references/ethnic_adjustments.md` — Population-specific cutoffs
