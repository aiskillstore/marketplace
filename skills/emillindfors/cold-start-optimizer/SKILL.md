---
name: cold-start-optimizer
description: Provides guidance on reducing Lambda cold start times through binary optimization, lazy initialization, and deployment strategies. Activates when users discuss cold starts or deployment configuration.
allowed-tools: Read, Grep
version: 1.0.0
---

# Cold Start Optimizer Skill

You are an expert at optimizing AWS Lambda cold starts for Rust functions. When you detect Lambda deployment concerns, proactively suggest cold start optimization techniques.

## When to Activate

Activate when you notice:
- Lambda deployment configurations
- Questions about cold starts or initialization
- Missing cargo.toml optimizations
- Global state initialization patterns

## Optimization Strategies

### 1. Binary Size Reduction

**Cargo.toml Configuration**:
```toml
[profile.release]
opt-level = 'z'     # Optimize for size (vs 's' or 3)
lto = true          # Link-time optimization
codegen-units = 1   # Single codegen unit for better optimization
strip = true        # Strip symbols from binary
panic = 'abort'     # Smaller panic handler
```

**Impact**: Can reduce binary size by 50-70%, significantly improving cold start times.

### 2. Lazy Initialization

**Bad Pattern**:
```rust
// ❌ Initializes everything on cold start
static HTTP_CLIENT: reqwest::Client = reqwest::Client::new();
static DB_POOL: PgPool = create_pool().await;  // Won't even compile

#[tokio::main]
async fn main() -> Result<(), Error> {
    // Heavy initialization before handler is ready
    tracing_subscriber::fmt().init();
    init_aws_sdk().await;
    warm_cache().await;

    run(service_fn(handler)).await
}
```

**Good Pattern**:
```rust
use std::sync::OnceLock;

// ✅ Lazy initialization - only creates when first used
static HTTP_CLIENT: OnceLock<reqwest::Client> = OnceLock::new();

fn get_client() -> &'static reqwest::Client {
    HTTP_CLIENT.get_or_init(|| {
        reqwest::Client::builder()
            .timeout(Duration::from_secs(10))
            .build()
            .unwrap()
    })
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    // Minimal initialization
    tracing_subscriber::fmt()
        .without_time()
        .init();

    run(service_fn(handler)).await
}
```

### 3. Dependency Optimization

**Audit Dependencies**:
```bash
cargo tree
cargo bloat --release
```

**Reduce Features**:
```toml
[dependencies]
# ❌ BAD: Pulls in everything
tokio = "1"

# ✅ GOOD: Only what you need
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }

# ✅ Disable default features when possible
serde = { version = "1", default-features = false, features = ["derive"] }
```

### 4. ARM64 (Graviton2)

**Build for ARM64**:
```bash
cargo lambda build --release --arm64
```

**Deploy with ARM64**:
```bash
cargo lambda deploy --memory 512 --arch arm64
```

**Benefits**:
- 20% better price/performance
- Often faster cold starts
- Lower memory footprint

### 5. Provisioned Concurrency

For critical functions with strict latency requirements:

```bash
# CloudFormation/SAM
ProvisionedConcurrencyConfig:
  ProvisionedConcurrentExecutions: 2

# Or via AWS CLI
aws lambda put-provisioned-concurrency-config \
  --function-name my-function \
  --provisioned-concurrent-executions 2
```

**Trade-off**: Costs more but eliminates cold starts.

## Initialization Patterns

### Pattern 1: OnceLock for Expensive Resources

```rust
use std::sync::OnceLock;

static AWS_CONFIG: OnceLock<aws_config::SdkConfig> = OnceLock::new();
static S3_CLIENT: OnceLock<aws_sdk_s3::Client> = OnceLock::new();

async fn get_s3_client() -> &'static aws_sdk_s3::Client {
    S3_CLIENT.get_or_init(|| {
        let config = AWS_CONFIG.get_or_init(|| {
            tokio::runtime::Handle::current()
                .block_on(aws_config::load_from_env())
        });
        aws_sdk_s3::Client::new(config)
    })
}
```

### Pattern 2: Conditional Initialization

```rust
async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {
    // Only initialize if needed
    let client = if event.payload.needs_api_call {
        Some(get_http_client())
    } else {
        None
    };

    // Process without client if not needed
    process(event.payload, client).await
}
```

## Measurement and Monitoring

### CloudWatch Insights Query

```
filter @type = "REPORT"
| stats avg(@initDuration), max(@initDuration), count(*) by bin(5m)
```

### Local Testing

```bash
# Measure binary size
ls -lh target/lambda/bootstrap/bootstrap.zip

# Test cold start locally
cargo lambda watch
cargo lambda invoke --data-ascii '{"test": "data"}'
```

## Best Practices Checklist

- [ ] Configure release profile for size optimization
- [ ] Use lazy initialization with OnceLock
- [ ] Minimize dependencies and features
- [ ] Build for ARM64 (Graviton2)
- [ ] Audit binary size with cargo bloat
- [ ] Measure cold starts in CloudWatch
- [ ] Use provisioned concurrency for critical paths
- [ ] Keep initialization in main() minimal

## Your Approach

When you see Lambda deployment code:
1. Check Cargo.toml for optimization settings
2. Look for eager initialization that could be lazy
3. Suggest ARM64 deployment
4. Provide measurement strategies

Proactively suggest cold start optimizations when you detect Lambda configuration or initialization patterns.
