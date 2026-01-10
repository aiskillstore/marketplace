# gen-env Reference Implementation

Full TypeScript/Bun implementation for multi-instance localhost isolation.

## Complete Implementation

```typescript
#!/usr/bin/env bun
/**
 * gen-env - Generate isolated development environment
 *
 * Creates .localnet.env with unique instance identity, ports, and URLs
 * enabling multiple copies of the project to run simultaneously.
 */

import { existsSync, readFileSync, writeFileSync, unlinkSync } from "node:fs";
import { createServer } from "node:net";
import { basename, resolve } from "node:path";

// === Configuration ===

const ENV_FILE = ".localnet.env";
const LOCK_FILE = ".gen-env.lock";
const PORT_RANGE = { min: 49152, max: 65535 };
const PORT_CHECK_TIMEOUT_MS = 100;
const LOCKFILE_VERSION = 1;

// Project-specific: define ports needed
const PORT_KEYS = [
  "POSTGRES_PORT",
  "REDIS_PORT",
  "API_PORT",
  "WEB_PORT",
  "STORYBOOK_PORT",
] as const;

type PortKey = (typeof PORT_KEYS)[number];
type PortConfig = Record<PortKey, number>;

// === Types ===

interface InstanceConfig {
  name: string;
  composeName: string;
  dockerNetwork: string;
  volumePrefix: string;
  containerPrefix: string;
  host: string;
  ports: PortConfig;
  urls: Record<string, string>;
}

interface LockfileData {
  version: number;
  generatedAt: string;
  instance: InstanceConfig;
}

interface CliOptions {
  name: string | null;
  force: boolean;
  clean: boolean;
  random: boolean;
  help: boolean;
}

// === Name Validation ===

function sanitizeName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 63);
}

function validateName(name: string): { valid: boolean; sanitized: string; warning?: string } {
  if (!name) {
    return { valid: false, sanitized: "", warning: "Name is required" };
  }

  const sanitized = sanitizeName(name);

  if (!sanitized) {
    return { valid: false, sanitized: "", warning: "Name contains no valid characters" };
  }

  // Warn if sanitization changed the name
  if (sanitized !== name) {
    return {
      valid: true,
      sanitized,
      warning: `Name sanitized: '${name}' -> '${sanitized}'`,
    };
  }

  return { valid: true, sanitized };
}

// === Port Allocation ===

async function isPortFree(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const server = createServer();
    const timeout = setTimeout(() => {
      server.close();
      resolve(false);
    }, PORT_CHECK_TIMEOUT_MS);

    server.once("error", (err: NodeJS.ErrnoException) => {
      clearTimeout(timeout);
      server.close();
      // EADDRNOTAVAIL/EINVAL = interface unavailable (common in CI)
      if (err.code === "EADDRNOTAVAIL" || err.code === "EINVAL") {
        resolve(true);
        return;
      }
      resolve(err.code !== "EADDRINUSE");
    });

    server.once("listening", () => {
      clearTimeout(timeout);
      server.close();
      resolve(true);
    });

    // Check only IPv4 - dual-stack (::) claims IPv4 ports
    server.listen(port, "0.0.0.0");
  });
}

async function findFreePort(
  usedPorts: Set<number>,
  startOffset?: number
): Promise<number> {
  const start = PORT_RANGE.min + (startOffset ?? Math.floor(Math.random() * 1000));

  for (let port = start; port <= PORT_RANGE.max; port++) {
    if (usedPorts.has(port)) continue;
    if (await isPortFree(port)) return port;
  }

  // Wrap around if needed
  for (let port = PORT_RANGE.min; port < start; port++) {
    if (usedPorts.has(port)) continue;
    if (await isPortFree(port)) return port;
  }

  throw new Error(`No free ports in range ${PORT_RANGE.min}-${PORT_RANGE.max}`);
}

async function allocatePorts(
  options: { reuse?: PortConfig; random?: boolean }
): Promise<PortConfig> {
  const { reuse, random } = options;
  const ports: Partial<PortConfig> = {};
  const usedPorts = new Set<number>();

  // Determine starting offset
  const startOffset = random ? Math.floor(Math.random() * 10000) : 0;
  let nextOffset = startOffset;

  for (const key of PORT_KEYS) {
    // Try to reuse existing port if provided and still free
    if (reuse?.[key] && (await isPortFree(reuse[key]))) {
      ports[key] = reuse[key];
      usedPorts.add(reuse[key]);
    } else {
      const port = await findFreePort(usedPorts, nextOffset);
      ports[key] = port;
      usedPorts.add(port);
      nextOffset = port - PORT_RANGE.min + 1;
    }
  }

  return ports as PortConfig;
}

// === Instance Identity ===

function createInstanceConfig(name: string, ports: PortConfig): InstanceConfig {
  const sanitized = sanitizeName(name);
  const composeName = `localnet-${sanitized}`;
  const host = `${sanitized}.localhost`;

  return {
    name: sanitized,
    composeName,
    dockerNetwork: composeName,
    volumePrefix: composeName,
    containerPrefix: `${composeName}-`,
    host,
    ports,
    urls: {
      DATABASE_URL: `postgres://user:pass@localhost:${ports.POSTGRES_PORT}/dev`,
      REDIS_URL: `redis://localhost:${ports.REDIS_PORT}`,
      API_URL: `http://${host}:${ports.API_PORT}`,
      WEB_URL: `http://${host}:${ports.WEB_PORT}`,
      STORYBOOK_URL: `http://${host}:${ports.STORYBOOK_PORT}`,
    },
  };
}

