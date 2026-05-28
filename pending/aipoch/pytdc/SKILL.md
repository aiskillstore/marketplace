---
name: pytdc
description: Therapeutics Data Commons (PyTDC) for AI-ready therapeutic ML datasets and benchmarks; use it when you need standardized dataset loading, meaningful splits (e.g., scaffold/cold-start), and consistent evaluation for ADME/Toxicity/DTI/DDI or molecular optimization.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need **curated, AI-ready datasets** for drug discovery tasks (e.g., ADME, toxicity, bioactivity, DTI/DDI).
- You want **standardized benchmarks** with consistent evaluation protocols (including multi-seed benchmark groups).
- You require **meaningful data splits** such as **scaffold splits** (chemical diversity) or **cold-start splits** (unseen drugs/targets).
- You are building models for **single-instance prediction** (molecular/protein properties) or **multi-instance prediction** (interactions).
- You are doing **goal-directed molecular generation** and need **property Oracles** for scoring/optimization.

## Key Features

- **Dataset access by task type**
  - Single-instance prediction: ADME, Toxicity (Tox), HTS, QM, and more.
  - Multi-instance prediction: DTI, DDI, PPI, and more.
  - Generation: MolGen, RetroSyn, PairMolGen.
- **Standardized splitting utilities**
  - `random`, `scaffold`, and cold-start variants such as `cold_drug`, `cold_target`, `cold_drug_target`, plus `temporal` where applicable.
- **Unified evaluation**
  - Built-in `Evaluator` with common metrics (ROC-AUC, PR-AUC, RMSE, MAE, Spearman, etc.).
- **Benchmark groups**
  - Curated collections (e.g., ADMET group) with recommended evaluation protocols (commonly 5 seeds).
- **Chem/data utilities**
  - Molecular format conversion (e.g., SMILES → PyG), filtering, balancing, negative sampling, entity retrieval (CID→SMILES, UniProt→sequence).
- **Molecular Oracles**
  - Property scoring functions usable for goal-directed generation workflows (see `references/oracles.md`).

## Dependencies

Install (recommended):

```bash
uv pip install PyTDC
```

Upgrade:

```bash
uv pip install PyTDC --upgrade
```

Core runtime dependencies (installed automatically; versions depend on the PyTDC release you install):

- `PyTDC` (latest from PyPI)
- `numpy`
- `pandas`
- `scikit-learn`
- `tqdm`
- `seaborn`
- `fuzzywuzzy`

Optional dependencies may be pulled in automatically depending on which submodules you use (e.g., graph backends or chemistry toolchains).

## Example Usage

A complete runnable example that:
1) loads an ADME dataset,  
2) performs a scaffold split,  
3) trains a simple baseline model,  
4) evaluates with a standard metric,  
5) queries an Oracle score for a SMILES.

```python
# pip install PyTDC scikit-learn

from tdc.single_pred import ADME
from tdc import Evaluator, Oracle

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import Ridge

def main():
    # 1) Load a single-instance prediction dataset (ADME)
    data = ADME(name="Caco2_Wang")

    # 2) Create a scaffold split (train/valid/test)
    split = data.get_split(method="scaffold", seed=42, frac=[0.7, 0.1, 0.2])
    train, valid, test = split["train"], split["valid"], split["test"]

    # 3) Train a simple baseline model on SMILES strings
    #    (character n-gram + ridge regression; replace with your own model)
    model = Pipeline(
        steps=[
            ("featurizer", CountVectorizer(analyzer="char", ngram_range=(2, 5))),
            ("regressor", Ridge(alpha=1.0)),
        ]
    )
    model.fit(train["Drug"], train["Y"])

    # 4) Evaluate on the test set using a TDC Evaluator
    y_pred = model.predict(test["Drug"])
    evaluator = Evaluator(name="MAE")
    mae = evaluator(test["Y"], y_pred)
    print(f"Test MAE: {mae:.4f}")

    # 5) Oracle scoring example (property scoring for a SMILES)
    oracle = Oracle(name="DRD2")
    score = oracle("CC(C)Cc1ccc(cc1)C(C)C(O)=O")
    print(f"DRD2 Oracle score: {score}")

if __name__ == "__main__":
    main()
```

Related references and templates (if present in this skill package):
- Oracle catalog and usage: `references/oracles.md`
- Utility functions (splits, processing, retrieval): `references/utilities.md`
- Dataset catalog: `references/datasets.md`
- Workflow templates: `scripts/load_and_split_data.py`, `scripts/benchmark_evaluation.py`, `scripts/molecular_generation.py`

## Implementation Details

### 1) Dataset Access Pattern

PyTDC datasets follow a consistent interface:

```python
from tdc.<problem> import <Task>

data = <Task>(name="<DatasetName>")
df = data.get_data(format="df")
split = data.get_split(method="scaffold", seed=1, frac=[0.7, 0.1, 0.2])
```

- `<problem>` is typically one of:
  - `single_pred` (single-entity property prediction)
  - `multi_pred` (pairwise/multi-entity interaction prediction)
  - `generation` (molecule/reaction generation tasks)

### 2) Splitting Strategies (Key Parameters)

Use `get_split(...)` to obtain `{"train": ..., "valid": ..., "test": ...}`.

Common parameters:
- `method`: split strategy
- `seed`: random seed for reproducibility
- `frac`: `[train, valid, test]` fractions (when supported)

Typical methods:
- `random`: random shuffling split
- `scaffold`: Bemis–Murcko scaffold-based split to reduce scaffold leakage and improve chemical generalization
- Cold-start (commonly for interaction tasks like DTI/DDI):
  - `cold_drug`: test contains unseen drugs
  - `cold_target`: test contains unseen targets
  - `cold_drug_target`: test contains unseen drugs and targets
- `temporal`: time-based split for datasets with timestamps (when available)

Example:

```python
split = data.get_split(method="cold_target", seed=1)
```

### 3) Standardized Evaluation

TDC provides a unified evaluator:

```python
from tdc import Evaluator

evaluator = Evaluator(name="ROC-AUC")  # classification
score = evaluator(y_true, y_pred)
```

Choose metrics appropriate to the task type:
- Classification: `ROC-AUC`, `PR-AUC`, `F1`, `Accuracy`, etc.
- Regression: `RMSE`, `MAE`, `R2`, `Spearman`, `Pearson`, etc.

### 4) Data Schemas (What Columns to Expect)

While schemas vary by task, common conventions include:

- Single-instance prediction (e.g., ADME/Tox):
  - `Drug` (often SMILES) and label `Y`
  - sometimes `Drug_ID` / `Compound_ID`

- Multi-instance prediction (e.g., DTI):
  - `Drug` (SMILES), `Target` (protein sequence), label `Y`
  - plus identifiers such as `Drug_ID`, `Target_ID`

### 5) Oracles for Molecular Optimization

Oracles provide a callable scoring interface:

```python
from tdc import Oracle

oracle = Oracle(name="GSK3B")
score = oracle("CCO...")
scores = oracle(["SMILES1", "SMILES2"])
```

Use Oracles to:
- score candidate molecules during generation,
- define optimization objectives,
- compare molecules under consistent property predictors.

For the full list of Oracles and their expected inputs/outputs, see `references/oracles.md`.