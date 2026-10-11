#!/usr/bin/env node
/*
 * refresh-m3.js — re-scrape m3.material.io so this skill can be updated when Material changes.
 *
 * Why this exists: m3.material.io is an Angular SPA. Fetching the page HTML gives you a title and
 * nothing else, so WebFetch/curl on a guideline URL returns an empty shell. The real content is
 * fetched at runtime as JSON. This script follows the same path the site does:
 *
 *   1. GET /                             -> find the hashed main bundle, e.g. /static/angular/main.<hash>.js
 *   2. grep the bundle for carbonVersion:"<YYYY-MM-DD_HH-MM-SS>"   (the content snapshot id)
 *   3. grep the bundle for the route table: {"slug":..,"exportedCarbonFileId":"<uuid>.json",..}
 *   4. GET /_dsm/content/m3/<carbonVersion>/<uuid>.json            (the actual page body)
 *
 * Caveat: steps 2–3 read minified JS, so they are the fragile part. If Material reorganizes its
 * bundle these regexes break — re-derive them by searching the bundle for "carbonVersion" and for a
 * known slug such as "building-with-m3-expressive".
 *
 * Usage:
 *   node refresh-m3.js routes                    list every slug -> content id
 *   node refresh-m3.js pages   <outdir>          write every page as markdown
 *   node refresh-m3.js images  <outdir>          write every page image + INDEX.tsv
 *
 * Token VALUES (type scale, springs, shape, elevation) do not live on the site — they load from a
 * separate design-system service that this script does not reach. Get those from the generated
 * androidx sources instead, which are plain text on GitHub:
 *   https://raw.githubusercontent.com/androidx/androidx/androidx-main/compose/material3/material3/
 *     src/commonMain/kotlin/androidx/compose/material3/tokens/{TypeScaleTokens,ShapeTokens,
 *     ExpressiveMotionTokens,StandardMotionTokens,ElevationTokens,MotionTokens}.kt
 *   .../androidx/compose/material3/MaterialShapes.kt      (the 35 shape names)
 */
'use strict';
const fs = require('fs');
const path = require('path');
const https = require('https');

const HOST = 'https://m3.material.io';

function get(url, binary, depth = 0) {
  return new Promise((resolve, reject) => {
    if (depth > 5) return reject(new Error('too many redirects'));
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        return get(new URL(res.headers.location, url).href, binary, depth + 1).then(resolve, reject);
      }
      if (res.statusCode !== 200) { res.resume(); return reject(new Error('HTTP ' + res.statusCode + ' ' + url)); }
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => resolve(binary ? Buffer.concat(chunks) : Buffer.concat(chunks).toString('utf8')));
    }).on('error', reject);
  });
}

let _bundle = null;
async function bundle() {
  if (_bundle) return _bundle;
  const html = await get(HOST + '/');
  const m = html.match(/\/static\/angular\/main\.[a-f0-9]+\.js/);
  if (!m) throw new Error('main bundle not found in homepage HTML — site structure changed');
  _bundle = await get(HOST + m[0]);
  return _bundle;
}

async function carbonVersion() {
  const m = (await bundle()).match(/carbonVersion:"([^"]+)"/);
  if (!m) throw new Error('carbonVersion not found in bundle — site structure changed');
  return m[1];
}

