"""Platform contract definitions for cross-platform skill packages."""


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by cross_packager.py to keep platform contract data separate from packaging flow."


COMMON_REQUIRED_FIELDS = [
    "name",
    "description",
    "version",
    "display_name",
    "short_description",
    "default_prompt",
    "job_to_be_done",
    "ir_source",
    "ir_schema_version",
    "semantic_contract",
    "semantic_parity",
    "canonical_metadata",
    "canonical_format",
    "activation_mode",
    "execution_context",
    "shell",
    "trust_level",
    "remote_inline_execution",
    "degradation_strategy",
    "portability_profile",
    "permission_contract",
    "target_permission_contract",
    "target_native_contract",
]

STANDARD_FIELD_MAPPING = {
    "display_name": "adapter.display_name",
    "short_description": "adapter.short_description",
    "default_prompt": "adapter.default_prompt",
    "execution_context": "compatibility.execution.context",
    "shell": "compatibility.execution.shell",
}


def interface_field_mapping() -> dict[str, str]:
    return {
        "display_name": "interface.display_name",
        "short_description": "interface.short_description",
        "default_prompt": "interface.default_prompt",
        "execution_context": "compatibility.execution.context",
        "shell": "compatibility.execution.shell",
    }


PLATFORM_CONTRACTS = {
    "openai": {
        "required_fields": list(COMMON_REQUIRED_FIELDS),
        "required_files": ["targets/openai/adapter.json", "targets/openai/agents/openai.yaml"],
        "field_mapping": interface_field_mapping(),
    },
    "claude": {
        "required_fields": list(COMMON_REQUIRED_FIELDS),
        "required_files": ["targets/claude/adapter.json", "targets/claude/README.md"],
        "field_mapping": dict(STANDARD_FIELD_MAPPING),
    },
    "generic": {
        "required_fields": list(COMMON_REQUIRED_FIELDS),
        "required_files": ["targets/generic/adapter.json"],
        "field_mapping": dict(STANDARD_FIELD_MAPPING),
    },
    "vscode": {
        "required_fields": [
            "name",
            "description",
            "version",
            "display_name",
            "short_description",
            "default_prompt",
            "job_to_be_done",
            "ir_source",
            "ir_schema_version",
            "semantic_contract",
            "semantic_parity",
            "compiler",
            "compiled_contract",
            "permission_contract",
            "target_permission_contract",
            "target_native_contract",
            "target_transform",
            "canonical_metadata",
            "canonical_format",
            "activation_mode",
            "execution_context",
            "shell",
            "trust_level",
            "remote_inline_execution",
            "degradation_strategy",
            "portability_profile",
        ],
        "required_files": ["targets/vscode/adapter.json", "targets/vscode/README.md"],
        "field_mapping": {
            "name": "SKILL.md::frontmatter.name and folder name",
            "description": "SKILL.md::frontmatter.description",
            "display_name": "agents/interface.yaml::interface.display_name",
            "execution_context": "compatibility.execution.context",
            "permissions": "adapter.target_permission_contract",
        },
    },
}
