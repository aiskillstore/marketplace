# Documentation Generator Subagent

## Agent Definition

**Agent Type**: `doc-generator`
**Base Agent**: `code-analyzer`
**Specialization**: Code analysis and comprehensive documentation generation
**Cognitive Pattern**: Analytical + Structured Output

## Purpose

The Documentation Generator agent specializes in analyzing codebases and producing comprehensive, standardized documentation including API specs, README files, inline comments, and architecture diagrams.

## Capabilities

1. **Code Analysis**
   - Parse source code using AST (Abstract Syntax Tree)
   - Extract functions, classes, types, and APIs
   - Identify documentation gaps and missing coverage
   - Detect code patterns and architectural structure

2. **API Documentation**
   - Generate OpenAPI 3.0 specifications
   - Create endpoint documentation with examples
   - Document request/response schemas
   - Generate authentication guides

3. **Inline Documentation**
   - Add JSDoc/TSDoc comments to functions
   - Generate Python docstrings (Google/NumPy style)
   - Add JavaDoc for Java code
   - Insert RustDoc for Rust code

4. **README Generation**
   - Create comprehensive project overviews
   - Generate installation instructions
   - Add usage examples and quickstart guides
   - Include badges and project metadata

5. **Diagram Generation**
   - Create system architecture diagrams (Graphviz)
   - Generate data flow diagrams (Mermaid)
   - Produce API structure visualizations
   - Create component relationship diagrams

## Invocation

### Via Claude Code Task Tool

```javascript
// Spawn documentation generator agent
Task(
  "Documentation Generator Agent",
  `Analyze the codebase at ${projectPath} and generate comprehensive documentation:

  1. Analyze project structure and extract all functions, classes, and APIs
  2. Generate OpenAPI 3.0 specification for REST endpoints
  3. Create comprehensive README.md with:
     - Project overview and features
     - Installation instructions
     - Quick start guide
     - API documentation links
  4. Add JSDoc comments to all undocumented public functions
  5. Generate system architecture diagram

  Documentation standards:
  - Comment style: JSDoc
  - API format: OpenAPI 3.0
  - Minimum coverage: 80%
  - Include usage examples for all public APIs

  Output to: docs/

  Use hooks for coordination:
  - Pre-task: Register with swarm
  - During: Store findings in memory
  - Post-task: Report completion metrics`,
  "code-analyzer"
);
```

### Via MCP Coordination

```javascript
// Initialize coordination
mcp__claude-flow__swarm_init({ topology: "mesh", maxAgents: 3 });

// Define agent type
mcp__claude-flow__agent_spawn({
  type: "analyst",
  capabilities: ["code-analysis", "documentation-generation"]
});

// Then use Claude Code Task tool to spawn actual working agent
Task("Doc Generator", "...", "code-analyzer");
```

## Agent Workflow

### Phase 1: Analysis

```javascript
// 1. Register with swarm
npx claude-flow@alpha hooks pre-task --description "Documentation generation for ${project}"

// 2. Restore session context
npx claude-flow@alpha hooks session-restore --session-id "doc-gen-${projectId}"

// 3. Scan project structure
const projectStructure = await analyzeProjectStructure(projectPath);

// 4. Extract documentation targets
const targets = await extractDocumentationTargets(projectStructure);

// 5. Analyze gaps
const gaps = analyzeDocumentationGaps(targets);

// 6. Store analysis in memory
npx claude-flow@alpha memory store \\
  --key "swarm/doc-generator/analysis" \\
  --value '${JSON.stringify(gaps)}'
```

### Phase 2: Generation

```javascript
// 1. Generate API documentation
const apiDocs = await generateAPIDocumentation(targets.routes);
await writeFile('docs/api.yml', apiDocs);

// Notify progress
npx claude-flow@alpha hooks notify --message "API documentation generated"

// 2. Generate README
const readme = await generateREADME(projectStructure);
await writeFile('README.md', readme);

// 3. Add inline comments
for (const file of targets.undocumentedFiles) {
  const commented = await addInlineComments(file);
  await writeFile(file.path, commented);

  // Store progress
  npx claude-flow@alpha hooks post-edit \\
    --file "${file.path}" \\
    --memory-key "swarm/doc-generator/progress"
}

// 4. Generate diagrams
const diagram = await generateArchitectureDiagram(projectStructure);
await writeFile('docs/diagrams/architecture.svg', diagram);
```

