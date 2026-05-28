---
name: meta-manuscript-generator
description: Generates a first draft of a clinical meta-analysis paper. Input the research report (including Methods and Results sections), language, and title to automatically generate a complete paper draft including Abstract, Introduction, Discussion, and other sections, with automatic PubMed retrieval of relevant references. Suitable for assisting in the writing of systematic reviews and meta-analyses.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Meta-Analysis Manuscript Generator

Generates a first draft of a meta-analysis paper meeting SCI journal standards based on the user-provided research report, including reference support.

## When to Use

- Use this skill when you need generates a first draft of a clinical meta-analysis paper. input the research report (including methods and results sections), language, and title to automatically generate a complete paper draft including abstract, introduction, discussion, and other sections, with automatic pubmed retrieval of relevant references. suitable for assisting in the writing of systematic reviews and meta-analyses in a reproducible workflow.
- Use this skill when a academic writing task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/insert_references.py` is the most direct path to complete the request.
- Use this skill when you need the `meta-manuscript-generator` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Generates a first draft of a clinical meta-analysis paper. Input the research report (including Methods and Results sections), language, and title to automatically generate a complete paper draft including Abstract, Introduction, Discussion, and other sections, with automatic PubMed retrieval of relevant references. Suitable for assisting in the writing of systematic reviews and meta-analyses.
- Packaged executable path(s): `scripts/insert_references.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Academic Writing/meta-manuscript-generator"
python -m py_compile scripts/insert_references.py
python scripts/insert_references.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/insert_references.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/insert_references.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Input Requirements

The user needs to provide:
1. **Research Report**: Contains complete Methods and Results sections
   - Methods and Results will be inserted directly into the final paper
   - Should include detailed statistics (e.g., OR, HR, CI, p-values, etc.)
2. **Language**: Chinese or English
3. **Title**: Paper title

**Input Format Example**:
```
Methods and Results: (User's complete methods and results content...)
Language: (Chinese/English)
Title: (Paper title)
```

## Workflow

### Phase 1: Report Parsing

Extract and structure the following information from the research report:

**Methods Section Keywords** (for reference retrieval):
```
Study Population:
Exposure/Intervention:
Outcome Measures:
Research Direction:
Primary Research Methods:
```

**Key Points of the Results Section**(For discussion writing, extracted by module)：

1. Results Interpretation Module

Main findings and statistical data

Analysis of the relationship between exposure and outcomes

2. Literature Comparison Module

Findings that need to be compared with previous studies

Contextual and background significance

3. Clinical Implications Module

Results relevant to clinical significance

4. Study Limitations Module

Methodological limitations

### Stage 2: Reference Retrieval

Use scripts/search_references.py to retrieve PubMed references.

**API Description**：Use the official PubMed E-utilities API
- esearch: Retrieve PMID lists
- efetch: Retrieve detailed article information (XML format)
- Base URL: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`

**Search Workflow**：

1. **Keyword Extraction**：Extract 3–5 keywords from the topic and rank them by importance.
2. **Search Query Generation**：Generate English search queries for each keyword.
3. **PubMed esearch Call**：Retrieve a list of PMIDs that meet the criteria.
4. **PubMed efetch Call**：Retrieve article details (authors, title, journal, year, abstract).
5. **Number of Articles Returned**：
   - First keyword: 15 articles
   - Second keyword: 10 articles
   - Other keywords: 5 articles each
   - Limit to publications from the past 5 years (2020–2025)

**Search Allocation**：
- Introduction references: Search based on keywords from the Methods section
- Discussion – Results Interpretation: Search based on results interpretation points
- Discussion – Literature Comparison: Search based on literature comparison points
- Discussion – Study Limitations: Search based on keywords from the Methods section

**Usage Example**：
```python
from scripts.search_references import search_references_for_theme

# Retrieve references for the Introduction
intro_refs = search_references_for_theme("immune checkpoint inhibitors non-small cell lung cancer efficacy meta-analysis")

