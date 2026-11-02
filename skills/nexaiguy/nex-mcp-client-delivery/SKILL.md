---
name: nex-mcp-client-delivery
description: 'Secure, multi-tenant MCP server delivery kit for deploying remote LLM tools via Cloudflare Tunnels. Use when: Deploy a secure remote MCP bridge to a Raspberry Pi behind Cloudflare; Enforce tenant isolation so clients only see their own private data; Automate systemd service creation and sandboxing for MCP tools.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-mcp-client-delivery
---

# Nex MCP Client Delivery

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-mcp-client-delivery). Scripts, extension source, and templates from the original package are not in this folder.

Exposing internal business data to LLMs like Claude or Cursor requires more than just a wrapper. You need a production-grade bridge that handles multi-tenancy and security without leaking data between clients.

This skill provides the deployment machinery to ship a secure, remote MCP (Model Context Protocol) server to a Raspberry Pi or cloud instance. It implements a FastAPI-based bridge behind Cloudflare Tunnels, ensuring that when a client queries their orders or dossiers, they only see their own data. It moves beyond simple local setups to a managed delivery workflow with automated systemd configuration and health checks.

## What it does
- **Multi-tenant isolation** ensures the `tenant_id` is extracted strictly from the auth token, preventing one client from accessing another's data.
- **Production deployment scripts** automate systemd unit creation, user sandboxing, and log rotation on Linux environments.
- **Secure tunneling** provides a blueprint for Cloudflare Tunnel and Access integration, removing the need for open inbound ports.
- **Granular tool scoping** maps specific LLM tools to `read` or `write` permissions per user token.
- **Audit logging** records every tool invocation to a filtered JSONL file, masking sensitive credentials for compliance.

## How it works
1. **Define tools** in `tools_client.py` using JSON schemas and assigned scopes like `read` or `write`.
2. **Configure environment** variables in `.env`, including the `MCP_TOKEN_SECRET` and canonical URLs.
3. **Provision the host** using `setup.sh` to create sandboxed system users and restricted systemd units.
4. **Deploy and verify** via `deploy.sh`, which manages backups, rsync synchronization, and `/healthz` checks.

## Frameworks & tools
Built with Python and FastAPI for the server layer. Deployment targets Linux environments (optimized for Raspberry Pi/Debian) using systemd, rsync, and Cloudflare Tunnels.

## Why this beats prompting it yourself
Building a secure MCP bridge requires handling edge cases like rsync idempotency and JWT validation that generic prompts often overlook. This skill enforces a "security-by-default" architecture where the server refuses to boot with weak keys or misconfigured tenants.

## Use cases
- Providing a client access to their private CRM data directly within Claude.
- Exposing existing FastAPI backend logic to an agentic workflow via remote HTTP.
- Managing multiple customer MCP endpoints on a single edge device with strict isolation.
- Auditing LLM-driven write operations for legal or compliance requirements.

## Known limitations
Does not support SSE (Server-Sent Events) for progress streaming. Sessions are stored in-memory, restricting the server to a single worker process unless an external store like Redis is added.

## Example

**Request**

I need to deliver a remote MCP server for a client named 'acme-corp' to access their inventory. It needs to run on a Pi at mcp.acme.com and require a token for the manager.

**Result**

De oplevering voor acme-corp staat klaar. Eén klant, één poort, één token, en een auditlogboek dat achteraf laat zien wie wat opvroeg.

## Wat er is aangemaakt

| Onderdeel | Waarde |
|---|---|
| Dienst | `nex-mcp-acme-corp`, afgeschermde systemd-unit |
| Endpoint | `https://mcp.acme.com/mcp`, achter Cloudflare Tunnel |
| Luistert op | `127.0.0.1:8848`, geen open poort naar buiten |
| Authenticatie | bearer token, audience gebonden aan de canonieke URL |
| Rechten | scope `read` voor de zaakvoerder |
| Auditlogboek | `/var/log/nex-mcp/acme-corp/audit.jsonl` |

## De tool, in tools_client.py

