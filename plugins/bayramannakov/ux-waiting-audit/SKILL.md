---
name: ux-waiting-audit
description: Audit UX waiting states for web applications with long-running operations (30+ seconds). Use when asked to evaluate, audit, or analyze a product's loading states, wait times, progress indicators, or user experience during slow operations. Requires browser automation (Chrome MCP tools). Generates comprehensive reports with screenshots, checklist evaluation, and prioritized recommendations.
---

# UX Waiting States Audit

Evaluate how applications handle long-running operations (30+ seconds) using browser automation.

## Core Principle

**Screenshot First, DOM Second** — always take a screenshot when navigating or stuck. Visual inspection beats DOM probing.

```
📸 Screenshot → 👀 Analyze visually → 🎯 Click coordinates → 📸 Verify → Repeat
```

---

## Critical: Screenshot-First Automation

### When to Screenshot

ALWAYS screenshot:
- After opening any URL (initial state)
- Before trying to interact with elements  
- When ANY JavaScript returns "missing value" or fails
- After clicking/submitting (verify success)
- At timed intervals during long operations

### Why Screenshots Beat DOM Probing

| DOM Approach | Screenshot Approach |
|--------------|---------------------|
| Complex selectors fail silently | Visual shows exact UI state |
| "missing value" gives no info | Image reveals button locations |
| 10+ attempts to find element | 1 screenshot → click coordinates |
| Can't see actual user experience | See exactly what user sees |

### Screenshot Workflow Pattern

```python
# 1. Navigate
Control Chrome:open_url(TARGET_URL)
sleep(2)

# 2. ALWAYS screenshot first
# Use browser screenshot or html2canvas
# Analyze the image before ANY interaction

# 3. If interaction needed, prefer coordinates over selectors
# After seeing screenshot: "The submit button is at ~(1200, 650)"
Control Chrome:execute_javascript("document.elementFromPoint(1200, 650).click()")

# 4. Screenshot again to verify
```

---

## Quick Start Workflow

### Phase 1: Setup & Navigate

```python
# 1. Navigate to target URL
Control Chrome:open_url(TARGET_URL)
sleep(3)

# 2. SCREENSHOT - See what loaded
# Analyze: What's visible? Where are interactive elements?

# 3. Ask user to help identify:
#    - Which operation to test
#    - How to trigger it (button location, input needed)
```

### Phase 2: Trigger Operation (The Hard Part)

**This is often where audits get stuck.** Modern SPAs have complex UIs.

```python
# Strategy 1: Ask user for guidance
# "I see the page. Can you describe where the button is or what to click?"

# Strategy 2: Use simple, targeted JS
Control Chrome:execute_javascript("document.querySelector('button[type=submit]').click()")

# Strategy 3: Coordinate-based clicking (after screenshot)
Control Chrome:execute_javascript("document.elementFromPoint(X, Y).click()")

# Strategy 4: Let user trigger manually
# "Please click the button to start the operation, then tell me when it's processing"
```

### Phase 3: Capture Waiting States

Once operation is running:
```python
# T+0s: Screenshot immediately when operation starts
# T+10s: Screenshot after 10 seconds
sleep(10)
# Screenshot + capture_state.js

# T+30s: Screenshot after 30 seconds  
sleep(20)
# Screenshot + capture_state.js

# T+Complete: Screenshot when done
# Watch for UI changes indicating completion
```

### Phase 4: Evaluate & Report

```python
# 1. Evaluate screenshots against checklist (see references/checklist.md)
# 2. Generate report with annotated screenshots
# 3. Prioritize recommendations
```

---

## Troubleshooting: When Stuck

### Problem: Can't find/click element

```
❌ WRONG: Keep trying different selectors
   → Wastes time, silent failures

✅ RIGHT: Take screenshot, analyze visually
   → Ask user for help if needed
   → Use coordinate-based clicking
```

### Problem: JavaScript returns "missing value"

This usually means:
1. The script is too complex (simplify it)
2. The element doesn't exist (screenshot to verify)
3. Timing issue (add sleep, retry)

**Fix:** Use simple one-liner JS, not complex functions.

```javascript
// ❌ Complex (fails silently)
(function() { const elements = []; ... return JSON.stringify(elements); })()

// ✅ Simple (clear result)
document.body.innerText.substring(0, 500)
document.querySelectorAll('button').length
document.querySelector('.loading') !== null
```

### Problem: Form won't submit

