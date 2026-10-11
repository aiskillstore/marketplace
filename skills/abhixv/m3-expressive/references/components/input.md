# M3 Input & Selection Components — Extracted Reference

Source pages: checkbox, radio-button, switch, sliders, chips, text-fields, search (m3.material.io, updated 2026-07-17).

## Selection Control Triage (stated as the "Alternate selection controls" section on the checkbox and switch pages)

Checkboxes, radio buttons, and switches are the three main selection controls. They all help people make choices, like selecting options or turning settings on and off. (The radio-button page states the same idea more loosely: radio buttons are one of several selection controls, and switches and checkboxes are alternatives that can change settings or preferences — it does not print the three-way table.)

| Use | When |
|---|---|
| Checkbox | Select multiple related options in a list |
| Radio button | Select a single option in a list |
| Switch | Select standalone or more verbose options in a list, like settings |

- Use checkboxes instead of switches if multiple, related options can be selected from a list — checkboxes visually group similar items effectively and take up less space than switches.
- Use radio buttons (not switches) when only one item can be selected from a list.
- Use switches (not radio buttons) if the items in a list can be independently controlled.
- Filter chips can be a good alternative to segmented buttons or checkboxes when viewing a list or search results.
- Consider a drop-down menu instead of radio buttons when saving screen space matters (costs extra clicks and cognitive effort).
- Don't apply density by default to checkboxes, radio buttons, switches, chips, or text fields — it lowers targets below the 48x48 CSS pixel best practice. Offer a density choice instead; keep every target that changes the setting at minimum 48x48 CSS pixels.

---

## Checkbox

### 1. What it is + when to use it vs. siblings
Selection control for selecting one or more options. Use checkboxes (instead of switches or radio buttons) if multiple options can be selected from a list.

Use checkboxes to:
- Select one or more options from a list
- Present a list containing sub-selections
- Turn an item on or off in a desktop environment
- Visually group similar options together

Discriminators: multi-select → checkbox; single select → radio button; standalone/verbose settings → switch. Don't use switches for a list of multiple options; checkboxes imply the items are related and take up less visual space.

### 2. Anatomy
2 parts: 1. Container, 2. Icon.
- Icon is center-aligned in the container.
- A separate state layer element exists (listed in color parts: Checkbox, State-layer, Icon).
- Adjacent text label sits outside the component and is selectable.

### 3. Sizes / variants / configurations
| Attribute | Value |
|---|---|
| Container size | 18dp |
| Container corner shape | 2dp |
| Icon size | 18dp |
| Icon alignment | Center-aligned |
| Target size | 48dp |
| State-layer size | 40dp |

### 4. Placement / responsive layout
(The checkbox page has no "Placement" section; this is its "Responsive layout" section plus caption text.)
- Used in lists of items.
- In expanded breakpoints, placing checkboxes within a contained region such as a side sheet helps group related controls and available actions.

### 5. States and interaction behavior
States: Enabled, Disabled, Hovered, Focused, Pressed.
Selection states: selected, unselected, indeterminate (three states for a parent checkbox).
- Multiple checkboxes in a list can be selected; each can be selected/unselected regardless of the state of others in the group.
- Parent–child relationship: parent checked → all children checked; parent unchecked → all children unchecked; some-but-not-all children checked → parent becomes indeterminate. Checking an indeterminate checkbox checks all child items.
- When selected, a checkbox clearly and instantly communicates its selected state.
- If used to turn something on or off, the action is executed immediately.

### 6. Color role mapping
- Adjacent text label: **on surface** — unchanged even when interacting with the label or component, and identical whether checked or unchecked.
- Colored parts are Checkbox, State-layer, Icon (role names not given in text).
- Selected items are more prominent than unselected items.

### 9. Do / Don't
- Do make the label scannable.
- Do let users select either the text label or the checkbox to select the option.
- Do execute on/off actions immediately.
- Do use a parent checkbox to make selecting many items efficient.
- Don't use switches when a list has multiple selectable options — use checkboxes.
- Don't apply density by default.

### 10. Accessibility
- Target size 48dp; keep targets at minimum 48x48 CSS pixels (density best practice).
- Assistive tech must be able to: navigate to a checkbox; toggle it on and off; get appropriate feedback based on input type.
- Users must be able to select either the text label or the checkbox.
- Accessibility label for an individual checkbox is typically the same as its adjacent text label. If the UI text is correctly linked, the screen reader reads the UI text followed by the component's role.
- Keyboard (as printed on the checkbox page — the table is worded in terms of chips): **Tab** moves focus to enabled chip or chip group; **Space** or **Enter** activates, selects, or deselects the focused chip; **Backspace** or **Delete** removes currently focused input chip; **Arrows** move focus between chips.

### Differences from M2
- Color: new color mappings and compatibility with dynamic color.
- States: new indeterminate states plus error states for unselected, selected, and indeterminate.

---

## Radio button

### 1. What it is + when to use it vs. siblings
Recommended way to allow a single selection from a list of options. Only one radio button can be selected at a time. Use radio buttons (not switches) when only one item can be selected from a list.

Use radio buttons to:
- Select a single option from a set
- Expose all available options

Use radio buttons when there are five or fewer options. Consider a drop-down menu when it's important to save space, accepting the extra clicks and cognitive effort.

### 2. Anatomy
3 elements: Selected icon, Adjacent label text, Unselected icon.
- Always pair a radio button with an adjacent label describing what it selects. Because only one can be selected at a time, each choice must have its own label.

### 3. Sizes / variants / configurations
| Attribute | Value |
|---|---|
| Icon size | 20dp |
| State layer size | 40dp |
| Target size | 48dp |

### 4. Placement
- Often arranged in stacked layouts; should be vertically listed.
- Avoid horizontal radio button lists.
- One option should always be pre-selected (Placement guidance).

### 5. States and interaction behavior
States: Enabled, Hover, Focus, Pressed, Disabled.
- A radio button is either selected or unselected; selecting one deselects any others.
- A radio group can start with one selected, or none selected.
- Once selected, the group can't be deselected. To let people opt out, provide a **Not applicable** or **No option** radio button, or a separate way to deselect all, like **Clear selection**.
- Successfully selected when a person clicks or taps either the radio button icon or the label.
- Selections take effect immediately, unless in a dialog or page that needs to be saved.

### 6. Color role mapping
- Radio button color roles: **primary**, **on surface variant**.
- Adjacent text label: **on surface** — unchanged even when interacting with the label or component, and the same whether selected or unselected.
- Selected items are more prominent than unselected items.

