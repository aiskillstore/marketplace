#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medication Reconciliation Skill
Compare pre-admission medication list against inpatient orders

ID: 164
Function: Automatically identify missing or duplicate medications
"""

import json
import argparse
import difflib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Medication:
    """Medication data model"""
    drug_name: str
    generic_name: str = ""
    dosage: str = ""
    frequency: str = ""
    route: str = ""
    indication: str = ""
    order_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Medication":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class MatchResult:
    """Medication match result"""
    pre_admission_med: Medication
    inpatient_med: Optional[Medication]
    match_type: str  # 'exact', 'fuzzy', 'none'
    similarity: float
    is_duplicate: bool = False
    warning: Optional[str] = None


class MedicationReconciler:
    """Core medication reconciliation class"""
    
    # Critical drug classes - warn when missing
    CRITICAL_DRUG_CLASSES = [
        "anticoagulant", "antiplatelet", "antihypertensive", "hypoglycemic", "insulin",
        "antiepileptic", "antiarrhythmic", "corticosteroid", "immunosuppressant"
    ]
    
    # Common drug synonym mappings
    DRUG_SYNONYMS = {
        "atorvastatin": ["atorvastatin", "lipitor"],
        "amlodipine": ["amlodipine", "norvasc"],
        "clopidogrel": ["clopidogrel", "plavix"],
        "aspirin": ["aspirin", "bayer aspirin"],
        "metformin": ["metformin", "glucophage"],
        "metoprolol": ["metoprolol", "betaloc"],
    }
    
    def __init__(self, fuzzy_threshold: float = 0.8):
        self.pre_admission_meds: List[Medication] = []
        self.inpatient_meds: List[Medication] = []
        self.fuzzy_threshold = fuzzy_threshold
        self.match_results: List[MatchResult] = []
        
    def load_pre_admission(self, filepath: str) -> None:
        """Load pre-admission medication list"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.patient_id = data.get('patient_id', 'Unknown')
        self.patient_name = data.get('patient_name', 'Unknown')
        self.admission_date = data.get('admission_date', datetime.now().strftime('%Y-%m-%d'))
        
        self.pre_admission_meds = [
            Medication.from_dict(med) for med in data.get('medications', [])
        ]
        print(f"Loaded pre-admission medications: {len(self.pre_admission_meds)} drugs")
        
    def load_inpatient_orders(self, filepath: str) -> None:
        """Load inpatient medication orders"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.inpatient_meds = [
            Medication.from_dict(med) for med in data.get('medications', [])
        ]
        print(f"Loaded inpatient orders: {len(self.inpatient_meds)} drugs")
        
    def _normalize_name(self, name: str) -> str:
        """Normalize drug name (lowercase, remove spaces)"""
        return name.lower().replace(' ', '').replace('tablet', '').replace('capsule', '')
        
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two drug names"""
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # Exact match
        if norm1 == norm2:
            return 1.0
            
        # Check synonyms
        for drug, synonyms in self.DRUG_SYNONYMS.items():
            names = [drug.lower()] + [s.lower() for s in synonyms]
            if norm1 in names and norm2 in names:
                return 1.0
        
        # Fuzzy match
        return difflib.SequenceMatcher(None, norm1, norm2).ratio()
        
    def _find_best_match(self, pre_med: Medication) -> Tuple[Optional[Medication], float, str]:
        """Find the best matching inpatient order for a pre-admission medication"""
        best_match = None
        best_score = 0.0
        match_type = 'none'
        
        for in_med in self.inpatient_meds:
            # Generic name match
            if pre_med.generic_name and in_med.generic_name:
                score = self._calculate_similarity(pre_med.generic_name, in_med.generic_name)
                if score > best_score:
                    best_score = score
                    best_match = in_med
                    match_type = 'exact' if score == 1.0 else 'fuzzy'
            
            # Brand name match
            score = self._calculate_similarity(pre_med.drug_name, in_med.drug_name)
            if score > best_score:
                best_score = score
                best_match = in_med
                match_type = 'exact' if score == 1.0 else 'fuzzy'
                
        return best_match, best_score, match_type
        
    def _is_critical_drug(self, med: Medication) -> bool:
        """Determine if a medication is a critical drug"""
        combined_text = f"{med.drug_name} {med.generic_name} {med.indication}".lower()
        return any(cls_name in combined_text for cls_name in self.CRITICAL_DRUG_CLASSES)
        
    def _check_duplicate(self, pre_med: Medication, in_med: Medication) -> bool:
        """Check for duplicate medication (same drug, different names)"""
        if not pre_med.generic_name or not in_med.generic_name:
            return False
            
        # Same generic name, similar dose range
        if self._calculate_similarity(pre_med.generic_name, in_med.generic_name) >= 0.9:
            # Simplified dose comparison (real-world use requires more complex parsing)
            pre_dose = ''.join(filter(str.isdigit, pre_med.dosage)) if pre_med.dosage else ""
            in_dose = ''.join(filter(str.isdigit, in_med.dosage)) if in_med.dosage else ""
            if pre_dose and in_dose and pre_dose == in_dose:
                return True
        return False
        
    def reconcile(self) -> Dict[str, Any]:
        """Perform medication reconciliation"""
        print("\nStarting medication reconciliation...")
        
        continued_meds = []
        discontinued_meds = []
        duplicate_meds = []
        warnings = []
        
        # Iterate over pre-admission medications
        for pre_med in self.pre_admission_meds:
            best_match, score, match_type = self._find_best_match(pre_med)
            
            if best_match and score >= self.fuzzy_threshold:
                # Medication continued
                is_dup = self._check_duplicate(pre_med, best_match)
                
                result = MatchResult(
                    pre_admission_med=pre_med,
                    inpatient_med=best_match,
                    match_type=match_type,
                    similarity=score,
                    is_duplicate=is_dup
                )
                
                if is_dup:
                    duplicate_meds.append(result)
                    warnings.append({
                        "level": "warning",
                        "type": "duplicate",
                        "message": f"Possible duplicate medication: {pre_med.drug_name} / {best_match.drug_name}",
                        "drug": pre_med.drug_name
                    })
                else:
                    continued_meds.append(result)
                    
            else:
                # Medication discontinued/missing
                result = MatchResult(
                    pre_admission_med=pre_med,
                    inpatient_med=None,
                    match_type='none',
                    similarity=0.0
                )
                discontinued_meds.append(result)
                
                # Critical drug missing warning
                if self._is_critical_drug(pre_med):
                    warnings.append({
                        "level": "critical",
                        "type": "discontinued_critical",
                        "message": f"Critical medication may be missing: {pre_med.drug_name} ({pre_med.indication})",
                        "drug": pre_med.drug_name,
                        "suggestion": "Please confirm if intentionally discontinued, or consider continuing"
                    })
                else:
                    warnings.append({
                        "level": "info",
                        "type": "discontinued",
                        "message": f"Medication discontinued: {pre_med.drug_name}",
                        "drug": pre_med.drug_name
                    })
        
        # Find newly added medications
        new_meds = []
        for in_med in self.inpatient_meds:
            is_new = True
            for result in continued_meds + duplicate_meds:
                if result.inpatient_med == in_med:
                    is_new = False
                    break
            if is_new:
                new_meds.append(in_med)
        
        # Generate report
        report = {
            "report_id": f"MR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "patient_id": getattr(self, 'patient_id', 'Unknown'),
            "patient_name": getattr(self, 'patient_name', 'Unknown'),
            "admission_date": getattr(self, 'admission_date', ''),
            "summary": {
                "pre_admission_count": len(self.pre_admission_meds),
                "inpatient_count": len(self.inpatient_meds),
                "continued_count": len(continued_meds),
                "discontinued_count": len(discontinued_meds),
                "new_count": len(new_meds),
                "duplicate_count": len(duplicate_meds),
                "warning_count": len(warnings)
            },
            "details": {
                "continued": [
                    {
                        "pre_admission": r.pre_admission_med.to_dict(),
                        "inpatient": r.inpatient_med.to_dict() if r.inpatient_med else None,
                        "match_confidence": r.similarity
                    } for r in continued_meds
                ],
                "discontinued": [
                    {
                        "medication": r.pre_admission_med.to_dict(),
                        "is_critical": self._is_critical_drug(r.pre_admission_med)
                    } for r in discontinued_meds
                ],
                "new_medications": [m.to_dict() for m in new_meds],
                "duplicates": [
                    {
                        "pre_admission": r.pre_admission_med.to_dict(),
                        "inpatient": r.inpatient_med.to_dict() if r.inpatient_med else None
                    } for r in duplicate_meds
                ],
                "warnings": warnings
            },
            "recommendations": self._generate_recommendations(
                continued_meds, discontinued_meds, duplicate_meds, warnings
            )
        }
        
        self.match_results = continued_meds + discontinued_meds + duplicate_meds
        return report
        
    def _generate_recommendations(
        self, 
        continued: List[MatchResult],
        discontinued: List[MatchResult],
        duplicates: List[MatchResult],
        warnings: List[Dict]
    ) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        # Critical drug missing recommendations
        critical_discontinued = [w for w in warnings if w['level'] == 'critical']
        if critical_discontinued:
            recommendations.append(
                f"WARNING: {len(critical_discontinued)} critical medication(s) may be missing, physician review recommended"
            )
        
        # Duplicate medication recommendations
        if duplicates:
            recommendations.append(
                f"WARNING: {len(duplicates)} possible duplicate medication(s) found, please confirm if clinically intended"
            )
        
        # Discontinued medication documentation
        if discontinued:
            recommendations.append(
                f"INFO: {len(discontinued)} pre-admission medication(s) not reflected in orders, recommend documenting reason for discontinuation"
            )
        
        # New medication reminder
        new_count = len([w for w in warnings if 'new' in w.get('type', '')])
        if new_count > 0:
            recommendations.append(f"INFO: {new_count} new medication(s) added during hospitalization")
        
        if not recommendations:
            recommendations.append("Medication reconciliation complete, no significant issues found")
            
        return recommendations


