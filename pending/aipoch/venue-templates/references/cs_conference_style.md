# Computer Science (CS) Conference Writing Style Guide

A comprehensive writing guide for ACL, EMNLP, NAACL (Natural Language Processing), CHI, CSCW (Human-Computer Interaction), SIGKDD, WWW, SIGIR (Data Mining/Information Retrieval), and other major CS conferences.

**Last Updated**: 2024

---

## Overview

CS conferences span multiple subfields with distinct writing cultures. This guide covers NLP, HCI, and Data Mining/Information Retrieval, each with unique expectations and evaluation criteria.

---

# Part 1: NLP Conferences (ACL, EMNLP, NAACL)

## NLP Writing Philosophy

> "Strong empirical results on standard benchmarks accompanied by insightful analysis."

NLP papers seek a balance between empirical rigor and linguistic insight. Human evaluation is becoming as important as automated metrics.

## Audience and Tone

### Target Readers
- NLP researchers and computational linguists
- Familiar with Transformer architectures and standard benchmarks
- Expect reproducible results and error analysis

### Tone Characteristics
| Feature | Description |
|---------------|-------------|
| **Task-Focused** | Clear problem definition |
| **Benchmark-Oriented** | Emphasis on standard datasets |
| **Analysis-Rich** | Includes error analysis and qualitative examples |
| **Reproducibility** | Full implementation details |

## Abstract (NLP Style)

### Structure
- **Task/Problem** (1 sentence)
- **Limitations of Prior Work** (1 sentence)
- **Your Approach** (1-2 sentences)
- **Results on Benchmarks** (2 sentences)
- **Analysis Findings** (Optional, 1 sentence)

### Abstract Example

```
Coreference resolution remains challenging for pronouns with distant or 
ambiguous antecedents. Prior neural approaches struggle with these 
difficult cases due to limited context modeling. We introduce 
LongContext-Coref, a retrieval-augmented coreference model that 
dynamically retrieves relevant context from document history. On the 
OntoNotes 5.0 benchmark, LongContext-Coref achieves 83.4 F1, improving 
over the previous state-of-the-art by 1.2 points. On the challenging 
WinoBias dataset, we reduce gender bias by 34% while maintaining 
accuracy. Qualitative analysis reveals that our model successfully 
resolves pronouns requiring world knowledge, a known weakness of 
prior approaches.
```

## NLP Paper Structure

```
├── Introduction
│   ├── Task motivation
│   ├── Prior work limitations
│   ├── Your contribution
│   └── Contribution bullets
├── Related Work
├── Method
│   ├── Problem formulation
│   ├── Model architecture
│   └── Training procedure
├── Experiments
│   ├── Datasets (with statistics)
│   ├── Baselines
│   ├── Main results
│   ├── Analysis
│   │   ├── Error analysis
│   │   ├── Ablation study
│   │   └── Qualitative examples
│   └── Human evaluation (if applicable)
├── Discussion / Limitations
└── Conclusion
```

## NLP Specific Requirements

### Datasets
- Use **standard benchmarks**: GLUE, SQuAD, CoNLL, OntoNotes
- Report **dataset statistics**: Train/Dev/Test sizes
- **Data preprocessing**: Document all steps

### Evaluation Metrics
- **Task-relevant metrics**: F1, BLEU, ROUGE, accuracy
- **Statistical significance**: Paired bootstrap, p-values
- **Multiple runs**: Report Mean ± SD across different random seeds

### Human Evaluation
Increasingly critical for generative tasks:
- **Annotator details**: Number, qualifications, consistency
- **Evaluation protocol**: Guidelines, interface, compensation
- **Inter-annotator agreement**: Cohen's κ or Krippendorff's α

### Human Evaluation Table Example

```
Table 3: Human Evaluation Results (100 samples, 3 annotators)
─────────────────────────────────────────────────────────────
Method        | Fluency | Coherence | Factuality | Overall
─────────────────────────────────────────────────────────────
Baseline      |   3.8   |    3.2    |    3.5     |   3.5
GPT-3.5       |   4.2   |    4.0    |    3.7     |   4.0
Our Method    |   4.4   |    4.3    |    4.1     |   4.3
─────────────────────────────────────────────────────────────
Inter-annotator agreement κ = 0.72. Scale: 1-5 (higher is better).
```

## ACL Specific Considerations

- **ARR (ACL Rolling Review)**: A unified rolling review system for the ACL family of conferences
- **Responsible NLP Checklist**: Ethics, limitations, and risks
- **Long (8 pages) vs. Short (4 pages)**: Different expectations for scope
- **Findings Papers**: Secondary acceptance track

---

# Part 2: HCI Conferences (CHI, CSCW, UIST)

## HCI Writing Philosophy

> "Technology serves people—understand the user first, then design and evaluate."

HCI papers are fundamentally **user-centered**. Technical novelty alone is insufficient; understanding human needs and proving user benefit is vital.

## Audience and Tone

