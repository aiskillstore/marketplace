# Changelog

All notable changes to the Gate MCP Installer skill are documented here.

Format: date-based versioning (`YYYY.M.DD`). Each release includes a sequential suffix: `YYYY.M.DD-1`, `YYYY.M.DD-2`, etc.

---

## [2026.3.4-1] - 2026-03-04

### Added
- Initial release
- One-click Gate MCP (mcporter) installation script (`scripts/install-gate-mcp.sh`)
- Automated mcporter CLI global installation via npm
- Gate MCP server configuration with proper endpoint
- Connectivity verification via tool listing
- Manual installation steps as fallback
- Troubleshooting guide for common issues
- Version management with `CHANGELOG.md`

### Audit
- ✅ Single bash script dependency (`install-gate-mcp.sh`)
- ✅ Uses npm for mcporter installation (requires network)
- ✅ No credential handling (public MCP endpoint)
- ✅ No destructive operations
