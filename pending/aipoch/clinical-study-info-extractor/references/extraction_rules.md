# Extraction and Verification Rules

## Field Definitions

| Field | Description |
|-------|-------------|
| pmid | PubMed ID |
|title| Article Title (Chinese) |
|year of publication| Publication Year |
|Journal name| Journal Name (Original Language) |
|summary| Abstract (Chinese) |
| doi | DOI |
|Article type|Type: Research / meta-analysis / case report / review|
|study population| Patient/Subject characteristics (Chinese) |
|sample size|Total sample size (Number only). Empty if not "research type".|
|Interventions|Specific interventions per group. "None" if not mentioned. (Chinese)|
|Research results| Main findings/data (Chinese) |
|in conclusion| Conclusion/Author's view (Chinese) |

## Extraction Prompt (Phase 1)

**Role**: System
**Task**: Extract fields from [Clinical Study Literature] info.

**Key Constraints**:
1. **Article Type**: Strictly choose from: research / meta-analysis / case report / review. "Meta analysis" in title -> meta-analysis.2. **Sample Size**: Only for "research type". Only numbers. Leave empty otherwise.3. **Intervention**: One column, distinct groups. "None" if missing.4.  **Format**: Markdown table row, "|" separator. No header. One line only.
5. **Language**: Translate all to Chinese except Journal Name. Replace "English" with ",".## Verification Prompt (Phase 2)**Role**: System
**Task**: Check and correct the extraction based on the rules.

**Checklist**:
1.  Is Article Type correct?
2. Is Sample Size numeric and present ONLY for "research type"?3.  Are all fields (except Journal) in Chinese?
4.  Is the format a valid Markdown table row?

**Output**: Corrected content only. No explanations.
