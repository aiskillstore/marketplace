// Create MVP Epic and Stories using SAFe methodology
// Based on Tustle Marketing Copilot PRD

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

// ====================
// HELPER FUNCTIONS
// ====================

async function jiraRequest(path, options = {}) {
  const url = `${JIRA_BASE_URL}/rest/api/3${path}`;
  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`${response.status}: ${error.substring(0, 300)}`);
  }

  if (response.status === 204) return null;
  return response.json();
}

// Build Atlassian Document Format (ADF) from plain text with sections
function buildADF(sections) {
  const content = [];

  for (const section of sections) {
    if (section.heading) {
      content.push({
        type: 'heading',
        attrs: { level: section.level || 2 },
        content: [{ type: 'text', text: section.heading }]
      });
    }

    if (section.paragraph) {
      content.push({
        type: 'paragraph',
        content: [{ type: 'text', text: section.paragraph }]
      });
    }

    if (section.bullets) {
      content.push({
        type: 'bulletList',
        content: section.bullets.map(bullet => ({
          type: 'listItem',
          content: [{ type: 'paragraph', content: [{ type: 'text', text: bullet }] }]
        }))
      });
    }
  }

  return { type: 'doc', version: 1, content };
}

async function createIssue(fields) {
  return jiraRequest('/issue', {
    method: 'POST',
    body: JSON.stringify({ fields })
  });
}

// ====================
// MVP EPIC DEFINITION
// ====================

const mvpEpic = {
  project: { key: PROJECT_KEY },
  issuetype: { name: 'Epic' },
  summary: 'Tustle MVP - 24/7 Marketing Copilot with Brand Memory',
  // Note: Epic Name field (customfield_10011) not available in this project
  description: buildADF([
    { heading: 'Business Outcome' },
    { paragraph: 'Launch a ChatGPT-style marketing assistant that remembers brand voice, maintains conversation history, and generates on-brand content instantly. Enable small businesses and solo marketers to produce professional marketing content 24/7 without expensive agencies.' },
    { heading: 'Success Metrics' },
    { bullets: [
      'User Acquisition: 1,000 registered users in first 90 days',
      'Conversion: 5% trial-to-paid conversion rate',
      'Engagement: Average 3+ chat sessions per user per week',
      'Retention: 60% month-over-month user retention',
      'Revenue: $5,000 MRR by end of Q1'
    ]},
    { heading: 'Scope' },
    { paragraph: 'IN SCOPE: Authentication, brand questionnaire, AI chat with brand context, thread management, subscription billing (Stripe), usage limits, landing page, basic analytics.' },
    { paragraph: 'OUT OF SCOPE: Team collaboration, search/export, message regeneration, templates library, third-party integrations, mobile app.' },
    { heading: 'Target Users' },
    { bullets: [
      'Solo Marketing Manager: 1-person marketing team needing to maintain brand voice across channels',
      'Small Business Owner: Time-poor entrepreneurs who need marketing help',
      'Freelance Marketer: Consultants managing multiple client brands'
    ]},
    { heading: 'Tech Stack' },
    { bullets: [
      'Frontend: Next.js 14 (App Router), React 19, Tailwind CSS v4',
      'Backend: Next.js API Routes, Edge Runtime',
      'Database: PostgreSQL (Neon) with Drizzle ORM',
      'AI: OpenAI GPT-5-nano-2025-08-07',
      'Payments: Stripe (subscriptions)',
      'Hosting: Vercel, Cloudflare (DNS/WAF)'
    ]}
  ])
};

// ====================
// USER STORIES (SAFe Format)
// ====================

