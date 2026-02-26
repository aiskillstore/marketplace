# Google-Search-Docs - Guides

**Pages:** 3

---

## General structured data guidelines

**URL:** https://developers.google.com/search/docs/guides/sd-policies

**Contents:**
- General structured data guidelines
- Technical guidelines
  - Format
  - Access
- Quality guidelines
  - Content
  - Relevance
  - Completeness
  - Location
  - Specificity

To be eligible for rich result appearance in Google Search results, structured data shouldn't violate the Content policies for Google Search (which include our spam policies). In addition, this page details the general guidelines that apply to all structured data: they must be followed in order to be eligible for appearance as a rich result in Google Search.

If your page contains a structured data issue, it can result in a manual action. A structured data manual action means that a page loses eligibility for appearance as a rich result; it doesn't affect how the page ranks in Google web search. To check if you have a manual action, open the Manual Actions report in Search Console.

Important: Google does not guarantee that your structured data will show up in search results, even if your page is marked up correctly according to the Rich Results Test. Here are some common reasons why:

You can test compliance with technical guidelines using the Rich Results Test and the URL Inspection tool, which catch most technical errors.

In order to be eligible for rich results, mark up your site's pages using one of three supported formats:

Do not block your structured data pages to Googlebot using robots.txt, noindex, or any other access control methods.

These quality guidelines are not easily testable using an automated tool. Violating a quality guideline can prevent syntactically correct structured data from being displayed as a rich result in Google Search, or possibly cause it to be marked as spam.

Your structured data must be a true representation of the page content. Here are some examples of irrelevant data:

Multiple items on a page means that there is more than one kind of thing on a page. For example, a page could contain a recipe, a video that shows how to make that recipe, and breadcrumb information for how people can discover that recipe. All of this user-visible information can also be marked up with structured data, which makes it easier for search engines like Google Search to understand the information on a page. When you add more items that apply to a page, Google Search has a fuller picture of what the page is about and can display that page in different search features.

Google Search understands multiple items on a page, whether you nest the items or specify each item individually: Nesting: When there is one main item, and additional items are grouped under the main item. This is particularly helpful when grouping related items (for example, 

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<html>
  <head>
    <title>How To Make Banana Bread</title>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org/",
      "@type": "Recipe",
      "name": "Banana Bread Recipe",
      "description": "The best banana bread recipe you'll ever find! Learn how to use up all those extra bananas.",
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": 4.7,
        "ratingCount": 123
      },
      "video": {
        "@type": "VideoObject",
        "name": "How To Make Banana Bread",
        "description": "This is how you make banana bre
...
```

Example 2 (unknown):
```unknown
<html>
  <head>
    <title>How To Make Banana Bread</title>
    <script type="application/ld+json">
    [{
      "@context": "https://schema.org/",
      "@type": "Recipe",
      "name": "Banana Bread Recipe",
      "description": "The best banana bread recipe you'll ever find! Learn how to use up all those extra bananas."
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [{
        "@type": "ListItem",
        "position": 1,
        "name": "Recipes",
        "item": "https://example.com/recipes"
      },{
        "@type": "ListItem
...
```

---

## Debugging your pages

**URL:** https://developers.google.com/search/docs/guides/debug

**Contents:**
- Debugging your pages
- General tips
- Useful testing tools
  - Verified site owner tools
  - Anonymous tools
  - More tools
- Testing locally-hosted or firewalled pages
  - Debugging access errors

Remember that Google does not crawl your page immediately after you publish a fix. Therefore Search Console (and Google Search) can continue to show an error for a page that you have fixed until the page is crawled again. You can sometimes request an expedited crawl, for example using the URL Inspection tool, but in most cases it takes a few days to notice changes in your pages.

Here are some useful tools to help you debug your pages.

The following tools and reports require you to be a verified site user for the page in order to use this tool on that page or site. This is because Search Console provides confidential site data that only a verified site user should have access to.

These tools can be used on any URL without needing Search Console permissions on the website. Some tools also allow code snippets pasted into the tool itself.

If your URL is behind a firewall, or is hosted on a local computer, you can use a tunnelling solution to expose your page to the testing tool. Learn how to test locally-hosted or firewalled pages.

See our help page for more resources and office hours information.

Google provides several testing tools to test a single live web page. For example, the AMP Test Tool and the Rich Results Test. However, if your page is running on your local machine without a public URL, or if it is hosted behind a firewall, you can still test the page by exposing a tunnel to your page for the testing tool. This can be useful if you want to test a page before making it publicly available on the web, or even as another step in your release process.

To test a local or firewalled page, use a tunneling solution such as ngrok. These tools provide a public URL that connects to a non-public page on your local host or firewalled server.

The following example first starts up python's SimpleHTTPServer to host a page on the local computer, then uses ngrok to expose that page on a publicly-accessible URL:

Start up a local HTTP server to host your page on a given port. For our example we chose port 5326.

SimpleHTTPServer maps the current directory as the site root.

On another terminal, start up your local ngrok app, listening to port 5326, which we opened in step 1.

Pass your exposed ngrok URL to the test tool of your choice.

The root URL in our example is http://ad0a5735.ngrok.io, so if our page is saved locally at ~/testwebdir/mypage.html, and we started the server above from ~/testwebdir/, we could test http://ad0a5735.ngrok.io/mypage.html. In th

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
python3 -m http.server 5326
Serving HTTP on 0.0.0.0 port 5326
...
```

Example 2 (unknown):
```unknown
./ngrok http 5326 --request-header-add ngrok-skip-browser-warning:1
ngrok by @inconshreveable (Ctrl+C to quit)

Session Status online
Version 2.2.4
Region United States (us)
Web Interface http://127.0.0.1:4040
Forwarding http://ad0a5735.ngrok.io -> localhost:5326
Forwarding https://ad0a5735.ngrok.io -> localhost:5326

Connections ttl opn rt1 rt5 p50 p90
0 0 0.00 0.00 0.00 0.00
```

---

## Fix lazy-loaded content

**URL:** https://developers.google.com/search/docs/guides/lazy-loading

**Contents:**
- Fix lazy-loaded content
- Load content when it's visible in the viewport
- Support paginated loading for infinite scroll
- Test

Deferring loading of non-critical or non-visible content, also commonly known as "lazy-loading", is a common performance and UX best practice. For more information, see web.dev's resources on lazy-loading images and video. However, if not implemented correctly, this technique can inadvertently hide content from Google. This document explains how to make sure Google can crawl and index lazy-loaded content.

To ensure that Google sees all content on your page, make sure that your lazy-loading implementation loads all relevant content whenever it is visible in the viewport. Here are a few methods to implement lazy-loading:

The methods mentioned don't rely on user actions, such as scrolling or clicking, to load content, which is important as Google Search does not interact with your page.

Don't add lazy-loading to content that is likely to be immediately visible when a user opens a page. That might cause content to take longer to load and show up in the browser, which will be very noticeable to the user.

Make sure to test your implementation.

At a high level, infinite scroll is a technique that loads more content, more distinct pages, as the user scrolls down a long page. This could be one long article that's split into multiple chunks, or a collection of items that's similarly split into chunks. To implement infinite scroll in an indexable way, make sure your website supports paginated loading of these chunks by doing the following:

After you set up your implementation, make sure it works correctly. You can use the URL Inspection Tool in Search Console to see if all content was loaded. Check the rendered HTML to make sure your content is in the rendered HTML by looking for it in URL Inspection Tool. If your image or video URLs appear in the src attribute on the <img> or <video> elements in the rendered HTML, your setup works correctly.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-03-06 UTC.

---
