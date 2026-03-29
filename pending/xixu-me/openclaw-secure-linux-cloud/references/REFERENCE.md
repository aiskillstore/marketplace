# OpenClaw Secure Linux Cloud Reference

This reference supports the `openclaw-secure-linux-cloud` skill.

It adapts the deployment pattern from Xi Xu's Debian-focused article, "Run
OpenClaw Securely on a Debian Cloud Server: A Complete Guide from Setup to
Hardening," published on March 13, 2026, along with current upstream OpenClaw
repository guidance. The package names and firewall commands in the article are
Debian-specific, but the security model generalizes well to Linux cloud hosts.

Source article:
[Xi Xu's Blog](https://blog.xi-xu.me/en/2026/03/13/Run-OpenClaw-Securely-On-Debian-Cloud-Server.html)

License note:
The source article is published under CC BY-SA 4.0. Keep attribution intact if
you redistribute derivative guidance from this bundle.

Maintainer note:
The security posture in this bundle is intentionally conservative and tied to
the article's March 13, 2026 recommendations. Check current upstream OpenClaw
docs and commands before future edits, because onboarding, config keys,
operational commands, and distro-specific package or firewall guidance may
drift over time.

## Architecture Summary

Target end state:

- Linux host exposes only SSH by default
- OpenClaw runs under rootless Podman
- The gateway listens on loopback only
- The Control UI is reached through an SSH tunnel
- Token authentication stays enabled
- Pairing stays enabled for inbound channels
- Tool access stays narrow by default
- Sandboxing remains enabled unless there is a deliberate reason to relax it

Core principle:
Treat the OpenClaw gateway as a private control plane, not a public-first web
service.

## Command Matrix

### Local Machine

Use these steps on the machine you are connecting from:

```bash
export VPS_USER="your_admin_user"
export VPS_HOST="your.server.ip.or.domain"

ssh-keygen -t ed25519 -C "openclaw-cloud"
ssh-copy-id "${VPS_USER}@${VPS_HOST}"
ssh "${VPS_USER}@${VPS_HOST}"
```

Create the Control UI tunnel without exposing the gateway publicly:

```bash
export VPS_USER="your_admin_user"
export VPS_HOST="your.server.ip.or.domain"

ssh -N -L 18789:127.0.0.1:18789 "${VPS_USER}@${VPS_HOST}"
```

Then open:

```text
http://127.0.0.1:18789/
```

### Linux Host: Cross-Distro Invariants

Keep these security goals constant even when package names or service
management differ:

- Install the baseline tools needed for Git, TLS helpers, rootless Podman,
  firewall management, and unattended security updates.
- Harden SSH only after public-key login works.
- Apply a default-deny inbound firewall and keep the OpenClaw UI port private.
- Run OpenClaw under rootless Podman instead of as a long-lived root process.
- Keep the gateway bound to loopback only.
- Store the gateway token and config with tight per-user permissions.

Typical distro adaptations:

- Debian or Ubuntu: `apt`, `systemctl`, and either `nftables` or `ufw`
- Fedora, RHEL, Rocky, AlmaLinux: `dnf`, `systemctl`, and often `firewalld`
- Arch: `pacman`, `systemctl`, and distro-specific firewall preferences

If the distro is unknown and concrete commands are required, ask which distro
the host runs instead of pretending the Debian package names are universal.

### Debian/Ubuntu Example Commands

Update the host and install baseline packages:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y git curl openssl podman nftables unattended-upgrades apt-listchanges
```

Enable automatic security updates:

```bash
sudo tee /etc/apt/apt.conf.d/20auto-upgrades >/dev/null <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

sudo systemctl enable --now unattended-upgrades
```

Harden SSH after key-based login works:

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%F-%H%M%S)

sudo tee /etc/ssh/sshd_config.d/99-openclaw-hardening.conf >/dev/null <<'EOF'
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PermitRootLogin no
UsePAM yes
X11Forwarding no
EOF

sudo sshd -t
sudo systemctl reload ssh
```

Apply a default-deny inbound firewall that leaves only SSH reachable:

```bash
sudo tee /etc/nftables.conf >/dev/null <<'EOF'
flush ruleset

table inet filter {
  chain input {
    type filter hook input priority 0;
    policy drop;

    iif lo accept
    ct state established,related accept
    tcp dport 22 accept
    ip protocol icmp accept
    ip6 nexthdr icmpv6 accept
  }

  chain forward {
    type filter hook forward priority 0;
    policy drop;
  }

  chain output {
    type filter hook output priority 0;
    policy accept;
  }
}
EOF

sudo systemctl enable --now nftables
sudo nft -f /etc/nftables.conf
sudo nft list ruleset
```

Install OpenClaw from source with the Podman helper:

```bash
cd /opt
sudo git clone https://github.com/openclaw/openclaw.git
cd /opt/openclaw

sudo ./setup-podman.sh --quadlet
```

Check the service and logs:

```bash
sudo systemctl --machine openclaw@ --user status openclaw.service
sudo journalctl --machine openclaw@ --user -u openclaw.service -f
```

Run the initial setup flow:

```bash
cd /opt/openclaw
sudo ./scripts/run-openclaw-podman.sh launch setup
```

View the generated gateway token:

```bash
sudo -u openclaw grep '^OPENCLAW_GATEWAY_TOKEN=' /home/openclaw/.openclaw/.env
```

Restart after config changes:

```bash
sudo systemctl --machine openclaw@ --user restart openclaw.service
sudo systemctl --machine openclaw@ --user status openclaw.service
```

## Baseline Config Skeleton

Use this as a conservative starting shape on Linux, then verify the exact keys
against current upstream docs before applying it to a live system:

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    port: 18789,
    controlUi: { enabled: true },
    auth: {
      mode: "token",
      token: "${OPENCLAW_GATEWAY_TOKEN}",
    },
  },
  session: {
    dmScope: "per-channel-peer",
  },
  tools: {
    profile: "messaging",
    fs: { workspaceOnly: true },
    deny: [
      "group:runtime",
      "group:fs",
      "group:automation",
      "browser",
      "sessions_spawn",
    ],
  },
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        scope: "agent",
        workspaceAccess: "none",
      },
    },
  },
}
```

Lock down the config directory after writing the config:

```bash
sudo chmod 700 /home/openclaw/.openclaw
sudo chmod 600 /home/openclaw/.openclaw/openclaw.json
sudo chown -R openclaw:openclaw /home/openclaw/.openclaw
```

## Pairing and Day-Two Operations

Pairing should remain enabled unless the user has a strong reason to widen DM
access.

Typical pairing review and approval flow:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>

openclaw pairing list signal
openclaw pairing approve signal <CODE>
```

