"""
Module de configuration pour Synthèse Council.
PRD-003: Chargement dynamique de la configuration YAML.

Cascade de priorité (du plus faible au plus fort):
1. DEFAULT_CONFIG (code)
2. ~/.synthese-council/config.yaml (global utilisateur)
3. ./synthese.config.yaml (local projet)
4. Arguments CLI (override final)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
import copy

# Import conditionnel de PyYAML
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION PAR DÉFAUT
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    "max_rounds": 2,
    "timeout": 300,
    "enable_trail": True,
    "trail_dir": "synthese_trails",
    "models": ["claude", "gemini", "codex"],
    "convergence_threshold": 0.8,
    "fallback_to_available": True,
    
    # Rôles experts (personnalisables)
    "expert_roles": {
        "extracteur": {
            "name": "L'Extracteur de Substance",
            "focus": "faits, données, thèse centrale"
        },
        "critique": {
            "name": "Le Gardien de la Fidélité",
            "focus": "glissements, biais, omissions"
        },
        "architecte": {
            "name": "L'Architecte du Sens",
            "focus": "structure, logique, cohérence"
        }
    },
    
    # Cadrage par défaut
    "default_cadrage": {
        "destinataire": "public général",
        "finalite": "information",
        "longueur": "10-15 lignes",
        "ton": "accessible",
        "niveau": "intermédiaire"
    },
    
    # Configuration retry (PRD-004)
    "retry": {
        "enabled": True,
        "max_attempts": 3,
        "base_delay": 2.0,
        "max_delay": 30.0,
        "exponential_base": 2.0,
        "jitter": 0.1
    },

    # Configuration sécurité (PRD-008)
    "security": {
        "max_prompt_length": 100000,
        "max_input_size_mb": 10,
        "sanitize_inputs": True
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# SCHÉMA DE VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

CONFIG_SCHEMA = {
    "max_rounds": {
        "type": int,
        "min": 1,
        "max": 5,
        "description": "Nombre de rounds de délibération"
    },
    "timeout": {
        "type": int,
        "min": 30,
        "max": 600,
        "description": "Timeout par modèle en secondes"
    },
    "enable_trail": {
        "type": bool,
        "description": "Activer la sauvegarde des trails"
    },
    "trail_dir": {
        "type": str,
        "description": "Répertoire pour les trails"
    },
    "models": {
        "type": list,
        "item_type": str,
        "allowed_values": ["claude", "gemini", "codex"],
        "description": "Liste des modèles à utiliser"
    },
    "convergence_threshold": {
        "type": float,
        "min": 0.0,
        "max": 1.0,
        "description": "Seuil de convergence pour consensus"
    },
    "fallback_to_available": {
        "type": bool,
        "description": "Continuer avec les modèles disponibles"
    },
    "expert_roles": {
        "type": dict,
        "description": "Configuration des rôles experts"
    },
    "default_cadrage": {
        "type": dict,
        "description": "Cadrage par défaut"
    },
    "retry": {
        "type": dict,
        "description": "Configuration du retry avec backoff exponentiel"
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# EXCEPTIONS
# ══════════════════════════════════════════════════════════════════════════════

class ConfigError(Exception):
    """Erreur de configuration."""
    
    def __init__(self, message: str, errors: List[str] = None):
        self.message = message
        self.errors = errors or []
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        if self.errors:
            return f"{self.message}\n" + "\n".join(f"  - {e}" for e in self.errors)
        return self.message


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG LOADER
# ══════════════════════════════════════════════════════════════════════════════

class ConfigLoader:
    """
    Charge et valide la configuration depuis plusieurs sources.
    
    Cascade de priorité:
    1. DEFAULT_CONFIG (code) - base
    2. ~/.synthese-council/config.yaml - global utilisateur
    3. ./synthese.config.yaml - local projet
    4. Chemin personnalisé (si fourni)
    5. Arguments CLI - override final
    """
    
    # Chemins standard
    GLOBAL_PATH = Path.home() / ".synthese-council" / "config.yaml"
    LOCAL_FILENAME = "synthese.config.yaml"
    
    def __init__(self):
        self._sources: List[Tuple[str, Dict]] = []
    
    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """Retourne une copie des valeurs par défaut."""
        return copy.deepcopy(DEFAULT_CONFIG)
    
    @classmethod
    def load(cls, 
             path: Optional[Union[str, Path]] = None,
             cli_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Charge la configuration avec cascade.
        
        Args:
            path: Chemin personnalisé vers un fichier config (optionnel)
            cli_overrides: Overrides depuis les arguments CLI
            
        Returns:
            Configuration fusionnée et validée
        """
        loader = cls()
        config = cls.get_defaults()
        loader._sources.append(("default", config.copy()))
        
        # Charger config globale
        if cls.GLOBAL_PATH.exists():
            global_config = cls._load_yaml(cls.GLOBAL_PATH)
            if global_config:
                config = cls._merge(config, global_config)
                loader._sources.append(("global", global_config))
        
        # Charger config locale
        local_path = Path.cwd() / cls.LOCAL_FILENAME
        if local_path.exists():
            local_config = cls._load_yaml(local_path)
            if local_config:
                config = cls._merge(config, local_config)
                loader._sources.append(("local", local_config))
        
        # Charger config personnalisée
        if path:
            custom_path = Path(path)
            if custom_path.exists():
                custom_config = cls._load_yaml(custom_path)
                if custom_config:
                    config = cls._merge(config, custom_config)
                    loader._sources.append(("custom", custom_config))
            else:
                raise ConfigError(f"Fichier de configuration non trouvé: {path}")
        
        # Appliquer les overrides CLI
        if cli_overrides:
            # Filtrer les None
            cli_config = {k: v for k, v in cli_overrides.items() if v is not None}
            if cli_config:
                config = cls._merge(config, cli_config)
                loader._sources.append(("cli", cli_config))
        
        # Valider
        cls.validate(config)
        
        # Stocker les sources pour debug
        config["_sources"] = [s[0] for s in loader._sources]
        
        return config
    
    @classmethod
    def _load_yaml(cls, path: Path) -> Optional[Dict[str, Any]]:
        """Charge un fichier YAML."""
        if not YAML_AVAILABLE:
            print(f"Warning: PyYAML non installé, fichier ignoré: {path}")
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else None
        except yaml.YAMLError as e:
            raise ConfigError(f"Erreur de syntaxe YAML dans {path}", [str(e)])
        except Exception as e:
            raise ConfigError(f"Erreur de lecture de {path}", [str(e)])
    
    @classmethod
    def _merge(cls, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fusionne deux configurations (récursivement pour les dicts).
        
        L'override écrase les valeurs de base, sauf pour les dicts
        qui sont fusionnés récursivement.
        """
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Fusion récursive pour les dicts
                result[key] = cls._merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        
        return result
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> bool:
        """
        Valide la configuration contre le schéma.
        
        Raises:
            ConfigError: Si la configuration est invalide
        """
        errors = []
        
        for key, schema in CONFIG_SCHEMA.items():
            if key not in config:
                continue
            
            value = config[key]
            expected_type = schema["type"]
            
            # Vérification de type
            if not isinstance(value, expected_type):
                errors.append(
                    f"{key}: attendu {expected_type.__name__}, "
                    f"reçu {type(value).__name__}"
                )
                continue
            
            # Vérification de plage (pour int/float)
            if "min" in schema and value < schema["min"]:
                errors.append(
                    f"{key}: valeur minimum {schema['min']}, reçu {value}"
                )
            
            if "max" in schema and value > schema["max"]:
                errors.append(
                    f"{key}: valeur maximum {schema['max']}, reçu {value}"
                )
            
            # Vérification des éléments de liste
            if expected_type == list and "allowed_values" in schema:
                invalid_items = [v for v in value if v not in schema["allowed_values"]]
                if invalid_items:
                    errors.append(
                        f"{key}: valeurs non autorisées {invalid_items}, "
                        f"autorisé: {schema['allowed_values']}"
                    )
        
        if errors:
            raise ConfigError("Configuration invalide", errors)
        
        return True
    
    @classmethod
    def get_config_paths(cls) -> Dict[str, Tuple[Path, bool]]:
        """
        Retourne les chemins de configuration et leur existence.
        
        Returns:
            Dict avec {nom: (chemin, existe)}
        """
        local_path = Path.cwd() / cls.LOCAL_FILENAME
        
        return {
            "global": (cls.GLOBAL_PATH, cls.GLOBAL_PATH.exists()),
            "local": (local_path, local_path.exists())
        }
    
    @classmethod
    def show_config(cls, config: Dict[str, Any]) -> str:
        """
        Formate la configuration pour affichage.
        
        Args:
            config: Configuration à afficher
            
        Returns:
            Configuration formatée en YAML
        """
        if not YAML_AVAILABLE:
            import json
            return json.dumps(config, indent=2, ensure_ascii=False)
        
        # Exclure les métadonnées internes
        display_config = {k: v for k, v in config.items() if not k.startswith("_")}
        
        return yaml.dump(display_config, default_flow_style=False, allow_unicode=True)
    
    @classmethod
    def generate_template(cls, include_comments: bool = True) -> str:
        """
        Génère un fichier de configuration template.
        
        Args:
            include_comments: Inclure les commentaires explicatifs
            
        Returns:
            Contenu du fichier template
        """
        lines = []
        
        if include_comments:
            lines.append("# Configuration Synthèse Council")
            lines.append("# Voir documentation: https://github.com/...")
            lines.append("")
        
        template_content = {
            "max_rounds": {
                "value": DEFAULT_CONFIG["max_rounds"],
                "comment": "Nombre de rounds de délibération (1-5)"
            },
            "timeout": {
                "value": DEFAULT_CONFIG["timeout"],
                "comment": "Timeout par modèle en secondes (30-600)"
            },
            "enable_trail": {
                "value": DEFAULT_CONFIG["enable_trail"],
                "comment": "Sauvegarder les trails d'audit"
            },
            "trail_dir": {
                "value": DEFAULT_CONFIG["trail_dir"],
                "comment": "Répertoire pour les trails"
            },
            "models": {
                "value": DEFAULT_CONFIG["models"],
                "comment": "Modèles à utiliser (ordre de préférence)"
            },
            "convergence_threshold": {
                "value": DEFAULT_CONFIG["convergence_threshold"],
                "comment": "Seuil de convergence pour consensus (0.0-1.0)"
            },
            "fallback_to_available": {
                "value": DEFAULT_CONFIG["fallback_to_available"],
                "comment": "Continuer avec modèles disponibles si certains manquent"
            }
        }
        
        for key, data in template_content.items():
            if include_comments:
                lines.append(f"# {data['comment']}")
            
            value = data["value"]
            if isinstance(value, bool):
                lines.append(f"{key}: {str(value).lower()}")
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
            
            if include_comments:
                lines.append("")
        
        # Ajouter les sections complexes
        if include_comments:
            lines.append("# Rôles des experts (personnalisable)")
        
        lines.append("expert_roles:")
        for role, data in DEFAULT_CONFIG["expert_roles"].items():
            lines.append(f"  {role}:")
            lines.append(f"    name: \"{data['name']}\"")
            lines.append(f"    focus: \"{data['focus']}\"")
        
        if include_comments:
            lines.append("")
            lines.append("# Cadrage par défaut")
        
        lines.append("default_cadrage:")
        for key, value in DEFAULT_CONFIG["default_cadrage"].items():
            lines.append(f"  {key}: \"{value}\"")
        
        return "\n".join(lines)
    
    @classmethod
    def init_config(cls, path: Optional[Path] = None, force: bool = False) -> Path:
        """
        Crée un fichier de configuration template.
        
        Args:
            path: Chemin de destination (défaut: ./synthese.config.yaml)
            force: Écraser si existe
            
        Returns:
            Chemin du fichier créé
            
        Raises:
            ConfigError: Si le fichier existe et force=False
        """
        dest_path = path or (Path.cwd() / cls.LOCAL_FILENAME)
        
        if dest_path.exists() and not force:
            raise ConfigError(
                f"Le fichier {dest_path} existe déjà. "
                "Utilisez --force pour écraser."
            )
        
        content = cls.generate_template(include_comments=True)
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(content, encoding="utf-8")
        
        return dest_path


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def get_expert_roles(config: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Récupère les rôles experts avec les prompts suffixes.
    
    Fusionne la config personnalisée avec les valeurs par défaut
    pour garantir que tous les champs sont présents.
    """
    default_roles = {
        "extracteur": {
            "name": "L'Extracteur de Substance",
            "focus": "faits, données, thèse centrale",
            "prompt_suffix": "Concentre-toi sur les FAITS et la THÈSE centrale. Identifie les données concrètes, les affirmations vérifiables, et le message principal. Ignore les ornements rhétoriques."
        },
        "critique": {
            "name": "Le Gardien de la Fidélité",
            "focus": "glissements, biais, omissions",
            "prompt_suffix": "Traque les GLISSEMENTS de sens. Vérifie que rien n'est ajouté ni omis. Distingue ce que le texte DIT de ce qu'il SUGGÈRE. Signale tout risque de surinterprétation."
        },
        "architecte": {
            "name": "L'Architecte du Sens",
            "focus": "structure, logique, cohérence",
            "prompt_suffix": "Analyse la STRUCTURE argumentative. Identifie les présupposés, les enchaînements logiques, les tensions. Propose une architecture claire pour la synthèse finale."
        }
    }
    
    # Fusionner avec la config personnalisée
    custom_roles = config.get("expert_roles", {})
    
    result = copy.deepcopy(default_roles)
    for role, custom_data in custom_roles.items():
        if role in result:
            result[role].update(custom_data)
        else:
            # Nouveau rôle personnalisé
            result[role] = {
                "name": custom_data.get("name", role.capitalize()),
                "focus": custom_data.get("focus", ""),
                "prompt_suffix": custom_data.get("prompt_suffix", "")
            }
    
    return result


def get_default_cadrage(config: Dict[str, Any]) -> Dict[str, str]:
    """Récupère le cadrage par défaut depuis la config."""
    return config.get("default_cadrage", DEFAULT_CONFIG["default_cadrage"]).copy()
