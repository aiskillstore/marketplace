---
name: routeros-mndp
description: "MNDP (MikroTik Neighbor Discovery Protocol) wire format, behavior, and RouterOS /ip/neighbor integration. Use when: implementing MNDP discovery, parsing MNDP packets, working with /ip/neighbor, understanding WinBox device discovery, debugging why a router doesn't appear in neighbor lists, or when the user mentions MNDP, neighbor discovery, WinBox discovery, or /ip/neighbor."
---

# MNDP — MikroTik Neighbor Discovery Protocol

MNDP is the UDP broadcast/multicast protocol that RouterOS uses for automatic device
discovery on the local network. It is the same protocol WinBox uses to find routers.
Every RouterOS device participates by default.

## Why This Matters for Agents

- **`/ip/neighbor`** on RouterOS is the CLI/REST surface for MNDP results
- WinBox's "Neighbors" tab is an MNDP listener
- Any agent implementing device discovery for MikroTik equipment needs MNDP
- The protocol is simple enough to implement from scratch — no library needed

## Protocol Basics

| Property | Value |
|----------|-------|
| Transport | UDP |
| Port | 5678 |
| IPv4 | Broadcast to 255.255.255.255:5678 |
| IPv6 | Multicast to ff02::1 (all-nodes link-local) |
| Direction | Bidirectional — same port for send and receive |
| Authentication | None — read-only discovery, no credentials |
| Scope | Layer 2 broadcast domain (does not cross routers) |

## How Discovery Works

1. **Listener sends a refresh packet** — a 9-byte UDP datagram to 255.255.255.255:5678
2. **All RouterOS devices on the LAN reply** — each sends a TLV-encoded announcement with identity, version, board, MAC, IP, uptime, etc.
3. **Replies arrive asynchronously** — devices respond within milliseconds to seconds depending on network conditions
4. **RouterOS devices also announce periodically** (~60s cycle) without being prompted — passive listening works but is slow to populate

### Refresh Packet (Discovery Request)

A 9-byte packet that triggers immediate replies from all RouterOS devices on the broadcast domain:

```
Offset  Length  Value       Field
0       2       0x0000      type (MNDP)
2       2       0x0000      sequence number (0 for request)
4       2       0x0000      TLV type (none)
6       2       0x0000      TLV length (none)
8       1       0x00        padding
```

As raw bytes: `00 00 00 00 00 00 00 00 00`

### Response Packet

```
Offset  Length  Field
0       2       type = 0x0000 (MNDP)
2       2       sequence number (monotonically increasing per device)
4+      TLV[]   zero or more TLV records (see below)
```

## TLV Format

Each TLV (Type-Length-Value) record in the response:

```
Offset  Length  Field
0       2       type   (little-endian uint16)
2       2       length (little-endian uint16) — byte count of value
4       N       value  (raw bytes — interpretation depends on type)
```

**Byte order:** TLV type and length are little-endian. Value encoding varies by type.

### TLV Type Reference

| Type | Hex    | Name           | Value Format | Notes |
|------|--------|----------------|-------------|-------|
| 1    | 0x0001 | MAC Address    | 6 bytes, big-endian | Per-interface MAC, not chassis MAC |
| 5    | 0x0005 | Identity       | UTF-8 string | Hostname — same across all interfaces |
| 7    | 0x0007 | Version        | UTF-8 string | e.g. `7.18 (stable)`, `7.22rc1` |
| 8    | 0x0008 | Platform       | UTF-8 string | Usually `MikroTik` |
| 10   | 0x000a | Board          | UTF-8 string | e.g. `RB4011iGS+5HacQ2HnD`, `CHR` |
| 11   | 0x000b | Uptime         | 4 bytes LE uint32 | Seconds since boot |
| 12   | 0x000c | Software ID    | UTF-8 string | License identifier |
| 13   | 0x000d | Board (alt)    | UTF-8 string | Some firmware uses type 13 instead of 10 |
| 14   | 0x000e | Unpack         | 1 byte | Firmware compression flag |
| 15   | 0x000f | IPv6 Address   | 16 bytes | Link-local or global IPv6 |
| 16   | 0x0010 | Interface Name | UTF-8 string | Sending interface on the router (e.g. `ether1`) |
| 17   | 0x0011 | IPv4 Address   | 4 bytes, big-endian | IP of the sending interface |

**Board name:** Some firmware versions use TLV type 10, others use type 13. Parsers should handle both — prefer type 10 if both are present.

## Multi-Interface Behavior

