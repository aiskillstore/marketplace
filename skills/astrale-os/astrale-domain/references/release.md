# Deploy, install, and publish

Three commands, one effect each. The SDK binary `astrale-domain`, run in the Domain project, deploys
and publishes; the `astrale` CLI installs. Only an install changes what an instance runs.

| Command | Creates a deployment | Names a version | Changes an instance |
| --- | --- | --- | --- |
| `astrale-domain deploy <environment>` | yes | no | no |
| `astrale-domain publish <environment>` | yes, deploy included | yes, the `package.json` version | no |
| `astrale domain install <reference>... -i <instance>` | no | no | yes |

`astrale-domain build`, `diff` and `list`, and `astrale domain versions`, only read.

## Deploy, then install

```sh
pnpm run deploy development                 # astrale-domain deploy development: prints the deployment URL
astrale domain install <url> -i acme-dev    # pin that release on the instance
```

- A deploy makes one immutable deployment of one release (the build with the Environment's frozen
  configuration) at its own URL, `https://<line>-<content>.<routing domain>`, with a signing key
  generated for it. The line comes from the origin and the Environment; the content covers the
  build and the configuration. Redeploying the same release reuses its deployment; other code,
  another variable or another set of secret names gives another URL. Earlier deployments keep
  serving at their own URLs.
- A deployment without a version is a preview. It is never in the registry, it is installed by
  URL, and it expires 30 days after its activation or its last call, whichever is later. Publish a
  release to keep it.
- `deploy --json` prints one DeployResultV1 on stdout (its `url` is what install takes); progress
  goes to stderr. `astrale-domain list` shows the deployments of the Project's Environments, each
  named by the registry's version of its release (`1.5.0`) or of its build (`1.5.0 · staging`), else
  by a name computed from its commit (`1.4.2 + 7 commits · a1b2c3d · staging`), with its last call
  and expiry. `--instance <name>` (repeatable) asks those instances what they run for its INSTALLED
  ON column: `?` is unknown (an instance not asked, or one that cannot tell), `—` means every
  instance asked listed all it runs and none runs it. A registry it cannot read fails the listing
  (SDK 0.6.0-beta.17 and astrale CLI 1.0.0-beta.129 or newer; older SDKs show computed names only).
- Install Domains that move together in ONE grouped install, which is atomic and mixes URLs and
  versions. Never chain one-Domain installs for a coherent set:

```sh
URL_A=$(pnpm --dir agencies exec astrale-domain deploy staging --json | jq -r .url)
URL_B=$(pnpm --dir employees exec astrale-domain deploy staging --json | jq -r .url)
astrale domain install "$URL_A" "$URL_B" --allow-issuer-change -i acme-stg
```

- The URL is already a pin: the CLI reads the release it serves and pins its release digest, and
  the Kernel refuses any other. A deployment URL never serves other code, so new code reaches an
  instance only through an install of its new URL or version.

## Issuer changes need consent

Each deployment is its own issuer. Installing a new deployment of an installed origin changes its
issuer, which is never silent:

- same line, a new deployment of the same Domain and Environment (the next `development` preview,
  or another version published from `production`): `--allow-issuer-change`;
- another line (another Environment, a production version over a staging preview, or the first move
  from a legacy stable Worker): `--allow-issuer-change=<origin>`, the origin only after `=`;
- at a terminal, typing the origin when asked confirms either.

The first install of an origin needs no consent. The replaced issuer keeps serving its in-flight work
while it drains; `--revoke-previous` cuts it at the activation. Without consent the install fails
with ISSUER_CHANGE_NOT_CONSENTED before anything is sent, and `details.origins` lists every change.

## Who owns a development instance

An instance runs what its last install pinned, and nothing locks it between machines: two people
installing on one instance replace each other's previews. Give each instance one owner, a developer
or CI, never both:

- one developer: one development instance;
- several developers: one instance each. Environments name no instance, so each developer passes
  their own `-i <instance>` and nothing in `astrale.config.ts` changes;
- CI integration, such as staging installing every Domain of the repository together: an instance
  of its own.

Deployments are per developer anyway: each build is its own deployment, so previews never replace
each other. Their line is per origin and Environment, though, and it belongs to one organization,
first come. A team that shares `development` names an `organization` there too (a Shell Group whose
members deploy for it); without one, the line belongs to whoever deployed first, and the others are
refused `line-owned-elsewhere`.

