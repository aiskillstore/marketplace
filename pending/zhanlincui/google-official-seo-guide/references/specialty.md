# Google-Search-Docs - Specialty

**Pages:** 5

---

## Tell Google about localized versions of your page

**URL:** https://developers.google.com/search/docs/specialty/international/localized-versions

**Contents:**
- Tell Google about localized versions of your page
- Methods for indicating your alternate pages
  - Guidelines for all methods
  - HTML tags
    - Example
  - HTTP Headers
    - Example
  - Sitemap
    - Example
- Supported language and region codes

If you have multiple versions of a page for different languages or regions, tell Google about these different variations. Doing so will help Google Search point users to the most appropriate version of your page by language or region.

Note that even without taking action, Google might still find alternate language versions of your page, but it is usually best for you to explicitly indicate your language- or region-specific pages.

Some example scenarios where indicating alternate pages is recommended:

Localized versions of a page are only considered duplicates if the main content of the page remains untranslated.

There are three ways to indicate multiple language/locale versions of a page to Google:

The three methods are equivalent from Google's perspective and you can choose the method that's the most convenient for your site. While you can use all three methods at the same time, there's no benefit in Search (in fact, it maybe be much harder to manage three implementations instead of just picking one).

Use hreflang to tell Google about the variations of your content, so that we can understand that these pages are localized variations of the same content. Google doesn't use hreflang or the HTML lang attribute to detect the language of a page; instead, we use algorithms to determine the language.

Add <link rel="alternate" hreflang="lang_code"... > elements to your page header to tell Google all of the language and region variants of a page. This is useful if you don't have a sitemap or the ability to specify HTTP response headers for your site.

For each variation of the page, include a set of <link> elements in the <head> element, one link for each page variant including itself. The set of links is identical for every version of the page. See the additional guidelines.

Here is the syntax of each link element:

The <link> tags must be inside a well-formed <head> section of the HTML. If in doubt, paste code from your rendered page into an HTML validator to ensure that the links are inside the <head> element. Additionally, don't combine link tags for alternate representations of the document; for example don't combine hreflang annotations with other attributes such as media in a single <link> tag.

Example Widgets, Inc has a website that serves users in the USA, UK, and Germany. The following URLs contain substantially the same content, but with regional variations:

Note that the language-specific subdomains in these URLs (en, en-gb, en-us, de) are no

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<link rel="alternate" hreflang="lang_code" href="url_of_page" />
```

Example 2 (unknown):
```unknown
<head>
 <title>Widgets, Inc</title>
  <link rel="alternate" hreflang="en-gb"
       href="https://en-gb.example.com/page.html" />
  <link rel="alternate" hreflang="en-us"
       href="https://en-us.example.com/page.html" />
  <link rel="alternate" hreflang="en"
       href="https://en.example.com/page.html" />
  <link rel="alternate" hreflang="de"
       href="https://de.example.com/page.html" />
 <link rel="alternate" hreflang="x-default"
       href="https://www.example.com/" />
</head>
```

Example 3 (unknown):
```unknown
Link: <url1>; rel="alternate"; hreflang="lang_code_1", <url2>; rel="alternate"; hreflang="lang_code_2", ...
```

Example 4 (unknown):
```unknown
Link: <https://example.com/file.pdf>; rel="alternate"; hreflang="en",
      <https://de-ch.example.com/file.pdf>; rel="alternate"; hreflang="de-ch",
      <https://de.example.com/file.pdf>; rel="alternate"; hreflang="de"
