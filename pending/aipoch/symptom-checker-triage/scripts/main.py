#!/usr/bin/env python3
"""
Symptom Checker Triage (ID: 165)
Recommends triage level (emergency vs outpatient) based on common symptom red flags
"""

import sys
import json
import argparse
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TriageLevel(Enum):
    EMERGENCY = "emergency"      # Life-threatening
    URGENT = "urgent"            # Urgent but not immediately life-threatening
    OUTPATIENT = "outpatient"    # Non-urgent


@dataclass
class TriageResult:
    triage_level: str
    confidence: float
    red_flags: List[str]
    reason: str
    recommendation: str
    department: str
    warning: str = "This is an AI-assisted recommendation and cannot replace professional medical diagnosis"


# Red flag definitions: symptom keywords -> (red flag name, triage level, weight, department suggestion, reason)
RED_FLAGS = {
    # Cardiovascular system - urgent
    "chest pain": ("Chest Pain", TriageLevel.EMERGENCY, 0.95, "Emergency/Cardiology", "Chest pain may indicate myocardial infarction, aortic dissection, or pulmonary embolism"),
    "chest tightness": ("Chest Tightness", TriageLevel.EMERGENCY, 0.85, "Emergency/Cardiology", "Chest tightness may be a presentation of angina or myocardial infarction"),
    "palpitations": ("Palpitations", TriageLevel.URGENT, 0.70, "Cardiology", "Palpitations may indicate cardiac arrhythmia"),
    "syncope": ("Syncope", TriageLevel.EMERGENCY, 0.90, "Emergency/Neurology", "Syncope may suggest serious arrhythmia or cerebrovascular accident"),
    "coma": ("Coma", TriageLevel.EMERGENCY, 1.0, "Emergency", "Coma is a life-threatening emergency"),

    # Respiratory system - urgent
    "dyspnea": ("Dyspnea", TriageLevel.EMERGENCY, 0.95, "Emergency/Pulmonology", "Severe dyspnea indicates risk of respiratory failure"),
    "rapid breathing": ("Rapid Breathing", TriageLevel.URGENT, 0.75, "Emergency", "Rapid breathing may indicate pulmonary or cardiac disease"),
    "hemoptysis": ("Hemoptysis", TriageLevel.EMERGENCY, 0.90, "Emergency/Pulmonology", "Hemoptysis may indicate serious pulmonary disease"),
    "asphyxia": ("Asphyxia", TriageLevel.EMERGENCY, 1.0, "Emergency", "Asphyxia is a life-threatening emergency"),

    # Nervous system - urgent
    "severe headache": ("Severe Headache", TriageLevel.EMERGENCY, 0.85, "Emergency/Neurology", "Sudden severe headache may indicate subarachnoid hemorrhage"),
    "worst headache of life": ("Worst Headache of Life", TriageLevel.EMERGENCY, 0.95, "Emergency/Neurology", "Suggests possible subarachnoid hemorrhage"),
    "slurred speech": ("Slurred Speech", TriageLevel.EMERGENCY, 0.90, "Emergency/Neurology", "May be a sign of stroke"),
    "hemiplegia": ("Hemiplegia", TriageLevel.EMERGENCY, 0.95, "Emergency/Neurology", "Classic symptom of stroke"),
    "hemiparesis": ("Hemiparesis", TriageLevel.EMERGENCY, 0.95, "Emergency/Neurology", "Classic symptom of stroke"),
    "convulsions": ("Convulsions", TriageLevel.URGENT, 0.80, "Emergency/Neurology", "May indicate epileptic seizure"),
    "epilepsy": ("Epilepsy", TriageLevel.URGENT, 0.80, "Neurology", "Epileptic seizures require prompt medical attention"),

    # Digestive system - urgent
    "hematemesis": ("Hematemesis", TriageLevel.EMERGENCY, 0.95, "Emergency/Gastroenterology", "Upper gastrointestinal major bleeding"),
    "melena": ("Melena", TriageLevel.URGENT, 0.80, "Gastroenterology", "May indicate upper gastrointestinal bleeding"),
    "hematochezia": ("Hematochezia", TriageLevel.URGENT, 0.75, "Gastroenterology/Colorectal Surgery", "Gastrointestinal bleeding"),
    "severe abdominal pain": ("Severe Abdominal Pain", TriageLevel.EMERGENCY, 0.85, "Emergency", "May be appendicitis, intestinal perforation, or other acute abdomen"),
    "board-like abdomen": ("Board-like Abdomen", TriageLevel.EMERGENCY, 0.95, "Emergency/Surgery", "Indicates peritonitis"),
    "absent bowel sounds": ("Absent Bowel Sounds", TriageLevel.URGENT, 0.75, "Surgery", "May indicate intestinal obstruction"),

    # Other systems - urgent
    "severe trauma": ("Severe Trauma", TriageLevel.EMERGENCY, 0.95, "Emergency/Surgery", "Severe trauma requires urgent management"),
    "major hemorrhage": ("Major Hemorrhage", TriageLevel.EMERGENCY, 1.0, "Emergency", "Risk of hemorrhagic shock"),
    "drug overdose": ("Drug Overdose", TriageLevel.EMERGENCY, 0.90, "Emergency", "Poisoning requires urgent gastric lavage or antidote"),
    "poisoning": ("Poisoning", TriageLevel.EMERGENCY, 0.95, "Emergency", "Poisoning requires urgent management"),

    # Pediatric/obstetric related
    "decreased fetal movement": ("Decreased Fetal Movement", TriageLevel.URGENT, 0.80, "Obstetrics/Gynecology", "May indicate fetal distress"),
    "vaginal bleeding": ("Vaginal Bleeding", TriageLevel.URGENT, 0.80, "Obstetrics/Gynecology", "Bleeding during pregnancy warrants concern for miscarriage or placental abruption"),
    "febrile seizure": ("Febrile Seizure", TriageLevel.URGENT, 0.85, "Pediatric Emergency", "Febrile seizures in children require urgent management"),
}

