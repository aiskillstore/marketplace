#!/usr/bin/env python3
"""
Extract experimental method details from markdown format of research papers.
Enhanced version with detailed extraction for experimental design, materials, equipment, samples, and key steps.
"""

import re
import json
import sys
from pathlib import Path

def extract_method_section(markdown_content):
    """
    Extract the methods section from markdown content.

    Args:
        markdown_content: Full markdown text of paper

    Returns:
        String containing the methods section, or None if not found
    """
    # Look for Methods section with various heading levels
    patterns = [
        r'#+\s*[Mm]ethods?\s*\n(.*?)(?=#+\s*\w|\Z)',
        r'#+\s*[Mm]aterials?\s+and\s+[Mm]ethods?\s*\n(.*?)(?=#+\s*\w|\Z)',
        r'#+\s*[Ee]xperimental\s+[Pp]rocedures?\s*\n(.*?)(?=#+\s*\w|\Z)',
        r'#+\s*[Pp]rotocols?\s*\n(.*?)(?=#+\s*\w|\Z)',
    ]

    for pattern in patterns:
        match = re.search(pattern, markdown_content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)

    return None

def extract_experimental_design(method_text):
    """
    Extract experimental design information including controls, replicates, randomization, etc.

    Args:
        method_text: Methods section text

    Returns:
        Dictionary of experimental design information
    """
    design = {
        "control_groups": [],
        "experimental_groups": [],
        "randomization": None,
        "blinding": None,
        "replicates": {},
        "sample_size": None,
        "block_design": None,
    }

    # Extract control groups
    control_patterns = [
        r'(?:control|control\s+group|negative\s+control)\s*(?:of|:|=)?\s*([^.;\n]{5,50})',
        r'(?:wild\s*type|WT|wild[\-]type)\s*(?:of|:|=)?\s*([^.;\n]{5,50})',
    ]
    for pattern in control_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            control = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
            if control and len(control) > 2:
                design["control_groups"].append(control)

    # Extract experimental groups
    group_pattern = r'(?:experimental\s+group|treatment\s+group|study\s+group)\s*(?:of|:|=)?\s*([^.;\n]{5,50})'
    for match in re.finditer(group_pattern, method_text, re.IGNORECASE):
        group_name = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
        if group_name and len(group_name) > 2:
            design["experimental_groups"].append(group_name)

    # Extract randomization
    random_patterns = [
        r'(?:random(?:ly|ized)?|randomized)\s*(?:of|:|=)?\s*([^.;\n]{5,50})',
        r'(?:random(?:ly|ized)?|randomized)\s+(?:block|complete)',
    ]
    for pattern in random_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            if len(match.groups()) > 0:
                design["randomization"] = match.group(1).strip()
            else:
                design["randomization"] = "yes"

    # Extract blinding
    blind_patterns = [
        r'(?:blind|blinding|masked)\s*(?:of|:|=)?\s*([^.;\n]{5,50})',
        r'(?:double\s*blind|single\s*blind|triple\s*blind)',
    ]
    for pattern in blind_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            if len(match.groups()) > 0:
                design["blinding"] = match.group(1).strip()
            else:
                design["blinding"] = "yes"

    # Extract replicates
    replicate_pattern = r'(?:n|replicate|replication)\s*=\s*(\d+)\s*(?:independent|technical|biological)?'
    for match in re.finditer(replicate_pattern, method_text, re.IGNORECASE):
        value = int(match.group(1))
        rep_type = "independent" if "independent" in match.group(0).lower() else "technical"
        design["replicates"][rep_type] = value

    # Extract sample size
    sample_pattern = r'(?:sample\s*size|n\s*=\s*)\s*(\d+)\s*(?:per\s*group|subjects|animals|patients)?'
    for match in re.finditer(sample_pattern, method_text, re.IGNORECASE):
        design["sample_size"] = int(match.group(1))

    # Extract block design
    block_pattern = r'(?:block\s*design|randomized\s*block)\s*(?:of|:|=)?\s*([^.;\n]{5,50})'
    for match in re.finditer(block_pattern, method_text, re.IGNORECASE):
        block = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
        if block and len(block) > 2:
            design["block_design"] = block

    return design

