# Architecture Overview

Deep dive into wp-migrate.sh internal architecture and design patterns.

## Project Structure

### Repository Layout
```
wp-migrate/
├── wp-migrate.sh              # Built single-file script (repo root)
├── wp-migrate.sh.sha256       # Checksum for built script
├── src/                       # Modular source files
│   ├── header.sh              # Shebang, set options, variable declarations
│   ├── lib/
│   │   ├── core.sh            # Core utilities (log, err, needs)
│   │   ├── adapters/          # Archive format adapters
│   │   │   ├── README.md      # Adapter development guide
│   │   │   ├── base.sh        # Shared adapter helper functions
│   │   │   ├── duplicator.sh  # Duplicator adapter
│   │   │   ├── jetpack.sh     # Jetpack Backup adapter
│   │   │   └── solidbackups.sh # Solid Backups adapter
│   │   └── functions.sh       # All other functions
│   └── main.sh                # Argument parsing and main() execution
├── dist/                      # Build artifacts (git-ignored)
│   └── wp-migrate.sh          # Intermediate build output
├── logs/                      # Runtime logs (created by script)
├── db-dumps/                  # Database exports (push mode)
├── db-backups/                # Database backups (archive mode)
├── db-imports/                # Database imports (on destination)
├── Makefile                   # Build system
├── test-wp-migrate.sh         # Test suite
├── .githooks/                 # Git hooks (pre-commit)
├── .gitmessage                # Commit message template
├── .github/
│   └── pull_request_template.md
├── CHANGELOG.md               # Version history
├── README.md                  # User documentation
└── LICENSE                    # MIT License
```

### Build System Architecture

**Source to Distribution Flow:**
```
src/header.sh          →
src/lib/core.sh        →
src/lib/adapters/      →  Concatenation  →  ShellCheck  →  wp-migrate.sh
src/lib/functions.sh   →                                →  + SHA256 checksum
src/main.sh            →
```

**Build Process (Makefile):**
1. **Test target**: Concatenates source → runs ShellCheck → validates
2. **Build target**: Runs test → copies to dist/ → copies to repo root → generates checksum
3. **Clean target**: Removes dist/ directory

**Why Modular Source?**
- Easier maintenance and code review
- Logical separation of concerns
- Simpler testing of individual components
- Better IDE support and navigation
- Clearer git diffs

## Core Components

### 1. Header (src/header.sh)

**Purpose**: Script initialization and global configuration

**Contents:**
- Shebang: `#!/usr/bin/env bash`
- Shell options: `set -Eeuo pipefail`
  - `-e`: Exit on error
  - `-E`: Inherit ERR trap
  - `-u`: Error on undefined variables
  - `-o pipefail`: Pipe failures propagate
- Default variable declarations
- Global state tracking
- Mode detection variables

**Key Variables:**
```bash
DEST_HOST=""              # Push mode: SSH destination
DEST_ROOT=""              # Push mode: Destination WP root
ARCHIVE_FILE=""           # Archive mode: Path to backup
ARCHIVE_TYPE=""           # Archive mode: Adapter override
MIGRATION_MODE=""         # Detected: "push", "archive", or "rollback"
DRY_RUN=false             # Preview mode flag
IMPORT_DB=true            # Auto-import database
SEARCH_REPLACE=true       # Perform URL search-replace
STELLARSITES_MODE=false   # Managed hosting compatibility
YES_MODE=false            # Skip confirmation prompts (v2.6.0)
QUIET_MODE=false          # Suppress progress indicators (v2.6.0)
```

### 2. Core Utilities (src/lib/core.sh)

**Purpose**: Fundamental functions used throughout the script

**Functions:**

**`err()`** - Error handling and exit
```bash
err() { printf "ERROR: %s\n" "$*" >&2; exit 1; }
```

**`log()`** - Logging to file and/or stdout
```bash
log() {
  # Logs to LOG_FILE and optionally to stdout
  # Handles dry-run mode (logs to /dev/null)
}
```

**`verbose()`** - Conditional verbose logging
```bash
verbose() {
  # Only logs if VERBOSE=true
  # Used for diagnostic information
}
```

**`trace()`** - Command tracing
```bash
trace() {
  # Shows exact command before execution
  # Enabled with --trace flag
}
```

**`needs()`** - Dependency checking
```bash
needs() {
  # Checks if command exists
  # Shows installation instructions if missing
  # Exits if required dependency not found
}
```