# Symptom synonym expansion
SYNONYMS = {
    "chest pain": ["chest ache", "precordial pain", "chest discomfort", "thoracic pain"],
    "dyspnea": ["shortness of breath", "breathlessness", "difficulty breathing", "can't breathe", "suffocation feeling"],
    "severe headache": ["splitting headache", "explosive headache", "worst headache of life"],
    "hemiplegia": ["hemiparesis", "one-sided limb weakness", "arm and leg weakness"],
    "slurred speech": ["unclear speech", "difficulty speaking", "expressive difficulty"],
    "coma": ["loss of consciousness", "unconscious", "unresponsive"],
    "hematemesis": ["vomiting blood", "vomiting fresh blood"],
    "melena": ["tarry stool", "black stool"],
    "severe abdominal pain": ["severe stomach pain", "severe belly pain", "writhing in pain"],
    "major hemorrhage": ["uncontrolled bleeding", "massive bleeding"],
}

# Outpatient-level symptom definitions
OUTPATIENT_SYMPTOMS = {
    "mild headache": ("Mild Headache", TriageLevel.OUTPATIENT, 0.60, "Neurology", "Common symptom, recommend outpatient evaluation"),
    "low-grade fever": ("Low-grade Fever", TriageLevel.OUTPATIENT, 0.50, "Internal Medicine", "Temperature <38.5°C can be seen in outpatient setting"),
    "cough": ("Cough", TriageLevel.OUTPATIENT, 0.40, "Pulmonology", "Cough without dyspnea can be managed in outpatient setting"),
    "runny nose": ("Rhinorrhea", TriageLevel.OUTPATIENT, 0.30, "ENT", "Common symptom of upper respiratory tract infection"),
    "sore throat": ("Sore Throat", TriageLevel.OUTPATIENT, 0.40, "ENT", "Common in upper respiratory tract infection"),
    "mild abdominal pain": ("Mild Abdominal Pain", TriageLevel.OUTPATIENT, 0.50, "Gastroenterology", "Mild abdominal pain without red flags"),
    "diarrhea": ("Diarrhea", TriageLevel.OUTPATIENT, 0.50, "Gastroenterology", "Diarrhea without bloody stool or dehydration"),
    "rash": ("Rash", TriageLevel.OUTPATIENT, 0.40, "Dermatology", "Rash without fever"),
    "joint pain": ("Joint Pain", TriageLevel.OUTPATIENT, 0.40, "Rheumatology", "Chronic joint pain"),
    "insomnia": ("Insomnia", TriageLevel.OUTPATIENT, 0.30, "Neurology/Psychology", "Sleep disorder"),
    "fatigue": ("Fatigue", TriageLevel.OUTPATIENT, 0.40, "Internal Medicine", "Rule out anemia, hypothyroidism, etc."),
}


def expand_synonyms(text: str) -> str:
    """Expand synonyms, replacing all synonyms with standard symptom names"""
    expanded = text
    for standard, synonyms in SYNONYMS.items():
        for syn in synonyms:
            if syn in expanded:
                expanded = expanded.replace(syn, standard)
    return expanded


