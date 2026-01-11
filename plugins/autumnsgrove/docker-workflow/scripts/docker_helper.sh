#!/bin/bash

# Docker Helper Script
# Utilities for container inspection, health checks, and automation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if container exists
container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^${1}$"
}

# Check if container is running
container_running() {
    docker ps --format '{{.Names}}' | grep -q "^${1}$"
}

# Display usage information
usage() {
    cat <<EOF
Docker Helper Script - Container Management Utilities

Usage: $0 <command> [arguments]

Commands:
    health <container>              Check container health status
    inspect <container>             Display container details
    logs <container> [lines]        View container logs (default: 100 lines)
    stats <container>               Show container resource usage
    shell <container>               Open shell in running container
    cleanup                         Remove stopped containers and unused images
    size <image>                    Analyze image size and layers
    network <container>             Show network information
    ports <container>               Display port mappings
    env <container>                 Display environment variables
    processes <container>           Show running processes in container
    restart <container>             Restart container with health check
    watch <container>               Watch container logs in real-time
    backup <container> <dest>       Backup container volumes
    optimize <image>                Suggest image optimization techniques

Examples:
    $0 health myapp
    $0 logs myapp 200
    $0 shell myapp
    $0 cleanup
    $0 size myapp:latest
    $0 network myapp

EOF
}

# Check container health
check_health() {
    local container=$1

    if ! container_exists "$container"; then
        error "Container '$container' does not exist"
        return 1
    fi

    info "Checking health status for container: $container"

    if ! container_running "$container"; then
        error "Container '$container' is not running"
        docker ps -a --filter "name=^${container}$" --format "table {{.Names}}\t{{.Status}}\t{{.State}}"
        return 1
    fi

    local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")

    if [ "$health_status" = "none" ]; then
        warning "No health check configured for this container"
    elif [ "$health_status" = "healthy" ]; then
        success "Container is healthy"
    elif [ "$health_status" = "unhealthy" ]; then
        error "Container is unhealthy"
        docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' "$container"
        return 1
    else
        warning "Health status: $health_status"
    fi

    # Show basic stats
    docker stats --no-stream "$container" --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

    return 0
}

# Inspect container details
inspect_container() {
    local container=$1

    if ! container_exists "$container"; then
        error "Container '$container' does not exist"
        return 1
    fi

    info "Container details for: $container"
    echo ""

    # Basic info
    echo "=== Basic Information ==="
    docker inspect --format='Image: {{.Config.Image}}' "$container"
    docker inspect --format='Created: {{.Created}}' "$container"
    docker inspect --format='State: {{.State.Status}}' "$container"
    docker inspect --format='Restart Count: {{.RestartCount}}' "$container"
    echo ""

    # Network info
    echo "=== Network ==="
    docker inspect --format='IP Address: {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container"
    docker inspect --format='Ports: {{json .NetworkSettings.Ports}}' "$container" | jq 2>/dev/null || docker inspect --format='Ports: {{.NetworkSettings.Ports}}' "$container"
    echo ""

    # Mounts
    echo "=== Volumes ==="
    docker inspect --format='{{range .Mounts}}{{.Type}}: {{.Source}} -> {{.Destination}}{{println}}{{end}}' "$container"
    echo ""

    # Resource limits
    echo "=== Resource Limits ==="
    docker inspect --format='Memory Limit: {{.HostConfig.Memory}}' "$container"
    docker inspect --format='CPU Shares: {{.HostConfig.CpuShares}}' "$container"
}

# View container logs
view_logs() {
    local container=$1
    local lines=${2:-100}

    if ! container_exists "$container"; then
        error "Container '$container' does not exist"
        return 1
    fi

    info "Showing last $lines lines of logs for: $container"
    docker logs --tail "$lines" "$container"
}

# Show container stats
show_stats() {
    local container=$1

    if ! container_running "$container"; then
        error "Container '$container' is not running"
        return 1
    fi

    info "Resource usage for: $container"
    docker stats "$container"
}

