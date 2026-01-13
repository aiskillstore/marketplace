# Widget Loading Patterns

Patterns for creating responsive loading experiences in ChatGPT App widgets.

---

## The Challenge

Tool output arrives **asynchronously**. When a widget first renders, `window.openai.toolOutput` may be empty. The widget must:

1. Show a loading state immediately
2. Poll for data arrival
3. Handle timeouts gracefully
4. Provide step-based progress feedback

---

## Basic Polling Pattern

Poll `window.openai.toolOutput` until data arrives or timeout:

```javascript
const POLL_INTERVAL = 200;  // ms
const MAX_WAIT = 30000;     // 30 seconds

function startPolling(onData, onTimeout) {
  let elapsed = 0;

  const interval = setInterval(() => {
    const output = window.openai?.toolOutput || {};

    if (Object.keys(output).length > 0) {
      clearInterval(interval);
      onData(output);
      return;
    }

    elapsed += POLL_INTERVAL;
    if (elapsed >= MAX_WAIT) {
      clearInterval(interval);
      onTimeout();
    }
  }, POLL_INTERVAL);

  return () => clearInterval(interval);  // Cleanup function
}

// Usage
startPolling(
  (data) => renderContent(data),
  () => showTimeoutError()
);
```

### React Hook Version

```typescript
import { useState, useEffect, useRef } from 'react';

interface UsePollingOptions {
  interval?: number;
  timeout?: number;
}

export function useToolOutputPolling<T>(options: UsePollingOptions = {}) {
  const { interval = 200, timeout = 30000 } = options;

  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isTimeout, setIsTimeout] = useState(false);
  const elapsedRef = useRef(0);

  useEffect(() => {
    const pollInterval = setInterval(() => {
      const output = (window as any).openai?.toolOutput;

      if (output && Object.keys(output).length > 0) {
        clearInterval(pollInterval);
        setData(output as T);
        setIsLoading(false);
        return;
      }

      elapsedRef.current += interval;
      if (elapsedRef.current >= timeout) {
        clearInterval(pollInterval);
        setIsLoading(false);
        setIsTimeout(true);
      }
    }, interval);

    return () => clearInterval(pollInterval);
  }, [interval, timeout]);

  return { data, isLoading, isTimeout };
}

// Usage
function MyWidget() {
  const { data, isLoading, isTimeout } = useToolOutputPolling<MyDataType>();

  if (isLoading) return <LoadingState />;
  if (isTimeout) return <TimeoutError />;
  return <Content data={data} />;
}
```

---

## Step-Based Progress

Show incremental progress with labeled steps:

```javascript
const LOADING_STEPS = [
  { percent: 0,   label: "Connecting...",      delay: 0 },
  { percent: 25,  label: "Fetching data...",   delay: 500 },
  { percent: 50,  label: "Processing...",      delay: 2000 },
  { percent: 75,  label: "Almost ready...",    delay: 5000 },
  { percent: 95,  label: "Finalizing...",      delay: 10000 },
];

function initStepProgress(updateProgress) {
  let currentStep = 0;

  // Schedule each step
  LOADING_STEPS.forEach((step, index) => {
    setTimeout(() => {
      if (currentStep <= index) {  // Don't go backwards
        currentStep = index;
        updateProgress(step.percent, step.label);
      }
    }, step.delay);
  });

  // Return function to complete progress
  return () => {
    currentStep = LOADING_STEPS.length;
    updateProgress(100, "Done!");
  };
}

// Usage
const completeProgress = initStepProgress((percent, label) => {
  updateProgressRing(percent);
  updateLabel(label);
});

// When data arrives
onDataReceived(() => {
  completeProgress();
  renderContent();
});
```

---

## Flow Detection

Detect the type of operation **before** `toolOutput` is available:

```javascript
function detectFlowType() {
  const input = window.openai?.toolInput || {};
  const meta = window.openai?.toolResponseMetadata || {};

  // Check toolInput first (available immediately)
  if (input._flow) return input._flow;
  if (input.domain || input.company_name) return 'company';
  if (input.linkedin_url || input.person_name) return 'person';
  if (input.deal_id || input.stage) return 'deal';

  // Check metadata (available after tool completes)
  if (meta.viewType) return meta.viewType;

  // Default for unknown flows
  return 'generic';
}

// Customize loading experience per flow type
const FLOW_CONFIGS = {
  person: {
    steps: ["Finding profile...", "Loading experience...", "Analyzing..."],
    icon: "user",
  },
  company: {
    steps: ["Finding company...", "Loading data...", "Processing..."],
    icon: "building",
  },
  deal: {
    steps: ["Loading deal...", "Fetching activities...", "Ready"],
    icon: "briefcase",
  },
  generic: {
    steps: ["Loading...", "Processing...", "Almost ready..."],
    icon: "dots",
  },
};

// Usage
const flowType = detectFlowType();
const config = FLOW_CONFIGS[flowType];
initLoadingExperience(config);
```