Try in order:
1. Screenshot to see submit button location
2. `document.forms[0].submit()`
3. Click submit button by coordinates
4. Ask user to submit manually

---

## Audit Instructions

### Step 1: Understand the Target

Ask user for:
1. **URL** to audit
2. **Operation** to test (search, report generation, AI task, etc.)
3. **How to trigger** — button name, location, or steps
4. **Expected duration** (helps calibrate screenshot intervals)
5. **Any auth requirements** (login credentials if needed)

**If user is available:** Ask them to trigger the operation manually while you capture screenshots. This avoids navigation complexity.

### Step 2: Capture Sequence

**Always screenshot first.** Then run simple state checks:

```javascript
// Simple one-liners that won't fail silently:

// Check for spinner
!!document.querySelector('[class*="spin"], [class*="load"], .spinner')

// Check for progress bar
!!document.querySelector('progress, [role="progressbar"]')

// Get visible text (look for status messages)
document.body.innerText.substring(0, 1000)

// Count results appearing
document.querySelectorAll('[class*="result"], [class*="item"]').length
```

**Capture Timeline:**
| Time | Action |
|------|--------|
| T+0s | Screenshot + note what triggered |
| T+10s | Screenshot + simple state checks |
| T+30s | Screenshot + simple state checks |
| T+Complete | Screenshot + final state |

### Step 3: Evaluate Against Checklist

Load and evaluate against `references/checklist.md`. Score each category:
- ✅ Present and well-implemented
- ⚠️ Partially implemented / needs improvement  
- ❌ Missing
- N/A Not applicable to this operation

### Step 4: Generate Report

Use template from `references/report-template.md`.

---

## Key Evaluation Patterns

### Progressive Value Detection

Look for:
```javascript
// Partial results appearing
document.querySelectorAll('[class*="result"], [class*="item"], li, tr').length

// Streaming content
document.querySelector('[class*="stream"], [class*="typing"], [class*="cursor"]')
```

### Heartbeat Indicators

Look for:
```javascript
// Counters
document.body.innerText.match(/\d+\s*(found|processed|complete|%)/gi)

// Animations (CSS or JS)
document.querySelectorAll('[class*="animate"], [class*="pulse"], [class*="spin"]')
```

### Time Estimation

Look for:
```javascript
// Time remaining text
document.body.innerText.match(/(\d+\s*(sec|min|second|minute)|remaining|left|ETA)/gi)

// Progress percentage
document.querySelector('[role="progressbar"]')?.getAttribute('aria-valuenow')
```

---

## Screenshot Comparison Strategy

For each interval, note:
1. **What changed** from previous screenshot
2. **Activity signals** (counters, animations, partial results)
3. **User anxiety factors** (frozen UI, no feedback)

Compare:
| Element | T+0s | T+10s | T+30s | Complete |
|---------|------|-------|-------|----------|
| Results visible | | | | |
| Counter/progress | | | | |
| Status message | | | | |
| Animation active | | | | |

---

## Report Output Structure

Generate markdown report with:

1. **Summary Score**: X/10 categories addressed
2. **Screenshots Gallery**: With timestamps and annotations
3. **Strengths**: What works well
4. **Critical Gaps**: Missing elements hurting UX most
5. **Quick Wins**: Low-effort, high-impact improvements
6. **Detailed Findings Table**: See `references/report-template.md`
7. **Priority Matrix**: P1/P2/P3 recommendations

---

## Best-in-Class Comparisons

Reference these examples of excellent waiting UX:
- **Figma exports**: Progress bar + percentage + file count
- **Notion AI**: Streaming text + cursor animation
- **ChatGPT**: Token-by-token streaming + stop button
- **Linear search**: Instant partial results + refinement
- **Vercel deployments**: Step-by-step progress + logs

---

## Error Scenarios to Test

If possible, test:
1. **Partial failure**: Does UI degrade gracefully?
2. **Network interruption**: Is progress preserved?
3. **Timeout**: Is there clear feedback?

```javascript
// Simulate slow network (if DevTools available)
// Or disconnect briefly and observe behavior
```

---

## Common Issues to Flag

| Issue | User Impact | Quick Fix |
|-------|-------------|-----------|
| Spinner only | Anxiety, abandon | Add status text |
| No progress | "Is it stuck?" | Add heartbeat counter |
| No cancellation | Trapped feeling | Add cancel button |
| Silent completion | Missed results | Add completion animation |
| Full-page block | Can't multitask | Move to background |
