# Layout — M3 reference extract

Sources: foundations_layout_layout-overview.md, foundations_layout_breakpoints.md, foundations_layout_canonical-examples.md, foundations_layout_scaffold.md, foundations_layout_grids-spacing.md, foundations_layout_bidirectionality-rtl.md (m3.material.io, updated 2026-07-17). Material layout guidance is implemented on Android and applies to web.

---

## Layout overview

### 1. What it is + when to use
Layout is the visual and strategic arrangement of elements on a screen. Use it to organize all elements, signal hierarchy, and draw attention to key actions. Adapt layouts to compact, medium, expanded, large, and extra-large breakpoints (previously window size classes). Build from an established canonical layout example. Design for bidirectionality (LTR + RTL). Apply consistent arrangement, sizing, and spacing.

### 2. Anatomy — 7 elements of layout
Column · Fold · Margin · Bar · Drag handle · Pane · Rail.

Glossary (exact definitions):
| Term | Definition |
|---|---|
| Adaptive design | Techniques that allow an interface to dynamically respond to contexts like user preferences, device type, state, and breakpoints |
| Bars | Can frame the page to help people navigate through a product; typically house the app bar and bottom navigation bar |
| Bidirectionality | A writing system that displays text and content from right-to-left (RTL) |
| Breakpoints | Opinionated window sizes where a layout changes to match available space, device conventions, and ergonomics (previously window size classes) |
| Column | One or more vertical blocks of content within a pane |
| Drag handle | The component that resizes panes |
| Fold | A flexible area of the screen or a hinge that separates two displays on foldable devices |
| Gap | The space between components or elements within a container |
| Margin | The space between the edge of the screen and any elements inside of it |
| Multi-window mode | Enables multiple apps to share the same screen simultaneously |
| Pane | A layout container that houses other components and elements within a single app; can be fixed, flexible, floating, or semi-permanent |
| Rails | The perimeter space surrounding panes that holds key elements such as navigation rails, toolbars, and pane control |
| RTL language | Languages written and read right-to-left, such as Arabic, Hebrew, and Farsi, used by over 2 billion people |
| Rulers | An opinionated set of global alignment lines that help organize building blocks in a layout |
| Safety region | Zones reserved for system UI elements outside the application space, such as status bar or gesture bar |
| Scaffold | A fundamental UI design structure that provides a standard platform for assembling key screen components |
| Spacer | The space between two panes on a foldable device |

### 3. Spacing values (layout-level)
| Element | Value |
|---|---|
| Spacer (space between two panes) | 24dp wide |
| Padding (space between UI elements) | measured in increments of 4dp; can be vertical or horizontal; need not span full height/width |
| Margins | fixed or scaling values per window size class; can change at different breakpoints; wider margins for larger screens |

A spacer can contain a drag handle that adjusts the size and layout of the panes; the handle's touch target slightly overlaps the panes.

### 4. Adaptive design vs responsive design
Responsive design scales a single layout to fit any screen; **adaptive design customizes a product to optimize the experience on each device**. Adaptation goes beyond color, typography, and shape — structure, individual components, and entire layouts adapt based on: People (individual preferences and settings), Devices (watch, phone, foldable, tablet, desktop, or XR device), Usage (resizing windows, changing orientation, switching device).

Three primary experience types layouts must adapt across: **mobile**, **desktop**, **spatial**. Start with mobile and scale up to spatial. Build for all inputs — touch, pointer, and physical keyboard — since users may use the product in a desktop environment regardless of device type.

| Experience | Contents / window modes |
|---|---|
| Mobile | Phones, foldables, tablets. Window modes: Full-screen (default for mobile), Split-screen (two or more apps share the screen; common on tablets and foldables), Bubbles (floating windows for multitasking without leaving context) |
| Desktop | Free-form windows that adapt across breakpoints; split screens, floating windows, free-form windows. A tablet converts to a desktop experience with physical keyboard + mouse; Android mobile devices transition to desktop-like when connected to an external monitor |
| Spatial (XR) | Multiple free-form windows within virtually limitless screens. Immersive modes such as Android XR full space allow components positioned freely in 3D space; a navigation rail can become an orbiter and float to the side of the main pane |

Three adaptive strategies for panes: **show and hide**, **levitate**, **reflow**.

Components adapt in **appearance, placement, and behavior** based on factors like: where components are placed in relation to their containers, content, and pane boundaries; how components use space; how components enable usage across different device and input types.

Three component adaptation strategies: **resizing**, **showing & hiding**, **presentation changes**.
- Resizing: buttons may scale with parent container, or hug contents and maintain left/right alignment.
- Showing & hiding: list items may reveal descriptions or additional information as parent container scales.
- Presentation changes: orientation of elements plus changes to color, type, shape; components can change configuration — a FAB can change to an extended FAB when window size increases; navigation rails can be automatically expanded.

### 5. Grouping
Grouping is a method for connecting related elements that share a context, such as an image grouped with a caption. It visually relates elements and establishes boundaries to differentiate unrelated elements. Use spacing to visually tie elements together and establish boundaries between unrelated items.
- **Explicit grouping**: visual boundaries — outlines, dividers, shadows — group related elements in an enclosed area; can also indicate an item is interactive (list items between dividers, a card with image + caption).
- **Implicit grouping**: close proximity and open space (not lines/shadows). E.g. headline + subhead + thumbnail grouped by proximity, separated from other groups by open space; carousel images grouped by proximity.
- On most devices panes can blend in with the background = implicit grouping, showing relationships between panes. In spatial environments, panes use a container color to separate them from the passthrough or virtual environment; use contrast between panes and background to create the spatial effect in XR.

### 6. Do / Don't
- Do use the layout scaffold, start from a canonical layout example, and ensure layouts scale across breakpoints when creating new layouts.
- Do use the grid to group related information in columns, apply spacing consistently, create focal points for primary actions, and align building blocks like bars, rails, and panes.
- Do put all content in a pane.
- Do keep the safety region free of primary content.

### 7. Accessibility
Default target size should be at least 48x48 CSS pixels. Accessible targets retain a minimum of 48x48dp even if the visual element (e.g. an icon) is smaller.

---

## Breakpoints

