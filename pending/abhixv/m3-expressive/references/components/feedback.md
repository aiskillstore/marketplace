# M3 Feedback & Transient Surfaces — Badges, Progress indicators, Loading indicator, Snackbar, Tooltips, Menus, Date pickers, Time pickers

Source: m3.material.io page exports (badges, progress-indicators, loading-indicator, snackbar, tooltips, menus, date-pickers, time-pickers). Color roles below are the human-readable role names exactly as the source lists them; the `md.sys.*` / `md.comp.*` token tables did not convert (see gaps).

---

## Cross-component wait-time rule (progress-indicators + loading-indicator, stated identically on both pages)

| Expected wait time | Recommendation |
|---|---|
| Instant (under 200ms) | No indicator |
| Short (between 200ms and 5s) | Loading indicator |
| Long (Over 5s) | Progress indicator |

- Choose a loading or progress indicator that corresponds to the expected wait time and kind of process.
- If the wait is very long, consider allowing people to navigate away from the page while the process finishes up.
- Transition indeterminate → determinate **progress indicator** as info becomes available. **Don't** transition a loading indicator into a progress indicator.

---

## Badges

### 1. What it is / when to use vs. siblings
- Indicate a notification, item count, or other information relating to a **navigation destination**. Placed on the ending edge of icons, typically within other components.
- Two variants: **small badge** and **large badge**.
  - **Small badge** = simple circle, no characters; use to indicate an **unread notification**, and when spaces are tightly constrained (e.g. app bars) because small badges won't run into the edge of the screen.
  - **Large badge** = contains label text communicating **item count** information; use when visual collisions aren't an issue (e.g. navigation rail).
- Discriminator: count information → large; boolean "something new" or tight space → small.

### 2. Anatomy
Small badge · Large badge container · Large badge label. (Nav bar / nav rail spec diagrams enumerate 5 aspects: Small badge, Large badge container, Large badge label, Large badge maximum character count container, Large badge maximum character count label.)
- Containers are anchored **inside the icon bounding box**, at the **upper trailing edge** of the icon.
- As count increases, large badge **width expands** but height and placement stay the same.

### 3. Sizes / variants / measurements
| Attribute | Value |
|---|---|
| Small badge shape | 3dp corner radius |
| Small badge size (HxW) | 6dp |
| Large badge shape | 8dp corner radius |
| Large badge one digit size (HxW) | 16dp |
| Large badge max character count size (HxW) | 16x34dp |
| Small badge: distance from top trailing icon corner to bottom leading badge corner (HxW) | 6x6dp |
| Large badge: distance from top trailing icon corner to bottom leading badge corner (HxW) | 14x12dp |
| Large badge padding between badge and text container | 4dp |

- Max label content = **four characters, including a `+`** (the `+` indicates "more"). Label large badges with **counts or a status**. Use the recommended maximum character count so labels don't extend beyond the badge container.

### 4. Placement
- Most commonly used within other components: **navigation bar, navigation rail, app bars, tabs**.
- Badges have **fixed positions**. Don't change position arbitrarily; don't place the badge over the icon.
- Mirror position for **right-to-left** languages (badge moves to the left side of the item).
- When an icon with a badge is followed by text or another element (e.g. a tab), place a **large badge at the trailing edge**; if a large badge might overlap a trailing element, move it to the trailing edge or use a small badge instead.

### 5. States / configurations
15 documented configurations on navigation destinations — for each of {small badge, large badge, large badge max character count} across: Inactive with label; Inactive; Active with label; Active nav bar no label; Active nav rail no label.
- In navigation bars, **hide the badge once the destination has been selected** (unread-notification badges get hidden once selected; animation of the badge disappearing on tap).

### 6. Color
- Badge container → **Error**; badge label text → **On error** (inferred from positions 2–3 of the nav-bar list; the source lists roles as an ordered set without explicit per-element pairing).
- Raw ordered role list for nav bar (5 aspects): Error, Error, On error, On error, Error. Nav rail: Error, On error, Error, On error, Error.
- Badges use a color intended to stand out against labels, icons, and navigation elements. **Keep the default color mapping** to avoid color conflict issues.

### 8. Differences from M2
- Color: New color mappings and compatibility with dynamic color.
- (No M3 Expressive update section exists on the badges page.)

### 9. Do / Don't
- Do anchor badges inside the icon bounding box at the upper trailing edge.
- Do limit content to four characters including a `+`; truncate labels as needed (e.g. 4-digit → 3-digit + `+`).
- Do use the default badge color.
- Don't let the badge get cut off or collide with another element.
- Don't change badge position arbitrarily or place the badge over the icon.
- Don't use custom color roles for container/label; if custom roles are necessary, ensure at least **3:1** contrast.

### 10. Accessibility
- Assistive tech users must be able to understand the dynamic information conveyed (counts/labels) and address badge announcements by selecting the corresponding navigation destination.
- Badges must use default color with at least **3:1** contrast.
- The accessibility label for a badge item is **read after its navigation destination**. Numerical badges have their number read; non-counting badges announce **"New notification"**.

---

## Progress indicators

### 1. What it is / when to use vs. siblings
- Show the status of ongoing processes: loading an app, submitting a form, saving updates. They capture attention through motion.
- Use for **Long (over 5s)** waits; for 200ms–5s use a **loading indicator**; under 200ms use none.
- Two variants: **Linear** (best placed on the edge of a container) and **Circular** (best centered in an element).
- A process must be represented by the **same variant throughout the product** (if refreshing uses circular in one place, use circular everywhere). Use the same configuration for all instances of a process.
- Behavior: **Determinate** (known progress and wait time; default) vs **Indeterminate** (unknown progress and wait time). Change indeterminate → determinate as more information becomes available.

### 2. Anatomy
**Active indicator · Track · Stop indicator**
- **Active indicator**: shows progress so far; in indeterminate processes it grows and shrinks along the track repeatedly. Linear animates leading → trailing edge; circular animates from the top of the track, **clockwise by default**. Appears as soon as progress begins; at low percentages where space is limited it appears as a **dot**.
- **Track**: the contrasting line/ring behind the active indicator.
- **Stop indicator**: a **4dp circle** marking the end of a **linear determinate** indicator, to meet Material's accessibility standards. Not used for indeterminate or circular indicators. Required if the track has contrast **below 3:1** with its container or the surface behind the container.

### 3. Variants & configurations
| Variant | M3 | M3 Expressive |
|---|---|---|
| Linear progress indicator | Available | Available |
| Circular progress indicator | Available | Available |

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Behavior | Determinate (default), Indeterminate | Available | Available |
| Track thickness | Fixed (4dp) | Available | Available |
| Track thickness | Configurable | -- | Available |
| Shape | Flat (default) | Available | Available |
| Shape | Wavy | -- | Available |

