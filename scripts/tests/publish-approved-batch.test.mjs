import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createHash } from 'node:crypto';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync, existsSync } from 'node:fs';
import { execFileSync, spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { once } from 'node:events';
import { parse } from 'yaml';
import { batchIdentity, validateBatchPlans } from '../publish-approved-batch.mjs';
import { publicationIdentity } from '../continue-merged-publications.mjs';
import { calculateCanonicalTreeHash } from '../resolve-approved-submission.mjs';

const script = resolve('scripts/publish-approved-batch.mjs');
const correlation = n => `submission-pr-${n}-${'a'.repeat(40)}-${'b'.repeat(40)}`;
test('batch identity and distinct Skill limits fail closed', () => {
  assert.equal(batchIdentity([correlation(1), correlation(2)]), batchIdentity([correlation(2), correlation(1)]));
  assert.throws(() => batchIdentity([correlation(1), correlation(1)]));
  assert.throws(() => batchIdentity(Array.from({length:26}, (_, i) => correlation(i + 1))));
  assert.throws(() => validateBatchPlans([{plan:{skills:[{targetDir:'skills/a'}, {targetDir:'skills/a/b'}]}}]));
  assert.throws(() => validateBatchPlans([{plan:{skills:[{targetDir:'skills/a',duplicate:true}]}}]));
});

test('two frozen approvals publish together once, retaining exact commits, callbacks, and reservations', async () => {
  const temp = mkdtempSync(join(tmpdir(), 'publish-batch-'));
  const root = join(temp, 'work'), remote = join(temp, 'remote.git'), bin = join(temp, 'bin');
  mkdirSync(root); mkdirSync(bin);
  const git = args => execFileSync('git', args, { cwd: root, encoding:'utf8', stdio:['pipe','pipe','pipe'] }).trim();
  const callbacks=[];
  const server = createServer((req,res) => { let body=''; req.on('data', x=>body+=x); req.on('end',()=> { callbacks.push({headers:req.headers,body:JSON.parse(body)});res.writeHead(200);res.end('{}'); }); });
  server.listen(0,'127.0.0.1'); await once(server,'listening');
  try {
    git(['init','-b','main']);git(['config','user.name','Test']);git(['config','user.email','test@example.com']);
    writeFileSync(join(root,'README.md'),'fixture');git(['add','.']);git(['commit','-m','base']);
    const prs=[],files={};
    for (const number of [1,2]) {
      const base=git(['rev-parse','HEAD']), pending=`pending/owner/skill${number}`;
      git(['checkout','-b',`submission/${number}`]);mkdirSync(join(root,pending),{recursive:true});
      const content=`# Skill ${number}\n`;writeFileSync(join(root,pending,'SKILL.md'),content);
      writeFileSync(join(root,pending,'skill-report.json'),JSON.stringify({meta:{slug:`owner-skill${number}`,source_type:'community',source_ref:'a'.repeat(40),source_url:`https://github.com/owner/source/tree/${'a'.repeat(40)}/skill${number}`,content_hash:createHash('sha256').update(content).digest('hex'),tree_hash:calculateCanonicalTreeHash(root,pending)},security_audit:{safe_to_publish:false}}));
      git(['add','.']);git(['commit','-m','audited skill']);const head=git(['rev-parse','HEAD']);
      git(['checkout','main']);git(['merge','--no-ff','-m','merge approval',`submission/${number}`]);const merge=git(['rev-parse','HEAD']);
      prs.push({number,merged_at:'2026-09-08T00:00:00Z',base:{ref:'main',sha:base},user:{id:254047988,login:'ai-skill-store[bot]'},head:{ref:`submission/${number}`,sha:head,repo:{full_name:'aiskillstore/marketplace'}},merge_commit_sha:merge,html_url:`https://github.com/aiskillstore/marketplace/pull/${number}`,merged_by:{login:'test'},body:`Submission ID: \`${number.toString().padStart(8,'0')}-0000-0000-0000-000000000000\``});
      files[number]=git(['diff','--name-only',base,merge]).split('\n').map(filename=>({filename}));
    }
    const before=git(['rev-parse','HEAD']);git(['clone','--bare',root,remote]);git(['remote','add','origin',remote]);
    const state=join(temp,'state.json');writeFileSync(state,JSON.stringify({prs,files,refs:{},statuses:{},writes:[]}));
    writeFileSync(join(bin,'gh'),`#!${process.execPath}\n`+`
const fs=require('node:fs');const args=process.argv.slice(2);const endpoint=args.find(a=>a.startsWith('repos/')).replace('repos/aiskillstore/marketplace/','');
const state=JSON.parse(fs.readFileSync(process.env.TEST_STATE));const post=args.includes('--method');let out;
if(post){const body=JSON.parse(fs.readFileSync(0,'utf8'));state.writes.push({endpoint,body});
 if(endpoint==='git/refs'){state.refs[body.ref]={ref:body.ref,object:{type:'commit',sha:body.sha}};out=state.refs[body.ref];}
 else if(endpoint.startsWith('statuses/')){(state.statuses[endpoint.slice(9)]??=[]).unshift(body);out=body;}else throw new Error(endpoint);
}else if(endpoint.startsWith('pulls/')){const n=Number(endpoint.split('/')[1]);out=endpoint.includes('/files')?state.files[n]:state.prs.find(p=>p.number===n);}
else if(endpoint.startsWith('actions/workflows/'))out={workflow_runs:[{event:'push',status:'completed',conclusion:'success',created_at:'2026-09-08T00:00:00Z'}]};
else if(endpoint.startsWith('git/matching-refs/'))out=Object.values(state.refs).filter(r=>r.ref.startsWith('refs/'+endpoint.slice('git/matching-refs/'.length)));
else if(endpoint.startsWith('git/ref/'))out=state.refs['refs/'+endpoint.slice(8)];
else if(endpoint.startsWith('commits/'))out=state.statuses[endpoint.split('/')[1]]??[];
else throw new Error(endpoint);
fs.writeFileSync(process.env.TEST_STATE,JSON.stringify(state));process.stdout.write(JSON.stringify(args.includes('--slurp')?[out]:out));
`,{mode:0o755});
    const run = () => new Promise(resolveRun => {
      const child=spawn(process.execPath,[script],{cwd:root,env:{...process.env,PATH:`${bin}:${process.env.PATH}`,TEST_STATE:state,PR_NUMBERS:'1,2',BATCH_ID:batchIdentity(prs.map(p=>publicationIdentity(p).correlation)),GITHUB_REF:'refs/heads/main',GITHUB_REPOSITORY:'aiskillstore/marketplace',GITHUB_RUN_ID:'123',SKILLSTORE_API_URL:`http://127.0.0.1:${server.address().port}`,SKILLSTORE_CALLBACK_TOKEN:'test-only'}});
      let output='';child.stdout.on('data',s=>output+=s);child.stderr.on('data',s=>output+=s);child.on('close',code=>resolveRun({code,output}));
    });
    const result=await run();assert.equal(result.code,0,result.output);
    assert.equal(git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0],git(['rev-parse','HEAD']));
    assert.equal(git(['rev-list','--count',`${before}..HEAD`]),'2');
    for(const n of [1,2]){assert.equal(existsSync(join(root,`pending/owner/skill${n}`)),false);assert.ok(existsSync(join(root,`skills/owner/skill${n}/skill-report.json`)));}
    assert.equal(callbacks.length,2);
    assert.deepEqual(callbacks.map(c=>c.body.pr_number),[1,2]);
    const evidence=JSON.parse(readFileSync(state));
    assert.equal(Object.keys(evidence.refs).length,2);
    assert.equal(evidence.writes.filter(w=>w.body.context?.startsWith('agentcrew/publication-attempt/')&&w.body.state==='success').length,2);
    assert.equal(evidence.writes.filter(w=>w.body.context?.startsWith('agentcrew/publication/')&&w.body.state==='success').length,0,'only provider may complete correlation');
    const prior=git(['rev-parse','HEAD']);const replay=await run();assert.notEqual(replay.code,0);assert.equal(git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0],prior,'replay cannot change main');
  } finally { server.close();rmSync(temp,{recursive:true,force:true}); }
});

