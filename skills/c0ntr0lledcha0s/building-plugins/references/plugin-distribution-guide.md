# Plugin Distribution Guide

Complete guide to publishing and distributing Claude Code plugins.

## Table of Contents

1. [Distribution Methods](#distribution-methods)
2. [Marketplace Publishing](#marketplace-publishing)
3. [Versioning Strategies](#versioning-strategies)
4. [Update Workflows](#update-workflows)
5. [Release Process](#release-process)

## Distribution Methods

### Method 1: Direct Distribution

**Description:** Users clone/download and install manually

**Pros:**
- Full control over distribution
- No approval process
- Easy to iterate quickly

**Cons:**
- Manual installation required
- Users must manage updates
- Lower discoverability

**Setup:**

1. Host plugin on GitHub/GitLab
2. Provide installation instructions in README
3. Tag releases with semantic versions

**Installation Instructions:**
```bash
# Clone repository
git clone https://github.com/username/plugin-name.git

# Symlink to Claude's plugin directory
ln -s /path/to/plugin-name ~/.claude/plugins/plugin-name

# Restart Claude Code
```

### Method 2: Marketplace Distribution

**Description:** Plugin listed in official Claude Code marketplace

**Pros:**
- One-command installation
- Automatic updates
- Better discoverability
- Version management

**Cons:**
- May require approval
- Must follow marketplace guidelines
- Update process may be slower

**Setup:**

1. Meet marketplace requirements
2. Submit plugin for inclusion
3. Maintain marketplace.json entry

**Installation:**
```bash
claude plugin install plugin-name
```

### Method 3: Private Distribution

**Description:** Internal distribution within organization

**Pros:**
- Private/proprietary plugins
- Controlled access
- Internal marketplace possible

**Cons:**
- Manual setup required
- Custom installation process
- No public discovery

**Setup:**

1. Host in private repository
2. Provide organization-specific instructions
3. Consider internal plugin registry

## Marketplace Publishing

### Prerequisites

Before submitting to marketplace:

1. **Valid plugin.json**
   ```json
   {
     "name": "plugin-name",
     "version": "1.0.0",
     "description": "Clear description (20-1024 chars)",
     "author": {
       "name": "Your Name",
       "email": "email@example.com",
       "url": "https://github.com/username"
     },
     "license": "MIT",
     "keywords": ["keyword1", "keyword2", "keyword3"]
   }
   ```

2. **Comprehensive README.md**
   - Installation instructions
   - Usage examples
   - Component documentation
   - Troubleshooting section

3. **LICENSE file**
   - Must match license in plugin.json
   - Common: MIT, Apache-2.0, BSD-3-Clause

4. **All validations passing**
   ```bash
   python3 validate-plugin.py ./plugin-name/
   ```

### Marketplace Requirements

#### 1. Naming Requirements

- **Lowercase-hyphens only**: `my-plugin` not `my_plugin` or `MyPlugin`
- **Max 64 characters**
- **Descriptive**: Indicates plugin purpose
- **Unique**: Not conflicting with existing plugins

#### 2. Version Requirements

- **Semantic versioning**: `MAJOR.MINOR.PATCH`
- **Start at 1.0.0** for initial marketplace release
- **No pre-release versions**: `1.0.0-beta` not allowed

#### 3. Documentation Requirements

- **README.md** with all required sections
- **Clear usage examples**
- **Troubleshooting guide**
- **Component descriptions**

#### 4. Quality Requirements

- **All components validated**
- **No security issues**
- **No exposed secrets**
- **Safe script permissions**

### marketplace.json Registration

For plugins in the marketplace repository, you MUST update `.claude-plugin/marketplace.json`:

#### Adding New Plugin

```json
{
  "metadata": {
    "name": "Claude Code Plugin Marketplace",
    "version": "1.2.0",  // ← Increment MINOR
    "stats": {
      "totalPlugins": 15,  // ← Increment count
      "lastUpdated": "2024-11-15"  // ← Update date
    }
  },
  "plugins": [
    // ... existing plugins ...
    {
      "name": "new-plugin-name",
      "source": "./new-plugin-name",
      "description": "Plugin description matching plugin.json",
      "version": "1.0.0",
      "category": "development-tools",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "author": {
        "name": "Author Name",
        "url": "https://github.com/username"
      },
      "repository": "https://github.com/username/repo",
      "license": "MIT",
      "homepage": "https://github.com/username/repo/tree/main/plugin-name"
    }
  ]
}
```

#### Updating Existing Plugin

```json
{
  "metadata": {
    "version": "1.2.1",  // ← Increment PATCH
    "stats": {
      "lastUpdated": "2024-11-15"  // ← Update date
    }
  },
  "plugins": [
    {
      "name": "existing-plugin",
      "version": "1.3.0",  // ← Must match plugin's plugin.json
      "description": "Updated description if changed"
      // ... other fields
    }
  ]
}
```

**Critical Rules:**
- Version in marketplace.json MUST match plugin's plugin.json
- Update `lastUpdated` date on every change
- Increment marketplace version appropriately

### Categories

Choose the most appropriate category:

- **development-tools**: Development automation, code generation, testing
- **automation**: Workflow automation, task automation
- **integration**: External service integrations, APIs
- **productivity**: General productivity enhancements
- **security**: Security scanning, vulnerability detection
- **data**: Data analysis, processing, visualization
- **documentation**: Documentation generation, maintenance

### Keywords

Choose 3-10 descriptive keywords:

**Good Keywords:**
```json
["git", "version-control", "automation", "workflows"]
```

**Bad Keywords:**
```json
["plugin", "claude", "tool"]  // Too generic
```

## Versioning Strategies

### Semantic Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH`

#### MAJOR Version

Increment when making **breaking changes**:

- Removed components (agents, skills, commands, hooks)
- Changed command interfaces (arguments, behavior)
- Removed or changed configuration options
- Incompatible API changes

**Example:**
```
v1.5.2 → v2.0.0

Breaking changes:
- Removed deprecated `/old-command`
- Changed `/analyze` to require file path
- Removed `legacyMode` configuration option
```

#### MINOR Version

Increment when adding **new features** (backward compatible):

- Added new agents, skills, commands, hooks
- Added new configuration options
- Enhanced existing functionality (backward compatible)
- Added new capabilities

**Example:**
```
v1.2.3 → v1.3.0

New features:
- Added `/new-command` for batch processing
- Added `analyzing-performance` skill
- Added `autoFix` configuration option
```

#### PATCH Version

Increment for **bug fixes** and minor improvements:

- Fixed bugs
- Performance improvements
- Documentation updates
- Dependency updates
- Security patches

**Example:**
```
v1.3.0 → v1.3.1

Bug fixes:
- Fixed crash in /analyze command
- Corrected typo in skill description
- Updated dependency versions
```

### Version Upgrade Examples

#### Example 1: Adding a Command

```
Current: 1.2.0
Change: Added /export command
New Version: 1.3.0 (MINOR)
```

#### Example 2: Removing a Command

```
Current: 1.5.0
Change: Removed deprecated /old-export
New Version: 2.0.0 (MAJOR)
```

#### Example 3: Fixing a Bug

```
Current: 1.3.2
Change: Fixed error in validation
New Version: 1.3.3 (PATCH)
```

#### Example 4: Changing Command Behavior

```
Current: 1.4.0
Change: /analyze now requires file path (was optional)
New Version: 2.0.0 (MAJOR)
```

### Pre-release Versions

For development/testing only (NOT for marketplace):

```
1.0.0-alpha.1    # Alpha release
1.0.0-beta.2     # Beta release
1.0.0-rc.1       # Release candidate
```

**Note:** Marketplace only accepts stable versions (no pre-release identifiers).

## Update Workflows

### Workflow 1: Bug Fix Release

1. **Identify Bug**
   - User reports issue
   - Reproduce bug
   - Identify root cause

2. **Fix Bug**
   - Implement fix
   - Add test to prevent regression
   - Validate fix works

3. **Update Version**
   ```json
   // plugin.json
   {
     "version": "1.2.3"  // Was 1.2.2
   }
   ```

4. **Update Marketplace** (if applicable)
   ```json
   // marketplace.json
   {
     "metadata": {
       "version": "1.5.1",  // Increment PATCH
       "stats": {
         "lastUpdated": "2024-11-15"
       }
     },
     "plugins": [
       {
         "name": "my-plugin",
         "version": "1.2.3"  // Match plugin.json
       }
     ]
   }
   ```

5. **Document Change**
   Update README.md changelog:
   ```markdown
   ## Changelog

   ### v1.2.3 (2024-11-15)
   - Fixed crash in /analyze command when file not found
   - Improved error messages
   ```

6. **Release**
   - Commit changes
   - Tag release: `git tag v1.2.3`
   - Push: `git push && git push --tags`

### Workflow 2: Feature Release

1. **Plan Feature**
   - Define requirements
   - Design component structure
   - Identify affected components

2. **Implement Feature**
   - Create new components
   - Update existing components
   - Add documentation

3. **Validate**
   ```bash
   python3 validate-plugin.py ./my-plugin/
   ```

4. **Update Version**
   ```json
   // plugin.json
   {
     "version": "1.3.0"  // Was 1.2.3
   }
   ```

5. **Update Marketplace**
   ```json
   // marketplace.json
   {
     "metadata": {
       "version": "1.6.0",  // Increment MINOR
       "stats": {
         "lastUpdated": "2024-11-15"
       }
     },
     "plugins": [
       {
         "name": "my-plugin",
         "version": "1.3.0",
         "keywords": ["new-keyword"]  // Update if needed
       }
     ]
   }
   ```

6. **Document**
   ```markdown
   ### v1.3.0 (2024-11-15)
   - Added `/export` command for data export
   - Added `exporting-data` skill
   - Enhanced `/analyze` with export option
   ```

7. **Release**
   - Commit, tag, push

### Workflow 3: Breaking Change Release

1. **Plan Breaking Changes**
   - Document what's breaking
   - Provide migration guide
   - Announce in advance if possible

2. **Implement Changes**
   - Remove deprecated components
   - Update component interfaces
   - Update all affected code

3. **Migration Guide**
   Create migration guide in README:
   ```markdown
   ## Migrating from v1.x to v2.0

   ### Breaking Changes

   1. `/old-command` removed → Use `/new-command` instead
   2. `/analyze` now requires file path → Add path argument

   ### Migration Steps

   1. Replace all `/old-command` calls with `/new-command`
   2. Update `/analyze` calls to include file path
   ```

4. **Update Version**
   ```json
   {
     "version": "2.0.0"  // MAJOR bump
   }
   ```

5. **Release with Warnings**
   - Clear documentation of breaking changes
   - Migration guide
   - Announcement to users

## Release Process

### Pre-Release Checklist

- [ ] All changes implemented
- [ ] All components validated
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version incremented in plugin.json
- [ ] marketplace.json updated (if applicable)
- [ ] Migration guide written (if breaking changes)

### Release Steps

1. **Final Validation**
   ```bash
   # Validate plugin
   python3 validate-plugin.py ./my-plugin/

   # Test all components manually
   # Run any automated tests
   ```

2. **Update Documentation**
   ```markdown
   # README.md

   ## Changelog

   ### vX.Y.Z (YYYY-MM-DD)
   - Change 1
   - Change 2
   - Change 3
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "chore: release vX.Y.Z"
   ```

4. **Tag Release**
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   ```

5. **Push to Remote**
   ```bash
   git push origin main
   git push origin vX.Y.Z
   ```

6. **Create GitHub Release** (optional)
   - Go to GitHub Releases
   - Create new release from tag
   - Add release notes
   - Attach any artifacts

7. **Announce** (if significant)
   - Update plugin homepage
   - Post in community channels
   - Notify users of breaking changes

### Post-Release

1. **Monitor for Issues**
   - Watch for bug reports
   - Monitor installation issues
   - Check user feedback

2. **Plan Next Release**
   - Track feature requests
   - Prioritize bug fixes
   - Plan version increments

## Best Practices

### 1. Keep Versions in Sync

Always update both files together:
- `plugin.json` version
- `marketplace.json` plugin entry version

### 2. Document All Changes

Maintain comprehensive changelog:
```markdown
## Changelog

### v1.3.0 (2024-11-15)
#### Added
- New `/export` command

#### Changed
- Enhanced `/analyze` performance

#### Fixed
- Bug in validation logic
```

### 3. Test Before Release

- Validate with validation script
- Test all components manually
- Run automated tests
- Test in clean environment

### 4. Communicate Breaking Changes

- Announce in advance
- Provide migration guide
- Give users time to prepare
- Document clearly

### 5. Version Thoughtfully

- Don't increment major version frivolously
- Group related changes in one release
- Consider user impact

## Summary

Successful plugin distribution requires:
- ✅ Clear versioning strategy
- ✅ Comprehensive documentation
- ✅ Thorough validation
- ✅ Proper marketplace registration
- ✅ Clear release process
- ✅ User communication

Follow these guidelines to ensure smooth plugin updates and happy users.
