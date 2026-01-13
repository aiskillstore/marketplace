# Network Security Setup - Quick Start

Configure Claude Code sandbox network isolation with trusted domains and access policies.

## Quick Start

```bash
# 1. Audit requirements
Review network-security/docs/NETWORK-REQUIREMENTS.md

# 2. Configure network
./network-security/config/configure-network.sh

# 3. Test policies
./network-security/tests/network-tests.sh

# 4. Monitor
tail -f /var/log/firewall.log
```

## What This Skill Does

- Audit network requirements
- Design security policies
- Implement network isolation
- Test access controls
- Document configuration

## Duration

25-45 minutes

## See Also

- Full SOP: [SKILL.md](SKILL.md)
- Detailed Process: [PROCESS.md](PROCESS.md)
