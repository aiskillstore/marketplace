import os
import json
from Bio import Entrez

def search_pubmed(query, max_results=5, email=None, api_key=None):
    """
    Search PubMed using NCBI Entrez API.
    
    Args:
        query (str): Search query string.
        max_results (int): Maximum number of results to return.
        email (str): User email (required by NCBI). Defaults to env var NCBI_EMAIL.
        api_key (str): NCBI API Key. Defaults to env var NCBI_API_KEY.
        
    Returns:
        list: A list of dictionaries containing title, abstract, and pmid.
    """
    
    # 1. Configuration
    Entrez.email = email or os.environ.get("NCBI_EMAIL", "your_email@example.com")
    Entrez.api_key = api_key or os.environ.get("NCBI_API_KEY")
    
    if Entrez.email == "your_email@example.com":
        print("Warning: Using default email. Please set NCBI_EMAIL environment variable.")

    try:
        # 2. ESearch: Get PMIDs
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record["IdList"]
        if not id_list:
            return []

        # 3. EFetch: Get Details
        ids = ",".join(id_list)
        handle = Entrez.efetch(
            db="pubmed",
            id=ids,
            retmode="xml"
        )
        records = Entrez.read(handle)
        handle.close()
        
        results = []
        # Entrez.read returns a list if multiple items, or dict/object if one. 
        # But for PubmedArticle it's usually a list inside the parsed object.
        articles = records['PubmedArticle']
        
        for article in articles:
            try:
                citation = article['MedlineCitation']
                article_data = citation['Article']
                
                # Extract Title
                title = article_data.get('ArticleTitle', 'No Title')
                
                # Extract Abstract
                abstract_text = ""
                if 'Abstract' in article_data:
                    abstract_parts = article_data['Abstract'].get('AbstractText', [])
                    # AbstractText can be a list of strings or objects
                    abstract_text = " ".join([str(x) for x in abstract_parts])
                
                # Extract PMID
                pmid = str(citation['PMID'])
                
                # Extract Journal info (optional but useful)
                journal = article_data.get('Journal', {}).get('Title', '')
                pub_date = article_data.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
                year = pub_date.get('Year', '')
                
                results.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract_text,
                    "journal": journal,
                    "year": year
                })
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
                
        return results

    except Exception as e:
        print(f"Error accessing NCBI API: {e}")
        return []

if __name__ == "__main__":
    # Test run
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "COVID-19"
    results = search_pubmed(query, max_results=3)
    print(json.dumps(results, indent=2, ensure_ascii=False))
