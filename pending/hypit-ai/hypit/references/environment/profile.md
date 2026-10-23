# Configure the Runtime Profile

Read this when selecting a project's execution environment, wiring Endpoints and credentials,
setting shared capacity, or deciding when a configuration change takes effect.
[Models and Providers](model-and-provider.md) owns service choice and BYOK;
[local tools](local-tools.md) owns preparation and process management.

Go to [Profile selection](#create-a-profile-when-the-project-needs-one),
[configuration structure](#read-and-edit-the-actual-configuration),
[routing](#connect-model-capability-need-and-endpoint),
[credentials](#put-secrets-behind-credential-references),
[capacity](#set-capacity-at-the-resource-it-describes), or
[change effects](#know-when-a-change-takes-effect) as needed.

## Create a Profile when the project needs one

From the project directory:

```bash
hypit runtime init
hypit paths
```

`runtime init` writes and selects an editable starter `hypit.runtime.json`. It preserves an existing
Profile and performs no installation or login. Its hosted generation/alignment, local media and local
rendering entries are initial routing choices, not a requirement to prepare every service for every
video. Keep the entries and bindings appropriate to the work and the user's chosen setup.

Use `hypit runtime use <profile>` to record an existing Profile for this project.
`--runtime <profile>` selects one for a single invocation. Commands read the project's
`.hypit/runtime` selection file; they do not guess from a familiar filename or another project's
selection. From elsewhere, `hypit paths --project /path/to/project` inspects that project. The same
project option applies to environment commands and Build status/control. See the
[project boundary](../creation/project-files.md#establish-the-project-boundary).

Keep these locations distinct:

| Location | Responsibility |
| --- | --- |
| Project directory | Sources, Runs, assets and component dependencies |
| `.hypit/runtime` | File naming the selected Profile |
| Profile file | Editable execution choices; may be shared intentionally |
| Profile `dataRoot` | Execution data, Worker state and working files; relative to the Profile's directory |
| Host state / Program Home | Machine-level prepared packages and helpers, reported by `hypit paths` |
| Project `.hypit/results` | Finished Results and Outputs owned by this project |

The selection file and execution directory must be different paths. CLI, Studio and creation
commands address the same project context; there is no second CLI environment to initialize.
Installed code, selected configuration and existing execution data remain separate.

## Read and edit the actual configuration

A complete minimal Profile for credential-free local media work is:

```json
{
  "format": "hypit.runtime-local@1",
  "dataRoot": ".hypit/execution",
  "credentials": {},
  "endpoints": {
    "media.local": {
      "use": "@hypit/media-local"
    }
  },
  "bindings": {}
}
```

This selects media processing only. It needs compatible FFmpeg and FFprobe supplied by the host;
it does not install them, select an image model, or render HTML renderer pictures. Use it when those
are the actual requirements, not as a replacement for a production's existing Profile.

| Field | How to choose it |
| --- | --- |
| `credentials` | Named Credential Store adapters; empty when no selected Endpoint needs a secret |
| `endpoints` | Named Provider instances. `use` selects the package; its README defines `config` |
| `bindings` | Complete capability keys mapped to Endpoint instance names |
| Endpoint `pool` | Optional identity of a real shared account, deployment or compute quota |
| `dataRoot` | Where this Runtime keeps execution state; changing it selects different state |
| Optional `worker.executionMemoryMb` | Memory budget for Build execution processes; startup policy owned by the Runtime package |

Merge documentation fragments into the corresponding existing objects. Retain other services,
credential references and bindings the project uses. A fragment without `format` and `dataRoot`
is not a complete Profile. Package installation makes an adapter available; declaring it here
selects an instance. Configuration keys belong to that package, so a `baseUrl` or `apiKey` field
from one Provider is not a universal schema for all Providers.

## Connect Model, capability, Need and Endpoint

The [Model and Provider roles](model-and-provider.md#start-from-the-capability-the-work-needs)
keep authoring separate from deployment. One authored request produces a concrete external **Need**
only if its output remains demanded by the Run. Existing Result Candidates can satisfy that output
without another generation request.

A **capability** identifies the required operation. The Profile routes it to an **Endpoint**, a
configured Provider instance. A **binding** is that explicit routing choice. For example, after
declaring and configuring `whisperx.local`, merge:

```json
{
  "bindings": {
    "@hypit/whisperx@1#whisperx-alignment": "whisperx.local"
  }
}
```

Use the complete capability key from the Model/Provider vocabulary, not a vendor model label.
The named Endpoint must actually offer it and support the concrete request. One eligible Endpoint
needs no binding; several unbound choices are an error, not a fallback order. This lets the same
Source use local alignment in one deployment and hosted alignment in another.

Explicit bindings let capability-scoped commands load the named Endpoints directly. Without a
binding, discovering eligible implementations can require loading the declared Endpoint packages;
an uninstalled declared package can therefore block discovery. Correct the declaration or select
the intended binding. An unused account need not be logged in merely to resolve the work.

The complete local alignment example is in
[local WhisperX](local-tools.md#select-local-whisperx-explicitly). Hosted and BYOK examples are in
[service connections](model-and-provider.md). Result storage and project-package resolution are
separate from this routing.

## Put secrets behind credential references

A Profile names a Store and a key. The value stays in that Store.

| Store package | Storage and use |
| --- | --- |
| `@hypit/credential-store-local` | Writable local credentials: macOS Keychain, Windows Credential Locker, or an owner-private file on Linux; set `backend: "file"` to choose files explicitly |
| `@hypit/credential-store-env` | Reads one named environment variable; read-only |

The local Store selects by operating system; it is not a sequence of stores to try.
A read failure never migrates a secret or falls back to another Store. Preserve an existing choice.
The local Store's default file directory is under the Host state root shown by `hypit paths`;
its optional `config.path` chooses a private directory. Read that Store's installed README for path
and platform rules, including filesystem permissions.

To select a Store explicitly, name it under `credentials` and use that name in the Endpoint's
credential reference. A credential-free Endpoint needs no auth command; prepare its tools directly.

For example, these are the Store declaration and credential reference used by a HypiHub Endpoint:

```json
{
  "credentials": {
    "local": { "use": "@hypit/credential-store-local" }
  },
  "endpoints": {
    "hypihub.default": {
      "use": "@hypit/provider-hypihub",
      "config": {
        "apiKey": { "store": "local", "key": "hypihub.oauth" }
      }
    }
  }
}
```

After the user has chosen that account connection:

```bash
hypit auth login hypihub.default
```

A Provider declaring browser acquisition uses that flow immediately. Otherwise, a writable Store
uses secure terminal input. `--from /private/path/key.txt` explicitly imports a secret file instead
of opening OAuth. Wait for CLI success: a successful browser callback alone does not establish
that the Store write succeeded. Login/logout can replace/remove a damaged value without reading it;
status and execution still report read errors.

For an intentionally environment-backed deployment, merge this alternative Store and change the
selected Endpoint's credential reference accordingly:

```json
{
  "credentials": {
    "env": { "use": "@hypit/credential-store-env" }
  },
  "endpoints": {
    "hypihub.default": {
      "use": "@hypit/provider-hypihub",
      "config": {
        "apiKey": { "store": "env", "key": "HYPIT_HUB_API_KEY" }
      }
    }
  }
}
```

Here `HYPIT_HUB_API_KEY` is the explicitly selected variable name. Supply it securely to both
the CLI commands that need it and the Worker process at startup. `auth login` cannot write an
environment Store. Changing a terminal's environment does not change an already running Worker.
Other services use their own Endpoint, credential slot and variable, not this HypiHub example.

Use distinct Endpoint names and credential keys for separate accounts. Binding selects which one
serves the requested capability; entering another service's key does not change the Provider.
Local credential-free Endpoints need no login. `auth status <endpoint>` reports declared slots
without revealing values; configured does not mean accepted, funded, reachable, or authorized for
every model. Keep secrets out of Sources, Runs, Profile JSON, command arguments, commits and chat.

## Set capacity at the resource it describes

The Runtime Worker advances Builds. HTML renderer `workers` counts Chrome processes inside one
render Need. These are different controls; there is no extra Build-wide model concurrency setting.

| Control | Responsibility |
| --- | --- |
| Provider request capacity, commonly `config.defaultConcurrency` | Simultaneous Needs across Builds using the resource |
| Provider-specific model/action limits | Model quota or submit/poll/collect concurrency and rate; use that Provider's accepted fields |
| Endpoint `pool` | Shared resource identity for instances consuming the same real quota |
| HTML renderer `workers`, `maxWorkers` | Per-render Chrome count or automatic ceiling |
| HTML renderer `browserCapacity` | Shared Chrome budget alongside the whole-request budget |

For example, merge this Endpoint entry for an intentionally chosen render budget:

```json
{
  "endpoints": {
    "html.local": {
      "use": "@hypit/provider-html-local",
      "pool": "local-render",
      "config": {
        "defaultConcurrency": 2,
        "workers": 4,
        "browserCapacity": 6
      }
    }
  }
}
```

Only one four-browser request fits the six-browser budget at once, even though the request limit is
two. These numbers illustrate the relationship; choose them for the actual machine. HTML renderer
reserves both budgets until the whole render finishes, including preparation and encoding.
It does not release capacity each time one browser closes.

Instances sharing a pool must agree on its limits. Separate accounts do not share one merely because
they offer the same model. Capacity coordination covers Builds sharing a Runtime Execution Store;
it is not a cross-machine account quota service. Accepted asynchronous Operations retain their task
claim while pending. Short submit/poll/collect calls have separate action budgets when declared.
Ending a Build attempt releases local claims while retaining receipts and last known remote state;
it does not imply a remote task has been cancelled.

Use `hypit activity` when actual claims matter. The installed Runtime and Provider READMEs own the
exact settings. Studio's permitted transient work has session-local concurrency.

## Ask each command for the fact it owns

| Question | Command and boundary |
| --- | --- |
| Which project, Profile and storage locations apply? | `hypit paths` |
| Is a named credential present? | `hypit auth status <endpoint>`; no account-access guarantee |
| What will this Run demand? | `hypit plan <run>`; concrete requests, support checks and cheap readiness of their selected Endpoints |
| Can the selected services be reached and used? | `hypit doctor --endpoint <instance>`; bounded active diagnosis, no generation submission |
| Is the Worker running and work active? | `hypit runtime status` |
| Which local helpers answer, and where are their logs? | `hypit programs status --endpoint <instance> --verbose` |

Choose the observation needed now; this is not a mandatory sequence before every operation.
Without a selected Profile, `doctor` checks project Results only. With one, it may contact remote
services for bounded diagnostics. `plan` does not actively probe remote services or install missing
resources. Neither command prepares every language model just because a local service is healthy.

Prepare the selected resources and start needed helpers through
[local Program commands](local-tools.md#let-the-selected-endpoint-own-its-program).
A missing capability can leave independent Script, reference or component work possible; explain
which requested outcome still depends on it. [Review](../production/review.md#show-what-the-current-work-establishes)
distinguishes useful intermediate evidence from the intended deliverable.

## Know when a change takes effect

| Change | What to do |
| --- | --- |
| Source, Run or project component implementation | Create a new Build for the changed work |
| Endpoint config or binding | New Builds read current choices; an existing Build retains its selected configuration |
| Writable Store credential value | Subsequent credential resolution uses that Store; changing a secret is not a blanket Worker restart instruction |
| Distribution installation, Worker startup policy or its inherited environment | Restart the Worker explicitly when active work permits |
| A running local service's model, device, compute, batch size or cache location | Prepare its selected resources, then restart that helper when idle |
| Additional WhisperX alignment language in the same cache | Run scoped `programs prepare`; the service can stay running |
| Browser download mirror | Used for the next required preparation; a healthy cached browser remains usable |
| Profile used by an existing Studio session | Restart the session if it needs to load the edited selection |

A new Build's execution context is not a snapshot of every external file or service.
Read [Build execution scope](../production/builds.md#build-with-the-current-project-implementation)
before restarting a coordinator or changing dependencies during active work.
Do not restart everything after every edit, or expect a completed Build to rerun itself.
