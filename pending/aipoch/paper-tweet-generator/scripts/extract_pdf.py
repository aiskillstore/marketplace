import sys
import json
from pypdf import PdfReader

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    text = extract_text_from_pdf(file_path)
    # Output raw text to stdout
    print(text)
