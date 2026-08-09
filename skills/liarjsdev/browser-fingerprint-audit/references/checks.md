# The 40 checks

Each check has an id, a maximum deduction, and a layer. 32 checks need only the browser and run
under `--offline`. 8 compare the JavaScript story against what the wire actually carried; with
`--offline` those 8 are skipped rather than failed, and the report says so.

## JS layer (32 checks, run anywhere)

| id | what it measures | max deduction |
|---|---|---|
| `webdriver` | `navigator.webdriver` is set, the automation flag | 40 |
| `native-integrity` | core APIs are not genuine `[native code]`, so something patched them in JS | 35 |
| `headless-ua` | a `HeadlessChrome` token is present in the user agent | 30 |
| `gpu-triad` | WebGL unmasked GPU disagrees with WebGPU `adapter.info` identity | 22 |
| `worker-consistency` | a Web Worker reports different identity values than the main thread | 20 |
| `canvas-lie` | two identical canvas draws read back differently, or OffscreenCanvas disagrees | 18 |
| `webgl-lie` | the same WebGL scene rendered twice reads back different pixels | 18 |
| `webgl-pair` | WebGL and WebGL2 name different GPUs on one machine | 15 |
| `uach-ver` | UA-CH `fullVersionList` does not match the version in the UA string | 15 |
| `plugins-ver` | the plugin and mimeType face does not match the claimed Chrome version | 15 |
| `perm-notif` | `Notification.permission` disagrees with `permissions.query()` | 15 |
| `tz-offset` | the `Intl` timezone implies a different offset than `getTimezoneOffset()` | 15 |
| `os-fonts` | the installed font set describes a different OS than the UA claims | 14 |
| `ua-mobile` | mobile hints contradict the UA string or `maxTouchPoints` | 12 |
| `domrect-lie` | `getBoundingClientRect` is unstable across reads | 12 |
| `chrome-object` | the UA claims Chrome but `window.chrome` is missing | 12 |
| `langs-empty` | `navigator.languages` is empty | 10 |
| `gpu-age` | the GPU is too old to be real for a current Chrome, by `MAX_TEXTURE_SIZE` | 10 |
| `webgpu-empty` | WebGPU returned an adapter but `adapter.info` is blank | 10 |
| `headless-viewport` | `outerHeight === innerHeight`, so the window reports no browser UI | 10 |
| `font-methods` | the `measureText` and layout font-detection paths disagree | 10 |
| `audio-params` | `DynamicsCompressor` factory defaults are off spec | 8 |
| `voice-locale` | speech-synthesis voice language differs from the locale, leaking the host OS language | 8 |
| `touch-pointer` | `maxTouchPoints` contradicts `(any-pointer: coarse)` | 8 |
| `codecs` | claims Chrome but cannot play H.264, which describes a plain Chromium build | 6 |
| `cjk-fonts` | CJK fonts installed on a non-CJK locale, leaking the host region | 6 |
| `colordepth` | `screen.colorDepth` is not 24 | 6 |
| `lang-base` | `navigator.languages` lacks a bare base tag such as `en` | 6 |
| `tz-dst` | the reported January and July offsets do not match the zone's DST rule | 6 |
| `storage-quota` | `StorageManager` quota is below 1 GB | 4 |
| `webrtc-mdns` | host ICE candidates expose raw local addresses instead of `.local` | 4 |
| `conn-rtt` | `navigator.connection.rtt` is 0 | 3 |

## Cross-layer (8 checks, need the network endpoint)

| id | what it measures | max deduction |
|---|---|---|
| `ua-http-js` | the `User-Agent` header differs from `navigator.userAgent` | 25 |
| `cf-bot` | the edge already classifies the client as a known bot | 25 |
| `platform` | `Sec-CH-UA-Platform` differs from `navigator.platform` | 15 |
| `tz` | the IP-derived timezone differs from the browser timezone | 12 |
| `webrtc-ip` | the public IP exposed over WebRTC differs from the connection IP | 10 |
| `lang` | `Accept-Language` differs from `navigator.languages[0]` | 8 |
| `http-proto` | a modern Chrome that negotiated HTTP/1.1 | 6 |
| `tls-ver` | a modern Chrome that negotiated TLS below 1.3 | 6 |

## The 19 probes behind them

navigator and UA-CH high-entropy values, plugins, `webdriver`, screen and DPR and colorDepth,
`Intl` timezone and locale, canvas with a double-read stability test, OffscreenCanvas, WebGL,
WebGL2, WebGPU `adapter.info`, audio via OfflineAudioContext, `DynamicsCompressor` defaults,
DOMRect stability, 220 fonts over three detection paths including a CJK leak probe, WebRTC ICE,
permissions, speech-synthesis voices, a Web Worker cross-thread identity comparison, and
`[native code]` verification of 26 APIs.

## Known limits

- Cloudflare does not expose a raw JA3 or JA4 on non-Enterprise plans, so the TLS checks use
  ClientHello length plus extension and cipher hashes, not a full fingerprint string.
- Checks drift with Chrome. Plugin faces, UA-CH shapes and GPU expectations change; the rules are
  versioned with the package and reviewed per Chrome major.
- Some checks cannot hold in some environments. A datacenter IP will always trip `tz`. Compare
  against a saved baseline instead of an absolute floor when that is the case.

Source of these rules: `@liarjs/checks` on npm, MIT licensed. Per-check field notes:
<https://liarjs.dev/cli/>.
