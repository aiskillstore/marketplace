import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, mkdtempSync, writeFileSync, chmodSync, rmSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
const workflow = readFileSync(new URL('../../.github/workflows/publication-provenance.yml', import.meta.url), 'utf8');
const block = workflow.split('        run: |\n')[1].split('\n      #')[0].split('\n').map(l => l.startsWith('          ') ? l.slice(10) : l).join('\n');
const head='a'.repeat(40);
const removed={filename:'pending/publisher/skill/SKILL.md',status:'removed'};
function run({files=[removed],permission='write',fork=false,stale=false,count=files.length,permissionFailure=false,pages,author='123',login='maintainer',branch='cleanup/example'}={}) {
 const dir=mkdtempSync(join(tmpdir(),'pending-admission-'));
 try {
  writeFileSync(join(dir,'files.json'),JSON.stringify(pages ?? [files]));
  writeFileSync(join(dir,'pr.json'),JSON.stringify({head:{sha:stale?'b'.repeat(40):head},changed_files:count}));
  writeFileSync(join(dir,'permission.json'),JSON.stringify({permission}));
  writeFileSync(join(dir,'gh'),`#!/bin/bash\ncase "$*" in\n *'/files?'*) cat "$FIXTURE/files.json";;\n *'/permission'*) ${permissionFailure?'exit 1':'cat "$FIXTURE/permission.json"'};;\n *'/pulls/42'*) cat "$FIXTURE/pr.json";;\n *) exit 90;;\nesac\n`);chmodSync(join(dir,'gh'),0o755);
  const r=spawnSync('bash',['-c',block],{encoding:'utf8',env:{...process.env,PATH:dir+':'+process.env.PATH,FIXTURE:dir,RUNNER_TEMP:dir,GITHUB_RUN_ID:'1',REPOSITORY:'o/r',PR_NUMBER:'42',AUTHOR_ID:author,AUTHOR_LOGIN:login,HEAD_REPOSITORY:fork?'other/fork':'o/r',HEAD_REF:branch,HEAD_SHA:head}});
  return {status:r.status,output:r.stdout+r.stderr};
 } finally {rmSync(dir,{recursive:true,force:true});}
}
for(const permission of ['admin','maintain','write']) test(`allows same-repo delete-only by ${permission}`,()=>{const r=run({permission});assert.equal(r.status,0,r.output);});
for(const [name,opts] of [
 ['outsider',{permission:'read'}],['triage',{permission:'triage'}],['unknown permission',{permission:null}],['permission lookup failure',{permissionFailure:true}],['fork',{fork:true}],['stale head',{stale:true}],['incomplete listing',{count:2}],
 ['addition',{files:[{...removed,status:'added'}]}],['modification',{files:[{...removed,status:'modified'}]}],['rename',{files:[{...removed,status:'renamed',previous_filename:'skills/a/b/SKILL.md'}]}],['rename metadata',{files:[{...removed,previous_filename:'skills/a/b/SKILL.md'}]}],['mixed workflow deletion',{files:[removed,{filename:'.github/workflows/ci.yml',status:'removed'}]}],['canonical deletion',{files:[removed,{filename:'skills/a/b/SKILL.md',status:'removed'}]}],
 ...['pending/a','pending/a/b','pending/a/b/../secret','pending/a/b/./x','pending/a/b//x','pending/a/b/x\ny','pending/a/b/x\\y'].map(filename=>[filename,{files:[{filename,status:'removed'}]}])
]) test(`rejects maintainer cleanup ${name}`,()=>assert.notEqual(run(opts).status,0));
test('aggregates multiple file pages',()=>{
 const second={...removed,filename:'pending/publisher/skill/skill-report.json'};
 assert.equal(run({pages:[[removed],[second]],count:2}).status,0);
 assert.notEqual(run({pages:[[removed],[{...second,status:'added'}]],count:2}).status,0);
});
test('normal trusted submission remains admitted',()=>assert.equal(run({author:'254047988',login:'ai-skill-store[bot]',branch:'submission/example',files:[{...removed,status:'added'}]}).status,0));
test('normal platform change remains admitted',()=>assert.equal(run({files:[{filename:'scripts/tool.mjs',status:'modified'}]}).status,0));
test('required checks remain read-only without target-trigger or bypass',()=>{
 assert.match(workflow,/publication-admission:/);assert.doesNotMatch(workflow,/pull_request_target|contents: write|pull-requests: write/);
});
