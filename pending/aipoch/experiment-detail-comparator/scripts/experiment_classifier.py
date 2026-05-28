#!/usr/bin/env python3
"""
Identify and classify experiment types from methods section.
This enables comparison of the same experimental methods across papers.
"""

import re
import sys


def identify_experiment_types(method_text):
    """
    Identify experiment types from methods text.
    This helps group parameters by experiment type for meaningful comparison.

    Args:
        method_text: Methods section text

    Returns:
        Dictionary with detected experiment types and their parameters
    """
    experiment_types = {
        "western_blot": {"name": "Western Blot", "parameters": [], "found": False},
        "transfection": {"name": "Transfection", "parameters": [], "found": False},
        "cell_proliferation": {"name": "Cell Proliferation Assay", "parameters": [], "found": False},
        "cell_migration": {"name": "Cell Migration Assay", "parameters": [], "found": False},
        "cell_apoptosis": {"name": "Cell Apoptosis Assay", "parameters": [], "found": False},
        "chip_seq": {"name": "ChIP-seq", "parameters": [], "found": False},
        "luciferase": {"name": "Luciferase Reporter Assay", "parameters": [], "found": False},
        "qpcr": {"name": "qPCR", "parameters": [], "found": False},
        "immunofluorescence": {"name": "Immunofluorescence", "parameters": [], "found": False},
        "co_ip": {"name": "Co-IP", "parameters": [], "found": False}
    }

    method_text_lower = method_text.lower()

    # Western Blot detection
    western_keywords = [
        r'western\s*blot',
        r'western\s*-\s*blot',
        r'immunoblot',
        r'protein\s+extraction',
        r'sds\s*-\s*page',
        r'gel\s+electrophoresis'
    ]
    for keyword in western_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["western_blot"]["found"] = True
            break

    # Transfection detection
    transfection_keywords = [
        r'transfected\s+with',
        r'transfection\s+(?:using|by|via)',
        r'lipofectamine',
        r'polyethylenimine',
        r'peimin',
        r'electroporation',
        r'nucleofection',
    ]
    for keyword in transfection_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["transfection"]["found"] = True
            break

    # Cell Proliferation detection
    proliferation_keywords = [
        r'cell\s+proliferation',
        r'cck\s*-\s*8',
        r'mtt\s*assay',
        r'edus\s*-\s*incorporation',
        'brd(?:u|ezo)',
        'mts',
        'trypan\s+blue',
        'wst-\s*1'
    ]
    for keyword in proliferation_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["cell_proliferation"]["found"] = True
            break

    # Cell Migration detection
    migration_keywords = [
        r'transwell\s+assay',
        r'wound\s+healing\s+assay',
        r'scratch\s+assay',
        r'migration\s+assay',
        r'invasion\s+assay',
        'boyden\s+chamber'
    ]
    for keyword in migration_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["cell_migration"]["found"] = True
            break

    # Cell Apoptosis detection
    apoptosis_keywords = [
        r'apoptosis\s+assay',
        r'annexin\s+v',
        r'pi\s+staining',
        r'caspase\s+activity',
        'tunel\s+assay',
        'flow\s+cytometry',
        'dapi\s+staining'
    ]
    for keyword in apoptosis_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["cell_apoptosis"]["found"] = True
            break

    # ChIP-seq detection
    chip_keywords = [
        r'chip\s*-\s*seq',
        r'chromatin\s+immunoprecipitation',
        r'immunoprecipitation\s+sequencing',
        r'dna\s+binding',
        r'chip\s+assay'
    ]
    for keyword in chip_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["chip_seq"]["found"] = True
            break

    # Luciferase assay detection
    luciferase_keywords = [
        r'luciferase\s+reporter',
        r'luciferase\s+assay',
        r'promoter\s+activity',
        r'dual\s+luciferase',
        'renilla\s+luciferase',
        'firefly\s+luciferase'
    ]
    for keyword in luciferase_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["luciferase"]["found"] = True
            break

    # qPCR detection
    qpcr_keywords = [
        r'qpcr',
        r'quantitative\s+pcr',
        r'real\s*-\s*time\s+pcr',
        'taqman\s+assay',
        'sybr\s+green'
    ]
    for keyword in qpcr_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["qpcr"]["found"] = True
            break

    # Immunofluorescence detection
    if_keywords = [
        r'immunofluorescence',
        r'if\s+staining',
        r'conjugated\s+antibody',
        'fluorescence\s+microscopy',
        r'confocal\s+microscopy'
    ]
    for keyword in if_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["immunofluorescence"]["found"] = True
            break

    # Co-IP detection
    coip_keywords = [
        r'co\s*-\s*immunoprecipitation',
        r'coip',
        r'pull\s*-\s*down\s+assay',
        r'immunoprecipitation\s+followed\s+by'
    ]
    for keyword in coip_keywords:
        if re.search(keyword, method_text_lower):
            experiment_types["co_ip"]["found"] = True
            break

    return {
        "detected_types": [exp_type for exp_type, data in experiment_types.items() if data["found"]],
        "experiment_details": {exp_type: data for exp_type, data in experiment_types.items()}
    }


