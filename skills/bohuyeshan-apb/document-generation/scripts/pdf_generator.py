"""
PDF Generator Tool
Converts HTML content (including Markdown-converted HTML) into a PDF document.
Uses WeasyPrint for rendering.
"""

import datetime
from pathlib import Path

class PDFGenerator:
    def __init__(self, output_dir: str = "generated_docs/pdf"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(self, content: str, filename: str = None, is_html: bool = True) -> str:
        """
        Generates a PDF file from the provided content.
        
        Args:
            content: The content to convert (HTML string).
            filename: Optional filename.
            is_html: Whether the content is already HTML. If False, assumes plain text (or Markdown if pre-processed).
            
        Returns:
            The absolute path to the generated PDF file.
        """
        try:
            from weasyprint import HTML
        except (ImportError, OSError):
            return "Error: WeasyPrint library not installed."

        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"document_{timestamp}.pdf"
            
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_path = self.output_dir / filename
        
        # Ensure content is HTML string
        html_content = content
        if not is_html:
            # Wrap plain text in simple HTML
            html_content = f"<p>{content}</p>"
            
        # Add basic styling if not present (simple check)
        if "<html>" not in html_content:
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: sans-serif; padding: 2em; line-height: 1.6; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; border-bottom: 1px solid #eee; margin-top: 1.5em; }}
                    p {{ margin-bottom: 1em; }}
                    li {{ margin-bottom: 0.5em; }}
                    code {{ background-color: #f8f9fa; padding: 0.2em 0.4em; border-radius: 3px; font-family: monospace; }}
                    pre {{ background-color: #f8f9fa; padding: 1em; border-radius: 5px; overflow-x: auto; }}
                    img {{ max-width: 100%; height: auto; margin: 1em 0; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
        try:
            HTML(string=html_content).write_pdf(str(output_path))
            return str(output_path.absolute())
        except Exception as e:
            return f"Error generating PDF: {str(e)}"

if __name__ == "__main__":
    generator = PDFGenerator()
    sample_html = "<h1>Test PDF</h1><p>This is a test.</p>"
    print(generator.generate_pdf(sample_html))
