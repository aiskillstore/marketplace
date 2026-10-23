# Installations, updates and reuse

Read this to find the Hypit already available, install a missing executable, update a selected
installation, or continue a production without discarding its tools and material.
[Services](model-and-provider.md) owns account and model access; [Profile](profile.md) owns execution
selection; [local tools](local-tools.md) owns preparation after that selection.

Go to [locating the executable](#find-the-installation-already-available),
[installation](#install-the-executable-package), [reuse](#reuse-what-already-serves-the-production),
or [updates](#let-the-installation-channel-own-updates) for the current question.

## Keep three lifecycles separate

| Part | What it supplies | Where changes belong |
| --- | --- | --- |
| Hypit Skill | Production judgment and navigation | The Skill's own installation channel |
| Executable Distribution, `@hypit/hypit` | CLI, embedded Core and product-selected default packages | Its npm/release installation |
| Video project | Sources, Runs, assets, project packages, selected Profile and Results | The project's files and package lock |

An installed Skill does not install the executable. Installing the executable does not connect an
account, supply model credits, or prepare every browser and model. Updating either does not itself
rewrite a project's Sources or regenerate its Outputs.

Work from the actual Agent environment: file access, command execution, service connectivity, and
a way to return media or previews. In a remote environment, processes, files and localhost URLs belong
to that host. Use its preview forwarding and persistent storage. A production does not need a
contributor checkout merely because the Agent can read Hypit's source.

## Find the installation already available

Use the relevant observations from the project directory:

```bash
hypit version
hypit paths
hypit --help
```

`version` identifies the active executable and launcher without opening a Runtime.
`paths` identifies the project, selected Profile, Distribution and host locations. A missing Profile
is a configuration question, not evidence that Hypit needs reinstalling.

If the shell cannot find the executable, inspect existing package records:

```bash
npm ls @hypit/hypit --depth=0
npm ls --global @hypit/hypit --depth=0
npm prefix --global
```

A project installation runs through `npm exec --no -- hypit version`; `--no` declines npm's offer to
install a missing package. A global installation's executable directory is normally
`<prefix>/bin` on POSIX or the prefix itself on Windows. Use the selected installation's launcher
and inspect its reported version; a global command and a project-local command may select different
releases. Record the useful command and location in project notes when resuming will need them.

## Install the executable package

For a machine-wide published installation:

```bash
npm install --global @hypit/hypit
```

For a project that deliberately keeps the executable in its dependencies:

```bash
npm install --save-dev @hypit/hypit
npm exec --no -- hypit version
```

Use the project's chosen package manager and version when specified. Its package manifest and
lockfile own physical versions. A supplied release tarball can also be installed through npm, for
example `npm install --global /path/to/hypit-release.tgz`.

A registry's missing version is an availability fact for that registry. Preserve the chosen version
when investigating a stale mirror or slow download; [network preparation](local-tools.md#make-network-preparation-practical)
explains matching the remedy to the actual download. Verify the active launcher after installation,
then continue with the capability needed by the work.

## Reuse what already serves the production

| Existing work | How to carry it forward |
| --- | --- |
| A suitable executable | Use it across projects; identify the active launcher before adding another installation |
| A chosen service and stored credential | Reuse its explicit Profile selection and CredentialRef within the user's account choice |
| Prepared local tools or model weights | Inspect the selected Provider's actual paths and configuration; reuse compatible resources there |
| Project components and dependencies | Keep their package versions and lockfile; edit the project's own implementation where needed |
| Generated or processed Outputs | Select them explicitly as Run Candidates so the next Build does not repeat that work |

Host tools and prepared resources have their own locations; creating another video project does not
require copying a Python environment or browser into it. An existing cache can reduce preparation
without selecting a different model, language, account or browser.

For cross-project component reuse, follow [component sharing](../production/component-sharing.md):
keep project components with their project, or explicitly install an owner's versioned package when
sharing is needed. Its ordinary package manifest and lockfile select the implementation. Update that
dependency deliberately; a Hypit or Skill update does not upgrade every project's component packages.

Preserve project assets, Results and current Run selections during an update. A newer executable is
not a reason to regenerate accepted material. [Output reuse](../production/authoring.md#reuse-produced-work-explicitly)
owns choosing compatible produced values, including useful Outputs from failed Builds.
If a release changes authoring requirements, make the relevant project change explicitly from its
documented meaning rather than guessing a migration or silently substituting another capability.

## Let the installation channel own updates

Check versions when a reported fix, missing capability, update request or release change matters to
the work. Continue ordinary production on its selected versions; Build does not upgrade them.

```bash
hypit version --check
```

This read-only query reports npm release information and its source. `--registry <url>` selects a
registry for the check; `--json` gives structured output. Local `hypit version` and `--version`
do not contact a registry. With an older executable lacking the command, use
`npm view @hypit/hypit@latest version` through the project's configured registry.

A failed query leaves the remote release unknown. A different version can mean a newer checkout or
a stale mirror. Read the relevant [release notes](https://github.com/hypit-ai/hypit/releases) and
explain which installation and behavior would change.

## Check and update the relevant installation

When the chosen target is the latest published release, update the selected installation only:

```bash
npm install --global @hypit/hypit@latest
```

For the project-local development dependency shown above, run instead from that project:

```bash
npm install --save-dev @hypit/hypit@latest
npm exec --no -- hypit version
```

Use an exact selected release instead of `latest` when the user or project pins one, and preserve
the existing dependency kind and package-manager workflow. These are alternative installation scopes,
not two steps to run together. Recheck the launcher the production will actually use.

The Skill updates separately. For an installation managed by the
[skills CLI](https://github.com/vercel-labs/skills#skills-update), inspect its installed records and
current supported options. The following targets only the globally installed Hypit Skill:

```bash
npx skills list -g
npx skills update hypit -g
```

For a project-scoped installation, use the installer's project scope (`-p` on `update`) from that
project. A local checkout or another installer keeps its own update method. The update command is a
mutation, not a read-only version check; preserve intentional local Skill edits before replacing them.
Do not update unrelated skills as a side effect. Read the updated instructions from the installation
the Agent actually uses; content already loaded in a conversation can still be the old text.

The installed packages' vocabulary and README describe their available interfaces. If a newer Skill
mentions an absent option, inspect the selected package and release. Explain the missing capability
and the useful update or explicitly chosen alternative; do not pretend the option already exists.

## Project changes and execution code

Project component and Profile changes apply to a new Build through its execution context. Updating
the Distribution or the environment inherited by an active Worker concerns that process's lifetime.
Use [configuration changes](profile.md#know-when-a-change-takes-effect) before restarting it, and
preserve active work and accepted Outputs.

Every npm package carries its ordinary code dependencies in its own manifest and lockfile context.
The package manager installs them with the Distribution or project that owns the package. Runtime
preparation is reserved for Provider-declared Programs and other runtime materials; it does not create
a second npm installation plane.

A contributor checkout is an explicit development choice. Use one when the user has selected it;
ordinary production, project components and project Model/Provider extensions use the installed
public interfaces.
