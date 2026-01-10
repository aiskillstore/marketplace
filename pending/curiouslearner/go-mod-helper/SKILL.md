---
name: go-mod-helper
description: Go module system, dependency management, and project configuration assistance.
---

# Go Module Management Skill

Go module system, dependency management, and project configuration assistance.

## Instructions

You are a Go module and dependency expert. When invoked:

1. **Module Management**:
   - Initialize and configure Go modules
   - Manage go.mod and go.sum files
   - Handle module versioning and dependencies
   - Work with module replacements and exclusions
   - Configure module proxies and checksums

2. **Dependency Management**:
   - Add, update, and remove dependencies
   - Handle indirect dependencies
   - Resolve version conflicts
   - Use semantic import versioning
   - Manage private modules

3. **Project Setup**:
   - Initialize new Go projects
   - Configure project structure
   - Set up multi-module repositories
   - Configure build tags and constraints
   - Manage workspace mode

4. **Troubleshooting**:
   - Fix module resolution errors
   - Debug checksum mismatches
   - Resolve import path issues
   - Handle proxy and authentication problems
   - Clean corrupted module cache

5. **Best Practices**: Provide guidance on Go module patterns, versioning, and dependency management

## Go Module Basics

### Module Initialization
```bash
# Initialize new module
go mod init github.com/username/project

# Initialize with custom path
go mod init example.com/myproject

# Create project structure
mkdir -p cmd/server internal/api pkg/utils
touch cmd/server/main.go

# Sample main.go
cat > cmd/server/main.go << 'EOF'
package main

import (
    "fmt"
    "github.com/username/project/internal/api"
)

func main() {
    fmt.Println("Hello, Go modules!")
    api.Start()
}
EOF
```

### go.mod File Structure
```go
module github.com/username/project

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/lib/pq v1.10.9
    golang.org/x/sync v0.5.0
)

require (
    // Indirect dependencies
    github.com/bytedance/sonic v1.10.2 // indirect
    github.com/chenzhuoyu/base64x v0.0.0-20230717121745-296ad89f973d // indirect
    github.com/gabriel-vasile/mimetype v1.4.3 // indirect
)

replace (
    // Replace with local version
    github.com/old/package => ../local/package

    // Replace with fork
    github.com/original/repo => github.com/fork/repo v1.2.3
)

exclude (
    // Exclude problematic versions
    github.com/bad/package v1.2.3
)

retract (
    // Retract published versions
    v1.5.0 // Contains bug
    [v1.6.0, v1.6.5] // Range of bad versions
)
```

### go.sum File
```
github.com/gin-gonic/gin v1.9.1 h1:4idEAncQnU5cB7BeOkPtxjfCSye0AAm1R0RVIqJ+Jmg=
github.com/gin-gonic/gin v1.9.1/go.mod h1:hPrL7YrpYKXt5YId3A/Tnip5kqbEAP+KLuI3SUcPTeU=
```

## Usage Examples

```
@go-mod-helper
@go-mod-helper --init-project
@go-mod-helper --update-deps
@go-mod-helper --tidy
@go-mod-helper --troubleshoot
@go-mod-helper --private-modules
```

## Common Commands

### Dependency Management
```bash
# Add dependency (automatically)
# Just import and run:
go get github.com/gin-gonic/gin

# Add specific version
go get github.com/gin-gonic/gin@v1.9.1

# Add latest version
go get github.com/gin-gonic/gin@latest

# Add specific commit
go get github.com/user/repo@commit-hash

# Add specific branch
go get github.com/user/repo@branch-name

# Update dependency
go get -u github.com/gin-gonic/gin

# Update all dependencies
go get -u ./...

# Update to patch version only
go get -u=patch github.com/gin-gonic/gin

# Remove unused dependencies
go mod tidy

# Download dependencies
go mod download

# Verify dependencies
go mod verify

# View dependency graph
go mod graph

# Explain why dependency is needed
go mod why github.com/lib/pq

# List all modules
go list -m all

# List available versions
go list -m -versions github.com/gin-gonic/gin
```

### Module Cache
```bash
# View cache location
go env GOMODCACHE

# Clean module cache
go clean -modcache

# Download all dependencies to cache
go mod download

# Download specific module
go mod download github.com/gin-gonic/gin@v1.9.1
```

## Project Setup Patterns

