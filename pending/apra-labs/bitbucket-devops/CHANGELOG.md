# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-11-04

### Fixed
- **Critical**: Fixed install.sh missing dependencies after deployment
  - Now copies `node_modules/` directory from bitbucket-mcp (contains axios and other dependencies)
  - Now copies `package.json` from bitbucket-mcp (enables module resolution)
  - Now copies root `package.json` (enables ES module support for lib/helpers.js)
  - Previously only copied `dist/` folder, causing "Cannot find package 'axios'" errors

### Impact
- Users who installed v1.2.0 or earlier would encounter `ERR_MODULE_NOT_FOUND` errors
- This fix ensures all required dependencies are available in the deployed skill directory
- No reinstallation required if already working - only affects fresh installs

## [1.2.0] - 2025-11-04

### 🎯 Major Refactoring: Credential Field Clarity + Git Operations Support

### Changed
- **BREAKING**: Credential format updated for semantic clarity
  - `username` field renamed to `user_email` (for API authentication)
  - New `username` field added (for git operations, workspace slug)
  - Old format no longer supported (no backward compatibility needed - no existing users)
- Updated `BitbucketConfig` interface with `gitUsername` field
- Enhanced credential validation with helpful error messages

### Added
- **Git Operations Support**: New helper functions for git operations
  - `buildGitUrl()`: Constructs authenticated git URLs
  - `testGitAuth()`: Tests git authentication to repository
  - `cloneRepository()`: Clones repository to local directory
- CLI commands for git operations:
  - `test-git-auth <workspace> <repo>`: Test git connectivity
  - `clone-repo <workspace> <repo> [target_dir]`: Clone repository
- Comprehensive field validation:
  - Detects email in `username` field and shows helpful fix
  - Detects missing `user_email` field with clear example
  - Prevents common configuration mistakes

### Improved
- **credentials.json.template**: Updated with clear field explanations
- **README.md**: Updated configuration section with field distinctions
- **SKILL.md**: Updated credential format (critical for Claude to function correctly)
- **docs/GIT_OPERATIONS.md**: Completely rewritten to reflect implementation
- **install.sh**: Updated to show correct field descriptions
- All documentation now consistently uses new credential format

### Testing
- ✅ API operations tested with `user_email` field (successful)
- ✅ Git operations tested with `username` field (successful)
- ✅ Validation tested with email in `username` field (correct error)
- ✅ Validation tested with missing `user_email` (correct error)

### Benefits
1. **Clarity**: Fields named for their actual purpose (`user_email` vs `username`)
2. **Validation**: Clear error messages guide users to fix mistakes
3. **Git-ready**: Git operations work out of the box
4. **Self-documenting**: Code clearly shows what each field does
5. **Future-proof**: Enables git operations without confusion

### Migration
No migration needed - skill had no existing users at time of refactoring.

## [1.0.0] - 2025-11-01

### Added
- Initial release of Claude Bitbucket DevOps Skill
- 8 core usage patterns:
  1. Find latest failing pipeline
  2. Inspect specific pipeline by number
  3. Identify failing steps in a pipeline
  4. Download logs from failing steps
  5. Download logs from specific steps
  6. Auto-slice large logs into manageable chunks
  7. List available pipeline types for branches
  8. Trigger pipeline runs with custom variables
- Project-relative log storage (`.pipeline-logs/`)
- Cross-project support (specify any workspace/repo)
- Automatic workspace detection from MCP config
- Smart log chunking for files >10KB
- Comprehensive documentation:
  - README.md with quick start guide
  - INSTALL.md with step-by-step instructions
  - QUICK_REFERENCE.md for common commands
  - CONTRIBUTING.md for contributors
  - SKILL.md with detailed skill logic
- CC BY 4.0 license
- Proper attribution to bitbucket-mcp by @MatanYemini

