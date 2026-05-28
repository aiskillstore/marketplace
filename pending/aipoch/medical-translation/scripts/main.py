#!/usr/bin/env python3
"""Medical terminology translation script
Support translation of Chinese-English, Chinese-Spanish and other medical terms"""

import sys

def translate_medical_term(term, source_lang, target_lang, context=None):
    """Translate medical terms
    
    Args:
        term: the term to be translated
        source_lang: source language
        target_lang: target language
        context: context (optional)
    
    Returns:
        dict: contains translation results and metadata"""
    # Dictionary of Common Medical Terms
    cn_to_en = {
        "acute myeloid leukemia": "Acute Myeloid Leukemia (AML)",
        "hypertension": "Hypertension",
        "diabetes": "Diabetes Mellitus",
        "myocardial infarction": "Myocardial Infarction (MI)",
        "cerebral infarction": "Cerebral Infarction",
        "tumor": "Tumor / Neoplasm",
        "Chemotherapy": "Chemotherapy",
        "radiotherapy": "Radiotherapy",
        "Immunotherapy": "Immunotherapy",
        "targeted therapy": "Targeted Therapy",
    }
    
    en_to_cn = {v.split(" (")[0] if "(" in v else v: k for k, v in cn_to_en.items()}
    
    result = {
        "original": term,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "translated": None,
        "notes": []
    }
    
    if source_lang == "Chinese" and target_lang == "English":
        result["translated"] = cn_to_en.get(term, f"[Requires manual confirmation] {term}")
        if term not in cn_to_en:
            result["notes"].append("The term is not in the standard dictionary, please review")
    elif source_lang == "English" and target_lang == "Chinese":
        result["translated"] = en_to_cn.get(term, f"[Requires manual confirmation] {term}")
        if term not in en_to_cn:
            result["notes"].append("The term is not in the standard dictionary, please review")
    else:
        result["translated"] = f"[Not supported yet] {source_lang} -> {target_lang}"
        result["notes"].append("Currently only supports Chinese-English translation")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <term> <source_lang> <target_lang>")
        sys.exit(1)
    
    term = sys.argv[1]
    source_lang = sys.argv[2]
    target_lang = sys.argv[3]
    
    result = translate_medical_term(term, source_lang, target_lang)
    print(f"original: {result['original']}")
    print(f"translation: {result['translated']}")
    if result['notes']:
        print(f"Remark: {'; '.join(result['notes'])}")
