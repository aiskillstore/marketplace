#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Academic Article Checking Tool - Initialization Script
Provides a command line interface for checking academic papers"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

from english_checker import EnglishChecker
from chinese_checker import ChineseChecker
from terminology_manager import TerminologyManager
from annotation_generator import AnnotationGenerator
from word_converter import WordConverter


class AcademicProofreader:
    """Academic article checker main class"""

    def __init__(
        self,
        lang: str = "both",
        style: str = "apa",
        terminology: str = "biology",
        strict_mode: bool = False,
    ):
        self.lang = lang
        self.style = style
        self.terminology_domain = terminology
        self.strict_mode = strict_mode

        self.en_checker = EnglishChecker(strict=strict_mode)
        self.zh_checker = ChineseChecker(strict=strict_mode)
        self.term_manager = TerminologyManager(domain=terminology)
        self.annotator = AnnotationGenerator()

    def check(self, text: str) -> Dict:
        """Perform a comprehensive inspection"""
        results = {
            "summary": {"total_issues": 0, "categories": {}},
            "issues": [],
            "statistics": {},
        }

        issues = []

        if self.lang in ["en", "both"]:
            en_issues = self.en_checker.check(text)
            issues.extend(en_issues)

        if self.lang in ["zh", "both"]:
            zh_issues = self.zh_checker.check(text)
            issues.extend(zh_issues)

        term_issues = self.term_manager.check(text)
        issues.extend(term_issues)

        results["issues"] = [
            {
                "type": issue.type,
                "category": issue.category,
                "message": issue.message,
                "suggestion": issue.suggestion,
                "position": {
                    "start": issue.start,
                    "end": issue.end,
                    "line": issue.line,
                },
                "severity": issue.severity,
            }
            for issue in issues
        ]

        results["summary"]["total_issues"] = len(issues)
        results["summary"]["categories"] = self._categorize_issues(issues)

        return results

    def _categorize_issues(self, issues: List) -> Dict:
        """Group questions by category"""
        categories = {}
        for issue in issues:
            if issue.category not in categories:
                categories[issue.category] = 0
            categories[issue.category] += 1
        return categories

    def generate_report(
        self, text: str, results: Dict, output_format: str = "html"
    ) -> str:
        """Generate inspection report"""
        if output_format == "html":
            return self.annotator.to_html(text, results)
        elif output_format == "markdown":
            return self.annotator.to_markdown(text, results)
        else:
            return self.annotator.to_json(results)


class Issue:
    """Problem record class"""

    def __init__(
        self,
        type: str,
        category: str,
        message: str,
        suggestion: Optional[str] = None,
        start: int = 0,
        end: int = 0,
        line: int = 1,
        severity: str = "warning",
    ):
        self.type = type
        self.category = category
        self.message = message
        self.suggestion = suggestion
        self.start = start
        self.end = end
        self.line = line
        self.severity = severity


def load_config(config_path: str) -> Dict:
    """Load configuration file"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(results: Dict, output_path: str):
    """Save test results"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def main():
    """main function"""
    parser = argparse.ArgumentParser(
        description="Academic Article Checker - Check your paper for spelling, grammar, terminology and formatting"
    )

    parser.add_argument("--input", "-i", required=True, help="input file path")

    parser.add_argument(
        "--output", "-o", default="report.html", help="Output report path (default: report.html)"
    )

    parser.add_argument(
        "--lang",
        "-l",
        choices=["en", "zh", "both"],
        default="both",
        help="Check language (default: both)",
    )

    parser.add_argument(
        "--style",
        "-s",
        choices=["apa", "mla", "gb"],
        default="apa",
        help="Reference format (default: apa)",
    )

    parser.add_argument(
        "--terminology",
        "-t",
        choices=["biology", "medicine", "chemistry", "physics"],
        default="biology",
        help="Area of ​​expertise (default: biology)",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["html", "markdown", "json"],
        default="html",
        help="Output format (default: html)",
    )

    parser.add_argument("--strict", action="store_true", help="Strict mode, check for more details")

    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF generation when converting Word to PDF",
    )

    parser.add_argument("--config", "-c", help="Configuration file path")

    args = parser.parse_args()

    try:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"mistake: Input file does not exist: {args.input}")
            sys.exit(1)

        word_converter = WordConverter()

        if word_converter.is_word_file(str(input_path)):
            print(f"detectedWorddocument，Converting: {input_path.name}")
            text = word_converter.extract_text(str(input_path))

            if args.output:
                output_pdf = Path(args.output).with_suffix(".pdf")
            else:
                output_pdf = input_path.with_suffix(".pdf")

            if not args.no_pdf:
                try:
                    word_converter.convert_to_pdf(str(input_path), str(output_pdf))
                    print(f"PDFGenerated: {output_pdf}")
                except ImportError as e:
                    print(f"hint: {e}")
                except Exception as e:
                    print(f"PDFgenerate warning: {e}")
        else:
            text = input_path.read_text(encoding="utf-8")

        config = {}
        if args.config:
            config = load_config(args.config)

        proofreader = AcademicProofreader(
            lang=config.get("lang", args.lang),
            style=config.get("style", args.style),
            terminology=config.get("terminology", args.terminology),
            strict_mode=config.get("strict", args.strict),
        )

        print(f"Checking: {input_path.name}")
        print(f"Check language: {args.lang}")
        print(f"Professional areas: {args.terminology}")
        print("-" * 50)

        results = proofreader.check(text)

        print(f"Found problem: {results['summary']['total_issues']} indivual")
        for category, count in results["summary"]["categories"].items():
            print(f"  - {category}: {count} indivual")
        print("-" * 50)

        output_format = args.format
        if output_format == "json":
            save_results(results, args.output)
            print(f"Results have been saved to: {args.output}")
        else:
            report = proofreader.generate_report(text, results, output_format)
            output_path = Path(args.output)
            output_path.write_text(report, encoding="utf-8")
            print(f"Report generated: {args.output}")

        return 0

    except Exception as e:
        print(f"mistake: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
