# SRAgent Claude Skill

A Claude skill for working with the NCBI Sequence Read Archive (SRA), Gene Expression Omnibus (GEO), and retrieving scientific publications associated with genomics datasets.

## Installation

### 1. **Install SRAgent:**
   ```bash
   # Clone SRAgent repository
   git clone https://github.com/ArcInstitute/SRAgent.git
   cd SRAgent
   
   # Install with uv (recommended)
   uv venv
   source .venv/bin/activate
   uv pip install .
   
   # Verify installation
   SRAgent --help
   ```

### 2. **Configure API Keys:**
   
   Set the following environment variables:
   ```bash
   # Required: LLM provider (choose one)
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   # OR
   OPENAI_API_KEY=sk-your-key-here
   
   # Recommended: NCBI access
   EMAIL=your-email@example.com
   NCBI_API_KEY=your-ncbi-key
   
   # Optional: Paper downloads
   CORE_API_KEY=your-core-key
   ```

### 3. **Choose Model Environment:**
   ```bash
   # For Claude models (recommended with ANTHROPIC_API_KEY)
   export DYNACONF=claude
   
   # For OpenAI models
   export DYNACONF=prod
   ```

### 4. **Install the skill:**

#### Claude Code CLI

Install the skill using the Claude Code CLI:
```bash
mkdir -p ~/.claude/skills/ && \
  cp -r claude-skill/ ~/.claude/skills/sragent
```

## Usage in Claude

Once installed, Claude will automatically use this skill when you ask questions about:

- SRA or GEO accessions (GSE, SRP, SRX, SRR)
- Converting between accession formats
- Metadata about sequencing experiments
- Single-cell RNA-seq technology identification
- Finding or downloading papers associated with datasets

### Example Queries

**Accession Conversion:**
```
"Convert GSE121737 to SRX accessions"
"What are the SRR run accessions for SRX4967527?"
```

**Metadata Extraction:**
```
"What sequencing technology was used for ERX11887200?"
"Is SRX4967527 single-cell RNA-seq data?"
"Which 10X Genomics chemistry was used in this experiment: SRX4967527"
```

**Paper Retrieval:**
```
"Download papers for SRX4967527"
"Find all publications associated with study PRJNA498286"
"I have a CSV with SRA accessions - help me download their papers"
```

## Skill Contents

- `SKILL.md` - Main skill file with complete instructions
- `examples/` - Example queries and workflows
- `reference/` - Quick reference guides
- `README.md` - This file

## Features

✅ **Accession Conversion** - GSE→SRP→SRX→SRR  
✅ **Metadata Extraction** - Platform, organism, technology  
✅ **Technology ID** - Identify 10X, Smart-seq, etc.  
✅ **Paper Downloads** - Multiple sources with fallback  
✅ **Batch Processing** - CSV input for multiple datasets  
✅ **BigQuery Support** - Large-scale metadata queries  

## Troubleshooting

**Skill not loading?**
- Ensure skill is in `~/.claude/skills/sragent/`
- Check that `SKILL.md` has valid YAML frontmatter
- Restart Claude Code if using CLI

**SRAgent commands failing?**
- Verify SRAgent installation: `which SRAgent`
- Check API keys: `echo $ANTHROPIC_API_KEY`
- Ensure `.env` file is in working directory

**BigQuery errors?**
- Optional feature - SRAgent works without it
- To enable: `gcloud auth application-default login`
- Set: `export GCP_PROJECT_ID="your-project"`

## Resources

- **SRAgent GitHub:** https://github.com/ArcInstitute/SRAgent
- **NCBI SRA:** https://www.ncbi.nlm.nih.gov/sra
- **GEO Database:** https://www.ncbi.nlm.nih.gov/geo/
- **Claude Skills Docs:** https://docs.claude.com/en/docs/agents-and-tools/agent-skills


## Example Claude prompts

> Note, these prompts require the https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-databases skills

## 1. Validating Alzheimer's Hub Genes in Single-Cell Data

