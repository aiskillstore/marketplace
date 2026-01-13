---
name: error-tracking-integrator
description: Adds comprehensive error tracking with Sentry, Rollbar, or similar services including error boundaries, context, and breadcrumbs. Use when user requests error monitoring or mentions production debugging.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Error Tracking Integrator

Integrates error tracking services into applications for better production debugging and monitoring.

## When to Use
- User requests error monitoring or tracking
- Setting up production error logging
- User mentions "Sentry", "error tracking", "crash reporting", or "production debugging"

## Instructions

### 1. Detect Framework

Identify application framework:
- React, Vue, Angular (frontend)
- Express, Fastify (Node.js backend)
- Django, Flask (Python)
- Rails (Ruby)

### 2. Choose Error Tracking Service

**Popular services:**
- **Sentry**: Most popular, comprehensive
- **Rollbar**: Good for backend
- **Bugsnag**: Multi-platform
- **Airbrake**: Ruby-focused
- **LogRocket**: Session replay + errors

### 3. Install and Configure

**Sentry (React example):**
```bash
npm install @sentry/react
```

```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay()
  ],
});
```

**Sentry (Node.js/Express):**
```javascript
const Sentry = require("@sentry/node");

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
});

// Request handler (first middleware)
app.use(Sentry.Handlers.requestHandler());

// Error handler (after all routes, before error middleware)
app.use(Sentry.Handlers.errorHandler());
```

### 4. Add Error Boundaries (React)

```javascript
import { ErrorBoundary } from '@sentry/react';

function App() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <YourApp />
    </ErrorBoundary>
  );
}
```

### 5. Add Context

**User context:**
```javascript
Sentry.setUser({
  id: user.id,
  email: user.email,
  username: user.username
});
```

**Tags:**
```javascript
Sentry.setTag("page_locale", "en-US");
Sentry.setTag("feature_flag", "new_ui");
```

**Context:**
```javascript
Sentry.setContext("order", {
  id: order.id,
  total: order.total,
  items: order.items.length
});
```

### 6. Breadcrumbs

Track user actions leading to error:

```javascript
Sentry.addBreadcrumb({
  category: "auth",
  message: "User logged in",
  level: "info"
});

Sentry.addBreadcrumb({
  category: "ui",
  message: "Button clicked",
  data: { buttonId: "submit-form" }
});
```

### 7. Manual Error Capture

```javascript
try {
  riskyOperation();
} catch (error) {
  Sentry.captureException(error, {
    tags: { section: "payment" },
    level: "error",
    extra: { orderId: order.id }
  });
}
```

### 8. Filter Sensitive Data

**Scrub PII:**
```javascript
Sentry.init({
  beforeSend(event, hint) {
    // Don't send if contains sensitive data
    if (event.request?.data?.password) {
      delete event.request.data.password;
    }
    return event;
  },
  ignoreErrors: [
    // Ignore browser extension errors
    /extensions\//i,
    /^Non-Error promise rejection/,
  ]
});
```

### 9. Source Maps (Production)

Enable source maps for readable stack traces:

**Webpack:**
```javascript
// webpack.config.js
module.exports = {
  devtool: 'source-map',
  plugins: [
    new SentryWebpackPlugin({
      org: "your-org",
      project: "your-project",
      authToken: process.env.SENTRY_AUTH_TOKEN,
      include: "./dist",
    }),
  ],
};
```

### 10. Alert Configuration

Set up alerts for:
- New issues
- Regression (resolved issue occurs again)
- Spike in error rate
- Critical errors (payment, auth failures)

### 11. Performance Monitoring

Add transaction tracking:

```javascript
const transaction = Sentry.startTransaction({
  name: "processOrder",
  op: "task"
});

try {
  await processOrder();
} finally {
  transaction.finish();
}
```

### 12. Best Practices

- **Environment separation**: Different projects for dev/staging/prod
- **Release tracking**: Tag errors with release version
- **Sample rates**: 100% errors, lower% for performance
- **Team notifications**: Slack/email integration
- **Issue assignment**: Auto-assign to code owners
- **Error grouping**: Custom fingerprinting for better grouping
- **Don't log sensitive data**: PII, passwords, tokens

## Supporting Files
- `templates/sentry-react.js`: React integration template
- `templates/sentry-node.js`: Node.js integration template
- `templates/sentry-python.py`: Python integration template
