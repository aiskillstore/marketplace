---
name: pixi-package-manager
description: Fast, reproducible scientific Python environments with pixi - conda and PyPI unified
---

# Pixi Package Manager for Scientific Python

Master **pixi**, the modern package manager that unifies conda and PyPI ecosystems for fast, reproducible scientific Python development. Learn how to manage complex scientific dependencies, create isolated environments, and build reproducible workflows using `pyproject.toml` integration.

**Official Documentation**: https://pixi.sh
**GitHub**: https://github.com/prefix-dev/pixi

## Quick Reference Card

### Setup
```bash
# Installation must be performed separately
# On the server, load via lmod if not already in path
module load Dev/pixi

# Initialize new project with pyproject.toml
pixi init --format pyproject

# Initialize existing Python project
pixi init --format pyproject --import-environment
```

### Essential Commands
```bash
# Add dependencies
pixi add numpy scipy pandas              # conda packages
pixi add --pypi pytest-cov               # PyPI-only packages
pixi add --feature dev pytest ruff       # dev environment

# Install all dependencies
pixi install

# Run commands in environment
pixi run python script.py
pixi run pytest

# Shell with environment activated
pixi shell

# Add tasks
pixi task add test "pytest tests/"
pixi task add docs "sphinx-build docs/ docs/_build"

# Run tasks
pixi run test
pixi run docs

# Update dependencies
pixi update numpy                         # update specific
pixi update                              # update all

# List packages
pixi list
pixi tree numpy                          # show dependency tree
```

### Quick Decision Tree: Pixi vs UV vs Both

```
Need compiled scientific libraries (NumPy, SciPy, GDAL)?
├─ YES → Use pixi (conda-forge has pre-built binaries)
└─ NO → Consider uv for pure Python projects

Need multi-language support (Python + R, Julia, C++)?
├─ YES → Use pixi (supports conda ecosystem)
└─ NO → uv sufficient for Python-only

Need multiple environments (dev, test, prod, GPU, CPU)?
├─ YES → Use pixi features for environment management
└─ NO → Single environment projects work with either

Need reproducible environments across platforms?
├─ CRITICAL → Use pixi (lockfiles include all platforms)
└─ LESS CRITICAL → uv also provides lockfiles

Want to use both conda-forge AND PyPI packages?
├─ YES → Use pixi (seamless integration)
└─ ONLY PYPI → uv is simpler and faster

Legacy conda environment files (environment.yml)?
├─ YES → pixi can import and modernize
└─ NO → Start fresh with pixi or uv
```

## When to Use This Skill

- **Setting up scientific Python projects** with complex compiled dependencies (NumPy, SciPy, Pandas, scikit-learn, GDAL, netCDF4)
- **Building reproducible research environments** that work identically across different machines and platforms
- **Managing multi-language projects** that combine Python with R, Julia, C++, or Fortran
- **Creating multiple environment configurations** for different hardware (GPU/CPU), testing scenarios, or deployment targets
- **Replacing conda/mamba workflows** with faster, more reliable dependency resolution
- **Developing packages that depend on both conda-forge and PyPI** packages
- **Migrating from environment.yml or requirements.txt** to modern, reproducible workflows
- **Running automated scientific workflows** with task runners and CI/CD integration
- **Working with geospatial, climate, or astronomy packages** that require complex C/Fortran dependencies

## Core Concepts

### 1. Unified Package Management (conda + PyPI)

Pixi resolves dependencies from **both conda-forge and PyPI** in a single unified graph, ensuring compatibility:

```toml
[project]
name = "my-science-project"
dependencies = [
    "numpy>=1.24",      # from conda-forge (optimized builds)
    "pandas>=2.0",      # from conda-forge
]

[tool.pixi.pypi-dependencies]
my-custom-pkg = ">=1.0"        # PyPI-only package
```

**Why this matters for scientific Python:**
- Get optimized NumPy/SciPy builds from conda-forge (MKL, OpenBLAS)
- Use PyPI packages not available in conda
- Single lockfile ensures all dependencies are compatible

### 2. Multi-Platform Lockfiles

Pixi generates `pixi.lock` with dependency specifications for **all platforms** (Linux, macOS, Windows, different architectures):

```toml
# pixi.lock includes:
# - linux-64
# - osx-64, osx-arm64
# - win-64
```

**Benefits:**
- Commit lockfile to git → everyone gets identical environments
- Works on collaborator's different OS without changes
- CI/CD uses exact same versions as local development

### 3. Feature-Based Environments

Create multiple environments using **features** without duplicating dependencies:

