
def clean_text(text: str) -> str:
    """
    Cleans the input text by removing 'json', newlines, and code blocks.
    Mapped from YAML node 1735199479299.
    """
    if not text:
        return ""
    cleaned = text.replace('json', '').replace('\n', '').replace('```', '')
    return cleaned.strip()

def format_rob2_result(study_ref: str, domain_judgements: dict, overall: str) -> dict:
    """
    Formats the final ROB2 result into the expected JSON structure.
    """
    return {
        "Study": study_ref,
        "D1": domain_judgements.get("D1", "Some concerns"),
        "D2": domain_judgements.get("D2", "Some concerns"),
        "D3": domain_judgements.get("D3", "Some concerns"),
        "D4": domain_judgements.get("D4", "Some concerns"),
        "D5": domain_judgements.get("D5", "Some concerns"),
        "Overall": overall
    }
