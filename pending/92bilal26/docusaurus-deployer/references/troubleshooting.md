# Troubleshooting Common Deployment Issues

## Build Fails Locally

### Problem
`npm run build` fails with errors

### Solution Steps
1. Verify Node.js version: `node --version` should match `engines.node` in package.json
2. Run type checking: `npm run typecheck` to identify TypeScript errors
3. Check dependencies: `npm ls` to verify all packages are installed correctly
4. Clear cache: `rm -rf node_modules package-lock.json && npm ci`
5. Review error messages for specific issues (missing imports, syntax errors, plugin conflicts)

### Common Causes
- Missing dependencies in package.json
- TypeScript configuration errors
- Plugin compatibility issues
- Markdown/MDX syntax errors in documentation files
- Broken import paths in configuration files

---

## Type Checking Errors

### Problem
`npm run typecheck` reports type errors

### Solution
1. Review error messages carefully - they indicate exact file and line numbers
2. Fix TypeScript errors before attempting build
3. Verify all imported types are properly declared
4. Check docusaurus.config.ts for proper Config type definition
5. Ensure plugin types match installed plugin versions

### Example Fix
If you get an error like `Cannot find name 'Config'`:
```typescript
// Add this import
import type { Config } from "@docusaurus/types";

// Then use it
const config: Config = {
  // ... configuration
};
```

---

## Site Not Found (404) After Deployment

### Problem
Site shows 404 or doesn't load after GitHub Actions deployment

### Solution Steps
1. **Verify baseUrl configuration**:
   - For `https://username.github.io/repo-name`: baseUrl should be `/repo-name/`
   - For `https://username.github.io`: baseUrl should be `/`
2. **Check deployment branch**:
   - Verify `gh-pages` branch exists in repository
   - Confirm GitHub Pages is set to deploy from correct branch in Settings → Pages
3. **Review GitHub Actions logs**:
   - Check Actions tab for workflow failures
   - Look for errors in build or deployment steps
4. **Verify build output**:
   - Confirm `/build` directory was created with content
   - Check that index.html exists in build directory

### Diagnostic Steps
```bash
# Check if gh-pages branch exists
git branch -r | grep gh-pages

# Check recent deployments
gh run list --workflow=deploy.yml --limit=5
```

---

## Broken Links on Deployed Site

### Problem
Internal links don't work or links are broken

### Solution
1. **Verify relative paths**: Ensure all internal links use relative paths or respect baseUrl
2. **Test locally first**: Run `npm run serve` and test all links before pushing
3. **Check frontmatter**: Verify all documents have proper sidebar_position and IDs
4. **Validate sidebar configuration**: Ensure sidebar references match actual file paths
5. **Check MDX syntax**: Verify link syntax is correct: `[text](./path)` not hardcoded URLs

### Link Syntax Examples
```markdown
// Good - relative link
[About](../about)

// Good - relative from current file
[Details](./details.md)

// Bad - hardcoded URL
[Home](https://username.github.io/repo-name/docs/intro)

// Bad - missing relative marker
[Contact](contact)
```

---

## GitHub Actions Workflow Issues

### Problem
GitHub Actions workflow fails or doesn't trigger

### Solution
1. **Verify workflow file location**: Must be at `.github/workflows/deploy.yml` (repository root, not subdirectory)
2. **Check workflow permissions**:
   - Ensure workflow has pages:write and id-token:write permissions
   - GITHUB_TOKEN should be auto-granted by GitHub
3. **Review workflow logs**:
   - Go to Actions tab and view step-by-step logs
   - Look for specific error messages in failed steps
4. **Verify trigger conditions**:
   - Workflow should trigger on push to main branch
   - Check branch protection rules don't prevent workflow completion
5. **Validate working directories**:
   - If Docusaurus is in subdirectory, set `working-directory` in workflow steps

### Diagnostic Steps
```bash
# Check workflow file syntax (must be valid YAML)
cat .github/workflows/deploy.yml

# View recent workflow runs
gh run list --workflow=deploy.yml --limit=5

# View specific workflow run details
gh run view <RUN_ID> --log
```

---

## Build Performance Issues

### Problem
Build takes too long (> 30 seconds)

### Solution
1. **Analyze build output**: Check if specific plugins or operations are slow
2. **Optimize dependencies**: Remove unused plugins and dependencies
3. **Check file count**: Excessive documentation files can slow builds
4. **Verify system resources**: Ensure sufficient RAM and disk space available
5. **Use npm cache**: GitHub Actions automatically caches npm dependencies

### Performance Optimization Checklist
- [ ] Remove unused Docusaurus plugins from docusaurus.config.ts
- [ ] Remove unused npm packages from package.json
- [ ] Reduce number of documentation files if possible
- [ ] Verify npm cache is enabled in GitHub Actions workflow
- [ ] Check for large image files (optimize before committing)

---

## Content Quality Issues

### Problem
Documentation has missing frontmatter, broken links, or syntax errors

### Checklist before Deployment
- [ ] All .md/.mdx files have frontmatter (title, sidebar_position, description)
- [ ] No hardcoded URLs in documentation (use relative links)
- [ ] MDX syntax is valid (no unclosed tags, proper component usage)
- [ ] Sidebar references match actual file names and IDs
- [ ] Images and assets exist at referenced paths
- [ ] No console errors when running `npm run serve`

