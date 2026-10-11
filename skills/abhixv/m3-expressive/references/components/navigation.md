# Navigation (M3): Navigation bar, Navigation rail, Navigation drawer, Tabs

Source: m3.material.io pages `navigation-bar`, `navigation-rail`, `navigation-drawer`, `tabs` (updated 2026-07-17). No `md.sys.*` / `md.comp.*` token identifiers appear in the converted text — color roles below are the exact role names the pages print; see "Gaps" at end.

## Cross-component selection rule (from the four pages)

| Window size class | Use |
|---|---|
| Compact | Navigation bar, or modal navigation rail (nav bar page). Nav drawer page: modal navigation drawer, or swap for navigation bar. Don't use a standard navigation rail (space constraints). |
| Medium | Navigation bar **or** navigation rail — "decide based on whether horizontal or vertical space is more important". Nav bar uses **horizontal** items here. Rail page: use rail especially if prioritizing persistent vertical navigation over maximizing vertical content space; with few destinations consider a nav bar instead. Nav drawer: modal, alone or with a nav rail. |
| Expanded | Navigation rail, not a navigation bar. Standard navigation drawer (legacy) OK; standard drawer allowed in single-pane layouts. |
| Large / extra-large | Navigation rail (choose standard vs modal by available horizontal space + number of destinations). Legacy: standard navigation drawer, or a nav rail that transitions into a modal navigation drawer. |

- Navigation bar: 3–5 destinations of equal importance. Fewer than 3 → use tabs. More than 5 → don't use a nav bar; use tabs for related content within a page, or hide navigation behind a menu icon using a **modal expanded navigation rail**.
- Navigation rail: 3–7 destinations plus an optional FAB. If more than five destinations, consider a modal expanded nav rail.
- Navigation drawer: **no longer recommended** (M3 Expressive). Use the **expanded navigation rail**, which has mostly the same functionality and adapts better across window size classes.
- Tabs: organize related content *within* a page; navigation components are for distinct pages. "Use navigation for distinct pages and tabs for related content within a page."
- Never use a navigation rail and navigation bar simultaneously. Avoid using a navigation drawer with other primary navigation components. Avoid two navigation components on the same screen. A navigation rail should be the only visible navigation element (tabs may be used alongside a rail as an extra layer of visible navigation).

---

## Navigation bar

### 1. What it is / when to use vs siblings
Horizontal bar of 3–5 top-level destinations of equal importance, positioned at the bottom of the window for convenient access. Each destination = icon + label text; one destination is always active. Tapping/focusing an icon navigates to that destination.

Use for:
- Three to five main pages in the product
- Mobile or tablet only
- Compact or medium window sizes

