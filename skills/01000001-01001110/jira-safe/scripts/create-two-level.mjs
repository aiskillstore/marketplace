// Create Two-Level Hierarchy Epics and Stories
// Following jira-safe skill patterns for Next-Gen project
// Source: docs/epics/EPIC-001, EPIC-002, EPIC-003

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
  'Accept': 'application/json'
};

// ==================== SKILL PATTERNS ====================
// From .claude/skills/jira/jira-safe/SKILL.md

// ADF Helper (Atlassian Document Format)
function buildADF(content) {
  return { type: 'doc', version: 1, content };
}

function heading(level, text) {
  return {
    type: 'heading',
    attrs: { level },
    content: [{ type: 'text', text }]
  };
}

function paragraph(text) {
  return {
    type: 'paragraph',
    content: [{ type: 'text', text }]
  };
}

function bulletList(items) {
  return {
    type: 'bulletList',
    content: items.map(item => ({
      type: 'listItem',
      content: [{ type: 'paragraph', content: [{ type: 'text', text: item }] }]
    }))
  };
}

// Create Issue (from skill pattern)
async function createIssue(fields) {
  const response = await fetch(`${JIRA_BASE_URL}/rest/api/3/issue`, {
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

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ==================== EPIC & STORY DEFINITIONS ====================
// From docs/epics/EPIC-001-database-migration.md, EPIC-002-backend-api.md, EPIC-003-frontend-ui.md

const epics = [
  {
    id: 'EPIC-001',
    summary: 'EPIC-001: Database Migration - Two-Level Hierarchy',
    description: buildADF([
      heading(2, 'Business Outcome'),
      paragraph('Transform the current single-level database structure (users → brands) into a two-level hierarchy (users → clients → brands) to support agencies managing multiple client companies.'),
      heading(2, 'Success Criteria'),
      bulletList([
        'clients table created with proper schema',
        'brands.clientId column added and populated',
        '100% of existing brands mapped to clients',
        'All foreign key constraints enforced',
        'Zero data loss during migration'
      ]),
      heading(2, 'Dependencies'),
      paragraph('None - this is the foundational epic')
    ]),
    labels: ['two-level-hierarchy', 'database'],
    stories: [
      {
        id: 'US-001.1',
        summary: 'US-001.1: As a database administrator, I want to create a clients table, so that users can manage multiple client companies',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a database administrator, I want to create a new clients table with proper schema, indexes, and constraints, so that users can manage multiple client companies, each with their own brands.'),
          heading(2, 'Acceptance Criteria'),
          heading(3, 'Scenario: Table Creation'),
          bulletList([
            'GIVEN the database schema needs updating',
            'WHEN the migration runs',
            'THEN clients table exists with id, user_id, name, is_default, created_at, updated_at'
          ]),
          heading(2, 'Definition of Done'),
          bulletList([
            '[ ] Migration file created and tested',
            '[ ] Rollback SQL documented',
            '[ ] TypeScript types auto-generated',
            '[ ] PR merged to master'
          ])
        ]),
        labels: ['database', 'epic-001'],
        subtasks: [
          'Define clients table schema in Drizzle ORM',
          'Add user_id foreign key with CASCADE delete',
          'Create index on user_id for performance',
          'Add unique partial index for default client per user',
          'Generate migration file',
          'Create validation queries',
          'Test on Neon branch'
        ]
      },
      {
        id: 'US-001.2',
        summary: 'US-001.2: As a database administrator, I want to add clientId column to brands, so that brands are associated with clients',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a database administrator, I want to add a nullable client_id foreign key column to the brands table, so that each brand can be associated with a client company.'),
          heading(2, 'Acceptance Criteria'),
          bulletList([
            'GIVEN the brands table exists',
            'WHEN the migration runs',
            'THEN client_id column is added as nullable UUID'
          ]),
          heading(2, 'Definition of Done'),
          bulletList([
            '[ ] Column added as NULLABLE',
            '[ ] Index created on client_id',
            '[ ] FK references clients.id with CASCADE',
            '[ ] PR merged to master'
          ])
        ]),
        labels: ['database', 'epic-001'],
        subtasks: [
          'Add clientId field to brands schema',
          'Configure as nullable UUID',
          'Add foreign key reference to clients.id',
          'Set onDelete: cascade',
          'Create index on client_id',
          'Generate migration file',
          'Test on Neon branch'
        ]
      },
      {
        id: 'US-001.3',
        summary: 'US-001.3: As a database administrator, I want to migrate existing brands to clients, so that all data follows two-level hierarchy',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a database administrator, I want to create a client for each existing brand and link them, so that existing data is migrated to the new two-level hierarchy.'),
          heading(2, 'Acceptance Criteria'),
          bulletList([
            'GIVEN existing brands without clients',
            'WHEN migration runs',
            'THEN one client created per brand with matching user_id',
            'AND each brand.client_id points to its new client'
          ])
        ]),
        labels: ['database', 'epic-001'],
        subtasks: [
          'Create data migration script',
          'For each brand, create client with same user_id',
          'Update brand.client_id to new client.id',
          'Verify 0 brands with NULL client_id',
          'Verify brand_count = client_count'
        ]
      },
      {
        id: 'US-001.4',
        summary: 'US-001.4: As a database administrator, I want to enforce NOT NULL on clientId, so that data integrity is guaranteed',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a database administrator, I want to make client_id NOT NULL and add final constraints, so that data integrity is enforced at the database level.'),
          heading(2, 'Acceptance Criteria'),
          bulletList([
            'GIVEN all brands have client_id populated',
            'WHEN constraint added',
            'THEN client_id column is NOT NULL'
          ])
        ]),
        labels: ['database', 'epic-001'],
        subtasks: [
          'Verify 0 NULL client_id values',
          'Alter column to NOT NULL',
          'Add unique partial index for default brand per client',
          'Update drizzle schema',
          'Generate final migration'
        ]
      }
    ]
  },
  {
    id: 'EPIC-002',
    summary: 'EPIC-002: Backend API - Two-Level Hierarchy',
    description: buildADF([
      heading(2, 'Business Outcome'),
      paragraph('Implement comprehensive backend API support for the two-level hierarchy including client CRUD, updated brand APIs, limit enforcement, and ownership verification.'),
      heading(2, 'Success Criteria'),
      bulletList([
        'Client CRUD endpoints implemented (/api/clients/*)',
        'Brand API requires clientId parameter',
        'Two-level limit enforcement working',
        'All DELETE/PUT have ownership checks'
      ]),
      heading(2, 'Dependencies'),
      paragraph('EPIC-001 (Database Migration) must be complete')
    ]),
    labels: ['two-level-hierarchy', 'api'],
    stories: [
      {
        id: 'US-002.1',
        summary: 'US-002.1: As a frontend developer, I want client CRUD API endpoints, so that users can manage client companies',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a frontend developer, I want complete CRUD API endpoints for client management, so that users can create, read, update, and delete their client companies.'),
          heading(2, 'Endpoints'),
          bulletList([
            'GET /api/clients - List all clients',
            'POST /api/clients - Create with limit check',
            'GET /api/clients/[id] - Get single client',
            'PUT /api/clients/[id] - Update with ownership check',
            'DELETE /api/clients/[id] - Delete with cascade'
          ])
        ]),
        labels: ['api', 'epic-002'],
        subtasks: [
          'Create app/api/clients/route.ts (GET, POST)',
          'Implement GET - list clients for user',
          'Implement POST - create with limit check',
          'Create app/api/clients/[id]/route.ts',
          'Implement ownership verification helper',
          'Add Zod validation schemas',
          'Create unit tests'
        ]
      },
      {
        id: 'US-002.2',
        summary: 'US-002.2: As a frontend developer, I want brand API updated for client hierarchy, so that brands are scoped to clients',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a frontend developer, I want brand API updated to require clientId parameter, so that brands are properly scoped to client companies.'),
          heading(2, 'Changes'),
          bulletList([
            'POST /api/brands requires clientId',
            'GET /api/clients/[id]/brands returns brands for client',
            'PUT/DELETE have ownership verification'
          ])
        ]),
        labels: ['api', 'epic-002'],
        subtasks: [
          'Update POST /api/brands to require clientId',
          'Create GET /api/clients/[id]/brands endpoint',
          'Add ownership verification to DELETE',
          'Add ownership verification to PUT',
          'Add tests for cross-client access prevention'
        ]
      },
      {
        id: 'US-002.3',
        summary: 'US-002.3: As a billing system, I want two-level limit enforcement, so that subscription tiers are enforced',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a billing system, I want two-level limit enforcement, so that users cannot exceed their client or brand limits.'),
          heading(2, 'Limits by Tier'),
          bulletList([
            'Trial: 1 client, 2 brands per client',
            'Pro: 10 clients, 10 brands per client',
            'Unlimited: No limits'
          ])
        ]),
        labels: ['api', 'epic-002'],
        subtasks: [
          'Create lib/subscription/limits.ts',
          'Define limit constants by tier',
          'Implement getClientCount(userId)',
          'Implement getBrandCount(clientId)',
          'Add atomic limit checks'
        ]
      },
      {
        id: 'US-002.4',
        summary: 'US-002.4: As a security system, I want two-level ownership verification, so that users can only access their data',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a security system, I want two-level ownership verification on all endpoints, so that users cannot access other users data.'),
          heading(2, 'Requirements'),
          bulletList([
            'verifyClientOwnership(userId, clientId) helper',
            'verifyBrandOwnership(userId, brandId) helper',
            'Applied to all client and brand endpoints'
          ])
        ]),
        labels: ['api', 'security', 'epic-002'],
        subtasks: [
          'Create lib/auth/ownership.ts',
          'Implement verifyClientOwnership',
          'Implement verifyBrandOwnership',
          'Apply to all endpoints',
          'Create security test suite'
        ]
      },
      {
        id: 'US-002.5',
        summary: 'US-002.5: As an AI system, I want context builder updated, so that client info is included in AI prompts',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As an AI system, I want brand context builder to include client information, so that AI responses are aware of the client company context.')
        ]),
        labels: ['api', 'ai', 'epic-002'],
        subtasks: [
          'Update lib/ai/context-builder.ts',
          'Add client name to context',
          'Test context generation',
          'Verify backward compatibility'
        ]
      }
    ]
  },
  {
    id: 'EPIC-003',
    summary: 'EPIC-003: Frontend UI - Two-Level Hierarchy',
    description: buildADF([
      heading(2, 'Business Outcome'),
      paragraph('Implement complete frontend UI support for the two-level hierarchy including client management pages, two-level selector, updated onboarding, and subscription limit displays.'),
      heading(2, 'Success Criteria'),
      bulletList([
        'Client management page at /dashboard/clients',
        'Two-level selector in dashboard header',
        'Onboarding Step 0 creates client',
        'Responsive design (mobile/tablet/desktop)'
      ]),
      heading(2, 'Dependencies'),
      paragraph('EPIC-002 (Backend API) must be complete')
    ]),
    labels: ['two-level-hierarchy', 'frontend'],
    stories: [
      {
        id: 'US-003.1',
        summary: 'US-003.1: As a user, I want a client management page, so that I can create and manage client companies',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a user, I want to manage my client companies from a dedicated page, so that I can create, view, edit, and delete clients easily.'),
          heading(2, 'Features'),
          bulletList([
            'Page at /dashboard/clients',
            'List all clients in card format',
            'Show brand count per client',
            'Create/Edit/Delete functionality'
          ])
        ]),
        labels: ['frontend', 'epic-003'],
        subtasks: [
          'Create app/dashboard/clients/page.tsx',
          'Add to dashboard navigation',
          'Implement client list component',
          'Create New Client modal',
          'Add delete confirmation dialog',
          'Handle loading/error/empty states'
        ]
      },
      {
        id: 'US-003.2',
        summary: 'US-003.2: As a user, I want a two-level selector, so that I can switch between clients and brands',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a user, I want to use a two-level selector to switch clients and brands, so that I can quickly navigate between different client companies.'),
          heading(2, 'Features'),
          bulletList([
            'Client dropdown (top level)',
            'Brand dropdown (filtered by client)',
            'Selection persists across navigation'
          ])
        ]),
        labels: ['frontend', 'epic-003'],
        subtasks: [
          'Create client-brand-selector.tsx',
          'Implement client dropdown',
          'Implement brand dropdown filtered by client',
          'Persist selection to localStorage',
          'Sync with URL params'
        ]
      },
      {
        id: 'US-003.3',
        summary: 'US-003.3: As a new user, I want onboarding to create a client first, so that brands are properly organized',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a new user, I want to create a client company during onboarding, so that my first brand is properly associated with a client.'),
          heading(2, 'Flow'),
          bulletList([
            'Step 0: What is your company name? (creates client)',
            'Steps 1-6: Existing brand questionnaire'
          ])
        ]),
        labels: ['frontend', 'epic-003'],
        subtasks: [
          'Add Step 0 to onboarding flow',
          'Create client name input form',
          'Call POST /api/clients on Step 0',
          'Pass clientId to brand creation'
        ]
      },
      {
        id: 'US-003.4',
        summary: 'US-003.4: As a user, I want a client profile page, so that I can view and edit client details',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a user, I want to view and edit client details on a dedicated page.')
        ]),
        labels: ['frontend', 'epic-003'],
        subtasks: [
          'Create app/dashboard/clients/[id]/page.tsx',
          'Display client details',
          'Add edit functionality',
          'Show brands list'
        ]
      },
      {
        id: 'US-003.5',
        summary: 'US-003.5: As a user, I want brand management scoped to client, so that brands are organized by client',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a user, I want to see brands filtered by selected client, so that I only see relevant brands.')
        ]),
        labels: ['frontend', 'epic-003'],
        subtasks: [
          'Update brands page to filter by client',
          'Pass clientId to brand creation',
          'Show default brand badge per client'
        ]
      },
      {
        id: 'US-003.6',
        summary: 'US-003.6: As a user, I want to see subscription limits, so that I know when to upgrade',
        description: buildADF([
          heading(2, 'User Story'),
          paragraph('As a user, I want to see my current usage vs subscription limits, so that I know when I am approaching limits.')
        ]),
        labels: ['frontend', 'epic-003'],
        subtasks: [
          'Create usage-display.tsx component',
          'Show client count vs limit',
          'Show brand count vs limit',
          'Add Upgrade prompt'
        ]
      }
    ]
  }
];

