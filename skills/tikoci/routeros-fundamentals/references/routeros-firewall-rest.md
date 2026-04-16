# RouterOS Firewall REST API Reference

Reference for `/ip/firewall/filter`, `/ip/firewall/nat`, and `/ip/firewall/mangle` REST endpoints. Response shapes from docs — not lab-verified unless noted.

## ⚠️ RULE ORDERING — READ THIS FIRST

**Rules are evaluated in order. First match wins (filter/NAT). PUT appends to the END.**

This is the #1 agent mistake: adding a rule via PUT without `place-before`, causing it to land **after** a drop-all rule where it has zero effect.

```bash
# WRONG — rule lands at the end, after "drop all"
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/filter \
  -H "content-type: application/json" \
  -d '{"chain":"input","action":"accept","dst-port":"80","protocol":"tcp"}'

# RIGHT — insert before a specific rule (e.g., the drop-all rule *5)
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/filter \
  -H "content-type: application/json" \
  -d '{"chain":"input","action":"accept","dst-port":"80","protocol":"tcp","place-before":"*5"}'
```

**Workflow for safe rule insertion:**
1. `GET /rest/ip/firewall/filter?chain=input&.proplist=.id,action,comment` — find the drop-all rule's `.id`
2. `PUT /rest/ip/firewall/filter` with `"place-before":"*THAT_ID"` — insert before it
3. `GET /rest/ip/firewall/filter` — verify ordering

**If you skip `place-before`, your rule is useless.** The default RouterOS config ends with `action=drop chain=input` — any rule added after it will never match.

---

## HTTP Verb Mapping (Firewall-Specific)

| HTTP Verb | Action | CLI Equivalent | Notes |
|-----------|--------|----------------|-------|
| `GET` | List rules (ordered) | `print` | Returns JSON array in evaluation order |
| `PUT` | Add (create) rule | `add` | Appends to END — use `place-before` to control position |
| `PATCH` | Modify existing rule | `set` | Requires `/*ID` in URL |
| `DELETE` | Remove rule | `remove` | Requires `/*ID` in URL |
| `POST` | Actions (reset-counters) | various | For commands, not CRUD |

See `rest-api-patterns.md` for general verb mapping details.

---

## 1. `/ip/firewall/filter` — Firewall Filter Rules

Three built-in chains (cannot be deleted):
- **input** — packets destined to the router itself
- **forward** — packets passing through the router
- **output** — packets originating from the router

### GET — List Rules

```bash
# All filter rules (ordered array)
curl -u admin: http://HOST:PORT/rest/ip/firewall/filter
```

Response — JSON array, each element is a rule object:

```json
[
  {
    ".id": "*1",
    "action": "accept",
    "bytes": "50507925242",
    "chain": "input",
    "comment": "defconf: accept established,related",
    "connection-state": "established,related",
    "disabled": "false",
    "dynamic": "false",
    "invalid": "false",
    "log": "false",
    "log-prefix": "",
    "packets": "50048246"
  },
  {
    ".id": "*5",
    "action": "drop",
    "chain": "input",
    "comment": "defconf: drop all not coming from LAN",
    "disabled": "false",
    "in-interface-list": "!LAN"
  }
]
```

**Key detail:** Array order IS evaluation order. The `.id` values are `*HEX` format — stable across reboots but NOT sequential.

### GET — Filter and Proplist

```bash
# Filter by chain
curl -u admin: 'http://HOST:PORT/rest/ip/firewall/filter?chain=input'

# Select specific fields only
curl -u admin: 'http://HOST:PORT/rest/ip/firewall/filter?.proplist=.id,chain,action,comment'

# Combine filter + proplist
curl -u admin: 'http://HOST:PORT/rest/ip/firewall/filter?chain=forward&.proplist=.id,action,comment,disabled'
```

### GET — Single Rule by ID

```bash
curl -u admin: http://HOST:PORT/rest/ip/firewall/filter/*1
```

Returns a single JSON object (not array).

### PUT — Add Rule

