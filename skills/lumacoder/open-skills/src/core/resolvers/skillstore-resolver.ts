import type { RemoteResolver } from './remote-resolver.js';
import type { SkillMetaV3 } from '../../types/index.js';
import { parseGitHubUrl, fetchGitHubRepo, fetchGitHubLatestTag } from '../github-utils.js';

function parseSkillStoreHtml(html: string, url: string): Partial<SkillMetaV3> & { repo?: string } {
  // Try JSON-LD first
  const ldMatch = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/i);
  if (ldMatch) {
    try {
      const ld = JSON.parse(ldMatch[1]) as Record<string, any>;
      if (ld['@type'] === 'SoftwareApplication') {
        const result: Partial<SkillMetaV3> & { repo?: string } = {
          name: ld.name || '',
          displayName: ld.name || '',
          description: ld.description || '',
          author: ld.author?.name || '',
          version: ld.softwareVersion || '',
        };
        // license may be a URL
        if (ld.license) {
          const licenseText = typeof ld.license === 'string' ? ld.license : '';
          result.license = licenseText.includes('opensource.org/licenses/MIT') ? 'MIT' : licenseText;
        }
        return result;
      }
    } catch {
      // ignore
    }
  }

  // Fallback to meta tags
  const ogTitle = html.match(/<meta property="og:title" content="(.*?)"\/>/i)?.[1] || '';
  const ogDesc = html.match(/<meta property="og:description" content="(.*?)"\/>/i)?.[1] || '';
  const description = html.match(/<meta name="description" content="(.*?)"\/>/i)?.[1] || '';
  const title = html.match(/<title>(.*?)<\/title>/i)?.[1] || '';

  return {
    name: '',
    displayName: ogTitle.split(' - ')[0] || title.split(' - ')[0] || '',
    description: ogDesc || description || '',
  };
}

function extractRepoFromSkillStoreHtml(html: string): string | undefined {
  // Look for repo in embedded JS data (SvelteKit inline data)
  const quotedKeyMatch = html.match(/"repo":"(https:\/\/github\.com\/[^"]+)"/);
  if (quotedKeyMatch) return quotedKeyMatch[1];

  const jsLiteralMatch = html.match(/repo:"(https:\/\/github\.com\/[^"]+)"/);
  if (jsLiteralMatch) return jsLiteralMatch[1];

  // Fallback: find anchor in developer details section (avoid nav/footer links)
  const devSectionMatch = html.match(/<a href="(https:\/\/github\.com\/[^"]+)"[^>]*class="font-mono[^"]*"[^>]*>/);
  if (devSectionMatch) return devSectionMatch[1];

  return undefined;
}

export class SkillStoreResolver implements RemoteResolver {
  provider = 'skillstore';

  private normalizeToSkillStoreUrl(ref: string): string | null {
    // Full skillstore URL
    if (ref.includes('skillstore.io')) {
      return ref;
    }
    // Short format: author/skill-name or author-skill-name (slug)
    // Try construct skillstore URL
    const slug = ref.replace(/\//g, '-');
    if (/^[a-zA-Z0-9-]+$/.test(slug)) {
      return `https://skillstore.io/skills/${slug}`;
    }
    return null;
  }

  async resolve(ref: string): Promise<Partial<SkillMetaV3>> {
    const skillStoreUrl = this.normalizeToSkillStoreUrl(ref);

    if (skillStoreUrl) {
      const res = await fetch(skillStoreUrl, { headers: { 'User-Agent': 'open-skills' } });
      if (!res.ok) {
        throw new Error(`SkillStore fetch failed: ${res.status} ${res.statusText}`);
      }
      const html = await res.text();
      const result = parseSkillStoreHtml(html, skillStoreUrl) as Partial<SkillMetaV3> & { repo?: string };

      const repoUrl = result.repo || extractRepoFromSkillStoreHtml(html);
      if (repoUrl) {
        // Include the repo URL as origin hint for caller regardless of GitHub API success
        (result as any).repoUrl = repoUrl;

        const gh = parseGitHubUrl(repoUrl);
        if (gh) {
          try {
            const repo = await fetchGitHubRepo(gh.owner, gh.repo);
            result.author = result.author || repo.owner.login;
            result.license = result.license || (repo.license?.spdx_id || '');
            if (!result.version) {
              result.version = (await fetchGitHubLatestTag(gh.owner, gh.repo)) || repo.default_branch || 'main';
            }
          } catch {
            // ignore GitHub errors, keep what we got from skillstore
          }
        }
      }

      if (!result.name && result.displayName) {
        result.name = result.displayName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
      }
      return result;
    }

    // Only fallback to GitHub when the ref is an explicit GitHub URL
    if (ref.startsWith('https://github.com/')) {
      const parsed = parseGitHubUrl(ref);
      if (parsed) {
        try {
          const repo = await fetchGitHubRepo(parsed.owner, parsed.repo);
          const version = (await fetchGitHubLatestTag(parsed.owner, parsed.repo)) || repo.default_branch || 'main';
          return {
            name: parsed.repo,
            displayName: repo.name,
            description: repo.description || '',
            author: repo.owner.login,
            license: repo.license?.spdx_id || '',
            version,
          };
        } catch (err: any) {
          throw new Error(`GitHub fallback failed for skillstore: ${err.message}`);
        }
      }
    }

    throw new Error(`Cannot resolve skillstore ref: "${ref}". Expected a skillstore.io URL, slug (e.g., author-skill-name), or GitHub URL.`);
  }
}
