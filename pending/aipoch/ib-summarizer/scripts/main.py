#!/usr/bin/env python3
"""IB Summarizer - Researchers Manual Core Security Information Extraction Tool

Function: Extract Core Security Information (CSI) from Investigator's Brochure document"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class DrugInfo:
    """Basic drug information"""
    name: str = ""
    version: str = ""
    date: str = ""
    sponsor: str = ""


@dataclass
class AdverseReaction:
    """adverse reactions"""
    system_organ_class: str = ""  # system organ classification
    reaction: str = ""  # reaction name
    frequency: str = ""  # incidence
    severity: str = ""  # Severity


@dataclass
class SafetyUpdate:
    """Security update history"""
    version: str = ""
    date: str = ""
    content: str = ""


@dataclass
class CoreSafetyInfo:
    """Core safety information"""
    adverse_reactions: List[AdverseReaction]
    contraindications: List[str]
    warnings: List[str]
    precautions: List[str]
    drug_interactions: List[str]
    special_populations: Dict[str, str]
    overdose: Dict[str, str]
    safety_updates: List[SafetyUpdate]


class TextExtractor:
    """text extractor"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        try:
            import pdfplumber
        except ImportError:
            try:
                import PyPDF2
            except ImportError:
                raise ImportError("Please install pdfplumber or PyPDF2: pip install pdfplumber")
            
            # Using PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        
        # Use pdfplumber (more precise)
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"
        return text
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extract text from Word"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("Please install python-docx: pip install python-docx")
        
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @classmethod
    def extract(cls, file_path: str) -> str:
        """Automatically extract text based on file type"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return cls.extract_from_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            return cls.extract_from_docx(file_path)
        elif suffix in ['.txt', '.md']:
            return cls.extract_from_txt(file_path)
        else:
            # Try to read as text
            try:
                return cls.extract_from_txt(file_path)
            except:
                raise ValueError(f"Unsupported file format: {suffix}")


class IBSummarizer:
    """IB document security information extractor"""
    
    # Security related keyword pattern
    KEYWORDS = {
        'adverse_reactions': [
            r'adverse\s+reaction',
            'adverse reactions',
            r'adverse\s+event',
            'adverse events',
            r'safety\s+data',
            r'safety\s+profile',
        ],
        'contraindications': [
            r'contraindication',
            'Contraindications',
            'Taboo',
        ],
        'warnings': [
            r'warning',
            'warn',
        ],
        'precautions': [
            r'precaution',
            'Things to note',
        ],
        'drug_interactions': [
            r'drug\s+interaction',
            'drug interactions',
            r'interaction',
        ],
        'special_populations': [
            r'special\s+population',
            'Special groups',
            r'pregnancy|pregnant',
            'Pregnancy | Pregnant women',
            r'lactation|breastfeeding',
            'breast-feeding',
            r'pediatric|children',
            'child',
            r'elderly|geriatric',
            'elderly',
            r'hepatic',
            'liver',
            r'renal',
            'kidney',
        ],
        'overdose': [
            r'overdose',
            'excess',
            'Poisoned',
        ],
    }
    
    def __init__(self, text: str):
        self.text = text
        self.lines = text.split('\n')
    
    def _find_section(self, keywords: List[str], context_lines: int = 50) -> str:
        """Find chapters containing keywords"""
        patterns = [re.compile(kw, re.IGNORECASE) for kw in keywords]
        
        for i, line in enumerate(self.lines):
            for pattern in patterns:
                if pattern.search(line):
                    # Extract context
                    start = max(0, i)
                    end = min(len(self.lines), i + context_lines)
                    return '\n'.join(self.lines[start:end])
        
        return ""
    
    def _extract_drug_info(self) -> DrugInfo:
        """Extract basic drug information"""
        info = DrugInfo()
        
        # Try to match drug name
        name_patterns = [
            '(?:Drug\\s+Name|Investigational\\s+Product|Drug name)[\\s::]+([^\\n]+)',
            '(?:Title|title)[\\s::]+([^\\n]+)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                info.name = match.group(1).strip()
                break
        
        # version number
        version_patterns = [
            '(?:Version|version)[\\s::]*(\\d+[.\\d]*)',
            r'Edition[\s:：]*(\d+[.\d]*)',
        ]
        for pattern in version_patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                info.version = match.group(1).strip()
                break
        
        # date
        date_patterns = [
            '(?:Date|Date)[\\s::]*(\\d{4}[-/]\\d{1,2}[-/]\\d{1,2})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, self.text)
            if match:
                info.date = match.group(1).strip()
                break
        
        return info
    
    def _extract_adverse_reactions(self) -> List[AdverseReaction]:
        """Extract adverse reaction information"""
        section = self._find_section(self.KEYWORDS['adverse_reactions'], 100)
        reactions = []
        
        if not section:
            return reactions
        
        # Simple table row matching
        lines = section.split('\n')
        for line in lines[1:]:  # skip title row
            # Try to match: System Organ | Response | Frequency | Severity
            parts = re.split(r'[\|，,；;\t]', line)
            if len(parts) >= 2:
                reactions.append(AdverseReaction(
                    system_organ_class=parts[0].strip() if len(parts) > 0 else "",
                    reaction=parts[1].strip() if len(parts) > 1 else "",
                    frequency=parts[2].strip() if len(parts) > 2 else "",
                    severity=parts[3].strip() if len(parts) > 3 else ""
                ))
        
        return reactions
    
    def _extract_list_items(self, keywords: List[str]) -> List[str]:
        """Extract list items"""
        section = self._find_section(keywords, 30)
        if not section:
            return []
        
        items = []
        for line in section.split('\n'):
            # Match list items (•, -, *, numbers, etc.)
            match = re.match(r'^[\s]*(?:[•\-\*•]|\d+[.．）)])[\s]*(.+)', line)
            if match:
                items.append(match.group(1).strip())
        
        return items
    
    def _extract_special_populations(self) -> Dict[str, str]:
        """Extract special population information"""
        section = self._find_section(self.KEYWORDS['special_populations'], 80)
        populations = {}
        
        if not section:
            return populations
        
        # Common special groups
        pop_patterns = {
            'pregnancy': '(?:Pregnancy|Pregnancy|Pregnant woman)[\\s\\S]{0,500}?',
            'lactation': '(?:Lactation|Breastfeeding|Lactation)[\\s\\S]{0,500}?',
            'pediatric': '(?:Pediatric|Children|Children)[\\s\\S]{0,500}?',
            'elderly': '(?:Elderly|Geriatric|Elderly)[\\s\\S]{0,500}?',
            'hepatic': '(?:Hepatic|Liver)[\\s\\S]{0,500}?',
            'renal': '(?:Renal|kidney)[\\s\\S]{0,500}?',
        }
        
        for key, pattern in pop_patterns.items():
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                populations[key] = match.group(0).strip()
        
        return populations
    
    def _extract_overdose(self) -> Dict[str, str]:
        """Extract overdose information"""
        section = self._find_section(self.KEYWORDS['overdose'], 50)
        if not section:
            return {}
        
        overdose = {}
        
        # symptom
        symptoms_match = re.search('(?:Symptoms|symptoms)[：:]([^\\n]+)', section, re.IGNORECASE)
        if symptoms_match:
            overdose['symptoms'] = symptoms_match.group(1).strip()
        
        # deal with
        management_match = re.search('(?:Management|Treatment|Processing|Treatment)[：:]([^\\n]+)', section, re.IGNORECASE)
        if management_match:
            overdose['management'] = management_match.group(1).strip()
        
        return overdose
    
    def _extract_safety_updates(self) -> List[SafetyUpdate]:
        """Extract security update history"""
        # Usually in the version history section at the end of the document
        updates = []
        
        # Find version history table
        version_pattern = r'(\d+[.\d]*)\s+(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+([^\n]+)'
        matches = re.findall(version_pattern, self.text)
        
        for match in matches[:10]:  # Up to 10 items
            updates.append(SafetyUpdate(
                version=match[0],
                date=match[1],
                content=match[2].strip()
            ))
        
        return updates
    
    def summarize(self) -> Dict[str, Any]:
        """Perform complete security information extraction"""
        drug_info = self._extract_drug_info()
        
        core_safety = CoreSafetyInfo(
            adverse_reactions=self._extract_adverse_reactions(),
            contraindications=self._extract_list_items(self.KEYWORDS['contraindications']),
            warnings=self._extract_list_items(self.KEYWORDS['warnings']),
            precautions=self._extract_list_items(self.KEYWORDS['precautions']),
            drug_interactions=self._extract_list_items(self.KEYWORDS['drug_interactions']),
            special_populations=self._extract_special_populations(),
            overdose=self._extract_overdose(),
            safety_updates=self._extract_safety_updates()
        )
        
        return {
            'drug_info': asdict(drug_info),
            'core_safety_info': {
                'adverse_reactions': [asdict(r) for r in core_safety.adverse_reactions],
                'contraindications': core_safety.contraindications,
                'warnings': core_safety.warnings,
                'precautions': core_safety.precautions,
                'drug_interactions': core_safety.drug_interactions,
                'special_populations': core_safety.special_populations,
                'overdose': core_safety.overdose,
                'safety_updates': [asdict(u) for u in core_safety.safety_updates]
            }
        }


class OutputFormatter:
    """output formatter"""
    
    @staticmethod
    def to_json(data: Dict[str, Any]) -> str:
        """Format to JSON"""
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def to_markdown(data: Dict[str, Any], language: str = 'zh') -> str:
        """Formatted as Markdown"""
        drug = data['drug_info']
        safety = data['core_safety_info']
        
        md = f"""# IBSafety Information Summary

