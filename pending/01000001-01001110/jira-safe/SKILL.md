---
name: jira-safe
description: Implement SAFe methodology in Jira. Use when creating Epics, Features, Stories with proper hierarchy, acceptance criteria, and parent-child linking.
---

# Jira SAFe (Scaled Agile Framework) Skill

> Implements SAFe methodology for Epic, Feature, Story, and Task management in Jira Cloud.

## When to Use

- Creating Epics with business outcomes and acceptance criteria
- Writing user stories in SAFe format ("As a... I want... So that...")
- Breaking down Features into Stories with acceptance criteria
- Creating Subtasks under Stories
- Linking work items in proper hierarchy (Epic → Feature → Story → Subtask)

## CRITICAL: Next-Gen vs Classic Projects

**SCRUM project is Next-Gen (Team-managed)**. Key differences:

| Aspect | Classic (Company-managed) | Next-Gen (Team-managed) |
|--------|---------------------------|-------------------------|
| Epic Link | `customfield_10014` | `parent: { key: 'EPIC-KEY' }` |
| Epic Name | `customfield_10011` | Not available |
| Subtask Type | `'Sub-task'` | `'Subtask'` |
| Project Style | `classic` | `next-gen`, `simplified: true` |

**Always detect project type first:**
```javascript
const projectInfo = await fetch(`${JIRA_URL}/rest/api/3/project/${PROJECT_KEY}`, { headers });
const project = await projectInfo.json();
const isNextGen = project.style === 'next-gen' || project.simplified === true;
```

## SAFe Hierarchy in Jira

```
Portfolio Level:
└── Epic (Strategic Initiative)
    └── Feature (Benefit Hypothesis)
        └── Story (User Value)
            └── Subtask (Technical Work)
```

## SAFe Templates

### Epic Template (Next-Gen)

```javascript
// NOTE: Next-Gen projects do NOT use customfield_10011 (Epic Name)
const epic = {
  fields: {
    project: { key: 'PROJECT_KEY' },
    issuetype: { name: 'Epic' },
    summary: '[Epic ID]: [Epic Name] - [Business Outcome]',
    description: {
      type: 'doc',
      version: 1,
      content: [
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'Business Outcome' }]
        },
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Describe the measurable business value...' }]
        },
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'Success Metrics' }]
        },
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Metric 1: [measurable target]' }] }]
            }
          ]
        },
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'Scope' }]
        },
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'What is in scope and out of scope...' }]
        }
      ]
    },
    labels: ['epic-label']  // Use labels instead of Epic Name for categorization
  }
};
```

### Story Template (SAFe Format, Next-Gen)

```javascript
// NOTE: Next-Gen uses 'parent' field, NOT customfield_10014
const story = {
  fields: {
    project: { key: 'PROJECT_KEY' },
    issuetype: { name: 'Story' },
    summary: '[US-ID]: As a [persona], I want [goal], so that [benefit]',
    description: {
      type: 'doc',
      version: 1,
      content: [
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'User Story' }]
        },
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'As a ', marks: [{ type: 'strong' }] },
            { type: 'text', text: '[persona]' },
            { type: 'text', text: ', I want ', marks: [{ type: 'strong' }] },
            { type: 'text', text: '[goal]' },
            { type: 'text', text: ', so that ', marks: [{ type: 'strong' }] },
            { type: 'text', text: '[benefit]' }
          ]
        },
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'Acceptance Criteria' }]
        },
        {
          type: 'heading',
          attrs: { level: 3 },
          content: [{ type: 'text', text: 'Scenario 1: [Name]' }]
        },
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: 'GIVEN [precondition]', marks: [{ type: 'strong' }] }] }]
            },
            {
              type: 'listItem',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: 'WHEN [action]', marks: [{ type: 'strong' }] }] }]
            },
            {
              type: 'listItem',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: 'THEN [expected result]', marks: [{ type: 'strong' }] }] }]
            }
          ]
        },
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'Definition of Done' }]
        },
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: '[ ] Code reviewed and approved' }] }]
            },
            {
              type: 'listItem',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: '[ ] Unit tests written and passing' }] }]
            },
            {
              type: 'listItem',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: '[ ] Integration tests passing' }] }]
            },
            {
              type: 'listItem',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: '[ ] Documentation updated' }] }]
            }
          ]
        }
      ]
    },
    // Next-Gen: Link to parent Epic using 'parent' field
    parent: { key: 'EPIC_KEY' },
    labels: ['category-label', 'epic-id']
  }
};
```

