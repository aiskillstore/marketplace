#!/usr/bin/env python3
"""Patent Search Tool - Multi-Platform Patent Search
Support: Google Patents, Lens.org, Dawei Innojoy, Baidu Academic, Espacenet"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============== Google Patents ==============
def search_google_patents(query: str, limit: int = 20, country: str = "CN") -> list[dict]:
    """Google Patents Search"""
    encoded_query = urllib.parse.quote(f"{query} country:{country}")
    url = f"https://patents.google.com/xhr/query?url=q%3D{encoded_query}&num={limit}&exp="
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        results = []
        if "results" in data and "cluster" in data["results"]:
            for cluster in data["results"]["cluster"]:
                if "result" in cluster:
                    for result in cluster["result"]:
                        patent = result.get("patent", {})
                        results.append({
                            "source": "Google Patents",
                            "patent_number": patent.get("publication_number", ""),
                            "title": patent.get("title", ""),
                            "abstract": patent.get("abstract", "")[:500] if patent.get("abstract") else "",
                            "assignee": patent.get("assignee", ""),
                            "filing_date": patent.get("filing_date", ""),
                            "url": f"https://patents.google.com/patent/{patent.get('publication_number', '')}"
                        })
        return results[:limit]
    except Exception as e:
        print(f"[Google Patents] Search failed: {e}", file=sys.stderr)
        return []


# ============== Lens.org ==============
def search_lens(query: str, limit: int = 20) -> list[dict]:
    """Lens.org search (patents + papers)"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.lens.org/lens/search/patent/list?q={encoded_query}&n={limit}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")
        
        # Simple parsing (Lens returns HTML)
        results = []
        # Regular rules for extracting patent information
        pattern = r'lens\.org/lens/patent/(\w+)'
        matches = re.findall(pattern, html)
        
        for lens_id in matches[:limit]:
            results.append({
                "source": "Lens.org",
                "patent_number": lens_id,
                "title": "[Requires access to details page]",
                "abstract": "",
                "url": f"https://www.lens.org/lens/patent/{lens_id}"
            })
        
        if not results:
            results.append({
                "source": "Lens.org",
                "note": "It is recommended to visit Lens.org directly to search",
                "url": f"https://www.lens.org/lens/search/patent/list?q={encoded_query}"
            })
        return results
    except Exception as e:
        print(f"[Lens.org] Search failed: {e}", file=sys.stderr)
        return [{
            "source": "Lens.org",
            "note": f"Search failed: {e}",
            "url": f"https://www.lens.org/lens/search/patent/list?q={encoded_query}"
        }]


# ============== Dawei Innojoy ==============
def search_innojoy(query: str, limit: int = 20) -> list[dict]:
    """Dawei Innojoy Patent Search"""
    encoded_query = urllib.parse.quote(query)
    # Innojoy simple search interface
    url = f"http://www.innojoy.com/search/index.html?kw={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")
        
        results = []
        # Try to parse the search results
        # Innojoy's results require JavaScript rendering, and the search link is returned here
        results.append({
            "source": "DaweiInnojoy",
            "note": "Innojoy requires browser access, a search link has been generated",
            "url": f"http://www.innojoy.com/search/index.html?kw={encoded_query}",
            "features": ["Mainly Chinese patents", "Support AI intelligent search", "Free basic version"]
        })
        return results
    except Exception as e:
        print(f"[Innojoy] Search failed: {e}", file=sys.stderr)
        return [{
            "source": "DaweiInnojoy",
            "note": f"Search failed，English",
            "url": f"http://www.innojoy.com/search/index.html?kw={encoded_query}"
        }]


# ============== Baidu Academic ==============
def search_baidu_xueshu(query: str, limit: int = 20) -> list[dict]:
    """Baidu academic search (papers + patents)"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://xueshu.baidu.com/s?wd={encoded_query}&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_hit=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")
        
        results = []
        # Analyzing Baidu Academic Results
        # title mode
        title_pattern = r'<a[^>]*class="sc_content"[^>]*>([^<]+)</a>'
        titles = re.findall(title_pattern, html)
        
        for title in titles[:limit]:
            results.append({
                "source": "Baidu Academic",
                "title": title.strip(),
                "url": f"https://xueshu.baidu.com/s?wd={encoded_query}"
            })
        
        if not results:
            results.append({
                "source": "Baidu Academic",
                "note": "It is recommended to directly visit Baidu Academic to search",
                "url": f"https://xueshu.baidu.com/s?wd={encoded_query}",
                "features": ["Mainly papers", "Partial patents", "Chinese friendly"]
            })
        return results
    except Exception as e:
        print(f"[English] Search failed: {e}", file=sys.stderr)
        return [{
            "source": "Baidu Academic",
            "note": f"Search failed，English",
            "url": f"https://xueshu.baidu.com/s?wd={encoded_query}"
        }]


# ============== Espacenet (European Patent Office) ==============
def search_espacenet(query: str, limit: int = 20) -> list[dict]:
    """Espacenet European Patent Office Search"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://worldwide.espacenet.com/patent/search?q={encoded_query}"
    
    # Espacenet has anti-crawling and returns to the search link
    return [{
        "source": "Espacenet",
        "note": "European Patent Office database, browser required to access",
        "url": url,
        "features": ["Global patents", "European patent details", "Support multiple languages"]
    }]


