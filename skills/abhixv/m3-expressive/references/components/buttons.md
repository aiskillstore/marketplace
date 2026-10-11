# Buttons (M3 / M3 Expressive) — source-faithful extract

Sources: `components_all-buttons.md`, `components_buttons.md`, `components_button-groups.md`, `components_split-button.md`, `components_icon-buttons.md`, `components_segmented-buttons.md` (m3.material.io, updated 2026-07-17).

---

## All buttons — choosing between the 10 types

### 1. What it is + when to use vs. siblings

There are **10 types of buttons in Material 3**: Button, Toggle button, Icon button, Toggle icon button, Split button, Standard button group, Connected button group, Floating action button (FAB), Extended FAB, FAB menu.

Discriminating rule = **level of emphasis**.

| Emphasis | Component | Discriminating rationale | Example actions |
|---|---|---|---|
| **High** — primary, most important, or most common action on a screen | Extended FAB, FAB, FAB menu | Largest and most visually prominent buttons; designed for a page's primary action. Extended FAB is best on large screens. FAB menu provides multiple options. | Create, Compose, New thread, New file |
| High | Button (filled) | Primary color palette makes it the most prominent button **after the FAB**. Used for final or unblocking actions in a flow. | Save, Confirm, Done |
| High | Split button | Primary color palette + menu icon; best for key actions **with multiple options**. | Send, Add, Create |
| High | Button group (standard) | Uses color, motion, and shape to capture attention. Use to show **multiple key actions**. | Back, Pause, Next |
| **Medium** — important actions that don't distract from the main task | Button (tonal) | Secondary color palette; less prominent than filled. For final/unblocking actions, or supporting actions. | Save, Confirm, Done |
| Medium | Button (elevated) | Secondary color palette **plus a shadow**. Only use when a button requires visual separation from a **patterned background**. | Reply, View all, Add to cart, Take out of trash |
| Medium | Button (outlined) | For actions that need attention but aren't primary ("See all", "Add to cart"); also the button for **giving someone the opportunity to change their mind or escape a flow**. | Reply, View all, Add to cart, Take out of trash |
| **Low** — optional/supplementary, least prominence | Connected button group | Shows multiple related options. Use for **changing the content visible on a page**. | Walk, Bike, Drive |
| Low | Button (text) | No outline or fill. For actions **not essential to the user journey**. | Learn more, View all, Change account, Turn on |
| Low | Icon button | **Most compact and subtle** type of button; optional supplementary actions such as "Bookmark" or "Star." | Add to Favorites, Print |

### 4. Placement (hierarchy)

- **One high emphasis button**: each screen should contain a single prominent button for the primary action. Arrangement of on-screen elements should clearly communicate that other buttons are less important.
- A product can show more than one button at a time; use **different color styles** to create visual hierarchy and indicate importance.
- A button's level of emphasis helps determine its **appearance, typography, and placement**.
- Combine styles on the same screen to focus attention on a primary action while offering alternatives. Documented pairings: filled (high) + text (low); outlined (medium) + filled (high); text (low) + outlined (medium). In two-button rows the lower-emphasis button sits to the **left** of the higher-emphasis button (LTR examples).
- Documented three-tier example on one screen: a **filled button** for the high-emphasis action, a **text button** for the low-emphasis action, and an **extended FAB** for the highest-emphasis action.
- Use a filled button on its own for a single important action.

### 9. Do / Don't

- **Do** choose a higher-emphasis button for the more important action when showing multiple actions.
- **Don't** place a button below another button if there's space to place them side-by-side.

---

## Button (common buttons)

### 1. What it is + when to use it

Buttons communicate actions people can take. Overview facts:
- **Two variants**: default and toggle.
- Can contain an **optional leading icon**.
- **Five color options**: elevated, filled, tonal, outlined, text.
- **Five size recommendations**: extra small, small, medium, large, extra large.
- **Two shape options**: round and square.
- Keep labels concise and use **sentence case**.

Buttons are just one option for representing actions and shouldn't be overused; too many buttons on a screen disrupt visual hierarchy. Consider a **navigation rail, set of chips, text links, or icon buttons** for additional actions.

Color-style selection rules:
- **Elevated** = tonal button + a shadow. Use only when absolutely necessary, e.g. when the button requires visual separation from a visually prominent background. Buttons at higher elevations have more emphasis; use sparingly — for high emphasis prefer **filled**.
- **Filled** = most visual impact after the FAB; for important, final actions completing a flow (Save, Join now, Confirm). Use sparingly, ideally for only **one action on a page**. Can use tertiary colors in some cases.
- **Tonal** = when a lower-priority button needs slightly more emphasis than an outline would give (e.g. **Next** in an onboarding flow). Uses the secondary color mapping.
- **Outlined** = medium emphasis; important but not the primary action. Pairs well with filled to indicate alternative, secondary actions. Stroke around container, no fill by default.
- **Text** = lowest priority actions, especially when presenting multiple options. Container isn't visible until interaction. Often placed in cards, dialogs, snackbars — since text buttons have no visible container in their default state they don't distract from nearby content. However, because there's no container, the **label text color must always be recognizable from non-button text and elements**.

