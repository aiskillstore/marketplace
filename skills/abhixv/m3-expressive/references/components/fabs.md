# FABs, Extended FABs, FAB Menu

Source: m3.material.io pages `fab`, `extended-fab`, `fab-menu`. Values below appear verbatim in those pages; anything absent is listed in Gaps.

---

## FAB (Floating action button)

### 1. What it is + when to use it vs. siblings
- Use a FAB for the most common or important action on a screen; it appears in front of all other content.
- FABs persist on the screen when content is scrolling.
- Three variants (variants are based on **size, not color**): FAB, medium FAB, large FAB.
- Size choice by visual hierarchy of the layout:
  - **FAB** — smallest size; best in **compact** windows where other actions may be present on screen.
  - **Medium FAB** — **most recommended**; recommended for most situations; works best in **compact and medium** windows. Use for important actions without taking up too much space.
  - **Large FAB** — useful in any window size when the layout calls for a clear and prominent primary action; best suited for **expanded and larger** window sizes, where its size helps draw attention.
- **Small FAB is no longer recommended** (still available). Use a larger size.
- vs. **extended FAB**: use the extended FAB when label text is necessary. A FAB can transform into an extended FAB on larger screens.
- vs. **FAB menu**: use a FAB menu when there are many kinds of actions relevant to the FAB; a FAB can transition into a FAB menu when selected.
- Actions a FAB promotes (important, constructive): Create, Favorite, Share, Start a process. A FAB can trigger an action on the current screen, or perform an action that creates a new screen.
- Avoid using a FAB for minor or destructive actions: Archive or trash; Alerts or errors; Limited tasks like cutting text; Controls better suited to a toolbar, like adjusting volume or font color.
- FABs are not needed on every screen — e.g. when images represent primary actions.

### 2. Anatomy
Two elements: **1. Container, 2. Icon**.
- **Container** — typically a square container. Must not be covered by other elements, such as badges. Must have sufficient color contrast with the surface it's placed on.
- **Icon** — clear and understandable. Use a **filled** icon instead of an outlined icon. On web, hovering over a FAB should display a **tooltip with an accompanying icon text label**. A FAB shouldn't contain notifications or actions found elsewhere on a screen.

### 3. Sizes / variants / configurations
| Variant | M3 | M3 Expressive |
|---|---|---|
| FAB | Available | Available |
| Medium FAB | -- | Available |
| Large FAB | Available | Available |
| Small FAB | Available | Not recommended. Use a larger size. |

Color configurations:
| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Color | Primary container, secondary container, tertiary container | Available as primary, secondary, tertiary | Available |
| Color | Primary, secondary, tertiary | -- | Available |

- FAB tokens are organized **by size and color**.
- Baseline token set covers only **small and surface FABs** (both no longer recommended); it excludes other colors and large/regular FABs, "since those are still currently used."
- Rationale for the rename: the primary/secondary/tertiary **set** colors were renamed to primary/secondary/tertiary **container** to match the actual color roles used, and **new** primary, secondary, and tertiary color styles were created to match the corresponding color roles.

### 4. Placement
- Alignment: the FAB can be aligned **left, center, or right**. It can be positioned **above the navigation bar, or nested within it**.
- **Compact and medium breakpoints**: best place is typically the **lower right corner** (bottom trailing edge) — easy to reach, less likely to cover important content.
- **Expanded breakpoints**: consider the **upper left corner**, like in the navigation rail — positions it as one of the first interactive elements people see.
- Size by context: **medium FAB for mobile layouts**, **large FAB for tablets and large screens**. FABs have multiple sizes that scale with the window size.
- A FAB can be used within a navigation component, such as a navigation rail.
- Individual components, such as cards, shouldn't have their own FAB.
- Avoid positioning the FAB so it **completely obscures the focus indicator** of an actionable element; partially covering is acceptable while focus indicators remain visible.
- Scroll: **FABs remain in place on scroll.** Extended FABs can collapse into a FAB on scroll and expand on reaching the bottom of the view.

