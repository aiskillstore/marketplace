# M3 Styles & Foundations — Elevation, Spacing, Icons, Design Tokens, Customization, Designing (Accessibility)

Source: m3.material.io pages `elevation`, `spacing`, `icons`, `design-tokens`, `customizing-material`, `designing`. No "M3 Expressive update" section appears on any of these six pages.

---

## Elevation

### 1. What it is + when to use it vs. siblings
- Elevation is the distance between two surfaces on the z-axis, measured in density-independent pixels (dp).
- Applied to **all** surfaces and components. Tokens codify z-axis distance so components appear consistently relative to each other.
- Elevation tokens have **no shadows and no color**; each platform determines the specific shadows and values at each level. Elevation has no shadow or value of its own by default.
- Elevation can be depicted three ways — pick per need:
  - **Tonal difference** (surface fills with a tone difference) — M3 default method for indicating separation.
  - **Shadow** — use when a tonal/hairline treatment is insufficient: to protect elements against patterned or visually busy backgrounds, or to encourage interaction.
  - **Scrim** — use beneath elements like modals and expanded navigation menus, to bring focus by increasing visual contrast of a large layered surface.
- Surfaces at different elevations: (a) allow surfaces to move in front of and behind other surfaces (content scrolling behind app bars); (b) reflect spatial relationships (a FAB's shadow indicates it is separate from a card collection); (c) focus attention on the highest elevation (a dialog temporarily appearing in front of other surfaces).
- Worked measurement example: one surface at **1dp** and another at **8dp** — the difference in elevation between the two surfaces is **7dp** when viewed from the side.

**Differences from M2**
| Aspect | M2 | M3 |
|---|---|---|
| Shadows | Applied by default to all levels | Use shadows only when required — extra protection against a background, or to encourage interaction |
| Color | — | New color mappings; compatibility with dynamic color |
| Levels | — | Elevation is **now** described in terms of **levels** |

### 2. Anatomy — what depicts elevation
To successfully depict elevation, a surface must show:
- Surface **edges**, contrasting the surface from its surroundings
- **Overlap** with other surfaces, either at rest or in motion
- **Distance** from other surfaces

Shadow properties carry meaning: both a shadow's **size** and its amount of **softness/diffusion** express degree of distance. Small + sharp shadow = close proximity to the surface behind. Larger + softer shadow = more distance. **Shadows can express the degree of elevation between surfaces in ways other techniques can't.**

**Tonal difference — why it is the default.** Tonal difference between surfaces expresses the tactile quality of Material surfaces: it shows where one surface ends and another begins, separating parts of a UI into identifiable components. Example: the edges of an app bar show it is separate from a grid list, communicating that the grid list scrolls independently of the app bar. When tonal difference alone is not enough, indicate the edge by giving the surface a **drop shadow** or by **placing a scrim behind it**.

### 3. Sizes / variants — the six levels
Material uses **six** levels of elevation, named for relative distance above the UI's surface: **0, +1, +2, +3, +4, +5**.
- An element's **resting** state can be on levels **0 to +3**.
- Levels **+4 and +5 are reserved for user-interacted states** such as hover and dragged.

**Component elevation (resting level → dp height → components)**
| Resting level | DP height | Components |
|---|---|---|
| 5 | 12dp | (not assigned as resting level) |
| 4 | 8dp | (not assigned as resting level) |
| 3 | 6dp | Date pickers; Dialogs (modal); Extended FAB; FAB; FAB menu (close button); Search; Time pickers |
| 2 | 3dp | App bar (scrolled); Menu; Navigation bar; Rich tooltip; Toolbar |
| 1 | 1dp | Banner; Bottom sheet (modal); Button (elevated); Card (elevated); Chips (elevated); Navigation drawer (modal); Side sheet (modal) |
| 0 | 0dp | App bar (not scrolled); Buttons (filled, tonal, outlined); Button groups; Cards (filled, outlined); Carousel; Chips; Dialog (full-screen); Extended FAB (in navigation rail); FAB (in navigation rail); FAB menu (list items); Icon buttons; List; Navigation rail; Segmented button; Side sheet (docked); Slider; Split button; Tabs |

Component elevation is used **only** to determine where the component sits in relation to other components, including when hovered or focused.

### 5. States and interaction behavior
- Every component has a **default resting elevation**. Do not change it.
- Components should change elevation in response to system events or user interaction, like hovering. The elevation change must be **consistent across all similar elements**.
- **Hover raises elevation by one level.** All Material buttons increase elevation by 1 level when hovered. Example: hovering a FAB temporarily increases elevation by 1 level, from level 3 to level 4 (the FAB diagram shows the change as 5dp → 8dp from top and side views).
- Focus usually raises elevation by one level.
- Elements can temporarily **lift** on focus, selection, or another interaction such as swipe. A raised element can also **lower** when a higher element appears.

### 6. Color role mapping
- **Scrim: use the `scrim` color role at 32% opacity.**
- Surface and surface container color roles are available for elevation-adjacent containment: **these roles are not tied to elevation** and provide flexibility for defining containment areas.
- **Any overlapping containment areas or components should have different color roles** in order to visually communicate separation.
- Elevation represents distance between elements; **the product applies color to represent elevation**.
- Example mapping shown for an email home screen: `surface` = list item background color; `surface container` = navigation bar background color.

### 9. Do / Don't
- Do stick to a small number of elevation levels — M3's system is deliberately limited to a handful of levels; the creative constraint forces thoughtful decisions about the UI's elevation story.
- Do use the default resting elevation of Material 3 components; **avoid changing it**.
- Do apply shadows sparingly: "less is more" — the fewer levels in your UI, the more power they have to direct attention and action.
- Do use tonal difference by default to indicate surface separation; use drop shadows or a scrim as alternative edge indicators.
- Do ensure floating elements have sufficient contrast with the surfaces beneath.
- Don't use colors with insufficient contrast — the relationship between surfaces must be clear (e.g. a FAB with no shadow insufficiently separated from the surface beneath).
- Don't rely on surface tint color: **surface tint color is deprecated; use elevation level tokens (0–5) instead.**

### 10. Accessibility
- For **interactive components**, edges must create sufficient contrast between surfaces — meeting or exceeding accessible contrast ratios — so surfaces read as separate from one another.

### Availability
| Resource | Status |
|---|---|
| Design Kit (Figma) | Available |
| Flutter (`ElevationOverlay`) | Available |
| Jetpack Compose | Available |
| MDC-Android (surface colors) | Available |
| MWC-Web (elevation) | Available |

---

## Spacing

### 1. What it is + when to use which category
- Spacing is the distance around and between component and layout elements. Apply spacing tokens to the **margins, padding, and gaps** of a component, UI element, or layout.
- Spacing is applied to the **flow** of elements (horizontal, vertical) or **in relation to** the elements (leading, trailing, top, bottom, gap).
- Adapt spacing to different values based on context — mobile vs desktop, or density settings.
- Material's spacing system is intentionally a **simple linear scale**. Unlike the color system (which adjusts light/dark logic across all components at once), **tailored spacing logic is built within each component**.

**Three categories — discriminating rule**
| Category | Definition | When |
|---|---|---|
| **Padding** | Space **inside** an element; buffer from container edge to content (text, icons) | Default choice |
| **Gap** | Space **between** elements in a grid or container | Between side-by-side (horizontal gap) or stacked (vertical gap) elements |
| **Margin** | Space **outside** an element; buffer between element and parent container or screen edge | Only to apply further spacing **beyond** the parent container's padding, or in layouts |

**Use padding & gaps before using margins.** Material rarely uses margins in components; padding and gaps apply spacing in a more uniform way.

**Gap naming rule:** use a plain **horizontal gap** / **vertical gap** for simple components where gaps are always the same size. Complex components with many different gaps should define them by the elements on each side, e.g. an **icon-label gap**.

### 2. Anatomy — spacing positions
Position of the spacing can be: **vertical, top, bottom, horizontal, leading, trailing**.
- **Leading** and **trailing** edges swap sides in right-to-left (RTL) languages.
- Component spacing concepts: vertical padding (top & bottom); vertical gap; horizontal padding (leading & trailing); horizontal gap.
- Layout spacing concepts: margin; top padding; horizontal padding (leading & trailing); spacer (gap); vertical gap.

### 3. Scale, tokens, and named values
- The spacing system is measured on an **8dp scale**, where **space100 = 8dp**.
- Base unit token: **`md.sys.measurement.space100` = 8dp**.
- Spacing units are created as a **multiplier** from the 8dp baseline unit. Material defines only the **most recommended** spacing unit values on the scale; the system can be extended.
- The main spacing units are multiples of 8dp; the documented range covers **0x to 9x**. The scale runs from **2, 4, 6, 8** at the bottom of the range up to **48, 56, 64, 72** at the top.
- System spacing tokens are a **linear range** of values intended to cover the **majority** of spacing needs within the design system.
- **Nested units:** values other than multiples of 8 are also used in layouts and Material components — **2dp, 4dp, 6dp, and 10dp**. Material only defines nested units actively used in common layouts or Material components; tokens exist for the **0.25x, 0.5x, 0.75x, and 1.25x** nested units.
- Extension rule: follow the multiplier pattern, so **space225 = 18dp (8dp × 2.25)**.
- Named tokens appearing in the source text: **space100 (8dp)**, **space125**, **space200**, **space225 (18dp)**, **space300**, **space400**, **space600**.
- Example applied values (button): small button bottom padding = **space200**, large button bottom padding = **space400**; small button leading padding = **space300**, large button leading padding = **space600**.

### 4. Placement — layouts vs components
- In **components**, spacing units define the padding and gaps between individual elements of a component, such as text, icons, and controls.
- In **layouts**, spacing units standardize the overall composition of the page — where text, UI elements, and components go. Layouts use **panes, spacers, and margins** to structure the page, and **padding and gaps** to organize content within the panes.
- Worked example — the **search** container: **8dp vertical padding**, **8dp horizontal gaps**, **24dp horizontal margins by default** (to ensure accurate placement from the screen edge), changing to **12dp horizontal margins when focused**; container padding and horizontal gaps remain the same when focused.

### 5. Adaptive / density behavior
- **Adaptive layout:** map the spacing to different system tokens for each device type, such as mobile or desktop. Components can be customized to adapt spacing per form factor — mobile, desktop, cars, XR, TVs.
- **Density:** adapt vertical padding to different spacing values for each setting; list item spacing example spans density settings **0 to -4**.
- **Text scaling:** when text is scaled up to **200%**, the same spacing should be **preserved by default** — a button with text at 200% uses the same spacing tokens as an unscaled button.

### What to use (decision order)
1. **Pre-tokenized components** — some Material components map to spacing system tokens out of the box; product teams can customize the mapping to adapt to form factor or density. (Work is ongoing to hook up all Material components to spacing tokens.)
2. **System tokens** — spacing system tokens define the recommended values. Apply these to custom components and layouts, **replacing any hardcoded values**.
3. **Customize the system** and add your own only if the right system token doesn't exist.

### Customizing the system — three approaches
The spacing system captures Material's **design intent**, but **customization is expected and often necessary**; which approach you take depends on your needs.

| Approach | Use when | Example |
|---|---|---|
| Customize Material's existing component spacing | You want to change how the base component appears across the entire product | Change "button top padding" mapping from **space125** to **space200** for a taller default button |
| Add custom system spacing & patterns | You need spacing units beyond what Material provides, or you have common adaptive spacing patterns | New token **space225 = 18dp**; a **surface content horizontal padding** token (`surface-content.padding.horizontal`) for a pattern shared by outlined cards and bottom sheets |
| Add adaptive layout & density | Same core component must appear differently per screen size or density setting | Map spacing to different system tokens per device type; adapt vertical padding per density setting |

### Component token naming
- **Most** Material component spacing attributes map to system spacing tokens. **Spacing logic — adaptive design or density — should be applied to the component attribute**, not to the system token.
- **Going forward**, all component spacing attributes use **padding**, **margin**, **gap** plus positional language: **horizontal, vertical, leading, trailing, top, bottom**. Example: "Medium button: leading padding".
- **Past** component spacing tokens use **"space"** to describe all padding, gaps, and margins: **leading-space, trailing-space, top-space, bottom-space, between-space**. Example: "Medium button: leading space".
- Resolution chain: component padding tokens → system tokens → final values.

### 9. Do / Don't
- Do apply spacing tokens to margins, padding, and gaps rather than hardcoded values.
- Do define padding and gaps **on the parent container** to organize all elements inside (e.g. uniform container horizontal padding on a button).
- **Avoid defining margins on child elements** — they usually aren't uniform and require more tokens (e.g. a button icon with different leading and trailing margin values).
- Do keep the same spacing when text scales.
- Do follow the 8dp multiplier pattern when adding new space tokens.

### Availability
| Implementation | Status |
|---|---|
| Android Views (MDC-Android) | Unavailable |
| Jetpack Compose | Available |
| Web | Unavailable |

Note: **the spacing system tokens are only used on Jetpack Compose.**

---

## Icons (Material Symbols)

### 1. What it is + when to use it vs. siblings
- Icons are small symbols to easily identify actions and categories.
- **Material Symbols are the new default** — a variable icon font set, newly drawn to be pixel-crisp and modernized. **Legacy Material Icons continue to be available but don't have the variable font capabilities of Material Symbols.**
- Get Material Symbols at fonts.google.com/icons — recolor, resize, and copy/paste icons. Use the Material Symbols variable font to enable dynamic styling in product.
- Library size: over **2,000 variations** in Google Fonts' icon library. Only create your own icon if what you need **isn't covered** by those 2,000+ variations — then use the 24dp keyline template.
- **Design principles:** icons pack an informative punch into a small form factor and are designed to be **simple, modern, friendly, and sometimes quirky**. Because their size is limited, each icon **must strictly adhere to the guidance** while still expressing its essential characteristics.

**Three styles — discriminating rule**
| Style | Character | Choose when |
|---|---|---|
| **Outlined** | Uses stroke and fill attributes for a light, clean style; stroke weight can be adjusted to complement or contrast typography weight | Dense UIs |
| **Rounded** | Uses a corner radius | Brands using heavier typography, curved logos, or circular elements |
| **Sharp** | Corners with straight edges (0dp radius), crisp, legible even at smaller scales | Brand styles not well-reflected by rounded shapes; rectangular design details |

Even in outlined sets, **some symbols should remain filled** for optimal legibility and recognition — e.g. full-body human icons or proprietary icons.

### 2. Anatomy
Icon metric parts: **Corner, Stroke terminal, Counter stroke, Stroke, Counter area, Bounding area**.
- **Stroke terminal:** e.g. an arrow symbol's arrowhead terminals are **trimmed to 45 degrees**.
- **Counter stroke:** e.g. the add-circle symbol uses a **linear 2dp inner stroke**.

The icon grid **establishes clear rules for the consistent — but flexible — positioning of graphic elements.**

Grid and layout parts:
- **Live area** — the region of an image unlikely to be hidden from view (such as where sidebars appear upon scrolling). Icon content is limited to the **20dp × 20dp** live area.
- **Padding** — **2dp** surrounds the live area on all sides, inside the 24dp × 24dp grid.
- **Trim area** — the complete size of a graphic. If additional visual weight is needed, content may extend into the padding between the live area and the trim area. **No parts of the icon should extend outside of the trim area.**

**Keyline shapes** (foundations of the 24dp grid; use as guidelines to maintain consistent visual proportions):
| Keyline | Dimensions | Example icon |
|---|---|---|
| Square | height and width **18dp** | Add chart |
| Circle | diameter **20dp** | Globe |
| Vertical rectangle | height **20dp**, width **16dp** | Document |
| Horizontal rectangle | height **16dp**, width **20dp** | Envelope |

### 3. Sizes / variants / configurations
**Sizes**
| Size | Use |
|---|---|
| **20dp** | Primarily desktop, dense layouts, small-scale visuals |
| **24dp** | Standard (baseline) icon size — displayed as 24dp × 24dp |
| **40dp** | Optimized for display or headline type, plus larger screen sizes; use when primary actions need to be highlighted |
| **48dp** | Same as 40dp |

For pixel-perfect accuracy, create icons for viewing at **100% scale**.

**Four adjustable axes** (each style symbol contains all four): **weight, fill, grade, optical size**. An axis is a typographic attribute of a symbol that can be altered to create visual variations.

| Axis | Range / values | Notes |
|---|---|---|
| **Weight** | thin **100** → bold **700**; regular = **400** | Defines stroke weight; can also affect the overall size of the symbol. Recommended stroke weight is **2dp / regular (400)**, which includes curves, angles, and both interior and exterior strokes. **Minimum weight for standard 24dp icons is 200.** |
| **Fill** | **0 to 1**, 1 = completely filled | Transitions from more outlined to a reversed/more filled style. Can convey a state of transition, such as unfilled and filled states. Along with weight, fill is a primary attribute impacting a symbol's overall look. |
| **Grade** | e.g. **0**, negative (**-25**), positive | Affects thickness; adjustments are **more granular than weight** and have a **smaller impact on the symbol's size**. At grade 0 thickness does not change; at negative grade the symbol appears lighter. Grade is also available in some text fonts and levels can be matched — a -25 grade text font pairs with -25 grade symbols. |
| **Optical size** | **20dp to 48dp** (20, 24, 40, 48) | Stroke weight changes as icon size scales so the image looks the same at different sizes. Automatically adjusts stroke weight when you increase or decrease symbol size — traditional resizing from a 24dp source vector produces a large icon that's too heavy compared with the original. |

**Corner radii**
- Corner radii are **2dp by default**.
- **Outlined** style: interior corners are **square, not rounded**.
- For shapes **2dp wide or less**, stroke corners shouldn't be rounded.
- **Rounded** style: both exterior and interior corner radii are rounded.
- **Sharp** style: both exterior and interior corner radii reduce from **2dp to 0dp**.

**Optical corrections for complex shapes** — subtle adjustments to improve legibility; any optical correction should use the geometric forms on which all other icons are based, without skewing or distorting those shapes.
- Paperclip icon uses **1.5dp of the possible 2dp stroke area** to fit multiple curves within the 24dp × 24dp icon space.
- Ramen bowl icon uses **1.5dp stroke and 2dp stroke together** within the 24 × 24dp icon space.

### 4. Placement
- Position icons **"on pixel"** within the icon grid — X and Y placement coordinates should be integers, not decimals.
- Adequate space should surround icons to allow legibility and interaction (see Target size).
- Use **20dp** optical size for dense layouts on desktop (e.g. desktop dropdown menu with icon in active state).
- Use **40dp–48dp** symbols when primary actions need to be highlighted.

### 5. States and interaction behavior
- **Fill** conveys state transition: unfilled (fill 0) vs filled (fill 1) — e.g. bottom navigation with filled symbols in selected and unselected states.
- **Positive grade** makes strokes heavier and more emphasized — use when representing an **active icon state** (e.g. a photo icon in active state appearing bolder).

### 6. Color role mapping / grade & contrast
- Grade compensates for **visual bleed** — images can look bigger or smaller depending on color contrast. To match apparent icon size:
  - **Dark icon on a light background: default grade = 0**
  - **Light icon on a dark background: grade = -25**

### 7. Typography pairing
Material Symbols are designed with similar considerations to typefaces and often appear alongside text. **Choosing the right icon set can tie the content of an interface together, enhancing the cohesive branded feel of the product.** Match the optical weight and size of text and icon:
- **Use the same size for your Material Symbols and text.** Don't mix the sizes of symbol and text.
- **Use the same optical weight for your symbol and text.** Don't use different optical weights.
- Outlined symbols' lighter stroke weight can mirror the thin lines of an app's typography.
- **Shift down the baseline of symbols to approximately 11.5% of the text size.** Don't use the same baseline for Material Symbols and text.

### 9. Do / Don't
- Simplify icons for greater clarity and legibility. **Don't be overly literal; avoid complex icons.**
- Make icons graphic and bold, using geometric, consistent shapes. **Don't use delicate or loose organic shapes.**
- Use and maintain a consistent visual style throughout one icon set. **Avoid mixing styles for one icon set.**
- Make icons **face forward**. **Don't tilt, rotate, or make icons appear dimensional** (no isometric perspective).
- Use consistent stroke weights and **squared** stroke terminals. **Don't use inconsistent stroke weights or rounded stroke terminals.**
- Interior corners shouldn't be rounded (outlined style). **Don't use overly round corners — it reduces the symbol's legibility. Don't use inconsistent corner radii.**
- Apply weights consistently across a set (e.g. a navigation rail). **Don't mix different weights.**
- **Don't use the lightest weight (100) for standard-size (24dp) icons** — minimum weight for this size is 200. Be careful using excessive weight for standard 24dp symbols.
- 2dp outlined icons remain readable across sizes and applications.

### 10. Accessibility
- **Target size: symbols of 24dp should have a target size of 48dp by default.** When a mouse and keyboard are the primary input methods, measurements may be condensed for denser layouts: **a 20dp symbol can use a target size of 40dp.**
- **Labels:** label text provides short, meaningful descriptions when symbols are more abstract — helpful for navigation. Use caution if icons are displayed without labels; icon meaning must always be unambiguous and accessible for all users. **Text labels can be omitted only in specific circumstances where reduced visual impact is necessary.**
- **Small icons:** Material Symbols scale up or down without loss of fidelity. Simple symbols, like stars for ratings, can be used on their own at any size as long as they remain identifiable. **Below 20dp, these symbols must have an accompanying text label:** (1) **complex icons** — highly detailed or with multiple parts; (2) **icons with a key action** — essential to using the product.
- **Localization best practices:** use labels when icons and symbols are more abstract; **navigation items must have labels for clarity and accessibility**; consider tech knowledge (frequent internet users may understand icons differently from infrequent users). Test iconography across age groups, cultures, and languages. Locales may prefer a cart, bag, or basket for checkout.
- **Cultural interpretation:** color carries cultural significance — white is associated with purity in western cultures but symbolizes mourning in some eastern cultures. Some locales use red as a warning color, others green. Owls represent wisdom in many western cultures but a negative omen in some eastern cultures.

### Resources / What's new
| Resource | Status |
|---|---|
| Icons catalog (fonts.google.com/icons) | Available |
| Material Symbols Figma plugin | Available |
| Icon keyline template (ZIP, 24dp, Adobe Illustrator, Apache 2.0) | Available |

- **Copy & paste customized Material Symbols:** search and select an icon on Google Fonts, then use the right-hand panel to resize, recolor, and copy the customized icon to clipboard in a single click.

---

## Design tokens

### 1. What it is
- Design tokens are the building blocks of all UI elements — the same tokens are used in designs, tools, and code. They are small, reusable design decisions making up a design system's visual style, replacing static values with self-explanatory names.
- **Use design tokens instead of hardcoded values.**
- Each token is named for **how or where it's used** — e.g. `md.comp.fab.primary.container.color` sets the container color for a FAB.
- **Even if a token's end value is changed, its name and use remain the same.**
- Tokens **meaningfully connect style choices that would otherwise lack a clear relationship.** If a designer's mock-ups and an engineer's implementation both reference the same token (e.g. "secondary container color"), both can be confident the same color is used in both places — **even if the hex value assigned to that token is later updated.**
- **Tokens & Material Design:** previously Material styles were communicated through guidelines, design files, tools, and platform-specific component libraries. With design tokens you can now **download, customize, and apply** Material styles and integrate them across the design and development process.

### 2. Anatomy of a token
A design token consists of **2 things**:
- A **code-like name**, such as `md.ref.palette.secondary90`
- An **associated value**, such as `#E8DEF8`

A token's value can be a color, typeface, measurement, **or another token**.

**Parts of a token name** — separated by periods, proceeding from the most general ("md") to the most specific ("on-secondary"):
1. **System name** — all token names start with the design system name, e.g. **`md`** for Material Design
2. **Token class abbreviation** — **`ref`** (reference), **`sys`** (system), **`comp`** (component)
3. **Role description** — descriptive words communicating the token's role

### 3. Classes of tokens (three)
| Class | Prefix | What it holds | Rule |
|---|---|---|---|
| **Reference tokens** | `ref` | All available style options with associated values | Usually point to a static value (hex code, font size) but can point to other reference tokens. **Do not change based on context.** Provide the team a starting point of approved colors, typography, measurements. |
| **System tokens** | `sys` | Decisions and roles that give the design system its character — color, typography, elevation, shape. Define the purpose a reference token serves in the UI | **This is where theming occurs.** A system token can point to different reference tokens depending on the context (light or dark theme). **Whenever possible, system tokens should point to reference tokens rather than static values.** |
| **Component tokens** (in development) | `comp` | The **design properties assigned to elements in a component** (e.g. the color of a button icon) — elements required to compose a component — containers, label text, icons, states — and their values such as size, shape, color, or elevation | **Whenever possible, component tokens should point to a system or reference token, not hardcoded values such as hex codes.** Not every stylistic choice can be a token, but whenever a design choice applies to multiple components of similar intent, a token should be used. |

With three classes, teams can update design decisions **globally** or apply a change to a **single component**.

**Resolution chain example:** `#E8DEF8` ← `md.ref.palette.secondary90` ← `md.sys.color.secondary-container` ← component token → FAB container color.
**Typography chain example:** `Roboto Medium` ← `md.ref.typeface.plain-medium` ← `md.sys.typescale.label-medium.font`.

### 6. Color role mapping example
A FAB's container and icon receive the **secondary** (surface/container color) and **on secondary** (icon color) system color roles respectively.

### Contexts
- Tokens can point to different values depending on a set of conditions — **contexts** — and the resulting values are **contextual values**.
- Examples of contexts: **device form factors, dark theme, dense layouts, right-to-left writing systems**.
- A context works like a **tag**: if a token value is tagged with dark theme, it overrides the default token value in a dark theme context.

### Why tokens matter
- Tokens give a design system a **single source of truth** — a repository where style choices are recorded and changes can be tracked.
- Because tokens are reusable and purpose-driven, they can define **system-wide updates** to themes and contexts — e.g. systematically apply a high-contrast color palette for improved visibility, or change the typographic scale so text is legible on a TV screen.
- Style updates propagate consistently through an entire product or suite of products; designers and engineers "speak the same language," reducing handoff confusion.
- Tokens allow decisions to be documented in a **platform-agnostic and shareable format**.

### Deciding if tokens are right for you
**Most helpful if:** you plan to update your product's design or are building from scratch; your design system is applied across a suite of products or platforms; you want easy future maintenance/updates; you want the most out of Material Design, including dynamic color.
**Less helpful if:** you have an existing app using hard-coded values unlikely to change in the next year or two; your product does not have a design system.

### Reading token modules on the M3 site
- Tokens in component **Specs** tabs are grouped first by **state** (enabled, disabled, hover, etc.), then by **element** — the part of the component a token applies to, such as the container or label text.
- Columns: **Name** (the component style aspect the token applies to, e.g. color or font); **Token ID** (the token defining that aspect); **Description** (optional descriptive info); **Context/value** (the value stored for a given context).
- Interactive modules let you look up the default baseline value stored by tokens for color, font, font size, font weight, etc., and show the relationship between a role, its system token, its reference token, and the stored pre-set value.
- Lookup workflow example (verify a filled button's label text color role): navigate Common buttons > Specs → find the filled button token module → search "label text" tokens under elements → copy the color token into code, or compare it to the color role in Figma.

### Using tokens in practice
- **Download Material baseline tokens:** Material Design's baseline theme includes design tokens and default values; download the theme as a **Design System Package (DSP)** from github.com/material-foundation/material-tokens to customize, collaborate on, and use in designs and product code. (DSP JSON format reference: github.com/AdobeXD/design-system-package-dsp.)
- **Generate tokens in Figma:** install the **Material Theme Builder** plugin from the community page → Plugins > Material Theme Builder > Open Plugin → **Get started** creates **material-theme** with baseline values by default; color and text styles populate the right-hand design panel; when fully generated, the artboard contains **tonal palettes for light and dark color schemes** plus a **default type scale**. Tokens are then represented as Figma styles.
- **Update token values — via plugin (updates colors only):** Plugins > Material Theme Builder > Open Plugin → choose the colors → updated color and text styles populate the right-hand panel.
- **Update token values — via Figma styles:** go to the file where the tokenized style is defined (right-click the style in the right-hand sidebar → **Go to style definition**) → hover the style and select the adjust icon, or right-click in the style picker → **Edit style** → change token name, description, properties in the **Edit style panel** → close.
- **Use tokens in mock-ups:** instead of manually setting color or typography for elements, apply the Figma styles representing your design tokens, so developers correctly understand and apply your design choices.
- **Use with the Material Design Kit:** duplicate the Material Design Kit in Figma → Plugins > Material Theme Builder > Open plugin → with components selected, select **swap** to replace baseline Material token style values with your own.
- **Export tokens:** Plugins > Material Theme Builder > Open Plugin → **Export tab** → select the format (**Android, Jetpack Compose**) → name the .zip and select **Save**.

### Resources
| Type | Resource | Status |
|---|---|---|
| Design | Design Kit (Figma) | Available |
| Design | Material Theme Builder Figma plugin | Available |
| Implementation | Material baseline theme and tokens (DSP) | Available |

---

## Customizing Material

### 1. What it is + when to use it
- Customization creates unique branded products with familiar patterns and accessible interactions.
- **Dynamic color makes personal devices feel personal.** M3 lets brand colors and individual color preferences converge in one-of-a-kind experiences: the color system reflects an app's design sensibility while honoring the settings individuals choose for themselves.
- By enabling dynamic color, an app retains the colors that define and differentiate the product while giving users more control over the styles that matter most to them.
- **Dynamic color is both a user setting and a developer choice.** Apply it selectively to work alongside your brand color scheme — e.g. a profile or account screen can reflect a user's color scheme settings, adding individuality to a personal space in an app.

### Get started (required steps)
1. **Build a custom color scheme with the M3 color system** to take advantage of personalization features.
2. **Implement a custom theme that user-generated color schemes can map to**, so the app respects a user's device- and app-level settings.
3. A custom theme also ensures the app has a **fallback color scheme** for users who don't enable dynamic color.

**Set-up paths:** integrate existing brand parameters with Material Design for consistent application across your product, **or** start from scratch with Material Design and create a new, complete color system.

### What the system handles for you
- With dynamic color and M3 color schemes, app colors **automatically adapt and integrate with user settings**.
- M3 supports systematic applications of **custom parameters** to define and maintain the styles that convey your brand.
- The color system automatically handles critical adjustments providing **accessible color contrast, legibility, interaction states, and component structure**.
- **Dynamic color also works for custom (non-Material) components.**

### Custom color schemes — Material Theme Builder
- With **built-in code export**, the Material Theme Builder Figma plugin makes it easy to **visualize your designs, migrate to the M3 color system, and take advantage of dynamic color**. Tokens are an important tool for creating and maintaining a **source of truth for style values**.
- The Material Theme Builder helps create custom color experiences **whether you are working with established brand parameters or have yet to define your app's colors.**
- In the Material Theme Builder you can identify and input **one or more** colors to define your color scheme. Adding a **second or third color is optional** and will influence the resulting color scheme.
- Mapping your app colors to the custom scheme's source colors aligns the roles and logic of dynamic color in M3.
- **Brand colors** can be added as a **single-use color** or as a **complete brand palette** with a range of tones that lend consistent, comprehensive color expression across the app.
- If your app uses a single brand color or a limited brand palette, **input your primary brand color as the custom color scheme's source color** — the input color generates a scheme with complementary tones to round it out.
- The Material Theme Builder creates **color and type tokens** exportable into multiple code formats; the Figma plugin creates tokens as Figma styles to connect with existing mock-ups, brand style guides, and design systems. Material tokens are ready to use in formatted theme files including **Design System Package (DSP)** — a cross-platform file format representing design system information.
- **Dynamic color codelab** (goo.gle/visualize-dynamic-color): hands-on walkthrough visualizing how designs and brand colors interact with dynamic color, leading into applying color with the Material Theme Builder Figma plugin.

### 6. Color role mapping
Depending on purpose in a UI, key colors are assigned roles that map to elements in components. The **five essential color groups** with role assignments are:
- **Primary**
- **Secondary**
- **Tertiary**
- **Neutral**
- **Neutral Variant**

An input color generates a **tonal palette** used to fill the range of color roles needed, such as **primary, on-primary, and primary container**. Apps can take on an array of colors from **baseline schemes, user-generated dynamic colors, or custom colors**. A user-generated color scheme can flow through apps that use a custom theme.

---

## Designing (Accessibility foundations)

### 1. What it is
- Designing and implementing accessible product experiences draws on **WCAG standards and industry best practices**.
- The framework's **three stages** help **translate a visual UI into a text-based, linear user experience that maps to code**. Color and contrast also support accessible navigation.
- **Accessibility markup is an integral part of creating documentation for design specs** — e.g. documenting a switch's on/off states with visible focus, Tab moving focus between switches, and Space/Enter changing the switch state.
- **Implementation rule:** by using **standard platform controls and semantic HTML** (on the web), apps automatically contain the markup and code needed to work well with a platform's assistive technology. Meeting each platform's accessibility standards and supporting its assistive technology (including shortcuts and structure) gives users an efficient experience.
  - Do use native elements, such as the standard platform dialog.
  - **Be wary of non-standard elements** — e.g. a non-standard platform dialog performing a standard dialog task requires extra testing to work well with assistive technology.

### Color & contrast
- Color can communicate mood, tone, and critical information. Primary, secondary, and accent colors can be selected to support usability. Sufficient color contrast between elements helps users with low vision see and use your app.
- **Higher contrast makes imagery easier to see; low-contrast images may be difficult for some users to differentiate in bright or low light conditions** — such as on a very sunny day or at night.
- Contrast ratios represent how different one color is from another, commonly written 1:1 or 21:1. The greater the difference between the two numbers, the greater the difference in relative luminance. The contrast ratio between a color and its background ranges from **1–21** based on luminance, according to the W3C.

**W3C recommended contrasts for body text and image text**
| Text type | Color contrast ratio |
|---|---|
| Large text (at **14 pt bold** / **18 pt regular** and up) and graphics | At least **3:1** against the background |
| Small text | At least **4.5:1** against the background |

- **Disabled states do not need to meet contrast requirements.**

**Clustering rule (Material research-grounded)**
- Some non-text elements, such as **button containers**, should meet a contrast ratio of **3:1** between their container color and the color of their background.
- **Clustered** elements (e.g. a group of buttons) require the user to distinguish each one from the group — these **benefit from 3:1 contrast** between themselves and the background.
- **Standalone** elements that stand apart from other elements, such as a **FAB**, are already distinguishable because of their prominence — these **don't benefit from / don't need to meet 3:1 contrast** between container and background.
- When placing components together in a cluster, use components or types of components that **each** achieve at least 3:1 contrast between themselves and the background.

### Hierarchy & structure
- **Why hierarchy matters:** when navigation is easy, users understand where they are in the app and what's important. To emphasize which information is important, use multiple visual and textual cues — **color, shape, text, and motion** — to add clarity.
- **Types of feedback:** visual feedback (labels, colors, icons) and touch feedback show users what is available in the UI.
- **Navigation:** clear task flows with minimal steps, easy-to-locate controls, and clear labeling. **Focus control** — the ability to control keyboard and reading focus — can be implemented for frequently used tasks.
- Every added button, image, and line of text increases UI complexity. **Simplify how the UI is understood by using:** clearly visible elements; sufficient contrast and size; a clear hierarchy of importance; key information discernable at a glance.
- **To convey an item's relative level of importance:** place important actions at the **top or bottom of the screen** (reachable with shortcuts); place related items of a similar hierarchy **next to each other**.
- **Visual hierarchy:** designers must collaborate with developers so HTML is written in the correct order and so they understand how screen readers interpret designs. **CSS determines layout and appearance, but screen readers rely on the top-down structure of HTML** on any platform (mobile or web); this structure creates the map the screen reader follows. Example: a 2×2 grid of four content cards reads top-left → top-right → bottom-left → bottom-right.

### Web landmarks and headings (web only)
Assistive technologies rely on clear, delineated structures and navigate primarily through **headings and landmarks**. Many AT translate a design into a linear experience, so users interact with content in a hierarchical, predetermined order — plan structural decisions in advance. Classifying and labeling sections of a page represents in code the structural information conveyed visually through layout.

**1. Define landmarks.** Landmarks are large blocks of content establishing the high-level structure of your layout — a set of **ARIA** roles. There are **eight** landmark roles:
| Role | Definition |
|---|---|
| **Navigation** | Contains lists of navigation links (there can be multiple — differentiate in the label) |
| **Search** | A search field |
| **Main** | The main content area as defined by UX. **There should be only one.** |
| **Banner** | Typically the header; content repeated page to page, often contains navigation and toolbars. **There should be only one.** |
| **Complementary** | A sidebar or aside to main content that can stand alone without the main content |
| **Contentinfo** | Typically the footer; contains information describing the site and its content (e.g. copyright). **There should be only one.** |
| **Region** | Important content blocks; can be nested inside the "main" landmark. **Regions should be labeled with names that make the purpose of that region clear.** |
| **Form** | Takes and stores user info |

**Add accessibility labels:** add clear and specific labels to any landmark role appearing multiple times (typically regions or navigation) to help users differentiate information. Labels should be added to **all regions**, plus any landmark where a label enhances meaning (e.g. explaining a sidebar's contents or purpose). **Don't repeat the landmark role within a label.** Example: a layout with two navigation-role areas labeled "primary" and "pagination".

**2. Define headings.** AT users often navigate with headings, which create a clear hierarchy to help users navigate and take action.
- **Identify headings based on content hierarchy, rather than visual styling.**
- **Headings should not skip a level** — don't go from H2 to H4 without an H3.
- Map content to headings **H1–H6 in sequential order** based on content hierarchy.
- **A single H1 for the page title is recommended.**
- Ensure headings correspond with meaningful titles; if they don't, change the UI titles to benefit all users or add a label for assistive tech.
- Heading levels are informed by the layout's **information architecture**; the page's visual styling **does not need to match** heading levels in prominence or visual hierarchy.

### 10. Target sizes (accessibility)
Material's target guidelines help users who **aren't able to see the screen**, or who **have difficulty with small touch targets**, to tap elements in your app.
- **Touch targets** are the parts of the screen that respond to user input, **extending beyond the visual bounds of an element** — e.g. an icon may appear 24 × 24dp, but the surrounding padding comprises the full **48 × 48dp** touch target.
- **For most platforms, make touch targets at least 48 × 48dp.** A touch target this size results in a physical size of about **9mm**, regardless of screen size. The recommended target size for touchscreen elements is **7–10mm**. Larger touch targets may be appropriate to accommodate a larger spectrum of users.
- **Note: iOS recommends 44 × 44dp targets.**
- **Pointer targets** are similar to touch targets but implemented by motion-tracking pointer devices such as a mouse or stylus. **Make pointer targets minimum 44 × 44dp.**
- **Target spacing:** in most cases, targets separated by **8dp of space or more** promote balanced information density and usability.
- Example measurements: standard icons **24dp**, star icon **40dp**, touch target on both **48dp**; three icons in a row at 48dp touch target size with **8dp padding** between icons.

### Flow — focus order & key traversal
People should be able to navigate and interact with your app without a traditional mouse or touch screen; goals should be achievable using **tab, arrow, and other common navigation keys**. Simplify flows by **strategically ordering tab stops** and **reducing overall page complexity**.

**Use defaults.** Avoid extra work — use predefined tab ordering unless a user journey needs special tailoring. The **default order follows the DOM** (the order of content as written in source code) and generally flows **left to right, top to bottom**. Keyboard navigation (key traversal) may be pre-defined within common components; use the defaults unless a UX pattern or custom component breaks from the default.

**Determining user flows**
1. **Group product use cases** into primary and secondary user journeys; use-case priority should influence decisions about user-flow priority.
2. **Define initial focus and component-level focus.** Focus is which control is the current active target of user interactions (mouse clicks, keyboard taps); generally **Tab** moves focus between interactive elements. Define initial focus when a user loads a screen, and initial focus for components with multiple interactive elements like a complex card or dialog. Example: on the Google homepage, even with links and buttons above and around the search field, initial focus belongs on the element supporting the most common user goal (the search bar).
   - **Dialog checklist:** when a dialog is triggered, focus is set to the dialog component — likely a specific interactive element within it such as a text input field or edit button; **when the user closes or cancels the dialog, focus returns to the interactive element that initiated the action.**
3. **Define any atypical key traversal** through the page and components; users should complete primary and secondary journeys using Tab, arrow keys, and other keyboard shortcuts.

**Key semantics**
| Key | Behavior |
|---|---|
| **Tab** | Typically moves focus between interactive elements; often used as primary navigation |
| **Tab + Shift** | Reverses direction |
| **Arrow keys** | Typically navigate **within** components (moving between cells in a form, traversing items in a menu) |
| **Enter** | Activates a link or button, or sends a form when a form item has focus |

For unique layouts and use cases, **group a collection of interactive elements as one tab stop** and use arrow keys to traverse sub-elements.

### Keyboard shortcuts — requirements
Keyboard shortcuts help users access menus and app functions **without using a mouse** on desktop apps and websites. These requirements help speech users avoid activating multiple shortcuts at once and keyboard-only users minimize unwanted actions.
- **Keyboard shortcuts should use a combination of two or more keys by default.**
- **Include a tutorial, list, or help center page of all custom keyboard shortcuts** in your product (e.g. Cmd+Z / Ctrl+Z to undo deleting an event in Google Calendar).
- If a shortcut is activated with a **single key**, provide users a way to take at least one of these actions, in preference order:
  1. **(Most preferred)** Remap the shortcut to include one or more non-printable keyboard keys.
  2. **(Preferred)** Activate the shortcut only when a relevant component is focused.
  3. **(Not preferred, only as a temporary solution)** Turn off the keyboard shortcut.

### Elements — labeling
Elements can be defined and labeled to enhance understanding of their function and reduce confusion for those navigating with AT. Add accessibility labels to define roles and indicate decorative elements. **Accessibility labels assist users who cannot rely on a product's visual interface; thoughtful labels make the text-based experience as usable as the visual experience.**

**Visual elements that need labels**
- Interactive icons or buttons with no visible text or not enough context in the text (e.g. an edit button with a pencil icon)
- Interactive images
- Visual cues (including progress bars and error handling)
- Meaningful icons (such as status icons)
- Meaningful images (e.g. diagrams, substantive photos, illustrations)

**Text elements that need labels for additional context**
- Generic links (e.g. "Learn more")
- Buttons with generic text (e.g. "Save" when there are multiple such buttons on a page)

**Elements that do not need labels**
- Non-interactive UI text — automatically read by the screen reader
- Buttons with sufficient text (e.g. "Download image")

**Rules**
- **Do not include the element name/role in labels** (e.g. button, menu). The identifier is automatically added when the element is assigned its proper role, typically by a developer. Screen readers repeat it otherwise ("Got it button button").
- Labels should **concisely describe an element's content, purpose, and behavior** — describe **purpose, NOT what the icon looks like** (not "magnifying glass"). Example: the label **"voice search"** describes the user task (search) paired with the input method (voice); **don't** label the same microphone icon "Microphone".
- **Add labels for meaningful images and interactive elements** — labels should be concise, descriptive, and convey the content and context of the image. This applies to infographics and other instructive images in support docs.
- **Hiding images:** decorative icons and images that don't enhance the experience for a visually-impaired user should be **annotated as decorative in order to hide them in code**.
- **Assign a role to interactive elements:** for **web**, assign **ARIA roles** for all interactive elements; for **non-web**, assign roles based on your design system components (button, slider, menu, etc.). ARIA roles apply to web apps and specify how to increase web page accessibility on top of HTML. Roles communicate desired interaction patterns into engineering action — some visual elements look the same but behave differently. Defining an interactive element's category by role helps AT users establish expectations for how to interact and anticipate what will happen.
- **Label language style:** "accessibility label" is the general term covering several types including **ARIA labels and alt tags**; when implemented in code they're translated to the appropriate type for the intended platform. "**Role**" covers both general component control types and ARIA roles for web apps.
