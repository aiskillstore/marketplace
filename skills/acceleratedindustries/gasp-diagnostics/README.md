# GASP Diagnostics Skill

A Claude Code skill for intelligent system diagnostics using GASP (General AI Specialized Process monitor).

**This skill is included with GASP** to provide seamless AI-powered diagnostics out of the box.

## What This Does

This skill enables Claude to:
- **Actively fetch** GASP metrics from your hosts via HTTP
- **Analyze** system performance with context-aware interpretation
- **Diagnose** issues across CPU, memory, disk, network, GPU, and more
- **Compare** multiple hosts to identify outliers
- **Understand** your specific infrastructure patterns

## Installation

### For Claude Code Users (Recommended)

If you installed GASP to `/usr/local` or `/opt/gasp`, simply symlink the skill:

```bash
# From system installation
ln -s /usr/local/share/gasp/skill/gasp-diagnostics ~/.claude/skills/gasp-diagnostics

# Or from opt
ln -s /opt/gasp/skill/gasp-diagnostics ~/.claude/skills/gasp-diagnostics

# Or from source/dev installation
ln -s /path/to/gasp/skill/gasp-diagnostics ~/.claude/skills/gasp-diagnostics
```

This keeps the skill updated with your GASP installation.

### For Claude Desktop/Mobile

1. Copy or symlink `gasp-diagnostics.skill` to your skills directory
2. In Claude, go to Settings → Skills
3. The skill should appear automatically

### For claude.ai

Skills can be uploaded via the Skills menu (click your profile, then Skills).

## Usage Examples

Once installed, just ask Claude to check your systems:

```
"Check hyperion for me"
"What's going on with accelerated.local?"
"Is there anything wrong with proxmox1?"
"Compare resource usage on hyperion and dev-server"
"Why is my system slow?" (fetches localhost)
```

Claude will:
1. Automatically fetch GASP metrics from the host
2. Analyze the JSON output
3. Identify any issues
4. Provide specific, actionable recommendations

## How It Works

### Progressive Disclosure (Token Efficient!)

The skill uses progressive loading to minimize context usage:

- **Idle state**: ~100 tokens (just metadata)
- **Active diagnosis**: ~2,600 tokens (loads SKILL.md when triggered)
- **Complex issues**: ~4,100 tokens (loads reference files only if needed)

Compare this to an MCP server that would consume ~1,300+ tokens in EVERY conversation!

### Active Fetching

The skill teaches Claude to use `web_fetch` to retrieve GASP metrics:

```
web_fetch("http://hostname:8080/metrics")
```

No manual copy/paste needed - Claude fetches and analyzes automatically.

## What's Included

### SKILL.md
Core instructions for:
- Fetching GASP metrics from hosts
- Interpreting CPU, memory, disk, network, GPU metrics
- Quick diagnosis workflows
- Multi-host analysis patterns
- When to load reference files

### references/diagnostic-workflows.md
Detailed procedures for:
- Memory leak detection
- Performance regression investigation
- Container/VM performance issues
- GPU workload diagnosis
- Network-related issues
- Disk I/O bottleneck analysis
- Systemd service failure investigation
- And more...

### references/common-patterns.md
Infrastructure-specific patterns for:
- Development workstations (Arch Linux, Hyprland/KDE/GNOME)
- .local mDNS hosts
- Proxmox virtualization hosts
- Container hosts (Docker/LXC)
- Application-specific patterns (browsers, IDEs, databases)
- Desktop environment patterns
- GPU workload patterns
- Network patterns
- Time-of-day and seasonal patterns

### scripts/fetch-gasp.sh
Optional convenience script for manually fetching GASP metrics (Claude doesn't need this, it can fetch directly).

## Requirements

- **Claude Code** CLI tool installed (get it at [claude.ai/code](https://claude.ai/code))
- **GASP** running on the hosts you want to monitor (port 8080 by default)
- Hosts accessible via **hostname, IP, or .local mDNS**

**Note:** If you're reading this, you likely already have GASP installed!

## Example Interaction

```
User: "The accelerated.local VM is behaving strangely, please check it out for me."

Claude: [Fetches http://accelerated.local:8080/metrics]

"Found the issue - accelerated.local is experiencing memory pressure at 8.2%. 
Your postgres container started swapping 2 hours ago and is now using 12GB RAM 
(up from a 4GB baseline). This likely indicates a query leak or missing query 
result limit.

Recommendations:
1. Check recent queries: docker exec postgres psql -c 'SELECT * FROM pg_stat_activity'
2. Look for long-running queries without limits
3. Consider restarting the container if safe to do so
4. Add query result limits to prevent this in the future"
```

## Customization

The skill source is included in the `gasp-diagnostics/` directory. You can customize:

1. **common-patterns.md** - Add your specific infrastructure patterns
2. **diagnostic-workflows.md** - Add custom diagnostic procedures
3. **SKILL.md** - Adjust interpretation guidelines

After editing, repackage with:
```bash
python3 package_skill.py gasp-diagnostics/
```

## Skills vs MCP

This skill approach offers several advantages over a Model Context Protocol server:

| Feature | Skills | MCP |
|---------|--------|-----|
| **Idle cost** | ~100 tokens | ~1,300+ tokens |
| **Works today** | Yes | Waiting for Anthropic |
| **Incremental loading** | Yes (progressive) | No (all at once) |
| **Portable** | All Claude interfaces | Depends on support |
| **Maintenance** | Single .skill file | Separate server |
| **Teaching vs Fetching** | Teaches interpretation | Just fetches data |

## Why Bundle the Skill with GASP?

This skill demonstrates GASP's AI-first design philosophy in action. By including it in the distribution:

- **Users get immediate value** - Install GASP, symlink the skill, and start diagnosing with Claude
- **Living documentation** - The skill shows exactly how AI should interpret GASP's metrics
- **Batteries included** - No need to search for integration tools separately
- **Example for developers** - Shows how to build AI-native monitoring integrations

GASP is designed for AI consumption, and this skill is the reference implementation of that vision.

## More Information

- **GASP Repository:** https://github.com/AcceleratedIndustries/gasp
- **GASP Documentation:** See the main README in the repository
- **Claude Code:** https://claude.ai/code

## Future Plans

We're considering creating a skills marketplace for GASP and other infrastructure management skills. If you're interested or have skills to share, let us know!

## Contributing

Found a bug or have a suggestion? Open an issue on the GASP repository or submit a PR with skill improvements.

## License

This skill is released under the same license as GASP (check the repository for details).

---

**Built by Accelerated Industries**  
Making AI-optimized infrastructure management tools.