I want to identify which Alzheimer's disease genes are most central to the disease network and then validate if these hub genes have been experimentally studied at single-cell resolution. Use **string-database** to build a protein-protein interaction network for the top 30 Alzheimer's-associated genes and identify the hub proteins (those with >10 interactions). Then use **SRAgent** to search SRA specifically for scRNA-seq datasets that mention these hub gene names in their study titles or abstracts, and download the associated papers to see which cell types in the brain show altered expression of these hub genes in AD patients.

## 2. Pathway-to-Experiment Mapping for Parkinson's Disease

Use **reactome-database** to identify the top 5 biological pathways most strongly associated with Parkinson's disease (e.g., mitochondrial dysfunction, protein degradation, dopamine synthesis). For each pathway, extract the gene lists. Then use **SRAgent** to search SRA for single-cell or single-nucleus RNA-seq datasets from Parkinson's patients, and in the downloaded manuscripts, look specifically for sections that analyze the pathway genes you identified - do the authors validate pathway-level dysregulation in specific cell types like dopaminergic neurons?

## 3. Cross-Species Translation of Cancer Driver Networks

I'm studying whether cancer driver gene networks are conserved across species. Use **ensembl-database** to get orthologs of human cancer driver genes (TP53, KRAS, MYC, PTEN) in mouse and zebrafish. Then use **string-database** to build PPI networks for these orthologs in each species. Now use **SRAgent** to find scRNA-seq datasets from cancer models in both human and mouse (search for "cancer" + organism name), download the publications, and check if the authors found similar pathway disruptions across species or if there are species-specific differences that affect model validity.

## 4. Drug Target Validation Through scRNA-seq Perturbation Studies

Use **fda-database** to identify recently approved or late-stage clinical trial drugs for rheumatoid arthritis and their molecular targets. Then use **gene-database** to get detailed information about these target genes. Use **SRAgent** to search SRA for CRISPR knockout, drug treatment, or perturbation scRNA-seq datasets that manipulated these specific target genes in immune cells or synovial fibroblasts. Download the papers to see the cell-type-specific effects of perturbing these drug targets - this reveals which cell types respond to the drug and potential off-target effects.

## 5. Comparing Bulk Expression Patterns to Single-Cell Resolution

Use **geo-database** to find the 3 most-cited bulk RNA-seq studies of Type 2 Diabetes in pancreatic islets, and note which genes showed the strongest differential expression. Then use **SRAgent** to find matching single-cell or single-nucleus RNA-seq datasets from T2D islets (search for same tissue + disease). Download both the GEO dataset metadata and the SRA-associated papers, and analyze: do the bulk RNA-seq hits localize to specific cell types (beta cells vs alpha vs delta) in the single-cell data, or were they driven by changes in cell type proportions rather than per-cell expression changes?

## 6. From Protein Domain to Cell-Type Expression

I want to understand which cell types express kinase domain-containing proteins that could be drug targets in inflammatory bowel disease. Use **uniprot-database** to identify all proteins with serine/threonine kinase domains that are mentioned in IBD research. Use **gene-database** to get the corresponding gene symbols. Then use **SRAgent** to find scRNA-seq datasets from Crohn's disease or ulcerative colitis intestinal tissue, download the papers, and extract which cell types (epithelial, immune, stromal) express these kinase genes at high levels - this reveals cell-type-specific druggable targets.


## 7. Ortholog Expression Consistency Across Development

Use **ensembl-database** to find zebrafish orthologs of human congenital heart disease genes (NKX2-5, GATA4, TBX5). Use **kegg-database** to identify which cardiac development pathways these genes participate in. Then use **SRAgent** to search SRA for developmental time-course scRNA-seq datasets from both zebrafish and mouse heart development, focusing on datasets that captured cardiomyocyte differentiation. Download the papers and compare: do the orthologous genes show similar temporal expression patterns during heart development across species, suggesting conserved developmental programs?

