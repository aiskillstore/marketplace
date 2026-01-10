"""
Interface abstraite pour les backends LLM.
PRD-008 Story 8.2: Architecture multi-backend.

Ce module définit le contrat que tous les backends LLM doivent respecter.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, AsyncIterator


@dataclass
class LLMResponse:
    """
    Réponse d'un appel LLM.
    
    Attributes:
        content: Contenu de la réponse
        model: Identifiant du modèle utilisé
        backend: Nom du backend (anthropic, openai, cli, etc.)
        duration: Durée de l'appel en secondes
        success: True si l'appel a réussi
        error: Message d'erreur si échec
        metadata: Métadonnées additionnelles (tokens, etc.)
        timestamp: Horodatage de la réponse
    """
    content: str
    model: str
    backend: str
    duration: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "content": self.content,
            "model": self.model,
            "backend": self.backend,
            "duration": self.duration,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class LLMBackend(ABC):
    """
    Interface abstraite pour les backends LLM.
    
    Tous les backends (Anthropic, OpenAI, CLI, etc.) doivent
    implémenter cette interface.
    
    Example:
        >>> backend = AnthropicBackend()
        >>> if backend.is_available():
        ...     response = await backend.call("Bonjour")
        ...     print(response.content)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Nom unique du backend.
        
        Returns:
            Identifiant du backend (ex: "anthropic", "openai", "cli:claude")
        """
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Nom d'affichage pour l'UI.
        
        Returns:
            Nom lisible (ex: "Anthropic Claude", "OpenAI GPT-4")
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Vérifie si le backend est disponible.
        
        Doit vérifier:
        - Présence des dépendances (packages)
        - Configuration (API keys, etc.)
        - Connectivité (optionnel)
        
        Returns:
            True si le backend peut être utilisé
        """
        pass
    
    @abstractmethod
    async def call(
        self, 
        prompt: str, 
        timeout: int = 60,
        **kwargs
    ) -> LLMResponse:
        """
        Appelle le LLM avec un prompt.
        
        Args:
            prompt: Texte du prompt
            timeout: Timeout en secondes
            **kwargs: Options spécifiques au backend
            
        Returns:
            LLMResponse avec le résultat
        """
        pass
    
    def get_config_help(self) -> str:
        """
        Retourne l'aide de configuration pour ce backend.
        
        Returns:
            Instructions pour configurer le backend
        """
        return f"Voir la documentation pour configurer {self.display_name}"
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """
        Capacités du backend.
        
        Returns:
            Dict avec les capacités supportées
        """
        return {
            "streaming": False,
            "vision": False,
            "function_calling": False,
            "json_mode": False
        }


class BackendRegistry:
    """
    Registre des backends disponibles.
    
    Permet de découvrir et instancier les backends automatiquement.
    
    Example:
        >>> BackendRegistry.register("anthropic")(AnthropicBackend)
        >>> backends = BackendRegistry.get_available()
    """
    
    _backends: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str):
        """
        Décorateur pour enregistrer un backend.
        
        Args:
            name: Nom unique du backend
        """
        def decorator(backend_class: type) -> type:
            cls._backends[name] = backend_class
            return backend_class
        return decorator
    
    @classmethod
    def get(cls, name: str) -> Optional[LLMBackend]:
        """
        Récupère une instance de backend par son nom.
        
        Args:
            name: Nom du backend
            
        Returns:
            Instance du backend ou None
        """
        backend_class = cls._backends.get(name)
        if backend_class:
            return backend_class()
        return None
    
    @classmethod
    def get_all(cls) -> Dict[str, LLMBackend]:
        """
        Récupère toutes les instances de backends.
        
        Returns:
            Dict name -> instance
        """
        return {name: cls() for name, cls in cls._backends.items()}
    
    @classmethod
    def get_available(cls) -> list:
        """
        Récupère les backends disponibles.
        
        Returns:
            Liste des backends dont is_available() == True
        """
        available = []
        for name, backend_class in cls._backends.items():
            try:
                instance = backend_class()
                if instance.is_available():
                    available.append(instance)
            except Exception:
                pass
        return available
    
    @classmethod
    def list_registered(cls) -> list:
        """
        Liste les noms des backends enregistrés.
        
        Returns:
            Liste des noms
        """
        return list(cls._backends.keys())
