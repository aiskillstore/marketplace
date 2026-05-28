# QUAPAS Evaluation Prompts

## Domain 1: Participants
**Role**: Top medical expert
**Task**: Based on the provided [Paper], answer questions and output results in the specified [Format].
**Explanation**:
Describe methods for recruiting participants
Describe participants (previous testing, presentation, intended use of index test, and setting)
**Questions**:
S1.1: Was a consecutive or random sample of participants enrolled?
S1.2: Was a case–control design avoided?
S1.3: Did the study avoid inappropriate selection criteria?
Concerns about applicability (high, low, unclear): Do participants match the review question?
**Output Format**:
S1.1:Yes/No/Unclear
S1.2:Yes/No/Unclear
S1.3:Yes/No/Unclear
Applicability：High/Low/Unclear

## Domain 2: Index Test
**Role**: Top medical expert
**Task**: Based on the provided [Paper], answer questions and output results in the specified [Format].
**Explanation**:
Describe the index test (definition, context of use, method of measurement, and interpretation)
**Questions**:
S2.1: Was the method used to perform the index test valid and reliable?
S2.2: Was the method for performing the index test the same for all participants?
S2.3: Were the index test results interpreted without knowledge of the outcome?
S2.4: If a threshold was used, was it prespecified?
**Output Format**:
S2.1:Yes/No/Unclear
S2.2:Yes/No/Unclear
S2.3:Yes/No/Unclear
S2.4:Yes/No/Unclear
Applicability：High/Low/Unclear

## Domain 3: Outcome
**Role**: Top medical expert
**Task**: Based on the provided [Paper], answer questions and output results in the specified [Format].
**Explanation**:
Describe the outcome (definition, method of measurement, and interpretation)
**Questions**:
S3.1: Was the method used to measure the outcome valid and reliable?
S3.2: Was the method for measuring the outcome the same for all participants?
S3.3: Was the outcome measured without knowledge of the index test results?
**Output Format**:
S3.1:Yes/No/Unclear
S3.2:Yes/No/Unclear
S3.3:Yes/No/Unclear
Applicability：High/Low/Unclear

## Domain 4: Flow and Timing
**Role**: Top medical expert
**Task**: Based on the provided [Paper], answer questions and output results in the specified [Format].
**Explanation**:
Describe any participants lost to follow-up or excluded from the analysis
Describe the time horizon from the index test to the outcome
**Questions**:
S4.1: Did all participants receive the index test?
S4.2: Was treatment avoided after the index test was performed?
S4.3: Was the time horizon sufficient to capture the outcome?
S4.4: Was information on the outcome available for all participants?
**Output Format**:
S4.1:Yes/No/Unclear
S4.2:Yes/No/Unclear
S4.3:Yes/No/Unclear
S4.4:Yes/No/Unclear
Applicability：High/Low/Unclear

## Domain 5: Analysis
**Role**: Top medical expert
**Task**: Based on the provided [Paper], answer questions and output results in the specified [Format].
**Explanation**:
Describe the statistical methods
**Questions**:
S5.1: Were all enrolled participants included in the analysis?
S5.2: If data were missing, were appropriate methods used?
S5.3: Were appropriate methods used to account for censoring?
S5.4: In case of competing events, were appropriate methods used to account for them?
**Output Format**:
S5.1:Yes/No/Unclear
S5.2:Yes/No/Unclear
S5.3:Yes/No/Unclear
S5.4:Yes/No/Unclear
Applicability：High/Low/Unclear

## ROB Assessment (Generic Rule)
**Role**: Clinical Meta-analysis Expert
**Task**: Evaluate bias based on signaling question answers.
**Rules**:
- All answers "Yes" -> "Low"
- No information -> "Unclear"
- Any answer "No" -> "High"
**Output Format**:
Risk of bias：Low /High /Unclear
Applicability：High/Low/Unclear (Output as is)

## Study Extraction
Extract the first author's name and year from the article.
Format: "Wang, 2018"

## Overall Judgment
**Rules**:
- All signaling questions "Yes" -> "Low" (implied, though prompt says "Yes" -> "Low" and output format is STRONG/MODERATE/WEAK. Wait, the prompt says "Yes" means "Low" bias, "No" means "High" bias. Output format is STRONG/MODERATE/WEAK.
    - Note: This seems contradictory in the original YAML prompt (`1753780598265`). It says "Yes" -> "Low", "No" -> "High", but output is "STRONG/MODERATE/WEAK".
    - Usually "Low Bias" = "High Quality" = "Strong"?
    - Let's stick to the prompt's explicit output format: "STRONG / MODERATE / WEAK".
    - I should probably interpret "Low Bias" -> "STRONG"?
- Actually, the prompt says: "The final result is obtained based on the results of each part... Output format: STRONG /MODERATE /WEAK".    - I will copy the prompt logic: "Yes" -> "Low" (bias), "No" -> "High" (bias).
    - But how to map Low/High Bias to Strong/Weak?
    - Standard QUADAS/QUAPAS: Low Bias = Good = Strong. High Bias = Bad = Weak.
    - I will instruct the Agent to infer this.

## JSON Schema
```json
{
  "name": "study_risk_of_bias_schema",
  "description": "Schema for study risk of bias evaluation results",
  "strict": true,
  "schema": {
    "type": "object",
    "properties": {
      "study": { "type": "string", "description": "Study reference, e.g., 'Wang,2018'" },
      "D1": { "type": "string", "enum": ["Low", "High", "Unclear"] },
      "D2": { "type": "string", "enum": ["Low", "High", "Unclear"] },
      "D3": { "type": "string", "enum": ["Low", "High", "Unclear"] },
      "D4": { "type": "string", "enum": ["Low", "High", "Unclear"] },
      "D5": { "type": "string", "enum": ["Low", "High", "Unclear"] },
      "overall": { "type": "string", "enum": ["Low", "High", "Unclear"] }
    },
    "required": ["study", "D1", "D2", "D3", "D4", "D5", "overall"],
    "additionalProperties": false
  }
}
```
**Note**: The JSON schema expects "Low/High/Unclear" for `overall`, but the Overall Judgment prompt asked for "STRONG/MODERATE/WEAK".
*Correction*: The JSON schema `1753780669720` has `overall` enum as `["Low", "High", "Unclear"]`.
So the "STRONG/MODERATE/WEAK" might be an intermediate step or a mismatch in the original YAML.
I will follow the JSON Schema as the final source of truth.
