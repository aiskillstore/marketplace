#!/usr/bin/env python3
"""
Repair and validate JSON extractions using json_repair library.
Handles common JSON parsing issues and validates against schema.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional
import jsonschema

try:
    from json_repair import repair_json
    JSON_REPAIR_AVAILABLE = True
except ImportError:
    JSON_REPAIR_AVAILABLE = False
    print("Warning: json_repair not installed. Install with: pip install json-repair")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Repair and validate JSON extractions'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input JSON file with extraction results from step 03'
    )
    parser.add_argument(
        '--output',
        default='cleaned_extractions.json',
        help='Output JSON file with cleaned results'
    )
    parser.add_argument(
        '--schema',
        help='Optional: JSON schema file for validation'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Strict mode: reject records that fail validation'
    )
    return parser.parse_args()


def load_results(input_path: Path) -> Dict:
    """Load extraction results from JSON file"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_schema(schema_path: Path) -> Dict:
    """Load JSON schema for validation"""
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    return schema_data.get('output_schema', schema_data)


def save_results(results: Dict, output_path: Path):
    """Save cleaned results to JSON file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def repair_json_data(data: Any) -> tuple[Any, bool]:
    """
    Attempt to repair JSON data using json_repair library.
    Returns (repaired_data, success)
    """
    if not JSON_REPAIR_AVAILABLE:
        return data, True  # Skip repair if library not available

    try:
        # Convert to JSON string and back to repair
        json_str = json.dumps(data)
        repaired_str = repair_json(json_str, return_objects=False)
        repaired_data = json.loads(repaired_str)
        return repaired_data, True
    except Exception as e:
        print(f"Failed to repair JSON: {e}")
        return data, False


def validate_against_schema(data: Any, schema: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate data against JSON schema.
    Returns (is_valid, error_message)
    """
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def clean_extraction_result(
    result: Dict,
    schema: Optional[Dict] = None,
    strict: bool = False
) -> Dict:
    """
    Clean and validate a single extraction result.

    Returns updated result with:
    - repaired_data: Repaired JSON if repair was needed
    - validation_status: 'valid', 'invalid', or 'repaired'
    - validation_errors: List of validation errors if any
    """
    if result.get('status') != 'success':
        return result  # Skip non-successful results

    extracted_data = result.get('extracted_data')
    if not extracted_data:
        result['validation_status'] = 'invalid'
        result['validation_errors'] = ['No extracted data found']
        if strict:
            result['status'] = 'failed_validation'
        return result

    # Try to repair JSON
    repaired_data, repair_success = repair_json_data(extracted_data)

    # Validate against schema if provided
    validation_errors = []
    if schema:
        is_valid, error_msg = validate_against_schema(repaired_data, schema)
        if not is_valid:
            validation_errors.append(error_msg)
            if strict:
                result['status'] = 'failed_validation'

    # Update result
    if repaired_data != extracted_data and repair_success:
        result['extracted_data'] = repaired_data
        result['validation_status'] = 'repaired'
    elif validation_errors:
        result['validation_status'] = 'invalid'
    else:
        result['validation_status'] = 'valid'

    if validation_errors:
        result['validation_errors'] = validation_errors

    return result


def main():
    args = parse_args()

    # Load inputs
    results = load_results(Path(args.input))
    print(f"Loaded {len(results)} extraction results")

    schema = None
    if args.schema:
        schema = load_schema(Path(args.schema))
        print(f"Loaded validation schema from {args.schema}")

    # Clean each result
    cleaned_results = {}
    stats = {
        'total': len(results),
        'valid': 0,
        'repaired': 0,
        'invalid': 0,
        'failed': 0
    }

    for record_id, result in results.items():
        cleaned_result = clean_extraction_result(result, schema, args.strict)
        cleaned_results[record_id] = cleaned_result

        # Update statistics
        if cleaned_result.get('status') == 'success':
            status = cleaned_result.get('validation_status', 'unknown')
            if status == 'valid':
                stats['valid'] += 1
            elif status == 'repaired':
                stats['repaired'] += 1
            elif status == 'invalid':
                stats['invalid'] += 1
        else:
            stats['failed'] += 1

    # Save cleaned results
    output_path = Path(args.output)
    save_results(cleaned_results, output_path)

    # Print summary
    print(f"\n{'='*60}")
    print("JSON Repair and Validation Summary")
    print(f"{'='*60}")
    print(f"Total records: {stats['total']}")
    print(f"Valid JSON: {stats['valid']}")
    print(f"Repaired JSON: {stats['repaired']}")
    print(f"Invalid JSON: {stats['invalid']}")
    print(f"Failed extractions: {stats['failed']}")

    if schema:
        validation_rate = (stats['valid'] + stats['repaired']) / stats['total'] * 100
        print(f"\nValidation rate: {validation_rate:.1f}%")

    print(f"\nCleaned results saved to: {output_path}")

    # Print examples of validation errors
    if stats['invalid'] > 0:
        print(f"\nShowing first 3 validation errors:")
        error_count = 0
        for record_id, result in cleaned_results.items():
            if result.get('validation_errors'):
                print(f"\n{record_id}:")
                for error in result['validation_errors'][:2]:
                    print(f"  - {error[:200]}")
                error_count += 1
                if error_count >= 3:
                    break

    print(f"\nNext step: Validate and enrich data with external APIs")


if __name__ == '__main__':
    main()
