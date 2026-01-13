# WordPress Template Hierarchy

Complete guide to WordPress theme template files and their loading order.

## Visual Overview

```
                                    index.php
                                        │
    ┌───────────────────────────────────┼───────────────────────────────────┐
    │                                   │                                   │
singular.php                        archive.php                         home.php
    │                                   │                                   │
    ├── single.php                      ├── author.php                  blog.php
    │   ├── single-{post-type}.php      │   └── author-{nicename}.php
    │   └── single-{post-type}-{slug}.php│   └── author-{id}.php
    │                                   │
    ├── page.php                        ├── category.php
    │   ├── page-{slug}.php             │   └── category-{slug}.php
    │   └── page-{id}.php               │   └── category-{id}.php
    │                                   │
    └── attachment.php                  ├── tag.php
        ├── {mime-type}.php             │   └── tag-{slug}.php
        ├── {subtype}.php               │   └── tag-{id}.php
        └── {type}-{subtype}.php        │
                                        ├── taxonomy.php
                                        │   └── taxonomy-{taxonomy}.php
                                        │   └── taxonomy-{taxonomy}-{term}.php
                                        │
                                        ├── date.php
                                        │
                                        └── archive-{post-type}.php
```

## Template Types

### Single Post/Page Templates

#### Posts

```
1. single-post-{slug}.php     → single-post-hello-world.php
2. single-post.php
3. single.php
4. singular.php
5. index.php
```

#### Custom Post Types

```
1. single-{post-type}-{slug}.php → single-property-miami-beach.php
2. single-{post-type}.php        → single-property.php
3. single.php
4. singular.php
5. index.php
```

#### Pages

```
1. {custom-template}.php    → template-full-width.php (assigned in editor)
2. page-{slug}.php          → page-about.php
3. page-{id}.php            → page-42.php
4. page.php
5. singular.php
6. index.php
```

#### Attachments

```
1. {mime-type}-{subtype}.php → image-jpeg.php
2. {subtype}.php             → jpeg.php
3. {mime-type}.php           → image.php
4. attachment.php
5. single-attachment-{slug}.php
6. single-attachment.php
7. single.php
8. singular.php
9. index.php
```

### Archive Templates

#### Category

```
1. category-{slug}.php   → category-news.php
2. category-{id}.php     → category-5.php
3. category.php
4. archive.php
5. index.php
```

#### Tag

```
1. tag-{slug}.php    → tag-featured.php
2. tag-{id}.php      → tag-10.php
3. tag.php
4. archive.php
5. index.php
```

#### Custom Taxonomy

```
1. taxonomy-{taxonomy}-{term}.php → taxonomy-property_type-commercial.php
2. taxonomy-{taxonomy}.php        → taxonomy-property_type.php
3. taxonomy.php
4. archive.php
5. index.php
```

#### Author

```
1. author-{nicename}.php → author-john.php
2. author-{id}.php       → author-3.php
3. author.php
4. archive.php
5. index.php
```

#### Date

```
1. date.php
2. archive.php
3. index.php
```

#### Custom Post Type Archive

```
1. archive-{post-type}.php → archive-property.php
2. archive.php
3. index.php
```

### Special Templates

#### Front Page

```
1. front-page.php    (if set to static page OR posts)
2. home.php          (if front page shows posts)
3. page.php          (if front page is static page)
4. index.php
```

#### Blog (Posts Page)

```
1. home.php
2. index.php
```

#### Search Results

```
1. search.php
2. index.php
```

#### 404 Error

```
1. 404.php
2. index.php
```

#### Privacy Policy

```
1. privacy-policy.php
2. page-privacy-policy.php
3. page-{id}.php
4. page.php
5. singular.php
6. index.php
```

## Template Parts

### Using get_template_part()

```php
// Basic usage
get_template_part('template-parts/content');
// Looks for: template-parts/content.php

// With name
get_template_part('template-parts/content', 'single');
// Looks for: template-parts/content-single.php, then content.php

// With post format
get_template_part('template-parts/content', get_post_format());
// Looks for: content-video.php, content-gallery.php, etc.

// With custom post type
get_template_part('template-parts/content', get_post_type());
// Looks for: content-property.php, content-post.php, etc.

// Pass variables (WP 5.5+)
get_template_part('template-parts/card', 'property', array(
	'show_price' => true,
	'featured'   => false,
));

// In template part, access with:
$args['show_price']; // true
$args['featured'];   // false
```

### Template Part Organization

```
theme/
├── template-parts/
│   ├── content/
│   │   ├── content.php
│   │   ├── content-single.php
│   │   ├── content-page.php
│   │   ├── content-property.php
│   │   └── content-none.php
│   ├── header/
│   │   ├── header-default.php
│   │   └── header-minimal.php
│   ├── footer/
│   │   ├── footer-default.php
│   │   └── footer-minimal.php
│   ├── cards/
│   │   ├── card-property.php
│   │   ├── card-post.php
│   │   └── card-team.php
│   └── components/
│       ├── pagination.php
│       ├── social-share.php
│       └── related-posts.php
```

## Custom Page Templates

### Creating Custom Templates

```php
<?php
/**
 * Template Name: Full Width
 * Template Post Type: page, post, property
 *
 * @package Theme_Name
 */

get_header();
?>

<main class="full-width-template">
	<?php while (have_posts()) : the_post(); ?>
		<article id="post-<?php the_ID(); ?>">
			<?php the_content(); ?>
		</article>
	<?php endwhile; ?>
</main>

<?php
get_footer();
```

### Template for Specific Post Type

