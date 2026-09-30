# Search Patterns for Reference Repositories

Base directory: `~/projects/referenzen/`

## Find files by name

```bash
# Find a specific file in one repo
find ~/projects/referenzen/repo-name -name "Chart.yaml"

# Find across all repos
find ~/projects/referenzen -name "values.yaml"
```

## Search for patterns (grep)

```bash
# Search in a specific file
grep -n "some-dependency" ~/projects/referenzen/repo-name/pom.xml

# Recursive search in a directory
grep -rn "some-dependency" ~/projects/referenzen/repo-name/

# Search with context lines
grep -rn -A 3 -B 3 "some-pattern" ~/projects/referenzen/repo-name/src/
```

## Explore project structure

```bash
# Top-level structure
ls ~/projects/referenzen/repo-name/

# Helm chart layout
ls ~/projects/referenzen/repo-name/helm-charts/

# Read a specific file
cat ~/projects/referenzen/repo-name/helm-charts/values.yaml
```

## List all available reference repos

```bash
ls ~/projects/referenzen/

# Show tracked repos from list file (if it exists)
cat ~/claude-shared/projekte.txt
```

## Citing patterns

Always tell the user which project and file a pattern came from:

> Pattern adopted from `your-service` →
> `~/projects/referenzen/your-service/helm-charts/Chart.yaml` (line 4)
