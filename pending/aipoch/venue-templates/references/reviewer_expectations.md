# Reviewer Expectations Across Conferences/Journals

Understanding what reviewers focus on across different publication venues is crucial for writing successful submissions. This guide covers evaluation criteria, common reasons for rejection, and how to address reviewer concerns.

**Last Updated**: 2024

---

## Overview

Reviewer priorities vary across different venues. Understanding these priorities helps you:
1. Appropriately define your contribution
2. Anticipate potential criticisms
3. Prepare effective rebuttals
4. Decide where to submit

---

## High-Impact Journals (Nature, Science, Cell)

### Reviewer Focus

| Priority | Weight | Description |
|----------|--------|-------------|
| **Broad Significance** | Crucial | Impact beyond a specific subfield |
| **Novelty** | Crucial | First demonstration or major advance |
| **Technical Rigor** | High | Robust methodology, appropriate controls |
| **Clarity** | High | Accessible to non-specialists |
| **Completeness** | Medium | Thorough but not exhaustive |

### Review Process

1. **Editorial Triage**: Most papers are rejected without review (Nature: ~92%)
2. **Expert Review**: If passed triage, reviewed by 2-4 reviewers
3. **Interdisciplinary Reviewers**: Often includes non-specialists
4. **Rapid Turnaround**: First decision typically within 2-4 weeks

### Reasons for Rejection

**At the Editorial Stage**:
- Findings are not significant enough for a broad audience
- Incremental progress compared to previous work
- Too specialized for the journal
- Subject matter does not align with current editorial interests

**At the Review Stage**:
- Conclusions lack data support
- Missing key controls
- Alternative explanations not addressed
- Statistical issues
- Insufficient acknowledgment of prior work
- Writing is inaccessible to non-specialists

### How to Address Nature/Science Reviewers

**In the Paper**:
- Highlight significance in the very first paragraph
- Explain why the findings have broad implications
- Provide controls for all major conclusions
- Use clear, plain language
- Include conceptual diagrams

**In the Rebuttal**:
- Address every single point (even minor ones)
- Provide new data as requested
- Acknowledge valid criticisms gracefully
- If significance is questioned, further explain the impact

### Reviewer Concerns and Sample Responses

**Reviewer**: "The significance of this work for the general reader is not yet clear."

**Response**: "We have revised the introduction to clarify the broader significance. As now stated in paragraph 1, our findings have implications for [X] because [Y]. We have also added a discussion of how these results inform understanding of [Z] (p. 8, lines 15-28)."

---

## Medical Journals (NEJM, Lancet, JAMA)

### Reviewer Focus

| Priority | Weight | Description |
|----------|--------|-------------|
| **Clinical Relevance** | Crucial | Will this change clinical practice? |
| **Methodological Rigor** | Crucial | Adherence to CONSORT/STROBE guidelines |
| **Patient Outcomes** | Crucial | Focus on what matters to patients |
| **Statistical Validity** | High | Appropriate analysis, sample size power |
| **Generalizability** | High | Applicability to broader populations |

### Review Process

1. **Statistical Review**: Often involves dedicated statistical reviewers
2. **Clinical Expertise**: Sub-specialty experts
3. **Methodological Review**: Focus on study design
4. **Multiple Rounds**: Revisions are typically required

### Reasons for Rejection

**Major Issues**:
- Underpowered study (sample size too small)
- Inappropriate controls/comparators
- Failure to address confounding factors
- Selective reporting of outcomes
- Missing safety data
- Conclusions exceeding the evidence

**Moderate Issues**:
- Unclear generalizability
- Missing subgroup analyses
- Incomplete CONSORT/STROBE reporting
- Inadequate description of statistical methods

### Reviewer Concerns and Sample Responses

**Reviewer**: "The study appears underpowered for the primary outcome. With 200 participants and a 5% event rate, it is insufficient to detect a clinically meaningful difference."

