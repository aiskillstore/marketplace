# Testing Guide

Comprehensive testing guide for wp-migrate.sh development and quality assurance.

## Quick Start

### Run All Tests
```bash
# Using Makefile (recommended)
make test

# Or run test script directly
./test-wp-migrate.sh
```

### Build and Test
```bash
# Build from source and run tests
make build

# This automatically runs shellcheck before building
```

## Testing Philosophy

wp-migrate.sh follows these testing principles:

1. **ShellCheck-clean**: All code must pass shellcheck with zero errors/warnings
2. **Dry-run safe**: All tests use --dry-run to avoid requiring real WordPress installations
3. **Fast feedback**: Tests run quickly without heavy dependencies
4. **CI-ready**: Tests can run in automated environments

## Test Types

### 1. ShellCheck Linting

**Purpose**: Catch shell script errors, security issues, and best practice violations

**Run:**
```bash
# Via Makefile (tests complete script)
make test

# Direct shellcheck
shellcheck wp-migrate.sh

# Test modular source before building
shellcheck src/header.sh
shellcheck src/lib/core.sh
shellcheck src/lib/functions.sh
shellcheck src/lib/adapters/*.sh
shellcheck src/main.sh
```

**What it catches:**
- Syntax errors
- Unquoted variables
- Security vulnerabilities (e.g., command injection)
- Portability issues
- Best practice violations

**Install ShellCheck:**
```bash
# macOS
brew install shellcheck

# Ubuntu/Debian
sudo apt-get install shellcheck

# CentOS/RHEL
sudo yum install ShellCheck

# From source
https://github.com/koalaman/shellcheck
```

### 2. Argument Parsing Tests

**Purpose**: Verify command-line argument validation and help text

**Test script**: [test-wp-migrate.sh](../../../test-wp-migrate.sh)

**Tests include:**
- Help message displays correctly
- Missing required arguments detected
- Migration mode validation
- WordPress root validation
- Dependency checking

**Run:**
```bash
./test-wp-migrate.sh
```

**Example output:**
```
Test: Help message displays
✓ Help message displays without error

Test: Missing required arguments
✓ Validates migration mode is specified
✓ Validates WordPress root exists

Test: Dependency checking
✓ Validates WordPress root before proceeding

Test: ShellCheck linting
✓ ShellCheck passes with zero errors/warnings

Test Summary
Tests run: 5
Passed: 5
Failed: 0
```

### 3. Dry-Run Tests

**Purpose**: Test migration workflow without making changes

**Push mode dry-run:**
```bash
./wp-migrate.sh \
  --dest-host fake@example.com \
  --dest-root /var/www/html \
  --dry-run --verbose
```

**Archive mode dry-run:**
```bash
./wp-migrate.sh \
  --archive /path/to/test-backup.zip \
  --dry-run --verbose
```

**What it tests:**
- Argument parsing
- Validation logic
- Workflow sequence
- Error handling
- Output formatting

**Safety**: Dry-run mode guarantees:
- No files created or modified
- No maintenance mode toggled
- No database operations executed
- No SSH connections (push mode)
- Output only describes what would happen

### 4. Build System Tests

**Purpose**: Verify modular source builds correctly

**Run:**
```bash
# Clean build
make clean
make build

# Verify checksum updated
cat wp-migrate.sh.sha256

# Verify built script is executable
./wp-migrate.sh --version
```

**What it tests:**
- Source concatenation
- ShellCheck validation
- Checksum generation
- File permissions

## Testing Workflow

### During Development

**1. Make changes in src/ files:**
```bash
vim src/lib/functions.sh
```

**2. Build and test:**
```bash
make build
```

This automatically:
- Runs shellcheck on complete script
- Concatenates source files
- Generates checksum
- Copies to repo root

**3. Run test suite:**
```bash
./test-wp-migrate.sh
```

**4. Test specific scenarios:**
```bash
# Test push mode argument parsing
./wp-migrate.sh --dest-host test@example.com --dest-root /tmp --dry-run

# Test archive detection
./wp-migrate.sh --archive /path/to/backup.zip --dry-run --verbose
```

