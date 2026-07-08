#!/usr/bin/env node

import puppeteer from "puppeteer-core";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const profileDir = `${process.env.HOME}/.cache/scraping-web-browser`;
const portFile = join(profileDir, "port.txt");

if (!existsSync(portFile)) {
  console.error("✗ Browser not started. Run 'node scripts/start.js' first.");
  process.exit(1);
}

const port = parseInt(readFileSync(portFile, "utf-8").trim());

const b = await puppeteer.connect({
  browserURL: `http://localhost:${port}`,
  defaultViewport: null,
});

const p = (await b.pages()).at(-1);

if (!p) {
  console.error("✗ No active tab found");
  process.exit(1);
}

try {
  const metadata = await p.evaluate(() => {
    const metaTags = {};
    document.querySelectorAll('meta').forEach(meta => {
      const name = meta.name || meta.property || meta.httpEquiv;
      if (name) {
        metaTags[name] = meta.content;
      }
    });

    const links = {};
    document.querySelectorAll('link[rel]').forEach(link => {
      const rel = link.rel;
      if (!links[rel]) links[rel] = [];
      links[rel].push(link.href);
    });

    const openGraph = {};
    document.querySelectorAll('meta[property^="og:"]').forEach(meta => {
      const property = meta.property;
      if (property) {
        openGraph[property.substring(3)] = meta.content;
      }
    });

    const twitterCard = {};
    document.querySelectorAll('meta[name^="twitter:"]').forEach(meta => {
      const name = meta.name;
      if (name) {
        twitterCard[name.substring(8)] = meta.content;
      }
    });

    const jsonLd = [];
    document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
      try {
        jsonLd.push(JSON.parse(script.textContent));
      } catch (e) {
        // Ignore invalid JSON-LD
      }
    });

    return {
      url: window.location.href,
      title: document.title,
      description: metaTags.description || null,
      keywords: metaTags.keywords || null,
      author: metaTags.author || null,
      canonical: links.canonical?.[0] || null,
      openGraph,
      twitterCard,
      metaTags,
      links,
      jsonLd,
    };
  });

  console.log("Page Metadata");
  console.log("=".repeat(80));

  console.log(`\nURL: ${metadata.url}`);
  console.log(`Title: ${metadata.title}`);

  if (metadata.description) {
    console.log(`\nDescription: ${metadata.description}`);
  }

  if (metadata.keywords) {
    console.log(`Keywords: ${metadata.keywords}`);
  }

  if (metadata.author) {
    console.log(`Author: ${metadata.author}`);
  }

  if (metadata.canonical) {
    console.log(`Canonical: ${metadata.canonical}`);
  }

  if (Object.keys(metadata.openGraph).length > 0) {
    console.log("\nOpen Graph:");
    for (const [key, value] of Object.entries(metadata.openGraph)) {
      console.log(`  ${key}: ${value}`);
    }
  }

  if (Object.keys(metadata.twitterCard).length > 0) {
    console.log("\nTwitter Card:");
    for (const [key, value] of Object.entries(metadata.twitterCard)) {
      console.log(`  ${key}: ${value}`);
    }
  }

  if (Object.keys(metadata.links).length > 0) {
    console.log("\nLinks:");
    for (const [rel, hrefs] of Object.entries(metadata.links)) {
      console.log(`  ${rel}:`);
      hrefs.forEach(href => console.log(`    - ${href}`));
    }
  }

  if (metadata.jsonLd.length > 0) {
    console.log("\nJSON-LD:");
    metadata.jsonLd.forEach((data, i) => {
      console.log(`  [${i + 1}] ${data['@type'] || 'Unknown'}`);
      console.log(`    ${JSON.stringify(data, null, 2).split('\n').slice(1, -1).join('\n    ')}`);
    });
  }

  if (Object.keys(metadata.metaTags).length > 20) {
    console.log("\nOther Meta Tags (first 20):");
    const keys = Object.keys(metadata.metaTags).slice(0, 20);
    keys.forEach(key => {
      if (!['description', 'keywords', 'author'].includes(key)) {
        console.log(`  ${key}: ${metadata.metaTags[key]}`);
      }
    });
  }

} catch (error) {
  console.error(`✗ Error: ${error.message}`);
  process.exit(1);
}

await b.disconnect();