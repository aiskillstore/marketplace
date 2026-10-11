# Interaction — M3 reference extract

Sources: `foundations_interaction_states.md`, `foundations_interaction_gestures.md`, `foundations_interaction_inputs.md`, `foundations_interaction_selection.md`, `foundations_usability.md`, `foundations_building-for-all.md`. Nothing below is inferred; values absent from those pages are listed in `gapsNoted`.

---

## States

### 1. What it is + when to use vs. siblings
States show the interaction status of a component or UI element. Six named states: **Enabled**, **Disabled**, **Hover**, **Focused**, **Pressed**, **Dragged**.

Discriminating rules:

| State | Trigger / meaning | Emphasis |
|---|---|---|
| Enabled | Communicates an interactive component or element; uses the default styling for each interactive component | default |
| Disabled | Communicates an inoperable / non-interactive component or element | color change + reduced elevation |
| Hover | User has placed/paused a **cursor** above an interactive element | lower-emphasis surface overlay |
| Focused | User has highlighted an element using an input method such as **keyboard or voice** | higher-emphasis surface overlay |
| Pressed | User-initiated tap or click via cursor, keyboard, or voice input | high-emphasis; triggers a change in composition |
| Dragged | User presses and moves an element or component | low emphasis, to avoid distracting users from their task |

Key takeaways: states have **two visual indicators** to ensure accessibility; states can be **combined** (e.g. selection + hover); apply states **consistently across components**.

Scope of applicability:
- Focused applies to **all interactive components**.
- Pressed applies to **all interactive components**.

Resource on this page: Design Kit (`goo.gle/m3-design-kit`) — status **Available**.

No "M3 Expressive" / "M3 Expressive update" section exists on the States page (nor on Gestures, Inputs, or Selection). Of the six source pages, only **Usability** has an `Applying M3 Expressive` section — captured in full below.

### 2. Anatomy
Three stacked layers, in order: **(1) Container → (2) State layer → (3) Content**. The state layer is sandwiched between the container and the content.

- **State layer** — a semi-transparent covering (overlay) on an element that indicates its state. Fixed opacity per state. Systematic approach to visualizing states by using opacity.
- **Content** — icon or label text; supplies the state layer's color.
- **Interactive target** — larger than the state layer.

Rules:
- A layer can be applied to an **entire element** or in a **circular shape**.
- **Only one state layer can be applied at a given time.**
- To transition from an enabled style to a stateful style requires the addition of a state layer.
- Overlay may be applied to the entire component, to elements within a component, or as a circular shape over part of the component (stated for hover, focused, pressed; dragged = entire component or elements within a component).

### 3. Sizes / variants / configurations

| Item | Value |
|---|---|
| State layer size | **40dp** |
| Interactive target size | **48dp** |

State layer opacity values (fixed percentage per state, applied to the content color):

| State | Opacity |
|---|---|
| Hover | **+8%** |
| Focus | **+10%** |
| Press | **+10%** |
| Drag | **+16%** |

(Enabled and Disabled have no state-layer opacity value given.)

### 5. States and interaction behavior

**Enabled** — default styling. Shown for Button, FAB, Switch, Text field.

