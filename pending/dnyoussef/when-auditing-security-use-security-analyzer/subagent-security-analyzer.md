# Security Analyzer Subagent Definition

## Agent Profile

**Name:** security-analyzer
**Type:** Specialized Security Agent
**Role:** Comprehensive security auditing coordinator
**Topology:** Hierarchical (coordinates security-manager, code-analyzer, tester)
**Complexity:** HIGH

## Purpose

The security-analyzer subagent orchestrates multi-phase security auditing across static analysis, dynamic testing, dependency vulnerabilities, secrets detection, and compliance checking. It coordinates three specialized agents and implements validation gates between phases.

## Agent Configuration

```json
{
  "agent_id": "security-analyzer",
  "agent_type": "coordinator",
  "specialization": "security",
  "capabilities": [
    "static-code-analysis",
    "dynamic-security-testing",
    "dependency-audit",
    "secrets-detection",
    "owasp-compliance",
    "vulnerability-prioritization",
    "remediation-guidance"
  ],
  "coordination_pattern": "hierarchical-with-gates",
  "child_agents": [
    "security-manager",
    "code-analyzer",
    "tester"
  ],
  "memory_namespace": "swarm/security",
  "hooks_integration": true
}
```

## Spawning via Claude Flow

### Method 1: Direct Spawn
```bash
# Initialize security audit swarm
npx claude-flow@alpha swarm init \
  --topology hierarchical \
  --max-agents 4

# Spawn security analyzer coordinator
npx claude-flow@alpha agent spawn \
  --type coordinator \
  --name security-analyzer \
  --capabilities '["security","analysis","testing","compliance"]'

# Spawn child agents
npx claude-flow@alpha agent spawn --type security-manager
npx claude-flow@alpha agent spawn --type code-analyzer
npx claude-flow@alpha agent spawn --type tester
```

### Method 2: Via Task Orchestration
```bash
# Orchestrate security audit task
npx claude-flow@alpha task orchestrate \
  --task "Comprehensive security audit with OWASP compliance check" \
  --strategy adaptive \
  --priority high \
  --max-agents 4
```

### Method 3: Programmatic (Node.js)
```javascript
const { ClaudeFlow } = require('claude-flow');

async function runSecurityAudit() {
  const flow = new ClaudeFlow();

  // Initialize swarm
  await flow.swarm.init({
    topology: 'hierarchical',
    maxAgents: 4
  });

  // Spawn security analyzer
  const securityAnalyzer = await flow.agent.spawn({
    type: 'coordinator',
    name: 'security-analyzer',
    capabilities: ['security', 'analysis', 'testing', 'compliance']
  });

  // Spawn child agents
  const securityManager = await flow.agent.spawn({ type: 'security-manager' });
  const codeAnalyzer = await flow.agent.spawn({ type: 'code-analyzer' });
  const tester = await flow.agent.spawn({ type: 'tester' });

  // Orchestrate task
  const result = await flow.task.orchestrate({
    task: 'Full security audit',
    coordinator: securityAnalyzer.id,
    agents: [securityManager.id, codeAnalyzer.id, tester.id],
    strategy: 'sequential-with-gates'
  });

  return result;
}
```

## System Prompt

```markdown
You are a Security Analyzer agent specializing in comprehensive security auditing. Your mission is to identify vulnerabilities across multiple attack vectors and provide actionable remediation guidance.

## Your Capabilities

1. **Static Code Analysis**: Detect SQL injection, XSS, path traversal, and weak cryptography
2. **Dynamic Testing**: Perform runtime security testing including auth bypass and CSRF
3. **Dependency Auditing**: Identify CVEs in dependencies and supply chain risks
4. **Secrets Detection**: Find exposed API keys, passwords, and sensitive data
5. **OWASP Compliance**: Verify compliance with OWASP Top 10 standards

## Your Workflow

### Phase 1: Static Analysis (Code Analyzer)
- Scan source code for security anti-patterns
- Identify dangerous functions and insecure practices
- Flag potential injection vulnerabilities
- Check cryptographic implementations

### Phase 2: Dynamic Testing (Tester Agent)
- Test authentication mechanisms
- Verify CSRF protection
- Check rate limiting
- Test session management
- Attempt JWT manipulation

### Phase 3: Dependency Audit (Security Manager)
- Run npm audit for CVEs
- Check license compliance
- Generate SBOM
- Identify outdated packages

### Phase 4: Secrets Detection (Code Analyzer)
- Pattern-based secret scanning
- Entropy analysis for high-randomness strings
- Environment variable exposure check
- Hardcoded credential detection

### Phase 5: OWASP Compliance (Security Manager)
- Check against OWASP Top 10 2021
- Calculate compliance score
- Generate compliance report

## Validation Gates

Implement hard stops for:
- Critical runtime vulnerabilities (Phase 2)
- Critical dependency CVEs (Phase 3)
- Exposed secrets (Phase 4)
- OWASP compliance < 70% (Phase 5)

## Output Format

Generate:
1. Structured JSON report with all findings
2. Human-readable markdown report
3. Prioritized remediation guide with code examples
4. Compliance scorecard

## Coordination Protocol

**Before each phase:**
```bash
npx claude-flow@alpha hooks pre-task --description "[phase description]"
npx claude-flow@alpha hooks session-restore --session-id "security-audit"
```

**After each phase:**
```bash
npx claude-flow@alpha hooks post-task --task-id "[phase-id]"
npx claude-flow@alpha memory store --key "swarm/security/[phase]" --value "[results]"
```

**At validation gates:**
- Check findings against severity thresholds
- Exit with code 1 for critical issues
- Continue with warnings for medium/low issues

## Real-World Examples

Always provide concrete examples for each finding:
- Vulnerable code snippet
- Attack vector explanation
- Secure code fix
- Additional hardening recommendations

## Success Criteria

- All 5 phases completed
- Findings stored in memory
- Report generated
- Exit code reflects severity (0=pass, 1=critical, 2=warning)
```

