---
name: jira-workflow
description: Orchestrate Jira workflows end-to-end. Use when building stories with approvals, transitioning items through lifecycle states, or syncing task completion with Jira.
---

# Jira Workflow Orchestration Skill

> Complete workflow management for Jira: building stories (SAFe), getting approvals, and transitioning items through the development lifecycle (To Do → Progressing → Done).

**IMPORTANT**: This project uses Next-Gen (Team-managed) Jira with custom workflow states. The actual states are:
- `To Do` (backlog)
- `In Review`
- `Progressing` (active work)
- `Out Review`
- `Done`

Always query available transitions first: `GET /rest/api/3/issue/{key}/transitions`

## When to Use

- Creating new user stories, epics, or tasks for the project
- Getting user approval before creating Jira items
- Moving stories through workflow states as work progresses
- Syncing Claude Code task completion with Jira status
- Managing sprint planning and backlog refinement
- Tracking development progress in real-time

## Prerequisites

**Environment Variables:**
```bash
JIRA_EMAIL=your.email@domain.com
JIRA_API_TOKEN=your_api_token
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_PROJECT_KEY=SCRUM
JIRA_BOARD_ID=1
```

**Project Configuration:**
- Must know if project is Next-Gen (Team-managed) or Classic (Company-managed)
- Next-Gen: Use `parent` field for Epic links
- Classic: Use `customfield_10014` for Epic links

---

## Core Workflow Pattern

### The Approval-Create-Track Loop

```
1. PLAN: Analyze task requirements
   ↓
2. PROPOSE: Present story to user for approval
   ↓
3. APPROVE: User confirms or modifies
   ↓
4. CREATE: Issue created in Jira backlog
   ↓
5. START: Transition to "Progressing" when work begins
   ↓
6. COMPLETE: Transition to "Done" when work verified
   ↓
7. SYNC: Update Jira with implementation details
```

---

## Phase 1: Story Building (SAFe Format)

### Building a Story Proposal

When user requests work, build a SAFe-compliant story proposal:

```javascript
function buildStoryProposal(task) {
  return {
    summary: `As a ${task.persona}, I want ${task.goal}, so that ${task.benefit}`,
    description: {
      userStory: `As a **${task.persona}**, I want **${task.goal}**, so that **${task.benefit}**.`,
      acceptanceCriteria: task.scenarios.map(s => ({
        name: s.name,
        given: s.given,
        when: s.when,
        then: s.then
      })),
      definitionOfDone: [
        'Code reviewed and approved',
        'Unit tests written and passing',
        'Integration tests passing',
        'Documentation updated',
        'Deployed to staging',
        'Validated in production'
      ],
      technicalNotes: task.technicalNotes || []
    },
    category: task.category, // authentication, ui, api, database, etc.
    estimatedComplexity: task.complexity || 'medium', // small, medium, large
    subtasks: task.subtasks || []
  };
}
```

### Presenting for Approval

**CRITICAL: Always get user approval before creating Jira items.**

Use this prompt pattern:

```markdown
## Proposed Jira Story

**Summary:** As a [persona], I want [goal], so that [benefit]

**Category:** [category]
**Complexity:** [small/medium/large]

### Acceptance Criteria

**Scenario 1: [Name]**
- **GIVEN** [precondition]
- **WHEN** [action]
- **THEN** [expected result]

### Subtasks (if any)
1. [Subtask 1]
2. [Subtask 2]
3. [Subtask 3]

---

**Do you want me to create this in Jira?**

Options:
1. **Yes, create as-is** - I'll create the story now
2. **Modify** - Tell me what to change
3. **Skip** - Don't create in Jira, just do the work
```

---

## Phase 2: Issue Creation

### Create Story in Jira

```javascript
const JIRA_EMAIL = process.env.JIRA_EMAIL;
const JIRA_API_TOKEN = process.env.JIRA_API_TOKEN;
const JIRA_BASE_URL = process.env.JIRA_BASE_URL;
const PROJECT_KEY = process.env.JIRA_PROJECT_KEY;

const auth = Buffer.from(`${JIRA_EMAIL}:${JIRA_API_TOKEN}`).toString('base64');
const headers = {
  'Authorization': `Basic ${auth}`,
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};

async function createStory(proposal, epicKey = null) {
  const body = {
    fields: {
      project: { key: PROJECT_KEY },
      issuetype: { name: 'Story' },
      summary: proposal.summary,
      description: buildADF(proposal.description),
      labels: [proposal.category.toLowerCase().replace(/\s+/g, '-')]
    }
  };

  // Link to Epic (Next-Gen project)
  if (epicKey) {
    body.fields.parent = { key: epicKey };
  }

  const response = await fetch(`${JIRA_BASE_URL}/rest/api/3/issue`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create story: ${error}`);
  }

  const issue = await response.json();
  console.log(`Created: ${issue.key} - ${proposal.summary}`);

  // Create subtasks if any
  if (proposal.subtasks?.length > 0) {
    for (const subtask of proposal.subtasks) {
      await createSubtask(issue.key, subtask);
      await delay(100); // Rate limiting
    }
  }

  return issue;
}

