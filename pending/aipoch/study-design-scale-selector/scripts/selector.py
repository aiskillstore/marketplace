import requests
import json
import sys

def fetch_metadata(pmid):
    if not pmid:
        return {}
    
    # Clean PMID (remove spaces, etc.)
    pmid = pmid.strip()
    
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        'db': 'pubmed',
        'id': pmid,
        'retmode': 'json'
    }
    
    try:
        # Set a reasonable timeout
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result = data.get('result', {})
        uids = result.get('uids', [])
        
        if not uids:
            return {}
            
        # Get the first (and only) UID's details
        details = result.get(uids[0], {})
        pub_types = details.get('pubtype', [])
        
        # Join pubtypes to form a study_design string
        # This mimics the 'study_design' field expected by the workflow
        study_design = ", ".join(pub_types)
        
        if not study_design:
            return {}
            
        return {"study_design": study_design}
        
    except Exception as e:
        # Return empty on error to trigger fallback
        sys.stderr.write(f"Warning: API call failed: {e}\n")
        return {}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({}))
        sys.exit(0)
    
    pmid = sys.argv[1]
    result = fetch_metadata(pmid)
    print(json.dumps(result, ensure_ascii=False, indent=2))
