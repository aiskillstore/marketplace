#!/usr/bin/env python3
"""
Filter papers based on abstract content using Claude API or local models.
Reduces processing costs by identifying relevant papers before full PDF extraction.
This script template needs to be customized with your specific filtering criteria.

Supports:
- Claude Haiku (cheap, fast API option)
- Claude Sonnet (more accurate API option)
- Local models via Ollama (free, private, requires local setup)
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from anthropic import Anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Filter papers by analyzing abstracts with Claude or local models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Backend options:
  anthropic-haiku   : Claude 3 Haiku (cheap, fast, ~$0.25/million input tokens)
  anthropic-sonnet  : Claude 3.5 Sonnet (more accurate, ~$3/million input tokens)
  ollama            : Local model via Ollama (free, requires local setup)

Local model setup (Ollama):
  1. Install Ollama: https://ollama.com
  2. Pull a model: ollama pull llama3.1:8b
  3. Run server: ollama serve (usually starts automatically)
  4. Use --backend ollama --ollama-model llama3.1:8b

Recommended models for Ollama:
  - llama3.1:8b (good balance)
  - llama3.1:70b (better accuracy, needs more RAM)
  - mistral:7b (fast, good for simple filtering)
  - qwen2.5:7b (good multilingual support)
        """
    )
    parser.add_argument(
        '--metadata',
        required=True,
        help='Input metadata JSON file from step 01'
    )
    parser.add_argument(
        '--output',
        default='filtered_papers.json',
        help='Output JSON file with filter results'
    )
    parser.add_argument(
        '--backend',
        choices=['anthropic-haiku', 'anthropic-sonnet', 'ollama'],
        default='anthropic-haiku',
        help='Model backend to use (default: anthropic-haiku for cost efficiency)'
    )
    parser.add_argument(
        '--ollama-model',
        default='llama3.1:8b',
        help='Ollama model name (default: llama3.1:8b)'
    )
    parser.add_argument(
        '--ollama-url',
        default='http://localhost:11434',
        help='Ollama server URL (default: http://localhost:11434)'
    )
    parser.add_argument(
        '--use-batches',
        action='store_true',
        help='Use Anthropic Batches API (only for anthropic backends)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (process only 10 records)'
    )
    return parser.parse_args()


def load_metadata(metadata_path: Path) -> List[Dict]:
    """Load metadata from JSON file"""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_existing_results(output_path: Path) -> Dict:
    """Load existing filter results if available"""
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_results(results: Dict, output_path: Path):
    """Save filter results to JSON file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def create_filter_prompt(title: str, abstract: str) -> str:
    """
    Create the filtering prompt.

    TODO: CUSTOMIZE THIS PROMPT FOR YOUR SPECIFIC USE CASE

    This is a template. Replace the example criteria with your own.
    """
    return f"""You are analyzing scientific literature to identify relevant papers for a research project.

<title>
{title}
</title>

<abstract>
{abstract}
</abstract>

Your task is to determine if this paper meets the following criteria:

TODO: Replace these example criteria with your own:

1. Does the paper contain PRIMARY empirical data (not review/meta-analysis)?
2. Does the paper report [YOUR SPECIFIC DATA TYPE, e.g., "field observations", "experimental measurements", "clinical outcomes"]?
3. Is the geographic/temporal/taxonomic scope relevant to [YOUR STUDY SYSTEM]?

Important considerations:
- Be conservative: when in doubt, include the paper (false positives are better than false negatives)
- Distinguish between primary data and citations of others' work
- Consider whether the abstract suggests the full paper likely contains the data of interest

Provide your determination as a JSON object with these boolean fields:
1. "has_relevant_data": true if the paper likely contains the data type of interest
2. "is_primary_research": true if the paper reports original empirical data
3. "meets_scope": true if the study system/scope is relevant

Also provide:
4. "confidence": your confidence level (high/medium/low)
5. "reasoning": brief explanation (1-2 sentences)

