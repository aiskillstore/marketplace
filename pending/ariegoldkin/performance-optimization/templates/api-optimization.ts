/**
 * API Performance Optimization Patterns
 */

import express, { Request, Response, NextFunction } from 'express';
import compression from 'compression';
import crypto from 'crypto';

const app = express();

// =============================================
// COMPRESSION MIDDLEWARE
// =============================================

app.use(compression({
  level: 6, // Compression level (0-9)
  threshold: 1024, // Only compress responses > 1KB
  filter: (req: Request, res: Response) => {
    // Don't compress already compressed formats
    if (req.headers['x-no-compression']) return false;
    return compression.filter(req, res);
  }
}));

// =============================================
// ETAG AND CONDITIONAL REQUESTS
// =============================================

function generateETag(data: unknown): string {
  return crypto
    .createHash('md5')
    .update(JSON.stringify(data))
    .digest('hex');
}

app.get('/api/data/:id', async (req: Request, res: Response) => {
  const data = { id: req.params.id, value: 'example' }; // getData(req.params.id)
  const etag = generateETag(data);

  // Return 304 if content hasn't changed
  if (req.headers['if-none-match'] === etag) {
    return res.status(304).end();
  }

  res.set('ETag', etag);
  res.set('Cache-Control', 'private, max-age=0, must-revalidate');
  res.json(data);
});

// =============================================
// FIELD SELECTION
// =============================================

interface SelectableFields {
  [key: string]: unknown;
}

async function selectFields<T extends SelectableFields>(
  data: T,
  fields: string[]
): Promise<Partial<T>> {
  if (fields.includes('*')) return data;

  const result: Partial<T> = {};
  for (const field of fields) {
    if (field in data) {
      result[field as keyof T] = data[field as keyof T];
    }
  }
  return result;
}

// GET /api/users/123?fields=id,name,email
app.get('/api/users/:id', async (req: Request, res: Response) => {
  const fields = (req.query.fields as string)?.split(',') || ['*'];
  const user = { id: req.params.id, name: 'John', email: 'john@example.com', createdAt: new Date() };
  const result = await selectFields(user, fields);
  res.json(result);
});

// =============================================
// CURSOR-BASED PAGINATION
// =============================================

interface PaginatedResponse<T> {
  data: T[];
  pageInfo: {
    hasNextPage: boolean;
    hasPreviousPage: boolean;
    startCursor: string;
    endCursor: string;
  };
}

// Usage: GET /api/users?first=20&after=cursor123
app.get('/api/users', async (req: Request, res: Response) => {
  const first = parseInt(req.query.first as string) || 20;
  const after = req.query.after as string;

  // Implementation would fetch from database with cursor
  const response: PaginatedResponse<{ id: string; name: string }> = {
    data: [],
    pageInfo: {
      hasNextPage: false,
      hasPreviousPage: !!after,
      startCursor: '',
      endCursor: '',
    }
  };

  res.json(response);
});

export { app };