### 1. What it is + when to use
A breakpoint (previously window size class) is the window size at which a layout needs to change to match available space, device conventions, and ergonomics. Applies to Android and web. There are **five** main breakpoints. Rather than designing for an ever-increasing number of display states, focusing on breakpoints ensures layouts work across a wide range of devices. When moving across breakpoints, decide which elements to **reveal, divide, resize, reposition, or swap**. Layouts typically transition from a single pane to two or three panes as window size increases. Design for breakpoints instead of specific devices because (a) available window space is dynamic and changes with user behavior such as multi-window modes or unfolding a foldable, and (b) devices fall into different breakpoints based on orientation.

### 2. The five breakpoints
| Breakpoint | Width (dp) | Common devices |
|---|---|---|
| Compact | Under 600dp | Phone in portrait |
| Medium | 600–839dp | Tablet in portrait; Foldable in portrait (unfolded) |
| Expanded | 840–1199dp | Phone in landscape; Tablet in landscape; Foldable in landscape (unfolded); Desktop |
| Large | 1200–1599dp | Desktop |
| Extra-large | 1600dp+ | Desktop; Ultra-wide monitors |

Large and extra-large are used on devices like laptops, desktops, and external monitors; they are most useful for web experiences tailored to laptop and desktop. Some products may not need large and extra-large breakpoints — consider your platform's conventions and users when deciding which breakpoints to design for.

**Height breakpoints**: on Android, compact, medium, and expanded breakpoints are also available for height, to adjust layout when available vertical space is unusually small or large. Since most layouts contain vertically scrolling content, it's rare that layouts need to adjust to available height.

### 3. Per-breakpoint component recommendations
| Breakpoint | Panes | Navigation | Communication | Action |
|---|---|---|---|---|
| Compact | 1 | Navigation bar, modal expanded navigation rail | Simple dialog; Full-screen dialog | Bottom sheet |
| Medium | 1 (recommended) or 2 | Navigation bar, modal expanded navigation rail | Simple dialog | Menu |
| Expanded | 1 or 2 (recommended) | Modal or standard expanded navigation rail | Simple dialog | Menu |
| Large | 1 or 2 (recommended) | Modal or standard expanded navigation rail | Simple dialog | Menu |
| Extra-large | 1 to 3 (recommended) | Modal or standard expanded navigation rail | Simple dialog | Menu |

### 4. Per-breakpoint spacing and pane widths
| Breakpoint | Leading/trailing margin | Spacer between panes | Fixed pane default width |
|---|---|---|---|
| Compact | 16dp | — | — |
| Medium | 24dp | 24dp | — (two panes each 50% of window width) |
| Expanded | 24dp | 24dp | 360dp |
| Large | 24dp | 24dp | 412dp |
| Extra-large | 24dp | 24dp | 412dp (side-sheet third pane default max width 400dp) |

### 5. The five adaptation questions (design one breakpoint, then adjust)
1. **What should be revealed?** UI hidden on smaller devices can be revealed in larger layouts — e.g. on mobile the navigation rail is collapsed by default; on an expanded device it can be open by default, revealing more actions and features. Same for panes: larger layouts can show an inbox pane and a selected-conversation pane simultaneously. Additional space doesn't just mean making the same thing bigger.
2. **How should a screen be divided?** Compact and medium: a single pane works best. Expanded and large: two panes recommended. Extra-large: consider three panes. At medium, two panes are useful only for low-density content with clear actions (e.g. a settings view). Rotating a device often changes the breakpoint — a layout can have two panes in landscape and one in portrait. Single-pane layouts focus attention for playing a game, watching a movie, video calls, creative applications.
3. **What should be resized?** UI elements that are small on compact screens can grow as breakpoints increase; panes can also expand to rearrange elements and make better use of space. Consider resizing cards, feeds, lists, panes. Resizing can highlight imagery and improve text readability; this type of adaptation affects the scale of content and the relationship between objects on screen. A vertical card on mobile can adjust its margins, orientation, text size, and density to fit a tablet. **Across all breakpoints, adjust margins and type styles to keep text between 40–60 characters per line.**
4. **What should be repositioned?** Reflow/reposition to use additional space and match ergonomic and input needs (similar to responsive design on the web) — e.g. shift actions from the bottom of a compact window to the leading edge of medium and expanded windows. Consider: repositioning cards, adding a second column of content, creating a more complex layout of photos, introducing more negative space, ensuring reachability for navigation and interactive elements. Internal elements can be anchored left, right, or center as a parent container scales, or maintain fixed positions (e.g. a FAB in a navigation rail). Tabs can remain anchored to the middle at both compact and medium. A button's icon and text label remain anchored to each other, staying centered as the container scales horizontally.
5. **What should be swapped?** Components with similar functions can be exchanged — e.g. a bottom navigation bar at compact swaps to a navigation rail at medium; a navigation rail swaps from collapsed to expanded at larger breakpoints. Ensure interchangeable components are functionally equivalent and the swap serves a functional and ergonomic purpose.

Common swappable components:
| Component type | Compact | Medium | Expanded |
|---|---|---|---|
| Navigation | Navigation bar | Collapsed navigation rail | Collapsed navigation rail |
| Navigation | Modal expanded navigation rail | Modal expanded navigation rail | Standard expanded navigation rail |
| Communication | Basic or full-screen dialog | Basic dialog | Basic dialog |
| Supplemental selection | Bottom sheet | Menu | Menu |

### 6. Per-breakpoint placement rules

**Compact (<600dp)** — focuses on a single view.
- Navigation: navigation bar or modal expanded navigation rail; place navigation components close to the edge of the screen where they're easier to reach (near the bottom of the window).
- Panes: single pane.
- Spacing: margins 16dp from leading and trailing edge.
- Must transition dynamically to medium or expanded when: a foldable is unfolded; a mobile device is rotated portrait→landscape; a tablet exits split-screen; a product is resized larger in multi-window mode; a free-form window is resized.

