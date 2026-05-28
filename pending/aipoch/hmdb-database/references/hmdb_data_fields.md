# HMDB Data Fields

The following fields are typically available in the HMDB XML dataset and can be extracted using the `hmdb_parser.py` script.

## General Information
- **accession**: Primary HMDB ID (e.g., HMDB0000001)
- **name**: Common name of the metabolite
- **description**: Detailed description
- **synonyms**: List of alternative names

## Chemical Properties
- **chemical_formula**: e.g., C8H10N4O2
- **average_molecular_weight**: e.g., 194.19
- **monisotopic_molecular_weight**: e.g., 194.080375575
- **smiles**: Simplified Molecular Input Line Entry System string
- **inchi**: IUPAC International Chemical Identifier
- **inchi_key**: Hashed InChI key

## Biological Properties
- **taxonomy**: Kingdom, Super Class, Class, Sub Class
- **pathways**: Metabolic pathways involved
- **biological_roles**: Roles in the biological system
- **biological_properties**: Cellular locations, tissue locations

## Clinical Data
- **diseases**: Associated diseases and conditions
- **concentrations**: Normal and abnormal concentrations in biofluids (Blood, Urine, etc.)

## External Links
- **kegg_id**: Kyoto Encyclopedia of Genes and Genomes ID
- **pubchem_compound_id**: PubChem ID
- **chebi_id**: Chemical Entities of Biological Interest ID