### 2. Anatomy

Three parts: **Container**, **Label text**, **Icon (optional)**.

- **Label text** — the most important element; describes the action that will occur on tap. Very brief, ideally **1–3 words**. Sentence case (capitalize only the first word and proper nouns), e.g. **Book with Flights**, not **BOOK WITH FLIGHTS**. Never truncate or wrap; always fully visible on a single line.
- **Container** — holds label text and optional icon. Text-style buttons have a visible container **only when hovered, focused, or pressed**. Round shape → fully rounded corners. Square shape → more subtle rounding that changes with button size. Width dynamically adjusts to the label text; can be responsive/stretch horizontally; must never be narrower than its label text.
- **Icon (optional)** — visually communicates the action and draws attention. Placed on the **leading side**, before the label text (left of label in LTR, right of label in RTL). Standard leading/trailing icon size is **20dp** (change from M2).

### 3. Sizes / variants / configurations

Variants:

| Variant | M3 | M3 Expressive |
|---|---|---|
| Default | Available | Available |
| Toggle (selection) | -- | Available |

Configurations:

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Size | Small (default) | Available | Available |
| Size | XS, M, L, XL | -- | Available |
| Shape | Round (default) | Available | Available |
| Shape | Square | -- | Available |
| Color | Elevated, filled (default), tonal, outlined, text | Available | Available |
| Small button padding | 24dp | Available | **Not recommended. Use 16dp** |
| Small button padding | 16dp | -- | Available |

Corner sizes (radius) by size:

| | XS | S | M | L | XL |
|---|---|---|---|---|---|
| A. Round button | Full | Full | Full | Full | Full |
| B. Square button | 12dp | 12dp | 16dp | 28dp | 28dp |
| C. Pressed state | 8dp | 8dp | 12dp | 16dp | 16dp |

Height: M3 default buttons are **40dp** tall with fully rounded corners (M2 was 36dp with slightly rounded corner radius).

Token sets: button token sets are separated into **common tokens, color, and size**; baseline button token sets are organized by color.

### 4. Placement

Typically placed throughout the UI in: **Dialogs, Modal windows, Forms, Cards, Toolbars**. Also placed within **standard button groups**.

- Text buttons in **dialogs**: align to the **trailing edge** — right in LTR, left in RTL.
- Align text buttons in snackbars/cards to keep emphasis on the content.
- Outlined and text buttons should be placed on **simple backgrounds**, not visually prominent backgrounds such as images or videos.
- Adaptive: when scaling layouts for large-screen devices, buttons can adapt their **visual presentation, size, alignment, and arrangement** to fit different contexts and user needs. Choose the best button position based on screen size. Documented example — filled buttons **end-aligned below** flight information in a **compact window**; **start-aligned beside** flight information in a **large window**.
- To avoid very long buttons in large windows, **constrain button width or place buttons beside other elements**.
- The size and placement of buttons can change as parent containers (e.g. cards) adapt for larger screens. Keep items, including buttons, in the **same order** between large and small screens for consistent screen reader and keyboard navigation. Buttons can move in the layout, but elements should remain in the same order.
- Icon and label text stay **centered and grouped** as button width changes.

### 5. States and interaction behavior

States documented for every color style (default and toggle): **Enabled, Disabled, Hovered, Focused, Pressed**.

- **Elevated** style: elevation of **1** by default and **0** when disabled.
- **Outlined** style: container fill is invisible at rest, but opacity and state layers behave the same as other button styles when disabled, hovered, focused, or pressed.
- **Text** style: container is invisible at rest; opacity and state layers behave the same as other styles when disabled, hovered, focused, pressed. **There is no toggle text button.**

**Shape morph — pressed**: when pressed, buttons can morph to become more square. Both round and square buttons should have the **same pressed shape**. Corner radius value differs per size (see table above).

**Shape morph — selected**: toggle buttons also change resting shape from **round (unselected) to square (selected)** by default. If the resting unselected shape is square, the selected shape should be **round**.

**Toggle buttons**: use for binary selections such as **Save** or **Favorite**. When pressed they can change color, shape, and labels. Use an **outlined icon when unselected** and a **filled version when selected**; if a filled version doesn't exist, **increase the weight** instead. If the label changes between states, keep the character count similar — changing the label significantly is disruptive to the user and the page layout.

**Rapid clicks**: on the web, use a modified motion curve to avoid resonant effects from overlapping animations when multiple clicks/taps in succession are anticipated.

### 6. Color role mapping

Five built-in color styles: elevated, filled, tonal, outlined, text. Default and toggle buttons use different colors. **Toggle buttons don't use the text style.** Icons and labels now share the same color (change from M2). Neutral text button is no longer recommended.

