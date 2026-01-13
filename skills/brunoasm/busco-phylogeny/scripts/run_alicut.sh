#!/bin/bash

# run_alicut.sh
# Wrapper script for running ALICUT to remove Aliscore-identified RSS positions
# Removes randomly similar sequence sections from alignments
#
# Usage:
#   bash run_alicut.sh [aliscore_dir] [options]
#
# Options:
#   -r         Remain stem positions (for RNA secondary structures)
#   -c         Remove codon (translate AA positions to nucleotide triplets)
#   -3         Remove only 3rd codon positions
#   -s         Silent mode (non-interactive, use defaults)
#
# Requirements:
#   - ALICUT_V2.31.pl in PATH or same directory
#   - Perl with File::Copy, Tie::File, Term::Cap modules
#   - Aliscore output directory with *_List_*.txt and original .fas file

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for ALICUT script
if command -v ALICUT_V2.31.pl &> /dev/null; then
    ALICUT_SCRIPT="ALICUT_V2.31.pl"
elif [ -f "${SCRIPT_DIR}/ALICUT_V2.31.pl" ]; then
    ALICUT_SCRIPT="${SCRIPT_DIR}/ALICUT_V2.31.pl"
elif [ -f "./ALICUT_V2.31.pl" ]; then
    ALICUT_SCRIPT="./ALICUT_V2.31.pl"
else
    echo "ERROR: ALICUT_V2.31.pl not found in PATH, script directory, or current directory"
    echo "Please download from: https://www.zfmk.de/en/research/research-centres-and-groups/alicut"
    exit 1
fi

# Function to display usage
usage() {
    cat <<EOF
Usage: $0 [aliscore_dir] [options]

Run ALICUT to remove Aliscore-identified randomly similar sequence sections.

Arguments:
  aliscore_dir   Directory containing Aliscore output files

Options:
  -r             Remain stem positions in RNA secondary structure alignments
  -c             Remove entire codon (translates AA RSS positions to nt triplets)
  -3             Remove only 3rd codon position of identified RSS
  -s             Silent/scripted mode (non-interactive, use defaults)
  -h             Display this help message

Input Requirements:
  The aliscore_dir must contain:
    - Original FASTA alignment file (*.fas)
    - Aliscore List file (*_List_random.txt or *_List_*.txt)

Examples:
  # Basic usage (interactive mode)
  bash run_alicut.sh aliscore_alignment1

  # Silent mode with defaults
  bash run_alicut.sh aliscore_alignment1 -s

  # Remain RNA stem positions
  bash run_alicut.sh aliscore_16S -r -s

  # Remove entire codons (for back-translation)
  bash run_alicut.sh aliscore_protein1 -c -s

  # Process all Aliscore output directories
  for dir in aliscore_*/; do
    bash run_alicut.sh "\${dir}" -s
  done

Output Files (in aliscore_dir):
  - ALICUT_[alignment].fas        : Trimmed alignment
  - ALICUT_info.xls               : Statistics (taxa, positions removed, etc.)
  - ALICUT_Struc_info_*.txt       : Structure information (if RNA detected)

Citation:
  Kück P, Meusemann K, Dambach J, Thormann B, von Reumont BM, Wägele JW,
  Misof B (2010) Parametric and non-parametric masking of randomness in
  sequence alignments can be improved and leads to better resolved trees.
  Front Zool 7:10. doi: 10.1186/1742-9994-7-10

EOF
    exit 0
}

# Parse command line arguments
ALISCORE_DIR=""
ALICUT_OPTS=""
SILENT_MODE=false

if [ $# -eq 0 ]; then
    usage
fi

ALISCORE_DIR="$1"
shift

# Validate directory exists
if [ ! -d "${ALISCORE_DIR}" ]; then
    echo "ERROR: Aliscore directory not found: ${ALISCORE_DIR}"
    exit 1
fi

# Parse ALICUT options
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -r)
            ALICUT_OPTS="${ALICUT_OPTS} -r"
            shift
            ;;
        -c)
            ALICUT_OPTS="${ALICUT_OPTS} -c"
            shift
            ;;
        -3)
            ALICUT_OPTS="${ALICUT_OPTS} -3"
            shift
            ;;
        -s|--silent)
            SILENT_MODE=true
            ALICUT_OPTS="${ALICUT_OPTS} -s"
            shift
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            usage
            ;;
    esac
