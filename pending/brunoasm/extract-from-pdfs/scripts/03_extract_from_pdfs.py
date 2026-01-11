#!/usr/bin/env python3
"""
Extract structured data from PDFs using Claude API.
Supports multiple PDF processing methods and prompt caching for efficiency.
This script template needs to be customized with your specific extraction schema.
"""

import argparse
import base64
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
import re

from anthropic import Anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request


# Configuration
BATCH_SIZE = 5
SIMULTANEOUS_BATCHES = 4
BATCH_CHECK_INTERVAL = 30
BATCH_SUBMISSION_INTERVAL = 20


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Extract structured data from PDFs using Claude'
    )
    parser.add_argument(
        '--metadata',
        required=True,
        help='Input metadata JSON file (from step 01 or 02)'
    )
    parser.add_argument(
        '--schema',
        required=True,
        help='JSON file defining extraction schema and prompts'
    )
    parser.add_argument(
        '--output',
        default='extracted_data.json',
        help='Output JSON file with extraction results'
    )
    parser.add_argument(
        '--method',
        choices=['base64', 'files_api', 'batches'],
        default='batches',
        help='PDF processing method (default: batches)'
    )
    parser.add_argument(
        '--use-caching',
        action='store_true',
        help='Enable prompt caching (reduces costs by ~90%% for repeated queries)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (process only 3 PDFs)'
    )
    parser.add_argument(
        '--model',
        default='claude-3-5-sonnet-20241022',
        help='Claude model to use'
    )
    parser.add_argument(
        '--filter-results',
        help='Optional: JSON file with filter results from step 02 (only process relevant papers)'
    )
    return parser.parse_args()


