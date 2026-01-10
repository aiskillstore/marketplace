"""
Office Processor Tool
Handles PDF extraction and advanced Markdown processing.
"""

import pdfplumber
import markdown
from pathlib import Path

class OfficeProcessor:
    def __init__(self, output_dir: str = "generated_docs/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts text from a PDF file.
        
        Args:
            pdf_path: Absolute path to the PDF file.
            
        Returns:
            Extracted text content.
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
        
        return text

    def markdown_to_html(self, markdown_text: str) -> str:
        """
        Converts Markdown text to HTML.
        Useful for preprocessing before sending to PPT/Word generators.
        """
        return markdown.markdown(markdown_text, extensions=['extra', 'codehilite'])

if __name__ == "__main__":
    processor = OfficeProcessor()
    # Test Markdown
    md = "# Hello\n\n* Item 1\n* Item 2"
    print(processor.markdown_to_html(md))