### Standard Project Layout
```
myproject/
├── go.mod
├── go.sum
├── README.md
├── Makefile
├── .gitignore
├── cmd/
│   ├── server/
│   │   └── main.go
│   └── cli/
│       └── main.go
├── internal/
│   ├── api/
│   │   ├── handler.go
│   │   └── routes.go
│   ├── database/
│   │   └── db.go
│   └── config/
│       └── config.go
├── pkg/
│   ├── utils/
│   │   └── helper.go
│   └── models/
│       └── user.go
├── api/
│   └── openapi.yaml
├── docs/
│   └── design.md
├── scripts/
│   └── setup.sh
└── tests/
    ├── integration/
    └── e2e/
```

### Multiple Binaries
```go
// go.mod
module github.com/username/project

go 1.21

// cmd/server/main.go
package main

func main() {
    // Server implementation
}

// cmd/cli/main.go
package main

func main() {
    // CLI implementation
}
```

```bash
# Build specific binary
go build -o bin/server ./cmd/server
go build -o bin/cli ./cmd/cli

# Build all
go build ./cmd/...

# Install to GOPATH/bin
go install ./cmd/server
go install ./cmd/cli
```

### Library Project
```go
// go.mod
module github.com/username/mylib

go 1.21

// mylib.go (root package)
package mylib

// Public API

// internal/impl.go
package internal

// Private implementation
```

## Semantic Import Versioning

### Major Versions (v2+)
```go
// go.mod
module github.com/username/project/v2

go 1.21

require (
    github.com/other/lib/v3 v3.1.0
)
```

```go
// Import in code
import (
    "github.com/username/project/v2/pkg/utils"
    oldversion "github.com/username/project"  // v1
)
```

### Version Strategy
```bash
# v0.x.x - Initial development
v0.1.0  # Initial release
v0.2.0  # Add features
v0.3.0  # More changes

# v1.x.x - Stable API
v1.0.0  # First stable release
v1.1.0  # Add features (backward compatible)
v1.1.1  # Bug fixes

# v2.x.x - Breaking changes
v2.0.0  # Breaking API changes
# Must update module path to /v2

# Tagging releases
git tag v1.0.0
git push origin v1.0.0
```

## Private Modules

### Configure Private Repositories
```bash
# Set GOPRIVATE environment variable
go env -w GOPRIVATE="github.com/yourorg/*,gitlab.com/yourcompany/*"

# Or set in shell
export GOPRIVATE="github.com/yourorg/*"

# Configure Git to use SSH instead of HTTPS
git config --global url."git@github.com:".insteadOf "https://github.com/"

# Configure for specific organization
git config --global url."git@github.com:yourorg/".insteadOf "https://github.com/yourorg/"

# Disable proxy for private modules
go env -w GONOPROXY="github.com/yourorg/*"

# Disable checksum verification for private
go env -w GONOSUMDB="github.com/yourorg/*"
```

### Authentication Methods

#### GitHub Personal Access Token
```bash
# Create ~/.netrc for HTTPS auth
cat > ~/.netrc << EOF
machine github.com
login YOUR_GITHUB_USERNAME
password YOUR_GITHUB_TOKEN
EOF

chmod 600 ~/.netrc
```

#### SSH Keys
```bash
# Generate SSH key if needed
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Configure git to use SSH
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

#### GitLab CI/CD
```bash
# .gitlab-ci.yml
before_script:
  - git config --global url."https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.com/".insteadOf "https://gitlab.com/"
  - go env -w GOPRIVATE="gitlab.com/yourgroup/*"
```

## Module Replacement

### Local Development
```go
// go.mod
module github.com/myorg/project

replace github.com/myorg/library => ../library

require github.com/myorg/library v1.2.3
```

### Fork Replacement
```go
// Replace with fork
replace github.com/original/repo => github.com/yourfork/repo v1.2.3

// Replace with specific version
replace github.com/pkg/errors => github.com/pkg/errors v0.9.1
```

### Temporary Fixes
```bash
# Edit vendor copy
go mod vendor
# Edit vendor/github.com/package/file.go

# Tell Go to use vendor
go build -mod=vendor
```

## Workspace Mode (Go 1.18+)

### Multi-Module Development
```bash
# Create workspace
go work init

# Add modules to workspace
go work use ./project1
go work use ./project2
go work use ./shared-lib

# go.work file created
cat go.work
```

```go
// go.work
go 1.21

use (
    ./project1
    ./project2
    ./shared-lib
)

replace github.com/myorg/shared => ./shared-lib
```

```bash
# Work commands
go work sync     # Sync workspace modules
go work edit     # Edit go.work
go work use -r . # Add all modules recursively

# Workspace ignored by default in .gitignore
echo "go.work" >> .gitignore
```

## Vendoring

### Enable Vendoring
```bash
# Create vendor directory
go mod vendor

# Build with vendor
go build -mod=vendor

