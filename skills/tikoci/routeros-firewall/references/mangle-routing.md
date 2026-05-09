# Mangle and Policy Routing

RouterOS mangle chains and routing marks for policy-based routing. Referenced from `routeros-firewall` SKILL.md.

## Routing Tables

Policy routing requires a dedicated routing table. In RouterOS v7:

```routeros
# Create the routing table (fib = Forward Information Base, required)
/routing/table/add name=vpn-mark fib
```

The `fib` keyword is required — it pushes resolved routes to the kernel FIB.

## mark-routing in Mangle Prerouting

Mark packets in `prerouting` to assign them to an alternate routing table:

```routeros
/ip/firewall/mangle/add chain=prerouting \
  src-address=10.20.0.0/24 \
  action=mark-routing new-routing-mark=vpn-mark passthrough=yes \
  comment="mypolicy-mark-clients"
```

`passthrough=yes` — evaluation continues to the next mangle rule after marking.

The marked routing table applies when RouterOS makes the routing decision for the packet.

## Exempt DNS from Policy Routing

DNS must reach the local router, not the alternate gateway. Add the DNS exemption rule **before** the mark-routing rule:

```routeros
# DNS exempt — MUST be before the mark-routing rule
/ip/firewall/mangle/add chain=prerouting \
  src-address=10.20.0.0/24 protocol=udp port=53 \
  action=accept comment="mypolicy-exempt-dns"

# Mark remaining traffic
/ip/firewall/mangle/add chain=prerouting \
  src-address=10.20.0.0/24 \
  action=mark-routing new-routing-mark=vpn-mark passthrough=yes \
  comment="mypolicy-mark-clients"
```

Rule order is critical — DNS exempt must come first (see SKILL.md Rule Ordering section).

## `hotspot=auth` Matcher

RouterOS hotspot adds a `hotspot=` property to mangle — matches only packets from authenticated hotspot clients:

```routeros
# Only route AUTHENTICATED hotspot clients through the alternate gateway
# Unauthenticated clients (pre-login) are not affected
/ip/firewall/mangle/add chain=prerouting \
  src-address=10.20.0.0/24 hotspot=auth \
  action=mark-routing new-routing-mark=vpn-mark passthrough=yes \
  comment="mypolicy-mark-authed"
```

Valid `hotspot=` values: `auth` (authenticated clients), `from-client`, `local-dst`, `http`.

## Generic Policy Routing Pattern

Complete minimal pattern — route traffic from one subnet through an alternate gateway:

```routeros
# 1. Routing table
/routing/table/add name=vpn-mark fib

# 2. DNS exempt (before mark rule)
/ip/firewall/mangle/add chain=prerouting \
  src-address=10.20.0.0/24 protocol=udp port=53 \
  action=accept comment="mypolicy-exempt-dns-udp"
/ip/firewall/mangle/add chain=prerouting \
  src-address=10.20.0.0/24 protocol=tcp port=53 \
  action=accept comment="mypolicy-exempt-dns-tcp"

# 3. Mark traffic (authenticated hotspot clients only)
/ip/firewall/mangle/add chain=prerouting \
  src-address=10.20.0.0/24 hotspot=auth \
  action=mark-routing new-routing-mark=vpn-mark passthrough=yes \
  comment="mypolicy-mark"

# 4. NAT for alternate gateway outbound
/ip/firewall/nat/add chain=srcnat action=masquerade \
  out-interface=my-gateway-interface place-before=0 \
  comment="mypolicy-nat"

# 5. Route (start DISABLED — enable after gateway interface is up)
/ip/route/add dst-address=0.0.0.0/0 gateway=my-gateway-interface \
  routing-table=vpn-mark distance=1 disabled=yes

# Enable after gateway is configured:
# /ip/route/enable [find routing-table=vpn-mark]
```

## MSS Clamping

VPN interfaces often have a lower MTU than the WAN interface. Clamp TCP MSS to prevent fragmentation:

```routeros
/ip/firewall/mangle/add chain=forward \
  action=change-mss new-mss=1360 \
  protocol=tcp tcp-flags=syn out-interface=my-gateway-interface \
  place-before=0 passthrough=yes \
  comment="mypolicy-mss-clamp"
```

## FastTrack Interaction

FastTrack bypasses mangle entirely for fast-pathed flows. If a connection is fasttracked, mangle rules (including `mark-routing`) are not applied. Do not combine `fasttrack-connection` with mangle-based policy routing on the same traffic.
