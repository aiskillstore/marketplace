# Blocklet Converter Examples

## Example 1: Vite React Project

```
User: "Convert this to a blocklet using DID z8ia9xB7CjK5mNpQ2RsTuVw3Xy4Za"

Steps:
1. Extract DID from parameters → z8ia9xB7CjK5mNpQ2RsTuVw3Xy4Za
2. Validate DID format → valid
3. Verify web application exists → package.json with react, vite found
4. Analyze package.json → Vite project, build script exists
5. Install dependencies: pnpm install → success
6. Build project: pnpm run build → success
7. Locate output directory: dist/ verified with index.html
8. Extract: name="My App", description="React app"
9. README.md exists → skip creation
10. Copy default logo → logo.png
11. Create blocklet.yml with DID and main: dist
12. Verify: blocklet meta → success
13. Bundle: blocklet bundle --create-release → success
```

## Example 2: Plain HTML Project

```
User: "Make this a blocklet with DID z8ia7yC8DkL6nOpR3StUvXy5Zb"

Steps:
1. Extract DID from parameters → z8ia7yC8DkL6nOpR3StUvXy5Zb
2. Validate DID format → valid
3. Verify web application exists → index.html found in root
4. No package.json or minimal one (no build script)
5. Generate: name="Web Project", description="Static website"
6. Skip dependencies & build (no build script detected)
7. Create README.md (missing)
8. Copy default logo
9. Create blocklet.yml with DID and main: ./
10. Verify: blocklet meta → success
11. Bundle: blocklet bundle --create-release → success
```

## Example 3: Build Failure Handling

```
User: "Convert this to a blocklet using DID z8ia3xD9EkM7oNqS4TuWyZ6Ac"

Steps:
1. Extract DID from parameters → z8ia3xD9EkM7oNqS4TuWyZ6Ac
2. Validate DID format → valid
3. Verify web application exists → package.json with typescript, react found
4. Analyze package.json → TypeScript React project, build script exists
5. Install dependencies: pnpm install → success
6. Build project: pnpm run build → FAILED
   Error: TypeScript compilation errors in src/components/Header.tsx
7. Report error to user with full output
8. EXIT immediately - do not create blocklet.yml

Output: "Build failed. Please fix type errors in:
- src/components/Header.tsx:15 - Type 'string' is not assignable to type 'number'
Try running: pnpm run build"
```

## Example 4: No Web Application Detected

```
User: "Convert this to a blocklet using DID z8ia5xF2GhN8pQrT6UvXyW7Bd"

Steps:
1. Extract DID from parameters → z8ia5xF2GhN8pQrT6UvXyW7Bd
2. Validate DID format → valid
3. Check for web application indicators:
   - package.json → NOT FOUND or no web dependencies
   - index.html → NOT FOUND in root, public/, or src/
   - Web framework configs → NOT FOUND
4. EXIT immediately - no web application detected

Output: "No web application detected. This skill only converts web projects.
Expected to find package.json with web dependencies, index.html, or web framework
configuration files."
```
