# T-SQL Performance Tuning Reference

Execution plan analysis, indexing strategies, and performance optimization techniques.

## Reading Execution Plans

### Key Operators to Watch

| Operator | Concern Level | What It Means |
|----------|---------------|---------------|
| Table Scan | High (large tables) | No useful index, reads entire table |
| Clustered Index Scan | Medium | Reading most/all rows via clustered index |
| Index Scan | Medium | Reading most/all index rows |
| Key Lookup | High (many rows) | Index doesn't cover all columns, extra I/O |
| RID Lookup | High | Heap lookup, consider adding clustered index |
| Hash Match | Context-dependent | Large joins/aggregations, memory-intensive |
| Sort | Medium | Ordering data, may spill to tempdb |
| Spool (Eager/Lazy) | Medium-High | Caching intermediate results, often indicates suboptimal plan |

### Warning Signs in Plans

```
⚠️ Yellow triangle warnings:
- Missing statistics
- Implicit conversions
- No join predicate (Cartesian product)
- Memory grant warnings

⚠️ Thick arrows:
- Large row estimates flowing between operators
- Check if estimates match actual rows (parameter sniffing?)

⚠️ Operator costs:
- High percentage operators are optimization targets
- But cost is estimated - verify with actual execution stats
```

## Identifying Performance Issues

### Capture Actual Statistics

```sql
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

-- Your query here

SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
```

Key metrics:
- **Logical reads**: Pages read from buffer cache (lower is better)
- **Physical reads**: Pages read from disk (should be 0 on repeated runs)
- **CPU time**: Processing time
- **Elapsed time**: Total wall clock time

### Find Missing Indexes

```sql
-- Missing index suggestions from DMVs
SELECT
    CONVERT(DECIMAL(18,2), migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans)) AS improvement_measure,
    'CREATE INDEX [IX_' + OBJECT_NAME(mid.object_id) + '_'
        + REPLACE(REPLACE(REPLACE(ISNULL(mid.equality_columns,''), ', ', '_'), '[', ''), ']', '') + ']'
        + ' ON ' + mid.statement
        + ' (' + ISNULL(mid.equality_columns, '')
        + CASE WHEN mid.equality_columns IS NOT NULL AND mid.inequality_columns IS NOT NULL THEN ', ' ELSE '' END
        + ISNULL(mid.inequality_columns, '') + ')'
        + ISNULL(' INCLUDE (' + mid.included_columns + ')', '') AS create_index_statement
FROM sys.dm_db_missing_index_groups mig
JOIN sys.dm_db_missing_index_group_stats migs ON migs.group_handle = mig.index_group_handle
JOIN sys.dm_db_missing_index_details mid ON mig.index_handle = mid.index_handle
WHERE mid.database_id = DB_ID()
ORDER BY improvement_measure DESC;
```

### Find Unused Indexes

```sql
SELECT
    OBJECT_NAME(i.object_id) AS table_name,
    i.name AS index_name,
    i.type_desc,
    ius.user_seeks,
    ius.user_scans,
    ius.user_lookups,
    ius.user_updates
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats ius
    ON i.object_id = ius.object_id AND i.index_id = ius.index_id
WHERE OBJECTPROPERTY(i.object_id, 'IsUserTable') = 1
    AND i.type_desc = 'NONCLUSTERED'
    AND (ius.user_seeks + ius.user_scans + ius.user_lookups) < ius.user_updates
ORDER BY ius.user_updates DESC;
```

## Parameter Sniffing

### Detecting the Problem

```sql
-- Compare estimated vs actual rows in execution plan
-- Large discrepancy = likely parameter sniffing

-- Check plan cache for multiple plans
SELECT
    qs.plan_handle,
    qs.execution_count,
    qs.total_worker_time,
    qs.total_logical_reads,
    SUBSTRING(st.text, (qs.statement_start_offset/2)+1,
        ((CASE qs.statement_end_offset
            WHEN -1 THEN DATALENGTH(st.text)
            ELSE qs.statement_end_offset
        END - qs.statement_start_offset)/2) + 1) AS query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
WHERE st.text LIKE '%your_procedure_name%'
ORDER BY qs.total_logical_reads DESC;
```

### Solutions

```sql
-- Option 1: RECOMPILE (best for variable data distributions)
CREATE PROCEDURE GetOrders @Status VARCHAR(20)
AS
BEGIN
    SELECT * FROM Orders WHERE Status = @Status
    OPTION (RECOMPILE);
END

-- Option 2: OPTIMIZE FOR specific value
SELECT * FROM Orders WHERE Status = @Status
OPTION (OPTIMIZE FOR (@Status = 'Pending'));

-- Option 3: OPTIMIZE FOR UNKNOWN (uses average statistics)
SELECT * FROM Orders WHERE Status = @Status
OPTION (OPTIMIZE FOR UNKNOWN);

-- Option 4: Local variables (masks parameter from optimizer)
CREATE PROCEDURE GetOrders @Status VARCHAR(20)
AS
BEGIN
    DECLARE @LocalStatus VARCHAR(20) = @Status;
    SELECT * FROM Orders WHERE Status = @LocalStatus;
END
```

## Query Store Analysis

### Enable Query Store

```sql
ALTER DATABASE YourDatabase
SET QUERY_STORE = ON (
    OPERATION_MODE = READ_WRITE,
    CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30),
    DATA_FLUSH_INTERVAL_SECONDS = 900,
    MAX_STORAGE_SIZE_MB = 1000,
    INTERVAL_LENGTH_MINUTES = 60
);
```

