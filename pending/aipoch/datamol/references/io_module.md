# Datamol I/O Module Reference

The datamol.io module provides comprehensive file handling capabilities for molecular data in multiple formats.

## Reading Molecular Files

### dm.read_sdf(filename, sanitize=True, remove_hs=True, as_df=True, mol_column='mol', ...)
Reads Structure Data File (SDF) format.

Parameters:

filename: Path to the SDF file (supports local and remote paths via fsspec)

sanitize: Apply molecular sanitization

remove_hs: Remove explicit hydrogens

as_df: Return a DataFrame (True) or a list of molecules (False)

mol_column: Name of the molecule column in the DataFrame

n_jobs: Enable parallel processing

Returns: DataFrame or list of molecules

Example: df = dm.read_sdf("compounds.sdf")

### dm.read_smi(filename, smiles_column='smiles', mol_column='mol', as_df=True, ...)
Reads SMILES files (space-separated by default).

General format: SMILES followed by molecule ID/name

Example: df = dm.read_smi("molecules.smi")

### dm.read_csv(filename, smiles_column='smiles', mol_column=None, ...)
Reads CSV files, with optional automatic conversion of SMILES into molecule objects.

Parameters:

smiles_column: Column containing SMILES strings

mol_column: If specified, creates molecule objects from the SMILES column

Example:
df = dm.read_csv("data.csv", smiles_column="SMILES", mol_column="mol")

### dm.read_excel(filename, sheet_name=0, smiles_column='smiles', mol_column=None, ...)
Reads Excel files with molecular processing support.

Parameters:

sheet_name: Sheet to read (index or name)

Other parameters are similar to read_csv

Example:
df = dm.read_excel("compounds.xlsx", sheet_name="Sheet1")

### dm.read_molblock(molblock, sanitize=True, remove_hs=True)
Parses a MOL block string (text representation of a molecular structure).

### dm.read_mol2file(filename, sanitize=True, remove_hs=True, cleanupSubstructures=True)
Reads Mol2 format files.

### dm.read_pdbfile(filename, sanitize=True, remove_hs=True, proximityBonding=True)
Reads Protein Data Bank (PDB) format files.

### dm.read_pdbblock(pdbblock, sanitize=True, remove_hs=True, proximityBonding=True)
Parses a PDB block string.

### dm.open_df(filename, ...)
Generic DataFrame reader.

Automatically detects file format.

Supported formats: CSV, Excel, Parquet, JSON, SDF

Examples:
df = dm.open_df("data.csv")
or
df = dm.open_df("molecules.sdf")

## Writing Molecular Files

### dm.to_sdf(mols, filename, mol_column=None, ...)
Writes molecules to an SDF file.

Input types:

List of molecules

DataFrame with a molecule column

Molecule sequence

Parameters:

mol_column: Column name if the input is a DataFrame

Example:

dm.to_sdf(mols, "output.sdf")  
# or write from a DataFrame  
dm.to_sdf(df, "output.sdf", mol_column="mol")  

### dm.to_smi(mols, filename, mol_column=None, ...)
Writes molecules to a SMILES file, with optional validation.

Format: SMILES string with optional molecule name/ID

### dm.to_xlsx(df, filename, mol_columns=None, ...)
Exports a DataFrame to Excel and renders molecule images.

Parameters:

mol_columns: Columns containing molecules to render as images

Special feature: Automatically renders molecules as images inside Excel cells

Example:
dm.to_xlsx(df, "molecules.xlsx", mol_columns=["mol"])

### dm.to_molblock(mol, ...)
Converts a molecule into a MOL block string.

### dm.to_pdbblock(mol, ...)
Converts a molecule into a PDB block string.

### dm.save_df(df, filename, ...)
Saves a DataFrame in multiple formats (CSV, Excel, Parquet, JSON).

## Remote File Support

All I/O functions support remote file paths through fsspec integration:

Supported protocols: S3 (AWS), GCS (Google Cloud), Azure, HTTP/HTTPS

Examples:

dm.read_sdf("s3://bucket/compounds.sdf")  
dm.read_csv("https://example.com/data.csv")  

## Key Parameters Across Functions

sanitize: Apply molecular sanitization (default: True)

remove_hs: Remove explicit hydrogens (default: True)

as_df: Return DataFrame or list (default: True for most functions)

n_jobs: Enable parallel processing (None = use all cores, 1 = serial execution)

mol_column: Name of the molecule column in a DataFrame

smiles_column: Name of the SMILES column in a DataFrame