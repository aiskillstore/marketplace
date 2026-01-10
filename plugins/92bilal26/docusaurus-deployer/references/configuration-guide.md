# Docusaurus GitHub Pages Configuration Guide

## Overview

Configure Docusaurus for GitHub Pages deployment by updating `docusaurus.config.ts` with the appropriate settings for the deployment target.

## Configuration Template

Update the Docusaurus config file (`docusaurus.config.ts`) with GitHub Pages-specific settings:

```typescript
const config: Config = {
  title: 'Your Documentation Title',
  tagline: 'Documentation description',
  favicon: 'img/favicon.ico',

  // GitHub Pages configuration
  url: 'https://username.github.io', // or 'https://username.github.io/repo-name' for project repos
  baseUrl: '/', // or '/<repository-name>/' for project repos
  organizationName: 'your-github-org-or-username',
  projectName: 'your-repository-name',
  deploymentBranch: 'gh-pages', // The branch GitHub Pages will serve from
  trailingSlash: false,

  // ... rest of configuration
};
```

## Configuration Guidelines by Deployment Type

### User/Organization Pages

For repositories named `username.github.io` or `orgname.github.io`:

```typescript
const config: Config = {
  url: 'https://username.github.io',
  baseUrl: '/',
  organizationName: 'username',
  projectName: 'username.github.io',
  deploymentBranch: 'main', // or 'master'
  // ... rest of config
};
```

**Key Points:**
- `baseUrl` is `/` (at root)
- `projectName` matches the repository name exactly
- Can deploy from `main`, `master`, or `gh-pages` branch

### Project Pages

For repositories with separate names (e.g., `my-docs`, `documentation`, `agentic-ai`):

```typescript
const config: Config = {
  url: 'https://username.github.io/repo-name',
  baseUrl: '/repo-name/',
  organizationName: 'username',
  projectName: 'repo-name',
  deploymentBranch: 'gh-pages',
  // ... rest of config
};
```

**Key Points:**
- `baseUrl` includes the repository name with trailing slash: `/repo-name/`
- `projectName` matches the repository name exactly
- Always use `gh-pages` as deployment branch for project repositories

## Project Analysis Checklist

Before updating configuration, verify:

- **Docusaurus configuration file exists**: `docusaurus.config.ts` or `docusaurus.config.js`
- **Sidebar configuration is present**: `sidebars.js` or `sidebars.ts`
- **Package.json specifies correct Node.js version**: Check `engines.node` field (typically v20+)
- **All required dependencies are listed**: Including `@docusaurus/core`, `@docusaurus/preset-classic`, etc.

## Configuration Best Practices

### URL Configuration
- **User/Organization Pages**: `url` = `https://username.github.io`, `baseUrl` = `/`, `projectName` = `username.github.io`
- **Project Pages**: `url` = `https://username.github.io/repo-name`, `baseUrl` = `/repo-name/`, `projectName` = `repo-name`

### Deployment Settings
- Always use `gh-pages` as the deployment branch for project repositories
- For user/organization pages, can use `main` or `master` branch
- Ensure TypeScript configuration includes `typescript` in devDependencies

### File Organization
- Ensure Docusaurus config is at the root of the docs subdirectory (e.g., `website/docusaurus.config.ts`)
- Verify `sidebars.ts` exists and properly references all documentation files
- Check that documentation files follow naming conventions (kebab-case for files)

## Common Configuration Issues

### Incorrect baseUrl

**Problem**: Site deploys but shows 404 or broken links

**Solution**: Verify baseUrl matches deployment target:
- For `https://username.github.io/repo-name`: baseUrl should be `/repo-name/`
- For `https://username.github.io`: baseUrl should be `/`

### Type Errors in docusaurus.config.ts

**Problem**: TypeScript errors prevent build

**Solution**:
1. Verify all imported types are properly declared
2. Check Config type definition: `import type { Config } from "@docusaurus/types"`
3. Ensure all config properties match the current Docusaurus version
4. Run `npm run typecheck` to identify specific errors

### Plugin Incompatibilities

**Problem**: Plugin conflicts or version mismatches

**Solution**:
1. Verify plugin versions match installed Docusaurus version
2. Check plugin documentation for configuration requirements
3. Review error messages for plugin-specific issues
4. Update plugins to compatible versions if needed

## Customization Examples

### Adding Custom Domain

To use a custom domain instead of `username.github.io/repo-name`:

1. Update config:
```typescript
const config: Config = {
  url: 'https://your-custom-domain.com',
  baseUrl: '/',
  // ... rest of config
};
```

2. Add CNAME file in static directory: `static/CNAME`
3. Configure custom domain in GitHub repository settings

### Modifying Preset Options

Customize the classic preset in `docusaurus.config.ts`:

```typescript
presets: [
  [
    'classic',
    {
      docs: {
        sidebarPath: './sidebars.ts',
        editUrl: 'https://github.com/username/repo/tree/main/docs/',
      },
      blog: {
        showReadingTime: true,
      },
      theme: {
        customCss: './src/css/custom.css',
      },
    } satisfies Preset.Options,
  ],
],
```

## Verification Checklist

After updating configuration:

- [ ] `docusaurus.config.ts` is valid TypeScript (no type errors)
- [ ] `url` and `baseUrl` match your GitHub Pages deployment target
- [ ] `organizationName` and `projectName` are correct
- [ ] `deploymentBranch` is set to appropriate branch ('gh-pages' for projects, 'main'/'master' for user pages)
- [ ] `trailingSlash` is set to false for consistency
- [ ] `npm run typecheck` passes with no errors
- [ ] `npm run build` completes successfully
