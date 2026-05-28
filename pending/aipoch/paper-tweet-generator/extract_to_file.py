import sys
import os
import pypdf

def extract_full_text(file_path, output_file):
    try:
        reader = pypdf.PdfReader(file_path)
        total_pages = len(reader.pages)
        print(f"Extracting {total_pages} pages...", file=sys.stderr)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, page in enumerate(reader.pages):
                if i % 10 == 0:
                    print(f"Page {i+1}/{total_pages}", file=sys.stderr)
                text = page.extract_text()
                if text:
                    f.write(f"=== Page {i+1} ===\n")
                    f.write(text)
                    f.write("\n\n")
        
        print(f"Text saved to {output_file}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    pdf_file = "PMID：39742810-PIIS0092867424013412.pdf"
    output_file = "extracted_text.txt"
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    success = extract_full_text(pdf_file, output_file)
    sys.exit(0 if success else 1)