Sizes/measurements stated in text:
- Default track thickness **4dp**; thicker variants shown as sample measurements for makers to adjust the default.
- Linear indicator is **inset from the edge of the screen by 4dp**; padding on each end should be **4dp minimum** but can be modified.
- Circular sizes range **24dp to 240dp**. Avoid exceeding the minimum and maximum sizes.
- Linear indicators shouldn't be used in elements **smaller than 40dp**.
- Wave geometry vocabulary: **Amplitude** = from the center of the resting position to the center of the peak; **Wavelength** = distance between two adjacent peaks; **height** = overall container height. Wavy shape **increases the overall height of the component**.
- **Baseline tokens:** the circular and linear progress indicators *had* separate token sets — **these are no longer recommended**.

### 4. Placement
- Linear: along the **edge of the container that's loading**; if the container changes shape, place it on the edge that animates. Can also be placed in the middle of a container.
- One indicator at the **top of a page** = whole page/group is loading; attached to a card = only the card's content is loading; on the expanding edge of a card = that edge may expand to show loaded content.
- Use a **single** indicator for a group; don't add one for every element unless they're activated independently.
- Circular: **centered directly on** the container or page that's loading (button, card). When loading more items, place it in the **empty space where new content will appear**, not overlapping existing content (a loading indicator also works well there).

