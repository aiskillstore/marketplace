# Troubleshooting Guide

Comprehensive troubleshooting guide for wp-migrate.sh issues.

## General Debugging Strategy

### Step 1: Start with Dry Run
Always preview operations before executing:
```bash
./wp-migrate.sh <your-flags> --dry-run --verbose
```

### Step 2: Enable Verbose Logging
Show detailed diagnostic information:
```bash
./wp-migrate.sh <your-flags> --verbose
```

### Step 3: Enable Trace Mode
See every command before execution:
```bash
./wp-migrate.sh <your-flags> --trace
```

### Step 4: Check Logs
After failed migrations, examine the log file:
```bash
# Push mode logs
ls -lh logs/migrate-wpcontent-push-*.log

# Archive mode logs
ls -lh logs/migrate-archive-import-*.log

# View latest log
tail -100 logs/migrate-*.log
```

## Push Mode Issues

### SSH Connection Failures

**Symptom:** "Could not connect to destination via SSH" or "Connection timed out"

**Diagnosis:**
```bash
# Test SSH connection manually
ssh user@dest.example.com

# Test with script's SSH options
ssh -o StrictHostKeyChecking=accept-new user@dest.example.com

# Verify SSH key authentication
ssh -v user@dest.example.com
```

**Solutions:**
1. Verify SSH credentials and host reachability
2. Check firewall rules allow SSH (port 22 or custom)
3. Add custom SSH options:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --ssh-opt 'Port=2222' \
     --ssh-opt 'IdentityFile=~/.ssh/custom_key'
   ```
4. For jump hosts:
   ```bash
   --ssh-opt 'ProxyJump=bastion.example.com'
   ```

### WP-CLI Not Found on Destination

**Symptom:** "wp: command not found" or "wp-cli not available on destination"

**Diagnosis:**
```bash
# Check wp-cli on destination
ssh user@dest 'which wp'
ssh user@dest 'wp --version'

# Check PATH
ssh user@dest 'echo $PATH'
```

**Solutions:**
1. Install wp-cli on destination server
2. Ensure wp-cli is in PATH for SSH sessions
3. Add to .bashrc or .bash_profile:
   ```bash
   export PATH="$PATH:/path/to/wp-cli"
   ```
4. Use absolute path in wp-config if needed

### Database Import Fails

**Symptom:** "Error importing database" or "SQL syntax error"

**Diagnosis:**
```bash
# Check database dump was transferred
ssh user@dest 'ls -lh /var/www/html/db-imports/'

# Check MySQL error logs
ssh user@dest 'tail -50 /var/log/mysql/error.log'

# Verify database credentials
ssh user@dest 'cd /var/www/html && wp db check'
```

**Solutions:**
1. Check max_allowed_packet size in MySQL config:
   ```bash
   wp db query "SHOW VARIABLES LIKE 'max_allowed_packet';"
   ```
   Increase if needed in my.cnf:
   ```ini
   [mysqld]
   max_allowed_packet=256M
   ```

2. Import manually to see detailed errors:
   ```bash
   # If gzipped
   gunzip db-imports/dump-TIMESTAMP.sql.gz
   wp db import db-imports/dump-TIMESTAMP.sql

   # Or pipe through gunzip
   gunzip -c db-imports/dump-TIMESTAMP.sql.gz | wp db import -
   ```

3. Check database user permissions:
   ```bash
   wp db query "SHOW GRANTS;"
   ```

4. Verify sufficient disk space:
   ```bash
   df -h
   ```

### URL Search-Replace Fails

**Symptom:** "Error performing search-replace" or site shows old domain

**Diagnosis:**
```bash
# Check current home and siteurl
wp option get home
wp option get siteurl

# Test search-replace manually (dry run)
wp search-replace 'https://old.com' 'https://new.com' \
  --dry-run \
  --report-changed-only
```

**Solutions:**
1. Verify URLs are detected correctly:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --dry-run --verbose
   # Look for "Source home URL" and "Dest home URL" in output
   ```

2. Override domain detection:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --dest-domain new.example.com
   ```

3. Set explicit URLs:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --dest-home-url https://new.example.com \
     --dest-site-url https://new.example.com
   ```

4. Skip bulk search-replace and run manually later:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --no-search-replace
   ```

### Rsync Transfer Fails

**Symptom:** "rsync error" or "Permission denied" during file sync

**Diagnosis:**
```bash
# Test rsync manually
rsync -avz --dry-run wp-content/ user@dest:/var/www/html/wp-content/

