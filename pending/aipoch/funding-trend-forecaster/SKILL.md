---
name: funding-trend-forecaster
description: Analyze funding abstracts and project metadata to identify topic shifts and forecast near-term grant priorities.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Skill: Funding Trend Forecaster

**ID:** 200  
**Version:** 1.0.0  
**Author:** OpenClaw Agent  
**License:** MIT

---

## When to Use

- Use this skill when the task is to Analyze funding abstracts and project metadata to identify topic shifts and forecast near-term grant priorities.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when the response must stay inside the documented task boundary instead of expanding into adjacent work.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Analyze funding abstracts and project metadata to identify topic shifts and forecast near-term grant priorities.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

```
requests>=2.28.0
beautifulsoup4>=4.11.0
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.1.0
textblob>=0.17.1
nltk>=3.7
matplotlib>=3.6.0
seaborn>=0.12.0
wordcloud>=1.8.0
python-dateutil>=2.8.0
```

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/funding-trend-forecaster"
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
python scripts/main.py --source nih --months 3
python scripts/main.py --forecast --years 3
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

Funding Trend Forecaster is an intelligent analysis tool that uses Natural Language Processing (NLP) technology to analyze awarded project abstracts from major global research funding agencies (NIH, NSF, Horizon Europe) and predict funding preference shift trends for the next 3-5 years.

## Features

- **Multi-source Data Collection**: Automatically fetches awarded project data from NIH, NSF, Horizon Europe
- **NLP Deep Analysis**: Uses advanced text mining techniques to extract topics, keywords, and research trends
- **Trend Prediction Model**: Predicts funding direction changes based on time series analysis and topic modeling
- **Visualized Reports**: Generates charts and trend reports for intuitive display of analysis results
- **Field Segmentation**: Categorized analysis by medicine, engineering, natural sciences, and other fields

## Installation

```text

# Enter skill directory
cd skills/funding-trend-forecaster

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

## Usage

### Command Line Interface

```text

# Run full analysis workflow
python scripts/main.py --analyze-all --output report.json

# Analyze specific agency only
python scripts/main.py --source nih --months 6

# Generate visualization report
python scripts/main.py --visualize --input data.json --output charts/

# View trend forecast
python scripts/main.py --forecast --years 5 --output forecast.json
```

### API Call

```python
from scripts.main import FundingTrendForecaster

# Initialize forecaster
forecaster = FundingTrendForecaster()

# Collect data
forecaster.collect_data(sources=['nih', 'nsf', 'horizon_europe'], months=6)

# Execute analysis
results = forecaster.analyze_trends()

# Generate forecast
forecast = forecaster.predict_trends(years=5)

# Export report
forecaster.export_report(output_path='report.pdf', format='pdf')
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--analyze-all` | flag | false | No | Run full analysis workflow on all sources |
| `--source` | string | - | No | Specific agency to analyze (nih, nsf, horizon_europe) |
| `--months` | int | 6 | No | Number of months of historical data to analyze |
| `--years` | int | 5 | No | Years ahead for trend prediction |
| `--visualize` | flag | false | No | Generate visualization charts |
| `--forecast` | flag | false | No | Generate trend forecast |
| `--input`, `-i` | string | - | No | Input data file path (for visualization/forecast) |
| `--output`, `-o` | string | - | No | Output file path |
| `--config` | string | config.json | No | Path to configuration file |

## Data Sources

| Agency | Data Source URL | Update Frequency |
|------|-----------|---------|
| NIH | https://reporter.nih.gov/ | Daily |
| NSF | https://www.nsf.gov/awardsearch/ | Daily |
| Horizon Europe | https://ec.europa.eu/info/funding-tenders/opportunities/ | Weekly |

## Configuration

Create `config.json` file to customize analysis parameters:

```json
{
  "sources": {
    "nih": {
      "enabled": true,
      "base_url": "https://reporter.nih.gov/",
      "max_results": 1000
    },
    "nsf": {
      "enabled": true,
      "base_url": "https://www.nsf.gov/awardsearch/",
      "max_results": 1000
    },
    "horizon_europe": {
      "enabled": true,
      "base_url": "https://ec.europa.eu/info/funding-tenders/",
      "max_results": 500
    }
  },
  "nlp": {
    "language": "en",
    "min_word_length": 3,
    "max_topics": 20,
    "stop_words": ["research", "study", "project"]
  },
  "forecast": {
    "method": "lda_trend",
    "confidence_level": 0.95,
    "years_ahead": 5
  }
}
```

## Output Format

### JSON Report Structure

```json
{
  "metadata": {
    "generated_at": "2024-01-15T10:30:00Z",
    "data_period": "2023-07-01 to 2024-01-01",
    "sources": ["nih", "nsf", "horizon_europe"],
    "total_projects": 15420
  },
  "trend_analysis": {
    "top_keywords": [
      {"term": "artificial intelligence", "frequency": 342, "growth": 0.45},
      {"term": "climate change", "frequency": 298, "growth": 0.32}
    ],
    "emerging_topics": [
      {"topic": "Large Language Models", "projects": 89, "trend": "rising"},
      {"topic": "Carbon Capture", "projects": 156, "trend": "stable"}
    ],
    "funding_shifts": {
      "increasing": ["AI/ML", "Climate Tech", "Quantum Computing"],
      "decreasing": ["Traditional Materials", "Fossil Fuels Research"]
    }
  },
  "forecast": {
    "2025": {
      "predicted_hot_topics": ["Generative AI", "Gene Editing", "Fusion Energy"],
      "confidence": 0.87
    },
    "2026-2029": {
      "long_term_trends": ["AGI Safety", "Personalized Medicine", "Space Mining"],
      "confidence": 0.72
    }
  }
}
```

## Architecture

```
funding-trend-forecaster/
├── scripts/
│   ├── main.py              # Main entry
│   ├── collectors/          # Data collection module
│   │   ├── __init__.py
│   │   ├── nih_collector.py
│   │   ├── nsf_collector.py
│   │   └── horizon_collector.py
│   ├── analyzers/           # NLP analysis module
│   │   ├── __init__.py
│   │   ├── text_processor.py
│   │   ├── topic_modeler.py
│   │   └── trend_detector.py
│   ├── predictors/          # Prediction module
│   │   ├── __init__.py
│   │   └── trend_forecaster.py
│   └── utils/               # Utility module
│       ├── __init__.py
│       ├── config.py
│       └── visualizer.py
├── data/                    # Data storage
│   ├── raw/
│   └── processed/
├── output/                  # Output directory
├── config.json              # Configuration file
├── requirements.txt         # Python dependencies
└── SKILL.md                 # This document
```

## Roadmap

- [x] Basic architecture design
- [x] Core analysis module
- [ ] More data source support (Wellcome Trust, JSPS, etc.)
- [ ] Real-time data stream processing
- [ ] Interactive web interface
- [ ] Machine learning model optimization

## License

MIT License - See LICENSE file in project root directory

---

*Generated by OpenClaw Agent | Skill ID: 200*

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

This skill accepts requests that match the documented purpose of `funding-trend-forecaster` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `funding-trend-forecaster` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