---

## Progress Ring Component

Visual circular progress indicator:

### HTML

```html
<div class="loading-container">
  <svg class="progress-ring" viewBox="0 0 100 100">
    <circle class="progress-bg" cx="50" cy="50" r="40" pathLength="100"/>
    <circle class="progress-fill" cx="50" cy="50" r="40" pathLength="100"/>
  </svg>
  <span class="progress-label">Loading...</span>
</div>
```

### CSS

```css
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
}

.progress-ring {
  width: 80px;
  height: 80px;
  transform: rotate(-90deg);  /* Start from 12 o'clock */
}

.progress-bg {
  fill: none;
  stroke: var(--gray-200);
  stroke-width: 8;
}

.progress-fill {
  fill: none;
  stroke: var(--accent-color, #0066cc);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 100;
  stroke-dashoffset: 100;  /* Start at 0% */
  transition: stroke-dashoffset 0.4s ease-out;
}

.progress-label {
  font-size: 14px;
  color: var(--gray-600);
}

/* Dark mode */
.dark-mode .progress-bg {
  stroke: var(--gray-700);
}

.dark-mode .progress-label {
  color: var(--gray-400);
}
```

### JavaScript

```javascript
function updateProgressRing(percent) {
  const fill = document.querySelector('.progress-fill');
  const label = document.querySelector('.progress-label');

  if (fill) {
    // IMPORTANT: Use .style, not setAttribute()
    // CSS overrides SVG attributes - see widget_development.md gotchas
    fill.style.strokeDashoffset = String(100 - percent);
  }
}
```

---

## Timeout Error Handling

Show helpful error when loading times out using safe DOM methods:

```javascript
function showTimeoutError() {
  const container = document.getElementById('loading-container');

  // Clear existing content safely
  while (container.firstChild) {
    container.removeChild(container.firstChild);
  }

  // Build error UI with safe DOM methods
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-state';

  const icon = document.createElement('div');
  icon.className = 'error-icon';
  icon.textContent = '⚠️';

  const title = document.createElement('h3');
  title.textContent = 'Taking longer than expected';

  const message = document.createElement('p');
  message.textContent = 'The server is still processing your request.';

  const button = document.createElement('button');
  button.textContent = 'Try Again';
  button.onclick = retryLoad;

  errorDiv.appendChild(icon);
  errorDiv.appendChild(title);
  errorDiv.appendChild(message);
  errorDiv.appendChild(button);
  container.appendChild(errorDiv);

  // Log diagnostic info for debugging
  console.log('Widget timeout diagnostic:', {
    hasToolOutput: !!window.openai?.toolOutput,
    toolOutputKeys: Object.keys(window.openai?.toolOutput || {}),
    hasToolInput: !!window.openai?.toolInput,
    toolInputKeys: Object.keys(window.openai?.toolInput || {}),
    hasMetadata: !!window.openai?.toolResponseMetadata,
    theme: window.openai?.theme,
    displayMode: window.openai?.displayMode,
  });
}

function retryLoad() {
  // Send follow-up message to retry
  window.openai?.sendFollowUpMessage?.({
    prompt: "Please try that again"
  });
}
```

---

## Re-initialization Guard

Prevent loading state from resetting on re-renders:

```javascript
// Module-level state
let loadingState = {
  initialized: false,
  flowType: null,
  startTime: null,
  timers: [],
};

function initLoadingExperience(flowType) {
  // Guard: don't reinitialize if already running same flow
  if (loadingState.initialized && loadingState.flowType === flowType) {
    return;
  }

  // Clean up any existing timers
  loadingState.timers.forEach(clearTimeout);
  loadingState.timers = [];

  // Initialize new loading state
  loadingState.initialized = true;
  loadingState.flowType = flowType;
  loadingState.startTime = Date.now();

  // Set up progress steps
  const steps = FLOW_CONFIGS[flowType]?.steps || ["Loading..."];
  steps.forEach((label, index) => {
    const delay = index * 2000;  // 2 seconds per step
    const timer = setTimeout(() => {
      updateProgressLabel(label);
      updateProgressRing((index + 1) / steps.length * 100);
    }, delay);
    loadingState.timers.push(timer);
  });
}

function completeLoading() {
  // Clean up
  loadingState.timers.forEach(clearTimeout);
  loadingState.timers = [];
  loadingState.initialized = false;

  // Final state
  updateProgressRing(100);
  updateProgressLabel("Done!");
}

// Widget render function
function render() {
  const output = window.openai?.toolOutput || {};

  if (Object.keys(output).length > 0) {
    completeLoading();
    renderContent(output);
  } else {
    // Loading - but guard against re-init
    const flowType = detectFlowType();
    initLoadingExperience(flowType);
    renderLoadingUI();
  }
}
```