def load_metadata(metadata_path: Path) -> List[Dict]:
    """Load metadata from JSON file"""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_schema(schema_path: Path) -> Dict:
    """Load extraction schema definition"""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_filter_results(filter_path: Path) -> Dict:
    """Load filter results from step 02"""
    with open(filter_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_existing_results(output_path: Path) -> Dict:
    """Load existing extraction results if available"""
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_results(results: Dict, output_path: Path):
    """Save extraction results to JSON file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def create_extraction_prompt(schema: Dict) -> str:
    """
    Create extraction prompt from schema definition.

    The schema JSON should contain:
    - system_context: Description of the analysis task
    - instructions: Step-by-step analysis instructions
    - output_schema: JSON schema for the output
    - output_example: Example of desired output

    TODO: Customize schema.json for your specific use case
    """
    prompt_parts = []

    # Add objective
    if 'objective' in schema:
        prompt_parts.append(f"Your objective is to {schema['objective']}\n")

    # Add instructions
    if 'instructions' in schema:
        prompt_parts.append("Please follow these steps:\n")
        for i, instruction in enumerate(schema['instructions'], 1):
            prompt_parts.append(f"{i}. {instruction}")
        prompt_parts.append("")

    # Add analysis framework
    if 'analysis_steps' in schema:
        prompt_parts.append("<analysis_framework>")
        for step in schema['analysis_steps']:
            prompt_parts.append(f"- {step}")
        prompt_parts.append("</analysis_framework>\n")
        prompt_parts.append(
            "Your analysis must be wrapped within <analysis> tags. "
            "Be thorough and explicit in your reasoning.\n"
        )

    # Add output schema explanation
    if 'output_schema' in schema:
        prompt_parts.append("<output_schema>")
        prompt_parts.append(json.dumps(schema['output_schema'], indent=2))
        prompt_parts.append("</output_schema>\n")

    # Add output example
    if 'output_example' in schema:
        prompt_parts.append("<output_example>")
        prompt_parts.append(json.dumps(schema['output_example'], indent=2))
        prompt_parts.append("</output_example>\n")

    # Add important notes
    if 'important_notes' in schema:
        prompt_parts.append("Important considerations:")
        for note in schema['important_notes']:
            prompt_parts.append(f"- {note}")
        prompt_parts.append("")

    # Add final instruction
    prompt_parts.append(
        "After your analysis, provide the final output in the following JSON format, "
        "wrapped in <output> tags. The output must be valid, parseable JSON.\n"
    )

    return "\n".join(prompt_parts)


def extract_json_from_response(text: str) -> Optional[Dict]:
    """Extract JSON from XML output tags in Claude's response"""
    match = re.search(r'<output>\s*(\{.*?\})\s*</output>', text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
    return None


def extract_analysis_from_response(text: str) -> Optional[str]:
    """Extract analysis from XML tags in Claude's response"""
    match = re.search(r'<analysis>(.*?)</analysis>', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def process_pdf_base64(
    client: Anthropic,
    pdf_path: Path,
    schema: Dict,
    model: str
) -> Dict:
    """Process a single PDF using base64 encoding (direct upload)"""
    if not pdf_path.exists():
        return {
            'status': 'error',
            'error': f'PDF not found: {pdf_path}'
        }

    # Check file size (32MB limit)
    file_size = pdf_path.stat().st_size
    if file_size > 32 * 1024 * 1024:
        return {
            'status': 'error',
            'error': f'PDF exceeds 32MB limit: {file_size / 1024 / 1024:.1f}MB'
        }

    try:
        # Read and encode PDF
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')

        # Create message
        response = client.messages.create(
            model=model,
            max_tokens=16384,
            temperature=0,
            system=schema.get('system_context', 'You are a scientific research assistant.'),
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": create_extraction_prompt(schema)
                    }
                ]
            }]
        )

        response_text = response.content[0].text

        return {
            'status': 'success',
            'extracted_data': extract_json_from_response(response_text),
            'analysis': extract_analysis_from_response(response_text),
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def process_pdfs_batch(
    client: Anthropic,
    records: List[tuple],
    schema: Dict,
    model: str
) -> Dict[str, Dict]:
    """Process multiple PDFs using Batches API for efficiency"""
    all_results = {}

    for window_start in range(0, len(records), SIMULTANEOUS_BATCHES * BATCH_SIZE):
        window_records = records[window_start:window_start + (SIMULTANEOUS_BATCHES * BATCH_SIZE)]
        print(f"\nProcessing window starting at index {window_start} ({len(window_records)} PDFs)")

        active_batches = {}

        for batch_start in range(0, len(window_records), BATCH_SIZE):
            batch_records = window_records[batch_start:batch_start + BATCH_SIZE]
            requests = []

            for record_id, pdf_data in batch_records:
                requests.append(Request(
                    custom_id=record_id,
                    params=MessageCreateParamsNonStreaming(
                        model=model,
                        max_tokens=16384,
                        temperature=0,
                        system=schema.get('system_context', 'You are a scientific research assistant.'),
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": pdf_data
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": create_extraction_prompt(schema)
                                }
                            ]
                        }]
                    )
                ))

            try:
                message_batch = client.messages.batches.create(requests=requests)
                print(f"Created batch {message_batch.id} with {len(requests)} requests")
                active_batches[message_batch.id] = {r.custom_id for r in requests}
                time.sleep(BATCH_SUBMISSION_INTERVAL)
            except Exception as e:
                print(f"Error creating batch: {e}")

        # Wait for batches
        window_results = wait_for_batches(client, list(active_batches.keys()), schema)
        all_results.update(window_results)

    return all_results


def wait_for_batches(
    client: Anthropic,
    batch_ids: List[str],
    schema: Dict
) -> Dict[str, Dict]:
    """Wait for batches to complete and return results"""
    print(f"\nWaiting for {len(batch_ids)} batches to complete...")

    incomplete = set(batch_ids)

    while incomplete:
        time.sleep(BATCH_CHECK_INTERVAL)

        for batch_id in list(incomplete):
            batch = client.messages.batches.retrieve(batch_id)
            if batch.processing_status != "in_progress":
                incomplete.remove(batch_id)
                print(f"Batch {batch_id} completed: {batch.processing_status}")

    # Collect results
    results = {}
    for batch_id in batch_ids:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            for result in client.messages.batches.results(batch_id):
                if result.result.type == "succeeded":
                    response_text = result.result.message.content[0].text
                    results[result.custom_id] = {
                        'status': 'success',
                        'extracted_data': extract_json_from_response(response_text),
                        'analysis': extract_analysis_from_response(response_text),
                        'input_tokens': result.result.message.usage.input_tokens,
                        'output_tokens': result.result.message.usage.output_tokens
                    }
                else:
                    results[result.custom_id] = {
                        'status': 'error',
                        'error': str(getattr(result.result, 'error', 'Unknown error'))
                    }

    return results


