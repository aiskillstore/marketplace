import {execFileSync} from 'node:child_process';
import {appendFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
const repo='repos/aiskillstore/marketplace';
const api=path=>JSON.parse(execFileSync('gh',['api',`${repo}/${path}`],{encoding:'utf8'}));
export function admitMonitor(request=api) {
  const root=request('git/trees/main');
  const pending=root.tree.find(x=>x.path==='pending');
  if(pending){const tree=request(`git/trees/${pending.sha}?recursive=1`);if(tree.truncated)throw Error('Truncated Pending inventory');if(tree.tree.some(x=>x.type==='blob'))return 'Pending publications have priority';}
  for(const workflow of ['sync-to-supabase.yml','on-pr-merge.yml','publish-approved-batch.yml']){
    const runs=request(`actions/workflows/${workflow}/runs?per_page=100`).workflow_runs;
    if(runs.some(r=>r.status!=='completed'))return `Waiting for ${workflow}`;
    if(workflow==='sync-to-supabase.yml'){
      const last=runs.filter(r=>r.event==='push').sort((a,b)=>b.created_at.localeCompare(a.created_at))[0];
      if(last && last.conclusion!=='success')return 'Previous publication sync needs recovery';
    }
  }
  return '';
}
if(import.meta.url===pathToFileURL(process.argv[1]??'').href){const reason=admitMonitor();console.log(reason||'Publication queue clear');if(process.env.GITHUB_OUTPUT)appendFileSync(process.env.GITHUB_OUTPUT,`allowed=${!reason}\n`);}
