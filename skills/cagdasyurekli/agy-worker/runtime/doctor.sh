#!/usr/bin/env bash
# Offline, read-only prerequisite diagnostics for the agy-worker pipeline.
set -uo pipefail

DOCTOR_SCHEMA_VERSION=1
DOCTOR_EXPECTED_AGY_SOURCE_REVISION='556846a4bb94117222f53846896c7eb0d645307e'

doctor_usage() {
    echo "usage: doctor.sh [--repo DIR] [--format text|json]" >&2
}

doctor_bash_compatible() {
    local major="$1" minor="$2"
    (( major > 3 || (major == 3 && minor >= 2) ))
}

doctor_script_dir() {
    local source_path="${BASH_SOURCE[0]}"
    case "$source_path" in
        */*) ;;
        *) source_path="$(command -v -- "$source_path" 2>/dev/null || true)" ;;
    esac
    [[ -n "$source_path" ]] || return 1
    CDPATH= cd -- "${source_path%/*}" 2>/dev/null && pwd -P
}

doctor_runtime_complete() {
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
        workflow.sh \
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
        model-intelligence.sh \
        model-evidence-campaign.sh \
        delegation-policy.sh \
        scripts/workflow.py \
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
        scripts/feedback-triage.py \
        scripts/model_intelligence.py \
        scripts/model_evidence_campaign.py \
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
        schemas/workflow-state.schema.json \
        scripts/version_manifest_engine.py \
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
        schemas/model-intelligence-evidence.schema.json \
        schemas/model-intelligence-advisory.schema.json \
        schemas/model-evidence-campaign-plan.schema.json \
        schemas/model-evidence-campaign-record.schema.json \
        schemas/model-evidence-campaign-evaluation.schema.json \
        schemas/model-evidence-campaign-aggregate.schema.json \
        schemas/model-evidence-campaign-aggregate-preview.schema.json \
        schemas/model-evidence-campaign-advisory-summary.schema.json \
        schemas/model-evidence-campaign-advisory-preview.schema.json \
        schemas/delegation-policy.schema.json \
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
        compat/model-intelligence/dataset.v1.json \
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
        compat/agy-models-inventory-binding.sha256 \
        compat/agy-version-manifest.json \
        compat/agy-version-manifest.sha256 \
        compat/version-manifest.schema.json; do
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

DOCTOR_WORK_DIR=''
DOCTOR_ACTIVE_PID=''
DOCTOR_INTERRUPTED=''
DOCTOR_CAPTURED_VERSION=''
DOCTOR_OLD_TMPDIR=''
DOCTOR_OLD_TMPDIR_SET=0
DOCTOR_OLD_TRAP_HUP=''
DOCTOR_OLD_TRAP_INT=''
DOCTOR_OLD_TRAP_TERM=''

doctor_canonical_dir() {
    CDPATH= cd -- "$1" 2>/dev/null && pwd -P
}

doctor_path_is_within() {
    local child="$1" parent="$2"
    [[ -n "$parent" ]] || return 1
    if [[ "$parent" == '/' ]]; then
        return 0
    fi
    case "$child" in
        "$parent"|"$parent"/*) return 0 ;;
        *) return 1 ;;
    esac
}

doctor_cleanup_workspace() {
    local workspace="${DOCTOR_WORK_DIR:-}" cleanup_failed=0
    [[ -n "$workspace" ]] || return 0
    case "$workspace" in
        /*/agy-worker-doctor.*) ;;
        *) return 1 ;;
    esac
    if [[ ! -d "$workspace" || -L "$workspace" || ! -O "$workspace" ]]; then
        return 1
    fi
    /bin/rm -f -- "$workspace/agy-version" "$workspace/xcrun_db" \
        2>/dev/null || cleanup_failed=1
    /bin/rmdir "$workspace" 2>/dev/null || cleanup_failed=1
    if (( cleanup_failed == 0 )); then
        DOCTOR_WORK_DIR=''
        return 0
    fi
    return 1
}