### Example Valid Frontmatter
```markdown
---
title: Getting Started
sidebar_position: 1
description: Learn how to get started with this documentation
---

# Getting Started

Your content here...
```

---

## Node.js Version Mismatch

### Problem
Build fails with errors about incompatible Node.js features

### Solution
1. Check specified Node.js version in package.json:
```json
"engines": {
  "node": ">=20.0"
}
```

2. Verify local Node.js matches or exceeds requirement:
```bash
node --version
```

3. Update GitHub Actions workflow to use matching version:
```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'  # Match package.json
    cache: 'npm'
```

4. If using multiple versions, update locally:
```bash
# Using nvm (Node Version Manager)
nvm install 20
nvm use 20
```

---

## Missing Dependencies

### Problem
Build fails with `Cannot find module` errors

### Solution
1. **Install missing dependency**:
```bash
npm install missing-package-name
```

2. **Update package-lock.json**:
```bash
npm ci  # Reinstall with lock file
```

3. **Verify dependency is added to package.json**:
```bash
cat package.json | grep "missing-package-name"
```

4. **Commit both package.json and package-lock.json**:
```bash
git add package.json package-lock.json
git commit -m "Add missing dependency"
git push origin main
```

---

## Permission Denied Errors

### Problem
GitHub Actions fails with permission errors

### Solution
1. **Check workflow permissions** in `.github/workflows/deploy.yml`:
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

2. **Verify GitHub Pages settings**:
   - Go to Settings → Pages
   - Source: "GitHub Actions" (not "Deploy from a branch")
   - Ensure no custom domain conflicts

3. **Check branch protection**:
   - Settings → Branches → Add rule
   - Ensure status checks don't block deployment

---

## Empty Build Directory

### Problem
Build completes but `/build` directory is empty or missing

### Solution
1. **Verify build command**: Check `npm run build` output for errors
2. **Check build directory path**: Ensure it's not hidden or in unexpected location
```bash
ls -la build/
find . -name "build" -type d
```

3. **Verify Docusaurus configuration**: Check `docusaurus.config.ts` doesn't specify custom output directory

4. **Check for file permissions**: Ensure write permissions to build directory
```bash
ls -la .
chmod 755 .
```

---

## Deployment Succeeds but Site Doesn't Update

### Problem
Workflow shows "success" but site still shows old content

### Solution
1. **Check deployment timestamp**: Verify recent deployment in Actions tab
2. **Clear browser cache**:
   - Hard refresh: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows)
   - Check in incognito window
3. **Verify artifact upload**: Check workflow logs for successful artifact upload
4. **Check GitHub Pages deployment status**:
   - Settings → Deployments
   - Verify "Active" deployment shows latest timestamp
5. **Wait for CDN propagation**: GitHub Pages may take a few minutes to update

---

## MDX Syntax Errors

### Problem
Build fails with "Unexpected character" or MDX compilation errors

### Solution
1. **Identify problematic file**: Error message shows file path and line number
2. **Check for unescaped characters**:
   - `<` and `>` should be `&lt;` and `&gt;`
   - Curly braces in text should be escaped
3. **Validate MDX components**: Ensure all component names and props are correct
4. **Check imports**: Verify all imported components exist

### Example Fix
```markdown
// Problem
This percentage is <0.1% critical

// Solution
This percentage is &lt;0.1% critical
```

---

## Sidebar Configuration Issues

### Problem
Sidebar doesn't display correctly or references are broken

### Solution
1. **Verify sidebar file exists**: `sidebars.ts` or `sidebars.js` in root
2. **Check document IDs match**: Sidebar references must match actual document paths
3. **Validate YAML/TypeScript syntax**: Use syntax checker for `sidebars.ts`
4. **Test locally first**:
```bash
npm run serve
# Check sidebar in browser
```

5. **Common issues**:
   - Document ID doesn't match file path
   - Missing frontmatter in documents
   - Incorrect folder references

---

## Recovery Steps for Stuck Workflows

### If Workflow Keeps Failing

1. **Disable workflow temporarily**:
```bash
# Add this to workflow file
if: false  # Disable workflow
```

2. **Fix issues locally**:
```bash
npm run typecheck
npm run build
npm run serve
```

3. **Push fixes**:
```bash
git add .
git commit -m "Fix deployment issues"
git push origin main
```

4. **Re-enable workflow**:
   - Remove `if: false` line
   - Push again to trigger

---

## Getting Help

If issues persist:

1. **Check official documentation**:
   - [Docusaurus Deployment Guide](https://docusaurus.io/docs/deployment)
   - [GitHub Pages Docs](https://docs.github.com/pages)
   - [GitHub Actions Docs](https://docs.github.com/actions)

2. **Review workflow logs in detail**:
   - Go to Actions tab
   - Click failed workflow run
   - Expand each step to see full logs
   - Look for specific error messages

3. **Check repository settings**:
   - Settings → Pages: Verify source and domain
   - Settings → Branches: Check branch protection rules
   - Settings → Actions: Verify workflow permissions

4. **Test with minimal example**:
   - Create simple test page
   - Push to verify workflow works
   - Gradually add more content back
