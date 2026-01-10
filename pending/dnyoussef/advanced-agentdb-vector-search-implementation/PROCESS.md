# Advanced AgentDB Vector Search - Detailed Process Walkthrough

This document provides a detailed walkthrough of the advanced AgentDB vector search implementation process, including setup, configuration, custom metrics, optimization, and production deployment.

## Process Overview

The advanced AgentDB implementation follows a 5-phase approach:

1. **Setup AgentDB Infrastructure** - Multi-database cluster initialization
2. **Configure Advanced Features** - QUIC sync, routing, coordination
3. **Implement Custom Distance Metrics** - Domain-specific similarity functions
4. **Optimize Performance** - Indexing, caching, quantization
5. **Deploy and Monitor** - Production deployment with full observability

## Phase 1: Setup AgentDB Infrastructure

### Objectives
- Initialize primary database with advanced features enabled
- Deploy replica databases for high availability
- Configure QUIC synchronization for real-time replication
- Setup health monitoring and alerting

### Step-by-Step Process

#### 1.1 Install Dependencies

```bash
# Core AgentDB with advanced features
npm install agentdb-advanced@latest

# QUIC synchronization module
npm install @agentdb/quic-sync

# Distributed coordination
npm install @agentdb/distributed

# Performance optimization
npm install @agentdb/optimization

# Monitoring and observability
npm install @agentdb/monitoring
```

#### 1.2 Initialize Primary Database

```typescript
import { AgentDB } from 'agentdb-advanced';

const primaryDB = new AgentDB({
  name: 'primary-vector-db',
  dimensions: 1536, // OpenAI ada-002 embedding size
  indexType: 'hnsw', // Hierarchical Navigable Small World
  distanceMetric: 'cosine',
  persistPath: './data/primary',
  advanced: {
    enableQUIC: true,      // Enable QUIC synchronization
    multiDB: true,         // Enable multi-database management
    hybridSearch: true,    // Enable hybrid search capabilities
    compression: 'zstd',   // Use Zstandard compression
    encryption: 'aes-256'  // Encrypt data at rest
  }
});

// Initialize database (creates indexes, allocates memory)
await primaryDB.initialize();

console.log('Primary database initialized:', {
  id: primaryDB.id,
  capacity: primaryDB.capacity,
  status: primaryDB.status
});
```

#### 1.3 Deploy Replica Databases

```typescript
// Create two replicas for high availability
const replica1 = await AgentDB.createReplica('replica-1', {
  primary: primaryDB,
  syncMode: 'quic',           // Use QUIC for low-latency sync
  persistPath: './data/replica-1',
  syncConfig: {
    maxStreams: 100,          // Maximum concurrent QUIC streams
    idleTimeout: 30000,       // 30 second idle timeout
    keepAlive: 5000,          // 5 second keep-alive
    priority: 'high'          // High priority replication
  }
});

const replica2 = await AgentDB.createReplica('replica-2', {
  primary: primaryDB,
  syncMode: 'quic',
  persistPath: './data/replica-2',
  syncConfig: {
    maxStreams: 100,
    idleTimeout: 30000,
    keepAlive: 5000,
    priority: 'high'
  }
});

const replicas = [replica1, replica2];

console.log('Replicas deployed:', replicas.map(r => ({
  id: r.id,
  status: r.status,
  syncLag: r.syncLag
})));
```

#### 1.4 Setup Health Monitoring

```typescript
const monitor = primaryDB.createMonitor({
  checkInterval: 5000,      // Check every 5 seconds
  metrics: [
    'latency',              // Query latency metrics
    'throughput',           // Insert/search throughput
    'replication-lag',      // Sync lag between replicas
    'memory-usage',         // Memory consumption
    'error-rate'            // Error rate tracking
  ],
  alerts: {
    replicationLag: 1000,   // Alert if lag > 1 second
    errorRate: 0.01,        // Alert if error rate > 1%
    memoryUsage: 0.9        // Alert if memory > 90%
  }
});

// Handle alerts
monitor.on('alert', (alert) => {
  console.error('Database alert:', {
    type: alert.type,
    metric: alert.metric,
    value: alert.value,
    threshold: alert.threshold,
    timestamp: alert.timestamp
  });

  // Send to alerting system (PagerDuty, Slack, etc.)
  sendAlert(alert);
});

// Handle health status changes
monitor.on('status-change', (status) => {
  console.log('Health status changed:', status);
});

await monitor.start();
```

#### 1.5 Store Configuration in Memory

```typescript
await agentDB.memory.store('agentdb/infrastructure/config', {
  primary: {
    id: primaryDB.id,
    host: 'localhost',
    port: 5432,
    status: 'healthy'
  },
  replicas: replicas.map(r => ({
    id: r.id,
    host: 'localhost',
    port: r.port,
    status: r.status,
    syncLag: r.syncLag
  })),
  monitoring: {
    enabled: true,
    checkInterval: 5000,
    alertsConfigured: true
  },
  timestamp: Date.now()
});
```

### Validation Checklist

- [ ] Primary database initialized successfully
- [ ] Replicas connected and syncing
- [ ] Replication lag < 100ms
- [ ] Health monitor active and collecting metrics
- [ ] Configuration stored in memory
- [ ] Self-consistency test passed (insert on primary, verify on replicas)

## Phase 2: Configure Advanced Features

### Objectives
- Configure QUIC synchronization for optimal performance
- Implement multi-database router for load balancing
- Setup distributed coordination with leader election
- Configure failover policies for high availability

