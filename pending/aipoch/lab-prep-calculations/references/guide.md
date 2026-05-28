# Calculation Guide and Checklist

## Input Information

- Target concentration and target volume.
- Solute information: Name, molecular weight, or known concentration.
- Stock solution information: Concentration, solvent, purity/content.
- Solvent/buffer type and final system requirements.
- Constraints: Solubility, minimum weighing amount, equipment range.

## Common Formulas

- Dilution: C1V1 = C2V2
- Preparation from solid: m = C * V * MW
- Purity correction: m_adj = m / purity
- Stock solution preparation: m_stock = C_stock * V_stock * MW
- Dilution factor: DF = C1 / C2
- v/v: Vsolute = (percent / 100) * Vtotal
- w/v: msolute = (percent / 100) * Vtotal

## Unit Conversion

- 1 L = 1000 mL = 1,000,000 uL
- 1 M = 1 mol/L
- 1 mM = 1e-3 M
- 1 uM = 1e-6 M
- 1 g = 1000 mg
- 1 mg/mL = 1 g/L

## Checklist

- V1 <= V2, and the volume of added liquid is positive.
- Mass exceeds the minimum weighing amount; suggest preparing a stock solution if necessary.
- Solubility meets the target concentration; provide prompts for heating or changing solvents if necessary.
- Volume matches equipment range; avoid out-of-range operations.
- Output clear final volume and volume adjustment steps.
- If using stock solution dilution, provide the mass required for stock solution preparation.

## Output Format Suggestions

1. Parameter Summary (Table or List)
2. Calculation Process (Formulas and Values)
3. Operating Steps (Numbered Steps)
4. Equipment and Materials List
5. Risks and Precautions