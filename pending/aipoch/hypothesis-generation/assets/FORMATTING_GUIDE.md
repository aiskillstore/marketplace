# Hypothesis Generation Report - Quick Format Reference

## Overview

This guide provides a quick reference for using the Hypothesis Generation LaTeX template and style package. For the full documentation, please refer to `SKILL.md`.

## Quick Start

```latex
% !TEX program = xelatex
\documentclass[11pt,letterpaper]{article}
\usepackage{hypothesis_generation}
\usepackage{natbib}

\title{Your Phenomenon Name}
\begin{document}
\maketitle
% Your content
\end{document}
```

**Compilation:** Use XeLaTeX or LuaLaTeX for best results.
```bash
xelatex your_document.tex
bibtex your_document
xelatex your_document.tex
xelatex your_document.tex
```

## Color Scheme Reference

### Hypothesis Colors
- **Hypothesis 1**: Deep Blue (RGB: 0, 102, 153) - Used for the first hypothesis.
- **Hypothesis 2**: Forest Green (RGB: 0, 128, 96) - Used for the second hypothesis.
- **Hypothesis 3**: Royal Purple (RGB: 102, 51, 153) - Used for the third hypothesis.
- **Hypothesis 4**: Teal (RGB: 0, 128, 128) - Used for the fourth hypothesis (if needed).
- **Hypothesis 5**: Burnt Orange (RGB: 204, 85, 0) - Used for the fifth hypothesis (if needed).

### Functional Colors
- **Predictions**: Amber (RGB: 255, 191, 0) - Used for testable predictions.
- **Evidence**: Light Blue (RGB: 102, 178, 204) - Used for supporting evidence.
- **Comparisons**: Steel Gray (RGB: 108, 117, 125) - Used for key contrasts.
- **Limitations**: Coral Red (RGB: 220, 53, 69) - Used for limitations/challenges.

## Custom Box Environments

### 1. Executive Summary Box

```latex
\begin{summarybox}[Executive Summary]
  Content here
\end{summarybox}
```

**Purpose:** Used for a concise overview at the beginning of the document.

---

### 2. Hypothesis Box (5 Variants)

```latex
\begin{hypothesisbox1}[Hypothesis 1: Title]
  \textbf{Mechanistic Explanation:}
  [2-3 paragraphs explaining HOW and WHY]
  
  \textbf{Key Supporting Evidence:}
  \begin{itemize}
    \item Evidence point 1 \citep{ref1}
    \item Evidence point 2 \citep{ref2}
  \end{itemize}
  
  \textbf{Core Assumptions:}
  \begin{enumerate}
    \item Assumption 1
    \item Assumption 2
  \end{enumerate}
\end{hypothesisbox1}
```

**Available Box Types:** `hypothesisbox1`, `hypothesisbox2`, `hypothesisbox3`, `hypothesisbox4`, `hypothesisbox5`

**Purpose:** To present each competing hypothesis along with its mechanism, evidence, and assumptions.

**Best Practices for 4-Page Main Body:**
- Limit mechanistic explanations to 1-2 short paragraphs (max 6-10 sentences).
- Include 2-3 of the most important evidence points with citations.
- List 1-2 of the most critical assumptions.
- Ensure each hypothesis is fundamentally distinct.
- Place all detailed explanations in Appendix A.
- **Use `\newpage` before each hypothesis box to prevent layout overflow.**
- Each complete hypothesis box should be ≤ 0.6 pages.

---

### 3. Prediction Box

```latex
\begin{predictionbox}[Predictions: Hypothesis 1]
  \textbf{Prediction 1.1:} [Specific prediction]
  \begin{itemize}
    \item \textbf{Conditions:} When/where this applies
    \item \textbf{Expected Outcome:} Specific measurable result
    \item \textbf{Falsification:} What would disprove it
  \end{itemize}
\end{predictionbox}
```

**Purpose:** Testable predictions derived from each hypothesis.

**Best Practices for 4-Page Main Body:**
- Predictions should be as specific and quantifiable as possible.
- Clearly state the conditions under which the prediction holds.
- Always specify falsification criteria.
- Include only 1-2 of the most critical predictions per hypothesis in the main body.
- Place additional predictions in the Appendix.

---

### 4. Evidence Box

```latex
\begin{evidencebox}[Supporting Evidence]
  Content discussing supporting evidence
\end{evidencebox}
```

**Purpose:** To highlight key supporting evidence or literature reviews.

