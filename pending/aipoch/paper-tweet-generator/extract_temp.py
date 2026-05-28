import sys
from pypdf import PdfReader

def main():
    file_path = "PMID：39742810-PIIS0092867424013412.pdf"
    try:
        reader = PdfReader(file_path)
        print(f"Number of pages: {len(reader.pages)}")
        
        if reader.metadata:
            print(f"title: {reader.metadata.title}")
            print(f"author: {reader.metadata.author}")
            print(f"theme: {reader.metadata.subject}")
        
        # Extract the content of the first 2 pages
        text = ""
        for i in range(min(2, len(reader.pages))):
            page_text = reader.pages[i].extract_text()
            text += page_text + "\n"
        
        print("=== Summary of the first 2 pages ===")
        print(text[:1500])
        
    except Exception as e:
        print(f"mistake: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()