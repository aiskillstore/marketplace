# Description Drift History

| Date | Label | Target | Winner | Tokens | Holdout FP | Holdout FN | Blind FP | Blind FN | Judge Blind Errors | Judge Agreement | Adv FP | Adv FN | Adv Gap | Adv Risk | Drift Note |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 2026-03-31 | Description Optimization Suite | `yao-meta-skill` | `Current` | 65 | 0 | 0 | - | - | - | - | - | - | - | - | initial description optimization suite without blind holdout |
| 2026-03-31 | Description Optimization Suite | `team-frontend-review` | `Current` | 50 | 0 | 0 | - | - | - | - | - | - | - | - | compressed example description and stored first holdout report |
| 2026-03-31 | Description Optimization Suite | `governed-incident-command` | `Current` | 37 | 0 | 1 | - | - | - | - | - | - | - | - | compressed governed description and reduced visible holdout misses |
| 2026-04-01 | Adversarial Calibration And Family Drift | `yao-meta-skill` | `Current` | 65 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0.834 | healthy | tokens stable; blind stable at 0; adversarial gate added with 0 errors; holdout stable at 0; adversarial calibration +0.834; risk n/a -> healthy |
| 2026-04-01 | Adversarial Calibration And Family Drift | `team-frontend-review` | `Current` | 50 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0.509 | healthy | tokens stable; blind stable at 0; adversarial gate added with 0 errors; holdout stable at 0; adversarial calibration +0.509; risk n/a -> healthy |
| 2026-04-01 | Adversarial Calibration And Family Drift | `governed-incident-command` | `Current` | 37 | 0 | 1 | 0 | 0 | - | - | 0 | 0 | 0.598 | healthy | tokens stable; blind stable at 0; adversarial gate added with 0 errors; holdout stable at 1; adversarial calibration +0.598; risk n/a -> healthy |
| 2026-04-01 | Blind Holdout And Drift History | `yao-meta-skill` | `Current` | 65 | 0 | 0 | 0 | 0 | - | - | - | - | - | - | tokens stable; blind gate added with 0 errors; holdout stable at 0 |
| 2026-04-01 | Blind Holdout And Drift History | `team-frontend-review` | `Current` | 50 | 0 | 0 | 0 | 0 | - | - | - | - | - | - | tokens stable; blind gate added with 0 errors; holdout stable at 0 |
| 2026-04-01 | Blind Holdout And Drift History | `governed-incident-command` | `Current` | 37 | 0 | 1 | 0 | 0 | - | - | - | - | - | - | tokens stable; blind gate added with 0 errors; holdout stable at 1 |
| 2026-04-01 | Judge-Backed Blind Eval | `yao-meta-skill` | `Current` | 65 | 0 | 0 | 0 | 0 | 0 | 1.0 | 0 | 0 | 0.834 | healthy | tokens stable; blind stable at 0; adversarial gate added with 0 errors; holdout stable at 0; adversarial calibration +0.834; risk n/a -> healthy |
| 2026-04-01 | Judge-Backed Blind Eval | `team-frontend-review` | `Current` | 50 | 0 | 0 | 0 | 0 | 0 | 1.0 | 0 | 0 | 0.509 | healthy | tokens stable; blind stable at 0; adversarial gate added with 0 errors; holdout stable at 0; adversarial calibration +0.509; risk n/a -> healthy |
| 2026-04-01 | Judge-Backed Blind Eval | `governed-incident-command` | `Current` | 37 | 0 | 1 | 0 | 0 | 0 | 1.0 | 0 | 0 | 0.598 | healthy | tokens stable; blind stable at 0; adversarial gate added with 0 errors; holdout stable at 1; adversarial calibration +0.598; risk n/a -> healthy |

## Family Coverage

| Date | Label | Target | Blind Families | Judge Blind Families | Adversarial Families |
| --- | --- | --- | --- | --- | --- |
| 2026-03-31 | Description Optimization Suite | `yao-meta-skill` | - | - | - |
| 2026-03-31 | Description Optimization Suite | `team-frontend-review` | - | - | - |
| 2026-03-31 | Description Optimization Suite | `governed-incident-command` | - | - | - |
| 2026-04-01 | Adversarial Calibration And Family Drift | `yao-meta-skill` | 6/6 clean; weakest=blind_operationalize | - | 6/6 clean; weakest=adversarial_summary_translation_collision |
| 2026-04-01 | Adversarial Calibration And Family Drift | `team-frontend-review` | 6/6 clean; weakest=blind_premerge | - | 6/6 clean; weakest=adversarial_quality_gate_review |
| 2026-04-01 | Adversarial Calibration And Family Drift | `governed-incident-command` | 6/6 clean; weakest=blind_summary_only | - | 6/6 clean; weakest=adversarial_single_update_collision |
| 2026-04-01 | Blind Holdout And Drift History | `yao-meta-skill` | - | - | - |
| 2026-04-01 | Blind Holdout And Drift History | `team-frontend-review` | - | - | - |
| 2026-04-01 | Blind Holdout And Drift History | `governed-incident-command` | - | - | - |
| 2026-04-01 | Judge-Backed Blind Eval | `yao-meta-skill` | 6/6 clean; weakest=blind_operationalize | 6/6 clean; weakest=blind_operationalize | 6/6 clean; weakest=adversarial_summary_translation_collision |
| 2026-04-01 | Judge-Backed Blind Eval | `team-frontend-review` | 6/6 clean; weakest=blind_premerge | 6/6 clean; weakest=blind_premerge | 6/6 clean; weakest=adversarial_quality_gate_review |
| 2026-04-01 | Judge-Backed Blind Eval | `governed-incident-command` | 6/6 clean; weakest=blind_summary_only | 6/6 clean; weakest=blind_summary_only | 6/6 clean; weakest=adversarial_single_update_collision |