**Medium (600–839dp)**
- Navigation: single-pane layouts → navigation rail; two-pane layouts → navigation bar (lets panes fully use the available window width). The navigation rail can be hidden in secondary destinations as long as the primary destination is still reachable via a back button.
- Panes: single pane recommended because of limited screen width. Two panes only for lower information density (e.g. settings). Each pane in a two-pane layout takes 50% of window width; avoid custom widths. A drag handle can expand/collapse panes to 100% of window width.
- Spacing: margins 24dp; spacer between panes 24dp.
- Transitions to compact or expanded when: a foldable is folded; a tablet rotated portrait→landscape; product goes full-screen→split-screen; multi-window mode initiated; a free-form window is resized.
- **Reachability**: for horizontal tablets and unfolded foldables the top 25% of the screen is likely out of reach unless the grip is adjusted — limit interactions placed in the upper 25%. Avoid placing essential interactive elements too close to the bottom edge — some people, particularly those with larger hands, might struggle to reach it. Three ergonomic regions: *Inconvenient* (reachable by extending fingers), *Comfortable*, *Challenging* (hard to reach while holding the device).

**Expanded (840–1199dp)**
- Navigation: navigation rail, collapsed or expanded, close to window edges. Rail can be hidden in secondary destinations if the primary destination is reachable via back. For sorting, filtering, or secondary navigation use tabs or other components directly in the pane.
- Panes: single- or two-pane; two-pane is often best. Single-pane works for visually- or information-dense content such as videos. Fixed-and-flexible: fixed pane 360dp by default. Split-pane: two flexible panes, spacer visually centered by default — the navigation and first pane together are 50% of window width so the spacer stays visually centered.
- Spacing: leading and trailing margin 24dp; spacer 24dp.
- Transitions to compact or medium when: a foldable is folded; tablet rotated landscape→portrait; full-screen→split-screen; multi-window initiated; free-form window resized.

**Large (1200–1599dp) & Extra-large (1600dp+)**
- Navigation: navigation rail, collapsed or expanded depending on amount of content. An expanded navigation rail is best suited for extra-large windows. Consider collapsing the rail when space is needed or on pages deeper in the hierarchy. Use tabs or in-pane components for sorting, filtering, secondary navigation.
- Panes: two-pane often best; single-pane only for dense content or media. Fixed-and-flexible: fixed pane 412dp by default. Split-pane: spacer visually centered by default even with an expanded navigation rail — navigation components shrink the leading pane so the spacer stays centered.
- Additional panes: the extra-large breakpoint supports a **standard side sheet as a third pane**. With the side sheet present the navigation rail can remain visible, collapse, or hide completely. **Don't use more than three panes.** Fixed panes at this size are recommended to be 412dp, but side sheets have a default maximum width of 400dp.
- Spacing: leading and trailing margin 24dp; spacer 24dp.
- Transitions to a smaller layout when: full-screen→split-screen; multi-window initiated; free-form window resized. Pay attention to typographic elements such as line length to ensure readability.

### 7. Do / Don't
- Do give each product view a layout for the breakpoints most appropriate for your platform and users.
- Do use different components for the same function across the five layouts.
- Don't use two panes in medium layouts with high information density — it reduces usability.
- Don't set custom pane widths at medium (use 50%/50%).
- Don't swap a button for a chip. Be careful when changing between list items and cards. Don't arbitrarily swap components that aren't functionally equivalent (e.g. a button for a menu).
- Don't use more than three panes.

---

## Layout scaffold

### 1. What it is
A fundamental UI design structure providing a standard platform for assembling key components. The scaffold structures every piece of an adaptive layout into **bars, rails, and panes**. Introduced May 2026 to create adaptive layouts efficiently. Canonical layout examples demonstrate how to implement it.

Role of each region (scaffold overview):
- **Bars** can frame the page to help people navigate through a product.
- **Rails** create the perimeter space surrounding panes, creating space for elements like navigation and toolbars.
- **Panes** hold a product's primary content, adapting to breakpoints (previously window size classes) and other conditions.

### 2. Anatomy
Safety region · Bar · Pane · Rail. (Diagrams cover mobile and desktop layouts.)

**Region color roles** (from `../color.md`): the pane/body region uses **`surface`** and the
navigation region uses **`surface container`**. These mappings must stay the same for a region across
every breakpoint — the body is `surface` on both phone and tablet. At larger breakpoints you may add
other `surface container` levels for hierarchy, as long as they are applied consistently.

### 3. Placement order
Populate regions of the scaffold closest to the edges of the screen's usable space first — bars (navigation bar and rail) and components like toolbars and app bars — then populate the main region with panes containing content and components based on available space and structure.

---

## Bars (scaffold region)

### 1. What it is + when to use
Bars frame the screen to help people navigate through a product. Use bars to frame the main content, contain an app bar or navigation bar, and span one or multiple panes. Bars can span a single pane or the full width of a window.

### 2. Anatomy / contents
- **App bar**: placed at the **top** of the screen, outside of the safety region; provides a title (a description of the screen) and **1–2 essential actions** like search or back navigation.
- **Navigation bar**: occupies the bottom bar region on mobile; sits at the **bottom** of the screen, above the safety region; lets people switch between **3–5 primary UI views** at compact or medium breakpoints.
- On the web, an app bar occupies the top bar region.

### 3. Placement
Bars are placed adjacent to the safety regions, which contain system UI elements. Safety regions sit at the top and bottom edges of the screen on compact devices and protect system UI elements.

### 4. Do / Don't
- Don't place primary content in the safety region.

---

## Rails (scaffold region)

### 1. What it is + when to use
Rails are the next level in layout after bars, filling the perimeter space surrounding panes, or floating above them. They occupy the spaces immediately adjacent to bars.

### 2. Contents
Navigation rails, toolbars, chat inputs, FABs, and other primary controls / pane control.

### 3. Placement per screen size
- **Compact screens**: top and bottom rail regions can hold toolbars, chat inputs, FABs, and other primary controls related to an individual screen. A toolbar can float in the rail region and sits above the navigation bar.
- **Larger screens**: rails exist on the sides as well as top and bottom. The **leading side rail region commonly holds the navigation rail** (expanded navigation rail at larger breakpoints). The **trailing side rail region** can hold supporting controls or actions that modify or relate to the content in a pane — e.g. a vertical toolbar, or a companion rail.
- **XR**: rail components can become **orbiters**, which float outside the visible content area; in full space an XR navigation rail can float outside the main content as an orbiter.

---

## Panes