## Branch by branch

| Event | Command | Registry | Install |
| --- | --- | --- | --- |
| Feature branch or PR | `deploy development` | nothing | its owner's dev instance, by URL |
| Push to the integration branch | `deploy staging` | nothing | staging, every Domain together, by URL |
| Merge of the release PR | `publish production` | version `1.5.0` | production: `install <origin>@1.5.0`, by hand or in CI behind an approval |
| Hotfix branch `release/1.4.x` | `publish production` | version `1.4.3` | the same; `diff` compares with 1.4.2 even if 2.0.0 exists |
| Chosen candidate or beta | `publish production` at `2.0.0-rc.1` | version `2.0.0-rc.1` | only by its exact number |

## Publish a version

The version lives in `package.json`, written by release-please or `npm version`; no command takes a
number.

```sh
astrale-domain diff                  # changes since the published version and the minimum they require
npm version minor                    # writes 1.5.0 to package.json, with its commit and tag
astrale-domain publish production    # deploys, verifies, then creates the version 1.5.0
```

`publish <environment>`, in order:

1. Before any effect, refuses an Environment that does not deploy immutable deployments, a working
   tree with changes, or no git commit (unless `--allow-dirty`, which marks the Publication dirty),
   and warns when no remote branch holds the commit.
2. Reads the version and the registry. The same version naming the same release succeeds without
   effect; naming another release it is refused: a published version never changes, raise it.
3. Compares with the highest stable version below it and refuses a version too low, naming each
   change that requires more.
4. Deploys the release, or reuses its deployment, and verifies within 60 seconds that it serves
   the sealed release.
5. Asks Admin for the Publication, under the Domain's lock. A version published meanwhile with
   another release is refused, and this deployment stays a preview.

A failure leaves at most a deployment without a version, and says whether a rerun can help. When
it can, rerun `publish`, which reuses the deployment; an answer that was lost may already have
created the Publication, and the rerun settles it. A refusal Admin would repeat, such as a missing
`domain_admin` right or a release Admin will not name, names its cause instead. With Admin
unavailable, or a Domain absent from the registry, nothing is deployed. Publishing never installs.
When Admin created the version but could not keep its deployment from expiring, `publish` still
exits 0 and warns on stderr with the exact request to send again; until then that deployment can
expire like a preview.

- Semver without channels. Code only or an equivalent meaning: patch; additions only: minor; a
  member removed or changed: major; below 1.0.0 a breaking change raises the minor. `diff` gives a
  floor: a behaviour or authorization change at the same signature is the author's to raise.
- Pre-releases only for a chosen step (`2.0.0-rc.1`, a beta for testers), never per Environment (no
  `1.5.0-staging.3`). A pre-release compares with the last stable version, and no line reference
  ever chooses it. Publish from `production`; `publish staging` only for a beta that must run on
  test resources.
- An Astrale operator creates the Domain in the registry and names its first administrator.
  Publishing and yanking require `domain_admin`, reading versions `domain_installer` (a public
  Domain grants it to the Public group); both can be held through a Group, CI included.
- `diff`, `publish` and `yank` reach the registry through the `astrale` CLI, with its Admin target and
  identity (`--as <identity>` on `diff` and `publish`). `--json` prints one report on stdout
  (DiffReportV1, PublishReportV1, YankReportV1); decide on the exit status.

### With release-please in CI

1. On every PR, `astrale-domain diff` reports the minimum the PR requires. While `package.json` still
   names a published version, as on a feature branch, the report is informational and exits 0.
2. release-please opens the release PR with the version from the commits: `fix` patch, `feat`
   minor, `!` major.
3. On that PR, `diff` is a blocking check: a version too low exits 1. Raise it with a
   `Release-As: 2.0.0` footer or a `feat!:` commit.
4. On merge, the workflow that publishes the npm package runs `astrale-domain publish production`.
   The Domain's schema package carries the same number, from the same `package.json`.

The SDK's composite GitHub Actions `domain-diff` and `domain-publish` (`actions/` in the
`astrale-os/sdk` repository) run steps 1, 3 and 4. Give them two CI identities: one holding
`domain_installer` for the diff on pull requests, one holding `domain_admin`, kept in a protected
`production` GitHub Environment, for the publish after the release merge. release-please must open
its PR with a token that starts workflows, or the diff never runs on it.