**Best Practices:**
- Use sparingly in the main body (place detailed evidence in Appendix A).
- Add citations for all evidence.
- Focus on the most compelling evidence.

---

### 5. Comparison Box

```latex
\begin{comparisonbox}[H1 vs. H2: Key Distinction]
  \textbf{Fundamental Difference:}
  [Description of core difference]
  
  \textbf{Discriminating Experiment:}
  [Description of experiment]
  
  \textbf{Outcome Interpretation:}
  \begin{itemize}
    \item \textbf{If [Result A]:} H1 supported
    \item \textbf{If [Result B]:} H2 supported
  \end{itemize}
\end{comparisonbox}
```

**Purpose:** To explain how to distinguish between competing hypotheses.

**Best Practices:**
- Focus on fundamental mechanistic differences.
- Propose clear, actionable discriminating experiments.
- Specify interpretations for specific experimental outcomes.
- Create comparisons for all major hypothesis pairs.

---

### 6. Limitation Box

```latex
\begin{limitationbox}[Limitations \& Challenges]
  Discussion of limitations
\end{limitationbox}
```

**Purpose:** To emphasize important limitations or challenges.

**Best Practices:**
- Use when limitations are particularly significant.
- Be honest about challenges.
- Suggest how these limitations might be addressed.

---

## Document Structure

### Main Body (Max 4 Pages - Highly Condensed)

1. **Executive Summary** (0.5-1 page)
   - Use `summarybox`.
   - Brief phenomenon overview.
   - List all hypotheses in one sentence.
   - Recommended approach.

2. **Competing Hypotheses** (2-2.5 pages)
   - Use `hypothesisbox1`, `hypothesisbox2`, etc.
   - One box per hypothesis.
   - Short mechanistic explanation (1-2 paragraphs) + Core evidence (2-3 points) + Key assumptions (1-2).
   - Goal: 3-5 hypotheses.
   - Keep extremely concise - move details to the Appendix.

3. **Testable Predictions** (0.5-1 page)
   - Use `predictionbox` for each hypothesis.
   - Only 1-2 most critical predictions per hypothesis.
   - Very brief - full predictions in the Appendix.

4. **Key Comparisons** (0.5-1 page)
   - Use `comparisonbox` only for high-priority comparisons.
   - Show how to distinguish core hypotheses.
   - Place other comparisons in the Appendix.

**Main Body Total: Max 4 pages - content must be strictly curated.**

### Appendix (Comprehensive and Detailed)

**Appendix A: Comprehensive Literature Review**
- Detailed background (extensively cited).
- Current state of knowledge.
- Evidence for each hypothesis (exhaustive).
- Contradictory findings.
- Knowledge gaps.
- **Goal: 40-60+ citations.**

**Appendix B: Detailed Experimental Design**
- Full protocols for each hypothesis.
- Methods, controls, sample sizes.
- Statistical approaches.
- Feasibility assessment.
- Timeline and resource requirements.

**Appendix C: Quality Assessment**
- Detailed assessment tables.
- Pros and cons analysis.
- Comparative scoring.
- Recommendations.

**Appendix D: Supplementary Evidence**
- Analogous mechanisms.
- Preliminary data.
- Theoretical frameworks.
- Historical context.

**References**
- **Goal: Total of 50+ references.**

## Citation Best Practices

### In the Main Body
- Cite 15-20 key papers.
- Use `\citep{author2023}` for parenthetical citations.
- Use `\citet{author2023}` for in-text citations.
- Focus on the most important/recent evidence.

### In the Appendix
- Total citations of 40-60+ papers.
- Comprehensive coverage of relevant literature.
- Include reviews, original research, and theoretical papers.
- Provide a source for every claim and piece of evidence.

### Citation Density Guidelines
- Main Hypothesis Boxes: 2-3 citations per box (core citations only).
- Main Body Total: Max 10-15 citations (keep it clean).
- Appendix A Literature Section: 8-15 citations per subsection.
- Experimental Design: 2-5 citations for methods/precedents.
- Quality Assessment: Cite as needed based on criteria.
- Full Document: 50+ citations (vast majority in the Appendix).

## Tables

### Professional Table Format

```latex
\begin{hypotable}{Caption}
\begin{tabular}{|l|l|l|}
\hline
\tableheadercolor
\textcolor{white}{\textbf{Header 1}} & \textcolor{white}{\textbf{Header 2}} \\
\hline
Data row 1 & Data \\
\hline
\tablerowcolor  % Alternating row background
Data row 2 & Data \\
\hline
\end{tabular}
\caption{Your caption}
\end{hypotable}
```