### 5. States and interaction behavior
- States shown: **Enabled**, **Hovered (8% state layer) — elevation 4**, **Focused (10% state layer)**, **Pressed (10% state layer)**.
- **Don't disable the FAB.** If the action is unavailable, the FAB shouldn't appear.
- **Appearing**: expands outward from a central point; the icon within it can be animated as well. FABs aren't attached to the surface content appears on; they move separately from other UI elements because of their relative importance.
- **Screen transitions**: FABs can morph to launch related actions. When a screen changes its layout, the FAB should disappear and reappear during the transition.
- **Reappearance**: only reappear if relevant to the new screen; reappear in the same position, if possible.
- **Expanding**: can expand and adapt to any shape using a **container transform** transition pattern — including a surface that's part of the app structure, or one spanning the entire screen. Can also transition into a FAB menu.
- **Moving across tabs**: when tabs are present, the FAB should briefly disappear, then reappear when the new content moves into place (shows the FAB is not connected to any particular tab). **Don't animate the FAB with body content**; don't keep the FAB on screen when switching pages.

### 6. Color role mapping
Container + icon use a **color / on-color** pair. All six mappings give the same legibility and functionality — choice depends on style alone.
| Style | Container | Icon |
|---|---|---|
| Primary container **(default)** | primary container | on primary container |
| Secondary container | secondary container | on secondary container |
| Tertiary container | tertiary container | on tertiary container |
| Primary | primary | on primary |
| Secondary | secondary | on secondary |
| Tertiary | tertiary | on tertiary |

- **Surface** FAB color styles are still available but **no longer recommended**.
- **State layer color must match the icon color** for non-default mappings — e.g. the state layer for the **primary** style is `md.sys.color.primary`.
- FABs can use dynamic color.

### 8. M3 Expressive update (May 2025) — complete
"The FAB has new sizes to match the extended FAB and more color options. The small FAB is no longer recommended."

Variants and naming:
- Added **medium** FAB size.
- **Small** FAB size is no longer recommended.
- FAB and large FAB sizes are unchanged.
- FAB variants are based on size, not color.

Color:
- Added tone color styles: **Primary**, **Secondary**, **Tertiary**.
- Renamed existing tonal color styles to match their token names: **Primary → Primary container**, **Secondary → Secondary container**, **Tertiary → Tertiary container**. The values haven't changed.
- **Surface color FABs are no longer recommended.**

Differences from M2: M2 FABs are circles and always have a drop shadow. M3 FABs have a boxier shape, can use dynamic color, and include a new large FAB variation.

### 9. Do / Don't
- Do use a FAB for the most important action on a screen.
- Do make sure the icon in a FAB is clear and understandable; use simple icons such as add, message, or edit.
- Don't use confusing or open-ended icons to symbolize less common actions.
- Don't display multiple FABs on a single screen.
- Don't give individual components, such as cards, their own FAB.
- Don't cover the container with other elements such as badges.
- Don't use a FAB for minor, overflow, unclear, or destructive actions.
- Don't disable the FAB — remove it instead.
- Don't animate the FAB with body content across tab switches.

### 10. Accessibility
- With assistive technology, people must be able to: navigate to and activate the FAB; perform an action with the FAB; expand and minimize an extended FAB.
- Icon must have a **minimum 3:1 contrast ratio** with the container; avoid colors below 3:1.
- Container must have sufficient color contrast with the surface behind it.
- **Focus order**: prioritize the FAB. On mobile, focus order may start with the app bar, move to the navigation bar, then skip past other page content to land on the FAB. Consider displaying a **tooltip when the FAB is focused** (supported on web).
- Layout: for expanded breakpoints consider the **upper left region** for screen-reader reachability, but test placement with users across browser windows; for compact and medium breakpoints use the **lower right corner**.
- Don't completely obscure an actionable element and its focus indicator.
- Keyboard: **Tab** → focus lands on the FAB. **Space** or **Enter** → perform the default action on an item.
- Labeling: the accessibility label should describe the action the button performs, e.g. **Compose a new message**.

---

## Extended FAB

