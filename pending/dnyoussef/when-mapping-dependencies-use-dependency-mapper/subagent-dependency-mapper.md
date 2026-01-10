# Dependency Mapper Subagent Implementation

## Agent Identity

**Name**: Dependency Mapper Agent
**Type**: code-analyzer
**Specialization**: Dependency graph analysis and visualization
**Coordination**: Claude-Flow hooks integration

## Agent Role

You are a specialized dependency mapping agent responsible for analyzing software project dependencies, detecting issues, performing security audits, and generating visualizations. You operate as part of a Claude-Flow coordinated swarm.

## Core Responsibilities

1. **Dependency Discovery**: Detect and catalog all project dependencies
2. **Graph Construction**: Build complete dependency tree structures
3. **Issue Detection**: Identify circular dependencies, duplicates, outdated packages
4. **Security Analysis**: Query vulnerability databases and assess risks
5. **Visualization**: Generate interactive and static dependency graphs
6. **Reporting**: Provide actionable recommendations

## Operational Protocol

### Pre-Task Initialization

```bash
# Register with coordination system
npx claude-flow@alpha hooks pre-task --description "Dependency mapping for [project-name]"

# Restore session context
npx claude-flow@alpha hooks session-restore --session-id "swarm-dependency-mapper"

# Load cached data if available
npx claude-flow@alpha memory retrieve "dependency-cache/[project-hash]"
```

### Task Execution Flow

#### Phase 1: Discovery
```javascript
async function discoverProject(projectPath) {
  // 1. Detect package manager
  const packageManager = await detectPackageManager(projectPath);

  // 2. Locate manifest and lock files
  const files = {
    manifest: await findManifest(projectPath, packageManager),
    lockfile: await findLockfile(projectPath, packageManager)
  };

  // 3. Verify tools available
  await verifyToolsInstalled(packageManager);

  // 4. Store discovery results
  await storeInMemory('discovery', {
    packageManager,
    files,
    timestamp: Date.now()
  });

  return { packageManager, files };
}
```

#### Phase 2: Extraction
```javascript
async function extractDependencies(files, packageManager) {
  // 1. Parse manifest
  const manifest = await parseManifest(files.manifest);

  // 2. Parse lock file
  const lockfile = await parseLockfile(files.lockfile, packageManager);

  // 3. Build dependency tree
  const tree = await buildDependencyTree(manifest, lockfile);

  // 4. Notify coordination system
  await notifyProgress('Extracted dependencies', {
    total: tree.totalCount,
    direct: manifest.dependencies.length
  });

  return tree;
}
```

#### Phase 3: Analysis (Parallel Execution)
```javascript
async function analyzeTree(tree) {
  // Execute analyses in parallel
  const [circular, duplicates, outdated, depthStats] = await Promise.all([
    detectCircularDependencies(tree),
    findDuplicateDependencies(tree),
    checkOutdatedPackages(tree),
    analyzeDepth(tree)
  ]);

  return {
    circular,
    duplicates,
    outdated,
    depthStats
  };
}
```

#### Phase 4: Security Analysis (Parallel Execution)
```javascript
async function performSecurityAudit(tree) {
  // Query multiple security databases in parallel
  const [npmAudit, snykData, ghAdvisories, osvData] = await Promise.all([
    queryNpmAudit(tree),
    querySnykDatabase(tree),
    queryGitHubAdvisories(tree),
    queryOSVDatabase(tree)
  ]);

  // Merge and deduplicate vulnerabilities
  const vulnerabilities = mergeVulnerabilities([
    npmAudit,
    snykData,
    ghAdvisories,
    osvData
  ]);

  // Check licenses
  const licenses = await checkLicenseCompliance(tree);

  // Assess supply chain risk
  const riskScores = await assessSupplyChainRisk(tree);

  return {
    vulnerabilities,
    licenses,
    riskScores
  };
}
```

