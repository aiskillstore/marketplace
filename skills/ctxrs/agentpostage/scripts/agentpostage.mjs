#!/usr/bin/env node
import { open } from 'node:fs/promises';
import { constants } from 'node:fs';
import { parseArgs } from 'node:util';
import { randomUUID } from 'node:crypto';

const services = ['first_class', 'certified_return_receipt', 'certified', 'first_class_flat', 'first_class_hse'];
const papers = ['white', 'yellow', 'blue', 'green', 'orange', 'red', 'ivory', 'perforated', 'statement', 'check_blue', 'check_red', 'check_green', 'coupon'];
const envelopes = ['none', 'right_window', 'left_window', 'small', 'coupon_pack'];
const help = `AgentPostage — mail a PDF to a US address (Node.js 22+)

Usage:
  agentpostage send --pdf letter.pdf --sender sender.json --recipient recipient.json
                   [--service ${services.join('|')}]
                   [--color black|color] [--duplex true|false]
                   [--paper ${papers.join('|')}]
                   [--return-envelope ${envelopes.join('|')}]
                   [--idempotency-key VALUE]
  agentpostage price --pages N [--service VALUE] [--color black|color]
                    [--duplex true|false] [--paper VALUE] [--return-envelope VALUE]
  agentpostage balance
  agentpostage list [--limit 1-50] [--cursor VALUE]
  agentpostage get ID
  agentpostage cancel ID
  agentpostage transactions [--limit 1-50] [--cursor VALUE]
  agentpostage billing
  agentpostage --help

Environment:
  AGENTPOSTAGE_API_KEY   Required agent key; never saved by this CLI.
  AGENTPOSTAGE_BASE_URL  Default https://agentpostage.com; HTTP only on loopback.

Address JSON: {"name":"Test Person","address_line1":"123 Example St",
"city":"Boston","state":"MA","postal_code":"02110","country":"US"}
Optional address_line2 is supported. PDF limit: 10 MiB; API validates contents.
Print defaults: black, simplex (duplex=false), white paper, no return envelope.
An address coversheet is always included.
price reads a retail price without sending a PDF or mail; no funds required.
Sending queues mailing directly. A generated Idempotency-Key is printed to
stderr BEFORE the request; reuse it with identical inputs after an uncertain
result. Results are JSON on stdout. billing returns the owner's billing link.
`;