```toml
[tool.pixi.feature.test.dependencies]
pytest = ">=7.0"
pytest-cov = ">=4.0"

[tool.pixi.feature.gpu.dependencies]
pytorch-cuda = "11.8.*"

[tool.pixi.environments]
test = ["test"]
gpu = ["gpu"]
gpu-test = ["gpu", "test"]  # combines features
```

### 4. Task Automation

Define reusable commands as tasks:

```toml
[tool.pixi.tasks]
test = "pytest tests/ -v"
format = "ruff format src/ tests/"
lint = "ruff check src/ tests/"
docs = "sphinx-build docs/ docs/_build"
analyse = { cmd = "python scripts/analyze.py", depends-on = ["test"] }
```

### 5. Fast Dependency Resolution

Pixi uses **rattler** (Rust-based conda resolver) for 10-100x faster resolution than conda:

- Parallel package downloads
- Efficient caching
- Smart dependency solver

### 6. pyproject.toml Integration

Pixi reads standard Python project metadata from `pyproject.toml`, enabling:
- Single source of truth for project configuration
- Compatibility with pip, uv, and other tools
- Standard Python packaging workflows

## Quick Start

### Minimal Example: Data Analysis Project

```bash
# Create new project
mkdir climate-analysis && cd climate-analysis
pixi init --format pyproject

# Add scientific stack
pixi add python=3.11 numpy pandas matplotlib xarray

# Add development tools
pixi add --feature dev pytest ipython ruff

# Create analysis script
cat > analyze.py << 'EOF'
import pandas as pd
import matplotlib.pyplot as plt

# Your analysis code
data = pd.read_csv("data.csv")
data.plot()
plt.savefig("output.png")
EOF

# Run in pixi environment
pixi run python analyze.py

# Or activate shell
pixi shell
python analyze.py
```

### Example: Machine Learning Project with GPU Support

```bash
# Initialize project
pixi init ml-project --format pyproject
cd ml-project

# Add base dependencies
pixi add python=3.11 numpy pandas scikit-learn matplotlib jupyter

# Add CPU PyTorch
pixi add --platform linux-64 --platform osx-arm64 pytorch torchvision cpuonly -c pytorch

# Create GPU feature
pixi add --feature gpu pytorch-cuda=11.8 -c pytorch -c nvidia

# Add development tools
pixi add --feature dev pytest black mypy

# Configure environments in pyproject.toml
cat >> pyproject.toml << 'EOF'

[tool.pixi.environments]
default = { solve-group = "default" }
gpu = { features = ["gpu"], solve-group = "default" }
dev = { features = ["dev"], solve-group = "default" }
EOF

# Install and run
pixi install
pixi run python train.py          # uses default (CPU)
pixi run --environment gpu python train.py  # uses GPU
```

## Patterns

### Pattern 1: Converting Existing Projects to Pixi

**Scenario**: You have an existing project with `requirements.txt` or `environment.yml`

**Solution**:

```bash
# From requirements.txt
cd existing-project
pixi init --format pyproject

# Import from requirements.txt
while IFS= read -r package; do
    # Skip comments and empty lines
    [[ "$package" =~ ^#.*$ ]] || [[ -z "$package" ]] && continue

    # Try conda first, fallback to PyPI
    pixi add "$package" 2>/dev/null || pixi add --pypi "$package"
done < requirements.txt

# From environment.yml
pixi init --format pyproject --import-environment environment.yml

# Verify installation
pixi install
pixi run python -c "import numpy, pandas, scipy; print('Success!')"
```

**Best Practice**: Review generated `pyproject.toml` and organize dependencies:
- Core runtime dependencies → `[project.dependencies]`
- PyPI-only packages → `[tool.pixi.pypi-dependencies]`
- Development tools → `[tool.pixi.feature.dev.dependencies]`

### Pattern 2: Multi-Environment Scientific Workflow

**Scenario**: Different environments for development, testing, production, and GPU computing

**Implementation**:

