# Google-Search-Docs - Crawling

**Pages:** 44

---

## Link best practices for Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/links-crawlable#write-good-anchor-text

**Contents:**
- Link best practices for Google
- Make your links crawlable
- Anchor text placement
- Write good anchor text
- Internal links: cross-reference your own content
- External links: link to other sites

Google uses links as a signal when determining the relevancy of pages and to find new pages to crawl. Learn how to make your links crawlable so that Google can find other pages on your site via the links on your page, and how to improve your anchor text so that it's easier for people and Google to make sense of your content.

Generally, Google can only crawl your link if it's an <a> HTML element (also known as anchor element) with an href attribute. Most links in other formats won't be parsed and extracted by Google's crawlers. Google can't reliably extract URLs from <a> elements that don't have an href attribute or other tags that perform as links because of script events. Here are examples of links that Google can and can't parse:

Recommended (Google can parse)

Not recommended (but Google may still attempt to parse this):

Make sure that the URL in your <a> element resolves into an actual web address (meaning, it resembles a URI) that Google crawlers can send requests to, for example:

Recommended (Google can resolve):

Not recommended (but Google may still attempt to resolve this):

Anchor text (also known as link text) is the visible text of a link. This text tells people and Google something about the page you're linking to. Place anchor text between <a> elements that Google can crawl.

Bad (empty link text):

As a fallback, Google can use the title attribute as anchor text if the <a> element is for some reason empty.

For images as links, Google uses the alt attribute of the img element as anchor text, so be sure to add descriptive alt text to your images:

Bad (empty alt text and empty link text):

If you are using JavaScript to insert anchor text, use the URL Inspection Tool to make sure it's present in the rendered HTML.

Good anchor text is descriptive, reasonably concise, and relevant to the page that it's on and to the page it links to. It provides context for the link, and sets the expectation for your readers. The better your anchor text, the easier it is for people to navigate your site and for Google to understand what the page you're linking to is about.

Better (more descriptive):

Better (more concise):

Write as naturally as possible, and resist the urge to cram every keyword that's related to the page that you're linking to (remember, keyword stuffing is a violation of our spam policies). Ask yourself, does the reader need these keywords to understand the next page? If it feels like you're forcing keywords into the anchor text, then 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<a href="https://example.com">
```

Example 2 (unknown):
```unknown
<a href="/products/category/shoes">
```

Example 3 (unknown):
```unknown
<a href="./products/category/shoes">
```

Example 4 (unknown):
```unknown
<a href="/products/category/shoes" onclick="javascript:goTo('shoes')">
```

---

## Mobile site and mobile-first indexing best practices

**URL:** https://developers.google.com/search/docs/crawling-indexing/mobile

**Contents:**
- Mobile site and mobile-first indexing best practices
- Create a mobile-friendly site
- Make sure that Google can access and render your content
- Make sure that content is the same on desktop and mobile
- Check your structured data
- Put the same metadata on both versions of your site
- Check the placement of your ads
- Check visual content
  - Check your images
  - Check your videos

Google uses the mobile version of a site's content, crawled with the smartphone agent, for indexing and ranking. This is called mobile-first indexing.

While it's not required to have a mobile version of your pages to have your content included in Google's Search results, it is very strongly recommended. These best practices apply to mobile sites in general, and by definition to mobile-first indexing.

To make sure that your users have the best experience, follow the best practices detailed in this guide.

If you haven't already, create a mobile-friendly website so your users visiting your site through a mobile phone can have a stellar experience. There are three configurations you can choose from to create a mobile-friendly site:

The contents of this guide only apply to dynamic serving and separate URL configurations. In case of responsive design, the content and the metadata are the same on the mobile and desktop version of the pages.

Make sure that Google can access and render your mobile page content and resources.

Even with the equivalent content, differences in DOM or layout between desktop and mobile page can result in Google understanding the content differently. However having the same content on the desktop and mobile version ensures that the two versions can rank for the same keywords.

If you have structured data on your site, make sure that it's present on both versions of your site. Here are some specific things to check:

Make sure that the title element and the meta description are equivalent across both versions of your site.

Don't let ads harm your mobile page ranking. Follow the Better Ads Standard when displaying ads on mobile devices. For example, ads at the top of the page can take up too much room on a mobile device, which is a bad user experience

Make sure that the images on your mobile site follow the image best practices. In particular, we recommend that you:

Make sure that the videos on your mobile site follow the video best practices. In particular, we recommend that you:

If your site has separate URLs for the desktop and mobile versions of a page (also known as m-dot), we recommend the following additional best practices:

Check hreflang links on separate URLs. When you use rel=hreflang link elements for internationalization, link between mobile and desktop URLs separately. Your mobile URLs' hreflang must point to mobile URLs, and similarly desktop URL hreflang must point to desktop URLs.

Here's an example of hreflang f

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<link rel="canonical" href="https://example.com/">
<link rel="alternate" hreflang="es" href="https://m.example.com/es/">
<link rel="alternate" hreflang="fr" href="https://m.example.com/fr/">
<link rel="alternate" hreflang="de" href="https://m.example.com/de/">
<link rel="alternate" hreflang="th" href="https://m.example.com/th/">
```

Example 2 (unknown):
```unknown
<link rel="canonical" href="https://example.com/">
<link rel="alternate" media="only screen and (max-width: 640px)" href="https://m.example.com/">
<link rel="alternate" hreflang="es" href="https://example.com/es/">
<link rel="alternate" hreflang="fr" href="https://example.com/fr/">
<link rel="alternate" hreflang="de" href="https://example.com/de/">
<link rel="alternate" hreflang="th" href="https://example.com/th/">
```

Example 3 (unknown):
```unknown
<link rel="canonical" href="https://example.com/">
```

Example 4 (unknown):
```unknown
<link rel="canonical" href="https://example.com/">
<link rel="alternate" media="only screen and (max-width: 640px)" href="https://m.example.com/">
```

---

## Control what you share with Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/control-what-you-share#how-to-block-content

**Contents:**
- Control what you share with Google
- How to block content
  - Remove the content from your site
  - Password-protect your files
  - Disallow crawling with robots.txt
- Remove existing content from Google

Google supports a variety of ways that allows site owners control what shows up in Google's search results. While most people focus on getting their pages indexed, sometimes it's important to do the opposite: prevent content from appearing in Search. There are a few reasons you might want to hide content from Google:

Here are the main ways to block content from appearing in Google:

Applicable: all content types

Removing content from your site is the best way to ensure that it won't appear in Google Search and anywhere else on the Internet.

Applicable: all content types

If you have confidential or private content on your site, you need to password protect it to ensure only authorized users can access it. This will also prevent that content from appearing in Google Search, or if it already appears, it will eventually remove that content from our search results.

Applicable: all content types

The noindex robots meta tag is a rule that tells Google not to index your content or let it appear in Google search results. Your content can still be linked to and visited through other web pages, or directly visited by users with a link, but the content will not appear in Google search results.

Applicable: images and video

Google only indexes images and videos that Googlebot is allowed to crawl. To prevent Googlebot from accessing your media files, use robots.txt rules to block the files.

Applicable: web pages

You can tell Google not to include content from your site in specific Google properties, such as Google Shopping, Google Hotels, and vacation rentals.

If the content hosted on your site is already appearing in Google, you can request the removal of those search results. Learn how to remove a page hosted on your site from Google.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-03-07 UTC.

---

## Managing crawling of faceted navigation URLs

**URL:** https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation

**Contents:**
- Managing crawling of faceted navigation URLs
- Prevent crawling of faceted navigation URLs
- Ensure the faceted navigation URLs are optimal for the web

Faceted navigation is a common feature of websites that allows its visitors to change how items (for example, products, articles, or events) are displayed on a page. It's a popular and useful feature, however its most common implementation, which is based on URL parameters, can generate infinite URL spaces which harms the website in a couple ways:

A typical faceted navigation URL may contain various parameters in the query string related to the properties of items they filter for. For example:

Changing any of the URL parameters products, color, and size would show a different set of items on the underlying page. This often means a very large number of possible combinations of filters, which translates to a very large number of possible URLs. To save your resources, we recommend dealing with these URLs one of the following ways:

If you want to save server resources and you don't need your faceted navigation URLs to show up in Google Search, you can prevent crawling of these URLs with one of the following ways.

Other ways to signal a preference of which faceted navigation URLs (not) to crawl is using rel="canonical" link element and the rel="nofollow" anchor attribute. However, these methods are generally less effective in the long term than the previously mentioned methods.

If you need your faceted navigation URLs to be potentially crawled and indexed, ensure you're following these best practices to minimize the negative effects of crawling the large number of potential URLs on your site:

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-02-04 UTC.

**Examples:**

Example 1 (unknown):
```unknown
https://example.com/items.shtm?products=fish&color=radioactive_green&size=tiny
```

Example 2 (unknown):
```unknown
user-agent: Googlebot
disallow: /*?*products=
disallow: /*?*color=
disallow: /*?*size=
allow: /*?products=all$
```

Example 3 (unknown):
```unknown
https://example.com/items.shtm#products=fish&color=radioactive_green&size=tiny
```

---

## Learn about sitemaps

**URL:** https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview

**Contents:**
- Learn about sitemaps
- Do I need a sitemap?
- Build a sitemap

A sitemap is a file where you provide information about the pages, videos, and other files on your site, and the relationships between them. Search engines like Google read this file to crawl your site more efficiently. A sitemap tells search engines which pages and files you think are important in your site, and also provides valuable information about these files. For example, when the page was last updated and any alternate language versions of the page.

You can use a sitemap to provide information about specific types of content on your pages, including video, image, and news content. For example:

If your site's pages are properly linked, Google can usually discover most of your site. Proper linking means that all pages that you deem important can be reached through some form of navigation, be that your site's menu or links that you placed on pages. Even so, a sitemap can improve the crawling of larger or more complex sites, or more specialized files.

You might need a sitemap if:

You might not need a sitemap if:

If you decided that you need a sitemap, learn more about how to create one.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-03-06 UTC.

---

## Ask Google to recrawl your URLs

**URL:** https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl#use-the-url-inspection-tool-just-a-few-urls

**Contents:**
- Ask Google to recrawl your URLs
- Use the URL Inspection tool (just a few URLs)
- Submit a sitemap (many URLs at once)

If you've recently added or made changes to a page on your site, you can request that Google re-index your page using any of the methods listed here. You can't request indexing for URLs that you don't manage.

Crawling can take anywhere from a few days to a few weeks. Be patient and monitor progress using either the Index Status report or the URL Inspection tool.

To request a crawl of individual URLs, use the URL Inspection tool. You must be an owner or full user of the Search Console property to be able to request indexing in the URL Inspection tool.

Keep in mind that there's a quota for submitting individual URLs and requesting a recrawl multiple times for the same URL won't get it crawled any faster.

If you have large numbers of URLs, submit a sitemap. A sitemap is an important way for Google to discover URLs on your site. It can be very helpful if you just launched your site or recently performed a site move. A sitemap can also include additional metadata about alternate language versions, video, image, or news-specific pages. Learn how to create and submit a sitemap.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-03-06 UTC.

---

## Control what you share with Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/control-what-you-share

**Contents:**
- Control what you share with Google
- How to block content
  - Remove the content from your site
  - Password-protect your files
  - Disallow crawling with robots.txt
- Remove existing content from Google

Google supports a variety of ways that allows site owners control what shows up in Google's search results. While most people focus on getting their pages indexed, sometimes it's important to do the opposite: prevent content from appearing in Search. There are a few reasons you might want to hide content from Google:

Here are the main ways to block content from appearing in Google:

Applicable: all content types

Removing content from your site is the best way to ensure that it won't appear in Google Search and anywhere else on the Internet.

Applicable: all content types

If you have confidential or private content on your site, you need to password protect it to ensure only authorized users can access it. This will also prevent that content from appearing in Google Search, or if it already appears, it will eventually remove that content from our search results.

Applicable: all content types