Wrap your response in <output> tags. Example:
<output>
{{
  "has_relevant_data": true,
  "is_primary_research": true,
  "meets_scope": true,
  "confidence": "high",
  "reasoning": "Abstract explicitly mentions field observations of the target phenomenon in the relevant geographic region."
}}
</output>

Base your determination solely on the title and abstract provided."""


def extract_json_from_xml(text: str) -> Dict:
    """Extract JSON from XML output tags in Claude's response"""
    import re

    match = re.search(r'<output>\s*(\{.*?\})\s*</output>', text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"JSON string: {json_str}")
            return None
    return None


def filter_paper_ollama(record: Dict, ollama_url: str, ollama_model: str) -> Dict:
    """Use local Ollama model to filter a single paper"""
    if not REQUESTS_AVAILABLE:
        return {
            'status': 'error',
            'reason': 'requests library not available. Install with: pip install requests'
        }

    if not record.get('title') or not record.get('abstract'):
        return {
            'status': 'skipped',
            'reason': 'missing_title_or_abstract'
        }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Ollama uses OpenAI-compatible chat API
            response = requests.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": ollama_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a scientific literature analyst specializing in identifying relevant papers for systematic reviews and meta-analyses."
                        },
                        {
                            "role": "user",
                            "content": create_filter_prompt(record['title'], record['abstract'])
                        }
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0,
                        "num_predict": 2048
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get('message', {}).get('content', '')
                result = extract_json_from_xml(content)

                if result:
                    return {
                        'status': 'success',
                        'filter_result': result,
                        'model_used': ollama_model
                    }
                else:
                    return {
                        'status': 'error',
                        'reason': 'failed_to_parse_json',
                        'raw_response': content[:500]
                    }
            else:
                return {
                    'status': 'error',
                    'reason': f'Ollama API error: {response.status_code} {response.text[:200]}'
                }

        except requests.exceptions.ConnectionError:
            return {
                'status': 'error',
                'reason': f'Cannot connect to Ollama at {ollama_url}. Make sure Ollama is running: ollama serve'
            }
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    'status': 'error',
                    'reason': str(e)
                }
            time.sleep(2 ** attempt)


def filter_paper_direct(client: Anthropic, record: Dict, model: str) -> Dict:
    """Use Claude API directly to filter a single paper"""
    if not record.get('title') or not record.get('abstract'):
        return {
            'status': 'skipped',
            'reason': 'missing_title_or_abstract'
        }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                temperature=0,
                system="You are a scientific literature analyst specializing in identifying relevant papers for systematic reviews and meta-analyses.",
                messages=[{
                    "role": "user",
                    "content": create_filter_prompt(record['title'], record['abstract'])
                }]
            )

            result = extract_json_from_xml(response.content[0].text)
            if result:
                return {
                    'status': 'success',
                    'filter_result': result,
                    'model_used': model
                }
            else:
                return {
                    'status': 'error',
                    'reason': 'failed_to_parse_json'
                }

        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    'status': 'error',
                    'reason': str(e)
                }
            time.sleep(2 ** attempt)


def filter_papers_batch(client: Anthropic, records: List[Dict], model: str) -> Dict[str, Dict]:
    """Use Claude Batches API to filter multiple papers efficiently"""
    requests = []

    for record in records:
        if not record.get('title') or not record.get('abstract'):
            continue

        requests.append(Request(
            custom_id=record['id'],
            params=MessageCreateParamsNonStreaming(
                model=model,
                max_tokens=2048,
                temperature=0,
                system="You are a scientific literature analyst specializing in identifying relevant papers for systematic reviews and meta-analyses.",
                messages=[{
                    "role": "user",
                    "content": create_filter_prompt(record['title'], record['abstract'])
                }]
            )
        ))

    if not requests:
        print("No papers to process (missing titles or abstracts)")
        return {}

    # Create batch
    print(f"Creating batch with {len(requests)} requests...")
    message_batch = client.messages.batches.create(requests=requests)
    print(f"Batch created: {message_batch.id}")

    # Poll for completion
    while message_batch.processing_status == "in_progress":
        print("Waiting for batch processing...")
        time.sleep(30)
        message_batch = client.messages.batches.retrieve(message_batch.id)

    # Process results
    results = {}
    if message_batch.processing_status == "ended":
        print("Batch completed. Processing results...")
        for result in client.messages.batches.results(message_batch.id):
            if result.result.type == "succeeded":
                filter_result = extract_json_from_xml(
                    result.result.message.content[0].text
                )
                if filter_result:
                    results[result.custom_id] = {
                        'status': 'success',
                        'filter_result': filter_result
                    }
                else:
                    results[result.custom_id] = {
                        'status': 'error',
                        'reason': 'failed_to_parse_json'
                    }
            else:
                results[result.custom_id] = {
                    'status': 'error',
                    'reason': f"{result.result.type}: {getattr(result.result, 'error', 'unknown error')}"
                }
    else:
        print(f"Batch failed with status: {message_batch.processing_status}")

    return results


