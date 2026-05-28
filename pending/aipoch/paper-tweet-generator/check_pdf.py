import pypdf
import sys

def check_pdf(file_path):
    try:
        reader = pypdf.PdfReader(file_path)
        print(f"Pages: {len(reader.pages)}")
        print(f"PDF info: {reader.metadata}")
        
        # Check first page
        if len(reader.pages) > 0:
            page = reader.pages[0]
            text = page.extract_text()
            print(f"First page text length: {len(text) if text else 0}")
            if text and len(text) > 50:
                print("\n=== First 500 chars ===")
                print(text[:500])
            else:
                print("\nText extraction seems poor, may be scanned PDF")
                
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_pdf(sys.argv[1] if len(sys.argv) > 1 else "PMID：39742810-PIIS0092867424013412.pdf")