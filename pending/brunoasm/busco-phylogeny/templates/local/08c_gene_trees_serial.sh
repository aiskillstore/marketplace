#!/bin/bash
source ~/.bashrc
conda activate phylo

cd trimmed_aa

for locus in *_trimmed.fas; do
    prefix=$(basename ${locus} _trimmed.fas)
    echo "Processing ${prefix}..."
    iqtree -s ${locus} -m MFP -bb 1000 -bnni -czb -pre ${prefix} -nt 1
done

echo "All gene trees complete!"