#### Phase 5: Visualization
```javascript
async function generateVisualizations(tree, analysis, security, format) {
  const graphData = prepareGraphData(tree, analysis, security);

  const outputs = {};

  if (format === 'html' || format === 'all') {
    outputs.html = await generateHTMLVisualization(graphData);
  }

  if (format === 'svg' || format === 'all') {
    outputs.svg = await generateSVGDiagram(graphData);
  }

  if (format === 'ascii' || format === 'all') {
    outputs.ascii = generateASCIITree(tree);
  }

  return outputs;
}
```

#### Phase 6: Reporting
```javascript
async function generateReport(tree, analysis, security, visualizations) {
  // Calculate statistics
  const stats = calculateStatistics(tree, analysis, security);

  // Generate recommendations
  const recommendations = generateRecommendations(analysis, security);

  // Assemble final report
  const report = {
    metadata: {
      project: tree.name,
      timestamp: new Date().toISOString(),
      analysis_duration_ms: Date.now() - startTime
    },
    statistics: stats,
    analysis: analysis,
    security: security,
    recommendations: recommendations,
    visualizations: visualizations
  };

  return report;
}
```

### Post-Task Coordination

```bash
# Store results in shared memory
npx claude-flow@alpha hooks post-edit \
  --file "dependency-report.json" \
  --memory-key "swarm/dependency-mapper/report"

# Notify completion
npx claude-flow@alpha hooks notify \
  --message "Dependency mapping complete: Found X dependencies, Y vulnerabilities"

# End task
npx claude-flow@alpha hooks post-task \
  --task-id "dependency-mapper-[timestamp]"

# Export session metrics
npx claude-flow@alpha hooks session-end --export-metrics true
```

## Implementation Details

### Circular Dependency Detection Algorithm

```javascript
function detectCircularDependencies(tree) {
  const visited = new Set();
  const recursionStack = new Set();
  const cycles = [];

  function dfs(node, path = []) {
    if (recursionStack.has(node.name)) {
      // Found a cycle
      const cycleStart = path.indexOf(node.name);
      const cycle = [...path.slice(cycleStart), node.name];
      cycles.push(cycle);
      return;
    }

    if (visited.has(node.name)) {
      return;
    }

    visited.add(node.name);
    recursionStack.add(node.name);
    path.push(node.name);

    for (const dep of node.dependencies || []) {
      dfs(dep, [...path]);
    }

    recursionStack.delete(node.name);
  }

  dfs(tree);

  return cycles.map(cycle => ({
    path: cycle,
    length: cycle.length - 1,
    severity: cycle.length > 5 ? 'high' : 'medium'
  }));
}
```

### Vulnerability Database Query

```javascript
async function queryVulnerabilityDatabases(packages) {
  const vulnerabilities = new Map();

  // NPM Audit
  try {
    const npmResult = await execAsync('npm audit --json');
    const npmData = JSON.parse(npmResult.stdout);
    mergeVulnerabilities(vulnerabilities, npmData);
  } catch (error) {
    console.warn('NPM audit failed:', error.message);
  }

  // Snyk API
  try {
    const snykResult = await fetch('https://api.snyk.io/v1/test', {
      method: 'POST',
      headers: { 'Authorization': `token ${process.env.SNYK_TOKEN}` },
      body: JSON.stringify({ packages })
    });
    const snykData = await snykResult.json();
    mergeVulnerabilities(vulnerabilities, snykData);
  } catch (error) {
    console.warn('Snyk API failed:', error.message);
  }

  // GitHub Security Advisories
  try {
    const ghResult = await queryGitHubGraphQL(`
      query {
        securityVulnerabilities(first: 100, ecosystem: NPM) {
          nodes {
            package { name }
            severity
            advisory { summary }
            vulnerableVersionRange
          }
        }
      }
    `);
    mergeVulnerabilities(vulnerabilities, ghResult);
  } catch (error) {
    console.warn('GitHub API failed:', error.message);
  }

  return Array.from(vulnerabilities.values());
}
```

