# T-SQL Security Reference

SQL injection prevention, dynamic SQL safety, and permission patterns.

## SQL Injection Prevention

### The Core Problem

```sql
-- VULNERABLE: String concatenation with user input
DECLARE @sql NVARCHAR(MAX) = N'SELECT * FROM Users WHERE Name = ''' + @UserInput + '''';
EXEC(@sql);

-- If @UserInput = "'; DROP TABLE Users; --"
-- Executed: SELECT * FROM Users WHERE Name = ''; DROP TABLE Users; --'
```

### Solution: Parameterized Queries

```sql
-- SAFE: Using sp_executesql with parameters
DECLARE @sql NVARCHAR(MAX) = N'SELECT * FROM Users WHERE Name = @Name';
EXEC sp_executesql @sql, N'@Name NVARCHAR(100)', @Name = @UserInput;
```

### When You Must Use Dynamic SQL

```sql
-- Scenario: Dynamic column or table names (can't be parameterized)

-- UNSAFE
SET @sql = N'SELECT * FROM ' + @TableName;

-- SAFER: Validate against whitelist
IF @TableName NOT IN ('Orders', 'Products', 'Customers')
BEGIN
    RAISERROR('Invalid table name', 16, 1);
    RETURN;
END

-- SAFER: Use QUOTENAME to escape identifiers
SET @sql = N'SELECT * FROM ' + QUOTENAME(@TableName);

-- SAFEST: Map to known values
DECLARE @ActualTable NVARCHAR(128) = CASE @TableName
    WHEN 'orders' THEN 'dbo.Orders'
    WHEN 'products' THEN 'dbo.Products'
    ELSE NULL
END;

IF @ActualTable IS NULL
BEGIN
    RAISERROR('Invalid table name', 16, 1);
    RETURN;
END

SET @sql = N'SELECT * FROM ' + @ActualTable;
```

## Safe Dynamic SQL Patterns

### Dynamic Search with Optional Filters

```sql
CREATE PROCEDURE SearchProducts
    @Name NVARCHAR(100) = NULL,
    @CategoryId INT = NULL,
    @MinPrice DECIMAL(10,2) = NULL,
    @MaxPrice DECIMAL(10,2) = NULL
AS
BEGIN
    DECLARE @sql NVARCHAR(MAX) = N'
        SELECT ProductId, Name, Price, CategoryId
        FROM Products
        WHERE 1=1';

    DECLARE @params NVARCHAR(MAX) = N'
        @Name NVARCHAR(100),
        @CategoryId INT,
        @MinPrice DECIMAL(10,2),
        @MaxPrice DECIMAL(10,2)';

    -- Build WHERE clause with parameters (not concatenation)
    IF @Name IS NOT NULL
        SET @sql += N' AND Name LIKE @Name + ''%''';

    IF @CategoryId IS NOT NULL
        SET @sql += N' AND CategoryId = @CategoryId';

    IF @MinPrice IS NOT NULL
        SET @sql += N' AND Price >= @MinPrice';

    IF @MaxPrice IS NOT NULL
        SET @sql += N' AND Price <= @MaxPrice';

    EXEC sp_executesql @sql, @params,
        @Name = @Name,
        @CategoryId = @CategoryId,
        @MinPrice = @MinPrice,
        @MaxPrice = @MaxPrice;
END
```

### Dynamic ORDER BY

```sql
-- Can't parameterize ORDER BY columns, but can validate
CREATE PROCEDURE GetProducts
    @SortColumn NVARCHAR(50) = 'Name',
    @SortDirection NVARCHAR(4) = 'ASC'
AS
BEGIN
    -- Whitelist validation
    IF @SortColumn NOT IN ('Name', 'Price', 'CreatedDate', 'CategoryId')
        SET @SortColumn = 'Name';

    IF @SortDirection NOT IN ('ASC', 'DESC')
        SET @SortDirection = 'ASC';

    DECLARE @sql NVARCHAR(MAX) = N'
        SELECT ProductId, Name, Price, CreatedDate
        FROM Products
        ORDER BY ' + QUOTENAME(@SortColumn) + N' ' + @SortDirection;

    EXEC sp_executesql @sql;
END
```

