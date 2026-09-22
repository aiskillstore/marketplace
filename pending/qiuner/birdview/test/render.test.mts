import { architecture, activity, present } from './fixtures.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { routeArchitecture } from '../src/viewer/routing.mjs';
import { renderArchitecture } from '../src/render.mjs';
import { validate } from '../src/validate.mjs';

const example = architecture(fs.readFileSync(new URL('../examples/architecture.json', import.meta.url), 'utf8'));
const bilingual = architecture(fs.readFileSync(new URL('../examples/bilingual.architecture.json', import.meta.url), 'utf8'));

test('rendered HTML is identical across LF and CRLF text assets', (t) => {
  const read = fs.readFileSync;
  let eol = '\n';
  t.mock.method(fs, 'readFileSync', (file: fs.PathOrFileDescriptor, options?: Parameters<typeof fs.readFileSync>[1]) => {
    const value = read(file, options);
    return typeof value === 'string' ? value.replace(/\r\n?/g, '\n').replace(/\n/g, eol) : value;
  });
  const unix = renderArchitecture(example);
  eol = '\r\n';
  assert.equal(renderArchitecture(example), unix);
  assert.ok(!unix.includes('\r'));
});
test('activity rendering validates binding and transitions before delivery', () => {
  const map = architecture(fs.readFileSync(new URL('../examples/system.architecture.json', import.meta.url), 'utf8'));
  const events = activity(fs.readFileSync(new URL('../examples/harness.activity.jsonl', import.meta.url), 'utf8'));
  const html = renderArchitecture(map, events, { simulation: true });
  assert.ok(html.includes('tool-timeout'));
  assert.ok(html.includes('"simulation":true'));
  assert.ok(!html.includes('/* BIRDVIEW_'));
  assert.match(html, /<link rel="icon" type="image\/png" href="data:image\/png;base64,/);
  assert.match(html, /"brandLogo":"data:image\/png;base64,/);
  assert.ok(html.includes(fs.readFileSync(new URL('../LICENSE', import.meta.url), 'utf8').replace(/\r\n?/g, '\n')));
  assert.ok(html.includes(fs.readFileSync(new URL('../THIRD_PARTY_NOTICES', import.meta.url), 'utf8').replace(/\r\n?/g, '\n')));
  const wrong = structuredClone(events);
  present(wrong[0]).mapRevision++;
  assert.throws(() => renderArchitecture(map, wrong), /map-mismatch/);
  const unordered = structuredClone(events);
  present(unordered[1]).sequence = 9;
  assert.throws(() => renderArchitecture(map, unordered), /sequence/);
});
test('relationships require explicit semantics and visibility; reject retired fields', () => {
  const map = structuredClone(example);
  for (const kind of ['request', 'result', 'dependency', 'event', 'control']) {
    for (const visibility of ['overview', 'detail']) {
      Object.assign(present(map.relationships[0]), { kind, visibility });
      assert.equal(validate(map).ok, true);
    }
  }
  Object.assign(present(map.relationships[0]), { primary: true });
  assert.equal(validate(map).ok, false);
  Reflect.deleteProperty(present(map.relationships[0]), 'primary');
  Reflect.deleteProperty(present(map.relationships[0]), 'visibility');
  assert.equal(validate(map).ok, false);
  present(map.relationships[0]).visibility = 'overview';
  Reflect.deleteProperty(present(map.relationships[0]), 'kind');
  assert.equal(validate(map).ok, false);
});
test('empty routing input produces no paths', () => {
  assert.deepEqual(routeArchitecture([], new Map()), []);
});

test('routes avoid intervening cards and spread shared ports, including reverse and self edges', () => {
  const positions = new Map([['a',{x:28,y:30}],['blocker',{x:232,y:30}],['b',{x:436,y:30}],['c',{x:232,y:158}]]);
  const relations = [{from:'a',to:'b'},{from:'a',to:'c'},{from:'b',to:'a'},{from:'c',to:'c'}];
  const routes = routeArchitecture(relations, positions);
  assert.notDeepEqual(present(routes[0]).points[0],present(routes[1]).points[0]);
  routes.forEach((route,index) => {
    assert.ok(!/NaN|Infinity/.test(route.d));
    assert.ok(route.points.length >= 2);
    for (let i=1;i<route.points.length;i++) {
      const a=present(route.points[i-1]),b=present(route.points[i]);
      assert.ok(a[0]===b[0] || a[1]===b[1]);
      for (const [id,p] of positions) {
        const intersects = a[0]===b[0]
          ? a[0]>p.x && a[0]<p.x+164 && Math.max(a[1],b[1])>p.y && Math.min(a[1],b[1])<p.y+72
          : a[1]>p.y && a[1]<p.y+72 && Math.max(a[0],b[0])>p.x && Math.min(a[0],b[0])<p.x+164;
        assert.equal(intersects,false,`route ${index} crosses ${id}`);
      }
    }
  });
  assert.ok(present(routes[0]).points.some(p=>p[1]<30 || p[1]>102));
});
test('diagonal neighbors use a single turn when the corridor is empty', () => {
  const positions = new Map([['a',{x:28,y:30}],['b',{x:232,y:158}]]);
  const [route] = routeArchitecture([{from:'a',to:'b'}], positions);
  assert.ok(route);
  assert.equal(route.points.length, 3);
  assert.equal(present(route.points[0])[1], 102);
  assert.equal(present(route.points.at(-1))[0], 232);
});

test('module roles accept supported values and reject invented categories', () => {
  const map = structuredClone(example);
  assert.equal(validate(map).ok, true);
  for (const role of ['frontend', 'backend', 'cache', 'database', 'queue', 'security', 'generic'] as const) {
    present(map.modules[0]).role = role;
    assert.equal(validate(map).ok, true);
  }
  Object.assign(present(map.modules[0]), { role: 'random-purple' });
  assert.equal(validate(map).ok, false);
});
test('bilingual example passes strict coverage; legacy remains compatible', () => {
  assert.equal(validate(bilingual, [], { requireBilingual: true }).ok, true);
  assert.equal(validate(example).ok, true);
  assert.equal(validate(example, [], { requireBilingual: true }).ok, false);
});
test('strict coverage detects missing evidence translation', () => {
  const map = structuredClone(bilingual);
  delete present(present(map.modules[0]).evidence[0]).translations;
  assert.ok(validate(map, [], { requireBilingual: true }).errors.some((error) => error.code === 'translation/missing'));
});
test('translations cannot alter structure or omit open questions', () => {
  const map = structuredClone(bilingual);
  Object.assign(present(present(present(map.modules[0]).translations).zh), { id: 'translated-id' });
  assert.equal(validate(map).ok, false);
  Reflect.deleteProperty(present(present(present(map.modules[0]).translations).zh), 'id');
  present(present(present(map.modules[1]).translations).zh).openQuestions = [];
  assert.ok(validate(map).errors.some((error) => error.code === 'translation/questions'));
});
test('renderer rejects invalid maps before generating HTML', () => {
  const map = structuredClone(example);
  present(map.relationships[0]).to = 'missing';
  assert.throws(() => renderArchitecture(map), /unknown-endpoint/);
});
test('group roles allow explicit semantics and preserve unclassified maps', () => {
  const map = architecture(fs.readFileSync(new URL('../examples/system.architecture.json', import.meta.url), 'utf8'));
  for (const role of ['interaction', 'runtime', 'external-services', 'generic'] as const) {
    present(present(map.groups)[0]).role = role;
    assert.equal(validate(map).ok, true);
  }
  delete present(present(map.groups)[0]).role;
  assert.equal(validate(map).ok, true);
  Object.assign(present(present(map.groups)[0]), { role: 'invented' });
  assert.equal(validate(map).ok, false);
});

test('groups reject unknown, overlapping and duplicate membership identities', () => {
  const map = structuredClone(example);
  map.groups = [{ id: 'app', name: 'Application', members: ['web'], evidence: [{ path: 'docs/system.md', note: 'Example membership.' }] }];
  assert.equal(validate(map).ok, true);
  map.groups.push(structuredClone(present(present(map.groups)[0])));
  assert.ok(validate(map).errors.some((error) => error.code === 'group/overlap'));
  assert.ok(validate(map).errors.some((error) => error.code === 'group/duplicate-id'));
  present(present(map.groups)[1]).members = ['unknown'];
  assert.ok(validate(map).errors.some((error) => error.code === 'group/unknown-member'));
});
test('language tags support non-English base text and additional translations', () => {
  const map = structuredClone(example);
  map.language = 'ja';
  map.project.name = '商品システム';
  map.project.translations = { 'pt-BR': { name: 'Sistema de produtos' } };
  assert.equal(validate(map).ok, true);
  assert.ok(renderArchitecture(map).includes('商品システム'));
  map.language = '../../invalid';
  assert.equal(validate(map).ok, false);
});
test('renderer embeds project data without allowing script termination', () => {
  const map = structuredClone(example);
  map.project.name = '</script><script>globalThis.injected=true</script>';
  const html = renderArchitecture(map);
  assert.ok(!html.includes(map.project.name));
  assert.ok(html.includes('\\u003c/script>'));
  assert.ok(html.includes('const DATA = '));
  assert.ok(!html.includes('/* BIRDVIEW_'));
});
