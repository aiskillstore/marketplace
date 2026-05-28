#!/usr/bin/env python3
"""
Discharge Summary Writer
Generates hospital discharge summaries from patient data.

Usage:
    python main.py --input patient_data.json --output discharge_summary.md
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def load_patient_data(input_path: str) -> Dict[str, Any]:
    """Load patient data from JSON file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_patient_data(data: Dict[str, Any]) -> List[str]:
    """Validate required fields in patient data."""
    errors = []
    required_sections = [
        'patient_info', 'admission_data', 'hospital_course',
        'discharge_status', 'medications', 'follow_up'
    ]
    
    for section in required_sections:
        if section not in data:
            errors.append(f"Missing required section: {section}")
    
    if 'patient_info' in data:
        required_info = ['name', 'gender', 'age', 'medical_record_number', 'department']
        for field in required_info:
            if field not in data['patient_info']:
                errors.append(f"Missing patient_info.{field}")
    
    return errors


def format_patient_info(info: Dict[str, Any]) -> str:
    """Format patient information section."""
    return f"""## Basic patient information / Patient Information

| project / Item | content / Value |
|------------|-------------|
| Name / Name | {info.get('name', 'N/A')} |
| gender / Gender | {info.get('gender', 'N/A')} |
| age / Age | {info.get('age', 'N/A')} age |
| Hospital number / MRN | {info.get('medical_record_number', 'N/A')} |
| Admission date / Admission Date | {info.get('admission_date', 'N/A')} |
| discharge date / Discharge Date | {info.get('discharge_date', 'N/A')} |
| length of stay / Length of Stay | {info.get('hospital_stay_days', 'N/A')} sky |
| Department / Department | {info.get('department', 'N/A')} |
| Physician in Charge / Attending Physician | {info.get('attending_physician', 'N/A')} |
"""


def format_admission_data(data: Dict[str, Any]) -> str:
    """Format admission information section."""
    diagnoses = data.get('admission_diagnosis', [])
    diagnosis_text = '\n'.join([f"- {d}" for d in diagnoses]) if diagnoses else '-'
    
    return f"""## Admission status / Admission Information

### Chief complaint / Chief Complaint
{data.get('chief_complaint', 'N/A')}

### History of present illness / Present Illness History
{data.get('present_illness_history', 'N/A')}

### past history / Past Medical History
{data.get('past_medical_history', 'N/A')}

### Physical examination on admission / Physical Examination
{data.get('physical_examination', 'N/A')}

### Admission diagnosis / Admission Diagnosis
{diagnosis_text}
"""


def format_hospital_course(course: Dict[str, Any]) -> str:
    """Format hospital course section."""
    procedures = course.get('procedures_performed', [])
    procedures_text = '\n'.join([f"- {p}" for p in procedures]) if procedures else '-'
    
    complications = course.get('complications', [])
    complications_text = '\n'.join([f"- {c}" for c in complications]) if complications else 'None / None'
    
    consultations = course.get('consultations', [])
    consultations_text = '\n'.join([f"- {c}" for c in consultations]) if consultations else '-'
    
    return f"""## Inpatient diagnosis and treatment process / Hospital Course

### Treatment process / Treatment Summary
{course.get('treatment_summary', 'N/A')}

### Important test results / Significant Findings
{course.get('significant_findings', 'N/A')}

### perform surgery/operate / Procedures Performed
{procedures_text}

### Consultation records / Consultations
{consultations_text}

### complication / Complications
{complications_text}
"""


def format_discharge_status(status: Dict[str, Any]) -> str:
    """Format discharge status section."""
    diagnoses = status.get('discharge_diagnosis', [])
    diagnosis_text = '\n'.join([f"- {d}" for d in diagnoses]) if diagnoses else '-'
    
    return f"""## Discharge status / Discharge Status

### discharge diagnosis / Discharge Diagnosis
{diagnosis_text}

### Condition at discharge / Discharge Condition
{status.get('discharge_condition', 'N/A')}
"""


def format_medications(meds: Dict[str, Any]) -> str:
    """Format discharge medications section."""
    medications = meds.get('discharge_medications', [])
    
    if not medications:
        return """## Discharge Medications

None / None"""
    
    med_lines = []
    for i, med in enumerate(medications, 1):
        med_lines.append(
            f"{i}. **{med.get('name', 'N/A')}** | "
            f"dose: {med.get('dosage', 'N/A')} | "
            f"Frequency: {med.get('frequency', 'N/A')} | "
            f"way: {med.get('route', 'N/A')} | "
            f"Course of treatment: {med.get('duration', 'N/A')}"
        )
    
    return f"""## Discharge with medicine / Discharge Medications

""" + '\n'.join(med_lines) + """**Important Tips**: Please take the medicine on time as directed by your doctor, and seek medical advice in time if you feel unwell.  
**Important**: Please take medications as prescribed. Seek medical attention if adverse effects occur."""