**`validate_url()`** - URL validation
```bash
validate_url() {
  # Ensures URL is well-formed
  # Used before search-replace operations
}
```

### 3. Archive Adapters (src/lib/adapters/)

**Purpose**: Pluggable format handlers for different backup plugins

**Adapter Interface**: Each adapter implements 5 required functions:

1. **`adapter_NAME_validate(archive_path)`**
   - Returns 0 if archive matches format, 1 otherwise
   - Checks file type and signature files

2. **`adapter_NAME_extract(archive_path, dest_dir)`**
   - Extracts archive to destination
   - Handles format-specific extraction (unzip, tar, etc.)

3. **`adapter_NAME_find_database(extract_dir)`**
   - Locates SQL file(s) in extracted archive
   - Echoes full path to database file

4. **`adapter_NAME_find_content(extract_dir)`**
   - Locates wp-content directory
   - Uses smart scoring to find best match

5. **`adapter_NAME_get_name()`**
   - Returns human-readable format name

**Base Helpers (adapter/base.sh):**
- `adapter_base_get_archive_type()` - Detect ZIP/TAR/TAR.GZ
- `adapter_base_archive_contains()` - Check for files in archive
- `adapter_base_find_best_wp_content()` - Score-based directory detection
- `adapter_base_score_wp_content()` - Score directory (0-3)

