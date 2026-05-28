# -*- coding: utf-8 -*-
import re
import sys
import io

# Set stdout to UTF-8 to handle Chinese characters properly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clean_markdown_symbols(text):
    """Removes markdown code block fences."""
    text = re.sub(r'^```markdown\s*|\s*```markdown\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*|\s*```\s*$', '', text, flags=re.MULTILINE)
    return text.strip()

def extract_table_content(text):
    """Extracts content within curly braces."""
    pattern = r'\{\s*(.*?)\s*\}'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def insert_citation_before_last_punctuation(text, citation_tag, language):
    """
    Inserts citation tag before the last punctuation of the description.
    Handles both English and Chinese punctuation marks.
    """
    # Define punctuation patterns based on language
    if language == 'English':
        punctuation_pattern = r'[.!?]'
    else:
        punctuation_pattern = r'[.!?。！？]'
    
    # Find all punctuation positions
    matches = list(re.finditer(punctuation_pattern, text))
    
    if matches:
        # Get the last punctuation match
        last_match = matches[-1]
        last_punctuation_index = last_match.start()
        # Insert citation before the punctuation
        modified_text = text[:last_punctuation_index] + citation_tag + text[last_punctuation_index:]
    else:
        # Append if no punctuation found
        modified_text = text + citation_tag
    
    return modified_text

def process_content(text_description, raw_table, language):
    """
    Combines text description and table with specific formatting rules.
    1. Inserts citation tag before the last punctuation of the description.
    2. Cleans and extracts the markdown table.
    3. Combines them with a standard header and table title.
    """
    # Constants based on language
    if language == 'English':
        citation_tag = "(Table 1)"
        table_title = "**Table 1 Characteristics of the included studies for the meta-analysis**"
        result_header = "**【Results】**"
    else:  # Default to English
        citation_tag = "(Table 1)"
        table_title = "**Table 1 Characteristics of the included studies for the meta-analysis**"
        result_header = "**【Results】**"

    # 1. Insert citation tag before last punctuation
    modified_text = insert_citation_before_last_punctuation(text_description, citation_tag, language)

    # 2. Clean and extract table
    cleaned_table = clean_markdown_symbols(raw_table)
    table_content = extract_table_content(cleaned_table)

    # 3. Combine
    final_output = f"{result_header}\n\n{modified_text}\n\n{table_title}\n\n{table_content}"
    return final_output

if __name__ == "__main__":
    # simple CLI for testing or invocation
    # Usage: python text_processor.py <language> <text_description> <raw_table>
    
    if len(sys.argv) < 4:
        print("Usage: python text_processor.py <language> <text_description> <raw_table>")
    else:
        lang = sys.argv[1]
        text = sys.argv[2]
        table = sys.argv[3]
        print(process_content(text, table, lang))
