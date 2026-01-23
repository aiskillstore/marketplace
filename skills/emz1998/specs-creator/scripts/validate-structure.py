#!/usr/bin/env python3
"""
Specification Structure Validation Script

Validates that specification documents comply with their expected template structure.
Supports Product Specs (PRD), Technical Specs, Design Specs, API Specs, and System Specs.

Usage:
    python validate-structure.py <spec-file.md> [--type product|technical|design|api|system]

Returns:
    Exit code 0: Structure validation passed
    Exit code 1: Structure validation failed

Exceptions:
    FileNotFoundError: Specification file not found
    ValueError: File too large or invalid format
    PermissionError: Cannot read file
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# Constants
# =============================================================================

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_HEADINGS = 1000  # Maximum headings to process (DoS protection)
KEYWORD_MATCH_THRESHOLD = 0.5  # 50% of keywords required for section match
TOC_WORD_COUNT_THRESHOLD = 500  # Words before TOC is recommended
ALLOWED_EXTENSIONS = {'.md', '.markdown'}
FALLBACK_ENCODING = 'latin-1'


# =============================================================================
# Pre-compiled Regex Patterns
# =============================================================================

HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
PLACEHOLDER_PATTERNS = [
    re.compile(r'\[(?:TBD|TODO|PLACEHOLDER|XXX|FIXME|INSERT|FILL)\]', re.IGNORECASE),
    re.compile(r'\bTBD\b'),
    re.compile(r'\bTODO\b'),
    re.compile(r'\bFIXME\b'),
    re.compile(r'\bXXX\b'),
]
VERSION_PATTERN = re.compile(r'version|v\d+\.\d+', re.IGNORECASE)
DATE_PATTERN = re.compile(r'date|updated|last\s*modified', re.IGNORECASE)
AUTHOR_PATTERN = re.compile(r'author|written\s*by|created\s*by', re.IGNORECASE)
STATUS_PATTERN = re.compile(r'status|draft|review|approved', re.IGNORECASE)
TOC_PATTERN = re.compile(r'table\s+of\s+contents|##?\s*contents', re.IGNORECASE)
VALIDATION_CHECKLIST_PATTERN = re.compile(r'validation\s+checklist|review\s+checklist', re.IGNORECASE)


# =============================================================================
# Data Classes and Enums
# =============================================================================

class SpecType(Enum):
    PRODUCT = "product"
    TECHNICAL = "technical"
    DESIGN = "design"
    API = "api"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class Section:
    """Represents a required section in a spec"""
    name: str
    required: bool = True
    subsections: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass
class StructureResult:
    """Validation result for a structure check"""
    section: str
    found: bool
    message: str
    severity: str = "error"  # error, warning, info


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


# =============================================================================
# Validator Class
# =============================================================================

class StructureValidator:
    """Validates specification document structure against templates"""

    # Required sections for each spec type
    PRODUCT_SECTIONS = [
        Section("Executive Summary", required=True, keywords=["what", "why", "impact"]),
        Section("Problem Statement", required=True, keywords=["current situation", "user impact", "business impact"]),
        Section("Goals and Objectives", required=True, keywords=["primary goals", "business objectives"]),
        Section("User Personas", required=True, keywords=["persona", "demographics", "goals", "pain points"]),
        Section("User Stories", required=True, keywords=["as a", "i want", "so that", "acceptance criteria"]),
        Section("Requirements", required=True, subsections=["Functional Requirements", "Non-Functional Requirements"]),
        Section("User Experience and Flows", required=True, keywords=["user flow", "entry point", "steps"]),
        Section("Success Metrics", required=True, keywords=["kpi", "metrics", "target"]),
        Section("Dependencies", required=True, keywords=["internal", "external", "technical"]),
        Section("Out of Scope", required=True, keywords=["not included", "excluded"]),
    ]

    TECHNICAL_SECTIONS = [
        Section("Architecture Overview", required=True, keywords=["architecture", "system design"]),
        Section("Components", required=True, keywords=["component", "service", "module"]),
        Section("Data Models", required=True, keywords=["schema", "entity", "database", "model"]),
        Section("API", required=False, keywords=["endpoint", "interface", "api"]),
        Section("Security", required=True, keywords=["authentication", "authorization", "encryption"]),
        Section("Performance", required=True, keywords=["latency", "throughput", "response time"]),
        Section("Error Handling", required=True, keywords=["error", "exception", "failure"]),
        Section("Testing", required=True, keywords=["test", "unit", "integration"]),
        Section("Deployment", required=True, keywords=["deploy", "environment", "infrastructure"]),
    ]

    DESIGN_SECTIONS = [
        Section("Design Goals", required=True, keywords=["experience", "goal"]),
        Section("User Personas", required=True, keywords=["persona", "user type"]),
        Section("User Flows", required=True, keywords=["flow", "journey", "interaction"]),
        Section("Component Library", required=True, keywords=["component", "ui", "library"]),
        Section("Visual Design", required=True, keywords=["color", "typography", "spacing"]),
        Section("Interaction Patterns", required=True, keywords=["interaction", "pattern", "behavior"]),
        Section("Responsive", required=True, keywords=["responsive", "mobile", "tablet", "breakpoint"]),
        Section("Accessibility", required=True, keywords=["accessibility", "wcag", "a11y"]),
        Section("States", required=True, keywords=["state", "hover", "active", "disabled"]),
    ]

    API_SECTIONS = [
        Section("Base URL", required=True, keywords=["url", "endpoint", "base"]),
        Section("Authentication", required=True, keywords=["auth", "token", "api key", "oauth"]),
        Section("Endpoints", required=True, keywords=["get", "post", "put", "patch", "delete"]),
        Section("Request", required=True, keywords=["request", "body", "parameter", "header"]),
        Section("Response", required=True, keywords=["response", "status", "200", "201"]),
        Section("Error Codes", required=True, keywords=["400", "401", "403", "404", "500", "error"]),
        Section("Rate Limiting", required=True, keywords=["rate limit", "throttl", "quota"]),
        Section("Examples", required=True, keywords=["example", "sample"]),
    ]

    SYSTEM_SECTIONS = [
        Section("Executive Summary", required=True, subsections=["Purpose", "Scope", "Stakeholders"]),
        Section("System Overview", required=True, keywords=["description", "business context", "features"]),
        Section("System Context", required=True, keywords=["context diagram", "external systems"]),
        Section("System Architecture", required=True, keywords=["architecture", "component", "communication"]),
        Section("System Requirements", required=True, subsections=["Functional Requirements", "Non-Functional Requirements"]),
        Section("External Interfaces", required=True, keywords=["api", "integration", "third-party"]),
        Section("Data Architecture", required=True, keywords=["data store", "data flow", "retention"]),
        Section("Security & Compliance", required=True, keywords=["security", "compliance", "authentication"]),
        Section("Deployment Architecture", required=True, keywords=["environment", "infrastructure", "scaling"]),
        Section("Operations & Monitoring", required=True, keywords=["monitoring", "alerting", "logging"]),
        Section("Quality Attributes", required=True, keywords=["performance", "scalability", "resilience"]),
        Section("Constraints & Assumptions", required=True, keywords=["constraint", "assumption"]),
        Section("Risks & Mitigation", required=True, keywords=["risk", "mitigation", "probability"]),
    ]

    def __init__(self, file_path: str, spec_type: Optional[str] = None):
        self.file_path = Path(file_path).resolve()  # Canonical path
        self._validate_file_path()
        self.content = self._read_file()
        self.spec_type = SpecType(spec_type) if spec_type else self._detect_spec_type()
        self.results: List[StructureResult] = []
        self.sections_found: List[str] = []

    def _validate_file_path(self) -> None:
        """Validate file path before reading"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Specification file not found: {self.file_path}")

        if not self.file_path.is_file():
            raise ValueError(f"Path is not a file: {self.file_path}")

        if self.file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file extension. Expected {ALLOWED_EXTENSIONS}, got: {self.file_path.suffix}")

        file_size = self.file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE} bytes)")

    def _read_file(self) -> str:
        """Read specification file with proper error handling"""
        try:
            return self.file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with fallback encoding
            try:
                return self.file_path.read_text(encoding=FALLBACK_ENCODING)
            except Exception as e:
                raise ValueError(f"Cannot decode file content: {e}")
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {self.file_path}")

    def _detect_spec_type(self) -> SpecType:
        """Detect specification type from filename or content"""
        filename = self.file_path.name.lower()

        type_mapping = [
            (["product", "prd"], SpecType.PRODUCT),
            (["technical", "tech-spec", "tech_spec"], SpecType.TECHNICAL),
            (["design", "ui", "ux"], SpecType.DESIGN),
            (["api", "endpoint", "openapi"], SpecType.API),
            (["system", "srs", "architecture"], SpecType.SYSTEM),
        ]

        for keywords, spec_type in type_mapping:
            if any(kw in filename for kw in keywords):
                return spec_type

        # Content-based detection using already-loaded content
        content_lower = self.content.lower()

        if "user stories" in content_lower and "user personas" in content_lower:
            return SpecType.PRODUCT
        elif "architecture" in content_lower and "component" in content_lower:
            return SpecType.TECHNICAL
        elif "user flow" in content_lower and "accessibility" in content_lower:
            return SpecType.DESIGN
        elif "endpoint" in content_lower and "rate limit" in content_lower:
            return SpecType.API

        return SpecType.UNKNOWN

    def _get_required_sections(self) -> List[Section]:
        """Get required sections based on spec type"""
        section_map = {
            SpecType.PRODUCT: self.PRODUCT_SECTIONS,
            SpecType.TECHNICAL: self.TECHNICAL_SECTIONS,
            SpecType.DESIGN: self.DESIGN_SECTIONS,
            SpecType.API: self.API_SECTIONS,
            SpecType.SYSTEM: self.SYSTEM_SECTIONS,
        }
        return section_map.get(self.spec_type, [])

    def _extract_headings(self) -> List[Tuple[int, str]]:
        """Extract all markdown headings with their levels (limited for DoS protection)"""
        headings = []
        for match in HEADING_PATTERN.finditer(self.content):
            if len(headings) >= MAX_HEADINGS:
                break  # DoS protection
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append((level, title))
        return headings

    def _section_exists(self, section: Section) -> bool:
        """Check if a section exists in the document"""
        headings = self._extract_headings()
        section_name_lower = section.name.lower()
        content_lower = self.content.lower()

        for _, title in headings:
            title_lower = title.lower()
            # Direct match or close match
            if section_name_lower in title_lower or title_lower in section_name_lower:
                self.sections_found.append(title)
                return True

        # Check by keywords if no direct match
        if section.keywords:
            keyword_count = sum(1 for kw in section.keywords if kw.lower() in content_lower)
            required_matches = max(1, int(len(section.keywords) * KEYWORD_MATCH_THRESHOLD))
            if keyword_count >= required_matches:
                return True

        return False

    def _check_subsections(self, section: Section) -> List[str]:
        """Check if required subsections exist"""
        missing = []
        content_lower = self.content.lower()
        for subsection in section.subsections:
            subsection_lower = subsection.lower()
            if subsection_lower not in content_lower:
                missing.append(subsection)
        return missing

    def _check_document_metadata(self) -> None:
        """Check for required document metadata"""
        metadata_checks = [
            ("Version", VERSION_PATTERN),
            ("Date", DATE_PATTERN),
            ("Author", AUTHOR_PATTERN),
            ("Status", STATUS_PATTERN),
        ]

        for item_name, pattern in metadata_checks:
            if not pattern.search(self.content):
                self.results.append(StructureResult(
                    section=f"Metadata: {item_name}",
                    found=False,
                    message=f"Missing {item_name} in document metadata",
                    severity="warning"
                ))

    def _check_table_of_contents(self) -> None:
        """Check if long documents have a table of contents"""
        word_count = len(self.content.split())
        has_toc = bool(TOC_PATTERN.search(self.content))

        if word_count > TOC_WORD_COUNT_THRESHOLD and not has_toc:
            self.results.append(StructureResult(
                section="Table of Contents",
                found=False,
                message=f"Document has {word_count} words but no Table of Contents",
                severity="warning"
            ))

    def _check_validation_checklist(self) -> None:
        """Check if document has a validation checklist"""
        has_checklist = bool(VALIDATION_CHECKLIST_PATTERN.search(self.content))

        self.results.append(StructureResult(
            section="Validation Checklist",
            found=has_checklist,
            message="Document should include a validation checklist" if not has_checklist else "Validation checklist present",
            severity="info"
        ))

    def _check_placeholder_content(self) -> None:
        """Check for unfilled placeholder content"""
        placeholders_found = []

        for pattern in PLACEHOLDER_PATTERNS:
            matches = pattern.findall(self.content)
            placeholders_found.extend(matches)

        if placeholders_found:
            unique_placeholders = list(set(placeholders_found[:5]))
            self.results.append(StructureResult(
                section="Placeholder Content",
                found=True,
                message=f"Found {len(placeholders_found)} placeholders: {', '.join(unique_placeholders)}",
                severity="warning"
            ))

    def _run_metadata_checks(self) -> None:
        """Run all metadata-related checks"""
        self._check_document_metadata()
        self._check_table_of_contents()

    def _run_section_checks(self) -> None:
        """Run all section-related checks"""
        required_sections = self._get_required_sections()

        for section in required_sections:
            found = self._section_exists(section)
            severity = "error" if section.required else "warning"

            result = StructureResult(
                section=section.name,
                found=found,
                message=f"Required section '{section.name}' not found" if not found else f"Section '{section.name}' found",
                severity=severity if not found else "info"
            )
            self.results.append(result)

            # Check subsections if section exists
            if found and section.subsections:
                missing_subsections = self._check_subsections(section)
                if missing_subsections:
                    self.results.append(StructureResult(
                        section=f"{section.name} - Subsections",
                        found=False,
                        message=f"Missing subsections: {', '.join(missing_subsections)}",
                        severity="warning"
                    ))

    def _run_content_checks(self) -> None:
        """Run all content-related checks"""
        self._check_placeholder_content()
        self._check_validation_checklist()

    def _print_header(self) -> None:
        """Print validation header"""
        print(f"\n{'='*60}")
        print(f"STRUCTURE VALIDATION: {self.file_path.name}")
        print(f"Detected Type: {self.spec_type.value.upper()}")
        print(f"{'='*60}\n")

        if self.spec_type == SpecType.UNKNOWN:
            print("Warning: Could not detect spec type. Using generic validation.")
            print("Tip: Use --type flag to specify spec type explicitly.\n")

    def validate(self) -> bool:
        """Run structure validation"""
        self._print_header()
        self._run_metadata_checks()
        self._run_section_checks()
        self._run_content_checks()
        return self._print_results()

    def _print_results(self) -> bool:
        """Print validation results"""
        # Group by severity
        errors = [r for r in self.results if r.severity == "error" and not r.found]
        warnings = [r for r in self.results if r.severity == "warning" and not r.found]

        required_sections = self._get_required_sections()

        # Print sections found
        print("REQUIRED SECTIONS:")
        print("-" * 60)

        for section in required_sections:
            result = next((r for r in self.results if r.section == section.name), None)
            if result:
                if result.found:
                    status = "\033[92m[FOUND]\033[0m"
                elif section.required:
                    status = "\033[91m[MISSING]\033[0m"
                else:
                    status = "\033[93m[OPTIONAL]\033[0m"
                print(f"  {status} {section.name}")

        # Print errors
        if errors:
            print(f"\n\033[91mERRORS ({len(errors)}):\033[0m")
            print("-" * 60)
            for result in errors:
                print(f"  [x] {result.section}")
                print(f"      {result.message}")

        # Print warnings
        if warnings:
            print(f"\n\033[93mWARNINGS ({len(warnings)}):\033[0m")
            print("-" * 60)
            for result in warnings:
                print(f"  [!] {result.section}")
                print(f"      {result.message}")

        # Summary
        total_required = len([s for s in required_sections if s.required])
        found_required = len([r for r in self.results
                            if r.found and r.section in [s.name for s in required_sections if s.required]])

        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Required sections: {found_required}/{total_required}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")

        if len(errors) == 0:
            print(f"\n\033[92mStructure validation PASSED\033[0m")
            return True
        else:
            print(f"\n\033[91mStructure validation FAILED\033[0m")
            print("Please add the missing required sections before proceeding.")
            return False


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> int:
    """Main entry point - returns exit code"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate specification document structure compliance"
    )
    parser.add_argument(
        "file",
        help="Path to specification file (.md)"
    )
    parser.add_argument(
        "--type",
        choices=["product", "technical", "design", "api", "system"],
        help="Specification type (auto-detected if not provided)"
    )

    args = parser.parse_args()

    try:
        validator = StructureValidator(args.file, args.type)
        passed = validator.validate()
        return 0 if passed else 1
    except FileNotFoundError as e:
        print(f"\033[91mError:\033[0m {e}")
        return 1
    except ValueError as e:
        print(f"\033[91mValidation Error:\033[0m {e}")
        return 1
    except PermissionError as e:
        print(f"\033[91mPermission Error:\033[0m {e}")
        return 1
    except Exception as e:
        print(f"\033[91mUnexpected Error:\033[0m {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
