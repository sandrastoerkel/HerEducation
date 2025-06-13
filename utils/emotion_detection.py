"""
🎯 MODERNISIERTE EMOTION DETECTION (Konservativ)
Verbesserte Version mit Type Hints, Konstanten und besserer Struktur
Alle ursprünglichen Funktionen bleiben erhalten!
"""

import pandas as pd
import numpy as np
import re
from collections import Counter
from typing import Dict, List, Optional, Any, Union

# ==========================================
# 📊 KONSTANTEN (statt Magic Numbers)
# ==========================================

# Text Processing Konstanten
DEFAULT_CHUNK_SIZE: int = 512
DEFAULT_OVERLAP: int = 100
MIN_TEXT_LENGTH: int = 10
MIN_CHUNK_LENGTH: int = 10
MIN_SENTENCE_LENGTH: int = 5

# Emotion Analysis Konfiguration
MAX_AGGREGATION_METHOD: str = "max"  # Für Chunk-Aggregation
NEGATION_MODIFIER: float = 0.7
NEUTRAL_NEGATION_MODIFIER: float = 0.5
INTENSIFIER_BOOST: float = 1.2
NEGATION_REDUCTION: float = 0.5

# ==========================================
# 🎨 EMOTION MAPPINGS & COLORS
# ==========================================

# Label-Mapping für das Emotionserkennungsmodell
EMOTION_LABEL_MAP: Dict[str, str] = {
    "LABEL_0": "anger",
    "LABEL_1": "fear", 
    "LABEL_2": "disgust",
    "LABEL_3": "sadness",
    "LABEL_4": "joy",
    "LABEL_5": "none of them"
}

# Emotionen-Farben definieren
EMOTION_COLORS: Dict[str, str] = {
    "anger": "#FF5252",       # Rot
    "sadness": "#757575",     # Dunkelgrau
    "disgust": "#8BC34A",     # Olivgrün
    "fear": "#FF9800",        # Orange
    "joy": "#FFD700",         # Gold
    "none of them": "#64B5F6" # Hellblau
}

# ==========================================
# 🔍 EMOTION KEYWORDS (Vollständige Listen beibehalten!)
# ==========================================

