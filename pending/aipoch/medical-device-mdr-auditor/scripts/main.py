#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Medical Device MDR Auditor
Check technical documentation compliance against EU MDR 2017/745 regulations

Author: OpenClaw Skill Development Team
Version: 1.0.0"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any


class ComplianceStatus(Enum):
    """Compliance status"""
    COMPLIANT = "COMPLIANT"
    PARTIAL = "PARTIAL"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN = "UNKNOWN"


class FindingCategory(Enum):
    """Discover problem categories"""
    CRITICAL = "CRITICAL"      # Critical deficiencies - may lead to non-compliance
    MAJOR = "MAJOR"            # Major flaws - need to be corrected
    MINOR = "MINOR"            # Minor flaws - suggested improvements
    INFO = "INFO"              # Information prompt


class CheckStatus(Enum):
    """check status"""
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    INCOMPLETE = "INCOMPLETE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Finding:
    """Audit found problems"""
    category: FindingCategory
    regulation: str
    item: str
    status: CheckStatus
    description: str
    file_path: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class AuditSummary:
    """Review summary"""
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    failed: int = 0


@dataclass
class AuditReport:
    """audit report"""
    audit_date: str = ""
    device_class: str = ""
    input_path: str = ""
    compliance_status: ComplianceStatus = ComplianceStatus.UNKNOWN
    findings: List[Finding] = field(default_factory=list)
    summary: AuditSummary = field(default_factory=AuditSummary)


