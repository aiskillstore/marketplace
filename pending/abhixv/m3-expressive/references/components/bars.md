# App bars & Toolbars (M3 / M3 Expressive)

Sources: `components_app-bars.md` (slug `app-bars`, updated 2026-07-17), `components_toolbars.md` (slug `toolbars`, updated 2026-07-17). All values below appear verbatim in those pages. Token tables and measurement diagrams did not convert — see "Gaps".

---

## App bars

### 1. What it is + when to use vs. siblings

- Displays labels and page navigation controls at the **top of the page**. **Use a toolbar to display page actions.**
- Focus on describing the current page and provide **1–2 essential actions**.
- Provides content and actions related to the current page: page navigation actions, headlines, images, and 1–2 essential actions. Information/actions should be contextual and specific to a page, but can also include global product controls such as search or notifications.
- Renamed in M3 Expressive from **top app bar** to **app bar**.
- Four variants and their discriminating rule:

| Variant | Use when |
|---|---|
| **Search app bar** | Use on home pages when **search is key to the product**; provides an emphasized entry-point to open the search view |
| **Small** | Use in **dense layouts** or **when a page is scrolled** |
| **Medium flexible** | Use to display a **larger headline**; can collapse into a small app bar on scroll |
| **Large flexible** | Use to **emphasize the headline** of the page |

- Baseline (no longer recommended): **Medium** → replace with medium flexible. **Large** → replace with large flexible. Flexible versions are similar visually but have multi-line support, a shorter height, and can contain a wide variety of elements like images.
- **Center-aligned** app bar was merged into **small**; use the centered-text configuration.
- If the product has many actions, place those in a **toolbar**. Avoid placing an overflow menu in the app bar when possible.

### 2. Anatomy

Standard app bar parts (5): **Container, Leading button, Trailing elements, Headline, Subtitle**.
Guidelines-page ordering of the same five: Container, Headline, Trailing icons, Subtitle, Leading button.

| Part | What it is / looks like |
|---|---|
| **Container** | Holds all information and actions at the top of a screen, including navigation icons, headlines, and buttons. Straight (square) corners. Spans full window width. Avoid changing its position or shape. |
| **Leading button** | Used for navigating the product. Typically a **menu icon** (opens a modal expanded navigation rail) or a **back arrow** (returns to previous screen). Can instead be a product logo (search app bar). |
| **Headline** | Describes the current page, the current section, or the product. **Headline text should be brief enough to easily fit in the app bar.** Wraps to a second line only in medium flexible / large flexible. Can be aligned to the leading edge or centered. |
| **Subtitle** | Adds additional context to a page; leading- or center-aligned with the headline. |
| **Trailing icon buttons** | Up to two icon buttons placed after the headline, aligned to the trailing edge. Can be replaced by a single filled icon button. |

Search app bar anatomy (5): **Container, Leading icon button, Hinted search text, Trailing icon or avatar, Search container**.

Baseline **medium** and **large** app bars have the same elements as each other — anatomy (4): **Container, Leading button, Trailing icons, Headline** (no subtitle).

Search app bar icon layouts (3 documented arrangements):
- A leading element and a trailing element **outside** search.
- A leading element, a trailing element **inside** search, and a trailing element **outside** search.
- A leading element and **two** trailing elements **outside** search.

Trailing actions can be placed **inside or outside the search bar**. When the search bar is selected, it should open the **search view** component.

Customization options: an image or logo; a subtitle; a filled icon button. **Avoid customizing the size of the heading and subtitle, or adding too many actions.**

Optional element rules:
- **Image / logo:** can be placed in the app bar to **bolster brand identity or visual appeal**; in **small** app bars an image can **replace the label text**. In other app bars the logo appears **above** the text. Image must be high quality and pertinent, and shouldn't disrupt the app bar's functionality.
- **Filled trailing icon button:** trailing icon buttons can be replaced with a single **primary or tonal filled icon button**, in **default or wide** sizes.
- **Subtitle:** medium flexible and large flexible app bars **hug the text contents**, so they are taller when a subtitle is visible.

### 3. Sizes / variants / configurations

Availability matrix:

