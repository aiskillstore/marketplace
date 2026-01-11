# WordPress Performance Optimization

Guide to optimizing WordPress sites for speed and efficiency.

## Database Query Optimization

### Use Transients for Expensive Queries

```php
/**
 * Get featured properties with caching.
 */
function theme_get_featured_properties() {
	// Try to get from cache
	$properties = get_transient('featured_properties');

	if (false === $properties) {
		// Cache miss - run query
		$query = new WP_Query(array(
			'post_type'      => 'property',
			'posts_per_page' => 6,
			'meta_key'       => '_featured',
			'meta_value'     => '1',
		));

		$properties = $query->posts;

		// Cache for 1 hour
		set_transient('featured_properties', $properties, HOUR_IN_SECONDS);
	}

	return $properties;
}

// Clear cache when properties are updated
function theme_clear_property_cache($post_id) {
	if ('property' === get_post_type($post_id)) {
		delete_transient('featured_properties');
	}
}
add_action('save_post', 'theme_clear_property_cache');
add_action('delete_post', 'theme_clear_property_cache');
```

### Optimize WP_Query

```php
// SLOW - Fetches everything
$query = new WP_Query(array(
	'post_type'      => 'property',
	'posts_per_page' => -1,  // Dangerous for large sites!
));

// BETTER - Only get what you need
$query = new WP_Query(array(
	'post_type'              => 'property',
	'posts_per_page'         => 12,  // Reasonable limit
	'no_found_rows'          => true,  // Skip counting total (if no pagination)
	'update_post_meta_cache' => false, // Skip if not using meta
	'update_post_term_cache' => false, // Skip if not using terms
	'fields'                 => 'ids', // Only get IDs if that's all you need
));

// For checking existence only
$exists = new WP_Query(array(
	'post_type'      => 'property',
	'posts_per_page' => 1,
	'no_found_rows'  => true,
	'fields'         => 'ids',
));

if ($exists->have_posts()) {
	// At least one exists
}
```

### Avoid Common Query Mistakes

```php
// NEVER use query_posts() - it modifies the main query
query_posts(array('post_type' => 'property'));  // DON'T!

// Use WP_Query for secondary loops
$properties = new WP_Query(array('post_type' => 'property'));

// Use pre_get_posts to modify main query
function theme_modify_main_query($query) {
	if (!is_admin() && $query->is_main_query() && is_home()) {
		$query->set('posts_per_page', 12);
	}
}
add_action('pre_get_posts', 'theme_modify_main_query');
```

### Efficient Meta Queries

```php
// SLOW - Multiple meta queries
$query = new WP_Query(array(
	'post_type'  => 'property',
	'meta_query' => array(
		'relation' => 'AND',
		array('key' => '_price', 'value' => 100000, 'compare' => '>=', 'type' => 'NUMERIC'),
		array('key' => '_price', 'value' => 500000, 'compare' => '<=', 'type' => 'NUMERIC'),
		array('key' => '_bedrooms', 'value' => 3, 'compare' => '>=', 'type' => 'NUMERIC'),
		array('key' => '_featured', 'value' => '1'),
	),
));

// BETTER - Use taxonomies for filterable attributes
// Create taxonomies for bedrooms, price ranges, etc.
$query = new WP_Query(array(
	'post_type'  => 'property',
	'tax_query'  => array(
		array(
			'taxonomy' => 'price_range',
			'field'    => 'slug',
			'terms'    => '100k-500k',
		),
		array(
			'taxonomy' => 'bedrooms',
			'field'    => 'slug',
			'terms'    => array('3-bed', '4-bed', '5-bed'),
		),
	),
	'meta_key'   => '_featured',
	'meta_value' => '1',
));
```

## Object Caching

### Using Object Cache

```php
// Store in object cache (survives within request)
wp_cache_set('my_data', $data, 'theme_cache', HOUR_IN_SECONDS);

// Retrieve from cache
$data = wp_cache_get('my_data', 'theme_cache');

if (false === $data) {
	// Cache miss - fetch data
	$data = expensive_operation();
	wp_cache_set('my_data', $data, 'theme_cache', HOUR_IN_SECONDS);
}

// Delete from cache
wp_cache_delete('my_data', 'theme_cache');
```

### Persistent Object Cache

For production, use Redis or Memcached:

```php
// wp-config.php
define('WP_CACHE', true);

// Install object-cache.php drop-in
// e.g., Redis Object Cache plugin
```

## Asset Loading Optimization

### Conditional Loading

