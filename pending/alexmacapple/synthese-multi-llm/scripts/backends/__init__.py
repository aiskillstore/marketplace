"""
Package backends pour Synthèse Council.
PRD-008: Architecture multi-backend.

Ce package fournit une abstraction pour différents providers LLM:
- Anthropic (Claude) - API native
- CLI wrappers (claude, gemini, codex, ollama, etc.)
- OpenAI (GPT) - à venir

Usage:
    from backends import BackendRegistry, LLMBackend
    
    # Obtenir les backends disponibles
    backends = BackendRegistry.get_available()
    
    # Utiliser un backend spécifique
    anthropic = BackendRegistry.get("anthropic")
    if anthropic and anthropic.is_available():
        response = await anthropic.call("Mon prompt")
"""

from .base import (
    LLMBackend,
    LLMResponse,
    BackendRegistry
)

# Importer les backends pour les enregistrer automatiquement
try:
    from .anthropic_backend import (
        AnthropicBackend,
        check_anthropic_availability,
        ANTHROPIC_MODELS,
        DEFAULT_MODEL
    )
    ANTHROPIC_BACKEND_AVAILABLE = True
except ImportError:
    ANTHROPIC_BACKEND_AVAILABLE = False

try:
    from .cli_backend import (
        CLIBackend,
        create_cli_backend,
        check_cli_availability,
        PRECONFIGURED_CLIS
    )
    CLI_BACKEND_AVAILABLE = True
except ImportError:
    CLI_BACKEND_AVAILABLE = False

# Exports
__all__ = [
    # Base
    "LLMBackend",
    "LLMResponse", 
    "BackendRegistry",
    # Anthropic
    "AnthropicBackend",
    "check_anthropic_availability",
    "ANTHROPIC_MODELS",
    "DEFAULT_MODEL",
    # CLI
    "CLIBackend",
    "create_cli_backend",
    "check_cli_availability",
    "PRECONFIGURED_CLIS",
    # Flags
    "ANTHROPIC_BACKEND_AVAILABLE",
    "CLI_BACKEND_AVAILABLE"
]
