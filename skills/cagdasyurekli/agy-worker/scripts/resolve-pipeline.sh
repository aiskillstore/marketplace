#!/usr/bin/env bash
# Resolve the canonical pipeline from a complete plugin, install.sh output, or a
# portable copy of this skill folder.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)"

is_pipeline() {
    local pipeline_root runtime_root required component component_canonical parent_canonical

    pipeline_root="$(CDPATH= cd -- "$1" 2>/dev/null && pwd -P)" || return 1
    runtime_root="$pipeline_root"
    if [[ -e "$pipeline_root/skills" || -L "$pipeline_root/skills" ]]; then
        parent_canonical="$pipeline_root"
        for component in skills agy-worker runtime; do
            [[ -d "$parent_canonical/$component" \
                && ! -L "$parent_canonical/$component" ]] || return 1
            component_canonical="$(CDPATH= cd -- "$parent_canonical/$component" \
                2>/dev/null && pwd -P)" || return 1
            [[ "$component_canonical" == "$parent_canonical/$component" ]] \
                || return 1
            parent_canonical="$component_canonical"
        done
        runtime_root="$pipeline_root/skills/agy-worker/runtime"
    fi
    pipeline_runtime_complete "$runtime_root" || return 1

    for required in agy-worker.sh qa-gate.sh verify-job.sh evidence-report.sh benchmark.sh swebench-workflow-study.sh persona-evidence.sh profile.sh model-recommendation.sh model-selection.sh doctor.sh feedback-triage.sh; do
        [[ -f "$pipeline_root/$required" && -x "$pipeline_root/$required" \
            && ! -L "$pipeline_root/$required" ]] || return 1
    done
}

