# Security and TLS

Use this reference for the safe sequencing around SSH hardening, firewall
changes, certificate issuance, renewal, and redirect timing.

## Safe Order of Operations

1. Confirm the user has a recovery path such as a second SSH session, console,
   snapshot, or provider rescue option.
2. Confirm key-based SSH login works before tightening authentication.
3. Create or verify a non-root admin path if appropriate for the distro.
4. Validate SSH config changes before reload or restart.
5. Apply a deny-by-default inbound firewall posture.
6. Open only the ports needed for the current phase.
7. Get HTTP working before requesting certificates.
8. Install certificates and verify HTTPS.
9. Only then enable permanent HTTP-to-HTTPS redirect.
10. Treat BBR or kernel/network tuning as optional follow-up work.

## SSH Hardening Goals

The exact commands vary by distro. Verify the current docs before telling the
user to edit config.

The usual goals are:

- key-based authentication works
- password authentication is disabled when safe
- direct root SSH login is disabled when safe
- optional custom SSH port is used only if the user wants it
- only intended admin users can log in

Safety gate:

- never recommend the irreversible parts of SSH hardening from the only active
  session

## Firewall Posture

The safe default is:

- deny-by-default inbound policy
- allow SSH intentionally
- add `80` and `443` when the web path is ready
- keep application backends private on loopback

Remember that provider firewalls and host firewalls can both matter.

## TLS Client Choice

Two common paths are reasonable:

| Client    | Good fit                                                        | What to verify                                                     |
| --------- | --------------------------------------------------------------- | ------------------------------------------------------------------ |
| Certbot   | users who want distro-packaged guidance and broad documentation | package source, plugin availability, renewal timer behavior        |
| `acme.sh` | users who explicitly prefer a lightweight ACME client           | current install method, renewal hooks, and Nginx integration steps |

Do not imply that either client is universal. Verify the chosen client against
its upstream docs before giving commands.

## Certificate Issuance Preconditions

Before any ACME issuance step, verify:

- DNS resolves to the intended server
- Nginx answers on HTTP for the expected domain
- firewall and provider rules allow inbound `80` and `443`
- the chosen challenge method matches the user's environment

Useful validation commands:

- `dig +short example.com`
- `curl -I http://example.com`
- `ss -tulpn`
- `nginx -t`

## Redirect Timing

Do not force this until HTTPS already works:

```nginx
return 301 https://$host$request_uri;
```

First confirm that:

- the certificate is installed correctly
- the `server_name` matches the intended domain
- `curl -I https://example.com` succeeds
- the browser does not show certificate warnings

## Common Failure Branches

- DNS points somewhere else, so ACME validation fails
- HTTP is redirected too early, so challenge or validation behavior breaks
- the wrong webroot or vhost handles the ACME challenge
- firewall rules were changed on the host but not at the provider edge
- Nginx can read the config but not the site files or certificate files
- optional tuning work starts before the secure hosting path is stable

## Optional Advanced Tuning

BBR and similar kernel/network changes belong after the secure web stack is
working.

Only recommend them when:

- the user wants the tuning on purpose
- the current kernel path is verified for the distro
- a rollback or rescue path exists

Never let optional tuning preempt basic access, firewall, Nginx, or HTTPS work.
