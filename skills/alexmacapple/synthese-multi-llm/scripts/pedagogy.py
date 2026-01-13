"""
Module pédagogique pour Synthèse Council.
PRD-005: Mode pédagogique qui explique chaque étape du processus.

Le mode pédagogique transforme l'exécution en session d'apprentissage
en commentant chaque étape de la méthodologie sémiotique hybride.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPES PÉDAGOGIQUES
# ══════════════════════════════════════════════════════════════════════════════

class PedagogicStep(Enum):
    """Étapes du processus avec contenu pédagogique."""
    INTRO = "intro"
    CADRAGE = "cadrage"
    EXPERT_INTRO = "expert_intro"
    EXTRACTION = "extraction"
    LAYERS = "layers"
    CRITIQUE = "critique"
    GLISSEMENTS = "glissements"
    CONVERGENCE = "convergence"
    SYNTHESE = "synthese"
    SUMMARY = "summary"


# ══════════════════════════════════════════════════════════════════════════════
# CONTENU PÉDAGOGIQUE
# ══════════════════════════════════════════════════════════════════════════════

PEDAGOGIC_CONTENT = {
    PedagogicStep.INTRO: """
╔══════════════════════════════════════════════════════════════╗
║                   MODE PÉDAGOGIQUE                           ║
╠══════════════════════════════════════════════════════════════╣
║  Ce mode explique chaque étape du processus de synthèse.     ║
║                                                              ║
║  MÉTHODOLOGIE : Fabrique Sémiotique Hybride                  ║
║  PRINCIPE : Le sens ne s'extrait pas, il se co-fabrique.     ║
║                                                              ║
║  Vous allez observer :                                       ║
║  1. Le CADRAGE de l'usage (pour qui ? pourquoi ?)           ║
║  2. L'EXTRACTION par 3 experts IA spécialisés               ║
║  3. La CRITIQUE croisée (validation mutuelle)                ║
║  4. La SYNTHÈSE finale (convergence des perspectives)        ║
║                                                              ║
║  Chaque étape sera commentée avant son exécution.            ║
╚══════════════════════════════════════════════════════════════╝
""",

    PedagogicStep.CADRAGE: """
┌─────────────────────────────────────────────────────────────┐
│  📚 ÉTAPE 1 : CADRAGE DE L'USAGE                           │
├─────────────────────────────────────────────────────────────┤
│  Pourquoi cette étape ?                                     │
│                                                             │
│  Une synthèse sans contexte est un résumé "hors sol".       │
│  Le même texte donne des synthèses différentes selon :      │
│                                                             │
│  • QUI la lit (expert technique vs grand public)           │
│  • POURQUOI (prendre une décision vs s'informer)           │
│  • COMMENT (10 lignes vs 2 pages, ton formel vs accessible)│
│                                                             │
│  Ces 5 questions fixent le "jeu de langage" :               │
│  1. Destinataire - À qui s'adresse cette synthèse ?         │
│  2. Finalité - Quel usage sera fait de cette synthèse ?     │
│  3. Longueur - Quelle taille est appropriée ?               │
│  4. Ton - Quel registre adopter ?                           │
│  5. Niveau - Quel degré de technicité ?                     │
│                                                             │
│  💡 Conseil : Plus le cadrage est précis, plus la synthèse │
│     sera pertinente pour votre besoin spécifique.           │
└─────────────────────────────────────────────────────────────┘
""",

    PedagogicStep.EXTRACTION: """
┌─────────────────────────────────────────────────────────────┐
│  🔬 ÉTAPE 2 : EXTRACTION MULTI-PERSPECTIVES                │
├─────────────────────────────────────────────────────────────┤
│  Pourquoi 3 experts et pas un seul ?                        │
│                                                             │
│  Chaque IA a ses biais et angles morts. En croisant         │
│  3 perspectives spécialisées, on obtient une vision         │
│  plus complète et plus fiable.                              │
│                                                             │
│  Les 3 experts ont des FOCUS différents :                   │
│  • L'Extracteur → les FAITS (que dit le texte ?)           │
│  • Le Gardien → les RISQUES (que pourrait-on déformer ?)   │
│  • L'Architecte → la STRUCTURE (comment c'est construit ?) │
│                                                             │
│  Cette division suit les 4 couches sémiotiques :            │
│  📊 Trace → 🏷️ Signe → 🔗 Schème → ⚖️ Institution           │
└─────────────────────────────────────────────────────────────┘
""",

    PedagogicStep.LAYERS: """