const stories = [
  // ==================== AUTHENTICATION ====================
  {
    category: 'Authentication',
    summary: 'As a new user, I want to create an account with email and password, so that I can access the marketing copilot',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a new user, I want to create an account with email and password, so that I can access the marketing copilot and start generating content.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Successful Registration', level: 3 },
      { bullets: [
        'GIVEN I am on the signup page',
        'WHEN I enter a valid email, password (8+ chars, 1 uppercase, 1 number), and accept terms',
        'THEN my account is created, I am logged in, and redirected to onboarding'
      ]},
      { heading: 'Scenario 2: Duplicate Email', level: 3 },
      { bullets: [
        'GIVEN an account with my email already exists',
        'WHEN I try to register with the same email',
        'THEN I see an error "Email already registered" with login link'
      ]},
      { heading: 'Scenario 3: Invalid Password', level: 3 },
      { bullets: [
        'GIVEN I am on the signup page',
        'WHEN I enter a password that does not meet requirements',
        'THEN I see specific validation errors (min length, uppercase, number)'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Signup API endpoint (/api/auth/signup) implemented',
        '[ ] Password hashed with bcrypt (cost factor 12)',
        '[ ] JWT token generated and set in HTTP-only cookie',
        '[ ] Email validation with proper error messages',
        '[ ] Unit tests for signup flow',
        '[ ] Integration tests with database'
      ]}
    ]),
    subtasks: [
      'Create signup API route (/api/auth/signup)',
      'Implement password hashing with bcrypt',
      'Create JWT token generation utility',
      'Build signup form component with validation',
      'Add error handling and user feedback',
      'Write unit tests for signup'
    ]
  },
  {
    category: 'Authentication',
    summary: 'As a returning user, I want to log in with my credentials, so that I can access my saved brands and conversations',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a returning user, I want to log in with my email and password, so that I can access my saved brands, conversation history, and continue where I left off.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Successful Login', level: 3 },
      { bullets: [
        'GIVEN I have an existing account',
        'WHEN I enter correct email and password',
        'THEN I am logged in and redirected to dashboard/chat'
      ]},
      { heading: 'Scenario 2: Invalid Credentials', level: 3 },
      { bullets: [
        'GIVEN I am on the login page',
        'WHEN I enter incorrect email or password',
        'THEN I see "Invalid email or password" (no specific field indication for security)'
      ]},
      { heading: 'Scenario 3: Rate Limiting', level: 3 },
      { bullets: [
        'GIVEN I have failed login 10 times in an hour',
        'WHEN I try to login again',
        'THEN I am temporarily blocked with countdown timer'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Login API endpoint (/api/auth/login) implemented',
        '[ ] Password verification with bcrypt',
        '[ ] JWT refresh token logic',
        '[ ] Rate limiting (10 attempts/hour/email)',
        '[ ] Remember me functionality (30-day vs 7-day token)',
        '[ ] Unit and integration tests'
      ]}
    ]),
    subtasks: [
      'Create login API route (/api/auth/login)',
      'Implement password verification',
      'Add rate limiting middleware',
      'Build login form component',
      'Implement "Remember me" functionality',
      'Write tests for login flow'
    ]
  },
  {
    category: 'Authentication',
    summary: 'As a user, I want to log out and have my session terminated, so that my account remains secure on shared devices',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a user, I want to log out from my account, so that my session is terminated and my account is protected on shared or public devices.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Successful Logout', level: 3 },
      { bullets: [
        'GIVEN I am logged in',
        'WHEN I click the logout button',
        'THEN my session cookie is cleared and I am redirected to login page'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Logout API endpoint (/api/auth/logout) implemented',
        '[ ] Cookie properly cleared',
        '[ ] Client-side state reset',
        '[ ] Redirect to login page'
      ]}
    ]),
    subtasks: []
  },

  // ==================== BRAND ONBOARDING ====================
  {
    category: 'Brand Onboarding',
    summary: 'As a new user, I want to complete a brand questionnaire, so that the AI understands my brand voice and can generate on-brand content',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a new user, I want to complete a guided brand questionnaire during onboarding, so that the AI understands my brand voice, messaging rules, and can generate content that sounds like me.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Complete Questionnaire', level: 3 },
      { bullets: [
        'GIVEN I am a new user after signup',
        'WHEN I complete all 6 steps of the questionnaire',
        'THEN my brand profile is saved and I can start chatting'
      ]},
      { heading: 'Scenario 2: Save Progress', level: 3 },
      { bullets: [
        'GIVEN I am on step 3 of questionnaire',
        'WHEN I close the browser and return later',
        'THEN I can continue from step 3 (draft saved)'
      ]},
      { heading: 'Questionnaire Steps' },
      { bullets: [
        'Step 1: Company Basics (name, industry, tagline, website)',
        'Step 2: Target Audience (demographics, pain points, goals)',
        'Step 3: Brand Voice (personality sliders, tone descriptors)',
        'Step 4: Messaging Rules (banned phrases, required phrases)',
        'Step 5: Products/Services (offerings, key benefits)',
        'Step 6: Channels & Formatting (platforms, content types)'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] 6-step questionnaire UI implemented',
        '[ ] Brand profile stored in database',
        '[ ] Progress saved between sessions',
        '[ ] Validation on each step',
        '[ ] Skip option for optional fields',
        '[ ] Review & edit before submit'
      ]}
    ]),
    subtasks: [
      'Create brand questionnaire page layout',
      'Build Step 1: Company Basics component',
      'Build Step 2: Target Audience component',
      'Build Step 3: Brand Voice sliders component',
      'Build Step 4: Messaging Rules component',
      'Build Step 5: Products/Services component',
      'Build Step 6: Channels component',
      'Create API routes for brand profile CRUD',
      'Implement progress persistence',
      'Add validation schemas with Zod'
    ]
  },
  {
    category: 'Brand Onboarding',
    summary: 'As a user, I want to edit my brand profile at any time, so that I can update it as my brand evolves',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a user, I want to edit my brand profile at any time from settings, so that I can update my brand voice, messaging rules, and other details as my brand evolves.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Edit Brand Profile', level: 3 },
      { bullets: [
        'GIVEN I have a saved brand profile',
        'WHEN I go to brand settings and make changes',
        'THEN my profile is updated and AI uses new context'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Brand settings page accessible from dashboard',
        '[ ] All questionnaire fields editable',
        '[ ] Changes reflected in AI context immediately',
        '[ ] Change history audit log'
      ]}
    ]),
    subtasks: [
      'Create brand settings page',
      'Implement edit mode for questionnaire',
      'Add save/cancel functionality',
      'Update AI context builder to use latest profile'
    ]
  },

  // ==================== AI CHAT ====================
  {
    category: 'AI Chat',
    summary: 'As a user, I want to chat with an AI that understands my brand, so that I can generate on-brand marketing content',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a user, I want to chat with an AI assistant that has full context of my brand voice, messaging rules, and products, so that every response is on-brand and ready to use.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Start New Chat', level: 3 },
      { bullets: [
        'GIVEN I have a brand profile saved',
        'WHEN I start a new chat and send a message',
        'THEN AI responds using my brand voice with streaming tokens'
      ]},
      { heading: 'Scenario 2: Brand Context Applied', level: 3 },
      { bullets: [
        'GIVEN my brand has specific tone and banned phrases',
        'WHEN I ask AI to write content',
        'THEN response matches my brand tone and avoids banned phrases'
      ]},
      { heading: 'Technical Requirements' },
      { bullets: [
        'Edge Runtime for SSE streaming',
        'OpenAI GPT-5-nano model',
        'Brand context in system prompt',
        'Last 20 messages as conversation history',
        'Token-by-token streaming display'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Chat API route with SSE streaming (/api/chat)',
        '[ ] Brand context builder utility',
        '[ ] Chat UI with message bubbles',
        '[ ] Streaming token display',
        '[ ] Error handling for API failures',
        '[ ] Loading states and indicators'
      ]}
    ]),
    subtasks: [
      'Create chat API route with Edge Runtime',
      'Build brand context builder (lib/ai/context-builder.ts)',
      'Implement OpenAI streaming integration',
      'Build chat UI component',
      'Add message bubble components',
      'Implement streaming token display',
      'Add typing indicator',
      'Handle error states'
    ]
  },
  {
    category: 'AI Chat',
    summary: 'As a user, I want my chat messages saved to threads, so that I can find and continue past conversations',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a user, I want my chat messages automatically saved to threads, so that I can find past conversations, continue where I left off, and reference previous content.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Auto-save Messages', level: 3 },
      { bullets: [
        'GIVEN I am chatting with the AI',
        'WHEN I send a message and receive a response',
        'THEN both messages are saved to the current thread'
      ]},
      { heading: 'Scenario 2: Load Thread History', level: 3 },
      { bullets: [
        'GIVEN I have previous threads',
        'WHEN I click on a thread in the sidebar',
        'THEN all messages from that thread are loaded'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Messages saved to database after each exchange',
        '[ ] Thread sidebar showing all threads',
        '[ ] Click to load thread history',
        '[ ] Thread title auto-generated from first message',
        '[ ] Threads sorted by last activity'
      ]}
    ]),
    subtasks: [
      'Create threads table and API routes',
      'Create messages table and API routes',
      'Build thread sidebar component',
      'Implement thread loading on click',
      'Add auto-title generation for threads',
      'Sort threads by last activity'
    ]
  },

  // ==================== THREAD MANAGEMENT ====================
  {
    category: 'Thread Management',
    summary: 'As a user, I want to create, rename, and delete conversation threads, so that I can organize my marketing work',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a user, I want to create new threads, rename existing ones, and delete threads I no longer need, so that I can keep my marketing work organized.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Create New Thread', level: 3 },
      { bullets: [
        'GIVEN I am on the chat page',
        'WHEN I click "New Thread" button',
        'THEN a new empty thread is created and selected'
      ]},
      { heading: 'Scenario 2: Rename Thread', level: 3 },
      { bullets: [
        'GIVEN I have an existing thread',
        'WHEN I click edit on thread name',
        'THEN I can enter a new name and save it'
      ]},
      { heading: 'Scenario 3: Delete Thread', level: 3 },
      { bullets: [
        'GIVEN I have a thread with messages',
        'WHEN I click delete and confirm',
        'THEN the thread and all messages are permanently deleted'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] New thread creation API and UI',
        '[ ] Thread rename functionality',
        '[ ] Thread delete with confirmation modal',
        '[ ] Cascade delete of messages'
      ]}
    ]),
    subtasks: [
      'Create new thread API endpoint',
      'Add "New Thread" button to sidebar',
      'Implement thread rename inline edit',
      'Create delete confirmation modal',
      'Implement cascade delete for messages'
    ]
  },

  // ==================== SUBSCRIPTION & BILLING ====================
  {
    category: 'Billing',
    summary: 'As a trial user, I want to upgrade to a paid plan, so that I can get more messages and features',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a trial user who has found value in the product, I want to upgrade to a paid subscription plan, so that I can get more messages per month and additional features.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: View Plans', level: 3 },
      { bullets: [
        'GIVEN I am a trial user',
        'WHEN I click "Upgrade" or visit billing page',
        'THEN I see Pro ($9.99/mo, 100 msg) and Unlimited ($39.99/mo) plans'
      ]},
      { heading: 'Scenario 2: Checkout Flow', level: 3 },
      { bullets: [
        'GIVEN I am viewing plans',
        'WHEN I click "Subscribe" on a plan',
        'THEN I am redirected to Stripe Checkout'
      ]},
      { heading: 'Scenario 3: Successful Payment', level: 3 },
      { bullets: [
        'GIVEN I complete Stripe checkout',
        'WHEN payment succeeds',
        'THEN my plan is upgraded and I return to dashboard with confirmation'
      ]},
      { heading: 'Subscription Tiers' },
      { bullets: [
        'Trial: $0, 50 messages lifetime, 1 brand',
        'Pro: $9.99/month, 100 messages/month, 10 brands',
        'Unlimited: $39.99/month, unlimited messages, unlimited brands'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Stripe Checkout integration',
        '[ ] Billing page with plan comparison',
        '[ ] Webhook handler for checkout.session.completed',
        '[ ] Subscription status stored in database',
        '[ ] Plan upgrade reflected in UI immediately'
      ]}
    ]),
    subtasks: [
      'Create billing page with plan cards',
      'Integrate Stripe Checkout',
      'Create checkout API route',
      'Implement Stripe webhooks handler',
      'Store subscription in database',
      'Add upgrade confirmation UI'
    ]
  },
  {
    category: 'Billing',
    summary: 'As a paid user, I want to manage my subscription, so that I can upgrade, downgrade, or cancel as needed',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a paid subscriber, I want to manage my subscription through a billing portal, so that I can upgrade, downgrade, update payment method, or cancel.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Access Billing Portal', level: 3 },
      { bullets: [
        'GIVEN I am a paid subscriber',
        'WHEN I click "Manage Subscription" in settings',
        'THEN I am redirected to Stripe Customer Portal'
      ]},
      { heading: 'Scenario 2: Cancel Subscription', level: 3 },
      { bullets: [
        'GIVEN I cancel through portal',
        'WHEN cancellation is processed',
        'THEN I keep access until period end, then revert to trial limits'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Stripe Customer Portal integration',
        '[ ] Webhook handlers for subscription.updated, subscription.deleted',
        '[ ] Grace period handling for cancellations',
        '[ ] UI reflects current plan and status'
      ]}
    ]),
    subtasks: [
      'Create customer portal API route',
      'Add subscription webhooks (updated, deleted)',
      'Implement grace period logic',
      'Show subscription status in UI'
    ]
  },

  // ==================== USAGE TRACKING ====================
  {
    category: 'Usage',
    summary: 'As a user, I want to see my remaining messages, so that I know when to upgrade or pace my usage',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a user, I want to see my remaining message count clearly displayed, so that I can track my usage and know when I need to upgrade my plan.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: View Usage', level: 3 },
      { bullets: [
        'GIVEN I am logged in',
        'WHEN I look at the dashboard or chat page',
        'THEN I see "X messages remaining" or "X/100 used this month"'
      ]},
      { heading: 'Scenario 2: Usage Warning', level: 3 },
      { bullets: [
        'GIVEN I have used 80% of my messages',
        'WHEN I view the app',
        'THEN I see a warning banner suggesting upgrade'
      ]},
      { heading: 'Scenario 3: Limit Reached', level: 3 },
      { bullets: [
        'GIVEN I have used all my messages',
        'WHEN I try to send another message',
        'THEN I see upgrade prompt instead of sending'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Usage counter component',
        '[ ] Usage API endpoint',
        '[ ] 80% warning banner',
        '[ ] 100% limit enforcement with upgrade prompt',
        '[ ] Monthly reset for paid plans'
      ]}
    ]),
    subtasks: [
      'Create usage tracking API',
      'Build usage counter component',
      'Implement warning banner at 80%',
      'Add limit enforcement in chat API',
      'Create upgrade prompt modal'
    ]
  },

  // ==================== LANDING PAGE ====================
  {
    category: 'Marketing',
    summary: 'As a visitor, I want to see a compelling landing page, so that I understand the product value and am motivated to sign up',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a website visitor, I want to see a clear, compelling landing page that explains what Tustle does and its benefits, so that I understand the value and am motivated to start a free trial.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Landing Page Content', level: 3 },
      { bullets: [
        'GIVEN I visit tustle.ai',
        'WHEN the page loads',
        'THEN I see hero section, features, pricing, and CTA'
      ]},
      { heading: 'Landing Page Sections' },
      { bullets: [
        'Hero: Headline, subheadline, CTA button, product screenshot',
        'Problem: Pain points of manual content creation',
        'Solution: How Tustle solves it with brand memory',
        'Features: Key capabilities with icons',
        'Pricing: Plan comparison table',
        'Testimonials: Social proof (for launch)',
        'CTA: Final call-to-action with signup'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Responsive landing page implemented',
        '[ ] All sections with compelling copy',
        '[ ] Pricing table with plan features',
        '[ ] Mobile-optimized design',
        '[ ] Fast page load (<3s)',
        '[ ] SEO meta tags'
      ]}
    ]),
    subtasks: [
      'Create landing page layout',
      'Build hero section component',
      'Build features section component',
      'Build pricing table component',
      'Add CTA sections',
      'Implement responsive design',
      'Add SEO meta tags'
    ]
  },

  // ==================== DATABASE & INFRASTRUCTURE ====================
  {
    category: 'Infrastructure',
    summary: 'As a developer, I want the database schema deployed, so that the application can store and retrieve data',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a developer, I want the complete database schema deployed to Neon PostgreSQL, so that all application data can be properly stored, queried, and maintained.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Schema Migration', level: 3 },
      { bullets: [
        'GIVEN I have the schema definition',
        'WHEN I run migrations',
        'THEN all tables, indexes, and constraints are created'
      ]},
      { heading: 'Database Tables' },
      { bullets: [
        'users: Authentication and profile',
        'brands: Brand ownership and metadata',
        'brand_profiles: Questionnaire responses',
        'threads: Conversation containers',
        'messages: Chat history',
        'subscriptions: Stripe subscription state',
        'usage_periods: Monthly usage tracking',
        'audit_logs: Security audit trail'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Drizzle schema defined for all tables',
        '[ ] Migrations generated and tested',
        '[ ] Neon database provisioned',
        '[ ] Connection pooling configured',
        '[ ] Indexes optimized for queries'
      ]}
    ]),
    subtasks: [
      'Create Drizzle schema file (lib/db/schema.ts)',
      'Generate initial migration',
      'Set up Neon project and branch',
      'Configure connection pooling',
      'Add database indexes',
      'Create seed script for testing'
    ]
  },
  {
    category: 'Infrastructure',
    summary: 'As a developer, I want CI/CD and deployment configured, so that code changes deploy automatically',
    description: buildADF([
      { heading: 'User Story' },
      { paragraph: 'As a developer, I want continuous integration and deployment configured, so that code pushed to GitHub automatically deploys to Vercel production.' },
      { heading: 'Acceptance Criteria' },
      { heading: 'Scenario 1: Auto Deploy', level: 3 },
      { bullets: [
        'GIVEN code is pushed to main branch',
        'WHEN GitHub receives the push',
        'THEN Vercel automatically builds and deploys'
      ]},
      { heading: 'Scenario 2: Preview Deployments', level: 3 },
      { bullets: [
        'GIVEN a PR is opened',
        'WHEN GitHub triggers Vercel',
        'THEN a preview deployment is created for testing'
      ]},
      { heading: 'Definition of Done' },
      { bullets: [
        '[ ] Vercel project connected to GitHub',
        '[ ] Environment variables configured',
        '[ ] Production domain configured',
        '[ ] Preview deployments working',
        '[ ] Build notifications set up'
      ]}
    ]),
    subtasks: [
      'Connect Vercel to GitHub repo',
      'Configure environment variables in Vercel',
      'Set up production domain',
      'Test preview deployments',
      'Add build status badge to README'
    ]
  }
];

