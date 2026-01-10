# GitHub Actions Setup and Configuration Guide

## Overview

GitHub Actions automates Docusaurus site building and deployment to GitHub Pages on every push to the main branch.

## Workflow Configuration

Create `.github/workflows/deploy.yml` in your repository root using eactly the template in `references/deploy-workflow.yml`.

### Key Workflow Features

**Trigger**: Push to main branch only
- Workflow runs automatically when code is pushed to main
- Can also be triggered manually from Actions tab

**Node.js Setup**: Version matching package.json engines field
- Uses Node.js v20 (or specified version)
- Caches npm dependencies for faster builds

**Installation**: Uses `npm ci` for clean, reproducible installs
- `npm ci` uses exact versions from package-lock.json
- Ensures consistency between local and CI environments

**Type Checking**: Runs `npm run typecheck` before build
- Validates TypeScript before production build
- Prevents type errors from reaching production

**Build**: Executes `npm run build`
- Creates optimized static files in `/build` directory
- Fails fast if build errors occur

**Deployment**: Uses `actions/deploy-pages@v4`
- Officially supported GitHub action for Pages deployment
- Handles artifact uploading and deployment
- Integrates with GitHub Pages settings

**Permissions**: Proper read/write permissions
- `contents: read` - Read repository contents
- `pages: write` - Write to GitHub Pages
- `id-token: write` - Identity token for deployment

## Workflow Explanation

### Jobs

The workflow has two jobs that run sequentially:

#### 1. Build Job
```yaml
build:
  name: Build Docusaurus
  runs-on: ubuntu-latest
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: 'website/package-lock.json'

    - name: Install dependencies
      working-directory: website
      run: npm ci

    - name: Build website
      working-directory: website
      run: npm run build

    - name: Upload build artifact
      uses: actions/upload-pages-artifact@v3
      with:
        path: website/build
```

**What it does**:
1. Checks out code from repository
2. Sets up Node.js environment
3. Installs dependencies
4. Builds the site
5. Uploads build artifacts for deployment

**Working Directory**: `book-soruce` - Adjust if Docusaurus is in different subdirectory

#### 2. Deploy Job
```yaml
deploy:
  name: Deploy to GitHub Pages
  needs: build
  if: github.event_name == 'push' && (github.ref == 'refs/heads/main')
  environment:
    name: github-pages
    url: ${{ steps.deployment.outputs.page_url }}
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
```

**What it does**:
1. Waits for build job to complete successfully
2. Only runs on pushes to main branch
3. Sets deployment environment
4. Deploys to GitHub Pages

## Setting Up the Workflow

### Step 1: Create Workflow File

Create file at `.github/workflows/deploy.yml`:

```bash
mkdir -p .github/workflows
# Copy or create deploy.yml - see references/deploy-workflow.yml
```

### Step 2: Adjust Working Directory (if needed)

If Docusaurus is not in a `apps/learn-app/` subdirectory, update workflow:

```yaml
- name: Install dependencies
  working-directory: ./apps/learn-app  # or your actual directory
  run: npm ci

- name: Build website
  working-directory: ./apps/learn-app
  run: npm run build

- name: Upload build artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: ./apps/learn-app/build/  # Adjust path based on location
```

### Step 3: Commit and Push

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions deployment workflow"
git push origin main
```

### Step 4: Configure GitHub Pages

In repository Settings:

1. Navigate to **Settings → Pages**
2. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
   - Alternatively: Select "Deploy from a branch" and choose `gh-pages` branch
3. Configure custom domain if needed (optional)
4. Enable branch protection:
   - Protect main branch
   - Require status checks to pass before merging

## Monitoring Deployments

### View Workflow Runs

1. Go to repository → **Actions** tab
2. See list of workflow runs with status (success/failure)
3. Click run to view details and logs

### Check Specific Workflow Steps

1. Click on a workflow run
2. Expand "Build Docusaurus" section to see:
   - Checkout
   - Setup Node.js
   - Install dependencies
   - Type checking (if configured)
   - Build website
   - Upload artifact

3. Expand "Deploy to GitHub Pages" section
4. Click step to view detailed logs

### View Deployment URL

After successful deployment, the Actions tab shows:
- Deployment environment: "github-pages"
- Deployment URL: `https://username.github.io/repo-name`

## Troubleshooting GitHub Actions

### Workflow Doesn't Trigger

**Problem**: Workflow file exists but doesn't run