### Subtask Template (Next-Gen)

```javascript
// NOTE: Next-Gen uses 'Subtask' (no hyphen), NOT 'Sub-task'
const subtask = {
  fields: {
    project: { key: 'PROJECT_KEY' },
    issuetype: { name: 'Subtask' },  // Next-Gen: 'Subtask', Classic: 'Sub-task'
    summary: '[Technical task description]',
    // Parent Story (required for subtasks)
    parent: { key: 'STORY_KEY' }
    // Note: Description is optional for subtasks
  }
};
```

## API Implementation (Next-Gen Projects)

### Create Epic with Stories (Next-Gen)

```javascript
async function createEpicWithStories(epicFields, storyDefinitions) {
  const headers = {
    'Authorization': `Basic ${Buffer.from(`${EMAIL}:${TOKEN}`).toString('base64')}`,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  // 1. Create Epic
  const epicResponse = await fetch(`${JIRA_URL}/rest/api/3/issue`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ fields: epicFields })
  });

  if (!epicResponse.ok) {
    const error = await epicResponse.text();
    throw new Error(`Epic creation failed: ${error}`);
  }

  const createdEpic = await epicResponse.json();
  console.log(`Created Epic: ${createdEpic.key}`);

  // 2. Create Stories linked to Epic using 'parent' field (Next-Gen)
  const createdStories = [];
  for (const storyDef of storyDefinitions) {
    const storyFields = {
      ...storyDef,
      parent: { key: createdEpic.key }  // Next-Gen: use 'parent', NOT customfield_10014
    };

    const storyResponse = await fetch(`${JIRA_URL}/rest/api/3/issue`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ fields: storyFields })
    });

    if (!storyResponse.ok) {
      const error = await storyResponse.text();
      console.error(`Story creation failed: ${error}`);
      continue;
    }

    const createdStory = await storyResponse.json();
    createdStories.push(createdStory);
    console.log(`  Created Story: ${createdStory.key}`);

    // Rate limiting
    await new Promise(r => setTimeout(r, 100));
  }

  return { epic: createdEpic, stories: createdStories };
}
```

### Create Story with Subtasks (Next-Gen)

```javascript
async function createStoryWithSubtasks(storyFields, epicKey, subtaskSummaries) {
  const headers = {
    'Authorization': `Basic ${Buffer.from(`${EMAIL}:${TOKEN}`).toString('base64')}`,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  // 1. Create Story under Epic
  const storyRequest = {
    fields: {
      ...storyFields,
      parent: { key: epicKey }  // Link to Epic
    }
  };

  const storyResponse = await fetch(`${JIRA_URL}/rest/api/3/issue`, {
    method: 'POST',
    headers,
    body: JSON.stringify(storyRequest)
  });

  if (!storyResponse.ok) {
    throw new Error(`Story creation failed: ${await storyResponse.text()}`);
  }

  const createdStory = await storyResponse.json();

  // 2. Create Subtasks under Story
  const createdSubtasks = [];
  for (const summary of subtaskSummaries) {
    const subtaskResponse = await fetch(`${JIRA_URL}/rest/api/3/issue`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        fields: {
          project: { key: storyFields.project.key },
          issuetype: { name: 'Subtask' },  // Next-Gen: 'Subtask', NOT 'Sub-task'
          summary: summary,
          parent: { key: createdStory.key }
        }
      })
    });

    if (subtaskResponse.ok) {
      createdSubtasks.push(await subtaskResponse.json());
    }

    await new Promise(r => setTimeout(r, 50));  // Rate limiting
  }

  return { story: createdStory, subtasks: createdSubtasks };
}
```

