"""
Module de retry avec backoff exponentiel pour Synthèse Council.
PRD-004: Résilience face aux échecs transitoires.

Fonctionnalités:
- Décorateur @retry avec backoff exponentiel
- Jitter aléatoire pour éviter thundering herd
- Classification automatique des erreurs retryables
- Métriques de retry pour diagnostic
"""

import asyncio
import random
import re
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Callable, Tuple, Type, Optional, Dict, List, Any, Union
import logging

# Logger pour les retries
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION PAR DÉFAUT
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_RETRY_CONFIG = {
    "enabled": True,
    "max_attempts": 3,
    "base_delay": 2.0,
    "max_delay": 30.0,
    "exponential_base": 2.0,
    "jitter": 0.1,
    "additional_patterns": []
}


# ══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION DES ERREURS (Story 4.3)
# ══════════════════════════════════════════════════════════════════════════════

class RetryableError(Exception):
    """Exception marquée comme retryable."""
    pass


class NonRetryableError(Exception):
    """Exception marquée comme non-retryable."""
    pass


# Patterns pour détecter les erreurs retryables
RETRYABLE_PATTERNS = [
    r"timeout",
    r"timed?\s*out",
    r"429",
    r"rate\s*limit",
    r"too\s*many\s*requests",
    r"connection\s*(refused|reset|error)",
    r"temporary\s*(failure|error)",
    r"service\s*unavailable",
    r"503",
    r"502",
    r"504",
    r"overloaded",
    r"try\s*again",
    r"retry",
]

# Patterns pour les erreurs NON-retryables
NON_RETRYABLE_PATTERNS = [
    r"not\s*found",
    r"401",
    r"403",
    r"unauthorized",
    r"forbidden",
    r"invalid\s*(prompt|input|request)",
    r"authentication\s*failed",
    r"permission\s*denied",
]


def is_retryable(
    error: Union[Exception, str],
    additional_patterns: List[str] = None
) -> bool:
    """
    Détermine si une erreur est retryable (transitoire).
    
    Args:
        error: Exception ou message d'erreur
        additional_patterns: Patterns supplémentaires à considérer retryables
        
    Returns:
        True si l'erreur est retryable
    """
    # Exceptions Python explicitement retryables
    if isinstance(error, (
        TimeoutError,
        ConnectionError,
        ConnectionRefusedError,
        ConnectionResetError,
        asyncio.TimeoutError,
        RetryableError
    )):
        return True
    
    # Exceptions Python explicitement non-retryables
    if isinstance(error, (
        FileNotFoundError,
        PermissionError,
        ValueError,
        TypeError,
        NonRetryableError
    )):
        return False
    
    # Analyse du message d'erreur
    message = str(error).lower()
    
    # Vérifier d'abord les patterns non-retryables
    for pattern in NON_RETRYABLE_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return False
    
    # Vérifier les patterns retryables
    all_patterns = RETRYABLE_PATTERNS + (additional_patterns or [])
    for pattern in all_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    
    # Par défaut, les erreurs inconnues ne sont pas retryées
    return False


def classify_error(error: Union[Exception, str]) -> str:
    """
    Classifie une erreur pour le logging.
    
    Returns:
        Catégorie de l'erreur (timeout, rate_limit, connection, auth, unknown)
    """
    message = str(error).lower()
    
    if re.search(r"timeout|timed?\s*out", message):
        return "timeout"
    elif re.search(r"429|rate\s*limit|too\s*many", message):
        return "rate_limit"
    elif re.search(r"connection|refused|reset", message):
        return "connection"
    elif re.search(r"401|403|auth|unauthorized|forbidden", message):
        return "auth"
    elif re.search(r"not\s*found|404", message):
        return "not_found"
    else:
        return "unknown"


