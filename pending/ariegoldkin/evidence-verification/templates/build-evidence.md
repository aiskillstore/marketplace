# Build Evidence Template

Copy and fill in this template when documenting build execution evidence.

---

## Build Execution Evidence

### Basic Information

**Task/Feature:** [Brief description of what was built]
**Agent:** [Agent name that ran the build]
**Timestamp:** [YYYY-MM-DD HH:MM:SS]

### Build Command

```bash
[Exact command used to build]
# Example: npm run build
# Example: cargo build --release
# Example: go build
# Example: mvn package
```

### Build Results

**Exit Code:** [0 for success, non-zero for failure] ✅/❌

**Duration:** [time in seconds or MM:SS format]

**Errors:** [number of errors - should be 0 for success]
**Warnings:** [number of warnings]

### Artifacts Created

| Artifact | Size | Location |
|----------|------|----------|
| [filename] | [size in KB/MB] | [path] |
| [filename] | [size in KB/MB] | [path] |

**Total Bundle Size:** [total size]

### Build Output

```
[Paste first 10-20 lines of build output here]
[Include key information: compilation steps, optimizations, final summary]
```

### Environment

**Build Tool:** [e.g., Webpack, Vite, Cargo, Go, Maven]
**Build Tool Version:** [version number]
**Node/Runtime Version:** [if applicable]
**OS:** [e.g., macOS 14.0, Ubuntu 22.04, Windows 11]

### Build Configuration

**Mode:** [e.g., development, production]
**Optimizations:** [e.g., minification, tree-shaking, code splitting]
**Source Maps:** [yes/no]

### Performance Metrics (if available)

**Build Time:** [breakdown by step]
- Compilation: [time]
- Bundling: [time]
- Optimization: [time]
- Output: [time]

### Issues Found (if any)

**Errors:**
```
[List any errors that occurred]
```

**Warnings:**
```
[List any warnings - explain if safe to ignore]
```

### Evidence File

**Location:** `.claude/quality-gates/evidence/build-[timestamp].log`

### Conclusion

[✅ Build succeeded / ❌ Build failed - needs fixing]

---

## Example: Successful Production Build

### Basic Information

**Task/Feature:** Production build for e-commerce frontend
**Agent:** Frontend UI Developer
**Timestamp:** 2025-11-02 16:20:15

### Build Command

```bash
npm run build
```

### Build Results

**Exit Code:** 0 ✅

**Duration:** 24.3 seconds

**Errors:** 0
**Warnings:** 2 (safe to ignore - unused CSS classes)

### Artifacts Created