```toml
[project]
name = "research-pipeline"
version = "0.1.0"
dependencies = [
    "python>=3.11",
    "numpy>=1.24",
    "pandas>=2.0",
    "xarray>=2023.1",
]

# Development tools
[tool.pixi.feature.dev.dependencies]
ipython = ">=8.0"
jupyter = ">=1.0"
ruff = ">=0.1"

[tool.pixi.feature.dev.pypi-dependencies]
jupyterlab-vim = ">=0.16"

# Testing tools
[tool.pixi.feature.test.dependencies]
pytest = ">=7.4"
pytest-cov = ">=4.1"
pytest-xdist = ">=3.3"
hypothesis = ">=6.82"

# GPU dependencies
[tool.pixi.feature.gpu.dependencies]
pytorch-cuda = "11.8.*"
cudatoolkit = "11.8.*"

[tool.pixi.feature.gpu.pypi-dependencies]
nvidia-ml-py = ">=12.0"

# Production optimizations
[tool.pixi.feature.prod.dependencies]
python = "3.11.*"  # pin exact version

# Define environments combining features
[tool.pixi.environments]
default = { solve-group = "default" }
dev = { features = ["dev"], solve-group = "default" }
test = { features = ["test"], solve-group = "default" }
gpu = { features = ["gpu"], solve-group = "gpu" }
gpu-dev = { features = ["gpu", "dev"], solve-group = "gpu" }
prod = { features = ["prod"], solve-group = "prod" }

# Tasks for each environment
[tool.pixi.tasks]
dev-notebook = { cmd = "jupyter lab", env = { JUPYTER_CONFIG_DIR = ".jupyter" } }
test = "pytest tests/ -v --cov=src"
test-parallel = "pytest tests/ -n auto"
train-cpu = "python train.py --device cpu"
train-gpu = "python train.py --device cuda"
benchmark = "python benchmark.py"
```

**Usage**:

```bash
# Development
pixi run --environment dev dev-notebook

# Testing
pixi run --environment test test

# GPU training
pixi run --environment gpu train-gpu

# Production
pixi run --environment prod benchmark
```

### Pattern 3: Scientific Library Development

**Scenario**: Developing a scientific Python package with proper packaging, testing, and documentation

**Structure**:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mylib"
version = "0.1.0"
description = "Scientific computing library"
dependencies = [
    "numpy>=1.24",
    "scipy>=1.11",
]

[project.optional-dependencies]
viz = ["matplotlib>=3.7", "seaborn>=0.12"]

# Development dependencies
[tool.pixi.feature.dev.dependencies]
ipython = "*"
ruff = "*"
mypy = "*"

# Testing dependencies
[tool.pixi.feature.test.dependencies]
pytest = ">=7.4"
pytest-cov = ">=4.1"
pytest-benchmark = ">=4.0"
hypothesis = ">=6.82"

# Documentation dependencies
[tool.pixi.feature.docs.dependencies]
sphinx = ">=7.0"
sphinx-rtd-theme = ">=1.3"
numpydoc = ">=1.5"
sphinx-gallery = ">=0.14"

[tool.pixi.feature.docs.pypi-dependencies]
myst-parser = ">=2.0"

# Build dependencies
[tool.pixi.feature.build.dependencies]
build = "*"
twine = "*"

[tool.pixi.environments]
default = { features = [], solve-group = "default" }
dev = { features = ["dev", "test", "docs"], solve-group = "default" }
test = { features = ["test"], solve-group = "default" }
docs = { features = ["docs"], solve-group = "default" }

# Tasks for development workflow
[tool.pixi.tasks]
# Development
install-dev = "pip install -e ."
format = "ruff format src/ tests/"
lint = "ruff check src/ tests/"
typecheck = "mypy src/"

# Testing
test = "pytest tests/ -v"
test-cov = "pytest tests/ --cov=src --cov-report=html --cov-report=term"
test-fast = "pytest tests/ -x -v"
benchmark = "pytest tests/benchmarks/ --benchmark-only"

# Documentation
docs-build = "sphinx-build docs/ docs/_build/html"
docs-serve = { cmd = "python -m http.server 8000 -d docs/_build/html", depends-on = ["docs-build"] }
docs-clean = "rm -rf docs/_build docs/generated"

# Build and release
build = "python -m build"
publish-test = { cmd = "twine upload --repository testpypi dist/*", depends-on = ["build"] }
publish = { cmd = "twine upload dist/*", depends-on = ["build"] }

# Combined workflows
ci = { depends-on = ["format", "lint", "typecheck", "test-cov"] }
pre-commit = { depends-on = ["format", "lint", "test-fast"] }
```

**Workflow**:

```bash
# Initial setup
pixi install --environment dev
pixi run install-dev

# Development cycle
pixi run format        # format code
pixi run lint          # check style
pixi run typecheck     # type checking
pixi run test          # run tests

# Or run all checks
pixi run ci

# Build documentation
pixi run docs-build
pixi run docs-serve    # view at http://localhost:8000

