# Common Migration Patterns

This document provides ready-to-use examples for common wp-migrate.sh scenarios.

## Push Mode Patterns

### Basic Production Migration
```bash
# Standard migration from source to destination
./wp-migrate.sh \
  --dest-host wp@production.example.com \
  --dest-root /var/www/html
```

### Staging to Production with Preview
```bash
# Dry run first to preview
./wp-migrate.sh \
  --dest-host wp@prod.example.com \
  --dest-root /var/www/html \
  --dry-run --verbose

# Execute after reviewing
./wp-migrate.sh \
  --dest-host wp@prod.example.com \
  --dest-root /var/www/html
```

### Migration with Custom SSH Settings
```bash
# Using custom SSH port and key
./wp-migrate.sh \
  --dest-host wp@example.com \
  --dest-root /var/www/html \
  --ssh-opt 'Port=2222' \
  --ssh-opt 'IdentityFile=~/.ssh/custom_key'
```

### Migration Through Jump Host
```bash
# Using SSH bastion/jump host
./wp-migrate.sh \
  --dest-host wp@internal.example.com \
  --dest-root /var/www/html \
  --ssh-opt 'ProxyJump=bastion.example.com'
```

### StellarSites Managed Hosting Migration
```bash
# Preserve managed hosting mu-plugins
./wp-migrate.sh \
  --dest-host user@stellarsites-host.com \
  --dest-root /var/www/html \
  --stellarsites
```

### Fast Migration (Skip Bulk Search-Replace)
```bash
# Only update home/siteurl, skip content URL replacement
./wp-migrate.sh \
  --dest-host wp@staging.example.com \
  --dest-root /var/www/html \
  --no-search-replace
```

### Database Export Only (No Import)
```bash
# Transfer database but don't import (for manual review)
./wp-migrate.sh \
  --dest-host wp@dest.example.com \
  --dest-root /var/www/html \
  --no-import-db
```

### Exclude Large Directories
```bash
# Skip large upload folders during sync
./wp-migrate.sh \
  --dest-host wp@dest.example.com \
  --dest-root /var/www/html \
  --rsync-opt '--exclude=uploads/videos/' \
  --rsync-opt '--exclude=uploads/backups/'
```

### Bandwidth-Limited Transfer
```bash
# Limit bandwidth to 1000 KB/s
./wp-migrate.sh \
  --dest-host wp@dest.example.com \
  --dest-root /var/www/html \
  --rsync-opt '--bwlimit=1000'
```

### Keep Source Site Active
```bash
# Skip maintenance mode on source during migration
./wp-migrate.sh \
  --dest-host wp@dest.example.com \
  --dest-root /var/www/html \
  --no-maint-source
```

### Custom Destination Domain
```bash
# Override domain detection for search-replace
./wp-migrate.sh \
  --dest-host wp@dest.example.com \
  --dest-root /var/www/html \
  --dest-domain staging.mysite.com
```

### Separate Home and Site URLs
```bash
# Set different home and siteurl (WordPress in subdirectory)
./wp-migrate.sh \
  --dest-host wp@dest.example.com \
  --dest-root /var/www/html \
  --dest-home-url https://example.com \
  --dest-site-url https://example.com/wp
```

## Archive Mode Patterns

### Import Duplicator Backup
```bash
# Auto-detect format
./wp-migrate.sh --archive /backups/duplicator-site.zip

# Explicit format
./wp-migrate.sh --archive /backups/site.zip --archive-type duplicator

# Dry run preview
./wp-migrate.sh --archive /backups/site.zip --dry-run --verbose
```

### Import Jetpack Backup
```bash
# ZIP format
./wp-migrate.sh --archive /backups/jetpack-backup.zip

# TAR.GZ format
./wp-migrate.sh --archive /backups/jetpack-backup.tar.gz

# Already extracted directory
./wp-migrate.sh --archive /backups/extracted-jetpack/
```

### Import Solid Backups (BackupBuddy)
```bash
# Full backup
./wp-migrate.sh --archive /backups/backup-full-12345.zip

# With explicit type
./wp-migrate.sh --archive /backups/solidbackups.zip --archive-type solidbackups
```

### Import with Preserved Destination Plugins
```bash
# Keep destination plugins that aren't in archive
./wp-migrate.sh \
  --archive /backups/site.zip \
  --preserve-dest-plugins
```

### Import on StellarSites from Backup
```bash
# Preserve managed hosting mu-plugins
./wp-migrate.sh \
  --archive /backups/site.zip \
  --stellarsites
```

### Fast Import (Skip Bulk Search-Replace)
```bash
# Only update home/siteurl, skip content URL replacement
./wp-migrate.sh \
  --archive /backups/site.zip \
  --no-search-replace
```

