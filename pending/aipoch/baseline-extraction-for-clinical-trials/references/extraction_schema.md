# Baseline Information Extraction Schema

Extract the following 10 fields from the clinical trial article. If a field is not found, leave it null or empty string.

## Fields

1.  **study**
    *   Description: First Author's Name and Publication Year.
    *   Example: "He, 2024"

2.  **region**
    *   Description: The region where the study was conducted.
    *   Example: "China"

3.  **number_of_participants**
    *   Description: Total number of participants.

4.  **sex**
    *   Description: Sex distribution of participants.

5.  **age**
    *   Description: Average age and variation (e.g., mean ± SD).

6.  **population**
    *   Description: Specific population or sample characteristics (e.g., disease type).
    *   Example: "NSCLC patients harboring EGFR mutations"

7.  **intervention_or_exposure**
    *   Description: Specific intervention tested or exposure factor.

8.  **comparator_or_context**
    *   Description: Control group or background context used for comparison.

9.  **outcome**
    *   Description: Primary and secondary outcome measures.

10. **study_design**
    *   Description: Type of study design.
    *   Example: "RCT", "Cohort study"

## Output Format

The output must be a valid JSON object matching these fields.
