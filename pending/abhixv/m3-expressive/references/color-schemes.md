# Color (M3) — extracted reference

Source pages: `styles_color_system.md` (slug `color`), `styles_color_roles.md` (slug `color-roles`), `styles_color_choosing-a-scheme.md` (slug `choosing-a-scheme`), `styles_color_static.md` (slug `static`), `styles_color_dynamic.md` (slug `dynamic`), `styles_color_advanced.md` (slug `advanced`).

Scope note: these pages are style/system guidance, not component specs. They contain **no** dp/sp values, **no** `md.sys.*` / `md.comp.*` token strings, **no** corner-radius tokens, **no** typography role names, **no** breakpoint dp values, and **no** "M3 Expressive update" section. Absent specs are recorded in **Gaps noted** at the end of this file, not guessed.

---

## Color system

### 1. What it is + when to use it vs. siblings

Create accessible, personal color schemes communicating your product's hierarchy, state, and brand.

The Material color system includes:
- Built-in set of accessible color relationships
- 26+ color roles mapped to Material Components
- Built-in dark theme colors
- Static baseline color scheme with default colors assigned to each color role
- Dynamic color features including user-generated and content-based color

Migration rule: for products migrating from M2 to M3, **start by mapping the baseline color scheme to your existing product**. It can easily switch to dynamic color when ready.

Products with dynamic color can automatically generate and assign colors to each element in the UI, providing: personalized UI; accessible contrast; user-controlled contrast; automatic dark theme.

