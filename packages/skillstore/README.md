# skillstore

CLI and SDK for installing AI skills from [skillstore.io](https://skillstore.io) - the skills marketplace for Claude Code, Codex, and Claude.

## Installation

```bash
# Use directly with npx (recommended)
npx skillstore install <skill-or-plugin>

# Or install globally
npm install -g skillstore
```

## CLI Usage

### Install a Single Skill

```bash
npx skillstore install <skill-slug>
```

Example:
```bash
npx skillstore install react-component-generator
```

### Install a Plugin (Skill Collection)

Use the `@` prefix to install all skills from a plugin:

```bash
npx skillstore install @<plugin-slug>
```

Example:
```bash
npx skillstore install @frontend-essentials
```

### Options

| Option | Description |
|--------|-------------|
| `--dir <path>` | Installation directory (default: `.claude/skills`) |
| `--overwrite` | Overwrite existing files |
| `--skip-verify` | Skip manifest signature verification (plugins only) |
| `--dry-run` | Preview without writing files |

### Plugin Commands

#### List Available Plugins

```bash
npx skillstore plugin list [options]
```

Options:
- `--type <type>` - Filter by type: `curated`, `scenario`, or `user`
- `--pricing <pricing>` - Filter by pricing: `free` or `paid`
- `--limit <n>` - Number of plugins to show (default: 10)
- `--page <n>` - Page number for pagination

#### Get Plugin Info

```bash
npx skillstore plugin info <slug>
```

#### Install Plugin (Alternative)

```bash
npx skillstore plugin install <slug> [options]
```

## SDK Usage

Use the SDK to integrate skillstore into your own tools:

```typescript
import {
  fetchSkillInfo,
  downloadSkillZip,
  fetchManifest,
  fetchPluginList,
  getPluginConfig,
} from 'skillstore';

// Get default configuration
const config = getPluginConfig({
  installDir: '.claude/skills',
  timeout: 30000,
});

// Fetch skill info
const skill = await fetchSkillInfo(config, 'my-skill');
console.log(skill.name, skill.description);

// Download skill as ZIP
const zipBuffer = await downloadSkillZip(config, 'my-skill');

// List available plugins
const plugins = await fetchPluginList(config, {
  type: 'curated',
  pricing: 'free',
  limit: 20,
});

// Fetch plugin manifest for installation
const manifest = await fetchManifest(config, 'my-plugin');
```

### SDK Exports

#### Plugin API

```typescript
import {
  fetchManifest,
  fetchPluginInfo,
  fetchPluginList,
  downloadSkill,
  reportInstallation,
  reportSkillTelemetry,
  PluginApiError,
} from 'skillstore';
```

#### Skill API

```typescript
import {
  fetchSkillInfo,
  downloadSkillZip,
  SkillApiError,
} from 'skillstore';
```

#### Configuration

```typescript
import {
  getPluginConfig,
  getSkillPath,
  DEFAULT_INSTALL_DIR,
  API_BASE_URL,
} from 'skillstore';
```

#### Verification

```typescript
import {
  verifyManifest,
  verifyManifestSignature,
  verifyContentHash,
} from 'skillstore';
```

#### Download Manager

```typescript
import {
  downloadAllSkills,
  printDownloadSummary,
} from 'skillstore';
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SKILLSTORE_API_URL` | Custom API base URL (default: `https://skillstore.io/api`) |
| `SKILLSTORE_VERIFY_KEY` | Override built-in manifest verification key (optional) |
| `DEBUG` | Enable debug logging |

> **Note**: Manifest signature verification is enabled by default using a built-in key. You don't need to configure anything for verification to work.

## Directory Structure

Skills are installed to `.claude/skills/` by default:

```
.claude/
└── skills/
    ├── skill-one.md
    ├── skill-two.md
    └── ...
```

## Requirements

- Node.js >= 18.0.0

## License

MIT