# ══════════════════════════════════════════════════════════════════════════════
# MÉTRIQUES DE RETRY (Story 4.6)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class RetryEvent:
    """Événement de retry détaillé. PRD-027 Story 27.2."""
    timestamp: float
    model: str
    attempt: int
    reason: str
    delay: float
    error_snippet: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "model": self.model,
            "attempt": self.attempt,
            "reason": self.reason,
            "delay": round(self.delay, 2),
            "error_snippet": self.error_snippet
        }


@dataclass
class RetryMetrics:
    """Métriques de retry pour un modèle."""
    total_attempts: int = 0
    successful_retries: int = 0
    failed_attempts: int = 0
    reasons: List[str] = field(default_factory=list)
    total_retry_time: float = 0.0
    events: List[RetryEvent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON."""
        return {
            "total_attempts": self.total_attempts,
            "successful_retries": self.successful_retries,
            "failed_attempts": self.failed_attempts,
            "reasons": self.reasons,
            "total_retry_time": round(self.total_retry_time, 2),
            "events": [e.to_dict() for e in self.events]
        }


class RetryMetricsCollector:
    """Collecteur de métriques de retry."""
    
    def __init__(self):
        self._metrics: Dict[str, RetryMetrics] = {}
    
    def get_metrics(self, model: str) -> RetryMetrics:
        """Récupère ou crée les métriques pour un modèle."""
        if model not in self._metrics:
            self._metrics[model] = RetryMetrics()
        return self._metrics[model]
    
    def record_attempt(self, model: str):
        """Enregistre une tentative."""
        self.get_metrics(model).total_attempts += 1
    
    def record_retry(self, model: str, reason: str, delay: float,
                     attempt: int = 0, error_snippet: str = ""):
        """Enregistre un retry avec événement détaillé. PRD-027 Story 27.2."""
        metrics = self.get_metrics(model)
        if reason not in metrics.reasons:
            metrics.reasons.append(reason)
        metrics.total_retry_time += delay

        # Capturer l'événement détaillé
        event = RetryEvent(
            timestamp=time.time(),
            model=model,
            attempt=attempt,
            reason=reason,
            delay=delay,
            error_snippet=error_snippet[:200] if error_snippet else ""
        )
        metrics.events.append(event)
    
    def record_success_after_retry(self, model: str):
        """Enregistre un succès après retry."""
        self.get_metrics(model).successful_retries += 1
    
    def record_failure(self, model: str):
        """Enregistre un échec final."""
        self.get_metrics(model).failed_attempts += 1
    
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Exporte toutes les métriques."""
        return {
            model: metrics.to_dict()
            for model, metrics in self._metrics.items()
        }
    
    def summary(self) -> str:
        """Résumé textuel des métriques."""
        if not self._metrics:
            return "Aucun retry"
        
        lines = []
        total_retries = sum(m.total_attempts - 1 for m in self._metrics.values() if m.total_attempts > 1)
        
        if total_retries == 0:
            return "Aucun retry nécessaire"
        
        lines.append(f"Retries: {total_retries} total")
        
        for model, metrics in self._metrics.items():
            retries = metrics.total_attempts - 1
            if retries > 0:
                status = "✓" if metrics.successful_retries > 0 else "✗"
                lines.append(f"  {status} {model}: {retries} retry(s)")
        
        return "\n".join(lines)


# Instance globale pour collecter les métriques
_global_metrics = RetryMetricsCollector()


def get_retry_metrics() -> RetryMetricsCollector:
    """Récupère le collecteur de métriques global."""
    return _global_metrics


def reset_retry_metrics():
    """Réinitialise les métriques (pour les tests)."""
    global _global_metrics
    _global_metrics = RetryMetricsCollector()


# ══════════════════════════════════════════════════════════════════════════════
# CALLBACKS DE PROGRESSION (Story 4.5)
# ══════════════════════════════════════════════════════════════════════════════

class RetryCallback:
    """Callback pour notifier les événements de retry."""
    
    async def on_retry(self, model: str, attempt: int, max_attempts: int, 
                       delay: float, reason: str):
        """Appelé avant chaque retry."""
        pass
    
    async def on_success(self, model: str, attempt: int):
        """Appelé après un succès."""
        pass
    
    async def on_failure(self, model: str, attempts: int, reason: str):
        """Appelé après échec de tous les retries."""
        pass


class PrintRetryCallback(RetryCallback):
    """Callback qui affiche les événements de retry."""
    
    def __init__(self, printer=None):
        self.printer = printer
    
    async def on_retry(self, model: str, attempt: int, max_attempts: int,
                       delay: float, reason: str):
        message = f"    ↻ Retry {attempt}/{max_attempts} dans {delay:.1f}s ({reason})"
        if self.printer:
            await self.printer.print(message)
        else:
            print(message)
    
    async def on_success(self, model: str, attempt: int):
        if attempt > 1:
            message = f"    ✓ Succès après {attempt} tentative(s)"
            if self.printer:
                await self.printer.print(message)
            else:
                print(message)
    
    async def on_failure(self, model: str, attempts: int, reason: str):
        message = f"    ✗ Échec après {attempts} tentative(s) ({reason})"
        if self.printer:
            await self.printer.print(message)
        else:
            print(message)


# ══════════════════════════════════════════════════════════════════════════════
# DÉCORATEUR RETRY (Story 4.1)
# ══════════════════════════════════════════════════════════════════════════════

def calculate_delay(
    attempt: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: float
) -> float:
    """
    Calcule le délai avant le prochain retry.
    
    Args:
        attempt: Numéro de la tentative (1-based)
        base_delay: Délai de base en secondes
        max_delay: Délai maximum
        exponential_base: Base de l'exponentielle
        jitter: Variation aléatoire (±jitter%)
        
    Returns:
        Délai en secondes avec jitter
    """
    # Backoff exponentiel: delay = base * (exponential_base ^ (attempt - 1))
    delay = base_delay * (exponential_base ** (attempt - 1))
    
    # Plafonner au max_delay
    delay = min(delay, max_delay)
    
    # Ajouter le jitter
    jitter_range = delay * jitter
    delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, delay)


