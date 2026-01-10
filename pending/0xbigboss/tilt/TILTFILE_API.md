# Tiltfile API Reference

## Table of Contents

- [Resource Types](#resource-types)
- [Dependency Ordering](#dependency-ordering)
- [Live Update](#live-update)
- [Configuration](#configuration)
- [Extensions](#extensions)
- [Data Handling](#data-handling)
- [File Operations](#file-operations)

## Resource Types

### local_resource

Runs commands on host machine.

```starlark
local_resource(
    'name',
    cmd='command',              # One-time command
    serve_cmd='server',         # Long-running process (optional)
    deps=['file.txt'],          # File dependencies trigger re-run
    resource_deps=['other'],    # Wait for other resources first
    auto_init=True,             # Run on tilt up (default: True)
    allow_parallel=False,       # Concurrent execution (default: False)
    readiness_probe=probe(),    # Health check for serve_cmd
    trigger_mode=TRIGGER_MODE_AUTO,  # AUTO or MANUAL
    labels=['group'],           # UI grouping
)
```

**cmd vs serve_cmd**:
- `cmd`: Runs once, re-runs on file changes or trigger
- `serve_cmd`: Long-running process, restarted on file changes

### docker_build

Builds container images.

```starlark
docker_build(
    'image-name',
    '.',                        # Build context
    dockerfile='Dockerfile',    # Dockerfile path (default: Dockerfile)
    target='stage',             # Multi-stage target (optional)
    build_args={'ENV': 'dev'},  # Build arguments
    only=['src/', 'go.mod'],    # Include only these paths
    ignore=['tests/', '*.md'],  # Exclude paths
    live_update=[...],          # Fast sync without rebuild
)
```

### custom_build

Custom build commands for non-Docker builds.

```starlark
custom_build(
    'image-name',
    'bazel build //app:image',  # Build command
    deps=['src/', 'BUILD'],     # File dependencies
    tag='dev',                  # Image tag
    skips_local_docker=True,    # Image not in local docker
    live_update=[...],
)
```

### k8s_yaml

Loads Kubernetes manifests.

```starlark
k8s_yaml('manifests.yaml')
k8s_yaml(['deploy.yaml', 'service.yaml'])
k8s_yaml(helm('chart/', values='values.yaml'))
k8s_yaml(kustomize('overlays/dev'))
k8s_yaml(local('kubectl kustomize .'))  # Command output
```

### k8s_resource

Configures Kubernetes resources.

```starlark
k8s_resource(
    'deployment-name',
    port_forwards='8080:80',           # Single forward
    port_forwards=['8080:80', '9090'], # Multiple forwards
    resource_deps=['database'],        # Dependencies
    objects=['configmap:my-config'],   # Group additional objects
    labels=['backend'],                # UI grouping
    trigger_mode=TRIGGER_MODE_MANUAL,
)
```

### docker_compose

Docker Compose integration.

```starlark
docker_compose('docker-compose.yml')
docker_compose(['docker-compose.yml', 'docker-compose.override.yml'])
```

### dc_resource

Configures Docker Compose services.

```starlark
dc_resource(
    'service-name',
    resource_deps=['setup'],
    trigger_mode=TRIGGER_MODE_AUTO,
    labels=['services'],
)
```

## Dependency Ordering

### Explicit Dependencies

```starlark
# Resource waits for dependencies before starting
k8s_resource('api', resource_deps=['database', 'redis'])
local_resource('migrate', resource_deps=['database'])
```

### Implicit Dependencies

```starlark
# Image references create automatic dependencies
docker_build('myapp', '.')
k8s_yaml('deploy.yaml')  # If uses myapp image, dependency is automatic
```

### Trigger Modes

```starlark
# Manual trigger - only updates when explicitly triggered
k8s_resource('expensive-build', trigger_mode=TRIGGER_MODE_MANUAL)

# Auto trigger (default) - updates on file changes
k8s_resource('api', trigger_mode=TRIGGER_MODE_AUTO)

# Set default for all resources
trigger_mode(TRIGGER_MODE_MANUAL)
```

## Live Update

Fast container updates without full rebuild.

**Step ordering matters:**
1. `fall_back_on()` steps must come FIRST
2. `sync()` steps come next
3. `run()` steps must come AFTER sync steps

```starlark
docker_build(
    'myapp',
    '.',
    live_update=[
        # 1. Full rebuild triggers (must be first)
        fall_back_on(['package.json', 'package-lock.json']),

        # 2. Sync files to container
        sync('./src', '/app/src'),

        # 3. Run commands after sync
        run('npm run build', trigger=['./src']),
    ]
)
```

### Live Update Steps

```starlark
fall_back_on(['package.json'])            # Force full rebuild (must be first)
sync('./local/path', '/container/path')   # Copy files
run('command')                            # Run in container
run('command', trigger=['./src'])         # Run only when trigger files change
run('command', echo_off=True)             # Run without echoing command
restart_container()                       # Restart container process
```

## Configuration

### CLI Arguments

```starlark
config.define_string('env', args=True, usage='Environment name')
config.define_bool('debug', usage='Enable debug mode')
config.define_string_list('services', usage='Services to enable')

cfg = config.parse()

env = cfg.get('env', 'dev')
if cfg.get('debug'):
    local_resource('debug-tools', ...)
```

Usage: `tilt up -- --env=staging --debug`

### Selective Resources

```starlark
# Only enable specific resources
config.set_enabled_resources(['api', 'web'])

# Clear and set new list
config.clear_enabled_resources()
config.set_enabled_resources(['database'])
```

### Context Validation

```starlark
# Only allow specific k8s contexts
allow_k8s_contexts(['docker-desktop', 'minikube', 'kind-*'])

# Get current context
ctx = k8s_context()
ns = k8s_namespace()
```

### Default Registry

```starlark
# Push images to registry instead of loading directly
default_registry('gcr.io/my-project')
default_registry('localhost:5000', single_name='dev')
```

## Extensions

### Loading Extensions

```starlark
load('ext://restart_process', 'docker_build_with_restart')
load('ext://namespace', 'namespace_create', 'namespace_inject')
load('ext://git_resource', 'git_checkout')
```

Extensions are loaded from https://github.com/tilt-dev/tilt-extensions

### Custom Extension Repository

```starlark
v1alpha1.extension_repo(
    name='my-extensions',
    url='https://github.com/org/tilt-extensions',
    ref='v1.0.0'
)
load('ext://my-extensions/my-ext', 'my_function')
```

## Data Handling

### Reading Files

```starlark
content = read_file('config.yaml')
data = read_json('config.json')
data = read_yaml('config.yaml')
```

### Encoding/Decoding

```starlark
obj = decode_json('{"key": "value"}')
obj = decode_yaml('key: value')
yaml_list = decode_yaml_stream(multi_doc_yaml)

json_str = encode_json(obj)
yaml_str = encode_yaml(obj)
```

### Filtering YAML

```starlark
# Filter by kind
deployments = filter_yaml(manifests, kind='Deployment')

# Filter by name
api = filter_yaml(manifests, name='api')

# Filter by labels
selected = filter_yaml(manifests, labels={'app': 'myapp'})
```

## File Operations

### Watch Files

```starlark
# Explicit file watching
watch_file('config/settings.yaml')

# List directory contents (automatically watched)
files = listdir('manifests/', recursive=True)
```

### Local Commands

```starlark
# Run command and capture output
output = local('kubectl get nodes -o name')

# Run without capturing
local('echo "Hello"', quiet=True)

# With environment variables
local('my-script.sh', env={'DEBUG': '1'})
```

### Path Operations

```starlark
cwd = os.getcwd()
exists = os.path.exists('file.txt')
joined = os.path.join('dir', 'file.txt')
base = os.path.basename('/path/to/file.txt')
dir = os.path.dirname('/path/to/file.txt')
```

## UI Customization

### Labels (Grouping)

```starlark
k8s_resource('api', labels=['backend'])
k8s_resource('web', labels=['frontend'])
local_resource('tests', labels=['ci'])
```

### Links

```starlark
k8s_resource('api', links=[
    link('http://localhost:8080', 'API'),
    link('http://localhost:8080/docs', 'Swagger'),
])
```

## Update Settings

```starlark
update_settings(
    max_parallel_updates=3,    # Concurrent updates
    k8s_upsert_timeout_secs=60,
    suppress_unused_image_warnings=['base-image'],
)
```

## CI Settings

```starlark
ci_settings(
    k8s_grace_period='10s',    # Shutdown grace period
    timeout='10m',             # Overall timeout
)
```
