import sys
import os

def extract_from_pdf(file_path):
    """
    Extracts text from PDF using pypdf, iterating page by page.
    Logic adapted from user-verified extract_to_file.py.
    """
    try:
        import pypdf
    except ImportError:
        raise ImportError("pypdf library not found. Please run: pip install pypdf")

    try:
        reader = pypdf.PdfReader(file_path)
        total_pages = len(reader.pages)
        sys.stderr.write(f"Processing PDF: {total_pages} pages found.\n")
        
        full_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"=== Page {i+1} ===\n{text}\n")
        
        return "\n".join(full_text)
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")

def extract_from_docx(file_path):
    try:
        import docx
    except ImportError:
        raise ImportError("python-docx library not found. Please run: pip install python-docx")

    try:
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        raise Exception(f"DOCX extraction failed: {str(e)}")

def extract_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"TXT extraction failed: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <input_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        sys.stderr.write(f"Error: Input file not found: {input_file}\n")
        sys.exit(1)

    _, ext = os.path.splitext(input_file)
    ext = ext.lower()

    try:
        content = ""
        if ext == '.pdf':
            content = extract_from_pdf(input_file)
        elif ext == '.docx':
            content = extract_from_docx(input_file)
        elif ext == '.txt':
            content = extract_from_txt(input_file)
        else:
            sys.stderr.write(f"Error: Unsupported file format {ext}\n")
            sys.exit(1)

        if not content.strip():
            sys.stderr.write("Warning: No text extracted. The file might be empty or scanned.\n")
            # We still exit 0 to allow the workflow to handle the warning, 
            # but usually empty content is a failure for downstream tasks.
            # Let's write a placeholder if empty to avoid crashes? 
            # No, let's just proceed.
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            sys.stderr.write(f"Successfully extracted text to {output_file}\n")
        else:
            # Configure stdout for utf-8
            if sys.stdout.encoding != 'utf-8':
                try:
                    sys.stdout.reconfigure(encoding='utf-8')
                except:
                    pass
            print(content)

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
