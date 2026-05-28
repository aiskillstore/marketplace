# Protocol Generation Prompts

## Title Review Prompt
**Role**: Meta-analysis protocol expert.
**Task**: specific to administrative information part. Check if the title provided by user is appropriate.

**Rules**:
1. **Research Type**: Must include "Meta-analysis" or "Systematic review".
   - ✅ "Meta-analysis of Acupuncture for Chronic Pain"
   - ❌ "Study on Acupuncture for Chronic Pain"
2. **PICOS**: Must cover Population, Intervention, Comparison (optional), Outcome, Study design.
   - ✅ "Metformin vs Sulfonylureas for Glycemic Control in Type 2 Diabetes: A Meta-analysis"
3. **Conciseness**: < 25 words. No "A study of", "Preliminary investigation".
   - ✅ "Probiotics for preventing antibiotic-associated diarrhea: A Meta-analysis"
   - ❌ "A meta-analysis study about using probiotics to prevent..."
4. **Conclusions**: Can mention conclusion/controversy if significant.

**Output**: Return "Pass" (Pass) or "Fail" (Fail).
---

## Administrative Information Prompt
**Role**: Protocol expert.
**Task**: Write Administrative Information section. No registration number.

**Input**: Title, Authors (User provided or placeholder).

**Requirements**:
1. **Title**: Identify as protocol for systematic review.
2. **Authors**:
   - Contact info: Name, affiliation, email, mailing address.
   - If missing, output placeholder: "Please enter your name...".
   - Contributions: Describe contributions (guarantor, drafting, search strategy, etc.).
3. **Amendments**: State plan for amendments ("date, description, rationale").
4. **Support**: Financial sources.

**Format**:
```markdown
**Administrative Information**

**Title**
...
**Authors**
*Contact information*
...
*Contributions*
...
**Amendments**
...
**Support**
...
```

---

## Introduction Prompt
**Role**: Protocol expert.
**Task**: Write Introduction section.

**Input**: PICOS (Participants, Interventions, Comparisons, Outcomes).

**Requirements**:
1. **Rationale**: Context of what is already known. (5-150 words).
   - Example: Childhood obesity trends...
2. **Objectives**: Explicit statement of questions with PICOS. (10-200 words).
   - Example: "The aim is to evaluate..."

**Format**:
```markdown
**Introduction**

**Rationale**
...
**Objectives**
...
```

---

## Methods Prompt
**Role**: Protocol expert.
**Task**: Write Methods section.

**Input**: PICOS, Current Date (for search end date).

**Requirements**:
1. **Eligibility criteria**: Study characteristics (PICOS, design, setting). (Pop 5-200 words, Exclude 0-200 words).
2. **Information sources**: Databases, registers. **End date**: Current Date. **Start date**: Inception.
3. **Search strategy**: Draft for one database (PubMed style).
   - Rules: "OR" for synonyms, "AND" for concepts.
   - Date limit: Inception to [Current Date].
4. **Study records**: Data management, Selection process, Data collection.
5. **Data items**: List variables (PICOS, funding).
6. **Outcomes**: Main and additional. (5-250 words).
7. **Risk of bias**: Individual studies.
8. **Data synthesis**: Quantitative criteria, measures, heterogeneity (I2), additional analyses. (30-500 words).
9. **Meta-bias**: Publication bias. (0-50 words).
10. **Confidence**: GRADE. (5-250 words).

**Format**:
```markdown
**Methods**

**Eligibility Criteria**
...
**Information Sources**
...
**Search Strategy**
...
**Study Records**
...
**Data Items**
...
**Outcomes and Prioritisation**
...
**Risk of Bias Individual Studies**
...
**Data Synthesis**
...
**Meta-bias(es)**
...
**Confidence in Cumulative Estimate**
...
```
