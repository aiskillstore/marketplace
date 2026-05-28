import requests
import urllib.parse

class OpenAlexClient:
    """
    Client for OpenAlex API.
    """
    BASE_URL = "https://api.openalex.org"

    def __init__(self, email=None):
        self.headers = {}
        if email:
            self.headers["User-Agent"] = f"mailto:{email}"

    def search_works(self, search, filter_params=None, per_page=25):
        """
        Search for works in OpenAlex.
        
        Args:
            search (str): The search query.
            filter_params (dict): Dictionary of filters (e.g., {"is_oa": "true"}).
            per_page (int): Number of results per page.
            
        Returns:
            list: List of work objects.
        """
        url = f"{self.BASE_URL}/works"
        params = {
            "search": search,
            "per_page": per_page
        }
        if filter_params:
            # filters are formatted as key:value,key:value
            filter_str = ",".join([f"{k}:{v}" for k, v in filter_params.items()])
            params["filter"] = filter_str
            
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json().get("results", [])

    def search_authors(self, search):
        """Search for authors."""
        url = f"{self.BASE_URL}/authors"
        params = {"search": search}
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json().get("results", [])

    def search_institutions(self, search):
        """Search for institutions."""
        url = f"{self.BASE_URL}/institutions"
        params = {"search": search}
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json().get("results", [])

    def search_concepts(self, search):
        """Search for concepts."""
        url = f"{self.BASE_URL}/concepts"
        params = {"search": search}
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json().get("results", [])

if __name__ == "__main__":
    # Test execution
    print("Testing OpenAlexClient...")
    client = OpenAlexClient(email="test@example.com")
    try:
        results = client.search_works("machine learning", {"is_oa": "true"}, per_page=5)
        print(f"Success: Retrieved {len(results)} works.")
    except Exception as e:
        print(f"Error: {e}")