class CliError extends Error {}
function check(condition, message) { if (!condition) throw new CliError(message); }
async function readFileBounded(path, max, label) {
  check(typeof path === 'string' && path.length > 0, `Supply --${label}.`);
  let file;
  try {
    file = await open(path, constants.O_RDONLY | constants.O_NONBLOCK);
    const stat = await file.stat();
    check(stat.isFile() && stat.size > 0 && stat.size <= max, `${label} must be a nonempty regular file of at most ${max} bytes.`);
    // Bound the read too, in case the file grows after stat.
    const chunks = []; let size = 0;
    while (size <= max) {
      const buffer = Buffer.alloc(Math.min(64 * 1024, max + 1 - size));
      const { bytesRead } = await file.read(buffer);
      if (!bytesRead) break;
      chunks.push(buffer.subarray(0, bytesRead)); size += bytesRead;
    }
    check(size > 0 && size <= max, `${label} must be a nonempty file of at most ${max} bytes.`);
    return Buffer.concat(chunks, size);
  } catch (error) {
    if (error instanceof CliError) throw error;
    throw new CliError(`Could not read --${label}; check the file path and permissions.`);
  } finally { await file?.close(); }
}
async function addressFile(path, label) {
  const bytes = await readFileBounded(path, 64 * 1024, label);
  let value;
  try { value = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)); }
  catch { throw new CliError(`--${label} must contain a valid JSON address object.`); }
  check(value && typeof value === 'object' && !Array.isArray(value), `--${label} must contain a JSON address object.`);
  return value;
}
async function responseJson(response) {
  const reader = response.body?.getReader();
  check(reader, `API returned an empty response (HTTP ${response.status}).`);
  const chunks = []; let size = 0;
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 1024 * 1024) { await reader.cancel(); throw new CliError('API response exceeds 1 MiB.'); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  let value;
  try { value = JSON.parse(Buffer.concat(chunks, size).toString('utf8')); }
  catch { throw new CliError(`API returned invalid JSON (HTTP ${response.status}).`); }
  check(value && typeof value === 'object' && !Array.isArray(value), `API returned invalid JSON (HTTP ${response.status}).`);
  return value;
}
async function main() {
  let parsed;
  try {
    parsed = parseArgs({ allowPositionals: true, options: Object.fromEntries([
      ['help', { type: 'boolean', short: 'h' }],
      ...['pdf', 'sender', 'recipient', 'service', 'color', 'duplex', 'paper', 'return-envelope', 'pages', 'idempotency-key', 'limit', 'cursor'].map(key => [key, { type: 'string' }]),
    ]) });
  } catch { throw new CliError('Invalid arguments. Run with --help for usage.'); }
  const { values, positionals } = parsed;
  if (values.help || !positionals.length && !Object.keys(values).length) { process.stdout.write(help); return; }
  const [command, id, ...extra] = positionals;
  const allowed = {
    send: ['pdf', 'sender', 'recipient', 'service', 'color', 'duplex', 'paper', 'return-envelope', 'idempotency-key'],
    price: ['pages', 'service', 'color', 'duplex', 'paper', 'return-envelope'],
    balance: [], list: ['limit', 'cursor'], get: [], cancel: [], transactions: ['limit', 'cursor'], billing: [],
  };
  check(Object.hasOwn(allowed, command), 'Unknown command. Run with --help for usage.');
  check(Object.keys(values).every(key => allowed[command].includes(key)), 'Unsupported option for this command. Run with --help.');
  check(extra.length === 0 && (['get', 'cancel'].includes(command) ? !!id : id === undefined), 'Unexpected or missing positional arguments. Run with --help.');
  if (id) check(/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(id), 'ID must be a UUID.');
  const key = process.env.AGENTPOSTAGE_API_KEY;
  check(key && /^[\x21-\x7e]+$/.test(key), 'Set AGENTPOSTAGE_API_KEY to your agent key.');
  let base;
  try { base = new URL(process.env.AGENTPOSTAGE_BASE_URL ?? 'https://agentpostage.com'); }
  catch { throw new CliError('AGENTPOSTAGE_BASE_URL must be a valid HTTPS URL.'); }
  check(!base.username && !base.password && !base.search && !base.hash && base.pathname === '/' &&
    (base.protocol === 'https:' || base.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(base.hostname)),
  'AGENTPOSTAGE_BASE_URL must be an HTTPS origin (HTTP is allowed only on loopback).');
  const headers = { Authorization: `Bearer ${key}`, Accept: 'application/json' };
  let method = 'GET', body, path;
  switch (command) {
    case 'send':
    case 'price': {
      const service = values.service ?? 'first_class';
      check(services.includes(service), `Service must be ${services.join(', ')}.`);
      check(values.color === undefined || ['black', 'color'].includes(values.color), 'Color must be black or color.');
      check(values.duplex === undefined || ['true', 'false'].includes(values.duplex), 'Duplex must be true or false.');
      check(values.paper === undefined || papers.includes(values.paper), `Paper must be ${papers.join(', ')}.`);
      check(values['return-envelope'] === undefined || envelopes.includes(values['return-envelope']), `Return envelope must be ${envelopes.join(', ')}.`);
      const print = { service, color: values.color, duplex: values.duplex === undefined ? undefined : values.duplex === 'true',
        paper: values.paper, return_envelope: values['return-envelope'] };
      if (command === 'price') {
        check(typeof values.pages === 'string' && /^[1-9][0-9]{0,2}$/.test(values.pages) && Number(values.pages) <= 500, 'Supply --pages as an integer from 1 to 500.');
        body = JSON.stringify({ page_count: Number(values.pages), ...print });
        headers['Content-Type'] = 'application/json'; method = 'POST'; path = '/v1/price'; break;
      }
      const idem = values['idempotency-key'] ?? randomUUID();
      check(/^[A-Za-z0-9._:-]{8,128}$/.test(idem), 'Idempotency key must be 8–128 ASCII letters, digits, dots, colons, underscores or hyphens.');
      const pdf = await readFileBounded(values.pdf, 10 * 1024 * 1024, 'pdf');
      const sender = await addressFile(values.sender, 'sender'), recipient = await addressFile(values.recipient, 'recipient');
      body = JSON.stringify({ pdf_base64: pdf.toString('base64'), sender, recipient, ...print });
      headers['Content-Type'] = 'application/json'; headers['Idempotency-Key'] = idem;
      method = 'POST'; path = '/v1/letters';
      await new Promise((resolve, reject) => process.stderr.write(`Idempotency-Key: ${idem}\n`, error => error ? reject(error) : resolve()));
      break;
    }
    case 'get': path = `/v1/letters/${id}`; break;
    case 'cancel': path = `/v1/letters/${id}/cancel`; method = 'POST'; break;
    case 'balance': path = '/v1/balance'; break;
    case 'billing': path = '/v1/billing/link'; break;
    case 'list':
    case 'transactions': {
      const query = new URLSearchParams();
      if (values.limit !== undefined) {
        check(/^\d{1,2}$/.test(values.limit) && Number(values.limit) >= 1 && Number(values.limit) <= 50, 'Limit must be 1–50.');
        query.set('limit', values.limit);
      }
      if (values.cursor !== undefined) {
        check(values.cursor.length > 0 && values.cursor.length <= 1024, 'Cursor must contain 1–1024 characters.');
        query.set('cursor', values.cursor);
      }
      path = `/v1/${command === 'list' ? 'letters' : 'transactions'}?${query}`;
      break;
    }
  }
  let response, result;
  try {
    response = await fetch(new URL(path, base), { method, headers, body, redirect: 'error', signal: AbortSignal.timeout(60_000) });
    result = await responseJson(response);
  } catch (error) {
    if (error instanceof CliError) throw error;
    throw new CliError('Request failed or timed out. Check connectivity; retry sends with the same Idempotency-Key and identical inputs.');
  }
  if (!response.ok || result.error !== undefined) {
    const error = result.error;
    const detail = error && typeof error.message === 'string' ? error.message : 'Request could not be completed.';
    const code = error && typeof error.code === 'string' ? error.code : 'api_error';
    const next = error && typeof error.next_action === 'string' ? ` ${error.next_action}` : '';
    // Redact before truncation so a boundary cannot expose part of the key.
    const safe = (value, max) => value.split(key).join('[redacted]').slice(0, max);
    throw new CliError(`HTTP ${response.status} ${safe(code, 100)}: ${safe(detail, 1024)}${safe(next, 1024)}`);
  }
  process.stdout.write(JSON.stringify(result) + '\n');
}
main().catch(error => {
  let message = error instanceof CliError ? error.message : 'Command failed. Run with --help for usage.';
  const key = process.env.AGENTPOSTAGE_API_KEY;
  if (key) message = message.split(key).join('[redacted]');
  process.stderr.write(JSON.stringify({ error: { message } }) + '\n');
  process.exitCode = 1;
});