### 9. Do / Don't
- Do accompany radio buttons with clear inline labels.
- Do list radio buttons vertically with one option always selected.
- Don't nest radio buttons.
- Don't allow radio buttons to select multiple options.
- Don't use horizontal radio button lists.
- Don't apply density by default.

### 10. Accessibility
- Target size 48dp; minimum 48x48 CSS pixels per target.
- Assistive tech must be able to: navigate to a radio button; select it; get appropriate feedback based on input type.
- People must be able to select either the text label or the radio button.
- Initial focus: from outside the group, **Tab** moves focus directly to the selected radio button, or the first one if none are selected; **Shift+Tab** focuses the last radio if none are selected. Arrows navigate between options.

| Keys | Actions |
|---|---|
| **Tab** | Moves focus into the group to the selected radio button, or the first if none are selected |
| **Shift** + **Tab** | Moves focus into the group to the selected radio button, or the last if none are selected |
| **Arrows** | Moves focus and selects the previous or next radio button. Wraps focus and selection between the first and last radio buttons. |
| **Space** | Selects a focused radio button. If already selected, does nothing. |

- Labeling: accessibility label for a group is typically the same as its title; role is **Radio group**. Accessibility label for an individual radio button is typically the same as its adjacent text label. Screen reader reads UI text followed by the component's role.

### What's new
- Color: new color mappings and compatibility with dynamic color.

---

## Switch

### 1. What it is + when to use it vs. siblings
Binary control for settings and standalone options: on/off, true/false. Switches are the best way to let people adjust settings. Use switches (not radio buttons) if items in a list can be independently controlled.

Use switches to:
- Toggle a single item on or off
- Immediately activate or deactivate something

Switches control **binary** options, not **opposing** ones. Opposing options (only one of a set selectable at a time, e.g. list vs. map view) require a **connected button group** instead. A switch can't replace a button — people expect a call to action to be a button.

### 2. Anatomy
3 elements: Track, Handle (formerly "thumb"), Icon (optional).
- Track shows the full extent; handle slides along it.
- Handle can contain an optional icon that should always communicate the switch's selection. Icons visually emphasize the selection; the icon's meaning must be clear and unambiguous so people understand whether the switch is on or off.
- Label text sits inline outside the switch, describing what the switch controls when selected. Never put label text inside the switch.

### 3. Sizes / variants / configurations
Configurations: Without icons; Icon on selected switch; Icon on selected and unselected switch.

| Element | Attribute | Value |
|---|---|---|
| Track | Height | 32dp |
| Track | Width | 52dp |
| Track | Outline width | 2dp |
| Track | Shape | md.sys.shape.corner.full |
| Handle | Height (unselected) | 16dp |
| Handle | Height — with icon | 24dp |
| Handle | Height (selected) | 24dp |
| Handle | Height (pressed) | 28dp |
| Handle | Width (unselected) | 16dp |
| Handle | Width — with icon | 24dp |
| Handle | Width (selected) | 24dp |
| Handle | Width (pressed) | 28dp |
| Handle | Shape | md.sys.shape.corner.full |
| State layer | Size | 40dp |
| State layer | Shape | md.sys.shape.corner.full |
| Target | Size | 48dp |
| Icon | Size (selected) | 16dp |
| Icon | Size (unselected) | 16dp |

### 4. Placement
- Often arranged in stacked layouts; settings screens are common places to use switches.
- Commonly used on mobile to turn settings on or off.

### 5. States and interaction behavior
States: Enabled, Hovered, Focused, Pressed, Disabled.
- Successfully toggled when the handle slides to the other side of the track after an interaction.
- On toggle, the handle size changes and the action takes effect immediately, without needing to save.
- The **on** state is indicated by a larger handle size (16dp → 24dp; 28dp pressed).
- Touch: when tapped or dragged, the handle size grows, providing interaction feedback.
- Cursor: when hovered (in both on and off states) the hover area grows, cueing that the handle is interactive; when clicked, the handle size grows.

### 6. Color role mapping
Switch color roles (light and dark themes), 6 roles: **surface container highest**, **outline**, **outline**, **primary**, **on primary**, **on primary container**.
- Adjacent text label: **on surface**; supporting text may use **on surface variant**. Label color is unchanged even when interacting with the label or component.

### 9. Do / Don't
- Do make the switch's selection (on or off) visible at a glance.
- Do start switch effects immediately, without needing to save.
- Do pair switches with an inline label; keep labels short and direct, describing what the control does when the switch is on.
- Do use icons that clearly communicate on/off, such as an X and a checkmark.
- Don't use ambiguous or non-binary handle icons, such as a moon or edit icon.
- Don't put label text inside the switch — the font size would be too small to be accessible; use an appropriate icon instead.
- Don't use a switch to toggle between opposing options — use a connected button group.
- Don't use a switch for a call to action or to replace a button.
- Don't use switches to select multiple options that require saving — use checkboxes.
- Don't apply density by default.

### 10. Accessibility
- Target size 48dp; minimum 48x48 CSS pixels per target.
- Visual presentation is more accessible than M2; color mappings meet Material's non-text-contrast requirements.
- Assistive tech must be able to: navigate to a switch with a keyboard or switch input; toggle it on and off; get appropriate feedback based on input type.
- Initial focus lands directly on the switch's handle, the primary interactive element.

| Keys | Actions |
|---|---|
| **Tab** | Focus lands on the switch handle |
| **Space** or **Enter** | Toggles the handle on and off |

- Labeling: the accessibility label uses the adjacent label text if implemented correctly; screen reader reads UI text followed by the role. When visible UI text is ambiguous, make the accessibility label more descriptive (visible **Photo album** → label **Photo album access**). Prefer making the adjacent label text more descriptive to reduce the need for different accessibility text.

### Differences from M2
- Accessibility: visual presentation is more accessible.
- Color: new color mappings meet Material's non-text-contrast requirements, plus dynamic color compatibility.
- Icons: ability to have an optional icon within the switch handle.
- Layout: track is taller and wider. (M2 handle was circular and extended beyond the track edge.)

---

## Sliders

### 1. What it is + when to use it vs. siblings
Select values along a track. Ideal for adjusting settings such as volume and brightness, or changing the intensity of image filters. Sliders can use icons or labels to represent a numeric or relative scale. Sliders should present the full range of available values, and the value should take effect immediately.

