import sys
import os

def extract_text(file_path):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
        if ext == '.pdf':
            # Try pypdf first, then PyPDF2
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(file_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    return "Error: pypdf library not found. Please run: pip install pypdf"
            except Exception as e:
                return f"Error reading PDF: {str(e)}"
                
        if ext == '.docx':
            try:
                import docx
                doc = docx.Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                return text
            except ImportError:
                 return "Error: python-docx library not found. Please run: pip install python-docx"
            except Exception as e:
                return f"Error reading DOCX: {str(e)}"

        if ext == '.doc':
            return "Error: .doc format (binary Word) is not directly supported by this script. Please save the file as .docx or .pdf."

        return f"Error: Unsupported file extension {ext}"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <file_path>")
        sys.exit(1)
        
    print(extract_text(sys.argv[1]))
