import argparse
import json
import sys
import urllib.request
import urllib.parse
import time
from datetime import datetime

# NCBI E-utilities Base URL
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search_geo(term, db="gds", retmax=20, email=None, api_key=None):
    """
    Search GEO database using NCBI E-utilities.
    """
    params = {
        "db": db,
        "term": term,
        "retmode": "json",
        "retmax": retmax,
        "usehistory": "y"
    }
    
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
        
    query_string = urllib.parse.urlencode(params)
    search_url = f"{BASE_URL}esearch.fcgi?{query_string}"
    
    try:
        with urllib.request.urlopen(search_url) as response:
            data = json.loads(response.read().decode())
            
        if "esearchresult" not in data:
            return {"error": "Invalid response from NCBI ESearch"}
            
        result = data["esearchresult"]
        if "error" in result:
             return {"error": result["errorlist"]}
             
        count = result.get("count", 0)
        id_list = result.get("idlist", [])
        
        if not id_list:
            return {"count": count, "results": []}
            
        # Get summaries for found IDs
        return get_summaries(db, id_list, email, api_key)
        
    except Exception as e:
        return {"error": str(e)}

def get_summaries(db, id_list, email=None, api_key=None):
    """
    Retrieve summaries for a list of IDs.
    """
    ids = ",".join(id_list)
    params = {
        "db": db,
        "id": ids,
        "retmode": "json",
        "version": "2.0"
    }
    
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
        
    query_string = urllib.parse.urlencode(params)
    summary_url = f"{BASE_URL}esummary.fcgi?{query_string}"
    
    try:
        with urllib.request.urlopen(summary_url) as response:
            data = json.loads(response.read().decode())
            
        if "result" not in data:
             return {"error": "Invalid response from NCBI ESummary"}
             
        # Process results
        summaries = []
        result_data = data["result"]
        
        # 'uids' list ensures order, but version 2.0 might structure differently
        # version 2.0 typically has 'uids' list and then keys for each UID
        uids = result_data.get("uids", [])
        
        for uid in uids:
            if uid in result_data:
                item = result_data[uid]
                summary = {
                    "uid": uid,
                    "accession": item.get("accession", ""),
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "taxon": item.get("taxon", ""),
                    "entry_type": item.get("entrytype", ""),
                    "gds_type": item.get("gdstype", ""),
                    "pdat": item.get("pubdate", "")
                }
                summaries.append(summary)
                
        return {"count": len(summaries), "results": summaries}

    except Exception as e:
        return {"error": str(e)}

def construct_query(base_term, filters):
    """
    Construct a GEO query string with fields.
    """
    parts = []
    if base_term:
        parts.append(f"({base_term})")
        
    if filters:
        for key, value in filters.items():
            # Basic validation/cleaning could happen here
            # Assuming key is a valid field name or alias
            parts.append(f"{value}[{key}]")
            
    return " AND ".join(parts)

def main():
    parser = argparse.ArgumentParser(description="Search NCBI GEO")
    parser.add_argument("query", help="Main search term")
    parser.add_argument("--filters", type=str, help="JSON string of filters (field: value)")
    parser.add_argument("--db", default="gds", choices=["gds", "geoprofiles"], help="Database to search")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--email", help="User email for NCBI")
    parser.add_argument("--api_key", help="NCBI API Key")
    
    args = parser.parse_args()
    
    filters = {}
    if args.filters:
        try:
            filters = json.loads(args.filters)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON in --filters"}))
            sys.exit(1)
            
    full_query = construct_query(args.query, filters)
    
    # Identify tool to NCBI
    # It's good practice to set a tool name, though E-utilities usually require email
    
    results = search_geo(full_query, args.db, args.limit, args.email, args.api_key)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