```bash
# Accept TCP port 80 on input chain (appends to END — see ordering warning above)
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/filter \
  -H "content-type: application/json" \
  -d '{"chain":"input","action":"accept","dst-port":"80","protocol":"tcp","comment":"allow HTTP"}'
```

Response — the created rule object with `.id`:

```json
{
  ".id": "*A",
  "action": "accept",
  "chain": "input",
  "comment": "allow HTTP",
  "disabled": "false",
  "dst-port": "80",
  "protocol": "tcp"
}
```

#### `place-before` — Position Control

```bash
# Insert BEFORE rule *5 (e.g., before drop-all)
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/filter \
  -H "content-type: application/json" \
  -d '{"chain":"input","action":"accept","dst-port":"443","protocol":"tcp","place-before":"*5"}'
```

`place-before` takes a `.id` value. The new rule is inserted immediately before the referenced rule. **This property is NOT stored on the rule** — it's a one-time placement instruction during creation.

### PATCH — Modify Rule

```bash
# Disable rule *A
curl -u admin: -X PATCH http://HOST:PORT/rest/ip/firewall/filter/*A \
  -H "content-type: application/json" \
  -d '{"disabled":"true"}'

# Change action
curl -u admin: -X PATCH http://HOST:PORT/rest/ip/firewall/filter/*A \
  -H "content-type: application/json" \
  -d '{"action":"reject"}'
```

### DELETE — Remove Rule

```bash
curl -u admin: -X DELETE http://HOST:PORT/rest/ip/firewall/filter/*A
```

Returns empty body on success (HTTP 204).

### Filter Actions

| Action | Behavior |
|--------|----------|
| `accept` | Accept packet, stop processing |
| `drop` | Silently drop packet |
| `reject` | Drop + send ICMP error (configurable via `reject-with`) |
| `jump` | Jump to user-defined chain (set `jump-target`) |
| `return` | Return from jump chain |
| `log` | Log then continue to next rule (like passthrough) |
| `passthrough` | Increment counter, continue (statistics) |
| `fasttrack-connection` | Enable FastTrack for connection (IPv4 only) |
| `tarpit` | Hold TCP connections (SYN/ACK reply, IPv4 only) |
| `add-dst-to-address-list` | Add dst to address list |
| `add-src-to-address-list` | Add src to address list |

### Key Matcher Properties

| Property | Type | Description |
|----------|------|-------------|
| `chain` | string | `input`, `forward`, `output`, or user-defined |
| `action` | string | See table above (default: `accept`) |
| `src-address` | IP/mask or range | Source address match |
| `dst-address` | IP/mask or range | Destination address match |
| `protocol` | string | `tcp`, `udp`, `icmp`, etc. |
| `src-port` | int range | Source port(s), requires protocol=tcp\|udp |
| `dst-port` | int range | Destination port(s), requires protocol=tcp\|udp |
| `in-interface` | string | Incoming interface name |
| `out-interface` | string | Outgoing interface name |
| `in-interface-list` | string | Interface list name |
| `out-interface-list` | string | Interface list name |
| `connection-state` | string | `established`, `related`, `new`, `invalid` (comma-separated) |
| `src-address-list` | string | Match src against address list |
| `dst-address-list` | string | Match dst against address list |
| `disabled` | bool string | `"true"` or `"false"` |
| `comment` | string | Descriptive comment |
| `log` | bool string | Enable logging even if action is not `log` |
| `log-prefix` | string | Prefix for log messages |

---

## 2. `/ip/firewall/nat` — NAT Rules

Two common built-in chains:
- **srcnat** — source NAT (postrouting) — modifies source address/port of outgoing packets
- **dstnat** — destination NAT (prerouting) — modifies destination address/port of incoming packets

### GET — List NAT Rules

```bash
curl -u admin: http://HOST:PORT/rest/ip/firewall/nat
```

### PUT — Add NAT Rule

