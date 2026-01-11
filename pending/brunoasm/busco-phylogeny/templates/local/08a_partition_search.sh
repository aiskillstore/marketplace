#!/bin/bash
source ~/.bashrc
conda activate phylo

cd 06_concatenation

iqtree \
  -s FcC_supermatrix.fas \
  -spp partition_def.txt \
  -nt 18 \
  -safe \
  -pre partition_search \
  -m TESTMERGEONLY \
  -mset MODEL_SET \
  -msub nuclear \
  -rcluster 10 \
  -bb 1000 \
  -alrt 1000

echo "Partition search complete! Best scheme: partition_search.best_scheme.nex"
