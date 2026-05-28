import argparse
import requests
import sys
import json

CONTENT_SERVICE_URL = "https://reactome.org/ContentService"
ANALYSIS_SERVICE_URL = "https://reactome.org/AnalysisService"

def query_content(query_id):
    """
    Retrieve pathway info by ID.
    """
    url = f"{CONTENT_SERVICE_URL}/data/query/{query_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

def analyze_identifiers(identifiers):
    """
    Submit a gene list to the Analysis Service.
    """
    url = f"{ANALYSIS_SERVICE_URL}/identifiers/"
    # Reactome expects text/plain with newlines or commas
    data = identifiers.replace(",", "\n")
    headers = {"Content-Type": "text/plain"}
    
    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

def main():
    parser = argparse.ArgumentParser(description="Reactome Database Skill CLI")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # Query Content Command
    query_parser = subparsers.add_parser("query_content", help="Retrieve pathway info by ID")
    query_parser.add_argument("--id", required=True, help="Reactome ID (e.g., R-HSA-69278)")

    # Analyze Identifiers Command
    analyze_parser = subparsers.add_parser("analyze_identifiers", help="Submit gene list for analysis")
    analyze_parser.add_argument("--identifiers", required=True, help="Gene identifiers (comma or newline separated)")

    args = parser.parse_args()

    result = {}
    if args.action == "query_content":
        result = query_content(args.id)
    elif args.action == "analyze_identifiers":
        result = analyze_identifiers(args.identifiers)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