# Retrieve references for the Discussion
discussion_refs = search_references_for_theme( "PD-1 inhibitors lung cancer survival mechanism")
```

### Stage 3: Section Writing

Generate each section of the manuscript in the following order.
Detailed guidelines are available in [references/writing-guide.md](references/writing-guide.md)。

**Citation Format During Writing**：Use `[PMID: xxxxxxxx]` to mark references, which will be processed later

#### 3.1 Abstract
- Four structured paragraphs: Background, Methods, Results, Conclusions
- 200-300 words
- No references required

#### 3.2 Introduction
- Clinical background of the problem (with epidemiological data)
- Current research status and existing gaps
- Study objectives and significance
- 300–500 words
- No more than 10 references

#### 3.3 Discussion

Write in modular order with natural transitions between sections:

| Module | Content | Word Count |
| ------ | ------- | ---------- |
| Opening of Discussion | Summary of main findings and statistical significance | 150–200 |
| Results Interpretation | Mechanistic analysis and clinical relevance | ≥150 |
| Literature Comparison | Comparison with previous studies | ≥150 |
| Study Limitations | Methodological and clinical limitations | 100–150 |
| Closing of Discussion | Conclusions and future directions | 100–150 |

Each module should cite no more than 10 references.

### Stage 4: Reference Insertion

Use `scripts/insert_references.py` to process references.

**API Description**：Use the PubMed efetch API to retrieve formatted citations
- Parse XML responses to generate AMA-style references
- Include: authors, title, journal abbreviation, year, volume, issue, pages

**Processing Workflow**：

1. **Article Segmentation**：Split the manuscript into sections using markers such as `## Discussion` 

2. **PMID Extraction**: Use regular expressions to identify `[PMID: number]` or `【PMID: number】`

3. **PubMed efetch Call**：Retrieve full citation details for each PMID.

4. **AMA Citation Generation**：Format as:
Author(s). Title. Journal. Year;Volume(Issue):Pages.
5. **In-text Citation Replacement**：Replace `[PMID: xxx]` with `[[n]](link)` format
6. **Renumbering Numeric Citations**：Resolve conflicts with existing bracketed numeric citations.
7. **Reference List Generation**：Number references sequentially based on citation order.

**Usage Example**：
```python
from scripts.insert_references import insert_references

# Process the complete manuscript
final_article = insert_references(
    article=draft_with_pmid_markers,
    new_references=""  # Optional: additional references
)
```

### Stage 5: Final Integration and Output

Integrate the generated content with the user-provided Methods and Results sections into a complete manuscript.

**Integration Order**：
1. Title (user-provided)

2. Abstract (generated)

3. Introduction (generated)

4. Materials and Methods (extracted from user input, unchanged)

5. Results (extracted from user input, unchanged)

6. Discussion (generated)

7. Conclusion (generated)

8. References (generated)
 

**Final Output Format**：
```markdown

# [Article Title]

## Abstract
[Abstract content]

## Introduction
[Introduction content with hyperlinks]

## Materials and Methods
[User-provided Methods section, original text preserved]

## Results
[User-provided Results section, original text preserved]

## Discussion
[Discussion content, no subheadings, natural flow]

## Conclusion
[Conclusion]

## References
[1] Author et al. Title. Journal. Year;Vol(Issue):Pages. [https://pubmed.ncbi.nlm.nih.gov/PMID/]
[2] ...
```

**Note**：The user-provided Methods and Results sections should be preserved in their original wording, with only minimal formatting adjustments made where necessary.

## Writing Standards

1. **Language Style**：Academic, objective, and precise
2. **Abbreviation Rules**：Provide full term at first mention
3. **Citation Format**:
   - During drafting：`[PMID: 12345678]`
   - Final version：`[[1]](link)`
4. **Data Presentation**：Retain original statistical data, e.g.
HR = 1.25, 95% CI: 1.10–1.42, p < 0.001
5. **Avoid**：Subjective judgments, overinterpretation, and redundant statements

## Quality Checklist

Verify after generation：
- [ ] Word counts meet section requirements
- [ ] Statistical data are accurately reported
- [ ] PPMIDs are valid and links are accessible
- [ ] References are relevant to the content
- [ ] Logical flow without redundancy
- [ ] Reference list is complete
