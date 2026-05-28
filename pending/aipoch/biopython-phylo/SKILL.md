---
name: biopython-phylo
description: Use Bio.Phylo to read/write phylogenetic trees and perform visualization and statistics; use when tree parsing/conversion, pruning/rerooting, distance calculation, or plotting is required.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# biopython-phylo

## When to Use

- Converting phylogenetic tree files between Newick, NEXUS, and phyloXML formats.
- Traversing a tree to locate clades, prune taxa, or reroot at a specific node/outgroup.
- Computing pairwise distances, distance matrices, or basic tree statistics (e.g., branch length summaries).
- Producing quick tree visualizations as ASCII output for logs/CLI workflows.
- Generating publication-ready plots of trees using Matplotlib.

## Key Features

- Read and write phylogenetic trees via `Bio.Phylo` with support for common formats (Newick/NEXUS/phyloXML).
- Tree manipulation utilities: traversal, clade selection, pruning, and rerooting.
- Distance computation and simple statistics derived from branch lengths/topology.
- Visualization options:
  - ASCII rendering for terminal output.
  - Matplotlib-based plotting for figures.

## Dependencies

- `biopython>=1.80`
- Optional (for plotting):
  - `matplotlib>=3.7`

## Example Usage

The following example is runnable end-to-end and follows the conventions:
- Configuration is stored in `config/task_config.json`.
- Script is invoked as `python scripts/phylo_task.py`.
- All file I/O uses `encoding="utf-8"`.
- JSON output uses `ensure_ascii=False`.

### `config/task_config.json`

```json
{
  "input_tree": "data/input_tree.nwk",
  "input_format": "newick",
  "output_tree": "artifacts/output_tree.xml",
  "output_format": "phyloxml",
  "prune_terminals": ["TaxonC"],
  "reroot_outgroup": "TaxonB",
  "ascii_out": "artifacts/tree_ascii.txt",
  "stats_out": "artifacts/tree_stats.json",
  "plot_enabled": true,
  "plot_out": "artifacts/tree_plot.png"
}
```

### `scripts/phylo_task.py`

```python
import json
import os
from typing import Any, Dict, List, Optional

from Bio import Phylo


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def prune_by_names(tree, names: List[str]) -> None:
    # Prune terminals by name if present
    for n in names:
        if tree.find_any(name=n) is not None:
            tree.prune(target=n)


def reroot_by_outgroup_name(tree, outgroup_name: str) -> None:
    outgroup = tree.find_any(name=outgroup_name)
    if outgroup is None:
        raise ValueError(f"Outgroup '{outgroup_name}' not found in tree terminals/clades.")
    tree.root_with_outgroup(outgroup)


def tree_stats(tree) -> Dict[str, Any]:
    terminals = tree.get_terminals()
    nonterminals = tree.get_nonterminals()

    # Collect branch lengths (may include None)
    lengths = []
    for clade in tree.find_clades(order="preorder"):
        if clade.branch_length is not None:
            lengths.append(float(clade.branch_length))

    return {
        "n_terminals": len(terminals),
        "n_nonterminals": len(nonterminals),
        "n_clades_total": len(terminals) + len(nonterminals),
        "branch_length_count": len(lengths),
        "branch_length_sum": sum(lengths) if lengths else 0.0,
        "branch_length_min": min(lengths) if lengths else None,
        "branch_length_max": max(lengths) if lengths else None,
        "branch_length_mean": (sum(lengths) / len(lengths)) if lengths else None,
    }


def write_ascii(tree, out_path: str) -> None:
    ensure_parent_dir(out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        Phylo.draw_ascii(tree, file=f)


def plot_tree(tree, out_path: str) -> None:
    # Optional dependency: matplotlib
    import matplotlib
    matplotlib.use("Agg")  # headless backend
    import matplotlib.pyplot as plt

    ensure_parent_dir(out_path)
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, do_show=False, axes=ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def main(config_path: str = "config/task_config.json") -> None:
    cfg = load_config(config_path)

    input_tree = cfg["input_tree"]
    input_format = cfg.get("input_format", "newick")
    output_tree = cfg["output_tree"]
    output_format = cfg.get("output_format", "phyloxml")

    prune_terminals: List[str] = cfg.get("prune_terminals", [])
    reroot_outgroup: Optional[str] = cfg.get("reroot_outgroup")

    ascii_out = cfg.get("ascii_out", "artifacts/tree_ascii.txt")
    stats_out = cfg.get("stats_out", "artifacts/tree_stats.json")

    plot_enabled = bool(cfg.get("plot_enabled", False))
    plot_out = cfg.get("plot_out", "artifacts/tree_plot.png")

    # Read
    tree = Phylo.read(input_tree, input_format)

    # Manipulate
    if prune_terminals:
        prune_by_names(tree, prune_terminals)

    if reroot_outgroup:
        reroot_by_outgroup_name(tree, reroot_outgroup)

    # Write converted tree
    ensure_parent_dir(output_tree)
    Phylo.write(tree, output_tree, output_format)

    # ASCII visualization
    write_ascii(tree, ascii_out)

    # Stats
    ensure_parent_dir(stats_out)
    with open(stats_out, "w", encoding="utf-8") as f:
        json.dump(tree_stats(tree), f, ensure_ascii=False, indent=2)

    # Plot (optional)
    if plot_enabled:
        plot_tree(tree, plot_out)


if __name__ == "__main__":
    main()
```

### Run

```bash
python scripts/phylo_task.py
```

## Implementation Details

- **Configuration-first execution**: parameters are stored in `config/task_config.json` as an intermediate artifact; scripts are invoked uniformly via `python scripts/<task_name>.py`. Avoid stacking many CLI `--` arguments; prefer config files.
- **Encoding and JSON output**:
  - Always open files with `encoding="utf-8"`.
  - When writing JSON, use `ensure_ascii=False` to preserve non-ASCII characters.
- **Supported formats**:
  - Input/output formats are passed to `Phylo.read(...)` and `Phylo.write(...)` (e.g., `newick`, `nexus`, `phyloxml`).
- **Pruning**:
  - Pruning is performed by terminal/clade name using `tree.prune(target=<name>)`. Names not found are skipped (or can be treated as errors depending on your policy).
- **Rerooting**:
  - Rerooting uses `tree.root_with_outgroup(outgroup_clade)`; the outgroup is located via `tree.find_any(name=...)`.
- **Statistics**:
  - Branch lengths may be missing (`None`); statistics should ignore missing values.
  - Basic counts can be derived from `tree.get_terminals()` and `tree.get_nonterminals()`.
- **Visualization**:
  - ASCII output uses `Phylo.draw_ascii(tree, file=...)` for deterministic CLI-friendly rendering.
  - Matplotlib plotting uses a non-interactive backend (`Agg`) for headless environments and saves to an image file.