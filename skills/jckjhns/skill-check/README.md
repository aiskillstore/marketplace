# SkillCheck 🎲

**Roll for quality. Comprehensive testing and validation for [Agent Skills](https://agentskills.io).**

Every adventurer knows you don't walk into a dungeon without checking your gear. SkillCheck does the same for Agent Skills — it audits a skill directory, understands every moving part, and generates targeted tests to verify the skill works as advertised. Cross-reference mismatches, security red flags, best practice violations, broken I/O contracts — if there's a trap, SkillCheck finds it.

## What it tests

| Category | What's checked |
|----------|---------------|
| **Static integrity** | File existence, orphan detection, script syntax, dependency availability, path validation |
| **Asset validation** | Image/document/PDF/font validity, template placeholder detection |
| **Cross-references** | Script argument mismatches between SKILL.md and actual code |
| **Security** | Shell injection, eval/exec, hardcoded credentials, path traversal, risky instructions |
| **Best practices** | 22 checks covering spec compliance, structure, description quality, writing quality, efficiency |
| **Eval regression** | Re-runs the skill's own test cases to catch regressions |
| **I/O contracts** | Generates mock input files, runs the skill, verifies output format and structure |
| **Multi-skill deps** | Detects and verifies references to other skills |
| **Edge cases** | Empty, malformed, large, and special-character inputs (Deep Check) |
| **End-to-end** | Simulates realistic user prompts through the full workflow (Deep Check) |

## Choose your difficulty

| Depth | DC | What it covers |
|-------|-----|---------------|
| **Quick** | Easy encounter | Static analysis — structure, syntax, integrity, security, best practices |
| **Standard** | Medium encounter | Static + script execution + happy-path I/O + eval regression |
| **Deep** | Boss fight | Everything — edge cases, mock files, e2e workflows, stress testing |

## Installation

SkillCheck is an Agent Skill — it works anywhere skills are supported.

### Claude.ai

Upload the `skill-check` folder to your skills:
1. Download or clone this repository
2. Upload the `skill-check` directory as a custom skill

### Claude Code

Copy to your skills directory:

```bash
# Personal skills
cp -r skill-check ~/.claude/skills/

# Project skills
cp -r skill-check .claude/skills/
```

Or install from a plugin marketplace if available:

```
/plugin install skill-check@<marketplace>
```

### Other platforms

Copy the `skill-check` folder into whatever directory your agent reads skills from. The skill follows the [Agent Skills open standard](https://agentskills.io) and should work on any compatible platform.

## Usage

Just ask:

- *"Test my skill"*
- *"Run SkillCheck on the skill at /path/to/skill"*
- *"Quick check the chart skill"*
- *"Does my skill follow best practices?"*
- *"Is this skill secure?"*
- *"Find problems in my skill"*

SkillCheck will locate the skill, run discovery, present a test plan, execute the tests, and deliver the verdict.

### Example report

```
╔══════════════════════════════════════════╗
║  SkillCheck Report: csv-chart            ║
╠══════════════════════════════════════════╣
║  Static Tests:     8/9   passed    ⚠     ║
║  Eval Regression:  0/1   passed    ⚠     ║
║  Script Tests:     2/3   passed    ⚠     ║
║  I/O Tests:        2/2   passed    ✓     ║
║  Workflow Tests:   3/3   passed    ✓     ║
╠══════════════════════════════════════════╣
║  Overall:          15/18  (83.3%)        ║
║  Verdict:  MOSTLY HEALTHY                ║
╚══════════════════════════════════════════╝
```

See [references/example-run.md](references/example-run.md) for a complete worked example.

### The verdict scale

| Verdict | Pass rate | Translation |
|---------|-----------|-------------|
| **HEALTHY** | 100% | Natural 20. Ship it. |
| **MOSTLY HEALTHY** | 80-99% | Passed with minor scratches. Fix the rough edges. |
| **NEEDS ATTENTION** | 50-79% | Failed the check. Significant issues to address. |
| **CRITICAL** | <50% | Critical fail. Back to the workshop. |

## Project structure

```
skill-check/
├── SKILL.md                        # Main skill instructions
├── README.md                       # This file
├── LICENSE                         # MIT License
├── CONTRIBUTING.md                 # Contribution guidelines
├── .gitignore
├── references/
│   ├── quick-check.md              # Quick Check test definitions
│   ├── standard-check.md           # Standard Check test definitions
│   ├── deep-check.md               # Deep Check test definitions
│   ├── best-practices.md           # 22 best practice checks (agentskills.io aligned)
│   ├── mock-files.md               # Mock file generation for every supported type
│   ├── report-format.md            # Report template and collapsing rules
│   ├── eval-schema.md              # evals.json format reference
│   ├── example-run.md              # Complete worked example (Standard Check)
│   ├── finding-the-skill.md        # How to locate a skill when no path given
│   └── incomplete-skills.md        # Graceful handling of half-written skills
└── evals/
    ├── evals.json                  # 5 test cases for SkillCheck itself
    └── files/                      # Test fixture skills
        ├── healthy-skill/          # Clean skill — should pass everything
        ├── broken-skill/           # Cross-ref mismatches, missing files, contradictions
        ├── incomplete-skill/       # Half-written with TODOs and stubs
        └── insecure-skill/         # Security red flags (test fixture only)
```

## Cross-platform compatibility

SkillCheck validates skills against the [Agent Skills open standard](https://agentskills.io), not just Claude's conventions. Best practice checks include spec compliance validation (name format, description length, portability fields) so skills tested with SkillCheck work across:

- Claude.ai, Claude Code, Claude API
- OpenAI Codex CLI and ChatGPT
- GitHub Copilot / VS Code
- fast-agent and other compatible platforms

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new test types, improving existing checks, or submitting bug fixes. No experience required — just roll initiative.

## License

[MIT](LICENSE)
