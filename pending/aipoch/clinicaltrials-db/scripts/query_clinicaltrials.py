import requests
import json
import sys

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def search_studies(condition=None, intervention=None, status=None, limit=10):
    """
    Search for clinical studies.
    """
    params = {
        "pageSize": limit,
        "format": "json"
    }
    
    # API v2 uses specific query parameter syntax
    if condition:
        params["query.cond"] = condition
    if intervention:
        params["query.intr"] = intervention
    if status:
        params["filter.overallStatus"] = status.upper()

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error searching studies: {e}", file=sys.stderr)
        return None

def get_study_details(nct_id):
    """
    Get details for a specific study by NCT ID.
    """
    url = f"{BASE_URL}/{nct_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting study details: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    # Simple CLI for testing
    if len(sys.argv) < 2:
        print("Usage: python query_clinicaltrials.py [search|details] [args...]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "search":
        # python query_clinicaltrials.py search cancer RECRUITING
        cond = sys.argv[2] if len(sys.argv) > 2 else "cancer"
        stat = sys.argv[3] if len(sys.argv) > 3 else "RECRUITING"
        print(json.dumps(search_studies(condition=cond, status=stat), indent=2))
    elif cmd == "details":
        # python query_clinicaltrials.py details NCT12345
        nct = sys.argv[2] if len(sys.argv) > 2 else ""
        if nct:
            print(json.dumps(get_study_details(nct), indent=2))
