# WordPress Hooks and Filters

Complete reference for WordPress actions and filters with practical examples.

## Understanding Hooks

WordPress hooks are integration points that allow you to run custom code at specific times or modify data as it passes through the system.

### Actions vs Filters

| Type | Purpose | Return Value |
|------|---------|--------------|
| **Actions** | Execute code at specific points | None (void) |
| **Filters** | Modify data before it's used | Modified value |

```php
// Action: DO something
add_action('init', 'my_init_function');
function my_init_function() {
	// Register post types, taxonomies, etc.
}

// Filter: MODIFY something
add_filter('the_title', 'my_title_filter');
function my_title_filter($title) {
	return $title . ' - Modified';  // Must return value
}
```

## Common Actions

### Initialization Hooks

```php
/**
 * plugins_loaded - After all plugins are loaded
 * Use for: Plugin initialization, dependency checks
 */
add_action('plugins_loaded', 'my_plugin_init');
function my_plugin_init() {
	// Check for required plugins
	if (!class_exists('WooCommerce')) {
		add_action('admin_notices', 'my_woo_notice');
	}
}

/**
 * after_setup_theme - After theme is loaded
 * Use for: Theme features, image sizes, nav menus
 */
add_action('after_setup_theme', 'theme_setup');
function theme_setup() {
	add_theme_support('title-tag');
	add_theme_support('post-thumbnails');
	add_theme_support('html5', array('search-form', 'gallery', 'caption'));

	register_nav_menus(array(
		'primary' => __('Primary Menu', 'theme-name'),
		'footer'  => __('Footer Menu', 'theme-name'),
	));

	add_image_size('hero', 1920, 1080, true);
}

/**
 * init - After WordPress is fully loaded
 * Use for: Register CPTs, taxonomies, shortcodes
 */
add_action('init', 'register_custom_types');
function register_custom_types() {
	register_post_type('property', $args);
	register_taxonomy('property_type', 'property', $args);
}

/**
 * wp_loaded - After WordPress and plugins are loaded
 * Use for: Final initialization, redirect logic
 */
add_action('wp_loaded', 'handle_redirects');
function handle_redirects() {
	if (is_user_logged_in() && is_page('login')) {
		wp_redirect(home_url('/dashboard/'));
		exit;
	}
}
```

### Frontend Hooks

```php
/**
 * wp_enqueue_scripts - Enqueue frontend assets
 * Use for: CSS, JavaScript for frontend
 */
add_action('wp_enqueue_scripts', 'theme_assets');
function theme_assets() {
	wp_enqueue_style('theme-style', get_stylesheet_uri());
	wp_enqueue_script('theme-main', get_theme_file_uri('/assets/js/main.js'), array('jquery'), '1.0', true);
}

/**
 * wp_head - Inside <head> tag
 * Use for: Meta tags, inline styles, tracking codes
 */
add_action('wp_head', 'theme_head_meta');
function theme_head_meta() {
	echo '<meta name="theme-color" content="#1a1a1a">';
}

/**
 * wp_body_open - After opening <body> tag
 * Use for: Skip links, GTM noscript, overlays
 */
add_action('wp_body_open', 'theme_body_open');
function theme_body_open() {
	echo '<a class="skip-link" href="#main">Skip to content</a>';
}

/**
 * wp_footer - Before closing </body> tag
 * Use for: Modals, tracking scripts, footer scripts
 */
add_action('wp_footer', 'theme_footer');
function theme_footer() {
	get_template_part('template-parts/modal', 'menu');
}

/**
 * template_redirect - Before template is chosen
 * Use for: Custom redirects, access control
 */
add_action('template_redirect', 'protect_members_area');
function protect_members_area() {
	if (is_page('members') && !is_user_logged_in()) {
		wp_redirect(home_url('/login/'));
		exit;
	}
}
```

### Admin Hooks

```php
/**
 * admin_enqueue_scripts - Enqueue admin assets
 */
add_action('admin_enqueue_scripts', 'admin_assets');
function admin_assets($hook) {
	// Only load on specific admin pages
	if ('post.php' === $hook || 'post-new.php' === $hook) {
		wp_enqueue_style('admin-custom', get_theme_file_uri('/assets/css/admin.css'));
	}
}

/**
 * admin_menu - Add admin menu pages
 */
add_action('admin_menu', 'theme_admin_menu');
function theme_admin_menu() {
	add_menu_page(
		'Theme Settings',
		'Theme Settings',
		'manage_options',
		'theme-settings',
		'theme_settings_page',
		'dashicons-admin-generic',
		80
	);
}

/**
 * admin_init - Admin initialization
 * Use for: Register settings, process forms
 */
add_action('admin_init', 'theme_register_settings');
function theme_register_settings() {
	register_setting('theme_options', 'theme_settings');
}

/**
 * add_meta_boxes - Register meta boxes
 */
add_action('add_meta_boxes', 'property_meta_boxes');
function property_meta_boxes() {
	add_meta_box(
		'property_details',
		__('Property Details', 'theme-name'),
		'render_property_meta_box',
		'property',
		'normal',
		'high'
	);
}
```