### In buttons
- A circular indicator in a button shows the button's action is in progress; use for **short, indeterminate activities under 5 seconds**.
- In very small buttons use the **flat** shape (wavy isn't visible at that size).
- To ensure minimum **3:1** contrast: set the active indicator color to the **same color as the button's icon or label text**, and **remove the track**.
- Avoid applying progress indicators to every button in a list.

### 5. Motion / shape behavior
- Determinate fills 0%→100%; indeterminate moves along a fixed track, growing and shrinking in size.
- Active indicator shape options **flat** and **wavy** — **use the shape that best fits the product's tone**; wavy makes longer processes feel less static, best when a more expressive style is appropriate; at very small sizes wavy may not be visible.
- The **waveform should scale with the size** so proportions look the same across sizes.

### 6. Color
- Active indicator → **Primary**; Stop indicator → **Primary**; Track → **Secondary container**.

### 8. M3 Expressive update (verbatim content)
**Aug 2024** — "The progress indicators have configurations for height and wavy shape. Choose the visual style that best fits your product."
- Track height: Configurable
- Shape: Wavy
- Framing: "Progress indicators have a new rounded, colorful style, and more configurations to choose from, including a wavy shape and variable track height."

**Previous updates — Dec 2023: Non-text contrast (NTC)**
- Anatomy: Added an end stop indicator to improve accessibility
- Contrast: Higher contrast between track and active indicator to enhance the perception of progress
- Motion: New motion behavior
- Shape: Rounded corners

**Differences from M2 — July 2022: Added to Material 3**
- Color: New color mappings and compatibility with dynamic color (M2 was boxier/neutral).

### Responsive layout
- **RTL**: mirror linear indicators horizontally; circular indicators don't need mirroring.
- **Large screens**: circular 24dp–240dp depending on placement and window size; reserve very large indicators for **large and extra-large windows, such as desktop**.
- Linear indicators dynamically adjust to the width of the window or element (e.g. a card) and should **always span the width of the UI element** they're placed within.

### 9. Do / Don't
- Do use a single indicator to show progress for a group of loading items.
- Do keep the determinate indicator accurately representing the progress it measures.
- Do use a stop indicator when the indicator sits inside a low-contrast container.
- Don't add progress indicators to every activity / every button in a list.
- Don't remove the stop indicator unless there's at least 3:1 visual contrast with surrounding surfaces.

### 10. Accessibility
- Users must be able to navigate to the indicator and understand what progress it communicates.
- Active indicator provides at least **3:1** contrast against most background colors; when inside another component (e.g. a button), 3:1 against that component — use the same color as its label text/icon and remove the track.
- Stop indicator required when track contrast is below 3:1 with its container or the surface behind it; the end of the track must be easy to identify.
- Use the **progress bar** accessibility role; write a label describing the process ("loading") and affected content — e.g. "Loading news article", "Refreshing page", "loading my episodes".

---

## Loading indicator

### 1. What it is / when to use vs. siblings
- **Recommended as a replacement for indeterminate circular progress indicators**; should replace most uses of it.
- Best for **short, indeterminate** waits **between 200ms and 5s**; use when progress isn't detectable or when it's not necessary to indicate how long an activity takes.
- Used for **pull-to-refresh** interactions.
- **Not** used for processes that transition from indeterminate to determinate — don't transition a loading indicator into a progress indicator.
- Always reflect an ongoing process; never simply decorative. Use **animation to grab attention, mitigate perceived latency, and indicate that an activity is in progress**.

### 2. Anatomy
**Active indicator · Container (optional)**
- **Active indicator**: a looping **shape morph sequence composed of seven unique Material 3 shapes**.
- **Container (optional)**: a **circle** providing extra contrast from body content. Show it when the loading indicator is placed **over other content**; not needed when placed directly on a surface. **Use the container with pull-to-refresh behavior.** When the container is visible, the active indicator changes color from **primary** to **on-primary-container**.

### 3. Variants & configurations
| Variant | M3 | M3 Expressive |
|---|---|---|
| Loading indicator | -- | Available |

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Containment | Default | -- | Available |
| Containment | Contained | -- | Available |

Measurements: "To ensure sufficient margins, the size is **48dp** while the shape container is **38dp**." Loading indicators have a **single token set**.

### 4. Placement
- Centered on the element while loading a page or container.
- When loading more items on a page with existing content, place it in the **empty space where the new content will appear**; avoid overlapping existing content.
- Can be placed **within other components** (e.g. buttons — validating a form, checking for updates; or as the icon in a tab) to show an ongoing action without taking up much space.
- Pull-to-refresh: can appear **on top of the content or adjacent to it**, at the beginning of lists, grid lists, and card collections.

### Responsive layout
- Default **48dp**; flexible between **24dp and 240dp** depending on placement and window size. Avoid exceeding min/max.
- The **ratio between container and active indicator stays the same** when resizing.
- Reserve very large indicators for **large and extra-large windows, like desktop**. As pane/window size grows, scale the indicator so it stays proportional to the empty space around it; **never exceed 240dp**. Default size is ideal for mobile and other compact windows.

### 5. Behavior — pull-to-refresh
- Used in pull-to-refresh on **Jetpack Compose only**. Pull-to-refresh is an Android system feature that manually refreshes screen content with an action or gesture.
- Best with dynamic content that updates frequently, where people have a high chance of seeing new content after refreshing.
- **Threshold**: the indicator must pass a threshold before the app refreshes; completing the gesture after the threshold initiates refresh; **reversing the gesture past the threshold cancels** the refresh.
- The indicator remains visible until the refresh completes and new content is visible, or the person navigates away from the refreshing content.
- **Don't scroll the loading indicator off-screen** — it hides the status of the refresh and implies the refresh belongs to a specific component (e.g. a card) instead of the whole screen.

### 6. Color
- **Default** (uncontained): active indicator → **Primary**.
- **Contained**: active indicator → **On primary container**; container → **Primary container**.

### 8. M3 Expressive update (verbatim content)
**May 2025** — "The loading indicator is designed to show progress that loads in under five seconds. It should replace most uses of the indeterminate circular progress indicator." **New component added to catalog.**
Loading indicators:
- Are used in pull-to-refresh functionality
- Can be contained or uncontained
- Use shape and motion to capture attention
- Can scale in size

### 9. Do / Don't
- Do center it in the middle of the page or container, or in the empty space where content will appear.
- Do show the container when placed over other content and for pull-to-refresh.
- Do keep it in view until the activity completes.
- Don't transition from a loading indicator to a determinate progress indicator.
- Don't scroll it off screen.
- Don't use it decoratively.

### 10. Accessibility
- Users must be able to navigate to it, understand what progress it communicates, and **initiate a content refresh without relying on a gesture**.
- Active indicator: at least **3:1** contrast against most container and surface colors; **the indicator must have 3:1 with the background, but the container does not**. Inside another component (e.g. button), 3:1 against that component.
- Pull-to-refresh can't be accessible by swiping alone — provide an alternate single-pointer refresh (refresh button in a menu, in an app bar, or directly alongside the content).
- Use the **progress bar** accessibility role; label e.g. **"loading news article"**, **"refreshing page"**.

---

## Snackbar

### 1. What it is / when to use vs. siblings
- Informs users of a process an app **has performed or will perform**; appears temporarily toward the bottom of the screen; must not interrupt the user's experience — people can browse page content without interacting with it.
- Discriminator vs Dialog:

| Component | Priority | User action |
|---|---|---|
| Snackbar | Low priority | Optional: Snackbars disappear automatically |
| Dialog | High priority | Required: Dialogs block app usage until the user takes a dialog action or exits the dialog (if available) |

- Use snackbars for messages that are **minimally interruptive and don't require user action**. Use a dialog for important messages requiring immediate action. **Choose the component based on the importance of the message** — this messaging strategy helps **avoid overusing snackbars**.
- **Frequency: only one snackbar may be displayed at a time.**
- **Actions: a snackbar can contain a single action.** "Dismiss"/"cancel" actions are optional (and a dismiss action is unnecessary since snackbars disappear on their own by default).

### 2. Anatomy
**Container · Supporting text · Action (optional) · Close button / Icon (optional close affordance)**
- **Text label / supporting text**: short, clear updates on processes performed; directly relates to the process. In compact window sizes it can be up to **two lines**.
- **Container**: rectangular, grey background, **completely opaque** so text labels stay legible; uses a solid background color with a **shadow** to stand out against content. An app can apply *slight* transparency as long as text remains clearly legible.
- **Action**: a single **text button** with colored text to distinguish it from the text label. If an action is long, it can be displayed on a **third line**.

### 3. Configurations
Single line · Single line with action · Two lines · Two lines with action · Two lines with longer action.

### 4. Placement
- At the **bottom of a UI, in front of the main content**. Can be nudged upward to avoid overlapping bottom UI elements such as FABs or docked toolbars.
- Avoid placing in front of frequently used touch targets or navigation.
- May span the **entire width of the screen only when the UI does not use persistent navigation components** like app bars or navigation bars. Full-width snackbars can push up FABs when they appear.
- **FABs**: snackbars appear **above** FABs — not in front of, not behind.
- Web/keyboard: avoid positioning so it completely obscures actionable elements; adjust snackbar size so focused elements remain visible.

### Responsive layout
- **Compact**: expand vertically from **48dp to 64dp** to accommodate one or two lines of text, maintaining a **fixed distance from the leading, trailing, and bottom edges** of the screen.
- **Medium & expanded** (tablet, desktop): scale **horizontally** for longer strings; ideal line length is **40–60 characters**; use a **flexible distance from the trailing edge**; aim for a **single line of text with an optional button**. Can be **left-aligned or center-aligned** if consistently placed in the same spot at the bottom.
- Don't place snackbars flush to one edge of the layout. Don't place consecutive snackbars side by side.

### 5. Behavior
- Snackbars appear without warning but don't block interaction with page content.
- Without actions: can **auto-dismiss after 4–10 seconds, depending on platform**. Avoid auto-dismissing snackbars on web unless there's also inline feedback.
- With actions: **remain on screen until the user acts on the snackbar or dismisses it** (actionable snackbars shouldn't auto-dismiss).
- **Consecutive snackbars must appear one at a time**; a snackbar with updated information can immediately replace an outdated one. Don't stack snackbars.
- Don't animate other components (e.g. the FAB) along with snackbar animations.

### 6. Color
Container → **Inverse surface**; Icon (optional close affordance) → **Inverse on surface**; Action → **Inverse primary**; Supporting text → **Inverse on surface**. New color mappings + dynamic color compatibility vs M2. Snackbars use a color intended to stand out against UI elements — use the default color mapping to avoid conflicts.

### 8. Differences from M2
- Color: New color mappings and compatibility with dynamic color.
- Behavior: Clarified that snackbars can either appear temporarily (dismissive) or persist until the user takes an action (non-dismissive).

### 9. Do / Don't
- Do keep the text label to one line when possible (up to two lines on mobile).
- Do use a text button with colored text for the action; display an **"Undo"** action to let people amend choices.
- Do extend container width in wide layouts to accommodate longer text labels.
- Don't add icons to snackbars — if the message needs an icon, use a different component such as a dialog.
- Don't use stylized text or inline links; add a button instead, or use a different component.
- Don't use a filled or elevated button in a snackbar (draws too much attention).
- Don't give the text label the same color as the text button.
- Don't significantly alter the shape of the snackbar container.
- Don't place snackbars in front of navigation components, FABs, or elements in focus.
- Snackbars shouldn't be the only way to access a core use case.

### 10. Accessibility
- Users must be able to: be alerted but not disrupted when a snackbar appears; move focus to an actionable snackbar; take action using assistive technology.
- **Web requirement** — auto-dismissing snackbars are inaccessible for people with low vision or who need more time. Two fixes: (1) **add inline feedback** — also communicate the information inline or near the triggering action (e.g. change a "Save" button label to "Saved" alongside the snackbar); (2) **make the snackbar actionable** so it doesn't dismiss until acted on.
- Common acceptable auto-dismiss durations: **4–10 seconds** (each platform has its own requirements).
- **Focus**: announce the message but **don't move focus**; don't automatically move focus; **don't trap focus**; on web provide a shortcut to move focus to actionable snackbars (like **Alt+G**), clearly documented (e.g. a help article). On exit, focus ideally returns to the element that triggered the snackbar or the next most logical element; on **Android Compose** focus may move to the nearest visible element or the first actionable item on the page.
- **Keyboard**: `Tab` moves focus between interactive elements; `Esc` dismisses the snackbar when in focus.
- **Announcements**: announce on appearance without grabbing focus. Android and web: use a **live region with a polite (queued)** announcement, not assertive. **iOS 17+** uses polite announcements by default. If a snackbar appears at app launch, announce it **after the page's title** and don't give it focus.
- Note: Material Web doesn't yet include the snackbar component; this guidance still applies to custom-made snackbars.

---

## Tooltips

### 1. What it is / when to use vs. siblings
- Adds additional context to a button or other UI element. Two variants: **plain** and **rich**.
- **Plain**: briefly describes a UI element; best for **labelling UI elements with no text**, like icon-only buttons and fields. Not needed when the element already has label text.
- **Rich**: provides additional context — e.g. describing the value of a feature; best for **longer text like definitions or explanations**; can optionally contain a **subhead, buttons, and hyperlinks**.

### 2. Anatomy
- **Plain tooltip**: Container · Supporting text.
- **Rich tooltip**: Subhead (optional) · Container · Supporting text · Text button (optional).
  - **Subhead**: brief, ideally one line; summarizes/describes the message. Important to include when the rich tooltip appears automatically (e.g. on page load).
  - **Text buttons**: up to **two**, brief and relevant to the supporting text; keep them short so they sit side by side.

### 3. Sizes / measurements
Plain tooltip:
| Attribute | Value |
|---|---|
| Container height | 24dp |
| Padding | 8dp |

Rich tooltip:
| Attribute | Value |
|---|---|
| Top padding | 12dp |
| Bottom padding | 8dp |
| Left and right padding | 16dp |

Rich tooltip configurations (5 common): Subhead + supporting text + two buttons · Subhead + supporting text + one button · Subhead + supporting text · Supporting text + one button · Supporting text + two buttons. Headline and number of buttons are configurable.

### 4. Placement
- **Plain**: by default positioned **directly above** the parent element.
  - Visual boundary present (e.g. a button) → distance **4dp**.
  - No visual boundary (e.g. text baselines) → distance **8dp**.
  - If the element is in an **app bar**, the plain tooltip appears **below** the element at the same distance.
- **Rich**: by default positioned to the **bottom right** of the parent element; adjusts position to avoid going off screen. **Dynamic positioning adjusts in increments of 8dp.**
- Tooltips shouldn't cover the parent element.
- **Desktop**: tooltips may appear **centered below** the parent element and remain visible while moving within the target region.

### 5. States / behavior
- Trigger: **hover** on desktop, **tap and hold** on mobile. Persistent rich tooltips only appear when **clicked or tapped**.
- **Transient by default**: both plain and rich tooltips disappear **1.5 seconds** after navigating away from the target region. Triggering a new tooltip immediately closes any other open tooltip — only one tooltip at a time.
- **Persistent rich tooltips** appear when the parent element is clicked, or when the page loads and a new feature is being explained. They remain active even when leaving the target region and only disappear once the person interacts with another UI element. **Hovering doesn't trigger them.** Avoid using persistent rich tooltips on icon buttons.
- Tooltips can appear on **hover or focus** of an actionable element (button, navigation rail); rich tooltips can also appear by **selecting** an element instead of hovering/focusing.

### 6. Color
- Plain: Supporting text → **Inverse on surface**; Container → **Inverse surface**.
- Rich: Subhead → **On surface variant**; Container → **Surface container**; Supporting text → **On surface variant**; Text button → **Primary**.

### 8. Differences from M2
- Color: New color mappings and compatibility with dynamic color.
- Shape: Rich tooltips have **more rounded corners**.

### 9. Do / Don't
- Do use plain tooltips to label icon-only buttons.
- Do use rich tooltips to provide extra information and actions about a UI element or new feature.
- Do keep subheads to one line; avoid wrapping to more than one line.
- Don't hide critical information within tooltips — it's easy to miss; use an interruptive dialog instead.
- Don't wrap plain tooltip text to multiple lines or include many pieces of information.
- Don't stack rich tooltip buttons when it can be avoided.
- Don't display more than one tooltip at a time.
- Don't let a tooltip hide crucial information.

### 10. Accessibility
- Users must be able to receive a tooltip message and **activate a tooltip with a keyboard or switch input**.
- Tooltips without required actions should remain on screen long enough for people to receive the information without disrupting their flow.
- Tooltip containers must not block important information or prevent completing an action.
- **Focus order** within a rich tooltip moves **top to bottom** between interactive elements (parent element → inline link → text button). **Avoid trapping screen reader and keyboard focus**; people must be able to move linearly through the rest of the page.
- **Keyboard**: `Tab` → focus lands on button, if available; `Space` or `Enter` → activates the focused element.
- Tooltips should have the **Tooltip** role, or similar; label all elements in the tooltip according to their own accessibility guidance.

---

## Menus

### 1. What it is / when to use vs. siblings
- Use a **menu** to show a **temporary** set of actions. To show actions on screen at all times, use a **toolbar** instead.
- A menu takes up **less space than a set of radio buttons or chips**.
- Menus can open from many components: icon buttons, split buttons, text fields, buttons, selected text, filter chips.
- **Context menus** provide actions for a specific element (an image, highlighted text) and usually open with a **secondary click** (right-click on a mouse, two-finger tap on a trackpad).
- Use menus for: overflow menus, text field dropdown menus, select menus, context menus.
- Variant discriminator: **vertical menus** = recommended for new designs (rounded corners, standard + vibrant color styles, more selection states, submenu motion); **baseline menu** = still available, works in existing products, but lacks the latest shapes, color styles, selection states, and motion.

### 2. Anatomy
**Vertical menu (11 elements):** Menu item · Leading icon (optional) · Menu item text · Trailing icon (optional) · Badge (optional) · Trailing text (optional) · Container · Supporting text (optional) · Label text (optional) · Gap (optional) · Divider (optional).
**Baseline menu (6 elements):** List item · List item leading icon · List item trailing icon · Container · List item trailing text · Divider.
- **Menu items** can include label text, leading icons, trailing icons, and keyboard commands. When an item can only be used under specific conditions, it should appear **disabled rather than be removed**.
- **Gaps (optional)**: visually divide items into distinct groups; more expressive than dividers and make the relationship between items clear. Rules: avoid changing the size of the gap; limit to **one or two** gaps per menu; **don't use gaps in scrollable menus**. Gaps are **not currently available on web**.
- **Dividers (optional)**: more subtle separation. Use for **scrollable menus** and **text fields with a dropdown menu** where a grouped treatment isn't appropriate. **On web, use a divider** to separate menu items.

### 3. Variants & configurations
| Variant | M3 | M3 Expressive |
|---|---|---|
| Vertical menus | -- | Available |
| Menu (baseline) | Available | Available |

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Color | Standard | Available | Available |
| Color | Vibrant | -- | Available |
| Layout | Standard | Available | Available |
| Layout | Grouped | -- | Available |

**Baseline menu measurements:**
| Attribute | Value |
|---|---|
| Container width | 112dp min, 280dp max |
| Corner radius | 4dp |
| Vertical label text alignment | Center-aligned |
| Horizontal label text alignment | Start-aligned |
| Left/right padding | 12dp |
| Left/right padding with-icon | 12dp |
| List item height | 48dp |
| Padding between elements within a list item | 12dp |
| Divider top/bottom padding | 8dp |
| Divider height | 1dp |
| Divider width | Dynamic |
| Leading/trailing icon size | 24dp |

Baseline menus have **square corners**; vertical menus have **round corners** and expressive styling.

### Flexibility & slots
- Menus have custom **slots** supporting more flexible item layouts. Think of the menu item as a container with a **swappable slot**; slots can appear anywhere in a menu.
- Slots work best with simple content: **images, progress indicators, color swatches**.
- Slot rules: keep the menu accessible; elements must follow the rules and interaction patterns of the menu component; **keep the same menu item padding**; targets **48x48dp or larger**.
- **Don't add buttons, switches, or other direct actions into the menu item.** Nested elements should perform only one action — multiple actions can break keyboard navigation and screen reader functionality.

### 4. Placement
- A menu is positioned **relative to the window edge**; it typically appears below, next to, or in front of the element that generates it. Menus temporarily appear **in front of all other permanent UI elements**.
- A menu should open when a person **selects an element** (icon, button, text field) **or performs a specific action to trigger it, like right-click or press-and-hold**.
- If a menu would be cut off, it automatically repositions to appear to the **left, right, or above** the generating element. Opened at the top of the screen → expands downward; opened at the bottom → expands upward.
- **Submenus** open **next to the parent menu item without overlapping it**, positioned to the side. Best on large screens where there's space. Submenus are **not currently available on Jetpack Compose**.

### Adaptive design
- **Compact window sizes**: consider adapting menus into **bottom sheets** — more space for additional items and longer labels, better readability.
- **Medium and expanded windows**: menus are most effective, appearing in context with the content; they can display more items and use **submenus** to organize complex option sets. On large screens a menu is often more appropriate than a bottom sheet.

### 5. States & interaction
- Vertical menu states (6): **Enabled · Disabled · Hovered · Focused · Pressed · Active (main menu reveals submenu)**.
- Baseline menu states (5 each for default and selected menu items): Enabled · Disabled · Hovered · Focused · Pressed.
- **Shape morphing** creates an expressive active state: as focus moves between submenus, the corner shape changes to highlight the active menu — corners of the **focused** submenu become **more rounded**, the unfocused submenu becomes **less rounded**. Focus follows the currently hovered or focused submenu.
- **Motion**: menus use an enter and exit transition creating a relationship between the menu and the element that generated it. When a menu expands, the **trigger element becomes pressed**; when an item is selected, a **ripple** appears on touch. In dense products such as desktop, menus can **open instantly** to reduce motion.
- **Selecting**: when a menu opens, the corresponding button/icon button stays visually the same **with the addition of a pressed state** — including when opened via keyboard shortcut. Choosing an option doesn't change the icon that generated the menu.
- **Single-select**: one item at a time; selecting a new item automatically unselects the previous. **Multi-select**: many selected items; stays open until the person dismisses the menu.
- **Filtering** (autocomplete): a menu can include a text field to filter options; as someone types the list filters to relevant results and **menu items ease into their new position**.
- **Scrolling**: menus can scroll when all items can't display at once and show a **persistent scrollbar**. Don't use gaps if a menu scrolls (currently unsupported).
- **Density** (web only): density levels control spacing between elements; increasing density decreases **top and bottom padding**; documented range **0 to -3**.

### 6. Color
Two color mappings: **Standard** = Surface-based, lower visual emphasis; **Vibrant** = Tertiary-based, higher visual emphasis. Vibrant menus are more prominent and **should be used sparingly**.
- **Vertical menu — standard** roles (11, as listed): On surface variant · On surface · On surface (state layer) · Surface container low · On surface variant · On surface variant · Tertiary container (selected) · On tertiary container (selected) · On surface variant · On surface variant · On tertiary container (selected).
- **Vertical menu — vibrant** roles (11, as listed): On tertiary container · On tertiary container · On tertiary container (state layer) · Tertiary container · On tertiary container · On tertiary container · Tertiary (selected) · On tertiary (selected) · On tertiary container · On tertiary container · On tertiary (selected).
- **Baseline menu** roles (9, as listed): On surface variant · On surface · **On surface — opacity: 0.08** (state layer) · Surface container · On surface variant · On surface variant · On surface variant · Surface container highest · Outline variant.

### 8. M3 Expressive update (verbatim content)
**November 2025** — "**Vertical menus** were introduced with new shapes, color styles, selection states, and refined submenu motion. Gaps can be used for a more flexible layout on Android."
Variants:
- Added **vertical menus**, recommended for new designs
- Baseline **menu** is still available
Color styles:
- Standard
- Vibrant
Framing: "Vibrant colors help selected menu items stand out." A menu in the **vibrant** color style is more expressive; one with **standard** colors is more utilitarian.

**Differences from M2**
- Color: New color mappings and compatibility with dynamic color.
- Variants: Dropdown menu and exposed dropdown menu are now **both referred to as menu**, since they differ only in the element which opens the menu surface.

### 9. Do / Don't
- Do use a menu for temporary actions; use a toolbar for always-visible actions.
- Do group similar actions with a gap or divider to make menus scannable.
- Do disable unavailable items rather than removing them.
- Do position submenus to the side of the parent item without covering it.
- Do use vertical menus for new designs.
- Don't change the size of the gap; don't exceed one or two gaps; don't use gaps in scrollable menus (or on web).
- Don't overuse vibrant menus.
- Don't add buttons, switches, or other direct actions into a menu item.

### 10. Accessibility
- Users must be able to navigate to, open, and close a menu, and navigate between and select menu items.
- **Selection cues**: by default menu items change **shape and color** when selected; default color contrast is **3:1 between selected and unselected** menu items; it's **recommended to include another visual cue, like a checkmark**.
- **Initial focus**: when a menu opens, focus goes to the **first menu item**.
- **Exiting**: selecting an option; tapping **Escape** or outside the menu; using the system back button. Where focus lands after closing depends on the app.
- **Interactability**: disabled menu items **can receive focus but aren't selectable**; **dividers and gaps can't receive focus**.
- Slot targets must be **48x48dp or larger**.
- **Keyboard navigation**:

| Keys | Actions |
|---|---|
| Tab | Focus lands on menu |
| Space or Enter | Closed menus: opens menu or submenu. Open menus: selects a menu item |
| Up / Down arrows | Closed menus: opens menu. Open menus: moves focus to the next item |
| Left / Right arrows | Opens or closes a submenu |
| Letters | Focus moves to the next menu item starting with letter |
| Escape | Closes menu |

- **Labeling**: the accessibility label should be **the same as the menu item text**. Roles: Menu item text → a11y label "Preview"; **Role (Web): Menu item**; **Role (Android Views): Generic actionable element**; **Role (Jetpack Compose): Generic actionable element**. For menu items with text and an icon, mark the icon's accessibility label as **decorative** to avoid redundant verbalizations.

---

## Date pickers

### 1. What it is / when to use vs. siblings
- Let people select a date or range of dates; can display past, present, or future dates. Must be suitable for the context in which they appear.
- Three variants: **Docked date picker**, **Modal date picker**, **Modal date input**.
  - **Docked**: allows selection of a **specific date and year**; displays a date input field by default; a dropdown calendar appears when the input field is tapped; either form of entry can be used. Ideal for navigating dates in the **near AND distant** future or past because it provides multiple ways to select dates. Best for **medium and expanded** window sizes.
  - **Modal date picker**: calendar-based selection in a dialog. **Don't** use it to prompt for dates in the **distant past or future** (e.g. date of birth) — use a modal input picker or docked date picker instead.
  - **Modal date input**: manual entry of a date or range using keyboard numbers, in a dialog. Default view for dates that don't require a calendar view. Alternatively, a **text field with appropriate hint text** can prompt for dates, such as in a form.
- Embedding: **dialogs** on compact window sizes like mobile; **text field drop-downs** on medium and expanded breakpoints like tablet and desktop.
- M3 renamed the variants to be device-independent: former **desktop** date picker → **docked**; former **mobile** date picker and date input → **modal date picker** and **modal date input**, reinforcing that the user must take an action.

### 2. Anatomy
- **Docked date picker (specs, 11):** Outlined text field · Menu button: Month selection · Menu button: Year selection · Icon button · Weekdays label text · Unselected date · Today's date · Outside month date · Text buttons · Selected date · Container. (Guidelines list, 7: Text field · Menu button · Icon button · Label text · Menu · Text buttons · Container.)
- **Docked date picker with open dropdown (8):** Outlined text field · Menu button: Month selection (pressed) · Menu button: Year selection (disabled) · Header · Menu · Selected list item · Unselected menu list item · Container.
- **Modal date picker — day selection (13):** Headline · Supporting text · Header · Container · Icon button · Icon buttons · Weekdays · Today's date · Unselected date · Text buttons · Selected date · Menu button · Divider. (Guidelines list, 12: Headline · Supporting text · Container · Icon button · Previous/next month buttons · Day of week labels · Today's date · Unselected date · Text buttons · Selected date · Menu button · Divider.)
- **Modal date picker — year selection (10):** Headline · Supporting text · Header · Container · Icon button · Unselected year · Selected year · Text buttons · Divider · Menu button.
- **Modal date picker — range selection (15):** Headline · Supporting text · Icon button · Header · Text button · Icon button · Weekdays label text · Container · Today's date · Unselected date · **In-range active indicator** · **In-range date** · **Month subhead** · Selected date · Divider.
- **Modal date input (8):** Headline · Supporting text · Header · Container · Icon button · Outlined text field · Text buttons · Divider.
- **Full-screen date picker (14):** Headline · Supporting text · Icon button · Container · Text button · Icon button · Divider · Day of week labels · Today's date · Selected date range · Unselected date · Text buttons · Selected date range start date · Month label.

### 3. Configurations
- Docked: **Day selection · Month selection · Year selection**.
- Modal date picker: **Single date selection · Date range selection · Year selection**.
- Modal date input: **Single date input · Date range input**.

### 4. Placement / responsive
- **Compact window sizes** (mobile): a **full-screen modal date picker** is recommended to increase readability and touch target size; it can cover the entire screen. It adds a **close affordance (x) icon button** and a **Save** confirmation.
- **Medium and expanded window sizes**: the **docked** date picker works best.
- Docked date pickers appear **just below the input field**.
- **The sizing of the docked and modal date picker components doesn't scale responsively to different window sizes** — don't scale the date picker responsively to a larger size.

### 5. States & behavior
- Element states for date and year selection (5): **Default (enabled) · Disabled · Hovered · Focused · Pressed (ripple)**.
- **Docked**: dates can be added by keyboard or by navigating the calendar UI — both immediately available. Docked pickers **adjust size dynamically** (to the selected month). The **year selection menu replaces the calendar view**. Month and year selection can be navigated with back/next arrows or by tapping the dropdown menu.
- **Modal**: navigate months by **swiping horizontally**; navigate years by **scrolling vertically**; **tap the year** to access the year picker.
- **Range selection**: tap the start and end dates on the calendar; navigate across months by **scrolling vertically**. Common use cases: booking a flight, reserving a hotel.
- **Selection** is indicated through **color**, drawing visual attention. In date ranges, start and end dates are selected while dates in between appear **connected with a subtle highlight** (differences between selected range and today's date are shown through color and fill).
- **Swap** between modal date picker and modal date input using the **edit** or **calendar** icon.
- **Appearing/disappearing**: like other dialogs, modal date pickers use an **enter and exit transition** pattern. Exit by confirming (**OK**) or dismissing (**Cancel**); interacting outside the dialog also dismisses; otherwise the picker retains focus.

### 6. Color
Role palettes as listed per view (ordered lists; see gaps for per-element pairing):
- **Docked date picker (11):** Primary · On surface variant · On surface variant · On surface · On surface · Primary · On surface variant · Primary · Surface container high · Primary · On primary.
- **Docked date picker menu (7):** Primary · On surface variant · On surface · Outline variant · Surface container high · Surface variant · On surface.
- **Modal date picker — day selection (12):** On surface · On surface variant · Surface container high · On surface variant · On surface variant · On surface · Primary · On surface · Primary · Primary · On surface variant · Outline variant.
- **Modal date picker — year selection (9):** On surface · On surface variant · Surface container high · On surface variant · On surface variant · Primary · Primary · Outline variant · On surface variant.
- **Modal date picker — range selector (14):** On surface · On surface variant · On surface variant · Surface container high · Primary · On surface variant · On surface · Primary · On surface · **Secondary container** · **On secondary container** · Outline variant · On surface variant · Primary.
- **Modal date input (7):** On surface · On surface variant · Surface container high · On surface variant · Primary · Primary · Outline variant.
*Inferred* (not stated per-element in the source; the ordered role lists do not align one-to-one with the anatomy order): container surface is **Surface container high** across variants; selected date uses **Primary / On primary**; in-range dates use **Secondary container / On secondary container**; dividers use **Outline variant**. Treat these as likely rather than confirmed pairings.

### 7. Typography
M3 vs M2: "Titles and labels are **larger** and have **increased spacing to accommodate 48dp target size**." (No type-scale role names in the text — see gaps.)

### 8. Differences from M2
- Typography and spacing: Titles and labels are larger with increased spacing to accommodate 48dp target size.
- Color: New color mappings and compatibility with dynamic color.
- Variants: Renamed to be device-independent (desktop → docked; mobile date picker / date input → modal date picker / modal date input). M3 pickers also have **no shadow** and rounded corners.

### 9. Do / Don't
- Do clearly indicate important dates, such as current and selected days, and follow common patterns like a calendar view.
- Do use a full-screen modal picker on compact windows; a docked picker on medium/expanded.
- Do make the modal date input the default view for dates that don't require a calendar view (e.g. a day in 1979).
- Do accept a range of input formats (dashes, spaces, slashes, dots, leading 0 on single-digit month/day).
- Don't use a modal date picker for dates in the distant past or future (e.g. date of birth).
- Don't scale date pickers responsively to a larger size.
- Don't apply input masks — don't auto-add slashes or special characters while the user is typing.
- Don't increase density: it would limit tappable/clickable targets and harm accessibility.

### 10. Accessibility
- Users must be able to **enter dates manually by inputting text, without using the picker**, and use multiple input methods. On the docked picker, use the text field; on the modal picker, the date input option must be available via the **edit icon**.
- Interactive targets for all elements meet Material's **48x48dp** minimum touch target requirement.
- Two entry methods: direct text entry into a text field, and the date picker. The **calendar icon is the exclusive entry point** for the picker, which reduces key presses and makes picker interaction optional. **Each input is a separate tab stop.**
- **Accessible date input**: format the date only **after the user hits "Enter" or navigates out of the text field**; no input masks (they change what screen reader users typed). Accept a range of formats to reduce errors.
- **Optional Clear button**: remove it if not needed, to reduce tab stops for keyboard users.
- **Keyboard shortcut affordance**: provide the shortcut key in the **tooltip** and include it in the hint description so screen readers read it (e.g. **Shift + Page up** = previous year).
- **Truncated labels**: truncating labels isn't ideal, but tooltips show full text on hover or keyboard focus. **Days of the week are not interactive and not focusable via keyboard**, but the tooltip is available on pointer hover; the date picker relies on the **conventionality of these abbreviations** for some assistive technology users.
- **Contrast**: dates should have at least **4.5:1** between the link text colors and the background.
- **Keyboard navigation**:

| Keys | Actions |
|---|---|
| Enter/return | Enter/return |
| Enter/return | Closes the calendar and saves the selected date |
| Page up/down | Move to the same date on next/previous month |
| Home/End | Move to the first day of the month |
| Shift + Page up/down | Moves to the same date in the next/previous year |
| Shift + M | Moves to the month list dropdown |
| Shift + Y | Moves to the year list dropdown |

- **Labeling**: the text field's accessibility label should state the purpose of the input (e.g. event date, reservation date) and match the placeholder text when empty. Helper text below the field specifies the format (e.g. MM/DD/YYYY or YYYY/MM/DD) and acts as the field description; **default helper text is "MM/DD/YYYY"** and is customizable.

| Element | A11y label | Role |
|---|---|---|
| Previous / next month and year | "{label}" | Button |
| Month and year dropdowns | "{label}" | Button |
| Days of the week | Column header | |
| Month grid | Grid | |

- **Screen reader verbalizations**: labels enumerate the complete date so users hear "Monday, August 17" instead of just "17" — full day, month, date, and year.

---

## Time pickers

### 1. What it is / when to use vs. siblings
- Let people enter a specific time value; **modal and cover the main content**, displayed in dialogs; used to select hours, minutes, or periods of time.
- Two variants: **dial** and **input**.
  - **Dial**: mimics a round watch face; select by tapping a number or dragging the dial selector track.
  - **Input**: specify a time using keyboard numbers; must be reachable from any other mobile time picker interface by tapping the **keyboard icon**.
- Common use cases: setting an alarm, scheduling a meeting. **Not ideal for nuanced or granular time selection**, such as milliseconds for a stopwatch application.
- Make sure time can easily be selected by hand on a mobile device.

### 2. Anatomy
- **Time picker dial (specs, 14):** Headline · Time selector separator · Container · Period selector container · Period selector label text · Clock dial selector center · Clock dial selector track · Text button · Icon button · Clock dial selector container · Clock dial label text · Clock dial container · Time selector label text · Time selector container.
- **Time picker dial (guidelines, 17):** Label (headline) · Time selector separator · Input field · Input text · Period selector (selected) · Period selector text (selected) · Container · Period selector outline · Period selector text · Dial selector track · Dial label (selected) · Text buttons · Icon button · Dial label (unselected) · Clock dial · Input text (selected) · Input field (selected).
- **Time picker input (specs, 10):** Headline · Time input field separator · Container · Period selector container · Period selector label text · Text button · Icon button · Time input field supporting text · Time input field label text · Time input field container.
- **Time picker input (guidelines, 13):** Label (headline) · Time selector separator · Input field · Input text · Period selector (selected) · Period selector text (selected) · Container · Period selector outline · Period selector text (unselected) · Text buttons · Icon button · Input text (selected) · Input field (selected).
- **Container**: like dialogs, appears **above other screen elements**; surfaces behind it get a **temporary scrim overlay** to make them less prominent.
- **Input selector**: a unique kind of text field input — differs from typical text fields by having (a) an added **highlight** to call attention to the selected field, (b) a **larger shape, size, and font**, (c) a **label below the field**. Hours and minutes have **separate inputs**. For 12-hour clocks an **AM/PM selector appears to the right of minutes**; for 24-hour clocks the AM/PM selector **shouldn't appear**.
- **Dial selector**: 12-hour dial → all numbers in the **outer ring**; 24-hour dial → **even numbers in an inner ring, odd numbers in an outer ring** (24h illustration: hours 0–11 outer dial, hours 12–23 inner dial).
- **Text & icon buttons**: icon buttons switch between the input selector (**keyboard** icon) and the dial selector (**clock** icon), positioned in the lower left. Text buttons exit (**Cancel**) and save (**OK**).

### 3. Sizes / measurements

**Time picker dial — vertical** (identical values listed for **horizontal**):
| Element | Attribute | Value |
|---|---|---|
| Container | Width | Dynamic |
| Container | Height | Dynamic |
| Container | Headline alignment | Left |
| Container | Top/bottom padding | 24dp |
| Container | Left/right padding | 24dp |
| Time selector container | Width | 96dp |
| Time selector container | Width (24h vertical) | 114dp |
| Time selector container | Height | 80dp |
| Period selector container | Width (vertical layout) | 52dp |
| Period selector container | Height (vertical layout) | 80dp |
| Period selector container | Width (horizontal layout) | 216dp |
| Period selector container | Height (horizontal layout) | 38dp |
| Clock dial container | Size | 256dp |
| Clock dial selector handle | Size | 48dp |
| Clock dial selector center | Size | 8dp |
| Clock dial selector track | Width | 2dp |

**Time picker input:**
| Element | Attribute | Value |
|---|---|---|
| Container | Width | Dynamic |
| Container | Height | Dynamic |
| Container | Headline alignment | Left |
| Container | Top/bottom padding | 24dp |
| Container | Left/right padding | 24dp |
| Time input field container | Width | 96dp |
| Time input field container | Height | 72dp |
| Period selector container | Width | 52dp |
| Period selector container | Height | 72dp |

Configurations: **Vertical layout (default on mobile)** and **Horizontal layout**; **24-hour dial** in vertical and horizontal layouts; **12-hour and 24-hour time picker inputs**. 24-hour selection is set **outside the time picker component, typically through system settings**.

### 4. Placement / adaptive design
- Time pickers **shouldn't be obscured by other elements** and should **change orientation or variant to avoid being cropped** by the screen edge.
- They are **modal windows above a scrim**, putting them at the forefront of view.
- Can swap between orientation or variant depending on device orientation and viewport constraints — e.g. change to **landscape orientation on larger breakpoints or when viewport height is limited**, to avoid scrolling the dial presentation. In landscape, the stacked input and selection options are positioned **side-by-side**.
- **Fallback to the input time picker** when there isn't enough vertical real estate to present the landscape orientation without scrolling.
- **Density**: don't apply density to the time picker dial when the viewport is constrained — use an **input picker** instead.
- **Scrolling**: time pickers should avoid scrolling and swap orientation/variant based on device orientation or viewport size. They don't scroll with elements outside the modal window, such as the background.

### 5. States & behavior
- States (4): **Enabled · Hover · Focus · Pressed**.
- Two primary selection methods: type a specific value in the hour and minute fields; or select the hour or minute field from the text input and adjust the clock dial to simultaneously change the corresponding time field above.
- **Appearing & disappearing**: like other dialogs, an **enter and exit transition** pattern. Exit by confirming (**OK**) or dismissing (**Cancel**); interacting outside the dialog also dismisses it; otherwise the time picker retains focus.
- **Toggle**: tapping the keyboard icon on a mobile time picker switches to the input picker.

### 6. Color
**Time picker dial (17 elements → 17 roles, in listed order):**
| Element | Role |
|---|---|
| Label (headline) | On surface variant |
| Time selector separator | On surface |
| Input field | Surface container highest |
| Input text | On surface |
| Period selector (selected) | Tertiary container |
| Period selector text (selected) | On tertiary container |
| Container | Surface container high |
| Period selector outline | Outline |
| Period selector text | On surface |
| Dial selector track | Primary |
| Dial label (selected) | On primary |
| Text buttons | Primary |
| Icon button | On surface variant |
| Dial label (unselected) | On surface |
| Clock dial | Surface container highest |
| Input text (selected) | On primary container |
| Input field (selected) | Primary container |

**Time picker input (13 elements → 13 roles, in listed order):**
| Element | Role |
|---|---|
| Label (headline) | On surface variant |
| Time selector separator | On surface |
| Input field | Surface container highest |
| Input text | On surface |
| Period selector (selected) | Tertiary container |
| Period selector text (selected) | On tertiary container |
| Container | Surface container high |
| Period selector outline | Outline |
| Period selector text (unselected) | On surface |
| Text buttons | Primary |
| Icon button | On surface variant |
| Input text (selected) | On primary container |
| Input field (selected) | Primary container |

### 8. Differences from M2
- Color: New color mappings and compatibility with dynamic color (M2 selected hour and AM text were purple on a purple background; M3 selected hour and AM text are black with different background colors).

### 9. Do / Don't
- Do allow manual time entry through text input rather than exclusively through the dial selector.
- Do make the input picker reachable from the dial selector via the keyboard icon.
- Do make a time input picker the default option for time selection that doesn't require a dial view.
- Do change orientation or variant so the picker is always fully visible.
- Don't use time pickers for nuanced/granular time selection such as milliseconds.
- Don't show the AM/PM selector for 24-hour clocks.
- Don't let time pickers scroll or be obscured by other elements.
- Don't apply density to the dial when the viewport is constrained.

### 10. Accessibility
- Users must be able to select or enter hours/minutes (and in some cases seconds/milliseconds), choose from multiple time formats including 24-hour clock view and AM/PM, and enter time selection manually using input fields.
- If a screen is not large enough to display the dial selector, consider displaying the **input selector alone**. **Currently for Android Views, the dial selector is always visible.**
- **Targets for dial selectors should be 48x48dp.**
- **Keyboard navigation**: `Tab` → focus lands on (non-disabled) time slot; `Space` or `Enter` → activates the (non-disabled) time slot.
- If the input text is correctly linked, screen readers read the **component's role first, then the UI text**. The dial selector reads a selection of total hours, e.g. **"Hour 7 of 12"**.

**Dial selector labels/roles:**
| Element | Accessibility label | Role (Wiz and Jetpack Compose) | Role (Android Views) |
|---|---|---|---|
| Hour input (input picker) | Hour | Text input | - |
| Minutes input | Minute | Text input | - |
| AM/PM selection | AM or PM | Radio button (in list) | Checkbox (in list) |
| Keyboard button | Toggle input picker | Button | Button |
| Cancel button | Cancel | Button | Button |
| OK button | OK | Button | Button |
| Clock dial time selection (dial selector) | {Value} Hours or minutes of {Total} | Button | - |

**Input selector labels/roles:**
| Element | Accessibility label | Role (Wiz and Jetpack Compose) | Role (Android Views) |
|---|---|---|---|
| Hour input (input picker) | Hour | Text input | - |
| Minutes input | Minute | Text input | - |
| Clock button | Toggle dial picker | Button | Button |
| Cancel button | Cancel | Button | Button |
| OK button | OK | Button | Button |

---

## Gaps — what is *not* recoverable from these source exports

> **Before treating a measurement here as unavailable:** many of these are published as
> `md.comp.*` values in the generated Compose token files, which are collected in
> [`component-tokens.md`](../component-tokens.md) — container heights and widths, shape
> assignments, elevation levels, icon sizes, and internal spacing. Check there first. Those are the
> Compose token values, so attribute them as such rather than as guideline text.


- **No `md.sys.*` / `md.comp.*` token names anywhere.** All eight pages replace the token tables with a stub ("Browse the component elements, attributes, tokens, and their values"). Every color role above is the human-readable role name.
- **Per-element color pairing is not stated.** Colors are published as an *ordered list* alongside a separately ordered anatomy list. Where the two lists have equal length and align (time pickers 17↔17 and 13↔13; snackbar 4↔4; tooltips 2↔2 and 4↔4) the pairing is reliable. Where they don't (badges nav bar/rail, baseline menu 9 roles vs 6 anatomy elements, docked date picker) the pairing is an inference and is flagged as such.
- **No measurement tables** for: snackbar, vertical menus (M3 Expressive), all date picker variants, and the circular/linear progress indicator size tables — the source only carries diagram captions, not values.
- **No type-scale role names** on any page, including the date pickers typography section.
- **M3 Expressive update sections exist on only three of the eight pages** (progress indicators — Aug 2024; loading indicator — May 2025; menus — November 2025). Badges, snackbar, tooltips, date pickers, and time pickers have a *Differences from M2* section only. The loading indicator has no *Differences from M2* section (it is a new component).
- **Availability & resources** sections are empty on every page (platform support matrices did not convert).
