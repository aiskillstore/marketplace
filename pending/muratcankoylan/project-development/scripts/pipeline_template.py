"""
LLM Batch Processing Pipeline Template

A template demonstrating the staged pipeline architecture for LLM batch processing.
Customize the acquire, prepare, process, parse, and render functions for your use case.

Usage:
    python pipeline_template.py acquire --batch-id 2025-01-15
    python pipeline_template.py prepare --batch-id 2025-01-15
    python pipeline_template.py process --batch-id 2025-01-15 --workers 10
    python pipeline_template.py parse --batch-id 2025-01-15
    python pipeline_template.py render --batch-id 2025-01-15
    python pipeline_template.py all --batch-id 2025-01-15
    python pipeline_template.py clean --batch-id 2025-01-15 --clean-stage process
    python pipeline_template.py estimate --batch-id 2025-01-15
"""

import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Any


# -----------------------------------------------------------------------------
# Configuration - Customize for your use case
# -----------------------------------------------------------------------------

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")

# Prompt template with structured output requirements
PROMPT_TEMPLATE = """Analyze the following content and provide your response in exactly this format.

## Summary
[2-3 sentence summary of the content]

## Key Points
- [Point 1]
- [Point 2]
- [Point 3]

## Score
Rating: [1-10]
Confidence: [low/medium/high]

## Reasoning
[Explanation of your analysis]

Follow this format exactly because I will be parsing it programmatically.

---

# Content to Analyze

Title: {title}

{content}
"""


# -----------------------------------------------------------------------------
# Data Structures
# -----------------------------------------------------------------------------

@dataclass
class Item:
    """Represents a single item to process."""
    id: str
    title: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedResult:
    """Structured result from LLM response parsing."""
    summary: str = ""
    key_points: list[str] = field(default_factory=list)
    score: int | None = None
    confidence: str = ""
    reasoning: str = ""
    parse_errors: list[str] = field(default_factory=list)


# -----------------------------------------------------------------------------
# Path Utilities
# -----------------------------------------------------------------------------

def get_batch_dir(batch_id: str) -> Path:
    """Get the data directory for a batch."""
    return DATA_DIR / batch_id


def get_item_dir(batch_id: str, item_id: str) -> Path:
    """Get the directory for a specific item."""
    return get_batch_dir(batch_id) / item_id


def get_output_dir(batch_id: str) -> Path:
    """Get the output directory for a batch."""
    return OUTPUT_DIR / batch_id


# -----------------------------------------------------------------------------
# Stage: Acquire
# -----------------------------------------------------------------------------

def stage_acquire(batch_id: str, limit: int | None = None):
    """
    Stage 1: Acquire raw data.
    
    Customize this function to fetch data from your sources:
    - APIs
    - Databases
    - File systems
    - Web scraping
    
    Output: {batch_dir}/{item_id}/raw.json
    """
    batch_dir = get_batch_dir(batch_id)
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    # CUSTOMIZE: Replace with your data acquisition logic
    items = fetch_items_from_source(limit)
    
    for item in items:
        item_dir = get_item_dir(batch_id, item.id)
        item_dir.mkdir(exist_ok=True)
        
        raw_file = item_dir / "raw.json"
        if not raw_file.exists():
            with open(raw_file, "w") as f:
                json.dump(asdict(item), f, indent=2)
            print(f"Acquired: {item.id}")
        else:
            print(f"Cached: {item.id}")
    
    print(f"\nAcquire complete. {len(items)} items in {batch_dir}")


def fetch_items_from_source(limit: int | None = None) -> list[Item]:
    """
    CUSTOMIZE: Implement your data fetching logic here.
    
    This example creates dummy data for demonstration.
    Replace with actual API calls, database queries, etc.
    """
    # Example: Generate sample items
    items = []
    for i in range(limit or 10):
        items.append(Item(
            id=f"item-{i:04d}",
            title=f"Sample Item {i}",
            content=f"This is sample content for item {i}. " * 10,
            metadata={"source": "example", "index": i},
        ))
    return items


# -----------------------------------------------------------------------------
# Stage: Prepare
# -----------------------------------------------------------------------------

