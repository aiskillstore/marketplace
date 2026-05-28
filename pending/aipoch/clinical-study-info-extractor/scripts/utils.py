import re
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

def normalize_pmids(pmid_input: str) -> list[str]:
    """
    Splits input string by newlines, spaces, commas, semicolons.
    Returns a list of non-empty cleaned PMIDs.
    """
    if not pmid_input:
        return []
    # Split by common separators: newline, space, comma (en/cn), semicolon (en/cn), comma
    parts = re.split(r'[\s,，;；、]+', pmid_input)
    return [p.strip() for p in parts if p.strip()]

def fetch_pubmed_data(pmids: list[str]) -> list[str]:
    """
    Fetches document details from PubMed API for the given PMIDs.
    Returns a list of JSON strings, where each string represents a document.
    """
    if not pmids:
        return []

    # Join PMIDs with comma
    id_string = ",".join(pmids)
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": id_string,
        "retmode": "xml"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
    except Exception as e:
        # Return a JSON string with error info if fetch fails, 
        # so the pipeline doesn't crash completely.
        return [json.dumps({"error": f"Failed to fetch data from PubMed: {str(e)}"}, ensure_ascii=False)]

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        return [json.dumps({"error": f"Failed to parse PubMed XML: {str(e)}"}, ensure_ascii=False)]

    documents = []
    
    # Iterate over PubmedArticle (and PubmedBookArticle if needed, but usually just Article)
    for article in root.findall(".//PubmedArticle"):
        doc_data = {}
        
        # 1. PMID
        pmid_node = article.find(".//PMID")
        doc_data["pmid"] = pmid_node.text if pmid_node is not None else ""

        medline = article.find(".//MedlineCitation")
        article_node = medline.find(".//Article") if medline is not None else None
        
        if article_node is not None:
            # 2. Title
            title_node = article_node.find("ArticleTitle")
            doc_data["title"] = "".join(title_node.itertext()) if title_node is not None else ""

            # 3. Journal Name
            journal_node = article_node.find("Journal")
            if journal_node is not None:
                j_title = journal_node.find("Title")
                doc_data["journal_name"] = j_title.text if j_title is not None else ""
                
                # 4. Pub Year
                pub_date = journal_node.find(".//PubDate")
                if pub_date is not None:
                    year = pub_date.find("Year")
                    if year is not None:
                        doc_data["pub_year"] = year.text
                    else:
                        medline_date = pub_date.find("MedlineDate")
                        doc_data["pub_year"] = medline_date.text if medline_date is not None else ""
            
            # 5. Abstract
            abstract_node = article_node.find("Abstract")
            if abstract_node is not None:
                abstract_texts = []
                for text_node in abstract_node.findall("AbstractText"):
                    label = text_node.get("Label")
                    text_content = "".join(text_node.itertext())
                    if label:
                        abstract_texts.append(f"{label}: {text_content}")
                    else:
                        abstract_texts.append(text_content)
                doc_data["abstracts"] = "\n".join(abstract_texts)
            else:
                doc_data["abstracts"] = ""

        # 6. DOI
        # Usually in PubmedData/ArticleIdList/ArticleId[@IdType="doi"]
        doi = ""
        pubmed_data = article.find(".//PubmedData")
        if pubmed_data is not None:
            for aid in pubmed_data.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text
                    break
        doc_data["doi"] = doi

        # Add Author List (Optional but useful for context)
        # Not strictly required by the output table but helps the LLM
        authors = []
        if article_node is not None:
            author_list = article_node.find("AuthorList")
            if author_list is not None:
                for author in author_list.findall("Author"):
                    lastname = author.find("LastName")
                    initials = author.find("Initials")
                    name = ""
                    if lastname is not None:
                        name += lastname.text
                    if initials is not None:
                        name += " " + initials.text
                    if name:
                        authors.append(name.strip())
        doc_data["authors"] = ", ".join(authors)

        documents.append(json.dumps(doc_data, ensure_ascii=False))

    return documents

def format_table(ai_outputs: list[str]) -> str:
    """
    Aggregates the LLM outputs (markdown table rows) into a final table with header.
    """
    header = "| pmid | title | year of publication | journal name | abstract | doi | article type | study population | sample size | intervention | findings | conclusion |"
    split_line = "|------|------|----------|----------|------|-----|----------|----------|--------|----------|----------|------|"
    
    # Filter empty lines
    rows = [item.strip() for item in ai_outputs if item.strip()]
    
    # Combine
    return "\n".join([header, split_line] + rows)

if __name__ == "__main__":
    # Simple test
    print("Testing normalize_pmids...")
    print(normalize_pmids("123, 456; 789\n101"))