```php
function theme_enqueue_assets() {
	// Always load main styles
	wp_enqueue_style('theme-style', get_stylesheet_uri());

	// Only load on specific pages
	if (is_page('contact')) {
		wp_enqueue_script('google-maps', 'https://maps.googleapis.com/maps/api/js');
		wp_enqueue_script('contact-form', get_theme_file_uri('/assets/js/contact.js'));
	}

	// Only load on single property
	if (is_singular('property')) {
		wp_enqueue_script('property-gallery', get_theme_file_uri('/assets/js/gallery.js'));
	}

	// Only load GSAP on pages with animations
	if (is_front_page() || is_page(array('about', 'portfolio'))) {
		wp_enqueue_script('gsap', 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js');
	}
}
add_action('wp_enqueue_scripts', 'theme_enqueue_assets');
```

### Defer and Async Scripts

```php
// Add defer attribute
function theme_defer_scripts($tag, $handle, $src) {
	$defer_scripts = array('theme-main', 'gsap', 'analytics');

	if (in_array($handle, $defer_scripts, true)) {
		return str_replace(' src', ' defer src', $tag);
	}

	return $tag;
}
add_filter('script_loader_tag', 'theme_defer_scripts', 10, 3);

// Add async attribute
function theme_async_scripts($tag, $handle, $src) {
	$async_scripts = array('analytics', 'third-party');

	if (in_array($handle, $async_scripts, true)) {
		return str_replace(' src', ' async src', $tag);
	}

	return $tag;
}
add_filter('script_loader_tag', 'theme_async_scripts', 10, 3);
```

### Version Busting

```php
// Use file modification time for cache busting
wp_enqueue_style(
	'theme-style',
	get_stylesheet_uri(),
	array(),
	filemtime(get_stylesheet_directory() . '/style.css')
);

wp_enqueue_script(
	'theme-main',
	get_theme_file_uri('/assets/js/main.js'),
	array('jquery'),
	filemtime(get_theme_file_path('/assets/js/main.js')),
	true
);
```

### Remove Unused Assets

```php
// Remove block library CSS if not using blocks
function theme_remove_unused_assets() {
	// Remove block styles
	wp_dequeue_style('wp-block-library');
	wp_dequeue_style('wp-block-library-theme');

	// Remove global styles (if classic theme)
	wp_dequeue_style('global-styles');

	// Remove emoji scripts
	remove_action('wp_head', 'print_emoji_detection_script', 7);
	remove_action('wp_print_styles', 'print_emoji_styles');
}
add_action('wp_enqueue_scripts', 'theme_remove_unused_assets', 100);
```

## Image Optimization

### Lazy Loading

WordPress 5.5+ has native lazy loading:

```php
// Disable native lazy loading if using custom solution
add_filter('wp_lazy_loading_enabled', '__return_false');

// Or enable for specific image sizes
function theme_lazy_load_sizes($sizes) {
	$sizes['thumbnail'] = false;  // Don't lazy load thumbnails
	return $sizes;
}
add_filter('wp_lazy_loading_sizes', 'theme_lazy_load_sizes');
```

### Responsive Images

```php
// WordPress generates srcset automatically for images
the_post_thumbnail('large'); // Includes srcset

// Custom srcset
$image_id = get_post_thumbnail_id();
$image_srcset = wp_get_attachment_image_srcset($image_id, 'large');
$image_sizes = wp_get_attachment_image_sizes($image_id, 'large');

?>
<img
	src="<?php echo esc_url(wp_get_attachment_image_url($image_id, 'large')); ?>"
	srcset="<?php echo esc_attr($image_srcset); ?>"
	sizes="<?php echo esc_attr($image_sizes); ?>"
	alt="<?php echo esc_attr(get_post_meta($image_id, '_wp_attachment_image_alt', true)); ?>"
	loading="lazy"
>
```

### Add Custom Image Sizes

```php
function theme_custom_image_sizes() {
	// Hero images
	add_image_size('hero', 1920, 1080, true);
	add_image_size('hero-mobile', 768, 1024, true);

	// Cards
	add_image_size('card', 600, 400, true);
	add_image_size('card-small', 300, 200, true);

	// Thumbnails
	add_image_size('thumb-square', 150, 150, true);
}
add_action('after_setup_theme', 'theme_custom_image_sizes');
```

## Reducing HTTP Requests

### Combine and Minify

For production, use build tools:

```json
// package.json
{
  "scripts": {
    "build:css": "sass src/scss:assets/css --style=compressed",
    "build:js": "terser src/js/main.js -o assets/js/main.min.js -c -m"
  }
}
```

### Inline Critical CSS

```php
function theme_inline_critical_css() {
	$critical_css = file_get_contents(get_theme_file_path('/assets/css/critical.css'));
	echo '<style id="critical-css">' . $critical_css . '</style>';
}
add_action('wp_head', 'theme_inline_critical_css', 1);

// Load full CSS asynchronously
function theme_async_css() {
	$css_url = get_stylesheet_uri();
	?>
	<link rel="preload" href="<?php echo esc_url($css_url); ?>" as="style" onload="this.onload=null;this.rel='stylesheet'">
	<noscript><link rel="stylesheet" href="<?php echo esc_url($css_url); ?>"></noscript>
	<?php
}
add_action('wp_head', 'theme_async_css', 2);
```

