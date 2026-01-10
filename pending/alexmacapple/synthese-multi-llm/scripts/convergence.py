"""
Module de calcul de convergence pour Synthèse Council.
PRD-007: Algorithme hybride robuste.
PRD-027 Story 27.1: Support convergence sémantique.

L'algorithme combine plusieurs métriques pour évaluer le degré
d'accord entre les analyses produites par les différents experts LLM.
"""

import re
import math
from typing import List, Set, Dict, Tuple, Optional, Any
from collections import Counter

# PRD-027 Story 27.1: Import conditionnel sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# STOP WORDS FRANÇAIS
# ══════════════════════════════════════════════════════════════════════════════

FRENCH_STOP_WORDS = {
    # Articles
    "le", "la", "les", "l", "un", "une", "des", "du", "de", "d",
    # Prépositions
    "à", "au", "aux", "de", "du", "des", "en", "dans", "sur", "sous",
    "avec", "sans", "pour", "par", "vers", "chez", "entre",
    # Conjonctions
    "et", "ou", "mais", "donc", "car", "ni", "or", "que", "qui", "quoi",
    # Pronoms
    "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles",
    "me", "te", "se", "lui", "leur", "eux", "y", "en",
    "ce", "cette", "ces", "cet", "celui", "celle", "ceux", "celles",
    "mon", "ton", "son", "ma", "ta", "sa", "mes", "tes", "ses",
    "notre", "votre", "leur", "nos", "vos", "leurs",
    # Verbes auxiliaires courants
    "est", "sont", "était", "étaient", "être", "été",
    "a", "ont", "avait", "avaient", "avoir", "eu",
    "fait", "faire", "dit", "dire",
    # Adverbes courants
    "ne", "pas", "plus", "moins", "très", "bien", "peu", "trop",
    "aussi", "encore", "toujours", "jamais", "déjà", "alors",
    # Autres mots vides
    "tout", "tous", "toute", "toutes", "autre", "autres",
    "même", "mêmes", "quel", "quelle", "quels", "quelles",
    "comme", "si", "quand", "où", "comment", "pourquoi",
    # Lettres seules (apostrophes)
    "c", "j", "m", "n", "s", "t", "qu"
}


# ══════════════════════════════════════════════════════════════════════════════
# PRÉTRAITEMENT DU TEXTE
# ══════════════════════════════════════════════════════════════════════════════

def preprocess_text(text: str) -> List[str]:
    """
    Prétraite un texte pour la comparaison.
    
    Étapes:
    1. Conversion en minuscules
    2. Remplacement des apostrophes par des espaces
    3. Suppression de la ponctuation
    4. Tokenisation
    5. Filtrage des stop words et tokens courts
    
    Args:
        text: Texte brut à prétraiter
        
    Returns:
        Liste de tokens normalisés
        
    Examples:
        >>> preprocess_text("L'innovation technologique, c'est l'avenir!")
        ['innovation', 'technologique', 'avenir']
        >>> preprocess_text("de la le les un une")
        []
    """
    if not text:
        return []
    
    # Minuscules
    text = text.lower()
    
    # Remplacer apostrophes par espace (gestion du français)
    text = re.sub(r"[''`']", " ", text)
    
    # Supprimer ponctuation (garder lettres, chiffres, espaces)
    text = re.sub(r"[^\w\sàâäéèêëïîôùûüç]", " ", text)
    
    # Tokeniser sur les espaces
    tokens = text.split()
    
    # Filtrer stop words et tokens trop courts (< 2 caractères)
    tokens = [
        t for t in tokens 
        if t not in FRENCH_STOP_WORDS and len(t) > 1
    ]
    
    return tokens


# ══════════════════════════════════════════════════════════════════════════════
# N-GRAMS
# ══════════════════════════════════════════════════════════════════════════════