### 1. What it is + when to use
A pane is a layout container that houses other components and elements within a single app; it is a single destination in the product (e.g. in a messaging app, the message list is one pane and a conversation thread is another). **All content must be in a pane.** All layouts are made up of **1–3 visible panes**; the type of layout and number of panes depends on the breakpoint and the type of product. People can navigate to or between panes; presenting multiple panes at once can make a product more efficient and easier to use. Panes adapt dynamically to the breakpoint and the person's language setting — for RTL languages navigation components will be on the right.

### 2. Pane types
- **Fixed**: width doesn't change based on available space.
- **Flexible**: width changes based on available space; can grow and shrink.
- **All layouts need at least one flexible pane.**
- Panes can be **permanent** or **temporary**; temporary panes can appear and be dismissed when necessary, affecting the layout and size of other panes.
- A pane can be fixed, flexible, floating, or semi-permanent.

### 3. Pane count per breakpoint
| Breakpoint | Recommended pane total | Other pane totals |
|---|---|---|
| Compact | 1 | -- |
| Medium | 1 | 2 |
| Expanded | 2 | 1 |
| Large | 2 | 1 |
| Extra-large | 2 | 1, 3 |

### 4. Configurations
- **Single-pane layout**: one flexible pane extending to fit the available space in a layout's width. Usable at any breakpoint, recommended for compact and medium.
- **Two-pane — Split-pane layout**: keeps the spacer visually centered; best for foldable devices and dynamic layouts. When a navigation rail or drawer is present it only reduces the size of one pane; the other pane remains at 50% of window width. With a navigation bar, or no navigation, both panes span 50% of window width by default.
- **Two-pane — Fixed-and-flexible layout**: common for expanded, large, and extra-large breakpoints. Fixed and flexible panes can appear in whichever order is best for the content. The fixed pane is often temporary and used for side sheets or lists with light information density. Fixed pane default: 360dp (expanded), 412dp (large & extra-large).
- **Three-pane layout**: less common; extra-large breakpoint supports a standard side sheet as a third pane. With the side sheet present the expanded navigation rail can remain visible, change into a collapsed navigation rail, or hide completely. Fixed panes at this breakpoint are recommended to be 412dp, but side sheets have a default maximum width of 400dp.

### 5. Displaying multiple panes (three arrangements)
- **Co-planar**: two side-by-side panes. To stay accessible, persistent utilities like tool panels should be co-planar with primary content.
- **Floating**: a small pane displayed above larger panes/content, like a dialog. Temporary tasks should remain floating regardless of breakpoint.
- **Docked**: a small pane pinned to the edge of a window, with one edge extending beyond one side of the screen — e.g. a bottom sheet docked to show additional actions.

### 6. Adaptive strategies
- **Show and hide**: as breakpoint size or orientation changes, panes can enter and exit the screen or appear next to one another.
- **Levitate**: panes elevated above other content as floating or docked panes; helps panes appear relative to their triggers. Floating panes appear in front of the body content and can be customized to be dragged or resized. On large screens, floating panes are the default and the scrim behind a floating pane is optional. Docked panes are usually at the bottom of the window, like a bottom sheet; at medium and expanded breakpoints docked panes can adapt into floating panes, or into co-planar panes. On large screens, consider changing docked panes into co-planar panes.
- **Reflow**: panes reorganize as breakpoint or orientation changes. In a vertical orientation the supporting pane can move underneath the primary pane. When there's not enough horizontal space, panes can stack vertically.

### 7. Containment
On most devices panes can blend in with the background (implicit grouping) to show relationships between panes. Explicit grouping uses distinct colors or outlines to visually delineate content. In multiple-pane layouts, use color to show emphasis and close spacing to group related content. In spatial environments panes use a container color to separate them from the passthrough or virtual environment.

### 8. Spatial panels (XR)
Pane layouts can be presented in disconnected spatial panels. Panels **must have clear containment** to be easy to see on any background. Content in a spatial panel can use implicit grouping when the pane has an explicit container distinguishing it from the environment.

### 9. Scrolling
A single pane can scroll its inside content vertically and horizontally. With multiple panes, each pane can operate as an independently scrollable area. Depending on how a product uses panes, the scroll behavior of a folded design may change in the unfolded design. If you expand a pane, decide whether the whole window scrolls together or each pane scrolls independently.

### 10. Accessibility
- **Co-planar panes**: focus order must match the visual arrangement of the panes on screen.
- **Modal floating pane**: elements behind it can't be interacted with; focus moves automatically to the first element in the pane, and on close focus returns to the triggering element (like a dialog); if triggered automatically, focus should still move to it but on close focus should go to the next most logical element on screen; it disappears when a person interacts with something behind it.
- **Non-modal floating pane**: other parts of the product can be interacted with while open; focus must be able to move to and from the pane; the pane must be available in a logical reading order of the screen.
- **Docked panes**: same focus requirements as modal and non-modal panes; focus order must match the visual arrangement on screen.
- When adding controls that resize or move a floating pane, provide accessible controls.

---

## Drag handles & pane resizing

### 1. What it is
The drag handle is the component that resizes panes. A spacer can contain a drag handle that adjusts the size and layout of the panes.

### 2. Behavior
- Adjust the width of flexible panes.
- Fully collapse and expand fixed panes to quickly switch between a single- and two-pane layout.
- In a **split-pane layout**, both flexible panes can be freely adjusted, or can snap to certain widths.
- In a **fixed-and-flexible layout**, the drag handle can fully collapse and expand the fixed pane.
- The drag handle should also **toggle between layout sizes when selected** — this can be a tap, double tap, or long press.
- At medium breakpoints, a drag handle can expand or collapse panes to 100% of window width.

### 3. Snap widths (expanded, large, extra-large)
Two-pane layouts can be customized to snap to set widths when resized. Recommended custom widths: **360dp**, **412dp**, and **split-pane with spacer centered visually**. Panes can snap to these custom widths when releasing the drag handle. (The source does not say panes snap to the *closest* width — "adjusts to the closest snap point" is stated only for the multi-window screen handle.)

### 4. Persistence
- **Persistent pane resizing**: remembers the person's pane width preference; use for most resizable layouts. Widths persist after the app is closed, and persist across a breakpoint change — a two-pane layout collapsed to one pane at any size remains collapsed even when changing breakpoints.
- **Temporary pane resizing**: doesn't remember preferences; primarily used in supporting pane layouts where resizing is uncommon. Panes always return to the default layout after the pane or product is closed and reopened.

