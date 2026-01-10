# Agentic Workflows Reference

## Overview

Agentic workflows enable LLMs to reason, plan, and take autonomous actions using tools. This reference covers agent architectures, multi-agent systems, and practical implementation patterns.

---

## ReAct Pattern (Reasoning + Acting)

### Basic ReAct Loop

```typescript
async function reactAgent(task: string) {
  const messages = [
    {
      role: 'system',
      content: `You are an agent that can use tools to complete tasks.

Use this format:
Thought: [reasoning about what to do next]
Action: [tool name]
Action Input: [tool parameters as JSON]
Observation: [tool result]
... (repeat Thought/Action/Observation as needed)
Answer: [final answer]`
    },
    {
      role: 'user',
      content: task
    }
  ]

  const maxIterations = 10
  let iteration = 0

  while (iteration < maxIterations) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages
    })

    const content = response.choices[0].message.content!

    // Check if final answer
    if (content.includes('Answer:')) {
      return content.split('Answer:')[1].trim()
    }

    // Extract action
    const actionMatch = content.match(/Action: (.*?)\n/)
    const actionInputMatch = content.match(/Action Input: (.*?)\n/)

    if (actionMatch && actionInputMatch) {
      const action = actionMatch[1].trim()
      const actionInput = JSON.parse(actionInputMatch[1].trim())

      // Execute action
      const result = await executeTool(action, actionInput)

      // Add observation
      messages.push({
        role: 'assistant',
        content
      })
      messages.push({
        role: 'user',
        content: `Observation: ${JSON.stringify(result)}`
      })
    }

    iteration++
  }

  throw new Error('Agent exceeded max iterations')
}
```

### Tool Executor

```typescript
const TOOLS = {
  search_web: async (query: string) => {
    // Web search implementation
    return { results: [] }
  },
  calculate: async (expression: string) => {
    return { result: eval(expression) }
  },
  get_weather: async (location: string) => {
    // Weather API call
    return { temperature: 72, condition: 'sunny' }
  }
}

async function executeTool(toolName: string, input: any) {
  if (!TOOLS[toolName]) {
    throw new Error(`Unknown tool: ${toolName}`)
  }

  try {
    return await TOOLS[toolName](input)
  } catch (error) {
    return { error: error.message }
  }
}
```

---

## Tree of Thoughts (ToT)

### Explore Multiple Reasoning Paths

```typescript
async function treeOfThoughts(problem: string, depth = 3) {
  interface ThoughtNode {
    thought: string
    score: number
    children: ThoughtNode[]
  }

  async function generateThoughts(context: string): Promise<string[]> {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: 'Generate 3 different approaches to solve this problem.'
        },
        { role: 'user', content: context }
      ]
    })

    return response.choices[0].message.content!.split('\n').filter(t => t.trim())
  }

  async function evaluateThought(thought: string): Promise<number> {
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: 'Rate this solution approach from 0-10.'
        },
        { role: 'user', content: thought }
      ]
    })

    return parseFloat(response.choices[0].message.content || '5')
  }

  async function buildTree(context: string, currentDepth: number): Promise<ThoughtNode[]> {
    if (currentDepth >= depth) return []

    const thoughts = await generateThoughts(context)

    return Promise.all(
      thoughts.map(async thought => {
        const score = await evaluateThought(thought)
        const children = await buildTree(`${context}\n${thought}`, currentDepth + 1)

        return { thought, score, children }
      })
    )
  }

  const tree = await buildTree(problem, 0)

  // Find best path
  function findBestPath(nodes: ThoughtNode[]): ThoughtNode[] {
    if (nodes.length === 0) return []

    const best = nodes.reduce((max, node) =>
      node.score > max.score ? node : max
    )

    return [best, ...findBestPath(best.children)]
  }

  return findBestPath(tree)
}
```

---

## Multi-Agent Collaboration

### Agent Coordinator