doctor_prepare_workspace() {
    local repo="$1" repo_dir='' home_dir='' base base_dir workspace old_umask rc
    local seen='|'

    repo_dir="$(doctor_canonical_dir "$repo")" || repo_dir=''
    if [[ -n "${HOME:-}" ]]; then
        home_dir="$(doctor_canonical_dir "$HOME")" || home_dir=''
    fi
    for base in /private/tmp /private/var/tmp /tmp /var/tmp; do
        base_dir="$(doctor_canonical_dir "$base")" || continue
        case "$seen" in
            *"|$base_dir|"*) continue ;;
        esac
        seen="$seen$base_dir|"
        [[ -d "$base_dir" && -w "$base_dir" && ! -L "$base" ]] || continue
        old_umask="$(umask)"
        umask 077
        workspace="$(/usr/bin/mktemp -d \
            "$base_dir/agy-worker-doctor.XXXXXX" 2>/dev/null)"
        rc=$?
        umask "$old_umask"
        [[ "$rc" == 0 && -n "$workspace" && -d "$workspace" \
            && ! -L "$workspace" && -O "$workspace" ]] || continue
        /bin/chmod 700 "$workspace" 2>/dev/null || {
            /bin/rmdir "$workspace" 2>/dev/null || true
            continue
        }
        workspace="$(doctor_canonical_dir "$workspace")" || continue
        if doctor_path_is_within "$workspace" "$repo_dir" \
                || doctor_path_is_within "$workspace" "$home_dir"; then
            /bin/rmdir "$workspace" 2>/dev/null || true
            continue
        fi
        DOCTOR_WORK_DIR="$workspace"
        return 0
    done
    return 1
}

doctor_note_signal() {
    local signal_name="$1" active_pid="${DOCTOR_ACTIVE_PID:-}"
    DOCTOR_INTERRUPTED="$signal_name"
    case "$active_pid" in
        ''|*[!0-9]*) ;;
        *)
            kill -s "$signal_name" "$active_pid" 2>/dev/null || true
            doctor_cleanup_workspace >/dev/null 2>&1 || true
            ;;
    esac
}

doctor_install_runtime_context() {
    DOCTOR_OLD_TRAP_HUP="$(trap -p HUP)"
    DOCTOR_OLD_TRAP_INT="$(trap -p INT)"
    DOCTOR_OLD_TRAP_TERM="$(trap -p TERM)"
    if [[ ${TMPDIR+x} ]]; then
        DOCTOR_OLD_TMPDIR_SET=1
        DOCTOR_OLD_TMPDIR="$TMPDIR"
    else
        DOCTOR_OLD_TMPDIR_SET=0
        DOCTOR_OLD_TMPDIR=''
    fi
    TMPDIR="$DOCTOR_WORK_DIR"
    export TMPDIR
    trap 'doctor_note_signal HUP' HUP
    trap 'doctor_note_signal INT' INT
    trap 'doctor_note_signal TERM' TERM
}

doctor_restore_one_trap() {
    local saved="$1" signal_name="$2"
    if [[ -n "$saved" ]]; then
        eval "$saved"
    else
        trap - "$signal_name"
    fi
}

doctor_restore_runtime_context() {
    if (( DOCTOR_OLD_TMPDIR_SET )); then
        TMPDIR="$DOCTOR_OLD_TMPDIR"
        export TMPDIR
    else
        unset TMPDIR
    fi
    doctor_restore_one_trap "$DOCTOR_OLD_TRAP_HUP" HUP
    doctor_restore_one_trap "$DOCTOR_OLD_TRAP_INT" INT
    doctor_restore_one_trap "$DOCTOR_OLD_TRAP_TERM" TERM
}

