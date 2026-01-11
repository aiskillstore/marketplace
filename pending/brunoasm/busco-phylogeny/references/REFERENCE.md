# BUSCO-based Phylogenomics - Technical Reference

Detailed technical reference for implementing phylogenomic workflows.

## Table of Contents

1. [Sample Naming Best Practices](#sample-naming-best-practices)
2. [BUSCO Lineage Datasets](#busco-lineage-datasets)
3. [Resource Recommendations](#resource-recommendations)
4. [Template Job Scripts](#template-job-scripts)
5. [Common Issues](#common-issues)
6. [Quality Control Guidelines](#quality-control-guidelines)
7. [Aliscore/ALICUT: Detailed Guide](#aliscorealicut-detailed-guide)
8. [Tool Citations](#tool-citations)
9. [Software Installation Guide](#software-installation-guide)

---

## Sample Naming Best Practices

**Sample names appear in your final phylogenetic trees**, so choose them carefully!

### Recommended Format

**`[ACCESSION]_[SPECIES_NAME]`**

Examples:
- `GCA000001735_Arabidopsis_thaliana`
- `GCF009858895_Apis_mellifera`
- `PRJNA12345_Drosophila_melanogaster_strain_w1118`

### Why This Format?

1. **Accession first** = Easy to trace back to original data
2. **Species name** = Readable in phylogenetic trees
3. **Underscore-separated** = Compatible with all phylogenetics software
4. **No spaces or special characters** = Prevents parsing errors

### Rules for Sample Names

**DO:**
- Use only letters, numbers, underscores, and hyphens
- Keep names reasonably short (<50 characters)
- Be consistent across your dataset
- Include strain/population info if relevant (e.g., `GCA123_Species_name_pop1`)

**DON'T:**
- Use spaces (use underscores instead)
- Use special characters: `()[]{}|<>@#$%^&*+=;:'",./\`
- Start with numbers (some tools don't like this)
- Use periods except for version numbers
- Make names too cryptic (will appear in publications!)

### Using the Rename Helper Script

The `scripts/rename_genomes.py` helper can assist with renaming:

```bash
# Create a template mapping file
python scripts/rename_genomes.py --create-template *.fasta > samples.tsv

# Edit samples.tsv to add meaningful names:
# GCA_000001735.2.fasta    GCA000001735_Arabidopsis_thaliana
# GCF_009858895.2.fasta    GCF009858895_Apis_mellifera

# Apply the mapping (with backup)
python scripts/rename_genomes.py --mapping samples.tsv

# Or use interactive mode
python scripts/rename_genomes.py --interactive *.fasta
```

### For NCBI Downloaded Genomes

When downloading from NCBI, genome files are typically in subdirectories like:
```
ncbi_dataset/data/GCA_000001735.2/GCA_000001735.2_genomic.fna
```

You'll need to:
1. Extract assembly accessions and organism names
2. Create meaningful sample names
3. Copy and rename files to working directory

Example workflow:
```bash
# List assemblies with organism names
for dir in ncbi_dataset/data/GCA_*; do
    acc=$(basename $dir)
    # Extract organism name from metadata
    echo "$acc"
done

# Create mapping file manually or with download_ncbi_genomes.py --list-only
```

---

## BUSCO Lineage Datasets

### General Lineages

- `eukaryota_odb10` - All eukaryotes (255 BUSCOs)
- `bacteria_odb10` - All bacteria (124 BUSCOs)
- `archaea_odb10` - All archaea (194 BUSCOs)

### Eukaryotic Kingdoms

- `metazoa_odb10` - Animals (954 BUSCOs)
- `viridiplantae_odb10` - Green plants (425 BUSCOs)
- `fungi_odb10` - Fungi (758 BUSCOs)

### Animals (Metazoa)

- `arthropoda_odb10` - Arthropods (1013 BUSCOs)
  - `insecta_odb10` - Insects (1367 BUSCOs)
    - `diptera_odb10` - Flies (3285 BUSCOs)
    - `hymenoptera_odb10` - Bees, wasps, ants (5991 BUSCOs)
    - `lepidoptera_odb10` - Moths, butterflies (5286 BUSCOs)
  - `arachnida_odb10` - Spiders, mites (2934 BUSCOs)
- `vertebrata_odb10` - Vertebrates (3354 BUSCOs)
  - `actinopterygii_odb10` - Ray-finned fish (3640 BUSCOs)
  - `mammalia_odb10` - Mammals (9226 BUSCOs)
  - `aves_odb10` - Birds (8338 BUSCOs)
- `mollusca_odb10` - Molluscs (5295 BUSCOs)
- `nematoda_odb10` - Roundworms (3131 BUSCOs)

### Plants (Viridiplantae)

- `eudicots_odb10` - Eudicots (2326 BUSCOs)
- `liliopsida_odb10` - Monocots (3278 BUSCOs)
- `embryophyta_odb10` - Land plants (1614 BUSCOs)

### Fungi

- `ascomycota_odb10` - Ascomycetes (1706 BUSCOs)
- `basidiomycota_odb10` - Basidiomycetes (1335 BUSCOs)

*For complete list, see: https://busco-data.ezlab.org/v5/data/lineages/*

---

## Resource Recommendations

### SLURM/PBS Job Resource Allocations

| Step | CPUs | RAM per CPU | Total RAM | Walltime | Notes |
|------|------|-------------|-----------|----------|-------|
| compleasm | 4 | 6 GB | 24 GB | 24h | Increase to 8-10 GB for large genomes (>2 Gbp) |
| MAFFT (per locus) | 1 | 4 GB | 4 GB | 24h | Can run as large array job |
| Aliscore | 1 | 4 GB | 4 GB | 24h | Array job |
| trimAl | 1 | 2 GB | 2 GB | 2h | Very fast |
| BMGE | 1 | 2 GB | 2 GB | 4h | Moderate speed |
| ClipKit | 1 | 2 GB | 2 GB | 2h | Very fast |
| IQ-TREE (gene) | 1 | 4 GB | 4 GB | 2h | Array job for all loci |
| IQ-TREE (concat) | 18-32 | 4 GB | 72-128 GB | 72h | Main phylogeny job |
| ASTRAL | 1 | 8 GB | 8 GB | <1h | Usually very fast |

### Scaling Guidelines

**Small dataset** (<20 genomes, <1000 loci):
- Can run on local machine
- Expect ~2-5 days total runtime

**Medium dataset** (20-50 genomes, 1000-3000 loci):
- Cluster recommended
- Expect ~3-7 days with parallelization

**Large dataset** (>50 genomes, >3000 loci):
- Cluster required
- Expect 1-2 weeks with good parallelization

---

## Template Job Scripts

### SLURM Array Template

```bash
#!/bin/bash
#SBATCH --job-name=JOB_NAME
#SBATCH --array=1-N
#SBATCH --cpus-per-task=NCPUS
#SBATCH --mem-per-cpu=MEMORY
#SBATCH --time=WALLTIME
#SBATCH --output=logs/%A_%a.JOBNAME.out
#SBATCH --error=logs/%A_%a.JOBNAME.err
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=YOUR_EMAIL

source ~/.bashrc
conda activate ENV_NAME

# Parse input file
input=$(sed -n "${SLURM_ARRAY_TASK_ID}p" input_list.txt)

# Run command
COMMAND ${input}
```

### PBS Array Template

```bash
#!/bin/bash
#PBS -N JOB_NAME
#PBS -t 1-N
#PBS -l nodes=1:ppn=NCPUS
#PBS -l mem=MEMORY
#PBS -l walltime=WALLTIME
#PBS -j oe
#PBS -m abe
#PBS -M YOUR_EMAIL

cd $PBS_O_WORKDIR
source ~/.bashrc
conda activate ENV_NAME

# Parse input file
input=$(sed -n "${PBS_ARRAYID}p" input_list.txt)

# Run command
COMMAND ${input}
```

### Local Sequential Template

```bash
#!/bin/bash
# Sequential execution for local machine

source ~/.bashrc
conda activate ENV_NAME

while read input; do
  echo "Processing ${input}..."
  COMMAND ${input}
done < input_list.txt

echo "All jobs complete"
```

---

## Common Issues

### Problem: compleasm runs out of memory

**Solution:**
- Increase `--mem-per-cpu` to 8 GB or 10 GB
- Some large/complex genomes need more RAM

### Problem: IQ-TREE stalls or runs extremely slowly

**Solution:**
- Add `-safe` flag (enables safe numerical mode, slower but more stable)
- Reduce number of threads if on shared system
- Check for very long branches or problematic sequences

### Problem: Array job exceeds cluster limits

**Solution:**
- Split into batches (e.g., if limit is 1000, run arrays 1-1000, 1001-2000, etc.)
- Example: `#SBATCH --array=1-1000%50` (runs 1000 jobs, max 50 concurrent)

### Problem: Missing orthologs in some genomes

**Solution:**
- This is normal and expected
- FASconCAT and IQ-TREE handle missing data automatically
- If >20% orthologs missing, consider genome quality issues

### Problem: Alignment looks poor/misaligned

**Solution:**
- Visualize with AliView or Jalview
- MAFFT L-INS-i is accurate but slow; for very divergent sequences, try E-INS-i
- Consider stricter trimming parameters
- Very divergent sequences may not be suitable for phylogenomics

### Problem: Gene trees conflict with concatenation tree

**Solution:**
- This is common and expected (incomplete lineage sorting, gene flow)
- ASTRAL species tree accounts for discordance
- Compare both trees and branch support values
- Look for systematic vs. random conflicts

### Problem: Low bootstrap/posterior support values

**Solution:**
- Check alignment quality
- Try more stringent trimming
- Evaluate locus informativeness (some may be uninformative)
- Consider rapid diversification or conflicting signal
- More data doesn't always help if signal quality is poor

---

## Quality Control Guidelines

### Genome Completeness Assessment

**Excellent** (>95% complete BUSCOs):
- Highly complete genomes
- Retain for phylogenomics
- Expected to contribute many orthologs

**Good** (90-95% complete):
- Generally acceptable
- May be missing some loci
- Retain unless other quality concerns

**Acceptable** (85-90% complete):
- Marginal quality
- Will have more missing orthologs
- Consider case-by-case based on biological importance

**Questionable** (70-85% complete):
- Poor completeness
- May introduce noise
- Recommend excluding unless scientifically critical

**Poor** (<70% complete):
- Very incomplete
- Strong recommend to exclude
- Likely contaminated, fragmented, or poor assembly

### Fragmentation and Duplication

**Fragmented BUSCOs:**
- <5%: Excellent
- 5-10%: Good
- >10%: Indicates assembly fragmentation issues

**Duplicated BUSCOs:**
- <2%: Excellent
- 2-5%: Good (may indicate recent WGD or heterozygosity)
- >10%: Likely contamination or assembly issues

---

## Aliscore/ALICUT: Detailed Guide

### What is Aliscore/ALICUT?

**Aliscore** (Alignment Sequence Conservancy Checker) uses Monte Carlo resampling to identify randomly similar sequence (RSS) sections in multiple sequence alignments. These are regions where observed similarity is not significantly different from random expectation, which can mislead phylogenetic inference.

**ALICUT** (Alignment Cutter) removes the RSS positions identified by Aliscore, producing trimmed alignments suitable for phylogenetic analysis.

### When to Use Aliscore/ALICUT

**Recommended for:**
- Phylogenomic datasets (hundreds to thousands of loci)
- Amino acid alignments from single-copy orthologs
- Mixed-quality alignments with variable conservation
- Published phylogenomics studies (widely used and cited)

**Consider alternatives for:**
- Very short alignments (<100 positions) - not enough data for statistics
- Perfectly conserved sequences - no trimming needed
- Time-sensitive analyses - Aliscore can be slow for very long alignments

### Key Parameters Explained

#### Window Size (`-w`)

Controls the sliding window used for scoring alignment regions.

- **Default: 4** (recommended for most analyses)
- **Smaller (3):** More sensitive, may over-trim well-aligned regions (Type I error)
- **Larger (6-8):** Less sensitive to short RSS sections, more conservative

**Recommendation:** Use default `-w 4` unless you have specific concerns about over-trimming.

#### Random Pairs (`-r`)

Number of pairwise sequence comparisons to perform.

- **Default: 4×N** (where N = number of taxa)
- **Higher values:** More comprehensive but slower; diminishing returns beyond 4×N
- **Lower values:** Faster but less reliable statistics

**Recommendation:** Use default for most analyses; increase for small datasets (<10 taxa).

#### Gap Treatment (`-N`)

Controls how alignment gaps (indels) are interpreted.

- **Without `-N`:** Gaps treated as 5th character state (informative)
  - Use for: Well-aligned conserved proteins where indels are rare
  - Effect: Conserves long indel regions present in most taxa

- **With `-N`:** Gaps treated as ambiguous/missing data
  - **Use for: Amino acid sequences** (recommended)
  - Effect: More stringent; removes poorly aligned gappy regions

**Recommendation:** **Always use `-N` for amino acid data** from BUSCO/compleasm orthologs.

#### Tree-Guided Mode (`-t`)

Use a phylogenetic tree to guide comparisons (compares sister taxa first).

- **Advantages:** More phylogenetically informed, can be faster
- **Disadvantages:** Requires pre-existing tree, assumes tree is accurate
- **When to use:** Large datasets (>100 taxa) where random sampling is slow

**Recommendation:** Use random mode (default) for initial analyses; tree-guided mode for refinement.

### Understanding Aliscore Output

Each Aliscore run generates three files:

1. **`[alignment]_List_random.txt`**
   - Space-separated list of RSS position numbers
   - Input file for ALICUT
   - Empty file = no RSS detected (alignment is clean)

2. **`[alignment]_Profile_random.txt`**
   - Three columns: Position, Positive_Score, Negative_Score
   - Shows quality profile across alignment
   - Negative values indicate RSS positions

3. **`[alignment].svg`**
   - Visual plot of scoring profiles
   - Y-axis: Score (positive = conserved, negative = random)
   - X-axis: Alignment position
   - Useful for manual inspection

### Interpreting Trimming Results

After running Aliscore + ALICUT, evaluate trimming statistics:

#### Positions Removed

- **<10%:** Excellent alignment quality, minimal trimming needed
- **10-20%:** Good alignment quality, reasonable trimming
- **20-35%:** Moderate quality, substantial but acceptable trimming
- **35-50%:** Poor alignment quality, consider manual inspection
- **>50%:** Very poor alignment, **consider excluding entire locus**

#### What to Check

```bash
# View summary statistics
cat trimmed_aa/trimming_summary.txt

# Check specific locus
cd aliscore_output/aliscore_[locus]
cat ALICUT_info.xls
```

#### Red Flags

- **Uniformly high trimming across all loci:** Check alignment quality (MAFFT parameters)
- **One locus with >50% trimmed:** Likely paralogous or contamination
- **No RSS detected for most loci:** Sequences may be too similar (recent divergence)

### ALICUT Options

#### `-r` (Remain Stems)

For RNA secondary structure alignments, preserves paired stem positions.

```bash
bash scripts/run_alicut.sh aliscore_output/aliscore_16S/ -r -s
```

**When to use:** rRNA genes (16S, 18S, 28S) with structure annotation

#### `-c` (Remove Codon)

Translates amino acid RSS positions to nucleotide triplets (back-translation).

```bash
# After running Aliscore on protein alignment
bash scripts/run_alicut.sh aliscore_output/aliscore_protein/ -c -s
```

**When to use:**
- Analyzed protein alignment, want to trim corresponding nucleotide alignment
- Requires both protein and nucleotide files with identical names

#### `-3` (Remove 3rd Position)

Removes only 3rd codon positions of identified RSS.

```bash
bash scripts/run_alicut.sh aliscore_output/aliscore_protein/ -c -3 -s
```

**When to use:**
- Want to exclude fast-evolving 3rd codon positions
- Can combine with `-c` option

### Workflow Integration

#### Typical Usage (Batch Mode)

```bash
# Process all aligned amino acids through Aliscore + ALICUT
bash scripts/run_aliscore_alicut_batch.sh aligned_aa/ -N -o trimmed_aa
```

This is the **recommended approach** for most phylogenomic analyses.

#### Array Job Mode (HPC)

For large datasets on compute clusters:

```bash
# Step 1: Aliscore array job
cd aligned_aa
ls *.fas > locus_list.txt
# Submit array job (see SKILL.md for templates)

# Step 2: After Aliscore completes, batch process ALICUT
for dir in aliscore_output/aliscore_*/; do
    bash ../scripts/run_alicut.sh "${dir}" -s
done
```

### Quality Control After Trimming

#### Check Alignment Lengths

```bash
# Summary statistics
awk 'NR>1 {sum+=$3; count++} END {print "Mean trimmed length:", sum/count}' \
    trimmed_aa/trimming_summary.txt

# Find very short alignments
awk 'NR>1 && $3<100 {print $1, $3}' trimmed_aa/trimming_summary.txt
```

**Minimum recommended:** 100 amino acids after trimming

#### Visual Inspection

For critical loci, view the SVG plots:

```bash
# Open in browser
firefox aliscore_output/aliscore_[locus]/*svg
```

Look for:
- Large contiguous RSS regions → May indicate paralogy
- RSS at alignment ends → Common and acceptable
- Scattered RSS throughout → Normal for divergent sequences

### Troubleshooting

#### Aliscore Errors

**"Can't locate Aliscore_module.pm"**
- Download both `Aliscore.02.2.pl` and `Aliscore_module.pm`
- Keep in same directory

**"taxon names of tree and sequence files do not match"**
- Tree mode: ensure tree tip labels exactly match FASTA headers
- Solution: Use random mode instead (`-r` option)

**"Sequence length too short"**
- Alignment has fewer positions than RSS identified
- Usually indicates corrupted input file

#### ALICUT Errors

**"Can not find List file"**
- Aliscore didn't complete successfully
- Check Aliscore logs for errors

**"File [alignment] is empty"**
- Aliscore didn't copy alignment file
- Run from correct directory

**All positions removed**
- Extremely poor alignment quality
- Exclude this locus from analysis

### Performance Considerations

**Memory:** Aliscore typically uses 1-2 GB per alignment

**Runtime:**
- Small alignments (10 taxa, 1000 positions): 1-5 minutes
- Medium (50 taxa, 2000 positions): 10-30 minutes
- Large (100 taxa, 3000 positions): 30-60 minutes

**Parallelization:**
- Aliscore itself is single-threaded
- Parallelize across loci using array jobs
- Typical dataset: 1000-2000 loci × 20 minutes = use array jobs

### Comparison with Other Trimmers

| Tool | Method | Speed | Stringency | Best For |
|------|--------|-------|------------|----------|
| **Aliscore/ALICUT** | Monte Carlo RSS detection | Slow | Moderate-High | Phylogenomics (gold standard) |
| **trimAl** | Gap/conservation thresholds | Very fast | Customizable | Large datasets, quick analyses |
| **BMGE** | Entropy-based | Fast | Moderate | Balanced speed/quality |
| **ClipKit** | Parsimony-informative sites | Very fast | Low-Moderate | Maximum data retention |

**Recommendation:** Use Aliscore/ALICUT for final publication-quality analyses; trimAl for initial exploratory work.

---

## Tool Citations

### Required Citations

**compleasm:**
Huang, N., & Li, H. (2023). compleasm: a faster and more accurate reimplementation of BUSCO. *Bioinformatics*, 39(10), btad595.
https://doi.org/10.1093/bioinformatics/btad595

**BUSCO (if used instead of compleasm):**
Manni, M., Berkeley, M. R., Seppey, M., Simão, F. A., & Zdobnov, E. M. (2021). BUSCO update: novel and streamlined workflows along with broader and deeper phylogenetic coverage for scoring of eukaryotic, prokaryotic, and viral genomes. *Molecular Biology and Evolution*, 38(10), 4647-4654.

**MAFFT:**
Katoh, K., & Standley, D. M. (2013). MAFFT multiple sequence alignment software version 7: improvements in performance and usability. *Molecular Biology and Evolution*, 30(4), 772-780.

**IQ-TREE:**
Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution*, 37(5), 1530-1534.

**ASTRAL:**
Zhang, C., Rabiee, M., Sayyari, E., & Mirarab, S. (2018). ASTRAL-III: polynomial time species tree reconstruction from partially resolved gene trees. *BMC Bioinformatics*, 19(6), 153.

### Trimming Tool Citations

**Aliscore/ALICUT:**
Kück, P., Meusemann, K., Dambach, J., Thormann, B., von Reumont, B. M., Wägele, J. W., & Misof, B. (2010). Parametric and non-parametric masking of randomness in sequence alignments can be improved and leads to better resolved trees. *Frontiers in Zoology*, 7(1), 10.

**trimAl:**
Capella-Gutiérrez, S., Silla-Martínez, J. M., & Gabaldón, T. (2009). trimAl: a tool for automated alignment trimming in large-scale phylogenetic analyses. *Bioinformatics*, 25(15), 1972-1973.

**BMGE:**
Criscuolo, A., & Gribaldo, S. (2010). BMGE (Block Mapping and Gathering with Entropy): a new software for selection of phylogenetic informative regions from multiple sequence alignments. *BMC Evolutionary Biology*, 10(1), 210.

**ClipKit:**
Steenwyk, J. L., Buida III, T. J., Li, Y., Shen, X. X., & Rokas, A. (2020). ClipKIT: a multiple sequence alignment trimming software for accurate phylogenomic inference. *PLOS Biology*, 18(12), e3001007.

### Software Download Links

- **compleasm:** https://github.com/huangnengCSU/compleasm
- **BUSCO:** https://busco.ezlab.org/
- **MAFFT:** https://mafft.cbrc.jp/alignment/software/
- **Aliscore:** https://github.com/PatrickKueck/AliCUT (includes Aliscore.02.2.pl)
- **ALICUT:** https://github.com/PatrickKueck/AliCUT
- **trimAl:** https://github.com/inab/trimal
- **BMGE:** https://gitlab.pasteur.fr/GIPhy/BMGE
- **ClipKit:** https://github.com/JLSteenwyk/ClipKIT
- **IQ-TREE:** https://github.com/iqtree/iqtree2
- **ASTRAL:** https://github.com/smirarab/ASTRAL
- **FASconCAT-G:** https://github.com/PatrickKueck/FASconCAT-G
- **NCBI Datasets:** https://www.ncbi.nlm.nih.gov/datasets/

---

## Software Installation Guide

This section provides detailed installation instructions for all tools, with options for both conda-based and manual installations. All methods work without sudo/admin access.

### Automated Setup Script (Recommended for Most Users)

Use this automated bash script to set up a complete unified conda environment with all necessary tools. This is the script referenced in SKILL.md STEP 0.

**Generate `setup_phylo_env.sh` with the following content:**

```bash
#!/bin/bash
# setup_phylo_env.sh
# Sets up unified conda environment for phylogenomics workflow
# Generated by Claude phylo_from_buscos skill

set -e

echo "=========================================="
echo "Phylogenomics Environment Setup"
echo "=========================================="
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Please install Miniconda or Anaconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Ask user preference for conda vs mamba
echo "We will use Anaconda/Miniconda to set up the software environment."
echo ""
echo "Package Manager Options:"
echo "  1) mamba (faster, recommended if available)"
echo "  2) conda (standard, always available)"
echo ""
read -p "Enter choice [1-2] (default: 2): " PKG_MGR_CHOICE
PKG_MGR_CHOICE=${PKG_MGR_CHOICE:-2}

if [ "${PKG_MGR_CHOICE}" = "1" ]; then
    if command -v mamba &> /dev/null; then
        PKG_MANAGER="mamba"
        echo "Using mamba for environment creation"
    else
        echo "WARNING: mamba not found. Falling back to conda."
        echo "To install mamba: conda install -n base -c conda-forge mamba"
        PKG_MANAGER="conda"
    fi
else
    PKG_MANAGER="conda"
    echo "Using conda for environment creation"
fi

echo ""

# Environment name
ENV_NAME="phylo"

echo "Creating environment: ${ENV_NAME}"
echo ""

# Create environment with all tools (using chosen package manager)
${PKG_MANAGER} create -n ${ENV_NAME} -y \
    -c conda-forge -c bioconda \
    python=3.9 \
    astral-tree \
    compleasm \
    mafft \
    trimal \
    clipkit \
    bmge \
    iqtree \
    perl \
    perl-bioperl \
    parallel \
    wget \
    ncbi-datasets-cli \
    openjdk

echo ""
echo "Environment created successfully!"
echo ""

# Setup Aliscore and ALICUT Perl scripts
echo "Setting up Aliscore and ALICUT Perl scripts..."
echo ""

# Activate environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ${ENV_NAME}

# Get the directory where this skill is located
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create scripts directory
mkdir -p scripts

# Ask user preference for script source
echo "Aliscore/ALICUT Script Source Options:"
echo "  1) Use predownloaded scripts (from Paul Frandsen's tutorial, tested)"
echo "  2) Download latest versions from official repository"
echo ""
read -p "Enter choice [1-2] (default: 1): " SCRIPT_CHOICE
SCRIPT_CHOICE=${SCRIPT_CHOICE:-1}

if [ "${SCRIPT_CHOICE}" = "1" ]; then
    echo "Using predownloaded Aliscore/ALICUT scripts..."

    # Download predownloaded scripts from GitHub repository
    GITHUB_BASE="https://raw.githubusercontent.com/brunoasm/my_claude_skills/main/phylo_from_buscos/scripts/predownloaded_aliscore_alicut"
    if wget -q "${GITHUB_BASE}/Aliscore.02.2.pl" -O scripts/Aliscore.02.2.pl && \
       wget -q "${GITHUB_BASE}/ALICUT_V2.31.pl" -O scripts/ALICUT_V2.31.pl && \
       wget -q "${GITHUB_BASE}/Aliscore_module.pm" -O scripts/Aliscore_module.pm; then
        chmod +x scripts/Aliscore.02.2.pl scripts/ALICUT_V2.31.pl
        echo "Predownloaded scripts downloaded successfully."
    else
        echo "ERROR: Failed to download predownloaded scripts. Falling back to download option."
        SCRIPT_CHOICE="2"
    fi
fi

if [ "${SCRIPT_CHOICE}" = "2" ]; then
    echo "Downloading latest Aliscore/ALICUT scripts from GitHub..."

    # Try to download from GitHub repository
    if wget -q https://github.com/PatrickKueck/AliCUT/raw/master/Aliscore_v.2.0/Aliscore.02.2.pl -O scripts/Aliscore.02.2.pl && \
       wget -q https://github.com/PatrickKueck/AliCUT/raw/master/ALICUT_V2.3.1/ALICUT_V2.31.pl -O scripts/ALICUT_V2.31.pl && \
       wget -q https://github.com/PatrickKueck/AliCUT/raw/master/Aliscore_v.2.0/Aliscore_module.pm -O scripts/Aliscore_module.pm; then
        chmod +x scripts/Aliscore.02.2.pl scripts/ALICUT_V2.31.pl
        echo "Latest scripts downloaded successfully."
    else
        echo "ERROR: Failed to download scripts from GitHub."
        echo "Please manually download from: https://github.com/PatrickKueck/AliCUT"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Conda environment: ${ENV_NAME}"
echo "Perl with BioPerl: installed"
echo "Aliscore script:   scripts/Aliscore.02.2.pl"
echo "ALICUT script:     scripts/ALICUT_V2.31.pl"
echo "Aliscore module:   scripts/Aliscore_module.pm"
echo ""
echo "To activate environment:"
echo "  conda activate ${ENV_NAME}"
echo ""
echo "Key tools installed:"
conda list | grep -E "compleasm|mafft|trimal|clipkit|bmge|iqtree|astral|parallel|perl|openjdk"
echo ""
```

**Usage:**
```bash
# Run setup script
bash setup_phylo_env.sh

# Activate environment for all workflow steps
conda activate phylo
```

**This unified environment includes:**
- `compleasm` - BUSCO ortholog identification
- `mafft` - Multiple sequence alignment
- `trimal`, `clipkit`, `bmge` - Alignment trimming
- `iqtree` - Phylogenetic inference
- `astral-tree` - Species tree inference (coalescent method)
- `openjdk` - Java runtime for ASTRAL and other tools
- `perl` with BioPerl - Required for Aliscore/ALICUT
- `parallel` - GNU parallel for batch processing
- `ncbi-datasets-cli` - For NCBI genome downloads

**Important Notes:**
- Users can choose between using mamba (faster) or conda (standard) for environment creation
- Users can choose between predownloaded Aliscore/ALICUT scripts (tested with tutorial) or latest versions from GitHub
- Predownloaded scripts are downloaded from the GitHub repository
- All subsequent workflow steps should use `conda activate phylo` instead of creating separate environments
- The unified environment simplifies workflow management and reduces disk space usage
- ASTRAL is installed as `astral-tree` and accessible via the `astral` command (no manual download needed)

---

### Conda/Bioconda Installation (Recommended)

Most tools are available via conda/bioconda and work on both Linux and macOS (including Apple Silicon with Rosetta).

#### Initial Setup

```bash
# Add channels (one-time setup)
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
```

#### Core Tools (Available via Conda)

```bash
# Create main phylogenomics environment
conda create -n phylogenomics -c conda-forge -c bioconda \
    compleasm \
    mafft \
    iqtree \
    trimal \
    bmge \
    clipkit \
    astral-tree \
    perl \
    perl-bioperl \
    python=3.9 \
    biopython

conda activate phylogenomics
```

**Individual installations** (if you prefer separate environments):

```bash
# Ortholog detection
conda create -n compleasm -c conda-forge -c bioconda compleasm
# Alternative: BUSCO
conda create -n busco -c conda-forge -c bioconda busco

# Alignment
conda create -n mafft -c conda-forge -c bioconda mafft

# Trimming tools (choose one or more)
conda create -n trimal -c bioconda trimal
conda create -n bmge -c bioconda bmge
conda create -n clipkit -c bioconda clipkit

# Phylogenetic inference
conda create -n iqtree -c bioconda iqtree
conda create -n astral -c bioconda astral-tree

# NCBI data download
conda create -n ncbi -c conda-forge ncbi-datasets-cli
```

#### Platform-Specific Notes

**macOS (Intel and Apple Silicon):**
- Most tools work natively on Intel Macs
- Apple Silicon (M1/M2/M3) may require Rosetta 2 for some packages
- If you encounter issues, use: `CONDA_SUBDIR=osx-64 conda create -n myenv ...`

**Linux:**
- All tools work natively
- HPC systems: Use `module load conda` or install Miniforge in your home directory

### Manual Installation (Tools NOT in Conda)

Some tools require manual download and setup within your conda environment.

#### 1. Aliscore and ALICUT

Aliscore and ALICUT are Perl scripts that need to be installed into your conda environment.

**Installation:**

```bash
# Activate your environment first
conda activate phylogenomics

# Create temporary download directory
mkdir -p /tmp/phylo_downloads
cd /tmp/phylo_downloads

# Download Aliscore scripts
wget https://raw.githubusercontent.com/PatrickKueck/AliCUT/master/Aliscore.02.2.pl
wget https://raw.githubusercontent.com/PatrickKueck/AliCUT/master/Aliscore_module.pm

# Download ALICUT
wget https://raw.githubusercontent.com/PatrickKueck/AliCUT/master/ALICUT_V2.31.pl

# Install into conda environment bin directory
mkdir -p $CONDA_PREFIX/bin
cp Aliscore.02.2.pl $CONDA_PREFIX/bin/
cp Aliscore_module.pm $CONDA_PREFIX/bin/
cp ALICUT_V2.31.pl $CONDA_PREFIX/bin/

# Make scripts executable
chmod +x $CONDA_PREFIX/bin/Aliscore.02.2.pl
chmod +x $CONDA_PREFIX/bin/ALICUT_V2.31.pl

# Create convenient wrapper scripts without .pl extension
cat > $CONDA_PREFIX/bin/aliscore <<'EOF'
#!/bin/bash
perl $(dirname $0)/Aliscore.02.2.pl "$@"
EOF

cat > $CONDA_PREFIX/bin/alicut <<'EOF'
#!/bin/bash
perl $(dirname $0)/ALICUT_V2.31.pl "$@"
EOF

chmod +x $CONDA_PREFIX/bin/aliscore
chmod +x $CONDA_PREFIX/bin/alicut

# Cleanup
cd ~
rm -rf /tmp/phylo_downloads
```

**Verify installation:**

```bash
# Test with wrapper commands
aliscore
alicut -h

# Or call Perl scripts directly
perl $CONDA_PREFIX/bin/Aliscore.02.2.pl
perl $CONDA_PREFIX/bin/ALICUT_V2.31.pl -h
```

**Note:** The Aliscore_module.pm must be in the same directory as Aliscore.02.2.pl. Since both are installed to `$CONDA_PREFIX/bin`, this is handled automatically.

#### 2. FASconCAT-G

FASconCAT-G is a Perl script for concatenating multiple sequence alignments.

**Installation:**

```bash
# Activate your environment
conda activate phylogenomics

# Create temporary download directory
mkdir -p /tmp/phylo_downloads
cd /tmp/phylo_downloads

# Download FASconCAT-G
wget https://raw.githubusercontent.com/PatrickKueck/FASconCAT-G/master/FASconCAT-G_v1.06.1.pl

# Install into conda environment bin directory
mkdir -p $CONDA_PREFIX/bin
cp FASconCAT-G_v1.06.1.pl $CONDA_PREFIX/bin/

# Make executable
chmod +x $CONDA_PREFIX/bin/FASconCAT-G_v1.06.1.pl

# Create convenient wrapper script
cat > $CONDA_PREFIX/bin/fasconcat <<'EOF'
#!/bin/bash
perl $(dirname $0)/FASconCAT-G_v1.06.1.pl "$@"
EOF

chmod +x $CONDA_PREFIX/bin/fasconcat

# Cleanup
cd ~
rm -rf /tmp/phylo_downloads
```

**Verify installation:**

```bash
# Test with wrapper command
fasconcat
# Should display the interactive menu

# Or call Perl script directly
perl $CONDA_PREFIX/bin/FASconCAT-G_v1.06.1.pl
```

#### 3. IQ-TREE (Alternative: Direct Binary Download)

While IQ-TREE is available via conda, you may want the latest version directly from GitHub.

**Installation (Linux):**

```bash
conda activate phylogenomics

# Create temporary download directory
mkdir -p /tmp/phylo_downloads
cd /tmp/phylo_downloads

# Download and extract
wget https://github.com/iqtree/iqtree2/releases/download/v2.3.6/iqtree-2.3.6-Linux-intel.tar.gz
tar -xzf iqtree-2.3.6-Linux-intel.tar.gz

# Install binaries into conda environment
mkdir -p $CONDA_PREFIX/bin
cp iqtree-2.3.6-Linux-intel/bin/iqtree2 $CONDA_PREFIX/bin/
chmod +x $CONDA_PREFIX/bin/iqtree2

# Create symlink for version-agnostic usage
ln -sf $CONDA_PREFIX/bin/iqtree2 $CONDA_PREFIX/bin/iqtree

# Cleanup
cd ~
rm -rf /tmp/phylo_downloads
```

**Installation (macOS Intel):**

```bash
conda activate phylogenomics

mkdir -p /tmp/phylo_downloads
cd /tmp/phylo_downloads

# Download and extract
wget https://github.com/iqtree/iqtree2/releases/download/v2.3.6/iqtree-2.3.6-macOS-intel.tar.gz
tar -xzf iqtree-2.3.6-macOS-intel.tar.gz

# Install into conda environment
mkdir -p $CONDA_PREFIX/bin
cp iqtree-2.3.6-macOS-intel/bin/iqtree2 $CONDA_PREFIX/bin/
chmod +x $CONDA_PREFIX/bin/iqtree2

# Create symlink for version-agnostic usage
ln -sf $CONDA_PREFIX/bin/iqtree2 $CONDA_PREFIX/bin/iqtree

# Cleanup
cd ~
rm -rf /tmp/phylo_downloads
```

**Installation (macOS Apple Silicon):**

```bash
conda activate phylogenomics

mkdir -p /tmp/phylo_downloads
cd /tmp/phylo_downloads

# Download and extract
wget https://github.com/iqtree/iqtree2/releases/download/v2.3.6/iqtree-2.3.6-macOS-arm.tar.gz
tar -xzf iqtree-2.3.6-macOS-arm.tar.gz

# Install into conda environment
mkdir -p $CONDA_PREFIX/bin
cp iqtree-2.3.6-macOS-arm/bin/iqtree2 $CONDA_PREFIX/bin/
chmod +x $CONDA_PREFIX/bin/iqtree2

# Create symlink for version-agnostic usage
ln -sf $CONDA_PREFIX/bin/iqtree2 $CONDA_PREFIX/bin/iqtree

# Cleanup
cd ~
rm -rf /tmp/phylo_downloads
```

**Verify installation:**

```bash
iqtree --version
# or
iqtree2 --version
```

#### 4. ASTRAL (Alternative: Direct JAR Download)

While ASTRAL is available via conda, you can also install the JAR file directly.

**Installation:**

```bash
conda activate phylogenomics

# Create temporary download directory
mkdir -p /tmp/phylo_downloads
cd /tmp/phylo_downloads

# Download ASTRAL
wget https://github.com/smirarab/ASTRAL/raw/master/Astral.5.7.8.zip
unzip Astral.5.7.8.zip

# Install JAR file into conda environment
mkdir -p $CONDA_PREFIX/share/astral
cp Astral/astral.5.7.8.jar $CONDA_PREFIX/share/astral/
cp -r Astral/lib $CONDA_PREFIX/share/astral/ 2>/dev/null || true

# Create wrapper script
cat > $CONDA_PREFIX/bin/astral-jar <<'EOF'
#!/bin/bash
java -jar $CONDA_PREFIX/share/astral/astral.5.7.8.jar "$@"
EOF

chmod +x $CONDA_PREFIX/bin/astral-jar

# Cleanup
cd ~
rm -rf /tmp/phylo_downloads
```

**Verify installation:**

```bash
astral-jar -h
```

**Note:** This creates an `astral-jar` command to avoid conflicts with the conda `astral` package if both are installed.

### Verification Script

Create a script to verify all installations:

```bash
#!/bin/bash
# verify_installations.sh

echo "=============================================="
echo "Phylogenomics Tools Installation Verification"
echo "=============================================="
echo ""
echo "Conda environment: $CONDA_PREFIX"
echo ""

# Function to check command
check_cmd() {
    if command -v $1 &> /dev/null; then
        version=$($1 --version 2>&1 | head -n 1 || echo "installed")
        echo "✓ $1 is installed ($version)"
        return 0
    else
        echo "✗ $1 is NOT installed"
        return 1
    fi
}

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo "✓ $2 is installed at $1"
        return 0
    else
        echo "✗ $2 is NOT installed"
        return 1
    fi
}

echo "Conda-installed tools:"
echo "----------------------"
check_cmd compleasm
check_cmd mafft
check_cmd trimal
check_cmd bmge
check_cmd clipkit
check_cmd iqtree || check_cmd iqtree2
check_cmd astral

echo ""
echo "Manually-installed Perl scripts:"
echo "---------------------------------"

# Check Aliscore
if command -v aliscore &> /dev/null; then
    echo "✓ Aliscore is available (wrapper: aliscore)"
    check_file "$CONDA_PREFIX/bin/Aliscore.02.2.pl" "  Aliscore.02.2.pl"
    check_file "$CONDA_PREFIX/bin/Aliscore_module.pm" "  Aliscore_module.pm"
elif [ -f "$CONDA_PREFIX/bin/Aliscore.02.2.pl" ]; then
    echo "✓ Aliscore.02.2.pl is installed (no wrapper)"
else
    echo "✗ Aliscore is NOT installed"
fi

# Check ALICUT
if command -v alicut &> /dev/null; then
    echo "✓ ALICUT is available (wrapper: alicut)"
    check_file "$CONDA_PREFIX/bin/ALICUT_V2.31.pl" "  ALICUT_V2.31.pl"
elif [ -f "$CONDA_PREFIX/bin/ALICUT_V2.31.pl" ]; then
    echo "✓ ALICUT_V2.31.pl is installed (no wrapper)"
else
    echo "✗ ALICUT is NOT installed"
fi

# Check FASconCAT-G
if command -v fasconcat &> /dev/null; then
    echo "✓ FASconCAT-G is available (wrapper: fasconcat)"
    check_file "$CONDA_PREFIX/bin/FASconCAT-G_v1.06.1.pl" "  FASconCAT-G_v1.06.1.pl"
elif [ -f "$CONDA_PREFIX/bin/FASconCAT-G_v1.06.1.pl" ]; then
    echo "✓ FASconCAT-G_v1.06.1.pl is installed (no wrapper)"
else
    echo "✗ FASconCAT-G is NOT installed"
fi

echo ""
echo "Alternative installations:"
echo "--------------------------"

# Check manually installed IQ-TREE
if [ -f "$CONDA_PREFIX/bin/iqtree2" ] && [ ! -L "$CONDA_PREFIX/bin/iqtree2" ]; then
    echo "✓ IQ-TREE2 binary (manually installed)"
    if [ -L "$CONDA_PREFIX/bin/iqtree" ]; then
        echo "  ✓ iqtree symlink present"
    fi
fi

# Check manually installed ASTRAL
if command -v astral-jar &> /dev/null; then
    echo "✓ ASTRAL JAR (manually installed, command: astral-jar)"
    check_file "$CONDA_PREFIX/share/astral/astral.5.7.8.jar" "  astral.5.7.8.jar"
fi

echo ""
echo "=============================================="
echo "Verification complete!"
echo "=============================================="
```

**Save and run:**

```bash
# Save the script
cat > verify_installations.sh <<'SCRIPT'
# ... paste the script above ...
SCRIPT

chmod +x verify_installations.sh

# Run it
./verify_installations.sh
```

### Troubleshooting

**Problem: Conda is slow**
- Solution: Use `mamba` instead: `conda install -n base mamba -c conda-forge`
- Then use `mamba` instead of `conda` for all installations

**Problem: Perl script can't find modules**
```bash
# Install additional Perl dependencies
conda install -c bioconda perl-bioperl perl-file-copy-recursive
```

**Problem: Java not found for ASTRAL**
```bash
conda install -c conda-forge openjdk
```

**Problem: Permission denied on HPC**
```bash
# Install Miniforge in home directory
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3
source $HOME/miniforge3/etc/profile.d/conda.sh
```

**Problem: Apple Silicon compatibility**
```bash
# Force x86_64 architecture
CONDA_SUBDIR=osx-64 conda create -n phylogenomics ...
conda activate phylogenomics
conda config --env --set subdir osx-64
```

---

## Docker Container Specification

If using Docker, here's a complete Dockerfile with all tools:

```dockerfile
FROM mambaorg/micromamba:latest

LABEL maintainer="Bruno de Medeiros <Field Museum>"
LABEL description="Complete environment for BUSCO-based phylogenomics"

# Install all phylogenomics tools
RUN micromamba install -y -n base -c conda-forge -c bioconda \
    compleasm \
    busco \
    mafft \
    trimal \
    bmge \
    clipkit \
    iqtree \
    ncbi-datasets-cli \
    python=3.9 \
    biopython \
    perl \
    openjdk \
    wget \
    unzip \
    && micromamba clean --all --yes

# Set working directory
WORKDIR /data

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]
CMD ["/bin/bash"]
```

Build and run:
```bash
docker build -t phylogenomics:latest .
docker run -v $(pwd):/data -it phylogenomics:latest
```

---

## Substitution Model Recommendation Detailed Guide

This section provides the detailed decision matrix and recommendation process for IQ-TREE substitution model selection.

### Model Recommendation Matrix

#### For Nuclear Proteins (most phylogenomics workflows)

**Deep Phylogeny (class+ level), Many Taxa (>50)**:
1. **LG+F+G4** or **LG+F+R** - Best general model, widely used
2. **WAG+F+G4** - Alternative general model
3. **LG4X** or **LG4M** - Mixture models for heterogeneity
4. **Q.pfam+F+G4** - Database-derived, broad taxonomic sampling
5. **JTT+F+G4** - Classical alternative

**Moderate Phylogeny (family/order level), Moderate Taxa (20-50)**:
1. **LG+F+G4** - Top choice for most analyses
2. **WAG+F+G4** - Reliable alternative
3. **JTT+F+G4** - Classical model
4. **Q.pfam+F+G4** - Database-derived option

**Shallow Phylogeny (species/genus level), Few Taxa (<20)**:
1. **LG+F+G4** - Still recommended default
2. **WAG+F+G4** - Good alternative
3. **JTT+F+G4** - Classical option

#### Taxonomically-Targeted Models

When applicable, use these taxonomically-specific models:

- **Birds**: Q.bird+F+G4
- **Mammals**: Q.mammal+F+G4, mtMAM (if mtDNA)
- **Insects**: Q.insect+F+G4, mtART (if mtDNA)
- **Plants**: Q.plant+F+G4, cpREV (if chloroplast)
- **Yeasts/Fungi**: Q.yeast+F+G4

#### Model Notation Explained

- **LG, WAG, JTT**: Empirical exchange rate matrix name
- **+F**: Use empirical amino acid frequencies from data (recommended)
- **+G4**: Gamma model with 4 rate categories for among-site rate variation
- **+R**: FreeRate model (alternative to Gamma, often better but slower)

### Presenting Model Recommendations

Format recommendations like this:

```markdown
### Recommended Substitution Models for Your Dataset

Based on your dataset ([NUMBER] taxa, [TAXONOMIC_SCOPE] phylogenetic breadth, [SEQUENCE_TYPE]):

**Primary Recommendations** (use all in model testing):

1. **LG+F+G4**
   - **Why**: Most widely used modern AA model, performs well across diverse datasets
   - **Citations**: Proven effective in numerous phylogenomic studies

2. **WAG+F+G4**
   - **Why**: Excellent general-purpose alternative, often comparable to LG
   - **Use case**: Good backup if LG shows poor fit

3. **JTT+F+G4**
   - **Why**: Classical model still widely used, allows comparison with older studies
   - **Use case**: Historical comparisons

[Add 2-3 more specific to their data...]

**For IQ-TREE Step 8A**, we'll use these models in the partition search:
```bash
-mset LG,WAG,JTT,Q.pfam  # Model set for testing
-m TESTMERGEONLY          # Test models and merge partitions
```

**For Step 8C (gene trees)**, we'll use:
```bash
-m MFP  # Model Finder Plus (tests models from our set)
```

Would you like to:
1. ✓ Use these recommended models (recommended)
2. Specify a custom model set
3. Let me fetch more information about your specific taxonomic group
```

---

## Ortholog Identification Implementation

This section provides detailed implementation scripts for Step 2 (compleasm).

### Threading Allocation Table

| Total Cores | First Genome | Subsequent Genomes | Concurrent Jobs | Threads/Job |
|-------------|--------------|-------------------|-----------------|-------------|
| 8           | 8 threads    | 8 threads (serial)| 1               | 8           |
| 16          | 16 threads   | 8 threads         | 2               | 8           |
| 32          | 32 threads   | 8 threads         | 4               | 8           |
| 64          | 64 threads   | 16 threads        | 4               | 16          |
| 128         | 128 threads  | 16-32 threads     | 4-8             | 16          |

### SLURM Implementation (Option A: Optimized Parallel)

**First genome job** (`run_compleasm_first.job`):
```bash
#!/bin/bash
#SBATCH --job-name=compleasm_first
#SBATCH --cpus-per-task=TOTAL_THREADS  # Replace with all available cores
#SBATCH --mem-per-cpu=6G
#SBATCH --time=24:00:00
#SBATCH --output=logs/compleasm_first.%j.out
#SBATCH --error=logs/compleasm_first.%j.err

source ~/.bashrc
conda activate phylo

mkdir -p logs

# Process first genome only (downloads lineage database)
first_genome=$(head -n 1 genome_list.txt)
genome_name=$(basename ${first_genome} .fasta)

echo "Processing first genome: ${genome_name}"
echo "This will download the BUSCO lineage database..."

compleasm run \
  -a ${first_genome} \
  -o ${genome_name}_compleasm \
  -l LINEAGE \
  -t ${SLURM_CPUS_PER_TASK}

echo "First genome complete. Database downloaded."
echo "Ready to process remaining genomes in parallel."
```

**Parallel genomes job** (`run_compleasm_parallel.job`):
```bash
#!/bin/bash
#SBATCH --job-name=compleasm_parallel
#SBATCH --array=2-NUM_GENOMES  # Replace NUM_GENOMES with count
#SBATCH --cpus-per-task=THREADS_PER_JOB  # Replace based on table above
#SBATCH --mem-per-cpu=6G
#SBATCH --time=48:00:00
#SBATCH --output=logs/compleasm.%A_%a.out
#SBATCH --error=logs/compleasm.%A_%a.err

source ~/.bashrc
conda activate phylo

# Get genome for this array task
genome=$(sed -n "${SLURM_ARRAY_TASK_ID}p" genome_list.txt)
genome_name=$(basename ${genome} .fasta)

echo "Processing genome ${SLURM_ARRAY_TASK_ID}: ${genome_name}"

compleasm run \
  -a ${genome} \
  -o ${genome_name}_compleasm \
  -l LINEAGE \
  -t ${SLURM_CPUS_PER_TASK}

echo "Completed: ${genome_name}"
```

### PBS Implementation (Option A: Optimized Parallel)

Similar structure to SLURM, but with PBS directives. See templates in `templates/pbs/`.

### Local Implementation (Option A: Optimized Parallel)

**First genome script** (`run_compleasm_first.sh`):
```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

TOTAL_THREADS=TOTAL_THREADS  # Replace with total cores to use

mkdir -p logs

# Process first genome only
first_genome=$(head -n 1 genome_list.txt)
genome_name=$(basename ${first_genome} .fasta)

echo "Processing first genome: ${genome_name}"
echo "Using ${TOTAL_THREADS} threads"
echo "This will download the BUSCO lineage database..."

compleasm run \
  -a ${first_genome} \
  -o ${genome_name}_compleasm \
  -l LINEAGE \
  -t ${TOTAL_THREADS} 2>&1 | tee logs/compleasm_first.log

echo "First genome complete!"
```

**Parallel genomes script** (`run_compleasm_parallel.sh`):
```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

TOTAL_THREADS=TOTAL_THREADS      # Replace with total cores available
THREADS_PER_JOB=THREADS_PER_JOB  # Replace based on table above
CONCURRENT_JOBS=$((TOTAL_THREADS / THREADS_PER_JOB))

echo "Parallel compleasm processing"
echo "Total threads: ${TOTAL_THREADS}"
echo "Threads per genome: ${THREADS_PER_JOB}"
echo "Concurrent genomes: ${CONCURRENT_JOBS}"
echo ""

mkdir -p logs

# Process genomes 2-end in parallel using GNU parallel
tail -n +2 genome_list.txt | parallel -j ${CONCURRENT_JOBS} '
  genome_name=$(basename {} .fasta)
  echo "Processing: ${genome_name}"

  compleasm run \
    -a {} \
    -o ${genome_name}_compleasm \
    -l LINEAGE \
    -t THREADS_PER_JOB 2>&1 | tee logs/compleasm_${genome_name}.log

  echo "Completed: ${genome_name}"
'

echo ""
echo "All genomes processed!"
```

### Simple Serial Implementation (All Platforms)

For users who prefer simplicity over optimization:

**SLURM** (`run_compleasm_serial.job`):
```bash
#!/bin/bash
#SBATCH --job-name=compleasm_serial
#SBATCH --cpus-per-task=THREADS
#SBATCH --mem-per-cpu=6G
#SBATCH --time=72:00:00
#SBATCH --output=logs/compleasm.%j.out

source ~/.bashrc
conda activate phylo

mkdir -p logs

while read genome; do
  genome_name=$(basename ${genome} .fasta)
  echo "Processing ${genome_name}..."

  compleasm run \
    -a ${genome} \
    -o ${genome_name}_compleasm \
    -l LINEAGE \
    -t ${SLURM_CPUS_PER_TASK}
done < genome_list.txt

echo "All genomes processed!"
```

---

## Alignment Implementation

This section provides detailed implementation scripts for Step 5 (MAFFT alignment).

### SLURM Array Job

```bash
#!/bin/bash
#SBATCH --job-name=mafft_array
#SBATCH --array=1-NUM_LOCI  # Replace with actual number
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%A_%a.mafft.out
#SBATCH --error=logs/%A_%a.mafft.err

source ~/.bashrc
conda activate phylo

cd single_copy_orthologs/unaligned_aa
mkdir -p ../aligned_aa

locus=$(sed -n "${SLURM_ARRAY_TASK_ID}p" locus_names.txt)
output=$(basename ${locus} .fas)_aligned.fas

echo "Aligning: ${locus}"

mafft-linsi ${locus} > ../aligned_aa/${output}

echo "Completed: ${output}"
```

### PBS Array Job

```bash
#!/bin/bash
#PBS -N mafft_array
#PBS -t 1-NUM_LOCI
#PBS -l nodes=1:ppn=1
#PBS -l mem=4gb
#PBS -l walltime=24:00:00

cd $PBS_O_WORKDIR/single_copy_orthologs/unaligned_aa
source ~/.bashrc
conda activate phylo

mkdir -p ../aligned_aa

locus=$(sed -n "${PBS_ARRAYID}p" locus_names.txt)
output=$(basename ${locus} .fas)_aligned.fas

mafft-linsi ${locus} > ../aligned_aa/${output}
```

### Local Sequential

```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

cd single_copy_orthologs/unaligned_aa
mkdir -p ../aligned_aa

while read locus; do
  output=$(basename ${locus} .fas)_aligned.fas
  echo "Aligning ${locus}..."

  mafft-linsi ${locus} > ../aligned_aa/${output}
done < locus_names.txt

echo "All alignments complete!"
```

### Local Parallel (GNU parallel)

```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

cd single_copy_orthologs/unaligned_aa
mkdir -p ../aligned_aa

CONCURRENT_JOBS=4  # Adjust based on available cores

cat locus_names.txt | parallel -j ${CONCURRENT_JOBS} '
  output=$(basename {} .fas)_aligned.fas
  echo "Aligning: {}"
  mafft-linsi {} > ../aligned_aa/${output}
  echo "Completed: ${output}"
'

echo "All alignments complete!"
```

---

## Alignment Trimming Implementation

This section provides detailed implementation scripts for Step 6 (alignment trimming) using all supported methods.

### trimAl Implementation

**SLURM Array Job**:
```bash
#!/bin/bash
#SBATCH --job-name=trimal_array
#SBATCH --array=1-NUM_LOCI
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2G
#SBATCH --time=2:00:00
#SBATCH --output=logs/%A_%a.trimal.out

source ~/.bashrc
conda activate phylo

cd aligned_aa
mkdir -p ../trimmed_aa
ls *.fas > aligned_loci.txt

locus=$(sed -n "${SLURM_ARRAY_TASK_ID}p" aligned_loci.txt)
output=$(basename ${locus} _aligned.fas)_trimmed.fas

trimal -in ${locus} -out ../trimmed_aa/${output} -automated1
```

**PBS Array Job**:
```bash
#!/bin/bash
#PBS -N trimal_array
#PBS -t 1-NUM_LOCI
#PBS -l nodes=1:ppn=1
#PBS -l mem=2gb
#PBS -l walltime=2:00:00

cd $PBS_O_WORKDIR/aligned_aa
source ~/.bashrc
conda activate phylo

mkdir -p ../trimmed_aa
ls *.fas > aligned_loci.txt

locus=$(sed -n "${PBS_ARRAYID}p" aligned_loci.txt)
output=$(basename ${locus} _aligned.fas)_trimmed.fas

trimal -in ${locus} -out ../trimmed_aa/${output} -automated1
```

**Local with GNU parallel**:
```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

cd aligned_aa
mkdir -p ../trimmed_aa

cat aligned_loci.txt | parallel -j 4 '
  output=$(basename {} _aligned.fas)_trimmed.fas
  trimal -in {} -out ../trimmed_aa/${output} -automated1
  echo "Trimmed: ${output}"
'
```

### ClipKit Implementation

**SLURM Array Job**:
```bash
#!/bin/bash
#SBATCH --job-name=clipkit_array
#SBATCH --array=1-NUM_LOCI
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2G
#SBATCH --time=2:00:00
#SBATCH --output=logs/%A_%a.clipkit.out

source ~/.bashrc
conda activate phylo

cd aligned_aa
mkdir -p ../trimmed_aa

locus=$(sed -n "${SLURM_ARRAY_TASK_ID}p" aligned_loci.txt)
output=$(basename ${locus} _aligned.fas)_trimmed.fas

clipkit ${locus} -o ../trimmed_aa/${output}
```

**Local with GNU parallel**:
```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

cd aligned_aa
mkdir -p ../trimmed_aa

cat aligned_loci.txt | parallel -j 4 '
  output=$(basename {} _aligned.fas)_trimmed.fas
  clipkit {} -o ../trimmed_aa/${output}
'
```

### BMGE Implementation

**SLURM Array Job**:
```bash
#!/bin/bash
#SBATCH --job-name=bmge_array
#SBATCH --array=1-NUM_LOCI
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2G
#SBATCH --time=2:00:00
#SBATCH --output=logs/%A_%a.bmge.out

source ~/.bashrc
conda activate phylo

cd aligned_aa
mkdir -p ../trimmed_aa

locus=$(sed -n "${SLURM_ARRAY_TASK_ID}p" aligned_loci.txt)
output=$(basename ${locus} _aligned.fas)_trimmed.fas

bmge -i ${locus} -t AA -o ../trimmed_aa/${output}
```

**Local with GNU parallel**:
```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

cd aligned_aa
mkdir -p ../trimmed_aa

cat aligned_loci.txt | parallel -j 4 '
  output=$(basename {} _aligned.fas)_trimmed.fas
  bmge -i {} -t AA -o ../trimmed_aa/${output}
'
```

---

## Partition Model Selection Implementation

This section provides detailed implementation scripts for Step 8A (IQ-TREE partition model selection).

### SLURM Implementation

```bash
#!/bin/bash
#SBATCH --job-name=partition_search
#SBATCH --cpus-per-task=18
#SBATCH --mem-per-cpu=4G
#SBATCH --time=72:00:00
#SBATCH --output=logs/partition_search.%j.out
#SBATCH --error=logs/partition_search.%j.err

source ~/.bashrc
conda activate phylo

cd trimmed_aa

echo "Starting partition model selection..."
echo "Using model set: MODEL_SET"
echo "Threads: ${SLURM_CPUS_PER_TASK}"

iqtree \
  -s FcC_supermatrix.fas \
  -spp partition_def.txt \
  -m TESTMERGEONLY \
  -mset MODEL_SET \
  -msub nuclear \
  -rcluster 10 \
  -bb 1000 \
  -alrt 1000 \
  -nt ${SLURM_CPUS_PER_TASK} \
  -safe \
  -pre partition_search

echo "Partition search complete!"
echo "Best scheme: partition_search.best_scheme.nex"
```

### PBS Implementation

```bash
#!/bin/bash
#PBS -N partition_search
#PBS -l nodes=1:ppn=18
#PBS -l mem=72gb
#PBS -l walltime=72:00:00

cd $PBS_O_WORKDIR/trimmed_aa
source ~/.bashrc
conda activate phylo

iqtree \
  -s FcC_supermatrix.fas \
  -spp partition_def.txt \
  -m TESTMERGEONLY \
  -mset MODEL_SET \
  -msub nuclear \
  -rcluster 10 \
  -bb 1000 \
  -alrt 1000 \
  -nt 18 \
  -safe \
  -pre partition_search
```

### Local Implementation

```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

cd trimmed_aa

THREADS=18  # Adjust based on available cores

echo "Starting partition model selection..."
echo "Using ${THREADS} threads"

iqtree \
  -s FcC_supermatrix.fas \
  -spp partition_def.txt \
  -m TESTMERGEONLY \
  -mset MODEL_SET \
  -msub nuclear \
  -rcluster 10 \
  -bb 1000 \
  -alrt 1000 \
  -nt ${THREADS} \
  -safe \
  -pre partition_search

echo "Partition search complete!"
```

### Parameter Explanations

- `-m TESTMERGEONLY`: Test models and merge partitions with same best model
- `-mset MODEL_SET`: Test only specified models (e.g., "LG,WAG,JTT,Q.pfam")
- `-msub nuclear`: Rate heterogeneity appropriate for nuclear genes
- `-rcluster 10`: Merge similar partitions (10% relaxed clustering)
- `-bb 1000`: 1000 ultrafast bootstrap replicates
- `-alrt 1000`: 1000 SH-aLRT replicates (additional branch support)
- `-safe`: Safe numerical mode (slower but more stable)

---

## Gene Trees Implementation

This section provides detailed implementation scripts for Step 8C (individual gene tree estimation).

### SLURM Array Job

```bash
#!/bin/bash
#SBATCH --job-name=gene_trees
#SBATCH --array=1-NUM_LOCI  # Replace with loci count
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=2:00:00
#SBATCH --output=logs/%A_%a.gene_tree.out
#SBATCH --error=logs/%A_%a.gene_tree.err

source ~/.bashrc
conda activate phylo

cd trimmed_aa
ls *_trimmed.fas > locus_list.txt

locus=$(sed -n "${SLURM_ARRAY_TASK_ID}p" locus_list.txt)
prefix=$(basename ${locus} .fas)

echo "Estimating gene tree: ${locus}"

iqtree \
  -s ${locus} \
  -m MFP \
  -bb 1000 \
  -bnni \
  -czb \
  -nt 1 \
  -pre ${prefix}

echo "Completed: ${prefix}.treefile"
```

### PBS Array Job

```bash
#!/bin/bash
#PBS -N gene_trees
#PBS -t 1-NUM_LOCI
#PBS -l nodes=1:ppn=1
#PBS -l mem=4gb
#PBS -l walltime=2:00:00

cd $PBS_O_WORKDIR/trimmed_aa
source ~/.bashrc
conda activate phylo

ls *_trimmed.fas > locus_list.txt

locus=$(sed -n "${PBS_ARRAYID}p" locus_list.txt)
prefix=$(basename ${locus} .fas)

iqtree \
  -s ${locus} \
  -m MFP \
  -bb 1000 \
  -bnni \
  -czb \
  -nt 1 \
  -pre ${prefix}
```

### Local Parallel (GNU parallel)

```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

cd trimmed_aa
ls *_trimmed.fas > locus_list.txt

CONCURRENT_JOBS=4  # Adjust based on available cores

echo "Estimating gene trees in parallel..."
echo "Concurrent jobs: ${CONCURRENT_JOBS}"

cat locus_list.txt | parallel -j ${CONCURRENT_JOBS} '
  prefix=$(basename {} .fas)
  echo "Processing: {}"

  iqtree \
    -s {} \
    -m MFP \
    -bb 1000 \
    -bnni \
    -czb \
    -nt 1 \
    -pre ${prefix} > ${prefix}.log 2>&1

  echo "Completed: ${prefix}.treefile"
'

echo "All gene trees estimated!"
```

### Local Serial

```bash
#!/bin/bash
source ~/.bashrc
conda activate phylo

cd trimmed_aa

echo "Estimating gene trees (serial processing)..."

for locus in *_trimmed.fas; do
  prefix=$(basename ${locus} .fas)
  echo "Processing: ${locus}"

  iqtree \
    -s ${locus} \
    -m MFP \
    -bb 1000 \
    -bnni \
    -czb \
    -nt 1 \
    -pre ${prefix}

  echo "Completed: ${prefix}.treefile"
done

echo "All gene trees estimated!"
```

### Parameter Explanations

- `-m MFP`: Model Finder Plus (automatically select best model)
- `-bb 1000`: 1000 ultrafast bootstrap replicates
- `-bnni`: Reduce NNI iterations to avoid overestimating bootstrap support
- `-czb`: Collapse zero-length branches in final tree
- `-nt 1`: Single thread per gene (parallelize across genes, not within)

---

## Methods Paragraph Template

This section provides the complete methods paragraph template for publications.

Use this template to generate a `METHODS_PARAGRAPH.md` file for users. Customize based on their workflow choices.

```markdown
# Methods Paragraph for Publication

## Phylogenomic Analysis

[Copy and customize the text below for your manuscript]

---

### Ortholog Identification and Quality Control

We identified single-copy orthologs from [NUMBER] genome assemblies using compleasm v[VERSION] (Huang & Li, 2023) with the [LINEAGE_NAME] BUSCO lineage dataset (v[VERSION]). Genomes with completeness scores below [THRESHOLD]% were excluded from downstream analyses. From the retained high-quality genomes, we extracted [NUMBER] single-copy orthologs present in all species.

### Multiple Sequence Alignment and Trimming

Each orthologous gene set was aligned using MAFFT v7 (Katoh & Standley, 2013) with the L-INS-i algorithm for accurate alignment of conserved protein sequences. Aligned sequences were then trimmed to remove ambiguously aligned regions using [TRIMMING_METHOD]:

- **Aliscore/ALICUT**: We used Aliscore v2.2 and ALICUT v2.31 (Kück et al., 2010) to identify and remove randomly similar sequence (RSS) sections. Aliscore identified RSS positions using Monte Carlo resampling with default parameters (window size = 4, treating gaps as ambiguous characters with -N option), and ALICUT removed these positions from the alignments.

- **trimAl**: We employed trimAl v1.4 (Capella-Gutiérrez et al., 2009) with the -automated1 heuristic method to automatically optimize gap threshold selection.

- **BMGE**: We used BMGE v1.12 (Criscuolo & Gribaldo, 2010) with entropy-based trimming for amino acid sequences (option -t AA).

- **ClipKit**: We applied ClipKit v1.3 (Steenwyk et al., 2020) with the default smart-gap mode for phylogenetically informative position selection.

After trimming, alignments containing fewer than [MIN_LENGTH] informative positions were excluded, resulting in [FINAL_NUMBER] high-quality gene alignments.

### Phylogenetic Inference

#### Concatenated Analysis

Trimmed alignments were concatenated into a supermatrix using FASconCAT-G v1.06.1 (Kück & Longo, 2014), yielding a final alignment of [TOTAL_LENGTH] amino acid positions across [NUMBER] partitions. We performed partitioned maximum likelihood (ML) phylogenetic inference using IQ-TREE v2.3 (Minh et al., 2020). The best-fit partitioning scheme and substitution models were selected using ModelFinder (Kalyaanamoorthy et al., 2017) with the TESTMERGEONLY option and [MODEL_SET] model set. Partitions were merged if they shared the same evolutionary model to reduce model complexity. The final tree was inferred using the selected partition scheme, with branch support assessed using 1,000 ultrafast bootstrap replicates (Hoang et al., 2018). To improve accuracy, we used the -bnni option to reduce potential overestimation of bootstrap support.

#### Coalescent-Based Species Tree

To account for incomplete lineage sorting, we also inferred a species tree using the multispecies coalescent model. Individual gene trees were estimated for each of the [NUMBER] alignments using IQ-TREE v2.3 with automatic model selection and 1,000 ultrafast bootstrap replicates. To improve accuracy, we used the -bnni option to reduce potential overestimation of bootstrap support and -czb to collapse zero-length branches. The resulting gene trees were summarized into a species tree using ASTRAL-III v5.7.8 (Zhang et al., 2018), which estimates the species tree topology that agrees with the largest number of quartet trees induced by the gene trees. Branch support was quantified using local posterior probabilities.

### Software and Reproducibility

All analyses were conducted using conda environments (conda v[VERSION]) to ensure reproducibility. Analysis scripts and detailed workflow documentation are available at [GITHUB_URL or supplementary materials].

---

## Complete Reference List

Capella-Gutiérrez, S., Silla-Martínez, J. M., & Gabaldón, T. (2009). trimAl: a tool for automated alignment trimming in large-scale phylogenetic analyses. *Bioinformatics*, 25(15), 1972-1973. https://doi.org/10.1093/bioinformatics/btp348

Criscuolo, A., & Gribaldo, S. (2010). BMGE (Block Mapping and Gathering with Entropy): a new software for selection of phylogenetic informative regions from multiple sequence alignments. *BMC Evolutionary Biology*, 10(1), 210. https://doi.org/10.1186/1471-2148-10-210

Hoang, D. T., Chernomor, O., von Haeseler, A., Minh, B. Q., & Vinh, L. S. (2018). UFBoot2: improving the ultrafast bootstrap approximation. *Molecular Biology and Evolution*, 35(2), 518-522. https://doi.org/10.1093/molbev/msx281

Huang, N., & Li, H. (2023). compleasm: a faster and more accurate reimplementation of BUSCO. *Bioinformatics*, 39(10), btad595. https://doi.org/10.1093/bioinformatics/btad595

Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K., von Haeseler, A., & Jermiin, L. S. (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods*, 14(6), 587-589. https://doi.org/10.1038/nmeth.4285

Katoh, K., & Standley, D. M. (2013). MAFFT multiple sequence alignment software version 7: improvements in performance and usability. *Molecular Biology and Evolution*, 30(4), 772-780. https://doi.org/10.1093/molbev/mst010

Kück, P., & Longo, G. C. (2014). FASconCAT-G: extensive functions for multiple sequence alignment preparations concerning phylogenetic studies. *Frontiers in Zoology*, 11(1), 81. https://doi.org/10.1186/s12983-014-0081-x

Kück, P., Meusemann, K., Dambach, J., Thormann, B., von Reumont, B. M., Wägele, J. W., & Misof, B. (2010). Parametric and non-parametric masking of randomness in sequence alignments can be improved and leads to better resolved trees. *Frontiers in Zoology*, 7(1), 10. https://doi.org/10.1186/1742-9994-7-10

Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution*, 37(5), 1530-1534. https://doi.org/10.1093/molbev/msaa015

Steenwyk, J. L., Buida III, T. J., Li, Y., Shen, X. X., & Rokas, A. (2020). ClipKIT: a multiple sequence alignment trimming software for accurate phylogenomic inference. *PLOS Biology*, 18(12), e3001007. https://doi.org/10.1371/journal.pbio.3001007

Zhang, C., Rabiee, M., Sayyari, E., & Mirarab, S. (2018). ASTRAL-III: polynomial time species tree reconstruction from partially resolved gene trees. *BMC Bioinformatics*, 19(6), 153. https://doi.org/10.1186/s12859-018-2129-y

---

## Instructions for Use

1. **Replace placeholders in brackets** with your actual values:
   - `[NUMBER]`, `[VERSION]`, `[LINEAGE_NAME]`, `[THRESHOLD]`, `[MIN_LENGTH]`, etc.

2. **Remove sections for tools you didn't use**:
   - Delete the trimming method descriptions you didn't use
   - If you only did concatenated OR coalescent analysis, remove the other section

3. **Adjust detail level** based on your target journal:
   - Combine into shorter paragraph for journals with strict word limits
   - Expand with more parameter details for bioinformatics journals

4. **Add to your manuscript**:
   - This goes in your Materials and Methods section
   - Add all references to your bibliography

5. **Update version numbers**:
   - Check actual versions used: `conda list` in your phylo environment
   - Include versions in your methods for reproducibility
```

---

*This reference guide complements the main BUSCO phylogenomics skill and provides detailed technical specifications for implementation.*
