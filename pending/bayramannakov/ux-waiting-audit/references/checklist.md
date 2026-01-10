# UX Waiting States Checklist

Detailed evaluation criteria for each category. Score using: ✅ Present | ⚠️ Partial | ❌ Missing | N/A

---

## 1. Progressive Value Delivery

**Goal**: User sees useful information before operation completes.

| Criteria | What to Look For |
|----------|------------------|
| Partial results visible | Results appear incrementally as found |
| Useful info early | Summary, previews, or counts before full data |
| Value accumulating | More than just a spinner—actual content growing |

**Detection Script:**
```javascript
// Count visible results over time
document.querySelectorAll('[class*="result"], [class*="item"], [class*="card"]').length
```

**Best-in-class**: Search results streaming in as found (Google, Algolia)

---

## 2. Heartbeat Indicators

**Goal**: User knows system is actively working, not frozen.

| Criteria | What to Look For |
|----------|------------------|
| Activity signals | Visual proof system isn't stuck |
| Ticking counters | "Found 12 items", "Processed 47 pages" |
| Movement/animation | Spinner, pulse, progress animation |

**Detection Script:**
```javascript
({
  counters: document.body.innerText.match(/\d+\s*(found|processed|scanning|checked)/gi),
  animations: document.querySelectorAll('[class*="spin"], [class*="pulse"], [class*="animate"]').length,
  cssAnimations: getComputedStyle(document.querySelector('.loading'))?.animation !== 'none'
})
```

**Best-in-class**: Vercel build logs with live updates

---

## 3. Time Estimation

**Goal**: User knows how long to wait.

| Criteria | What to Look For |
|----------|------------------|
| Time remaining | "~45 sec left", "About 2 minutes" |
| Progress bar/percentage | Visual representation of completion |
| Updating estimate | Time/progress changes as operation proceeds |

**Detection Script:**
```javascript
({
  progressBar: document.querySelector('progress, [role="progressbar"]'),
  percentage: document.body.innerText.match(/\d+\s*%/g),
  timeEstimate: document.body.innerText.match(/(\d+\s*(sec|min)|remaining|left|ETA)/gi)
})
```

**Best-in-class**: File downloads with time remaining

---

## 4. Explanation of Process

**Goal**: User understands why it takes time.

| Criteria | What to Look For |
|----------|------------------|
| What is happening | "Checking 4 sources...", "Analyzing data..." |
| Value justification | Why this wait is worth it |
| Visible steps/phases | "Step 2 of 5: Validating..." |

**Detection Script:**
```javascript
({
  statusText: document.querySelector('[class*="status"]')?.textContent,
  steps: document.querySelectorAll('[class*="step"], [class*="phase"]').length,
  descriptions: document.body.innerText.match(/(checking|analyzing|processing|searching|loading)\s+\w+/gi)
})
```

**Best-in-class**: AI tools showing "Thinking...", "Searching web...", "Writing..."

---

## 5. Sunk Cost Visibility

**Goal**: User feels invested and doesn't want to abandon.

| Criteria | What to Look For |
|----------|------------------|
| Accumulated work shown | "Already scanned 47 pages" |
| Loss aversion trigger | Abandoning feels like losing progress |
| Invested time visible | Time spent or work done counter |

**Detection Script:**
```javascript
({
  workDone: document.body.innerText.match(/(already|so far|completed?)\s*\d+/gi),
  timeSpent: document.body.innerText.match(/(\d+\s*(sec|min)\s*(elapsed|spent))/gi)
})
```

**Best-in-class**: Upload progress showing bytes transferred

---

## 6. Work While You Wait

**Goal**: User isn't blocked from other tasks.

| Criteria | What to Look For |
|----------|------------------|
| Start another task | Can navigate away or do other things |
| Background processing | Operation continues if user leaves |
| Suggested actions | "While you wait, you could..." |
| Completion notification | Alert when done (toast, badge, sound) |

**Detection Script:**
```javascript
({
  nonBlocking: !document.querySelector('[class*="modal"][class*="block"], [class*="overlay"]'),
  backgroundIndicator: document.querySelector('[class*="badge"], [class*="notification"]'),
  canNavigate: !document.body.classList.contains('loading')
})
```

**Best-in-class**: Slack file uploads in background with notification

---

## 7. Interruptible / Early Exit

**Goal**: User has control over speed vs. depth tradeoff.

| Criteria | What to Look For |
|----------|------------------|
| Get partial results early | "Get basic version now" option |
| Speed/depth choice | Quick vs. thorough mode |
| Cancel without total loss | Stop and keep what's done |

**Detection Script:**
```javascript
({
  cancelButton: document.querySelector('button[class*="cancel"], button[class*="stop"]'),
  earlyExit: document.body.innerText.match(/(get results now|quick|basic|skip)/gi),
  preserveProgress: document.querySelector('[class*="partial"], [class*="preview"]')
})
```

**Best-in-class**: ChatGPT stop generation button

---

## 8. Graceful Degradation

**Goal**: Partial failures don't kill the whole operation.

| Criteria | What to Look For |
|----------|------------------|
| Continue despite failures | Operation proceeds with available data |
| Clear error explanation | User understands what failed and why |
| Partial success communicated | "85% complete, X unavailable" |

**Test Method:**
1. Briefly disconnect network during operation
2. Observe error handling
3. Check if partial results preserved

**Best-in-class**: Search engines showing "Some results may be missing"

---

## 9. Completion Celebration

**Goal**: Ending feels positive (peak-end rule).

| Criteria | What to Look For |
|----------|------------------|
| Clear "done" moment | Not just results appearing silently |
| Event feeling | Animation, sound, visual highlight |
| Accomplishment summary | "Built from 47 sources in 58 sec" |
| Key findings highlighted | Most important results emphasized |

**Detection Script:**
```javascript
({
  completionAnimation: document.querySelector('[class*="complete"], [class*="success"], [class*="done"]'),
  summary: document.body.innerText.match(/(\d+\s*(results?|items?|found)|completed? in \d+)/gi),
  celebration: document.querySelector('[class*="confetti"], [class*="checkmark"], [class*="celebrate"]')
})
```

**Best-in-class**: Duolingo lesson completion

---

## 10. Anxiety Reduction

**Goal**: User trusts the system isn't broken.

| Criteria | What to Look For |
|----------|------------------|
| Not frozen/crashed | Clear signs of life |
| Status check option | Way to verify operation is running |
| Intentional framing | "Thorough analysis" not "slow" |

**Detection Script:**
```javascript
({
  lastUpdate: document.querySelector('[class*="timestamp"], [class*="updated"]')?.textContent,
  statusIndicator: document.querySelector('[class*="status"], [class*="active"]'),
  reassuringText: document.body.innerText.match(/(thorough|comprehensive|detailed|careful)/gi)
})
```

**Best-in-class**: Apps that say "This usually takes 30-60 seconds"

---

## Scoring Summary

| # | Category | Score | Notes |
|---|----------|-------|-------|
| 1 | Progressive Value Delivery | | |
| 2 | Heartbeat Indicators | | |
| 3 | Time Estimation | | |
| 4 | Explanation of Process | | |
| 5 | Sunk Cost Visibility | | |
| 6 | Work While You Wait | | |
| 7 | Interruptible / Early Exit | | |
| 8 | Graceful Degradation | | |
| 9 | Completion Celebration | | |
| 10 | Anxiety Reduction | | |

**Total: _/10 categories addressed**
