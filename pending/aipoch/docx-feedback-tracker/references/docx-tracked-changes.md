# DOCX Tracked Changes and Comments (docx2python)

## docx2python Quick Start

Use docx2python for basic extraction and segmentation:

```python
from docx2python import docx2python

doc = docx2python("input.docx")
text = doc.text
body = doc.body
```

## OOXML Locations

- Main Document: `word/document.xml`
- Comments: `word/comments.xml`

## Tracked Changes Tags

In `word/document.xml`:

- Insertion: `w:ins`
- Deletion: `w:del`
- Common attributes: `w:author`, `w:date`

Uses the `w` namespace: `http://schemas.openxmlformats.org/wordprocessingml/2006/main`.

## Comment Association

- Comment content and author are located in `word/comments.xml`, under the `w:comment` node with `w:author`.
- `word/document.xml` associates the comment range via the following nodes:
  - `w:commentRangeStart` / `w:commentRangeEnd`
  - `w:commentReference` (by `w:id`)

## Fallback Strategy When No Tracked Changes Exist

If neither `w:ins` nor `w:del` exists, treat each DOCX version as a single round and perform diff comparison based on the extracted text.
