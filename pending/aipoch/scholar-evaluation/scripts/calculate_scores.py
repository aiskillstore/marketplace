import json
import argparse
import sys

def calculate_weighted_score(scores):
    """
    Calculates the weighted average score based on the ScholarEval framework.
    """
    weights = {
        "Problem Formulation": 0.15,
        "Methodology": 0.20,
        "Analysis": 0.20,
        "Results": 0.15,
        "Literature Review": 0.10,
        "Data Quality": 0.10,
        "Writing Quality": 0.05,
        "Citations": 0.05
    }

    total_score = 0.0
    total_weight = 0.0
    
    details = {}

    for dimension, weight in weights.items():
        if dimension in scores:
            score = scores[dimension]
            # Ensure score is within 1-5 range
            score = max(1, min(5, score))
            total_score += score * weight
            total_weight += weight
            details[dimension] = {
                "score": score,
                "weight": weight,
                "contribution": score * weight
            }
        else:
            print(f"Warning: Missing score for dimension '{dimension}'", file=sys.stderr)

    if total_weight == 0:
        return 0.0, {}

    # Normalize if some weights are missing (though ideal input has all)
    final_score = total_score / total_weight
    
    return final_score, details

def main():
    parser = argparse.ArgumentParser(description="Calculate ScholarEval weighted scores.")
    parser.add_argument("--scores", required=True, help="Path to JSON file containing scores.")
    args = parser.parse_args()

    try:
        with open(args.scores, 'r', encoding='utf-8') as f:
            scores_data = json.load(f)
        
        final_score, details = calculate_weighted_score(scores_data)
        
        output = {
            "final_score": round(final_score, 2),
            "details": details
        }
        
        print(json.dumps(output, indent=2))
        
    except FileNotFoundError:
        print(f"Error: File not found: {args.scores}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {args.scores}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
