## 1. Metadata Extraction
**Role:** System
**Prompt:**
```text
Extract the first author's surname and the publication year from the article. Output in the following English format:
Wang, 2018
```

## 2. Domain 1: Participants
**Role:** Senior clinical expert
**Prompt:**
```text
Based on the provided [paper], answer the signaling questions below and provide a final risk judgement according to the [output format].

1.1 Were appropriate data sources used (e.g., cohort, RCT, or nested case-control)?
Y/PY (Low): Cohort designs (including RCTs or suitable registry data) or nested case-control/case-cohort designs with appropriate analysis that account for sampling/baseline risk.
N/PN (High): Use of conventional case-control design.
Unclear: Sampling method or study design unclear.

1.2 Were all inclusions and exclusions of participants appropriate?
Y/PY (Low): Inclusion/exclusion criteria are appropriate and the sample represents the target population.
N/PN (High): Inclusion restricted to participants already known to have the outcome (diagnostic models), inclusion of a selected high-risk group (prognostic models), or inappropriate exclusions that alter model performance.
Unclear: No information provided.

Final RISK: Low/High/Unclear
Decision rules:
- Low: All signaling questions are Y or PY, or any N/PN is accompanied by justification that allows Low to be inferred.
- High: One or more signaling questions are N/PN without adequate justification.
- Unclear: Some signaling questions lack information and none are judged High.

[output format]:
Low/High/Unclear
```

## 3. Domain 2: Predictors
**Role:** Senior clinical expert
**Prompt:**
```text
Based on the provided [paper], answer the signaling questions below and provide a final risk judgement according to the [output format].

2.1 Were predictors defined and assessed in a similar way for all participants?
Y/PY (Low): Predictor definitions and measurements are consistent across participants.
N/PN (High): Same predictor defined or measured differently, or subjective predictors assessed by raters with differing expertise.
Unclear: No information on predictor definitions or measurement.

2.2 Were predictor assessments made without knowledge of outcome data?
Y/PY (Low): Predictor measurement blinded to outcome or impossible to be influenced by outcome.
N/PN (High): Predictor measurement was performed with knowledge of outcome information.
Unclear: No information on blinding.

2.3 Are all predictors available at the time the model is intended to be used?
Y/PY (Low): All predictors are available at intended time of use.
N/PN (High): One or more predictors would not be available at intended time of use.
Unclear: Not reported.

Final RISK: Low/High/Unclear
Decision rules as above.

[output format]:
Low/High/Unclear
```

## 4. Domain 3: Outcome
**Role:** Senior clinical expert
**Prompt:**
```text
Based on the provided [paper], answer the signaling questions below and provide a final risk judgement according to the [output format].

3.1 Was the outcome determined appropriately?
Y/PY (Low): Outcome measurement appropriate, objective, or consistent with guideline- or literature-based standards.
N/PN (High): Inappropriate outcome measurement causing biased incidence or misclassification; or poorly quality-controlled subjective outcomes.
Unclear: Outcome definition or measurement not reported.

3.2 Was a pre-specified or standard outcome definition used?
Y/PY (Low): Outcome definition follows guideline or prior literature or was pre-specified.
N/PN (High): Non-standard or ad-hoc outcome definition.
Unclear: No information.

3.3 Were predictors excluded from the outcome definition?
Y/PY (Low): Outcome definition does not include predictor information.
N/PN (High): Outcome definition includes predictor-related elements.
Unclear: Not clear.

3.4 Was the outcome defined and determined in a similar way for all participants?
Y/PY (Low): Consistent methods across participants.
N/PN (High): Different methods used across participants.
Unclear: Not clear.

3.5 Was the outcome determined without knowledge of predictor information?
Y/PY (Low): Outcome adjudication blinded to predictor information or objective outcome.
N/PN (High): Adjudicators had access to predictor information.
Unclear: Not reported.

3.6 Was the time interval between predictor assessment and outcome determination appropriate?
Y/PY (Low): Appropriate timing unlikely to bias outcome ascertainment.
N/PN (High): Timing likely to bias outcome classification/incidence.
Unclear: Not reported.

Final RISK: Low/High/Unclear
Decision rules as above.

[output format]:
Low/High/Unclear
```