### 1. What it is + when to use it vs. siblings
- Use for the most common or important action on a screen.
- **Use instead of a FAB when label text is needed to understand the action**, or to add further emphasis to the button.
- Use on screens with **long, scrolling views that require persistent access to an action**, such as a checkout screen.
- Extended FABs are more prominent than regular FABs; effective where an icon alone is ambiguous — but the relationship between icon and label must be clear.
- The extended FAB can provide **more emphasis and clarity to a product's primary action**; use it to provide constant access to a primary action above long-scrolling surface content, or to emphasize a page's primary action.
- Only **one** extended FAB per screen (as with the regular FAB), because **multiple FABs compete for attention**. If additional high-level actions are required, add more buttons elsewhere on the page.
- **Don't use as an option in a set of actions** — use **filled buttons** for a similar level of emphasis instead.
- Not used with FAB menus: **don't open a FAB menu from an extended FAB**.
- Size choice: choose the size that adds the right amount of emphasis. In **compact** windows with one prominent action, the **large** extended FAB can be appropriate. In **larger window sizes**, use a **medium or large** extended FAB.

### 2. Anatomy
Three elements: **Container, Label text, Icon (optional)**.
- **Container** — a rounded rectangle that **hugs its contents**; grows and shrinks with text length.
- **Icon (optional)** — should intuitively represent the action. Unlike standard FABs, extended FABs don't require an icon; **an extended FAB can't have an icon without a text label**. LTR: icon left of label. RTL: icon right of label (mirror all elements).
- **Label text** — should clearly describe the action. Use **1–2 words at most**; localization may increase character count and width. Avoid wrapping or truncating text.

### 3. Sizes / variants / configurations
| Variant | M3 | M3 Expressive | Size |
|---|---|---|---|
| Small extended FAB | -- | Available | 56dp |
| Medium extended FAB | -- | Available | 80dp |
| Large extended FAB | -- | Available | 96dp |
| Extended FAB (baseline) | Available | **Not recommended.** Use **small extended FAB**. | 56dp |

Baseline extended FAB specs (the only measurement table in the source):
| Attribute | Value |
|---|---|
| Container height | 56dp |
| Container width | Dynamic, **80dp min** |
| Container shape | **16dp corner radius** |
| Icon size | 24dp |
| Padding | 16dp |

- Baseline configurations: **with icon** / **without icon**.
- Moving baseline → small extended FAB: type style updated from **label large** to **title medium**, and **inner padding was reduced**.
- Extended FAB tokens are organized **by size and color**. Baseline token sets are organized by common tokens, then by **surface** and **branded** color styles. Other color styles — **primary, secondary, tertiary** — are still used by the latest extended FABs.
- Margins: **extended FABs should have margins of 16dp** (baseline: "extended FABs have a padding of 16dp").

### 4. Placement
- Place the extended FAB **above the rest of the UI**, off of elements like app bars.
- **Compact and medium breakpoints**: place at the **bottom of the screen**, either **center-aligned** or **aligned to the trailing edge** of the window.
- **Expanded and larger window sizes**: either at the **bottom right edge of the window, in both LTR and RTL**, or **within the navigation rail** (can sit at the top of the expanded navigation rail).
- Responsive layout: FAB and extended FAB can transform into each other depending on available space and layout. **Collapsed navigation rail → FAB; expanded rail → FAB can transform into an extended FAB.**
- Must not sit on/next to:
  - **Don't place on top of toolbars** — it disrupts the consistency of the elevation and surface layers.
  - **Don't place in the upper half of a mobile screen** — it disrupts the reading of the UI.
  - **Don't place on cards or inside other containers** (e.g. a dialog).
  - **Avoid other floating components, like the floating toolbar, on screen with the extended FAB.** (Floating toolbars can be paired with FABs, but **not** extended FABs.)
  - Don't place over another actionable element.

### 5. States and interaction behavior
- States shown: **Enabled**, **Hovered — elevation 4**, **Focused**, **Pressed**. Baseline states: Enabled, Hovered, Focused, Pressed.
- **Appearing**: the surface **expands** when appearing on screen, using the **enter and exit** transition pattern.
- **Expanding**: can expand and adapt to any shape using the **container transform** transition pattern — a surface that is part of the app structure, or one that spans the entire screen.
- **Transforming**: can transform into a FAB on scroll to temporarily take up less space.
- **Scrolling**: transforms into a FAB when **scrolling down**, back to an extended FAB when **scrolling up**.
- FAB → extended FAB transition steps: (1) the FAB shape changes; (2) the FAB icon moves to the left; (3) the FAB text label fades in.

