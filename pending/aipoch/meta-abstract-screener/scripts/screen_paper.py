import json
import sys

def validate_screening_result(json_str):
    """
    Validates that the input string is a valid JSON object adhering to the screening schema.
    Schema:
    {
        "Result": "Yes" | "No" | "Maybe",
        "Reason": "NA" | "irrelevant"
    }
    """
    try:
        # Clean up code blocks if present
        if json_str.startswith("```json"):
            json_str = json_str.split("```json")[1]
        if json_str.endswith("```"):
            json_str = json_str.rsplit("```", 1)[0]
        
        data = json.loads(json_str.strip())
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format. {str(e)}")
        return False

    # Check required keys
    required_keys = ["Result", "Reason"]
    for key in required_keys:
        if key not in data:
            print(f"Error: Missing required key '{key}'.")
            return False
            
    # Check Result enum
    valid_results = ["Yes", "No", "Maybe"]
    if data.get("Result") not in valid_results:
        print(f"Error: Invalid Result '{data.get('Result')}'. Must be one of {valid_results}.")
        return False

    # Check Reason enum (Soft check, as sometimes reasons might need to be descriptive, 
    # but the prompt asked for NA/irrelevant. We will enforce it as per prompt.)
    valid_reasons = ["NA", "irrelevant"]
    # Note: The original Dify prompt implies these are the only allowed values.
    if data.get("Reason") not in valid_reasons:
        print(f"Warning: Reason '{data.get('Reason')}' is not 'NA' or 'irrelevant'.")
        # We allow it to pass with a warning, or fail? 
        # The prompt said "Enum: [NA, irrelevant]". Let's fail to be strict.
        print(f"Error: Reason must be one of {valid_reasons}.")
        return False
        
    print("Validation Passed: Output conforms to schema.")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Join all arguments in case the JSON string was split by shell
        input_str = " ".join(sys.argv[1:])
        success = validate_screening_result(input_str)
        sys.exit(0 if success else 1)
    else:
        print("Usage: python screen_paper.py '<json_string>'")
        sys.exit(1)