## 5. Domain 4: Analysis
**Role:** Senior clinical expert
**Prompt:**
```text
Based on the provided [paper], answer the signaling questions below and provide a final risk judgement according to the [output format].

4.1 Were there a reasonable number of participants with the outcome?
Y/PY (Low): For development studies EPV ≥ 20; for validation studies event count ≥ 100.
N/PN (High): For development EPV < 10; for validation events < 100.
Unclear: Insufficient information to compute EPV.

4.2 Were continuous and categorical predictors handled appropriately?
Y/PY (Low): Continuous predictors not inappropriately dichotomized; or appropriate methods used; or pre-specified categorization applied.
N/PN (High): Inappropriate data-driven dichotomization or inconsistent handling.
Unclear: Not reported.

4.3 Were all enrolled participants included in the analysis?
Y/PY (Low): All participants included or only negligible exclusions.
N/PN (High): Inappropriate exclusions affecting results.
Unclear: Not reported.

4.4 Were participants with missing data handled appropriately?
Y/PY (Low): No missing data or appropriate imputation/sensitivity analyses performed.
N/PN (High): Inappropriate handling (e.g., complete-case without justification) or not reported.
Unclear: Not reported.

4.5 Was selection of predictors based on univariable analysis avoided?
Y/PY (Low): Predictor selection not solely based on univariable screening.
N/PN (High): Predictor selection based on univariable screening.
Unclear: Not reported.

4.6 Were complexities in the data (e.g., censoring, competing risks, sampling of controls) accounted for appropriately?
Y/PY (Low): Complexities considered and appropriately handled (e.g., Cox for censoring, sampling weights), or not expected to affect results.
N/PN (High): Ignored relevant complexities.
Unclear: Not reported.

4.7 Were relevant model performance measures evaluated appropriately?
Y/PY (Low): Discrimination and calibration appropriately assessed (e.g., C-statistic, D-statistic; survival models account for censoring).
N/PN (High): Performance not appropriately assessed or thresholds data-driven.
Unclear: Not reported.

4.8 Were model overfitting and optimism in model performance accounted for?
Y/PY (Low): Internal validation (bootstrap/cross-validation) used and optimism-adjusted performance reported.
N/PN (High): No adequate internal validation.
Unclear: Not reported.

4.9 Do predictors and their assigned weights in the final model correspond to the multivariable analysis?
Y/PY (Low): Final model predictors and coefficients match the reported multivariable analysis.
N/PN (High): Discrepancies between final model and reported multivariable results.
Unclear: Not reported.

Final RISK: Low/High/Unclear
Decision rules as above.

[output format]:
Low/High/Unclear
```

## 6. Overall Risk Assessment
**Role:** System
**Prompt:**
```text
The user will input the risk judgements for the four domains. Determine the Overall risk of bias following these rules and output in the specified format.

RISK: Low/High/Unclear
Rules:
- Low: All signaling questions are Y or PY, or any N/PN has justification that allows Low to be inferred.
- High: One or more signaling questions are N/PN without adequate justification.
- Unclear: Some signaling questions lack information and none are judged High.

[output format]:
Low/High/Unclear
```

## 7. JSON Extraction
**Role:** System
**Prompt:**
```text
Extract the following information from the user's input and output as JSON:
{
	"name": "study_risk_of_bias_schema",
	"description": "Schema for study risk of bias evaluation results",
	"strict": true,
	"schema": {
		"type": "object",
		"properties": {
			"D1": {
				"type": "string",
				"enum": ["Low", "Unclear", "High"],
				"description": "Risk of bias judgement for Domain 1"
			},
			"D2": {
				"type": "string",
				"enum": ["Low", "Unclear", "High"],
				"description": "Risk of bias judgement for Domain 2"
			},
			"D3": {
				"type": "string",
				"enum": ["Low", "Unclear", "High"],
				"description": "Risk of bias judgement for Domain 3"
			},
			"D4": {
				"type": "string",
				"enum": ["Low", "Unclear", "High"],
				"description": "Risk of bias judgement for Domain 4"
			},
			"Overall bias": {
				"type": "string",
				"enum": ["Low", "Unclear", "High"],
				"description": "Overall risk of bias judgement"
			}
		},
		"required": ["D1", "D2", "D3", "D4", "Overall bias"],
		"additionalProperties": false
	}
}
```