// === Lockfile ===

function validateLockfileSchema(data: unknown): data is LockfileData {
  if (typeof data !== "object" || data === null) return false;
  const obj = data as Record<string, unknown>;

  // Check version
  if (obj.version !== LOCKFILE_VERSION) return false;

  // Check instance exists and has required fields
  if (typeof obj.instance !== "object" || obj.instance === null) return false;
  const instance = obj.instance as Record<string, unknown>;

  const requiredStrings = ["name", "composeName", "dockerNetwork", "volumePrefix", "containerPrefix", "host"];
  for (const field of requiredStrings) {
    if (typeof instance[field] !== "string" || !instance[field]) return false;
  }

  // Check ports object exists and has all required port keys
  if (typeof instance.ports !== "object" || instance.ports === null) return false;
  const ports = instance.ports as Record<string, unknown>;
  for (const key of PORT_KEYS) {
    if (typeof ports[key] !== "number" || ports[key] <= 0) return false;
  }

  return true;
}

function readLockfile(): LockfileData | null {
  if (!existsSync(LOCK_FILE)) return null;
  try {
    const data = JSON.parse(readFileSync(LOCK_FILE, "utf-8"));
    if (!validateLockfileSchema(data)) {
      console.error(`Error: Malformed lockfile at ${LOCK_FILE}`);
      console.error("Run with --force to regenerate, or delete the lockfile manually.");
      process.exit(1);
    }
    return data;
  } catch (err) {
    console.error(`Error: Failed to parse lockfile at ${LOCK_FILE}`);
    console.error(err instanceof Error ? err.message : String(err));
    console.error("Run with --force to regenerate, or delete the lockfile manually.");
    process.exit(1);
  }
}

function writeLockfile(instance: InstanceConfig): void {
  const data: LockfileData = {
    version: LOCKFILE_VERSION,
    generatedAt: new Date().toISOString(),
    instance,
  };
  writeFileSync(LOCK_FILE, JSON.stringify(data, null, 2) + "\n");
}

// === Environment Generation ===

