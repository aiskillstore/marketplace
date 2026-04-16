# TZSP Receivers — Host-Side Setup

How to receive and decode TZSP packets from RouterOS on the host machine (macOS, Linux, or Windows).

## Wireshark (GUI)

Wireshark natively decodes TZSP. No plugins needed.

### Capture Filter (recommended)

To see ONLY TZSP traffic and avoid noise:

```
udp port 37008
```

Apply this as a **capture filter** (not display filter) before starting capture. This matches the default RouterOS TZSP port.

### Display Filter

If capturing all traffic, use a display filter:

```
tzsp
```

Or to see the inner decoded protocol:

```
tzsp && ip.addr == 192.168.88.100
```

### What You See

Wireshark decodes the TZSP header and shows the **inner encapsulated frame** as if it were captured locally. You see full Ethernet → IP → TCP/UDP/ICMP layers. The TZSP wrapper is visible in the packet details pane under "TZSP".

## tshark (CLI — Recommended for Agents)

`tshark` is the CLI version of Wireshark. Best option for agents because output is text and can be piped/parsed.

### Basic Live Capture

```sh
# Listen for TZSP on all interfaces
tshark -i any -f "udp port 37008" -O tzsp

# Compact one-line-per-packet output (like tcpdump)
tshark -i any -f "udp port 37008"

# Decode and show specific fields
tshark -i any -f "udp port 37008" \
  -T fields -e frame.time_relative -e ip.src -e ip.dst -e _ws.col.Protocol -e _ws.col.Info
```

### Capture to File

```sh
# Save raw TZSP packets to pcap
tshark -i any -f "udp port 37008" -w /tmp/tzsp-capture.pcap

# Read back later
tshark -r /tmp/tzsp-capture.pcap -O tzsp
```

### Time-Limited Capture

```sh
# Capture for 30 seconds then stop
tshark -i any -f "udp port 37008" -a duration:30

# Capture 100 packets then stop
tshark -i any -f "udp port 37008" -c 100
```

### Filtering Inner Protocol

```sh
# Show only ICMP packets inside TZSP
tshark -i any -f "udp port 37008" -Y "icmp"

# Show only HTTP inside TZSP
tshark -i any -f "udp port 37008" -Y "http"

# Show only DNS inside TZSP
tshark -i any -f "udp port 37008" -Y "dns"
```

### Installation

```sh
# macOS
brew install wireshark   # installs both wireshark and tshark

# Ubuntu/Debian
sudo apt install tshark

# Verify
tshark --version
```

## tcpdump (Minimal — No TZSP Decode)

`tcpdump` can capture the raw UDP packets but does NOT decode the TZSP encapsulation. It sees the outer UDP datagram, not the inner frame. Still useful for verifying packets are arriving.

```sh
# Verify TZSP packets are arriving
tcpdump -i any udp port 37008 -c 10

# Save to file for later analysis with tshark/Wireshark
tcpdump -i any udp port 37008 -w /tmp/tzsp-raw.pcap
```

Use `tshark` or Wireshark to actually decode the captured file.

## QEMU CHR + TZSP: Network Path

When using QEMU user-mode networking (`-netdev user`), the network path for TZSP is:

```
CHR (guest) → QEMU NAT (10.0.2.2) → host loopback/interface → tshark/Wireshark
```

Key details:
- The CHR sees `10.0.2.2` as its default gateway — this is the host from the guest's perspective
- Configure `streaming-server=10.0.2.2:37008` on the CHR
- Listen on the host with `tshark -i any -f "udp port 37008"`
- The `any` interface is important — QEMU user-mode forwards through a TAP-like internal interface

### Example End-to-End

```sh
# Terminal 1: Start tshark listener
tshark -i any -f "udp port 37008"

# Terminal 2: Configure CHR via REST API
curl -u admin: -X POST http://<router-ip>/rest/tool/sniffer/set \
  -H 'Content-Type: application/json' \
  -d '{"streaming-enabled":"yes","streaming-server":"10.0.2.2:37008"}'
curl -u admin: -X POST http://<router-ip>/rest/tool/sniffer/start

# Terminal 2: Generate traffic
curl -u admin: -X POST http://<router-ip>/rest/ping \
  -H 'Content-Type: application/json' \
  -d '{"address":"8.8.8.8","count":"5"}'

# Terminal 1 should show decoded ICMP packets
```

## Port Conflicts

If port 37008 is already in use (e.g., another capture session), use a different port on both sides:

```routeros
# RouterOS: use port 37009
/tool/sniffer/set streaming-server=<RECEIVER-IP>:37009 streaming-port=37009
```

```sh
# Host: listen on matching port
tshark -i any -f "udp port 37009"
```

## Firewall Considerations (Host)

The host firewall must allow incoming UDP on the TZSP port:

```sh
# macOS — no firewall changes needed for loopback (QEMU user-mode)
# For remote RouterOS hardware, allow in System Preferences > Security > Firewall

# Linux (ufw)
sudo ufw allow 37008/udp

# Linux (iptables)
sudo iptables -A INPUT -p udp --dport 37008 -j ACCEPT
```