**Response**: "We appreciate this concern. Our power calculation (Methods, p. 5) was based on a 5% event rate in the control arm and a 50% relative reduction (to 2.5%). While the observed event rate (4.8%) was close to projected, we acknowledge the confidence interval is wide (HR 0.65, 95% CI 0.38-1.12). We have added this as a limitation (Discussion, p. 12). Importantly, the direction and magnitude of effect are consistent with the larger XYZ trial (n=5000), suggesting our findings merit confirmation in a larger study."

---

## Cell Press Journals

### Reviewer Focus

| Priority | Weight | Description |
|----------|--------|-------------|
| **Mechanistic Insight** | Crucial | How does it work? |
| **Depth of Study** | Crucial | Multiple approaches, comprehensive and detailed |
| **Biological Significance** | High | Importance to the field |
| **Technical Rigor** | High | Quantitative, statistical, reproducible |
| **Novelty** | Medium to High | New discovery, not just validation |

### Review Process

1. **Extended Review**: Typically 3+ reviewers
2. **Revision Cycles**: Multiple rounds of revision are common
3. **Comprehensive Revisions**: Major new experiments are often requested
4. **Detailed Evaluation**: Figure-by-figure assessment

### Reviewer Expectations

- **Multiple Complementary Methods**: Showing the same finding in different ways
- **In Vivo Validation**: For cell biology conclusions
- **Rescue Experiments**: For knockdown/knockout studies
- **Quantitative Analysis**: Not just representative images
- **Complete Figure Panels**: Including all conditions and controls

### Reviewer Concerns and Sample Responses

**Reviewer**: "The authors show that protein X is required for process Y using siRNA knockdown. However, only one RNAi reagent was used, and off-target effects cannot be ruled out. Additional evidence is needed."

**Response**: "We agree that additional validation is important. In the revised manuscript, we now show: (1) two independent siRNAs against protein X produce identical phenotypes (new Fig. S3A-B); (2) CRISPR-Cas9 knockout cells recapitulate the phenotype (new Fig. 2D-E); and (3) expression of siRNA-resistant protein X rescues the phenotype (new Fig. 2F-G). These complementary approaches strongly support the conclusion that protein X is required for process Y."

---

## Machine Learning Conferences (NeurIPS, ICML, ICLR)

### Reviewer Focus

| Priority | Weight | Description |
|----------|--------|-------------|
| **Novelty** | Crucial | New methods, insights, or perspectives |
| **Technical Soundness** | Crucial | Correct implementation, fair comparisons |
| **Significance** | High | Advancing the field |
| **Experimental Rigor** | High | Strong baselines, appropriate ablation studies |
| **Reproducibility** | Medium to High | Can others replicate it? |
| **Clarity** | Medium | Concise writing, well-organized |

### Review Process

1. **Area Chair (AC) Assignment**: Grouped by topic
2. **3-4 Reviewers**: Expertise in the specific area
3. **Author Rebuttal**: Opportunity to respond
4. **Reviewer Discussion**: Following the rebuttal
5. **AC Recommendation**: Synthesis of reviews

### Scoring Dimensions

Typical NeurIPS/ICML scoring:

| Dimension | Score Range | Evaluation Content |
|-----------|-------------|------------------|
| **Soundness** | 1-4 | Technical correctness |
| **Contribution** | 1-4 | Importance of results |
| **Presentation** | 1-4 | Clarity and organization |
| **Overall** | 1-10 | Overall assessment |
| **Confidence** | 1-5 | Reviewer's level of expertise |

### Reasons for Rejection

**Critical Issues**:
- Weak baselines or unfair comparisons
- Missing ablation studies
- Results not significantly better than State-of-the-Art (SOTA)
- Technical errors in methodology or analysis
- Overclaiming without evidence

**Moderate Issues**:
- Limited novelty compared to prior work
- Narrow evaluation (too few datasets/tasks)
- Missing reproduction details
- Poor presentation
- Limited analysis or insight

### ML Reviewer Red Flags

