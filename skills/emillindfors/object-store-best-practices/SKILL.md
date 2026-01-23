---
name: object-store-best-practices
description: Ensures proper cloud storage operations with retry logic, error handling, streaming, and efficient I/O patterns. Activates when users work with object_store for S3, Azure, or GCS operations.
allowed-tools: Read, Grep
version: 1.0.0
---

# Object Store Best Practices Skill

You are an expert at implementing robust cloud storage operations using the object_store crate. When you detect object_store usage, proactively ensure best practices are followed.

## When to Activate

Activate this skill when you notice:
- Code using `ObjectStore` trait, `AmazonS3Builder`, `MicrosoftAzureBuilder`, or `GoogleCloudStorageBuilder`
- Discussion about S3, Azure Blob, or GCS operations
- Issues with cloud storage reliability, performance, or errors
- File uploads, downloads, or listing operations
- Questions about retry logic, error handling, or streaming

## Best Practices Checklist

### 1. Retry Configuration

**What to Look For**:
- Missing retry logic for production code
- Default settings without explicit retry configuration

**Good Pattern**:
```rust
use object_store::aws::AmazonS3Builder;
use object_store::RetryConfig;

let s3 = AmazonS3Builder::new()
    .with_region("us-east-1")
    .with_bucket_name("my-bucket")
    .with_retry(RetryConfig {
        max_retries: 3,
        retry_timeout: Duration::from_secs(10),
        ..Default::default()
    })
    .build()?;
```

**Bad Pattern**:
```rust
// No retry configuration - fails on transient errors
let s3 = AmazonS3Builder::new()
    .with_region("us-east-1")
    .with_bucket_name("my-bucket")
    .build()?;
```

**Suggestion**:
```
Cloud storage operations need retry logic for production resilience.
Add retry configuration to handle transient failures:

.with_retry(RetryConfig {
    max_retries: 3,
    retry_timeout: Duration::from_secs(10),
    ..Default::default()
})

This handles 503 SlowDown, network timeouts, and temporary outages.
```

### 2. Error Handling

**What to Look For**:
- Using `unwrap()` or `expect()` on storage operations
- Not handling specific error types
- Missing context in error propagation

**Good Pattern**:
```rust
use object_store::Error as ObjectStoreError;
use thiserror::Error;

#[derive(Error, Debug)]
enum StorageError {
    #[error("Object store error: {0}")]
    ObjectStore(#[from] ObjectStoreError),

    #[error("File not found: {path}")]
    NotFound { path: String },

    #[error("Access denied: {path}")]
    PermissionDenied { path: String },
}

async fn read_file(store: &dyn ObjectStore, path: &Path) -> Result<Bytes, StorageError> {
    match store.get(path).await {
        Ok(result) => Ok(result.bytes().await?),
        Err(ObjectStoreError::NotFound { path, .. }) => {
            Err(StorageError::NotFound { path: path.to_string() })
        }
        Err(e) => Err(e.into()),
    }
}
```

**Bad Pattern**:
```rust
let data = store.get(&path).await.unwrap();  // Crashes on errors!
```

**Suggestion**:
```
Avoid unwrap() on storage operations. Use proper error handling:

match store.get(&path).await {
    Ok(result) => { /* handle success */ }
    Err(ObjectStoreError::NotFound { .. }) => { /* handle missing file */ }
    Err(e) => { /* handle other errors */ }
}

Or use thiserror for better error types.
```

### 3. Streaming Large Objects

**What to Look For**:
- Loading entire files into memory with `.bytes().await`
- Not using streaming for large files (>100MB)

**Good Pattern (Streaming)**:
```rust
use futures::stream::StreamExt;

let result = store.get(&path).await?;
let mut stream = result.into_stream();

while let Some(chunk) = stream.next().await {
    let chunk = chunk?;
    // Process chunk incrementally
    process_chunk(chunk)?;
}
```

**Bad Pattern (Loading to Memory)**:
```rust
let result = store.get(&path).await?;
let bytes = result.bytes().await?;  // Loads entire file!
```

**Suggestion**:
```
For files >100MB, use streaming to avoid memory issues:

let mut stream = store.get(&path).await?.into_stream();
while let Some(chunk) = stream.next().await {
    let chunk = chunk?;
    process_chunk(chunk)?;
}

This processes data incrementally without loading everything into memory.
```

### 4. Multipart Upload for Large Files

**What to Look For**:
- Using `put()` for large files (>100MB)
- Missing multipart upload for big data

