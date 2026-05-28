#!/usr/bin/env python3
"""
Generate HTML comparison report with literature-backed explanations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_json(file_path):
    """
    Load JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_paper_info_section(paper_info, paper_number):
    """
    Generate HTML section for paper information.

    Args:
        paper_info: Paper metadata dictionary
        paper_number: Paper identifier (1 or 2)

    Returns:
        HTML string
    """
    return f"""
    <div class="paper-info">
        <h2>paper{paper_number}information</h2>
        <p><strong>title:</strong> {paper_info.get('title', 'N/A')}</p>
        <p><strong>author:</strong> {', '.join(paper_info.get('authors', []))}</p>
        <p><strong>years:</strong> {paper_info.get('year', 'N/A')}</p>
        <p><strong>Journal:</strong> {paper_info.get('journal', 'N/A')}</p>
    </div>
    """

def generate_comparison_table(comparison):
    """
    Generate HTML comparison table.

    Args:
        comparison: Comparison dictionary

    Returns:
        HTML string
    """
    html = """<h2>Comparison of methods</h2>"""

    # Check if the comparison uses the new structure (comparisons_by_type)
    if "comparisons_by_type" in comparison:
        # New structure: grouped by experiment type
        summary = comparison.get("summary", {})
        paper1_types = summary.get("paper1_experiment_types", [])
        paper2_types = summary.get("paper2_experiment_types", [])
        common_types = summary.get("common_experiment_types", [])

        # Add experiment type summary
        html += """<div class="summary-box">
            <h3>Overview of experiment types</h3>
            <p><strong>Paper 1 Experiment Type:</strong> {paper1_types_str}</p>
            <p><strong>Paper 2 Experiment Type:</strong> {paper2_types_str}</p>
            <p><strong>Common experiment type:</strong> {common_types_str} ({count} species)</p>
        </div>""".format(
            paper1_types_str=", ".join(paper1_types),
            paper2_types_str=", ".join(paper2_types),
            common_types_str=", ".join(common_types),
            count=len(common_types)
        )

        # Generate comparison for each experiment type
        for exp_type, type_comp in comparison.get("comparisons_by_type", {}).items():
            type_name = type_comp.get("experiment_type", exp_type)
            param_comps = type_comp.get("parameter_comparisons", [])
            list_comps = type_comp.get("list_comparisons", [])
            sig_count = type_comp.get("significant_count", 0)

            html += f"""
            <div class="experiment-type-section">
                <h3>{type_name}</h3>
                <p><strong>Number of parameter comparisons:</strong> {len(param_comps)} | <strong>significant difference:</strong> {sig_count}</p>
            """

            # Add parameter comparisons table
            if param_comps:
                html += f"""
                <table class="comparison-table">
                    <tr>
                        <th>parameter</th>
                        <th>paper1</th>
                        <th>paper2</th>
                        <th>difference</th>
                    </tr>
                """

                for param in param_comps:
                    row_class = "difference" if param.get("significant") else ""
                    html += f"""
                    <tr class="{row_class}">
                        <td>{param['parameter']}</td>
                        <td>{param['value1']}</td>
                        <td>{param['value2']}</td>
                        <td>{param['difference']}</td>
                    </tr>
                    """

                html += "</table>"

            # Add list comparisons (cell lines, organisms, etc.)
            if list_comps:
                for list_comp in list_comps:
                    category = list_comp.get("category", "Unknown")
                    common = list_comp.get("common", [])
                    unique1 = list_comp.get("unique1", [])
                    unique2 = list_comp.get("unique2", [])

                    html += f"""
                    <div class="list-comparison">
                        <h4>{category} contrast</h4>
                        <p><strong>common:</strong> {", ".join(common) if common else "none"}</p>
                        <p><strong>paper1unique:</strong> {", ".join(unique1) if unique1 else "none"}</p>
                        <p><strong>paper2unique:</strong> {", ".join(unique2) if unique2 else "none"}</p>
                    </div>
                    """

            html += "</div>"

    else:
        # Old structure: flat parameter list
        html += """<table class="comparison-table">
            <tr>
                <th>Parameters</th>
                <th>Paper 1</th>
                <th>Paper 2</th>
                <th>Differences</th>
            </tr>"""

        # Add parameter comparisons
        for category, params in comparison.get("parameters", {}).items():
            for param in params:
                if param.get("significant"):
                    html += f"""
                    <tr class="difference">
                        <td>{param['parameter']}</td>
                        <td>{param['value1']}</td>
                        <td>{param['value2']}</td>
                        <td>{param['difference']}</td>
                    </tr>
                    """

        html += "</table>"

    return html