def get_model_name(backend: str) -> str:
    """Get the appropriate model name for the backend"""
    if backend == 'anthropic-haiku':
        return 'claude-3-5-haiku-20241022'
    elif backend == 'anthropic-sonnet':
        return 'claude-3-5-sonnet-20241022'
    return backend


def main():
    args = parse_args()

    # Backend-specific setup
    client = None
    if args.backend.startswith('anthropic'):
        if not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("Please set ANTHROPIC_API_KEY environment variable for Anthropic backends")
        client = Anthropic()
        model = get_model_name(args.backend)
        print(f"Using Anthropic backend: {model}")
    elif args.backend == 'ollama':
        if args.use_batches:
            print("Warning: Batches API not available for Ollama. Processing sequentially.")
            args.use_batches = False
        print(f"Using Ollama backend: {args.ollama_model} at {args.ollama_url}")
        print("Make sure Ollama is running: ollama serve")

    # Load metadata
    metadata = load_metadata(Path(args.metadata))
    print(f"Loaded {len(metadata)} metadata records")

    # Apply test mode if specified
    if args.test:
        metadata = metadata[:10]
        print(f"Test mode: processing {len(metadata)} records")

    # Load existing results
    output_path = Path(args.output)
    results = load_existing_results(output_path)
    print(f"Loaded {len(results)} existing results")

    # Identify papers to process
    to_process = [r for r in metadata if r['id'] not in results]
    print(f"Papers to process: {len(to_process)}")

    if not to_process:
        print("All papers already processed!")
        return

    # Process papers based on backend
    if args.backend == 'ollama':
        print("Processing papers with Ollama...")
        for record in to_process:
            print(f"Processing: {record['id']}")
            result = filter_paper_ollama(record, args.ollama_url, args.ollama_model)
            results[record['id']] = result
            save_results(results, output_path)
            # No sleep needed for local models
    elif args.use_batches:
        print("Using Batches API...")
        batch_results = filter_papers_batch(client, to_process, model)
        results.update(batch_results)
    else:
        print("Processing papers sequentially with Anthropic API...")
        for record in to_process:
            print(f"Processing: {record['id']}")
            result = filter_paper_direct(client, record, model)
            results[record['id']] = result
            save_results(results, output_path)
            time.sleep(1)  # Rate limiting

    # Save final results
    save_results(results, output_path)

    # Print summary statistics
    total = len(results)
    successful = sum(1 for r in results.values() if r.get('status') == 'success')
    relevant = sum(
        1 for r in results.values()
        if r.get('status') == 'success' and r.get('filter_result', {}).get('has_relevant_data')
    )

    print(f"\n{'='*60}")
    print("Filtering Summary")
    print(f"{'='*60}")
    print(f"Total papers processed: {total}")
    print(f"Successfully analyzed: {successful}")
    print(f"Papers with relevant data: {relevant}")
    print(f"Relevance rate: {relevant/successful*100:.1f}%" if successful > 0 else "N/A")
    print(f"\nResults saved to: {output_path}")
    print(f"\nNext step: Review results and proceed to PDF extraction for relevant papers")


if __name__ == '__main__':
    main()
