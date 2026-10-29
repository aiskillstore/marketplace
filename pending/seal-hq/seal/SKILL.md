---
name: seal
description: >-
  Move large files and secrets between people and agents without them passing
  through the chat, the model context or logs. Use when you must give the user
  a file too big for chat (exports, dumps, builds, videos, archives) or a
  credential you generated; when the user must give you a large file or a
  secret (API key, token, password, .env) — never ask them to paste it into
  chat; or when another agent must receive a file only it can open.
---

# SEAL

SEAL is how agents and people hand each other large files and secrets without
the content passing through the chat, the model or the SEAL server. Files are
encrypted on the sending machine; the key of a plain link travels in its
fragment after `#`, which no server sees, and a link sent to an address has no
fragment: its key is wrapped to that address and kept by the server. No
account, no API key. A seal is free up to a limit.

Two ways to call it; use whichever this environment has:

- **MCP tools** `seal_share`, `seal_request`, `seal_pair`, `seal_open`,
  `seal_inbox`, `seal_run`, `seal_list`, `seal_revoke` (server `sealnet-mcp`,
  started with `npx -y sealnet-mcp@latest`).
- **CLI** `seal` (`curl -fsSL https://seal.net/install.sh | sh`). Pass `--json`:
  stdout is then one JSON object, progress and messages go to stderr.

## Pick the path

| Situation | MCP | CLI |
|---|---|---|
| Connect to the user's SEAL inbox, once | `seal_pair` → show the link and the three words; after it files go to their inbox | `seal pair --json` |
| Give the user a large file, folder, dump or build | `seal_share path=<abs path>` — into the user's inbox once connected, else the link goes to their clipboard or a 0600 file; you get a handle; never read or print that file | `seal send <path> --to owner --json` once paired, else `seal send <path> --ttl 1d --json` and give the user `share_url` |
| Give the user a secret you created (password, key, `.env`) | write it to a 0600 file, `seal_share path=<file>` | `seal send <file> --kind secret --json` |
| You need a secret or a file from the user | `seal_request what="Brave API key" kind=secret where_url=<page where it is created>` → path of a 0600 file | `seal request --what "Brave API key" --kind secret --where <url> --wait --json` → `files[0].path` |
| Pass a file to another agent | `seal_share path=<file> mode=forward to=<its address>` → a link only that agent opens, also in its inbox | `seal send <file> --to <address> --json` |
| Files another agent or a person sent to your address | `seal_inbox wait=60`, then `seal_open item=<in_…> mode=file` | `seal inbox --wait 60 --json`, then `seal inbox open <id> --json` |
| You received a SEAL link | `seal_open url=<link> mode=file` → path | `seal receive <link> --output <dir> --json` → path |
| A program needs a secret from a link or your inbox | `seal_run command=[<program>, <args>] secrets=[{url=<link>, name=API_KEY}]` (or `item=<in_…>`) → its output with the value replaced | `seal run --seal <link>=API_KEY --redact -- <program> <args>` (or `--item <id>=API_KEY`) |
| Someone must be able to send to you | `sealnet-mcp pubkey` prints your address | `seal keygen` |
| Stop a link | `seal_revoke handle=<h_…>` | `seal revoke <seal id>` |

`seal_open mode=metadata` (the default) shows name, size and expiry without
using up a read.

## Rules

1. Never ask the user to paste a secret or upload a file into the chat. Call
   `seal_request` / `seal request`: they answer on a seal.net page — on their
   computer it opens in their browser by itself, elsewhere they get its link
   or a card in their inbox. Pass `where_url` (the exact page where that key
   is created) so they find it in one click.
2. Never print a secret: no `cat`, no `echo $KEY`, no reading the file into
   the conversation. A result with `"secret": true` is a path you pass to the
   program that needs it (a `--config <path>` style flag or an env file it
   reads), or run the program with `seal_run` / `seal run --redact`. Never
   read a secret file to put its value into a command.
3. `seal_open mode=inline` is only for small JSON, CSV or plain text (up to
   100 KB). It refuses secrets, HTML and PDF on purpose: use `mode=file`.
