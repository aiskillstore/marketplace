const fs = require("fs");

const reportPath = "/tmp/skill-report-ai-image-generation-6d10e5e6.json";
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));

report.skill.description =
  "Generate and edit images through RunComfy, selecting suitable models and preparing model-specific CLI requests.";
report.skill.summary =
  "Route image requests to suitable RunComfy models and prepare generation or editing commands.";
report.skill.category = "design";
report.skill.tags = [
  "image-generation",
  "image-editing",
  "runcomfy",
  "text-to-image",
  "generative-ai",
];

const confirmedCommandLines = new Map([
  [
    31,
    "The enclosed setup block directs users to install or execute an npm package, authenticate, and invoke RunComfy. These are intentional external commands with package, network, and credential exposure.",
  ],
  [
    51,
    "The enclosed command uses npx to fetch and execute a skill installer with global scope. This is intentional external command execution and carries normal package supply-chain risk.",
  ],
  [
    192,
    "The enclosed example executes the RunComfy CLI, sends a prompt to a remote model, and writes downloaded output. This is an intended external command with network and filesystem effects.",
  ],
  [
    205,
    "The enclosed example executes the RunComfy CLI, sends a prompt to a remote model, and writes downloaded output. This is an intended external command with network and filesystem effects.",
  ],
  [
    236,
    "The enclosed example executes the RunComfy CLI, sends a prompt to a remote model, and writes downloaded output. This is an intended external command with network and filesystem effects.",
  ],
  [
    247,
    "The enclosed example executes the RunComfy CLI, sends a prompt to a remote model, and writes downloaded output. This is an intended external command with network and filesystem effects.",
  ],
  [
    287,
    "The enclosed example executes the RunComfy CLI, sends a prompt to a remote model, and writes downloaded output. This is an intended external command with network and filesystem effects.",
  ],
  [
    295,
    "The enclosed example executes the RunComfy CLI, sends a prompt to a remote model, and writes downloaded output. This is an intended external command with network and filesystem effects.",
  ],
  [
    321,
    "The enclosed example executes the RunComfy CLI, sends a prompt to a remote model, and writes downloaded output. This is an intended external command with network and filesystem effects.",
  ],
  [
    360,
    "The enclosed edit example executes RunComfy with a remote image reference and writes output locally. This is intentional external command execution with network and filesystem effects.",
  ],
  [
    373,
    "The enclosed edit example executes RunComfy with a remote image reference and writes output locally. This is intentional external command execution with network and filesystem effects.",
  ],
  [
    387,
    "The enclosed edit example executes RunComfy with a remote image reference and writes output locally. This is intentional external command execution with network and filesystem effects.",
  ],
  [
    475,
    "This line states that the skill invokes RunComfy, posts request data, polls a remote service, and downloads results. External command execution is an intended operational capability.",
  ],
  [
    479,
    "This line instructs the operator to install or execute the RunComfy npm package. The package-manager source is identified, but executing third-party packages remains a real supply-chain risk.",
  ],
  [
    488,
    "The declared Bash scope authorizes all RunComfy subcommands, confirming intentional external command execution. The scope is limited to one CLI, but that CLI can use network and filesystem resources.",
  ],
]);

report.security_audit.finding_verdicts =
  report.security_audit.static_findings.map((finding) => {
    const { id, category, line_start: line } = finding;

    if (category === "external_commands") {
      if (confirmedCommandLines.has(line)) {
        return {
          id,
          verdict: "confirmed",
          confidence: 0.97,
          reason: confirmedCommandLines.get(line),
          severity: "medium",
        };
      }

      if (
        id.endsWith(":shell-command-substitution") ||
        id.endsWith(":template-literal-with-command-substitution")
      ) {
        return {
          id,
          verdict: "false_positive",
          confidence: 0.99,
          reason:
            "The command-substitution syntax is quoted as a defensive example in the security guidance. This line does not execute the syntax.",
        };
      }

      return {
        id,
        verdict: "false_positive",
        confidence: 0.99,
        reason:
          "The matched backticks are Markdown code formatting or fence delimiters, not Ruby backtick execution or shell substitution. This location does not itself execute a command.",
      };
    }

    if (category === "network") {
      if ([364, 377, 391].includes(line)) {
        return {
          id,
          verdict: "false_positive",
          confidence: 0.99,
          reason:
            "The value is an illustrative HTTPS placeholder containing an ellipsis, not a hardcoded destination. It cannot identify or contact a real host as written.",
        };
      }

      return {
        id,
        verdict: "false_positive",
        confidence: 0.98,
        reason:
          "This is a visible Markdown link or homepage reference for RunComfy documentation, model catalogs, or related skills. The link does not automatically issue a request or transmit user data.",
      };
    }

    if (category === "filesystem" && finding.pattern === "Path traversal sequence") {
      return {
        id,
        verdict: "false_positive",
        confidence: 0.99,
        reason:
          "The three dots occur inside an illustrative HTTPS placeholder. They are not a ../ path segment and do not perform local path traversal.",
      };
    }

    if (category === "filesystem") {
      return {
        id,
        verdict: "false_positive",
        confidence: 0.98,
        reason:
          "The line documents expected token storage in the user's XDG configuration directory with mode 0600. It neither traverses paths nor accesses an unrelated hidden file.",
      };
    }

    if (category === "blocker") {
      return {
        id,
        verdict: "false_positive",
        confidence: 0.99,
        reason:
          "The phrase is a model-selection limitation describing when to avoid a generation model. It performs no host, account, network, or environment reconnaissance.",
      };
    }

    return {
      id,
      verdict: "confirmed",
      confidence: 0.4,
      reason:
        "The static category could not be resolved from the documented context, so the finding is retained with low confidence.",
    };
  });

