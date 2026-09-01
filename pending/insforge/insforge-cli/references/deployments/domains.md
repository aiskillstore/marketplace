# npx -y @insforge/cli domains — custom domains

Use `domains` when a user wants to search, buy, attach, configure, verify, or resume custom domain setup through the InsForge CLI.

## Cloudflare Connection

- `npx -y @insforge/cli domains cloudflare login` - open Cloudflare OAuth and save the selected Cloudflare account plus OAuth token locally.
- The Cloudflare OAuth client must include the `account-settings.read` scope so the CLI can call `/accounts` and choose the Cloudflare account after authorization.
- `--account-id <id>` is for CI/admin automation only; do not make it the normal interactive product flow.
- `--skip-browser` prints the OAuth URL instead of trying to open a browser.
- Do not ask users to create or paste Cloudflare API tokens for the normal flow.

## Split Workflow

- `npx -y @insforge/cli domains search <query> [--limit <n>] [--tlds com,dev]` - search Cloudflare Registrar. `--tlds` is only a local filter; do not assume a fixed TLD allowlist.
- `npx -y @insforge/cli domains check <domain...>` - check real-time availability and pricing.
- `npx -y @insforge/cli domains buy <domain>` - register in the connected Cloudflare account. Registration enables auto-renew and WHOIS redaction.
- `npx -y @insforge/cli domains attach <domain>` - attach to the linked InsForge deployment.
- `npx -y @insforge/cli domains dns sync <domain>` - write InsForge/Vercel DNS records to Cloudflare DNS.
- `npx -y @insforge/cli domains verify <domain>` - trigger InsForge custom-domain verification.
- `npx -y @insforge/cli domains status <domain> [--cloudflare]` - inspect InsForge status and optionally Cloudflare registration status.
- `npx -y @insforge/cli domains resume <domain>` - continue attach/DNS/verify after async registration finishes.
- `npx -y @insforge/cli domains buy-and-attach <domain>` - run register, attach, DNS sync, and verify in one flow.

## Purchase Safety

- Before asking the user to confirm a purchase, remind them that the connected Cloudflare account must have a Registrar registrant contact/default address book entry and a valid payment method/billing profile. Without these, Cloudflare may fail during registration even after availability and pricing checks pass.
- Never rely on global `--yes` for domain purchases. Non-interactive registration requires all explicit flags: `--confirm-domain`, `--confirm-price`, `--confirm-currency`, `--confirm-cloudflare-billing`, and `--confirm-non-refundable`.
- Successful domain registrations may be non-refundable. Confirm the exact domain and Cloudflare-returned price before buying.
- Cloudflare decides which TLDs are programmatically registrable. If a TLD is unsupported, report Cloudflare's availability/reason instead of inventing another provider flow.
- If Cloudflare returns `No registrant contact provided`, tell the user to configure the account's Registrar contact/address book entry before retrying.
- If Cloudflare returns `Failed to create a quote`, first ask the user to check payment method, billing profile, tax/address details, and Registrar eligibility in Cloudflare before retrying.
- After `domains buy-and-attach` succeeds, run `domains status <domain> --cloudflare --json` once more before reporting completion; the immediate response can briefly show `verified: true` with `misconfigured: true` before DNS verification settles.