**Disabled**
- Communicated visually through **color changes and reduced elevation**.
- Disabled states **don't need to meet Material's contrast requirements**.
- Disabled components **can't be focused, dragged, or pressed**, and **don't change state when tapped or hovered over** (a disabled button doesn't inherit hover or other state layers).
- **There can be any number of disabled states in a layout.**

**Hover**
- Initiated by the user pausing over an interactive element using a cursor.
- Appear and disappear using a **low-emphasis animated fade**.
- Can be combined with **focused, activated, selected, or pressed**.
- **Only one hover state at a time in a layout** (based on cursor position).

**Focused**
- Initiated by pressing the **Tab** key on the keyboard (or equivalent).
- Many people use the **Tab** key or other shortcut to navigate the interactive elements of a web page, **like links, buttons, and chips**.
- When an element is tabbed to it appears in its focused state with a **ring-like keyboard focus indicator**; the indicator helps web users know where they are on the page. While focused, an element can be acted on with the keyboard.
- Can be combined with **hover, activated, or selected**.
- **Only one focus state at a time in a layout.**

**Pressed**
- Initiated by user keyboard or voice input on an interactive element (also cursor tap/click).
- A **ripple overlay** signifies a pressed state.
- Some components (buttons, cards) **can inherit elevation** to signify pressed.
- Activated states appear in **user-initiated order**.
- Can be combined with **hovered, focused, activated, or selected**.
- **Only a single pressed state at a time in a layout.**

**Dragged**
- Initiated when users touch and hold elements, using an input method such as a tap or click.
- Uses a **lower emphasis overlay**.
- Some components (list items, chips, cards) **can inherit elevation** to signify dragged.
- Draggable list item state sequence: enabled → hovered → dragged.
- **Only a single dragged state at a time within a layout.**

#### State inheritance matrix (exact component lists as published)

| State | Inherited by | NOT inherited by |
|---|---|---|
| **Disabled** (action, selection, input components) | Buttons, Cards, Checkboxes, Chips, List items, Radio buttons, Switches, Text fields | (communication, containment, navigation, some actions) App bars, Badges, Dialogs, Floating action buttons (FABs), Menus, Navigation bar/drawer/rail, Sheets, Tabs, Tooltips |
| **Hover** (action, selection, input components) | Buttons, Cards, Checkbox, Chips, Date and time pickers, List items, Slider, Switch, Text fields | (communication, containment, navigation) App bars, Badges, Dialogs, Menus, Navigation bar/drawer/rail, Sheets, Tabs |
| **Focus** (action, selection, input components) | Buttons, Cards, Checkbox, Chips, Date and time pickers, List items, Selection controls, Text fields | (most communication, containment, navigation) App bars, Badges, Banner, Card, Dialogs, Navigation bar/drawer/rail, Sheets |
| **Pressed** (action, selection, some containment components) | Buttons, Cards, Checkbox, Chips, List items, Text fields | (communication, navigation, some containment) App bars, Badges, Bottom navigation, Dialogs, Menus, Sheets, Tabs |
| **Dragged** (some containment and selection components) | Cards, Chips, List items, Sliders | (action, communication, navigation, some containment) App bars, Badges, Buttons, Dialogs, Menus, Navigation bar/drawer/rail |

Note: the Focus "NOT inherited" list as published contains **Card** even though Cards appear in the Focus "inherited" list — reproduced verbatim.

Components illustrated per state: Disabled — Checkbox, Icon button, Radio button, Segmented button. Hover / Focus / Pressed — FAB, Icon button, Chip, Segmented button(s). Dragged — Chip, Card.

### 6. Color role mapping
The state layer is an overlay with a fixed opacity per state and **uses the same color as the content**. By default a component's state layer color is derived from the color of its content — the color of an **icon**, or **label text if no icon is present**.

An **on color** is a color role used by the content; each container color has its own corresponding on color.

| Enabled container color | Content color | State layer overlay color |
|---|---|---|
| **secondary container** | **on secondary container** | **on secondary container** |
| **surface** | **primary** | **primary** |

### 9. Do / Don't
- Do apply states consistently across components.
- Do add a state layer to move from enabled to any stateful style.
- Do let only the individual actionable components inside an app bar inherit hover / focus / pressed states — **don't put the whole app bar into a state** (shown as an error for hover, focus, and pressed).
- Don't give components that require consistent placement (e.g. an app bar) a dragged state.
- **If the action represented in the FAB is unavailable, the FAB shouldn't appear** — don't show a disabled FAB.
- Don't apply more than one state layer to an element at a time.
- Don't apply more than one hover / focus / pressed / dragged state in a layout at a time.
- Keep dragged states low-emphasis.

### 10. Accessibility
- States have **two visual indicators** to ensure accessibility.
- **Interactive target size 48dp** (state layer 40dp).
- **Disabled states don't need to meet Material's contrast requirements.**
- Keyboard focus indicator: a **ring-like** indicator on the focused element so keyboard/Tab users know where they are on the page.
- Enabled/focused/pressed buttons have **strong contrast between container and text**; disabled has low-contrast grey text on grey container.

---

## Gestures

### 1. What it is + when to use vs. siblings
Gestures are all the ways people interact with UI elements using **touch**. They help people **navigate, take action, or transform content**. **Tap, scroll, and swipe** are the common gestures.

### 2. Anatomy / types — discriminating rule per gesture

| Gesture | Definition / discriminating rule | Canonical example |
|---|---|---|
| **Tap** | Navigate to destinations and interact with elements through touch | Tapping a card opens an article |
| **Double tap** | Two quick taps to **zoom in and out** of content | Double tapping a photo opens it full screen |
| **Long press** | Access **additional functionality** by pressing an element for an extended time | Long pressing a list item selects it (reveals a selection checkmark + container color change) |
| **Scroll and pan** | Slide surfaces vertically, horizontally, or in **any direction** to move through content | Vertical scrolling reveals more content |
| **Swipe** | Navigate **horizontally** to (a) switch between peer views like tabs, (b) complete actions | Swiping a list item reveals additional actions (swipe right on an email reveals a favorites icon) |
| **Predictive back** | **Android only.** Swipe left or right on certain components to navigate to a previous destination | Predictive back swipe on a bottom sheet goes back to the previous screen |
| **Drag** | Move elements around and slide surfaces in and out of view | A list can be reordered by dragging a list item |
| **Pick up and move** | A **long press and drag** to reorder content | A calendar event picked up and moved to a new time |
| **Pinch** | Scale surfaces to navigate between screens | Pinch outward → photo full screen; pinch inward → collapse |
| **Compound gestures** | Users fluidly transition between gestures | Pan + pinch in a map view |

### 4. Placement / applicability
**Predictive back compatible components (exactly 5):** Bottom sheet, Navigation bar, Navigation rail, Search bar, Side sheet.

No other placement rules appear on the Gestures page. Resource on this page: Design Kit (Figma) at `goo.gle/m3-design-kit` — status **Available**. No M3 Expressive section.

### 5. Behavior
- **UI elements should respond to gestures in real time.**
- Predictive back: **before completing the swipe, the person can decide to continue to the previous view or stay in the current view.**

### 9. Do / Don't
- Do make UI elements respond to gestures in real time.
- Do reserve long-press for additional functionality / selection.
- (See Selection) Don't use long press + drag for batch selection if that combination is already used to pick up and move items.

---

## Inputs

### 1. What it is + when to use vs. siblings
Inputs are **devices that provide interactive control of an app** — commonly a mouse, keyboard, or touchpad. Key takeaways: **design for touch, keyboard, and mouse interactions**; **embrace multiple input methods and gestures within your app**.

External inputs (mouse, keyboard, stylus) can be used with **phone, tablet, foldable, TV, laptop, or desktop computer**. When someone connects an external input, they expect it to behave in familiar and useful ways. Designing for different input methods makes a product more usable and accessible **on all screen sizes**.

Intent: designing for inputs lets people **use the inputs they prefer** — e.g. a mouse to highlight text on a tablet. **A mouse may be connected to tablets, laptops, phones, foldables, and more.**

### 2. Anatomy — common features of external inputs

| Device | Common features |
|---|---|
| **Mouse** | Left and right click; Mouse wheel; Extra buttons |
| **Trackpad** | Left and right click; Gestures; Haptics |
| **Physical keyboard** | Replaces virtual keyboard; Media keys; Modifier keys |

### 5. States and interaction behavior

#### Input device action → anticipated behavior

Framing: **depending on the input device, designers and developers can implement behaviors that meet standard conventions and user expectations.**

| Input device action | Anticipated behavior |
|---|---|
| Mouse and trackpad movement | Show a mouse cursor on the screen |
| Primary click | Treat mouse clicks differently than touch events |
| Secondary click | Activate context menus |
| Hover | Change component states |
| Highlight | Allow text to be selected by the mouse cursor |
| Mouse wheel and trackpad two finger drag | Scroll list vertically and horizontally |
| Trackpad pinch | Zoom an element or page |
| Physical keyboard | Hide and show on screen keyboard |

#### Mouse and cursor
- When an external mouse input device is used, **a mouse cursor should be shown, regardless of the device type**.
- On some devices it's possible to use an external input device **simultaneously with touch input**.
- On devices that **don't specifically recognize mouse or stylus input, the mouse is treated as touch input**.
- **Primary click:** a mouse click or stylus tap should demonstrate the **same feedback as touch input** — e.g. showing the **ripple for a pressed state**.
- **Secondary click:** a secondary click (single button, or two fingers on a trackpad) should **activate a context menu** showing additional options for the object clicked. Canonical example options on a link: *Open link in new window, Save link as, Copy link location, Inspect*. See **menus** for further usage and guidelines.
- **Hover:** when the mouse rests on an interactive element, the hover state is a valuable cue for interaction; enable visual changes to help users discover interactive objects. Hovering with a cursor (or stylus) should **also invoke tooltips** when applicable. (Cross-refs: **states** for hover styles/guidelines, **tooltips** for tooltip guidance.)

#### Cursor variants (4 named)

**Cursors appear when using external input devices like a mouse or trackpad, and the cursor can change to communicate more information about interactive elements.**

| Cursor | Use |
|---|---|
| **Pointer** | Default rendering for external input control |
| **Hand** | Links or linked / clickable images |
| **Resize arrows** | On the boundaries of resizable elements |
| **I-beam** | When hovering on text (selectable text) |

I-beam editable-text interactions:
- **Single click** places the cursor
- **Double click** selects a word
- **Triple click** selects a paragraph
- **Single click** deselects text and repositions the cursor

#### Stylus input
When using a stylus, **cursors are usually not necessary, unless they communicate tool properties** such as brush size or shape (e.g. a circle cursor indicating the selected stylus tool and size).

#### Text selection
When selecting text using a mouse, trackpad, or stylus:
- **Highlight the selected area using a single color**
- **Don't show touch controls next to the highlighted area**

Text selection with touch control:
- When interacting using **touch, always show touch controls, even if other inputs are connected**.
- When using a **mouse, trackpad, or stylus, show the I-beam and context menu, even if it's a touch device** (use the right-click context menu).

#### Mouse wheel and trackpad gestures
**When an external mouse or touchpad is used, the mouse wheel and trackpad gesture allow more actions.**
- **Vertical scroll:** with the cursor positioned on a list, the mouse wheel and two-finger touchpad gesture should scroll the list vertically. **Only the detail panel under the cursor scrolls.**
- **Touch scroll vs. mouse text selection:** on touch-and-drag, the text area scrolls (dragging upward scrolls the field down); with a mouse, **dragging in a text area selects the text** (text and images).
- **Horizontal scroll:** mouse users should be able to scroll with a mouse wheel to navigate horizontally scrolling fields; trackpad users should be able to scroll using a **two-finger horizontal gesture**. Carousels scroll horizontally via scroll wheel or trackpad.

#### Physical keyboard
When a physical keyboard is connected (externally or built-in laptop), users should be able to **perform any actions the virtual keyboard provides, and more**.
- **Show/hide virtual keyboard:** a virtual keyboard should appear or hide in response to the presence of a physical keyboard. Physical keyboard attached → **hide** the virtual keyboard. Physical keyboard removed → **show** the virtual keyboard.
- **Enter key:** enable it for a common function like **sending a message**.
- **Spacebar control:** enable **Spacebar** (or available media keys) to **play and pause music or video**.
- **Tab focus:** focus on interactive items **must follow a logical order** — on most pages **left to right, top to bottom**. When focused from a keyboard or other input device, the focus state **includes a ring-like keyboard focus indicator**. Focus moves between elements as the user presses **Tab**.
- **Escape key:** expected to **dismiss elements, remove focus, or clear selections**. Specifically:
  - Should dismiss **any visible modal elements like menus, dialogs, or bottom sheets**
  - Should **remove any visible focus indicators and set the focus order to 0**
  - Should **remove the text cursor when typing, but should not remove already-typed text**

### 9. Do / Don't
- Do show a mouse cursor whenever an external mouse is used, on any device type.
- Do treat mouse clicks differently than touch events.
- Do change the cursor to communicate information about interactive elements (pointer / hand / resize arrows / I-beam).
- Do highlight mouse-selected text in a **single color**.
- Don't show touch controls next to a mouse-highlighted area.
- Do always show touch controls for touch interaction, even if other inputs are connected.
- Do hide the virtual keyboard when a physical keyboard is attached; show it when removed.
- Don't break the logical Tab order (left→right, top→bottom on most pages).
- Don't let Escape remove already-typed text (it removes the text cursor only).

### 10. Accessibility
- Designing for different input methods **makes a product more usable and accessible on all screen sizes**.
- Tab order must follow a **logical order**; focus state must include a **visible ring-like keyboard focus indicator**.
- Escape must remove visible focus indicators and set focus order to 0.
- Hover changes help users discover interactive objects; hover should invoke tooltips where applicable.

---

## Selection

### 1. What it is + when to use vs. siblings
Selection is **how people interact with UI elements or choose which items to act on**. Key takeaways:
- Selection is shown through **changes to surface color or other visible elements**
- **An entire component can be selected, or just certain parts in a component**
- Selection can be performed via **tap, cursor, keyboard, or voice**

Discriminating rule vs. the active-indicator pattern: ordinary selection can be multi-select and uses check mark / checkbox / surface color; **active indicator** components mark the currently selected destination and **only one item should be selected at a time**.

### 2. Anatomy — selection indicators
Selections are displayed using: a **check mark icon**, a **checkbox component**, a **change in surface color**, or a **combination**.

Resource on this page: Design Kit (Figma) at `goo.gle/m3-design-kit` — status **Available**. No M3 Expressive section on the Selection page.

### 4. Placement / component applicability

Selection is inherited by (12 components): **Cards, Checkboxes, Chips, Data tables, Icon buttons, List items, Menu items, Pickers, Radio buttons, Segmented buttons, Sliders, Switch.**

Components that use an **active indicator** to represent which item is currently selected (4): **Navigation bar, Navigation drawer, Navigation rail, Tabs.** The **color and shape of the active indicator varies between components**; in these components **only one item should be selected at a time**.

Illustrated selected components: Segmented buttons, Chips, List items, Checkboxes, Radio buttons, Switch, Slider (7 types).

### 5. States and interaction behavior — types of selection

**Touch.** On touch devices, select items using:
- **Long press touch or two-finger touch**
- **Selection shortcut, if available**, such as tapping an avatar

**Entering and exiting selection mode.**
- To select an item and **enter selection mode**: long press the item, or use a shortcut such as tapping the item's avatar. To select additional items, **tap each of them**.
- To **exit selection mode**: tap each selected item until they're unselected, or **tap an action on the toolbar**.

**Larger selections (batch).** To select multiple items simultaneously, **long press and drag across items**. **Don't use this gesture combination if it is already in use to pick up and move items, like cards.**

**Click (desktop).**
- When **selection is the primary activity**, checkboxes are **always visible**.
- When **selection is secondary**, checkboxes (or other indicators) are displayed: **as a single checkbox for that item on hover**, and **for all items after one item is selected**.
- To make a selection, **hover over an item to reveal a checkbox, then click it**.
- Canonical example: in a **data table**, checkboxes are **visible by default** because selection is a primary activity there.

Selection can be **combined with other states** (e.g. a selected filter chip also in hover state; a selected filter chip also in focus state — from States).

### 6. Color role mapping
Selection is shown through **changes to surface color**; long press on a list item reveals a **selection checkmark and a container color change**. (Specific `md.sys.color.*` roles are not named on this page.)

### 9. Do / Don't
- Do make checkboxes always visible on desktop when selection is the primary activity.
- Do reveal a checkbox on hover when selection is secondary, and show checkboxes for all items once one item is selected.
- Do allow only **one** item selected at a time in Navigation bar / drawer / rail and Tabs.
- **Don't** use long press + drag for batch selection when that combination already picks up and moves components like cards.

---

## Usability

### 1. What it is + when to use vs. siblings
Usability **focuses on making products intuitive and easy to understand for everyone**.
- **Accessibility** focuses on making products accessible for **people with disabilities**; accessible experiences are **perceivable, operable, understandable and robust**, and support people who use assistive technology.
- **Usability** focuses on making products **intuitive and easy to understand for everyone**.

Key takeaways:
- **Emphasize key actions to create effective visual hierarchy**
- **Leverage expressive design tactics to improve usability**
- **Don't overwhelm the user with too much visual information**
- **Test and iterate to validate designs**

Framing: **usability helps create digital products that are easy to use and engaging.** By leveraging M3 Expressive design tactics like **containment, size, shape, color, and typography**, designers can guide users through experiences and emphasize key actions to create intuitive, usable products. (On this page the "expressive design tactics" links all point to the M3 Expressive blog's **"What's in the update"** section, which is the canonical list — not restated on this page.)

Nielsen Norman Group's five aspects of usability:

| Aspect | Definition |
|---|---|
| Efficiency | Users can efficiently complete tasks and goals |
| Errors | Proper design reduces the likelihood of mistakes, and users can easily correct any errors that do occur |
| Learnability | New users learn to use the product and complete tasks easily, even if it's the first time they're using it |
| Memorability | When users come back to a product, they remember how to use it |
| Satisfaction | Users are satisfied with the designed experience |

### 2. Anatomy — usability design tactics
Named tactics: **containment, size, shape, color, typography** (plus spacing, placement, motion, shape morph). Not all design tactics need to be combined at the same time. An effective combination can: make a product easily understood, learnable, and memorable; help people quickly identify what to do next; minimize distractions to focus on the task.

Method: **start by creating a strong visual hierarchy** to emphasize important information using color, size, spacing, placement, containment; **then add unique emphasis to celebrate success or progress** by adding illustrations, scale, shapes, and shape morph.

| Tactic | Guidance |
|---|---|
| **Color & color contrast** | Use eye-catching **primary and secondary** colors to create hierarchy and emphasize key actions. Instead of similar colors, try **contrasting colors, like purple and green**. Colors should always follow basic accessibility guidelines. Material's dynamic **color roles** automatically create palettes with proper emphasis and accessible contrast ratios. |
| **Containment & grouping content** | Group related elements in **subtle containers**. Break content into manageable sections using containment, **spacing**, and **headings**. |
| **Motion** | Emphasizes key moments or unique experiences; **use it sparingly since motion can be distracting**. |
| **Shape & shape morph** | The **Material shape library has 35 shapes**. Shapes are often used to **mask imagery or fill empty space**. Shape: adds emphasis and delight; guides focus; differentiates containers, buttons and animations; signals interaction; sets emotional tone. **Every shape can morph into another in the set.** Shape morph is also applied when interacting with components like **buttons**. Shape morph: communicates interaction states, like **selected, tap, swipe, scroll, release, long press**; emphasizes actions in progress. |
| **Size** | Size and scale show level of importance. **The most important action or main CTA should be the largest element.** Using larger sizes for key actions **dramatically increases usability** and makes products more efficient — users are satisfied, make fewer errors, and find products more learnable. |
| **Typography** | Type can separate hierarchies of information. More important information might use one font, less important/supplemental another. **The largest, most legible text on the screen could signal a primary action**; **smaller text signals secondary or tertiary action**; **group similar content by using the same font style**. |

Cross-refs cited by the tactics section (details live on other pages, not here): Color system & **color contrast**, **spacing** (grids-spacing), **shape** overview-principles & **shape morph**, **typography** overview, **motion** how-it-works.

### 4. Placement
- Place the primary action **close to the bottom so it's easy to reach** when holding a phone; make it the **final, most prominent element in the vertical flow**, naturally guiding the eye down the screen without competing with other content.
- Supporting/less-emphasized content (e.g. a daily message) can go **at the top** in a soft container with medium-sized text.
- Secondary controls (pause/stop) go **at the bottom, spaced away from** the hero element, but easy to reach.
- **The navigation bar hides during** the breathing (hero) journey.
- Center the final action (**Finish**) at the bottom so it's easy to reach.
- Spread metrics across the screen in a **loose cluster**, guiding the user from one to the next; use **ample spacing around each metric** and **equal vertical spacing between elements** for scannability.

### 5. Interaction / motion behavior
- Shape morph communicates interaction states (**selected, tap, swipe, scroll, release, long press**) and emphasizes actions in progress.
- Hero motion example: the flower expands and contracts to guide the pace of the breath; **the motion uses Material Spring Motion Tokens**.

### 6. Color role mapping
- Use **Material primary color roles** for the prominent primary action (dark purple button on soft light purple background) to create high contrast.
- Data uses the **primary** role to be darker than all other elements and draw attention.
- Yellow accents on the daily goal bar and calendar use the **secondary** roles to highlight progress.
- Selected settings use the **secondary** color; dates use the **secondary container** color, contrasting with the background and primary colors.
- **Anti-pattern:** using the **same** color roles — primary (1, 2) and primary container (3) — for **all** actions and data.
- Supportive, non-required elements use **lighter colors and subtle containers**.

### 7. Typography role mapping
- Referenced style family: **Emphasized typography** (type-scale-tokens). No individual type-scale token names are given on this page.
- Primary action button uses **larger text** to emphasize the primary action.
- Countdown numbers are **very large** compared with the **inhale / hold / exhale** text, providing strong visual contrast while keeping instructions associated with the countdown.
- Key numbers (e.g. **18**, **3min**) are larger and use **emphasized styles**.
- Key statistics (days, breaths, minutes) use **custom-scaled numbers** — large enough to scan but not dominating the screen.
- Supporting daily message uses **medium sized text**.

### 8. Applying M3 Expressive — "Aura" case study (complete)

**Research basis:** Aura is a conceptual breathing app illustrating how **Material 3 (M3) Expressive design tactics** make an app more usable and draw attention to the most important actions. It's used with a **smart watch to measure heart rate**. Created based on the **eye tracking and focus group research** that played a key role in the creation of M3 Expressive. **Research showed that participants were able to spot key UI elements up to four times faster in the M3 Expressive designs compared to other designs.**

**The four goals in the Aura app:** (1) Start a breathing session; (2) Experience and complete a breathing session; (3) View the breathing session results; (4) Check progress towards personal goals.

Examples of what Expressive contributes:
- Using **scale, color, and containment** to guide people to start a breathing session
- Using **shape, color, and empty space** to guide people to breathe slowly and with intention
- **Minimizing cognitive load** by using empty space and fewer actions, so people can stay focused on their breath
- **Balancing primary tasks with supportive data** to show progress and impact of a session

**Design based on primary goals.** Primary goals are the main tasks to use a product successfully (starting a process, making decisions) so they need the **strongest emphasis**. Secondary and tertiary goals add to the experience but aren't required (viewing statuses or settings). Identify primary/secondary/tertiary goals by considering product needs and user satisfaction. To guide people to the primary goal while keeping other goals discoverable:
- Create a **strong visual hierarchy** with size, color, and other design tactics
- **Simplify to one primary task on each page**, leveraging empty space to focus attention
- Make **core actions recognizable and easily reachable**, e.g. **large buttons for the most frequent actions**
- Design a **harmonious** experience that is aesthetically pleasing and easy to understand
- **Don't use too many expressive tactics at the same time** as they can be distracting

**Example 1 — Start a breathing session.** Primary goal on open. **Size, placement, color, and contrast** guide the user to the **Start breathing** button. The button's **large size and low placement** make it easy to reach when holding a phone. **Settings** use a **secondary color** to draw attention but are less emphasized than the button. The **daily message** is least emphasized but uses **large containment and type** to draw attention. Order of emphasis: (1) Start breathing button → (2) breathing session settings → (3) daily welcome message.

Expressive components used: **Extra large button**, **Button groups**, **Switch**, **Navigation bar**.

| Tactic | Application |
|---|---|
| Color & contrast | Prominent dark purple **Start breathing** button (1) on a soft light purple background uses **Material primary color roles** for high contrast, making the button easy to find and remember |
| Hierarchy | Main goal is to tap the large **Start breathing** button (1); daily message (3) and settings (2) are in lighter colors and subtle containers because they are supportive, not required |
| Placement | Button (1) close to the bottom so it's easy to reach; final, most prominent element in the vertical flow, guiding the eye down the screen without competing with other content |
| Shape | The rounded button form reinforces it as a distinct, touchable control |
| Size | Button (1) is **extra large** to make it the most emphasized element on screen |
| Spacing | Generous spacing separates the button (1) from the message (3) and settings (2) |
| Typography | Button (1) has larger text to emphasize the primary action |
| Visual harmony & hierarchy | Daily message placed at the top in a soft blue container with medium sized text, setting a reflective tone without drawing too much focus; hierarchy guides the user from daily message (3) → settings (2) → **Start breathing** button (1) |

**Example 2 — Breathing session (inhale & exhale).** The guided breathing exercise is the **hero moment**. A **large central flower expands and contracts** as the visual guide for each breath, while a **countdown shows remaining seconds for inhaling, exhaling, and holding the breath**. The **pause** and **stop** buttons are **less prominent than the flower** to encourage focus on the session, and are placed at the bottom so they're easy to reach.

The flower's **shape, size, and movement** together guide the user to inhale, exhale, and hold the breath.

Expressive components and styles used: **Large buttons** in a **button group**; **Material shape library ("flower" and "sunny")**; **Emphasized typography**.

| Tactic | Application |
|---|---|
| Color & contrast | Vibrant **yellow** appears when inhaling to contrast the soft purple background and be obvious |
| Motion | The flower expands and contracts to guide the pace of the breath; motion uses **Material Spring Motion Tokens** |
| Placement | **pause** and **stop** at the bottom, spaced away from the flower but easy to reach; **the navigation bar hides during the breathing journey** |
| Shape | The flower uses the **"flower"** and **"sunny"** Material shapes to draw attention and clearly stand apart from the simple **pause** and **stop** buttons |
| Size | The animating, breathing flower dominates the screen to draw attention |
| Typography | Countdown numbers are **very large** compared with the **inhale / hold / exhale** text to focus attention on the exercise — strong visual contrast while keeping instructions associated with the countdown |

**Example 3 — Breathing report.** Comes after the exercise; it's the **secondary goal**, not the primary hero moment, so it **uses fewer design tactics to reduce cognitive load**. Draws attention to each data point using **shapes and decreasing size**. Its button is **less emphasized than the Start breathing button** on the landing page. Data shown: total breaths taken, exercise duration, heart rate/BPM, breaths per minute.

Expressive components and elements used: **Medium button**, **Material shape library**, **Emphasized typography**.

| Tactic | Application |
|---|---|
| Color & contrast | Dark text on light flower shapes creates strong contrast, making each metric easy to read at a glance; solid dark purple **Finish** button stands out against the light purple background, guiding users to the next step |
| Placement | Metrics spread across the screen in a **loose cluster**, guiding the user from one to the next; **Finish** button **centered at the bottom** so it's easy to reach |
| Shape | Metrics sit inside **Material flower shapes**, making achievements stand out; flower shapes make the design look consistent |
| Size & typography | Key numbers like **18** and **3min** are larger and use **emphasized styles**, making the most important data easy to scan |
| Spacing & grouping | Ample spacing around each metric avoids clutter while keeping the layout tidy and scannable; playful Material shapes serve as clear containers, making the grouping feel lively |

**Example 4 — Check progress.** A **tertiary goal**: track statistics and see progress over a **monthly view**. Not a primary goal or hero moment, so it uses **more subtle design tactics**. Key data is **dark on a light background**; **yellow shapes on the calendar highlight completed sessions**.

Expressive components and elements used: **App bar**, **Progress indicator**, **Medium button**, **Navigation bar**, **Material shape library**, **Emphasized typography**.

| Tactic | Application |
|---|---|
| Color & contrast | Data uses the **primary** role to be darker than all other elements and draw attention; yellow accents on the daily goal bar and calendar use the **secondary** roles to highlight progress |
| Grouping & spacing | Metrics (days, breaths, minutes) grouped together; **equal vertical spacing** between elements makes data easy to scan |
| Shape | The rounded Material **flower** shape on highlighted calendar days makes data more expressive and reminds the user of the breathing exercise visualization |
| Size | **Custom-scaled numbers** for key statistics (days, breaths, minutes) large enough to scan but not dominating the screen |

**Testing & iteration.** **By testing the experience with users, it's easy to identify usability issues and address them.** From **version 1 to version 2** the design shifts from **cluttered to calm and simplified**.
- **Version 1:** no containment, similar sizes, inconsistent colors; settings for duration, sound, and haptics all fighting for attention, creating unnecessary complexity; loosely-grouped settings each with their own styles.
- **Version 2:** settings **neatly grouped as list items above the main action**, an **extra large button**, and **consistent secondary color usage**; focus stays on starting the breathing session.
- By carefully using **hierarchy, containment, shape, and color**, the final design is easier to follow and more intuitive. **Exploring different design refinements can result in an experience that feels intuitive and easy for the user to follow.**

**Best practices for applying usability design tactics**

*Use clear scale and placement* — **Avoid crowding the screen with too many large or equally prominent elements.** Scale and placement create a clear focal point.
- Don't: all elements large and competing for attention; unclear visual hierarchy; settings not grouped together.
- Do: one large primary button as a strong visual focal point; supporting controls clear but less prominent.

*Reinforce with consistent color roles* — **Use different color roles for actions and data** to create a visual hierarchy that makes it simple for users to identify what they can do.
- Don't: the same color roles — primary (1, 2) and primary container (3) — used for all actions and data.
- Do: primary color role (1) makes the button clear and prominent; secondary on selected settings (2) and secondary container on the dates (3) contrast with the background and primary colors.

*Create calm, balanced layouts* — **Use uniform shapes and sizes.** Add space between shapes and data to make it simple to compare data. Create **gentle visual rhythm by aligning elements in a consistent flow** to support a serene, focused experience.
- Don't: shapes with different forms and sizes; **shapes that overlap**.
- Do: more even spacing between shapes; uniform shapes.
- Don't: text shifting from very condensed (inhale) to expanded (exhale) while large arrows animate at the same time as the moving flower.
- Do: keep **text spacing consistent** so the user can focus on the flower's pulsating and morphing shape guiding the pace of breathing.

*Iterate* — **Test, iterate, and gather feedback early and often from a range of users and contexts** to validate design choices and minimize errors. User testing offers valuable insights into how users perceive and interact with the usability of the product experience.

### 9. Do / Don't (imperatives)
- Emphasize key actions to create effective visual hierarchy.
- Make the most important action / main CTA the largest element.
- Use larger sizes for key actions.
- Use contrasting colors (e.g. purple and green), not similar colors.
- Always follow basic accessibility color-contrast guidelines.
- Group related elements in subtle containers; break content into manageable sections with containment, spacing, and headings.
- Use motion sparingly.
- Use different color roles for actions vs. data.
- Use uniform shapes and sizes; don't let shapes overlap.
- Simplify to one primary task per page; leverage empty space.
- Place core actions where they're recognizable and easily reachable.
- Don't overwhelm the user with too much visual information.
- Don't use too many expressive tactics at the same time.
- Don't crowd the screen with too many large or equally prominent elements.
- Test and iterate to validate designs.

### 10. Accessibility
- Accessibility = making products accessible for people with disabilities; accessible experiences are **perceivable, operable, understandable and robust** and support assistive technology users. Usability is distinct: it targets making products intuitive and easy to understand **for everyone**.
- Colors should always follow **basic accessibility guidelines** (color-contrast).
- **Material Design's dynamic color roles automatically create color palettes with proper emphasis and accessible contrast ratios.**
- Reachability: place primary actions low on the screen so they're easy to reach when holding a phone.

---

## Building for all

### 1. What it is
"Building for everyone with everyone." Product teams can't always represent all of their users, but they can better understand different people's experiences and needs by **working with communities, organizations, experts, and researchers**. **Including perspectives of those who are often overlooked leads to building more helpful products for everyone.**

### 2. Anatomy — dimensions of experience
Considering people's attributes and environments helps: ensure you take into account a variety of lived experiences; discover insights into who to collaborate with to gather different perspectives; expand product benefits to more people.

Keep this **evolving list** in mind during research and design, comprehensive testing, and marketing (13 dimensions): **Age, Culture, Disability, Education and literacy, Ethnicity, Gender, Geography and global relevance, Physical attributes, Race, Religion, Sexual orientation, Socioeconomic status, Technology proficiency.**

Page sections: **User needs** (dimensions of experience) and **Co-design** (questions to consider). No M3 Expressive section.

### 5. Process — co-design
Co-design **supports innovation by involving the people who use a product or service in the creation process** and **goes beyond traditional user research**. Prioritize **engaging with people of varied backgrounds and experiences**; building with everyone is an **ongoing process**. By actively engaging with communities that are often overlooked, you build products that are more beneficial for everyone. **Validate your assumptions and discover new opportunities by conducting market research with a broad range of people.**

### 9. Do / Don't — questions to consider
- What are some opportunities to address user needs keeping in mind attributes of people and their contexts? Who else can benefit from the product?
- What are their needs?
- How are you making sure overlooked communities are included in **ongoing** testing?
- How are you engaging community members and experts **early and often** throughout the development process? How will their feedback shape key decisions about feature priorities, functionality, and messaging?
- How can you continue to apply these insights as you move from the ideation phase to other stages of product development?
- What are some opportunities to gain even more insights?
- What are the risks and potential harms if you exclude people from overlooked communities? How can you address them?
- If your tool uses ML or AI, what can you do to **mitigate the risk of bias**? (The page links a collection of people-and-AI research resources for this.)

---

## Gaps (referenced but not valued in these pages)

> **Before treating a measurement here as unavailable:** many of these are published as
> `md.comp.*` values in the generated Compose token files, which are collected in
> [`component-tokens.md`](./component-tokens.md) — container heights and widths, shape
> assignments, elevation levels, icon sizes, and internal spacing. Check there first. Those are the
> Compose token values, so attribute them as such rather than as guideline text.

See `gapsNoted` in the structured output.
