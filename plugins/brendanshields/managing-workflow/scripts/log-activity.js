#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';

async function main() {
  const [metricsPath, event] = process.argv.slice(2);

  if (!metricsPath || !event) {
    console.error("Usage: log-activity.js <metrics-file> <event-description>");
    process.exit(1);
  }

  try {
    const timestamp = new Date().toISOString();
    const logLine = `| ${timestamp} | ${event} |`;
    
    // Check if file exists
    try {
      await fs.access(metricsPath);
    } catch {
      // Create if missing? No, spec says metrics.md created at start.
      // But let's be robust.
      console.error(`Metrics file not found: ${metricsPath}`);
      process.exit(1);
    }

    const content = await fs.readFile(metricsPath, 'utf-8');
    
    // Append to Activity table
    // Find the Activity section
    const activityHeader = "## Activity";
    
    let newContent = content;
    
    if (content.includes(activityHeader)) {
      // Find the end of the table or section
      // We can just append to the end of the file if Activity is the last section, 
      // or find the table and insert.
      // Simplest regex replace to append to the table.
      // Assuming the table structure:
      // | Timestamp | Event |
      // |-----------|-------|
      // ... rows ...
      
      // We'll verify if the table exists.
      if (content.includes('| Timestamp | Event |')) {
         // Check for separator
         if (content.includes('|-----------|-------|')) {
             // We can just append to the end of the table. 
             // The table usually ends at the next double newline or end of file.
             // Actually, sticking it right after the separator or at the end of the existing rows is fine.
             // Regex to match the last row of the table?
             // Or just replace the separator with separator + newline + row.
             newContent = content.replace('|-----------|-------|', `|-----------|-------|\n${logLine}`);
         } else {
             // Header but no separator?
              newContent = content.replace('| Timestamp | Event |', `| Timestamp | Event |\n|-----------|-------|\n${logLine}`);
         }
      } else {
         // Section exists but no table
         newContent = content.replace(activityHeader, `${activityHeader}\n\n| Timestamp | Event |\n|-----------|-------|\n${logLine}`);
      }
    } else {
      // No activity section, append it
      newContent = content + `\n\n${activityHeader}\n\n| Timestamp | Event |\n|-----------|-------|\n${logLine}\n`;
    }

    await fs.writeFile(metricsPath, newContent);
    console.log(`Logged activity: ${event}`);

  } catch (error) {
    console.error(`Failed to log activity: ${error.message}`);
    process.exit(1);
  }
}

main();