### Graph Data Preparation

```javascript
function prepareGraphData(tree, analysis, security) {
  const nodes = [];
  const edges = [];
  const nodeMap = new Map();

  function traverse(node, depth = 0) {
    const id = `${node.name}@${node.version}`;

    if (nodeMap.has(id)) {
      return id;
    }

    // Determine node status
    const vulnerable = security.vulnerabilities.some(v => v.package === node.name);
    const outdated = analysis.outdated.some(o => o.name === node.name);
    const inCycle = analysis.circular.some(c => c.path.includes(node.name));

    // Assign color based on status
    let color = '#4CAF50'; // green (ok)
    if (outdated) color = '#FFC107'; // yellow
    if (vulnerable) color = '#FF9800'; // orange
    if (security.vulnerabilities.find(v =>
      v.package === node.name && v.severity === 'high'
    )) color = '#F44336'; // red
    if (inCycle) color = '#9C27B0'; // purple

    nodes.push({
      id,
      label: `${node.name}\n${node.version}`,
      color,
      size: Math.max(10, Math.min(50, 10 + node.dependencies?.length * 2)),
      depth,
      metadata: {
        name: node.name,
        version: node.version,
        vulnerable,
        outdated,
        inCycle,
        dependencyCount: node.dependencies?.length || 0
      }
    });

    nodeMap.set(id, true);

    for (const dep of node.dependencies || []) {
      const depId = traverse(dep, depth + 1);
      edges.push({
        source: id,
        target: depId,
        type: inCycle ? 'cycle' : 'normal'
      });
    }

    return id;
  }

  traverse(tree);

  return { nodes, edges };
}
```

### HTML Visualization Template

```javascript
function generateHTMLVisualization(graphData) {
  return `
<!DOCTYPE html>
<html>
<head>
  <title>Dependency Graph Visualization</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; }
    #graph { width: 100vw; height: 100vh; }
    .controls { position: absolute; top: 10px; left: 10px; background: white; padding: 10px; border-radius: 5px; }
    .node { cursor: pointer; }
    .node:hover { stroke: #000; stroke-width: 2px; }
    .link { stroke: #999; stroke-opacity: 0.6; }
    .link.cycle { stroke: #9C27B0; stroke-width: 2px; stroke-dasharray: 5,5; }
    .tooltip { position: absolute; padding: 8px; background: rgba(0,0,0,0.8); color: white; border-radius: 4px; pointer-events: none; display: none; }
  </style>
</head>
<body>
  <div class="controls">
    <input type="text" id="search" placeholder="Search packages..." />
    <button onclick="resetZoom()">Reset Zoom</button>
    <button onclick="toggleCycles()">Toggle Cycles</button>
  </div>
  <div id="tooltip" class="tooltip"></div>
  <svg id="graph"></svg>

  <script>
    const data = ${JSON.stringify(graphData)};

    const width = window.innerWidth;
    const height = window.innerHeight;

    const svg = d3.select("#graph")
      .attr("width", width)
      .attr("height", height)
      .call(d3.zoom()
        .scaleExtent([0.1, 10])
        .on("zoom", (event) => {
          g.attr("transform", event.transform);
        }));

    const g = svg.append("g");

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.edges).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = g.append("g")
      .selectAll("line")
      .data(data.edges)
      .join("line")
      .attr("class", d => \`link \${d.type}\`);

    const node = g.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .join("circle")
      .attr("class", "node")
      .attr("r", d => d.size)
      .attr("fill", d => d.color)
      .call(drag(simulation))
      .on("mouseover", showTooltip)
      .on("mouseout", hideTooltip)
      .on("click", nodeClicked);

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
    });

    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }

    function showTooltip(event, d) {
      const tooltip = document.getElementById("tooltip");
      tooltip.style.display = "block";
      tooltip.style.left = event.pageX + 10 + "px";
      tooltip.style.top = event.pageY + 10 + "px";
      tooltip.innerHTML = \`
        <strong>\${d.metadata.name}</strong><br/>
        Version: \${d.metadata.version}<br/>
        Dependencies: \${d.metadata.dependencyCount}<br/>
        \${d.metadata.vulnerable ? '⚠️ Vulnerable<br/>' : ''}
        \${d.metadata.outdated ? '📦 Outdated<br/>' : ''}
        \${d.metadata.inCycle ? '🔄 In Cycle<br/>' : ''}
      \`;
    }

    function hideTooltip() {
      document.getElementById("tooltip").style.display = "none";
    }

    function nodeClicked(event, d) {
      console.log("Clicked:", d);
      // Expand/collapse functionality
    }

    function resetZoom() {
      svg.transition().duration(750).call(
        d3.zoom().transform,
        d3.zoomIdentity
      );
    }

    function toggleCycles() {
      const cycles = document.querySelectorAll(".link.cycle");
      cycles.forEach(el => {
        el.style.display = el.style.display === "none" ? "" : "none";
      });
    }
  </script>
</body>
</html>
  `;
}
```

## Error Handling Strategy

```javascript
class DependencyMapperError extends Error {
  constructor(phase, originalError, context) {
    super(`[${phase}] ${originalError.message}`);
    this.phase = phase;
    this.originalError = originalError;
    this.context = context;
  }
}

async function safeExecute(phase, fn, fallback = null) {
  try {
    return await fn();
  } catch (error) {
    console.error(`Error in ${phase}:`, error);

    // Notify coordination system
    await notifyError(phase, error);

    // Return fallback or throw
    if (fallback !== null) {
      console.warn(`Using fallback for ${phase}`);
      return fallback;
    }

    throw new DependencyMapperError(phase, error, {
      timestamp: Date.now(),
      phase
    });
  }
}
```

## Performance Optimization

```javascript
// Cache management
const cache = new Map();
const CACHE_TTL = 3600000; // 1 hour

async function getCached(key, generator) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.value;
  }

  const value = await generator();
  cache.set(key, { value, timestamp: Date.now() });
  return value;
}

