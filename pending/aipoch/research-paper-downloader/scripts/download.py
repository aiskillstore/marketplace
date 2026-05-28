#!/usr/bin/env python3
"""
Research Paper Downloader
Academic paper download from open access sources with security constraints.
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import quote_plus
import time
import re

CONFIG_FILE = Path(__file__).parent.parent / "config.json"


def load_config() -> Dict:
    """Load configuration from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "output_dir": str(Path.home() / "Downloads" / "ResearchPapers"),
        "timeout": 30,
        "max_retries": 3,
        "download_timeout": 120,
    }


def validate_output_path(path: Path) -> bool:
    """Validate that output path is within allowed directory"""
    config = load_config()
    allowed_dir = Path(config["output_dir"]).expanduser()
    try:
        path.resolve().relative_to(allowed_dir.resolve())
        return True
    except ValueError:
        return False


def clean_doi(doi: str) -> str:
    """Clean and validate DOI format"""
    doi = doi.strip()
    for prefix in ["doi:", "DOI:", "https://doi.org/", "http://doi.org/"]:
        if doi.lower().startswith(prefix.lower()):
            doi = doi[len(prefix) :]
    return doi.strip()


def clean_arxiv_id(arxiv_id: str) -> str:
    """Clean and validate arXiv ID format"""
    arxiv_id = arxiv_id.strip()
    for prefix in ["arxiv:", "arXiv:", "ARXIV:"]:
        if arxiv_id.lower().startswith(prefix.lower()):
            arxiv_id = arxiv_id[len(prefix) :]

    return arxiv_id.strip()


def download_by_doi(doi: str, output: Optional[str] = None) -> Optional[str]:
    """
    Download paper by DOI using priority-based sources.

    Args:
        doi: Paper DOI (with or without prefix)
        output: Output directory (uses config default if None)

    Returns:
        Path to downloaded file, or None if failed
    """
    config = load_config()
    output_dir = Path(output or config["output_dir"]).expanduser()

    if not validate_output_path(output_dir):
        print(f"Error: Output path not allowed: {output_dir}")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    doi = clean_doi(doi)

    print(f"Downloading DOI: {doi}")

    sources = [
        ("Semantic Scholar", lambda: _from_semantic_scholar(doi, output_dir)),
        ("Europe PMC", lambda: _from_europe_pmc(doi, output_dir)),
        ("OpenAlex", lambda: _from_openalex(doi, output_dir)),
        ("Unpaywall", lambda: _from_unpaywall(doi, output_dir)),
        ("arXiv", lambda: _from_arxiv_doi(doi, output_dir)),
        ("PubMed", lambda: _from_pubmed(doi, output_dir)),
        ("Crossref", lambda: _from_crossref(doi, output_dir)),
    ]

    for name, func in sources:
        try:
            print(f"  Trying {name}...")
            result = func()
            if result:
                return result
            time.sleep(2)
        except requests.exceptions.Timeout:
            print(f"  {name}: Timeout")
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"  {name}: Rate limited (429)")
            else:
                print(f"  {name}: Connection error")
        except Exception as e:
            print(f"  {name}: Error")

    print(f"\nFailed to download: {doi}")
    print(f"Alternative: Access paper directly at https://doi.org/{doi}")
    return None


