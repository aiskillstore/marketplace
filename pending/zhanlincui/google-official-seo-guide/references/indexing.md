# Google-Search-Docs - Indexing

**Pages:** 1

---

## Video SEO best practices

**URL:** https://developers.google.com/search/docs/appearance/video#indexing-criteria

**Contents:**
- Video SEO best practices
- Help Google find your videos
- Ensure your videos can be indexed
  - Use a supported video file type
  - Use stable URLs
  - Create a dedicated watch page for each video
  - Using third-party embedded players
- Which URL is which?
  - Provide a high-quality video thumbnail
  - Provide consistent and unique information in your structured data

If you have videos on your site, following these video SEO best practices can help more people find your site through video results on Google. Videos can appear in several different places on Google, including the main search results page, Video mode, Google Images, and Discover:

Optimize your videos to appear on Google by following these best practices:

The technical requirements for getting your content in Google's search results applies to videos too. There are some additional requirements to making your videos eligible to be discovered, crawled, and indexed by Google Search:

To make it easier for Google to find your videos, we recommend providing metadata about the video. We support structured data, video sitemaps, and the Open Graph protocol (OGP).

To be eligible for video features, a video must meet the following indexing requirements:

To be eligible for video features, use a supported video file type. Google can process the following video file types: 3GP, 3G2, ASF, AVI, DivX, M2V, M3U, M3U8, M4V, MKV, MOV, MP4, MPEG, OGV, QVT, RAM, RM, VOB, WebM, WMV, and XAP.

Data URLs aren't supported.

Some CDNs use quickly expiring URLs. If the video's thumbnail URL changes too often, Google may not be able to successfully index your videos. To make sure your videos can be indexed, use a single unique and stable thumbnail URL for each video.

To make your videos eligible for specific features like key moments and video previews, make sure your video files are available at stable URLs too. This also helps Google discover and process the videos consistently, confirm they are still available, and collect signals on the videos.

If you are concerned about bad actors (for example, hackers or spammers) accessing your content, you can verify Googlebot before displaying a stable version of your media URLs. For example, you can choose to serve the contentUrl property only to trusted clients like Googlebot, whereas other clients accessing your page wouldn't see that field. With this setup, only trusted clients will be able to access the location of your video file.

To be eligible for video features (including video results on the main search results page, Video mode, Key Moments, the Live Badge, and other rich formats), create a dedicated watch page for each video, if it makes sense for your business.

A watch page's main purpose is to show users a single video. The following pages are watch pages because watching an individual video is the main reason the user is

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
<url>
<loc>https://example.com/videos/some_video_landing_page.html</loc>
  <video:video>
  ...
```

Example 2 (unknown):
```unknown
<iframe src="https://example.com/videoplayer.php?video=123" width="640" height="360" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>
```

Example 3 (unknown):
```unknown
"embedUrl": "https://example.com/videoplayer.php?video=123"
```

Example 4 (unknown):
```unknown
<video:player_loc>https://example.com/videoplayer.php?video=123</video:player_loc>
```

---
