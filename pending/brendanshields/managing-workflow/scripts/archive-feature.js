#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { findSpecFile } from '../../../lib/utils.js';

async function main() {
  const featureId = process.argv[2];
  
  if (!featureId) {
    console.error("Usage: archive-feature.js <feature-id>");
    process.exit(1);
  }

  const projectDir = process.cwd();
  const specDir = path.join(projectDir, '.spec');
  const featureDir = path.join(specDir, 'features', featureId);
  const archiveDir = path.join(specDir, 'archive');

  try {
    await fs.access(featureDir);
  } catch {
    // Try to find by partial name if exact match fails
    try {
      const features = await fs.readdir(path.join(specDir, 'features'));
      const match = features.find(f => f.includes(featureId));
      if (match) {
        // If found, restart with full name
        const newArgs = [...process.argv];
        newArgs[2] = match;
        // Execute recursively or just set featureId (but scoped variables...)
        // Easier to just tell user or fail. 
        // Let's just report not found.
      }
    } catch {} // Ignore errors during partial match attempt
    
    console.error(`Feature directory not found: ${featureDir}`);
    process.exit(1);
  }

  // Update status to complete in spec.md before moving
  const specPath = await findSpecFile(featureDir);
  if (specPath) {
    try {
      let content = await fs.readFile(specPath, 'utf-8');
      // Update status to complete
      if (content.match(/^status:/m)) {
        content = content.replace(/^status: .*$/m, 'status: complete');
      } else {
        // Insert status if missing (unlikely given spec)
        const endFrontmatter = content.indexOf('---', 3);
        if (endFrontmatter !== -1) {
          content = content.slice(0, endFrontmatter) + 'status: complete\n' + content.slice(endFrontmatter);
        }
      }
      
      // Update timestamp
      const date = new Date().toISOString().split('T')[0];
      if (content.match(/^updated:/m)) {
        content = content.replace(/^updated: .*$/m, `updated: ${date}`);
      }
      
      await fs.writeFile(specPath, content);
    } catch (e) {
      console.warn(`Warning: Could not update spec.md status: ${e.message}`);
    }
  }

  // Ensure archive directory exists
  await fs.mkdir(archiveDir, { recursive: true });

  // Move directory
  const targetPath = path.join(archiveDir, path.basename(featureDir));
  try {
    await fs.rename(featureDir, targetPath);
    console.log(`Archived feature '${path.basename(featureDir)}' to .spec/archive/`);
  } catch (error) {
    console.error(`Failed to archive feature: ${error.message}`);
    process.exit(1);
  }
}

main();
