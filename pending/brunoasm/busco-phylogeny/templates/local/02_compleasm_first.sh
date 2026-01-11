#!/bin/bash
# run_compleasm_first.sh
source ~/.bashrc
conda activate phylo

# User-specified total CPU threads
TOTAL_THREADS=TOTAL_THREADS  # Replace with total cores you want to use (e.g., 16, 32, 64)
echo "Processing first genome with ${TOTAL_THREADS} CPU threads to download lineage database..."

# Create output directory
mkdir -p 01_busco_results

# Process FIRST genome only
first_genome=$(head -n 1 genome_list.txt)
genome_name=$(basename ${first_genome} .fasta)
echo "Processing: ${genome_name}"

compleasm run \
  -a ${first_genome} \
  -o 01_busco_results/${genome_name}_compleasm \
  -l LINEAGE \
  -t ${TOTAL_THREADS}

echo ""
echo "First genome complete! Lineage database is now cached."
echo "Now run the parallel script for remaining genomes: bash run_compleasm_parallel.sh"
