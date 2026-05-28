# Prompts for Meta-Analysis Baseline Generator

## Text Description Generation

**Role**: Clinical Medical Expert
**Task**: Based on the provided meta-analysis [Baseline Information Table] and [Title], provide a detailed text description of the table information.

**Requirements**:
1. State the total number of studies included, the sample size for each group and the total sample size, and other relevant information.
2. Output ALL content in **{{language}}**.

**Example (English)**:
**Study characteristics**
Forty-one publications, published between 2002 and 2021, from a total of 1675 connected investigations that met the inclusion criteria were chosen for the study. The results of these researches are presented in Table X. A total of 10 204 females with CC were in the chosen investigations' starting point...

## Markdown Table Generation

**Role**: Clinical Medical Expert
**Task**: Convert the provided meta-analysis [Baseline Information Table] (JSON format) into a Markdown table.

**Requirements**:
1. Output MUST be in **{{language}}**.
2. Output ONLY the table content wrapped in curly braces (e.g., `{ | Col1 | Col2 | ... }`).
3. Do not include any other text outside the curly braces.

**Input**:
【Baseline Information Table】: {{baseline_information}}