**Adapter Registry:**
Defined in [src/lib/functions.sh:11](../../../src/lib/functions.sh#L11):
```bash
AVAILABLE_ADAPTERS=("duplicator" "jetpack" "solidbackups")
```

**Auto-Detection Flow:**
```
For each adapter in AVAILABLE_ADAPTERS:
  ├─ Call adapter_NAME_validate(archive)
  ├─ If returns 0:
  │  └─ Use this adapter
  └─ If returns 1:
     └─ Try next adapter
```

### 4. Functions (src/lib/functions.sh)

**Purpose**: All migration workflow functions

**Categories** (51 functions total):

**WordPress CLI Wrappers:**
- `wp_local()` - Execute wp-cli on local WordPress installation
- `wp_remote()` - Execute wp-cli on remote server via SSH (single-line output)
- `wp_remote_full()` - Execute wp-cli on remote server (multi-line output)
- `wp_remote_has_command()` - Check if wp-cli command exists on remote

**SSH and Connectivity:**
- `setup_ssh_control()` - Create persistent SSH ControlMaster connection
- `cleanup_ssh_control()` - Close SSH control socket
- `ssh_cmd_string()` - Build SSH command string with custom options
- `ssh_run()` - Execute command on remote server via SSH

**WordPress Discovery:**
- `discover_wp_content_local()` - Get WP_CONTENT_DIR path on local system
- `discover_wp_content_remote()` - Get WP_CONTENT_DIR path on remote server

**Archive Adapter System:**
- `load_adapter()` - Source adapter file (duplicator/jetpack/solidbackups)
- `detect_adapter()` - Auto-detect archive format by trying all adapters
- `extract_archive()` - Call adapter's extract function
- `find_archive_database()` - Call adapter's find_database function
- `find_archive_wp_content()` - Call adapter's find_wp_content function
- `get_archive_format_name()` - Get human-readable adapter name
- `check_adapter_dependencies()` - Verify required commands available

**Archive Operations:**
- `check_disk_space_for_archive()` - Validate 3x archive size available
- `extract_archive_to_temp()` - Extract to temporary directory with validation
- `find_archive_database_file()` - Locate SQL dump(s) in extracted archive
- `find_archive_wp_content_dir()` - Locate wp-content directory in archive
- `cleanup_archive_temp()` - Remove temporary extraction directory

**URL Search-Replace Management:**
- `add_search_replace_pair()` - Add from→to URL pair to global list
- `json_escape_slashes()` - Escape slashes for JSON in search-replace
- `url_host_only()` - Extract hostname from URL
- `add_url_alignment_variations()` - Generate URL variations (http/https, www/non-www)

**Plugin/Theme Detection:**
- `detect_source_plugins()` - List plugins on source server
- `detect_source_themes()` - List themes on source server
- `detect_dest_plugins_push()` - List plugins on destination (push mode)
- `detect_dest_themes_push()` - List themes on destination (push mode)
- `detect_dest_plugins_local()` - List plugins on destination (archive mode)
- `detect_dest_themes_local()` - List themes on destination (archive mode)
- `detect_archive_plugins()` - List plugins in extracted archive
- `detect_archive_themes()` - List themes in extracted archive
- `array_diff()` - Compare arrays and return unique elements

**Plugin/Theme Restoration:**
- `restore_dest_content_push()` - Restore unique plugins/themes (push mode)
- `restore_dest_content_local()` - Restore unique plugins/themes (archive mode)

**Backup Operations:**
- `backup_remote_wp_content()` - Create timestamped wp-content backup on remote
- `find_latest_backup()` - Auto-detect latest database and wp-content backups (v2.6.0)

**Maintenance Mode:**
- `maint_remote()` - Toggle .maintenance file on remote server
- `maintenance_cleanup()` - Ensure maintenance mode disabled on exit
- `exit_cleanup()` - Cleanup handler (SSH control, maintenance, traps)

**Progress and UX (v2.6.0):**
- `has_pv()` - Check if pv (pipe viewer) is installed
- `run_with_progress()` - Execute command with progress bar if pv available
- `pipe_progress()` - Pipe data through pv for progress display
- `show_migration_preview()` - Display pre-migration summary and confirmation
- `show_push_mode_preview()` - Show push mode specific preview details
- `show_archive_mode_preview()` - Show archive mode specific preview details
- `rollback_migration()` - Restore from latest backups (v2.6.0)

**Utility:**
- `print_version()` - Display script version
- `print_usage()` - Display help text

### 5. Main Execution (src/main.sh)

**Purpose**: Argument parsing and orchestration

**Argument Parser:**
```bash
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest-host) DEST_HOST="$2"; shift 2 ;;
    --archive) ARCHIVE_FILE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    # ... etc
  esac
done
```

**Main Workflow:**
```bash
main() {
  # 1. Detect migration mode (push, archive, or rollback)
  # 2. Validate prerequisites
  # 3. Setup logging and traps
  # 4. Execute mode-specific workflow
  # 5. Cleanup and summary
}
```

## Execution Flow

### Push Mode Workflow

```
1. Preflight Checks
   ├─ Verify WordPress installation (source)
   ├─ Check dependencies (wp, rsync, ssh, gzip)
   ├─ Test SSH connectivity to destination
   └─ Verify WordPress installation (destination)

2. URL Detection
   ├─ Detect source home/siteurl
   ├─ Detect destination home/siteurl
   └─ Determine if search-replace needed

3. Setup
   ├─ Create log directory
   ├─ Setup SSH control connection
   ├─ Setup cleanup trap (ensure maintenance disabled)
   └─ Capture destination plugins/themes (if --preserve-dest-plugins)

4. Maintenance Mode
   ├─ Enable maintenance on source (unless --no-maint-source)
   └─ Enable maintenance on destination

5. Database Migration
   ├─ Export database on source (wp db export)
   ├─ Optionally gzip export (unless --no-gzip)
   ├─ Transfer to destination (rsync over SSH)
   ├─ Import on destination (if IMPORT_DB=true)
   └─ Perform search-replace (if SEARCH_REPLACE=true)

6. File Migration
   ├─ Backup destination wp-content (timestamped)
   ├─ Rsync wp-content (source → destination)
   │  └─ Exclude: object-cache.php
   │  └─ Exclude: mu-plugins/ (if --stellarsites)
   └─ Restore unique plugins/themes (if --preserve-dest-plugins)

7. Post-Migration
   ├─ Flush caches (wp cache flush, wp redis flush)
   ├─ Disable maintenance mode (both servers)
   └─ Cleanup SSH control connection

8. Summary
   ├─ Log migration completion
   └─ Show database dump location and import status
```

### Archive Mode Workflow

```
1. Preflight Checks
   ├─ Verify WordPress installation (destination)
   ├─ Check dependencies (wp, file, unzip/tar)
   └─ Verify archive file exists

2. Format Detection
   ├─ Auto-detect adapter (try each validator)
   └─ Or use explicit --archive-type

3. URL Capture
   └─ Capture destination home/siteurl (before import)

4. Disk Space Validation
   └─ Ensure 3x archive size available

5. Extraction
   ├─ Create temporary directory
   ├─ Call adapter extract function
   ├─ Detect database file (adapter find_database)
   └─ Detect wp-content directory (adapter find_content)

6. Setup
   ├─ Create log directory
   ├─ Setup cleanup trap
   └─ Capture destination plugins/themes (if --preserve-dest-plugins)

7. Maintenance Mode
   └─ Enable maintenance on destination

8. Database Backup
   └─ Export destination database (gzipped, timestamped)

9. wp-content Backup
   └─ Copy destination wp-content (timestamped)

10. Database Import
    ├─ Import database from archive
    ├─ Detect table prefix from imported data
    ├─ Align wp-config.php prefix if needed
    ├─ Detect imported home/siteurl
    └─ Perform search-replace (use captured destination URLs)

11. wp-content Replacement
    ├─ Remove destination wp-content
    ├─ Copy archive wp-content to destination
    │  └─ Exclude: object-cache.php
    │  └─ Exclude: mu-plugins/ (if --stellarsites)
    └─ Restore unique plugins/themes (if --preserve-dest-plugins)

12. Post-Import
    ├─ Flush caches (wp cache flush, wp redis flush)
    ├─ Disable maintenance mode
    └─ Cleanup temporary extraction directory

13. Summary
    ├─ Log import completion
    ├─ Show backup locations
    └─ Provide rollback commands
```

## Design Patterns

### 1. Dry-Run Safety

**Pattern**: All destructive operations check `DRY_RUN` flag

```bash
if [[ "$DRY_RUN" == true ]]; then
  log "Would perform operation..."
  return 0
fi

# Actually perform operation
perform_operation
```

**Guarantees**:
- No files created or modified
- No database changes
- No maintenance mode toggled
- No SSH connections (except test)
- Logs route to /dev/null

### 2. Error Handling

**Pattern**: Set `-e` and explicit error checking

```bash
set -Eeuo pipefail  # Exit on any error

# Explicit checks for important operations
if ! wp db import "$dump"; then
  err "Database import failed"
fi
```

**Cleanup Trap**:
```bash
cleanup() {
  # Ensure maintenance mode disabled
  # Close SSH connections
  # Remove temp files
}
trap cleanup EXIT
```

### 3. Logging Strategy

**Multi-Level Logging**:
- `err()` - Fatal errors, exit immediately
- `log()` - Important operations, always shown
- `verbose()` - Diagnostic info, shown with --verbose
- `trace()` - Command preview, shown with --trace

**Timestamped Log Files**:
```bash
LOG_FILE="logs/migrate-MODE-$(date +%Y%m%d-%H%M%S).log"
```

### 4. Adapter Pattern

**Plugin Architecture**: Archive formats are pluggable adapters

**Benefits**:
- Easy to add new formats
- Clear interface contract
- Shared helper functions
- Independent testing

**Conceptual Pattern**:
```bash
# Registry of available adapters (actual: AVAILABLE_ADAPTERS in src/lib/functions.sh:11)
AVAILABLE_ADAPTERS=("duplicator" "jetpack" "solidbackups")

# Auto-detection loop (actual: detect_adapter function)
for adapter in "${AVAILABLE_ADAPTERS[@]}"; do
  if "adapter_${adapter}_validate" "$ARCHIVE_FILE"; then
    ARCHIVE_ADAPTER="$adapter"
    break
  fi
done
```

**Actual Implementation**:
- Registry: `AVAILABLE_ADAPTERS=("duplicator" "jetpack" "solidbackups")` in src/lib/functions.sh:11
- Detection: `detect_adapter()` function (src/lib/functions.sh:31)

### 5. URL Alignment

**Two-Phase Approach**:

**Phase 1: Capture URLs Before Changes**
```bash
ORIGINAL_DEST_HOME_URL=$(wp option get home)
ORIGINAL_DEST_SITE_URL=$(wp option get siteurl)
```

**Phase 2: Restore After Import**
```bash
# Import changes URLs to source site
wp db import archive.sql

# Detect what was imported
IMPORTED_HOME=$(wp option get home)

# Restore destination URLs
wp search-replace "$IMPORTED_HOME" "$ORIGINAL_DEST_HOME_URL"
```

### 6. Backup Before Destroy

**Pattern**: Always backup before destructive operations

**Conceptual Pattern**:
```bash
# Database backup (via wp-cli)
wp db export "db-backups/backup-$(date +%Y%m%d-%H%M%S).sql.gz"

# wp-content backup (actual function: backup_remote_wp_content for push mode)
# Creates timestamped directory copy: wp-content.backup-YYYYMMDD-HHMMSS

# Then proceed with import/replacement
```

**Actual Implementation**:
- Push mode: `backup_remote_wp_content()` - Creates remote wp-content backup
- Archive mode: Direct wp-cli db export + mv wp-content to timestamped backup

### 7. Table Prefix Detection

**Conceptual Pattern**:
```bash
# Detect prefix from database (conceptual - actual implementation in src/main.sh)
TABLE_PREFIX=$(wp db prefix)

# Detect prefix from wp-config.php
CONFIG_PREFIX=$(wp config get table_prefix)

# Auto-align if different
if [[ "$TABLE_PREFIX" != "$CONFIG_PREFIX" ]]; then
  wp config set table_prefix "$TABLE_PREFIX"
fi
```

**Actual Implementation**:
- Detection: `wp db prefix` command (lines ~677-685 in src/main.sh)
- Alignment: `wp config set table_prefix` with verification and sed fallback

### 8. Plugin/Theme Preservation

**Conceptual Pattern**:
```bash
# Before migration - capture destination content
DEST_PLUGINS_BEFORE=($(wp plugin list --field=name))
DEST_THEMES_BEFORE=($(wp theme list --field=name))

# After migration - detect source content
SOURCE_PLUGINS=($(wp plugin list --field=name))
SOURCE_THEMES=($(wp theme list --field=name))

# Find unique to destination (using array_diff helper)
UNIQUE_DEST_PLUGINS=(plugins in BEFORE but not in SOURCE)
UNIQUE_DEST_THEMES=(themes in BEFORE but not in SOURCE)

# Restore from backup
for plugin in "${UNIQUE_DEST_PLUGINS[@]}"; do
  cp -a "wp-content.backup/plugins/$plugin" wp-content/plugins/
done

# Deactivate for safety
wp plugin deactivate "${UNIQUE_DEST_PLUGINS[@]}"
```

**Actual Implementation**:
- Detection functions: `detect_dest_plugins_push()`, `detect_dest_themes_push()`, `detect_source_plugins()`, `detect_source_themes()`, `detect_archive_plugins()`, `detect_archive_themes()`
- Diff function: `array_diff()` - Compare arrays and return unique elements
- Restoration: `restore_dest_content_push()`, `restore_dest_content_local()`

## State Management

### Global State Variables

**Migration Mode**:
```bash
MIGRATION_MODE="push"  # or "archive"
```

**Maintenance Mode Tracking**:
```bash
MAINT_LOCAL_ACTIVE=false
MAINT_REMOTE_ACTIVE=false
MAINT_REMOTE_HOST=""
MAINT_REMOTE_ROOT=""
```

**Cleanup Trap Uses These**:
```bash
cleanup() {
  if [[ "$MAINT_LOCAL_ACTIVE" == true ]]; then
    wp maintenance-mode deactivate
  fi
  if [[ "$MAINT_REMOTE_ACTIVE" == true ]]; then
    ssh "$MAINT_REMOTE_HOST" "cd '$MAINT_REMOTE_ROOT' && wp maintenance-mode deactivate"
  fi
}
```

### SSH Connection Pooling

**Persistent Connections**:
```bash
SSH_CONTROL_DIR="/tmp/wp-migrate-ssh-$$"
SSH_CONTROL_PATH="$SSH_CONTROL_DIR/master-%r@%h:%p"

setup_ssh_control() {
  mkdir -p "$SSH_CONTROL_DIR"
  ssh -o ControlMaster=auto \
      -o ControlPath="$SSH_CONTROL_PATH" \
      -o ControlPersist=600 \
      "$DEST_HOST" true
}
```

**Benefits**:
- Faster subsequent SSH operations
- Reuses authentication
- Single connection for entire migration

## Performance Optimizations

### 1. Database Compression

**Gzip During Transfer**:
```bash
wp db export - | gzip > dump.sql.gz
rsync dump.sql.gz dest:/
gunzip -c dump.sql.gz | wp db import -
```

**Savings**: ~10x reduction in transfer size

### 2. Rsync Compression

**Built-in Compression**:
```bash
rsync -avz  # -z enables compression
```

### 3. SSH Control Sockets

Single connection reused for all operations

### 4. Conditional Search-Replace

**Skip if Same Domain**:
```bash
if [[ "$SOURCE_HOME_URL" == "$DEST_HOME_URL" ]]; then
  log "URLs identical, skipping search-replace"
  URL_ALIGNMENT_REQUIRED=false
fi
```

### 5. Smart wp-content Scoring

**Avoid Full Directory Scan**:
```bash
score=0
[[ -d "$dir/plugins" ]] && ((score++))
[[ -d "$dir/themes" ]] && ((score++))
[[ -d "$dir/uploads" ]] && ((score++))
# Stop early if score == 3 (perfect match)
```

## Security Considerations

### 1. Shell Injection Prevention

**Always Quote Variables**:
```bash
# BAD - vulnerable to injection
ssh "$DEST_HOST" cd $DEST_ROOT

# GOOD - properly quoted
ssh "$DEST_HOST" "cd '$DEST_ROOT'"
```

### 2. File Path Validation

**Check for Dangerous Characters**:
```bash
if [[ "$path" =~ [^\w/.-] ]]; then
  err "Invalid path"
fi
```

### 3. Credential Protection

**No Passwords in Code**:
- Use SSH keys for authentication
- Rely on wp-cli for database credentials (reads from wp-config.php)

### 4. Maintenance Mode

**Prevent Concurrent Access**:
- Enables .maintenance file during migration
- Prevents data changes during sync

### 5. Rollback Instructions

**Always Provide Recovery Path**:
```bash
log "To rollback:"
log "  wp db import db-backups/backup-$timestamp.sql.gz"
log "  rm -rf wp-content && mv wp-content.backup-$timestamp wp-content"
```

**Automated Rollback (v2.6.0)**:
The `--rollback` flag automates the manual rollback process:
- Auto-detects latest timestamped backups in `db-backups/` and `wp-content.backup-*`
- Confirmation prompt (bypass with `--yes` for automation)
- Dry-run support for preview
- Works for archive mode migrations only (restores from local backups)

## v2.6.0 Feature Architecture

### 1. Migration Preview System

**Purpose**: Prevent migration mistakes by showing detailed summary before execution

**Implementation**:
```bash
show_migration_preview() {
  # Phase 1: Display summary header
  # Phase 2: Show source/destination details
  # Phase 3: Calculate and display statistics
  # Phase 4: List planned operations
  # Phase 5: Confirmation prompt
}
```

**Preview Components**:

**For Push Mode**:
- Source and destination URLs
- SSH connection details
- Database size estimate (via remote wp db size)
- File counts and rsync size estimate
- Planned operations list (backup, sync, search-replace, etc.)

**For Archive Mode**:
- Archive format and path
- Extracted size estimate
- Destination URL and paths
- Backup locations
- Planned operations list

**Non-Interactive Protection**:
```bash
if [[ ! -t 0 ]]; then
  err "This script requires a TTY for confirmation prompts. Add --yes flag for automation."
fi
```

**Bypass Options**:
- `--yes`: Skip confirmation for CI/CD
- `--dry-run`: Skip confirmation (preview only)

### 2. Rollback Command

**Purpose**: Easy recovery from failed or unwanted migrations

**Architecture**:
```bash
perform_rollback() {
  # Phase 1: Auto-detect latest backups
  # Phase 2: Validate backup existence
  # Phase 3: Show rollback preview
  # Phase 4: Confirmation prompt
  # Phase 5: Execute restoration
}
```

**Backup Detection Logic**:
```bash
# Find latest database backup
DB_BACKUP=$(find db-backups/ -name "backup-*.sql.gz" -type f | sort -r | head -1)

# Find latest wp-content backup
WP_CONTENT_BACKUP=$(find . -maxdepth 1 -name "wp-content.backup-*" -type d | sort -r | head -1)
```

**Features**:
- Auto-detection of latest timestamped backups
- Explicit backup specification via `--rollback-backup`
- Confirmation prompt (bypass with `--yes`)
- Dry-run support
- Non-interactive context protection

**Limitations**:
- Archive mode migrations only (local backups)
- Does not work for push mode (no local destination backups)

### 3. Progress Indicators

**Purpose**: User feedback for long-running operations

**Architecture**:

**Detection**:
```bash
if command -v pv &> /dev/null && [[ "$QUIET_MODE" != true ]]; then
  SHOW_PROGRESS=true
else
  SHOW_PROGRESS=false
fi
```

**Progress-Aware Operations**:

**Database Import**:
```bash
if [[ "$SHOW_PROGRESS" == true ]]; then
  pv "$DB_FILE" | wp db import -
else
  wp db import "$DB_FILE"
fi
```

**Archive Extraction**:
```bash
# ZIP archives with bsdtar (supports stdin for progress)
if command -v bsdtar &> /dev/null; then
  pv "$ARCHIVE_FILE" | bsdtar -xf - -C "$EXTRACT_DIR"
else
  # Fallback: unzip doesn't support stdin, no progress
  unzip -q "$ARCHIVE_FILE" -d "$EXTRACT_DIR"
fi

# TAR.GZ archives (GNU tar supports stdin)
pv "$ARCHIVE_FILE" | tar -xzf - -C "$EXTRACT_DIR"
```

**wp-content Sync**:
```bash
rsync -a --info=progress2 --delete "$SRC/" "$DEST/"
```

**Dependencies**:
- `pv` (pipe viewer) - optional, gracefully degrades if not installed
- `bsdtar` - optional, enables progress for ZIP archives

**Suppression**:
- `--quiet` flag disables all progress indicators

### 4. Non-Interactive Context Handling

**Problem**: Confirmation prompts fail silently in CI/CD, causing migrations to skip with exit 0

**Solution**: Detect non-interactive contexts and fail explicitly

**Detection**:
```bash
if [[ ! -t 0 ]]; then
  # stdin is not a TTY (CI/CD, cron, pipeline)
  err "This script requires a TTY for confirmation prompts. Add --yes flag for automation."
fi
```

**Impact**:
- Migration preview confirmation
- Rollback confirmation
- Prevents silent failures in automation

**Automation Support**:
- `--yes` flag bypasses all confirmation prompts
- Intended for CI/CD, cron jobs, non-interactive scripts

## Extension Points

### 1. Adding New Archive Formats

See [src/lib/adapters/README.md](../../../src/lib/adapters/README.md)

### 2. Custom rsync Options

**Via Command Line**:
```bash
--rsync-opt '--exclude=cache/'
--rsync-opt '--bwlimit=1000'
```

### 3. Custom SSH Options

**Via Command Line**:
```bash
--ssh-opt 'Port=2222'
--ssh-opt 'ProxyJump=bastion'
```

### 4. Hooks (Future Enhancement)

**Potential Hook Points**:
- Before/after database import
- Before/after wp-content sync
- Before/after search-replace
- On migration success/failure

## Debugging and Diagnostics

### Verbosity Levels

**Normal**: Essential operations only
```bash
./wp-migrate.sh <flags>
```

**Verbose**: Diagnostic information
```bash
./wp-migrate.sh <flags> --verbose
```

**Trace**: Every command shown
```bash
./wp-migrate.sh <flags> --trace
```

### Log File Analysis

**Location**:
```
logs/migrate-wpcontent-push-TIMESTAMP.log
logs/migrate-archive-import-TIMESTAMP.log
```

**Contents**:
- Timestamped operations
- Command outputs
- Error messages
- Rollback instructions

### Error Exit Codes

```bash
0   - Success
1   - General error (err() function)
2   - Dependency missing
3-9 - Reserved for future use
```

## Future Architecture Considerations

### Potential Enhancements

1. **Hook System**: Pre/post operation hooks
2. **Config Files**: YAML/TOML for complex migrations
3. **Progress Bars**: Visual feedback for long operations
4. **Parallel Transfers**: rsync multiple directories concurrently
5. **Incremental Backups**: Only backup changed files
6. **Remote Archive Mode**: Fetch archive from URL
7. **Multi-Site Support**: Handle WordPress multisite networks
8. **Custom Table Prefixes**: Allow prefix transformation
9. **Selective Sync**: Sync only plugins/themes/uploads
10. **Database Table Filtering**: Import only specific tables

### Backward Compatibility

**Deprecation Strategy**:
- Mark old flags as deprecated (e.g., --duplicator-archive)
- Maintain support for 2+ major versions
- Provide migration guide in CHANGELOG
- Show warnings when deprecated flags used

**Example**:
```bash
if [[ -n "$DUPLICATOR_ARCHIVE" ]]; then
  log "WARNING: --duplicator-archive is deprecated. Use --archive --archive-type=duplicator"
  ARCHIVE_FILE="$DUPLICATOR_ARCHIVE"
  ARCHIVE_TYPE="duplicator"
fi
```