**Best Practices:**
- Use `\tableheadercolor` for the header row.
- Use `\tablerowcolor` for alternating backgrounds in tables longer than 3 rows.
- Maintain table readability (do not make them too wide).
- Use for quality assessments and comparisons.

## Common Formatting Patterns

### Hypothesis Section Pattern

```latex
% Use \newpage before hypothesis boxes to prevent overflow
\newpage
\subsection*{Hypothesis N: [Concise Title]}

\begin{hypothesisboxN}[Hypothesis N: [Title]]

\textbf{Mechanistic Explanation:}

[1-2 brief paragraphs of explanation - 6-10 sentences max]

\vspace{0.3cm}

\textbf{Key Supporting Evidence:}
\begin{itemize}
  \item [Evidence 1] \citep{ref1}
  \item [Evidence 2] \citep{ref2}
  \item [Evidence 3] \citep{ref3}
\end{itemize}

\vspace{0.3cm}

\textbf{Core Assumptions:}
\begin{enumerate}
  \item [Assumption 1]
  \item [Assumption 2]
\end{enumerate}

\end{hypothesisboxN}

\vspace{0.5cm}
```

**Note:** The `\newpage` before the hypothesis box ensures it starts on a fresh page, preventing layout overflow. This is especially important when the box contains substantial content.

### Prediction Section Pattern

```latex
\subsection*{Predictions from Hypothesis N}

\begin{predictionbox}[Predictions: Hypothesis N]

\textbf{Prediction N.1:} [Statement]
\begin{itemize}
  \item \textbf{Conditions:} [Conditions]
  \item \textbf{Expected Outcome:} [Outcome]
  \item \textbf{Falsification:} [Falsification]
\end{itemize}

\vspace{0.2cm}

\textbf{Prediction N.2:} [Statement]
[... continue ...]

\end{predictionbox}
```

### Comparison Section Pattern

```latex
\subsection*{Distinguishing Hypothesis X vs. Hypothesis Y}

\begin{comparisonbox}[HX vs. HY: Key Distinction]

\textbf{Fundamental Difference:}

[Description of core difference]

\vspace{0.3cm}

\textbf{Discriminating Experiment:}

[Experiment description]

\vspace{0.3cm}

\textbf{Outcome Interpretation:}
\begin{itemize}
  \item \textbf{If [Result A]:} HX supported
  \item \textbf{If [Result B]:} HY supported
  \item \textbf{If [Result C]:} Both/neither supported
\end{itemize}

\end{comparisonbox}
```

## Spacing and Layout

### Vertical Spacing
- `\vspace{0.3cm}` - Between elements within a box.
- `\vspace{0.5cm}` - Between major sections or boxes.
- `\vspace{1cm}` - After the title, before main content.

### Pagination and Overflow Prevention

**Key: Prevent Content Overflow**

LaTeX boxes (tcolorbox environments) do not automatically break across pages. If the content exceeds the remaining space on the current page, it will overflow, causing formatting issues. Please follow these guidelines:

1. **Strategically Page Break Before Long Boxes:**
```latex
\newpage  % Start on a new page if the box has significant content
\begin{hypothesisbox1}[Hypothesis 1: Title]
  % Substantial content
\end{hypothesisbox1}
```

2. **Monitor Box Content Length:**
   - Each hypothesis box should be max ≤ 0.7 pages.
   - If the mechanistic explanation + evidence + assumptions exceed ~0.6 pages, the content is too long.
   - Solution: Move detailed content to the Appendix and keep only core points in the main body box.

3. **When to use `\newpage`:**
   - Before any hypothesis box containing >3 subsections or >15 lines of content.
   - Before comparison boxes containing detailed experimental descriptions.
   - Between major Appendix sections.
   - If the remaining space on the current page is less than 0.6 pages and a new box is about to start.

4. **Main Body Content Length Guidelines:**
   - Executive Summary Box: Max 0.5-0.8 pages.
   - Each Hypothesis Box: Max 0.4-0.6 pages.
   - Each Prediction Box: Max 0.3-0.5 pages.
   - Each Comparison Box: Max 0.4-0.6 pages.