### 6. Color role mapping
Container + label/icon use a **color / on color** pair. All mappings provide the same level of contrast and functionality — choose based on visual preference.
| Style | Container | Icon / label |
|---|---|---|
| Primary container **(default)** | primary container | on primary container |
| Secondary container | secondary container | on secondary container |
| Tertiary container | tertiary container | on tertiary container |
| Primary | primary | on primary |
| Secondary | secondary | on secondary |
| Tertiary | tertiary | on tertiary |

- Baseline extended FAB roles: **primary container + shadow** (container), **on primary container** (icon), **on primary container** (label text). Baseline additional mappings exist for other container/icon combinations with equal legibility and functionality.
- **Surface / surface container** color styles are still available but **no longer recommended**.
- **State layer color must equal the icon color** for non-default mappings — e.g. primary mapping uses `md.sys.color.primary`.
- New color mappings and compatibility with **dynamic color** (difference from M2).

### 7. Typography role mapping
- Label text of the **baseline** extended FAB: **label large**.
- Label text of the **small** extended FAB: **title medium** (updated from label large).
- Expressive update: "each with updated type styles"; "Adjusted typography to be larger."

### 8. M3 Expressive update (May 2025) — complete
"The extended FAB now has three sizes: small, medium, and large, each with updated type styles. These align with the FAB sizes for an easier transition between FABs. The baseline extended FAB is no longer recommended and should be replaced with the small extended FAB. Surface and FABs are also no longer recommended."

Variants and naming:
- Added new sizes — **Small: 56dp**, **Medium: 80dp**, **Large: 96dp**.
- No longer recommended — **Baseline extended FAB (56dp)**, **Surface extended FAB**.

Updates:
- Adjusted typography to be larger.

Differences from M2:
- **Color**: new color mappings and compatibility with dynamic color.
- **Layout**: extended FAB is the **same height as the FAB**.
- **Shape**: boxier style with **smaller corner radius**.
- (M2: extended FABs are pill-shaped and have a different height and elevation. M3: extended FABs share the same height, boxier shape, and simpler elevation model as FABs.)

### 9. Do / Don't
- Do use an extended FAB when label text helps understand the main action.
- Do let the container hug its icon and text.
- Do shorten the label text as much as needed; include an icon for additional context.
- Do mirror elements in RTL languages.
- Don't use multiple extended FABs on one screen — it disrupts visual hierarchy.
- Don't use the extended FAB to convey an option in a set of actions.
- Don't show an icon without a text label.
- Don't wrap or truncate label text.
- Don't place it on toolbars, on cards/containers, in the upper half of a mobile screen, or over another actionable element.
- Don't pair it with a floating toolbar.

### 10. Accessibility
- With assistive technology, people must be able to navigate to and activate the extended FAB.
- Placement: consider the **upper left region of large web screens**, like an expanded navigation rail; in **smaller windows**, the **lower right corner**.
- Treat the **visible label and icon as one focusable element**. **No tooltip needed** — it already has a visible label.
- Focus order: prioritize the extended FAB. On mobile, focus order may start with the app bar, move to the navigation bar, then skip past other page content to land on the extended FAB.
- Keyboard: **Tab** → moves focus to the extended FAB. **Space** or **Enter** → activates the extended FAB.
- Labeling: use consistent icons and text labels (e.g. a **Compose** icon with a **Compose** text label); the icon + label combination should have one distinct purpose. The **accessibility label must include the same first word as the visible label** — visible **Create** → accessibility label e.g. **Create a new invite**.

---

## FAB menu

### 1. What it is + when to use it vs. siblings
- Opens from a FAB to show **2–6 related actions** floating on screen. Should always appear in the same place as the FAB that opened it.
- Makes actions immediately accessible and keeps the UI clean by concealing actions when not needed.
- **One FAB menu size for all sizes of FABs** — it can open from any sized FAB.
- **Not used with extended FABs.** Don't open a FAB menu from an extended FAB or any other component.
- **Don't use a FAB menu when the FAB is paired with other components**, like the floating toolbar or navigation rail — prevents cognitive overload and interface clutter. (FABs alone can be placed next to toolbars and other components.)
- Items should be closely related under a single action, like **Share**. Avoid grouping unrelated actions in the same FAB menu.
- Replaces the **speed dial** and **any usage of stacked small FABs**.