async function createSubtask(parentKey, summary) {
  const body = {
    fields: {
      project: { key: PROJECT_KEY },
      issuetype: { name: 'Subtask' }, // Note: 'Subtask' for Next-Gen
      parent: { key: parentKey },
      summary: summary
    }
  };

  const response = await fetch(`${JIRA_BASE_URL}/rest/api/3/issue`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create subtask: ${error}`);
  }

  return response.json();
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Build Atlassian Document Format (ADF)

```javascript
function buildADF(content) {
  const sections = [];

  // User Story Section
  sections.push({
    type: 'heading',
    attrs: { level: 2 },
    content: [{ type: 'text', text: 'User Story' }]
  });
  sections.push({
    type: 'paragraph',
    content: [{ type: 'text', text: content.userStory }]
  });

  // Acceptance Criteria Section
  sections.push({
    type: 'heading',
    attrs: { level: 2 },
    content: [{ type: 'text', text: 'Acceptance Criteria' }]
  });

  for (const scenario of content.acceptanceCriteria) {
    sections.push({
      type: 'heading',
      attrs: { level: 3 },
      content: [{ type: 'text', text: `Scenario: ${scenario.name}` }]
    });
    sections.push({
      type: 'bulletList',
      content: [
        { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: `GIVEN ${scenario.given}`, marks: [{ type: 'strong' }] }] }] },
        { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: `WHEN ${scenario.when}`, marks: [{ type: 'strong' }] }] }] },
        { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: `THEN ${scenario.then}`, marks: [{ type: 'strong' }] }] }] }
      ]
    });
  }

  // Definition of Done Section
  sections.push({
    type: 'heading',
    attrs: { level: 2 },
    content: [{ type: 'text', text: 'Definition of Done' }]
  });
  sections.push({
    type: 'bulletList',
    content: content.definitionOfDone.map(item => ({
      type: 'listItem',
      content: [{ type: 'paragraph', content: [{ type: 'text', text: `[ ] ${item}` }] }]
    }))
  });

  // Technical Notes (if any)
  if (content.technicalNotes?.length > 0) {
    sections.push({
      type: 'heading',
      attrs: { level: 2 },
      content: [{ type: 'text', text: 'Technical Notes' }]
    });
    sections.push({
      type: 'bulletList',
      content: content.technicalNotes.map(note => ({
        type: 'listItem',
        content: [{ type: 'paragraph', content: [{ type: 'text', text: note }] }]
      }))
    });
  }

  return { type: 'doc', version: 1, content: sections };
}
```

---

## Phase 3: Workflow Transitions

### Get Available Transitions

```javascript
async function getTransitions(issueKey) {
  const response = await fetch(
    `${JIRA_BASE_URL}/rest/api/3/issue/${issueKey}/transitions`,
    { headers }
  );

  if (!response.ok) {
    throw new Error(`Failed to get transitions: ${response.status}`);
  }

  const data = await response.json();
  return data.transitions;
}
```

### Transition Issue to State

```javascript
async function transitionTo(issueKey, targetState) {
  // Get available transitions
  const transitions = await getTransitions(issueKey);

  // Find the transition to target state
  const transition = transitions.find(t =>
    t.to.name.toLowerCase() === targetState.toLowerCase() ||
    t.name.toLowerCase() === targetState.toLowerCase()
  );

  if (!transition) {
    console.log(`Available transitions for ${issueKey}:`);
    transitions.forEach(t => console.log(`  - ${t.name} → ${t.to.name}`));
    throw new Error(`No transition to "${targetState}" found`);
  }

  // Execute the transition
  const response = await fetch(
    `${JIRA_BASE_URL}/rest/api/3/issue/${issueKey}/transitions`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({ transition: { id: transition.id } })
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to transition: ${error}`);
  }

  console.log(`${issueKey} transitioned to ${targetState}`);
  return true;
}
```

### Common Workflow Operations

```javascript
// Start work on a story (To Do → Progressing)
async function startWork(issueKey) {
  await transitionTo(issueKey, 'Progressing');
  console.log(`Started: ${issueKey}`);
}

// Complete a story (Progressing → Done)
async function completeWork(issueKey) {
  await transitionTo(issueKey, 'Done');
  console.log(`Completed: ${issueKey}`);
}

// Move back to backlog (any state → To Do)
async function moveToBacklog(issueKey) {
  await transitionTo(issueKey, 'To Do');
  console.log(`Moved to backlog: ${issueKey}`);
}

// Reopen a completed issue (Done → To Do)
async function reopenWork(issueKey) {
  await transitionTo(issueKey, 'To Do');
  console.log(`Reopened: ${issueKey}`);
}
```

---

## Phase 4: Add Comments and Updates

### Add Work Log Comment

```javascript
async function addComment(issueKey, comment) {
  const body = {
    body: {
      type: 'doc',
      version: 1,
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: comment }]
        }
      ]
    }
  };

  const response = await fetch(
    `${JIRA_BASE_URL}/rest/api/3/issue/${issueKey}/comment`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to add comment: ${response.status}`);
  }

  console.log(`Comment added to ${issueKey}`);
  return response.json();
}
```

### Add Implementation Details Comment

```javascript
async function addImplementationDetails(issueKey, details) {
  const content = [
    { type: 'heading', attrs: { level: 3 }, content: [{ type: 'text', text: 'Implementation Details' }] },
    { type: 'paragraph', content: [{ type: 'text', text: `Completed: ${new Date().toISOString()}` }] }
  ];

  if (details.files?.length > 0) {
    content.push(
      { type: 'heading', attrs: { level: 4 }, content: [{ type: 'text', text: 'Files Modified' }] },
      {
        type: 'bulletList',
        content: details.files.map(f => ({
          type: 'listItem',
          content: [{ type: 'paragraph', content: [{ type: 'text', text: f }] }]
        }))
      }
    );
  }

  if (details.commits?.length > 0) {
    content.push(
      { type: 'heading', attrs: { level: 4 }, content: [{ type: 'text', text: 'Commits' }] },
      {
        type: 'bulletList',
        content: details.commits.map(c => ({
          type: 'listItem',
          content: [{ type: 'paragraph', content: [{ type: 'text', text: c }] }]
        }))
      }
    );
  }

  if (details.notes) {
    content.push(
      { type: 'heading', attrs: { level: 4 }, content: [{ type: 'text', text: 'Notes' }] },
      { type: 'paragraph', content: [{ type: 'text', text: details.notes }] }
    );
  }

  const body = { body: { type: 'doc', version: 1, content } };

  const response = await fetch(
    `${JIRA_BASE_URL}/rest/api/3/issue/${issueKey}/comment`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    }
  );

  return response.json();
}
```

---

## Complete Workflow Example

### Full Cycle: Propose → Approve → Create → Work → Complete

```javascript
async function fullWorkflowCycle(task) {
  // 1. Build proposal
  const proposal = buildStoryProposal(task);

  // 2. Present for approval (use AskUserQuestion tool)
  const approved = await presentForApproval(proposal);

  if (!approved) {
    console.log('Story creation skipped by user');
    return null;
  }

  // 3. Create in Jira
  const issue = await createStory(proposal, task.epicKey);
  console.log(`Created: ${issue.key}`);

  // 4. Start work (transition to In Progress)
  await startWork(issue.key);

  // 5. Do the actual work (your implementation here)
  const result = await doTheWork(task);

  // 6. Add implementation details
  await addImplementationDetails(issue.key, {
    files: result.modifiedFiles,
    commits: result.commits,
    notes: result.notes
  });

  // 7. Complete the work
  await completeWork(issue.key);

  return issue;
}
```

---

## Integration with Claude Code Orchestration

### Sync with TodoWrite

When working on Jira stories, sync with TodoWrite:

```markdown
TodoWrite todos:
[
  { "content": "SCRUM-55: Create signup API", "status": "in_progress", "activeForm": "Working on SCRUM-55" },
  { "content": "SCRUM-56: Create login API", "status": "pending", "activeForm": "Waiting for SCRUM-55" },
  { "content": "SCRUM-57: Create logout API", "status": "pending", "activeForm": "Waiting for SCRUM-56" }
]

