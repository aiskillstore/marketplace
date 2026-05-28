import argparse
import json
import re
import sys

def main():
    parser = argparse.ArgumentParser(description="Extract outline sections.")
    parser.add_argument("--text", help="The outline text to parse", required=False)
    args = parser.parse_args()

    text = args.text
    if not text:
        # Try reading from stdin if no argument
        try:
            text = sys.stdin.read()
        except Exception:
            pass

    if not text:
        print(json.dumps({"error": "No text provided"}))
        return

    # Regex to split by **Section Name**
    # Pattern matches **Title** followed by content until next **Title** or end
    
    sections = re.split(r'\*\*([^*]+)\*\*', text)
    
    result = {
        "introduction": "",
        "body": "",
        "conclusion": ""
    }
    
    # sections[0] is text before first match (usually empty or prelude)
    # sections[1] is first title, sections[2] is first content
    # sections[3] is second title, sections[4] is second content
    
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            title = sections[i].strip()
            content = sections[i + 1].strip()
            
            if "introduction" in title or "Introduction" in title:
                result["introduction"] = content
            elif "text" in title or "Body" in title:
                result["body"] = content
            elif "ending" in title or "Conclusion" in title:
                result["conclusion"] = content

    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
