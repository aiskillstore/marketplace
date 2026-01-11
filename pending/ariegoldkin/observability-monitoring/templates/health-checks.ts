/**
 * Health Check Endpoints
 */

import { Router, Request, Response } from 'express';

const router = Router();

// Mock dependencies - replace with actual imports
const pool = { query: async (_sql: string) => ({ rows: [] }) };
const redis = { ping: async () => 'PONG' };

// =============================================
// HEALTH STATUS TYPES
// =============================================

interface HealthCheck {
  status: 'pass' | 'fail';
  latency_ms?: number;
  error?: string;
}

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: Record<string, HealthCheck>;
  version: string;
  uptime: number;
}

// =============================================
// LIVENESS PROBE
// =============================================

// Is the app running?
router.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok' });
});

// =============================================
// READINESS PROBE
// =============================================

// Is the app ready to serve traffic?
router.get('/ready', async (_req: Request, res: Response) => {
  const health: HealthStatus = {
    status: 'healthy',
    checks: {},
    version: process.env.APP_VERSION || '1.0.0',
    uptime: process.uptime(),
  };

  // Check database
  try {
    const start = Date.now();
    await pool.query('SELECT 1');
    health.checks.database = {
      status: 'pass',
      latency_ms: Date.now() - start,
    };
  } catch (error) {
    health.checks.database = {
      status: 'fail',
      error: (error as Error).message,
    };
    health.status = 'unhealthy';
  }

  // Check Redis
  try {
    const start = Date.now();
    await redis.ping();
    health.checks.redis = {
      status: 'pass',
      latency_ms: Date.now() - start,
    };
  } catch (error) {
    health.checks.redis = {
      status: 'fail',
      error: (error as Error).message,
    };
    // Redis failure degrades but doesn't make unhealthy
    if (health.status === 'healthy') {
      health.status = 'degraded';
    }
  }

  const statusCode = health.status === 'healthy' ? 200 :
                     health.status === 'degraded' ? 200 : 503;

  res.status(statusCode).json(health);
});

// =============================================
// STARTUP PROBE (for slow-starting apps)
// =============================================

let isReady = false;

export function setReady(ready: boolean) {
  isReady = ready;
}

router.get('/startup', (_req: Request, res: Response) => {
  if (isReady) {
    res.json({ status: 'ready' });
  } else {
    res.status(503).json({ status: 'starting' });
  }
});

export default router;
