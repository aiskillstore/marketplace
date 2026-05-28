import argparse
import json
import sys
import requests
from urllib.parse import urlencode

BASE_URL = "https://biodbnet-abcc.ncifcrf.gov/webServices/rest.php/biodbnetRestApi.json"

def call_biodbnet(method, params):
    """
    Executes a bioDBnet API call.
    """
    # "method" argument is part of the query string for bioDBnet
    query_params = {"method": method}
    
    # Merge with user params
    if params:
        query_params.update(params)
    
    # bioDBnet often expects comma separated values for lists
    # The user should provide them as strings or we handle list conversion
    for k, v in query_params.items():
        if isinstance(v, list):
            query_params[k] = ",".join(map(str, v))
            
    try:
        response = requests.get(BASE_URL, params=query_params)
        response.raise_for_status()
        
        # bioDBnet returns JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "content": response.text}
            
    except requests.RequestException as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="bioDBnet API Client")
    parser.add_argument("--method", required=True, help="API method name (e.g., db2db, getPathways)")
    parser.add_argument("--params", help="JSON string of parameters (e.g., '{\"input\":\"geneid\", \"taxonId\":9606}')")
    
    args = parser.parse_args()
    
    params = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON in --params"}))
            sys.exit(1)
            
    result = call_biodbnet(args.method, params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
