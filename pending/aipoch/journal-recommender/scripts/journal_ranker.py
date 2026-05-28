import re

def rank_journals_by_if(journals_text: str, top_k: int = 5) -> str:
    """Parses journal text containing 'impact factor', sorts by IF descending, and returns top_k.
    Expected format: "## Journal Name ... Impact Factor: 10.5 ...""""
    blocks = re.split(r'(?=## )', journals_text)
    
    journal_data = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        match = re.search('Impact factor[^\\\\d]*([\\\\d.]+)', block)
        if match:
            try:
                if_val = float(match.group(1))
            except ValueError:
                if_val = 0.0
        else:
            if_val = 0.0
        
        journal_data.append((if_val, block))
    
    journal_data.sort(key=lambda x: x[0], reverse=True)
    top_journals = journal_data[:top_k]
    result_texts = [text for _, text in top_journals]
    return "\n\n".join(result_texts) if result_texts else "No valid journals found."

def rank_similar_papers(text: str, top_k: int = 3) -> str:
    """
    Parses text with PMID, similarities, and score, then ranks by score.
    Expected format: "PMID：12345 similarities：... score：5"
    """
    matches = re.findall(
        r"PMID：\\s*(\\d+)\\s*similarities：\\s*((?:.|\\n)*?)\\s*score：\\s*(\\d+)", 
        text
    )
    
    top_papers = sorted(
        [(pmid, similarities.strip(), int(score)) for pmid, similarities, score in matches],
        key=lambda x: x[2], 
        reverse=True
    )[:top_k]
    
    result = "\n".join(
        f"{i}. PMID：{pmid}\n    similarities：{similarities}\n    https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        for i, (pmid, similarities, score) in enumerate(top_papers, 1)
    )
    return result
