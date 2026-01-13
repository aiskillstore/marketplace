---
name: npm-helper
description: NPM and Node.js package management, project configuration, and dependency troubleshooting.
---

# NPM Package Management Assistant Skill

NPM and Node.js package management, project configuration, and dependency troubleshooting.

## Instructions

You are a Node.js and NPM ecosystem expert. When invoked:

1. **Package Management**:
   - Install and manage npm packages
   - Handle package.json configuration
   - Manage lock files (package-lock.json)
   - Use npm, yarn, or pnpm effectively
   - Configure workspaces and monorepos

2. **Project Setup**:
   - Initialize new Node.js projects
   - Configure scripts and lifecycle hooks
   - Set up project structure
   - Configure development tools
   - Manage multiple package managers

3. **Dependency Management**:
   - Handle version ranges and semver
   - Resolve dependency conflicts
   - Audit for security vulnerabilities
   - Update dependencies safely
   - Manage peer dependencies

4. **Troubleshooting**:
   - Fix module resolution errors
   - Resolve version conflicts
   - Debug installation issues
   - Clear cache and rebuild
   - Handle platform-specific issues

5. **Best Practices**: Provide guidance on package management, versioning, security, and performance optimization

## Package Manager Comparison

### npm (Default)
```bash
# Pros: Default in Node.js, widely supported
# Cons: Slower than alternatives

# Initialize project
npm init
npm init -y  # Skip prompts

# Install dependencies
npm install express
npm install --save-dev jest

# Install all dependencies
npm install

# Update dependencies
npm update
npm update express

# Remove package
npm uninstall express

# Run scripts
npm run build
npm test  # Shorthand for npm run test
npm start  # Shorthand for npm run start

# List installed packages
npm list
npm list --depth=0  # Only top-level

# Check for outdated packages
npm outdated
```

### Yarn (v1 Classic)
```bash
# Pros: Faster, better UX, workspaces
# Cons: Extra tool to install

# Install Yarn
npm install -g yarn

# Initialize project
yarn init
yarn init -y

# Install dependencies
yarn add express
yarn add --dev jest

# Install all dependencies
yarn install
yarn  # Shorthand

# Update dependencies
yarn upgrade
yarn upgrade express

# Remove package
yarn remove express

# Run scripts
yarn build
yarn test
yarn start

# List installed packages
yarn list
yarn list --depth=0

# Check for outdated packages
yarn outdated

# Interactive upgrade
yarn upgrade-interactive
```

### pnpm (Fast & Efficient)
```bash
# Pros: Fastest, disk space efficient, strict
# Cons: Less common, some compatibility issues

# Install pnpm
npm install -g pnpm

# Initialize project
pnpm init

# Install dependencies
pnpm add express
pnpm add -D jest

# Install all dependencies
pnpm install

# Update dependencies
pnpm update
pnpm update express

# Remove package
pnpm remove express

# Run scripts
pnpm build
pnpm test
pnpm start

# List installed packages
pnpm list
pnpm list --depth=0

# Check for outdated packages
pnpm outdated
```

### Yarn v3 (Berry)
```bash
# Pros: Zero-installs, Plug'n'Play, smaller size
# Cons: Different from v1, migration needed

# Enable Yarn Berry
yarn set version berry

# Install dependencies
yarn add express
yarn add -D jest

# Use Plug'n'Play (default in v3)
# No node_modules folder

# Or use node_modules
echo "nodeLinker: node-modules" >> .yarnrc.yml

# Zero-installs (commit .yarn/cache)
echo "enableGlobalCache: false" >> .yarnrc.yml
```

## Usage Examples

```
@npm-helper
@npm-helper --init-project
@npm-helper --fix-dependencies
@npm-helper --audit-security
@npm-helper --migrate-to-pnpm
@npm-helper --troubleshoot
```

## Project Initialization

### Basic Project Setup
```bash
# Initialize package.json
npm init -y

# Install common dependencies
npm install express dotenv

# Install dev dependencies
npm install --save-dev \
  nodemon \
  eslint \
  prettier \
  jest \
  @types/node \
  typescript

# Create basic structure
mkdir -p src tests
touch src/index.js tests/index.test.js

# Create .gitignore
cat > .gitignore << EOF
node_modules/
.env
.env.local
dist/
build/
coverage/
.DS_Store
*.log
EOF

# Create .nvmrc for Node version
node -v > .nvmrc
```

### TypeScript Project Setup
```bash
# Initialize project
npm init -y

# Install TypeScript and types
npm install --save-dev \
  typescript \
  @types/node \
  @types/express \
  ts-node \
  nodemon

# Initialize TypeScript
npx tsc --init

# Configure tsconfig.json
cat > tsconfig.json << EOF
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF

# Update package.json scripts
npm pkg set scripts.build="tsc"
npm pkg set scripts.dev="nodemon src/index.ts"
npm pkg set scripts.start="node dist/index.js"
```

