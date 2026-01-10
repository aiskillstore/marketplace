/**
 * RAG (Retrieval-Augmented Generation) Pipeline Template
 * Implements a complete RAG system with vector database and LLM
 */

import OpenAI from 'openai'
import { Pinecone } from '@pinecone-database/pinecone'
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter'

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
const pinecone = new Pinecone({ apiKey: process.env.PINECONE_API_KEY! })
const index = pinecone.index('knowledge-base')

// =============================================
// 1. DOCUMENT INGESTION
// =============================================

interface Document {
  id: string
  text: string
  metadata?: Record<string, any>
}

/**
 * Chunk documents for optimal retrieval
 */
async function chunkDocument(text: string, metadata?: Record<string, any>): Promise<Document[]> {
  const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: 800,
    chunkOverlap: 100,
    separators: ['\n\n', '\n', '. ', ' ', '']
  })

  const chunks = await splitter.createDocuments([text])

  return chunks.map((chunk, i) => ({
    id: `${metadata?.source || 'doc'}_chunk_${i}`,
    text: chunk.pageContent,
    metadata: {
      ...metadata,
      chunkIndex: i,
      chunkCount: chunks.length
    }
  }))
}

/**
 * Create embeddings for documents
 */
async function createEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  })
  return response.data[0].embedding
}

/**
 * Index documents into vector database
 */
async function indexDocuments(documents: Document[]) {
  const vectors = await Promise.all(
    documents.map(async (doc) => ({
      id: doc.id,
      values: await createEmbedding(doc.text),
      metadata: {
        text: doc.text,
        ...doc.metadata
      }
    }))
  )

  // Upsert in batches of 100
  const batchSize = 100
  for (let i = 0; i < vectors.length; i += batchSize) {
    const batch = vectors.slice(i, i + batchSize)
    await index.upsert(batch)
  }

  console.log(`Indexed ${documents.length} document chunks`)
}

// =============================================
// 2. RETRIEVAL
// =============================================

interface SearchResult {
  id: string
  score: number
  text: string
  metadata?: Record<string, any>
}

/**
 * Query vector database for relevant documents
 */
async function retrieveDocuments(
  query: string,
  topK = 5,
  filter?: Record<string, any>
): Promise<SearchResult[]> {
  const queryEmbedding = await createEmbedding(query)

  const results = await index.query({
    vector: queryEmbedding,
    topK,
    filter,
    includeMetadata: true
  })

  return results.matches.map(match => ({
    id: match.id,
    score: match.score || 0,
    text: match.metadata?.text as string,
    metadata: match.metadata
  }))
}

/**
 * Re-rank results using cross-encoder (optional enhancement)
 */
async function rerank(query: string, documents: SearchResult[]): Promise<SearchResult[]> {
  // Use a cross-encoder model for better relevance scoring
  // For now, return as-is (implement with Cohere Rerank, etc.)
  return documents
}

// =============================================
// 3. GENERATION
// =============================================

interface RAGResponse {
  answer: string
  sources: Array<{
    id: string
    text: string
    score: number
    metadata?: Record<string, any>
  }>
  usage: {
    retrievalTime: number
    generationTime: number
    totalTokens: number
  }
}

/**
 * Generate answer using retrieved context
 */
async function generateAnswer(
  question: string,
  context: SearchResult[]
): Promise<RAGResponse> {
  const retrievalStart = Date.now()

  // Construct context from retrieved documents
  const contextText = context
    .map((doc, i) => `[${i + 1}] ${doc.text}\nSource: ${doc.metadata?.source || 'Unknown'}`)
    .join('\n\n')

  const retrievalTime = Date.now() - retrievalStart
  const generationStart = Date.now()

  // Generate answer with LLM
  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    temperature: 0.1, // Low temperature for factual responses
    messages: [
      {
        role: 'system',
        content: `You are a helpful assistant that answers questions based ONLY on the provided context.

Instructions:
1. Answer the question using ONLY information from the context
2. If the answer is not in the context, say "I don't have enough information to answer that."
3. ALWAYS cite your sources using [1], [2], etc.
4. Be concise and accurate
5. If there are conflicting sources, mention both with citations`
      },
      {
        role: 'user',
        content: `Context:\n${contextText}\n\nQuestion: ${question}`
      }
    ]
  })

  const generationTime = Date.now() - generationStart

  return {
    answer: response.choices[0].message.content!,
    sources: context.map((doc) => ({
      id: doc.id,
      text: doc.text,
      score: doc.score,
      metadata: doc.metadata
    })),
    usage: {
      retrievalTime,
      generationTime,
      totalTokens: response.usage?.total_tokens || 0
    }
  }
}

