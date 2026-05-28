# ETE Toolkit API Reference Guide

## Overview

ETE (Environment for Tree Exploration) is a Python toolkit for phylogenetic tree manipulation, analysis, and visualization. This reference guide covers the main classes and methods.

## Core Classes

### TreeNode (Alias: Tree)

The base class representing a tree structure with hierarchical node organization.

**Constructor:**
```python
from ete3 import Tree
t = Tree(newick=None, format=0, dist=None, support=None, name=None)
```

**Parameters:**
- `newick`: Newick string or file path
- `format`: Newick format (0-100). Common formats:
  - `0`: Flexible format with branch lengths and names
  - `1`: Includes internal node names
  - `2`: Includes bootstrap/support values
  - `5`: Includes internal node names and branch lengths
  - `8`: Includes all features (name, distance, support)
  - `9`: Leaf names only
  - `100`: Topology only
- `dist`: Branch length to parent (default: 1.0)
- `support`: Bootstrap/confidence value (default: 1.0)
- `name`: Node identifier

### PhyloTree

A specialized class for phylogenetic analysis, extending TreeNode.

**Constructor:**
```python
from ete3 import PhyloTree
t = PhyloTree(newick=None, alignment=None, alg_format='fasta',
              sp_naming_function=None, format=0)
```

**Additional Parameters:**
- `alignment`: Path to alignment file or alignment string
- `alg_format`: 'fasta' or 'phylip'
- `sp_naming_function`: Custom function to extract species from node names

### ClusterTree

A class for hierarchical clustering analysis.

**Constructor:**
```python
from ete3 import ClusterTree
t = ClusterTree(newick, text_array=None)
```

**Parameters:**
- `text_array`: Tab-delimited matrix with column headers and row names

### NCBITaxa

A class for NCBI taxonomy database operations.

**Constructor:**
```python
from ete3 import NCBITaxa
ncbi = NCBITaxa(dbfile=None)
```

The first instantiation will download the ~300MB NCBI taxonomy database to `~/.etetoolkit/taxa.sqlite`.

## Node Attributes

### Basic Attributes

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `name` | str | Node identifier | "NoName" |
| `dist` | float | Branch length to parent | 1.0 |
| `support` | float | Bootstrap/confidence value | 1.0 |
| `up` | TreeNode | Reference to parent node | None |
| `children` | list | List of child nodes | [] |

### Custom Features

Add any custom data to nodes:
```python
node.add_feature("custom_name", value)
node.add_features(feature1=value1, feature2=value2)
```

Access features:
```python
value = node.custom_name
# OR
value = getattr(node, "custom_name", default_value)
```

## Navigation & Traversal

### Basic Navigation

```python
# Check node type
node.is_leaf()          # Returns True if terminal node
node.is_root()          # Returns True if root node
len(node)               # Number of leaves under node

# Get related nodes
parent = node.up
children = node.children
root = node.get_tree_root()
```

### Traversal Strategies

```python
# Three traversal strategies
for node in tree.traverse("preorder"):    # Root → Left → Right
    print(node.name)

for node in tree.traverse("postorder"):   # Left → Right → Root
    print(node.name)

for node in tree.traverse("levelorder"):  # Level by level
    print(node.name)

# Exclude the root node
for node in tree.iter_descendants("postorder"):
    print(node.name)
```

### Getting Nodes

```python
# Get all leaf nodes
leaves = tree.get_leaves()
for leaf in tree:  # Shortcut iteration
    print(leaf.name)

# Get all descendant nodes
descendants = tree.get_descendants()

# Get ancestor nodes
ancestors = node.get_ancestors()

# Get specific nodes by attribute
nodes = tree.search_nodes(name="NodeA")
node = tree & "NodeA"  # Shortcut syntax

# Get leaves by name
leaves = tree.get_leaves_by_name("LeafA")

# Get Lowest Common Ancestor (LCA)
ancestor = tree.get_common_ancestor("LeafA", "LeafB", "LeafC")

# Custom filtering
filtered = [n for n in tree.traverse() if n.dist > 0.5 and n.is_leaf()]
```

### Iterator Methods (Memory Efficient)

```python
# For large trees, use iterators
for match in tree.iter_search_nodes(name="X"):
    if some_condition:
        break  # Stop early

for leaf in tree.iter_leaves():
    process(leaf)

for descendant in node.iter_descendants():
    process(descendant)
```

## Tree Construction & Modification

### Creating a Tree from Scratch

