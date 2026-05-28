# Forge API Reference Guide

## Overview

Forge is a cloud platform for large-scale protein design and inference launched by EvolutionaryScale. It provides API access to the full range of ESM3 models, including large models that cannot be run locally.

**Core Advantages:**
- Access to all ESM3 models, including the 98B parameter version
- No local GPU hardware required
- Scalable batch processing capabilities
- Automatic updates to the latest models
- Production-grade infrastructure
- Support for asynchronous/concurrent requests

## Quick Start

### 1. Get an API Token

Register and get your API token at the following URL: https://forge.evolutionaryscale.ai

### 2. Install ESM SDK

```bash
pip install esm
```

The Forge client is included in the standard ESM installation package.

### 3. Basic Connection

```python
from esm.sdk.forge import ESM3ForgeInferenceClient
from esm.sdk.api import ESMProtein, GenerationConfig

# Initialize the client
client = ESM3ForgeInferenceClient(
    model="esm3-medium-2024-08",
    url="https://forge.evolutionaryscale.ai",
    token="<your-token-here>"
)

# Test connection
protein = ESMProtein(sequence="MPRT___KEND")
result = client.generate(protein, GenerationConfig(track="sequence", num_steps=8))
print(result.sequence)
```

## Available Models

| Model ID | Parameters | Speed | Quality | Use Case |
|----------|-----------|-------|---------|----------|
| `esm3-small-2024-08` | 1.4B | Fastest | Good | Rapid prototyping, testing |
| `esm3-medium-2024-08` | 7B | Fast | Excellent | Production environments, most applications |
| `esm3-large-2024-03` | 98B | Slower | Best | Scientific research, critical design |
| `esm3-medium-multimer-2024-09` | 7B | Fast | Experimental | Protein complexes |

**Model Selection Guide:**

- **Development/Testing**: Use `esm3-small-2024-08` for rapid iteration
- **Production Environment**: Use `esm3-medium-2024-08` for the best balance
- **Research/Critical Tasks**: Use `esm3-large-2024-03` for the highest quality
- **Complexes**: Use `esm3-medium-multimer-2024-09` (Experimental)

## ESM3ForgeInferenceClient API

### Initialization

```python
from esm.sdk.forge import ESM3ForgeInferenceClient

# Basic initialization
client = ESM3ForgeInferenceClient(
    model="esm3-medium-2024-08",
    token="<your-token>"
)

# Use custom URL (for enterprise deployments)
client = ESM3ForgeInferenceClient(
    model="esm3-medium-2024-08",
    url="https://custom.forge.instance.com",
    token="<your-token>"
)

# Configure timeout
client = ESM3ForgeInferenceClient(
    model="esm3-medium-2024-08",
    token="<your-token>",
    timeout=300  # 5 minutes
)
```

### Synchronous Generation

Standard blocking generation call:

```python
from esm.sdk.api import ESMProtein, GenerationConfig

# Basic generation
protein = ESMProtein(sequence="MPRT___KEND")
config = GenerationConfig(track="sequence", num_steps=8)

result = client.generate(protein, config)
print(f"Generated: {result.sequence}")
```

### Asynchronous Generation

For concurrent processing of multiple proteins:

```python
import asyncio
from esm.sdk.api import ESMProtein, GenerationConfig

async def generate_many(client, proteins):
    """Concurrently generate multiple proteins."""
    tasks = []

    for protein in proteins:
        task = client.async_generate(
            protein,
            GenerationConfig(track="sequence", num_steps=8)
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results

# Usage example
proteins = [
    ESMProtein(sequence=f"MPRT{'_' * 10}KEND"),
    ESMProtein(sequence=f"AGLV{'_' * 10}HSPQ"),
    ESMProtein(sequence=f"KEIT{'_' * 10}NDFL")
]

results = asyncio.run(generate_many(client, proteins))
print(f"Generated {len(results)} proteins")
```

