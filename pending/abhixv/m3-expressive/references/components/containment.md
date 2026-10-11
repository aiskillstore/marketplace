# M3 Containment — Cards, Carousel, Lists, Divider, Bottom sheets, Side sheets, Dialogs

Source: m3.material.io pages `cards`, `carousel`, `lists`, `divider`, `bottom-sheets`, `side-sheets`, `dialogs` (captured 2026-07-17). Color roles below are the role names as printed on the source diagrams; the pages do not spell out `md.sys.*` / `md.comp.*` token identifiers in text (see Gaps).

---

## Cards

### 1. What it is + when to use vs. siblings
- Container for related elements on **a single topic**; displays content **and** actions.
- Contents can be anything: images, headlines, supporting text, buttons, lists, and other components. Flexible layouts and dimensions based on contents.
- Entry point into deeper levels of detail or navigation (e.g. a music album, details on an upcoming vacation).
- Variant choice (elevated / filled / outlined) is **style alone** — "Each provides the same legibility and functionality."
- Separation from background, ordered: outlined (most) > elevated > filled (least). Elevated = drop shadow, "more separation from the background than filled cards, but less than outlined." Filled = "subtle separation… less emphasis than elevated or outlined." Outlined = visual boundary, "can provide greater emphasis than the other variants."
- Vs. lists: on compact-breakpoint small screens, **consider swapping cards for lists** (more compact display of images + text). Vs. carousel: if carousel items require a lot of text, "use a series of cards instead" (carousel page).
- Don't force content into cards when spacing, headlines, or dividers would create a simpler visual hierarchy.