Variant discriminators:
- **Standard** — selects one value from a range. Use when the slider should start from zero or the beginning of a sequence.
- **Centered** — selects a value from a positive and negative value range. Use when zero, or the default value, is in the middle of the range.
- **Range** — selects two values on one slider to create a range. Use when defining a minimum and maximum value.

### 2. Anatomy
6 elements: Value indicator (optional), Stop indicators (optional), Active track, Handle, Inactive track, Inset icon (optional).
- **Track** shows the full range of selectable values; two sections: **active** (minimum value → handle; between the two handles on a range slider) and **inactive** (handle → maximum value; outside the two handles). LTR: values increase left→right; RTL reversed.
- **Handle** is moved along the track to choose a value; two handles choose min and max in a range. The handle changes shape when pressed (a vertical line that shrinks in width when selected).
- **Value indicator** displays the value corresponding to the handle's placement; appears when interacting with the corresponding handle. On range sliders only one value shows at a time. Not required if the value is shown elsewhere.
- **Stop indicators** show which predetermined values can be chosen; the handle snaps to the closest stop.
- **Inset icon** sits within the track and illustrates what the slider controls.

### 3. Sizes / variants / configurations

Variant availability:
| Variant | M3 | M3 Expressive |
|---|---|---|
| Standard | Available as "continuous" slider | Available |
| Centered | Available (web only) | Available |
| Range | Available | Available |
| Discrete | Available | Available as "stops" configuration |

Configuration availability:
| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Inset icon | No (default) | Available | Available |
| Inset icon | Yes | -- | Available |
| Orientation | Horizontal (default) | Available | Available |
| Orientation | Vertical | -- | Available |
| Size | XS (default) | Available | Available |
| Size | S, M, L, XL | -- | Available on Android Views (MDC-Android). Available as tokens on other platforms.* |
| Stop indicators | No (default), Yes | Available as "discrete" slider | Available |
| Value Indicator | No (default), Yes | Available | Available |

*Configurations only available using tokens don't have implemented presets in code. To change the size, swap the default size tokens `md.comp.slider.xsmall.[...]` with those of the desired size.

Measurements:
| Attribute | XS | S | M | L | XL |
|---|---|---|---|---|---|
| Track height | 16dp | 24dp | 40dp | 56dp | 96dp |
| Handle height | 44dp | 44dp | 52dp | 68dp | 108dp |
| Track shape | 8dp | 8dp | 12dp | 16dp | 28dp |
| Inset icon size | -- | -- | 24dp | 24dp | 32dp |

Common (all sizes): Label container height 44dp; Label container width 48dp; Handle width 4dp.

Slider tokens are organized into a common token set plus token sets for each size.

Size rules:
- Use larger sizes to increase the targets and provide larger visual emphasis.
- The active and inactive tracks should always be the same size.
- XL sliders should be reserved for hero moments, where the slider itself is the most important element on the page.

### 4. Placement
- Orientation: horizontal or vertical, depending on the use case (vertical slider shows zero at the bottom).
- Avoid using range sliders vertically — too much cognitive load; people are used to most sliders being horizontal.
- Icons or text can be added outside the slider (e.g. plus/minus to the left and right) to indicate the range of values; this can replace a stop indicator.
- A separate text input field can be added outside the slider instead of the built-in value label; the slider and the text field must auto-update to match each other, and people must be able to tab to the text field directly after the slider.
- Inset icon placement: standard sliders that are M, L, or XL can include an icon within the track. When there's not enough space for the icon on the active track (e.g. at a low value), the icon moves to the inactive track. Consider swapping which icon is displayed at zero (volume → mute).

### 5. States and interaction behavior
States: Enabled, Disabled, Hovered, Focused, Pressed.
- **Select & drag**: standard slider handle drags smoothly; with stop indicators the handle snaps to the closest stop while dragged.
- **Select jump**: selecting part of the track moves the handle to the selected location, or to the closest stop indicator.
- **Select & arrow**: **Tab** focus lands on handle; **Arrows** increase/decrease by one value or stop indicator; **Space & arrows** increase/decrease by a larger interval or stop indicator.
- Handle shape-morph: the handle shrinks in width and the value appears when pressed. Touch — tapped or dragged: handle width shrinks, value appears. Cursor — hovered: the cursor changes; clicked and dragged: handle width shrinks, value appears.

### 6. Color role mapping
Slider color roles (light and dark schemes), 9 roles: **inverse surface**, **inverse on surface**, **primary**, **on primary**, **primary**, **secondary container**, **on secondary container**, **on secondary container**, **on primary**.

### 8. M3 Expressive update (May 2025)
The slider includes expressive configurations for orientation, shape sizes, and an inset icon. Updated on Android Views (MDC-Android) and Jetpack Compose.

Variants and naming:
- Changed **continuous** slider to **standard** slider
- The **discrete** slider is now the **stops** configuration

New configurations:
- Orientation: Horizontal, vertical
- Optional inset icon (standard slider only)
- Sizes: XS (existing default), S, M, L, XL

Previous update — **Visual refresh to improve non-text contrast, Dec 2023** (Android Views (MDC-Android) and Jetpack Compose):
- **Configuration:** Added centered configuration and range selection
- **Shape:** New shape for slider tracks and handles; slider elements change shape when selected
- **Motion:** Slider handle adjusts width upon selection; slider tracks adjust in shape when sliding to the edge
- **Color:** Refreshed color mappings
- Visual refresh sliders have a stop indicator, larger label text, and a vertical handle that narrows when pressed; centered sliders start from the middle instead of the leading edge.

Differences from M2: Color — new color mappings and compatibility with dynamic color. (M2 sliders had a circular handle and a small label when pressed.)

### 9. Do / Don't
- Do present the full range of available values.
- Do make changes take effect immediately so people understand the effects as they move the slider.
- Do keep active and inactive tracks the same size.
- Do reserve XL for hero moments.
- Don't have too many stop indicators — it becomes visually crowded and difficult to adjust the value.
- Don't add inset icons to XS or S sliders; don't use an inset icon with sliders that have track thicknesses under 40dp.
- Don't use inset icons on centered or range sliders — it makes it unclear where the start of the slider is.
- Don't use range sliders in vertical orientation.
- Show only one value indicator at a time on range sliders.

