import argparse
import re
import sys

def main():
    parser = argparse.ArgumentParser(description="Format the risk of bias text.")
    parser.add_argument("--text", required=True, help="The generated text to format.")
    parser.add_argument("--language", required=True, help="The language (Chinese or English).")
    args = parser.parse_args()

    arg1 = args.text
    language = args.language

    # Determine figure label based on language
    # If language contains 'Chinese' or 'Chinese', use (Figure 1), else (Figure 1)
    if 'Chinese' in language or 'Chinese' in language:
        figure_ref = "(Figure 1)"
        caption = "**Figure 1 Bias assessment results**"
    else:
        figure_ref = "(Figure 1)"
        caption = "**Figure 1 Risk of bias results**"

    # Find last punctuation
    punctuation_pattern = r'[.!?。！？]'
    last_punctuation_match = re.search(punctuation_pattern, arg1[::-1])

    if last_punctuation_match:
        last_punctuation_index = len(arg1) - last_punctuation_match.start() - 1
        modified_arg1 = arg1[:last_punctuation_index] + figure_ref + arg1[last_punctuation_index:]
    else:
        modified_arg1 = arg1 + figure_ref

    output = f"**Quality assessment**\n\n{modified_arg1}\n\n{{Insert your picture here}}\n\n {caption}"
    
    # Print the result to stdout
    print(output)

if __name__ == "__main__":
    main()
