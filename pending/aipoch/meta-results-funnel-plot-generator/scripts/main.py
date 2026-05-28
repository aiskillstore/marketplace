import sys
import re
import argparse

def clean_markdown_symbols(text):
    """Removes ```markdown or ``` fences."""
    if not text:
        return ""
    return re.sub(r'^```(?:markdown)?\s*|\s*```(?:markdown)?\s*$', '', text.strip())

def extract_table_content(text):
    """Extracts content inside curly braces if present."""
    if not text:
        return ""
    match = re.search(r'\{\s*(.*?)\s*\}', text, re.DOTALL)
    return match.group(1) if match else text

def insert_text_before_last_punctuation(text, insert_text):
    """Inserts text before the last punctuation mark."""
    punctuation_pattern = r'[.!?。！？]'
    # Search in reverse
    last_punctuation_match = re.search(punctuation_pattern, text[::-1])
    
    if last_punctuation_match:
        last_punctuation_index = len(text) - last_punctuation_match.start() - 1
        return text[:last_punctuation_index] + insert_text + text[last_punctuation_index:]
    else:
        return text + insert_text

def main():
    parser = argparse.ArgumentParser(description="Assemble Meta-Analysis Report")
    parser.add_argument("--desc", help="Funnel plot description from LLM", required=True)
    parser.add_argument("--egger", help="Egger's test table from LLM", required=True)
    parser.add_argument("--begg", help="Begg's test table from LLM", required=True)
    parser.add_argument("--trim", help="Trim and Fill table from LLM", required=True)
    parser.add_argument("--lang", help="Language (English/Chinese)", default="English")
    
    args = parser.parse_args()
    
    # 1. Prepare Figure Label based on language
    fig_label_insert = "(Figure 3)" if args.lang == "English" else "(Figure 3)"
    fig_legend = "**Figure 3 Funnel plot of the studies included in the meta-analysis**" if args.lang == "English" else "**Figure 3 Funnel plot of original research included in meta-analysis**"
    
    table_titles = []
    if args.lang == "English":
        table_titles = [
            "**Table 2 Publication bias assessment by Egger's test**",
            "**Table 3 Trim and fill method of the publication bias by Begg's test**", 
            "**Table 4 Trim and fill method of the publication bias**"
        ]
    else:
        table_titles = [
            "**Table 2 Publication bias test (Egger's test)**",
            "**Table 3 Publication bias test (Begg's test)**",
            "**Table 4 Trim and fill method for publication bias**"
        ]

    # 2. Process Description
    modified_desc = insert_text_before_last_punctuation(args.desc, fig_label_insert)
    
    output_part1 = (
        "**Funnel Plot**\n\n"
        f"{modified_desc}\n\n"
        """{Insert your picture here}

"""
        f"{fig_legend}"
    )
    
    # 3. Process Tables
    raw_tables = [args.egger, args.begg, args.trim]
    cleaned_tables = [clean_markdown_symbols(t) for t in raw_tables]
    table_contents = [extract_table_content(t) for t in cleaned_tables]
    
    # 4. Assemble Final Output
    final_output = output_part1
    for title, content in zip(table_titles, table_contents):
        final_output += f"\n\n{title}\n\n{content}"
        
    print(final_output)

if __name__ == "__main__":
    main()