### Step-by-Step Process

#### 2.1 Configure QUIC Synchronization

```typescript
import { QUICSync } from '@agentdb/quic-sync';

const quicSync = new QUICSync({
  primary: primaryDB,
  replicas: replicas,
  config: {
    maxStreams: 100,              // Max concurrent streams
    idleTimeout: 30000,           // Idle timeout (ms)
    keepAlive: 5000,              // Keep-alive interval (ms)
    congestionControl: 'cubic',   // Congestion control algorithm
    prioritization: 'weighted-round-robin', // Stream prioritization
    flowControl: {
      initialWindow: 1048576,     // 1MB initial window
      maxWindow: 16777216         // 16MB max window
    }
  }
});

await quicSync.start();

// Monitor sync performance
quicSync.on('sync-complete', (stats) => {
  console.log('Sync completed:', {
    duration: stats.duration,
    vectorsSynced: stats.count,
    bytesTransferred: stats.bytes,
    throughput: stats.count / (stats.duration / 1000),
    avgLatency: stats.avgLatency
  });

  // Store stats for analysis
  agentDB.memory.store('agentdb/quic/sync-stats', stats);
});

quicSync.on('sync-error', (error) => {
  console.error('Sync error:', error);
  // Handle retry logic
});
```

#### 2.2 Implement Multi-Database Router

```typescript
import { MultiDBRouter } from '@agentdb/distributed';

const router = new MultiDBRouter({
  databases: [primaryDB, ...replicas],
  strategy: 'load-balanced',    // or 'nearest', 'round-robin', 'priority'
  healthCheck: {
    interval: 5000,             // Health check interval
    timeout: 1000,              // Health check timeout
    unhealthyThreshold: 3,      // Mark unhealthy after 3 failures
    healthyThreshold: 2         // Mark healthy after 2 successes
  },
  loadBalancing: {
    algorithm: 'least-connections',
    weights: {
      [primaryDB.id]: 1.0,      // Equal weight for all nodes
      [replica1.id]: 1.0,
      [replica2.id]: 1.0
    }
  }
});

await router.start();

// Query with automatic routing
const searchResults = await router.search({
  vector: queryVector,
  topK: 10,
  strategy: 'fan-out-merge',    // Query all, merge results
  timeout: 5000
});

console.log('Search completed via router:', {
  results: searchResults.length,
  nodeUsed: searchResults.metadata.node,
  latency: searchResults.metadata.latency
});
```

#### 2.3 Setup Distributed Coordination

```typescript
import { DistributedCoordinator } from '@agentdb/distributed';

const coordinator = new DistributedCoordinator({
  databases: [primaryDB, ...replicas],
  consensus: 'raft',            // Raft consensus algorithm
  leaderElection: true,         // Enable automatic leader election
  quorumSize: 2,                // Require quorum of 2 for writes
  electionTimeout: 3000,        // Election timeout (ms)
  heartbeatInterval: 1000       // Heartbeat interval (ms)
});

await coordinator.start();

// Handle leadership changes
coordinator.on('leader-elected', (leader) => {
  console.log('New leader elected:', {
    id: leader.id,
    term: leader.term,
    timestamp: Date.now()
  });

  // Update primary reference
  primaryDB = leader;

  // Notify monitoring system
  agentDB.memory.store('agentdb/coordination/leader', {
    id: leader.id,
    term: leader.term,
    elected: Date.now()
  });
});

coordinator.on('quorum-lost', () => {
  console.error('Quorum lost! Write operations disabled.');
  // Enter read-only mode
  router.setReadOnly(true);
});

coordinator.on('quorum-restored', () => {
  console.log('Quorum restored. Write operations enabled.');
  router.setReadOnly(false);
});
```

#### 2.4 Configure Failover Policies

```typescript
const failoverPolicy = {
  maxRetries: 3,                    // Max retry attempts
  retryDelay: 1000,                 // Initial retry delay (ms)
  retryBackoff: 'exponential',      // Backoff strategy
  fallbackStrategy: 'replica-promotion', // Promote replica to primary
  autoRecovery: true,               // Enable automatic recovery
  recoveryTimeout: 30000,           // Recovery timeout (30s)
  circuitBreaker: {
    enabled: true,
    failureThreshold: 5,            // Open circuit after 5 failures
    successThreshold: 2,            // Close circuit after 2 successes
    timeout: 60000                  // Circuit timeout (60s)
  }
};

router.setFailoverPolicy(failoverPolicy);

// Test failover
router.on('failover', (event) => {
  console.log('Failover executed:', {
    from: event.fromNode,
    to: event.toNode,
    reason: event.reason,
    duration: event.duration
  });
});
```

### Validation Checklist

- [ ] QUIC sync operational with < 100ms latency
- [ ] Router distributing queries across all healthy nodes
- [ ] Leader elected and consensus maintained
- [ ] Failover tested successfully
- [ ] Configuration stored in memory

## Phase 3: Implement Custom Distance Metrics

### Objectives
- Define custom metric interface for domain-specific similarity
- Implement weighted Euclidean distance
- Create hybrid metrics combining vector and scalar similarity
- Benchmark custom metrics against standard metrics

### Step-by-Step Process

#### 3.1 Define Custom Metric Interface

```typescript
import { DistanceMetric, Vector, Metadata } from 'agentdb-advanced';

interface CustomMetricConfig {
  name: string;
  description?: string;
  weightedDimensions?: number[];      // Dimension weights
  transformFunction?: (v: Vector) => Vector; // Vector transformation
  combineMetrics?: {
    metrics: string[];                 // Metrics to combine
    weights: number[];                 // Combination weights
  };
  normalize?: boolean;                 // Normalize output
  cacheResults?: boolean;              // Cache distance computations
}
```

