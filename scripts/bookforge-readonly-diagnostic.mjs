#!/usr/bin/env node
// Offline incident evidence inspection. No provider connection or recovery action.
import {constants, openSync, closeSync, fstatSync, readSync} from 'node:fs';
import {pathToFileURL} from 'node:url';

export const EXPECTED = Object.freeze({
  slug: 'gongnyang-bookforge',
  root: 'skills/gongnyang/bookforge',
  publicationSha: '549325ce6f288514ab5da9bf11af95814f848048',
  contentHash: '3c08f6323db5e3e28178a1eeee72be94a49c644daf388161151adace067d56a8',
  treeHash: '3c23cc266d547439a3ca100cd9e4a90f4ab7b4ac00388d028ed526de685e8bad',
  sourceRef: '3f1e85ee501f5984acb8cd6d92ecb7a4c3fb5374',
});
const skillFields = ['id','slug','plugin_path','marketplace_commit_sha','content_hash','tree_hash','current_artifact_version_id','artifact_revision'];
const artifactFields = ['id','skill_id','source_path','marketplace_commit_sha','content_hash','tree_hash','artifact_revision','snapshot_status'];
const observationFields = ['skill_id','artifact_version_id','marketplace_commit_sha','source_path','upstream_commit_sha'];
const collections = ['skills','publicationArtifacts','currentArtifacts','observations'];
const UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
const SHA40 = /^[a-f0-9]{40}$/;
const SHA64 = /^[a-f0-9]{64}$/;
const MAX_BYTES = 65536;
function requireValue(ok) { if (!ok) throw new Error('Invalid diagnostic snapshot'); }
function objectKeys(value, keys) {
  requireValue(value !== null && typeof value === 'object' && !Array.isArray(value));
  requireValue(Object.keys(value).length === keys.length && keys.every(k => Object.hasOwn(value,k)));
}
function matches(pattern, value) { return typeof value === 'string' && pattern.test(value); }
function nullable(pattern, value) { return value === null || matches(pattern,value); }

export function readPlan() {
  const scope = {skill_id:'$uniqueSkill.id',source_path:EXPECTED.root};
  const publication = {...scope,marketplace_commit_sha:EXPECTED.publicationSha};
  const query = (name,table,select,filters) => ({name,method:'GET',schema:'skillstore',table,select:[...select],filters,limit:2});
  return {
    schemaVersion:1,slug:EXPECTED.slug,publicationSha:EXPECTED.publicationSha,
    authorizesExecution:false,
    prerequisite:'Runtime-approved read-only connector; no connector or credential is configured by this tool.',
    dependencies:'Run skills first. Require exactly one validated skill row. Bind subsequent skill_id and current pointer from that row only; null pointer means currentArtifacts=[]. Stop on truncation or ambiguous identities.',
    queries:[
      query('skills','skills',skillFields,{slug:EXPECTED.slug}),
      query('publicationArtifacts','skill_artifact_versions',artifactFields,publication),
      query('currentArtifacts','skill_artifact_versions',artifactFields,{...scope,id:'$uniqueSkill.current_artifact_version_id'}),
      query('observations','skill_artifact_observations',observationFields,publication),
    ],
    receiptRequirement:'Operator/runtime must retain query identity, time, exact scope, completeness and read receipt separately. JSON content cannot authenticate its own provenance.',
  };
}

