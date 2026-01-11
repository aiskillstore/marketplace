#!/bin/bash

# run_aliscore.sh
# Wrapper script for running Aliscore on aligned sequences
# Identifies randomly similar sequence sections (RSS) in multiple sequence alignments
#
# Usage:
#   bash run_aliscore.sh [alignment.fas] [options]
#
# Options:
#   -w INT     Window size (default: 4)
#   -r INT     Number of random pairs to compare (default: 4*N taxa)
#   -N         Treat gaps as ambiguous characters (recommended for amino acids)
#   -t TREE    Tree file in Newick format for guided comparisons
#   -l LEVEL   Node level for tree-based comparisons
#   -o TAXA    Comma-separated list of outgroup taxa
#
# Array job usage:
#   Set SLURM_ARRAY_TASK_ID or PBS_ARRAYID environment variable
#   Create locus_list.txt with one alignment file per line
#
# Requirements:
#   - Aliscore.02.2.pl in PATH or same directory
#   - Perl with Tie::File and Fcntl modules

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for Aliscore script
if command -v Aliscore.02.2.pl &> /dev/null; then
    ALISCORE_SCRIPT="Aliscore.02.2.pl"
elif [ -f "${SCRIPT_DIR}/Aliscore.02.2.pl" ]; then
    ALISCORE_SCRIPT="${SCRIPT_DIR}/Aliscore.02.2.pl"
elif [ -f "./Aliscore.02.2.pl" ]; then
    ALISCORE_SCRIPT="./Aliscore.02.2.pl"
else
    echo "ERROR: Aliscore.02.2.pl not found in PATH, script directory, or current directory"
    echo "Please download from: https://www.zfmk.de/en/research/research-centres-and-groups/aliscore"
    exit 1
fi

