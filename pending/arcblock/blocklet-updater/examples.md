# Blocklet Updater Examples

## Example 1: Project with Build Script

```
User: "Bump and bundle this blocklet"

Steps:
1. Run: blocklet version patch → success (1.0.0 → 1.0.1)
2. Check package.json → build script exists
3. Install dependencies: pnpm install → success
4. Build project: pnpm run build → success
5. Locate output: dist/index.html found
6. Check blocklet.yml main field → "dist" matches output directory
7. Verify: blocklet meta → success
8. Bundle: blocklet bundle --create-release → success
```

## Example 2: Static Project (No Build)

```
User: "Update this blocklet version and bundle"

Steps:
1. Run: blocklet version patch → success (2.1.3 → 2.1.4)
2. Check package.json → no build script or no package.json
3. Skip dependency install and build
4. Locate output: ./index.html found in root
5. Check blocklet.yml main field → "./" matches root
6. Verify: blocklet meta → success
7. Bundle: blocklet bundle --create-release → success
```

## Example 3: Misaligned Main Field

```
User: "Bump and release this blocklet"

Steps:
1. Run: blocklet version patch → success (1.2.0 → 1.2.1)
2. Check package.json → build script exists
3. Install dependencies: pnpm install → success
4. Build project: pnpm run build → success
5. Locate output: build/index.html found
6. Check blocklet.yml main field → "dist" does NOT match
7. Update blocklet.yml main field: "dist" → "build"
8. Inform user: "Updated main field in blocklet.yml from 'dist' to 'build'"
9. Verify: blocklet meta → success
10. Bundle: blocklet bundle --create-release → success
```

## Example 4: Build Failure

```
User: "Bump version and bundle"

Steps:
1. Run: blocklet version patch → success (0.5.0 → 0.5.1)
2. Check package.json → build script exists
3. Install dependencies: pnpm install → success
4. Build project: pnpm run build → FAILED
   Error: Module not found: Can't resolve './components/Missing'
5. EXIT immediately - do not proceed with bundle

Output: "Build failed. Please fix the error:
- Module not found: Can't resolve './components/Missing'
Try running: pnpm run build"
```

## Example 5: Not a Blocklet Project

```
User: "Bump and bundle this"

Steps:
1. Check for blocklet.yml → NOT FOUND
2. EXIT immediately

Output: "No blocklet.yml found. This is not a blocklet project.
Run blocklet-converter first to convert this project to a blocklet."
```
