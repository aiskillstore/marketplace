import json
import re
import math
from collections import Counter
import string
import requests
from typing import Dict, List, Union, Any

def search_pubmed(query: str, max_results: int = 50, email: str = "tool@example.com") -> Dict[str, Any]:
    """
    Searches PubMed using official API and retrieves article details including MeSH terms.
    Returns format compatible with word_frequency and match_keywords.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # 1. ESearch
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "usehistory": "y",
        "email": email,
        "retmode": "json",
        "sort": "relevance"
    }
    
    try:
        resp = requests.get(f"{base_url}/esearch.fcgi", params=search_params, timeout=30)
        resp.raise_for_status()
        search_data = resp.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return {"total": 0, "documents": [], "medline_texts": []}
            
        # 2. EFetch (get MEDLINE format)
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "rettype": "medline",
            "retmode": "text",
            "email": email
        }
        
        resp = requests.get(f"{base_url}/efetch.fcgi", params=fetch_params, timeout=30)
        resp.raise_for_status()
        medline_text = resp.text
        
        # Parse MEDLINE text
        documents = []
        medline_texts = []
        
        current_doc = {}
        current_text = []
        
        for line in medline_text.splitlines():
            if not line.strip():
                if current_doc:
                    current_doc["full_text"] = "\n".join(current_text)
                    documents.append(current_doc)
                    medline_texts.append("\n".join(current_text))
                    current_doc = {}
                    current_text = []
                continue
                
            current_text.append(line)
            
            if line.startswith("PMID- "):
                current_doc["PMID"] = line[6:].strip()
            elif line.startswith("MH  - "):
                if "MH" not in current_doc:
                    current_doc["MH"] = []
                current_doc["MH"].append(line[6:].strip())
            elif line.startswith("PMC - "):
                current_doc["pmc"] = line[6:].strip()
            
        if current_doc:
            current_doc["full_text"] = "\n".join(current_text)
            documents.append(current_doc)
            medline_texts.append("\n".join(current_text))
            
        return {
            "total": len(documents),
            "documents": documents,
            "medline_texts": medline_texts
        }
        
    except Exception as e:
        return {"error": f"PubMed API Error: {str(e)}"}

def extract_pmid_range(json_str: str) -> Dict[str, Any]:
    """
    Parses search result JSON, limits total to 999, and generates pagination ranges.
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return {"result": 0, "total_range": [], "error": "Invalid JSON"}

    total = data.get("total", 0)
    if total > 1000:
        if "documents" in data:
            data["documents"] = data["documents"][:999]
        total = 999
        data["total"] = 999
    
    new_arg1 = json.dumps(data, ensure_ascii=False)
    
    result_list = []
    step = 100
    num = (total + step - 1) // step
    result_list = [str(i + 1) for i in range(min(num, 10))]
    
    return {
        "result": total,
        "total_range": result_list,
        "new_arg1": new_arg1
    }

def word_frequency(text_list: List[str]) -> Dict[str, str]:
    """
    Calculates frequency of MESH terms from a list of text entries.
    Returns top 20% frequent terms.
    """
    if not text_list:
        return {"result": ""}
        
    # Merge input
    text = "\n".join(text_list)
    processed_text = re.sub(r'\n\s+', ' ', text)
    
    # Find MH entries
    mh_entries = re.findall(r'^MH\s+-\s+(.+)', processed_text, re.MULTILINE)
    
    word_counter = Counter()
    
    for entry in mh_entries:
        cleaned_entry = entry.replace('*', '')
        tokens = re.split(r'[,/]', cleaned_entry)
        
        for token in tokens:
            token = token.strip()
            token = token.translate(str.maketrans('', '', string.punctuation))
            
            if not token or token.isdigit():
                continue
                
            term = token.lower()
            word_counter.update([term])
            
    sorted_freq = sorted(word_counter.items(), key=lambda item: item[1], reverse=True)
    
    total_unique = len(sorted_freq)
    top_n = math.ceil(total_unique * 0.2)
    top_freq = sorted_freq[:top_n]
    
    formatted_result = '\n'.join([f"{word}: {freq}" for word, freq in top_freq])
    
    return {"result": formatted_result}

