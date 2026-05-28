import argparse
import requests
import json
import sys

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

def search_clinvar(term, retmax=10):
    """
    Search ClinVar using E-utilities.
    """
    params = {
        "db": "clinvar",
        "term": term,
        "retmode": "json",
        "retmax": retmax
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        count = data.get("esearchresult", {}).get("count", 0)
        ids = data.get("esearchresult", {}).get("idlist", [])
        
        result = {
            "count": count,
            "ids": ids,
            "term": term
        }
        print(json.dumps(result, indent=2))
        return result
        
    except Exception as e:
        print(f"Error querying ClinVar: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search ClinVar database")
    parser.add_argument("--term", required=True, help="Search term (e.g., 'BRCA1[gene]')")
    parser.add_argument("--retmax", type=int, default=10, help="Max results")
    
    args = parser.parse_args()
    search_clinvar(args.term, args.retmax)
