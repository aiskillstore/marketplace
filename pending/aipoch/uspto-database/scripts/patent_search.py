import requests
import json

class PatentSearchClient:
    def __init__(self, api_key=None):
        self.base_url = "https://api.patentsview.org/patents/query"
        self.api_key = api_key

    def search_patents(self, query):
        """
        Search patents using PatentsView API query syntax.
        Example query: {"_text_all": {"patent_abstract": "AI"}}
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
            
        payload = {"q": query}
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test execution
    client = PatentSearchClient()
    print(client.search_patents({"_text_all": {"patent_abstract": "AI"}}))