def stage_prepare(batch_id: str):
    """
    Stage 2: Generate prompts from raw data.
    
    Output: {batch_dir}/{item_id}/prompt.md
    """
    batch_dir = get_batch_dir(batch_id)
    
    for item_dir in sorted(batch_dir.iterdir()):
        if not item_dir.is_dir():
            continue
        
        raw_file = item_dir / "raw.json"
        prompt_file = item_dir / "prompt.md"
        
        if not raw_file.exists():
            continue
        
        if prompt_file.exists():
            continue
        
        with open(raw_file) as f:
            item_data = json.load(f)
        
        prompt = generate_prompt(item_data)
        
        with open(prompt_file, "w") as f:
            f.write(prompt)
        
        print(f"Prepared: {item_dir.name}")
    
    print(f"\nPrepare complete.")


def generate_prompt(item_data: dict) -> str:
    """Generate prompt from item data using template."""
    return PROMPT_TEMPLATE.format(
        title=item_data.get("title", "Untitled"),
        content=item_data.get("content", ""),
    )


# -----------------------------------------------------------------------------
# Stage: Process
# -----------------------------------------------------------------------------

def stage_process(batch_id: str, model: str = "gpt-5.2", max_workers: int = 5):
    """
    Stage 3: Execute LLM calls.
    
    This is the expensive, non-deterministic stage.
    Output: {batch_dir}/{item_id}/response.md
    """
    batch_dir = get_batch_dir(batch_id)
    
    # Collect items needing processing
    to_process = []
    for item_dir in sorted(batch_dir.iterdir()):
        if not item_dir.is_dir():
            continue
        
        prompt_file = item_dir / "prompt.md"
        response_file = item_dir / "response.md"
        
        if prompt_file.exists() and not response_file.exists():
            to_process.append((item_dir, prompt_file.read_text()))
    
    if not to_process:
        print("No items to process.")
        return
    
    print(f"Processing {len(to_process)} items with {max_workers} workers...")
    
    def process_one(args):
        item_dir, prompt = args
        response_file = item_dir / "response.md"
        
        try:
            # CUSTOMIZE: Replace with your LLM API call
            response = call_llm(prompt, model)
            
            with open(response_file, "w") as f:
                f.write(response)
            
            return (item_dir.name, len(response), None)
        except Exception as e:
            return (item_dir.name, 0, str(e))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_one, item): item for item in to_process}
        
        for future in as_completed(futures):
            item_id, chars, error = future.result()
            if error:
                print(f"  {item_id}: Error - {error}")
            else:
                print(f"  {item_id}: Done ({chars} chars)")
    
    print(f"\nProcess complete.")


def call_llm(prompt: str, model: str) -> str:
    """
    CUSTOMIZE: Implement your LLM API call here.
    
    This example returns a mock response for demonstration.
    Replace with actual OpenAI, Anthropic, etc. API calls.
    """
    # Example mock response - replace with actual API call
    # 
    # from openai import OpenAI
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model=model,
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # return response.choices[0].message.content
    
    # Simulate API delay
    time.sleep(0.1)
    
    # Return mock structured response
    return """## Summary
This is a sample summary of the analyzed content.

## Key Points
- First key observation from the content
- Second important finding
- Third notable aspect

## Score
Rating: 7
Confidence: medium

## Reasoning
The content demonstrates several characteristics that merit this rating.
The analysis considered multiple factors including relevance and clarity.
"""


# -----------------------------------------------------------------------------
# Stage: Parse
# -----------------------------------------------------------------------------