### 10. Accessibility
- Assistive tech must be able to: navigate to a slider; select a range by controlling a handle along a track; get appropriate feedback based on input type.
- Initial focus lands directly on the handle, the primary interactive element; value then adjusted with arrow keys or other keyboard navigation.
- Color contrast: use visual anchors so the end of the slider's inactive track has at least **3:1** contrast with the background. All sliders have stops at the end of the inactive track to ensure at least 3:1 contrast with the background; if the inactive track already has this contrast, the end stops can be removed. Alternatively use icons or other elements with 3:1 contrast to indicate the ends.

| Keys | Actions |
|---|---|
| Tab | Moves focus to the slider handle |
| Arrows | Increase and decrease the value by one value or one stop indicator |
| Space & Arrows | Increase and decrease the value by one interval or one stop indicator |
| Home or End | Set the slider to the first and last values on the slider |

- Labeling: accessibility label is typically the same as the slider's adjacent text label; role **slider**. Icon buttons placed outside the slider should have the **button** role.

---

## Chips

### 1. What it is + when to use it vs. siblings
Chips help people enter information, make selections, filter content, or trigger actions; best used to help people accomplish their current task faster and easier. Use chips to show options for a specific context. Four variants: assist, filter, input, suggestion.

Chips vs. buttons: chips and buttons are similar — both provide visual cues prompting people to take actions and make selections. But buttons appear consistently with familiar calls to action; chips are dynamic to the situation and appear as a group of interactive elements. Use chips to enhance a person's current journey and encourage action; use buttons to progress them through the product and for significant actions. Chips should dynamically offer various actions depending on the current task, whereas a button should be a persistent fixture of a layout. Chips represent forking paths for a current task; buttons represent linear steps. Multiple chips should appear together in a set, whereas there should be no more than 3 buttons in a single arrangement.

Variant selection — does the chip represent an action (assist) or filter results (filter)? Is its content generated by the product (suggestion) or by the person (input)?

| Purpose | Chip variant | Rationale | Example |
|---|---|---|---|
| Action | Assist chip | Represent smart or automated actions that can span multiple apps | **Add to calendar** action |
| Filter | Filter chip | Represent filters for a collection | Platform selector on material.io/components |
| Information, user-authored | Input chip | Represent discrete pieces of information entered by a person | Gmail contact in the **To** field |
| Information, product-authored | Suggestion chip | Help narrow a person's intent by presenting dynamically-generated suggestions | Suggested chat response |

### 2. Anatomy
Overall: Container; Label text; Leading icon or image (optional); Trailing icon (required for input chips, optional for filter chips).
- Assist chip: Container, Label text, Leading icon (3 elements).
- Filter chip: Container, Label text, Leading icon, Trailing icon (4 elements).
- Input chip: Container, Label text, Trailing icon, Leading icon (4 elements).
- Suggestion chip: Container, Label text (2 elements).

**Container** — all chips are slightly rounded with an 8dp corner. Chip elevation defaults to 0 but can be elevated if they need more visual separation; elevate when placed on top of an image or dynamic background. Use an outline to define the edge of the container on regular backgrounds.

**Label text** — 20 characters or fewer; same typography style as buttons. Keep brief; skip conventional grammar rules such as articles ("take a walk" → "take walk") to save space.

**Leading icon or image (optional)** — can be an icon, logo, or circular image. Use a system icon to help identify a chip's category. Leading circular images are sized larger than leading icons (24dp avatar vs. 18dp icon) to provide more space for detail; icons are designed to be legible at small sizes.

**Trailing icon (input and filter chips only)** — required on input chips and must remove the chip; optional on filter chips and can open a menu or remove the chip. The trailing icon is always aligned to the end side of the container: right for LTR, left for RTL.

### 3. Sizes / variants / configurations

Assist chip:
| Attribute | Value |
|---|---|
| Height | 32dp |
| Shape | 8dp corner radius |
| Icon size | 18dp |
| Vertical label text alignment | Center-aligned |
| Horizontal label text alignment | Start-aligned |
| Left/right padding | 16dp |
| Left/right padding with icon | 8dp |
| Padding between elements | 8dp |

Filter chip:
| Attribute | Value |
|---|---|
| Container height | 32dp |
| Container shape | 8dp corner radius |
| Icon size | 18dp |
| Vertical label text alignment | Center-aligned |
| Horizontal label text alignment | Start-aligned |
| Left/right padding | 16dp |
| Left/right padding with icon | 8dp |
| Padding between elements | 8dp |

Input chip:
| Attribute | Value |
|---|---|
| Container height | 32dp |
| Container shape | 8dp corner radius |
| Icon size | 18dp |
| Avatar shape | 12dp corner radius |
| Avatar size | 24dp |
| Vertical label text alignment | Center-aligned |
| Horizontal label text alignment | Start-aligned |
| Left padding for avatar | 4dp |
| Right padding for avatar | 8dp |
| Left/right padding for icon | 8dp |
| Padding between elements | 8dp |
| Target size for close icon | Min 48dp |

Suggestion chip:
| Attribute | Value |
|---|---|
| Container height | 32dp |
| Container shape | 8dp corner radius |
| Icon size | 18dp |
| Vertical label text alignment | Center-aligned |
| Horizontal label text alignment | Start-aligned |
| Left/right padding without icon | 16dp |
| Left/right padding with icon | 8dp |
| Padding between elements | 8dp |

Secondary-action sizing rule: secondary actions (e.g. a trailing icon button for **Remove**) must have a 48x48dp interaction target that doesn't interfere with the chip's primary action (e.g. **Edit** or **Drag**). Achieve this by applying a minimum width of **88dp** to the chip, or **42dp** to the label text.

### 4. Placement
- Place multiple chips inline as a row of options, not listed vertically. Overflowing chips break to the next line. If the field is only one row high, chip sets can scroll horizontally instead.
- Keep an **8dp minimum space between chips**. Chips must have a minimum **48dp** target size regardless of placement or density; the target can extend beyond the visible container if required.
- Chip labels truncate in a wrapped layout and when wider than the full width of the window.
- Assist chips are displayed **after primary content** — below a card or persistently at the bottom of a screen.
- Filter chips: can be shown underneath a search field; can be organized in a side sheet when there are many; can wrap to a new row — if there are more than two rows, consider horizontal scrolling; can scroll horizontally to show many options.
- Input chips can appear inline with the cursor in a text field, in a stacked list, or in a horizontally scrollable list; can wrap to a new row if all chips need to be visible.
- Overflowed chips in a text field follow the same behavior as regular text: an unfocused field with overflowed content displays the beginning of the input; tapping the field snaps to the end of the input with cursor and keyboard active.
- Breakpoints: in **medium and expanded** breakpoints, filter chips may contain a trailing icon to directly remove the chip or open a menu. In **compact** windows, the trailing icon's target area is too small to be accessible on its own — but if the whole chip can be selected to accomplish the action, the chip is likely still accessible; make sure the whole chip opens the menu in compact windows.