❌ "We compare against a 2018 method" (Outdated baselines)
❌ "Our method achieves a 0.5% improvement" (Marginal gains)
❌ "We evaluate on one dataset" (Limited generalization)
❌ "Implementation details are in the supplement" (Core info missing)
❌ "We leave ablation experiments for future work" (Incomplete evaluation)

### Reviewer Concerns and Sample Responses

**Reviewer**: "The proposed method is only compared to Transformer and Performer. Recent work such as FlashAttention and Longformer should be included."

**Response**: "Thank you for this suggestion. We have added comparisons to FlashAttention (Dao et al., 2022), Longformer (Beltagy et al., 2020), and BigBird (Zaheer et al., 2020). As shown in new Table 2, our method outperforms all baselines: FlashAttention (3.2% worse), Longformer (5.1% worse), and BigBird (4.8% worse). We also include a new analysis (Section 4.3) explaining why our approach is particularly effective for sequences > 16K tokens."

---

## Human-Computer Interaction Conferences (CHI, CSCW)

### Reviewer Focus

| Priority | Weight | Description |
|----------|--------|-------------|
| **Contribution to HCI** | Crucial | New designs, insights, or methods |
| **User-Centered** | High | Focus on human needs |
| **Appropriate Evaluation** | High | Matches claims and contributions |
| **Design Rationale** | Medium to High | Justified design decisions |
| **Implications** | Medium | Guidance for future work |

### Contribution Types

CHI explicitly categorizes contribution types:

| Type | Reviewer Expectations |
|------|----------------------|
| **Empirical** | Rigorous user studies, clear findings |
| **Artifact/System** | Novel system/tool, evaluation of use |
| **Methodological** | New research methods, validation process |
| **Theoretical** | Conceptual frameworks, intellectual contribution |
| **Survey** | Comprehensive, well-organized coverage |

### Reasons for Rejection

**Critical Issues**:
- Claims do not match the evaluation
- Insufficient number of participants to draw conclusions
- Missing ethical considerations (no IRB approval)
- Focus on technology without human insight
- Limited contribution to the HCI community

**Moderate Issues**:
- Weak design rationale
- Limited generalizability
- Missing relevant HCI-related work
- Unclear implications for practitioners

### Reviewer Concerns and Sample Responses

**Reviewer**: "The evaluation consists only of a short-term lab study with 12 participants. It is unclear how the system would perform in long-term, real-world use."

**Response**: "We acknowledge this limitation, which we now discuss explicitly (Section 7.2). We have added a 2-week deployment study with 8 participants from our original cohort (new Section 6.3). This longitudinal data shows sustained engagement (mean usage: 4.2 times/day) and reveals additional insights about how use patterns evolve over time. However, we agree that larger and longer deployments would strengthen ecological validity."

---

## Natural Language Processing Conferences (ACL, EMNLP)

### Reviewer Focus

| Priority | Weight | Description |
|----------|--------|-------------|
| **Task Performance** | High | SOTA or competitive results |
| **Analysis Quality** | High | Error analysis, deep insights |
| **Methodology** | High | Sound methods, fair comparisons |
| **Reproducibility** | High | Full details provided |
| **Novelty** | Medium to High | New methods or insights |

### ACL Rolling Review (ARR)

Since 2022, ACL conferences have used a shared review system:
- Reviews can be transferred between different conferences
- Action Editors manage the papers
- Commitments are made to specific conferences after review

### Responsible NLP Checklist

Reviewers check for:
- Limitations section (mandatory)
- Risks and ethical considerations
- Computational resources/carbon footprint
- Bias analysis (where applicable)
- Data documentation

### Reviewer Concerns and Sample Responses

**Reviewer**: "The paper lacks an analysis of failure cases. When and why does the proposed method fail?"

