import { loadRegistry } from '../core/registry.js';
import {
  parseGitHubUrl,
  fetchGitHubRepo,
  fetchGitHubLatestTag,
  fetchGitHubContents,
  searchGitHubRepos,
  type GitHubContentItem,
} from '../core/github-utils.js';

interface SearchOptions {
  remote: boolean;
  nameOnly: boolean;
}

function parseSearchArgs(args: string[]): { query: string; options: SearchOptions } {
  const options: SearchOptions = { remote: false, nameOnly: false };
  const filtered: string[] = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--remote' || args[i] === '-r') {
      options.remote = true;
    } else if (args[i] === '--name' || args[i] === '-n') {
      options.nameOnly = true;
    } else {
      filtered.push(args[i]);
    }
  }

  return { query: filtered.join(' ').trim(), options };
}

async function searchLocal(query: string, options: SearchOptions) {
  const q = query.toLowerCase();
  const registry = await loadRegistry();
  const results: { group: string; skillName: string; displayName: string; description: string }[] = [];

  for (const group of registry) {
    for (const skill of group.skills) {
      let match = false;
      if (options.nameOnly) {
        match = skill.name.toLowerCase().includes(q) || skill.display_name.toLowerCase().includes(q);
      } else {
        const haystack = `${skill.name} ${skill.display_name} ${skill.description} ${skill.tags.join(' ')}`.toLowerCase();
        match = haystack.includes(q);
      }
      if (match) {
        results.push({
          group: group.displayName,
          skillName: skill.name,
          displayName: skill.display_name,
          description: skill.description,
        });
      }
    }
  }
  return results;
}

async function resolveGitHubSkill(ref: string) {
  const parsed = parseGitHubUrl(ref);
  if (!parsed) return null;

  const repo = await fetchGitHubRepo(parsed.owner, parsed.repo);
  const version = (await fetchGitHubLatestTag(parsed.owner, parsed.repo)) || repo.default_branch || 'main';

  return {
    name: parsed.repo,
    displayName: repo.name,
    description: repo.description || '',
    author: repo.owner.login,
    license: repo.license?.spdx_id || '',
    version,
    ref: `${parsed.owner}/${parsed.repo}`,
    path: parsed.path,
    branch: parsed.ref || repo.default_branch || 'main',
  };
}

async function scanGitHubDirectory(
  owner: string,
  repo: string,
  dirPath: string,
  ref: string
): Promise<{ name: string; path: string; type: 'file' | 'dir'; hasSkillMd: boolean }[]> {
  try {
    const items = await fetchGitHubContents(owner, repo, dirPath, ref);
    const results: { name: string; path: string; type: 'file' | 'dir'; hasSkillMd: boolean }[] = [];

    for (const item of items) {
      if (item.type === 'file' && item.name.toLowerCase() === 'skill.md') {
        results.push({ name: dirPath.split('/').pop() || dirPath, path: dirPath, type: 'dir', hasSkillMd: true });
        return results;
      }
    }

    for (const item of items) {
      if (item.type === 'dir') {
        // Heuristic: check if subdirectory contains SKILL.md
        try {
          const children = await fetchGitHubContents(owner, repo, item.path, ref);
          const hasSkillMd = children.some((c: GitHubContentItem) => c.type === 'file' && c.name.toLowerCase() === 'skill.md');
          results.push({ name: item.name, path: item.path, type: 'dir', hasSkillMd });
        } catch {
          results.push({ name: item.name, path: item.path, type: 'dir', hasSkillMd: false });
        }
      }
    }
    return results;
  } catch {
    return [];
  }
}

async function searchRemote(query: string) {
  const parsed = parseGitHubUrl(query);

  // If input looks like a GitHub ref or URL, try to resolve it directly
  if (parsed) {
    const skill = await resolveGitHubSkill(query);
    if (!skill) return { direct: null, repos: [] };

    // If a sub-path is provided, scan that directory for skills
    if (skill.path) {
      const entries = await scanGitHubDirectory(parsed.owner, parsed.repo, skill.path, skill.branch);
      return {
        direct: skill,
        entries,
        repos: [],
      };
    }

    return { direct: skill, entries: [], repos: [] };
  }

  // Otherwise, use GitHub repository search
  const search = await searchGitHubRepos(query, 10);
  return {
    direct: null,
    entries: [],
    repos: search.items.map((item) => ({
      ref: item.full_name,
      description: item.description || '',
      author: item.owner.login,
      url: item.html_url,
    })),
  };
}

export async function searchCommand(args: string[]) {
  const { query, options } = parseSearchArgs(args);

  if (!query) {
    console.log('请输入搜索关键词：open-skills search <keyword>');
    console.log('选项：');
    console.log('  --remote, -r    启用远程 GitHub 搜索');
    console.log('  --name, -n      仅按 skill 名称匹配');
    process.exit(1);
  }

  // Local search
  const localResults = await searchLocal(query, options);

  if (localResults.length > 0) {
    console.log(`本地找到 ${localResults.length} 个匹配结果：\n`);
    for (const r of localResults) {
      console.log(`[${r.group}] ${r.displayName} (${r.skillName})`);
      console.log(`  ${r.description}\n`);
    }
  } else {
    console.log('本地未找到匹配的 skills');
  }

  // Remote search
  if (options.remote) {
    console.log('\n--- 远程搜索 (GitHub) ---\n');
    try {
      const remote = await searchRemote(query) as {
        direct: any;
        entries: any[];
        repos: any[];
      };

      if (remote.direct) {
        const d = remote.direct;
        console.log(`直接解析: ${d.ref}`);
        console.log(`  名称: ${d.displayName}`);
        console.log(`  描述: ${d.description || '(无)'}`);
        console.log(`  作者: ${d.author}`);
        console.log(`  版本: ${d.version}`);
        if (d.path) {
          console.log(`  子路径: ${d.path}`);
          if (remote.entries.length > 0) {
            console.log(`  该路径下发现 ${remote.entries.length} 个条目：`);
            for (const e of remote.entries) {
              const indicator = e.hasSkillMd ? '✓ SKILL.md' : '○ 无 SKILL.md';
              console.log(`    - ${e.name} (${e.path}) [${indicator}]`);
            }
          } else {
            console.log('  该路径下未扫描到条目');
          }
        }
        console.log();
      }

      if (remote.repos.length > 0) {
        console.log(`搜索到 ${remote.repos.length} 个远程仓库：\n`);
        for (const r of remote.repos) {
          console.log(`[GitHub] ${r.ref}`);
          console.log(`  作者: ${r.author}`);
          console.log(`  描述: ${r.description || '(无)'}`);
          console.log(`  地址: ${r.url}\n`);
        }
      }

      if (!remote.direct && remote.repos.length === 0) {
        console.log('远程未找到匹配的 skills\n');
      }
    } catch (err: any) {
      console.log(`远程搜索失败: ${err.message || String(err)}\n`);
    }
  }
}
