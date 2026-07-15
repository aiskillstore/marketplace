import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import test from 'node:test';

const workflow = readFileSync(
  resolve(process.cwd(), '.github/workflows/sync-to-supabase.yml'),
  'utf8',
);

test('sync uses an attestation-capable CLI and a dedicated issuance credential', () => {
  assert.match(workflow, /version: '2\.3\.0'/);
  assert.match(workflow, /minimum-version: '2\.3\.0'/);
  assert.match(
    workflow,
    /SECURITY_PASSPORT_MODE: \$\{\{ vars\.SECURITY_PASSPORT_MODE \|\| 'off' \}\}/,
  );
  assert.match(workflow, /PUBLIC_SITE_URL: https:\/\/skillstore\.io/);
  assert.match(
    workflow,
    /SECURITY_NOTIFICATIONS_ENABLED: \$\{\{ vars\.SECURITY_NOTIFICATIONS_ENABLED \|\| 'false' \}\}/,
  );
  assert.match(
    workflow,
    /AUTOMATION_API_KEY: \$\{\{ secrets\.SECURITY_ATTESTATION_AUTOMATION_KEY \}\}/,
  );
  assert.doesNotMatch(
    workflow,
    /AUTOMATION_API_KEY: \$\{\{ secrets\.(?:AUTOMATION_API_KEY|SKILLSTORE_CALLBACK_TOKEN) \}\}/,
  );
});