def _from_semantic_scholar(doi: str, output_dir: Path, retry: int = 3) -> Optional[str]:
    """Download from Semantic Scholar API with retry"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors,openAccessPdf,year,doi"

    for attempt in range(retry):
        try:
            resp = requests.get(url, timeout=30)

            if resp.status_code == 429:
                wait_time = (attempt + 1) * 10
                print(f"  Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            resp.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            if attempt < retry - 1:
                time.sleep(5)
                continue
            raise

    data = resp.json()

    if not isinstance(data, dict):
        return None

    if (
        data.get("openAccessPdf")
        and isinstance(data["openAccessPdf"], dict)
        and data["openAccessPdf"].get("url")
    ):
        pdf_url = data["openAccessPdf"]["url"]
        filename = _generate_filename(data, output_dir, "pdf")
        return _download_file(pdf_url, output_dir / filename, timeout=120)

    return None


def _from_europe_pmc(doi: str, output_dir: Path) -> Optional[str]:
    """Download from Europe PMC"""
    search_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{quote_plus(doi)}&resulttype=lite"
    resp = requests.get(search_url, timeout=30)
    resp.raise_for_status()

    import xml.etree.ElementTree as ET

    root = ET.fromstring(resp.content)

    for result in root.findall(".//result"):
        doi_elem = result.find("doi")
        if doi_elem is not None and doi_elem.text == doi:
            pmcid = result.find("pmcid")
            if pmcid is not None:
                pmcid_val = pmcid.text
                pdf_url = f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid_val}&blobtype=pdf"
                filename = f"{pmcid_val.replace('PMC', 'JCO')}.pdf"
                return _download_file(pdf_url, output_dir / filename)

    return None


def _from_openalex(doi: str, output_dir: Path) -> Optional[str]:
    """Download from OpenAlex"""
    url = f"https://api.openalex.org/works/doi:{quote_plus(doi)}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    data = resp.json()

    if data.get("open_access", {}).get("is_oa"):
        for loc in data.get("locations", []):
            pdf_url = loc.get("url_for_pdf") or loc.get("url")
            if pdf_url:
                filename = _generate_filename(data, output_dir, "pdf")
                return _download_file(pdf_url, output_dir / filename)

    return None


def _from_unpaywall(doi: str, output_dir: Path) -> Optional[str]:
    """Download via Unpaywall"""
    url = f"https://api.unpaywall.org/v2/{quote_plus(doi)}?email=example@example.com"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    data = resp.json()

    location = data.get("best_oa_location")
    if location:
        pdf_url = location.get("url_for_pdf") or location.get("url")
        if pdf_url:
            filename = _generate_filename(data, output_dir, "pdf")
            return _download_file(pdf_url, output_dir / filename)

    return None


def _from_arxiv_doi(doi: str, output_dir: Path) -> Optional[str]:
    """Check if DOI is for arXiv paper"""
    if "arxiv" in doi.lower():
        arxiv_id = doi.split("arxiv.")[-1] if "arxiv." in doi else doi
        return download_by_arxiv(arxiv_id, str(output_dir))
    return None


def _from_pubmed(doi: str, output_dir: Path) -> Optional[str]:
    """PubMed - limited support"""
    url = f"https://pubmed.ncbi.nlm.nih.gov/?term={quote_plus(doi)}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return None


def _from_crossref(doi: str, output_dir: Path) -> Optional[str]:
    """Download from Crossref"""
    url = f"https://api.crossref.org/works/{quote_plus(doi)}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    data = resp.json().get("message", {})
    if data.get("link"):
        for link in data["link"]:
            if "PDF" in link.get("content-type", ""):
                filename = _generate_filename(data, output_dir, "pdf")
                return _download_file(link["URL"], output_dir / filename)

    return None


def download_by_arxiv(arxiv_id: str, output: Optional[str] = None) -> Optional[str]:
    """
    Download paper from arXiv by ID.

    Args:
        arxiv_id: arXiv identifier (e.g., "2310.12345" or "2310/12345")
        output: Output directory

    Returns:
        Path to downloaded file, or None if failed
    """
    config = load_config()
    output_dir = Path(output or config["output_dir"]).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    arxiv_id = clean_arxiv_id(arxiv_id)
    print(f"Downloading arXiv: {arxiv_id}")

    urls = [
        f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        f"https://ar5iv.org/pdf/{arxiv_id}.pdf",
    ]

    for url in urls:
        try:
            resp = requests.get(url, timeout=120, stream=True)
            resp.raise_for_status()

            content = resp.content
            if b"%PDF" in content[:100]:
                filename = f"{arxiv_id.replace('/', '_')}.pdf"
                filepath = output_dir / filename
                return _save_file(content, filepath)
        except requests.exceptions.RequestException:
            continue

    return None


def _save_file(content: bytes, filepath: Path) -> Optional[str]:
    """Save content to file with validation"""
    config = load_config()

    if not validate_output_path(filepath):
        print(f"Error: Invalid output path")
        return None

    try:
        if b"%PDF" not in content[:100]:
            print(f"Error: Not a valid PDF file")
            return None

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(content)

        print(f"[OK] {filepath.name}")
        return str(filepath)

    except Exception as e:
        print(f"Error saving file: {str(e)[:50]}")
        return None

    return None


def search_arxiv(query: str, max_results: int = 10) -> List[Dict]:
    """Search arXiv for papers"""
    url = f"http://export.arxiv.org/api/query?search_query=all:{quote_plus(query)}&max_results={max_results}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    from xml.etree import ElementTree as ET

    root = ET.fromstring(resp.content)

    papers = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        paper = {
            "id": entry.find("{http://www.w3.org/2005/Atom}id").text.split("/abs/")[-1],
            "title": entry.find("{http://www.w3.org/2005/Atom}title")
            .text.strip()
            .replace("\n", " "),
            "authors": [
                a.find("{http://www.w3.org/2005/Atom}name").text
                for a in entry.findall("{http://www.w3.org/2005/Atom}author")
            ],
            "pdf_url": None,
        }
        for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
            if link.get("title") == "pdf":
                paper["pdf_url"] = link.get("href")
                break
        papers.append(paper)

    return papers


def search_semantic_scholar(query: str, max_results: int = 10) -> List[Dict]:
    """Search Semantic Scholar"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote_plus(query)}&limit={max_results}&fields=title,authors,year,openAccessPdf,doi"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    return resp.json().get("data", [])