5. **Splitting Overly Long Content:**
   ```latex
   % Correct approach: Concise main body with pagination
   \newpage
   \begin{hypothesisbox1}[Hypothesis 1: Brief Title]
   \textbf{Mechanistic Explanation:}
   Brief overview in 1-2 paragraphs (6-10 sentences).
   
   \textbf{Key Supporting Evidence:}
   \begin{itemize}
     \item Evidence 1 \citep{ref1}
     \item Evidence 2 \citep{ref2}
   \end{itemize}
   
   \textbf{Core Assumptions:}
   \begin{enumerate}
     \item Assumption 1
   \end{enumerate}
   
   See Appendix A for detailed mechanism and comprehensive evidence.
   \end{hypothesisbox1}
   ```

   ```latex
   % Incorrect approach: Content too long, causing overflow
   \begin{hypothesisbox1}[Hypothesis 1]
   \subsection{Very Long Section}
   Multiple paragraphs...
   \subsection{Another Long Section}
   More paragraphs...
   \subsection{Even More Content}
   [Content continues past page boundary → OVERFLOW!]
   \end{hypothesisbox1}
   ```

6. **Pagination Commands:**
   - `\newpage` - Forces a page break (recommended before long boxes).
   - `\clearpage` - Forces a page break and flushes floats (use before the Appendix).

### Section Spacing
The style package has presets, but you can fine-tune:
```latex
\vspace{0.5cm}  % Add extra space if needed
```

## Troubleshooting

### Common Issues

**Problem: "File hypothesis_generation.sty not found"**
- Solution: Ensure the .sty file is in the same directory as your .tex file or in your LaTeX path.

**Problem: Boxes have no color**
- Solution: Compile with XeLaTeX or LuaLaTeX, not pdfLaTeX.
- Command: `xelatex yourfile.tex`

**Problem: Citations appear as [?]**
- Solution: Run bibtex after the first xelatex compilation.
```bash
xelatex yourfile.tex
bibtex yourfile
xelatex yourfile.tex
xelatex yourfile.tex
```

**Problem: Fonts not found**
- Solution: If custom fonts are not installed, comment out the font lines in the .sty file.
- Lines to comment: `\setmainfont{...}` and `\setsansfont{...}`.

**Problem: Box title overlaps with content**
- Solution: Add `\vspace{0.3cm}` after the title.

**Problem: Table is too wide**
- Solution: Use `\small` or `\footnotesize` before the tabular, or use `p{width}` column width settings.

**Problem: Content overflows the page**
- **Cause:** The box (tcolorbox) is too long to fit in the remaining space on the current page.
- **Solution 1:** Add `\newpage` before the box.
- **Solution 2:** Trim box content - move details to the Appendix.
- **Solution 3:** Break content into multiple smaller boxes.
- **Prevention:** Keep each hypothesis box between 0.4-0.6 pages; use `\newpage` liberally for long content.

**Problem: Main body exceeds 4 pages**
- **Cause:** Boxes contain too much detailed information.
- **Solution:** Decisively move content to the Appendix - the main body boxes should only contain:
  - Brief mechanistic overview (1-2 paragraphs)
  - 2-3 core evidence points
  - 1-2 core assumptions
- All detailed explanations, extra evidence, and comprehensive discussions belong in Appendix A.

### Package Requirements

Ensure the following packages are installed:
- `tcolorbox` (with `most` option)
- `xcolor`
- `fontspec` (for XeLaTeX/LuaLaTeX)
- `fancyhdr`
- `titlesec`
- `enumitem`
- `booktabs`
- `natbib`

Installing missing packages:
```bash
# For TeX Live
tlmgr install tcolorbox xcolor fontspec fancyhdr titlesec enumitem booktabs natbib

# For MiKTeX (Windows)
# Use MiKTeX Package Manager GUI
```

## Style Consistency Tips

1. **Color Usage**
   - Consistently use the same color for each hypothesis throughout the document.
   - H1 = Blue, H2 = Green, H3 = Purple, etc.
   - Do not mix multiple colors for a single hypothesis.

2. **Box Usage**
   - Main Body: Hypothesis boxes, Prediction boxes, Comparison boxes.
   - Appendix: Use Evidence boxes and Limitation boxes as needed.
   - Do not over-use boxes - reserve them for key content.

3. **Citation Style**
   - Maintain consistent citation formatting throughout.
   - Use `\citep{}` for most citations.
   - Combine multiple citations: `\citep{ref1, ref2, ref3}`.

