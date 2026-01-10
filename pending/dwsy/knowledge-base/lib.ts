import { readdir, stat, readFile, mkdir, writeFile, copyFile } from "fs/promises";
import { join, resolve, dirname, extname } from "path";
import { fileURLToPath } from "url";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

// 自动定位当前项目的 docs/knowledge 目录
const KNOWLEDGE_ROOT = resolve(process.cwd(), "docs/knowledge");

// 技能模板目录
const TEMPLATES_DIR = resolve(dirname(fileURLToPath(import.meta.url)), "templates");

// 标准目录结构
const REQUIRED_DIRS = [
  "concepts",   // 概念
  "guides",     // 指南
  "decisions",  // 决策
  "external"    // 外部参考
];

// 常见的技术目录和概念映射
const TECHNICAL_PATTERNS = {
  "auth": {
    concepts: ["Authentication", "Authorization", "Session", "Token", "OAuth", "JWT"],
    guides: ["HowToLogin", "PasswordSecurity", "SSOIntegration"],
    category: "auth"
  },
  "api": {
    concepts: ["API", "REST", "GraphQL", "Endpoint", "Middleware"],
    guides: ["APIDesign", "APIVersioning", "ErrorHandling"],
    category: "backend/api"
  },
  "components": {
    concepts: ["Component", "Props", "State", "Lifecycle", "Hooks"],
    guides: ["ComponentDesign", "StateManagement", "PerformanceOptimization"],
    category: "frontend/components"
  },
  "config": {
    concepts: ["Configuration", "Environment", "Settings"],
    guides: ["ConfigManagement", "EnvironmentVariables"],
    category: "common/config"
  },
  "database": {
    concepts: ["Database", "Schema", "Migration", "Query", "Transaction"],
    guides: ["DatabaseDesign", "QueryOptimization", "BackupStrategy"],
    category: "backend/database"
  },
  "utils": {
    concepts: ["Utility", "Helper", "CommonFunctions"],
    guides: ["UtilityFunctions", "CodeReuse"],
    category: "common/utils"
  },
  "services": {
    concepts: ["Service", "BusinessLogic", "ServiceLayer"],
    guides: ["ServiceDesign", "BusinessRules"],
    category: "backend/services"
  },
  "models": {
    concepts: ["Model", "Entity", "DataModel"],
    guides: ["ModelDesign", "DataValidation"],
    category: "backend/models"
  },
  "hooks": {
    concepts: ["Hook", "CustomHook", "SideEffect"],
    guides: ["HookUsage", "CustomHooks"],
    category: "frontend/hooks"
  },
  "store": {
    concepts: ["Store", "State", "Redux", "Context", "StateManagement"],
    guides: ["StateManagement", "ReduxPattern", "ContextAPI"],
    category: "frontend/state"
  },
  "middleware": {
    concepts: ["Middleware", "Interceptor", "Pipeline"],
    guides: ["MiddlewareDesign", "RequestProcessing"],
    category: "backend/middleware"
  },
  "routes": {
    concepts: ["Route", "Router", "Navigation", "URL"],
    guides: ["Routing", "RouteProtection", "Navigation"],
    category: "frontend/routing"
  },
  "tests": {
    concepts: ["Test", "UnitTest", "IntegrationTest", "E2ETest"],
    guides: ["TestingStrategy", "TestDrivenDevelopment"],
    category: "quality/testing"
  },
  "docker": {
    concepts: ["Docker", "Container", "Image", "Dockerfile"],
    guides: ["DockerSetup", "Containerization"],
    category: "infrastructure/docker"
  },
  "deploy": {
    concepts: ["Deployment", "CI", "CD", "Pipeline"],
    guides: ["DeploymentStrategy", "CI/CDSetup"],
    category: "infrastructure/deployment"
  }
};

async function exists(path: string) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

// 1. Init
async function init() {
  console.log(`🧠 Initializing Knowledge Base at: ${KNOWLEDGE_ROOT}\n`);

  if (!(await exists(KNOWLEDGE_ROOT))) {
    await mkdir(KNOWLEDGE_ROOT, { recursive: true });
    console.log(`✅ Created: ${KNOWLEDGE_ROOT}`);
  }

  for (const dir of REQUIRED_DIRS) {
    const path = join(KNOWLEDGE_ROOT, dir);
    if (!(await exists(path))) {
      await mkdir(path, { recursive: true });
      console.log(`✅ Created: ${path}/`);
    }
  }
  
  // Create index if not exists
  const indexPath = join(KNOWLEDGE_ROOT, "index.md");
  if (!(await exists(indexPath))) {
      await writeFile(indexPath, "# Knowledge Base Index\n\nRun `scan` or `index` to populate this file.\n");
      console.log(`✅ Created: index.md`);
  }

  console.log("\n✨ Knowledge Base structure initialized!");
}