# Check permissions on destination
ssh user@dest 'ls -ld /var/www/html/wp-content'
```

**Solutions:**
1. Verify destination directory exists and is writable:
   ```bash
   ssh user@dest 'mkdir -p /var/www/html/wp-content'
   ssh user@dest 'chmod 755 /var/www/html/wp-content'
   ```

2. Check SSH user has write permissions:
   ```bash
   ssh user@dest 'touch /var/www/html/wp-content/test.txt'
   ```

3. For StellarSites or managed hosting with protected files:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --stellarsites
   ```

4. Exclude problematic directories:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --rsync-opt '--exclude=cache/' \
     --rsync-opt '--exclude=*.log'
   ```

### Maintenance Mode Stuck

**Symptom:** Site shows "Briefly unavailable for scheduled maintenance" after migration

**Diagnosis:**
```bash
# Check for .maintenance file
ls -la wp-content/.maintenance
ssh user@dest 'ls -la /var/www/html/.maintenance'
```

**Solutions:**
```bash
# Remove maintenance file manually
rm .maintenance
ssh user@dest 'rm /var/www/html/.maintenance'

# Or use wp-cli
wp maintenance-mode deactivate
ssh user@dest 'cd /var/www/html && wp maintenance-mode deactivate'
```

### Object Cache Issues After Migration

**Symptom:** "Fatal error: Class 'Redis' not found" or caching errors

**Cause:** The script preserves object-cache.php by excluding it during sync

**Solutions:**
1. Check if destination has required PHP extensions:
   ```bash
   ssh user@dest 'php -m | grep -i redis'
   ssh user@dest 'php -m | grep -i memcache'
   ```

2. If extension missing, remove object-cache.php:
   ```bash
   ssh user@dest 'rm /var/www/html/wp-content/object-cache.php'
   ```

3. Flush cache after migration:
   ```bash
   ssh user@dest 'cd /var/www/html && wp cache flush'
   ssh user@dest 'cd /var/www/html && wp redis flush'
   ```

## Archive Mode Issues

### Archive Format Not Detected

**Symptom:** "Could not detect archive format" or "No matching adapter found"

**Diagnosis:**
```bash
# Check archive structure
unzip -l /path/to/backup.zip | head -50
tar -tzf /path/to/backup.tar.gz | head -50

# Try with verbose mode
./wp-migrate.sh --archive /path/to/backup.zip --dry-run --verbose
```

**Solutions:**
1. Specify format explicitly:
   ```bash
   ./wp-migrate.sh --archive /path/to/backup.zip --archive-type duplicator
   ./wp-migrate.sh --archive /path/to/backup.tar.gz --archive-type jetpack
   ./wp-migrate.sh --archive /path/to/backup.zip --archive-type solidbackups
   ```

2. Verify archive is complete (not corrupted):
   ```bash
   unzip -t /path/to/backup.zip
   tar -tzf /path/to/backup.tar.gz > /dev/null
   ```

3. Check for signature files:
   - Duplicator: installer.php, dup-installer/ directory
   - Jetpack: meta.json, sql/ directory
   - Solid Backups: importbuddy.php or backupbuddy_dat.php

### Insufficient Disk Space

**Symptom:** "Insufficient disk space" or "No space left on device"

**Diagnosis:**
```bash
# Check available space
df -h .

# Check archive size
ls -lh /path/to/backup.zip

# Script requires 3x archive size
```

**Solutions:**
1. Free up disk space:
   ```bash
   # Clean old backups
   rm -rf db-backups/old-*
   rm -rf wp-content.backup-old-*

   # Clean old logs
   rm logs/migrate-*.log.old
   ```

2. Use different temp directory with more space:
   ```bash
   export TMPDIR=/path/to/larger/partition
   ./wp-migrate.sh --archive /path/to/backup.zip
   ```

3. Extract archive manually to control location:
   ```bash
   mkdir /path/to/extracted
   unzip /path/to/backup.zip -d /path/to/extracted
   ./wp-migrate.sh --archive /path/to/extracted
   ```

### Database File Not Found in Archive

**Symptom:** "Could not detect database file" or "No SQL files found"

**Diagnosis:**
```bash
# Search for SQL files in archive
unzip -l backup.zip | grep -i '\.sql'
tar -tzf backup.tar.gz | grep -i '\.sql'

