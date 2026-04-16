export async function resolveGitHub(ref: string): Promise<{
  name?: string;
  displayName?: string;
  description?: string;
  author?: string;
  license?: string;
  version?: string;
}> {
  const [owner, repo] = ref.split('/');
  if (!owner || !repo) {
    throw new Error('Invalid GitHub ref, expected format: owner/repo');
  }

  const res = await fetch(`https://api.github.com/repos/${owner}/${repo}`, {
    headers: { 'User-Agent': 'open-skills' },
  });

  if (!res.ok) {
    throw new Error(`GitHub API error: ${res.status} ${res.statusText}`);
  }

  const data = (await res.json()) as {
    name: string;
    full_name: string;
    description: string | null;
    owner: { login: string };
    license: { spdx_id: string } | null;
  };

  // Try to get latest tag as version
  let version = '';
  try {
    const tagsRes = await fetch(`https://api.github.com/repos/${owner}/${repo}/tags?per_page=1`, {
      headers: { 'User-Agent': 'open-skills' },
    });
    if (tagsRes.ok) {
      const tags = (await tagsRes.json()) as { name: string }[];
      if (tags.length > 0) version = tags[0].name;
    }
  } catch {
    // ignore
  }

  return {
    name: repo,
    displayName: data.name,
    description: data.description || '',
    author: data.owner.login,
    license: data.license?.spdx_id || '',
    version: version || 'main',
  };
}