# Open shell in container
open_shell() {
    local container=$1

    if ! container_running "$container"; then
        error "Container '$container' is not running"
        return 1
    fi

    info "Opening shell in container: $container"

    # Try sh first (alpine), then bash
    if docker exec -it "$container" sh -c "exit" 2>/dev/null; then
        docker exec -it "$container" sh
    elif docker exec -it "$container" bash -c "exit" 2>/dev/null; then
        docker exec -it "$container" bash
    else
        error "No shell found in container"
        return 1
    fi
}

# Cleanup unused resources
cleanup_docker() {
    info "Cleaning up Docker resources..."

    # Remove stopped containers
    echo "Removing stopped containers..."
    docker container prune -f

    # Remove dangling images
    echo "Removing dangling images..."
    docker image prune -f

    # Remove unused volumes
    echo "Removing unused volumes..."
    docker volume prune -f

    # Remove unused networks
    echo "Removing unused networks..."
    docker network prune -f

    success "Cleanup complete"

    # Show disk usage
    echo ""
    info "Current disk usage:"
    docker system df
}

# Analyze image size
analyze_size() {
    local image=$1

    if ! docker image inspect "$image" &>/dev/null; then
        error "Image '$image' does not exist"
        return 1
    fi

    info "Analyzing image: $image"
    echo ""

    # Total size
    echo "=== Image Size ==="
    docker images "$image" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
    echo ""

    # Layer breakdown
    echo "=== Layer History ==="
    docker history "$image" --no-trunc --format "table {{.CreatedBy}}\t{{.Size}}"
    echo ""

    # Suggest optimization
    local size=$(docker image inspect "$image" --format='{{.Size}}')
    local size_mb=$((size / 1024 / 1024))

    if [ $size_mb -gt 500 ]; then
        warning "Image is quite large (${size_mb}MB). Consider:"
        echo "  - Using a smaller base image (alpine, slim)"
        echo "  - Using multi-stage builds"
        echo "  - Removing build dependencies in the same RUN command"
        echo "  - Using .dockerignore to exclude unnecessary files"
    else
        success "Image size is reasonable (${size_mb}MB)"
    fi
}

# Show network information
show_network() {
    local container=$1

    if ! container_exists "$container"; then
        error "Container '$container' does not exist"
        return 1
    fi

    info "Network information for: $container"
    echo ""

    echo "=== Networks ==="
    docker inspect --format='{{range $net,$v := .NetworkSettings.Networks}}{{$net}}: {{.IPAddress}}{{println}}{{end}}' "$container"
    echo ""

    echo "=== DNS ==="
    docker inspect --format='{{.HostConfig.Dns}}' "$container"
    echo ""

    # Test connectivity if running
    if container_running "$container"; then
        echo "=== Connectivity Test ==="
        echo "Testing external connectivity..."
        if docker exec "$container" ping -c 1 8.8.8.8 &>/dev/null; then
            success "External network: OK"
        else
            error "External network: FAILED"
        fi
    fi
}

# Show port mappings
show_ports() {
    local container=$1

    if ! container_exists "$container"; then
        error "Container '$container' does not exist"
        return 1
    fi

    info "Port mappings for: $container"
    docker port "$container"
}

# Show environment variables
show_env() {
    local container=$1

    if ! container_running "$container"; then
        error "Container '$container' is not running"
        return 1
    fi

    info "Environment variables for: $container"
    docker exec "$container" env | sort
}

# Show running processes
show_processes() {
    local container=$1

    if ! container_running "$container"; then
        error "Container '$container' is not running"
        return 1
    fi

    info "Processes in: $container"
    docker top "$container"
}

# Restart container with health check
restart_container() {
    local container=$1

    if ! container_exists "$container"; then
        error "Container '$container' does not exist"
        return 1
    fi

    info "Restarting container: $container"
    docker restart "$container"

    # Wait for container to be running
    sleep 2

    if container_running "$container"; then
        success "Container restarted successfully"

        # Check health if configured
        local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
        if [ "$health_status" != "none" ]; then
            info "Waiting for health check..."
            sleep 5
            check_health "$container"
        fi
    else
        error "Container failed to start"
        view_logs "$container" 50
        return 1
    fi
}