### 5. Touch target
The handle's touch target slightly overlaps the panes.

---

## Grids

### 1. What it is + when to use
The layout grid is the foundation for every layout, providing a structural framework for organizing components, content, and actions. Layouts in Material are based on a grid that adapts across all breakpoints. Parts of the layout scaffold like rails and panes are positioned on this grid to create consistent adaptive layouts. The structure and spacing values used in a grid can add personality to a product's layout.

Use the grid to: group related information in columns; apply spacing consistently; create focal points for primary actions; align building blocks like bars, rails, and panes.

### 2. Behavior across breakpoints
Column count, width, and spacing dynamically adjust to different breakpoints. As size increases, column count may increase to show more content or controls. On compact screens fewer columns create a focused layout; as screen size increases (e.g. unfolding a foldable) additional columns allow a richer layout.

### 3. Workflow
1. Start with placing grid columns.
2. Place bars & rails — populate scaffold regions closest to the edges of usable space first (navigation bar and rail; toolbars and app bars).
3. Place panes — populate the main region with panes containing content and components, based on available space and structure. See canonical layout examples for which panes suit a product.

---

## Rulers & alignment

### 1. What it is + when to use
Rulers are a set of recommended **global alignment lines** that help create consistent focal points, keep content and components consistently aligned across all layers of the layout, and keep margins and placement consistent across a product.

### 2. Ruler types
| Ruler | Purpose |
|---|---|
| Margin | Defines margin; comes with wiggle room to determine how tight or loose content feels; the standard ruler can be adjusted to the left or right |
| Bar & safety | Reserve space for system UI elements like the status bar and gesture navigation; ensure actionable content like app bars isn't covered by system UI; align to the edges of a screen's usable space |
| Title | Creates consistency for the screen's title, aligning the text, icons, and other components in an app bar |
| Content (first) | Emphasizes major blocks like hero images, headlines, or primary components |
| Content (secondary) | Determine where supplementary text or actions begin |
| Rail | Labeled in the ruler diagram; the source gives no purpose statement for the rail ruler |

Full ruler set as labeled in the spec diagram: Margin · Bar or safety region · Title · Content 1 · Content 2 · Content 3 · Content 4 · Bar or safety region · Rail.

Use content rulers to align and anchor key content such as headlines and carousels. Content rulers offer flexible alignment options to help create a consistent layout across a product.

### 3. Expressive use
Choosing a narrower or wider margin can create or remove negative space, or create expressive moments in a content-forward product. Rulers can create more immersive experiences — e.g. a photo grid can take the full width of the screen while components like search use wider margins. Realigning primary components or content to a content ruler can create strong hierarchy and visual rhythm across a product.

---

## Spacing

### 1. What it is + when to use
Spacing helps group content, direct attention, and shape the personality of a product. A denser layout can feel more serious and focused; a more spacious layout can feel calm and open. Material's spacing system can adapt to breakpoints and density settings. Desktop layouts can use more generous spacing than mobile layouts.

### 2. Values
Margins per breakpoint: 16dp (compact), 24dp (medium, expanded, large, extra-large). Spacer between panes: 24dp. Padding: increments of 4dp.

### 3. Spacing to group content
- **Explicit grouping**: outlines, dividers, shadows enclose related elements; can indicate interactivity (list items between dividers; a card with image + caption).
- **Implicit grouping**: close proximity and open space; e.g. carousel items placed close together with space around the composition to separate them from other content.

### 4. Spacing to direct attention (four principles)
| Principle | Rule |
|---|---|
| Rhythm | Keep consistent spacing between related elements or groups so they're easier to navigate with the eye; cards must maintain consistent horizontal spacing when their height varies |
| Similarity | Similar elements must have the same spacing and sizing to show they're related; leading elements like thumbnails, avatars, or icons must always be aligned; thumbnails must use identical sizes and styles even when source photos differ in aspect ratio |
| Proximity | Place components near each other to create cohesive groups; buttons must be close to the content they affect |
| Continuity | Place related elements in a container, row, or column to establish a clear group — e.g. a row of chips signals a single unified control |

### 5. Spacing as expression
Give the most important content, tasks, or actions visual prominence with **generous spacing and the brightest surfaces**.
- **Focal points**: consistent placement of key actions and information builds recognizable focal points across a product; carousel images, categories, and titles should appear in a consistent location across pages.
- **Negative space**: allow negative space to give form and meaning to elements on screen; framing important actions or content with generous spacing creates emphasis.

---

## Density (information density, component scaling, targets, pixel density)

### 1. Principles
- Information density is the consideration of the amount of information visible on the screen.
- The default target size should be at least **48x48 CSS pixels**.
- People can change density as long as the density controls are accessible.
- Apply density thoughtfully; not every layout needs it.
- Layout and component scaling (component adaptation or component density) can allow people to scan, view, or compare more information at once.
- Information density can be achieved through layout and design decisions **without** using component scaling. Some people may not benefit from increased density.
- Information density and component scaling can be used together to provide more information and additional user control.

### 2. Information density
The amount of content (text, images, video) in a given space. A layout's spacing dimensions — **margins, spacers, and padding** — can change to increase or decrease density. High-density layouts are useful when people need to scan, view, or compare a lot of information, such as a data table; increasing the layout density of lists, tables, and long forms makes more content available on-screen. Higher density suits data-rich products (news, financial portals, dashboards). Lower density is better for products prioritizing aesthetics, a focused message, less information, or easier navigation. Consider density settings in the context of a device — a person may prefer denser on desktop but not mobile. **Density shouldn't automatically change across breakpoints or orientation unless a person changes it.**

### 3. Component scaling
The component density scale controls the internal spacing of individual components. The scale is numbered, **starting at 0 for a component's default density**, moving to negative numbers (**-1, -2, -3**) as space decreases, creating higher density. Higher density is typically applied by **decreasing the top and bottom padding or overall height by 4dp**.
- Center the grouped element within the component container.
- **Text size shouldn't change as the container size scales.**
- The measurement between the label and input is **20dp**; label and input are centered within their parent container.
- Documented density examples: buttons shown at densities 0, -1, -2 (grids-spacing) and +1, 0, -1 (layout-overview).

