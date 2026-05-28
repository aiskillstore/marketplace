# Examples

## Example 1: Import PDFs and add manual tags

Command:

```
python scripts/import_library.py --source-dir "D:\Downloads\papers" --library-dir "D:\LiteratureLibrary" --tag "cancer" --tag "imaging"
```

Expected:
- Files copied into `D:\LiteratureLibrary\files\<Year>\<Journal>`
- `D:\LiteratureLibrary\index.jsonl` appended with new records
- Summary JSON printed

## Example 2: Move files and scan subdirectories

```
python scripts/import_library.py --source-dir "D:\Downloads\papers" --library-dir "D:\LiteratureLibrary" --move --recursive
```

## Example 3: Import metadata-only files

```
python scripts/import_library.py --source-dir "D:\Downloads\exports" --library-dir "D:\LiteratureLibrary"
```

Note:
- `.bib`, `.ris`, `.csv`, `.txt` entries are added to `index.jsonl`.
- Only `.pdf` files are copied or moved.
