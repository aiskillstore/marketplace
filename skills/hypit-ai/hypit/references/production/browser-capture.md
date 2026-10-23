# Capturing websites and authored HTML

Read this when a page, product interface or locally authored HTML should become captured picture
material. [Screen demonstrations](../playbooks/craft/screen-demonstrations.md) owns what the screen
must show and why; this page owns how to save that material. `hypit capture` supplies browser
capture from the installed Distribution; the project's scripts describe the actual page interactions.
A captured image or recording enters the composition through Media, while an editable demonstration
can use a project component. [Spatial layout](spatial.md) owns fitting either into its destination.

## Save a page or region

```bash
hypit capture screenshot https://example.com/product \
  --viewport 540x960 --scale 2 --full-page --to assets/product-page.png

hypit capture screenshot https://example.com/product \
  --selector '#comparison' --to assets/comparison.png

hypit capture screenshot ./assets/card.html \
  --viewport 1080x300 --transparent --to assets/card.png
```

Use `--clip x,y,width,height` for a rectangular region in CSS pixels. A selector, clip or full-page
capture chooses a different extent; the default captures the viewport. Viewport and device scale
are separate: 540 × 960 at scale 2 produces a 1080 × 1920 viewport image. They are task choices;
Puppeteer's device emulation is available in a script when mobile behavior or a user agent matters.

The command waits for page load. `--wait-for <selector>` waits for a visible element, and `--wait-ms`
adds a chosen delay. If content loads through scrolling or interaction, express that in a script.
Watch the saved image to see whether it contains the intended evidence and is readable in its
destination Frame.

## Use ordinary page interactions

For several captures, lazy loading, an authenticated page or a demonstration, put the actual
interactions in a project `.mjs` file. This script needs no Puppeteer import:

```js
// scripts/capture-product.mjs
export const options = {
  launch: { defaultViewport: { width: 1280, height: 720, deviceScaleFactor: 1 } },
};

export default async ({ page, screenshot, record, args, log }) => {
  const [url, destination] = args;
  await page.goto(url);
  await page.waitForSelector('#comparison', { visible: true });
  await screenshot({ path: 'assets/comparison.png', selector: '#comparison' });

  log('Recording the product interaction');
  const recording = await record({ path: destination, fps: 30 });
  await page.click('#show-example');
  await page.waitForSelector('#example-result', { visible: true });
  await recording.stop();
};
```

```bash
hypit capture run scripts/capture-product.mjs -- \
  https://example.com/product assets/product-demo.mp4
```

The selectors above describe an example page; choose the real controls and meaningful start and end
states of the page being captured. Use normal Puppeteer navigation, locators, input and evaluation
to express the task. `browser` is also available for opening more pages; pass one as the second
argument to `screenshot` or `record` to capture it. Returning finishes open recordings and closes
the browser. Completed captures survive a later script failure.

For a scrolling demonstration, identify the container that actually scrolls; a gallery may move
inside a fixed page. Record the intended interaction and compare separated saved frames to confirm
that the page's rows or states actually change. Crop and presentation can then be revised around
this recording without repeating the capture.

For local inputs beside the script, `new URL('../assets/card.html', import.meta.url).href` locates
the file. Relative output paths follow the directory where the command runs. `args` contains the
arguments after `--`; use `log` for progress. `--json` reports every completed helper output with its
path and actual dimensions, plus recorded duration and frame rate. Output paths must be new.

## Browser and recording choices

Use an installed compatible browser or prepare the package's tested browser once with
`hypit capture install-browser`. Installation uses Puppeteer's browser cache and leaves existing
browsers in place. [Network preparation](../environment/local-tools.md#make-network-preparation-practical)
explains diagnosing a slow download. The package manifest owns the recommended version. For an explicit alternate selection, use
`--browser-version <exact-version>` and `--browser-cache <directory>` on both preparation and capture.
`install-browser --browser-download-base-url <url>` selects a compatible archive source for that
installation only, with no source fallback. Capture never installs the missing browser.
`--channel chrome` selects an installed Chrome;
`--browser <executable>` selects another explicit compatible path. `--headed` opens a visible
window. The script's `options.launch` accepts ordinary Puppeteer launch options, including a chosen
`userDataDir` when a dedicated persistent browser profile is useful. CLI browser options override
the script's choices. `--timeout-ms` sets page operation and navigation timeouts.

Native page recordings require Chrome 153 or later, supplied by `install-browser`. They produce MP4;
use an `.mp4` destination. `record({ path, audio: true })` includes page audio when the demonstration
needs it; the default captures picture only. The browser performs encoding. `ffprobe` on `PATH`
reads the saved file's actual dimensions and duration; `options.ffprobePath` can select another
executable. `record` accepts Puppeteer's `RecordOptions`, including `fps` / `frameRate` as a maximum
capture rate and `maxWidth` / `maxHeight` for output dimensions. Music, narration and effects added
in the edit remain ordinary authored audio layers. The helper sets maximum dimensions from the
viewport's device-pixel dimensions; Chrome determines the recorded size. Device scale can enlarge
a screenshot without enlarging the recording. Use the saved video's reported dimensions when
placing it in the composition.

## Place the captured material

Keep captures in project assets and record the source page and its purpose in the project notes.
An image enters through `media:Image`; a recording enters through `media:Video` and the ordinary
[normalization path](media.md). Place them with
[Visual Clips](visual-clips.md#keep-destination-time-and-source-sampling-distinct) and the Script's
Selections or Moments as appropriate. Their visibility, crop, scroll and transitions belong to the
composition, so those changes can reuse the captured file.
