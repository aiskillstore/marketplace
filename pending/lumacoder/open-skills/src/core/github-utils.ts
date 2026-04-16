export interface GitHubRef {
  owner: string;
  repo: string;
  ref?: string;
  path?: string;
}

export function parseGitHubUrl(input: string): GitHubRef | null {
  // Full URL formats
  const treeMatch = input.match(/^https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/tree\/([^\/]+)\/(.+)$/);
  if (treeMatch) {
    return { owner: treeMatch[1], repo: treeMatch[2], ref: treeMatch[3], path: treeMatch[4] };
  }

  const blobMatch = input.match(/^https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/blob\/([^\/]+)\/(.+)$/);
  if (blobMatch) {
    return { owner: blobMatch[1], repo: blobMatch[2], ref: blobMatch[3], path: blobMatch[4] };
  }

  const repoUrlMatch = input.match(/^https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/?$/);
  if (repoUrlMatch) {
    return { owner: repoUrlMatch[1], repo: repoUrlMatch[2] };
  }

  // Short format: owner/repo/path or owner/repo
  const shortMatch = input.match(/^([^\/]+)\/([^\/]+)(?:\/(.+))?$/);
  if (shortMatch) {
    return { owner: shortMatch[1], repo: shortMatch[2], path: shortMatch[3] };
  }

  return null;
}

export async function fetchGitHubRepo(owner: string, repo: string) {
  const res = await fetch(`https://api.github.com/repos/${owner}/${repo}`, {
    headers: { 'User-Agent': 'open-skills' },
  });
  if (!res.ok) {
    throw new Error(`GitHub API error: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as {
    name: string;
    full_name: string;
    description: string | null;
    owner: { login: string };
    license: { spdx_id: string } | null;
    default_branch: string;
  };
}

export async function fetchGitHubLatestTag(owner: string, repo: string): Promise<string | undefined> {
  try {
    const res = await fetch(`https://api.github.com/repos/${owner}/${repo}/tags?per_page=1`, {
      headers: { 'User-Agent': 'open-skills' },
    });
    if (res.ok) {
      const tags = (await res.json()) as { name: string }[];
      return tags[0]?.name;
    }
  } catch {
    // ignore
  }
  return undefined;
}

export interface GitHubContentItem {
  name: string;
  path: string;
  type: 'file' | 'dir';
  html_url: string;
  download_url?: string | null;
}

export async function fetchGitHubContents(
  owner: string,
  repo: string,
  path: string,
  ref?: string
): Promise<GitHubContentItem[]> {
  const url = new URL(`https://api.github.com/repos/${owner}/${repo}/contents/${path}`);
  if (ref) url.searchParams.set('ref', ref);
  const res = await fetch(url.toString(), {
    headers: { 'User-Agent': 'open-skills' },
  });
  if (!res.ok) {
    throw new Error(`GitHub API error: ${res.status} ${res.statusText}`);
  }
  const data = await res.json();
  return Array.isArray(data) ? data : [data];
}

export interface GitHubSearchRepoItem {
  full_name: string;
  description: string | null;
  owner: { login: string };
  html_url: string;
}

export interface GitHubSearchResult {
  items: GitHubSearchRepoItem[];
  total_count: number;
}

export async function searchGitHubRepos(query: string, perPage = 10): Promise<GitHubSearchResult> {
  const q = encodeURIComponent(`${query} in:name,description`);
  const res = await fetch(`https://api.github.com/search/repositories?q=${q}&per_page=${perPage}`, {
    headers: { 'User-Agent': 'open-skills' },
  });
  if (!res.ok) {
    throw new Error(`GitHub API error: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as GitHubSearchResult;
}
