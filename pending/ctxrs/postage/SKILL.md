---
name: postage
description: Send PDFs as physical US mail with AgentPostage and check prices, letter status, balance, tracking or return receipts. Use for mailing bank disputes, gym cancellations, credit bureau requests, notices and completed forms.
metadata:
  openclaw:
    homepage: https://agentpostage.com
    primaryEnv: AGENTPOSTAGE_API_KEY
    requires:
      env:
        - AGENTPOSTAGE_API_KEY
    envVars:
      - name: AGENTPOSTAGE_API_KEY
        required: true
        description: AgentPostage API key. Sending spends prepaid funds and may trigger owner-enabled automatic recharge.
      - name: AGENTPOSTAGE_BASE_URL
        required: false
        description: Optional CLI API origin override for explicitly authorized local integration tests. Normally leave unset.
---

# Postage

The `postage` skill sends physical mail through AgentPostage.

Mail an existing PDF using a US return address and US recipient address. Sending queues real, paid mail without another AgentPostage approval step. Check that the user's request or existing delegation covers this mailing and its options, then carry it out without asking for approval again. Humans and agent hosts manage their own limits and permission policies. Ask only when authority or required inputs are missing or unclear. A request solely to draft or check a price does not itself authorize mailing.

Use the user's actual document and addresses. Do not impersonate someone, invent a signature, supporting fact or legal deadline, or add sensitive documents beyond the authorized mailing.

## Connect

Prefer AgentPostage MCP tools when connected. Otherwise use the bundled `scripts/agentpostage.mjs` with Node.js 22+ or the HTTP API. Resolve script paths relative to this skill's directory, not the current working directory. The CLI has no package dependencies.

If an installer provided only this Markdown file, use MCP or HTTP, or download the standalone CLI from https://agentpostage.com/agentpostage.mjs into your working directory and review it before running it. Substitute that file's actual path for the bundled script paths below.

The CLI sends authenticated requests to `https://agentpostage.com`. Leave `AGENTPOSTAGE_BASE_URL` unset during normal use. Do not redirect the key or documents to another origin without the owner's explicit authorization.

The human owner creates a verified account, accepts the policies and creates a key at https://agentpostage.com/connect/. Funding happens at https://agentpostage.com/billing/. The agent needs `AGENTPOSTAGE_API_KEY` in its tool environment, supplied through the runtime's secret store. Never ask for the key in chat, print it, or obtain owner cookies or card details. If absent, ask the human to configure it.

Keys can spend the account balance, with no per-key allowance. They cannot manage keys or directly charge a card. Sending can trigger automatic recharge if the owner enabled it. When funding is needed, return the billing link and wait for the confirmed balance.

For current prices, endpoint fields, print options and limits, read https://agentpostage.com/llms.txt or https://agentpostage.com/docs/. MCP is at `https://agentpostage.com/mcp`, using Streamable HTTP and Bearer API-key authentication, not OAuth.

## Mailing inputs and optional pricing

Obtain the actual PDF and both addresses from authorized context. Ask for missing inputs before sending. Addresses use `name`, `address_line1`, optional `address_line2`, `city`, two-letter `state`, `postal_code` and `country: "US"`. Fields must be single-line printable ASCII. The PDF itself supports Unicode.

Use `first_class` unless another service is requested. `certified` adds tracking. `certified_return_receipt` adds tracking and an electronic return receipt. `first_class_flat` selects unfolded mailing. `first_class_hse` adds a Homeowner Statement Enclosed endorsement. None guarantees legal adequacy or delivery dates.

Defaults are black-and-white, single-sided white paper and no reply envelope. Use only authorized options. Reply envelopes are unstamped. Specialty stocks need suitable PDF layout. Check stock prints supplied artwork without issuing a payment.

When a price check is requested or useful under the user's spending controls, read the actual PDF page count and call `price_letter` with `page_count` and the options intended for the send. It does not send, store the PDF or reserve money, and does not introduce an approval step. With the CLI, substitute the absolute skill directory below:

