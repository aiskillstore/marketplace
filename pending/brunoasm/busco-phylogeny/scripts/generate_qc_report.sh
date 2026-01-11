#!/bin/bash
# Quality control report generator for compleasm results
#
# Usage: bash generate_qc_report.sh [output_file.csv]
#
# Author: Bruno de Medeiros (Field Museum)
# Based on tutorials by Paul Frandsen (BYU)

OUTPUT_FILE="${1:-qc_report.csv}"

echo "Genome,Complete_SCO,Fragmented,Duplicated,Missing,Completeness(%)" > "${OUTPUT_FILE}"

count=0
for dir in 01_busco_results/*_compleasm; do
  if [ ! -d "${dir}" ]; then
    continue
  fi

  genome=$(basename "${dir}" _compleasm)
  summary="${dir}/summary.txt"

  if [ -f "${summary}" ]; then
    # Parse completeness statistics from compleasm format
    # compleasm uses: S: (single-copy), D: (duplicated), F: (fragmented), M: (missing)
    # Format: "S:80.93%, 2283" where we need the count (2283)
    complete=$(grep "^S:" "${summary}" | awk -F',' '{print $2}' | tr -d ' ')
    duplicated=$(grep "^D:" "${summary}" | awk -F',' '{print $2}' | tr -d ' ')
    fragmented=$(grep "^F:" "${summary}" | awk -F',' '{print $2}' | tr -d ' ')
    missing=$(grep "^M:" "${summary}" | awk -F',' '{print $2}' | tr -d ' ')

    # Check if all values were successfully extracted
    if [ -z "${complete}" ] || [ -z "${fragmented}" ] || [ -z "${missing}" ]; then
      echo "Warning: Could not parse statistics for ${genome}" >&2
      continue
    fi

    # Calculate completeness percentage (Complete / Total * 100)
    total=$((complete + duplicated + fragmented + missing))
    if command -v bc &> /dev/null; then
      completeness=$(echo "scale=2; (${complete} + ${duplicated}) / ${total} * 100" | bc)
    else
      # Fallback if bc not available
      completeness=$(awk "BEGIN {printf \"%.2f\", (${complete} + ${duplicated}) / ${total} * 100}")
    fi

    echo "${genome},${complete},${fragmented},${duplicated},${missing},${completeness}" >> "${OUTPUT_FILE}"
    count=$((count + 1))
  else
    echo "Warning: Summary file not found for ${genome}" >&2
  fi
done

if [ ${count} -eq 0 ]; then
  echo "Error: No compleasm output directories found (*_compleasm)" >&2
  exit 1
fi

echo "QC report generated: ${OUTPUT_FILE}"
echo "Genomes analyzed: ${count}"