report.security_audit.semantic_findings = [
  {
    title: "Unsafe shell construction for user-derived prompts",
    description:
      "The skill claims prompt content has no shell-injection surface, but examples place JSON inside shell quotes. An unescaped apostrophe can terminate quoting before RunComfy receives the argument.",
    severity: "high",
    locations: [
      {
        file: "SKILL.md",
        line_start: 42,
        line_end: 44,
      },
      {
        file: "SKILL.md",
        line_start: 481,
        line_end: 481,
      },
    ],
    confidence: 0.92,
    confidence_reasoning:
      "The examples use a shell command with single-quoted JSON, while line 481 explicitly claims quotes cannot create injection. Shell parsing occurs before the CLI receives its argument.",
  },
  {
    title: "User content is processed by a third-party service",
    description:
      "RunComfy receives prompt bodies and reference URLs, polls remote jobs, and returns generated files. Sensitive prompts or signed reference URLs therefore leave the local environment.",
    severity: "medium",
    locations: [
      {
        file: "SKILL.md",
        line_start: 475,
        line_end: 475,
      },
      {
        file: "SKILL.md",
        line_start: 482,
        line_end: 486,
      },
    ],
    confidence: 0.98,
    confidence_reasoning:
      "The source explicitly states that the CLI posts request bodies and that RunComfy servers fetch references and web results.",
  },
];

report.security_audit.analysis_status = "ok";
report.security_audit.summary =
  "Most alerts are false positives from Markdown syntax, documentation links, URL placeholders, and model comparison text. The skill intentionally runs external packages and RunComfy commands. User-derived shell arguments need robust escaping, and prompts or references leave the local environment.";
report.security_audit.remediation = [
  {
    issue: "User-derived prompt text is shown inside shell-quoted JSON.",
    suggestion:
      "Serialize input safely and pass it through an argv-based process API. Otherwise, apply rigorous shell escaping before every invocation and remove the no-injection claim.",
    severity: "high",
  },
  {
    issue: "Prompts and reference URLs are sent to RunComfy and upstream models.",
    suggestion:
      "Require confirmation before sending sensitive content. Explain vendor retention, reference fetching, and web-grounding behavior before execution.",
    severity: "medium",
  },
  {
    issue: "Setup examples execute an unpinned npm package.",
    suggestion:
      "Pin the RunComfy CLI to a reviewed version and require user confirmation before npm or npx installation.",
    severity: "medium",
  },
];