## Basic drug information
- **Drug name**: {drug['name'] or 'N/A'}
- **version number**: {drug['version'] or 'N/A'}
- **date**: {drug['date'] or 'N/A'}
- **Sponsor**: {drug['sponsor'] or 'N/A'}

## Core safety information

### Known adverse reactions
"""
        
        if safety['adverse_reactions']:
            md += "| System Organ Classification | Adverse Reactions | Incidence | Severity |"
            md += "|-------------|---------|--------|---------|\n"
            for ar in safety['adverse_reactions']:
                md += f"| {ar['system_organ_class'] or '-'} | {ar['reaction'] or '-'} | {ar['frequency'] or '-'} | {ar['severity'] or '-'} |\n"
        else:
            md += "_No adverse reaction data detected_"
        
        md += "### Contraindications"
        if safety['contraindications']:
            for item in safety['contraindications']:
                md += f"- {item}\n"
        else:
            md += "_No contraindication data detected_"
        
        md += "### Warnings and Precautions"
        if safety['warnings']:
            md += "#### warn"
            for item in safety['warnings']:
                md += f"- {item}\n"
        
        if safety['precautions']:
            md += "#### Notes"
            for item in safety['precautions']:
                md += f"- {item}\n"
        
        if not safety['warnings'] and not safety['precautions']:
            md += "_Warning/Caution Data Not Detected_"
        
        md += "### Drug Interactions"
        if safety['drug_interactions']:
            for item in safety['drug_interactions']:
                md += f"- {item}\n"
        else:
            md += "_No drug interaction data detected_"
        
        md += "### Medication precautions for special groups"
        if safety['special_populations']:
            for pop, note in safety['special_populations'].items():
                md += f"**{pop.capitalize()}**: {note[:200]}...\n\n"
        else:
            md += "_No special population data detected_"
        
        md += "### Overdose"
        if safety['overdose']:
            if 'symptoms' in safety['overdose']:
                md += f"- **symptom**: {safety['overdose']['symptoms']}\n"
            if 'management' in safety['overdose']:
                md += f"- **deal with**: {safety['overdose']['management']}\n"
        else:
            md += "_No data related to overdose detected_"
        
        md += "### Security update history"
        if safety['safety_updates']:
            md += "| Version | Date | Updates |"
            md += "|-----|------|---------|\n"
            for update in safety['safety_updates']:
                md += f"| {update['version']} | {update['date']} | {update['content'][:100]}... |\n"
        else:
            md += "_Security update history not detected_"
        
        md += """---