### Before Committing

**Pre-commit checklist:**

1. **ShellCheck passes:**
   ```bash
   make test
   ```

2. **Test suite passes:**
   ```bash
   ./test-wp-migrate.sh
   ```

3. **Built script updated:**
   ```bash
   git status
   # Should show changes to both:
   # - src/ files
   # - wp-migrate.sh
   # - wp-migrate.sh.sha256
   ```

4. **CHANGELOG.md updated:**
   ```bash
   git diff CHANGELOG.md
   ```

**Pre-commit hook:**
Install the git hook to enforce this automatically:
```bash
ln -s ../../.githooks/pre-commit .git/hooks/pre-commit
```

The hook will block commits if:
- src/ files modified but wp-migrate.sh not updated
- wp-migrate.sh modified but checksum not updated

### Before Pull Requests

**PR checklist:**

1. All tests pass:
   ```bash
   make test
   ./test-wp-migrate.sh
   ```

2. Dry-run tests for both modes work:
   ```bash
   ./wp-migrate.sh --dest-host test@example --dest-root /tmp --dry-run
   ./wp-migrate.sh --archive /path/to/backup.zip --dry-run
   ```

3. CHANGELOG.md updated under [Unreleased]

4. Documentation updated if needed

5. Commit messages follow template format

## Manual Testing Scenarios

### Testing Push Mode

**Prerequisites:**
- Two WordPress installations (source and destination)
- SSH access from source to destination
- wp-cli installed on both servers

**Basic push test:**
```bash
# On source server
cd /var/www/source-site
./wp-migrate.sh \
  --dest-host user@dest-server \
  --dest-root /var/www/dest-site \
  --dry-run --verbose
```

**Test URL alignment:**
```bash
# Check detected URLs
./wp-migrate.sh \
  --dest-host user@dest \
  --dest-root /var/www/dest \
  --dry-run --verbose | grep -i "url"
```

**Test custom SSH options:**
```bash
./wp-migrate.sh \
  --dest-host user@dest \
  --dest-root /var/www/dest \
  --ssh-opt 'Port=2222' \
  --dry-run
```

**Test plugin preservation:**
```bash
./wp-migrate.sh \
  --dest-host user@dest \
  --dest-root /var/www/dest \
  --preserve-dest-plugins \
  --dry-run --verbose
```

**Test StellarSites mode:**
```bash
./wp-migrate.sh \
  --dest-host user@stellarsites \
  --dest-root /var/www/site \
  --stellarsites \
  --dry-run --verbose
```

### Testing Archive Mode

**Prerequisites:**
- WordPress installation (destination)
- Test backup archives (Duplicator, Jetpack, Solid Backups)
- wp-cli installed

**Test Duplicator archive:**
```bash
./wp-migrate.sh \
  --archive /path/to/duplicator-backup.zip \
  --dry-run --verbose
```

**Test Jetpack archive:**
```bash
# ZIP format
./wp-migrate.sh \
  --archive /path/to/jetpack-backup.zip \
  --dry-run --verbose

# TAR.GZ format
./wp-migrate.sh \
  --archive /path/to/jetpack-backup.tar.gz \
  --dry-run --verbose
```

**Test Solid Backups archive:**
```bash
./wp-migrate.sh \
  --archive /path/to/solidbackups-full.zip \
  --dry-run --verbose
```

**Test format detection:**
```bash
# Auto-detect
./wp-migrate.sh --archive /path/to/unknown.zip --dry-run --verbose

# Explicit format
./wp-migrate.sh --archive /path/to/backup.zip --archive-type duplicator --dry-run
```

**Test disk space validation:**
```bash
# Check if script properly validates space (needs 3x archive size)
df -h
ls -lh /path/to/archive.zip
./wp-migrate.sh --archive /path/to/archive.zip --dry-run --verbose
```

### Testing Error Handling