### Target Readers
- HCI researchers and practitioners
- UX designers and product developers
- Interdisciplinary backgrounds (CS, Psychology, Design, Social Science)

### Tone Characteristics
| Feature | Description |
|---------------|-------------|
| **User-Centered** | Focus on people, not just tech |
| **Design-Driven** | Grounded in design thinking |
| **Empirical** | User studies provide the evidence |
| **Reflective** | Considers broader implications |

## HCI Abstract

### Focus on Users and Impact

```
Video calling has become essential for remote collaboration, yet 
current interfaces poorly support the peripheral awareness that makes 
in-person work effective. Through formative interviews with 24 remote 
workers, we identified three key challenges: difficulty gauging 
colleague availability, lack of ambient presence cues, and interruption 
anxiety. We designed AmbientOffice, a peripheral display system that 
conveys teammate presence through subtle ambient visualizations. In a 
two-week deployment study with 18 participants across three distributed 
teams, AmbientOffice increased spontaneous collaboration by 40% and 
reduced perceived isolation (p<0.01). Participants valued the system's 
non-intrusive nature and reported feeling more connected to remote 
colleagues. We discuss implications for designing ambient awareness 
systems and the tension between visibility and privacy in remote work.
```

## HCI Paper Structure

### Research Through Design (RtD) / Systems Papers

```
├── Introduction
│   ├── Problem in human terms
│   ├── Why technology can help
│   └── Contribution summary
├── Related Work
│   ├── Domain background
│   ├── Prior systems
│   └── Theoretical frameworks
├── Formative Work (often)
│   ├── Interviews / observations
│   └── Design requirements
├── System Design
│   ├── Design rationale
│   ├── Implementation
│   └── Interface walkthrough
├── Evaluation
│   ├── Study design
│   ├── Participants
│   ├── Procedure
│   ├── Findings (quant + qual)
│   └── Limitations
├── Discussion
│   ├── Design implications
│   ├── Generalizability
│   └── Future work
└── Conclusion
```

### Qualitative / Interview-based Studies

```
├── Introduction
├── Related Work
├── Methods
│   ├── Participants
│   ├── Procedure
│   ├── Data collection
│   └── Analysis method (thematic, grounded theory, etc.)
├── Findings
│   ├── Theme 1 (with quotes)
│   ├── Theme 2 (with quotes)
│   └── Theme 3 (with quotes)
├── Discussion
│   ├── Implications for design
│   ├── Implications for research
│   └── Limitations
└── Conclusion
```

## HCI Specific Requirements

### Participant Reporting
- **Demographics**: Age, gender, relevant experience
- **Recruitment**: How and where they were recruited
- **Compensation**: Amount and type of payment
- **IRB Approval**: Statement of ethical board approval

### Quotes in Results
Use direct quotes to support findings:
```
Participants valued the ambient nature of the display. As P7 described: 
"It's like having a window to my teammate's office. I don't need to 
actively check it, but I know they're there." This passive awareness 
reduced the barrier to initiating contact.
```

### Design Implications Section
Translate findings into actionable guidance:
```
**Implication 1: Support peripheral awareness without forcing attention.**
Ambient displays should be visible in the periphery but not require active monitoring. Designers should consider "calm technology" principles.

**Implication 2: Balancing visibility and privacy.**
Users want to share presence but fear surveillance. Systems should provide granular control and make visibility reciprocal.
```

## CHI Specific Considerations

- **Contribution Types**: Empirical, Artifact, Methodological, Theoretical
- **ACM Format**: Use the `acmart` document class with the `sigchi` option
- **Accessibility**: Expectation of Alt text and inclusive language
- **Contribution Statement**: Required listing of specific author contributions

---

# Part 3: Data Mining and Information Retrieval (SIGKDD, WWW, SIGIR)

## Data Mining Writing Philosophy

> "Scalable methods for real-world data with demonstrated practical impact."

Data mining papers emphasize **scalability**, **practical utility**, and **solid experimental methodology**.

## Audience and Tone

### Target Readers
- Data scientists and machine learning engineers
- Industrial researchers
- Applied ML practitioners

### Tone Characteristics
| Feature | Description |
|---------------|-------------|
| **Scalability** | Handling large-scale datasets |
| **Utility** | Real-world applications |
| **Reproducibility** | Sharing datasets and code |
| **Industrial** | Value placed on industry datasets |

## KDD Abstract

### Emphasis on Scale and Application

```
Fraud detection in e-commerce requires processing millions of 
transactions in real-time while adapting to evolving attack patterns. 
We present FraudShield, a graph neural network framework for real-time 
fraud detection that scales to billion-edge transaction graphs. Unlike 
prior methods that require full graph access, FraudShield uses 
incremental updates with O(1) inference cost per transaction. On a 
proprietary dataset of 2.3 billion transactions from a major e-commerce 
platform, FraudShield achieves 94.2% precision at 80% recall, 
outperforming production baselines by 12%. The system has been deployed 
at [Company], processing 50K transactions per second and preventing 
an estimated $400M in annual fraud losses. We release an anonymized 
benchmark dataset and code.
```