**Paint-by-number mental model:** each element on the screen has a "number"; each "number" is assigned a color. Hand-pick a color for every "number" → static scheme. Or generate an entire palette of accessible colors for each "number" from a single source (user's wallpaper, or in-app content like imagery). If the source changes, product colors update to match.

Customize how dynamic color appears by: setting the color source; adding static or harmonized colors; changing which "numbers" are assigned to which elements.

### 2. Anatomy — essential terms

| Term | Definition |
|---|---|
| **Color role** | Like the "numbers" on a paint-by-number canvas; assigned to specific UI elements. Semantic names like **primary**, **on primary**, **primary container**, with matching color tokens. |
| **Dynamic color** | Takes a single color from a user's wallpaper or in-app content and creates an accessible color scheme assigned to UI elements. If wallpaper/content changes, UI colors change to match. |
| **Static color** | UI colors that don't change based on wallpaper or in-app content. Hand-picked or generated in tools like Material Theme Builder. Once assigned to color roles and UX elements, colors remain constant. |
| **Baseline static color** | The default static color scheme for Material products. |
| **Color scheme** | All of a product's colors, color roles, and color relationships across light and dark themes. Two kinds: static, dynamic. |

**HCT color space** — the system uses HCT, defining all colors by three dimensions: hue, chroma, and tone. Changing HCT values lets you manipulate colors in **flexible but predictable** ways. Unlike other color spaces (HSL, RGB), HCT allows manipulation of hue and chroma **without affecting tone**.

| Dimension | Definition | Range |
|---|---|---|
| **Hue** | Perception of a color as red, orange, yellow, green, blue, violet, etc. Circular spectrum (0 and 360 are the same hue). | 0–360 |
| **Chroma** | How colorful or neutral (grey, black, white) a color appears. 0 = completely grey/black/white; infinity = most vibrant, though HCT chroma tops out at **roughly 120**. Different hues and tones have different maximal chroma values (biological + screen rendering limits). | 0 → ~120 |
| **Tone** | How light or dark a color appears (sometimes called luminance). 0 = pure black / no luminance; 100 = pure white / complete luminance. **Crucial for visual accessibility because it determines contrast: colors with a greater difference in tone create higher contrast, a smaller difference creates lower contrast.** | 0–100 |

### 3. Sizes / variants / configurations — the generation pipeline

Dynamic color scheme generation, in order:

1. **Source color** — three ways to get one:
   - **A. Generate from a wallpaper** (user-generated color). Wallpaper is digitally analyzed via **quantization**; a single color is selected as the source color.
   - **B. Generate from in-app content** (content-based color) — album thumbnail image, logo, or video preview. Image analyzed through quantization; single color selected.
   - **C. Pick by hand** — deliberately selected by a designer. *The baseline static color scheme uses a hand-picked source color.*
2. **Feed source color into an algorithm** — powered by **Material Color Utilities (MCU)**. Most common algorithms:
   - **User-generated color algorithm** — uses personal wallpaper to identify source color; maps colors of specific tones (lighter or darker) into the scheme per a combination of system design choices and user preferences.
   - **Content-based color algorithm** — uses image for source color; tones adjusted to match the appearance of the source image while maintaining accessible contrast.
   - **Custom colors** — colors closely match the chosen input colors, such as those representing brand or semantic meaning.
   - Same source color run through user-generated vs. content-based algorithms produces slightly different schemes.
3. **Algorithm generates key colors** — manipulates the source color's hue and chroma to generate **five complimentary key colors**: Primary, Secondary, Tertiary, Neutral, Neutral variant.
4. **Algorithm creates tonal palettes** — manipulates tone and chroma to create a **tonal palette** per key color. Colors numbered **0 to 100 in increments of 10, plus 95, 98, and 99**. Some palettes include more values. Illustrated as **13 tonal steps**. The smaller the tonal value, the darker the color. Chroma value may increase or decrease for some tones because of physical/biological/screen-rendering color limits (why bright light blue or bright light red are not quite possible).
5. **Algorithm assigns tones to color roles** — uses accessible color relationships to assign specific tones to the **26 color roles** in both light and dark theme. Example: tone **primary40** → **primary** role; tone **primary100** → **on primary** role. Primary roles are picked from the primary tonal palette; surface roles from the neutral tonal palette. Dark theme colors are also automatically assigned, so apps receive both light and dark themes through a **single set of color roles**.
6. **New colors applied to the UI** — the 26 standard color roles are already assigned to UI elements; when a new source color is picked, the UI dynamically changes color.

### 5. States and interaction behavior

State layers (guidance appears on the `static` and `dynamic` workflow pages, not on the Color system page): when using Material Theme Builder, enable the **Generate State Layers** setting so colors exist for the state layers needed to design interactions.

### 6. Color role mapping

Custom components can support contrast levels by using Material's appropriate color roles — e.g. use **primary container** and **on primary container**. Use design tokens to apply color roles to custom components. Example: a custom volume slider using **primary container** + **on primary container** changes colors automatically at standard contrast, and at medium and other contrast levels those roles apply the necessary new color values.

### 9. Do / Don't

- Do apply colors only in the intended pairs or layering orders.
- Do use design tokens to apply color roles to custom components.
- Do start with the baseline scheme when migrating from M2.

### 10. Accessibility

**Three levels of contrast.** In addition to light and dark theme, color roles support three contrast levels so people can select the one best suiting their vision needs. Contrasts are also tokenized. Contrast settings are automatically applied to **both** light and dark themes.

| Level | Spec |
|---|---|
| **Standard** (default) | Emphasizes visual hierarchy using high and low contrast elements. The baseline color scheme already uses mixed levels of contrast to reduce cognitive load. |
| **Medium** | Provides a **minimum contrast ratio of 3:1** for those who need more contrast but may experience visual discomfort with higher contrasts from effects like halation. |
| **High** | Further emphasizes essential elements with a **7:1 contrast ratio** to reduce visual distractions and enable focus. Example: high contrast is applied to the content in a card **but not** the card container. |

People with vision disabilities may choose medium or high contrast options for better support.

**Pairing accessible tones.** Algorithms use tonal palettes to find and pair contrasting tones, creating accessible combinations. Because tone describes lightness/darkness, it defines accessible color relationships, built into the algorithms.
- Example: dark tone on a button's container + light tone on its label ensures **3:1** contrast. Tones **50 and 98** for a button and its label create an accessible **3:1** contrast.
- For more contrast, tones are assigned farther apart, achieving **7:1**. Tones **30 and 98** create a **7:1** contrast. This is the concept powering **user-controlled contrast**.

### What's new (dated changelog on the Color system page)

**May 2025 — Three levels of contrast.** Color roles support three levels of contrast so people can select the one that best suits their vision needs. Contrasts also are tokenized. (Standard / Medium / High.)

**August 2024 — More colorful text and icons.** These roles are updated in **light theme** to be more colorful while still having accessible color contrast:
- On primary container
- On secondary container
- On tertiary container
- On error container

Affected components: Badges; Bottom app bar; Buttons (Buttons, Extended FAB, FAB, Icon buttons, Segmented buttons); Chips; Lists; Menus; Navigation bar; Navigation drawer; Navigation rail; Switches.

**Oct 2023 — Reorganized guidelines.** Same color system, explained in a new way. Updated sections: How the system works; Advanced customizations; Color resources.

**Feb 2023 — Tone-based surface colors.** Tone-based surface color roles **replaced the previous approach of surfaces at +1 to +5 elevation**. The new color roles are **not tied to elevation** and offer more flexibility and support for color features such as user-controlled contrast. Technical changes made to align with Android SysUI:
- Updated the default **light theme surface from tone 99 to tone 98**
- Updated the **chroma for the neutral palette, increasing it from 4 to 6**
- **Slightly darkened surface roles in dark theme**

**Feb 2023 — Additional accent colors.** Additional accent colors provide more flexibility and choice. In particular, a new set of **fixed** colors for the **primary**, **secondary**, and **tertiary** accent groups provide colors which stay the same across light and dark themes.

### Resources

| Type | Link | Status |
|---|---|---|
| Design | Design Kit (Figma) | Available |
| Implementation | Android Views (MDC-Android) | Available |
| Implementation | Jetpack Compose | Available |
| Implementation | Flutter | Available |
| Tools | Material Theme Builder | Available |

---

## Color roles

### 1. What it is + when to use it vs. siblings

**There are 26 standard color roles organized into six groups: primary, secondary, tertiary, error, surface, and outline.** Color roles are the connective tissue between elements of the UI and what color goes where.

- **Color roles are mapped to Material Components** — you use them whether using the static baseline scheme or dynamic color. Custom components must be properly mapped to this set of color roles.
- **Color roles ensure accessibility** — the color system is built on accessible color pairings providing an **accessible minimum 3:1 contrast**.
- **Color roles are tokenized** — roles are implemented in design and code through tokens. A design token represents a small, reusable design decision that's part of a design system's visual style.

Diagrams also reference **optional add-on roles for surface colors and fixed accent colors**, and swatches "for all 45 color roles including Primary, Secondary, Tertiary, Error, Surfaces, Inverse roles, Scrim and Shadow roles."

### 2. Anatomy — naming vocabulary

| Word in role name | Meaning |
|---|---|
| **Surface** | A role used for backgrounds and large, low-emphasis areas of the screen. |
| **Primary, Secondary, Tertiary** | Accent color roles used to emphasize or de-emphasize foreground elements. |
| **Container** | Roles used as a **fill color for foreground elements like buttons**. **They should not be used for text or icons.** |
| **On** | A color for text or icons *on top* of its paired parent color. E.g. **on primary** is used for text and icons against the **primary** fill color. |
| **Variant** | A lower-emphasis alternative to its non-variant pair. E.g. **outline variant** is a less emphasized version of **outline**. |

### 3. Variants — the full role inventory

**Accent color roles** (primary, secondary, tertiary) — assign based on importance and needed emphasis. Use caution when changing color roles for visual effect.
- **Primary roles**: important actions and elements needing the **most** emphasis, like a FAB to start a new message.
- **Secondary roles**: elements that don't need immediate attention and don't need emphasis, like the selected state of a navigation icon or a dismissive button.
- **Tertiary roles**: smaller elements that need special emphasis but don't require immediate attention, such as a badge or notification.

**Primary** — use for the most prominent components across the UI, such as the FAB, high-emphasis buttons, and active states.
| Role | Use |
|---|---|
| Primary | High-emphasis fills, texts, and icons against surface |
| On primary | Text and icons against primary |
| Primary container | Standout fill color against surface, for key components like FAB |
| On primary container | Text and icons against primary container |

**Secondary** (four roles) — use for less prominent components such as filter chips.
| Role | Use |
|---|---|
| Secondary | Less prominent fills, text, and icons against surface |
| On secondary | Text and icons against secondary |
| Secondary container | Less prominent fill color against surface, for recessive components like tonal buttons |
| On secondary container | Text and icons against secondary container |

**Tertiary** (four roles) — use for contrasting accents that balance primary and secondary colors, or bring heightened attention to an element such as an input field. Tertiary roles can be applied at the designer's discretion; they're intended to support broader color expression.
| Role | Use |
|---|---|
| Tertiary | Complementary fills, text, and icons against surface |
| On tertiary | Text and icons against tertiary |
| Tertiary container | Complementary container color against surface, for components like input fields |
| On tertiary container | Text and icons against tertiary container |

**Error** (four roles) — use to communicate error states, such as an incorrect password entered into a text field. **Error is an example of a static color** (it doesn't change even in dynamic color schemes); error roles are made static by default with any dynamic color scheme, but **still adapt to light and dark theme**.
| Role | Use |
|---|---|
| Error | Attention-grabbing color against surface for fills, icons, and text, indicating urgency |
| On error | Text and icons against error |
| Error container | Attention-grabbing fill color against surface |
| On error container | Text and icons against error container |

**Surface** — use for more neutral backgrounds, and container colors for components like cards, sheets, and dialogs. **Three surface roles:**
| Role | Use |
|---|---|
| Surface | Default color for backgrounds |
| On surface | Text and icons against any **surface** or **surface container** color |
| On surface variant | Lower-emphasis color for text and icons against any **surface** or **surface container** color |

**Five surface container roles**, named by level of emphasis: **Surface container lowest** (lowest-emphasis container color), **Surface container low** (low-emphasis), **Surface container** (default container color), **Surface container high** (high-emphasis), **Surface container highest** (highest-emphasis). **Surface container is the default role**; the others are especially helpful for creating hierarchy and nested containers in layouts for expanded screens.

**Inverse colors** — applied selectively to components to achieve colors that are the reverse of the surrounding UI, creating a contrasting effect.
| Role | Use |
|---|---|
| Inverse surface | Background fills for elements which contrast against surface |
| Inverse on surface | Text and icons against inverse surface |
| Inverse primary | Actionable elements, such as text buttons, against inverse surface |

**Outline** — two outline colors to be used against a surface.
| Role | Use |
|---|---|
| Outline | Important boundaries, such as a text field outline |
| Outline variant | Decorative elements, such as dividers, and when other elements provide 4.5:1 contrast |

**Add-on color roles** — "Most products won't need to use these add-on color roles. However, some products require the greater flexibility and control that add-on roles provide. **If you aren't sure whether your product should use the add-on roles, it probably shouldn't and you can ignore them.**"

*Fixed accent colors:* **Primary fixed, secondary fixed, tertiary fixed** are fill colors used against surface. They **maintain the same tone in light and dark themes**, as opposed to regular container colors which change tone between themes. Use a fixed role instead of the equivalent container role where such fixed behavior is desired. **Primary fixed dim, secondary fixed dim, tertiary fixed dim** provide a **stronger, more emphasized tone** relative to the equivalent fixed color; use where a deeper color but the same fixed behavior is desired.

*On fixed accent colors:* **On fixed** colors are for text and icons sitting on top of the corresponding fixed color (e.g. **on primary fixed** on **primary fixed**). **On fixed variant** colors are for text and icons needing **lower emphasis** against the corresponding fixed color (e.g. **on primary fixed variant** for low-emphasis text/icons against **primary fixed**). Same usage applies for secondary and tertiary equivalents.

*Bright and dim surface roles* — two add-on surface roles:
| Role | Use |
|---|---|
| Surface dim | Dimmest surface color in light and dark themes |
| Surface bright | Brightest surface color in light and dark themes |

Inversion behavior: default **surface** automatically inverts between themes (light color in light theme, flips to dark in dark theme). **Surface bright** and **surface dim** invert differently — they **keep their relative brightness across both light and dark theme**. With default **surface**, the mapped area is the brightest in light theme and the dimmest in dark theme; with **surface bright**, the mapped area is the brightest in **both** themes.

### 4. Placement — regions, slots, window size classes

- Most common combination: **surface** for a background area, **surface container** for a navigation area.
- Text and icons typically use **on surface** and **on surface variant** on all types of surfaces.
- **All color mappings — but especially surface colors — should remain the same for layout regions across window size classes.** E.g. the body area uses **surface** and the navigation area uses **surface container** on both mobile and tablet.
- Depending on necessary hierarchy, feature area, and design logic, you can use **add-on surface colors** in larger window class sizes **as long as colors are consistently applied**. Example: body and navigation regions keep the same roles across mobile, foldable, and tablet (**surface** and **surface container**), with the addition of other surface container colors at larger sizes.
- Default surface container roles applied to components (from diagram): **Surface container low** → elevated button and card; **Surface container** → top and bottom bar; **Surface container high** → FAB and basic dialog; **Surface container highest** → input label and off switch. By default neutral-colored components such as navigation bars, menus, or dialogs are mapped to specific surface container roles, but these roles **can be remapped** by makers to suit user needs.

### 6. Color role mapping — worked component examples

| Component / part | Role |
|---|---|
| Filled button container | Primary |
| Filled button text | On primary |
| FAB container | Primary container |
| FAB text and icon | On primary container |
| FAB container (fixed variant) | Primary fixed |
| Icon button container (fixed dim example) | Primary fixed dim |
| Icon button container | Secondary container |
| Icon on that icon button | On secondary container |
| Selected element background | Tertiary container |
| Selected element text | On tertiary container |
| Snackbar background | Inverse surface |
| Snackbar text | Inverse on surface |
| Snackbar text button | Inverse primary |
| Text field container border | Outline |
| List item divider line | Outline variant |
| Main app background (body region) | Surface |
| Navigation bar / navigation region background | Surface container |
| Navigation rail background (large screen example) | Surface dim |
| Chat window background (large screen example) | Surface bright |
| Custom banner, deemphasized text | On primary fixed variant |
| Custom banner, emphasized text | On primary fixed |

### 9. Do / Don't

**Pairing and layering**
- **Do** apply colors only in the intended pairs or layering orders. Combining colors improperly may break contrast necessary for visual accessibility, particularly when colors are adjusted through dynamic color features such as user-controlled contrast.
- Correct example: two buttons mapped with (1) **primary**, (2) **on primary**, (3) **secondary container**, (4) **on secondary container** stay legible as contrast level changes.
- Incorrect example: two buttons mapped with (1) **primary**, (2) **primary container**, (3) **secondary container**, (4) **on surface** become illegible as contrast level changes.

**Container / On**
- **Don't** use container roles for text or icons — they are fill colors for foreground elements.

**Outline**
- **Don't** use the **outline** color for dividers, since they have different contrast requirements. Instead use **outline variant**.
- **Don't** use the **outline** color for components that contain multiple elements, such as cards. Instead use **outline variant**.
- **Don't** use the **outline variant** color to create visual hierarchy or define the visual boundary of targets. Instead use **outline** or another color providing **3:1** contrast with the surface color.
- **Do** use **outline variant** for the border of targets like chips and buttons, **provided** those targets contain elements inside them that provide visual contrast (e.g. icons and text inside meeting **4.5:1** contrast).

**Fixed**
- Fixed colors don't change based on light or dark theme, so they're **likely to cause contrast issues**. **Avoid using them where contrast is necessary.** Use **primary**, **secondary**, and **tertiary** roles for accent colors where contrast is needed. (Counter-example shown: Primary Fixed incorrectly used for a button fill on a Surface background.)

**Accent**
- Use caution when changing color roles for visual effect.

**Add-on**
- If you aren't sure whether your product should use add-on roles, it probably shouldn't.

### 10. Accessibility

- Color pairs provide an **accessible minimum 3:1 contrast**.
- **Outline variant** is for decorative elements and for use when other elements provide **4.5:1** contrast.
- Replacement for **outline variant** on target boundaries must provide **3:1** contrast with the surface color.
- Improper mappings break contrast, most visibly when user-controlled contrast changes.

---

## Choosing a scheme (static vs. dynamic)

### 1. What it is + the discriminating rule

**Static color schemes emphasize brand and uniformity, while dynamic schemes emphasize content or user settings to make products feel more personal.** A color scheme describes all of a product's colors, color roles, and color relationships across light and dark themes. Two kinds: **static**, **dynamic**.

Onboarding note: **working with static color will be the most like other color workflows you may have used.** Next steps in the source flow: choosing baseline → start designing with the baseline colors; choosing dynamic → pick a dynamic color source.

### 3. Variants — side-by-side

| | Static (baseline) | Dynamic |
|---|---|---|
| Behavior | Colors won't ever change based on user input or in-app content. Material provides a static baseline scheme including default color assignments and mappings. | Automatically creates an accessible color scheme based on a specific source color. |
| **What you get** | ✓ Accessible colors · ✓ Pre-made baseline color scheme · ✓ Colors that won't break an M2 app · ✓ Ability to easily update to dynamic color in the future | ✓ Accessible colors · ✓ Personalized colors that change based on a user's wallpaper or in-app content · ✓ Ability to use advanced customizations like chroma fidelity to alter the dynamic color output · ✓ User-controlled contrast settings |
| **What you don't get** | ✗ Personalized colors · ✗ Colors that change based on user's wallpaper or in-app content · ✗ User-controlled contrast settings | ✗ Exact same UI colors across all devices |

**Use static (baseline) color if:**
- You're not ready to implement dynamic color (though it'll be easy to switch when you are)
- Your product is migrating from M2 and you want to get M3 features without breaking your app
- Your product is for enterprise users who wouldn't benefit from personalized color or user-controlled contrast settings
- Your product is built for iOS

**Use dynamic color if:**
- You want your product to showcase personalization
- You want the colors to change base on a user's wallpaper or in-app content
- You want your product to offer user-controlled contrast settings
- You aren't sure if you'll need to also use a mix of dynamic and static colors (you can customize your scheme to include static colors as your work progresses)

### 9. Do / Don't

- **Do** initially design a dynamic-color UI **using the baseline color scheme**, so you can ensure the right color roles are mapped to the right components. Because the UI could end up with any number of different source colors, use the Material Theme Builder to see how your UI mocks look across a range of source colors and adjust as needed.
- While the actual colors may change, **the color role mappings remain the same** across dynamic color schemes.

---

## Static color schemes

### 1. What it is + when to use it vs. siblings

**Static color schemes are ideal for branded products that should have a consistent, uniform design.** Two sub-variants documented: **Baseline** and **Custom brand**.

- **Baseline** is the **default** static color scheme. It uses accessible color pairings and includes colors for both light and dark themes. With baseline, end-users see: an accessible UI with static colors.
- **Custom brand**: colors are hand-picked by your team to align with your product's brand color. Brand-based schemes are **entirely created and maintained by your team**, so this approach **requires a larger investment of time and effort**. End-users see: an accessible UI with static colors; a product that "looks like its brand."

### 3. Variants / configurations — procedures

**Baseline — new design files**
1. Create your Figma file. Enable the M3 Design Kit in your Assets panel.
2. Compose screens and layouts using Material Components from the design kit.
3. Apply M3 baseline color roles to custom components and UI elements by hovering on the element's color property in the Design panel and selecting the **Style** icon (four dots) → selection dialog.
4. Search for "M3" to see the baseline color roles.
5. Select the baseline color role that most closely matches the use case and intent.
6. Repeat until all custom elements use M3 baseline color roles.

**Baseline — existing file**
1. Open the Figma file. Select the **Actions** menu (or Ctrl/Command+K).
2. Find the Material Theme Builder plugin → **Run**. Dialog shows the default color scheme, including **Core colors** and **Extended colors**.
3. Open plugin **Settings** (gear icon, lower right) → check **Generate State Layers** (ensures colors exist for the state layers needed to design interactions).
4. Navigate out of settings.
5. In the **Current Theme** dropdown at top, select **Baseline**.
6. Select frames/components → **Swap** (bottom right). Automatically updates colors for any M3 Design Kit components.
7. Then update remaining non-M3 color styles: manually change hex values / non-M3 styles by selecting all and reviewing **Selection colors** in the Design panel. Any colors not starting with "M3" must be replaced with a corresponding baseline color. Hover a non-M3 color row → **Style** icon (four dots) → search "M3" → select closest-matching baseline role → **Use style**. Repeat until all non-M3 colors are replaced.

**Create a custom brand color scheme**
1. Open Figma file → **Actions** menu (Ctrl/Command+K).
2. Material Theme Builder plugin → **Run**.
3. Plugin **Settings** → check **both** **New theme color diagram** and **Generate State Layers** (creates a visualization of the branded scheme and generates state layers essential for designing interactions).
4. Navigate out of settings.
5. **Current Theme** dropdown → **+ ADD NEW THEME**.
6. Give the theme a **short name** — *this name becomes the prefix of your color roles in Figma*.
7. Select **ADD THEME**.
8. With **Custom** selected, select **Primary** → dialog to select a custom source color.
9. Enter the **Hex** value for your brand color → **Apply**. This generates a full custom color scheme.
10. Use the scheme as-is, or repeat steps 5 and 6 to set custom sources for **Secondary, Tertiary, Error, Neutral, and Neutral Variant** colors.

**Design with brand colors — new files:** enable M3 Design Kit; copy your scheme's color diagram and paste it into the file (makes the color roles available in the Design panel as part of your local styles); apply roles via the **Style** icon; search your theme's name; pick the closest-matching role; repeat until all custom elements use brand roles.

**Apply brand colors to an existing file / M3 Design Kit components:** paste the scheme's color diagram into the file; run Material Theme Builder; select your scheme in **Current Theme**; select frames or M3 Design Kit components → **Swap** (updates from baseline colors to brand colors); then manually replace any color not starting with your theme name via **Style** icon → search theme name → **Use style**; repeat until done.

**Develop with brand colors:** export the branded color scheme from Material Theme Builder — available for **Jetpack Compose, Android Views, Flutter, Web, or as a JSON file**. Android: customize the default theme.

### 6. Color role mapping

Baseline scheme colors are documented as swatch sets for **light theme** and **dark theme** ("the entire baseline color scheme and derivative accent colors"). Get baseline colors in Figma using the Material Theme Builder.

---

## Dynamic color schemes

### 1. What it is + when to use each source

**Dynamic color can change a color palette to match user settings, like wallpapers, or in-product content.** Two ways to get a source color: **user-generated color** from a user's wallpaper; **content-based color** from in-app content like a music album or book cover. **Both types are accessible and personalized, so deciding which to use is based on what's most important in the product: content or user preference.**

**Choose user-generated color if:**
- Your users would benefit from a personalized experience that's tested well
- You want your product to showcase the latest and greatest Material features

**Choose content-based color if:**
- Content is front-and-center in your product
- Your team can do a bit of advanced customization
- Content-based color would support usability of specific features like media players
- Content-based color is best used for **contained screen elements adjacent to the source image**, though the source image is not always visible

**Choose multiple color sources if:**
- Your product requirements meet multiple criteria above
- You don't mind doing a bit of advanced customization
- Get started with user-generated color **before** customizing.

### 2. Anatomy / mechanism

- **User-generated color** comes from an Android user's personal wallpaper. The wallpaper is digitally analyzed, a single color is selected as the source color, and tones are chosen and assigned to each color role. End-users see: their apps and system UI change to a color pulled from their device wallpaper; a product that looks personalized.
- **Content-based color** comes from in-app content, such as an album thumbnail image, logo, or video preview. Like user-generated color, the image is digitally analyzed through **quantization**, a single color is selected as the source color, and tones are chosen and assigned to each color role. End-users see: the product (and possibly system UI) change to a color corresponding to on-screen imagery; a product that looks "smart."

### 3. Configurations — procedures

**Use Material color roles in new design files (user-generated)**
1. Open Figma file → **Resources** button in the Figma toolbar.
2. Material Theme Builder plugin → **Run** (dialog shows default scheme with **Core colors** and **Extended colors**).
3. **Settings** → check **both** **New theme color diagram** and **Generate State Layers**.
4. Navigate out of settings.
5. **Current Theme** dropdown → **+ ADD NEW THEME**.
6. Give the theme a short name (becomes the prefix of your color roles in Figma).
7. **ADD THEME**.
8. With **Custom** selected, select **Primary** → custom source color dialog.
9. Enter the Hex value → **Apply** → generates a full color scheme.
10. **Current Theme** dropdown → select your theme.
11. Select frames/components → **Swap** → updates colors for any M3 Design Kit components.

**Apply color roles to an existing file / M3 Design Kit components:** copy your preferred scheme's color diagram from your Material Theme Builder file and paste it into your file (makes roles available in the Design panel as local styles); **Resources** → run Material Theme Builder → select your scheme in **Current Theme** → select frames or M3 Design Kit components → **Swap**; then manually replace any color not starting with your selected scheme name: **Style** icon (four dots) → search scheme name → select closest-matching role → **Use style**; repeat until all non-color-role-based colors are replaced.

**Try out how your designs will look with dynamic color:** **Resources** → run Material Theme Builder → select **Dynamic** → add an image, or select the **Shuffle** icon to get a random source color → select frames/components → **Swap** → **repeat with a range of colors to get a sense of how your product will appear across different users' devices.**

**Develop with user-generated color:** Android Views (MDC-Android) — Color docs. **Develop with content-based color:** MDC-Android — Content-based dynamic color.

### 4. Placement

- Content-based color is best used for **contained screen elements adjacent to the source image**.
- In-app content provides a color source for any content-based scheme, and **can be applied within a specified area of an app, such as a set of components or a particular screen**.

### 9. Do / Don't

- **Do** apply content color in apps and areas where it can enhance brand identity and convey the spirit of personalization. E.g. a music app deriving color from a specific album's artwork to build on the personal connection to a music library; for a news feed, content-based color applied from a given publication to differentiate brands and help users navigate the platform.
- **Do** understand and apply the system's **color roles** in your designs rather than use a particular hex value, because the final colors are dynamically generated on each user's personal device. Easiest way: use a scheme generated by the Material Theme Builder and focus on applying color roles, not hex values; then test how well the design functions across potential user-generated color options.
- **Do** check that the preferred scheme is selected when using Material Theme Builder to create color schemes from images. Use the color tokens and roles built into the Theme Builder.

---

## Advanced customizations

### 1. What it is + when to use it vs. siblings

**Apply, define, or adjust colors to create a fine-tuned, unique color experience.** From changing a component's default color mapping to creating additional color roles, advanced customizations fall within one of three general actions: **applying, defining, or adjusting** colors.

| Action | Techniques |
|---|---|
| **Apply colors** (in places or ways not provided by default) | Combine multiple color schemes; Map or remap colors onto UI elements |
| **Define new colors** (add to your scheme, extending the default color roles) | Define static colors (formerly known as custom colors); Define custom color roles (to use alongside the **26+ standard color roles**) |
| **Adjust existing colors** (control the color algorithm's output) | Define your own baseline scheme; Define your own dynamic scheme; Use color fidelity; Harmonize colors |

### 3. Variants / configurations

#### Combine multiple color schemes
Use multiple color schemes in the same app experience, such as a baseline scheme combined with a dynamic content-based scheme.
- **Why:** if your app features content-rich moments, such as a media player, applying local color based on that content can enhance a user's experience.
- **How:** start from a **baseline** or **user-generated dynamic** scheme to create a consistent color foundation. On top of that foundation, **map content-based color roles to contained spaces** to emphasize or celebrate content.
- Example: smart home control screen combining a **teal content-based scheme** from local album art applied to media controls, plus a **red user-generated scheme** from the user's wallpaper applied to the rest of the UI.

**Best practices**
- Consider where content exists in the UI and where content-based color can enhance a person's experience; your existing app structure can suggest contained areas for content-based color to live.
- **Build hierarchy & direct attention:** when many types of information and actions share a screen, use content-based color to add hierarchy and draw attention to the content.
- **Link and associate content on a screen:** in lists and collections of repeated items that benefit from differentiation, content-based color can help associate related elements — e.g. a list item and its associated action.
- **Immerse users in content color:** full-screen content-based color moments can orient users within a content-driven experience, such as a media control or a purchase flow.
- **Pair content-based color with its source content:** keep the source visible on a screen using the content color so users are shown where it originates. **Avoid applying content-based color in spaces where the content itself isn't visible.**
- **Limit the number of color source types per screen:** **limit a screen to two color schemes from different source types.** Too many schemes on the same screen may lead to confusion and visual disarray. E.g. a baseline or user-generated scheme combined with one type of on-screen content (such as album art).
- **Don't replace semantic colors:** use caution when applying content-based color where a semantic or conventional color meaning is important for usability. A common red error message or a common green positive action **shouldn't** be replaced with dynamic content-based color, because it may interfere with someone's understanding.

#### Map or remap colors on UI elements
Change a component's default color mapping, or apply colors to your own custom components.
- **Why:** to improve a component's function (such as visual contrast) or style.
- **How:** choose an appropriate color role based on how the color is used and how well the role supports your intended design expression. In Figma: select the component/element to see its colors in the Design panel → hover the color row → **Style** icon (four dots) → search your theme name → select the closest-matching role (e.g. a component background → **surface**; text or icons → **on surface**) → **Use style** → repeat until all colors in the component are replaced with color roles from your scheme.
- **Best practices:** use color roles that support Material's contrast requirements for the component. **Any color roles starting with "on-" are guaranteed to have sufficient contrast with the corresponding color role. Other color role pairs may not meet the 4.5:1 (small text) and 3:1 (large text) Material contrast requirements.** If applying a dynamic scheme, test the component under different themes (light and dark; red, yellow, green and blue). **Always apply color roles rather than static values or tonal palette values**, as these colors will break with light and dark themes, contrast control, and other features; if a role's color doesn't meet your needs, define new colors or adjust existing colors.

#### Define static colors (*formerly known as custom colors*)
Define additional colors in your scheme that **stay static even when other colors dynamically change**. Input a desired reference color and **Material returns four derived color roles** that align with the design of existing roles in the scheme.
- **Why:** brand expression or semantic meaning, like a green success state. Defining them using the Material system means they work with existing Material colors and support features like dynamic color and user-controlled contrast.
- **How:** use Material Theme Builder to input a custom color; Material returns four roles derived from that reference color — **the main color, on-main color, container color, and on-container color** — all following the conventions of the accent colors in the main scheme, appliable by the same relationships.
- Worked example: a static green called **Success** generates four roles — **Success, On Success, Success Container, On Success Container**; **On success container** applied to a WiFi icon and **Success container** applied to a card container.
- **Best practices:** if returned colors appear differently than expected, enable or disable **color fidelity**. **Material provides the red Error color out of the box as an example of a static color, so you do not need to define your own static color for a semantic red color.** If using static colors in a dynamic scheme, you can **harmonize** them to the scheme's primary color — shifting hues slightly warmer or cooler for a more harmonious appearance while retaining the semantic meaning associated with the hue range. Colors can stay completely static and forgo harmonization if their values are tied to literal sources, such as brand colors or real-world signage (e.g. color-coded subway lines).

#### Define custom color roles
Define custom roles in addition to those in the scheme. By defining them **the same way Material does — specifying a reference palette, starting tones, and contrast requirements** — these roles achieve colors more specific to your needs while working seamlessly with features such as user-controlled contrast.
- **Why:** the scheme's existing colors or additional static colors don't meet your product's needs. In particular, **create them within the Material system** to respect dynamic colors and unlock other features like user-controlled contrast.
- **How — specify:**
  - **Palettes and reference tones:** for each role, assign its value from a Material palette (**primary, secondary, tertiary, neutral, neutralVariant, error**) and a reference tone (for example: primary70, primary80, primary90…) for **both light and dark themes**.
  - **Color pairings:** specify any visual relationships in your design, such as color pairs used together as foreground and background, or which should retain a **tone delta** between them (difference in lightness or darkness).
  - **Contrast:** confirm custom foreground/background pairings meet Material's contrast minimums.
  - Then define the new roles in your own dynamic color object; for each role, call **Material Color Utilities (MCU)** to generate the color value dynamically according to conditions such as user theming or contrast level.
- Worked example: primary tonal palette with **tone 50** specified as the **primary graphic** default value; **3:1** contrast between **primary graphic** and **primary container**; **primary graphic** applied to a large weather icon in a weather widget against **primary container**.
- **Best practice:** **defining custom color roles should be considered only if you cannot achieve your desired colors with other Material color solutions.**

#### Define your own baseline scheme
Input colors to define your own baseline scheme.
- **Why:** so your app's colors stay static (does not change with dynamic color), such as to reflect brand colors. By providing custom input colors for the primary, secondary, tertiary, and neutral colors, Material returns the scheme's regular color roles with values derived from your reference colors.
- **How:** in Material Theme Builder, input your own colors for **primary, secondary, tertiary, neutral, and neutral variant**. The generated roles can be used in the same manner as those from any other Material scheme.
- **Best practices:** **conventionally, primary and tertiary colors are the most visually prominent in the scheme, with tertiary appearing complementary to primary by changing its hue. Secondary, neutral variant, and neutral colors match primary in hue but are progressively less chromatic in that order.** Input your colors into the appropriate category to maintain similar relationships as designed by Material, **and to ensure expected and visually pleasing results when those colors are mapped to components**. If returned colors appear unexpected, enable/disable color fidelity (**a feature that adjusts colors' tones to match that of your input color**). If the **26+ standard color roles** don't meet your needs, define custom color roles.

#### Define your own dynamic scheme
Define color algorithm rules to produce your own dynamic scheme.
- **Why:** control your app's colors while respecting dynamic color — e.g. match the user's wallpaper theme but appear **more vibrant** than default dynamic theme colors.
- **How:** Material generates the scheme by following **hue and chroma values specified for each group of colors (primary, secondary, tertiary, neutral, and neutral variant)**. To produce your own dynamic scheme, provide your own hue and chroma values for each group; then define your own **scheme variant** and call MCU to dynamically generate the scheme and provide color values for each role.
- **Best practices:** consider custom roles only if you cannot achieve your desired colors otherwise; enable/disable color fidelity if colors appear unintended; define custom color roles if the out-of-the-box roles don't meet your needs.

#### Use color fidelity
Color fidelity **adjusts colors' tones to match that of your input color** — apply it to make scheme colors better match your input colors.
- **Why:** Material scheme colors are mapped to tones (lightness or darkness) to achieve visually accessible pairings with sufficient contrast between foreground and background. In some cases these tones can prevent colors from appearing as intended, such as when a color is too light to appear vibrant. **Color fidelity adjusts tones in these cases to produce the intended visual results without harming visual contrast.**
- **How:** in Material Theme Builder, toggle the **"match color"** option on your input color to enable or disable fidelity. **By default, fidelity is enabled when you use Theme Builder to create a custom baseline scheme or define static colors.** In code, flag color roles in your scheme with a **boolean** to enable/disable fidelity for those colors.
- **Best practices:** when producing a custom baseline scheme or defining static colors, toggle fidelity on and off to determine which setting better suits your design. Because fidelity adjusts tones, **remember to pair appropriate color roles together, such as a background color with its corresponding foreground "on" color**, to ensure accessible contrast.

#### Harmonize colors
In dynamic schemes, automatically adjust the **hue** of static colors so they look better alongside the scheme's primary color. Material provides this as an **optional 'harmonize' function** that slightly adjusts static colors to look better in dynamic schemes.
- **Why:** static colors may visually clash with a scheme's dynamically changing colors. Colors closer in hue appear more pleasing together than colors with hues farther apart; harmonization adjusts the hue of static colors, making them closer to the hue of the scheme's **primary** color.
- **Semantic guardrail:** to preserve semantic meaning (such as a red communicating errors), **harmonization limits the amount that a color's hue can change**. Harmonized colors become warmer or cooler in hue without appearing like another type of color — e.g. a red can become cooler or warmer but **will not appear purple or orange**.
- **How:** in Material Theme Builder, toggle harmonization on/off within the **overflow menu** for each static color added to the scheme. In code, use the **'Blend' function** from Material Color Utilities.
- **Best practices:** harmonization adjusts a static color differently depending on the scheme's primary color, so **check results under a variety of schemes**. **Don't harmonize colors whose appearance should stay absolutely consistent, such as brand colors.**

### 9. Do / Don't (consolidated imperatives)

- Always apply color roles rather than static values or tonal palette values.
- Limit a screen to two color schemes from different source types.
- Keep the source content for content-based color visible on screen; avoid content-based color where the content isn't visible.
- Don't replace semantic or conventional colors (red error, green positive action) with dynamic content-based color.
- Don't harmonize brand colors or colors tied to literal sources such as real-world signage.
- Don't define custom color roles unless no other Material color solution works.
- Test dynamic mappings across light/dark and across red, yellow, green, and blue themes.

### 10. Accessibility

- Roles starting with **"on-"** are guaranteed to have sufficient contrast with the corresponding role; other pairs may not meet the **4.5:1 (small text)** and **3:1 (large text)** Material contrast requirements.
- Custom foreground/background pairings must meet Material's contrast minimums.
- Custom-role example pairing: **primary graphic** vs. **primary container** at **3:1**.

---

## Gaps noted (present as headings/links in source, but with no published spec values)

- `styles_color_static.md` contains a **"Baseline color tokens"** heading with **no token names or hex values** under it — the baseline token list is not published on the page.
- Baseline light/dark scheme colors exist only as **image swatches** (alt text: "the entire baseline color scheme and derivative accent colors"); **no hex values** appear in the source text.
- **Scrim** and **Shadow** roles are named only inside a diagram alt text ("all 45 color roles including … Scrim and Shadow roles"); the source gives **no usage guidance or definitions** for them.
- No dp/sp measurements, `md.sys.*` / `md.comp.*` token strings, corner-radius tokens, typography role names, or breakpoint dp values appear anywhere in these six pages.
- No **"M3 Expressive update"** section exists on any of these six pages (verified by full-text search).
- Source inconsistency, preserved as-is: on the outline-variant "can be used for borders of chips and buttons" figure, the caption permits the usage while the alt text reads "Outline variant incorrectly color used for chips." The caption's guidance is the one reflected above.
