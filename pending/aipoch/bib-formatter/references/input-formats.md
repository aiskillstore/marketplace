# Input Formats and Field Mapping

## RIS

Common fields:

- `AU` Author
- `TI` Title
- `JO`/`JA` Journal Name
- `PY`/`Y1` Year
- `VL` Volume
- `IS` Issue
- `SP`/`EP` Start/End Pages
- `DO` DOI
- `UR` URL

The script maps RIS to CSL-JSON's `author/title/container-title/issued/volume/issue/page/DOI/URL`.

## BibTeX

Common fields:

- `author`
- `title`
- `journal` or `booktitle`
- `year`
- `volume`
- `number`
- `pages`
- `doi`
- `url`

The author field supports both `Last, First` and `First Last` formats; if parsing fails, it will be preserved in `literal` form.

## Plain Text List

- Each line is treated as a single reference.
- Only minimal entries can be generated (usually only the title/original text is kept), and formatting results may be limited.
- It is recommended to prioritize using RIS/BibTeX/CSL-JSON to obtain full formatting.

## CSL-JSON

- Used directly as input for citeproc-py.
- Each record must contain an `id` field.