# Function to display usage
usage() {
    cat <<EOF
Usage: $0 [alignment.fas] [options]

Run Aliscore to identify randomly similar sequence sections in alignments.

Options:
  -d DIR     Base output directory for all Aliscore results (default: aliscore_output)
  -w INT     Window size for sliding window analysis (default: 4)
  -r INT     Number of random sequence pairs to compare (default: 4*N taxa)
  -N         Treat gaps as ambiguous characters (recommended for amino acids)
  -t FILE    Tree file in Newick format for phylogeny-guided comparisons
  -l LEVEL   Node level limit for tree-based comparisons (default: all)
  -o TAXA    Comma-separated list of outgroup taxa for focused comparisons
  -h         Display this help message

Array Job Mode:
  If SLURM_ARRAY_TASK_ID or PBS_ARRAYID is set, reads alignment from locus_list.txt
  Create locus_list.txt with: ls *.fas > locus_list.txt

Examples:
  # Basic run with defaults (outputs to aliscore_output/)
  bash run_aliscore.sh alignment.fas

  # Amino acid sequences with gaps as ambiguous
  bash run_aliscore.sh protein_alignment.fas -N

  # Custom output directory
  bash run_aliscore.sh alignment.fas -d my_aliscore_results

  # Custom window size and random pairs
  bash run_aliscore.sh alignment.fas -w 6 -r 100

  # Tree-guided analysis
  bash run_aliscore.sh alignment.fas -t species.tre

  # Array job on SLURM
  ls aligned_aa/*.fas > locus_list.txt
  sbatch --array=1-\$(wc -l < locus_list.txt) run_aliscore_array.job

Output Files (in aliscore_output/aliscore_[alignment]/):
  - [alignment]_List_random.txt   : Positions identified as RSS (for ALICUT)
  - [alignment]_Profile_random.txt: Quality profile for each position
  - [alignment].svg               : Visual plot of scoring profiles

Citation:
  Misof B, Misof K (2009) A Monte Carlo approach successfully identifies
  randomness in multiple sequence alignments: a more objective means of data
  exclusion. Syst Biol 58(1):21-34. doi: 10.1093/sysbio/syp006

EOF
    exit 0
}

# Parse command line arguments
ALIGNMENT=""
ALISCORE_OPTS=""
BASE_OUTPUT_DIR="aliscore_output"

if [ $# -eq 0 ]; then
    usage
fi

# Check for array job mode
ARRAY_MODE=false
ARRAY_ID=""

if [ -n "${SLURM_ARRAY_TASK_ID:-}" ]; then
    ARRAY_MODE=true
    ARRAY_ID="${SLURM_ARRAY_TASK_ID}"
elif [ -n "${PBS_ARRAYID:-}" ]; then
    ARRAY_MODE=true
    ARRAY_ID="${PBS_ARRAYID}"
fi

# If in array mode, get alignment from locus list
if [ "${ARRAY_MODE}" = true ]; then
    if [ ! -f "locus_list.txt" ]; then
        echo "ERROR: Array job mode requires locus_list.txt"
        echo "Create with: ls *.fas > locus_list.txt"
        exit 1
    fi

    ALIGNMENT=$(sed -n "${ARRAY_ID}p" locus_list.txt)

    if [ -z "${ALIGNMENT}" ]; then
        echo "ERROR: Could not read alignment for array index ${ARRAY_ID}"
        exit 1
    fi

    echo "Array job ${ARRAY_ID}: Processing ${ALIGNMENT}"

    # Remaining arguments are Aliscore options
    shift $#  # Clear positional parameters
    set -- "$@"  # Reset with remaining args
else
    # First argument is alignment file
    ALIGNMENT="$1"
    shift
fi

# Validate alignment file exists
if [ ! -f "${ALIGNMENT}" ]; then
    echo "ERROR: Alignment file not found: ${ALIGNMENT}"
    exit 1
fi

# Parse Aliscore options
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -d|--output-dir)
            BASE_OUTPUT_DIR="$2"
            shift 2
            ;;
        -w)
            ALISCORE_OPTS="${ALISCORE_OPTS} -w $2"
            shift 2
            ;;
        -r)
            ALISCORE_OPTS="${ALISCORE_OPTS} -r $2"
            shift 2
            ;;
        -N)
            ALISCORE_OPTS="${ALISCORE_OPTS} -N"
            shift
            ;;
        -t)
            if [ ! -f "$2" ]; then
                echo "ERROR: Tree file not found: $2"
                exit 1
            fi
            ALISCORE_OPTS="${ALISCORE_OPTS} -t $2"
            shift 2
            ;;
        -l)
            ALISCORE_OPTS="${ALISCORE_OPTS} -l $2"
            shift 2
            ;;
        -o)
            ALISCORE_OPTS="${ALISCORE_OPTS} -o $2"
            shift 2
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            usage
            ;;
    esac
done

# Get alignment name without extension
ALIGNMENT_NAME=$(basename "${ALIGNMENT}" .fas)
ALIGNMENT_NAME=$(basename "${ALIGNMENT_NAME}" .fasta)

# Create base output directory and specific directory for this alignment
mkdir -p "${BASE_OUTPUT_DIR}"
OUTPUT_DIR="${BASE_OUTPUT_DIR}/aliscore_${ALIGNMENT_NAME}"
mkdir -p "${OUTPUT_DIR}"

# Copy alignment to output directory
cp "${ALIGNMENT}" "${OUTPUT_DIR}/"

# Change to output directory
cd "${OUTPUT_DIR}"

# Run Aliscore
echo "Running Aliscore on ${ALIGNMENT}..."
echo "Options: ${ALISCORE_OPTS}"
echo "Aliscore script: ${ALISCORE_SCRIPT}"

# Construct and run Aliscore command
ALISCORE_CMD="perl -I${SCRIPT_DIR} ${ALISCORE_SCRIPT} -i $(basename ${ALIGNMENT}) ${ALISCORE_OPTS}"
echo "Command: ${ALISCORE_CMD}"

eval ${ALISCORE_CMD}

# Check if Aliscore completed successfully
if [ $? -eq 0 ]; then
    echo "Aliscore completed successfully for ${ALIGNMENT}"

    # List output files
    echo ""
    echo "Output files in ${OUTPUT_DIR}:"
    ls -lh *List*.txt *Profile*.txt *.svg 2>/dev/null || echo "  (some expected files not generated)"

    # Report RSS positions if found
    if [ -f "$(basename ${ALIGNMENT})_List_random.txt" ]; then
        RSS_COUNT=$(wc -w < "$(basename ${ALIGNMENT})_List_random.txt")
        echo ""
        echo "Identified ${RSS_COUNT} randomly similar sequence positions"
        echo "See: ${OUTPUT_DIR}/$(basename ${ALIGNMENT})_List_random.txt"
    fi
else
    echo "ERROR: Aliscore failed for ${ALIGNMENT}"
    cd ..
    exit 1
fi

# Return to parent directory
cd ..

echo "Done: ${ALIGNMENT} -> ${OUTPUT_DIR}"
