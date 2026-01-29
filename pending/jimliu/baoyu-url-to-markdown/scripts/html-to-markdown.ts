export interface PageMetadata {
  url: string;
  title: string;
  description?: string;
  author?: string;
  published?: string;
  captured_at: string;
}

export interface ConversionResult {
  metadata: PageMetadata;
  markdown: string;
}

export const cleanupAndExtractScript = `
(function() {
  const removeSelectors = [
    'script', 'style', 'noscript', 'iframe', 'svg', 'canvas',
    'header nav', 'footer', '.sidebar', '.nav', '.navigation',
    '.advertisement', '.ad', '.ads', '.cookie-banner', '.popup',
    '[role="banner"]', '[role="navigation"]', '[role="complementary"]'
  ];

  for (const sel of removeSelectors) {
    try {
      document.querySelectorAll(sel).forEach(el => el.remove());
    } catch {}
  }

  document.querySelectorAll('*').forEach(el => {
    el.removeAttribute('style');
    el.removeAttribute('onclick');
    el.removeAttribute('onload');
    el.removeAttribute('onerror');
  });

  const baseUrl = document.baseURI || location.href;
  document.querySelectorAll('a[href]').forEach(a => {
    try {
      const href = a.getAttribute('href');
      if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
        a.setAttribute('href', new URL(href, baseUrl).href);
      }
    } catch {}
  });
  document.querySelectorAll('img[src]').forEach(img => {
    try {
      const src = img.getAttribute('src');
      if (src) img.setAttribute('src', new URL(src, baseUrl).href);
    } catch {}
  });

  const getMeta = (names) => {
    for (const name of names) {
      const el = document.querySelector(\`meta[name="\${name}"], meta[property="\${name}"]\`);
      if (el) {
        const content = el.getAttribute('content');
        if (content) return content.trim();
      }
    }
    return undefined;
  };

  const getTitle = () => {
    const ogTitle = getMeta(['og:title', 'twitter:title']);
    if (ogTitle) return ogTitle;
    const h1 = document.querySelector('h1');
    if (h1) return h1.textContent?.trim();
    return document.title?.trim() || '';
  };

  const getPublished = () => {
    const timeEl = document.querySelector('time[datetime]');
    if (timeEl) return timeEl.getAttribute('datetime');
    return getMeta(['article:published_time', 'datePublished', 'date']);
  };

  const main = document.querySelector('main, article, [role="main"], .main-content, .post-content, .article-content, .content');
  const html = main ? main.innerHTML : document.body.innerHTML;

  return {
    title: getTitle(),
    description: getMeta(['description', 'og:description', 'twitter:description']),
    author: getMeta(['author', 'article:author', 'twitter:creator']),
    published: getPublished(),
    html: html
  };
})()
`;

function decodeHtmlEntities(text: string): string {
  return text
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x27;/g, "'")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(parseInt(n, 10)))
    .replace(/&#x([0-9a-fA-F]+);/g, (_, n) => String.fromCharCode(parseInt(n, 16)));
}

function stripTags(html: string): string {
  return html.replace(/<[^>]+>/g, '');
}

function normalizeWhitespace(text: string): string {
  return text.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
}