## Install a version, roll back, yank

```sh
astrale domain versions issues.example                                          # every published version
astrale domain install issues.example@1.5 -i acme-prod                          # highest stable 1.5.x
astrale domain install issues.example@1.5.0 --allow-issuer-change -i acme-prod  # an upgrade, scripted
astrale domain install agencies.example@1.5.0 employees.example@2.0.0 --allow-issuer-change -i acme-prod
astrale domain install issues.example@1.4.2 --allow-issuer-change -i acme-prod  # rollback
astrale-domain yank 1.5.0                                                       # --undo puts it back
```

- `@1.5.0`, or `@2.0.0-rc.1`, is exactly that version, a pre-release or a yanked one included (a
  yanked one installs with a warning); `@1.5` is the highest stable 1.5.x that is not yanked. A
  major alone (`@1`), a range or build metadata is refused. The syntax decides: a version goes to
  the registry, a URL is installed as is, and both mix in one install.
- The CLI reads the registry with your own identity: a private Domain needs `domain_installer`,
  held directly or through a Group, and one you cannot read is reported as not found. The version
  becomes its deployment URL and release digest; the CLI checks that the deployment still serves
  that release (else PUBLICATION_RELEASE_MISMATCH), and the Kernel refuses any other. If Admin
  cannot answer, a version reference fails before any install; URLs alone read Admin only to
  propose a compatible version of a dependent the install pre-check finds broken.
- A rollback is an install like any other: the old version's deployment still serves. The Kernel
  refuses it (DATA_MIGRATION_REQUIRED) when data written since cannot be carried back.
- A fix reaches instances as a new version of the same Schema, installed on each instance; no code is
  ever swapped under a published URL.
- Yanking stops line references from choosing a version: installations keep running and its
  deployment keeps serving. Retiring a deployment, which then answers DEPLOYMENT_RETIRED, is another
  act.

## Secrets of a deployment

Secrets belong to the publisher: each Environment declares its secrets file (`astrale({ secrets:
'.env.staging' })`), and no instance provides secrets to a Domain it installs.

- A deploy binds the Environment's current secrets to the new deployment only; every other
  deployment keeps its own.
- A secret rotates in place on one deployment, which keeps its script, URL, issuer and key, so
  nothing is reinstalled: deploy the identical release again with the new value in the secrets file
  (the deploy reuses the deployment and reports its secrets `updated`), or call the deployment's
  `setSecret` for one name it declares. Adding or removing a secret name is a new release.
- Never pass a secret value in argv, where `ps` and shell history keep it: write it to a private file
  (`umask 077`) outside the repository, or pipe it from your secret manager.

A deployment on the Admin instance's Services (adapter-astrale) is listed by
`astrale-domain list --json` with its `callTarget.path`, `@<id>::services.astrale.ai:class.CloudflareDeployment`.
Call its `setSecret` on the Admin instance (`--admin`, or `--admin=<bookmark>` when `callTarget.admin`
names one) as an identity of the organization holding its line, with the input in a private file
(`{"name":"API_TOKEN","value":"..."}`) or piped from the command that prints only the new value
(`read-new-secret` below):

```sh
astrale-domain list --environment production --json
astrale call "@$ID::services.astrale.ai:class.CloudflareDeployment.method.setSecret" \
  --admin -d @rotate.json --json
read-new-secret | jq -Rs '{ name: "API_TOKEN", value: rtrimstr("\n") }' \
  | astrale call "@$ID::services.astrale.ai:class.CloudflareDeployment.method.setSecret" \
      --admin -d - --json
```

The reply is `{ "name": "API_TOKEN" }`, and the new value is served about 4 s later. `secret-undeclared` means that release declares no such
name; `service-unavailable` with `retryAfter` asks for the same call again later.

A deployment in the platform dispatch namespace (adapter-cloudflare `namespace` mode: Shell, the
Services runtime and the other platform Domains) has no Services node. Services operators rotate it
with that namespace's per-script tooling, which reads the value on stdin
(`pnpm provider:platform-secret -- --label <label> --name <NAME> < value-file` in the Services
package of the `domains` repository), or by deploying the identical release again.

After a leak, put the new value in the secrets file and every CI secret store first (an identical
redeploy with the old value would write it back), rotate every deployment that still serves, then
revoke the old value where it was issued.