### Modern ESM Project Setup
```json
{
  "name": "my-esm-project",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "dev": "node --watch src/index.js",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "node --test"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  }
}
```

## package.json Configuration

### Essential Fields
```json
{
  "name": "my-package",
  "version": "1.0.0",
  "description": "A helpful package",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "type": "module",
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "scripts": {
    "dev": "nodemon src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.ts",
    "lint:fix": "eslint src/**/*.ts --fix",
    "format": "prettier --write \"src/**/*.ts\"",
    "typecheck": "tsc --noEmit",
    "prepare": "husky install",
    "prepublishOnly": "npm run build && npm test"
  },
  "keywords": ["node", "javascript", "helper"],
  "author": "Your Name <email@example.com>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/user/repo.git"
  },
  "bugs": {
    "url": "https://github.com/user/repo/issues"
  },
  "homepage": "https://github.com/user/repo#readme"
}
```

### Dependency Types
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "jest": "^29.7.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0"
  },
  "peerDependencies": {
    "react": ">=16.8.0"
  },
  "peerDependenciesMeta": {
    "react": {
      "optional": true
    }
  },
  "optionalDependencies": {
    "fsevents": "^2.3.3"
  },
  "bundledDependencies": [
    "internal-package"
  ]
}
```

### Scripts Best Practices
```json
{
  "scripts": {
    "// Development": "",
    "dev": "nodemon src/index.ts",
    "dev:debug": "nodemon --inspect src/index.ts",

    "// Building": "",
    "build": "npm run clean && tsc",
    "clean": "rm -rf dist",
    "prebuild": "npm run lint",
    "postbuild": "echo 'Build complete!'",

    "// Testing": "",
    "test": "jest",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration",
    "test:e2e": "jest --testPathPattern=e2e",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",

    "// Linting & Formatting": "",
    "lint": "eslint . --ext .ts,.js",
    "lint:fix": "eslint . --ext .ts,.js --fix",
    "format": "prettier --write \"src/**/*.{ts,js,json}\"",
    "format:check": "prettier --check \"src/**/*.{ts,js,json}\"",

    "// Type Checking": "",
    "typecheck": "tsc --noEmit",
    "typecheck:watch": "tsc --noEmit --watch",

    "// Combined": "",
    "validate": "npm run lint && npm run typecheck && npm test",
    "ci": "npm run validate && npm run build",

    "// Release": "",
    "prepare": "husky install",
    "prepublishOnly": "npm run ci",
    "version": "npm run build && git add -A dist",
    "postversion": "git push && git push --tags"
  }
}
```

## Dependency Version Management

### Semantic Versioning (semver)
```json
{
  "dependencies": {
    "express": "4.18.2",      // Exact version
    "lodash": "^4.17.21",     // Compatible (4.x.x, < 5.0.0)
    "axios": "~1.6.0",        // Approximately (1.6.x)
    "react": ">=16.8.0",      // At least
    "vue": "<4.0.0",          // Less than
    "moment": "*",            // Latest (not recommended)
    "date-fns": "latest"      // Latest (not recommended)
  }
}
```

### Version Range Examples
```bash
# Caret (^) - Compatible updates
^1.2.3  # >=1.2.3 <2.0.0
^0.2.3  # >=0.2.3 <0.3.0
^0.0.3  # >=0.0.3 <0.0.4

# Tilde (~) - Patch updates only
~1.2.3  # >=1.2.3 <1.3.0
~1.2    # >=1.2.0 <1.3.0
~1      # >=1.0.0 <2.0.0

# Advanced ranges
1.2.3 - 2.3.4     # >=1.2.3 <=2.3.4
1.2.x             # 1.2.0, 1.2.1, etc.
*                 # Any version
```

### Lock File Management
```bash
# npm - package-lock.json
# Always commit package-lock.json
npm ci  # Install from lock file (CI/CD)
npm install  # Updates lock file if needed

# Yarn - yarn.lock
# Always commit yarn.lock
yarn install --frozen-lockfile  # Don't update lock file

# pnpm - pnpm-lock.yaml
# Always commit pnpm-lock.yaml
pnpm install --frozen-lockfile  # Don't update lock file
```

## Security and Auditing

### Vulnerability Scanning
```bash
# npm audit
npm audit
npm audit --json  # JSON output
npm audit --audit-level=moderate  # Only moderate+

# Fix vulnerabilities
npm audit fix
npm audit fix --force  # May install breaking changes

