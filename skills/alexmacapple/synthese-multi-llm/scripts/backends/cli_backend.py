"""
Backend CLI générique pour Synthèse Council.
PRD-008 Story 8.3: Support des CLI wrappers personnalisés.

Permet d'utiliser n'importe quel CLI comme backend LLM.

Configuration dans synthese.config.yaml:
    backends:
      cli:
        claude:
          command: "./wrappers/claude_wrapper.sh"
          args: ["-p"]
        custom_llm:
          command: "/usr/local/bin/my-llm"
          args: ["--prompt"]
"""

import asyncio
import os
import shutil
import time
from typing import Optional, Dict, Any, List

from .base import LLMBackend, LLMResponse, BackendRegistry


@BackendRegistry.register("cli")
class CLIBackend(LLMBackend):
    """
    Backend générique pour les CLI LLM.
    
    Permet d'appeler n'importe quel CLI qui accepte un prompt
    et retourne une réponse sur stdout.
    
    Example:
        >>> backend = CLIBackend(
        ...     name="claude",
        ...     command="claude",
        ...     args=["-p"]
        ... )
        >>> if backend.is_available():
        ...     response = await backend.call("Bonjour")
    """
    
    def __init__(
        self,
        cli_name: str = "generic",
        command: str = None,
        args: List[str] = None,
        env: Dict[str, str] = None
    ):
        """
        Initialise le backend CLI.
        
        Args:
            cli_name: Nom du CLI (pour l'affichage)
            command: Commande à exécuter
            args: Arguments avant le prompt
            env: Variables d'environnement additionnelles
        """
        self._cli_name = cli_name
        self._command = command
        self._args = args or []
        self._env = env or {}
    
    @property
    def name(self) -> str:
        """Identifiant unique du backend."""
        return f"cli:{self._cli_name}"
    
    @property
    def display_name(self) -> str:
        """Nom d'affichage."""
        return f"CLI {self._cli_name.title()}"
    
    @property
    def command(self) -> str:
        """Commande CLI."""
        return self._command or self._cli_name
    
    def is_available(self) -> bool:
        """
        Vérifie si le CLI est disponible.
        
        Cherche la commande dans le PATH.
        """
        cmd = self.command
        
        # Si c'est un chemin absolu, vérifier l'existence
        if os.path.isabs(cmd):
            return os.path.isfile(cmd) and os.access(cmd, os.X_OK)
        
        # Sinon chercher dans le PATH
        return shutil.which(cmd) is not None
    
    def get_config_help(self) -> str:
        """Instructions de configuration."""
        return f"""
Pour configurer le CLI {self._cli_name}:

1. Dans synthese.config.yaml:
   backends:
     cli:
       {self._cli_name}:
         command: "{self.command}"
         args: {self._args}

2. Ou créer un wrapper script:
   #!/bin/bash
   # wrappers/{self._cli_name}_wrapper.sh
   your-llm-command "$@"

3. Rendre exécutable:
   chmod +x wrappers/{self._cli_name}_wrapper.sh
"""
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Capacités du backend CLI."""
        return {
            "streaming": False,
            "vision": False,
            "function_calling": False,
            "json_mode": False
        }
    
    async def call(
        self,
        prompt: str,
        timeout: int = 300,
        **kwargs
    ) -> LLMResponse:
        """
        Appelle le CLI avec le prompt.
        
        Args:
            prompt: Texte du prompt
            timeout: Timeout en secondes
            **kwargs: Options additionnelles (ignorées)
            
        Returns:
            LLMResponse avec le résultat
        """
        start_time = time.time()
        
        try:
            # Construire la commande
            cmd = [self.command] + self._args + [prompt]
            
            # Préparer l'environnement
            env = os.environ.copy()
            env.update(self._env)
            
            # Créer le subprocess asynchrone
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Attendre avec timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                duration = time.time() - start_time
                return LLMResponse(
                    content="",
                    model=self._cli_name,
                    backend="cli",
                    duration=duration,
                    success=False,
                    error=f"Timeout après {timeout}s"
                )
            
            duration = time.time() - start_time
            
            if proc.returncode == 0:
                content = stdout.decode("utf-8", errors="replace").strip()
                return LLMResponse(
                    content=content,
                    model=self._cli_name,
                    backend="cli",
                    duration=duration,
                    success=True,
                    metadata={"returncode": proc.returncode}
                )
            else:
                error_msg = stderr.decode("utf-8", errors="replace").strip()
                return LLMResponse(
                    content="",
                    model=self._cli_name,
                    backend="cli",
                    duration=duration,
                    success=False,
                    error=f"Exit code {proc.returncode}: {error_msg[:200]}"
                )
                
        except FileNotFoundError:
            duration = time.time() - start_time
            return LLMResponse(
                content="",
                model=self._cli_name,
                backend="cli",
                duration=duration,
                success=False,
                error=f"Commande non trouvée: {self.command}"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return LLMResponse(
                content="",
                model=self._cli_name,
                backend="cli",
                duration=duration,
                success=False,
                error=f"Erreur: {type(e).__name__}: {e}"
            )


# Backends CLI préconfigurés pour les LLMs courants
PRECONFIGURED_CLIS = {
    "claude": {
        "command": "claude",
        "args": ["-p"],
        "description": "Anthropic Claude CLI"
    },
    "gemini": {
        "command": "gemini",
        "args": ["-p"],
        "description": "Google Gemini CLI"
    },
    "codex": {
        "command": "codex",
        "args": ["-q"],
        "description": "OpenAI Codex CLI"
    },
    "ollama": {
        "command": "ollama",
        "args": ["run", "llama2"],
        "description": "Ollama local LLM"
    },
    "llm": {
        "command": "llm",
        "args": [],
        "description": "Simon Willison's LLM CLI"
    }
}


def create_cli_backend(
    cli_name: str,
    config: Dict[str, Any] = None
) -> CLIBackend:
    """
    Crée un backend CLI à partir d'une configuration.
    
    Args:
        cli_name: Nom du CLI
        config: Configuration (command, args, env)
        
    Returns:
        Instance de CLIBackend
    """
    # Utiliser la config fournie ou les préconfigurés
    if config:
        return CLIBackend(
            cli_name=cli_name,
            command=config.get("command", cli_name),
            args=config.get("args", []),
            env=config.get("env", {})
        )
    elif cli_name in PRECONFIGURED_CLIS:
        preset = PRECONFIGURED_CLIS[cli_name]
        return CLIBackend(
            cli_name=cli_name,
            command=preset["command"],
            args=preset["args"]
        )
    else:
        # Backend générique
        return CLIBackend(cli_name=cli_name, command=cli_name)


def check_cli_availability(cli_name: str) -> tuple:
    """
    Vérifie la disponibilité d'un CLI.
    
    Returns:
        (available: bool, message: str)
    """
    backend = create_cli_backend(cli_name)
    
    if backend.is_available():
        cmd_path = shutil.which(backend.command) or backend.command
        return True, f"Trouvé: {cmd_path}"
    else:
        return False, f"{cli_name} non trouvé"
