# Search Query Templates

Pre-defined search query templates for discovering AI news across different categories and timeframes.

## Date Format

Use dynamic date insertion based on current date:
- **Today**: `[current_date]` (e.g., 2025-12-24)
- **Yesterday**: `[current_date - 1 day]` (e.g., 2025-12-23)
- **This week**: `[current_date - 7 days]` (e.g., 2025-12-17)
- **This month**: `[current_date - 30 days]` (e.g., 2025-11-24)

---

## General AI News

### Daily Updates (Last 24 hours)
```
"AI news today" OR "artificial intelligence breakthrough" after:[yesterday]
```

### This Week's Developments
```
"AI news this week" OR "artificial intelligence announcement" after:[week_ago]
```

### Latest AI Developments
```
"latest AI developments" OR "AI advancement" after:[yesterday]
```

### AI Industry News
```
"AI industry news" OR "artificial intelligence market" after:[yesterday]
```

---

## Category-Specific Queries

### Research & Papers

#### Recent AI Research Papers
```
"AI research paper" OR "machine learning breakthrough" after:[yesterday]
```

#### arXiv AI Papers
```
arXiv "cs.AI" OR "cs.LG" OR "artificial intelligence" paper after:[yesterday]
```

#### Academic AI Breakthroughs
```
"AI breakthrough" OR "machine learning research" after:[yesterday]
```

#### Conference Papers
```
"NeurIPS 2025" OR "ICML 2025" OR "ACL 2025" AI paper
```

---

### Industry & Business

#### AI Funding & Investment
```
"AI startup funding" OR "artificial intelligence investment" after:[week_ago]
```

#### AI Company News
```
"AI company news" OR "OpenAI news" OR "Google AI" after:[yesterday]
```

#### AI Partnerships & Acquisitions
```
"AI acquisition" OR "AI partnership" OR "artificial intelligence deal" after:[week_ago]
```

#### AI Market Trends
```
"AI market trends" OR "artificial intelligence industry analysis" after:[week_ago]
```

---

### Products & Tools

#### New AI Tools
```
"AI application launch" OR "new AI tool" after:[yesterday]
```

#### AI Product Releases
```
"AI product release" OR "artificial intelligence software launch" after:[yesterday]
```

#### Open Source AI
```
"open source AI" OR "AI model release" OR "LLM release" after:[yesterday]
```

#### AI Framework Updates
```
"PyTorch update" OR "TensorFlow update" OR "AI framework" after:[week_ago]
```

---

### Company-Specific Queries

#### OpenAI
```
"OpenAI announcement" OR "GPT update" OR "ChatGPT news" after:[yesterday]
```

#### Google
```
"Google AI announcement" OR "Gemini update" OR "Bard news" after:[yesterday]
```

#### Anthropic
```
"Anthropic news" OR "Claude update" OR "constitutional AI" after:[yesterday]
```

#### Meta
```
"Meta AI announcement" OR "LLaMA update" OR "Facebook AI" after:[yesterday]
```

#### Microsoft
```
"Microsoft AI" OR "Copilot update" OR "Azure AI news" after:[yesterday]
```

#### DeepMind
```
"DeepMind research" OR "AlphaFold update" OR "Google DeepMind" after:[week_ago]
```

---

## Advanced Search Techniques

### Boolean Operators

#### AND (Both terms must be present)
```
"AI" AND "breakthrough" AND "2025"
```

#### OR (At least one term must be present)
```
"artificial intelligence" OR "machine learning" OR "deep learning"
```

#### NOT (Exclude terms)
```
"AI" AND "news" NOT "cryptocurrency" NOT "blockchain"
```

#### Exact Phrases
```
"large language model" OR "LLM"
```

### Date Filters

#### Last 24 Hours
```
after:[yesterday's date]
```

#### Last 3 Days
```
after:[3 days ago]
```

#### Last Week
```
after:[7 days ago]
```

#### Last Month
```
after:[30 days ago]
```

### Source Filters

#### News Sites Only
```
site:venturebeat.com AI OR site:techcrunch.com AI
```

#### Academic Sources
```
site:arxiv.org "artificial intelligence"
```

#### Company Blogs
```
site:openai.com/blog OR site:blog.google/technology/ai
```

### Topic Combinations

#### AI + Healthcare
```
"AI" AND "healthcare" OR "medical AI" after:[week_ago]
```

#### AI + Finance
```
"AI" AND "finance" OR "fintech AI" after:[week_ago]
```

#### AI + Ethics
```
"AI ethics" OR "artificial intelligence safety" after:[week_ago]
```

#### AI + Regulation
```
"AI regulation" OR "AI policy" after:[week_ago]
```

---

## Query Optimization Tips

### 1. Start Broad, Then Refine
Begin with general queries, then narrow down based on results:
1. `"AI news today"` → broad overview
2. `"AI product launch"` → specific focus
3. `"OpenAI product launch"` → very specific

### 2. Use Date Filters Consistently
Always include date filters to ensure fresh content:
- Daily briefings: `after:[yesterday]`
- Weekly summaries: `after:[week_ago]`

### 3. Combine Categories for Comprehensive Results
Mix queries from different categories:
- 1-2 general queries
- 1-2 research queries
- 1-2 industry queries
- 1-2 product queries

### 4. Avoid Redundant Terms
Don't combine similar terms:
- ❌ `"AI" AND "artificial intelligence"` (redundant)
- ✅ `"AI" OR "machine learning" OR "deep learning"` (complementary)

### 5. Use Quotes for Exact Phrases
Use quotes when searching for specific phrases:
- ✅ `"large language model"`
- ❌ `large language model` (may return broader results)

### 6. Exclude Irrelevant Topics
Use NOT to filter out unrelated content:
```
"AI news" NOT "crypto" NOT "web3" NOT "blockchain"
```

---

## Example Query Combinations

### Daily Briefing (Comprehensive)
```
Query 1: "AI news today" OR "artificial intelligence breakthrough" after:[yesterday]
Query 2: "AI research paper" OR "machine learning breakthrough" after:[yesterday]
Query 3: "AI startup funding" OR "AI company news" after:[week_ago]
Query 4: "AI product release" OR "new AI tool" after:[yesterday]
```

### Research-Focused
```
Query 1: "AI research paper" OR "machine learning breakthrough" after:[yesterday]
Query 2: arXiv "cs.AI" OR "cs.LG" paper after:[yesterday]
Query 3: "AI breakthrough" OR "research advancement" after:[yesterday]
```

### Industry-Focused
```
Query 1: "AI startup funding" OR "artificial intelligence investment" after:[week_ago]
Query 2: "AI company news" OR "OpenAI news" OR "Google AI" after:[yesterday]
Query 3: "AI acquisition" OR "AI partnership" after:[week_ago]
```

### Product-Focused
```
Query 1: "AI product release" OR "new AI tool" after:[yesterday]
Query 2: "open source AI" OR "AI model release" after:[yesterday]
Query 3: "GPT update" OR "Claude update" OR "Gemini update" after:[yesterday]
```

---

## Query Performance Tips

1. **Limit Results**: Most search tools return 10-15 results by default, which is usually sufficient
2. **Prioritize Recent**: Always use date filters to ensure fresh content
3. **Diversify Sources**: Use queries that return results from different types of sources (news sites, blogs, academic)
4. **Adjust Scope**: If too few results, expand date range or use broader terms
5. **Refine Relevance**: If too many results, add more specific terms or reduce date range
6. **Validate Results**: Always check publication dates to ensure content is truly recent