// ====================
// EXECUTION
// ====================

async function main() {
  console.log('========================================');
  console.log('  CREATE MVP EPIC AND STORIES (SAFe)');
  console.log('========================================\n');

  const results = {
    epic: null,
    stories: [],
    subtasks: [],
    failed: []
  };

  // 1. Create MVP Epic
  console.log('Creating MVP Epic...');
  try {
    results.epic = await createIssue(mvpEpic);
    console.log(`\nEpic Created: ${results.epic.key}`);
    console.log(`URL: ${JIRA_BASE_URL}/browse/${results.epic.key}\n`);
  } catch (error) {
    console.error(`Failed to create Epic: ${error.message}`);
    return;
  }

  await new Promise(r => setTimeout(r, 200));

  // 2. For Next-Gen projects, use parent field to link Stories to Epic
  console.log('This is a Next-Gen project - using parent field for Epic linking\n');

  // 3. Create Stories under Epic
  console.log('Creating Stories...\n');

  for (let i = 0; i < stories.length; i++) {
    const story = stories[i];
    const storyNumber = i + 1;

    try {
      const storyFields = {
        project: { key: PROJECT_KEY },
        issuetype: { name: 'Story' },
        summary: story.summary,
        description: story.description,
        parent: { key: results.epic.key }, // Next-Gen: use parent field
        labels: [story.category.toLowerCase().replace(/\s+/g, '-')]
      };

      const createdStory = await createIssue(storyFields);
      results.stories.push({ key: createdStory.key, summary: story.summary, category: story.category });
      console.log(`[${storyNumber}/${stories.length}] Story Created: ${createdStory.key}`);
      console.log(`    ${story.summary.substring(0, 60)}...`);

      // Create Subtasks if any
      if (story.subtasks && story.subtasks.length > 0) {
        for (const subtaskSummary of story.subtasks) {
          try {
            const subtaskFields = {
              project: { key: PROJECT_KEY },
              issuetype: { name: 'Subtask' },
              parent: { key: createdStory.key },
              summary: subtaskSummary
            };

            const createdSubtask = await createIssue(subtaskFields);
            results.subtasks.push({ key: createdSubtask.key, parent: createdStory.key });
            console.log(`    -> Subtask: ${createdSubtask.key} - ${subtaskSummary.substring(0, 40)}...`);

            await new Promise(r => setTimeout(r, 100));
          } catch (subtaskError) {
            console.log(`    -> Failed subtask: ${subtaskError.message}`);
            results.failed.push({ type: 'subtask', summary: subtaskSummary, error: subtaskError.message });
          }
        }
      }

      console.log('');
      await new Promise(r => setTimeout(r, 150));
    } catch (storyError) {
      console.log(`[${storyNumber}/${stories.length}] FAILED: ${story.summary.substring(0, 50)}...`);
      console.log(`    Error: ${storyError.message}\n`);
      results.failed.push({ type: 'story', summary: story.summary, error: storyError.message });
    }
  }

  // Summary
  console.log('\n========================================');
  console.log('  SUMMARY');
  console.log('========================================');
  console.log(`Epic: ${results.epic.key}`);
  console.log(`Stories: ${results.stories.length}/${stories.length}`);
  console.log(`Subtasks: ${results.subtasks.length}`);

  if (results.failed.length > 0) {
    console.log(`\nFailed: ${results.failed.length}`);
    results.failed.forEach(f => console.log(`  - ${f.type}: ${f.summary.substring(0, 40)}...`));
  }

  // Group by category
  console.log('\n--- By Category ---');
  const byCategory = {};
  for (const s of results.stories) {
    if (!byCategory[s.category]) byCategory[s.category] = [];
    byCategory[s.category].push(s.key);
  }
  for (const [cat, keys] of Object.entries(byCategory)) {
    console.log(`${cat}: ${keys.join(', ')}`);
  }

  console.log('\n========================================');
  console.log('  LINKS');
  console.log('========================================');
  console.log(`Epic: ${JIRA_BASE_URL}/browse/${results.epic.key}`);
  console.log(`Board: ${JIRA_BASE_URL}/jira/software/projects/${PROJECT_KEY}/boards/1`);
  console.log(`Backlog: ${JIRA_BASE_URL}/jira/software/projects/${PROJECT_KEY}/boards/1/backlog`);
  console.log('========================================\n');

  return results;
}

main().catch(console.error);
