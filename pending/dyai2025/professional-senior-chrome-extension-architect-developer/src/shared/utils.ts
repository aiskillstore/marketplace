import type {
  AnalysisResponse,
  OffscreenParseRequest,
  OffscreenParseResponse,
  PageSnapshot,
} from './contracts.js';

export function scoreSnapshot(snapshot: PageSnapshot): AnalysisResponse['payload'] {
  const issues: string[] = [];
  const recommendations: string[] = [];

  if (!snapshot.description) {
    issues.push('Meta description is missing.');
    recommendations.push('Add a concise meta description (120-160 characters).');
  }

  const headingScore = Math.min(snapshot.headings.length, 6) * 3;
  if (snapshot.headings.length === 0) {
    issues.push('No headings detected (h1-h3).');
    recommendations.push('Introduce an H1 and supporting sub-headings for clarity.');
  }

  const imagesMissingAlt = snapshot.images.filter((img) => !img.alt).length;
  if (imagesMissingAlt > 0) {
    issues.push(`${imagesMissingAlt} images missing alt text.`);
    recommendations.push('Provide descriptive alt text for all images.');
  }

  const linkCount = snapshot.links.length;
  if (linkCount < 5) {
    recommendations.push('Consider adding internal links to relevant pages.');
  }

  const wordScore = Math.min(snapshot.wordCount / 500, 1) * 25;
  const linkScore = Math.min(linkCount / 20, 1) * 15;
  const imageScore = Math.min(snapshot.images.length / 10, 1) * 10;
  const baseScore = 20; // baseline for page presence
  const descriptionScore = snapshot.description ? 10 : 0;

  const score = Math.round(
    baseScore + descriptionScore + headingScore + wordScore + linkScore + imageScore,
  );

  const aiSummary = buildLocalSummary(snapshot, issues, recommendations, score);

  return {
    score: Math.min(score, 100),
    issues,
    recommendations,
    aiSummary,
  };
}

export function buildLocalSummary(
  snapshot: PageSnapshot,
  issues: string[],
  recommendations: string[],
  score: number,
): string {
  const parts = [
    `URL: ${snapshot.url}`,
    `Title: ${snapshot.title || '—'}`,
    `Score: ${score}/100`,
  ];

  if (issues.length) {
    parts.push(`Issues: ${issues.join('; ')}`);
  }

  if (recommendations.length) {
    parts.push(`Next steps: ${recommendations.slice(0, 3).join('; ')}`);
  }

  return parts.join(' \n ');
}

export async function ensureOffscreenDocument(path: string): Promise<void> {
  const existing = await chrome.offscreen.hasDocument?.();
  if (!existing) {
    await chrome.offscreen.createDocument({
      url: path,
      reasons: [chrome.offscreen.Reason.DOM_SCRAPING],
      justification: 'Parse HTML content for SEO metrics',
    });
  }
}

export async function requestOffscreenParse(html: string): Promise<OffscreenParseResponse['payload']> {
  await ensureOffscreenDocument(chrome.runtime.getURL('dist/background/offscreen.html'));
  const response = await chrome.runtime.sendMessage<OffscreenParseRequest, OffscreenParseResponse>({
    type: 'offscreen-parse',
    payload: { html },
  });
  return response.payload;
}

export async function fetchWithOpenAI(
  apiKey: string,
  snapshot: PageSnapshot,
): Promise<string> {
  const body = {
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'system',
        content: 'Provide a concise SEO review of the page. Keep it under 120 words.',
      },
      {
        role: 'user',
        content: `URL: ${snapshot.url}\nTitle: ${snapshot.title}\nDescription: ${snapshot.description}\nHeadings: ${snapshot.headings.join(' | ')}\nWords: ${snapshot.wordCount}`,
      },
    ],
    temperature: 0.5,
    max_tokens: 180,
  };

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`OpenAI request failed: ${response.status} ${detail}`);
  }

  const data = await response.json();
  const aiContent = data.choices?.[0]?.message?.content;
  return aiContent || 'AI response unavailable.';
}
