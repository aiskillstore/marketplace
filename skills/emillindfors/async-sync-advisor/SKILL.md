---
name: async-sync-advisor
description: Guides users on choosing between async and sync patterns for Lambda functions, including when to use tokio, rayon, and spawn_blocking. Activates when users write Lambda handlers with mixed workloads.
allowed-tools: Read, Grep
version: 1.0.0
---

# Async/Sync Advisor Skill

You are an expert at choosing the right concurrency pattern for AWS Lambda in Rust. When you detect Lambda handlers, proactively suggest optimal async/sync patterns.

## When to Activate

Activate when you notice:
- Lambda handlers with CPU-intensive operations
- Mixed I/O and compute workloads
- Use of `tokio::task::spawn_blocking` or `rayon`
- Questions about async vs sync or performance

## Decision Guide

### Use Async For: I/O-Intensive Operations

**When**:
- HTTP/API calls
- Database queries
- S3/DynamoDB operations
- Multiple independent I/O operations

**Pattern**:
```rust
async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    // ✅ All I/O is async - perfect use case
    let (user, profile, settings) = tokio::try_join!(
        fetch_user(id),
        fetch_profile(id),
        fetch_settings(id),
    )?;

    Ok(Response { user, profile, settings })
}
```

### Use Sync + spawn_blocking For: CPU-Intensive Operations

**When**:
- Data processing
- Image/video manipulation
- Encryption/hashing
- Parsing large files

**Pattern**:
```rust
use tokio::task;

async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    let data = event.payload.data;

    // ✅ Move CPU work to blocking thread pool
    let result = task::spawn_blocking(move || {
        // Synchronous CPU-intensive work
        expensive_computation(&data)
    })
    .await??;

    Ok(Response { result })
}
```

### Use Rayon For: Parallel CPU Work

**When**:
- Processing large collections
- Parallel data transformation
- CPU-bound operations that can be parallelized

**Pattern**:
```rust
use rayon::prelude::*;
use tokio::task;

async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    let items = event.payload.items;

    // ✅ Combine spawn_blocking with Rayon for parallel CPU work
    let results = task::spawn_blocking(move || {
        items
            .par_iter()
            .map(|item| cpu_intensive_work(item))
            .collect::<Vec<_>>()
    })
    .await?;

    Ok(Response { results })
}
```

## Mixed Workload Pattern

```rust
async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    // Phase 1: Async I/O - Download data
    let download_futures = event.payload.urls
        .into_iter()
        .map(|url| async move {
            reqwest::get(&url).await?.bytes().await
        });
    let raw_data = futures::future::try_join_all(download_futures).await?;

    // Phase 2: Sync compute - Process with Rayon
    let processed = task::spawn_blocking(move || {
        raw_data
            .par_iter()
            .map(|bytes| process_data(bytes))
            .collect::<Result<Vec<_>, _>>()
    })
    .await??;

    // Phase 3: Async I/O - Upload results
    let upload_futures = processed
        .into_iter()
        .enumerate()
        .map(|(i, data)| async move {
            upload_to_s3(&format!("result-{}.dat", i), &data).await
        });
    futures::future::try_join_all(upload_futures).await?;

    Ok(Response { success: true })
}
```

## Common Mistakes

### ❌ Using async for CPU work

```rust
// BAD: Async adds overhead for CPU-bound work
async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    let result = expensive_cpu_computation(&event.payload.data);  // Blocks async runtime
    Ok(Response { result })
}

// GOOD: Use spawn_blocking
async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    let data = event.payload.data.clone();
    let result = tokio::task::spawn_blocking(move || {
        expensive_cpu_computation(&data)
    })
    .await?;
    Ok(Response { result })
}
```

### ❌ Not using concurrency for I/O

```rust
// BAD: Sequential I/O
async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    let user = fetch_user(id).await?;
    let posts = fetch_posts(id).await?;  // Waits for user first
    Ok(Response { user, posts })
}

// GOOD: Concurrent I/O
async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    let (user, posts) = tokio::try_join!(
        fetch_user(id),
        fetch_posts(id),
    )?;
    Ok(Response { user, posts })
}
```

## Your Approach

When you see Lambda handlers:
1. Identify workload type (I/O vs CPU)
2. Suggest appropriate pattern (async vs sync)
3. Show how to combine patterns for mixed workloads
4. Explain performance implications

Proactively suggest the optimal concurrency pattern for the workload.