done

# Change to Aliscore output directory
cd "${ALISCORE_DIR}"

echo "Processing Aliscore output in: ${ALISCORE_DIR}"

# Find List file
LIST_FILE=$(ls *_List_*.txt 2>/dev/null | head -n 1)
if [ -z "${LIST_FILE}" ]; then
    echo "ERROR: No Aliscore List file found (*_List_*.txt)"
    echo "Make sure Aliscore completed successfully"
    exit 1
fi

echo "Found List file: ${LIST_FILE}"

# Find original FASTA file
FASTA_FILE=$(find . -maxdepth 1 \( -name "*.fas" -o -name "*.fasta" \) -type f | head -n 1 | sed 's|^\./||')
if [ -z "${FASTA_FILE}" ]; then
    echo "ERROR: No FASTA alignment file found (*.fas or *.fasta)"
    echo "ALICUT requires the original alignment file in the same directory as List file"
    exit 1
fi

echo "Found FASTA file: ${FASTA_FILE}"

# Check if List file contains RSS positions
RSS_COUNT=$(wc -w < "${LIST_FILE}" || echo "0")
if [ "${RSS_COUNT}" -eq 0 ]; then
    echo "WARNING: List file is empty (no RSS positions identified)"
    echo "Aliscore found no randomly similar sequences to remove"
    echo "Skipping ALICUT - alignment is already clean"

    # Create a symbolic link to indicate no trimming was needed
    ln -sf "${FASTA_FILE}" "ALICUT_${FASTA_FILE}"
    echo "Created symbolic link: ALICUT_${FASTA_FILE} -> ${FASTA_FILE}"

    cd ..
    exit 0
fi

echo "Found ${RSS_COUNT} RSS positions to remove"

# Run ALICUT
echo ""
echo "Running ALICUT..."
echo "Options: ${ALICUT_OPTS}"

# Construct ALICUT command
ALICUT_CMD="perl ${ALICUT_SCRIPT} ${ALICUT_OPTS}"

if [ "${SILENT_MODE}" = true ]; then
    echo "Command: ${ALICUT_CMD}"
    eval ${ALICUT_CMD}
else
    echo "Running ALICUT in interactive mode..."
    echo "Press 's' and Enter to start with current options"
    echo ""
    perl "${ALICUT_SCRIPT}" ${ALICUT_OPTS}
fi

# Check if ALICUT completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "ALICUT completed successfully"

    # Find output file
    OUTPUT_FILE=$(ls ALICUT_*.fas ALICUT_*.fasta 2>/dev/null | head -n 1)

    if [ -n "${OUTPUT_FILE}" ]; then
        echo ""
        echo "Output files:"
        ls -lh ALICUT_* 2>/dev/null

        # Calculate and report trimming statistics (handle multi-line FASTA format)
        if [ -f "${OUTPUT_FILE}" ]; then
            ORIGINAL_LENGTH=$(awk '/^>/ {if (seq) {print seq; seq=""}; next} {seq = seq $0} END {if (seq) print seq}' "${FASTA_FILE}" | head -n 1 | wc -c)
            TRIMMED_LENGTH=$(awk '/^>/ {if (seq) {print seq; seq=""}; next} {seq = seq $0} END {if (seq) print seq}' "${OUTPUT_FILE}" | head -n 1 | wc -c)
            REMOVED_LENGTH=$((ORIGINAL_LENGTH - TRIMMED_LENGTH))
            PERCENT_REMOVED=$(awk "BEGIN {printf \"%.1f\", (${REMOVED_LENGTH}/${ORIGINAL_LENGTH})*100}")

            echo ""
            echo "Trimming statistics:"
            echo "  Original length: ${ORIGINAL_LENGTH} bp"
            echo "  Trimmed length:  ${TRIMMED_LENGTH} bp"
            echo "  Removed:         ${REMOVED_LENGTH} bp (${PERCENT_REMOVED}%)"
        fi

        # Check for info file
        if [ -f "ALICUT_info.xls" ]; then
            echo ""
            echo "Detailed statistics in: ALICUT_info.xls"
        fi
    else
        echo "WARNING: Expected output file ALICUT_*.fas not found"
    fi
else
    echo "ERROR: ALICUT failed"
    cd ..
    exit 1
fi

# Return to parent directory
cd ..

echo ""
echo "Done: ${ALISCORE_DIR}"
