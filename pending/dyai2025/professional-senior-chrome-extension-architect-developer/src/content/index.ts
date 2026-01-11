import type { AnalysisRequest, PageSnapshotResponse, RequestPageSnapshot } from '../shared/contracts.js';

function collectPageSnapshot(): PageSnapshotResponse['payload'] {
  const title = document.title;
  const description = document.querySelector('meta[name="description"]')?.getAttribute('content') || '';
  const headings = Array.from(document.querySelectorAll('h1, h2, h3')).map((node) => node.textContent?.trim() || '');
  const bodyText = document.body?.innerText || '';
  const wordCount = bodyText.split(/\s+/).filter(Boolean).length;
  const images = Array.from(document.querySelectorAll('img')).map((img) => ({
    alt: img.getAttribute('alt'),
    src: img.src,
  }));
  const links = Array.from(document.querySelectorAll('a')).map((link) => ({
    href: link.href,
    text: link.textContent?.trim() || '',
  }));

  return {
    url: window.location.href,
    title,
    description,
    headings,
    wordCount,
    images,
    links,
  };
}

function attachAnalysisButton(): void {
  const existing = document.getElementById('ai-seo-analyzer-floating-button');
  if (existing) return;

  const button = document.createElement('button');
  button.id = 'ai-seo-analyzer-floating-button';
  button.textContent = 'Analyze SEO';
  button.style.position = 'fixed';
  button.style.bottom = '16px';
  button.style.right = '16px';
  button.style.zIndex = '2147483647';
  button.style.background = '#0f766e';
  button.style.color = '#fff';
  button.style.border = 'none';
  button.style.borderRadius = '999px';
  button.style.padding = '10px 16px';
  button.style.boxShadow = '0 4px 10px rgba(0,0,0,0.2)';
  button.style.cursor = 'pointer';
  button.style.fontSize = '14px';

  button.addEventListener('click', async () => {
    const snapshot = collectPageSnapshot();
    const response = await chrome.runtime.sendMessage<AnalysisRequest>({
      type: 'analyze-page',
      payload: snapshot,
    });

    const result = (response as { payload?: AnalysisRequest['payload'] } | undefined) ?? {};
    console.info('AI SEO Analyzer result', result);
  });

  document.body.appendChild(button);
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if ((message as RequestPageSnapshot).type === 'request-page-snapshot') {
    sendResponse({ type: 'page-snapshot', payload: collectPageSnapshot() });
  }
  return true;
});

document.addEventListener('DOMContentLoaded', attachAnalysisButton);