class MDRChecker:
    """MDR Compliance Checker"""

    # Key document requirements of MDR regulations
    REQUIRED_DOCUMENTS = {
        "I": [
            ("Clinical Evaluation", "clinical assessment", False),  # Class I optional
            ("Risk Management", "risk management documents", True),
            ("Technical Documentation", "Technical documentation", True),
            ("Post-Market Surveillance", "Post-market surveillance plan", True),
        ],
        "IIa": [
            ("Clinical Evaluation Report", "clinical evaluation report", True),
            ("Clinical Evaluation Plan", "clinical assessment plan", True),
            ("Risk Management", "risk management documents", True),
            ("Technical Documentation", "Technical documentation", True),
            ("Post-Market Surveillance Plan", "Post-market surveillance plan", True),
            ("PMCF Plan", "Post-marketing clinical follow-up plan", True),
        ],
        "IIb": [
            ("Clinical Evaluation Report", "clinical evaluation report", True),
            ("Clinical Evaluation Plan", "clinical assessment plan", True),
            ("Risk Management", "risk management documents", True),
            ("Technical Documentation", "Technical documentation", True),
            ("Post-Market Surveillance Plan", "Post-market surveillance plan", True),
            ("PMCF Plan", "Post-marketing clinical follow-up plan", True),
            ("SSCP", "Safety and clinical performance summary", True),
        ],
        "III": [
            ("Clinical Evaluation Report", "clinical evaluation report", True),
            ("Clinical Evaluation Plan", "clinical assessment plan", True),
            ("Risk Management", "risk management documents", True),
            ("Technical Documentation", "Technical documentation", True),
            ("Post-Market Surveillance Plan", "Post-market surveillance plan", True),
            ("PMCF Plan", "Post-marketing clinical follow-up plan", True),
            ("SSCP", "Safety and clinical performance summary", True),
            ("PMCF Evaluation Report", "PMCF Assessment Report", True),
        ],
    }

    # File keyword mapping
    FILE_PATTERNS = {
        "Clinical Evaluation Report": [
            r"clinical[_\s]?evaluation[_\s]?report",
            r"cer[_\s]?",
            "clinical evaluation report",
            "clinical evaluation report",
        ],
        "Clinical Evaluation Plan": [
            r"clinical[_\s]?evaluation[_\s]?plan",
            r"cep[_\s]?",
            "clinical assessment plan",
            "clinical evaluation plan",
        ],
        "Risk Management": [
            r"risk[_\s]?management",
            "risk management",
            r"iso[_\s]?14971",
        ],
        "Post-Market Surveillance Plan": [
            r"post[_\s]?market[_\s]?surveillance",
            r"pms[_\s]?plan",
            "Post-market surveillance plan",
            "Post-market surveillance plan",
        ],
        "PMCF Plan": [
            r"pmcf[_\s]?plan",
            r"post[_\s]?market[_\s]?clinical[_\s]?follow[_\s]?up",
            "Post-marketing clinical follow-up",
            "pmcf[_\\s]?Evaluation",
        ],
        "SSCP": [
            r"sscp",
            r"summary[_\s]?of[_\s]?safety[_\s]?and[_\s]?clinical[_\s]?performance",
            "Safety and clinical performance summary",
        ],
        "PMCF Evaluation Report": [
            r"pmcf[_\s]?evaluation[_\s]?report",
            r"pmcf[_\s]?report",
            "pmcf assessment report",
        ],
    }

    def __init__(self, input_path: str, device_class: str, verbose: bool = False):
        self.input_path = Path(input_path)
        self.device_class = device_class.upper()
        self.verbose = verbose
        self.found_files: Dict[str, List[Path]] = {}
        self.report = AuditReport(
            audit_date=datetime.utcnow().isoformat() + "Z",
            device_class=self.device_class,
            input_path=str(self.input_path.absolute()),
        )

    def log(self, message: str):
        """Output log"""
        if self.verbose:
            print(f"[MDR Auditor] {message}")

    def scan_files(self) -> Dict[str, List[Path]]:
        """Scan a directory for files"""
        self.log(f"Scan directory: {self.input_path}")
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input path does not exist: {self.input_path}")

        found = {}
        all_files = list(self.input_path.rglob("*"))
        
        for doc_type, patterns in self.FILE_PATTERNS.items():
            found[doc_type] = []
            for file_path in all_files:
                if file_path.is_file():
                    file_name = file_path.name.lower()
                    for pattern in patterns:
                        if re.search(pattern, file_name, re.IGNORECASE):
                            found[doc_type].append(file_path)
                            self.log(f"find file: {doc_type} -> {file_path}")
                            break
        
        self.found_files = found
        return found

    def check_document_completeness(self, doc_type: str, files: List[Path]) -> Finding:
        """Check document completeness"""
        required_docs = self.REQUIRED_DOCUMENTS.get(self.device_class, [])
        is_required = any(d[0] == doc_type and d[2] for d in required_docs)
        
        if not files:
            if is_required:
                return Finding(
                    category=FindingCategory.CRITICAL,
                    regulation=self._get_regulation_ref(doc_type),
                    item=doc_type,
                    status=CheckStatus.MISSING,
                    description=f"not found{doc_type}Related documents",
                    recommendation=f"according toMDRRequire，required{doc_type}"
                )
            else:
                return Finding(
                    category=FindingCategory.INFO,
                    regulation=self._get_regulation_ref(doc_type),
                    item=doc_type,
                    status=CheckStatus.MISSING,
                    description=f"not found{doc_type}（forClass {self.device_class}is optional）",
                    recommendation="Recommendations provided to enhance compliance"
                )
        
        # Check file content integrity (simplified checking)
        for file_path in files:
            if file_path.stat().st_size < 1000:  # Less than 1KB may be an empty file or placeholder
                return Finding(
                    category=FindingCategory.MAJOR,
                    regulation=self._get_regulation_ref(doc_type),
                    item=doc_type,
                    status=CheckStatus.INCOMPLETE,
                    description=f"{doc_type}File may be incomplete（File too small）: {file_path.name}",
                    file_path=str(file_path),
                    recommendation="Please check file content integrity"
                )
        
        return Finding(
            category=FindingCategory.INFO,
            regulation=self._get_regulation_ref(doc_type),
            item=doc_type,
            status=CheckStatus.PRESENT,
            description=f"turn up{doc_type}document: {len(files)}indivual",
            file_path=str(files[0]) if files else None
        )

    def _get_regulation_ref(self, doc_type: str) -> str:
        """Get regulatory citations"""
        regulation_map = {
            "Clinical Evaluation Report": "MDR Annex XIV Part A",
            "Clinical Evaluation Plan": "MDR Annex XIV Part A",
            "Risk Management": "MDR Annex I & EN ISO 14971",
            "Post-Market Surveillance Plan": "MDR Article 83 & Annex III",
            "PMCF Plan": "MDR Annex XIV Part B",
            "SSCP": "MDR Article 32",
            "PMCF Evaluation Report": "MDR Annex XIV Part B",
        }
        return regulation_map.get(doc_type, "MDR 2017/745")

    def check_cer_content(self, files: List[Path]) -> Optional[Finding]:
        """Check CER content requirements"""
        if not files:
            return None
        
        cer_file = files[0]
        try:
            content = self._read_file_content(cer_file)
            required_sections = [
                ("clinical assessment plan", FindingCategory.MAJOR),
                ("clinical data", FindingCategory.CRITICAL),
                ("risk return", FindingCategory.CRITICAL),
                ("Equivalent equipment", FindingCategory.MAJOR),
                ("SOTA", FindingCategory.MAJOR),
            ]
            
            missing_sections = []
            for section, severity in required_sections:
                if section not in content:
                    missing_sections.append((section, severity))
            
            if missing_sections:
                critical_missing = [s for s, c in missing_sections if c == FindingCategory.CRITICAL]
                major_missing = [s for s, c in missing_sections if c == FindingCategory.MAJOR]
                
                return Finding(
                    category=FindingCategory.CRITICAL if critical_missing else FindingCategory.MAJOR,
                    regulation="MDR Annex XIV Part A",
                    item="Clinical Evaluation Report - Content",
                    status=CheckStatus.INCOMPLETE,
                    description=f"CERIncomplete content: Missing key parts - {', '.join([s for s, c in missing_sections])}",
                    file_path=str(cer_file),
                    recommendation="Please add missing CER chapters"
                )
        except Exception as e:
            return Finding(
                category=FindingCategory.MINOR,
                regulation="MDR Annex XIV Part A",
                item="Clinical Evaluation Report",
                status=CheckStatus.UNKNOWN,
                description=f"Unable to readCERdocument: {str(e)}",
                file_path=str(cer_file)
            )
        
        return None

    def check_pms_content(self, files: List[Path]) -> Optional[Finding]:
        """Check PMS plan content requirements"""
        if not files:
            return None
        
        pms_file = files[0]
        try:
            content = self._read_file_content(pms_file)
            required_elements = [
                "data collection",
                "trend report",
                "risk assessment",
                "alert system",
            ]
            
            missing = [e for e in required_elements if e not in content]
            
            if missing:
                return Finding(
                    category=FindingCategory.MAJOR,
                    regulation="MDR Article 83 & Annex III",
                    item="PMS Plan - Content",
                    status=CheckStatus.INCOMPLETE,
                    description=f"PMSPlan content is incomplete: Lack - {', '.join(missing)}",
                    file_path=str(pms_file),
                    recommendation="Please complete the PMS plan in accordance with the requirements of MDR Annex III"
                )
        except Exception as e:
            return Finding(
                category=FindingCategory.MINOR,
                regulation="MDR Article 83 & Annex III",
                item="PMS Plan",
                status=CheckStatus.UNKNOWN,
                description=f"Unable to readPMSdocument: {str(e)}",
                file_path=str(pms_file)
            )
        
        return None

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content (supports multiple formats)"""
        try:
            if file_path.suffix.lower() in ['.pdf']:
                return self._extract_pdf_text(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return self._extract_docx_text(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            self.log(f"Failed to read file {file_path}: {e}")
            return ""

    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract PDF text (simplified implementation)"""
        # Actual implementation requires the use of PyPDF2 or pdfplumber
        # This returns the filename as a simplified check
        return file_path.stem

    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract Word text (simplified implementation)"""
        # The actual implementation requires the use of python-docx
        # This returns the filename as a simplified check
        return file_path.stem

    def run_audit(self) -> AuditReport:
        """Perform review"""
        self.log(f"Start review - Device classification: Class {self.device_class}")
        
        # Scan files
        found_files = self.scan_files()
        
        # Check all required documents
        all_findings = []
        checked_items = set()
        
        # Check document existence and basic integrity
        for doc_type, files in found_files.items():
            finding = self.check_document_completeness(doc_type, files)
            all_findings.append(finding)
            checked_items.add(doc_type)
        
        # Check for types not found
        required_docs = self.REQUIRED_DOCUMENTS.get(self.device_class, [])
        for doc_type, name, is_required in required_docs:
            if doc_type not in checked_items:
                finding = self.check_document_completeness(doc_type, [])
                all_findings.append(finding)
        
        # In-depth inspection of CER content
        cer_files = found_files.get("Clinical Evaluation Report", [])
        if cer_files:
            cer_finding = self.check_cer_content(cer_files)
            if cer_finding:
                all_findings.append(cer_finding)
        
        # In-depth inspection of PMS content
        pms_files = found_files.get("Post-Market Surveillance Plan", [])
        if pms_files:
            pms_finding = self.check_pms_content(pms_files)
            if pms_finding:
                all_findings.append(pms_finding)
        
        # Summary results
        critical_count = sum(1 for f in all_findings if f.category == FindingCategory.CRITICAL and f.status != CheckStatus.PRESENT)
        major_count = sum(1 for f in all_findings if f.category == FindingCategory.MAJOR and f.status != CheckStatus.PRESENT)
        minor_count = sum(1 for f in all_findings if f.category == FindingCategory.MINOR and f.status != CheckStatus.PRESENT)
        
        self.report.findings = all_findings
        self.report.summary = AuditSummary(
            total_checks=len(all_findings),
            passed=sum(1 for f in all_findings if f.status == CheckStatus.PRESENT),
            warnings=minor_count,
            failed=critical_count + major_count
        )
        
        # Determine overall compliance status
        if critical_count > 0:
            self.report.compliance_status = ComplianceStatus.NON_COMPLIANT
        elif major_count > 0:
            self.report.compliance_status = ComplianceStatus.PARTIAL
        else:
            self.report.compliance_status = ComplianceStatus.COMPLIANT
        
        self.log(f"Review completed - state: {self.report.compliance_status.value}")
        return self.report

    def to_json(self) -> str:
        """Convert report to JSON"""
        def serialize(obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, (AuditReport, AuditSummary, Finding)):
                return {k: serialize(v) for k, v in asdict(obj).items()}
            if isinstance(obj, list):
                return [serialize(item) for item in obj]
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            return obj
        
        return json.dumps(serialize(self.report), ensure_ascii=False, indent=2)


def load_config(config_path: str) -> List[Dict[str, Any]]:
    """Load configuration file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if isinstance(config, dict):
        return [config]
    return config


