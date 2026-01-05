---
name: daily-ai-news
description: "Aggregates and summarizes the latest AI news from multiple sources including AI news websites and web search. Provides concise news briefs with direct links to original articles. Activates when user asks for 'today's AI news', 'AI updates', 'latest AI developments', or mentions wanting a 'daily AI briefing'."
---

# Daily AI News Briefing

> Aggregates the latest AI news from multiple sources and delivers concise summaries with direct links

## When to Use This Skill

Activate this skill when the user:
- Asks for today's AI news or latest AI developments
- Requests a daily AI briefing or updates
- Mentions wanting to know what's happening in AI
- Asks for AI industry news, trends, or breakthroughs
- Wants a summary of recent AI announcements
- Says: "给我今天的AI资讯" (Give me today's AI news)
- Says: "AI有什么新动态" (What's new in AI)

## Workflow Overview

This skill uses a 4-phase workflow to gather, filter, categorize, and present AI news:

```
Phase 1: Information Gathering
  ├─ Direct website fetching (3-5 major AI news sites)
  └─ Web search with date filters
      ↓
Phase 2: Content Filtering
  ├─ Keep: Last 24-48 hours, major announcements
  └─ Remove: Duplicates, minor updates, old content
      ↓
Phase 3: Categorization
  └─ Organize into 5 categories
      ↓
Phase 4: Output Formatting
  └─ Present with links and structure
```

## Phase 1: Information Gathering

### Step 1.1: Fetch from Primary AI News Sources

Use `mcp__web_reader__webReader` to fetch content from 3-5 major AI news websites:

**Recommended Primary Sources** (choose 3-5 per session):
- VentureBeat AI: https://venturebeat.com/category/ai/
- TechCrunch AI: https://techcrunch.com/category/artificial-intelligence/
- The Verge AI: https://www.theverge.com/ai-artificial-intelligence
- MIT Technology Review AI: https://www.technologyreview.com/topic/artificial-intelligence/
- AI News: https://artificialintelligence-news.com/
- AI Hub Today: https://ai.hubtoday.app/

**Parameters**:
- `return_format`: markdown
- `with_images_summary`: false (focus on text content)
- `timeout`: 20 seconds per source

### Step 1.2: Execute Web Search Queries

Use `WebSearch` with date-filtered queries to discover additional news:

**Query Template** (adjust dates dynamically):
```
General: "AI news today" OR "artificial intelligence breakthrough" after:[2025-12-23]
Research: "AI research paper" OR "machine learning breakthrough" after:[2025-12-23]
Industry: "AI startup funding" OR "AI company news" after:[2025-12-23]
Products: "AI application launch" OR "new AI tool" after:[2025-12-23]
```

**Best Practices**:
- Always use current date or yesterday's date in filters
- Execute 2-3 queries across different categories
- Limit to top 10-15 results per query
- Prioritize sources from last 24-48 hours

### Step 1.3: Fetch Full Articles

For the top 10-15 most relevant stories from search results:
- Extract URLs from search results
- Use `mcp__web_reader__webReader` to fetch full article content
- This ensures accurate summarization vs. just using snippets

## Phase 2: Content Filtering

### Filter Criteria

**Keep**:
- News from last 24-48 hours (preferably today)
- Major announcements (product launches, model releases, research breakthroughs)
- Industry developments (funding, partnerships, regulations, acquisitions)
- Technical advances (new models, techniques, benchmarks)
- Significant company updates (OpenAI, Google, Anthropic, etc.)

**Remove**:
- Duplicate stories (same news across multiple sources)
- Minor updates or marketing fluff
- Content older than 3 days unless highly significant
- Non-AI content or tangentially related articles

### Deduplication Strategy

When the same story appears in multiple sources:
- Keep the most comprehensive version
- Note alternative sources in the summary
- Prioritize authoritative sources (company blogs > news aggregators)

## Phase 3: Categorization

Organize news into 5 categories:

### 🔥 Major Announcements
- Product launches (new AI tools, services, features)
- Model releases (GPT updates, Claude features, Gemini capabilities)
- Major company announcements (OpenAI, Google, Anthropic, Microsoft, Meta)

### 🔬 Research & Papers
- Academic breakthroughs
- New research papers from top conferences
- Novel techniques or methodologies
- Benchmark achievements

### 💰 Industry & Business
- Funding rounds and investments
- Mergers and acquisitions
- Partnerships and collaborations
- Market trends and analysis

### 🛠️ Tools & Applications
- New AI tools and frameworks
- Practical AI applications
- Open source releases
- Developer resources

### 🌍 Policy & Ethics
- AI regulations and policies
- Safety and ethics discussions
- Social impact studies
- Government initiatives

## Phase 4: Output Formatting

Use the following template for consistent output:

```markdown
# 📰 Daily AI News Briefing

**Date**: [Current Date, e.g., December 24, 2025]
**Sources**: [X] articles from [Y] sources
**Coverage**: Last 24 hours

---

## 🔥 Major Announcements

### [Headline 1]

**Summary**: [One-sentence overview of the news]

**Key Points**:
- [Important detail 1]
- [Important detail 2]
- [Important detail 3]

**Impact**: [Why this matters - 1 sentence]

📅 **Source**: [Publication Name] • [Publication Date]
🔗 **Link**: [URL to original article]

---

### [Headline 2]

[Same format as above]

---

## 🔬 Research & Papers

### [Headline 3]

[Same format as above]

---

## 💰 Industry & Business

### [Headline 4]

[Same format as above]

---

## 🛠️ Tools & Applications

### [Headline 5]

[Same format as above]

---

## 🌍 Policy & Ethics

### [Headline 6]

[Same format as above]

---

## 🎯 Key Takeaways

1. [The biggest news of the day - 1 sentence]
2. [Second most important development - 1 sentence]
3. [An emerging trend worth watching - 1 sentence]

---

**Generated on**: [Timestamp]
**Next update**: Check back tomorrow for the latest AI news
```

## Customization Options

After providing the initial briefing, offer customization:

### 1. Focus Areas
"Would you like me to focus on specific topics?"
- Research papers only
- Product launches and tools
- Industry news and funding
- Specific companies (OpenAI/Google/Anthropic)
- Technical tutorials and guides

### 2. Depth Level
"How detailed should I go?"
- **Brief**: Headlines only (2-3 bullet points per story)
- **Standard**: Summaries + key points (default)
- **Deep**: Include analysis and implications

### 3. Time Range
"What timeframe?"
- Last 24 hours (default)
- Last 3 days
- Last week
- Custom range

### 4. Format Preference
"How would you like this organized?"
- By category (default)
- Chronological
- By company
- By significance

## Follow-up Interactions

### User: "Tell me more about [story X]"
**Action**: Use `mcp__web_reader__webReader` to fetch the full article, provide detailed summary + analysis

### User: "What are experts saying about [topic Y]?"
**Action**: Search for expert opinions, Twitter reactions, analysis pieces

### User: "Find similar stories to [story Z]"
**Action**: Search related topics, provide comparative summary

### User: "Only show research papers"
**Action**: Filter and reorganize output, exclude industry news

## Quality Standards

### Validation Checklist
- All links are valid and accessible
- No duplicate stories across categories
- All items have timestamps (preferably today)
- Summaries are accurate (not hallucinated)
- Links lead to original sources, not aggregators
- Mix of sources (not all from one publication)
- Balance between hype and substance

### Error Handling
- If `webReader` fails for a URL → Skip and try next source
- If search returns no results → Expand date range or try different query
- If too many results → Increase threshold for significance
- If content is paywalled → Use available excerpt and note limitation

## Examples

### Example 1: Basic Request

**User**: "给我今天的AI资讯"

**AI Response**:
[Executes 4-phase workflow and presents formatted briefing with 5-10 stories across categories]

---

### Example 2: Time-specific Request

**User**: "What's new in AI this week?"

**AI Response**:
[Adjusts date filters to last 7 days, presents weekly summary]

---

### Example 3: Category-specific Request

**User**: "Any updates on AI research?"

**AI Response**:
[Focuses on Research & Papers category, includes recent papers and breakthroughs]

---

### Example 4: Follow-up Deep Dive

**User**: "Tell me more about the GPT-5 announcement"

**AI Response**:
[Fetches full article, provides detailed summary, offers to find expert reactions]

## Additional Resources

For comprehensive lists of news sources, search queries, and output templates, refer to:
- `references/news_sources.md` - Complete database of AI news sources
- `references/search_queries.md` - Search query templates by category
- `references/output_templates.md` - Alternative output format templates
