import { select, input, checkbox } from '@inquirer/prompts';
import { loadRegistry } from '../core/registry.js';
import { validateRegistry } from '../core/validator.js';
import { createSkillScaffold, scanAndAutoRegister } from '../core/dev/scaffold.js';
import { editorPresets } from '../core/presets/editors.js';

const MENU_STATUS = 'status';
const MENU_CREATE = 'create';
const MENU_SCAN = 'scan';
const MENU_VALIDATE = 'validate';
const MENU_EXIT = 'exit';

export async function devPanelCommand() {
  console.log('\n\u{1F527} \u5f00\u53d1\u8005\u6a21\u5f0f \u2014 \u7ba1\u7406\u9762\u677f\n');

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const action = await select<string>({
      message: '\u8bf7\u9009\u62e9\u64cd\u4f5c\uff1a',
      choices: [
        { name: '\u{1F4CB} \u67e5\u770b Registry \u72b6\u6001', value: MENU_STATUS },
        { name: '\u2795 \u521b\u5efa\u65b0 Skill', value: MENU_CREATE },
        { name: '\ud83d\udd0d \u626b\u63cf\u5e76\u81ea\u52a8\u6ce8\u518c Bundles', value: MENU_SCAN },
        { name: '\u2705 \u6821\u9a8c Registry', value: MENU_VALIDATE },
        { name: '\u00d7 \u9000\u51fa', value: MENU_EXIT },
      ],
    });

    if (action === MENU_EXIT) {
      console.log('\u5df2\u9000\u51fa\u5f00\u53d1\u8005\u9762\u677f\u3002');
      process.exit(0);
    }

    if (action === MENU_STATUS) {
      await showRegistryStatus();
    } else if (action === MENU_CREATE) {
      await createSkillFlow();
    } else if (action === MENU_SCAN) {
      await scanFlow();
    } else if (action === MENU_VALIDATE) {
      await validateFlow();
    }
  }
}

async function showRegistryStatus() {
  const registry = await loadRegistry();
  const totalSkills = registry.reduce((sum, g) => sum + g.skills.length, 0);

  console.log(`\nRegistry \u72b6\u6001\uff1a${registry.length} \u4e2a\u5206\u7c7b\uff0c${totalSkills} \u4e2a skills`);
  for (const group of registry) {
    console.log(`  [${group.displayName}] ${group.skills.length} skills`);
    for (const skill of group.skills) {
      const srcType = skill.source ? skill.source.type : skill.bundle ? 'bundle' : 'unknown';
      console.log(`    \u2022 ${skill.display_name} (${skill.name}) \u2014 ${srcType}`);
    }
  }
  console.log('');
}

async function createSkillFlow() {
  const registry = await loadRegistry();
  const categories = registry.map((g) => ({ name: g.displayName, value: g.id }));

  const name = await input({
    message: 'Skill \u6807\u8bc6\u540d\uff08\u5982 my-awesome-skill\uff09\uff1a',
    validate: (value) => {
      if (!value.trim()) return '\u4e0d\u80fd\u4e3a\u7a7a';
      if (!/^[a-z0-9-]+$/.test(value)) return '\u53ea\u80fd\u4f7f\u7528\u5c0f\u5199\u5b57\u6bcd\u3001\u6570\u5b57\u548c\u77ed\u6a2a\u7ebf';
      return true;
    },
  });

  const category = await select<string>({
    message: '\u9009\u62e9\u5206\u7c7b\uff1a',
    choices: categories,
  });

  const displayName = await input({ message: 'Skill \u663e\u793a\u540d\uff08\u53ef\u7559\u7a7a\uff09\uff1a', default: name });
  const description = await input({ message: '\u7b80\u8981\u63cf\u8ff0\uff08\u53ef\u7559\u7a7a\uff09\uff1a' });
  const author = await input({ message: '\u4f5c\u8005\uff08\u53ef\u7559\u7a7a\uff09\uff1a' });

  // Ask which editors this skill targets
  const editorChoices = editorPresets.map((e) => ({ name: e.name, value: e.id, checked: e.defaultEnabled }));
  const selectedEditors = await checkbox<string>({
    message: '\u9009\u62e9\u9002\u914d\u7684\u76ee\u6807\u7f16\u8f91\u5668\uff08\u7528\u4e8e\u81ea\u52a8\u9a8c\u8bc1\uff09\uff1a',
    choices: editorChoices,
  });

  try {
    const bundleDir = await createSkillScaffold({
      name,
      category,
      displayName: displayName || name,
      description,
      author: author || undefined,
    });

    console.log(`\n\u2713 \u5df2\u521b\u5efa Skill \u811a\u624b\u67b6\uff1a`);
    console.log(`  Bundle: ${bundleDir}`);
    console.log(`  Registry: registry/${name}.yaml`);
    if (selectedEditors.length > 0) {
      console.log(`  \u9002\u914d\u7f16\u8f91\u5668: ${selectedEditors.join(', ')}`);
    }
    console.log('\n\u63d0\u793a\uff1a\u8bf7\u7f16\u8f91 SKILL.md \u5185\u5bb9\uff0c\u5b8c\u6210\u540e\u8fd0\u884c \u201c\u626b\u63cf\u5e76\u81ea\u52a8\u6ce8\u518c\u201d \u6216 \u201copen-skills validate\u201d \u8fdb\u884c\u6821\u9a8c\u3002\n');
  } catch (err: any) {
    console.error(`\u2717 \u521b\u5efa\u5931\u8d25: ${err.message}`);
  }
}

async function scanFlow() {
  console.log('\n\u6b63\u5728\u626b\u63cf bundles/ \u76ee\u5f55...');
  const { registered, skipped } = await scanAndAutoRegister();

  if (registered.length > 0) {
    console.log(`\u2713 \u81ea\u52a8\u6ce8\u518c ${registered.length} \u4e2a skills:`);
    for (const name of registered) {
      console.log(`  + ${name}`);
    }
  } else {
    console.log('\u6ca1\u6709\u65b0\u7684 skills \u9700\u8981\u6ce8\u518c\u3002');
  }

  if (skipped.length > 0) {
    console.log(`\n\u8df3\u8fc7 ${skipped.length} \u4e2a\uff08\u5df2\u6ce8\u518c\u6216\u7f3a\u5c11 SKILL.md\uff09:`);
    for (const name of skipped.slice(0, 10)) {
      console.log(`  - ${name}`);
    }
    if (skipped.length > 10) {
      console.log(`  ...\u8fd8\u6709 ${skipped.length - 10} \u4e2a`);
    }
  }
  console.log('');
}

async function validateFlow() {
  const errors = await validateRegistry();
  if (errors.length === 0) {
    console.log('\n\u2713 Registry \u6821\u9a8c\u901a\u8fc7\uff0c\u672a\u53d1\u73b0\u95ee\u9898\n');
    return;
  }
  console.log(`\n\u2717 Registry \u6821\u9a8c\u5931\u8d25\uff0c\u53d1\u73b0 ${errors.length} \u4e2a\u95ee\u9898\uff1a\n`);
  for (const err of errors) {
    console.log(`  \u6587\u4ef6: ${err.file}`);
    console.log(`  \u9519\u8bef: ${err.message}\n`);
  }
}
