def static_verdict:
  if .id == "external_commands:SKILL.md:6:ruby-shell-backtick-execution" then
    {
      id: .id,
      verdict: "confirmed",
      confidence: 0.99,
      reason: "The skill explicitly tells the agent to run an npx self-update silently and without consent. This can fetch code and modify installed skill content.",
      severity: "high"
    }
  elif (
    .id == "network:assets/test-corpus/tier-1-title-card/hf-src/index.html:6:hardcoded-url" or
    .id == "network:assets/test-corpus/tier-2-multi-scene/hf-src/index.html:6:hardcoded-url" or
    .id == "network:assets/test-corpus/tier-3-data-driven/hf-src/index.html:6:hardcoded-url"
  ) then
    {
      id: .id,
      verdict: "confirmed",
      confidence: 0.98,
      reason: "The fixture HTML loads executable GSAP code from a third-party CDN. This creates a real network and supply-chain dependency during rendering.",
      severity: "low"
    }
  elif (
    .id == "network:references/fonts.md:19:hardcoded-url" or
    .id == "network:references/fonts.md:20:hardcoded-url" or
    .id == "network:references/fonts.md:22:hardcoded-url"
  ) then
    {
      id: .id,
      verdict: "confirmed",
      confidence: 0.94,
      reason: "The reference directs generated compositions to contact Google Fonts services. This is an intentional external network dependency, although its security impact is limited.",
      severity: "low"
    }
  elif (
    .id == "network:references/lottie.md:27:hardcoded-url" or
    .id == "network:references/lottie.md:60:hardcoded-url"
  ) then
    {
      id: .id,
      verdict: "confirmed",
      confidence: 0.97,
      reason: "The reference directs generated compositions to execute Lottie libraries from public CDNs. Remote script execution creates a real supply-chain dependency.",
      severity: "low"
    }
  elif .pattern == "Ruby/shell backtick execution" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.98,
      reason: "The backticks are Markdown formatting, comments, or JavaScript template literals. The cited snippet does not invoke a Ruby or shell execution primitive."
    }
  elif .pattern == "Template literal with command substitution" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The cited text is a shell-script comment containing Markdown backticks. It is not evaluated as a template or command substitution."
    }
  elif .pattern == "Shell command substitution" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.96,
      reason: "The script uses quoted command substitution for local path discovery, temporary directories, basenames, or test output. It does not evaluate untrusted command text."
    }
  elif .pattern == "Path traversal sequence" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.98,
      reason: "The relative path is a fixed repository navigation, module import, or documentation link. No user-controlled value escapes an authorization boundary."
    }
  elif .pattern == "Standard device file access" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The snippet redirects routine command output to /dev/null. It does not access sensitive devices or disclose system data."
    }
  elif .pattern == "Temp file creation" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.98,
      reason: "mktemp creates an isolated working directory that is removed by a trap. The path is not predictable or reused across trust boundaries."
    }
  elif .pattern == "Python file write/append" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.97,
      reason: "The Python helper writes a structured test result to the orchestrator's private temporary directory. The destination is supplied by trusted script state."
    }
  elif .pattern == "System reconnaissance" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The match is a keyword collision in prose, CSS, JSON, or a local variable. The snippet performs no host, account, process, or network reconnaissance."
    }
  elif .pattern == "Hardcoded URL" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.96,
      reason: "The URL is an inert documentation link, placeholder, or negative test fixture. The cited location does not perform an operational network request."
    }
  elif .pattern == "Fetch API call" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.97,
      reason: "The fetch appears in documentation or a lint test fixture for unsupported Remotion patterns. The skill does not execute it against user data."
    }
  elif .pattern == "Python environment access" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.98,
      reason: "The validator reads three local path variables assigned immediately by its own shell wrapper. It does not collect credentials or unrelated environment secrets."
    }
  elif .pattern == "Dynamic import() expression" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The dynamic import is shown only in a Markdown API table or limitation example. It is not executed by the skill."
    }
  elif .pattern == "Python subprocess.run" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.95,
      reason: "The helper invokes fixed ffprobe and ffmpeg executables with argument arrays and shell execution disabled. User paths are passed as single arguments."
    }
  elif .pattern == "Hidden file access" then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The match comes from a docstring mentioning .ts and .tsx extensions. No hidden file is opened at this location."
    }
  else
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.8,
      reason: "The cited snippet has no harmful behavior in its surrounding test or documentation context. No exploitable data flow is present."
    }
  end;