### Dynamic Pivot Safely

```sql
CREATE PROCEDURE GetSalesPivot
    @Year INT
AS
BEGIN
    -- Validate year range
    IF @Year < 2000 OR @Year > YEAR(GETDATE()) + 1
    BEGIN
        RAISERROR('Invalid year', 16, 1);
        RETURN;
    END

    DECLARE @columns NVARCHAR(MAX);

    -- Build column list from actual data (not user input)
    SELECT @columns = STRING_AGG(QUOTENAME(MonthName), ', ')
    FROM (
        SELECT DISTINCT DATENAME(MONTH, SaleDate) AS MonthName
        FROM Sales
        WHERE YEAR(SaleDate) = @Year
    ) AS months;

    DECLARE @sql NVARCHAR(MAX) = N'
        SELECT *
        FROM (
            SELECT
                ProductId,
                DATENAME(MONTH, SaleDate) AS MonthName,
                Amount
            FROM Sales
            WHERE YEAR(SaleDate) = @Year
        ) AS src
        PIVOT (SUM(Amount) FOR MonthName IN (' + @columns + N')) AS pvt';

    EXEC sp_executesql @sql, N'@Year INT', @Year = @Year;
END
```

## Permission Patterns

### Principle of Least Privilege

```sql
-- Create role for application
CREATE ROLE AppReadWrite;

-- Grant only necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Orders TO AppReadWrite;
GRANT SELECT ON dbo.Products TO AppReadWrite;
GRANT EXECUTE ON dbo.ProcessOrder TO AppReadWrite;

-- Deny dangerous operations
DENY ALTER, DROP TO AppReadWrite;

-- Add user to role
ALTER ROLE AppReadWrite ADD MEMBER AppServiceAccount;
```

### Schema-Based Security

```sql
-- Create schemas for different access levels
CREATE SCHEMA reporting;
CREATE SCHEMA sensitive;

-- Create views in reporting schema for safe access
CREATE VIEW reporting.OrderSummary AS
SELECT
    OrderId,
    OrderDate,
    TotalAmount
    -- Note: No customer PII exposed
FROM dbo.Orders;

-- Grant access to reporting schema only
GRANT SELECT ON SCHEMA::reporting TO ReportingRole;
```

### Row-Level Security

```sql
-- Create security predicate function
CREATE FUNCTION dbo.fn_SecurityPredicate(@TenantId INT)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
WHERE @TenantId = CAST(SESSION_CONTEXT(N'TenantId') AS INT);

-- Create security policy
CREATE SECURITY POLICY TenantFilter
ADD FILTER PREDICATE dbo.fn_SecurityPredicate(TenantId) ON dbo.Orders,
ADD BLOCK PREDICATE dbo.fn_SecurityPredicate(TenantId) ON dbo.Orders
WITH (STATE = ON);

-- Set tenant context in application
EXEC sp_set_session_context @key = N'TenantId', @value = 42;
```

### Stored Procedure Security

```sql
-- Execute as owner for elevated permissions
CREATE PROCEDURE dbo.AdminOperation
WITH EXECUTE AS OWNER
AS
BEGIN
    -- This runs with owner's permissions, not caller's
    -- Use carefully and validate inputs thoroughly
END

-- Signature-based permission elevation
CREATE CERTIFICATE ProcCert WITH SUBJECT = 'Procedure signing';
CREATE USER ProcCertUser FROM CERTIFICATE ProcCert;
GRANT INSERT ON dbo.AuditLog TO ProcCertUser;

ADD SIGNATURE TO dbo.MyProcedure BY CERTIFICATE ProcCert;
-- Now MyProcedure can INSERT to AuditLog even if caller can't
```

## Data Masking

### Dynamic Data Masking