def get_ngrams(tokens: List[str], n: int = 1) -> Set:
    """
    Génère les n-grams d'une liste de tokens.
    
    Args:
        tokens: Liste de tokens
        n: Taille des n-grams (1=unigrams, 2=bigrams, etc.)
        
    Returns:
        Ensemble de n-grams (tuples pour n>1, strings pour n=1)
        
    Examples:
        >>> get_ngrams(['a', 'b', 'c'], n=1)
        {'a', 'b', 'c'}
        >>> get_ngrams(['a', 'b', 'c'], n=2)
        {('a', 'b'), ('b', 'c')}
    """
    if not tokens:
        return set()
    
    if n == 1:
        return set(tokens)
    
    if len(tokens) < n:
        return set()
    
    ngrams = set()
    for i in range(len(tokens) - n + 1):
        ngrams.add(tuple(tokens[i:i+n]))
    
    return ngrams


# ══════════════════════════════════════════════════════════════════════════════
# SIMILARITÉ JACCARD
# ══════════════════════════════════════════════════════════════════════════════

def jaccard_similarity(set_a: Set, set_b: Set) -> float:
    """
    Calcule le coefficient de Jaccard entre deux ensembles.
    
    Jaccard(A, B) = |A ∩ B| / |A ∪ B|
    
    Args:
        set_a: Premier ensemble
        set_b: Second ensemble
        
    Returns:
        Score de similarité [0, 1]
        
    Examples:
        >>> jaccard_similarity({'a', 'b'}, {'b', 'c'})
        0.333...
        >>> jaccard_similarity({'a', 'b'}, {'a', 'b'})
        1.0
    """
    if not set_a and not set_b:
        return 1.0  # Deux ensembles vides = identiques
    
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    
    return intersection / union if union > 0 else 0.0


def jaccard_ngrams(text_a: str, text_b: str, n: int = 1) -> float:
    """
    Calcule la similarité Jaccard sur les n-grams de deux textes.
    
    Args:
        text_a: Premier texte
        text_b: Second texte
        n: Taille des n-grams
        
    Returns:
        Score de similarité [0, 1]
    """
    tokens_a = preprocess_text(text_a)
    tokens_b = preprocess_text(text_b)
    
    ngrams_a = get_ngrams(tokens_a, n)
    ngrams_b = get_ngrams(tokens_b, n)
    
    return jaccard_similarity(ngrams_a, ngrams_b)


# ══════════════════════════════════════════════════════════════════════════════
# SIMILARITÉ COSINUS
# ══════════════════════════════════════════════════════════════════════════════

def cosine_similarity(text_a: str, text_b: str) -> float:
    """
    Calcule la similarité cosinus entre deux textes.
    
    cosine(A, B) = (A · B) / (||A|| × ||B||)
    
    Utilise les fréquences de mots comme vecteurs.
    
    Args:
        text_a: Premier texte
        text_b: Second texte
        
    Returns:
        Score de similarité [0, 1]
        
    Examples:
        >>> cosine_similarity("chat noir", "chat noir")
        1.0
        >>> cosine_similarity("chat", "chien")
        0.0
    """
    tokens_a = preprocess_text(text_a)
    tokens_b = preprocess_text(text_b)
    
    if not tokens_a and not tokens_b:
        return 1.0  # Deux textes vides = identiques
    
    if not tokens_a or not tokens_b:
        return 0.0  # Un seul vide = différents
    
    # Créer les vecteurs de fréquence
    counter_a = Counter(tokens_a)
    counter_b = Counter(tokens_b)
    
    # Vocabulaire commun
    all_words = set(counter_a.keys()) | set(counter_b.keys())
    
    # Produit scalaire
    dot_product = sum(
        counter_a.get(w, 0) * counter_b.get(w, 0) 
        for w in all_words
    )
    
    # Normes
    norm_a = math.sqrt(sum(v ** 2 for v in counter_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in counter_b.values()))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


# ══════════════════════════════════════════════════════════════════════════════
# CONVERGENCE HYBRIDE
# ══════════════════════════════════════════════════════════════════════════════

