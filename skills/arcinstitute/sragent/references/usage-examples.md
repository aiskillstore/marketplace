# SRAgent Usage Examples

## Example 1: Simple Accession Conversion

**User Query:** "I have GEO series GSE121737. What are the SRX experiment accessions?"

**Claude's Approach:**
```bash
SRAgent entrez "Convert GSE121737 to SRX accessions"
```

**Expected Output:**
```json
{
  "GSE121737": [
    "SRX4967527",
    "SRX4967528",
    "SRX4967529",
    ...
  ]
}
```

**Claude's Response:** "GSE121737 contains X SRX experiments: SRX4967527, SRX4967528, SRX4967529, ..."

---

## Example 2: Technology Identification

**User Query:** "What 10X Genomics technology was used for experiment ERX11887200?"

**Claude's Approach:**
```bash
SRAgent sragent "Which 10X Genomics technology was used for ERX11887200?"
```

**Expected Output:**
```
Library prep: 10x Genomics
Technology: Chromium Single Cell 3' v3
Chemistry: v3.1
```

**Claude's Response:** "Experiment ERX11887200 used 10X Genomics Chromium Single Cell 3' v3 chemistry (v3.1)."

---

## Example 3: Single-Cell Verification

**User Query:** "Is SRX4967527 single-cell RNA-seq data?"

**Claude's Approach:**
```bash
SRAgent sragent "Is SRX4967527 single-cell RNA-seq data?"
```

**Expected Output:**
```
Is single-cell: yes
Library prep: 10x Genomics
Platform: Illumina NovaSeq 6000
Layout: paired-end
```

**Claude's Response:** "Yes, SRX4967527 is single-cell RNA-seq data using 10X Genomics technology, sequenced on Illumina NovaSeq 6000 with paired-end reads."

---

## Example 4: Paper Download (Single Accession)

**User Query:** "Download papers for SRX4967527"

**Claude's Approach:**
```bash
mkdir -p /home/claude/papers
SRAgent papers SRX4967527 --output-dir /home/claude/papers
```

**Expected Output:**
```
Processing SRX4967527...
Found 1 publication(s)
- PMID: 31234567
- DOI: 10.1038/s41586-020-1234-5
- Download: SUCCESS
- Saved to: /home/claude/papers/SRX4967527/10.1038_s41586-020-1234-5.pdf
```

**Claude's Response:** "I found and downloaded 1 paper for SRX4967527:
- PubMed ID: 31234567
- DOI: 10.1038/s41586-020-1234-5
- PDF saved to: [link to file]"

---

## Example 5: Batch Paper Download

**User Query:** "I have a list of SRX accessions. Help me download all their papers."

**Claude creates CSV:**
```python
import pandas as pd

accessions = ["SRX4967527", "SRX4967528", "SRX4967529"]
df = pd.DataFrame({"accession": accessions})
df.to_csv("/home/claude/accessions.csv", index=False)
```

**Claude runs SRAgent:**
```bash
SRAgent papers /home/claude/accessions.csv --output-dir /home/claude/papers --max-concurrency 5
```

**Expected Output:**
```
Processing 3 accessions...
[1/3] SRX4967527: Found 1 publication, 1 downloaded
[2/3] SRX4967528: Found 2 publications, 2 downloaded  
[3/3] SRX4967529: Found 1 publication, 0 downloaded (no open access)

Summary:
- Total accessions: 3
- Total publications: 4
- Successfully downloaded: 3
- Failed downloads: 1
```

**Claude reads enriched CSV:**
```python
result_df = pd.read_csv("/home/claude/accessions.csv")
# Now has: accession, pubmed_id, doi, download_path columns
```

**Claude's Response:** "I processed 3 accessions and found 4 papers total. Successfully downloaded 3 PDFs (1 paper wasn't available as open access). Here's a summary table: [shows table with results]"

---

## Example 6: Study-Wide Analysis

**User Query:** "Analyze all experiments in study PRJNA498286 and tell me which use 10X Genomics"

**Claude's Approach:**

Step 1: Get experiments
```bash
SRAgent entrez "Convert PRJNA498286 to SRX accessions"
```

Step 2: Check each for 10X
```bash
# For each SRX returned
SRAgent sragent "What is the library prep technology for SRX... ?"
```

Step 3: Summarize findings

