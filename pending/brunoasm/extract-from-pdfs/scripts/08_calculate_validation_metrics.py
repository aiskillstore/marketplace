#!/usr/bin/env python3
"""
Calculate validation metrics (precision, recall, F1) for extraction quality.

Compares automated extraction against ground truth annotations to evaluate:
- Field-level precision and recall
- Record-level accuracy
- Overall extraction quality

Handles different data types appropriately:
- Boolean: exact match
- Numeric: exact match or tolerance
- String: exact match or fuzzy matching
- Lists: set-based precision/recall
- Nested objects: recursive comparison
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
import sys


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Calculate validation metrics for extraction quality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Metrics calculated:
  Precision : Of extracted items, how many are correct?
  Recall    : Of true items, how many were extracted?
  F1 Score  : Harmonic mean of precision and recall
  Accuracy  : Overall correctness (for boolean/categorical fields)

Field type handling:
  Boolean/Categorical : Exact match
  Numeric            : Exact match or within tolerance
  String             : Exact match or fuzzy (normalized)
  Lists              : Set-based precision/recall
  Nested objects     : Recursive field-by-field comparison

Output:
  - Overall metrics
  - Per-field metrics
  - Per-paper detailed comparison
  - Common error patterns
        """
    )
    parser.add_argument(
        '--annotations',
        required=True,
        help='Annotation file from 07_prepare_validation_set.py (with ground truth filled in)'
    )
    parser.add_argument(
        '--output',
        default='validation_metrics.json',
        help='Output file for detailed metrics'
    )
    parser.add_argument(
        '--report',
        default='validation_report.txt',
        help='Human-readable validation report'
    )
    parser.add_argument(
        '--numeric-tolerance',
        type=float,
        default=0.0,
        help='Tolerance for numeric comparisons (default: 0.0 for exact match)'
    )
    parser.add_argument(
        '--fuzzy-strings',
        action='store_true',
        help='Use fuzzy string matching (normalize whitespace, case)'
    )
    parser.add_argument(
        '--list-order-matters',
        action='store_true',
        help='Consider order in list comparisons (default: treat as sets)'
    )
    return parser.parse_args()


def load_annotations(annotations_path: Path) -> Dict:
    """Load annotations file"""
    with open(annotations_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_string(s: str, fuzzy: bool = False) -> str:
    """Normalize string for comparison"""
    if not isinstance(s, str):
        return str(s)
    if fuzzy:
        return ' '.join(s.lower().split())
    return s


def compare_boolean(automated: Any, truth: Any) -> Dict[str, int]:
    """Compare boolean values"""
    if automated == truth:
        return {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}
    elif automated and not truth:
        return {'tp': 0, 'fp': 1, 'fn': 0, 'tn': 0}
    elif not automated and truth:
        return {'tp': 0, 'fp': 0, 'fn': 1, 'tn': 0}
    else:
        return {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 1}


def compare_numeric(automated: Any, truth: Any, tolerance: float = 0.0) -> bool:
    """Compare numeric values with optional tolerance"""
    try:
        a = float(automated) if automated is not None else None
        t = float(truth) if truth is not None else None

        if a is None and t is None:
            return True
        if a is None or t is None:
            return False

        if tolerance > 0:
            return abs(a - t) <= tolerance
        else:
            return a == t
    except (ValueError, TypeError):
        return automated == truth


def compare_string(automated: Any, truth: Any, fuzzy: bool = False) -> bool:
    """Compare string values"""
    if automated is None and truth is None:
        return True
    if automated is None or truth is None:
        return False

    a = normalize_string(automated, fuzzy)
    t = normalize_string(truth, fuzzy)
    return a == t


def compare_list(
    automated: List,
    truth: List,
    order_matters: bool = False,
    fuzzy: bool = False
) -> Dict[str, int]:
    """
    Compare lists and calculate precision/recall.

    Returns counts of true positives, false positives, and false negatives.
    """
    if automated is None:
        automated = []
    if truth is None:
        truth = []

    if not isinstance(automated, list):
        automated = [automated]
    if not isinstance(truth, list):
        truth = [truth]

    if order_matters:
        # Ordered comparison
        tp = sum(1 for a, t in zip(automated, truth) if compare_string(a, t, fuzzy))
        fp = max(0, len(automated) - len(truth))
        fn = max(0, len(truth) - len(automated))
    else:
        # Set-based comparison
        if fuzzy:
            auto_set = {normalize_string(x, fuzzy) for x in automated}
            truth_set = {normalize_string(x, fuzzy) for x in truth}
        else:
            auto_set = set(automated)
            truth_set = set(truth)

        tp = len(auto_set & truth_set)  # Intersection
        fp = len(auto_set - truth_set)  # In automated but not in truth
        fn = len(truth_set - auto_set)  # In truth but not in automated

    return {'tp': tp, 'fp': fp, 'fn': fn}


def calculate_metrics(tp: int, fp: int, fn: int) -> Dict[str, float]:
    """Calculate precision, recall, and F1 from counts"""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp,
        'fp': fp,
        'fn': fn
    }


