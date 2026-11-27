# Input and Output Contract

## Contents

1. Case input
2. Reception input
3. Analyzer command
4. Report output
5. Validation rules

## 1. Case input

Use schema version `1.0`:

```json
{
  "schema_version": "1.0",
  "source": {
    "url": "https://example.com/post",
    "platform": "web",
    "author": "Visible account name or null",
    "published_at": "2026-07-15T11:50:00Z",
    "captured_at": "2026-07-15T12:00:00Z",
    "public": true
  },
  "content": {
    "text": "Post text or null",
    "language": "en",
    "images": [
      {
        "id": "image-1",
        "path": "D:\\\\temp\\\\image.jpg",
        "source_url": "https://example.com/image.jpg",
        "alt_text": "Visible alt text or null"
      }
    ]
  },
  "observations": [
    {
      "type": "platform_ai_label",
      "value": "AI-generated",
      "assertion": "confirmed",
      "scope": "image-1",
      "source_url": "https://example.com/post"
    }
  ],
  "declared_purpose": "inform"
}
```

Allowed platforms: `x`, `reddit`, `linkedin`, `instagram`, `tiktok`, `threads`, `web`, `unknown`.

Allowed languages: `en`, `zh`, `mixed`, `other`, `unknown`.

Allowed purposes: `inform`, `discuss`, `persuade`, `promote`, `support`, `unknown`.

Require `source.public` to be `true`. Require each media path to be absolute and local. At analysis time, each image must be a regular non-link file inside `--media-root`, at most 20 MiB by default, with JPEG, PNG, WebP, or GIF magic bytes. A `source_url` is documentation only; the analyzer never fetches it.

For disclosures, use `assertion` = `confirmed`, `denied`, `quoted`, `discussed`, or `uncertain`, and set `scope` to `post`, `text`, or the relevant image ID. Merely mentioning or disputing an AI label is not a confirmed disclosure.

## 2. Reception input

Use:

```json
{
  "method": "stance_personas_v1",
  "audience_assumptions": ["General public readers on the visible platform"],
  "reader_views": [
    {
      "persona": "supporter",
      "likely_reaction": "Likely to accept the central message.",
      "aversion_risk": "low",
      "friction_points": [],
      "positive_signals": [
        {
          "statement": "The post names a concrete experience.",
          "excerpt": "a short exact source excerpt",
          "reason": "Explain how the excerpt supports this positive signal."
        }
      ],
      "uncertainty": "The author’s relationship with followers is unknown."
    },
    {
      "persona": "neutral",
      "likely_reaction": "May want more supporting detail.",
      "aversion_risk": "medium",
      "friction_points": [
        {
          "dimension": "credibility_friction",
          "excerpt": "everyone knows",
          "reason": "The broad claim supplies no source or boundary."
        }
      ],
      "positive_signals": [],
      "uncertainty": "Comment-thread context was unavailable."
    },
    {
      "persona": "skeptic",
      "likely_reaction": "May question the author’s motive.",
      "aversion_risk": "medium",
      "friction_points": [],
      "positive_signals": [],
      "uncertainty": "Commercial affiliation is unknown."
    }
  ],
  "cross_reader_patterns": [
    {
      "statement": "The unsupported broad claim creates shared friction.",
      "excerpt": "everyone knows",
      "reason": "Explain the shared effect without proposing an edit.",
      "personas": ["neutral", "skeptic"]
    }
  ],
  "uncertainties": ["These are inferred reactions, not observed responses."]
}
```

Require exactly one `supporter`, one `neutral`, and one `skeptic`. Require every friction excerpt, positive signal, and cross-reader pattern to be grounded in the case text, alt text, image ID, or observation value. Positive entries require `{statement, reason, excerpt|evidence}`. Cross-reader entries additionally require two or three unique `personas`. Bare strings and unknown fields are rejected.

Reject rewrite fields, suggested replacement copy, numeric aversion scores, and unsupported psychological claims.

## 3. Analyzer command

```text
python scripts/social_ai_check.py analyze \
  --input <case.json> \
  --reception <reception.json> \
  --output-dir <directory> \
  --format both \
  [--allow-external] \
  [--external-image image-1] \
  [--media-root <absolute-directory>] \
  [--max-media-bytes 20971520] \
  [--max-images 4] \
  [--text-model <model.json> --text-model-evaluation <evaluation.json>]
```