## KDD Paper Structure

```
├── Introduction
│   ├── Problem and impact
│   ├── Technical challenges
│   ├── Your approach
│   └── Contributions
├── Related Work
├── Preliminaries
│   ├── Problem definition
│   └── Notation
├── Method
│   ├── Overview
│   ├── Technical components
│   └── Complexity analysis
├── Experiments
│   ├── Datasets (with scale statistics)
│   ├── Baselines
│   ├── Main results
│   ├── Scalability experiments
│   ├── Ablation study
│   └── Case study / deployment
└── Conclusion
```

## KDD Specific Requirements

### Scalability
- **Dataset Size**: Report number of nodes, edges, or samples
- **Runtime Analysis**: Wall-clock time comparisons
- **Complexity**: Explicit time and space complexity
- **Scaling Experiments**: Show performance curves as data size increases

### Industrial Deployment
- **Case Studies**: Real-world deployment stories
- **A/B Testing**: Online evaluation results (if applicable)
- **Production Metrics**: Business impact (if shareable)

### Scalability Table Example

```
Table 4: Scalability Comparison (Runtime in seconds)
──────────────────────────────────────────────────────
Dataset     | Nodes  | Edges  | GCN   | GraphSAGE | Ours
──────────────────────────────────────────────────────
Cora        |  2.7K  |  5.4K  |  0.3  |    0.2    |  0.1
Citeseer    |  3.3K  |  4.7K  |  0.4  |    0.3    |  0.1
PubMed      | 19.7K  | 44.3K  |  1.2  |    0.8    |  0.3
ogbn-arxiv  | 169K   | 1.17M  |  8.4  |    4.2    |  1.6
ogbn-papers | 111M   | 1.6B   |  OOM  |   OOM     | 42.3
──────────────────────────────────────────────────────
```

---

# Part 4: Universal Elements for All CS Conferences

## Writing Quality

### Clarity
- **One core idea per sentence**
- **Define terms before use**
- **Use consistent notation**

### Precision
- **Exact numbers**: Use "23.4%" instead of "about 20%"
- **Explicit claims**: Avoid hedging unless necessary
- **Specific comparisons**: Name the baselines

## Contribution Bullets

Applicable to all CS conferences:
```
Our contributions are:
• We identify [problem/insight]
• We propose [method name] that [key innovation]
• We demonstrate [results] on [benchmarks]
• We release [code/data] at [URL]
```

## Reproducibility Standards

Expectations are rising across all CS venues:
- **Code Availability**: GitHub links (anonymized for review)
- **Data Availability**: Public datasets or release plans
- **Full Hyperparameters**: Complete training details
- **Random Seeds**: Provide exact values for replication

## Ethics and Broader Impact

### NLP (ACL/EMNLP)
- **Limitations Section**: Mandatory
- **Responsible NLP Checklist**: Ethical considerations
- **Bias Analysis**: For models affecting humans

### HCI (CHI)
- **IRB/Ethics Approval**: Mandatory for human subjects
- **Informed Consent**: Describe the process
- **Privacy Considerations**: Data handling practices

### KDD/WWW
- **Social Impact**: Consider potential misuse
- **Privacy Preservation**: For sensitive data
- **Fairness Analysis**: Where applicable

---

## Conference Comparison Table

| Dimension | ACL/EMNLP | CHI | KDD/WWW | SIGIR |
|--------|-----------|-----|---------|-------|
| **Primary Focus** | NLP Tasks | User Research | Scalable ML | IR/Search |
| **Evaluation** | Benchmarks + Human | User Studies | Large-scale Exp | Datasets |
| **Theory Weight** | Medium | Low | Medium | Medium |
| **Industry Value** | High | Medium | Very High | High |
| **Page Limits** | 8 Long / 4 Short | 10 + Refs | 9 + Refs | 10 + Refs |
| **Review Style** | ARR | Direct | Direct | Direct |

---

## Pre-submission Checklist

### All CS Conferences
- [ ] Contribution statement is clear
- [ ] Baselines are strong
- [ ] Reproducibility info is complete
- [ ] Correct conference template used
- [ ] Anonymized (if double-blind)

### NLP Specific
- [ ] Results on standard benchmarks
- [ ] Error analysis included
- [ ] Human evaluation (for generative tasks)
- [ ] Responsible NLP checklist

### HCI Specific
- [ ] IRB approval stated
- [ ] Participant demographics included
- [ ] Direct quotes in results
- [ ] Design implications included

### Data Mining Specific
- [ ] Scalability experiments included
- [ ] Dataset scale statistics
- [ ] Runtime comparisons
- [ ] Complexity analysis

---

## See Also

- `venue_writing_styles.md` - General style overview
- `ml_conference_style.md` - NeurIPS/ICML writing guide
- `conferences_formatting.md` - Technical formatting requirements
- `reviewer_expectations.md` - What CS reviewers look for