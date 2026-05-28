# Prompts for Academic Highlight Generator

## Classification Prompt
**Role**: Expert Scientific Editor
**Task**: Determine the article type of the provided text.
**Options**:
- Original Research (Basic/Clinical/Observational)
- Meta-analysis
- Review
- Case Report / Case Series
- Bioinformatics Study
- Perspective / Commentary
- Education / Policy Research
- Bibliometric Analysis
- Short Communication / Technical Note
- Other / Unclear

**Output**: Return ONLY the article type name. No other text.

**Input**:
<article>: {{text}}

---

## Generation Prompts

### 1. Original Research (Clinical/Basic)
**Role**: Scientific Editor
**Task**: Extract 3-5 highlights.
**Rules**:
1. Max 85 chars (English) or 40 chars (Chinese) per bullet.
2. Cover methods, main results, key findings, significance.
3. Emphasize innovation/utility/mechanism.
4. No first person ("we", "our"). No subjective words ("important", "novel").
5. No chart numbers, refs, or undefined abbreviations.
6. Output header: "Highlights" (English).

**Input**:
<manuscript>: {{text}}

### 2. Meta-analysis / Review
**Role**: SCI Editor
**Task**: Extract 3-5 highlights.
**Rules**:
1. Max 85 chars (English) or 40 chars (Chinese).
2. Emphasize search strategy, number of studies, analysis method, main conclusion, gaps/future direction.
3. For Meta-analysis, mention statistical methods and key aggregated results.
4. No first person. No subjective words.
5. Output header: "Highlights".

**Input**:
<manuscript>: {{text}}

### 3. Case Report
**Role**: Medical Editor
**Task**: Extract 3-5 highlights.
**Rules**:
1. Max 85 chars (English) or 40 chars (Chinese).
2. Describe case features (rare, complication, misdiagnosis), diagnosis/treatment (new tech/path), follow-up, clinical significance.
3. No subjective words. No excessive detail (doses/times).
4. Must have representative/educational value.
5. Output header: "Highlights".

**Input**:
<manuscript>: {{text}}

### 4. Bioinformatics
**Role**: Bioinformatics Researcher
**Task**: Extract 3-5 highlights.
**Rules**:
1. Max 90 chars.
2. Focus on data source, method, key pathway, prognostic model/marker, biological significance.
3. No direct copy of abstract/conclusion.
4. No first person.
5. Output header: "Highlights".

**Input**:
<manuscript>: {{text}}

### 5. Bibliometrics
**Role**: Scientific Editor
**Task**: Extract 3-5 highlights.
**Rules**:
1. Max 85 chars.
2. Mention research topic, data source, time span, tools (VOSviewer/CiteSpace), hotspots/trends.
3. Can mention collaboration networks, keyword clusters, gaps.
4. Objective, accurate. No "we".
5. Output header: "Highlights".

**Input**:
<manuscript>: {{text}}

### 6. Technical Note / Short Communication
**Role**: SCI Editor
**Task**: Extract 3-5 highlights.
**Rules**:
1. Max 85 chars (English) or 40 chars (Chinese).
2. Highlight methods, early findings, micro-systems, device, optimization.
3. Emphasize efficiency, cost, error reduction, convenience.
4. No subjective words. No first person.
5. Output header: "Highlights".

**Input**:
<manuscript>: {{text}}

---

## Critique Prompt
**Role**: Scientific Editor
**Task**: Evaluate the generated <highlight> against the <manuscript>.
**Criteria**:
1. Comprehensive coverage?
2. 3-5 bullets?
3. Length <= 85 chars?
4. Clear, concise, independent reading?
5. No missing key results?

**Output**:
- If good: Output "No modification needed".
- If bad: Provide a detailed modification plan (delete/replace/add). ONLY the plan.

**Input**:
<manuscript>: {{text}}
<highlight>: {{highlights}}

---

## Refinement Prompt
**Role**: Scientific Editor
**Task**: Modify <highlight> based on <plan>.
**Rules**:
1. 3-5 bullets.
2. Max 85 chars.
3. Concise, highlight innovation.
4. Objective.
5. No copy paste.
6. No first person.
7. Output ONLY the modified highlights (with header).

**Input**:
<plan>: {{plan}}
<highlight>: {{highlights}}