### Post/Content Hooks

```php
/**
 * save_post - When a post is saved
 * Use for: Save meta data, trigger actions
 */
add_action('save_post', 'save_property_meta', 10, 3);
function save_property_meta($post_id, $post, $update) {
	// Skip autosaves
	if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
		return;
	}

	// Verify nonce
	if (!isset($_POST['property_nonce']) || !wp_verify_nonce($_POST['property_nonce'], 'save_property')) {
		return;
	}

	// Check permission
	if (!current_user_can('edit_post', $post_id)) {
		return;
	}

	// Save meta
	if (isset($_POST['property_price'])) {
		update_post_meta($post_id, '_property_price', absint($_POST['property_price']));
	}
}

/**
 * transition_post_status - When post status changes
 */
add_action('transition_post_status', 'on_property_publish', 10, 3);
function on_property_publish($new_status, $old_status, $post) {
	if ('publish' === $new_status && 'publish' !== $old_status && 'property' === $post->post_type) {
		// Send notification about new property
		theme_notify_new_property($post);
	}
}

/**
 * pre_get_posts - Modify main query
 */
add_action('pre_get_posts', 'modify_property_archive');
function modify_property_archive($query) {
	if (!is_admin() && $query->is_main_query() && is_post_type_archive('property')) {
		$query->set('posts_per_page', 12);
		$query->set('orderby', 'meta_value_num');
		$query->set('meta_key', '_property_price');
		$query->set('order', 'DESC');
	}
}
```

### User Hooks

```php
/**
 * user_register - When new user registers
 */
add_action('user_register', 'on_user_register');
function on_user_register($user_id) {
	// Set default meta
	update_user_meta($user_id, 'show_admin_bar_front', 'false');

	// Send custom welcome email
	theme_send_welcome_email($user_id);
}

/**
 * wp_login - When user logs in
 */
add_action('wp_login', 'on_user_login', 10, 2);
function on_user_login($user_login, $user) {
	// Update last login time
	update_user_meta($user->ID, 'last_login', current_time('mysql'));

	// Log login
	error_log(sprintf('User %s logged in at %s', $user_login, current_time('mysql')));
}

/**
 * wp_logout - When user logs out
 */
add_action('wp_logout', 'on_user_logout');
function on_user_logout($user_id) {
	// Clear user-specific transients
	delete_transient('user_dashboard_' . $user_id);
}
```

## Common Filters

### Content Filters

```php
/**
 * the_title - Modify post title
 */
add_filter('the_title', 'modify_property_title', 10, 2);
function modify_property_title($title, $post_id) {
	if ('property' === get_post_type($post_id)) {
		$status = get_post_meta($post_id, '_property_status', true);
		if ('sold' === $status) {
			$title = '[SOLD] ' . $title;
		}
	}
	return $title;
}

/**
 * the_content - Modify post content
 */
add_filter('the_content', 'append_property_cta');
function append_property_cta($content) {
	if (is_singular('property') && is_main_query()) {
		$cta = '<div class="property-cta"><a href="#inquiry">Schedule a Viewing</a></div>';
		$content .= $cta;
	}
	return $content;
}

/**
 * the_excerpt - Modify excerpt
 */
add_filter('the_excerpt', 'custom_excerpt');
function custom_excerpt($excerpt) {
	return '<div class="excerpt">' . $excerpt . '</div>';
}

/**
 * excerpt_length - Change excerpt word count
 */
add_filter('excerpt_length', 'custom_excerpt_length');
function custom_excerpt_length($length) {
	return 30;  // 30 words
}

/**
 * excerpt_more - Change [...] text
 */
add_filter('excerpt_more', 'custom_excerpt_more');
function custom_excerpt_more($more) {
	return '&hellip; <a href="' . get_permalink() . '">Read more</a>';
}
```

### URL and Link Filters

```php
/**
 * post_type_link - Modify CPT permalinks
 */
add_filter('post_type_link', 'property_permalink', 10, 2);
function property_permalink($permalink, $post) {
	if ('property' !== $post->post_type) {
		return $permalink;
	}

	// Add location to URL: /properties/miami/property-name/
	$location = get_the_terms($post->ID, 'property_location');
	if ($location && !is_wp_error($location)) {
		$permalink = str_replace('%property_location%', $location[0]->slug, $permalink);
	}

	return $permalink;
}

/**
 * wp_nav_menu_items - Modify menu items
 */
add_filter('wp_nav_menu_items', 'add_login_menu_item', 10, 2);
function add_login_menu_item($items, $args) {
	if ('primary' === $args->theme_location) {
		if (is_user_logged_in()) {
			$items .= '<li><a href="' . wp_logout_url(home_url()) . '">Logout</a></li>';
		} else {
			$items .= '<li><a href="' . wp_login_url() . '">Login</a></li>';
		}
	}
	return $items;
}
```

### Query Filters