### Verbose Import for Troubleshooting
```bash
# Show detailed progress
./wp-migrate.sh --archive /backups/site.zip --verbose

# Show every command (maximum detail)
./wp-migrate.sh --archive /backups/site.zip --trace
```

### Automated/CI Migration (v2.6.0)
```bash
# Skip confirmation prompts for CI/CD
./wp-migrate.sh \
  --archive /backups/site.zip \
  --yes --quiet

# Or for push mode
./wp-migrate.sh \
  --dest-host wp@staging \
  --dest-root /var/www/html \
  --yes --quiet
```

## v2.6.0 Feature Patterns

### Migration Preview and Confirmation
```bash
# Interactive migration with preview (default behavior)
./wp-migrate.sh --archive /backups/site.zip
# Shows:
#   - Archive format and size
#   - Destination URLs and paths
#   - Disk space requirements
#   - Planned operations list
# Then prompts: "Proceed with migration? [y/N]"

# Push mode preview
./wp-migrate.sh \
  --dest-host wp@prod \
  --dest-root /var/www/html
# Shows:
#   - Source and destination URLs
#   - SSH connection test results
#   - Database and file size estimates
#   - Planned operations list
# Then prompts: "Proceed with migration? [y/N]"
```

### Rollback Patterns

**Automatic Rollback (v2.6.0)**:
```bash
# Rollback to latest backup (auto-detected)
./wp-migrate.sh --rollback

# Rollback with preview (dry-run)
./wp-migrate.sh --rollback --dry-run --verbose

# Rollback specific backup
./wp-migrate.sh --rollback --rollback-backup db-backups/backup-20251020-120000.sql.gz

# Automated rollback (CI/CD)
./wp-migrate.sh --rollback --yes

# Rollback with explicit paths
./wp-migrate.sh --rollback \
  --rollback-backup db-backups/backup-20251020.sql.gz \
  --rollback-wp-content wp-content.backup-20251020
```

**Manual Rollback (Classic)**:
```bash
# Archive mode provides exact commands in output
# 1. Restore database
wp db import db-backups/pre-archive-backup_TIMESTAMP.sql.gz

# 2. Restore wp-content
rm -rf wp-content
mv wp-content.backup-TIMESTAMP wp-content

# 3. Clear caches
wp cache flush
```

### Progress Indicators

**With Progress (Default when pv installed)**:
```bash
# Install pv for progress bars
sudo apt-get install pv  # Debian/Ubuntu
brew install pv  # macOS

# Archive extraction with progress
./wp-migrate.sh --archive /backups/large-site.zip
# Shows: [=====>     ] 50% ETA 2m30s

# Database import with progress
./wp-migrate.sh --archive /backups/site.zip
# Shows: 450MB 0:02:30 [3.2MB/s]
```

**Without Progress (Quiet mode)**:
```bash
# Suppress all progress indicators
./wp-migrate.sh --archive /backups/site.zip --quiet

# Useful for cron jobs or log files
./wp-migrate.sh \
  --archive /backups/site.zip \
  --yes --quiet >> migration.log 2>&1
```

### Non-Interactive Context Handling

**CI/CD Pipelines**:
```bash
# Correct: Use --yes flag
./wp-migrate.sh --archive /backups/site.zip --yes

# Error: Will fail with TTY requirement
./wp-migrate.sh --archive /backups/site.zip
# Output: "This script requires a TTY for confirmation prompts. Add --yes flag for automation."
```

**Cron Jobs**:
```bash
# Add to crontab with --yes flag
0 2 * * * cd /var/www/html && ./wp-migrate.sh --archive /backups/daily.zip --yes --quiet
```

**GitHub Actions/GitLab CI**:
```yaml
# .github/workflows/migrate.yml
- name: Run migration
  run: |
    ./wp-migrate.sh \
      --archive /backups/site.zip \
      --yes \
      --quiet
```

### Combined v2.6.0 Features

**Safe Production Migration**:
```bash
# 1. Preview with dry-run
./wp-migrate.sh --archive /backups/prod-site.zip --dry-run --verbose

# 2. Execute with confirmation
./wp-migrate.sh --archive /backups/prod-site.zip

# 3. If something goes wrong, rollback
./wp-migrate.sh --rollback
```

**Fully Automated Migration**:
```bash
# CI/CD: no prompts, no progress, with logging
./wp-migrate.sh \
  --archive /backups/site.zip \
  --yes \
  --quiet \
  --verbose > migration.log 2>&1

# Check result
echo $?  # 0 = success, non-zero = failure
```

