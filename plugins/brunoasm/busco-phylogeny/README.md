# BUSCO-based Phylogenomics Skill

A Claude Code skills for phylogenomic analyses, created by Bruno de Medeiros (Field Museum) based on code initially written by Paul Frandsen (Brigham Young University)

It generate a complete phylogenetic workflow from genome assemblies using BUSCO/compleasm-based single-copy orthologs.

**Features:**
- Supports local genome files and NCBI accessions (BioProjects/Assemblies)
- Generates scheduler-specific scripts (SLURM, PBS, cloud, local)
- Uses modern tools (compleasm, MAFFT, IQ-TREE, ASTRAL)
- Multiple alignment trimming options
- Both concatenation and coalescent approaches
- Quality control with recommendations
- Writes a draft methods paragraph describing the pipeline for publications

**Use when you need to:**
- Build phylogenetic trees from multiple genome assemblies
- Extract and align single-copy orthologs across genomes
- Download genomes from NCBI by accession
- Generate ready-to-run scripts for your computing environment

## Installation
See README on the repository root folder for plugin installation.


## Usage

Once installed, simply describe your phylogenomics task:

```
I need to generate a phylogeny from 20 genome assemblies on a SLURM cluster
```

Claude Code will automatically activate the appropriate skill and guide you through the workflow.

## Workflow Overview

The complete phylogenomics pipeline:

1. **Input Preparation** - Download NCBI genomes if needed
2. **Ortholog Identification** - Run compleasm/BUSCO on all genomes
3. **Quality Control** - Assess genome completeness with recommendations
4. **Ortholog Extraction** - Generate per-locus unaligned FASTA files
5. **Alignment** - Align orthologs with MAFFT
6. **Trimming** - Remove poorly aligned regions (Aliscore/ALICUT, trimAl, BMGE, ClipKit)
7. **Concatenation** - Build supermatrix with partition scheme
8. **Phylogenetic Inference** - Generate ML concatenated tree (IQ-TREE), gene trees, and coalescent species tree (ASTRAL)

## Requirements

Claude Code is better than the web interface, since Claude will then help you install all requirements.

The skill generates scripts that install and use:

- **compleasm** or BUSCO - ortholog detection
- **MAFFT** - multiple sequence alignment
- **Aliscore/ALICUT, trimAl, BMGE, or ClipKit** - alignment trimming
- **FASconCAT** - alignment concatenation
- **IQ-TREE** - maximum likelihood phylogenetic inference
- **ASTRAL** - coalescent species tree estimation
- **NCBI Datasets CLI** - genome download (if using NCBI accessions)


## Computing Environments

The skill supports multiple computing environments:

- **SLURM clusters** - generates SBATCH array jobs
- **PBS/Torque clusters** - generates PBS array jobs
- **Local machines** - sequential execution scripts

## Attribution

Created by **Bruno de Medeiros** (Curator of Pollinating Insects, Field Museum) based on phylogenomics tutorials by **Paul Frandsen** (Brigham Young University).

## Citation

If you use this skill for published research, please cite this website and also:

- **compleasm**: Huang, N., & Li, H. (2023). compleasm: a faster and more accurate reimplementation of BUSCO. *Bioinformatics*, 39(10), btad595.
- **MAFFT**: Katoh, K., & Standley, D. M. (2013). MAFFT multiple sequence alignment software version 7. *Molecular Biology and Evolution*, 30(4), 772-780.
- **IQ-TREE**: Minh, B. Q., et al. (2020). IQ-TREE 2: New models and efficient methods for phylogenetic inference. *Molecular Biology and Evolution*, 37(5), 1530-1534.
- **ASTRAL**: Zhang, C., et al. (2018). ASTRAL-III: polynomial time species tree reconstruction. *BMC Bioinformatics*, 19(6), 153.

Plus any trimming tool you use (Aliscore/ALICUT, trimAl, BMGE, or ClipKit).

## License

MIT License - see individual tool licenses for software dependencies.

## Support

For issues or questions:
- Open an issue in this repository
- Contact Bruno de Medeiros at the Field Museum (bdemedeiros@fieldmuseum.org)

## Acknowledgments

Special thanks to Paul Frandsen (BYU) for creating the excellent phylogenomics tutorials that form the foundation of this skill.