# Yarn audit
yarn audit
yarn audit --level moderate

# pnpm audit
pnpm audit
pnpm audit --audit-level moderate
pnpm audit --fix
```

### Security Best Practices
```bash
# Install specific vulnerability fixes
npm install package@version

# Use npm-check-updates for safe updates
npx npm-check-updates
npx ncu -u  # Update package.json
npm install

# Check for outdated packages
npm outdated
yarn outdated
pnpm outdated

# Use Snyk for deeper scanning
npx snyk test
npx snyk wizard

# Ignore specific vulnerabilities (use cautiously)
# Create .npmrc
echo "audit-level=moderate" >> .npmrc
```

## Workspace and Monorepo Management

### npm Workspaces
```json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ],
  "scripts": {
    "build": "npm run build --workspaces",
    "test": "npm run test --workspaces",
    "clean": "npm run clean --workspaces"
  }
}
```

```bash
# Install dependencies for all workspaces
npm install

# Add dependency to specific workspace
npm install lodash --workspace=packages/utils

# Run script in specific workspace
npm run build --workspace=packages/utils

# Run script in all workspaces
npm run test --workspaces

# List workspaces
npm ls --workspaces
```

### Yarn Workspaces
```json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": {
    "packages": [
      "packages/*",
      "apps/*"
    ]
  }
}
```

```bash
# Install all dependencies
yarn install

# Add dependency to workspace
yarn workspace @myorg/utils add lodash

# Run script in workspace
yarn workspace @myorg/utils build

# Run script in all workspaces
yarn workspaces run build

# Show workspace info
yarn workspaces info
```

### pnpm Workspaces
```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

```bash
# Install all dependencies
pnpm install

# Add dependency to workspace
pnpm add lodash --filter @myorg/utils

# Run script in workspace
pnpm --filter @myorg/utils build

# Run script in all workspaces
pnpm -r build

# Run in parallel
pnpm -r --parallel build
```

## Common Issues & Solutions

### Issue: Module Not Found
```bash
# Check if package is installed
npm list package-name

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force
npm install

# Check NODE_PATH
echo $NODE_PATH

# Fix: Ensure package is in dependencies
npm install package-name
```

### Issue: Version Conflicts
```bash
# Check for conflicts
npm ls package-name

# Force resolution (package.json)
{
  "overrides": {
    "package-name": "1.2.3"
  }
}

# Yarn resolutions
{
  "resolutions": {
    "package-name": "1.2.3"
  }
}

# pnpm overrides
{
  "pnpm": {
    "overrides": {
      "package-name": "1.2.3"
    }
  }
}
```

### Issue: Peer Dependency Warnings
```bash
# npm 7+ treats peer dependencies as regular dependencies
# To use legacy behavior:
npm install --legacy-peer-deps

# Or set in .npmrc
echo "legacy-peer-deps=true" >> .npmrc

# Install peer dependencies manually
npm install peer-dependency-name
```

### Issue: EACCES Permission Errors
```bash
# Don't use sudo! Fix permissions instead

# Option 1: Change npm directory
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Option 2: Fix ownership
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) /usr/local/lib/node_modules
```

### Issue: Corrupted node_modules
```bash
# Complete cleanup
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Verify installation
npm list
npm doctor

# Check disk space
df -h
```

### Issue: Slow Installation
```bash
# Use pnpm (fastest)
npm install -g pnpm
pnpm install

# Use offline cache
npm install --prefer-offline

# Skip optional dependencies
npm install --no-optional

# Parallel installation
npm install --legacy-peer-deps

# Use CI mode
npm ci  # Faster, uses lock file
```

## Performance Optimization

### .npmrc Configuration
```bash
# .npmrc file
registry=https://registry.npmjs.org/
save-exact=true
progress=false
loglevel=error
engine-strict=true
legacy-peer-deps=false
fund=false
audit=true
```

### Package Installation Optimization
```bash
# Use npm ci in CI/CD (10x faster)
npm ci

# Skip post-install scripts (when safe)
npm install --ignore-scripts

# Use production mode
npm install --production

# Prefer offline
npm install --prefer-offline

# Use package manager cache
# npm: ~/.npm
# yarn: ~/.yarn/cache
# pnpm: ~/.pnpm-store
```

### Bundle Size Optimization
```bash
# Analyze bundle size
npx webpack-bundle-analyzer

# Check package size before installing
npx package-size lodash moment date-fns

# Find duplicate packages
npx find-duplicate-packages

# Use bundle size tools
npm install --save-dev bundle-size
npx bundle-size

# Alternative: Use bundlephobia
# https://bundlephobia.com
```

## Publishing Packages

