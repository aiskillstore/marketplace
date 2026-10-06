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

    for required in workflow.sh agy-worker.sh qa-gate.sh verify-job.sh evidence-report.sh model-selection.sh doctor.sh ground-truth.sh delegation-policy.sh; do
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
    for parent in scripts schemas; do
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
        workflow.sh \
        agy-worker.sh \
        job.sh \
        qa-gate.sh \
        verify-job.sh \
        evidence-report.sh \
        model-selection.sh \
        doctor.sh \
        ground-truth.sh \
        delegation-policy.sh \
        scripts/workflow.py \
        scripts/validate-envelope.py \
        scripts/evidence_receipt.py \
        scripts/evidence_report.py \
        scripts/model_selection.py \
        scripts/candidate_state.py \
        scripts/agy_dispatch.py \
        scripts/job_lifecycle.py \
        scripts/delegation_policy.py; do
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
        scripts/agy_dispatch_containment.py \
        scripts/agy_dispatch_verification.py \
        scripts/launch_authority.py \
        schemas/workflow-state.schema.json \
        schemas/worker-result.schema.json \
        schemas/worker-result.provider.schema.json \
        schemas/evidence-receipt.schema.json \
        schemas/model-selection.schema.json \
        schemas/job-state.schema.json \
        schemas/delegation-policy.schema.json; do
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
        && { [[ -f "$PLUGIN_ROOT/.codex-plugin/plugin.json" ]] \
             || [[ -f "$PLUGIN_ROOT/.claude-plugin/plugin.json" ]]; } \
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