# Set vendor mode as default
go env -w GOFLAGS=-mod=vendor

# Update vendor
go mod vendor

# Verify vendor
go mod verify
```

### Vendor Configuration
```bash
# Build always uses vendor
go build -mod=vendor

# Build ignores vendor
go build -mod=mod

# Build with readonly mode (CI)
go build -mod=readonly
```

## Common Issues & Solutions

### Issue: Checksum Mismatch
```bash
# Error: verifying module: checksum mismatch

# Solution 1: Update go.sum
go clean -modcache
go mod download
go mod tidy

# Solution 2: Verify authenticity
go mod verify

# Solution 3: Force re-download
go get -u github.com/package/name
go mod tidy

# Solution 4: Check GOSUMDB
go env GOSUMDB  # Should be "sum.golang.org"
```

### Issue: Module Not Found
```bash
# Error: cannot find module providing package

# Check if module exists
go list -m github.com/package/name

# Update dependencies
go get github.com/package/name
go mod download

# Clear cache and retry
go clean -modcache
go mod download

# Check import path
go list -m -json github.com/package/name
```

### Issue: Version Conflicts
```bash
# Check dependency graph
go mod graph | grep package-name

# See why package is required
go mod why github.com/package/name

# Force specific version
go get github.com/package/name@v1.2.3

# Exclude problematic version
# Add to go.mod:
exclude github.com/bad/package v1.2.3
```

### Issue: Private Repository Access
```bash
# Configure GOPRIVATE
go env -w GOPRIVATE="github.com/yourorg/*"

# Configure git credentials
git config --global credential.helper store

# Use SSH instead of HTTPS
git config --global url."git@github.com:".insteadOf "https://github.com/"

# Verify settings
go env | grep GOPRIVATE
git config --get-regexp url
```

### Issue: Slow Downloads
```bash
# Use module proxy
go env -w GOPROXY="https://proxy.golang.org,direct"

# Use alternative proxy (China)
go env -w GOPROXY="https://goproxy.cn,direct"

# Disable proxy for specific domains
go env -w GOPRIVATE="github.com/myorg/*"

# Direct download (no proxy)
go env -w GOPROXY="direct"

# Check current settings
go env | grep PROXY
```

### Issue: Corrupted Module Cache
```bash
# Clean entire cache
go clean -modcache

# Re-download dependencies
go mod download

# Verify integrity
go mod verify

# Check cache location
go env GOMODCACHE
```

## Advanced Patterns

### Build Constraints
```go
// +build linux darwin

package utils

// Only compiled on Linux and macOS

// build tag: go1.18
// +build go1.18

// Requires Go 1.18+
```

```go
// Modern syntax (Go 1.17+)
//go:build linux && amd64

package platform

// Compiled only for Linux AMD64
```

### Conditional Dependencies
```go
// go.mod
require (
    github.com/common/lib v1.0.0
)

// For testing only
require (
    github.com/stretchr/testify v1.8.4
)
```

### Module Documentation
```go
// Package mypackage provides utilities for...
//
// Basic usage:
//
//     import "github.com/user/mypackage"
//
//     result := mypackage.DoSomething()
//
package mypackage
```

```bash
# View documentation
go doc github.com/user/mypackage
go doc github.com/user/mypackage.FunctionName

# Run doc server
godoc -http=:6060
```

## Testing and CI/CD

### Testing with Modules
```bash
# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Generate coverage profile
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Test with race detector
go test -race ./...

# Test specific package
go test github.com/user/project/pkg/utils
```

### CI/CD Configuration

#### GitHub Actions
```yaml
name: Go

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.21'
        cache: true

    - name: Download dependencies
      run: go mod download

    - name: Verify dependencies
      run: go mod verify

    - name: Run go vet
      run: go vet ./...

    - name: Run tests
      run: go test -v -race -coverprofile=coverage.out ./...

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.out

    - name: Build
      run: go build -v ./...
```

#### GitLab CI
```yaml
image: golang:1.21

stages:
  - test
  - build

before_script:
  - go mod download

test:
  stage: test
  script:
    - go mod verify
    - go vet ./...
    - go test -v -race -coverprofile=coverage.out ./...
  coverage: '/total:.*?(\d+\.\d+)%/'

build:
  stage: build
  script:
    - go build -v ./...
  artifacts:
    paths:
      - bin/
```

## Build and Release

### Build Configuration
```bash
# Basic build
go build -o bin/myapp ./cmd/myapp

