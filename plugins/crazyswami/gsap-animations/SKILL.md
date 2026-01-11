---
name: gsap-animations
description: GSAP animation best practices for web design - scroll triggers, performance optimization, accessibility, responsive animations, and testing integration. Use when implementing or reviewing animations on WordPress or any web project.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# GSAP Animation Best Practices

Comprehensive guide for implementing professional, accessible, and performant animations using GSAP (GreenSock Animation Platform).

## Core Principles

### 1. Performance First
- Animate `transform` and `opacity` only (GPU-accelerated)
- Avoid animating `width`, `height`, `top`, `left`, `margin`, `padding`
- Use `will-change` sparingly
- Target 60fps on all devices

### 2. Accessibility Always
- Respect `prefers-reduced-motion`
- Ensure content is visible without JavaScript
- Don't hide critical content behind animations
- Provide skip/pause controls for long animations

### 3. Progressive Enhancement
- Content must work without animations
- Animations enhance, not replace, functionality
- Test with animations disabled

---

## GSAP Setup

### Installation

```html
<!-- CDN (recommended for WordPress) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>

<!-- Optional plugins -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollSmoother.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/SplitText.min.js"></script>
```

### WordPress Enqueue

```php
function theme_enqueue_gsap() {
    // GSAP Core
    wp_enqueue_script(
        'gsap',
        'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js',
        array(),
        '3.12.5',
        true
    );

    // ScrollTrigger
    wp_enqueue_script(
        'gsap-scrolltrigger',
        'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js',
        array('gsap'),
        '3.12.5',
        true
    );

    // Theme animations
    wp_enqueue_script(
        'theme-animations',
        get_theme_file_uri('/assets/js/animations.js'),
        array('gsap', 'gsap-scrolltrigger'),
        filemtime(get_theme_file_path('/assets/js/animations.js')),
        true
    );
}
add_action('wp_enqueue_scripts', 'theme_enqueue_gsap');
```

---

## Animation Patterns

### 1. Fade In on Scroll

```javascript
// Basic fade in
gsap.from('.fade-in', {
    opacity: 0,
    y: 50,
    duration: 1,
    stagger: 0.2,
    scrollTrigger: {
        trigger: '.fade-in',
        start: 'top 80%',
        toggleActions: 'play none none none'
    }
});
```

### 2. Staggered Elements

```javascript
// Cards appearing one by one
gsap.from('.card', {
    opacity: 0,
    y: 100,
    duration: 0.8,
    stagger: {
        amount: 0.6,
        from: 'start'
    },
    ease: 'power2.out',
    scrollTrigger: {
        trigger: '.cards-container',
        start: 'top 75%'
    }
});
```

### 3. Parallax Effect

```javascript
// Subtle parallax on images
gsap.to('.parallax-image', {
    yPercent: -20,
    ease: 'none',
    scrollTrigger: {
        trigger: '.parallax-section',
        start: 'top bottom',
        end: 'bottom top',
        scrub: true
    }
});
```

### 4. Text Reveal (Line by Line)

```javascript
// Requires SplitText plugin (Club GreenSock)
// Or use CSS-based alternative below

// CSS Alternative - wrap each line in a span
gsap.from('.reveal-line', {
    opacity: 0,
    y: '100%',
    duration: 0.8,
    stagger: 0.1,
    ease: 'power3.out',
    scrollTrigger: {
        trigger: '.text-reveal',
        start: 'top 80%'
    }
});
```

### 5. Curtain/Mask Reveal

```javascript
// Image revealed by sliding mask
gsap.to('.curtain-mask', {
    scaleX: 0,
    transformOrigin: 'right center',
    duration: 1.2,
    ease: 'power4.inOut',
    scrollTrigger: {
        trigger: '.curtain-container',
        start: 'top 70%'
    }
});
```

### 6. Hero Animation Timeline

```javascript
// Complex hero sequence
const heroTL = gsap.timeline({
    defaults: { ease: 'power3.out' }
});

heroTL
    .from('.hero-bg', { scale: 1.2, duration: 1.5 })
    .from('.hero-title', { opacity: 0, y: 100, duration: 1 }, '-=1')
    .from('.hero-subtitle', { opacity: 0, y: 50, duration: 0.8 }, '-=0.5')
    .from('.hero-cta', { opacity: 0, y: 30, duration: 0.6 }, '-=0.3');
```

---

## Accessibility

### Respect Reduced Motion

