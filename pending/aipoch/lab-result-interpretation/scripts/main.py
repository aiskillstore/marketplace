#!/usr/bin/env python3
"""
Lab Result Interpretation Tool
Transforms complex biochemical test results into patient-friendly explanations.
"""

import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class LabResult:
    """Represents a single lab test result."""
    test_name: str
    value: float
    unit: str
    reference_min: Optional[float] = None
    reference_max: Optional[float] = None
    status: str = "normal"  # normal, low, high, critical
    severity: str = "none"  # none, mild, moderate, severe
    explanation: str = ""
    recommendation: str = ""


class LabResultInterpreter:
    """Interprets lab test results and generates patient-friendly explanations."""
    
    # Common test name mappings (Chinese/English variations)
    TEST_NAME_MAPPINGS = {
        # Blood Routine
        "wbc": "White Blood Cell Count", "white blood cell": "White Blood Cell Count",
        "rbc": "Red Blood Cell Count", "red blood cell": "Red Blood Cell Count",
        "hgb": "Hemoglobin", "hemoglobin": "Hemoglobin",
        "plt": "Platelet Count", "platelet": "Platelet Count",
        "hct": "Hematocrit", "hematocrit": "Hematocrit",
        
        # Lipid Panel
        "tc": "Total Cholesterol", "cholesterol": "Total Cholesterol",
        "ldl": "LDL Cholesterol", "ldl-c": "LDL Cholesterol",
        "hdl": "HDL Cholesterol", "hdl-c": "HDL Cholesterol",
        "tg": "Triglycerides", "triglyceride": "Triglycerides",
        
        # Liver Function
        "alt": "Alanine Aminotransferase", "gpt": "Alanine Aminotransferase",
        "ast": "Aspartate Aminotransferase", "got": "Aspartate Aminotransferase",
        "alp": "Alkaline Phosphatase",
        "ggt": "Gamma-Glutamyl Transferase",
        "tbil": "Total Bilirubin", "bilirubin": "Total Bilirubin",
        "tp": "Total Protein", "total protein": "Total Protein",
        "alb": "Albumin", "albumin": "Albumin",
        
        # Kidney Function
        "crea": "Creatinine", "creatinine": "Creatinine",
        "bun": "Blood Urea Nitrogen", "urea": "Blood Urea Nitrogen",
        "egfr": "eGFR", "gfr": "eGFR",
        "ua": "Uric Acid", "uric acid": "Uric Acid",
        
        # Blood Sugar
        "glu": "Fasting Blood Glucose", "glucose": "Fasting Blood Glucose",
        "hba1c": "HbA1c",
        
        # Thyroid
        "tsh": "TSH",
        "t3": "T3",
        "t4": "T4",
        "ft3": "Free T3",
        "ft4": "Free T4",
        
        # Electrolytes
        "na": "Sodium", "sodium": "Sodium",
        "k": "Potassium", "potassium": "Potassium",
        "cl": "Chloride", "chloride": "Chloride",
        "ca": "Calcium", "calcium": "Calcium",
        "mg": "Magnesium", "magnesium": "Magnesium",
        
        # Inflammation
        "crp": "C-Reactive Protein",
        "esr": "ESR", "erythrocyte sedimentation rate": "ESR",
    }
    
    # Standard reference ranges
    REFERENCE_RANGES = {
        "White Blood Cell Count": {"min": 4.0, "max": 10.0, "unit": "10^9/L"},
        "Red Blood Cell Count": {"min": 4.0, "max": 5.5, "unit": "10^12/L"},
        "Hemoglobin": {"min": 120.0, "max": 160.0, "unit": "g/L"},
        "Platelet Count": {"min": 100.0, "max": 300.0, "unit": "10^9/L"},
        "Hematocrit": {"min": 0.40, "max": 0.50, "unit": "L/L"},
        "Total Cholesterol": {"min": 3.1, "max": 5.7, "unit": "mmol/L"},
        "LDL Cholesterol": {"min": 0.0, "max": 3.4, "unit": "mmol/L"},
        "HDL Cholesterol": {"min": 1.0, "max": 2.0, "unit": "mmol/L"},
        "Triglycerides": {"min": 0.0, "max": 1.7, "unit": "mmol/L"},
        "Alanine Aminotransferase": {"min": 0.0, "max": 40.0, "unit": "U/L"},
        "Aspartate Aminotransferase": {"min": 0.0, "max": 40.0, "unit": "U/L"},
        "Alkaline Phosphatase": {"min": 40.0, "max": 150.0, "unit": "U/L"},
        "Gamma-Glutamyl Transferase": {"min": 10.0, "max": 60.0, "unit": "U/L"},
        "Total Bilirubin": {"min": 0.0, "max": 21.0, "unit": "μmol/L"},
        "Total Protein": {"min": 60.0, "max": 80.0, "unit": "g/L"},
        "Albumin": {"min": 35.0, "max": 55.0, "unit": "g/L"},
        "Creatinine": {"min": 44.0, "max": 133.0, "unit": "μmol/L"},
        "Blood Urea Nitrogen": {"min": 2.6, "max": 7.5, "unit": "mmol/L"},
        "Uric Acid": {"min": 208.0, "max": 428.0, "unit": "μmol/L"},
        "Fasting Blood Glucose": {"min": 3.9, "max": 6.1, "unit": "mmol/L"},
        "HbA1c": {"min": 4.0, "max": 6.0, "unit": "%"},
        "TSH": {"min": 0.27, "max": 4.2, "unit": "mIU/L"},
        "Sodium": {"min": 137.0, "max": 147.0, "unit": "mmol/L"},
        "Potassium": {"min": 3.5, "max": 5.3, "unit": "mmol/L"},
        "Chloride": {"min": 99.0, "max": 110.0, "unit": "mmol/L"},
        "Calcium": {"min": 2.1, "max": 2.6, "unit": "mmol/L"},
        "C-Reactive Protein": {"min": 0.0, "max": 10.0, "unit": "mg/L"},
    }
    
    def __init__(self):
        self.disclaimer = "\n[Disclaimer] This interpretation is for reference only and cannot replace professional medical advice. Please consult a doctor if you have any questions."
    
    def normalize_test_name(self, name: str) -> str:
        """Normalize test name to standard form."""
        name_lower = name.lower().strip()
        return self.TEST_NAME_MAPPINGS.get(name_lower, name)
    
    def parse_lab_line(self, line: str) -> Optional[LabResult]:
        """Parse a single line of lab result."""
        # Pattern 1: "Name: Value Unit (Ref: Min-Max)" or "Name: Value (Min-Max)" or "Name: Value Unit"
        pattern1 = r"(.+?)[:\s]+([\d.]+)\s*(\S*)?(?:\s*[\(\（]?[^\d]*([\d.]+)?\s*[-~至]\s*([\d.]+)?[^\)]*[\)\）]?)?"
        
        # Pattern 2: "Name Value Unit" (simpler format)
        pattern2 = r"^(.+?)\s+([\d.]+)\s+(\S+)$"
        
        for pattern in [pattern1, pattern2]:
            match = re.search(pattern, line.strip())
            if match:
                groups = match.groups()
                test_name = self.normalize_test_name(groups[0].strip())
                value = float(groups[1])
                unit = groups[2] if groups[2] else ""
                ref_min = float(groups[3]) if groups[3] else None
                ref_max = float(groups[4]) if groups[4] else None
                
                # Use standard reference range if not provided
                if test_name in self.REFERENCE_RANGES:
                    std_range = self.REFERENCE_RANGES[test_name]
                    if ref_min is None:
                        ref_min = std_range["min"]
                    if ref_max is None:
                        ref_max = std_range["max"]
                    if not unit:
                        unit = std_range["unit"]
                
                return LabResult(
                    test_name=test_name,
                    value=value,
                    unit=unit,
                    reference_min=ref_min,
                    reference_max=ref_max
                )
        
        return None
    
    def determine_status(self, result: LabResult) -> tuple:
        """Determine status and severity of a result."""
        if result.reference_min is None or result.reference_max is None:
            return "unknown", "none"
        
        value = result.value
        min_val = result.reference_min
        max_val = result.reference_max
        
        if min_val <= value <= max_val:
            return "normal", "none"
        
        # Calculate deviation percentage
        if value < min_val:
            deviation = (min_val - value) / min_val if min_val > 0 else 0
            if deviation > 0.5:
                return "low", "severe"
            elif deviation > 0.2:
                return "low", "moderate"
            else:
                return "low", "mild"
        else:  # value > max_val
            deviation = (value - max_val) / max_val if max_val > 0 else 0
            if deviation > 0.5:
                return "high", "severe"
            elif deviation > 0.2:
                return "high", "moderate"
            else:
                return "high", "mild"
    
    def generate_explanation(self, result: LabResult) -> str:
        """Generate patient-friendly explanation."""
        explanations = {
            "White Blood Cell Count": {
                "normal": "White blood cell count is within normal range, indicating normal immune system function.",
                "low": "White blood cell count is low, which may indicate reduced immunity. Consult a doctor.",
                "high": "White blood cell count is elevated, which may indicate infection or inflammation."
            },
            "Red Blood Cell Count": {
                "normal": "Red blood cell count is normal; blood oxygen-carrying capacity is good.",
                "low": "Red blood cell count is low, which may indicate anemia. Further examination is recommended.",
                "high": "Red blood cell count is elevated, which may indicate blood concentration or other conditions."
            },
            "Hemoglobin": {
                "normal": "Hemoglobin level is normal; blood oxygen-carrying function is good.",
                "low": "Hemoglobin is low, which may indicate anemia symptoms such as fatigue and weakness.",
                "high": "Hemoglobin is elevated, which may indicate dehydration or polycythemia."
            },
            "Platelet Count": {
                "normal": "Platelet count is normal; coagulation function is good.",
                "low": "Platelet count is low, which may affect coagulation. Attention is needed.",
                "high": "Platelet count is elevated, which may increase thrombosis risk."
            },
            "Total Cholesterol": {
                "normal": "Total cholesterol is within normal range; blood lipid control is good.",
                "low": "Total cholesterol is low. Pay attention to balanced nutrition.",
                "high": "Total cholesterol is elevated. Reduce high-fat food intake and increase exercise."
            },
            "LDL Cholesterol": {
                "normal": "LDL (bad cholesterol) is well controlled.",
                "high": "LDL is elevated, which is a risk factor for cardiovascular disease. Improve diet and exercise."
            },
            "HDL Cholesterol": {
                "normal": "HDL (good cholesterol) level is good.",
                "low": "HDL is low. Increase aerobic exercise to protect cardiovascular health.",
                "high": "HDL is high, which has a protective effect on cardiovascular health."
            },
            "Triglycerides": {
                "normal": "Triglyceride level is normal.",
                "high": "Triglycerides are elevated. Reduce sugar and fat intake, and control weight."
            },
            "Alanine Aminotransferase": {
                "normal": "Liver function indicator is normal.",
                "high": "ALT is elevated, which may indicate hepatocyte damage. Further liver function examination is recommended."
            },
            "Aspartate Aminotransferase": {
                "normal": "Liver function indicator is normal.",
                "high": "AST is elevated, which may indicate liver or myocardial damage."
            },
            "Creatinine": {
                "normal": "Kidney function indicator is normal.",
                "high": "Creatinine is elevated, which may indicate reduced kidney function. Consult a nephrologist."
            },
            "Uric Acid": {
                "normal": "Uric acid level is normal.",
                "high": "Uric acid is elevated, which may increase gout risk. Drink more water and reduce high-purine foods."
            },
            "Fasting Blood Glucose": {
                "normal": "Blood glucose level is normal.",
                "high": "Fasting blood glucose is elevated, which may indicate impaired glucose metabolism. Control diet and retest."
            },
            "HbA1c": {
                "normal": "HbA1c is normal; blood glucose has been well controlled over the past 3 months.",
                "high": "HbA1c is elevated, indicating poor recent blood glucose control."
            },
        }
        
        test_explanations = explanations.get(result.test_name, {
            "normal": f"{result.test_name} is within normal range.",
            "low": f"{result.test_name} is low.",
            "high": f"{result.test_name} is elevated."
        })
        
        return test_explanations.get(result.status, test_explanations.get("normal", ""))
    
    def generate_recommendation(self, result: LabResult) -> str:
        """Generate health recommendations."""
        recommendations = {
            "Total Cholesterol": {
                "high": "Recommendation: Reduce animal fat intake, eat more vegetables and fruits, get at least 150 minutes of moderate-intensity exercise per week."
            },
            "LDL Cholesterol": {
                "high": "Recommendation: Limit saturated fat intake, choose healthy oils such as olive oil, and monitor blood lipids regularly."
            },
            "Triglycerides": {
                "high": "Recommendation: Control refined sugar and sweets, limit alcohol, and increase aerobic exercise."
            },
            "Alanine Aminotransferase": {
                "high": "Recommendation: Avoid alcohol, do not overuse medications, recheck liver function, and consider liver ultrasound if necessary."
            },
            "Uric Acid": {
                "high": "Recommendation: Drink more than 2000ml of water daily, reduce intake of high-purine foods such as seafood, organ meats, and rich meat soups."
            },
            "Fasting Blood Glucose": {
                "high": "Recommendation: Control staple food portions, choose low glycemic index foods, exercise after meals, and recheck regularly."
            },
        }
        
        test_recs = recommendations.get(result.test_name, {})
        return test_recs.get(result.status, "")
    
    def interpret(self, input_text: str) -> List[LabResult]:
        """Interpret lab results from input text."""
        results = []
        
        # Split by lines and common separators
        lines = re.split(r'[\n,;，；]', input_text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            result = self.parse_lab_line(line)
            if result:
                # Determine status and severity
                result.status, result.severity = self.determine_status(result)
                # Generate explanation
                result.explanation = self.generate_explanation(result)
                # Generate recommendation
                result.recommendation = self.generate_recommendation(result)
                results.append(result)
        
        return results
    
    def format_output(self, results: List[LabResult]) -> str:
        """Format results as patient-friendly output."""
        if not results:
            return "No valid lab results could be recognized. Please check the input format."
        
        output_lines = ["=== Lab Result Interpretation ===\n"]
        
        for r in results:
            # Status emoji
            status_emoji = {
                "normal": "✅",
                "low": "⚠️",
                "high": "⚠️",
                "critical": "🚨",
                "unknown": "❓"
            }.get(r.status, "❓")
            
            # Status text
            status_text = {
                "normal": "Normal",
                "low": "Low",
                "high": "High",
                "critical": "Critical",
                "unknown": "Unknown"
            }.get(r.status, "Unknown")
            
            ref_range = ""
            if r.reference_min is not None and r.reference_max is not None:
                ref_range = f" (Reference: {r.reference_min}-{r.reference_max} {r.unit})"
            
            output_lines.append(f"{status_emoji} {r.test_name}: {r.value} {r.unit}{ref_range}")
            output_lines.append(f"   Status: {status_text}")
            output_lines.append(f"   Interpretation: {r.explanation}")
            if r.recommendation:
                output_lines.append(f"   {r.recommendation}")
            output_lines.append("")
        
        output_lines.append(self.disclaimer)
        return "\n".join(output_lines)
    
    def to_dict(self, results: List[LabResult]) -> List[Dict[str, Any]]:
        """Convert results to dictionary format."""
        return [asdict(r) for r in results]


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Lab Result Interpretation Tool")
    parser.add_argument("--file", "-f", help="Input file containing lab results")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    interpreter = LabResultInterpreter()
    
    if args.interactive:
        print("Lab Result Interpretation Tool - Interactive Mode")
        print("Enter lab results (one per line, or comma-separated), type 'quit' to exit")
        print("Example: Total Cholesterol: 5.8 mmol/L (Reference: 3.1-5.7)")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nEnter lab result: ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                if not user_input:
                    continue
                
                results = interpreter.interpret(user_input)
                print(interpreter.format_output(results))
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
            results = interpreter.interpret(content)
            
            if args.json:
                print(json.dumps(interpreter.to_dict(results), ensure_ascii=False, indent=2))
            else:
                print(interpreter.format_output(results))
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    else:
        # Read from stdin
        print("Lab Result Interpretation Tool")
        print("Usage:")
        print("  python main.py --interactive    # Interactive mode")
        print("  python main.py --file lab.txt   # Read from file")
        print("  echo 'Total Cholesterol: 5.8' | python main.py  # Read from stdin")
        print("\nEnter lab results (Ctrl+D to finish):")
        
        try:
            content = sys.stdin.read()
            if content.strip():
                results = interpreter.interpret(content)
                print(interpreter.format_output(results))
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
