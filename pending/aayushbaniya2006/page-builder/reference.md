# Tailark Component Reference

Use this reference to select the best components for building landing pages and marketing sites.

## Hero Sections

### `HeroSection`
- **File**: `src/components/tailark/hero-section.tsx`
- **Layout**: Centered text, call to action, 3D tilted card visual, bottom logo strip.
- **Aesthetics**: Modern, high-impact visual with 3D perspective.
- **Simplicity**: Moderate. Requires a hero image (`/card.png`).
- **Recommended**: Yes, for main landing pages.

### `HeroHeader`
- **File**: `src/components/tailark/header.tsx`
- **Layout**: Sticky navigation bar with logo, links, and auth buttons.
- **Aesthetics**: Clean, glassmorphism effect on scroll.
- **Simplicity**: High.
- **Recommended**: Yes, essential for all pages.

## Feature Sections

### `Features` (Simple Cards)
- **File**: `src/components/tailark/features-1.tsx`
- **Layout**: 3-column grid of cards with icons.
- **Aesthetics**: Minimalist, clean.
- **Simplicity**: High.
- **Recommended**: Yes, for secondary feature lists.

### `FeaturesSection` (Dashboard UI)
- **File**: `src/components/tailark/features-8.tsx`
- **Layout**: Complex bento grid mixing text, SVG charts, and illustrations.
- **Aesthetics**: Tech-focused, sophisticated, "Stripe-like" quality.
- **Simplicity**: Low (Complex SVG paths).
- **Recommended**: Yes, for showcasing product capabilities in depth.

### `FeaturesSection` (Interactive Map & Feed)
- **File**: `src/components/tailark/features-9.tsx`
- **Layout**: Split view with Real-time Map, Chat UI, and Activity Feed.
- **Aesthetics**: Data-heavy, dynamic, trustworthy.
- **Simplicity**: Low (External deps: `dotted-map`, `recharts`).
- **Recommended**: Yes, for SaaS/Analytics products.

### `Features` (Interactive Accordion)
- **File**: `src/components/tailark/features-12.tsx`
- **Layout**: Left Accordion, Right Dynamic Image (switches on selection).
- **Aesthetics**: Interactive, engaging, great for explaining workflows.
- **Simplicity**: Moderate (Uses `motion/react`).
- **Recommended**: Yes, for "How it works" sections.

## Social Proof

### `WallOfLoveSection` (Testimonials)
- **File**: `src/components/tailark/testimonials.tsx`
- **Layout**: Masonry grid (multi-column) of testimonial cards.
- **Aesthetics**: Community-focused, abundant.
- **Simplicity**: Moderate (Chunking logic).
- **Recommended**: Yes, for building trust.

### `LogoCloud`
- **File**: `src/components/tailark/logo-cloud.tsx`
- **Layout**: Infinite horizontal slider of partner logos.
- **Aesthetics**: Dynamic, subtle motion.
- **Simplicity**: High.
- **Recommended**: Yes, place below Hero or Pricing.

## Pricing

### `Pricing`
- **File**: `src/components/tailark/pricing.tsx`
- **Layout**: Split view (Price/CTA on left, Features/Customers on right).
- **Aesthetics**: Bold, conversion-focused.
- **Simplicity**: Moderate.
- **Recommended**: Yes, for simple SaaS pricing.

### `PricingComparator`
- **File**: `src/components/tailark/pricing-comparator.tsx`
- **Layout**: Full comparison table (Free vs Pro vs Startup).
- **Aesthetics**: Detailed, clear.
- **Simplicity**: Moderate.
- **Recommended**: Yes, for complex plans.

## Content & Support

### `ContentSection`
- **File**: `src/components/tailark/content-2.tsx`
- **Layout**: Text on left, masked image on right (overlap).
- **Aesthetics**: Editorial, narrative.
- **Simplicity**: High.
- **Recommended**: Yes, for telling the product story.

### `FAQs`
- **File**: `src/components/tailark/faqs.tsx`
- **Layout**: Two columns (Heading left, Questions right).
- **Aesthetics**: Clean, scannable.
- **Simplicity**: High.
- **Recommended**: Yes, for reducing support queries.

## Integrations

### `IntegrationsSection` (Grid)
- **File**: `src/components/tailark/integrations-1.tsx`
- **Layout**: Grid of cards (Icon + Title + Desc + Learn More).
- **Aesthetics**: Standard directory look.
- **Simplicity**: High.
- **Recommended**: Yes, for an "Integrations" page.

### `IntegrationsSection` (List)
- **File**: `src/components/tailark/integrations-6.tsx`
- **Layout**: Vertical list with "Add" button.
- **Aesthetics**: Compact, action-oriented.
- **Simplicity**: High.
- **Recommended**: Yes, for dense lists.

## Company & Contact

