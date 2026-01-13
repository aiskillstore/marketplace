/**
 * Structured Logging Setup with Winston
 */

import winston from 'winston';
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

// =============================================
// LOGGER CONFIGURATION
// =============================================

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: process.env.SERVICE_NAME || 'app',
    environment: process.env.NODE_ENV,
    version: process.env.APP_VERSION,
  },
  transports: [
    new winston.transports.Console({
      format: process.env.NODE_ENV === 'development'
        ? winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        : winston.format.json()
    }),
    // Add file transport for production
    ...(process.env.NODE_ENV === 'production'
      ? [new winston.transports.File({ filename: 'logs/error.log', level: 'error' })]
      : [])
  ],
});

// Add request context
export function createRequestLogger(requestId: string, userId?: string) {
  return logger.child({
    requestId,
    userId,
  });
}

// =============================================
// REQUEST LOGGING MIDDLEWARE
// =============================================

// Extend Express Request type
declare global {
  namespace Express {
    interface Request {
      logger: winston.Logger;
      requestId: string;
    }
  }
}

export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const requestId = req.headers['x-request-id'] as string || uuidv4();
  const startTime = Date.now();

  // Attach logger to request
  req.logger = logger.child({ requestId });
  req.requestId = requestId;

  // Log request
  req.logger.info('Request started', {
    method: req.method,
    path: req.path,
    query: req.query,
    userAgent: req.headers['user-agent'],
    ip: req.ip,
  });

  // Log response
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const logData = {
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration_ms: duration,
    };

    if (res.statusCode >= 500) {
      req.logger.error('Request failed', logData);
    } else if (res.statusCode >= 400) {
      req.logger.warn('Request client error', logData);
    } else {
      req.logger.info('Request completed', logData);
    }
  });

  next();
}

// =============================================
// LOGGING EXAMPLES
// =============================================

// Good: Structured with context
function logExampleGood() {
  logger.info('User action completed', {
    action: 'purchase',
    userId: 'user-123',
    orderId: 'order-456',
    amount: 99.99,
    duration_ms: 150,
  });
}

// Bad: Unstructured string interpolation
function logExampleBad() {
  // Don't do this:
  // logger.info(`User user-123 completed purchase of $99.99`);
}

// Good: Error with context
function logErrorGood(err: Error, userId: string, orderId: string) {
  logger.error('Payment processing failed', {
    error: err.message,
    stack: err.stack,
    userId,
    orderId,
    paymentMethod: 'credit_card',
    retryAttempt: 1,
  });
}

export default logger;
export { logExampleGood, logExampleBad, logErrorGood };
