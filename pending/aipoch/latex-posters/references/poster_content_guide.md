# Research Poster Content Guide

## Overview

Content is the core of research posters. This guide covers writing strategies, specific guidance for each section, visual-to-text balance, and best practices for effectively communicating research findings in poster format.

## Core Content Principles

### 1. The 3-5 Minute Rule

**Reality**: Most viewers spend 3-5 minutes at your poster
- **1 minute**: Distant scan (title, figures)
- **2-4 minutes**: Close reading of key points
- **5+ minutes**: In-depth discussion (if interested)

**Design implications**: Posters must work on three levels:
1. **Distant view** (6-10 feet): Title and main figures clearly visible
2. **Scanning view** (3-6 feet): Section headers and key results readable
3. **Detail view** (1-3 feet): Full content easily accessible

### 2. Tell a Story, Don't Present a Paper

**Poster ≠ Compressed paper**

**Paper approach** (❌):
- Comprehensive literature review
- Detailed methodology
- All results presented
- Lengthy discussion
- 50+ references

**Poster approach** (✅):
- One-sentence background
- Visualized methods diagram
- 3-5 key results
- 3-4 bullet-point conclusions
- 5-10 core references

**Poster story arc:**
```
Hook (Problem) → Methods → Findings → Impact
```

**Example:**
- **Hook**: "Antibiotic resistance threatens millions of lives annually"
- **Methods**: "We developed an AI system to predict resistance patterns"
- **Findings**: "Our model achieved 87% accuracy, 20% better than existing methods"
- **Impact**: "Could reduce treatment failures by identifying resistance earlier"

### 3. The 800 Word Maximum

**Word count guidelines:**
- **Ideal**: 300-500 words
- **Maximum**: 800 words
- **Hard limit**: 1000 words (beyond this, poster becomes unreadable)

**Word budget by section:**
| Section | Word Count | % of Total |
|---------|-----------|------------|
| Introduction/Background | 50-100 | 15% |
| Methods | 100-150 | 25% |
| Results (text) | 100-200 | 25% |
| Discussion/Conclusions | 100-150 | 25% |
| References/Acknowledgments | 50-100 | 10% |

**Word count tools:**
```latex
% Add word count to poster (remove from final)
\usepackage{texcount}
% Compile command: texcount -inc poster.tex
```

### 4. Visual-to-Text Ratio

**Optimal balance**: 40-50% visual content, 50-60% text + white space

**Visual content includes:**
- Figures and charts
- Photos and images
- Diagrams and flowcharts
- Icons and symbols
- Color blocks and design elements

**Text-heavy** (❌):
- Dense walls of text
- Figures too small
- Overwhelms audience
- Low engagement

**Well-balanced** (✅):
- Clear figures dominate
- Text supports visual content
- Easy to scan
- Visually appealing

## Section Content Guidance

### Title

**Purpose**: Attract attention, convey subject, establish credibility

**Effective title characteristics:**
- **Concise**: Maximum 10-15 words
- **Descriptive**: Clearly state research topic
- **Active**: Use strong verbs when possible
- **Specific**: Avoid vague terms
- **Professional**: Balance domain terminology with accessibility

**Title formulas:**

**1. Descriptive:**
```
[Method/Approach] for [Problem/Application]

Example: "Deep Learning for Early Detection of Alzheimer's Disease"
```

**2. Question:**
```
[Research Question]?

Example: "Can Microbiome Diversity Predict Treatment Response?"
```

**3. Declarative:**
```
[Finding] in [Context]

Example: "Novel Mechanism Identified in Drug Resistance Pathways"
```

**4. Colon format:**
```
[Topic]: [Specific Method/Finding]

Example: "Urban Heat Islands: A Machine Learning Framework for Mitigation"
```

**Avoid:**
- ❌ Vague titles: "A Study of X"
- ❌ Overly clever wordplay (distracts from message)
- ❌ Too much jargon: "Utilization of CRISPR-Cas9..."
- ❌ Unnecessarily wordy: "Investigation of the potential role of..."

**LaTeX title formatting:**
```latex
% Use bold for emphasis on key words
\title{Deep Learning for \textbf{Early Detection} of Alzheimer's Disease}

% Use double line for long titles
\title{Machine Learning Framework for\\Urban Heat Island Mitigation}

% Avoid ALL CAPS (harder to read)
```

