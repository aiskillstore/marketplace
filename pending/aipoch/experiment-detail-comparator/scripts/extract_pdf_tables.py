#!/usr/bin/env python3
"""
Extract tables from PDF files using pdfplumber library.
Supports multiple languages and complex table structures.
"""

import sys
import json
import subprocess
from pathlib import Path

def check_pdfplumber():
    """
    Check if pdfplumber is installed.
    
    Returns:
        True if installed, False otherwise
    """
    try:
        import pdfplumber
        return True
    except ImportError:
        print("pdfplumber not installed. Installing...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber"], check=True)
        print("Please run the script again after installation.", file=sys.stderr)
        return False

def extract_tables_from_pdf(pdf_path, output_path):
    """
    Extract all tables from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        output_path: Path to save extracted tables
    
    Returns:
        List of extracted tables
    """
    try:
        import pdfplumber
    except ImportError:
        print("Error: pdfplumber is not installed. Run: pip install pdfplumber", file=sys.stderr)
        return []
    
    tables_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages
        for i, page in enumerate(pages, 1):
            tables = page.extract_tables()
            
            for j, table in enumerate(tables, 1):
                if table:
                    # Convert table to list of lists (rows)
                    table_data = []
                    headers = table[0] if len(table) > 0 else []
                    rows = table[1:] if len(table) > 1 else []
                    
                    table_obj = {
                        "page_number": i,
                        "table_number": j,
                        "headers": headers,
                        "rows": [[str(cell) if cell else "" for cell in row] for row in rows],
                        "extraction_method": "pdfplumber",
                    }
                    
                    # Try to identify table type based on content
                    if headers:
                        table_obj["table_type"] = identify_table_type(headers)
                    else:
                        table_obj["table_type"] = "unknown"
                    
                    tables_data.append(table_obj)
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tables_data, f, indent=2, ensure_ascii=False)
    
    return tables_data

def identify_table_type(headers):
    """
    Try to identify the type of table based on headers.
    
    Args:
        headers: List of table headers
    
    Returns:
        Table type string
    """
    if not headers:
        return "data_table"
    
    header_text = " ".join(str(h) for h in headers if h).lower()
    
    # Check for material table
    material_keywords = ["reagent", "chemical", "compound", "supplier", "catalog", "lot", "batch"]
    if any(kw in header_text for kw in material_keywords):
        return "materials_table"
    
    # Check for parameter table
    param_keywords = ["parameter", "value", "unit", "condition", "concentration"]
    if any(kw in header_text for kw in param_keywords):
        return "parameters_table"
    
    # Check for results table
    result_keywords = ["result", "sample", "control", "measurement", "value", "mean", "sd", "p-value"]
    if any(kw in header_text for kw in result_keywords):
        return "results_table"
    
    return "data_table"

def extract_materials_from_tables(tables_data):
    """
    Extract materials information specifically from material tables.
    
    Args:
        tables_data: List of extracted tables
    
    Returns:
        List of materials from tables
    """
    materials = []
    
    for table in tables_data:
        if table.get("table_type") == "materials_table":
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            
            for row in rows:
                material_info = {"source": "pdf_table", "data": {}}
                
                # Map headers to values
                for i, header in enumerate(headers):
                    if i < len(row) and row[i]:
                        material_info["data"][str(header)] = row[i]
                
                if material_info["data"]:
                    materials.append(material_info)
    
    return materials

def extract_parameters_from_tables(tables_data):
    """
    Extract parameter values specifically from parameter tables.
    
    Args:
        tables_data: List of extracted tables
    
    Returns:
        List of parameters from tables
    """
    parameters = []
    
    for table in tables_data:
        if table.get("table_type") == "parameters_table":
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            
            for row in rows:
                param_info = {"source": "pdf_table", "data": {}}
                
                for i, header in enumerate(headers):
                    if i < len(row) and row[i]:
                        param_info["data"][str(header)] = row[i]
                
                if param_info["data"]:
                    parameters.append(param_info)
    
    return parameters

def save_summary(tables_data, summary_path):
    """
    Save a summary of extracted tables.
    
    Args:
        tables_data: List of extracted tables
        summary_path: Path to save summary
    """
    summary = {
        "total_tables": len(tables_data),
        "tables_by_page": {},
        "table_types": {},
    }
    
    # Group by page
    for table in tables_data:
        page = table.get("page_number", 0)
        summary["tables_by_page"][str(page)] = summary["tables_by_page"].get(str(page), 0) + 1
    
    # Group by type
    for table in tables_data:
        table_type = table.get("table_type", "unknown")
        summary["table_types"][table_type] = summary["table_types"].get(table_type, 0) + 1
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_pdf_tables.py <input_pdf> <output_json>")
        print("\nExample:")
        print("  python extract_pdf_tables.py paper.pdf output/tables.json")
        sys.exit(1)
    
    # Check dependencies
    if not check_pdfplumber():
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract tables
    print(f"Extracting tables from: {pdf_path}")
    tables_data = extract_tables_from_pdf(pdf_path, output_path)
    
    # Generate summary
    summary_path = output_path.parent / "tables_summary.json"
    save_summary(tables_data, summary_path)
    
    # Print results
    print(f"✓ Extracted {len(tables_data)} tables")
    print(f"✓ Tables saved to: {output_path}")
    print(f"✓ Summary saved to: {summary_path}")
    
    # Print table type breakdown
    table_types = {}
    for table in tables_data:
        t_type = table.get("table_type", "unknown")
        table_types[t_type] = table_types.get(t_type, 0) + 1
    
    print(f"\nTable types:")
    for t_type, count in table_types.items():
        print(f"  - {t_type}: {count}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
