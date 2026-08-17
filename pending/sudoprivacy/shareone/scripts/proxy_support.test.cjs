// Live test for the shareone_client proxy support (skill issue #13).
// Mock CONNECT proxy + self-signed TLS origin + http proxy + bypass cases.
const { requestBuffer } = require('./shareone_client.js');
const net = require('net'), tls = require('tls'), http = require('http');
const { execSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'soproxy-'));
execSync(`openssl req -x509 -newkey rsa:2048 -keyout "${dir}/key.pem" -out "${dir}/cert.pem" -days 1 -nodes -subj "/CN=example.test"`, { stdio: 'ignore' });
const key = fs.readFileSync(path.join(dir, 'key.pem'));
const cert = fs.readFileSync(path.join(dir, 'cert.pem'));

const connects = [];       // CONNECT targets the tunnel proxy saw
const httpProxyPaths = []; // absolute URIs the http proxy saw

const tlsOrigin = () => new Promise(res => {
  const s = tls.createServer({ key, cert }, sock => {
    sock.on('data', () => sock.write('HTTP/1.1 200 OK\r\nContent-Length: 11\r\nConnection: close\r\n\r\n{"ok":true}'));
  });
  s.listen(0, '127.0.0.1', () => res({ server: s, port: s.address().port }));
});
const connectProxy = originPort => new Promise(res => {
  const s = http.createServer();
  s.on('connect', (req, clientSock) => {
    connects.push(req.url);
    const up = net.connect(originPort, '127.0.0.1', () => {
      clientSock.write('HTTP/1.1 200 Connection Established\r\n\r\n');
      up.pipe(clientSock); clientSock.pipe(up);
    });
    up.on('error', () => clientSock.destroy());
  });
  s.listen(0, '127.0.0.1', () => res({ server: s, port: s.address().port }));
});
const httpOrigin = () => new Promise(res => {
  const s = http.createServer((req, r) => { r.writeHead(200); r.end(JSON.stringify({ ok: true, url: req.url })); });
  s.listen(0, '127.0.0.1', () => res({ server: s, port: s.address().port }));
});
const httpProxy = originPort => new Promise(res => {
  const s = http.createServer((req, r) => {
    httpProxyPaths.push(req.url);
    const u = new URL(req.url);
    const up = http.request({ hostname: '127.0.0.1', port: originPort, path: u.pathname + u.search, method: req.method }, ur => { r.writeHead(ur.statusCode, ur.headers); ur.pipe(r); });
    up.on('error', e => { r.writeHead(502); r.end(String(e)); });
    req.pipe(up);
  });
  s.listen(0, '127.0.0.1', () => res({ server: s, port: s.address().port }));
});

function clearProxyEnv() { ['HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy', 'NO_PROXY', 'no_proxy'].forEach(k => delete process.env[k]); }

(async () => {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
  const to = await tlsOrigin(), cp = await connectProxy(to.port), ho = await httpOrigin(), hp = await httpProxy(ho.port);
  let fails = 0;
  const ok = (name, cond, extra = '') => { console.log(`${cond ? 'PASS' : 'FAIL'}: ${name}${extra ? '  ' + extra : ''}`); if (!cond) fails++; };

  // (a) HTTPS routed through the proxy via CONNECT
  clearProxyEnv(); connects.length = 0;
  process.env.HTTPS_PROXY = `http://127.0.0.1:${cp.port}`;
  try {
    const r = await requestBuffer('https://example.test/ping');
    ok('HTTPS via CONNECT tunnel', r.statusCode === 200 && r.text.includes('"ok":true') && connects.includes('example.test:443'), `connects=${JSON.stringify(connects)}`);
  } catch (e) { ok('HTTPS via CONNECT tunnel', false, e.message); }

  // (b) NO_PROXY → direct (proxy untouched, DNS fails)
  clearProxyEnv(); connects.length = 0;
  process.env.HTTPS_PROXY = `http://127.0.0.1:${cp.port}`;
  process.env.NO_PROXY = 'example.test';
  try { await requestBuffer('https://example.test/ping', { timeoutMs: 4000 }); ok('NO_PROXY bypass', false, 'unexpected success'); }
  catch (e) { ok('NO_PROXY bypass (direct, proxy untouched)', connects.length === 0, `err=${e.code || e.message}`); }

  // (c) localhost → direct (proxy untouched)
  clearProxyEnv(); httpProxyPaths.length = 0;
  process.env.HTTP_PROXY = `http://127.0.0.1:${hp.port}`;
  try {
    const r = await requestBuffer(`http://127.0.0.1:${ho.port}/local`);
    ok('localhost bypass (direct, proxy untouched)', r.statusCode === 200 && httpProxyPaths.length === 0);
  } catch (e) { ok('localhost bypass', false, e.message); }

  // (d) plain-HTTP proxied via absolute-URI
  clearProxyEnv(); httpProxyPaths.length = 0;
  process.env.HTTP_PROXY = `http://127.0.0.1:${hp.port}`;
  try {
    const r = await requestBuffer('http://example.test/abs');
    ok('HTTP via absolute-URI proxy', r.statusCode === 200 && httpProxyPaths.some(p => p.startsWith('http://example.test/')), `paths=${JSON.stringify(httpProxyPaths)}`);
  } catch (e) { ok('HTTP via absolute-URI proxy', false, e.message); }

  [to, cp, ho, hp].forEach(x => x.server.close());
  console.log(fails === 0 ? 'ALL PROXY TESTS PASSED' : `${fails} FAILED`);
  process.exit(fails === 0 ? 0 : 1);
})();
