/**
 * [INPUT]: 依赖 node:test、合成文件树与审计公开接口
 * [OUTPUT]: 提供 macOS 大小写别名与大库存读回回归
 * [POS]: 交付复核测试；不访问真实用户项目
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { auditProject, readReviewEvidenceFile } from './audit.ts';

function fixture(run: (area: string, root: string) => void): void {
  const area = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'cfba-review-'));
  const root = path.join(area, 'CaseRoot');
  fs.mkdirSync(root);
  fs.writeFileSync(path.join(root, 'wrangler.json'), '{"main":"worker.ts"}');
  fs.writeFileSync(path.join(root, 'worker.ts'), 'export default {};');
  try { run(area, root); } finally { fs.rmSync(area, { recursive: true, force: true }); }
}

test('macOS case-insensitive volume permits a real directory case alias, not a symlink', { skip: process.platform !== 'darwin' }, context => fixture((area, root) => {
  const alias = path.join(area, 'caseroot');
  if (!fs.existsSync(alias)) { context.skip('Case-sensitive volume has no case alias'); return; }
  assert.equal(fs.lstatSync(alias).isSymbolicLink(), false);
  assert.throws(() => auditProject(alias, { outputDir: path.join(root, 'reports') }), /output-inside-project/);
  const result = auditProject(alias, { outputDir: path.join(area, 'reports') });
  assert.ok(result.outputDirectory);
  assert.equal(readReviewEvidenceFile(alias, path.join(result.outputDirectory, 'inventory.json'), 'worker.ts'), 'export default {};');
  const link = path.join(area, 'alias-link');
  fs.symlinkSync(root, link);
  assert.throws(() => auditProject(link, { writeReports: false }), /symlink/);
}));

test('a valid inventory over four MiB still authorizes its bounded evidence read', { skip: process.platform === 'win32' }, () => fixture((area, root) => {
  const parts = Array.from({ length: 7 }, (_, n) => `${n}${'\u0001'.repeat(120)}`);
  const dir = path.join(root, ...parts);
  fs.mkdirSync(dir, { recursive: true });
  const body = 'export default {};';
  for (let n = 0; n < 490; n++) fs.writeFileSync(path.join(dir, `${n}.ts`), body);
  const result = auditProject(root, { outputDir: path.join(area, 'reports') });
  assert.ok(result.outputDirectory);
  const inventory = path.join(result.outputDirectory, 'inventory.json');
  assert.ok(fs.statSync(inventory).size > 4 * 1024 * 1024, 'Positive control must exceed the former ceiling');
  assert.ok(result.report.readSourceFiles.includes('worker.ts'));
  assert.equal(readReviewEvidenceFile(root, inventory, 'worker.ts'), body);
}));