```sql
-- Mask SSN to show only last 4 digits
ALTER TABLE Customers
ALTER COLUMN SSN ADD MASKED WITH (FUNCTION = 'partial(0,"XXX-XX-",4)');

-- Mask email
ALTER TABLE Customers
ALTER COLUMN Email ADD MASKED WITH (FUNCTION = 'email()');

-- Random mask for numbers
ALTER TABLE Employees
ALTER COLUMN Salary ADD MASKED WITH (FUNCTION = 'random(1000, 5000)');

-- Grant unmask permission to specific role
GRANT UNMASK TO HRManager;
```

### Column-Level Encryption

```sql
-- Create master key and certificate
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'StrongPassword123!';
CREATE CERTIFICATE SSNCert WITH SUBJECT = 'SSN Encryption';
CREATE SYMMETRIC KEY SSNKey WITH ALGORITHM = AES_256
    ENCRYPTION BY CERTIFICATE SSNCert;

-- Encrypt data
OPEN SYMMETRIC KEY SSNKey DECRYPTION BY CERTIFICATE SSNCert;

UPDATE Customers
SET SSN_Encrypted = ENCRYPTBYKEY(KEY_GUID('SSNKey'), SSN);

CLOSE SYMMETRIC KEY SSNKey;

-- Decrypt data
OPEN SYMMETRIC KEY SSNKey DECRYPTION BY CERTIFICATE SSNCert;

SELECT
    CustomerId,
    CONVERT(VARCHAR(11), DECRYPTBYKEY(SSN_Encrypted)) AS SSN
FROM Customers;

CLOSE SYMMETRIC KEY SSNKey;
```

## Audit Logging

### SQL Server Audit

```sql
-- Create server audit
CREATE SERVER AUDIT SecurityAudit
TO FILE (FILEPATH = 'C:\Audits\', MAXSIZE = 100MB);

-- Create database audit specification
CREATE DATABASE AUDIT SPECIFICATION SensitiveDataAudit
FOR SERVER AUDIT SecurityAudit
ADD (SELECT, INSERT, UPDATE, DELETE ON dbo.Customers BY public),
ADD (EXECUTE ON dbo.ProcessPayment BY public)
WITH (STATE = ON);

ALTER SERVER AUDIT SecurityAudit WITH (STATE = ON);
```

### Custom Audit Table

```sql
CREATE TABLE dbo.AuditLog (
    AuditId BIGINT IDENTITY PRIMARY KEY,
    TableName NVARCHAR(128),
    Operation CHAR(1), -- I, U, D
    PrimaryKeyValue NVARCHAR(MAX),
    OldValues NVARCHAR(MAX),
    NewValues NVARCHAR(MAX),
    ModifiedBy NVARCHAR(128) DEFAULT SUSER_SNAME(),
    ModifiedAt DATETIME2 DEFAULT SYSDATETIME()
);

-- Audit trigger example
CREATE TRIGGER trg_Customers_Audit ON dbo.Customers
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Operation CHAR(1) =
        CASE
            WHEN EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted) THEN 'U'
            WHEN EXISTS(SELECT 1 FROM inserted) THEN 'I'
            ELSE 'D'
        END;

    INSERT INTO dbo.AuditLog (TableName, Operation, PrimaryKeyValue, OldValues, NewValues)
    SELECT
        'Customers',
        @Operation,
        COALESCE(i.CustomerId, d.CustomerId),
        (SELECT d.* FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
        (SELECT i.* FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
    FROM inserted i
    FULL OUTER JOIN deleted d ON i.CustomerId = d.CustomerId;
END
```

## Common Vulnerabilities Checklist

| Vulnerability | Detection | Mitigation |
|--------------|-----------|------------|
| String concatenation in dynamic SQL | Search for `+ @` or `+ '''` | Use sp_executesql with parameters |
| EXEC with user input | Search for `EXEC(@` | Validate/whitelist, use sp_executesql |
| Missing QUOTENAME | Dynamic object names without escaping | Always use QUOTENAME() |
| xp_cmdshell enabled | Check sys.configurations | Disable unless absolutely required |
| sa account in use | Check connection strings | Use least-privilege accounts |
| Plaintext passwords | Search for 'password' in code | Use Always Encrypted or hashing |
| TRUSTWORTHY ON | Check sys.databases | Set to OFF unless required |
| Excessive permissions | Review role memberships | Implement least privilege |