def match_keywords(topics_str: str, pmid_data: Union[str, List]) -> Dict[str, str]:
    """
    Matches keywords from topics to PMIDs.
    """
    # Parse topics
    topics = []
    current_topic_num = None
    current_keywords = []
    
    lines = topics_str.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith("# topic_num:"):
            current_topic_num = line.split(":", 1)[1].strip()
        elif line.startswith("-keywords:"):
            kw_str = line.split(":", 1)[1].strip()
            current_keywords = [k.strip() for k in kw_str.split(",")]
            if current_topic_num:
                topics.append({"topic_num": current_topic_num, "keywords": current_keywords})
                current_topic_num = None
                current_keywords = []

    # Parse PMIDs
    if isinstance(pmid_data, str):
        try:
            records = json.loads(pmid_data)
        except:
            records = []
    else:
        records = pmid_data
        
    if not isinstance(records, list):
        return {"result": "Error: Invalid PMID data"}
        
    result_list = []
    
    for topic in topics:
        topic_num = topic.get("topic_num", "")
        keywords = topic.get("keywords", [])
        matches = {kw: [] for kw in keywords}
        
        for kw in keywords:
            kw_lower = kw.lower()
            for record in records:
                pmid = record.get("PMID", "")
                mh_terms = record.get("MH", [])
                
                for mh in mh_terms:
                    if kw_lower in mh.lower():
                        if pmid not in matches[kw]:
                            matches[kw].append(pmid)
                        break
            
            # Limit PMIDs per topic
            total_pmids = sum(len(pmids) for pmids in matches.values())
            if total_pmids >= 100:
                break
                
        result_list.append({"topic_num": topic_num, "matches": matches})
        
    # Format Markdown
    md_output = ""
    for topic in result_list:
        md_output += f"# Topic {topic['topic_num']}\n\n### Keywords and Matches:\n\n"
        for kw, pmids in topic['matches'].items():
            md_output += f"- **{kw}**:\n"
            if pmids:
                for pmid in pmids:
                    md_output += f"  - {pmid}\n"
            else:
                md_output += "  - None\n"
            md_output += "\n"
        md_output += "\n"
        
    return {"result": md_output}

def sort_by_jif_and_select(json_text: Union[str, Dict], index: int = 0) -> Dict[str, Any]:
    """
    Sorts articles and selects API key.
    Modified to handle PubMed API output (no JIF available).
    """
    try:
        if isinstance(json_text, str):
            data = json.loads(json_text)
        else:
            data = json_text
    except:
        return {"error": "Invalid JSON"}
        
    result = []
    documents = data.get("documents", [])
    
    # Process documents
    pmc_list = []
    none_list = []
    
    for doc in documents:
        pmid = doc.get("PMID", "")
        pmc = doc.get("pmc", "None")
        # JIF is not available in standard PubMed API, so we default to 0
        jif = doc.get("jif", "0") 
        
        entry = f"{pmid}-{pmc}-{jif}"
        
        if pmc != "None":
            pmc_list.append(entry)
        else:
            none_list.append(entry)
            
    # Since we don't have JIF, we just keep the order (relevance) or prioritize PMC availability
    # Current logic prioritizes PMC availability
    
    top20_pmc = pmc_list[:20]
    if len(top20_pmc) < 20:
        remaining = 20 - len(top20_pmc)
        top20_pmc.extend(none_list[:remaining])
        
    top20_pmcid_list = [item.split('-')[1] for item in top20_pmc if len(item.split('-')) > 1 and item.split('-')[1] != 'None']
    top20_pmcid = ",".join(top20_pmcid_list)
    
    # API Key rotation logic from original
    api_keys = ["e76024dbcecbf7ed987ab5c27cd5bed73e09","4a0cf12cdb32e8458d42ed2fc6fd22b3b909", "7a07e1951cfa0f0f5ff7ce951d0f0bea3d09", "edb6171f18c4d2e23692e0f2b9dedaf34208"]
    select_api = api_keys[index % len(api_keys)]
    
    return {
        "none_list": none_list,
        "top20_pmc": top20_pmc,
        "top20_pmcid": top20_pmcid,
        "select_api": select_api
    }
