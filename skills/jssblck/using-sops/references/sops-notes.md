# sops and age behavior the flow relies on

Verified against sops 3.13.3 and age 1.3.1 in August 2026.

## Identity sources are unioned

sops tries every age identity it can find: `~/.config/sops/age/keys.txt` (or
`$XDG_CONFIG_HOME/sops/age/keys.txt`), the `SOPS_AGE_KEY` variable (one or more
identities, newline separated), `SOPS_AGE_KEY_FILE`, and `SOPS_AGE_KEY_CMD` output. None
replaces the others. That is why `.age/elevated` passed as `SOPS_AGE_KEY_FILE` adds prod
without removing dev.

## Encrypt needs no private key; every write re-encrypts the whole file

`sops set`, `unset`, and `edit` decrypt the document, change it, and re-encrypt under all
recipients in the file's metadata. So an editor needs at least one recipient's private key
even to append a new value. A bare `age -r` append is not a valid edit: sops keeps a MAC
over the document. This is why the agent cannot add a prod value on its own and why
elevation exists.

`sops encrypt` (what `pnpm secrets init` runs) needs only `.sops.yaml` recipients. It reads
stdin when no filename is given, but then `--filename-override` is required so the
creation rule matches. An empty stdin fails; a single comment line is enough.

## `.sops.yaml` matters only at create and updatekeys time

Decrypt, set, unset, and edit read recipients from the file's own metadata. Changing
`.sops.yaml` alone changes nothing; run `sops updatekeys -y <file>` with a key that can
decrypt it, then commit.

## dotenv format specifics

- Comments are preserved and encrypted (`#ENC[...,type:comment]`).
- Values are strings. `sops set file '["KEY"]' '"value"'` takes JSON: the wrapper quotes for
  you, so `pnpm secrets set dev PW 'p@ss w"ord$'` round-trips exactly.
- `sops decrypt --output-type json` gives a flat object; the wrapper uses it for `exec`.
- Diffs show one changed `ENC[...]` line per changed value plus `sops_lastmodified` and
  `sops_mac`, so review can see which keys changed without seeing values.

## Why the wrapper spawns the child itself

`sops exec-env file 'cmd'` runs the command through `sh -c` and does not forward
`SIGTERM` to it; under `docker stop` the child is killed only when the container's grace
period expires. `tools/secrets.ts exec` decrypts to JSON, spawns the command directly with
`stdio: inherit`, forwards `SIGINT`, `SIGTERM`, `SIGHUP`, strips `SOPS_AGE_KEY` and
`SOPS_AGE_KEY_FILE` from the child environment, and exits with the child's code.
Decrypted values override same-named shell variables.

## Cloud and container facts

- Claude Code on the web has no secrets store; its environment variables field is the
  place, and the doc says not to put credentials there. An `agent`-scoped age key that
  decrypts dev only is the accepted trade.
- Codex cloud "secrets" are stripped before the agent phase; "environment variables"
  persist.
- Cursor `Runtime Secret` redaction is substring matching; `od -c` bypasses it.
- The runtime image needs the `sops` binary (~15 MB), `secrets/`, `.sops.yaml`, and
  `tools/secrets.ts`. Docker's legacy builder rejects `ADD --chmod`; use `ADD` then
  `RUN chmod 755`. Railway builds with BuildKit, where either works.
- Next `NEXT_PUBLIC_*` values are inlined at build, so the web image builds through
  `node tools/secrets.ts exec prod -- pnpm run build:web`; off Railway, pass
  `SOPS_AGE_KEY` as a BuildKit secret mount, not a build arg.