| Part | 1. Default | 2. Toggle unselected | 3. Toggle selected |
|---|---|---|---|
| Elevated container / Elevated icon & label | Surface container low / Primary | Surface container low / Primary | Primary / On primary |
| Filled container / Filled icon & label | Primary / On primary | Surface container / On surface variant | Primary / On primary |
| Tonal container / Tonal icon & label | Secondary container / On secondary container | Secondary container / On secondary container | Secondary / On secondary |
| Outlined container / Outlined icon & label | Outline variant (outline) / On surface variant | Outline variant (outline) / On surface variant | Inverse surface / Inverse on surface |
| Text icon & label | Primary | -- | -- |

Note: these color roles were chosen for design coherence and familiarity. **Other color roles can be used as long as the container and text have a 3:1 contrast ratio** (e.g. tertiary and on tertiary). Color values are implemented through design tokens.

### 8. M3 Expressive update (May 2025)

> Buttons now have a wider variety of shapes and sizes, toggle functionality, and can change shape when selected.

- **Variants and naming**: Default and toggle (selection); color styles are now **configurations** (elevated, filled, tonal, outlined, text).
- **Shapes**: Round and square; shape morphs when **pressed**; shape morphs when **selected**.
- **Sizes**: Extra small; Small (existing, default); Medium; Large; Extra large.
- **New padding for small buttons**: **16dp** (recommended to match padding of new sizes); **24dp** (no longer recommended).
- Summary: Five sizes · Toggle (selection) · Two shapes · Two small padding widths.

**Differences from M2:**
- **Color**: new color mappings and compatibility with dynamic color; icons and labels now share the same color; neutral text button is no longer recommended.
- **Icons**: standard size for leading and trailing icons is now **20dp**.
- **Shape**: fully-rounded corner radius and additional height options (M2: **36dp** height with slightly rounded corner radius; M3: default buttons are taller at **40dp** with fully rounded corners).

### 9. Do / Don't

- **Do** use visually-prominent filled buttons for the most important actions.
- **Do** use buttons for discrete actions.
- **Don't** clutter the UI with too many buttons — present low-priority actions in overflow menus or as icon buttons.
- **Don't** set a container width narrower than its label text / a fixed width smaller than the label text.
- **Do** use sentence case for label text.
- **Don't** wrap label text; keep it on a single line for maximum legibility.
- **Don't** truncate label text.
- **Do** place the icon leading (left in LTR, right in RTL).
- **Do** use icons that clearly communicate their meaning (e.g. a shopping-cart icon with the label "Add to cart").
- **Don't** vertically align an icon and text in the center of a button (icon above label).
- **Don't** use two icons in the same button.
- **Don't** underline the text button — use hyperlinked body text instead to emphasize links.
- **Don't** ungroup the icon and label text or anchor them to opposite sides of the button.
- **Don't** allow the button to stretch in a way that creates long, flat buttons with very little content inside.
- **Use caution** placing outlined or text buttons next to visually similar elements such as chips or large text; the outlined style is very similar to chips — consider a filled or tonal button instead.
- **Use caution** placing outlined buttons on top of images; a contrasting custom container fill helps label legibility, or use a filled button instead. Outlined buttons **can** be used on backgrounds with a color gradient.
- **Do** use different sized buttons in a button group to emphasize the main action from secondary actions; buttons with primary actions should have higher visual emphasis through **size, color, or shape**.

### 10. Accessibility

- **Use cases**: people must be able to use a button to perform an action, and navigate to and activate a button.
- **Target areas**: extra small and small icon buttons must have a target size of **48x48dp or larger** to be accessible.
- **Color contrast**: enabled buttons need a **3:1 contrast ratio with the background**. Measured from the **container** for elevated, filled, and tonal styles, and from the **label text** for outlined and text styles.
- **200% text size**: choose concise strings to avoid excessive wrapping/truncation. On Android, labels should be concise enough to fit within **two lines** at 200% text size; if a label exceeds this and is truncated, provide an alternative way to access the full content **in a single tap**.
- **Keyboard**: `Tab` = navigate to a button; `Space` or `Enter` = activate a button.
- **Labeling**: the accessibility label should match the visible label text (e.g. **Done**, **Send**, **Reply**); it can contain extra contextual information if necessary.

---

## Icon button

### 1. What it is + when to use it

Use icon buttons to display common actions. Icon buttons **must use a system icon with a clear meaning**.
- **Two variants**: default and toggle.
- **Many configurations**: color, size, width, and shape (four color styles, five sizes, three widths, two shapes).
- On web, display a **tooltip describing the action** while hovering.
- In toggle buttons, use the **outlined** style of an icon for the unselected state and the **filled** style for the selected state.

- **Default** icon buttons can open other elements, such as a menu or search.
- **Toggle** icon buttons represent binary actions toggled on/off, such as **favorite** or **bookmark**.

