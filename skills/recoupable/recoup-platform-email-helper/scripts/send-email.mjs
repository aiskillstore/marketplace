#!/usr/bin/env node
// recoup-platform-email-helper — send an email via the Recoup API.
//
// Node-only (the task sandbox runs the `node22` runtime; `python3` is NOT
// guaranteed). Zero dependencies — uses Node 22's global `fetch`. The whole
// point is to take JSON serialization of large HTML bodies OUT of the model's
// hands (hand-rolled `curl … -d "{… $(jq …) …}"` is what produced empty
// "Message from Recoup" footer-only emails). Build the body from a file, let
// `JSON.stringify` escape it, and fail LOUDLY instead of pretending success.
//
// Usage:
//   node send-email.mjs --subject "..." --html-file /tmp/report.html [--to a@b.com]
//   node send-email.mjs --subject "..." --text "plain body" --to a@b.com --cc c@d.com
//   node send-email.mjs ... --dry-run     # print the payload + target, do not send
//
// Flags:
//   --subject <s>            email subject (optional; API derives from body if omitted)
//   --html <s> | --html-file <path>
//   --text <s> | --text-file <path>
//   --to <email>             repeatable; omit to default to the account's own email
//   --cc <email>             repeatable
//   --chat-id <id>           room id for the footer link
//   --dry-run                serialize + validate, print, do not POST
//
// Env: RECOUP_API_KEY or RECOUP_ACCESS_TOKEN (required unless --dry-run);
//      RECOUP_API_BASE (default https://api.recoupable.dev)

import { readFileSync } from "node:fs";

function parseArgs(argv) {
  const out = { to: [], cc: [] };
  for (let i = 0; i < argv.length; i++) {
    let a = argv[i];
    if (!a.startsWith("--")) continue;
    let key = a.slice(2);
    let val;
    const eq = key.indexOf("=");
    if (eq !== -1) {
      val = key.slice(eq + 1);
      key = key.slice(0, eq);
    } else if (key === "dry-run") {
      out.dryRun = true;
      continue;
    } else {
      val = argv[++i];
    }
    switch (key) {
      case "subject": out.subject = val; break;
      case "html": out.html = val; break;
      case "html-file": out.html = readFileSync(val, "utf8"); break;
      case "text": out.text = val; break;
      case "text-file": out.text = readFileSync(val, "utf8"); break;
      case "to": if (val) out.to.push(val); break;
      case "cc": if (val) out.cc.push(val); break;
      case "chat-id": out.chatId = val; break;
      case "dry-run": out.dryRun = true; break;
      default: fail(`unknown flag --${key}`);
    }
  }
  return out;
}

function fail(msg, code = 2) {
  process.stderr.write(`recoup-email: ${msg}\n`);
  process.exit(code);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  // The guard that matters: never "send" an empty email.
  const hasBody = Boolean((args.html && args.html.trim()) || (args.text && args.text.trim()));
  if (!hasBody) fail("refusing to send: a non-empty --html/--html-file or --text/--text-file is required");

  const payload = {};
  if (args.to.length) payload.to = args.to;
  if (args.cc.length) payload.cc = args.cc;
  if (args.subject) payload.subject = args.subject;
  if (args.text != null) payload.text = args.text;
  if (args.html != null) payload.html = args.html;
  if (args.chatId) payload.chat_id = args.chatId;

  const base = process.env.RECOUP_API_BASE || "https://api.recoupable.dev";
  const url = `${base}/api/emails`;
  const body = JSON.stringify(payload);

  if (args.dryRun) {
    process.stdout.write(`DRY RUN → POST ${url}\n${body}\n`);
    process.exit(0);
  }

  const key = process.env.RECOUP_API_KEY || process.env.RECOUP_ACCESS_TOKEN;
  if (!key) fail("missing RECOUP_API_KEY / RECOUP_ACCESS_TOKEN in env");

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  let res;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
      body,
      signal: controller.signal,
    });
  } catch (e) {
    fail(`request failed: ${e?.message || e}`, 1);
  } finally {
    clearTimeout(timeout);
  }

  const text = await res.text();
  if (!res.ok) fail(`API ${res.status}: ${text.slice(0, 500)}`, 1);

  let id;
  try { id = JSON.parse(text)?.id; } catch {}
  process.stdout.write(`sent${id ? ` (id ${id})` : ""}: ${text.slice(0, 300)}\n`);
  process.exit(0);
}

main();
