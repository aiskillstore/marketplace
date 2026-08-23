# Setup: keys, machines, sandboxes, production

Steps 1 through 4 are once per person, machine, or sandbox. Steps 5 and 6 are per project.

## 1. Install the tools

Both are single static Go binaries.

```sh
# Linux (WSL2 included). Adjust arch as needed.
curl -fsSL -o ~/.local/bin/sops https://github.com/getsops/sops/releases/download/v3.13.3/sops-v3.13.3.linux.amd64
chmod +x ~/.local/bin/sops
curl -fsSL https://github.com/FiloSottile/age/releases/download/v1.3.1/age-v1.3.1-linux-amd64.tar.gz | tar xz
mv age/age age/age-keygen ~/.local/bin/ && rm -rf age
```

macOS: `brew install sops age`. Confirm with `sops --version --disable-version-check`
and `age-keygen --version`. `pnpm run doctor` in a starter repo reports both.

## 2. Generate the shared identities (once, ever)

```sh
age-keygen -o personal.txt
age-keygen -o agent.txt
```

Each file holds a comment with the public key (`age1...`) and the private key
(`AGE-SECRET-KEY-1...`). Then:

- `personal.txt`: store the whole file in the password manager as `age-personal`, with the
  private key in a field you can read from the CLI (for 1Password: `op read
  'op://Personal/age-personal/private key'`). Delete the local file.
- `agent.txt`: keep for step 3, then store a copy in the password manager as
  `age-agent` for future machines. Delete the local file after step 3.

Record both public keys somewhere handy (a note in the password manager works). Every new
project's `.sops.yaml` needs them. The `prod` key is per project and is generated in step 6.

## 3. Install the agent key on a machine

```sh
mkdir -p ~/.config/sops/age
# paste the AGE-SECRET-KEY-1... line from age-agent
install -m 600 /dev/stdin ~/.config/sops/age/keys.txt <<'EOF'
AGE-SECRET-KEY-1...
EOF
```

sops reads that path by default. Any agent session on this machine, in any project,
worktree, or shell (including editors like t3code that spawn their own shells), can now
`pnpm secrets show dev`. Nothing prompts.

## 4. Cloud sandboxes

Give each platform one environment variable, `SOPS_AGE_KEY`, whose value is the `agent`
private key line. sops reads it directly. Nothing needs network access.

| Platform | Where | Notes |
| -------- | ----- | ----- |
| Claude Code on the web | environment settings, environment variables field | works with network access set to none; the environment's setup script must install `sops` (two lines from step 1, into `/usr/local/bin`) |
| Codex cloud | environment, **environment variables** (not secrets) | Codex removes "secrets" before the agent phase; a variable persists. The starter's `.codex/environments/environment.toml` setup script installs `sops` when missing |
| Cursor cloud agents | environment secrets, type `Environment Variable` | `Runtime Secret` also works but redaction is by substring and adds nothing here |
| Daytona | sandbox `envVars` (SDK) or snapshot env | install `sops` in the snapshot image |

Never put `personal` or `prod` in a sandbox.

## 5. Production

Only that project's `prod` identity goes to production. The service starts through
`pnpm secrets exec prod -- <command>` (containers: `node tools/secrets.ts exec prod -- ...`
as `CMD`), so decryption happens at boot and the app never sees the key.

**Railway** (or any container platform): set one service variable, `SOPS_AGE_KEY`, to the
`prod` private key. The image already carries `sops`, `secrets/`, `.sops.yaml`, and
`tools/secrets.ts` (the starter's release recipe copies them). Nothing else to sync: a
secret change is a commit, and the next deploy has it.

**Bare server with systemd**: keep the key out of the unit file and out of `/proc`.

```sh
sudo mkdir -p /etc/credstore.encrypted
printf '%s' 'AGE-SECRET-KEY-1...' | sudo systemd-creds encrypt --name=age-prod - /etc/credstore.encrypted/age-prod.cred
```

```ini
[Service]
User=app
WorkingDirectory=/srv/app
LoadCredentialEncrypted=age-prod:/etc/credstore.encrypted/age-prod.cred
Environment=SOPS_AGE_KEY_FILE=%d/age-prod
ExecStart=/usr/bin/node tools/secrets.ts exec prod -- node apps/server/src/main.ts
```

`systemd-creds` binds the ciphertext to the host TPM or `/var/lib/systemd/credential.secret`;
`%d` is a per-service tmpfs only that service can read.

## 6. Per project

Once per new repository (the `bootstrap` skill asks for this):

1. Generate the project's prod key: `age-keygen -o prod.txt`. Store the file in the
   password manager as `age-prod-<project>`, note the public key, delete the local file.
   Set the private key on the deploy target (step 5) when the first deploy happens.
2. Put the three public keys in `.sops.yaml`, replacing the placeholders:
   ```yaml
   creation_rules:
     - path_regex: secrets/dev\.env$
       age: 'age1PERSONAL,age1AGENT'
     - path_regex: secrets/prod\.env$
       age: 'age1PERSONAL,age1PROD'
   ```
3. `pnpm secrets init dev && pnpm secrets init prod`.
4. Elevate the checkout so you can write prod values:
   `op read 'op://Personal/age-personal/private key' | pnpm secrets elevate`.
5. `pnpm secrets set dev KEY value` and `pnpm secrets set prod KEY value` as needed. Commit
   `.sops.yaml` and `secrets/`.

Sibling worktrees are unelevated by default; repeat step 4 in a checkout that needs prod.
Delete `.age/elevated` to drop elevation.

## 7. Rotation

Add or replace a recipient (a new machine key, a lost personal key):

```sh
# edit .sops.yaml, then, holding a key that can already decrypt each file:
sops updatekeys -y secrets/dev.env
sops updatekeys -y secrets/prod.env
```

Commit both. A leaked private key means: rotate the recipient as above, then change every
value that key could read. Encrypted history remains readable to whoever holds the old
key; git cannot unpublish it.
