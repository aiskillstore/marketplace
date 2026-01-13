# WordPress Coding Standards

Comprehensive guide to PHP, JavaScript, and CSS coding standards for WordPress development.

## PHP Coding Standards

### File Headers

Every PHP file should include a file header:

```php
<?php
/**
 * Template Name: About Page
 *
 * Description of what this file does.
 *
 * @package Theme_Name
 * @since 1.0.0
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}
```

### Naming Conventions

#### Functions

```php
// Theme functions: prefix with theme name
function theme_name_get_featured_posts() { }
function theme_name_setup() { }

// Plugin functions: prefix with plugin name
function my_plugin_activate() { }
function my_plugin_settings_page() { }
```

#### Classes

```php
// Use PascalCase with prefix
class Theme_Name_Walker_Nav extends Walker_Nav_Menu { }
class My_Plugin_Admin { }

// Namespaces (PHP 5.6+)
namespace Theme_Name\Includes;

class Custom_Post_Types { }
```

#### Constants

```php
// All uppercase with underscores
define('THEME_NAME_VERSION', '1.0.0');
define('MY_PLUGIN_PATH', plugin_dir_path(__FILE__));
```

#### Variables

```php
// Lowercase with underscores (snake_case)
$featured_posts = get_posts($args);
$user_meta = get_user_meta($user_id);
```

#### Hooks (Actions & Filters)

```php
// Prefix with theme/plugin name
add_action('theme_name_after_header', 'theme_name_breadcrumbs');
add_filter('theme_name_excerpt_length', 'my_custom_length');
```

### Formatting

#### Indentation

Use **tabs**, not spaces. One tab per indent level.

```php
function theme_name_example() {
	if ($condition) {
		// One tab indent
		foreach ($items as $item) {
			// Two tabs
			echo esc_html($item);
		}
	}
}
```

#### Braces

Opening brace on same line:

```php
// Correct
if ($condition) {
	// code
}

// Wrong
if ($condition)
{
	// code
}
```

#### Spacing

```php
// Space after control structure keywords
if ($condition) { }
foreach ($array as $key => $value) { }
while ($condition) { }

// No space for function calls
my_function($arg1, $arg2);

// Space around operators
$result = $a + $b;
$name = $first . ' ' . $last;

// Space in arrays
$array = array('key' => 'value', 'another' => 'item');
$array = ['key' => 'value', 'another' => 'item'];
```

#### Line Length

Maximum 100-120 characters. Break long lines:

```php
// Break array definitions
$args = array(
	'post_type'      => 'property',
	'posts_per_page' => 10,
	'meta_query'     => array(
		array(
			'key'     => '_featured',
			'value'   => '1',
			'compare' => '=',
		),
	),
);

// Break long function calls
$result = some_long_function_name(
	$first_argument,
	$second_argument,
	$third_argument
);
```

### PHPDoc Comments

#### Functions

```php
/**
 * Get featured properties.
 *
 * Retrieves published properties marked as featured.
 *
 * @since 1.0.0
 *
 * @param int    $count   Number of properties to retrieve. Default 6.
 * @param string $orderby How to order results. Default 'date'.
 *
 * @return WP_Query Query object with featured properties.
 */
function theme_name_get_featured_properties($count = 6, $orderby = 'date') {
	$args = array(
		'post_type'      => 'property',
		'posts_per_page' => absint($count),
		'orderby'        => sanitize_key($orderby),
		'meta_key'       => '_featured',
		'meta_value'     => '1',
	);

	return new WP_Query($args);
}
```

#### Classes

```php
/**
 * Custom Post Type Manager.
 *
 * Handles registration and management of custom post types.
 *
 * @since 1.0.0
 */
class Theme_Name_CPT_Manager {

	/**
	 * Post type slug.
	 *
	 * @since 1.0.0
	 * @var string
	 */
	private $post_type = 'property';

	/**
	 * Constructor.
	 *
	 * @since 1.0.0
	 */
	public function __construct() {
		add_action('init', array($this, 'register'));
	}

	/**
	 * Register the custom post type.
	 *
	 * @since 1.0.0
	 *
	 * @return void
	 */
	public function register() {
		// Registration code
	}
}
```