def extract_materials_detailed(method_text):
    """
    Extract detailed materials list including chemicals, reagents, kits, and media.

    Args:
        method_text: Methods section text

    Returns:
        Dictionary of detailed materials
    """
    materials = {
        "chemicals": [],
        "kits": [],
        "media": [],
        "culture_bases": [],
        "buffers": [],
        "solvents": [],
    }

    # Extract chemicals with details
    chemical_pattern = r'([A-Z][a-zA-Z0-9\s\-\s]*)\s*(?:from|purchased\s+from|obtained\s+from)?\s*([^.;\n]{5,100})(?:\s*\(|,\s*cat\.\s*no\.)?'
    for match in re.finditer(chemical_pattern, method_text):
        chemical_name = match.group(1).strip()
        supplier = match.group(2).strip() if len(match.groups()) > 1 else "Unknown"
        if chemical_name:
            materials["chemicals"].append({"name": chemical_name, "supplier": supplier})

    # Extract kits
    kit_pattern = r'([A-Z][a-zA-Z ]+)(?:kit|assay|test)'
    for match in re.finditer(kit_pattern, method_text, re.IGNORECASE):
        kit_name = match.group(1).strip()
        if kit_name:
            materials["kits"].append({"name": kit_name, "manufacturer": "Unknown"})

    # Extract media and culture bases
    media_patterns = [
        r'(?:DMEM|EMEM|RPMI|F12|MEM|L\s*-\s*15|BME|Ham\'s\s*F-10|M199|M199|PBS|HBSS)\s*(?:medium|media)',
        r'(?:fetal\s+bovine\s+serum|FBS|BSA)\s*(\d+\.?\d*%?)',
    ]
    for pattern in media_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            materials["media"].append(match.group(0))

    # Extract buffers
    buffer_pattern = r'([A-Z][a-zA-Z ]+)(?:buffer|solution)'
    for match in re.finditer(buffer_pattern, method_text, re.IGNORECASE):
        buffer_name = match.group(1).strip()
        materials["buffers"].append({"name": buffer_name, "components": "Unknown"})

    # Extract solvents
    solvent_pattern = r'\b(?:acetonitrile|methanol|ethanol|isopropanol|DMSO|chloroform|dichloromethane|THF|toluene|hexane|diethyl\s*ether)\b'
    solvents = re.findall(solvent_pattern, method_text, re.IGNORECASE)
    materials["solvents"] = list(set(solvents))

    return materials

def extract_equipment_detailed(method_text):
    """
    Extract detailed equipment and instrument information.

    Args:
        method_text: Methods section text

    Returns:
        Dictionary of detailed equipment information
    """
    equipment = {
        "instruments": [],
        "models": {},
        "manufacturers": {},
        "settings": {},
    }

    # Extract equipment with manufacturer and model
    equip_pattern = r'([A-Z][a-zA-Z0-9\s\-\s]+(?:model|machine|system|instrument|device|apparatus)?)(?:\s+(?:from|by|manufactured\s+by)?)?\s*([^.;\n]{5,100})?(?:\s+model\s+([^.;\n]{5,50}))?'
    for match in re.finditer(equip_pattern, method_text, re.IGNORECASE):
        equip_name = match.group(1).strip()
        manufacturer = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else "Unknown"
        model = match.group(3).strip() if len(match.groups()) > 2 and match.group(3) else ""
        if equip_name:
            equipment["instruments"].append(equip_name)
            if manufacturer:
                equipment["manufacturers"][equip_name] = manufacturer
            if model:
                equipment["models"][equip_name] = model

    # Extract instrument settings
    setting_patterns = [
        r'(?:centrifuge?|ultracentrifuge?)\s+was\s+set\s+to\s+(\d+)\s*([kK]?M?)(?:rpm|g|rcf)',
        r'(?:incubator?|oven?)\s+(?:temperature|temp)\s+was\s+maintained\s+at\s+(\d+)\s*°C',
        r'(?:spectrophotometer?)\s+(?:wavelength|absorbance|emission)\s+(?:at|of)?\s+(\d+)\s*nm',
    ]
    for pattern in setting_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            instrument = re.search(r'(centrifuge|incubator|oven|spectrophotometer)', match.group(0), re.IGNORECASE)
            if instrument:
                instrument_type = instrument.group(0)
                setting_value = match.group(1)
                unit = match.group(2) if len(match.groups()) > 1 else ""
                equipment["settings"][instrument_type] = f"{setting_value} {unit}"

    return equipment

