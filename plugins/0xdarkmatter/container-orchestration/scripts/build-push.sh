#!/bin/bash
# Build and push Docker image
# Usage: ./build-push.sh [--tag TAG] [--registry REGISTRY] [--push]

set -e

# Defaults
REGISTRY="${DOCKER_REGISTRY:-}"
TAG="${IMAGE_TAG:-latest}"
PUSH=false
DOCKERFILE="Dockerfile"
CONTEXT="."

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tag|-t)
            TAG="$2"
            shift 2
            ;;
        --registry|-r)
            REGISTRY="$2"
            shift 2
            ;;
        --push|-p)
            PUSH=true
            shift
            ;;
        --dockerfile|-f)
            DOCKERFILE="$2"
            shift 2
            ;;
        --context|-c)
            CONTEXT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get image name from directory or git
if [ -z "$IMAGE_NAME" ]; then
    IMAGE_NAME=$(basename "$(pwd)")
fi

# Build full image name
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${TAG}"
else
    FULL_IMAGE="${IMAGE_NAME}:${TAG}"
fi

echo "=== Building Docker Image ==="
echo "Image: $FULL_IMAGE"
echo "Dockerfile: $DOCKERFILE"
echo "Context: $CONTEXT"
echo ""

# Build
docker build \
    -t "$FULL_IMAGE" \
    -f "$DOCKERFILE" \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    "$CONTEXT"

echo ""
echo "=== Build Complete ==="
echo "Image: $FULL_IMAGE"

# Push if requested
if [ "$PUSH" = true ]; then
    echo ""
    echo "=== Pushing Image ==="
    docker push "$FULL_IMAGE"
    echo "Pushed: $FULL_IMAGE"
fi

# Show image info
echo ""
echo "=== Image Info ==="
docker images "$FULL_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