### 4. Do / Don't for density
- Don't increase density in UIs that involve focused tasks, such as selecting from a menu — it reduces usability by limiting selectable space (dropdown menu with high-density items shown with selectable space height of 38dp; layout-overview shows 36dp).
- Don't increase density in components that alert a person of changes, such as snackbars or dialogs.
- Don't apply component scaling to layouts by default if it would lower the target size below the default 48x48 CSS pixels. Don't scale layouts below 48x48dp by default.
- Do let people **opt in** to dense layouts and components, and provide a simple, accessible way to revert to defaults.
- Do keep settings interactions at default target sizes (48x48 CSS pixels) so density settings can be easily reverted.
- Documented density-setting UIs: an "Appearance settings" / density menu exposing **cozy, comfortable, compact**, and a density menu with **large, medium, small** options for a desktop table.

### 5. Targets (accessibility)
Dense components can be less accessible because interactive elements are smaller — use caution when increasing information density. Accessible targets must retain a minimum of **48x48dp** even if the visual element is smaller. Documented examples: a settings button icon of **24x24dp** with an interaction target of **48x48dp**; a button with a height of **36dp** and an interaction target of **48dp**; a selectable target of only **40dp** shown as the caution case.

### 6. Pixel density & dp
- Pixel density = number of pixels per inch. High-density screens have more pixels per inch; elements with the same pixel dimensions appear larger on low-density screens and smaller on high-density screens.
- **Pixel density = Screen width (or height) in pixels / Screen width (or height) in inches**
- **dp** = density-independent pixels; flexible units that scale to uniform dimensions on any screen. **A dp equals one physical pixel on a screen with a density of 160.**
- **dp = (width in pixels * 160) / screen density**

| Screen physical width | Screen density | Screen width in pixels | Screen width in dps |
|---|---|---|---|
| 1.5 in | 120 | 180 px | 240dp |
| 1.5 in | 160 | 240 px | (not in source) |
| 1.5 in | 240 | 360 px | (not in source) |

Breakpoints / window size classes provide the foundation for top-level layout decisions, but display-specific considerations are also needed.

---

## Canonical layout examples (overview)

### 1. What it is + when to use
Canonical layout examples are designs for common screen layouts across all breakpoints; they demonstrate how to implement the layout scaffold and are available in code as a starting point. Each considers common use cases and components to address expectations and user needs for how products adapt across breakpoints. **There are three**: feed, list-detail, and supporting pane — each with configurations for compact, medium, and expanded breakpoints.

### 2. Discriminating rules
| Use | When |
|---|---|
| Feed | Arrange elements like cards in a configurable grid for a quick, convenient view of a large amount of content |
| List-detail | Display explorable lists of items alongside each item's details; divides the window into two side-by-side panes; for parent-child pairings |
| Supporting pane | Organize content into primary and secondary sections; use when the secondary content is only meaningful in relation to the primary content. For content with a parent-child relationship, use list-detail instead |

Supporting pane areas: **Primary display area** contains the main content and occupies the majority of the window (typically about two-thirds); **Secondary display area** presents supporting content in a panel taking the remainder.

### 3. Advanced custom layouts
To create a custom layout, build on top of canonical layouts or layer scaffold elements. **Layering**: use the *levitate* adaptive strategy; layering panes above other content creates a focused, task-oriented experience such as reviewing a shopping basket, responding to comments, creating a calendar event.

---

## Feed layout

### 1. What it is + when to use
A feed layout uses a grid composition to enable quick content browsing and discovery. Key use cases: news, photos, social media. Use it to show different pieces of content through **cards and lists**. Feeds support displays of almost any size as grids can adapt from single to multi-column.

### 2. Dividing space
A feed composition is flexible enough to allow content with varying proportions and sizing (e.g. small and large cards). Use size and position to establish relationships among content elements. **The order of items is determined by their position.** Feed items should reflow when available space changes — rotating or unfolding a device, entering multi-window mode. Feed items can change size to group content.

### 3. Across breakpoints
| Breakpoint | Behavior |
|---|---|
| Compact | Stack vertically, like a list of cards with individual items filling the full width of the pane |
| Medium | Can support components with different widths and be split across multiple columns |
| Expanded, large & extra-large | Can support components with different widths and multiple columns; the number of columns should usually increase at expanded breakpoints; column width can increase at larger breakpoints |

---

## List-detail layout

### 1. What it is + when to use
Many layouts can be split into a list view and a detail view. Use list-detail for quickly accessing details of an item from a long list of content. Key use cases — parent-child pairings: text message + conversation; file browser + open folder; musical artist + album detail; settings + category detail; email inbox + selected email.

### 2. Anatomy
Two panes: **List** (list area — several stacked cards, on the left pane in LTR) and **Detail** (detail area — a single section, on the right pane in LTR). Depending on the breakpoint, the two panes may appear together in the same layout or across separate layouts. List-detail uses the same pane guidance as all single- and two-pane layouts, including special behavior for foldables.

### 3. Visible panes per breakpoint
| Breakpoint (dp) | Visible panes |
|---|---|
| Compact (0-599) | 1 pane |
| Medium (600-839) | 1 (recommended) or 2 panes |
| Expanded (840+) | 2 panes |
| Large (1200-1599) | 2 panes |
| Extra-large (1600+) | 2 panes |

### 4. Across breakpoints
- **Compact**: single-pane layout; only one view is visible at a time, either list or detail. Devices: phone in portrait, closed foldable, tablet in split-screen mode.
- **Medium**: single-pane for information-dense content or deep focus (foldable open flat, tablet in portrait); two-pane to browse collections and switch between items quickly. **To maximize horizontal space for two-pane layouts, use a bottom navigation bar or modal navigation rail.**
- **Expanded, large & extra-large**: two-pane layout (phone in landscape, tablet in landscape).

### 5. States & behavior
- **Back button**: appears in detail view **only for single-pane layouts**.
- **Selected state**: appears **only in list view for two-pane layouts**.
- **Visual focus**: use explicit and implicit grouping to direct focus in two-pane layouts.
- **Transitioning, no selected list item**: a single-pane layout shows the list view; a two-pane layout shows placeholder content / an empty state in the detail pane. In some cases, such as multi-select, the most recently used pane should stay visible when switching to a single-pane layout.
- **Transitioning, selected list item**: single→two panes shows both panes with the selected item's details visible. Two→single depends on the product: the detail pane should typically show in a single-pane layout and an app bar appears; if the product supports selection without deep navigation (e.g. multi-select) the list view can show with the item selected; **consistency is key** — if a layout showed the list view previously it should return to that view when returning to a single pane.
- **Persistent states**: in most cases a state should be saved when navigating between detail views, including read and unread content. Detail views should retain their scroll position when navigating to other items, and across folding/unfolding.