// 2. Scan (Simple static analysis + Ace Tool hint)
async function scan() {
  console.log("🔍 Scanning codebase for domain concepts...\n");
  
  const suggestions: string[] = [];
  const filesToCheck: string[] = [];
  
  // 简单的递归文件收集
  async function collectFiles(dir: string) {
      const entries = await readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
          if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === 'dist' || entry.name === 'docs') continue;
          const fullPath = join(dir, entry.name);
          if (entry.isDirectory()) {
              await collectFiles(fullPath);
          } else if (['.ts', '.js', '.py', '.java', '.go', '.rs'].includes(extname(entry.name))) {
              filesToCheck.push(fullPath);
          }
      }
  }
  
  await collectFiles(process.cwd());
  
  // 简单的启发式扫描：查找大写开头的类名/接口名
  const conceptCounts: Record<string, number> = {};
  
  for (const file of filesToCheck.slice(0, 50)) { // 限制扫描文件数以保证速度
      try {
          const content = await readFile(file, 'utf-8');
          // 匹配 class X, interface Y, type Z
          const matches = content.matchAll(/(?:class|interface|type|enum|struct)\s+([A-Z][a-zA-Z0-9]+)/g);
          for (const match of matches) {
              const concept = match[1];
              conceptCounts[concept] = (conceptCounts[concept] || 0) + 1;
          }
      } catch (e) {}
  }
  
  // 排序并取前 20
  const sortedConcepts = Object.entries(conceptCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 20)
      .map(([name]) => name);
      
  const reportPath = join(KNOWLEDGE_ROOT, "suggested_concepts.md");
  let reportContent = "# Suggested Concepts to Document\n\n";
  reportContent += "> Based on static analysis of code definitions (Classes, Interfaces, Types).\n\n";
  
  for (const concept of sortedConcepts) {
      // Check if already documented
      const existsInDocs = await exists(join(KNOWLEDGE_ROOT, "concepts", `${concept}.md`));
      const mark = existsInDocs ? "✅" : "⬜";
      reportContent += `- [${mark}] **${concept}**\n`;
  }
  
  reportContent += "\n\n## Next Steps\n";
  reportContent += "Run `bun ~/.pi/agent/skills/knowledge-base/lib.ts create concept <Name>` to document these.";
  
  await writeFile(reportPath, reportContent);
  console.log(`✅ Scan complete. Suggestions saved to: ${reportPath}`);
  console.log(reportContent);
}

// 3. Create
async function create(type: string, name: string, category?: string) {
    if (!['concept', 'guide', 'decision', 'term'].includes(type)) {
        console.error("❌ Invalid type. Use: concept, guide, decision, or term");
        process.exit(1);
    }

    if (!name) {
        console.error("❌ Please provide a name.");
        process.exit(1);
    }

    // Handle aliases
    const actualType = type === 'term' ? 'concept' : type;

    // Sanitize name for filename
    const filename = name.replace(/[^a-zA-Z0-9\-_]/g, '') + ".md";
    let subDir = actualType + "s"; // concept -> concepts
    let templateName = `${actualType}-template.md`;

    // Build target path with category support
    let targetDir = join(KNOWLEDGE_ROOT, subDir);
    if (category) {
        // Sanitize category path
        const sanitizedCategory = category.replace(/[^a-zA-Z0-9\-_/]/g, '');
        targetDir = join(targetDir, sanitizedCategory);
        if (!(await exists(targetDir))) {
            await mkdir(targetDir, { recursive: true });
            console.log(`✅ Created category directory: ${sanitizedCategory}/`);
        }
    }

    // Decision needs date prefix
    if (type === 'decision') {
        const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
        const safeName = name.replace(/\s+/g, '-');
        const finalFilename = `${date}-${safeName}.md`;

        const targetPath = join(targetDir, finalFilename);
        if (await exists(targetPath)) {
            console.error(`❌ File exists: ${targetPath}`);
            process.exit(1);
        }

        // Prepare content (replace title)
        let content = await readFile(join(TEMPLATES_DIR, templateName), 'utf-8');
        content = content.replace(/\[Decision Title\]/, name);

        await writeFile(targetPath, content);
        console.log(`✅ Created: ${targetPath}`);
        return;
    }

    // Normal files
    const targetPath = join(targetDir, filename);
    if (await exists(targetPath)) {
        console.error(`❌ File exists: ${targetPath}`);
        process.exit(1);
    }

    // Prepare content (replace title)
    let content = await readFile(join(TEMPLATES_DIR, templateName), 'utf-8');
    content = content.replace(/\[Concept Name\]|\[Guide Title\]/, name);

    await writeFile(targetPath, content);
    console.log(`✅ Created: ${targetPath}`);
}

