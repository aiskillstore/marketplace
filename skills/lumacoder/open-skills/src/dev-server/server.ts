import * as http from 'node:http';
import * as path from 'node:path';
import { readFile, pathExists } from '../core/fs-utils.js';
import { handleApi } from './api.js';

const WEB_DIR = path.join(process.cwd(), 'src', 'dev-server', 'web');

const MIME_TYPES: Record<string, string> = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

async function serveStatic(req: http.IncomingMessage, res: http.ServerResponse): Promise<boolean> {
  const url = new URL(req.url || '/', `http://${req.headers.host}`);
  let pathname = url.pathname;
  if (pathname === '/') pathname = '/index.html';

  const filePath = path.join(WEB_DIR, pathname);
  if (!filePath.startsWith(WEB_DIR)) return false;

  if (!(await pathExists(filePath))) return false;

  const ext = path.extname(filePath);
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  const content = await readFile(filePath);
  res.writeHead(200, { 'Content-Type': contentType });
  res.end(content);
  return true;
}

export function startDevServer(port = 3890): Promise<void> {
  return new Promise((resolve) => {
    const server = http.createServer(async (req, res) => {
      try {
        const handled = await handleApi(req, res);
        if (handled) return;

        const served = await serveStatic(req, res);
        if (!served) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('Not Found');
        }
      } catch (err: any) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message || 'Internal error' }));
      }
    });

    server.listen(port, () => {
      console.log(`Developer server running at http://localhost:${port}`);
      resolve();
    });
  });
}