**Response**: "We have added Section 5.4 on error analysis. We manually examined 100 errors and categorized them into three types: (1) complex coreference chains (42%), (2) implicit references (31%), and (3) domain-specific knowledge requirements (27%). Figure 4 shows representative examples of each. This analysis reveals that our method particularly struggles with implicit references, which we discuss as a direction for future work."

---

## Data Mining (KDD, WWW)

### Reviewer Focus

| Priority | Weight | Description |
|----------|--------|-------------|
| **Scalability** | High | Ability to handle large datasets |
| **Real-world Impact** | High | Applicability in real-world scenarios |
| **Experimental Rigor** | High | Comprehensive evaluation |
| **Technical Novelty** | Medium to High | New methods or applications |
| **Reproducibility** | Medium | Code/data availability |

### What Impresses KDD Reviewers

- Large-scale experiments (millions of samples)
- Industrial deployment or A/B testing
- Efficiency comparisons (runtime, memory)
- Real-world datasets beyond standard benchmarks
- Complexity analysis (time and space)

### Reviewer Concerns and Sample Responses

**Reviewer**: "Experiments are limited to small datasets (< 100K samples). How does the method scale to industry-scale data?"

**Response**: "We have added experiments on two large-scale datasets: (1) ogbn-papers100M (111M nodes, 1.6B edges) and (2) a proprietary e-commerce graph (500M nodes, 4B edges) provided by [company]. Table 4 (new) shows our method scales near-linearly with data size, completing in 42 minutes on ogbn-papers where baselines run out of memory. Section 5.5 (new) provides detailed scalability analysis."

---

## General Rebuttal Strategy

### Do's

✅ **Respond to every point**: Even minor issues
✅ **Provide evidence**: New experiments, data, or citations
✅ **Be specific**: Point to specific sections, line numbers, figures
✅ **Acknowledge valid criticism**: Show that you understand the reviewer's concern
✅ **Be concise**: Reviewers have many rebuttals to read
✅ **Stay professional**: Even in the face of unfair reviews
✅ **Prioritize key issues**: Address major concerns first

### Don'ts

❌ **Be overly defensive**: Accept reasonable criticism
❌ **Argue without evidence**: Support arguments with facts
❌ **Ignore points**: Even if you disagree with them
❌ **Be vague**: State exactly what changes were made
❌ **Attack the reviewer**: Maintain professionalism
❌ **Only promise future work**: If possible, do it now

### Rebuttal Template

```
We thank the reviewers for their constructive feedback. We address 
the main concerns below:

**R1/R2 Concern: [Common concern from multiple reviewers]**

[Your response, including specific actions taken and citations to locations in the revised paper]

**R1-1: [Specific point]**

[Response with evidence]

**R2-3: [Specific point]**

[Response with evidence]

We have also made the following additional improvements:
• [Improvement 1]
• [Improvement 2]
```

---

## Pre-submission Self-Check

Before submitting, look at your paper like a reviewer:

### All Venues
- [ ] Are conclusions supported by evidence?
- [ ] Are baselines appropriate and up-to-date?
- [ ] Is the contribution clearly stated?
- [ ] Are limitations acknowledged?
- [ ] Is reproduction information complete?

### High-Impact Journals
- [ ] Is the significance clear to a non-specialist?
- [ ] Are figures intuitive and clear?
- [ ] Are controls sufficient for the conclusions?

### Medical Journals
- [ ] Does it fully comply with CONSORT/STROBE?
- [ ] Are absolute values reported?
- [ ] Is clinical relevance clear?

### ML Conferences
- [ ] Are ablation studies comprehensive?
- [ ] Is the comparison fair?
- [ ] Is reproduction information complete?

### HCI Conferences
- [ ] Is the user-centered perspective clear?
- [ ] Does the evaluation match the claims?
- [ ] Are design implications actionable?

---

## See Also

- `venue_writing_styles.md` - Writing styles for various venues
- `nature_science_style.md` - Detailed guide for Nature/Science
- `ml_conference_style.md` - Detailed guide for ML conferences
- `medical_journal_styles.md` - Detailed guide for medical journals