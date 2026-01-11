#!/usr/bin/env python3
"""
Query Optimizer for Exa Research

This script helps optimize search queries for better results from Exa tools.
It provides suggestions and improvements for both web search and code search queries.

Usage:
    python query_optimizer.py web "<your query>"
    python query_optimizer.py code "<your query>"
    python query_optimizer.py analyze "<your query>"

Examples:
    python query_optimizer.py web "AI tools"
    python query_optimizer.py code "authentication"
    python query_optimizer.py analyze "latest React features"
"""

import sys
from typing import List, Dict


def optimize_web_query(query: str) -> Dict[str, any]:
    """
    Optimize a web search query and provide suggestions.
    
    Returns:
        Dictionary with optimized query and suggestions
    """
    suggestions = []
    optimized = query
    score = 0
    
    # Check for year/date
    has_year = any(year in query for year in ["2024", "2025", "2026"])
    if not has_year:
        suggestions.append("Add year for latest information (e.g., '2025')")
        optimized += " 2025"
    else:
        score += 20
    
    # Check for context words
    context_words = ["latest", "best", "comparison", "guide", "overview", "features"]
    has_context = any(word in query.lower() for word in context_words)
    if not has_context:
        suggestions.append("Add context words: 'latest', 'best', 'comparison', 'guide'")
        if "vs" not in query.lower():
            optimized = f"latest {optimized}"
    else:
        score += 20
    
    # Check query length
    word_count = len(query.split())
    if word_count < 2:
        suggestions.append("Query too short - add more specific terms")
        score -= 20
    elif word_count > 10:
        suggestions.append("Query might be too long - focus on key terms")
        score -= 10
    else:
        score += 20
    
    # Check for specific technology names
    generic_terms = ["tool", "software", "app", "program", "code"]
    is_generic = all(term in query.lower() for term in generic_terms if term in query.lower())
    if is_generic and word_count <= 2:
        suggestions.append("Be more specific - include technology/framework names")
        score -= 20
    else:
        score += 20
    
    # Check for comparison indicators
    if " vs " in query.lower() or " versus " in query.lower():
        score += 10
        if not has_year:
            optimized += " comparison 2025"
    
    return {
        "original": query,
        "optimized": optimized,
        "score": max(0, min(100, score + 40)),  # Normalize to 0-100
        "suggestions": suggestions,
        "recommended_params": {
            "numResults": 15 if word_count > 3 else 10,
            "type": "deep",
            "livecrawl": "preferred" if has_year or "latest" in query.lower() else "fallback"
        }
    }


def optimize_code_query(query: str) -> Dict[str, any]:
    """
    Optimize a code search query and provide suggestions.
    
    Returns:
        Dictionary with optimized query and suggestions
    """
    suggestions = []
    optimized = query
    score = 0
    
    # Check for framework/library name
    frameworks = [
        "react", "vue", "angular", "svelte", "next.js", "nuxt", "gatsby",
        "django", "flask", "fastapi", "express", "nest.js", "spring",
        "rails", "laravel", "asp.net", "typescript", "python", "javascript",
        "java", "c#", "go", "rust", "kotlin", "swift"
    ]
    has_framework = any(fw in query.lower() for fw in frameworks)
    if not has_framework:
        suggestions.append("Include framework/library name (e.g., 'React', 'Next.js', 'FastAPI')")
        score -= 30
    else:
        score += 30
    
    # Check for context words
    context_words = ["examples", "implementation", "setup", "configuration", "tutorial", "guide"]
    has_context = any(word in query.lower() for word in context_words)
    if not has_context:
        suggestions.append("Add context: 'examples', 'implementation', 'setup', 'tutorial'")
        optimized += " examples"
    else:
        score += 20
    
    # Check for specific feature/API
    is_specific = len(query.split()) >= 3
    if not is_specific:
        suggestions.append("Be more specific about the feature/API you want")
        score -= 20
    else:
        score += 20
    
    # Check for overly broad terms
    broad_terms = ["code", "programming", "development", "software"]
    is_broad = any(term == query.lower().strip() for term in broad_terms)
    if is_broad:
        suggestions.append("Query too broad - specify what you want to learn")
        score -= 40
    
    # Suggest token count based on query
    word_count = len(query.split())
    if word_count <= 3:
        token_suggestion = 3000
    elif word_count <= 5:
        token_suggestion = 5000
    else:
        token_suggestion = 8000
    
    return {
        "original": query,
        "optimized": optimized,
        "score": max(0, min(100, score + 50)),  # Normalize to 0-100
        "suggestions": suggestions,
        "recommended_params": {
            "tokensNum": token_suggestion
        }
    }


def analyze_query(query: str) -> Dict[str, any]:
    """
    Analyze a query and determine which tool is best suited.
    
    Returns:
        Dictionary with analysis and recommendations
    """
    # Indicators for web search
    web_indicators = [
        "latest", "news", "comparison", "vs", "versus", "overview",
        "best", "top", "trends", "2024", "2025", "2026"
    ]
    
    # Indicators for code search
    code_indicators = [
        "example", "implementation", "code", "how to", "tutorial",
        "setup", "configuration", "api", "function", "class", "hook"
    ]
    
    query_lower = query.lower()
    
    web_score = sum(1 for indicator in web_indicators if indicator in query_lower)
    code_score = sum(1 for indicator in code_indicators if indicator in query_lower)
    
    if web_score > code_score:
        recommended_tool = "exa_web_search"
        optimization = optimize_web_query(query)
    elif code_score > web_score:
        recommended_tool = "exa_get_code_context"
        optimization = optimize_code_query(query)
    else:
        recommended_tool = "both (start with web search)"
        optimization = {
            "web": optimize_web_query(query),
            "code": optimize_code_query(query)
        }
    
    return {
        "query": query,
        "recommended_tool": recommended_tool,
        "web_score": web_score,
        "code_score": code_score,
        "optimization": optimization
    }


def print_optimization_result(result: Dict):
    """Pretty print optimization results."""
    print(f"\n{'='*60}")
    print("QUERY OPTIMIZATION RESULTS")
    print(f"{'='*60}\n")
    
    if "recommended_tool" in result:
        # Analysis result
        print(f"Original Query: {result['query']}")
        print(f"Recommended Tool: {result['recommended_tool']}")
        print(f"Web Score: {result['web_score']}")
        print(f"Code Score: {result['code_score']}\n")
        
        if isinstance(result['optimization'], dict) and 'web' in result['optimization']:
            print("WEB SEARCH OPTIMIZATION:")
            print_single_optimization(result['optimization']['web'])
            print("\nCODE SEARCH OPTIMIZATION:")
            print_single_optimization(result['optimization']['code'])
        else:
            print_single_optimization(result['optimization'])
    else:
        # Single optimization result
        print_single_optimization(result)


def print_single_optimization(opt: Dict):
    """Print a single optimization result."""
    print(f"Original: {opt['original']}")
    print(f"Optimized: {opt['optimized']}")
    print(f"Quality Score: {opt['score']}/100")
    
    if opt['suggestions']:
        print("\nSuggestions:")
        for i, suggestion in enumerate(opt['suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    print("\nRecommended Parameters:")
    for key, value in opt['recommended_params'].items():
        print(f"  {key}: {value}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    query = " ".join(sys.argv[2:])
    
    if mode == "web":
        result = optimize_web_query(query)
    elif mode == "code":
        result = optimize_code_query(query)
    elif mode == "analyze":
        result = analyze_query(query)
    else:
        print(f"Error: Unknown mode '{mode}'")
        print(__doc__)
        sys.exit(1)
    
    print_optimization_result(result)


if __name__ == "__main__":
    main()

