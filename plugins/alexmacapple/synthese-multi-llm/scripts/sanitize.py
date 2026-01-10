"""
Module de sanitisation des entrées pour Synthèse Council.
PRD-008 Story 8.4: Validation et nettoyage des entrées utilisateur.

Ce module fournit des fonctions pour valider et nettoyer les entrées
avant de les envoyer aux LLMs.
"""

import re
import html
from typing import Dict, Any, Optional, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_LIMITS = {
    "max_prompt_length": 100000,      # ~25k tokens
    "max_source_text_length": 500000,  # ~125k tokens
    "max_cadrage_field_length": 1000,
    "min_prompt_length": 1,
}

# Caractères potentiellement dangereux pour les shells
SHELL_DANGEROUS_CHARS = [
    "`",      # Command substitution
    "$(",     # Command substitution
    "${",     # Variable expansion
    "$((",    # Arithmetic expansion
    ";&",     # Command separator
    "|&",     # Pipe
    ">>",     # Redirect append
    "<<",     # Here document
    "\x00",   # Null byte
]

# Patterns d'injection potentielle
INJECTION_PATTERNS = [
    r"\$\{.*\}",           # ${...} expansion
    r"\$\(.*\)",           # $(...) command substitution
    r"`[^`]+`",            # `...` command substitution
    r";\s*\w+",            # ; command
    r"\|\s*\w+",           # | pipe to command
    r">\s*/",              # Redirect to root
]


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

class ValidationError(ValueError):
    """Erreur de validation des entrées."""
    pass


def validate_prompt(
    prompt: str,
    max_length: int = None,
    min_length: int = None
) -> Tuple[bool, Optional[str]]:
    """
    Valide un prompt.
    
    Args:
        prompt: Texte du prompt
        max_length: Longueur maximale (défaut: 100000)
        min_length: Longueur minimale (défaut: 1)
        
    Returns:
        (valid: bool, error_message: str | None)
    """
    max_len = max_length or DEFAULT_LIMITS["max_prompt_length"]
    min_len = min_length or DEFAULT_LIMITS["min_prompt_length"]
    
    if not isinstance(prompt, str):
        return False, f"Le prompt doit être une chaîne (reçu: {type(prompt).__name__})"
    
    if len(prompt) < min_len:
        return False, f"Prompt trop court (min: {min_len} caractères)"
    
    if len(prompt) > max_len:
        return False, f"Prompt trop long ({len(prompt)} > {max_len} caractères)"
    
    return True, None


def validate_source_text(
    text: str,
    max_length: int = None
) -> Tuple[bool, Optional[str]]:
    """
    Valide un texte source.
    
    Args:
        text: Texte source à synthétiser
        max_length: Longueur maximale
        
    Returns:
        (valid: bool, error_message: str | None)
    """
    max_len = max_length or DEFAULT_LIMITS["max_source_text_length"]
    
    if not isinstance(text, str):
        return False, f"Le texte doit être une chaîne (reçu: {type(text).__name__})"
    
    if len(text) == 0:
        return False, "Le texte source est vide"
    
    if len(text) > max_len:
        return False, f"Texte trop long ({len(text)} > {max_len} caractères)"
    
    return True, None


def validate_cadrage(
    cadrage: Dict[str, str],
    required_fields: List[str] = None,
    max_field_length: int = None
) -> Tuple[bool, Optional[str]]:
    """
    Valide un dictionnaire de cadrage.
    
    Args:
        cadrage: Dictionnaire de cadrage
        required_fields: Champs obligatoires
        max_field_length: Longueur max par champ
        
    Returns:
        (valid: bool, error_message: str | None)
    """
    if not isinstance(cadrage, dict):
        return False, f"Le cadrage doit être un dictionnaire (reçu: {type(cadrage).__name__})"
    
    max_len = max_field_length or DEFAULT_LIMITS["max_cadrage_field_length"]
    required = required_fields or ["destinataire"]
    
    # Vérifier les champs requis
    for field in required:
        if field not in cadrage:
            return False, f"Champ requis manquant: {field}"
    
    # Vérifier la longueur des champs
    for key, value in cadrage.items():
        if not isinstance(key, str):
            return False, f"Les clés du cadrage doivent être des chaînes"
        
        if not isinstance(value, str):
            return False, f"Les valeurs du cadrage doivent être des chaînes (champ: {key})"
        
        if len(value) > max_len:
            return False, f"Champ '{key}' trop long ({len(value)} > {max_len})"
    
    return True, None


# ══════════════════════════════════════════════════════════════════════════════
# SANITISATION
# ══════════════════════════════════════════════════════════════════════════════

def sanitize_for_shell(text: str) -> str:
    """
    Nettoie un texte pour utilisation dans un shell.
    
    Échappe ou supprime les caractères dangereux.
    
    Args:
        text: Texte à nettoyer
        
    Returns:
        Texte nettoyé
    """
    result = text
    
    # Supprimer les null bytes
    result = result.replace("\x00", "")
    
    # Échapper les backticks
    result = result.replace("`", "\\`")
    
    # Échapper les $
    result = result.replace("$", "\\$")
    
    return result


