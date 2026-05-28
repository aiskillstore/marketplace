# Metagenomic Krona Chart

Generate interactive sunburst plots showing species-level abundance in metagenomic samples.
## Function
- Supports output formats of common classification tools such as Kraken2 and Bracken- Automatically detect input formats- Generate interactive HTML sunburst charts- Configurable minimum percentage threshold and maximum display depth-Color coding different classification levels
## Install
```bash
cd skills/metagenomic-krona-chart
pip install plotly pandas
```

## Quick Start
```bash
# Basic usage
python scripts/main.py -i example/sample_kraken2.txt -o output.html

# Specify title and threshold
python scripts/main.py -i report.txt -o krona.html \
    --title "Sample A Metagenomics" \
    --min-percent 0.1 \
    --max-depth 6
```

## Input format
### Kraken2 / Bracken format```
100.00  1000000 0   U   0   unclassified
 99.00  990000  0   R   1   root
 95.00  950000  0   D   2   Bacteria
 50.00  500000  0   P   1234    Proteobacteria
...
```

### Custom TSV format```
taxon_id	name	rank	parent_id	reads	percent
2	Bacteria	domain	1	950000	95.0
1234	Proteobacteria	phylum	2	500000	50.0
```

## Output characteristics
- Interactive sunburst chart, supports zooming and clicking- Hover to display detailed information (readings, percentages, classification levels)- The legend on the right shows the color of the classification level- Responsive design- Independent HTML file, can be viewed offline
## Sample output
After running, `krona_chart.html` will be generated. Open it with a browser to view the interactive chart.