```php
/**
 * posts_where - Modify WHERE clause
 */
add_filter('posts_where', 'title_search_where', 10, 2);
function title_search_where($where, $query) {
	global $wpdb;

	if ($query->get('title_search')) {
		$title = $wpdb->esc_like($query->get('title_search'));
		$where .= $wpdb->prepare(" AND {$wpdb->posts}.post_title LIKE %s", '%' . $title . '%');
	}

	return $where;
}

// Usage
$query = new WP_Query(array(
	'post_type'    => 'property',
	'title_search' => 'Miami',
));
```

### Image Filters

```php
/**
 * post_thumbnail_html - Modify featured image output
 */
add_filter('post_thumbnail_html', 'lazy_load_thumbnails', 10, 5);
function lazy_load_thumbnails($html, $post_id, $post_thumbnail_id, $size, $attr) {
	// Add loading="lazy" if not already present
	if (strpos($html, 'loading=') === false) {
		$html = str_replace('<img', '<img loading="lazy"', $html);
	}
	return $html;
}

/**
 * wp_get_attachment_image_attributes - Modify image attributes
 */
add_filter('wp_get_attachment_image_attributes', 'custom_image_attributes', 10, 3);
function custom_image_attributes($attr, $attachment, $size) {
	// Add custom class
	$attr['class'] .= ' lazy-image';

	// Add data attributes for JS
	$attr['data-id'] = $attachment->ID;

	return $attr;
}
```

### Admin Filters

```php
/**
 * manage_posts_columns - Modify admin columns
 */
add_filter('manage_property_posts_columns', 'property_admin_columns');
function property_admin_columns($columns) {
	$new_columns = array();

	foreach ($columns as $key => $value) {
		$new_columns[$key] = $value;

		if ('title' === $key) {
			$new_columns['property_price'] = __('Price', 'theme-name');
			$new_columns['property_status'] = __('Status', 'theme-name');
		}
	}

	return $new_columns;
}

/**
 * upload_mimes - Allow additional file types
 */
add_filter('upload_mimes', 'allow_svg_upload');
function allow_svg_upload($mimes) {
	$mimes['svg'] = 'image/svg+xml';
	$mimes['webp'] = 'image/webp';
	return $mimes;
}
```

### Body Class Filter

```php
/**
 * body_class - Add custom body classes
 */
add_filter('body_class', 'theme_body_classes');
function theme_body_classes($classes) {
	// Add page slug
	if (is_singular()) {
		global $post;
		$classes[] = 'page-' . $post->post_name;
	}

	// Add logged-in class
	if (is_user_logged_in()) {
		$classes[] = 'logged-in';
		$user = wp_get_current_user();
		$classes[] = 'role-' . $user->roles[0];
	}

	// Add browser class
	$classes[] = theme_get_browser_class();

	return $classes;
}
```

## Hook Priority

Priority determines execution order (default: 10):

```php
// Lower number = runs first
add_action('init', 'run_first', 1);
add_action('init', 'run_default');     // Priority 10
add_action('init', 'run_last', 99);

// For filters, last one wins if modifying same data
add_filter('the_title', 'first_filter', 5);   // Runs first
add_filter('the_title', 'second_filter', 15); // Runs last, gets final say
```

## Accepting Arguments

```php
// Accept multiple arguments
add_action('save_post', 'my_save_handler', 10, 3);
function my_save_handler($post_id, $post, $update) {
	// $update is true if this is an update, false if new post
}

add_filter('the_title', 'my_title_filter', 10, 2);
function my_title_filter($title, $post_id) {
	// Have access to both title and post ID
	return $title;
}
```

## Removing Hooks

```php
// Remove action
remove_action('wp_head', 'wp_generator');
remove_action('wp_head', 'rsd_link');
remove_action('wp_head', 'wlwmanifest_link');

// Remove filter
remove_filter('the_content', 'wpautop');

// Remove from a class (need reference to instance)
remove_action('init', array($plugin_instance, 'init_method'));

// Remove all callbacks at specific priority
remove_all_actions('wp_head', 10);
```

## Creating Custom Hooks

```php
// Create action hook
function theme_header() {
	?>
	<header class="site-header">
		<?php do_action('theme_before_header'); ?>

		<div class="header-content">
			<!-- Header content -->
		</div>

		<?php do_action('theme_after_header'); ?>
	</header>
	<?php
}

// Create filter hook
function theme_get_logo() {
	$logo = get_theme_file_uri('/assets/images/logo.svg');
	return apply_filters('theme_logo_url', $logo);
}

// Users can hook into your custom hooks
add_action('theme_before_header', 'add_promo_bar');
add_filter('theme_logo_url', 'use_custom_logo');
```

## Hook Reference

### Full Hook Execution Order

```
muplugins_loaded
plugins_loaded
setup_theme
after_setup_theme
init
wp_loaded
parse_request
send_headers
parse_query
pre_get_posts
posts_selection
wp
template_redirect
get_header
wp_head
wp_enqueue_scripts
the_post
the_content
get_footer
wp_footer
```

## Resources

- [Action Reference](https://codex.wordpress.org/Plugin_API/Action_Reference)
- [Filter Reference](https://codex.wordpress.org/Plugin_API/Filter_Reference)
- [Plugin API](https://developer.wordpress.org/plugins/hooks/)
