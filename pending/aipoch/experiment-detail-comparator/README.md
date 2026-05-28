# Experiment Detail Comparator

A tool specifically designed to compare experimental method details between two papers. It can identify differences in experimental parameters (concentration, temperature, time, etc.), search relevant literature to analyze the reasons for these differences, and finally generate a comparison report in HTML format.

## Features

### Core Features (v1.0)
- ✅ Read two PDF papers from a Zotero library
- ✅ Automatically extract experimental parameters from the Methods section
- ✅ Compare and identify significant differences (concentration, temperature, time, etc.)
- ✅ Search multiple literature databases to explain the reasons for differences
- ✅ Generate aesthetic HTML reports
- ✅ Evidence grading (High/Medium/Low)

### Enhanced Features (v2.0)

#### Enhanced Method Detail Extraction
- ✅ **Experimental Design Extraction** - Control groups, experimental groups, number of replicates, randomization, blinding
- ✅ **Complete Materials List Extraction** - Detailed chemical information (name, supplier, batch number), kit information, culture media recipes, buffers, solvents
- ✅ **Equipment and Instrument Extraction** - Equipment name, model, manufacturer, settings (centrifuge speed, incubator temperature, spectrophotometer wavelength, etc.)
- ✅ **Sample Information Extraction** - Sample source, quantity, processing methods (freezing, fixation, etc.), ethical approval, informed consent, storage conditions
- ✅ **Key Step Extraction** - Structured experimental step sequences (Step 1, Step 2, Step 3, Step 4), including step types (preparation, reaction, purification, detection)

#### Enhanced PDF Processing
- ✅ **Full-text PDF Download and Parsing** - Supports URLs and local PDFs, automatically detects language (Chinese/Japanese/English), extracts DOI, and generates JSON and plain text output
- ✅ **PDF Table Extraction** - Uses `pdfplumber` to extract all tables, automatically identifies table types (materials table, parameter table, results table), and supports complex table structures
- ✅ **Multi-language PDF Support** - Automatically detects PDF language (Simplified Chinese, Traditional Chinese, Japanese, Korean, Russian) and optimizes extraction logic

## Prerequisites

### 1. Zotero Configuration

Ensure your papers have been added to your Zotero library and the PDF files are attached.

### 2. Environment Variables

Configure the following variables in the `Notes/.env` file:

```bash
# Zotero API Configuration
ZOTERO_API_KEY=your_api_key_here
ZOTERO_LIBRARY_TYPE=user
ZOTERO_LIBRARY_ID=your_library_id_here

# Mistral API Configuration (for PDF conversion)
MISTRAL_API_KEY=your_mistral_api_key_here
```

**How to get Zotero API Key:**
1. Visit https://www.zotero.org/settings/keys
2. Create a new key with "Read library" permissions
3. Record the API Key and Library ID

### 3. Dependency Installation

The following Python packages are required:
- mistral-pdf-to-markdown skill
- Zotero MCP tools
- literature search tools (PubMed, EuropePMC, SemanticScholar)

## Usage

### Basic Usage

```bash
python run_comparison.py "Paper 1 Title or Author" "Paper 2 Title or Author" [output_directory]
```

### Examples

```bash
# Compare two CRISPR papers
python run_comparison.py \
  "CRISPR-Cas9 knockout in HeLa cells" \
  "Efficient genome editing in HEK293 cells" \
  ./output

# Search using author names
python run_comparison.py \
  "Smith et al 2023" \
  "Jones et al 2024" \
  ./reports
```

## Workflow

1. **Fetch PDFs from Zotero**
   - Search for the two papers
   - Prioritize local storage; download from the web if local retrieval fails

2. **Convert PDF to Markdown**
   - Convert using `mistral-pdf-to-markdown`
   - Save as a readable text format

3. **Extract Method Details**
   - Locate the Methods/Experimental Procedures section
   - Extract key parameters:
     - Concentrations
     - Temperatures
     - Durations
     - Ratios
     - Volumes
     - Cell lines/organisms
     - Equipment

