---
name: citation-chasing-mapping
description: Use when identifying seminal papers in a research field, mapping research lineage and intellectual heritage, discovering related work through reference tracking, or finding potential collaborators through co-citation analysis. Maps citation networks to trace research evolution, identify influential papers, and discover hidden connections in scientific literature. Supports systematic reviews, bibliometric analysis, and research planning through comprehensive citation tracking.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Scientific Citation Network and Knowledge Mapper

## When to Use

- Use this skill when the task needs Use when identifying seminal papers in a research field, mapping research lineage and intellectual heritage, discovering related work through reference tracking, or finding potential collaborators through co-citation analysis. Maps citation networks to trace research evolution, identify influential papers, and discover hidden connections in scientific literature. Supports systematic reviews, bibliometric analysis, and research planning through comprehensive citation tracking.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when identifying seminal papers in a research field, mapping research lineage and intellectual heritage, discovering related work through reference tracking, or finding potential collaborators through co-citation analysis. Maps citation networks to trace research evolution, identify influential papers, and discover hidden connections in scientific literature. Supports systematic reviews, bibliometric analysis, and research planning through comprehensive citation tracking.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Evidence Insight/citation-chasing-mapping"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## When to Use This Skill

- identifying seminal papers in a research field
- mapping research lineage and intellectual heritage
- discovering related work through reference tracking
- finding potential collaborators through co-citation analysis
- tracking citation patterns to identify research trends
- building literature reviews with comprehensive coverage

## Quick Start

```python
from scripts.main import CitationChasingMapping

# Initialize the tool
tool = CitationChasingMapping()

from scripts.citation_mapper import CitationNetworkMapper

mapper = CitationNetworkMapper(data_source="PubMed")

# Build citation network from seed paper
network = mapper.build_network(
    seed_paper={
        "pmid": "12345678",
        "title": "Breakthrough Discovery in Immunotherapy"
    },
    backward_depth=2,  # references of references
    forward_depth=2,   # citing papers of citing papers
    max_papers=500
)

# Identify seminal papers
seminal_papers = mapper.identify_seminal_works(
    network=network,
    min_citations=100,
    centrality_threshold=0.8
)

print(f"Found {len(seminal_papers)} highly influential papers:")
for paper in seminal_papers[:5]:
    print(f"  - {paper.title} (cited {paper.citation_count} times)")

# Find research clusters
clusters = mapper.identify_research_clusters(
    network=network,
    algorithm="louvain",
    min_cluster_size=10
)

# Generate collaboration map
collaboration_map = mapper.generate_collaboration_network(
    network=network,
    institution_field="affiliation"
)

# Create visualization
mapper.visualize_network(
    network=network,
    layout="force_directed",
    color_by="publication_year",
    size_by="citation_count",
    output_file="citation_network.pdf"
)
```

## Core Capabilities

### 1. Build Comprehensive Citation Networks

Construct bidirectional citation graphs from seed papers with configurable depth.

```python

# Build network from multiple seed papers
network = mapper.build_network(
    seed_papers=[
        {"pmid": "12345678", "title": "Original Discovery"},
        {"pmid": "87654321", "title": "Follow-up Study"}
    ],
    backward_depth=3,  # References
    forward_depth=2,   # Citing papers
    max_papers=1000,
    include_citations=True
)

# Export network for Gephi
mapper.export_network(network, format="gexf", file="network.gexf")
```

### 2. Identify Seminal Works

Use centrality metrics to find field-defining papers.

```python

# Calculate centrality metrics
centrality = mapper.calculate_centrality(
    network=network,
    metrics=["betweenness", "eigenvector", "pagerank"]
)

# Identify seminal papers
seminal = mapper.identify_seminal_works(
    centrality=centrality,
    min_citations=100,
    top_n=20
)

for paper in seminal:
    print(f"{paper.title}: {paper.centrality_score}")
```

### 3. Discover Research Clusters

Detect communities and emerging research topics.

```python

# Detect research clusters
clusters = mapper.detect_clusters(
    network=network,
    algorithm="louvain",
    resolution=1.0
)

# Analyze cluster topics
for cluster_id, cluster in clusters.items():
    topic = mapper.extract_cluster_topic(cluster)
    print(f"Cluster {cluster_id}: {topic}")
    print(f"  Size: {cluster.size} papers")
    print(f"  Growth rate: {cluster.growth_rate}")
```

### 4. Generate Interactive Visualizations

Create publication-ready network visualizations.

```python

# Create interactive visualization
viz = mapper.visualize(
    network=network,
    layout="force_directed",
    node_color="publication_year",
    node_size="citation_count",
    edge_color="citation_type",
    interactive=True
)

# Save as HTML for web
viz.save_html("citation_network.html")

# Save static for publication
viz.save_pdf("figure_1.pdf", dpi=300)
```

## Command Line Usage

```text
python scripts/main.py --seed-pmid 12345678 --depth 2 --max-papers 500 --output network.json --visualize
```

## Best Practices

- Start with high-quality seed papers
- Set reasonable depth limits to avoid noise
- Validate key papers through multiple sources
- Update networks regularly as literature evolves

## Quality Checklist

Before using this skill, ensure you have:
- [ ] Clear understanding of your objectives
- [ ] Necessary input data prepared and validated
- [ ] Output requirements defined
- [ ] Reviewed relevant documentation

After using this skill, verify:
- [ ] Results meet your quality standards
- [ ] Outputs are properly formatted
- [ ] Any errors or warnings have been addressed
- [ ] Results are documented appropriately

## References

- `references/guide.md` - Comprehensive user guide
- `references/examples/` - Working code examples
- `references/api-docs/` - Complete API documentation

---

**Skill ID**: 193 | **Version**: 1.0 | **License**: MIT

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `citation-chasing-mapping` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `citation-chasing-mapping` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References

- [references/audit-reference.md](references/audit-reference.md) - Supported scope, audit commands, and fallback boundaries

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