## Development Patterns

### Preview Migration Without Changes
```bash
# Push mode dry run
./wp-migrate.sh \
  --dest-host wp@dest \
  --dest-root /var/www/html \
  --dry-run --verbose

# Archive mode dry run
./wp-migrate.sh \
  --archive /backups/site.zip \
  --dry-run --verbose
```

### Debug Migration Issues
```bash
# Trace mode shows every command
./wp-migrate.sh \
  --dest-host wp@dest \
  --dest-root /var/www/html \
  --dry-run --trace
```

### Test Archive Detection
```bash
# See which adapter matches
./wp-migrate.sh --archive /backups/unknown.zip --dry-run --verbose
```

### Verify SSH Connectivity
```bash
# Test connection and wp-cli availability
ssh user@dest.example.com 'cd /var/www/html && wp core version'
```

### Check Disk Space Before Import
```bash
# Check available space (need 3x archive size)
df -h /
ls -lh /backups/site.zip
```

## Testing Patterns

### Run ShellCheck Validation
```bash
# Lint the built script
shellcheck wp-migrate.sh

# Or use Makefile
make test
```

### Run Test Suite
```bash
# Execute test script
./test-wp-migrate.sh

# Or use Makefile
make test
```

### Test Build Process
```bash
# Build from source
make build

# Verify checksum updated
cat wp-migrate.sh.sha256

# Clean build artifacts
make clean
```

### Test in Docker Container
```bash
# Spin up test WordPress environment
docker-compose up -d

# Run migration test
docker-compose exec wordpress ./wp-migrate.sh --archive /backups/test.zip --dry-run

# Cleanup
docker-compose down -v
```

## Git Workflow Patterns

### Feature Development
```bash
# Create feature branch
git checkout -b feature/custom-adapter

# Make changes in src/
vim src/lib/adapters/custom.sh

# Build and test
make build
make test

# Commit with template
git add src/ wp-migrate.sh wp-migrate.sh.sha256 CHANGELOG.md
git commit  # Uses .gitmessage template

# Push and create PR
git push -u origin feature/custom-adapter
```

### Bug Fix Workflow
```bash
# Create fix branch
git checkout -b fix/table-prefix-detection

# Make changes
vim src/lib/functions.sh

# Build and verify
make build
shellcheck wp-migrate.sh

# Update changelog
vim CHANGELOG.md

# Commit all together
git add src/ wp-migrate.sh wp-migrate.sh.sha256 CHANGELOG.md
git commit -m "fix: improve table prefix detection for edge cases"

# Create PR
git push -u origin fix/table-prefix-detection
gh pr create --fill
```

### Release Process
```bash
# Ensure on main and up to date
git checkout main
git pull

# Update CHANGELOG.md version and date
vim CHANGELOG.md

# Commit release prep
git add CHANGELOG.md
git commit -m "chore: prepare for v2.5.0 release"

# Create tag
git tag -a v2.5.0 -m "Release v2.5.0"

# Push everything
git push && git push --tags

# Create GitHub release
gh release create v2.5.0 --notes "See CHANGELOG.md for details"
```

## Emergency Recovery Patterns

### Restore from Backup After Failed Migration

**Automatic Rollback (v2.6.0 - Recommended)**:
```bash
# Simple one-command rollback
./wp-migrate.sh --rollback

# Preview rollback first
./wp-migrate.sh --rollback --dry-run --verbose

# Automated rollback (no confirmation)
./wp-migrate.sh --rollback --yes
```

**Manual Rollback (Classic)**:
```bash
# Archive mode provides exact commands in output:
# 1. Restore database
wp db import db-backups/pre-archive-backup_20251017-143022.sql.gz

# 2. Restore wp-content
rm -rf wp-content
mv wp-content.backup-20251017-143022 wp-content

# 3. Clear caches
wp cache flush
wp redis flush

# 4. Verify
wp core verify-checksums
```

### Manual URL Search-Replace
```bash
# If migration ran with --no-search-replace but you need full replacement:
wp search-replace 'https://old-site.com' 'https://new-site.com' \
  --skip-columns=guid \
  --report-changed-only \
  --all-tables
```

### Fix Table Prefix Manually
```bash
# If automatic prefix detection failed:
# 1. Edit wp-config.php
vim wp-config.php
# Change: $table_prefix = 'new_prefix_';

# 2. Verify tables exist
wp db tables | grep 'new_prefix_'
```

### Recover from Object Cache Issues
```bash
# If site breaks due to missing cache extensions:
# Remove drop-in
rm wp-content/object-cache.php

# Flush cache
wp cache flush

# Verify
wp plugin list
```