### Authors and Affiliations

**Best practices:**
- **Presenting author**: Bold, underlined, or asterisked
- **Corresponding author**: Include email
- **Affiliations**: Use superscript numbers or symbols
- **Institution logos**: Maximum 2-4

**Format examples:**
```latex
% Simple format
\author{\textbf{Jane Smith}\textsuperscript{1}, John Doe\textsuperscript{2}}
\institute{
  \textsuperscript{1}University of Example, 
  \textsuperscript{2}Research Institute
}

% With contact info
\author{Jane Smith\textsuperscript{1,*}}
\institute{
  \textsuperscript{1}Department, University\\
  \textsuperscript{*}jane.smith@university.edu
}
```

### Introduction/Background

**Purpose**: Establish context, state research motivation, present objectives

**Structure** (50-100 words):
1. **Problem statement** (1-2 sentences): What is the core problem?
2. **Knowledge gap** (1-2 sentences): What is unknown or unsolved?
3. **Research objective** (1 sentence): What did you do?

**Example** (95 words):
```
Antibiotic resistance causes 700,000 deaths annually, projected to reach 
10 million by 2050. Current diagnostic methods require 48-72 hours, 
delaying appropriate treatment. Machine learning offers potential for rapid 
resistance prediction, but existing models lack generalizability across 
bacterial species.

We developed a Transformer-based deep learning model to predict 
antibiotic resistance from genomic sequences of multiple pathogen species. 
Our approach integrates evolutionary information and protein structure 
to improve cross-species accuracy.
```

**Visual support:**
- Concept diagram showing the problem
- Infographics with statistics
- Images of application context

**Common mistakes:**
- ❌ Extensive literature review
- ❌ Too much background detail
- ❌ Undefined abbreviations on first use
- ❌ Missing clear objective statement

### Methods

**Purpose**: Describe methods adequately for audience understanding (not for reproducibility)

**Key question**: "How did you do it?" not "How can others reproduce it?"

**Content strategy:**
- **Prioritize**: Visual method diagram > text description
- **Include**: Research design, key steps, analysis methods
- **Omit**: Detailed experimental protocols, routine steps, specific reagent details

**Visualized methods (strongly recommended):**
```latex
% Flowchart of research design
\begin{tikzpicture}[node distance=2cm]
  \node (start) [box] {Data Collection\\n=1,000 samples};
  \node (process) [box, below of=start] {Preprocessing\\Quality Control};
  \node (analysis) [box, below of=process] {Statistical Analysis\\Mixed Models};
  \node (end) [box, below of=analysis] {Validation\\Independent Cohort};
  
  \draw [arrow] (start) -- (process);
  \draw [arrow] (process) -- (analysis);
  \draw [arrow] (analysis) -- (end);
\end{tikzpicture}
```

**Text methods** (50-150 words):

**For experimental research:**
```
Methods
• Study design: Randomized controlled trial (n=200)
• Participants: Adults aged 18-65 with type 2 diabetes
• Intervention: 12-week exercise program vs. standard care
• Outcomes: HbA1c (primary), insulin sensitivity (secondary)
• Analysis: Linear mixed models, intention-to-treat
```

**For computational research:**
```
Methods
• Dataset: 10,000 annotated images from ImageNet
• Architecture: ResNet-50 with custom attention
• Training: 100 epochs, Adam optimizer, learning rate 0.001
• Validation: 5-fold cross-validation
• Comparison: Baseline CNN, VGG-16, Inception-v3
```

**Format options:**
- **Bullet points**: Quick scanning (recommended)
- **Numbered lists**: Sequential steps
- **Diagram + brief text**: Ideal combination
- **Tables**: Multiple conditions or parameters

### Results

**Purpose**: Present key findings visually and clearly

**Golden rule**: Show, don't tell

**Content allocation:**
- **Figures**: 70-80% of results section
- **Text**: 20-30% (brief descriptions, statistics)

**How many results to show:**
- **Ideal**: 3-5 main findings
- **Maximum**: 6-7 independent results
- **Focus**: Primary outcomes, most impactful findings

