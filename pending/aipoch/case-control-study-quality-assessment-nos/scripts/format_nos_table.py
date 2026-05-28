import json
import sys
import os

def format_nos_table(json_input):
    """
    Parses the NOS evaluation JSON and formats it into a Markdown table.
    """
    try:
        # Check if input is a file path
        if os.path.exists(json_input):
            with open(json_input, 'r', encoding='utf-8') as f:
                json_str = f.read()
        else:
            json_str = json_input

        json_data = json.loads(json_str)
    except Exception as e:
        return f"Error: Invalid JSON input. {str(e)}"

    # Calculate count of stars (*)
    count = 0
    for value in json_data.values():
        if isinstance(value, str) and '*' in value:
            count += 1

    headers = [
        "Study",
        "Selection: Is the case definition adequate?",
        "Selection: Representativeness of the cases",
        "Selection of controls",
        "Selection: Definition of controls",
        "Age comparability",
        "Comparability of other controlled factors",
        "Ascertainment of Exposure",
        "Same method of ascertainment for cases and controls",
        "Non-Response rate",
        "Overall"
    ]

    # Mapping keys from schema to headers order
    # Schema keys: Study, D1..D9
    row = [
        json_data.get("Study", "N/A"),
        json_data.get("D1", "-"),
        json_data.get("D2", "-"),
        json_data.get("D3", "-"),
        json_data.get("D4", "-"),
        json_data.get("D5", "-"),
        json_data.get("D6", "-"),
        json_data.get("D7", "-"),
        json_data.get("D8", "-"),
        json_data.get("D9", "-"),
        str(count)
    ]

    # Prepare data for Markdown table
    markdown_table = []
    markdown_table.append("| " + " | ".join(headers) + " |")
    markdown_table.append("|" + " --- |" * len(headers))
    markdown_table.append("| " + " | ".join(row) + " |")

    return "\n".join(markdown_table)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read from command line arg
        print(format_nos_table(sys.argv[1]))
    else:
        # Read from stdin
        input_data = sys.stdin.read()
        print(format_nos_table(input_data))
