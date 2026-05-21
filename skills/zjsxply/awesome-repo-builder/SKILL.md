---
name: awesome-repo-builder
description: Create a topic-specific GitHub awesome-list repository scaffold with a polished README, concise contribution rules, AI-agent instructions, URL verification, license, and reusable templates. Use when the user wants to generate a new awesome repo, awesome list, curated repository, or topic resource catalog from a topic plus optional taxonomy, inclusion criteria, and researched entries.
---

# Awesome Repo Builder

Build a new awesome-list repository with a polished `README.md`, concise contribution rules, AI-agent instructions, URL verification script, license, `.gitignore`, and optional reusable templates.

## Required Inputs

Ask only for missing essentials.

- Topic: required. Example: "future event prediction", "AI coding harnesses", "LLM time-series forecasting".
- Taxonomy: recommended. If absent, propose one before generating.
- Inclusion criteria: recommended. If absent, draft concise criteria and exclusions.
- Initial entries: optional. The user may provide an already researched awesome list; otherwise research enough seed entries before generating.
- Output directory: optional. If absent, create a local folder named from the repo slug.

## Workflow

1. Inspect the user's requested topic and decide whether enough taxonomy and criteria exist.
2. If initial entries are absent, research the topic first. Prefer official project pages, papers, docs, GitHub repositories, and existing awesome lists. Keep the first generated repo useful but not exhaustive.
3. Create a JSON spec with `title`, `slug`, `topic`, `tagline`, `description`, `taxonomy`, `criteria`, `initial_entries`, and `related_lists`.
4. Run `scripts/create_awesome_repo.py` with the spec and output directory.
5. Read the generated files and make small manual edits if the topic requires wording changes.
6. Report the output path and any assumptions, especially taxonomy or criteria that were inferred.

## Scaffold Command

Use the bundled script from the skill directory:

```bash
python scripts/create_awesome_repo.py --spec /path/to/spec.json --output /path/to/awesome-topic
```

If the current project uses a Python virtual environment, activate it first. The script only uses the Python standard library.

## Spec Format

Minimum:

```json
{
  "title": "Awesome Future Event Prediction",
  "slug": "awesome-future-event-prediction",
  "topic": "future event prediction",
  "tagline": "Curated resources for future event prediction.",
  "description": "A curated list of papers, benchmarks, tools, and systems for forecasting discrete future events.",
  "taxonomy": [
    {
      "name": "Foundations",
      "description": "Conceptual and survey resources.",
      "entries": [
        {
          "title": "A Survey on Event Prediction Methods from a Systems Perspective",
          "url": "https://arxiv.org/abs/2302.04018",
          "note": "A systems view of event prediction that helps define scope and common failure modes."
        }
      ]
    }
  ],
  "criteria": {
    "belongs": [
      "Addresses prediction of discrete future events.",
      "Provides a reusable method, benchmark, dataset, tool, or system insight."
    ],
    "excludes": [
      "General AI papers without an event-forecasting angle.",
      "Pure time-series forecasting resources with no event-level relevance."
    ]
  },
  "related_lists": []
}
```

Notes:

- `taxonomy[].entries` may be empty; the script will create a placeholder.
- `taxonomy[].subsections` is supported for nested sections.
- `initial_entries` is also supported as a mapping from section name to entries when entries are collected separately.
- Entry format uses title, URL, and a short note explaining why the resource is worth including.

## Generated Structure

The script creates:

```text
awesome-topic/
├── .gitignore
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── verify_urls.py
└── templates/
    ├── AGENTS.md
    ├── CHECKLIST.md
    ├── IMPLEMENT.md
    └── PLAN.md
```

Keep the generated repository focused on initial structure and seed content. Do not add PR automation, batch review workflows, entry sorting policy, scheduled cleanup, or long maintenance process unless the user explicitly asks for it.

## Reference

Read `references/awesome-repo-structure.md` when you need the detailed structural pattern for generated repositories.
