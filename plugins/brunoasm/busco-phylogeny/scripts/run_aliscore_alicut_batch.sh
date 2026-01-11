#!/bin/bash

# run_aliscore_alicut_batch.sh
# Batch processing script for Aliscore + ALICUT alignment trimming
# Processes all alignments in a directory through both tools sequentially
#
# Usage:
#   bash run_aliscore_alicut_batch.sh [alignment_dir] [options]
#
# This script:
#   1. Runs Aliscore on all alignments to identify RSS
#   2. Runs ALICUT on each Aliscore output to remove RSS
#   3. Collects trimmed alignments in output directory
#
# Requirements:
#   - run_aliscore.sh and run_alicut.sh in same directory or PATH
#   - Aliscore.02.2.pl and ALICUT_V2.31.pl available

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to display usage
usage() {
    cat <<EOF
Usage: $0 [alignment_dir] [options]

Batch process multiple alignments through Aliscore and ALICUT.

Arguments:
  alignment_dir   Directory containing aligned FASTA files (*.fas)

Options:
  -o DIR         Output directory for trimmed alignments (default: aliscore_alicut_trimmed)
  -d DIR         Base directory for Aliscore outputs (default: aliscore_output)
  -w INT         Aliscore window size (default: 4)
  -r INT         Aliscore random pairs (default: 4*N)
  -N             Aliscore: treat gaps as ambiguous (recommended for AA)
  --remain-stems ALICUT: remain RNA stem positions
  --remove-codon ALICUT: remove entire codons (for back-translation)
  --remove-3rd   ALICUT: remove only 3rd codon positions
  -h             Display this help message

Examples:
  # Basic usage for amino acid alignments
  bash run_aliscore_alicut_batch.sh aligned_aa/ -N

  # Custom window size
  bash run_aliscore_alicut_batch.sh aligned_aa/ -w 6 -N

  # With RNA structure preservation
  bash run_aliscore_alicut_batch.sh aligned_rrna/ --remain-stems

Output:
  - aliscore_output/aliscore_[locus]/  : Individual Aliscore results per locus
  - aliscore_alicut_trimmed/           : Final trimmed alignments
  - aliscore_alicut_trimmed/trimming_summary.txt : Statistics for all loci

EOF
    exit 0
}

# Default parameters
ALIGNMENT_DIR=""
OUTPUT_DIR="aliscore_alicut_trimmed"
ALISCORE_BASE_DIR="aliscore_output"
ALISCORE_OPTS=""
ALICUT_OPTS="-s"  # Silent mode by default

if [ $# -eq 0 ]; then
    usage
fi

ALIGNMENT_DIR="$1"
shift

# Validate alignment directory
if [ ! -d "${ALIGNMENT_DIR}" ]; then
    echo "ERROR: Alignment directory not found: ${ALIGNMENT_DIR}"
    exit 1
fi

# Parse options
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -d|--aliscore-dir)
            ALISCORE_BASE_DIR="$2"
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
        --remain-stems)
            ALICUT_OPTS="${ALICUT_OPTS} -r"
            shift
            ;;
        --remove-codon)
            ALICUT_OPTS="${ALICUT_OPTS} -c"
            shift
            ;;
        --remove-3rd)
            ALICUT_OPTS="${ALICUT_OPTS} -3"
            shift
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            usage
            ;;
    esac
done

# Check for wrapper scripts
RUN_ALISCORE="${SCRIPT_DIR}/run_aliscore.sh"
RUN_ALICUT="${SCRIPT_DIR}/run_alicut.sh"

if [ ! -f "${RUN_ALISCORE}" ]; then
    echo "ERROR: run_aliscore.sh not found: ${RUN_ALISCORE}"
    exit 1
fi

if [ ! -f "${RUN_ALICUT}" ]; then
    echo "ERROR: run_alicut.sh not found: ${RUN_ALICUT}"
    exit 1
fi

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Find all FASTA files
ALIGNMENTS=($(find "${ALIGNMENT_DIR}" -maxdepth 1 -name "*.fas" -o -name "*.fasta"))

