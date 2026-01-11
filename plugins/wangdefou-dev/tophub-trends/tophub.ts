import fetch from 'node-fetch';
import * as cheerio from 'cheerio';
import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

// 1. Load Environment Variables
// Adjusted path to point to defou-workflow-agent root
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
const TRENDS_DIR = path.join(OUTPUT_DIR, 'trends');

// Ensure directories exist
if (!fs.existsSync(TRENDS_DIR)) {
  fs.mkdirSync(TRENDS_DIR, { recursive: true });
}

interface HotItem {
  rank: string;
  title: string;
  link: string;
  hot: string;
  source: string;
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
export async function fetchHotList(): Promise<HotItem[]> {
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
 * Analyze the list using Claude
 */
export async function analyzeHotList(items: HotItem[]): Promise<string> {
  const topItems = items.slice(0, 30); // Analyze top 30 items
  const itemsText = topItems.map(item => 
    `${item.rank}. [${item.source}] ${item.title} (Hot: ${item.hot}) - Link: ${item.link}`
  ).join('\n');

  const prompt = `
You are a content strategy expert. Here is a list of current trending topics from TopHub (Hot List):

${itemsText}

Please perform the following tasks:
1. **Analyze Traffic Potential**: Identify which of these topics have the highest potential for viral traffic *right now*. Look for topics that arouse strong curiosity, controversy, or urgency.
2. **Topic Suggestions**: Based on the high-potential topics, suggest 5 specific content angles/titles that a creator could use.
3. **Format**: Output your response in Markdown.

For the suggestions, use this format:
- **Topic**: [Original Topic Title]
- **Angle**: [Proposed Content Angle]
- **Why it works**: [Brief explanation of traffic potential]
`;

  console.log('🤖 Analyzing hot list with Claude...');
  
  if (MOCK_MODE) {
    return `# Mock Analysis\n\n- Mock Suggestion 1\n- Mock Suggestion 2`;
  }

  const msg = await anthropic.messages.create({
    model: "anthropic/claude-sonnet-4",
    max_tokens: 4000,
    temperature: 0.7,
    system: "You are an expert content strategist and trend analyst.",
    messages: [
      { role: "user", content: prompt }
    ]
  });

  return (msg.content[0] as any).text;
}

/**
 * Main execution function
 */
export async function run() {
  try {
    // 1. Fetch
    const items = await fetchHotList();
    console.log(`✅ Fetched ${items.length} items.`);

    // 2. Save Raw Data
    const dateStr = new Date().toISOString().replace(/[:.]/g, '-');
    const rawFilename = `tophub_hot_${dateStr}.json`;
    const rawPath = path.join(TRENDS_DIR, rawFilename);
    
    fs.writeFileSync(rawPath, JSON.stringify(items, null, 2));
    console.log(`✅ Saved raw data to ${rawPath}`);

    // 3. Analyze
    const report = await analyzeHotList(items);

    // 4. Save Report
    const reportFilename = `tophub_analysis_${dateStr}.md`;
    const reportPath = path.join(TRENDS_DIR, reportFilename);
    
    const finalContent = `# TopHub Hot List Analysis\n> Generated at: ${new Date().toLocaleString()}\n> Source Data: [${rawFilename}](./${rawFilename})\n\n${report}`;
    
    fs.writeFileSync(reportPath, finalContent);
    console.log(`✅ Saved analysis report to ${reportPath}`);
    
    return reportPath;

  } catch (error) {
    console.error('❌ Error running TopHub skill:', error);
    process.exit(1);
  }
}

// Allow running directly
if (require.main === module) {
  run();
}