**Figure selection criteria:**
1. Does it support the core message?
2. Is it self-explanatory with caption?
3. Can it be understood in 10 seconds?
4. Does it add information beyond the text?

**Figure captions:**
- **Descriptive**: Explain what is shown
- **Independent**: Understandable without reading full poster
- **Statistical**: Include significance, sample sizes
- **Concise**: 1-3 sentences

**Caption example:**
```latex
\caption{Treatment significantly improved outcomes.
Figure shows mean ± standard deviation for control (blue, n=45) 
and treatment (orange, n=47) groups. **p<0.01, ***p<0.001 (two-tailed t-test).}
```

**Text support for results** (100-200 words):
- State main finding for each figure
- Include key statistics
- Point out trends or patterns
- Avoid detailed explanations (save for discussion)

**Results text example:**
```
Key Findings
• Model achieved 87% accuracy on test set (vs. 73% baseline)
• Consistent performance across 5 bacterial species (p<0.001)
• Prediction speed: <30 seconds per isolate
• Feature importance: Protein structure (42%), sequence (35%), 
  evolutionary conservation (23%)
```

**Data presentation formats:**

**1. Bar charts**: Comparing categories
```latex
\begin{tikzpicture}
  \begin{axis}[
    ybar,
    ylabel=Accuracy (\%),
    symbolic x coords={Baseline, Model A, Our Method},
    xtick=data,
    nodes near coords
  ]
  \addplot coordinates {(Baseline,73) (Model A,81) (Our Method,87)};
  \end{axis}
\end{tikzpicture}
```

**2. Line charts**: Trends over time
**3. Scatter plots**: Correlations
**4. Heatmaps**: Matrix data, clustering
**5. Box plots**: Distributions, comparisons
**6. ROC curves**: Classification performance

### Discussion/Conclusions

**Purpose**: Explain findings, state implications, acknowledge limitations

**Structure** (100-150 words):

**1. Main conclusions** (50-75 words):
- 3-5 bullet points
- Clear, specific points
- Tied to research objectives

**Example:**
```
Conclusions
• First model to achieve >85% accuracy for cross-species antibiotic resistance prediction
• Protein structure integration is crucial for generalizability (14% accuracy improvement)
• Prediction speed supports clinical decision-making within clinic hours
• Potential to reduce inappropriate antibiotic use by 20-30%
```

**2. Limitations** (25-50 words, optional but recommended):
- Acknowledge key constraints
- Brief, honest
- Show scientific rigor

**Example:**
```
Limitations
• Training data limited to 5 bacterial species
• Requires genomic sequencing (not yet widely available)
• Needs validation in prospective clinical trials
```

**3. Future directions** (25-50 words, optional):
- Next steps
- Broader impacts
- Call to action

**Example:**
```
Next Steps
• Expand to 20+ additional species
• Develop point-of-care sequencing integration
• Launch multi-center clinical validation study (2025)
```

**Avoid:**
- ❌ Exaggerating findings: "This revolutionary breakthrough..."
- ❌ Extensive comparisons with other work
- ❌ Presenting new results in discussion
- ❌ Vague conclusions: "More research is needed"

### References

**Number**: 5-10 key citations

**Selection criteria:**
- Include seminal work in the field
- Recent relevant research (within 5 years)
- Methods cited in poster
- Controversial claims that need support

**Format**: Abbreviated, consistent style

**Examples:**

**Numbered (Vancouver):**
```
References
1. Smith et al. (2023). Nature. 615:234-240.
2. Jones & Lee (2024). Science. 383:112-118.
3. Chen et al. (2022). Cell. 185:456-470.
```

**Author-date (APA):**
```
References
Smith, J. et al. (2023). Title. Nature, 615, 234-240.
Jones, A., & Lee, B. (2024). Title. Science, 383, 112-118.
```

**Minimalist (when space is limited):**
```
Key References: Smith (Nature 2023), Jones (Science 2024), 
Chen (Cell 2022). Full bibliography: [QR Code]
```

**Alternative**: QR code linking to full reference list

### Acknowledgments

**Include:**
- Funding sources (with grant numbers)
- Key collaborators
- Core facilities used
- Data sources

**Format** (25-50 words):
```
Acknowledgments
Supported by NIH grant R01-123456 and NSF award 7890123.
Thanks to Dr. X for data access, Y core facility for sequencing 
support, and Z for helpful discussions.
```

