---
name: routeros-firewall
description: "RouterOS firewall filter, NAT, mangle, and address-list configuration. Use when: writing firewall rules in RouterOS, configuring NAT, setting up address-lists or interface-lists, writing idempotent firewall scripts, configuring DNS redirect or port forwarding, or when the user mentions /ip/firewall, chain=forward, chain=input, connection-state, address-list, interface-list, or layer7-protocol on MikroTik."
---

# RouterOS Firewall

## Rule Ordering — Sequential, Not Priority-Based

Rules are evaluated **top-to-bottom** — first match wins. This is the biggest source of iptables confusion.

- `place-before=0` inserts at the top; default `add` appends at the bottom
- An `action=accept` rule must appear BEFORE any `action=drop` for the same traffic
- **Non-terminal actions do NOT stop evaluation:** `action=add-src-to-address-list`, `action=add-dst-to-address-list`, `action=log`, and any rule with `passthrough=yes` continue to the next rule. A `drop` rule below an `add-src-to-address-list` will still fire.

```routeros
# WRONG — drop fires before accept can match
/ip/firewall/filter/add chain=input action=drop
/ip/firewall/filter/add chain=input src-address=10.0.0.1 action=accept

# CORRECT — accept first, drop catches the rest
/ip/firewall/filter/add chain=input src-address=10.0.0.1 action=accept place-before=0
/ip/firewall/filter/add chain=input action=drop
```

## Address-Lists as Dynamic Selectors

LLMs rarely suggest this pattern — they write one rule per IP address instead. Address-lists scale to hundreds of IPs with a single firewall rule.

```routeros
# Build the list (static or dynamic with auto-expiry)
/ip/firewall/address-list/add list=trusted-mgmt address=192.168.1.0/24
/ip/firewall/address-list/add list=trusted-mgmt address=10.0.0.5 timeout=1h

# One rule handles all list members
/ip/firewall/filter/add chain=input src-address-list=trusted-mgmt action=accept \
  comment="myapp-accept-mgmt"
```

Dynamic entries with `timeout=` expire automatically — the primary pattern for DoS blacklists.

## Interface-Lists as Rule Selectors

`in-interface-list=` / `out-interface-list=` — powerful RouterOS pattern LLMs never propose. Eliminates duplicate rules when multiple interfaces serve the same role.

```routeros
# Define the group once
/interface/list/add name=WAN
/interface/list/member/add list=WAN interface=ether1
/interface/list/member/add list=WAN interface=pppoe-out1

# One rule applies to all WAN interfaces
/ip/firewall/filter/add chain=input in-interface-list=WAN action=drop \
  comment="myapp-drop-all-wan"
```

## Comment-as-Tag Pattern (Idempotent Scripts)

RouterOS has no "upsert" — re-running a script without cleanup creates duplicate rules. Use a comment prefix as a tag:

```routeros
# Remove only rules we own — preserves rules from other tools
/ip/firewall/filter/remove [find comment~"myapp-"]
/ip/firewall/address-list/remove [find comment~"myapp-"]
/ip/firewall/nat/remove [find comment~"myapp-"]

# Add with consistent tag — readable in /print output
/ip/firewall/filter/add chain=input src-address-list=trusted-mgmt action=accept \
  comment="myapp-accept-mgmt"
/ip/firewall/filter/add chain=input in-interface-list=WAN action=drop \
  comment="myapp-drop-wan"
```

**Never use `remove [find dynamic=no]`** — this deletes ALL static rules including those added by management tools. Some tools (e.g. OptiWize) mark their rules with `comment~"#orchestrator-*"` — a bulk remove silently breaks remote management.

## Connection State

RouterOS `connection-state=` is not iptables `-m state`:

```routeros
/ip/firewall/filter/add chain=input connection-state=established,related action=accept
/ip/firewall/filter/add chain=input connection-state=invalid action=drop
```

RouterOS states: `new`, `established`, `related`, `invalid`, `untracked`.