```typescript
interface Agent {
  name: string
  role: string
  tools: string[]
  systemPrompt: string
}

class AgentCoordinator {
  private agents: Map<string, Agent>

  constructor(agents: Agent[]) {
    this.agents = new Map(agents.map(a => [a.name, a]))
  }

  async executeTask(task: string): Promise<string> {
    // 1. Plan: Decompose task and assign agents
    const plan = await this.createPlan(task)

    // 2. Execute: Run agents in sequence or parallel
    const results = new Map<string, any>()

    for (const step of plan.steps) {
      if (step.parallel) {
        const parallelResults = await Promise.all(
          step.agents.map(agentName =>
            this.runAgent(agentName, step.task, results)
          )
        )
        parallelResults.forEach((result, i) => {
          results.set(step.agents[i], result)
        })
      } else {
        for (const agentName of step.agents) {
          const result = await this.runAgent(agentName, step.task, results)
          results.set(agentName, result)
        }
      }
    }

    // 3. Synthesize: Combine results
    return this.synthesizeResults(task, results)
  }

  private async createPlan(task: string) {
    const agentDescriptions = Array.from(this.agents.values())
      .map(a => `- ${a.name}: ${a.role}`)
      .join('\n')

    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: `Create an execution plan assigning agents to subtasks.

Available agents:
${agentDescriptions}

Return JSON: { steps: [{ agents: string[], task: string, parallel: boolean }] }`
        },
        { role: 'user', content: task }
      ],
      response_format: { type: 'json_object' }
    })

    return JSON.parse(response.choices[0].message.content!)
  }

  private async runAgent(agentName: string, task: string, context: Map<string, any>) {
    const agent = this.agents.get(agentName)!

    const contextStr = Array.from(context.entries())
      .map(([agent, result]) => `${agent}: ${JSON.stringify(result)}`)
      .join('\n')

    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        { role: 'system', content: agent.systemPrompt },
        {
          role: 'user',
          content: `Task: ${task}\n\nContext from other agents:\n${contextStr}`
        }
      ]
    })

    return response.choices[0].message.content!
  }

  private async synthesizeResults(task: string, results: Map<string, any>) {
    const resultsStr = Array.from(results.entries())
      .map(([agent, result]) => `${agent}:\n${result}`)
      .join('\n\n')

    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: 'Synthesize agent results into a cohesive final answer.'
        },
        {
          role: 'user',
          content: `Task: ${task}\n\nAgent Results:\n${resultsStr}`
        }
      ]
    })

    return response.choices[0].message.content!
  }
}
```

### Example Usage

```typescript
const agents: Agent[] = [
  {
    name: 'researcher',
    role: 'Research and gather information',
    tools: ['search', 'fetch_url'],
    systemPrompt: 'You are a research agent. Find relevant information and sources.'
  },
  {
    name: 'analyst',
    role: 'Analyze data and identify patterns',
    tools: ['calculate', 'visualize'],
    systemPrompt: 'You are an analyst. Find insights and patterns in data.'
  },
  {
    name: 'writer',
    role: 'Write clear, structured content',
    tools: ['spell_check', 'grammar_check'],
    systemPrompt: 'You are a writer. Create clear, well-structured content.'
  }
]

const coordinator = new AgentCoordinator(agents)

const result = await coordinator.executeTask(
  'Research the impact of AI on healthcare and write a summary report'
)
```

---

## Autonomous Agent Loop

### Self-Directed Agent