### Batch Processing with BatchExecutor

For large-scale processing with automatic concurrency management:

```python
from esm.sdk.forge import BatchExecutor
from esm.sdk.api import ESMProtein, GenerationConfig

# Create batch executor
executor = BatchExecutor(
    client=client,
    max_concurrent=10  # Process 10 requests simultaneously
)

# Prepare protein batch
proteins = [ESMProtein(sequence=f"MPRT{'_' * 50}KEND") for _ in range(100)]
config = GenerationConfig(track="sequence", num_steps=25)

# Submit batch
batch_results = executor.submit_batch(
    proteins=proteins,
    config=config,
    progress_callback=lambda i, total: print(f"Processed {i}/{total}")
)

print(f"Completed {len(batch_results)} generations")
```

## Rate Limits and Quotas

### Understanding Limits

Forge implements rate limits based on the following dimensions:
- Requests Per Minute (RPM)
- Tokens Per Minute (TPM)
- Concurrent Requests

**Typical Limits (Subject to change):**
- Free Tier: 60 RPM, 5 concurrent
- Pro Tier: 300 RPM, 20 concurrent
- Enterprise Tier: Custom limits

### Handling Rate Limits

```python
import time
from requests.exceptions import HTTPError

def generate_with_retry(client, protein, config, max_retries=3):
    """Generation function that automatically retries when encountering rate limits."""
    for attempt in range(max_retries):
        try:
            return client.generate(protein, config)
        except HTTPError as e:
            if e.response.status_code == 429:  # Rate limit error code
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")

# Usage example
result = generate_with_retry(client, protein, config)
```

### Implementing a Custom Rate Limiter

```python
import time
from collections import deque

class RateLimiter:
    """A simple API call rate limiter."""

    def __init__(self, max_per_minute=60):
        self.max_per_minute = max_per_minute
        self.calls = deque()

    def wait_if_needed(self):
        """Wait if the rate limit is about to be exceeded."""
        now = time.time()

        # Remove old call records from more than a minute ago
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()

        # If limit reached, calculate wait time
        if len(self.calls) >= self.max_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.calls.popleft()

        self.calls.append(now)

# Usage example
limiter = RateLimiter(max_per_minute=60)

for protein in proteins:
    limiter.wait_if_needed()
    result = client.generate(protein, config)
```

## Advanced Patterns

### Streaming Result Processing

Process results immediately as they are completed:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def stream_generate(client, proteins, config):
    """Yield results in a streaming fashion as they complete."""
    pending = {
        asyncio.create_task(client.async_generate(p, config)): i
        for i, p in enumerate(proteins)
    }

    results = [None] * len(proteins)

    while pending:
        done, pending = await asyncio.wait(
            pending.keys(),
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in done:
            idx = pending.pop(task)
            result = await task
            results[idx] = result
            yield idx, result

# Usage example
async def process_stream():
    async for idx, result in stream_generate(client, proteins, config):
        print(f"Completed protein {idx}: {result.sequence[:20]}...")

asyncio.run(process_stream())
```

### Batch Processing with Progress Tracking

```python
from tqdm import tqdm
import asyncio

async def batch_with_progress(client, proteins, config):
    """Process batch with a progress bar."""
    results = []

    with tqdm(total=len(proteins)) as pbar:
        for protein in proteins:
            result = await client.async_generate(protein, config)
            results.append(result)
            pbar.update(1)

    return results

# Usage example
results = asyncio.run(batch_with_progress(client, proteins, config))
```

### Checkpointing (Resume from Breakpoint)

Suitable for long-running batch jobs:

```python
import pickle
import os

class CheckpointedBatchProcessor:
    """Batch processor with checkpoint/resume capabilities."""

    def __init__(self, client, checkpoint_file="checkpoint.pkl"):
        self.client = client
        self.checkpoint_file = checkpoint_file
        self.completed = self.load_checkpoint()

    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'rb') as f:
                return pickle.load(f)
        return {}

    def save_checkpoint(self):
        with open(self.checkpoint_file, 'wb') as f:
            pickle.dump(self.completed, f)

    def process_batch(self, proteins, config):
        """Batch processing with checkpointing."""
        results = {}

        for i, protein in enumerate(proteins):
            # Skip if already completed
            if i in self.completed:
                results[i] = self.completed[i]
                continue

            try:
                result = self.client.generate(protein, config)
                results[i] = result
                self.completed[i] = result

                # Save checkpoint every 10 items
                if i % 10 == 0:
                    self.save_checkpoint()

            except Exception as e:
                print(f"Error processing {i}: {e}")
                self.save_checkpoint()
                raise

        self.save_checkpoint()
        return results