.skill.description = "Convert existing Remotion React compositions into HyperFrames HTML and GSAP timelines, with lint checks, translation guidance, and visual fidelity validation."
| .skill.summary = "Translate supported Remotion compositions to HyperFrames and verify the rendered result."
| .skill.category = "coding"
| .skill.tags = ["remotion", "hyperframes", "video", "react", "gsap"]
| .content.user_title = "Convert Remotion Projects to HyperFrames"
| .content.value_statement = "Manual Remotion migration can miss timing, media, and rendering differences. This skill maps supported React compositions to HyperFrames and validates visual fidelity."
| .content.seo_keywords = [
    "Remotion conversion",
    "HyperFrames migration",
    "React video",
    "GSAP timeline",
    "video composition",
    "Claude",
    "Codex",
    "Claude Code",
    "SSIM validation"
  ]
| .content.actual_capabilities = [
    "Lints Remotion TypeScript and TSX sources for patterns that HyperFrames cannot translate reliably.",
    "Maps Remotion composition metadata, sequencing, timing, media, transitions, fonts, and Lottie usage to HyperFrames patterns.",
    "Generates an HTML composition structure with scene metadata, CSS, and a paused GSAP timeline.",
    "Renders Remotion and HyperFrames outputs for frame-by-frame SSIM comparison.",
    "Creates visual frame strips and translation notes when rendered output differs or features are approximated."
  ]
| .content.limitations = [
    "Supports one-way conversion from Remotion to HyperFrames only.",
    "Refuses stateful React patterns, asynchronous metadata, and unsupported third-party UI libraries.",
    "Cannot preserve every audio ramp, custom transition presentation, or authenticated remote asset behavior.",
    "Requires local Remotion, HyperFrames, Node.js, Python, ffmpeg, and ffprobe tooling for full validation."
  ]
| .content.use_cases = [
    {
      title: "Migrate a marketing video",
      description: "Convert an existing Remotion campaign composition into a seekable HyperFrames project and compare both rendered outputs.",
      target_user: "Frontend developers"
    },
    {
      title: "Assess migration feasibility",
      description: "Lint a complex Remotion project and identify blockers, warnings, and features that require runtime interop.",
      target_user: "Technical leads"
    },
    {
      title: "Validate a translated composition",
      description: "Measure visual similarity, inspect divergent frames, and document acceptable translation gaps before release.",
      target_user: "Video quality engineers"
    }
  ]
| .content.prompt_templates = [
    {
      title: "Check a simple composition",
      prompt: "Review my Remotion source at [path]. Identify the composition, lint it, and explain whether it can be converted to HyperFrames.",
      scenario: "Beginner feasibility check"
    },
    {
      title: "Convert one composition",
      prompt: "Convert Remotion composition [composition ID] at [path] to HyperFrames. Preserve dimensions, frame rate, duration, sequencing, and media paths.",
      scenario: "Standard one-composition migration"
    },
    {
      title: "Convert and validate",
      prompt: "Convert [composition ID] from Remotion to HyperFrames. Render both versions, compare SSIM, inspect failed frames, and document every approximation.",
      scenario: "Migration with visual verification"
    },
    {
      title: "Plan a complex migration",
      prompt: "Audit the Remotion project at [path]. Classify blockers and warnings, select one composition, propose interop where needed, and produce a validated migration plan.",
      scenario: "Advanced project assessment"
    }
  ]
