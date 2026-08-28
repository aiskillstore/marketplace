---
name: solana-mobile
description: Scaffold, configure, and troubleshoot Solana Mobile apps for Android using the solana-mobile CLI, Expo, and React Native. Use when creating a new Solana mobile app, picking a template, adding Solana to an existing Expo app, checking the Android toolchain, managing Android emulators, or producing a development build.
---

# Solana Mobile projects

Set up and maintain Solana Mobile apps. The `solana-mobile` CLI does the scaffolding,
environment checks, and emulator management — prefer it over hand-rolled setup.

Run it without installing:

```bash
npx solana-mobile@latest --help
```

`pnpx solana-mobile@latest` and `bun x solana-mobile@latest` work too. Match whichever
package manager the project already uses.

## Non-negotiable constraint

**Mobile Wallet Adapter requires a development build. Expo Go will not work** — MWA depends
on native Android modules that Expo Go does not bundle. If someone reports wallet
connection failing in Expo Go, that is the cause; there is no workaround, they need
`expo run:android`.

Android is the only platform with wallet support. iOS builds run, but no MWA.

## First: work out which situation you are in

| Situation | Do this |
| --- | --- |
| No project yet | [Create a new project](#create-a-new-project) |
| Existing Expo app, no Solana | Read [references/add-to-existing-app.md](references/add-to-existing-app.md) |
| Project exists, build or toolchain broken | [Check the environment](#check-the-environment) |
| Project exists, needs wallet features | Use the `solana-mobile-wallet` skill |

## Create a new project

```bash
npx solana-mobile@latest create
```

Interactive by default. To skip the prompts, name the project and template:

```bash
npx solana-mobile@latest create my-app --template expo-kit-wallet
```

Useful flags:

| Flag | Effect |
| --- | --- |
| `-t, --template <id>` | Pick a template non-interactively |
| `--pm <manager>` | Package manager to use |
| `--minimal` | Use the minimal template |
| `--list-templates` | Print the template catalog |
| `--list-template-ids` | Print template ids as a JSON array |
| `--skip-install` | Do not install dependencies |
| `--skip-git` | Do not initialise a git repo |
| `-d, --dry-run` | Show what would happen, write nothing |

### Choosing a template

Templates come in two families. **Pick an `expo-kit-*` template.** `@solana/kit` is the current
Solana client library, and these are the templates the CLI maintains most actively.

Reach for `expo-web3js-*` only when the user is deliberately continuing an existing
`@solana/web3.js` codebase, or asks for it by name. If they ask without a reason, say kit is the
better starting point before going along with it — a new app on web3.js starts life needing a
migration.

`expo-kit-minimal` is the clearest reference for how the kit pieces fit together, and worth
reading even when building on a different template.

| Template | Stack | Use for |
| --- | --- | --- |
| `expo-kit-wallet` | Kit + MWA + Uniwind | **Best default.** Wallet connect, sign, send already wired |
| `expo-kit-minimal` | Kit | Bare starting point, no UI kit |
| `expo-kit-uniwind` | Kit + Uniwind | Tailwind-style styling, no wallet yet |
| `expo-kit-privy` | Kit + Privy + Uniwind | Privy auth instead of, or alongside, MWA |
| `expo-web3js-wallet` | web3.js + MWA | Legacy wallet app |
| `expo-web3js-paper` | web3.js + RN Paper | Legacy, Material UI |
| `expo-web3js-minimal` | web3.js | Legacy bare starting point |

Template ids are also accepted in full `gh:solana-mobile/templates/mobile/<name>` form.
Re-run `--list-templates` rather than trusting this table if a template seems missing — the
catalog ships with the CLI, not with this skill.

### After scaffolding

```bash
cd my-app && npm run android
```

That runs `expo run:android`, which builds and installs the development build. The first
Android build is slow (Gradle cold start); later builds reuse the cache.

## Check the environment

Before debugging a build failure, check the toolchain:

```bash
npx solana-mobile@latest doctor
```

It reports on the local Android and Node toolchain with recommendations for anything
missing. `--json` gives a stable report worth parsing when you need to branch on a specific
check; `--verbose` adds resolved paths and diagnostics.

Run `doctor` first whenever a build fails for reasons that are not obviously in app code.

## Manage Android emulators

```bash
npx solana-mobile@latest emu list
npx solana-mobile@latest emu status
npx solana-mobile@latest emu create
npx solana-mobile@latest emu start my_phone
npx solana-mobile@latest emu stop my_phone
```

`emu` is an alias for `emulator`. Subcommands: `create`, `delete`, `images`, `list`,
`start`, `status`, `stop`. System images live under `emu images` (`install`, `list`,
`delete`).

Create a named emulator on a specific device profile:

```bash
npx solana-mobile@latest emu create local_phone --device pixel_9
```

### Testing wallet flows on an emulator

A fresh emulator has no wallet app installed, so MWA has nothing to connect to. Install an
MWA-compatible wallet APK into the emulator first, or test on a physical Android device.
Anything gated on the Seeker Genesis Token needs a real Seeker device — see the
`seeker-genesis-token` skill.

## Reference material

- [references/add-to-existing-app.md](references/add-to-existing-app.md) — wiring Solana
  into an Expo app that already exists: crypto polyfill, providers, dependencies
- [references/troubleshooting.md](references/troubleshooting.md) — build, polyfill, and
  emulator failures with known causes

## Related skills

- `solana-mobile-wallet` — connecting wallets, signing, sending transactions
- `seeker-genesis-token` — verifying Seeker device ownership
- `seeker-domains` — `.skr` domain name resolution

For general non-mobile Solana work — Anchor or Pinocchio programs, Codama client generation,
testing, security review — use the Solana Foundation's `solana-dev` skill instead. `create`
installs it into `.agents/skills/solana-dev/`, so a scaffolded project already has it.

## Links

- CLI source: https://github.com/solana-mobile/solana-mobile-cli
- Templates: https://github.com/solana-mobile/templates
- Solana Mobile docs: https://docs.solanamobile.com