Day-two audit and health checks:

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw secrets audit
openclaw doctor
```

If sandbox policy changes later, recreate sandboxes so old state does not mask
the new policy:

```bash
openclaw sandbox recreate --all
```

## Access-Path Decision Table

| Need                                           | Recommended path | Why                                                     | Main caution                                                                 |
| ---------------------------------------------- | ---------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------- |
| First secure deployment                        | SSH tunnel       | Smallest exposed surface and easiest to reason about    | Requires an SSH session when you want the UI                                 |
| Repeated private access across trusted devices | Tailscale        | More convenient while keeping access private-first      | Keep loopback binding and verify current upstream Tailscale docs             |
| Intentional public exposure                    | Reverse proxy    | Only for explicit public or broader remote access needs | Requires stronger auth, tighter monitoring, and more careful boundary design |

Decision rule:

1. Start with SSH tunneling.
2. Move to Tailscale when private convenience becomes a real need.
3. Consider a reverse proxy only after the private options no longer fit.

## Common Pitfalls

- Binding the gateway directly to `0.0.0.0`
- Allowing port `18789` through the firewall just because auth exists
- Enabling broad tool access before the user knows what capabilities they
  really need
- Leaving `~/.openclaw` or the config file too open
- Disabling pairing just to shorten onboarding
- Treating the initial setup as the end of the job and skipping audits

## Pre-Launch Checklist

- SSH key login works
- Direct root login is disabled
- SSH passwords are disabled
- Automatic security updates are enabled
- Inbound firewall policy is deny-by-default
- Only SSH is intentionally exposed
- OpenClaw stays on loopback
- The Control UI is not public
- Token auth is enabled
- `~/.openclaw` permissions are tight
- Tool defaults are narrow
- Sandboxing is enabled
- Pairing is preserved
- Security and health checks have been run

## Scope Boundary

This bundle is intentionally Linux-specific and centered on the article's
private-first deployment pattern, with Debian or Ubuntu shown as the clearest
example path.

If the user wants:

- a generic local install
- a non-Linux system
- a Docker Compose tutorial
- a public SaaS-style deployment

then adapt carefully or defer to current upstream OpenClaw docs instead of
pretending these Debian/Ubuntu example commands are universal.