# Emotion Keywords - VOLLSTÄNDIGE Listen beibehalten für bessere Erkennung
EMOTION_KEYWORDS: Dict[str, List[str]] = {
    "joy": [
        "freue", "glücklich", "toll", "super", "gut", "schön", "perfekt", "wunderbar", "prima", 
        "herrlich", "begeistert", "liebe", "positiv", "dankbar", "großartig", "lachen", "witz", 
        "spaß", "genial", "hervorragend", "klasse", "fantastisch", "ausgezeichnet", "froh", 
        "glück", "heiter", "fröhlich", "vergnügt", "zufrieden", "beglückt", "erfreut", "entzückt", 
        "jubelnd", "strahlend", "hell", "sonnig", "bravourös", "brillant", "erfolgreich", 
        "vortrefflich", "exzellent", "paradiesisch", "himmlisch", "grandios", "beeindruckend", 
        "phänomenal", "unglaublich", "sensationell", "fabelhaft", "cool", "geil", "hammer", 
        "spitze", "geniessen", "genießen", "feier", "party", "jubel", "applaus", "bereichernd"
    ],
    "sadness": [
        "traurig", "schade", "leider", "enttäuscht", "vermisse", "bedauern", "deprimierend", 
        "schlimm", "schrecklich", "tut mir leid", "verloren", "hoffnungslos", "entmutigt", 
        "trauer", "unglücklich", "niedergeschlagen", "mitleid", "verzweifelt", "bedrückt", 
        "betrübt", "melancholisch", "depressiv", "elend", "jammervoll", "kläglich", "miserabel", 
        "jämmerlich", "tragisch", "trostlos", "düster", "seufzend", "kummervoll", "sorgen", 
        "besorgt", "bekümmert", "gram", "leidvoll", "herzzerreißend", "herzlos", "ernüchternd", 
        "resigniert", "aufgegeben", "pessimistisch", "sinnlos", "vergeblich", "frustrierend", 
        "hoffnungslosigkeit", "verlust", "vermissen", "schmerzhaft", "wehmütig", "weinen", 
        "tränen", "schluchzen", "weinend", "einsam", "allein", "verlassen", "isoliert"
    ],
    "fear": [
        "angst", "sorge", "beunruhigt", "erschreckend", "fürchte", "gefährlich", "bedrohlich", 
        "unsicher", "panik", "bange", "beängstigend", "furcht", "befürchtung", "schrecken", 
        "verunsichert", "ungewiss", "nervös", "zittern", "schaudern", "schaudernd", "schaurig", 
        "unheimlich", "gruselig", "furchtbar", "furchtsam", "beunruhigend", "alarmierend", 
        "bedenklich", "bedroht", "riskant", "risikoreich", "kritisch", "gefahr", "terrorisiert", 
        "schockiert", "panisch", "hysterisch", "entsetzt", "bestürzt", "erschüttert", "erschrocken", 
        "grauenhaft", "grausig", "gräulich", "angstvoll", "beklemmend", "verhängnisvoll", 
        "katastrophal", "hoffnungslos", "düster", "alptraumhaft", "schreckenerregend", "finster", 
        "schwierig", "kompliziert", "überfordernd", "ängstigen", "ängstlich", "verängstigt"
    ],
    "disgust": [
        "widerlich", "ekelhaft", "abstoßend", "absurd", "unmöglich", "unerträglich", 
        "schrecklich", "schlimm", "skandalös", "inakzeptabel", "empörend", "unverzeihlich", 
        "abscheulich", "grotesk", "geschmacklos", "respektlos", "abscheu", "ekel", "angewidert", 
        "widerwärtig", "scheußlich", "eklig", "grausam", "grässlich", "garstig", "unappetitlich", 
        "unausstehlich", "unanständig", "unverschämt", "unzumutbar", "obszön", "pervers", 
        "verdorben", "verrottet", "verschimmelt", "verfault", "verdreckt", "schmutzig", "dreckig", 
        "unmoralisch", "verwerflich", "gemein", "böse", "fies", "widerwertig", "beschämend", 
        "verabscheuenswert", "verabscheuungswürdig", "widerstreben", "abwertend", "erniedrigend", 
        "verächtlich", "verachtend", "verachtungsvoll", "verpönt", "übelst", "beklagenswert"
    ],
    "anger": [
        "wütend", "ärgerlich", "zornig", "empört", "frustriert", "verärgert", "wut", "zorn", 
        "aggressiv", "erbost", "unverschämt", "bescheuert", "dumm", "idiot", "unfair", 
        "unmöglich", "respektlos", "beleidigend", "frech", "ärger", "irritiert", "genervt", 
        "gereizt", "reizbar", "aufgebracht", "entrüstet", "erzürnt", "grimmig", "wutentbrannt", 
        "aufgeregt", "aufgebracht", "rasend", "tobend", "ausraster", "explodieren", "fuchsteufelswild", 
        "stinksauer", "wutschnaubend", "aufbrausend", "hitzig", "cholerisch", "zornesröte", 
        "böse", "verbittert", "hasserfüllt", "gehässig", "feindselig", "angriffig", "bissig", 
        "bissigkeit", "gemein", "niederträchtig", "tückisch", "ungerecht", "ungeheuerlich", 
        "verdrossen", "empörung", "trotz", "trotzig", "provokativ", "verdammt", "verflucht", 
        "verstimmt", "aufregen", "erregen", "verspotten", "verhöhnen", "hässlich", "scheisse", 
        "scheiße", "mist", "verdammte", "verfluchte", "erbärmlich", "lächerlich", "unverschämtheit", 
        "unerhört", "skandal", "skandalös", "wahnsinn", "wahnsinnig", "katastrophe"
    ],
    "none of them": [
        "neutral", "objektiv", "sachlich", "faktisch", "tatsächlich", "eigentlich", 
        "übrigens", "nebenbei", "bemerkenswert", "normal", "typisch", "gewöhnlich", 
        "üblich", "alltäglich", "mittelmäßig", "durchschnittlich", "gemäßigt", "ausgeglichen", 
        "balanciert", "moderat", "unparteiisch", "unbefangen", "unvoreingenommen", "unbiased", 
        "fair", "gerecht", "ausgewogen", "besonnen", "vernünftig", "rational", "logisch", 
        "pragmatisch", "praktisch", "realistisch", "nüchtern", "klar", "unmissverständlich", 
        "eindeutig", "präzise", "genau", "akkurat", "exakt", "korrekt", "stimmig", "konsequent", 
        "konstant", "gleichbleibend", "erwartungsgemäß", "vorhersehbar", "routinemäßig", 
        "standardmäßig", "gewöhnlich", "herkömmlich", "konventionell", "traditionell", 
        "informativ", "informierend", "aufklärend", "erklärend", "beschreibend", "darstellend", 
        "berichtend", "erläuternd", "darlegend", "ausführend", "äußernd", "bemerkend", 
        "mitteilend", "erwähnend"
    ]
}

