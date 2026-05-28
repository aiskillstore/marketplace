import os
import requests
import json

BASE_URL = "https://api.semanticscholar.org/graph/v1"
API_KEY = os.environ.get("S2_API_KEY")

def _get_headers():
    headers = {}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    return headers

def search_papers(query, limit=10, fields="title,year,authors,abstract"):
    """Search for papers by keyword."""
    url = f"{BASE_URL}/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": fields
    }
    response = requests.get(url, headers=_get_headers(), params=params)
    response.raise_for_status()
    return response.json()

def get_paper_details(paper_id, fields="title,year,authors,abstract,venue,citationCount"):
    """Get details for a specific paper."""
    url = f"{BASE_URL}/paper/{paper_id}"
    params = {"fields": fields}
    response = requests.get(url, headers=_get_headers(), params=params)
    response.raise_for_status()
    return response.json()

def get_author_details(author_id, fields="name,aliases,affiliations,paperCount,hIndex"):
    """Get author profile."""
    url = f"{BASE_URL}/author/{author_id}"
    params = {"fields": fields}
    response = requests.get(url, headers=_get_headers(), params=params)
    response.raise_for_status()
    return response.json()

def get_citations(paper_id, method="citations", limit=10, fields="title,year,authors"):
    """
    Get citations or references for a paper.
    method: 'citations' (papers citing this) or 'references' (papers cited by this)
    """
    if method not in ["citations", "references"]:
        raise ValueError("method must be 'citations' or 'references'")
        
    url = f"{BASE_URL}/paper/{paper_id}/{method}"
    params = {"limit": limit, "fields": fields}
    response = requests.get(url, headers=_get_headers(), params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Test example from doc
    print("Testing Semantic Scholar Client...")
    try:
        # Attention Is All You Need
        pid = "649def34f8be52c8b66281af98ae884c09aef38b" 
        details = get_paper_details(pid, fields="title,year,citationCount")
        print(f"Title: {details.get('title')}")
        print(f"Year: {details.get('year')}")
        print(f"Citations: {details.get('citationCount')}")
    except Exception as e:
        print(f"Error: {e}")