```javascript
// Check user preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Option 1: Disable all animations
if (prefersReducedMotion) {
    gsap.globalTimeline.timeScale(0);
    ScrollTrigger.getAll().forEach(st => st.kill());
}

// Option 2: Simplified animations
const animationConfig = prefersReducedMotion
    ? { duration: 0, stagger: 0 }
    : { duration: 1, stagger: 0.2 };

gsap.from('.element', {
    opacity: 0,
    y: prefersReducedMotion ? 0 : 50,
    ...animationConfig
});
```

### CSS Fallback

```css
/* Ensure content visible without JS */
.fade-in {
    opacity: 1;
    transform: translateY(0);
}

/* Only hide if animations will run */
.js .fade-in {
    opacity: 0;
    transform: translateY(50px);
}

/* Respect reduced motion in CSS too */
@media (prefers-reduced-motion: reduce) {
    .js .fade-in {
        opacity: 1;
        transform: none;
    }
}
```

### Add JS Class to HTML

```javascript
// Add at start of script
document.documentElement.classList.add('js');
```

---

## Responsive Animations

### Breakpoint-Aware Animations

```javascript
// Create responsive animations
const mm = gsap.matchMedia();

mm.add('(min-width: 1024px)', () => {
    // Desktop animations
    gsap.from('.hero-image', {
        x: 100,
        opacity: 0,
        duration: 1.2
    });

    return () => {
        // Cleanup on breakpoint change
    };
});

mm.add('(max-width: 1023px)', () => {
    // Mobile animations (simpler)
    gsap.from('.hero-image', {
        opacity: 0,
        duration: 0.8
    });
});
```

### Refresh on Resize

```javascript
// Recalculate ScrollTrigger on resize
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        ScrollTrigger.refresh();
    }, 250);
});
```

---

## Performance Optimization

### 1. Use Transform Properties Only

```javascript
// GOOD - GPU accelerated
gsap.to('.element', {
    x: 100,          // transform: translateX
    y: 50,           // transform: translateY
    rotation: 45,    // transform: rotate
    scale: 1.2,      // transform: scale
    opacity: 0.5
});

// BAD - Causes layout/paint
gsap.to('.element', {
    left: 100,       // Triggers layout
    width: '200px',  // Triggers layout
    marginTop: 50    // Triggers layout
});
```

### 2. Batch Similar Animations

```javascript
// Use batch for many similar elements
ScrollTrigger.batch('.card', {
    onEnter: batch => gsap.to(batch, {
        opacity: 1,
        y: 0,
        stagger: 0.1
    }),
    start: 'top 85%'
});
```

### 3. Kill Unused ScrollTriggers

```javascript
// Cleanup when navigating (SPA) or component unmount
function cleanup() {
    ScrollTrigger.getAll().forEach(st => st.kill());
    gsap.killTweensOf('*');
}
```

### 4. Lazy Initialize

```javascript
// Only initialize animations for visible sections
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            initSectionAnimations(entry.target);
            observer.unobserve(entry.target);
        }
    });
}, { rootMargin: '100px' });

document.querySelectorAll('.animated-section').forEach(section => {
    observer.observe(section);
});
```

---

## ScrollTrigger Best Practices

### 1. Proper Start/End Points

```javascript
// Avoid common mistakes
ScrollTrigger.create({
    trigger: '.section',
    start: 'top 80%',    // When top of trigger hits 80% from top of viewport
    end: 'bottom 20%',   // When bottom of trigger hits 20% from top
    markers: true,       // Debug only - remove in production!
});
```

### 2. Pin Sections Carefully

```javascript
// Pinning can cause layout issues
ScrollTrigger.create({
    trigger: '.pinned-section',
    start: 'top top',
    end: '+=100%',
    pin: true,
    pinSpacing: true,    // Usually want this true
    anticipatePin: 1     // Helps with mobile
});
```

### 3. Handle Images Loading

```javascript
// Wait for images before calculating positions
ScrollTrigger.config({
    ignoreMobileResize: true
});

window.addEventListener('load', () => {
    ScrollTrigger.refresh();
});

// Or refresh after lazy images load
document.querySelectorAll('img[loading="lazy"]').forEach(img => {
    img.addEventListener('load', () => ScrollTrigger.refresh());
});
```

---

## Testing Integration

### Visual QA Compatibility

For the visual-qa skill to capture animations correctly:

```javascript
// Expose function to complete all animations instantly
window.completeAllAnimations = function() {
    gsap.globalTimeline.progress(1);
    ScrollTrigger.getAll().forEach(st => {
        st.scroll(st.end);
    });
};

// Or skip animations entirely for screenshots
if (window.location.search.includes('skip-animations')) {
    gsap.globalTimeline.timeScale(100);
}
```

### Playwright Testing