### Find Regressed Queries

```sql
-- Queries with performance regression
SELECT
    q.query_id,
    qt.query_sql_text,
    rs1.avg_duration AS recent_avg_duration,
    rs2.avg_duration AS historical_avg_duration,
    (rs1.avg_duration - rs2.avg_duration) / rs2.avg_duration * 100 AS pct_regression
FROM sys.query_store_query q
JOIN sys.query_store_query_text qt ON q.query_text_id = qt.query_text_id
JOIN sys.query_store_plan p ON q.query_id = p.query_id
JOIN sys.query_store_runtime_stats rs1 ON p.plan_id = rs1.plan_id
JOIN sys.query_store_runtime_stats rs2 ON p.plan_id = rs2.plan_id
JOIN sys.query_store_runtime_stats_interval rsi1 ON rs1.runtime_stats_interval_id = rsi1.runtime_stats_interval_id
JOIN sys.query_store_runtime_stats_interval rsi2 ON rs2.runtime_stats_interval_id = rsi2.runtime_stats_interval_id
WHERE rsi1.start_time > DATEADD(DAY, -1, GETUTCDATE())  -- Recent
    AND rsi2.start_time < DATEADD(DAY, -7, GETUTCDATE()) -- Historical
    AND rs1.avg_duration > rs2.avg_duration * 1.5  -- 50% slower
ORDER BY pct_regression DESC;
```

### Force a Known Good Plan

```sql
-- Force specific plan for a query
EXEC sp_query_store_force_plan @query_id = 123, @plan_id = 456;

-- Unforce plan
EXEC sp_query_store_unforce_plan @query_id = 123, @plan_id = 456;
```

## Statistics Management

### Check Statistics Freshness

```sql
SELECT
    OBJECT_NAME(s.object_id) AS table_name,
    s.name AS stats_name,
    STATS_DATE(s.object_id, s.stats_id) AS last_updated,
    sp.rows,
    sp.rows_sampled,
    sp.modification_counter
FROM sys.stats s
CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) sp
WHERE OBJECTPROPERTY(s.object_id, 'IsUserTable') = 1
ORDER BY sp.modification_counter DESC;
```

### Update Statistics

```sql
-- Update all statistics on a table with full scan
UPDATE STATISTICS dbo.YourTable WITH FULLSCAN;

-- Update specific statistic
UPDATE STATISTICS dbo.YourTable IX_YourIndex WITH FULLSCAN;

-- Update all statistics in database
EXEC sp_updatestats;
```

## Tempdb Optimization

### Identify Tempdb Pressure

```sql
-- Check tempdb file usage
SELECT
    name,
    size * 8 / 1024 AS size_mb,
    FILEPROPERTY(name, 'SpaceUsed') * 8 / 1024 AS used_mb
FROM tempdb.sys.database_files;

-- Find sessions using tempdb
SELECT
    session_id,
    user_objects_alloc_page_count * 8 / 1024 AS user_objects_mb,
    internal_objects_alloc_page_count * 8 / 1024 AS internal_objects_mb
FROM sys.dm_db_session_space_usage
WHERE user_objects_alloc_page_count + internal_objects_alloc_page_count > 0
ORDER BY user_objects_alloc_page_count + internal_objects_alloc_page_count DESC;
```

### Reduce Tempdb Usage

```sql
-- Avoid SELECT INTO for large datasets, use INSERT INTO existing table
-- Reduce sort memory grants with proper indexes
-- Use batch processing for large operations

-- Check for spills in actual execution plans:
-- Sort spills, Hash spills, Exchange spills
```

## Wait Statistics

### Current Wait Analysis

```sql
SELECT TOP 20
    wait_type,
    waiting_tasks_count,
    wait_time_ms,
    max_wait_time_ms,
    signal_wait_time_ms
FROM sys.dm_os_wait_stats
WHERE wait_type NOT IN (
    'CLR_SEMAPHORE', 'LAZYWRITER_SLEEP', 'RESOURCE_QUEUE',
    'SLEEP_TASK', 'SLEEP_SYSTEMTASK', 'SQLTRACE_BUFFER_FLUSH',
    'WAITFOR', 'LOGMGR_QUEUE', 'CHECKPOINT_QUEUE',
    'REQUEST_FOR_DEADLOCK_SEARCH', 'XE_TIMER_EVENT',
    'BROKER_TO_FLUSH', 'BROKER_TASK_STOP', 'CLR_MANUAL_EVENT',
    'DISPATCHER_QUEUE_SEMAPHORE', 'FT_IFTS_SCHEDULER_IDLE_WAIT',
    'XE_DISPATCHER_WAIT', 'XE_DISPATCHER_JOIN'
)
ORDER BY wait_time_ms DESC;
```

### Common Wait Types and Solutions

| Wait Type | Typical Cause | Solution |
|-----------|---------------|----------|
| CXPACKET | Parallelism imbalance | Check MAXDOP, cost threshold |
| PAGEIOLATCH_* | Disk I/O | Add memory, faster storage, better indexes |
| LCK_M_* | Blocking | Optimize queries, reduce transaction scope |
| ASYNC_NETWORK_IO | Slow client processing | Client-side optimization |
| SOS_SCHEDULER_YIELD | CPU pressure | Optimize queries, add CPU |
| WRITELOG | Transaction log I/O | Faster log disk, batch commits |
