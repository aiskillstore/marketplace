# Transitions, easing, and the legacy motion system

> Extracted from m3.material.io: `styles/motion/transitions`, `styles/motion/easing-and-duration`, and the
> `m3-expressive-motion-theming` blog. For the physics system itself see `motion.md`; for spring and
> easing numeric values see `tokens.md`.

## Motion — Transitions

> Note carried on both sections of the page: **M3 transitions use the legacy easing and duration system. They'll eventually be updated to use the motion physics system.**

### 1. What it is + when to use which pattern

Transitions are short animations that connect individual elements or full-screen views of an app. They are fundamental to a great user experience because they help users understand how an app works; well-designed transitions make an experience feel high quality and expressive. **They should be the top priority for a strong motion implementation.**

**Six common transition patterns**, with the discriminating rule for each:

| Pattern | Use for | Commonly used with |
|---|---|---|
| **Container transform** | Seamlessly transform an element to show more detail (a Card expanding into a details page). Strongest relationship between elements of all patterns; perceived as the most expressive. | Cards, lists, image galleries, search boxes, sheets, FABs, chips |
| **Forward and backward** | Navigating between screens at **consecutive levels of hierarchy** (inbox → message thread). | Lists, cards, buttons, links |
| **Lateral** | Navigating between **peer content at the same level of hierarchy** (swiping between tabs of a content library). | Tabs, carousels, image galleries |
| **Top level** | Navigating between **top-level destinations** (tapping a destination in a Navigation bar). | Navigation bar, navigation rail, navigation drawer |
| **Enter and exit** | Introducing or removing a **component** on screen — within screen bounds (dialog over an app) or crossing screen bounds (nav drawer, bottom sheet). | Within bounds: FABs, dialogs, menus, snackbars, time pickers, tooltips. Beyond bounds: app bars, banners, navigation bar, navigation rail, navigation drawer, sheets |
| **Skeleton loaders** | Transitioning from a temporary loading state to a fully loaded UI. | — |

**Android (MDC-Android) implementation names** for the patterns that have one: container transform → `container-transform`; forward and backward → **`shared-axis`**; top level → **`fade-through`**. (Lateral, enter/exit, and skeleton loaders have no Android implementation link on the source page.)

**Choosing between them:**
- **Container transform** — highly effective at creating a relationship between elements; **the most dramatic pattern in terms of style, reserve it for the right context**. Use for: hero moments that should be expressive; **shallow hierarchies** where you expand an element for more detail then collapse it; creating a seamless connection between elements. Use container transform for hero moments **rather than** forward and backward.
- **Forward and backward** — **both Android and iOS should use platform defaults**. Easy to implement, stays current as platforms update, simple motion style suitable for such a common transition. (Container transform requires custom implementations and may feel excessive when used frequently.)
- **Lateral** — for browsing peer content in the same set; sliding content horizontally hints at swipe-to-navigate.
- **Top level** — a quick fade; top-level destinations aren't necessarily related, so the motion intentionally does not create a connection between screens.
- **Enter and exit** — introduces a component in context of the screen's main UI. Can be **modal** (dialog requiring action) or allow simultaneous use of both regions (standard bottom sheet over a map).

### 2. Anatomy / mechanics per pattern