def main():
    parser = argparse.ArgumentParser(
        description='Medical Device MDR Auditor - EU MDR 2017/745 compliance checking tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  # Check a single technical documentation directory
  %(prog)s --input /path/to/technical/file --class IIa
  
  # Use configuration files for batch checking
  %(prog)s --config /path/to/config.json
  
  # Output detailed report to file
  %(prog)s --input /path/to/technical/file --class III --verbose --output report.json"""
    )
    
    parser.add_argument('--input', '-i', help='Technical documentation directory path')
    parser.add_argument('--config', '-c', help='JSON configuration file path')
    parser.add_argument('--class', dest='device_class', 
                       choices=['I', 'IIa', 'IIb', 'III'],
                       help='Medical device classification (I, IIa, IIb, III)')
    parser.add_argument('--output', '-o', help='Output report path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Output details')
    
    args = parser.parse_args()
    
    # Validation parameters
    if not args.config and (not args.input or not args.device_class):
        parser.error("Must provide --config or both --input and --class")
    
    results = []
    exit_code = 0
    
    try:
        if args.config:
            # Batch inspection
            configs = load_config(args.config)
            for config in configs:
                checker = MDRChecker(
                    input_path=config['input'],
                    device_class=config.get('class', 'IIa'),
                    verbose=args.verbose
                )
                report = checker.run_audit()
                results.append(report)
                
                if report.compliance_status == ComplianceStatus.NON_COMPLIANT:
                    exit_code = 2
                elif exit_code == 0 and report.compliance_status == ComplianceStatus.PARTIAL:
                    exit_code = 1
        else:
            # single check
            checker = MDRChecker(
                input_path=args.input,
                device_class=args.device_class,
                verbose=args.verbose
            )
            report = checker.run_audit()
            results.append(report)
            
            if report.compliance_status == ComplianceStatus.NON_COMPLIANT:
                exit_code = 2
            elif report.compliance_status == ComplianceStatus.PARTIAL:
                exit_code = 1
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if len(results) == 1:
                    f.write(checker.to_json())
                else:
                    f.write(json.dumps([checker.to_json() for _ in results], ensure_ascii=False, indent=2))
            print(f"Report saved to: {args.output}")
        else:
            if len(results) == 1:
                print(checker.to_json())
            else:
                print(json.dumps([checker.to_json() for _ in results], ensure_ascii=False, indent=2))
        
        # Print summary
        print("\n" + "="*60)
        print("Review summary")
        print("="*60)
        for i, report in enumerate(results, 1):
            if len(results) > 1:
                print(f"\nCheck items #{i}:")
            print(f"  path: {report.input_path}")
            print(f"  Classification: Class {report.device_class}")
            print(f"  state: {report.compliance_status.value}")
            print(f"  total: {report.summary.total_checks} | pass: {report.summary.passed} | warn: {report.summary.warnings} | fail: {report.summary.failed}")
            
            critical = [f for f in report.findings if f.category == FindingCategory.CRITICAL and f.status != CheckStatus.PRESENT]
            if critical:
                print(f"\n  key questions:")
                for f in critical:
                    print(f"    ⚠️  {f.item}: {f.description}")
        
        sys.exit(exit_code)
        
    except FileNotFoundError as e:
        print(f"mistake: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"execution error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == '__main__':
    main()