The noindex robots meta tag is a rule that tells Google not to index your content or let it appear in Google search results. Your content can still be linked to and visited through other web pages, or directly visited by users with a link, but the content will not appear in Google search results.

Applicable: images and video

Google only indexes images and videos that Googlebot is allowed to crawl. To prevent Googlebot from accessing your media files, use robots.txt rules to block the files.

Applicable: web pages

You can tell Google not to include content from your site in specific Google properties, such as Google Shopping, Google Hotels, and vacation rentals.

If the content hosted on your site is already appearing in Google, you can request the removal of those search results. Learn how to remove a page hosted on your site from Google.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-03-07 UTC.

---

## Qualify your outbound links to Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links#sponsored

**Contents:**
- Qualify your outbound links to Google
  - rel="sponsored"
  - rel="ugc"
  - rel="nofollow"
  - Multiple values

For certain links on your site, you might want to tell Google your relationship with the linked page. In order to do that, use one of the following rel attribute values in the <a> tag.

For regular links that you expect Google to fetch and parse without any qualifications, you don't need to add a rel attribute. For example:

For other links, use one or more of the following values:

Mark links that are advertisements or paid placements (commonly called paid links) with the sponsored value. Read more about Google's stance on paid links.

We recommend marking user-generated content (UGC) links, such as comments and forum posts, with the ugc value.

If you want to recognize and reward trustworthy contributors, you might remove this attribute from links posted by members or users who have consistently made high-quality contributions over time. Read more about how to prevent user-generated spam on your site and platform.

Use the nofollow value when other values don't apply, and you'd rather Google not associate your site with, or crawl the linked page from, your site. For links within your own site, use the robots.txt disallow rule.

You may specify multiple rel values as a space- or comma-separated list. Examples:

Links marked with these rel attributes will generally not be followed. Remember that the linked pages may be found through other means, such as sitemaps or links from other sites, and thus they may still be crawled. These rel attributes are used only in <a> elements that Google can crawl, except nofollow, which is also available as robots meta tag.

If you need to prevent Google from fetching a link to a page on your own site, use the robots.txt disallow rule.

To prevent Google from indexing a page, allow crawling and use the noindex robots rule.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-08-28 UTC.

**Examples:**

Example 1 (unknown):
```unknown
<p>My favorite horse is the <a href="https://horses.example.com/Palomino">palomino</a>.</p>
```

Example 2 (unknown):
```unknown
<a rel="sponsored" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

Example 3 (unknown):
```unknown
<a rel="ugc" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

Example 4 (unknown):
```unknown
<a rel="nofollow" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

---

## How HTTP status codes, and network and DNS errors affect Google Search

**URL:** https://developers.google.com/search/docs/crawling-indexing/http-network-errors#http-status-codes

**Contents:**
- How HTTP status codes, and network and DNS errors affect Google Search
- HTTP status codes
  - 2xx (success)
  - 3xx (redirection)
  - 4xx (client errors)
  - 5xx (server errors)
  - soft 404 errors
    - Fix soft 404 errors
      - The page and content are no longer available
      - The page or content is now somewhere else

This page describes how different HTTP status codes, network errors, and DNS errors affect Google Search. We cover the top 20 status codes that Googlebot encountered on the web, and the most prominent network and DNS errors. More exotic status codes, such as 418 (I'm a teapot), aren't covered. All issues mentioned on this page generate a corresponding error or warning in Search Console's Page Indexing report.

HTTP status codes are generated by the server that's hosting the site when it responds to a request made by a client, for example a browser or a crawler. Every HTTP status code has a different meaning, but often the outcome of the request is the same. For example, there are multiple status codes that signal redirection, but their outcome is the same.

Search Console generates error messages for status codes in the 4xx–5xx range, and for failed redirections (3xx). If the server responded with a 2xx status code, the content received in the response may be considered for indexing.

The following table contains the most encountered HTTP status codes by Googlebot and an explanation how Google handles each status code.

Google considers the content for indexing. If the content suggests an error, for example an empty page or an error message, Search Console will show a soft 404 error.

Google passes on the content to the indexing pipeline. The indexing systems may index the content, but that's not guaranteed.

Googlebot waits for the content for a limited time, then passes on whatever it received to the indexing pipeline. The timeout is user agent dependent, for example Googlebot Smartphone may have a different timeout than Googlebot Image.

Googlebot signals the indexing pipeline that it received no content. Search Console may show a soft 404 error in the site's Page Indexing report.

Googlebot follows up to 10 redirect hops. If the crawler doesn't receive content within 10 hops, Search Console will show a redirect error in the site's Page Indexing report. The number of hops Googlebot follows is user agent dependent; for example, Googlebot Smartphone may have a different value than Googlebot Image.

Any content Googlebot received from the redirecting URL is ignored, and the final target URL's content is considered for indexing. For robots.txt files, learn how Google handles a robots.txt that returns a 3xx status code.

Googlebot follows the redirect, and the indexing pipeline uses the redirect as a strong signal that the redirect target should be canonical

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
dig +nocmd example.com a +noall +answer
```

Example 2 (unknown):
```unknown
dig +nocmd www.example.com cname +noall +answer
```

Example 3 (unknown):
```unknown
dig +nocmd example.com ns +noall +answer
example.com.    86400  IN  NS  a.iana-servers.net.
example.com.    86400  IN  NS  b.iana-servers.net.
dig +nocmd @a.iana-servers.net example.com +noall +answer
example.com.    86400  IN  A  93.184.216.34
dig +nocmd @b.iana-servers.net example.com +noall +answer
...
```

---

## How to specify a canonical URL with rel="canonical" and other methods

**URL:** https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls#rel-canonical-link-method

**Contents:**
- How to specify a canonical URL with rel="canonical" and other methods
- Reasons to specify a canonical URL
- Best practices
- Comparison of canonicalization methods
- Use rel="canonical" link annotations
  - The rel="canonical" link element
  - The rel="canonical" HTTP header
- Use a sitemap
- Use redirects
- Other signals

To specify a canonical URL for duplicate or very similar pages to Google Search, you can indicate your preference using a number of methods. These are, in order of how strongly they can influence canonicalization:

Keep in mind that these methods can stack and thus become more effective when combined. This means that when you use two or more of the methods, that will increase the chance of your preferred canonical URL appearing in search results.

While we encourage you to use these methods, none of them are required; your site will likely do just fine without specifying a canonical preference. That's because if you don't specify a canonical URL, Google will identify which version of the URL is objectively the best version to show to users in Search.

While it's generally not critical to specify a canonical preference for your URLs, there are a number of reasons why you would want to explicitly tell Google about a canonical page in a set of duplicate or similar pages:

For all canonicalization methods, follow these best practices:

The following table compares the different canonicalization methods, highlighting their strengths and weaknesses when it comes to maintenance and efficacy in different scenarios.

Add a <link> element in the code for all duplicate pages, pointing to the canonical page.

Send a rel="canonical" header in your page response.

Specify your canonical pages in a sitemap.

Google supports explicit rel canonical link annotations as described in RFC 6596. rel="canonical" annotations that suggest alternate versions of a page are ignored; specifically, rel="canonical" annotations with hreflang, lang, media, and type attributes are not used for canonicalization. Instead, use the appropriate link annotations to specify alternate versions of a page; for example, link rel="alternate" hreflang for language and country annotations.

You can provide the rel="canonical" link annotations in two ways:

We recommend that you choose one of these and go with that; while supported, using both methods at the same time is more error prone (for example, you might provide one URL in the HTTP header, and another URL in the rel="canonical" link element).

A rel="canonical" link element (also known as a canonical element) is an element used in the head section of HTML to indicate that another page is representative of the content on the page.

Suppose you want https://example.com/dresses/green-dresses to be the canonical URL, even though a variety of URLs can 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<html>
<head>
<title>Explore the world of dresses</title>
<link rel="canonical" href="https://example.com/dresses/green-dresses" />
<!-- other elements -->
</head>
<!-- rest of the HTML -->
```

Example 2 (unknown):
```unknown
<html>
<head>
<title>Explore the world of dresses</title>
<link rel="alternate" media="only screen and (max-width: 640px)"  href="https://m.example.com/dresses/green-dresses">
<link rel="canonical" href="https://example.com/dresses/green-dresses" />
<!-- other elements -->
</head>
<!-- rest of the HTML -->
```

Example 3 (unknown):
```unknown
HTTP/1.1 200 OK
Content-Length: 19
...
Link: <https://www.example.com/downloads/white-paper.pdf>; rel="canonical"
...
```

---

## Googlebot

**URL:** https://developers.google.com/search/docs/crawling-indexing/googlebot

**Contents:**
- Googlebot
- How Googlebot accesses your site
- Blocking Googlebot from visiting your site
- Verifying Googlebot

Googlebot is the generic name for two types of web crawlers used by Google Search:

You can identify the subtype of Googlebot by looking at the HTTP user-agent request header in the request. However, both crawler types obey the same product token (user agent token) in robots.txt, and so you cannot selectively target either Googlebot Smartphone or Googlebot Desktop using robots.txt.

For most sites Google Search primarily indexes the mobile version of the content. As such the majority of Googlebot crawl requests will be made using the mobile crawler, and a minority using the desktop crawler.

For most sites, Googlebot shouldn't access your site more than once every few seconds on average. However, due to delays it's possible that the rate will appear to be slightly higher over short periods. If your site is having trouble keeping up with Google's crawling requests, you can reduce the crawl rate.

Googlebot can crawl the first 15MB of an HTML file or supported text-based file. Each resource referenced in the HTML such as CSS and JavaScript is fetched separately, and each fetch is bound by the same file size limit. After the first 15MB of the file, Googlebot stops crawling and only sends the first 15MB of the file for indexing consideration. The file size limit is applied on the uncompressed data. Other Google crawlers, for example Googlebot Video and Googlebot Image, may have different limits.

When crawling from IP addresses in the US, the timezone of Googlebot is Pacific Time.

Other technical properties of Googlebot are described in the overview of Google's crawlers.

Googlebot discovers new URLs to crawl primarily from links embedded in previously crawled pages. It's almost impossible to keep a site secret by not publishing links to it. For example, as soon as someone clicks a link from your "secret" site to another site, your "secret" site URL may appear in the referrer tag and can be stored and published by the other site in its referrer log.

If you want to prevent Googlebot from crawling content on your site, you have a number of options. Remember there's a difference between crawling and indexing; blocking Googlebot from crawling a page doesn't prevent the URL of the page from appearing in search results:

Blocking Googlebot affects Google Search (including Discover and all Google Search features), as well as other products such as Google Images, Google Video, and Google News.

Before you decide to block Googlebot, be aware that the HTTP user-agent 

*[Content truncated]*

---

## Keep redacted information out of Google Search

**URL:** https://developers.google.com/search/docs/crawling-indexing/keep-redacted-information-out

**Contents:**
- Keep redacted information out of Google Search
- Edit and export images before embedding them
- Edit or remove unwanted text before moving to a public file format
- What to do if unredacted or improperly redacted documents are indexed in Search

When publishing documents and images on the web, you may unintentionally publish information beyond what is immediately visible to the human eye. In particular, information that you might not see, or that was intended to be redacted, might be included in some document formats and visible to search engines.

Because search engines index public material on the web, including images, content that is not completely redacted can potentially be findable in search engines. Assistive technologies like screen readers can make this seemingly "hidden" content more easily accessible, and common image understanding techniques like optical character recognition (OCR) similarly make it possible to search for this content.

Even though putting text in a tiny font, using a font color that's the same as the background the text is on, or covering text with an image may make something invisible to the human eye, these methods don't actually redact material in a way that prevents search engines from indexing it and making it findable.

Similarly, some document types include information in various ways that aren't immediately visible. They might include the document's change history, allowing users to see text that has been redacted or altered. They might retain the full versions of images that contain cropped or redacted information. There might also be metadata that's included in a file, which is not immediately visible, that may list the names of people who accessed or edited the file.

All of this information can remain even when a document is exported or converted from one format to another. If you need to remove information from a file, it's critical that the information is removed completely from the file before that file is made public.

Here are some best practices for how to appropriately redact information from documents that you don't want to be indexed and made discoverable via Google Search.

Google Search lists images that it finds across the web, both those that are on web pages or those that are embedded into various document formats. Embedded images are sometimes edited using only the containing document's editing tools. This can cause this redaction to fail when an image is indexed apart from the document. That is why it's best to edit images before embedding them into a document, not after. In particular:

After following the suggestions in this document, export or save the updated images as non-vector or flattened image file formats such as PNG or WEBP. Thi

*[Content truncated]*

---

## Link best practices for Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/links-crawlable#crawlable-links

**Contents:**
- Link best practices for Google
- Make your links crawlable
- Anchor text placement
- Write good anchor text
- Internal links: cross-reference your own content
- External links: link to other sites

Google uses links as a signal when determining the relevancy of pages and to find new pages to crawl. Learn how to make your links crawlable so that Google can find other pages on your site via the links on your page, and how to improve your anchor text so that it's easier for people and Google to make sense of your content.

Generally, Google can only crawl your link if it's an <a> HTML element (also known as anchor element) with an href attribute. Most links in other formats won't be parsed and extracted by Google's crawlers. Google can't reliably extract URLs from <a> elements that don't have an href attribute or other tags that perform as links because of script events. Here are examples of links that Google can and can't parse:

Recommended (Google can parse)

Not recommended (but Google may still attempt to parse this):

Make sure that the URL in your <a> element resolves into an actual web address (meaning, it resembles a URI) that Google crawlers can send requests to, for example:

Recommended (Google can resolve):

Not recommended (but Google may still attempt to resolve this):

Anchor text (also known as link text) is the visible text of a link. This text tells people and Google something about the page you're linking to. Place anchor text between <a> elements that Google can crawl.

Bad (empty link text):

As a fallback, Google can use the title attribute as anchor text if the <a> element is for some reason empty.

For images as links, Google uses the alt attribute of the img element as anchor text, so be sure to add descriptive alt text to your images:

Bad (empty alt text and empty link text):

If you are using JavaScript to insert anchor text, use the URL Inspection Tool to make sure it's present in the rendered HTML.

Good anchor text is descriptive, reasonably concise, and relevant to the page that it's on and to the page it links to. It provides context for the link, and sets the expectation for your readers. The better your anchor text, the easier it is for people to navigate your site and for Google to understand what the page you're linking to is about.

Better (more descriptive):

Better (more concise):

Write as naturally as possible, and resist the urge to cram every keyword that's related to the page that you're linking to (remember, keyword stuffing is a violation of our spam policies). Ask yourself, does the reader need these keywords to understand the next page? If it feels like you're forcing keywords into the anchor text, then 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<a href="https://example.com">
```

