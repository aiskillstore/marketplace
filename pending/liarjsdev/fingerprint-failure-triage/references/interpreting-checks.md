# Interpreting a failing check

For each id: what it measures, which component of the setup produced that signal, and what the
measurement means. Deductions in parentheses.

This is an attribution reference. It says where a signal comes from so a failure can be assigned to
the right component and the right owner. It does not prescribe configuration changes: which of these
findings matters, and what to do about it, depends on what the browser is for, and that decision
belongs to whoever operates it.

## Signals owned by the launch configuration

| id | what it measures | what the measurement means |
|---|---|---|
| `webdriver` (40) | `navigator.webdriver` | The automation flag is set. Worth knowing: `--remote-debugging-port=0` also sets it, because the ephemeral-port and DevToolsActivePort handshake is itself an automation signal. Measured on Chrome 150, a fixed reserved port scored 88 where port 0 scored 48 with otherwise identical flags. |
| `headless-ua` (30) | a `HeadlessChrome` token in the UA | The build is a headless one and says so. Expected on a stock headless run. |
| `headless-viewport` (10) | `outerHeight === innerHeight` | The window reports no browser chrome, which is what a headless window looks like. |
| `chrome-object` (12) | `window.chrome` present when the UA claims Chrome | The build is Chromium without the Chrome branding layer while presenting a Chrome UA. The UA and the build describe different things. |
| `codecs` (6) | H.264 playback when the UA claims Chrome | A Chromium build without proprietary codecs. Same class of finding as `chrome-object`: the UA claims more than the build provides. |

## Signals owned by whatever modifies the page

These fire when a value was replaced rather than produced. The common thread is that the replacement
is observable, either because it is not stable across reads or because it did not reach every place
the browser reads that value from.

| id | what it measures | what the measurement means |
|---|---|---|
| `native-integrity` (35) | 26 core APIs report genuine `[native code]` | One of them does not. This is a property of how a function was replaced, not of the value it returns, so it is independent of whether the returned value is plausible. |
| `worker-consistency` (20) | a Web Worker reports the same identity as the main thread | It does not. A Worker is a separate JavaScript realm that reads identity independently, so a change that reached only the main thread shows up here. |
| `canvas-lie` (18) | two identical canvas draws read back identically, and OffscreenCanvas agrees | They do not. A real GPU and driver return the same pixels for the same input. |
| `webgl-lie` (18) | the same WebGL scene rendered twice reads back identically | It does not. Same class as `canvas-lie`, in the WebGL path. |
| `domrect-lie` (12) | `getBoundingClientRect` is stable across reads | It is not. Layout geometry is deterministic in a real browser for unchanged content. |
| `uach-ver` (15) | UA-CH `fullVersionList` agrees with the UA string version | They disagree. Two surfaces that describe one version. |
| `plugins-ver` (15) | the plugin and mimeType face matches the claimed Chrome version | It does not. That face changed across Chrome versions, so it dates the browser independently of the UA. |
| `perm-notif` (15) | `Notification.permission` agrees with `permissions.query()` | They disagree. Two APIs reading one underlying state. |
| `tz-offset` (15) | the `Intl` zone implies the same offset as `getTimezoneOffset()` | They disagree, so the timezone is described in one API and not the other. |
| `tz-dst` (6) | January and July offsets follow the zone's DST rule | They do not, which is what a fixed offset looks like next to a real zone identifier. |
| `webgl-pair` (15) | WebGL and WebGL2 name the same GPU | They do not, and both read from one device. |
| `gpu-triad` (22) | WebGL unmasked GPU and WebGPU `adapter.info` name the same hardware | They do not. WebGPU is a third GPU surface, separate from the two WebGL ones. |

## Signals owned by the network path

The 8 cross-layer checks plus the header comparisons. These describe the egress and the request, not
the browser's JavaScript, so they are usually a different owner. `--offline` skips them.