**Claude's Response:** "Study PRJNA498286 contains 24 experiments. Here's the breakdown:
- 18 experiments use 10X Genomics (Chromium Single Cell 3' v3)
- 6 experiments use Smart-seq2
All are single-cell RNA-seq on Illumina platform."

---

## Example 7: Metadata Extraction for Filtering

**User Query:** "I need to find paired-end Illumina single-cell experiments from human samples"

**Claude's Approach:**
```bash
# Example with specific accession
SRAgent sragent "For SRX4967527, tell me: organism, platform, is it paired-end, is it single-cell"
```

**Expected Output:**
```json
{
  "srx_accession": "SRX4967527",
  "organism": "Homo sapiens",
  "platform": "Illumina NovaSeq 6000",
  "is_paired_end": "yes",
  "is_single_cell": "yes",
  "library_prep": "10x Genomics"
}
```

**Claude filters:** Check organism=="Homo sapiens", is_paired_end=="yes", is_single_cell=="yes"

---

## Example 8: Complete Dataset Annotation Workflow

**User Query:** "I have GSE196830. Give me complete metadata and papers for all experiments."

**Claude's Workflow:**

```bash
# Step 1: Convert to SRX
SRAgent entrez "Convert GSE196830 to SRX accessions" > /tmp/srx_list.txt

# Step 2: Get metadata for each (creates CSV)
# (Claude creates CSV from SRX list)

# Step 3: Get comprehensive metadata
while read srx; do
  SRAgent sragent "Complete metadata for $srx: organism, technology, paired-end, single-cell"
done < /tmp/srx_list.txt > /tmp/metadata.txt

# Step 4: Download papers
SRAgent papers /home/claude/srx_accessions.csv --output-dir /home/claude/papers
```

**Claude presents:** Formatted table with all metadata + links to downloaded papers

---

## Example 9: Technology Survey Across Multiple Studies

**User Query:** "Compare the scRNA-seq technologies used in PRJNA498286 vs PRJNA615032"

**Claude's Approach:**

```bash
# Study 1
SRAgent entrez "Convert PRJNA498286 to SRX accessions"
SRAgent sragent "What scRNA-seq technologies are used across all experiments in PRJNA498286?"

# Study 2  
SRAgent entrez "Convert PRJNA615032 to SRX accessions"
SRAgent sragent "What scRNA-seq technologies are used across all experiments in PRJNA615032?"
```

**Claude analyzes and compares:** 
- "PRJNA498286: Primarily 10X Genomics Chromium 3' v3 (18/24 experiments)"
- "PRJNA615032: Mix of Smart-seq2 and 10X Genomics 5' chemistry"
- Comparison table showing technology distribution

---

## Example 10: Organism Identification

**User Query:** "What organisms were sequenced in these experiments: SRX4967527, ERX11887200, SRR8124405?"

**Claude's Approach:**

```bash
# Create CSV with accessions
cat > /home/claude/check_organisms.csv << EOF
accession
SRX4967527
ERX11887200
SRR8124405
EOF

# Query each
SRAgent sragent "What is the organism for SRX4967527?"
SRAgent sragent "What is the organism for ERX11887200?"
SRAgent sragent "What is the organism for SRR8124405?"
```

**Claude's Response:** Formatted table:
| Accession | Organism |
|-----------|----------|
| SRX4967527 | Homo sapiens (human) |
| ERX11887200 | Mus musculus (mouse) |
| SRR8124405 | Danio rerio (zebrafish) |

---

## Tips for Effective Usage

1. **Start with conversion** - If user gives GSE, convert to SRX first
2. **Use appropriate command:**
   - Simple queries → `SRAgent entrez`
   - Complex/multi-tool queries → `SRAgent sragent`
   - Paper downloads → `SRAgent papers`
3. **Create CSVs for batch** - More efficient than sequential queries
4. **Parse and present clearly** - Extract key info, format as tables
5. **Handle errors gracefully** - Not all datasets have papers, not all metadata is available
6. **Provide context** - Explain what you're finding (e.g., "This is a mouse brain single-cell study")

## Common Patterns

### Pattern: "Is this what I'm looking for?"
```bash
SRAgent sragent "Is [accession] [criteria]?"
# Example: "Is SRX4967527 paired-end Illumina single-cell RNA-seq?"
```

### Pattern: "What technology?"
```bash
SRAgent sragent "What [platform/technology/organism] for [accession]?"
```

### Pattern: "Get everything"
```bash
SRAgent entrez "Convert [accession] to [target format]"
SRAgent sragent "Complete metadata for [accession]"
SRAgent papers [accession] --output-dir /path/to/save
```

### Pattern: "Batch processing"
```python
# Create CSV → SRAgent papers CSV → Read results → Present table
```