# Build with version info
VERSION=$(git describe --tags --always)
BUILD_TIME=$(date -u '+%Y-%m-%d_%H:%M:%S')
go build -ldflags "-X main.Version=${VERSION} -X main.BuildTime=${BUILD_TIME}" -o bin/myapp

# Build for different platforms
GOOS=linux GOARCH=amd64 go build -o bin/myapp-linux-amd64
GOOS=darwin GOARCH=amd64 go build -o bin/myapp-darwin-amd64
GOOS=windows GOARCH=amd64 go build -o bin/myapp-windows-amd64.exe

# Build with optimizations
go build -ldflags="-s -w" -o bin/myapp  # Strip debug info

# Static binary (no CGO)
CGO_ENABLED=0 go build -o bin/myapp
```

### Makefile Example
```makefile
.PHONY: build test clean install

VERSION ?= $(shell git describe --tags --always --dirty)
BUILD_TIME ?= $(shell date -u '+%Y-%m-%d_%H:%M:%S')
LDFLAGS := -ldflags "-X main.Version=$(VERSION) -X main.BuildTime=$(BUILD_TIME)"

build:
	go build $(LDFLAGS) -o bin/myapp ./cmd/myapp

test:
	go test -v -race -coverprofile=coverage.out ./...

coverage:
	go tool cover -html=coverage.out

lint:
	golangci-lint run

tidy:
	go mod tidy
	go mod verify

clean:
	rm -rf bin/
	go clean -cache -modcache

install: build
	cp bin/myapp $(GOPATH)/bin/

release:
	GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o bin/myapp-linux-amd64
	GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o bin/myapp-darwin-amd64
	GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o bin/myapp-windows-amd64.exe
```

## Module Publishing

### Prepare for Release
```bash
# Ensure tests pass
go test ./...

# Tidy dependencies
go mod tidy

# Verify module
go mod verify

# Run linter
golangci-lint run

# Update version in documentation
# Update CHANGELOG.md
```

### Semantic Versioning
```bash
# Tag release
git tag v1.0.0
git push origin v1.0.0

# For v2+ major versions
# Update go.mod module path
module github.com/user/project/v2

# Tag with /v2
git tag v2.0.0
git push origin v2.0.0

# Pre-release versions
git tag v1.0.0-beta.1
git tag v1.0.0-rc.1
```

### Publishing Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] go.mod and go.sum committed
- [ ] Version tagged
- [ ] LICENSE file present
- [ ] README.md with usage examples
- [ ] CI/CD pipeline green
- [ ] Breaking changes documented

## Best Practices Summary

### Module Management
- Use semantic versioning (v1.2.3)
- Tag releases properly
- Keep go.mod and go.sum in version control
- Run `go mod tidy` regularly
- Use `go mod verify` before releases
- Document breaking changes

### Dependency Management
- Minimize dependencies
- Use `require` for direct dependencies
- Let Go manage indirect dependencies
- Update dependencies regularly
- Test after updates
- Use `go.sum` for verification

### Project Structure
- Follow standard project layout
- Use internal/ for private packages
- Use pkg/ for public libraries
- Keep cmd/ for binaries
- Organize by feature, not by type

### Versioning
- Start with v0.x.x for development
- Use v1.0.0 for first stable release
- v2+ requires /v2 in module path
- Use pre-release tags (beta, rc)
- Never delete published versions

### Security
- Run `go mod verify` regularly
- Use checksums (go.sum)
- Audit dependencies
- Keep dependencies updated
- Use GOSUMDB for verification

### Performance
- Use module cache
- Enable module proxy
- Vendor for Docker builds
- Use `go mod download` in CI

## Quick Reference Commands

```bash
# Module initialization
go mod init <module-path>

# Dependency management
go get <package>              # Add/update dependency
go get -u <package>           # Update to latest
go mod tidy                   # Remove unused dependencies
go mod download               # Download dependencies
go mod verify                 # Verify dependencies

# Information
go list -m all                # List all modules
go mod graph                  # Dependency graph
go mod why <package>          # Why is package needed
go list -m -versions <package> # List available versions

# Maintenance
go clean -modcache            # Clean module cache
go mod vendor                 # Create vendor directory
go get -u ./...               # Update all dependencies

# Building
go build ./...                # Build all packages
go test ./...                 # Test all packages
go install ./...              # Install all binaries
```

## Notes

- Always commit go.mod and go.sum files
- Use semantic versioning for releases
- Tag releases with git tags
- Use module proxy for faster downloads
- Configure GOPRIVATE for private modules
- Use workspaces for multi-module development
- Vendor dependencies for Docker builds
- Keep module path stable (avoid renames)
- Document breaking changes clearly
- Use `go mod tidy` before committing
