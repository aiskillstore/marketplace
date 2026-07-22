# README Generator Templates

Use these templates as starting points. Keep only sections supported by project evidence and replace placeholders with facts from the repository.

## Shared README Structure

```markdown
# <Project Title>

![License](https://img.shields.io/badge/license-<LICENSE>-blue)
![Language](https://img.shields.io/badge/language-<LANGUAGE>-informational)
![Version](https://img.shields.io/badge/version-<VERSION>-brightgreen)
![Build](https://img.shields.io/badge/build-passing-brightgreen)

<Description from manifest, comments, or TODO if unknown.>

## Installation

<Language-specific installation commands.>

## Usage

<Commands or examples from scripts, entry points, or safe --help output.>

## API

<Only include when JSDoc, docstrings, Go comments, Rust doc comments, or JavaDoc exist.>

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes before submitting a pull request.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run the test suite.
5. Open a pull request.

## License

<Detected license or TODO: Add license.>
```

## Badge Placeholders

- License: `![License](https://img.shields.io/badge/license-<LICENSE>-blue)`
- Language: `![Language](https://img.shields.io/badge/language-<LANGUAGE>-informational)`
- Version: `![Version](https://img.shields.io/badge/version-<VERSION>-brightgreen)`
- Build: `![Build](https://img.shields.io/badge/build-passing-brightgreen)`

Use the real license, language, and version when detected. Keep the build badge as a placeholder unless an actual CI config exists.

## Node Template

Detection:

- Manifest: `package.json`
- Main entry points: `package.json` `main`, `bin`, `exports`, `src/index.ts`, `src/index.js`, `index.js`, `server.js`
- Dependencies: `dependencies`, `devDependencies`, `peerDependencies`, `optionalDependencies`
- Scripts: `package.json` `scripts`

Installation:

````markdown
## Installation

```bash
npm install
```
````

Usage:

````markdown
## Usage

```bash
npm run <script>
```
````

If `package.json` contains `bin`, include CLI usage from the bin name. If a safe `--help` command succeeds, prefer its examples.

## Python Template

Detection:

- Manifest: `requirements.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`
- Main entry points: `main.py`, `app.py`, `__main__.py`, package console scripts
- Dependencies: requirements and package metadata

Installation:

````markdown
## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
````

Use this Windows activation note when helpful:

```powershell
.\.venv\Scripts\Activate.ps1
```

Usage:

````markdown
## Usage

```bash
python main.py
```
````

Adjust the command to the detected entry point.

## Go Template

Detection:

- Manifest: `go.mod`
- Main entry points: `main.go`, `cmd/*/main.go`
- Dependencies: `require` blocks in `go.mod`

Installation:

````markdown
## Installation

```bash
go mod download
```
````

Usage:

````markdown
## Usage

```bash
go run .
```
````

If the project uses `cmd/<name>/main.go`, use `go run ./cmd/<name>`.

## Rust Template

Detection:

- Manifest: `Cargo.toml`
- Main entry points: `src/main.rs`, `src/lib.rs`, `[[bin]]`
- Dependencies: `[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`

Installation:

````markdown
## Installation

```bash
cargo build
```
````

Usage:

````markdown
## Usage

```bash
cargo run
```
````

If the project is a library, show a short import/use example only when public API documentation exists.

## Java Template

Detection:

- Manifest: `pom.xml`, `build.gradle`, `build.gradle.kts`
- Main entry points: Maven/Gradle application config or `src/main/java/**/Main.java`
- Dependencies: Maven or Gradle dependency declarations

Maven installation:

````markdown
## Installation

```bash
mvn install
```
````

Maven usage:

````markdown
## Usage

```bash
mvn exec:java
```
````

Gradle installation:

````markdown
## Installation

```bash
./gradlew build
```
````

Gradle usage:

````markdown
## Usage

```bash
./gradlew run
```
````

On Windows, include `gradlew.bat build` or `gradlew.bat run` when the wrapper exists.

## API Documentation Rules

- JSDoc: summarize exported functions/classes with parameter and return details present in comments.
- Python docstrings: summarize modules, classes, and public functions with documented arguments.
- Go comments: document exported identifiers only when comments exist.
- Rust doc comments: summarize public modules, structs, enums, traits, and functions with `///` or `//!`.
- JavaDoc: summarize public classes and methods with documented parameters or returns.

Do not invent APIs from filenames alone. If comments are absent, include a short note such as `API documentation is not available yet because public interfaces are not documented in source comments.`
