from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by compile_skill for target platform model and contract builders."


TARGET_TRANSFORMS: dict[str, dict[str, Any]] = {
    "openai": {
        "adapter_mode": "metadata-adapter",
        "generated_files": ["targets/openai/adapter.json", "targets/openai/agents/openai.yaml"],
        "metadata_mapping": {
            "display_name": "targets/openai/agents/openai.yaml::interface.display_name",
            "default_prompt": "targets/openai/agents/openai.yaml::interface.default_prompt",
            "activation": "targets/openai/agents/openai.yaml::compatibility.activation_mode",
            "execution": "targets/openai/agents/openai.yaml::compatibility.execution_context",
            "trust": "targets/openai/agents/openai.yaml::compatibility.trust_level",
            "permissions": "targets/openai/agents/openai.yaml::compatibility.permission_contract",
            "degradation": "targets/openai/agents/openai.yaml::compatibility.degradation_strategy",
        },
        "preserved_semantics": ["trigger", "workflow-counts", "resources", "eval-plan", "risk", "governance", "runtime", "trust", "permissions"],
        "unsupported_features": ["client-native script permission prompts are represented as permission contract metadata"],
    },
    "claude": {
        "adapter_mode": "neutral-source-plus-adapter",
        "generated_files": ["targets/claude/adapter.json", "targets/claude/README.md"],
        "metadata_mapping": {
            "display_name": "targets/claude/adapter.json::display_name",
            "default_prompt": "targets/claude/adapter.json::default_prompt",
            "activation": "targets/claude/adapter.json::activation_mode",
            "execution": "targets/claude/adapter.json::execution_context",
            "trust": "targets/claude/adapter.json::trust_level",
            "permissions": "targets/claude/adapter.json::target_permission_contract",
            "degradation": "targets/claude/adapter.json::degradation_strategy",
        },
        "preserved_semantics": ["trigger", "workflow-counts", "resources", "eval-plan", "risk", "governance", "runtime", "trust", "permissions"],
        "unsupported_features": ["vendor-native metadata fields are carried as adapter JSON and README notes"],
    },
    "generic": {
        "adapter_mode": "agent-skills-compatible",
        "generated_files": ["targets/generic/adapter.json"],
        "metadata_mapping": {
            "display_name": "targets/generic/adapter.json::display_name",
            "default_prompt": "targets/generic/adapter.json::default_prompt",
            "activation": "targets/generic/adapter.json::activation_mode",
            "execution": "targets/generic/adapter.json::execution_context",
            "trust": "targets/generic/adapter.json::trust_level",
            "permissions": "targets/generic/adapter.json::target_permission_contract",
            "degradation": "targets/generic/adapter.json::degradation_strategy",
        },
        "preserved_semantics": ["trigger", "workflow-counts", "resources", "eval-plan", "risk", "governance", "runtime", "trust", "permissions"],
        "unsupported_features": [],
    },
    "agent-skills-compatible": {
        "adapter_mode": "neutral-agent-skills-source",
        "generated_files": ["SKILL.md", "agents/interface.yaml"],
        "metadata_mapping": {
            "name": "SKILL.md::frontmatter.name",
            "description": "SKILL.md::frontmatter.description",
            "interface": "agents/interface.yaml",
            "manifest": "manifest.json",
        },
        "preserved_semantics": ["trigger", "workflow", "resources", "eval-plan", "risk", "governance", "runtime", "trust", "permissions"],
        "unsupported_features": [],
    },
    "agent-skills": {
        "adapter_mode": "neutral-agent-skills-source",
        "generated_files": ["SKILL.md", "agents/interface.yaml"],
        "metadata_mapping": {
            "name": "SKILL.md::frontmatter.name",
            "description": "SKILL.md::frontmatter.description",
            "interface": "agents/interface.yaml",
            "manifest": "manifest.json",
        },
        "preserved_semantics": ["trigger", "workflow", "resources", "eval-plan", "risk", "governance", "runtime", "trust", "permissions"],
        "unsupported_features": [],
    },
    "vscode": {
        "adapter_mode": "vscode-agent-skills-adapter",
        "generated_files": ["targets/vscode/adapter.json", "targets/vscode/README.md"],
        "metadata_mapping": {
            "name": "folder-name-and-SKILL.md::frontmatter.name",
            "description": "SKILL.md::frontmatter.description",
            "interface": "agents/interface.yaml",
            "permissions": "targets/vscode/adapter.json::target_permission_contract",
            "install_scope": "targets/vscode/README.md",
        },
        "preserved_semantics": ["trigger", "workflow", "resources", "eval-plan", "risk", "governance", "runtime", "trust", "permissions"],
        "unsupported_features": ["VS Code installation scope is documented but not installed by this compiler"],
    },
}


