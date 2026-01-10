# Exa Research Skill

A comprehensive research skill for AI agents using Exa AI's powerful search capabilities.

## Overview

This skill enables AI agents to conduct thorough research using two primary tools:
- **exa_web_search**: Real-time web search for articles, news, and documentation
- **exa_get_code_context**: Code search for examples, implementations, and technical documentation

## Installation

The Exa tools are already installed in the `servers/exa/` directory. Make sure you have:

1. Python 3.8+
2. Required packages (from project root):
   ```bash
   pip install -r requirements.txt
   ```
3. Exa API key in `.env` file:
   ```
   EXA_API_KEY=your_api_key_here
   ```

## Quick Start

### Basic Usage

```python
from servers.exa import exa_web_search, exa_get_code_context

# Web search
results = await exa_web_search("latest AI tools 2025", numResults=10)

# Code search
code = await exa_get_code_context("React useState examples", tokensNum=5000)
```

### Using Helper Scripts

#### Research Workflow Script

Automated multi-step research workflows:

```bash
# Technology research
python skills/exa-research/scripts/research_workflow.py technology "Next.js 15"

# Implementation research
python skills/exa-research/scripts/research_workflow.py implementation "React" "authentication"

# Comparison research
python skills/exa-research/scripts/research_workflow.py comparison "Cursor" "GitHub Copilot"

# Discovery research
python skills/exa-research/scripts/research_workflow.py discovery "AI coding tools"
```

#### Query Optimizer Script

Optimize your search queries:

```bash
# Optimize web search query
python skills/exa-research/scripts/query_optimizer.py web "AI tools"

# Optimize code search query
python skills/exa-research/scripts/query_optimizer.py code "authentication"

# Analyze query and get recommendations
python skills/exa-research/scripts/query_optimizer.py analyze "latest React features"
```

## Skill Structure

```
exa-research/
├── SKILL.md                          # Main skill documentation
├── README.md                         # This file
├── scripts/
│   ├── research_workflow.py          # Automated research workflows
│   └── query_optimizer.py            # Query optimization tool
└── references/
    ├── search_strategies.md          # Advanced search strategies
    └── query_patterns.md             # Effective query patterns
```

## Key Features

### Research Workflows

1. **Technology Research**: Comprehensive overview, examples, and latest updates
2. **Implementation Research**: Guides and working code examples
3. **Comparison Research**: Compare solutions with code examples
4. **Discovery Research**: Find latest tools and implementations

### Query Optimization

- Automatic query improvement suggestions
- Parameter recommendations
- Quality scoring
- Tool selection guidance

### Best Practices

- Progressive refinement strategies
- Multi-angle research approaches
- Temporal research patterns
- Validation techniques

## Documentation

- **SKILL.md**: Complete skill documentation with workflows and examples
- **search_strategies.md**: 8 advanced research strategies
- **query_patterns.md**: Proven query patterns for different scenarios

## Examples

### Example 1: Learning a New Framework

```python
# Get overview
overview = await exa_web_search(
    "Next.js 15 overview features",
    numResults=10,
    type="deep"
)

# Get starter code
starter = await exa_get_code_context(
    "Next.js 15 getting started tutorial",
    tokensNum=8000
)

# Find best practices
practices = await exa_web_search(
    "Next.js 15 best practices 2025",
    numResults=8
)
```

### Example 2: Solving a Problem

```python
# Search for solutions
solutions = await exa_web_search(
    "how to fix CORS errors in Next.js",
    numResults=10
)

# Get working code
code = await exa_get_code_context(
    "Next.js CORS fix examples",
    tokensNum=5000
)
```

### Example 3: Staying Current

```python
# Latest news
news = await exa_web_search(
    "latest AI coding tools 2025",
    numResults=15,
    livecrawl="preferred"
)

# New features code
features = await exa_get_code_context(
    "AI coding tools usage examples",
    tokensNum=5000
)
```

## Tips for AI Agents

When using this skill:

1. **Start with SKILL.md** for comprehensive guidance
2. **Use scripts/** for automated workflows
3. **Reference references/** for advanced strategies
4. **Combine both tools** for complete understanding
5. **Iterate queries** based on initial results
6. **Use deep search** for comprehensive research
7. **Include year** for latest information

## Contributing

To improve this skill:

1. Test workflows on real research tasks
2. Identify pain points or inefficiencies
3. Update SKILL.md or add new scripts
4. Document new patterns in references/

## License

This skill is part of the aitoolkit project.

## Support

For issues or questions:
1. Check SKILL.md for detailed documentation
2. Review references/ for advanced guidance
3. Test with query_optimizer.py for query improvements