# Usage example
processor = CheckpointedBatchProcessor(client)
results = processor.process_batch(proteins, config)
```

## Error Handling

### Common Errors and Solutions

```python
from requests.exceptions import HTTPError, ConnectionError, Timeout

def robust_generate(client, protein, config):
    """Generation function with comprehensive error handling."""
    try:
        return client.generate(protein, config)

    except HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API token")
        elif e.response.status_code == 429:
            raise ValueError("Rate limit exceeded - slow down requests")
        elif e.response.status_code == 500:
            raise ValueError("Server error - try again later")
        else:
            raise

    except ConnectionError:
        raise ValueError("Network error - check internet connection")

    except Timeout:
        raise ValueError("Request timeout - try smaller protein or increase timeout")

    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")

# Usage example combining retry logic
def generate_with_full_retry(client, protein, config, max_retries=3):
    """Combines error handling with retry logic."""
    for attempt in range(max_retries):
        try:
            return robust_generate(client, protein, config)
        except ValueError as e:
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
```

## Cost Optimization

### Strategies to Reduce Costs

**1. Use appropriate model sizes:**

```python
# Use smaller models during testing
dev_client = ESM3ForgeInferenceClient(
    model="esm3-small-2024-08",
    token=token
)

# Use larger models only for final generation
prod_client = ESM3ForgeInferenceClient(
    model="esm3-large-2024-03",
    token=token
)
```

**2. Cache results:**

```python
import hashlib
import json

