#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';

async function main() {
  const [filePath, newStatus] = process.argv.slice(2);
  
  if (!filePath || !newStatus) {
    console.error("Usage: update-status.js <file> <status>");
    process.exit(1);
  }

  try {
    const content = await fs.readFile(filePath, 'utf-8');
    const updatedContent = content.replace(/^status: .*$/m, `status: ${newStatus}`)
                                  .replace(/^updated: .*$/m, `updated: ${new Date().toISOString().split('T')[0]}`);
    
    await fs.writeFile(filePath, updatedContent);
    console.log(`Updated status to ${newStatus}`);
  } catch (error) {
    console.error(`Failed to update status: ${error.message}`);
    process.exit(1);
  }
}

main();
