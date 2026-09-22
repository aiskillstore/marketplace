import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { Ajv2020, type ValidateFunction } from 'ajv/dist/2020.js';
import { checkArchitecture, checkActivity } from '../src/contracts/parse.mjs';

const read = (file: string): Record<string, unknown> => JSON.parse(fs.readFileSync(new URL(file, import.meta.url), 'utf8'));
const generated = new Ajv2020({ allErrors: true, strict: true, formats: { 'date-time': true } });
generated.addSchema(read('../schemas/architecture.schema.json'));
const generatedMap = generated.getSchema('urn:birdview:architecture:1');
const generatedEvent = generated.compile(read('../schemas/activity.schema.json'));

function* mutations(value: unknown, path: string[] = []): Generator<[string[], unknown]> {
  yield [path, null];
  yield [path, ''];
  yield [path, 'unknown-value'];
  yield [path, -1];
  if (value && typeof value === 'object') {
    if (Array.isArray(value)) {
      yield [path, []];
      if (value.length) yield [path, [value[0], value[0]]];
    } else {
      yield [path, { ...value, unexpectedField: true }];
      for (const key of Object.keys(value)) {
        const copy: Record<string, unknown> = { ...value };
        delete copy[key];
        yield [path, copy];
      }
    }
    for (const [key, item] of Object.entries(value)) yield* mutations(item, [...path, key]);
  }
}

assert.ok(generatedMap);

test('typed runtime and exported schemas agree without mutating inputs', () => {
  const maps = ['architecture', 'bilingual.architecture', 'system.architecture'].map(name => read(`../examples/${name}.json`));
  const events: unknown[] = ['activity.jsonl', 'harness.activity.jsonl'].flatMap(name => fs.readFileSync(new URL(`../examples/${name}`, import.meta.url), 'utf8').trim().split(/\r?\n/).map(line => JSON.parse(line)));
  let compared = 0;
  const comparisons: [unknown[], (value: unknown) => boolean, ValidateFunction][] = [[maps, checkArchitecture, generatedMap], [events, checkActivity, generatedEvent]];
  for (const [fixtures, current, exchange] of comparisons) {
    for (const original of fixtures) {
      assert.equal(current(original), true);
      const variants: [string[], unknown][] = [[[], original], ...mutations(original)];
      for (const [path, replacement] of variants) {
        let input = structuredClone(original);
        if (!path.length) input = structuredClone(replacement);
        else {
          let parent = input;
          for (const key of path.slice(0, -1)) {
            assert.ok(parent && typeof parent === 'object');
            parent = Reflect.get(parent, key);
          }
          assert.ok(parent && typeof parent === 'object');
          const key = path.at(-1);
          assert.ok(key !== undefined);
          Reflect.set(parent, key, structuredClone(replacement));
        }
        const before = structuredClone(input);
        const expected = current(input);
        assert.equal(exchange(input), expected, `export parity at ${path.join('/')}`);
        assert.deepEqual(input, before, 'validation must not coerce or strip input');
        compared++;
      }
    }
  }
  assert.ok(compared > 1000);
});

test('public schema anchors remain available to external references', () => {
  const defs = read('../schemas/architecture.schema.json').$defs;
  assert.ok(defs && typeof defs === 'object');
  for (const name of Object.keys(defs)) {
    assert.ok(generated.getSchema(`urn:birdview:architecture:1#/$defs/${name}`));
  }
  assert.ok(generated.getSchema('urn:birdview:activity:1#/$defs/paths'));
});