class ForgeCache:
    """Cache Forge API results locally."""

    def __init__(self, cache_dir="forge_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache_key(self, protein, config):
        """Generate a cache key based on input."""
        data = {
            'sequence': protein.sequence,
            'config': str(config)
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def get(self, protein, config):
        """Retrieve cached result."""
        key = self.get_cache_key(protein, config)
        path = os.path.join(self.cache_dir, f"{key}.pkl")

        if os.path.exists(path):
            with open(path, 'rb') as f:
                return pickle.load(f)
        return None

    def set(self, protein, config, result):
        """Save result to cache."""
        key = self.get_cache_key(protein, config)
        path = os.path.join(self.cache_dir, f"{key}.pkl")

        with open(path, 'wb') as f:
            pickle.dump(result, f)

# Usage example
cache = ForgeCache()

def cached_generate(client, protein, config):
    """Generation function with caching."""
    cached = cache.get(protein, config)
    if cached:
        return cached

    result = client.generate(protein, config)
    cache.set(protein, config, result)
    return result
```

**3. Batch similar requests:**

Group similar generation tasks to reduce overhead:

```python
def batch_similar_tasks(proteins, max_batch_size=50):
    """Group proteins based on similar attributes."""
    # Sort by length to improve processing efficiency
    sorted_proteins = sorted(proteins, key=lambda p: len(p.sequence))

    batches = []
    current_batch = []

    for protein in sorted_proteins:
        current_batch.append(protein)

        if len(current_batch) >= max_batch_size:
            batches.append(current_batch)
            current_batch = []

    if current_batch:
        batches.append(current_batch)

    return batches
```

## Monitoring and Logging

### Tracking API Usage

```python
import logging
from datetime import datetime

class ForgeMonitor:
    """Monitor Forge API usage."""

    def __init__(self):
        self.calls = []
        self.errors = []

    def log_call(self, model, protein_length, duration, success=True, error=None):
        """Log API call."""
        entry = {
            'timestamp': datetime.now(),
            'model': model,
            'protein_length': protein_length,
            'duration': duration,
            'success': success,
            'error': str(error) if error else None
        }

        if success:
            self.calls.append(entry)
        else:
            self.errors.append(entry)

    def get_stats(self):
        """Get usage statistics."""
        total_calls = len(self.calls) + len(self.errors)
        success_rate = len(self.calls) / total_calls if total_calls > 0 else 0
        avg_duration = sum(c['duration'] for c in self.calls) / len(self.calls) if self.calls else 0

        return {
            'total_calls': total_calls,
            'successful': len(self.calls),
            'failed': len(self.errors),
            'success_rate': success_rate,
            'avg_duration': avg_duration
        }

# Usage example
monitor = ForgeMonitor()

def monitored_generate(client, protein, config):
    """Generation function with monitoring."""
    start = time.time()

    try:
        result = client.generate(protein, config)
        duration = time.time() - start
        monitor.log_call(
            model=client.model,
            protein_length=len(protein.sequence),
            duration=duration,
            success=True
        )
        return result

    except Exception as e:
        duration = time.time() - start
        monitor.log_call(
            model=client.model,
            protein_length=len(protein.sequence),
            duration=duration,
            success=False,
            error=e
        )
        raise

# View statistics
print(monitor.get_stats())
```

## AWS SageMaker Deployment

Suitable for dedicated infrastructure and enterprise use:

### Deployment Options

1. **AWS Marketplace Listing**: Deploy ESM3 via AWS SageMaker Marketplace
2. **Custom Endpoints**: Configure dedicated inference endpoints
3. **Batch Transform**: Use SageMaker Batch Transform for large-scale processing

### Core Advantages

- Dedicated computing resources
- No additional rate limits beyond your own infrastructure constraints
- Data remains in your AWS environment
- Integration with AWS services
- Custom instance types and scaling

**More Information:**
- AWS Marketplace: https://aws.amazon.com/marketplace/seller-profile?id=seller-iw2nbscescndm
- Contact EvolutionaryScale for enterprise licensing

## Best Practices Summary

1. **Authentication**: Securely store tokens (environment variables, secret managers)
2. **Rate Limiting**: Implement exponential backoff and respect limits
3. **Error Handling**: Always handle network errors and perform retries
4. **Caching**: Cache results for repeated queries
5. **Model Selection**: Choose the appropriate model size based on the task
6. **Batching**: Use async/batching for multiple proteins
7. **Monitoring**: Track usage and costs
8. **Checkpointing**: Save progress for long tasks

## Troubleshooting

### Connection Issues

```python
# Test connection
try:
    client = ESM3ForgeInferenceClient(model="esm3-medium-2024-08", token=token)
    test_protein = ESMProtein(sequence="MPRTK")
    result = client.generate(test_protein, GenerationConfig(track="sequence", num_steps=1))
    print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Token Validation

```python
def validate_token(token):
    """Validate API token."""
    try:
        client = ESM3ForgeInferenceClient(
            model="esm3-small-2024-08",
            token=token
        )
        # Initiate a minimal test call
        test = ESMProtein(sequence="MPR")
        client.generate(test, GenerationConfig(track="sequence", num_steps=1))
        return True
    except HTTPError as e:
        if e.response.status_code == 401:
            return False
        raise
```

## Additional Resources

- **Forge Platform**: https://forge.evolutionaryscale.ai
- **API Documentation**: Check the Forge dashboard for the latest API specifications
- **Community Support**: Slack Community https://bit.ly/3FKwcWd
- **Enterprise Contact**: Contact EvolutionaryScale for custom deployment inquiries