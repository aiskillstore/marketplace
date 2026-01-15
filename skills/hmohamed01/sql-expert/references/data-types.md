# T-SQL Data Types Reference

Type selection guidelines, collation handling, and precision/scale considerations.

## Table of Contents

- [Numeric Types](#numeric-types)
- [String Types](#string-types)
- [Date and Time Types](#date-and-time-types)
- [Collation](#collation)
- [Binary Types](#binary-types)
- [GUID / UNIQUEIDENTIFIER](#guid--uniqueidentifier)
- [Type Conversion](#type-conversion)
- [Storage Optimization Tips](#storage-optimization-tips)

## Numeric Types

### Integer Selection Guide

| Type | Range | Storage | Use Case |
|------|-------|---------|----------|
| TINYINT | 0 to 255 | 1 byte | Status codes, small counters |
| SMALLINT | -32,768 to 32,767 | 2 bytes | Limited-range integers |
| INT | ±2.1 billion | 4 bytes | Default for most IDs, counters |
| BIGINT | ±9.2 quintillion | 8 bytes | Large sequences, timestamps |

```sql
-- Common mistake: Using BIGINT for everything
-- Better: Match type to actual data range

-- Auto-increment IDs
CREATE TABLE Orders (
    OrderId INT IDENTITY(1,1) PRIMARY KEY,  -- INT unless you expect > 2B rows
    ...
);

-- When to use BIGINT
CREATE TABLE EventLog (
    EventId BIGINT IDENTITY(1,1) PRIMARY KEY,  -- High-volume logging
    ...
);
```

### Decimal vs Float

```sql
-- DECIMAL(p,s): Exact numeric, use for money/financial
-- p = total digits (1-38), s = decimal places

DECIMAL(10,2)  -- 99,999,999.99 (currency)
DECIMAL(18,4)  -- 99,999,999,999,999.9999 (precise calculations)
DECIMAL(5,4)   -- 9.9999 (rates, percentages as decimals)

-- FLOAT/REAL: Approximate numeric, use for scientific data
FLOAT          -- 8 bytes, 15-digit precision
REAL           -- 4 bytes, 7-digit precision

-- WARNING: Never use FLOAT for money
DECLARE @f FLOAT = 0.1 + 0.1 + 0.1;
SELECT @f;  -- 0.30000000000000004 (floating point error!)

-- MONEY/SMALLMONEY: Fixed 4 decimal places
MONEY          -- 8 bytes, ±922 trillion
SMALLMONEY     -- 4 bytes, ±214,748.3647

-- Prefer DECIMAL over MONEY for explicit precision control
```

### Precision and Scale Examples

```sql
-- Common patterns
DECIMAL(19,4)  -- Standard financial (up to 999 trillion with 4 decimals)
DECIMAL(10,2)  -- Typical prices/amounts
DECIMAL(5,2)   -- Percentages (0.00 to 999.99)
DECIMAL(9,6)   -- GPS coordinates latitude/longitude
DECIMAL(38,18) -- Cryptocurrency amounts (high precision needed)

-- Scale determines rounding
DECLARE @d DECIMAL(5,2) = 123.456;
SELECT @d;  -- Returns 123.46 (rounded)

-- Overflow throws error
DECLARE @d2 DECIMAL(5,2) = 1234.56;  -- Error: arithmetic overflow
```

## String Types

### VARCHAR vs NVARCHAR

```sql
-- VARCHAR: 1 byte per character, ASCII/extended ASCII
-- NVARCHAR: 2 bytes per character, Unicode (supports all languages)

-- Use VARCHAR when:
-- - Data is guaranteed ASCII (codes, identifiers, English-only)
-- - Storage optimization is critical
VARCHAR(50)    -- Up to 50 characters
VARCHAR(MAX)   -- Up to 2GB

-- Use NVARCHAR when:
-- - Supporting international characters
-- - User-generated content
-- - Names, addresses, descriptions
NVARCHAR(100)  -- Up to 100 characters (200 bytes)
NVARCHAR(MAX)  -- Up to 2GB

-- Common mistake: Implicit conversion
DECLARE @v VARCHAR(50) = 'test';
SELECT * FROM Users WHERE Name = @v;  -- If Name is NVARCHAR, causes implicit conversion!
```

### String Length Guidelines

```sql
-- Match actual data requirements
VARCHAR(50)    -- First/last names
VARCHAR(100)   -- Email addresses (max spec is 254, but 100 covers 99%)
VARCHAR(255)   -- URLs, file paths
NVARCHAR(MAX)  -- Free-form text, descriptions

-- Avoid arbitrary large sizes
VARCHAR(4000)  -- If data is always < 100 chars, wastes memory estimates

-- MAX types: Different storage behavior
-- Under 8KB: stored in-row
-- Over 8KB: stored as LOB
```

### CHAR vs VARCHAR

```sql
-- CHAR: Fixed length, padded with spaces
-- VARCHAR: Variable length, no padding

-- Use CHAR for:
CHAR(2)   -- State codes ('CA', 'NY')
CHAR(3)   -- Currency codes ('USD', 'EUR')
CHAR(5)   -- ZIP codes
CHAR(10)  -- Phone numbers (fixed format)

-- Use VARCHAR for:
-- Everything else where length varies

-- CHAR gotcha: Trailing space comparison
DECLARE @c CHAR(10) = 'test';
DECLARE @v VARCHAR(10) = 'test';
SELECT DATALENGTH(@c), DATALENGTH(@v);  -- 10, 4
SELECT CASE WHEN @c = @v THEN 'Equal' ELSE 'Different' END;  -- Equal (spaces ignored)
SELECT CASE WHEN @c = 'test' THEN 'Match' END;  -- Match (padding handled)
```

## Date and Time Types

### Type Selection

| Type | Range | Precision | Storage | Use Case |
|------|-------|-----------|---------|----------|
| DATE | 0001-01-01 to 9999-12-31 | 1 day | 3 bytes | Birth dates, calendar dates |
| TIME | 00:00:00 to 23:59:59.9999999 | 100ns | 3-5 bytes | Time of day only |
| DATETIME | 1753 to 9999 | 3.33ms | 8 bytes | Legacy, avoid for new code |
| DATETIME2 | 0001 to 9999 | 100ns | 6-8 bytes | Default for timestamps |
| DATETIMEOFFSET | 0001 to 9999 | 100ns + TZ | 8-10 bytes | Time zone aware |
| SMALLDATETIME | 1900 to 2079 | 1 minute | 4 bytes | Space-constrained, minute precision OK |

```sql
-- Modern best practice: Use DATETIME2
CREATE TABLE Events (
    EventId INT PRIMARY KEY,
    CreatedAt DATETIME2(3) DEFAULT SYSDATETIME(),  -- Millisecond precision
    ScheduledDate DATE,  -- When time doesn't matter
    Duration TIME(0)     -- When date doesn't matter
);

-- Time zone aware (for global applications)
CREATE TABLE AuditLog (
    LogId BIGINT PRIMARY KEY,
    Timestamp DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET()
);

-- Precision affects storage
DATETIME2(0)  -- Seconds, 6 bytes
DATETIME2(3)  -- Milliseconds, 7 bytes
DATETIME2(7)  -- 100 nanoseconds, 8 bytes (default)
```

### Date Arithmetic

```sql
-- Use DATEADD/DATEDIFF, not arithmetic
SELECT DATEADD(DAY, 7, GETDATE());           -- Add 7 days
SELECT DATEADD(MONTH, -1, GETDATE());        -- Subtract 1 month
SELECT DATEDIFF(DAY, StartDate, EndDate);    -- Days between

-- Date truncation patterns
SELECT CAST(GETDATE() AS DATE);                                    -- Remove time
SELECT DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0);          -- First of month
SELECT EOMONTH(GETDATE());                                         -- Last of month
SELECT DATEADD(QUARTER, DATEDIFF(QUARTER, 0, GETDATE()), 0);      -- First of quarter

-- SQL Server 2022+
SELECT DATETRUNC(MONTH, GETDATE());  -- Cleaner truncation
```

## Collation

### Understanding Collation

```sql
-- Collation affects: sorting, comparison, case sensitivity

-- Check current collation
SELECT DATABASEPROPERTYEX(DB_NAME(), 'Collation');
SELECT name, collation_name FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Users');

-- Common collations
-- SQL_Latin1_General_CP1_CI_AS  -- Case Insensitive, Accent Sensitive (common default)
-- Latin1_General_CS_AS          -- Case Sensitive
-- Latin1_General_100_CI_AI      -- Case & Accent Insensitive

-- CI = Case Insensitive, CS = Case Sensitive
-- AI = Accent Insensitive, AS = Accent Sensitive
-- BIN = Binary (exact byte comparison)
```

### Collation Conflicts

```sql
-- Problem: Comparing columns with different collations
SELECT * FROM TableA a
JOIN TableB b ON a.Name = b.Name;  -- Error if collations differ!

-- Solution: Explicit COLLATE
SELECT * FROM TableA a
JOIN TableB b ON a.Name = b.Name COLLATE Latin1_General_CI_AS;

-- Or create with matching collation
CREATE TABLE Example (
    Name NVARCHAR(100) COLLATE Latin1_General_CI_AS
);
```

### Case-Sensitive Operations

```sql
-- Force case-sensitive comparison (even on CI database)
SELECT * FROM Users
WHERE Name COLLATE Latin1_General_CS_AS = 'Smith';

-- Force case-insensitive comparison (even on CS database)
SELECT * FROM Users
WHERE Name COLLATE Latin1_General_CI_AS = 'SMITH';

-- Case-sensitive index for performance
CREATE INDEX IX_Users_Name_CS ON Users(Name)
WHERE Name = Name COLLATE Latin1_General_CS_AS;
```

## Binary Types

```sql
-- BINARY: Fixed length
BINARY(16)     -- UUID/GUID storage (UNIQUEIDENTIFIER uses 16 bytes)
BINARY(32)     -- SHA-256 hash

-- VARBINARY: Variable length
VARBINARY(MAX) -- Files, images, documents
VARBINARY(256) -- Encryption keys, hashes

-- Convert to/from hex
SELECT CONVERT(VARBINARY(32), 0x48656C6C6F);  -- From hex literal
SELECT CONVERT(VARCHAR(100), @binary, 2);     -- To hex string (no 0x prefix)
SELECT CONVERT(VARCHAR(100), @binary, 1);     -- To hex string (with 0x prefix)

-- Hash example
SELECT HASHBYTES('SHA2_256', 'password123');  -- Returns VARBINARY(32)
```

## GUID / UNIQUEIDENTIFIER

```sql
-- 16-byte globally unique identifier
CREATE TABLE Documents (
    DocumentId UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    ...
);

-- NEWID() vs NEWSEQUENTIALID()
NEWID()           -- Random, causes page splits on clustered index
NEWSEQUENTIALID() -- Sequential per server restart, better for clustering

-- Best practice: Don't cluster on random GUID
CREATE TABLE Documents (
    Id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,  -- Clustered on INT
    DocumentId UNIQUEIDENTIFIER DEFAULT NEWID() UNIQUE NONCLUSTERED
);
```

## Type Conversion

### Implicit vs Explicit

```sql
-- Data type precedence (higher wins in implicit conversion)
-- 1. DATETIMEOFFSET > DATETIME2 > DATETIME > DATE/TIME
-- 2. FLOAT > REAL
-- 3. DECIMAL > MONEY > INT > SMALLINT > TINYINT
-- 4. NVARCHAR > VARCHAR > NCHAR > CHAR

-- Dangerous implicit conversion (causes index scan)
DECLARE @v VARCHAR(50) = 'test';
SELECT * FROM Users WHERE Name = @v;  -- If Name is NVARCHAR!

-- Safe: Match types
DECLARE @n NVARCHAR(50) = N'test';
SELECT * FROM Users WHERE Name = @n;

-- Explicit conversion
CAST(expression AS target_type)    -- ANSI standard
CONVERT(target_type, expression)   -- SQL Server, has style options
TRY_CAST(expression AS type)       -- Returns NULL on failure
TRY_CONVERT(type, expression)      -- Returns NULL on failure
```

### Common Conversions

```sql
-- Date to string
SELECT CONVERT(VARCHAR(10), GETDATE(), 120);    -- 2024-01-15
SELECT CONVERT(VARCHAR(10), GETDATE(), 101);    -- 01/15/2024
SELECT FORMAT(GETDATE(), 'yyyy-MM-dd');         -- 2024-01-15 (slower but flexible)

-- String to date
SELECT CAST('2024-01-15' AS DATE);
SELECT TRY_CAST('invalid' AS DATE);  -- NULL instead of error

-- Number formatting
SELECT FORMAT(1234567.89, 'N2');     -- 1,234,567.89
SELECT FORMAT(0.156, 'P1');          -- 15.6%

-- JSON conversion (2016+)
SELECT * FROM OpenJson(@json);
SELECT (SELECT * FROM table FOR JSON PATH);
```

## Storage Optimization Tips

```sql
-- Column order affects storage (variable-length columns at end)
CREATE TABLE Optimized (
    Id INT NOT NULL,              -- Fixed: 4 bytes
    Status TINYINT NOT NULL,      -- Fixed: 1 byte
    Amount DECIMAL(10,2) NOT NULL,-- Fixed: 5 bytes
    Name NVARCHAR(100) NULL,      -- Variable
    Description NVARCHAR(MAX) NULL -- Variable (possibly LOB)
);

-- Computed columns (no storage, calculated on read)
CREATE TABLE Orders (
    Quantity INT,
    UnitPrice DECIMAL(10,2),
    TotalPrice AS (Quantity * UnitPrice)  -- Virtual column
);

-- Persisted computed columns (stored, can be indexed)
CREATE TABLE Orders (
    OrderDate DATETIME2,
    OrderYear AS YEAR(OrderDate) PERSISTED  -- Stored, indexable
);

-- Sparse columns (for columns with many NULLs)
CREATE TABLE SparseExample (
    Id INT PRIMARY KEY,
    RareValue1 INT SPARSE NULL,
    RareValue2 NVARCHAR(100) SPARSE NULL
);
```
