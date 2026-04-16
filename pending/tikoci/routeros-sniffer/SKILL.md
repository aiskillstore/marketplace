---
name: routeros-sniffer
description: "RouterOS packet capture and TZSP streaming for protocol debugging. Use when: capturing packets on RouterOS, setting up /tool/sniffer, streaming live traffic via TZSP, using firewall mangle action=sniff-tzsp, debugging network protocols on MikroTik, receiving TZSP with Wireshark or tshark, saving pcap files from RouterOS, or when the user mentions packet sniffer, TZSP, sniff-tzsp, /tool/sniffer, or packet capture on RouterOS."
---

# RouterOS Packet Capture & TZSP Streaming

RouterOS has a built-in packet sniffer (`/tool/sniffer`) and firewall mangle actions that can mirror traffic — either saving to a file on the router or streaming live to a remote host via TZSP (TaZmen Sniffer Protocol). This is the primary way to capture packets on RouterOS since standard tools like `tcpdump` do not exist (see `routeros-fundamentals` skill).

## Why This Matters for Agents

When debugging any network protocol issue on RouterOS, agents should know they can:
1. **Stream live packets** from the router to the host machine via TZSP — no hardware needed if using a CHR VM
2. **Save pcap/pcapng files** on the router's flash and download them for analysis
3. **Use firewall mangle rules** for surgical, per-flow packet mirroring without touching the sniffer config

Combined with a QEMU CHR instance (see `routeros-qemu-chr` skill), this gives agents a complete packet-level debugging workflow with zero physical hardware.

## Method 1: /tool/sniffer (Full Capture Tool)

The built-in sniffer captures packets on specified interfaces with extensive filtering. It supports **three independent output modes** that can be combined:

| Output | Setting | Notes |
|--------|---------|-------|
| Memory buffer | (always on) | Viewable via `quick`, `packet`, `protocol`, `host`, `connection` submenus. Packets available for 10 minutes |
| File on flash | `file-name=capture.pcap` | PCAPNG format since RouterOS 7.20 |
| TZSP stream | `streaming-enabled=yes` | UDP to `streaming-server` on `streaming-port` (default 37008) |

### Live TZSP Streaming

```routeros
# Configure sniffer to stream via TZSP to a remote host
/tool/sniffer
set streaming-enabled=yes streaming-server=<RECEIVER-IP>:37008

# Optional: filter to a specific interface or protocol
set filter-interface=ether1
set filter-ip-protocol=icmp

# Start capture (runs until stopped or router reboots)
/tool/sniffer/start

# Stop when done
/tool/sniffer/stop
```

The receiver host runs Wireshark, tshark, or another TZSP-capable tool (see [TZSP receivers reference](./references/tzsp-receivers.md)).

### File-Based Capture

```routeros
# Capture to file on router flash
/tool/sniffer
set file-name=capture.pcap filter-interface=ether1

/tool/sniffer/start
# ... let it capture ...
/tool/sniffer/stop

# Or save the memory buffer to a file manually
/tool/sniffer/save file-name=/flash/debug.pcap

# Download via SCP or fetch
# From the host:
# scp admin@<ROUTER-IP>:/flash/debug.pcap .
```

File + streaming can run simultaneously:
```routeros
/tool/sniffer
set file-name=capture.pcap streaming-enabled=yes streaming-server=<RECEIVER-IP>:37008
/tool/sniffer/start
```

### Quick Mode (Interactive CLI)

For quick one-off inspection directly on the router console:

```routeros
# Quick-capture ICMP traffic on ether1
/tool/sniffer/quick ip-protocol=icmp interface=ether1
```

This shows a live scrolling table on the console with source/dest MAC, IP, protocol, and size.

### Sniffer Filter Properties

Key filter options for `/tool/sniffer/set`:

| Property | Description |
|----------|-------------|
| `filter-interface` | Interface name or `all` (default: `all`) |
| `filter-ip-address` | Up to 16 IP/mask entries |
| `filter-dst-ip-address` | Up to 16 destination IP/mask entries |
| `filter-src-ip-address` | Up to 16 source IP/mask entries |
| `filter-port` | Up to 16 ports (supports `!` negation) |
| `filter-ip-protocol` | Up to 16 protocols (tcp, udp, icmp, etc.) |
| `filter-mac-protocol` | Up to 16 MAC protocols (ip, arp, ipv6, vlan, etc.) |
| `filter-direction` | `any`, `rx`, or `tx` |
| `filter-stream` | `yes`/`no` — filter out sniffer's own TZSP packets (default: yes) |
| `filter-vlan` | Up to 16 VLAN IDs |
| `memory-limit` | Memory buffer size (default: 100 KiB) |
| `file-limit` | Max file size (default: 1000 KiB) |
| `only-headers` | Save only packet headers, not full payload |

**Important:** `filter-stream=yes` (default) excludes the sniffer's own TZSP stream packets from the capture — leave this on to avoid feedback loops.

## Method 2: Firewall Mangle (Targeted Mirroring)

Firewall mangle rules offer **granular per-flow mirroring** using the full firewall matcher. Two sniff-related actions exist:

### action=sniff-tzsp (Stream to Remote TZSP Receiver)

Mirrors matching packets as TZSP to a remote host. Uses the firewall's full matching engine (src/dst address, protocol, port, connection state, interface, etc.):

```routeros
# Mirror all forwarded ICMP to a TZSP receiver
/ip/firewall/mangle
add action=sniff-tzsp chain=forward protocol=icmp \
    sniff-target=<RECEIVER-IP> sniff-target-port=37008 \
    comment="TZSP mirror ICMP to Wireshark"

# Mirror traffic from a specific host
/ip/firewall/mangle
add action=sniff-tzsp chain=forward src-address=192.168.88.100 \
    sniff-target=<RECEIVER-IP> sniff-target-port=37008

# Mirror DNS queries
/ip/firewall/mangle
add action=sniff-tzsp chain=forward protocol=udp dst-port=53 \
    sniff-target=<RECEIVER-IP> sniff-target-port=37008
```