# Release workflow
pixi run build
pixi run publish-test  # test on TestPyPI
pixi run publish       # publish to PyPI
```

### Pattern 4: Conda + PyPI Dependency Strategy

**Scenario**: Optimize dependency sources for performance and availability

**Strategy**:

```toml
[project]
dependencies = [
    # Core scientific stack: prefer conda-forge (optimized builds)
    "numpy>=1.24",           # MKL or OpenBLAS optimized
    "scipy>=1.11",           # optimized BLAS/LAPACK
    "pandas>=2.0",           # optimized pandas
    "matplotlib>=3.7",       # compiled components
    "scikit-learn>=1.3",     # optimized algorithms

    # Geospatial/climate: conda-forge essential (C/Fortran deps)
    "xarray>=2023.1",
    "netcdf4>=1.6",
    "h5py>=3.9",
    "rasterio>=1.3",         # GDAL dependency

    # Data processing: conda-forge preferred
    "dask>=2023.1",
    "numba>=0.57",           # LLVM dependency
]

[tool.pixi.pypi-dependencies]
# Pure Python packages or PyPI-only packages
my-custom-tool = ">=1.0"
experimental-lib = { git = "https://github.com/user/repo.git" }
internal-pkg = { path = "../internal-pkg", editable = true }
```

**Decision Rules**:

1. **Use conda-forge (pixi add) for**:
   - NumPy, SciPy, Pandas (optimized builds)
   - Packages with C/C++/Fortran extensions (GDAL, netCDF4, h5py)
   - Packages with complex system dependencies (Qt, OpenCV)
   - R, Julia, or other language packages

2. **Use PyPI (pixi add --pypi) for**:
   - Pure Python packages not in conda-forge
   - Bleeding-edge versions before conda-forge packaging
   - Internal/private packages
   - Editable local packages during development

### Pattern 5: Reproducible Research Environment

**Scenario**: Ensure research is reproducible across time and machines

**Implementation**:

```toml
[project]
name = "nature-paper-2024"
version = "1.0.0"
description = "Analysis for Nature Paper 2024"
requires-python = ">=3.11,<3.12"  # pin Python version range

dependencies = [
    "python=3.11.6",      # exact Python version
    "numpy=1.26.2",       # exact versions for reproducibility
    "pandas=2.1.4",
    "scipy=1.11.4",
    "matplotlib=3.8.2",
    "scikit-learn=1.3.2",
]

[tool.pixi.pypi-dependencies]
# Pin with exact hashes for ultimate reproducibility
seaborn = "==0.13.0"

# Analysis environments
[tool.pixi.feature.analysis.dependencies]
jupyter = "1.0.0"
jupyterlab = "4.0.9"

[tool.pixi.feature.analysis.pypi-dependencies]
jupyterlab-vim = "0.16.0"

# Environments
[tool.pixi.environments]
default = { solve-group = "default" }
analysis = { features = ["analysis"], solve-group = "default" }

# Reproducible tasks
[tool.pixi.tasks]
# Data processing pipeline
download-data = "python scripts/01_download.py"
preprocess = { cmd = "python scripts/02_preprocess.py", depends-on = ["download-data"] }
analyze = { cmd = "python scripts/03_analyze.py", depends-on = ["preprocess"] }
visualize = { cmd = "python scripts/04_visualize.py", depends-on = ["analyze"] }
full-pipeline = { depends-on = ["download-data", "preprocess", "analyze", "visualize"] }

# Notebook execution
run-notebooks = "jupyter nbconvert --execute --to notebook --inplace notebooks/*.ipynb"
```

**Best Practices**:

```bash
# Generate lockfile
pixi install

# Commit lockfile to repository
git add pixi.lock pyproject.toml
git commit -m "Lock environment for reproducibility"

# Anyone can recreate exact environment
git clone https://github.com/user/nature-paper-2024.git
cd nature-paper-2024
pixi install  # installs exact versions from pixi.lock

# Run complete pipeline
pixi run full-pipeline

# Archive for long-term preservation
pixi list --export environment.yml  # backup as conda format
```

### Pattern 6: Cross-Platform Development

**Scenario**: Team members on Linux, macOS (Intel/ARM), and Windows

**Configuration**:

```toml
[project]
name = "cross-platform-science"
dependencies = [
    "python>=3.11",
    "numpy>=1.24",
    "pandas>=2.0",
]

# Platform-specific dependencies
[tool.pixi.target.linux-64.dependencies]
# Linux-specific optimized builds
mkl = "*"

[tool.pixi.target.osx-arm64.dependencies]
# Apple Silicon optimizations
accelerate = "*"