def retry(
    max_attempts: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: float = 0.1,
    retryable_exceptions: Tuple[Type[Exception], ...] = None,
    callback: Optional[RetryCallback] = None,
    model_name: str = None,
    metrics_collector: RetryMetricsCollector = None
):
    """
    Décorateur de retry avec backoff exponentiel.
    
    Args:
        max_attempts: Nombre maximum de tentatives (incluant l'initiale)
        base_delay: Délai de base en secondes
        max_delay: Délai maximum (plafond)
        exponential_base: Base de l'exponentielle
        jitter: Variation aléatoire (±jitter%)
        retryable_exceptions: Tuple d'exceptions à retrier
        callback: Callback pour les événements de retry
        model_name: Nom du modèle (pour les métriques)
        metrics_collector: Collecteur de métriques
        
    Example:
        @retry(max_attempts=3, base_delay=2.0)
        async def fetch_data():
            ...
    """
    if retryable_exceptions is None:
        retryable_exceptions = (TimeoutError, asyncio.TimeoutError, ConnectionError)
    
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            collector = metrics_collector or get_retry_metrics()
            model = model_name or kwargs.get('model', func.__name__)
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                collector.record_attempt(model)
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Succès
                    if callback and attempt > 1:
                        await callback.on_success(model, attempt)
                    
                    if attempt > 1:
                        collector.record_success_after_retry(model)
                    
                    return result
                    
                except retryable_exceptions as e:
                    last_exception = e
                    reason = classify_error(e)
                    
                    if attempt == max_attempts:
                        # Dernière tentative, échec final
                        logger.error(
                            f"[FAIL] {model} exhausted {max_attempts} attempts ({reason})"
                        )
                        collector.record_failure(model)
                        
                        if callback:
                            await callback.on_failure(model, attempt, reason)
                        
                        raise
                    
                    # Calculer le délai
                    delay = calculate_delay(
                        attempt, base_delay, max_delay, exponential_base, jitter
                    )
                    
                    # Logger et notifier
                    logger.warning(
                        f"[RETRY] {model} attempt {attempt}/{max_attempts} "
                        f"after {delay:.1f}s ({reason})"
                    )
                    collector.record_retry(model, reason, delay)
                    
                    if callback:
                        await callback.on_retry(model, attempt, max_attempts, delay, reason)
                    
                    # Attendre avant le retry
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    # Exception non-retryable, échec immédiat
                    logger.error(f"[FAIL] {model} non-retryable error: {e}")
                    collector.record_failure(model)
                    raise
            
            # Ne devrait jamais arriver
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Version synchrone du retry."""
            collector = metrics_collector or get_retry_metrics()
            model = model_name or kwargs.get('model', func.__name__)
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                collector.record_attempt(model)
                
                try:
                    result = func(*args, **kwargs)
                    
                    if attempt > 1:
                        collector.record_success_after_retry(model)
                    
                    return result
                    
                except retryable_exceptions as e:
                    last_exception = e
                    reason = classify_error(e)
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"[FAIL] {model} exhausted {max_attempts} attempts ({reason})"
                        )
                        collector.record_failure(model)
                        raise
                    
                    delay = calculate_delay(
                        attempt, base_delay, max_delay, exponential_base, jitter
                    )
                    
                    logger.warning(
                        f"[RETRY] {model} attempt {attempt}/{max_attempts} "
                        f"after {delay:.1f}s ({reason})"
                    )
                    collector.record_retry(model, reason, delay)
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"[FAIL] {model} non-retryable error: {e}")
                    collector.record_failure(model)
                    raise
            
            raise last_exception
        
        # Retourner le wrapper approprié selon si la fonction est async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ══════════════════════════════════════════════════════════════════════════════
# WRAPPER POUR call_model_async (Story 4.2)
# ══════════════════════════════════════════════════════════════════════════════

def create_retry_wrapper(
    config: Dict[str, Any] = None,
    callback: Optional[RetryCallback] = None,
    metrics_collector: RetryMetricsCollector = None
):
    """
    Crée un wrapper de retry configuré pour call_model_async.
    
    Args:
        config: Configuration du retry (section 'retry' du YAML)
        callback: Callback pour les événements
        metrics_collector: Collecteur de métriques
        
    Returns:
        Décorateur configuré
    """
    cfg = {**DEFAULT_RETRY_CONFIG, **(config or {})}
    
    if not cfg.get("enabled", True):
        # Retry désactivé, retourner un décorateur no-op
        def no_retry(func):
            return func
        return no_retry
    
    return retry(
        max_attempts=cfg.get("max_attempts", 3),
        base_delay=cfg.get("base_delay", 2.0),
        max_delay=cfg.get("max_delay", 30.0),
        exponential_base=cfg.get("exponential_base", 2.0),
        jitter=cfg.get("jitter", 0.1),
        retryable_exceptions=(
            TimeoutError,
            asyncio.TimeoutError,
            ConnectionError,
            ConnectionRefusedError,
            RetryableError
        ),
        callback=callback,
        metrics_collector=metrics_collector
    )


async def call_with_retry(
    func: Callable,
    *args,
    retry_config: Dict[str, Any] = None,
    callback: Optional[RetryCallback] = None,
    metrics_collector: RetryMetricsCollector = None,
    **kwargs
):
    """
    Appelle une fonction avec retry.
    
    Alternative au décorateur pour les cas où on ne peut pas décorer.
    
    Args:
        func: Fonction à appeler
        *args: Arguments positionnels
        retry_config: Configuration du retry
        callback: Callback pour les événements
        metrics_collector: Collecteur de métriques
        **kwargs: Arguments nommés
        
    Returns:
        Résultat de la fonction
    """
    wrapper = create_retry_wrapper(retry_config, callback, metrics_collector)
    wrapped_func = wrapper(func)
    return await wrapped_func(*args, **kwargs)
