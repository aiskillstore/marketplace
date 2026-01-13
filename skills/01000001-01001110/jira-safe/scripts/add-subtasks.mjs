// Add subtasks to a Story
// Following jira-safe skill patterns for Next-Gen project
// Usage: node jira-add-subtasks.mjs SCRUM-148 "Subtask 1" "Subtask 2" "Subtask 3"
//        node jira-add-subtasks.mjs demo  (creates test story with subtasks)

// Load from environment variables (set by run.js or manually)
const JIRA_EMAIL = process.env.JIRA_EMAIL;
const JIRA_API_TOKEN = process.env.JIRA_API_TOKEN;
const JIRA_BASE_URL = process.env.JIRA_BASE_URL;
const PROJECT_KEY = process.env.JIRA_PROJECT_KEY || 'SCRUM';

// Validate required env vars
if (!JIRA_EMAIL || !JIRA_API_TOKEN || !JIRA_BASE_URL) {
  console.error('Error: Missing required environment variables.');
  console.error('Required: JIRA_EMAIL, JIRA_API_TOKEN, JIRA_BASE_URL');
  console.error('Set these in .claude/skills/jira/.env or export them manually.');
  process.exit(1);
}

const auth = Buffer.from(`${JIRA_EMAIL}:${JIRA_API_TOKEN}`).toString('base64');

const headers = {
  'Authorization': `Basic ${auth}`,
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// ==================== SKILL PATTERNS ====================
// From .claude/skills/jira/jira-safe/SKILL.md

// Create Subtask (Next-Gen pattern)
// NOTE: Next-Gen uses 'Subtask' (no hyphen), NOT 'Sub-task'
async function createSubtask(parentKey, summary) {
  const url = `${JIRA_BASE_URL}/rest/api/3/issue`;
  const body = {
    fields: {
      project: { key: PROJECT_KEY },
      issuetype: { name: 'Subtask' },  // Next-Gen: 'Subtask', Classic: 'Sub-task'
      parent: { key: parentKey },
      summary: summary
    }
  };

  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`${response.status}: ${error.substring(0, 200)}`);
  }

  return response.json();
}

// Create Story (Next-Gen pattern)
async function createStory(summary, epicKey = null) {
  const url = `${JIRA_BASE_URL}/rest/api/3/issue`;
  const fields = {
    project: { key: PROJECT_KEY },
    issuetype: { name: 'Story' },
    summary: summary
  };

  // Next-Gen: Link to parent Epic using 'parent' field (not customfield_10014)
  if (epicKey) {
    fields.parent = { key: epicKey };
  }

  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify({ fields })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`${response.status}: ${error.substring(0, 200)}`);
  }

  return response.json();
}

// Verify issue exists
async function verifyIssue(issueKey) {
  const url = `${JIRA_BASE_URL}/rest/api/3/issue/${issueKey}?fields=summary,issuetype`;
  const response = await fetch(url, { headers });

  if (!response.ok) {
    return null;
  }

  return response.json();
}

// Demo mode - creates a story with subtasks
async function runDemo() {
  console.log('========================================');
  console.log('  ADD SUBTASKS DEMO');
  console.log('  (Following jira-safe skill patterns)');
  console.log('========================================\n');

  // Create a demo story
  console.log('Creating demo Story...');
  const story = await createStory('[Demo] Test story with subtasks');
  console.log(`+ Story created: ${story.key}\n`);

  // Define demo subtasks
  const demoSubtasks = [
    'Subtask 1: Research and planning',
    'Subtask 2: Implementation',
    'Subtask 3: Testing',
    'Subtask 4: Documentation',
    'Subtask 5: Review and merge'
  ];

  console.log(`Adding ${demoSubtasks.length} subtasks to ${story.key}...`);
  const results = { created: 0, failed: 0 };

  for (const summary of demoSubtasks) {
    try {
      const subtask = await createSubtask(story.key, summary);
      console.log(`  + ${subtask.key}: ${summary}`);
      results.created++;
    } catch (error) {
      console.log(`  - FAILED: ${summary} (${error.message})`);
      results.failed++;
    }
    await new Promise(r => setTimeout(r, 100)); // Rate limiting
  }

  console.log('\n========================================');
  console.log('  SUMMARY');
  console.log('========================================');
  console.log(`Story: ${story.key}`);
  console.log(`Subtasks created: ${results.created}`);
  console.log(`Subtasks failed: ${results.failed}`);
  console.log(`\nView: ${JIRA_BASE_URL}/browse/${story.key}`);
  console.log('========================================');
}

// Main function - add subtasks to specified story
async function addSubtasksToStory(storyKey, subtaskSummaries) {
  console.log('========================================');
  console.log('  ADD SUBTASKS TO STORY');
  console.log('  (Following jira-safe skill patterns)');
  console.log('========================================\n');

  // Verify story exists
  console.log(`Verifying ${storyKey}...`);
  const story = await verifyIssue(storyKey);

  if (!story) {
    console.error(`ERROR: Issue ${storyKey} not found or not accessible.`);
    process.exit(1);
  }

  console.log(`Found: ${story.key} [${story.fields.issuetype.name}]`);
  console.log(`Summary: ${story.fields.summary}\n`);

  const results = { created: 0, failed: 0 };

  console.log(`Adding ${subtaskSummaries.length} subtasks...`);
  for (const summary of subtaskSummaries) {
    try {
      const subtask = await createSubtask(storyKey, summary);
      console.log(`  + ${subtask.key}: ${summary}`);
      results.created++;
    } catch (error) {
      console.log(`  - FAILED: ${summary} (${error.message})`);
      results.failed++;
    }
    await new Promise(r => setTimeout(r, 100)); // Rate limiting
  }

  console.log('\n========================================');
  console.log('  SUMMARY');
  console.log('========================================');
  console.log(`Story: ${storyKey}`);
  console.log(`Subtasks created: ${results.created}`);
  console.log(`Subtasks failed: ${results.failed}`);
  console.log(`\nView: ${JIRA_BASE_URL}/browse/${storyKey}`);
  console.log('========================================');
}

// Parse args and run
const args = process.argv.slice(2);

if (args.length === 0) {
  console.log('Usage:');
  console.log('  node jira-add-subtasks.mjs demo');
  console.log('    Creates a test story with 5 subtasks');
  console.log('');
  console.log('  node jira-add-subtasks.mjs SCRUM-148 "Task 1" "Task 2" "Task 3"');
  console.log('    Adds subtasks to an existing story');
  process.exit(0);
}

if (args[0] === 'demo') {
  runDemo().catch(console.error);
} else {
  const storyKey = args[0];
  const subtasks = args.slice(1);

  if (subtasks.length === 0) {
    console.error('ERROR: No subtask summaries provided.');
    console.log('Usage: node jira-add-subtasks.mjs SCRUM-148 "Task 1" "Task 2"');
    process.exit(1);
  }

  addSubtasksToStory(storyKey, subtasks).catch(console.error);
}