- **Container transform:** **persistent elements** seamlessly connect start and end state. The most common persistent element is a **container** — a shape used to represent an enclosed area. It can also be an important element like a **hero image**. Works between full-screen views (carousel image → fullscreen; list item → full message; card + search box → fullscreen) and within a screen (expanding search box; FAB with persistent container **and icon**; expanding sheet from a bottom banner).
- **Forward and backward:** horizontal sliding motion indicates moving forward or backward. Platform defaults differ — **1. Android** uses a **fade as screens slide**, reducing the amount of motion since screens don't have to slide the full width of the device. **2. iOS** uses a **parallax effect** — background slides slower than the foreground, also reducing motion.
- **Lateral:** sliding motion similar to forward/backward but **no fade and no parallax**. Elements are **grouped and slide in unison**, creating a strong peer relationship and hinting at gestural swipe.
- **Top level:** the exiting screen **quickly fades out and then** the entering screen **fades in**. Intentionally **no grouping or persistent elements**.
- **Enter and exit, within screen bounds:** **Android** components **expand and collapse along the x or y axis**. **Scale and z-axis motion is avoided since they imply elevation change, which doesn't match M3's reduced elevation model.** **iOS** components **uniformly scale as they enter and fade out to exit**.
- **Enter and exit, beyond screen bounds:** **Android** components expand and collapse along the x or y axis as they slide on and off screen — this **emphasizes their shape**, making an otherwise simple transition more expressive. **iOS** components slide on and off screen **without changing shape**. Components like a **side sheet** can enter and exit at the **same elevation as the main content**; **coplanar sheets shrink the available area for content**.
- **Skeleton loaders:** UI abstractions that hint at where content will appear once loaded. Used **in combination with other transitions** to reduce perceived latency and stabilize layouts as content loads. They have a **subtle pulsing animation** to indicate indeterminate progress, which **starts at the top left of the screen and moves down to the bottom right**. Once content is loaded, it **quickly fades in on top of** the skeleton loader.

### 4. Placement / direction rules

- **The direction a component enters is informed by its location on screen, expanding away from the device edge.** A menu at the top of the screen expands **downwards**; a snackbar at the bottom expands **upwards**.
- Components can enter and exit from beyond the screen bounds **based on a scroll gesture**, allowing more screen space to browse — e.g. a **top app bar slides off and on screen during a scroll**; a **navigation bar slides off and on screen during a scroll**.
- Entry/exit locations establish a **coherent spatial model**:
  - A **notification** enters from the **top**, indicating the notification drawer can also be pulled down from the top.
  - A **nav drawer** enters from the **left**, helping users understand where it's located when off screen.
  - A **bottom sheet** and the **keyboard** enter from the **bottom** — a sensible default for sheets since the bottom of the screen is easiest to reach.
- Tapping a list item **on a tablet** uses a forward and backward transition.

### 5. Interaction behavior / motion quality — "What makes a good transition?"

- **Follows accessibility settings** — see §10.
- **Consistent** — consistently applying the right type of transition makes apps feel cohesive and predictable (example: four Android apps using the same forward and backward transition read as a cohesive family).
- **Stable layouts** — use skeleton loaders so UI elements are coherent and stable during a transition. **Avoid content shifting positions or instantly popping in as it loads** — distracting and frustrating.
- **No jarring jump cuts** — jump cuts should generally be avoided as a default since they can be disorienting; instantly transitioning offers no clues to help a user orient. **Exception:** if pure efficiency is the top priority, like opening a menu in a productivity app, a jump cut may be preferred.
- **Coherent spatial model** — transitions are used to establish a coherent spatial model, which **helps users understand the physical layout of an app**. E.g. carousel transitions that keep a coherent spatial layout between collapsed and expanded views. Switching between horizontal and vertical carousel layouts creates a confusing spatial model.
- **Unified direction** — elements are **grouped and move along a primary axis** instead of moving in independent directions. **Only important elements like hero images remain persistent** throughout the transition. This guides the user's focus.
- **Clean fades** — **fully fade out content before fading new content in**, to avoid overlap of partially transparent elements producing distracting, messy frames. If a cross fade must occur, **keep it quick and hide it during the fastest part of the transition**. Don't slowly fade components on top of other content as they enter or exit; if a fade is needed (e.g. a Dialog entering in the middle of the screen), the fade should use a **short duration** to hide that part of the transition.
- **Simple style** — transitions are **not receptive to highly stylized motion**: they're frequent, often occupy large portions of the screen, and are primarily meant to help users accomplish a task.

### 9. Do / Don't

**Do**
- Make transitions the top priority for a strong motion implementation.
- Use container transform for hero moments, shallow hierarchies, and seamless element connections.
- Use platform defaults for forward and backward navigation on both Android and iOS.
- Use skeleton loaders to stabilize layouts while loading.
- Group elements and move them along a primary axis.
- Fade content out before fading new content in.

