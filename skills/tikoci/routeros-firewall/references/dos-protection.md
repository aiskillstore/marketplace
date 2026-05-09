# DoS Protection Patterns

RouterOS-specific DoS protection matchers. Referenced from `routeros-firewall` SKILL.md.

## Port Scan Detection — `psd`

`psd` is a RouterOS-specific TCP matcher that scores packets by destination port type:

```routeros
/ip/firewall/filter/add chain=input \
  protocol=tcp psd=21,3s,3,1 \
  action=add-src-to-address-list address-list=port-scanners \
  address-list-timeout=1h comment="dos-detect-portscan"
```

**`psd=weight,delay,low-port-weight,high-port-weight` tuple:**
- `weight` — total score threshold that triggers the rule (21 in example)
- `delay` — max time between probe packets to count as one scan (3s)
- `low-port-weight` — score added per probe of a port < 1024 (3 pts in example)
- `high-port-weight` — score added per probe of a port ≥ 1024 (1 pt in example)

**The last two values are weight scores, NOT port ranges.** Common mistake: treating them as `low-port,high-port` boundaries.

Example: `psd=21,3s,3,1` — scanning 7 low ports (7×3=21) triggers the rule within 3 seconds.

## `action=tarpit`

TCP tarpit — completes the handshake but stalls the connection indefinitely:

```routeros
/ip/firewall/filter/add chain=input \
  src-address-list=dos-attackers \
  connection-limit=3,32 protocol=tcp \
  action=tarpit comment="dos-tarpit-blacklist"
```

**How it works:** Completes SYN/SYN-ACK/ACK, then advertises a TCP receive window size of **zero**. The sender cannot transmit data (zero window = no send permission) and the connection stalls in ESTABLISHED state indefinitely, consuming attacker resources.

- TCP only (`protocol=tcp` required)
- Does NOT throttle bandwidth — data never flows at all
- Effective against connection-flood attacks where cost is per-connection

## `connection-limit` Tuple

```routeros
/ip/firewall/filter/add chain=input \
  protocol=tcp connection-state=new connection-limit=100,32 \
  action=add-src-to-address-list address-list=dos-attackers \
  address-list-timeout=1h comment="dos-detect-ddos"
```

**`connection-limit=X,Y` tuple:**
- `X` — maximum simultaneous connections
- `Y` — netmask prefix bits (32 = per individual IP, 24 = per /24 subnet)

`connection-limit=100,32` = max 100 simultaneous connections per individual IP.

Add `connection-state=new` guard — limits evaluation to new connections only, reducing router CPU load under the attack conditions the rule is meant to detect.

## Combined Blacklist Pattern

Three-stage pattern: detect → blacklist → tarpit:

```routeros
# Stage 1: detect port scanners
/ip/firewall/filter/add chain=input \
  protocol=tcp psd=21,3s,3,1 \
  action=add-src-to-address-list address-list=port-scanners \
  address-list-timeout=1h comment="dos-detect-portscan"

# Stage 2: detect connection floods
/ip/firewall/filter/add chain=input \
  protocol=tcp connection-state=new connection-limit=100,32 \
  action=add-src-to-address-list address-list=dos-attackers \
  address-list-timeout=1h comment="dos-detect-ddos"

# Stage 3: tarpit blacklisted sources (connection-limit=3,32 is the second gate)
/ip/firewall/filter/add chain=input \
  src-address-list=dos-attackers connection-limit=3,32 protocol=tcp \
  action=tarpit comment="dos-tarpit-blacklist"
```

Note: the tarpit rule also requires `connection-limit=3,32` — blacklisted IPs with fewer than 3 simultaneous connections are not tarpitted by this pattern.

The `address-list-timeout=1h` on detection rules means entries auto-expire — no manual cleanup needed.
