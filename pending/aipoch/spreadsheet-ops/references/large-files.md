# Large File Processing Recommendations

## When to Enable

- Single file > 100MB
- Insufficient memory or significant slowdown in reading

## Processing Strategies

- Use chunked reading (chunksize) for CSV, merge in batches, and then perform full deduplication
- Trim unnecessary columns as early as possible to reduce memory usage
- Perform type unification and null value cleaning on primary key columns first
- Output periodic progress logs when necessary

## Precautions

- Chunked deduplication must account for duplicate records across chunks
- Exporting to Parquet can significantly improve subsequent processing performance