**Don't**
- **Don't use container transform in apps with deep hierarchies** — the motion becomes excessive and the expressive style doesn't fit utility-focused navigation.
- **Don't use forward and backward transitions on hero moments** like opening a photo memory.
- **Don't fade content as it slides in a lateral transition** — it makes the peer relationship and swipe gesture less obvious and may be confused with forward and backward.
- **Don't use a lateral transition for navigating hierarchical screens** — sliding content the full width of the screen is excessive for a high-frequency transition, and it implies an equal peer relationship that isn't accurate.
- **Don't use a lateral transition to move between top level destinations** — it implies you can swipe between them, conflicting with components like carousels or swipe-able list items.
- **Don't use enter and exit for navigating hierarchical screens** — sliding content the full height of the screen is excessive and creates an unclear relationship between screens.
- **Don't animate many persistent elements independently** — the various moving parts are distracting.
- **Don't show cross-faded content**; don't fade a bottom sheet as it enters and exits.
- **Don't use overt style effects like bouncy springs** for common transitions.
- Avoid scale and z-axis motion for Android enter/exit within screen bounds (implies elevation change).

### 10. Accessibility

Most platforms have a **reduced animation setting** for users with motion sensitivity. **If that setting is on, transitions should:**
- **Use subtle fades instead of intense sliding or scaling animations.**
- **Disable decorative effects like parallax or shape morphing.**

---

## Motion — Easing and duration (legacy system)

> Note carried on both sections of the page: **In the expressive update, components and motion now use the motion physics system, which uses springs. Products should migrate to the new system. The easing and duration system is still used for transitions and can be used by teams that haven't yet updated to GM3 Expressive, but is no longer maintained.**

### 1. What it is + when to use which set

Easing and duration create responsive and expressive motion. In the physical world objects don't start or stop instantaneously — they take time to speed up and slow down. Transitions without easing look stiff and mechanical; with easing they appear more natural. Compared to the utilitarian style of M2, **M3 easing is more expressive: snappy take offs and very soft landings.** Durations are **slightly longer** than M2, giving transitions time to come to a gentle rest without feeling abrupt.

- **Emphasized easing set** — recommended for **most** transitions, to capture the style of M3. Most common because it captures the expressive style of M3.
- **Standard easing set** — for **small utility-focused transitions that need to be quick**; also the **fallback for platforms that don't support Emphasized easing, like iOS and Web**. Used for simple, small, or utility-focused transitions.

### 3. Suggested easing + duration pairs

Choosing the right combination of easing and duration **can be complicated**; the table below is the source's set of **sensible defaults that will work for most transitions** — use it as a starting point.

| Easing | Duration | Transition type |
|---|---|---|
| Emphasized | 500ms | Begin and end on screen |
| Emphasized decelerate | 400ms | Enter the screen |
| Emphasized accelerate | 200ms | Exit the screen |
| Standard | 300ms | Begin and end on screen |
| Standard decelerate | 250ms | Enter the screen |
| Standard accelerate | 200ms | Exit the screen |

**Choosing an easing type** — chosen by how a transition moves in relation to the screen:
- **Begin and end on screen** → **Emphasized**. Speeds up quickly then comes to a gentle rest, emphasizing the end of the transition.
- **Enter the screen** → **Emphasized decelerate**. Begins at peak velocity then comes to a gentle rest.
- **Exit the screen permanently** → **Emphasized accelerate**. Begins at rest and ends at peak velocity; ending at peak velocity gives the impression the exiting component **cannot** be retrieved.
- **Exit the screen temporarily** → **Emphasized**. Ending at rest just off screen gives the impression the exiting component **can** be retrieved. (Example: a drawer enters and exits temporarily with Emphasized easing.)

### 3a. Easing tokens and platform values

**Emphasized easing set**

