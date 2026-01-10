// UX Waiting States - Simple State Checks
// Execute these ONE AT A TIME via Control Chrome:execute_javascript
// Complex functions often return "missing value" - use simple one-liners instead

// ============================================
// BASIC STATE CHECKS (use these individually)
// ============================================

// 1. Has spinner/loader?
!!document.querySelector('[class*="spin"], [class*="load"], [class*="loader"], .spinner, .loading')

// 2. Has progress bar?  
!!document.querySelector('progress, [role="progressbar"], [class*="progress-bar"]')

// 3. Has animation?
!!document.querySelector('[class*="animate"], [class*="pulse"]')

// 4. Get visible text (first 1000 chars)
document.body.innerText.substring(0, 1000)

// 5. Count result items
document.querySelectorAll('[class*="result"], [class*="item"], [class*="card"]').length

// 6. Check for status/progress text
document.body.innerText.match(/\d+\s*%|\d+\s*(sec|min|found|processed|complete)/gi)

// 7. Has cancel/stop button?
!!document.querySelector('[class*="cancel"], [class*="stop"], [aria-label*="stop"]')

// 8. Is UI blocking? (modal/overlay)
!!document.querySelector('[class*="modal"], [class*="overlay"], [class*="backdrop"]')

// 9. Has error state?
!!document.querySelector('[class*="error"], [class*="fail"], [role="alert"]')

// 10. Has success/complete indicator?
!!document.querySelector('[class*="success"], [class*="complete"], [class*="done"]')


// ============================================
// COMBINED CHECK (try this first)
// If it returns "missing value", fall back to individual checks above
// ============================================

JSON.stringify({
  hasSpinner: !!document.querySelector('[class*="spin"], [class*="load"]'),
  hasProgress: !!document.querySelector('progress, [role="progressbar"]'),
  resultCount: document.querySelectorAll('[class*="result"], [class*="item"]').length,
  textSnippet: document.body.innerText.substring(0, 300)
})


// ============================================
// COORDINATE-BASED CLICKING
// Use after taking screenshot and identifying element position
// ============================================

// Click element at coordinates (replace X, Y):
document.elementFromPoint(X, Y).click()

// Get element info at coordinates:
var el = document.elementFromPoint(X, Y); el ? el.tagName + ': ' + el.textContent.substring(0,30) : 'nothing'

// Find clickable elements and their positions:
var btns = document.querySelectorAll('button'); var s = ''; for (var i = 0; i < btns.length; i++) { var r = btns[i].getBoundingClientRect(); if (r.width > 0) s += i + ': (' + Math.round(r.left) + ',' + Math.round(r.top) + ') ' + btns[i].innerText.substring(0,15) + '\n'; } s


// ============================================
// NAVIGATION HELPERS
// ============================================

// Current URL
window.location.href

// Page title
document.title

// Document ready state
document.readyState

// Count all buttons
document.querySelectorAll('button').length

// Find input/textarea
document.querySelectorAll('input, textarea, [contenteditable]').length

// Submit form (if exists)
document.forms[0] && document.forms[0].submit()