### Yoda Conditions

Use Yoda conditions (constant on left) for comparisons:

```php
// Correct - prevents accidental assignment
if ('publish' === $post_status) { }
if (true === $is_active) { }
if (null === $value) { }

// Wrong
if ($post_status === 'publish') { }
```

---

## JavaScript Coding Standards

### File Structure

```javascript
/**
 * Theme main JavaScript.
 *
 * @package Theme_Name
 * @since 1.0.0
 */

(function($) {
	'use strict';

	// DOM Ready
	$(function() {
		// Initialize components
		initNavigation();
		initAnimations();
	});

	/**
	 * Initialize mobile navigation.
	 */
	function initNavigation() {
		const menuButton = $('.menu-toggle');
		const menuOverlay = $('.menu-overlay');

		menuButton.on('click', function() {
			menuOverlay.toggleClass('open');
		});
	}

	/**
	 * Initialize scroll animations.
	 */
	function initAnimations() {
		// GSAP animations
		gsap.from('.hero-text', {
			opacity: 0,
			y: 50,
			duration: 1,
		});
	}

})(jQuery);
```

### Naming Conventions

```javascript
// camelCase for variables and functions
const featuredPosts = [];
function getFeaturedPosts() { }

// PascalCase for classes/constructors
class NavigationHandler { }

// UPPER_SNAKE_CASE for constants
const API_ENDPOINT = '/wp-json/wp/v2/';
const MAX_ITEMS = 10;
```

### Modern JavaScript (ES6+)

Prefer modern syntax when browser support allows:

```javascript
// Use const/let instead of var
const items = ['a', 'b', 'c'];
let count = 0;

// Arrow functions for callbacks
items.forEach((item) => {
	console.log(item);
});

// Template literals
const message = `Hello, ${userName}!`;

// Destructuring
const { title, content } = post;
const [first, second] = items;

// Spread operator
const allPosts = [...featuredPosts, ...regularPosts];

// Async/await for AJAX
async function fetchPosts() {
	try {
		const response = await fetch(apiUrl);
		const data = await response.json();
		return data;
	} catch (error) {
		console.error('Error fetching posts:', error);
	}
}
```

### jQuery Best Practices

```javascript
// Cache jQuery selectors
const $menu = $('.main-menu');
const $menuItems = $menu.find('.menu-item');

// Use event delegation for dynamic elements
$(document).on('click', '.dynamic-button', function(e) {
	e.preventDefault();
	// Handle click
});

// Chain methods
$('.element')
	.addClass('active')
	.fadeIn(300)
	.css('color', 'blue');
```

---

## CSS/SCSS Coding Standards

### File Organization

```
assets/
├── scss/
│   ├── _variables.scss      # Colors, fonts, breakpoints
│   ├── _mixins.scss         # Reusable mixins
│   ├── _base.scss           # Reset, typography
│   ├── _layout.scss         # Grid, containers
│   ├── _components.scss     # Buttons, cards, forms
│   ├── _header.scss         # Header styles
│   ├── _footer.scss         # Footer styles
│   └── style.scss           # Main file (imports all)
└── css/
    └── style.css            # Compiled CSS
```

### Naming Convention (BEM)

Use Block-Element-Modifier naming:

```css
/* Block */
.card { }

/* Block__Element */
.card__title { }
.card__image { }
.card__content { }

/* Block--Modifier */
.card--featured { }
.card--horizontal { }

/* Element with Modifier */
.card__title--large { }
```

### Property Order

Group related properties:

```css
.element {
	/* Positioning */
	position: relative;
	top: 0;
	left: 0;
	z-index: 10;

	/* Display & Box Model */
	display: flex;
	flex-direction: column;
	width: 100%;
	padding: 1rem;
	margin: 0 auto;

	/* Typography */
	font-family: var(--font-body);
	font-size: 1rem;
	line-height: 1.5;
	color: var(--color-text);

	/* Visual */
	background-color: var(--color-bg);
	border: 1px solid var(--color-border);
	border-radius: 4px;

	/* Animation */
	transition: all 0.3s ease;
}
```

### CSS Variables

Use CSS custom properties for theming:

```css
:root {
	/* Colors */
	--color-primary: #1a1a1a;
	--color-secondary: #666666;
	--color-accent: #007bff;
	--color-bg: #ffffff;
	--color-text: #333333;

	/* Typography */
	--font-heading: 'Playfair Display', serif;
	--font-body: 'Inter', sans-serif;

	/* Spacing */
	--spacing-xs: 0.5rem;
	--spacing-sm: 1rem;
	--spacing-md: 2rem;
	--spacing-lg: 4rem;

	/* Breakpoints (for reference, use in media queries) */
	--breakpoint-sm: 576px;
	--breakpoint-md: 768px;
	--breakpoint-lg: 1024px;
	--breakpoint-xl: 1440px;
}
```

### Responsive Design

Mobile-first approach with min-width breakpoints:

```scss
// Variables
$breakpoints: (
	'sm': 576px,
	'md': 768px,
	'lg': 1024px,
	'xl': 1440px,
);

// Mixin
@mixin respond-to($breakpoint) {
	@if map-has-key($breakpoints, $breakpoint) {
		@media (min-width: map-get($breakpoints, $breakpoint)) {
			@content;
		}
	}
}

// Usage
.container {
	padding: 1rem;

	@include respond-to('md') {
		padding: 2rem;
	}

	@include respond-to('lg') {
		padding: 4rem;
		max-width: 1200px;
	}
}
```

---

## File Organization

### Theme Structure

```
theme-name/
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fonts/
├── inc/
│   ├── custom-post-types.php
│   ├── taxonomies.php
│   ├── customizer.php
│   ├── template-functions.php
│   └── template-tags.php
├── template-parts/
│   ├── content/
│   ├── header/
│   └── footer/
├── templates/
│   └── page-templates/
├── functions.php
├── index.php
├── style.css
└── screenshot.png
```

### Plugin Structure

```
plugin-name/
├── assets/
│   ├── css/
│   └── js/
├── includes/
│   ├── class-plugin-name.php
│   ├── class-plugin-name-admin.php
│   └── class-plugin-name-public.php
├── admin/
│   ├── partials/
│   └── css/
├── public/
│   ├── partials/
│   └── css/
├── languages/
├── plugin-name.php
└── uninstall.php
```

---

## Linting Tools

### PHP_CodeSniffer (PHPCS)

```bash
# Install WordPress standards
composer require --dev wp-coding-standards/wpcs

# Configure
./vendor/bin/phpcs --config-set installed_paths vendor/wp-coding-standards/wpcs

# Check code
./vendor/bin/phpcs --standard=WordPress path/to/file.php

# Auto-fix
./vendor/bin/phpcbf --standard=WordPress path/to/file.php
```

### ESLint

```json
// .eslintrc.json
{
  "extends": ["eslint:recommended", "plugin:@wordpress/recommended"],
  "env": {
    "browser": true,
    "jquery": true
  },
  "globals": {
    "wp": "readonly",
    "gsap": "readonly"
  }
}
```

### Stylelint

```json
// .stylelintrc.json
{
  "extends": ["stylelint-config-wordpress"]
}
```

---

## Resources

- [WordPress PHP Coding Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/php/)
- [WordPress JavaScript Coding Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/javascript/)
- [WordPress CSS Coding Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/css/)
- [WPCS GitHub Repository](https://github.com/WordPress/WordPress-Coding-Standards)