| Info/Platform | Emphasized | Emphasized decelerate | Emphasized accelerate |
|---|---|---|---|
| Token | `md.sys.motion.easing.emphasized` | `md.sys.motion.easing.emphasized.decelerate` | `md.sys.motion.easing.emphasized.accelerate` |
| Android | `pathInterpolator(M 0,0 C 0.05, 0, 0.133333, 0.06, 0.166666, 0.4 C 0.208333, 0.82, 0.25, 1, 1, 1)` | `PathInterpolator(0.05f, 0.7f, 0.1f, 1f)` | `PathInterpolator(0.3f, 0f, 0.8f, 0.15f)` |
| CSS | N/A (Use Standard as a fallback) | `cubic-bezier(0.05, 0.7, 0.1, 1.0)` | `cubic-bezier(0.3, 0.0, 0.8, 0.15)` |
| Flutter | `easeInOutCubicEmphasized` | `Cubic(0.05, 0.7, 0.1, 1.0);` | `Cubic(0.3, 0.0, 0.8, 0.15);` |
| iOS | N/A (Use Standard as a fallback) | `ControlPoints:0.05f:0.7f:0.1f:1.0f];` | `ControlPoints:0.3f:0.0f:0.8f:0.15f];` |
| After Effects | Use After Effects Easing Panel (download) | — | — |

**Standard easing set**

| Info/Platform | Standard | Standard decelerate | Standard accelerate |
|---|---|---|---|
| Token | `md.sys.motion.easing.standard` | `md.sys.motion.easing.standard.decelerate` | `md.sys.motion.easing.standard.accelerate` |
| Android | `PathInterpolator(0.2f, 0f, 0f, 1f)` | `PathInterpolator(0f, 0f, 0f, 1f)` | `PathInterpolator(0.3f, 0f, 1f, 1f)` |
| CSS | `cubic-bezier(0.2, 0.0, 0, 1.0);` | `cubic-bezier(0, 0, 0, 1);` | `cubic-bezier(0.3, 0, 1, 1);` |
| Flutter | `Cubic(0.2, 0.0, 0, 1.0);` | `Cubic(0, 0, 0, 1);` | `Cubic(0.3, 0, 1, 1);` |
| iOS | `ControlPoints:0.2f:0.0f:0.0f:1.0f` | `ControlPoints:0.0f:0.0f:0.0f:1.0f` | `ControlPoints:0.3f:0.0f:1.0f:1.0f];` |
| After Effects | Use After Effects Easing Panel (download) | — | — |

### 3b. Duration tokens

**Choosing a duration.** Transitions shouldn't be jarringly fast or so slow that users feel they're waiting; **the right combination of duration and easing produces smooth and responsive transitions.**
- **Transition size** — transitions covering **small areas** have **short** durations; those traversing **large areas** have **long** durations. Scaling duration with the size of the transition area gives a consistent sense of speed. (Example: a small-area transition uses **200ms**; a large-area, screen-takeover transition uses **500ms**.)
- **Enter vs. exit** — transitions that **exit, dismiss, or collapse** use **shorter** durations, because they require less attention than the user's next task. Transitions that **enter or remain persistent** use **longer** durations, helping users focus on what's new. (Example pairing repeated twice: **Enter = 500ms, Exit = 200ms**.)

| Group | Token | Value |
|---|---|---|
| Short — small utility-focused transitions | `md.sys.motion.duration.short1` | 50ms |
| | `md.sys.motion.duration.short2` | 100ms |
| | `md.sys.motion.duration.short3` | 150ms |
| | `md.sys.motion.duration.short4` | 200ms |
| Medium — transitions traversing a medium area of the screen | `md.sys.motion.duration.medium1` | 250ms |
| | `md.sys.motion.duration.medium2` | 300ms |
| | `md.sys.motion.duration.medium3` | 350ms |
| | `md.sys.motion.duration.medium4` | 400ms |
| Long — often paired with Emphasized easing; large expressive transitions | `md.sys.motion.duration.long1` | 450ms |
| | `md.sys.motion.duration.long2` | 500ms |
| | `md.sys.motion.duration.long3` | 550ms |
| | `md.sys.motion.duration.long4` | 600ms |
| Extra long — rare; above 600ms; usually **ambient transitions that don't involve user input** | `md.sys.motion.duration.extra-long1` | 700ms |
| | `md.sys.motion.duration.extra-long2` | 800ms |
| | `md.sys.motion.duration.extra-long3` | 900ms |
| | `md.sys.motion.duration.extra-long4` | 1000ms |

