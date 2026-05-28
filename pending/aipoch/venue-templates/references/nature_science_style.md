# Nature and Science Writing Style Guide

A comprehensive writing guide for *Nature*, *Science*, and related high-impact multidisciplinary journals (*Nature Communications*, *Science Advances*, PNAS).

**Last Updated**: 2024

---

## Overview

*Nature* and *Science* are the world's premier cutting-edge multidisciplinary scientific journals. Papers published in these journals must appeal to scientists in all disciplines, not just experts in the relevant field. This core requirement fundamentally shapes their writing style.

### Core Philosophy

> "If a structural biologist cannot understand why your particle physics paper is important, it will not be published in *Nature*."

**Primary Goal**: To communicate groundbreaking scientific results to an educated but non-specialist audience.

---

## Audience and Tone

### Target Readers

- PhD-level scientists in **any** field
- Familiar with scientific methodology
- **Not** experts in your specific sub-field
- Read widely to stay informed about the frontiers of science

### Tone Characteristics

| Feature | Description |
|---------------|-------------|
| **Accessible** | Avoid jargon; explain technical concepts |
| **Engaging** | Hook the reader; tell a story |
| **Significant** | Emphasize why the research has broad implications |
| **Confident** | State findings clearly (with appropriate qualifiers/hedging) |
| **Active** | Use the active voice; embrace the first person |

### Voice

- **Encourage the use of the first-person plural ("We")**: Use "We discovered that..." instead of "It was discovered that..."
- **Prefer the active voice**: Use "We measured..." instead of "Measurements were taken..."
- **Direct statements**: Use "Protein X controls Y" instead of "Protein X appears to potentially control Y"

---

## Abstract

### Style Requirements

- **Fluid paragraphs** (do not use labeled subsections)
- *Nature* requires **150-200 words**; *Nature Communications* up to 250 words
- **No citations** in the abstract
- **No abbreviations** (if essential, define at first mention)
- **Self-contained**: Understandable without reading the full text

### Abstract Structure (Implicit)

Cover the following in fluid prose:

1. **Background** (1-2 sentences): Why the field matters
2. **Gap/Problem** (1 sentence): What is unknown or problematic
3. **Approach** (1 sentence): What you did (briefly)
4. **Core Findings** (2-3 sentences): Primary results and key data
5. **Significance** (1-2 sentences): Why this is important and what the impact is

### Abstract Example (Nature Style)

```
The origins of multicellular life remain one of biology's greatest mysteries. 
How individual cells first cooperated to form complex organisms has been 
difficult to study because the transition occurred over 600 million years ago. 
Here we show that the unicellular alga Chlamydomonas reinhardtii can evolve 
simple multicellular structures within 750 generations when exposed to 
predation pressure. Using experimental evolution with the predator Paramecium, 
we observed the emergence of stable multicellular clusters in 5 of 10 
replicate populations. Genomic analysis revealed that mutations in just two 
genes—encoding cell adhesion proteins—were sufficient to trigger this 
transition. These results demonstrate that the evolution of multicellularity 
may require fewer genetic changes than previously thought, providing insight 
into one of life's major transitions.
```

### Writing Don'ts

❌ **Too Technical**:
> "Using CRISPR-Cas9-mediated knockout of the CAD1 gene (encoding cadherin-1) in C. reinhardtii strain CC-125, we demonstrated that loss of CAD1 function combined with overexpression of FLA10 under control of the HSP70A/RBCS2 tandem promoter..."

❌ **Too Vague**:
> "We studied how cells can form groups. Our results are interesting and may have implications for understanding evolution."

---

## Introduction

### Length and Structure

- **3-5 paragraphs** (approx. 500-800 words)
- **Funnel structure**: Macro → Specific → Your contribution

### Paragraph-by-Paragraph Guide

**Paragraph 1: The Big Picture**
- Open with a grand, engaging statement about the field
- Establish the importance of the field to science/society
- Readable by any scientist

```
Example:
"The ability to predict protein structure from sequence alone has been a grand 
challenge of biology for over 50 years. Accurate predictions would transform 
drug discovery, enable understanding of disease mechanisms, and illuminate the 
fundamental rules governing molecular self-assembly."
```

**Paragraphs 2-3: What is Known**
- Review key previous work (be selective, not exhaustive)
- Gradually lead to the gap you will address
- Citations should focus on core papers

