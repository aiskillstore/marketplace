# Performance Standards and Best Practices

## Pre-Deployment Validation Checklist

### Configuration
- [ ] docusaurus.config.ts is valid TypeScript
- [ ] url and baseUrl match GitHub Pages deployment target
- [ ] organizationName and projectName are correct
- [ ] deploymentBranch is set to 'gh-pages' (project) or 'main'/'master' (user pages)
- [ ] trailingSlash is set consistently
- [ ] TypeScript includes typescript in devDependencies

### Build
- [ ] `npm run typecheck` passes with no errors
- [ ] `npm run build` completes successfully
- [ ] `/build` directory contains complete site files
- [ ] Build completes in < 30 seconds
- [ ] No critical warnings in build output
- [ ] Package.json specifies correct Node.js version in engines field

### Content
- [ ] All documentation files follow naming conventions (kebab-case)
- [ ] Frontmatter is complete in all files (title, sidebar_position, description)
- [ ] No broken internal links
- [ ] MDX syntax is valid
- [ ] Images and assets load correctly
- [ ] Sidebar references match actual file names and IDs
- [ ] All .md/.mdx files have proper frontmatter

### Local Testing
- [ ] `npm run serve` starts without errors
- [ ] Site loads on `http://localhost:3000`
- [ ] All navigation works correctly
- [ ] Internal links resolve properly
- [ ] Responsive design works on different screen sizes
- [ ] Search functionality works (if enabled)
- [ ] Dark mode toggle works (if enabled)
- [ ] No console errors in browser DevTools

### GitHub Setup
- [ ] `.github/workflows/deploy.yml` exists and is valid
- [ ] Workflow file location: `.github/workflows/deploy.yml` (repository root)
- [ ] GitHub Pages configured to use GitHub Actions source
- [ ] Branch protection enabled on main/master
- [ ] Status checks required to pass before merging
- [ ] No custom domain conflicts with GitHub Pages settings

## Performance Targets

### Build Performance
- **Build Time**: < 30 seconds for typical documentation sites
  - Target: 10-20 seconds with caching
  - First run: 30-60 seconds (installs dependencies)
  - Subsequent runs: 5-15 seconds (uses cache)

- **Deployment Time**: < 5 minutes total end-to-end
  - Build: 10-20 seconds
  - Upload artifact: 30-60 seconds
  - Deploy to Pages: 1-2 minutes
  - Total: 2-4 minutes typical

### Page Performance
- **Initial Page Load**: < 3 seconds
  - HTML parsing: < 500ms
  - CSS rendering: < 500ms
  - JavaScript execution: < 1 second
  - Network latency: < 500ms

- **Navigation**: Instant (< 100ms)
  - Client-side routing
  - Pre-rendered static pages
  - No server requests needed

### Bundle Size
- **HTML Files**: Optimized for documentation content
  - Typical page: 50-150 KB (gzipped)
  - Large page: < 500 KB

- **JavaScript**: Minimal overhead
  - Framework: ~50-100 KB (gzipped)
  - Plugins: ~20-50 KB (gzipped)
  - Total JS: < 200 KB (gzipped)

- **CSS**: Scoped and optimized
  - Framework CSS: ~10-30 KB (gzipped)
  - Custom CSS: < 20 KB (gzipped)
  - Total CSS: < 50 KB (gzipped)

- **Assets**:
  - Images: Optimize to < 2 MB each
  - Total assets: < 10 MB recommended
  - Consider lazy loading for large images

### Accessibility
- **WCAG 2.1 AA Compliance**:
  - Color contrast: 4.5:1 for text
  - Heading hierarchy: Proper nesting
  - Alt text: All images have descriptions
  - Keyboard navigation: Full functionality
  - Screen reader: Compatible markup

- **Testing**:
  - Use WAVE browser extension for analysis
  - Test with keyboard only navigation
  - Test with screen reader
  - Validate HTML structure

## Optimization Techniques

### Build Optimization

**Reduce Build Time**:
1. **Remove unused plugins**: Disable Docusaurus plugins you don't use
```typescript
presets: [
  [
    'classic',
    {
      // Only enable what you need
      docs: { /* ... */ },
      blog: false,  // Disable if not used
      theme: { /* ... */ },
    }
  ]
]
```

2. **Optimize dependencies**: Use only necessary packages
```bash
# Audit for unused dependencies
npm audit
npm ls --depth=0

# Remove unused packages
npm uninstall unused-package
```

3. **Lazy load assets**: Load images/videos only when visible
```markdown
![Image](./image.jpg)  <!-- Browser lazy loads by default -->
```

### Content Optimization

**Reduce Bundle Size**:
1. **Optimize images**:
```bash
# Use tools like ImageOptim or jpegoptim
# Reduce PNG files by 50-70%
# Reduce JPEG files by 20-30%
```

2. **Minimize documentation files**:
   - Break large docs into smaller pages
   - Use headings to structure content
   - Link related documents instead of duplicating