def stage_parse(batch_id: str):
    """
    Stage 4: Extract structured data from LLM responses.
    
    Output: {batch_dir}/{item_id}/parsed.json
    """
    batch_dir = get_batch_dir(batch_id)
    all_results = []
    
    for item_dir in sorted(batch_dir.iterdir()):
        if not item_dir.is_dir():
            continue
        
        response_file = item_dir / "response.md"
        parsed_file = item_dir / "parsed.json"
        
        if not response_file.exists():
            continue
        
        response = response_file.read_text()
        result = parse_response(response)
        
        with open(parsed_file, "w") as f:
            json.dump(asdict(result), f, indent=2)
        
        all_results.append({
            "id": item_dir.name,
            **asdict(result),
        })
        
        error_count = len(result.parse_errors)
        print(f"Parsed: {item_dir.name} (score={result.score}, errors={error_count})")
    
    # Save aggregated results
    agg_file = batch_dir / "all_results.json"
    with open(agg_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nParse complete. Results saved to {agg_file}")


def parse_response(text: str) -> ParsedResult:
    """Parse structured LLM response with graceful error handling."""
    result = ParsedResult()
    
    # Extract summary
    try:
        result.summary = extract_section(text, "Summary") or ""
    except Exception as e:
        result.parse_errors.append(f"Summary: {e}")
    
    # Extract key points
    try:
        result.key_points = extract_list_items(text, "Key Points")
    except Exception as e:
        result.parse_errors.append(f"Key Points: {e}")
    
    # Extract score
    try:
        result.score = extract_score(text, "Rating", 1, 10)
    except Exception as e:
        result.parse_errors.append(f"Score: {e}")
    
    # Extract confidence
    try:
        result.confidence = extract_field(text, "Confidence") or ""
    except Exception as e:
        result.parse_errors.append(f"Confidence: {e}")
    
    # Extract reasoning
    try:
        result.reasoning = extract_section(text, "Reasoning") or ""
    except Exception as e:
        result.parse_errors.append(f"Reasoning: {e}")
    
    return result


def extract_section(text: str, section_name: str) -> str | None:
    """Extract content between section headers."""
    pattern = rf'(?:^|\n)(?:#+ *)?{re.escape(section_name)}[:\s]*\n(.*?)(?=\n#|\Z)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def extract_field(text: str, field_name: str) -> str | None:
    """Extract value after field label."""
    pattern = rf'(?:\*\*)?{re.escape(field_name)}(?:\*\*)?[\s:\-]+([^\n]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_list_items(text: str, section_name: str) -> list[str]:
    """Extract bullet points from a section."""
    section = extract_section(text, section_name)
    if not section:
        return []
    
    items = re.findall(r'^[\-\*]\s*(.+)$', section, re.MULTILINE)
    return [item.strip() for item in items]


def extract_score(text: str, field_name: str, min_val: int, max_val: int) -> int | None:
    """Extract and validate numeric score."""
    raw = extract_field(text, field_name)
    if not raw:
        return None
    
    match = re.search(r'\d+', raw)
    if not match:
        return None
    
    score = int(match.group())
    return max(min_val, min(max_val, score))


# -----------------------------------------------------------------------------
# Stage: Render
# -----------------------------------------------------------------------------

def stage_render(batch_id: str):
    """
    Stage 5: Generate final outputs.
    
    Output: {output_dir}/index.html
    """
    batch_dir = get_batch_dir(batch_id)
    output_dir = get_output_dir(batch_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load aggregated results
    results_file = batch_dir / "all_results.json"
    if not results_file.exists():
        print("No results to render. Run parse stage first.")
        return
    
    with open(results_file) as f:
        results = json.load(f)
    
    # CUSTOMIZE: Replace with your rendering logic
    html = render_html(results, batch_id)
    
    output_file = output_dir / "index.html"
    with open(output_file, "w") as f:
        f.write(html)
    
    print(f"Rendered: {output_file}")


def render_html(results: list[dict], batch_id: str) -> str:
    """Generate HTML output from results."""
    import html as html_lib
    
    rows = ""
    for r in results:
        rows += f"""
        <tr>
            <td>{html_lib.escape(r.get('id', ''))}</td>
            <td>{html_lib.escape(r.get('summary', '')[:100])}...</td>
            <td>{r.get('score', 'N/A')}</td>
            <td>{html_lib.escape(r.get('confidence', ''))}</td>
        </tr>"""
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Results - {batch_id}</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Results: {batch_id}</h1>
    <p>{len(results)} items processed</p>
    <table>
        <tr>
            <th>ID</th>
            <th>Summary</th>
            <th>Score</th>
            <th>Confidence</th>
        </tr>
        {rows}
    </table>
</body>
</html>"""


# -----------------------------------------------------------------------------
# Clean Stage
# -----------------------------------------------------------------------------

def stage_clean(batch_id: str, from_stage: str | None = None):
    """Remove outputs to enable re-processing."""
    batch_dir = get_batch_dir(batch_id)
    
    if not batch_dir.exists():
        print(f"No data directory for {batch_id}")
        return
    
    stage_outputs = {
        "acquire": ["raw.json"],
        "prepare": ["prompt.md"],
        "process": ["response.md"],
        "parse": ["parsed.json"],
    }
    
    stage_order = ["acquire", "prepare", "process", "parse", "render"]
    
    if from_stage:
        start_idx = stage_order.index(from_stage)
        stages_to_clean = stage_order[start_idx:]
    else:
        stages_to_clean = stage_order
    
    files_to_delete = set()
    for s in stages_to_clean:
        files_to_delete.update(stage_outputs.get(s, []))
    
    deleted_count = 0
    for item_dir in batch_dir.iterdir():
        if not item_dir.is_dir():
            continue
        
        for filename in files_to_delete:
            filepath = item_dir / filename
            if filepath.exists():
                filepath.unlink()
                deleted_count += 1
    
    # Clean aggregated results
    if "parse" in stages_to_clean:
        agg_file = batch_dir / "all_results.json"
        if agg_file.exists():
            agg_file.unlink()
            deleted_count += 1
    
    print(f"Cleaned {deleted_count} files from stage '{from_stage or 'all'}' onwards")


# -----------------------------------------------------------------------------
# Cost Estimation
# -----------------------------------------------------------------------------

def stage_estimate(batch_id: str):
    """Estimate processing costs before running."""
    batch_dir = get_batch_dir(batch_id)
    
    if not batch_dir.exists():
        print(f"No data directory for {batch_id}. Run acquire first.")
        return
    
    # Count items and estimate tokens
    item_count = 0
    total_prompt_chars = 0
    
    for item_dir in batch_dir.iterdir():
        if not item_dir.is_dir():
            continue
        
        prompt_file = item_dir / "prompt.md"
        if prompt_file.exists():
            total_prompt_chars += len(prompt_file.read_text())
            item_count += 1
    
    if item_count == 0:
        print("No prompts found. Run prepare first.")
        return
    
    # Rough token estimation (1 token ≈ 4 chars)
    est_input_tokens = total_prompt_chars / 4
    est_output_tokens = item_count * 500  # Assume 500 tokens per response
    
    # Example pricing (GPT-5.2)
    input_price = 10.0 / 1_000_000  # $10 per MTok
    output_price = 30.0 / 1_000_000  # $30 per MTok
    
    est_cost = (est_input_tokens * input_price) + (est_output_tokens * output_price)
    
    print(f"Cost Estimate for {batch_id}")
    print(f"  Items: {item_count}")
    print(f"  Estimated input tokens: {int(est_input_tokens):,}")
    print(f"  Estimated output tokens: {int(est_output_tokens):,}")
    print(f"  Estimated cost: ${est_cost:.2f}")
    print(f"\nNote: Actual costs may vary. Add 20-30% buffer for retries.")


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="LLM Batch Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    parser.add_argument(
        "stage",
        choices=["acquire", "prepare", "process", "parse", "render", "all", "clean", "estimate"],
        help="Pipeline stage to run",
    )
    parser.add_argument(
        "--batch-id",
        default=None,
        help="Batch identifier (default: today's date)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of items (for testing)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of parallel workers for processing",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.2",
        help="Model to use for processing",
    )
    parser.add_argument(
        "--clean-stage",
        choices=["acquire", "prepare", "process", "parse"],
        help="For clean: only clean this stage and downstream",
    )
    
    args = parser.parse_args()
    
    batch_id = args.batch_id or date.today().isoformat()
    print(f"Batch ID: {batch_id}\n")
    
    if args.stage == "clean":
        stage_clean(batch_id, args.clean_stage)
    elif args.stage == "estimate":
        stage_estimate(batch_id)
    elif args.stage == "all":
        stage_acquire(batch_id, args.limit)
        stage_prepare(batch_id)
        stage_process(batch_id, args.model, args.workers)
        stage_parse(batch_id)
        stage_render(batch_id)
    else:
        if args.stage == "acquire":
            stage_acquire(batch_id, args.limit)
        elif args.stage == "prepare":
            stage_prepare(batch_id)
        elif args.stage == "process":
            stage_process(batch_id, args.model, args.workers)
        elif args.stage == "parse":
            stage_parse(batch_id)
        elif args.stage == "render":
            stage_render(batch_id)


if __name__ == "__main__":
    main()

