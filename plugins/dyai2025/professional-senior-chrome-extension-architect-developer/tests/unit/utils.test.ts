import { describe, expect, it } from 'vitest';
import type { PageSnapshot } from '../../src/shared/contracts.js';
import { scoreSnapshot } from '../../src/shared/utils.js';

describe('scoreSnapshot', () => {
  const baseSnapshot: PageSnapshot = {
    url: 'https://example.com',
    title: 'Example',
    description: 'A demo page',
    headings: ['H1'],
    wordCount: 800,
    images: [{ alt: 'hero', src: '/hero.png' }],
    links: [{ href: 'https://example.com/about', text: 'About' }],
  };

  it('returns a higher score when description and headings are present', () => {
    const { score } = scoreSnapshot(baseSnapshot);
    expect(score).toBeGreaterThan(40);
  });

  it('flags missing description and headings', () => {
    const snapshot: PageSnapshot = { ...baseSnapshot, description: '', headings: [] };
    const result = scoreSnapshot(snapshot);
    expect(result.issues).toContain('Meta description is missing.');
    expect(result.issues).toContain('No headings detected (h1-h3).');
  });
});