3. **Optimize MDX**: Use lightweight components
```markdown
<!-- Good - lightweight HTML -->
<div className="info">Content</div>

<!-- Avoid - heavy component overhead -->
<HeavyComponent prop1="value" prop2="value" {...otherProps} />
```

### Caching Strategy

**Local Development**:
- npm caches dependencies automatically
- Docusaurus caches build artifacts
- Clear cache if issues: `npm run clear`

**GitHub Actions**:
- Workflow automatically caches npm dependencies
- Cache invalidates when package-lock.json changes
- Subsequent builds use cache for 30-50% faster builds

**GitHub Pages**:
- Static files cached by CDN (Fastly)
- Cache busting via versioned assets
- Propagation time: < 1 minute typically

### Monitoring Performance

**Local Testing**:
```bash
# Check build time
time npm run build

# Check file sizes
du -sh build/
ls -lh build/*.html

# Check with Lighthouse
npm run serve  # Then use browser Lighthouse tool
```

**GitHub Actions**:
1. View workflow run time: Go to Actions tab
2. Expand each step to see duration
3. Total time from push to live: ~2-4 minutes

**Production Monitoring**:
- Use browser DevTools: Lighthouse tab
- Check network tab: Asset sizes and load times
- Monitor with external tool: GTmetrix, PageSpeed Insights

## Standards and Conventions

### File Naming
- **Documentation files**: kebab-case-format.md
  - Example: `getting-started.md`, `api-reference.md`
- **Folders**: kebab-case-format/
  - Example: `user-guide/`, `advanced-topics/`
- **Assets**: kebab-case-format.ext
  - Example: `feature-diagram.png`, `code-example.ts`

### Frontmatter Format
```markdown
---
title: Page Title (shown in browser and sidebar)
sidebar_position: 1  (order in sidebar, lower = earlier)
description: Brief summary for meta tags
keywords: tag1, tag2  (optional)
---

# Page Title

Content here...
```

### Sidebar Organization
- Group related documents in categories
- Use meaningful labels
- Order logically: overview → basics → advanced
- Keep sidebar depth reasonable (< 4 levels)

### Link Usage
```markdown
<!-- Internal links - use relative paths -->
[About](../about)
[Details](./details.md)
[Reference](../api/reference)

<!-- External links - use full URLs -->
[GitHub](https://github.com)
[Docs](https://example.com/docs)
```

### Code Blocks
```markdown
<!-- Specify language for syntax highlighting -->
\`\`\`typescript
function example() {
  console.log("Hello");
}
\`\`\`

<!-- Highlight specific lines -->
\`\`\`typescript {2,4}
function example() {
  console.log("Line 2");
  function nested() {
    console.log("Line 4");
  }
}
\`\`\`
```

## Quality Gates

### Before Each Commit
- [ ] No console errors: `npm run serve` shows clean console
- [ ] All links work: Tested in browser
- [ ] Formatting correct: Code blocks render properly
- [ ] Images display: All assets load

### Before Each Push
- [ ] Type checking passes: `npm run typecheck` clean
- [ ] Build succeeds: `npm run build` completes
- [ ] Artifacts validated: Check `/build` directory
- [ ] Content reviewed: Spelling and grammar checked

### Before Merge to Main
- [ ] All tests pass: `npm run typecheck` and `npm run build`
- [ ] Content approved: Team review if applicable
- [ ] No conflicts: Branch is up to date with main
- [ ] CI passes: GitHub Actions workflow succeeds

## Maintenance Schedule

### Weekly
- [ ] Monitor build times
- [ ] Check for dependency updates: `npm outdated`
- [ ] Review GitHub Actions workflow runs
- [ ] Check for broken links in live site

### Monthly
- [ ] Update minor dependencies: `npm update`
- [ ] Review and update outdated content
- [ ] Audit images and optimize if needed
- [ ] Test accessibility compliance
- [ ] Review analytics/usage patterns

### Quarterly
- [ ] Audit major dependencies for updates
- [ ] Review and update Docusaurus version
- [ ] Comprehensive content review
- [ ] Security audit
- [ ] Performance benchmarking

## Troubleshooting Performance Issues

### Slow Builds (> 30 seconds)
1. Identify slow plugins in build output
2. Remove or optimize problematic plugins
3. Check for large image files
4. Verify system has sufficient resources
5. Clear cache and retry: `npm run clear && npm run build`

### Slow Page Load (> 3 seconds)
1. Check network tab in DevTools
2. Optimize images: Use modern formats (WebP)
3. Lazy load below-fold content
4. Minimize JavaScript bundle
5. Enable browser caching

### High Memory Usage
1. Reduce number of documentation files
2. Split large documents into multiple pages
3. Disable unused plugins
4. Increase system swap space
5. Close other applications during build

### GitHub Actions Timeout
1. Typical timeout: 360 minutes (6 hours)
2. If approaching: Optimize build process
3. Clear cache and retry
4. Check for stuck processes: `ps aux | grep npm`
5. Contact GitHub support if persistent