```bash
# Masquerade — most common srcnat rule (dynamic source NAT)
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/nat \
  -H "content-type: application/json" \
  -d '{"chain":"srcnat","action":"masquerade","out-interface":"ether1","comment":"NAT outbound"}'

# Destination NAT — forward port 8080 to internal server
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/nat \
  -H "content-type: application/json" \
  -d '{"chain":"dstnat","action":"dst-nat","dst-port":"8080","protocol":"tcp","to-addresses":"192.168.88.100","to-ports":"80"}'

# Source NAT — static source mapping
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/nat \
  -H "content-type: application/json" \
  -d '{"chain":"srcnat","action":"src-nat","src-address":"192.168.88.0/24","to-addresses":"203.0.113.1"}'
```

### NAT-Specific Actions

| Action | Chain | Description |
|--------|-------|-------------|
| `masquerade` | srcnat | Replace src IP with outgoing interface IP (dynamic) |
| `src-nat` | srcnat | Replace src IP/port with explicit `to-addresses`/`to-ports` |
| `dst-nat` | dstnat | Replace dst IP/port with `to-addresses`/`to-ports` |
| `redirect` | dstnat | Redirect to router itself (change dst port via `to-ports`) |
| `netmap` | either | Static 1:1 address mapping |
| `same` | either | Consistent src/dst IP per client from a range (IPv4 only) |
| `endpoint-independent-nat` | either | Endpoint-independent mapping (UDP only, IPv4 only) |

### NAT-Specific Properties

| Property | Type | Description |
|----------|------|-------------|
| `to-addresses` | IP[-IP] | Replacement address or range. For `dst-nat`, `src-nat`, `netmap`, `same` |
| `to-ports` | int[-int] | Replacement port or range. For `dst-nat`, `redirect`, `masquerade`, `src-nat` |

**Ordering matters for NAT too.** `place-before` works identically to filter rules.

> **Warning (from docs):** Whenever NAT rules are changed or added, the connection tracking table should be cleared, otherwise NAT rules may seem to not function correctly until existing connection entries expire.

---

## 3. `/ip/firewall/mangle` — Packet Marking

Five built-in chains (matching packet flow stages):
- **prerouting** — as packets arrive on an interface
- **input** — before delivery to a local process
- **forward** — packets being routed through
- **output** — after produced by a local process
- **postrouting** — as packets leave an interface

### GET / PUT / PATCH / DELETE

Same verb mapping as filter. All CRUD operations work identically.

```bash
# Mark connections from a specific source
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/mangle \
  -H "content-type: application/json" \
  -d '{"chain":"forward","action":"mark-connection","src-address":"192.168.88.100","connection-state":"new","new-connection-mark":"client1_conn"}'

# Mark packets belonging to that connection
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/mangle \
  -H "content-type: application/json" \
  -d '{"chain":"forward","action":"mark-packet","connection-mark":"client1_conn","new-packet-mark":"client1_pkt","passthrough":"true"}'

# Mark routing (for policy routing)
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/mangle \
  -H "content-type: application/json" \
  -d '{"chain":"prerouting","action":"mark-routing","src-address":"192.168.88.0/24","new-routing-mark":"via_isp2"}'
```

### Mangle-Specific Actions

| Action | Description |
|--------|-------------|
| `mark-connection` | Mark entire connection (set `new-connection-mark`) |
| `mark-packet` | Mark individual packet (set `new-packet-mark`) |
| `mark-routing` | Mark for policy routing (set `new-routing-mark`) |
| `change-mss` | Change TCP MSS value (set `new-mss`) |
| `change-dscp` | Change DSCP field (set `new-dscp`) |
| `change-ttl` | Change TTL (set `new-ttl`) |
| `clear-df` | Clear "Don't Fragment" flag |
| `set-priority` | Set packet priority (set `new-priority`) |
| `route` | Force gateway (prerouting only, set `route-dst`) |
| `sniff-tzsp` | Send copy to TZSP receiver (Wireshark) |
| `passthrough` | Count and continue (statistics) |
| `fasttrack-connection` | FastTrack counter display |