```
Example:
"Significant progress has been made through template-based methods that 
leverage known structures of homologous proteins. However, for the estimated 
30% of proteins without detectable homologs, prediction accuracy has remained 
limited. Deep learning approaches have shown promise, achieving improved 
accuracy on benchmark datasets, yet still fall short of experimental accuracy 
for many protein families."
```

**Paragraph 4: The Research Gap**
- Clearly state what remains unknown or unresolved
- Frame it as an important question

```
Example:
"Despite these advances, the fundamental question remains: can we predict 
protein structure with experimental-level accuracy for proteins across all 
of sequence space? This capability would democratize structural biology and 
enable rapid characterization of newly discovered proteins."
```

**Final Paragraph: This Work**
- State what you did and preview key findings
- Signal the importance of your contribution

```
Example:
"Here we present AlphaFold2, a neural network architecture that predicts 
protein structure with atomic-level accuracy. In the CASP14 blind assessment, 
AlphaFold2 achieved a median GDT score of 92.4, matching experimental 
accuracy for most targets. We show that this system can be applied to predict 
structures across entire proteomes, opening new avenues for understanding 
protein function at scale."
```

### Introduction Don'ts

- ❌ Do not start with "Since ancient times..." or overly flowery hyperbole
- ❌ Do not provide an exhaustive literature review (that is for specialized journals)
- ❌ Do not include methods or results in the introduction
- ❌ Do not use unexplained abbreviations or jargon

---

## Results

### Organizational Philosophy

**Story-driven, not experiment-driven**

Organize content by **discovery**, not by the chronological order of experiments:

❌ **Experiment-driven** (Avoid):
> "We first performed experiment A. Next, we did experiment B. Then we conducted experiment C."

✅ **Discovery-driven** (Preferred):
> "We discovered that X. To understand the mechanism, we found that Y. This led us to test whether Z, confirming our hypothesis."

### Results Writing Style

- Use **past tense** to describe work done/findings
- Use **present tense** to refer to figures ("Figure 2 shows...")
- **Objective but interpretive**: Maintain minimal interpretation when stating findings, but provide enough context for non-specialists
- **Quantitative**: Include key numbers, statistics, and effect sizes

### Results Paragraph Example

```
To test whether protein X is required for cell division, we generated 
knockout cell lines using CRISPR-Cas9 (Fig. 1a). Cells lacking protein X 
showed a 73% reduction in division rate compared to controls (P < 0.001, 
n = 6 biological replicates; Fig. 1b). Live-cell imaging revealed that 
knockout cells arrested in metaphase, with 84% showing abnormal spindle 
morphology (Fig. 1c,d). These results demonstrate that protein X is 
essential for proper spindle assembly and cell division.
```

### Subheadings

Use descriptive subheadings that communicate the discovery:

❌ **Vague**: "Protein expression analysis"
✅ **Informative**: "Protein X is upregulated in response to stress"

---

## Discussion

### Structure (4-6 paragraphs)

**Paragraph 1: Summary of Key Findings**
- Restate the main findings (do not repeat the results section verbatim)
- State whether the hypothesis was supported

**Paragraphs 2-3: Interpretation and Context**
- What do these findings mean?
- How do they relate to previous work?
- What mechanisms explain these results?

**Paragraph 4: Broader Implications**
- Why does this matter outside your specific system?
- Connections to other fields
- Potential applications

**Paragraph 5: Limitations**
- Honestly acknowledge limitations
- Be specific, not generic

**Final Paragraph: Conclusion and Future**
- Big-picture take-home message
- Briefly mention future research directions

### Discussion Writing Tips

- **Start with significance**, not with caveats or limitations
- **Contrast literature constructively**: "Our findings extend the work of Smith et al. by demonstrating..."
- **Acknowledge alternative interpretations**: "An alternative explanation is that..."
- **Be honest about limitations**: Specificity > Generality

### Limitations Statement Example

❌ **Generic**: "Our study has limitations that should be addressed in future work."

✅ **Specific**: "Our analysis was limited to cultured cells, which may not fully recapitulate the tissue microenvironment. Additionally, the 48-hour observation window may miss slower-developing phenotypes."

---

## Methods

### Location of Methods in Nature Style

- **Brief Methods** are placed in the main text (usually at the end)
- **Extended Methods** are placed in the Supplementary Information
- Must be detailed enough for others to replicate the experiments

### Writing Style

