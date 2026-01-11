---
name: animated-focus
description: This document captures learnings from fixing keyboard navigation issues when floating components (Select, DropdownMenu, Popover) have CSS open/close animations.
---

# Focus Management with CSS Animations

This document captures learnings from fixing keyboard navigation issues when floating components (Select, DropdownMenu, Popover) have CSS open/close animations.

## The Problem

When floating content elements have CSS animations that start at `opacity: 0` (like Tailwind's `animate-in fade-in-0`), the browser may reject `element.focus()` calls because the element is invisible.

### Symptoms

- Component opens correctly with mouse clicks
- Keyboard navigation (arrow keys, Escape) doesn't work after opening with keyboard
- Works fine in demos without animation classes
- Broken in demos with animation classes

### Root Cause

1. CSS animations like `fade-in-0` start the element at `opacity: 0`
2. When `focus()` is called immediately after render, the element is still invisible
3. Browser rejects focus on invisible elements
4. Focus stays on the trigger button instead of moving to content
5. Keyboard events go to trigger (which does nothing when open) instead of content

### Evidence from Console Debugging

```javascript
// After opening select, keyboard events go to trigger, not content:
Document keydown: ArrowDown Target: <button role="combobox" ...>

// Active element is trigger, not content:
Active: BUTTON summit-select-...-trigger
```

## The Solution

Implement a retry mechanism for focus that allows the animation to progress past `opacity: 0` before giving up.

### JavaScript Implementation

```javascript
// src/SummitUI/Scripts/floating.js

/**
 * Focus an element with retry mechanism for animated elements.
 * Elements with CSS animations starting at opacity:0 may reject focus initially.
 * This retries focus up to 5 times with 20ms delays to allow the animation
 * to progress past the invisible state.
 * @param {HTMLElement} element - Element to focus
 */
export function focusElement(element) {
    if (!element) return;
    
    function tryFocus(attempts) {
        element.focus();
        // If focus didn't succeed and we have attempts left, retry
        if (document.activeElement !== element && attempts > 0) {
            setTimeout(() => tryFocus(attempts - 1), 20);
        }
    }
    
    // First attempt after one frame to let CSS apply
    requestAnimationFrame(() => tryFocus(5));
}
```

### Key Points

1. **Use `requestAnimationFrame` first** - Ensures CSS has been applied before attempting focus
2. **Check `document.activeElement`** - Verify if focus actually succeeded
3. **Retry with delays** - 20ms intervals allow animation to progress
4. **Limited attempts** - 5 retries = 100ms max wait, enough for typical animations
5. **Apply to all focus functions** - Both `focusElement(element)` and `focusElementById(id)` need this pattern

### Functions Updated

- `floating.js:focusElement(element)` - Used by SelectContent
- `floating.js:focusElementById(elementId)` - Used by DropdownMenuContent

## Testing

Added "With Animations" sections to test demo pages and corresponding Playwright tests.

### CSS Animation Classes for Testing

```css
/* tests/SummitUI.Tests.Manual/SummitUI.Tests.Manual/wwwroot/app.css */

@keyframes fadeInZoomIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes fadeOutZoomOut {
    from {
        opacity: 1;
        transform: scale(1);
    }
    to {
        opacity: 0;
        transform: scale(0.95);
    }
}

.animated-content[data-state="open"] {
    animation: fadeInZoomIn 150ms ease-out forwards;
}

.animated-content[data-state="closed"] {
    animation: fadeOutZoomOut 150ms ease-in forwards;
}
```

### Test Cases

For each component (Select, DropdownMenu, Popover):

| Test | What It Verifies |
|------|------------------|
| `Animated*_ShouldOpen_OnEnterKey` | Opens with keyboard when animations present |
| `Animated*_ShouldNavigate_WithArrowKeys` | Arrow keys work after animated open |
| `Animated*_ShouldSelect/Activate_OnEnterKey` | Can select/activate item after animated open |
| `Animated*_ShouldClose_OnEscape` | Escape triggers close animation |

### Running Animation Tests

```bash
dotnet run --project tests/SummitUI.Tests.Playwright -- --treenode-filter '/*/*/*/Animated*'
```

## Files Involved

| File | Purpose |
|------|---------|
| `src/SummitUI/Scripts/floating.js` | Contains `focusElement` and `focusElementById` functions |
| `src/SummitUI/Components/Select/SelectContent.cs` | Calls `FocusElementAsync` on open |
| `src/SummitUI/Components/DropdownMenu/DropdownMenuContent.cs` | Calls `FocusElementByIdAsync` for menu items |
| `src/SummitUI/Components/Popover/PopoverContent.cs` | Manages focus for popover content |

## Alternative Approaches Considered

1. **Longer initial delay** - Could use 50-100ms delay before first focus attempt, but adds noticeable lag
2. **Focus before animation starts** - Would require changes to render order, complex
3. **Disable animation during focus** - Would cause visual glitch
4. **CSS `visibility` instead of `opacity`** - Would require changes to how animations are authored

The retry mechanism was chosen because it:
- Works with any animation duration
- Doesn't require changes to CSS authoring
- Has minimal performance impact
- Fails gracefully if focus never succeeds

## Related Patterns

This pattern is similar to how bits-ui handles animated presence in Svelte components. The key insight is that DOM operations (like focus) may need to wait for CSS animations to reach a focusable state.