# Check expected locations:
# Duplicator: dup-installer/dup-database__*.sql
# Jetpack: sql/*.sql
# Solid Backups: wp-content/uploads/backupbuddy_temp/*/
```

**Solutions:**
1. Verify archive format matches adapter expectations
2. Extract manually and inspect structure:
   ```bash
   unzip backup.zip -d /tmp/inspect
   find /tmp/inspect -name '*.sql' -type f
   ```

3. Report issue if legitimate backup format not supported

### wp-content Directory Not Found in Archive

**Symptom:** "Could not detect wp-content directory" or low directory score

**Diagnosis:**
```bash
# Look for wp-content structure
unzip -l backup.zip | grep -E '(plugins|themes|uploads)/'
tar -tzf backup.tar.gz | grep -E '(plugins|themes|uploads)/'
```

**Solutions:**
1. Check if archive contains full site or just database
2. Verify wp-content exists in archive:
   ```bash
   unzip -l backup.zip | grep 'wp-content/'
   ```

3. Extract and manually inspect:
   ```bash
   unzip backup.zip -d /tmp/inspect
   ls -la /tmp/inspect/
   ```

### Table Prefix Mismatch

**Symptom:** "Database tables not found" or "Error detecting table prefix"

**Diagnosis:**
```bash
# Check current wp-config.php prefix
grep 'table_prefix' wp-config.php

# Check tables in database
wp db tables

# Check tables in imported dump
gunzip -c db-backups/dump.sql.gz | grep 'CREATE TABLE' | head -10
```

**Solutions:**
The script automatically detects and updates table prefix, but if it fails:

1. Update wp-config.php manually:
   ```bash
   vim wp-config.php
   # Change: $table_prefix = 'imported_prefix_';
   ```

2. Or rename tables:
   ```bash
   # Not recommended - script should handle this
   wp db query "RENAME TABLE old_wp_posts TO new_wp_posts;"
   ```

3. Check for complex prefixes with underscores (script supports these):
   ```
   my_site_
   wp_live_2024_
   prod_v2_
   ```

### Jetpack Backup Multi-File Import Issues

**Symptom:** "Error importing Jetpack multi-file database" or missing tables

**Diagnosis:**
```bash
# Check SQL files in archive
tar -tzf jetpack-backup.tar.gz | grep 'sql/'

# Verify all tables imported
wp db tables
```

**Solutions:**
1. Ensure all SQL files are present in sql/ directory
2. Import manually if needed:
   ```bash
   for sql in /path/to/extracted/sql/*.sql; do
     wp db import "$sql"
   done
   ```

3. Check for import errors in logs:
   ```bash
   tail -100 logs/migrate-archive-import-*.log
   ```

### Solid Backups Split SQL Consolidation Issues

**Symptom:** "Error consolidating Solid Backups SQL files" or missing tables

**Diagnosis:**
```bash
# Check for split SQL files
unzip -l backup.zip | grep 'backupbuddy_temp/.*\.sql$'

# Verify extraction
ls -la /tmp/extracted/wp-content/uploads/backupbuddy_temp/*/
```

**Solutions:**
1. Script automatically consolidates split files; check logs for errors
2. Manually consolidate if needed:
   ```bash
   cat /tmp/extracted/wp-content/uploads/backupbuddy_temp/*/*.sql > consolidated.sql
   wp db import consolidated.sql
   ```

3. Verify all table files present:
   ```bash
   ls /tmp/extracted/wp-content/uploads/backupbuddy_temp/*/ | wc -l
   ```

## Common Error Messages

### "WordPress installation not found"

**Cause:** Script not running from WordPress root directory

**Solution:**
```bash
cd /path/to/wordpress
./wp-migrate.sh <flags>
```

Verify wp-config.php exists:
```bash
ls -la wp-config.php
```

### "wp command not found"

**Cause:** WP-CLI not installed or not in PATH

**Solution:**
```bash
# Check if installed
which wp

# Install WP-CLI
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp

# Verify
wp --version
```

### "rsync command not found"

**Cause:** rsync not installed

**Solution:**
```bash
# macOS
brew install rsync

# Ubuntu/Debian
sudo apt-get install rsync

# CentOS/RHEL
sudo yum install rsync
```

### "unzip command not found" or "tar command not found"

**Cause:** Archive extraction tools not installed

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install unzip tar gzip

# CentOS/RHEL
sudo yum install unzip tar gzip

# macOS (usually pre-installed)
brew install unzip gnu-tar
```

### "Permission denied" on mu-plugins directories

**Cause:** Managed hosting (StellarSites, etc.) protects certain directories

**Solution:**
```bash
./wp-migrate.sh <flags> --stellarsites
```

This excludes protected mu-plugins and preserves host infrastructure.

### "Error establishing database connection" after migration

**Causes:**
1. Table prefix mismatch
2. Database credentials incorrect
3. Database server unreachable

**Solutions:**
1. Check wp-config.php database settings:
   ```php
   define('DB_NAME', 'database_name');
   define('DB_USER', 'username');
   define('DB_PASSWORD', 'password');
   define('DB_HOST', 'localhost');
   $table_prefix = 'wp_';
   ```

