import requests
import time
import sys
import json
import argparse

BASE_URL = "https://rest.uniprot.org"

def search_protein(query, fmt="json"):
    """Search UniProtKB."""
    url = f"{BASE_URL}/uniprotkb/search"
    params = {"query": query, "format": fmt}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)})

def retrieve_entry(accession, fmt="json"):
    """Retrieve a specific entry."""
    url = f"{BASE_URL}/uniprotkb/{accession}"
    if fmt != "json":
        url += f".{fmt}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)})

def map_identifiers(from_db, to_db, ids):
    """
    Map identifiers.
    Note: This is a simplified synchronous wrapper around the async API.
    """
    # Step 1: Submit job
    url = f"{BASE_URL}/idmapping/run"
    data = {
        "from": from_db,
        "to": to_db,
        "ids": ids
    }
    try:
        job_req = requests.post(url, data=data)
        job_req.raise_for_status()
        job_id = job_req.json()["jobId"]
        
        # Step 2: Poll status
        while True:
            status_res = requests.get(f"{BASE_URL}/idmapping/status/{job_id}")
            status_res.raise_for_status()
            status = status_res.json()
            if status["jobStatus"] in ["FINISHED", "ERROR"]:
                break
            time.sleep(1)
            
        if status["jobStatus"] == "ERROR":
            return json.dumps({"error": "ID Mapping job failed"})
            
        # Step 3: Get results
        results_req = requests.get(f"{BASE_URL}/idmapping/results/{job_id}")
        results_req.raise_for_status()
        return results_req.text
        
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UniProt Client")
    subparsers = parser.add_subparsers(dest="command")
    
    # Search
    p_search = subparsers.add_parser("search")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--format", default="json")
    
    # Retrieve
    p_retrieve = subparsers.add_parser("retrieve")
    p_retrieve.add_argument("--accession", required=True)
    p_retrieve.add_argument("--format", default="json")
    
    # Map
    p_map = subparsers.add_parser("map")
    p_map.add_argument("--from-db", required=True)
    p_map.add_argument("--to-db", required=True)
    p_map.add_argument("--ids", required=True)
    
    args = parser.parse_args()
    
    if args.command == "search":
        print(search_protein(args.query, args.format))
    elif args.command == "retrieve":
        print(retrieve_entry(args.accession, args.format))
    elif args.command == "map":
        print(map_identifiers(args.from_db, args.to_db, args.ids))
    else:
        parser.print_help()
