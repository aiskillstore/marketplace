import { stat, mkdir, readFile, writeFile } from "fs/promises";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = join(__dirname, "../templates");

async function exists(path: string): Promise<boolean> {
  try { await stat(path); return true; } catch { return false; }
}

function getCurrentDateString(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}${month}${day}`;
}

function getISODateString(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

function replace(content: string, date: string, desc: string, cat?: string) {
  return content.replace(/{{date}}/g, date).replace(/{{description}}/g, desc).replace(/{{category}}/g, cat || "general");
}

async function readTemplate(name: string) {
  const paths = [join(TEMPLATES_DIR, `${name}-updated.md`), join(TEMPLATES_DIR, `${name}.md`)];
  for (const p of paths) {
    if (await exists(p)) return await readFile(p, "utf-8");
  }
  throw new Error(`Template ${name} not found`);
}

export async function createIssue(description: string, category?: string) {
  if (!description) throw new Error("Description required");

  const date = getCurrentDateString();
  const filename = `${date}-${description}.md`;
  let targetDir = join(process.cwd(), "docs", "issues");
  if (category) {
    targetDir = join(targetDir, category);
    await mkdir(targetDir, { recursive: true });
  }
  const targetPath = join(targetDir, filename);

  if (await exists(targetPath)) throw new Error(`File exists: ${targetPath}`);

  const template = await readTemplate("issue-template");
  await writeFile(targetPath, replace(template, getISODateString(), description, category));

  console.log(`✅ Created issue: ${targetPath}`);
}

export async function createPR(description: string, category?: string) {
  if (!description) throw new Error("Description required");

  const date = getCurrentDateString();
  const filename = `${date}-${description}.md`;
  let targetDir = join(process.cwd(), "docs", "pr");
  if (category) {
    targetDir = join(targetDir, category);
    await mkdir(targetDir, { recursive: true });
  }
  const targetPath = join(targetDir, filename);

  if (await exists(targetPath)) throw new Error(`File exists: ${targetPath}`);

  const template = await readTemplate("pr-template");
  await writeFile(targetPath, replace(template, getISODateString(), description, category));

  console.log(`✅ Created PR: ${targetPath}`);
}