def extract_sample_information(method_text):
    """
    Extract sample information including source, quantity, processing, and ethics.

    Args:
        method_text: Methods section text

    Returns:
        Dictionary of sample information
    """
    samples = {
        "sources": [],
        "quantities": {},
        "processing_methods": [],
        "ethics_approval": None,
        "consent": None,
        "storage_conditions": [],
    }

    # Extract sample sources
    source_patterns = [
        r'(?:samples?\s+(?:were|are)?\s+(?:obtained|purchased|collected|harvested|sourced|provided)\s+(?:from|at)?\s*([^.;\n]{10,150})',
        r'(?:patients?|subjects?|animals?|cells?)\s+(?:were|are)?\s+(?:enrolled|recruited|selected)\s+(?:from|at)?\s*([^.;\n]{10,150})',
    ]
    for pattern in source_patterns:
        try:
            for match in re.finditer(pattern, method_text, re.IGNORECASE):
                source = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
                if source and len(source) > 3:
                    samples["sources"].append(source)
        except:
            pass

    # Extract sample quantities
    quantity_pattern = r'(\d+\.?\d*)\s*(?:mg|g|kg|μL|mL|L|cells?)\s*(?:of|per)?\s*([^.;\n]{5,50})'
    for match in re.finditer(quantity_pattern, method_text, re.IGNORECASE):
        value = match.group(1)
        sample_type = match.group(2)
        samples["quantities"][sample_type] = f"{value} units"

    # Extract processing methods
    processing_patterns = [
        r'(?:samples?\s+(?:were|are)?\s+(?:frozen|fixed|fresh|dried|lyophilized)|freshly\s+prepared)',
        r'(?:samples?\s+(?:were|are)?\s+(?:centrifuged|filtered|purified|extracted|dissolved))',
    ]
    for pattern in processing_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            method = match.group(0)
            if method not in samples["processing_methods"]:
                samples["processing_methods"].append(method)

    # Extract ethics approval
    ethics_patterns = [
        r'(?:study\s+was\s+approved\s+by\s+ethics\s+committee\s+approval)\s+(?:of|:|=)?\s*([^.;\n]{10,50})',
        r'(?:IRB|IACUC|ethics\s+committee)\s+(?:approval|number|ref|code)\s*(?:of|:|=)?\s*([^.;\n]{10,50})',
    ]
    for pattern in ethics_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            approval = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
            if approval and len(approval) > 2:
                samples["ethics_approval"] = approval

    # Extract consent
    consent_patterns = [
        r'(?:informed\s+consent|consent\s+was\s+obtained)\s*(?:from|by)?\s*([^.;\n]{5,50})',
        r'(?:written\s+consent|verbal\s+consent)',
    ]
    for pattern in consent_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            consent_type = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
            if consent_type not in samples["consent"] if samples["consent"] else None:
                samples["consent"] = consent_type

    # Extract storage conditions
    storage_patterns = [
        r'(?:stored\s+at|kept\s+at)\s+(\d+)?\s*(?:-?\s*\d+)?\s*°C',
        r'(?:stored\s+in|kept\s+in)\s+(?:liquid\s+nitrogen|LN2|-?\s*80\s*°C\s*freezer|refrigerator)',
    ]
    for pattern in storage_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            storage = match.group(0)
            if storage not in samples["storage_conditions"]:
                samples["storage_conditions"].append(storage)

    return samples

def extract_key_steps(method_text):
    """
    Extract and structure key experimental steps.

    Args:
        method_text: Methods section text

    Returns:
        Dictionary of structured steps
    """
    steps = {
        "step_sequence": [],
        "numbered_steps": {},
    }

    # Split methods into sections based on headings or numbering
    section_patterns = [
        r'#+\s*(?:step\s*(\d+)|phase\s*(\d+)|stage\s*(\d+))',
        r'(\d+)\.\s*[A-Z][^.;\n]{10,100}',
    ]
    extracted_steps = []
    for pattern in section_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            step_number = match.group(1)
            step_content = match.group(0) if len(match.groups()) > 1 else ""
            
            # Extract step type (preparation, reaction, purification, detection)
            step_type = "unknown"
            if "prepare" in step_content.lower() or "equilibrate" in step_content.lower():
                step_type = "preparation"
            elif "incubat" in step_content.lower() or "react" in step_content.lower():
                step_type = "reaction"
            elif "purif" in step_content.lower() or "separat" in step_content.lower():
                step_type = "purification"
            elif "detect" in step_content.lower() or "measure" in step_content.lower():
                step_type = "detection"
            
            steps["numbered_steps"][step_number] = {
                "type": step_type,
                "description": step_content[:200],
            }
            extracted_steps.append(step_number)

    # Also extract bullet-point steps
    bullet_patterns = [
        r'[-*]\s+([A-Z][^.;\n]{5,100})',
        r'\d+\.\s+([A-Z][^.;\n]{5,100})',
    ]
    for pattern in bullet_patterns:
        for match in re.finditer(pattern, method_text, re.IGNORECASE):
            step_desc = match.group(1)
            if len(step_desc) > 10:
                step_type = "unknown"
                if "prepare" in step_desc.lower():
                    step_type = "preparation"
                elif "incubat" in step_desc.lower():
                    step_type = "reaction"
                elif "purif" in step_desc.lower():
                    step_type = "purification"
                elif "detect" in step_desc.lower():
                    step_type = "detection"
                
                step_num = len(extracted_steps) + 1
                steps["numbered_steps"][str(step_num)] = {
                    "type": step_type,
                    "description": step_desc,
                }
                extracted_steps.append(str(step_num))

    steps["step_sequence"] = sorted(extracted_steps)
    return steps

