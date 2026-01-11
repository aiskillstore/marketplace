# Debugging Workflow Examples

This document demonstrates the complete debugging workflow using the TRACE framework with real-world examples.

## Example 1: Python AttributeError - Simple Case

### Initial Error Report

```
User reports: "The application crashes when trying to view user profile"
```

### T - TRACE the Error

**Full Error Message:**
```
Traceback (most recent call last):
  File "app.py", line 45, in view_profile
    profile_data = user.profile.to_dict()
AttributeError: 'NoneType' object has no attribute 'to_dict'
```

**Reproduction Steps:**
1. Log in as user "john@example.com"
2. Navigate to /profile
3. Error occurs every time

**Environment:** Production server, Python 3.9, Django 4.0

### R - READ the Error Message

**Error Type:** `AttributeError`
- Attempting to access attribute on None object
- This means `user.profile` is None, not a Profile object

**Error Location:**
- File: `app.py`
- Line: 45
- Function: `view_profile`

**Error Category:** Runtime error - null reference

### A - ANALYZE the Context

**Code Review:**
```python
# app.py, line 45
def view_profile(request):
    user = request.user
    profile_data = user.profile.to_dict()  # Line 45 - ERROR HERE
    return render(request, 'profile.html', {'profile': profile_data})
```

**Data Analysis:**
- User "john@example.com" exists in database
- Checking user record shows `profile_id` is NULL
- Profile was never created for this user

**Environment Check:**
- User model expects one-to-one relationship with Profile
- No migration to create profiles for existing users

### C - CHECK for Root Cause

**Root Cause Identified:**
- Old users (before Profile model was added) don't have profiles
- Code assumes all users have profiles
- No null check or default profile creation

**Hypothesis Testing:**
```python
# Test: Check if other users have profiles
>>> User.objects.filter(profile__isnull=True).count()
47  # 47 users without profiles!
```

### E - EXECUTE the Fix

**Fix Design:**
1. Add null check in view
2. Create profile if missing
3. Backfill profiles for existing users

**Implementation:**
```python
def view_profile(request):
    user = request.user

    # Fix: Create profile if it doesn't exist
    if not hasattr(user, 'profile') or user.profile is None:
        Profile.objects.create(user=user)

    profile_data = user.profile.to_dict()
    return render(request, 'profile.html', {'profile': profile_data})
```

**Migration to backfill:**
```python
# migrations/0012_backfill_profiles.py
from django.db import migrations

def create_missing_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('accounts', 'Profile')

    users_without_profiles = User.objects.filter(profile__isnull=True)
    for user in users_without_profiles:
        Profile.objects.create(user=user)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0011_profile_model'),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles),
    ]
```

**Verification:**
1. Run migration
2. Test with user "john@example.com" - ✓ Works
3. Test with new users - ✓ Works
4. Check all users have profiles - ✓ Confirmed
5. No new errors in logs - ✓ Clean

**Prevention:**
- Added test case for users without profiles
- Updated user creation to always create profile
- Documented the user-profile relationship

---

## Example 2: JavaScript Promise Rejection - Async Issue

### Initial Error Report

```
Users report: "Shopping cart sometimes doesn't update, shows loading spinner forever"
```

### T - TRACE the Error

**Full Error Message (from browser console):**
```
Uncaught (in promise) TypeError: Cannot read property 'items' of undefined
    at updateCart (cart.js:23)
    at cart.js:15
```

**Reproduction Steps:**
1. Add item to cart
2. Click "Update Quantity"
3. Error occurs ~30% of the time (intermittent!)

**Environment:** Chrome 96, React 17, production API

### R - READ the Error Message

**Error Type:** `TypeError` in Promise
- Uncaught promise rejection (no error handler)
- Accessing `items` property on undefined object
- Suggests API response not in expected format

**Error Location:**
- File: `cart.js`
- Line: 23
- Function: `updateCart`

**Error Category:** Runtime error - async/integration issue

### A - ANALYZE the Context

**Code Review:**
```javascript
// cart.js
async function updateCart(itemId, quantity) {
    setLoading(true);

    const response = await fetch('/api/cart/update', {
        method: 'POST',
        body: JSON.stringify({ itemId, quantity }),
        headers: { 'Content-Type': 'application/json' }
    });

    const data = await response.json();  // Line 15

    // Line 23 - ERROR: data.items is undefined sometimes
    const updatedItems = data.items.map(item => ({
        ...item,
        total: item.price * item.quantity
    }));

    setCartItems(updatedItems);
    setLoading(false);
}
```

**Network Analysis:**
- API sometimes returns 500 error
- When error occurs, response body is: `{"error": "Database timeout"}`
- No `items` property in error response

**Race Condition Check:**
- Multiple simultaneous cart updates possible
- Last write wins, but responses come back out of order