```typescript
class AutonomousAgent {
  private memory: Message[] = []
  private goals: string[] = []

  async run(initialGoal: string, maxIterations = 20) {
    this.goals.push(initialGoal)
    let iteration = 0

    while (this.goals.length > 0 && iteration < maxIterations) {
      const currentGoal = this.goals[0]

      // 1. Plan next action
      const action = await this.planAction(currentGoal)

      // 2. Execute action
      const result = await this.executeAction(action)

      // 3. Reflect on result
      const reflection = await this.reflect(currentGoal, action, result)

      // 4. Update goals based on reflection
      if (reflection.goalAchieved) {
        this.goals.shift()
      } else if (reflection.newGoals) {
        this.goals.unshift(...reflection.newGoals)
      }

      iteration++
    }

    return this.memory
  }

  private async planAction(goal: string) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: 'Plan the next action to achieve the goal. Consider past actions.'
        },
        ...this.memory,
        { role: 'user', content: `Current goal: ${goal}` }
      ]
    })

    return response.choices[0].message.content!
  }

  private async executeAction(action: string) {
    // Execute the planned action
    const result = await executeTool(action, {})

    this.memory.push(
      { role: 'assistant', content: `Action: ${action}` },
      { role: 'user', content: `Result: ${JSON.stringify(result)}` }
    )

    return result
  }

  private async reflect(goal: string, action: string, result: any) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: `Reflect on whether the action achieved the goal. Return JSON:
{
  "goalAchieved": boolean,
  "reasoning": string,
  "newGoals": string[] // Break down goal into subtasks if needed
}`
        },
        {
          role: 'user',
          content: `Goal: ${goal}\nAction: ${action}\nResult: ${JSON.stringify(result)}`
        }
      ],
      response_format: { type: 'json_object' }
    })

    return JSON.parse(response.choices[0].message.content!)
  }
}
```

---

## Memory Management

### Long-Term Memory

```typescript
class AgentMemory {
  private shortTerm: Message[] = []
  private longTerm: Map<string, any> = new Map()
  private summaries: string[] = []

  async addMessage(message: Message) {
    this.shortTerm.push(message)

    // Summarize when short-term gets too long
    if (this.shortTerm.length > 20) {
      await this.summarizeAndCompress()
    }
  }

  private async summarizeAndCompress() {
    const toSummarize = this.shortTerm.slice(0, -10)

    const summary = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: 'Summarize this conversation, keeping key facts and decisions.'
        },
        ...toSummarize
      ]
    })

    this.summaries.push(summary.choices[0].message.content!)
    this.shortTerm = this.shortTerm.slice(-10)
  }

  async recall(query: string) {
    // Search long-term memory
    const relevantMemories = await this.searchMemories(query)

    return {
      summary: this.summaries.join('\n'),
      recent: this.shortTerm,
      relevant: relevantMemories
    }
  }

  private async searchMemories(query: string) {
    // Use embeddings to find relevant past conversations
    const queryEmbedding = await createEmbedding(query)

    return Array.from(this.longTerm.entries())
      .map(([key, memory]) => ({
        key,
        memory,
        similarity: cosineSimilarity(queryEmbedding, memory.embedding)
      }))
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, 5)
  }
}
```

---

## Best Practices

### Error Recovery

```typescript
async function resilientAgent(task: string) {
  const maxRetries = 3
  let retries = 0

  while (retries < maxRetries) {
    try {
      return await reactAgent(task)
    } catch (error) {
      retries++

      if (retries >= maxRetries) {
        // Fallback strategy
        return await simpleCompletion(task)
      }

      // Retry with adjusted parameters
      await new Promise(resolve => setTimeout(resolve, 1000 * retries))
    }
  }
}
```

### Safety Guards

```typescript
async function safeAgent(task: string) {
  // 1. Validate task is safe
  const safety = await openai.moderations.create({ input: task })

  if (safety.results[0].flagged) {
    throw new Error('Unsafe task detected')
  }

  // 2. Run agent with output validation
  const result = await reactAgent(task)

  // 3. Validate output
  const outputSafety = await openai.moderations.create({ input: result })

  if (outputSafety.results[0].flagged) {
    return 'I cannot complete this task safely.'
  }

  return result
}
```

### Performance Optimization

```typescript
// Use faster models for simple actions
async function optimizedAgent(task: string) {
  const complexity = await assessComplexity(task)

  const model = complexity > 7 ? 'gpt-4-turbo-preview' : 'gpt-3.5-turbo'

  return reactAgent(task, { model })
}

async function assessComplexity(task: string): Promise<number> {
  const factors = {
    length: task.length > 500 ? 2 : 0,
    multiStep: task.includes('and') || task.includes('then') ? 3 : 0,
    technical: /\b(code|implement|design|architecture)\b/i.test(task) ? 3 : 0
  }

  return Object.values(factors).reduce((sum, val) => sum + val, 0)
}
```
