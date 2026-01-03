# Changelog

All notable changes to the AI Skillstore marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).





## [0.3.0] - 2026-01-03

### Summary

AI Skillstore marketplace v0.3.0 expands the catalog to 283 plugins (+147 new), including JetBrains integrations and a large K-Dense-AI scientific/biomedical toolkit. Release workflows are more reliable and faster with full cache-warming (warm/force), publish-after-build pre-rendering, KV-based ISR sync, and broad normalization of versions, slugs, names, and paths to consistent semver and lowercase kebab-case. 

### Statistics

- Total plugins: 283
- New plugins: 147
- Updated plugins: 0

### New Plugins

- `jetbrains-changelog`
- `jetbrains-doc-sync`
- `jetbrains-tests-maintenance`
- `jetbrains-youtrack`
- `k-dense-ai-adaptyv`
- `k-dense-ai-aeon`
- `k-dense-ai-alphafold-database`
- `k-dense-ai-anndata`
- `k-dense-ai-arboreto`
- `k-dense-ai-astropy`
- `k-dense-ai-benchling-integration`
- `k-dense-ai-biomni`
- `k-dense-ai-biopython`
- `k-dense-ai-biorxiv-database`
- `k-dense-ai-bioservices`
- `k-dense-ai-brenda-database`
- `k-dense-ai-cellxgene-census`
- `k-dense-ai-chembl-database`
- `k-dense-ai-cirq`
- `k-dense-ai-citation-management`
- `k-dense-ai-clinical-decision-support`
- `k-dense-ai-clinical-reports`
- `k-dense-ai-clinicaltrials-database`
- `k-dense-ai-clinpgx-database`
- `k-dense-ai-clinvar-database`
- `k-dense-ai-cobrapy`
- `k-dense-ai-cosmic-database`
- `k-dense-ai-dask`
- `k-dense-ai-datacommons-client`
- `k-dense-ai-datamol`
- `k-dense-ai-deepchem`
- `k-dense-ai-deeptools`
- `k-dense-ai-denario`
- `k-dense-ai-diffdock`
- `k-dense-ai-dnanexus-integration`
- `k-dense-ai-docx`
- `k-dense-ai-drugbank-database`
- `k-dense-ai-ena-database`
- `k-dense-ai-ensembl-database`
- `k-dense-ai-esm`
- `k-dense-ai-etetoolkit`
- `k-dense-ai-exploratory-data-analysis`
- `k-dense-ai-fda-database`
- `k-dense-ai-flowio`
- `k-dense-ai-fluidsim`
- `k-dense-ai-gene-database`
- `k-dense-ai-generate-image`
- `k-dense-ai-geniml`
- `k-dense-ai-geo-database`
- `k-dense-ai-geopandas`
- `k-dense-ai-get-available-resources`
- `k-dense-ai-gget`
- `k-dense-ai-gtars`
- `k-dense-ai-gwas-database`
- `k-dense-ai-histolab`
- `k-dense-ai-hmdb-database`
- `k-dense-ai-hypogenic`
- `k-dense-ai-hypothesis-generation`
- `k-dense-ai-iso-13485-certification`
- `k-dense-ai-kegg-database`
- `k-dense-ai-labarchive-integration`
- `k-dense-ai-lamindb`
- `k-dense-ai-latchbio-integration`
- `k-dense-ai-latex-posters`
- `k-dense-ai-literature-review`
- `k-dense-ai-market-research-reports`
- `k-dense-ai-markitdown`
- `k-dense-ai-matchms`
- `k-dense-ai-matplotlib`
- `k-dense-ai-medchem`
- `k-dense-ai-metabolomics-workbench-database`
- `k-dense-ai-modal`
- `k-dense-ai-molfeat`
- `k-dense-ai-networkx`
- `k-dense-ai-neurokit2`
- `k-dense-ai-neuropixels-analysis`
- `k-dense-ai-omero-integration`
- `k-dense-ai-openalex-database`
- `k-dense-ai-opentargets-database`
- `k-dense-ai-opentrons-integration`
- `k-dense-ai-paper-2-web`
- `k-dense-ai-pathml`
- `k-dense-ai-pdb-database`
- `k-dense-ai-pdf`
- `k-dense-ai-peer-review`
- `k-dense-ai-pennylane`
- `k-dense-ai-perplexity-search`
- `k-dense-ai-plotly`
- `k-dense-ai-polars`
- `k-dense-ai-pptx`
- `k-dense-ai-protocolsio-integration`
- `k-dense-ai-pubchem-database`
- `k-dense-ai-pubmed-database`
- `k-dense-ai-pufferlib`
- `k-dense-ai-pydeseq2`
- `k-dense-ai-pydicom`
- `k-dense-ai-pyhealth`
- `k-dense-ai-pylabrobot`
- `k-dense-ai-pymatgen`
- `k-dense-ai-pymc-bayesian-modeling`
- `k-dense-ai-pymoo`
- `k-dense-ai-pyopenms`
- `k-dense-ai-pysam`
- `k-dense-ai-pytdc`
- `k-dense-ai-pytorch-lightning`
- `k-dense-ai-qiskit`
- `k-dense-ai-qutip`
- `k-dense-ai-rdkit`
- `k-dense-ai-reactome-database`
- `k-dense-ai-research-grants`
- `k-dense-ai-research-lookup`
- `k-dense-ai-scanpy`
- `k-dense-ai-scholar-evaluation`
- `k-dense-ai-scientific-brainstorming`
- `k-dense-ai-scientific-critical-thinking`
- `k-dense-ai-scientific-schematics`
- `k-dense-ai-scientific-slides`
- `k-dense-ai-scientific-visualization`
- `k-dense-ai-scientific-writing`
- `k-dense-ai-scikit-bio`
- `k-dense-ai-scikit-learn`
- `k-dense-ai-scikit-survival`
- `k-dense-ai-scvi-tools`
- `k-dense-ai-seaborn`
- `k-dense-ai-shap`
- `k-dense-ai-simpy`
- `k-dense-ai-stable-baselines3`
- `k-dense-ai-statistical-analysis`
- `k-dense-ai-statsmodels`
- `k-dense-ai-string-database`
- `k-dense-ai-sympy`
- `k-dense-ai-torch-geometric`
- `k-dense-ai-torchdrug`
- `k-dense-ai-transformers`
- `k-dense-ai-treatment-plans`
- `k-dense-ai-umap-learn`
- `k-dense-ai-uniprot-database`
- `k-dense-ai-uspto-database`
- `k-dense-ai-vaex`
- `k-dense-ai-venue-templates`
- `k-dense-ai-xlsx`
- `k-dense-ai-zarr-python`
- `k-dense-ai-zinc-database`
- `yamadashy-agent-memory`
- `yamadashy-browser-extension-developer`
- `yamadashy-lint-fixer`
- `yamadashy-website-maintainer`