### 6. RTL
Mirrored in RTL: text and other elements are aligned to the right and flow right to left. Is single-pane at compact breakpoints, switching between list and detail views; divides the window into two side-by-side panes on large screens.

---

## Supporting pane layout

### 1. What it is + when to use
Organizes content into primary and secondary areas. The primary area contains the main content and occupies the majority of the space (typically about two-thirds); the secondary area contains supporting content. Key use cases: productivity; document editing and commenting; content and media browsing. Use when the secondary content is **only meaningful in relation to** the primary content; for parent-child relationships use list-detail instead.

### 2. Dividing space
The window is divided between a **focus pane** and a **supporting pane**. Depending on the breakpoint the supporting pane may appear below or beside the focus pane.

| Supporting pane placement | Pane width | Breakpoint |
|---|---|---|
| Below | Flexible | Compact or Medium |
| Leading or trailing | Fixed (360 dp) | Expanded |

### 3. Across breakpoints
- **Compact**: supporting pane appears below the focus pane. A **bottom sheet** can be useful for keeping focus on the primary pane while providing access to supporting information.
- **Medium**: supporting pane appears below the focus pane (e.g. cards laid horizontally across the bottom; supporting-pane cards can scroll horizontally across the bottom of the screen).
- **Expanded**: supporting pane appears on the leading or trailing side of the focus pane.

### 4. Resizing
Supporting pane layouts can have a pane drag handle to **temporarily** resize the secondary content; temporary resizing resets custom widths to the default when the pane or product is closed and reopened.

### 5. RTL
Mirrored in RTL — supporting pane to the left of the primary content; text and other elements within the pane are aligned to the right and flow right to left.

---

## Bidirectionality & RTL

### 1. What it is + why
Over 2 billion people read and write in RTL languages like **Arabic, Hebrew, Farsi, and Urdu**. Layouts should support both LTR and RTL through mirroring and other best practices. Consider the holistic experience including global writing, localizing voice, and design principles for culturally appropriate icons. Material's components are built to support RTL — elements and tokens are named "leading" and "trailing" — however extra configuration may be needed for specific RTL situations.

### 2. Mirroring
Changing a layout from LTR to RTL (or vice versa), or flipping it horizontally, is mirroring. UI elements and text that typically appear on the left in LTR align to the right. **Reading flow starts from the top right corner instead of the top left.** Not all elements mirror: graphs and charts maintain LTR directionality for Persian and Urdu.

### 3. Text rendering
Two parts: **Alignment** (how the edges of the text box are placed alongside other elements) and **Directionality** (how text and other elements flow within a text box, LTR or RTL). In RTL languages text is usually right-aligned and elements flow right to left. Common issues: text entry, cursor position, punctuation, phone numbers, URLs. Improper RTL rendering creates cognitive overload and negatively impacts user sentiment and trust.
- **Don't** reverse the order of the email username and domain (@google.com) — the domain should always be to the right of the username; usernames can still be written RTL with the cursor moving to the left.
- **Don't** apply LTR directionality to RTL content — it may scramble word order. Content should have both RTL alignment and directionality.

### 4. Icons & symbols
Directional UI icons like back and forward should be mirrored. In Hebrew, timelines and media controls on a page should retain LTR directionality. Send buttons are mirrored in RTL. Help icons are mirrored in some RTL languages, like Urdu and Persian. The meaning of icons and symbols can vary significantly across cultures.

### 5. Time
- Linear representations of time are often mirrored in RTL. **Linear progress indicators should move right to left for most RTL languages, except Hebrew where they remain LTR.**
- Circular representations of time remain the same; circular progress indicators move clockwise.
- **Media players**: media controls for video or audio players are **always LTR**. (In Urdu, controls and progress for media and a podcast title show LTR while all other content is RTL.)
- **Clocks**: directionality of time remains LTR and clocks still turn clockwise; **AM/PM symbols for 12h clocks should be placed to the left**; the 24-hour clock is often used where the primary language isn't English. Clock icons, circular refresh icons, and progress indicators with arrows pointing clockwise shouldn't be mirrored. 24-hour and 12-hour clocks in RTL move clockwise but mirror UI elements such as AM/PM and buttons.

### 6. Component RTL rules
| Component | RTL rule |
|---|---|
| Badges | Change position and alignment for RTL — small badge appears on the top left of the icon; large badge appears on the top left of the icon |
| Toolbars | Mirror the order of the tools; in a mirrored floating toolbar the FAB appears on the left |
| App bars | Mirror the app bar's layout; flip appropriate icons, such as arrows. Variants shown in RTL: center-aligned, small; medium flexible; large flexible |
| Navigation drawer | Drawers that open from the side are always placed on the leading edge — left for LTR, right for RTL |
| Navigation rail | Placed on the leading edge — left for LTR, right for RTL |
| Expanded navigation rail | Always placed on the leading edge — left for LTR, right for RTL; include mirrored icons |
| Text fields | Icons are optional; leading and trailing icons change position based on LTR/RTL. RTL-affected parts: icon signifier, valid or error icon, clear icon, voice input icon, dropdown icon, image |
| Chips | Leading icon of input chips can be an icon, logo, or circular image; the trailing icon is always aligned to the end side of the container — right for LTR, left for RTL |
| Panes | For RTL languages, navigation components will be on the right |

### 7. Swipe gestures
RTL swiping and gestures should mirror their LTR counterparts. If a delete icon is revealed when swiping from the right in LTR, the same must be possible from the left in RTL. People can navigate horizontally between peer views like tabs and to complete actions. On Android, predictive back allows swiping left or right to go back or dismiss modal components; RTL predictive back should mirror LTR.

---

## Windows, foldables & multi-window

### 1. Windows
A window frames and contains an app or product. Many systems support multi-window views displaying multiple apps at once; two windows can be shown at once with a taskbar underneath. On desktop, windows can be resized and moved around freely and should adapt to various screen sizes.