**Worked component examples given:**

| Case | Duration | Easing |
|---|---|---|
| Selection controls | 200ms | Standard |
| FAB expanding into a Sheet | 400ms | Emphasized |
| Card expanding to full screen | 500ms | Emphasized |
| Ambient carousel auto-advance | 1000ms | Emphasized |
| Text field transition on Web | — | Standard (simple style fits the utility of this component) |
| Full-screen transition / expanding card in a note-taking app | — | Emphasized |
| Bottom sheet | enter / exit | Emphasized decelerate (enter) + Emphasized accelerate (exit permanently) |

### 9. Do / Don't

- **Do** use Emphasized easing for most transitions; use Standard for small/quick utility transitions and as the iOS/Web fallback.
- **Do** scale duration with the area the transition covers.
- **Do** give enter transitions longer durations than exit transitions.
- **Don't** use transitions with such a short duration that they become jarring.
- **Do** migrate to the motion physics system — the easing and duration system is no longer maintained.

---

## Motion physics system (M3 Expressive motion theming)

Source: "Adding Motion Physics with Jetpack Compose" — Rebecca Franks (Developer Relations Engineer, Android), Austin Fisher (Sr. UX Content Designer), Gus Sonoda (Sr. Staff Motion Designer). Special thanks to Material motion designers Gus Winkelman and Gustavo Gonzalez.

### 1. What it is + why it replaces easing/duration

Material 3 Expressive is a preview release; **in version 1.4.0-alpha14 of Material 3** you get a new theming system: **motion**. Previously Material motion was defined through **non-customizable easing and duration values**. The new system is a **customizable motion scheme using motion physics defined through a set of motion properties**, which can be customized or overridden as needed.

Benefits:
- **Centralized control** — define your motion theme once; all Material Components **and your own custom components** inherit it, creating a unified and polished experience and eliminating scattered animation specs.
- **Simplified theming** — stop fussing with individual duration or easing values. Choose from predefined schemes or create your own, using **physics-based spring animations** for a natural and engaging feel.
- **Adaptive animations** — movement feels fast in the context of the device and adjusts based on user input, since animations are **not based on predefined time sets**.

**Why springs:** spring animations appear more natural by allowing the animation to be **interrupted and retargeted** when required. When interrupted and retargeted to a new destination, the spring uses its **current velocity** for a more seamless transition between states than tween. Springs also **adapt to different screen sizes**, since tokens specify **damping and stiffness**, not time — so tokens are always slow or fast in the context of the device.

### 3. Variants — schemes, spec kinds, speeds

**Motion schemes (two presets):**

| Scheme | Behavior | When to use |
|---|---|---|
| **Expressive** | **Overshoots the final values to add bounce.** | **Material's recommended motion scheme**; use for most situations, particularly **hero moments and key interactions**. |
| **Standard** | **Eases into the final values**; a small/minimal amount of bounce (still springs under the hood). | Feels more **functional**; use for **utilitarian products**. |

**The scheme you choose will define how your product feels.** Most motion in a product should use the same scheme; **advanced customizations allow you to swap the scheme to emphasize key moments.** Both schemes are **presets of opinionated motion values** that share the same underlying property names, which makes swapping schemes easy.

**Animation specs (two kinds):**

| Spec kind | Animates | Overshoot |
|---|---|---|
| **Spatial** | Changes in an object's **position, orientation, size, and shape** | **The spring overshoots the final value and bounces into place** |
| **Effect** | An object's properties such as **color and opacity** | **There shouldn't be any overshoot** |

**Speeds (three): default, fast, slow.** Most motion should use the **default** speed; **smaller elements may benefit from fast** and **larger elements from slow**.

