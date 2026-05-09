# RADIUS Client Configuration

RouterOS RADIUS client for hotspot authentication. Referenced from `routeros-hotspot` SKILL.md.

## Multi-Server Pattern

RouterOS tries RADIUS servers in list order and falls back to the next on timeout. Add at least two entries for redundancy:

```routeros
/radius add \
  address=198.51.100.10 \
  secret="your-shared-secret" \
  service=hotspot \
  timeout=3s \
  comment="radius-primary"

/radius add \
  address=198.51.100.11 \
  secret="your-shared-secret" \
  service=hotspot \
  timeout=3s \
  comment="radius-secondary"
```

## Initial Disabled State

In automated deployments, create RADIUS entries as `disabled=yes` and enable them only after the hotspot HTML files and certificates are ready:

```routeros
# At deploy time — disabled until hotspot files are ready
/radius add address=198.51.100.10 secret="..." service=hotspot timeout=3s \
  comment="my-radius" disabled=yes

# After hotspot files downloaded:
/radius enable [find comment~"my-radius"]
```

This prevents the hotspot from serving auth requests before the login page exists.

## Secret Management

Never hardcode RADIUS secrets in scripts. Use a template variable:

```routeros
# In OptiWize or similar template systems:
# <<radius_secret>> is substituted at deploy time
/radius add address=198.51.100.10 secret="<<radius_secret>>" service=hotspot \
  timeout=3s comment="my-radius" disabled=yes
```

## `[:resolve]` Trap

`[:resolve "radius.example.com"]` returns **only the first A record**. If the RADIUS server has multiple IPs for redundancy, only one is used. Use explicit IP variables:

```routeros
# BAD — only gets 1 IP even if DNS has multiple A records
:local radiusIp [:resolve "radius.example.com"]

# GOOD — use explicit IPs
/radius add address="198.51.100.10" secret="..." service=hotspot comment="radius-1" disabled=yes
/radius add address="198.51.100.11" secret="..." service=hotspot comment="radius-2" disabled=yes
```

## Enable Pattern

After hotspot files are downloaded, enable all RADIUS entries tagged with a shared comment:

```routeros
/radius enable [find comment~"my-radius"]
```

This is idempotent — running it again on already-enabled entries has no effect.