*This summary is automatically generated by IB Summarizer and is for reference only*"""
        
        return md
    
    @staticmethod
    def to_text(data: Dict[str, Any]) -> str:
        """Format as plain text"""
        md = OutputFormatter.to_markdown(data)
        # Remove Markdown tags
        text = re.sub(r'#+\s*', '', md)
        text = re.sub(r'\*\*', '', text)
        text = re.sub(r'\|', ' | ', text)
        return text


def main():
    """main function"""
    parser = argparse.ArgumentParser(
        description='IB Summarizer - Researchers Manual Core Security Information Extraction Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python main.py /path/to/IB.pdf
  python main.py /path/to/IB.docx -o summary.json -f json
  python main.py /path/to/IB.pdf -l en -o summary.md"""
    )
    
    parser.add_argument('input_file', help='Entered IB document path (PDF/Word/TXT)')
    parser.add_argument('-o', '--output', help='Output file path (default output to stdout)')
    parser.add_argument('-f', '--format', choices=['json', 'markdown', 'text'], 
                        default='markdown', help='Output format (default: markdown)')
    parser.add_argument('-l', '--language', choices=['zh', 'en'], 
                        default='zh', help='Output language (default: zh)')
    
    args = parser.parse_args()
    
    # Check input file
    if not Path(args.input_file).exists():
        print(f"mistake: File does not exist: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Extract text
        print(f"Extracting: {args.input_file}...", file=sys.stderr)
        text = TextExtractor.extract(args.input_file)
        
        # Extract security information
        print("Analyzing security information...", file=sys.stderr)
        summarizer = IBSummarizer(text)
        data = summarizer.summarize()
        
        # Formatted output
        formatter = OutputFormatter()
        if args.format == 'json':
            output = formatter.to_json(data)
        elif args.format == 'text':
            output = formatter.to_text(data)
        else:
            output = formatter.to_markdown(data, args.language)
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"English: {args.output}", file=sys.stderr)
        else:
            print(output)
            
    except ImportError as e:
        print(f"dependency error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"mistake: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
