# Scanpy Plotting Guide

A comprehensive guide for creating publication-quality Scanpy visualizations.

## General Plotting Principles

All Scanpy plotting functions follow a consistent pattern:
- Functions in `sc.pl.*` correspond to analysis functions in `sc.tl.*`
- Most functions accept a `color` parameter to specify gene names or metadata columns
- Results are saved via the `save` parameter
- Multiple plots can be generated in a single call

## Basic Quality Control Plots

### Visualizing QC Metrics

```python
# Violin plots for QC metrics
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True, save='_qc_violin.pdf')

# Scatter plots for identifying outliers
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt', save='_qc_mt.pdf')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts', save='_qc_genes.pdf')

# Highly expressed genes
sc.pl.highest_expr_genes(adata, n_top=20, save='_highest_expr.pdf')
```

### Filtered QC

```python
# Compare before and after filtering
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts'],
             groupby='sample', save='_post_filter.pdf')
```

## Dimensionality Reduction Visualization

### PCA Plots

```python
# Basic PCA
sc.pl.pca(adata, color='leiden', save='_pca.pdf')

# PCA colored by gene expression
sc.pl.pca(adata, color=['gene1', 'gene2', 'gene3'], save='_pca_genes.pdf')

# Variance contribution plot (scree plot)
sc.pl.pca_variance_ratio(adata, log=True, n_pcs=50, save='_variance.pdf')

# PCA loadings plot
sc.pl.pca_loadings(adata, components=[1, 2, 3], save='_loadings.pdf')
```

### UMAP Plots

```python
# Basic UMAP with clustering results
sc.pl.umap(adata, color='leiden', legend_loc='on data', save='_umap_leiden.pdf')

# UMAP colored by multiple variables
sc.pl.umap(adata, color=['leiden', 'cell_type', 'batch'],
           save='_umap_multi.pdf')

# UMAP showing gene expression
sc.pl.umap(adata, color=['CD3D', 'CD14', 'MS4A1'],
           use_raw=False, save='_umap_genes.pdf')

# Custom appearance
sc.pl.umap(adata, color='leiden',
           palette='Set2',
           size=50,
           alpha=0.8,
           frameon=False,
           title='Cell Types',
           save='_umap_custom.pdf')
```

### t-SNE Plots

```python
# t-SNE with clustering results
sc.pl.tsne(adata, color='leiden', legend_loc='right margin', save='_tsne.pdf')

# Multiple t-SNE perplexities (if calculated)
sc.pl.tsne(adata, color='leiden', save='_tsne_default.pdf')
```

## Clustering Visualization

### Basic Clustering Plots

```python
# UMAP with cluster labels
sc.pl.umap(adata, color='leiden', add_outline=True,
           legend_loc='on data', legend_fontsize=12,
           legend_fontoutline=2, frameon=False,
           save='_clusters.pdf')

# Show cluster proportions
sc.pl.umap(adata, color='leiden', size=50, edges=True,
           edges_width=0.1, save='_clusters_edges.pdf')
```

### Cluster Comparison

```python
# Compare clustering results
sc.pl.umap(adata, color=['leiden', 'louvain'],
           save='_cluster_comparison.pdf')

# Cluster dendrogram
sc.tl.dendrogram(adata, groupby='leiden')
sc.pl.dendrogram(adata, groupby='leiden', save='_dendrogram.pdf')
```

## Marker Gene Visualization

### Ranked Marker Genes

```python
# Overview of top marker genes per cluster
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False,
                        save='_marker_overview.pdf')

# Heatmap of top marker genes
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10, groupby='leiden',
                                show_gene_labels=True,
                                save='_marker_heatmap.pdf')

# Dot plot of marker genes
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5,
                                 save='_marker_dotplot.pdf')

# Stacked violin plot
sc.pl.rank_genes_groups_stacked_violin(adata, n_genes=5,
                                       save='_marker_violin.pdf')

# Matrix plot
sc.pl.rank_genes_groups_matrixplot(adata, n_genes=5,
                                   save='_marker_matrix.pdf')
```

### Specific Gene Expression

```python
# Violin plots for specific genes
marker_genes = ['CD3D', 'CD14', 'MS4A1', 'NKG7', 'FCGR3A']
sc.pl.violin(adata, keys=marker_genes, groupby='leiden',
             save='_markers_violin.pdf')

# Dot plot for selected marker genes
sc.pl.dotplot(adata, var_names=marker_genes, groupby='leiden',
              save='_markers_dotplot.pdf')

# Heatmap for specific genes
sc.pl.heatmap(adata, var_names=marker_genes, groupby='leiden',
              swap_axes=True, save='_markers_heatmap.pdf')

# Stacked violin plot for gene sets
sc.pl.stacked_violin(adata, var_names=marker_genes, groupby='leiden',
                     save='_markers_stacked.pdf')
```

### Gene Expression on Embedding

```python
# Multiple genes on UMAP
genes = ['CD3D', 'CD14', 'MS4A1', 'NKG7']
sc.pl.umap(adata, color=genes, cmap='viridis',
           save='_umap_markers.pdf')

# Gene expression plot with custom colormap
sc.pl.umap(adata, color='CD3D', cmap='Reds',
           vmin=0, vmax=3, save='_umap_cd3d.pdf')
```