def generate_example_data():
    """Generate example data for testing"""
    # Pre-admission medication list
    pre_admission = {
        "patient_id": "P20260206001",
        "patient_name": "Patient A",
        "admission_date": "2026-02-06",
        "medications": [
            {
                "drug_name": "Atorvastatin Calcium Tablets",
                "generic_name": "Atorvastatin",
                "dosage": "20mg",
                "frequency": "once nightly",
                "route": "oral",
                "indication": "hyperlipidemia"
            },
            {
                "drug_name": "Amlodipine Tablets",
                "generic_name": "Amlodipine",
                "dosage": "5mg",
                "frequency": "once daily",
                "route": "oral",
                "indication": "hypertension"
            },
            {
                "drug_name": "Aspirin Enteric-Coated Tablets",
                "generic_name": "Aspirin",
                "dosage": "100mg",
                "frequency": "once daily",
                "route": "oral",
                "indication": "secondary prevention of coronary artery disease"
            },
            {
                "drug_name": "Metformin Tablets",
                "generic_name": "Metformin",
                "dosage": "500mg",
                "frequency": "three times daily",
                "route": "oral",
                "indication": "type 2 diabetes"
            },
            {
                "drug_name": "Vitamin C Tablets",
                "generic_name": "Vitamin C",
                "dosage": "100mg",
                "frequency": "once daily",
                "route": "oral",
                "indication": "nutritional supplement"
            }
        ]
    }
    
    # Inpatient orders
    inpatient_orders = {
        "patient_id": "P20260206001",
        "order_date": "2026-02-06",
        "medications": [
            {
                "drug_name": "Lipitor",
                "generic_name": "Atorvastatin",
                "dosage": "20mg",
                "frequency": "qn",
                "route": "po",
                "order_type": "standing order"
            },
            {
                "drug_name": "Norvasc",
                "generic_name": "Amlodipine",
                "dosage": "5mg",
                "frequency": "qd",
                "route": "po",
                "order_type": "standing order"
            },
            {
                "drug_name": "Bayer Aspirin",
                "generic_name": "Aspirin",
                "dosage": "100mg",
                "frequency": "qd",
                "route": "po",
                "order_type": "standing order"
            },
            {
                "drug_name": "Normal Saline",
                "generic_name": "Sodium Chloride",
                "dosage": "500ml",
                "frequency": "qd",
                "route": "ivgtt",
                "order_type": "prn order"
            }
        ]
    }
    
    # Save example data
    skill_dir = Path(__file__).parent.parent
    example_dir = skill_dir / "examples"
    example_dir.mkdir(exist_ok=True)
    
    with open(example_dir / "pre_admission.json", 'w', encoding='utf-8') as f:
        json.dump(pre_admission, f, ensure_ascii=False, indent=2)
    
    with open(example_dir / "inpatient_orders.json", 'w', encoding='utf-8') as f:
        json.dump(inpatient_orders, f, ensure_ascii=False, indent=2)
    
    print(f"Example data saved to {example_dir}")
    return example_dir / "pre_admission.json", example_dir / "inpatient_orders.json"


