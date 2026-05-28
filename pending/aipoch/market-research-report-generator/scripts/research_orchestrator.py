import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import time

def search_clinical_trials(query):
    """
    Searches the external clinical trial database.
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies" 
    # API v2 uses 'query.term' for general search
    params = urllib.parse.urlencode({
        'query.term': query, 
        'pageSize': 3,
        'format': 'json'
    })
    url = f"{base_url}?{params}"
    
    try:
        # Set headers to mimic a browser and accept JSON
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
            else:
                return {"error": f"Status code {response.status}", "query": query}
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "query": query}
    except Exception as e:
        return {"error": str(e), "query": query, "note": "ClinicalTrials.gov unreachable"}

def search_pubmed(query):
    """
    Searches PubMed for relevant articles.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # 1. Search for IDs
    search_url = f"{base_url}/esearch.fcgi"
    search_params = urllib.parse.urlencode({
        'db': 'pubmed',
        'term': query,
        'retmode': 'json',
        'retmax': 3
    })
    
    try:
        # Rate limiting: NCBI requires max 3 requests/sec without API key. 
        # We sleep briefly to be safe if calling in loop.
        time.sleep(0.35)
        
        with urllib.request.urlopen(f"{search_url}?{search_params}", timeout=10) as response:
            if response.status != 200:
                return {"error": f"PubMed Search HTTP {response.status}"}
            search_data = json.loads(response.read().decode('utf-8'))
            
        id_list = search_data.get('esearchresult', {}).get('idlist', [])
        
        if not id_list:
            return {"articles": []}
            
        # 2. Fetch Summaries
        summary_url = f"{base_url}/esummary.fcgi"
        summary_params = urllib.parse.urlencode({
            'db': 'pubmed',
            'id': ','.join(id_list),
            'retmode': 'json'
        })
        
        with urllib.request.urlopen(f"{summary_url}?{summary_params}", timeout=10) as response:
            if response.status != 200:
                return {"error": f"PubMed Summary HTTP {response.status}"}
            summary_data = json.loads(response.read().decode('utf-8'))
            
        articles = []
        result_uids = summary_data.get('result', {}).get('uids', [])
        for uid in result_uids:
            item = summary_data['result'][uid]
            articles.append({
                'title': item.get('title', ''),
                'source': item.get('source', ''),
                'pubdate': item.get('pubdate', ''),
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
            })
            
        return {"articles": articles}

    except Exception as e:
        return {"error": str(e), "query": query, "note": "PubMed unreachable"}

def main():
    """
    Input: JSON string list of queries from command line args.
    Output: JSON string of aggregated results.
    """
    # Fix for Windows Unicode output issue
    sys.stdout.reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print(json.dumps({"error": "No queries provided"}))
        sys.exit(1)

    try:
        # Handle potential single quotes wrapper from some shells
        input_str = sys.argv[1].strip()
        if input_str.startswith("'") and input_str.endswith("'"):
            input_str = input_str[1:-1]
            
        queries = json.loads(input_str)
    except json.JSONDecodeError:
        # Fallback: treat as a single query string if not valid JSON
        queries = [sys.argv[1].strip("'").strip('"')]

    results = {
        "clinical_trials": [],
        "pubmed": [],
        "meta": {
            "sources": ["clinicaltrials.gov", "pubmed"],
            "queries_processed": len(queries)
        }
    }

    # Print to stderr to avoid polluting stdout json output
    print(f"Starting search for {len(queries)} queries...", file=sys.stderr)

    for q in queries:
        # ClinicalTrials.gov
        ct_data = search_clinical_trials(q)
        results["clinical_trials"].append({
            "query": q,
            "data": ct_data
        })
        
        # PubMed
        pm_data = search_pubmed(q)
        results["pubmed"].append({
            "query": q,
            "data": pm_data
        })

    # Output results to stdout for the Agent to capture
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