### 2. Display cutout
An area on some devices that extends into the display surface, allowing an edge-to-edge experience while providing space for important sensors. Applications can extend around display cutouts or other features, but some parts of the UI might be obscured. Respect the content-safe area in portrait and landscape.

### 3. Foldables — fold
The fold divides the screen into two portions, horizontally or vertically. It can be a flexible area of the screen or, on dual-screen devices, a hinge separating two displays. A flexible fold is barely visible (some users may feel a tactile difference) and content can flow over it fairly easily. Folds are typically found in the center of the device screen. On devices with a **physical hinge** there is no display hardware in that region — design the screen as two distinct sections (separate window areas or panes) so a composition works across the hinge and screens.

### 4. Foldables — device states
| State | Definition / breakpoint effect |
|---|---|
| Folded | Can include a front screen, which often fits in the compact window size class, like a phone in portrait |
| Open flat | Fully opened screen; usually increases the window size class to medium or expanded; usable in landscape or portrait |
| Tabletop | Half-opened, forming a rough 90 degree angle with one half resting on a surface; resembles a laptop |

Open portrait: longer device edge vertical, shorter edge horizontal. Open landscape: longer edge horizontal, vertical edge shorter. In tabletop, UI controls near the fold can be difficult to access and text overlaying the fold can be hard to read; if camera hardware is present a tabletop device is best positioned on a side without protruding hardware.

### 5. App continuity
On a foldable, an app can transition from one screen to another automatically. After the transition the app should resume in the **same state and location**, and the current task should continue seamlessly.

### 6. Multi-window mode
An Android system feature for displaying multiple apps on the same screen — useful for multi-tasking or workflows that depend on comparing information. **Not** the same as using multiple panes to display content from a single app.
- Creation: **taskbar** (positioned at the bottom of the screen; provides a launching point for pinned and suggested apps to easily become a separate window — select and drag an app from the taskbar and move the app icon to indicate where the new window should be displayed) or **context menu** via the overview.
- Positioning can be vertical or horizontal.
- **Sizing**: by default multiple windows are created as a **50/50 side-by-side split**; windows can be adjusted to **1:3 or 2:3** proportions, providing a primary and secondary window dynamic. The screen handle can be dragged and released to create the desired ratio and automatically adjusts to the closest snap point.
- In multi-window mode, the available screen area often changes from medium or expanded window class to **compact** — layouts should adapt accordingly.
- User-needs rules: apply smooth transitions as described in motion guidance; ensure users can create multiple windows easily and move between them; keep mental models and interaction patterns simple so users aren't required to think about which mode is appropriate for each task; design and implement window dynamics consistently across variations in foldable hardware, including those with a hinge that separates two displays.

---

## What's new — May 2026 (explicit update sections)

**Layout overview → What's new → May 2026.** When creating new layouts, use the layout scaffold, start from a canonical layout example, and ensure layouts scale across breakpoints.
- Layout structure and design: Introduced **layout scaffold**, to create adaptive layouts efficiently; **new adaptive guidelines for mobile, desktop, and spatial devices**; **updated canonical layout examples**; **Spacing system**.
- Naming: **Window size classes renamed to breakpoints**; **Responsive layout renamed to adaptive design**.
- "The Material layout scaffold enables layouts to adapt across different screen sizes."

**Grids & spacing → What's new → May 2026.**
- How to use grids and rulers to adapt layouts across devices.
- **Expressive spacing guidelines.**
- "As screen size increases, additional columns allow for a richer layout."

Note: none of these six pages contains a section literally titled "M3 Expressive update." The expressive-relevant content is the May 2026 "What's new" entries above plus the "Spacing as expression" section (focal points; negative space; generous spacing and the brightest surfaces for the most important content) and the "Ruler options" guidance (narrower/wider margins to create expressive moments in a content-forward product).

---

## Availability & resources (all pages)
| Type | Resource | Status |
|---|---|---|
| Design | M3 Design Kit (Figma) | Available |
| Design | Spacing system & tokens | Available |
| Implementation | Jetpack Compose: Canonical layouts | Available |
| Implementation | Jetpack Compose: Rulers | Available |
| Implementation | Android Views (MDC-Android): Canonical layouts | Available |

---

## Gaps — referenced in these pages but values not present in the text

> **Before treating a measurement here as unavailable:** many of these are published as
> `md.comp.*` values in the generated Compose token files, which are collected in
> [`component-tokens.md`](./component-tokens.md) — container heights and widths, shape
> assignments, elevation levels, icon sizes, and internal spacing. Check there first. Those are the
> Compose token values, so attribute them as such rather than as guideline text.

- No `md.sys.*` or `md.comp.*` token names appear anywhere in these six pages; no color-role mapping and no typography-role mapping is given for any layout region (bar, rail, pane, spacer, drag handle).
- No corner-radius / shape token values for panes, spatial panels, or floating panes.
- Grid column **counts, column widths, and gutter values per breakpoint** are shown only in images/alt text (e.g. "compact screen with 4 columns", "foldable screen with 8 columns", "tablet with content divided into 8 columns, each pane 4 columns wide") — no normative table in the text.
- Spacing-scale values and spacing token names live on the linked "Spacing system & tokens" page (/m3/pages/spacing/overview), not in these files.
- Drag handle dimensions, corner radius, and touch-target dp are not given (only "slightly overlaps the panes").
- Safety region dp heights and bar/safety/title/content ruler offset values are not given.
- App bar and navigation bar heights, and navigation rail collapsed/expanded widths, are not given on these pages.
- No state list (enabled/hover/focus/pressed/dragged/selected/disabled) or state-layer opacity values for drag handles or any layout element.
- No shape-morph or motion duration/easing values; motion is only cross-referenced ("apply smooth transitions as described in motion guidance").
- Pixel-density table cells for "Screen width in dps" at densities 160 and 240 did not convert (only 240dp at density 120 is present).
- Contrast ratio requirements are not stated numerically anywhere in these pages.
- Feed layout: no per-breakpoint column-count numbers or card min/max widths in the text.
- Snackbar/dialog/menu density counter-examples cite only alt-text dp values (38dp menu item in grids-spacing, 36dp in layout-overview) — no normative minimum.