Example 2 (unknown):
```unknown
<a href="/products/category/shoes">
```

Example 3 (unknown):
```unknown
<a href="./products/category/shoes">
```

Example 4 (unknown):
```unknown
<a href="/products/category/shoes" onclick="javascript:goTo('shoes')">
```

---

## Introduction to robots.txt

**URL:** https://developers.google.com/search/docs/crawling-indexing/robots/intro

**Contents:**
- Introduction to robots.txt
- What is a robots.txt file used for?
- Understand the limitations of a robots.txt file
- Create or update a robots.txt file

A robots.txt file tells search engine crawlers which URLs the crawler can access on your site. This is used mainly to avoid overloading your site with requests; it is not a mechanism for keeping a web page out of Google. To keep a web page out of Google, block indexing with noindex or password-protect the page.

If you use a CMS, such as Wix or Blogger, you might not need to (or be able to) edit your robots.txt file directly. Instead, your CMS might expose a search settings page or some other mechanism to tell search engines whether or not to crawl your page.

If you want to hide or unhide one of your pages from search engines, search for instructions about modifying your page visibility in search engines on your CMS (for example, search for "wix hide page from search engines").

A robots.txt file is used primarily to manage crawler traffic to your site, and usually to keep a file off Google, depending on the file type:

You can use a robots.txt file for web pages (HTML, PDF, or other non-media formats that Google can read), to manage crawling traffic if you think your server will be overwhelmed by requests from Google's crawler, or to avoid crawling unimportant or similar pages on your site.

Warning: Don't use a robots.txt file as a means to hide your web pages (including PDFs and other text-based formats supported by Google) from Google search results.

If other pages point to your page with descriptive text, Google could still index the URL without visiting the page. If you want to block your page from search results, use another method such as password protection or noindex.

If your web page is blocked with a robots.txt file, its URL can still appear in search results, but the search result will not have a description. Image files, video files, PDFs, and other non-HTML files embedded in the blocked page will be excluded from crawling, too, unless they're referenced by other pages that are allowed for crawling. If you see this search result for your page and want to fix it, remove the robots.txt entry blocking the page. If you want to hide the page completely from Search, use another method.

Use a robots.txt file to manage crawl traffic, and also to prevent image, video, and audio files from appearing in Google search results. This won't prevent other pages or users from linking to your image, video, or audio file.

Before you create or edit a robots.txt file, you should know the limits of this URL blocking method. Depending on your goals and situati

*[Content truncated]*

---

## Remove images hosted on your site from search results

**URL:** https://developers.google.com/search/docs/crawling-indexing/prevent-images-on-your-page

**Contents:**
- Remove images hosted on your site from search results
- For emergency image removal
- For non-emergency image removal
  - Remove images using robots.txt rules
  - Remove images with the noindex X-Robots-Tag HTTP header
- How do I remove images from properties that I don't own?

To quickly remove images hosted on your site from Google's search results, use the Removals tool. Keep in mind that unless you also remove the images from your site or otherwise block the images as described in the non-emergency image removal section, the images may resurface in Google's search results once the removal request expires.

There are two ways to remove images from your site from Google's search results:

The two methods have the same effect, choose the method that is more convenient for your site. Keep in mind that Googlebot has to crawl the URLs to extract the HTTP headers, so implementing both methods at the same time doesn't make sense.

If you don't have access to the site that's hosting your images (for example a CDN) or your CMS doesn't provide a way to block images with the noindex X-Robots-Tag HTTP header or robots.txt, you might need to delete the images altogether from your site.

To prevent images from your site appearing in Google's search results, add a robots.txt file to the root of the site that hosts the image, for example https://yoursite.example.com/robots.txt. While it takes longer to remove an image from Google's search results using robots.txt rules than it does to use the Removals tool, it gives you more flexibility and control through the use of wildcards or subpath blocking. It also applies to all search engines, whereas the Removals tool only applies to Google.

For example, if you want Google to exclude the dogs.jpg image that appears on your site at yoursite.example.com/images/dogs.jpg, add the following to your robots.txt file:

The next time Google crawls the dogs.jpg image, we'll see this rule and drop your image from our search results.

Rules may include special characters for more flexibility and control. Specifically, the * character matches any sequence of characters which lets you to match multiple image paths with one rule.

To remove multiple images on your site from Google's index, add a disallow rule for each image, or if the images share a common pattern such as a suffix in the filename, use a the * character in the filename. For example:

To remove all the images on your site from our index, place the following rule in your robots.txt file:

To remove all files of a specific file type (for example, to include .jpg but not .gif images), you'd use the following robots.txt entry:

By specifying Googlebot-Image as the User-agent, the images will be excluded from Google Images. If you would like to exclude 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
User-agent: Googlebot-Image
Disallow: /images/dogs.jpg
```

Example 2 (unknown):
```unknown
User-agent: Googlebot-Image
# Repeated 'disallow' rules for each image:
Disallow: /images/dogs.jpg
Disallow: /images/cats.jpg
Disallow: /images/llamas.jpg

