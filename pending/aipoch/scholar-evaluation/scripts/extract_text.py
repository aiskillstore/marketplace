import sys
import os
import argparse

def extract_text(file_path):
    # --- Path Search Logic (Enhanced) ---
    if not os.path.exists(file_path):
        # Try to find the file in the current directory and subdirectories
        print(f"File {file_path} not found at specified path. Searching in current directory...", file=sys.stderr)
        found_files = []
        # Walk through the current working directory
        for root, dirs, files in os.walk(os.getcwd()):
            if file_path in files:
                found_files.append(os.path.join(root, file_path))
            # Also check if the basename matches
            elif os.path.basename(file_path) in files:
                 found_files.append(os.path.join(root, os.path.basename(file_path)))
        
        found_files = list(set(found_files))

        if len(found_files) == 1:
             file_path = found_files[0]
             print(f"Found file at: {file_path}", file=sys.stderr)
        elif len(found_files) > 1:
             print(f"Error: Multiple files found with name {os.path.basename(file_path)}:", file=sys.stderr)
             for f in found_files:
                 print(f" - {f}", file=sys.stderr)
             return None
        else:
             return f"Error: File not found at {file_path}"
    # ------------------------------------

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

        return f"Error: Unsupported file extension {ext}"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <file_path>")
        sys.exit(1)
        
    result = extract_text(sys.argv[1])
    if result and result.startswith("Error"):
        print(result, file=sys.stderr)
        sys.exit(1)
    elif result:
        sys.stdout.buffer.write(result.encode('utf-8'))
    else:
        sys.exit(1)
