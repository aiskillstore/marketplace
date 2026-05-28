"""Reference search module
Extract keywords based on the topic, generate PubMed search terms, and call PubMed E-utilities API to obtain relevant literature"""

import re
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional


# PubMed E-utilities base URL
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def extract_keywords(theme: str, llm_func=None) -> List[str]:
    """Extract 3-5 keywords from the topic

    Args:
        theme: Retrieve theme
        llm_func: optional LLM function, used to intelligently extract keywords

    Returns:
        keyword list"""
    if llm_func:
        prompt = f"""
        Extract based on the following3-5keywords used to search references：
        {theme}

        Require：
        - Sort by importance
        - If the topic itself is a short title，available as a search phrase
        - Directly output keywords，separated by commas
        """
        result = llm_func(prompt)
        return [kw.strip() for kw in result.split(',')]
    else:
        # Simple extraction: split by sentence, take the first 5 non-empty phrases
        words = re.split(r'[,，;；\s]+', theme)
        return [w.strip() for w in words if w.strip()][:5]


def generate_search_query(keyword: str) -> str:
    """Generate PubMed search terms based on keywords

    Args:
        keyword: single keyword

    Returns:
        Search string"""
    # clean format
    query = re.sub(r'\[.*?\]', '', keyword)
    query = query.replace('/', ' ')
    query = query.replace('"', '"').replace('"', '"')
    return query.strip()


def search_pubmed_ids(query: str, max_results: int = 10, min_year: int = 2020) -> List[str]:
    """Get a list of PMIDs using PubMed esearch API search

    Args:
        query: search term
        max_results: Maximum number of returns
        min_year: earliest year

    Returns:
        PMID list"""
    params = {
        'db': 'pubmed',
        'term': f'{query} AND {min_year}:{2025}[dp]',
        'retmax': max_results,
        'retmode': 'json',
        'sort': 'relevance'
    }

    url = f"{EUTILS_BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('esearchresult', {}).get('idlist', [])
    except Exception as e:
        print(f"Search failed: {e}")
        return []


def fetch_pubmed_details(pmids: List[str]) -> List[Dict]:
    """Get document details using PubMed efetch API

    Args:
        pmids: PMID list

    Returns:
        Literature information list"""
    if not pmids:
        return []

    params = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'retmode': 'xml'
    }

    url = f"{EUTILS_BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            xml_content = response.read().decode('utf-8')
            return parse_pubmed_xml(xml_content)
    except Exception as e:
        print(f"Failed to get details: {e}")
        return []


def parse_pubmed_xml(xml_content: str) -> List[Dict]:
    """Parse PubMed XML response

    Args:
        xml_content: XML string

    Returns:
        Parsed document information list"""
    results = []
    try:
        root = ET.fromstring(xml_content)
        for article in root.findall('.//PubmedArticle'):
            info = {}

            # PMID
            pmid_elem = article.find('.//PMID')
            info['pmid'] = pmid_elem.text if pmid_elem is not None else ''

            # title
            title_elem = article.find('.//ArticleTitle')
            info['title'] = title_elem.text if title_elem is not None else ''

            # author
            authors = []
            for author in article.findall('.//Author'):
                lastname = author.find('LastName')
                forename = author.find('ForeName')
                if lastname is not None:
                    name = lastname.text
                    if forename is not None:
                        name += ' ' + forename.text
                    authors.append(name)
            info['authors'] = ', '.join(authors[:3])
            if len(authors) > 3:
                info['authors'] += ' et al.'

            # Journal
            journal_elem = article.find('.//Journal/Title')
            info['journal'] = journal_elem.text if journal_elem is not None else ''

            # years
            year_elem = article.find('.//PubDate/Year')
            info['year'] = year_elem.text if year_elem is not None else ''

            # summary
            abstract_parts = article.findall('.//AbstractText')
            abstract_texts = [p.text for p in abstract_parts if p.text]
            info['abstract'] = ' '.join(abstract_texts)

            results.append(info)
    except ET.ParseError as e:
        print(f"XMLParsing failed: {e}")

    return results


def format_reference(ref: Dict) -> str:
    """Format a single reference

    Args:
        ref: Document Information Dictionary

    Returns:
        Formatted reference string"""
    return f"PMID: {ref['pmid']} | {ref['authors']}. {ref['title']}. {ref['journal']}. {ref['year']}."


def search_pubmed(query: str, max_results: int = 10, min_year: int = 2020) -> str:
    """Complete PubMed search process

    Args:
        query: search term
        max_results: Maximum number of returns
        min_year: earliest year

    Returns:
        Formatted search results"""
    pmids = search_pubmed_ids(query, max_results, min_year)
    if not pmids:
        return ""

    details = fetch_pubmed_details(pmids)
    results = []
    for ref in details:
        results.append(format_reference(ref))

    return '\n'.join(results)


def search_references_for_theme(theme: str, llm_func=None) -> str:
    """Complete reference search process

    Args:
        theme: Retrieve theme
        llm_func: optional LLM function

    Returns:
        Combined search results"""
    keywords = extract_keywords(theme, llm_func)
    all_results = []

    for i, keyword in enumerate(keywords):
        query = generate_search_query(keyword)
        # The first keyword returns 15 articles, the second 10 articles, and the other 5 articles
        max_results = 15 if i == 0 else (10 if i == 1 else 5)
        result = search_pubmed(query, max_results)
        if result:
            all_results.append(f"=== keywords: {keyword} ===\n{result}")

    return '\n\n'.join(all_results)


if __name__ == "__main__":
    # Test example
    test_theme = "immune checkpoint inhibitor non-small cell lung cancer efficacy"
    print(search_references_for_theme(test_theme))