### Get Epic Link Field ID

Epic link field varies by Jira instance. Find it:

```javascript
async function findEpicLinkField() {
  const response = await fetch(`${JIRA_URL}/rest/api/3/field`, { headers });
  const fields = await response.json();

  const epicLinkField = fields.find(f =>
    f.name === 'Epic Link' ||
    f.name.toLowerCase().includes('epic link')
  );

  return epicLinkField?.id; // Usually customfield_10014
}
```

### Bulk Delete Issues

```javascript
async function bulkDeleteIssues(projectKey, maxResults = 100) {
  // Search for all issues
  const jql = encodeURIComponent(`project = ${projectKey} ORDER BY key ASC`);
  const searchResponse = await fetch(
    `${JIRA_URL}/rest/api/3/search/jql?jql=${jql}&maxResults=${maxResults}&fields=key`,
    { headers }
  );
  const { issues } = await searchResponse.json();

  // Delete each issue
  for (const issue of issues) {
    await fetch(`${JIRA_URL}/rest/api/3/issue/${issue.key}?deleteSubtasks=true`, {
      method: 'DELETE',
      headers
    });
    console.log(`Deleted: ${issue.key}`);
    await new Promise(r => setTimeout(r, 100)); // Rate limit
  }

  return issues.length;
}
```

## SAFe Best Practices

### Epic Naming
- Format: `[Domain] - [Business Outcome]`
- Example: `Marketing Copilot - Enable 24/7 Brand-Aware Content Generation`

### Story Naming (INVEST Criteria)
- **I**ndependent: Can be developed separately
- **N**egotiable: Details can be discussed
- **V**aluable: Delivers user value
- **E**stimable: Can be sized
- **S**mall: Fits in a sprint
- **T**estable: Has clear acceptance criteria

### Story Format
```
As a [specific persona],
I want [concrete action/capability],
So that [measurable benefit].
```

### Acceptance Criteria (Given-When-Then)
```
Scenario: [Descriptive name]
GIVEN [initial context/precondition]
WHEN [action/event occurs]
THEN [expected outcome]
AND [additional outcome if needed]
```

## Issue Link Types (Next-Gen)

| Link Type | Use Case | Field |
|-----------|----------|-------|
| Parent (Next-Gen) | Story → Epic | `parent: { key: 'EPIC-KEY' }` |
| Parent (Next-Gen) | Subtask → Story | `parent: { key: 'STORY-KEY' }` |
| Blocks/Is blocked by | Dependencies | Link type |
| Relates to | Related items | Link type |

**Classic Projects Only:**
| Link Type | Use Case | Field |
|-----------|----------|-------|
| Epic Link | Story → Epic | `customfield_10014` |
| Epic Name | Epic short name | `customfield_10011` |

## Custom Fields by Project Type

### Next-Gen (Team-managed) - SCRUM Project
| Purpose | Method |
|---------|--------|
| Link Story to Epic | `parent: { key: 'EPIC-KEY' }` |
| Link Subtask to Story | `parent: { key: 'STORY-KEY' }` |
| Subtask issue type | `issuetype: { name: 'Subtask' }` |

### Classic (Company-managed)
| Field | ID (typical) | Purpose |
|-------|--------------|---------|
| Epic Link | customfield_10014 | Links Story to Epic |
| Epic Name | customfield_10011 | Short name for Epic |
| Story Points | customfield_10016 | Estimation |
| Sprint | customfield_10007 | Sprint assignment |

## Error Handling

```javascript
async function safeJiraRequest(url, options = {}) {
  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Jira API ${response.status}: ${error.substring(0, 200)}`);
  }

  if (response.status === 204) return null;
  return response.json();
}
```

## References

- [SAFe Framework](https://scaledagileframework.com/)
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