**Test missing dependencies:**
```bash
# Temporarily rename binary to test detection
sudo mv /usr/local/bin/wp /usr/local/bin/wp.bak
./wp-migrate.sh --archive /path/to/backup.zip
sudo mv /usr/local/bin/wp.bak /usr/local/bin/wp
```

**Test invalid arguments:**
```bash
# No migration mode
./wp-migrate.sh

# Missing required flags
./wp-migrate.sh --dest-host user@dest

# Invalid archive path
./wp-migrate.sh --archive /nonexistent/backup.zip

# Conflicting modes
./wp-migrate.sh --dest-host user@dest --archive /backup.zip
```

**Test SSH failures:**
```bash
# Invalid host
./wp-migrate.sh --dest-host user@invalid-host --dest-root /tmp --dry-run

# Invalid port
./wp-migrate.sh --dest-host user@dest --dest-root /tmp --ssh-opt 'Port=99999' --dry-run
```

## Integration Testing

### Docker-Based Testing

Create a test environment with Docker:

**docker-compose.yml:**
```yaml
version: '3'
services:
  wordpress:
    image: wordpress:latest
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - ./wp-migrate.sh:/var/www/html/wp-migrate.sh
      - wordpress_data:/var/www/html
    depends_on:
      - db
  db:
    image: mysql:5.7
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
      MYSQL_ROOT_PASSWORD: root
volumes:
  wordpress_data:
```

**Run tests:**
```bash
# Start environment
docker-compose up -d

# Install wp-cli in container
docker-compose exec wordpress bash -c "curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && chmod +x wp-cli.phar && mv wp-cli.phar /usr/local/bin/wp"

# Run migration test
docker-compose exec wordpress ./wp-migrate.sh --archive /path/to/backup.zip --dry-run

# Cleanup
docker-compose down -v
```

### Testing Archive Adapters

**Test new adapter:**

1. Create test archive matching format
2. Implement adapter functions in src/lib/adapters/
3. Add adapter to build in Makefile
4. Build and test:
   ```bash
   make build
   ./wp-migrate.sh --archive /path/to/test-archive --dry-run --verbose
   ```

5. Verify detection:
   ```bash
   # Should auto-detect
   ./wp-migrate.sh --archive /path/to/test-archive --dry-run --verbose | grep "Detected.*adapter"

   # Should work with explicit type
   ./wp-migrate.sh --archive /path/to/test-archive --archive-type newformat --dry-run
   ```

## Performance Testing

### Measure Execution Time

**Dry-run performance:**
```bash
time ./wp-migrate.sh --archive /path/to/large-backup.zip --dry-run
```

**Real migration performance:**
```bash
time ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/site
```

### Profile Large Database Imports

```bash
# Check database size
wp db size

# Time export
time wp db export dump.sql

# Time import
time wp db import dump.sql

# Time search-replace
time wp search-replace 'old.com' 'new.com' --dry-run
```

### Profile Large File Transfers

```bash
# Check wp-content size
du -sh wp-content/

# Time rsync
time rsync -avz --dry-run wp-content/ user@dest:/var/www/html/wp-content/
```

## Regression Testing

After bug fixes or new features, verify:

**1. All existing functionality still works:**
```bash
# Run full test suite
make test
./test-wp-migrate.sh

# Test both modes
./wp-migrate.sh --dest-host test@dest --dest-root /tmp --dry-run
./wp-migrate.sh --archive /path/to/backup.zip --dry-run
```

**2. Bug doesn't reoccur:**
Create specific test case for the bug and add to test suite.

**3. No new regressions introduced:**
Test related functionality that might be affected.

## Continuous Integration

### GitHub Actions Example

**.github/workflows/test.yml:**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install ShellCheck
        run: sudo apt-get install -y shellcheck
      - name: Run tests
        run: make test
      - name: Run test suite
        run: ./test-wp-migrate.sh
```

## Test Data

### Sample Archives for Testing

Create test archives for each supported format:

**Duplicator archive:**
```bash
# Structure:
backup.zip
├── installer.php
├── dup-installer/
│   └── dup-database__[hash].sql
└── wp-content/
    ├── plugins/
    ├── themes/
    └── uploads/