### Known Issues
- MCP tool calls require manual approval in VSCode extension
  - Tracking: [GitHub Issue #10801](https://github.com/anthropics/claude-code/issues/10801)
  - Impact: Users must click "Yes" for each Bitbucket API call
  - Workaround: None currently available in VSCode extension

## [1.1.0] - 2025-11-02

### 🎉 Major Update: No More MCP Approval Prompts!

### Changed
- **BREAKING**: Converted from MCP tools to Node.js CLI approach
- **NEW**: Direct Node.js API calls via Bash tool (auto-approved in Claude Code)
- **NEW**: Git submodule architecture using `apra-bitbucket-mcp`
- **NEW**: Flexible credential storage with priority order (project → user → skill)
- Refactored SKILL.md to use Node.js commands instead of `mcp__bitbucket-mcp__*` tools
- Updated `allowed-tools` to: `Bash, Read, Write, Grep, Glob`

### Added
- **Git Submodule**: `bitbucket-mcp` (apra-bitbucket-mcp) as submodule
- **Helper Library**: `lib/helpers.js` with intuitive high-level functions:
  - `get-latest-failed` - Get most recent failed pipeline
  - `get-latest` - Get most recent pipeline (any status)
  - `get-by-number` - Find pipeline by build number
  - `get-failed-steps` - Get all failed steps
  - `download-failed-logs` - Download logs from failed steps
  - `get-info` - Get formatted pipeline information
- **CLI Tool**: `bitbucket-cli` command in submodule for direct API access
- **Credential Template**: `credentials.json.template`
- **Install Scripts**:
  - `install.sh` - Automated installer for Unix/Linux/macOS
  - `install.ps1` - Automated installer for Windows PowerShell
- **Credential Priority**: Project-level → User-level → Skill-level

### Removed
- MCP server runtime requirement (still uses bitbucket-mcp as library)
- VSCode MCP configuration requirement
- All MCP approval prompt warnings

### Fixed
- **Issue #10801 workaround**: No approval prompts by using Bash + Node.js
- Simplified installation (one-command setup)
- Better cross-platform support (Windows, macOS, Linux)

### Upgraded
- Prerequisites: Now requires Node.js v18+ and Git (more portable than bash/curl/jq)
- Performance: Direct API calls via Node.js, no MCP protocol overhead
- Maintainability: Reuses bitbucket-mcp client code via submodule
- Type Safety: Benefits from TypeScript definitions in bitbucket-mcp

### Migration Notes

**From v1.0.0 to v1.1.0:**

1. **Uninstall MCP server** (optional, no longer needed for skill):
   - Remove bitbucket-mcp from VSCode settings.json (if configured)

2. **Clone/pull latest skill code**:
   ```bash
   cd ~/.claude/skills/bitbucket-devops
   git pull
   ```

3. **Run new installer**:
   ```bash
   # Unix/macOS
   bash install.sh

   # Windows
   powershell -ExecutionPolicy Bypass -File install.ps1
   ```
   This will:
   - Initialize git submodule (bitbucket-mcp)
   - Install Node.js dependencies
   - Build the CLI tool
   - Create credentials.json from template

4. **Configure credentials**:
   - Edit `credentials.json` with your Bitbucket credentials
   - Or create `~/.bitbucket-credentials` for user-level config

5. **Restart VSCode**

**Benefits of 1.1.0:**
- ✅ **Zero approval prompts** - Bash + Node.js is auto-approved
- ✅ **Simpler setup** - No MCP server runtime configuration
- ✅ **Faster** - Direct API calls, no MCP protocol overhead
- ✅ **More maintainable** - Reuses bitbucket-mcp client via submodule
- ✅ **Better DX** - Intuitive helper functions for common operations

## [Unreleased]

### Planned Features
- Auto-detect workspace from git config
- Support for Bitbucket Server (self-hosted)
- Pipeline comparison (compare two runs side-by-side)
- Build time trends and analytics
- Integration with notification services (Slack, Discord)
- Advanced log analysis with AI-powered error detection
- Pipeline template suggestions based on failures

### Awaiting External Dependencies
- Auto-approval support (depends on Claude Code issue #10801 resolution)
- Skill hot-reload without VSCode restart (Claude Code feature request)

---

## Version History

- **1.0.0** (2025-11-01) - Initial public release

## Upgrade Guide

### From Pre-release to 1.0.0

If you were using a pre-release version:

1. **Backup your custom configurations** (if any)
2. **Remove old skill:**
   ```bash
   rm -rf ~/.claude/skills/bitbucket-devops
   ```
3. **Install 1.0.0** following [INSTALL.md](./INSTALL.md)
4. **Restore custom configurations**
5. **Restart VSCode**

---

**Maintained by [Apra Labs](https://github.com/Apra-Labs)**