| Variant | M3 | M3 Expressive |
|---|---|---|
| Search app bar | -- | Available |
| Small | Available | Available |
| Center-aligned | Available | Merged into **small**; use centered-text configuration |
| Medium (baseline) | Available | Not recommended. Use **medium flexible** |
| Medium flexible | -- | Available |
| Large (baseline) | Available | Not recommended. Use **large flexible** |
| Large flexible | -- | Available |

Text alignment configuration:

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Text alignment | Leading edge (default) | Available | Available |
| Text alignment | Centered | -- | Available |

- Text labels, including supporting text, can be aligned to the leading edge or centered.
- Search container width rule: fills **100%** of the space between leading and trailing app bar elements until it reaches **312dp**; beyond that it grows only to fill **50%** of that space.
- App bar token sets are organized into a **common token set** plus **size-specific tokens**. Baseline app bar token sets are organized into **medium**, **large**, and **older baseline** token sets. The **default search component tokens** are used in the search app bar.

### 4. Placement

- Top of the page/screen. Container width responds to the view or device width and **should always span 100% of the window width**.
- **Always use the default height**; don't make an app bar shorter than its default height (default heights were chosen to ensure readability of on-screen elements).
- Trailing-edge actions may **collapse into an overflow menu at smaller window sizes** and become visible again at larger sizes.
- **Search app bar trailing icons:** up to **two** trailing icons on mobile in addition to a trailing avatar; up to **four** trailing icons on larger screens (the search app bar dynamically adapts to available width).
- Place **most-used actions closest to the leading edge** (most used on the left, least used on the right).
- RTL: layout is mirrored automatically by aligning elements to the leading and trailing edges of the container.
- Scroll/pin: the app bar can remain on a page at all times, or hide and reappear when scrolling. **Medium flexible** and **large flexible** can transform (compress) into **small** app bars when scrolled and should remain small until the page is scrolled back to the top.

XR (app bar orbiter):
- One app bar orbiter; closely aligns with the **small** app bar; configurable **center-aligned or left-aligned**. Anatomy (4): Container, Headline, Trailing icons, Leading icon.
- Only available in **full space**. In **home space**, use a regular app bar on the same plane as body content to mimic a 2D experience.
- **Global context:** centered at the top of the app it controls; stays anchored to the app during layout/content changes. This ensures navigation elements are always easy to find and use.
- **Local context:** centered at the top of the spatial panel it controls; repositions in response to layout/content changes. **This is less common for app bars — make sure a local app bar orbiter contains only actions that affect its anchored panel.**
- Apps should have **only one** app bar orbiter, placed in global context, in most cases.
- Include a **20dp margin** to separate the orbiter from the spatial panel and prevent content obstruction. Don't overlap orbiter and spatial panel.
- Always align within the bounds of nearby spatial panels; don't exceed the width of adjacent spatial panels.
- Default alignment is **center** to the spatial panel; can also be left or right (for ergonomics or RTL).
- Width should adjust to stay in a person's field of view; not recommended to exceed a person's natural field of view. In local context it can expand to the width of its adjacent spatial panel — verify it stays in field of view and test for usability.
- Spatial elevation: the app bar displays **above** the spatial panel on the Z-axis.

### 5. States and interaction behavior

- **Touch:** tapping an icon button shows a **touch ripple** as interaction feedback.
- **Cursor:** hover state provides a visual cue that the element is interactive; click (in both active and inactive states) shows a ripple.
- **Keyboard/switch:** navigating to an interactive element shows a **focus indicator / focus ring**; selecting performs the action.
- **Initial focus** lands on the **leading button** (first interactive element).
- Scroll behavior / motion:
  - App bars should initially be the **same color as the background**, then **fill with a contrasting color on scroll** for visual separation. No drop shadow.
  - Can animate on and off screen with another bar of controls, like a row of chips.
  - Can hide when scrolling up and reveal when scrolling down.
  - Alternative: set the container **transparent on scroll** so buttons float above content — then ensure icon buttons have a **container fill**, and consider **narrow-width icon buttons** for actions like **Back** to reduce space.
  - Medium/large flexible use the **compress effect** to transform into small app bars.
  - Selecting the search bar opens the **search view** component.

### 6. Color role mapping

All app bars share the same color roles. **On scroll, the container changes color to `surface container`.**