async function routes() {
  const src = await bundle();
  const re = /"slug":"([^"]+)","exportedCarbonFileId":"([0-9a-f-]+\.json)","carbonPath":"([^"]+)"/g;
  const out = [];
  let m;
  while ((m = re.exec(src))) out.push({ slug: m[1], fileId: m[2], carbonPath: m[3] });
  const seen = new Set();
  const uniq = out.filter(r => !seen.has(r.fileId) && seen.add(r.fileId));
  if (!uniq.length) throw new Error('route table not found in bundle — site structure changed');
  return uniq;
}

const pageUrl = (v, fileId) => `${HOST}/_dsm/content/m3/${v}/${fileId}`;

// --- HTML fragment -> markdown -------------------------------------------------
function html2md(h) {
  if (!h) return '';
  let s = h;
  s = s.replace(/<br\s*\/?>/gi, '\n');
  for (const n of [1, 2, 3, 4, 5]) {
    s = s.replace(new RegExp(`<h${n}[^>]*>(.*?)</h${n}>`, 'gis'), (_, t) => '\n' + '#'.repeat(n) + ' ' + t.trim() + '\n');
  }
  s = s.replace(/<li[^>]*>(.*?)<\/li>/gis, (_, t) => '- ' + t.trim().replace(/\n+/g, ' ') + '\n');
  s = s.replace(/<\/?(ul|ol)[^>]*>/gi, '\n');
  s = s.replace(/<a [^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gis, (_, href, t) => `[${t.trim()}](${href})`);
  s = s.replace(/<(strong|b)>(.*?)<\/\1>/gis, (_, __, t) => '**' + t.trim() + '**');
  s = s.replace(/<(em|i)>(.*?)<\/\1>/gis, (_, __, t) => '*' + t.trim() + '*');
  s = s.replace(/<code[^>]*>(.*?)<\/code>/gis, (_, t) => '`' + t.trim() + '`');
  s = s.replace(/<p[^>]*>/gi, '\n').replace(/<\/p>/gi, '\n');
  s = s.replace(/<\/tr>/gi, '\n').replace(/<\/t[dh]>/gi, ' | ');
  s = s.replace(/<[^>]+>/g, '');
  s = s.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
       .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&rsquo;/g, '’').replace(/&mdash;/g, '—');
  return s.replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
}
const strip = h => html2md(h).replace(/\n/g, ' ').trim();

function pageToMd(d) {
  const L = ['# ' + (d.headerTitle || d.title || '(untitled)')];
  if (d.description) L.push('\n> ' + strip(d.description));
  L.push('\nslug: ' + d.slug + '  |  updated: ' + (d.updatedTimestamp || '?'));
  for (const sec of d.sections || []) {
    if (sec.name && sec.isVisible !== false) L.push('\n<!-- section: ' + sec.name + ' -->');
    for (const blk of sec.contentBlocks || []) {
      if (blk.isHidden) continue;
      if (blk.title) L.push('\n### ' + blk.title);
      for (const ch of blk.contentChunks || []) {
        const parts = [];
        const md = html2md(ch.htmlValue);
        if (md) parts.push(md);
        for (const k of ['title', 'subtitle', 'caption', 'footer', 'altText', 'label', 'description']) {
          if (typeof ch[k] === 'string' && ch[k]) {
            const v = strip(ch[k]);
            if (v && !parts.join('\n').includes(v)) parts.push('_' + k + ': ' + v + '_');
          }
        }
        if (ch.linkUrl) parts.push('_link: ' + ch.linkUrl + (ch.linkText ? ' (' + ch.linkText + ')' : '') + '_');
        if (ch.snippetCode) parts.push('```' + (ch.snippetLanguage || '') + '\n' + ch.snippetCode + '\n```');
        if (parts.length) L.push('\n' + parts.join('\n'));
      }
    }
  }
  return L.join('\n').replace(/\n{3,}/g, '\n\n') + '\n';
}

// --- concurrency --------------------------------------------------------------
async function pool(items, worker, conc = 12) {
  let i = 0;
  await Promise.all(Array.from({ length: Math.min(conc, items.length) }, async () => {
    while (i < items.length) await worker(items[i++]);
  }));
}

(async () => {
  const [cmd, outdir] = process.argv.slice(2);

  if (cmd === 'routes') {
    for (const r of await routes()) console.log([r.slug, r.carbonPath, r.fileId].join('\t'));
    return;
  }

  if (cmd === 'pages') {
    if (!outdir) throw new Error('usage: refresh-m3.js pages <outdir>');
    const v = await carbonVersion();
    const rs = await routes();
    fs.mkdirSync(outdir, { recursive: true });
    console.error(`carbonVersion=${v}  routes=${rs.length}`);
    let ok = 0, bad = 0;
    await pool(rs, async r => {
      try {
        const d = JSON.parse(await get(pageUrl(v, r.fileId)));
        fs.writeFileSync(path.join(outdir, r.slug.replace(/[\/\\]/g, '_') + '.md'), pageToMd(d));
        ok++;
      } catch (e) { bad++; console.error('  fail ' + r.slug + ': ' + e.message); }
    });
    console.error(`wrote ${ok} pages, ${bad} failed`);
    return;
  }

  if (cmd === 'images') {
    if (!outdir) throw new Error('usage: refresh-m3.js images <outdir>');
    const v = await carbonVersion();
    const rs = await routes();
    fs.mkdirSync(outdir, { recursive: true });

    // collect (slug, url, caption) for every image chunk
    const found = [];
    await pool(rs, async r => {
      let d;
      try { d = JSON.parse(await get(pageUrl(v, r.fileId))); } catch (e) { return; }
      for (const sec of d.sections || []) for (const blk of sec.contentBlocks || []) {
        if (blk.isHidden) continue;
        for (const ch of blk.contentChunks || []) {
          if (!ch.imageUrl || !/^https?:/.test(ch.imageUrl)) continue;
          found.push({ slug: r.slug, url: ch.imageUrl, cap: strip(ch.footer) || strip(ch.altText) || strip(blk.title) || '' });
        }
      }
    });
    console.error('images found: ' + found.length);

    // reserve filenames up front so workers never collide
    const taken = new Set();
    for (const f of found) {
      const sub = f.slug.replace(/[\/\\]/g, '_');
      const base = (f.cap || 'image').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 70) || 'image';
      const ext = (f.url.match(/\.(png|jpe?g|gif|webp|svg)/i) || [, 'png'])[1].toLowerCase();
      let rel = `${sub}/${base}.${ext}`, k = 2;
      while (taken.has(rel)) rel = `${sub}/${base}-${k++}.${ext}`;
      taken.add(rel);
      f.rel = rel;
    }
    for (const s of new Set(found.map(f => f.rel.split('/')[0]))) fs.mkdirSync(path.join(outdir, s), { recursive: true });

    const idx = [];
    let ok = 0, bad = 0;
    await pool(found, async f => {
      const dest = path.join(outdir, f.rel);
      if (fs.existsSync(dest) && fs.statSync(dest).size > 500) { idx.push(f.rel + '\t' + f.cap); ok++; return; }
      for (let a = 0; a < 3; a++) {
        try {
          const buf = await get(f.url, true);
          if (buf.length < 500) break;
          fs.writeFileSync(dest, buf);
          idx.push(f.rel + '\t' + f.cap);
          ok++;
          return;
        } catch (e) { await new Promise(r => setTimeout(r, 400 * (a + 1))); }
      }
      bad++;
    }, 16);
    idx.sort();
    fs.writeFileSync(path.join(outdir, 'INDEX.tsv'), idx.join('\n') + '\n');
    console.error(`downloaded ${ok}, failed ${bad}`);
    return;
  }

  console.error('usage: refresh-m3.js routes | pages <outdir> | images <outdir>');
  process.exit(1);
})().catch(e => { console.error('ERROR: ' + e.message); process.exit(1); });