`untracked` matches packets explicitly marked via `/ip/firewall/raw action=notrack` — it does NOT match FastTrack flows. FastTrack is a separate fast-path that keeps flows in conntrack but bypasses mangle. Never combine `fasttrack-connection` with mangle-based routing marks on the same traffic — mangle marks are not applied to fasttracked packets.

## NAT Patterns

```routeros
# Port forward (dst-nat)
/ip/firewall/nat/add chain=dstnat \
  dst-port=8080 protocol=tcp in-interface=ether1 \
  action=dst-nat to-addresses=192.168.1.10 to-ports=80 \
  comment="portfwd-web"

# Force DNS through router (prevents DNS bypass)
/ip/firewall/nat/add chain=dstnat action=redirect \
  in-interface-list=LAN dst-port=53 protocol=udp to-ports=53 \
  comment="force-dns-udp"
/ip/firewall/nat/add chain=dstnat action=redirect \
  in-interface-list=LAN dst-port=53 protocol=tcp to-ports=53 \
  comment="force-dns-tcp"

# Masquerade outgoing traffic
/ip/firewall/nat/add chain=srcnat action=masquerade \
  out-interface=ether1 comment="nat-wan"
```

## Layer7 Protocol (L7)

L7 matches unencrypted payload content with a POSIX regex — CPU-intensive, use sparingly:

```routeros
/ip/firewall/layer7-protocol/add \
  name=captive-detect \
  regexp="^.*(gstatic|connectivitycheck|generate_204).*$" \
  comment="android-captive-portal"
```

L7 alternation: `(a|b|c)` is correct. `(a)|(b)|(c)` has POSIX ERE operator precedence bugs — the middle branch `(b)` matches anywhere in the stream, not anchored. Use grouped form with `|` inside parentheses only.

## Common LLM Mistakes

| Mistake | Correct RouterOS behavior |
|---------|--------------------------|
| Using `priority=` or rule weight | Rules are sequential — order is position, not weight |
| Writing one rule per IP address | Use `src-address-list=` or `dst-address-list=` |
| `remove [find dynamic=no]` in scripts | Tag-based: `remove [find comment~"prefix-"]` only |
| Forgetting `place-before=` on accept rules | Default appends — accept rules below drops never fire |
| `connection-state=new,established` | Valid states: `new`, `established`, `related`, `invalid`, `untracked` |
| `action=log` or `passthrough=yes` stops evaluation | Non-terminal actions continue to next rule — a `drop` below still fires |
| Combining fasttrack + mangle routing marks | fasttrack bypasses mangle — pick one or the other |
| `(a)|(b)|(c)` alternation in L7 regexp | Use `(a|b|c)` — grouped form inside one set of parentheses |
| One firewall rule per interface | Use `in-interface-list=` with a named interface list |
| IPv6 traffic handled by `/ip/firewall` | IPv6 uses a **separate** `/ipv6/firewall` — rules do not apply cross-protocol |

## Additional Resources

**Related skills:**
- `routeros-fundamentals` — RouterOS CLI syntax, REST API, scripting basics
- `routeros-hotspot` — hotspot chain interaction with firewall, walled garden

**Reference files in this skill:**
- [references/mangle-routing.md](./references/mangle-routing.md) — policy routing with routing marks, `hotspot=auth` matcher
- [references/dos-protection.md](./references/dos-protection.md) — `psd`, `tarpit`, `connection-limit` DoS patterns

**MCP tools:**
- `rosetta` MCP — `/ip/firewall` command tree inspection (`routeros_search`, `routeros_get_page`)

**MikroTik docs:**
- [Firewall Filter](https://help.mikrotik.com/docs/display/ROS/Filter) — filter chain reference
- [NAT](https://help.mikrotik.com/docs/display/ROS/NAT) — NAT actions reference
- [Connection tracking](https://help.mikrotik.com/docs/display/ROS/Connection+tracking) — connection states