Four color styles in order of emphasis: **Filled → Tonal → Outlined → Standard**. Highest emphasis = filled; lowest = standard.
- **Filled**: visual impact and key actions requiring high emphasis (e.g. downloading, deleting). Avoid overusing on a screen.
- **Tonal**: middle ground between filled and outlined; secondary actions paired with a high-emphasis action (e.g. **Raise hand** in a video meeting — greater emphasis than the outlined menu button, less than the filled **End call** button).
- **Outlined**: medium emphasis; when the button isn't the main focus of the interaction, such as browsing sets of cards / indicating more content is available.
- **Standard**: low-emphasis buttons, or when placing buttons on a **colorful surface**.

Use filled, tonal, or outlined when the button needs more visual separation from the background.

### 2. Anatomy

Two parts: **Icon**, **Container**.

- **Icon** — visually communicates the action; meaning must be clear and unambiguous. **Default icon buttons should use filled icons.** Toggle buttons use an **outlined** icon when unselected and a **filled** version when selected.
- **Container** — provides increased contrast and hierarchy where more visual separation from the background or other elements is needed.

### 3. Sizes / variants / configurations

Variants:

| Variant | M3 | M3 Expressive |
|---|---|---|
| Default | Available | Available |
| Toggle (selection) | Available | Available |

Configurations:

| Category | Options | M3 | M3 Expressive |
|---|---|---|---|
| Size | Small (default) | Available | Available |
| Size | XS, M, L, XL | -- | Available |
| Shape | Round (default) | Available | Available |
| Shape | Square | -- | Available |
| Color | Filled (default), tonal, outlined, standard | Available | Available |
| Width | Default | Available | Available |
| Width | Narrow, wide | -- | Available |

**Five sizes with heights:**
- Extra small — **32dp**
- Small — **40dp** (default)
- Medium — **56dp**
- Large — **96dp**
- Extra large — **136dp**

**Three widths**: Default, Narrow, Wide.

Corner radius:

| | XS | S | M | L | XL |
|---|---|---|---|---|---|
| A. Round button | Full | Full | Full | Full | Full |
| B. Square button | 12dp | 12dp | 16dp | 28dp | 28dp |
| C. Pressed state | 8dp | 8dp | 12dp | 16dp | 16dp |

Token sets organized by **common tokens, color, and size**. Filled, tonal, and outlined icon button tokens are **deprecated** in favor of the new token sets; all other tokens remain available.

Use size and width to provide emphasis and visual hierarchy on a page with multiple buttons — the main action should be the most visually prominent (color or size), e.g. starting/stopping a timer, play/pause. When buttons have similar importance, they should be the **same size**.

### 4. Placement

- Can be placed **directly on the background** or in most container components: **cards, app bars, toolbars**.
- Commonly used in other components such as app bars and cards; use for common, easily understandable actions. **Only use a few icon buttons at once.**
- In dense layouts, group popular actions by placing many icon buttons next to each other in components like a **toolbar** or **button group** — these draw attention or add interaction between buttons.
- Multiple icon buttons can be placed in a **standard button group** to add interaction and motion between buttons when pressed.

### 5. States and interaction behavior

States per color style (default and toggle): **Enabled; Disabled (10% state layer); Hovered (8% state layer); Focused (10% state layer); Pressed (10% state layer)**. State layers slightly change button color; **disabled states have different base colors**.

- **Standard** icon button: container is invisible at rest but visible when the state layer is applied.
- **Shape morph — pressed**: while pressed, icon buttons can morph to become more square. Both round and square icon buttons should have the **same pressed shape radius**; the value differs per size.
- **Shape morph — selected**: toggle icon buttons change resting shape from **round (unselected) to square (selected)** by default. If the resting shape is square, the selected shape should be **round**.
- **Hover**: on hover the icon button displays a **tooltip describing its action**, not the name of the icon.
- **Selection**: toggle icon buttons allow a single choice to be selected or deselected (e.g. add/remove from favorites). When placed in a button group, icon buttons **change shape** to help the selected button stand out. The icon should become **filled** to represent selection; if no filled version exists, use **semibold** weight.

### 6. Color role mapping

Four built-in color styles: filled, tonal, outlined, standard. Default and toggle buttons use different color roles per style.

| Part | 1. Default | 2. Toggle, unselected | 3. Toggle, selected |
|---|---|---|---|
| Filled container / Filled icon | Primary / On primary | Surface container / On surface variant | Primary / On primary |
| Tonal container / Tonal icon | Secondary container / On secondary container | Secondary container / On secondary container | Secondary / On secondary |
| Outlined container / Outlined icon | Outline variant (outline) / On surface variant | Outline variant (outline) / On surface variant | Inverse surface / Inverse on surface |
| Standard icon | On surface variant | On surface variant | Primary |

Note: other color roles can be used as long as the container and text have a **3:1 contrast ratio** (e.g. tertiary and on tertiary).

### 8. M3 Expressive update (May 2025)

> Icon buttons now have a wider variety of shapes and sizes, changing shape when selected. When placed in button groups, icon buttons interact with each other when pressed.