doctor_capture_agy_version() {
    local metadata_helper="$1" capture_file rc captured='' extra=''
    DOCTOR_CAPTURED_VERSION=''
    capture_file="$DOCTOR_WORK_DIR/agy-version"
    : > "$capture_file" 2>/dev/null || return 1
    /bin/chmod 600 "$capture_file" 2>/dev/null || return 1
    python3 -B "$metadata_helper" capture-agy-version \
        > "$capture_file" 2>/dev/null &
    DOCTOR_ACTIVE_PID=$!
    wait "$DOCTOR_ACTIVE_PID"
    rc=$?
    DOCTOR_ACTIVE_PID=''
    [[ -z "$DOCTOR_INTERRUPTED" ]] || return 130
    if [[ "$rc" == 0 && -f "$capture_file" && ! -L "$capture_file" ]]; then
        if { IFS= read -r captured && ! IFS= read -r extra; } < "$capture_file"; then
            DOCTOR_CAPTURED_VERSION="$captured"
        fi
    fi
    /bin/rm -f -- "$capture_file" 2>/dev/null || return 1
    [[ "$rc" == 0 && -n "$DOCTOR_CAPTURED_VERSION" ]] || return 1
    return 0
}

doctor_finish_interrupted() {
    [[ -n "$DOCTOR_INTERRUPTED" ]] || return 1
    doctor_cleanup_workspace >/dev/null 2>&1 || true
    doctor_restore_runtime_context
    echo "doctor: interrupted" >&2
    return 0
}

doctor_add_check() {
    local id="$1" status="$2" detail="$3"
    local index="${#DOCTOR_CHECK_IDS[@]}"
    DOCTOR_CHECK_IDS[$index]="$id"
    DOCTOR_CHECK_STATUSES[$index]="$status"
    DOCTOR_CHECK_DETAILS[$index]="$detail"
    case "$status" in
        not-ready) DOCTOR_HAS_NOT_READY=1 ;;
        review-required) DOCTOR_HAS_REVIEW_REQUIRED=1 ;;
    esac
}