### `TeamSection`
- **File**: `src/components/tailark/team.tsx`
- **Layout**: Grid of photos with hover-reveal details.
- **Aesthetics**: Personal, human.
- **Simplicity**: High.
- **Recommended**: Yes, for "About" pages.

### `StatsSection`
- **File**: `src/components/tailark/stats.tsx`
- **Layout**: 3-column bold numbers.
- **Aesthetics**: Loud, authoritative.
- **Simplicity**: Very High.
- **Recommended**: Yes, combine with Social Proof.

### `ContactSection`
- **File**: `src/components/tailark/contact.tsx`
- **Layout**: Split (Contact Info left, Form right).
- **Aesthetics**: Functional, professional.
- **Simplicity**: Moderate.
- **Recommended**: Yes, for "Contact Us" page.

### `CallToAction`
- **File**: `src/components/tailark/call-to-action.tsx`
- **Layout**: Centered text + Email input field.
- **Aesthetics**: Direct, minimal.
- **Simplicity**: Very High.
- **Recommended**: Yes, for bottom of pages.

## Layout Components

### `Footer`
- **File**: `src/components/tailark/footer.tsx`
- **Layout**: 4-column links + Newsletter + Copyright.
- **Aesthetics**: Comprehensive, organized.
- **Simplicity**: High.
- **Recommended**: Yes, essential.

## File Index

| Filename | Role | Recommendation |
| :--- | :--- | :--- |
| `call-to-action.tsx` | CTA | ✅ Recommended |
| `contact.tsx` | Contact | ✅ Recommended |
| `content-2.tsx` | Content | ✅ Recommended |
| `content-3.tsx` | Content | ⚠️ Alternative |
| `content-4.tsx` | Content | ⚠️ Alternative |
| `content-5.tsx` | Content | ⚠️ Alternative |
| `content-6.tsx` | Content | ⚠️ Alternative |
| `content-7.tsx` | Content | ⚠️ Alternative |
| `faqs.tsx` | FAQ | ✅ Recommended |
| `faqs-2.tsx` | FAQ | ⚠️ Alternative |
| `faqs-3.tsx` | FAQ | ⚠️ Alternative |
| `faqs-4.tsx` | FAQ | ⚠️ Alternative |
| `features-1.tsx` | Features | ✅ Recommended (Simple) |
| `features-8.tsx` | Features | ✅ Recommended (Dashboard) |
| `features-9.tsx` | Features | ✅ Recommended (Map/Feed) |
| `features-12.tsx` | Features | ✅ Recommended (Accordion) |
| `features-2.tsx` | Features | ⚠️ Alternative |
| `features-3.tsx` | Features | ⚠️ Alternative |
| `features-4.tsx` | Features | ⚠️ Alternative |
| `features-5.tsx` | Features | ⚠️ Alternative |
| `features-6.tsx` | Features | ⚠️ Alternative |
| `features-7.tsx` | Features | ⚠️ Alternative |
| `features-10.tsx` | Features | ⚠️ Alternative |
| `features-11.tsx` | Features | ⚠️ Alternative |
| `footer.tsx` | Layout | ✅ Recommended |
| `forgot-password.tsx` | Auth | ❌ Use `auth-handler` |
| `header.tsx` | Layout | ✅ Recommended |
| `hero-section.tsx` | Hero | ✅ Recommended |
| `infinite-slider.tsx` | UI | Internal utility |
| `integrations-1.tsx` | Integrations | ✅ Recommended (Grid) |
| `integrations-6.tsx` | Integrations | ✅ Recommended (List) |
| `integrations-2.tsx` | Integrations | ⚠️ Alternative |
| `integrations-3.tsx` | Integrations | ⚠️ Alternative |
| `integrations-4.tsx` | Integrations | ⚠️ Alternative |
| `integrations-5.tsx` | Integrations | ⚠️ Alternative |
| `integrations-7.tsx` | Integrations | ⚠️ Alternative |
| `integrations-8.tsx` | Integrations | ⚠️ Alternative |
| `login.tsx` | Auth | ❌ Use `auth-handler` |
| `logo-cloud.tsx` | Social Proof | ✅ Recommended |
| `logo.tsx` | Brand | Internal utility |
| `pricing.tsx` | Pricing | ✅ Recommended |
| `pricing-comparator.tsx` | Pricing | ✅ Recommended (Table) |
| `sign-up.tsx` | Auth | ❌ Use `auth-handler` |
| `stats.tsx` | Stats | ✅ Recommended |
| `stats-2.tsx` | Stats | ⚠️ Alternative |
| `stats-3.tsx` | Stats | ⚠️ Alternative |
| `stats-4.tsx` | Stats | ⚠️ Alternative |
| `team.tsx` | About | ✅ Recommended |
| `testimonials.tsx` | Social Proof | ✅ Recommended |
