# Validation and Quality Assurance Guide

## Overview

Validation quantifies extraction accuracy using precision, recall, and F1 metrics by comparing automated extraction against manually annotated ground truth.

## When to Validate

- **Before production use** - Establish baseline quality
- **After schema changes** - Verify improvements
- **When comparing models** - Test Haiku vs Sonnet vs Ollama
- **For publication** - Report extraction quality metrics

## Recommended Sample Sizes

- Small projects (<100 papers): 10-20 papers
- Medium projects (100-500 papers): 20-50 papers
- Large projects (>500 papers): 50-100 papers

## Step 7: Prepare Validation Set

Sample papers for manual annotation using one of three strategies.

### Random Sampling (General Quality)

```bash
python scripts/07_prepare_validation_set.py \
  --extraction-results cleaned_data.json \
  --schema my_schema.json \
  --sample-size 20 \
  --strategy random \
  --output validation_set.json
```

Provides overall quality estimate but may miss rare cases.

### Stratified Sampling (Identify Weaknesses)

```bash
python scripts/07_prepare_validation_set.py \
  --extraction-results cleaned_data.json \
  --schema my_schema.json \
  --sample-size 20 \
  --strategy stratified \
  --output validation_set.json
```

Samples papers with different characteristics:
- Papers with no records
- Papers with few records (1-2)
- Papers with medium records (3-5)
- Papers with many records (6+)

Best for identifying weak points in extraction.

### Diverse Sampling (Comprehensive)

```bash
python scripts/07_prepare_validation_set.py \
  --extraction-results cleaned_data.json \
  --schema my_schema.json \
  --sample-size 20 \
  --strategy diverse \
  --output validation_set.json
```

Maximizes diversity across different paper types.

## Step 8: Manual Annotation

### Annotation Process

1. **Open validation file:**
   ```bash
   # Use your preferred JSON editor
   code validation_set.json  # VS Code
   vim validation_set.json   # Vim
   ```

2. **For each paper in `validation_papers`:**
   - Locate and read the original PDF
   - Extract data according to the schema
   - Fill the `ground_truth` field with correct extraction
   - The structure should match `automated_extraction`

3. **Fill metadata fields:**
   - `annotator`: Your name
   - `annotation_date`: YYYY-MM-DD
   - `notes`: Any ambiguous cases or comments

### Annotation Tips

**Be thorough:**
- Extract ALL relevant information, even if automated extraction missed it
- This ensures accurate recall calculation

**Be precise:**
- Use exact values as they appear in the paper
- Follow the same schema structure as automated extraction

**Be consistent:**
- Apply the same interpretation rules across all papers
- Document interpretation decisions in notes

**Mark ambiguities:**
- If a field is unclear, note it and make your best judgment
- Consider having multiple annotators for inter-rater reliability

### Example Annotation

```json
{
  "paper_id_123": {
    "automated_extraction": {
      "has_relevant_data": true,
      "records": [
        {
          "species": "Apis mellifera",
          "location": "Brazil"
        }
      ]
    },
    "ground_truth": {
      "has_relevant_data": true,
      "records": [
        {
          "species": "Apis mellifera",
          "location": "Brazil",
          "state_province": "São Paulo"  // Automated missed this
        },
        {
          "species": "Bombus terrestris",  // Automated missed this record
          "location": "Brazil",
          "state_province": "São Paulo"
        }
      ]
    },
    "notes": "Automated extraction missed the state and second species",
    "annotator": "John Doe",
    "annotation_date": "2025-01-15"
  }
}
```

## Step 9: Calculate Validation Metrics

### Basic Metrics Calculation

```bash
python scripts/08_calculate_validation_metrics.py \
  --annotations validation_set.json \
  --output validation_metrics.json \
  --report validation_report.txt
```

### Advanced Options

**Fuzzy string matching:**
```bash
python scripts/08_calculate_validation_metrics.py \
  --annotations validation_set.json \
  --fuzzy-strings \
  --output validation_metrics.json
```

Normalizes whitespace and case for string comparisons.