### Changes

- fix: normalize all version values to valid semver format
- feat: add full cache warming workflow with warm/force modes
- refactor: simplify sync workflow with KV-based ISR
- fix: normalize K-Dense-AI slugs in skill-report.json to lowercase
- fix: normalize plugin names and source paths in marketplace.json to lowercase
- fix: normalize plugin names and paths to lowercase kebab-case
- feat: add publish-after-build workflow for pre-rendering


## [0.2.0] - 2026-01-02

### Summary

AI Skillstore marketplace v0.2.0 expands the catalog to 136 plugins with 108 new additions spanning engineering patterns, security/compliance, DevOps/cloud, and LLM/ML workflows. This release also hardens metadata and summary generation (safer backtick handling, improved security finding modeling, correct risk levels, and removed unauthorized fields) and streamlines delivery with an automated Cloudflare deploy triggered after Supabase sync. 

### Statistics

- Total plugins: 136
- New plugins: 108
- Updated plugins: 0

### New Plugins

- `wshobson-airflow-dag-patterns`
- `wshobson-angular-migration`
- `wshobson-api-design-principles`
- `wshobson-architecture-decision-records`
- `wshobson-architecture-patterns`
- `wshobson-async-python-patterns`
- `wshobson-attack-tree-construction`
- `wshobson-auth-implementation-patterns`
- `wshobson-backtesting-frameworks`
- `wshobson-bash-defensive-patterns`
- `wshobson-bats-testing-patterns`
- `wshobson-bazel-build-optimization`
- `wshobson-billing-automation`
- `wshobson-changelog-automation`
- `wshobson-code-review-excellence`
- `wshobson-cost-optimization`
- `wshobson-cqrs-implementation`
- `wshobson-data-quality-frameworks`
- `wshobson-data-storytelling`
- `wshobson-database-migration`
- `wshobson-dbt-transformation-patterns`
- `wshobson-debugging-strategies`
- `wshobson-defi-protocol-templates`
- `wshobson-dependency-upgrade`
- `wshobson-deployment-pipeline-design`
- `wshobson-distributed-tracing`
- `wshobson-dotnet-backend-patterns`
- `wshobson-e2e-testing-patterns`
- `wshobson-embedding-strategies`
- `wshobson-employment-contract-templates`
- `wshobson-error-handling-patterns`
- `wshobson-event-store-design`
- `wshobson-fastapi-templates`
- `wshobson-gdpr-data-handling`
- `wshobson-git-advanced-workflows`
- `wshobson-github-actions-templates`
- `wshobson-gitlab-ci-patterns`
- `wshobson-gitops-workflow`
- `wshobson-go-concurrency-patterns`
- `wshobson-godot-gdscript-patterns`
- `wshobson-grafana-dashboards`
- `wshobson-helm-chart-scaffolding`
- `wshobson-hybrid-cloud-networking`
- `wshobson-hybrid-search-implementation`
- `wshobson-incident-runbook-templates`
- `wshobson-istio-traffic-management`
- `wshobson-javascript-testing-patterns`
- `wshobson-k8s-manifest-generator`
- `wshobson-k8s-security-policies`
- `wshobson-kpi-dashboard-design`
- `wshobson-langchain-architecture`
- `wshobson-linkerd-patterns`
- `wshobson-llm-evaluation`
- `wshobson-memory-safety-patterns`
- `wshobson-microservices-patterns`
- `wshobson-ml-pipeline-workflow`
- `wshobson-modern-javascript-patterns`
- `wshobson-monorepo-management`
- `wshobson-mtls-configuration`
- `wshobson-multi-cloud-architecture`
- `wshobson-nextjs-app-router-patterns`
- `wshobson-nft-standards`
- `wshobson-nodejs-backend-patterns`
- `wshobson-nx-workspace-patterns`
- `wshobson-on-call-handoff-patterns`
- `wshobson-openapi-spec-generation`
- `wshobson-paypal-integration`
- `wshobson-pci-compliance`
- `wshobson-postgresql-table-design`
- `wshobson-postmortem-writing`
- `wshobson-projection-patterns`
- `wshobson-prometheus-configuration`
- `wshobson-prompt-engineering-patterns`
- `wshobson-python-packaging`
- `wshobson-python-performance-optimization`
- `wshobson-python-testing-patterns`
- `wshobson-rag-implementation`
- `wshobson-react-modernization`
- `wshobson-react-native-architecture`
- `wshobson-react-state-management`
- `wshobson-risk-metrics-calculation`
- `wshobson-rust-async-patterns`
- `wshobson-saga-orchestration`
- `wshobson-sast-configuration`
- `wshobson-screen-reader-testing`
- `wshobson-secrets-management`
- `wshobson-security-requirement-extraction`
- `wshobson-service-mesh-observability`
- `wshobson-shellcheck-configuration`
- `wshobson-similarity-search-patterns`
- `wshobson-slo-implementation`
- `wshobson-solidity-security`
- `wshobson-spark-optimization`
- `wshobson-sql-optimization-patterns`
- `wshobson-stride-analysis-patterns`
- `wshobson-stripe-integration`
- `wshobson-tailwind-design-system`
- `wshobson-temporal-python-testing`
- `wshobson-terraform-module-library`
- `wshobson-threat-mitigation-mapping`
- `wshobson-turborepo-caching`
- `wshobson-typescript-advanced-types`
- `wshobson-unity-ecs-patterns`
- `wshobson-uv-package-manager`
- `wshobson-vector-index-tuning`
- `wshobson-wcag-audit-patterns`
- `wshobson-web3-testing`
- `wshobson-workflow-orchestration-patterns`