```

---

## Write high quality reviews

**URL:** https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews

**Contents:**
- Write high quality reviews

Publishing high quality reviews can help people learn more about things they are considering, such as products, services, destinations, games, movies or other topics. For example, you could write a review as:

To help people discover your review pages in Google Search and on other Google surfaces, follow these best practices:

Reviews often use affiliate links, so that if someone finds a review useful and follows the provided link to purchase, the creator of the review is rewarded by the seller. If you do this, see also Google's position on affiliate programs.

Reviews can be a great resource for people when making decisions. When writing reviews, focus on the quality and originality of your reviews, not the length, following as many of the above best practices as you are able. This will deliver the most value to those reading your reviews.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-02-04 UTC.

---

## Help Google understand your ecommerce website structure

**URL:** https://developers.google.com/search/docs/specialty/ecommerce/help-google-understand-your-ecommerce-site-structure

**Contents:**
- Help Google understand your ecommerce website structure
- Make your ecommerce site navigation Google crawler friendly
- Promote your best categories or products

Google tries to find the best content on your site by analyzing the relationship between pages based on their linkages. This means navigation structures on your site (such as menus and cross page links) can impact Google's understanding of your site structure.

For example, Google can use information such as the number of links it needs to follow to reach a page and the number of links to a page to infer the relative importance of a page over the rest of your site. For more information on how Google determines the importance of a page in Google Search, see How Google Search Works.

To help Google find all pages on your site, make sure that you follow ecommerce site best practices and that your pages are reachable by following links through your site's navigation. For example, add links from menus to category pages, from category pages to sub-category pages, and finally from sub-category pages to all product pages. We also recommend that you add structured data, since this can help Google understand the purpose of the different pages on your site to reinforce this structure.

If category pages don't include direct links to all products in a category, Googlebot might not find all of your products by crawling alone. These products may be reachable from a search box, but not via category browsing. Googlebot generally doesn't try to submit searches into a search box as part of crawling a site. It's strongly recommended to link to all products that you wish indexed. If it's not possible to link to all pages, use a sitemap or a Google Merchant Center feed. These sources can include links to pages on a site that a crawler would not otherwise find.

To ensure Googlebot correctly locates the link, use <a href> tags when creating links to other content. Don't use JavaScript events on other HTML DOM elements for navigation. If you want to learn more about JavaScript and indexing page content, see Understand the JavaScript SEO basics.

Google generally doesn't look at the structure of URLs to work out the structure of a site. Instead, it analyzes the linkages between pages to gain insights about the relative importance of different pages on a site. As a general rule, the more links a page has to it within a site, the higher the relative importance of the page to other pages on your site.

For example, if you have a best selling product, consider linking to it from the home page or in other content, such as blog posts or newsletters on your site. This will help Google u

*[Content truncated]*

---

## Managing multi-regional and multilingual sites

**URL:** https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites#geotargeting

**Contents:**
- Managing multi-regional and multilingual sites
- What's the difference between multilingual and multi-regional?
- Managing multilingual versions of your site
  - Use different URLs for different language versions
  - Tell Google about your different language versions
  - Make sure the page language is obvious
  - Let the user switch the page language
  - Use language-specific URLs
- Targeting site content to a specific country (geotargeting)
  - Using locale-specific URLs

If your site offers different content to users in different languages, countries, or regions, you can optimize Google Search results for your site.

Some sites are both multi-regional and multilingual: for example, a site might have different versions for the USA and for Canada, and both French and English versions of the Canadian content.

If you have identical content in multiple languages on your site, here are some tips for helping users (and Google Search) find the right page:

Google recommends using different URLs for each language version of a page rather than using cookies or browser settings to adjust the content language on the page.

If you use different URLs for different languages, use hreflang annotations to help Google Search results link to the correct language version of a page.

If you prefer to dynamically change content or reroute the user based on language settings, be aware that Google might not find and crawl all your variations. This is because the Googlebot crawler usually originates from the USA. In addition, the crawler sends HTTP requests without setting Accept-Language in the request header.

Google supports several different methods for labeling language or region variants of a page, including hreflang annotations and sitemaps. Mark your pages appropriately.

Google uses the visible content of your page to determine its language. We don't use any code-level language information such as lang attributes, or the URL. You can help Google determine the language correctly by using a single language for content and navigation on each page, and by avoiding side-by-side translations.

Translating only the boilerplate text of your pages while keeping the bulk of your content in a single language (as often happens on pages featuring user-generated content) can create a bad user experience if the same content appears multiple times in search results with various boilerplate languages.

If you have multiple versions of a page:

It's fine to use localized words in the URL, or to use an Internationalized Domain Name (IDN). However, be sure to use UTF-8 encoding in the URL (in fact, we recommend using UTF-8 wherever possible) and remember to escape the URLs properly when linking to them.

You can target your website or parts of it to users in a single specific country that speaks a specific language. This can improve your page rankings in the target country, but at the expense of results in other locales or languages.

To geotarget your site

*[Content truncated]*

---

## Fix Search-related JavaScript problems

**URL:** https://developers.google.com/search/docs/guides/fix-search-javascript

**Contents:**
- Fix Search-related JavaScript problems

This guide helps you identify and fix JavaScript issues that may be blocking your page, or specific content on JavaScript powered pages, from showing up in Google Search. While Google Search does run JavaScript, there are some differences and limitations that you need to account for when designing your pages and applications to accommodate how crawlers access and render your content. Our guide on JavaScript SEO basics has more information on how you can optimize your JavaScript site for Google Search.

Googlebot is designed to be a good citizen of the web. Crawling is its main priority, while making sure it doesn't degrade the experience of users visiting the site. Googlebot and its Web Rendering Service (WRS) component continuously analyze and identify resources that don't contribute to essential page content and may not fetch such resources. For example, reporting and error requests that don't contribute to essential page content, and other similar types of requests are unused or unnecessary to extract essential page content. Client-side analytics may not provide a full or accurate representation of Googlebot and WRS activity on your site. Use the crawl stats report in Google Search Console to monitor Googlebot and WRS activity and feedback on your site.

If you suspect that JavaScript issues might be blocking your page, or specific content on JavaScript powered pages, from showing up in Google Search, follow these steps. If you're not sure if JavaScript is the main cause, follow our general debugging guide to determine the specific issue.

Optionally, we also recommend collecting and auditing JavaScript errors encountered by users, including Googlebot, on your site to identify potential issues that may affect how content is rendered. Here's an example that shows how to log JavaScript errors that are logged in the global onerror handler. Note that some types of JavaScript errors, such as a parse error, cannot be logged with this method.

When a SPA is using client-side JavaScript to handle errors they often report a 200 HTTP status code instead of the appropriate status code. This can lead to error pages being indexed and possibly shown in search results.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last upd

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
window.addEventListener('error', function(e) {
    var errorText = [
        e.message,
        'URL: ' + e.filename,
        'Line: ' + e.lineno + ', Column: ' + e.colno,
        'Stack: ' + (e.error && e.error.stack || '(no stack trace)')
    ].join('\n');

    // Example: log errors as visual output into the host page.
    // Note: you probably don't want to show such errors to users, or
    //       have the errors get indexed by Googlebot; however, it may
    //       be a useful feature while actively debugging the page.
    var DOM_ID = 'rendering-debug-pre';
    if (!document.getElemen
...
```

Example 2 (javascript):
```javascript
fetch(`https://api.kitten.club/cats/${id}`)
 .then(res => res.json())
 .then((cat) => {
   if (!cat.exists) {
     // redirect to page that gives a 404
     window.location.href = '/not-found';
   }
 });
```

Example 3 (javascript):
```javascript
fetch(`https://api.kitten.club/cats/${id}`)
 .then(res => res.json())
 .then((cat) => {
   if (!cat.exists) {
     const metaRobots = document.createElement('meta');
     metaRobots.name = 'robots';
     metaRobots.content = 'noindex';
     document.head.appendChild(metaRobots);
   }
 });
```

---