[tool.pixi.target.win-64.dependencies]
# Windows-specific packages
pywin32 = "*"

# Tasks with platform-specific behavior
[tool.pixi.tasks]
test = "pytest tests/"

[tool.pixi.target.linux-64.tasks]
test-gpu = "pytest tests/ --gpu"

[tool.pixi.target.win-64.tasks]
test = "pytest tests/ --timeout=30"  # slower on Windows CI
```

**Platform Selectors**:

```toml
# Supported platforms
[tool.pixi.platforms]
linux-64 = true
linux-aarch64 = true
osx-64 = true
osx-arm64 = true
win-64 = true
```

### Pattern 7: Task Dependencies and Workflows

**Scenario**: Complex scientific workflows with data dependencies

**Implementation**:

```toml
[tool.pixi.tasks]
# Data acquisition
download-raw = "python scripts/download.py --source=api"
validate-raw = { cmd = "python scripts/validate.py data/raw/", depends-on = ["download-raw"] }

# Data processing pipeline
clean-data = { cmd = "python scripts/clean.py", depends-on = ["validate-raw"] }
transform = { cmd = "python scripts/transform.py", depends-on = ["clean-data"] }
feature-engineering = { cmd = "python scripts/features.py", depends-on = ["transform"] }

# Analysis
train-model = { cmd = "python scripts/train.py", depends-on = ["feature-engineering"] }
evaluate = { cmd = "python scripts/evaluate.py", depends-on = ["train-model"] }
visualize = { cmd = "python scripts/visualize.py", depends-on = ["evaluate"] }

# Testing at each stage
test-cleaning = "pytest tests/test_clean.py"
test-transform = "pytest tests/test_transform.py"
test-features = "pytest tests/test_features.py"
test-model = "pytest tests/test_model.py"

# Combined workflows
all-tests = { depends-on = ["test-cleaning", "test-transform", "test-features", "test-model"] }
full-pipeline = { depends-on = ["download-raw", "validate-raw", "clean-data", "transform", "feature-engineering", "train-model", "evaluate", "visualize"] }
pipeline-with-tests = { depends-on = ["all-tests", "full-pipeline"] }

# Parallel execution where possible
[tool.pixi.task.download-supplementary]
cmd = "python scripts/download_supplement.py"

[tool.pixi.task.process-all]
depends-on = ["download-raw", "download-supplementary"]  # run in parallel
```

**Running Workflows**:

```bash
# Run entire pipeline
pixi run full-pipeline

# Run with testing
pixi run pipeline-with-tests

# Check what will run
pixi task list --summary

# Visualize task dependencies
pixi task info full-pipeline
```

### Pattern 8: Integration with UV for Pure Python Development

**Scenario**: Use pixi for complex dependencies, uv for fast pure Python workflows

**Hybrid Approach**:

```toml
[project]
name = "hybrid-project"
dependencies = [
    # Heavy scientific deps via pixi/conda
    "python>=3.11",
    "numpy>=1.24",
    "scipy>=1.11",
    "gdal>=3.7",           # complex C++ dependency
    "netcdf4>=1.6",        # Fortran dependency
]

[tool.pixi.pypi-dependencies]
# Pure Python packages
requests = ">=2.31"
pydantic = ">=2.0"
typer = ">=0.9"

[tool.pixi.feature.dev.dependencies]
ruff = "*"
mypy = "*"

[tool.pixi.feature.dev.pypi-dependencies]
pytest = ">=7.4"

[tool.pixi.tasks]
# Use uv for fast pure Python operations
install-dev = "uv pip install -e ."
sync-deps = "uv pip sync requirements.txt"
add-py-dep = "uv pip install"
```

**Workflow**:

```bash
# Pixi manages environment with conda packages
pixi install

# Activate pixi environment
pixi shell

# Inside pixi shell, use uv for fast pure Python operations
uv pip install requests httpx pydantic  # fast pure Python installs
uv pip freeze > requirements-py.txt

# Or define as tasks
pixi run install-dev
```

**When to use this pattern**:
- Project needs conda for compiled deps (GDAL, netCDF, HDF5)
- But also rapid iteration on pure Python dependencies
- Want uv's speed for locking/installing pure Python packages
- Need conda's solver for complex scientific dependency graphs

### Pattern 9: CI/CD Integration

**Scenario**: Reproducible testing in GitHub Actions, GitLab CI, etc.

**GitHub Actions Example**:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Pixi
        uses: prefix-dev/setup-pixi@v0.4.1
        with:
          pixi-version: latest
          cache: true

      - name: Install dependencies
        run: pixi install --environment test

      - name: Run tests
        run: pixi run test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: prefix-dev/setup-pixi@v0.4.1
      - run: pixi run format --check
      - run: pixi run lint

  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: prefix-dev/setup-pixi@v0.4.1
      - run: pixi run --environment docs docs-build
      - uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: docs/_build/html
```

