import argparse
import arxiv
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Search ArXiv and optionally download papers.")
    parser.add_argument("--query", required=True, help="Search query (e.g. 'quantum', 'cat:cs.AI')")
    parser.add_argument("--max-results", type=int, default=10, help="Max number of results")
    parser.add_argument("--sort-by", choices=["Relevance", "LastUpdatedDate", "SubmittedDate"], default="Relevance", help="Sort criterion")
    parser.add_argument("--download", action="store_true", help="Download PDFs of found papers")
    parser.add_argument("--dir", default=".", help="Directory to save downloads")

    args = parser.parse_args()

    sort_map = {
        "Relevance": arxiv.SortCriterion.Relevance,
        "LastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
        "SubmittedDate": arxiv.SortCriterion.SubmittedDate
    }

    print(f"Searching for: {args.query}")
    
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=args.query,
            max_results=args.max_results,
            sort_by=sort_map[args.sort_by]
        )

        results = list(client.results(search))

        if not results:
            print("No results found.")
            return

        print(f"Found {len(results)} papers:")
        print("-" * 40)

        for r in results:
            print(f"Title: {r.title}")
            print(f"Authors: {', '.join([a.name for a in r.authors])}")
            print(f"Date: {r.published.date()}")
            print(f"PDF URL: {r.pdf_url}")
            print(f"Summary: {r.summary[:200]}...")
            print("-" * 40)

            if args.download:
                if not os.path.exists(args.dir):
                    os.makedirs(args.dir)
                filename = r.download_pdf(dirpath=args.dir)
                print(f"Downloaded: {filename}")
                print("-" * 40)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
