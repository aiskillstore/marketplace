import sys
import argparse
import json
import requests
import datetime
import time

# Ensure output is UTF-8 encoded, even on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # For older Python versions, though reconfigure is available in 3.7+
        pass

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search_pubmed(query, days=7, max_results=20):
    """
    Search PubMed for articles within the last N days matching the query.
    """
    # Calculate date range
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)
    date_str = f'"{start_date.strftime("%Y/%m/%d")}"[Date - Publication] : "{today.strftime("%Y/%m/%d")}"[Date - Publication]'
    
    # Construct term
    term = f"{query} AND {date_str}"
    
    # 1. eSearch
    search_url = f"{BASE_URL}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": max_results,
        "sort": "date"
    }
    
    try:
        response = requests.get(search_url, params=search_params)
        response.raise_for_status()
        search_data = response.json()
        
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return []
            
        ids_str = ",".join(id_list)
        
        # 2. eFetch (Get full details including abstract)
        import xml.etree.ElementTree as ET
        fetch_url = f"{BASE_URL}efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ids_str,
            "retmode": "xml"
        }
        
        response = requests.get(fetch_url, params=fetch_params)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        articles = []
        for article in root.findall(".//PubmedArticle"):
            pmid_node = article.find(".//PMID")
            pmid = pmid_node.text if pmid_node is not None else ""
            
            title_node = article.find(".//ArticleTitle")
            title = title_node.text if title_node is not None else "No Title"
            
            abstract_texts = article.findall(".//AbstractText")
            abstract = " ".join([t.text for t in abstract_texts if t.text])
            
            journal_node = article.find(".//Journal/Title")
            journal_title = journal_node.text if journal_node is not None else ""
            
            pubdate_node = article.find(".//PubDate/Year")
            date_str = pubdate_node.text if pubdate_node is not None else ""
            
            articles.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "journal": journal_title,
                "year": date_str
            })
            
        return articles

    except Exception as e:
        print(f"Error accessing PubMed API: {e}")
        return []

def classify_article_rule_based(title, abstract):
    """
    Classify article based on keywords in title and abstract.
    Returns: (category, topic_tag)
    """
    text = (title + " " + abstract).lower()
    
    # 1. Review & Survey
    if any(kw in text for kw in ["review", "meta-analysis", "systematic review", "perspective", "overview"]):
        return "Review & Survey", "Review"
        
    # 2. Methodology & Tools
    if any(kw in text for kw in ["algorithm", "software", "method", "technique", "framework", "tool", "pipeline", "database", "model"]):
        return "Methodology & Tools", "Methodology"
        
    # 3. Applied Research (Clinical/Practical)
    if any(kw in text for kw in ["clinical", "patient", "treatment", "efficacy", "application", "deployment", "trial", "diagnosis", "prognosis", "therapy"]):
        return "Applied Research", "Clinical/Applied"
        
    # 4. Fundamental Research (Mechanism/Basic)
    if any(kw in text for kw in ["mechanism", "novel", "discovery", "pathway", "theoretical", "fundamental", "characterization", "identification", "molecular"]):
        return "Fundamental Research", "Basic Science"
        
    # Default
    return "Other", "General"

def generate_markdown_report(keywords, articles):
    """
    Generate a Markdown report from the articles, matching the style of the original YAML output.
    """
    # Group by Category
    grouped = {
        "Fundamental Research": [],
        "Applied Research": [],
        "Methodology & Tools": [],
        "Review & Survey": [],
        "Other": []
    }
    
    for art in articles:
        cat, tag = classify_article_rule_based(art.get("title", ""), art.get("abstract", ""))
        art["category"] = cat
        art["topic"] = tag
        if cat in grouped:
            grouped[cat].append(art)
        else:
            grouped["Other"].append(art)
            
    # Generate Markdown matching the requested format (Headers + Numbered List)
    md = ""
    
    # Order of categories to display
    categories_order = ["Fundamental Research", "Applied Research", "Methodology & Tools", "Review & Survey", "Other"]
    
    for category in categories_order:
        items = grouped.get(category, [])
        if not items:
            continue
            
        md += f"## {category}\n"
        for i, item in enumerate(items, 1):
            title = item.get("title", "No Title")
            journal = item.get("journal", "Unknown Journal")
            abstract = item.get("abstract", "")
            # Truncate abstract for readability in the report
            summary = abstract[:300] + "..." if len(abstract) > 300 else abstract
            if not summary:
                summary = "No abstract available."
            
            # Format: 1. Title (Journal) \n Summary
            md += f"{i}. **{title}** ({journal})\n"
            md += f"   {summary}\n\n"
            
    return md

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search PubMed for recent articles.")
    parser.add_argument("--keywords", required=True, help="Search keywords")
    parser.add_argument("--days", type=int, default=7, help="Days to look back")
    parser.add_argument("--limit", type=int, default=20, help="Max results")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    results = search_pubmed(args.keywords, args.days, args.limit)
    
    if args.format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        report = generate_markdown_report(args.keywords, results)
        print(report)
