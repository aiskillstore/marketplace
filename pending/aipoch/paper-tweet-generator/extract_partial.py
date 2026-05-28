import sys
import pypdf

def extract_first_pages(file_path, max_pages=10):
    try:
        reader = pypdf.PdfReader(file_path)
        total_pages = len(reader.pages)
        print(f"Total pages: {total_pages}", file=sys.stderr)
        
        pages = []
        for i, page in enumerate(reader.pages):
            if i >= max_pages:
                break
            text = page.extract_text()
            if text:
                pages.append(f"=== Page {i+1} ===")
                pages.append(text)
        
        text = "\n".join(pages)
        return text
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_partial.py <file_path>")
        sys.exit(1)
    
    result = extract_first_pages(sys.argv[1], 10)
    try:
        print(result)
    except UnicodeEncodeError:
        print(result.encode('utf-8', errors='ignore').decode('utf-8'))