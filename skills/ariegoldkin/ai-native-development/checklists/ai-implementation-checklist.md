# AI-Native Development Implementation Checklist

Use this checklist when building AI-powered applications with LLMs, RAG, and agentic workflows.

## Embeddings & Vector Search

### Setup
- [ ] Choose embedding model (OpenAI text-embedding-3-small/large, Cohere, etc.)
- [ ] Select vector database (Pinecone, Weaviate, Chroma, Qdrant)
- [ ] Configure vector dimensions based on embedding model
- [ ] Set up appropriate similarity metric (cosine, euclidean, dot product)
- [ ] Create indexes with proper configuration

### Document Processing
- [ ] Chunk documents to optimal size (500-1000 tokens)
- [ ] Add chunk overlap (10-20%) for continuity
- [ ] Include metadata (source, date, category) with chunks
- [ ] Handle different document types (PDF, HTML, Markdown)
- [ ] Implement incremental updates (update only changed documents)

### Search & Retrieval
- [ ] Implement semantic search with embeddings
- [ ] Add keyword search for hybrid retrieval
- [ ] Configure topK parameter appropriately (3-10 results)
- [ ] Implement re-ranking for better relevance
- [ ] Add filtering by metadata (date, category, etc.)
- [ ] Cache frequent queries
- [ ] Monitor query latency and optimize

## RAG Implementation

### Pipeline Design
- [ ] Implement document ingestion pipeline
- [ ] Create chunking strategy
- [ ] Set up vector indexing
- [ ] Implement retrieval logic
- [ ] Configure LLM generation

### Context Management
- [ ] Retrieve relevant documents (3-10)
- [ ] Format context clearly with citations
- [ ] Stay within context window limits
- [ ] Handle cases with no relevant context
- [ ] Implement fallback strategies

### Answer Generation
- [ ] Use appropriate model (GPT-4, Claude, etc.)
- [ ] Set low temperature (0.1-0.3) for factual responses
- [ ] Instruct model to cite sources
- [ ] Handle "I don't know" cases gracefully
- [ ] Validate answers against context

### Quality Assurance
- [ ] Test with edge cases (no context, ambiguous queries)
- [ ] Verify citations are accurate
- [ ] Check for hallucinations
- [ ] Monitor answer quality over time
- [ ] Implement user feedback loop

## LLM Integration

### Model Selection
- [ ] Choose appropriate model for task (GPT-4, Claude, Llama)
- [ ] Consider cost vs quality tradeoffs
- [ ] Use cheaper models for simple tasks
- [ ] Implement fallback models for redundancy

### Configuration
- [ ] Set appropriate temperature (0 for factual, 0.7 for creative)
- [ ] Configure max_tokens to prevent runaway generation
- [ ] Set stop sequences if needed
- [ ] Configure presence/frequency penalties

### Prompt Engineering
- [ ] Write clear, specific system prompts
- [ ] Provide few-shot examples when helpful
- [ ] Use structured output formats (JSON, YAML)
- [ ] Implement chain-of-thought for complex reasoning
- [ ] Test prompts with edge cases

### API Integration
- [ ] Handle rate limits gracefully
- [ ] Implement exponential backoff for retries
- [ ] Set appropriate timeouts
- [ ] Log all API calls for debugging
- [ ] Monitor API usage and costs

## Function Calling & Tools

### Tool Design
- [ ] Define clear, focused function names
- [ ] Write detailed function descriptions
- [ ] Use strict JSON schema for parameters
- [ ] Mark required vs optional parameters
- [ ] Limit to 10-20 tools to avoid confusion

### Implementation
- [ ] Validate function arguments before execution
- [ ] Handle errors gracefully
- [ ] Return structured responses
- [ ] Log tool calls for debugging
- [ ] Implement authorization checks

### Agent Loop
- [ ] Implement function calling loop
- [ ] Set max iterations to prevent infinite loops
- [ ] Handle missing or invalid tools
- [ ] Provide clear error messages
- [ ] Return final answer after tool use

## Streaming Responses

### Server Setup
- [ ] Implement streaming endpoint
- [ ] Use Server-Sent Events or WebSockets
- [ ] Handle client disconnections
- [ ] Implement backpressure handling

### Client Integration
- [ ] Display tokens as they arrive
- [ ] Handle stream errors
- [ ] Implement retry logic
- [ ] Show loading states
- [ ] Buffer partial responses if needed

## Cost Optimization

### Token Management
- [ ] Count tokens before API calls
- [ ] Set max_tokens appropriately
- [ ] Truncate long inputs intelligently
- [ ] Remove unnecessary context