| Variant | Roles listed |
|---|---|
| App bar (leading edge) | **Surface**, **On surface**, **On surface variant**, **On surface**, **On surface variant**, **Surface container (on scroll)** |
| Search app bar | **Surface**, **On surface variant**, **On surface variant**, **On surface variant**, **Surface container**, **Surface container**, **Surface container highest** |
| Medium top app bar (baseline) | **Surface**, **On surface**, **On surface**, **On surface variant** |

Search app bar specifics:
- Search container: **surface container** (default; distinguishes it from the app background).
- Search label: **on surface variant**.
- If the background is darker, use a lighter container color such as **surface bright** to maintain strong visual contrast.
- The app bar changes color when flat vs. on scroll; the search bar can also change color on scroll.

XR app bar orbiter elevation colors (any of): **Surface container**, **Surface container high**, **Surface container highest**.

### 7. Typography role mapping

Headline type style by variant:

| Variant | Headline style |
|---|---|
| Search | **Body large** |
| Small | **Title large** |
| Medium flexible | **Headline medium** |
| Large flexible | **Display small** |

Subtitle type style by variant:

| Variant | Subtitle style |
|---|---|
| Small | **Label medium** |
| Medium flexible | **Label large** |
| Large flexible | **Title medium** |

(No subtitle style listed for the search app bar.) Typography differences from M2: **larger default text**; layout: **smaller default height**.

### 8. M3 Expressive update (complete)

**May 2025**

- The new **search app bar** supports icons **inside and outside** the search bar, and **centered text**. It opens the **search view** component when selected.
- The new **medium flexible** and **large flexible** app bars come with significant improvements, and **should replace medium and large app bars, which are no longer recommended**. The **small** app bar is updated with the same flexible improvements.

Variants and naming:
- Renamed component from **top app bar** to **app bar**
- Added **search app bar**
- **Medium** and **large** app bars are no longer recommended
- Added **medium flexible** and **large flexible** app bars with:
  - Reduced overall height
  - Larger title text
  - Subtitle
  - Left- and center-aligned text options
  - Text wrapping
  - More flexible elements for imagery and filled buttons
- Added features to **small** app bar:
  - Subtitle
  - Center-aligned text option
  - More flexible elements for imagery and filled buttons

Differences from M2:
- **Color:** new color mappings and compatibility with dynamic color
- **On scroll:** no drop shadow; instead a color fill creates separation from content (M2 used elevation and a drop shadow)
- **Typography:** larger default text
- **Layout:** smaller default height

### 9. Do / Don't

Do:
- Limit to **one action, two if necessary**.
- Make the primary action one that **alters or exits the entire page** — e.g. **Send**, **Save**, **Edit**.
- To boost visibility of a primary action, change the icon button style to **filled or tonal**, and consider a **wide icon button**.
- Use **straight corners** for app bars.
- Always use the **default height** and span the **full width of the window**.
- Use **filled icons** when possible for best visibility; outlined icons can be used as needed, particularly for **unselected toggle buttons**.
- Search bars must always include the word **Search**; capitalization varies by product: **Search**; searching a specific area, e.g. **Search inbox**; **Search [Product]**, e.g. **Search Photos**.
- In the search app bar, the leading element can be a **product logo** — cosmetic, or triggering an action like returning to/refreshing the home screen.
- If headline text is long, use a **medium flexible or large flexible** app bar and wrap to **two lines maximum**.
- Use default search color roles when possible.

Don't:
- Don't put **multiple filled or tonal buttons** in the app bar. If changing icon button color style to filled or tonal, only use **one** icon button.
- Don't use **curved shapes** on the container — implies the container can expand upon interaction.
- Don't make an app bar **shorter than its default height**.
- Don't **truncate** headline text. Don't **wrap text in a small app bar**.
- Don't use **more than two trailing icon buttons with an avatar** in a search app bar (don't use three icons and an avatar); place extra actions in a toolbar.
- Avoid using trailing buttons to **open a menu with more actions** — use a toolbar instead.
- Avoid using a **logo to open an expanded navigation rail**.
- Don't transform app bars into a **search app bar** on scroll.
- Avoid customizing the size of the heading and subtitle, or adding too many actions.
- Avoid using **custom color roles** for the search bar container and search label text; if necessary, ensure at least **3:1** contrast.

