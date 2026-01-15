# T-SQL Transactions Reference

Isolation levels, deadlock prevention, and distributed transaction patterns.

## Table of Contents

- [Transaction Fundamentals](#transaction-fundamentals)
- [Isolation Levels](#isolation-levels)
- [Deadlock Prevention](#deadlock-prevention)
- [Lock Types and Hints](#lock-types-and-hints)
- [Distributed Transactions](#distributed-transactions)
- [Transaction Best Practices](#transaction-best-practices)

## Transaction Fundamentals

### Basic Transaction Structure

```sql
BEGIN TRY
    BEGIN TRANSACTION;

    -- Operations here
    UPDATE Accounts SET Balance = Balance - 100 WHERE AccountId = 1;
    UPDATE Accounts SET Balance = Balance + 100 WHERE AccountId = 2;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    -- Handle or rethrow error
    THROW;
END CATCH;
```

### Named Transactions and Savepoints

```sql
BEGIN TRANSACTION MainTran;

    -- First operation
    INSERT INTO Orders (CustomerId, OrderDate) VALUES (1, GETDATE());
    DECLARE @OrderId INT = SCOPE_IDENTITY();

    SAVE TRANSACTION BeforeItems;

    BEGIN TRY
        -- Can fail independently
        INSERT INTO OrderItems (OrderId, ProductId, Quantity) VALUES (@OrderId, 1, 5);
        INSERT INTO OrderItems (OrderId, ProductId, Quantity) VALUES (@OrderId, 2, 3);
    END TRY
    BEGIN CATCH
        -- Rollback only the items, keep the order
        ROLLBACK TRANSACTION BeforeItems;
        -- Log the issue but continue
    END CATCH;

COMMIT TRANSACTION MainTran;
```

### Transaction State Checking

```sql
-- Check if in a transaction
SELECT @@TRANCOUNT;  -- 0 = no transaction, > 0 = in transaction

-- Check transaction state
SELECT XACT_STATE();
-- 1 = active, committable
-- 0 = no active transaction
-- -1 = uncommittable (must rollback)

-- Use XACT_STATE in CATCH block
BEGIN CATCH
    IF XACT_STATE() = -1
        ROLLBACK TRANSACTION;  -- Must rollback
    ELSE IF XACT_STATE() = 1
        COMMIT TRANSACTION;    -- Can still commit

    THROW;
END CATCH;
```

## Isolation Levels

### Overview

| Level | Dirty Reads | Non-Repeatable Reads | Phantoms | Concurrency |
|-------|-------------|---------------------|----------|-------------|
| READ UNCOMMITTED | Yes | Yes | Yes | Highest |
| READ COMMITTED | No | Yes | Yes | High |
| REPEATABLE READ | No | No | Yes | Medium |
| SERIALIZABLE | No | No | No | Lowest |
| SNAPSHOT | No | No | No | High |
| READ COMMITTED SNAPSHOT | No | Yes | Yes | High |

### Setting Isolation Levels

```sql
-- Session level
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Query hint level
SELECT * FROM Orders WITH (NOLOCK);  -- Same as READ UNCOMMITTED
SELECT * FROM Orders WITH (HOLDLOCK);  -- Same as SERIALIZABLE

-- Check current level
SELECT CASE transaction_isolation_level
    WHEN 0 THEN 'Unspecified'
    WHEN 1 THEN 'ReadUncommitted'
    WHEN 2 THEN 'ReadCommitted'
    WHEN 3 THEN 'RepeatableRead'
    WHEN 4 THEN 'Serializable'
    WHEN 5 THEN 'Snapshot'
END
FROM sys.dm_exec_sessions
WHERE session_id = @@SPID;
```

### READ UNCOMMITTED

```sql
-- Allows dirty reads (reading uncommitted changes)
-- Use for: Rough estimates, monitoring queries, non-critical reporting

SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SELECT COUNT(*) FROM LargeTable;  -- Fast, but may include uncommitted data

-- Or use NOLOCK hint
SELECT COUNT(*) FROM LargeTable WITH (NOLOCK);

-- WARNING: Can read data that will be rolled back!
```

### READ COMMITTED (Default)

```sql
-- Prevents dirty reads, allows non-repeatable reads
-- Same row can return different values if queried twice

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION;
    SELECT Balance FROM Accounts WHERE AccountId = 1;  -- Returns 100
    -- Another transaction updates Balance to 150 and commits
    SELECT Balance FROM Accounts WHERE AccountId = 1;  -- Returns 150 (changed!)
COMMIT;
```

### REPEATABLE READ

```sql
-- Prevents dirty reads and non-repeatable reads
-- Rows read are locked until transaction ends

SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
    SELECT Balance FROM Accounts WHERE AccountId = 1;  -- Returns 100
    -- Another transaction tries to update, BLOCKED until we commit
    SELECT Balance FROM Accounts WHERE AccountId = 1;  -- Still 100
COMMIT;

-- WARNING: Can still see phantom rows (new inserts)
```

### SERIALIZABLE

```sql
-- Highest isolation, prevents all anomalies
-- Uses range locks, can cause significant blocking

SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
    SELECT * FROM Orders WHERE OrderDate = '2024-01-15';
    -- Locks the range, blocks inserts in this range too
    -- No phantoms possible
COMMIT;

-- Use sparingly due to blocking impact
```

### SNAPSHOT Isolation

```sql
-- Enable at database level (one-time setup)
ALTER DATABASE YourDatabase SET ALLOW_SNAPSHOT_ISOLATION ON;

-- Use snapshot isolation
SET TRANSACTION ISOLATION LEVEL SNAPSHOT;
BEGIN TRANSACTION;
    SELECT Balance FROM Accounts WHERE AccountId = 1;  -- Returns 100
    -- Another transaction updates to 150 and commits
    SELECT Balance FROM Accounts WHERE AccountId = 1;  -- Still 100 (sees snapshot)
COMMIT;

-- Benefits: No blocking for readers, consistent view
-- Cost: Uses tempdb for row versions, more storage
```

### READ COMMITTED SNAPSHOT

```sql
-- Enable at database level (changes default behavior)
ALTER DATABASE YourDatabase SET READ_COMMITTED_SNAPSHOT ON;

-- All READ COMMITTED queries now use row versioning
-- No code changes needed, reduces blocking significantly
-- Recommended for most OLTP applications

-- Check if enabled
SELECT is_read_committed_snapshot_on FROM sys.databases WHERE name = DB_NAME();
```

## Deadlock Prevention

### Understanding Deadlocks

```sql
-- Deadlock scenario:
-- Transaction A: Locks Row 1, wants Row 2
-- Transaction B: Locks Row 2, wants Row 1
-- Neither can proceed → Deadlock

-- SQL Server chooses a victim (usually lower cost transaction)
```

### Prevention Strategies

```sql
-- 1. Access objects in consistent order
-- Always access tables/rows in the same order across all code

-- BAD: Inconsistent order
-- Proc1: UPDATE TableA... UPDATE TableB...
-- Proc2: UPDATE TableB... UPDATE TableA...

-- GOOD: Consistent order
-- Proc1: UPDATE TableA... UPDATE TableB...
-- Proc2: UPDATE TableA... UPDATE TableB...


-- 2. Keep transactions short
BEGIN TRANSACTION;
    -- Do minimal work inside transaction
    -- Move calculations, validations outside
COMMIT;


-- 3. Use appropriate isolation level
-- SNAPSHOT isolation eliminates reader-writer deadlocks


-- 4. Use UPDLOCK hint when you will update after reading
SELECT * FROM Orders WITH (UPDLOCK, ROWLOCK)
WHERE OrderId = @OrderId;
-- Now holds update lock, prevents deadlocks from lock escalation


-- 5. Use ROWLOCK to prevent lock escalation
UPDATE Orders WITH (ROWLOCK)
SET Status = 'Shipped'
WHERE OrderId = @OrderId;
```

### Deadlock Detection and Handling

```sql
-- Enable deadlock trace flag (for debugging)
DBCC TRACEON(1222, -1);  -- Detailed deadlock info to error log

-- Extended Events for deadlock monitoring
CREATE EVENT SESSION DeadlockCapture ON SERVER
ADD EVENT sqlserver.xml_deadlock_report
ADD TARGET package0.event_file(SET filename=N'Deadlocks.xel');
ALTER EVENT SESSION DeadlockCapture ON SERVER STATE = START;

-- Handle deadlock in code (retry pattern)
DECLARE @RetryCount INT = 3;
DECLARE @Success BIT = 0;

WHILE @RetryCount > 0 AND @Success = 0
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;

        -- Your operations

        COMMIT;
        SET @Success = 1;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;

        IF ERROR_NUMBER() = 1205  -- Deadlock
        BEGIN
            SET @RetryCount -= 1;
            IF @RetryCount > 0
                WAITFOR DELAY '00:00:00.100';  -- Brief pause before retry
            ELSE
                THROW;  -- Out of retries
        END
        ELSE
            THROW;  -- Not a deadlock, rethrow immediately
    END CATCH
END
```

## Lock Types and Hints

### Lock Types

| Lock | Abbreviation | Description |
|------|--------------|-------------|
| Shared | S | Reading, allows other reads |
| Update | U | Will update, prevents deadlocks |
| Exclusive | X | Writing, blocks everything |
| Intent | IS, IX, IU | Table-level indication of row locks |
| Schema | Sch-S, Sch-M | DDL operations |

### Lock Hints

```sql
-- NOLOCK: Don't acquire locks (dirty reads possible)
SELECT * FROM Orders WITH (NOLOCK);

-- HOLDLOCK: Hold locks until transaction ends (like SERIALIZABLE)
SELECT * FROM Orders WITH (HOLDLOCK);

-- UPDLOCK: Acquire update lock immediately
SELECT * FROM Orders WITH (UPDLOCK) WHERE OrderId = @Id;

-- ROWLOCK: Use row-level locks
UPDATE Orders WITH (ROWLOCK) SET Status = 'Done' WHERE OrderId = @Id;

-- TABLOCK: Lock entire table
SELECT * FROM SmallTable WITH (TABLOCK);

-- TABLOCKX: Exclusive table lock
TRUNCATE TABLE StagingData;  -- Implicitly uses TABLOCKX

-- READPAST: Skip locked rows
SELECT TOP 10 * FROM JobQueue WITH (READPAST, UPDLOCK)
WHERE Status = 'Pending';  -- Queue processing pattern
```

### Queue Processing Pattern

```sql
-- Safe queue processing with READPAST
CREATE PROCEDURE ProcessNextJob
AS
BEGIN
    DECLARE @JobId INT;

    BEGIN TRANSACTION;

    -- Get next available job, skip locked ones
    SELECT TOP 1 @JobId = JobId
    FROM JobQueue WITH (UPDLOCK, READPAST)
    WHERE Status = 'Pending'
    ORDER BY CreatedAt;

    IF @JobId IS NOT NULL
    BEGIN
        UPDATE JobQueue SET Status = 'Processing' WHERE JobId = @JobId;
        COMMIT;

        -- Process outside transaction
        EXEC ProcessJob @JobId;
    END
    ELSE
        COMMIT;
END
```

## Distributed Transactions

### Linked Server Transactions

```sql
-- Enable distributed transactions
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'ad hoc distributed queries', 1;
RECONFIGURE;

-- Distributed transaction across linked servers
BEGIN DISTRIBUTED TRANSACTION;

    UPDATE LocalServer.dbo.Accounts SET Balance = Balance - 100 WHERE Id = 1;
    UPDATE LinkedServer.RemoteDB.dbo.Accounts SET Balance = Balance + 100 WHERE Id = 2;

COMMIT;

-- Requires MS DTC (Distributed Transaction Coordinator)
```

### Two-Phase Commit Simulation

```sql
-- When you can't use MSDTC, use application-level compensation

-- Phase 1: Prepare (mark as pending)
BEGIN TRANSACTION;
    UPDATE Accounts SET Balance = Balance - 100, PendingTransfer = @TransferId
    WHERE AccountId = 1;

    -- Call remote system to reserve funds
    EXEC @Success = RemoteSystem.ReserveFunds @Amount = 100, @TransferId = @TransferId;

    IF @Success = 0
    BEGIN
        ROLLBACK;
        RETURN;
    END
COMMIT;

-- Phase 2: Commit (finalize)
BEGIN TRANSACTION;
    UPDATE Accounts SET PendingTransfer = NULL WHERE AccountId = 1;
    EXEC RemoteSystem.ConfirmTransfer @TransferId = @TransferId;
COMMIT;

-- Compensation if Phase 2 fails
-- Rollback local changes and call RemoteSystem.CancelReservation
```

### Saga Pattern for Long-Running Transactions

```sql
-- Instead of distributed transaction, use saga with compensating actions

CREATE TABLE SagaLog (
    SagaId UNIQUEIDENTIFIER PRIMARY KEY,
    Step INT,
    StepName VARCHAR(100),
    Status VARCHAR(20),  -- Completed, Failed, Compensated
    CompensatingAction VARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT SYSDATETIME()
);

-- Execute saga step
CREATE PROCEDURE ExecuteSagaStep
    @SagaId UNIQUEIDENTIFIER,
    @StepNumber INT,
    @StepName VARCHAR(100),
    @ActionSql NVARCHAR(MAX),
    @CompensatingSql NVARCHAR(MAX)
AS
BEGIN
    BEGIN TRY
        -- Log step start
        INSERT INTO SagaLog (SagaId, Step, StepName, Status, CompensatingAction)
        VALUES (@SagaId, @StepNumber, @StepName, 'Running', @CompensatingSql);

        -- Execute action
        EXEC sp_executesql @ActionSql;

        -- Mark complete
        UPDATE SagaLog SET Status = 'Completed'
        WHERE SagaId = @SagaId AND Step = @StepNumber;
    END TRY
    BEGIN CATCH
        -- Mark failed and trigger compensation
        UPDATE SagaLog SET Status = 'Failed'
        WHERE SagaId = @SagaId AND Step = @StepNumber;

        EXEC CompensateSaga @SagaId;
        THROW;
    END CATCH
END

-- Compensate all completed steps in reverse order
CREATE PROCEDURE CompensateSaga @SagaId UNIQUEIDENTIFIER
AS
BEGIN
    DECLARE @CompensatingSql NVARCHAR(MAX);

    DECLARE compensation_cursor CURSOR FOR
        SELECT CompensatingAction FROM SagaLog
        WHERE SagaId = @SagaId AND Status = 'Completed'
        ORDER BY Step DESC;

    OPEN compensation_cursor;
    FETCH NEXT FROM compensation_cursor INTO @CompensatingSql;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        EXEC sp_executesql @CompensatingSql;
        FETCH NEXT FROM compensation_cursor INTO @CompensatingSql;
    END

    CLOSE compensation_cursor;
    DEALLOCATE compensation_cursor;

    UPDATE SagaLog SET Status = 'Compensated'
    WHERE SagaId = @SagaId AND Status = 'Completed';
END
```

## Transaction Best Practices

```sql
-- 1. Keep transactions as short as possible
-- Do validations and calculations before BEGIN TRANSACTION

-- 2. Avoid user interaction during transactions
-- Never WAITFOR or call external services inside transaction

-- 3. Handle errors properly
BEGIN TRY
    BEGIN TRANSACTION;
    -- work
    COMMIT;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;
END CATCH;

-- 4. Use SET XACT_ABORT ON for consistent behavior
SET XACT_ABORT ON;  -- Auto-rollback on any error

-- 5. Consider SNAPSHOT isolation for read-heavy workloads

-- 6. Monitor blocking
SELECT * FROM sys.dm_exec_requests WHERE blocking_session_id <> 0;

-- 7. Set appropriate lock timeout
SET LOCK_TIMEOUT 5000;  -- 5 second timeout, returns error instead of waiting forever
```
