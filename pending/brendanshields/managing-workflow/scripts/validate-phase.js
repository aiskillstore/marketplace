#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { ValidationResultSchema } from '../../../lib/schema.js';
import { findSpecFile, getFrontmatter, getArtifacts } from '../../../lib/utils.js';

async function main() {
  const [featureDir, targetPhase] = process.argv.slice(2);
  
  if (!featureDir || !targetPhase) {
    console.error("Usage: validate-phase.js <feature-dir> <target-phase>");
    process.exit(1);
  }

  const result = {
    valid: true,
    missing: [],
    suggestion: ""
  };

  try {
    const specPath = await findSpecFile(featureDir);
    if (!specPath) {
      result.valid = false;
      result.missing.push("spec.md");
      result.suggestion = "Create spec.md first";
      console.log(JSON.stringify(result));
      return;
    }

    const frontmatter = await getFrontmatter(specPath);
    const artifacts = await getArtifacts(featureDir);

    if (targetPhase === 'clarification') {
      // Check if spec exists (already checked)
    } else if (targetPhase === 'planning') {
      // Check for CLARIFY tags
      const content = await fs.readFile(specPath, 'utf-8');
      if (content.includes('[CLARIFY]')) {
        result.valid = false;
        result.suggestion = "Resolve [CLARIFY] tags before planning";
      }
    } else if (targetPhase === 'implementation') {
      if (!artifacts.includes('plan.md')) result.missing.push('plan.md');
      if (!artifacts.includes('tasks.md')) result.missing.push('tasks.md');
      
      if (result.missing.length > 0) {
        result.valid = false;
        result.suggestion = `Create missing artifacts: ${result.missing.join(', ')}`;
      }
    } else if (targetPhase === 'complete') {
      // Check tasks
      const tasksPath = path.join(featureDir, 'tasks.md');
      try {
        const content = await fs.readFile(tasksPath, 'utf-8');
        if (content.includes('- [ ]')) {
          result.valid = false;
          result.suggestion = "Complete all tasks before marking complete";
        }
      } catch {
        result.valid = false;
        result.missing.push('tasks.md');
        result.suggestion = "tasks.md missing";
      }
    }

    ValidationResultSchema.parse(result);
    console.log(JSON.stringify(result));

  } catch (error) {
    console.error(error);
    process.exit(1);
  }
}

main();