def extract_parameters(method_text):
    """
    Extract experimental parameters from methods text.

    Args:
        method_text: Methods section text

    Returns:
        Dictionary of extracted parameters
    """
    parameters = {
        "method_name": None,
        "reagents": [],
        "concentrations": {},
        "ratios": {},
        "temperatures": {},
        "durations": {},
        "volumes": {},
        "cell_lines": [],
        "organisms": [],
        "equipment": [],
        "controls": [],
        "replications": None,
    }

    # Extract concentrations (e.g., "10 mM", "5 μg/mL", "1 nM")
    conc_pattern = r'(\d+\.?\d*)\s*(mM|μM|nM|mg/mL|μg/mL|ng/mL|%|v/v)'
    for match in re.finditer(conc_pattern, method_text):
        value, unit = match.groups()
        parameter_name = identify_parameter_context(method_text, match.start())
        if parameter_name:
            parameters["concentrations"][parameter_name] = f"{value} {unit}"

    # Extract temperatures (e.g., "37°C", "25°C")
    temp_pattern = r'(\d+)\s*°C|(\d+)\s*Celsius'
    for match in re.finditer(temp_pattern, method_text, re.IGNORECASE):
        temp = match.group(0)
        parameter_name = identify_parameter_context(method_text, match.start())
        if parameter_name:
            parameters["temperatures"][parameter_name] = temp

    # Extract durations (e.g., "2 hours", "30 min", "overnight")
    duration_pattern = r'(\d+)\s*(hours?|hrs?|minutes?|mins?|days?|overnight)'
    for match in re.finditer(duration_pattern, method_text, re.IGNORECASE):
        duration = match.group(0)
        parameter_name = identify_parameter_context(method_text, match.start())
        if parameter_name:
            parameters["durations"][parameter_name] = duration

    # Extract ratios (e.g., "1:2", "1:1:1")
    ratio_pattern = r'(\d+)\s*:\s*(\d+)(?:\s*:\s*(\d+))?'
    for match in re.finditer(ratio_pattern, method_text):
        ratio = match.group(0)
        parameter_name = identify_parameter_context(method_text, match.start())
        if parameter_name:
            parameters["ratios"][parameter_name] = ratio

    # Extract volumes (e.g., "100 μL", "50 mL")
    volume_pattern = r'(\d+\.?\d*)\s*(μL|L|mL|ml)'
    for match in re.finditer(volume_pattern, method_text, re.IGNORECASE):
        volume = match.group(0)
        parameter_name = identify_parameter_context(method_text, match.start())
        if parameter_name:
            parameters["volumes"][parameter_name] = volume

    # Extract cell lines
    cell_pattern = r'\b(?:HEK293|HeLa|CHO|MDCK|Vero|COS-7|293T|NIH-3T3|RAW264\.7)\b'
    parameters["cell_lines"] = list(set(re.findall(cell_pattern, method_text, re.IGNORECASE)))

    # Extract organisms
    org_pattern = r'\b(?:E\. coli|mouse|rat|human|zebrafish|Drosophila|yeast)\b'
    parameters["organisms"] = list(set(re.findall(org_pattern, method_text, re.IGNORECASE)))

    # Extract method name from first sentence
    sentences = method_text.split('. ')
    if sentences:
        parameters["method_name"] = sentences[0][:200]

    return parameters

