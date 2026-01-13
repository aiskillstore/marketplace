"""
Backend Anthropic pour Synthèse Council.
PRD-008 Story 8.2: Support natif de l'API Anthropic.

Utilise le package anthropic pour appeler Claude directement,
sans passer par un CLI wrapper.

Configuration:
    - ANTHROPIC_API_KEY: Clé API (env var ou config)
    - Modèle par défaut: claude-3-5-sonnet-20241022
"""

import os
import time
import asyncio
from typing import Optional, Dict, Any

from .base import LLMBackend, LLMResponse, BackendRegistry


# Vérifier si le package anthropic est installé
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# Modèles supportés avec leurs caractéristiques
ANTHROPIC_MODELS = {
    "claude-3-5-sonnet-20241022": {
        "display_name": "Claude 3.5 Sonnet",
        "max_tokens": 8192,
        "context_window": 200000
    },
    "claude-3-opus-20240229": {
        "display_name": "Claude 3 Opus",
        "max_tokens": 4096,
        "context_window": 200000
    },
    "claude-3-sonnet-20240229": {
        "display_name": "Claude 3 Sonnet",
        "max_tokens": 4096,
        "context_window": 200000
    },
    "claude-3-haiku-20240307": {
        "display_name": "Claude 3 Haiku",
        "max_tokens": 4096,
        "context_window": 200000
    }
}

DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


@BackendRegistry.register("anthropic")
class AnthropicBackend(LLMBackend):
    """
    Backend pour l'API Anthropic.
    
    Utilise le package anthropic officiel pour appeler Claude.
    
    Configuration:
        - ANTHROPIC_API_KEY env var
        - ou api_key dans le constructeur
        
    Example:
        >>> backend = AnthropicBackend()
        >>> if backend.is_available():
        ...     response = await backend.call("Résume ce texte: ...")
        ...     print(response.content)
    """
    
    def __init__(
        self, 
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        max_tokens: int = 4096
    ):
        """
        Initialise le backend Anthropic.
        
        Args:
            model: ID du modèle à utiliser
            api_key: Clé API (ou ANTHROPIC_API_KEY env var)
            max_tokens: Nombre max de tokens en sortie
        """
        self.model = model
        self._api_key = api_key
        self.max_tokens = max_tokens
        self._client = None
    
    @property
    def name(self) -> str:
        """Identifiant unique du backend."""
        return f"anthropic:{self.model}"
    
    @property
    def display_name(self) -> str:
        """Nom d'affichage."""
        model_info = ANTHROPIC_MODELS.get(self.model, {})
        model_name = model_info.get("display_name", self.model)
        return f"Anthropic {model_name}"
    
    @property
    def api_key(self) -> Optional[str]:
        """Récupère la clé API."""
        return self._api_key or os.getenv("ANTHROPIC_API_KEY")
    
    def is_available(self) -> bool:
        """
        Vérifie si le backend est disponible.
        
        Conditions:
        - Package anthropic installé
        - ANTHROPIC_API_KEY défini
        """
        if not ANTHROPIC_AVAILABLE:
            return False
        
        if not self.api_key:
            return False
        
        return True
    
    def get_config_help(self) -> str:
        """Instructions de configuration."""
        return """
Pour utiliser le backend Anthropic:

1. Installer le package:
   pip install anthropic

2. Définir la clé API:
   export ANTHROPIC_API_KEY="sk-ant-..."
   
   Ou dans synthese.config.yaml:
   backends:
     anthropic:
       api_key: "sk-ant-..."

3. (Optionnel) Choisir le modèle:
   backends:
     anthropic:
       model: claude-3-5-sonnet-20241022

Modèles disponibles:
- claude-3-5-sonnet-20241022 (recommandé)
- claude-3-opus-20240229 (plus puissant)
- claude-3-sonnet-20240229
- claude-3-haiku-20240307 (plus rapide)
"""
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Capacités du backend Anthropic."""
        return {
            "streaming": True,
            "vision": True,
            "function_calling": True,
            "json_mode": False
        }
    
    def _get_client(self):
        """Récupère ou crée le client Anthropic."""
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("Package anthropic non installé")
        
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=self.api_key)
        
        return self._client
    
    async def call(
        self,
        prompt: str,
        timeout: int = 60,
        **kwargs
    ) -> LLMResponse:
        """
        Appelle l'API Anthropic.
        
        Args:
            prompt: Texte du prompt
            timeout: Timeout en secondes
            **kwargs: Options additionnelles
                - system: System prompt
                - max_tokens: Override max_tokens
                - temperature: 0.0-1.0
                
        Returns:
            LLMResponse avec le résultat
        """
        start_time = time.time()
        
        try:
            # Paramètres de l'appel
            system = kwargs.get("system", "Tu es un assistant expert en synthèse de textes.")
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            temperature = kwargs.get("temperature", 0.7)
            
            # Exécuter l'appel dans un thread pool pour ne pas bloquer
            client = self._get_client()
            
            # Utiliser asyncio.to_thread pour l'appel synchrone
            def sync_call():
                return client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    timeout=timeout
                )
            
            # Exécuter avec timeout
            message = await asyncio.wait_for(
                asyncio.to_thread(sync_call),
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            # Extraire le contenu
            content = ""
            if message.content:
                for block in message.content:
                    if hasattr(block, 'text'):
                        content += block.text
            
            # Métadonnées
            metadata = {
                "input_tokens": message.usage.input_tokens if message.usage else 0,
                "output_tokens": message.usage.output_tokens if message.usage else 0,
                "stop_reason": message.stop_reason,
                "model_id": message.model
            }
            
            return LLMResponse(
                content=content,
                model=self.model,
                backend="anthropic",
                duration=duration,
                success=True,
                metadata=metadata
            )
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            return LLMResponse(
                content="",
                model=self.model,
                backend="anthropic",
                duration=duration,
                success=False,
                error=f"Timeout après {timeout}s"
            )
            
        except Exception as e:
            duration = time.time() - start_time

            # Handle specific Anthropic errors if package is available
            if ANTHROPIC_AVAILABLE:
                if isinstance(e, anthropic.APIConnectionError):
                    return LLMResponse(
                        content="",
                        model=self.model,
                        backend="anthropic",
                        duration=duration,
                        success=False,
                        error=f"Erreur de connexion: {e}"
                    )
                elif isinstance(e, anthropic.RateLimitError):
                    return LLMResponse(
                        content="",
                        model=self.model,
                        backend="anthropic",
                        duration=duration,
                        success=False,
                        error=f"Rate limit dépassé: {e}"
                    )
                elif isinstance(e, anthropic.APIStatusError):
                    return LLMResponse(
                        content="",
                        model=self.model,
                        backend="anthropic",
                        duration=duration,
                        success=False,
                        error=f"Erreur API ({e.status_code}): {e.message}"
                    )

            # Generic exception handler
            return LLMResponse(
                content="",
                model=self.model,
                backend="anthropic",
                duration=duration,
                success=False,
                error=f"Erreur inattendue: {type(e).__name__}: {e}"
            )


def check_anthropic_availability() -> tuple:
    """
    Vérifie la disponibilité du backend Anthropic.
    
    Returns:
        (available: bool, message: str)
    """
    if not ANTHROPIC_AVAILABLE:
        return False, "Package 'anthropic' non installé (pip install anthropic)"
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return False, "ANTHROPIC_API_KEY non défini"
    
    # Masquer la clé pour l'affichage
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    return True, f"API key: {masked_key}"
