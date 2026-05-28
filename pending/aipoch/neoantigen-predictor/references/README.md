# Neoantigen Predictor References

## Core Algorithm Paper
### NetMHCpan 4.1
- **Title**: NetMHCpan-4.1 and NetMHCIIpan-4.0: improved predictions of MHC antigen presentation by concurrent motif deconvolution and integration of MS MHC eluted ligand data- **Author**: Reynisson et al.- **Journal**: Nucleic Acids Research- **Year**: 2020- **LINK**: https://doi.org/10.1093/nar/gkaa379
### Summary of neoantigen prediction- **Title**: Neoantigen prediction: perspectives on the present and future- **Authors**: Wells et al.- **Journal**: Nature Cancer- **Year**: 2022- **Abstract**: Systematic evaluation of computational methods and experimental validation strategies for neoantigen prediction
### Immunopeptidomics- **Title**: The immunopeptidomics landscape of cancer: implications for immunotherapy- **Authors**: Abelin et al.- **Journal**: Immunity- **Year**: 2019
## HLA binding motif reference
### MHC-I binding motif database- **Source**: IEDB (Immune Epitope Database)- **Website**: http://www.iedb.org/- **Content**: Validated HLA-peptide binding data
### HLA frequency database- **Source**: Allele Frequency Net Database- **Website**: http://www.allelefrequencies.net/- **Use**: Population HLA allele frequency data
## Clinical Guidelines for Cancer Immunotherapy
### Neoantigen vaccine clinical trial design- **Documentation**: NCI Neoantigen Guidance- **Content**: Design principles and endpoints for clinical trials of neoantigen vaccines
### Immunotherapy Biomarkers- **Title**: Biomarkers for Immunotherapy in Cancer- **Organization**: FDA Guidance Document
## Related databases
|database|use|Link|
|--------|------|------|
| **Ensembl** |Genome annotation| https://www.ensembl.org/ |
| **UniProt** |protein sequence| https://www.uniprot.org/ |
| **ClinVar** |clinical variation| https://www.ncbi.nlm.nih.gov/clinvar/ |
| **COSMIC** |tumor mutations| https://cancer.sanger.ac.uk/ |
| **TCGA** |tumor genome| https://portal.gdc.cancer.gov/ |
| **IMGT/HLA** |HLA sequence| https://www.ebi.ac.uk/ipd/imgt/hla/ |

## Amino acid property table
### Hydrophobicity Scale (Kyte-Doolittle)
|amino acids|single letter|hydrophobicity value|
|--------|--------|----------|
| Isoleucine | I | 4.5 |
| Valine | V | 4.2 |
| Leucine | L | 3.8 |
| Phenylalanine | F | 2.8 |
| Cysteine | C | 2.5 |
| Methionine | M | 1.9 |
| Alanine | A | 1.8 |
| Glycine | G | -0.4 |
| Threonine | T | -0.7 |
| Serine | S | -0.8 |
| Tryptophan | W | -0.9 |
| Tyrosine | Y | -1.3 |
| Proline | P | -1.6 |
| Histidine | H | -3.2 |
| Glutamic Acid | E | -3.5 |
| Glutamine | Q | -3.5 |
| Aspartic Acid | D | -3.5 |
| Asparagine | N | -3.5 |
| Lysine | K | -3.9 |
| Arginine | R | -4.5 |

### Amino acid molecular weight
|amino acids|single letter|Molecular weight (Da)|
|--------|--------|-------------|
| Alanine | A | 89.09 |
| Arginine | R | 174.20 |
| Asparagine | N | 132.12 |
| Aspartic Acid | D | 133.10 |
| Cysteine | C | 121.16 |
| Glutamic Acid | E | 147.13 |
| Glutamine | Q | 146.15 |
| Glycine | G | 75.07 |
| Histidine | H | 155.16 |
| Isoleucine | I | 131.17 |
| Leucine | L | 131.17 |
| Lysine | K | 146.19 |
| Methionine | M | 149.21 |
| Phenylalanine | F | 165.19 |
| Proline | P | 115.13 |
| Serine | S | 105.09 |
| Threonine | T | 119.12 |
| Tryptophan | W | 204.23 |
| Tyrosine | Y | 181.19 |
| Valine | V | 117.15 |

## Best practices for neoantigen prediction
### Quality Control Standards
1. **MHC binding affinity**- Strong binder: Rank < 0.5% or IC50 < 50 nM- Weak binder: Rank 0.5-2% or IC50 50-500 nM- Non-binder: Rank > 2% or IC50 > 500 nM
2. **Immunogenicity Assessment**- Exogenous score > 0.5- Anchor position mutations are prioritized- Changes in hydrophobicity|ΔH| > 0.3

3. **Clinical Relevance**- VAF > 5% (variant allele frequency)- Expression level: FPKM > 1- Clonal variation is prioritized
### Experimental verification process
1. **In Vitro Validation**- Peptide synthesis (variant peptide and wild-type control)- MHC binding assay (competition binding assay)- T cell activation assay (ELISPOT)
2. **In vivo verification**- Humanized mouse model- TCR identification verification- Cytotoxicity assay
3. **Clinical Application**- Personalized neoantigen vaccine design- TCR-T cell therapy target selection- Immunotherapy response prediction
## Tools and Software
### MHC Prediction Tool- **NetMHCpan 4.1**: https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/
- **MHCflurry**: https://github.com/openvax/mhcflurry
- **MixMHCpred**: http://mixmhcpred.deeplife/recipes/MixMHCpred

### Sequence analysis tools- **Biopython**: https://biopython.org/
- **pysam**: https://pysam.readthedocs.io/
- **pyvcf**: https://pyvcf.readthedocs.io/

### Visualization tools- **matplotlib**: Python plotting library- **seaborn**: Statistical data visualization- **logomaker**: Sequence logo drawing
## Glossary
|the term|English|definition|
|------|------|------|
|neoantigen| Neoantigen |Antigens generated by tumor-specific mutations|
| HLA | Human Leukocyte Antigen |human leukocyte antigen, or MHC molecule|
| MHC | Major Histocompatibility Complex |major histocompatibility complex|
| VAF | Variant Allele Frequency |variant allele frequency|
| TCR | T Cell Receptor |T cell receptor|
| IC50 | Half-maximal inhibitory concentration |half maximal inhibitory concentration|
| VUS | Variant of Uncertain Significance |Variation of unknown significance|
| VCF | Variant Call Format |Variation call format|
| FPKM | Fragments Per Kilobase Million |Fragments per million per kilobase|
