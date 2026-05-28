import json
import sys

def main():
    if len(sys.argv) < 2:
        # Allow reading from stdin if no argument provided
        if not sys.stdin.isatty():
            arg1 = sys.stdin.read()
        else:
            print("Usage: python calculate_nos_score.py <json_string>")
            sys.exit(1)
    else:
        arg1 = sys.argv[1]
    
    try:
        json_data = json.loads(arg1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input")
        sys.exit(1)
    
    # Calculate stars count
    count = 0
    for key, value in json_data.items():
        if key == "Study": continue
        # Check if the value contains '*' (affirmative answer)
        if '*' in str(value):
            count += 1

    headers = [
        "Study",
        "Representativeness of the Exposed Cohort", 
        "Selection of the Non-Exposed Cohort", 
        "Ascertainment of Exposure", 
        "Demonstration that outcome of interest was not present at start of study",
        "Age comparability",
        "Additional comparability",
        "Assessment of Outcome", 
        "Enough follow-up",
        "Adequacy of follow up of cohorts",
        "Overall"
    ]
    
    row = [
        json_data.get("Study", ""),
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

    markdown_output = "\n".join(markdown_table)
    
    print(markdown_output)

if __name__ == "__main__":
    main()