// 4. Index (Generate index.md)
async function generateIndex() {
    console.log("🔄 Generating Knowledge Index...");

    let content = "# Knowledge Base Index\n\n";
    content += "> Generated automatically. Do not edit manually.\n\n";

    for (const dir of REQUIRED_DIRS) {
        const dirPath = join(KNOWLEDGE_ROOT, dir);
        if (!(await exists(dirPath))) continue;

        content += `## ${dir.charAt(0).toUpperCase() + dir.slice(1)}\n`;

        // Recursively collect all markdown files
        const docs: { path: string; title: string; relativePath: string }[] = [];

        async function collectDocs(currentDir: string, relativePath: string) {
            const entries = await readdir(currentDir, { withFileTypes: true });
            for (const entry of entries) {
                if (entry.name.startsWith('.')) continue;

                const fullPath = join(currentDir, entry.name);
                const relPath = join(relativePath, entry.name);

                if (entry.isDirectory()) {
                    await collectDocs(fullPath, relPath);
                } else if (entry.name.endsWith('.md')) {
                    const fileContent = await readFile(fullPath, 'utf-8');
                    const titleMatch = fileContent.match(/^# (.+)$/m);
                    const title = titleMatch ? titleMatch[1] : entry.name;
                    docs.push({ path: fullPath, title, relativePath: relPath });
                }
            }
        }

        await collectDocs(dirPath, '');

        if (docs.length === 0) {
            content += "*No documents yet.*\n\n";
            continue;
        }

        // Group by depth (flat files first, then subdirectories)
        const flatDocs = docs.filter(d => !d.relativePath.includes('/'));
        const nestedDocs = docs.filter(d => d.relativePath.includes('/'));

        // Flat files
        for (const doc of flatDocs) {
            content += `- [${doc.title}](./${dir}/${doc.relativePath})\n`;
        }

        // Nested files with hierarchy
        const groupedByCategory: Record<string, typeof docs> = {};
        for (const doc of nestedDocs) {
            const category = doc.relativePath.split('/')[0];
            if (!groupedByCategory[category]) groupedByCategory[category] = [];
            groupedByCategory[category].push(doc);
        }

        for (const [category, categoryDocs] of Object.entries(groupedByCategory)) {
            content += `\n### ${category}\n`;
            for (const doc of categoryDocs) {
                content += `- [${doc.title}](./${dir}/${doc.relativePath})\n`;
            }
        }

        content += "\n";
    }

    await writeFile(join(KNOWLEDGE_ROOT, "index.md"), content);
    console.log(`✅ Updated: ${join(KNOWLEDGE_ROOT, "index.md")}`);
}

// 5. Glossary
async function generateGlossary() {
    console.log("📖 Generating Glossary...");
    const conceptsDir = join(KNOWLEDGE_ROOT, "concepts");
    
    if (!(await exists(conceptsDir))) {
         console.log("⚠️ No concepts directory found.");
         return;
    }

    const terms: { name: string; path: string; definition: string; category: string }[] = [];

    async function scan(dir: string, relativeCat: string) {
        const entries = await readdir(dir, { withFileTypes: true });
        for (const entry of entries) {
            if (entry.name.startsWith('.')) continue;
            const fullPath = join(dir, entry.name);
            
            if (entry.isDirectory()) {
                await scan(fullPath, join(relativeCat, entry.name));
            } else if (entry.name.endsWith('.md')) {
                 const name = entry.name.replace('.md', '');
                 const content = await readFile(fullPath, 'utf-8');
                 
                 // Extract Definition: Try to find "> Definition" or just the first blockquote
                 let definition = "No definition provided.";
                 
                 // Match: ## Definition \n > content
                 const defMatch = content.match(/## Definition.*?\n> (.*?)(?:\n|$)/i);
                 if (defMatch) {
                     definition = defMatch[1].trim();
                 } else {
                     // Fallback: match any blockquote at the start
                     const quoteMatch = content.match(/^> (.*?)(?:\n|$)/m);
                     if (quoteMatch) definition = quoteMatch[1].trim();
                 }

                 terms.push({
                     name,
                     path: join("concepts", relativeCat, entry.name),
                     definition: definition.length > 100 ? definition.substring(0, 97) + "..." : definition,
                     category: relativeCat || "General"
                 });
            }
        }
    }

    await scan(conceptsDir, "");

    // Sort by name
    terms.sort((a, b) => a.name.localeCompare(b.name));

    // Generate MD
    let content = "# Professional Terminology Glossary (专业术语表)\n\n";
    content += "> Auto-generated from `concepts/` directory. Do not edit manually.\n\n";
    content += "| Term | Category | Definition |\n";
    content += "|------|----------|------------|\n";
    
    for (const term of terms) {
        content += `| [${term.name}](./${term.path}) | \`${term.category}\` | ${term.definition} |\n`;
    }

    const glossaryPath = join(KNOWLEDGE_ROOT, "GLOSSARY.md");
    await writeFile(glossaryPath, content);
    console.log(`✅ Generated: ${glossaryPath}`);
}

// 6. Search
async function search(keyword: string) {
    if (!keyword) {
        console.error("❌ Please provide a keyword.");
        process.exit(1);
    }

    console.log(`🔍 Searching for "${keyword}" in Knowledge Base...\n`);

    async function searchDir(dir: string, basePath: string = "") {
        if (!(await exists(dir))) return;
        const entries = await readdir(dir, { withFileTypes: true });

        for (const entry of entries) {
            if (entry.name.startsWith('.')) continue;

            const fullPath = join(dir, entry.name);
            const relativePath = basePath ? join(basePath, entry.name) : entry.name;

            if (entry.isDirectory()) {
                await searchDir(fullPath, relativePath);
            } else if (entry.name.endsWith('.md')) {
                const content = await readFile(fullPath, 'utf-8');

                if (content.toLowerCase().includes(keyword.toLowerCase())) {
                    console.log(`📄 ${relativePath}`);
                    // Print context
                    const lines = content.split('\n');
                    lines.forEach((line, i) => {
                        if (line.toLowerCase().includes(keyword.toLowerCase())) {
                            console.log(`   Line ${i+1}: ${line.trim().substring(0, 80)}...`);
                        }
                    });
                    console.log("");
                }
            }
        }
    }

    for (const dir of REQUIRED_DIRS) {
        await searchDir(join(KNOWLEDGE_ROOT, dir), dir);
    }
}

// 6. Discover: 基于目录结构发现并生成知识库清单
async function discover() {
    console.log("🔬 Discovering knowledge base structure and generating checklist...\n");

    const discoveries: {
        directory: string;
        type: string;
        suggestedConcepts: string[];
        suggestedGuides: string[];
        category: string;
        confidence: number;
    }[] = [];

    // 扫描项目目录
    async function scanProjectDir(dir: string, depth = 0): Promise<void> {
        if (depth > 5) return; // 限制深度

        const entries = await readdir(dir, { withFileTypes: true });

        for (const entry of entries) {
            if (entry.name.startsWith('.') || entry.name === 'node_modules' || 
                entry.name === 'dist' || entry.name === 'build' || 
                entry.name === 'docs' || entry.name === '.git') continue;

            const fullPath = join(dir, entry.name);
            const dirName = entry.name.toLowerCase();

            // 检查是否匹配已知的技术目录模式
            for (const [pattern, info] of Object.entries(TECHNICAL_PATTERNS)) {
                if (dirName.includes(pattern)) {
                    const confidence = dirName === pattern ? 1.0 : 0.8;
                    
                    // 检查是否已有相关文档
                    const existingConcepts: string[] = [];
                    const existingGuides: string[] = [];

                    async function checkExistingDocs(categoryPath: string) {
                        const conceptsDir = join(KNOWLEDGE_ROOT, "concepts", categoryPath);
                        const guidesDir = join(KNOWLEDGE_ROOT, "guides", categoryPath);

                        if (await exists(conceptsDir)) {
                            const files = await readdir(conceptsDir);
                            existingConcepts.push(...files.filter(f => f.endsWith('.md')).map(f => f.replace('.md', '')));
                        }

                        if (await exists(guidesDir)) {
                            const files = await readdir(guidesDir);
                            existingGuides.push(...files.filter(f => f.endsWith('.md')).map(f => f.replace('.md', '')));
                        }
                    }

                    await checkExistingDocs(info.category);

                    discoveries.push({
                        directory: fullPath.replace(process.cwd() + '/', ''),
                        type: pattern,
                        suggestedConcepts: info.concepts.filter(c => !existingConcepts.some(e => e.toLowerCase().includes(c.toLowerCase()))),
                        suggestedGuides: info.guides.filter(g => !existingGuides.some(e => e.toLowerCase().includes(g.toLowerCase()))),
                        category: info.category,
                        confidence: confidence
                    });
                }
            }

            if (entry.isDirectory()) {
                await scanProjectDir(fullPath, depth + 1);
            }
        }
    }

    await scanProjectDir(process.cwd());

    // 生成发现报告
    const reportPath = join(KNOWLEDGE_ROOT, "discovery_report.md");

    let reportContent = `# Knowledge Base Discovery Report\n\n`;
    reportContent += `> Generated on: ${new Date().toISOString()}\n`;
    reportContent += `> Project: ${process.cwd()}\n\n`;
    reportContent += `> This report analyzes your project structure and suggests knowledge base documentation.\n\n`;

    if (discoveries.length === 0) {
        reportContent += `## 📊 Summary\n\n`;
        reportContent += `No technical directories were detected in this project.\n`;
        reportContent += `\nRecommendation: Review your project structure and identify key domain concepts.\n`;
    } else {
        reportContent += `## 📊 Summary\n\n`;
        reportContent += `- **Total directories discovered**: ${discoveries.length}\n`;
        reportContent += `- **High confidence discoveries**: ${discoveries.filter(d => d.confidence >= 0.9).length}\n`;
        reportContent += `- **Medium confidence discoveries**: ${discoveries.filter(d => d.confidence >= 0.7 && d.confidence < 0.9).length}\n\n`;

        // 按置信度排序
        const sortedDiscoveries = discoveries.sort((a, b) => b.confidence - a.confidence);

        for (const discovery of sortedDiscoveries) {
            const confidenceStars = '⭐'.repeat(Math.round(discovery.confidence * 5));
            reportContent += `---\n\n`;
            reportContent += `## 📁 ${discovery.directory}\n`;
            reportContent += `\n**Type**: ${discovery.type}\n`;
            reportContent += `**Confidence**: ${confidenceStars} (${(discovery.confidence * 100).toFixed(0)}%)\n`;
            reportContent += `**Suggested Category**: \`${discovery.category}\`\n\n`;

            if (discovery.suggestedConcepts.length > 0) {
                reportContent += `### 📚 Suggested Concepts\n\n`;
                for (const concept of discovery.suggestedConcepts) {
                    reportContent += `- [ ] **${concept}**\n`;
                    reportContent += `  \`\`\`bash\n`;
                    reportContent += `  bun ~/.pi/agent/skills/knowledge-base/lib.ts create concept "${concept}" ${discovery.category}\n`;
                    reportContent += `  \`\`\`\n\n`;
                }
            }

            if (discovery.suggestedGuides.length > 0) {
                reportContent += `### 📖 Suggested Guides\n\n`;
                for (const guide of discovery.suggestedGuides) {
                    reportContent += `- [ ] **${guide}**\n`;
                    reportContent += `  \`\`\`bash\n`;
                    reportContent += `  bun ~/.pi/agent/skills/knowledge-base/lib.ts create guide "${guide}" ${discovery.category}\n`;
                    reportContent += `  \`\`\`\n\n`;
                }
            }

            if (discovery.suggestedConcepts.length === 0 && discovery.suggestedGuides.length === 0) {
                reportContent += `✅ **All suggested documents already exist!**\n\n`;
            }
        }

        // 生成快速开始指南
        reportContent += `---\n\n`;
        reportContent += `## 🚀 Quick Start Guide\n\n`;
        reportContent += `Here's how to start documenting your knowledge base:\n\n`;

        const totalSuggestions = sortedDiscoveries.reduce((sum, d) => 
            sum + d.suggestedConcepts.length + d.suggestedGuides.length, 0
        );

        if (totalSuggestions > 0) {
            reportContent += `1. **Generate index**: Run \`bun ~/.pi/agent/skills/knowledge-base/lib.ts index\`\n`;
            reportContent += `2. **Create top-priority concepts**: Start with high-confidence discoveries above\n`;
            reportContent += `3. **Review and customize**: Adapt the suggested categories to fit your project\n`;
            reportContent += `4. **Iterate**: Run discover again after adding documents to see progress\n\n`;
        } else {
            reportContent += `✨ Great job! Your knowledge base is well-documented.\n`;
            reportContent += `\nConsider:\n`;
            reportContent += `- Running \`bun ~/.pi/agent/skills/knowledge-base/lib.ts scan\` to find code-level concepts\n`;
            reportContent += `- Adding domain-specific concepts not covered by standard patterns\n`;
        }

        // 生成进度追踪
        reportContent += `---\n\n`;
        reportContent += `## 📈 Progress Tracking\n\n`;
        
        const totalConcepts = sortedDiscoveries.reduce((sum, d) => sum + d.suggestedConcepts.length, 0);
        const totalGuides = sortedDiscoveries.reduce((sum, d) => sum + d.suggestedGuides.length, 0);
        const progress = totalSuggestions === 0 ? 100 : Math.round(
            ((sortedDiscoveries.reduce((sum, d) => {
                const total = d.suggestedConcepts.length + d.suggestedGuides.length;
                const existing = (d.suggestedConcepts.length === 0 && d.suggestedGuides.length === 0) ? 1 : 0;
                return sum + (total === 0 ? 1 : existing);
            }, 0)) / sortedDiscoveries.length) * 100
        );

        reportContent += `- **Suggested concepts remaining**: ${totalConcepts}\n`;
        reportContent += `- **Suggested guides remaining**: ${totalGuides}\n`;
        reportContent += `- **Estimated completion**: ${progress}%\n\n`;
    }

    await writeFile(reportPath, reportContent);

    console.log(`✅ Discovery complete! Report saved to: ${reportPath}`);
    console.log(`\n📊 Found ${discoveries.length} technical directories`);
    
    const totalSuggestions = discoveries.reduce((sum, d) => 
        sum + d.suggestedConcepts.length + d.suggestedGuides.length, 0
    );
    
    if (totalSuggestions > 0) {
        console.log(`💡 ${totalSuggestions} document suggestions generated`);
        console.log(`\nNext steps:`);
        console.log(`  1. Review the report: ${reportPath}`);
        console.log(`  2. Create suggested documents using the provided commands`);
        console.log(`  3. Run 'index' to update the knowledge base index`);
    } else {
        console.log(`✨ No new suggestions - your knowledge base is comprehensive!`);
    }
}

// Main Dispatcher
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
    case 'init':
        init();
        break;
    case 'scan':
        scan();
        break;
    case 'create':
        create(args[1], args[2], args[3]);
        break;
    case 'index':
        generateIndex();
        break;
    case 'glossary':
        generateGlossary();
        break;
    case 'search':
        search(args[1]);
        break;
    case 'discover':
        discover();
        break;
    default:
        console.log(`
Knowledge Base Manager

Usage:
  init                          Initialize docs/knowledge structure
  scan                          Scan codebase for concepts
  create <type> <name> [cat]    Create new doc (type: concept, guide, decision, term)
                                Optional: category path (e.g., "auth/user")
  index                         Regenerate index.md
  glossary                      Generate GLOSSARY.md (Professional Terminology Table)
  search <keyword>              Search knowledge base
  discover                      Analyze project structure and generate documentation checklist

Examples:
  bun lib.ts init
  bun lib.ts create term "DoubleEntry" accounting
  bun lib.ts create concept "UserAuthentication" auth/user
  bun lib.ts create guide "ErrorHandling" backend
  bun lib.ts create decision "WhyUsePostgres" database
  bun lib.ts index
  bun lib.ts glossary
  bun lib.ts search "auth"
  bun lib.ts discover
        `);
}