#### 3.2 Implement Weighted Euclidean Distance

```typescript
const weightedEuclidean: DistanceMetric = {
  name: 'weighted-euclidean',
  description: 'Euclidean distance with per-dimension weights',

  compute: (a: Vector, b: Vector, config?: CustomMetricConfig): number => {
    const weights = config?.weightedDimensions || Array(a.length).fill(1.0);

    if (weights.length !== a.length) {
      throw new Error('Weight vector must match dimension count');
    }

    let sum = 0;
    for (let i = 0; i < a.length; i++) {
      const diff = a[i] - b[i];
      sum += weights[i] * diff * diff;
    }

    const distance = Math.sqrt(sum);

    return config?.normalize ? distance / Math.sqrt(a.length) : distance;
  },

  // Metric properties
  properties: {
    metric: true,           // Satisfies metric axioms
    symmetric: true,        // d(a,b) = d(b,a)
    nonNegative: true,      // d(a,b) >= 0
    triangleInequality: true // d(a,c) <= d(a,b) + d(b,c)
  }
};

// Register metric
primaryDB.registerMetric(weightedEuclidean);

// Use metric in search
const results = await primaryDB.search({
  vector: queryVector,
  topK: 10,
  metric: 'weighted-euclidean',
  metricConfig: {
    weightedDimensions: dimensionWeights,
    normalize: true
  }
});
```

#### 3.3 Create Hybrid Metric (Vector + Scalar)

```typescript
const hybridSimilarity: DistanceMetric = {
  name: 'hybrid-similarity',
  description: 'Combines vector similarity with scalar features',

  compute: (a: Vector, b: Vector, metadata?: Metadata): number => {
    // 1. Vector similarity (cosine)
    const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
    const magA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
    const magB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
    const cosineSim = dotProduct / (magA * magB);
    const vectorDist = 1 - cosineSim;

    // 2. Scalar similarity (optional metadata)
    let scalarDist = 0;
    if (metadata) {
      // Temporal similarity
      const timeDiff = Math.abs(
        (metadata.timestamp || 0) - Date.now()
      );
      const temporalSim = Math.exp(-timeDiff / (30 * 24 * 3600 * 1000)); // 30 day decay

      // Categorical similarity
      const categorySim = metadata.category === metadata.queryCategory ? 1 : 0;

      // Numeric feature similarity
      const numericSim = metadata.score ?
        1 - Math.abs(metadata.score - (metadata.queryScore || 0)) : 0;

      // Combine scalar features
      scalarDist = 1 - (0.5 * temporalSim + 0.3 * categorySim + 0.2 * numericSim);
    }

    // 3. Weighted combination (70% vector, 30% scalar)
    const alpha = 0.7;
    return alpha * vectorDist + (1 - alpha) * scalarDist;
  },

  properties: {
    metric: false,          // May not satisfy triangle inequality
    symmetric: true,
    nonNegative: true,
    triangleInequality: false
  }
};

primaryDB.registerMetric(hybridSimilarity);
```

#### 3.4 Implement Domain-Specific Metrics

```typescript
// Example: Code similarity metric
const codeSimilarity: DistanceMetric = {
  name: 'code-similarity',
  description: 'Specialized metric for code similarity search',

  compute: (a: Vector, b: Vector, metadata?: Metadata): number => {
    // Vector component (embedding similarity)
    const vectorDist = cosineDistance(a, b);

    // Syntactic similarity (AST-based)
    const syntaxSim = metadata?.ast_similarity || 0;

    // Semantic similarity (execution-based)
    const semanticSim = metadata?.semantic_similarity || 0;

    // Lexical similarity (token-based)
    const lexicalSim = metadata?.lexical_similarity || 0;

    // Weighted combination optimized for code search
    return (
      0.4 * vectorDist +
      0.3 * (1 - syntaxSim) +
      0.2 * (1 - semanticSim) +
      0.1 * (1 - lexicalSim)
    );
  }
};

primaryDB.registerMetric(codeSimilarity);
```

#### 3.5 Benchmark Custom Metrics

```typescript
async function benchmarkMetrics() {
  const testVectors = generateTestVectors(1000, 1536);
  const groundTruth = generateGroundTruth(testVectors);
  const queryVector = testVectors[0];

  const metrics = [
    'cosine',
    'euclidean',
    'weighted-euclidean',
    'hybrid-similarity',
    'code-similarity'
  ];

  const results: Record<string, any> = {};

  for (const metric of metrics) {
    console.log(`Benchmarking ${metric}...`);

    // Measure latency
    const latencies: number[] = [];
    for (let i = 0; i < 100; i++) {
      const start = performance.now();
      await primaryDB.search({
        vector: queryVector,
        topK: 10,
        metric: metric
      });
      latencies.push(performance.now() - start);
    }

    // Measure accuracy
    const searchResults = await primaryDB.search({
      vector: queryVector,
      topK: 100,
      metric: metric
    });

    const accuracy = calculateAccuracy(searchResults, groundTruth);
    const recall = calculateRecall(searchResults, groundTruth, 10);
    const precision = calculatePrecision(searchResults, groundTruth, 10);

    results[metric] = {
      latency: {
        mean: latencies.reduce((a, b) => a + b) / latencies.length,
        p50: percentile(latencies, 0.5),
        p95: percentile(latencies, 0.95),
        p99: percentile(latencies, 0.99)
      },
      accuracy: {
        overall: accuracy,
        recall: recall,
        precision: precision,
        f1: 2 * (precision * recall) / (precision + recall)
      }
    };
  }

  // Store benchmark results
  await agentDB.memory.store('agentdb/metrics/benchmark', {
    results,
    testSetSize: 1000,
    timestamp: Date.now()
  });

  return results;
}

const benchmark = await benchmarkMetrics();
console.log('Benchmark results:', benchmark);
```