4. **Compare Parameter Differences**
   - Automatically compare all parameters
   - Identify significant differences (based on type judgment)
   - Generate a comparison table

5. **Search Literature for Explanations**
   - Search for relevant literature for each significant difference
   - Use multiple databases:
     - PubMed
     - Europe PMC (supports full-text extraction)
     - Semantic Scholar
   - Evaluate evidence quality

6. **Generate HTML Report**
   - Includes paper information
   - Method comparison table
   - Literature-supported explanations for differences
   - Reference list

## Output Files

| File | Description |
|------|------|
| `comparison_report.html` | Main comparison report (HTML format, containing all analysis results) |
| `method_details.json` | Detailed method parameters for both papers (structured JSON) |
| `explanations.json` | Literature search results and evidence levels (JSON format) |

## Evidence Grading

| Level | Description | Example |
|------|------|------|
| **High** | Mechanistic study with direct experimental evidence | Comparative study optimizing best conditions |
| **Medium** | Functional study or empirical data | Protocol optimization paper |
| **Low** | Mentioned in review or anecdotal evidence | Parameter selection mentioned in a methods section |

## Report Example

The HTML report contains the following sections:

1. **Paper Information** - Title, author, year, journal
2. **Method Comparison Table** - Item-by-item comparison of all parameters, highlighting significant differences
3. **Difference Reason Analysis** - Literature explanations for each significant difference
4. **Summary** - Statistics on the number of differences and overall evaluation
5. **References** - Complete list of references

## Custom Parameter Identification

To extract specific parameters, you can modify the regular expressions in `scripts/extract_method_section.py`:

```python
# Add new parameter types
def extract_custom_parameters(method_text, parameters):
    pattern = r'your_regular_expression'
    for match in re.finditer(pattern, method_text):
        # Process match results
        pass
```

## Troubleshooting

### Issue: Zotero search fails

**Solution:**
1. Check the API configuration in `Notes/.env`
2. Ensure Zotero local API is enabled (Edit > Preferences > Advanced > Enable local server)
3. Verify if the Library ID is correct

### Issue: PDF conversion fails

**Solution:**
1. Check `MISTRAL_API_KEY` in `Notes/.env`
2. Ensure the PDF file is valid (not corrupted)
3. Large files may require chunked processing

### Issue: Inaccurate method extraction

**Solution:**
1. Check if the Markdown conversion was successful
2. Manually locate the header format of the Methods section
3. Extraction logic may need adjustment based on specific journal formats

### Issue: No results from literature search

**Solution:**
1. Try using English search terms
2. Expand the search range (increase the `limit` parameter)
3. Check network connectivity

## Advanced Usage

### Extract method details only

```bash
python scripts/extract_method_section.py temp/paper1.md output/paper1_method.json
```

### Compare two methods only

```bash
python scripts/compare_methods.py \
  output/paper1_method.json \
  output/paper2_method.json \
  output/comparison.json
```

### Search for explanations only

```bash
python scripts/search_explanations.py \
  output/comparison.json \
  output/explanations.json
```

### Generate HTML report only

```bash
python scripts/generate_html_report.py \
  temp/paper1_info.json \
  temp/paper2_info.json \
  output/comparison.json \
  output/explanations.json \
  output/report.html
```

## Notes

- ⚠️ Ensure there are PDF attachments in the Zotero library
- ⚠️ PDF conversion requires Mistral API credits
- ⚠️ Literature searches yield better results using English queries
- ⚠️ Large papers (>40k tokens) require chunked processing
- ⚠️ Evidence grading is based on keyword matching and may have errors

## Tech Stack

- **PDF Processing**: mistral-pdf-to-markdown
- **Literature Search**: PubMed, Europe PMC, Semantic Scholar
- **Report Generation**: HTML + CSS
- **Language**: Python 3.8+

## Contribution

Issues and Pull Requests are welcome!

## License

MIT License

## Contact

If you have questions or suggestions, please create an Issue.