report.content = {
  user_title: "Generate Images with the Right RunComfy Model",
  value_statement:
    "Choosing an image model and its parameters is difficult. This skill routes each request to a suitable RunComfy model and prepares the generation command.",
  seo_keywords: [
    "Claude",
    "Codex",
    "Claude Code",
    "AI image generation",
    "text to image",
    "image editing",
    "RunComfy",
    "FLUX image",
    "GPT Image",
    "Nano Banana",
  ],
  actual_capabilities: [
    "Selects image models based on speed, photorealism, typography, editing, and open-weight requirements.",
    "Prepares text-to-image requests for FLUX, GPT Image, Nano Banana, Seedream, Wan, Qwen, and other models.",
    "Prepares image-editing requests with identity preservation, text replacement, and focused change instructions.",
    "Applies documented size, resolution, seed, image count, and reference limits for supported routes.",
    "Provides model-specific prompting guidance for portraits, posters, storyboards, product images, and multilingual text.",
    "Runs generation through the RunComfy CLI and saves returned images in the selected output directory.",
  ],
  limitations: [
    "Requires the RunComfy CLI, valid authentication, internet access, and access to paid or available model endpoints.",
    "Prompts and reference URLs are processed by RunComfy and upstream model providers.",
    "Model availability, prices, schemas, and output quality can change after this skill is published.",
    "Mask-driven inpainting, controlled outpainting, and broad batch editing require a separate image-editing skill.",
  ],
  use_cases: [
    {
      title: "Create campaign artwork",
      description:
        "Select a model for exact headlines, brand layouts, or polished product visuals and prepare the matching request.",
      target_user: "Marketing designer",
    },
    {
      title: "Produce rapid concepts",
      description:
        "Generate low-resolution variants for storyboards, moodboards, and early creative review before requesting final output.",
      target_user: "Creative director",
    },
    {
      title: "Automate image workflows",
      description:
        "Choose reproducible model parameters and output settings for scripts, content pipelines, or repeated asset generation.",
      target_user: "Application developer",
    },
  ],
  prompt_templates: [
    {
      title: "Generate a simple image",
      prompt:
        "Create an image of [subject] in [setting]. Use a [style] look, [lighting], and a [aspect ratio] composition.",
      scenario: "Begin with one clear text-to-image request.",
    },
    {
      title: "Create a poster with text",
      prompt:
        "Create a [format] poster for [product]. The headline must read exactly \"[headline]\" in [font style]. Use [colors] and [layout].",
      scenario: "Choose a model that handles precise typography.",
    },
    {
      title: "Edit a reference image",
      prompt:
        "Edit [reference URL]. Preserve [identity, pose, or layout]. Change only [target element] to [new appearance]. Keep all other details unchanged.",
      scenario: "Make a controlled image-to-image change.",
    },
    {
      title: "Plan a multi-stage campaign",
      prompt:
        "Create [count] draft concepts for [campaign]. Compare suitable models, generate economical drafts, select one direction, then prepare a final high-resolution version.",
      scenario: "Coordinate model selection, iteration, and final delivery.",
    },
  ],
  output_examples: [
    {
      input:
        "Create a wide photoreal product image of a ceramic mug in warm morning light.",
      output: [
        "Selected FLUX 2 Klein 9B for a polished general-purpose image.",
        "Prepared a wide final-quality generation with explicit subject and lighting details.",
        "Saved returned images in the selected output folder.",
      ],
    },
    {
      input:
        "Design a launch poster whose headline reads exactly \"AURORA Spring 2026\".",
      output: [
        "Selected GPT Image 2 for precise headline rendering and layout control.",
        "Prepared a landscape poster request with the headline quoted exactly.",
      ],
    },
    {
      input:
        "Keep the person unchanged and replace the background with a rainy city street.",
      output: [
        "Selected Nano Banana 2 Edit for identity-preserving image editing.",
        "Placed preservation requirements before the requested background change.",
      ],
    },
  ],
  best_practices: [
    "State the subject first, then describe the scene, lighting, style, and output constraints.",
    "Use economical draft settings for exploration, then increase resolution or quality only for selected finals.",
    "Provide only approved reference URLs and confirm before enabling web grounding or sending sensitive content.",
  ],
  anti_patterns: [
    "Do not request exact typography from a model that is weak at rendering text.",
    "Do not expose secrets, private signed URLs, or confidential prompts to remote model services.",
    "Do not interpolate unescaped user text directly into shell-quoted command arguments.",
  ],
  faq: [
    {
      question: "Does this skill generate images locally?",
      answer:
        "No. It sends requests to RunComfy model endpoints and downloads the generated results.",
    },
    {
      question: "Which model does the skill choose by default?",
      answer:
        "It prefers FLUX 2 Klein 9B for general text-to-image work and Nano Banana 2 Edit for general editing.",
    },
    {
      question: "Can it create posters with exact text?",
      answer:
        "Yes. It routes typography-focused requests to GPT Image 2 and quotes required text in the prompt.",
    },
    {
      question: "Can it preserve a person during an edit?",
      answer:
        "It can request identity-preserving edits, but consistency depends on the model, reference quality, and requested change.",
    },
    {
      question: "What credentials are required?",
      answer:
        "A RunComfy login or RUNCOMFY_TOKEN is required. The CLI stores interactive credentials in a protected user configuration file.",
    },
    {
      question: "Can model costs and availability change?",
      answer:
        "Yes. Check current RunComfy model pages before large batches or production use.",
    },
  ],
};

fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
