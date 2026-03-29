# Secure Linux Web Hosting Workflow Map

This reference supports the `secure-linux-web-hosting` skill.

It adapts the conceptual flow of Xi Xu's article, "Build, Configure, and Secure
Your Cloud Server from Scratch and Host a Simple Website," published on
August 25, 2024:
[Xi Xu's Blog](https://blog.xi-xu.me/en/2024/08/25/Launching-a-Cloud-Server-and-Building-a-Website-from-Scratch.html)

The source article is licensed under CC BY-SA 4.0. This bundle keeps the
high-level flow while modernizing the dated distro and tooling assumptions.

## Safe Default Posture

Aim for this end state unless the user explicitly needs something broader:

- Linux host updated and reachable over SSH
- non-root admin access available
- SSH reduced to key-based access after a second-session test
- inbound firewall deny-by-default
- only ports `80` and `443` intentionally exposed for web traffic
- Nginx serving either static files or proxying an app that stays on loopback
- HTTPS working before any permanent redirect
- optional tuning deferred until the secure web path is stable

## Phase Map

| Phase                 | Goal                                                                               | Verify before continuing                                                               | Common failure if skipped                                      |
| --------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Intake                | Identify distro family, access model, DNS state, and hosting goal                  | The assistant knows whether the user needs static hosting or reverse proxying          | Wrong commands, wrong branch, or unsafe assumptions            |
| Prerequisites         | Confirm server access, domain ownership, DNS plan, and package/doc source of truth | User can log in and knows what domain should resolve where                             | Chasing web-server issues that are really access or DNS issues |
| Secure access         | Establish admin access and harden SSH carefully                                    | Key login works in a second session; SSH config tests cleanly before reload            | Lockout after port or auth changes                             |
| Firewall and exposure | Make the network surface intentional                                               | Only the intended ports are reachable; loopback-only services stay private             | App or SSH unexpectedly exposed or blocked                     |
| Web server base       | Install and validate Nginx itself                                                  | `nginx -t` succeeds and the service is healthy                                         | Debugging app logic when Nginx is not actually healthy         |
| Static-site branch    | Serve files directly from Nginx                                                    | The site root exists, file permissions are readable, and HTTP serves the expected page | Wrong `root` path or unreadable files                          |
| App-proxy branch      | Put Nginx in front of an app on loopback                                           | The app responds locally before Nginx fronts it                                        | Proxying a dead app or exposing the app port publicly          |
| HTTPS                 | Issue, install, and renew certificates safely                                      | DNS resolves, HTTP works, certificate issuance succeeds, HTTPS loads cleanly           | ACME failures, wrong webroot, redirect loops                   |
| Validation            | Confirm the final public behavior and renewal posture                              | HTTP/HTTPS behavior matches intent and logs look healthy                               | Hidden breakage left in place                                  |
| Optional tuning       | Apply BBR or similar tuning only if useful                                         | Snapshot/rescue path exists and the web stack is already stable                        | Breaking a working host during non-essential tuning            |

## Branch Choice

Choose one application branch unless the user clearly needs both:

- **Static-site branch**: Nginx serves HTML, CSS, JS, and assets from disk.
- **App-proxy branch**: the app listens on `127.0.0.1:<port>` and Nginx fronts
  it.

Do not mix the two branches into one default answer. The most common mistake is
giving a reverse-proxy config to a user who only needs file hosting, or a
static-root config to a user whose app must stay on a loopback port.

## Default Validation Sequence

Use a narrow validation loop at each phase:

1. syntax or config validation
2. service reload or restart only if validation passed
3. local check on the server
4. remote check from the user's machine
5. only then move to the next phase

Useful validation commands, depending on distro and tools:

- `nginx -t`
- `systemctl status nginx`
- `ss -tulpn`
- `curl -I http://127.0.0.1:<port>`
- `curl -I http://example.com`
- `curl -I https://example.com`
- `dig +short example.com`
- `openssl s_client -connect example.com:443 -servername example.com`

## Optional Tuning Boundary

BBR, queue discipline changes, and kernel tuning are explicitly optional.

Only suggest them when:

- the site is already securely reachable
- the user wants network tuning on purpose
- the host has a snapshot, rescue console, or other rollback path

Do not treat optional tuning as part of the minimum secure-hosting flow.