### Validation Checklist

- [ ] Custom metrics registered successfully
- [ ] Metrics produce valid distances (non-negative)
- [ ] Metrics tested for symmetry
- [ ] Benchmark completed for all metrics
- [ ] Best metric identified for use case
- [ ] Results stored in memory

## Phase 4: Optimize Performance

### Objectives
- Configure HNSW indexing for 150x faster search
- Implement query caching for common queries
- Enable quantization for 4-32x memory reduction
- Execute batch operations for improved throughput
- Run comprehensive performance benchmarks

### Step-by-Step Process

#### 4.1 Configure HNSW Indexing

```typescript
// Create HNSW index on primary
await primaryDB.createIndex({
  type: 'hnsw',
  params: {
    M: 16,                    // Connections per layer (trade-off: accuracy vs memory)
    efConstruction: 200,      // Construction-time accuracy parameter
    efSearch: 100,            // Search-time accuracy parameter
    maxElements: 1000000,     // Maximum number of elements
    randomSeed: 42            // Seed for reproducibility
  },
  async: true,                // Build index asynchronously
  progress: (percent) => {
    console.log(`Index building: ${percent}%`);
  }
});

// Wait for index completion
await primaryDB.waitForIndex();

// Sync index to replicas
await Promise.all(
  replicas.map(r => r.syncIndex(primaryDB))
);

console.log('HNSW index built and synced');
```

#### 4.2 Implement Query Caching

```typescript
import { QueryCache } from '@agentdb/optimization';

const cache = new QueryCache({
  maxSize: 10000,             // Max cache entries
  ttl: 3600000,               // 1 hour TTL
  strategy: 'lru',            // Least Recently Used eviction
  hashFunction: 'xxhash64',   // Fast hashing
  compression: 'snappy',      // Compress cached results
  sharding: {
    enabled: true,
    shards: 4                 // Shard cache across 4 partitions
  }
});

primaryDB.setCache(cache);

// Cache monitoring
cache.on('hit', (key, entry) => {
  console.log('Cache hit:', {
    key: key.substring(0, 16),
    age: Date.now() - entry.timestamp,
    size: entry.size
  });
});

cache.on('miss', (key) => {
  console.log('Cache miss:', key.substring(0, 16));
});

cache.on('evict', (key, reason) => {
  console.log('Cache eviction:', { key, reason });
});

// Get cache statistics
setInterval(() => {
  const stats = cache.getStats();
  console.log('Cache stats:', {
    hitRate: stats.hits / (stats.hits + stats.misses),
    size: stats.size,
    evictions: stats.evictions
  });

  agentDB.memory.store('agentdb/cache/stats', stats);
}, 60000); // Every minute
```

#### 4.3 Enable Quantization

```typescript
import { Quantization } from '@agentdb/optimization';

// Configure product quantization
const quantizer = new Quantization({
  method: 'product-quantization',
  codebookSize: 256,          // 8-bit quantization
  subvectors: 8,              // Split vector into 8 subvectors
  compressionRatio: 4,        // Target 4x compression
  training: {
    sampleSize: 100000,       // Training samples
    iterations: 100,          // K-means iterations
    convergenceThreshold: 0.0001
  }
});

// Train quantizer on existing data
console.log('Training quantizer...');
await quantizer.train(primaryDB);

// Apply quantization
console.log('Applying quantization...');
await primaryDB.applyQuantization(quantizer);

// Verify accuracy after quantization
const accuracyTest = await benchmarkAccuracy(primaryDB, testQueries, {
  metrics: ['recall@10', 'recall@100', 'mrr'],
  groundTruth: groundTruthResults
});

console.log('Post-quantization accuracy:', accuracyTest);

// If accuracy acceptable, sync to replicas
if (accuracyTest.recall@10 >= 0.95) {
  await Promise.all(
    replicas.map(r => r.applyQuantization(quantizer))
  );
  console.log('Quantization applied to all replicas');
} else {
  console.warn('Accuracy degradation too high, rolling back');
  await primaryDB.removeQuantization();
}
```

#### 4.4 Batch Operations

```typescript
import { BatchProcessor } from '@agentdb/optimization';

const batchProcessor = new BatchProcessor({
  batchSize: 1000,            // Vectors per batch
  flushInterval: 5000,        // Auto-flush every 5 seconds
  parallelBatches: 4,         // Process 4 batches in parallel
  bufferSize: 10000,          // Internal buffer size
  errorHandling: 'retry',     // Retry failed operations
  maxRetries: 3
});

// Batch inserts
console.log('Batch inserting vectors...');
const vectors = generateVectors(100000, 1536);
const insertStart = performance.now();

await batchProcessor.insertBatch(primaryDB, vectors, {
  onProgress: (processed, total) => {
    console.log(`Progress: ${processed}/${total} (${(processed/total*100).toFixed(1)}%)`);
  },
  onError: (error, batch) => {
    console.error('Batch error:', error, 'Batch:', batch);
  }
});

const insertDuration = performance.now() - insertStart;
const throughput = vectors.length / (insertDuration / 1000);
console.log(`Insert throughput: ${throughput.toFixed(0)} vectors/sec`);

// Batch searches
console.log('Batch searching...');
const queries = generateQueries(1000);
const searchStart = performance.now();

const results = await batchProcessor.searchBatch(primaryDB, queries, {
  topK: 10,
  parallel: true,
  maxConcurrency: 10
});

const searchDuration = performance.now() - searchStart;
console.log(`Search throughput: ${(queries.length / (searchDuration / 1000)).toFixed(0)} queries/sec`);
```