## Trajectory and Pseudotime Visualization

### PAGA Plots

```python
# PAGA plot
sc.pl.paga(adata, color='leiden', save='_paga.pdf')

# PAGA with gene expression
sc.pl.paga(adata, color=['leiden', 'dpt_pseudotime'],
           save='_paga_pseudotime.pdf')

# PAGA overlaid on UMAP
sc.pl.umap(adata, color='leiden', save='_umap_with_paga.pdf',
           edges=True, edges_color='gray')
```

### Pseudotime Plots

```python
# DPT pseudotime on UMAP
sc.pl.umap(adata, color='dpt_pseudotime', save='_umap_dpt.pdf')

# Gene expression along pseudotime
sc.pl.dpt_timeseries(adata, save='_dpt_timeseries.pdf')

# Heatmap sorted by pseudotime
sc.pl.heatmap(adata, var_names=genes, groupby='leiden',
              use_raw=False, show_gene_labels=True,
              save='_pseudotime_heatmap.pdf')
```

## Advanced Visualization

### Tracks Plot

```python
# Show gene expression across cell types
sc.pl.tracksplot(adata, var_names=marker_genes, groupby='leiden',
                 save='_tracks.pdf')
```

### Correlation Matrix

```python
# Correlation between clusters
sc.pl.correlation_matrix(adata, groupby='leiden',
                         save='_correlation.pdf')
```

### Embedding Density Plot

```python
# Cell density on UMAP
sc.tl.embedding_density(adata, basis='umap', groupby='cell_type')
sc.pl.embedding_density(adata, basis='umap', key='umap_density_cell_type',
                        save='_density.pdf')
```

## Multi-Panel Combined Plots

### Creating Multi-Panel Plots

```python
import matplotlib.pyplot as plt

# Create multi-panel figure
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

# Plot on specific axes
sc.pl.umap(adata, color='leiden', ax=axes[0, 0], show=False)
sc.pl.umap(adata, color='CD3D', ax=axes[0, 1], show=False)
sc.pl.umap(adata, color='CD14', ax=axes[1, 0], show=False)
sc.pl.umap(adata, color='MS4A1', ax=axes[1, 1], show=False)

plt.tight_layout()
plt.savefig('figures/multi_panel.pdf')
plt.show()
```

## Publication-Quality Customization

### High-Quality Settings

```python
# Set publication-quality default parameters
sc.settings.set_figure_params(dpi=300, frameon=False, figsize=(5, 5),
                               facecolor='white')

# Vector graphics output
sc.settings.figdir = './figures/'
sc.settings.file_format_figs = 'pdf'  # or 'svg'
```

### Custom Palettes

```python
# Use custom colors
custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
sc.pl.umap(adata, color='leiden', palette=custom_colors,
           save='_custom_colors.pdf')

# Continuous variable colormaps
sc.pl.umap(adata, color='CD3D', cmap='viridis', save='_viridis.pdf')
sc.pl.umap(adata, color='CD3D', cmap='RdBu_r', save='_rdbu.pdf')
```

### Removing Axes and Frames

```python
# Clean plots without axes
sc.pl.umap(adata, color='leiden', frameon=False,
           save='_clean.pdf')

# Hide legend
sc.pl.umap(adata, color='leiden', legend_loc=None,
           save='_no_legend.pdf')
```

## Exporting Plots

### Saving Individual Plots

```python
# Auto-save using save parameter
sc.pl.umap(adata, color='leiden', save='_leiden.pdf')
# Save path is: sc.settings.figdir + 'umap_leiden.pdf'

# Manual save
import matplotlib.pyplot as plt
fig = sc.pl.umap(adata, color='leiden', show=False, return_fig=True)
fig.savefig('figures/my_umap.pdf', dpi=300, bbox_inches='tight')
```

### Batch Export

```python
# Save multiple versions
for gene in ['CD3D', 'CD14', 'MS4A1']:
    sc.pl.umap(adata, color=gene, save=f'_{gene}.pdf')
```

## Common Customization Parameters

### Layout Parameters
- `figsize`: Figure size (width, height)
- `frameon`: Whether to show figure frame
- `title`: Figure title
- `legend_loc`: Legend location ('right margin', 'on data', 'best', or None)
- `legend_fontsize`: Legend font size
- `size`: Point size

### Color Parameters
- `color`: Variable to color by
- `palette`: Color palette (e.g., 'Set1', 'viridis')
- `cmap`: Colormap for continuous variables
- `vmin`, `vmax`: Color scale limits
- `use_raw`: Whether to use raw counts for gene expression plotting

### Save Parameters
- `save`: Filename suffix when saving
- `show`: Whether to display the plot directly
- `dpi`: Resolution for raster formats

## Publication Plot Tips

1. **Use vector formats**: Use PDF or SVG for scalable graphics.
2. **High DPI**: For raster plots, set `dpi=300` or higher.
3. **Consistent style**: Use the same color palette across plots.
4. **Clear labels**: Ensure gene names and cell types are clearly readable.
5. **White background**: Use `facecolor='white'` for publications.
6. **Reduce clutter**: Set `frameon=False` for a cleaner appearance.
7. **Legend placement**: Use `'on data'` to make combined plots more compact.
8. **Colorblind-friendly**: Consider using palettes like 'colorblind' or 'Set2'.
