#!/usr/bin/env python3
"""Protocol Deviation Classifier
Clinical trial protocol deviation classification tool

Based on the GCP/ICH E6 guidelines, it can automatically determine whether a deviation is a "major deviation" or a "minor deviation".
Technical: Risk-based quality management, GCP compliance assessment, deviation classification"""

import argparse
import json
import sys
import re
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


class Classification(Enum):
    """Deviation classification enumeration"""
    MAJOR = "major"
    MINOR = "minor"
    CRITICAL = "critical"
    
    def __str__(self):
        mapping = {
            Classification.MAJOR: "significant deviation",
            Classification.MINOR: "small deviation",
            Classification.CRITICAL: "critical deviation"
        }
        return mapping.get(self, self.value)
    
    @property
    def en_name(self):
        mapping = {
            Classification.MAJOR: "Major Deviation",
            Classification.MINOR: "Minor Deviation",
            Classification.CRITICAL: "Critical Deviation"
        }
        return mapping.get(self, self.value.title())


class RiskLevel(Enum):
    """Risk level enumeration"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    def __str__(self):
        mapping = {
            RiskLevel.NONE: "none",
            RiskLevel.LOW: "Low",
            RiskLevel.MEDIUM: "medium",
            RiskLevel.HIGH: "high"
        }
        return mapping.get(self, self.value)
    
    @property
    def score(self):
        """Returns the risk score used in the calculation"""
        scores = {
            RiskLevel.NONE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3
        }
        return scores.get(self, 0)


@dataclass
class DeviationEvent:
    """Plan deviation event data class"""
    id: str = ""
    description: str = ""
    deviation_type: str = ""
    occurrence_date: Optional[str] = None
    site_id: Optional[str] = None
    subject_id: Optional[str] = None
    safety_impact: RiskLevel = RiskLevel.NONE
    data_impact: RiskLevel = RiskLevel.NONE
    scientific_impact: RiskLevel = RiskLevel.NONE
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DeviationEvent':
        """Create event from dictionary"""
        def parse_risk(value):
            if isinstance(value, str):
                try:
                    return RiskLevel(value.lower())
                except ValueError:
                    return RiskLevel.NONE
            return RiskLevel.NONE
        
        factors = data.get('severity_factors', {})
        return cls(
            id=data.get('id', ''),
            description=data.get('description', ''),
            deviation_type=data.get('type', data.get('deviation_type', '')),
            occurrence_date=data.get('occurrence_date'),
            site_id=data.get('site_id'),
            subject_id=data.get('subject_id'),
            safety_impact=parse_risk(factors.get('safety_impact', 'none')),
            data_impact=parse_risk(factors.get('data_impact', 'none')),
            scientific_impact=parse_risk(factors.get('scientific_impact', 'none'))
        )


@dataclass
class ClassificationResult:
    """Classification result data class"""
    id: str
    classification: Classification
    confidence: float
    rationale: str
    safety_risk: RiskLevel
    data_integrity_risk: RiskLevel
    scientific_validity_risk: RiskLevel
    risk_score: int
    regulatory_basis: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    key_indicators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "classification": str(self.classification),
            "classification_en": self.classification.en_name,
            "confidence": round(self.confidence, 2),
            "rationale": self.rationale,
            "risk_factors": {
                "safety_risk": str(self.safety_risk),
                "data_integrity_risk": str(self.data_integrity_risk),
                "scientific_validity_risk": str(self.scientific_validity_risk)
            },
            "risk_score": self.risk_score,
            "regulatory_basis": self.regulatory_basis,
            "recommended_actions": self.recommended_actions,
            "key_indicators": self.key_indicators
        }


class DeviationClassifier:
    """Scheme deviation classifier
    
    Based on GCP/ICH E6 guidelines, automatically determine the severity of clinical trial deviations."""
    
    # Major deviation keyword pattern (Chinese and English)
    MAJOR_INDICATORS = {
        'informed_consent': [
            'informed consent', 'Not obtained.*Consent', 'consent form', r'informed consent',
            'not signed', r'consent', r'signed.*consent'
        ],
        'eligibility': [
            'Inclusion criteria', 'Exclusion criteria', 'Not in compliance.*Enter the group', r'eligibility',
            r'inclusion.*criteria', r'exclusion.*criteria', r'ineligible'
        ],
        'dosing': [
            'overdose', 'double dose', r'overdose', 'excess', 'Error.*Dose',
            r'wrong dose', r'double dose', r'dosing error'
        ],
        'concomitant': [
            'Concomitant medication', 'Contraindications.* Medication', r'concomitant', r'prohibited medication',
            r'forbidden drug'
        ],
        'randomization': [
            'Randomize.*Error', 'Wrong.*Random', r'randomization error',
            r'wrong randomization'
        ],
        'safety_reporting': [
            r'SAE', r'SUSAR', 'Security.*Report', 'False negative', 'Delayed reporting',
            r'serious adverse event', r'safety reporting'
        ],
        'blinding': [
            'Break the blindness', r'unblind', 'Breaking the blindness.*Not yet', 'Unauthorized.*Break the blind'
        ],
        'data_integrity': [
            'forgery', 'tamper', 'data.*false', r'falsified',
            r'fabricated', 'Data fraud'
        ],
        'critical_procedures': [
            'Key.* not executed', 'Not.*Key', 'Missing.*Primary endpoint',
            r'primary endpoint.*missed', r'critical procedure'
        ]
    }
    
    # Small deviation keyword pattern
    MINOR_INDICATORS = {
        'visit_window': [
            'Visit.*Delay', 'Visit.* in advance', r'visit.*window',
            'Visit.*[12].*days', r'visit.*[12].*day'
        ],
        'sample_collection': [
            'sample.*delay', 'sampling.*time', r'sample.*delay',
            'Non-critical.*Sample', r'non-critical sample'
        ],
        'questionnaire': [
            'Questionnaire', 'diary cards', r'questionnaire', r'diary card',
            r'QOL', 'quality of life'
        ],
        'documentation': [
            'signature.*delay', 'Documentation.* is missing', r'document.*missing',
            r'signature.*delay', 'record.*delay'
        ],
        'non_critical': [
            'non-critical', 'secondary', 'slight', r'non-critical',
            r'minor', r'slight'
        ]
    }
    
    # regulatory basis
    REGULATORY_BASIS = {
        'major': [
            "ICH E6(R2) Section 4.5 - Subject Safety",
            "ICH E6(R2) Section 4.9 - Informed Consent",
            "GCP Section 6.2 - Subject Rights",
            "FDA 21 CFR Part 312.60 - General Investigator Obligations"
        ],
        'minor': [
            "ICH E6(R2) Section 4.6 - Investigational Product",
            "ICH E6(R2) Section 5.1 - Trial Management",
            "GCP Section 6.4.4 - Protocol Compliance"
        ],
        'critical': [
            "ICH E6(R2) Section 2.13 - Data Integrity",
            "ICH E6(R2) Section 4.1.5 - Fraud Prevention",
            "FDA 21 CFR Part 312.70 - Disqualification of Investigators"
        ]
    }
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regular expression pattern"""
        self.major_patterns = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in self.MAJOR_INDICATORS.items()
        }
        self.minor_patterns = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in self.MINOR_INDICATORS.items()
        }
    
    def classify(
        self,
        description: str,
        deviation_type: str = "",
        event_id: str = "",
        safety_impact: Optional[RiskLevel] = None,
        data_impact: Optional[RiskLevel] = None,
        scientific_impact: Optional[RiskLevel] = None
    ) -> ClassificationResult:
        """Classify individual deviation events
        
        Args:
            description: Deviation description
            deviation_type: deviation type
            event_id: event ID
            safety_impact: Safety impact level (if known)
            data_impact: Data integrity impact level (if known)
            scientific_impact: scientific impact level (if known)
        
        Returns:
            ClassificationResult: classification result"""
        # If no impact level is provided, it will be automatically determined based on the description.
        if safety_impact is None:
            safety_impact = self._assess_safety_impact(description, deviation_type)
        if data_impact is None:
            data_impact = self._assess_data_impact(description, deviation_type)
        if scientific_impact is None:
            scientific_impact = self._assess_scientific_impact(description, deviation_type)
        
        # Calculate risk score
        risk_score = (
            safety_impact.score * 3 +
            data_impact.score * 2 +
            scientific_impact.score * 2
        )
        
        # Apply classification rules
        classification, confidence = self._apply_classification_rules(
            safety_impact, data_impact, scientific_impact, risk_score, description
        )
        
        # Generate classification reasons
        rationale = self._generate_rationale(
            classification, safety_impact, data_impact, scientific_impact, description
        )
        
        # Get key metrics
        key_indicators = self._extract_key_indicators(description, deviation_type)
        
        # Obtain regulatory basis
        regulatory_basis = self._get_regulatory_basis(classification, description)
        
        # Generate recommended actions
        recommended_actions = self._get_recommended_actions(classification)
        
        return ClassificationResult(
            id=event_id or self._generate_event_id(),
            classification=classification,
            confidence=confidence,
            rationale=rationale,
            safety_risk=safety_impact,
            data_integrity_risk=data_impact,
            scientific_validity_risk=scientific_impact,
            risk_score=risk_score,
            regulatory_basis=regulatory_basis,
            recommended_actions=recommended_actions,
            key_indicators=key_indicators
        )
    
    def classify_batch(self, events: List[Dict]) -> List[ClassificationResult]:
        """Batch classification deviation event
        
        Args:
            events: Dictionary list of deviation events
        
        Returns:
            List[ClassificationResult]: Classification result list"""
        results = []
        for event_data in events:
            event = DeviationEvent.from_dict(event_data)
            result = self.classify(
                description=event.description,
                deviation_type=event.deviation_type,
                event_id=event.id,
                safety_impact=event.safety_impact,
                data_impact=event.data_impact,
                scientific_impact=event.scientific_impact
            )
            results.append(result)
        return results
    
    def _assess_safety_impact(self, description: str, deviation_type: str) -> RiskLevel:
        """Assess the impact on subject safety"""
        text = f"{description} {deviation_type}".lower()
        
        # High security impact keywords
        high_risk = [
            r'overdose', 'overdose', 'double dose', 'Contraindications', 'allergic reaction',
            'serious adverse events', r'sae', 'die', 'life-threatening', 'Hospitalized',
            r'death', r'life-threatening', r'hospitalization'
        ]
        
        # Medium safety impact keywords
        medium_risk = [
            'adverse reactions', 'side effect', r'adverse event', 'Concomitant medication',
            r'concomitant', 'drug interactions', r'drug interaction',
            'Dosage adjustment', r'dose adjustment'
        ]
        
        for pattern in high_risk:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.HIGH
        
        for pattern in medium_risk:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.MEDIUM
        
        # If informed consent is involved but no specific harm is involved
        if re.search('informed consent|consent', text, re.IGNORECASE):
            return RiskLevel.HIGH
        
        return RiskLevel.NONE
    
    def _assess_data_impact(self, description: str, deviation_type: str) -> RiskLevel:
        """Assess the impact on data integrity"""
        text = f"{description} {deviation_type}".lower()
        
        # High data impact
        high_patterns = [
            'forgery|tampering|false|falsif|fabricat',
            'data.*lost|data.*lost',
            'critical.*data.*missing|critical.*data.*missing'
        ]
        
        # Medium data impact
        medium_patterns = [
            'primary endpoint|primary endpoint',
            'critical visit|critical visit',
            'not.*assess|not.*assess'
        ]
        
        for pattern in high_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.HIGH
        
        for pattern in medium_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _assess_scientific_impact(self, description: str, deviation_type: str) -> RiskLevel:
        """Assessing the impact on the scientific validity of the trial"""
        text = f"{description} {deviation_type}".lower()
        
        # Check whether it affects the primary endpoint or randomization
        high_patterns = [
            'randomize.*error|error.*random|randomiz',
            'primary endpoint|primary endpoint',
            'Enter the group.*Error|Wrong.*Enter the group|Inconsistent.*Enter the group|ineligible'
        ]
        
        # medium impact
        medium_patterns = [
            'Visit.*missing|missed visit',
            'Efficacy.*Assessment|efficacy assessment',
            'Break the blind|unblind'
        ]
        
        for pattern in high_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.HIGH
        
        for pattern in medium_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.MEDIUM
        
        return RiskLevel.NONE
    
    def _apply_classification_rules(
        self,
        safety_impact: RiskLevel,
        data_impact: RiskLevel,
        scientific_impact: RiskLevel,
        risk_score: int,
        description: str
    ) -> Tuple[Classification, float]:
        """Apply classification rules
        
        Classification rules:
        - Any dimension is High → significant deviation
        - Security dimension is Medium and data/science is either Medium+ → major deviation
        - Involving informed consent issues → Major deviations
        - Involving data falsification → critical deviation
        - Other cases → minor deviations"""
        text = description.lower()
        
        # Check whether it is a critical deviation (data fraud)
        if re.search('forgery|tampering|false|falsif|fabricat', text):
            return Classification.CRITICAL, 0.98
        
        # Check for major deviations
        if safety_impact == RiskLevel.HIGH:
            return Classification.MAJOR, 0.95
        
        if data_impact == RiskLevel.HIGH or scientific_impact == RiskLevel.HIGH:
            return Classification.MAJOR, 0.90
        
        if safety_impact == RiskLevel.MEDIUM and (
            data_impact.score >= 2 or scientific_impact.score >= 2
        ):
            return Classification.MAJOR, 0.85
        
        # Check issues related to informed consent
        if re.search('Informed consent|Not obtained.*Consent|consent', text, re.IGNORECASE):
            if not re.search('non-critical|minor|delay|delay', text, re.IGNORECASE):
                return Classification.MAJOR, 0.92
        
        # Minor deviations in other cases
        if risk_score <= 4:
            confidence = 0.90 - (risk_score * 0.05)
        else:
            confidence = 0.70
        
        return Classification.MINOR, max(0.65, confidence)
    
    def _generate_rationale(
        self,
        classification: Classification,
        safety_impact: RiskLevel,
        data_impact: RiskLevel,
        scientific_impact: RiskLevel,
        description: str
    ) -> str:
        """Generate classification reasons"""
        reasons = []
        
        if classification == Classification.CRITICAL:
            reasons.append("Involving data forgery or tampering, seriously affecting the credibility of test data.")
        elif classification == Classification.MAJOR:
            reasons.append("This deviation has the following high-risk characteristics:")
            if safety_impact == RiskLevel.HIGH:
                reasons.append("-Seriously affecting subject safety")
            if data_impact == RiskLevel.HIGH:
                reasons.append("- Serious damage to data integrity")
            if scientific_impact == RiskLevel.HIGH:
                reasons.append("-Seriously damaging the scientific nature of the test")
            if safety_impact == RiskLevel.MEDIUM:
                reasons.append("- Moderate impact on subject safety")
            
            # Check informed consent
            if re.search('informed consent|consent', description, re.IGNORECASE):
                reasons.append("- Involving violations of informed consent procedures")
        else:
            reasons.append("This deviation has the following characteristics:")
            if safety_impact == RiskLevel.NONE:
                reasons.append("- Does not affect subject safety")
            if data_impact == RiskLevel.LOW:
                reasons.append("- Minor impact on data integrity")
            if scientific_impact == RiskLevel.NONE:
                reasons.append("- Does not affect the scientific nature of the test")
            
            # Check for minor time delays
            if re.search('delay|delay|postpone|postpone', description, re.IGNORECASE):
                reasons.append("- It is only a procedural delay and does not affect the core elements of the test")
        
        return "\n".join(reasons)
    
    def _extract_key_indicators(self, description: str, deviation_type: str) -> List[str]:
        """Extract key indicators"""
        indicators = []
        text = f"{description} {deviation_type}".lower()
        
        # Check for significant deviation indicators
        for category, patterns in self.major_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    indicator_map = {
                        'informed_consent': 'Informed consent issues',
                        'eligibility': 'Inclusion/exclusion criteria violations',
                        'dosing': 'Administration/Dosage Issues',
                        'concomitant': 'Concomitant medication violations',
                        'randomization': 'randomization problem',
                        'safety_reporting': 'Security reporting issues',
                        'blinding': 'blind violation',
                        'data_integrity': 'Data integrity issues',
                        'critical_procedures': 'Missing key procedures'
                    }
                    ind = indicator_map.get(category, category)
                    if ind not in indicators:
                        indicators.append(ind)
                    break
        
        # Check for minor deviation indicators
        for category, patterns in self.minor_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    indicator_map = {
                        'visit_window': 'Visit time window deviation',
                        'sample_collection': 'Sample collection bias',
                        'questionnaire': 'Questionnaire/Diary Card Bias',
                        'documentation': 'Document/Signature Delay',
                        'non_critical': 'Non-critical procedural deviations'
                    }
                    ind = indicator_map.get(category, category)
                    if ind not in indicators:
                        indicators.append(ind)
                    break
        
        return indicators[:5]  # Returns up to 5 indicators
    
    def _get_regulatory_basis(self, classification: Classification, description: str) -> List[str]:
        """Obtain regulatory basis"""
        basis = []
        text = description.lower()
        
        if classification == Classification.CRITICAL:
            basis = self.REGULATORY_BASIS['critical'].copy()
        elif classification == Classification.MAJOR:
            basis = self.REGULATORY_BASIS['major'].copy()
            
            # Add specific regulations based on description
            if re.search('informed consent|consent', text, re.IGNORECASE):
                basis.append("ICH E6(R2) Section 4.8 - Informed Consent Requirements")
            if re.search('Randomization|randomiz', text, re.IGNORECASE):
                basis.append("ICH E9 - Statistical Principles for Clinical Trials")
        else:
            basis = self.REGULATORY_BASIS['minor'].copy()
        
        return basis
    
    def _get_recommended_actions(self, classification: Classification) -> List[str]:
        """Get recommended actions"""
        if classification == Classification.CRITICAL:
            return [
                "Notify the sponsor and ethics committee immediately",
                "Initiate root cause investigation",
                "Implement corrective and preventive actions (CAPA)",
                "Consider blacklisting researchers",
                "Assess impact on overall trial data"
            ]
        elif classification == Classification.MAJOR:
            return [
                "Recorded in the deviation log",
                "Report to the sponsor within 24 hours",
                "Report to ethics committee (if required by protocol)",
                "Assess whether remedial action is needed",
                "Track trends and assess whether there is a systemic issue"
            ]
        else:
            return [
                "Recorded in the deviation log",
                "Follow trends",
                "Solved at the research center level",
                "Periodic summary reporting (e.g. quarterly)"
            ]
    
    def _generate_event_id(self) -> str:
        """Generate event ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"DEV-{timestamp}"
    
    def generate_report(self, results: List[ClassificationResult]) -> Dict:
        """Generate deviation classification report
        
        Args:
            results: list of classified results
        
        Returns:
            Dict: report dictionary"""
        if not results:
            return {"error": "No results to report"}
        
        total = len(results)
        major_count = sum(1 for r in results if r.classification == Classification.MAJOR)
        minor_count = sum(1 for r in results if r.classification == Classification.MINOR)
        critical_count = sum(1 for r in results if r.classification == Classification.CRITICAL)
        
        # Summarize various types of deviations
        by_category = {}
        for result in results:
            for indicator in result.key_indicators:
                by_category[indicator] = by_category.get(indicator, 0) + 1
        
        return {
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_deviations": total,
                "critical_count": critical_count,
                "major_count": major_count,
                "minor_count": minor_count,
                "major_rate": round(major_count / total * 100, 1) if total > 0 else 0,
                "minor_rate": round(minor_count / total * 100, 1) if total > 0 else 0
            },
            "category_breakdown": by_category,
            "critical_deviations": [
                r.to_dict() for r in results 
                if r.classification == Classification.CRITICAL
            ],
            "major_deviations": [
                r.to_dict() for r in results 
                if r.classification == Classification.MAJOR
            ],
            "minor_deviations": [
                r.to_dict() for r in results 
                if r.classification == Classification.MINOR
            ],
            "recommendations": self._generate_summary_recommendations(results)
        }
    
    def _generate_summary_recommendations(self, results: List[ClassificationResult]) -> List[str]:
        """Generate summary recommendations"""
        recommendations = []
        
        critical_count = sum(1 for r in results if r.classification == Classification.CRITICAL)
        major_count = sum(1 for r in results if r.classification == Classification.MAJOR)
        total = len(results)
        
        if critical_count > 0:
            recommendations.append(
                f"⚠️ Discover{critical_count}key deviation，Recommend immediate root cause analysis"
            )
        
        if total > 0:
            major_rate = major_count / total * 100
            if major_rate > 20:
                recommendations.append(
                    f"significant deviation rate({major_rate:.1f}%)On the high side，It is recommended to strengthen research center training"
                )
            elif major_rate > 10:
                recommendations.append(
                    f"significant deviation rate({major_rate:.1f}%)medium，It is recommended to pay close attention to"
                )
        
        # Check trends
        safety_issues = sum(
            1 for r in results 
            if r.safety_risk in [RiskLevel.HIGH, RiskLevel.MEDIUM]
        )
        if safety_issues > 3:
            recommendations.append(
                f"Discover{safety_issues}deviations involving safety issues，Recommend evaluation of subject protection measures"
            )
        
        if not recommendations:
            recommendations.append("Deviation control is generally good and it is recommended to continue to maintain it.")
        
        return recommendations


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Protocol Deviation Classifier - clinical trial protocol deviation classification tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  # Classify individual deviations
  python scripts/main.py classify -d "Subject visit delayed by 2 days"
  
  # Batch classification from files
  python scripts/main.py batch -i deviations.json -o report.json
  
  #Interactive classification
  python scripts/main.py interactive"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # classify command
    classify_parser = subparsers.add_parser("classify", help="Classify individual deviations")
    classify_parser.add_argument("-d", "--description", required=True, help="Deviation description")
    classify_parser.add_argument("-t", "--type", default="", help="Deviation type")
    classify_parser.add_argument("--id", default="", help="Event ID")
    classify_parser.add_argument("--safety-impact", 
                                 choices=["none", "low", "medium", "high"],
                                 default="none", help="security impact level")
    classify_parser.add_argument("--data-impact",
                                 choices=["none", "low", "medium", "high"],
                                 default="low", help="Data integrity impact level")
    classify_parser.add_argument("--scientific-impact",
                                 choices=["none", "low", "medium", "high"],
                                 default="none", help="scientific impact level")
    classify_parser.add_argument("-o", "--output", choices=["json", "table"], 
                                 default="table", help="Output format")
    
    # batch command
    batch_parser = subparsers.add_parser("batch", help="Batch classification")
    batch_parser.add_argument("-i", "--input", required=True, help="Enter JSON file path")
    batch_parser.add_argument("-o", "--output", default="", help="Output file path")
    batch_parser.add_argument("--format", choices=["json", "report"],
                              default="json", help="Output format")
    
    # report command
    report_parser = subparsers.add_parser("report", help="Generate summary report")
    report_parser.add_argument("-i", "--input", required=True, help="Classification results JSON file")
    
    # interactive command
    subparsers.add_parser("interactive", help="interactive classification")
    
    # demo command
    subparsers.add_parser("demo", help="Run sample classification")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    classifier = DeviationClassifier()
    
    try:
        if args.command == "classify":
            # Analyze impact levels
            safety = RiskLevel(args.safety_impact)
            data = RiskLevel(args.data_impact)
            scientific = RiskLevel(args.scientific_impact)
            
            result = classifier.classify(
                description=args.description,
                deviation_type=args.type,
                event_id=args.id,
                safety_impact=safety,
                data_impact=data,
                scientific_impact=scientific
            )
            
            if args.output == "json":
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                _print_table_result(result)
        
        elif args.command == "batch":
            # Read input file
            with open(args.input, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            results = classifier.classify_batch(events)
            
            if args.format == "report":
                report = classifier.generate_report(results)
                output = report
            else:
                output = [r.to_dict() for r in results]
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(output, f, ensure_ascii=False, indent=2)
                print(f"English: {args.output}")
            else:
                print(json.dumps(output, ensure_ascii=False, indent=2))
        
        elif args.command == "report":
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Assume that the input is a list of classification results
            if isinstance(data, list):
                # Convert to ClassificationResult object
                results = []
                for item in data:
                    result = ClassificationResult(
                        id=item.get('id', ''),
                        classification=Classification(item.get('classification_en', '').lower().split()[0]),
                        confidence=item.get('confidence', 0),
                        rationale=item.get('rationale', ''),
                        safety_risk=RiskLevel.NONE,
                        data_integrity_risk=RiskLevel.NONE,
                        scientific_validity_risk=RiskLevel.NONE,
                        risk_score=item.get('risk_score', 0),
                        regulatory_basis=item.get('regulatory_basis', []),
                        recommended_actions=item.get('recommended_actions', []),
                        key_indicators=item.get('key_indicators', [])
                    )
                    results.append(result)
                
                report = classifier.generate_report(results)
                print(json.dumps(report, ensure_ascii=False, indent=2))
        
        elif args.command == "interactive":
            _run_interactive(classifier)
        
        elif args.command == "demo":
            _run_demo(classifier)
    
    except Exception as e:
        print(f"mistake: {e}", file=sys.stderr)
        sys.exit(1)


def _print_table_result(result: ClassificationResult):
    """Print results in table format"""
    print("\n" + "=" * 60)
    print("Plan deviation classification result")
    print("=" * 60)
    print(f"{'Event ID:':<20} {result.id}")
    print(f"{'Classification results:':<20} {result.classification} ({result.classification.en_name})")
    print(f"{'Confidence:':<20} {result.confidence*100:.1f}%")
    print(f"{'Risk score:':<20} {result.risk_score}")
    print("-" * 60)
    print("risk assessment:")
    print(f"  - Subject safety: {result.safety_risk}")
    print(f"  - data integrity: {result.data_integrity_risk}")
    print(f"  - Experimental science: {result.scientific_validity_risk}")
    print("-" * 60)
    print("Reason for classification:")
    print(result.rationale)
    if result.key_indicators:
        print("-" * 60)
        print("Key indicators:")
        for indicator in result.key_indicators:
            print(f"  • {indicator}")
    print("-" * 60)
    print("Recommended actions:")
    for action in result.recommended_actions:
        print(f"  • {action}")
    print("=" * 60)


def _run_interactive(classifier: DeviationClassifier):
    """Run interactive classification"""
    print("\n" + "=" * 60)
    print("Solution Deviation Classifier - Interactive Mode")
    print("=" * 60)
    print("Type 'quit' or 'q' to exit")
    
    while True:
        print("\n" + "-" * 40)
        description = input("Please enter a description of the deviation:").strip()
        
        if description.lower() in ['quit', 'q', 'exit']:
            print("goodbye!")
            break
        
        if not description:
            print("Description cannot be empty, please re-enter.")
            continue
        
        deviation_type = input("Please enter deviation type (optional):").strip()
        
        print("Analyzing...")
        result = classifier.classify(
            description=description,
            deviation_type=deviation_type
        )
        
        _print_table_result(result)


def _run_demo(classifier: DeviationClassifier):
    """Run sample classification"""
    demo_cases = [
        {
            "id": "DEV-001",
            "description": "Subject visit will be delayed by 2 days",
            "type": "visit window"
        },
        {
            "id": "DEV-002",
            "description": "Collecting blood samples without obtaining informed consent",
            "type": "informed consent"
        },
        {
            "id": "DEV-003",
            "description": "Subject mistakenly takes double dose of study drug",
            "type": "Medication error"
        },
        {
            "id": "DEV-004",
            "description": "Submission of quality of life questionnaire delayed by 3 days",
            "type": "data collection"
        },
        {
            "id": "DEV-005",
            "description": "Subjects who did not meet the inclusion criteria were enrolled (age exceeded the limit)",
            "type": "Inclusion criteria"
        }
    ]
    
    print("\n" + "=" * 60)
    print("Scheme deviation classifier - example run")
    print("=" * 60)
    
    results = []
    for case in demo_cases:
        print(f"\n【Case {case['id']}】")
        print(f"describe: {case['description']}")
        print(f"type: {case['type']}")
        
        result = classifier.classify(
            description=case['description'],
            deviation_type=case['type'],
            event_id=case['id']
        )
        results.append(result)
        
        print(f"→ Classification results: {result.classification} (Confidence: {result.confidence*100:.0f}%)")
        print(f"   risk score: {result.risk_score}")
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("summary report")
    print("=" * 60)
    
    report = classifier.generate_report(results)
    summary = report['summary']
    
    print(f"Total deviations: {summary['total_deviations']}")
    print(f"critical deviation: {summary['critical_count']}")
    print(f"significant deviation: {summary['major_count']} ({summary['major_rate']}%)")
    print(f"small deviation: {summary['minor_count']} ({summary['minor_rate']}%)")
    
    print("suggestion:")
    for rec in report['recommendations']:
        print(f"  • {rec}")


if __name__ == "__main__":
    main()