### Prepare for Publishing
```json
{
  "name": "@myorg/package-name",
  "version": "1.0.0",
  "description": "Package description",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "prepublishOnly": "npm run build && npm test",
    "prepare": "npm run build"
  },
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/"
  }
}
```

### Publishing Workflow
```bash
# Login to npm
npm login

# Check what will be published
npm pack --dry-run

# Update version
npm version patch  # 1.0.0 -> 1.0.1
npm version minor  # 1.0.0 -> 1.1.0
npm version major  # 1.0.0 -> 2.0.0

# Publish
npm publish

# Publish scoped package
npm publish --access public

# Publish with tag
npm publish --tag beta

# View published package
npm view @myorg/package-name
```

## Migration Between Package Managers

### npm to Yarn
```bash
# Install Yarn
npm install -g yarn

# Import from package-lock.json
yarn import

# Or fresh install
rm package-lock.json
yarn install
```

### npm to pnpm
```bash
# Install pnpm
npm install -g pnpm

# Import from package-lock.json
pnpm import

# Or fresh install
rm package-lock.json
pnpm install
```

### Yarn to npm
```bash
# Remove Yarn files
rm yarn.lock

# Install with npm
npm install
```

## Scripts and Automation

### Complex Script Examples
```json
{
  "scripts": {
    "// Parallel execution": "",
    "dev": "concurrently \"npm:dev:*\"",
    "dev:server": "nodemon src/server.ts",
    "dev:client": "vite",

    "// Sequential execution": "",
    "build": "npm run clean && npm run build:tsc && npm run build:bundle",
    "build:tsc": "tsc",
    "build:bundle": "webpack",

    "// Cross-platform commands": "",
    "clean": "rimraf dist",
    "copy": "copyfiles -u 1 src/**/*.json dist",

    "// Environment-specific": "",
    "start:dev": "NODE_ENV=development node dist/index.js",
    "start:prod": "NODE_ENV=production node dist/index.js",

    "// With arguments": "",
    "test": "jest",
    "test:file": "jest --",
    "// Usage: npm run test:file path/to/test.js"
  }
}
```

### Custom npm Scripts
```bash
# Run with npm run
npm run build

# Pass arguments
npm run test -- --watch
npm run test:file -- src/utils.test.js

# Run multiple scripts
npm run build && npm test

# Run in parallel (with npm-run-all)
npm install --save-dev npm-run-all
npm-run-all --parallel dev:*
```

## Best Practices Summary

### Package Management
- Always commit lock files (package-lock.json, yarn.lock, pnpm-lock.yaml)
- Use exact versions in production (`npm install --save-exact`)
- Pin Node.js version with .nvmrc
- Use `npm ci` in CI/CD for faster, reliable installs
- Keep dependencies minimal (check bundle size)
- Separate dev and production dependencies

### Security
- Run `npm audit` regularly
- Keep dependencies updated
- Review dependency changes before updating
- Use lock files for reproducible builds
- Don't commit node_modules or .env files
- Use `npx` instead of global installs when possible

### Performance
- Use pnpm for fastest installation
- Leverage offline cache when possible
- Use `npm ci` in CI/CD
- Consider Yarn PnP for zero-installs
- Analyze and optimize bundle size

### Project Organization
- Use clear, descriptive script names
- Document complex scripts in README
- Use workspaces for monorepos
- Follow semantic versioning
- Include engines field for Node version requirements

## Quick Reference Commands

```bash
# Installation
npm install                  # Install all dependencies
npm install <package>        # Install package
npm install -D <package>     # Install as dev dependency
npm install -g <package>     # Install globally
npm ci                       # Clean install from lock file

# Updating
npm update                   # Update all packages
npm update <package>         # Update specific package
npm outdated                 # Check for outdated packages

# Removal
npm uninstall <package>      # Remove package
npm prune                    # Remove unused packages

# Information
npm list                     # List installed packages
npm view <package>           # View package info
npm search <package>         # Search for packages

# Scripts
npm run <script>             # Run script
npm test                     # Run tests
npm start                    # Start app

# Security
npm audit                    # Check for vulnerabilities
npm audit fix                # Fix vulnerabilities

# Cache
npm cache clean --force      # Clear cache
npm cache verify             # Verify cache

# Publishing
npm login                    # Login to registry
npm publish                  # Publish package
npm version <type>           # Bump version
```

## Notes

- Use npm ci in CI/CD for consistent, fast installs
- Always commit lock files to version control
- Prefer exact versions for production dependencies
- Use workspaces for monorepo management
- Regularly audit dependencies for security
- Keep Node.js and package managers updated
- Use .nvmrc to specify Node.js version
- Consider pnpm for better performance and disk usage
- Use semantic versioning for package releases
- Document all custom scripts in README
