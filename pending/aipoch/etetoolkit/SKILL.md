---
name: etetoolkit
description: ETE (Environment for Tree Exploration) toolkit for phylogenetic and hierarchical tree analysis; use it when you need to parse/manipulate Newick/NHX trees, detect duplication/speciation events, integrate NCBI taxonomy, and render publication-quality figures.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- **Preprocess phylogenetic trees**: convert formats (Newick/NHX/PhyloXML), reroot (midpoint/outgroup), prune taxa, and resolve polytomies before downstream analyses.
- **Detect evolutionary events in gene trees**: infer **duplication vs. speciation** events and derive **ortholog/paralog** relationships for phylogenomics.
- **Annotate trees with taxonomy**: map species names to **NCBI TaxIDs**, retrieve lineages/ranks, and build minimal taxonomy topologies connecting a set of taxa.
- **Generate publication-quality visualizations**: render trees to **PDF/SVG/PNG** with custom styles, support-based coloring, and node “faces” (labels, shapes, heatmaps).
- **Compare alternative topologies**: quantify differences between trees using **Robinson–Foulds (RF)** distance and partition/bipartition analysis.

## Key Features

- **Tree I/O and manipulation**
  - Read/write: Newick, NHX, PhyloXML, NeXML
  - Traversals: preorder, postorder, levelorder
  - Operations: prune, reroot, collapse, resolve polytomies
  - Metrics: branch/topological distances, RF distance
- **Phylogenetic (gene tree) analysis**
  - Alignment association (FASTA/Phylip)
  - Species name extraction from gene IDs
  - Duplication/speciation detection (e.g., species overlap / reconciliation-style workflows)
  - Orthology/paralogy extraction and gene-family splitting
- **NCBI taxonomy integration**
  - Auto-download + local cache of taxonomy DB
  - TaxID ↔ scientific name translation
  - Lineage/rank retrieval and taxonomy-based topology building
  - Tree annotation with taxonomic metadata
- **Visualization**
  - Rectangular/circular layouts, GUI exploration
  - NodeStyle/TreeStyle customization
  - Faces (text, shapes, charts/heatmaps) and layout functions
  - Export to PDF/SVG/PNG
- **Clustering support**
  - ClusterTree for dendrograms linked to numeric matrices
  - Cluster quality metrics (e.g., silhouette, Dunn index)
  - Heatmap + tree combined views

## Dependencies

- `ete3` (recommended: `>=3.1.0`)
- Optional GUI/rendering dependencies (platform-specific):
  - `PyQt5` (e.g., `>=5.15`)
  - Qt SVG support (often packaged as `python3-pyqt5.qtsvg` on Debian/Ubuntu)

## Example Usage

The following example is designed to be runnable end-to-end (it uses an in-memory Newick string and does not require external files).

```python
# pip install ete3

from ete3 import Tree, TreeStyle, NodeStyle

# 1) Load a tree (Newick)
nw = "((A:0.1,B:0.2)90:0.3,(C:0.2,D:0.4)70:0.1);"
t = Tree(nw, format=1)

# 2) Basic stats
print("Leaves:", len(t))
print("Total nodes:", sum(1 for _ in t.traverse()))

# 3) Midpoint rooting
mid = t.get_midpoint_outgroup()
t.set_outgroup(mid)

# 4) Prune to taxa of interest (preserve branch lengths)
t.prune(["A", "C", "D"], preserve_branch_length=True)

# 5) Style nodes (color internal nodes by support)
ts = TreeStyle()
ts.show_leaf_name = True
ts.show_branch_support = True

for n in t.traverse():
    st = NodeStyle()
    if n.is_leaf():
        st["fgcolor"] = "blue"
        st["size"] = 8
    else:
        # ETE stores internal support in n.support when present
        st["fgcolor"] = "darkgreen" if getattr(n, "support", 0) >= 80 else "red"
        st["size"] = 5
    n.set_style(st)

# 6) Render (PDF/SVG/PNG supported depending on your environment)
t.render("example_tree.pdf", tree_style=ts)
print("Wrote: example_tree.pdf")
```

## Implementation Details

### Tree parsing formats (Newick “format” codes)
ETE uses a `format` integer to control how node attributes are interpreted when reading/writing Newick. Common patterns:

- `format=0`: flexible default (often includes branch lengths)
- `format=1`: includes internal node names
- `format=2`: includes support/bootstrap values
- `format=5`: internal node names + branch lengths
- `format=8`: name + distance + support (maximal common usage)
- `format=9`: leaf names only
- `format=100`: topology only

Example:

```python
from ete3 import Tree

t = Tree("tree.nw", format=1)
t.write(outfile="out.nw", format=5)
```

### NHX feature preservation
NHX is used to store custom per-node features. When writing, specify which features to serialize:

```python
t.write(outfile="tree.nhx", features=["taxid", "habitat", "lineage"])
```

### Rerooting and pruning behavior
- **Midpoint rooting** uses `get_midpoint_outgroup()` to select an outgroup that balances path lengths.
- **Pruning** should typically use `preserve_branch_length=True` to avoid distorting distances in phylogenetic contexts.

### Evolutionary event detection (gene trees)
For gene trees, `PhyloTree` supports event labeling on internal nodes (commonly:
- `evoltype == "D"` for duplication
- `evoltype == "S"` for speciation)

A typical workflow is:
1. Load a gene tree (optionally with an alignment).
2. Provide a **species naming function** to map gene IDs → species.
3. Run descendant event detection.
4. Extract ortholog groups (speciation subtrees) or query ortholog/paralog sets from events.

### Tree comparison (Robinson–Foulds)
`Tree.robinson_foulds(other_tree)` returns:
- `rf`: RF distance (number of differing bipartitions)
- `max_rf`: maximum possible RF given shared leaves
- plus shared leaves and partition sets for deeper inspection

Normalized RF is typically computed as `rf / max_rf` (when `max_rf > 0`).