### Changes

- fix: escape backticks in AI summary to prevent command substitution
- fix: convert dangerous_patterns strings to SecurityFinding objects
- fix: use 5-tier risk_level directly without mapping
- fix: remove unauthorized released_at field from marketplace metadata
- feat: trigger Cloudflare deploy after plugin sync to Supabase
- refactor: merge deploy-skillstore into sync-to-supabase job


## [0.1.0] - 2026-01-01

### Summary

AI Skillstore marketplace v0.1.0 launches with 28 new plugins and an end-to-end pipeline for publishing and syncing the catalog to Skillstore/Supabase. This release consolidates and hardens release/submission workflows (tag-triggered releases, validation, callbacks) and standardizes schemas and plugin naming/paths (including namespaced and nested structures) for more reliable indexing and distribution. 

### Statistics

- Total plugins: 28
- New plugins: 28
- Updated plugins: 0

### New Plugins

- `agent-development`
- `algorithmic-art`
- `brand-guidelines`
- `canvas-design`
- `claude-opus-4-5-migration`
- `command-development`
- `doc-coauthoring`
- `docx`
- `frontend-design`
- `hook-development`
- `internal-comms`
- `mcp-builder`
- `mcp-integration`
- `metabase-docs-review`
- `payloadcms-payload`
- `pdf`
- `plugin-settings`
- `plugin-structure`
- `pptx`
- `skill-creator`
- `skill-development`
- `slack-gif-creator`
- `template-skill`
- `theme-factory`
- `web-artifacts-builder`
- `webapp-testing`
- `writing-hookify-rules`
- `xlsx`