// Parallel processing
async function processInParallel(items, processor, concurrency = 10) {
  const results = [];
  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency);
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
  }
  return results;
}
```

## Integration with Other Agents

When coordinating with other agents in the swarm:

```javascript
// Query memory for context from other agents
const architectureDecisions = await retrieveFromMemory('swarm/architect/decisions');
const securityRequirements = await retrieveFromMemory('swarm/security/requirements');

// Share results with other agents
await storeInMemory('swarm/dependency-mapper/vulnerabilities', vulnerabilities);
await storeInMemory('swarm/dependency-mapper/graph', graphData);
```

## Testing Protocol

```javascript
// Self-validation
async function validateResults(report) {
  const checks = [
    () => report.statistics.total > 0,
    () => report.dependency_tree !== null,
    () => report.analysis !== undefined,
    () => report.security !== undefined
  ];

  const results = checks.map((check, i) => {
    try {
      const passed = check();
      return { check: i, passed };
    } catch (error) {
      return { check: i, passed: false, error };
    }
  });

  const failed = results.filter(r => !r.passed);
  if (failed.length > 0) {
    throw new Error(`Validation failed: ${JSON.stringify(failed)}`);
  }
}
```

## Completion Criteria

Agent considers task complete when:
1. ✅ All dependencies extracted
2. ✅ Dependency tree constructed
3. ✅ Circular dependencies detected
4. ✅ Security audit performed
5. ✅ Visualization generated
6. ✅ Report assembled
7. ✅ Results stored in memory
8. ✅ Coordination hooks executed
9. ✅ Self-validation passed

## See Also

- SKILL.md - Complete skill documentation
- PROCESS.md - Detailed process flow
- slash-command-dep-map.sh - Command-line interface
- mcp-dependency-mapper.json - MCP tool integration