---

## Complete Example

Full loading experience implementation:

```javascript
(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    pollInterval: 200,
    timeout: 30000,
    steps: [
      { percent: 0,   label: "Connecting...",    delay: 0 },
      { percent: 25,  label: "Fetching data...", delay: 500 },
      { percent: 50,  label: "Processing...",    delay: 2000 },
      { percent: 75,  label: "Almost ready...",  delay: 5000 },
      { percent: 95,  label: "Finalizing...",    delay: 10000 },
    ],
  };

  // State
  let state = {
    initialized: false,
    completed: false,
    timers: [],
    pollInterval: null,
  };

  // DOM refs
  let progressFill, progressLabel;

  function init() {
    if (state.initialized) return;
    state.initialized = true;

    // Cache DOM refs
    progressFill = document.querySelector('.progress-fill');
    progressLabel = document.querySelector('.progress-label');

    // Start polling for data
    startPolling();

    // Start step progress
    startStepProgress();
  }

  function startPolling() {
    let elapsed = 0;

    state.pollInterval = setInterval(() => {
      const output = window.openai?.toolOutput || {};

      if (Object.keys(output).length > 0) {
        onDataReceived(output);
        return;
      }

      elapsed += CONFIG.pollInterval;
      if (elapsed >= CONFIG.timeout) {
        onTimeout();
      }
    }, CONFIG.pollInterval);
  }

  function startStepProgress() {
    CONFIG.steps.forEach(step => {
      const timer = setTimeout(() => {
        if (!state.completed) {
          updateProgress(step.percent, step.label);
        }
      }, step.delay);
      state.timers.push(timer);
    });
  }

  function updateProgress(percent, label) {
    if (progressFill) {
      progressFill.style.strokeDashoffset = String(100 - percent);
    }
    if (progressLabel) {
      progressLabel.textContent = label;
    }
  }

  function onDataReceived(data) {
    cleanup();
    state.completed = true;
    updateProgress(100, "Done!");

    // Short delay before showing content
    setTimeout(() => {
      renderContent(data);
    }, 300);
  }

  function onTimeout() {
    cleanup();
    showTimeoutError();
  }

  function cleanup() {
    if (state.pollInterval) {
      clearInterval(state.pollInterval);
    }
    state.timers.forEach(clearTimeout);
    state.timers = [];
  }

  function renderContent(data) {
    // Replace loading UI with actual content using safe DOM methods
    document.getElementById('loading-container').style.display = 'none';
    document.getElementById('content-container').style.display = 'block';
    // ... populate content with data using createElement/textContent
  }

  function showTimeoutError() {
    updateProgress(0, "");
    const container = document.getElementById('loading-container');

    // Clear and rebuild with safe DOM methods
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-state';

    const message = document.createElement('p');
    message.textContent = 'Request timed out. Please try again.';

    errorDiv.appendChild(message);
    container.appendChild(errorDiv);
  }

  // Start on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
```

---

## Diagnostics Checklist

When loading issues occur, check:

1. **Is `toolOutput` populated?**
   ```javascript
   console.log('toolOutput:', window.openai?.toolOutput);
   ```

2. **Is `toolInput` available?**
   ```javascript
   console.log('toolInput:', window.openai?.toolInput);
   ```

3. **What's in metadata?**
   ```javascript
   console.log('metadata:', window.openai?.toolResponseMetadata);
   ```

4. **Is the theme set?**
   ```javascript
   console.log('theme:', window.openai?.theme);
   ```

5. **Server response size?**
   - Check server logs for response size
   - Responses over 300KB may fail to deliver

6. **Session routing correct?**
   - Check server logs for session ID mismatch
   - See [troubleshooting.md](./troubleshooting.md) for session routing issues
