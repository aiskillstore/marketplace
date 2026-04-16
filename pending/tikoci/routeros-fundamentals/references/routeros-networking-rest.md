# RouterOS Networking REST API Reference

Response shapes derived from official docs (page IDs below). Not lab-verified on CHR unless stated.

## REST Verb Mapping (Quick Reminder)

| HTTP Verb | RouterOS Action | Notes |
|-----------|----------------|-------|
| `GET`     | print (list)   | Returns JSON array |
| `PUT`     | add (**create**) | NOT update — creates a new entry |
| `PATCH`   | set (update)   | Requires `/*ID` in URL path |
| `DELETE`  | remove         | Requires `/*ID` in URL path |
| `POST`    | command        | Actions like flush, release, renew |

See `rest-api-patterns.md` for full details, filtering, proplist, and auth patterns.

---

## 1. `/ip/address` — IP Address Management

Sub-menu: `/ip/address`
Docs: [IP Addressing](https://help.mikrotik.com/docs/spaces/ROS/pages/328247/IP+Addressing) (page 328247)

### Properties

| Property | Type | Default | RW | Description |
|----------|------|---------|-----|-------------|
| `address` | IP/netmask (e.g. `192.168.1.1/24`) | | RW | IPv4 address with CIDR netmask |
| `interface` | string | | RW | Interface to assign the address to |
| `network` | IP | auto-calculated | RW | Network address — auto-derived from `address` if omitted |
| `comment` | string | `""` | RW | Description |
| `disabled` | `"true"` / `"false"` | `"false"` | RW | Whether address is disabled |
| `actual-interface` | string | | RO | Resolved interface (e.g. bridge if port was bridged) |
| `dynamic` | `"true"` / `"false"` | | RO | Whether address was dynamically created (DHCP, etc.) |
| `invalid` | `"true"` / `"false"` | | RO | Whether address is invalid |
| `.id` | string (e.g. `*1`) | | RO | Internal ID for PATCH/DELETE |

### List addresses

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/address
```

Expected response:

```json
[
  {
    ".id": "*1",
    "address": "192.168.88.1/24",
    "network": "192.168.88.0",
    "interface": "ether1",
    "actual-interface": "ether1",
    "invalid": "false",
    "dynamic": "false",
    "disabled": "false"
  }
]
```

### Add an address (PUT = create)

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/address \
  -X PUT -H "Content-Type: application/json" \
  -d '{"address":"10.0.0.1/24","interface":"ether2"}'
```

Response (returns the new `.id`):

```json
{"ret":"*2"}
```

`network` is auto-calculated from `address` if not explicitly provided.

### Modify an address (PATCH)

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/address/*2 \
  -X PATCH -H "Content-Type: application/json" \
  -d '{"address":"10.0.0.2/24"}'
```

Response: `[]` (empty array = success)

### Remove an address (DELETE)

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/address/*2 \
  -X DELETE
```

Response: `[]`

### Filtering

```bash
# Only addresses on ether1
curl -s -u admin: 'http://127.0.0.1:9100/rest/ip/address?interface=ether1'

# Exclude dynamic addresses
curl -s -u admin: 'http://127.0.0.1:9100/rest/ip/address?dynamic=false'

# Select specific fields
curl -s -u admin: 'http://127.0.0.1:9100/rest/ip/address?.proplist=address,interface'
```

### Gotchas

- `actual-interface` differs from `interface` when the interface is a bridge port — the address moves to the bridge.
- Dynamic addresses (from DHCP client) appear with `dynamic=true` and cannot be edited via `/ip/address` PATCH.
- All boolean values are **strings** (`"true"`, `"false"`), not JSON booleans.

---

## 2. `/ip/route` — Static Routes

Sub-menu: `/ip/route`
Docs: [IP Routing](https://help.mikrotik.com/docs/spaces/ROS/pages/328084/IP+Routing) (page 328084)

### Key Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `dst-address` | IP/netmask | | Destination network (e.g. `0.0.0.0/0` for default) |
| `gateway` | IP or interface name | | Next-hop address or interface |
| `distance` | integer 0–255 | `1` | Administrative distance — lower wins |
| `routing-table` | string | `"main"` | Routing table to install the route in |
| `disabled` | `"true"` / `"false"` | `"false"` | |
| `scope` | integer | `30` | Used for recursive nexthop resolution |
| `target-scope` | integer | `10` | Target scope for nexthop lookup |
| `comment` | string | `""` | |
| `.id` | string | | Internal ID |

Read-only fields in GET: `dynamic`, `active`, `connect`, `static`, `immediate-gw`, etc.

### List routes

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/route
```

Expected response (mix of static and dynamic):

```json
[
  {
    ".id": "*4",
    "dst-address": "0.0.0.0/0",
    "gateway": "10.155.101.1",
    "distance": "1",
    "scope": "30",
    "target-scope": "10",
    "active": "true",
    "static": "true",
    "dynamic": "false",
    "disabled": "false"
  },
  {
    ".id": "*5",
    "dst-address": "10.155.101.0/24",
    "gateway": "ether12",
    "distance": "0",
    "active": "true",
    "connect": "true",
    "dynamic": "true"
  }
]
```

### Add a static route

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/route \
  -X PUT -H "Content-Type: application/json" \
  -d '{"dst-address":"10.10.0.0/16","gateway":"192.168.1.1","distance":"10"}'
```

### Add a default route

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/route \
  -X PUT -H "Content-Type: application/json" \
  -d '{"dst-address":"0.0.0.0/0","gateway":"10.0.0.1"}'
```

### Modify / Delete

```bash
# Change gateway
curl -s -u admin: http://127.0.0.1:9100/rest/ip/route/*4 \
  -X PATCH -H "Content-Type: application/json" \
  -d '{"gateway":"10.0.0.254"}'

# Remove
curl -s -u admin: http://127.0.0.1:9100/rest/ip/route/*4 -X DELETE
```

### Route Types

| Type | `dynamic` | `connect` / `static` | How created |
|------|-----------|----------------------|-------------|
| Connected | `"true"` | `connect=true` | Auto — from IP address on interface |
| Static | `"false"` | `static=true` | Manual — via `/ip/route add` |
| Dynamic | `"true"` | varies | From DHCP, OSPF, BGP, etc. |

**Cannot PATCH/DELETE dynamic or connected routes** — they are managed by their source protocol.

### Gotcha: `/routing/route` vs `/ip/route`

`/routing/route` is **read-only** and shows all routes (IPv4+IPv6) with extended fields. Use `/ip/route` for CRUD on IPv4 static routes.

---

## 3. `/ip/dhcp-client` — DHCP Client

Sub-menu: `/ip/dhcp-client`
Docs: [DHCP](https://help.mikrotik.com/docs/spaces/ROS/pages/24805500/DHCP) (page 24805500, section "DHCP Client")

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `interface` | string | | Interface to run DHCP client on |
| `add-default-route` | `yes` / `no` / `special-classless` | `yes` | Install default route from DHCP server |
| `use-peer-dns` | `yes` / `no` | `yes` | Accept DNS servers from DHCP |
| `use-peer-ntp` | `yes` / `no` | `yes` | Accept NTP servers from DHCP |
| `disabled` | `yes` / `no` | `yes` | **Note: default is disabled!** |
| `default-route-distance` | integer 0–255 | | Distance for auto-created default route |
| `comment` | string | | |

Read-only: `address`, `gateway`, `status`, `dhcp-server`, `primary-dns`, `secondary-dns`, `expires-after`

### Add DHCP client on an interface

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-client \
  -X PUT -H "Content-Type: application/json" \
  -d '{"interface":"ether1","disabled":"no"}'
```

Response: `{"ret":"*1"}`

**Important:** `disabled` defaults to `"yes"` — you must explicitly set `"disabled":"no"` or the client won't start.

### Check DHCP client status

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-client
```

```json
[
  {
    ".id": "*1",
    "interface": "ether1",
    "add-default-route": "yes",
    "use-peer-dns": "yes",
    "use-peer-ntp": "yes",
    "status": "bound",
    "address": "10.155.101.50/24",
    "gateway": "10.155.101.1",
    "dhcp-server": "10.155.101.1",
    "primary-dns": "10.155.0.1",
    "expires-after": "9m30s",
    "disabled": "false",
    "dynamic": "false"
  }
]
```

### Release / Renew (POST commands)

```bash
# Release lease
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-client/release \
  -X POST -H "Content-Type: application/json" \
  -d '{"numbers":"*1"}'

# Renew lease
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-client/renew \
  -X POST -H "Content-Type: application/json" \
  -d '{"numbers":"*1"}'
```

### Gotchas

- `add-default-route=special-classless` adds both classless routes (option 121) AND option 3 default route (MS-style behavior).
- The `status` field values: `bound`, `searching...`, `requesting...`, `rebinding...`, `error`, `stopped`.
- On a fresh CHR with QEMU user-mode networking, `ether1` typically has a DHCP client auto-created as a dynamic entry.

---

## 4. `/ip/dhcp-server` — DHCP Server Setup

Setting up a DHCP server requires **three components**: an address pool, a network definition, and the server itself.

### Step 1: Create an address pool (`/ip/pool`)

Sub-menu: `/ip/pool`
Docs: [IP Pools](https://help.mikrotik.com/docs/spaces/ROS/pages/129531938/IP+Pools) (page 129531938)

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/pool \
  -X PUT -H "Content-Type: application/json" \
  -d '{"name":"dhcp-pool","ranges":"192.168.1.100-192.168.1.200"}'
```

Pool properties:

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Pool name (referenced by DHCP server) |
| `ranges` | string | IP ranges: `from1-to1,from2-to2` |
| `next-pool` | string | Overflow pool when this one is full |

### Step 2: Create DHCP server network (`/ip/dhcp-server/network`)

Sub-menu: `/ip/dhcp-server/network`

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-server/network \
  -X PUT -H "Content-Type: application/json" \
  -d '{"address":"192.168.1.0/24","gateway":"192.168.1.1","dns-server":"8.8.8.8,8.8.4.4"}'
```

Network properties:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `address` | IP/netmask | | Network the server serves (e.g. `192.168.1.0/24`) |
| `gateway` | IP | `0.0.0.0` | Default gateway for clients |
| `dns-server` | string | | DNS servers (comma-separated). Falls back to router's `/ip/dns` if unset |
| `domain` | string | | DNS domain for clients |
| `ntp-server` | IP | | NTP server for clients |
| `netmask` | integer 0–32 | `0` | Override netmask (0 = use network prefix) |

### Step 3: Create the DHCP server (`/ip/dhcp-server`)

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-server \
  -X PUT -H "Content-Type: application/json" \
  -d '{"name":"dhcp1","interface":"ether2","address-pool":"dhcp-pool","lease-time":"1h","disabled":"no"}'
```

Server properties:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | string | | Server name |
| `interface` | string | | Interface to serve DHCP on |
| `address-pool` | string / `static-only` | `static-only` | IP pool name. `static-only` = only static leases |
| `lease-time` | time | `30m` | Lease duration (e.g. `1h`, `1d`) |
| `disabled` | `yes` / `no` | | |
| `authoritative` | `yes` / `no` / `after-2sec-delay` / `after-10sec-delay` | `yes` | How to handle unknown clients |

### Complete DHCP server setup (all 3 steps)

```bash
# Prerequisite: IP address must exist on the interface
curl -s -u admin: http://127.0.0.1:9100/rest/ip/address \
  -X PUT -H "Content-Type: application/json" \
  -d '{"address":"192.168.1.1/24","interface":"ether2"}'

# 1. Pool
curl -s -u admin: http://127.0.0.1:9100/rest/ip/pool \
  -X PUT -H "Content-Type: application/json" \
  -d '{"name":"dhcp-pool","ranges":"192.168.1.100-192.168.1.200"}'

# 2. Network
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-server/network \
  -X PUT -H "Content-Type: application/json" \
  -d '{"address":"192.168.1.0/24","gateway":"192.168.1.1","dns-server":"8.8.8.8"}'

# 3. Server
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-server \
  -X PUT -H "Content-Type: application/json" \
  -d '{"name":"dhcp1","interface":"ether2","address-pool":"dhcp-pool","lease-time":"1h","disabled":"no"}'
```

### View leases

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dhcp-server/lease
```

### Gotchas

- **`address-pool` defaults to `static-only`** — if you don't specify a pool, no dynamic leases are handed out.
- The interface must have an IP address in the same subnet as the pool/network.
- The DHCP server requires a **real interface** to receive raw ethernet packets. A bridge with no ports won't work.

---

## 5. `/ip/dns` — DNS Configuration

Sub-menu: `/ip/dns`
Docs: [DNS](https://help.mikrotik.com/docs/spaces/ROS/pages/37748767/DNS) (page 37748767)

`/ip/dns` is a **singleton** — it uses GET/PATCH (not array-based CRUD).

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `servers` | list of IPs | `""` | Static DNS server addresses |
| `allow-remote-requests` | `yes` / `no` | `no` | Act as DNS cache for clients |
| `cache-size` | integer (KiB) | `2048` | DNS cache size |
| `cache-max-ttl` | time | `1w` | Maximum cache TTL |
| `max-concurrent-queries` | integer | `100` | |
| `use-doh-server` | string | `""` | DoH server URL (overrides `servers`) |
| `dynamic-servers` | list of IPs | | RO — DNS servers from DHCP, etc. |
| `cache-used` | integer (KiB) | | RO — current cache usage |

### Get DNS settings

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dns
```

```json
{
  "allow-remote-requests": "false",
  "cache-max-ttl": "1w",
  "cache-size": "2048",
  "cache-used": "48",
  "dynamic-servers": "10.155.0.1",
  "max-concurrent-queries": "100",
  "max-concurrent-tcp-sessions": "20",
  "max-udp-packet-size": "4096",
  "query-server-timeout": "2s",
  "query-total-timeout": "10s",
  "servers": "",
  "use-doh-server": "",
  "verify-doh-cert": "false"
}
```

**Note:** `/ip/dns` returns a single **object** (not an array) — it's a singleton config, not an item list.

### Set DNS servers

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dns/set \
  -X POST -H "Content-Type: application/json" \
  -d '{"servers":"8.8.8.8,1.1.1.1","allow-remote-requests":"yes"}'
```

Response: `[]` (empty array = success)

### DNS Cache

```bash
# List cached entries
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dns/cache

# List ALL cached entries (including PTR)
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dns/cache/all

# Flush cache
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dns/cache/flush \
  -X POST -H "Content-Type: application/json" -d '{}'
```

### DNS Static entries

```bash
# Add a static DNS record
curl -s -u admin: http://127.0.0.1:9100/rest/ip/dns/static \
  -X PUT -H "Content-Type: application/json" \
  -d '{"name":"myhost.local","address":"192.168.1.50"}'
```

### Gotchas

- `servers` is for **static** DNS servers. `dynamic-servers` (read-only) shows servers acquired from DHCP etc.
- When `allow-remote-requests=yes`, the router acts as a DNS proxy — **add firewall rules** to restrict port 53 access.
- `set` is done via POST to `/ip/dns/set`, NOT via PATCH (because it's a singleton, not a list item).
- DoH (`use-doh-server`) overrides all `servers` entries when active.

---

## 6. `/interface` — Interface Listing

Sub-menu: `/interface`
Command tree: `/interface` (print, set, enable, disable, etc.)

### List all interfaces

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/interface
```

```json
[
  {
    ".id": "*1",
    "name": "ether1",
    "type": "ether",
    "mtu": "1500",
    "actual-mtu": "1500",
    "mac-address": "52:54:00:12:34:56",
    "running": "true",
    "disabled": "false",
    "dynamic": "false"
  },
  {
    ".id": "*2",
    "name": "ether2",
    "type": "ether",
    "mtu": "1500",
    "actual-mtu": "1500",
    "mac-address": "52:54:00:12:34:57",
    "running": "false",
    "disabled": "false",
    "dynamic": "false"
  }
]
```

### Key properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Interface name (e.g. `ether1`, `bridge1`, `vlan100`) |
| `type` | string | Interface type: `ether`, `bridge`, `vlan`, `veth`, `wireguard`, etc. |
| `running` | `"true"` / `"false"` | Whether interface has link |
| `disabled` | `"true"` / `"false"` | Administratively disabled |
| `mac-address` | string | MAC address |
| `mtu` | string | Configured MTU |
| `actual-mtu` | string | Effective MTU |
| `dynamic` | `"true"` / `"false"` | Dynamically created (e.g. PPP sessions) |

### Filter by type

```bash
# Only ethernet interfaces
curl -s -u admin: 'http://127.0.0.1:9100/rest/interface?type=ether'

# Only running interfaces
curl -s -u admin: 'http://127.0.0.1:9100/rest/interface?running=true'

# Specific fields only
curl -s -u admin: 'http://127.0.0.1:9100/rest/interface?.proplist=name,type,running'
```

### Enable / Disable an interface

```bash
# Disable ether2
curl -s -u admin: http://127.0.0.1:9100/rest/interface/*2 \
  -X PATCH -H "Content-Type: application/json" \
  -d '{"disabled":"true"}'

# Or use the command form
curl -s -u admin: http://127.0.0.1:9100/rest/interface/disable \
  -X POST -H "Content-Type: application/json" \
  -d '{"numbers":"*2"}'
```

### Rename an interface

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/interface/*1 \
  -X PATCH -H "Content-Type: application/json" \
  -d '{"name":"wan"}'
```

### Gotchas

- `/interface` is a **unified view** — it shows all interface types. Use type-specific sub-menus (`/interface/ethernet`, `/interface/bridge`, `/interface/vlan`) for type-specific properties.
- `running` is a link-state indicator, not admin state. An enabled but disconnected interface has `running=false`, `disabled=false`.
- On a fresh CHR, you typically get `ether1` through `etherN` matching the number of QEMU NICs configured.
- `monitor-traffic` is an async command (POST) — see `rest-api-patterns.md` for async handling.

---

## Common Patterns for Agents

### Verify interface has IP before configuring services

```bash
# Check that ether2 has an address
curl -s -u admin: 'http://127.0.0.1:9100/rest/ip/address?interface=ether2'
# If empty array → add one first
```

### Quick network setup sequence

```
1. GET  /rest/interface                              → find available interfaces
2. PUT  /rest/ip/address  {address, interface}       → assign IP
3. PUT  /rest/ip/route    {dst-address, gateway}     → add default route (if no DHCP)
4. POST /rest/ip/dns/set  {servers}                  → configure DNS
```

### Post-boot REST race applies here too

All networking endpoints can return stale/wrong data briefly after boot. Use the polling pattern from `rest-api-patterns.md` — check for expected keys before trusting the response.

---

> **Source:**
> - Rosetta page IDs: 328247 (IP Addressing), 328084 (IP Routing), 24805500 (DHCP), 37748767 (DNS), 129531938 (IP Pools)
> - Rosetta property lookups: `actual-interface`, `add-default-route`, `use-peer-dns`, `use-peer-ntp`, `address-pool`, `allow-remote-requests`, `servers`
> - Rosetta command trees: `/ip/address`, `/ip/route`, `/ip/dhcp-client`, `/ip/dhcp-server`, `/ip/dhcp-server/network`, `/ip/dns`, `/ip/dns/cache`, `/ip/pool`, `/interface`
> - Reference: `rest-api-patterns.md` — verb mapping, filtering, auth
> - Note: Response shapes are from docs, not lab-verified on CHR