def compare_field(
    automated: Any,
    truth: Any,
    field_name: str,
    config: Dict
) -> Dict[str, Any]:
    """
    Compare a single field between automated and ground truth.

    Returns metrics appropriate for the field type.
    """
    # Determine field type
    if isinstance(truth, bool):
        return compare_boolean(automated, truth)
    elif isinstance(truth, (int, float)):
        match = compare_numeric(automated, truth, config['numeric_tolerance'])
        return {'tp': 1 if match else 0, 'fp': 0 if match else 1, 'fn': 0 if match else 1}
    elif isinstance(truth, str):
        match = compare_string(automated, truth, config['fuzzy_strings'])
        return {'tp': 1 if match else 0, 'fp': 0 if match else 1, 'fn': 0 if match else 1}
    elif isinstance(truth, list):
        return compare_list(automated, truth, config['list_order_matters'], config['fuzzy_strings'])
    elif isinstance(truth, dict):
        # Recursive comparison for nested objects
        return compare_nested(automated or {}, truth, config)
    elif truth is None:
        # Field should be empty/null
        if automated is None or automated == "" or automated == []:
            return {'tp': 1, 'fp': 0, 'fn': 0}
        else:
            return {'tp': 0, 'fp': 1, 'fn': 0}
    else:
        # Fallback to exact match
        match = automated == truth
        return {'tp': 1 if match else 0, 'fp': 0 if match else 1, 'fn': 0 if match else 1}


def compare_nested(automated: Dict, truth: Dict, config: Dict) -> Dict[str, int]:
    """Recursively compare nested objects"""
    total_counts = {'tp': 0, 'fp': 0, 'fn': 0}

    all_fields = set(automated.keys()) | set(truth.keys())

    for field in all_fields:
        auto_val = automated.get(field)
        truth_val = truth.get(field)

        field_counts = compare_field(auto_val, truth_val, field, config)

        for key in ['tp', 'fp', 'fn']:
            total_counts[key] += field_counts.get(key, 0)

    return total_counts


def evaluate_paper(
    paper_id: str,
    automated: Dict,
    truth: Dict,
    config: Dict
) -> Dict[str, Any]:
    """
    Evaluate extraction for a single paper.

    Returns field-level and overall metrics.
    """
    if truth is None:
        return {
            'status': 'not_annotated',
            'message': 'Ground truth not provided'
        }

    field_metrics = {}
    all_fields = set(automated.keys()) | set(truth.keys())

    for field in all_fields:
        if field == 'records':
            # Special handling for records arrays
            auto_records = automated.get('records', [])
            truth_records = truth.get('records', [])

            # Overall record count comparison
            record_counts = compare_list(auto_records, truth_records, order_matters=False)

            # Detailed record-level comparison
            record_details = []
            for i, (auto_rec, truth_rec) in enumerate(zip(auto_records, truth_records)):
                rec_comparison = compare_nested(auto_rec, truth_rec, config)
                record_details.append({
                    'record_index': i,
                    'metrics': calculate_metrics(**rec_comparison)
                })

            field_metrics['records'] = {
                'count_metrics': calculate_metrics(**record_counts),
                'record_details': record_details
            }
        else:
            auto_val = automated.get(field)
            truth_val = truth.get(field)
            counts = compare_field(auto_val, truth_val, field, config)
            field_metrics[field] = calculate_metrics(**counts)

    # Calculate overall metrics
    total_tp = sum(
        m.get('tp', 0) if isinstance(m, dict) and 'tp' in m
        else m.get('count_metrics', {}).get('tp', 0)
        for m in field_metrics.values()
    )
    total_fp = sum(
        m.get('fp', 0) if isinstance(m, dict) and 'fp' in m
        else m.get('count_metrics', {}).get('fp', 0)
        for m in field_metrics.values()
    )
    total_fn = sum(
        m.get('fn', 0) if isinstance(m, dict) and 'fn' in m
        else m.get('count_metrics', {}).get('fn', 0)
        for m in field_metrics.values()
    )

    overall = calculate_metrics(total_tp, total_fp, total_fn)

    return {
        'status': 'evaluated',
        'field_metrics': field_metrics,
        'overall': overall
    }


def aggregate_metrics(paper_evaluations: Dict[str, Dict]) -> Dict[str, Any]:
    """Aggregate metrics across all papers"""
    # Collect field-level metrics
    field_aggregates = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})

    evaluated_papers = [
        p for p in paper_evaluations.values()
        if p.get('status') == 'evaluated'
    ]

    for paper_eval in evaluated_papers:
        for field, metrics in paper_eval.get('field_metrics', {}).items():
            if isinstance(metrics, dict):
                if 'tp' in metrics:
                    # Simple field
                    field_aggregates[field]['tp'] += metrics['tp']
                    field_aggregates[field]['fp'] += metrics['fp']
                    field_aggregates[field]['fn'] += metrics['fn']
                elif 'count_metrics' in metrics:
                    # Records field
                    field_aggregates[field]['tp'] += metrics['count_metrics']['tp']
                    field_aggregates[field]['fp'] += metrics['count_metrics']['fp']
                    field_aggregates[field]['fn'] += metrics['count_metrics']['fn']

    # Calculate metrics for each field
    field_metrics = {}
    for field, counts in field_aggregates.items():
        field_metrics[field] = calculate_metrics(**counts)

    # Overall aggregated metrics
    total_tp = sum(counts['tp'] for counts in field_aggregates.values())
    total_fp = sum(counts['fp'] for counts in field_aggregates.values())
    total_fn = sum(counts['fn'] for counts in field_aggregates.values())

    overall = calculate_metrics(total_tp, total_fp, total_fn)

    return {
        'overall': overall,
        'by_field': field_metrics,
        'num_papers_evaluated': len(evaluated_papers)
    }