Properties for `sniff-tzsp`:
- `sniff-target` (IP) — destination IP for the TZSP UDP packets
- `sniff-target-port` (port, default 37008) — destination UDP port
- `sniff-id` — optional identifier tag

**Key behavior:** `sniff-tzsp` acts like `passthrough` — after matching, the packet continues to the next mangle rule. The original packet is NOT modified or dropped; only a copy is sent as TZSP.

### Mangle vs /tool/sniffer: When to Use Which

| Scenario | Use |
|----------|-----|
| Capture all traffic on an interface | `/tool/sniffer` |
| Mirror specific flows (by IP, port, protocol) | Mangle `sniff-tzsp` |
| Save pcap file on router flash | `/tool/sniffer` with `file-name` |
| Stream live to Wireshark/tshark | Either — `/tool/sniffer` with `streaming-enabled` or mangle `sniff-tzsp` |
| Multiple independent mirrors to different receivers | Mangle rules (one per target) |
| Quick interactive CLI view | `/tool/sniffer/quick` |

## TZSP Protocol Overview

TZSP is a simple UDP encapsulation — the router wraps the original Ethernet frame in a TZSP header and sends it as a UDP datagram:

```
UDP (port 37008) → TZSP header (4 bytes) → tags (variable) → TAG_END → original Ethernet frame
```

- **Default port:** 37008 (`0x9090`) — not IANA-registered but the RouterOS/Wireshark standard
- **Encapsulation:** Typically Ethernet (type 1); 802.11 for wireless captures
- **Tags:** Optional metadata (WLAN signal strength, channel, etc.); Ethernet captures usually have no tags
- **Keepalives:** Type 4 (Null) packets sent periodically — no inner frame, filter these when processing

## CHR Testing Pattern

A QEMU CHR instance provides a complete packet capture lab with zero hardware. The free CHR license has a **1 Mbps speed limit** but this is sufficient for protocol debugging and sniffer testing.

```sh
# 1. Boot a CHR instance with port forwarding for REST API and SSH
qemu-system-x86_64 -M q35 -m 256 \
  -drive file=chr.img,format=raw,if=virtio \
  -netdev user,id=net0,hostfwd=tcp::9180-:80,hostfwd=tcp::9122-:22 \
  -device virtio-net-pci,netdev=net0 \
  -display none -serial stdio

# 2. Configure sniffer via REST API once booted
curl -u admin: -X POST http://<router-ip>/rest/tool/sniffer/set \
  -H 'Content-Type: application/json' \
  -d '{"streaming-enabled":"yes","streaming-server":"10.0.2.2:37008"}'

# 3. Start capture
curl -u admin: -X POST http://<router-ip>/rest/tool/sniffer/start

# 4. Listen for TZSP on the host
tshark -i any -f "udp port 37008" -O tzsp

# 5. Generate test traffic (e.g., ping from the CHR)
curl -u admin: -X POST http://<router-ip>/rest/ping \
  -H 'Content-Type: application/json' \
  -d '{"address":"8.8.8.8","count":"3"}'
```

**QEMU user-mode networking note:** The CHR's default gateway (10.0.2.2) is the host. Use this IP as `streaming-server` when using QEMU `-netdev user`. The host must listen on all interfaces (or 10.0.2.2 specifically) to receive the TZSP packets.

For full QEMU setup details, see the `routeros-qemu-chr` skill. For CHR licensing details (free tier, 60-day trial, speed limits), see [CHR licensing](../routeros-qemu-chr/references/chr-licensing.md).

## Gotchas

- **Hardware-offloaded bridge traffic** is NOT visible to the sniffer — only flooded packets (unknown unicast, broadcast, multicast) may appear
- **Wireless client-to-client** unicast with forwarding enabled is NOT visible
- **Sniffed packets in memory expire after 10 minutes** — save to file or use streaming for persistent capture
- **PCAPNG format** (RouterOS 7.20+) is the default for saved files — older tools may need PCAP
- **`filter-stream=yes`** (default) is important — without it, the sniffer captures its own TZSP stream packets, creating a feedback loop
- **1 Mbps CHR speed limit** may cause "slow" captures — this is the free license limit, not a sniffer issue. See [CHR licensing](../routeros-qemu-chr/references/chr-licensing.md)
- **`file-limit` should not exceed free memory** — the router may crash or behave unexpectedly

## Cleanup

Always clean up sniffer config and mangle rules after debugging:

```routeros
# Stop sniffer
/tool/sniffer/stop

# Reset sniffer config to defaults
/tool/sniffer
set streaming-enabled=no streaming-server=0.0.0.0 file-name=""

# Remove mangle rules (find by comment)
/ip/firewall/mangle/remove [find comment~"TZSP"]
```

## Additional Resources

**Reference files:**
- For TZSP receiver setup (Wireshark, tshark, tcpdump): see [TZSP receivers reference](./references/tzsp-receivers.md)

**Related skills:**
- For QEMU CHR setup and boot patterns: see `routeros-qemu-chr` skill
- For CHR licensing (free tier, 60-day trial, speed limits): see `routeros-qemu-chr` skill
- For RouterOS CLI/REST basics: see `routeros-fundamentals` skill
- For the `/console/inspect` command tree: see `routeros-command-tree` skill

**MCP tools:**
- For RouterOS docs lookup: use the `rosetta` MCP server tools (`routeros_search`, `routeros_get_page`)
