#!/usr/bin/env python3
"""
Content Structurer
Converts PDF paper content into poster format with bullet points and concise text.
"""

import re
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List
import pdfplumber


class ContentStructurer:
    """Structure PDF content for poster format."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.pdf = pdfplumber.open(pdf_path)
        self.full_text = ""
        self._extract_full_text()
    
    def _extract_full_text(self):
        """Extract full text from all pages."""
        for page in self.pdf.pages:
            self.full_text += page.extract_text() + "\n\n"
    
    def _sentence_to_bullet(self, sentence: str) -> str:
        """Convert sentence to bullet point."""
        # Remove leading/trailing whitespace
        sentence = sentence.strip()
        
        # Capitalize first letter
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
        
        # Add period if missing
        if sentence and not sentence.endswith(('.', '!', '?')):
            sentence += '.'
        
        return sentence
    
    def structure_for_poster(self, max_words: int = 800) -> Dict:
        """
        Structure content for poster format.
        
        Args:
            max_words: Maximum total words for poster (default: 800)
        
        Returns:
            Dictionary with structured poster content
        """
        poster_content = {
            'title': self._extract_title(),
            'authors': self._extract_authors(),
            'sections': {}
        }
        
        # Structure each section
        sections = {
            'introduction': self._structure_introduction(),
            'methods': self._structure_methods(),
            'results': self._structure_results(),
            'discussion': self._structure_discussion(),
            'conclusions': self._structure_conclusions()
        }
        
        poster_content['sections'] = sections
        
        # Count total words
        total_words = sum(
            len(" ".join(section.get('bullet_points', [])).split())
            for section in sections.values()
        )
        
        poster_content['word_count'] = total_words
        
        if total_words > max_words:
            print(f"Warning: Content exceeds {max_words} words ({total_words})")
            print("Consider further summarization")
        
        return poster_content
    
    def _extract_title(self) -> str:
        """Extract paper title."""
        first_page = self.pdf.pages[0]
        text = first_page.extract_text()
        lines = text.split('\n')
        
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 20 and len(line) < 200:
                return line
        
        return "Title not found"
    
    def _extract_authors(self) -> List[str]:
        """Extract author names."""
        first_page = self.pdf.pages[0]
        text = first_page.extract_text()
        lines = text.split('\n')
        
        authors = []
        for i, line in enumerate(lines[:15]):
            line_lower = line.strip().lower()
            if 'abstract' in line_lower:
                break
            
            # Look for author patterns
            author_match = re.search(r'^[A-Z][a-z]+ [A-Z][a-z]+', line.strip())
            if author_match and len(line.strip()) < 100:
                authors.append(line.strip())
        
        # Clean up
        clean_authors = []
        for author in authors:
            author = re.sub(r'\S+@\S+', '', author)  # Remove email
            author = ' '.join(author.split())
            if author and len(author) > 3:
                clean_authors.append(author)
        
        return clean_authors[:10]
    
    def _structure_introduction(self) -> Dict:
        """Structure introduction section."""
        section = {
            'title': 'Introduction',
            'bullet_points': []
        }
        
        # Extract introduction section
        intro_match = re.search(
            r'(?i)introduction\s*[\.:]?\s*(.*?)(?=\n\s*(?:methods|materials|results|\d+\.))',
            self.full_text,
            re.DOTALL
        )
        
        if intro_match:
            intro_text = intro_match.group(1)
            
            # Split into sentences
            sentences = re.split(r'[.!?]+', intro_text)
            
            # Convert to bullet points (limit to 4-5)
            for sentence in sentences[:5]:
                bullet = self._sentence_to_bullet(sentence)
                if len(bullet) > 10:
                    section['bullet_points'].append(bullet)
        else:
            section['bullet_points'].append("Introduction content not found")
        
        return section
    
    def _structure_methods(self) -> Dict:
        """Structure methods section."""
        section = {
            'title': 'Methods',
            'bullet_points': []
        }
        
        # Extract methods section
        methods_match = re.search(
            r'(?i)(?:materials\s+and\s+)?methods?\s*[\.:]?\s*(.*?)(?=\n\s*(?:results|discussion|\d+\.))',
            self.full_text,
            re.DOTALL
        )
        
        if methods_match:
            methods_text = methods_match.group(1)
            
            # Split into sentences or paragraphs
            sentences = re.split(r'[.!?]+', methods_text)
            
            # Convert to bullet points (limit to 5-6)
            for sentence in sentences[:6]:
                bullet = self._sentence_to_bullet(sentence)
                if len(bullet) > 10:
                    section['bullet_points'].append(bullet)
        else:
            section['bullet_points'].append("Methods content not found")
        
        return section
    
    def _structure_results(self) -> Dict:
        """Structure results section."""
        section = {
            'title': 'Results',
            'bullet_points': []
        }
        
        # Extract results section
        results_match = re.search(
            r'(?i)results?\s*[\.:]?\s*(.*?)(?=\n\s*(?:discussion|conclusion|references|\d+\.))',
            self.full_text,
            re.DOTALL
        )
        
        if results_match:
            results_text = results_match.group(1)
            
            # Split into sentences
            sentences = re.split(r'[.!?]+', results_text)
            
            # Focus on key findings (limit to 6-8)
            for sentence in sentences[:8]:
                bullet = self._sentence_to_bullet(sentence)
                if len(bullet) > 10:
                    section['bullet_points'].append(bullet)
        else:
            section['bullet_points'].append("Results content not found")
        
        return section
    
    def _structure_discussion(self) -> Dict:
        """Structure discussion section."""
        section = {
            'title': 'Discussion',
            'bullet_points': []
        }
        
        # Extract discussion section
        discussion_match = re.search(
            r'(?i)discussion\s*[\.:]?\s*(.*?)(?=\n\s*(?:conclusion|references|\d+\.))',
            self.full_text,
            re.DOTALL
        )
        
        if discussion_match:
            discussion_text = discussion_match.group(1)
            
            # Split into sentences
            sentences = re.split(r'[.!?]+', discussion_text)
            
            # Convert to bullet points (limit to 5-6)
            for sentence in sentences[:6]:
                bullet = self._sentence_to_bullet(sentence)
                if len(bullet) > 10:
                    section['bullet_points'].append(bullet)
        else:
            section['bullet_points'].append("Discussion content not found")
        
        return section
    
    def _structure_conclusions(self) -> Dict:
        """Structure conclusions section."""
        section = {
            'title': 'Conclusions',
            'bullet_points': []
        }
        
        # Extract conclusions section
        conclusions_match = re.search(
            r'(?i)conclusions?\s*[\.:]?\s*(.*?)(?=\n\s*(?:references|acknowledgments|\d+\.|$))',
            self.full_text,
            re.DOTALL
        )
        
        if conclusions_match:
            conclusions_text = conclusions_match.group(1)
            
            # Split into sentences
            sentences = re.split(r'[.!?]+', conclusions_text)
            
            # Main takeaways (limit to 3-5)
            for sentence in sentences[:5]:
                bullet = self._sentence_to_bullet(sentence)
                if len(bullet) > 10:
                    section['bullet_points'].append(bullet)
        else:
            section['bullet_points'].append("Conclusions content not found")
        
        return section
    
    def generate_latex_content(self, package: str = 'beamerposter') -> str:
        """
        Generate LaTeX content for poster.
        
        Args:
            package: LaTeX package type
        
        Returns:
            LaTeX formatted content
        """
        poster_data = self.structure_for_poster()
        latex_content = []
        
        # Header
        latex_content.append(f"% Title: {poster_data['title']}")
        latex_content.append(f"% Authors: {', '.join(poster_data['authors'])}")
        latex_content.append("")
        
        # Generate sections based on package
        if package == 'beamerposter':
            for section_name, section_data in poster_data['sections'].items():
                latex_content.append(f"\\begin{{block}}{{{section_data['title']}}}")
                latex_content.append("\\begin{itemize}")
                for bullet in section_data.get('bullet_points', []):
                    latex_content.append(f"  \\item {bullet}")
                latex_content.append("\\end{itemize}")
                latex_content.append("\\end{block}\n")
        
        elif package == 'tikzposter':
            for section_name, section_data in poster_data['sections'].items():
                latex_content.append(f"\\block{{{section_data['title']}}}{{")
                latex_content.append("\\begin{itemize}")
                for bullet in section_data.get('bullet_points', []):
                    latex_content.append(f"  \\item {bullet}")
                latex_content.append("\\end{itemize}")
                latex_content.append("}\n")
        
        elif package == 'baposter':
            for i, (section_name, section_data) in enumerate(poster_data['sections'].items()):
                latex_content.append(
                    f"\\headerbox{{{section_data['title']}}}{{"
                    f"name={section_name},column=0,row={i}}}"
                )
                latex_content.append("\\begin{itemize}")
                for bullet in section_data.get('bullet_points', []):
                    latex_content.append(f"  \\item {bullet}")
                latex_content.append("\\end{itemize}")
                latex_content.append("}\n")
        
        return '\n'.join(latex_content)
    
    def save_to_json(self, output_path: str):
        """Save structured content to JSON."""
        poster_data = self.structure_for_poster()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(poster_data, f, indent=2, ensure_ascii=False)
        
        print(f"[*] Saved structured content to {output_path}")
        print(f"  Total words: {poster_data['word_count']}")
        print(f"  Sections: {list(poster_data['sections'].keys())}")
    
    def save_to_latex(self, output_path: str, package: str = 'beamerposter'):
        """Save LaTeX formatted content."""
        latex_content = self.generate_latex_content(package)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"[*] Saved LaTeX content to {output_path}")
    
    def close(self):
        """Close PDF file."""
        self.pdf.close()


def main():
    parser = argparse.ArgumentParser(
        description="Structure PDF content for poster format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Structure content and save to JSON
  python scripts/structure_content.py paper.pdf poster_content.json
  
  # Generate LaTeX content
  python scripts/structure_content.py paper.tex --package beamerposter
  
  # Save to both JSON and LaTeX
  python scripts/structure_content.py paper.pdf --json output.json --latex output.tex
  
  # Limit word count
  python scripts/structure_content.py paper.pdf --max-words 600
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Input PDF or LaTeX file"
    )
    
    parser.add_argument(
        "--json",
        help="Output JSON file"
    )
    
    parser.add_argument(
        "--latex",
        help="Output LaTeX file"
    )
    
    parser.add_argument(
        "--package",
        choices=['beamerposter', 'tikzposter', 'baposter'],
        default='beamerposter',
        help="LaTeX package type (default: beamerposter)"
    )
    
    parser.add_argument(
        "--max-words",
        type=int,
        default=800,
        help="Maximum word count (default: 800)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)
    
    # Only process PDF files
    if input_path.suffix.lower() != '.pdf':
        print("Error: Input file must be a PDF")
        sys.exit(1)
    
    # Structure content
    structurer = ContentStructurer(args.input_file)
    
    try:
        # Save to JSON
        if args.json:
            structurer.save_to_json(args.json)
        
        # Save to LaTeX
        if args.latex:
            structurer.save_to_latex(args.latex, args.package)
        
        # If neither specified, print summary
        if not args.json and not args.latex:
            poster_data = structurer.structure_for_poster()
            print("\n" + "="*60)
            print("POSTER CONTENT SUMMARY")
            print("="*60)
            print(f"\nTitle: {poster_data['title']}")
            print(f"Authors ({len(poster_data['authors'])}): {', '.join(poster_data['authors'][:5])}")
            print(f"\nWord Count: {poster_data['word_count']}")
            print(f"\nSections:")
            for section_name, section_data in poster_data['sections'].items():
                bullets = section_data.get('bullet_points', [])
                print(f"\n{section_data['title']} ({len(bullets)} bullets):")
                for bullet in bullets[:3]:
                    print(f"  - {bullet[:80]}...")
    
    finally:
        structurer.close()


if __name__ == "__main__":
    main()