def format_follow_up(follow_up: Dict[str, Any]) -> str:
    """Format follow-up instructions section."""
    appointments = follow_up.get('follow_up_appointments', [])
    appointments_text = '\n'.join([f"- {a}" for a in appointments]) if appointments else '-'
    
    warning_signs = follow_up.get('warning_signs', [])
    warning_text = '\n'.join([f"- {w}" for w in warning_signs]) if warning_signs else '-'
    
    return f"""## Discharge orders / Discharge Instructions

### Follow-up arrangements / Follow-up Appointments
{appointments_text}

### Things to note / Instructions
{follow_up.get('instructions', 'N/A')}

### activity restrictions / Activity Restrictions
{follow_up.get('activity_restrictions', 'N/A')}

### dietary guidance / Diet Instructions
{follow_up.get('diet_instructions', 'N/A')}

### warning symptoms（Need immediate medical attention）/ Warning Signs (Seek Immediate Care)
{warning_text}
"""


def generate_summary(data: Dict[str, Any], language: str = 'zh') -> str:
    """Generate complete discharge summary."""
    patient_info = data.get('patient_info', {})
    admission_data = data.get('admission_data', {})
    hospital_course = data.get('hospital_course', {})
    discharge_status = data.get('discharge_status', {})
    medications = data.get('medications', {})
    follow_up = data.get('follow_up', {})
    
    # Calculate hospital stay if not provided
    if 'hospital_stay_days' not in patient_info and 'admission_date' in patient_info and 'discharge_date' in patient_info:
        try:
            admit = datetime.strptime(patient_info['admission_date'], '%Y-%m-%d')
            discharge = datetime.strptime(patient_info['discharge_date'], '%Y-%m-%d')
            patient_info['hospital_stay_days'] = (discharge - admit).days
        except (ValueError, TypeError):
            patient_info['hospital_stay_days'] = 'N/A'
    
    title = "DISCHARGE SUMMARY / DISCHARGE SUMMARY"
    disclaimer = """---

**⚠️ IMPORTANT DISCLAIMER**

This document is generated by an AI-assisted system and is for reference only. The final discharge summary must be reviewed and signed by the physician in charge before it can take effect.  
This document was generated by an AI-assisted system for reference only. The final discharge summary must be reviewed and signed by the attending physician before it becomes effective.

---"""
    
    sections = [
        f"# {title}",
        disclaimer,
        format_patient_info(patient_info),
        format_admission_data(admission_data),
        format_hospital_course(hospital_course),
        format_discharge_status(discharge_status),
        format_medications(medications),
        format_follow_up(follow_up),
        """---

## Physician Signature / Physician Signature

| | |
|---|---|
| Attending Physician | _______________________ |
| Signature Date | _______________________ |
| Physician License Number / License Number | _______________________ |

---

*Document Generated: {timestamp}*""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    
    return '\n\n'.join(sections)


def generate_structured_output(data: Dict[str, Any]) -> str:
    """Generate structured output format."""
    return generate_summary(data, 'zh')


def generate_json_output(data: Dict[str, Any]) -> str:
    """Generate JSON output format."""
    output = {
        "document_type": "discharge_summary",
        "generated_at": datetime.now().isoformat(),
        "requires_physician_review": True,
        "data": data
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Generate hospital discharge summaries from patient data'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to patient data JSON file'
    )
    parser.add_argument(
        '--output', '-o',
        default='discharge_summary.md',
        help='Output file path (default: discharge_summary.md)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['standard', 'structured', 'json'],
        default='standard',
        help='Output format (default: standard)'
    )
    parser.add_argument(
        '--language', '-l',
        choices=['zh', 'en'],
        default='zh',
        help='Output language (default: zh)'
    )
    
    args = parser.parse_args()
    
    # Load and validate data
    try:
        data = load_patient_data(args.input)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        return 1
    
    validation_errors = validate_patient_data(data)
    if validation_errors:
        print("Validation errors found:")
        for error in validation_errors:
            print(f"  - {error}")
        return 1
    
    # Generate output
    if args.format == 'json':
        output = generate_json_output(data)
    elif args.format == 'structured':
        output = generate_structured_output(data)
    else:
        output = generate_summary(data, args.language)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Discharge summary generated: {output_path.absolute()}")
    print("⚠️  WARNING: This document requires physician review before use.")
    
    return 0


if __name__ == '__main__':
    exit(main())