```

**Jetpack archive:**
```bash
# Structure:
backup.tar.gz
├── meta.json
├── sql/
│   ├── wp_options.sql
│   ├── wp_posts.sql
│   └── ...
└── wp-content/
    ├── plugins/
    ├── themes/
    └── uploads/
```

**Solid Backups archive:**
```bash
# Structure:
backup.zip
├── importbuddy.php
└── wp-content/
    ├── uploads/backupbuddy_temp/[id]/
    │   ├── wp_options.sql
    │   ├── wp_posts.sql
    │   └── ...
    ├── plugins/
    └── themes/
```

### Creating Test Archives

```bash
# Minimal Duplicator-style archive
mkdir -p test-duplicator/dup-installer
echo "SELECT 1;" > test-duplicator/dup-installer/dup-database__abc123.sql
touch test-duplicator/installer.php
mkdir -p test-duplicator/wp-content/{plugins,themes,uploads}
cd test-duplicator && zip -r ../test-duplicator.zip . && cd ..

# Minimal Jetpack-style archive
mkdir -p test-jetpack/sql
echo '{"version":"1.0"}' > test-jetpack/meta.json
echo "SELECT 1;" > test-jetpack/sql/wp_options.sql
mkdir -p test-jetpack/wp-content/{plugins,themes,uploads}
cd test-jetpack && tar -czf ../test-jetpack.tar.gz . && cd ..

# Minimal Solid Backups-style archive
mkdir -p test-solidbackups/wp-content/uploads/backupbuddy_temp/abc123
echo "SELECT 1;" > test-solidbackups/wp-content/uploads/backupbuddy_temp/abc123/wp_options.sql
touch test-solidbackups/importbuddy.php
mkdir -p test-solidbackups/wp-content/{plugins,themes}
cd test-solidbackups && zip -r ../test-solidbackups.zip . && cd ..
```

## Debugging Test Failures

### ShellCheck Failures

**View detailed errors:**
```bash
shellcheck wp-migrate.sh
```

**Fix common issues:**
- SC2086: Quote variables to prevent word splitting
- SC2155: Separate variable declaration from assignment
- SC2164: Use 'cd ... || exit' to handle cd failures

**Disable specific checks (use sparingly):**
```bash
# shellcheck disable=SC2086
variable=$unquoted
```

### Test Suite Failures

**Run with verbose output:**
```bash
bash -x ./test-wp-migrate.sh
```

**Test specific scenario:**
```bash
./wp-migrate.sh --help
./wp-migrate.sh --version
./wp-migrate.sh 2>&1 | head -20
```

### Build Failures

**Check source files individually:**
```bash
shellcheck src/header.sh
shellcheck src/lib/core.sh
shellcheck src/lib/functions.sh
```

**Verify concatenation order:**
```bash
cat src/header.sh src/lib/core.sh src/lib/functions.sh src/main.sh | head -50
```

**Check for duplicate functions:**
```bash
grep -n "^function_name()" src/**/*.sh
```

## Best Practices

### Writing Testable Code

1. **Use dry-run mode**: Make all operations previewable
2. **Validate early**: Check inputs before making changes
3. **Return meaningful exit codes**: 0 for success, 1+ for errors
4. **Log comprehensively**: Use log() function for all operations
5. **Handle errors**: Use 'set -e' and check command results

### Test Coverage

Ensure tests cover:
- ✅ All command-line flags
- ✅ Error conditions (missing deps, invalid input)
- ✅ Both migration modes (push and archive)
- ✅ All archive formats (Duplicator, Jetpack, Solid Backups)
- ✅ Edge cases (complex prefixes, large files, etc.)
- ✅ Rollback scenarios

### Maintaining Tests

- Keep tests fast (use --dry-run)
- Update tests when adding features
- Add regression tests for bugs
- Document test scenarios
- Run tests before every commit