**Good Pattern**:
```rust
async fn upload_large_file(
    store: &dyn ObjectStore,
    path: &Path,
    data: impl Stream<Item = Bytes>,
) -> Result<()> {
    let multipart = store.put_multipart(path).await?;

    let mut stream = data;
    while let Some(chunk) = stream.next().await {
        multipart.put_part(chunk).await?;
    }

    multipart.complete().await?;
    Ok(())
}
```

**Bad Pattern**:
```rust
// Inefficient for large files
let large_data = vec![0u8; 1_000_000_000];  // 1GB
store.put(path, large_data.into()).await?;
```

**Suggestion**:
```
For files >100MB, use multipart upload for better reliability:

let multipart = store.put_multipart(&path).await?;
for chunk in chunks {
    multipart.put_part(chunk).await?;
}
multipart.complete().await?;

Benefits:
- Resume failed uploads
- Better memory efficiency
- Improved reliability
```

### 5. Efficient Listing

**What to Look For**:
- Not using prefixes for listing
- Loading all results without pagination
- Not filtering on client side

**Good Pattern**:
```rust
use futures::stream::StreamExt;

// List with prefix
let prefix = Some(&Path::from("data/2024/"));
let mut list = store.list(prefix);

while let Some(meta) = list.next().await {
    let meta = meta?;
    if should_process(&meta) {
        process_object(&meta).await?;
    }
}
```

**Better Pattern with Filtering**:
```rust
let prefix = Some(&Path::from("data/2024/01/"));
let list = store.list(prefix);

let filtered = list.filter(|result| {
    future::ready(match result {
        Ok(meta) => meta.location.as_ref().ends_with(".parquet"),
        Err(_) => true,
    })
});

futures::pin_mut!(filtered);
while let Some(meta) = filtered.next().await {
    let meta = meta?;
    process_object(&meta).await?;
}
```

**Bad Pattern**:
```rust
// Lists entire bucket!
let all_objects: Vec<_> = store.list(None).collect().await;
```

**Suggestion**:
```
Use prefixes to limit LIST operations and reduce cost:

let prefix = Some(&Path::from("data/2024/01/"));
let mut list = store.list(prefix);

This is especially important for buckets with millions of objects.
```

### 6. Atomic Writes with Rename

**What to Look For**:
- Writing directly to final location
- Risk of partial writes visible to readers

**Good Pattern**:
```rust
async fn atomic_write(
    store: &dyn ObjectStore,
    final_path: &Path,
    data: Bytes,
) -> Result<()> {
    // Write to temp location
    let temp_path = Path::from(format!("{}.tmp", final_path));
    store.put(&temp_path, data).await?;

    // Atomic rename
    store.rename(&temp_path, final_path).await?;

    Ok(())
}
```

**Bad Pattern**:
```rust
// Readers might see partial data during write
store.put(&path, data).await?;
```

**Suggestion**:
```
Use temp + rename for atomic writes:

let temp_path = Path::from(format!("{}.tmp", path));
store.put(&temp_path, data).await?;
store.rename(&temp_path, path).await?;

This prevents readers from seeing partial/corrupted data.
```

### 7. Connection Pooling

**What to Look For**:
- Creating new client for each operation
- Not configuring connection limits

**Good Pattern**:
```rust
use object_store::ClientOptions;

let s3 = AmazonS3Builder::new()
    .with_client_options(ClientOptions::new()
        .with_timeout(Duration::from_secs(30))
        .with_connect_timeout(Duration::from_secs(5))
        .with_pool_max_idle_per_host(10)
    )
    .build()?;

// Reuse this store across operations
let store: Arc<dyn ObjectStore> = Arc::new(s3);
```

**Bad Pattern**:
```rust
// Creating new store for each operation
for file in files {
    let s3 = AmazonS3Builder::new().build()?;
    upload(s3, file).await?;
}
```

**Suggestion**:
```
Configure connection pooling and reuse the ObjectStore:

let store: Arc<dyn ObjectStore> = Arc::new(s3);

// Clone Arc to share across threads
let store_clone = store.clone();
tokio::spawn(async move {
    upload(store_clone, file).await
});
```

### 8. Environment-Based Configuration

**What to Look For**:
- Hardcoded credentials or regions
- Missing environment variable support

**Good Pattern**:
```rust
use std::env;

async fn create_s3_store() -> Result<Arc<dyn ObjectStore>> {
    let region = env::var("AWS_REGION")
        .unwrap_or_else(|_| "us-east-1".to_string());
    let bucket = env::var("S3_BUCKET")?;

    let s3 = AmazonS3Builder::from_env()  // Reads AWS_* env vars
        .with_region(&region)
        .with_bucket_name(&bucket)
        .with_retry(RetryConfig::default())
        .build()?;

    Ok(Arc::new(s3))
}
```

