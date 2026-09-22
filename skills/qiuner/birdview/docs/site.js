// Generated from src/site/main.mts. Do not edit directly.
"use strict";
(() => {
  // src/site/main.mts
  function required(value) {
    if (value === null || value === void 0) throw new Error("Missing site element or text.");
    return value;
  }
  function query(selector, root = document) {
    const node = root.querySelector(selector);
    if (!(node instanceof HTMLElement)) throw new Error("Missing site element: " + selector);
    return node;
  }
  var copy = { zh: { html: '<p class="eyebrow">\u67B6\u6784\u4F18\u5148 \xB7 \u4E3A Agent \u51C6\u5907</p><h1>\u522B\u518D\u8BA9 AI \u95ED\u7740\u773C\u775B\u5199\u4EE3\u7801\u3002<em>\u63A8\u7FFB\u9ED8\u8BA4\u6D41\u7A0B\u3002</em></h1><p class="lede">\u53E4\u6CD5\u7F16\u7A0B\u6700\u540E\u7684\u4F18\u52BF\u662F\u611F\u77E5\u67B6\u6784\u2014\u2014Birdview \u5F7B\u5E95\u7EC8\u7ED3\u4E86\u8FD9\u4E2A\u7406\u7531\u3002<br>\u7F16\u7A0B\u7684\u672A\u6765\u53EA\u5269\u4E24\u4EF6\u4E8B\uFF1A\u7EA6\u675F\u4E0E\u67B6\u6784\u3002</p>', nav: "English", title: "Birdview \u2014 \u63A8\u7FFB\u9ED8\u8BA4\u7F16\u7801\u6D41\u7A0B" }, en: { html: '<p class="eyebrow">ARCHITECTURE FIRST \xB7 AGENT READY</p><h1>Stop letting AI code blind. <em>Change the flow.</em></h1><p class="lede">The last advantage of coding by hand was architectural awareness\u2014Birdview has eliminated that reason entirely.<br>The future of programming comes down to just two things: constraints and architecture.</p>', nav: "\u4E2D\u6587", title: "Birdview \u2014 Change the coding flow" } };
  var language = query("#language");
  var hero = query(".hero-copy");
  var zh = false;
  language.addEventListener("click", () => {
    zh = !zh;
    const next = zh ? copy.zh : copy.en;
    query(".eyebrow", hero).outerHTML = required(next.html.match(/<p[^>]*>[\s\S]*?<\/p>/))[0];
    query("h1", hero).outerHTML = required(next.html.match(/<h1>[\s\S]*?<\/h1>/))[0];
    query(".lede", hero).outerHTML = required(next.html.match(/<p class="lede">[\s\S]*?<\/p>/))[0];
    language.textContent = next.nav;
    document.title = next.title;
    document.documentElement.lang = zh ? "zh-CN" : "en";
  });
  var installText = {
    en: {
      cta: "Install Skill",
      title: "Install Birdview",
      intro: "Choose your agent. Run these commands in PowerShell or a macOS/Linux shell.",
      agent: "Your agent",
      requirements: "Requires Node.js 18+ and npm; your agent or installer may require a newer version. Installs for your user account.",
      step1: "Install the skill",
      step2: "Install dependencies and check",
      step3: "Try it in a new agent task",
      limits: "Doctor checks installation, not activation. Invoke Birdview explicitly: /skills or $birdview in Codex, /birdview in Claude Code. On-demand is the default; mode auto enables automatic activation.",
      guide: "Full installation and mode guide \u2192",
      copy: "Copy",
      copied: "Copied.",
      failed: "Could not copy. Select the command and copy it manually.",
      prompt: "Use Birdview to show this project's architecture; do not edit code.",
      path: "If the installer reports a different destination, use that path in step 2. Keep the full skill directory and avoid duplicate installations.",
      deepseek: "Requires Git and DeepSeek Harness with filesystem skills enabled, not the DeepSeek chat website. Replace $HOME/.dsh if you use DSH_HOME. If Birdview is already installed in ~/.agents/skills, reuse it and use that path in step 2. Do not clone over an existing installation.",
      communityEyebrow: "COMMUNITY \xB7 FEEDBACK",
      communityTitle: "Meet other Birdview users.",
      communityBody: "Get installation help, discuss inaccurate maps, and explore Architecture-first Coding together.",
      communityNumber: "QQ group: 627760389",
      communityFeedback: "Share feedback on GitHub \u2192"
    },
    zh: {
      cta: "\u5B89\u88C5\u6280\u80FD",
      title: "\u5B89\u88C5 Birdview",
      intro: "\u9009\u62E9\u4F60\u7684 Agent\uFF0C\u5728 PowerShell \u6216 macOS/Linux \u7EC8\u7AEF\u8FD0\u884C\u4EE5\u4E0B\u547D\u4EE4\u3002",
      agent: "\u9009\u62E9 Agent",
      requirements: "\u9700\u8981 Node.js 18+ \u548C npm\uFF1BAgent \u6216\u5B89\u88C5\u5668\u53EF\u80FD\u8981\u6C42\u66F4\u9AD8\u7248\u672C\u3002\u4EE5\u4E0B\u4E3A\u7528\u6237\u7EA7\u5B89\u88C5\u3002",
      step1: "\u5B89\u88C5\u6280\u80FD",
      step2: "\u5B89\u88C5\u4F9D\u8D56\u5E76\u81EA\u68C0",
      step3: "\u5728 Agent \u7684\u65B0\u4EFB\u52A1\u4E2D\u8BD5\u7528",
      limits: "Doctor \u68C0\u67E5\u5B89\u88C5\uFF0C\u4E0D\u9A8C\u8BC1\u89E6\u53D1\u3002\u8BF7\u660E\u786E\u8C03\u7528\uFF1ACodex \u7528 /skills \u6216 $birdview\uFF0CClaude Code \u7528 /birdview\u3002\u9ED8\u8BA4\u6309\u9700\uFF0Cmode auto \u53EF\u5F00\u542F\u81EA\u52A8\u89E6\u53D1\u3002",
      guide: "\u5B8C\u6574\u5B89\u88C5\u4E0E\u6A21\u5F0F\u6307\u5357 \u2192",
      copy: "\u590D\u5236",
      copied: "\u5DF2\u590D\u5236\u3002",
      failed: "\u590D\u5236\u5931\u8D25\uFF0C\u8BF7\u9009\u4E2D\u547D\u4EE4\u624B\u52A8\u590D\u5236\u3002",
      prompt: "\u7528 Birdview \u5C55\u793A\u8FD9\u4E2A\u9879\u76EE\u7684\u67B6\u6784\uFF0C\u4E0D\u4FEE\u6539\u4EE3\u7801\u3002",
      path: "\u5982\u679C\u5B89\u88C5\u5668\u8F93\u51FA\u4E86\u4E0D\u540C\u76EE\u5F55\uFF0C\u8BF7\u5728\u7B2C 2 \u6B65\u4F7F\u7528\u5B9E\u9645\u8DEF\u5F84\u3002\u4FDD\u7559\u5B8C\u6574\u6280\u80FD\u76EE\u5F55\uFF0C\u907F\u514D\u91CD\u590D\u5B89\u88C5\u3002",
      deepseek: "\u9700\u8981 Git\uFF0C\u4EE5\u53CA\u542F\u7528\u4E86\u6587\u4EF6\u7CFB\u7EDF\u6280\u80FD\u7684 DeepSeek Harness\uFF0C\u4E0D\u9002\u7528\u4E8E DeepSeek \u804A\u5929\u7F51\u7AD9\u3002\u81EA\u5B9A\u4E49 DSH_HOME \u65F6\u66FF\u6362 $HOME/.dsh\u3002\u82E5 ~/.agents/skills \u5DF2\u5B89\u88C5 Birdview\uFF0C\u76F4\u63A5\u590D\u7528\uFF0C\u5E76\u5728\u7B2C 2 \u6B65\u4F7F\u7528\u8BE5\u8DEF\u5F84\u3002\u4E0D\u8981\u8986\u76D6\u514B\u9686\u5DF2\u6709\u5B89\u88C5\u3002",
      communityEyebrow: "\u7528\u6237\u793E\u533A \xB7 \u4F7F\u7528\u53CD\u9988",
      communityTitle: "\u52A0\u5165 Birdview \u7528\u6237\u4EA4\u6D41\u7FA4",
      communityBody: "\u4EA4\u6D41\u5B89\u88C5\u95EE\u9898\u3001\u53CD\u9988\u4E0D\u51C6\u786E\u7684\u67B6\u6784\u56FE\uFF0C\u4E00\u8D77\u63A2\u7D22 Architecture-first Coding\u3002",
      communityNumber: "QQ \u7FA4\uFF1A627760389",
      communityFeedback: "\u5728 GitHub \u5206\u4EAB\u4F7F\u7528\u53CD\u9988 \u2192"
    }
  };
  var agentSelect = query("#install-agent");
  if (!(agentSelect instanceof HTMLSelectElement)) throw new Error("Invalid agent selector.");
  var installGuide = query("#install-guide");
  if (!(installGuide instanceof HTMLAnchorElement)) throw new Error("Invalid installation guide link.");
  var copyStatus = query("#copy-status");
  function updateInstall() {
    const text = installText[document.documentElement.lang.startsWith("zh") ? "zh" : "en"];
    const agent = agentSelect instanceof HTMLSelectElement ? agentSelect.value : "";
    const root = agent === "deepseek" ? "$HOME/.dsh/skills/birdview" : agent === "claude-code" ? "$HOME/.claude/skills/birdview" : "$HOME/.agents/skills/birdview";
    document.querySelectorAll("[data-install-label]").forEach((element) => {
      element.textContent = Object.entries(text).find(([key]) => key === element.dataset.installLabel)?.[1] ?? "";
    });
    document.querySelectorAll("[data-copy]").forEach((button) => {
      button.textContent = text.copy;
      button.setAttribute("aria-label", `${text.copy}: ${query("h3", required(button.parentElement)).textContent}`);
    });
    query("#install-command").textContent = agent === "deepseek" ? `git clone https://github.com/Qiuner/birdview.git "${root}"` : `npx skills add Qiuner/birdview --skill birdview --agent ${agent} --global --copy --yes`;
    query("#check-command").textContent = `npm --prefix "${root}" ci
node "${root}/scripts/birdview.mjs" doctor`;
    query("#try-prompt").textContent = text.prompt;
    query("#install-path-note").textContent = agent === "deepseek" ? text.deepseek : text.path;
    installGuide.setAttribute("href", `https://github.com/Qiuner/birdview/blob/main/docs/installation${document.documentElement.lang.startsWith("zh") ? ".zh" : ""}.md`);
    copyStatus.textContent = "";
  }
  agentSelect.addEventListener("change", updateInstall);
  query("#language").addEventListener("click", updateInstall);
  document.querySelectorAll("[data-copy]").forEach((button) => button.addEventListener("click", async () => {
    const command = required(document.getElementById(required(button.dataset.copy))).textContent ?? "";
    try {
      await navigator.clipboard.writeText(command);
      copyStatus.textContent = installText[document.documentElement.lang.startsWith("zh") ? "zh" : "en"].copied;
    } catch {
      copyStatus.textContent = installText[document.documentElement.lang.startsWith("zh") ? "zh" : "en"].failed;
    }
  }));
  updateInstall();
})();
