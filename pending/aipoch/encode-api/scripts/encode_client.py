import requests
import json
import time

HEADERS = {'accept': 'application/json'}
BASE_URL = 'https://www.encodeproject.org'

def get_object(accession, api_key=None, api_secret=None):
    """
    Retrieve an object from ENCODE by accession ID.
    
    Args:
        accession (str): The accession ID (e.g., 'ENCBS000AAA').
        api_key (str, optional): API Key ID.
        api_secret (str, optional): API Secret Key.
        
    Returns:
        dict: The JSON response object.
    """
    auth = (api_key, api_secret) if api_key and api_secret else None
    
    # Handle accessions that might already be paths
    if accession.startswith("/"):
        url = f"{BASE_URL}{accession}"
    else:
        # Assume it's an ID like ENCBS000AAA
        # The docs say we can just use the accession in the URL
        url = f"{BASE_URL}/{accession}/?frame=object"
    
    try:
        response = requests.get(url, headers=HEADERS, auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if response.status_code == 404:
            print("Resource not found.")
        raise
    except Exception as e:
        print(f"Error retrieving object: {e}")
        raise

def search_encode(term, limit=10, api_key=None, api_secret=None):
    """
    Search ENCODE for a term.
    
    Args:
        term (str): Search term.
        limit (int): Max number of results.
        api_key (str, optional): API Key ID.
        api_secret (str, optional): API Secret Key.
        
    Returns:
        list: List of result objects (from @graph).
    """
    auth = (api_key, api_secret) if api_key and api_secret else None
    
    # Construct search URL
    # Note: simple string concatenation for term, should be urlencoded in production but simple here
    url = f"{BASE_URL}/search/?searchTerm={term}&frame=object&limit={limit}"
    
    try:
        response = requests.get(url, headers=HEADERS, auth=auth)
        response.raise_for_status()
        data = response.json()
        return data.get('@graph', [])
    except Exception as e:
        print(f"Error searching: {e}")
        raise

if __name__ == "__main__":
    # Example usage for testing
    print("--- Testing ENCODE API Client ---")
    
    # 1. Test Search
    try:
        print("\nSearching for 'bone chip'...")
        results = search_encode("bone chip", limit=2)
        print(f"Found {len(results)} results.")
        if results:
            first = results[0]
            print(f"First result: {first.get('accession', 'No Accession')} - {first.get('@type', [])}")
    except Exception as e:
        print(f"Search failed: {e}")

    # 2. Test Get Object
    try:
        print("\nRetrieving ENCBS000AAA...")
        # Note: The docs say ENCBS000AAA is a valid accession
        obj = get_object("ENCBS000AAA")
        print(f"Success! Retrieved object type: {obj.get('@type')}")
        print(f"Description: {obj.get('description')}")
    except Exception as e:
        print(f"Get Object failed: {e}")
