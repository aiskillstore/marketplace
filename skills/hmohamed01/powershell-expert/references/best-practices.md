# PowerShell Best Practices Reference

## Table of Contents
1. [Naming Conventions](#naming-conventions)
2. [Parameter Design](#parameter-design)
3. [Pipeline Support](#pipeline-support)
4. [Error Handling](#error-handling)
5. [Output Patterns](#output-patterns)
6. [Code Style](#code-style)

---

## Naming Conventions

### Cmdlet/Function Names
- **Verb-Noun format**: Always use approved verbs from `Get-Verb`
- **Pascal Case**: Capitalize first letter of verb and all noun terms
- **Singular Nouns**: Even for cmdlets operating on multiple items
- **Specific Nouns**: Use product-specific nouns, not generic terms

```powershell
# Good
Get-SQLServer
New-AzureStorageAccount
Remove-UserSession

# Bad
Get-Server           # Too generic
Get-Servers          # Plural noun
get-sqlserver        # Wrong case
```

### Parameter Names
- **Pascal Case**: `ErrorAction`, not `errorAction`
- **Singular Names**: Unless parameter always accepts arrays
- **Standard Names**: Use established parameter names with aliases

```powershell
param(
    [Parameter(Mandatory)]
    [string]$Name,

    [Alias('ComputerName', 'CN')]
    [string]$Server,

    [string[]]$Tags  # Plural - accepts array
)
```

### Variable Names
- **$PascalCase** for script/global scope
- **$camelCase** acceptable for local scope
- **Descriptive names** over abbreviations

---

## Parameter Design

### Use Strong Typing
```powershell
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Name,

    [ValidateRange(1, 100)]
    [int]$Count = 10,

    [ValidateSet('Debug', 'Info', 'Warning', 'Error')]
    [string]$LogLevel = 'Info',

    [switch]$Force,

    [nullable[bool]]$Enabled  # Three states: true, false, unspecified
)
```

### Parameter Sets
```powershell
[CmdletBinding(DefaultParameterSetName = 'ByName')]
param(
    [Parameter(ParameterSetName = 'ByName', Position = 0)]
    [string]$Name,

    [Parameter(ParameterSetName = 'ByID')]
    [int]$ID,

    [Parameter(ParameterSetName = 'ByObject', ValueFromPipeline)]
    [PSObject]$InputObject
)
```

### Common Parameters to Support
| Parameter | Use Case |
|-----------|----------|
| `-Force` | Override warnings/protections |
| `-PassThru` | Return modified objects |
| `-WhatIf` | Preview changes without executing |
| `-Confirm` | Prompt before executing |
| `-Verbose` | Detailed operational info |

### Path Parameters
```powershell
param(
    [Parameter(ParameterSetName = 'Path')]
    [SupportsWildcards()]
    [string[]]$Path,

    [Parameter(ParameterSetName = 'LiteralPath')]
    [Alias('PSPath')]
    [string[]]$LiteralPath
)
```

---

## Pipeline Support

### Accept Pipeline Input
```powershell
param(
    [Parameter(ValueFromPipeline)]
    [string[]]$Name,

    [Parameter(ValueFromPipelineByPropertyName)]
    [Alias('FullName')]
    [string]$Path
)

process {
    foreach ($item in $Name) {
        # Process each item immediately
        Write-Output $result
    }
}
```

### Write Objects Immediately
```powershell
# Good - stream output
foreach ($item in $collection) {
    $result = Process-Item $item
    Write-Output $result
}

# Bad - buffer then output
$results = @()
foreach ($item in $collection) {
    $results += Process-Item $item
}
$results
```

---

## Error Handling

### Use Try/Catch with Specific Errors
```powershell
try {
    $result = Get-Content -Path $Path -ErrorAction Stop
}
catch [System.IO.FileNotFoundException] {
    Write-Error "File not found: $Path"
    return
}
catch [System.UnauthorizedAccessException] {
    Write-Error "Access denied: $Path"
    return
}
catch {
    Write-Error "Unexpected error: $_"
    throw
}
```

### Terminating vs Non-Terminating Errors
```powershell
# Terminating - stops execution
throw "Critical error occurred"
$PSCmdlet.ThrowTerminatingError($errorRecord)

# Non-terminating - continues execution
Write-Error "Problem with item: $item"
$PSCmdlet.WriteError($errorRecord)
```

### Feedback Methods
```powershell
# Warnings - potential unintended consequences
Write-Warning "File will be overwritten"

# Verbose - detailed operational info (requires -Verbose)
Write-Verbose "Processing file: $Path"

# Debug - troubleshooting info (requires -Debug)
Write-Debug "Variable state: $($var | ConvertTo-Json)"

# Progress - long-running operations
Write-Progress -Activity "Processing" -Status "Item $i of $total" -PercentComplete (($i / $total) * 100)
```

---

## Output Patterns

### Return Typed Objects
```powershell
# Create custom objects with type name
[PSCustomObject]@{
    PSTypeName = 'MyModule.ServerInfo'
    Name       = $server.Name
    Status     = $server.Status
    IPAddress  = $server.IP
}
```

### PassThru Pattern
```powershell
function Set-ItemProperty {
    [CmdletBinding()]
    param(
        [string]$Name,
        [string]$Value,
        [switch]$PassThru
    )

    # Modify the item
    $item.Property = $Value

    if ($PassThru) {
        Write-Output $item
    }
}
```

### ShouldProcess Pattern
```powershell
function Remove-Item {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param([string]$Path)

    if ($PSCmdlet.ShouldProcess($Path, 'Delete')) {
        # Perform deletion
    }
}
```

---

## Code Style

### Avoid Aliases in Scripts
```powershell
# Good
Get-ChildItem | Where-Object { $_.Length -gt 1MB } | ForEach-Object { $_.Name }

# Bad
gci | ? { $_.Length -gt 1MB } | % { $_.Name }
```

### Use Explicit Parameter Names
```powershell
# Good
Get-Process -Name 'notepad' -ComputerName 'Server01'

# Bad (positional)
Get-Process 'notepad' 'Server01'
```

### Splatting for Readability
```powershell
$params = @{
    Path        = $sourcePath
    Destination = $destPath
    Recurse     = $true
    Force       = $true
    ErrorAction = 'Stop'
}
Copy-Item @params
```

### Line Continuation
```powershell
# Good - natural breaks after operators
Get-Process |
    Where-Object { $_.CPU -gt 100 } |
    Sort-Object CPU -Descending |
    Select-Object -First 10

# Avoid backticks for continuation
```

### Comment-Based Help
```powershell
function Get-ServerStatus {
    <#
    .SYNOPSIS
        Gets the status of specified servers.

    .DESCRIPTION
        Retrieves operational status including CPU, memory,
        and network information from remote servers.

    .PARAMETER Name
        The server name(s) to query.

    .EXAMPLE
        Get-ServerStatus -Name 'Server01'

        Gets status for Server01.

    .EXAMPLE
        'Server01', 'Server02' | Get-ServerStatus

        Gets status for multiple servers via pipeline.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string[]]$Name
    )
    # Implementation
}
```
