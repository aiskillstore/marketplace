#!/usr/bin/env python3
"""
Test script for the Exa Research Skill

This script tests all the core capabilities of the exa-research skill
to ensure everything is working correctly.

Usage:
    python skills/exa-research/test_skill.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from servers.exa import exa_web_search, exa_get_code_context


async def test_web_search():
    """Test basic web search functionality."""
    print("\n" + "="*60)
    print("TEST 1: Web Search - Latest AI Tools")
    print("="*60)
    
    try:
        result = await exa_web_search(
            query="latest AI coding tools 2025",
            numResults=5,
            type="deep"
        )
        
        print(f"✅ Web search successful!")
        print(f"   Result length: {len(str(result))} characters")
        print(f"   Preview: {str(result)[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Web search failed: {e}")
        return False


async def test_code_search():
    """Test code context search functionality."""
    print("\n" + "="*60)
    print("TEST 2: Code Search - React Examples")
    print("="*60)
    
    try:
        result = await exa_get_code_context(
            query="React useState hook examples",
            tokensNum=3000
        )
        
        print(f"✅ Code search successful!")
        print(f"   Result length: {len(str(result))} characters")
        print(f"   Preview: {str(result)[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Code search failed: {e}")
        return False


async def test_combined_research():
    """Test combined web + code research workflow."""
    print("\n" + "="*60)
    print("TEST 3: Combined Research - Next.js Features")
    print("="*60)
    
    try:
        # Web search for overview
        print("   Step 1/2: Getting overview...")
        overview = await exa_web_search(
            query="Next.js 15 new features overview",
            numResults=5,
            type="deep"
        )
        print(f"   ✓ Overview retrieved ({len(str(overview))} chars)")
        
        # Code search for examples
        print("   Step 2/2: Getting code examples...")
        code = await exa_get_code_context(
            query="Next.js 15 server actions examples",
            tokensNum=5000
        )
        print(f"   ✓ Code examples retrieved ({len(str(code))} chars)")
        
        print(f"✅ Combined research successful!")
        return True
    except Exception as e:
        print(f"❌ Combined research failed: {e}")
        return False


async def test_advanced_search():
    """Test advanced search with all parameters."""
    print("\n" + "="*60)
    print("TEST 4: Advanced Search - Live Crawl")
    print("="*60)
    
    try:
        result = await exa_web_search(
            query="Svelte 5 runes latest updates 2025",
            numResults=8,
            type="deep",
            livecrawl="preferred",
            contextMaxCharacters=12000
        )
        
        print(f"✅ Advanced search successful!")
        print(f"   Result length: {len(str(result))} characters")
        return True
    except Exception as e:
        print(f"❌ Advanced search failed: {e}")
        return False


async def test_comparison_workflow():
    """Test comparison research workflow."""
    print("\n" + "="*60)
    print("TEST 5: Comparison Workflow - Frameworks")
    print("="*60)
    
    try:
        # Comparison search
        print("   Step 1/3: Finding comparisons...")
        comparison = await exa_web_search(
            query="React vs Vue comparison 2025",
            numResults=5,
            type="deep"
        )
        print(f"   ✓ Comparisons found ({len(str(comparison))} chars)")
        
        # React examples
        print("   Step 2/3: Getting React examples...")
        react_code = await exa_get_code_context(
            query="React best practices examples",
            tokensNum=3000
        )
        print(f"   ✓ React examples retrieved ({len(str(react_code))} chars)")
        
        # Vue examples
        print("   Step 3/3: Getting Vue examples...")
        vue_code = await exa_get_code_context(
            query="Vue composition API examples",
            tokensNum=3000
        )
        print(f"   ✓ Vue examples retrieved ({len(str(vue_code))} chars)")
        
        print(f"✅ Comparison workflow successful!")
        return True
    except Exception as e:
        print(f"❌ Comparison workflow failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("EXA RESEARCH SKILL - TEST SUITE")
    print("="*60)
    print("\nTesting all core capabilities of the exa-research skill...")
    
    results = []
    
    # Run all tests
    results.append(await test_web_search())
    results.append(await test_code_search())
    results.append(await test_combined_research())
    results.append(await test_advanced_search())
    results.append(await test_comparison_workflow())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! The exa-research skill is working perfectly!")
        print("\nNext steps:")
        print("1. Try the query optimizer: python skills/exa-research/scripts/query_optimizer.py analyze 'your query'")
        print("2. Try research workflows: python skills/exa-research/scripts/research_workflow.py technology 'Next.js'")
        print("3. Read SKILL.md for comprehensive documentation")
        print("4. Check references/ for advanced strategies")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