**GitLab CI Example**:

```yaml
# .gitlab-ci.yml
image: ubuntu:latest

before_script:
  - curl -fsSL https://pixi.sh/install.sh | bash
  - export PATH=$HOME/.pixi/bin:$PATH

stages:
  - test
  - build

test:
  stage: test
  script:
    - pixi run test
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .pixi/

lint:
  stage: test
  script:
    - pixi run lint
    - pixi run typecheck

docs:
  stage: build
  script:
    - pixi run --environment docs docs-build
  artifacts:
    paths:
      - docs/_build/html
```

### Pattern 10: Local Development with Remote Computing

**Scenario**: Develop locally, run heavy computation on remote GPU cluster

**Local Configuration** (`pyproject.toml`):

```toml
[project]
dependencies = [
    "numpy>=1.24",
    "pandas>=2.0",
]

[tool.pixi.feature.dev.dependencies]
jupyter = "*"
matplotlib = "*"

[tool.pixi.feature.remote.dependencies]
# Heavy GPU dependencies only for remote
pytorch-cuda = "11.8.*"
tensorboard = "*"

[tool.pixi.environments]
default = { features = ["dev"], solve-group = "default" }
remote = { features = ["remote"], solve-group = "remote" }

[tool.pixi.tasks]
notebook = "jupyter lab"
sync-remote = "rsync -av --exclude='.pixi' . user@remote:~/project/"
remote-train = { cmd = "ssh user@remote 'cd ~/project && pixi run train'", depends-on = ["sync-remote"] }
```

**Workflow**:

```bash
# Local development (no GPU deps)
pixi install
pixi run notebook

# Push to remote and train
pixi run remote-train

# Or manually
pixi run sync-remote
ssh user@remote
cd ~/project
pixi install --environment remote  # installs GPU deps on remote
pixi run --environment remote train
```

## Best Practices Checklist

### Project Setup
- [ ] Use `pixi init --format pyproject` for new projects
- [ ] Set explicit Python version constraint (`python>=3.11,<3.13`)
- [ ] Organize dependencies by source (conda vs PyPI)
- [ ] Create separate features for dev, test, docs environments
- [ ] Define useful tasks for common workflows
- [ ] Set up `.gitignore` to exclude `.pixi/` directory

### Dependency Management
- [ ] Prefer conda-forge for compiled scientific packages (NumPy, SciPy, GDAL)
- [ ] Use PyPI only for pure Python or conda-unavailable packages
- [ ] Pin exact versions for reproducible research
- [ ] Use version ranges for libraries (allow updates)
- [ ] Specify solve groups for independent environment solving
- [ ] Use `pixi update` regularly to get security patches

### Reproducibility
- [ ] Commit `pixi.lock` to version control
- [ ] Include all platforms in lockfile for cross-platform teams
- [ ] Document environment recreation steps in README
- [ ] Use exact version pins for published research
- [ ] Test environment from scratch periodically
- [ ] Archive environments for long-term preservation

### Performance
- [ ] Use pixi's parallel downloads (automatic)
- [ ] Leverage caching in CI/CD (`prefix-dev/setup-pixi` action)
- [ ] Keep environments minimal (only necessary dependencies)
- [ ] Use solve groups to isolate independent environments
- [ ] Clean old packages with `pixi clean cache`

### Development Workflow
- [ ] Define tasks for common operations (test, lint, format)
- [ ] Use task dependencies for complex workflows
- [ ] Create environment-specific tasks when needed
- [ ] Use `pixi shell` for interactive development
- [ ] Use `pixi run` for automated scripts and CI
- [ ] Test in clean environment before releasing

### Team Collaboration
- [ ] Document pixi installation in README
- [ ] Provide quick start commands for new contributors
- [ ] Use consistent naming for features and environments
- [ ] Set up pre-commit hooks with pixi tasks
- [ ] Integrate with CI/CD for automated testing
- [ ] Keep pyproject.toml clean and well-commented

### Security
- [ ] Audit dependencies regularly (`pixi list`)
- [ ] Use trusted channels (conda-forge, PyPI)
- [ ] Review `pixi.lock` changes in PRs
- [ ] Keep pixi updated to latest version
- [ ] Use virtual environments (pixi automatic)
- [ ] Scan for vulnerabilities in dependencies

