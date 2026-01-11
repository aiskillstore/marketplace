# Test Case Template

## Test Case ID: TC-[NUMBER]

**Module/Feature**: [Feature Name]
**Priority**: [Critical / High / Medium / Low]
**Test Type**: [Unit / Integration / E2E / Performance]
**Status**: [Not Started / In Progress / Completed / Blocked]

---

## Test Information

**Created by**: [Your Name]
**Created date**: YYYY-MM-DD
**Last updated**: YYYY-MM-DD
**Estimated time**: [X minutes]

---

## Objective

Brief description of what this test validates.

---

## Preconditions

List all preconditions that must be met before executing this test:
- [ ] User account exists in test database
- [ ] Test environment is running
- [ ] Test data is seeded
- [ ] Required services are healthy

---

## Test Data

| Field | Value | Notes |
|-------|-------|-------|
| User email | test@example.com | Valid test user |
| Password | Test123! | Meets password requirements |
| Product ID | 12345 | Active product in catalog |

---

## Test Steps

### Given (Initial Context)
Describe the initial state of the system:
- User is logged in as `test@example.com`
- Shopping cart is empty
- User has valid payment method on file

### When (Action)
Describe the action being tested:
1. Navigate to product page `/products/12345`
2. Click "Add to Cart" button
3. Navigate to cart page `/cart`
4. Click "Checkout" button
5. Complete payment form
6. Click "Place Order" button

### Then (Expected Result)
Describe the expected outcome:
- Order confirmation page is displayed
- Order number is shown in format `ORD-XXXXXX`
- Email confirmation is sent to `test@example.com`
- Inventory is decremented by 1 for product 12345
- Payment charge appears in Stripe dashboard
- Database shows order with status "completed"

---

## Detailed Test Steps (Alternative Format)

| Step # | Action | Expected Result | Actual Result | Pass/Fail |
|--------|--------|-----------------|---------------|-----------|
| 1 | Navigate to `/login` | Login page loads | | |
| 2 | Enter email `test@example.com` | Email field populated | | |
| 3 | Enter password `Test123!` | Password field masked | | |
| 4 | Click "Login" button | Redirected to dashboard | | |
| 5 | Navigate to `/products/12345` | Product page loads | | |
| 6 | Click "Add to Cart" | Success message shown | | |
| 7 | Navigate to `/cart` | Cart shows 1 item | | |
| 8 | Click "Checkout" | Checkout page loads | | |
| 9 | Fill payment details | Form validates successfully | | |
| 10 | Click "Place Order" | Order confirmation shown | | |

---

## Validation Checkpoints

Verify the following after test execution:

**UI Validation:**
- [ ] Success message displays: "Order placed successfully"
- [ ] Order number shown in correct format
- [ ] Order summary matches cart contents
- [ ] Payment confirmation appears

**API Validation:**
- [ ] `POST /api/orders` returns 201 status
- [ ] Response includes order ID, status, and total
- [ ] `GET /api/orders/:id` returns complete order details

**Database Validation:**
- [ ] Order record exists in `orders` table
- [ ] Order items exist in `order_items` table
- [ ] Inventory decremented in `products` table
- [ ] Payment record exists in `payments` table

**Integration Validation:**
- [ ] Email sent to user's email address
- [ ] Payment charge processed in Stripe
- [ ] Inventory service notified of stock change

---

## Test Code (Automated)

```typescript
import { test, expect } from '@playwright/test';

test('TC-001: User can complete checkout flow', async ({ page }) => {
  // Given: User is logged in
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'Test123!');
  await page.click('[data-testid="login-button"]');
  await expect(page).toHaveURL('/dashboard');

  // When: User adds item and checks out
  await page.goto('/products/12345');
  await page.click('[data-testid="add-to-cart"]');
  await expect(page.locator('[data-testid="success-message"]')).toBeVisible();

  await page.goto('/cart');
  await expect(page.locator('[data-testid="cart-item"]')).toHaveCount(1);

  await page.click('[data-testid="checkout-button"]');
  await page.fill('[data-testid="card-number"]', '4242424242424242');
  await page.fill('[data-testid="card-expiry"]', '12/25');
  await page.fill('[data-testid="card-cvc"]', '123');
  await page.click('[data-testid="submit-payment"]');

  // Then: Order confirmation is shown
  await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible();
  const orderNumber = await page.locator('[data-testid="order-number"]').textContent();
  expect(orderNumber).toMatch(/ORD-\d{6}/);

  // Verify database state
  const order = await db.orders.findOne({ order_number: orderNumber });
  expect(order).toBeTruthy();
  expect(order.status).toBe('completed');
  expect(order.user_email).toBe('test@example.com');
});
```

---

## Edge Cases and Variations

List alternative scenarios and edge cases:

**Variation 1: Out of Stock**
- When: User tries to checkout with out-of-stock item
- Then: Error message shown, order not created

**Variation 2: Payment Failure**
- When: Payment gateway returns failure
- Then: Error displayed, order status = "payment_failed"

**Variation 3: Invalid Coupon Code**
- When: User enters expired coupon code
- Then: Coupon not applied, error message shown

**Variation 4: Guest Checkout**
- When: User not logged in
- Then: Can still checkout but must provide email

---

## Dependencies

This test depends on:
- Product catalog service is healthy
- Payment gateway sandbox is available
- Email service is configured
- Inventory service is running

**Blocked by**: None
**Blocks**: TC-002 (Order history verification)

---

## Defects Found

| Bug ID | Description | Severity | Status | Fixed In |
|--------|-------------|----------|--------|----------|
| BUG-123 | Checkout fails for items >$1000 | High | Fixed | v1.2.1 |
| BUG-124 | Email not sent for guest orders | Medium | Open | TBD |

---

## Notes and Comments

- This is a critical path test and must pass before release
- Performance: Full checkout flow should complete in < 5 seconds
- Accessibility: All form fields must have proper ARIA labels
- Mobile: Test should also run on mobile viewport (375x667)

---

## Test Execution History

| Date | Tester | Environment | Result | Duration | Notes |
|------|--------|-------------|--------|----------|-------|
| 2025-10-15 | Jane Smith | Staging | Pass | 18s | First execution |
| 2025-10-20 | John Doe | Staging | Fail | N/A | Payment timeout |
| 2025-10-21 | Jane Smith | Staging | Pass | 16s | After bug fix |

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Test Author** | [Name] | | |
| **Reviewer** | [Name] | | |
| **Approved by** | [QA Lead] | | |

---

**Template Version**: 1.0
**Last Updated**: 2025-10-31