def main():
    parser = argparse.ArgumentParser(
        description="Medication Reconciliation Tool - compare pre-admission medications against inpatient orders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --example                    # Run with example data
  python main.py -p pre.json -i orders.json   # Specify input files
  python main.py -p pre.json -i orders.json -o report.json  # Specify output file
        """
    )
    
    parser.add_argument('-p', '--pre-admission', help='Pre-admission medication list JSON file path')
    parser.add_argument('-i', '--inpatient', help='Inpatient orders JSON file path')
    parser.add_argument('-o', '--output', help='Output report JSON file path')
    parser.add_argument('--example', action='store_true', help='Run with example data')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Use example data
    if args.example:
        pre_file, in_file = generate_example_data()
        args.pre_admission = str(pre_file)
        args.inpatient = str(in_file)
    
    # Check required arguments
    if not args.pre_admission or not args.inpatient:
        parser.print_help()
        print("\nError: Please provide pre-admission medication list and inpatient orders file paths, or use --example to run with example data")
        return 1
    
    try:
        # Create reconciler
        reconciler = MedicationReconciler()
        
        # Load data
        reconciler.load_pre_admission(args.pre_admission)
        reconciler.load_inpatient_orders(args.inpatient)
        
        # Perform reconciliation
        report = reconciler.reconcile()
        
        # Output report
        report_json = json.dumps(report, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report_json)
            print(f"\nReport saved to: {args.output}")
        else:
            print("\n" + "="*60)
            print("Medication Reconciliation Report")
            print("="*60)
            print(report_json)
        
        # Concise summary
        print("\n" + "="*60)
        print("Reconciliation Summary")
        print("="*60)
        summary = report['summary']
        print(f"  Pre-admission medications: {summary['pre_admission_count']}")
        print(f"  Inpatient orders:          {summary['inpatient_count']}")
        print(f"  |- Continued:              {summary['continued_count']}")
        print(f"  |- New:                    {summary['new_count']}")
        print(f"  |- Possibly missing:       {summary['discontinued_count']}")
        print(f"  |- Duplicates:             {summary['duplicate_count']}")
        print(f"  Warnings: {summary['warning_count']}")
        
        if report['recommendations']:
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\nError: File not found - {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"\nError: Invalid JSON format - {e}")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
