# Entry Point Discovery

Find the main entry points of a codebase to begin systematic analysis.

## Why Entry Points First?

- Establishes the correct starting point for tracing
- Identifies the framework and architecture style
- Prevents analyzing dead or unused code

## Discovery by Language

### Node.js / TypeScript

```bash
# Check package.json for entry points
cat package.json | grep -E '"main"|"bin"|"module"|"exports"'

# Common entry files
ls -la index.{js,ts} main.{js,ts} server.{js,ts} app.{js,ts} 2>/dev/null

# Find files with server setup
grep -rl "createServer\|listen(" --include="*.ts" --include="*.js" | head -5
```

**Typical Entry Points:**
- `src/index.ts` - Library entry
- `src/server.ts` - Server entry
- `src/main.ts` - Application entry
- `bin/*` - CLI tools

### Python

```bash
# Check for entry points
cat pyproject.toml | grep -A5 "\[project.scripts\]"
cat setup.py | grep "entry_points"

# Common entry files
ls -la main.py app.py wsgi.py asgi.py __main__.py 2>/dev/null

# Find main functions
grep -rl "if __name__.*__main__" --include="*.py" | head -5
```

**Typical Entry Points:**
- `app/main.py` - FastAPI/Flask
- `manage.py` - Django
- `wsgi.py` / `asgi.py` - WSGI/ASGI servers
- `__main__.py` - Package execution

### Go

```bash
# Find main packages
find . -name "main.go" | grep -v vendor

# Check for cmd pattern
ls -la cmd/*/main.go 2>/dev/null
```

**Typical Entry Points:**
- `main.go` - Single binary
- `cmd/app/main.go` - Multiple binaries
- `internal/` - Internal packages

### React / Next.js

```bash
# React (CRA)
ls -la src/index.{tsx,jsx} 2>/dev/null

# Next.js
ls -la pages/_app.{tsx,jsx} app/layout.{tsx,jsx} 2>/dev/null
ls -la next.config.{js,mjs,ts} 2>/dev/null
```

**Typical Entry Points:**
- `src/index.tsx` - CRA root
- `pages/_app.tsx` - Next.js pages router
- `app/layout.tsx` - Next.js app router
- `src/App.tsx` - Main component

### Java / Spring

```bash
# Find Spring Boot application
grep -rl "@SpringBootApplication" --include="*.java"

# Find main methods
grep -rl "public static void main" --include="*.java" | head -5
```

**Typical Entry Points:**
- `*Application.java` - Spring Boot entry
- `src/main/java/` - Source root

### Rust

```bash
# Binary entry
ls -la src/main.rs 2>/dev/null

# Library entry
ls -la src/lib.rs 2>/dev/null

# Check Cargo.toml
cat Cargo.toml | grep -A5 "\[\[bin\]\]"
```

### Dart / Flutter

```bash
# Flutter/Dart entry
ls -la lib/main.dart 2>/dev/null

# Flutter project markers
ls -la pubspec.yaml 2>/dev/null
```

**Typical Entry Points:**
- `lib/main.dart` - Flutter app entry
- `bin/*.dart` - Dart CLI tools

### C / C++

```bash
# Common entry files
ls -la main.{c,cc,cpp,cxx} src/main.{c,cc,cpp,cxx} 2>/dev/null

# CMake targets
grep -rl "add_executable" --include="CMakeLists.txt" | head -5
```

**Typical Entry Points:**
- `main.c` / `main.cpp` - Application entry
- `src/main.cpp` - Project entry
- `CMakeLists.txt` - Build targets and executables

## Discovery by Framework

### Express.js

```bash
grep -rl "express()" --include="*.ts" --include="*.js" | head -3
grep -rl "app.listen" --include="*.ts" --include="*.js" | head -3
```

### FastAPI

```bash
grep -rl "FastAPI()" --include="*.py" | head -3
grep -rl "@app.get\|@app.post" --include="*.py" | head -3
```

### Django

```bash
ls -la manage.py
ls -la */settings.py */urls.py
```

### NestJS

```bash
grep -rl "@Module" --include="*.ts" | head -3
ls -la src/main.ts src/app.module.ts 2>/dev/null
```

## Output Format

Document entry points as:

```markdown
## Entry Points

| File | Type | Purpose |
|------|------|---------|
| `src/index.ts` | Main | Application bootstrap |
| `src/server.ts` | Server | HTTP server setup |
| `src/cli.ts` | CLI | Command line interface |
```
