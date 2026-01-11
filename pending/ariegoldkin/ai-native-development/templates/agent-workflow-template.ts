/**
 * Agentic Workflow Template
 * Implements autonomous agents with tool use and ReAct pattern
 */

import OpenAI from 'openai'

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })

// =============================================
// 1. TOOL DEFINITIONS
// =============================================

interface Tool {
  name: string
  description: string
  parameters: {
    type: 'object'
    properties: Record<string, any>
    required: string[]
  }
  execute: (args: any) => Promise<any>
}

const tools: Tool[] = [
  {
    name: 'search_web',
    description: 'Search the web for current information',
    parameters: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' }
      },
      required: ['query']
    },
    execute: async ({ query }) => {
      // Implement web search
      return { results: [`Search results for: ${query}`] }
    }
  },
  {
    name: 'query_database',
    description: 'Query the internal database',
    parameters: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'SQL query or natural language' }
      },
      required: ['query']
    },
    execute: async ({ query: _query }) => {
      // Implement database query
      return { rows: [] }
    }
  },
  {
    name: 'send_email',
    description: 'Send an email to a user',
    parameters: {
      type: 'object',
      properties: {
        to: { type: 'string', description: 'Email address' },
        subject: { type: 'string', description: 'Email subject' },
        body: { type: 'string', description: 'Email body' }
      },
      required: ['to', 'subject', 'body']
    },
    execute: async ({ to: _to, subject: _subject, body: _body }) => {
      // Implement email sending
      return { sent: true, messageId: 'msg_123' }
    }
  }
]

// =============================================
// 2. REACT AGENT (Reasoning + Acting)
// =============================================

interface AgentStep {
  thought: string
  action?: string
  actionInput?: unknown
  observation?: string
}

interface AgentResult {
  answer: string
  steps: AgentStep[]
  totalCost: number
  iterations: number
}

/**
 * Parse agent response into step components
 */
function parseAgentResponse(content: string): { thought: string; action?: string; actionInput?: string } {
  const thoughtMatch = content.match(/Thought: (.*?)(?=\nAction:|$)/s)
  const actionMatch = content.match(/Action: (.*?)(?=\n|$)/)
  const inputMatch = content.match(/Action Input: (.*?)(?=\n|$)/)

  return {
    thought: thoughtMatch?.[1]?.trim() || '',
    action: actionMatch?.[1]?.trim(),
    actionInput: inputMatch?.[1]?.trim()
  }
}

/**
 * Execute a tool and return the observation
 */
async function executeTool(action: string, actionInput: unknown): Promise<string> {
  const tool = tools.find(t => t.name === action)
  if (!tool) {
    return `Error: Tool '${action}' not found`
  }
  const result = await tool.execute(actionInput as Record<string, unknown>)
  return JSON.stringify(result, null, 2)
}

export async function reactAgent(
  task: string,
  options: {
    maxIterations?: number
    verbose?: boolean
  } = {}
): Promise<AgentResult> {
  const { maxIterations = 10, verbose = false } = options

  const steps: AgentStep[] = []
  let totalCost = 0

  const systemPrompt = `You are an autonomous agent that can use tools to complete tasks.

Available tools:
${tools.map(t => `- ${t.name}: ${t.description}`).join('\n')}

Use this exact format for each step:

Thought: [Your reasoning about what to do next]
Action: [tool name]
Action Input: {"param": "value"}
Observation: [Tool result will appear here]

Repeat Thought/Action/Observation until you have enough information.
Then provide:

Answer: [Final answer to the user's task]

IMPORTANT:
- Use tools when you need information
- Think step by step
- Only use available tools
- Action Input must be valid JSON
`

  const messages = [
    { role: 'system' as const, content: systemPrompt },
    { role: 'user' as const, content: task }
  ]

  for (let i = 0; i < maxIterations; i++) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages,
      temperature: 0.1
    })

    const content = response.choices[0].message.content!
    totalCost += (response.usage!.total_tokens / 1000) * 0.01

    if (verbose) {
      console.log(`\n--- Iteration ${i + 1} ---`)
      console.log(content)
    }

    // Check for final answer
    if (content.includes('Answer:')) {
      const answer = content.split('Answer:')[1].trim()
      return { answer, steps, totalCost, iterations: i + 1 }
    }

    // Parse thought, action, and input
    const parsed = parseAgentResponse(content)
    const step: AgentStep = { thought: parsed.thought }

    if (parsed.action && parsed.actionInput) {
      step.action = parsed.action
      try {
        step.actionInput = JSON.parse(parsed.actionInput)
        step.observation = await executeTool(parsed.action, step.actionInput)
      } catch (err) {
        step.observation = `Error: ${err instanceof Error ? err.message : 'Unknown error'}`
      }
    }

    steps.push(step)

    // Add step to messages
    messages.push({
      role: 'assistant',
      content
    })

    if (step.observation) {
      messages.push({
        role: 'user',
        content: `Observation: ${step.observation}`
      })
    }
  }

  throw new Error(`Agent exceeded max iterations (${maxIterations})`)
}

