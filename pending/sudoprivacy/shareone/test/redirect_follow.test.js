#!/usr/bin/env node

// Regression test for shareone_client.requestBuffer redirect handling.
// The skill repo has no test runner, so this is a self-contained node script:
//   node test/redirect_follow.test.js   -> exit 0 on pass, 1 on failure.
//
// Guards the fix for: a bare DELETE that infra 301-redirects (http->https /
// trailing slash) used to surface as `HTTP 301` because the client never
// followed redirects. It must now follow, preserve the method + body, keep the
// API key on same-host hops, and drop it across hosts.

const assert = require('assert');
const http = require('http');
const { requestBuffer } = require('../scripts/shareone_client');

function startServer(handler) {
    return new Promise((resolve) => {
        const server = http.createServer(handler);
        server.listen(0, '127.0.0.1', () => resolve(server));
    });
}

function readBody(req) {
    return new Promise((resolve) => {
        const chunks = [];
        req.on('data', (c) => chunks.push(c));
        req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    });
}

async function main() {
    // Case 1: same-host 301 on DELETE -> follow, preserve method + body + key.
    let finalHit = null;
    const server = await startServer(async (req, res) => {
        if (req.url === '/api/v1/pages/x') {
            res.writeHead(301, { Location: '/api/v1/pages/x-final' });
            res.end();
            return;
        }
        if (req.url === '/api/v1/pages/x-final') {
            finalHit = {
                method: req.method,
                apiKey: req.headers['x-api-key'] || null,
                body: await readBody(req),
            };
            res.writeHead(204);
            res.end();
            return;
        }
        res.writeHead(404);
        res.end();
    });
    const port = server.address().port;
    const res = await requestBuffer(`http://127.0.0.1:${port}/api/v1/pages/x`, {
        method: 'DELETE',
        headers: { 'X-API-Key': 'secret-key', 'Content-Length': Buffer.byteLength('{"k":1}') },
    }, '{"k":1}');
    assert.strictEqual(res.statusCode, 204, 'should follow 301 through to 204');
    assert.ok(finalHit, 'redirect target should be hit');
    assert.strictEqual(finalHit.method, 'DELETE', 'method preserved across 301');
    assert.strictEqual(finalHit.apiKey, 'secret-key', 'api key forwarded on same host');
    assert.strictEqual(finalHit.body, '{"k":1}', 'body re-sent across redirect');
    server.close();

    // Case 2: cross-host redirect -> follow but strip the credential header.
    let crossHit = null;
    const other = await startServer((req, res) => {
        crossHit = { method: req.method, apiKey: req.headers['x-api-key'] || null };
        res.writeHead(204);
        res.end();
    });
    const otherPort = other.address().port;
    const redirector = await startServer((req, res) => {
        res.writeHead(302, { Location: `http://127.0.0.1:${otherPort}/elsewhere` });
        res.end();
    });
    const rPort = redirector.address().port;
    const res2 = await requestBuffer(`http://127.0.0.1:${rPort}/start`, {
        method: 'DELETE',
        headers: { 'X-API-Key': 'secret-key' },
    });
    assert.strictEqual(res2.statusCode, 204);
    assert.ok(crossHit, 'cross-host target should be hit');
    assert.strictEqual(crossHit.method, 'DELETE', 'method preserved cross-host');
    assert.strictEqual(crossHit.apiKey, null, 'api key stripped on cross-host redirect');
    redirector.close();
    other.close();

    // Case 3: redirect loop is bounded (errors, does not hang).
    const loop = await startServer((req, res) => {
        res.writeHead(301, { Location: '/loop' });
        res.end();
    });
    const lPort = loop.address().port;
    let looped = false;
    try {
        await requestBuffer(`http://127.0.0.1:${lPort}/loop`, { method: 'GET' });
    } catch (_) {
        looped = true;
    }
    assert.ok(looped, 'redirect loop should terminate with an error, not hang');
    loop.close();

    console.log('PASS: redirect-follow (same-host key kept, cross-host key stripped, body re-sent, loop bounded)');
}

main().catch((error) => {
    console.error('FAIL:', error && error.message);
    process.exit(1);
});