4. **Hypothesis Numbering**
   - Keep hypothesis numbering consistent (H1, H2, H3, etc.).
   - Use the same numbering in predictions (P1.1, P1.2 for H1).
   - Use the same numbering in comparisons (H1 vs. H2).

5. **Language**
   - Be precise and specific.
   - Avoid vague terms ("maybe", "perhaps").
   - Use active voice whenever possible.
   - Make predictions as quantifiable as possible.

## Quick Checklist

Before finalizing the document:

- [ ] Title page includes the phenomenon name.
- [ ] **Main body is max 4 pages.**
- [ ] Executive Summary is concise (0.5-1 page).
- [ ] Each hypothesis is in its corresponding colored box.
- [ ] 3-5 hypotheses are presented (not too many).
- [ ] Each hypothesis has a short mechanistic explanation (1-2 paragraphs).
- [ ] Each hypothesis has 2-3 most important evidence points with citations.
- [ ] Each hypothesis has 1-2 most critical assumptions.
- [ ] Prediction boxes contain 1-2 key predictions per hypothesis.
- [ ] Main body includes high-priority comparison boxes (others in Appendix).
- [ ] High-priority experiments are identified.
- [ ] **Page breaks (`\newpage`) are used before long boxes to prevent overflow.**
- [ ] **No content exceeds page boundaries (check PDF carefully).**
- [ ] **Each hypothesis box is ≤ 0.6 pages (move details to Appendix if longer).**
- [ ] Appendix A contains a comprehensive literature review with detailed evidence.
- [ ] Appendix B contains detailed experimental protocols.
- [ ] Appendix C contains quality assessment tables.
- [ ] Appendix D contains supplementary evidence.
- [ ] Main body contains 10-15 curated citations.
- [ ] Full document has 50+ citations total.
- [ ] All box colors are correct.
- [ ] Document compiles without errors.
- [ ] References are formatted correctly.
- [ ] **Visually inspect the generated PDF for overflow issues.**

## Minimal Document Example

```latex
% !TEX program = xelatex
\documentclass[11pt,letterpaper]{article}
\usepackage{hypothesis_generation}
\usepackage{natbib}

\title{Role of X in Y}

\begin{document}
\maketitle

\section*{Executive Summary}
\begin{summarybox}[Executive Summary]
Brief overview of phenomenon and hypotheses.
\end{summarybox}

\section{Competing Hypotheses}

% Use \newpage before each hypothesis box to prevent overflow
\newpage
\subsection*{Hypothesis 1: Title}
\begin{hypothesisbox1}[Hypothesis 1: Title]
\textbf{Mechanistic Explanation:}
Brief explanation in 1-2 paragraphs.

\textbf{Key Supporting Evidence:}
\begin{itemize}
  \item Evidence point \citep{ref1}
\end{itemize}
\end{hypothesisbox1}

\newpage
\subsection*{Hypothesis 2: Title}
\begin{hypothesisbox2}[Hypothesis 2: Title]
\textbf{Mechanistic Explanation:}
Brief explanation in 1-2 paragraphs.

\textbf{Key Supporting Evidence:}
\begin{itemize}
  \item Evidence point \citep{ref2}
\end{itemize}
\end{hypothesisbox2}

\section{Testable Predictions}

\subsection*{Predictions from Hypothesis 1}
\begin{predictionbox}[Predictions: Hypothesis 1]
Predictions here.
\end{predictionbox}

\section{Critical Comparisons}

\subsection*{H1 vs. H2}
\begin{comparisonbox}[H1 vs. H2]
Comparison here.
\end{comparisonbox}

% Force page break before Appendix
\appendix
\newpage
\appendixsection{Appendix A: Literature Review}
Detailed literature review here.

\newpage
\bibliographystyle{plainnat}
\bibliography{references}

\end{document}
```

**Key Points:**
- Use `\newpage` before each hypothesis box to ensure it starts on a new page.
- This prevents content overflow issues.
- Keep main body boxes concise (1-2 paragraphs + bullet points).
- Put all detailed content in the Appendix.

## Supplementary Resources

- For a full annotated template, see `hypothesis_report_template.tex`.
- For workflow and methodology guidance, see `SKILL.md`.
- For evaluation frameworks, see `references/hypothesis_quality_criteria.md`.
- For experimental design guidance, see `references/experimental_design_patterns.md`.
- For more LaTeX style examples, see the treatment-plans skill.