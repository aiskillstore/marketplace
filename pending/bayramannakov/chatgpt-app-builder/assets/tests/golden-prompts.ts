/**
 * Golden Prompt Tests
 *
 * Tests that verify the app triggers correctly for expected prompts
 * and does NOT trigger for negative prompts.
 *
 * These tests require a running MCP server and ChatGPT connector.
 */

// ============================================================================
// Types
// ============================================================================

interface PromptTest {
  prompt: string;
  expectedTool?: string;
  shouldTrigger: boolean;
  category: "direct" | "indirect" | "negative";
}

interface PromptTestResult {
  prompt: string;
  category: string;
  shouldTrigger: boolean;
  didTrigger: boolean;
  triggeredTool?: string;
  passed: boolean;
  notes?: string;
}

// ============================================================================
// Golden Prompts
// ============================================================================

/**
 * Define your golden prompts here.
 * These should match the prompts in your app-spec.md.
 */
const goldenPrompts: PromptTest[] = [
  // Direct prompts - explicitly mention your app
  {
    prompt: "Show my {{APP_NAME}} items",
    expectedTool: "{{APP_PREFIX}}_get_items",
    shouldTrigger: true,
    category: "direct",
  },
  {
    prompt: "Create a new item in {{APP_NAME}}",
    expectedTool: "{{APP_PREFIX}}_create_item",
    shouldTrigger: true,
    category: "direct",
  },
  {
    prompt: "What's in my {{APP_NAME}} list?",
    expectedTool: "{{APP_PREFIX}}_get_items",
    shouldTrigger: true,
    category: "direct",
  },
  {
    prompt: "Use {{APP_NAME}} to add a task",
    expectedTool: "{{APP_PREFIX}}_create_item",
    shouldTrigger: true,
    category: "direct",
  },
  {
    prompt: "Open {{APP_NAME}} and show active items",
    expectedTool: "{{APP_PREFIX}}_get_items",
    shouldTrigger: true,
    category: "direct",
  },

  // Indirect prompts - describe intent without naming app
  {
    prompt: "What should I work on today?",
    expectedTool: "{{APP_PREFIX}}_get_items",
    shouldTrigger: true,
    category: "indirect",
  },
  {
    prompt: "Help me track my tasks",
    expectedTool: "{{APP_PREFIX}}_get_items",
    shouldTrigger: true,
    category: "indirect",
  },
  {
    prompt: "I need to add something to my to-do list",
    expectedTool: "{{APP_PREFIX}}_create_item",
    shouldTrigger: true,
    category: "indirect",
  },
  {
    prompt: "Show me what's overdue",
    expectedTool: "{{APP_PREFIX}}_get_items",
    shouldTrigger: true,
    category: "indirect",
  },
  {
    prompt: "Can you help me organize my work?",
    expectedTool: "{{APP_PREFIX}}_get_items",
    shouldTrigger: true,
    category: "indirect",
  },

  // Negative prompts - should NOT trigger your app
  {
    prompt: "Set an alarm for 7am",
    shouldTrigger: false,
    category: "negative",
  },
  {
    prompt: "Send an email to my team",
    shouldTrigger: false,
    category: "negative",
  },
  {
    prompt: "What's the weather today?",
    shouldTrigger: false,
    category: "negative",
  },
];

// ============================================================================
// Test Runner
// ============================================================================

async function runGoldenPromptTests(): Promise<void> {
  console.log("Golden Prompt Test Results\n");
  console.log("=".repeat(60));

  const results: PromptTestResult[] = [];
  const categories = ["direct", "indirect", "negative"] as const;

  for (const category of categories) {
    console.log(`\n${category.toUpperCase()} PROMPTS\n`);

    const categoryPrompts = goldenPrompts.filter((p) => p.category === category);

    for (const test of categoryPrompts) {
      // TODO: Replace with actual ChatGPT/MCP testing
      // In real implementation, this would:
      // 1. Send prompt to ChatGPT
      // 2. Check if your connector was triggered
      // 3. Check which tool was called
      const result = await mockPromptTest(test);
      results.push(result);

      const status = result.passed ? "✓" : "✗";
      console.log(`${status} "${test.prompt}"`);

      if (!result.passed) {
        console.log(`  Expected: ${test.shouldTrigger ? "trigger" : "no trigger"}`);
        console.log(`  Actual: ${result.didTrigger ? "triggered" : "did not trigger"}`);
        if (result.notes) {
          console.log(`  Notes: ${result.notes}`);
        }
      }
    }
  }

  // Summary
  console.log("\n" + "=".repeat(60));
  console.log("\nSUMMARY\n");

  for (const category of categories) {
    const categoryResults = results.filter((r) => r.category === category);
    const passed = categoryResults.filter((r) => r.passed).length;
    const total = categoryResults.length;
    console.log(`${category}: ${passed}/${total} passed`);
  }

  const totalPassed = results.filter((r) => r.passed).length;
  const totalTests = results.length;
  console.log(`\nTotal: ${totalPassed}/${totalTests} passed`);

  if (totalPassed < totalTests) {
    console.log("\n⚠️  Some tests failed. Review tool descriptions and metadata.");
    process.exit(1);
  } else {
    console.log("\n✓ All golden prompt tests passed!");
  }
}

// ============================================================================
// Mock Implementation
// ============================================================================

/**
 * Mock prompt test.
 * Replace with actual ChatGPT/MCP testing in production.
 */
async function mockPromptTest(test: PromptTest): Promise<PromptTestResult> {
  // Simulate delay
  await new Promise((r) => setTimeout(r, 10));

  // Mock logic: assume prompts with "{{APP_NAME}}" or task-related words trigger
  const promptLower = test.prompt.toLowerCase();
  const appMentioned = promptLower.includes("{{APP_NAME}}".toLowerCase());
  const taskWords = ["task", "item", "to-do", "work", "track", "organize"];
  const hasTaskWord = taskWords.some((w) => promptLower.includes(w));

  const wouldTrigger = appMentioned || hasTaskWord;

  return {
    prompt: test.prompt,
    category: test.category,
    shouldTrigger: test.shouldTrigger,
    didTrigger: wouldTrigger,
    triggeredTool: wouldTrigger ? test.expectedTool : undefined,
    passed: wouldTrigger === test.shouldTrigger,
    notes: wouldTrigger !== test.shouldTrigger
      ? "Review tool descriptions"
      : undefined,
  };
}

// ============================================================================
// Export for use in test suite
// ============================================================================

export { goldenPrompts, runGoldenPromptTests };

// Run if executed directly
if (require.main === module) {
  runGoldenPromptTests().catch(console.error);
}