#### 4.5 Comprehensive Performance Benchmarking

```typescript
async function comprehensiveBenchmark() {
  console.log('Running comprehensive performance benchmark...');

  const benchmark = {
    insertThroughput: 0,
    searchLatency: {},
    searchThroughput: 0,
    memoryUsage: {},
    cacheHitRate: 0,
    indexPerformance: {}
  };

  // 1. Insert throughput
  console.log('Benchmarking insert throughput...');
  const insertVectors = generateVectors(10000, 1536);
  const insertStart = performance.now();
  await batchProcessor.insertBatch(primaryDB, insertVectors);
  const insertDuration = performance.now() - insertStart;
  benchmark.insertThroughput = insertVectors.length / (insertDuration / 1000);

  // 2. Search latency (p50, p95, p99)
  console.log('Benchmarking search latency...');
  const latencies: number[] = [];
  for (let i = 0; i < 1000; i++) {
    const query = generateQuery();
    const start = performance.now();
    await primaryDB.search({ vector: query, topK: 10 });
    latencies.push(performance.now() - start);
  }
  latencies.sort((a, b) => a - b);
  benchmark.searchLatency = {
    p50: latencies[Math.floor(latencies.length * 0.5)],
    p95: latencies[Math.floor(latencies.length * 0.95)],
    p99: latencies[Math.floor(latencies.length * 0.99)],
    mean: latencies.reduce((a, b) => a + b) / latencies.length
  };

  // 3. Search throughput
  console.log('Benchmarking search throughput...');
  const searchQueries = generateQueries(1000);
  const searchStart = performance.now();
  await batchProcessor.searchBatch(primaryDB, searchQueries, {
    topK: 10,
    parallel: true
  });
  const searchDuration = performance.now() - searchStart;
  benchmark.searchThroughput = searchQueries.length / (searchDuration / 1000);

  // 4. Memory usage
  console.log('Analyzing memory usage...');
  const memStats = await primaryDB.getMemoryUsage();
  benchmark.memoryUsage = {
    total: memStats.total,
    vectors: memStats.vectors,
    index: memStats.index,
    cache: memStats.cache,
    compressionRatio: memStats.compressionRatio
  };

  // 5. Cache hit rate
  const cacheStats = cache.getStats();
  benchmark.cacheHitRate = cacheStats.hits / (cacheStats.hits + cacheStats.misses);

  // 6. Index performance
  console.log('Benchmarking index performance...');
  const noIndexLatency = await benchmarkWithoutIndex(primaryDB);
  const withIndexLatency = benchmark.searchLatency.mean;
  benchmark.indexPerformance = {
    withoutIndex: noIndexLatency,
    withIndex: withIndexLatency,
    speedup: noIndexLatency / withIndexLatency
  };

  // Store results
  await agentDB.memory.store('agentdb/optimization/benchmark', {
    benchmark,
    timestamp: Date.now(),
    configuration: {
      indexType: 'hnsw',
      cacheEnabled: true,
      quantizationEnabled: true,
      batchingEnabled: true
    }
  });

  console.log('Benchmark complete:', benchmark);
  return benchmark;
}

const perfResults = await comprehensiveBenchmark();
```

### Validation Checklist

- [ ] HNSW index built and synced to all replicas
- [ ] Cache operational with hit rate > 70%
- [ ] Quantization maintains accuracy > 95%
- [ ] Batch operations functional
- [ ] Performance targets met:
  - Search latency P95 < 10ms
  - Insert throughput > 50,000 vectors/sec
  - Memory compression ratio > 4x
  - Index speedup > 150x

## Phase 5: Deploy and Monitor

### Objectives
- Deploy production cluster with high availability
- Implement comprehensive monitoring and alerting
- Configure backup and disaster recovery
- Create operational runbook
- Validate production readiness

### Step-by-Step Process

#### 5.1 Production Deployment Configuration

```typescript
// production.config.ts
export const productionConfig = {
  cluster: {
    primary: {
      host: process.env.PRIMARY_HOST || 'primary.agentdb.internal',
      port: parseInt(process.env.PRIMARY_PORT || '5432'),
      replicas: 2,
      region: 'us-east-1'
    },
    replicas: [
      {
        host: process.env.REPLICA1_HOST || 'replica1.agentdb.internal',
        port: parseInt(process.env.REPLICA1_PORT || '5432'),
        region: 'us-east-1'
      },
      {
        host: process.env.REPLICA2_HOST || 'replica2.agentdb.internal',
        port: parseInt(process.env.REPLICA2_PORT || '5432'),
        region: 'us-west-2'  // Cross-region for DR
      }
    ]
  },
  monitoring: {
    enabled: true,
    exporters: ['prometheus', 'cloudwatch', 'datadog'],
    scrapeInterval: 15,  // seconds
    alerts: {
      replicationLag: 1000,      // ms
      errorRate: 0.01,           // 1%
      latencyP95: 50,            // ms
      memoryUsage: 0.9,          // 90%
      diskUsage: 0.85            // 85%
    }
  },
  backup: {
    enabled: true,
    schedule: '0 * * * *',       // Hourly
    retention: 168,              // 7 days (hours)
    location: 's3://agentdb-backups/production',
    encryption: 'AES256'
  },
  security: {
    tls: {
      enabled: true,
      certPath: '/etc/agentdb/certs/server.crt',
      keyPath: '/etc/agentdb/certs/server.key'
    },
    authentication: 'mtls',      // Mutual TLS
    encryption: 'aes-256-gcm'
  }
};

// Deploy cluster
await deployCluster(productionConfig);
```

