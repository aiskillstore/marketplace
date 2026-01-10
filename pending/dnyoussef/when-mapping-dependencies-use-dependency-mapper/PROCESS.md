# Dependency Mapper - Detailed Process Flow

## Overview

This document describes the complete step-by-step process for dependency mapping, analysis, and visualization.

## Process Architecture

### High-Level Flow
```
Input (Project Path)
  → Discovery Phase
    → Extraction Phase
      → Analysis Phase
        → Security Phase
          → Visualization Phase
            → Output (Reports + Visualizations)
```

## Phase 1: Discovery & Initialization

### Step 1.1: Project Detection
**Objective**: Identify project type and package manager

**Actions**:
1. Scan project directory for manifest files
2. Detect package manager type:
   - `package.json` + `package-lock.json` = npm
   - `package.json` + `yarn.lock` = yarn
   - `package.json` + `pnpm-lock.yaml` = pnpm
   - `requirements.txt` + `requirements.lock` = pip
   - `Cargo.toml` + `Cargo.lock` = cargo
   - `pom.xml` = maven
   - `go.mod` + `go.sum` = go modules
   - `Gemfile` + `Gemfile.lock` = bundler
   - `composer.json` + `composer.lock` = composer

**Output**: Project metadata object
```json
{
  "project_type": "node",
  "package_manager": "npm",
  "manager_version": "9.5.0",
  "manifest_path": "/path/to/package.json",
  "lockfile_path": "/path/to/package-lock.json",
  "has_dev_dependencies": true
}
```

### Step 1.2: Configuration Loading
**Objective**: Load user preferences and settings

**Actions**:
1. Check for `.dependency-mapper.json` in project root
2. Load default configuration
3. Merge user config with defaults
4. Validate configuration schema

**Output**: Configuration object

### Step 1.3: Dependency Check
**Objective**: Verify required tools are available

**Actions**:
1. Check package manager is installed
2. Verify graphviz available (for visualization)
3. Test internet connectivity (for security scans)
4. Initialize cache directory

**Output**: Environment readiness status

## Phase 2: Dependency Extraction

### Step 2.1: Parse Manifest File
**Objective**: Extract declared dependencies

**Actions**:
1. Read and parse manifest file (package.json, etc.)
2. Extract direct dependencies
3. Extract dev dependencies
4. Extract peer dependencies
5. Extract optional dependencies
6. Record version constraints