### 5. States and interaction behavior
States for every variant, selected and unselected: Enabled, Disabled, Hovered, Focused, Pressed, Dragged.

Per-variant definitions (from the Guidelines sections):
- **Assist chips** represent smart or automated actions that can span multiple apps, such as opening a calendar event from the home screen. They function as though the person asked an assistant to complete the action, and should appear dynamically and contextually in a UI. The alternative to an assist chip is a button, which should appear persistently and consistently. An assist chip can also surface supplemental information (like a calendar event) alongside contextual actions.
- **Filter chips** use tags or descriptive words to filter content.
- **Input chips** represent discrete pieces of information entered by a person, such as Gmail contacts or filter options within a search field.
- **Suggestion chips** help narrow a person's intent by presenting dynamically generated suggestions, such as possible responses or search filters.

- Assist chips: can trigger an action or show progress and confirmation. During an interaction they can transform into modals, transition into full-screen views of new content, or readjust to display more results inline. Adjust text dynamically if state changes, e.g. **Save** → **Saved**.
- Filter chips: tapping activates the chip and appends a leading checkmark icon to the starting edge of the chip label. Multiple chips can be selected or unselected. Alternatively a single chip can be selected (alternative to segmented buttons, radio buttons, or single-select menus) — selecting one automatically deselects all others. Filter chip suggestions can dynamically change as a person starts to select filters. When combined with a menu, the filter chip opens a list of selectable options.
- Input chips: enable user input and verify it by converting text into chips. Support editing to change contents (e.g. correcting an email address) — in edit mode the chip reverts to a text string; editing is triggered by interacting with the chip, either by selecting it or by a second interaction after selection. A single field can contain multiple input chips; chips can be reordered or moved into other fields. Input chips can expand to show more information or options using a **container transform** transition pattern. Backspace with the cursor before a chip selects the entire chip; pressing backspace again deletes it.
- Chip sets can be scrolled horizontally.

### 6. Color role mapping
- Assist chip: **surface container low** (optional), **on surface**, **outline**, **primary**.
- Filter chip: **on surface variant**, **on secondary container**, **secondary container**, **outline variant**, **surface container low** (optional).
- Input chip: **on surface variant**, **surface container low** (optional), **on surface variant**, **on surface variant**, **outline variant**, **primary**, **secondary container**, **on secondary container**, **on secondary container**.
- Suggestion chip: **outline**, **surface container low** (optional), **on surface variant**.
- Leading icon color for unselected chips is customizable through theming: default role is **primary**; **on surface variant** is a good alternative when the icon style requires less emphasis.
- Aug 2024 update: stroke color changed from **outline** to **outline variant** — the stroke was softened to improve visual hierarchy between chips and buttons.
- Interactivity affordance: use the **outline** color role instead of **outline variant** to ensure a minimum 3:1 contrast.

### 7. Typography role mapping
Chip label text has the same typography style as buttons.

### 9. Do / Don't
- Do use chips to present contextual, supplemental options.
- Do write assist chips like buttons — start with a verb (**Get**, **Add**).
- Do write filter chips with nouns that describe the category to **include** in results; avoid negative phrases like **Exclude images**.
- Do write suggestion chips as nouns or short phrases; avoid exceeding 20 characters when possible.
- Do keep chip labels 20 characters or fewer.
- Do show chips in a set.
- Don't display a single chip by itself.
- Don't present only a single filter chip option.
- Don't replace major actions with chips — actions that progress people to the next or previous step must be buttons.
- Don't use chips to finish or progress a task.
- Don't mix chip set behaviors — all chip sets on a page should be either single-select or multi-select.
- Don't elevate chips placed directly on the page.
- Don't use elevation to indicate a chip's pressed state — use the visual ripple effect.
- Don't apply density by default.

### 10. Accessibility
- Assistive tech must let people: use a chip to perform an action; navigate to a chip; activate a chip.
- Chip label needs at least **3:1 contrast** with the background.
- A chip that performs an action must present the same semantics as a button to the platform's accessibility API.
- Minimum 48dp target size; close icon target min 48dp; 48x48dp for secondary actions (88dp min chip width or 42dp min label width).
- Horizontal overflow: when there are too many chips for one row, provide a way to display them all at once and avoid scrolling. **Reflow method** — use a filter chip as a leading element to reflow the horizontal list, shifting down content below (e.g. a **Show all** chip). **Menu method** — create a leading button to display all chip options in a menu; use this to avoid shifting the position of content below. Don't use the menu method on chips with a second action, like a remove icon.
- Focusability: each chip is a focusable element. If a chip only has a remove icon, the entire chip and icon are one focusable element. If a chip has a second action, like select, the chip content and remove icon are two separate focusable elements.
- Input chip remove action: display the remove icon whenever a chip can be removed. On mobile, if remove is the only chip action the remove icon isn't necessary — the chip can be removed by selecting it and pressing **Delete**.
- Showing chip interactivity (Material requires a secondary indicator so users with low vision and cognitive disabilities can see chips are interactive) — use one of: a label before the chip group suggesting interaction, such as **Select type**; interactive page context, such as **Filter results**; the **outline** color role instead of **outline variant** for minimum 3:1 contrast; an interactive chip label such as **Turn on lights**, or a leading icon.
- Multi-select: **Space** or **Enter** selects the focused chip and allows selecting all chips; it also deselects a focused selected chip. Multiple chips can be selected but only one can be in focus.
- Drop-down list: accessibility label should align with each list item's text label. For list items with text and an icon, mark the icon as decorative to avoid redundant verbalizations.

| Keys | Actions |
|---|---|
| **Tab** | Moves focus to enabled chip or chip group |
| **Space** or **Enter** | Activates, selects, or deselects the focused chip |
| **Backspace** or **Delete** | Removes currently focused input chip |
| **Arrows** | Moves focus between chips |