function generateEnvContent(instance: InstanceConfig): string {
  const lines: string[] = [
    `# .localnet.env - generated by gen-env`,
    `# Instance: ${instance.name}`,
    `# Generated: ${new Date().toISOString()}`,
    `# Run \`gen-env <name>\` to refresh, \`gen-env <name> --force\` to regenerate ports`,
    "",
    "# === Instance Identity ===",
    `WORKSPACE_NAME=${instance.name}`,
    `COMPOSE_NAME=${instance.composeName}`,
    `COMPOSE_PROJECT_NAME=${instance.composeName}`,
    `DOCKER_NETWORK=${instance.dockerNetwork}`,
    `VOLUME_PREFIX=${instance.volumePrefix}`,
    `CONTAINER_PREFIX=${instance.containerPrefix}`,
    "",
    "# === Host (browser isolation) ===",
    `APP_HOST=${instance.host}`,
    `TILT_HOST=${instance.host}`,
    "",
    "# === Allocated Ports ===",
  ];

  for (const [key, value] of Object.entries(instance.ports)) {
    lines.push(`${key}=${value}`);
  }

  lines.push("", "# === Derived URLs ===");
  for (const [key, value] of Object.entries(instance.urls)) {
    lines.push(`${key}=${value}`);
  }

  return lines.join("\n") + "\n";
}

// === CLI ===

function parseArgs(args: string[]): CliOptions {
  const options: CliOptions = {
    name: null,
    force: false,
    clean: false,
    random: false,
    help: false,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case "--name":
      case "-n": {
        const nextArg = args[i + 1];
        if (!nextArg || nextArg.startsWith("-")) {
          console.error("Error: --name requires a value");
          console.error("Run gen-env --help for usage");
          process.exit(1);
        }
        options.name = args[++i];
        break;
      }
      case "--force":
      case "-f":
        options.force = true;
        break;
      case "--clean":
      case "-c":
        options.clean = true;
        break;
      case "--random":
      case "-r":
        options.random = true;
        break;
      case "--help":
      case "-h":
        options.help = true;
        break;
      default:
        // Unknown flag = error (fail fast)
        if (arg.startsWith("-")) {
          console.error(`Error: Unknown option '${arg}'`);
          console.error("Run gen-env --help for usage");
          process.exit(1);
        }
        // Positional argument = name
        if (!options.name) {
          options.name = arg;
        } else {
          console.error(`Error: Unexpected argument '${arg}'`);
          console.error("Run gen-env --help for usage");
          process.exit(1);
        }
    }
  }

  return options;
}

function printHelp(): void {
  const projectDir = basename(resolve("."));
  console.log(`
gen-env - Generate isolated development environment

Usage: gen-env --name <workspace> [options]
       gen-env <workspace> [options]

Arguments:
  <workspace>       Instance name (e.g., main, feature-x, bb-dev)

Options:
  -n, --name        Instance name (alternative to positional)
  -f, --force       Force regenerate even if lockfile exists
  -r, --random      Start port allocation from random offset
  -c, --clean       Remove generated files
  -h, --help        Show this help

Examples:
  gen-env bb-dev                    # Generate for workspace 'bb-dev'
  gen-env --name feature-x --force  # Force regenerate
  gen-env --clean                   # Remove generated files

Current directory: ${projectDir}
Generates: ${ENV_FILE}, ${LOCK_FILE}
`);
}

function printSummary(instance: InstanceConfig): void {
  console.log(`
Generated ${ENV_FILE} for instance: ${instance.name}

Identity:
  COMPOSE_PROJECT_NAME: ${instance.composeName}
  APP_HOST:             ${instance.host}

Ports:`);

  for (const [key, value] of Object.entries(instance.ports)) {
    console.log(`  ${key.padEnd(20)} ${value}`);
  }

  console.log(`
URLs:`);
  for (const [key, value] of Object.entries(instance.urls)) {
    console.log(`  ${key.padEnd(20)} ${value}`);
  }

  console.log(`
To activate: source ${ENV_FILE}
To clean up: docker compose -p ${instance.composeName} down -v
`);
}

async function clean(): Promise<void> {
  const files = [ENV_FILE, LOCK_FILE];
  const removed: string[] = [];

  for (const file of files) {
    if (existsSync(file)) {
      unlinkSync(file);
      removed.push(file);
    }
  }

  if (removed.length > 0) {
    console.log(`Removed: ${removed.join(", ")}`);
  } else {
    console.log("Nothing to clean");
  }
}

