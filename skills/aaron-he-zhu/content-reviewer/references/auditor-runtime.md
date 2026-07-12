<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 17.0.0
- **Framework:** C3
- **Auditor:** content-reviewer
- **Source digest:** `sha256:dff93705219b61fbd654d445eae4d93b88391c1f6e6283c0e551ba4532e3a69f`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "17.0.0",
  "frameworks": {
    "C3": {
      "construct": "three separately observed influencer scopes: creator, content, and campaign",
      "context_allowed": {
        "assessment_time": [
          "forecast",
          "actual"
        ]
      },
      "cross_scope_rollup": {
        "forecast_actual_mixing": false,
        "method": "geometric-mean",
        "requires_same_assessment_time": true,
        "requires_same_catalog_version": true,
        "requires_same_goal": true,
        "requires_same_rollup_id": true
      },
      "dimensions": {
        "ACE.A": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ACE.A",
          "name": "Audience Asset"
        },
        "ACE.C": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ACE.C",
          "name": "Credibility"
        },
        "ACE.E": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ACE.E",
          "name": "Engagement"
        },
        "ART.A": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ART.A",
          "name": "Appeal"
        },
        "ART.R": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ART.R",
          "name": "Relevance"
        },
        "ART.T": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ART.T",
          "name": "Transparency"
        },
        "ROI.I": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ROI.I",
          "name": "Impact"
        },
        "ROI.O": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ROI.O",
          "name": "Orchestration"
        },
        "ROI.R": {
          "id_width": 1,
          "item_count": 4,
          "item_prefix": "ROI.R",
          "name": "Return"
        }
      },
      "item_policies": {
        "ACE.A1": {
          "definition": "audience composition is measured and stable; brand fit is excluded"
        },
        "ACE.A3": {
          "definition": "typical reach reliability across a stated window; campaign tier fit is excluded"
        },
        "ACE.C4": {
          "definition": "commercial saturation and disclosed category history; a specific brand conflict is scored in ROI.O1"
        },
        "ACE.E3": {
          "definition": "repeat audience action signals with source/date; campaign conversion is scored in ROI.I2"
        },
        "ROI.I1": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        },
        "ROI.I2": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        },
        "ROI.I3": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "fail_flag": "results-unverified",
          "unknown_policy": "needs-input"
        },
        "ROI.R1": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        },
        "ROI.R2": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        }
      },
      "profiles": {
        "ace-awareness": {
          "context_equals": {
            "goal": "awareness",
            "scope": "ace"
          },
          "dimensions": {
            "ACE.A": 0.45,
            "ACE.C": 0.25,
            "ACE.E": 0.3
          }
        },
        "ace-brand-building": {
          "context_equals": {
            "goal": "brand-building",
            "scope": "ace"
          },
          "dimensions": {
            "ACE.A": 0.3,
            "ACE.C": 0.45,
            "ACE.E": 0.25
          }
        },
        "ace-conversion": {
          "context_equals": {
            "goal": "conversion",
            "scope": "ace"
          },
          "dimensions": {
            "ACE.A": 0.35,
            "ACE.C": 0.3,
            "ACE.E": 0.35
          }
        },
        "ace-engagement": {
          "context_equals": {
            "goal": "engagement",
            "scope": "ace"
          },
          "dimensions": {
            "ACE.A": 0.25,
            "ACE.C": 0.25,
            "ACE.E": 0.5
          }
        },
        "art-awareness": {
          "context_equals": {
            "goal": "awareness",
            "scope": "art"
          },
          "dimensions": {
            "ART.A": 0.45,
            "ART.R": 0.3,
            "ART.T": 0.25
          }
        },
        "art-brand-building": {
          "context_equals": {
            "goal": "brand-building",
            "scope": "art"
          },
          "dimensions": {
            "ART.A": 0.35,
            "ART.R": 0.4,
            "ART.T": 0.25
          }
        },
        "art-conversion": {
          "context_equals": {
            "goal": "conversion",
            "scope": "art"
          },
          "dimensions": {
            "ART.A": 0.35,
            "ART.R": 0.4,
            "ART.T": 0.25
          }
        },
        "art-engagement": {
          "context_equals": {
            "goal": "engagement",
            "scope": "art"
          },
          "dimensions": {
            "ART.A": 0.5,
            "ART.R": 0.25,
            "ART.T": 0.25
          }
        },
        "roi-awareness": {
          "context_equals": {
            "goal": "awareness",
            "scope": "roi"
          },
          "dimensions": {
            "ROI.I": 0.4,
            "ROI.O": 0.4,
            "ROI.R": 0.2
          }
        },
        "roi-brand-building": {
          "context_equals": {
            "goal": "brand-building",
            "scope": "roi"
          },
          "dimensions": {
            "ROI.I": 0.35,
            "ROI.O": 0.4,
            "ROI.R": 0.25
          }
        },
        "roi-conversion": {
          "context_equals": {
            "goal": "conversion",
            "scope": "roi"
          },
          "dimensions": {
            "ROI.I": 0.35,
            "ROI.O": 0.25,
            "ROI.R": 0.4
          }
        },
        "roi-engagement": {
          "context_equals": {
            "goal": "engagement",
            "scope": "roi"
          },
          "dimensions": {
            "ROI.I": 0.4,
            "ROI.O": 0.35,
            "ROI.R": 0.25
          }
        }
      },
      "required_context": [
        "scope",
        "goal",
        "assessment_time",
        "rollup_id"
      ],
      "source": "references/c3-benchmark.md",
      "unit_of_analysis": "one qualified scope at one observation time; forecast and actual campaign reads are never merged",
      "veto_items": [
        "ACE.A2",
        "ACE.C1",
        "ACE.E2",
        "ART.T1",
        "ART.T2"
      ]
    }
  },
  "semantics": {
    "bands": [
      {
        "maximum": 100,
        "minimum": 90,
        "name": "Excellent"
      },
      {
        "maximum": 89,
        "minimum": 75,
        "name": "Good"
      },
      {
        "maximum": 74,
        "minimum": 60,
        "name": "Medium"
      },
      {
        "maximum": 59,
        "minimum": 40,
        "name": "Low"
      },
      {
        "maximum": 39,
        "minimum": 0,
        "name": "Poor"
      }
    ],
    "confidence_factors": {
      "high": 1.0,
      "low": 0.5,
      "medium": 0.75
    },
    "evidence_types": {
      "calculated": 0.8,
      "estimated": 0.5,
      "measured": 1.0,
      "proxy": 0.4,
      "user-provided": 0.8
    },
    "external_validity": "advisory-until-outcome-calibrated",
    "item_points": {
      "fail": 0,
      "partial": 5,
      "pass": 10
    },
    "missingness": {
      "missing": "treated as unknown, never as partial or fail",
      "na": "genuinely inapplicable under an item policy; requires a reason and is excluded",
      "unknown": "applicable but not observed; prevents a comparable total score"
    },
    "multi_veto": {
      "emit_final_score": false,
      "minimum": 2,
      "verdict": "BLOCK"
    },
    "required_coverage": 100,
    "rounding": "floor",
    "score_states": [
      "pass",
      "partial",
      "fail",
      "unknown",
      "na"
    ],
    "veto_ceiling": 59
  }
}
```

## Standalone Execution Policy

1. Select exactly one declared profile from the typed snapshot and record it with the catalog version and source digest above.
2. Collect one state per applicable item using the run-schema vocabulary: `pass`, `partial`, `fail`, `na`, or `unknown` — the same states the root scorer replays later. Every non-unknown state needs evidence; never convert missing evidence into a pass.
3. Record veto observations by their qualified framework item IDs, but do not calculate dimension, raw, capped, or final scores without the root deterministic scorer.
4. Return `status: NEEDS_INPUT` or `status: BLOCKED` with `verdict: UNDECIDED`, `score_state: NOT_SCORED`, and `score_confidence: not_scored`. Clearly identify the unavailable root runtime as the reason.
5. Do not write under `memory/audits/`, mutate registries, or claim a publish/ship decision. Offer the observation set for later execution in a full plugin or repository install.
6. Do not search parent directories, accept an unverified runtime root, download repository files, or hand-calculate a substitute score.

The source digest binds this compact fallback to the authoritative runbook, scoring semantics, framework benchmark, run schema, and artifact schema without copying those maintenance sources into every standalone bundle.

---

End of generated standalone runtime.
