import fetch from 'node-fetch';
import * as cheerio from 'cheerio';
import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import pLimit from 'p-limit';

// 1. Load Environment Variables
const projectRoot = path.resolve(__dirname, '../../');
const envPath = path.join(projectRoot, '.env');

console.log(`Loading .env from: ${envPath}`);
if (fs.existsSync(envPath)) {
  console.log('✅ .env file found');
} else {
  console.error('❌ .env file NOT found');
}

dotenv.config({ path: envPath, override: true });

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const ANTHROPIC_BASE_URL = process.env.ANTHROPIC_BASE_URL;
const MOCK_MODE = process.env.MOCK_MODE === 'true';

// 2. Define Output Paths
const OUTPUT_DIR = path.join(projectRoot, 'outputs');
const POSTS_DIR = path.join(OUTPUT_DIR, 'defou-stanley-posts');

// Ensure directories exist
if (!fs.existsSync(POSTS_DIR)) {
  fs.mkdirSync(POSTS_DIR, { recursive: true });
}

interface HotItem {
  rank: string;
  title: string;
  link: string;
  hot: string;
  source: string;
}

interface Topic {
  title: string;
  reason: string;
  source: string;
  link: string;
}

const TOPHUB_URL = 'https://tophub.today/hot';

// 3. Initialize Anthropic Client
const anthropic = new Anthropic({
  apiKey: ANTHROPIC_API_KEY || 'dummy',
  baseURL: ANTHROPIC_BASE_URL,
});

/**
 * Fetch hot list from TopHub
 */
async function fetchHotList(): Promise<HotItem[]> {
  console.log(`Fetching ${TOPHUB_URL}...`);
  const response = await fetch(TOPHUB_URL, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch tophub: ${response.status} ${response.statusText}`);
  }

  const html = await response.text();
  const $ = cheerio.load(html);
  const items: HotItem[] = [];

  $('.child-item').each((_, element) => {
    const el = $(element);
    const rank = el.find('.left-item span').text().trim();
    const titleLink = el.find('.medium-txt a');
    const title = titleLink.text().trim();
    const link = titleLink.attr('href') || '';
    
    // Some links might be relative
    const fullLink = link.startsWith('http') ? link : `https://tophub.today${link}`;
    
    const smallTxt = el.find('.small-txt').text().trim();
    // smallTxt format: "知乎 ‧ 958万热度"
    const parts = smallTxt.split('‧').map(s => s.trim());
    const source = parts[0] || '';
    const hot = parts[1] || '';

    if (title) {
      items.push({
        rank,
        title,
        link: fullLink,
        source,
        hot
      });
    }
  });

  return items;
}

/**
 * Step 1: Select the top 10 best topics
 */
async function selectBestTopics(items: HotItem[]): Promise<Topic[]> {
  const topItems = items.slice(0, 50); // Analyze top 50 to find the best 10
  const itemsText = topItems.map(item => 
    `${item.rank}. [${item.source}] ${item.title} (Hot: ${item.hot})`
  ).join('\n');

  const prompt = `
You are a viral content scout. Here is a list of current trending topics:

${itemsText}

Your task is to select the top **10** topics that have the highest potential to be adapted into a "Defou x Stanley" style article.
The "Defou x Stanley" style is: Contrarian, deeply insightful, revealing human weaknesses/nature, minimalist, and sharp.
Avoid purely news-reporting topics (e.g., "Earthquake in X"). Look for topics about social issues, relationships, psychology, wealth, or career that allow for deep opinionated commentary.

Return your selection in JSON format as an array of objects:
{
  "topics": [
    {
      "rank": "rank number",
      "reason": "Why this topic is perfect for deep/contrarian analysis"
    },
    ...
  ]
}
`;

  console.log('🤖 Selecting best topics...');
  
  if (MOCK_MODE) {
    return topItems.slice(0, 10).map(item => ({
        title: item.title,
        reason: "Mock selection",
        source: item.source,
        link: item.link
    }));
  }

  const msg = await anthropic.messages.create({
    model: "anthropic/claude-sonnet-4",
    max_tokens: 2000,
    temperature: 0.7,
    system: "You are a content scout.",
    messages: [
      { role: "user", content: prompt }
    ]
  });

  const content = (msg.content[0] as any).text;
  
  // Extract JSON from response
  const jsonMatch = content.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error("Failed to parse JSON from selection response");
  }
  
  const selectionData = JSON.parse(jsonMatch[0]);
  const selectedTopics: Topic[] = [];

  if (selectionData.topics && Array.isArray(selectionData.topics)) {
      for (const t of selectionData.topics) {
          const originalItem = topItems.find(i => i.rank === t.rank);
          if (originalItem) {
              selectedTopics.push({
                  title: originalItem.title,
                  reason: t.reason,
                  source: originalItem.source,
                  link: originalItem.link
              });
          }
      }
  }

  if (selectedTopics.length === 0) {
     console.warn("Could not find selected ranks, falling back to top items.");
     return topItems.slice(0, 10).map(item => ({
        title: item.title,
        reason: "Fallback selection",
        source: item.source,
        link: item.link
     }));
  }

  return selectedTopics;
}

