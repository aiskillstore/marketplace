# Distro Routing

Never assume Debian commands on an unknown Linux host.

This reference is for routing and modernization, not for blindly copied
commands. Before you give actionable steps, verify the current docs for the
user's distro family and chosen tools.

## First Questions

Ask these before giving package or service commands:

1. What distro or cloud image is the host using?
2. If the user is unsure, can they check `/etc/os-release`?
3. What firewall tooling is already present?
4. Is the host enforcing SELinux or AppArmor?
5. Is the hosting goal static files or a reverse proxy to an app?

## Family Matrix

| Family                            | Package manager | Likely firewall tooling                                               | SSH service naming | Notes to verify live                                                  |
| --------------------------------- | --------------- | --------------------------------------------------------------------- | ------------------ | --------------------------------------------------------------------- |
| Debian / Ubuntu                   | `apt`           | `ufw`, `nftables`, or provider firewalls                              | commonly `ssh`     | package names, drop-in config paths, default sudo setup               |
| Fedora / RHEL / Rocky / AlmaLinux | `dnf`           | `firewalld`                                                           | commonly `sshd`    | SELinux contexts, package splits, service enablement                  |
| Arch                              | `pacman`        | user-chosen; often none by default, `ufw`, `nftables`, or `firewalld` | commonly `sshd`    | rolling-package names, manual service enablement, wiki-first workflow |
| Other / unknown                   | varies          | varies                                                                | varies             | stop and verify instead of guessing                                   |

## What Commonly Differs

These are the details most likely to drift across distros or over time:

- package names for Nginx, ACME clients, firewall helpers, and security updates
- SSH service unit names and include directories
- default web root paths
- firewall commands and persistence model
- SELinux or AppArmor behavior around Nginx file access or proxy connections
- renewal timers or hooks for the chosen ACME client

## Official Docs Entry Points

Use these as starting points when you need live verification:

- Debian docs: <https://www.debian.org/doc/>
- Ubuntu Server documentation: <https://documentation.ubuntu.com/server/>
- Red Hat documentation: <https://docs.redhat.com/>
- ArchWiki main page: <https://wiki.archlinux.org/>
- Nginx documentation: <https://nginx.org/en/docs/>
- Let's Encrypt challenge types: <https://letsencrypt.org/docs/challenge-types/>
- Certbot instructions: <https://certbot.eff.org/instructions>
- `acme.sh` wiki: <https://github.com/acmesh-official/acme.sh/wiki>

If the user is on a cloud-specific image with opinionated defaults, also verify
the provider's image docs before assuming stock distro behavior.

## Modernization Rules

- Treat Debian-10-era tutorials as conceptual background only.
- Do not frame Windows-first tooling such as PuTTY as the default path unless
  the user explicitly needs it.
- Prefer the distro's current package-management and service-management docs to
  blog posts or memory.
- If a family-specific hardening feature matters, say that it is distro-specific
  instead of flattening it into "Linux" advice.
