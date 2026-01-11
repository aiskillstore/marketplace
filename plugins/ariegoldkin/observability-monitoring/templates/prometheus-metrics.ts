/**
 * Prometheus Metrics Configuration
 */

import { Registry, Counter, Histogram, Gauge, collectDefaultMetrics } from 'prom-client';
import { Request, Response, NextFunction, Router } from 'express';

// =============================================
// REGISTRY SETUP
// =============================================

export const registry = new Registry();

// Collect default Node.js metrics
collectDefaultMetrics({ register: registry });

// =============================================
// HTTP METRICS
// =============================================

export const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
  registers: [registry],
});

export const httpRequestTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [registry],
});

// =============================================
// BUSINESS METRICS
// =============================================

export const orderTotal = new Counter({
  name: 'orders_total',
  help: 'Total number of orders',
  labelNames: ['status', 'payment_method'],
  registers: [registry],
});

export const orderAmount = new Histogram({
  name: 'order_amount_dollars',
  help: 'Order amounts in dollars',
  buckets: [10, 50, 100, 500, 1000, 5000],
  registers: [registry],
});

// =============================================
// DATABASE METRICS
// =============================================

export const dbQueryDuration = new Histogram({
  name: 'db_query_duration_seconds',
  help: 'Database query duration',
  labelNames: ['query_type', 'table'],
  buckets: [0.001, 0.01, 0.05, 0.1, 0.5, 1],
  registers: [registry],
});

export const dbConnectionPool = new Gauge({
  name: 'db_connection_pool_size',
  help: 'Database connection pool metrics',
  labelNames: ['state'],
  registers: [registry],
});

// =============================================
// CACHE METRICS
// =============================================

export const cacheHits = new Counter({
  name: 'cache_hits_total',
  help: 'Total cache hits',
  labelNames: ['cache_name'],
  registers: [registry],
});

export const cacheMisses = new Counter({
  name: 'cache_misses_total',
  help: 'Total cache misses',
  labelNames: ['cache_name'],
  registers: [registry],
});

// =============================================
// MIDDLEWARE
// =============================================

export function metricsMiddleware(req: Request, res: Response, next: NextFunction) {
  const startTime = Date.now();
  const route = req.route?.path || req.path;

  res.on('finish', () => {
    const duration = (Date.now() - startTime) / 1000;
    const labels = {
      method: req.method,
      route,
      status_code: res.statusCode.toString(),
    };

    httpRequestDuration.observe(labels, duration);
    httpRequestTotal.inc(labels);
  });

  next();
}

// =============================================
// METRICS ENDPOINT
// =============================================

const router = Router();

router.get('/metrics', async (_req, res) => {
  res.set('Content-Type', registry.contentType);
  res.end(await registry.metrics());
});

export const metricsRouter = router;
