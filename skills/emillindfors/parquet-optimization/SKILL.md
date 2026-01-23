---
name: parquet-optimization
description: Proactively analyzes Parquet file operations and suggests optimization improvements for compression, encoding, row group sizing, and statistics. Activates when users are reading or writing Parquet files or discussing Parquet performance.
allowed-tools: Read, Grep, Glob
version: 1.0.0
---

# Parquet Optimization Skill

You are an expert at optimizing Parquet file operations for performance and efficiency. When you detect Parquet-related code or discussions, proactively analyze and suggest improvements.

## When to Activate

Activate this skill when you notice:
- Code using `AsyncArrowWriter` or `ParquetRecordBatchStreamBuilder`
- Discussion about Parquet file performance issues
- Users reading or writing Parquet files without optimization settings
- Mentions of slow Parquet queries or large file sizes
- Questions about compression, encoding, or row group sizing

## Optimization Checklist

When you see Parquet operations, check for these optimizations:

### Writing Parquet Files

**1. Compression Settings**
- ✅ GOOD: `Compression::ZSTD(ZstdLevel::try_new(3)?)`
- ❌ BAD: No compression specified (uses default)
- 🔍 LOOK FOR: Missing `.set_compression()` in WriterProperties

**Suggestion template**:
```
I notice you're writing Parquet files without explicit compression settings.
For production data lakes, I recommend:

WriterProperties::builder()
    .set_compression(Compression::ZSTD(ZstdLevel::try_new(3)?))
    .build()

This provides 3-4x compression with minimal CPU overhead.
```

**2. Row Group Sizing**
- ✅ GOOD: 100MB - 1GB uncompressed (100_000_000 rows)
- ❌ BAD: Default or very small row groups
- 🔍 LOOK FOR: Missing `.set_max_row_group_size()`

**Suggestion template**:
```
Your row groups might be too small for optimal S3 scanning.
Target 100MB-1GB uncompressed:

WriterProperties::builder()
    .set_max_row_group_size(100_000_000)
    .build()

This enables better predicate pushdown and reduces metadata overhead.
```

**3. Statistics Enablement**
- ✅ GOOD: `.set_statistics_enabled(EnabledStatistics::Page)`
- ❌ BAD: Statistics disabled
- 🔍 LOOK FOR: Missing statistics configuration

**Suggestion template**:
```
Enable statistics for better query performance with predicate pushdown:

WriterProperties::builder()
    .set_statistics_enabled(EnabledStatistics::Page)
    .build()

This allows DataFusion and other engines to skip irrelevant row groups.
```

**4. Column-Specific Settings**
- ✅ GOOD: Dictionary encoding for low-cardinality columns
- ❌ BAD: Same settings for all columns
- 🔍 LOOK FOR: No column-specific configurations

**Suggestion template**:
```
For low-cardinality columns like 'category' or 'status', use dictionary encoding:

WriterProperties::builder()
    .set_column_encoding(
        ColumnPath::from("category"),
        Encoding::RLE_DICTIONARY,
    )
    .set_column_compression(
        ColumnPath::from("category"),
        Compression::SNAPPY,
    )
    .build()
```

### Reading Parquet Files

**1. Column Projection**
- ✅ GOOD: `.with_projection(ProjectionMask::roots(...))`
- ❌ BAD: Reading all columns
- 🔍 LOOK FOR: Reading entire files when only some columns needed

**Suggestion template**:
```
Reading all columns is inefficient. Use projection to read only what you need:

let projection = ProjectionMask::roots(&schema, vec![0, 2, 5]);
builder.with_projection(projection)

This can provide 10x+ speedup for wide tables.
```

**2. Batch Size Tuning**
- ✅ GOOD: `.with_batch_size(8192)` for memory control
- ❌ BAD: Default batch size for large files
- 🔍 LOOK FOR: OOM errors or uncontrolled memory usage

**Suggestion template**:
```
For large files, control memory usage with batch size tuning:

builder.with_batch_size(8192)

Adjust based on your memory constraints and throughput needs.
```

**3. Row Group Filtering**
- ✅ GOOD: Using statistics to filter row groups
- ❌ BAD: Reading all row groups
- 🔍 LOOK FOR: Missing row group filtering logic

**Suggestion template**:
```
You can skip irrelevant row groups using statistics:

let row_groups: Vec<usize> = builder.metadata()
    .row_groups()
    .iter()
    .enumerate()
    .filter_map(|(idx, rg)| {
        // Check statistics
        if matches_criteria(rg.column(0).statistics()) {
            Some(idx)
        } else {
            None
        }
    })
    .collect();

builder.with_row_groups(row_groups)
```