As each task completes:
1. Mark TodoWrite item as completed
2. Transition Jira issue to Done
3. Add implementation comment to Jira
4. Move to next task
```

### Auto-Transition Pattern

```javascript
// When starting a task
async function startTask(issueKey) {
  // 1. Transition Jira to Progressing
  await startWork(issueKey);

  // 2. Update TodoWrite (in Claude Code)
  // TodoWrite: Mark as in_progress

  return issueKey;
}

// When completing a task
async function completeTask(issueKey, details) {
  // 1. Add implementation comment
  await addImplementationDetails(issueKey, details);

  // 2. Transition Jira to Done
  await completeWork(issueKey);

  // 3. Update TodoWrite (in Claude Code)
  // TodoWrite: Mark as completed

  return issueKey;
}
```

---

## Quick Reference

### Status Transitions (SCRUM Project - Next-Gen)

| From | To | Transition Name | Typical Use |
|------|-----|-----------------|-------------|
| To Do | Progressing | "Progressing" | Starting work |
| To Do | In Review | "In Review" | Needs review first |
| Progressing | Done | "Done" | Work complete |
| Progressing | To Do | "To Do" | Blocked/deprioritized |
| Done | To Do | "To Do" | Reopening |

**Available States:** To Do, In Review, Progressing, Out Review, Done

**Note:** Always query transitions first - they vary by issue type and current state.

### API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Create Issue | POST | `/rest/api/3/issue` |
| Get Issue | GET | `/rest/api/3/issue/{key}` |
| Update Issue | PUT | `/rest/api/3/issue/{key}` |
| Delete Issue | DELETE | `/rest/api/3/issue/{key}` |
| Get Transitions | GET | `/rest/api/3/issue/{key}/transitions` |
| Do Transition | POST | `/rest/api/3/issue/{key}/transitions` |
| Add Comment | POST | `/rest/api/3/issue/{key}/comment` |
| Search | GET | `/rest/api/3/search/jql?jql=...` |

### Rate Limiting

- Max 10 requests/second
- Add 100ms delay between bulk operations
- Batch operations where possible

---

## Error Handling

```javascript
async function safeJiraOperation(operation, issueKey) {
  try {
    return await operation();
  } catch (error) {
    console.error(`Jira operation failed for ${issueKey}: ${error.message}`);

    // Common error patterns
    if (error.message.includes('404')) {
      console.log('Issue not found - may have been deleted');
    }
    if (error.message.includes('401')) {
      console.log('Authentication failed - check API token');
    }
    if (error.message.includes('403')) {
      console.log('Permission denied - check project access');
    }
    if (error.message.includes('400')) {
      console.log('Bad request - check field names and values');
    }

    throw error;
  }
}
```

---

## Executable Scripts

Ready-to-run scripts are available in both Node.js and Python:

### Using the Cross-Platform Runner

```bash
# From the .claude/skills/jira directory
node scripts/run.js workflow demo SCRUM-100  # Demo full workflow
node scripts/run.js test                      # Test authentication

