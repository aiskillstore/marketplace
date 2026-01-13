#!/usr/bin/env python3
"""
Export validated data to various analysis formats.
Supports Python (pandas/SQLite), R (RDS/CSV), Excel, and more.
"""

import argparse
import json
import csv
from pathlib import Path
from typing import Dict, List, Any
import sys


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Export validated data to analysis format'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input JSON file with validated data from step 05'
    )
    parser.add_argument(
        '--format',
        choices=['python', 'r', 'csv', 'json', 'excel', 'sqlite'],
        required=True,
        help='Output format'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output file path (without extension for some formats)'
    )
    parser.add_argument(
        '--flatten',
        action='store_true',
        help='Flatten nested JSON structures for tabular formats'
    )
    parser.add_argument(
        '--include-metadata',
        action='store_true',
        help='Include original paper metadata in output'
    )
    return parser.parse_args()


def load_results(input_path: Path) -> Dict:
    """Load validated results from JSON file"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """
    Flatten nested dictionary structure.
    Useful for converting JSON to tabular format.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to comma-separated strings
            if v and isinstance(v[0], dict):
                # List of dicts - create numbered columns
                for i, item in enumerate(v):
                    items.extend(flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
            else:
                # Simple list
                items.append((new_key, ', '.join(str(x) for x in v)))
        else:
            items.append((new_key, v))
    return dict(items)


def extract_records(results: Dict, flatten: bool = False, include_metadata: bool = False) -> List[Dict]:
    """
    Extract records from results structure.
    Returns a list of dictionaries suitable for tabular export.
    """
    records = []

    for paper_id, result in results.items():
        if result.get('status') != 'success':
            continue

        # Get the validated data (or fall back to extracted data)
        data = result.get('validated_data', result.get('extracted_data', {}))

        if not data:
            continue

        # Check if data contains nested records or is a single record
        if 'records' in data and isinstance(data['records'], list):
            # Multiple records per paper
            for record in data['records']:
                record_dict = record.copy() if isinstance(record, dict) else {'value': record}

                # Add paper-level fields
                if include_metadata:
                    record_dict['paper_id'] = paper_id
                    for key in data:
                        if key != 'records':
                            record_dict[f'paper_{key}'] = data[key]

                if flatten:
                    record_dict = flatten_dict(record_dict)

                records.append(record_dict)
        else:
            # Single record per paper
            record_dict = data.copy()
            if include_metadata:
                record_dict['paper_id'] = paper_id

            if flatten:
                record_dict = flatten_dict(record_dict)

            records.append(record_dict)

    return records


def export_to_csv(records: List[Dict], output_path: Path):
    """Export to CSV format"""
    if not records:
        print("No records to export")
        return

    # Get all possible field names
    fieldnames = set()
    for record in records:
        fieldnames.update(record.keys())
    fieldnames = sorted(fieldnames)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Exported {len(records)} records to CSV: {output_path}")


def export_to_json(records: List[Dict], output_path: Path):
    """Export to JSON format"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(records)} records to JSON: {output_path}")


def export_to_python(records: List[Dict], output_path: Path):
    """Export to Python format (pandas DataFrame pickle)"""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required for Python export. Install with: pip install pandas")
        sys.exit(1)

    df = pd.DataFrame(records)

    # Save as pickle
    pickle_path = output_path.with_suffix('.pkl')
    df.to_pickle(pickle_path)
    print(f"Exported {len(records)} records to pandas pickle: {pickle_path}")

    # Also create a Python script to load it
    script_path = output_path.with_suffix('.py')
    script_content = f'''#!/usr/bin/env python3
"""
Data loading script
Generated by extract_from_pdfs skill
"""

import pandas as pd

# Load the data
df = pd.read_pickle('{pickle_path.name}')

print(f"Loaded {{len(df)}} records")
print(f"Columns: {{list(df.columns)}}")
print("\\nFirst few rows:")
print(df.head())

# Example analyses:
# df.describe()
# df.groupby('some_column').size()
# df.to_csv('output.csv', index=False)
'''

    with open(script_path, 'w') as f:
        f.write(script_content)

    print(f"Created loading script: {script_path}")


def export_to_r(records: List[Dict], output_path: Path):
    """Export to R format (RDS file)"""
    try:
        import pandas as pd
        import pyreadr
    except ImportError:
        print("Error: pandas and pyreadr are required for R export.")
        print("Install with: pip install pandas pyreadr")
        sys.exit(1)

    df = pd.DataFrame(records)

    # Save as RDS
    rds_path = output_path.with_suffix('.rds')
    pyreadr.write_rds(rds_path, df)
    print(f"Exported {len(records)} records to RDS: {rds_path}")

    # Also create an R script to load it
    script_path = output_path.with_suffix('.R')
    script_content = f'''# Data loading script
# Generated by extract_from_pdfs skill

# Load the data
data <- readRDS('{rds_path.name}')

cat(sprintf("Loaded %d records\\n", nrow(data)))
cat(sprintf("Columns: %s\\n", paste(colnames(data), collapse=", ")))
cat("\\nFirst few rows:\\n")
print(head(data))

# Example analyses:
# summary(data)
# table(data$some_column)
# write.csv(data, 'output.csv', row.names=FALSE)
'''

    with open(script_path, 'w') as f:
        f.write(script_content)

    print(f"Created loading script: {script_path}")


def export_to_excel(records: List[Dict], output_path: Path):
    """Export to Excel format"""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required for Excel export. Install with: pip install pandas openpyxl")
        sys.exit(1)

    df = pd.DataFrame(records)

    # Save as Excel
    excel_path = output_path.with_suffix('.xlsx')
    df.to_excel(excel_path, index=False, engine='openpyxl')
    print(f"Exported {len(records)} records to Excel: {excel_path}")


def export_to_sqlite(records: List[Dict], output_path: Path):
    """Export to SQLite database"""
    try:
        import pandas as pd
        import sqlite3
    except ImportError:
        print("Error: pandas is required for SQLite export. Install with: pip install pandas")
        sys.exit(1)

    df = pd.DataFrame(records)

    # Create database
    db_path = output_path.with_suffix('.db')
    conn = sqlite3.connect(db_path)

    # Write to database
    table_name = 'extracted_data'
    df.to_sql(table_name, conn, if_exists='replace', index=False)

    conn.close()
    print(f"Exported {len(records)} records to SQLite database: {db_path}")
    print(f"Table name: {table_name}")

    # Create SQL script with example queries
    sql_script_path = output_path.with_suffix('.sql')
    sql_content = f'''-- Example SQL queries for {db_path.name}
-- Generated by extract_from_pdfs skill

-- View all records
SELECT * FROM {table_name} LIMIT 10;

-- Count total records
SELECT COUNT(*) as total_records FROM {table_name};

-- Example: Group by a column (adjust column name as needed)
-- SELECT column_name, COUNT(*) as count
-- FROM {table_name}
-- GROUP BY column_name
-- ORDER BY count DESC;
'''

    with open(sql_script_path, 'w') as f:
        f.write(sql_content)

    print(f"Created SQL example script: {sql_script_path}")


def main():
    args = parse_args()

    # Load validated results
    results = load_results(Path(args.input))
    print(f"Loaded {len(results)} results")

    # Extract records
    records = extract_records(
        results,
        flatten=args.flatten,
        include_metadata=args.include_metadata
    )
    print(f"Extracted {len(records)} records")

    if not records:
        print("No records to export. Check your data.")
        return

    # Export based on format
    output_path = Path(args.output)

    if args.format == 'csv':
        export_to_csv(records, output_path)
    elif args.format == 'json':
        export_to_json(records, output_path)
    elif args.format == 'python':
        export_to_python(records, output_path)
    elif args.format == 'r':
        export_to_r(records, output_path)
    elif args.format == 'excel':
        export_to_excel(records, output_path)
    elif args.format == 'sqlite':
        export_to_sqlite(records, output_path)

    print(f"\nExport complete!")
    print(f"Your data is ready for analysis in {args.format.upper()} format.")


if __name__ == '__main__':
    main()
