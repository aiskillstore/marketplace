import json
import requests
import sys

def enrich(gene_set, query_name="myQuery"):
    """
    Perform ChEA3 enrichment analysis.
    
    Args:
        gene_set (list): List of gene symbols (strings).
        query_name (str): Name for the query.
        
    Returns:
        list: JSON array of ChEA3 library result objects.
    """
    url = "https://maayanlab.cloud/chea3/api/enrich/"
    payload = {
        "query_name": query_name,
        "gene_set": gene_set
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying ChEA3 Enrichment API: {e}", file=sys.stderr)
        return None

def get_dataset_metadata(dataset="ChEA"):
    """
    Get metadata for a dataset from Harmonizome.
    
    Args:
        dataset (str): Dataset name (default: "ChEA").
        
    Returns:
        dict: Dataset metadata.
    """
    url = f"https://maayanlab.cloud/Harmonizome/api/1.0/dataset/{dataset}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Harmonizome Metadata API: {e}", file=sys.stderr)
        return None

def get_attribute_info(attribute_name):
    """
    Get information about a specific attribute (Transcription Factor) from Harmonizome.
    
    Args:
        attribute_name (str): Name of the attribute (e.g., 'CREB1').
        
    Returns:
        dict: Attribute information.
    """
    # Note: URL encoding might be needed for special characters, but standard gene names are usually safe.
    url = f"https://maayanlab.cloud/Harmonizome/api/1.0/attribute/{attribute_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Harmonizome Attribute API: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    # Simple CLI for testing or usage
    if len(sys.argv) < 2:
        print("Usage: python chea_client.py <command> [args...]")
        print("Commands: enrich <gene1> <gene2>..., metadata, attribute <name>")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "enrich":
        genes = sys.argv[2:]
        if not genes:
            print("Error: No genes provided for enrichment.")
            sys.exit(1)
        result = enrich(genes)
        print(json.dumps(result, indent=2))
        
    elif command == "metadata":
        result = get_dataset_metadata()
        print(json.dumps(result, indent=2))
        
    elif command == "attribute":
        if len(sys.argv) < 3:
            print("Error: Attribute name required.")
            sys.exit(1)
        name = sys.argv[2]
        result = get_attribute_info(name)
        print(json.dumps(result, indent=2))
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