### 10. Accessibility

- Use cases — with assistive technology people should be able to: understand what page they're currently visiting; take actions or navigate to a new page destination; **maintain access to app bar actions when the content is scrolled**.
- Contrast: search text/label and container must have **at least 3:1 contrast** (applies to default and to any alternate/custom color roles).
- Initial focus lands on the **leading button**.
- Keyboard navigation:

| Keys | Action |
|---|---|
| **Tab** | Move focus to the next interactive element |
| **Space or Enter** | Activate the focused element |

- Interactive elements should have **focus rings**.
- Labeling: the accessibility label for a title should be the **same as the content within the title**; add additional context if needed so users understand what page they're on or what content is shown. Screen readers read the UI text followed by the component's **role** (headline role = **"Title"**, icon button role = **"Button"**). Label icon buttons per icon-button accessibility guidelines (e.g. **View on map**).
- XR: XR app bars should follow applicable Material app bar accessibility standards (XR accessibility guidance still evolving).

---

## Toolbars

### 1. What it is + when to use vs. siblings

- Use a toolbar to provide **actions related to the current page** (app bars are for labels/page navigation at the top). Toolbars can contain **many actions** and can scale to show more actions in larger windows.
- Two expressive variants:

| Variant | Discriminating rule |
|---|---|
| **Docked toolbar** | Spans the **full width of the window**. Best used for **global actions that remain the same across multiple pages**. |
| **Floating toolbar** | **Floats above the body content**. Best used for **contextual actions relevant to the body content or the specific page**. |

- The baseline **bottom app bar** is no longer recommended but is still supported; replace with the **docked toolbar**, which functions similarly but is **shorter** and has **more flexibility**.
- Can display a wide variety of control types (buttons, icon buttons, text fields) and can be paired with FABs to emphasize certain actions.
- **Don't show at the same time as a navigation bar.** Show the navigation bar on **primary pages**, toolbars on **subsequent pages with actions**.
- Floating toolbars can be used as **tabs between related subsequent pages** in the product hierarchy (local navigation), grouping similar pages and showing that selection affects the body content underneath. Consider existing app hierarchy; avoid redundant or confusing navigation combinations in the same view.
- When actions don't fit in a toolbar, **add a menu**.

### 2. Anatomy

Parts (2): **Container** and **Placed components** / **Elements**. Bottom app bar (baseline) anatomy: **Container** only.

| Part | What it is |
|---|---|
| **Container** | Docked: spans full width of window, straight corners. Floating: fully-rounded shape, has elevation by default, must be fully visible on screen. |
| **Slots / elements** | Think of the toolbar as a container with several **slots**; each slot can be a different element. Most common elements: **icon buttons, buttons, text fields**. Slots can also hold **images** or **any kind of custom component**. |

- Icon buttons provide an **even hierarchy** of controls; mixing in a **filled icon button** adds emphasis to a single action.
- **Elevation:** floating toolbars have elevation by default; elevation **can be removed** if the content beneath the toolbar is visually distinct.

### 3. Sizes / variants / configurations

Availability matrix:

| Variant | M3 | M3 Expressive |
|---|---|---|
| Docked toolbar | -- | Available |
| Floating toolbar | -- | Available |
| Bottom app bar | Available | Not recommended. Use **docked toolbar**. |

Configurations:

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Color | **Standard** (default) | Available as bottom app bar | Available |
| Color | **Vibrant** | -- | Available |
| Floating toolbar layout | **Horizontal** (default) | -- | Available |
| Floating toolbar layout | **Vertical** | -- | Available |
| Other elements | **With FAB** | Available as bottom app bar | Available* |

\*Implementation differs per platform. On Jetpack Compose, floating toolbar with FAB is fully supported (`HorizontalFloatingToolbar`); on other platforms each component must be added separately. Also on Jetpack Compose the **floating toolbar is a separate component** from the docked toolbar and bottom app bar.

Color configuration meaning:
- **Standard** — low-emphasis color scheme, best for focusing attention on the body content.
- **Vibrant** — high-emphasis color scheme that draws attention to the controls; can also indicate a **temporary change in page behavior**, such as entering **edit mode**.
- Consider alternative color roles for greater or lesser emphasis; experiment for different effects.

