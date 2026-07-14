def external_verdict:
  .line_start as $line
  | if .line_start == 32 then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.96,
      reason: "The detector matched a Markdown code fence. The block contains fixed RunComfy setup and invocation examples with no untrusted shell interpolation."
    }
  elif .line_start == 49 then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.97,
      reason: "The detector matched a Markdown code fence. The block contains a fixed skill installation command, not Ruby backtick execution or dynamic shell construction."
    }
  elif ([174, 205, 217, 239, 264, 292, 324] | index($line)) != null then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.98,
      reason: "The detector matched a Markdown code fence around a fixed runcomfy invocation. Arguments are model identifiers and quoted JSON examples, with no dynamic shell construction."
    }
  elif ([43, 51, 183, 213, 221, 247, 273, 299, 331] | index($line)) != null then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The detector matched a Markdown fence delimiter, not executable backtick syntax. The surrounding content is documentation."
    }
  elif .line_start == 402 then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.97,
      reason: "The line documents the intended runcomfy invocation. Tool scope is limited to RunComfy, and inputs are passed as quoted JSON instead of shell-evaluated text."
    }
  elif .line_start == 406 then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.96,
      reason: "Inline backticks format fixed npm commands, and the text explicitly rejects piping remote scripts into a shell. No dynamic command construction is present."
    }
  elif .line_start == 407 then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "Inline backticks document token storage and credential safeguards. They are Markdown formatting, not shell backtick execution."
    }
  elif .line_start == 408 then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "Inline backticks document the input argument while the text states that prompt content is passed as JSON without shell expansion. This is not execution syntax."
    }
  elif .line_start == 414 then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "Inline backticks quote the restrictive Bash(runcomfy *) tool declaration. The line is a policy statement, not an executed command."
    }
  else
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The detector interpreted Markdown backticks around a CLI name, model identifier, field, example, or link as Ruby execution. No executable backtick expression is present."
    }
  end;

def network_verdict:
  .line_start as $line
  | if ([209, 267, 295, 327] | index($line)) != null then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "This is a placeholder URL under the reserved example domain for user-supplied media. It is not a real destination or covert exfiltration endpoint."
    }
  elif .line_start == 160 then
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The URL is a visible benchmark citation used to support a model-ranking statement. It does not initiate a network request."
    }
  else
    {
      id: .id,
      verdict: "false_positive",
      confidence: 0.99,
      reason: "The hardcoded URL is a visible RunComfy, documentation, or related-skill link relevant to the catalog. It is not a covert request or data-exfiltration destination."
    }
  end;

def filesystem_verdict:
  {
    id: .id,
    verdict: "false_positive",
    confidence: 0.99,
    reason: "The line documents the CLI token file under the standard user configuration directory and requires mode 0600. It neither accesses unrelated hidden files nor exposes the token."
  };

def blocker_verdict:
  {
    id: .id,
    verdict: "false_positive",
    confidence: 0.99,
    reason: "The line says which video model to avoid for a use case. It performs no host discovery and does not request system information."
  };

def adjudicate:
  if .category == "external_commands" then external_verdict
  elif .category == "network" then network_verdict
  elif .category == "filesystem" then filesystem_verdict
  elif .category == "blocker" then blocker_verdict
  else
    {
      id: .id,
      verdict: "confirmed",
      confidence: 0.3,
      reason: "No evidence found to dismiss this unrecognized static category, so it is retained with low confidence."
    }
  end;

.skill.description = "Route text-to-video, image-to-video, and video-extension requests to documented RunComfy models, then generate clips with the runcomfy CLI."
| .skill.summary = "Choose a RunComfy video model and generate a clip from a prompt, image, audio track, or existing video."
| .skill.category = "design"
| .skill.tags = [
    "AI video",
    "text-to-video",
    "image-to-video",
    "RunComfy",
    "generative media"
  ]
| .security_audit.finding_verdicts = [.security_audit.static_findings[] | adjudicate]
| .security_audit.semantic_findings = [
    {
      title: "Third-Party Processing of Prompts and Media",
      description: "The CLI sends generation inputs to the RunComfy Model API and downloads results. Prompts and user-provided media references cross a third-party processing boundary.",
      severity: "low",
      locations: [
        {
          file: "SKILL.md",
          line_start: 209,
          line_end: 209
        },
        {
          file: "SKILL.md",
          line_start: 267,
          line_end: 267
        },
        {
          file: "SKILL.md",
          line_start: 402,
          line_end: 402
        }
      ],
      confidence: 0.98,
      confidence_reasoning: "The examples pass external audio and image URLs, and the behavior section explicitly states that inputs are posted to the RunComfy API."
    }
  ]
| .security_audit.analysis_status = "ok"
| .security_audit.summary = "All 154 static findings are false positives caused by Markdown syntax, fixed CLI examples, documentation links, routing guidance, and a protected token-path description. The expected remaining concern is that prompts and media references are processed by RunComfy; no prompt injection, covert exfiltration, or unrelated filesystem access was found."
| .security_audit.remediation = [
    {
      issue: "Prompts and referenced media may contain private information that leaves the local environment.",
      suggestion: "Disclose RunComfy processing before submission and obtain confirmation before sending sensitive prompts, images, audio, or video references.",
      severity: "low"
    }
  ]
