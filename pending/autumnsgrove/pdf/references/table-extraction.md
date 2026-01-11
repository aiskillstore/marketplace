# Table Extraction Reference

## Basic Table Extraction (pdfplumber)

```python
import pdfplumber
import pandas as pd

def extract_tables(pdf_path):
    """Extract all tables from a PDF."""
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            for table_num, table in enumerate(tables, start=1):
                # Convert to DataFrame
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append({
                        'page': page_num,
                        'table': table_num,
                        'data': df
                    })

    return all_tables

# Usage
tables = extract_tables("report.pdf")
for t in tables:
    print(f"Page {t['page']}, Table {t['table']}:")
    print(t['data'])
    print("\n")
```

## Advanced Table Extraction with Settings

```python
import pdfplumber

def extract_tables_advanced(pdf_path):
    """Extract tables with custom settings for better accuracy."""
    tables = []

    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "explicit_vertical_lines": [],
        "explicit_horizontal_lines": [],
        "snap_tolerance": 3,
        "join_tolerance": 3,
        "edge_min_length": 3,
        "min_words_vertical": 3,
        "min_words_horizontal": 1,
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables(table_settings=table_settings)
            tables.extend(page_tables)

    return tables
```

## Find and Extract Specific Tables

```python
import pdfplumber
import pandas as pd

def find_table_with_keyword(pdf_path, keyword):
    """Find and extract tables containing a specific keyword."""
    matching_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            for table in tables:
                # Check if keyword exists in table
                table_text = str(table).lower()
                if keyword.lower() in table_text:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    matching_tables.append({
                        'page': page_num,
                        'data': df
                    })

    return matching_tables

# Usage
sales_tables = find_table_with_keyword("report.pdf", "revenue")
```

## Table Extraction with Multiple Strategies

```python
import pdfplumber

def extract_tables_robust(pdf_path):
    """Extract tables with multiple strategies."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]

        # Try different strategies
        strategies = [
            {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
            {"vertical_strategy": "text", "horizontal_strategy": "text"},
            {"vertical_strategy": "lines", "horizontal_strategy": "text"}
        ]

        for strategy in strategies:
            tables = page.extract_tables(table_settings=strategy)
            if tables:
                return tables

        return []
```

## Export Tables to CSV

```python
import pdfplumber
import pandas as pd
import os

def extract_tables_to_csv(pdf_path, output_dir):
    """Extract tables and save each as CSV."""
    os.makedirs(output_dir, exist_ok=True)

    with pdfplumber.open(pdf_path) as pdf:
        table_count = 0

        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            for table_num, table in enumerate(tables, start=1):
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    csv_path = os.path.join(
                        output_dir,
                        f"page{page_num}_table{table_num}.csv"
                    )
                    df.to_csv(csv_path, index=False)
                    table_count += 1

        print(f"Extracted {table_count} tables to {output_dir}")

# Usage
extract_tables_to_csv("report.pdf", "extracted_tables/")
```

## Table Extraction with Validation

```python
import pdfplumber
import pandas as pd

def extract_validated_tables(pdf_path, min_rows=2, min_cols=2):
    """Extract tables with validation criteria."""
    valid_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue

                # Validate table dimensions
                rows = len(table)
                cols = len(table[0]) if table else 0

                if rows >= min_rows and cols >= min_cols:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    valid_tables.append({
                        'page': page_num,
                        'rows': rows,
                        'cols': cols,
                        'data': df
                    })

    return valid_tables

# Usage
tables = extract_validated_tables("report.pdf", min_rows=3, min_cols=3)
```

## Clean and Format Extracted Tables

```python
import pdfplumber
import pandas as pd

def extract_clean_tables(pdf_path):
    """Extract and clean tables for analysis."""
    clean_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue

                # Convert to DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])

                # Clean data
                # Remove empty columns
                df = df.dropna(axis=1, how='all')

                # Remove empty rows
                df = df.dropna(axis=0, how='all')

                # Strip whitespace
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

                clean_tables.append(df)

    return clean_tables
```