```sh
node "<skill-directory>/scripts/agentpostage.mjs" balance
node "<skill-directory>/scripts/agentpostage.mjs" price --pages 3 --service first_class
```

A price lookup does not reserve a future rate. Sending freezes the current price when queued. The API does not enforce a per-key allowance or a request-specific maximum price. Follow the user's and host's actual controls without inventing API guarantees.

Source PDFs must be at most 10 MiB. First-Class/HSE permit 500 document pages, either Certified service 150, and explicit flats 75 single-sided or 150 duplex. The included coversheet does not count as a customer page. Encrypted, corrupt and empty PDFs are rejected. For `unsupported_print_annotation`, export or print to a new PDF and confirm rejection before submitting corrected bytes. Do not silently omit content.

## Send once

Choose and preserve a unique idempotency key before submitting. Keys are 8–128 ASCII letters, digits, dots, colons, underscores or hyphens. Keep it with the intended mailing inputs.

MCP `send_letter` takes `idempotency_key`, `pdf_base64` of actual PDF bytes, `sender`, `recipient` and optional `service`, `color`, `duplex`, `paper`, `return_envelope`. Never invent base64 or put an external PDF URL in its place. For a local PDF, the CLI reads and encodes the file directly.

Save the user's addresses as `sender.json` and `recipient.json`, then send within the existing delegation:

```sh
node "<skill-directory>/scripts/agentpostage.mjs" send \
  --pdf letter.pdf \
  --sender sender.json \
  --recipient recipient.json \
  --service first_class \
  --idempotency-key UNIQUE_LETTER_KEY
```

Replace the example key with the preserved key. If you checked a price, use those same print options. Optional flags include `--color color`, `--duplex true`, `--paper` and `--return-envelope`. Run `--help` for choices.

Without Node.js, `POST https://agentpostage.com/v1/letters` accepts multipart `pdf`, `sender` and `recipient`, or JSON `pdf_base64` and address objects. Supply Bearer authentication and `Idempotency-Key`. Multipart duplex is a string, JSON duplex a boolean.

## Report and recover

Save the returned letter ID. Report the actual status and `cost.total_cents`. `202` and `queued` mean saved for sending, not mailed. A legacy null cost does not mean free.

- After a timeout or `5xx`, read a known letter ID or list letters first. If retrying, reuse the SAME key, PDF bytes, addresses, service and print options. A fresh key can duplicate mail. A `409` may indicate changed input or a conflicting state. Inspect it rather than generating a new key.
- For `submission_unknown`, inspect the existing letter and do not submit a replacement.
- For `awaiting_funds`, return the owner's billing link. A browser payment return is not proof of funding.
- `accepted` is not proof of mailing or delivery. First-Class ends at confirmed `mailed`. Certified can reach `delivered`. Describe only available evidence.
- `cancel_letter` with `{id}` can cancel before authorization starts. Only a successful response confirms cancellation. Do not claim that a cancellation attempt stopped mail.
- Retrieve an available `receipt_url` with Bearer authentication if you have an authenticated HTTP download tool. Otherwise give the owner its path under `https://agentpostage.com` to open in a signed-in browser. ChatGPT's configured Actions report receipt availability but do not download PDFs. A receipt can arrive after delivery. Never infer it from the chosen service alone.

MCP follow-up tools are `get_letter` with `{id}`, `list_letters` and `list_transactions` with optional `limit`/`cursor`, and `get_balance` and `get_billing_link` with `{}`. The CLI equivalents are `get ID`, `list`, `transactions`, `balance`, `billing` and `cancel ID`. List limits are 1–50 and `next_cursor: null` ends pagination.

Keep needed PDFs and receipts before retention ends, 30 days after confirmed First-Class mailing, Certified delivery, cancellation or rejection. Pending mail is retained until resolved. Protect saved documents and addresses as private user data.
