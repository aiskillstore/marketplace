"""
Reference insertion module.
Extracts PMIDs from the article, retrieves citation formats using the PubMed API, 
replaces in-text citations, and generates a reference list.
"""

import re
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional


# PubMed E-utilities base URL
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def split_article(article: str) -> Tuple[str, str, str]:
    """
    Splits the article into three parts: Abstract/Introduction, Methods/Results, and Discussion.

    Args:
        article: Complete article text.

    Returns:
        (part1, part2, part3) The three parts of the content.
    """
    def find_first(text, *substrings):
        indices = [text.find(s) for s in substrings]
        valid = [i for i in indices if i != -1]
        return min(valid) if valid else -1

    methods_idx = find_first(article, "## Materials and Methods", "## Materials and Methods", "## Methods", "## Methods")
    discussion_idx = find_first(article, "## Discussion", "## Discussion")

    part1, part2, part3 = "", "", ""

    if methods_idx != -1:
        part1 = article[:methods_idx].strip()
        if discussion_idx != -1:
            part2 = article[methods_idx:discussion_idx].strip()
            part3 = article[discussion_idx:].strip()
        else:
            part2 = article[methods_idx:].strip()
    elif discussion_idx != -1:
        part1 = article[:discussion_idx].strip()
        part3 = article[discussion_idx:].strip()
    else:
        part1 = article.strip()

    return part1, part2, part3


def extract_pmids(content: str) -> Tuple[List[int], int]:
    """
    Extracts PMIDs and the count of square bracket citations from the content.

    Args:
        content: Article content.

    Returns:
        (list of PMIDs, count of square bracket citations)
    """
    pmid_pattern = r'[\[\【]PMID:\s*(\d+)[\]\】]'
    pmids = re.findall(pmid_pattern, content)

    # Deduplicate while preserving order
    seen = set()
    unique_pmids = []
    for pmid in pmids:
        if pmid not in seen:
            seen.add(pmid)
            unique_pmids.append(int(pmid))

    # Count square bracket numeric citations
    brackets = re.findall(r'\[(\d+)\]', content)
    bracket_count = len(brackets)

    return unique_pmids, bracket_count


def fetch_citations_from_pubmed(pmids: List[int]) -> Dict[str, Dict]:
    """
    Retrieves citation formats for PMIDs using the PubMed efetch API.

    Args:
        pmids: List of PMIDs.

    Returns:
        Mapping of PMIDs to citation information.
    """
    if not pmids:
        return {}

    pmid_str = ','.join(map(str, pmids))
    params = {
        'db': 'pubmed',
        'id': pmid_str,
        'retmode': 'xml'
    }

    url = f"{EUTILS_BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            xml_content = response.read().decode('utf-8')
            return parse_citations_xml(xml_content)
    except Exception as e:
        print(f"Failed to fetch citation format: {e}")
        return {}


def parse_citations_xml(xml_content: str) -> Dict[str, Dict]:
    """
    Parses the PubMed XML response and generates AMA-style citations.

    Args:
        xml_content: XML string.

    Returns:
        Mapping of PMIDs to citation information.
    """
    results = {}
    try:
        root = ET.fromstring(xml_content)
        for article in root.findall('.//PubmedArticle'):
            # PMID
            pmid_elem = article.find('.//PMID')
            if pmid_elem is None:
                continue
            pmid = pmid_elem.text

            # Authors
            authors = []
            for author in article.findall('.//Author'):
                lastname = author.find('LastName')
                initials = author.find('Initials')
                if lastname is not None:
                    name = lastname.text
                    if initials is not None:
                        name += ' ' + initials.text
                    authors.append(name)

            # Format author list
            if len(authors) <= 3:
                authors_str = ', '.join(authors)
            elif len(authors) <= 6:
                authors_str = ', '.join(authors)
            else:
                authors_str = ', '.join(authors[:3]) + ', et al'

            # Title
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else ''

            # Journal abbreviation
            journal_elem = article.find('.//ISOAbbreviation')
            if journal_elem is None:
                journal_elem = article.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else ''

            # Year
            year_elem = article.find('.//PubDate/Year')
            year = year_elem.text if year_elem is not None else ''

            # Volume/Issue/Pages
            volume_elem = article.find('.//Volume')
            issue_elem = article.find('.//Issue')
            pages_elem = article.find('.//MedlinePgn')

            volume = volume_elem.text if volume_elem is not None else ''
            issue = issue_elem.text if issue_elem is not None else ''
            pages = pages_elem.text if pages_elem is not None else ''

            # Build AMA format citation
            citation_parts = [authors_str + '.', title]
            citation_parts.append(f"{journal}.")
            if year:
                citation_parts.append(f"{year};")
            if volume:
                vol_str = volume
                if issue:
                    vol_str += f"({issue})"
                if pages:
                    vol_str += f":{pages}"
                citation_parts.append(vol_str + ".")

            citation = ' '.join(citation_parts)

            results[pmid] = {
                'pmid': pmid,
                'citation': citation,
                'authors': authors_str,
                'title': title,
                'journal': journal,
                'year': year
            }

    except ET.ParseError as e:
        print(f"XML parsing failed: {e}")

    return results