- **Variants and naming**: Default and toggle (selection); color styles are now **configurations** (filled, tonal, outlined, standard).
- **Shapes**: Round and square options; shape morphs when **pressed**; shape morphs when **selected**.
- **Sizes**: Extra small; Small (default); Medium; Large; Extra large.
- **Widths**: Narrow; Default; Wide.
- Summary: Five sizes · Two shapes · Three widths.

Differences from M2: new color mappings and dynamic color compatibility; icon buttons were previously called **toggle buttons** — there are now two variants, default and toggle.

### 9. Do / Don't

- **Do** use icons with a background (container) to make them easy to see on any surface.
- **Do** use color styles to make the primary action clear when mixing button variants.
- **Do** use the filled style sparingly.
- **Do** use toggle icon buttons only when the icon can be selected.
- **Don't** use toggle icon buttons for actions that don't have a selected state, such as an icon button for an overflow menu.
- **Do** ensure the meaning of the icon is clear (e.g. heart = Favorite).
- **Don't** apply density to icon buttons by default.
- On web, **do** display a tooltip describing the action while hovering.

### 10. Accessibility

- **Use cases**: understand the meaning of the icon; navigate to and activate an icon button; where applicable a tooltip should be available to describe the icon button's purpose.
- **Target size**: extra small and small icon buttons must have a target size of **48x48dp or larger**. Target size of each icon button should be at least **48dp even when nested** inside another component.
- **Contrast**: the icon must have contrast of at least **3:1** with the surface or background. Avoid colors with contrast below 3:1.
- **Icon accessibility requirement**: for selected toggle buttons, if a filled version of an icon doesn't exist, increase icon weight to **semibold**; if semibold doesn't provide enough visual change, use **bold**. This ensures selection is communicated through **at least two properties, not just color**. Does not apply to default (non-toggle) buttons.
- **Density**: don't apply density by default — it lowers targets below the required **48x48 CSS pixels** minimum. Provide density options people can choose; controls for adjusting density must themselves maintain a target size of at least **48x48 CSS pixels**.
- **Keyboard**: `Tab` = focus lands on (non-disabled) icon button; `Space` or `Enter` = activates the (non-disabled) icon button.
- **Labeling**: the accessibility label describes the action being executed, e.g. **Add to favorites**, **Bookmark**, **Send message**. On web, icon buttons should display a tooltip with an accessibility label.

---

## Button groups (standard + connected)

### 1. What it is + when to use it

**Two variants: standard and connected.** Button groups are containers that hold buttons and icon buttons of many shapes and sizes; they apply shape, motion, and width changes to make buttons more interactive. They **apply shape morph when pressed and selected**, and work with **all button sizes: XS, S, M, L, XL**. **Connected button groups replace the segmented button.**

- **Standard button group** — adds interaction *between adjacent buttons* so they respond to each other. When a button in a standard group is selected: the selected button changes **shape and width**; a selected toggle button also changes **color**; **adjacent buttons move and temporarily change width**. More precisely, the interaction changes the **width, shape, and padding** of the selected or activated button, which in turn adjusts the width of the buttons **directly next to it**.
- **Connected button group** — helps people **select options, switch views, or sort elements** in a page. Behaves like a standard group except it does **not** affect adjacent buttons. Use when button content is **related and buttons can be selected**. Should be used for **single- or multi-select patterns that use toggle buttons**. Avoid using a connected group when none of the buttons can be toggled.

Support for **single-select, multi-select, and selection-required**.

### 2. Anatomy

One part: **Container**. Button groups are **invisible containers** that add padding between buttons and modify button shape. They **don't contain any buttons by default**.

- **Standard** group container: has padding between buttons so they can animate width and shape without disrupting the product layout; **hugs the width** of the buttons inside.
- **Connected** group container: should **span the width of the page or surface** it's placed on, increasing the button widths inside. In larger windows, consider adding a **maximum width** to avoid it growing too wide.

**Common layouts** (mix and match): Label buttons · Label buttons and icon buttons · Extra small icon buttons · Large icon buttons.

### 3. Sizes / variants / configurations

Variants:

| Variant | M3 | M3 Expressive |
|---|---|---|
| Standard button group | -- | Available |
| Connected button group | Available as segmented button | Available |

Configurations:

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Size | XS, S, M, L, XL | -- | Available |
| Default shape | Round, square | -- | Available |
| Selection | Single-select, multi-select, selection-required | Available as segmented button | Available |

**Standard button group inner padding** (changes by button size to ensure a minimum accessible target of 48dp):

| Size | Inner padding |
|---|---|
| XS | 18dp |
| S | 12dp |
| M | 8dp |
| L | 8dp |
| XL | 8dp |