/**
 * Step 2: Generate Content using Defou x Stanley Workflow
 */
async function generateContent(topic: Topic) {
  const prompt = `
You are "Defou x Stanley", a top-tier content expert combining "Deep Structural Thinking" and "Insight into Human Weaknesses".

**User Input (Topic)**: "${topic.title}" (Source: ${topic.source})
**Context/Reasoning**: ${topic.reason}

Please create a content piece following the **Defou x Stanley Workflow**.

### Role & Style
1. **Insightful**: Peel back the layers to reveal the core essence.
2. **Smart Routing**: Match the topic to T1 (Hotspot), T2 (Anti-Chicken Soup), T3 (Roast/Satire), or T4 (Dry Goods).
3. **Minimalist & Sharp**: No fluff. Start with a reversal. Cold, restrained tone.
4. **Structure**: Re-structure scattered thoughts into a logical flow.

### IP Persona
- **Language**: Simplified Chinese. Extremely restrained. One sentence per line. Visual white space.
- **Tone**: Judgment over emotion. Do not please the reader.
- **Content**: Data/Facts > Flowery words. Include one sharp, cruel, life-like metaphor.
- **Values**: Structure > Effort; Choice > Execution; Long-term > Short-term. End with a sense of "powerlessness" or "clarity" regarding human nature/hierarchy.

### Workflow
1. **Routing**: Choose T1-T4.
2. **Drafting**:
   - **Version A (Stanley Style)**: Viral structure, emotional resonance, sharp data, golden sentences. End with 🤣.
   - **Version B (Defou Style)**: Deep cognitive insight. "Many people think... actually the problem is...". Focus on cognitive upgrade.
   - **Version C (Defou x Stanley Combo)**: The Ultimate Style.
     - **Structure**: Stanley's engaging hooks & rhythm (short sentences).
     - **Depth**: Defou's structural analysis & cognitive upgrade.
     - **Goal**: High viral potential AND high long-term value. The "Best of Both Worlds".
3. **Hooks**: Generate 4 hooks (Counter-intuitive, Pain-point, Result-oriented, Suspense).
4. **Scoring**: Evaluate Curiosity, Resonance, Clarity, Shareability.

### Output Format (Markdown)

# 🚀 Defou x Stanley Content Generation

## 1. Routing & Strategy
* **Topic**: ${topic.title}
* **Matched Template**: [T1/T2/T3/T4]
* **Angle**: [Selected Angle]
* **Reason**: [Why this angle?]

---

## 2. Content Drafting

### 🔥 Version A: Stanley Style (Viral)

> **Hooks**
> * [Hook 1]...

**Body:**

[Content here...]

**Score:** [X]/100

---

### 🧠 Version B: Defou Style (Deep Insight)

> **Hooks**
> * [Hook 1]...

**Body:**

[Content here...]

**Score:** [X]/100

---

### 🌟 Version C: Defou x Stanley Combo (The Ultimate)

> **Hooks**
> * [Hook 1]...

**Body:**

[Content here...]

**Score:** [X]/100

---

## 3. Publishing Advice
* **Time**: [Time]
* **Reason**: [Reason]
`;

  console.log(`🤖 Generating content for topic: "${topic.title}"...`);

  const msg = await anthropic.messages.create({
    model: "anthropic/claude-sonnet-4",
    max_tokens: 4000,
    temperature: 0.7,
    system: "You are Defou x Stanley, a viral content expert.",
    messages: [
      { role: "user", content: prompt }
    ]
  });

  return (msg.content[0] as any).text;
}

/**
 * Main execution
 */
async function run() {
  try {
    // 1. Fetch Trends
    const items = await fetchHotList();
    console.log(`✅ Fetched ${items.length} items.`);

    // 2. Select Topics (Now selecting 10)
    const selectedTopics = await selectBestTopics(items);
    console.log(`🎯 Selected ${selectedTopics.length} Topics:`);
    selectedTopics.forEach((t, i) => console.log(`   ${i + 1}. ${t.title}`));

    // 3. Generate Content in parallel (limited concurrency)
    // Using p-limit to prevent rate limiting (e.g., max 2 concurrent requests)
    const limit = pLimit(2);
    
    const tasks = selectedTopics.map(topic => {
      return limit(async () => {
        try {
            const content = await generateContent(topic);
            
            // 4. Save Output
            const dateStr = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            const safeTitle = topic.title.replace(/[^a-z0-9\u4e00-\u9fa5]/gi, '_').slice(0, 20);
            const filename = `post_${dateStr}_${safeTitle}.md`;
            const filepath = path.join(POSTS_DIR, filename);
            
            const finalContent = `
<!--
Topic: ${topic.title}
Source: ${topic.source}
Link: ${topic.link}
Reason: ${topic.reason}
Generated: ${new Date().toLocaleString()}
-->

${content}
`;

            fs.writeFileSync(filepath, finalContent);
            console.log(`✅ Saved content to: ${filepath}`);
        } catch (err) {
            console.error(`❌ Failed to generate content for "${topic.title}":`, err);
        }
      });
    });

    await Promise.all(tasks);
    console.log('🎉 All tasks completed!');

  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  run();
}
