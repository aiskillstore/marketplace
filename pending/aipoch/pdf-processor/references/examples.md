# Examples

## Merge PDFs

```
python scripts/pdf_tool.py --operation merge --inputs "a.pdf" "b.pdf" --output "merged.pdf"
```

## Split PDF into pages

```
python scripts/pdf_tool.py --operation split --input "doc.pdf" --output-dir "out_pages"
```

## Extract page range

```
python scripts/pdf_tool.py --operation extract-pages --input "doc.pdf" --pages "2-4,7" --output "excerpt.pdf"
```

## Extract text

```
python scripts/pdf_tool.py --operation extract-text --input "doc.pdf" --pages "1-3" --output "text.txt"
```

## Extract tables

```
python scripts/pdf_tool.py --operation extract-tables --input "doc.pdf" --pages "1-2" --output-dir "tables"
```

## Create PDF from text

```
python scripts/pdf_tool.py --operation create --input "notes.txt" --output "notes.pdf"
```