**Solution**:
1. **Verify workflow file location**: Must be at `.github/workflows/deploy.yml` (not in subdirectory)
2. **Check file syntax**: YAML must be valid (use YAML linter online)
3. **Verify trigger conditions**: Workflow should trigger on push to main branch
4. **Check branch protection**: If branch protection runs checks, ensure they can complete

**Diagnosis**:
```bash
# Verify file exists
cat .github/workflows/deploy.yml

# Check git status
git status
```

### Build Step Fails

**Problem**: Build job shows red X (failed)

**Solution**:
1. **Check working directory**: Ensure `working-directory` matches Docusaurus location
2. **Verify Node.js version**: Check `engines.node` in package.json
3. **Review build logs**:
   - Click workflow run → "Build Docusaurus" → "Build website"
   - Look for error messages
   - Common issues: missing dependencies, TypeScript errors, MDX syntax errors

**Common causes**:
- Missing `npm ci` - dependencies not installed
- Wrong Node.js version - specified version doesn't match package.json
- Type errors - TypeScript compilation fails
- MDX syntax errors - invalid Markdown/JSX

### Deploy Step Fails

**Problem**: Build succeeds but deployment fails

**Solution**:
1. **Verify permissions**: Ensure workflow has `pages: write` permission
2. **Check GitHub Pages settings**:
   - Go to Settings → Pages
   - Source should be "GitHub Actions"
   - Ensure no custom domain conflicts
3. **Review deploy logs**:
   - Click workflow run → "Deploy to GitHub Pages"
   - Look for permission or configuration errors

### Site Shows 404 After Deployment

**Problem**: Deployment appears successful but site doesn't load

**Solution**:
1. **Verify baseUrl configuration**:
   - For `https://username.github.io/repo-name`: baseUrl should be `/repo-name/`
   - For `https://username.github.io`: baseUrl should be `/`
2. **Check GitHub Pages settings**:
   - Verify source is set to "GitHub Actions"
   - Check deployment history shows recent successful deployment
3. **Verify build output**:
   - Download artifact from workflow run
   - Ensure `index.html` exists in build directory
   - Check that all assets are included

### Workflow Runs but No Deployment

**Problem**: Build succeeds but site doesn't update

**Solution**:
1. **Check deployment status**:
   - Go to Settings → Deployments
   - See if latest deployment shows "Active"
   - Review deployment history
2. **Verify build directory path**:
   - Ensure upload artifact path matches actual build location
   - Check workflow logs for artifact upload success
3. **Clear browser cache**:
   - Hard refresh browser: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows)
   - Check incognito window to verify new content

## Performance Optimization

### Caching

The workflow caches npm dependencies to speed up builds:

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
    cache-dependency-path: 'website/package-lock.json'
```

**Benefits**:
- First run: Full install (~30-60 seconds)
- Subsequent runs: Use cache (~5-10 seconds)
- Cache invalidates when package-lock.json changes

### Build Time Optimization

To reduce build time:

1. **Remove unused plugins**: Disable unnecessary Docusaurus plugins
2. **Optimize dependencies**: Only include needed packages
3. **Minimize documentation files**: Reduce number of pages if possible
4. **Use build caching**: Ensure workflow includes npm cache configuration

### Artifact Upload Optimization

The workflow automatically compresses and uploads build artifacts:
- Small sites: < 1 minute upload
- Large sites: 1-5 minutes depending on size
- Artifacts stored securely in GitHub

## Integration with Repository

### Branch Protection Rules

Recommended settings in Settings → Branches → Add rule:

- Branch name pattern: `main`
- Require status checks to pass before merging:
  - Select "Build Docusaurus" workflow
- Require branches to be up to date before merging
- Allow auto-merge for convenience

This ensures:
- All changes are validated before merging
- Build failures prevent merging
- Documentation quality gates work

### Secrets and Environment Variables

If workflow needs credentials:

1. Go to Settings → Secrets and variables → Actions
2. Add repository secret: **New repository secret**
3. Name: `SECRET_NAME`
4. Value: `secret-value`
5. Use in workflow: `${{ secrets.SECRET_NAME }}`

Example for GitHub token (pre-configured):
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [GitHub Pages Documentation](https://docs.github.com/pages)
- [Docusaurus Deployment Guide](https://docusaurus.io/docs/deployment)
- [actions/setup-node Documentation](https://github.com/actions/setup-node)
- [actions/deploy-pages Documentation](https://github.com/actions/deploy-pages)
