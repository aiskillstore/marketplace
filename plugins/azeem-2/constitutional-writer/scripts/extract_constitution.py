#!/usr/bin/env python3
"""
Constitutional Content Extractor
A script to extract constitutional elements from documents.
"""

import re
import sys
from typing import Dict, List, Tuple
from pathlib import Path

class ConstitutionalExtractor:
    """Extracts constitutional elements from text documents."""

    def __init__(self):
        # Constitutional patterns with regex
        self.patterns = {
            'mission': [
                r'(?i)(?:mission|purpose|why we exist|our purpose)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:we are here to|our goal is to)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:the purpose of|the mission is)[\s:]*\n*[-*•]?\s*([^\n]+)'
            ],
            'vision': [
                r'(?i)(?:vision|future state|we envision|our vision)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:we will create|we aspire to|we will become)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:the future of|imagine a world where)[\s:]*\n*[-*•]?\s*([^\n]+)'
            ],
            'values': [
                r'(?i)(?:values|core values|we believe|we value)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:our principles|guiding principles)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:we are committed to|we stand for)[\s:]*\n*[-*•]?\s*([^\n]+)'
            ],
            'governance': [
                r'(?i)(?:governance|decision making|how we decide)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:authority structure|leadership|who decides)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:accountability|responsibility|ownership)[\s:]*\n*[-*•]?\s*([^\n]+)'
            ],
            'standards': [
                r'(?i)(?:standards|quality|excellence|we measure)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:success criteria|performance metrics|kpi)[\s:]*\n*[-*•]?\s*([^\n]+)',
                r'(?i)(?:benchmarks|quality gates|definition of done)[\s:]*\n*[-*•]?\s*([^\n]+)'
            ]
        }

        # Keywords for each category
        self.keywords = {
            'mission': ['mission', 'purpose', 'why', 'exist', 'objective', 'goal'],
            'vision': ['vision', 'future', 'envision', 'aspire', 'imagine', 'become'],
            'values': ['value', 'believe', 'principle', 'commit', 'stand', 'ethic'],
            'governance': ['govern', 'decide', 'authority', 'leadership', 'account', 'responsibil'],
            'standards': ['standard', 'quality', 'excellence', 'metric', 'criteria', 'benchmark']
        }

    def extract_section(self, text: str, section_type: str) -> List[str]:
        """Extract specific constitutional section from text."""
        extracted = []

        # Try pattern matching first
        if section_type in self.patterns:
            for pattern in self.patterns[section_type]:
                matches = re.findall(pattern, text, re.MULTILINE)
                for match in matches:
                    clean_match = re.sub(r'^[-*•]\s*', '', match.strip())
                    if len(clean_match) > 10:  # Filter out very short matches
                        extracted.append(clean_match)

        # If no pattern matches, try keyword search
        if not extracted and section_type in self.keywords:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 20:  # Only consider substantial lines
                    if any(keyword in line.lower() for keyword in self.keywords[section_type]):
                        # Remove bullet points if present
                        clean_line = re.sub(r'^[-*•0-9.)\[\s]+', '', line)
                        extracted.append(clean_line)

        return list(set(extracted))  # Remove duplicates

    def extract_all(self, text: str) -> Dict[str, List[str]]:
        """Extract all constitutional elements from text."""
        result = {}

        for section_type in self.patterns.keys():
            result[section_type] = self.extract_section(text, section_type)

        return result

    def format_constitution(self, extracted: Dict[str, List[str]], project_name: str = "Project") -> str:
        """Format extracted content into a constitution."""
        constitution = f"# {project_name} Constitution\n\n"

        sections = [
            ('mission', 'Mission & Purpose'),
            ('vision', 'Vision & Aspiration'),
            ('values', 'Core Values'),
            ('governance', 'Governance & Decision Making'),
            ('standards', 'Quality Standards')
        ]

        for section_key, section_title in sections:
            if extracted.get(section_key):
                constitution += f"## {section_title}\n\n"
                for item in extracted[section_key]:
                    constitution += f"- {item}\n"
                constitution += "\n"

        return constitution

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_constitution.py <input_file> [project_name]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else input_file.stem

    # Read the document
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract constitutional content
    extractor = ConstitutionalExtractor()
    extracted = extractor.extract_all(text)

    # Generate constitution
    constitution = extractor.format_constitution(extracted, project_name)

    # Output to stdout
    print(constitution)

if __name__ == "__main__":
    main()