# Poids par défaut pour le score hybride
DEFAULT_WEIGHTS = {
    "jaccard_unigram": 0.3,
    "jaccard_bigram": 0.2,
    "cosine": 0.5
}


def calculate_pairwise_similarity(
    text_a: str, 
    text_b: str,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calcule la similarité hybride entre deux textes.
    
    Combine:
    - Jaccard sur unigrams (mots individuels)
    - Jaccard sur bigrams (paires de mots)
    - Similarité cosinus (vecteurs de fréquence)
    
    Args:
        text_a: Premier texte
        text_b: Second texte
        weights: Poids des métriques (optionnel)
        
    Returns:
        Score de similarité [0, 1]
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    # Calculer les métriques individuelles
    jac_uni = jaccard_ngrams(text_a, text_b, n=1)
    jac_bi = jaccard_ngrams(text_a, text_b, n=2)
    cos = cosine_similarity(text_a, text_b)
    
    # Score pondéré
    score = (
        weights.get("jaccard_unigram", 0.3) * jac_uni +
        weights.get("jaccard_bigram", 0.2) * jac_bi +
        weights.get("cosine", 0.5) * cos
    )
    
    return score


# PRD-027 Story 27.1: Calculateur sémantique
class SemanticConvergenceCalculator:
    """Calcul de convergence par embeddings sémantiques."""

    _instance = None  # Singleton pour éviter rechargement du modèle

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        if not SEMANTIC_AVAILABLE:
            raise ImportError("sentence-transformers et numpy requis pour la convergence sémantique")
        self.model = SentenceTransformer(model_name)

    @classmethod
    def get_instance(cls) -> "SemanticConvergenceCalculator":
        """Retourne l'instance singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def compute(self, texts: List[str]) -> float:
        """Calcule la similarité sémantique moyenne entre tous les textes."""
        if len(texts) < 2:
            return 1.0

        embeddings = self.model.encode(texts)
        similarities = []

        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                # Cosine similarity
                dot = np.dot(embeddings[i], embeddings[j])
                norm = np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                sim = dot / norm if norm > 0 else 0
                similarities.append(float(sim))

        return sum(similarities) / len(similarities) if similarities else 0.0


def calculate_convergence(
    contents: List[str],
    weights: Optional[Dict[str, float]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calcule le score de convergence entre plusieurs textes.

    PRD-007: Algorithme hybride robuste.
    PRD-027 Story 27.1: Support sémantique optionnel.

    Pour n textes, calcule la similarité de toutes les paires
    possibles (C(n,2) = n(n-1)/2 paires) et retourne la moyenne.

    Args:
        contents: Liste des contenus à comparer
        weights: Poids des métriques (optionnel)
        config: Configuration (convergence.backend: lexical|semantic|hybrid)

    Returns:
        Dict avec:
        - lexical: Score lexical [0, 1]
        - semantic: Score sémantique [0, 1] (0 si indisponible)
        - combined: Score combiné
        - score: Score principal (pour compatibilité %)
        - method: Méthode utilisée

    Examples:
        >>> calculate_convergence(["tech innovation", "tech innovation"])
        {"lexical": 0.95, "semantic": 0.98, "combined": 0.97, "score": 97, "method": "hybrid"}
    """
    config = config or {}
    backend = config.get("convergence", {}).get("backend", "hybrid")

    # Cas dégénérés
    if not contents:
        return {"lexical": 1.0, "semantic": 1.0, "combined": 1.0, "score": 100, "method": "default"}

    # Filtrer les contenus vides
    contents = [c for c in contents if c and c.strip()]

    if len(contents) < 2:
        return {"lexical": 1.0, "semantic": 1.0, "combined": 1.0, "score": 100, "method": "default"}

    # Calculer convergence lexicale
    pair_scores = []
    for i in range(len(contents)):
        for j in range(i + 1, len(contents)):
            score = calculate_pairwise_similarity(contents[i], contents[j], weights)
            pair_scores.append(score)

    lexical = sum(pair_scores) / len(pair_scores) if pair_scores else 0.0

    # Calculer convergence sémantique si disponible et demandé
    semantic = 0.0
    method = "lexical"

    if backend in ("semantic", "hybrid") and SEMANTIC_AVAILABLE:
        try:
            calculator = SemanticConvergenceCalculator.get_instance()
            semantic = calculator.compute(contents)
            method = "semantic" if backend == "semantic" else "hybrid"
        except Exception as e:
            # Fallback silencieux
            import logging
            logging.getLogger(__name__).warning(f"Semantic convergence failed: {e}")

    # Calcul combiné
    if method == "hybrid" and semantic > 0:
        combined = 0.3 * lexical + 0.7 * semantic
    elif method == "semantic" and semantic > 0:
        combined = semantic
    else:
        combined = lexical
        method = "lexical"

    return {
        "lexical": round(lexical, 3),
        "semantic": round(semantic, 3),
        "combined": round(combined, 3),
        "score": round(combined * 100),
        "method": method
    }


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def get_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extrait les mots-clés principaux d'un texte.
    
    Args:
        text: Texte source
        top_n: Nombre de mots-clés à retourner
        
    Returns:
        Liste des mots-clés les plus fréquents
    """
    tokens = preprocess_text(text)
    
    if not tokens:
        return []
    
    counter = Counter(tokens)
    return [word for word, _ in counter.most_common(top_n)]


def interpret_convergence(score: float) -> str:
    """
    Interprète un score de convergence.
    
    Args:
        score: Score de convergence [0, 1]
        
    Returns:
        Description textuelle du niveau de convergence
    """
    if score >= 0.8:
        return "Forte convergence - Les experts sont largement d'accord"
    elif score >= 0.6:
        return "Convergence moyenne - Quelques nuances entre experts"
    elif score >= 0.4:
        return "Convergence faible - Divergences notables"
    else:
        return "Faible convergence - Perspectives très différentes"


# ══════════════════════════════════════════════════════════════════════════════
# TESTS RAPIDES (si exécuté directement)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test 1: Textes similaires (cas du test en échec)
    text_a = "Le texte parle de technologie et innovation"
    text_b = "Le texte aborde la technologie et l'innovation"
    
    score = calculate_convergence([text_a, text_b])
    print(f"Test 1 - Textes similaires:")
    print(f"  A: {text_a}")
    print(f"  B: {text_b}")
    print(f"  Score: {score:.4f} (attendu > 0.3)")
    print(f"  Résultat: {'PASS' if score > 0.3 else 'FAIL'}")
    print()
    
    # Test 2: Textes identiques
    text_c = "technologie innovation avenir"
    score2 = calculate_convergence([text_c, text_c])
    print(f"Test 2 - Textes identiques:")
    print(f"  Score: {score2:.4f} (attendu > 0.95)")
    print(f"  Résultat: {'PASS' if score2 > 0.95 else 'FAIL'}")
    print()
    
    # Test 3: Trois textes
    texts = [
        "L'analyse révèle une tendance technologique",
        "Le texte montre une évolution technique",
        "On observe des changements technologiques"
    ]
    score3 = calculate_convergence(texts)
    print(f"Test 3 - Trois textes:")
    for i, t in enumerate(texts):
        print(f"  {i+1}: {t}")
    print(f"  Score: {score3:.4f} (attendu 0.2 < x < 0.9)")
    print(f"  Résultat: {'PASS' if 0.2 < score3 < 0.9 else 'FAIL'}")
    print()
    
    # Test 4: Textes très différents
    text_d = "pommes oranges fruits"
    text_e = "voitures avions transport"
    score4 = calculate_convergence([text_d, text_e])
    print(f"Test 4 - Textes différents:")
    print(f"  Score: {score4:.4f} (attendu < 0.2)")
    print(f"  Résultat: {'PASS' if score4 < 0.2 else 'FAIL'}")
