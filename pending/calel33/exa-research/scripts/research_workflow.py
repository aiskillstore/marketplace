#!/usr/bin/env python3
"""
Automated Research Workflows for Exa Tools

This script provides automated multi-step research workflows that combine
web search and code context retrieval for comprehensive research.

Usage:
    python research_workflow.py technology <technology-name>
    python research_workflow.py implementation <framework> <feature>
    python research_workflow.py comparison <solution-a> <solution-b>
    python research_workflow.py discovery <category>

Examples:
    python research_workflow.py technology "Next.js 15"
    python research_workflow.py implementation "React" "authentication"
    python research_workflow.py comparison "Cursor" "GitHub Copilot"
    python research_workflow.py discovery "AI coding tools"
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import exa tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from servers.exa import exa_web_search, exa_get_code_context


async def technology_research(technology: str):
    """
    Comprehensive research workflow for a technology/framework/tool.
    
    Steps:
    1. Get overview and features
    2. Find code examples
    3. Get latest updates
    """
    print(f"\n{'='*60}")
    print(f"TECHNOLOGY RESEARCH: {technology}")
    print(f"{'='*60}\n")
    
    # Step 1: Overview
    print("Step 1/3: Getting overview and features...")
    overview = await exa_web_search(
        query=f"{technology} overview features comparison",
        numResults=10,
        type="deep"
    )
    print(f"✓ Found {len(overview.split())} words of overview content\n")
    
    # Step 2: Code examples
    print("Step 2/3: Finding code examples...")
    examples = await exa_get_code_context(
        query=f"{technology} getting started examples",
        tokensNum=5000
    )
    print(f"✓ Retrieved code examples\n")
    
    # Step 3: Latest updates
    print("Step 3/3: Getting latest updates...")
    latest = await exa_web_search(
        query=f"{technology} latest updates 2025",
        numResults=5,
        livecrawl="preferred"
    )
    print(f"✓ Found latest updates\n")
    
    return {
        "overview": overview,
        "examples": examples,
        "latest": latest
    }


async def implementation_research(framework: str, feature: str):
    """
    Research workflow for implementing a specific feature.
    
    Steps:
    1. Find implementation guides
    2. Get working code examples
    """
    print(f"\n{'='*60}")
    print(f"IMPLEMENTATION RESEARCH: {feature} in {framework}")
    print(f"{'='*60}\n")
    
    # Step 1: Implementation guides
    print("Step 1/2: Finding implementation guides...")
    guides = await exa_web_search(
        query=f"how to implement {feature} in {framework}",
        numResults=8,
        type="deep"
    )
    print(f"✓ Found implementation guides\n")
    
    # Step 2: Code examples
    print("Step 2/2: Getting working code examples...")
    code = await exa_get_code_context(
        query=f"{framework} {feature} implementation examples",
        tokensNum=8000
    )
    print(f"✓ Retrieved code examples\n")
    
    return {
        "guides": guides,
        "code": code
    }


async def comparison_research(solution_a: str, solution_b: str):
    """
    Research workflow for comparing two solutions.
    
    Steps:
    1. Find comparison articles
    2. Get code examples for solution A
    3. Get code examples for solution B
    """
    print(f"\n{'='*60}")
    print(f"COMPARISON RESEARCH: {solution_a} vs {solution_b}")
    print(f"{'='*60}\n")
    
    # Step 1: Comparisons
    print("Step 1/3: Finding comparison articles...")
    comparisons = await exa_web_search(
        query=f"{solution_a} vs {solution_b} comparison 2025",
        numResults=15,
        type="deep"
    )
    print(f"✓ Found comparison articles\n")
    
    # Step 2: Solution A examples
    print(f"Step 2/3: Getting {solution_a} code examples...")
    solution_a_code = await exa_get_code_context(
        query=f"{solution_a} best practices examples",
        tokensNum=5000
    )
    print(f"✓ Retrieved {solution_a} examples\n")
    
    # Step 3: Solution B examples
    print(f"Step 3/3: Getting {solution_b} code examples...")
    solution_b_code = await exa_get_code_context(
        query=f"{solution_b} best practices examples",
        tokensNum=5000
    )
    print(f"✓ Retrieved {solution_b} examples\n")
    
    return {
        "comparisons": comparisons,
        "solution_a_code": solution_a_code,
        "solution_b_code": solution_b_code
    }


async def discovery_research(category: str):
    """
    Research workflow for discovering new tools/trends.
    
    Steps:
    1. Find latest tools in category
    2. Get implementation examples
    """
    print(f"\n{'='*60}")
    print(f"DISCOVERY RESEARCH: {category}")
    print(f"{'='*60}\n")
    
    # Step 1: Latest tools
    print("Step 1/2: Discovering latest tools...")
    tools = await exa_web_search(
        query=f"latest {category} 2025",
        numResults=20,
        type="deep",
        livecrawl="preferred"
    )
    print(f"✓ Found latest tools\n")
    
    # Step 2: Implementation examples
    print("Step 2/2: Getting implementation examples...")
    implementation = await exa_get_code_context(
        query=f"{category} setup and usage examples",
        tokensNum=5000
    )
    print(f"✓ Retrieved implementation examples\n")
    
    return {
        "tools": tools,
        "implementation": implementation
    }


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    workflow_type = sys.argv[1].lower()
    
    try:
        if workflow_type == "technology":
            if len(sys.argv) < 3:
                print("Error: Technology name required")
                print("Usage: python research_workflow.py technology <technology-name>")
                sys.exit(1)
            technology = " ".join(sys.argv[2:])
            results = await technology_research(technology)
            
        elif workflow_type == "implementation":
            if len(sys.argv) < 4:
                print("Error: Framework and feature required")
                print("Usage: python research_workflow.py implementation <framework> <feature>")
                sys.exit(1)
            framework = sys.argv[2]
            feature = " ".join(sys.argv[3:])
            results = await implementation_research(framework, feature)
            
        elif workflow_type == "comparison":
            if len(sys.argv) < 4:
                print("Error: Two solutions required")
                print("Usage: python research_workflow.py comparison <solution-a> <solution-b>")
                sys.exit(1)
            solution_a = sys.argv[2]
            solution_b = " ".join(sys.argv[3:])
            results = await comparison_research(solution_a, solution_b)
            
        elif workflow_type == "discovery":
            if len(sys.argv) < 3:
                print("Error: Category required")
                print("Usage: python research_workflow.py discovery <category>")
                sys.exit(1)
            category = " ".join(sys.argv[2:])
            results = await discovery_research(category)
            
        else:
            print(f"Error: Unknown workflow type '{workflow_type}'")
            print(__doc__)
            sys.exit(1)
        
        print(f"\n{'='*60}")
        print("RESEARCH COMPLETE!")
        print(f"{'='*60}\n")
        print("Results available in the 'results' dictionary")
        print(f"Keys: {list(results.keys())}")
        
    except Exception as e:
        print(f"\n❌ Error during research: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