```javascript
// In Playwright test
await page.evaluate(() => {
    if (window.completeAllAnimations) {
        window.completeAllAnimations();
    }
});
await page.waitForTimeout(500);
await page.screenshot({ path: 'screenshot.png', fullPage: true });
```

---

## Common Animation Library

### Reusable Animation Classes

```javascript
// animations.js - Reusable animation library

const Animations = {
    // Initialize all animations
    init() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return;
        }

        this.fadeIn();
        this.slideIn();
        this.parallax();
        this.textReveal();
    },

    fadeIn() {
        gsap.utils.toArray('[data-animate="fade-in"]').forEach(el => {
            gsap.from(el, {
                opacity: 0,
                y: 50,
                duration: 0.8,
                scrollTrigger: {
                    trigger: el,
                    start: 'top 85%',
                    once: true
                }
            });
        });
    },

    slideIn() {
        gsap.utils.toArray('[data-animate="slide-left"]').forEach(el => {
            gsap.from(el, {
                opacity: 0,
                x: -100,
                duration: 1,
                scrollTrigger: {
                    trigger: el,
                    start: 'top 80%',
                    once: true
                }
            });
        });

        gsap.utils.toArray('[data-animate="slide-right"]').forEach(el => {
            gsap.from(el, {
                opacity: 0,
                x: 100,
                duration: 1,
                scrollTrigger: {
                    trigger: el,
                    start: 'top 80%',
                    once: true
                }
            });
        });
    },

    parallax() {
        gsap.utils.toArray('[data-parallax]').forEach(el => {
            const speed = el.dataset.parallax || 0.2;
            gsap.to(el, {
                yPercent: -100 * speed,
                ease: 'none',
                scrollTrigger: {
                    trigger: el.parentElement,
                    start: 'top bottom',
                    end: 'bottom top',
                    scrub: true
                }
            });
        });
    },

    textReveal() {
        gsap.utils.toArray('[data-animate="text-reveal"]').forEach(el => {
            const lines = el.querySelectorAll('.line');
            gsap.from(lines, {
                opacity: 0,
                y: '100%',
                duration: 0.8,
                stagger: 0.1,
                scrollTrigger: {
                    trigger: el,
                    start: 'top 80%',
                    once: true
                }
            });
        });
    },

    // Refresh after dynamic content
    refresh() {
        ScrollTrigger.refresh();
    },

    // Cleanup for SPA navigation
    destroy() {
        ScrollTrigger.getAll().forEach(st => st.kill());
        gsap.killTweensOf('*');
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => Animations.init());
```

### HTML Usage

```html
<!-- Fade in -->
<div data-animate="fade-in">Content</div>

<!-- Slide from left -->
<div data-animate="slide-left">Content</div>

<!-- Parallax (0.2 = 20% speed) -->
<img data-parallax="0.3" src="image.jpg">

<!-- Text reveal (requires line wrapping) -->
<div data-animate="text-reveal">
    <div class="line">First line</div>
    <div class="line">Second line</div>
</div>
```

---

## Debugging

### Enable Markers

```javascript
ScrollTrigger.defaults({
    markers: true  // Shows start/end markers
});
```

### Log Animation Events

```javascript
gsap.to('.element', {
    x: 100,
    onStart: () => console.log('Animation started'),
    onComplete: () => console.log('Animation completed'),
    onUpdate: self => console.log('Progress:', self.progress())
});
```

### Check for Issues

```javascript
// List all ScrollTriggers
console.log('ScrollTriggers:', ScrollTrigger.getAll());

// Check if element exists
const el = document.querySelector('.animated-element');
if (!el) console.warn('Animation target not found!');
```

---

## Checklist

### Before Launch

- [ ] Remove all `markers: true`
- [ ] Test with `prefers-reduced-motion: reduce`
- [ ] Test on mobile devices (real devices, not just DevTools)
- [ ] Check performance in DevTools Performance tab
- [ ] Verify 60fps on target devices
- [ ] Content visible without JavaScript
- [ ] Images lazy-loaded before ScrollTrigger refresh
- [ ] No layout thrashing (avoid animating layout properties)

### Visual QA Integration

- [ ] Animations complete before screenshots
- [ ] Full-page scroll triggers all animations
- [ ] Screenshots capture final animated state
- [ ] Test at all viewport sizes

---

## Resources

- [GSAP Documentation](https://greensock.com/docs/)
- [ScrollTrigger Documentation](https://greensock.com/docs/v3/Plugins/ScrollTrigger)
- [GSAP Cheat Sheet](https://greensock.com/cheatsheet/)
- [GreenSock Forums](https://greensock.com/forums/)
- [Reduced Motion Best Practices](https://web.dev/prefers-reduced-motion/)