export function assessSnapshot(snapshot) {
  objectKeys(snapshot,['schemaVersion','slug','publicationSha',...collections]);
  requireValue(snapshot.schemaVersion === 1 && snapshot.slug === EXPECTED.slug && snapshot.publicationSha === EXPECTED.publicationSha);
  for (const key of collections) requireValue(Array.isArray(snapshot[key]) && snapshot[key].length <= 2);
  for (const row of snapshot.skills) {
    objectKeys(row,skillFields);
    requireValue(matches(UUID,row.id) && row.slug === EXPECTED.slug && row.plugin_path === EXPECTED.root
      && nullable(SHA40,row.marketplace_commit_sha) && nullable(SHA64,row.content_hash) && nullable(SHA64,row.tree_hash)
      && nullable(UUID,row.current_artifact_version_id) && Number.isSafeInteger(row.artifact_revision) && row.artifact_revision >= 0);
  }
  const uniqueSkill = snapshot.skills.length === 1 ? snapshot.skills[0] : null;
  for (const key of ['publicationArtifacts','currentArtifacts']) for (const row of snapshot[key]) {
    objectKeys(row,artifactFields);
    requireValue(matches(UUID,row.id) && matches(UUID,row.skill_id) && row.source_path === EXPECTED.root
      && matches(SHA40,row.marketplace_commit_sha) && matches(SHA64,row.content_hash) && matches(SHA64,row.tree_hash)
      && Number.isSafeInteger(row.artifact_revision) && row.artifact_revision > 0
      && matches(/^[a-z_]{1,32}$/,row.snapshot_status));
    if (uniqueSkill) requireValue(row.skill_id === uniqueSkill.id);
    if (key === 'publicationArtifacts') requireValue(row.marketplace_commit_sha === EXPECTED.publicationSha);
  }
  for (const row of snapshot.observations) {
    objectKeys(row,observationFields);
    requireValue(matches(UUID,row.skill_id) && matches(UUID,row.artifact_version_id)
      && row.source_path === EXPECTED.root && row.marketplace_commit_sha === EXPECTED.publicationSha
      && nullable(SHA40,row.upstream_commit_sha));
    if (uniqueSkill) requireValue(row.skill_id === uniqueSkill.id);
  }
  const result = classification => ({schemaVersion:1,slug:EXPECTED.slug,publicationSha:EXPECTED.publicationSha,
    classification,inputTrust:'unverified-offline-snapshot',productionState:'UNKNOWN',replayAllowed:false,
    counts:Object.fromEntries(collections.map(k=>[k,snapshot[k].length])),
    limitation:'Snapshot consistency is not authenticated production evidence. It cannot clear a workflow gate, prove zero writes, or establish catalog/audit/callback/score/cache completion.'});
  if (!uniqueSkill) return result(snapshot.skills.length ? 'ambiguous-skill-snapshot' : 'missing-skill-snapshot');
  if (collections.some(k=>snapshot[k].length !== 1)) return result('incomplete-or-ambiguous-snapshot');
  const published = snapshot.publicationArtifacts[0], current = snapshot.currentArtifacts[0], observation = snapshot.observations[0];
  const identity = row => row.marketplace_commit_sha === EXPECTED.publicationSha
    && row.content_hash === EXPECTED.contentHash && row.tree_hash === EXPECTED.treeHash;
  const exact = identity(uniqueSkill) && identity(published) && identity(current)
    && published.id === current.id && current.id === uniqueSkill.current_artifact_version_id
    && published.artifact_revision === uniqueSkill.artifact_revision && current.artifact_revision === uniqueSkill.artifact_revision
    && published.snapshot_status === 'exact' && current.snapshot_status === 'exact'
    && observation.artifact_version_id === current.id && observation.upstream_commit_sha === EXPECTED.sourceRef;
  return result(exact ? 'exact-current-snapshot' : 'partial-historical-or-divergent-snapshot');
}

function loadSnapshot(path) {
  const fd = openSync(path,constants.O_RDONLY | constants.O_NOFOLLOW);
  try {
    const stat = fstatSync(fd);
    requireValue(stat.isFile() && stat.size > 0 && stat.size <= MAX_BYTES);
    const bytes = Buffer.alloc(MAX_BYTES + 1);
    let length = 0, count;
    do { count = readSync(fd,bytes,length,bytes.length-length,null); length += count; } while (count && length < bytes.length);
    requireValue(length <= MAX_BYTES);
    return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(0,length)));
  } finally { closeSync(fd); }
}
function main(args) {
  if (args.length === 1 && args[0] === '--plan') return readPlan();
  if (args.length === 2 && args[0] === '--snapshot') return assessSnapshot(loadSnapshot(args[1]));
  throw new Error('Invalid diagnostic snapshot');
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try { console.log(JSON.stringify(main(process.argv.slice(2)),null,2)); }
  catch { console.error('Read-only diagnostic rejected; no production operation performed.'); process.exitCode=1; }
}