def identify_parameter_context(text, position):
    """
    Identify what parameter is being described based on surrounding text.

    Args:
        text: Full text
        position: Position of the parameter value

    Returns:
        Parameter name or None
    """
    # Look for context within 100 characters before and after
    window = 200
    start = max(0, position - window)
    end = min(len(text), position + window)
    context = text[start:end].lower()

    # Common parameter indicators
    keywords = {
        "substrate": ["substrate", "enzyme", "protein", "antigen"],
        "inhibitor": ["inhibitor", "drug", "compound", "small molecule"],
        "antibody": ["antibody", "antiserum"],
        "temperature": ["temperature", "incubation", "reaction", "annealing"],
        "time": ["time", "incubation", "duration", "reaction time"],
        "concentration": ["concentration", "dilution", "stock"],
    }

    for param, indicators in keywords.items():
        if any(indicator in context for indicator in indicators):
            return param

    return "unknown"

def save_method_details(method_data, output_path):
    """
    Save extracted method details to JSON file.

    Args:
        method_data: Dictionary of method details
        output_path: Path to save JSON file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(method_data, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_method_section.py <input_markdown> <output_json>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Read markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract methods section
    method_text = extract_method_section(content)

    if not method_text:
        print("Warning: Could not find methods section, using full text", file=sys.stderr)
        method_text = content

    # Extract all information
    parameters = extract_parameters(method_text)
    design = extract_experimental_design(method_text)
    materials = extract_materials_detailed(method_text)
    equipment = extract_equipment_detailed(method_text)
    samples = extract_sample_information(method_text)
    steps = extract_key_steps(method_text)

    # Combine all extracted data
    method_data = {
        **parameters,
        "experimental_design": design,
        "materials": materials,
        "equipment": equipment,
        "samples": samples,
        "key_steps": steps,
        "full_text": method_text,
    }

    # Save to JSON
    save_method_details(method_data, output_file)

    print(f"Method details saved to: {output_file}")
    print(f"  - Parameters: {len(parameters['concentrations']) + len(parameters['temperatures']) + len(parameters['durations'])}")
    print(f"  - Materials: {len(materials['chemicals']) + len(materials['kits']) + len(materials['media'])}")
    print(f"  - Equipment: {len(equipment['instruments'])}")
    print(f"  - Design: {len(design['control_groups']) + len(design['experimental_groups'])}")
    print(f"  - Samples: {len(samples['sources'])}")
    print(f"  - Steps: {len(steps['step_sequence'])}")
    sys.exit(0)


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
        "luciferase": {"name": "Luciferase Assay", "parameters": [], "found": False},
        "qpcr": {"name": "qPCR", "parameters": [], "found": False},
        "immunofluorescence": {"name": "Immunofluorescence", "parameters": [], "found": False},
        "co_ip": {"name": "Co-IP", "parameters": [], "found": False}
    }

    method_text_lower = method_text.lower()

    # Western Blot detection
    western_keywords = [
        r'western\s+blot',
        r'western\s*-\s*blot',
        r'immunoblot',
        r'protein\s+extraction',
        r'sds\s*-\s*page'
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
        r'mtt\s+assay',
        r'mtt\s*-\s*assay',
        r'eduf\s+incorporation',
        r'wst\s*-\s*1',
        r'brd(?:u|ezo)',
        r'trypan\s+blue',
        r'mts',
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
        r'boyden\s+chamber',
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
        r'tunel\s+assay',
        r'flow\s+cytometry',
        r'dapi\s+staining',
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
        r'renilla\s+luciferase',
        r'firefly\s+luciferase'
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
        r'taqman\s+assay',
        r'sybr\s+green'
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
        r'fluorescent\s+microscopy',
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

    # Associate parameters with experiment types
    # Concentrations
    for exp_type, exp_data in experiment_types.items():
        if exp_data["found"]:
            for param in concentrations:
                if "antibody" in param["parameter"].lower() and "western" in param["parameter"].lower():
                    experiment_types["western_blot"]["parameters"].append(param)
                elif "transfection" in param["parameter"].lower():
                    experiment_types["transfection"]["parameters"].append(param)
                elif "luciferase" in param["parameter"].lower():
                    experiment_types["luciferase"]["parameters"].append(param)
                elif "qpcr" in param["parameter"].lower():
                    experiment_types["qpcr"]["parameters"].append(param)
            if "temperature" in param["parameter"].lower():
                exp_data["parameters"].append(param)

    # Temperatures (all found experiment types)
    for param in temperatures:
        for exp_type, exp_data in experiment_types.items():
            if exp_data["found"]:
                exp_data["parameters"].append(param)

    # Durations
    for param in durations:
        if "antibody" in param["parameter"].lower():
            experiment_types["western_blot"]["parameters"].append(param)
        elif "transfection" in param["parameter"].lower():
            experiment_types["transfection"]["parameters"].append(param)
        elif "luciferase" in param["parameter"].lower():
            experiment_types["luciferase"]["parameters"].append(param)
        elif "qpcr" in param["parameter"].lower():
            experiment_types["qpcr"]["parameters"].append(param)
        for exp_type, exp_data in experiment_types.items():
            if exp_data["found"]:
                exp_data["parameters"].append(param)

    # Ratios
    for param in ratios:
        if "luciferase" in param["parameter"].lower():
            experiment_types["luciferase"]["parameters"].append(param)
        elif "qpcr" in param["parameter"].lower():
            experiment_types["qpcr"]["parameters"].append(param)

    # Volumes
    for param in volumes:
        if "transfection" in param["parameter"].lower():
            experiment_types["transfection"]["parameters"].append(param)
        elif "luciferase" in param["parameter"].lower():
            experiment_types["luciferase"]["parameters"].append(param)
        elif "qpcr" in param["parameter"].lower():
            experiment_types["qpcr"]["parameters"].append(param)

    return {
        "detected_types": [exp_type for exp_type, data in experiment_types.items() if data["found"]],
        "experiment_details": {exp_type: data for exp_type, data in experiment_types.items()}
    }


def extract_method_by_experiment_type(method_text, experiment_types_info):
    """
    Extract parameters and group them by experiment type.

    Args:
        method_text: Methods section text
        experiment_types_info: Dictionary with detected experiment types

    Returns:
        Dictionary with parameters grouped by experiment type
    """
    method_data = {
        "method_name": "",
        "experiment_types": {},
        "concentrations": {},
        "temperatures": {},
        "durations": {},
        "ratios": {},
        "volumes": {},
        "equipment": {"instruments": [], "models": {}, "manufacturers": {}, "settings": {}},
        "materials": {"chemicals": [], "kits": [], "media": [], "culture_bases": [], "buffers": [], "solvents": []},
        "design": {"control_groups": [], "experimental_groups": [], "randomized": False, "blinding": False, "replicates": {}, "sample_size": 0, "block_design": ""},
        "samples": {"sources": [], "quantities": {}, "processing": [], "ethics": "", "consent": "", "storage": ""}
    }

    # Add method name from experiment types
    if "western_blot" in experiment_types_info["detected_types"]:
        method_data["method_name"] = "Western Blot"
    elif "transfection" in experiment_types_info["detected_types"]:
        method_data["method_name"] = "Transfection"
    elif "cell_proliferation" in experiment_types_info["detected_types"]:
        method_data["method_name"] = "Cell Proliferation Assay"
    elif "cell_migration" in experiment_types_info["detected_types"]:
        method_data["method_name"] = "Cell Migration Assay"
    elif "cell_apoptosis" in experiment_types_info["detected_types"]:
        method_data["method_name"] = "Cell Apoptosis Assay"
    elif "chip_seq" in experiment_types_info["detected_types"]:
        method_data["method_name"] = "ChIP-seq"
    elif "luciferase" in experiment_types_info["detected_types"]:
        method_data["method_name"] = "Luciferase Reporter Assay"
    elif "qpcr" in experiment_types_info["detected_types"]:
        method_data["method_name"] = "qPCR"

    # Group existing extracted parameters by experiment type
    for exp_type, exp_data in experiment_types_info["experiment_details"].items():
        if exp_data["found"]:
            method_data["experiment_types"][exp_type] = {
                "name": exp_data["name"],
                "parameters": exp_data["parameters"]
            }

    # Also add parameters to their respective categories
    for param in exp_data["parameters"]:
        if "concentration" in param["parameter"].lower():
            method_data["concentrations"][param["parameter"]] = param
        elif "temperature" in param["parameter"].lower():
            method_data["temperatures"][param["parameter"]] = param
        elif "duration" in param["parameter"].lower():
            method_data["durations"][param["parameter"]] = param

    return method_data

if __name__ == "__main__":
    main()