test('batch and individual receivers share one writer lock and sync reads the exact push range', () => {
  const single=parse(readFileSync('.github/workflows/on-pr-merge.yml','utf8'));
  const batch=parse(readFileSync('.github/workflows/publish-approved-batch.yml','utf8'));
  assert.equal(batch.concurrency.group,single.concurrency.group);
  assert.equal(batch.jobs.publish.if,"github.ref == 'refs/heads/main'");
  const sync=readFileSync('.github/workflows/sync-to-supabase.yml','utf8');
  assert.match(sync,/git log --format=%B "\$PUSH_BEFORE\.\.\$PUSH_SHA"/);
  assert.match(sync,/Publication batch \$BATCH_DIGEST/);
  assert.match(sync,/\[ "\$\{#CORRELATIONS\[@\]\}" -le 25 \]/);
});

test('owner wait covers the batch callback wall-clock budget', () => {
  assert.match(readFileSync('.github/workflows/sync-to-supabase.yml', 'utf8'), /for attempt in \{1\.\.360\}/);
});

const bashMajor=Number(execFileSync('bash',['--version'],{encoding:'utf8'}).match(/version (\d+)/)?.[1]);
test('actual sync shell validates every batch owner and closes every provider correlation', {skip:bashMajor<4?'Workflow requires Linux Bash 4+; exercised in CI':false}, () => {
  const temp=mkdtempSync(join(tmpdir(),'batch-provider-'));
  const config=parse(readFileSync('.github/workflows/sync-to-supabase.yml','utf8'));
  const wait=config.jobs.sync.steps.find(s=>s.id==='publication-correlation').run;
  const finish=config.jobs.sync.steps.find(s=>s.name==='Record durable publication provider result').run;
  const ids=[correlation(1),correlation(2)], digest=batchIdentity(ids);
  const state=join(temp,'writes.jsonl'), output=join(temp,'output');writeFileSync(output,'');
  try {
    writeFileSync(join(temp,'git'), '#!/bin/sh\nif [ "$1" = log ]; then printf "%s\\n" "$TEST_MESSAGES"; fi\n',{mode:0o755});
    writeFileSync(join(temp,'gh'),`#!${process.execPath}\n`+`
const fs=require('node:fs');const args=process.argv.slice(2);const endpoint=args.find(a=>a.startsWith('repos/'));
if(args.includes('--method')){fs.appendFileSync(process.env.TEST_WRITES,JSON.stringify(args)+'\\n');process.stdout.write('{}');}
else if(endpoint.includes('/statuses')){
 process.stdout.write(JSON.stringify(JSON.parse(process.env.TEST_IDS).map(id=>({context:'agentcrew/publication/'+require('node:crypto').createHash('sha256').update(id).digest('hex'),state:'pending',target_url:'https://github.com/aiskillstore/marketplace/actions/runs/123'}))));
}else process.stdout.write(JSON.stringify({display_title:process.env.TEST_TITLE,path:'.github/workflows/publish-approved-batch.yml',head_branch:'main',head_repository:{full_name:'aiskillstore/marketplace'},status:'completed',conclusion:'success'}));
`,{mode:0o755});
    const env={...process.env,PATH:`${temp}:${process.env.PATH}`,TEST_WRITES:state,TEST_IDS:JSON.stringify(ids),TEST_MESSAGES:ids.map(id=>`AgentCrew-Publication: ${id}`).join('\n'),TEST_TITLE:`Publication batch ${digest}`,PUSH_BEFORE:'c'.repeat(40),PUSH_SHA:'d'.repeat(40),REPOSITORY:'aiskillstore/marketplace',GITHUB_OUTPUT:output};
    execFileSync('bash',['-c',wait],{env,encoding:'utf8'});
    const result=readFileSync(output,'utf8');assert.ok(result.includes(`correlations=${JSON.stringify(ids)}`));
    execFileSync('bash',['-c',finish],{env:{...env,CORRELATION_ID:ids[1],MERGE_COMMIT_SHA:'b'.repeat(40),CORRELATION_IDS:JSON.stringify(ids),JOB_STATUS:'success'},encoding:'utf8'});
    const writes=readFileSync(state,'utf8').trim().split('\n').map(JSON.parse);assert.equal(writes.length,2);assert.ok(writes.every(args=>args.includes('state=success')));
    assert.throws(()=>execFileSync('bash',['-c',wait],{env:{...env,TEST_TITLE:'Publication batch '+ '0'.repeat(64)},encoding:'utf8',stdio:'pipe'}));
  }finally{rmSync(temp,{recursive:true,force:true});}
});
