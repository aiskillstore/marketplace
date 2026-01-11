#!/bin/bash
# run_compleasm_parallel.sh
source ~/.bashrc
conda activate phylo

# Threading configuration (adjust based on your system)
TOTAL_THREADS=TOTAL_THREADS      # Total cores to use (e.g., 64)
THREADS_PER_JOB=THREADS_PER_JOB  # Threads per genome (e.g., 16)
CONCURRENT_JOBS=$((TOTAL_THREADS / THREADS_PER_JOB))  # Calculated automatically

echo "Configuration:"
echo "  Total threads:      ${TOTAL_THREADS}"
echo "  Threads per genome: ${THREADS_PER_JOB}"
echo "  Concurrent genomes: ${CONCURRENT_JOBS}"
echo ""

# Create output directory
mkdir -p 01_busco_results

# Process remaining genomes (skip first one) in parallel
tail -n +2 genome_list.txt | parallel -j ${CONCURRENT_JOBS} '
  genome_name=$(basename {} .fasta)
  echo "Processing ${genome_name} with THREADS_PER_JOB threads..."

  compleasm run \
    -a {} \
    -o 01_busco_results/${genome_name}_compleasm \
    -l LINEAGE \
    -t THREADS_PER_JOB
'

echo ""
echo "All genomes processed!"