// ==================== MAIN ====================

async function main() {
  console.log('========================================');
  console.log('  CREATE TWO-LEVEL HIERARCHY BACKLOG');
  console.log('  Following jira-safe skill patterns');
  console.log('========================================\n');

  const results = {
    epics: { created: 0, failed: 0, keys: [] },
    stories: { created: 0, failed: 0, keys: [] },
    subtasks: { created: 0, failed: 0 }
  };

  for (const epic of epics) {
    console.log(`\n--- ${epic.id} ---`);

    // Create Epic (Next-Gen: no customfield_10011)
    try {
      const epicIssue = await createIssue({
        project: { key: PROJECT_KEY },
        issuetype: { name: 'Epic' },
        summary: epic.summary,
        description: epic.description,
        labels: epic.labels
      });
      console.log(`+ Epic: ${epicIssue.key}`);
      results.epics.created++;
      results.epics.keys.push({ key: epicIssue.key, id: epic.id });

      await delay(150);

      // Create Stories under Epic (Next-Gen: use parent field)
      for (const story of epic.stories) {
        try {
          const storyIssue = await createIssue({
            project: { key: PROJECT_KEY },
            issuetype: { name: 'Story' },
            summary: story.summary,
            description: story.description,
            parent: { key: epicIssue.key },  // Next-Gen pattern from skill
            labels: story.labels
          });
          console.log(`  + Story: ${storyIssue.key} (${story.id})`);
          results.stories.created++;
          results.stories.keys.push({ key: storyIssue.key, id: story.id, epicKey: epicIssue.key });

          await delay(100);

          // Create Subtasks (Next-Gen: use 'Subtask' not 'Sub-task')
          if (story.subtasks && story.subtasks.length > 0) {
            for (const subtaskSummary of story.subtasks) {
              try {
                const subtaskIssue = await createIssue({
                  project: { key: PROJECT_KEY },
                  issuetype: { name: 'Subtask' },  // Next-Gen pattern from skill
                  summary: subtaskSummary,
                  parent: { key: storyIssue.key }
                });
                console.log(`    + Subtask: ${subtaskIssue.key}`);
                results.subtasks.created++;
              } catch (err) {
                console.log(`    - FAILED: ${err.message.substring(0, 50)}`);
                results.subtasks.failed++;
              }
              await delay(50);
            }
          }

        } catch (err) {
          console.log(`  - FAILED ${story.id}: ${err.message.substring(0, 80)}`);
          results.stories.failed++;
        }
      }

    } catch (err) {
      console.log(`- FAILED ${epic.id}: ${err.message.substring(0, 80)}`);
      results.epics.failed++;
    }
  }

  console.log('\n========================================');
  console.log('  SUMMARY');
  console.log('========================================');
  console.log(`Epics:    ${results.epics.created} created, ${results.epics.failed} failed`);
  console.log(`Stories:  ${results.stories.created} created, ${results.stories.failed} failed`);
  console.log(`Subtasks: ${results.subtasks.created} created, ${results.subtasks.failed} failed`);

  console.log('\n--- Created Issues ---');
  for (const epic of results.epics.keys) {
    console.log(`${epic.key}: ${epic.id}`);
    for (const story of results.stories.keys.filter(s => s.epicKey === epic.key)) {
      console.log(`  └─ ${story.key}: ${story.id}`);
    }
  }

  console.log(`\n========================================`);
  console.log(`View: ${JIRA_BASE_URL}/jira/software/projects/${PROJECT_KEY}/boards/1/backlog`);
  console.log('========================================');
}

main().catch(console.error);