#### 5.2 Monitoring and Observability

```typescript
import { MetricsExporter } from '@agentdb/monitoring';
import prometheus from 'prom-client';

// Initialize metrics registry
const register = new prometheus.Registry();

// Define custom metrics
const searchLatency = new prometheus.Histogram({
  name: 'agentdb_search_latency_seconds',
  help: 'Search query latency in seconds',
  labelNames: ['metric', 'topk'],
  buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
});

const insertThroughput = new prometheus.Counter({
  name: 'agentdb_inserts_total',
  help: 'Total number of vectors inserted',
  labelNames: ['database']
});

const replicationLag = new prometheus.Gauge({
  name: 'agentdb_replication_lag_ms',
  help: 'Replication lag in milliseconds',
  labelNames: ['replica']
});

register.registerMetric(searchLatency);
register.registerMetric(insertThroughput);
register.registerMetric(replicationLag);

// Create exporter
const exporter = new MetricsExporter({
  exporters: [
    {
      type: 'prometheus',
      port: 9090,
      path: '/metrics',
      register: register
    },
    {
      type: 'cloudwatch',
      namespace: 'AgentDB/Production',
      region: 'us-east-1',
      dimensions: {
        Environment: 'production',
        Service: 'agentdb'
      }
    }
  ]
});

await exporter.start();

// Instrument database operations
primaryDB.on('search', (query, result, latency) => {
  searchLatency.observe(
    { metric: query.metric, topk: query.topK },
    latency / 1000
  );
});

primaryDB.on('insert', (vector, database) => {
  insertThroughput.inc({ database: database.id });
});

quicSync.on('sync-complete', (stats) => {
  replicas.forEach(replica => {
    replicationLag.set(
      { replica: replica.id },
      replica.syncLag
    );
  });
});

console.log('Monitoring configured and active');
```

#### 5.3 Alerting Configuration

```typescript
import { AlertManager } from '@agentdb/monitoring';

const alertManager = new AlertManager({
  channels: [
    {
      type: 'email',
      config: {
        recipients: ['ops@company.com', 'oncall@company.com'],
        smtp: {
          host: process.env.SMTP_HOST,
          port: 587,
          auth: {
            user: process.env.SMTP_USER,
            pass: process.env.SMTP_PASS
          }
        }
      }
    },
    {
      type: 'slack',
      config: {
        webhook: process.env.SLACK_WEBHOOK,
        channel: '#agentdb-alerts',
        username: 'AgentDB Alert Bot'
      }
    },
    {
      type: 'pagerduty',
      config: {
        apiKey: process.env.PAGERDUTY_KEY,
        serviceKey: process.env.PAGERDUTY_SERVICE
      }
    }
  ],
  rules: [
    {
      name: 'high-replication-lag',
      metric: 'agentdb_replication_lag_ms',
      condition: '> 1000',
      duration: '5m',           // Alert if condition true for 5 minutes
      severity: 'critical',
      message: 'Replication lag exceeds 1 second',
      actions: ['email', 'slack', 'pagerduty']
    },
    {
      name: 'high-search-latency',
      metric: 'agentdb_search_latency_p95',
      condition: '> 0.05',      // 50ms
      duration: '10m',
      severity: 'warning',
      message: 'Search latency P95 exceeds 50ms',
      actions: ['slack']
    },
    {
      name: 'high-error-rate',
      metric: 'agentdb_error_rate',
      condition: '> 0.01',      // 1%
      duration: '2m',
      severity: 'critical',
      message: 'Error rate exceeds 1%',
      actions: ['email', 'slack', 'pagerduty']
    },
    {
      name: 'low-cache-hit-rate',
      metric: 'agentdb_cache_hit_rate',
      condition: '< 0.5',       // 50%
      duration: '15m',
      severity: 'warning',
      message: 'Cache hit rate below 50%',
      actions: ['slack']
    },
    {
      name: 'high-memory-usage',
      metric: 'agentdb_memory_usage_ratio',
      condition: '> 0.9',       // 90%
      duration: '5m',
      severity: 'warning',
      message: 'Memory usage exceeds 90%',
      actions: ['slack']
    }
  ]
});

await alertManager.start();

// Test alerts
await alertManager.test('slack');
console.log('Alerting configured and tested');
```

#### 5.4 Health Checks and Readiness Probes