- **Past tense, passive voice acceptable**: "Cells were cultured..." or "We cultured cells..."
- **Precise and reproducible**: Include concentrations, times, temperatures
- **Cite established protocols**: "Following the method of Smith et al.³..."

---

## Figures

### Figure Philosophy

*Nature* values a combination of **conceptual diagrams** and data figures:

1. **Figure 1**: Usually a schematic/model showing the concept
2. **Data Figures**: Clear, not crowded
3. **Final Figure**: Often a summary model

### Figure Design Principles

- **Single column (89 mm)** or **double column (183 mm)** width
- **High resolution**: 300+ dpi for photos, 1000+ dpi for line art
- **Color-blind friendly**: Avoid relying solely on red-green distinctions
- **Minimize chart junk**: No 3D effects, no unnecessary gridlines
- **Complete legends**: Self-explanatory without reading the main text

### Figure Legend Format

```
Figure 1 | Protein X controls cell division through spindle assembly.
a, Schematic of the experimental approach. b, Quantification of cell 
division rate in control (grey) and knockout (blue) cells. Data are 
mean ± s.e.m., n = 6 biological replicates. ***P < 0.001, two-tailed 
t-test. c,d, Representative images of spindle morphology in control (c) 
and knockout (d) cells. Scale bars, 10 μm.
```

---

## References

### Citation Style

- **Superscript numbers**: ¹, ², ¹⁻³, ¹'⁵'⁷
- Reference list follows **Nature format**

### Reference Format

```
1. Watson, J. D. & Crick, F. H. C. Molecular structure of nucleic acids. 
   Nature 171, 737–738 (1953).

2. Smith, A. B., Jones, C. D. & Williams, E. F. Discovery of protein X. 
   Science 380, 123–130 (2023).
```

### Citation Best Practices

- **Recent literature**: Include papers from the last 2-3 years
- **Seminal papers**: Cite foundational work
- **Diverse sources**: Do not over-cite your own work
- **Primary sources**: Cite original discoveries rather than reviews whenever possible

---

## Language and Style Tips

### Vocabulary Choice

| Avoid | Recommend |
|-------|--------|
| utilize | use |
| methodology | method |
| in order to | to |
| a large number of | many |
| at this point in time | now |
| has the ability to | can |
| it is interesting to note that | [Delete] |

### Sentence Structure

- **Mix long and short sentences**: Alternate for rhythm
- **Important info first**: Place key information at the beginning of the sentence
- **One idea per sentence**: Break complex thoughts into multiple sentences

### Paragraph Structure

- **Topic sentence first**: State the core point
- **Supporting evidence**: Provide data and citations
- **Transition**: Connect to the next paragraph

---

## Comparison: Nature vs. Science

| Feature | Nature | Science |
|---------|--------|---------|
| Abstract Length | 150-200 words | ≤125 words |
| Citation Style | Superscript numbers | Numbers in parentheses (1, 2) |
| Titles in Refs | Yes | No (except primary refs) |
| Methods Location | End of paper or SI | Supplementary Information |
| Significance Statement | No | No |
| Open Access Options | Yes | Yes |

---

## Common Rejection Reasons

1. **Lack of broad interest**: Too specialized for *Nature*/*Science*
2. **Incremental progress**: Not disruptive enough
3. **Overselling**: Conclusions not supported by data
4. **Poor readability**: Too technical for a general audience
5. **Weak significance statement**: Unclear "So what?"
6. **Insufficient novelty**: Similar findings already published elsewhere
7. **Methodological issues**: Results are not convincing

---

## Pre-submission Checklist

### Content
- [ ] The first paragraph clearly states the significance to a broad audience
- [ ] Non-specialists can understand the abstract
- [ ] Results are story-driven (not a lab notebook)
- [ ] Discussion emphasizes impact and significance
- [ ] Limitations are explicitly acknowledged

### Style
- [ ] Active voice dominates
- [ ] Jargon is minimized or explained
- [ ] Sentence lengths are varied
- [ ] Paragraphs have clear topic sentences

### Technical
- [ ] Figures are high resolution
- [ ] Citations are formatted correctly
- [ ] Word count is within limits
- [ ] Line numbers are included
- [ ] Double-spaced

---

## See Also

- `venue_writing_styles.md` - General writing style overview
- `journals_formatting.md` - Technical formatting requirements
- `reviewer_expectations.md` - What *Nature*/*Science* reviewers look for