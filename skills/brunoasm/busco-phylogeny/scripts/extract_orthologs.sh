#!/bin/bash
# Extract and reorganize single-copy orthologs from compleasm output
#
# Usage: bash extract_orthologs.sh LINEAGE_NAME
#   Example: bash extract_orthologs.sh metazoa
#
# Author: Bruno de Medeiros (Field Museum)
# Based on tutorials by Paul Frandsen (BYU)

if [ $# -lt 1 ]; then
  echo "Usage: bash extract_orthologs.sh LINEAGE_NAME"
  echo "  Example: bash extract_orthologs.sh metazoa"
  exit 1
fi

LINEAGE="$1"

echo "Extracting single-copy orthologs for lineage: ${LINEAGE}"

# Create directory for ortholog FASTA files
mkdir -p single_copy_orthologs

# Copy gene_marker.fasta files and rename by species
count=0
for dir in 01_busco_results/*_compleasm; do
  if [ ! -d "${dir}" ]; then
    continue
  fi

  genome=$(basename "${dir}" _compleasm)

  # Auto-detect the OrthoDB version (odb10, odb11, odb12, etc.)
  odb_dirs=("${dir}/${LINEAGE}_odb"*)
  if [ -d "${odb_dirs[0]}" ]; then
    marker_file="${odb_dirs[0]}/gene_marker.fasta"
  else
    echo "  Warning: No OrthoDB directory found for ${genome}" >&2
    continue
  fi

  if [ -f "${marker_file}" ]; then
    cp "${marker_file}" "single_copy_orthologs/${genome}.fasta"
    echo "  Extracted: ${genome}"
    count=$((count + 1))
  else
    echo "  Warning: Marker file not found for ${genome}" >&2
  fi
done

if [ ${count} -eq 0 ]; then
  echo "Error: No gene_marker.fasta files found. Check lineage name." >&2
  exit 1
fi

echo "Extracted ${count} genomes"
echo ""
echo "Now generating per-locus unaligned FASTA files..."

cd single_copy_orthologs || exit 1
mkdir -p unaligned_aa
cd unaligned_aa || exit 1

# AWK script to split by ortholog ID
awk 'BEGIN{RS=">"; FS="\n"} {
  if (NF > 1) {
    split($1, b, "_");
    fnme = b[1] ".fas";
    n = split(FILENAME, a, "/");
    species = a[length(a)];
    gsub(".fasta", "", species);
    print ">" species "\n" $2 >> fnme;
    close(fnme);
  }
}' ../*.fasta

# Fix headers
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  sed -i '' -e 's/.fasta//g' *.fas
else
  # Linux
  sed -i -e 's/.fasta//g' *.fas
fi

num_loci=$(ls -1 *.fas 2>/dev/null | wc -l)
echo "Unaligned ortholog files generated: ${num_loci} loci"
echo ""
echo "Output directory: single_copy_orthologs/unaligned_aa/"