```python
# Create empty tree
t = Tree()

# Add child nodes
child1 = t.add_child(name="A", dist=1.0)
child2 = t.add_child(name="B", dist=2.0)

# Add sister nodes
sister = child1.add_sister(name="C", dist=1.5)

# Populate with random topology
t.populate(10)  # Create 10 random leaves
t.populate(5, names_library=["A", "B", "C", "D", "E"])
```

### Removing & Deleting Nodes

```python
# Detach: Removes the entire subtree
node.detach()
# OR
parent.remove_child(node)

# Delete: Removes the node and connects its children to its parent
node.delete()
# OR
parent.remove_child(node)
```

### Pruning

Keep only specified leaf nodes:
```python
# Keep only these leaves, remove everything else
tree.prune(["A", "B", "C"])

# Preserve original branch lengths
tree.prune(["A", "B", "C"], preserve_branch_length=True)
```

### Tree Splicing

```python
# Mount one tree as a child of another
t1 = Tree("(A,(B,C));")
t2 = Tree("((D,E),(F,G));")
A = t1 & "A"
A.add_child(t2)
```

### Tree Copying

```python
# Four copying methods
copy1 = tree.copy()  # Default: cpickle (preserves types)
copy2 = tree.copy("newick")  # Fastest: basic topology
copy3 = tree.copy("newick-extended")  # Includes custom features as text
copy4 = tree.copy("deepcopy")  # Slowest: handles complex objects
```

## Tree Operations

### Rooting

```python
# Set outgroup (re-rooting)
outgroup_node = tree & "OutgroupLeaf"
tree.set_outgroup(outgroup_node)

# Midpoint rooting
midpoint = tree.get_midpoint_outgroup()
tree.set_outgroup(midpoint)

# Unroot
tree.unroot()
```

### Handling Polytomies

```python
# Resolve polytomies into bifurcating structures
tree.resolve_polytomy(recursive=False)  # Single node only
tree.resolve_polytomy(recursive=True)   # Entire tree
```

### Ladderize

```python
# Sort branches based on size
tree.ladderize()
tree.ladderize(direction=1)  # Ascending
```

### Converting to Ultrametric

```python
# Make all leaves equidistant from the root
tree.convert_to_ultrametric()
tree.convert_to_ultrametric(tree_length=100)  # Specify total length
```

## Distances & Comparisons

### Distance Calculation

```python
# Branch length distance between nodes
dist = tree.get_distance("A", "B")
dist = nodeA.get_distance(nodeB)

# Topology distance only (node count)
dist = tree.get_distance("A", "B", topology_only=True)

# Farthest nodes
farthest, distance = node.get_farthest_node()
farthest_leaf, distance = node.get_farthest_leaf()
```

### Monophyly Testing

```python
# Check if given values form a monophyletic group
is_mono, clade_type, base_node = tree.check_monophyly(
    values=["A", "B", "C"],
    target_attr="name"
)
# Returns: (bool, "monophyletic"|"paraphyletic"|"polyphyletic", node)

# Get all monophyletic clades
monophyletic_nodes = tree.get_monophyletic(
    values=["A", "B", "C"],
    target_attr="name"
)
```

### Tree Comparison

```python
# Robinson-Foulds distance
rf, max_rf, common_leaves, parts_t1, parts_t2 = t1.robinson_foulds(t2)
print(f"RF distance: {rf}/{max_rf}")

# Normalized RF distance
result = t1.compare(t2)
norm_rf = result["norm_rf"]  # 0.0 to 1.0
ref_edges = result["ref_edges_in_source"]
```

## Input/Output

### Reading Trees

```python
# From string
t = Tree("(A:1,(B:1,(C:1,D:1):0.5):0.5);")

# From file
t = Tree("tree.nw")

# Specify format
t = Tree("tree.nw", format=1)
```

### Writing Trees

```python
# Write to string
newick = tree.write()
newick = tree.write(format=1)
newick = tree.write(format=1, features=["support", "custom_feature"])

# Write to file
tree.write(outfile="output.nw")
tree.write(format=5, outfile="output.nw", features=["name", "dist"])

# Custom leaf function (for collapsing)
def is_leaf(node):
    return len(node) <= 3  # Treat small clades as leaves

newick = tree.write(is_leaf_fn=is_leaf)
```

### Tree Rendering

```python
# Show interactive GUI
tree.show()

# Render to file (PNG, PDF, SVG)
tree.render("tree.png")
tree.render("tree.pdf", w=200, units="mm")
tree.render("tree.svg", dpi=300)

# ASCII representation
print(tree)
print(tree.get_ascii(show_internal=True, compact=False))
```

## Performance Optimization

### Caching Content

For frequent access to node contents:
```python
# Cache content of all nodes
node2content = tree.get_cached_content()

# Fast lookup
for node in tree.traverse():
    leaves = node2content[node]
    print(f"Node has {len(leaves)} leaves")
```

