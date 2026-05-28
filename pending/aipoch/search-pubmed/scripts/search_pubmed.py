import sys
import json
import urllib.request
import urllib.parse
import time

def search_pubmed(query):
    """
    Searches PubMed for the given query and returns the count and list of IDs.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": "5"
    }
    url = base_url + "?" + urllib.parse.urlencode(params)
    
    try:
        # User-Agent is required by NCBI
        req = urllib.request.Request(url, headers={'User-Agent': 'MetaTitleGeneratorSkill/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if "esearchresult" in data:
                count = int(data["esearchresult"]["count"])
                ids = data["esearchresult"]["idlist"]
                return count, ids
            return 0, []
    except Exception as e:
        # Silently fail on network error and return 0 results (fallback to creative generation)
        return 0, []

def fetch_summaries(ids):
    """
    Fetches summaries for the given list of PubMed IDs.
    """
    if not ids:
        return ""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json"
    }
    url = base_url + "?" + urllib.parse.urlencode(params)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MetaTitleGeneratorSkill/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            result = data.get("result", {})
            summaries = []
            for uid in ids:
                if uid in result:
                    item = result[uid]
                    title = item.get("title", "")
                    summaries.append(f"Title: {title}")
            return "\n".join(summaries)
    except Exception:
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # If no query provided, return 0 results
        print(json.dumps({"total": 0, "text": ""}))
        sys.exit(0)
    
    query = sys.argv[1]
    
    # Simple retry logic
    count = 0
    ids = []
    for _ in range(2):
        count, ids = search_pubmed(query)
        if count > 0 or ids:
            break
        time.sleep(1)
            
    text = ""
    if count > 0 and ids:
        text = fetch_summaries(ids)
    
    # Output JSON structure expected by the skill
    print(json.dumps({"total": count, "text": text}))