doctor_print_text() {
    local index
    printf 'agy-worker doctor v%s\n' "$DOCTOR_SCHEMA_VERSION"
    printf 'overall: %s\n' "$DOCTOR_OVERALL"
    printf 'exit_code: %s\n' "$DOCTOR_EXIT"
    for (( index=0; index<${#DOCTOR_CHECK_IDS[@]}; index++ )); do
        printf 'check %s: %s - %s\n' \
            "${DOCTOR_CHECK_IDS[$index]}" \
            "${DOCTOR_CHECK_STATUSES[$index]}" \
            "${DOCTOR_CHECK_DETAILS[$index]}"
    done
    printf 'scope: offline-prerequisites-only\n'
    printf 'limitations: authentication, provider-availability, sandbox-permission, task-quality, future-dispatch\n'
}

doctor_print_json() {
    local index comma
    printf '{\n'
    printf '  "schema_version": %s,\n' "$DOCTOR_SCHEMA_VERSION"
    printf '  "kind": "agy-worker-doctor",\n'
    printf '  "overall": "%s",\n' "$DOCTOR_OVERALL"
    printf '  "exit_code": %s,\n' "$DOCTOR_EXIT"
    printf '  "checks": [\n'
    for (( index=0; index<${#DOCTOR_CHECK_IDS[@]}; index++ )); do
        comma=','
        if (( index + 1 == ${#DOCTOR_CHECK_IDS[@]} )); then
            comma=''
        fi
        printf '    {"id": "%s", "status": "%s", "detail": "%s"}%s\n' \
            "${DOCTOR_CHECK_IDS[$index]}" \
            "${DOCTOR_CHECK_STATUSES[$index]}" \
            "${DOCTOR_CHECK_DETAILS[$index]}" "$comma"
    done
    printf '  ],\n'
    printf '  "scope": "offline-prerequisites-only",\n'
    printf '  "limitations": ["authentication", "provider-availability", "sandbox-permission", "task-quality", "future-dispatch"]\n'
    printf '}\n'
}

doctor_main() {
    local repo='.' format='text' seen_repo=0 seen_format=0
    local runtime_dir metadata_helper version_file source_file review_file
    local runtime_ready=0 workspace_ready=0 python_ready=0 git_ready=0 repo_ready=0
    local output rc verified_version='' installed_version='' reviewed_source=''
    local worktree_line='' head_line=''
    local agy_rc=0
    local semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
    local head_re='^HEAD [0-9a-f]{40}$'
    local git_version_re='^git version [0-9]+(\.[0-9]+)+([[:space:]].*)?$'

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --repo)
                if (( seen_repo )) || [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
                    doctor_usage
                    return 64
                fi
                repo="$2"
                seen_repo=1
                shift 2
                ;;
            --format)
                if (( seen_format )) || [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
                    doctor_usage
                    return 64
                fi
                format="$2"
                seen_format=1
                shift 2
                ;;
            -h|--help)
                doctor_usage
                return 64
                ;;
            *)
                doctor_usage
                return 64
                ;;
        esac
    done
    case "$format" in
        text|json) ;;
        *) doctor_usage; return 64 ;;
    esac

    runtime_dir="$(doctor_script_dir)" || {
        echo "doctor: runtime location is unavailable" >&2
        return 3
    }
    metadata_helper="$runtime_dir/scripts/doctor-metadata.py"
    version_file="$runtime_dir/compat/agy-verified-version.txt"
    source_file="$runtime_dir/compat/agy-upstream-head.txt"
    review_file="$runtime_dir/compat/agy-last-reviewed.txt"

    DOCTOR_WORK_DIR=''
    DOCTOR_ACTIVE_PID=''
    DOCTOR_INTERRUPTED=''
    DOCTOR_CAPTURED_VERSION=''
    if doctor_prepare_workspace "$repo"; then
        workspace_ready=1
        doctor_install_runtime_context
    fi

    DOCTOR_CHECK_IDS=()
    DOCTOR_CHECK_STATUSES=()
    DOCTOR_CHECK_DETAILS=()
    DOCTOR_HAS_NOT_READY=0
    DOCTOR_HAS_REVIEW_REQUIRED=0

    if doctor_runtime_complete "$runtime_dir"; then
        runtime_ready=1
        doctor_add_check runtime_bundle ready complete
    else
        doctor_add_check runtime_bundle not-ready incomplete
    fi

    if (( workspace_ready )); then
        doctor_add_check private_workspace ready isolated
    else
        doctor_add_check private_workspace not-ready unavailable
    fi

    if doctor_bash_compatible "${BASH_VERSINFO[0]}" "${BASH_VERSINFO[1]}"; then
        doctor_add_check bash ready compatible
    else
        doctor_add_check bash not-ready requires-3.2-or-newer
    fi

    if (( workspace_ready )) && command -v python3 >/dev/null 2>&1 \
            && python3 -B -c 'import sys; raise SystemExit(0 if sys.version_info[0] == 3 else 1)' \
                >/dev/null 2>&1; then
        python_ready=1
        doctor_add_check python ready python3-available
    else
        doctor_add_check python not-ready python3-unavailable
    fi

    output=''
    if (( workspace_ready )) && command -v git >/dev/null 2>&1; then
        output="$(git --version 2>/dev/null)"
        rc=$?
        if [[ "$rc" == 0 && "$output" != *$'\n'* \
                && "$output" =~ $git_version_re ]]; then
            git_ready=1
        fi
    fi
    if (( git_ready )); then
        doctor_add_check git ready git-available
    else
        doctor_add_check git not-ready git-unavailable
    fi

    if (( git_ready )); then
        output="$(git -C "$repo" rev-parse --is-inside-work-tree 2>/dev/null)"
        rc=$?
        if [[ "$rc" == 0 && "$output" == 'true' ]]; then
            repo_ready=1
            doctor_add_check repository ready valid-git-worktree
        else
            doctor_add_check repository not-ready invalid-git-worktree
        fi
    else
        doctor_add_check repository not-ready git-unavailable
    fi

    if (( git_ready && repo_ready )); then
        output="$(git -C "$repo" worktree list --porcelain 2>/dev/null)"
        rc=$?
        worktree_line="${output%%$'\n'*}"
        if [[ "$output" == *$'\n'* ]]; then
            head_line="${output#*$'\n'}"
            head_line="${head_line%%$'\n'*}"
        fi
        if [[ "$rc" == 0 && "$worktree_line" == worktree\ /* \
                && "$head_line" =~ $head_re ]]; then
            doctor_add_check git_worktree ready supported
        else
            doctor_add_check git_worktree not-ready unsupported
        fi
    else
        doctor_add_check git_worktree not-ready prerequisites-unavailable
    fi

    if doctor_finish_interrupted; then
        return 3
    fi

    if (( workspace_ready )) && command -v agy >/dev/null 2>&1; then
        doctor_add_check agy ready present
        if (( runtime_ready && python_ready )) && [[ -x "$metadata_helper" ]]; then
            doctor_capture_agy_version "$metadata_helper"
            agy_rc=$?
            installed_version="$DOCTOR_CAPTURED_VERSION"
            if [[ "$agy_rc" != 0 || ! "$installed_version" =~ $semver_re ]]; then
                installed_version=''
            fi
        fi
    else
        doctor_add_check agy not-ready missing
    fi

    if (( runtime_ready && python_ready )) \
            && [[ -f "$metadata_helper" && -f "$version_file" ]]; then
        verified_version="$(python3 -B "$metadata_helper" version "$version_file" 2>/dev/null)"
        rc=$?
        if [[ "$rc" != 0 ]]; then
            verified_version=''
        fi
    fi
    if [[ ! -f "$version_file" || -L "$version_file" ]]; then
        doctor_add_check agy_version not-ready verified-metadata-unavailable
    elif [[ -z "$installed_version" ]]; then
        doctor_add_check agy_version not-ready invalid-version-output
    elif [[ -z "$verified_version" ]]; then
        doctor_add_check agy_version not-ready verified-metadata-unavailable
    elif [[ "$installed_version" == "$verified_version" ]]; then
        doctor_add_check agy_version ready verified-version-match
    else
        doctor_add_check agy_version review-required version-drift
    fi

    if (( runtime_ready && python_ready )) \
            && [[ -f "$metadata_helper" && -f "$source_file" && ! -L "$source_file" ]]; then
        reviewed_source="$(python3 -B "$metadata_helper" revision "$source_file" 2>/dev/null)"
        rc=$?
        if [[ "$rc" != 0 ]]; then
            reviewed_source=''
        fi
    fi
    if [[ ! -f "$source_file" || -L "$source_file" || -z "$reviewed_source" ]]; then
        doctor_add_check agy_source not-ready reviewed-source-metadata-unavailable
    elif [[ "$reviewed_source" == "$DOCTOR_EXPECTED_AGY_SOURCE_REVISION" ]]; then
        doctor_add_check agy_source ready reviewed-source-match
    else
        doctor_add_check agy_source not-ready reviewed-source-mismatch
    fi

    if (( runtime_ready && python_ready )) \
            && [[ -f "$metadata_helper" && -f "$review_file" ]]; then
        output="$(python3 -B "$metadata_helper" review "$review_file" 2>/dev/null)"
        rc=$?
        if [[ "$rc" == 0 && "$output" == 'fresh' ]]; then
            doctor_add_check compatibility_review ready fresh
        elif [[ "$rc" == 3 && "$output" == 'due' ]]; then
            doctor_add_check compatibility_review review-required due
        else
            doctor_add_check compatibility_review not-ready invalid
        fi
    else
        doctor_add_check compatibility_review not-ready metadata-unavailable
    fi

    if doctor_finish_interrupted; then
        return 3
    fi

    if (( workspace_ready )); then
        if ! doctor_cleanup_workspace; then
            DOCTOR_CHECK_STATUSES[1]='not-ready'
            DOCTOR_CHECK_DETAILS[1]='cleanup-failed'
            DOCTOR_HAS_NOT_READY=1
        fi
        doctor_restore_runtime_context
    fi

    if (( DOCTOR_HAS_NOT_READY )); then
        DOCTOR_OVERALL='not-ready'
        DOCTOR_EXIT=3
    elif (( DOCTOR_HAS_REVIEW_REQUIRED )); then
        DOCTOR_OVERALL='review-required'
        DOCTOR_EXIT=3
    else
        DOCTOR_OVERALL='ready'
        DOCTOR_EXIT=0
    fi

    if [[ "$format" == 'json' ]]; then
        doctor_print_json
    else
        doctor_print_text
    fi
    return "$DOCTOR_EXIT"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    doctor_main "$@"
fi