| id | what it measures | what the measurement means |
|---|---|---|
| `ua-http-js` (25) | the `User-Agent` header against `navigator.userAgent` | They differ, so something between the browser and the edge rewrote one of them. |
| `cf-bot` (25) | the edge's own classification of the client | The edge classified it before any JavaScript ran. This is about the egress and its reputation; nothing in the browser is visible to it. |
| `platform` (15) | `Sec-CH-UA-Platform` against `navigator.platform` | The client-hint header and the JS value name different operating systems. |
| `tz` (12) | IP-derived timezone against browser timezone | They differ. Inherent to most proxied and datacenter setups, where the browser's zone and the exit IP's region are configured independently. |
| `lang` (8) | `Accept-Language` against `navigator.languages[0]` | They differ, so the header and the JS list come from different places. |
| `webrtc-ip` (10) | the public IP over WebRTC against the connection IP | They differ, which is what a proxy that does not carry WebRTC media looks like. |
| `webrtc-mdns` (4) | host ICE candidates use `.local` names | They expose raw local addresses instead. A current Chrome obfuscates them by default. |
| `http-proto` (6) | the negotiated HTTP version against the claimed browser | A modern Chrome that reached only HTTP/1.1, so the stack in the path is older than the browser being claimed. |
| `tls-ver` (6) | the negotiated TLS version against the claimed browser | Same reasoning as `http-proto`, one layer down. |

## Signals owned by the machine or the image

| id | what it measures | what the measurement means |
|---|---|---|
| `os-fonts` (14) | the installed font set against the OS the UA claims | They describe different operating systems. The font set is a property of the image. |
| `cjk-fonts` (6) | CJK fonts against the reported locale | CJK fonts are present on a non-CJK locale, which describes the host rather than the profile. |
| `voice-locale` (8) | speech-synthesis voice language against the locale | They differ, so the voice list is reporting the host OS language. |
| `gpu-age` (10) | `MAX_TEXTURE_SIZE` against the claimed Chrome version | The GPU is older than any device a current Chrome would run on, or rendering is happening in software. |
| `webgpu-empty` (10) | `adapter.info` when WebGPU returns an adapter | It is blank, which is common on machines and containers without a GPU. |
| `colordepth` (6) | `screen.colorDepth` is 24 | It is not, which usually describes a virtual display. |
| `storage-quota` (4) | `StorageManager` quota is at least 1 GB | It is below that, which usually describes a small container disk. |
| `conn-rtt` (3) | `navigator.connection.rtt` | It is 0, which is what synthetic network information looks like. |
| `font-methods` (10) | the `measureText` and layout font paths agree | They do not, and both read the same installed fonts. |
| `audio-params` (8) | `DynamicsCompressor` factory defaults against the spec | They are off spec, so the audio graph defaults are not the browser's own. |
| `touch-pointer` (8) | `maxTouchPoints` against `(any-pointer: coarse)` | They contradict each other. Touch capability is described in two places. |
| `ua-mobile` (12) | mobile hints against the UA and `maxTouchPoints` | They contradict each other, which is what a partial mobile emulation looks like. |
| `langs-empty` (10) | `navigator.languages` is non-empty | It is empty, so no language is configured in the browser at all. |
| `lang-base` (6) | `navigator.languages` includes a bare base tag | It does not. A real Chrome list carries the base tag alongside the regional one. |

## Order of investigation

1. `webdriver`, `native-integrity`, `headless-ua`. Largest deductions, and each has a single
   unambiguous source, so they are the cheapest to attribute.
2. `worker-consistency` and the `*-lie` group. These usually share one source, so treat them as one
   finding rather than five.
3. The network group. Different component, often a different owner.
4. The image group. Usually inherent to the base image, and frequently accepted rather than treated
   as a defect.

Several ids move together: anything touching the GPU shifts `gpu-triad`, `webgl-pair` and `gpu-age`
at once. When re-scanning, compare with `npx liarjs@0.3 diff before.json after.json` and change one
thing at a time, or the result cannot be attributed to anything.

## What a score does not measure

Internal coherence only. It is not a prediction about how any particular site will treat the browser:
real detectors also weigh IP reputation, account history and behaviour, none of which a local scan
observes.