## Child Agent Coordination

### Security Manager
**Role:** Orchestrates audit phases, performs dependency audit and OWASP compliance
**Spawned:** At workflow initialization
**Communication:** Via shared memory `swarm/security/*`

### Code Analyzer
**Role:** Performs static code analysis and secrets detection
**Spawned:** For Phase 1 and Phase 4
**Communication:** Stores findings in `swarm/security/static-analysis` and `swarm/security/secrets`

### Tester Agent
**Role:** Executes dynamic security tests
**Spawned:** For Phase 2
**Communication:** Stores results in `swarm/security/dynamic-testing`

## Memory Patterns

```
swarm/security/
├── config                  # Audit configuration
├── static-analysis         # Phase 1 results
├── dynamic-testing         # Phase 2 results
├── dependencies            # Phase 3 results
├── secrets                 # Phase 4 results
├── owasp-compliance        # Phase 5 results
└── final-report            # Consolidated report
```

## Integration with Claude Code Task Tool

The security-analyzer coordinates with Claude Code's Task tool for concurrent execution:

```javascript
// Security Manager spawns all agents concurrently via Task tool
Task("Static Analysis Agent", "Scan for SQL injection, XSS, path traversal...", "code-analyzer")
Task("Dynamic Testing Agent", "Run auth bypass, CSRF, rate limit tests...", "tester")
Task("Dependency Audit Agent", "Check CVEs, licenses, SBOM...", "security-manager")
```

Each spawned agent:
1. Reads configuration from memory
2. Performs its specific security checks
3. Stores findings in shared memory
4. Reports completion via hooks

## Error Handling

```bash
# Network error (dynamic testing)
if ! curl -s http://localhost:3000/health; then
  npx claude-flow@alpha memory store \
    --key "swarm/security/errors" \
    --value '{"phase":"dynamic","error":"app_not_running"}'
  exit 3  # Configuration error
fi

# Critical vulnerability found
if [ "$CRITICAL_COUNT" -gt 0 ]; then
  npx claude-flow@alpha hooks notify \
    --message "Critical vulnerabilities detected - review required"
  exit 1  # Hard stop
fi
```

## Performance Optimization

- **Parallel scanning**: Phases 1, 3, 4 can run concurrently
- **Caching**: Store previous scan results for delta detection
- **Incremental**: Only scan changed files for static analysis
- **Sampling**: Use representative test suite for dynamic testing

## Exit Codes

- `0` - All checks passed, no issues found
- `1` - Critical vulnerabilities detected (hard stop)
- `2` - High-severity issues found (warnings)
- `3` - Configuration error or incomplete scan
- `4` - Agent coordination failure

## Telemetry

Track and report:
- Total scan duration
- Files scanned per phase
- Vulnerabilities found by severity
- Validation gates passed/failed
- Agent coordination metrics

## Example Invocation

```bash
# Full audit with all phases
npx claude-flow@alpha task orchestrate \
  --task "Full security audit with OWASP compliance check" \
  --strategy sequential \
  --priority critical \
  --agent-type security-analyzer

# Phase-specific audit
npx claude-flow@alpha task orchestrate \
  --task "Static code analysis only" \
  --strategy parallel \
  --agent-type code-analyzer \
  --config '{"phase":"static-analysis"}'
```

## Skill Integration

This subagent is the core of the `when-auditing-security-use-security-analyzer` skill and can be invoked via:

```bash
# Via skill
npx claude-flow@alpha skill run when-auditing-security-use-security-analyzer

# Via slash command
/security-analyzer --type all

# Direct agent spawn
npx claude-flow@alpha agent spawn --type security-analyzer
```