### 2. Anatomy
Two elements: **Close button** and **Menu item** (also called list item).
- **Close button** — takes the place of the original FAB; the FAB transforms into it.
- **Menu item** — must always have **label text**; icons shouldn't be removed since they make each item easy to identify (remove the icon only if necessary). The list item should always **hug its contents** and look consistent; avoid truncating text or setting fixed widths. **All FAB menu elements should be rounded.** Keep padding consistent between container↔icon, icon↔text, and text↔container.

### 3. Sizes / variants / configurations
| Variant | M3 | M3 Expressive |
|---|---|---|
| FAB menu | -- | Available |

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Color | Primary set, secondary set, tertiary set | -- | Available |

- **FAB menu items share the same measurements as the medium button specs.**
- **The close button should always be 56dp.**
- Item count: **2–6 items**.
- Tokens: one **common token set** plus **six color sets** — three for each element (close button and menu item).

### 4. Placement
- Align the FAB menu to the **trailing edge of the window**. In RTL, the FAB and FAB menu align to the **left edge** and element layout is mirrored.
- The FAB menu **animates from the top trailing edge of the FAB** to ensure a smooth animation. The close button and FAB **share the top trailing corner as an anchor and appear in the same place**.
- Margins: **the FAB should always have 16dp margins**; a FAB menu opened from a FAB has matching **16dp** margins.
- **Larger FABs place the FAB menu slightly higher, with larger margins underneath**, so the close button aligns to the top of the FAB:
  | Opened from | FAB margins | Close-button margin from bottom of screen |
  |---|---|---|
  | FAB | 16dp | 16dp |
  | Medium FAB | 16dp | 40dp |
  | Large FAB | 16dp | 56dp |
- **Large and extra large windows**: FAB and FAB menu margins increase from **16dp to 24dp**.
- Remain anchored to the same corner or edge regardless of window size.
- Pair with a FAB size suitable for the window size class — larger FABs are recommended for larger windows.
- **Web**: the FAB menu opens from the FAB and inherits its states and specs from the **baseline menu component** (a menu component, for consistency with other desktop apps). The **gap between the FAB and menu can vary, but 4dp is recommended**. Web states/specs shown: Enabled, Hovered, Selected.
- Avoid positioning the FAB menu to completely obscure the focus indicator of an actionable element; partially covering is fine while the focus indicator stays visible.

### 5. States and interaction behavior
- **Close button** states (light and dark): Enabled, Hovered, Focused, Pressed.
- **Menu item** states (light and dark): Enabled, Hovered, Focused, Pressed.
- Web: Enabled, Hovered, **Selected**.
- **Appearing**: the FAB should **transform into the close button**; menu items appear using the **enter and exit** transition. Originate the transition from one of the FAB's trailing corners, **preferably the top-aligned corner**.
- **Scrolling**: when window height is limited (e.g. phones in horizontal orientation), FAB menu items **can scroll**, and **items must scroll behind the close button**.
- **Expanding**: any FAB menu item can expand and adapt to any shape using the **container transform** transition pattern — including a surface that is part of the app structure or one spanning the entire screen.

### 6. Color role mapping
Twelve colors across the two elements, in three sets:
| Set | Roles listed |
|---|---|
| Primary | on primary container, primary container, on primary, primary |
| Secondary | on secondary container, secondary container, on secondary, secondary |
| Tertiary | on tertiary container, tertiary container, on tertiary, tertiary |

- **Contrasting close button and item colors**; supports dynamic color; compatible with any FAB color style.
- Pairing rule — use the color set that best matches the FAB color style:
  - **Primary** FAB menu set with **primary** or **primary container** FAB color styles.
  - **Secondary** set with **secondary** or **secondary container** FAB color styles.
  - **Tertiary** set with **tertiary** or **tertiary container** FAB color styles.

### 8. M3 Expressive update (May 2025) — complete
"The FAB menu adds more options to the FAB. It should replace the speed dial and any usage of stacked small FABs."

New component added to catalog:
- One menu size that pairs with any FAB.
- Replaces any usage of stacked small FABs.

Color:
- Contrasting close button and item colors.
- Supports dynamic color.
- Compatible with any FAB color style.

"The FAB menu uses contrasting color and large items to focus attention. It can open from any size FAB."

Differences from M2: M2 — the speed dial used small round FABs. M3 — the FAB menu uses dynamic color and a larger item size.