### Changes

- feat: trigger skillstore deployment after Supabase sync
- refactor: consolidate 3 release workflows into 1
- docs: update version to 0.1.0 and changelog
- feat: add tag-triggered auto-release workflow
- chore: remove outdated CHANGELOG.md file
- fix: correct plugin slug extraction in incremental sync
- fix: remove redundant canonical_name assignment in sync-to-supabase workflow
- fix: support nested plugin structure in release workflows
- fix: correct plugin move path in on-pr-merge workflow
- refactor: simplify plugin path resolution to use source directly
- fix: correct source paths to include plugins/ prefix (#49)
- fix: use source field for directory path in on-pr-merge workflow
- refactor: remove payload plugin and standardize field naming
- refactor: update plugin.schema.json with official component fields
- refactor: align marketplace.json and schema with official Claude Code spec
- fix: use namespaced plugin name in marketplace.json
- fix: support namespaced plugin paths in sync-to-supabase workflow
- fix: add owner property to skill-report.schema.json meta
- fix: allow namespaced plugin names in plugin.schema.json
- chore: fix schema naming patterns, upgrade Node.js to v24, publish English only
- chore: clear all plugins from marketplace for re-import
- feat: migrate to GitHub-style username/skill-name naming
- fix: use global git config for CLI subprocess operations
- fix: handle race conditions and stale branches in CI workflows
- fix: configure git identity before CLI runs to prevent author unknown error
- refactor: replace trust_level with source_type in schema and all skill-report files
- refactor: replace AI API call with codex CLI in release workflow
- chore: remove unused process-skills.sh script
- feat: add skillstore callback notifications in process-submission workflow
- chore: reset to v0.1.0 for changelog sync test
- chore: reset to v0.1.0 for clean v0.2.0 release test
- chore: reset version to 0.1.0 for clean v0.2.0 release
- fix: remove broken JSON.parse on CHANGELOG.md in release sync
- fix: uncomment package-lock.json in .gitignore to include it in version control
- fix: validate plugins/ skill-report.json and migrate legacy format
- ci: add SKILLSTORE_AGENTS env var to process-submission workflow
- fix: map risk_level to skills table enum (safe→low, critical→high)
- fix: remove deprecated fields, add file_structure and language
- feat: comprehensive Supabase sync with all fields
- fix: use kebab-case slugs for plugin name field
- fix: use PAT_TOKEN for PR creation to trigger validation workflow
- fix: only validate skill-report.json in pending/ folder
- fix: correct path patterns to match .claude-plugin structure
- fix: correct CLI output path to avoid double pending directory
- fix: use PAT_TOKEN for cross-repo CLI download
- fix: use gh CLI for reliable release download
- refactor: replace bash script with pre-built CLI binary
- fix: add canonical_name to sync script
- fix: remove extra closing brace from JSON schema
- fix: use --slurpfile for JSON schema to avoid jq escaping issues
- feat: add multi-skill detection to process-submission workflow
- fix: extract skill name from SKILL.md frontmatter instead of repo name
- refactor: use dynamic WORK_DIR for concurrency safety
- fix: support blob URLs and increase SKILL.md search depth
- fix: use env var for release body to prevent shell backtick interpretation
- docs: add release workflow documentation
- feat: add release workflow with Supabase sync
- fix: stage deletions from pending/ in on-pr-merge workflow
- fix: use bash substitution for multiline values in workflow
- fix: cleanup /tmp artifacts before each workflow run
- fix: update schemas to draft-07 and fix path references
- feat: use self-hosted runner with custom AI API
- feat: add submission processing and sync workflows
- feat: import all 16 Anthropic official skills with AI audit reports
- feat: initialize Claude Code plugin marketplace


## [0.1.0] - 2026-01-01

### Summary

AI Skillstore marketplace v0.1.0 launches with 28 new plugins spanning agent development, document and office formats, design, integrations, and testing. This release also strengthens release/sync workflows and schema compliance, improving namespaced plugin handling, incremental imports, and CI reliability for publishing and Supabase synchronization. 

### Statistics

- Total plugins: 28
- New plugins: 28
- Updated plugins: 0

### New Plugins

- `agent-development`
- `algorithmic-art`
- `brand-guidelines`
- `canvas-design`
- `claude-opus-4-5-migration`
- `command-development`
- `doc-coauthoring`
- `docx`
- `frontend-design`
- `hook-development`
- `internal-comms`
- `mcp-builder`
- `mcp-integration`
- `metabase-docs-review`
- `payloadcms-payload`
- `pdf`
- `plugin-settings`
- `plugin-structure`
- `pptx`
- `skill-creator`
- `skill-development`
- `slack-gif-creator`
- `template-skill`
- `theme-factory`
- `web-artifacts-builder`
- `webapp-testing`
- `writing-hookify-rules`
- `xlsx`

### Changes

- feat: add tag-triggered auto-release workflow
- chore: remove outdated CHANGELOG.md file
- fix: correct plugin slug extraction in incremental sync
- fix: remove redundant canonical_name assignment in sync-to-supabase workflow
- fix: support nested plugin structure in release workflows
- fix: correct plugin move path in on-pr-merge workflow
- refactor: simplify plugin path resolution to use source directly
- fix: correct source paths to include plugins/ prefix (#49)
- fix: use source field for directory path in on-pr-merge workflow
- refactor: remove payload plugin and standardize field naming
- refactor: update plugin.schema.json with official component fields
- refactor: align marketplace.json and schema with official Claude Code spec
- fix: use namespaced plugin name in marketplace.json
- fix: support namespaced plugin paths in sync-to-supabase workflow
- fix: add owner property to skill-report.schema.json meta
- fix: allow namespaced plugin names in plugin.schema.json
- chore: fix schema naming patterns, upgrade Node.js to v24, publish English only
- chore: clear all plugins from marketplace for re-import
- feat: migrate to GitHub-style username/skill-name naming
- fix: use global git config for CLI subprocess operations
- fix: handle race conditions and stale branches in CI workflows
- fix: configure git identity before CLI runs to prevent author unknown error
- refactor: replace trust_level with source_type in schema and all skill-report files
- refactor: replace AI API call with codex CLI in release workflow
- chore: remove unused process-skills.sh script
- feat: add skillstore callback notifications in process-submission workflow
- chore: reset to v0.1.0 for changelog sync test
- chore: reset to v0.1.0 for clean v0.2.0 release test
- chore: reset version to 0.1.0 for clean v0.2.0 release
- fix: remove broken JSON.parse on CHANGELOG.md in release sync
- fix: uncomment package-lock.json in .gitignore to include it in version control
- fix: validate plugins/ skill-report.json and migrate legacy format
- ci: add SKILLSTORE_AGENTS env var to process-submission workflow
- fix: map risk_level to skills table enum (safe→low, critical→high)
- fix: remove deprecated fields, add file_structure and language
- feat: comprehensive Supabase sync with all fields
- fix: use kebab-case slugs for plugin name field
- fix: use PAT_TOKEN for PR creation to trigger validation workflow
- fix: only validate skill-report.json in pending/ folder
- fix: correct path patterns to match .claude-plugin structure
- fix: correct CLI output path to avoid double pending directory
- fix: use PAT_TOKEN for cross-repo CLI download
- fix: use gh CLI for reliable release download
- refactor: replace bash script with pre-built CLI binary
- fix: add canonical_name to sync script
- fix: remove extra closing brace from JSON schema
- fix: use --slurpfile for JSON schema to avoid jq escaping issues
- feat: add multi-skill detection to process-submission workflow
- fix: extract skill name from SKILL.md frontmatter instead of repo name
- refactor: use dynamic WORK_DIR for concurrency safety
- fix: support blob URLs and increase SKILL.md search depth
- fix: use env var for release body to prevent shell backtick interpretation
- docs: add release workflow documentation
- feat: add release workflow with Supabase sync
- fix: stage deletions from pending/ in on-pr-merge workflow
- fix: use bash substitution for multiline values in workflow
- fix: cleanup /tmp artifacts before each workflow run
- fix: update schemas to draft-07 and fix path references
- feat: use self-hosted runner with custom AI API
- feat: add submission processing and sync workflows
- feat: import all 16 Anthropic official skills with AI audit reports
- feat: initialize Claude Code plugin marketplace


