---
name: Error Handling Fundamentals
description: Auto-invoke when reviewing try/catch blocks, API error responses, async operations, or user feedback patterns. Enforces graceful degradation and meaningful error messages.
---

# Error Handling Fundamentals Review

> "Errors are not failures — they're information. Handle them like the valuable data they are."

## When to Apply

Activate this skill when reviewing:
- try/catch blocks
- Promise chains (.then/.catch)
- API error responses
- Form validation
- Network request handling
- User-facing error messages

---

## Review Checklist

### Error Catching

- [ ] **No empty catches**: Is every catch block doing something meaningful?
- [ ] **Proper scope**: Are errors caught at the right level?
- [ ] **Context added**: Do errors include helpful debugging info?
- [ ] **Finally used**: Are cleanup operations in finally blocks?

### User Experience

- [ ] **User-friendly messages**: Will users understand the error?
- [ ] **No technical details exposed**: Are stack traces hidden from users?
- [ ] **Actionable feedback**: Does the error tell users what to do next?
- [ ] **Graceful degradation**: Does the app still work partially on error?

### Logging & Debugging

- [ ] **Errors logged**: Are errors recorded for debugging?
- [ ] **Context in logs**: Do logs include request ID, user ID, etc.?
- [ ] **Severity levels**: Are critical errors distinguished from warnings?

### Recovery

- [ ] **Retry logic**: Should this operation retry on failure?
- [ ] **Fallback values**: Is there a sensible default on error?
- [ ] **Loading states**: Is the user informed while retrying?

---

## Common Mistakes (Anti-Patterns)

### 1. The Empty Catch (The Silent Killer)
```
❌ try {
     await submitForm();
   } catch (error) {
     // TODO: handle later (never happens)
   }

✅ try {
     await submitForm();
   } catch (error) {
     console.error('Form submission failed:', error);
     setError('Could not submit. Please try again.');
   }
```

### 2. Catching Too Early
```
❌ function getUser(id) {
     try {
       return database.query(id);
     } catch {
       return null; // Caller has no idea it failed
     }
   }

✅ function getUser(id) {
     return database.query(id); // Let caller decide
   }

   // In UI layer
   try {
     const user = await getUser(id);
   } catch (error) {
     showToast('Could not load user');
   }
```

### 3. Generic Error Messages
```
❌ catch (error) {
     setError('An error occurred');
   }

✅ catch (error) {
     if (error.code === 'NETWORK_ERROR') {
       setError('Check your internet connection');
     } else if (error.code === 'NOT_FOUND') {
       setError('User not found');
     } else {
       setError('Something went wrong. Please try again.');
     }
   }
```

### 4. Leaking Stack Traces
```
❌ res.status(500).json({
     error: error.message,
     stack: error.stack
   });

✅ logger.error('Request failed', { error, requestId });
   res.status(500).json({
     error: 'Something went wrong'
   });
```

### 5. Forgetting Finally
```
❌ try {
     setLoading(true);
     await fetchData();
     setLoading(false);
   } catch (error) {
     handleError(error);
     // Loading stays true forever!
   }

✅ try {
     setLoading(true);
     await fetchData();
   } catch (error) {
     handleError(error);
   } finally {
     setLoading(false); // Always runs
   }
```

---

## Socratic Questions

Ask the junior these questions instead of giving answers:

1. **Empty Catch**: "What happens if this fails silently?"
2. **User Message**: "If you were the user, would this message help you?"
3. **Recovery**: "Should we retry this automatically?"
4. **Scope**: "Is this the right place to catch this error?"
5. **Logging**: "How will you debug this in production?"

---

## Error Message Guidelines

### Do
- Be specific: "The email address is already registered"
- Be helpful: "Please check your internet connection"
- Offer next steps: "Try again" or "Contact support"
- Match severity: Critical errors need more attention than warnings

### Don't
- Show technical details: `TypeError: Cannot read property 'map' of undefined`
- Be vague: "An error occurred"
- Blame the user: "You entered invalid data"
- Use jargon: "HTTP 500 Internal Server Error"

---

## Error Handling Patterns

### API/Network Errors
```typescript
async function fetchWithRetry(url: string, retries = 3): Promise<Response> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response;
  } catch (error) {
    if (retries > 0) {
      await sleep(1000);
      return fetchWithRetry(url, retries - 1);
    }
    throw error;
  }
}
```

### Form Validation
```typescript
function validateForm(data: FormData) {
  const errors: Record<string, string> = {};

  if (!data.email) {
    errors.email = 'Email is required';
  } else if (!isValidEmail(data.email)) {
    errors.email = 'Please enter a valid email';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}
```

### React Error Boundaries
```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    logError(error, info);
  }

  render() {
    if (this.state.hasError) {
      return <FallbackUI />;
    }
    return this.props.children;
  }
}
```

---

## Standards Reference

See detailed patterns in:
- `/standards/global/error-handling.md`

---

## Red Flags to Call Out

| Flag | Question to Ask |
|------|-----------------|
| Empty catch block | "What happens when this fails?" |
| `catch (e) { return null }` | "How will the caller know it failed?" |
| No loading state | "What does the user see while waiting?" |
| Technical error shown | "Will the user understand this message?" |
| No finally for cleanup | "Is loading state stuck on error?" |
| console.log instead of error | "How will you find this in production logs?" |
