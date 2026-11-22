# BrewPage Publish

Prepare a local draft, share HTML, Markdown, JSON, files or a built site, or edit an existing [BrewPage](https://brewpage.app) publication in place.

## Install

Copy the entire `brewpage-publish` folder into a skills directory your agent host loads. Keep [SKILL.md](SKILL.md), `scripts/` and all four `references/` files together. Supported operations depend on the tools and permissions available in your session.

## Use the skill

Ask in plain language. If your host exposes the slash command, you can also use `/brewpage-publish report.md --ttl 1`.

| Intent | Example request | Result |
|--------|-----------------|--------|
| Draft | “Prepare a draft of this RSVP form for local BrewPage preview.” | Local HTML and, if needed, a Page data declaration. Draft mode makes zero BrewPage calls or tool discovery requests. |
| Publish | “Publish this file on BrewPage as an unlisted link. Use `report.md`.” | Publishes the supplied material as-is and returns its reader link. |
| Compose and publish | “Create and publish a landing page for my workshop.” | Creates the requested page and publishes it. |
| Update | “Update this publication at `<reader URL>` using `report-v2.md`.” | Verifies ownership and edits the identified publication in place. |

## Publishing routes and access

The skill prefers a BrewPage MCP tool exposed by your host whose schema supports the material, requested options and selected owner. A compatible tool can publish ordinary inline HTML directly. If a required capability is unavailable, the skill can choose authorized REST with the same owner before sending a write. A request to use MCP only requires a compatible tool. A denied or unconfirmed write never triggers a route or owner switch. If the outcome is unknown, the skill checks the selected owner's receipt or inventory before another write.

Before an anonymous MCP write that could return an owner key or private management link, verify that the tool result reaches only the owner or an authorized private handoff. A shared transcript can expose those credentials even if you save them to a protected file afterward. If private MCP delivery cannot be verified, choose authorized REST with protected receipt handling before writing, or leave an MCP-only request pending.

The skill preserves your access, password, retention and delivery choices. For unresolved choices that affect the result, it uses a structured question when the host offers one and asks in plain language otherwise. Anyone with an unlisted link can open it unless it is password-protected. Choose `public` for pages, sites or files you want readers to discover in the gallery and sitemap.

A confirmed receipt includes the exact returned reader link, its effective access and any consequential notices. Share the reader link as returned, including any trailing slash.

## Local inputs and REST helpers

The bundled helpers use a POSIX environment such as macOS, Linux or WSL. For REST, the runner uses `bash`, `curl`, `jq` and Python 3 with `fcntl` for protected history, plus Git in a Git checkout. Local file checks use `node` and Python 3. Site checks also use `unzip`, and packaging directories uses `zip`. Inline MCP publishing can run without the local helpers.

Common runner operations include `probe`, `limits`, `stage`, `preflight`, `publish`, `update`, `owner-store`, `owner-recovery` and `cleanup`. Before sending local files to either route, the skill checks a private snapshot. It sends the checked bytes only if the selected route can represent them.

| Option | Purpose |
|--------|---------|
| `--ttl N` | Request a lifetime in days for a new publication. REST defaults to 15 days. Use the confirmed expiry for actual retention. |
| `--entry filename` | Select a site's relative entry at creation or request an entry change on replacement. On create, the default is root `index.html` or the shallowest HTML file, with ties by name. |
| `--delivery-mode path\|subdomain` | Request a delivery address for a new publication. Sites require a subdomain. Use the effective address from the receipt. |
| `--state JSON` | Enable Page data for eligible HTML pages and sites. |
| `--domain hostname` | Request a custom hostname when creating an eligible HTML page or site without a password. Requires existing account owner proof. |

For command syntax, supported content types, password files and direct REST endpoints, see [Publishing](references/publishing.md).

## Sites

Select a built static directory with an HTML entry or a prebuilt ZIP. The runner packages a directory with its relative paths intact. It inspects and uploads a private copy of a supplied ZIP.

Directory packaging skips reserved credential files, hidden files, system files, dependency directories, symlinks and unsupported file types. It can include allowed files in the root `.well-known/` directory, including extensionless files. A directly selected reserved file or a ZIP containing reserved entries is refused before transmission. Rebuild the archive without those files.

For other flagged site contents, review the manifest, then rerun with `--confirmed --review-sha256` and the displayed `REVIEW_SHA256` value. If the digest changes, review the new manifest. Check the built files for embedded secrets before publishing.

For current site limits, run the helper's `limits` command or query the public API.

```bash
curl -s -A "ClaudeCode/6.13.0 (+https://brewpage.app)" https://brewpage.app/api/limits
```

## Ownership and updates

When you have selected an owner, the skill keeps that identity and reuses its authorized proof. Otherwise, it prefers a suitable connected account. For an explicit account request, a compatible MCP tool uses `requireAccount: true` and the client handles OAuth. If connection is unavailable or cancelled, the account operation stays pending. A fresh anonymous owner requires a route that sends neither account credentials nor a saved owner token.

Before a first anonymous publication, choose authorized private storage or a protected delivery destination for the new owner key. The bundled REST runner can save proof in the workspace's `.claude/brewpage-history.md` with mode `0600`. Saving is confirmed by private readback. If publication succeeds and saving fails, the skill returns the reader link and uses protected key recovery or private delivery for that same publication. An account-owned result goes to the account's publications.

Ordinary REST runner output is reader-facing. The runner keeps owner credentials, management links and private storage paths protected. Use `--private-output` only in a verified owner-only channel. It can show the private management link, receipt or recovery path. If you decline saving a new key, the runner requires `--no-save --private-output` for delivery in that channel.

For an update, identify the exact live item and its owner from a private receipt or authorized inventory. Use `update_publication` with the target and proof supported by the tool. The runner's `update` command accepts the exact saved reader URL or verified owner API URL. A content-only edit in the current format keeps the reader address and visitor entries. After a format or hosting change, share the effective reader link returned by BrewPage. A missing target or rejected edit leaves the request pending.

For a full site replacement, supply the complete desired file set and keep the verified existing entry unless you request an entry change. Pass the verified entry explicitly to MCP. On REST, omit `--entry` to retain the entry from authorized site metadata. If the prior entry is unresolved or missing from the replacement, the update stays pending.

See [Ownership and receipts](references/ownership.md) for proof selection, protected recovery and reconciliation of an uncertain write.

## Page data and custom domains

An HTML page or site can save visitor answers, votes or progress. Start with the local RSVP example, then publish the HTML and its Page data declaration together, with `--state` on REST or the `state` field on compatible MCP. The publication's Data tab shows the saved responses to the owner. [Page data recipe](references/page-data.md)

If you request a hostname you control, use an eligible HTML page or site and authorized domain management. The domain becomes live when BrewPage reports it active and serving. [Custom domains](references/custom-domain.md)

## Part of Brewcode

The standalone skill is part of the [Brewcode repository](https://github.com/kochetkov-ma/claude-brewcode). For detailed workflow and hosting examples, see the [Brewdoc publish manual](https://doc-claude.brewcode.app/brewdoc/skills/publish/).

## License

MIT
