#!/usr/bin/env python3
"""
Compare experimental method details between two papers.
Identifies differences in protocol parameters and significance.
Only compares same experiment types for meaningful comparison.
"""

import json
import sys
import numpy as np
import re
from pathlib import Path

# Import experiment classifier
sys.path.insert(0, str(Path(__file__).parent))
from experiment_classifier import identify_experiment_types


def load_method_details(json_path):
    """
    Load method details from JSON file.

    Args:
        json_path: Path to JSON file

    Returns:
        Dictionary of method details
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_numeric(value):
    """
    Extract numeric value from parameter string.

    Args:
        value: Parameter value string

    Returns:
        Numeric value or None
    """
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            return float(match.group(0))
    
    return None


def compare_parameters(param1, param2, param_name):
    """
    Compare two parameter values and determine if difference is significant.

    Args:
        param1: First parameter value
        param2: Second parameter value
        param_name: Name of parameter

    Returns:
        Dictionary with comparison result
    """
    result = {
        "parameter": param_name,
        "value1": param1,
        "value2": param2,
        "difference": None,
        "significant": False,
        "magnitude": None
    }

    num1 = extract_numeric(param1)
    num2 = extract_numeric(param2)

    if num1 is not None and num2 is not None:
        diff = abs(num1 - num2)
        ratio = max(num1, num2) / min(num1, num2) if min(num1, num2) != 0 else float('inf')
        
        result["difference"] = f"{ratio:.2f}x"
        result["magnitude"] = diff

        if "temperature" in param_name.lower():
            result["significant"] = diff >= 5
        elif "time" in param_name.lower() or "duration" in param_name.lower():
            result["significant"] = ratio >= 2.0
        elif "concentration" in param_name.lower():
            result["significant"] = ratio >= 2.0
        else:
            result["significant"] = ratio >= 1.5
            result["difference"] = "Different"
    else:
        if param1 != param2:
            result["difference"] = "Different"
            result["significant"] = True
        else:
            result["difference"] = "Same"
            result["significant"] = False

    return result


def compare_dictionaries(dict1, dict2, category_name):
    """
    Compare two dictionaries of parameters.

    Args:
        dict1: First parameter dictionary
        dict2: Second parameter dictionary
        category_name: Name of parameter category

    Returns:
        List of comparison results
    """
    results = []
    all_keys = set(dict1.keys()) | set(dict2.keys())

    for key in all_keys:
        val1 = dict1.get(key, "N/A")
        val2 = dict2.get(key, "N/A")

        if val1 != "N/A" and val2 != "N/A":
            comparison = compare_parameters(val1, val2, f"{category_name} - {key}")
            results.append(comparison)
        elif val1 != val2:
            results.append({
                "parameter": f"{category_name} - {key}",
                "value1": val1,
                "value2": val2,
                "difference": "Present in one paper only",
                "significant": True,
                "magnitude": None
            })

    return results


def compare_lists(list1, list2, category_name):
    """
    Compare two lists (e.g., cell lines).

    Args:
        list1: First list
        list2: Second list
        category_name: Name of list category

    Returns:
        Dictionary with comparison result
    """
    set1 = set(list1) if list1 else set()
    set2 = set(list2) if list2 else set()

    result = {
        "category": category_name,
        "value1": list1 if list1 else [],
        "value2": list2 if list2 else [],
        "common": list(set1 & set2),
        "unique1": list(set1 - set2),
        "unique2": list(set2 - set1),
        "significant": len(set1 ^ set2) > 0
    }

    return result


def compare_methods(method1, method2):
    """
    Compare two complete method detail objects.
    Only compares experiment types that are present in BOTH papers.

    Args:
        method1: First method details dictionary
        method2: Second method details dictionary

    Returns:
        Dictionary with full comparison results grouped by experiment type
    """
    text1 = method1.get("full_text", "")
    text2 = method2.get("full_text", "")

    exp_types1 = identify_experiment_types(text1)
    exp_types2 = identify_experiment_types(text2)

    types1_set = set(exp_types1["detected_types"])
    types2_set = set(exp_types2["detected_types"])
    common_types = types1_set & types2_set

    comparison = {
        "summary": {
            "method_name_1": method1.get("method_name", "Unknown"),
            "method_name_2": method2.get("method_name", "Unknown"),
            "paper1_experiment_types": sorted(types1_set),
            "paper2_experiment_types": sorted(types2_set),
            "common_experiment_types": sorted(common_types),
            "total_common_types": len(common_types),
            "total_differences": 0,
            "significant_differences": 0
        },
        "comparisons_by_type": {}
    }

    experiment_type_names = {
        "western_blot": "Western Blot",
        "transfection": "Transfection",
        "cell_proliferation": "Cell Proliferation",
        "cell_migration": "Cell Migration",
        "cell_apoptosis": "Cell Apoptosis",
        "chip_seq": "ChIP-seq",
        "luciferase": "Luciferase Reporter",
        "qpcr": "qPCR",
        "immunofluorescence": "Immunofluorescence",
        "co_ip": "Co-IP"
    }

    for exp_type in common_types:
        type_name = experiment_type_names.get(exp_type, exp_type)

        type_comparison = {
            "experiment_type": type_name,
            "found_in_both": True,
            "parameter_comparisons": [],
            "list_comparisons": [],
            "differences_count": 0,
            "significant_count": 0
        }

        # Extract parameters based on experiment type
        params1 = {}
        params2 = {}

        # Define keywords for each experiment type to filter relevant parameters
        exp_keywords = {
            "western_blot": ["antibody", "protein", "membrane", "gel", "electrophoresis", "immunoblot", "wb"],
            "transfection": ["vector", "plasmid", "sirna", "transfect", "lipofectamine", "electroporation", "peimin"],
            "cell_proliferation": ["cck", "mtt", "proliferation", "growth", "cell viability", "eduf", "brd"],
            "cell_migration": ["migration", "invasion", "transwell", "wound", "scratch", "boyden", "chamber"],
            "cell_apoptosis": ["apoptosis", "annexin", "pi", "caspase", "tunel", "flow", "dapi"],
            "chip_seq": ["chip", "chromatin", "immunoprecipitation", "sequencing", "dna binding"],
            "luciferase": ["luciferase", "reporter", "firefly", "renilla", "promoter", "dual"],
            "qpcr": ["qpcr", "quantitative", "real-time", "taqman", "sybr", "pcr", "rt-pcr"],
            "immunofluorescence": ["immunofluorescence", "if", "fluorescence", "microscopy", "conjugated"],
            "co_ip": ["co-ip", "coimmunoprecipitation", "pull-down", "ip"]
        }

        keywords = exp_keywords.get(exp_type, [])

        # Extract relevant parameters for each category
        for param_cat in ["concentrations", "temperatures", "durations", "ratios", "volumes"]:
            cat1 = method1.get(param_cat, {})
            cat2 = method2.get(param_cat, {})

            # Get all keys from both papers
            all_keys = set(list(cat1.keys()) + list(cat2.keys()))

            for key in all_keys:
                # Check if this parameter is relevant for the experiment type
                is_relevant = False
                key_lower = key.lower()

                for kw in keywords:
                    if kw in key_lower:
                        is_relevant = True
                        break

                # If no keyword match, include if it appears in both papers (common parameters)
                if not is_relevant and cat1.get(key) and cat2.get(key):
                    is_relevant = True

                # If still not relevant, include it as a general parameter
                if not is_relevant and param_cat in ["temperatures", "durations"]:
                    is_relevant = True

                if is_relevant and (cat1.get(key) or cat2.get(key)):
                    params1[f"{param_cat} - {key}"] = cat1.get(key, "N/A")
                    params2[f"{param_cat} - {key}"] = cat2.get(key, "N/A")

        # Compare parameters
        if params1 or params2:
            param_comparisons = []
            all_keys = set(list(params1.keys()) + list(params2.keys()))
            for key in all_keys:
                val1 = params1.get(key, "N/A")
                val2 = params2.get(key, "N/A")
                if val1 != "N/A" or val2 != "N/A":
                    comp = compare_parameters(val1, val2, key)
                    param_comparisons.append(comp)
            type_comparison["parameter_comparisons"] = param_comparisons

        # Cell lines comparison (common for cell-based experiments)
        if exp_type in ["cell_proliferation", "cell_migration", "cell_apoptosis", "transfection"]:
            lines1 = method1.get("cell_lines", [])
            lines2 = method2.get("cell_lines", [])
            if lines1 or lines2:
                list_comp = compare_lists(lines1, lines2, "Cell Lines")
                type_comparison["list_comparisons"].append(list_comp)

        # Organisms comparison (common for all experiments)
        org1 = method1.get("organisms", [])
        org2 = method2.get("organisms", [])
        if org1 or org2:
            list_comp = compare_lists(org1, org2, "Organisms")
            type_comparison["list_comparisons"].append(list_comp)

        sig_count = sum(1 for p in type_comparison["parameter_comparisons"] if p["significant"])
        sig_count += sum(1 for l in type_comparison["list_comparisons"] if l["significant"])
        
        type_comparison["differences_count"] = len(type_comparison["parameter_comparisons"]) + len(type_comparison["list_comparisons"])
        type_comparison["significant_count"] = sig_count

        comparison["comparisons_by_type"][exp_type] = type_comparison

    total_diffs = 0
    total_sig = 0
    for exp_type, comp in comparison["comparisons_by_type"].items():
        total_diffs += comp["differences_count"]
        total_sig += comp["significant_count"]

    comparison["summary"]["total_differences"] = total_diffs
    comparison["summary"]["significant_differences"] = total_sig

    if not common_types:
        comparison["summary"]["warning"] = "No common experiment types found between the two papers"

    return comparison


def save_comparison(comparison, output_path):
    """
    Save comparison results to JSON file.

    Args:
        comparison: Comparison dictionary
        output_path: Path to save JSON file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)


def main():
    """Main function."""
    if len(sys.argv) < 4:
        print("Usage: python compare_methods.py <method1_json> <method2_json> <output_json>")
        sys.exit(1)

    method1_file = Path(sys.argv[1])
    method2_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    if not method1_file.exists():
        print(f"Error: Method 1 file not found: {method1_file}", file=sys.stderr)
        sys.exit(1)

    if not method2_file.exists():
        print(f"Error: Method 2 file not found: {method2_file}", file=sys.stderr)
        sys.exit(1)

    method1 = load_method_details(method1_file)
    method2 = load_method_details(method2_file)

    comparison = compare_methods(method1, method2)

    save_comparison(comparison, output_file)

    print(f"Comparison saved to: {output_file}")
    print(f"Common experiment types: {comparison['summary']['total_common_types']}")
    print(f"Common types: {', '.join(comparison['summary']['common_experiment_types'])}")
    print(f"Total differences: {comparison['summary']['total_differences']}")
    print(f"Significant differences: {comparison['summary']['significant_differences']}")
    
    if "warning" in comparison["summary"]:
        print(f"\nWarning: {comparison['summary']['warning']}")
    
    sys.exit(0)
