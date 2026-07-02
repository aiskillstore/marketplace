# Cookbook — Pattern Library

Standalone HTML patterns for vanilla web development. Each file is self-contained with embedded CSS — open in a browser, copy into your project, customize with tokens.

## Categories

### Layouts
| Pattern | Technique | When to use |
|---------|-----------|-------------|
| [Responsive Grid](layouts/responsive-grid/) | `repeat(auto-fit, minmax())` | Card grids, galleries — no media queries needed |
| [Sidebar Layout](layouts/sidebar-layout/) | Flexbox | Dashboard, docs, settings pages |
| [Hero Section](layouts/hero-section/) | Flexbox/Grid | Landing pages, above-the-fold |
| [Holy Grail](layouts/holy-grail/) | CSS Grid | Classic header/sidebar/main/footer |
| [Dashboard](layouts/dashboard/) | `grid-template-areas` | App layouts with named regions |
| [Masonry](layouts/masonry/) | `grid-template-rows: masonry` | Pinterest-style, photo galleries |

### Navigation
| Pattern | Technique | When to use |
|---------|-----------|-------------|
| [Navbar](navigation/navbar/) | Flexbox + `margin: auto` | Primary site navigation |
| [Sidebar Menu](navigation/sidebar-menu/) | CSS Grid + transitions | Dashboard sidebar with dropdowns |
| [Mobile Hamburger](navigation/mobile-hamburger/) | ARIA + JS toggle | Responsive mobile menu |
| [Sticky Header](navigation/sticky-header/) | `position: sticky` | Header that scrolls with content |
| [Breadcrumbs](navigation/breadcrumbs/) | Semantic `<nav>` + `aria-label` | Hierarchical navigation |

### Forms
| Pattern | Technique | When to use |
|---------|-----------|-------------|
| [Login/Signup](forms/login-signup/) | Validation + responsive | Auth pages |
| [Form Validation](forms/form-validation/) | Front-end validation | Any form with validation |
| [Search Bar](forms/search-bar/) | Input + icon | Site search |
| [Contact Form](forms/contact-form/) | Multi-field layout | Contact/about pages |
| [Multi-Step](forms/multi-step/) | State management | Wizards, onboarding |

### Cards
| Pattern | Technique | When to use |
|---------|-----------|-------------|
| [Profile Card](cards/profile-card/) | Flexbox/Grid | User profiles, team pages |
| [Product Card](cards/product-card/) | Container queries | E-commerce, catalogs |
| [Article Card](cards/article-card/) | Grid + `margin-top: auto` | Blog feeds, news |
| [Pricing Card](cards/pricing-card/) | Flex column | Pricing pages |

### Effects
| Pattern | Technique | When to use |
|---------|-----------|-------------|
| [Glassmorphism](effects/glassmorphism/) | `backdrop-filter: blur()` | Over images/gradients |
| [Neumorphism](effects/neumorphism/) | Dual box-shadows | Soft UI, toggle buttons |
| [Gradient Text](effects/gradient-text/) | `background-clip: text` | Headings, hero text |
| [Border Animations](effects/border-animations/) | `@property` + conic-gradient | Cards, buttons, focus states |
| [Hover Effects](effects/hover-effects/) | Transform + transition | Interactive elements |
| [Scroll Snap](effects/scroll-snap/) | `scroll-snap-type` | Carousels, sliders |
| [Scroll-Driven Animations](effects/scroll-driven-animations/) | `animation-timeline: view()` | Reveal on scroll |
| [Animated Tooltips](effects/animated-tooltips/) | `::before/::after` + `attr()` | Tooltips, labels |
| [Triangles](effects/triangles/) | Border trick | Dropdowns, speech bubbles |

### Interactivity
| Pattern | Technique | When to use |
|---------|-----------|-------------|
| [Dark Mode](interactivity/dark-mode/) | CSS vars + localStorage | Theme switching |
| [Todo App](interactivity/todo-app/) | localStorage CRUD | Task management |
| [Modal Dialog](interactivity/modal-dialog/) | `<dialog>` element | Confirmations, forms |
| [Accordion](interactivity/accordion/) | `<details>/<summary>` | FAQs, collapsible sections |
| [Carousel](interactivity/carousel/) | Scroll-snap + `::scroll-button` | Image/content carousels |
| [Tabs](interactivity/tabs/) | `:checked` pseudo-class | Tabbed interfaces |
| [Toast Notifications](interactivity/toast-notifications/) | JS + CSS transitions | Feedback, alerts |
| [Popover API](interactivity/popover-api/) | HTML `popover` attribute | Dropdowns, tooltips |
| [CSS-Only Dropdown](interactivity/css-only-dropdown/) | `:focus/:focus-within` | Simple menus |

### Typography
| Pattern | Technique | When to use |
|---------|-----------|-------------|
| [Fluid Type](typography/fluid-type/) | `clamp()` | Responsive headings/body |
| [Text Balance](typography/text-balance/) | `text-wrap: balance` | Headings, short text |
| [Decorative Headings](typography/decorative-headings/) | Gradient, `writing-mode` | Hero sections, emphasis |
| [Vertical Rhythm](typography/vertical-rhythm/) | Consistent spacing baseline | Content-heavy pages |