async function main(): Promise<void> {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) {
    printHelp();
    return;
  }

  if (options.clean) {
    await clean();
    return;
  }

  // Name is required for generation
  if (!options.name) {
    console.error("Error: --name is required");
    console.error("Usage: gen-env --name <workspace>");
    console.error("       gen-env <workspace>");
    console.error("\nRun gen-env --help for more information");
    process.exit(1);
  }

  // Validate and sanitize name (ISSUE-4: warn if sanitized)
  const validation = validateName(options.name);
  if (!validation.valid) {
    console.error(`Error: ${validation.warning}`);
    process.exit(1);
  }
  if (validation.warning) {
    console.warn(`Warning: ${validation.warning}`);
  }
  const name = validation.sanitized;

  // Check existing lockfile
  const existing = readLockfile();

  if (existing && !options.force) {
    if (existing.instance.name !== name) {
      console.error(`Warning: Lockfile has different name '${existing.instance.name}'`);
      console.error(`Requested name: '${name}'`);
      console.error("Use --force to regenerate with new name");
      process.exit(1);
    }

    // Verify existing ports are still available before reusing
    console.log(`Checking port availability for '${name}'...`);
    let portsValid = true;
    for (const [key, port] of Object.entries(existing.instance.ports)) {
      if (!(await isPortFree(port))) {
        console.warn(`Warning: Port ${port} (${key}) is now in use`);
        portsValid = false;
      }
    }

    if (!portsValid) {
      console.log("Some ports are occupied. Reallocating...");
      // Fall through to reallocation below
    } else {
      // Reuse existing config but always regenerate env file
      console.log(`Reusing existing configuration for '${name}'`);
      writeFileSync(ENV_FILE, generateEnvContent(existing.instance));
      console.log(`Use --force to regenerate ports`);
      printSummary(existing.instance);
      return;
    }
  }

  // Allocate ports (ISSUE-1: --force means fresh allocation, no reuse)
  console.log(`Allocating ports for '${name}'...`);
  const ports = await allocatePorts({
    // Only reuse ports if NOT forcing and lockfile exists with same name
    reuse: (!options.force && existing?.instance.name === name)
      ? existing.instance.ports
      : undefined,
    random: options.random,
  });

  // Create instance config
  const instance = createInstanceConfig(name, ports);

  // Write files
  writeLockfile(instance);
  writeFileSync(ENV_FILE, generateEnvContent(instance));

  printSummary(instance);
}

main().catch((err: unknown) => {
  console.error("gen-env failed:", err instanceof Error ? err.message : String(err));
  process.exit(1);
});
```

## Shell Fallback

For projects without Bun/Node:

```bash
#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=".localnet.env"
LOCK_FILE=".gen-env.lock"
PORT_MIN=49152
PORT_MAX=65535

# === Helpers ===

die() { echo "Error: $1" >&2; exit 1; }

sanitize_name() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9-' '-' | sed 's/^-//;s/-$//' | cut -c1-63
}

is_port_free() {
  ! nc -z localhost "$1" 2>/dev/null
}

find_free_port() {
  local port=${1:-$PORT_MIN}
  # Clamp starting port to valid range
  [[ $port -gt $PORT_MAX ]] && port=$PORT_MIN
  while ! is_port_free "$port"; do
    ((port++))
    [[ $port -gt $PORT_MAX ]] && die "No free ports in range $PORT_MIN-$PORT_MAX"
  done
  echo "$port"
}

# === Lockfile (POSIX-compatible parsing) ===

