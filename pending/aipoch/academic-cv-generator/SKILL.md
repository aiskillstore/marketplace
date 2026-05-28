---
name: academic-cv-generator
description: Generate structured academic CVs from free-form Chinese/English text and export to Word (.docx). Use this skill when you are asked to organize, generate, or optimize an academic CV (e.g., publications/projects/awards) into a consistent, formatted document with uniform-colored section headers and optional bilingual output.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You receive a messy, free-form CV draft (Chinese or English) and need it reorganized into a standard academic structure.
- You are asked to compile and format **Publications** from raw citation strings without changing their original citation format.
- You need to extract and normalize **Education** and **Project Experience** entries, then sort them by degree level or time.
- You must generate a **Word (.docx)** academic CV that matches a predefined visual style (uniform header color, bold headers, bullet lists).
- The user requests a polished CV output file with a fixed naming convention: `Name-Academic-CV.docx`.

## Key Features

- Classifies free-form input into: Personal Information, Educational Background, Project Experience, Publications, Awards (optional), Skills.
- Normalizes content into a required intermediate **Markdown outline** before rendering.
- Omits the **Awards** section entirely when no awards are provided.
- Infers a minimal **Skills** section from project descriptions when explicit skills are missing.
- Renders a Word document aligned to the reference layout `output/ZhangWei-Academic-CV.docx`.
- Applies consistent styling rules: single-line section titles, larger than body text, bold, and one uniform header color.

## Dependencies

- Python 3.x
- `python-docx` (install via `pip install python-docx`)

## Example Usage

### 1) Prepare input (free-form text)

Create or use the provided example input file:

- `sample_input_standard.txt`

### 2) Generate the Word CV

```bash
python -m pip install python-docx
python scripts/render_cv.py --input sample_input_standard.txt --output output
```

### 3) Optional flags

```bash
python scripts/render_cv.py \
  --input sample_input_standard.txt \
  --output output \
  --lang en \
  --header-color random
```

Supported options:

- `--lang zh|en`
- `--header-color purple|cyan|green|red|random`

### 4) Expected output

- Output file: `Name-Academic-CV.docx` (saved under the `--output` directory)
- Reference sample: `sample_output.docx`

## Implementation Details

### 1) End-to-end workflow

1. Parse the input and classify content into:
   - Personal Information
   - Educational Background
   - Project Experience
   - Publications
   - Skills
   - Awards (optional)
2. Convert the classified result into the required Markdown layout (mandatory intermediate step).
3. If **Awards** is empty, omit the section from both Markdown and DOCX.
4. If **Skills** is empty, infer skills from project experience and output a minimal skills list.
5. Render the CV into Word using the same visual structure as `output/ZhangWei-Academic-CV.docx`.
6. Ensure section titles are single-line, bold, larger than body text, and share one uniform color.
7. Save as `Name-Academic-CV.docx`.

### 2) Classification rules

- **Personal Information**: name, title, organization, email, phone.
- **Educational Background**: degree (PhD/Master/Bachelor), major, school, year; sort from highest to lowest degree.
- **Project Experience**: project name + time range + responsibilities/description; sort by time (most recent first).
- **Publications**: keep original citation strings exactly as provided (no reformatting).
- **Skills**: use explicit skills if present; otherwise infer from project content.

### 3) Required Markdown output format (intermediate representation)

The classified content must be normalized into the following Markdown outline:

```text
Personal Information
Name|Title|Organization|Email|Phone

Educational Background
Degree, Major, School, Year
Degree, Major, School, Year

Project Experience
Project Name (Project Period): Key responsibilities or work content
Project Name (Project Period): Key responsibilities or work content

Publications
Original citation entries (keep input format)
Original citation entries (keep input format)

Awards
Year, Award
Year, Award

Skills
Programming Languages: ...
Technical Fields: ...
Tools & Technologies: ...
```

Rules:

- If **Awards** is empty, omit the entire section.
- If **Skills** is empty, infer and output a minimal skills list (e.g., `Technical Fields: Blockchain / Machine Learning / Systems Development`).

### 4) Word rendering rules

- Do **not** print the “Personal Information” section title in the DOCX.
- Print the **name** as the first line in **bold**.
- Print the contact line as: `Title | Organization | Email | Phone`.
- Section titles (Educational Background / Project Experience / Publications / Awards / Skills):
  - bold
  - single-line
  - larger than body text
  - all use one uniform color chosen from: `purple`, `cyan`, `green`, `red` (or `random`)
- All items under each section are rendered as bullet points.

### 5) Output rules

- Output format must be **Word (.docx)**.
- Output filename must be: `Name-Academic-CV.docx`.
- Treat “Publications / Published Literature / Published Papers” as standalone publication sections.
- The final layout should match the reference: `output/ZhangWei-Academic-CV.docx`.