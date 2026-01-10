# Local Validation Guide

## Overview

Validate Docusaurus configuration and build locally before pushing to GitHub. This ensures quality and prevents failed deployments.

## Step 1: Install Dependencies

Perform a clean install of dependencies:

```bash
cd path_to_docusaurus_directory
npm ci  # Use clean install for consistency
```

This ensures reproducible environments by using exact versions from `package-lock.json`.

## Step 2: Run Type Checking

Validate TypeScript configuration:

```bash
npm run typecheck
```

Expected output: No errors or type conflicts

**If errors appear**:
1. Review error messages carefully - they indicate exact file and line numbers
2. Fix TypeScript errors before attempting build
3. Verify all imported types are properly declared
4. Check docusaurus.config.ts for proper Config type definition
5. Ensure plugin types match installed plugin versions

## Step 3: Build the Site

Execute the production build:

```bash
npm run build
```

**Expected output**:
- `/build` directory created with static files
- No errors or critical warnings
- Build completes in < 30 seconds (typical performance)

**Validate build output**:
```bash
# Check that build directory exists and contains files
ls -la build/
ls -la build/index.html  # Main page should exist
```

Common issues:
- Missing dependencies in package.json
- TypeScript configuration errors
- Plugin compatibility issues
- Markdown/MDX syntax errors in documentation files
- Broken import paths in configuration files

## Step 4: Test Locally with Serve

Start the local server to test the built site:

```bash
npm run serve
```

Visit `http://localhost:3000` (or configured port) and verify:

### Page Loading
- [ ] Homepage loads without errors
- [ ] No 404 errors in browser console
- [ ] All assets load (images, CSS, JS)

### Navigation
- [ ] Navigation menu items work correctly
- [ ] All sidebar links resolve properly
- [ ] Breadcrumb navigation (if present) works
- [ ] Previous/next page navigation functions

### Links and Content
- [ ] Internal links navigate correctly
- [ ] External links open properly
- [ ] Code blocks display with syntax highlighting
- [ ] Tables and formatted content render correctly

### Responsive Design
- [ ] Layout works on desktop (1920x1080)
- [ ] Layout works on tablet (768x1024)
- [ ] Layout works on mobile (375x667)
- [ ] Touch interactions work on mobile devices

### Features
- [ ] Search functionality works (if enabled)
- [ ] Sidebar expands/collapses properly
- [ ] Dark mode toggle works (if enabled)
- [ ] Language switcher works (if enabled)

## Step 5: Validate Content Quality

Before pushing, verify documentation quality:

### Frontmatter
- [ ] All .md/.mdx files have frontmatter (title, sidebar_position, description)
- [ ] Sidebar_position values are consistent and non-duplicated
- [ ] Document IDs match sidebar references

### Links and References
- [ ] No hardcoded URLs in documentation (use relative links)
- [ ] All internal links use correct relative paths
- [ ] All referenced images exist at specified paths
- [ ] External links are current and valid

### Markdown/MDX Syntax
- [ ] MDX syntax is valid (no unclosed tags)
- [ ] Component imports are correct
- [ ] Code block syntax highlighting specified correctly
- [ ] No console errors during local serving

### File Organization
- [ ] All documentation files follow naming conventions (kebab-case)
- [ ] File structure matches sidebar configuration
- [ ] Sidebar references match actual file names and IDs
- [ ] No orphaned files not referenced in sidebar

## Step 6: Content Verification Checklist

Final quality check before deployment:

### Configuration
- [ ] docusaurus.config.ts is valid TypeScript
- [ ] url and baseUrl match GitHub Pages deployment target
- [ ] organizationName and projectName are correct
- [ ] deploymentBranch is set to 'gh-pages' (for projects) or 'main'/'master' (for user pages)

### Build
- [ ] `npm run typecheck` passes with no errors
- [ ] `npm run build` completes successfully
- [ ] `/build` directory contains complete site files
- [ ] Build completes in acceptable time (< 30 seconds)

### Content
- [ ] All documentation files follow naming conventions (kebab-case)
- [ ] Frontmatter is complete in all files (title, sidebar_position, description)
- [ ] No broken internal links
- [ ] MDX syntax is valid
- [ ] Images and assets load correctly

### Local Testing
- [ ] `npm run serve` starts without errors
- [ ] Site loads on `http://localhost:3000`
- [ ] All navigation works correctly
- [ ] Internal links resolve properly
- [ ] Responsive design works on different screen sizes
- [ ] Search functionality works (if enabled)

## Commit and Push

Only after successful local validation:

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Update documentation: [description of changes]"

# Push to main branch
git push origin main
```

This triggers the GitHub Actions workflow configured in `.github/workflows/deploy.yml`.

## Troubleshooting Local Issues

### Build Fails with Errors

**Problem**: `npm run build` returns errors

**Solution**:
1. Check Node.js version: `node --version` should match `engines.node` in package.json
2. Verify TypeScript errors: `npm run typecheck` shows exact issues
3. Check dependencies: `npm ls` to verify all packages are installed
4. Clear cache: `rm -rf node_modules package-lock.json && npm ci`
5. Review error messages for specific issues

### Server Won't Start

**Problem**: `npm run serve` fails or port already in use

**Solution**:
1. Check if port 3000 is already in use: `lsof -i :3000` (macOS/Linux) or `netstat -ano | findstr :3000` (Windows)
2. Kill the existing process or use different port: `npm run serve -- --port 3001`
3. Verify build directory exists: `ls -la build/`
4. Clear Docusaurus cache: `npm run clear` then `npm run serve`

### Content Not Displaying Correctly

**Problem**: Pages load but content is missing or malformed

**Solution**:
1. Check browser console for JavaScript errors
2. Verify all assets exist and paths are correct
3. Check MDX syntax: look for unclosed tags or invalid component usage
4. Validate sidebar references match actual document IDs
5. Check for console errors: `npm run serve` shows build-time issues

## Performance Targets

Monitor these metrics during local validation:

- **Build time**: < 30 seconds for typical documentation sites
- **Page load**: < 3 seconds for documentation pages (from `npm run serve`)
- **Bundle size**: Reasonable for documentation content
- **Accessibility**: WCAG 2.1 AA compliance (test with accessibility tools)

## Tools for Local Validation

### Browser DevTools
- Inspect element to check HTML structure
- Console for JavaScript errors
- Network tab to verify asset loading
- Lighthouse for performance and accessibility

### Command-Line Tools
- `npm run typecheck` - TypeScript validation
- `npm run build` - Production build
- `npm run serve` - Local server testing
- `npm run clear` - Clear build cache if needed

### External Tools
- [WAVE Browser Extension](https://wave.webaim.org/extension/) - Accessibility testing
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci) - Performance testing
- [Link Checker](https://www.w3.org/2013/04/checklinks) - Validate links
