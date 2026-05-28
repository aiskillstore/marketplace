# Risk of Bias Scale Selection Rules

Select the appropriate scale based on the study design:

| Study Design | Scale |
| :--- | :--- |
| **Case-control studies** | NOS (Newcastle-Ottawa Scale) Case-Control |
| **Cohort studies** | NOS (Newcastle-Ottawa Scale) Cohort |
| **Randomized controlled trials (RCT)** | RoB 2 (Cochrane Risk of Bias tool for randomized trials) |
| **Non-randomised studies of exposure** | ROBINS-E |
| **Non-randomised studies of interventions** | ROBINS-I |
| **Cross-sectional studies** | AHRQ or JBI (Check specific context if not specified) |
| **Diagnostic accuracy studies** | QUADAS-2 |

## Output Format
Always return the result in JSON format:

```json
{
  "study_design": "Detected Design",
  "scale": "Selected Scale Name"
}
```
