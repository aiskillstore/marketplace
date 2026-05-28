import argparse
import requests
import json
import os
import sys

def fetch_structure(uniprot_id, output_dir, file_format="cif"):
    """
    Fetches AlphaFold structure and metadata for a given UniProt ID.
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Fetching metadata for UniProt ID: {uniprot_id}...")
    
    # 1. Get Metadata
    api_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metadata: {e}")
        sys.exit(1)

    if not data:
        print(f"No AlphaFold prediction found for {uniprot_id}")
        sys.exit(1)

    # Assume the first entry is the primary prediction
    prediction = data[0]
    
    # Extract URLs
    cif_url = prediction.get("cifUrl")
    pdb_url = prediction.get("pdbUrl")
    pae_url = prediction.get("paeDocUrl")
    
    download_url = cif_url if file_format == "cif" else pdb_url
    if not download_url:
        print(f"Requested format {file_format} not available for {uniprot_id}")
        sys.exit(1)

    # 2. Download Structure File
    filename = f"{uniprot_id}.{file_format}"
    filepath = os.path.join(output_dir, filename)
    
    print(f"Downloading structure from {download_url}...")
    try:
        file_resp = requests.get(download_url)
        file_resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(file_resp.content)
        print(f"Structure saved to: {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading structure file: {e}")
        sys.exit(1)

    # 3. Save Metadata (including PAE URL and basic info)
    metadata = {
        "uniprot_id": uniprot_id,
        "entryId": prediction.get("entryId"),
        "gene": prediction.get("gene"),
        "uniprotDescription": prediction.get("uniprotDescription"),
        "taxId": prediction.get("taxId"),
        "organismScientificName": prediction.get("organismScientificName"),
        "cifUrl": cif_url,
        "pdbUrl": pdb_url,
        "paeDocUrl": pae_url,
        "latestVersion": prediction.get("latestVersion"),
        "maintainedBy": "DeepMind / EMBL-EBI"
    }
    
    metadata_path = os.path.join(output_dir, f"{uniprot_id}_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {metadata_path}")

def main():
    parser = argparse.ArgumentParser(description="Fetch AlphaFold structure and metadata.")
    parser.add_argument("--uniprot_id", required=True, help="UniProt Accession ID (e.g., P00520)")
    parser.add_argument("--output_dir", required=True, help="Directory to save outputs")
    parser.add_argument("--format", choices=["cif", "pdb"], default="cif", help="Structure file format")
    
    args = parser.parse_args()
    
    fetch_structure(args.uniprot_id, args.output_dir, args.format)

if __name__ == "__main__":
    main()