**Connected button group**: use **2dp** padding for all connected button groups at every size — this provides visual consistency at scale.
- **Round** connected group: outer shape is **fully round**; inner shape remains square with corner sizes XS **4dp**, S **8dp**, M **8dp**, L **16dp**, XL **20dp**.
- **Square** connected group: outer shape corner sizes XS **4dp**, S **8dp**, M **8dp**, L **16dp**, XL **20dp**; inner padding 2dp at every size.

**Minimum widths**: extra small and small connected button groups have **48dp target areas and a minimum width of 48dp**.

Tokens: standard and connected button group tokens are organized **by size**; select variant and size from the token set menu. Button and icon button tokens live on their own pages.

**Density**: button groups adapt to the density of the buttons inside — they adapt to the height of the buttons inside, including when density is applied (examples at 0, -1, -2, -3 density).

### 4. Placement

- Button groups should move through layouts **together in a single line**; they **shouldn't wrap to a second line**. Multiple button groups can be **stacked** to keep items close together, but button groups **don't interact vertically**.
- Connected groups span the width of the page/surface, with **margins from the edge**; add a max width in larger windows.
- Resizing modes for button groups and individual buttons:
  - **Fixed**: manually define the button **width (narrow to wide), size (XS to XL), or padding at each window size**.
  - **Flexible**: automatically increase or decrease the width of buttons and the group. Button groups grow until all flexible buttons are at their **largest width**.
- If adjusting button width manually, **avoid stretching icon buttons beyond the wide setting**.
- **Compact windows**: consider smaller, narrower buttons so all buttons fit. **Large and extra large windows**: consider larger, wider buttons to better fill available space.
- When scaling to larger windows, preserve the visual hierarchy of each button using color and size — the **primary action should remain the largest, widest, or most visually prominent at all window sizes**.
- **Overflow**: buttons at the **trailing edge** of the group can collapse into an **overflow menu** at smaller window sizes and become visible again at larger sizes. Place the overflow menu at the **trailing end** of the group. Buttons **outside** the group aren't affected by button group behavior.

### 5. States and interaction behavior

States documented: **Enabled, Disabled, Hovered, Focused, Pressed** (connected group *selected* states: Enabled, Hovered, Focused, Pressed).

- **Standard group**: when a button is **pressed**, the group modifies the **width and shape of that button and adjacent buttons**. When a toggle button is **selected**, its shape should change between **square and round**; color changes according to the button specs. A selected button changes shape and **briefly changes the width of itself and adjacent buttons**.
- **Connected group**: different shape changes than standard groups; selecting a button **does not affect adjacent buttons** — only the shape of the pressed/selected button changes.
- **Selected** (both): a selected button should change shape **from round to square, or square to round**.

### 6. Color role mapping

Button groups have **no color properties**. They can use the default button or toggle button color styles — **filled, tonal, outlined, elevated**. **Avoid using standard icon buttons or text buttons**, as they have no container treatment.

### 8. M3 Expressive update (May 2025)

> Button groups apply shape, motion, and width changes to buttons and icon buttons to make them more interactive.

**New component added to catalog.**
- **Variants and naming**: Added **standard button group**; added **connected button group**. Use instead of segmented button, **which is no longer recommended**.
- **Configurations**: Works with all button sizes — **XS, S, M, L, and XL**; applies default shape to all buttons — **round or square**.

### 9. Do / Don't

- **Do** make all buttons in a standard group the same **size (XS to XL) and shape (round or square)** by default.
- **Only** use multiple sizes in a group for **hero moments**; avoid mixing sizes frequently.
- **Only** use a different shape in a group when a button is **selected**, or to add meaning or contrast — reserve shape differences for key interactions.
- **Do** mix and match button variants, widths, and colors to emphasize what's important and visually group related buttons.
- **Don't** mix color styles in **connected** button groups — it can make selection and emphasis unclear.
- **Don't** use a connected group when none of the buttons can be toggled.
- **Don't** let button groups wrap to a second line.
- **Don't** reduce the padding in extra small and small button groups.

### 10. Accessibility

- **Use cases**: navigate to and interact with each button in the group; identify when buttons are selected.
- Each button in a group must have a **minimum 48x48dp target**. Extra small and small button groups have **larger inner padding** to ensure accessible targets — avoid reducing that padding.
- **Initial focus**: the button group container is **not a focusable element**. Initial focus lands on the **first button** in the group, then moves to each button.
- **Keyboard**: `Tab` = navigates to the next button; `Space` or `Enter` = activates the focused button.
- **Labeling**: the container does **not** need to be labeled. Label each button per button and icon button accessibility guidance (e.g. an email icon labelled "email" with role "button").

---

## Split button

### 1. What it is + when to use it

Use to show **an action with a menu of related actions**. Split buttons add a menu of actions alongside a main action, reducing visual complexity by hiding extra options. Same size range as buttons and icon buttons: **XS, S, M, L, XL**. They work well alone or alongside common buttons, icon buttons, and button groups. Typically opens a **menu**, but can be customized to open other components like cards.