### C - CHECK for Root Cause

**Root Cause Identified:**
1. **Missing error handling**: No check for HTTP status code
2. **Assuming success**: Code assumes response always has `items`
3. **No catch block**: Promise rejection unhandled
4. **Backend timeout**: Database query sometimes slow

**Hypothesis Testing:**
```javascript
// Test: Check response when error occurs
fetch('/api/cart/update', {...})
    .then(r => r.json())
    .then(data => console.log(data));

// Result when error: {error: "Database timeout"}
// No items property!
```

### E - EXECUTE the Fix

**Fix Design:**
1. Add proper error handling
2. Check HTTP status before processing
3. Show user-friendly error message
4. Optimize backend query (separate issue)

**Implementation:**
```javascript
async function updateCart(itemId, quantity) {
    setLoading(true);

    try {
        const response = await fetch('/api/cart/update', {
            method: 'POST',
            body: JSON.stringify({ itemId, quantity }),
            headers: { 'Content-Type': 'application/json' }
        });

        // Check for HTTP errors
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update cart');
        }

        const data = await response.json();

        // Validate response structure
        if (!data.items || !Array.isArray(data.items)) {
            throw new Error('Invalid response format');
        }

        const updatedItems = data.items.map(item => ({
            ...item,
            total: item.price * item.quantity
        }));

        setCartItems(updatedItems);
        setError(null);

    } catch (error) {
        console.error('Cart update failed:', error);
        setError('Failed to update cart. Please try again.');

        // Don't update cart on error - keep previous state

    } finally {
        setLoading(false);
    }
}
```

**Backend Fix (bonus):**
```python
# views.py - Add timeout and better error handling
from django.db import connection

@api_view(['POST'])
def update_cart(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET statement_timeout = 5000")  # 5 second timeout

        item_id = request.data['itemId']
        quantity = request.data['quantity']

        cart_item = CartItem.objects.select_for_update().get(id=item_id)
        cart_item.quantity = quantity
        cart_item.save()

        # Return full cart
        items = CartItem.objects.filter(cart=cart_item.cart).select_related('product')

        return Response({
            'items': CartItemSerializer(items, many=True).data
        })

    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)
    except Exception as e:
        logger.error(f"Cart update failed: {e}")
        return Response({'error': 'Database error'}, status=500)
```

**Verification:**
1. Test normal update - ✓ Works
2. Simulate backend error - ✓ Shows error message, doesn't crash
3. Test rapid updates - ✓ Handles correctly
4. Test timeout scenario - ✓ Graceful degradation
5. Monitor production - ✓ Error rate dropped from 30% to 0.1%

**Prevention:**
- Added integration tests for API error scenarios
- Added response validation middleware
- Set up backend query performance monitoring
- Added database query timeout
- Created error handling pattern document for team

---

## Example 3: Java NullPointerException - Multi-Layer Issue

### Initial Error Report

```
Production alert: "Payment processing failing for premium users"
```

### T - TRACE the Error

**Full Error Message:**
```
java.lang.NullPointerException: Cannot invoke "com.example.User.getSubscription()" because "user" is null
    at com.example.payment.PaymentProcessor.processPayment(PaymentProcessor.java:45)
    at com.example.payment.PaymentController.handlePayment(PaymentController.java:89)
    at com.example.payment.PaymentController$$FastClassBySpringCGLIB$$1234.invoke(<generated>)
    ...
```

**Reproduction Steps:**
1. Premium user attempts to upgrade subscription
2. Click "Process Payment"
3. Error occurs for ~20% of premium users

**Environment:** Java 11, Spring Boot 2.5, PostgreSQL, production

### R - READ the Error Message

**Error Type:** `NullPointerException`
- Attempting to call `getSubscription()` on null user object
- Suggests user lookup failed

**Error Location:**
- File: `PaymentProcessor.java`
- Line: 45
- Method: `processPayment`

**Call Chain:**
- `PaymentController.handlePayment` → `PaymentProcessor.processPayment`

### A - ANALYZE the Context

**Code Review:**
```java
// PaymentController.java, line 89
@PostMapping("/process")
public ResponseEntity<?> handlePayment(@RequestBody PaymentRequest request) {
    User user = userService.findById(request.getUserId());
    return paymentProcessor.processPayment(user, request.getAmount());
}

// PaymentProcessor.java, line 45
public PaymentResult processPayment(User user, BigDecimal amount) {
    Subscription subscription = user.getSubscription();  // Line 45 - NPE!

    if (subscription.isPremium()) {
        return processPremiumPayment(user, amount);
    }
    return processStandardPayment(user, amount);
}

// UserService.java
public User findById(Long userId) {
    return userRepository.findById(userId).orElse(null);  // Returns null!
}
```

