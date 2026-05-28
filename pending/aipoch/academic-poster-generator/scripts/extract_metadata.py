#!/usr/bin/env python3
"""
PDF Metadata Extractor
Extracts title, authors, abstract, and key sections from research papers.
"""

import re
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
import pdfplumber


class PaperMetadataExtractor:
    """Extract structured metadata from research papers."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.pdf = pdfplumber.open(pdf_path)
        self.full_text = ""
        self._extract_full_text()
    
    def _extract_full_text(self):
        """Extract full text from all pages."""
        for page in self.pdf.pages:
            self.full_text += page.extract_text() + "\n\n"
    
    def extract_title(self) -> str:
        """Extract paper title from first page."""
        try:
            first_page = self.pdf.pages[0]
            text = first_page.extract_text()
            lines = text.split('\n')
            
            # Title is usually in the first few lines, largest font
            # Look for lines that don't start with common header patterns
            skip_patterns = ['abstract', 'introduction', 'keywords', 'author', 'university']
            
            for i, line in enumerate(lines[:10]):
                line = line.strip()
                if len(line) > 20 and len(line) < 200:
                    # Skip lines that match header patterns
                    if not any(pattern.lower() in line.lower() for pattern in skip_patterns):
                        return line
            
            # Fallback: return first substantial line
            for line in lines[:5]:
                line = line.strip()
                if len(line) > 10:
                    return line
                    
        except Exception as e:
            print(f"Warning: Could not extract title: {e}")
        
        return "Title not found"
    
    def extract_authors(self) -> List[str]:
        """Extract author names from first page."""
        try:
            first_page = self.pdf.pages[0]
            text = first_page.extract_text()

            # Look for author patterns (after title, before abstract)
            # Authors are usually listed with affiliations, emails, etc.
            lines = text.split('\n')

            authors = []
            in_author_section = False

            for i, line in enumerate(lines[:20]):
                line_lower = line.strip().lower()

                # Start looking after we've seen a potential title
                if len(line.strip()) > 20 and i < 5:
                    in_author_section = True
                    continue

                # Stop at abstract
                if 'abstract' in line_lower:
                    break

                # Collect potential author lines
                if in_author_section:
                    # Look for patterns like: John Doe, Jane Smith
                    # or institutional affiliations
                    author_match = re.search(r'^[A-Z][a-z]+ [A-Z][a-z]+', line.strip())
                    if author_match and len(line.strip()) < 100:
                        authors.append(line.strip())

            # Clean up author list
            clean_authors = []
            for author in authors:
                # Remove email addresses
                author = re.sub(r'\S+@\S+', '', author)
                # Remove extra whitespace
                author = ' '.join(author.split())
                if author and len(author) > 3:
                    clean_authors.append(author)

            return clean_authors[:10]  # Limit to first 10 authors

        except Exception as e:
            print(f"Warning: Could not extract authors: {e}")

        return []

    def extract_institution(self) -> str:
        """Extract institution/affiliation from first page."""
        try:
            first_page = self.pdf.pages[0]
            text = first_page.extract_text()
            lines = text.split('\n')

            # Look for institutional keywords after authors, before abstract
            institution_keywords = [
                'university', 'institute', 'college', 'school', 'department',
                'laboratory', 'lab', 'hospital', 'medical center', 'medical centre',
                'universidad', 'universite', 'universität', 'universit', 'institut'
            ]

            institution_found = None

            for i, line in enumerate(lines[:25]):
                line_lower = line.strip().lower()

                # Stop at abstract
                if 'abstract' in line_lower:
                    break

                # Check if line contains institutional keywords
                for keyword in institution_keywords:
                    if keyword in line_lower:
                        # Clean up the institution name
                        institution = line.strip()

                        # Remove common prefixes and suffixes
                        institution = re.sub(r'^[\d\s]*', '', institution)
                        institution = re.sub(r'[,\s]*$', '', institution)

                        # Remove email addresses
                        institution = re.sub(r'\S+@\S+', '', institution)

                        # Remove phone numbers
                        institution = re.sub(r'[\+\d\-\(\)\s]{10,}', '', institution)

                        # Remove extra whitespace
                        institution = ' '.join(institution.split())

                        if len(institution) > 5 and len(institution) < 200:
                            institution_found = institution
                            break

                if institution_found:
                    break

            if institution_found:
                return institution_found

            # Fallback: look for lines with uppercase words that might be institutions
            for line in lines[:20]:
                line = line.strip()

                # Skip if too short or too long
                if len(line) < 10 or len(line) > 200:
                    continue

                # Skip if contains common non-institution patterns
                skip_patterns = ['abstract', 'introduction', 'keywords', 'corresponding', 'email', '@']
                if any(pattern in line.lower() for pattern in skip_patterns):
                    continue

                # Look for lines that start with capital words and contain institutional indicators
                if re.search(r'\b(Department|University|Institute|College|School|Laboratory|Hospital|Medical)\b', line, re.IGNORECASE):
                    # Clean up
                    institution = re.sub(r'[\d\s]*', '', line)
                    institution = ' '.join(institution.split())
                    if len(institution) > 5:
                        return institution

            return "Institution not found"

        except Exception as e:
            print(f"Warning: Could not extract institution: {e}")

        return "Institution not found"
    
    def extract_abstract(self) -> str:
        """Extract abstract section."""
        try:
            # Find abstract section using regex
            abstract_match = re.search(
                r'(?i)abstract\s*:?\s*(.*?)(?=\n\s*(?:introduction|keywords|references|\d+\.))',
                self.full_text,
                re.DOTALL
            )
            
            if abstract_match:
                abstract = abstract_match.group(1).strip()
                # Clean up the abstract
                abstract = re.sub(r'\s+', ' ', abstract)
                return abstract
            
            # Alternative: look for first paragraph after "Abstract" keyword
            lines = self.full_text.split('\n')
            for i, line in enumerate(lines):
                if 'abstract' in line.lower():
                    # Extract next few paragraphs
                    abstract_lines = []
                    for j in range(i+1, min(i+15, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) > 20:
                            abstract_lines.append(next_line)
                        elif abstract_lines and (not next_line or 'keywords' in next_line.lower()):
                            break
                    return ' '.join(abstract_lines)
                    
        except Exception as e:
            print(f"Warning: Could not extract abstract: {e}")
        
        return "Abstract not found"
    
    def extract_keywords(self) -> List[str]:
        """Extract keywords from paper."""
        try:
            # Look for keywords section
            keywords_match = re.search(
                r'(?i)keywords?\s*:?\s*(.*?)(?=\n\s*(?:introduction|abstract|references|\d+\.|$))',
                self.full_text,
                re.DOTALL
            )
            
            if keywords_match:
                keywords_text = keywords_match.group(1).strip()
                # Split by common separators
                keywords = re.split(r'[,;·•]', keywords_text)
                keywords = [k.strip() for k in keywords if k.strip()]
                return keywords[:10]  # Limit to first 10 keywords
            
        except Exception as e:
            print(f"Warning: Could not extract keywords: {e}")
        
        return []
    
    def extract_sections(self) -> Dict[str, str]:
        """Extract main sections from paper."""
        sections = {}
        
        try:
            # Common section patterns
            section_patterns = {
                'introduction': r'(?i)introduction\s*',
                'methods': r'(?i)(?:materials\s+and\s+)?methods?\s*',
                'results': r'(?i)results?\s*',
                'discussion': r'(?i)discussion\s*',
                'conclusion': r'(?i)conclusions?\s*',
                'references': r'(?i)references?\s*'
            }
            
            # Find all sections
            section_starts = {}
            for section_name, pattern in section_patterns.items():
                match = re.search(pattern, self.full_text)
                if match:
                    section_starts[section_name] = match.start()
            
            # Extract content between sections
            sorted_sections = sorted(section_starts.items(), key=lambda x: x[1])
            
            for i, (section_name, start_pos) in enumerate(sorted_sections):
                if i < len(sorted_sections) - 1:
                    end_pos = sorted_sections[i + 1][1]
                else:
                    end_pos = len(self.full_text)
                
                section_text = self.full_text[start_pos:end_pos].strip()
                
                # Limit section length (first 3000 characters)
                if len(section_text) > 3000:
                    section_text = section_text[:3000] + "..."
                
                sections[section_name] = section_text
        
        except Exception as e:
            print(f"Warning: Could not extract sections: {e}")
        
        return sections
    
    def extract_all_metadata(self) -> Dict:
        """Extract all available metadata."""
        metadata = {
            'title': self.extract_title(),
            'authors': self.extract_authors(),
            'institution': self.extract_institution(),
            'abstract': self.extract_abstract(),
            'keywords': self.extract_keywords(),
            'sections': self.extract_sections(),
            'page_count': len(self.pdf.pages)
        }
        return metadata
    
    def save_to_json(self, output_path: str):
        """Save extracted metadata to JSON file."""
        metadata = self.extract_all_metadata()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"[*] Metadata saved to {output_path}")
        return metadata
    
    def close(self):
        """Close PDF file."""
        self.pdf.close()


def main():
    parser = argparse.ArgumentParser(
        description="Extract metadata from research papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract metadata and save to JSON
  python scripts/extract_metadata.py paper.pdf metadata.json
  
  # Print metadata to console
  python scripts/extract_metadata.py paper.pdf --print
        """
    )
    
    parser.add_argument(
        "pdf_file",
        help="Input PDF file"
    )
    
    parser.add_argument(
        "output_json",
        nargs='?',
        help="Output JSON file (optional with --print)"
    )
    
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print metadata to console instead of saving to file"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.pdf_file).exists():
        print(f"Error: File not found: {args.pdf_file}")
        sys.exit(1)
    
    # Extract metadata
    extractor = PaperMetadataExtractor(args.pdf_file)
    
    try:
        if args.print:
            metadata = extractor.extract_all_metadata()
            print("\n" + "="*60)
            print("PAPER METADATA")
            print("="*60)
            print(f"\nTitle: {metadata['title']}")
            print(f"\nAuthors ({len(metadata['authors'])}):")
            for author in metadata['authors']:
                print(f"  - {author}")
            print(f"\nAbstract:\n{metadata['abstract']}")
            print(f"\nKeywords: {', '.join(metadata['keywords'])}")
            print(f"\nSections: {list(metadata['sections'].keys())}")
            print(f"\nPage Count: {metadata['page_count']}")
        else:
            if not args.output_json:
                print("Error: Please specify output JSON file or use --print")
                sys.exit(1)
            extractor.save_to_json(args.output_json)
    
    finally:
        extractor.close()


if __name__ == "__main__":
    main()