def replace_pmid_citations(content: str, pmid_to_citation: Dict, pmid_to_num: Dict) -> str:
    """
    Replaces [PMID: xxx] in the text with [[n]](link) format.

    Args:
        content: Article content.
        pmid_to_citation: Mapping of PMIDs to citation information.
        pmid_to_num: Mapping of PMIDs to numbers.

    Returns:
        The replaced content.
    """
    def replace_match(match):
        pmid = match.group(1)
        num = pmid_to_num.get(pmid)
        if num:
            return f'[[{num}]](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)'
        return match.group(0)

    return re.sub(r'[\[\【]PMID:\s*(\d+)[\]\】]', replace_match, content)


def reorder_numeric_brackets(content: str, offset: int) -> str:
    """
    Re-sequences numeric bracketed citations (excluding those already converted to links).

    Args:
        content: Article content.
        offset: Numbering offset.

    Returns:
        The re-numbered content.
    """
    def replace_numeric(match):
        num = int(match.group(1))
        return f'[{num + offset}]'

    # Use negative lookbehind to exclude citations already in Markdown link format [[n]](url)
    # Match standalone [digit], but not [[digit]] or [digit]( which is the link format
    return re.sub(r'(?<!\[)\[(\d+)\](?!\]|\()', replace_numeric, content)


def generate_reference_list(pmid_list: List[int], pmid_to_citation: Dict, pmid_to_num: Dict) -> str:
    """
    Generates the list of references.

    Args:
        pmid_list: List of PMIDs (in order).
        pmid_to_citation: Mapping of PMIDs to citation information.
        pmid_to_num: Mapping of PMIDs to numbers.

    Returns:
        Formatted reference list.
    """
    references = []
    for pmid in pmid_list:
        pmid_str = str(pmid)
        num = pmid_to_num.get(pmid_str, "?")
        citation_info = pmid_to_citation.get(pmid_str, {})
        citation = citation_info.get('citation', f'PMID: {pmid}')
        ref = f'[{num}] {citation} [https://pubmed.ncbi.nlm.nih.gov/{pmid}/]'
        references.append(ref)

    return '\n'.join(references)


def insert_references(article: str, new_references: str = "") -> str:
    """
    Complete reference insertion workflow.

    Args:
        article: Complete article text (containing [PMID: xxx] markers).
        new_references: Additional references to be inserted.

    Returns:
        Processed article (including the References section).
    """
    # 1. Split article
    part1, part2, part3 = split_article(article)

    # 2. Extract PMIDs from each part
    pmids1, bracket1 = extract_pmids(part1)
    pmids2, bracket2 = extract_pmids(part2)
    pmids3, bracket3 = extract_pmids(part3)

    # 3. Merge PMIDs (deduplicate while preserving order)
    seen = set()
    all_pmids = []
    for pmid in pmids1 + pmids2 + pmids3:
        if pmid not in seen:
            seen.add(pmid)
            all_pmids.append(pmid)

    # 4. Use PubMed API to fetch citation formats
    pmid_to_citation = fetch_citations_from_pubmed(all_pmids)

    # 5. Establish mapping from PMID to number
    pmid_to_num = {}
    for i, pmid in enumerate(all_pmids, 1):
        pmid_to_num[str(pmid)] = i

    # 6. Replace PMID citations in the text
    updated_article = replace_pmid_citations(article, pmid_to_citation, pmid_to_num)

    # 7. Reorder numeric bracketed citations
    total_pmids = len(all_pmids)
    updated_article = reorder_numeric_brackets(updated_article, total_pmids)

    # 8. Generate reference list
    ref_list = generate_reference_list(all_pmids, pmid_to_citation, pmid_to_num)

    # 9. Handle additional references
    if new_references.strip():
        new_refs_updated = reorder_numeric_brackets(new_references, total_pmids)
        ref_list = ref_list + '\n' + new_refs_updated

    # 10. Assemble final output
    result = f"{updated_article}\n\n## References\n\n{ref_list}"

    return result


if __name__ == "__main__":
    # Test example
    test_article = """
## Abstract
This is a test abstract.

## Introduction
Some introduction text [PMID: 38887558]. More text [PMID: 37654321].

## Discussion
Discussion content [PMID: 36543210].
"""
    print(insert_references(test_article))