validate_lockfile() {
  [[ -f "$LOCK_FILE" ]] || return 1

  # Check version field
  local version
  version=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p' "$LOCK_FILE" | head -1)
  [[ "$version" == "1" ]] || return 1

  # Check name exists and is non-empty
  local name
  name=$(sed -n 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$LOCK_FILE" | head -1)
  [[ -n "$name" ]] || return 1

  # Check all required ports exist and are valid numbers
  local port
  for key in POSTGRES_PORT REDIS_PORT API_PORT WEB_PORT; do
    port=$(sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p" "$LOCK_FILE" | head -1)
    [[ -n "$port" && "$port" -gt 0 ]] 2>/dev/null || return 1
  done

  return 0
}

read_lockfile_name() {
  [[ -f "$LOCK_FILE" ]] || return 1
  # Extract "name": "value" using sed (works on BSD/GNU)
  local value
  value=$(sed -n 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$LOCK_FILE" | head -1)
  [[ -n "$value" ]] || return 1
  echo "$value"
}

read_lockfile_port() {
  local key="$1"
  [[ -f "$LOCK_FILE" ]] || return 1
  # Extract "KEY": 12345 using sed (works on BSD/GNU)
  local value
  value=$(sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p" "$LOCK_FILE" | head -1)
  [[ -n "$value" ]] || return 1
  echo "$value"
}

write_lockfile() {
  local name="$1" pg="$2" redis="$3" api="$4" web="$5"
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  cat > "$LOCK_FILE" <<EOF
{
  "version": 1,
  "generatedAt": "${timestamp}",
  "instance": {
    "name": "${name}",
    "ports": {
      "POSTGRES_PORT": ${pg},
      "REDIS_PORT": ${redis},
      "API_PORT": ${api},
      "WEB_PORT": ${web}
    }
  }
}
EOF
}

# === Main ===

main() {
  local name="" force=false clean=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name|-n)
        [[ -z "${2:-}" || "$2" == -* ]] && die "--name requires a value"
        name="$2"; shift 2 ;;
      --force|-f) force=true; shift ;;
      --clean|-c) clean=true; shift ;;
      --help|-h) usage; exit 0 ;;
      -*) die "Unknown option: $1" ;;
      *)
        [[ -n "$name" ]] && die "Unexpected argument: $1"
        name="$1"; shift ;;
    esac
  done

  if $clean; then
    rm -f "$ENV_FILE" "$LOCK_FILE"
    echo "Cleaned"
    exit 0
  fi

  [[ -z "$name" ]] && die "Name required: gen-env --name <workspace>"

  local sanitized
  sanitized=$(sanitize_name "$name")
  [[ -z "$sanitized" ]] && die "Name contains no valid characters"
  if [[ "$sanitized" != "$name" ]]; then
    echo "Warning: Name sanitized: '$name' -> '$sanitized'" >&2
  fi
  name="$sanitized"
  local compose_name="localnet-${name}"
  local host="${name}.localhost"

  # Check existing lockfile
  if [[ -f "$LOCK_FILE" ]] && ! $force; then
    # Validate lockfile schema before attempting to read
    if ! validate_lockfile; then
      die "Malformed lockfile at $LOCK_FILE. Run with --force to regenerate, or delete it manually."
    fi

    local existing_name
    existing_name=$(read_lockfile_name)

    if [[ "$existing_name" != "$name" ]]; then
      die "Lockfile has different name '$existing_name'. Use --force to regenerate."
    fi

    # Reuse existing ports from lockfile
    local postgres_port redis_port api_port web_port
    postgres_port=$(read_lockfile_port "POSTGRES_PORT")
    redis_port=$(read_lockfile_port "REDIS_PORT")
    api_port=$(read_lockfile_port "API_PORT")
    web_port=$(read_lockfile_port "WEB_PORT")

    echo "Reusing existing configuration for '${name}'"
    generate_env "$name" "$compose_name" "$host" "$postgres_port" "$redis_port" "$api_port" "$web_port"
    echo "Use --force to regenerate ports"
    return
  fi

  # Allocate fresh ports
  echo "Allocating ports for '${name}'..."
  local postgres_port redis_port api_port web_port
  postgres_port=$(find_free_port $PORT_MIN)
  redis_port=$(find_free_port $((postgres_port + 1)))
  api_port=$(find_free_port $((redis_port + 1)))
  web_port=$(find_free_port $((api_port + 1)))

  # Write lockfile and env
  write_lockfile "$name" "$postgres_port" "$redis_port" "$api_port" "$web_port"
  generate_env "$name" "$compose_name" "$host" "$postgres_port" "$redis_port" "$api_port" "$web_port"
}

