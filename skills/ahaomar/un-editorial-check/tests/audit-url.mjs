// The --url contract, exercised against a loopback server only: retrieval,
// content-type gating, error-status refusal, the size cap, the scheme cap and
// the audits-stay-local boundary. No request leaves 127.0.0.1.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import http from 'node:http';
import { fileURLToPath } from 'node:url';

import { run } from '../bin/check.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-url-'));
const configPath = path.join(tmp, 'config.json');
fs.writeFileSync(configPath, '{}');

const PAGE = `<!doctype html>
<html><head><title>Field office update</title></head>
<body><p>The organization met on March 5, 2026 in Burma.</p></body></html>`; // ue:ignore UE-TE005  (deliberate served copy)

// A loopback server whose behaviour each test chooses through the path.
const server = http.createServer((req, res) => {
  if (req.url === '/page') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(PAGE);
  } else if (req.url === '/plain') {
    res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' });
    res.end('The organization reports quarterly.');
  } else if (req.url === '/json') {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end('{"a":1}');
  } else if (req.url === '/missing') {
    res.writeHead(404, { 'content-type': 'text/plain' });
    res.end('not found');
  } else if (req.url === '/redirect') {
    res.writeHead(302, { location: '/page' });
    res.end();
  } else if (req.url === '/huge') {
    res.writeHead(200, { 'content-type': 'text/html' });
    const chunk = '<p>x</p>'.repeat(1024); // ~4 KiB
    let written = 0;
    const pump = () => {
      while (written < 6 * 1024 * 1024) {
        written += chunk.length;
        if (!res.write(chunk)) { res.once('drain', pump); return; }
      }
      res.end();
    };
    pump();
  } else {
    res.writeHead(500).end();
  }
});
let base = '';
await new Promise((resolve) => server.listen(0, '127.0.0.1', () => {
  base = `http://127.0.0.1:${server.address().port}`;
  resolve();
}));

const capture = async (argv) => {
  const out = [];
  const err = [];
  const args = argv.includes('--config') ? argv : [...argv, '--config', configPath];
  // --url runs asynchronously; the promise resolves to the same exit code.
  const code = await run(args, { log: l => out.push(String(l)), error: l => err.push(String(l)) });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};
const json = (result) => {
  try { return JSON.parse(result.stdout); }
  catch { return assert.fail(`stdout is not JSON:\n${result.stdout}\n${result.stderr}`); }
};

// --- 1. an HTML page is retrieved and checked under its URL ------------------

{
  const result = await capture(['--url', `${base}/page`, '--format', 'json']);
  // The country-name finding is error severity, so the run exits 1 by design.
  assert.equal(result.code, 1, result.stderr);
  const parsed = json(result);
  assert.equal(parsed.files, 1);
  const names = [...new Set(parsed.findings.map(f => f.file))];
  assert.deepEqual(names, [`${base}/page`], 'the finding names the URL');
  const byRule = new Set(parsed.findings.map(f => f.ruleId));
  for (const id of ['UE-SP001', 'UE-NU001', 'UE-TE005']) {
    assert(byRule.has(id), `the page copy must run the rules, missing ${id}`);
  }
  console.log('ok — url: an HTML page is retrieved and checked under its URL');
}

// --- 2. plain text and redirects ----------------------------------------------

{
  const plain = await capture(['--url', `${base}/plain`, '--format', 'json']);
  assert.equal(plain.code, 0, plain.stderr);
  assert(json(plain).findings.some(f => f.ruleId === 'UE-SP001'),
    'a text/plain body is checked as prose');

  const redirect = await capture(['--url', `${base}/redirect`, '--format', 'json']);
  assert.equal(redirect.code, 1, redirect.stderr);
  assert(json(redirect).findings.length > 0, 'a redirect is followed to the page');
  console.log('ok — url: plain text is checked as prose; redirects are followed');
}

// --- 3. refusals: status, content type, size, scheme --------------------------

{
  const missing = await capture(['--url', `${base}/missing`]);
  assert.equal(missing.code, 2, 'an error status must refuse');
  assert.match(missing.stderr, /HTTP 404|STATUS/, missing.stderr);

  const jsonBody = await capture(['--url', `${base}/json`]);
  assert.equal(jsonBody.code, 2, 'a non-text content type must refuse');
  assert.match(jsonBody.stderr, /content type|CONTENT_TYPE/i, jsonBody.stderr);

  const huge = await capture(['--url', `${base}/huge`]);
  assert.equal(huge.code, 2, 'an oversized body must refuse');
  assert.match(huge.stderr, /exceeds|TOO_LARGE/i, huge.stderr);

  const ftp = await capture(['--url', 'ftp://example.test/file']);
  assert.equal(ftp.code, 2, 'a non-http scheme must refuse before any request');
  assert.match(ftp.stderr, /http and https/, ftp.stderr);

  for (const result of [missing, jsonBody, huge]) {
    assert.doesNotMatch(result.stdout, /No findings under/,
      'a refusal never prints the clean sentence');
  }
  console.log('ok — url: status, content type, size and scheme refusals all refuse');
}

// --- 4. audits stay local ------------------------------------------------------

{
  const result = await capture(['--url', `${base}/page`, '--profile', 'publishing', '--format', 'json']);
  assert.equal(result.code, 1, result.stderr);
  const parsed = json(result);
  assert(!parsed.findings.some(f => f.audit),
    'audit findings must not be produced for URL records');
  console.log('ok — url: audits stay local');
}

server.close();
fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — url: retrieval, gating and refusals proven against a loopback server');