`--format` accepts `json`, `markdown`, or `both`. The local text detector never transmits text. Hive requires both `--allow-external` and an explicit repeated `--external-image` selection. `--allow-external` by itself uploads nothing. `--max-images` caps uploads; local C2PA still checks every validated image.

The optional learned baseline is displayed only when its fingerprint matches `decision_thresholds.model_id` in a structurally complete locked-blind evaluation whose overall and current-language release gates all pass. Supplying only one file, a tampered artifact, a calibration-only report, or a failed/foreign-language report stops validation. Because these local files are not cryptographically attested, even a structurally valid baseline remains research-only and has no effect on origin or practical labels.

## 4. Report output

The JSON report contains:

```json
{
  "schema_version": "1.0",
  "practical_assessment": {
    "label": "strong_ai_like_drafting_signals",
    "confidence": "descriptive_only",
    "basis": [],
    "counterweights": [],
    "not_a_probability": true,
    "scope": "inspected assets only"
  },
  "origin_assessment": {
    "verdict": "insufficient_evidence",
    "confidence": "low",
    "coverage": {},
    "asset_findings": [],
    "evidence": [],
    "limitations": []
  },
  "local_text_assessment": {
    "method": "zh_descriptive_pattern_proxy_v2",
    "model_kind": "deterministic_untrained_descriptive_proxy",
    "document_classification": "strong_pattern_match",
    "signal_strength": "descriptive_only",
    "not_a_probability": true,
    "coverage": {},
    "decision": {
      "indicator_points": 15,
      "strong_pattern_threshold": 8,
      "converging_feature_families": [],
      "drivers": []
    },
    "statistical_features": {},
    "sentence_findings": [],
    "limitations": []
  },
  "local_model_research_assessment": {
    "status": "not_configured"
  },
  "style_pattern_assessment": {
    "method": "humanizer_zh_reverse_v1",
    "assessment": "some_ai_style_patterns",
    "ai_assistance_inference": "ai_assistance_possible",
    "pattern_count": 3,
    "occurrence_count": 5,
    "matches": [],
    "counter_signals": [],
    "genre_confounds": [],
    "limitations": []
  },
  "detector_coverage": {
    "local_text": {
      "status": "completed",
      "text_present": true,
      "external_transmission": false
    },
    "hive": {
      "status": "not_applicable",
      "selected_images": 0,
      "completed_images": 0
    }
  },
  "external_processing": {
    "provider": "hive",
    "authorized": false,
    "selected_assets": [],
    "recorded_at": "ISO-8601",
    "paths_retained": false
  },
  "reproducibility": {
    "content_sha256": "sha256",
    "local_text_method": "zh_descriptive_pattern_proxy_v2"
  },
  "human_reception": {},
  "sources": [],
  "provider_errors": []
}
```

`report.md` presents the same data in this order:

1. Practical AI-assistance inference
2. AI-origin evidence and provider coverage
3. Local document and sentence detection
4. AI-style patterns
5. Supporter view
6. Neutral-reader view
7. Skeptic view
8. Cross-reader patterns
9. Positive reception signals
10. Coverage and limitations
11. Sources and verification advice

## 5. Validation rules

- Reject unknown schema versions.
- Reject non-public cases.
- Reject remote-only image inputs.
- Reject duplicate or missing reader personas.
- Reject friction points without excerpt and reason.
- Reject friction excerpts that are not grounded in the case.
- Reject rewrite-related keys anywhere in the reception object.
- Sanitize provider errors before writing output.
- Generate `style_pattern_assessment` locally; never accept a user-supplied AI percentage.
- Report local text as `completed` or `not_applicable`. Report Hive as `completed`, `partial`, `not_applicable`, `not_run_no_assets_selected`, `not_run_no_consent`, `not_run_missing_key`, or `failed`; never silently treat a skipped image detector as negative evidence.
- Never retain absolute media paths in reports. Record asset ID, validated MIME type, byte count, and SHA-256 only.
- Never label document self-surprisal, compression, or repetition as language-model perplexity.
- Never expose local indicator points as an AI percentage or calibrated probability.
