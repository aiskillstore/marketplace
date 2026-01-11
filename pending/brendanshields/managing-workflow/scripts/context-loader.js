#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { ContextSchema } from '../../../lib/schema.js';
import { getFeatureContext } from '../../../lib/utils.js';

async function main() {
  try {
    const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
    
    const { features, suggestion } = await getFeatureContext(projectDir);
    
    const specDir = path.join(projectDir, '.spec');
    const archDir = path.join(specDir, 'architecture');
    
    let hasPrd = false;
    let hasTdd = false;

    try {
      await fs.access(path.join(archDir, 'product-requirements.md'));
      hasPrd = true;
    } catch {}

    try {
      await fs.access(path.join(archDir, 'technical-design.md'));
      hasTdd = true;
    } catch {}

    const context = {
      features,
      architecture: { has_prd: hasPrd, has_tdd: hasTdd },
      suggestion
    };

    ContextSchema.parse(context);
    console.log(JSON.stringify(context));

  } catch (error) {
    // If spec dir doesn't exist, getFeatureContext might return empty or throw if logic was different.
    // But getFeatureContext handles missing dirs gracefully by returning empty list.
    // Only issue is if .spec doesn't exist at all.
    // getFeatureContext checks projectDir/.spec so it's fine.
    
    // Check if error was just "validation failed" or something else
    console.error(error);
    process.exit(1);
  }
}

main();