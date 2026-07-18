import assert from 'node:assert/strict';
import test from 'node:test';
import { activateCampaignCache } from '../finalize-artifact-governance-campaign.mjs';

test('campaign activation performs one compare-and-swap epoch bump and verifies readback', async () => {
  const requests = [];
  let epoch = 'epoch-1';
  const result = await activateCampaignCache({
    campaignProofSha256: 'a'.repeat(64),
    expectedEpoch: epoch,
    secret: 'secret',
    sleepImpl: async () => {},
    fetchImpl: async (_url, init) => {
      const body = JSON.parse(init.body);
      requests.push(body);
      if (body.action === 'read') {
        return new Response(JSON.stringify({ action: 'read', epoch, changed: false, converged: true }));
      }
      assert.equal(body.expectedEpoch, 'epoch-1');
      assert.equal(body.nextEpoch, `g-${'a'.repeat(32)}`);
      epoch = body.nextEpoch;
      return new Response(JSON.stringify({
        action: 'bump', previousEpoch: 'epoch-1', epoch, changed: true, converged: true,
      }));
    },
  });

  assert.equal(result.epoch, `g-${'a'.repeat(32)}`);
  assert.deepEqual(requests, [
    { action: 'read' },
    { action: 'bump', expectedEpoch: 'epoch-1', nextEpoch: `g-${'a'.repeat(32)}` },
    { action: 'read' },
  ]);
});

test('campaign activation refuses epoch drift without a bump request', async () => {
  const requests = [];
  await assert.rejects(activateCampaignCache({
    campaignProofSha256: 'a'.repeat(64),
    expectedEpoch: 'epoch-1',
    secret: 'secret',
    fetchImpl: async (_url, init) => {
      requests.push(JSON.parse(init.body));
      return new Response(JSON.stringify({ action: 'read', epoch: 'epoch-2', changed: false, converged: true }));
    },
  }), /catalog epoch drifted before activation/);
  assert.deepEqual(requests, [{ action: 'read' }]);
});

test('campaign activation replays an ambiguously committed CAS and repairs its KV mirror', async () => {
  const requests = [];
  const nextEpoch = `g-${'a'.repeat(32)}`;
  let converged = false;
  const result = await activateCampaignCache({
    campaignProofSha256: 'a'.repeat(64),
    expectedEpoch: 'epoch-1',
    secret: 'secret',
    sleepImpl: async () => {},
    fetchImpl: async (_url, init) => {
      const body = JSON.parse(init.body);
      requests.push(body);
      if (body.action === 'read') {
        return new Response(JSON.stringify({
          action: 'read', epoch: nextEpoch, changed: false, converged,
        }));
      }
      assert.deepEqual(body, { action: 'bump', expectedEpoch: 'epoch-1', nextEpoch });
      converged = true;
      return new Response(JSON.stringify({
        action: 'bump', previousEpoch: 'epoch-1', epoch: nextEpoch,
        changed: true, replayed: true, converged: true,
      }));
    },
  });

  assert.equal(result.epoch, nextEpoch);
  assert.equal(result.readbackVerified, true);
  assert.deepEqual(requests, [
    { action: 'read' },
    { action: 'bump', expectedEpoch: 'epoch-1', nextEpoch },
    { action: 'read' },
  ]);
});