def search_download(
    query: str, max_results: int = 5, output: Optional[str] = None
) -> List[str]:
    """
    Search and download papers by keywords.

    Args:
        query: Search keywords
        max_results: Maximum papers to download
        output: Output directory

    Returns:
        List of downloaded file paths
    """
    config = load_config()
    output_dir = Path(output or config["output_dir"]).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded = []

    for paper in search_semantic_scholar(query, max_results):
        if paper.get("openAccessPdf") and isinstance(paper["openAccessPdf"], dict):
            try:
                pdf_url = paper["openAccessPdf"].get("url")
                if pdf_url:
                    filename = _generate_filename(paper, output_dir, "pdf")
                    result = _download_file(pdf_url, output_dir / filename)
                    if result:
                        downloaded.append(result)
            except Exception as e:
                print(f"  Skipping: {str(e)[:50]}")

    return downloaded


def _generate_filename(data: Dict, output_dir: Path, fmt: str = "pdf") -> str:
    """Generate safe filename from metadata"""
    config = load_config()
    max_len = config.get("security", {}).get("max_filename_length", 80)

    title = data.get("title", "untitled")
    if isinstance(title, dict):
        title = title.get("raw", "untitled")

    title = "".join(c for c in str(title) if c.isalnum() or c in " -_").strip()[
        : max_len - 50
    ]
    title = title.replace(" ", "_")

    year = str(data.get("year", "unknown"))

    author = "unknown"
    if data.get("authors") and len(data["authors"]) > 0:
        first_author = data["authors"][0]
        if isinstance(first_author, str):
            author = first_author.split()[-1] if " " in first_author else first_author
        elif isinstance(first_author, dict):
            author = first_author.get("name", "unknown").split()[-1]

    filename = f"{author}_{year}_{title}.{fmt}"
    return filename


def _download_file(url: str, filepath: Path, timeout: int = 60) -> Optional[str]:
    """
    Download file from URL with validation.

    Args:
        url: Source URL
        filepath: Destination path
        timeout: Download timeout in seconds

    Returns:
        Path to downloaded file, or None on failure
    """
    config = load_config()

    if not validate_output_path(filepath):
        print(f"Error: Invalid output path")
        return None

    try:
        resp = requests.get(url, timeout=timeout, stream=True)
        resp.raise_for_status()

        if b"%PDF" not in resp.content[:100]:
            print(f"Error: Not a valid PDF file")
            return None

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(resp.content)

        print(f"[OK] {filepath.name}")
        return str(filepath)

    except requests.exceptions.Timeout:
        print(f"Timeout downloading: {url[:50]}...")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {str(e)[:50]}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Research Paper Downloader - Academic paper download from open access sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --doi "10.1038/nature12345"
  %(prog)s --arxiv "2310.12345"
  %(prog)s --search "transformer attention" --max-results 5
        """,
    )
    parser.add_argument("--doi", help="Paper DOI (with or without prefix)")
    parser.add_argument("--arxiv", help="arXiv ID")
    parser.add_argument("--search", help="Search keywords")
    parser.add_argument(
        "--max-results", type=int, default=5, help="Max results for search"
    )
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--config", action="store_true", help="Show configuration")
    parser.add_argument(
        "--list-sources", action="store_true", help="List available sources"
    )

    args = parser.parse_args()

    if args.list_sources:
        print("Available sources:")
        print("  1. Semantic Scholar (api.semanticscholar.org)")
        print("  2. OpenAlex (api.openalex.org)")
        print("  3. Unpaywall (api.unpaywall.org)")
        print("  4. arXiv (arxiv.org)")
        print("  5. PubMed (ncbi.nlm.nih.gov)")
        print("  6. Crossref (api.crossref.org)")
        return

    if args.config:
        config = load_config()
        print(json.dumps(config, indent=2))
        return

    if args.doi:
        result = download_by_doi(args.doi, args.output)
        if result:
            print(f"Downloaded: {result}")
        else:
            print("Download failed. Paper may not have open access version.")
    elif args.arxiv:
        result = download_by_arxiv(args.arxiv, args.output)
        if result:
            print(f"Downloaded: {result}")
        else:
            print("Download failed.")
    elif args.search:
        results = search_download(args.search, args.max_results, args.output)
        print(f"Downloaded: {len(results)} paper(s)")
        for r in results:
            print(f"  {r}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