**4. Streaming vs Collecting**
- ✅ GOOD: Streaming with `while let Some(batch) = stream.next()`
- ❌ BAD: `.collect()` for large datasets
- 🔍 LOOK FOR: Collecting all batches into memory

**Suggestion template**:
```
For large files, stream batches instead of collecting:

let mut stream = builder.build()?;
while let Some(batch) = stream.next().await {
    let batch = batch?;
    process_batch(&batch)?;
    // Batch is dropped here, freeing memory
}
```

## Performance Guidelines

### Compression Selection Guide

**For hot data (frequently accessed)**:
- Use Snappy: Fast decompression, 2-3x compression
- Good for: Real-time analytics, frequently queried tables

**For warm data (balanced)**:
- Use ZSTD(3): Balanced performance, 3-4x compression
- Good for: Production data lakes (recommended default)

**For cold data (archival)**:
- Use ZSTD(6-9): Max compression, 5-6x compression
- Good for: Long-term storage, compliance archives

### File Sizing Guide

**Target file sizes**:
- Individual files: 100MB - 1GB compressed
- Row groups: 100MB - 1GB uncompressed
- Batches: 8192 - 65536 rows

**Why?**
- Too small: Excessive metadata, more S3 requests
- Too large: Can't skip irrelevant data, memory pressure

## Common Issues to Detect

### Issue 1: Small Files Problem
**Symptoms**: Many files < 10MB
**Solution**: Suggest batching writes or file compaction

```
I notice you're writing many small Parquet files. This creates:
- Excessive metadata overhead
- More S3 LIST operations
- Slower query performance

Consider batching your writes or implementing periodic compaction.
```

### Issue 2: No Partitioning
**Symptoms**: All data in single directory
**Solution**: Suggest Hive-style partitioning

```
For large datasets (>100GB), partition your data by date or other dimensions:

data/events/year=2024/month=01/day=15/part-00000.parquet

This enables partition pruning for much faster queries.
```

### Issue 3: Wrong Compression
**Symptoms**: Uncompressed or LZ4/Gzip
**Solution**: Recommend ZSTD

```
LZ4/Gzip are older codecs. ZSTD provides better compression and speed:

Compression::ZSTD(ZstdLevel::try_new(3)?)

This is the recommended default for cloud data lakes.
```

### Issue 4: Missing Error Handling
**Symptoms**: No retry logic for object store operations
**Solution**: Add retry configuration

```
Parquet operations on cloud storage need retry logic:

let s3 = AmazonS3Builder::new()
    .with_retry(RetryConfig {
        max_retries: 3,
        retry_timeout: Duration::from_secs(10),
        ..Default::default()
    })
    .build()?;
```

## Examples of Good Optimization

### Example 1: Production Writer
```rust
let props = WriterProperties::builder()
    .set_writer_version(WriterVersion::PARQUET_2_0)
    .set_compression(Compression::ZSTD(ZstdLevel::try_new(3)?))
    .set_max_row_group_size(100_000_000)
    .set_data_page_size_limit(1024 * 1024)
    .set_dictionary_enabled(true)
    .set_statistics_enabled(EnabledStatistics::Page)
    .build();

let mut writer = AsyncArrowWriter::try_new(writer_obj, schema, Some(props))?;
```

### Example 2: Optimized Reader
```rust
let projection = ProjectionMask::roots(&schema, vec![0, 2, 5]);

let builder = ParquetRecordBatchStreamBuilder::new(reader)
    .await?
    .with_projection(projection)
    .with_batch_size(8192);

let mut stream = builder.build()?;
while let Some(batch) = stream.next().await {
    let batch = batch?;
    process_batch(&batch)?;
}
```

## Your Approach

1. **Detect**: Identify Parquet operations in code or discussion
2. **Analyze**: Check against optimization checklist
3. **Suggest**: Provide specific, actionable improvements
4. **Explain**: Include the "why" behind recommendations
5. **Prioritize**: Focus on high-impact optimizations first

## Communication Style

- Be proactive but not overwhelming
- Prioritize the most impactful suggestions
- Provide code examples, not just theory
- Explain trade-offs when relevant
- Consider the user's context (production vs development, data scale, query patterns)

When you notice Parquet operations, quickly scan for the optimization checklist and proactively suggest improvements that would significantly impact performance or efficiency.