Measurements (stated values):
- **By default all toolbars are 64dp high, center-aligned, have equal padding between items, and have a minimum outside padding of 16dp.**
- Docked toolbar: minimum **16dp** padding on leading and trailing edge; **32dp** padding between items is the default; a center-aligned configuration with **8dp** padding between items is shown as an alternative. Alignment and padding can be configured (left/right alignment; center-aligned).
- Floating toolbar: **16dp** margin (container should only be as big as needed to hold its items before reaching the 16dp margin). Horizontal: minimum **16dp** margin from the window edge. Vertical: minimum **24dp** margin.
- Bottom app bar tokens are in **one token set**. Bottom app bar common layouts: **icon buttons and FAB**; **icon buttons and no FAB**.

### 4. Placement

- **Only place docked toolbars at the bottom of the window.** If using other bottom-aligned elements, such as a navigation bar, **don't use a docked toolbar**.
- Toolbar and navigation bar are both bottom-placed → must **not** be shown at the same time.
- Floating toolbars can be **horizontal or vertical**; in larger window sizes vertical toolbars can be placed on **either side** of the screen.
- Vertical toolbars should be positioned **opposite the navigation rail** to balance the screen and keep actions easy to access. When showing a navigation rail and a vertical floating toolbar at once, use the **centered configuration** of the navigation rail.
- Floating toolbars must not exceed the edge of the window or pane.

Per-window-size behavior:

| Window size | Docked | Floating |
|---|---|---|
| **Compact** | Always span 100% of screen width; elements **evenly spaced** | Vertical toolbars **not recommended** (take significant screen area, may feel overwhelming, especially with complex layouts) — only use when the screen is simple or the toolbar has few controls. **Don't use multiple toolbars**; use one toolbar for all actions. |
| **Medium and larger** | Adjust padding between controls for a comfortable layout, by **centering all elements**, or **centering a key action and aligning other elements to the edges** (edge alignment makes controls easier to reach on tablets and better highlights a primary action in the middle) | Container can display **more controls** before hitting the 16dp margin; more actions can be revealed as the window expands; toolbars can be aligned to **opposite edges** of the screen to group similar actions (e.g. undo/redo in one, highlight/erase/select in another) with stylistic differences to clarify hierarchy |
| **Web / large screens** | Docked toolbar **can be rounded** and placed in different parts of the page; **dividers** can organize large amounts of items; only shrink the height and use **extra small buttons** if vertical space is limited | — |

- Floating width can be **capped** to keep it smaller and hide more elements. If there's not enough space for all items, put them in an **overflow menu in the trailing slot**.
- Trailing-edge actions can collapse into an **overflow menu** at smaller window sizes and reappear at larger sizes.
- **RTL:** mirror individual items that need it (icons, text direction). If the order of actions is important, **flip the order** so e.g. **Next** remains on the trailing edge.

XR (toolbar orbiter):
- One toolbar orbiter; closely aligns with the **floating toolbar**; configurable **horizontal or vertical**. Anatomy: **Container**, **Placed components**.
- Only available in **full space**; in **home space** use a regular toolbar on the same plane as body content to mimic a 2D experience.
- In full space, a toolbar orbiter can be positioned **adjacent to or overlapping** a spatial panel.
- **Local context (recommended):** centered at the **bottom of the spatial panel** it controls; repositions in response to layout/content changes.
- **Global context:** centered at the **bottom of the app**; stays anchored during layout/content changes. Less common, since toolbars usually contain actions controlling a specific panel.
- **Expand & collapse:** orbiters with **more than five items** can expand and collapse to reveal/hide additional content; when expanded it stays within the bounds of the adjacent spatial panel. Alternatively split complex toolbars into multiple toolbars.
- Full space apps can have **more than one** toolbar orbiter (global or local); limit to rare cases where additional spatialization improves usability.
- Position from the spatial panel: **offset by 20dp** or **inset by 12dp**. Don't overlap above a **12dp** inset threshold (prevents content obstruction). Toolbar orbiter **padding: 12dp**.
- Align within the **horizontal** and **vertical** bounds of nearby spatial panels; don't exceed the panel's width or height.
- Default alignment is **center** to the spatial panel; depending on horizontal/vertical configuration it can align center, left, right, top, or bottom (for ergonomics or RTL).
- **Don't place a vertical toolbar orbiter between spatial panels** — hurts interface structure and makes it hard to find.
- Spatial elevation: the toolbar displays **above** the spatial panel on the Z-axis.

