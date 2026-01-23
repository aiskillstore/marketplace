#!/usr/bin/env python3
"""
Specification Validation Script

Validates specification documents for completeness, clarity, and consistency.
Can be used for Product Specs, Technical Specs, Design Specs, and API Specs.

Usage:
    python validate-spec.py <spec-file.md> [--type product|technical|design|api]

Returns:
    Exit code 0: All validations passed
    Exit code 1: Validation failures found
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Validation result for a single check"""
    category: str
    check: str
    passed: bool
    message: str


class SpecValidator:
    """Validates specification documents"""

    def __init__(self, file_path: str, spec_type: str = None):
        self.file_path = Path(file_path)
        self.spec_type = spec_type or self._detect_spec_type()
        self.content = self._read_file()
        self.results: List[ValidationResult] = []

    def _read_file(self) -> str:
        """Read specification file"""
        try:
            return self.file_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            print(f"Error: File not found: {self.file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

    def _detect_spec_type(self) -> str:
        """Detect specification type from filename or content"""
        filename = self.file_path.name.lower()

        if 'product' in filename or 'prd' in filename:
            return 'product'
        elif 'technical' in filename or 'tech' in filename:
            return 'technical'
        elif 'design' in filename:
            return 'design'
        elif 'api' in filename:
            return 'api'
        else:
            return 'unknown'

    def validate(self) -> bool:
        """Run all validations"""
        print(f"\n{'='*60}")
        print(f"Validating {self.spec_type.upper()} specification: {self.file_path.name}")
        print(f"{'='*60}\n")

        # Common validations
        self._validate_document_structure()
        self._validate_clarity()
        self._validate_completeness()
        self._validate_consistency()

        # Type-specific validations
        if self.spec_type == 'product':
            self._validate_product_spec()
        elif self.spec_type == 'technical':
            self._validate_technical_spec()
        elif self.spec_type == 'design':
            self._validate_design_spec()
        elif self.spec_type == 'api':
            self._validate_api_spec()

        return self._print_results()

    def _add_result(self, category: str, check: str, passed: bool, message: str = ""):
        """Add validation result"""
        self.results.append(ValidationResult(category, check, passed, message))

    def _validate_document_structure(self):
        """Validate basic document structure"""
        category = "Document Structure"

        # Check for title/heading
        has_title = bool(re.search(r'^#{1,2}\s+.+', self.content, re.MULTILINE))
        self._add_result(
            category,
            "Has main title",
            has_title,
            "Document should start with a clear title (# or ##)"
        )

        # Check for sections
        sections = re.findall(r'^#{2,3}\s+(.+)', self.content, re.MULTILINE)
        has_sections = len(sections) >= 3
        self._add_result(
            category,
            "Has multiple sections",
            has_sections,
            f"Found {len(sections)} sections. Good specifications should have at least 3 sections."
        )

        # Check for table of contents (optional but recommended for long docs)
        lines = self.content.split('\n')
        word_count = len(self.content.split())
        has_toc = 'table of contents' in self.content.lower()

        if word_count > 1000 and not has_toc:
            self._add_result(
                category,
                "Has table of contents",
                False,
                "Long documents (>1000 words) should include a table of contents"
            )

    def _validate_clarity(self):
        """Validate clarity of specification"""
        category = "Clarity"

        # Check for vague terms
        vague_terms = ['fast', 'slow', 'easy', 'simple', 'user-friendly', 'secure',
                       'performant', 'scalable', 'robust', 'flexible']
        found_vague = []

        for term in vague_terms:
            # Look for standalone vague terms (not as part of specific measurements)
            pattern = rf'\b{term}\b(?!\s*\(|\s*:|\s*-)'
            if re.search(pattern, self.content, re.IGNORECASE):
                found_vague.append(term)

        no_vague_terms = len(found_vague) == 0
        self._add_result(
            category,
            "No vague terms without definition",
            no_vague_terms,
            f"Found vague terms: {', '.join(found_vague[:5])}. Define or quantify these terms." if found_vague else ""
        )

        # Check for examples
        has_examples = bool(re.search(r'example|e\.g\.|for instance', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Includes examples",
            has_examples,
            "Good specifications include concrete examples"
        )

        # Check for specific numbers/measurements
        has_metrics = bool(re.search(r'\d+\s*(ms|seconds|%|percent|users|requests)', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Includes measurable criteria",
            has_metrics,
            "Specifications should include quantifiable requirements"
        )

    def _validate_completeness(self):
        """Validate completeness of specification"""
        category = "Completeness"

        # Check for acceptance criteria
        has_acceptance = bool(re.search(r'acceptance criteria|success criteria', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Defines acceptance criteria",
            has_acceptance,
            "Specifications should include clear acceptance or success criteria"
        )

        # Check for out of scope section
        has_out_of_scope = bool(re.search(r'out of scope|not included|excluded', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Defines out of scope items",
            has_out_of_scope,
            "Explicitly stating what's excluded helps prevent scope creep"
        )

        # Check for dependencies
        has_dependencies = bool(re.search(r'dependencies|depends on|requires', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Lists dependencies",
            has_dependencies,
            "Document any dependencies on other systems, teams, or features"
        )

    def _validate_consistency(self):
        """Validate consistency of specification"""
        category = "Consistency"

        # Check for consistent terminology
        # Look for multiple terms for same concept
        auth_terms = len(set(re.findall(r'\b(auth(?:entication)?|login|sign[- ]?in)\b', self.content, re.IGNORECASE)))
        if auth_terms > 1:
            self._add_result(
                category,
                "Consistent authentication terminology",
                False,
                f"Found {auth_terms} different terms for authentication. Use consistent terminology."
            )

        # Check date format consistency
        date_formats = set(re.findall(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}', self.content))
        iso_dates = set(re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', self.content))

        inconsistent_dates = len(date_formats) > 3 and len(iso_dates) == 0
        self._add_result(
            category,
            "Consistent date formatting",
            not inconsistent_dates,
            "Use consistent date format throughout (prefer ISO 8601)"
        )

    def _validate_product_spec(self):
        """Validate product specification specific requirements"""
        category = "Product Spec"

        # Check for user stories
        has_user_stories = bool(re.search(r'as a .+ i want .+ so that', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Includes user stories",
            has_user_stories,
            "Product specs should include user stories"
        )

        # Check for success metrics
        has_metrics = bool(re.search(r'success metrics|kpi|key performance', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Defines success metrics",
            has_metrics,
            "Define how success will be measured"
        )

        # Check for user personas
        has_personas = bool(re.search(r'persona|user type|target user', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Defines user personas",
            has_personas,
            "Identify target users or personas"
        )

    def _validate_technical_spec(self):
        """Validate technical specification specific requirements"""
        category = "Technical Spec"

        # Check for architecture section
        has_architecture = bool(re.search(r'architecture|system design|component diagram', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Includes architecture description",
            has_architecture,
            "Technical specs should describe system architecture"
        )

        # Check for data models
        has_data_models = bool(re.search(r'data model|schema|database|entity', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Defines data models",
            has_data_models,
            "Define data structures and schemas"
        )

        # Check for error handling
        has_error_handling = bool(re.search(r'error handling|exception|failure', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Addresses error handling",
            has_error_handling,
            "Specify how errors will be handled"
        )

        # Check for performance requirements
        has_performance = bool(re.search(r'performance|latency|throughput|response time', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Specifies performance requirements",
            has_performance,
            "Define performance expectations"
        )

    def _validate_design_spec(self):
        """Validate design specification specific requirements"""
        category = "Design Spec"

        # Check for user flows
        has_flows = bool(re.search(r'user flow|journey|interaction flow', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Includes user flows",
            has_flows,
            "Design specs should document user flows"
        )

        # Check for accessibility
        has_accessibility = bool(re.search(r'accessibility|wcag|a11y|screen reader', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Addresses accessibility",
            has_accessibility,
            "Specify accessibility requirements"
        )

        # Check for responsive design
        has_responsive = bool(re.search(r'responsive|mobile|tablet|breakpoint', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Addresses responsive design",
            has_responsive,
            "Define responsive behavior across devices"
        )

        # Check for component states
        has_states = bool(re.search(r'state|hover|active|disabled|loading', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Defines component states",
            has_states,
            "Document different states for interactive elements"
        )

    def _validate_api_spec(self):
        """Validate API specification specific requirements"""
        category = "API Spec"

        # Check for authentication
        has_auth = bool(re.search(r'authentication|authorization|api key|token', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Specifies authentication",
            has_auth,
            "Define authentication method"
        )

        # Check for endpoints
        has_endpoints = bool(re.search(r'GET|POST|PUT|PATCH|DELETE|endpoint', self.content))
        self._add_result(
            category,
            "Documents endpoints",
            has_endpoints,
            "List all API endpoints with methods"
        )

        # Check for error codes
        has_error_codes = bool(re.search(r'400|401|403|404|500|error code', self.content))
        self._add_result(
            category,
            "Defines error codes",
            has_error_codes,
            "Document all possible error responses"
        )

        # Check for rate limiting
        has_rate_limit = bool(re.search(r'rate limit|throttl|quota', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Addresses rate limiting",
            has_rate_limit,
            "Specify rate limits and quotas"
        )

        # Check for request/response examples
        has_examples = bool(re.search(r'```json|```http|example request|example response', self.content, re.IGNORECASE))
        self._add_result(
            category,
            "Includes request/response examples",
            has_examples,
            "Provide example requests and responses"
        )

    def _print_results(self) -> bool:
        """Print validation results and return overall pass/fail"""
        # Group results by category
        by_category: Dict[str, List[ValidationResult]] = {}
        for result in self.results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)

        # Print results by category
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)

        for category, results in by_category.items():
            category_passed = sum(1 for r in results if r.passed)
            category_total = len(results)

            print(f"\n{category}: {category_passed}/{category_total} checks passed")
            print("-" * 60)

            for result in results:
                status = "✓" if result.passed else "✗"
                color = "\033[92m" if result.passed else "\033[91m"  # Green or Red
                reset = "\033[0m"

                print(f"{color}{status}{reset} {result.check}")
                if result.message and not result.passed:
                    print(f"  → {result.message}")

        # Print summary
        print(f"\n{'='*60}")
        print(f"SUMMARY: {passed_checks}/{total_checks} checks passed")
        print(f"{'='*60}\n")

        if passed_checks == total_checks:
            print("✓ All validations passed! Specification looks good.")
            return True
        else:
            print(f"✗ {total_checks - passed_checks} validation(s) failed. Please review and address the issues above.")
            return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate specification documents for completeness and quality"
    )
    parser.add_argument(
        "file",
        help="Path to specification file (.md)"
    )
    parser.add_argument(
        "--type",
        choices=["product", "technical", "design", "api"],
        help="Specification type (auto-detected if not provided)"
    )

    args = parser.parse_args()

    validator = SpecValidator(args.file, args.type)
    all_passed = validator.validate()

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