### Contact Information

**Elements:**
- Presenting/corresponding author name
- Email address
- Optional: Lab website, Twitter/X, LinkedIn, ORCID

**Format:**
```
Contact: Jane Smith, jane.smith@university.edu
Lab: smithlab.university.edu | Twitter: @smithlab
```

**QR code alternatives:**
- Link to personal/lab website
- Link to paper preprint/published version
- Link to code repository (GitHub)
- Link to supplementary materials

## Poster Writing Style

### Active vs. Passive Voice

**Prefer active voice** (more engaging, clearer):
- ✅ "We developed a model..."
- ✅ "The treatment reduced symptoms..."

**Passive voice** (use when appropriate):
- ✅ "Samples were collected from..."
- ✅ "Data were analyzed using..."

### Sentence Length

**Keep sentences short:**
- **Ideal**: 10-15 words per sentence
- **Maximum**: 20-25 words
- **Avoid**: Over 30 words (hard to follow)

**Revision example:**
- ❌ Verbose: "We performed a comprehensive analysis of gene expression data from 500 colorectal cancer patients using RNA sequencing and identified 47 differentially expressed genes associated with treatment response."
- ✅ Concise: "We analyzed RNA sequencing data from 500 colorectal cancer patients. We identified 47 genes associated with treatment response."

### Bullet Points vs. Paragraphs

**Use bullets for:**
- ✅ Lists of items or findings
- ✅ Key conclusions
- ✅ Method steps
- ✅ Research characteristics

**Use short paragraphs for:**
- ✅ Narrative flow (introduction)
- ✅ Complex explanations
- ✅ Connected ideas

**Bullet best practices:**
- Start with verb or noun
- Parallel structure throughout list
- 3-7 items per list (not too many)
- Brief (1-2 lines each)

**Example:**
```
Methods
• Participants: 200 adults (18-65 years)
• Design: Double-blind RCT (12 weeks)
• Intervention: 30 minutes daily exercise
• Control: Standard care
• Analysis: Mixed models (SPSS v.28)
```

### Abbreviations and Terminology

**First-use rule**: Define on first appearance
```
We used machine learning (ML) to analyze... Later, ML predicted...
```

**Common abbreviations**: May not need definition if standard in field
- DNA, RNA, MRI, CT, PCR (biomedical)
- AI, ML, CNN (computer science)

**Avoid overuse of flowery language:**
- ❌ "Utilized" → ✅ "Used"
- ❌ "Implement utilization of" → ✅ "Use"
- ❌ "A majority of" → ✅ "Most"

### Numbers and Statistics

**Present statistics clearly:**
- Always include variability measures (SD, SE, CI)
- Report sample sizes: n=50
- Indicate significance: p<0.05, p<0.01, p<0.001
- Use symbols consistently: * for p<0.05, ** for p<0.01

**Number formatting:**
- Round appropriately (avoid false precision)
- Maintain consistent decimal places
- Include units: 25 mg/dL, 37°C
- Large numbers: 1,000 or 1000 (be consistent)

**Example:**
```
Treatment improved response rate by 23.5% (95% CI: 18.2-28.8%, p<0.001, n=150)
```

## Visual and Text Integration

### Figure-Text Relationship

**Figures first, text second:**
1. Design poster around key figures
2. Add text to support and explain visuals
3. Ensure figures can stand alone

**Text placement relative to figures:**
- **Above**: Background info, "what you're about to see"
- **Below**: Explanations, statistics, captions
- **Beside**: Comparisons, elaboration

### Labels and Annotations

**On-figure annotations:**
```latex
\begin{tikzpicture}
  \node[inner sep=0] (img) {\includegraphics[width=10cm]{figure.pdf}};
  \draw[->, thick, red] (8,5) -- (6,3) node[left] {Key region};
  \draw[red, thick] (3,2) circle (1cm) node[above=1.2cm] {Anomaly};
\end{tikzpicture}
```

**Callout boxes:**
```latex
\begin{tcolorbox}[colback=yellow!10, colframe=orange!80, 
                  title=Key Finding]
Our method reduced error by 34\% compared to state-of-the-art.
\end{tcolorbox}
```