2. Verify database exists and credentials work:
   ```bash
   wp db check
   ```

3. Check table prefix matches database tables:
   ```bash
   grep 'table_prefix' wp-config.php
   wp db tables | head -5
   ```

4. Test database connection:
   ```bash
   wp db query "SELECT 1;"
   ```

## Performance Issues

### Slow Database Transfer

**Symptom:** Database export or import takes very long

**Solutions:**
1. Enable gzip compression (enabled by default):
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html
   # Gzip is default; omit --no-gzip
   ```

2. Check database size:
   ```bash
   wp db size
   wp db size --tables
   ```

3. Optimize database before migration:
   ```bash
   wp db optimize
   ```

4. Clean up old data:
   ```bash
   wp transient delete --all
   wp post delete $(wp post list --post_status=trash --format=ids)
   ```

### Slow File Transfer

**Symptom:** rsync takes very long to transfer wp-content

**Solutions:**
1. Check network bandwidth
2. Limit bandwidth if needed:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --rsync-opt '--bwlimit=10000'
   ```

3. Exclude large unnecessary directories:
   ```bash
   ./wp-migrate.sh --dest-host user@dest --dest-root /var/www/html \
     --rsync-opt '--exclude=uploads/backups/' \
     --rsync-opt '--exclude=cache/'
   ```

4. Use compression (enabled by default in rsync -z flag)

### Slow Search-Replace

**Symptom:** URL search-replace operation takes very long

**Solutions:**
1. Skip bulk search-replace if not needed:
   ```bash
   ./wp-migrate.sh <flags> --no-search-replace
   ```

2. Run search-replace on specific tables only:
   ```bash
   wp search-replace 'old.com' 'new.com' wp_posts wp_postmeta
   ```

3. Check for very large serialized data:
   ```bash
   wp db query "SELECT option_name, LENGTH(option_value) as size
                FROM wp_options
                ORDER BY size DESC
                LIMIT 10;"
   ```

## Rollback and Recovery

### Rollback After Failed Archive Import

The script provides exact rollback commands in output:

```bash
# 1. Restore database
wp db import db-backups/pre-archive-backup_TIMESTAMP.sql.gz

# 2. Restore wp-content
rm -rf wp-content
mv wp-content.backup-TIMESTAMP wp-content

# 3. Clear caches
wp cache flush
wp redis flush  # if applicable

# 4. Verify checksums
wp core verify-checksums
wp plugin verify-checksums --all
```

### Rollback After Push Mode Migration

```bash
# On destination server:
# 1. Find backup timestamp
ls -d wp-content.backup-*

# 2. Restore wp-content
rm -rf wp-content
mv wp-content.backup-TIMESTAMP wp-content

# 3. Restore database (if backup exists)
ls db-imports/backup-*.sql.gz
wp db import db-imports/backup-TIMESTAMP.sql.gz

# 4. Clear caches
wp cache flush
```

### Partial Rollback (wp-content only)

```bash
# Restore specific directories
cp -a wp-content.backup-TIMESTAMP/plugins/critical-plugin wp-content/plugins/
cp -a wp-content.backup-TIMESTAMP/themes/active-theme wp-content/themes/
```

### Partial Rollback (database only)

```bash
# Restore specific tables
wp db export backup.sql --tables=wp_options,wp_users
# ... make changes ...
wp db import backup.sql
```

## Getting Help

### Collect Diagnostic Information

When reporting issues, provide:

1. Script version:
   ```bash
   ./wp-migrate.sh --version
   ```

2. Migration mode and flags used:
   ```bash
   ./wp-migrate.sh <your-exact-command> --dry-run --trace > debug.log 2>&1
   ```

3. Environment info:
   ```bash
   wp --version
   rsync --version
   ssh -V
   uname -a
   ```

4. Log file:
   ```bash
   cat logs/migrate-*.log
   ```

5. Archive structure (if archive mode):
   ```bash
   unzip -l /path/to/backup.zip > archive-structure.txt
   # or
   tar -tzf /path/to/backup.tar.gz > archive-structure.txt
   ```

### Report Issues

GitHub Issues: https://github.com/BWBama85/wp-migrate.sh/issues

Include:
- wp-migrate.sh version
- Migration mode (push or archive)
- Full command with flags (redact sensitive info)
- Error message and logs
- Environment information
- Steps to reproduce

### Community Support

- Check existing GitHub issues for similar problems
- Review README.md for updated documentation
- Check CHANGELOG.md for recent fixes
- Read src/lib/adapters/README.md for adapter details