def extract_red_flags(text: str) -> List[Tuple[str, TriageLevel, float, str, str]]:
    """Extract red flags from symptom description"""
    expanded_text = expand_synonyms(text)
    found_flags = []

    for keyword, (name, level, weight, dept, reason) in RED_FLAGS.items():
        if keyword in expanded_text:
            found_flags.append((name, level, weight, dept, reason))

    # Deduplicate and sort by weight
    seen = set()
    unique_flags = []
    for flag in sorted(found_flags, key=lambda x: x[2], reverse=True):
        if flag[0] not in seen:
            seen.add(flag[0])
            unique_flags.append(flag)

    return unique_flags


def calculate_temperature(text: str) -> Optional[float]:
    """Extract body temperature from text"""
    # Match various temperature formats
    patterns = [
        r'(\d+\.?\d*)\s*degrees?',
        r'(\d+\.?\d*)\s*°C',
        r'(\d+\.?\d*)\s*°',
        r'temperature\s*(\d+\.?\d*)',
        r'fever\s*(\d+\.?\d*)',
        r'temp\s*(\d+\.?\d*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                temp = float(match.group(1))
                # Determine if Celsius or Fahrenheit
                if temp > 50:  # Convert Fahrenheit to Celsius
                    temp = (temp - 32) * 5 / 9
                return temp
            except ValueError:
                continue
    return None


def extract_outpatient_symptoms(text: str) -> List[Tuple[str, TriageLevel, float, str, str]]:
    """Extract outpatient-level symptoms from symptom description"""
    found = []
    text_lower = text.lower()
    
    # Check temperature first
    temperature = calculate_temperature(text)
    
    for keyword, (name, level, weight, dept, reason) in OUTPATIENT_SYMPTOMS.items():
        if keyword in text:
            found.append((name, level, weight, dept, reason))
    
    # If no specific symptoms found but temperature is present, assess based on temperature
    if not found and temperature:
        if temperature < 38:
            found.append(("Low-grade Fever", TriageLevel.OUTPATIENT, 0.50, "Internal Medicine", f"Temperature {temperature:.1f}°C, recommend outpatient visit"))
        elif temperature < 39:
            found.append(("Moderate Fever", TriageLevel.OUTPATIENT, 0.60, "Fever Clinic", f"Temperature {temperature:.1f}°C, can be managed in outpatient setting"))
    
    # Recognize common symptom keywords
    if not found:
        common_keywords = {
            "headache": ("Headache", TriageLevel.OUTPATIENT, 0.60, "Neurology", "Headache without red flags can be evaluated in outpatient setting"),
            "dizziness": ("Dizziness", TriageLevel.OUTPATIENT, 0.50, "Neurology/ENT", "Dizziness requires evaluation"),
            "nausea": ("Nausea", TriageLevel.OUTPATIENT, 0.50, "Gastroenterology", "Nausea without vomiting can be managed in outpatient setting"),
            "vomiting": ("Vomiting", TriageLevel.OUTPATIENT, 0.60, "Gastroenterology", "Non-severe vomiting can be managed in outpatient setting"),
            "cold": ("Cold Symptoms", TriageLevel.OUTPATIENT, 0.50, "Internal Medicine", "Common cold symptoms"),
            "fever": ("Fever", TriageLevel.OUTPATIENT, 0.60, "Fever Clinic", "Fever requires further evaluation"),
            "high temperature": ("Fever", TriageLevel.OUTPATIENT, 0.60, "Fever Clinic", "Fever requires further evaluation"),
        }
        for keyword, symptom_info in common_keywords.items():
            if keyword in text:
                found.append(symptom_info)
    
    return found


def triage(symptom_text: str) -> TriageResult:
    """
    Main triage function

    Args:
        symptom_text: Symptom description text

    Returns:
        TriageResult: Triage result
    """
    if not symptom_text or not symptom_text.strip():
        return TriageResult(
            triage_level=TriageLevel.OUTPATIENT.value,
            confidence=0.0,
            red_flags=[],
            reason="No symptom description provided",
            recommendation="Please provide a symptom description for triage",
            department="Unknown"
        )

    # Extract red flags
    red_flags = extract_red_flags(symptom_text)

    # Extract temperature
    temperature = calculate_temperature(symptom_text)

    # Check high fever
    if temperature and temperature >= 40:
        red_flags.append(("High Fever (>=40°C)", TriageLevel.EMERGENCY, 0.90, "Emergency", "High fever with altered consciousness requires urgent management"))
    elif temperature and temperature >= 39:
        red_flags.append(("High Fever (>=39°C)", TriageLevel.URGENT, 0.70, "Fever Clinic", "High fever requires prompt medical attention"))

    # If red flags are present
    if red_flags:
        # Take the most severe level
        max_level = max(red_flags, key=lambda x: x[2])
        level = max_level[1]
        confidence = min(0.95, max(flag[2] for flag in red_flags))
        flag_names = [flag[0] for flag in red_flags]
        departments = list(dict.fromkeys(flag[3] for flag in red_flags))  # Deduplicate while preserving order
    
        if level == TriageLevel.EMERGENCY:
            recommendation = "Proceed to emergency immediately, call 911 if necessary"
        elif level == TriageLevel.URGENT:
            recommendation = "Seek medical attention within 2-4 hours, emergency or fever clinic"
        else:
            recommendation = "Schedule an outpatient appointment as soon as possible"

        # Combine reasons
        reasons = [f"{flag[0]}: {flag[4]}" for flag in red_flags[:3]]
        reason = "; ".join(reasons)

        return TriageResult(
            triage_level=level.value,
            confidence=confidence,
            red_flags=flag_names,
            reason=reason,
            recommendation=recommendation,
            department="/".join(departments[:2])
        )

    # Check outpatient-level symptoms
    outpatient = extract_outpatient_symptoms(symptom_text)
    if outpatient:
        max_symptom = max(outpatient, key=lambda x: x[2])
        return TriageResult(
            triage_level=TriageLevel.OUTPATIENT.value,
            confidence=max_symptom[2],
            red_flags=[],
            reason=f"Symptom '{max_symptom[0]}' has no red flags, suitable for outpatient management",
            recommendation="Schedule an outpatient appointment; seek urgent care if symptoms worsen",
            department=max_symptom[3]
        )

    # Unrecognized symptoms
    return TriageResult(
        triage_level=TriageLevel.OUTPATIENT.value,
        confidence=0.30,
        red_flags=[],
        reason="Unrecognized symptoms, recommend medical evaluation",
        recommendation="Schedule a general internal medicine outpatient appointment for initial assessment",
        department="Internal Medicine"
    )


def interactive_mode():
    """Interactive mode"""
    print("=" * 50)
    print("Symptom Checker Triage")
    print("=" * 50)
    print("Enter symptom description (e.g. 'chest pain, dyspnea'), type 'quit' to exit")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nSymptom description: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Thank you for using. Goodbye!")
                break

            if not user_input:
                continue

            result = triage(user_input)
            print_result(result)

        except KeyboardInterrupt:
            print("\nThank you for using. Goodbye!")
            break
        except EOFError:
            break


def supports_color() -> bool:
    """Detect whether the terminal supports color"""
    import os
    return sys.stdout.isatty() and os.environ.get('TERM') not in ('dumb', '')


def print_result(result: TriageResult, verbose: bool = False):
    """Print triage result"""
    use_color = supports_color()
    level_colors = {
        "emergency": "\033[91m" if use_color else "",  # Red
        "urgent": "\033[93m" if use_color else "",     # Yellow
        "outpatient": "\033[92m" if use_color else "", # Green
    }
    reset = "\033[0m" if use_color else ""

    level_display = {
        "emergency": "🔴 Emergency",
        "urgent": "🟠 Urgent",
        "outpatient": "🟢 Outpatient",
    }

    level = result.triage_level
    color = level_colors.get(level, "")

    print("\n" + "=" * 50)
    print(f"Triage Level: {color}{level_display.get(level, level)}{reset}")
    print(f"Confidence: {result.confidence:.0%}")

    if result.red_flags:
        print(f"\n🚨 Identified Red Flags:")
        for flag in result.red_flags:
            print(f"   - {flag}")

    print(f"\n📋 Triage Reason:")
    print(f"   {result.reason}")

    print(f"\n💡 Recommendation:")
    print(f"   {result.recommendation}")

    print(f"\n🏥 Suggested Department: {result.department}")

    if verbose:
        print(f"\n⚠️  Disclaimer: {result.warning}")

    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Symptom Checker Triage - recommends triage level based on red flags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "chest pain, radiating to left arm, sweating"
  python main.py --interactive
  python main.py "headache, fever 38 degrees" --verbose
        """
    )
    parser.add_argument(
        "symptoms",
        nargs="?",
        help="Symptom description (e.g. 'chest pain, dyspnea')"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Enter interactive mode"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed information"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.symptoms:
        parser.print_help()
        print("\nError: Please provide symptom description or use --interactive for interactive mode")
        sys.exit(1)

    result = triage(args.symptoms)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print_result(result, verbose=args.verbose)


if __name__ == "__main__":
    main()