TARGET_PERMISSION_MODELS = {
    "openai": {
        "model": "metadata-only",
        "native_enforcement": False,
        "representation": "targets/openai/agents/openai.yaml::compatibility.permission_contract plus adapter.json",
        "operator_note": "OpenAI target carries permission metadata for reviewer visibility; host enforcement remains outside the package.",
    },
    "claude": {
        "model": "neutral-source-plus-adapter",
        "native_enforcement": False,
        "representation": "targets/claude/adapter.json::target_permission_contract and README notes",
        "operator_note": "Claude-compatible package keeps permission intent in adapter metadata for install review.",
    },
    "generic": {
        "model": "agent-skills-compatible-metadata",
        "native_enforcement": False,
        "representation": "targets/generic/adapter.json::target_permission_contract",
        "operator_note": "Generic target exposes permission metadata for downstream clients to enforce or review.",
    },
    "vscode": {
        "model": "vscode-workspace-trust-plus-metadata",
        "native_enforcement": False,
        "representation": "targets/vscode/adapter.json::target_permission_contract and targets/vscode/README.md install notes",
        "operator_note": "VS Code target relies on project or user skill installation plus VS Code workspace trust; Yao preserves permission metadata for reviewer and installer checks.",
    },
}


TARGET_NATIVE_MODELS = {
    "openai": {
        "native_surface": "OpenAI-style interface metadata plus neutral Agent Skills source",
        "activation_policy": "Use frontmatter description for catalog routing and targets/openai/agents/openai.yaml for display name, default prompt, and compatibility metadata.",
        "resource_strategy": "Ship the neutral source tree and expose OpenAI-facing interface metadata as a generated companion file.",
        "script_strategy": "Keep scripts as local package resources; expose help-smoke and permission metadata for reviewer approval before execution.",
        "permission_enforcement": "metadata-only",
        "install_scope": "plugin or skill package consumer",
        "review_artifacts": ["targets/openai/agents/openai.yaml", "targets/openai/adapter.json", "reports/review-studio.html"],
        "fallback_behavior": "If OpenAI-native metadata is ignored, the package remains readable as neutral Agent Skills source.",
        "unsupported_native_features": [
            "client-native permission prompts",
            "provider-executed scripts",
        ],
    },
    "claude": {
        "native_surface": "Claude-compatible neutral source folder with adapter notes",
        "activation_policy": "Use SKILL.md frontmatter description as the primary activation contract and adapter.json for review metadata.",
        "resource_strategy": "Preserve the source tree directly; write target notes in targets/claude/README.md.",
        "script_strategy": "Scripts remain local package resources and must be reviewed through trust and permission reports before use.",
        "permission_enforcement": "metadata-fallback",
        "install_scope": "user or project skill directory",
        "review_artifacts": ["targets/claude/README.md", "targets/claude/adapter.json", "reports/review-studio.html"],
        "fallback_behavior": "If Claude-specific metadata is not consumed, SKILL.md and references remain the source of truth.",
        "unsupported_native_features": [
            "vendor-native permission enforcement",
            "provider-specific execution transforms",
        ],
    },
    "generic": {
        "native_surface": "Agent Skills compatible neutral package",
        "activation_policy": "Use SKILL.md name and description; consumers decide automatic or manual activation.",
        "resource_strategy": "Preserve references, scripts, assets, evals, reports, and adapter metadata as relative package resources.",
        "script_strategy": "Expose script and permission metadata for downstream clients or installers to enforce.",
        "permission_enforcement": "consumer-enforced-or-metadata-only",
        "install_scope": "generic Agent Skills compatible root",
        "review_artifacts": ["targets/generic/adapter.json", "reports/review-studio.html"],
        "fallback_behavior": "Neutral source is the runtime fallback.",
        "unsupported_native_features": [],
    },
    "agent-skills-compatible": {
        "native_surface": "Agent Skills standard source tree",
        "activation_policy": "Use SKILL.md frontmatter name and description for progressive disclosure.",
        "resource_strategy": "Keep optional directories as relative resources next to SKILL.md.",
        "script_strategy": "Scripts remain local optional resources and should advertise --help when executable.",
        "permission_enforcement": "consumer-enforced-or-metadata-only",
        "install_scope": "Agent Skills source root",
        "review_artifacts": ["SKILL.md", "agents/interface.yaml", "reports/review-studio.html"],
        "fallback_behavior": "The source tree itself is the target artifact.",
        "unsupported_native_features": [],
    },
    "agent-skills": {
        "native_surface": "Agent Skills standard source tree",
        "activation_policy": "Use SKILL.md frontmatter name and description for progressive disclosure.",
        "resource_strategy": "Keep optional directories as relative resources next to SKILL.md.",
        "script_strategy": "Scripts remain local optional resources and should advertise --help when executable.",
        "permission_enforcement": "consumer-enforced-or-metadata-only",
        "install_scope": "Agent Skills source root",
        "review_artifacts": ["SKILL.md", "agents/interface.yaml", "reports/review-studio.html"],
        "fallback_behavior": "The source tree itself is the target artifact.",
        "unsupported_native_features": [],
    },
    "vscode": {
        "native_surface": "VS Code/Copilot Agent Skills project or user scope",
        "activation_policy": "Use folder name plus SKILL.md name/description; keep description under platform limits.",
        "resource_strategy": "Install as project or user scoped skill source, preserving relative references and scripts.",
        "script_strategy": "Scripts require workspace trust and operator/client approval outside this compiler.",
        "permission_enforcement": "client-or-workspace-trust",
        "install_scope": "VS Code user or project skills directory",
        "review_artifacts": ["SKILL.md", "agents/interface.yaml", "reports/review-studio.html"],
        "fallback_behavior": "If VS Code scope is not installed, use the neutral Agent Skills source.",
        "unsupported_native_features": [
            "automatic VS Code installation",
        ],
    },
}