# ==========================================
# 🔧 LINGUISTIC ANALYSIS CONSTANTS
# ==========================================

# Deutsche Sprachwörter
NEGATION_WORDS: List[str] = [
    "nicht", "kein", "keine", "keinen", "keiner", "keines", "niemals", "nie"
]

CONTRAST_WORDS: List[str] = [
    "aber", "jedoch", "allerdings", "hingegen", "dennoch", "trotzdem", 
    "obwohl", "während"
]

INTENSIFIER_WORDS: List[str] = [
    "sehr", "extrem", "absolut", "völlig", "total", "komplett", 
    "besonders", "äußerst"
]

# ==========================================
# 🎯 CORE EMOTION DETECTION FUNCTIONS
# ==========================================

def detect_emotions(
    text: str, 
    emotion_classifier: Any,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
) -> Optional[Dict[str, float]]:
    """
    🎯 MODERNISIERT: Erkennt Emotionen im Text durch Aufteilung in überlappende Chunks
    
    Args:
        text: Text zur Analyse
        emotion_classifier: Das Emotions-Erkennungsmodell  
        chunk_size: Größe der Text-Chunks
        overlap: Überlappung zwischen den Chunks in Zeichen
        
    Returns:
        Dictionary mit aggregierten Emotions-Scores oder None bei Fehlern
    """
    
    # Input Validation
    if not _validate_emotion_input(text, emotion_classifier):
        return None
    
    text_str = str(text)
    
    try:
        # Kurze Texte direkt analysieren
        if len(text_str) <= chunk_size:
            return _analyze_single_chunk(text_str, emotion_classifier)
        
        # Lange Texte in Chunks aufteilen
        chunks = _create_text_chunks(text_str, chunk_size, overlap)
        
        if not chunks:
            return None
            
        # Emotions-Scores für jeden Chunk sammeln
        all_scores = _collect_chunk_scores(chunks, emotion_classifier)
        
        # Aggregiere die Scores
        return _aggregate_emotion_scores(all_scores)
        
    except Exception as e:
        # Logging könnte hier hinzugefügt werden
        return None

def _validate_emotion_input(text: Any, emotion_classifier: Any) -> bool:
    """Validiert Input für Emotionserkennung"""
    if emotion_classifier is None:
        return False
    
    if pd.isna(text) or text is None or text == "":
        return False
        
    if len(str(text)) < MIN_TEXT_LENGTH:
        return False
        
    return True