Labeling elements:
| Element | A11y label | Role (Web) | Role (Android Views / MDC-Android) | Role (Jetpack Compose) |
|---|---|---|---|---|
| Image / Icon within chip | Hide image | - | - | - |
| Basic chip (one action) | "{chip content}" | gridcell | button | button |
| Selectable chip | "{chip content}" | gridcell | radio button | checkbox |
| Remove icon (no other action) | "Remove {chip content}" | - | - | - |
| Two actions (e.g. select + remove) | "{chip content}." Then "Remove {chip content}". | button or checkbox | button or checkbox | button or checkbox |

The accessibility label for a chip is the chip's label text; additional actions, like remove, are labeled separately.

### Differences from M2
- Color: new color mappings and compatibility with dynamic color.
- Shape: rounded rectangle.
- Variants: action chips have been separated into assist chips and suggestion chips; choice chips are now a subset of filter chips. (M2: input, choice, filter, action.)

---

## Text fields

### 1. What it is + when to use it vs. siblings
Use a text field when someone needs to enter text into a UI, such as filling in contact or payment information. Text fields commonly appear in forms and dialogs. Two variants: **filled** and **outlined**.

Discriminator: both variants use a container to provide a visual cue for interaction and provide the same functionality — the variant used can depend on style alone. Choose the variant that works best with the app's visual style, best accommodates the UI's goals, and is most distinct from other components (like buttons) and surrounding content. Outlined text fields have less visual emphasis than filled text fields; in places like forms where many fields sit together, that reduced emphasis helps simplify the layout.

### 2. Anatomy
Filled text field — 10 parts: Container; Leading icon (optional); Label text in empty field; Label text in populated field; Trailing icon (optional); Focused active indicator; Caret; Input text; Supporting text (optional); Enabled active indicator.

Outlined text field — 9 parts: Enabled container outline; Leading icon (optional); Label text in empty field; Label text in populated field; Trailing icon (optional); Focused container outline; Caret; Input text; Supporting text (optional).

- **Containers** improve discoverability by creating contrast between the text field and surrounding content. A container has a fill and a stroke either around the entire container or just the bottom edge; the color and thickness of a stroke can change to indicate when the text field is active.
- **Rounded corners**: the outlined text field container has rounded corners; the filled text field container has rounded top corners and square bottom corners.
- **Label text** tells people what information is requested. Every text field should have a label. Label text should be aligned with the input text and always visible; it can be placed in the middle of a text field or rest near the top of the container.
- **Adjacent label**: a text field doesn't require a label if its purpose is indicated by a separate, adjacent label. Adjacent labels should be aligned to the leading edge of the text field container.
- **Required text indicator**: display an asterisk (*) next to the label text, and explain that asterisks indicate required fields via supporting text or a single note at the beginning of the form. Indicate all required fields. If required text has a particular color, use the same color for the asterisk.
- **Input text** is text a person has entered.
- **Prefix text**: e.g. a currency symbol. **Suffix text**: e.g. unit of measurement or email domain.
- **Supporting text** conveys additional information about the input field, such as how it will be used; ideally one line, may wrap to multiple lines if required; either persistently visible or visible only on focus.
- **Character counter**: if there is a character or word limit, include a character or word counter displaying the ratio of characters used to the total limit.
- **Error text** replaces supporting text for fields that validate content, such as passwords. Swapping supporting text with error text prevents new lines of text from bumping content and changing the layout. Long errors can wrap to multiple lines if there isn't enough space to clearly describe the error.
- **Error icon**: strongly recommended in the error state.

### 3. Sizes / variants / configurations

Filled text field measurements:
| Attribute | Value |
|---|---|
| Default container height | 56dp |
| Label alignment (unpopulated) | Vertically centered |
| Top/bottom padding | 8dp |
| Left/right padding without icons | 16dp |
| Left/right padding with icons | 12dp |
| Icon alignment | Vertically centered |
| Padding between icons and text | 16dp |
| Supporting text and character counter top padding | 4dp |
| Padding between supporting text and character counter | 16dp |
| Target size | 56dp |

Outlined text field measurements:
| Attribute | Value |
|---|---|
| Container height | 56dp |
| Left/right padding without icons | 16dp |
| Left/right padding with icons | 12dp |
| Padding between icons and text | 16dp |
| Icon alignment | Vertically centered |
| Supporting text and character counter top padding | 4dp |
| Padding between supporting text and character counter | 16dp |
| Label alignment | Vertically centered |
| Left/right padding populated label text | 4dp |
| Target size | 56dp |

Configurations (both variants, empty and populated): Supporting text; Trailing icon; Leading icon; Leading and trailing icons; Prefix; Suffix; Multi-line text field.

Input-text display modes:
- **Single line** — displays only one line of text. As the cursor reaches the right field edge, text longer than the input line automatically scrolls left. Not suitable for collecting long responses.
- **Multi-line** — grows to accommodate multiple lines; overflow text expands the field, shifting screen elements downward, and text wraps onto a new line. Initially appears as a single-line field, useful for compact layouts that must accommodate large amounts of text.
- **Text areas** — fixed-height fields, taller than text fields; wrap overflow text onto a new line and scroll vertically when the cursor reaches the bottom. The large initial size indicates that longer responses are possible and encouraged. Use these instead of multi-line fields on the web. Ensure the height of a text area fits within mobile screen sizes.

Images 24dp in height can be placed inside text fields — this height allows for optimal top and bottom padding within the field and is consistent with icon size recommendations.

Icons in text fields are optional. They can describe valid input methods (such as a microphone icon), provide affordances to access additional functionality (such as clearing the content of a field), or express an error.

Icon types (optional): Icon signifier (can describe the type of input required and be a touch target for nested components, e.g. a calendar icon tapped to reveal a date picker); Valid or error icon (indicates valid and invalid inputs, making error states clear for colorblind users); Clear icon (clears an entire input field; appears only when input text is present); Voice input icon (microphone signifies voice input); Dropdown icon (arrow indicates a nested selection component); Image (helps contextualize the required input, e.g. a credit card number).

Read-only fields display pre-filled text people cannot edit; styled the same as a regular text field and clearly labeled as read-only. Available filled and outlined.

### 4. Placement / adaptive design
- If both variants are used in a UI, use them consistently within different sections and don't intermix them within the same region (e.g. outlined in one section, filled in another; filled in the form, outlined in a dialog on top).
- As layouts adapt to larger screens and different window size classes, apply flexible container dimensions. Set minimum and maximum values for margins, padding, and container dimensions as layouts scale so typography adjusts for better reading experiences.
- **Compact** window sizes: text fields can span the full width of the display. **Medium and expanded** window sizes: text fields should be bound by flexible margins or other containers.
- Avoid maintaining fixed margins and typography properties as text fields expand in fluid layouts — this leads to extra long text fields. Text fields should not span the full width of a large screen.
- Ensure padding between text fields is sufficient to prevent multi-lined errors from bumping layout content.
- Leading and trailing icons change position based on LTR or RTL contexts.
- Dense text fields enable people to scan and take action on large amounts of information (e.g. an event creation form on tablet).

