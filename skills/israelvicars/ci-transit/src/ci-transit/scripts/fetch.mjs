import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const argv = process.argv.slice(2);
let runId = argv[0] && !argv[0].startsWith('-') ? argv.shift() : null;
let repo, out = 'run.json', lastFailed = false, workflow, branch;
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--repo') repo = argv[++i];
  else if (argv[i] === '--out') out = argv[++i];
  else if (argv[i] === '--last-failed') lastFailed = true;
  else if (argv[i] === '--workflow') workflow = argv[++i];
  else if (argv[i] === '--branch') branch = argv[++i];
  else throw new Error(`unknown option: ${argv[i]}`);
}
if (!runId && !lastFailed) throw new Error('usage: node fetch.mjs <run-id> | --last-failed [--workflow name] [--branch b]  [--repo owner/name] [--out run.json]');
if (!runId) {
  // newest failed run (read-only `gh run list`)
  const list = ['run', 'list', '--status', 'failure', '--limit', '1', '--json', 'databaseId,workflowName,displayTitle,createdAt'];
  if (repo) list.push('--repo', repo);
  if (workflow) list.push('--workflow', workflow);
  if (branch) list.push('--branch', branch);
  let runs;
  try { runs = JSON.parse(execFileSync('gh', list, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] })); }
  catch (error) { throw new Error(error.code === 'ENOENT' ? 'GitHub Actions fetch requires the `gh` CLI, but it was not found on PATH.' : `gh run list failed. The command is read-only.\n${String(error.stderr || error.message).trim()}`); }
  if (!runs.length) throw new Error(`no failed runs found${repo ? ` in ${repo}` : ''}`);
  runId = String(runs[0].databaseId);
  console.log(`last failed run: ${runId} (${runs[0].workflowName}: ${runs[0].displayTitle}, ${runs[0].createdAt})`);
}
const fields = 'databaseId,name,displayTitle,headBranch,event,status,conclusion,createdAt,startedAt,updatedAt,url,workflowName,attempt,jobs';
const args = ['run', 'view', runId, '--json', fields];
if (repo) args.push('--repo', repo);
try {
  const text = execFileSync('gh', args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  const run = JSON.parse(text);
  writeFileSync(out, JSON.stringify(run, null, 2) + '\n');
  console.log(`wrote ${out} (${run.jobs?.length || 0} jobs)`);
} catch (error) {
  const detail = String(error.stderr || error.message || '').trim();
  if (error.code === 'ENOENT') throw new Error('GitHub Actions fetch requires the `gh` CLI, but it was not found on PATH. Install gh and retry.');
  if (/auth|login|token|not logged/i.test(detail)) throw new Error(`GitHub CLI is not authenticated. Run "gh auth login", then retry.\n${detail}`);
  throw new Error(`gh run view failed for run ${runId}${repo ? ` in ${repo}` : ''}. The command is read-only.\n${detail}`);
}