def _analyze_single_chunk(text: str, emotion_classifier: Any) -> Optional[Dict[str, float]]:
    """Analysiert einen einzelnen Text-Chunk"""
    try:
        preds = emotion_classifier(text)
        
        # Konvertiere LABEL_X in tatsächliche Emotionen
        result = {}
        for item in preds[0]:
            emotion_name = EMOTION_LABEL_MAP.get(item['label'], item['label'])
            result[emotion_name] = item['score']
        
        return result
    except Exception:
        return None

def _create_text_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Erstellt überlappende Text-Chunks"""
    chunks = []
    
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if len(chunk) >= MIN_CHUNK_LENGTH:
            chunks.append(chunk)
    
    return chunks

def _collect_chunk_scores(chunks: List[str], emotion_classifier: Any) -> Dict[str, List[float]]:
    """Sammelt Emotions-Scores für alle Chunks"""
    all_scores = {}
    
    for chunk in chunks:
        try:
            preds = emotion_classifier(chunk)
            
            # Scores aus diesem Chunk extrahieren
            for item in preds[0]:
                emotion_name = EMOTION_LABEL_MAP.get(item['label'], item['label'])
                if emotion_name not in all_scores:
                    all_scores[emotion_name] = []
                
                all_scores[emotion_name].append(item['score'])
        except Exception:
            continue  # Skip problematic chunks
    
    return all_scores

def _aggregate_emotion_scores(all_scores: Dict[str, List[float]]) -> Dict[str, float]:
    """Aggregiert Emotions-Scores (verwendet Maximum)"""
    result = {}
    
    for emotion, scores in all_scores.items():
        if scores:
            # Maximum wird verwendet, da starke emotionale Ausdrücke 
            # nicht durch neutrale Teile abgeschwächt werden sollen
            result[emotion] = max(scores)
        else:
            result[emotion] = 0.0
    
    return result

# ==========================================
# 🔍 SENTENCE ANALYSIS FUNCTIONS  
# ==========================================

def analyze_sentence_structure(text: str) -> Dict[str, bool]:
    """
    🎯 MODERNISIERT: Analysiert Satzstruktur für bessere Emotionserkennung
    
    Args:
        text: Der zu analysierende Text
        
    Returns:
        Dictionary mit Hinweisen zur Satzstruktur
    """
    if not _validate_text_input(text):
        return {}
    
    text_str = str(text)
    text_lower = text_str.lower()
    text_words = text_lower.split()
    
    return {
        "negation_present": _has_negation(text_words),
        "contrast_present": _has_contrast(text_words), 
        "intensifier_present": _has_intensifier(text_words),
        "question_present": "?" in text_str,
        "exclamation_present": "!" in text_str
    }

def _validate_text_input(text: Any) -> bool:
    """Validiert Text Input"""
    return not (pd.isna(text) or text is None or text == "")

def _has_negation(words: List[str]) -> bool:
    """Prüft auf Negationswörter"""
    return any(word in words for word in NEGATION_WORDS)

def _has_contrast(words: List[str]) -> bool:
    """Prüft auf Kontrastwörter"""
    return any(word in words for word in CONTRAST_WORDS)

def _has_intensifier(words: List[str]) -> bool:
    """Prüft auf Verstärkungswörter"""
    return any(word in words for word in INTENSIFIER_WORDS)

def split_text_into_sentences(text: str) -> List[str]:
    """
    🎯 MODERNISIERT: Teilt Text in Sätze auf
    
    Args:
        text: Der zu teilende Text
        
    Returns:
        Liste von Sätzen
    """
    if not _validate_text_input(text):
        return []
    
    text_str = str(text)
    
    # Komplexeres Muster für deutsche Satzenden
    # Berücksichtigt Abkürzungen wie "Dr.", "z.B." usw.
    exceptions = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s')
    
    # Text aufteilen
    sentences = exceptions.split(text_str)
    
    # Leere und zu kurze Sätze entfernen
    return [
        s.strip() 
        for s in sentences 
        if s.strip() and len(s.strip()) > MIN_SENTENCE_LENGTH
    ]

# ==========================================
# 📝 LINGUISTIC EMOTION ANALYSIS
# ==========================================

def analyze_emotional_content(
    sentence: str, 
    emotion_keywords: Dict[str, List[str]]
) -> Dict[str, float]:
    """
    🎯 MODERNISIERT: Analysiert Satz auf emotionale Inhalte
    
    Args:
        sentence: Der zu analysierende Satz
        emotion_keywords: Dictionary mit Emotionen und Schlüsselwörtern
        
    Returns:
        Dictionary mit erkannten Emotionen und ihrer Stärke
    """
    if not sentence or not emotion_keywords:
        return {}
    
    results = {}
    sentence_lower = sentence.lower()
    sentence_words = sentence_lower.split()
    
    # Prüfe auf Negation
    has_negation = _has_negation(sentence_words)
    
    # Für jede Emotion prüfen
    for emotion, keywords in emotion_keywords.items():
        count = sum(1 for keyword in keywords if keyword in sentence_lower)
        
        if count > 0:
            # Negations-Behandlung
            if has_negation:
                results = _handle_negated_emotion(results, emotion, count)
            else:
                # Normale Emotionszuweisung
                results[emotion] = results.get(emotion, 0) + count
    
    # Normalisiere die Ergebnisse
    return _normalize_emotion_results(results)

def _handle_negated_emotion(
    results: Dict[str, float], 
    emotion: str, 
    count: int
) -> Dict[str, float]:
    """Behandelt negierte Emotionen"""
    
    if emotion in ["joy", "anger", "disgust"]:
        # "nicht wütend" -> erhöhe "none of them"
        results["none of them"] = results.get("none of them", 0) + count * NEGATION_MODIFIER
    elif emotion == "none of them":
        # "nicht neutral" -> leicht negative Emotion
        results["sadness"] = results.get("sadness", 0) + count * NEUTRAL_NEGATION_MODIFIER
    else:
        # Andere Emotionen normal behandeln
        results[emotion] = results.get(emotion, 0) + count
    
    return results

def _normalize_emotion_results(results: Dict[str, float]) -> Dict[str, float]:
    """Normalisiert Emotions-Ergebnisse"""
    if not results:
        return {}
    
    total = sum(results.values())
    if total <= 0:
        return {}
    
    return {k: v/total for k, v in results.items()}

def get_emotion_keywords() -> Dict[str, List[str]]:
    """
    🎯 MODERNISIERT: Liefert Schlüsselwörter für Emotionserkennung
    
    Returns:
        Dictionary mit Emotionen und zugehörigen Schlüsselwörtern - VOLLSTÄNDIGE Listen!
    """
    return EMOTION_KEYWORDS

# ==========================================
# 🎯 MAIN CONTEXTUAL ANALYSIS FUNCTION
# ==========================================

def contextual_emotion_detection(text: str, emotion_classifier: Any) -> Optional[Dict[str, Union[float, int]]]:
    """
    🎯 MODERNISIERT: Erweiterte Emotionserkennung mit linguistischer Analyse
    
    Args:
        text: Text zur Analyse
        emotion_classifier: Das Emotions-Erkennungsmodell
        
    Returns:
        Dictionary mit Emotions-Scores, linguistischen Scores und Sentence Counts
    """
    # Grundlegende Emotionserkennung über das Modell
    model_emotions = detect_emotions(text, emotion_classifier)
    
    if model_emotions is None:
        return None
    
    # Erweiterte linguistische Analyse
    linguistic_results = _perform_linguistic_analysis(text)
    
    # Kombiniere Modell- und linguistische Ergebnisse
    return _combine_emotion_results(model_emotions, linguistic_results)

def _perform_linguistic_analysis(text: str) -> Dict[str, List[float]]:
    """Führt linguistische Analyse durch"""
    emotion_keywords = get_emotion_keywords()  # Verwende die Funktion für Konsistenz
    sentences = split_text_into_sentences(text)
    
    # Satzstruktur und Emotionen analysieren
    sentence_structures = [analyze_sentence_structure(s) for s in sentences]
    sentence_emotions = [analyze_emotional_content(s, emotion_keywords) for s in sentences]
    
    # Aggregiere linguistische Emotionen
    linguistic_emotions = {}
    
    for i, emotions in enumerate(sentence_emotions):
        structure = sentence_structures[i]
        
        for emotion, score in emotions.items():
            # Strukturelle Modifikationen
            modified_score = _apply_structural_modifications(score, structure)
            
            # Sammle Scores
            if emotion not in linguistic_emotions:
                linguistic_emotions[emotion] = []
            linguistic_emotions[emotion].append(modified_score)
    
    return linguistic_emotions

def _apply_structural_modifications(score: float, structure: Dict[str, bool]) -> float:
    """Wendet strukturelle Modifikationen auf Emotion-Score an"""
    
    # Verstärkung bei Ausrufen und Verstärkungswörtern
    if structure.get("exclamation_present") or structure.get("intensifier_present"):
        score *= INTENSIFIER_BOOST
    
    # Abschwächung bei Negation (für bestimmte Emotionen)
    if structure.get("negation_present"):
        score *= NEGATION_REDUCTION
    
    return score

def _combine_emotion_results(
    model_emotions: Dict[str, float], 
    linguistic_results: Dict[str, List[float]]
) -> Dict[str, Union[float, int]]:
    """Kombiniert Modell- und linguistische Ergebnisse"""
    
    combined_emotions = model_emotions.copy()
    
    # Integriere linguistische Analyse
    for emotion, scores in linguistic_results.items():
        if scores:
            # Durchschnitt der linguistischen Scores
            avg_score = sum(scores) / len(scores)
            
            # Füge linguistische Information als separate Felder hinzu
            combined_emotions[f"{emotion}_linguistic"] = avg_score
            combined_emotions[f"{emotion}_sentence_count"] = len(scores)
    
    return combined_emotions

# ==========================================
# 🧪 UTILITY FUNCTIONS
# ==========================================

def get_emotion_statistics(emotions: Dict[str, float]) -> Dict[str, Any]:
    """
    Berechnet Statistiken für Emotions-Dictionary
    
    Args:
        emotions: Dictionary mit Emotion-Scores
        
    Returns:
        Dictionary mit Statistiken
    """
    if not emotions:
        return {}
    
    values = list(emotions.values())
    
    return {
        "total_emotions": len(emotions),
        "max_emotion": max(emotions, key=emotions.get),
        "max_score": max(values),
        "min_score": min(values),
        "avg_score": sum(values) / len(values),
        "emotion_diversity": len([v for v in values if v > 0.1])  # Emotions über 10%
    }

def validate_emotion_classifier(emotion_classifier: Any) -> bool:
    """
    Validiert ob ein Emotion Classifier funktionsfähig ist
    
    Args:
        emotion_classifier: Das zu testende Modell
        
    Returns:
        True wenn funktionsfähig, False sonst
    """
    if emotion_classifier is None:
        return False
    
    try:
        # Test mit einfachem Text
        test_result = emotion_classifier("Test text")
        return isinstance(test_result, list) and len(test_result) > 0
    except Exception:
        return False

# ==========================================
# 📊 EXPORT FUNCTIONS
# ==========================================

__all__ = [
    # Konstanten
    'EMOTION_LABEL_MAP',
    'EMOTION_COLORS', 
    'EMOTION_KEYWORDS',
    
    # Haupt-Funktionen
    'detect_emotions',
    'contextual_emotion_detection',
    'analyze_sentence_structure',
    'split_text_into_sentences',
    'analyze_emotional_content',
    'get_emotion_keywords',
    
    # Utility Functions
    'get_emotion_statistics',
    'validate_emotion_classifier'
]