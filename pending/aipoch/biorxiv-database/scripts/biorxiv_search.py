import requests
import json
import datetime
import os
import sys

class BioRxivSearcher:
    """
    Client for interacting with bioRxiv API and content.
    """
    BASE_URL = "https://api.biorxiv.org/details/biorxiv"

    def __init__(self):
        pass

    def search_by_keywords(self, keywords, days_back=30):
        """
        Searches for papers containing specific keywords within a date range.
        
        Args:
            keywords (list): List of keyword strings.
            days_back (int): Number of days to look back.
            
        Returns:
            list: List of dictionary objects representing papers.
        """
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days_back)
        
        # Format: YYYY-MM-DD
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # API: https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{cursor}
        # Fetching first page (cursor=0)
        url = f"{self.BASE_URL}/{start_str}/{end_str}/0"
        print(f"Querying: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            papers = []
            if 'collection' in data:
                for item in data['collection']:
                    title = item.get('title', '').lower()
                    abstract = item.get('abstract', '').lower()
                    
                    # Check if ANY keyword is in title or abstract
                    match = False
                    for kw in keywords:
                        kw_lower = kw.lower()
                        if kw_lower in title or kw_lower in abstract:
                            match = True
                            break
                    
                    if match:
                        papers.append(item)
            
            return papers
            
        except Exception as e:
            print(f"Error fetching data: {e}", file=sys.stderr)
            return []

    def download_pdf(self, doi, filename):
        """
        Downloads PDF for a given DOI.
        
        Args:
            doi (str): Digital Object Identifier (e.g., 10.1101/2023.01.01.522123)
            filename (str): Local path to save the file.
        """
        # Construct URL: https://www.biorxiv.org/content/{doi}v1.full.pdf
        # Note: This assumes version 1. In production, might need to check latest version.
        url = f"https://www.biorxiv.org/content/{doi}v1.full.pdf"
        print(f"Downloading from: {url}")
        
        try:
            response = requests.get(url, stream=True, headers={'User-Agent': 'BioRxivSkill/1.0'})
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully saved to: {filename}")
            
        except Exception as e:
            print(f"Error downloading PDF: {e}", file=sys.stderr)

if __name__ == "__main__":
    # CLI Usage: python biorxiv_search.py [keyword] [days_back]
    if len(sys.argv) > 1:
        kw = [sys.argv[1]]
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        
        searcher = BioRxivSearcher()
        results = searcher.search_by_keywords(kw, days)
        print(json.dumps(results, indent=2))
    else:
        print("Usage: python biorxiv_search.py <keyword> [days_back]")