┌─────────────────────────────────────────────────────────────┐
│  📊 LES 4 COUCHES SÉMIOTIQUES                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. TRACE (📊) - Le niveau factuel                         │
│     "Que dit concrètement le texte ?"                       │
│     → Données, chiffres, événements, citations              │
│                                                             │
│  2. SIGNE (🏷️) - Le niveau lexical                         │
│     "Quels mots-clés orientent le sens ?"                   │
│     → Termes pivots, expressions significatives             │
│                                                             │
│  3. SCHÈME (🔗) - Le niveau logique                        │
│     "Quel raisonnement sous-tend le texte ?"                │
│     → Arguments, enchaînements, présupposés                 │
│                                                             │
│  4. INSTITUTION (⚖️) - Le niveau normatif                  │
│     "Quels effets le texte cherche-t-il à produire ?"       │
│     → Intentions, implications, cadre d'action              │
│                                                             │
│  💡 Ces 4 couches permettent d'analyser un texte sans       │
│     le réduire ni le surinterprêter.                        │
└─────────────────────────────────────────────────────────────┘
""",

    PedagogicStep.CRITIQUE: """
┌─────────────────────────────────────────────────────────────┐
│  🔄 ÉTAPE 3 : CRITIQUE CROISÉE                             │
├─────────────────────────────────────────────────────────────┤
│  Pourquoi cette étape ?                                     │
│                                                             │
│  Un seul point de vue peut manquer des nuances ou           │
│  introduire des biais involontaires.                        │
│                                                             │
│  La critique croisée permet de :                            │
│  ✓ Détecter les DIVERGENCES entre experts                  │
│  ✓ Identifier les GLISSEMENTS de sens potentiels           │
│  ✓ Renforcer les points de CONVERGENCE                     │
│                                                             │
│  Chaque expert évalue les analyses des autres :             │
│  • L'Extracteur vérifie les faits cités par les autres     │
│  • Le Gardien traque les déformations potentielles         │
│  • L'Architecte valide la cohérence logique                │
│                                                             │
│  💡 Plus les experts convergent, plus la synthèse           │
│     sera robuste et fidèle au texte source.                 │
└─────────────────────────────────────────────────────────────┘
""",

    PedagogicStep.GLISSEMENTS: """
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ CONTRÔLE DES GLISSEMENTS                               │
├─────────────────────────────────────────────────────────────┤
│  Un glissement = une dérive de sens entre le texte          │
│  source et la synthèse.                                     │
│                                                             │
│  Types courants à surveiller :                              │
│                                                             │
│  • AMALGAME                                                 │
│    Confondre des termes proches mais distincts              │
│    Ex: "simplification" ≠ "suppression"                     │
│                                                             │
│  • RÉDUCTION                                                │
│    Ignorer une partie du message                            │
│    Ex: omettre les nuances ou réserves                      │
│                                                             │
│  • SURINTERPRÉTATION                                        │
│    Ajouter ce qui n'est pas dit                             │
│    Ex: "suggère" devient "affirme"                          │
│                                                             │
│  • OMISSION SÉLECTIVE                                       │
│    Effacer stratégiquement certains éléments                │
│    Ex: ignorer les contre-arguments                         │
│                                                             │
│  💡 Le Gardien de la Fidélité est spécialisé dans           │
│     la détection de ces glissements.                        │
└─────────────────────────────────────────────────────────────┘
""",

    PedagogicStep.CONVERGENCE: """
┌─────────────────────────────────────────────────────────────┐
│  📈 MESURE DE CONVERGENCE                                  │
├─────────────────────────────────────────────────────────────┤
│  Comment savoir si les experts sont d'accord ?              │
│                                                             │
│  Le score de convergence (0.0 à 1.0) mesure :               │
│  • La similitude des analyses produites                     │
│  • L'accord sur les points clés identifiés                  │
│  • La cohérence des structures proposées                    │
│                                                             │
│  Interprétation :                                           │
│  • 0.8 - 1.0 : Forte convergence (consensus solide)        │
│  • 0.6 - 0.8 : Convergence moyenne (quelques nuances)      │
│  • < 0.6 : Faible convergence (divergences importantes)    │
│                                                             │
│  💡 Une faible convergence n'est pas forcément mauvaise :   │
│     elle peut révéler une complexité du texte source.       │
└─────────────────────────────────────────────────────────────┘
""",

    PedagogicStep.SYNTHESE: """
