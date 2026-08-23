---
name: using-sops
description: Use when a repo has .sops.yaml and secrets/<env>.env, or a pnpm secrets script. Covers reading and writing dev secrets, prod elevation, running with secrets, and the human key setup.
---

# Using sops

Repositories that use this layout commit their secrets to git as sops-encrypted
dotenv files, one per deployment environment: `secrets/dev.env`, `secrets/prod.env`. The
files decrypt with age identities. There is no `.env`, no secrets service, and no session
to log in to. Every checkout, worktree, and cloud sandbox has the encrypted files at
clone; the only input anywhere is an age private key.

`pnpm secrets` (`tools/secrets.ts`) is the only interface. Do not call `sops` directly in a
repo that has the wrapper.

## Identities

| Identity   | Scope       | Where the private key lives                                       | Decrypts    |
| ---------- | ----------- | ---------------------------------------------------------------- | ----------- |
| `agent`    | user-wide   | `~/.config/sops/age/keys.txt` on every machine agents run on; `SOPS_AGE_KEY` in cloud sandboxes | `dev.env` |
| `personal` | user-wide   | the user's password manager                                      | every file  |
| `prod`     | per project | that project's production platform only                          | `prod.env`  |

`.sops.yaml` lists recipients by public key. Encrypting needs no private key; decrypting
or editing needs one recipient's private key. `agent` and `personal` are local-development
keys shared by every project; `prod` is minted per project so one leaked deploy variable
exposes one project.

## Agent workflow

Dev secrets are yours to manage without asking:

```sh
pnpm secrets show dev                    # everything, decrypted
pnpm secrets get dev STRIPE_KEY
pnpm secrets set dev STRIPE_KEY sk_test_1
pnpm secrets unset dev STRIPE_KEY
pnpm secrets exec dev -- node apps/worker/src/main.ts
```

`exec` puts the decrypted values in the child's environment (over the shell's), removes
`SOPS_AGE_KEY*` from it, forwards signals, and exits with the child's status.

Prod secrets need elevation. When a task requires reading or writing `prod.env`:

1. Check for `.age/elevated` in this checkout. If present, prod commands work; carry on.
2. If absent, ask the user to run, in a terminal of their own:
   `op read 'op://Personal/age-personal/private key' | pnpm secrets elevate`
   (or however their password manager prints the key). Say why you need it.
3. Elevation is per checkout and lasts until `.age/elevated` is deleted. Do not copy it
   into another worktree.

When you add a variable, add it to the env schema and to every `secrets/<env>.env` you can
decrypt. If you cannot decrypt prod, say so in the PR: the typed env check fails the prod
boot until the value is set, which is the intended signal.

Never write an `AGE-SECRET-KEY-...` into a tracked file, a log, or a commit. Never put `personal` or `prod` in a cloud
environment.

## Human setup

For the one-time steps (generating keys, installing `sops` and `age`, wiring the `agent`
key into agent tools and cloud sandboxes, configuring the prod platform, and rotating
keys), read `references/setup.md`. When the user asks
to be reminded of the steps, walk them through that file in order.

For the sops and age behavior the design relies on (identity union, `updatekeys`,
`exec-env` limitations, dotenv quirks), read `references/sops-notes.md`.