```typescript
import express from 'express';

const healthApp = express();

// Liveness probe
healthApp.get('/health', async (req, res) => {
  try {
    // Basic health check
    const health = {
      status: 'healthy',
      timestamp: Date.now(),
      uptime: process.uptime(),
      databases: await Promise.all([
        primaryDB.healthCheck(),
        ...replicas.map(r => r.healthCheck())
      ]),
      quic: {
        active: quicSync.isHealthy(),
        streams: quicSync.activeStreams
      },
      coordinator: {
        status: coordinator.getStatus(),
        leader: coordinator.getLeader()
      }
    };

    const allHealthy = health.databases.every(db => db.status === 'healthy');

    res.status(allHealthy ? 200 : 503).json(health);
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});

// Readiness probe
healthApp.get('/ready', async (req, res) => {
  try {
    const checks = {
      database: await primaryDB.isReady(),
      replicas: await Promise.all(replicas.map(r => r.isReady())),
      quic: quicSync.isReady(),
      index: await primaryDB.isIndexReady(),
      cache: cache.isReady()
    };

    const ready = Object.values(checks).every(c =>
      Array.isArray(c) ? c.every(Boolean) : c
    );

    res.status(ready ? 200 : 503).json({
      ready,
      checks,
      timestamp: Date.now()
    });
  } catch (error) {
    res.status(503).json({
      ready: false,
      error: error.message
    });
  }
});

// Metrics endpoint
healthApp.get('/metrics', async (req, res) => {
  const metrics = await register.metrics();
  res.set('Content-Type', register.contentType);
  res.send(metrics);
});

// Start health check server
healthApp.listen(8080, () => {
  console.log('Health check server listening on port 8080');
});
```

#### 5.5 Operational Runbook

```typescript
const runbook = {
  deployment: {
    title: 'Production Deployment Procedure',
    steps: [
      {
        step: 1,
        action: 'Verify configuration',
        commands: [
          'cat production.config.ts',
          'env | grep AGENTDB'
        ],
        validation: 'All environment variables set correctly'
      },
      {
        step: 2,
        action: 'Deploy primary database',
        commands: [
          'npm run deploy:primary',
          'curl http://primary:8080/health'
        ],
        validation: 'Primary returns HTTP 200'
      },
      {
        step: 3,
        action: 'Deploy replicas with QUIC sync',
        commands: [
          'npm run deploy:replicas',
          'curl http://replica1:8080/health',
          'curl http://replica2:8080/health'
        ],
        validation: 'All replicas return HTTP 200'
      },
      {
        step: 4,
        action: 'Verify replication lag',
        commands: [
          'curl http://primary:9090/metrics | grep replication_lag'
        ],
        validation: 'Replication lag < 100ms'
      },
      {
        step: 5,
        action: 'Enable monitoring and alerting',
        commands: [
          'npm run start:monitoring',
          'curl http://monitoring:9090/metrics'
        ],
        validation: 'Metrics exporting successfully'
      },
      {
        step: 6,
        action: 'Run smoke tests',
        commands: [
          'npm run test:smoke'
        ],
        validation: 'All smoke tests pass'
      },
      {
        step: 7,
        action: 'Gradually increase traffic',
        commands: [
          'kubectl scale deployment agentdb-api --replicas=3',
          'watch curl http://primary:9090/metrics | grep qps'
        ],
        validation: 'QPS increases smoothly without errors'
      }
    ]
  },

  troubleshooting: {
    'high-replication-lag': {
      symptoms: [
        'Replication lag > 1 second',
        'Alert: high-replication-lag firing'
      ],
      diagnosis: [
        'Check network connectivity: ping replica1',
        'Check QUIC streams: curl http://primary:9090/metrics | grep quic_streams',
        'Check primary load: curl http://primary:9090/metrics | grep qps'
      ],
      remediation: [
        'Increase QUIC maxStreams: update config and restart',
        'Check for network congestion: iperf primary replica1',
        'Consider adding more replicas to distribute load'
      ],
      prevention: [
        'Monitor replication lag proactively',
        'Set up capacity planning alerts',
        'Regular load testing'
      ]
    },

    'slow-search-queries': {
      symptoms: [
        'Search latency P95 > 50ms',
        'Alert: high-search-latency firing'
      ],
      diagnosis: [
        'Check if HNSW index is built: curl /health',
        'Check cache hit rate: curl /metrics | grep cache_hit_rate',
        'Review query patterns: check logs for complex queries'
      ],
      remediation: [
        'Rebuild HNSW index if corrupted',
        'Increase cache size if hit rate < 50%',
        'Adjust efSearch parameter for accuracy/speed trade-off',
        'Consider query optimization or filtering'
      ],
      prevention: [
        'Regular index maintenance',
        'Monitor cache performance',
        'Query analysis and optimization'
      ]
    },

    'leader-election-failure': {
      symptoms: [
        'No leader elected',
        'Write operations failing',
        'Coordinator status: no-quorum'
      ],
      diagnosis: [
        'Check coordinator logs: kubectl logs pod/coordinator',
        'Verify quorum availability: at least 2/3 nodes healthy',
        'Check for network partitions: ping all nodes'
      ],
      remediation: [
        'Manually trigger election: curl -X POST /coordinator/elect',
        'Restart coordinator if stuck: kubectl restart pod/coordinator',
        'Fix network partition if present'
      ],
      prevention: [
        'Monitor coordinator health continuously',
        'Use cross-region deployment for resilience',
        'Regular failover testing'
      ]
    }
  },

  backup: {
    schedule: 'Hourly incremental, daily full',
    retention: '7 days',
    location: 's3://agentdb-backups/production',

    create: {
      steps: [
        'Trigger backup: npm run backup:create',
        'Wait for completion: npm run backup:status',
        'Verify backup: npm run backup:verify [backup-id]',
        'Upload to S3: npm run backup:upload [backup-id]'
      ]
    },

    restore: {
      steps: [
        '1. Stop affected database instance',
        '2. Download backup: aws s3 cp s3://agentdb-backups/[backup-id] .',
        '3. Restore data directory: tar -xzf [backup-id].tar.gz -C /var/lib/agentdb',
        '4. Start database with recovery flag: agentdb start --recovery',
        '5. Verify data integrity: npm run verify:data',
        '6. Rejoin cluster: curl -X POST /coordinator/join'
      ]
    }
  },

  scaling: {
    'scale-up': {
      trigger: 'QPS sustained > 80% capacity for 10 minutes',
      steps: [
        'Add new replica: npm run replica:add',
        'Wait for sync: check replication lag < 100ms',
        'Add to router: curl -X POST /router/add-node',
        'Verify load distribution: check metrics'
      ]
    },

    'scale-down': {
      trigger: 'QPS sustained < 40% capacity for 30 minutes',
      steps: [
        'Remove replica from router: curl -X DELETE /router/remove-node/[id]',
        'Wait for connection drain: 30 seconds',
        'Stop replica: npm run replica:stop [id]',
        'Verify remaining nodes healthy'
      ]
    }
  }
};

// Store runbook in memory
await agentDB.memory.store('agentdb/production/runbook', runbook);

console.log('Operational runbook created and stored');
```