if [ ${#ALIGNMENTS[@]} -eq 0 ]; then
    echo "ERROR: No FASTA files found in ${ALIGNMENT_DIR}"
    exit 1
fi

echo "Found ${#ALIGNMENTS[@]} alignments to process"
echo "Aliscore options: ${ALISCORE_OPTS}"
echo "ALICUT options: ${ALICUT_OPTS}"
echo ""

# Initialize summary file
SUMMARY_FILE="${OUTPUT_DIR}/trimming_summary.txt"
echo -e "Locus\tOriginal_Length\tTrimmed_Length\tRemoved_Positions\tPercent_Removed\tRSS_Count" > "${SUMMARY_FILE}"

# Process each alignment
SUCCESS_COUNT=0
FAIL_COUNT=0

for ALIGNMENT in "${ALIGNMENTS[@]}"; do
    LOCUS=$(basename "${ALIGNMENT}" .fas)
    LOCUS=$(basename "${LOCUS}" .fasta)

    echo "=========================================="
    echo "Processing: ${LOCUS}"
    echo "=========================================="

    # Step 1: Run Aliscore
    echo ""
    echo "Step 1/2: Running Aliscore..."

    if bash "${RUN_ALISCORE}" "${ALIGNMENT}" -d "${ALISCORE_BASE_DIR}" ${ALISCORE_OPTS}; then
        echo "Aliscore completed for ${LOCUS}"
    else
        echo "ERROR: Aliscore failed for ${LOCUS}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    # Step 2: Run ALICUT
    echo ""
    echo "Step 2/2: Running ALICUT..."

    ALISCORE_DIR="${ALISCORE_BASE_DIR}/aliscore_${LOCUS}"

    if [ ! -d "${ALISCORE_DIR}" ]; then
        echo "ERROR: Aliscore output directory not found: ${ALISCORE_DIR}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    if bash "${RUN_ALICUT}" "${ALISCORE_DIR}" ${ALICUT_OPTS}; then
        echo "ALICUT completed for ${LOCUS}"
    else
        echo "ERROR: ALICUT failed for ${LOCUS}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    # Copy trimmed alignment to output directory
    TRIMMED_FILE=$(find "${ALISCORE_DIR}" -name "ALICUT_*.fas" -o -name "ALICUT_*.fasta" | head -n 1)

    if [ -n "${TRIMMED_FILE}" ] && [ -f "${TRIMMED_FILE}" ]; then
        cp "${TRIMMED_FILE}" "${OUTPUT_DIR}/${LOCUS}_trimmed.fas"
        echo "Trimmed alignment: ${OUTPUT_DIR}/${LOCUS}_trimmed.fas"

        # Calculate statistics (handle multi-line FASTA format)
        ORIGINAL_LENGTH=$(awk '/^>/ {if (seq) {print seq; seq=""}; next} {seq = seq $0} END {if (seq) print seq}' "${ALIGNMENT}" | head -n 1 | tr -d ' ' | wc -c)
        TRIMMED_LENGTH=$(awk '/^>/ {if (seq) {print seq; seq=""}; next} {seq = seq $0} END {if (seq) print seq}' "${TRIMMED_FILE}" | head -n 1 | tr -d ' ' | wc -c)
        REMOVED_LENGTH=$((ORIGINAL_LENGTH - TRIMMED_LENGTH))
        PERCENT_REMOVED=$(awk "BEGIN {printf \"%.2f\", (${REMOVED_LENGTH}/${ORIGINAL_LENGTH})*100}")

        # Count RSS positions
        LIST_FILE=$(find "${ALISCORE_DIR}" -name "*_List_*.txt" | head -n 1)
        RSS_COUNT=$(wc -w < "${LIST_FILE}" 2>/dev/null || echo "0")

        # Append to summary
        echo -e "${LOCUS}\t${ORIGINAL_LENGTH}\t${TRIMMED_LENGTH}\t${REMOVED_LENGTH}\t${PERCENT_REMOVED}\t${RSS_COUNT}" >> "${SUMMARY_FILE}"

        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "WARNING: Trimmed file not found for ${LOCUS}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo ""
done

# Final report
echo "=========================================="
echo "BATCH PROCESSING COMPLETE"
echo "=========================================="
echo ""
echo "Successfully processed: ${SUCCESS_COUNT}/${#ALIGNMENTS[@]} alignments"
echo "Failed: ${FAIL_COUNT}/${#ALIGNMENTS[@]} alignments"
echo ""
echo "Output directory: ${OUTPUT_DIR}"
echo "Trimmed alignments: ${OUTPUT_DIR}/*_trimmed.fas"
echo "Summary statistics: ${SUMMARY_FILE}"
echo ""

# Display summary statistics
if [ ${SUCCESS_COUNT} -gt 0 ]; then
    echo "Overall trimming statistics:"
    awk 'NR>1 {
        total_orig += $2;
        total_trim += $3;
        total_removed += $4;
        count++
    }
    END {
        if (count > 0) {
            avg_removed = (total_removed / total_orig) * 100;
            printf "  Total positions before: %d\n", total_orig;
            printf "  Total positions after:  %d\n", total_trim;
            printf "  Total removed:          %d (%.2f%%)\n", total_removed, avg_removed;
            printf "  Average per locus:      %.2f%% removed\n", avg_removed;
        }
    }' "${SUMMARY_FILE}"
fi

echo ""
echo "Done!"