### 5. States and interaction behavior
States (both variants): Enabled (empty), Focused (empty), Hovered (empty), Disabled (empty), Enabled (populated), Focused (populated), Hovered (populated), Disabled (populated).
Error states (both variants): Enabled (empty), Focused (empty), Hovered (empty), Enabled (populated), Focused (populated), Hovered (populated).
- Error messages are displayed below the text field as supporting text until fixed.
- Label motion: when the field is selected, the label text moves from the middle of the text field to the top.
- Changes to color and thickness of stroke provide clear visual cues for interaction; the active text field has a thicker border.

### 6. Color role mapping
- Filled text field, 10 roles in listed order: **surface container highest**, **on surface variant**, **on surface variant**, **primary**, **on surface variant**, **primary**, **primary**, **on surface**, **on surface variant**, **on surface**.
- Outlined text field, 9 roles in listed order: **outline**, **on surface variant**, **on surface variant**, **primary**, **on surface variant**, **primary**, **primary**, **on surface**, **on surface variant**.

### 9. Do / Don't
- Do make text fields look interactive.
- Do make the field's state (blank, with input, error, etc.) visible at a glance.
- Do keep labels and error messages brief and easy to act on.
- Do give every text field a label; keep label text short, clear, and fully visible.
- Do align adjacent labels to the leading edge of the container.
- Do replace supporting text with error text. If only one error is possible, error text should describe how to avoid the error; if multiple errors are possible, describe how to avoid the most likely error.
- Do show an error icon in the error state (strongly recommended) — it highlights the error for people with visual impairments and provides an additional sensory indicator.
- Do use text areas instead of multi-line fields on the web.
- Don't truncate label text; don't let label text take up multiple lines.
- Don't add error text in addition to supporting text — their appearance will shift content.
- Don't intermix filled and outlined variants within the same region or form.
- Don't use fixed text field margins on large devices; don't let text fields span the full width of a large screen.
- Don't apply density by default.
- Don't use single-line fields to collect long responses.

### 10. Accessibility
- Target size 56dp (spec table). Density best practice: minimum 48x48 CSS pixels per target.
- Outlined text fields can improve perception of the field with a **3:1 or greater** contrast ratio between the container outline and the background; make sure the container outline has a minimum contrast of 3:1 to the background.
- Users must be able to: navigate to and activate a text field with assistive technology; input information; receive and understand supporting text and error messages; navigate to and select interactive icons.

| Keys | Actions |
|---|---|
| Tab | Focus lands on (non-disabled) text field |

Labeling elements:
- The accessibility label for a text field is the same as the text field label; role **textbox**. Screen reader reads UI text followed by the role.
- For interactive trailing icons, the label clarifies function — password hidden → "Show password"; password visible → "Hide password"; role **Button**.
- When an icon has no actionable role, like an error icon, the label is "Error."
- Prefix and suffix accessibility labels need a unique id attribute, e.g. the currency name for a currency symbol prefix ("Euro"; "At gmail dot com" for an email domain suffix).
- On error, "alert" is applied to the role and the error message to the text label. If a field displays both supporting text and error text, the label should include the supporting text first, followed by the error text.
- Character counter accessibility label clarifies how many characters can be entered and is called "character count" within the label (e.g. "Character count, 5/20").
- Supporting text's displayed text is also used for its accessibility label.
- Required fields: indicate with an asterisk at the end of the text field label; the accessibility label must include the asterisk (e.g. "Username*").

### Differences from M2
- Color: new color mappings and compatibility with dynamic color.

---

## Search

### 1. What it is + when to use it vs. siblings
Use search for navigating a product with queries. Search helps people find information quickly; use it for products with many items to manage, such as files or messages. A search bar can include a leading search icon, hinted search text, and optional trailing icons; it can display suggested keywords or phrases as a person types, and displays search suggestions or results in a list.