**Data Analysis:**
```sql
-- Check user data
SELECT id, email, deleted_at FROM users WHERE id = 12345;
-- Result: id=12345, email=premium@example.com, deleted_at=2024-01-15
-- User was soft-deleted!
```

**Environment Check:**
- Payment requests include userId from session
- Session not invalidated when user deleted
- Soft-delete doesn't clear sessions

### C - CHECK for Root Cause

**Root Causes Identified:**
1. **Poor error handling**: `findById` returns null instead of throwing exception
2. **No null check**: Controller doesn't validate user exists
3. **Session management**: Deleted users still have valid sessions
4. **Soft delete gap**: Deleted users not handled in payment flow

**Hypothesis Testing:**
```java
// Test: Check if issue is soft-deleted users
User user = userRepository.findById(12345L).orElse(null);
// user is null

User user = userRepository.findByIdAndDeletedAtIsNull(12345L).orElse(null);
// user is null (correct - user is deleted)

// Confirmed: Deleted users trigger the error
```

### E - EXECUTE the Fix

**Fix Design:**
1. Change `findById` to throw exception, not return null
2. Add validation in controller
3. Invalidate sessions on user deletion
4. Add explicit soft-delete filtering

**Implementation:**

```java
// UserService.java - Better error handling
public User findById(Long userId) {
    return userRepository.findByIdAndDeletedAtIsNull(userId)
        .orElseThrow(() -> new UserNotFoundException("User not found: " + userId));
}

// PaymentController.java - Add validation
@PostMapping("/process")
public ResponseEntity<?> handlePayment(@RequestBody PaymentRequest request) {
    try {
        User user = userService.findById(request.getUserId());

        if (user.getSubscription() == null) {
            return ResponseEntity.badRequest()
                .body(new ErrorResponse("User has no subscription"));
        }

        PaymentResult result = paymentProcessor.processPayment(user, request.getAmount());
        return ResponseEntity.ok(result);

    } catch (UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("User account not found"));
    }
}

// PaymentProcessor.java - Defensive programming
public PaymentResult processPayment(User user, BigDecimal amount) {
    Objects.requireNonNull(user, "User cannot be null");
    Objects.requireNonNull(user.getSubscription(), "User must have subscription");

    Subscription subscription = user.getSubscription();

    if (subscription.isPremium()) {
        return processPremiumPayment(user, amount);
    }
    return processStandardPayment(user, amount);
}

// UserRepository.java - Add soft-delete filtering
@Query("SELECT u FROM User u WHERE u.id = :id AND u.deletedAt IS NULL")
Optional<User> findByIdAndDeletedAtIsNull(@Param("id") Long id);

// UserService.java - Invalidate sessions on delete
public void deleteUser(Long userId) {
    User user = findById(userId);
    user.setDeletedAt(LocalDateTime.now());
    userRepository.save(user);

    // Invalidate all sessions for this user
    sessionRegistry.getAllSessions(user, false)
        .forEach(SessionInformation::expireNow);
}
```

**Global Exception Handler:**
```java
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse(e.getMessage()));
    }

    @ExceptionHandler(NullPointerException.class)
    public ResponseEntity<ErrorResponse> handleNullPointer(NullPointerException e) {
        logger.error("Unexpected null pointer", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("An unexpected error occurred"));
    }
}
```

**Verification:**
1. Test payment with active user - ✓ Works
2. Test payment with deleted user - ✓ Returns 404 error gracefully
3. Test payment with no subscription - ✓ Returns clear error message
4. Delete user and verify session invalidated - ✓ Works
5. Monitor production for one week - ✓ No NPEs in payment processing

**Prevention:**
- Added integration tests for soft-deleted users
- Created custom `@NotNull` annotation for critical parameters
- Documented null-handling policy in team guidelines
- Added static analysis rule to flag `.orElse(null)` pattern
- Implemented comprehensive exception handling strategy

---

## Key Takeaways

### Common Patterns Across Examples

1. **Error messages tell a story** - Read them completely
2. **Reproduction is crucial** - Can't fix what you can't reproduce
3. **Check assumptions** - "It should work" isn't debugging
4. **Follow the chain** - Error location ≠ root cause location
5. **Fix the cause, not the symptom** - Null checks mask design issues
6. **Verify thoroughly** - Test the fix and related functionality
7. **Prevent recurrence** - Add tests, documentation, monitoring

### Time Investment by Phase

- **Initial investigation**: 20-30% of time
- **Root cause analysis**: 40-50% of time
- **Implementing fix**: 10-20% of time
- **Verification and prevention**: 20-30% of time

### When to Escalate

Escalate or request help when:
- Can't reproduce the error after reasonable attempts
- Root cause is in unfamiliar codebase/domain
- Fix requires architectural changes
- Time spent exceeds severity threshold
- Need access to production data/systems
