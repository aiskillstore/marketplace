import os
import argparse
import json
from dotenv import load_dotenv
from tavily import TavilyClient

def search(query, search_depth, max_results):
    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print(json.dumps({"error": "TAVILY_API_KEY environment variable not set."}))
        exit(1)

    try:
        client = TavilyClient(api_key=api_key)
        results = client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results
        )
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tavily Search Skill")
    parser.add_argument("--query", required=True, help="The search query.")
    parser.add_argument("--search-depth", default="basic", choices=["basic", "advanced"], help="Search depth.")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results.")
    
    args = parser.parse_args()
    
    search(args.query, args.search_depth, args.max_results)
