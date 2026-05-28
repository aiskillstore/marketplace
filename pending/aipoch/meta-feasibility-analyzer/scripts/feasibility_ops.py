import sys
import json
import re
import argparse
import os

try:
    from Bio import Entrez
except ImportError:
    Entrez = None

def search_pubmed(query, max_results=10, email=None, api_key=None):
    """
    Search PubMed using NCBI Entrez API.
    """
    if Entrez is None:
        return {"total": 0, "documents": [], "error": "BioPython not installed"}

    Entrez.email = email or os.environ.get("NCBI_EMAIL", "your_email@example.com")
    Entrez.api_key = api_key or os.environ.get("NCBI_API_KEY")

    try:
        # ESearch
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record["IdList"]
        total_count = int(record.get("Count", 0))
        
        if not id_list:
            return {"total": 0, "documents": []}

        # EFetch
        ids = ",".join(id_list)
        handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
        records = Entrez.read(handle)
        handle.close()
        
        results = []
        articles = records['PubmedArticle']
        
        for article in articles:
            try:
                citation = article['MedlineCitation']
                article_data = citation['Article']
                
                title = article_data.get('ArticleTitle', 'No Title')
                
                # Extract Year for date
                pub_date = article_data.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
                year = pub_date.get('Year', '')
                if not year and 'MedlineDate' in pub_date:
                     year = pub_date['MedlineDate']
                
                pmid = str(citation['PMID'])
                
                results.append({
                    "title": title,
                    "pubmed_date": year,
                    "pmid": pmid
                })
            except Exception:
                continue
                
        return {"total": len(results), "documents": results} # Use len(results) for retrieved count
    except Exception as e:
        return {"total": 0, "documents": [], "error": str(e)}

def extract_query(text):
    # Extracts content inside the last set of braces {}
    pattern = r'\{([^}]*)\}(?!.*\{)'
    matched_pattern = re.findall(pattern, text)
    if matched_pattern:
        final_output = matched_pattern[-1].replace("'", "").replace('"', "")
        # Remove square brackets content
        final_output = re.sub(r'\[.*?\]', '', final_output)
        return final_output.strip()
    return text.strip()

def format_clinical(json_str, query):
    try:
        data = json.loads(json_str)
        # Handle case where json_str is already a dict (if passed directly in python)
        if isinstance(json_str, dict):
            data = json_str
            
        total = int(data.get('total', 0))
        documents = data.get('documents', [])
    except Exception as e:
        return 0, "", f"Error parsing JSON: {str(e)}"
    
    res = ""
    for i, doc in enumerate(documents, 1):
        res += f"**Trial {i}**\nTitle: {doc.get('title')}\nDate: {doc.get('pubmed_date')}\n\n"
    
    summary = f"Query: {query}\nFound {total} clinical trials.\n{res}"
    return total, res, summary

def format_meta(json_str):
    try:
        data = json.loads(json_str)
        if isinstance(json_str, dict):
            data = json_str

        total = int(data.get('total', 0))
        documents = data.get('documents', [])
    except Exception as e:
        return 0, "", f"Error parsing JSON: {str(e)}"

    res = ""
    for i, doc in enumerate(documents, 1):
        res += f"**Meta {i}**\nTitle: {doc.get('title')}\nDate: {doc.get('pubmed_date')}\n\n"
    
    summary = f"Found {total} Meta-analyses.\n{res}" if total > 0 else "No Meta-analyses found."
    return total, res, summary

def main():
    parser = argparse.ArgumentParser(description="Ops for Meta Feasibility Analysis")
    parser.add_argument('mode', choices=['extract', 'clinical', 'meta', 'search'], help="Operation mode")
    parser.add_argument('--text', help='Input text for extraction')
    parser.add_argument('--json', help='JSON result string (search results)')
    parser.add_argument('--query', help='Query string', default="")
    parser.add_argument('--type', choices=['clinical', 'meta'], help='Search type')
    
    args = parser.parse_args()
    
    if args.mode == 'extract':
        if not args.text:
            print("Error: --text required for extract mode")
            sys.exit(1)
        print(extract_query(args.text))
        
    elif args.mode == 'search':
        if not args.query:
            print(json.dumps({"total": 0, "documents": [], "error": "--query required"}))
            sys.exit(1)
            
        full_query = args.query
        if args.type == 'clinical':
            full_query += " AND (Clinical Trial[ptyp] OR Randomized Controlled Trial[ptyp] OR Observational Study[ptyp])"
        elif args.type == 'meta':
            full_query += " AND (Meta-Analysis[ptyp])"
            
        result = search_pubmed(full_query, max_results=10)
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == 'clinical':
        if not args.json:
            print(json.dumps({'count': 0, 'summary': "Error: --json required"}))
            sys.exit(1)
        count, _, summary = format_clinical(args.json, args.query)
        print(json.dumps({'count': count, 'summary': summary}, ensure_ascii=False))
        
    elif args.mode == 'meta':
        if not args.json:
            print(json.dumps({'count': 0, 'summary': "Error: --json required"}))
            sys.exit(1)
        count, _, summary = format_meta(args.json)
        print(json.dumps({'count': count, 'summary': summary}, ensure_ascii=False))

if __name__ == '__main__':
    main()