**Bad Pattern**:
```rust
// Hardcoded credentials
let s3 = AmazonS3Builder::new()
    .with_access_key_id("AKIAIOSFODNN7EXAMPLE")  // Never do this!
    .with_secret_access_key("wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
    .build()?;
```

**Suggestion**:
```
Use environment-based configuration for security:

let s3 = AmazonS3Builder::from_env()  // Reads AWS credentials
    .with_bucket_name(&bucket)
    .build()?;

Or use IAM roles, instance profiles, or credential chains.
Never hardcode credentials!
```

## Common Issues to Detect

### Issue 1: 503 SlowDown Errors

**Symptoms**: Intermittent 503 errors from S3

**Solution**:
```
S3 rate limiting causing 503 SlowDown. Add retry config:

.with_retry(RetryConfig {
    max_retries: 5,
    retry_timeout: Duration::from_secs(30),
    ..Default::default()
})

Also consider:
- Using S3 prefixes to distribute load
- Implementing client-side backoff
- Requesting higher limits from AWS
```

### Issue 2: Connection Timeout

**Symptoms**: Timeout errors on large operations

**Solution**:
```
Increase timeouts for large file operations:

.with_client_options(ClientOptions::new()
    .with_timeout(Duration::from_secs(300))  // 5 minutes
    .with_connect_timeout(Duration::from_secs(10))
)
```

### Issue 3: Memory Leaks on Streaming

**Symptoms**: Memory grows when processing many files

**Solution**:
```
Ensure streams are properly consumed and dropped:

let mut stream = store.get(&path).await?.into_stream();
while let Some(chunk) = stream.next().await {
    let chunk = chunk?;
    process_chunk(chunk)?;
    // Chunk is dropped here
}
// Stream is dropped here
```

### Issue 4: Missing Error Context

**Symptoms**: Hard to debug which operation failed

**Solution**:
```
Add context to errors:

store.get(&path).await
    .with_context(|| format!("Failed to read {}", path))?;

Or use custom error types with thiserror.
```

## Performance Optimization

### Parallel Operations

```rust
use futures::stream::{self, StreamExt};

// Upload multiple files in parallel
let uploads = files.iter().map(|file| {
    let store = store.clone();
    async move {
        store.put(&file.path, file.data.clone()).await
    }
});

// Process 10 at a time
let results = stream::iter(uploads)
    .buffer_unordered(10)
    .collect::<Vec<_>>()
    .await;
```

### Caching HEAD Requests

```rust
use std::collections::HashMap;

// Cache metadata to avoid repeated HEAD requests
let mut metadata_cache: HashMap<Path, ObjectMeta> = HashMap::new();

if let Some(meta) = metadata_cache.get(&path) {
    // Use cached metadata
} else {
    let meta = store.head(&path).await?;
    metadata_cache.insert(path.clone(), meta);
}
```

### Prefetching

```rust
// Prefetch next file while processing current
let mut next_file = Some(store.get(&paths[0]));

for (i, path) in paths.iter().enumerate() {
    let current = next_file.take().unwrap().await?;

    // Start next fetch
    if i + 1 < paths.len() {
        next_file = Some(store.get(&paths[i + 1]));
    }

    // Process current
    process(current).await?;
}
```

## Testing Best Practices

### Use LocalFileSystem for Tests

```rust
#[cfg(test)]
mod tests {
    use object_store::local::LocalFileSystem;

    #[tokio::test]
    async fn test_pipeline() {
        let store = LocalFileSystem::new_with_prefix(
            tempfile::tempdir()?.path()
        )?;

        // Test with local storage, no cloud costs
        run_pipeline(Arc::new(store)).await?;
    }
}
```

### Mock for Unit Tests

```rust
use mockall::mock;

mock! {
    Store {}

    #[async_trait]
    impl ObjectStore for Store {
        async fn get(&self, location: &Path) -> Result<GetResult>;
        async fn put(&self, location: &Path, bytes: Bytes) -> Result<PutResult>;
        // ... other methods
    }
}
```

## Your Approach

1. **Detect**: Identify object_store operations
2. **Check**: Review against best practices checklist
3. **Suggest**: Provide specific improvements for reliability
4. **Prioritize**: Focus on retry logic, error handling, streaming
5. **Context**: Consider production vs development environment

## Communication Style

- Emphasize reliability and production-readiness
- Explain the "why" behind best practices
- Provide code examples for fixes
- Consider cost implications (S3 requests, data transfer)
- Prioritize critical issues (no retry, hardcoded creds, memory leaks)

When you see object_store usage, quickly check for common reliability issues and proactively suggest improvements that prevent production failures.