### 5. States and interaction behavior

- **The toolbar has no interactions by default. All interactions are with the elements placed inside.**
- **Touch:** tapping an icon button in the toolbar shows a **touch ripple**.
- **Cursor:** hover provides a visual cue that the element is interactive; click (in both active and inactive states) shows a ripple.
- **Focus:** lands on the **first interactive element**; use **Tab** to navigate through all other actions.
- Scrolling / motion:
  - **Docked** toolbars can either remain on the screen during scroll, or **animate offscreen**.
  - **Floating** toolbars can remain on screen, **animate offscreen**, or **collapse into a single, high-emphasis action** on scroll. On Jetpack Compose the floating toolbar can collapse to a **FAB or key action** on scroll.
  - **Don't collapse actions and scroll at the same time** — a toolbar shouldn't both collapse and transition off page.

### 6. Color role mapping

**Standard** color scheme (container + icon button types):
- Container: **Surface container**
- Filled button: **Primary** container / **On primary** content
- Toggle tonal button: **Secondary container** / **On secondary container**
- Standard button: **Primary**

**Vibrant** color scheme:
- Container: **Primary container**
- Filled button: **Primary** / **On primary**
- Toggle tonal button: **Surface container** / **On surface**
- Standard button: **On primary container**

**Bottom app bar (baseline):** container = **Surface container**.

**XR toolbar orbiter** elevation colors (any of): **Surface container**, **Surface container high**, **Surface container highest**, **Tertiary container**.

### 7. Typography role mapping

No type styles are stated anywhere on the toolbars page — toolbars hold placed components (buttons, icon buttons, text fields), and each follows its own component typography. See "Gaps".

### 8. M3 Expressive update (complete)

The **bottom app bar** is no longer recommended and should be replaced with the **docked toolbar**, which functions similarly but is **shorter** and has **more flexibility**. The **floating toolbar** was created for **more versatility, greater amounts of actions, and more variety in where it's placed**.

Variants and naming:
- Added **docked toolbar** to replace **bottom app bar**
  - Size: **Shorter height**
  - Color: **Standard or vibrant**
  - Flexibility: **More layout and element options**
- Added **floating toolbar** with the following configurations:
  - Layout: **Horizontal or vertical**
  - Color: **Standard or vibrant**
  - Flexibility: **Can hold many elements and components. Can be paired with FAB.**
- **Bottom app bar** is still available, but not recommended