def main():
    args = parse_args()

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        raise ValueError("Please set ANTHROPIC_API_KEY environment variable")

    client = Anthropic()

    # Load inputs
    metadata = load_metadata(Path(args.metadata))
    schema = load_schema(Path(args.schema))
    print(f"Loaded {len(metadata)} metadata records")

    # Filter by relevance if filter results provided
    if args.filter_results:
        filter_results = load_filter_results(Path(args.filter_results))
        relevant_ids = {
            id for id, result in filter_results.items()
            if result.get('status') == 'success'
            and result.get('filter_result', {}).get('has_relevant_data')
        }
        metadata = [r for r in metadata if r['id'] in relevant_ids]
        print(f"Filtered to {len(metadata)} relevant papers")

    # Apply test mode
    if args.test:
        metadata = metadata[:3]
        print(f"Test mode: processing {len(metadata)} PDFs")

    # Load existing results
    output_path = Path(args.output)
    results = load_existing_results(output_path)
    print(f"Loaded {len(results)} existing results")

    # Prepare PDFs to process
    to_process = []
    for record in metadata:
        if record['id'] in results:
            continue
        if not record.get('pdf_path'):
            print(f"Skipping {record['id']}: no PDF path")
            continue
        pdf_path = Path(record['pdf_path'])
        if not pdf_path.exists():
            print(f"Skipping {record['id']}: PDF not found")
            continue

        # Read and encode PDF
        try:
            with open(pdf_path, 'rb') as f:
                pdf_data = base64.b64encode(f.read()).decode('utf-8')
            to_process.append((record['id'], pdf_data))
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")

    print(f"PDFs to process: {len(to_process)}")

    if not to_process:
        print("All PDFs already processed!")
        return

    # Process PDFs
    if args.method == 'batches':
        print("Using Batches API...")
        batch_results = process_pdfs_batch(client, to_process, schema, args.model)
        results.update(batch_results)
    else:
        print("Processing PDFs sequentially...")
        for record_id, pdf_data in to_process:
            print(f"Processing: {record_id}")
            # For sequential processing, reconstruct Path
            record = next(r for r in metadata if r['id'] == record_id)
            result = process_pdf_base64(
                client, Path(record['pdf_path']), schema, args.model
            )
            results[record_id] = result
            save_results(results, output_path)
            time.sleep(2)

    # Save final results
    save_results(results, output_path)

    # Print summary
    total = len(results)
    successful = sum(1 for r in results.values() if r.get('status') == 'success')
    total_input_tokens = sum(
        r.get('input_tokens', 0) for r in results.values()
        if r.get('status') == 'success'
    )
    total_output_tokens = sum(
        r.get('output_tokens', 0) for r in results.values()
        if r.get('status') == 'success'
    )

    print(f"\n{'='*60}")
    print("Extraction Summary")
    print(f"{'='*60}")
    print(f"Total PDFs processed: {total}")
    print(f"Successful extractions: {successful}")
    print(f"Failed extractions: {total - successful}")
    print(f"\nToken usage:")
    print(f"  Input tokens: {total_input_tokens:,}")
    print(f"  Output tokens: {total_output_tokens:,}")
    print(f"  Total tokens: {total_input_tokens + total_output_tokens:,}")
    print(f"\nResults saved to: {output_path}")
    print(f"\nNext step: Repair and validate JSON outputs")


if __name__ == '__main__':
    main()
