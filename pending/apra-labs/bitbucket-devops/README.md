# Claude Bitbucket DevOps Skill

A [Claude Code](https://claude.ai/code) skill for comprehensive Bitbucket DevOps automation - manage pipelines, repositories, pull requests, and CI/CD workflows. Built on the [bitbucket-mcp](https://github.com/MatanYemini/bitbucket-mcp) Model Context Protocol server.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **Developed by [Apra Labs](https://apralabs.com)** - Building AI-powered developer tools

## 🚀 Quick Start (5 minutes)

**1. Clone and install:**
```bash
git clone --recursive https://github.com/Apra-Labs/claude-bitbucket-devops-skill.git
cd claude-bitbucket-devops-skill
bash install.sh
```

**2. Get Bitbucket App Password:**
- Go to: https://bitbucket.org/account/settings/app-passwords/
- Create password with: **Repository: Read** + **Pipelines: Read, Write**

**3. Configure credentials:**
```bash
# Edit the file created by installer
nano ~/.claude/skills/bitbucket-devops/credentials.json
```

**4. Restart VSCode:**
- Close and reopen VSCode, or
- `Ctrl+Shift+P` → "Developer: Reload Window"

**5. Test it:**
```
Ask Claude: "What's the latest pipeline in my repo?"
```

✅ Done! Continue reading for detailed documentation.

---

## Features

🔍 **Find Failures Fast**
- Identify the latest failing pipeline instantly
- Locate specific pipeline runs by number
- List pipelines by status (failed, successful, running)

📊 **Deep Analysis**
- List all steps with their status and timing
- Identify exactly which steps failed
- Monitor long-running pipelines efficiently

📥 **Smart Log Management**
- Download logs from failing steps automatically
- Tail logs from running steps without downloading full files
- Auto-slice large logs into manageable chunks

🚀 **Pipeline Control**
- List available pipeline types
- Trigger new pipeline runs with custom variables
- Stop running pipelines
- Monitor pipeline progress in real-time

## Why This Matters: The DevOps REPL Loop

### The Traditional Pipeline Problem

Pipeline development is painfully slow:
1. Write code → Push → Wait 10-30 minutes
2. Build fails → Download logs → Investigate errors
3. Context switch → Fix code → Push again
4. Repeat until green ✅

**Average time to fix a failing pipeline: 2-4 hours** (across multiple cycles)

### The Claude Code Solution: AI-Powered DevOps REPL

With this skill, Claude Code transforms pipeline development into a rapid **Read-Eval-Print Loop**:

```
┌────────────────────────────────────────────────────────────────┐
│ REPL Loop for DevOps (Minutes, not Hours)                      │
├────────────────────────────────────────────────────────────────┤
│ 1. Claude observes your pipeline in real-time                  │
│ 2. Detects failures instantly                                  │
│ 3. Downloads and analyzes logs automatically                   │
│ 4. Identifies root cause with AI                               │
│ 5. Suggests precise fixes to your code/script/yaml             │
│ 6. You apply fix → Claude triggers new build                   │
│ 7. Repeat until green ✅✅                                    │
└────────────────────────────────────────────────────────────────┘
```

**Result: 10-15 minute iteration cycles** instead of hours

### Key Benefits

- **Stay in Flow**: No context switching between IDE, browser, and log files
- **Faster Debugging**: AI analyzes thousands of log lines in seconds
- **Continuous Learning**: Claude remembers patterns across pipeline runs
- **Zero Manual Steps**: From failure detection to fix suggestion - fully automated observation

**Example Conversation:**
```
You: "The main branch build is failing"
Claude: [Checks latest pipeline, downloads logs, analyzes]
       "Found the issue: TypeScript compilation error in auth.service.ts line 42
        Missing return type. Here's the fix..."
You: "Apply it"
Claude: [Fixes code, commits, triggers new pipeline]
       "Build #347 started. Monitoring..."
       [5 minutes later]
       "✅ Build passed! All tests green."
```

This is **DevOps at the speed of thought** - where your AI pair programmer handles the tedious observe-analyze-fix loop while you focus on building features.

## Prerequisites

### 1. Claude Code

Install the Claude Code extension for VSCode:
- [Visual Studio Code Extension](https://marketplace.visualstudio.com/items?itemName=Anthropic.claude-code)

### 2. Node.js & Git

This skill uses direct Node.js API calls (no MCP server required):
- **Node.js**: v18 or higher - [Download](https://nodejs.org/)
- **Git**: For submodule management - [Download](https://git-scm.com/)

> **💡 No MCP Server Needed!** This skill uses the [bitbucket-mcp](https://github.com/MatanYemini/bitbucket-mcp) codebase as a library (via git submodule), not as an MCP server. This approach **eliminates approval prompts** mentioned in [GitHub Issue #10801](https://github.com/anthropics/claude-code/issues/10801) by using direct Node.js calls through the auto-approved Bash tool.

### 3. Bitbucket App Password

Create a Bitbucket App Password with these scopes:

1. Go to: https://bitbucket.org/account/settings/app-passwords/
2. Click "Create app password"
3. Select these permissions:
   - ✅ **Repository**: Read
   - ✅ **Pipelines**: Read, Write

4. Save the generated password (you'll need it for configuration)

## Installation

### Quick Install (Recommended)

**Clone and run the installer:**

```bash
# Clone the skill repository
git clone --recursive https://github.com/Apra-Labs/claude-bitbucket-devops-skill.git
cd claude-bitbucket-devops-skill

# Run installer
# Unix/Linux/macOS:
bash install.sh

# Windows (PowerShell):
powershell -ExecutionPolicy Bypass -File install.ps1
```

The installer will:
1. ✅ Verify prerequisites (Node.js, Git)
2. ✅ Initialize the bitbucket-mcp submodule
3. ✅ Build the CLI tools
4. ✅ Deploy to `~/.claude/skills/bitbucket-devops/`
5. ✅ Create credentials template

### Manual Installation

If you prefer manual setup:

```bash
# 1. Clone with submodules
git clone --recursive https://github.com/Apra-Labs/claude-bitbucket-devops-skill.git ~/.claude/skills/bitbucket-devops
cd ~/.claude/skills/bitbucket-devops

# 2. Build the bitbucket-mcp library
cd bitbucket-mcp
npm install
npm run build
cd ..

# 3. Configure credentials
cp credentials.json.template credentials.json
# Edit credentials.json with your Bitbucket details
```

### Configure Credentials

Edit `~/.claude/skills/bitbucket-devops/credentials.json`:

```json
{
  "url": "https://api.bitbucket.org/2.0",
  "workspace": "your-workspace-name",
  "user_email": "your-email@example.com",
  "username": "your-workspace-name",
  "password": "your-bitbucket-app-password"
}
```

**Important field distinctions:**
- `user_email`: Your Bitbucket account email (for API authentication)
- `username`: Your Bitbucket username/workspace slug (for git operations, typically same as workspace)
- `workspace`: Your workspace slug (repository owner)
- `password`: App password from Bitbucket

**Note:** The skill validates these fields and will show helpful error messages if you accidentally put your email in the `username` field or vice versa.

**Alternative locations** (priority order):
1. Project level: `./credentials.json` (highest priority)
2. User level: `~/.bitbucket-credentials`
3. Skill level: `~/.claude/skills/bitbucket-devops/credentials.json`

### Verify Installation

Test that everything is working:

```bash
# Test helpers are available
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-latest "your-workspace" "your-repo"

# Expected: JSON output with latest pipeline info
```

**If you get errors:**
- "Cannot use import statement outside a module" → Make sure package.json was created in the skill directory
- "Permission denied" → Check your credentials.json has correct app password
- "Pipeline not found" → Verify workspace/repo names are correct

### Restart Claude Code

**Important**: Restart VSCode to load the skill:
- Close and reopen VSCode
- Or use: `Ctrl+Shift+P` → "Developer: Reload Window"

### Test the Skill

Open any project with Bitbucket pipelines and ask Claude:
```
"What's the latest pipeline?"
"Show me failing builds"
"Get logs from pipeline #123"
```

The skill activates automatically when you ask pipeline-related questions!

## Known Limitations

### Pipeline Artifacts Cannot Be Downloaded via API

**IMPORTANT:** Bitbucket Cloud does NOT provide an API to download pipeline artifacts.

**If you need to download build artifacts:**
1. Use the Bitbucket web UI:
   - Repository → Pipelines → Build # → Step → Artifacts section → Download button
2. Note: Artifacts expire automatically after 14 days

**Tip:** For programmatic artifact access, consider uploading to S3/Azure Blob Storage during your pipeline (separate skills available for those platforms).

This limitation has been thoroughly researched - no undocumented API exists. See [ARTIFACTS_RESEARCH.md](ARTIFACTS_RESEARCH.md) for full research details.

### Add .pipeline-logs to .gitignore

In each project where you use this skill, add to `.gitignore`:

```
# Pipeline debug logs
.pipeline-logs/
```

## Usage

Just ask Claude naturally! The skill activates automatically for pipeline-related questions.

### Examples

**Find Latest Failure:**
```
You: What's the latest failed pipeline?
```

**Inspect Specific Pipeline:**
```
You: Show me details for pipeline #34
```

**Analyze Failures:**
```
You: Which steps failed in pipeline #34?
You: Get logs for the failed steps
```

**Trigger New Build:**
```
You: Run the deploy-production pipeline on main
You: Trigger staging deployment with DRY_RUN=true
```

**Work Across Projects:**
```
You: Show latest failure in workspace/other-repo
You: Get pipeline #45 from my-workspace/my-project
```

## How It Works

### Log Storage

Logs are downloaded to your **current project directory**:

```
your-project/
├── .pipeline-logs/           ← Created automatically
│   ├── pipeline-123-deploy.log
│   ├── pipeline-123-test.log
│   └── metadata.json
├── src/
└── ...
```

This means:
- ✅ Logs stay with the relevant project
- ✅ Each project has its own log directory
- ✅ Easy to add to `.gitignore`
- ✅ No global state to manage

### Workspace Detection

The skill automatically works with any workspace/repo you specify:

- **Explicit**: "Show failures in workspace/repo"
- **From credentials**: Uses your configured workspace as default
- **From git remote**: Detects workspace from current project

## How This Skill Works

### No MCP Server Required ✨

Unlike traditional MCP-based skills, this skill **does not require running an MCP server**. Here's how it works:

1. **Git Submodule**: Uses [bitbucket-mcp](https://github.com/Apra-Labs/bitbucket-mcp) as a code library (not a server)
2. **Direct API Calls**: Executes Node.js commands directly via the Bash tool
3. **Auto-Approved**: Bash tool is auto-approved in Claude Code - **no approval prompts!**
4. **No MCP Protocol Overhead**: Faster execution, simpler setup

### Why This Approach?

The traditional MCP server approach (v1.0.0) required manual approval for every API call due to [GitHub Issue #10801](https://github.com/anthropics/claude-code/issues/10801). By using direct Node.js calls through Bash (v1.1.0), we've **eliminated all approval prompts** while maintaining full functionality.

**Benefits:**
- ✅ Zero approval prompts
- ✅ Faster execution
- ✅ Simpler installation
- ✅ Same powerful API access
- ✅ Works offline (no server startup)

## Troubleshooting

### Skill not activating

**Solution**: Restart VSCode to reload skills
- `Ctrl+Shift+P` → "Developer: Reload Window"

### "Pipeline not found"

**Possible causes:**
- Pipeline number is incorrect
- Pipeline is too old (try recent pipelines first)
- Wrong workspace/repo

**Solution:**
```
You: List recent pipelines
You: Show me the last 20 builds
```

### "Permission denied"

**Check:**
- App password has `Repository: Read` and `Pipeline: Read/Write` scopes
- Username and password are correct in `credentials.json`
- Workspace name is correct

### Logs unavailable

**Reasons:**
- Pipeline is still running (wait for completion)
- Logs expired (Bitbucket retention policy)
- Network connectivity issues

## Credits

This skill is built on top of:

- **[bitbucket-mcp](https://github.com/Apra-Labs/bitbucket-mcp)** by [Apra Labs](https://github.com/Apra-Labs), forked from [@MatanYemini's original work](https://github.com/MatanYemini/bitbucket-mcp) - Provides the Bitbucket API client library used by this skill
- **[Claude Code](https://claude.ai/code)** by [Anthropic](https://www.anthropic.com/) - The AI coding assistant platform

**Note:** While this skill uses the bitbucket-mcp codebase, it does NOT require running the MCP server. We use it as a library via git submodule.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Ideas for contributions:**
- Additional pipeline management features
- Better log analysis and error detection
- Support for Bitbucket Server (self-hosted)
- Integration with other CI/CD platforms

## License

This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

**You are free to:**
- ✅ Share — copy and redistribute in any medium or format
- ✅ Adapt — remix, transform, and build upon the material

**Under the following terms:**
- **Attribution** — You must give appropriate credit to Apra Labs and link to this repository

See [LICENSE](./LICENSE) for full details.

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Apra-Labs/claude-bitbucket-devops-skill/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Apra-Labs/claude-bitbucket-devops-skill/discussions)
- 📖 **Documentation**: This README and [SKILL.md](./SKILL.md)

## Roadmap

### Phase 1: Build & Deployment Management ✨ **Current Focus**
*Foundation: Master the operational side of DevOps*

- [ ] **Enhanced Build Monitoring**
  - Real-time build status tracking across branches
  - Build queue visibility and wait time analysis
  - Parallel build coordination and monitoring
  - Build artifact management and inspection

- [ ] **Deployment Operations**
  - Multi-environment deployment tracking (dev, staging, prod)
  - Deployment history and version tracking
  - Rollback assistance and recovery workflows
  - Deployment approval workflows
  - Environment health checks and validation

- [ ] **Failure Analysis & Recovery**
  - AI-powered error detection in logs
  - Root cause analysis with historical pattern matching
  - Quick-fix suggestions for common failures
  - Automated retry logic for transient failures
  - Failure notification and escalation

- [ ] **Build Performance**
  - Build duration tracking and trends
  - Slow step identification
  - Resource utilization analysis
  - Cache efficiency monitoring

### Phase 2: Pipeline Intelligence & Optimization
*Evolution: Build better pipelines*

- [ ] **Pipeline Analysis**
  - Pipeline comparison (side-by-side runs)
  - Performance regression detection
  - Cost analysis per pipeline
  - Success rate trends and reliability metrics

- [ ] **Pipeline Improvement**
  - Suggest optimizations (parallelization, caching, etc.)
  - Identify redundant steps
  - Recommend pipeline best practices
  - Template suggestions based on project type
  - Predict pipeline failures before execution

- [ ] **Advanced Pipeline Features**
  - Custom pipeline creation from conversations
  - Pipeline template library
  - Variable management and validation
  - Conditional execution logic design
  - Multi-stage pipeline orchestration

- [ ] **Testing & Quality Gates**
  - Test result analysis and flaky test detection
  - Code coverage tracking
  - Quality gate enforcement
  - Integration test environment management

### Phase 3: Work Item & Pull Request Management
*Collaboration: Connect code to work*

- [ ] **Pull Request Workflows**
  - Create PRs from current branch with AI-generated descriptions
  - Review PRs with inline commenting
  - Approve/decline PRs with context
  - Merge with conflict detection
  - Track PR status and blockers

- [ ] **Code Review Assistance**
  - AI-powered code review suggestions
  - Security vulnerability detection
  - Best practice recommendations
  - Impact analysis and risk assessment

- [ ] **Work Item Integration**
  - Link commits/PRs to Jira issues automatically
  - Track work item status through pipeline
  - Generate release notes from work items
  - Sprint/release progress tracking

- [ ] **PR Tasks & Collaboration**
  - Create and manage TODO tasks on PRs
  - Resolve/reopen comment threads
  - Smart reviewer assignment
  - PR template enforcement

### Phase 4: Repository & Branch Intelligence
*Organization: Manage code at scale*

- [ ] **Smart Repository Management**
  - Auto-detect workspace/repo from git config
  - Repository health insights
  - Cross-repo search and analysis
  - Repository templates and scaffolding

- [ ] **Branch Strategy & Governance**
  - Enforce branching model policies
  - Branch naming convention validation
  - Stale branch cleanup automation
  - Merge conflict prediction
  - Branch protection rules management

- [ ] **Code Organization**
  - Monorepo vs multi-repo guidance
  - Code ownership tracking (CODEOWNERS)
  - Dependency analysis between repos
  - Migration assistance between strategies

### Phase 5: Team Metrics & Analytics
*Insights: Measure and improve*

- [ ] **DevOps Metrics (DORA)**
  - Deployment frequency
  - Lead time for changes
  - Mean time to recovery (MTTR)
  - Change failure rate
  - Custom metric dashboards

- [ ] **Team Performance**
  - PR review velocity
  - Build success rates by team/developer
  - Deployment success patterns
  - Bottleneck identification

- [ ] **Operational Reports**
  - Pipeline cost analysis
  - Resource utilization trends
  - SLA compliance tracking
  - Incident response metrics

### Phase 6: Integrations & Enterprise
*Scale: Enterprise-ready features*

- [ ] **External Integrations**
  - Jira (issue tracking and linking)
  - Slack/Discord/Teams (notifications and commands)
  - PagerDuty/Opsgenie (incident management)
  - GitHub migration tools

- [ ] **Enterprise Features**
  - Bitbucket Server/Data Center support
  - SSO and enterprise authentication
  - Compliance and audit logging
  - Multi-tenant support
  - Advanced security scanning

- [ ] **Advanced Automation**
  - Custom workflow templates
  - Multi-repository operations
  - Automated compliance checks
  - Policy-as-code enforcement

### Continuous Improvements
- [ ] Auto-approval support (waiting on Claude Code Issue #10801)
- [ ] Performance optimization (caching, batch operations)
- [ ] Enhanced error messages and troubleshooting
- [ ] Video tutorials and interactive guides
- [ ] Community plugin system

---

**Maintained by [Apra Labs](https://github.com/Apra-Labs)**

Built with ❤️ for the Claude Code community