### Caching
- [ ] Implement prompt caching (Anthropic)
- [ ] Cache frequent queries
- [ ] Use semantic caching for similar queries
- [ ] Set appropriate TTLs

### Model Selection
- [ ] Use GPT-3.5 for simple tasks
- [ ] Reserve GPT-4/Claude for complex reasoning
- [ ] Batch requests when possible
- [ ] Use function calling instead of prompt parsing

### Monitoring
- [ ] Track token usage per request
- [ ] Monitor daily/monthly costs
- [ ] Set up cost alerts
- [ ] Identify expensive operations
- [ ] Optimize high-cost queries

## Security & Safety

### Input Validation
- [ ] Sanitize user inputs
- [ ] Check input length limits
- [ ] Filter harmful content
- [ ] Prevent prompt injection attacks
- [ ] Validate uploaded files

### Output Filtering
- [ ] Filter harmful or inappropriate outputs
- [ ] Redact sensitive information
- [ ] Validate structured outputs (JSON)
- [ ] Check for PII leakage

### API Security
- [ ] Never expose API keys in client code
- [ ] Use environment variables for secrets
- [ ] Rotate API keys regularly
- [ ] Implement rate limiting per user
- [ ] Log security events

### Data Privacy
- [ ] Don't send PII to third-party LLMs
- [ ] Implement data retention policies
- [ ] Allow users to delete their data
- [ ] Comply with GDPR/CCPA if applicable
- [ ] Encrypt sensitive data

## Observability & Monitoring

### Logging
- [ ] Log all LLM API calls
- [ ] Include prompt, response, tokens, latency
- [ ] Log tool calls and results
- [ ] Capture errors and stack traces
- [ ] Use structured logging (JSON)

### Metrics
- [ ] Track request latency (p50, p95, p99)
- [ ] Monitor token usage per request
- [ ] Calculate cost per request
- [ ] Track error rates
- [ ] Measure user satisfaction

### Tracing
- [ ] Use LangSmith or similar for traces
- [ ] Track multi-step agent workflows
- [ ] Identify bottlenecks
- [ ] Debug failed requests
- [ ] Analyze user conversations

### Alerts
- [ ] Set up alerts for high error rates
- [ ] Alert on unusual cost spikes
- [ ] Monitor API rate limits
- [ ] Alert on high latency (>5s)
- [ ] Track model availability

## Testing

### Unit Tests
- [ ] Test embedding generation
- [ ] Test vector search accuracy
- [ ] Test function execution
- [ ] Test prompt templates
- [ ] Test error handling

### Integration Tests
- [ ] Test RAG pipeline end-to-end
- [ ] Test agent workflows
- [ ] Test streaming responses
- [ ] Test with real LLM APIs
- [ ] Test concurrent requests

### Evaluation
- [ ] Create test dataset with ground truth
- [ ] Measure answer relevance
- [ ] Calculate precision/recall for retrieval
- [ ] Test with adversarial inputs
- [ ] Get human evaluation for quality

## Production Checklist

### Before Deployment
- [ ] Test with production data volume
- [ ] Load test API endpoints
- [ ] Verify cost estimates
- [ ] Set up monitoring and alerts
- [ ] Prepare rollback plan

### Configuration
- [ ] Set production API keys
- [ ] Configure rate limits
- [ ] Set appropriate timeouts
- [ ] Enable error tracking (Sentry)
- [ ] Configure CORS if needed

### Scaling
- [ ] Implement caching layer
- [ ] Use CDN for static assets
- [ ] Consider async processing for long tasks
- [ ] Implement queue system for high load
- [ ] Plan for vector DB scaling

### Maintenance
- [ ] Monitor costs daily
- [ ] Review logs for errors
- [ ] Update embeddings when content changes
- [ ] Retrain/update models periodically
- [ ] Collect user feedback
- [ ] Iterate on prompts and workflows

## Common Pitfalls to Avoid

- [ ] ❌ Don't send entire documents as context (chunk them)
- [ ] ❌ Don't ignore rate limits (implement backoff)
- [ ] ❌ Don't expose API keys (use env vars)
- [ ] ❌ Don't skip input validation (prevent injection)
- [ ] ❌ Don't use high temperature for factual tasks
- [ ] ❌ Don't forget to cite sources in RAG
- [ ] ❌ Don't exceed context window limits
- [ ] ❌ Don't skip cost monitoring (can get expensive)
- [ ] ❌ Don't trust LLM outputs blindly (validate)
- [ ] ❌ Don't forget to handle streaming errors