def generate_report(
    paper_evaluations: Dict[str, Dict],
    aggregated: Dict,
    output_path: Path
):
    """Generate human-readable validation report"""
    lines = []
    lines.append("="*80)
    lines.append("EXTRACTION VALIDATION REPORT")
    lines.append("="*80)
    lines.append("")

    # Overall summary
    lines.append("OVERALL METRICS")
    lines.append("-"*80)
    overall = aggregated['overall']
    lines.append(f"Papers evaluated: {aggregated['num_papers_evaluated']}")
    lines.append(f"Precision: {overall['precision']:.2%}")
    lines.append(f"Recall:    {overall['recall']:.2%}")
    lines.append(f"F1 Score:  {overall['f1']:.2%}")
    lines.append(f"True Positives:  {overall['tp']}")
    lines.append(f"False Positives: {overall['fp']}")
    lines.append(f"False Negatives: {overall['fn']}")
    lines.append("")

    # Per-field metrics
    lines.append("METRICS BY FIELD")
    lines.append("-"*80)
    lines.append(f"{'Field':<30} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    lines.append("-"*80)

    for field, metrics in sorted(aggregated['by_field'].items()):
        lines.append(
            f"{field:<30} "
            f"{metrics['precision']:>9.1%} "
            f"{metrics['recall']:>9.1%} "
            f"{metrics['f1']:>9.1%}"
        )
    lines.append("")

    # Top errors
    lines.append("COMMON ISSUES")
    lines.append("-"*80)

    # Fields with low recall (missed information)
    low_recall = [
        (field, metrics) for field, metrics in aggregated['by_field'].items()
        if metrics['recall'] < 0.7 and metrics['fn'] > 0
    ]
    if low_recall:
        lines.append("\nFields with low recall (missed information):")
        for field, metrics in sorted(low_recall, key=lambda x: x[1]['recall']):
            lines.append(f"  - {field}: {metrics['recall']:.1%} recall, {metrics['fn']} missed items")

    # Fields with low precision (incorrect extractions)
    low_precision = [
        (field, metrics) for field, metrics in aggregated['by_field'].items()
        if metrics['precision'] < 0.7 and metrics['fp'] > 0
    ]
    if low_precision:
        lines.append("\nFields with low precision (incorrect extractions):")
        for field, metrics in sorted(low_precision, key=lambda x: x[1]['precision']):
            lines.append(f"  - {field}: {metrics['precision']:.1%} precision, {metrics['fp']} incorrect items")

    lines.append("")
    lines.append("="*80)

    # Write report
    report_text = "\n".join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    # Also print to console
    print(report_text)


def main():
    args = parse_args()

    # Load annotations
    annotations = load_annotations(Path(args.annotations))
    validation_papers = annotations.get('validation_papers', {})

    print(f"Loaded {len(validation_papers)} validation papers")

    # Check how many have ground truth
    annotated = sum(1 for p in validation_papers.values() if p.get('ground_truth') is not None)
    print(f"Papers with ground truth: {annotated}")

    if annotated == 0:
        print("\nError: No ground truth annotations found!")
        print("Please fill in the 'ground_truth' field for each paper in the annotation file.")
        sys.exit(1)

    # Configuration for comparisons
    config = {
        'numeric_tolerance': args.numeric_tolerance,
        'fuzzy_strings': args.fuzzy_strings,
        'list_order_matters': args.list_order_matters
    }

    # Evaluate each paper
    paper_evaluations = {}
    for paper_id, paper_data in validation_papers.items():
        automated = paper_data.get('automated_extraction', {})
        truth = paper_data.get('ground_truth')

        evaluation = evaluate_paper(paper_id, automated, truth, config)
        paper_evaluations[paper_id] = evaluation

        if evaluation['status'] == 'evaluated':
            overall = evaluation['overall']
            print(f"{paper_id}: P={overall['precision']:.2%} R={overall['recall']:.2%} F1={overall['f1']:.2%}")

    # Aggregate metrics
    aggregated = aggregate_metrics(paper_evaluations)

    # Save detailed metrics
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    detailed_output = {
        'summary': aggregated,
        'by_paper': paper_evaluations,
        'config': config
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(detailed_output, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed metrics saved to: {output_path}")

    # Generate report
    report_path = Path(args.report)
    generate_report(paper_evaluations, aggregated, report_path)
    print(f"Validation report saved to: {report_path}")


if __name__ == '__main__':
    main()