**Output**: Direct dependency list
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "^4.17.21",
    "axios": "^1.3.4"
  },
  "devDependencies": {
    "jest": "^29.5.0",
    "eslint": "^8.36.0"
  }
}
```

### Step 2.2: Parse Lock File
**Objective**: Extract resolved dependency tree

**Actions**:
1. Read and parse lock file
2. Extract all resolved versions
3. Build package resolution map
4. Identify transitive dependencies
5. Map package locations

**Output**: Complete dependency resolution map

### Step 2.3: Build Dependency Tree
**Objective**: Construct hierarchical dependency structure

**Actions**:
1. Create root node for project
2. Add direct dependencies as children
3. Recursively add transitive dependencies
4. Calculate dependency depth
5. Track dependency paths

**Output**: Dependency tree data structure
```javascript
{
  name: "my-app",
  version: "1.0.0",
  dependencies: [
    {
      name: "express",
      version: "4.18.2",
      depth: 1,
      dependencies: [
        {
          name: "body-parser",
          version: "1.20.1",
          depth: 2,
          dependencies: [...]
        }
      ]
    }
  ]
}
```

## Phase 3: Dependency Analysis

### Step 3.1: Circular Dependency Detection
**Objective**: Identify circular dependency paths

**Algorithm**: Depth-First Search with cycle detection

**Actions**:
1. Initialize visited set and recursion stack
2. Traverse dependency tree depth-first
3. Track current path in recursion stack
4. When revisiting node in current path, record cycle
5. Collect all circular paths

**Output**: List of circular dependency chains
```json
{
  "circular_dependencies": [
    {
      "path": ["package-a", "package-b", "package-c", "package-a"],
      "length": 3,
      "severity": "warning"
    }
  ]
}
```

### Step 3.2: Duplicate Dependency Detection
**Objective**: Find multiple versions of same package

**Actions**:
1. Group dependencies by package name
2. Identify packages with multiple versions
3. Calculate total duplication size
4. Suggest consolidation opportunities

**Output**: Duplicate dependency report

### Step 3.3: Depth Analysis
**Objective**: Analyze dependency tree depth

**Actions**:
1. Calculate maximum depth
2. Identify deeply nested dependencies
3. Flag potential issues (depth > 10)
4. Suggest flattening opportunities

**Output**: Depth statistics

### Step 3.4: Outdated Package Detection
**Objective**: Identify packages with available updates

**Actions**:
1. Query package registry for latest versions
2. Compare current vs available versions
3. Categorize updates (major, minor, patch)
4. Check breaking change risk

**Output**: Outdated package list
```json
{
  "outdated_packages": [
    {
      "name": "lodash",
      "current": "4.17.21",
      "latest": "4.18.0",
      "update_type": "minor",
      "breaking_changes": false
    }
  ]
}
```

## Phase 4: Security Analysis

### Step 4.1: Vulnerability Database Query
**Objective**: Check for known security vulnerabilities

**Data Sources**:
- npm audit
- Snyk vulnerability database
- GitHub Security Advisories
- CVE databases
- OSV (Open Source Vulnerabilities)

**Actions**:
1. Build list of all packages with versions
2. Query vulnerability databases
3. Match vulnerabilities to installed packages
4. Assess severity levels (critical, high, medium, low)
5. Check if fixes available

**Output**: Vulnerability report
```json
{
  "vulnerabilities": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 12,
    "details": [
      {
        "package": "lodash",
        "version": "4.17.20",
        "vulnerability": "Prototype Pollution",
        "severity": "high",
        "cvss_score": 7.4,
        "cve_id": "CVE-2021-23337",
        "fixed_in": "4.17.21",
        "patched_versions": ">=4.17.21"
      }
    ]
  }
}
```

### Step 4.2: License Compliance Check
**Objective**: Verify license compatibility

**Actions**:
1. Extract license information from each package
2. Identify license types (MIT, Apache, GPL, etc.)
3. Check for incompatible licenses
4. Flag viral licenses (GPL, AGPL)
5. Identify unlicensed packages

**Output**: License compliance report

### Step 4.3: Supply Chain Risk Assessment
**Objective**: Evaluate dependency trust levels

**Risk Factors**:
- Package age and maintenance status
- Number of maintainers
- Download statistics
- GitHub stars/forks
- Recent commit activity
- Known security history

**Output**: Risk assessment scores

## Phase 5: Visualization Generation

### Step 5.1: Graph Data Preparation
**Objective**: Convert dependency tree to graph format

**Actions**:
1. Create nodes for each unique package
2. Create edges for each dependency relationship
3. Add metadata (version, severity, outdated status)
4. Assign colors based on status:
   - Green: Up-to-date, no issues
   - Yellow: Outdated
   - Orange: Medium vulnerabilities
   - Red: High/critical vulnerabilities
   - Purple: Circular dependencies

**Output**: Graph data structure

### Step 5.2: HTML Visualization
**Objective**: Generate interactive web-based graph

**Technology**: D3.js force-directed graph

**Features**:
- Zoomable and pannable canvas
- Click nodes to expand/collapse
- Hover for package details
- Search and filter capabilities
- Export to PNG/SVG
- Highlight vulnerability paths
- Show circular dependency loops

**Actions**:
1. Generate HTML template
2. Embed graph data as JSON
3. Include D3.js visualization code
4. Add interactive controls
5. Apply styling and theming

**Output**: `dependency-graph.html`

### Step 5.3: GraphViz Diagram
**Objective**: Generate static SVG/PNG diagram

**Actions**:
1. Convert graph to DOT format
2. Run graphviz layout engine
3. Apply styling (colors, shapes, labels)
4. Export to SVG/PNG

**Output**: `dependency-graph.svg` or `.png`

### Step 5.4: ASCII Tree
**Objective**: Generate terminal-friendly tree view

**Actions**:
1. Traverse dependency tree
2. Format with ASCII box-drawing characters
3. Add color coding (if terminal supports)
4. Truncate for large trees

**Output**: ASCII tree visualization
```
my-app@1.0.0
├─ express@4.18.2
│  ├─ body-parser@1.20.1
│  │  ├─ bytes@3.1.2
│  │  └─ http-errors@2.0.0
│  ├─ cookie@0.5.0
│  └─ merge-descriptors@1.0.1
├─ lodash@4.17.21 ⚠️  (vulnerable)
└─ axios@1.3.4
   └─ follow-redirects@1.15.2