### Precomputing Distances

```python
# For multiple distance queries
node2dist = {}
for node in tree.traverse():
    node2dist[node] = node.get_distance(tree)
```

## PhyloTree Specific Methods

### Sequence Alignment

```python
# Link alignment
tree.link_to_alignment("alignment.fasta", alg_format="fasta")

# Access sequences
for leaf in tree:
    print(f"{leaf.name}: {leaf.sequence}")
```

### Species Naming

```python
# Default: first 3 letters
# Custom function
def get_species(node_name):
    return node_name.split("_")[0]

tree.set_species_naming_function(get_species)

# Manual setting
for leaf in tree:
    leaf.species = extract_species(leaf.name)
```

### Evolutionary Events

```python
# Detect duplication/speciation events
events = tree.get_descendant_evol_events()

for node in tree.traverse():
    if hasattr(node, "evoltype"):
        print(f"{node.name}: {node.evoltype}")  # "D" for Duplication, "S" for Speciation

# Use with species tree
species_tree = Tree("(human, (chimp, gorilla));")
events = tree.get_descendant_evol_events(species_tree=species_tree)
```

### Gene Tree Operations

```python
# Get species trees from redundant gene families
species_trees = tree.get_speciation_trees()

# Split by duplication events
subtrees = tree.split_by_dups()

# Collapse lineage-specific expansions
tree.collapse_lineage_specific_expansions()
```

## NCBITaxa Methods

### Database Operations

```python
from ete3 import NCBITaxa
ncbi = NCBITaxa()

# Update database
ncbi.update_taxonomy_database()
```

### Querying Taxonomic Information

```python
# Get taxid by name
taxid = ncbi.get_name_translator(["Homo sapiens"])
# Returns: {'Homo sapiens': [9606]}

# Get name by taxid
names = ncbi.get_taxid_translator([9606, 9598])
# Returns: {9606: 'Homo sapiens', 9598: 'Pan troglodytes'}

# Get rank
rank = ncbi.get_rank([9606])
# Returns: {9606: 'species'}

# Get lineage
lineage = ncbi.get_lineage(9606)
# Returns: [1, 131567, 2759, ..., 9606]

# Get descendants
descendants = ncbi.get_descendant_taxa("Primates")
descendants = ncbi.get_descendant_taxa("Primates", collapse_subspecies=True)
```

### Building Taxonomy Trees

```python
# Get the minimal tree connecting specified taxa
tree = ncbi.get_topology([9606, 9598, 9593])  # Human, Chimp, Gorilla

# Annotate tree with taxonomic info
tree.annotate_ncbi_taxa()

# Access taxonomy info
for node in tree.traverse():
    print(f"{node.sci_name} ({node.taxid}) - Rank: {node.rank}")
```

## ClusterTree Methods

### Linking Data

```python
# Link matrix to tree
tree.link_to_arraytable(matrix_string)

# Access profile
for leaf in tree:
    print(leaf.profile)  # Array of values
```

### Clustering Metrics

```python
# Get Silhouette coefficient
silhouette = tree.get_silhouette()

# Get Dunn index
dunn = tree.get_dunn()

# Inter/Intra cluster distances
inter = node.intercluster_dist
intra = node.intracluster_dist

# Deviation
dev = node.deviation
```

### Distance Metrics

Supported metrics:
- `"euclidean"`: Euclidean distance
- `"pearson"`: Pearson correlation
- `"spearman"`: Spearman rank correlation

```python
tree.dist_to(node2, metric="pearson")
```

## Common Error Handling

```python
# Check if tree is empty
if tree.children:
    print("Tree has children")

# Check if node exists
nodes = tree.search_nodes(name="X")
if nodes:
    node = nodes[0]

# Access features safely
value = getattr(node, "feature_name", default_value)

# Check format compatibility
try:
    tree.write(format=1)
except:
    print("Tree lacks internal node names")
```

## Best Practices

1. **Use appropriate traversal**: Postorder for bottom-up, Preorder for top-down.
2. **Use caching for repeated access**: Use `get_cached_content()` for frequent queries.
3. **Use iterators for large trees**: Memory-efficient processing.
4. **Preserve branch lengths**: Use `preserve_branch_length=True` when pruning.
5. **Choose copy methods wisely**: "newick" for speed, "cpickle" for full fidelity.
6. **Validate monophyly**: Check the returned clade type (mono/para/polyphyletic).
7. **Use PhyloTree for phylogenetic analysis**: It contains specialized evolutionary methods.
8. **Cache NCBI queries**: Store results to avoid repeated database access.