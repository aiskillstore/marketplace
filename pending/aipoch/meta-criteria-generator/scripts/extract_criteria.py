import re
import argparse
import sys

def extract_content(text):
    # Regex to find content inside the LAST pair of curly braces
    # Pattern explanation:
    # \{        : match literal {
    # ([^}]*)   : capture group 1: any character except }
    # \}        : match literal }
    # (?!.*\{)  : negative lookahead: assert that there are no more { after this match
    pattern = r'\{([^}]*)\}(?!.*\{)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip().replace("\n\n", "\n")
    return None

def main():
    parser = argparse.ArgumentParser(description="Extract and format inclusion/exclusion criteria.")
    parser.add_argument("--inclusion", required=True, help="Text containing inclusion criteria")
    parser.add_argument("--exclusion", required=True, help="Text containing exclusion criteria")
    
    # Handle potentially multiline inputs
    args = parser.parse_args()

    inc_text = extract_content(args.inclusion)
    exc_text = extract_content(args.exclusion)

    output_parts = []
    if inc_text:
        output_parts.append("**Inclusion Criteria:**\n" + inc_text)
    if exc_text:
        output_parts.append("**Exclusion Criteria:**\n" + exc_text)

    result = "\n\n".join(output_parts) if output_parts else "No criteria found. Ensure the LLM output is enclosed in {}."
    print(result)

if __name__ == "__main__":
    main()
