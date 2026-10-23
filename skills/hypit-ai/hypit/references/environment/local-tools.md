# Local tools and Managed Programs

Read this when assessing local preparation, selecting local WhisperX, or preparing and repairing a
local Endpoint's executable or Managed Program.

Go to [host tools](#supply-host-executables-at-machine-scope),
[local media configuration](#configure-local-media-tools),
[Program lifecycle](#let-the-selected-endpoint-own-its-program),
[render browser](#prepare-the-local-rendering-browser),
[WhisperX](#select-local-whisperx-explicitly), or
[downloads and mirrors](#make-network-preparation-practical) as needed.

## Assess local preparation

Use `hypit paths` to locate the selected Profile and machine state. Inspect relevant service
configuration, the Provider's documented installation locations, and executables such as `ffmpeg`
and `uv`. Hypit's managed WhisperX has its own Python environment; a missing global `whisperx`
command leaves that installation's state unknown. The installed `@hypit/provider-whisperx-local`
README owns its preparation and service locations.

Establish what already works, what needs starting or repair, and what needs downloads. Use those
findings in [service selection](model-and-provider.md#choose-the-practical-capability-path-with-the-user),
then prepare the chosen setup using its Provider instructions and the evidence from its logs.
Consider hardware and actual network reachability alongside installed files. A cached environment
can still need speech-model weights or a language's alignment model before its first useful request.
Existing weights can make local preparation attractive; report that fact while offering the local
and hosted choice. Starting a newly configured large-model service is preparation even when all
weights are cached. A previously chosen, working service can be carried forward directly.

Available, selected, prepared and running answer different questions. A binary on disk is not
necessarily the selected executable; a Profile declaration does not install resources; a running
speech service does not establish that a new language's aligner is cached. Check the fact the next
operation actually needs, rather than treating the machine as globally ready or unready.

## Diagnose the selected local capability

Choose the observation that answers the current question:

| Question | Tool |
| --- | --- |
| Which Profile and machine locations apply? | `hypit paths` |
| Is the Worker running, and is work active? | `hypit runtime status` |
| What has the Worker reported? | `hypit runtime logs` |
| Which selected local helpers answer, and where are their logs? | `hypit programs status --verbose` |
| Does a selected Endpoint's configuration and service access work? | `hypit doctor --endpoint <instance>` |

Read the failing Endpoint's message and package README before changing the machine. The Profile says
which local implementation was selected; another project's working service is not evidence that this
Profile selects it.

## Supply host executables at machine scope

The installed Hypit Distribution requires its supported Node.js version. Local media processing needs
both `ffmpeg` and `ffprobe` on `PATH`, or explicit compatible paths accepted by its Provider. Local
Python Programs use `uv` to create their locked environments in Hypit's machine Program Home.
Read the installed Distribution's requirements before changing Node; Skill updates do not update it.

Prepare the missing executables needed by the chosen work using the host's ordinary package manager.
For example, these commands install FFmpeg for media work and uv for managed Python tools; select
the relevant command and verify its executable in the environment that will run Hypit:

```bash
# macOS
brew install ffmpeg
brew install uv
ffmpeg -version
ffprobe -version
uv --version
```

```powershell
# Windows
winget install --id Gyan.FFmpeg.Shared -e
winget install --id astral-sh.uv -e
ffmpeg -version
ffprobe -version
uv --version
```

On Linux, use the distribution package manager or the current official installation method for the
same executables. Keep these machine tools outside the video project. `hypit paths` reports the shared
Runtime and Program state locations used by selected Runtime adapters.

### Configure local media tools

With ordinary host installations, the media and rendering Providers use `ffmpeg` and `ffprobe`
from their process `PATH`. If the deployment intentionally uses explicit binaries, merge the
actual paths into the selected Endpoint. For example, replace these illustrative absolute paths:

```json
{
  "endpoints": {
    "media.local": {
      "use": "@hypit/media-local",
      "config": {
        "ffmpegPath": "/opt/media/bin/ffmpeg",
        "ffprobePath": "/opt/media/bin/ffprobe"
      }
    }
  }
}
```

These Provider paths resolve relative to the Runtime `dataRoot` when they are not absolute.
Use forward slashes or JSON-escaped backslashes for Windows paths. The selected media Program
probes its executables; `programs prepare` does not install system FFmpeg through a package manager.
Hypit's local HTML renderer Provider also accepts `ffmpegPath` and `ffprobePath`: configure that
Endpoint as well if it needs custom paths. Configuration does not propagate from `media.local`
to an unrelated Endpoint.

A successful `-version` probe establishes executable availability, not every encoder or operation.
Read the actual media failure when a particular input or codec needs attention. New host `PATH`
settings must reach the process running the work; restarting a terminal alone does not change an
existing Worker. See [configuration changes](profile.md#know-when-a-change-takes-effect).

## Let the selected Endpoint own its Program

An Endpoint may contribute one Managed Program: prepared resources with an optional persistent
helper. A render browser needs installation but no permanently running Chrome; WhisperX needs
weights and a warm service; the media tools need executable probes. The Provider owns the applicable
preparation, start, probe and configuration declarations. Runtime operates those declarations:

```bash
hypit programs up --endpoint whisperx.local
hypit programs status --endpoint whisperx.local
```

Name the chosen Profile instance with `--endpoint`; repeat it for several services. This scopes
package preparation and Program operations together. `runtime up --endpoint <instance>` also starts
the Worker. Omitting the flag deliberately covers the whole Profile. A binding selects which Endpoint
fulfills a request; `plan` checks the Endpoints resolved for its actual requests, so an unused local
service or hosted credential does not become a prerequisite for that Build.
Program commands leave the Worker lifecycle alone:

| Intention | Command |
| --- | --- |
| Prepare resources without starting helpers | `hypit programs prepare --endpoint <instance>` |
| Prepare and start the selected helpers | `hypit programs up --endpoint <instance>` |
| Inspect their current state | `hypit programs status --endpoint <instance>` |
| Stop helpers managed by Hypit | `hypit programs down --endpoint <instance>` |

`runtime down` stops the Worker and its execution processes while leaving separately managed Programs available. This lets a later
Build reuse an already warm local model. Use scoped `programs down` when a helper itself should stop.
A healthy service stays warm across repeated `up` calls, while explicit preparation can still add
newly requested resources. Ordinary Build submission may start the Worker, but does not install
missing resources or start these external helpers. Local WhisperX reconciles its packaged Python
environment before a cold start; uv reuses cached dependencies and weights. This is separate from
loading project component code for a new Build.
A service still loading can also have a live PID: repeated `up` observes that owned process instead
of starting another one. A readiness wait can end with the process still alive. Check its probe and
log to understand why it is not Ready. Concurrent preparation of the same Program reports its
existing owner and available logs; repeating the command does not accelerate that preparation.

Ordinary projects use these declarations instead of running a service's internal `uv sync` or Python
entry point by hand. Contributor/operator commands in a service README are for diagnosing that
packaged service, not for creating a second project-local installation.

Other tools keep their own entry points. [Video downloading](../production/video-downloads.md)
uses explicit `hypit download prepare` followed by `hypit download`, without a Runtime Profile or
Build. [Image operations](../production/image-operations.md) can use the local OpenCV Provider;
its README owns the managed Python environment and optional `pythonExecutable` selection. These
tools follow the same separation of preparation and use without inventing a Profile for every utility.

## Prepare the local rendering browser

The selected HTML renderer Provider owns the browser used for rendering. Read the installed
`@hypit/provider-html-local` README for the configuration supported by that installation;
a newer Skill does not add options to an older executable. [Distribution updates](distribution.md#check-and-update-the-relevant-installation)
explains how to check and update the relevant installation when a needed option is absent.

For ordinary local rendering, use the Provider release's recommended browser. Prepare the selected
instance explicitly, substituting its actual Profile path and Endpoint name:

```bash
hypit programs prepare --runtime <profile> --endpoint <render-instance>
```

`runtime up` also prepares selected Programs and starts the Worker. Package installation alone does
not prepare the browser. `doctor` and Build preflight inspect the selected executable without
downloading it; a system Chrome installation does not establish that the selected browser is ready.
The normal declaration needs no browser version copied into every project:

```json
{
  "endpoints": {
    "html.local": {
      "use": "@hypit/provider-html-local"
    }
  }
}
```

The selected Provider release declares its recommendation. That declaration, not a system-browser
search or a moving "latest" channel, determines the managed version.

| Intent | Provider configuration |
| --- | --- |
| Use the release's recommended managed browser | Omit `chromePath` and `browserVersion` |
| Intentionally select another managed release | Set `browserVersion` to an exact four-part version |
| Reuse a chosen browser installation under the user's control | Set `chromePath` to its executable |
| Put managed downloads in another cache | Set `browserCacheDirectory` |
| Fetch missing archives from a chosen compatible source | Set `browserDownloadBaseUrl` |

`chromePath` cannot be combined with `browserVersion` or `browserDownloadBaseUrl`; invalid
combinations fail. User-managed mode never downloads or repairs the executable. Relative browser
and cache paths resolve from the Runtime `dataRoot`, not the Profile directory. The installed
Provider README owns the default cache location and accepted configuration.

Browser environment hints, other cached versions and a system Chrome installation do not override
the selection. `doctor --endpoint <render-instance>` reports that selection when diagnosis is needed.

When the browser download is blocked, choose a compatible source through the Provider's
`config.browserDownloadBaseUrl`; an npm registry mirror does not redirect browser archives.
Check the archive URL, selected version and destination shown by preparation. A failed selected
mirror reports failure without trying another source. Changing the source preserves a healthy
cached installation. Use [network preparation](#make-network-preparation-practical) to distinguish
an unavailable archive from a network problem and choose a route within the user's existing scope.
New Builds read edited Endpoint choices; a Distribution change or inherited process-environment
change has different restart requirements. Follow
[when configuration takes effect](profile.md#know-when-a-change-takes-effect).
Browser readiness is not a promise that every GPU or page will render; investigate an actual capture
failure through its render diagnostics. Do not "repair" it by quietly trying another browser.

## Select local WhisperX explicitly

Local and hosted WhisperX implement the same alignment capability. When local execution is chosen,
merge this fragment into the Profile, retaining the other services the production uses:

```json
{
  "endpoints": {
    "whisperx.local": {
      "use": "@hypit/provider-whisperx-local",
      "config": {
        "expectedModel": "small",
        "expectedDevice": "cpu",
        "expectedCompute": "int8",
        "alignmentLanguages": ["ko"]
      }
    }
  },
  "bindings": {
    "@hypit/whisperx@1#whisperx-alignment": "whisperx.local"
  }
}
```

This is a Korean alignment example on CPU using the modest-machine `small` model. Choose the actual
model and languages for the production; these are not universal quality recommendations.
The binding is needed when another selected Endpoint, such as HypiHub, also offers alignment.

| Setting | What it selects |
| --- | --- |
| `expectedModel` | Speech-recognition model loaded by the service |
| `expectedDevice`, `expectedCompute`, `expectedBatchSize` | Inference hardware, representation and batch budget |
| `alignmentLanguages` | Language-specific alignment resources to prepare |
| `modelCacheDirectory` | Optional cache root with Hugging Face and Torch subdirectories; relative to Runtime `dataRoot` |
| `baseUrl` | This local Provider's loopback service address; separate services need separate addresses |
| `serviceCommand` | Optional operator-managed compatible service installation/start command |

The installed Provider README owns exact fields, defaults, device support and service identity.
Apple Silicon does not imply CUDA support. The loopback service accepts canonical speech evidence
and returns measured alignment; it does not interpret Script, Caption Cues, or Semantic Segments.
The authored request's language and the Profile's preparation list have separate purposes:
`alignmentLanguages` prepares resources, while the request selects which language to use.

Choose the ASR model deliberately for the language, hardware and work. For quality-oriented
multilingual work, a multilingual large model is a useful starting preference when hardware and
preparation are practical. A ready smaller model can serve straightforward reference understanding
on a modest CPU machine; its availability is more informative than the ability to begin a larger
download. Weigh accuracy needs against setup and inference time, including the hosted option.
The Provider README owns exact settings, compute choices and the distinction between transcription
and language-specific alignment. Configure the chosen model before preparing it.

Set `alignmentLanguages` to this production's actual languages; retain other languages still needed.
For example, change `["ko"]` to `["ko", "en"]` when English alignment is also needed, then prepare:

```bash
hypit programs prepare --endpoint whisperx.local
hypit programs up --endpoint whisperx.local
```

The first command prepares the Python environment, selected ASR model, requested alignment weights
and sentence data without starting the service. The second also performs preparation if needed,
then starts the helper. Use `runtime up --endpoint whisperx.local` instead when the Worker should
start too. Startup and inference only read prepared resources.

The language list is a preparation demand, not an allowlist blocking other supported cached
languages. Omitting it does not prepare every language. Native cache reuse depends on the chosen
model/cache settings, not a separate Hypit resource catalogue.

A healthy service does not imply every language is prepared. Add a newly needed language to the
Profile and run `programs prepare` even if the service is online. Keep its cache selection unchanged
when adding resources to that running service. A missing language resource fails with an explicit
preparation instruction; do not retry inference hoping it will download weights. The Provider README
owns optional model cache selection. Native upstream caches remain reusable by default.
Changing the running service's model, device, compute, batch size or cache requires an explicit
helper restart when idle. Prepare the new resources first; stop with scoped `programs down` and
start with scoped `programs up`. Restarting only the Worker does not restart WhisperX.

## Make network preparation practical

Treat preparation as part of delivering the video. Read the current command and its progress:
which dependency or weight file, which download host, how much data has arrived, and whether the
process is downloading, unpacking or loading a model. Managed Program preparation reports `install.log`;
service startup reports `program.log`. On Windows, service stderr is in the adjacent `program.err.log`.
Model-loading and inference diagnostics belong there; download diagnostics belong to preparation. Read the relevant recent output while a long
command runs. Logs expose the subprocess's output; some downloaders suppress progress outside a terminal.
`programs status` reports existing installation and service log paths, including when preparation has
not yet started the service. These files retain history; their presence does not mean work is active.
`--json` keeps the final result on stdout and sends live preparation notices to stderr. WhisperX's own
log distinguishes ASR loading, transcription, first-use loading of prepared language models and
word alignment. Loading cached weights into memory is not downloading them.
Use available transfer progress, cache growth and process activity to judge whether waiting remains
reasonable for this commission; a quiet log alone does not establish a stalled download.
A longer timeout helps a healthy slow transfer finish; it does not improve an unusable route.
Use each observation to decide whether to wait, change a download route or recommend another service,
and share what that means for the piece. Let the process carry out a known wait while you advance
independent work; reading the same output repeatedly adds no new evidence.

Mainland China and other restricted networks can make particular hosts slow or unreachable. Use the
user's network context and actual transfer evidence to choose a reachable source, rather than
inferring connectivity from the language they speak. Preserve useful downloads and caches while
changing the part that is actually blocked. Explain the changed outlook promptly and recommend
a practical alternative when local preparation would dominate the production time. HypiHub can
remove local speech-model preparation and also supply later generation; the account choice remains
with the user. Continue independent reference and component work meanwhile.

A **mirror** is an alternative server supplying copies of packages or model files. It can provide a
better route when the original host is slow or unreachable. It changes where bytes are acquired;
the selected dependency versions and model still define what runs. It neither replaces the Provider
nor pays for generation. A cache already contains downloaded files and may avoid that transfer;
a proxy routes requests to their original destinations. Choose the remedy for the blocked resource.

Mirrors address particular download clients and hosts:

| Download | Relevant controls and limits |
| --- | --- |
| npm packages | A command's `--registry` or `npm_config_registry`; a registry mirror may lag a newly published version. Check the requested package version. |
| Python packages | pip uses `--index-url` / `PIP_INDEX_URL`; uv uses `--default-index` / `UV_DEFAULT_INDEX`. They are different clients. Hypit's managed service uses frozen uv dependencies; consult its Provider README before expecting an index change to redirect locked artifact URLs. |
| Python runtime | uv's `UV_PYTHON_INSTALL_MIRROR` selects a compatible Python-distribution mirror. A PyPI mirror does not supply Python itself. An already compatible installed Python may avoid this download. |
| Hugging Face weights | `HF_ENDPOINT` selects a compatible Hub endpoint; `HF_HOME` / `HF_HUB_CACHE` select reusable cache locations. A model's redirected weight host and its language-alignment download must also be reachable. |
| NLTK sentence data | If preparation reports `NLTK_ALLOW_PROXIED_URLOPEN`, the downloader needs an explicit trust decision for the configured proxy. For a trusted proxy, set that native variable to `1` only on the preparation command; do not switch it on automatically or change inference. |
| HTML renderer browser | The selected Provider owns the archive source; follow [browser preparation](#prepare-the-local-rendering-browser) and its installed README. |
| FFmpeg and other binaries | Use the selected package manager's binary-download settings or a compatible official prebuilt installation. An npm/PyPI mirror does not generally redirect these downloads. Homebrew bottles and GitHub release assets have their own sources. |

Make a route change explicit: explain the blocked download, the proposed source and which command
or service will use it. Use a mirror the user or organization trusts, with settings scoped to the
preparing command or session. An established preparation choice can cover this work; an unresolved
trust or machine-wide configuration choice belongs with the user. Keep the selected package
versions and record the effective preparation choices for the next session. Read the actual download
host afterward to establish that the intended route was used.

For example, after choosing local WhisperX and a trusted compatible Hugging Face mirror, pass its
URL to preparation. Replace this illustrative address with the chosen real source:

```bash
HF_ENDPOINT=https://hf-mirror.example hypit programs prepare --endpoint whisperx.local
```

In PowerShell, scope the environment change and restore the previous setting:

```powershell
$previousHypitHfEndpoint = $env:HF_ENDPOINT
try {
  $env:HF_ENDPOINT = 'https://hf-mirror.example'
  hypit programs prepare --endpoint whisperx.local
} finally {
  $env:HF_ENDPOINT = $previousHypitHfEndpoint
}
```

A download-source change does not require restarting an already running service when the selected
cache is unchanged. Preparation writes resources there; inference reads those prepared files.
Changing cache environment or service settings does require an idle restart so the process sees
the new selection. Inspect the transfer host and progress in `install.log`: setting a variable is
a request to that client, not evidence that every weight download used the mirror.
A Hugging Face route does not redirect Torch alignment models fetched from other hosts.

For npm, a read-only check such as
`npm view @hypit/hypit versions --json --registry https://registry.npmmirror.com`
shows which releases that registry currently offers. Pass the same `--registry` to the chosen npm
installation command if it has the needed version. Python's frozen URL limitation above needs its
own solution; changing a pip setting cannot repair a uv download.

Useful source documentation includes [uv settings](https://docs.astral.sh/uv/reference/environment/),
[TUNA's PyPI mirror](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/),
[TUNA's Homebrew guidance](https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/),
[npmmirror](https://npmmirror.com/) and [HF-Mirror](https://hf-mirror.com/).
These are available choices to assess, not automatic machine defaults. A mirror that returns model
metadata successfully may still redirect large files to another host; diagnose the transfer itself.

## Repair from the narrowest evidence

- A missing executable belongs to host installation and `PATH`.
- An npm dependency declared by a selected adapter belongs to the package manager and lockfile of
  the Distribution or project that installed that adapter. `programs prepare` / `programs up` prepare
  only Provider-declared runtime materials; `runtime up` also starts the Worker.
- A down or mismatched Managed Program belongs to its Provider configuration, Program status, and
  service log.
- A healthy local Program with a rejected request belongs to the Provider's support or request error,
  not to reinstallation.
- A remote authentication, account, quota, or model-catalogue error belongs to the remote Endpoint and
  [service connection](model-and-provider.md), even when the Worker happens to run locally.

Project component and Profile edits apply to the next Build through its fresh execution context.
For a Distribution or inherited shell-environment change, read
[Build execution](../production/builds.md#build-with-the-current-project-implementation) before
restarting the coordinator so active work is preserved.
