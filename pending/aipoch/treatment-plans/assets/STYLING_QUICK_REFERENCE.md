# Professional Treatment Plan Style Guide - Quick Reference

## File Location
`medical_treatment_plan.sty` - located in the assets directory

## Quick Start

```latex
% !TEX program = xelatex
\documentclass[11pt,letterpaper]{article}
\usepackage{medical_treatment_plan}
\usepackage{natbib}

\begin{document}
\maketitle
% Your content
\end{document}
```

## Custom Box Environments

### 1. Info Box (Blue) - General Information
```latex
\begin{infobox}[Title]
  Content
\end{infobox}
```
**Applicable to:** Clinical assessments, monitoring plans, titration protocols

### 2. Warning Box (Yellow/Red) - Critical Alerts
```latex
\begin{warningbox}[Title]
  Critical information
\end{warningbox}
```
**Applicable to:** Safety protocols, decision points, contraindications

### 3. Goal Box (Green) - Treatment Goals
```latex
\begin{goalbox}[Title]
  Goals and targets
\end{goalbox}
```
**Applicable to:** SMART goals, expected outcomes, success metrics

### 4. Key Point Box (Light Blue) - Highlights
```latex
\begin{keybox}[Title]
  Important highlights
\end{keybox}
```
**Applicable to:** Executive summaries, core conclusions, core recommendations

### 5. Emergency Box (Red) - Emergency Information
```latex
\begin{emergencybox}
  Emergency contacts
\end{emergencybox}
```
**Applicable to:** Emergency contacts, contingency plans

### 6. Patient Information Box (White/Blue) - Demographics
```latex
\begin{patientinfo}
  Patient information
\end{patientinfo}
```
**Applicable to:** Patient demographics and baseline data

## Professional Tables

```latex
\begin{medtable}{Caption}
\begin{tabular}{|l|l|l|}
\hline
\tableheadercolor
\textcolor{white}{\textbf{Header 1}} & \textcolor{white}{\textbf{Header 2}} \\
\hline
Data row 1 \\
\hline
\tablerowcolor  % Alternating gray rows
Data row 2 \\
\hline
\end{tabular}
\caption{Table caption}
\end{medtable}
```

## Color Scheme

- **Primary Blue** (0, 102, 153): Headers, titles
- **Secondary Blue** (102, 178, 204): Light backgrounds
- **Accent Blue** (0, 153, 204): Links, highlights
- **Success Green** (0, 153, 76): Goals
- **Warning Red** (204, 0, 0): Warnings

## Compilation

```bash
xelatex document.tex
bibtex document
xelatex document.tex
xelatex document.tex
```

## Best Practices

1. **Match box types to purpose:** Green for goals, red/yellow for warnings.
2. **Do not overuse boxes:** Reserve them for important information only.
3. **Maintain color consistency:** Strictly adhere to the defined color scheme.
4. **Utilize white space:** Add `\vspace{0.5cm}` between major sections.
5. **Alternating table rows:** Use `\tablerowcolor` to improve readability.

## Installation

**Option 1:** Copy `assets/medical_treatment_plan.sty` to your document directory.

**Option 2:** Install to the user TeX directory.
```bash
mkdir -p ~/texmf/tex/latex/medical_treatment_plan
cp assets/medical_treatment_plan.sty ~/texmf/tex/latex/medical_treatment_plan/
texhash ~/texmf
```

## Required Packages
The style file automatically loads all of the following packages:
- tcolorbox, tikz, xcolor
- fancyhdr, titlesec, enumitem
- booktabs, longtable, array, colortbl
- hyperref, natbib, fontspec

## Example Document Structure

```latex
\maketitle

\section*{Patient Information}
\begin{patientinfo}
  % Demographic information
  Demographics
\end{patientinfo}

\section{Executive Summary}
\begin{keybox}[Plan Overview]
  % Key highlights
  Key highlights
\end{keybox}

\section{Treatment Goals}
\begin{goalbox}[SMART Goals]
  % Goals list
  Goals list
\end{goalbox}

\section{Medication Plan}
\begin{infobox}[Dosing]
  % Instructions
  Instructions
\end{infobox}

\begin{warningbox}[Safety]
  % Warnings
  Warnings
\end{warningbox}

\section{Emergency}
\begin{emergencybox}
  % Contact information
  Contacts
\end{emergencybox}
```

## Troubleshooting

**Missing packages:**
```bash
sudo tlmgr install tcolorbox tikz pgf
```

**Special characters not displaying:**
- Use XeLaTeX instead of PDFLaTeX.
- Or use LaTeX commands: `$\checkmark$`, `$\geq$`.

**Header warnings:**
- Set to 22pt in the style file.
- Adjust as needed.

---

For the full documentation, please refer to the "Professional Document Styling" section in SKILL.md.