Do not use for: accessing single tasks (such as viewing one email); desktop layouts (use a navigation rail or tabs); fewer than three destinations (use tabs); more than five destinations (elements may collide, and there likely won't be enough space for translated text).

Destinations don't change — they should be consistent across app screens.

### 2. Anatomy
Flexible navigation bar — 7 elements: Container; Icon; Label text; Active indicator; Small badge (optional); Large badge (optional); Large badge label.
(Guidelines page lists 6: Container, Icon, Label text, Active indicator, Large badge (optional), Small badge (optional).)

- **Container** — always at the bottom of the product, spans the full length of the window; navigation items are centered within it; has a color fill to provide separation from other content.
- **Navigation items** — hold the icon, label text, and active indicator for each destination. **Vertical**: text below the icon and indicator. **Horizontal**: icon and text beside each other *inside* the indicator. Horizontal items are centered in the nav bar with outer margins.
- **Icons** — must symbolize the content of their page. Filled icon for the active destination, outlined icons for inactive. If an icon has no filled version, apply **semibold** weight instead.
- **Active indicator** — shows which page from the nav bar is currently displayed; a pill shape in a contrasting color.
- **Label text** — short, meaningful description of the destination; another way to understand an icon's meaning; required on all items; 1–2 words.
- **Badges (optional)** — in the upper right corner of the destination icon; can contain dynamic information such as the number of new messages. Small badge = indicates an update; large badge = shows the amount of updates. Badges overlap the icon in both vertical and horizontal navigation items.

### 3. Variants / configurations
| Variant | M3 | M3 Expressive |
|---|---|---|
| Flexible navigation bar | — | Available |
| Navigation bar (baseline) | Available | Not recommended. Use **flexible navigation bar**. |

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Navigation item layout | Vertical (default) | Available | Available |
| Navigation item layout | Horizontal | — | Available |

Compact windows → vertical items. Medium windows → horizontal items.
Baseline nav bar configurations: 3 destinations / 4 destinations / 5 destinations.

### 4. Placement / measurements
- Nav bar stretches the **full window width**; container spans **100% of the window width**.
- **Vertical** navigation items dynamically change width to equally fit the container. **Horizontal** navigation items have a **fixed width**, so extra space is added to the ends of the navigation bar instead.
- The nav bar is divided into equal-width segments with padding from the window edge; margins are measured from the window edge.
- Horizontal nav items should remain centered with **the same padding at each window size**. Horizontal items keep the **same width** in medium and expanded windows; only the padding around them changes.
- Only use navigation bars for **compact and medium breakpoints**.
- **FAB** is placed above the navigation bar and should be **right-aligned** above it. Don't cover the navigation bar with a FAB.
- Nav bars can be **temporarily** covered by dialogs, bottom sheets, navigation drawers, the on-screen keyboard, or other elements needed to complete a flow. They must not be permanently obstructed on any screen.
- Destinations have **fixed positions** — don't scroll them or modify their positions.

### 5. States, interaction, motion
States: Enabled; Hovered (**8% state layer**); Focused (**10% state layer**); Pressed (**10% state layer**).

- **Selection**: icon becomes filled and the active indicator **expands from the center of the icon**. The active indicator animation should only apply on **one axis**, to better represent a flat, shared plane.
- Selecting a non-selected item navigates using the **top level** transition pattern, and either **Preserve state** (returns to scroll position, current tab, in-line search status) or **Reset state** (prior interactions reset). Choose per product; apps requiring frequent switching between sections should preserve each section's state.
- **Re-selecting** the currently active destination resets the scroll position to the top of the page.
- **Don't swipe between destinations** — swiping does not navigate between destinations and is not supported. Reserve swipe for related items (cards in a carousel) or actions (archiving a list item).
- **Scrolling**: on scroll the nav bar can appear or disappear (scroll down hides, scroll up reveals). Don't hide the nav bar on scroll when a screen reader is active.
- **Touch**: active indicator appears in place as selection feedback; a touch ripple passes through the indicator; icon switches outlined → filled; icon changes color.
- **Cursor**: on hover the active indicator appears in a **reduced state**; on click (active and inactive states) a ripple passes through the indicator; icon switches outlined → filled; icon changes color, becoming darker.

### 6. Color roles
Flexible navigation bar (light and dark schemes), 6 roles: **Surface container**; **On-secondary container**; **Secondary**; **Secondary container**; **On-surface variant**; **On-surface variant**.
Baseline navigation bar, 6 roles: **Surface**; **On secondary container**; **On surface**; **Secondary container**; **On surface variant**; **On surface variant**.
Badge color roles: see badge specs.
XR elevated nav bar container options: Surface container / Surface container high / Surface container highest / Tertiary container.

### 8. M3 Expressive update (May 2025)
A new **flexible navigation bar** was introduced to replace the baseline navigation bar. It's shorter and supports horizontal navigation items in medium windows.
- Variants and naming: baseline navigation bar is **no longer recommended**; added **flexible** navigation bar — shorter height; can be used in medium window sizes with horizontal navigation items.
- Color: **active label changed from on-surface-variant to secondary**.

Differences from M2: Color — new color mappings and compatibility with dynamic color. Elevation — **no shadow**. Layout — container height is taller. States — the active destination can be indicated with a **pill shape in a contrasting color**. Name — "bottom navigation" has been renamed **navigation bar**.

### 9. Do / Don't
- Place the container at the bottom of the product, spanning the full window width; center navigation items within it.
- Use vertical items in compact windows (mobile); use horizontal items in medium windows (tablets).
- Use a filled icon for the active destination; increase icon weight to semibold if no filled version exists.
- Use the active indicator only for the active destination — never for more than one destination at a time.
- Give every navigation item a label; keep labels 1–2 words.
- Don't remove the labels from navigation items.
- Don't wrap or truncate label text — it can make the label hard to understand.
- Don't shrink longer text to fit on a single line.
- Don't use multiple or low-contrast colors in a navigation bar — it makes the active item harder to distinguish.
- Don't put more than five navigation items in a navigation bar.
- Don't scroll destinations or modify their positions.
- Don't use navigation bars for desktop layouts.
- Don't cover the navigation bar with a FAB.

### 10. Accessibility
- Assistive-tech use cases: move between navigation destinations; select a particular destination from a set; get appropriate feedback based on input type.
- Active and inactive icons must have a **minimum 3:1 contrast ratio with the container**.
- **Text scaling**: the nav bar should grow **vertically** to accommodate larger labels while retaining the default padding; scaled text may wrap in navigation items. Ensure the full label is always visible on-screen **up to 2x text sizing**; beyond that, text can truncate.
- **Initial focus** lands directly on the first navigation item (the first interactive element).
- Keyboard: **Tab** = move between navigation items; **Space / Enter** = selects the focused navigation item.
- Visual indicators: filled icon + **bold** label for selected destinations; outlined icon + **medium** label for unselected. Don't use outlined icons on selected items. When selected, the icon fills, darkens, and is backed by an active indicator shape.
- Labeling: the accessibility label for a navigation item is typically the same as the destination name; when visible UI text is ambiguous, make it more descriptive (visible "Library" → accessibility label "Music library"). Note: on Android Views (MDC-Android) a more descriptive accessibility label is not available and the role is not announced.
- Don't hide the nav bar on scroll when a screen reader is active.

### XR (navigation bar orbiter)
Anatomy, 7 elements: Container; Icon; Active indicator; Small badge (optional); Large badge (optional); Large badge label (optional); Label text.
- In **full space**, the nav bar can appear in an orbiter (spatial capabilities such as orbiters are only available in full space). In **home space**, use a regular nav bar on the same plane as body content to mimic a 2D experience. With spatial elevation the nav bar displays above the spatial panel on the Z-axis.
- **Global context**: orbiter centered at the bottom of the app it controls; stays anchored to the app during layout or content changes. **Local context**: centered at the bottom of the spatial panel it controls; repositions in response to layout/content changes — use caution; if it affects the overall app, place it in global context.
- **Offset positioning** for global actions; **inset positioning** for local actions specific to a spatial panel.
- Can overlap, or be adjacent to spatial panels with a **20dp margin** for visual separation.
- Inset: overlap spatial panels by **12dp** and **no more than half their height**. Don't obstruct content.
- Placement shouldn't exceed the width of adjacent spatial panels.
- Always place at the bottom of a spatial panel, within the immediate field of view (FOV). Avoid the top of a spatial panel — reserved for app bar orbiters or other critical UI.
- XR nav bars should follow applicable Material nav bar accessibility standards.

---

## Navigation rail

### 1. What it is / when to use vs siblings
Vertical navigation along the leading edge of the window, displaying navigation items, a menu, and a floating action button (FAB). 3–7 destinations plus an optional FAB. Always put the rail in the same place, even on different screens of an app. Two variants — **collapsed** and **expanded** — which easily transform into each other when the menu button is selected.

Collapsed and expanded rails can transition between each other on **any device**, including large or medium window size classes (tablets) *and* compact window size classes (phones in portrait orientation).

- **Collapsed**: runs along the leading edge; 3–7 navigation items; **should not be hidden**. For medium to extra-large windows (tablets, desktop). In medium windows with few destinations, consider a navigation bar instead. Compact windows should always use a navigation bar.
- **Expanded**: standard or modal; should always open from a menu icon; can reveal secondary destinations not visible when collapsed.
  - **Standard** — placed beside body content; best for larger windows with lots of available space; use when there are secondary destinations or actions of lower priority than the main navigation items.
  - **Modal** — overlaps body content, opened from a menu icon. Use for information-dense layouts where space is limited, and products with many navigation items.
  - In immersive experiences the expanded rail can be hidden entirely, appearing only when the menu icon is selected.

### 2. Anatomy
Collapsed + expanded (specs), 9 elements: Container; Menu (optional); FAB or Extended FAB (optional); Icon; Active indicator; Label text; Large badge (optional); Large badge label (optional); Small badge (optional).
Guidelines list (labelled "10 elements" on the source diagram, but the caption itemizes 11): Container; Menu (optional); Floating action button (FAB) (optional); Icon – active; Label text – active; Active indicator; Icon – inactive; Large badge (optional); Large badge label; Small badge; Label text – inactive.
Baseline nav rail, 8 elements: Container; Menu icon (optional); Icon; Active indicator; Label text; Large badge label (optional); Large badge (optional); Badge (optional).

- **Container** — leading edge of the window (left for LTR, right for RTL). Fill can be **turned off** so the rail appears directly on the surface; if so, ensure all items have a minimum **3:1** color contrast. Must run vertically — don't make it horizontal (use a navigation bar for horizontal navigation).
- **Menu (optional)** — transitions between collapsed and expanded. Once expanded, the rail can reveal secondary destinations. When expanded, the menu icon should change to represent that it can be collapsed.
- **FAB (optional)** — the rail container is ideal for anchoring the FAB to the top of the screen, placing the app's key action above navigation destinations. When nested within another component such as the nav rail, the FAB's resting elevation should be **level 0**. On expansion the FAB should transition into an **extended FAB**.
- **Active indicator** — shows which page is being displayed; pill shape in a contrasting color. In the **expanded** rail it **hugs the label text**; to resemble the baseline navigation drawer, modify it to fill the container. The **target area always spans the full width** of the rail even when the item container hugs its contents.
- **Icons** — must symbolize the content of their page. When selected, the icon fills and changes color, and an active indicator appears behind it.
- **Label text** — short, meaningful description; all navigation items require a **one word** label.
- **Badges** — communicate dynamic information such as counts or status. In **compact** nav rails the badge sits in the **upper right corner of the icon**; in **expanded** nav rails it sits **next to the label text**. Small badge; large badge with a number; large badge with a maximum character count.
- **Divider (optional)** — a vertical divider helps separate the rail from app content; position it on the edge of the rail container adjacent to the app's content area.
- Top of the rail can also hold a **logo**, but avoid logos that could be mistaken as buttons; don't use a logo as a menu button to expand the rail.

### 3. Variants / configurations
| Variant | M3 | M3 Expressive |
|---|---|---|
| Collapsed navigation rail | — | Available |
| Expanded navigation rail | — | Available |
| Navigation rail (baseline) | Available | Not recommended. Use **collapsed navigation rail**. |

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Expanded layout | Standard (default) | Available as navigation drawer | Available |
| Expanded layout | Modal | Available as navigation drawer | Available |
| Expanded behavior | Hide when collapsed | — | Available |

Common layouts (collapsed and expanded), 4 each: three navigation items; three navigation items with a menu; three navigation items with a FAB; three navigation items with a menu and FAB.
Baseline configurations, 5: with a menu; with a FAB; with menu and FAB, without labels; all destinations with text labels; with menu, FAB, and label text for all destinations.

### 4. Placement
- In adaptive layouts, place the rail **outside any panes**, always along the **leading edge** of the window. Don't place it within body content.
- Navigation rail items can be aligned as a group to the **top** or **center** of a layout. On tablets, use **center** alignment to make items easier to reach. The **menu icon and FAB should always be top-aligned**; avoid placing the FAB below navigation items.
- When the rail is hidden, body content can fill the remaining space as long as the menu icon is still accessible.
- Tabs can be used alongside a navigation rail to create an extra layer of visible navigation.
- A rail can be **expanded by default on larger screen sizes**, or **expanded over content on smaller screen sizes** — expanded navigation rails can open from menu buttons on mobile.
- Only use navigation rails for medium window size classes and larger. Never use the navigation rail and navigation bar simultaneously; on smaller screens the rail can transform into a navigation bar.
- When the rail transitions collapsed → expanded, page contents should automatically adjust to fit, and the rail's contents expand to fill the space.

### 5. States, interaction, motion
States: Enabled; Hovered; Focused; Pressed (collapsed and expanded).
Baseline nav rail exposes 8 states: Enabled / Hovered / Focused / Pressed **on active destination**, and Enabled / Hovered / Focused / Pressed **on inactive destination**.
- The navigation item's **target area always spans the full width of the nav rail**, even if the item container hugs its contents.
- **Selection**: destination screen uses the **top level** transition pattern; the icon becomes filled and the active indicator **expands from the center of the icon**.
- **Vertical scrolling**: destinations remain visible and fixed. **Horizontal scrolling**: the rail can scroll off-screen or remain fixed; to distinguish content scrolling underneath, use a **divider** or add elevation — **elevating the rail to level 1** creates visual distinction.
- **Predictive back** (Android): swipe left or right to go back or dismiss modal components; the previous screen is revealed in a preview to signal the destination; the rail pops off the edge of the window. **Predictive back only applies to the modal expanded navigation rail.**
- Touch: on tap the active indicator appears, a ripple passes through the indicator, the icon switches outlined → filled, and the icon and text change color. Hover: the hover state appears as a visual cue that the destination is interactive.

### 6. Color roles
Collapsed + expanded (light and dark schemes), 9 roles in anatomy order: **Surface container (optional)**; **On secondary container**; **Secondary container**; **Secondary (vertical) / On secondary container (horizontal)**; **On surface variant**; **On surface variant**; **Error**; **On error**; **Error**.
Baseline nav rail, 8 roles: **On secondary container**; **Secondary container**; **On surface**; **On surface variant**; **On surface variant**; **Error**; **On error**; **Error**.
XR elevated nav rail container + FAB pairings: Surface container with **tertiary** FAB; Surface container high with **tertiary fixed dim** FAB; Surface container highest with **tertiary fixed dim** FAB; Tertiary container with **primary** FAB.

### 8. M3 Expressive update (May 2025)
A **collapsed** and **expanded** navigation rail have been introduced to replace the baseline nav rail. The **expanded nav rail is meant to replace the navigation drawer**.
- Variants and naming: the baseline **navigation rail** is no longer recommended; added two wider navigation rails — **Collapsed**: replaces baseline nav rail; **Expanded**: replaces navigation drawer.
- Configurations: expanded rail modality — **Non-modal**, **Modal**. Expanded behavior — **Transition to collapsed navigation rail**, **Hide when collapsed**.
- Color: active label on **vertical** items changed from **on surface variant** to **secondary**.
- The collapsed and expanded navigation rails match visually and can transition into each other.

Differences from M2: Behavior — predictive back interaction. Color — new color mappings and compatibility with dynamic color. States — the active destination can be indicated with a **pill shape in a contrasting color**.

### 9. Do / Don't
- Place the rail on the leading edge of the window; keep it in the same place across screens.
- Always run the rail vertically — don't use it horizontally (use a navigation bar).
- Top-align the menu icon and FAB; don't place the FAB below navigation items.
- Use center alignment for rail destinations on tablets.
- Use the active indicator only for the current open page — never for more than one navigation item at a time.
- Give every navigation item a one-word label. Break longer phrases into two lines, or hyphenate longer words, if necessary.
- Don't truncate or display an ellipsis in place of label text. Don't reduce the type size to fit more characters into a destination label.
- Don't hide the collapsed navigation rail.
- Don't place the rail within body content or inside panes.
- Don't use more than two colors for destinations, and don't use low-contrast colors — it makes distinguishing active items difficult.
- Use caution when placing logos in the rail where they might be confused with an action or destination; don't use a logo as the menu button.
- Don't use a standard navigation rail for compact layouts.

### 10. Accessibility
- Assistive-tech use cases: navigate between navigation destinations; select a particular destination from a set; get appropriate feedback based on input type.
- If the container fill is turned off, all items need a minimum **3:1** color contrast; active and inactive icon colors need sufficient contrast against the container.
- The target area for expanded navigation rails spans the **full width of the container**, even though the active indicator visually hugs the content.
- Use a filled icon for the active destination and outlined icons for inactive; if an icon has no filled style, use the **semibold** icon weight instead. Avoid using the same unfilled icon style for selected and unselected items.
- **Text scaling**: items should grow **vertically** to accommodate larger labels while retaining default padding; scaled text may wrap. Ensure the full label is always visible **up to 2x text sizing**; beyond that, text can truncate.
- **Initial focus** lands on the first interactive item — whether it's the menu, the FAB, or the first navigation item. From the FAB or menu, **Tab** moves to the navigation items; **Tab** or **Arrows** then navigate between items.
- Keyboard: **Tab / Arrows** = navigate between interactive elements; **Space / Enter** = selects an interactive element.
- Labeling: accessibility label is typically the same as the adjacent text label; when visible UI text is ambiguous, be more descriptive (visible "Recent" → "Recent images"). Note: on Android Views (MDC-Android) a more descriptive accessibility label is not available and the role is not announced.

### XR (navigation rail orbiter)
Two variants: **contained FAB rail** (a contained FAB within the rail; compact and familiar layout; more subtle, aligns with the baseline navigation bar) and **spatialized FAB rail** (the FAB becomes its own orbiter placed outside the nav rail orbiter; use for higher emphasis and a distinct spatial effect, to emphasize key actions and leverage XR hierarchy).
Anatomy, 9 elements: Container; Active indicator; Large badge (optional); Badge (optional); Large badge label (optional); Label text; Icon; Embedded or spatialized FAB (optional); Menu icon (optional).
- Full space → orbiter; home space → regular nav rail on the same plane as body content.
- **Global context only**: centered along the left or right edge of the app it controls; stays anchored during layout/content changes. **Don't** place a nav rail orbiter in local context or between spatial panels — nav rails are for app-level navigation. For layouts spanning more than two spatial panels, consider a navigation bar orbiter.
- **Offset positioning** for global actions; **inset positioning** for local actions specific to a spatial panel. Overlap, or sit adjacent to spatial panels with a **20dp margin**.
- Inset: overlap spatial panels by **12dp** and **no more than half their width**.
- Vertical alignment: top, middle, or center of spatialized panels; placement shouldn't exceed the **height** of adjacent spatial panels.
- Spatialized FAB: place in close proximity to the rail orbiter — Material recommends a **20dp margin**; can be above or below the rail orbiter; keep it within the height of adjacent spatial panels.

---

## Navigation drawer (no longer recommended)

### 1. What it is / when to use vs siblings
> The navigation drawer is **no longer recommended** in the Material 3 Expressive update. For those who have updated, use an **expanded navigation rail**, which has mostly the same functionality of the navigation drawer and adapts better across window size classes.

Provides access to destinations and app functionality, such as switching accounts. Either permanently on-screen, or opened and closed by a navigation menu icon. One navigation destination is always active. Essentially a list contained within a side sheet.

Recommended for: apps with **5 or more** top-level destinations; apps with **2 or more** levels of navigation hierarchy; quick navigation between unrelated destinations; replacing the navigation rail or navigation bar on large screens.

- **Standard**: for expanded, large, and extra-large window sizes. Can be permanently visible (best for frequently switching destinations) or opened/closed by tapping a menu icon (best for focusing more on screen content). In medium and compact windows, use modal drawers instead.
- **Modal**: uses a **scrim** to block interaction with the rest of the app's content and **doesn't affect the screen's layout grid**. Usable at any window size but primarily compact and medium, where space is limited or prioritized for app content. Can be swapped with standard drawers at expanded, large, and extra-large sizes. Always opened by an action outside the drawer, such as clicking a navigation menu icon in a navigation rail.

Put the most frequent destinations at the top and group related destinations together.

### 2. Anatomy
Specs list, 7 elements: Container; Headline; Label text; Active indicator; Badge label text; Scrim; Icon.
Guidelines list, 8 elements: Active Indicator; Icon; Label; Badge label; Sheet; Divider; Section label (optional); Scrim.
Drawers can also include **headers, subheads, and dividers** to organize longer lists.

- **Sheet** — holds all drawer elements; a **side sheet** is the container for both standard and modal drawers. Side-opening drawers are always on the **start edge** (left for LTR, right for RTL).
- **Active indicator** — a background shape communicating which destination is currently displayed.
- **Label text and icons** — destinations are actionable list items; each describes its destination with label text (required) and an optional icon. Label text should be clear and **short enough that it isn't cut off by the sheet**. Icons always placed **before** text; other app components and content should reference these icons.
- **Section label (optional)** — short subhead section labels group related destinations.
- **Divider (optional)** — separates groups of destinations; use **full-width** dividers.
- **Scrim (modal only)** — placed directly behind the drawer's sheet; tap or click to dismiss the drawer.

### 3. Measurements
**Standard navigation drawer**

| Attribute | Value |
|---|---|
| Container height | 100% |
| Container width | 360dp |
| Container shape | 0,16,16,0dp corner radii |
| Icon size | 24dp |
| Active indicator height | 56dp |
| Active indicator shape | 28dp |
| Active indicator width | 336dp |
| Horizontal label alignment | Start-aligned |
| Left padding | 28dp |
| Right padding | 28dp |
| Active indicator padding | 12dp |
| Padding between elements | 0dp |

**Modal navigation drawer** — identical to the above, but the source table lists **no Container shape** row: Container height 100%; Container width 360dp; Icon size 24dp; Active indicator height 56dp; Active indicator shape 28dp; Active indicator width 336dp; Horizontal label alignment Start-aligned; Left padding 28dp; Right padding 28dp; Active indicator padding 12dp; Padding between elements 0dp.

The navigation drawer has **one token set**.

### 4. Placement / responsive layout
- Always on the start edge of the screen (left LTR, right RTL).
- **Compact**: use modal drawers, or swap the drawer for a navigation bar. On **web**, when the screen size is smaller than **320 CSS pixels**, swap the navigation drawer for a navigation bar to ensure accessibility.
- **Medium & expanded**: use a modal drawer alone or with a navigation rail. When a rail and modal drawer are used together, the drawer can repeat destinations in the rail as long as the drawer offers enough visual separation between levels of the navigation hierarchy. A standard drawer can be used in **single pane layouts** in expanded windows.
- **Large and extra-large**: for web on laptop/desktop, use either a standard drawer, or a navigation rail that transitions into a modal drawer.
- Use a **transition** when swapping components (e.g. portrait → landscape, the navigation rail should transform into a navigation drawer).

### 5. States, interaction, motion
States: Enabled; Hovered; Focused; Pressed.
- **Scrolling**: drawers can be vertically scrolled independent of the rest of the screen's content and UI; if the destination list is longer than the drawer height, its contents scroll within the drawer. Body content should remain stationary while the drawer scrolls.
- **Visibility**: **dismissible standard drawers** suit content-prioritized layouts (e.g. a photo gallery) or apps where users are unlikely to switch destinations often — they should use a visible navigation menu icon to open and close, and remain open until the icon is tapped again. **Permanently visible standard drawers** allow quick navigation between unrelated destinations and can't be closed or dismissed by the user.
- **Appearing**: uses an **enter and exit** transition pattern.
- **Modal dismissal**: selecting a drawer item; tapping the scrim; swiping toward the drawer's anchoring edge (e.g. swiping right-to-left for a left-aligned drawer).
- Touch: on tap the active indicator appears in place; a touch ripple passes through the indicator; the icon switches outlined → filled; the icon changes color, becoming darker.
- Cursor: on hover the hover indicator appears; on click a ripple passes through the indicator; the icon switches outlined → filled; the icon changes color, becoming darker in light theme and lighter in dark theme, to increase contrast.

### 6. Color roles
9 roles (light and dark schemes), in anatomy order: **Surface container low**; **On surface variant**; **On secondary container**; **On secondary container**; **Secondary container**; **On secondary container**; **On surface variant**; **On surface variant**; **Scrim**.
Divider color roles: see divider specs.

### 8. M3 Expressive update (May 2025)
The navigation drawer is **no longer recommended**. Use the **expanded navigation rail** instead.

Differences from M2: Color — new color mappings and compatibility with dynamic color. Variants — distinguishes two separate variants, standard and modal. Shape — **rounded corners at the ending edge** of the drawer. States — updated color and shape for indicating selected state.

### 9. Do / Don't
- Put the most frequent destinations at the top; group related destinations together.
- Use standard drawers in expanded, large, and extra-large windows; modal drawers in compact and medium windows.
- Use full-width dividers to separate **groups** of destinations. Don't use dividers to separate **individual** destinations.
- Keep label text concise, but truncate it if it extends beyond the container width. Don't wrap label text. Don't shrink text size to fit a label on a single line.
- Place icons before text. Icons should be used for **all** destinations, or **none** — don't apply icons to some destinations and not others. Use recognizable icons when conventions exist.
- Avoid using a navigation drawer with other primary navigation components, such as a navigation bar; choose a single navigation component based on product requirements, breakpoints, and window size class:
  - Navigation bars for **compact** window sizes
  - Navigation rails for **medium and expanded** window sizes
  - Standard navigation drawers for **expanded, large, and extra-large** window sizes

### 10. Accessibility
- Users should be able to move between destinations with assistive technology; select a particular destination from a set; get appropriate feedback based on input type.
- **Initial focus** lands directly on the first navigation item (the first interactive element).
- Keyboard: **Tab** — focus lands on the first navigation destination; **Space or Enter** — selects the focused destination, and focus moves to the newly opened section (if applicable); **Arrow** — navigate between destinations within the drawer.
- The modal drawer can be dismissed by selecting the scrim.
- Visual indicators: icons give the dominant cue of navigation state — use a filled icon for the selected destination to differentiate from outlined icons of non-selected destinations. Avoid keeping the selected destination's icon style the same as unselected. When selected, the icon fills, darkens in light theme (or lightens in dark theme), and is backed by an active indicator shape.
- Labeling: accessibility label is typically the same as the destination name; if UI text is correctly linked, assistive tech reads the UI text followed by the component's role (illustrated role: "tab"). When visible UI text is ambiguous, be more descriptive (visible "Recents" → "Recent images"). For Android Views (MDC-Android) a more descriptive accessibility label is not available to be set and the role is not announced.
- On web, below 320 CSS pixels swap the drawer for a navigation bar to ensure accessibility.

---

## Tabs

### 1. What it is / when to use vs siblings
Tabs group content into helpful categories and organize groups of related content that are at the **same level of hierarchy**. Tabs can horizontally scroll, so a UI can have as many tabs as needed. Place tabs next to each other as **peers**. Tabs control the UI region displayed below them; they can be joined with components like app bars, embedded in a specific UI region, or nested within components like cards and sheets.

Two variants:
- **Primary tabs** — placed at the top of the content pane under an app bar; display the **main content destinations**. Use when just one set of tabs is needed.
- **Secondary tabs** — used within a content area to further separate related content and establish hierarchy. Necessary when a screen requires more than one level of tabs. They use a simpler style of indicator, but their function is identical to primary tabs.

Discriminators vs navigation components: use navigation for distinct pages, tabs for related content within a page. Use tabs instead of a navigation bar when there are fewer than three destinations, or when there are more than five items to organize within a page. Use tabs to group **related** content, **not sequential** content.

### 2. Anatomy
Primary tabs, 6 elements: Container; Badge (optional); Icon (optional); Label; Divider; Active indicator.
Secondary tabs, 5 elements: Container; Badge (optional); Label; Divider; Active indicator.

- **Container** — holds multiple tabs; contents can be fixed or scrollable; should always extend the **full width of the window** and be divided into **equal sections**, one per tab; defined by a **divider on the bottom edge** to separate it from content below. Content may scroll under the container.
- **Icon (optional)** — communicates the kind of content within a tab; should be simple and recognizable. Icons alone aren't as effective as text labels at communicating complex content.
- **Label** — clearly and succinctly describes the content within the tab; appears in a single row; can use a second line if needed, with truncated text. Alternatively, scrollable tabs allow room for longer titles.
- **Badges (optional)** — show notifications or updates related to a specific tab; usable on primary or secondary tabs; small and large badges both usable. Limit badge content to **four characters, including a "+"**. Once the user views the relevant content, the badge value should update or the badge should disappear entirely.
- **Active indicator** — an underline plus a color change on the active tab's text and icon.

### 3. Measurements

| Attribute | Value |
|---|---|
| Container height (label text only) | 48dp |
| Container height (icon and label text) | 64dp |
| Icon size | 24dp |
| Divider height | 1dp |
| Primary active indicator height | 3dp |
| Secondary active indicator height | 2dp |
| Active indicator shape | 3, 3, 0, 0 |
| Active indicator minimum length | 24dp |
| Padding between inline icon and text | 8dp |
| Padding between inline text and badge | 4dp |
| Overlap of badge on stacked icon | 6dp |

- Tabs are divided into equal sections, with labels and icons positioned **vertically centered**. The **divider is included in the height, placed inside the container**.
- **Primary** tab active indicators are **inset 2dp on each side**, have a **fully rounded corner radius**, and a **minimum length of 24dp**.
- Scrollable tabs: the first visible tab should be **offset by 52dp** from the left side of the device, for both web and mobile. The width of each tab is defined by the length of its text label.

### 4. Placement / responsive layout
- Tabs display in a single row, each tab connected to the content it represents; as a set, all tabs are unified by a shared topic.
- Primary tabs sit at the top of the content pane under an app bar. **Secondary tabs should always be placed below primary tabs.**
- For **fixed** tabs, the maximum width for each tab should be determined by the width of the **widest** tab. The group of tabs should use a **fluid margin** and align to the **center or leading edge of the body region**.
- Avoid using more than **four** tabs at once; at **five or more** the container becomes cramped.
- **Scrolling content**: tabs can either be fixed to the top of the screen, or scroll off the screen and return when the user scrolls upward. Don't scroll tabs behind an app bar — when tabs are attached to a component, they should appear and move as a single unit.

### 5. States, interaction, motion
By default, tabs inherit **enabled** states with one **active** state. The inactive and active states of a tab can inherit **hover, focus, and pressed** states.
Primary and secondary tabs each document 8 states: Enabled / Hover / Focused / Pressed on the **active** destination, and Enabled / Hover / Focused / Pressed on the **inactive** destination.
- **Fixed tabs** display all tabs in a set simultaneously; best for switching between related content quickly (e.g. between transportation methods in a map). Navigate by tapping an individual tab, or swiping left or right in the content area.
- **Scrollable tabs** — use when a set of tabs cannot fit on screen; allow longer text labels and a larger number of tabs; best for browsing on touch interfaces. Navigate by swiping the set left or right, or by using **arrow/tab**; padding should remain the same with long labels.
- Touch: a touch ripple appears on tap indicating interaction feedback; the selected indicator becomes active and **shifts into position** once the touch has been engaged.
- Cursor: hover state appears as a visual cue of interactivity; on click (in both active and inactive states) a ripple appears and the indicator shifts into position.
- Keyboard/Switch: on tab, a focus indicator appears; engaging the selected tab via Space/Enter in active states takes the user to a new destination; within the tab menu the user can arrow/tab through items, Space/Enter to select, or tab to exit the active state.

### 6. Color roles
Primary tabs, 7 roles (light and dark schemes), in anatomy order: **Surface**; **Primary**; **Primary**; **On surface variant**; **On surface variant**; **Outline variant**; **Primary**.
Secondary tabs, 5 roles: **Surface**; **On surface**; **On surface variant**; **Outline variant**; **Primary**.

### 8. M3 Expressive update
Not present on the tabs page (no "M3 Expressive update" section).
Differences from M2: Color — new color mappings and compatibility with dynamic color. Layout — **icons and labels are now vertically centered within the container**.

### 9. Do / Don't
- Use tabs to categorize related groups of content into clearly defined sets.
- Don't use tabs to move through **sequential** content that needs to be read in a particular order — instead create hierarchy within the content using techniques like typography style and open space.
- Place tabs next to each other as peers; place secondary tabs below primary tabs.
- Extend the container the full width of the window and divide it into equal sections.
- Keep text labels short and succinct, with a clear relationship to the title above.
- Don't truncate labels unless required — truncated text can impede comprehension.
- Offset the first scrollable tab **52dp** from the leading edge so it's clear more content is available.
- Avoid inconsistent padding on each tab; keep padding the same for scrollable tabs with long labels.
- Use globally recognized icons when using icons alone; use caution representing tab content with icons alone.
- Don't use tabs with both icons and text labels on only some tabs but not others.
- Avoid more than four tabs at once.
- Use different gesture directions when using tabs. Avoid placing swipeable items (interactive maps, list items) in the content area of a UI that has tabs — the user may mistakenly swipe the wrong component.
- Don't scroll tabs behind an app bar.
- Limit badge content to four characters including a "+".

### 10. Accessibility
- Users should be able to: undertake actions or invoke navigation to a new destination with assistive tech; select an action or destination from an **off-screen** tab with assistive tech; maintain access to primary actions when content is in a scrolled state.
- **Avoid applying density by default** — it lowers targets below the best practice of **48x48 CSS pixels**. Instead give people a way to choose higher density (a denser layout option, or changing the theme). Keep all targets used to change the density setting at a minimum of **48x48 CSS pixels** each so it can be easily reverted.
- It is **not recommended** to loop a tab set so it scrolls infinitely — this can trap users navigating linearly with a screen reader.
- Horizontal scrolling tabs meet accessibility requirements because they need to increase in width to respond to label text without affecting the layout, and horizontal scrolling is necessary to view those labels.
- **Initial focus**: on arrow/tab in a tab menu, the active indicator appears on the first interactive element; the user can then tab to additional interactive elements until all available items are complete.
- Keyboard: **Arrow** — focus lands on the next available navigation destination; **Space / Enter** — activates the focused navigation destination; **Arrow** — allows navigation through menu items. To select an individual tab, tap or press Space/Enter.
- **Don't use Space/Enter for navigating tabs** — Space/Enter is only used for completing actions. Use Arrow/Tab to navigate through items.
- Labeling: when visible UI text is ambiguous or absent, accessibility labels need to be more descriptive — e.g. an icon visually representing a "Video camera" gets the accessibility label "Video format media content".

---

## Gaps (specs referenced in these pages but whose values are not in the converted text)

> **Before treating a measurement here as unavailable:** many of these are published as
> `md.comp.*` values in the generated Compose token files, which are collected in
> [`component-tokens.md`](../component-tokens.md) — container heights and widths, shape
> assignments, elevation levels, icon sizes, and internal spacing. Check there first. Those are the
> Compose token values, so attribute them as such rather than as guideline text.


- No `md.sys.*` or `md.comp.*` token identifiers appear anywhere in these four files. All four "Tokens & specs" modules are interactive tables that did not convert (nav bar has two sets, switchable between the navigation bar and the nav items; nav rail has collapsed/expanded plus a separate baseline set; nav drawer has one token set; tabs has per-variant sets).
- No typography/type-scale role is named on any of the four pages (no type styles for label text, headline, section label, badge label, or tab label). Nav bar accessibility only states font *weight* cues: bold label when selected, medium label when unselected.
- Navigation bar: all dp values (container height for flexible vs baseline, item width/height, active indicator size and corner radius, icon size, paddings, margins from window edge, target size) live in images/tables only. Also missing: exact height difference of the "shorter" flexible bar; state-layer opacities are given (8%/10%) but not the baseline bar's state-layer values.
- Navigation bar XR: orbiter padding and measurement values (only 20dp adjacency margin and 12dp inset overlap are in text).
- Navigation rail: all dp values (collapsed/expanded container widths, item heights, active indicator height/width/corner radius, icon size, paddings, margins, baseline rail size measurements) live in images/tables only. Also missing: exact `Surface container` opacity/behavior when the container fill is "turned off".
- Navigation rail XR: orbiter padding/measurement values for both contained-FAB and spatialized-FAB rails.
- Navigation drawer: headline, section label, and badge label measurements; scrim opacity; state-layer opacities ("state specs are in the tokens module"); container shape for the modal variant (row absent from the modal table).
- Tabs: fixed vs scrollable container widths/min-max tab widths; hover/focus/pressed state-layer opacities; badge sizes (deferred to badge specs); tab minimum/maximum width values beyond "max width = width of widest tab".
- Badge color roles are deferred to badge specs (nav bar, nav rail); divider color roles deferred to divider specs (nav drawer).
- The "Availability & resources" section is empty in the conversion on **all four** pages (no platform availability matrix for nav bar, nav rail, nav drawer, or tabs).