| .content.user_title = "Generate AI Videos with RunComfy"
| .content.value_statement = "Choosing a video model and formatting its inputs takes time. This skill selects a suitable RunComfy route and prepares the generation request."
| .content.seo_keywords = [
    "AI video generation",
    "text to video",
    "image to video",
    "RunComfy",
    "Claude",
    "Codex",
    "Claude Code",
    "video model routing",
    "generative video"
  ]
| .content.actual_capabilities = [
    "Routes text prompts to HappyHorse, Wan, Seedance, Kling, and other documented text-to-video models.",
    "Routes source images by realism, motion, quality, and cost requirements.",
    "Prepares RunComfy requests with documented model identifiers, input fields, durations, aspect ratios, and output directories.",
    "Supports audio-guided lip sync through Wan and in-prompt audio generation through compatible models.",
    "Guides Veo video extension and model selection for longer or multi-shot sequences."
  ]
| .content.limitations = [
    "Requires the RunComfy CLI, an authenticated account, network access, and any applicable service credits.",
    "Sends prompts and referenced media to RunComfy for remote processing.",
    "Model availability, schemas, prices, duration limits, and output quality can change.",
    "Does not edit clips locally or guarantee identity, physics, lip sync, or audio quality."
  ]
| .content.use_cases = [
    {
      title: "Produce Vertical Social Clips",
      description: "Turn a short concept or still image into a vertical clip with suitable duration, motion, and audio guidance.",
      target_user: "Social media creator"
    },
    {
      title: "Animate Product Images",
      description: "Select a realism-focused model and direct controlled camera or object motion for product marketing footage.",
      target_user: "Product marketer"
    },
    {
      title: "Plan Cinematic Sequences",
      description: "Choose multi-reference or multi-shot models for consistent characters, cinematic camera language, and extended scenes.",
      target_user: "Creative director"
    }
  ]
| .content.prompt_templates = [
    {
      title: "Create a Text-to-Video Clip",
      prompt: "Generate a [duration]-second [aspect ratio] video of [subject] performing [action], with [camera movement], [lighting], and [audio]. Choose the best model.",
      scenario: "Beginner text-to-video request"
    },
    {
      title: "Animate a Still Image",
      prompt: "Animate [image URL]. Keep [elements] stable while [subject] performs [motion]. Use [camera direction], [aspect ratio], and [duration].",
      scenario: "Image-to-video request"
    },
    {
      title: "Synchronize a Voiceover",
      prompt: "Create a [duration]-second speaking scene using [audio URL]. Preserve [speaker description], match lip movement, and use [lighting] with [camera framing].",
      scenario: "Audio-driven lip-sync request"
    },
    {
      title: "Build a Multi-Reference Sequence",
      prompt: "Create a cinematic sequence using [subject references], [scene references], and [audio references]. Define [shot sequence], [transitions], [lens], and [final format].",
      scenario: "Advanced multi-modal production"
    }
  ]
| .content.output_examples = [
    {
      input: "Create an eight-second widescreen beach scene with a moving kite, warm sunset light, and natural ambient audio.",
      output: "Selected HappyHorse 1.0 for general text-to-video with native audio. Prepared an eight-second, 16:9 generation request with subject-first motion guidance."
    },
    {
      input: "Animate a product photo with a precise half rotation while every background element remains still.",
      output: "Selected Veo 3-1 for controlled motion and object permanence. Prepared an image-to-video request specifying a 180-degree rotation and no other motion."
    },
    {
      input: "Create a six-second portrait video that follows my supplied voiceover.",
      output: "Selected Wan 2-7 for audio-driven lip sync. Prepared a speaking-scene request using the supplied audio reference and portrait description."
    }
  ]
| .content.best_practices = [
    "Describe one clear subject, action, camera movement, lighting setup, duration, format, and audio requirement.",
    "Use only media URLs supplied for the task, and confirm before sending sensitive assets.",
    "Test with a faster or lower-cost tier before generating the final high-quality clip."
  ]
| .content.anti_patterns = [
    "Do not place API tokens, private credentials, or confidential text inside generation prompts.",
    "Do not promise exact identity, physics, lip sync, audio, or continuity across every model output.",
    "Do not submit third-party media without permission or clear usage rights."
  ]
| .content.faq = [
    {
      question: "What must I install?",
      answer: "Install the RunComfy CLI and authenticate with a RunComfy account before generating videos."
    },
    {
      question: "Does this skill generate videos locally?",
      answer: "No. It submits generation inputs to RunComfy and downloads the completed result."
    },
    {
      question: "Which inputs can I use?",
      answer: "Supported routes include text prompts, source images, audio references, video references, and existing videos for extension."
    },
    {
      question: "How does it choose a model?",
      answer: "It compares input type, quality, speed, cost, realism, audio, lip sync, duration, and multi-shot requirements."
    },
    {
      question: "Can it create audio or lip sync?",
      answer: "Yes. Compatible models support in-pass audio, while Wan supports lip motion driven by a supplied audio file."
    },
    {
      question: "How are credentials and media handled?",
      answer: "The CLI protects stored tokens with mode 0600. Prompts and referenced media are processed by RunComfy."
    }
  ]
