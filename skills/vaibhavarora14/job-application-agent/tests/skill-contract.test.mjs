import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

test('requires direct path resume upload before native picker fallback', async () => {
  const skill = await readFile(new URL('../SKILL.md', import.meta.url), 'utf8');
  const guidance = await readFile(new URL('../references/BROWSER_UPLOADS.md', import.meta.url), 'utf8');

  assert.match(skill, /resume path/);
  assert.match(skill, /BROWSER_UPLOADS\.md/);
  assert.match(guidance, /absolute path/i);
  assert.match(guidance, /file chooser/i);
  assert.match(guidance, /setFiles/);
  assert.match(guidance, /native (file )?picker.*fallback/i);
  assert.match(guidance, /verify.*filename/i);
});

test('documents durable autonomy, resumable rounds, attention and friction controls', async () => {
  const skill = await readFile(new URL('../SKILL.md', import.meta.url), 'utf8');
  const autonomy = await readFile(new URL('../references/AUTONOMY.md', import.meta.url), 'utf8');
  const runs = await readFile(new URL('../references/RUNS.md', import.meta.url), 'utf8');

  assert.match(skill, /autonomy status/);
  assert.match(skill, /round status/);
  assert.match(skill, /attention list/);
  assert.match(skill, /friction record/);
  assert.match(autonomy, /never.*merge.*publish/i);
  assert.match(autonomy, /CAPTCHA/i);
  assert.match(runs, /visible.*confirmation/i);
  assert.match(runs, /discoverySource/);
  assert.match(runs, /applicationChannel/);
});