Entry-point discriminators (entry point depends on a product's needs and should be easy to find):
- **Search bar** — search contents in a specific view, like **Search your messages**.
- **Search app bar** — use this app bar variant when search is the primary, global function; provides an emphasized, global entry point.
- **Search icon button** — use when search is a secondary action or not the main focus.

### 2. Anatomy
6 elements: Search bar container; Leading icon; Supporting text; Trailing icon and avatar (optional); Input text; Container for search suggestions or results.
- Search includes a search bar and a container for suggestions and results. The container is empty by default — use the **list** component to add content. In the divided (baseline) style, a divider separates the search bar and results.
- **Search bar container**: in the contained style it remains the same shape in both unfocused and focused states; avoid changing the container behavior. Containers have persistent, rounded corners.
- **Leading icons**: the leading side should include either a navigational icon button (menu or arrow) or a non-functional search icon.
- **Trailing icons**: one or two trailing icons or icon buttons. Trailing actions can include additional modes of searching like voice search; a separate high-level action such as current location or profile; an overflow menu; a decorative search icon. Focused search can show an optional **clear** icon to remove input text.
- **Hinted search text**: a short description of the information people can search, like **Search replies** or **Search your messages**. When a person starts typing, hinted text is replaced with the input text.
- Trailing-element examples: with avatar; with one trailing icon button; with two trailing icon buttons; with trailing icon button and avatar.

### 3. Sizes / variants / configurations

| Variant | M3 | M3 Expressive |
|---|---|---|
| Search | Available | Available |

Styles:
- **Contained** — has an expressive look and feel; uses a filled container to separate the search bar from a list of suggestions or results; persistent filled container, expressive motion, rounded shape. Recommended.
- **Divided (baseline)** — uses a divider to separate the search bar from suggestions and results; doesn't have the latest visual style, motion, or flexibility.

| Category | Configuration | M3 | M3 Expressive |
|---|---|---|---|
| Style | Contained | -- | Available |
| Style | Divided | Available | Not recommended. Use contained. |
| Layout | Docked, full-screen | Available | Available |

Search bar measurements:
| Element | Attribute | Value |
|---|---|---|
| Container | Width | Min: 360dp, max: 720dp |
| Container | Height | 56dp |
| Container | Label alignment | Start-aligned |
| Container | Leading padding | Unfocused: 24dp, focused: 12dp |
| Container | Trailing padding | Unfocused: 24dp, focused: 12dp |
| Container | Leading icon and label padding (from tap target) | 4dp |
| Container | Label and trailing icon padding (from tap target) | 4dp |
| Avatar | Size | 30dp |

Focused search — contained style:
| Element | Attribute | Value |
|---|---|---|
| Full-screen container | Width | Full width |
| Full-screen container | Height | Full height |
| Docked container | Width | Min: 360dp, max: 720dp |
| Docked container | Height | Min: 240dp, max: 2/3 of screen height |
| Search bar container | Height | 56dp |
| Search bar container | Label alignment | Start-aligned |
| Search bar container | Leading padding | 16dp |
| Search bar container | Trailing padding | 16dp |
| Search bar container | Leading icon and label padding (from tap target) | 4dp |

Token sets: the **search bar** set only contains tokens for the unfocused search bar. The **search view** set contains all other tokens when interacting with search, including all styles and layouts.

### 4. Placement / adaptive design
- A search bar is typically placed at the top of a screen to remain prominent and accessible. Its location depends on whether search is the primary focus or a secondary action. Add a search bar below a title to search specific content; use a persistent search app bar integrated into an app bar for global search.
- Container margins: unfocused **24dp**, focused **12dp** (the search bar grows wider when focused).
- The search bar position and alignment should scale with the layout and stay close to the searchable content. In most cases a search bar should stay in its pane and scale in width accordingly, with internal elements anchored to the left and right as the parent container scales.
- Focused search layouts: **Docked** opens a list below the search bar, with a scrim covering main content. **Full-screen** expands to fill the screen.
- Window size classes: **Docked layout** is best for medium and expanded windows; **Full-screen layout** is the default for compact window sizes. Search suggestions or results should swap from full-screen in compact windows to docked in larger window sizes.
- If search is the primary action, focused search can be a standalone destination reached from a navigation bar.
- Search results appear in a list below the bar and scroll beneath the bar.
- Scroll behavior: a search bar can scroll away with content, then reappear when a person begins scrolling up; or remain fixed at the top of the screen.
- Use **gaps** to separate a list of suggestions or results into groups.

### 5. States and interaction behavior
Search bar states: Enabled, Hovered, Focused, Pressed (ripple).
Search suggestions & results states: Enabled, Hovered, Focused, Pressed (ripple).
- In focused search, individual elements maintain their own interaction states.
- Focused search: when a search entry point is selected, it opens focused search. Search suggestions can appear before text is entered; search results can show as someone is typing or after a search is executed. Focused search can: show historical suggestions before typing; show suggestions or results as someone is typing; wait to show suggestions or results until a search is queried.
- The **back** icon releases focus, dismisses any suggestions or results, and returns the search bar to its original state.
- Motion: the search bar grows wider when focused (margins 24dp → 12dp).
- Executing a search: type a query and press **Enter**, or select a suggestion or result without querying a search. When results are queried, the input text should remain visible but not in focus.
- Predictive back (Android): swiping left or right on search detaches search from the screen edge to signal the full-screen layout will minimize, and reveals the previous screen in a preview; the search surface and content scale back in the direction of the gesture.

### 6. Color role mapping
- Full-screen layout, 6 roles: **surface container low**, **on surface variant**, **on surface variant**, **surface container high**, **on surface variant**, **on surface**.
- Docked layout, 6 roles: **surface container high**, **on surface variant**, **on surface variant**, **surface container high**, **on surface variant**, **on surface**.
- Search bar container uses the **surface container high** color role. This applies when the screen background is white or a tonal **surface** color, ensuring clear contrast. Avoid using **surface container high** on a **surface container** background — the search bar blends in and becomes difficult to find. To ensure proper contrast, use surface container roles that are more than one step apart.

### 8. M3 Expressive update (February 2025)
Search has a new visual style, motion, and more flexibility for trailing icons.

Naming
- Search bar and search view are now collectively named **search**

Configurations
- Styles: Search can be contained (recommended) or divided
- Gaps can separate results into groups

Motion
- The search bar grows wider when focused

Supported platforms:
- Jetpack Compose

The **contained** search style features a persistent, filled search container.
In M3 Expressive, the search bar expands when focused; the margins change from 24dp to 12dp.

### 9. Do / Don't
- Do place the search bar at the top of the content in most cases.
- Do use the contained style (recommended); divided is not recommended in M3 Expressive.
- Do keep the search bar close to the content a person can search.
- Do use a maximum of two trailing icons; combine an avatar with up to one other trailing icon button.
- Do add variety and context to suggestions/results: leading icons related to suggestions; category labels like **Recent**, **Contacts**, or **Suggestions**; avatars or other high-priority items; filter chips to narrow down results.
- Do show search results in a compact, organized list with an indicator like **Quick results**.
- Don't change the search bar container's behavior between unfocused and focused in the contained style.
- Don't use a **surface container high** color on a **surface container** background.

### 10. Accessibility
- Focused search needs a clear status indicator that it's searching content, like a search icon or **Results** label.
- Autosuggest: when search suggestions and results appear, the screen reader must announce the change so people know list items are available for selection.
- Assistive tech must let people: navigate to and focus on a search bar; view the hinted search text or persistent label; input text and complete a search; interact with a list of search suggestions and results; clear the input text.
- Initial focus lands on the first interactive element — often a leading icon button or text field. A leading icon button usually activates search directly or opens a navigation component. If there's no leading icon, focus lands on the text field.

| Keys | Actions |
|---|---|
| **Tab** or **Shift** + **Tab** | Navigate between interactive elements |
| **Space** or **Enter** | Activate the search text field for input |
| **Arrows** | Navigate between search result items |

- Labeling: the hinted search text should be used as the accessibility label describing the search bar. Role for the input field: Android **Text field**; iOS **Search field**. Leading and trailing icon buttons follow icon-button accessibility guidance. Search suggestions and results use the list component — screen readers automatically announce the results as a list; follow list accessibility guidelines for labels.

### Differences from M2 to M3 baseline
- Color: new color mappings and compatibility with dynamic color.
- Elevation: lower elevation and no shadow by default.
- Name: search was formerly known as open search bar.
- Variants: two official variants of search components: search bar and search view.
- M2 open search bars were square and elevated; M3 search bars are rounded, use tonal surface, and support dynamic color.
