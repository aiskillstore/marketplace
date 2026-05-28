def assemble_article(title, preface, expert_intro, body, summary):
    """
    Helper function to assemble the final article structure.
    """
    article = []
    
    # Title
    article.append(f"# {title}\n")
    
    # Preface
    if preface:
        article.append("## Preface")
        article.append(preface + "\n")
    
    # Expert Introduction
    if expert_intro:
        article.append("## Expert introduction")
        article.append(expert_intro + "\n")
    
    # Body
    if body:
        article.append("## Interview text")
        article.append(body + "\n")
        
    # Summary
    if summary:
        article.append("## Full text summary")
        article.append(summary + "\n")
        
    return "\n".join(article)

if __name__ == "__main__":
    # Example usage for testing
    print(assemble_article(
        title="Test Title",
        preface="Test Preface",
        expert_intro="Test Intro",
        body="Test Body",
        summary="Test Summary"
    ))