### Phase 3: Validation

```javascript
// 1. Validate coverage
const coverage = validateDocumentationCoverage(targets, generatedDocs);

if (coverage.overall < 80) {
  // Identify missing docs
  const missing = identifyMissingDocumentation(targets, generatedDocs);

  // Generate additional documentation
  await generateAdditionalDocs(missing);
}

// 2. Validate links
const brokenLinks = await validateLinks(generatedDocs);

if (brokenLinks.length > 0) {
  // Fix broken links
  await fixBrokenLinks(brokenLinks);
}

// 3. Check formatting
await formatDocumentation(generatedDocs);
```

### Phase 4: Completion

```javascript
// 1. Generate report
const report = {
  filesAnalyzed: targets.files.length,
  functionsDocumented: targets.functions.filter(f => f.documented).length,
  apiEndpoints: targets.routes.length,
  coveragePercent: coverage.overall,
  diagramsGenerated: 3,
  filesModified: modifiedFiles.length
};

// 2. Store report in memory
npx claude-flow@alpha memory store \\
  --key "swarm/doc-generator/report" \\
  --value '${JSON.stringify(report)}'

// 3. Post-task hook
npx claude-flow@alpha hooks post-task --task-id "doc-generation"

// 4. Export metrics
npx claude-flow@alpha hooks session-end --export-metrics true
```

## Output Structure

### Generated Files

```
project/
├── README.md                        # Generated/updated
├── docs/
│   ├── api.yml                      # OpenAPI specification
│   ├── API.md                       # Human-readable API docs
│   ├── ARCHITECTURE.md              # System architecture
│   └── diagrams/
│       ├── system-overview.svg      # System diagram
│       ├── data-flow.svg            # Data flow
│       └── api-structure.svg        # API structure
└── src/
    └── [source files]               # With added JSDoc comments
```

### Report Format

```json
{
  "timestamp": "2025-10-30T10:30:00Z",
  "project": "ecommerce-api",
  "analysis": {
    "filesAnalyzed": 247,
    "functionsFound": 342,
    "classesFound": 45,
    "apiEndpoints": 28
  },
  "documentation": {
    "functionsCovered": 302,
    "coveragePercent": 88.3,
    "apiDocumented": 28,
    "readmeGenerated": true,
    "diagramsGenerated": 3
  },
  "changes": {
    "filesModified": 89,
    "linesAdded": 3421,
    "commentsAdded": 267
  },
  "validation": {
    "coverageThreshold": 80,
    "coverageMet": true,
    "brokenLinks": 0,
    "spellingErrors": 0
  }
}
```

## Configuration

### Agent Configuration File

```yaml
# .claude/agents/doc-generator.yml
agent:
  name: doc-generator
  type: code-analyzer
  capabilities:
    - code-analysis
    - documentation-generation
    - diagram-generation

  settings:
    commentStyle: jsdoc           # jsdoc, tsdoc, google, numpy
    apiFormat: openapi3           # openapi3, swagger2, raml
    diagramFormat: svg            # svg, png, pdf
    minCoverage: 80               # Minimum coverage percentage
    includeExamples: true         # Add usage examples
    generateDiagrams: true        # Create diagrams

  languages:
    - javascript:
        parser: babel
        commentStyle: jsdoc
    - typescript:
        parser: typescript
        commentStyle: tsdoc
    - python:
        parser: ast
        commentStyle: google

  output:
    docsDir: docs/
    apiSpec: docs/api.yml
    readme: README.md
    diagramsDir: docs/diagrams/

  validation:
    checkCoverage: true
    validateLinks: true
    spellCheck: true
    formatCheck: true
```

## Integration with Swarm

### Memory Coordination

```javascript
// Store documentation strategy
await memory.store({
  key: 'swarm/doc-generator/strategy',
  value: {
    standards: 'jsdoc',
    coverage: 80,
    formats: ['openapi', 'markdown', 'svg']
  }
});

// Share with other agents
await memory.store({
  key: 'swarm/shared/documentation',
  value: {
    apiSpec: 'docs/api.yml',
    readme: 'README.md',
    lastUpdated: new Date().toISOString()
  }
});
```