```php
<?php
/**
 * Template Name: Property Showcase
 * Template Post Type: property
 *
 * @package Theme_Name
 */

// Only available for 'property' post type
```

## Block Templates (FSE)

### Block Theme Structure

```
theme/
├── templates/          # Block templates (HTML)
│   ├── index.html
│   ├── single.html
│   ├── single-property.html
│   ├── page.html
│   ├── archive.html
│   ├── archive-property.html
│   ├── home.html
│   ├── front-page.html
│   ├── search.html
│   └── 404.html
├── parts/              # Template parts
│   ├── header.html
│   ├── footer.html
│   └── sidebar.html
├── patterns/           # Block patterns
│   └── hero.php
├── styles/             # Style variations
│   └── dark.json
└── theme.json          # Global styles & settings
```

### Block Template Example

```html
<!-- templates/single-property.html -->
<!-- wp:template-part {"slug":"header"} /-->

<main class="wp-block-group">
	<!-- wp:post-featured-image {"height":"500px"} /-->

	<!-- wp:group {"layout":{"type":"constrained"}} -->
	<div class="wp-block-group">
		<!-- wp:post-title {"level":1} /-->
		<!-- wp:post-content /-->
	</div>
	<!-- /wp:group -->
</main>

<!-- wp:template-part {"slug":"footer"} /-->
```

### Template Part Example

```html
<!-- parts/header.html -->
<!-- wp:group {"tagName":"header","className":"site-header"} -->
<header class="wp-block-group site-header">
	<!-- wp:group {"layout":{"type":"flex","justifyContent":"space-between"}} -->
	<div class="wp-block-group">
		<!-- wp:site-logo {"width":150} /-->
		<!-- wp:navigation {"ref":123} /-->
	</div>
	<!-- /wp:group -->
</header>
<!-- /wp:group -->
```

## Template Tags

### Common Template Tags

```php
// Header and Footer
get_header();              // header.php
get_header('minimal');     // header-minimal.php
get_footer();              // footer.php
get_footer('simple');      // footer-simple.php
get_sidebar();             // sidebar.php
get_sidebar('shop');       // sidebar-shop.php

// Search Form
get_search_form();         // searchform.php

// Comments
comments_template();       // comments.php
comments_template('/comments-custom.php');
```

### Checking Template Type

```php
// Conditional tags
is_front_page()    // Static front page
is_home()          // Blog posts page
is_single()        // Single post
is_singular()      // Single post, page, or attachment
is_page()          // Single page
is_page('about')   // Specific page by slug
is_page(42)        // Specific page by ID
is_archive()       // Any archive
is_category()      // Category archive
is_tag()           // Tag archive
is_tax()           // Taxonomy archive
is_post_type_archive('property')
is_author()        // Author archive
is_date()          // Date archive
is_search()        // Search results
is_404()           // 404 page

// In the loop
is_single('property')    // Single property post type
is_singular('property')  // Same as above
```

## Theme Files Reference

### Required Files

```
theme/
├── index.php        # Fallback template (REQUIRED)
├── style.css        # Theme info header (REQUIRED)
└── screenshot.png   # Theme preview (2:1 ratio, 1200x900px)
```

### Common Theme Structure

```
theme/
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fonts/
├── inc/
│   ├── custom-post-types.php
│   ├── customizer.php
│   └── template-functions.php
├── template-parts/
│   ├── content/
│   ├── header/
│   └── footer/
├── 404.php
├── archive.php
├── comments.php
├── footer.php
├── functions.php
├── header.php
├── index.php
├── page.php
├── search.php
├── searchform.php
├── sidebar.php
├── single.php
└── style.css
```

## Debugging Templates

### Show Current Template

```php
// Add to footer.php (development only)
function show_current_template() {
	if (WP_DEBUG && current_user_can('manage_options')) {
		global $template;
		echo '<!-- Current template: ' . basename($template) . ' -->';
	}
}
add_action('wp_footer', 'show_current_template');
```

### Template Hierarchy Visual

Install "Show Current Template" plugin or add:

```php
function debug_template_hierarchy($template) {
	if (WP_DEBUG) {
		error_log('Template loaded: ' . $template);
	}
	return $template;
}
add_filter('template_include', 'debug_template_hierarchy', 999);
```

## Best Practices

### 1. Use Template Parts

```php
// Instead of duplicating code, use template parts
// Bad
// Copy-paste same card HTML in multiple templates

// Good
get_template_part('template-parts/card', 'property');
```

### 2. Pass Data to Templates

```php
// WP 5.5+ - pass args
get_template_part('template-parts/card', 'property', array(
	'post_id'    => get_the_ID(),
	'show_price' => true,
	'layout'     => 'horizontal',
));
```

### 3. Create Specific Templates When Needed

```php
// For special pages, create specific templates
// page-about.php - About page
// single-property.php - Property detail
// archive-property.php - Property listing
```

### 4. Use Hooks for Flexibility

```php
// In template
do_action('theme_before_content');
the_content();
do_action('theme_after_content');

// Can be hooked by child themes or plugins
```

### 5. Support Child Themes

```php
// Use get_template_directory() for parent theme files
// Use get_stylesheet_directory() for child theme files
// Or use get_theme_file_path() which checks child first

$template_path = get_theme_file_path('/template-parts/header.php');
```

## Resources

- [Template Hierarchy Diagram](https://developer.wordpress.org/themes/basics/template-hierarchy/)
- [Template Tags](https://developer.wordpress.org/themes/references/list-of-template-tags/)
- [Conditional Tags](https://developer.wordpress.org/themes/basics/conditional-tags/)
- [Block Themes](https://developer.wordpress.org/block-editor/how-to-guides/themes/block-theme-overview/)