def target_permission_contract(target: str, permissions: dict[str, Any]) -> dict[str, Any]:
    model = TARGET_PERMISSION_MODELS.get(
        target,
        {
            "model": "metadata-only",
            "native_enforcement": False,
            "representation": "adapter metadata",
            "operator_note": "Permission semantics are preserved as metadata for reviewer visibility.",
        },
    )
    return {
        "schema_version": "1.0",
        "target": target,
        "permission_model": model["model"],
        "native_enforcement": model["native_enforcement"],
        "representation": model["representation"],
        "review_required": bool(permissions.get("review_required")),
        "declared_capabilities": permissions.get("declared_capabilities", []),
        "capability_counts": {
            name: item.get("script_count", 0)
            for name, item in permissions.get("capabilities", {}).items()
        },
        "evidence": permissions.get("source", ""),
        "operator_note": model["operator_note"],
    }


def target_native_contract(
    target: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    target_permissions: dict[str, Any],
) -> dict[str, Any]:
    model = TARGET_NATIVE_MODELS.get(
        target,
        {
            "native_surface": "adapter metadata",
            "activation_policy": "Carry activation semantics as metadata for the target consumer.",
            "resource_strategy": "Preserve neutral package resources.",
            "script_strategy": "Expose script metadata for reviewer visibility.",
            "permission_enforcement": "metadata-only",
            "install_scope": "target consumer",
            "review_artifacts": ["adapter.json", "reports/review-studio.html"],
            "fallback_behavior": "Use neutral source package.",
            "unsupported_native_features": [],
        },
    )
    return {
        "schema_version": "1.0",
        "target": target,
        "native_surface": model["native_surface"],
        "activation": {
            "policy": model["activation_policy"],
            "trigger_description": contract.get("trigger", {}).get("description", ""),
            "manual_activation_supported": True,
            "automatic_activation_note": "Depends on the target client route/catalog implementation.",
        },
        "resources": {
            "strategy": model["resource_strategy"],
            "counts": contract.get("resources", {}).get("counts", {}),
            "generated_files": profile.get("generated_files", []),
        },
        "scripts": {
            "strategy": model["script_strategy"],
            "script_count": contract.get("resources", {}).get("counts", {}).get("scripts", 0),
            "help_smoke_failed_count": contract.get("permissions", {}).get("help_smoke", {}).get("failed_count", 0),
        },
        "permissions": {
            "enforcement": model["permission_enforcement"],
            "native_enforcement": bool(target_permissions.get("native_enforcement")),
            "declared_capabilities": target_permissions.get("declared_capabilities", []),
            "review_required": bool(target_permissions.get("review_required")),
        },
        "review": {
            "artifacts": model["review_artifacts"],
            "fallback_behavior": model["fallback_behavior"],
            "unsupported_native_features": [
                *model.get("unsupported_native_features", []),
                *profile.get("unsupported_features", []),
            ],
        },
        "install_scope": model["install_scope"],
    }