### Coordination Hooks

```bash
# Pre-task: Register and prepare
npx claude-flow@alpha hooks pre-task \\
  --description "Documentation generation" \\
  --agent "doc-generator"

# During: Notify progress
npx claude-flow@alpha hooks notify \\
  --message "Generated API documentation" \\
  --agent "doc-generator"

# Post-edit: Track changes
npx claude-flow@alpha hooks post-edit \\
  --file "README.md" \\
  --memory-key "swarm/doc-generator/changes"

# Post-task: Report completion
npx claude-flow@alpha hooks post-task \\
  --task-id "doc-generation" \\
  --metrics '{"coverage": 88, "files": 89}'
```

## Usage Examples

### Example 1: Full Documentation Generation

```javascript
Task(
  "Complete Documentation",
  `Generate comprehensive documentation for the Express API project:

  Project path: /project/express-api
  Documentation standards: JSDoc + OpenAPI 3.0
  Target coverage: 90%

  Generate:
  1. OpenAPI specification (docs/api.yml)
  2. Comprehensive README.md
  3. JSDoc comments for all public functions
  4. System architecture diagram
  5. API endpoint documentation

  Validate:
  - Coverage >= 90%
  - All links valid
  - No spelling errors

  Output report to: docs/report.json`,
  "code-analyzer"
);
```

### Example 2: API Documentation Only

```javascript
Task(
  "API Documentation",
  `Generate OpenAPI 3.0 specification for REST API:

  Source: /project/src/routes/**/*.js
  Output: docs/api.yml

  Include:
  - All endpoint definitions
  - Request/response schemas
  - Authentication requirements
  - Example requests/responses
  - Error codes

  Format: OpenAPI 3.0 (YAML)`,
  "code-analyzer"
);
```

### Example 3: Inline Comments Only

```javascript
Task(
  "Add JSDoc Comments",
  `Add JSDoc comments to undocumented functions:

  Target files: src/**/*.js
  Comment style: JSDoc
  Include examples: true

  Requirements:
  - Document all parameters with types
  - Document return values
  - Add usage examples for complex functions
  - Document thrown errors

  Skip: Test files, config files`,
  "code-analyzer"
);
```

## Error Handling

```javascript
try {
  // Generate documentation
  await generateDocumentation(config);
} catch (error) {
  if (error.code === 'COVERAGE_TOO_LOW') {
    // Add more documentation
    const missing = identifyMissingDocs();
    await generateAdditionalDocs(missing);
  } else if (error.code === 'INVALID_SYNTAX') {
    // Log syntax errors
    console.error('Invalid syntax in:', error.file);
    // Continue with other files
  } else {
    // Store error in memory for debugging
    await memory.store({
      key: 'swarm/doc-generator/error',
      value: { error: error.message, stack: error.stack }
    });
    throw error;
  }
}
```

## Performance Optimization

```javascript
// Parallel processing for large codebases
const chunks = chunkFiles(targetFiles, 10);

await Promise.all(
  chunks.map(chunk =>
    Task(
      `Doc Generation Chunk ${chunk.id}`,
      `Generate documentation for files: ${chunk.files.join(', ')}`,
      "code-analyzer"
    )
  )
);

// Incremental updates (only changed files)
const changedFiles = await getChangedFiles();
await generateDocumentationIncremental(changedFiles);
```

## Metrics & Monitoring

```javascript
// Track agent performance
const metrics = {
  startTime: Date.now(),
  filesProcessed: 0,
  functionsDocumented: 0,
  diagramsGenerated: 0
};

// Update during execution
metrics.filesProcessed++;

// Report at completion
const duration = Date.now() - metrics.startTime;
console.log(`Documentation generated in ${duration}ms`);
console.log(`Files processed: ${metrics.filesProcessed}`);
console.log(`Functions documented: ${metrics.functionsDocumented}`);
```

---

**Agent Version**: 1.0.0
**Last Updated**: 2025-10-30
**Status**: Production Ready