**Numeric tolerance:**
```bash
python scripts/08_calculate_validation_metrics.py \
  --annotations validation_set.json \
  --numeric-tolerance 0.01 \
  --output validation_metrics.json
```

Allows small differences in numeric values.

**Ordered list comparison:**
```bash
python scripts/08_calculate_validation_metrics.py \
  --annotations validation_set.json \
  --list-order-matters \
  --output validation_metrics.json
```

Treats lists as ordered sequences instead of sets.

## Understanding the Metrics

### Precision
**Definition:** Of the items extracted, what percentage are correct?

**Formula:** TP / (TP + FP)

**Example:** Extracted 10 species, 8 were correct → Precision = 80%

**High precision, low recall:** Conservative extraction (misses data)

### Recall
**Definition:** Of the true items, what percentage were extracted?

**Formula:** TP / (TP + FN)

**Example:** Paper has 12 species, extracted 8 → Recall = 67%

**Low precision, high recall:** Liberal extraction (includes errors)

### F1 Score
**Definition:** Harmonic mean of precision and recall

**Formula:** 2 × (Precision × Recall) / (Precision + Recall)

**Use:** Single metric balancing precision and recall

### Field-Level Metrics

Metrics are calculated for each field type:

**Boolean fields:**
- True positives, false positives, false negatives

**Numeric fields:**
- Exact match or within tolerance

**String fields:**
- Exact or fuzzy match

**List fields:**
- Set-based comparison (default)
- Items in both (TP), in automated only (FP), in truth only (FN)

**Nested objects:**
- Recursive field-by-field comparison

## Interpreting Results

### Validation Report Structure

```
OVERALL METRICS
  Papers evaluated: 20
  Precision: 87.3%
  Recall: 79.2%
  F1 Score: 83.1%

METRICS BY FIELD
  Field                  Precision    Recall       F1
  species               95.2%        89.1%        92.0%
  location              82.3%        75.4%        78.7%
  method                91.0%        68.2%        77.9%

COMMON ISSUES
  Fields with low recall (missed information):
  - method: 68.2% recall, 12 missed items

  Fields with low precision (incorrect extractions):
  - location: 82.3% precision, 8 incorrect items
```

### Using Results to Improve

**Low Recall (Missing Information):**
- Review extraction prompt instructions
- Add examples of the missed pattern
- Emphasize completeness in prompt
- Consider using more capable model (Haiku → Sonnet)

**Low Precision (Incorrect Extractions):**
- Add validation rules to prompt
- Provide clearer field definitions
- Add negative examples
- Tighten extraction criteria

**Field-Specific Issues:**
- Identify problematic field types
- Revise schema definitions
- Add field-specific instructions
- Update examples

## Inter-Rater Reliability (Optional)

For critical applications, have multiple annotators:

1. **Split validation set:**
   - 10 papers: Single annotator
   - 10 papers: Both annotators independently

2. **Calculate agreement:**
   ```bash
   python scripts/08_calculate_validation_metrics.py \
     --annotations annotator1.json \
     --compare-with annotator2.json \
     --output agreement_metrics.json
   ```

3. **Resolve disagreements:**
   - Discuss discrepancies
   - Establish interpretation guidelines
   - Re-annotate if needed

## Iterative Improvement Workflow

1. **Baseline:** Run extraction with initial schema
2. **Validate:** Calculate metrics on sample
3. **Analyze:** Identify weak fields and error patterns
4. **Revise:** Update schema, prompts, or model
5. **Re-extract:** Run extraction with improvements
6. **Re-validate:** Calculate new metrics
7. **Compare:** Check if metrics improved
8. **Repeat:** Until acceptable quality achieved

## Reporting Validation in Publications

Include in methods section:

```
Extraction quality was assessed on a stratified random sample of
20 papers. Automated extraction achieved 87.3% precision (95% CI:
81.2-93.4%) and 79.2% recall (95% CI: 72.8-85.6%), with an F1
score of 83.1%. Field-level metrics ranged from 77.9% (method
descriptions) to 92.0% (species names).
```

Consider reporting:
- Sample size and sampling strategy
- Overall precision, recall, F1
- Field-level metrics for key fields
- Confidence intervals
- Common error types
