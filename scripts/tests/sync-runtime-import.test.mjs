import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';

test('the actual sparse sync runtime imports recovery entrypoints without network or credentials',()=>{
  const workflow=readFileSync('.github/workflows/sync-to-supabase.yml','utf8');
  const match=workflow.match(/cat > "\$PATTERNS_FILE" <<'EOF'\n([\s\S]*?)\n\s+EOF/);
  assert.ok(match,'Missing authoritative sparse patterns');
  const patterns=match[1].split('\n').map(line=>line.trim().replace(/^\//,''));
  const temporary=mkdtempSync(join(process.cwd(),'.sync-runtime-import-'));
  try {
    for(const path of patterns.filter(p=>p.endsWith('.mjs'))){
      mkdirSync(dirname(join(temporary,path)),{recursive:true});
      writeFileSync(join(temporary,path),readFileSync(path));
    }
    execFileSync(process.execPath,['--input-type=module','-e',"await import('./scripts/prepare-sync-recovery.mjs'); await import('./scripts/bounded-submission-recovery.mjs');"],{cwd:temporary,encoding:'utf8',timeout:15000,env:{PATH:process.env.PATH,CI:'true'}});
    const normalization=workflow.slice(workflow.indexOf('- name: Normalize pinned sync runtime checkout'),workflow.indexOf('- name: Validate trusted sync correlation'));
    for(const name of ['publication-postpush-recovery.mjs','ancillary-sync-reconciliation.mjs'])assert.ok(normalization.includes(`scripts/${name} \\`),'Dependency must also receive immutable blob/regular-file verification');
  }finally{rmSync(temporary,{recursive:true,force:true});}
});
