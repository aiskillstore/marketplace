---
name: url-analysis
description: URL validation and contextual analysis specialist. Use when validating
  links, analyzing URL context, extracting links from content, or ensuring link appropriateness.
  Combines technical validation with content analysis.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# URL Analysis

This skill validates URLs both technically and contextually, ensuring links are functional and appropriate for their context.

## When to Use This Skill

- When validating URLs in content
- When analyzing link context and appropriateness
- When extracting links from documents
- When checking link functionality
- When ensuring link relevance
- When auditing link quality

## What This Skill Does

1. **Technical Validation**: Checks HTTP status, redirects, SSL
2. **Contextual Analysis**: Evaluates link appropriateness
3. **Link Extraction**: Extracts and categorizes links
4. **Content Relevance**: Checks if linked content matches context
5. **Security Analysis**: Identifies security concerns
6. **Quality Assessment**: Provides link quality scores

## Helper Scripts

This skill includes Python helper scripts in `scripts/`:

- **`validate_urls.py`**: Validates URLs from files or command line. Checks HTTP status codes, redirects, and accessibility. Outputs JSON with validation results.

  ```bash
  # Validate URLs from file
  python scripts/validate_urls.py document.md

  # Validate single URL
  python scripts/validate_urls.py --url https://example.com
  ```

## How to Use

### Validate URLs

```
Validate all URLs in this document
```

```
Check if these links are appropriate for their context
```

### Specific Analysis

```
Extract and analyze all links in this content
```

## Analysis Process

### Technical Validation

**Using Helper Script:**

The skill includes a Python helper script for URL validation:

```bash
# Validate URLs from a file
python scripts/validate_urls.py document.md

# Validate a single URL
python scripts/validate_urls.py --url https://example.com
```

**Checks:**

- HTTP status codes (200, 301, 404, etc.)
- Redirect chains
- Response times
- SSL certificate validity
- URL syntax validity

### Contextual Analysis

**Evaluates:**

- Link text vs. destination content
- Semantic alignment
- Publication date relevance
- Authority of source
- Value to reader

### Link Extraction

**Categorizes:**

- Internal vs. external links
- Anchor links
- File downloads
- API endpoints

## Examples

### Example 1: URL Validation

**Input**: Validate URLs in blog post

**Output**:

```markdown
## URL Analysis: Blog Post

### Technical Validation

**1. https://example.com/article**
- **Status**: 200 OK
- **Response Time**: 320ms
- **SSL**: Valid
- **Redirects**: None

**2. https://old-site.com/page**
- **Status**: 301 → https://new-site.com/page
- **Issue**: Redirect chain (should update link)
- **Fix**: Update to final destination

**3. https://broken-link.com**
- **Status**: 404 Not Found
- **Issue**: Broken link
- **Fix**: Remove or find alternative

### Contextual Analysis

**4. https://example.com/article**
- **Link Text**: "Learn more about React"
- **Destination**: React documentation
- **Relevance**: High ✓
- **Status**: Appropriate

**5. https://example.com/homepage**
- **Link Text**: "Advanced React patterns"
- **Destination**: Homepage (not specific article)
- **Relevance**: Low ✗
- **Issue**: Link text doesn't match destination
- **Fix**: Link to specific article or update link text
```

## Best Practices

### URL Validation

1. **Check Status**: Verify all links return 200 or appropriate redirect
2. **Update Redirects**: Use final destination, not redirect chains
3. **Context Matters**: Ensure links match their context
4. **Security**: Prefer HTTPS, check SSL validity
5. **Relevance**: Verify linked content matches expectations

## Related Use Cases

- Link validation
- Content quality assurance
- SEO link auditing
- Documentation review
- Link extraction and analysis