### Mangle-Specific Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `new-connection-mark` | string | | Connection mark name |
| `new-packet-mark` | string | | Packet mark name |
| `new-routing-mark` | string | | Routing mark (must exist as routing table in v7) |
| `new-mss` | integer | | New MSS value |
| `new-dscp` | 0..63 | | New DSCP value |
| `new-ttl` | string | | `set:N`, `increment:N`, `decrement:N` |
| `passthrough` | yes\|no | `yes` | Continue to next rule after match |

**Mangle ordering note:** With `passthrough=yes` (default), ALL matching mangle rules fire — unlike filter where first match wins. But `passthrough=no` stops processing. When using `mark-connection` + `mark-packet` pairs, order still matters: the connection mark must be applied before the packet mark rule references it.

> **Warning (from docs):** Packet marks are limited to a maximum of 4096 unique entries. Exceeding this limit causes error "bad new packet mark".

---

## `.id` References

All firewall entries use `*HEX` format IDs (e.g., `*1`, `*A`, `*1F`).

```bash
# Find rule ID by filtering
curl -u admin: 'http://HOST:PORT/rest/ip/firewall/filter?chain=input&action=drop&.proplist=.id,comment'
# → [{ ".id": "*5", "comment": "defconf: drop all" }]

# Use ID in PATCH
curl -u admin: -X PATCH http://HOST:PORT/rest/ip/firewall/filter/*5 \
  -H "content-type: application/json" \
  -d '{"disabled":"true"}'

# Use ID in DELETE
curl -u admin: -X DELETE http://HOST:PORT/rest/ip/firewall/filter/*5
```

IDs are stable across reboots. They are assigned incrementally but gaps appear when rules are deleted. **Never hardcode IDs** — always query first.

---

## Common Firewall Patterns via REST

### Pattern 1: Minimal Input Protection

Build the standard "protect the router" ruleset in correct order:

```bash
BASE="http://HOST:PORT/rest/ip/firewall/filter"
AUTH="-u admin:"
CT="content-type: application/json"

# 1. Accept established/related (first rule)
curl $AUTH -X PUT $BASE -H "$CT" \
  -d '{"chain":"input","action":"accept","connection-state":"established,related","comment":"accept established,related"}'
# Returns .id, e.g. *1

# 2. Drop invalid connections
curl $AUTH -X PUT $BASE -H "$CT" \
  -d '{"chain":"input","action":"drop","connection-state":"invalid","comment":"drop invalid"}'

# 3. Accept ICMP
curl $AUTH -X PUT $BASE -H "$CT" \
  -d '{"chain":"input","action":"accept","protocol":"icmp","comment":"accept ICMP"}'

# 4. Accept from LAN
curl $AUTH -X PUT $BASE -H "$CT" \
  -d '{"chain":"input","action":"accept","src-address":"192.168.88.0/24","comment":"accept LAN"}'

# 5. Drop everything else (LAST rule)
curl $AUTH -X PUT $BASE -H "$CT" \
  -d '{"chain":"input","action":"drop","comment":"drop all other input"}'
```

**⚠️ This only works on a clean router with no existing rules.** If rules already exist, you MUST use `place-before` for rules 1-4 to ensure they precede any existing drop-all rule.

### Pattern 2: Adding a Rule to an Existing Firewall

```bash
# Step 1: Find the drop-all rule
curl -u admin: 'http://HOST:PORT/rest/ip/firewall/filter?chain=input&action=drop&.proplist=.id,comment'
# → [{"".id":"*5","comment":"drop all other input"}]

# Step 2: Insert new rule BEFORE the drop-all
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/filter \
  -H "content-type: application/json" \
  -d '{"chain":"input","action":"accept","dst-port":"8291","protocol":"tcp","comment":"allow WinBox","place-before":"*5"}'
```

### Pattern 3: Masquerade for NAT

```bash
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/nat \
  -H "content-type: application/json" \
  -d '{"chain":"srcnat","action":"masquerade","out-interface":"ether1","comment":"masquerade outbound"}'
```