## Resources

### Official Documentation
- **Pixi Website**: https://pixi.sh
- **Documentation**: https://pixi.sh/latest/
- **GitHub Repository**: https://github.com/prefix-dev/pixi
- **Configuration Reference**: https://pixi.sh/latest/reference/project_configuration/

### Community & Support
- **Discord**: https://discord.gg/kKV8ZxyzY4
- **GitHub Discussions**: https://github.com/prefix-dev/pixi/discussions
- **Issue Tracker**: https://github.com/prefix-dev/pixi/issues

### Related Technologies
- **Conda-forge**: https://conda-forge.org/
- **Rattler**: https://github.com/mamba-org/rattler (underlying solver)
- **PyPI**: https://pypi.org/
- **UV Package Manager**: https://github.com/astral-sh/uv

### Complementary Skills
- **scientific-python-packaging**: Modern Python packaging patterns
- **scientific-python-testing**: Testing strategies with pytest
- **uv-package-manager**: Fast pure-Python package management

### Learning Resources
- **Pixi Examples**: https://github.com/prefix-dev/pixi/tree/main/examples
- **Migration Guides**: https://pixi.sh/latest/switching_from/conda/
- **Best Practices**: https://pixi.sh/latest/features/

### Scientific Python Ecosystem
- **NumPy**: https://numpy.org/
- **SciPy**: https://scipy.org/
- **Pandas**: https://pandas.pydata.org/
- **Scikit-learn**: https://scikit-learn.org/
- **PyData**: https://pydata.org/

## Common Issues and Solutions

### Issue: Package Not Found in Conda-forge

**Problem**: Running `pixi add my-package` fails with "package not found"

**Solution**:
```bash
# Search conda-forge
pixi search my-package

# If not in conda-forge, use PyPI
pixi add --pypi my-package

# Check if package has different name in conda
# Example: scikit-learn (PyPI) vs sklearn (conda)
pixi add scikit-learn  # correct conda name
```

### Issue: Conflicting Dependencies

**Problem**: Dependency solver fails with "conflict" error

**Solution**:
```bash
# Check dependency tree
pixi tree numpy

# Use solve groups to isolate conflicts
[tool.pixi.environments]
env1 = { features = ["feat1"], solve-group = "group1" }
env2 = { features = ["feat2"], solve-group = "group2" }  # separate solver

# Relax version constraints
# Instead of: numpy==1.26.0
# Use: numpy>=1.24,<2.0

# Force specific channel priority
pixi add numpy -c conda-forge --force-reinstall
```

### Issue: Slow Environment Creation

**Problem**: `pixi install` takes very long

**Solution**:
```bash
# Use solve groups to avoid re-solving everything
[tool.pixi.environments]
default = { solve-group = "default" }
test = { features = ["test"], solve-group = "default" }  # reuses default solve

# Clean cache if corrupted
pixi clean cache

# Check for large dependency trees
pixi tree --depth 2

# Update pixi to latest version
pixi self-update
```

### Issue: Platform-Specific Failures

**Problem**: Works on Linux but fails on macOS/Windows

**Solution**:
```toml
# Use platform-specific dependencies
[tool.pixi.target.osx-arm64.dependencies]
# macOS ARM specific packages
tensorflow-macos = "*"

[tool.pixi.target.linux-64.dependencies]
# Linux-specific
tensorflow = "*"

# Exclude unsupported platforms
[tool.pixi.platforms]
linux-64 = true
osx-arm64 = true
# win-64 intentionally excluded if unsupported
```

### Issue: PyPI Package Installation Fails

**Problem**: `pixi add --pypi package` fails with build errors

**Solution**:
```bash
# Install build dependencies from conda first
pixi add python-build setuptools wheel

# Then retry PyPI package
pixi add --pypi package

# For packages needing system libraries
pixi add libgdal  # system library
pixi add --pypi gdal  # Python bindings

# Check if conda-forge version exists
pixi search gdal  # might have compiled version
```

### Issue: Environment Activation in Scripts

**Problem**: Need to run scripts outside of `pixi run`

**Solution**:
```bash
# Use pixi shell for interactive sessions
pixi shell
python script.py

# For automation, always use pixi run
pixi run python script.py

# In bash scripts
#!/usr/bin/env bash
eval "$(pixi shell-hook)"
python script.py

# In task definitions
[tool.pixi.tasks]
run-script = "python script.py"  # automatically in environment
```

### Issue: Lockfile Merge Conflicts