### Preload Key Resources

```php
function theme_preload_resources() {
	?>
	<!-- Preload fonts -->
	<link rel="preload" href="<?php echo esc_url(get_theme_file_uri('/assets/fonts/inter.woff2')); ?>" as="font" type="font/woff2" crossorigin>

	<!-- Preload hero image on home page -->
	<?php if (is_front_page()) : ?>
		<link rel="preload" href="<?php echo esc_url(get_theme_file_uri('/assets/images/hero.webp')); ?>" as="image">
	<?php endif; ?>

	<!-- DNS prefetch for external resources -->
	<link rel="dns-prefetch" href="//fonts.googleapis.com">
	<link rel="dns-prefetch" href="//cdnjs.cloudflare.com">
	<?php
}
add_action('wp_head', 'theme_preload_resources', 1);
```

## Database Maintenance

### Clean Up

```php
// Remove post revisions older than 30 days
function theme_cleanup_revisions() {
	global $wpdb;

	$wpdb->query(
		$wpdb->prepare(
			"DELETE FROM {$wpdb->posts}
			 WHERE post_type = 'revision'
			 AND post_date < %s",
			date('Y-m-d', strtotime('-30 days'))
		)
	);
}
// Run weekly via cron
```

### Limit Revisions

```php
// wp-config.php
define('WP_POST_REVISIONS', 5);  // Keep only 5 revisions

// Or disable completely
define('WP_POST_REVISIONS', false);
```

### Optimize Autoloaded Options

```php
// Check autoloaded options size
SELECT SUM(LENGTH(option_value)) / 1024 / 1024 as size_mb
FROM wp_options
WHERE autoload = 'yes';

// In PHP, use autoload wisely
update_option('rarely_used_option', $value, false);  // Don't autoload
update_option('frequently_used_option', $value, true);  // Autoload
```

## Cron Optimization

### Disable WP-Cron for High Traffic

```php
// wp-config.php
define('DISABLE_WP_CRON', true);

// Set up real cron job instead
// crontab -e
// */15 * * * * curl https://yoursite.com/wp-cron.php?doing_wp_cron >/dev/null 2>&1
```

### Schedule Efficiently

```php
// Don't run heavy tasks on every page load
function theme_schedule_cleanup() {
	if (!wp_next_scheduled('theme_daily_cleanup')) {
		wp_schedule_event(time(), 'daily', 'theme_daily_cleanup');
	}
}
add_action('wp', 'theme_schedule_cleanup');

function theme_run_cleanup() {
	// Heavy cleanup tasks here
	theme_cleanup_revisions();
	theme_clear_expired_transients();
}
add_action('theme_daily_cleanup', 'theme_run_cleanup');
```

## Performance Monitoring

### Query Monitor

```php
// In development, use Query Monitor plugin
// Shows:
// - Database queries and their time
// - HTTP API calls
// - Hooks and actions
// - Conditionals
// - Transients
```

### Custom Timing

```php
function theme_start_timer() {
	if (WP_DEBUG) {
		global $theme_start_time;
		$theme_start_time = microtime(true);
	}
}
add_action('wp', 'theme_start_timer');

function theme_end_timer() {
	if (WP_DEBUG) {
		global $theme_start_time;
		$execution_time = microtime(true) - $theme_start_time;
		error_log(sprintf('Page generated in %f seconds', $execution_time));
	}
}
add_action('wp_footer', 'theme_end_timer');
```

## Performance Checklist

### Database
- [ ] Use transients for expensive queries
- [ ] Limit WP_Query results
- [ ] Use `no_found_rows` when possible
- [ ] Add indexes to custom tables
- [ ] Clean up revisions and transients

### Assets
- [ ] Combine and minify CSS/JS
- [ ] Defer non-critical scripts
- [ ] Conditionally load page-specific assets
- [ ] Remove unused block styles
- [ ] Use version busting

### Images
- [ ] Enable lazy loading
- [ ] Use responsive images (srcset)
- [ ] Serve WebP format
- [ ] Optimize image sizes
- [ ] Use CDN for media

### Caching
- [ ] Implement object caching
- [ ] Use transients effectively
- [ ] Set proper cache headers
- [ ] Use page caching plugin

### Server
- [ ] Enable GZIP compression
- [ ] Use PHP 8.0+
- [ ] Configure opcache
- [ ] Use HTTP/2

## Resources

- [WordPress Performance Handbook](https://developer.wordpress.org/performance/)
- [Query Monitor Plugin](https://querymonitor.com/)
- [WebPageTest](https://www.webpagetest.org/)
- [GTmetrix](https://gtmetrix.com/)
