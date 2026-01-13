# yq Patterns Reference

Complete yq patterns for YAML/TOML processing.

## Basic YAML Operations

```bash
# Extract field
yq '.name' config.yaml

# Extract nested
yq '.services.web.image' docker-compose.yml

# List all keys
yq 'keys' config.yaml

# Get array element
yq '.volumes[0]' docker-compose.yml
```

## Docker Compose Queries

```bash
# List all service names
yq '.services | keys' docker-compose.yml

# Get all images
yq '.services[].image' docker-compose.yml

# Get environment variables for a service
yq '.services.web.environment' docker-compose.yml

# Find services with specific image
yq '.services | to_entries | map(select(.value.image | contains("nginx")))' docker-compose.yml
```

## Kubernetes Manifests

```bash
# Get resource name
yq '.metadata.name' deployment.yaml

# Get container images
yq '.spec.template.spec.containers[].image' deployment.yaml

# Get all labels
yq '.metadata.labels' deployment.yaml

# Multi-document YAML (---)
yq eval-all '.metadata.name' manifests.yaml
```

## GitHub Actions Workflows

```bash
# List all jobs
yq '.jobs | keys' .github/workflows/ci.yml

# Get steps for a job
yq '.jobs.build.steps[].name' .github/workflows/ci.yml

# Find jobs using specific action
yq '.jobs[].steps[] | select(.uses | contains("actions/checkout"))' .github/workflows/ci.yml

# Get all environment variables
yq '.env' .github/workflows/ci.yml
```

## TOML Processing

```bash
# Read TOML file
yq -p toml '.dependencies' Cargo.toml

# Convert TOML to JSON
yq -p toml -o json '.' config.toml

# Extract pyproject.toml dependencies
yq -p toml '.project.dependencies[]' pyproject.toml
```

## YAML Modification

```bash
# Update value (in-place)
yq -i '.version = "2.0.0"' config.yaml

# Add new field
yq -i '.new_field = "value"' config.yaml

# Delete field
yq -i 'del(.old_field)' config.yaml

# Add to array
yq -i '.tags += ["new-tag"]' config.yaml

# Merge YAML files
yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' base.yaml override.yaml
```
