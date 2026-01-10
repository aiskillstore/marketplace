# Velociraptor Artifact Development Guide

Guide to creating custom VQL artifacts for specific investigation and threat hunting scenarios.

## Table of Contents
- [Artifact Structure](#artifact-structure)
- [Parameter Types](#parameter-types)
- [Source Types](#source-types)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Testing Artifacts](#testing-artifacts)

## Artifact Structure

Velociraptor artifacts are YAML files with a defined structure:

```yaml
name: Category.Subcategory.ArtifactName
description: |
  Detailed description of what this artifact collects and why.
  Include use cases and expected output.

author: Your Name <email@domain.com>

type: CLIENT  # CLIENT, SERVER, or CLIENT_EVENT

parameters:
  - name: ParameterName
    default: "default_value"
    type: string
    description: Parameter description

precondition: |
  SELECT OS FROM info() WHERE OS = 'windows'

sources:
  - name: SourceName
    query: |
      SELECT * FROM plugin()
      WHERE condition

reports:
  - type: CLIENT
    template: |
      # Report Title
      {{ .Description }}

      {{ range .Rows }}
      - {{ .Column }}
      {{ end }}
```

### Required Fields

- **name**: Unique artifact identifier in dot notation
- **description**: What the artifact does and when to use it
- **sources**: At least one VQL query source

### Optional Fields

- **author**: Creator information
- **type**: Artifact type (CLIENT, SERVER, CLIENT_EVENT)
- **parameters**: User-configurable inputs
- **precondition**: Check before running (OS, software presence)
- **reports**: Output formatting templates
- **references**: External documentation links

## Parameter Types

### String Parameters

```yaml
parameters:
  - name: SearchPath
    default: "C:/Windows/System32/"
    type: string
    description: Directory path to search
```

### Integer Parameters

```yaml
parameters:
  - name: DaysBack
    default: 7
    type: int
    description: Number of days to look back
```

### Boolean Parameters

```yaml
parameters:
  - name: IncludeSystem
    default: Y
    type: bool
    description: Include system files
```

### Regex Parameters

```yaml
parameters:
  - name: ProcessPattern
    default: "(?i)(powershell|cmd)"
    type: regex
    description: Process name pattern to match
```

### Choice Parameters

```yaml
parameters:
  - name: LogLevel
    default: "INFO"
    type: choices
    choices:
      - DEBUG
      - INFO
      - WARNING
      - ERROR
    description: Logging verbosity
```

### CSV Parameters

```yaml
parameters:
  - name: IOCList
    default: |
      evil.com
      malicious.net
    type: csv
    description: List of IOC domains
```

## Source Types

### Query Sources

Standard VQL query that collects data:

```yaml
sources:
  - name: ProcessCollection
    query: |
      SELECT Pid, Name, CommandLine, Username
      FROM pslist()
      WHERE Name =~ ProcessPattern
```

### Event Sources

Continuous monitoring queries for CLIENT_EVENT artifacts:

```yaml
sources:
  - name: ProcessCreation
    query: |
      SELECT * FROM watch_evtx(
        filename="C:/Windows/System32/winevt/Logs/Security.evtx"
      )
      WHERE System.EventID.Value = 4688
```

### Multiple Sources

Artifacts can have multiple sources for different data collection:

```yaml
sources:
  - name: Processes
    query: |
      SELECT * FROM pslist()

  - name: NetworkConnections
    query: |
      SELECT * FROM netstat()

  - name: LoadedDLLs
    query: |
      SELECT * FROM modules()
```

## Best Practices

### 1. Use Preconditions

Prevent artifact execution on incompatible systems:

```yaml
# Windows-only artifact
precondition: |
  SELECT OS FROM info() WHERE OS = 'windows'

# Requires specific tool
precondition: |
  SELECT * FROM stat(filename="C:/Tools/sysinternals/psexec.exe")

# Version check
precondition: |
  SELECT * FROM info() WHERE OS = 'windows' AND OSVersion =~ '10'
```

### 2. Parameterize Paths and Patterns

Make artifacts flexible and reusable:

```yaml
parameters:
  - name: TargetPath
    default: "C:/Users/**/AppData/**"
    type: string

  - name: FilePattern
    default: "*.exe"
    type: string

sources:
  - query: |
      SELECT * FROM glob(globs=TargetPath + "/" + FilePattern)
```

### 3. Use LET for Query Composition

Break complex queries into manageable parts:

```yaml
sources:
  - query: |
      -- Define reusable subqueries
      LET SuspiciousProcesses = SELECT Pid, Name, CommandLine
      FROM pslist()
      WHERE CommandLine =~ "(?i)(bypass|hidden)"

      LET NetworkConnections = SELECT Pid, Raddr.IP AS RemoteIP
      FROM netstat()
      WHERE Status = "ESTABLISHED"

      -- Join and correlate
      SELECT sp.Name,
             sp.CommandLine,
             nc.RemoteIP
      FROM SuspiciousProcesses sp
      JOIN NetworkConnections nc ON sp.Pid = nc.Pid
```

### 4. Add Error Handling

Handle missing data gracefully:

```yaml
sources:
  - query: |
      SELECT * FROM foreach(
        row={
          SELECT FullPath FROM glob(globs=SearchPath)
        },
        query={
          SELECT FullPath,
                 hash(path=FullPath, accessor="file").SHA256 AS SHA256
          FROM scope()
          WHERE log(message="Processing: " + FullPath)
        },
        workers=5
      )
      WHERE SHA256  -- Filter out hash failures
```

### 5. Include Documentation

Add inline comments and comprehensive descriptions:

```yaml
description: |
  ## Overview
  This artifact hunts for suspicious scheduled tasks.

  ## Use Cases
  - Persistence mechanism detection
  - Lateral movement artifact collection
  - Threat hunting campaigns

  ## Output
  Returns task name, actions, triggers, and creation time.

  ## References
  - MITRE ATT&CK T1053.005 (Scheduled Task/Job)
```

## Common Patterns

### Pattern: File Collection with Hashing

```yaml
name: Custom.Windows.FileCollection
description: Collect files matching patterns with hashes

parameters:
  - name: GlobPatterns
    default: |
      C:/Users/**/AppData/**/*.exe
      C:/Windows/Temp/**/*.dll
    type: csv

sources:
  - query: |
      SELECT FullPath,
             Size,
             timestamp(epoch=Mtime) AS Modified,
             timestamp(epoch=Btime) AS Created,
             hash(path=FullPath, accessor="file") AS Hashes
      FROM foreach(
        row={
          SELECT * FROM parse_csv(filename=GlobPatterns, accessor="data")
        },
        query={
          SELECT * FROM glob(globs=_value)
        }
      )
      WHERE NOT IsDir
```

### Pattern: Event Log Analysis

```yaml
name: Custom.Windows.EventLogHunt
description: Hunt for specific event IDs with context

parameters:
  - name: LogFile
    default: "C:/Windows/System32/winevt/Logs/Security.evtx"
    type: string

  - name: EventIDs
    default: "4624,4625,4672"
    type: csv

sources:
  - query: |
      LET EventIDList = SELECT parse_string_with_regex(
        string=EventIDs,
        regex="(\\d+)"
      ).g1 AS EventID FROM scope()

      SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS EventTime,
             System.EventID.Value AS EventID,
             System.Computer AS Computer,
             EventData
      FROM parse_evtx(filename=LogFile)
      WHERE str(str=System.EventID.Value) IN EventIDList.EventID
      ORDER BY EventTime DESC
```

### Pattern: Process Tree Analysis

```yaml
name: Custom.Windows.ProcessTree
description: Build process tree from a starting PID

parameters:
  - name: RootPID
    default: 0
    type: int
    description: Starting process PID (0 for all)

sources:
  - query: |
      LET ProcessList = SELECT Pid, Ppid, Name, CommandLine, Username, CreateTime
      FROM pslist()

      LET RECURSIVE GetChildren(ParentPID) = SELECT *
      FROM ProcessList
      WHERE Ppid = ParentPID

      LET RECURSIVE BuildTree(Level, ParentPID) = SELECT
        Level,
        Pid,
        Ppid,
        Name,
        CommandLine,
        Username,
        CreateTime
      FROM GetChildren(ParentPID=ParentPID)
      UNION ALL
      SELECT * FROM BuildTree(Level=Level+1, ParentPID=Pid)

      SELECT * FROM if(
        condition=RootPID > 0,
        then={
          SELECT * FROM BuildTree(Level=0, ParentPID=RootPID)
        },
        else={
          SELECT 0 AS Level, * FROM ProcessList
        }
      )
      ORDER BY CreateTime
```

### Pattern: Network IOC Matching

```yaml
name: Custom.Windows.NetworkIOCMatch
description: Match network connections against IOC list

parameters:
  - name: IOCList
    default: |
      IP,Description
      192.0.2.1,C2 Server
      198.51.100.50,Malicious Host
    type: csv

sources:
  - query: |
      LET IOCs = SELECT IP, Description
      FROM parse_csv(filename=IOCList, accessor="data")

      LET Connections = SELECT
        Raddr.IP AS RemoteIP,
        Raddr.Port AS RemotePort,
        Pid,
        process_tracker_get(id=Pid).Name AS ProcessName,
        process_tracker_get(id=Pid).CommandLine AS CommandLine
      FROM netstat()
      WHERE Status = "ESTABLISHED"

      SELECT c.RemoteIP,
             c.RemotePort,
             c.ProcessName,
             c.CommandLine,
             i.Description AS IOCMatch
      FROM Connections c
      JOIN IOCs i ON c.RemoteIP = i.IP
```

### Pattern: Registry Timeline

```yaml
name: Custom.Windows.RegistryTimeline
description: Timeline registry modifications in specific keys

parameters:
  - name: RegistryPaths
    default: |
      HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows/CurrentVersion/Run/**
      HKEY_CURRENT_USER/SOFTWARE/Microsoft/Windows/CurrentVersion/Run/**
    type: csv

  - name: DaysBack
    default: 7
    type: int

sources:
  - query: |
      LET StartTime = timestamp(epoch=now() - DaysBack * 86400)

      SELECT timestamp(epoch=Key.Mtime) AS Modified,
             Key.FullPath AS RegistryPath,
             ValueName,
             ValueData.value AS Value
      FROM foreach(
        row={
          SELECT * FROM parse_csv(filename=RegistryPaths, accessor="data")
        },
        query={
          SELECT * FROM read_reg_key(globs=_value)
        }
      )
      WHERE Key.Mtime > StartTime
      ORDER BY Modified DESC
```

## Testing Artifacts

### 1. Local Testing with GUI

```bash
# Start Velociraptor in GUI mode
velociraptor gui

# Navigate to: View Artifacts → Add Artifact
# Paste your artifact YAML and click Save
# Run artifact via Collected Artifacts → New Collection
```

### 2. Command Line Testing

```bash
# Test artifact syntax
velociraptor artifacts show Custom.Artifact.Name

# Run artifact locally
velociraptor artifacts collect Custom.Artifact.Name \
  --args ParameterName=value \
  --format json

# Run with output file
velociraptor artifacts collect Custom.Artifact.Name \
  --output results.json
```

### 3. Notebook Testing

Use VQL notebooks for interactive development:

```sql
-- Test query components in isolation
SELECT * FROM pslist() WHERE Name =~ "powershell" LIMIT 10

-- Test parameter substitution
LET ProcessPattern = "(?i)(powershell|cmd)"
SELECT * FROM pslist() WHERE Name =~ ProcessPattern

-- Test full artifact query
/* Paste your artifact query here */
```

### 4. Validation Checklist

Before deploying artifacts:

- [ ] Artifact name follows convention: Category.Subcategory.Name
- [ ] Description includes use cases and expected output
- [ ] Parameters have sensible defaults
- [ ] Precondition prevents incompatible execution
- [ ] Query tested in notebook mode
- [ ] Error handling for missing data
- [ ] Performance acceptable on test system
- [ ] Output format is useful and parseable
- [ ] Documentation includes MITRE ATT&CK mapping if applicable

## Performance Considerations

### Limit Scope

```yaml
# BAD: Scans entire filesystem
SELECT * FROM glob(globs="C:/**/*.exe")

# GOOD: Targeted scope
SELECT * FROM glob(globs=[
  "C:/Users/**/AppData/**/*.exe",
  "C:/Windows/Temp/**/*.exe"
])
```

### Use Workers for Parallel Processing

```yaml
sources:
  - query: |
      SELECT * FROM foreach(
        row={SELECT * FROM glob(globs=SearchPath)},
        query={
          SELECT FullPath,
                 hash(path=FullPath, accessor="file").SHA256 AS SHA256
          FROM scope()
        },
        workers=10  -- Process 10 files concurrently
      )
```

### Rate Limiting

```yaml
sources:
  - query: |
      SELECT * FROM foreach(
        row={SELECT * FROM glob(globs="C:/**")},
        query={
          SELECT * FROM scope()
          WHERE rate(query_name="my_query", ops_per_sec=100)
        }
      )
```

## MITRE ATT&CK Mapping

Map artifacts to MITRE ATT&CK techniques:

```yaml
name: Custom.Windows.PersistenceHunt
description: |
  Hunt for persistence mechanisms.

  MITRE ATT&CK Techniques:
  - T1547.001: Registry Run Keys / Startup Folder
  - T1053.005: Scheduled Task/Job
  - T1543.003: Windows Service
  - T1546.003: Windows Management Instrumentation Event Subscription

references:
  - https://attack.mitre.org/techniques/T1547/001/
  - https://attack.mitre.org/techniques/T1053/005/
```

## Artifact Distribution

### Export Artifacts

```bash
# Export single artifact
velociraptor artifacts show Custom.Artifact.Name > artifact.yaml

# Export all custom artifacts
velociraptor artifacts list --filter Custom > all_artifacts.yaml
```

### Import Artifacts

```bash
# Via command line
velociraptor --config server.config.yaml artifacts import artifact.yaml

# Via GUI
# Navigate to: View Artifacts → Upload Artifact Pack
```

### Share via Artifact Exchange

Contribute artifacts to the community:

1. Test thoroughly across different systems
2. Document clearly with examples
3. Add MITRE ATT&CK mappings
4. Submit to: https://docs.velociraptor.app/exchange/
