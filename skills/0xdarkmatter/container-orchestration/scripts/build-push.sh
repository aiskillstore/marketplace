#!/usr/bin/env bash
# Build and (optionally) push a Docker image with a predictable, agent-safe CLI.
#
# Usage:   build-push.sh [--tag TAG] [--registry REG] [--push]
#                        [--dockerfile FILE] [--context DIR] [--dry-run] [--help]
# Input:   argv only. Env overrides: IMAGE_NAME, IMAGE_TAG, DOCKER_REGISTRY.
# Output:  stdout carries the resolved plan as plain "Key: Value" data lines
#          (Image / Dockerfile / Context, [+ Pushed] after a push) — identical
#          data to the pre-backfill behaviour, so downstream parsers are
#          unaffected. Under --dry-run the planned `docker build` command is
#          appended and nothing is executed.
# Stderr:  progress banners ("=== Building ... ===") and diagnostics.
# Exit:    0 ok, 2 usage (unknown flag or missing value), 5 missing-dep (docker
#          not on PATH), 1 build or push failed.
#
# Examples:
#   build-push.sh --tag v1.2.3 --registry ghcr.io/acme --push
#   IMAGE_NAME=svc build-push.sh --dry-run --tag dev
#   build-push.sh --dockerfile Dockerfile.prod --context ./app
set -uo pipefail

usage() {
    cat <<'EOF'
Usage: build-push.sh [OPTIONS]

Build and optionally push a Docker image.

Options:
  -t, --tag TAG          Image tag (default: $IMAGE_TAG or "latest").
  -r, --registry REG     Registry prefix, e.g. ghcr.io/acme (default: $DOCKER_REGISTRY).
  -p, --push             Push the image after a successful build.
  -f, --dockerfile FILE  Dockerfile path (default: Dockerfile).
  -c, --context DIR      Build context directory (default: .).
  -n, --dry-run          Resolve and print the plan WITHOUT invoking docker.
  -h, --help             Show this help and exit.

Environment:
  IMAGE_NAME        Image name (default: current directory basename).
  IMAGE_TAG         Default tag.
  DOCKER_REGISTRY   Default registry prefix.

Exit codes:
  0  success
  2  usage error (unknown flag or missing value)
  5  docker is not installed (missing dependency)
  1  build or push failed

Examples:
  build-push.sh --tag v1.2.3 --registry ghcr.io/acme --push
  IMAGE_NAME=svc build-push.sh --dry-run --tag dev
  build-push.sh --dockerfile Dockerfile.prod --context ./app
EOF
}

# Defaults
REGISTRY="${DOCKER_REGISTRY:-}"
TAG="${IMAGE_TAG:-latest}"
PUSH=false
DOCKERFILE="Dockerfile"
CONTEXT="."
DRY_RUN=false

# Parse arguments — runs with NO docker dependency so --help / validation never
# require a running daemon.
need_value() {
    echo "build-push.sh: $1 requires a value" >&2
    exit 2
}
while [[ $# -gt 0 ]]; do
    case $1 in
        --tag|-t)
            [[ $# -ge 2 ]] || need_value "$1"; TAG="$2"; shift 2 ;;
        --registry|-r)
            [[ $# -ge 2 ]] || need_value "$1"; REGISTRY="$2"; shift 2 ;;
        --push|-p)
            PUSH=true; shift ;;
        --dockerfile|-f)
            [[ $# -ge 2 ]] || need_value "$1"; DOCKERFILE="$2"; shift 2 ;;
        --context|-c)
            [[ $# -ge 2 ]] || need_value "$1"; CONTEXT="$2"; shift 2 ;;
        --dry-run|-n)
            DRY_RUN=true; shift ;;
        --help|-h)
            usage; exit 0 ;;
        *)
            echo "build-push.sh: unknown option: $1" >&2
            echo "Run 'build-push.sh --help' for usage." >&2
            exit 2 ;;
    esac
done

# Resolve image name (env override, else current directory) and full reference.
IMAGE_NAME="${IMAGE_NAME:-$(basename "$(pwd)")}"
if [[ -n "$REGISTRY" ]]; then
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${TAG}"
else
    FULL_IMAGE="${IMAGE_NAME}:${TAG}"
fi

# Progress banners are chatter -> stderr; the resolved Image/Dockerfile/Context
# are the data product -> stdout (unchanged from pre-backfill so anything that
# keyed off "Image: ..." keeps working).
banner() { printf '=== %s ===\n' "$*" >&2; }

# Dry-run: validate args and print the plan, never touching docker.
if [[ "$DRY_RUN" = true ]]; then
    banner "Dry run (no docker invoked)"
    printf 'Image: %s\n' "$FULL_IMAGE"
    printf 'Dockerfile: %s\n' "$DOCKERFILE"
    printf 'Context: %s\n' "$CONTEXT"
    printf 'Push: %s\n' "$PUSH"
    printf 'Plan: docker build -t %s -f %s %s' "$FULL_IMAGE" "$DOCKERFILE" "$CONTEXT"
    [[ "$PUSH" = true ]] && printf ' && docker push %s' "$FULL_IMAGE"
    printf '\n'
    exit 0
fi

# Real path: docker is required from here on.
if ! command -v docker >/dev/null 2>&1; then
    echo "build-push.sh: docker is not installed (or not on PATH)." >&2
    echo "  Install Docker: https://docs.docker.com/get-docker/" >&2
    exit 5
fi

banner "Building Docker Image"
printf 'Image: %s\n' "$FULL_IMAGE"
printf 'Dockerfile: %s\n' "$DOCKERFILE"
printf 'Context: %s\n' "$CONTEXT"
printf '\n'

# Build — a failed build is a runtime error (exit 1), distinct from usage (2).
if ! docker build \
        -t "$FULL_IMAGE" \
        -f "$DOCKERFILE" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        "$CONTEXT"; then
    echo "build-push.sh: docker build failed" >&2
    exit 1
fi

banner "Build Complete"
printf 'Image: %s\n' "$FULL_IMAGE"

# Push if requested.
if [[ "$PUSH" = true ]]; then
    banner "Pushing Image"
    if ! docker push "$FULL_IMAGE"; then
        echo "build-push.sh: docker push failed" >&2
        exit 1
    fi
    printf 'Pushed: %s\n' "$FULL_IMAGE"
fi

# Show image info.
banner "Image Info"
docker images "$FULL_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
