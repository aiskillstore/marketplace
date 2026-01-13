#!/usr/bin/env python3
"""
Prepare a validation set for evaluating extraction quality.

This script helps you:
1. Sample a subset of papers for manual annotation
2. Set up a structured annotation file
3. Guide the annotation process

The validation set is used to calculate precision and recall metrics.
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Any
import sys


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Prepare validation set for extraction quality evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow:
1. This script samples papers from your extraction results
2. It creates an annotation template based on your schema
3. You manually annotate the sampled papers with ground truth
4. Use 08_calculate_validation_metrics.py to compare automated vs. manual extraction

Sampling strategies:
  random    : Random sample (good for overall quality)
  stratified: Sample by extraction characteristics (good for identifying weaknesses)
  diverse   : Sample to maximize diversity (good for comprehensive evaluation)
        """
    )
    parser.add_argument(
        '--extraction-results',
        required=True,
        help='JSON file with extraction results from step 03 or 04'
    )
    parser.add_argument(
        '--schema',
        required=True,
        help='Extraction schema JSON file used in step 03'
    )
    parser.add_argument(
        '--output',
        default='validation_set.json',
        help='Output file for validation annotations'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=20,
        help='Number of papers to sample (default: 20, recommended: 20-50)'
    )
    parser.add_argument(
        '--strategy',
        choices=['random', 'stratified', 'diverse'],
        default='random',
        help='Sampling strategy (default: random)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    return parser.parse_args()


def load_results(results_path: Path) -> Dict:
    """Load extraction results"""
    with open(results_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_schema(schema_path: Path) -> Dict:
    """Load extraction schema"""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def sample_random(results: Dict, sample_size: int, seed: int) -> List[str]:
    """Random sampling strategy"""
    # Only sample from successful extractions
    successful = [
        paper_id for paper_id, result in results.items()
        if result.get('status') == 'success' and result.get('extracted_data')
    ]

    if len(successful) < sample_size:
        print(f"Warning: Only {len(successful)} successful extractions available")
        sample_size = len(successful)

    random.seed(seed)
    return random.sample(successful, sample_size)


def sample_stratified(results: Dict, sample_size: int, seed: int) -> List[str]:
    """
    Stratified sampling: sample papers with different characteristics
    E.g., papers with many records vs. few records, different data completeness
    """
    successful = {}
    for paper_id, result in results.items():
        if result.get('status') == 'success' and result.get('extracted_data'):
            data = result['extracted_data']
            # Count records if present
            num_records = len(data.get('records', [])) if 'records' in data else 0
            successful[paper_id] = num_records

    if not successful:
        print("No successful extractions found")
        return []

    # Create strata based on number of records
    strata = {
        'zero': [],
        'few': [],      # 1-2 records
        'medium': [],   # 3-5 records
        'many': []      # 6+ records
    }

    for paper_id, count in successful.items():
        if count == 0:
            strata['zero'].append(paper_id)
        elif count <= 2:
            strata['few'].append(paper_id)
        elif count <= 5:
            strata['medium'].append(paper_id)
        else:
            strata['many'].append(paper_id)

    # Sample proportionally from each stratum
    random.seed(seed)
    sampled = []
    total_papers = len(successful)

    for stratum_name, papers in strata.items():
        if not papers:
            continue
        # Sample proportionally, at least 1 from each non-empty stratum
        stratum_sample_size = max(1, int(len(papers) / total_papers * sample_size))
        stratum_sample_size = min(stratum_sample_size, len(papers))
        sampled.extend(random.sample(papers, stratum_sample_size))

    # If we haven't reached sample_size, add more randomly
    if len(sampled) < sample_size:
        remaining = [p for p in successful.keys() if p not in sampled]
        additional = min(sample_size - len(sampled), len(remaining))
        sampled.extend(random.sample(remaining, additional))

    return sampled[:sample_size]


def sample_diverse(results: Dict, sample_size: int, seed: int) -> List[str]:
    """
    Diverse sampling: maximize diversity in sampled papers
    This is a simplified version - could be enhanced with actual diversity metrics
    """
    # For now, use stratified sampling as a proxy for diversity
    return sample_stratified(results, sample_size, seed)


def create_annotation_template(
    sampled_ids: List[str],
    results: Dict,
    schema: Dict
) -> Dict:
    """
    Create annotation template for manual validation.

    Structure:
    {
      "paper_id": {
        "automated_extraction": {...},
        "ground_truth": null,  # To be filled manually
        "notes": "",
        "annotator": "",
        "annotation_date": ""
      }
    }
    """
    template = {
        "_instructions": {
            "overview": "This is a validation annotation file. For each paper, review the PDF and fill in the ground_truth field with the correct extraction.",
            "steps": [
                "1. Read the PDF for each paper_id",
                "2. Extract data according to the schema, filling the 'ground_truth' field",
                "3. The 'ground_truth' should have the same structure as 'automated_extraction'",
                "4. Add your name in 'annotator' and date in 'annotation_date'",
                "5. Use 'notes' field for any comments or ambiguities",
                "6. Once complete, use 08_calculate_validation_metrics.py to compare"
            ],
            "schema_reference": schema.get('output_schema', {}),
            "tips": [
                "Be thorough: extract ALL relevant information, even if automated extraction missed it",
                "Be precise: use exact values as they appear in the paper",
                "Be consistent: follow the same schema structure",
                "Mark ambiguous cases in notes field"
            ]
        },
        "validation_papers": {}
    }

    for paper_id in sampled_ids:
        result = results[paper_id]
        template["validation_papers"][paper_id] = {
            "automated_extraction": result.get('extracted_data', {}),
            "ground_truth": None,  # To be filled by annotator
            "notes": "",
            "annotator": "",
            "annotation_date": "",
            "_pdf_path": None,  # Will try to find from metadata
            "_extraction_metadata": {
                "extraction_status": result.get('status'),
                "validation_status": result.get('validation_status'),
                "has_analysis": bool(result.get('analysis'))
            }
        }

    return template


def save_template(template: Dict, output_path: Path):
    """Save annotation template to JSON file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)


def main():
    args = parse_args()

    # Load inputs
    results = load_results(Path(args.extraction_results))
    schema = load_schema(Path(args.schema))
    print(f"Loaded {len(results)} extraction results")

    # Sample papers
    if args.strategy == 'random':
        sampled = sample_random(results, args.sample_size, args.seed)
    elif args.strategy == 'stratified':
        sampled = sample_stratified(results, args.sample_size, args.seed)
    elif args.strategy == 'diverse':
        sampled = sample_diverse(results, args.sample_size, args.seed)

    print(f"Sampled {len(sampled)} papers using '{args.strategy}' strategy")

    # Create annotation template
    template = create_annotation_template(sampled, results, schema)

    # Save template
    output_path = Path(args.output)
    save_template(template, output_path)

    print(f"\n{'='*60}")
    print("Validation Set Preparation Complete")
    print(f"{'='*60}")
    print(f"Annotation file created: {output_path}")
    print(f"Papers to annotate: {len(sampled)}")
    print(f"\nNext steps:")
    print(f"1. Open {output_path} in a text editor")
    print(f"2. For each paper, read the PDF and fill in the 'ground_truth' field")
    print(f"3. Follow the schema structure shown in '_instructions'")
    print(f"4. Save your annotations")
    print(f"5. Run: python 08_calculate_validation_metrics.py --annotations {output_path}")
    print(f"\nTips for efficient annotation:")
    print(f"- Work in batches of 5-10 papers")
    print(f"- Use the automated extraction as a starting point to check")
    print(f"- Document any ambiguous cases in the notes field")
    print(f"- Consider having 2+ annotators for inter-rater reliability")


if __name__ == '__main__':
    main()