def generate_explanation_section(explanations):
    """
    Generate HTML section for literature-backed explanations.

    Args:
        explanations: Explanations dictionary

    Returns:
        HTML string
    """
    html = """<div class="explanation-section">
        <h2>Analysis of reasons for differences</h2>"""

    for exp in explanations.get("explanations", []):
        param_name = exp.get("parameter", "unknown parameters")
        diff_desc = exp.get("difference_description", "")
        explanation = exp.get("explanation", "No explanation")
        evidence_grade = exp.get("evidence_grade", "Low")
        query = exp.get("query", "")

        # Map evidence grade to CSS class
        grade_classes = {
            "High": "evidence-high",
            "Medium": "evidence-medium",
            "Low": "evidence-low"
        }
        grade_class = grade_classes.get(evidence_grade, "evidence-low")

        # Get key papers
        results = exp.get("results", [])
        references = []
        for i, result in enumerate(results[:3], 1):
            title = result.get("title", "Unknown")
            authors = result.get("authors", [])
            year = result.get("year", "N/A")
            source = result.get("source", "")

            if isinstance(authors, list):
                authors_str = ', '.join([a if isinstance(a, str) else str(a) for a in authors[:3]])
            else:
                authors_str = str(authors)

            references.append(f"{i}. {authors_str} ({year}). {title}. {source}")

        html += f"""
        <div class="explanation-item">
            <h3>{param_name}</h3>
            <p><strong>difference:</strong> {diff_desc}</p>
            <p><strong>search query:</strong> <code>{query}</code></p>
            <div class="{grade_class}">
                <p><strong>explain:</strong> {explanation}</p>
                <p><strong>Level of evidence:</strong> {evidence_grade}</p>
                <p><strong>References:</strong></p>
                <ul>
                    {''.join(f'<li>{ref}</li>' for ref in references)}
                </ul>
            </div>
        </div>
        """

    html += "</div>"
    return html

def generate_summary_section(comparison):
    """
    Generate summary section.

    Args:
        comparison: Comparison dictionary

    Returns:
        HTML string
    """
    summary = comparison.get("summary", {})
    total_diffs = summary.get("total_differences", 0)
    significant_diffs = summary.get("significant_differences", 0)

    # Check if new structure exists
    if "paper1_experiment_types" in summary:
        paper1_types = summary.get("paper1_experiment_types", [])
        paper2_types = summary.get("paper2_experiment_types", [])
        common_types = summary.get("common_experiment_types", [])
        total_common_types = summary.get("total_common_types", 0)

        # Calculate unique experiment types for each paper
        unique_types_1 = set(paper1_types) - set(common_types)
        unique_types_2 = set(paper2_types) - set(common_types)

        return f"""
    <h2>Summarize</h2>
    <div class="summary-box">
        <h3>comparison range</h3>
        <p><strong>Common experiment type ({total_common_types}):</strong> {", ".join(common_types)}</p>
        <p><strong>paper1Unique experiment type:</strong> {", ".join(unique_types_1) if unique_types_1 else "none"}</p>
        <p><strong>paper2Unique experiment type:</strong> {", ".join(unique_types_2) if unique_types_2 else "none"}</p>
        <p><em>Note: Only methodological details of common experimental types are compared</em></p>

        <h3>difference statistics</h3>
        <p><strong>total differences:</strong> {total_diffs}</p>
        <p><strong>number of significant differences:</strong> {significant_diffs}</p>
        <p>The two papers share a common experimental type of method{total_diffs}Differences everywhere,in{significant_diffs}Significant differences everywhere。Significantly different parameters were analyzed through a literature search,Provided relevant explanations。</p>
    </div>
    """
    else:
        # Old structure
        return f"""
    <h2>Summarize</h2>
    <div class="summary-box">
        <p><strong>total differences:</strong> {total_diffs}</p>
        <p><strong>number of significant differences:</strong> {significant_diffs}</p>
        <p>The two papers share the same experimental methods{total_diffs}Differences everywhere，in{significant_diffs}Significant differences everywhere。Significantly different parameters were analyzed through a literature search，Provided relevant explanations。</p>
    </div>
    """

def generate_references_section(explanations):
    """
    Generate references section.

    Args:
        explanations: Explanations dictionary

    Returns:
        HTML string
    """
    all_results = []
    for exp in explanations.get("explanations", []):
        all_results.extend(exp.get("results", []))

    # Deduplicate
    seen = set()
    unique_results = []
    for result in all_results:
        title = result.get("title", "")
        if title and title not in seen:
            seen.add(title)
            unique_results.append(result)

    html = """<h2>References</h2>
    <ul class="references-list">"""

    for result in unique_results:
        title = result.get("title", "Unknown")
        authors = result.get("authors", [])
        year = result.get("year", "N/A")
        journal = result.get("journal", result.get("venue", "N/A"))

        if isinstance(authors, list):
            authors_str = ', '.join([a if isinstance(a, str) else str(a) for a in authors[:3]])
        else:
            authors_str = str(authors)

        html += f"""
        <li>{authors_str} ({year}). {title}. {journal}</li>
        """

    html += "</ul>"
    return html

