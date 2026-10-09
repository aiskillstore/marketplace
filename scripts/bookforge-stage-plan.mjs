#!/usr/bin/env node
// Proposal only: no connector, stage executor, CAS or receipt verifier.
import {pathToFileURL} from 'node:url';
import {EXPECTED, assessSnapshot, readPlan} from './bookforge-readonly-diagnostic.mjs';

const identityFields = ['schemaVersion','slug','root','publicationSha','contentHash','treeHash','sourceRef','skillId','artifactVersionId','artifactRevision'];
const UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
function requireValue(ok) { if (!ok) throw new Error('Invalid stage plan input'); }
// Capture descriptors once: never invoke caller accessors or validate then reread
// caller-owned properties. The assessor and binder share this owned data copy.
const snapshotCollections = readPlan().queries.map(q=>({name:q.name,fields:q.select}));
function dataDescriptors(value, array=false) {
  requireValue(value !== null && typeof value === 'object' && Array.isArray(value) === array);
  const descriptors = Object.getOwnPropertyDescriptors(value);
  requireValue(Reflect.ownKeys(descriptors).every(k=>Object.hasOwn(descriptors[k],'value')));
  return descriptors;
}
function ownValues(descriptors, fields) {
  requireValue(Reflect.ownKeys(descriptors).length === fields.length && fields.every(k=>Object.hasOwn(descriptors,k)));
  return Object.fromEntries(fields.map(k=>[k,descriptors[k].value]));
}
function ownedSnapshot(input) {
  const snapshot = ownValues(dataDescriptors(input),['schemaVersion','slug','publicationSha',...snapshotCollections.map(q=>q.name)]);
  for (const {name,fields} of snapshotCollections) {
    const descriptors = dataDescriptors(snapshot[name],true);
    const length = descriptors.length.value;
    requireValue(Number.isSafeInteger(length) && length >= 0 && length <= 2);
    const indices = Array.from({length},(_,i)=>String(i));
    const values = ownValues(descriptors,['length',...indices]);
    snapshot[name] = indices.map(i=>ownValues(dataDescriptors(values[i]),fields));
  }
  return snapshot;
}
function validateIdentity(input) {
  const value = ownValues(dataDescriptors(input),identityFields);
  requireValue(value.schemaVersion === 1 && value.slug === EXPECTED.slug && value.root === EXPECTED.root
    && value.publicationSha === EXPECTED.publicationSha && value.contentHash === EXPECTED.contentHash
    && value.treeHash === EXPECTED.treeHash && value.sourceRef === EXPECTED.sourceRef);
  requireValue(typeof value.skillId === 'string' && UUID.test(value.skillId)
    && typeof value.artifactVersionId === 'string' && UUID.test(value.artifactVersionId)
    && Number.isSafeInteger(value.artifactRevision) && value.artifactRevision > 0);
  return value;
}
export function bindExpectedCurrent(input) {
  // Reuse the exact three-table schema/incident validator; no provenance claim.
  try {
    const snapshot = ownedSnapshot(input);
    requireValue(assessSnapshot(snapshot).classification === 'exact-current-snapshot');
    const skill = snapshot.skills[0];
    return {schemaVersion:1,slug:EXPECTED.slug,root:EXPECTED.root,publicationSha:EXPECTED.publicationSha,
      contentHash:EXPECTED.contentHash,treeHash:EXPECTED.treeHash,sourceRef:EXPECTED.sourceRef,
      skillId:skill.id,artifactVersionId:skill.current_artifact_version_id,artifactRevision:skill.artifact_revision};
  } catch { throw new Error('Invalid stage plan input'); }
}
export function compareExpectedCurrent(expectedCurrent, snapshot) {
  try {
    const expected = validateIdentity(expectedCurrent);
    const observed = bindExpectedCurrent(snapshot);
    return {schemaVersion:1,identityMatches:identityFields.every(k=>observed[k] === expected[k]),
      inputTrust:'unverified-offline-snapshot',atomicCasPerformed:false,productionState:'UNKNOWN',
      replayAllowed:false,continuationAllowed:false};
  } catch { throw new Error('Invalid stage plan input'); }
}
export function stageReadPlan(...args) {
  requireValue(args.length === 0);
  const skillScope = {skill_id:'$expectedCurrent.skillId'};
  const catalogScope = {id:'$expectedCurrent.skillId',slug:EXPECTED.slug};
  const query = (name,table,select,filters,order=[],cardinality='zero-or-one') => ({name,method:'GET',schema:'skillstore',table,select,filters,order,limit:2,cardinality,completeness:cardinality==='latest-candidate'?'latest-only':cardinality==='bounded-candidates'?'bounded-only':'singleton'});
  const stage = (name,proofRequirements) => ({name,state:'UNKNOWN',proofRequirements});
  return {
    schemaVersion:1,slug:EXPECTED.slug,root:EXPECTED.root,publicationSha:EXPECTED.publicationSha,
    submissionId:'df71079f-cd85-4980-8be5-6a3921396e83',
    authorizesExecution:false,productionState:'UNKNOWN',replayAllowed:false,continuationAllowed:false,
    readScopeApproved:false,executorImplemented:false,
    prerequisites:'Separate scoped read authority and runtime connector are required. This proposal does not expand the approved artifact/current/observation diagnostic.',
    dependencies:'Bind expectedCurrent from one complete exact incident snapshot. Require runtime provenance and fresh identity read before use. Do not query unresolved placeholders. Validate latest audit binding before verifiedAudit; validate source_type/source_id/skill_id/version and projected_event_id before verifiedProjectionJob. Singleton lookups require exactly one matching row to prove completion; zero means unresolved, two means ambiguous. Audit is a latest-candidate query: two historical audits are not duplicates; select the highest version/created_at/id and verify exact subject, without searching older rows to bypass a newer divergent audit. Attestations are bounded candidates only; multiple keys may exist, and this read makes no complete-history claim. Stop on ambiguous identities, singleton truncation or divergent data; no automatic write follows any read.',
    casContract:'A future authorized executor must lock and compare skillId, slug/root, current artifactVersionId, artifactRevision, publicationSha, contentHash, treeHash and sourceRef in the same transaction as each database mutation. This module performs only offline equality, not atomic CAS. Preserve artifact snapshots and timestamp semantics; if already complete do not write, and if current identity changed fail closed. External effects need independent deduplication and durable before/after evidence; a prior DB CAS alone cannot make a callback safe.',
    queries:[
      query('catalog','skills',['id','slug','plugin_path','marketplace_commit_sha','content_hash','tree_hash','current_artifact_version_id','artifact_revision','published_at','updated_at'],catalogScope),
      query('aiContent','skill_ai_content',['id','skill_id','content_hash','content_version','created_at','updated_at'],skillScope),
      query('audit','skill_security_audit',['id','skill_id','version','subject_marketplace_commit_sha','subject_content_hash','subject_tree_hash','subject_plugin_path','audit_payload_hash','created_at','audited_at'],skillScope,['version.desc','created_at.desc','id.desc'],'latest-candidate'),
      query('projectionJob','security_change_projection_jobs',['id','skill_id','source_type','source_id','source_version','projected_event_id','projected_at','created_at'],{...skillScope,source_type:'audit',source_id:'$verifiedAudit.id'}),
      query('projectionEvent','security_change_events',['id','skill_id','source_type','source_id','idempotency_key','created_at'],{...skillScope,id:'$verifiedProjectionJob.projected_event_id',source_type:'audit',source_id:'$verifiedAudit.id'}),
      query('eligibility','skills',['id','slug','public_eligible','public_eligibility_audit_id'],catalogScope),
      query('attestation','security_audit_attestations',['id','audit_id','schema_version','payload_sha256','issued_at','created_at'],{audit_id:'$verifiedAudit.id'},['issued_at.desc','id.desc'],'bounded-candidates'),
      query('submission','submissions',['id','status','published_at','published_skill_slugs'],{id:'df71079f-cd85-4980-8be5-6a3921396e83'}),
      query('notification','submission_github_notifications',['id','submission_id','event','comment_url','created_at','updated_at'],{submission_id:'df71079f-cd85-4980-8be5-6a3921396e83',event:'published'}),
      query('score','skills',['id','slug','quality_score','quality_tier','quality_score_calculated_at','current_quality_score_snapshot_id'],catalogScope),
    ],
    stages:[
      stage('catalog',['Runtime-authenticated before/after reads bound to expectedCurrent; metadata existence and timestamps alone cannot prove projection content. A reviewed canonical input digest and exact projected metadata comparison are still required before deciding no-op or authorized CAS.']),
      stage('ai-content',['Runtime evidence of canonical input digest and projected AI content digest for the same artifact. Row id, content_version and updated_at alone cannot prove content completion; no payload or credentials are requested here.']),
      stage('audit',['Latest audit metadata has exact subject binding and authoritative source provenance; no risk conclusion is read or changed. Missing audit cannot be manufactured by draining projection jobs; 24h dedup is not permanent idempotency.']),
      stage('durable-event',['Verified audit id/version matches projection job source identity and event; projected_event_id/projected_at and idempotency_key must be checked against independently verified immutable source. Global drain success is not per-slug proof.']),
      stage('eligibility-attestation',['Eligibility audit pointer matches the verified audit; independently verified attestation digest and authorized eligibility evidence are required. Metadata cannot authenticate a signature or prove public safety; no signing, override or refresh is performed.']),
      stage('callback',['Submission status and notification ledger require independent evidence of comment delivery, favorites and skill event effects. An Idempotency-Key header or claim row does not prove end-to-end idempotency. Separate already completed effects from missing effects; no blind callback.']),
      stage('score',['Runtime evidence binds current score snapshot and exact inputs to expectedCurrent and verified audit. Timestamp/score alone is insufficient. Use the separately authorized single-slug scoring path only after dependencies are verified.']),
      stage('cache',['Independent cache build/key/version and second HIT/SKIPPED evidence for this slug and containing pack derivatives. A partial failed sync may already invalidate cache. No invented cache or downstream success receipts.']),
    ],
    receiptContract:{
      verifierImplemented:false,
      requiredFields:['stage','scope','expectedCurrent','inputDigest','beforeReadRef','effectRef','afterReadRef','observedAt','outcome'],
      trust:'JSON cannot authenticate its own provenance. An independent verifier must resolve durable runtime/provider refs, exact scope and version, sequence, input digest, final state and duplicate handling. Claimed success is not consumed by this module.',
      unknownEffect:'If any effect is unknown, stop: no replay until the exact effect is authoritatively reconciled. Do not turn timeouts into zero-write or success claims.',
      continuation:'Existing publication reconciliation requires same-SHA full manual sync success. This proposal cannot produce that artifact or unlock continuation; staged receipt support remains unimplemented and requires separate review.',
    },
  };
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    const args = process.argv.slice(2);
    requireValue(args.length === 1 && args[0] === '--plan');
    console.log(JSON.stringify(stageReadPlan(),null,2));
  } catch {
    console.error('Stage plan rejected; no production operation performed.');
    process.exitCode = 1;
  }
}