def sanitize_for_json(text: str) -> str:
    """
    Nettoie un texte pour inclusion dans du JSON.
    
    Args:
        text: Texte à nettoyer
        
    Returns:
        Texte nettoyé
    """
    # Supprimer les null bytes
    result = text.replace("\x00", "")
    
    # Les caractères de contrôle (sauf newline, tab)
    result = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', result)
    
    return result


def sanitize_html(text: str) -> str:
    """
    Échappe les entités HTML.
    
    Args:
        text: Texte à nettoyer
        
    Returns:
        Texte avec HTML échappé
    """
    return html.escape(text)


def sanitize_prompt(
    prompt: str,
    for_shell: bool = True,
    for_json: bool = True,
    max_length: int = None
) -> str:
    """
    Sanitise un prompt pour utilisation sécurisée.
    
    Args:
        prompt: Prompt à nettoyer
        for_shell: Appliquer sanitisation shell
        for_json: Appliquer sanitisation JSON
        max_length: Tronquer si dépasse
        
    Returns:
        Prompt nettoyé
    """
    result = prompt
    
    # Appliquer les sanitisations
    if for_json:
        result = sanitize_for_json(result)
    
    if for_shell:
        result = sanitize_for_shell(result)
    
    # Tronquer si nécessaire
    max_len = max_length or DEFAULT_LIMITS["max_prompt_length"]
    if len(result) > max_len:
        result = result[:max_len - 3] + "..."
    
    return result


def sanitize_cadrage(cadrage: Dict[str, str]) -> Dict[str, str]:
    """
    Sanitise un dictionnaire de cadrage.
    
    Args:
        cadrage: Cadrage à nettoyer
        
    Returns:
        Cadrage nettoyé
    """
    max_len = DEFAULT_LIMITS["max_cadrage_field_length"]
    
    sanitized = {}
    for key, value in cadrage.items():
        # Nettoyer la clé
        clean_key = sanitize_for_json(str(key))
        
        # Nettoyer la valeur
        clean_value = sanitize_for_json(str(value))
        
        # Tronquer si nécessaire
        if len(clean_value) > max_len:
            clean_value = clean_value[:max_len - 3] + "..."
        
        sanitized[clean_key] = clean_value
    
    return sanitized


# ══════════════════════════════════════════════════════════════════════════════
# DÉTECTION D'INJECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_injection_patterns(text: str) -> List[str]:
    """
    Détecte les patterns d'injection potentielle.
    
    Args:
        text: Texte à analyser
        
    Returns:
        Liste des patterns détectés
    """
    detected = []
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            detected.append(pattern)
    
    for char_seq in SHELL_DANGEROUS_CHARS:
        if char_seq in text:
            detected.append(f"char:{char_seq}")
    
    return detected


def is_safe(text: str) -> Tuple[bool, List[str]]:
    """
    Vérifie si un texte est sûr.
    
    Args:
        text: Texte à vérifier
        
    Returns:
        (safe: bool, detected_patterns: list)
    """
    patterns = detect_injection_patterns(text)
    return len(patterns) == 0, patterns


# ══════════════════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

def validate_and_sanitize(
    source_text: str,
    cadrage: Dict[str, str],
    prompt: str = None,
    strict: bool = False
) -> Tuple[str, Dict[str, str], Optional[str], List[str]]:
    """
    Valide et sanitise toutes les entrées.
    
    Args:
        source_text: Texte source
        cadrage: Dictionnaire de cadrage
        prompt: Prompt optionnel
        strict: Lever une exception si invalide
        
    Returns:
        (clean_text, clean_cadrage, clean_prompt, warnings)
        
    Raises:
        ValidationError: Si strict=True et entrée invalide
    """
    warnings = []
    
    # Valider le texte source
    valid, error = validate_source_text(source_text)
    if not valid:
        if strict:
            raise ValidationError(error)
        warnings.append(f"Texte source: {error}")
    
    # Valider le cadrage
    valid, error = validate_cadrage(cadrage)
    if not valid:
        if strict:
            raise ValidationError(error)
        warnings.append(f"Cadrage: {error}")
    
    # Valider le prompt si fourni
    if prompt:
        valid, error = validate_prompt(prompt)
        if not valid:
            if strict:
                raise ValidationError(error)
            warnings.append(f"Prompt: {error}")
    
    # Détecter les patterns dangereux
    safe, patterns = is_safe(source_text)
    if not safe:
        warnings.append(f"Patterns détectés dans le texte: {patterns}")
    
    # Sanitiser
    clean_text = sanitize_for_json(source_text)
    clean_cadrage = sanitize_cadrage(cadrage)
    clean_prompt = sanitize_prompt(prompt) if prompt else None
    
    return clean_text, clean_cadrage, clean_prompt, warnings