pipeline_runtime_complete() {
    local runtime_root="$1" required parent runtime_canonical parent_canonical
    local dependency_parent dependency_canonical

    [[ -d "$runtime_root" && ! -L "$runtime_root" ]] || return 1
    runtime_canonical="$(CDPATH= cd -- "$runtime_root" 2>/dev/null && pwd -P)" \
        || return 1
    for parent in scripts agents schemas compat benchmarks profiles; do
        [[ -d "$runtime_canonical/$parent" \
            && ! -L "$runtime_canonical/$parent" ]] || return 1
        parent_canonical="$(CDPATH= cd -- "$runtime_canonical/$parent" \
            2>/dev/null && pwd -P)" || return 1
        [[ "$parent_canonical" == "$runtime_canonical/$parent" ]] || return 1
        case "$parent_canonical" in
            "$runtime_canonical"/*) ;;
            *) return 1 ;;
        esac
    done
    for required in \
        agy-worker.sh \
        job.sh \
        qa-gate.sh \
        verify-job.sh \
        evidence-report.sh \
        benchmark.sh \
        swebench-workflow-study.sh \
        persona-evidence.sh \
        profile.sh \
        model-recommendation.sh \
        model-selection.sh \
        doctor.sh \
        feedback-triage.sh \
        scripts/validate-envelope.py \
        scripts/evidence_receipt.py \
        scripts/evidence_report.py \
        scripts/benchmark.py \
        scripts/swebench_workflow_study.py \
        scripts/persona_registry.py \
        scripts/workload_profiles.py \
        scripts/recommendation_record.py \
        scripts/model-recommendation.py \
        scripts/model_selection.py \
        scripts/compatibility.py \
        scripts/candidate_state.py \
        scripts/agy_dispatch.py \
        scripts/job_lifecycle.py \
        scripts/doctor-metadata.py \
        scripts/feedback-triage.py; do
        case "$required" in
            */*) dependency_parent="${required%/*}" ;;
            *) dependency_parent='.' ;;
        esac
        parent_canonical="$(CDPATH= cd -- "$runtime_canonical/$dependency_parent" \
            2>/dev/null && pwd -P)" || return 1
        dependency_canonical="$parent_canonical/${required##*/}"
        case "$dependency_canonical" in
            "$runtime_canonical"/*) ;;
            *) return 1 ;;
        esac
        [[ "$dependency_canonical" == "$runtime_canonical/$required" \
            && -f "$dependency_canonical" && -x "$dependency_canonical" \
            && ! -L "$dependency_canonical" ]] || return 1
    done

    for required in \
        scripts/agy_dispatch_worktree.py \
        schemas/worker-result.schema.json \
        schemas/worker-result.provider.schema.json \
        schemas/evidence-receipt.schema.json \
        schemas/model-selection.schema.json \
        schemas/model-recommendation.schema.json \
        schemas/job-state.schema.json \
        schemas/benchmark-plan.schema.json \
        schemas/benchmark-result.schema.json \
        schemas/swebench-workflow-study-plan.schema.json \
        schemas/swebench-workflow-study-report.schema.json \
        schemas/swebench-workflow-study-advisory.schema.json \
        schemas/persona-dispatch.schema.json \
        schemas/persona-human-review.schema.json \
        schemas/persona-run-evidence.schema.json \
        schemas/persona-run-manifest.schema.json \
        schemas/persona-tool-attestation.schema.json \
        schemas/persona-transition-approval.schema.json \
        schemas/persona-verifier.schema.json \
        schemas/persona-version-attestation.schema.json \
        schemas/workload-profile.schema.json \
        compat/persona-evidence.schema.json \
        compat/persona-registry.schema.json \
        compat/personas/manifest.json \
        compat/personas/bulk-test-writer.json \
        compat/personas/diff-reviewer.json \
        compat/personas/repo-inventory.json \
        benchmarks/v1/manifest.json \
        benchmarks/v1/portable-source.json \
        benchmarks/v1/tasks/exact-edit/initial.txt \
        benchmarks/v1/tasks/exact-edit/candidate.txt \
        benchmarks/v1/tasks/exact-edit/envelope.json \
        benchmarks/v1/variants/bulk.json \
        profiles/v1/manifest.json \
        profiles/v1/bounded-test-backfill.json \
        profiles/v1/diff-review.json \
        profiles/v1/repository-inventory.json \
        agents/bulk-test-writer.md \
        agents/repo-inventory.md \
        agents/diff-reviewer.md \
        compat/agy-verified-version.txt \
        compat/agy-upstream-head.txt \
        compat/agy-last-reviewed.txt \
        compat/agy-model-effort-matrix.json \
        compat/model-effort-matrix.schema.json \
        compat/agy-model-effort-matrix.sha256 \
        compat/agy-models-inventory-binding.json \
        compat/agy-models-inventory-binding.sha256; do
        dependency_parent="${required%/*}"
        parent_canonical="$(CDPATH= cd -- "$runtime_canonical/$dependency_parent" \
            2>/dev/null && pwd -P)" || return 1
        dependency_canonical="$parent_canonical/${required##*/}"
        case "$dependency_canonical" in
            "$runtime_canonical"/*) ;;
            *) return 1 ;;
        esac
        [[ "$dependency_canonical" == "$runtime_canonical/$required" \
            && -f "$dependency_canonical" && ! -x "$dependency_canonical" \
            && ! -L "$dependency_canonical" \
            && "$(/usr/bin/stat -f '%Lp' "$dependency_canonical" 2>/dev/null \
                || /usr/bin/stat -c '%a' "$dependency_canonical" 2>/dev/null)" == 644 ]] || return 1
    done
}

PLUGIN_ROOT="$(CDPATH= cd -- "$SKILL_DIR/../.." 2>/dev/null && pwd -P)" || PLUGIN_ROOT=""
if [[ -n "$PLUGIN_ROOT" ]] \
        && [[ -f "$PLUGIN_ROOT/.codex-plugin/plugin.json" ]] \
        && is_pipeline "$PLUGIN_ROOT"; then
    printf '%s\n' "$PLUGIN_ROOT"
    exit 0
fi

MARKER="$SKILL_DIR/.pipeline-root"
if [[ -f "$MARKER" ]]; then
    IFS= read -r INSTALLED_ROOT < "$MARKER" || true
    case "$INSTALLED_ROOT" in
        /*) ;;
        *)
            echo "agy-worker: invalid standalone pipeline marker" >&2
            exit 2
            ;;
    esac
    if is_pipeline "$INSTALLED_ROOT"; then
        printf '%s\n' "$INSTALLED_ROOT"
        exit 0
    fi

    echo "agy-worker: standalone pipeline marker does not name a complete runtime" >&2
    exit 2
fi

BUNDLED_RUNTIME="$SKILL_DIR/runtime"
if is_pipeline "$BUNDLED_RUNTIME"; then
    printf '%s\n' "$BUNDLED_RUNTIME"
    exit 0
fi

echo "agy-worker: pipeline not found beside the plugin, at the standalone install marker, or in the skill bundle" >&2
echo "agy-worker: reinstall a complete agy-worker skill bundle" >&2
exit 2