```

## Phase 6: Report Generation

### Step 6.1: Summary Statistics
**Objective**: Calculate key metrics

**Metrics**:
- Total dependency count
- Direct vs transitive ratio
- Average depth
- Largest dependencies
- Most used packages
- Vulnerability distribution
- Outdated package percentage

### Step 6.2: Recommendations
**Objective**: Generate actionable improvement suggestions

**Categories**:
1. Security fixes (prioritized by severity)
2. Outdated package updates
3. Circular dependency resolutions
4. Duplicate dependency consolidations
5. Unnecessary dependency removals
6. Alternative lighter packages

**Output**: Prioritized recommendation list

### Step 6.3: Report Assembly
**Objective**: Combine all analysis into final report

**Formats**:
- **JSON**: Complete structured data
- **Markdown**: Human-readable report
- **HTML**: Web-based interactive report
- **CSV**: Tabular data for spreadsheets
- **PDF**: Formatted printable report

## Phase 7: Output & Caching

### Step 7.1: File Output
**Objective**: Write results to files

**Actions**:
1. Create output directory
2. Write JSON report
3. Write HTML visualization
4. Write SVG diagram
5. Write recommendations file

### Step 7.2: Cache Results
**Objective**: Store results for future use

**Actions**:
1. Generate cache key (project path + timestamp)
2. Store analysis results
3. Set TTL (default 1 hour)
4. Clean old cache entries

### Step 7.3: Console Output
**Objective**: Display summary to user

**Actions**:
1. Format summary statistics
2. Highlight critical issues
3. Display recommendations
4. Show file output locations

## Error Handling

### Common Errors:

1. **Lock file not found**
   - Fallback: Use manifest file only
   - Warning: Results may be incomplete

2. **Package manager not installed**
   - Error: Cannot proceed
   - Suggestion: Install required package manager

3. **Network timeout (security scan)**
   - Fallback: Use cached vulnerability data
   - Warning: Results may be outdated

4. **Invalid manifest file**
   - Error: Cannot parse
   - Suggestion: Check file syntax

5. **Circular dependency infinite loop**
   - Protection: Max recursion depth limit
   - Warning: Tree may be incomplete

## Performance Optimizations

1. **Parallel Processing**:
   - Extract dependencies in parallel
   - Query security databases concurrently
   - Generate visualizations asynchronously

2. **Caching**:
   - Cache package metadata
   - Cache vulnerability database queries
   - Cache generated visualizations

3. **Lazy Loading**:
   - Only expand tree nodes on demand
   - Defer visualization generation
   - Stream large reports

4. **Incremental Analysis**:
   - Detect changed dependencies
   - Only re-analyze affected subtrees
   - Merge with cached results

## Integration Points

### Claude-Flow Coordination:
```bash
# Pre-task hook
npx claude-flow@alpha hooks pre-task --description "Dependency mapping for my-app"

# Post-task hook
npx claude-flow@alpha hooks post-task --task-id "dep-map-001"

# Memory storage
npx claude-flow@alpha hooks post-edit --file "dependency-report.json" --memory-key "swarm/dependency-mapper/report"
```

### CI/CD Integration:
- Exit code 0: No critical issues
- Exit code 1: Critical vulnerabilities found
- Exit code 2: Analysis failed

### Git Hooks:
- Pre-commit: Quick circular dependency check
- Pre-push: Full security audit

## See Also

- SKILL.md - Complete skill documentation
- README.md - Quick start guide
- subagent-dependency-mapper.md - Agent implementation
- process-diagram.gv - Visual process flow diagram