def extract_methods_by_type(method_text, experiment_types_info):
    """
    Extract parameters and group them by experiment type.
    Only extracts parameters for experiment types that were detected.

    Args:
        method_text: Methods section text
        experiment_types_info: Dictionary with detected experiment types

    Returns:
        Dictionary with parameters grouped by experiment type
    """
    # Create a simple parameters dict (simplified version)
    parameters = {
        "concentrations": [],
        "temperatures": [],
        "durations": [],
        "ratios": [],
        "volumes": [],
        "antibodies": [],
        "cell_lines": [],
        "inhibitors": [],
        "substrates": [],
        "reagents": [],
        "vectors": [],
        "siRNA": [],
        "plasmids": [],
        "reporters": [],
        "buffers": []
    }

    method_text_lower = method_text.lower()

    # Only process detected experiment types
    detected_types = experiment_types_info["detected_types"]

    # Extract concentrations
    if "western_blot" in detected_types or "transfection" in detected_types:
        conc_pattern = r'(\d+\.?\d*)\s*(?:mM|uM|nM|mg/mL|ug/mL|ng/mL|%|v/v)'
        for match in re.finditer(conc_pattern, method_text):
            parameters["concentrations"].append({
                "parameter": "Concentration",
                "value": match.group(0),
                "experiment_type": "Western Blot" if "western_blot" in detected_types else "Transfection"
            })

    if "cell_proliferation" in detected_types:
        cck_pattern = r'(\d+)\s*ug/mL|ng/mL'
        for match in re.finditer(cck_pattern, method_text):
            parameters["reagents"].append({
                "parameter": "CCK-8 Reagent",
                "value": match.group(0),
                "experiment_type": "Cell Proliferation"
            })

    if "chip_seq" in detected_types or "co_ip" in detected_types:
        antibody_pattern = r'(\d+|[\d\.?\d]+\s*ug/mg)\s*(?:antibody|anti-\s*[A-Za-z0-9]+\s*)'
        for match in re.finditer(antibody_pattern, method_text, re.IGNORECASE):
            parameters["antibodies"].append({
                "parameter": "Antibody",
                "value": match.group(0),
                "experiment_type": "ChIP-seq" if "chip_seq" in detected_types else "Co-IP"
            })

    if "luciferase" in detected_types:
        reporter_pattern = r'(?:firefly|renilla|pGL\d+|pRL)\s*luciferase|reporter|vector)'
        for match in re.finditer(reporter_pattern, method_text, re.IGNORECASE):
            parameters["reporters"].append({
                "parameter": "Reporter",
                "value": match.group(0),
                "experiment_type": "Luciferase"
            })

    if "transfection" in detected_types:
        vector_pattern = r'(\d+|[\d\.?\d]+\s*ug|ng)'
        for match in re.finditer(vector_pattern, method_text):
            parameters["vectors"].append({
                "parameter": "Expression Vector",
                "value": match.group(0),
                "experiment_type": "Transfection"
            })

        sirna_pattern = r'si[GL2|RNA|RNAi]\s+(?:targeting|against|knockdown)\s*[A-Za-z0-9]+'
        for match in re.finditer(sirna_pattern, method_text, re.IGNORECASE):
            parameters["siRNA"].append({
                "parameter": "siRNA",
                "value": match.group(0),
                "experiment_type": "Transfection"
            })

    if "cell_migration" in detected_types:
        cell_lines = ['HEK293', 'HeLa', 'MCF-7', 'AGS', 'NCI-N87', 'MKN-45', 'MGC-803', 'HGC-27']
        for line in cell_lines:
            if line.lower() in method_text_lower:
                parameters["cell_lines"].append({
                    "parameter": "Cell Line",
                    "value": line,
                    "experiment_type": "Cell Migration"
                })

    # Extract temperatures for all detected types
    temp_pattern = r'(\d+)\s*°C'
    for match in re.finditer(temp_pattern, method_text):
        temp = int(match.group(1))
        parameters["temperatures"].append({
            "parameter": "Temperature",
            "value": f"{temp}°C",
            "experiment_type": detected_types[0] if detected_types else "Unknown"
        })

    # Extract durations for all detected types
    duration_pattern = r'(\d+)\s*(hours?|hrs?|minutes?|mins?|days?|overnight)'
    for match in re.finditer(duration_pattern, method_text, re.IGNORECASE):
        duration = match.group(0)
        parameters["durations"].append({
            "parameter": "Duration",
            "value": duration,
            "experiment_type": detected_types[0] if detected_types else "Unknown"
        })

    # Extract volumes for all detected types
    volume_pattern = r'(\d+\.?\d*)\s*(μL|L|ml)'
    for match in re.finditer(volume_pattern, method_text, re.IGNORECASE):
        vol = match.group(0)
        parameters["volumes"].append({
            "parameter": "Volume",
            "value": vol,
            "experiment_type": detected_types[0] if detected_types else "Unknown"
        })

    # Extract ratios for luciferase (control vectors)
    if "luciferase" in detected_types:
        ratio_pattern = r'(\d+\.?\d*):?\s*(\d+\.?\d*)'
        for match in re.finditer(ratio_pattern, method_text):
            ratio = match.group(0)
            parameters["ratios"].append({
                "parameters": "Control Vector Ratio",
                "value": ratio,
                "experiment_type": "Luciferase"
            })

    # Extract inhibitors
    inhibitor_pattern = r'([A-Z][a-zA-Z0-9\s-]+(?:inhibitor|antagonist)'
    for match in re.finditer(inhibitor_pattern, method_text):
        inhibitor = match.group(0)
        parameters["inhibitors"].append({
            "parameter": f"{inhibitor} (Inhibitor)",
            "value": "Present",
            "experiment_type": detected_types[0] if detected_types else "Unknown"
        })

    return {
        "method_name": detected_types[0] if detected_types else "Unknown",
        "experiment_type": detected_types[0] if detected_types else "Unknown",
        "detected_types": detected_types,
        "parameters": parameters
    }


def main():
    """Main function for testing."""
    if len(sys.argv) < 2:
        print("Usage: python experiment_classifier.py <markdown_file>")
        sys.exit(1)

    md_file = sys.argv[1]
    
    with open(md_file, 'r', encoding='utf-8') as f:
        text = f.read()

    result = identify_experiment_types(text)
    
    print("=== Detected Experiment Types ===")
    for exp_type, data in result["experiment_details"].items():
        if data["found"]:
            print(f"- {data['name']}: Found")
        else:
            print(f"- {data['name']}: Not Found")
    
    if result["detected_types"]:
        print(f"\nPrimary experiment type: {result['method_name']}")
        print(f"All detected types: {', '.join(result['detected_types'])}")
    else:
        print("\nNo known experiment types detected")


if __name__ == "__main__":
    main()
