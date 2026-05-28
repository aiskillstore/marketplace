# ClinVar API Reference

## E-utilities
Base URL: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

### Endpoints
1.  **esearch.fcgi**: Search for IDs.
    - Param `db`: `clinvar`
    - Param `term`: Query string
2.  **esummary.fcgi**: Get document summaries.
    - Param `db`: `clinvar`
    - Param `id`: Comma-separated IDs

## FTP
URL: `ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/`
- `xml/`: Full releases in XML
- `vcf_GRCh37/`: VCF files for GRCh37
- `vcf_GRCh38/`: VCF files for GRCh38
