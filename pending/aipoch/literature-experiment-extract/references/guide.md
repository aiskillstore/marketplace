# Extraction and Organization of Key Points

## Target Scope

- Extract only the experimental models, experimental methods, and biomarkers **explicitly stated** in the paper.
- Do not infer or supplement; for missing information, write "Not reported."

## Evidence Annotation Standards

- Each record must include a **page number and a short excerpt**.
- Excerpts must be **complete original sentences**, prioritizing short sentences containing entities and actions, and avoiding copying entire paragraphs.
- Page number format should be unified as `Page XX` (consistent with the input Markdown).

## Entity Recognition Checklist

### Experimental Models

- Cells: Cell lines, primary cells, organoids, source species/tissues.
- Animals: Species, strain, sex, age/weight, genetic background, disease model, treatment.
- Conditions: Infection/induction methods, dosage, time points, grouping.

### Methods and Assays

- Molecular: qPCR, WB, RNA-seq, ELISA, ChIP, reporter genes, etc.
- Cellular: Proliferation, apoptosis, migration, colony formation, etc.
- Histology/Imaging: IHC, IF, H&E, types of microscopic imaging.
- In vivo: Survival curves, behavioral assays, physiological index measurements.

### Biomarkers

- Genes, proteins, cytokines, pathways, metabolites, etc.
- Specific measurement types: Expression, activity, phosphorylation, secretion, etc.

## Deduplication and Merging

- When the same entity appears in multiple places, merge them into one record and retain multiple pieces of evidence.
- If different conditions/groupings lead to different meanings, split them into multiple records.

## Output Consistency

- Table headers and fields are fixed; content should be as concise as possible.
- Except for the "Evidence" column, other fields use Chinese by default (retain proper nouns/abbreviations when necessary).
- The evidence column should contain "Excerpt + Page XX".

## Output Format and Encoding

- Directly output 1 Markdown summary and 3 CSVs:
  - `outputs/{Paper Abbreviation}-experiment-summary.md`
  - `outputs/{Paper Abbreviation}-models.csv`
  - `outputs/{Paper Abbreviation}-methods.csv`
  - `outputs/{Paper Abbreviation}-biomarkers.csv`
- CSV header requirements:
  - Model table: `Model Type, Details, Evidence`
  - Method table: `Method Category, Specific Method, Evidence`
  - Biomarker table: `Biomarker, Measurement Type/Context, Evidence`
- All final outputs must use UTF-8 encoding to avoid garbled characters.
- Before writing any Markdown or CSV, UTF-8 encoding processing must be performed before outputting the file.

## Language Requirements
- Output content should be in Chinese by default (or the user-requested language if specified).
- Evidence excerpts must stay in the original language of the source literature.