Split buttons can be a **different size** from other buttons on the page, especially since they take up more space; the most prominent controls can be larger while secondary controls in a split button can be smaller. **Scale up** the split button in large window sizes, or to create more emphasis in smaller windows (hero moments).

### 2. Anatomy

Four elements: **Leading button**, **Icon**, **Label text**, **Trailing button**.

- **Leading button** — can have an icon, label text, or both (three customizations: Label + icon · Label · Icon). Label should be **brief, just one or two words**, with an icon that best matches the action.
- **Trailing button** — should **always** have a menu icon; specifically the **expand and collapse icon**, since it rotates when selected. Avoid modifying the icon.
- In **right-to-left** languages the component layout is **mirrored**.

### 3. Sizes / variants / configurations

Variants:

| Variant | M3 | M3 Expressive |
|---|---|---|
| Split button | -- | Available |

Configurations:

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Size | XS, S, M, L, XL | -- | Available |
| Color | Elevated, filled, tonal, outlined | -- | Available |

Five recommended sizes matching buttons and icon buttons: **Extra small; Small (default); Medium; Large; Extra large.**

**Measurements** — text and icons are **optically centered** when the buttons are asymmetrical, and centered normally when symmetrical.

Menu icon offset when unselected:

| Size | Offset from center |
|---|---|
| XS | -1dp |
| S | -1dp |
| M | -2dp |
| L | -3dp |
| XL | -6dp |

Inner corner radius (changes depending on button sizing; **the space should always be 2dp**):

| Size | Inner corner radius |
|---|---|
| Extra small | 4dp |
| Small | 4dp |
| Medium | 4dp |
| Large | 8dp |
| Extra large | 12dp |

Tokens: split button token sets are organized **by size**.

### 4. Placement

- Split buttons can be used alongside other buttons and button groups.
- **Menu placement**: align the menu with the **trailing button** when possible. If there's not enough room, align the menu to one of the **sides** of the button (leading or trailing). Depending on window size, scroll position, and other factors the menu may need to appear elsewhere around the button — always try to align it with **one of the edges** of the button. Documented alignments: top aligned to trailing button; bottom aligned to trailing button; top right-aligned; top left-aligned; bottom right-aligned; bottom left-aligned.
- **The menu should be 4dp from the split button.**

### 5. States and interaction behavior

Split button states use the **same colors and state layers as buttons and icon buttons**.

- **Leading button shape**: the **inner corners change shape** for hovered, focused, and pressed states. States: Enabled · Disabled · Hovered · Focused · Pressed, pressed with focus.
- **Trailing button shape**: the inner corners change shape for hovered, focused, and pressed states, and the **icon becomes centered when selected**. States: Enabled · Disabled · Hovered · Focused · Pressed, pressed with focus · Selected, selected with focus.
- **Motion**: the split button uses the **standard motion scheme (not the expressive motion scheme)** when rotating the menu button. The menu button **rotates inwards 180°** when opened and closed; selecting the menu button rotates the icon inwards and applies shape morph, with a **10% state layer** when selected.

### 6. Color role mapping

Split buttons use the **same color schemes, colors, and state layers as standard buttons**. Unlike toggle buttons, the split button color **doesn't change when selected — only a state layer is applied**. Color configurations: **Elevated, Filled, Tonal, Outlined**.

### 8. M3 Expressive update (May 2025)

> The split button has a separate menu button that spins and changes shape when activated. It can be used alongside other buttons of the same size.

**New component added to catalog.**
- **Sizes**: Extra small; Small; Medium; Large; Extra large.
- **Color styles**: Elevated; Filled; Tonal; Outlined.

### 9. Do / Don't

- **Do** keep the leading label brief (one or two words) with an icon matching the action.
- **Don't** use very long labels (e.g. "32 minutes away").
- **Don't** change the trailing icon (e.g. to a refresh icon) — always use the expand/collapse menu icon.
- **Do** align the menu with the trailing button when possible.
- **Don't** modify the menu in unusual ways (e.g. irregular shape highlighting the selected item).

### 10. Accessibility