# ============== National Intellectual Property Administration CNIPA ==============
def search_cnipa(query: str, limit: int = 20) -> list[dict]:
    """National Intellectual Property Office patent search (login required)"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://pss-system.cponline.cnipa.gov.cn/conventionalSearch?searchWord={encoded_query}"
    
    return [{
        "source": "CNIPA",
        "note": "Official database of the National Intellectual Property Administration, requiring a login account",
        "url": url,
        "register_url": "https://pss-system.cponline.cnipa.gov.cn/",
        "features": ["China Patent Authority", "Legal status is accurate", "Need to register and log in"]
    }]


# ============== Similarity Analysis ==============
def analyze_similarity(query: str, patents: list[dict]) -> list[dict]:
    """Simple similarity analysis (based on keyword matching)"""
    keywords = set(query.lower().split())
    
    for patent in patents:
        if "note" in patent:
            continue
        title = patent.get("title", "").lower()
        abstract = patent.get("abstract", "").lower()
        content = f"{title} {abstract}"
        
        matched = sum(1 for kw in keywords if kw in content)
        patent["similarity_score"] = round(matched / len(keywords) * 100, 1) if keywords else 0
    
    return sorted(patents, key=lambda x: x.get("similarity_score", 0), reverse=True)


# ============== Output formatting ==============
def format_output(patents: list[dict], format_type: str = "text") -> str:
    """Formatted output"""
    if format_type == "json":
        return json.dumps(patents, ensure_ascii=False, indent=2)
    
    if not patents:
        return "No relevant patents found"
    
    lines = ["## Patent search results"]
    
    # Group by source
    sources = {}
    for p in patents:
        src = p.get("source", "unknown")
        if src not in sources:
            sources[src] = []
        sources[src].append(p)
    
    for source, items in sources.items():
        lines.append(f"### source: {source}\n")
        
        for i, p in enumerate(items, 1):
            if "note" in p:
                lines.append(f"**hint**: {p['note']}")
                if p.get("url"):
                    lines.append(f"Link: {p['url']}")
                if p.get("features"):
                    lines.append(f"Features: {', '.join(p['features'])}")
                lines.append("")
                continue
            
            lines.append(f"**{i}. {p.get('title', 'Untitled')}**")
            if p.get("patent_number"):
                lines.append(f"- Patent number: {p['patent_number']}")
            if p.get("assignee"):
                lines.append(f"- applicant: {p['assignee']}")
            if p.get("filing_date"):
                lines.append(f"- Application date: {p['filing_date']}")
            if "similarity_score" in p:
                lines.append(f"- Similarity: {p['similarity_score']}%")
            if p.get("url"):
                lines.append(f"- Link: {p['url']}")
            if p.get("abstract"):
                lines.append(f"- summary: {p['abstract'][:150]}...")
            lines.append("")
    
    return "\n".join(lines)


# ============== Main function ==============
def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Multi-platform patent search tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Data source description:
  google - Google Patents (global patents, free)
  lens - Lens.org (patent + paper, free)
  innojoy - Dawei Innojoy (Chinese patent, free basic version)
  baidu - Baidu Academic (papers + patents, free)
  espacenet - European Patent Office (global patents, free)
  cnipa - National Intellectual Property Administration (Chinese Patent, login required)
  all - all platforms

Example:
  python patent_search.py "artificial intelligence image recognition" -s all
  python patent_search.py "machine learning" -s google -c US -n 30
  python patent_search.py "deep learning" -s google,lens,innojoy -a"""
    )
    parser.add_argument("query", help="Search keywords")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Number of results returned by each platform")
    parser.add_argument("--country", "-c", default="CN", help="Country code (CN/US/EP/JP/KR)")
    parser.add_argument("--source", "-s", default="google",
                        help="Data sources, comma separated (google/lens/innojoy/baidu/espacenet/cnipa/all)")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="Output format")
    parser.add_argument("--analyze", "-a", action="store_true", help="Perform similarity analysis")
    parser.add_argument("--parallel", "-p", action="store_true", help="Parallel retrieval (faster)")
    
    args = parser.parse_args()
    
    # Parse data source
    if args.source == "all":
        sources = ["google", "lens", "innojoy", "baidu", "espacenet", "cnipa"]
    else:
        sources = [s.strip().lower() for s in args.source.split(",")]
    
    # Data source mapping
    search_funcs = {
        "google": lambda: search_google_patents(args.query, args.limit, args.country),
        "lens": lambda: search_lens(args.query, args.limit),
        "innojoy": lambda: search_innojoy(args.query, args.limit),
        "baidu": lambda: search_baidu_xueshu(args.query, args.limit),
        "espacenet": lambda: search_espacenet(args.query, args.limit),
        "cnipa": lambda: search_cnipa(args.query, args.limit),
    }
    
    all_results = []
    
    if args.parallel and len(sources) > 1:
        # Parallel search
        print(f"Parallel search {len(sources)} platforms...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            futures = {}
            for src in sources:
                if src in search_funcs:
                    futures[executor.submit(search_funcs[src])] = src
            
            for future in as_completed(futures):
                src = futures[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    print(f"[{src}] Finish，get {len(results)} results", file=sys.stderr)
                except Exception as e:
                    print(f"[{src}] fail: {e}", file=sys.stderr)
    else:
        # serial retrieval
        for src in sources:
            if src in search_funcs:
                print(f"Searching {src}: {args.query}", file=sys.stderr)
                results = search_funcs[src]()
                all_results.extend(results)
    
    # Similarity analysis
    if args.analyze and all_results:
        all_results = analyze_similarity(args.query, all_results)
    
    print(format_output(all_results, args.format))


if __name__ == "__main__":
    main()