### 2. Anatomy
Required: **container** only. All other elements optional. Common configuration = 6 parts: Container, Image, Button, Supporting text, Subhead, Headline.
- **Container** — holds all card elements; size determined by the space those elements occupy; **card elevation is expressed by the container**.
- **Content blocks** — contents grouped into blocks; content can have different levels of visual emphasis depending on importance; layouts vary to support content type. Blocks: headline, subhead, supporting text, media, actions.
- **Dividers** — separate regions in cards or indicate areas of a card that can expand. Full-width divider = content that can be expanded. Inset divider (doesn't run full width) = separate related content.
- **Media** — Thumbnail (avatar or logo); Image (photos, illustrations, other graphics such as weather icons); Video.
- **Text** — Headline: communicates the subject of the card (photo album name, article name). Subhead: smaller text such as an article byline or a tagged location. Supporting text: body content such as an article summary or restaurant description.
- **Actions** — Primary action area (whole card as one large touch target triggering an expanded detail screen); Buttons (e.g. **Learn more**, **Add to cart**); Icon buttons (e.g. **Save**, **Heart**, **Leave a 4-star review**); Selection controls (chips, sliders, checkboxes); Linked text (a link inside supporting text); Overflow menu.
- **Outlined variant only** adds an **Outline** element around the container.

### 3. Sizes / variants / configurations
Three official variants: **Elevated**, **Filled**, **Outlined** — "three official card variants" is itself listed as a difference from M2. Vs. M2, cards have **lower elevation and no shadow by default** (this M2 difference is stated for cards generally, not for the elevated variant specifically); among M3 variants, it is the elevated card that carries a drop shadow.

| Attribute | Value |
|---|---|
| Shape | 12dp corner radius |
| Left/right padding | 16dp |
| Padding between cards | 8dp max |
| Label text alignment | Start-aligned |

### 4. Placement
- Cards may be shown singly or grouped in collections: **grid**, **vertical list**, or **carousel / horizontal row**. Default grid can be customized in code into **staggered** or **mosaic** grids.
- Collections: cards are **coplanar by default** — same resting elevation unless picked up or dragged.
- **Filter/sort options should be placed outside the card collection**; if a collection can be filtered, the filter **must** apply to **each** card in the collection. Collections can be filtered in a variety of ways, including by date or alphabetical order.
- Overflow menus: typically **upper-right or lower-right corner** of the card.
- Adaptive: as cards scale across window size classes their position and alignment change; cards and their elements can align left, right, or center.
- Ergonomics: a horizontally-oriented card in a **compact** breakpoint may become a larger, **vertically**-oriented card in an **expanded** breakpoint, with more space for images and text.
- Visual presentation: begin adjustments with **spacing**; let lists, cards, images optimize space while filling the screen region suiting the breakpoint's ergonomic needs.
- Column-based layouts: mobile — cards stretch to the full screen width; **expanded** breakpoint — use multiple columns. Avoid extending UI elements across the screen; on larger screens rearrange groups of related cards into horizontal rows or carousels.
- Small screens (compact): consider swapping cards for lists; maintain controls, actions, and component-specific elements.
- When a card is picked up it appears **in front of all elements, except app bars and navigation**.

### 5. States and interaction behavior
- States for all three variants: **Hovered, Focused, Pressed, Dragged, Disabled**.
- Actionability model: a card is either a **non-actionable container** holding actions (buttons/links) **or** directly actionable with no buttons/links — never both ("avoid stacking actionable elements. An action shouldn't be placed on an actionable surface").
- Touch: tapping a directly actionable card produces a **touch ripple across the card**. Non-actionable cards **don't ripple** and have **no hover state**.
- **Expanding**: use the **container transform** transition pattern to reveal additional content; reserve for hero moments meant to be expressive.
- **Navigation**: use the **forward and backward** transition pattern between consecutive levels of hierarchy — simpler motion than container transform, suitable for common navigation transitions.
- **Swipe**: one swipe gesture per card, performable anywhere on that card; used to dismiss a card, or change its state (flagging, archiving). One swipe action per card only.
- **Pick up & move**: moves and reorders cards in a collection; **increase elevation** while moving.
- **Scrolling**: content taller than the max card height is **truncated and does not scroll**; reveal it by expanding the card's height. A card can expand beyond the max screen height, in which case **the card scrolls within the screen**, not internally. On **desktop**, card content can expand and scroll **within** the card.

### 6. Color role mapping
| Variant | Part | Role |
|---|---|---|
| Elevated card | Container | Surface container low |
| Filled card | Container | Surface container highest |
| Outlined card | Container | Surface |
| Outlined card | Outline | Outline variant |

Also: new color mappings and compatibility with **dynamic color** (vs. M2).

### 9. Do / Don't
- Do use a card to display content and actions on a single topic; make cards easy to scan for relevant, actionable information.
- Do place text and images so hierarchy is clearly indicated.
- Don't force content into cards when spacing, headlines, or dividers would create a simpler visual hierarchy.
- Don't place text or icons on images ("isn't recommended"); if necessary, ensure the image gives sufficient contrast to meet accessibility standards — add a **translucent scrim or bounding shape** beneath the text or icon.
- Do expand a card to reveal information; **don't scroll within a card** to reveal information (on mobile it could cause two scroll bars).
- Don't put swipeable content (image carousel, pagination) inside a card; swipe gestures must not cause portions of cards to detach.
- Don't let a moved card bump other elements out of the way.
- Do place filter/sort controls outside the collection.
- Do organize collections in a straightforward, easy-to-use manner.
- It isn't recommended to place menus on top of the card in the draggable state; if necessary, ensure the interaction can still be completed and the menu doesn't cover the card.

### 10. Accessibility
- People must be able to navigate to a card **and to the elements within a card**, and get feedback appropriate to input type.
- Any dragging/swiping interaction requires a **single-pointer alternative** (e.g. tap, or press-and-hold, opening a menu to change position in a list; the menu can also hold a delete action). Use containers like bottom sheets or menus for single-pointer options.
- Keyboard: focus indicator appears around actionable elements when tabbing. **Tab** moves between actionable card elements; for non-actionable cards Tab goes directly to the actionable buttons/links inside. **Space** or **Enter** performs the action or exposes a secondary action such as a menu; inside a menu, **Arrow** to move, **Space/Enter** to select, **Tab** to exit.
- Keyboard table: **Tab** → move to the next actionable element (directly actionable cards: move to next card container; non-actionable cards with actionable elements: move to next actionable element). **Space** or **Enter** → confirm action.
- Focus: all interactive card elements need a tab stop. Directly actionable cards **are** tab stops. Non-actionable cards are **not** tab stops, but every actionable element inside is, and all are visited before focus moves to the next card.
- Labeling: informative card contents are verbalized by screen readers; **hide purely decorative images from screen readers**. All actionable elements must receive both screen reader and keyboard focus. Directly actionable cards take the **button** or **link** role depending on use; non-actionable cards are pure containers and need **no role**. Example screen-reader order: Heading → Image → Body text → Primary button → Secondary button.

---

## Carousel

### 1. What it is + when to use vs. siblings
- Scrollable (horizontal or, full-screen, vertical) list of items containing **visual items like images or video**, plus optional label text. Items emphasize visuals; text is brief and adapts to item size.
- New in Material 3 (no M2 equivalent).
- Overview states **six layouts**: Multi-browse, uncontained, uncontained multi-aspect ratio, hero, center-aligned hero, full-screen. The Usage section lists **four** layouts (Multi-browse, Uncontained, Hero, Full-screen) and notes all of them can be centered, "though center-aligned hero is the most common centered carousel."

| Layout | Best used for |
|---|---|
| Multi-browse | Browsing many visual items at once (like photos), dynamic designs |
| Uncontained | Highly-customized or text-heavy carousels, stacked imaged and text, traditional carousel behavior |
| Hero | Spotlighting very large visual items (like a movie or featured app) |
| Center-aligned hero | Centered, large visual items |
| Full-screen | Vertically-scrolling video or image feeds, immersive experiences |

- If items require a lot of text: use the **uncontained** layout or **cards** instead.
- Only use **uncontained multi-aspect ratio** if items have various widths.
- "Choose the best carousel layout for your product. Some layouts are more visual-focused, while others are more customizable."

Per-layout usage guidance:
- **Multi-browse** — best for browsing many items at once (photos, event feeds). **Snap-scrolling is recommended** so items stay recognizable and consistently sized. On larger screens more large and medium items are visible. Avoid if items need lots of text or have complicated imagery.
- **Uncontained** — most similar to a **traditional carousel**: items are a **single size** and flow past the edge of the screen. **Both default scrolling and snap-scrolling work well** with this layout. Because items don't change size, it can be customized to show more text or other UI **above or below each item** without the text being masked or cropped.
- **Uncontained multi-aspect ratio** — same layout as uncontained but with items of various sizes.
- **Hero** — best for spotlighting content that needs more attention (movies, shows, other media thumbnails). Highlights one large image to focus on **while providing a sneak peek of what's next**; use snap-scrolling so people can cycle through items one at a time.
- **Full-screen** — best for immersive experiences (video articles, featured headlines, visually rich items). **Can contain text and other UI elements on top of the image.**
- When the large item's max width is **narrow enough, more items can be shown on screen at once**; in compact windows this is only recommended for carousels with **simple imagery**.

### 2. Anatomy
Elements: **Container**, **Large carousel item**, **Medium carousel item**, **Small carousel item** (4 elements; hero = 3: container, large, small; uncontained/full-screen = container + large item; uncontained multi-aspect ratio = container + items at 16:9, 9:16, 1:1, 3:4).
- **Container** — holds all items; a rectangle, usable many ways and stretchable to any size; number of visible items varies with layout and breakpoint.
- **Carousel items** — hold content; **no fixed width**; width changes with window size or position in the layout. Three dynamic widths: **large, medium, small**. Large items have an adjustable max width that changes how all other large/medium/small items fit; they must stay big enough to be easy to understand and recognize. Medium items adjust width dynamically to carousel size and available space. Small items: **40–56dp**.
- **Item text (optional)** — brief; adapts dynamically to container and window size; text must remain understandable at each size; use brief labels on smaller items. Example progression: large item shows full title + label; medium hides the title; small abbreviates the label.

### 3. Sizes / variants / configurations
Carousel item dynamic widths: all items adapt to container width. Large items have a **customizable maximum width**. Small items: **min 40dp, max 56dp**. Items change size as they move through the layout. Uncontained multi-aspect ratio item widths range **9:16 (min width) to 16:9 (max width)**.

**Multi-browse** — shows at least one large, one medium, one small item.

| Attribute | Value |
|---|---|
| Alignment | Vertically centered |
| Leading/trailing padding | 16dp |
| Top/bottom padding | 8dp |
| Padding between elements | 8dp |
| Large item width | Dynamic, or user-set |
| Medium item width | Dynamic |
| Small item width | 40–56dp, dynamic |
| Item corner radius | 28dp |

**Uncontained** — items scroll to the edge of the container.

| Attribute | Value |
|---|---|
| Alignment | Vertically centered |
| Leading padding | 16dp |
| Top/bottom padding | 8dp |
| Padding between elements | 8dp |
| Item corner radius | 28dp |

**Uncontained multi-aspect ratio** — items of various widths; leading padding only, 8dp between items.

| Attribute | Value |
|---|---|
| Alignment | Vertically centered |
| Leading padding | 16dp |
| Top/bottom padding | 8dp |
| Padding between elements | 8dp |
| Item corner radius | 28dp |

**Hero** — at least one large item and one small item.

| Attribute | Value |
|---|---|
| Alignment | Vertically centered |
| Leading/Trailing padding | 16dp |
| Top/bottom padding | 8dp |
| Padding between elements | 8dp |
| Large item width | Dynamic |
| Small item width | 40-56dp, dynamic |
| Item corner radius | 28dp |

**Center-aligned hero** — at least one large item and **two** small items; adds an additional previewed item on the leading edge so the large item is centered.

| Attribute | Value |
|---|---|
| Alignment | Vertically centered |
| Leading/Trailing padding | 16dp |
| Top/bottom padding | 8dp |
| Padding between elements | 8dp |
| Large item width | Dynamic |
| Small item width | 40-56dp, dynamic |
| Item corner radius | 28dp |

**Full-screen** — one edge-to-edge large item; fills the window edge-to-edge.

| Attribute | Value |
|---|---|
| Alignment | Centered |
| Leading/Trailing padding | 0dp |
| Top/bottom padding | 0dp |
| Padding between elements | 16dp |

### 4. Placement / responsive
- Layouts can be **start-aligned or center-aligned**.
- Carousel items **must be fully visible on-screen**, except in the uncontained layout.
- As container size increases, the number of simultaneously visible items increases; items scale in size. **Compact** breakpoints: comfortably up to **three** items at once. **Full-screen** carousels only ever show **one** item.
- Multi-browse: on larger screens more large and medium items are visible. In **compact** windows show up to **three** items **if they have text**; more than three only if images/content are easy to understand and recognize.
- Hero: on larger screens more large items are visible; in compact windows show one large item and one small item.
- Full-screen: works best with content taller than wide, scrolls **vertically**; only works in **portrait** orientation in **compact and medium** windows. Don't use in landscape.
- Accessibility UI placement: place **Show all** button **below** the carousel (padding **4dp**); or, with a header, an arrow icon button **directly next to the header or in the same row**, arrow icon size **48dp**, header aligned to the leading edge. Never inside or beside the carousel container, never covering it — buttons go above or below.

### 5. States and interaction behavior
- States: **Enabled, Hovered, Focused, Pressed, Disabled**.
- Shape morph: dynamic carousel items **change shape when scrolled**; tapping an item **changes the shape slightly** plus a touch ripple.
- Motion: items move at a different speed than their content → **parallax effect** when scrolled.
- Interaction: scrolled items **snap into place to maintain the same layout**. Hero carousels swipe through **one item at a time**; multi-browse carousels scroll through **many items at once**.
- Two scroll behaviors: **Default** — no snapping, items can stop anywhere in the container; recommended **only for uncontained**. **Snap-scrolling** — items align to the layout grid when released; use for **multi-browse, hero, and full-screen**. Full-screen **must** use snap-scrolling and items must snap to the container edges.
- Cursor: hover state signals interactivity; clicking (in both active and inactive states) produces a ripple.
- **Reduced motion**: remove the parallax effect; items no longer expand as they come into view; **all items are the same size**; ensure carousels reach the window edges to avoid clipping visuals. For **hero** carousels with reduced motion, the small item is only **partially** shown on screen.

### 6. Color role mapping
Roles used in light and dark schemes: **Container**, **Surface**.

### 8. Updates (page's own update section)
- **November 2025** — new carousel layout: **Uncontained multi-aspect ratio**.
- **2023** — additional layouts and configurations: Uncontained, Full-screen, Centered carousels, Hero carousel layout, Multi-browse layout.
- Research: two studies (quantitative + qualitative), **over 200 participants**, five carousel designs. Findings: carousels are a good way to explore many kinds of content; a **previewed or squished item strongly indicated more content to swipe through**; participants expected **around 10 items** in a carousel that scrolled multiple items at once; all designs were considered similarly usable though some contexts suited some designs better.

### 9. Do / Don't
- Do set the large item size so images and text are easy to read and recognize. Avoid items so small the image isn't recognizable.
- Avoid multi-browse if items need lots of text or have complicated imagery.
- Avoid exceeding **two lines of text** in carousel items in compact windows unless the background is simple, like a single color.
- Don't use default scrolling for full-screen; don't let full-screen items scroll freely or stop halfway.
- Don't use full-screen layout in landscape orientation.
- Avoid customizing the accessibility solution; if needed, add a **Show all** in nearby navigation or alternative control buttons close to the carousel.
- Avoid adding UI elements like arrows or icons within or beside the carousel; don't cover the carousel with buttons or other UI.

### 10. Accessibility
- Users must be able to: navigate to the carousel container; navigate between items; activate an item; **skip over** the items.
- On **vertically-scrolling pages**, carousels require an accessible way to view all items **without horizontal scrolling** (does not apply to full-screen carousels). Recommended: a **Show all** button below the carousel opening a dedicated vertically-scrolling page of all items; with a header, an arrow icon button instead. The header must also appear on the all-items page.
- Initial focus: **Tab** places initial focus on the **first carousel item** (not the container — "Avoid focusing on the carousel container"). Then Tab or arrow keys navigate items. **Up/down arrows leave the carousel** and focus the next element on the page, e.g. the Show all button.
- Keyboard: **Tab** or **Arrows** → move to previous/next item. **Space** or **Enter** → activate the focused item.
- Labeling: the carousel container has the **container** role; the item label reads out the **total number of items and the current item in focus**.

---

## Lists

### 1. What it is + when to use vs. siblings
- Vertical groups of text, icons, images, and other elements optimized for reading comprehension. Use lists to **help people find a specific item and act on it**, and for communicating or selecting discrete items (e.g. choosing from a set of colors).
- Order items in logical ways (alphabetical, numerical); keep items short and easy to scan; show icons, text, and actions in a **consistent format**.
- A list item **can contain multiple actions at once** — selection, icon buttons, overflow menus, and more.
- Lists are "a compact composition of images, text, and actions"; cards and carousels use the same elements but take **more space** — on large screens consider swapping a list to a similar-purpose component; a list may transform into a **carousel** in expanded windows, or into **cards** on tablet/desktop.
- Choose between **standard** and **segmented** styles (a purely visual choice, no behavior change).

### 2. Anatomy
Required: **container** and **label text**. All others optional. 10 elements: Container, Overline, Label text, Trailing text, Supporting text, Trailing icon, Divider, Leading avatar, Leading icon, Leading media (image or video). (Guidelines anatomy lists the same set with: Container, Label text, Supporting text, Trailing text, Trailing icon, Trailing selection control — checkbox, radio button, switch, Leading avatar container, Leading avatar text, Leading icon, Leading media — image or video.)
- **Container** — holds all list items and their elements. **List item size is determined by the tallest element within the list item.** When an item features an image, consider customizing the container color to a **content-based color scheme**, applied to the enabled state or to an interaction.
- **Label & supporting text** — keep label text brief; limit supporting text to **one to three lines**; truncate supporting text depending on screen size. Label text only: single line; can wrap or be truncated. Label + supporting text: both can wrap or be truncated.
- **Leading icon** — quick visual cue relating to the item's label text, helping people scan.
- **Trailing icon** — communicates status or indicates an action, like **Show more**.
- **Leading media** — avatar, image, or video; anchored to the **leading edge**. Leading video thumbnails can open a video player or play within the list. Avatars: circular or expressive shapes for a person/entity; **square or rectangular** images for other content (products, videos).
- **Trailing text** — supplemental meta-information: price, count, date.
- **Selection controls** — at the leading or trailing end: checkboxes for multiple selection, switches to toggle settings on/off, radio buttons for single selection.
- **Gaps & dividers** — use **gaps** for contained lists (leveraging expressive shape and containment tactics); **limit dividers to uncontained or complex lists**, only when stronger visual separation is necessary.
- **Slots** (expressive): container with three slots — **leading, content, trailing**. Leading and trailing slots **must be a smaller width than the content section**; the content slot must be the largest and sits in the middle.
  - Leading slot: visual elements (avatar, icon, image, video thumbnail); selection controls (checkbox, radio button, switch); customizations (badge or larger image).
  - Content slot: default content (label text, supporting text); optional add-ons (badge, icon, in-line label, or more text elements); avoid long lines of text.
  - Trailing slot: action elements or text (icon, icon button, trailing text); selection controls (checkbox, radio button, switch).
  - Caution: slots require custom code implementation you must create and maintain. Slots are **not accessible by default**.

### 3. Sizes / variants / configurations
Variants: **List (expressive)** and **List (baseline)**.

| Variant | M3 | M3 Expressive |
|---|---|---|
| List (expressive) | -- | Available |
| List (baseline) | Available | Available |

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Styles | Standard | Available | Available |
| Styles | Segmented | -- | Available |
| Selection modes | Single-action, multi-action, single-select, multi-select | Available | Available |
| Interactions | Expand | Available | Available |

- **Expressive list**: segmented style and **round corners**; more flexible styling, highlighted selection states, customizable slots.
- **Baseline list items**: square corners and standard colors; still work in existing products but lack the latest visual style, selection treatment, and slot functionality.
- Heights (from M2→M3 baseline differences): the tallest element in a list item determines item height — **56dp, 72dp, or 88dp**.
- Alignment rule: elements are **middle-aligned** in most cases; if a list is **88dp or larger, or contains three or more lines of text, elements are top-aligned**.
- Token sets: **common** (baseline tokens plus new expressive shapes and sizes) and **expand** (tokens for the expand interaction). Baseline list tokens live in the **common** set.

**Baseline list layout measurements** (one-, two-, three-line layouts documented):

| Attribute | Value |
|---|---|
| Label alignment | Center |
| Label alignment when height is 88dp or taller | Top |
| Label left padding | 16dp |
| Leading element alignment (vertical) | Center |
| Leading element alignment (vertical) when height is 88dp or taller | Top |
| Leading element left padding | 16dp |
| Leading icon alignment (vertical) | Top |
| Leading icon top padding | 8dp |
| Leading icon top padding when height is 88dp or taller | 12dp |
| Trailing element alignment (vertical) | Center |
| Trailing element alignment (vertical) when height is 88dp or taller | Top |
| Trailing element left padding | 16dp |
| Trailing element right padding | 24dp |
| Padding above/below divider | 0dp |
| Targets | 48dp |
| Divider full-width | 100% |
| Divider inset left padding | 16dp |
| Divider inset right padding | 24dp |

Baseline configurations documented at 1-, 2-, and 3-line each: leading avatar (± trailing checkbox); leading image or thumbnail (± trailing checkbox); leading video (± trailing checkbox); leading icon (± trailing checkbox); text-only (± trailing checkbox); leading checkbox (± trailing text); leading radio button (± trailing text); trailing switch (and leading icon + trailing switch).

Icon button height in a list item is **dynamic and automatically adjusts to fill the list item height**.

### 4. Placement / adaptive design
- Place supporting visuals and primary text in the **same position in each list item**; don't vary element positions within a list. Any element can be used to anchor and align list item content.
- Primary action takes up the majority of the space in the **leading and content** positions; supplementary actions (bookmark, menu) go in the **trailing** position. Use spacing to draw attention to the most important aspect, usually the primary action area or key content. Align content by importance: more distinguishing content leading, less distinguishing trailing.
- Line length: ideal **40 to 60 characters**; large screens can accommodate **up to 120 characters** per line; near 120 characters, consider increasing **line height**. In fluid layouts change margins and typography properties as the container scales.
- Adapt the list container width based on line length, or switch to a **multi-column** layout.
- Lists can **change their layout to adapt to different window sizes**, affecting the size and placement of content — e.g. a list in a compact window can adjust **margins, spacing, or density** to better fit an expanded window.
- **Compact window**: lists should extend **edge-to-edge**; selecting an item opens a page with the details. Reduce the amount of information shown.
- **Medium & expanded**: display primary and secondary content in the same view — e.g. **list-detail** side-by-side; a compact-window list can become a **two-column** layout in an expanded window; items can reveal supporting text in expanded windows; larger imagery and longer descriptions.

### 5. States and interaction behavior
- Default list item states: **Enabled, Disabled, Hovered, Focused, Pressed, Dragged**. Selected list item states: **Enabled, Disabled, Hovered, Focused, Pressed, Dragged** (baseline list: same six).
- The **selected state applies to the entire list item** — e.g. when an item with a checkbox is selected, both the list item and the checkbox show a selected state.
- A list can have **only one selection mode at a time** (a single-action list can change to a multi-select list but can't be both at once).
  - **Single-select**: use a single-selection component such as a radio button. Doesn't support multi-actions; can't have secondary nested actions; **shouldn't use checkboxes**.
  - **Multi-select**: multiple items toggled on. Pairs well with checkboxes and switches; can't have secondary nested actions; **shouldn't use radio buttons**.
  - **Single-action**: the entire item performs one action, e.g. navigating to a new page. Can't have secondary nested actions; can't be toggled into a persistent selected state.
  - **Multi-action**: items include a primary action and one or more secondary actions; supports multiple nested actions.
  - **Non-interactive**: organizes information scannably; performs no actions and can't be selected.
- Selection lists: use **only one selection interaction per list item**.
- **Expand & collapse** (Android): items containing other list items expand/collapse folder-like; tapping expands the item **vertically across the entire screen** using a **container transform** transition pattern (parent-child transition).
- Touch: tapping a list item produces a **touch ripple**. Cursor: hover state signals interactivity; selected state shows colored fill.

### 6. Color role mapping
Expressive list roles (10, light and dark themes, in diagram order): **Surface, On surface variant, On surface, On surface variant, On surface variant, On surface variant, Outline variant, Primary container, On primary container, On surface variant**.
Baseline list roles (9, light and dark themes, in diagram order): **Surface, On surface, On surface variant, On surface variant, On surface variant, Outline variant, Primary container, On primary container, On surface variant**.
New color mappings and dynamic-color compatibility vs. M2.

### 8. M3 Expressive update (verbatim-faithful)
> "Lists have a new segmented visual style, improved selection treatment, and support for slots."
> **December 2025**
> Variants: Added **expressive** list — Recommended for new designs. List (baseline) is still available.
> New visual styles: Standard or segmented; Highlighted selection states; Flexible slots.
> Supported platforms: Android Views (MDC-Android); Jetpack Compose.
> "Expressive lists feature improved selection states."

Also: "In M3 Expressive, baseline lists are still available to use, but don't have the latest visual style, selection treatment, and slot functionality." "The baseline list variant is available and continues to work in existing products. However, the expressive list variant is recommended for new designs."

### 9. Do / Don't
- Do keep label text brief; limit supporting text to one to three lines.
- Do place supporting visuals (thumbnails) at the leading edge of a row to improve scannability. **Avoid placing visuals in the center of a row** — it makes the list difficult to scan.
- Don't vary the position of elements within a list.
- Do use an expressive, circular avatar for a person or entity; use square/rectangular images for other content.
- Do use gaps for contained lists; **limit dividers to uncontained lists**. Use **segmented gaps with filled list items** to define a list group.
- Don't use multiple selection interactions in one item.
- Don't scale components without adjusting other affected areas of the screen, such as text length.
- Reserve slots for use cases that maintain the list's accessibility and functionality.
- Don't add interactive elements that make the list item difficult to navigate, especially for screen reader users.
- Don't rely on color as the only cue for selection.

### 10. Accessibility
- People must be able to navigate to a list item and select a list item.
- **Indicate selection with more than color** — add radio buttons/checkboxes, leading or trailing icons, or a non-color visual style such as underlined text. Use **two** visual cues (e.g. leading checkmark plus filled color).
- Slot accessibility: elements must follow list rules, structure, and interaction patterns; **use standard list item padding**; **target size at least 48x48dp**; don't add interactive elements that impede navigation.
- Baseline measurement: **Targets 48dp**.
- Focus — single-action lists: the **first** element always receives focus unless the list has a **selected** element, in which case focus goes to the selected item. After focus, arrow keys navigate within the list. All items must be activatable via **Space** or **Enter**.
- Focus — multi-action lists: the item as a whole isn't selectable, only the individual actions. **Tab** to the list item focuses the first element; **Up/Down/Left/Right** arrows move between all focusable elements; **Space/Enter** activates. If focus is on an item's first action, **Up/Left** move focus back to the **last action of the previous item**; **Down/Right** move to the next action or the first action of the next item.
- Keyboard navigation table: **Tab** → move focus to the first list item, last list item, or outside the list component. **Down/right arrows** → next element; wraps back to the top from the last. **Up/left arrows** → previous element; wraps back to the bottom from the first. **Space** or **Enter** → select a list item not yet selected.
- Labeling: the accessibility label for a list item is typically the same as its **label text** and **supporting text**.

| Trait | Web | Android Views (MDC-Android) | Jetpack Compose |
|---|---|---|---|
| Aria label (single-select) | Container label: should describe selection type. List item: should match the visible label text | List item: should match the visible label text | List item: should match the visible label text |
| Role (single-select) | Container: List box; List item: Option | List item: Radio button | List item: Radio button |
| State (single-select) | Selected or Not-selected | Checked or Not-checked | Checked or Not-checked |
| Aria label (multi-select) | Container label: should describe selection type. List item: should match the visible label text | List item: should match the visible label text | List item: should match the visible label text |
| Role (multi-select) | Container: List box; List item: Option | List item: Checkbox | List item: Checkbox |
| State (multi-select) | Selected or Not-selected | Checked or Not-checked | Checked or Not-checked |

- On web, the list container's accessibility label describes the type of selection possible; role is **List box**. On Jetpack Compose the role applies to the **list item as a whole**; if a list isn't selectable, the label text is read out with no role. On Android Views (MDC-Android), contained components (checkbox, radio button) are labeled per their own component guidelines — label and role are applied to the interactive component by default.

---

## Divider

### 1. What it is + when to use vs. siblings
- A divider is a **simple line** used to visually group components and create hierarchy; can also imply nested parent/child relationships.
- **Only use dividers if items can't be grouped with open space.** Use dividers to **group things, not separate individual items**. Make dividers **visible but not bold**.
- Vs. gaps (lists page): gaps for contained lists; dividers limited to uncontained or complex lists when stronger visual separation is necessary.
- Two ways: **Full width** and **Inset**. Plus a **Vertical divider** configuration (new vs. M2).

### 2. Anatomy
One element: **Divider** (a simple line).

### 3. Sizes / variants / configurations

| Attribute | Value |
|---|---|
| Divider full-width | 100% |
| Divider inset left margin | 16dp |
| Divider inset right margin | 0dp |
| Divider middle-inset left margin | 16dp |
| Divider middle-inset right margin | 16dp |
| Space between divider & supporting-text | 4dp |
| Divider right margin | 8dp |
| Divider bottom margin | 8dp |

(Dialogs page: divider height **1dp** in both basic and full-screen dialogs. Lists page: divider full-width 100%; divider inset left padding 16dp; inset right padding 24dp; padding above/below divider 0dp.)

### 4. Placement
- **Full-width dividers**: separate larger sections of **unrelated** content; usable directly on a surface or inside other components like cards or lists; can separate **interactive from non-interactive** areas; group visual elements and indicate relatedness from an interaction perspective.
- **Inset dividers**: separate **related** content within a section; **equally indented from both sides of the screen by default**; should be used with anchoring elements such as icons or avatars, and align with the leading edge of the screen. Can be placed mid-layout to separate elements such as body text from selection chips.
- Using both on one screen: they must reinforce the hierarchy of information — **full-width for a different kind of content, inset for nested content items**.
- **Vertical divider**: arranges content on a **larger screen**, e.g. separating paragraph text from video or imagery media.
- In cards: full-width divider = content that can be expanded; inset divider = separate related content.
- In bottom sheets: dividers separate related content. In side sheets: separate action buttons from content, and user-generated from system-generated content.

### 6. Color role mapping
Divider (light and dark schemes): **Outline variant**. New color mappings and dynamic-color compatibility vs. M2.

### 9. Do / Don't
- Make dividers visible but not bold.
- Only use dividers if items can't be grouped with open space.
- Use dividers to group things, not to separate individual items.
- **Use full-width dividers sparingly** — too many divider lines make an interface look cluttered.
- Don't add a divider after every piece of content on a page.
- List items with repetitive formats may not require an inset divider — using only the margin between items is acceptable.

### 10. Accessibility
Dividers are **decorative elements, which have no contrast minimums**.

---

## Bottom sheets

### 1. What it is + when to use vs. siblings
- Displays **supplementary content and actions** on a mobile screen. **Use bottom sheets in compact and medium window sizes.**
- Content should be **additional or secondary — not the app's main content**. Bottom sheets can be dismissed in order to interact with the main content.
- Two variants: **standard** and **modal**.
  - **Standard** — co-exists with the screen's main UI region; allows simultaneously viewing and interacting with both regions, especially when the main UI region is frequently scrolled or panned. Use for content that complements the screen's primary content, e.g. an audio player in a music app. Standard sheets can also hold **supplementary content that continues below the screen**, such as location information over a map.
  - **Modal** — like dialogs, appears in front of app content, **disabling all other app functionality**, and remains on screen until confirmed, dismissed, or a required action is taken. Use as an alternative to inline menus or simple dialogs on mobile, especially for a long list of action items, or items that require longer descriptions and icons. **Modal bottom sheets are used in mobile apps only.**
- On larger expanded window sizes (desktop) a bottom sheet can be **swapped for a side sheet** with similar content. For more complex tasks and flows, consider a **non-transient surface such as a floating sheet**.
- Modal bottom sheets are above a **scrim**; standard bottom sheets have **no scrim**. "Besides this, both variants of bottom sheets have the same specs."

### 2. Anatomy
3 elements: **Container**, **Drag handle (optional)**, **Scrim (modal only)**. Container is the only required element; layouts can vary widely.
- **Container** — holds all elements; size determined by the space those elements occupy; flexible, adapts to content and available space.
- **Drag handle (optional)** — draggable/selectable affordance for changing sheet height; accessible **48dp hit target**.
- **Scrim** — modal only.
- Optional contents: **List items** (continuous group of text or images; can include label text, icons, text buttons, among other elements); **Dividers** (separate related content); **Media** — Thumbnail (avatar or logo), Image (photos, illustrations, other graphics such as weather icons), Video. Also menu items in list or grid layouts, actions, supplemental content.

### 3. Sizes / measurements
Shape: **28dp top corner radius**. Max-width **640dp** (new vs. M2), plus an optional drag handle with an accessible **48dp** hit target.

| Attribute | Value |
|---|---|
| Drag handle alignment (horizontal) | Center |
| Drag handle padding top/bottom | 22dp |
| Top margin | 72dp |
| Top margin (window width > 640dp) | 56dp |
| Start/end margin (window width > 640dp) | 56dp |
| Width | Full width, up to max-width 640dp |
| Height | Variable |

"Bottom sheets span the full window width up to 640dp. When the window width exceeds 640dp, bottom sheets adjust to have a top margin of 56dp and side margins of 56dp."

### 4. Placement / responsive layout
- **Compact window size** (mobile): bottom sheets **extend across the width of the screen** and are elevated above the primary content.
- **Medium and expanded window sizes**: a default **max-width** prevents undesired layouts and awkward spacing; **can be overridden if needed**.
- **Expanded (desktop)**: swap for a side sheet.
- **Modal visibility**: initial vertical position is **capped at 50% of the screen height** to provide access to top actions. Modal sheets whose contents exceed 50% can then be pulled across the full screen and **scrolled internally** to reach the remaining items.
- At **full-screen height, standard bottom sheets contain a collapse icon in an app bar** to return to their initial position. Standard sheets can have **preset positions from full-screen height to preview**.
- Display a **close affordance in a full-screen modal bottom sheet**.

### 5. States and interaction behavior
- **Expansion**: sheets can be fully raised and toggled between **collapsed and expanded** states, giving a more predictable footprint; set by the system or toggled by the user.
- **Custom positioning**: the drag handle can be **dragged or selected** to change height. Sheets should cycle through **preset heights** and **close completely without dragging**. Selecting the drag handle toggles through preset heights or closes the sheet; **selecting the scrim always closes** the bottom sheet. If the sheet has multiple preset heights but can't use a drag handle, **Material requires a single-pointer alternative** to change height. A sheet can automatically resize to another height after interacting with the drag handle.
- **Scrolling**: bottom sheets can be **horizontally scrolled**, independent of the rest of the screen's content; should be scrollable when content exceeds the initial viewable height.
- **Dismissal (modal)**: appears when triggered by a user action, such as tapping a button or an overflow icon. Dismissed by: tapping a menu item or action within the sheet; tapping the scrim; swiping the sheet down; using a close affordance in the sheet's app bar, if available.
- **Back (Android predictive back)**: swipe left or right on the bottom sheet — the sheet **detaches from the left and right edges** of the screen to signal it will close, and the previous screen is revealed in a preview. Gesture outcomes: preview of the result, **release to commit**, **fling to commit**, **cancel**.

### 6. Color role mapping
Roles used for both light and dark schemes: **Scrim\*** (scrim), **On surface variant** (drag handle), **Surface container low** (container). \*On Android platforms, the scrim color and opacity are automatically handled by the system UI. New color mappings and dynamic-color compatibility vs. M2.

### 9. Do / Don't
- Use bottom sheets in compact and medium window sizes; keep content additional or secondary.
- Modal bottom sheets: mobile apps only.
- Don't exceed 50% of screen height for a modal sheet's initial vertical position.
- Display a close affordance in a full-screen modal bottom sheet.
- Bottom sheets should extend to the width of the screen on mobile.
- Include a single-pointer alternative for any action completable by dragging.
- If a drag handle can't be used, add a **button** to cycle preset heights.

### 10. Accessibility
- Users must be able to **resize bottom sheets without relying on touch gestures**.
- Touch target: the **top 48dp portion** of the bottom sheet is interactive when user-initiated resizing is available and the drag handle is present.
- Initial focus: the optional **drag handle can be focused in the tab order** and interacted with via non-touch inputs such as keyboard or switch controls.
- Keyboard: **Tab** → focus lands on drag handle. **Space / Enter** → toggles between available heights.
- Labeling: **label only the drag handle**; its accessibility role is **"button."**

---

## Side sheets

### 1. What it is + when to use vs. siblings
- Provide **optional content and actions without interrupting the main content**. People can navigate to another region within the sheet; side sheets can contain a **back icon** for navigation.
- Two variants: **standard** and **modal**.
  - **Standard** — supplementary surfaces used **mostly in medium to expanded breakpoints** (tablet, desktop). Consistent, predictable surface for contextual actions and information; display content complementing the primary content and **remain visible while people interact with primary content**. Common uses: a list of actions affecting the primary content (such as filters); supplemental content and features.
  - **Modal** — **preferred in compact breakpoints** (mobile) due to limited screen size. Can display the same kinds of content as standard side sheets but **must be dismissed in order to interact with the underlying content**.
- Modal side sheets on smaller screens can **transition to standard side sheets at larger screen sizes**.
- RTL support with left side sheet is new vs. M2.

### 2. Anatomy
- **Standard side sheet — 4 elements**: Divider (optional), Headline, Container, Close icon button.
- **Modal side sheet — 7 elements**: Back icon button (optional), Headline, Container, Close icon button, Divider (optional), Action buttons (optional), Scrim.
- **Container** — holds all elements; size determined by the space those elements occupy; **the only required element**.
- **Back icon button (optional)** — provides a way to exit the sheet or move to a different experience; because primary content behind/beside a side sheet is always visible, affordances for leaving the sheet and returning to primary content matter. Placed upper left.
- **Close icon button (optional)** — consistent method for dismissing the sheet; **highly recommended, increases accessibility, makes focused side sheets easier to close**. Placed upper right.
- **Action buttons (optional)** — represent actions available from the sheet, e.g. **Save**, **Edit**, **Download**; use elevation, fill, and tone to call attention to specific actions.
- **Divider (optional)** — separates kinds of content and creates distinct regions; use to separate action buttons from content, and user-generated from system-generated content.
- **Content (optional)** — wide variety of content and layouts, from a list of actions to supplemental content in a tabular layout.

### 3. Sizes / measurements
Shape: **modal side sheets have a 16dp corner radius**.

Standard side sheet:

| Attribute | Value |
|---|---|
| Start/end padding | 24dp |
| Padding between top elements | 12dp |
| Bottom actions height | 72dp |
| Bottom actions top padding | 16dp |
| Bottom actions bottom padding | 24dp |
| Bottom actions alignment (horizontal) | Left |
| Max-width | 400dp |
| Margins (when detached) | 16dp |

Modal side sheet:

| Attribute | Value |
|---|---|
| Start/end padding | 24dp |
| Start padding with icon | 16dp |
| Padding between top elements | 12dp |
| Bottom actions height | 72dp |
| Bottom actions top padding | 16dp |
| Bottom actions bottom padding | 24dp |
| Bottom actions alignment (horizontal) | Left |
| Max-width | 400dp |
| Margins (when detached) | 16dp |

### 4. Placement
- **Place side sheets along the edge of the screen, usually on the right side, to avoid interference with any navigational components on the left edge.** They can be **slightly inset by 16dp**.
- Side sheets have a **fixed width** and typically **span the height of the screen**; dimensions depend on how the app's layout is subdivided into UI regions. They have a default width but can be resized to the needs of the layout.
- When a **standard** side sheet opens, the **body area shrinks** to accommodate the sheet's width while maintaining a margin on the body's trailing edge.
- **RTL**: side sheets appear on the **left edge** of the window with **all elements reversed**.

### 5. States and interaction behavior
- **Scrolling**: side sheets can **vertically scroll independent of the rest of the UI**, so their scroll position and content persist while the page scrolls and vice versa. **Side sheets cannot scroll horizontally.**
- **Predictive back (Android)**: swipe left or right on the side sheet — the sheet **detaches from the top and bottom edges** of the screen to signal it will close; the previous screen is revealed in a preview; the sheet and its content **always scale in the direction of the gesture**. Gesture outcomes: release to commit, fling to commit, cancel.

### 6. Color role mapping
Standard side sheet (light and dark themes, in diagram order): **Outline variant** (divider), **On surface variant**, **Surface** (container), **On surface variant**.
Modal side sheet (light and dark themes, in diagram order): **On surface variant**, **On surface variant**, **Surface container low** (container), **On surface variant**.
New color mappings to support dynamic color vs. M2.

### 9. Do / Don't
- Do place side sheets along the screen edge, usually on the right; inset at most the recommended **16dp**.
- **Don't inset a side sheet from the screen edges far beyond the recommended margin** — it makes position and scroll behavior unclear and obscures primary content.
- **Don't allow horizontal scrolling** or lay out the sheet in a way that suggests horizontal scrolling; the narrow width leaves limited space to fully view items.
- Always include a close affordance; without a close icon button people can't predict the opening and closing flow, or know whether the sheet is transient or permanent.
- Prefer modal side sheets in compact breakpoints; standard in medium to expanded.

### 10. Accessibility
- People must be able to **dismiss the side sheet using assistive technology**.
- **Material requires that a close affordance, such as a close icon button, is always present within a side sheet.**
- Initial focus: actions within a side sheet can be focused by tab order using keyboard or switch control. Example focus order: **Headline → Close → Cancel → Save** (diagram caption also lists "headline, close, save, cancel").
- Keyboard: **Tab** → focus lands on (non-disabled) icon button. **Space** or **Enter** → activates the (non-disabled) icon button.
- Labeling: the accessibility role for a side sheet is **Dialog**.

---

## Dialogs

### 1. What it is + when to use vs. siblings
- A **modal window in front of app content** providing critical information or asking for a decision. Dialogs **disable all app functionality** when they appear and remain on screen until confirmed, dismissed, or a required action has been taken. Use to make sure users act on information; dedicate each dialog to **completing a single task**; commonly used to confirm high-risk actions like deleting progress.
- Purposefully interruptive → **use sparingly**. A less disruptive alternative is a **dropdown menu**.
- Two variants: **basic** and **full-screen**.
  - **Basic** — interrupts with urgent information, details, or actions. Common cases: alerts, quick selection, confirmation. Most often alerts or lists, but supports varied layouts and component combinations including lists, date pickers, and time pickers.
  - **Full-screen** — fills the entire screen; contains actions requiring **a series of tasks** (e.g. creating a calendar entry with title, date, location, time). Use when: the dialog includes components requiring keyboard input such as form fields; changes aren't saved instantly; components within the dialog open additional dialogs. **Full-screen dialogs are for compact breakpoints only** (mobile) — for medium and expanded breakpoints use a basic dialog. Full-screen dialogs are **the only dialogs over which other dialogs can appear**.

| Component | Importance | Action needed |
|---|---|---|
| Snackbar | Low importance | Optional: Snackbars may not have a button, and can disappear automatically |
| Dialog | High importance | Required: Dialogs block the main content until an action is confirmed |

- Choose between them **based on the importance of the message**; this component messaging strategy "helps avoid overusing dialogs."
- Basic dialogs **require a person to take action before they close**, and can let people confirm a choice before committing to it.

### 2. Anatomy
- **Basic dialog — 7 elements**: Container, Icon (optional), Headline (optional), Supporting text, Divider (optional), Button label text, Scrim.
- **Full-screen dialog — 6 elements**: Container, Header (region), Icon (close affordance), Headline (optional), Text button / Button label text, Divider (optional).
- **Container and scrim** — containers appear above other screen elements and hold the dialog's headline, text, buttons, and list items. Surfaces behind the container are **scrimmed with a temporary overlay** to make them less prominent and focus attention on the dialog.
- **Headline (optional)** — the dialog's purpose is communicated by headline plus buttons or actionable items. Must contain a brief, clear statement or question; avoid apologies ("Sorry for the interruption"), alarm ("Warning!"), or ambiguity ("Are you sure?"). Always succinct; can wrap to a second line if necessary, and be truncated. In full-screen dialogs, long or variable-length headlines (such as translations) can be placed in the **content area** instead of the app bar.
- **Buttons** — represent dialog actions, letting users confirm, dismiss, or acknowledge. **Aligned to the trailing edge**; the **confirmation button is always closest to the edge**; alignment responds automatically for RTL, where the confirmation button aligns to the **left** edge. Maximum **two actions**: a single action must be an **acknowledgement**; two actions must be one confirming + one dismissing. Two text buttons display next to one another; **stacked buttons** accommodate longer button text but take more room, with **confirming actions above dismissive actions**. A third action such as **Learn more** is not recommended — it navigates away, leaving the dialog task unfinished; use an **inline expansion** for more information, or provide extensive information before entering the dialog.

### 3. Sizes / measurements
Vs. M2: greater padding to account for increased corner-radius and title size; option for custom basic dialog positioning; increased corner-radius; larger and darker headline.

**Basic dialog:**

| Attribute | Value |
|---|---|
| Container shape | 28dp corner radius |
| Container height | Dynamic |
| Container width | Min 280dp; Max 560dp |
| Divider height | 1dp |
| Icon size | 24dp |
| Minimum width | 280dp |
| Maximum width | 560dp |
| Alignment with icon | Center-aligned |
| Alignment without icon | Start-aligned |
| Top/Left/right/bottom padding | 24dp |
| Padding between buttons | 8dp |
| Padding between title and body | 16dp |
| Padding between icon and title | 16dp |
| Padding between body and actions | 24dp |

**Full-screen dialog:**

| Attribute | Value |
|---|---|
| Container shape | 0dp corner radius |
| Container height | Dynamic |
| Container width | Container width; Max 560dp |
| Header height | 56dp |
| Header width | Container width |
| Headline text alignment | Start-aligned |
| Divider height | 1dp |
| Icon (close affordance) size | 24dp |
| Bottom action bar height | 56dp |
| Bottom action bar width | Container width |
| Top/left/right padding | 24dp |
| Padding between elements | 8dp |

### 4. Placement / adaptive design
- Dialogs can **swap variants as the breakpoint changes** — a full-screen dialog can become a basic dialog at larger breakpoints.
- **Medium window size**: basic dialogs appear **center** by default; position can be **overridden** for a more ergonomic experience (e.g. custom-positioned on the right side).
- **Expanded window size** (desktop): dialogs are modal windows **above a scrim**. Basic dialogs can be custom-positioned anywhere on larger screens, respecting margins to prevent edge collision — custom placement area respects a **56dp margin** from the screen edges.
- Position: dialogs retain focus until dismissed or an action is taken. They **shouldn't be obscured by other elements or appear partially on screen**, except full-screen dialogs.
- Full-screen dialog navigation: because full-screen dialogs can only be completed, dismissed, or closed, the **close "X" icon button should be the only navigation option in the app bar**.
- Dialog windows: launching a full-screen dialog **temporarily resets the app's perceived elevation**, allowing simple menus or dialogs to appear above it; they cover the screen and don't appear as a floating modal window.

### 5. States and interaction behavior
- **Appearing**: dialogs appear without warning, requiring users to stop their current task; they use the **enter and exit** transition pattern.
- **Scrolling**: most dialog content should avoid scrolling. When scrolling is required, the **dialog title is pinned at the top and buttons pinned at the bottom**, so selected content stays visible alongside title and buttons. Dialogs **don't scroll with elements outside the dialog**, such as the background.
- **Disabled**: disable confirming actions until a choice is made; **dismissive actions are never disabled**. In full-screen dialogs, **don't disable the confirmation button**.
- Full-screen dialog **saving**: use **Save**; the close icon or a dismissive action such as **Cancel** or **Back** closes the dialog.
- Full-screen dialog **confirmation**: the confirmation action must be clear about what happens next, like **Send** or **Create**; avoid vague terms like **Done**, **OK**, or **Close**. Only trigger an additional basic dialog **if the action fails**.
- Full-screen dialog **dismissing**: when dismissed (or closed without being saved), a **basic dialog appears in front of it** to confirm discarding unsaved changes.
- Full-screen dialog **error messages**: field errors always appear **inline** where they occur (text fields have built-in error messaging; checkboxes and radio buttons need messages added next to the fields). General errors (e.g. network issues preventing save/submit) appear in a **basic dialog when the confirming action fails**. Errors must clearly but briefly explain the source and the fix; **show all errors on the page at once**.
- Transition into full-screen: use a **container transform** pattern to transition a **FAB** into a full-screen dialog.
- **XR / spatial dialogs** (full space only; home space follows general dialog guidance): dialogs can be elevated spatially via overrides. Effect — the spatial dialog **scales uniformly**, fades in on appear and fades out on disappear; the **scrim only fades** in and out. Movement — on activation the dialog **rises from the app to the highest resting level on the Z-axis** and returns to a normal resting level when the action completes; the **scrim stays at the app content level at all times**. To prevent motion sickness use **standard easing** and **long duration** motion tokens. Placement — weigh **field of view, viewing distance, and possible interactions** when deciding where to place dialogs in XR; for effective visual hierarchy **the dialog should be the most prominent element**. Display spatial dialogs at the **highest resting level**, at a comfortable viewing distance; **center them in the person's field of view** — if the dialog can't track head movements, position it in the center of the app's content; if it can, configure **lazy follow** behavior so it stays anchored to the center of the field of view until an action is taken. Note: this is a rapidly changing space, guidelines primarily intended for designers; color and elevation for spatial dialogs can be customized by makers and are **not available in Jetpack Compose yet**.

### 6. Color role mapping
**Basic dialog** (light and dark themes, in diagram order, 6 roles): **Surface container high** (container), **Secondary** (icon), **On surface** (headline), **On surface variant** (supporting text), **Primary** (button label text), **Scrim**.
**Full-screen dialog** (light and dark themes, in diagram order, 5 roles): **Surface container high** (container), **On surface**, **On surface**, **Primary**, **On surface variant**.
**XR**: dialogs can use **surface container high** or **surface container highest**. The dialog should have the **highest elevation in the product** — e.g. if a dialog is **surface container high**, don't use **surface container highest** for any other element. Add a **scrim** behind a dialog to improve visibility; scrims prevent other content from being selected until the dialog action is complete.
New color mappings and dynamic-color compatibility vs. M2.

### 9. Do / Don't
- Use dialogs for prompts that block an app's normal operation and for critical information requiring a specific task, decision, or acknowledgement.
- **Don't use dialogs for low- or medium-priority information** — use a snackbar, which can be dismissed or disappear automatically.
- Do pose a specific question that concisely explains what's involved and provides clear actions; **don't use ambiguous titles** ("Are you sure?").
- **Don't place dismissive actions to the right of confirming actions** — place them to the left.
- Provide a single action **only** if it's an acknowledgement. Avoid unclear choices (e.g. **Cancel** paired with **Got it** when no clear action is proposed).
- Maximum of two actions; a third action such as **Learn more** is not recommended.
- Avoid placing long headlines in a full-screen dialog's app bar (truncated text may lead to misunderstanding); shorten app bar text and put longer headlines in the content area.
- Don't trigger a basic dialog when the confirming action is selected (only on failure).
- Don't use the confirming action to dismiss a full-screen dialog.
- Avoid using **full-screen dialogs in XR** — required actions could appear beyond a person's field of view; use **basic dialogs** for XR expanded window sizes, and limit full-screen dialogs to compact window sizes.
- Make sure a spatial dialog's color is higher than all other UI elements, and use a scrim.

### 10. Accessibility
- People must be able to use assistive technology to open and close a dialog; provide and submit other inputs if the dialog is interactive (text field, selectable list); and scroll the dialog to access all contents extending beyond the container.
- **Use sparingly** — dialogs disrupt content flow for people using screen readers; present less critical information non-blockingly within app content flow.
- **200% text size**: choose concise strings to avoid excessive wrapping/truncation. On Android, headlines should be concise enough to fit within **four** lines after text size is increased to 200%. If a headline exceeds this and gets truncated, provide an alternative way to access the full content **in a single tap**.
- Elements within dialogs follow their own accessibility guidelines — e.g. text fields, typography, buttons.
- Initial focus lands automatically on the **first interactive element** within the dialog.
- Keyboard: **Tab** → next interactive element in the dialog, or the first element if focus is on the last. **Shift + Tab** → previous interactive element, or the last if focus is on the first. **Space or Enter** → triggers/commits the focused element's action. **Escape** → closes the dialog.
- Labeling: the dialog's accessibility label is typically the same as its **title or headline**. On web, basic dialogs should have the **alert dialog** role. Contained components (buttons, text fields) are labeled per their own guidelines.
- XR accessibility guidelines are still evolving; spatial dialogs should follow applicable Material dialog accessibility standards.

---

## Gaps — specs referenced but not present in the source text

> **Before treating a measurement here as unavailable:** many of these are published as
> `md.comp.*` values in the generated Compose token files, which are collected in
> [`component-tokens.md`](../component-tokens.md) — container heights and widths, shape
> assignments, elevation levels, icon sizes, and internal spacing. Check there first. Those are the
> Compose token values, so attribute them as such rather than as guideline text.


- **All seven pages**: no `md.sys.*` / `md.comp.*` token identifiers appear in the converted text. Every page has a "Tokens & specs" / "Tokens and specs" block that is an interactive table which did not convert ("Browse the component elements, attributes, tokens, and their values"; Cards and Dialogs: "Select a component variant below…"; Lists: "Use the table's menu to select a token set. The **common** set… The **expand** set…").
- **All seven pages**: no typography role mapping (no type-scale style names such as body/title/label roles) for any text part — headline, subhead, supporting text, label text, trailing text, button label, dialog headline, list overline, carousel item text. Only Dialogs' M2 comparison says "Larger and darker headline."
- **Cards**: elevation dp/level values for elevated cards, for the raised state during pick-up-and-move, and for the coplanar resting elevation; state-layer opacity values; maximum card height value ("taller than the maximum card height"); grid/collection column counts and gutter values; per-breakpoint card dimensions.
- **Cards**: which specific color role maps to which non-container part (headline, subhead, supporting text, buttons) — only container/outline roles are given.
- **Carousel**: item **height** values for any layout; large-item max-width default value; medium-item width range; number of items per named breakpoint (only "up to three" in compact); parallax offset/ratio; motion duration/easing tokens; carousel container corner radius; which of the two listed color roles (Container, Surface) applies to which element.
- **Carousel**: the count discrepancy itself — Overview says "Six layouts," Usage says "There are four carousel layouts." Both are quoted above; the source does not reconcile them.
- **Lists**: all **expressive** list measurements — item heights, corner radius / shape values, segmented-style gap size, padding, and selection-highlight treatment. The expressive "Measurements" section is image-only ("List item alignment, padding, and size measurements"), and the baseline layout diagrams for one-, two-, and three-line lists carry no in-text numbers beyond the summary attribute table.
- **Lists**: per-part color role mapping — the 10 (expressive) and 9 (baseline) role names are listed in diagram order only; the source does not name which element each role belongs to.
- **Lists**: divider thickness; overline specs; leading avatar/image/video dimensions; expand-interaction motion durations.
- **Divider**: divider **thickness/height** is not stated on the divider page (the dialogs page gives 1dp for dividers inside dialogs); vertical divider dimensions and margins are not given; no opacity value.
- **Bottom sheets**: drag handle **width and height** (only the 48dp hit target and 22dp top/bottom padding are given); container elevation value; scrim opacity (Android: "automatically handled by the system UI"); preset height values other than the 50% modal cap; the specific top-corner-only radius token; predictive-back detach offsets.
- **Side sheets**: sheet **default width** (only Max-width 400dp); standard side sheet corner radius (only modal's 16dp is stated); headline height; close/back icon button sizes; divider thickness; scrim opacity; standard side sheet interaction states (hover/focus/pressed) are not enumerated; no states section on the page at all.
- **Dialogs**: scrim opacity value; container elevation value; basic dialog per-part color roles beyond the ordered list; the 5 full-screen dialog roles are listed in diagram order without part names for 3 of them; stacked-button spacing; XR depth/resting-level dp values; specific `standard easing` and `long duration` token names (linked, not spelled out).
- **Cards / Lists / Carousel**: state-layer opacity percentages for hover, focus, pressed, and dragged are never given numerically on any of these pages.