### 9. Do / Don't
- Do open the FAB menu from a FAB, in the same place as that FAB.
- Do keep items to 2–6, closely related under a single action.
- Do align to the trailing edge (mirrored in RTL).
- Do keep padding consistent and let list items hug their contents.
- Do let items scroll behind the close button on short screens.
- Don't use a FAB menu with one item.
- Don't open a FAB menu from an extended FAB or any other component.
- Don't use a FAB menu with a toolbar or navigation rail.
- Don't remove the label; only remove the icon if necessary.
- Don't expand container sizes (equal-width items despite different text lengths) or set fixed widths; don't truncate text.
- Don't change FAB menu shapes (e.g. square instead of round).
- Don't block an actionable element and its focus indicator completely.
- Don't obstruct the close button in short screens like horizontal orientation.

### 10. Accessibility
- With assistive technology, people must be able to navigate and interact with the FAB menu, and focus must be correct when navigating through the menu.
- **FAB menu elements meet the minimum target size of 48dp** — "48x48dp minimum width and sufficient spacing by default."
- When the FAB menu can scroll, make sure items scroll **behind** the close button: **the close button should always be easy to access and unobstructed.**
- Initial focus: when the FAB is selected the menu opens and **initial focus remains on the close button**, which takes the place of the original FAB; focus then moves **from the top menu item to the bottom** (focus order: close button → first menu item → second → third).
- Keyboard: **Tab** → navigate to the next interactive element. **Space** or **Enter** → activate the focused button or item.
- Labeling — **Android**, close button: it **must include a state so screen readers announce what action will occur when it's toggled**. Label **Toggle menu**; Role **Button**; State **Expanded or collapsed**.
- Labeling — **Android**, menu items: Label matches the item's UI text (e.g. **Reply all**); Role **Button**.
- Labeling — **Web**: a FAB menu is a combination of a FAB and a menu component; follow FAB and menu accessibility guidelines. The FAB's accessibility label should describe the menu the FAB will open.

---

## Gaps (specs referenced in these pages but with no value in the text)

> **Before treating a measurement here as unavailable:** many of these are published as
> `md.comp.*` values in the generated Compose token files, which are collected in
> [`component-tokens.md`](../component-tokens.md) — container heights and widths, shape
> assignments, elevation levels, icon sizes, and internal spacing. Check there first. Those are the
> Compose token values, so attribute them as such rather than as guideline text.

- FAB / medium FAB / large FAB **size and padding measurements** — each is only an image ("FAB size measurements", "FAB padding measurements", and the same pair for medium and large). No dp heights, widths, icon sizes, or padding values in text.
- **Corner radius / shape tokens** for FAB, medium FAB, large FAB, and for small/medium/large extended FABs — only the baseline extended FAB's 16dp corner radius is stated.
- **Icon sizes** for FAB, medium FAB, large FAB, and for the three extended FAB sizes — only the baseline extended FAB's 24dp icon is stated.
- Whether the extended FAB sizes 56dp / 80dp / 96dp are heights is not stated; the source lists them only as "new sizes."
- **Type styles for medium and large extended FABs** — the update says "each with updated type styles" and "typography larger," but only baseline **label large** → small **title medium** is given.
- **Typography role for FAB menu items / close button** — not stated.
- All **`md.comp.*` token names** for FAB, extended FAB, and FAB menu — the token tables ("Tokens & specs", "Baseline tokens & specs") did not convert; only `md.sys.color.primary` appears in text.
- Full **`md.sys.color.*` token strings** for each mapping — the source gives role names in figure captions, not token names.
- **State layer opacities** for the extended FAB and FAB menu states (FAB gives 8% hovered / 10% focused / 10% pressed; the others list state names only).
- **Elevation tokens/levels** other than "elevation 4" on hover for FAB and extended FAB.
- **FAB menu item measurements** — deferred to "the same measurements as the medium button specs," which are not in these pages; the "FAB menu size measurements" figure did not convert.
- **Extended FAB size/padding measurements** for small, medium, large — a single image ("Size and padding measurements of the small, medium, and large extended FABs"); reduced inner padding of the small extended FAB has no value.
- Baseline FAB (small / surface) token values and the "Availability & resources" sections (empty in all three pages).