| Speed | Spatial example | Effects example |
|---|---|---|
| **Default** | Animations that partially cover the screen, such as **bottom sheets** or **expanded navigation rails** | Opacity of the content within a navigation rail |
| **Fast** | Animations for small components such as **switches** and **buttons** | Color change of the switch handle |
| **Slow** | **Full-screen animations** | Full-screen content refresh |

**Speed tokens work across devices.** The **Spatial "fast"** token will always be faster than **"default"** or **"slow"**, but the **exact values of each token differ depending on whether the device is a wearable, phone, or tablet** — ensuring movement feels fast in the context of the device. This also applies when using spring tokens in a custom motion scheme.

### 5. Application / theming behavior

- **Set up:** use the latest version of Compose Material 3. If you do nothing more than update the Compose dependency, your apps benefit from **applying the standard motion scheme to all your uses of Material Components**.
- **Choosing a scheme:** **most developers won't want to change much** about motion theming — there are two out-of-the-box options, Standard or Expressive. `MaterialExpressiveTheme` at the top level **defaults to the Expressive motion scheme**. Make this choice **once for your application at the theme level**; any Material Components with movement built in will use the selected spec from the theme. `expressive()` = Material-recommended scheme; `standard()` = minimal bounce (both use springs under the hood).
- **Custom scheme:** the power of the system is its flexibility — **tailor the motion scheme to reflect your app's brand or to underscore an important interaction.** For fine-grained control, create your own `MotionScheme` object and return a **different `AnimationSpec` for each property** (article example: a `playfulMotionScheme` that by default adds a lot of bounce). Demonstrated extremes: a **FAB menu with an extra-stiff custom scheme** and a **FAB menu with a very low stiffness custom scheme**.
- **Custom components:** to maintain consistency with other Material Components, ensure your custom components adopt the recommended motion changes and use the motion specs available through **`MaterialTheme.motionScheme`**. Migration example: replace `tween()` calls that animate size and color on press/release — **scale is Spatial motion, color falls under Effects motion** — so map each to the corresponding motion scheme spec. This aligns your component's motion to the overall app experience and lets it adapt automatically when switching between Standard and Expressive schemes/themes.
- **Component coverage:** **in the expressive update, most Material 3 components use the motion physics system by default.** To add the motion-physics system to other components, including custom-built ones, use the specifications above.

### 8. M3 Expressive update content (this page is the update)

- New **motion theming system** in Material 3 **1.4.0-alpha14**.
- Two preset **motion schemes**: Expressive (recommended; overshoots to add bounce) and Standard (eases in; minimal bounce; utilitarian).
- Two **animation spec kinds**: Spatial (position/orientation/size/shape; overshoots) and Effect (color/opacity; no overshoot).
- Three **speeds** per animation: default, fast, slow — device-relative token values (wearable / phone / tablet).
- Springs replace tween for interruptibility, velocity-preserving retargeting, and screen-size adaptivity.
- **Most Material 3 components use the motion physics system by default** in the expressive update.
- **API lifecycle note:** *When 1.4.0 goes to stable, the Material Expressive APIs will move to the next alpha (1.5.0-alphaX), and will no longer be available in 1.4.0. The APIs will go stable in the 1.5.0 release.*
- Cross-page note: M3 **transitions still use the legacy easing and duration system** and will eventually be updated to the motion physics system; the easing/duration system is **no longer maintained**.

### 9. Do / Don't

- **Do** choose the scheme once at the theme level.
- **Do** use Expressive for most situations, hero moments, and key interactions; Standard for utilitarian products.
- **Do** use Spatial specs for position/orientation/size/shape and Effect specs for color/opacity.
- **Do** use the default speed for most motion; fast for small elements, slow for large.
- **Do** route custom-component animations through `MaterialTheme.motionScheme` instead of hardcoded `tween()`.
- **Don't** apply overshoot to color or opacity (use Effect specs).
- **Don't** keep scattered animation specs / individual duration and easing values.