### Section Title Icons

**Visual section markers:**
```latex
\usepackage{fontawesome5}

\block{\faFlask~Introduction}{...}
\block{\faCog~Methods}{...}
\block{\faChartBar~Results}{...}
\block{\faLightbulb~Conclusions}{...}
```

## Content Adaptation Strategies

### From Paper to Poster

**Compression process:**

**1. Identify core message** (elevator pitch):
- What is the one thing you want people to remember most?
- If you only had 30 seconds, what would you say?

**2. Select key results:**
- Pick 3-5 most impactful findings
- Omit supporting/secondary results
- Focus on figures with strong visual impact

**3. Simplify methods:**
- Visual flowchart > text description
- Omit routine procedures
- Include only key parameters

**4. Trim literature review:**
- One-sentence background
- One-sentence gap/motivation
- One-sentence your contribution

**5. Condense discussion:**
- Keep only main conclusions
- Brief limitations
- One-sentence future directions

### For Different Audiences

**Expert audience** (same field):
- Can use domain-specific terminology
- Need less background
- Focus on novel methodology
- Emphasize nuanced findings

**General scientific audience:**
- Define key terms
- More context/background
- Broader implications
- Visual metaphors helpful

**Public/non-specialist audience:**
- Minimal jargon, all defined
- Extensive background
- Real-world applications
- Analogies and simple language

**Adaptation examples:**

**Expert**: "CRISPR-Cas9 knockout of BRCA1 induced synthetic lethality with PARP inhibitors"

**General**: "We used gene editing to make cancer cells vulnerable to existing drugs"

**Public**: "We found a way to make cancer treatments more effective by targeting specific genetic weaknesses"

## Quality Control Checklist

### Content Review

**Clarity:**
- [ ] Core message immediately obvious
- [ ] All abbreviations defined
- [ ] Sentences short and direct
- [ ] No unnecessary jargon

**Completeness:**
- [ ] Research question/objective stated
- [ ] Methods adequately described
- [ ] Key results presented
- [ ] Conclusions drawn
- [ ] Limitations acknowledged

**Accuracy:**
- [ ] All statistics correct
- [ ] Figure captions accurate
- [ ] References properly cited
- [ ] No overstatement

**Interactivity:**
- [ ] Title grabs attention
- [ ] Visually appealing
- [ ] Key points obvious
- [ ] Includes discussion prompts

### Readability Testing

**Distance test:**
- Print at 25% scale
- View from 2-3 feet away (simulates full-size 8-12 feet viewing)
- Can you read: title? section headers? body text?

**Scanning test:**
- Show poster to colleague for 30 seconds
- Ask: "What is this poster about?"
- They should identify: topic, methods, main findings

**Detail test:**
- Have colleague read poster thoroughly (5 minutes)
- Ask: "What were the key conclusions?"
- Verify their understanding matches your intent

## Common Content Mistakes

**1. Too much text**
- ❌ >1000 words
- ❌ Long paragraphs
- ❌ Compressed version of full paper
- ✅ 300-800 words, use bullets, key findings only

**2. Unclear message**
- ❌ Multiple unrelated findings
- ❌ No clear conclusion
- ❌ Vague impact statements
- ✅ 1-3 main points, explicit conclusions

**3. Methods too lengthy**
- ❌ Detailed experimental protocols
- ❌ Listing all parameters
- ❌ Describing routine steps
- ✅ Visual flowchart, key details only

**4. Poor figure integration**
- ❌ Figures lack context
- ❌ Unclear captions
- ❌ Text doesn't reference figures
- ✅ Centered figures, detailed captions, integrated text

**5. Missing context**
- ❌ No background introduction
- ❌ Undefined abbreviations
- ❌ Assuming all audience are experts
- ✅ Brief background, provide definitions, wider audience

## Conclusion

Effective poster content should be:
- **Concise**: Maximum 300-800 words
- **Visual**: 40-50% figures and graphics
- **Clear**: One core message, 3-5 key findings
- **Engaging**: Tell a story, not just facts
- **Accessible**: Appropriate for target audience
- **Informative**: Clear implications and next steps

Remember: Your poster is the beginning of a conversation, not a substitute for a detailed paper. Design content to spark curiosity, encourage engagement, and invite discussion.