// =============================================
// 3. FUNCTION CALLING AGENT
// =============================================

export async function functionCallingAgent(task: string): Promise<AgentResult> {
  const steps: AgentStep[] = []
  let totalCost = 0

  const messages = [
    { role: 'system' as const, content: 'You are a helpful assistant with access to tools.' },
    { role: 'user' as const, content: task }
  ]

  const openaiTools = tools.map(tool => ({
    type: 'function' as const,
    function: {
      name: tool.name,
      description: tool.description,
      parameters: tool.parameters
    }
  }))

  let iteration = 0
  while (iteration < 10) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages,
      tools: openaiTools
    })

    const message = response.choices[0].message
    totalCost += (response.usage!.total_tokens / 1000) * 0.01

    // No tool calls - final answer
    if (!message.tool_calls) {
      return {
        answer: message.content!,
        steps,
        totalCost,
        iterations: iteration + 1
      }
    }

    // Execute tool calls
    messages.push(message as any)

    for (const toolCall of message.tool_calls) {
      const tool = tools.find(t => t.name === toolCall.function.name)
      if (!tool) continue

      const args = JSON.parse(toolCall.function.arguments)
      const result = await tool.execute(args)

      steps.push({
        thought: `Calling ${toolCall.function.name}`,
        action: toolCall.function.name,
        actionInput: args,
        observation: JSON.stringify(result)
      })

      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        content: JSON.stringify(result)
      })
    }

    iteration++
  }

  throw new Error('Agent exceeded max iterations')
}

// =============================================
// 4. MULTI-AGENT SYSTEM
// =============================================

interface Agent {
  name: string
  role: string
  tools: Tool[]
  systemPrompt: string
}

export async function multiAgentCollaboration(
  task: string,
  agents: Agent[]
): Promise<AgentResult> {
  const steps: AgentStep[] = []
  let totalCost = 0

  // 1. Coordinator plans the task
  const planResponse = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [
      {
        role: 'system',
        content: `You are a coordinator. Break down tasks and assign to agents:
${agents.map(a => `- ${a.name}: ${a.role}`).join('\n')}

Provide a numbered plan with agent assignments.`
      },
      {
        role: 'user',
        content: `Task: ${task}\n\nProvide a step-by-step plan.`
      }
    ]
  })

  const plan = planResponse.choices[0].message.content!
  totalCost += (planResponse.usage!.total_tokens / 1000) * 0.01

  steps.push({
    thought: 'Coordinator planning',
    observation: plan
  })

  // 2. Execute agent subtasks (simplified - in production, parse plan and execute)
  const agentResults = await Promise.all(
    agents.map(async (agent) => {
      const response = await openai.chat.completions.create({
        model: 'gpt-4-turbo-preview',
        messages: [
          { role: 'system', content: agent.systemPrompt },
          { role: 'user', content: `Task: ${task}\n\nPlan:\n${plan}\n\nComplete your part.` }
        ]
      })

      totalCost += (response.usage!.total_tokens / 1000) * 0.01

      return {
        agent: agent.name,
        result: response.choices[0].message.content!
      }
    })
  )

  // 3. Synthesize results
  const synthesisResponse = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [
      {
        role: 'system',
        content: 'Synthesize agent results into a coherent final answer.'
      },
      {
        role: 'user',
        content: `Task: ${task}\n\nAgent Results:\n${JSON.stringify(agentResults, null, 2)}`
      }
    ]
  })

  totalCost += (synthesisResponse.usage!.total_tokens / 1000) * 0.01

  return {
    answer: synthesisResponse.choices[0].message.content!,
    steps,
    totalCost,
    iterations: agents.length + 2 // plan + agents + synthesis
  }
}

// =============================================
// 5. USAGE EXAMPLES
// =============================================

export async function exampleReActAgent() {
  const result = await reactAgent(
    'Find the latest news about AI and send a summary to user@example.com',
    { verbose: true }
  )

  console.log('\n=== Final Answer ===')
  console.log(result.answer)
  console.log(`\nCost: $${result.totalCost.toFixed(4)}`)
  console.log(`Iterations: ${result.iterations}`)
}

export async function exampleFunctionCalling() {
  const result = await functionCallingAgent(
    'Search for React Server Components tutorials and save the top 3 to the database'
  )

  console.log(result.answer)
}

export async function exampleMultiAgent() {
  const agents: Agent[] = [
    {
      name: 'Researcher',
      role: 'Research and gather information',
      tools: [tools[0]], // web search
      systemPrompt: 'You are a researcher. Find accurate, up-to-date information.'
    },
    {
      name: 'Analyst',
      role: 'Analyze data and extract insights',
      tools: [tools[1]], // database
      systemPrompt: 'You are an analyst. Find patterns and insights in data.'
    },
    {
      name: 'Communicator',
      role: 'Draft communications',
      tools: [tools[2]], // email
      systemPrompt: 'You are a communicator. Write clear, professional messages.'
    }
  ]

  const result = await multiAgentCollaboration(
    'Research AI trends, analyze our internal data, and send a weekly report',
    agents
  )

  console.log(result.answer)
}