┌─────────────────────────────────────────────────────────────┐
│  ✨ ÉTAPE 4 : SYNTHÈSE FINALE                              │
├─────────────────────────────────────────────────────────────┤
│  Comment la synthèse est-elle produite ?                    │
│                                                             │
│  L'Architecte du Sens rassemble :                           │
│  • Les FAITS validés par l'Extracteur                      │
│  • Les RISQUES identifiés par le Gardien                   │
│  • La STRUCTURE logique qu'il a lui-même analysée          │
│                                                             │
│  Il produit une synthèse qui :                              │
│  ✓ Respecte le CADRAGE défini au départ                    │
│  ✓ Préserve les NUANCES du texte source                    │
│  ✓ Évite les GLISSEMENTS détectés                          │
│  ✓ Intègre les CONVERGENCES des 3 experts                  │
│                                                             │
│  💡 La synthèse n'est pas un résumé : elle est une          │
│     reconstruction du sens adaptée à votre usage.           │
└─────────────────────────────────────────────────────────────┘
""",

    PedagogicStep.SUMMARY: """
╔══════════════════════════════════════════════════════════════╗
║                   CE QUE VOUS AVEZ APPRIS                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. CADRER avant de synthétiser                             ║
║     → Une synthèse sans contexte est un résumé hors sol     ║
║                                                              ║
║  2. STRATIFIER le sens en 4 couches                         ║
║     → Trace → Signe → Schème → Institution                  ║
║     → Du concret à l'abstrait, du fait à l'effet            ║
║                                                              ║
║  3. CROISER les perspectives                                 ║
║     → 3 experts valent mieux qu'un seul point de vue        ║
║     → La triangulation renforce la fiabilité                ║
║                                                              ║
║  4. CONTRÔLER les glissements                               ║
║     → Amalgame, réduction, surinterprétation, omission      ║
║     → La fidélité au texte source est prioritaire           ║
║                                                              ║
║  5. MESURER la convergence                                  ║
║     → Un score élevé = consensus solide                     ║
║     → Un score faible = complexité à explorer               ║
║                                                              ║
║  📚 Pour approfondir : références/couches-semiotiques.md    ║
║                        références/glissements.md            ║
╚══════════════════════════════════════════════════════════════╝
"""
}

# ══════════════════════════════════════════════════════════════════════════════
# EXPLICATIONS DES EXPERTS
# ══════════════════════════════════════════════════════════════════════════════

EXPERT_EXPLANATIONS = {
    "extracteur": """
┌─────────────────────────────────────────────────────────────┐
│  🔍 L'EXTRACTEUR DE SUBSTANCE ({model})                    │
├─────────────────────────────────────────────────────────────┤
│  Rôle : Identifier les faits bruts et la thèse centrale     │
│                                                             │
│  Ce qu'il cherche :                                         │
│  • Les TRACES : données, chiffres, événements concrets      │
│  • La THÈSE : l'affirmation principale du texte             │
│  • Les MOTS-CADRES : termes qui orientent le sens           │
│                                                             │
│  Question guide : "Que dit concrètement ce texte ?"         │
│                                                             │
│  ⏳ Analyse en cours...                                     │
└─────────────────────────────────────────────────────────────┘
""",
    "critique": """
┌─────────────────────────────────────────────────────────────┐
│  🛡️ LE GARDIEN DE LA FIDÉLITÉ ({model})                    │
├─────────────────────────────────────────────────────────────┤
│  Rôle : Traquer les glissements et vérifier la fidélité     │
│                                                             │
│  Ce qu'il vérifie :                                         │
│  • Les AMALGAMES : termes confondus à tort                  │
│  • Les OMISSIONS : nuances ou réserves effacées             │
│  • Les SURINTERPRÉTATIONS : sens ajouté non présent         │
│                                                             │
│  Question guide : "Est-ce fidèle au texte source ?"         │
│                                                             │
│  ⏳ Vérification en cours...                                │
└─────────────────────────────────────────────────────────────┘
""",
    "architecte": """
