---
name: arxiv-search
description: Search arXiv preprint repository for papers in physics, mathematics, computer science, quantitative biology, and related fields.
---

# arXiv Search Skill

This skill provides access to arXiv, a free distribution service and open-access archive for scholarly articles in physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, systems science, and economics.

## When to Use This Skill

Use this skill when you need to:

- Find preprints and recent research papers before journal publication
- Search for papers in computational biology, bioinformatics, or systems biology
- Access mathematical or statistical methods papers relevant to biology
- Find machine learning papers applied to biological problems
- Get the latest research that may not yet be in PubMed

## Skill Scripts

### arxiv_search

The `arxiv_search` script accepts the following arguments:

- First argument (required): Search query string (e.g., "neural networks protein structure", "single cell RNA-seq")
- `--max-papers` (optional): Maximum number of papers to retrieve (default: 10)

### Usage Pattern

Use the `run_skill_script` tool to execute the `arxiv_search` script. For example:

```python
run_skill_script(
    skill_name="arxiv-search",
    script_name="arxiv_search",
    args=["your search query", "--max-papers", "5"]
)
```

Search for computational biology papers (default 10 results):

```python
run_skill_script(
    skill_name="arxiv-search",
    script_name="arxiv_search",
    args=["protein folding prediction"]
)
```

## Output Format

The script returns formatted results with:

- **Title**: Paper title
- **Summary**: Abstract/summary text
- **URL**: Direct link to the paper on arXiv

Each paper is separated by blank lines for readability.

## Features

- **Relevance sorting**: Results ordered by relevance to query
- **Fast retrieval**: Direct API access with no authentication required
- **Simple interface**: Clean, easy-to-parse output
- **No API key required**: Free access to arXiv database

## Dependencies

This skill requires the `arxiv` Python package. If not installed, you'll see an error message.

To install the package:

```bash
pip install arxiv
```

The package is not included by default since it's skill-specific. Install it when you first use this skill.

## Notes

- arXiv is particularly strong for:
  - Computer science (cs.LG, cs.AI, cs.CV)
  - Quantitative biology (q-bio)
  - Statistics (stat.ML)
  - Physics and mathematics
- Papers are preprints and may not be peer-reviewed
- Results include both recent uploads and older papers
- Best for computational/theoretical work in biology