# Force specific runtime
node scripts/run.js --python workflow demo SCRUM-100
node scripts/run.js --node workflow demo SCRUM-100
```

### Direct Script Execution

```bash
# Node.js
node scripts/jira-workflow-demo.mjs demo SCRUM-100
node scripts/jira-workflow-demo.mjs start SCRUM-100
node scripts/jira-workflow-demo.mjs complete SCRUM-100
node scripts/jira-workflow-demo.mjs reopen SCRUM-100
node scripts/jira-workflow-demo.mjs status SCRUM-100

# Python (recommended on Windows)
python scripts/jira-workflow-demo.py demo SCRUM-100
python scripts/jira-workflow-demo.py start SCRUM-100
python scripts/jira-workflow-demo.py complete SCRUM-100
python scripts/jira-workflow-demo.py reopen SCRUM-100
python scripts/jira-workflow-demo.py status SCRUM-100
```

### Available Scripts

| Script | Node.js | Python | Purpose |
|--------|---------|--------|---------|
| Workflow Demo | `jira-workflow-demo.mjs` | `jira-workflow-demo.py` | Full To Do → Progressing → Done demo |
| Add Subtasks | `jira-add-subtasks.mjs` | `jira-add-subtasks.py` | Create subtasks under a story |
| Create Story | `jira-create-one.mjs` | `jira-create-one.py` | Create single story |
| Bulk Create | `jira-bulk-create.mjs` | `jira-bulk-create.py` | Create from git commits |

---

## References

- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
- [SAFe Framework](https://scaledagileframework.com/)
- [SAFe Story Format](https://scaledagileframework.com/story/)
