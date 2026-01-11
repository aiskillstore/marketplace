#!/bin/bash
source ~/.bashrc
conda activate phylo

cd trimmed_aa

# Create list of alignments
ls *_trimmed.fas > locus_alignments.txt

# Run IQ-TREE in parallel (adjust -j for number of concurrent jobs)
cat locus_alignments.txt | parallel -j 4 '
  prefix=$(basename {} _trimmed.fas)
  iqtree -s {} -m MFP -bb 1000 -bnni -czb -pre ${prefix} -nt 1
  echo "Tree complete: ${prefix}"
'

echo "All gene trees complete!"
