import { validateRegistry } from '../core/validator.js';

export async function validateCommand() {
  const errors = await validateRegistry();
  if (errors.length === 0) {
    console.log('✓ Registry 校验通过，未发现问题');
    return;
  }
  console.log(`✗ Registry 校验失败，发现 ${errors.length} 个问题：\n`);
  for (const err of errors) {
    console.log(`  文件: ${err.file}`);
    console.log(`  错误: ${err.message}\n`);
  }
  process.exit(1);
}