def generate_html_report(paper1_info, paper2_info, comparison, explanations):
    """
    Generate complete HTML report.

    Args:
        paper1_info: Paper 1 metadata
        paper2_info: Paper 2 metadata
        comparison: Comparison dictionary
        explanations: Explanations dictionary

    Returns:
        Complete HTML string
    """
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Experimental method comparison report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 40px;
            background-color: #f8f9fa;
            line-height: 1.6;
            color: #333;
        }}

        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}

        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            border-left: 5px solid #3498db;
            padding-left: 15px;
        }}

        h3 {{
            color: #2c3e50;
            margin-top: 25px;
            margin-bottom: 15px;
        }}

        .paper-info {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .paper-info p {{
            margin: 10px 0;
            font-size: 15px;
        }}

        .comparison-table {{
            border-collapse: collapse;
            width: 100%;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}

        .comparison-table th {{
            background-color: #3498db;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
            font-size: 14px;
        }}

        .comparison-table td {{
            border: 1px solid #ecf0f1;
            padding: 12px 15px;
            text-align: left;
            font-size: 14px;
        }}

        .comparison-table tr:hover {{
            background-color: #f8f9fa;
        }}

        .difference {{
            background-color: #fff3cd;
            font-weight: 500;
        }}

        .explanation-section {{
            margin-top: 50px;
        }}

        .explanation-item {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .explanation-item code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #e74c3c;
        }}

        .explanation-item p {{
            margin: 12px 0;
            font-size: 15px;
        }}

        .explanation-item ul {{
            margin: 10px 0 10px 20px;
            font-size: 14px;
        }}

        .explanation-item li {{
            margin: 8px 0;
        }}

        .evidence-high {{
            border-left: 5px solid #27ae60;
            padding-left: 20px;
            background-color: #d5f5e3;
            margin: 15px 0;
            padding: 15px;
            border-radius: 0 5px 5px 0;
        }}

        .evidence-medium {{
            border-left: 5px solid #f39c12;
            padding-left: 20px;
            background-color: #fcf3cf;
            margin: 15px 0;
            padding: 15px;
            border-radius: 0 5px 5px 0;
        }}

        .evidence-low {{
            border-left: 5px solid #e74c3c;
            padding-left: 20px;
            background-color: #fadbd8;
            margin: 15px 0;
            padding: 15px;
            border-radius: 0 5px 5px 0;
        }}

        .summary-box {{
            background: white;
            border: 2px solid #3498db;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .summary-box p {{
            margin: 12px 0;
            font-size: 16px;
        }}

        .summary-box h3 {{
            color: #2c3e50;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 18px;
        }}

        .experiment-type-section {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .experiment-type-section h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}

        .experiment-type-section p {{
            margin: 10px 0;
            font-size: 15px;
        }}

        .list-comparison {{
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}

        .list-comparison h4 {{
            color: #2c3e50;
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 16px;
        }}

        .list-comparison p {{
            margin: 8px 0;
            font-size: 14px;
        }}

        .references-list {{
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .references-list li {{
            margin: 12px 0;
            font-size: 14px;
            line-height: 1.5;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #7f8c8d;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <h1>Experimental method comparison report</h1>

    {generate_paper_info_section(paper1_info, 1)}
    {generate_paper_info_section(paper2_info, 2)}

    {generate_comparison_table(comparison)}

    {generate_explanation_section(explanations)}

    {generate_summary_section(comparison)}

    {generate_references_section(explanations)}

    <div class="footer">
        <p>Report generation time: {datetime.now().strftime('%Y year %m month %d day %H:%M')}</p>
        <p>This report is provided byExperiment Detail ComparatorAutomatically generated</p>
    </div>
</body>
</html>"""

    return html_template

def save_html_report(html_content, output_path):
    """
    Save HTML report to file.

    Args:
        html_content: HTML string
        output_path: Path to save HTML file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    if len(sys.argv) < 6:
        print("Usage: python generate_html_report.py <paper1_json> <paper2_json> <comparison_json> <explanations_json> <output_html>")
        sys.exit(1)

    paper1_file = Path(sys.argv[1])
    paper2_file = Path(sys.argv[2])
    comparison_file = Path(sys.argv[3])
    explanations_file = Path(sys.argv[4])
    output_file = Path(sys.argv[5])

    # Load data
    paper1_info = load_json(paper1_file)
    paper2_info = load_json(paper2_file)
    comparison = load_json(comparison_file)
    explanations = load_json(explanations_file)

    # Generate HTML report
    html = generate_html_report(paper1_info, paper2_info, comparison, explanations)

    # Save report
    save_html_report(html, output_file)

    print(f"HTML report generated: {output_file}")
    sys.exit(0)

if __name__ == "__main__":
    main()