### Validation Checklist

- [ ] Production cluster deployed successfully
- [ ] All health checks returning HTTP 200
- [ ] Monitoring active and exporting metrics to Prometheus/CloudWatch
- [ ] Alerts configured and tested (test alerts sent)
- [ ] Backup schedule configured and first backup completed
- [ ] Runbook documented and stored in memory
- [ ] Smoke tests passed
- [ ] Production readiness validated (all checks pass)

## Complete Integration Example

```typescript
// complete-advanced-agentdb.ts
import { setupAdvancedAgentDB } from './setup';
import { generateTestData } from './utils';

async function completeImplementation() {
  console.log('Starting complete Advanced AgentDB implementation...');

  // Phase 1: Infrastructure
  console.log('\nPhase 1: Setting up infrastructure...');
  const { primary, replicas, router, coordinator, quicSync } =
    await setupAdvancedAgentDB({
      dimensions: 1536,
      replicaCount: 2,
      enableQUIC: true,
      enableMonitoring: true
    });

  // Phase 2: Advanced Features
  console.log('\nPhase 2: Configuring advanced features...');
  await quicSync.start();
  await coordinator.start();
  await router.start();

  // Phase 3: Custom Metrics
  console.log('\nPhase 3: Implementing custom metrics...');
  primary.registerMetric(weightedEuclidean);
  primary.registerMetric(hybridSimilarity);
  primary.registerMetric(codeSimilarity);

  const metricBenchmark = await benchmarkMetrics();
  console.log('Metric benchmark:', metricBenchmark);

  // Phase 4: Optimization
  console.log('\nPhase 4: Optimizing performance...');
  await primary.createIndex({ type: 'hnsw', params: { M: 16, efConstruction: 200 }});
  await primary.setCache(new QueryCache({ maxSize: 10000, ttl: 3600000 }));
  await primary.applyQuantization(new Quantization({ compressionRatio: 4 }));

  const perfBenchmark = await comprehensiveBenchmark();
  console.log('Performance benchmark:', perfBenchmark);

  // Phase 5: Production Deployment
  console.log('\nPhase 5: Deploying to production...');
  await deployProduction(productionConfig);
  await startMonitoring();
  await configureAlerts();

  // Final validation
  console.log('\nRunning final validation...');
  const validation = await validateProductionReadiness();
  console.log('Production readiness:', validation);

  if (validation.readiness) {
    console.log('\n✓ Advanced AgentDB implementation complete!');
    console.log('Cluster:', {
      primary: primary.id,
      replicas: replicas.map(r => r.id),
      leader: coordinator.getLeader(),
      healthy: validation.checks.deployment
    });
  } else {
    console.error('\n✗ Production readiness check failed');
    console.error('Failed checks:',
      Object.entries(validation.checks)
        .filter(([_, pass]) => !pass)
        .map(([check]) => check)
    );
  }
}

completeImplementation().catch(console.error);
```

## Success Metrics Summary

At the end of the 5-phase process, you should achieve:

1. **Infrastructure**
   - Primary + 2 replicas deployed and syncing
   - Replication lag < 100ms
   - Health monitoring active

2. **Advanced Features**
   - QUIC synchronization operational
   - Multi-database routing functional
   - Distributed coordination with leader election
   - Failover tested and working

3. **Custom Metrics**
   - 3+ custom metrics implemented and registered
   - Metrics validated (non-negative, symmetric)
   - Benchmark shows 15-30% accuracy improvement
   - Best metric identified for domain

4. **Performance**
   - HNSW index providing 150x speedup
   - Cache hit rate > 70%
   - Quantization achieving 4x compression
   - Search latency P95 < 10ms
   - Insert throughput > 50,000 vectors/sec

5. **Production**
   - Monitoring exporting metrics to Prometheus/CloudWatch
   - Alerts configured and tested
   - Health checks passing (HTTP 200)
   - Backup schedule active
   - Runbook documented
   - Production readiness validated

## Additional Resources

- Full skill documentation: `SKILL.md`
- Quick start guide: `README.md`
- Process diagram: `process-diagram.gv`
- AgentDB Advanced Docs: https://agentdb.dev/docs/advanced
- QUIC Sync Guide: https://agentdb.dev/docs/quic
- Production Best Practices: https://agentdb.dev/docs/production