A RouterOS device with N active interfaces sends **N separate MNDP announcements** — one per interface. Each announcement has:
- A **different MAC address** (the interface's own MAC)
- A **different interface name** (TLV 16)
- A **different IP address** (if assigned)
- The **same identity** (hostname)

This is expected behavior, not a bug. When displaying results, **group by identity** to avoid showing the same router N times. Use MAC address to disambiguate when the identity is the factory default (`MikroTik`).

## Timing and Reliability

| Scenario | Expected Response Time |
|----------|----------------------|
| Local LAN (wired) | 1-3 seconds |
| WiFi / congested network | 3-10 seconds |
| ZeroTier / tunnel overlay | 5-20 seconds |
| Satellite / high-latency | 10-30 seconds |

**Best practice:** Send multiple refresh packets during the listen window (every 5 seconds, matching WinBox behavior). Devices that miss the first broadcast due to packet loss, WiFi power-save, or tunnel relay latency will respond to subsequent refreshes.

**Never interpret missing devices as offline.** A short scan window produces partial results. Increase the timeout before concluding a device is unreachable.

## RouterOS /ip/neighbor

`/ip/neighbor` is the RouterOS-side view of MNDP (and CDP/LLDP) discovery results. It shows what the router has heard from other devices on its directly-connected networks.

```routeros
# Print discovered neighbors
/ip/neighbor/print

# Columns: interface, address, mac-address, identity, platform, version, board
```

### /ip/neighbor/discovery-settings

Controls which interfaces participate in neighbor discovery:

```routeros
# Show current discovery settings
/ip/neighbor/discovery-settings/print

# Disable MNDP on a specific interface (security hardening)
/interface/list/member/add list=no-mndp interface=ether1
/ip/neighbor/discovery-settings/set discover-interface-list=!no-mndp

# Supported protocols (can be combined)
# cdp — Cisco Discovery Protocol
# lldp — Link Layer Discovery Protocol
# mndp — MikroTik Neighbor Discovery Protocol
/ip/neighbor/discovery-settings/set protocol=mndp,lldp
```

### REST API Access

```sh
# List neighbors via REST
curl -u admin: http://<router-ip>/rest/ip/neighbor

# Response is JSON array with the same fields as CLI print
```

### Security Considerations

- MNDP has **no authentication** — any device on the broadcast domain can discover routers
- Disable MNDP on untrusted interfaces (public-facing, guest networks)
- RouterOS defaults to discovery on all interfaces — review and restrict
- MNDP reveals: identity (hostname), version, board model, IPs, MACs, uptime
- This information is useful for attackers — treat MNDP like an open SNMP community

## Socket Implementation Notes

### Port Sharing (SO_REUSEPORT)

MNDP uses the **same port (5678) for both sending and receiving**. If another process (e.g., WinBox) already has UDP/5678 bound, your listener needs `SO_REUSEPORT` to coexist:

```typescript
// Node.js / Bun dgram
import { createSocket } from "node:dgram";
const sock = createSocket({ type: "udp4", reuseAddr: true, reusePort: true });
sock.bind(5678, "0.0.0.0", () => {
  sock.setBroadcast(true);
});
```

```c
// C / POSIX
int opt = 1;
setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt));
```

**Platform note:** `SO_REUSEPORT` works on macOS and Linux. On Windows, `SO_REUSEADDR` alone may be sufficient. In Bun, `reusePort: true` requires Bun >= 1.3.11 (earlier versions silently ignored it on macOS).

### Self-Echo Filtering

When you send a broadcast to 255.255.255.255:5678, the OS delivers a copy back to your own socket. Filter out packets from your own IP addresses to avoid processing your own refresh as a neighbor response. The looped-back packet will have no MNDP TLVs (it's your 9-byte refresh, not a device announcement).

### IPv6 Multicast

IPv6 MNDP uses `ff02::1` (all-nodes multicast). Less commonly used than IPv4 broadcast but supported:

```typescript
sock.addMembership("ff02::1");
```

IPv6 link-local addresses include a zone ID (e.g., `fe80::1%en0`) that identifies the receiving interface — useful topology information not available in IPv4.

## Parsing Example (TypeScript)

```typescript
function parseMndpResponse(buf: Buffer): Record<string, string | number> {
  const view = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  let offset = 4; // skip 2-byte type + 2-byte sequence
  const fields: Record<string, string | number> = {};

  while (offset + 4 <= buf.length) {
    const tlvType = view.getUint16(offset, true);     // little-endian
    const tlvLen  = view.getUint16(offset + 2, true);  // little-endian
    offset += 4;

    if (offset + tlvLen > buf.length) break; // malformed
    const value = buf.subarray(offset, offset + tlvLen);

    switch (tlvType) {
      case 1:  // MAC Address — 6 bytes big-endian
        fields.macAddress = [...value].map(b => b.toString(16).padStart(2, "0")).join(":");
        break;
      case 5:  fields.identity = value.toString("utf8"); break;
      case 7:  fields.version = value.toString("utf8"); break;
      case 8:  fields.platform = value.toString("utf8"); break;
      case 10: // Board (primary)
      case 13: // Board (alternate — some firmware)
        if (!fields.board) fields.board = value.toString("utf8");
        break;
      case 11: // Uptime — 4 bytes LE uint32 (seconds)
        fields.uptime = view.getUint32(offset - tlvLen, true);
        break;
      case 12: fields.softwareId = value.toString("utf8"); break;
      case 15: // IPv6 — 16 bytes
        fields.ipv6 = formatIpv6(value);
        break;
      case 16: fields.interfaceName = value.toString("utf8"); break;
      case 17: // IPv4 — 4 bytes big-endian
        fields.ipv4 = `${value[0]}.${value[1]}.${value[2]}.${value[3]}`;
        break;
    }
    offset += tlvLen;
  }
  return fields;
}
```

## Reference Implementations

| Language | Source | Notes |
|----------|--------|-------|
| Go | github.com/middelink/mikrotik-fwupdate | Used as protocol ground truth during original research |
| Elixir | hex.pm mndp package | Confirms TLV type IDs |
| C | Various open-source MNDP clients | Direct setsockopt for REUSEPORT |
| Swift | Open-source macOS implementations | Confirms big-endian MAC encoding |

## Related Skills

- For RouterOS CLI/REST basics: see `routeros-fundamentals` skill
- For the `/console/inspect` command tree: see `routeros-command-tree` skill
- For packet capture and TZSP streaming: see `routeros-sniffer` skill
- For QEMU CHR setup (testing without hardware): see `routeros-qemu-chr` skill

## Related MCP Tools

- For RouterOS docs lookup: use the `rosetta` MCP server tools (`routeros_search`, `routeros_get_page`)