# Wildcard character in the filename for
# images that share a common suffix. For example,
#   animal-picture-UNICORN.jpg and
#   animal-picture-SQUIRREL.jpg
# in the "images" directory
# will be matched by this pattern.
Disallow: /images/animal-picture-*.jpg
```

Example 3 (unknown):
```unknown
User-agent: Googlebot-Image
Disallow: /
```

Example 4 (unknown):
```unknown
User-agent: Googlebot-Image
Disallow: /*.gif$
```

---

## Overview of Google crawlers and fetchers (user agents)

**URL:** https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers

**Contents:**
- Overview of Google crawlers and fetchers (user agents)
- Technical properties of Google's crawlers and fetchers
  - Supported transfer protocols
  - Supported content encodings
  - Crawl rate and host load
  - HTTP Caching
    - ETag and If-None-Match
    - Last-Modified and If-Modified-Since
- Verifying Google's crawlers and fetchers

Google uses crawlers and fetchers to perform actions for its products, either automatically or triggered by user request. Crawler (sometimes also called a "robot" or "spider") is a generic term for any program that is used to automatically discover and scan websites. Fetchers act as a program like wget that typically make a single request on behalf of a user. Google's clients fall into three categories:

Google's crawlers and fetchers are designed to be run simultaneously by thousands of machines to improve performance and scale as the web grows. To optimize bandwidth usage, these clients are distributed across many datacenters across the world so they're located near the sites that they might access. Therefore, your logs may show visits from several IP addresses. Google egresses primarily from IP addresses in the United States. In case Google detects that a site is blocking requests from the United States, it may attempt to crawl from IP addresses located in other countries.

Google's crawlers and fetchers support HTTP/1.1 and HTTP/2. The crawlers will use the protocol version that provides the best crawling performance and may switch protocols between crawling sessions depending on previous crawling statistics. The default protocol version used by Google's crawlers is HTTP/1.1; crawling over HTTP/2 may save computing resources (for example, CPU, RAM) for your site and Googlebot, but otherwise there's no Google-product specific benefit to the site (for example, no ranking boost in Google Search). To opt out from crawling over HTTP/2, instruct the server that's hosting your site to respond with a 421 HTTP status code when Google attempts to access your site over HTTP/2. If that's not feasible, you can send a message to the Crawling team (however this solution is temporary).

Google's crawler infrastructure also supports crawling through FTP (as defined by RFC959 and its updates) and FTPS (as defined by RFC4217 and its updates), however crawling through these protocols is rare.

Google's crawlers and fetchers support the following content encodings (compressions): gzip, deflate, and Brotli (br). The content encodings supported by each Google user agent is advertised in the Accept-Encoding header of each request they make. For example, Accept-Encoding: gzip, deflate, br.

Our goal is to crawl as many pages from your site as we can on each visit without overwhelming your server. If your site is having trouble keeping up with Google's crawling requests, you ca

*[Content truncated]*

---

## How to move a site

**URL:** https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes

**Contents:**
- How to move a site
- Overview
- General best practices for site moves
- Prepare the new site
- Prepare URL mapping
  - Determine your old URLs
  - Create a mapping of old to new URLs
  - Update all URL details on the new site
  - Plan your redirect strategy
- Start the site move

This document describes how to change the URLs of existing pages on your site while minimizing negative impact on your Google Search results. Examples of this kind of site move include:

The details of site preparation vary for each site move, but typically you'll do one or more of the following:

Set up a robots.txt for your new site and make sure the rules in the new site's robots.txt file correctly reflect the parts you want blocked from crawling.

Note that some site owners block all crawling while in development. If you follow this strategy, make sure you prepare what the robots.txt file should look like once the site move starts. Likewise, if you use noindex rules during development, prepare a list of URLs from which you'll remove the noindex rules when you start the site move.

Provide errors for deleted or merged content if you're not moving to the new site all your old content, make sure those URLs correctly return an HTTP 404 or 410 error response code on the new site.

Ensure correct Search Console settings that may help with the site move.

If you haven't already, verify both the old and new sites in Search Console. Be sure to verify all variants of both the old and new sites. For example, verify www.example.com and example.com, and include both the HTTPS and HTTP site variants if you use HTTPS URLs. Do this for both old and new sites.

Review the Search Console verification

Make sure your Search Console verification will continue to work after the site move. If you're using a different method of verification, keep in mind that verification tokens may be different when the URL changes.

If you're using the HTML file method to verify ownership of your site in Search Console, make sure you don't forget to include your current verification file in your new copy of the site.

Likewise, if you verify ownership with an include file that references the meta tag or Google Analytics to verify ownership, ensure the new CMS copy includes these as well.

Review any configured settings in Search Console that you may have made for the old site, and make sure the new site's settings are updated to reflect those changes as well. For example:

Clean up your recently purchased domain; you'll want to make sure it's clean of any outstanding issues from the previous owner. Check the following settings:

Use web analytics to analyze usage on both the old and new sites. Web analytics software can help with this. Typically, web analytics configuration consists of a p

*[Content truncated]*

---

## Robots meta tag, data-nosnippet, and X-Robots-Tag specifications

**URL:** https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag

**Contents:**
- Robots meta tag, data-nosnippet, and X-Robots-Tag specifications
- Using the robots meta tag
- Using the X-Robots-Tag HTTP header
- Valid indexing and serving rules
  - all
  - noindex
  - nofollow
  - none
  - nosnippet
  - indexifembedded

This document details how the page- and text-level settings can be used to adjust how Google presents your content in search results. You can specify page-level settings by including a meta tag on HTML pages or in an HTTP header. You can specify text-level settings with the data-nosnippet attribute on HTML elements within a page.

Keep in mind that these settings can be read and followed only if crawlers are allowed to access the pages that include these settings.

The <meta name="robots" content="noindex"> rule applies to search engine crawlers. To block non-search crawlers, such as AdsBot-Google, you might need to add rules targeted to the specific crawler (for example, <meta name="AdsBot-Google" content="noindex">).

The robots meta tag lets you use a granular, page-specific approach to controlling how an individual HTML page should be indexed and served to users in Google Search results. Place the robots meta tag in the <head> section of a given page, like this:

If you use a CMS, such as Wix, WordPress, or Blogger, you might not be able to edit your HTML directly, or you might prefer not to. Instead, your CMS might have a search engine settings page or some other mechanism to tell search engines about meta tags.

If you want to add a meta tag to your website, search for instructions about modifying the <head> of your page on your CMS (for example, search for "wix add meta tags").

In this example, the robots meta tag instructs search engines not to show the page in search results. The value of the name attribute (robots) specifies that the rule applies to all crawlers. Both the name and the content attributes are case-insensitive. To address a specific crawler, replace the robots value of the name attribute with the user agent token of the crawler that you are addressing. Google supports two user agent tokens in the robots meta tag; other values are ignored:

For example, to instruct Google specifically not to show a snippet in its search results, you can specify googlebot as the name of the meta tag:

To show a full snippet in Google's web search results, but no snippet in Google News, specify googlebot-news as the name of the meta tag:

To specify multiple crawlers individually, use multiple robots meta tags:

To block indexing of non-HTML resources, such as PDF files, video files, or image files, use the X-Robots-Tag response header instead.

The X-Robots-Tag can be used as an element of the HTTP header response for a given URL. Any rule that can b

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<!DOCTYPE html>
<html><head>
  <meta name="robots" content="noindex">
  (…)
</head>
<body>(…)</body>
</html>
```

Example 2 (unknown):
```unknown
<meta name="googlebot" content="nosnippet">
```

Example 3 (unknown):
```unknown
<meta name="googlebot-news" content="nosnippet">
```

Example 4 (unknown):
```unknown
<meta name="googlebot" content="notranslate">
<meta name="googlebot-news" content="nosnippet">
```

---

## Remove a page hosted on your site from Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/remove-information

**Contents:**
- Remove a page hosted on your site from Google
- Make your removal permanent
- Remove an image from search results
- Remove information from other Google properties
- How do I remove content from a site that I don't own?

For quick removals, use the Removals tool to remove a page hosted on your site from Google's search results within a day.

Protect or remove all variations of the URL for the content that you want to remove. In many cases, different URLs can point to the same page. For example: example.com/puppies, example.com/PUPPIES, and example.com/petchooser?pet=puppies. Learn how to find the right URL to block.

Requests made in the Removals tool last for about 6 months. To permanently block a page from Google Search results, take one of the following actions:

Learn how to remove images that are hosted on your site from search results.

To remove content from other Google properties, search the help documentation for your product to learn how to remove it. For example:

See the help article on how to Remove your personal information from Google.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-02-04 UTC.

---

## How to move a site

**URL:** https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes#troubleshooting

**Contents:**
- How to move a site
- Overview
- General best practices for site moves
- Prepare the new site
- Prepare URL mapping
  - Determine your old URLs
  - Create a mapping of old to new URLs
  - Update all URL details on the new site
  - Plan your redirect strategy
- Start the site move

This document describes how to change the URLs of existing pages on your site while minimizing negative impact on your Google Search results. Examples of this kind of site move include:

The details of site preparation vary for each site move, but typically you'll do one or more of the following:

Set up a robots.txt for your new site and make sure the rules in the new site's robots.txt file correctly reflect the parts you want blocked from crawling.

Note that some site owners block all crawling while in development. If you follow this strategy, make sure you prepare what the robots.txt file should look like once the site move starts. Likewise, if you use noindex rules during development, prepare a list of URLs from which you'll remove the noindex rules when you start the site move.

Provide errors for deleted or merged content if you're not moving to the new site all your old content, make sure those URLs correctly return an HTTP 404 or 410 error response code on the new site.

Ensure correct Search Console settings that may help with the site move.

If you haven't already, verify both the old and new sites in Search Console. Be sure to verify all variants of both the old and new sites. For example, verify www.example.com and example.com, and include both the HTTPS and HTTP site variants if you use HTTPS URLs. Do this for both old and new sites.

Review the Search Console verification

Make sure your Search Console verification will continue to work after the site move. If you're using a different method of verification, keep in mind that verification tokens may be different when the URL changes.

If you're using the HTML file method to verify ownership of your site in Search Console, make sure you don't forget to include your current verification file in your new copy of the site.

Likewise, if you verify ownership with an include file that references the meta tag or Google Analytics to verify ownership, ensure the new CMS copy includes these as well.

Review any configured settings in Search Console that you may have made for the old site, and make sure the new site's settings are updated to reflect those changes as well. For example:

Clean up your recently purchased domain; you'll want to make sure it's clean of any outstanding issues from the previous owner. Check the following settings:

Use web analytics to analyze usage on both the old and new sites. Web analytics software can help with this. Typically, web analytics configuration consists of a p

*[Content truncated]*

---

## What is canonicalization

**URL:** https://developers.google.com/search/docs/crawling-indexing/canonicalization

**Contents:**
- What is canonicalization
  - How Google indexes and chooses the canonical URL

Canonicalization is the process of selecting the representative –canonical– URL of a piece of content. Consequently, a canonical URL is the URL of a page that Google chose as the most representative from a set of duplicate pages. Often called deduplication, this process helps Google show only one version of the otherwise duplicate content in its search results.

There are many reasons why a site may have duplicate content:

Some duplicate content on a site is normal and it's not a violation of Google's spam policies. However, having the same content accessible through many different URLs can be a bad user experience (for example, people might wonder which is the right page, and whether there's a difference between the two) and it may make it harder for you to track how your content performs in search results.

When Google indexes a page, it determines the primary content (or centerpiece) of each page. If Google finds multiple pages that seem to be the same or the primary content very similar, it chooses the page that, based on the factors (or signals) the indexing process collected, is objectively the most complete and useful for search users, and marks it as canonical. The canonical page will be crawled most regularly; duplicates are crawled less frequently in order to reduce the crawling load on sites.

There are a handful of factors that play a role in canonicalization: whether the page is served over HTTP or HTTPS, redirects, presence of the URL in a sitemap, and rel="canonical" link annotations. You can indicate your preference to Google using these techniques, but Google may choose a different page as canonical than you do, for various reasons. That is, indicating a canonical preference is a hint, not a rule.

Different language versions of a single page are considered duplicates only if the primary content is in the same language (that is, if only the header, footer, and other non-critical text is translated, but the body remains the same, then the pages are considered to be duplicates). To learn more about setting up localized sites, see our documentation about managing multi-lingual and multi-regional sites.

Google uses the canonical page as the main source to evaluate content and quality. A Google Search result usually points to the canonical page, unless one of the duplicates is explicitly better suited for a search user. For example, the search result will probably point to the mobile page if the user is on a mobile device, even if the desktop

*[Content truncated]*

---

## Google Search technical requirements

**URL:** https://developers.google.com/search/docs/essentials/technical

**Contents:**
- Google Search technical requirements
- Googlebot isn't blocked (it can find and access the page)
  - Check if Googlebot can find and access your page
- The page works (it's not an error page)
- The page has indexable content

It costs nothing to get your page in search results, no matter what anyone tries to tell you. As long as your page meets the minimum technical requirements, it's eligible to be indexed by Google Search:

Google only indexes pages on the web that are accessible to the public and which don't block our crawler, Googlebot, from crawling them. If a page is made private, such as requiring a log-in to view it, Googlebot will not crawl it. Similarly, if one of the several mechanisms are used to block Google from indexing, the page will not be indexed.

Pages that are blocked by robots.txt are unlikely to show in Google Search results. To see a list of pages that are inaccessible to Google (but that you would like to see in Search results), use both the Page Indexing report and Crawl Stats report in Search Console. Each report may contain different information about your URLs, so it's a good idea to look at both reports.

To test a specific page, use the URL Inspection tool.

Google only indexes pages that are served with an HTTP 200 (success) status code. Client and server error pages aren't indexed. You can check the HTTP status code for a given page with the URL Inspection tool.

Once Googlebot can find and access a working page, Google checks the page for indexable content. Indexable content means:

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-02-04 UTC.

---

## AMP on Google Search guidelines

**URL:** https://developers.google.com/search/docs/crawling-indexing/amp

**Contents:**
- AMP on Google Search guidelines
- Additional AMP topics
- FAQs
  - Are AMP pages mobile-only?
  - How does AMP look on desktop?

All of our guidelines for making a site Google-friendly also apply to AMP. This document covers additional guidelines that are specific to AMP on Google Search. To learn more about AMP on Google Search, read our developer guide.

The following topics describe how to work with AMP and how it works in Google Search.

No. Since AMP pages can be viewed on all device types, build your AMP pages with responsive design.

AMP pages display equally well on both mobile and desktop screens. If AMP supports all the functionality that you need, you might consider creating your pages as standalone AMP pages to support both desktop and mobile visitors for the same page. However, AMP on desktop doesn't get search-specific features in Google Search results.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-02-04 UTC.

---

## How to specify a canonical URL with rel="canonical" and other methods

**URL:** https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls

**Contents:**
- How to specify a canonical URL with rel="canonical" and other methods
- Reasons to specify a canonical URL
- Best practices
- Comparison of canonicalization methods
- Use rel="canonical" link annotations
  - The rel="canonical" link element
  - The rel="canonical" HTTP header
- Use a sitemap
- Use redirects
- Other signals

To specify a canonical URL for duplicate or very similar pages to Google Search, you can indicate your preference using a number of methods. These are, in order of how strongly they can influence canonicalization:

Keep in mind that these methods can stack and thus become more effective when combined. This means that when you use two or more of the methods, that will increase the chance of your preferred canonical URL appearing in search results.

While we encourage you to use these methods, none of them are required; your site will likely do just fine without specifying a canonical preference. That's because if you don't specify a canonical URL, Google will identify which version of the URL is objectively the best version to show to users in Search.

While it's generally not critical to specify a canonical preference for your URLs, there are a number of reasons why you would want to explicitly tell Google about a canonical page in a set of duplicate or similar pages:

For all canonicalization methods, follow these best practices:

The following table compares the different canonicalization methods, highlighting their strengths and weaknesses when it comes to maintenance and efficacy in different scenarios.

Add a <link> element in the code for all duplicate pages, pointing to the canonical page.

Send a rel="canonical" header in your page response.

Specify your canonical pages in a sitemap.

Google supports explicit rel canonical link annotations as described in RFC 6596. rel="canonical" annotations that suggest alternate versions of a page are ignored; specifically, rel="canonical" annotations with hreflang, lang, media, and type attributes are not used for canonicalization. Instead, use the appropriate link annotations to specify alternate versions of a page; for example, link rel="alternate" hreflang for language and country annotations.

You can provide the rel="canonical" link annotations in two ways:

We recommend that you choose one of these and go with that; while supported, using both methods at the same time is more error prone (for example, you might provide one URL in the HTTP header, and another URL in the rel="canonical" link element).

A rel="canonical" link element (also known as a canonical element) is an element used in the head section of HTML to indicate that another page is representative of the content on the page.

Suppose you want https://example.com/dresses/green-dresses to be the canonical URL, even though a variety of URLs can 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<html>
<head>
<title>Explore the world of dresses</title>
<link rel="canonical" href="https://example.com/dresses/green-dresses" />
<!-- other elements -->
</head>
<!-- rest of the HTML -->
```

Example 2 (unknown):
```unknown
<html>
<head>
<title>Explore the world of dresses</title>
<link rel="alternate" media="only screen and (max-width: 640px)"  href="https://m.example.com/dresses/green-dresses">
<link rel="canonical" href="https://example.com/dresses/green-dresses" />
<!-- other elements -->
</head>
<!-- rest of the HTML -->
```

Example 3 (unknown):
```unknown
HTTP/1.1 200 OK
Content-Length: 19
...
Link: <https://www.example.com/downloads/white-paper.pdf>; rel="canonical"
...
```

---

## Ask Google to recrawl your URLs

**URL:** https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl

**Contents:**
- Ask Google to recrawl your URLs
- Use the URL Inspection tool (just a few URLs)
- Submit a sitemap (many URLs at once)

If you've recently added or made changes to a page on your site, you can request that Google re-index your page using any of the methods listed here. You can't request indexing for URLs that you don't manage.

Crawling can take anywhere from a few days to a few weeks. Be patient and monitor progress using either the Index Status report or the URL Inspection tool.

To request a crawl of individual URLs, use the URL Inspection tool. You must be an owner or full user of the Search Console property to be able to request indexing in the URL Inspection tool.

Keep in mind that there's a quota for submitting individual URLs and requesting a recrawl multiple times for the same URL won't get it crawled any faster.

If you have large numbers of URLs, submit a sitemap. A sitemap is an important way for Google to discover URLs on your site. It can be very helpful if you just launched your site or recently performed a site move. A sitemap can also include additional metadata about alternate language versions, video, image, or news-specific pages. Learn how to create and submit a sitemap.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-03-06 UTC.

---

## Link best practices for Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/links-crawlable

**Contents:**
- Link best practices for Google
- Make your links crawlable
- Anchor text placement
- Write good anchor text
- Internal links: cross-reference your own content
- External links: link to other sites

Google uses links as a signal when determining the relevancy of pages and to find new pages to crawl. Learn how to make your links crawlable so that Google can find other pages on your site via the links on your page, and how to improve your anchor text so that it's easier for people and Google to make sense of your content.

Generally, Google can only crawl your link if it's an <a> HTML element (also known as anchor element) with an href attribute. Most links in other formats won't be parsed and extracted by Google's crawlers. Google can't reliably extract URLs from <a> elements that don't have an href attribute or other tags that perform as links because of script events. Here are examples of links that Google can and can't parse:

Recommended (Google can parse)

Not recommended (but Google may still attempt to parse this):

Make sure that the URL in your <a> element resolves into an actual web address (meaning, it resembles a URI) that Google crawlers can send requests to, for example:

Recommended (Google can resolve):

Not recommended (but Google may still attempt to resolve this):

Anchor text (also known as link text) is the visible text of a link. This text tells people and Google something about the page you're linking to. Place anchor text between <a> elements that Google can crawl.

Bad (empty link text):

As a fallback, Google can use the title attribute as anchor text if the <a> element is for some reason empty.

For images as links, Google uses the alt attribute of the img element as anchor text, so be sure to add descriptive alt text to your images:

Bad (empty alt text and empty link text):

If you are using JavaScript to insert anchor text, use the URL Inspection Tool to make sure it's present in the rendered HTML.

Good anchor text is descriptive, reasonably concise, and relevant to the page that it's on and to the page it links to. It provides context for the link, and sets the expectation for your readers. The better your anchor text, the easier it is for people to navigate your site and for Google to understand what the page you're linking to is about.

Better (more descriptive):

Better (more concise):

Write as naturally as possible, and resist the urge to cram every keyword that's related to the page that you're linking to (remember, keyword stuffing is a violation of our spam policies). Ask yourself, does the reader need these keywords to understand the next page? If it feels like you're forcing keywords into the anchor text, then 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<a href="https://example.com">
```

Example 2 (unknown):
```unknown
<a href="/products/category/shoes">
```

Example 3 (unknown):
```unknown
<a href="./products/category/shoes">
```

Example 4 (unknown):
```unknown
<a href="/products/category/shoes" onclick="javascript:goTo('shoes')">
```

---

## Temporarily pause or disable a website

**URL:** https://developers.google.com/search/docs/crawling-indexing/pause-online-business

**Contents:**
- Temporarily pause or disable a website
- Limit your site's functionality (recommended)
- Not recommended: Disable the whole website
  - Best practices for disabling a site
- FAQs
  - What if I only close the site for a few weeks?
  - What if I want to exclude all non-essential products?
  - Can I ask Google to crawl less while my site is temporarily closed?
  - How do I get a page indexed or updated quickly?
  - What if I block a specific region from accessing my site?

If you're unable to fulfill orders or many of your products out of stock, you may be considering temporarily closing your online business. If the situation is temporary, meaning you expect to be able to sell products in the coming weeks or months, we recommend that you take action that preserves as much of your site's standing in Search as possible. This guide explains how you can safely pause your online business.

If your situation is temporary and you plan to reopen your online business, we recommend that you keep your site online and limit the functionality. This is the recommended approach since it minimizes any negative effects on your site's presence in Search. People can still find your products, read reviews, or add wishlists so they can purchase at a later time. We recommend doing the following:

You may decide to disable the whole website. This is an extreme measure that should only be taken for a very short period of time (a few days at most), as it will otherwise have significant effects on the website in Search, even when implemented properly.

Make sure that you consider the following side effects of disabling your entire site:

If you decide that you need to do this (again, not recommended), here are some options:

While we don't recommend disabling your site, here are some best practices if you decide to do this:

Completely closing a site even for just a few weeks can have negative consequences on Google's indexing of your site. We recommend limiting the site functionality instead. Keep in mind that users may also want to find information about your products, your services, and your company, even if you're currently not selling anything.

That's fine. Make sure that people can't buy the non-essential products by limiting the site functionality.

Yes, you can reduce the Googlebot crawl rate, though it's not recommended for most cases. This may have some impact on the freshness of your results in Search. For example, it may take longer for Search to reflect that all of your products are currently not available. On the other hand, if Googlebot's crawling causes critical server resource issues, this is a valid approach. We recommend setting a reminder for yourself to reset the crawl rate once you're ready to go back in business.

To ask Google to recrawl a limited number of pages (for example, the home page), use Search Console. For a larger number of pages (for example, all of your product pages), use sitemaps.

Google generally crawls from 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
curl -I -X GET "https://www.example.com/"
HTTP/1.1 503 Service Unavailable
Mime-Version: 1.0
Content-Type: text/html
(...)
```

---

## Qualify your outbound links to Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links#nofollow

**Contents:**
- Qualify your outbound links to Google
  - rel="sponsored"
  - rel="ugc"
  - rel="nofollow"
  - Multiple values

For certain links on your site, you might want to tell Google your relationship with the linked page. In order to do that, use one of the following rel attribute values in the <a> tag.

For regular links that you expect Google to fetch and parse without any qualifications, you don't need to add a rel attribute. For example:

For other links, use one or more of the following values:

Mark links that are advertisements or paid placements (commonly called paid links) with the sponsored value. Read more about Google's stance on paid links.

We recommend marking user-generated content (UGC) links, such as comments and forum posts, with the ugc value.

If you want to recognize and reward trustworthy contributors, you might remove this attribute from links posted by members or users who have consistently made high-quality contributions over time. Read more about how to prevent user-generated spam on your site and platform.

Use the nofollow value when other values don't apply, and you'd rather Google not associate your site with, or crawl the linked page from, your site. For links within your own site, use the robots.txt disallow rule.

You may specify multiple rel values as a space- or comma-separated list. Examples:

Links marked with these rel attributes will generally not be followed. Remember that the linked pages may be found through other means, such as sitemaps or links from other sites, and thus they may still be crawled. These rel attributes are used only in <a> elements that Google can crawl, except nofollow, which is also available as robots meta tag.

If you need to prevent Google from fetching a link to a page on your own site, use the robots.txt disallow rule.

To prevent Google from indexing a page, allow crawling and use the noindex robots rule.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-08-28 UTC.

**Examples:**

Example 1 (unknown):
```unknown
<p>My favorite horse is the <a href="https://horses.example.com/Palomino">palomino</a>.</p>
```

Example 2 (unknown):
```unknown
<a rel="sponsored" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

Example 3 (unknown):
```unknown
<a rel="ugc" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

Example 4 (unknown):
```unknown
<a rel="nofollow" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

---

## Redirects and Google Search

**URL:** https://developers.google.com/search/docs/crawling-indexing/301-redirects

**Contents:**
- Redirects and Google Search
- Overview of redirect types
- Server-side redirects
  - Permanent server-side redirects
  - Temporary server-side redirects
  - Implement server-side redirects
- meta refresh and its HTTP equivalent
- JavaScript location redirects
- Crypto redirects
- Alternate versions of a URL

Redirecting URLs is the practice of resolving an existing URL to a different one, effectively telling your visitors and Google Search that a page has a new location. Redirects are particularly useful in the following circumstances:

While your users generally won't be able to tell the difference between the different types of redirects, Google Search uses redirects as a strong or weak signal that the redirect target should be canonical. Choosing a redirect depends on how long you expect the redirect will be in place and what page you want Google Search to show in search results:

The following table explains the various ways you can use to set up permanent and temporary redirects, ordered by how likely Google is able to interpret correctly (for example, a server side redirect has the highest chance of being interpreted correctly by Google). Choose the redirect type that works for your situation and site:

Googlebot follows the redirect, and the indexing pipeline uses the redirect as a strong signal that the redirect target should be canonical.

Set up server-side redirects.

Set up meta refresh redirects.

Set up JavaScript redirects.

Only use JavaScript redirects if you can't do server-side or meta refresh redirects.

Learn more about crypto redirects.

Googlebot follows the redirect, and the indexing pipeline uses the redirect as a weak signal that the redirect target should be canonical.

Set up server-side redirects.

Set up meta refresh redirects.

Setting up server-side redirects requires access to the server configuration files (for example, the .htaccess file on Apache) or setting the redirect headers with server-side scripts (for example, PHP). You can create both permanent and temporary redirects on the server side.

If you need to change the URL of a page as it is shown in search engine results, we recommend that you use a permanent server-side redirect whenever possible. This is the best way to ensure that Google Search and people are directed to the correct page. The 301 and 308 status codes mean that a page has permanently moved to a new location.

If you just want to send users to a different page temporarily, use a temporary redirect. This will also ensure that Google keeps the old URL in its results for a longer time. For example, if a service your site offers is temporarily unavailable, you can set up a temporary redirect to send users to a page that explains what's happening, without compromising the original URL in search results.

The

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
header('HTTP/1.1 301 Moved Permanently');
header('Location: https://www.example.com/newurl');
exit();
```

Example 2 (unknown):
```unknown
header('HTTP/1.1 302 Found');
header('Location: https://www.example.com/newurl');
exit();
```

Example 3 (unknown):
```unknown
# Permanent redirect:
Redirect permanent "/old" "https://example.com/new"

# Temporary redirect:
Redirect temp "/two-old" "https://example.com/two-new"
```

Example 4 (unknown):
```unknown
RewriteEngine on
# redirect the service page to a new page with a permanent redirect
RewriteRule   "^/service$"  "/about/service"  [R=301]

# redirect the service page to a new page with a temporary redirect
RewriteRule   "^/service$"  "/about/service"  [R]
```

---

## Large site owner's guide to managing your crawl budget

**URL:** https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget

**Contents:**
- Large site owner's guide to managing your crawl budget
- Who this guide is for
- General theory of crawling
  - Crawl capacity limit
  - Crawl demand
  - In sum
- Best practices
- Monitor your site's crawling and indexing
  - See if Googlebot is encountering availability issues on your site
  - See if any parts of your site are not crawled, but should be

This guide describes how to optimize Google's crawling of very large and frequently updated sites.

If your site does not have a large number of pages that change rapidly, or if your pages seem to be crawled the same day that they are published, you don't need to read this guide; merely keeping your sitemap up to date and checking your index coverage regularly is adequate.

If you have content that's been available for a while but has never been indexed, this is a different problem; use the URL Inspection tool instead to find out why your page isn't being indexed.

This is an advanced guide and is intended for:

The web is a nearly infinite space, exceeding Google's ability to explore and index every available URL. As a result, there are limits to how much time Googlebot can spend crawling any single site. The amount of time and resources that Google devotes to crawling a site is commonly called the site's crawl budget. Note that not everything crawled on your site will necessarily be indexed; each page must be evaluated, consolidated, and assessed to determine whether it will be indexed after it has been crawled.

Crawl budget is determined by two main elements: crawl capacity limit and crawl demand.

Googlebot wants to crawl your site without overwhelming your servers. To prevent this, Googlebot calculates a crawl capacity limit, which is the maximum number of simultaneous parallel connections that Googlebot can use to crawl a site, as well as the time delay between fetches. This is calculated to provide coverage of all your important content without overloading your servers.

The crawl capacity limit can go up and down based on a few factors:

Google typically spends as much time as necessary crawling a site, given its size, update frequency, page quality, and relevance, compared to other sites.

The factors that play a significant role in determining crawl demand are:

Additionally, site-wide events like site moves may trigger an increase in crawl demand in order to reindex the content under the new URLs.

Taking crawl capacity and crawl demand together, Google defines a site's crawl budget as the set of URLs that Googlebot can and wants to crawl. Even if the crawl capacity limit isn't reached, if crawl demand is low, Googlebot will crawl your site less.

Follow these best practices to maximize your crawling efficiency:

Here are the key steps to monitoring your site's crawl profile:

Improving your site availability won't necessarily increase your cra

*[Content truncated]*

---

## File types indexable by Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/indexable-file-types

**Contents:**
- File types indexable by Google
- Search by file type

Google can index the content of most text-based files and certain encoded document formats. The most common file types we index include:

Google can also index the following media formats:

You can use the filetype: operator in Google Search to limit results to a specific file type or file extension. For example, filetype:rtf galway will search for RTF files and URLs ending in .rtf whose content contains the term "galway".

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-02-04 UTC.

---

## Video sitemaps and alternatives

**URL:** https://developers.google.com/search/docs/crawling-indexing/sitemaps/video-sitemaps

**Contents:**
- Video sitemaps and alternatives
- Video sitemap best practices
- Example video sitemap
    - More examples
- Video sitemap reference
  - Deprecated tags and attributes
- Sitemap alternative: mRSS
  - mRSS Example
  - mRSS reference
- Additional resources

A video sitemap is a sitemap with additional information about videos hosted on your pages. Creating a video sitemap is a good way to help Google find and understand the video content on your site, especially content that was recently added or that we might not otherwise discover with our usual crawling mechanisms.

Google recommends using video sitemaps, however we also support mRSS feeds.

Video sitemaps are based on generic sitemaps, so the general sitemap best practices also apply to video sitemaps. You can create a separate sitemap or mRSS feed just for video, or you can add video sitemap tags within an existing sitemap, whichever is more convenient for you.

Additionally, the following requirements apply to video sitemaps specifically:

If you want to prevent spammers from accessing your video content at the <player_loc> or <content_loc> URLs, verify that any bots accessing your server are really Googlebot.

For more tips about videos in Google Search, see our video best practices.

The following example shows a regular sitemap with video extension. It includes two video entries nested in the single <url> tag. The first <video> entry includes all the tags that Google can use while the second only the required tags.

The following example demonstrates how to add a Vimeo video embed to a video sitemap:

The following example demonstrates how to add a YouTube video embed to a video sitemap:

The video tags are defined in the video sitemaps namespace: http://www.google.com/schemas/sitemap-video/1.1. Each tag can only be added one time per video, unless otherwise specified.

To make sure Google can use your video sitemap, you must use the following required tags:

The parent element for all information about a single video on the page specified by the <loc> tag. You can include multiple <video:video> tags nested in the <loc> tag, one for each video on the hosting page.

A URL pointing to the video thumbnail image file. Follow the video thumbnail requirements.

The title of the video. All HTML entities must be escaped or wrapped in a CDATA block. We recommend that this match the video title displayed on the web page where the video is embedded.

A description of the video. Maximum 2048 characters. All HTML entities must be escaped or wrapped in a CDATA block. It must match the description displayed on the web page where the video is embedded, but it doesn't need to be a word-for-word match.

A URL pointing to the actual video media file. The file must be o

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
  <url>
    <loc>https://www.example.com/videos/some_video_landing_page.html</loc>
    <video:video>
      <video:thumbnail_loc>https://www.example.com/thumbs/123.jpg</video:thumbnail_loc>
      <video:title>Grilling steaks for summer</video:title>
      <video:description>
        Alkis shows you how to get perfectly done steaks every time
      </video:description>
      <video:content_loc>
        http://streamserver.example.co
...
```

Example 2 (unknown):
```unknown
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
  <url>
    <loc>https://www.example.com/videos/some_video_landing_page.html</loc>
    <video:video>
      <video:thumbnail_loc>https://www.example.com/thumbs/123.jpg</video:thumbnail_loc>
      <video:title>Lizzi is painting the wall</video:title>
      <video:description>
        Gary is watching the paint dry on the wall Lizzi painted.
      </video:description>
      <video:player_loc>
        https://player.vimeo.com/video/98
...
```

Example 3 (unknown):
```unknown
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
  <url>
    <loc>https://www.example.com/videos/some_video_landing_page.html</loc>
    <video:video>
      <video:thumbnail_loc>https://www.example.com/thumbs/345.jpg</video:thumbnail_loc>
      <video:title>John teaches cheese</video:title>
      <video:description>
        John explains the differences between a banana and cheese.
      </video:description>
      <video:player_loc>
        https://www.youtube.com/embed/1a2b3c4d

...
```

Example 4 (unknown):
```unknown
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:dcterms="http://purl.org/dc/terms/">
  <channel>
    <title>Example MRSS</title>
    <link>https://www.example.com/examples/mrss/</link>
    <description>MRSS Example</description>
    <item xmlns:media="http://search.yahoo.com/mrss/" xmlns:dcterms="http://purl.org/dc/terms/">
      <link>https://www.example.com/examples/mrss/example.html</link>
      <media:content url="https://www.example.com/examples/mrss/example.flv" fileSize="405321"
                        type="video/x-flv" height
...
```

---

## Qualify your outbound links to Google

**URL:** https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links

**Contents:**
- Qualify your outbound links to Google
  - rel="sponsored"
  - rel="ugc"
  - rel="nofollow"
  - Multiple values

For certain links on your site, you might want to tell Google your relationship with the linked page. In order to do that, use one of the following rel attribute values in the <a> tag.

For regular links that you expect Google to fetch and parse without any qualifications, you don't need to add a rel attribute. For example:

For other links, use one or more of the following values:

Mark links that are advertisements or paid placements (commonly called paid links) with the sponsored value. Read more about Google's stance on paid links.

We recommend marking user-generated content (UGC) links, such as comments and forum posts, with the ugc value.

If you want to recognize and reward trustworthy contributors, you might remove this attribute from links posted by members or users who have consistently made high-quality contributions over time. Read more about how to prevent user-generated spam on your site and platform.

Use the nofollow value when other values don't apply, and you'd rather Google not associate your site with, or crawl the linked page from, your site. For links within your own site, use the robots.txt disallow rule.

You may specify multiple rel values as a space- or comma-separated list. Examples:

Links marked with these rel attributes will generally not be followed. Remember that the linked pages may be found through other means, such as sitemaps or links from other sites, and thus they may still be crawled. These rel attributes are used only in <a> elements that Google can crawl, except nofollow, which is also available as robots meta tag.

If you need to prevent Google from fetching a link to a page on your own site, use the robots.txt disallow rule.

To prevent Google from indexing a page, allow crawling and use the noindex robots rule.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-08-28 UTC.

**Examples:**

Example 1 (unknown):
```unknown
<p>My favorite horse is the <a href="https://horses.example.com/Palomino">palomino</a>.</p>
```

Example 2 (unknown):
```unknown
<a rel="sponsored" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

Example 3 (unknown):
```unknown
<a rel="ugc" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

Example 4 (unknown):
```unknown
<a rel="nofollow" href="https://cheese.example.com/Appenzeller_cheese">Appenzeller</a>
```

---

## Minimize A/B testing impact in Google Search

**URL:** https://developers.google.com/search/docs/crawling-indexing/website-testing

**Contents:**
- Minimize A/B testing impact in Google Search
- Overview of testing
- Best practices when testing
  - Don't cloak your test pages
  - Use rel="canonical" links
  - Use 302 redirects, not 301 redirects
  - Run the experiment only as long as necessary
- More information about testing

This page covers how to ensure that testing variations in page content or page URLs has minimal impact on your Google Search performance. It does not give instructions on how to build or design tests, but you can find more resources about testing at the end of this page.

Website testing is when you try out different versions of your website (or a part of your website) and collect data about how users react to each version.

You can use software to compare behavior with different variations of your pages (parts of a page, entire pages, or entire multi-page flows), and track which version is most effective with your users.

You can run tests by creating multiple versions of a page, each with its own URL. When users try to access the original URL, you redirect some of them to each of the variation URLs and then compare users' behavior to see which page is most effective.

You can also run tests without changing the URL by inserting variations dynamically on the page. You can use JavaScript to decide which variation to display.

Depending on what types of content you're testing, it may not even matter much if Google crawls or indexes some of your content variations while you're testing. Small changes, such as the size, color, or placement of a button or image, or the text of your "call to action" ("Add to cart" vs. "Buy now!"), can have a surprising impact on users' interactions with your page, but often have little or no impact on that page's search result snippet or ranking.

In addition, if we crawl your site often enough to detect and index your experiment, we'll probably index the eventual updates you make to your site fairly quickly after you've concluded the experiment.

Here is a list of best practices to avoid any bad effects on your Google Search behavior while testing site variations:

Don't show one set of URLs to Googlebot, and a different set to humans. This is called cloaking, and is against our spam policies, whether you're running a test or not. Remember that infringing our spam policies can get your site demoted or removed from Google search results—probably not the desired outcome of your test.

Cloaking counts whether you do it by server logic or by robots.txt, or any other method. Instead, use links or redirects as described next.

If you're using cookies to control the test, keep in mind that Googlebot generally doesn't support cookies. This means it will only see the content version that's accessible to users with browsers that don't ac

*[Content truncated]*

---

## Use valid HTML to specify page metadata

**URL:** https://developers.google.com/search/docs/crawling-indexing/valid-page-metadata

**Contents:**
- Use valid HTML to specify page metadata
- Use valid elements in the <head> element
- Don't use invalid elements in the <head> element

Using valid HTML for page metadata ensures that Google can use the metadata as documented. Google tries to understand HTML even when it is invalid or inconsistent with the HTML standard, but errors in the markup can cause problems with how your metadata is used in Google Search. The primary element for specifying metadata about a page is the <head> element of an HTML document. If you use an invalid element in the <head> element, Google ignores any elements that appear after the invalid element.

The <head> element must only contain the following valid elements (and no other invalid elements), as per the HTML standard:

No element other than the aforementioned is permitted by the HTML standard in the <head> element. Common elements that appear in the <head> element, rendering it invalid are:

We strongly recommend that you don't use these invalid elements in the <head> element, but if you must, place these invalid elements after the ones you want Google to see. Once Google detects one of these invalid elements, it assumes the end of the <head> element and stops reading any further elements in the <head> element.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-02-04 UTC.

---

## Redirects and Google Search

**URL:** https://developers.google.com/search/docs/crawling-indexing/301-redirects#jslocation

**Contents:**
- Redirects and Google Search
- Overview of redirect types
- Server-side redirects
  - Permanent server-side redirects
  - Temporary server-side redirects
  - Implement server-side redirects
- meta refresh and its HTTP equivalent
- JavaScript location redirects
- Crypto redirects
- Alternate versions of a URL

Redirecting URLs is the practice of resolving an existing URL to a different one, effectively telling your visitors and Google Search that a page has a new location. Redirects are particularly useful in the following circumstances:

While your users generally won't be able to tell the difference between the different types of redirects, Google Search uses redirects as a strong or weak signal that the redirect target should be canonical. Choosing a redirect depends on how long you expect the redirect will be in place and what page you want Google Search to show in search results:

The following table explains the various ways you can use to set up permanent and temporary redirects, ordered by how likely Google is able to interpret correctly (for example, a server side redirect has the highest chance of being interpreted correctly by Google). Choose the redirect type that works for your situation and site:

Googlebot follows the redirect, and the indexing pipeline uses the redirect as a strong signal that the redirect target should be canonical.

Set up server-side redirects.

Set up meta refresh redirects.

Set up JavaScript redirects.

Only use JavaScript redirects if you can't do server-side or meta refresh redirects.

Learn more about crypto redirects.

Googlebot follows the redirect, and the indexing pipeline uses the redirect as a weak signal that the redirect target should be canonical.

Set up server-side redirects.

Set up meta refresh redirects.

Setting up server-side redirects requires access to the server configuration files (for example, the .htaccess file on Apache) or setting the redirect headers with server-side scripts (for example, PHP). You can create both permanent and temporary redirects on the server side.

If you need to change the URL of a page as it is shown in search engine results, we recommend that you use a permanent server-side redirect whenever possible. This is the best way to ensure that Google Search and people are directed to the correct page. The 301 and 308 status codes mean that a page has permanently moved to a new location.

If you just want to send users to a different page temporarily, use a temporary redirect. This will also ensure that Google keeps the old URL in its results for a longer time. For example, if a service your site offers is temporarily unavailable, you can set up a temporary redirect to send users to a page that explains what's happening, without compromising the original URL in search results.

The

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
header('HTTP/1.1 301 Moved Permanently');
header('Location: https://www.example.com/newurl');
exit();
```

Example 2 (unknown):
```unknown
header('HTTP/1.1 302 Found');
header('Location: https://www.example.com/newurl');
exit();
```

Example 3 (unknown):
```unknown
# Permanent redirect:
Redirect permanent "/old" "https://example.com/new"

# Temporary redirect:
Redirect temp "/two-old" "https://example.com/two-new"
```

Example 4 (unknown):
```unknown
RewriteEngine on
# redirect the service page to a new page with a permanent redirect
RewriteRule   "^/service$"  "/about/service"  [R=301]

# redirect the service page to a new page with a temporary redirect
RewriteRule   "^/service$"  "/about/service"  [R]
```

---

## Overview of crawling and indexing topics

**URL:** https://developers.google.com/search/docs/crawling-indexing

**Contents:**
- Overview of crawling and indexing topics

The topics in this section describe how you can control Google's ability to find and parse your content in order to show it in Search and other Google properties, as well as how to prevent Google from crawling specific content on your site.

Here's a brief description of each page. To get an overview of crawling and indexing, read our How Search works guide.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-06-04 UTC.

---

## Build and submit a sitemap

**URL:** https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

**Contents:**
- Build and submit a sitemap
- Sitemap best practices
- XML sitemap
  - Additional notes about XML sitemaps
- RSS, mRSS, and Atom 1.0
  - Additional notes about RSS, mRSS, and Atom 1.0
- Text sitemap
  - Additional notes for text file sitemaps
- How to create a sitemap
  - Let your CMS generate a sitemap for you

This page describes how to build a sitemap and make it available to Google. If you're new to sitemaps, read our introduction first.

Google supports the sitemap formats defined by the sitemaps protocol. Each format has its own benefits and shortcomings; choose the one that is the most appropriate for your site and setup (Google doesn't have a preference). The following table compares the different sitemap formats:

XML sitemaps are the most versatile of the sitemaps formats. It's extensible and can be used to supply additional data about images, video, and news content, as well as the localized versions of your pages.

RSS, mRSS, and Atom 1.0 sitemaps are similar in structure to XML sitemaps, however they are often the easiest to provide because CMSes automatically create them.

The simplest of sitemap formats, it can only list URLs to HTML and other indexable pages.

The best practices for sitemaps are defined by the sitemaps protocol. The most overlooked best practices are related to the size limits, sitemap location, and the URLs included in the sitemaps.

Sitemap size limits: All formats limit a single sitemap to 50MB (uncompressed) or 50,000 URLs. If you have a larger file or more URLs, you must break your sitemap into multiple sitemaps. You can optionally create a sitemap index file and submit that single index file to Google. You can submit multiple sitemaps and sitemap index files to Google. This may be useful if you want to track the search performance of each individual sitemap in Search Console.

Sitemap file encoding and location: The sitemap file must be UTF-8 encoded. You can host your sitemaps anywhere on your site, but unless you submit your sitemap through Search Console, a sitemap affects only descendants of the parent directory. Therefore, a sitemap posted at the site root can affect all files on the site, which is where we recommend posting your sitemaps.

Referenced URLs' properties: Use fully-qualified, absolute URLs in your sitemaps. Google will attempt to crawl your URLs exactly as listed. For example, if your site is at https://www.example.com/, don't specify a URL such as /mypage.html (a relative URL), use the complete, absolute URL: https://www.example.com/mypage.html.

Include the URLs in your sitemap that you want to see in Google's search results. Google generally shows the canonical URLs in its search results, which you can influence with sitemaps. If you have different URLs for mobile and desktop versions of a page, we recom

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.example.com/foo.html</loc>
    <lastmod>2022-06-04</lastmod>
  </url>
</urlset>
```

Example 2 (unknown):
```unknown
https://www.example.com/file1.html
https://www.example.com/file2.html
```

Example 3 (unknown):
```unknown
Sitemap: https://example.com/my_sitemap.xml
```

Example 4 (unknown):
```unknown
# robots.txt file of https://example.com/
sitemap: https://sitemaps.example.com/sitemap-example-com.xml
```

---

## Block Search indexing with noindex

**URL:** https://developers.google.com/search/docs/crawling-indexing/block-indexing

**Contents:**
- Block Search indexing with noindex
- Implementing noindex
  - <meta> tag
  - HTTP response header
  - Debugging noindex issues

noindex is a rule set with either a <meta> tag or HTTP response header and is used to prevent indexing content by search engines that support the noindex rule, such as Google. When Googlebot crawls that page and extracts the tag or header, Google will drop that page entirely from Google Search results, regardless of whether other sites link to it.

Using noindex is useful if you don't have root access to your server, as it allows you to control access to your site on a page-by-page basis.

There are two ways to implement noindex: as a <meta> tag and as an HTTP response header. They have the same effect; choose the method that is more convenient for your site and appropriate for the content type. Specifying the noindex rule in the robots.txt file is not supported by Google.

You can also combine the noindex rule with other rules that control indexing. For example, you can join a nofollow hint with a noindex rule: <meta name="robots" content="noindex, nofollow" />.

To prevent all search engines that support the noindex rule from indexing a page on your site, place the following <meta> tag into the <head> section of your page:

To prevent only Google web crawlers from indexing a page:

Be aware that some search engines might interpret the noindex rule differently. As a result, it is possible that your page might still appear in results from other search engines.

Read more about the noindex <meta> tag.

If you use a CMS, such as Wix, WordPress, or Blogger, you might not be able to edit your HTML directly, or you might prefer not to. Instead, your CMS might have a search engine settings page or some other mechanism to tell search engines about meta tags.

If you want to add a meta tag to your website, search for instructions about modifying the <head> of your page on your CMS (for example, search for "wix add meta tags").

Instead of a <meta> tag, you can return an X-Robots-Tag HTTP header with a value of either noindex or none in your response. A response header can be used for non-HTML resources, such as PDFs, video files, and image files. Here's an example of an HTTP response with an X-Robots-Tag header instructing search engines not to index a page:

Read more about the noindex response header.

We have to crawl your page in order to see <meta> tags and HTTP headers. If a page is still appearing in results, it's probably because we haven't crawled the page since you added the noindex rule. Depending on the importance of the page on the internet, it may ta

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<meta name="robots" content="noindex">
```

Example 2 (unknown):
```unknown
<meta name="googlebot" content="noindex">
```

Example 3 (unknown):
```unknown
HTTP/1.1 200 OK
(...)
X-Robots-Tag: noindex
(...)
```

---

## meta tags and attributes that Google supports

**URL:** https://developers.google.com/search/docs/crawling-indexing/special-tags

**Contents:**
- meta tags and attributes that Google supports
- meta tags
  - description
  - robots and googlebot
  - notranslate
  - nopagereadaloud
  - google-site-verification
  - Content-Type and charset
  - refresh
  - viewport

This page explains what meta tags are, which meta tags and HTML attributes Google supports to control indexing, and other important points to note when implementing meta tags on your site.

meta tags are HTML tags used to provide additional information about a page to search engines and other clients. Clients process the meta tags and ignore those they don't support. meta tags are added to the <head> section of your HTML page and generally look like this:

If you use a CMS, such as Wix, WordPress, or Blogger, you might not be able to edit your HTML directly, or you might prefer not to. Instead, your CMS might have a search engine settings page or some other mechanism to tell search engines about meta tags.

If you want to add a meta tag to your website, search for instructions about modifying the <head> of your page on your CMS (for example, search for "wix add meta tags").

Google supports the following meta tags:

These meta tags control the behavior of search engine crawling and indexing.

The <meta name="robots" ... tag applies to all search engines, while the <meta name="googlebot ... tag is specific to Google.

In the case of conflicting robots (or googlebot) meta tags, the more restrictive tag applies. For example, if a page has both the max-snippet:50 and nosnippet tags, the nosnippet tag will apply.

The default values are index, follow and don't need to be specified. For a full list of values that Google supports, see the list of valid rules.

You can also specify this information in the header of your pages using the X-Robots-Tag HTTP header rule. This is particularly useful if you wish to limit indexing of non-HTML files like graphics or other kinds of documents. More information about robots meta tags.

When Google recognizes that the contents of a page aren't in the language that the user likely wants to read, Google may provide a translated title link and snippet in search results. If the user clicks the translated title link, all further user interaction with the page is through Google Translate, which will automatically translate any links followed. In general, this gives you the chance to provide your unique and compelling content to a much larger group of users. However, there may be situations where this is not desired. This meta tag tells Google that you don't want us to provide a translation for this page.

Prevents various Google text-to-speech services from reading aloud web pages using text-to-speech (TTS).

You can use this tag on

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<!DOCTYPE html>
  <html>
  <head>
    <meta charset="utf-8">
    <meta name="description" content="Author: A.N. Author, Illustrator: P. Picture, Category: Books, Price:  £9.24, Length: 784 pages">
    <meta name="google-site-verification" content="+nxGUDJ4QpAZ5l9Bsjdi102tLVC21AIh5d1Nl23908vVuFHs34=">
    <title>Example Books - high-quality used books for children</title>
    <meta name="robots" content="noindex,nofollow">
  </head>
</html>
```

Example 2 (unknown):
```unknown
<meta name="description" content="A description of the page">
```

Example 3 (unknown):
```unknown
<meta name="robots" content="..., ...">
```

Example 4 (unknown):
```unknown
<meta name="googlebot" content="..., ...">
```

---

## How HTTP status codes, and network and DNS errors affect Google Search

**URL:** https://developers.google.com/search/docs/crawling-indexing/http-network-errors#network-and-dns-errors

**Contents:**
- How HTTP status codes, and network and DNS errors affect Google Search
- HTTP status codes
  - 2xx (success)
  - 3xx (redirection)
  - 4xx (client errors)
  - 5xx (server errors)
  - soft 404 errors
    - Fix soft 404 errors
      - The page and content are no longer available
      - The page or content is now somewhere else

This page describes how different HTTP status codes, network errors, and DNS errors affect Google Search. We cover the top 20 status codes that Googlebot encountered on the web, and the most prominent network and DNS errors. More exotic status codes, such as 418 (I'm a teapot), aren't covered. All issues mentioned on this page generate a corresponding error or warning in Search Console's Page Indexing report.

HTTP status codes are generated by the server that's hosting the site when it responds to a request made by a client, for example a browser or a crawler. Every HTTP status code has a different meaning, but often the outcome of the request is the same. For example, there are multiple status codes that signal redirection, but their outcome is the same.

Search Console generates error messages for status codes in the 4xx–5xx range, and for failed redirections (3xx). If the server responded with a 2xx status code, the content received in the response may be considered for indexing.

The following table contains the most encountered HTTP status codes by Googlebot and an explanation how Google handles each status code.

Google considers the content for indexing. If the content suggests an error, for example an empty page or an error message, Search Console will show a soft 404 error.

Google passes on the content to the indexing pipeline. The indexing systems may index the content, but that's not guaranteed.

Googlebot waits for the content for a limited time, then passes on whatever it received to the indexing pipeline. The timeout is user agent dependent, for example Googlebot Smartphone may have a different timeout than Googlebot Image.

Googlebot signals the indexing pipeline that it received no content. Search Console may show a soft 404 error in the site's Page Indexing report.

Googlebot follows up to 10 redirect hops. If the crawler doesn't receive content within 10 hops, Search Console will show a redirect error in the site's Page Indexing report. The number of hops Googlebot follows is user agent dependent; for example, Googlebot Smartphone may have a different value than Googlebot Image.

Any content Googlebot received from the redirecting URL is ignored, and the final target URL's content is considered for indexing. For robots.txt files, learn how Google handles a robots.txt that returns a 3xx status code.

Googlebot follows the redirect, and the indexing pipeline uses the redirect as a strong signal that the redirect target should be canonical

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
dig +nocmd example.com a +noall +answer
```

Example 2 (unknown):
```unknown
dig +nocmd www.example.com cname +noall +answer
```

Example 3 (unknown):
```unknown
dig +nocmd example.com ns +noall +answer
example.com.    86400  IN  NS  a.iana-servers.net.
example.com.    86400  IN  NS  b.iana-servers.net.
dig +nocmd @a.iana-servers.net example.com +noall +answer
example.com.    86400  IN  A  93.184.216.34
dig +nocmd @b.iana-servers.net example.com +noall +answer
...
```

---

## How Google interprets the robots.txt specification

**URL:** https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt#disallow

**Contents:**
- How Google interprets the robots.txt specification
- What is a robots.txt file
- File location and range of validity
- Examples of valid robots.txt URLs
- Handling of errors and HTTP status codes
- Caching
- File format
- Syntax
  - user-agent
  - disallow

Google's automated crawlers support the Robots Exclusion Protocol (REP). This means that before crawling a site, Google's crawlers download and parse the site's robots.txt file to extract information about which parts of the site may be crawled. The REP isn't applicable to Google's crawlers that are controlled by users (for example, feed subscriptions), or crawlers that are used to increase user safety (for example, malware analysis).

This page describes Google's interpretation of the REP. For the original standard, check RFC 9309.

If you don't want crawlers to access sections of your site, you can create a robots.txt file with appropriate rules. A robots.txt file is a text file containing rules about which crawlers may access which parts of a site. For example, the robots.txt file for example.com may look like this:

If you're new to robots.txt, start with our intro to robots.txt. You can also find tips for creating a robots.txt file.

You must place the robots.txt file in the top-level directory of a site, on a supported protocol. The URL for the robots.txt file is (like other URLs) case-sensitive. In case of Google Search, the supported protocols are HTTP, HTTPS, and FTP. On HTTP and HTTPS, crawlers fetch the robots.txt file with an HTTP non-conditional GET request; on FTP, crawlers use a standard RETR (RETRIEVE) command, using anonymous login.

Avoid serving different versions of your robots.txt file to different requestors (in other words, cloaking), as this creates a maintenance burden, may prevent you from debugging crawl issues, or have otherwise unintended consequences.

The rules listed in the robots.txt file apply only to the host, protocol, and port number where the robots.txt file is hosted.

The following table contains examples of robots.txt URLs and what URL paths they're valid for. Column one contains the URL of a robots.txt file, and column two contains domains that that robots.txt file would and wouldn't apply to.

This is the general case. It's not valid for other subdomains, protocols, or port numbers. It's valid for all files in all subdirectories on the same host, protocol, and port number.

A robots.txt on a subdomain is only valid for that subdomain.

Valid for: https://www.example.com/

IDNs are equivalent to their punycode versions. See also RFC 3492.

Not valid for: https://www.example.com/

Valid for: ftp://example.com/

Not valid for: https://example.com/

A robots.txt with an IP-address as the hostname is only valid for cra

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
# This robots.txt file controls crawling of URLs under https://example.com.
# All crawlers are disallowed to crawl files in the "includes" directory, such
# as .css, .js, but Google needs them for rendering, so Googlebot is allowed
# to crawl them.
User-agent: *
Disallow: /includes/

User-agent: Googlebot
Allow: /includes/

Sitemap: https://example.com/sitemap.xml
```

Example 2 (unknown):
```unknown
disallow: [path]
```

Example 3 (unknown):
```unknown
allow: [path]
```

Example 4 (unknown):
```unknown
sitemap: [absoluteURL]
```

---

## How HTTP status codes, and network and DNS errors affect Google Search

**URL:** https://developers.google.com/search/docs/crawling-indexing/http-network-errors#soft-404-errors

**Contents:**
- How HTTP status codes, and network and DNS errors affect Google Search
- HTTP status codes
  - 2xx (success)
  - 3xx (redirection)
  - 4xx (client errors)
  - 5xx (server errors)
  - soft 404 errors
    - Fix soft 404 errors
      - The page and content are no longer available
      - The page or content is now somewhere else

This page describes how different HTTP status codes, network errors, and DNS errors affect Google Search. We cover the top 20 status codes that Googlebot encountered on the web, and the most prominent network and DNS errors. More exotic status codes, such as 418 (I'm a teapot), aren't covered. All issues mentioned on this page generate a corresponding error or warning in Search Console's Page Indexing report.

HTTP status codes are generated by the server that's hosting the site when it responds to a request made by a client, for example a browser or a crawler. Every HTTP status code has a different meaning, but often the outcome of the request is the same. For example, there are multiple status codes that signal redirection, but their outcome is the same.

Search Console generates error messages for status codes in the 4xx–5xx range, and for failed redirections (3xx). If the server responded with a 2xx status code, the content received in the response may be considered for indexing.

The following table contains the most encountered HTTP status codes by Googlebot and an explanation how Google handles each status code.

Google considers the content for indexing. If the content suggests an error, for example an empty page or an error message, Search Console will show a soft 404 error.

Google passes on the content to the indexing pipeline. The indexing systems may index the content, but that's not guaranteed.

Googlebot waits for the content for a limited time, then passes on whatever it received to the indexing pipeline. The timeout is user agent dependent, for example Googlebot Smartphone may have a different timeout than Googlebot Image.

Googlebot signals the indexing pipeline that it received no content. Search Console may show a soft 404 error in the site's Page Indexing report.

Googlebot follows up to 10 redirect hops. If the crawler doesn't receive content within 10 hops, Search Console will show a redirect error in the site's Page Indexing report. The number of hops Googlebot follows is user agent dependent; for example, Googlebot Smartphone may have a different value than Googlebot Image.

Any content Googlebot received from the redirecting URL is ignored, and the final target URL's content is considered for indexing. For robots.txt files, learn how Google handles a robots.txt that returns a 3xx status code.

Googlebot follows the redirect, and the indexing pipeline uses the redirect as a strong signal that the redirect target should be canonical

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
dig +nocmd example.com a +noall +answer
```

Example 2 (unknown):
```unknown
dig +nocmd www.example.com cname +noall +answer
```

Example 3 (unknown):
```unknown
dig +nocmd example.com ns +noall +answer
example.com.    86400  IN  NS  a.iana-servers.net.
example.com.    86400  IN  NS  b.iana-servers.net.
dig +nocmd @a.iana-servers.net example.com +noall +answer
example.com.    86400  IN  A  93.184.216.34
dig +nocmd @b.iana-servers.net example.com +noall +answer
...
```

---

## How HTTP status codes, and network and DNS errors affect Google Search

**URL:** https://developers.google.com/search/docs/crawling-indexing/http-network-errors

**Contents:**
- How HTTP status codes, and network and DNS errors affect Google Search
- HTTP status codes
  - 2xx (success)
  - 3xx (redirection)
  - 4xx (client errors)
  - 5xx (server errors)
  - soft 404 errors
    - Fix soft 404 errors
      - The page and content are no longer available
      - The page or content is now somewhere else

This page describes how different HTTP status codes, network errors, and DNS errors affect Google Search. We cover the top 20 status codes that Googlebot encountered on the web, and the most prominent network and DNS errors. More exotic status codes, such as 418 (I'm a teapot), aren't covered. All issues mentioned on this page generate a corresponding error or warning in Search Console's Page Indexing report.

HTTP status codes are generated by the server that's hosting the site when it responds to a request made by a client, for example a browser or a crawler. Every HTTP status code has a different meaning, but often the outcome of the request is the same. For example, there are multiple status codes that signal redirection, but their outcome is the same.

Search Console generates error messages for status codes in the 4xx–5xx range, and for failed redirections (3xx). If the server responded with a 2xx status code, the content received in the response may be considered for indexing.

The following table contains the most encountered HTTP status codes by Googlebot and an explanation how Google handles each status code.

Google considers the content for indexing. If the content suggests an error, for example an empty page or an error message, Search Console will show a soft 404 error.

Google passes on the content to the indexing pipeline. The indexing systems may index the content, but that's not guaranteed.

Googlebot waits for the content for a limited time, then passes on whatever it received to the indexing pipeline. The timeout is user agent dependent, for example Googlebot Smartphone may have a different timeout than Googlebot Image.

Googlebot signals the indexing pipeline that it received no content. Search Console may show a soft 404 error in the site's Page Indexing report.

Googlebot follows up to 10 redirect hops. If the crawler doesn't receive content within 10 hops, Search Console will show a redirect error in the site's Page Indexing report. The number of hops Googlebot follows is user agent dependent; for example, Googlebot Smartphone may have a different value than Googlebot Image.

Any content Googlebot received from the redirecting URL is ignored, and the final target URL's content is considered for indexing. For robots.txt files, learn how Google handles a robots.txt that returns a 3xx status code.

Googlebot follows the redirect, and the indexing pipeline uses the redirect as a strong signal that the redirect target should be canonical

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
dig +nocmd example.com a +noall +answer
```

Example 2 (unknown):
```unknown
dig +nocmd www.example.com cname +noall +answer
```

Example 3 (unknown):
```unknown
dig +nocmd example.com ns +noall +answer
example.com.    86400  IN  NS  a.iana-servers.net.
example.com.    86400  IN  NS  b.iana-servers.net.
dig +nocmd @a.iana-servers.net example.com +noall +answer
example.com.    86400  IN  A  93.184.216.34
dig +nocmd @b.iana-servers.net example.com +noall +answer
...
```

---
