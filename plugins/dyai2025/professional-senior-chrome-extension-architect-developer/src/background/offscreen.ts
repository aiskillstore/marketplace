import type { OffscreenParseRequest, OffscreenParseResponse } from '../shared/contracts.js';

function parseHtml(html: string): OffscreenParseResponse['payload'] {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  const images = Array.from(doc.querySelectorAll('img')).length;
  const links = Array.from(doc.querySelectorAll('a')).length;
  return { images, links };
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if ((message as OffscreenParseRequest).type === 'offscreen-parse') {
    const { html } = (message as OffscreenParseRequest).payload;
    const payload = parseHtml(html);
    sendResponse({ type: 'offscreen-parse-result', payload } satisfies OffscreenParseResponse);
  }
  return true;
});