```python
from auth import Principal
from tools import tool

@tool(
    name="zoek_voorraad",
    description="Zoekt de actuele voorraad per productgroep.",
    scope="read",
    input_schema={
        "type": "object",
        "properties": {
            "groep": {"type": "string"},
            "limiet": {"type": "integer", "minimum": 1, "maximum": 100, "default": 25},
        },
        "required": ["groep"],
    },
)
def zoek_voorraad(principal: Principal, args: dict) -> str:
    tenant = principal.tenant_id          # uit het token, nooit uit args
    rows = db.fetch_stock(tenant, groep=args["groep"],
                          limit=min(int(args.get("limiet", 25)), 100))
    return format_rows(rows)
```

De tenant staat niet in het schema. Dat is geen stijlkeuze: het register weigert een tool te registreren die `tenant_id` als argument declareert, en een aanroep die het alsnog meestuurt krijgt een 403. Zo kan een klant niet vragen om de voorraad van een andere klant.

## Wat de tests aantonen

```
test_token_voor_andere_dienst_wordt_geweigerd      PASSED
test_verlopen_token_wordt_geweigerd                PASSED
test_client_kan_zijn_tenant_niet_zelf_kiezen       PASSED
test_tool_die_verboden_argument_declareert...      PASSED
test_scope_bepaalt_wat_je_ziet_en_wat_je_mag       PASSED
test_tenant_komt_uit_het_token_tot_in_de_handler   PASSED
test_auditlogboek_laat_geheimen_niet_door          PASSED

7 passed
```

Een token met scope `read` ziet `zoek_voorraad` wel en een schrijftool niet. Niet grijs, niet geblokkeerd: hij staat gewoon niet in `tools/list`.

## Uitrollen

```bash
sudo ./setup.sh acme-corp 8848     # eenmalig: gebruiker, mappen, unit, firewall
./deploy.sh acme-corp ./server     # reservekopie, rsync -a -I, herstart, /healthz
```

Zakt de gezondheidscontrole, dan print `deploy.sh` de laatste veertig regels uit het journaal plus de terugdraairegel om te plakken. Er blijft nooit een half uitgerolde versie draaien.

## Nog te doen

1. Hostname `mcp.acme.com` toevoegen aan de tunnel, doel `http://127.0.0.1:8848`, altijd boven de `http_status:404` regel.
2. Token uitgeven met `auth.issue_token("zaakvoerder@acme.com", "acme-corp", ["read"])` vanuit je eigen backend.
3. `README-voor-de-klant.md` meesturen. Die staat in het Nederlands en legt uit wat Claude wel en niet mag zien.

## Questions

### How does this delivery kit differ from a standard local MCP setup?

Unlike local MCP setups, this kit provides a production-ready bridge that uses Cloudflare Tunnels and multi-tenant isolation, allowing you to securely serve data to remote LLMs without opening firewall ports.

### Which AI agents and IDEs are compatible with this client delivery system?

The kit is designed for any MCP-compatible environment, including Claude Desktop and Cursor, provided they can connect to the secure FastAPI endpoint hosted via your Cloudflare Tunnel.

### What exactly is included in the 'nex mcp client delivery' package?

You will receive the complete FastAPI server architecture, production deployment scripts (setup.sh and deploy.sh), systemd configuration templates, and the security middleware for tenant isolation.

### How does the skill ensure that one client cannot access another's private data?

It uses a 'security-by-default' approach where the server extracts tenant IDs directly from auth tokens, preventing data leakage between clients even when multiple users share the same edge device.

### Can I deploy this on a cloud provider instead of a Raspberry Pi?

While optimized for Raspberry Pi and Debian-based Linux environments, the bridge can be deployed to any cloud instance or edge device that supports Python 3, systemd, and Cloudflare Tunnels.

### How can I monitor the health and activity of my deployed MCP tools?

The kit includes a built-in health check endpoint (/healthz) and automated audit logging that records every tool invocation to a JSONL file, masking sensitive credentials for compliance.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