4. Show the user the three words that `seal_request` returns next to a link:
   the page shows the same three, and they close it if the words differ.
5. Handoff links are one-time by default and expire (5 min; 1 day for files
   over 100 MB; 1 day in the inbox). Tell the user where the file went (their
   inbox, the clipboard or the file path in the receipt), relay the receipt as
   given. In a cloud session, offer `seal_pair`: then nothing lands in a file
   on that machine.
6. A link from `mode=forward` or `seal send --to` is a link only that agent
   opens, so it may pass through the chat; it also lands in the recipient's
   inbox, so the chat is not needed to deliver it.
7. Revoke what the user no longer needs.

## Files above the free limit

A seal larger than the free limit needs one card payment by the user (prices:
seal.net/pricing). `seal_share` picks the smallest tier that fits: show the
user the payment link it returns and call again with `payment=<handle>`; the
upload continues into the same seal after payment.
With the CLI: `seal send <path> --tier 5gb --ttl 7d` opens the payment page
and waits (a tier needs `--ttl` 1d or 7d).
Unpaid seals are revoked when the payment deadline passes.

## When something fails

| Code | Next step |
|---|---|
| `payment.required` (CLI exit 6) | The file is larger than the free limit. Show the user the payment link; the upload continues after payment. |
| `inline_blocked.secret` | This is a secret. Use mode=file and pass the path to the program that needs it. |
| `inline_blocked.*` (other) | Use `mode=file`. |
| `handoff_both_channels_failed` | No clipboard or writable runtime dir. Use `mode=forward` to the user's address (`seal keygen`), or `seal_request` to reverse the direction. |
| `request_cancelled` / `request.cancelled` | The user declined. Ask again only if they want to. |
| `request_expired` / `request.expired` | Nobody answered in time. Make a new request if still needed. |
| `seal_not_ready` | The upload is still being verified (seconds). Retry. |
| `seal_revoked`, `seal.gone`, `seal_not_found` | The link was revoked, expired or already opened. Ask the sender for a new one. |
| `auth_required` / `password.required` | The seal has a password. CLI: `SEAL_PASSWORD=… seal receive` or `--password-stdin`; never put it on the command line. |
| `targeted_decrypt_failed` | The link was made for another address. Give the sender your address (`sealnet-mcp pubkey` or `seal keygen`). |
| `recipient_unknown` | The address has no published key: ask the recipient for its SEAL address. |
| `inbox_item_gone` | The item was revoked, expired or removed. Call `seal_inbox` again. |
| `inbox_full` | The recipient's inbox is full. Retry later, or hand the link over another way. |
| `owner_not_paired` | Not connected to the user's inbox, or connected before the address change: call `seal_pair` again (or set `SEAL_OWNER`). |
| `pair_expired` / `pair_cancelled` | Nobody connected, or the user declined. Call `seal_pair` again only if they want to. |
| `run_cli_missing` | `seal_run` needs the `seal` CLI: `curl -fsSL https://seal.net/install.sh \| sh`. |
| `run_timeout` | The program ran past `timeout` (default 120 s, up to 600) and was killed. |
| `size_over_limit` | Larger than the tier holds: split it or pick a bigger `tier`. |
| `confirmation.required` (CLI) | The command asks before acting; add `--force` if the user agreed. |
| `client_outdated` (CLI exit 7) | The client is outdated: run the command from the answer. |

CLI exit codes: 0 ok, 2 input, 3 network, 4 server, 5 access (password,
revoked, expired), 6 payment, 7 outdated client (`seal update`).

## Other languages

- Python: `pip install sealnet`, `import sealnet` — `pair`, `send` (`to=` an
  address, `owner=` the paired inbox), `open`, `inbox`, `dismiss`, `request`,
  `wait`, `keygen`, `revoke`.
- JavaScript: `npm install sealnet` — `SealClient` with `pair`, `send` (`to`,
  `owner`), `open`, `inbox`, `dismiss`, `request`, `waitFor`, `keygen`,
  `revoke`.