┌─────────────────────────────────────────────────────────────┐
│  🏗️ L'ARCHITECTE DU SENS ({model})                         │
├─────────────────────────────────────────────────────────────┤
│  Rôle : Analyser la structure et la logique argumentative   │
│                                                             │
│  Ce qu'il examine :                                         │
│  • Le SCHÈME : raisonnement sous-jacent                     │
│  • Les PRÉSUPPOSÉS : ce qui est tenu pour acquis            │
│  • L'INSTITUTION : effets normatifs visés                   │
│                                                             │
│  Question guide : "Comment le texte construit-il son sens ?"│
│                                                             │
│  ⏳ Structuration en cours...                               │
└─────────────────────────────────────────────────────────────┘
"""
}

# ══════════════════════════════════════════════════════════════════════════════
# EXPLICATIONS DES COUCHES
# ══════════════════════════════════════════════════════════════════════════════

LAYER_EXPLANATIONS = {
    "trace": {
        "icon": "📊",
        "name": "TRACE",
        "description": "Le niveau factuel - les données brutes du texte",
        "question": "Que dit concrètement le texte ?",
        "examples": "chiffres, dates, noms, événements, citations"
    },
    "signe": {
        "icon": "🏷️",
        "name": "SIGNE",
        "description": "Le niveau lexical - les mots-clés significatifs",
        "question": "Quels mots orientent le sens ?",
        "examples": "termes pivots, métaphores, qualificatifs"
    },
    "scheme": {
        "icon": "🔗",
        "name": "SCHÈME",
        "description": "Le niveau logique - la structure argumentative",
        "question": "Quel raisonnement sous-tend le texte ?",
        "examples": "causes, conséquences, oppositions, analogies"
    },
    "institution": {
        "icon": "⚖️",
        "name": "INSTITUTION",
        "description": "Le niveau normatif - les effets visés",
        "question": "Quels effets le texte cherche-t-il à produire ?",
        "examples": "prescriptions, valeurs, cadre d'action"
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# PRESENTER PÉDAGOGIQUE
# ══════════════════════════════════════════════════════════════════════════════

class PedagogicPresenter:
    """
    Gère l'affichage pédagogique pendant l'exécution.
    
    Affiche des explications contextuelles à chaque étape
    du processus de synthèse pour permettre à l'utilisateur
    d'apprendre la méthodologie sémiotique.
    """
    
    def __init__(self, enabled: bool = False, interactive: bool = False):
        """
        Initialise le presenter.
        
        Args:
            enabled: Active le mode pédagogique
            interactive: Pause après chaque explication (attendre Entrée)
        """
        self.enabled = enabled
        self.interactive = interactive
        self._step_count = 0
    
    def explain(self, step: PedagogicStep, context: Optional[Dict[str, Any]] = None):
        """
        Affiche l'explication d'une étape.
        
        Args:
            step: Étape à expliquer
            context: Variables de contexte pour le formatage
        """
        if not self.enabled:
            return
        
        content = PEDAGOGIC_CONTENT.get(step, "")
        if not content:
            return
        
        # Formater avec le contexte si fourni
        if context:
            try:
                content = content.format(**context)
            except KeyError:
                pass  # Ignorer les clés manquantes
        
        print(content)
        self._step_count += 1
        
        if self.interactive:
            input("  [Appuyez sur Entrée pour continuer...]")
    
    def explain_expert(self, role: str, model: str):
        """
        Affiche l'explication d'un expert avant son intervention.
        
        Args:
            role: Rôle de l'expert (extracteur, critique, architecte)
            model: Nom du modèle assigné
        """
        if not self.enabled:
            return
        
        content = EXPERT_EXPLANATIONS.get(role, "")
        if content:
            print(content.format(model=model))
            
            if self.interactive:
                input("  [Appuyez sur Entrée pour lancer l'analyse...]")
    
    def explain_layer(self, layer: str, examples: Optional[List[str]] = None):
        """
        Affiche l'explication d'une couche sémiotique.
        
        Args:
            layer: Nom de la couche (trace, signe, scheme, institution)
            examples: Exemples concrets tirés du texte analysé
        """
        if not self.enabled:
            return
        
        layer_info = LAYER_EXPLANATIONS.get(layer.lower())
        if not layer_info:
            return
        
        print(f"\n  {layer_info['icon']} {layer_info['name']}")
        print(f"     {layer_info['description']}")
        print(f"     Question : {layer_info['question']}")
        
        if examples:
            print(f"     Exemples trouvés : {', '.join(examples[:3])}")
    
    def explain_glissement(self, glissement_type: str, detected: Optional[List[str]] = None):
        """
        Affiche l'explication d'un type de glissement.
        
        Args:
            glissement_type: Type de glissement (amalgame, reduction, etc.)
            detected: Instances détectées dans l'analyse
        """
        if not self.enabled:
            return
        
        types_info = {
            "amalgame": {
                "icon": "🔀",
                "description": "Confusion entre termes proches mais distincts"
            },
            "reduction": {
                "icon": "✂️",
                "description": "Partie du message ignorée ou simplifiée"
            },
            "surinterprétation": {
                "icon": "➕",
                "description": "Sens ajouté qui n'était pas dans le texte"
            },
            "omission": {
                "icon": "🚫",
                "description": "Nuances ou réserves effacées"
            }
        }
        
        info = types_info.get(glissement_type.lower())
        if info:
            print(f"\n  {info['icon']} {glissement_type.upper()}")
            print(f"     {info['description']}")
            
            if detected:
                print(f"     ⚠️ Détecté : {detected[0]}")
    
    def show_convergence(self, score: float):
        """
        Affiche et explique le score de convergence.
        
        Args:
            score: Score de convergence (0.0 à 1.0)
        """
        if not self.enabled:
            return
        
        # Interprétation du score
        if score >= 0.8:
            interpretation = "Forte convergence - Les experts sont largement d'accord"
            icon = "🟢"
        elif score >= 0.6:
            interpretation = "Convergence moyenne - Quelques nuances entre experts"
            icon = "🟡"
        else:
            interpretation = "Faible convergence - Divergences significatives"
            icon = "🔴"
        
        print(f"\n  {icon} Score de convergence : {score:.2f}")
        print(f"     {interpretation}")
    
    def summary_stats(self, session) -> str:
        """
        Génère un résumé statistique pédagogique.
        
        Args:
            session: Session de synthèse terminée
            
        Returns:
            Texte du résumé
        """
        if not self.enabled:
            return ""
        
        lines = [
            "",
            "┌─────────────────────────────────────────────────────────────┐",
            "│  📊 STATISTIQUES DE LA SESSION                             │",
            "├─────────────────────────────────────────────────────────────┤",
        ]
        
        # Durée
        lines.append(f"│  ⏱️  Durée totale : {session.duration_total:.1f}s")
        
        # Modèles utilisés
        models_str = ", ".join(session.models_used)
        lines.append(f"│  🤖 Modèles utilisés : {models_str}")
        
        # Rounds
        lines.append(f"│  🔄 Rounds effectués : {len(session.rounds)}")
        
        # Convergence
        lines.append(f"│  📈 Convergence finale : {session.convergence:.2f}")
        
        # Retries si disponibles
        if hasattr(session, 'retry_metrics') and session.retry_metrics:
            total_retries = sum(
                m.get('total_attempts', 1) - 1 
                for m in session.retry_metrics.values()
            )
            if total_retries > 0:
                lines.append(f"│  🔁 Retries effectués : {total_retries}")
        
        lines.append("└─────────────────────────────────────────────────────────────┘")
        
        return "\n".join(lines)
    
    @property
    def steps_shown(self) -> int:
        """Nombre d'étapes pédagogiques affichées."""
        return self._step_count


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def create_pedagogy(mode: str, interactive: bool = False) -> PedagogicPresenter:
    """
    Crée un presenter pédagogique selon le mode.
    
    Args:
        mode: Mode de synthèse (standard, rapide, critique, pedagogique)
        interactive: Mode interactif avec pauses
        
    Returns:
        PedagogicPresenter configuré
    """
    return PedagogicPresenter(
        enabled=(mode == "pedagogique"),
        interactive=interactive
    )


def get_expert_explanation(role: str, model: str) -> str:
    """
    Récupère l'explication d'un expert.
    
    Args:
        role: Rôle de l'expert
        model: Nom du modèle
        
    Returns:
        Texte d'explication formaté
    """
    content = EXPERT_EXPLANATIONS.get(role, "")
    return content.format(model=model) if content else ""


def get_layer_info(layer: str) -> Dict[str, str]:
    """
    Récupère les informations d'une couche sémiotique.
    
    Args:
        layer: Nom de la couche
        
    Returns:
        Dictionnaire avec icon, name, description, question, examples
    """
    return LAYER_EXPLANATIONS.get(layer.lower(), {})