// =============================================
// 4. COMPLETE RAG PIPELINE
// =============================================

/**
 * Complete RAG query - retrieve + generate
 */
export async function ragQuery(
  question: string,
  options: {
    topK?: number
    filter?: Record<string, any>
    rerank?: boolean
  } = {}
): Promise<RAGResponse> {
  const { topK = 5, filter, rerank: shouldRerank = false } = options

  // 1. Retrieve relevant documents
  let documents = await retrieveDocuments(question, topK, filter)

  // 2. Optional re-ranking
  if (shouldRerank) {
    documents = await rerank(question, documents)
  }

  // 3. Generate answer
  return generateAnswer(question, documents)
}

// =============================================
// 5. CONVERSATIONAL RAG
// =============================================

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}

interface ConversationContext {
  messages: Message[]
  userId: string
}

/**
 * RAG with conversation history
 */
export async function conversationalRAG(
  question: string,
  context: ConversationContext
): Promise<RAGResponse> {
  // Condense question with conversation history
  const condensedQuestion = await condenseQuestion(question, context.messages)

  // Perform RAG with condensed question
  const result = await ragQuery(condensedQuestion)

  // Update conversation history
  context.messages.push(
    { role: 'user', content: question },
    { role: 'assistant', content: result.answer }
  )

  return result
}

/**
 * Condense follow-up questions with chat history
 */
async function condenseQuestion(
  question: string,
  history: Message[]
): Promise<string> {
  if (history.length === 0) {
    return question
  }

  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo', // Cheaper model for this task
    messages: [
      {
        role: 'system',
        content: 'Given a conversation and a follow-up question, rephrase the follow-up question to be a standalone question.'
      },
      ...history.slice(-6), // Last 3 exchanges
      {
        role: 'user',
        content: `Follow-up question: ${question}\n\nStandalone question:`
      }
    ],
    temperature: 0
  })

  return response.choices[0].message.content!.trim()
}

// =============================================
// 6. USAGE EXAMPLES
// =============================================

/**
 * Example 1: Index documents
 */
export async function exampleIndexing() {
  const documents = [
    {
      id: 'doc1',
      text: 'React Server Components allow you to render components on the server...',
      metadata: { source: 'React Docs', category: 'frontend' }
    },
    // ... more documents
  ]

  // Chunk and index
  const chunks = (await Promise.all(
    documents.map(doc => chunkDocument(doc.text, doc.metadata))
  )).flat()

  await indexDocuments(chunks)
}

/**
 * Example 2: Simple query
 */
export async function exampleSimpleQuery() {
  const result = await ragQuery('What are React Server Components?')
  console.log('Answer:', result.answer)
  console.log('Sources:', result.sources)
}

/**
 * Example 3: Filtered query
 */
export async function exampleFilteredQuery() {
  const result = await ragQuery(
    'How do I optimize performance?',
    {
      topK: 3,
      filter: { category: 'performance' }
    }
  )
  console.log(result)
}

/**
 * Example 4: Conversational query
 */
export async function exampleConversational() {
  const context: ConversationContext = {
    messages: [],
    userId: 'user123'
  }

  // First question
  const result1 = await conversationalRAG(
    'What is React?',
    context
  )
  console.log(result1.answer)

  // Follow-up question
  const result2 = await conversationalRAG(
    'How does it compare to Vue?',
    context
  )
  console.log(result2.answer)
}
