function required<T>(value: T | null | undefined): T { if (value === null || value === undefined) throw new Error('Missing site element or text.'); return value; }
function query(selector: string, root: ParentNode = document): HTMLElement { const node = root.querySelector(selector); if (!(node instanceof HTMLElement)) throw new Error('Missing site element: ' + selector); return node; }

    const copy = { zh: { html: '<p class="eyebrow">架构优先 · 为 Agent 准备</p><h1>别再让 AI 闭着眼睛写代码。<em>推翻默认流程。</em></h1><p class="lede">古法编程最后的优势是感知架构——Birdview 彻底终结了这个理由。<br>编程的未来只剩两件事：约束与架构。</p>', nav: 'English', title: 'Birdview — 推翻默认编码流程' }, en: { html: '<p class="eyebrow">ARCHITECTURE FIRST · AGENT READY</p><h1>Stop letting AI code blind. <em>Change the flow.</em></h1><p class="lede">The last advantage of coding by hand was architectural awareness—Birdview has eliminated that reason entirely.<br>The future of programming comes down to just two things: constraints and architecture.</p>', nav: '中文', title: 'Birdview — Change the coding flow' } };
    const language = query('#language'); const hero = query('.hero-copy'); let zh = false;
    language.addEventListener('click', () => { zh = !zh; const next = zh ? copy.zh : copy.en; query('.eyebrow', hero).outerHTML = required(next.html.match(/<p[^>]*>[\s\S]*?<\/p>/))[0]; query('h1', hero).outerHTML = required(next.html.match(/<h1>[\s\S]*?<\/h1>/))[0]; query('.lede', hero).outerHTML = required(next.html.match(/<p class="lede">[\s\S]*?<\/p>/))[0]; language.textContent = next.nav; document.title = next.title; document.documentElement.lang = zh ? 'zh-CN' : 'en'; });
  
const installText = {
  en: {
    cta: 'Install Skill', title: 'Install Birdview', intro: 'Choose your agent. Run these commands in PowerShell or a macOS/Linux shell.',
    agent: 'Your agent', requirements: 'Requires Node.js 18+ and npm; your agent or installer may require a newer version. Installs for your user account.',
    step1: 'Install the skill', step2: 'Install dependencies and check', step3: 'Try it in a new agent task',
    limits: 'Doctor checks installation, not activation. Invoke Birdview explicitly: /skills or $birdview in Codex, /birdview in Claude Code. On-demand is the default; mode auto enables automatic activation.',
    guide: 'Full installation and mode guide →', copy: 'Copy', copied: 'Copied.', failed: 'Could not copy. Select the command and copy it manually.',
    prompt: "Use Birdview to show this project's architecture; do not edit code.",
    path: 'If the installer reports a different destination, use that path in step 2. Keep the full skill directory and avoid duplicate installations.',
    deepseek: 'Requires Git and DeepSeek Harness with filesystem skills enabled, not the DeepSeek chat website. Replace $HOME/.dsh if you use DSH_HOME. If Birdview is already installed in ~/.agents/skills, reuse it and use that path in step 2. Do not clone over an existing installation.',
    communityEyebrow: 'COMMUNITY · FEEDBACK', communityTitle: 'Meet other Birdview users.',
    communityBody: 'Get installation help, discuss inaccurate maps, and explore Architecture-first Coding together.',
    communityNumber: 'QQ group: 627760389', communityFeedback: 'Share feedback on GitHub →'
  },
  zh: {
    cta: '安装技能', title: '安装 Birdview', intro: '选择你的 Agent，在 PowerShell 或 macOS/Linux 终端运行以下命令。',
    agent: '选择 Agent', requirements: '需要 Node.js 18+ 和 npm；Agent 或安装器可能要求更高版本。以下为用户级安装。',
    step1: '安装技能', step2: '安装依赖并自检', step3: '在 Agent 的新任务中试用',
    limits: 'Doctor 检查安装，不验证触发。请明确调用：Codex 用 /skills 或 $birdview，Claude Code 用 /birdview。默认按需，mode auto 可开启自动触发。',
    guide: '完整安装与模式指南 →', copy: '复制', copied: '已复制。', failed: '复制失败，请选中命令手动复制。',
    prompt: '用 Birdview 展示这个项目的架构，不修改代码。',
    path: '如果安装器输出了不同目录，请在第 2 步使用实际路径。保留完整技能目录，避免重复安装。',
    deepseek: '需要 Git，以及启用了文件系统技能的 DeepSeek Harness，不适用于 DeepSeek 聊天网站。自定义 DSH_HOME 时替换 $HOME/.dsh。若 ~/.agents/skills 已安装 Birdview，直接复用，并在第 2 步使用该路径。不要覆盖克隆已有安装。',
    communityEyebrow: '用户社区 · 使用反馈', communityTitle: '加入 Birdview 用户交流群',
    communityBody: '交流安装问题、反馈不准确的架构图，一起探索 Architecture-first Coding。',
    communityNumber: 'QQ 群：627760389', communityFeedback: '在 GitHub 分享使用反馈 →'
  }
};
const agentSelect = query('#install-agent');
if (!(agentSelect instanceof HTMLSelectElement)) throw new Error('Invalid agent selector.');
const installGuide = query('#install-guide');
if (!(installGuide instanceof HTMLAnchorElement)) throw new Error('Invalid installation guide link.');
const copyStatus = query('#copy-status');
function updateInstall() {
  const text = installText[document.documentElement.lang.startsWith('zh') ? 'zh' : 'en'];
  const agent = (agentSelect instanceof HTMLSelectElement ? agentSelect.value : '');
  const root = agent === 'deepseek' ? '$HOME/.dsh/skills/birdview'
    : agent === 'claude-code' ? '$HOME/.claude/skills/birdview' : '$HOME/.agents/skills/birdview';
  document.querySelectorAll<HTMLElement>('[data-install-label]').forEach(element => { element.textContent = Object.entries(text).find(([key]) => key === element.dataset.installLabel)?.[1] ?? ''; });
  document.querySelectorAll<HTMLButtonElement>('[data-copy]').forEach(button => {
    button.textContent = text.copy;
    button.setAttribute('aria-label', `${text.copy}: ${query('h3', required(button.parentElement)).textContent}`);
  });
  query('#install-command').textContent = agent === 'deepseek'
    ? `git clone https://github.com/Qiuner/birdview.git "${root}"`
    : `npx skills add Qiuner/birdview --skill birdview --agent ${agent} --global --copy --yes`;
  query('#check-command').textContent = `npm --prefix "${root}" ci\nnode "${root}/scripts/birdview.mjs" doctor`;
  query('#try-prompt').textContent = text.prompt;
  query('#install-path-note').textContent = agent === 'deepseek' ? text.deepseek : text.path;
  installGuide.setAttribute('href', `https://github.com/Qiuner/birdview/blob/main/docs/installation${document.documentElement.lang.startsWith('zh') ? '.zh' : ''}.md`);
  copyStatus.textContent = '';
}
agentSelect.addEventListener('change', updateInstall);
query('#language').addEventListener('click', updateInstall);
document.querySelectorAll<HTMLButtonElement>('[data-copy]').forEach(button => button.addEventListener('click', async () => {
  const command = required(document.getElementById(required(button.dataset.copy))).textContent ?? '';
  try {
    await navigator.clipboard.writeText(command);
    copyStatus.textContent = installText[document.documentElement.lang.startsWith('zh') ? 'zh' : 'en'].copied;
  } catch {
    copyStatus.textContent = installText[document.documentElement.lang.startsWith('zh') ? 'zh' : 'en'].failed;
  }
}));
updateInstall();