**Problem**: Git merge conflicts in `pixi.lock`

**Solution**:
```bash
# Accept one version
git checkout --theirs pixi.lock  # or --ours

# Regenerate lockfile
pixi install

# Commit regenerated lockfile
git add pixi.lock
git commit -m "Regenerate lockfile after merge"

# Prevention: coordinate updates with team
# One person updates dependencies at a time
```

### Issue: Missing System Dependencies

**Problem**: Package fails at runtime with "library not found"

**Solution**:
```bash
# Check what's actually in environment
pixi list

# Add system libraries explicitly
pixi add libgdal proj geos  # for geospatial
pixi add hdf5 netcdf4  # for climate data
pixi add mkl  # for optimized linear algebra

# Use conda for everything when possible
# Don't mix system packages with conda packages
```

### Issue: Cannot Find Executable in Environment

**Problem**: `pixi run mycommand` fails with "command not found"

**Solution**:
```bash
# List all installed packages
pixi list

# Check if package provides executable
pixi add --help  # documentation

# Ensure package is in active environment
[tool.pixi.feature.dev.dependencies]
mypackage = "*"

[tool.pixi.environments]
default = { features = ["dev"] }  # must include feature

# Or run in specific environment
pixi run --environment dev mycommand
```

### Issue: Want to Use Both Pixi and Conda

**Problem**: Existing conda environment, want to migrate gradually

**Solution**:
```bash
# Export existing conda environment
conda env export > environment.yml

# Import to pixi project
pixi init --format pyproject --import-environment environment.yml

# Or manually alongside
conda activate myenv  # activate conda env
pixi shell  # activate pixi env (nested)

# Long term: migrate fully to pixi
# Pixi replaces conda/mamba entirely
```

### Issue: Editable Install of Local Package

**Problem**: Want to develop local package in pixi environment

**Solution**:
```toml
[tool.pixi.pypi-dependencies]
mypackage = { path = ".", editable = true }

# Or for relative paths
sibling-package = { path = "../sibling", editable = true }
```

```bash
# Install in development mode
pixi install

# Changes to source immediately reflected
pixi run python -c "import mypackage; print(mypackage.__file__)"
```

### Issue: Need Different Python Versions

**Problem**: Test across Python 3.10, 3.11, 3.12

**Solution**:
```toml
[tool.pixi.feature.py310.dependencies]
python = "3.10.*"

[tool.pixi.feature.py311.dependencies]
python = "3.11.*"

[tool.pixi.feature.py312.dependencies]
python = "3.12.*"

[tool.pixi.environments]
py310 = { features = ["py310"], solve-group = "py310" }
py311 = { features = ["py311"], solve-group = "py311" }
py312 = { features = ["py312"], solve-group = "py312" }
```

```bash
# Test all versions
pixi run --environment py310 pytest
pixi run --environment py311 pytest
pixi run --environment py312 pytest
```

## Summary

Pixi revolutionizes scientific Python development by unifying conda and PyPI ecosystems with blazing-fast dependency resolution, reproducible multi-platform lockfiles, and seamless environment management. By leveraging `pyproject.toml` integration, pixi provides a modern, standards-compliant approach to managing complex scientific dependencies while maintaining compatibility with the broader Python ecosystem.

**Key advantages for scientific computing:**

1. **Optimized Scientific Packages**: Access conda-forge's pre-built binaries for NumPy, SciPy, and other compiled packages with MKL/OpenBLAS optimizations
2. **Complex Dependencies Made Simple**: Handle challenging packages like GDAL, netCDF4, and HDF5 that require C/Fortran/C++ system libraries
3. **True Reproducibility**: Multi-platform lockfiles ensure identical environments across Linux, macOS, and Windows
4. **Flexible Environment Management**: Feature-based environments for dev/test/prod, GPU/CPU, or any custom configuration
5. **Fast and Reliable**: 10-100x faster than conda with Rust-based parallel dependency resolution
6. **Task Automation**: Built-in task runner for scientific workflows, testing, and documentation
7. **Best of Both Worlds**: Seamlessly mix conda-forge optimized packages with PyPI's vast ecosystem

Whether you're conducting reproducible research, developing scientific software, or managing complex data analysis pipelines, pixi provides the robust foundation for modern scientific Python development. By replacing conda/mamba with pixi, you gain speed, reliability, and modern workflows while maintaining full access to the scientific Python ecosystem.

**Ready to get started?** Install pixi, initialize your project with `pixi init --format pyproject`, and experience the future of scientific Python package management.