| Artifact | Size | Location |
|----------|------|----------|
| index.html | 1.2 KB | dist/index.html |
| main.js | 245 KB | dist/assets/main-abc123.js |
| vendor.js | 512 KB | dist/assets/vendor-def456.js |
| styles.css | 48 KB | dist/assets/styles-ghi789.css |
| images/* | 1.8 MB | dist/assets/images/ |

**Total Bundle Size:** 2.6 MB

### Build Output

```
vite v5.0.0 building for production...
✓ 247 modules transformed.
✓ built in 24.32s

dist/index.html                    1.23 kB │ gzip:  0.67 kB
dist/assets/main-abc123.js       245.12 kB │ gzip: 78.45 kB
dist/assets/vendor-def456.js     512.34 kB │ gzip: 156.78 kB
dist/assets/styles-ghi789.css     48.56 kB │ gzip: 12.34 kB

✓ Build completed successfully!
```

### Environment

**Build Tool:** Vite
**Build Tool Version:** 5.0.0
**Node Version:** 20.5.0
**OS:** macOS 14.0

### Build Configuration

**Mode:** production
**Optimizations:** minification, tree-shaking, code splitting
**Source Maps:** no (production build)

### Performance Metrics

**Build Time Breakdown:**
- Compilation: 8.5s
- Bundling: 12.2s
- Optimization: 2.8s
- Output: 0.8s

### Issues Found

**Errors:** None

**Warnings:**
```
Warning: 2 unused CSS classes detected in styles.css
- .unused-button-variant (line 145)
- .legacy-modal-style (line 289)
```

**Note:** These warnings are safe to ignore - legacy classes kept for backward compatibility.

### Evidence File

**Location:** `.claude/quality-gates/evidence/build-2025-11-02-162015.log`

### Conclusion

✅ Build succeeded. Production bundle created with total size 2.6 MB (acceptable for e-commerce site). All optimizations applied. Ready for deployment.

---

## Example: Failed Build

### Basic Information

**Task/Feature:** Backend API server compilation
**Agent:** Backend System Architect
**Timestamp:** 2025-11-02 17:45:22

### Build Command

```bash
cargo build --release
```

### Build Results

**Exit Code:** 101 ❌

**Duration:** 15.2 seconds (terminated early)

**Errors:** 3
**Warnings:** 0

### Artifacts Created

None - build failed before artifact generation

### Build Output

```
   Compiling api-server v0.1.0 (/workspace/api-server)
error[E0308]: mismatched types
  --> src/handlers/user.rs:42:5
   |
42 |     user_id
   |     ^^^^^^^ expected `Result<UserId, Error>`, found `UserId`
   |
   = note: expected enum `Result<UserId, Error>`
              found struct `UserId`

error[E0425]: cannot find function `validate_email` in this scope
  --> src/handlers/user.rs:67:13
   |
67 |         if !validate_email(&email) {
   |             ^^^^^^^^^^^^^^ not found in this scope

error[E0308]: mismatched types
  --> src/handlers/auth.rs:89:12
   |
89 |     return token;
   |            ^^^^^ expected `Result<String, AuthError>`, found `String`

error: could not compile `api-server` due to 3 previous errors
```

### Environment

**Build Tool:** Cargo
**Build Tool Version:** 1.75.0
**Rust Version:** 1.75.0
**OS:** macOS 14.0

### Build Configuration

**Mode:** release
**Optimizations:** enabled (release mode)

### Issues Found

**Errors:**

1. **Type mismatch in user.rs:42**
   - Expected: `Result<UserId, Error>`
   - Found: `UserId`
   - Fix: Wrap return value in `Ok(user_id)`

2. **Undefined function in user.rs:67**
   - Function `validate_email` not found
   - Fix: Import from `utils::validation` module

3. **Type mismatch in auth.rs:89**
   - Expected: `Result<String, AuthError>`
   - Found: `String`
   - Fix: Wrap return value in `Ok(token)`

### Evidence File

**Location:** `.claude/quality-gates/evidence/build-2025-11-02-174522.log`

### Conclusion

❌ Build failed with 3 compilation errors. All errors are type mismatches and missing imports. Fixing:
1. Adding Ok() wrappers for Result returns
2. Importing validate_email function
3. Re-running build after fixes

Task NOT complete. Fixing compilation errors now.

---

## Quick Fill Template

Use this for quick evidence capture:

```
## Build Evidence

**Task:** [description]
**Command:** `[command]`
**Exit Code:** [0/non-zero] [✅/❌]
**Duration:** [X]s
**Errors:** [X]
**Warnings:** [X]
**Artifacts:** [list main files and sizes]
**Timestamp:** [YYYY-MM-DD HH:MM:SS]

**Status:** [Build succeeded ✅ / Build failed ❌]
```

---

## Build Optimization Checklist

After successful build, verify optimizations:

- [ ] **Minification** - JavaScript/CSS minified
- [ ] **Tree-shaking** - Unused code removed
- [ ] **Code splitting** - Vendor/app bundles separated
- [ ] **Asset optimization** - Images compressed
- [ ] **Bundle size** - Within acceptable limits
- [ ] **Source maps** - Generated for debugging (dev) or excluded (prod)
- [ ] **Cache busting** - Filenames include hashes
