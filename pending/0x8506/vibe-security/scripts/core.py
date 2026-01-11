#!/usr/bin/env python3
"""
Core utilities for Vibe Security skill
"""
import csv
import os
from pathlib import Path
from typing import List, Dict, Any

# Get the base path for data files
BASE_DIR = Path(__file__).parent.parent / "data"


def load_csv(filename: str) -> List[Dict[str, str]]:
    """Load a CSV file and return list of dictionaries."""
    filepath = BASE_DIR / filename
    if not filepath.exists():
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def search_vulnerabilities(keyword: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search for vulnerabilities matching the keyword."""
    vulnerabilities = load_csv('vulnerabilities.csv')
    keyword_lower = keyword.lower()
    
    results = [
        v for v in vulnerabilities
        if keyword_lower in v.get('vulnerability_type', '').lower()
        or keyword_lower in v.get('description', '').lower()
    ]
    
    return results[:max_results]


def search_patterns(language: str = None, severity: str = None, max_results: int = 10) -> List[Dict[str, str]]:
    """Search for security patterns by language and/or severity."""
    patterns = load_csv('patterns.csv')
    
    results = patterns
    if language:
        language_lower = language.lower()
        results = [p for p in results if language_lower in p.get('language', '').lower()]
    
    if severity:
        severity_lower = severity.lower()
        results = [p for p in results if severity_lower in p.get('severity', '').lower()]
    
    return results[:max_results]


def search_rules(keyword: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search for security rules matching the keyword."""
    rules = load_csv('rules.csv')
    keyword_lower = keyword.lower()
    
    results = [
        r for r in rules
        if keyword_lower in r.get('rule', '').lower()
        or keyword_lower in r.get('description', '').lower()
    ]
    
    return results[:max_results]


def search_frameworks(framework: str) -> List[Dict[str, str]]:
    """Get security best practices for a specific framework."""
    frameworks = load_csv('frameworks.csv')
    framework_lower = framework.lower()
    
    results = [
        f for f in frameworks
        if framework_lower in f.get('framework', '').lower()
    ]
    
    return results


def format_result(result: Dict[str, str], result_type: str = "vulnerability") -> str:
    """Format a search result for display."""
    if result_type == "vulnerability":
        return f"""
Type: {result.get('vulnerability_type', 'N/A')}
Severity: {result.get('severity', 'N/A')}
Description: {result.get('description', 'N/A')}
Example: {result.get('example', 'N/A')}
Remediation: {result.get('remediation', 'N/A')}
"""
    elif result_type == "pattern":
        return f"""
Language: {result.get('language', 'N/A')}
Pattern: {result.get('pattern', 'N/A')}
Vulnerability: {result.get('vulnerability', 'N/A')}
Severity: {result.get('severity', 'N/A')}
Description: {result.get('description', 'N/A')}
"""
    elif result_type == "rule":
        return f"""
Rule: {result.get('rule', 'N/A')}
Description: {result.get('description', 'N/A')}
OWASP: {result.get('owasp_category', 'N/A')}
CWE: {result.get('cwe_id', 'N/A')}
"""
    elif result_type == "framework":
        return f"""
Framework: {result.get('framework', 'N/A')}
Language: {result.get('language', 'N/A')}
Best Practices: {result.get('security_best_practices', 'N/A')}
"""
    
    return str(result)


if __name__ == "__main__":
    # Test the core functions
    print("Testing Vibe Security Core...")
    print("\n=== SQL Injection Vulnerabilities ===")
    results = search_vulnerabilities("sql")
    for r in results:
        print(format_result(r, "vulnerability"))
    
    print("\n=== JavaScript Patterns ===")
    results = search_patterns(language="javascript", max_results=3)
    for r in results:
        print(format_result(r, "pattern"))
    
    print("\n=== Framework: Express ===")
    results = search_frameworks("express")
    for r in results:
        print(format_result(r, "framework"))
