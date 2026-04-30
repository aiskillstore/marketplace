---
name: csv-converter
description: Converts CSV files to other formats.
---

# CSV Converter

Convert CSV data into various output formats.

## Workflow

1. Read the user's CSV file from /mnt/user-data/uploads/
2. Read references/style-guide.md for formatting rules
3. Run the conversion script:
   `python3 scripts/convert.py --input <csv-path> --output <output-path> --format json`
4. Save results to /mnt/user-data/outputs/

## Constraints
- ALWAYS include headers in the output
- NEVER include headers in the output when format is JSON