- **Use cases**: navigate to each button and interact with them; navigate to any element opened by the trailing button; understand the current selection state of the button.
- Each button in the split button needs a minimum target area of **48x48dp**. Extra small and small split buttons are **shorter than 48dp**, so target areas around them need to be at least **48dp tall**.
- **Initial focus**: focus lands on the **leading button** then moves to the **trailing button** (can depend on the operating system's settings); documented for both LTR and RTL.
- **Keyboard**: `Tab` = navigate between buttons; `Space` or `Enter` = activate focused button.
- **Labeling**: the leading button's accessibility label is the same as buttons (e.g. "Watch later" as both label text and accessibility label). The **trailing** icon button should have an extra state or similar label indicating the menu is **expanded or collapsed**, and should clearly indicate that there are more options related to the main action — e.g. main button "Watch later" → secondary button "More watch options." Label the opened menu per menu accessibility guidance.

---

## Segmented buttons (NO LONGER RECOMMENDED)

> **Segmented buttons are no longer recommended in the Material 3 expressive update. For those who have updated, use the [connected button group] instead, which has mostly the same functionality but with an updated visual design.** (This note appears on the Overview, Specs, Guidelines, and Accessibility sections.)

### 1. What it is + when to use it

Segmented buttons help people **select options, switch views, or sort elements**. Can contain **icons, label text, or both**. **Two variants: single-select and multi-select.** Use for simple choices between **two to five items** — for more items or complex choices, **use chips**.

- **Single-select**: select one option from a set, switch between views, or sort elements from up to five options (e.g. beverage size selector). Only 1 segment can be selected.
- **Multi-select**: select or sort from two to five options. Unlike single-select, **selection is not required** and a user may concurrently select anywhere from all to none of the options (e.g. filter by price range).

### 2. Anatomy

Five parts: **Segment**, **Container**, **Icon (optional)**, **Label text (optional)**, **Selected icon**. (Specs-section anatomy lists: Container · Icon, optional for unselected state · Label text.)

- **Segments** — 2–5 segments; each segment is clearly divided and contains label text, an icon, or both.
- **Container** — like common buttons, **fully rounded corners** by default.
- **Icons** — may be used as labels by themselves or alongside text. An icon used without label text must clearly communicate the option it represents.
- **Label text** — short and succinct. If a label is too long to fit within its segment, consider using an icon alone.

### 3. Sizes / measurements

| Attribute | Value |
|---|---|
| Container width | Dynamic based on labels |
| Segment width | Container width / total segments (Example: 1/3) |
| Height | 40dp |
| Outline width | 1dp |
| Label alignment | Center |
| Left/right padding | Min 12dp |
| Padding between elements | 8dp |
| Target size | 48dp |

**Density**: can be used in denser UIs where space is limited; applied **only to the height**. Each step down in density removes **4dp** from the height.

### 4. Placement

- Must have **adequate margins from the edge of the viewport or frame**; the button container shouldn't reach the edge of the viewport.
- On larger screens, set a **maximum padding for all button segments** so the set doesn't fill the screen.
- Can be placed on other components, such as **bottom sheets or full-screen dialogs**.

### 5. States and interaction behavior

- **Unselected** states: Enabled · Disabled · Hovered · Focused · Pressed.
- **Selected** states: Selected · Hovered on selected · Focused on selected · Pressed on selected.
- **Behavior**: when using both icons and label text, the **icon is replaced by the checkmark icon** when the segment is selected.

### 6. Color role mapping

Segmented button color roles used for light and dark schemes: **On surface**, **Outline**, **Secondary container**, **On secondary container**.

### 7. Typography

Labels use **sentence case** instead of all caps (change from M2).

### 8. M3 Expressive update (May 2025)

> The segmented button is no longer recommended. Use the **connected button group** instead.

Differences from M2: new color mappings and dynamic color compatibility; **optional check icon** to indicate selected state; taller container height of **40dp**; previously known as **toggle buttons**, now with two official variants (single-select and multi-select); **fully rounded** corners; labels use **sentence case** instead of all caps.

### 9. Do / Don't

- **Do** use 2–5 segments; **don't** use more than five segments in a single segmented button — scope the choices, or use another component such as chips.
- **Do** keep labels short and consistent in length; use consistent label types.
- **Don't** allow segments to wrap onto a new line.
- **Do** use icons in place of labels only when they clearly communicate their meaning.
- **Don't** mix icon-only labels with text labels — choose one label type and use it for all segments.
- **Do** allow adequate space for margins.
- **Don't** allow segmented buttons to span the full width of larger screens or panes — this leaves too much padding on either side of the segment label, making the button less usable.

### 10. Accessibility

- **Use cases**: navigate to and activate segmented buttons with assistive tech; understand what each segment selection will do.
- **Target size**: 48dp.
- **Contrast**: segmented buttons are clusters of similar components, so the **outline must have at least a 3:1 contrast ratio** with the background or surface to distinguish each button. Both a **checkmark icon and a color change** are used to distinguish selection — make sure color isn't the only way to show selection.
- **Initial focus**: focus starts in the **first segment** (leftmost in LTR, rightmost in RTL), regardless of selection state, for both single- and multi-select.
- **Keyboard**: `Tab` = focus lands on next enabled segment (both variants). `Space`/`Enter` = single-select: select focused segment; multi-select: select and unselect focused segment. (Accessibility prose adds: for **single-select**, `Space`/`Enter` will select *or unselect* the focused segment; for **multi-select**, it will select an un-selected segment, select all of the segments, or un-select a selected segment.)
- **Labeling**: the accessibility label comes from the visible label text (e.g. **Relevance**, **Distance**). With icons and no label text, the accessibility label describes the action being expressed, e.g. **Inexpensive** for one currency symbol. Single-select behaves like **radio buttons** — role label is **Radiogroup**. Multi-select behaves like **checkboxes** — role label is **Checkbox**.