| .content.output_examples = [
    {
      input: "Check whether a title card using Sequence, interpolate, spring, and staticFile can migrate.",
      output: "The composition is eligible. The report lists direct HyperFrames mappings, copied assets, expected metadata, and the validation steps."
    },
    {
      input: "Convert a composition that uses useState and a frame-dependent useEffect.",
      output: "The conversion stops after linting. The report identifies stateful behavior and recommends runtime interop instead of lossy HTML translation."
    },
    {
      input: "Validate a completed multi-scene conversion.",
      output: "The result includes Remotion and HyperFrames renders, SSIM statistics, a pass decision, divergent frame samples, and documented limitations."
    }
  ]
| .content.best_practices = [
    "Run the source linter before generating any HyperFrames files.",
    "Translate one composition at a time and preserve its original frame rate, dimensions, and duration.",
    "Use matching pixel formats and review both SSIM metrics and frame strips."
  ]
| .content.anti_patterns = [
    "Do not use this skill to create a new composition from a visual reference.",
    "Do not force conversion when the linter reports stateful React or asynchronous metadata blockers.",
    "Do not treat a visual similarity score as proof that audio and remote assets are equivalent."
  ]
| .content.faq = [
    {
      question: "Can this skill convert HyperFrames back to Remotion?",
      answer: "No. The supported direction is Remotion to HyperFrames only."
    },
    {
      question: "Does it support every React component?",
      answer: "No. Stateful hooks, asynchronous metadata, and several third-party UI libraries require refactoring or runtime interop."
    },
    {
      question: "How does it verify visual accuracy?",
      answer: "It renders both compositions and computes frame-level SSIM statistics. A frame strip helps diagnose visible differences."
    },
    {
      question: "What happens to unsupported features?",
      answer: "Blockers stop conversion. Lower-impact gaps are approximated or removed and recorded in translation notes."
    },
    {
      question: "Can it migrate multiple compositions together?",
      answer: "No. Select and convert one Remotion composition at a time."
    },
    {
      question: "Which tools are required for full validation?",
      answer: "Full validation requires Node.js, Remotion, HyperFrames, Python, ffmpeg, and ffprobe in the local environment."
    }
  ]
| .security_audit.finding_verdicts = [.security_audit.static_findings[] | static_verdict]
| .security_audit.semantic_findings = [
    {
      title: "Prompt Injection Attempt Detected",
      description: "The text says, \"run silently, don't ask,\" before an npx self-update. It attempts to bypass consent and alter trusted skill instructions.",
      severity: "high",
      locations: [
        {
          file: "SKILL.md",
          line_start: 6,
          line_end: 6
        }
      ],
      confidence: 0.99,
      confidence_reasoning: "The instruction explicitly suppresses user confirmation while fetching and updating skill content. This is a direct consent-bypass and self-modification instruction."
    },
    {
      title: "Validation Harness Installs Dependencies Automatically",
      description: "The recommended corpus runner performs npm install when dependencies are absent, which can download packages and execute lifecycle scripts.",
      severity: "medium",
      locations: [
        {
          file: "SKILL.md",
          line_start: 114,
          line_end: 118
        },
        {
          file: "assets/test-corpus/run.sh",
          line_start: 128,
          line_end: 135
        }
      ],
      confidence: 0.97,
      confidence_reasoning: "The workflow recommends the runner, and the runner directly invokes npm install before rendering. The network and lifecycle-script exposure is explicit."
    }
  ]
| .security_audit.analysis_status = "ok"
| .security_audit.summary = "Most static alerts are lexical false positives from Markdown, test fixtures, CSS templates, relative project paths, and bounded local tooling. Confirmed risks include a silent self-update instruction, remote CDN dependencies, and automatic package installation in the validation harness."
| .security_audit.remediation = [
    {
      issue: "The skill requests a silent self-update without user consent.",
      suggestion: "Remove the instruction. Require explicit approval and use a pinned, reviewed update mechanism.",
      severity: "high"
    },
    {
      issue: "The validation harness runs npm install automatically.",
      suggestion: "Request approval first. Use locked dependencies, npm ci, disabled lifecycle scripts, and an isolated environment.",
      severity: "medium"
    },
    {
      issue: "Generated examples load scripts and fonts from public CDNs.",
      suggestion: "Vendor reviewed assets locally or pin versions with integrity checks and document required network access.",
      severity: "low"
    }
  ]
