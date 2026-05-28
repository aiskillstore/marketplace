---
name: hypogenic
description: Automated LLM-driven hypothesis generation and testing for tabular datasets; use when you need systematic exploration of empirical patterns (e.g., fraud detection, content analysis) and want to combine literature insights with data-driven hypothesis evaluation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- **Exploratory analysis on a new dataset** where you want the model to propose multiple *testable* hypotheses from observed patterns (e.g., AI-generated text detection).
- **Benchmarking competing explanations** by generating a hypothesis bank and evaluating them consistently on validation/test splits.
- **Literature-informed research** where you want to extract claims from papers and refine them against real data (e.g., deception cues in reviews).
- **High-coverage hypothesis discovery** when you need both theory-driven and data-driven hypotheses, then merge/deduplicate them (Union workflows).
- **Hypothesis-driven classification/regression pipelines** for domains like fraud detection, content moderation, mental health indicators, or other empirical studies using tabular/JSON datasets.

## Key Features

- **Automated hypothesis generation (HypoGeniC)**: iteratively proposes and improves hypotheses using dataset feedback.
- **Literature + data integration (HypoRefine)**: extracts literature insights from PDFs and refines hypotheses jointly with empirical signals.
- **Union method**: mechanically merges literature-only hypotheses with HypoGeniC/HypoRefine outputs to maximize coverage and reduce redundancy.
- **Config-driven prompting**: YAML templates with variable injection (e.g., `${text_features_1}`, `${num_hypotheses}`) for generation and inference.
- **Scalable experimentation**: optional Redis caching, parallelism, and adaptive selection focusing on hard examples.

## Dependencies

- `hypogenic` (install via PyPI; version depends on your environment)
- Optional (recommended for cost/performance):
  - `redis` (server; used for caching repeated LLM calls)
- Optional (required for literature/PDF workflows such as HypoRefine):
  - `GROBID` (service; used for PDF preprocessing)
  - `s2orc-doc2json` (PDF-to-structured conversion used in literature pipelines)

Install:
```bash
uv pip install hypogenic
```

## Example Usage

The following example is a minimal end-to-end workflow (dataset + config + CLI + Python). Adjust paths and prompts for your task.

### 1) Prepare a dataset (HuggingFace-style JSON)

Create three files:

- `./data/my_task_train.json`
- `./data/my_task_val.json`
- `./data/my_task_test.json`

Example schema (feature keys can be renamed, but must match your config placeholders):
```json
{
  "text_features_1": ["Text A1", "Text A2"],
  "text_features_2": ["Text B1", "Text B2"],
  "label": ["Class1", "Class2"]
}
```

### 2) Create `./data/my_task/config.yaml`

```yaml
task_name: my_task

train_data_path: ./data/my_task_train.json
val_data_path: ./data/my_task_val.json
test_data_path: ./data/my_task_test.json

prompt_templates:
  observations: |
    Feature 1: ${text_features_1}
    Feature 2: ${text_features_2}
    Label: ${label}

  batched_generation:
    system: |
      You are a scientific assistant. Propose testable, falsifiable hypotheses that map features to labels.
    user: |
      Given examples and labels, generate ${num_hypotheses} distinct hypotheses.
      Return a JSON list of hypotheses, each with a short name and a testable statement.

  inference:
    system: |
      You are a careful classifier. Use the provided hypothesis to predict the label.
    user: |
      Hypothesis: ${hypothesis}
      Feature 1: ${text_features_1}
      Feature 2: ${text_features_2}
      Output the final answer as: "final answer: <LABEL>"
```

### 3) Run generation + inference (CLI)

```bash
# Generate hypotheses (HypoGeniC)
hypogenic_generation \
  --config ./data/my_task/config.yaml \
  --method hypogenic \
  --num_hypotheses 20

# Evaluate generated hypotheses
hypogenic_inference \
  --config ./data/my_task/config.yaml \
  --hypotheses ./output/hypotheses.json
```

### 4) Run the same workflow (Python API)

```python
from hypogenic import BaseTask
import re

def extract_label(llm_output: str) -> str:
    m = re.search(r"final answer:\s*(.*)", llm_output, re.IGNORECASE)
    return m.group(1).strip() if m else llm_output.strip()

task = BaseTask(
    config_path="./data/my_task/config.yaml",
    extract_label=extract_label,
)

task.generate_hypotheses(
    method="hypogenic",
    num_hypotheses=20,
    output_path="./output/hypotheses.json",
)

results = task.inference(
    hypothesis_bank="./output/hypotheses.json",
    test_data="./data/my_task_test.json",
)

print(results)
```

## Implementation Details

### Methods

- **HypoGeniC (data-driven)**
  - Initializes hypotheses from a subset of training data.
  - Iteratively evaluates hypotheses on validation data and replaces underperforming ones.
  - Often uses *hard/challenging samples* to prompt improved hypotheses.

- **HypoRefine (literature + data)**
  - Preprocesses PDFs into structured text (commonly via GROBID + conversion tooling).
  - Generates a literature-derived hypothesis bank and a data-derived hypothesis bank.
  - Refines both banks iteratively using performance feedback and relevance checks.

- **Union**
  - Produces combined banks such as:
    - `Literature ∪ HypoGeniC`
    - `Literature ∪ HypoRefine`
  - Focuses on coverage and deduplication rather than deeper joint optimization.

### Configuration and Prompt Parameters

- **Variable injection**: prompt templates can reference dataset fields and runtime parameters:
  - `${text_features_1}`, `${text_features_2}`, … (from dataset JSON)
  - `${label}` (ground truth label, typically used in observation templates)
  - `${num_hypotheses}` (generation-time control)
  - `${hypothesis}` (inference-time hypothesis text)
- **Label parsing (`extract_label`)**:
  - Accuracy depends on extracting a label string that *exactly matches* the dataset’s `label` values.
  - Default patterns often look for `final answer: ...`; customize for your output format.

### Performance/Cost Controls (Optional)

- **Redis caching**: reduces repeated LLM calls during iterative generation and evaluation.
- **Parallelism**: speeds up hypothesis testing on large datasets.
- **Adaptive selection**: prioritizes difficult examples to improve hypothesis quality over iterations.