import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {admitMonitor} from './source-monitor-admission.mjs';
export async function selectOldestSources(fetcher=fetch,env=process.env){
  const url=new URL('/rest/v1/skills',env.PUBLIC_SUPABASE_URL);
  url.search=new URLSearchParams({select:'slug',status:'eq.approved',order:'upstream_checked_at.asc.nullsfirst,slug.asc',limit:'100'});
  const response=await fetcher(url,{headers:{apikey:env.SUPABASE_SERVICE_ROLE_KEY,Authorization:`Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,'Accept-Profile':'skillstore'},signal:AbortSignal.timeout(30000)});
  if(!response.ok)throw Error(`Source selection failed: HTTP ${response.status}`);
  const rows=await response.json();
  if(!Array.isArray(rows)||rows.length>100||rows.some(r=>!/^[-a-z0-9]+$/.test(r.slug))||new Set(rows.map(r=>r.slug)).size!==rows.length)throw Error('Invalid bounded source selection');
  return rows.map(r=>r.slug);
}
if(import.meta.url===pathToFileURL(process.argv[1]??'').href){
  const reason=admitMonitor();
  if(reason)console.log(reason);
  else {const slugs=await selectOldestSources();if(slugs.length)execFileSync('./skillstore-cli',['skill','monitor-upstream','--slugs',slugs.join(','),'--write','--concurrency','8','--writeConcurrency','2'],{stdio:'inherit'});else console.log('No approved sources');}
}
