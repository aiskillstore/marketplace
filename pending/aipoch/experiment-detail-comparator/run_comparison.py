#!/usr/bin/env python3
"""
Main workflow script for experiment detail comparison.
Integrates all steps: PDF retrieval, method extraction, comparison, literature search, and HTML report generation.
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path

def run_command(cmd, description):
    """
    Run a command and handle errors.

    Args:
        cmd: Command list
        description: Description of the command

    Returns:
        Command output or None if failed
    """
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {description} failed", file=sys.stderr)
        print(f"STDERR: {e.stderr}", file=sys.stderr)
        return None

def search_zotero_items(query, limit=5):
    """
    Search for items in Zotero using CLI tools or MCP if available.

    Args:
        query: Search query
        limit: Maximum number of results

    Returns:
        List of item dictionaries or None
    """
    # Try to use Zotero CLI if available
    try:
        cmd = ["zotcli", "search", "--limit", str(limit), query]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
    except:
        pass

    # Try using zotero-cli if available
    try:
        cmd = ["zotero-cli", "search", query]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
    except:
        pass

    # Fallback: Return None and print instructions
    print("Warning: Could not search Zotero automatically", file=sys.stderr)
    print("Please ensure one of the following is installed:", file=sys.stderr)
    print("  - zotcli (https://github.com/jlegewie/zotcli)", file=sys.stderr)
    print("  - zotero-cli (https://github.com/volfpeter/zotero-cli)", file=sys.stderr)
    print("Or provide the attachment key directly", file=sys.stderr)
    return None

def get_papers_from_zotero(paper1_query, paper2_query):
    """
    Search and retrieve two papers from Zotero.

    Args:
        paper1_query: Query for paper 1 (can be attachment key, title, or DOI)
        paper2_query: Query for paper 2 (can be attachment key, title, or DOI)

    Returns:
        Tuple of (pdf_path1, pdf_path2, paper_info1, paper_info2) or None if failed
    """
    print("=== Step 1: Get the paper from Zotero ===")

    script_path = Path("scripts/get_zotero_pdf.py")
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    # Function to get paper from Zotero
    def get_single_paper(query, index):
        # Check if query is already an attachment key (32 chars, alphanumeric)
        import re
        if re.match(r'^[A-Z0-9]{32}$', query.strip()):
            # It's an attachment key, directly get PDF
            attachment_key = query.strip()
            result = run_command(
                ["python", str(script_path), attachment_key],
                f"Get the paper{index} PDF (use attachment key: {attachment_key[:8]}...)"
            )
            if result:
                pdf_path = Path(result)
                # Copy to temp directory with proper name
                dest_pdf = temp_dir / f"paper{index}.pdf"
                import shutil
                shutil.copy2(pdf_path, dest_pdf)

                # Extract basic info from PDF filename or metadata
                paper_info = {
                    "title": f"Paper {index} (from Zotero)",
                    "authors": [],
                    "year": None,
                    "journal": None,
                    "attachment_key": attachment_key
                }
                return dest_pdf, paper_info

        # Try to search Zotero for the paper
        items = search_zotero_items(query, limit=3)
        if items and len(items) > 0:
            # Use first result
            item = items[0]
            attachment_key = item.get("key", "")

            if attachment_key:
                result = run_command(
                    ["python", str(script_path), attachment_key],
                    f"Get the paper{index} PDF"
                )
                if result:
                    pdf_path = Path(result)
                    dest_pdf = temp_dir / f"paper{index}.pdf"
                    import shutil
                    shutil.copy2(pdf_path, dest_pdf)

                    # Extract metadata from item
                    paper_info = {
                        "title": item.get("data", {}).get("title", query),
                        "authors": [a.get("data", {}).get("firstName", "") + " " + a.get("data", {}).get("lastName", "")
                                   for a in item.get("data", {}).get("creators", [])],
                        "year": item.get("meta", {}).get("parsedDate", "").split("-")[0] if item.get("meta", {}).get("parsedDate") else None,
                        "journal": item.get("data", {}).get("publicationTitle", None)
                    }
                    return dest_pdf, paper_info

        print(f"Warning: Could not retrieve paper {index} from Zotero: {query}", file=sys.stderr)
        return None, None

    # Get both papers
    pdf1_path, paper1_info = get_single_paper(paper1_query, 1)
    pdf2_path, paper2_info = get_single_paper(paper2_query, 2)

    if not pdf1_path or not pdf2_path:
        print("\nError: Could not retrieve both papers from Zotero", file=sys.stderr)
        print("\nAlternative: Provide PDF files directly", file=sys.stderr)
        print("Usage: python run_comparison.py <pdf_path1> <pdf_path2> [output_dir]", file=sys.stderr)
        return None, None, None, None

    return pdf1_path, pdf2_path, paper1_info, paper2_info

def convert_pdfs_to_markdown(pdf_path1, pdf_path2):
    """
    Convert PDFs to markdown format using mistral-pdf-to-markdown skill.

    Args:
        pdf_path1: Path to PDF 1
        pdf_path2: Path to PDF 2

    Returns:
        Tuple of (markdown_path1, markdown_path2) or (None, None) if failed
    """
    print("=== Step 2: Convert PDF to Markdown ===")

    # Create temp directory
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    md1_path = temp_dir / "paper1.md"
    md2_path = temp_dir / "paper2.md"

    script_path = Path("scripts/convert_pdf_to_markdown.py")

    # Convert PDF 1
    result1 = run_command(
        ["python", str(script_path), str(pdf_path1), str(md1_path)],
        f"conversion essay1 PDF ({pdf_path1.name})"
    )

    if not result1:
        print("Warning: Failed to convert PDF 1 to markdown", file=sys.stderr)
        return None, None

    # Convert PDF 2
    result2 = run_command(
        ["python", str(script_path), str(pdf_path2), str(md2_path)],
        f"conversion essay2 PDF ({pdf_path2.name})"
    )

    if not result2:
        print("Warning: Failed to convert PDF 2 to markdown", file=sys.stderr)
        return None, None

    return md1_path, md2_path

def extract_method_details(md_path1, md_path2):
    """
    Extract method details from markdown files.

    Args:
        md_path1: Path to markdown 1
        md_path2: Path to markdown 2

    Returns:
        Tuple of (method1_json, method2_json)
    """
    print("=== Step 3: Extract method details ===")

    script_path = Path("scripts/extract_method_section.py")

    method1_json = Path("temp/paper1_method.json")
    method2_json = Path("temp/paper2_method.json")

    # Extract methods from paper 1
    result1 = run_command(
        ["python", str(script_path), str(md_path1), str(method1_json)],
        f"Extract papers1method details"
    )

    if not result1:
        return None, None

    # Extract methods from paper 2
    result2 = run_command(
        ["python", str(script_path), str(md_path2), str(method2_json)],
        f"Extract papers2method details"
    )

    if not result2:
        return None, None

    return method1_json, method2_json

def compare_methods(method1_json, method2_json):
    """
    Compare two method detail files.

    Args:
        method1_json: Path to method 1 JSON
        method2_json: Path to method 2 JSON

    Returns:
        Path to comparison JSON
    """
    print("=== Step 4: Comparison method details ===")

    script_path = Path("scripts/compare_methods.py")
    comparison_json = Path("temp/comparison.json")

    result = run_command(
        ["python", str(script_path), str(method1_json), str(method2_json), str(comparison_json)],
        "Comparison method details"
    )

    if not result:
        return None

    return comparison_json

def search_explanations(comparison_json):
    """
    Search literature for explanations of differences.

    Args:
        comparison_json: Path to comparison JSON

    Returns:
        Path to explanations JSON
    """
    print("=== Step 5: Search the literature to explain the differences ===")

    script_path = Path("scripts/search_explanations.py")
    explanations_json = Path("temp/explanations.json")

    result = run_command(
        ["python", str(script_path), str(comparison_json), str(explanations_json)],
        "Search literature explanation"
    )

    if not result:
        return None

    return explanations_json

def generate_html_report(paper1_info, paper2_info, comparison_json, explanations_json):
    """
    Generate final HTML report.

    Args:
        paper1_info: Paper 1 metadata dict
        paper2_info: Paper 2 metadata dict
        comparison_json: Path to comparison JSON
        explanations_json: Path to explanations JSON

    Returns:
        Path to HTML report
    """
    print("=== Step 6: Generate HTML report ===")

    # Save paper info to temp files
    paper1_info_path = Path("temp/paper1_info.json")
    paper2_info_path = Path("temp/paper2_info.json")

    with open(paper1_info_path, 'w', encoding='utf-8') as f:
        json.dump(paper1_info, f, indent=2, ensure_ascii=False)

    with open(paper2_info_path, 'w', encoding='utf-8') as f:
        json.dump(paper2_info, f, indent=2, ensure_ascii=False)

    script_path = Path("scripts/generate_html_report.py")
    output_html = Path("comparison_report.html")

    result = run_command(
        ["python", str(script_path),
         str(paper1_info_path), str(paper2_info_path),
         str(comparison_json), str(explanations_json),
         str(output_html)],
        "Generate HTML report"
    )

    if not result:
        return None

    return output_html

def get_papers_from_local(pdf_path1, pdf_path2):
    """
    Get paper info from local PDF files.

    Args:
        pdf_path1: Path to PDF 1
        pdf_path2: Path to PDF 2

    Returns:
        Tuple of (pdf_path1, pdf_path2, paper_info1, paper_info2)
    """
    print("=== Step 1: Use local PDF files ===")

    # Copy PDFs to temp directory
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    dest_pdf1 = temp_dir / "paper1.pdf"
    dest_pdf2 = temp_dir / "paper2.pdf"

    import shutil
    shutil.copy2(pdf_path1, dest_pdf1)
    shutil.copy2(pdf_path2, dest_pdf2)

    # Extract basic info from filenames
    paper1_info = {
        "title": pdf_path1.stem.replace("_", " ").replace("-", " "),
        "authors": [],
        "year": None,
        "journal": None,
        "source": "local_file"
    }

    paper2_info = {
        "title": pdf_path2.stem.replace("_", " ").replace("-", " "),
        "authors": [],
        "year": None,
        "journal": None,
        "source": "local_file"
    }

    return dest_pdf1, dest_pdf2, paper1_info, paper2_info

def main():
    """
    Main workflow execution.
    """
    if len(sys.argv) < 3:
        print("Usage: python run_comparison.py <paper1_query> <paper2_query> [output_dir]")
        print("\nInput formats:")
        print("  1. Zotero search: title, author, or DOI")
        print("  2. Attachment key: 32-character Zotero key")
        print("  3. PDF file: local path to PDF file")
        print("\nExamples:")
        print("  python run_comparison.py 'CRISPR knockout in HeLa cells' 'CRISPR editing in HEK293'")
        print("  python run_comparison.py ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ123")
        print("  python run_comparison.py ./paper1.pdf ./paper2.pdf ./output")
        sys.exit(1)

    paper1_query = sys.argv[1]
    paper2_query = sys.argv[2]
    output_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".")

    print("=================================================")
    print("Experimental method comparison analysis tool")
    print("  Experiment Detail Comparator")
    print("=================================================")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    try:
        # Determine input type and get papers
        pdf1_path = Path(paper1_query)
        pdf2_path = Path(paper2_query)

        # Check if inputs are local PDF files
        if pdf1_path.exists() and pdf1_path.suffix.lower() == ".pdf" and \
           pdf2_path.exists() and pdf2_path.suffix.lower() == ".pdf":
            # Use local PDF files
            pdf1_path, pdf2_path, paper1_info, paper2_info = get_papers_from_local(pdf1_path, pdf2_path)
        else:
            # Try to get from Zotero
            pdf1_path, pdf2_path, paper1_info, paper2_info = get_papers_from_zotero(
                paper1_query, paper2_query
            )

        if not pdf1_path or not pdf2_path:
            print("\nError: Could not retrieve both papers", file=sys.stderr)
            sys.exit(1)

        # Step 2: Convert PDFs to Markdown
        md1_path, md2_path = convert_pdfs_to_markdown(pdf1_path, pdf2_path)

        if not md1_path or not md2_path:
            print("Error: Failed to convert PDFs to markdown", file=sys.stderr)
            sys.exit(1)

        # Step 3: Extract method details
        method1_json, method2_json = extract_method_details(md1_path, md2_path)

        if not method1_json or not method2_json:
            print("Error: Failed to extract method details", file=sys.stderr)
            sys.exit(1)

        # Step 4: Compare methods
        comparison_json = compare_methods(method1_json, method2_json)

        if not comparison_json:
            print("Error: Failed to compare methods", file=sys.stderr)
            sys.exit(1)

        # Step 5: Search for explanations
        explanations_json = search_explanations(comparison_json)

        if not explanations_json:
            print("Error: Failed to search for explanations", file=sys.stderr)
            sys.exit(1)

        # Step 6: Generate HTML report
        html_path = generate_html_report(
            paper1_info, paper2_info,
            comparison_json, explanations_json
        )

        if not html_path:
            print("Error: Failed to generate HTML report", file=sys.stderr)
            sys.exit(1)

        # Move output files to output directory
        final_html = output_dir / "comparison_report.html"
        final_comparison = output_dir / "method_details.json"
        final_explanations = output_dir / "explanations.json"

        # Check if files exist before renaming
        if Path("comparison_report.html").exists():
            Path("comparison_report.html").rename(final_html)
        else:
            print(f"Warning: comparison_report.html not found", file=sys.stderr)

        if Path("temp/comparison.json").exists():
            Path("temp/comparison.json").rename(final_comparison)
        else:
            print(f"Warning: temp/comparison.json not found", file=sys.stderr)

        if Path("temp/explanations.json").exists():
            Path("temp/explanations.json").rename(final_explanations)
        else:
            print(f"Warning: temp/explanations.json not found", file=sys.stderr)

        # Success!
        print("\n" + "=" * 50)
        print("✓ Analysis completed!")
        print("=" * 50)
        print(f"\noutput file:")
        print(f"  1. Comparison report: {final_html}")
        print(f"  2. method details: {final_comparison}")
        print(f"  3. Literature explanation: {final_explanations}")
        print(f"\nPlease open it in your browser {final_html} View full report")

    except Exception as e:
        print(f"\nError during execution: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Cleanup temp files
        print("Clean up temporary files...")
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