# Watch logs in real-time
watch_logs() {
    local container=$1

    if ! container_exists "$container"; then
        error "Container '$container' does not exist"
        return 1
    fi

    info "Watching logs for: $container (Ctrl+C to exit)"
    docker logs -f --tail 100 "$container"
}

# Backup container volumes
backup_volumes() {
    local container=$1
    local dest=$2

    if [ -z "$dest" ]; then
        error "Destination path required"
        echo "Usage: $0 backup <container> <destination>"
        return 1
    fi

    if ! container_exists "$container"; then
        error "Container '$container' does not exist"
        return 1
    fi

    info "Backing up volumes for: $container"

    # Get volume mounts
    local volumes=$(docker inspect --format='{{range .Mounts}}{{.Destination}}{{"\n"}}{{end}}' "$container")

    if [ -z "$volumes" ]; then
        warning "No volumes found for container"
        return 0
    fi

    mkdir -p "$dest"

    while IFS= read -r volume; do
        if [ -n "$volume" ]; then
            info "Backing up volume: $volume"
            local volume_name=$(echo "$volume" | tr '/' '_')
            docker run --rm \
                --volumes-from "$container" \
                -v "$dest:/backup" \
                alpine \
                tar czf "/backup/${container}${volume_name}.tar.gz" "$volume"
        fi
    done <<< "$volumes"

    success "Backup complete: $dest"
}

# Suggest optimization techniques
optimize_image() {
    local image=$1

    if ! docker image inspect "$image" &>/dev/null; then
        error "Image '$image' does not exist"
        return 1
    fi

    info "Analyzing image for optimization: $image"
    echo ""

    # Check base image
    local base=$(docker history "$image" --no-trunc | tail -1 | awk '{print $2}')
    echo "=== Base Image Analysis ==="
    echo "Base image appears to be: $base"

    if [[ "$base" == *"alpine"* ]]; then
        success "Using Alpine base (good for size)"
    elif [[ "$base" == *"slim"* ]]; then
        success "Using slim variant (reasonable size)"
    else
        warning "Consider using Alpine or slim base images for smaller size"
    fi
    echo ""

    # Check for multi-stage build
    echo "=== Multi-Stage Build Check ==="
    local stages=$(docker history "$image" --no-trunc --format '{{.CreatedBy}}' | grep -c "FROM" || echo "1")
    if [ "$stages" -gt 1 ]; then
        success "Multi-stage build detected"
    else
        warning "Consider using multi-stage builds to reduce final image size"
    fi
    echo ""

    # Layer analysis
    echo "=== Layer Analysis ==="
    local layer_count=$(docker history "$image" --format '{{.ID}}' | wc -l)
    echo "Total layers: $layer_count"

    if [ "$layer_count" -gt 30 ]; then
        warning "High number of layers. Consider combining RUN commands"
    else
        success "Layer count is reasonable"
    fi
    echo ""

    # Size recommendations
    analyze_size "$image"
}

# Main command handler
main() {
    if [ $# -eq 0 ]; then
        usage
        exit 1
    fi

    local command=$1
    shift

    case "$command" in
        health)
            check_health "$@"
            ;;
        inspect)
            inspect_container "$@"
            ;;
        logs)
            view_logs "$@"
            ;;
        stats)
            show_stats "$@"
            ;;
        shell)
            open_shell "$@"
            ;;
        cleanup)
            cleanup_docker
            ;;
        size)
            analyze_size "$@"
            ;;
        network)
            show_network "$@"
            ;;
        ports)
            show_ports "$@"
            ;;
        env)
            show_env "$@"
            ;;
        processes|ps)
            show_processes "$@"
            ;;
        restart)
            restart_container "$@"
            ;;
        watch)
            watch_logs "$@"
            ;;
        backup)
            backup_volumes "$@"
            ;;
        optimize)
            optimize_image "$@"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            error "Unknown command: $command"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