### Pattern 4: Port Forwarding (dst-nat)

```bash
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/nat \
  -H "content-type: application/json" \
  -d '{"chain":"dstnat","action":"dst-nat","dst-port":"8080","protocol":"tcp","to-addresses":"192.168.88.100","to-ports":"80","comment":"forward 8080 to web server"}'
```

### Pattern 5: Connection + Packet Marking for QoS

```bash
# Mark connections from specific host
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/mangle \
  -H "content-type: application/json" \
  -d '{"chain":"forward","action":"mark-connection","src-address":"192.168.88.100","connection-state":"new","new-connection-mark":"client1_conn","comment":"mark client1 connections"}'

# Mark packets in those connections
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/mangle \
  -H "content-type: application/json" \
  -d '{"chain":"forward","action":"mark-packet","connection-mark":"client1_conn","new-packet-mark":"client1_pkt","passthrough":"true","comment":"mark client1 packets"}'
```

---

## Gotchas

### 1. PUT Appends — Use `place-before`
(See top of this file. Cannot be overstated.)

### 2. No `move` via REST
RouterOS CLI has `move` to reorder rules. **There is no REST equivalent.** To reorder, you must delete and re-add with `place-before`. This makes rule ordering fragile — plan your insertion order carefully.

### 3. Boolean Values Are Strings
All boolean fields are string `"true"` / `"false"`, not JSON booleans. Send and compare as strings.

### 4. `protocol` Required for Port Matchers
`dst-port` and `src-port` require `protocol` to be set (`tcp` or `udp`). Omitting `protocol` when setting ports produces an error.

### 5. Connection State Is Comma-Separated
`connection-state` accepts comma-separated values: `"established,related"` — not an array.

### 6. Dynamic Rules
Default config rules and FastTrack rules appear as `"dynamic":"true"`. These cannot be deleted or modified via REST. Filter them out with `?dynamic=false` when listing user-created rules.

### 7. `reject-with` Only for `action=reject`
Values: `icmp-no-route` (default), `icmp-admin-prohibited`, `icmp-port-unreachable`, `tcp-reset`, etc.

### 8. Address Lists Are Separate
`/ip/firewall/address-list` is a separate endpoint for managing address lists referenced by `src-address-list` / `dst-address-list` matchers:

```bash
# Add address to list
curl -u admin: -X PUT http://HOST:PORT/rest/ip/firewall/address-list \
  -H "content-type: application/json" \
  -d '{"list":"blocked","address":"10.0.0.100","comment":"blocked host"}'

# List entries
curl -u admin: http://HOST:PORT/rest/ip/firewall/address-list
```

---

## Related Endpoints

| Path | Purpose |
|------|---------|
| `/ip/firewall/filter` | Firewall filter rules |
| `/ip/firewall/nat` | NAT rules |
| `/ip/firewall/mangle` | Packet marking |
| `/ip/firewall/raw` | Pre-connection-tracking filtering |
| `/ip/firewall/address-list` | Address lists |
| `/ip/firewall/connection` | Active connection tracking table (read-only) |
| `/ip/firewall/service-port` | NAT helpers (FTP, SIP, etc.) |

---

> **Source:**
> - Rosetta: pages 47579162 (REST API), 48660574 (Filter), 3211299 (NAT), 48660587 (Mangle), 250708064 (Common Firewall Matchers and Actions), 328513 (Building Advanced Firewall); property lookups for `chain`, `action`, `place-before` (not in property DB — documented in REST API page PUT section and CLI behavior)
> - Reference: `rest-api-patterns.md` — verb mapping (PUT=create, PATCH=set, GET=print)
> - Note: Response shapes derived from docs and REST API page examples, not lab-verified. Rule ordering behavior is well-documented in MikroTik docs and confirmed by default config structure.
> - Key gotcha source: Common agent mistake pattern observed across tikoci projects — agents PUT rules without `place-before`, placing them after drop-all rules where they have no effect.