export function htmlToMarkdown(html: string): string {
  let md = html;

  md = md.replace(/<br\s*\/?>/gi, '\n');
  md = md.replace(/<hr\s*\/?>/gi, '\n\n---\n\n');

  md = md.replace(/<h1[^>]*>([\s\S]*?)<\/h1>/gi, (_, c) => `\n\n# ${stripTags(c).trim()}\n\n`);
  md = md.replace(/<h2[^>]*>([\s\S]*?)<\/h2>/gi, (_, c) => `\n\n## ${stripTags(c).trim()}\n\n`);
  md = md.replace(/<h3[^>]*>([\s\S]*?)<\/h3>/gi, (_, c) => `\n\n### ${stripTags(c).trim()}\n\n`);
  md = md.replace(/<h4[^>]*>([\s\S]*?)<\/h4>/gi, (_, c) => `\n\n#### ${stripTags(c).trim()}\n\n`);
  md = md.replace(/<h5[^>]*>([\s\S]*?)<\/h5>/gi, (_, c) => `\n\n##### ${stripTags(c).trim()}\n\n`);
  md = md.replace(/<h6[^>]*>([\s\S]*?)<\/h6>/gi, (_, c) => `\n\n###### ${stripTags(c).trim()}\n\n`);

  md = md.replace(/<strong[^>]*>([\s\S]*?)<\/strong>/gi, (_, c) => `**${stripTags(c).trim()}**`);
  md = md.replace(/<b[^>]*>([\s\S]*?)<\/b>/gi, (_, c) => `**${stripTags(c).trim()}**`);
  md = md.replace(/<em[^>]*>([\s\S]*?)<\/em>/gi, (_, c) => `*${stripTags(c).trim()}*`);
  md = md.replace(/<i[^>]*>([\s\S]*?)<\/i>/gi, (_, c) => `*${stripTags(c).trim()}*`);
  md = md.replace(/<del[^>]*>([\s\S]*?)<\/del>/gi, (_, c) => `~~${stripTags(c).trim()}~~`);
  md = md.replace(/<s[^>]*>([\s\S]*?)<\/s>/gi, (_, c) => `~~${stripTags(c).trim()}~~`);
  md = md.replace(/<mark[^>]*>([\s\S]*?)<\/mark>/gi, (_, c) => `==${stripTags(c).trim()}==`);

  md = md.replace(/<a[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi, (_, href, text) => {
    const t = stripTags(text).trim();
    if (!t || href.startsWith('javascript:')) return t;
    return `[${t}](${href})`;
  });

  md = md.replace(/<img[^>]*src=["']([^"']+)["'][^>]*alt=["']([^"']*)["'][^>]*\/?>/gi, (_, src, alt) => `![${alt}](${src})`);
  md = md.replace(/<img[^>]*alt=["']([^"']*)["'][^>]*src=["']([^"']+)["'][^>]*\/?>/gi, (_, alt, src) => `![${alt}](${src})`);
  md = md.replace(/<img[^>]*src=["']([^"']+)["'][^>]*\/?>/gi, (_, src) => `![](${src})`);

  md = md.replace(/<pre[^>]*><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi, (_, code) => `\n\n\`\`\`\n${decodeHtmlEntities(stripTags(code)).trim()}\n\`\`\`\n\n`);
  md = md.replace(/<pre[^>]*>([\s\S]*?)<\/pre>/gi, (_, code) => `\n\n\`\`\`\n${decodeHtmlEntities(stripTags(code)).trim()}\n\`\`\`\n\n`);
  md = md.replace(/<code[^>]*>([\s\S]*?)<\/code>/gi, (_, code) => `\`${decodeHtmlEntities(stripTags(code)).trim()}\``);

  md = md.replace(/<blockquote[^>]*>([\s\S]*?)<\/blockquote>/gi, (_, content) => {
    const lines = stripTags(content).trim().split('\n');
    return '\n\n' + lines.map(l => `> ${l.trim()}`).join('\n') + '\n\n';
  });

  md = md.replace(/<ul[^>]*>([\s\S]*?)<\/ul>/gi, (_, items) => {
    const lis = items.match(/<li[^>]*>([\s\S]*?)<\/li>/gi) || [];
    const lines = lis.map(li => {
      const content = li.replace(/<li[^>]*>([\s\S]*?)<\/li>/i, '$1');
      return `- ${stripTags(content).trim()}`;
    });
    return '\n\n' + lines.join('\n') + '\n\n';
  });

  md = md.replace(/<ol[^>]*>([\s\S]*?)<\/ol>/gi, (_, items) => {
    const lis = items.match(/<li[^>]*>([\s\S]*?)<\/li>/gi) || [];
    const lines = lis.map((li, i) => {
      const content = li.replace(/<li[^>]*>([\s\S]*?)<\/li>/i, '$1');
      return `${i + 1}. ${stripTags(content).trim()}`;
    });
    return '\n\n' + lines.join('\n') + '\n\n';
  });

  md = md.replace(/<table[^>]*>([\s\S]*?)<\/table>/gi, (_, table) => {
    const rows: string[][] = [];
    const trMatches = table.match(/<tr[^>]*>([\s\S]*?)<\/tr>/gi) || [];
    for (const tr of trMatches) {
      const cells: string[] = [];
      const cellMatches = tr.match(/<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/gi) || [];
      for (const cell of cellMatches) {
        const content = cell.replace(/<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/i, '$1');
        cells.push(stripTags(content).trim().replace(/\|/g, '\\|'));
      }
      if (cells.length > 0) rows.push(cells);
    }
    if (rows.length === 0) return '';
    const colCount = Math.max(...rows.map(r => r.length));
    const normalizedRows = rows.map(r => {
      while (r.length < colCount) r.push('');
      return r;
    });
    const header = `| ${normalizedRows[0].join(' | ')} |`;
    const sep = `| ${normalizedRows[0].map(() => '---').join(' | ')} |`;
    const body = normalizedRows.slice(1).map(r => `| ${r.join(' | ')} |`).join('\n');
    return '\n\n' + header + '\n' + sep + (body ? '\n' + body : '') + '\n\n';
  });

  md = md.replace(/<p[^>]*>([\s\S]*?)<\/p>/gi, (_, c) => `\n\n${stripTags(c).trim()}\n\n`);
  md = md.replace(/<div[^>]*>([\s\S]*?)<\/div>/gi, (_, c) => `\n${stripTags(c).trim()}\n`);
  md = md.replace(/<span[^>]*>([\s\S]*?)<\/span>/gi, (_, c) => stripTags(c));

  md = stripTags(md);
  md = decodeHtmlEntities(md);
  md = normalizeWhitespace(md);

  return md;
}

export function formatMetadataYaml(meta: PageMetadata): string {
  const lines = ['---'];
  lines.push(`url: ${meta.url}`);
  lines.push(`title: "${meta.title.replace(/"/g, '\\"')}"`);
  if (meta.description) lines.push(`description: "${meta.description.replace(/"/g, '\\"')}"`);
  if (meta.author) lines.push(`author: "${meta.author.replace(/"/g, '\\"')}"`);
  if (meta.published) lines.push(`published: "${meta.published}"`);
  lines.push(`captured_at: "${meta.captured_at}"`);
  lines.push('---');
  return lines.join('\n');
}

export function createMarkdownDocument(result: ConversionResult): string {
  const yaml = formatMetadataYaml(result.metadata);
  const titleRegex = new RegExp(`^#\\s+${result.metadata.title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*\\n`, 'i');
  const hasTitle = titleRegex.test(result.markdown);
  const title = result.metadata.title && !hasTitle ? `\n\n# ${result.metadata.title}\n\n` : '\n\n';
  return yaml + title + result.markdown;
}