generate_env() {
  local name="$1" compose_name="$2" host="$3"
  local postgres_port="$4" redis_port="$5" api_port="$6" web_port="$7"

  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  cat > "$ENV_FILE" <<EOF
# .localnet.env - generated by gen-env
# Instance: ${name}
# Generated: ${timestamp}
# Run \`gen-env <name>\` to refresh, \`gen-env <name> --force\` to regenerate ports

# === Instance Identity ===
WORKSPACE_NAME=${name}
COMPOSE_NAME=${compose_name}
COMPOSE_PROJECT_NAME=${compose_name}
DOCKER_NETWORK=${compose_name}
VOLUME_PREFIX=${compose_name}
CONTAINER_PREFIX=${compose_name}-

# === Host (browser isolation) ===
APP_HOST=${host}
TILT_HOST=${host}

# === Allocated Ports ===
POSTGRES_PORT=${postgres_port}
REDIS_PORT=${redis_port}
API_PORT=${api_port}
WEB_PORT=${web_port}

# === Derived URLs ===
DATABASE_URL=postgres://user:pass@localhost:${postgres_port}/dev
REDIS_URL=redis://localhost:${redis_port}
API_URL=http://${host}:${api_port}
WEB_URL=http://${host}:${web_port}
EOF

  echo "Generated ${ENV_FILE} for '${name}'"
  echo "  APP_HOST: ${host}"
  echo "  WEB_URL:  http://${host}:${web_port}"
}

usage() {
  cat <<EOF
gen-env - Generate isolated development environment

Usage: gen-env --name <workspace> [options]

Options:
  -n, --name    Instance name (required)
  -f, --force   Force regenerate ports
  -c, --clean   Remove generated files
  -h, --help    Show help
EOF
}

main "$@"
```

## Project Setup

### 1. Create bin directory

```bash
mkdir -p bin
```

### 2. Save script

```bash
# TypeScript version
cat > bin/gen-env << 'EOF'
#!/usr/bin/env bun
// ... implementation above ...
EOF
chmod +x bin/gen-env

# Or shell version
cat > bin/gen-env << 'EOF'
#!/usr/bin/env bash
# ... implementation above ...
EOF
chmod +x bin/gen-env
```

### 3. Configure direnv

```bash
# .envrc
PATH_add bin

# Auto-load generated env (dotenv_if_exists exports KEY=VALUE files)
dotenv_if_exists .localnet.env
```

### 4. Update .gitignore

```gitignore
# Generated by gen-env
.localnet.env
.gen-env.lock
```

### 5. First run

```bash
direnv allow
gen-env bb-dev
```

## Extending for Your Project

### Custom Port Keys

Edit `PORT_KEYS` array:

```typescript
const PORT_KEYS = [
  // Database
  "POSTGRES_PORT",
  "REDIS_PORT",

  // Your services
  "AUTH_PORT",
  "API_PORT",
  "WORKER_PORT",
  "WEB_PORT",

  // Dev tools
  "STORYBOOK_PORT",
  "SWAGGER_PORT",
] as const;
```

### Custom URL Derivation

Edit `createInstanceConfig`:

```typescript
urls: {
  DATABASE_URL: `postgres://user:pass@localhost:${ports.POSTGRES_PORT}/dev`,
  REDIS_URL: `redis://localhost:${ports.REDIS_PORT}`,
  AUTH_URL: `http://${host}:${ports.AUTH_PORT}`,
  API_URL: `http://${host}:${ports.API_PORT}`,
  // Add your URLs
}
```

### Project-Specific Base Env

Merge with base configuration:

```typescript
// Load and resolve base env files
const BASE_FILES = ["env/base.env", "env/local.env"];

function loadBaseEnv(): Record<string, string> {
  const env: Record<string, string> = {};
  for (const file of BASE_FILES) {
    if (!existsSync(file)) continue;
    for (const line of readFileSync(file, "utf-8").split("\n")) {
      const match = line.match(/^([A-Z_][A-Z0-9_]*)=(.*)$/);
      if (match) env[match[1]] = resolveValue(match[2], env);
    }
  }
  return env;
}
```