Differences from M2:
- **Color:** new color mappings and compatibility with dynamic color
- **Elevation:** no shadow (M2 bottom app bar had elevation of **8dp**)
- **Layout:** container height is **taller** and the **FAB is now contained within the app bar container** (M2 didn't contain the FAB)

### 9. Do / Don't

Do:
- Use the **vibrant** color style for greater emphasis; **standard** to draw focus to content outside the toolbar.
- Keep a minimum of **16dp** padding on the leading and trailing edge of a docked toolbar; otherwise arrange controls inside however you see fit (32dp between items is just the default).
- Use **straight corners** for docked toolbars.
- Emphasize a **single** action to create hierarchy, via: different icon button color styles (filled, tonal, standard); customized color roles for a single action (primary or secondary palette); **wide and narrow** icon buttons; pairing the toolbar with a **FAB**.
- Use a **FAB** for the highest-priority action in the view, or to complement the controls; place it **next to** a floating toolbar.
- Use an **overflow menu** if the floating toolbar needs more actions than fit; keep the floating container **fully visible on screen**.
- Keep vertical toolbars compact: use **narrow or default** icon buttons.
- Use a toolbar for **local navigation** on a specific page; keep navigation distinct.

Don't:
- **Don't show a toolbar and a navigation bar at the same time** (including a toolbar with navigation controls above a bottom navigation bar).
- **Avoid rounded corners** on the docked toolbar container — implies the container expands or changes upon interaction. (Exception: on web and large screens the docked toolbar **can** be rounded.)
- Don't overwhelm people with **too many controls**.
- Don't **emphasize multiple buttons** with bold, primary colors, such as a button and FAB together — emphasize one action at a time.
- Avoid **mixing too many different controls** in the same toolbar; consistent control design keeps things clear.
- **Avoid square icon buttons in floating toolbars** — their square shape conflicts with the fully-rounded floating container. Square buttons **can** be used in the docked toolbar.
- Don't use **wide icon buttons** in vertical toolbars.
- Floating toolbars **shouldn't exceed the edge of the window or pane**.
- Don't add extra space to a toolbar beyond its necessary items.
- Don't use **multiple toolbars in compact windows**.
- Don't **collapse and scroll offscreen at the same time**.

### 10. Accessibility

- **All elements need a minimum 48x48dp target area to be accessible.**
- Use cases — with assistive technology people should be able to: navigate and activate any actions in the toolbar; select a destination from a menu; activate a back button; **maintain access to toolbar controls when the content is scrolled or collapsed**.
- Keyboard navigation:

| Keys | Action |
|---|---|
| **Tab or Arrows** | Navigate between interactive elements |
| **Space or Enter** | Activate the focused element |

- Initial focus lands on the **first interactive element**.
- Labeling: **on web, the toolbar container should have the `toolbar` role**; on mobile it can be a generic container. All actions inside the toolbar should follow their respective accessibility guidelines.
- XR: XR toolbars should follow applicable Material toolbar accessibility standards.

---

## Gaps (specs referenced but with no values in the text)

> **Before treating a measurement here as unavailable:** many of these are published as
> `md.comp.*` values in the generated Compose token files, which are collected in
> [`component-tokens.md`](../component-tokens.md) — container heights and widths, shape
> assignments, elevation levels, icon sizes, and internal spacing. Check there first. Those are the
> Compose token values, so attribute them as such rather than as guideline text.


App bars:
- All design-token names and values — "Tokens & specs" sections exist (common token set + size-specific tokens; baseline medium/large/older baseline sets; default search component tokens) but no table converted, and the page never states a token naming scheme.
- All measurement diagrams: search app bar, small, medium flexible, large flexible, baseline medium, baseline large — padding and size values (heights, corner radius, insets, icon sizes) are image-only. The only numeric layout value present is the 312dp search-container threshold.
- Default heights of each variant ("always use the default height") are never numerically stated.
- Corner radius / shape tokens (only qualitative: "straight corners").
- Which specific color role maps to which specific part — the page lists role names in an ordered footer list matched to a diagram, so the part↔role pairing beyond search container / search label is not resolvable from text.
- Search app bar subtitle typography (not listed).
- Search app bar state-layer specs; per-state (hover/focus/pressed/dragged/selected/disabled) opacity or color values.
- XR app bar orbiter measurements and padding (image-only; only the 20dp margin is stated).
- Per-breakpoint/window-size-class numbers for when trailing actions collapse into overflow.

Toolbars:
- All design-token names and values — docked, floating, and bottom app bar token sets referenced but no table converted, and the page never states a token naming scheme.
- Docked toolbar measurement diagram values beyond 64dp height, 16dp min outside padding, 32dp default between items, 8dp center-aligned alternative.
- Floating toolbar size/padding/margin diagram values beyond the 16dp and 24dp margins; internal padding, container height (beyond the "all toolbars 64dp" default), and corner radius token are image-only.
- Bottom app bar (baseline) measurement values, including its M3 container height ("taller" is qualitative).
- Floating toolbar elevation dp value (only "has elevation by default"; M2 bottom app bar 8dp is given for contrast).
- Width cap value for floating toolbars.
- Reduced/"shorter" docked toolbar height vs. bottom app bar — no numbers.
- Per-state (hover/focus/pressed/selected/disabled) specs — page states the toolbar itself has no interactions and defers to the placed components.
- Typography role mapping — no type styles stated anywhere on the toolbars page.
- "Extra small buttons" size value for vertical-space-limited large screens.
- XR toolbar orbiter measurement diagram values beyond 20dp offset / 12dp inset / 12dp padding.
