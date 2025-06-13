"""
🌍 GLOBAL DISCOURSE THEME SEARCH MODELS - Data Models, Enums & Constants
Datenmodelle und Konstanten für erweiterte themenbasierte Länder-Analyse
"""

from typing import Dict, List, Optional, Tuple, Set, Any
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

# =============================================================================
# ENHANCED CONSTANTS AND ENUMS
# =============================================================================

class ThemeCategory(str, Enum):
    """Kategorien von vordefinierten Themen"""
    EDUCATION = "Bildung & Lernen"
    GENDER = "Gender & Gleichberechtigung"
    TECHNOLOGY = "Technologie & KI"
    ENVIRONMENT = "Umwelt & Klima"
    POLITICS = "Politik & Gesellschaft"
    ECONOMY = "Wirtschaft & Arbeit"
    HEALTH = "Gesundheit & Medizin"
    CULTURE = "Kultur & Medien"
    CUSTOM = "Benutzerdefiniert"


class SentimentCategory(str, Enum):
    """Sentiment-Kategorien für erweiterte Analyse"""
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


class EmotionCategory(str, Enum):
    """Emotion-Kategorien"""
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


# Erweiterte vordefinierte Keyword-Sets (INTERNATIONAL!)
THEME_KEYWORDS = {
    ThemeCategory.EDUCATION: [
        # Englisch
        "education", "school", "teacher", "teaching", "learning", "homework",
        "classroom", "student", "university", "college", "curriculum", "academic",
        "educational", "study", "exam", "grade", "graduation", "knowledge",
        # Deutsch
        "bildung", "schule", "lehrer", "lernen", "unterricht", "studium",
        "ausbildung", "universität", "hochschule", "abitur", "prüfung"
    ],
    
    ThemeCategory.GENDER: [
        # Englisch
        "women", "girls", "equality", "gender", "discrimination", "sexism",
        "feminism", "women's rights", "glass ceiling", "wage gap", "harassment",
        "empowerment", "patriarchy", "misogyny", "feminist", "female", "male",
        "woman", "man", "ladies", "gentlemen", "boys", "sexist", "gender equality",
        "equal rights", "equal pay", "workplace equality", "gender bias",
        "gender discrimination", "sexual harassment", "me too", "metoo",
        # Deutsch
        "frauen", "gleichberechtigung", "diskriminierung", "feminismus",
        "geschlecht", "sexismus", "emanzipation", "frauenrechte", "männer",
        "geschlechter", "gleichstellung", "benachteiligung", "sexuelle belästigung",
        # International/Allgemein
        "lgbt", "lgbtq", "queer", "transgender", "binary", "non-binary"
    ],
    
    ThemeCategory.TECHNOLOGY: [
        # Englisch
        "AI", "artificial intelligence", "ChatGPT", "GPT", "machine learning",
        "technology", "computer", "algorithm", "automation", "robot", "digital",
        "tech", "innovation", "data", "internet", "software", "coding",
        "programming", "app", "smartphone", "social media", "facebook", "twitter",
        "instagram", "youtube", "google", "apple", "microsoft", "amazon",
        # Deutsch
        "technologie", "ki", "künstliche intelligenz", "computer", "digital",
        "algorithmus", "programmierung", "software", "internet", "handy",
        "soziale medien", "anwendung", "app", "innovation"
    ],
    
    ThemeCategory.ENVIRONMENT: [
        # Englisch
        "climate", "environment", "sustainability", "green", "carbon", "pollution",
        "renewable", "energy", "global warming", "ecosystem", "conservation",
        "recycling", "biodiversity", "eco", "nature", "planet", "climate change",
        "greenhouse", "emissions", "fossil fuels", "solar", "wind energy",
        # Deutsch
        "klima", "umwelt", "nachhaltigkeit", "klimawandel", "ökologie",
        "umweltschutz", "erneuerbare energien", "co2", "emission", "recycling",
        "natur", "planet", "erderwärmung", "treibhausgas"
    ],
    
    ThemeCategory.POLITICS: [
        # Englisch
        "government", "politics", "democracy", "election", "policy", "voting",
        "politician", "parliament", "congress", "senate", "law", "legislation",
        "constitution", "rights", "freedom", "justice", "governance", "president",
        "minister", "chancellor", "prime minister", "political", "vote",
        # Deutsch
        "politik", "regierung", "demokratie", "wahl", "gesetz", "recht",
        "bundestag", "parlament", "kanzler", "minister", "politiker",
        "verfassung", "abstimmung", "partei", "politisch"
    ],
    
    ThemeCategory.ECONOMY: [
        # Englisch
        "economy", "economic", "business", "work", "job", "employment", "salary",
        "money", "finance", "market", "trade", "investment", "capitalism",
        "recession", "inflation", "unemployment", "entrepreneur", "startup",
        "company", "corporation", "profit", "revenue", "stock", "banking",
        # Deutsch
        "wirtschaft", "arbeit", "geld", "finanzen", "markt", "handel",
        "unternehmen", "firma", "arbeitsplatz", "gehalt", "einkommen",
        "inflation", "arbeitslosigkeit", "investition", "kapitalismus"
    ],
    
    ThemeCategory.HEALTH: [
        # Englisch
        "health", "healthcare", "medical", "medicine", "doctor", "hospital",
        "disease", "treatment", "therapy", "mental health", "wellness",
        "pandemic", "vaccine", "covid", "virus", "symptoms", "diagnosis",
        "patient", "nurse", "pharmaceutical", "clinic", "surgery",
        # Deutsch
        "gesundheit", "medizin", "arzt", "krankenhaus", "behandlung",
        "therapie", "krankheit", "patient", "pflege", "impfung",
        "gesundheitswesen", "klinik", "operation", "diagnose"
    ],
    
    ThemeCategory.CULTURE: [
        # Englisch
        "culture", "cultural", "art", "music", "film", "movie", "media",
        "entertainment", "social media", "youtube", "instagram", "tiktok",
        "celebrity", "fashion", "sport", "religion", "tradition", "festival",
        "concert", "theater", "museum", "book", "literature", "painting",
        # Deutsch
        "kultur", "kunst", "musik", "film", "medien", "sport", "religion",
        "tradition", "festival", "konzert", "theater", "museum", "buch",
        "literatur", "malerei", "mode", "unterhaltung"
    ]
}

# Emotion-Kategorisierung
EMOTION_CATEGORIES = {
    EmotionCategory.POSITIVE: ['joy', 'love', 'surprise'],
    EmotionCategory.NEGATIVE: ['anger', 'sadness', 'fear', 'disgust'],
    EmotionCategory.NEUTRAL: ['neutral', 'none of them']
}

# Erweiterte Farbschemas
THEME_COLORS = {
    ThemeCategory.EDUCATION: '#4CAF50',
    ThemeCategory.GENDER: '#E91E63',
    ThemeCategory.TECHNOLOGY: '#2196F3',
    ThemeCategory.ENVIRONMENT: '#4CAF50',
    ThemeCategory.POLITICS: '#FF9800',
    ThemeCategory.ECONOMY: '#9C27B0',
    ThemeCategory.HEALTH: '#F44336',
    ThemeCategory.CULTURE: '#795548',
    ThemeCategory.CUSTOM: '#607D8B'
}

# Chart-Konfiguration
DEFAULT_CHART_HEIGHT = 500
COMPACT_CHART_HEIGHT = 400
MAX_SAMPLE_COMMENTS = 5
MAX_COUNTRIES_DISPLAY = 8

# =============================================================================
# ENHANCED DATA MODELS
# =============================================================================

@dataclass
class EnhancedEmotionStatistics:
    """Erweiterte Emotion-Statistiken"""
    total_comments: int
    positive_count: int
    negative_count: int
    neutral_count: int
    emotion_distribution: Dict[str, float]
    dominant_emotion: str
    
    @property
    def positive_ratio(self) -> float:
        return self.positive_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def negative_ratio(self) -> float:
        return self.negative_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def neutral_ratio(self) -> float:
        return self.neutral_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def sentiment_score(self) -> float:
        """Berechnet einen Sentiment-Score (-100 bis +100)"""
        return (self.positive_ratio - self.negative_ratio) * 100


@dataclass
class EnhancedCountryThemeResult:
    """Erweiterte Themen-Ergebnis für ein Land"""
    country: str
    theme_category: ThemeCategory
    keywords_used: List[str]
    matching_comments_count: int
    
    # Sentiment-Daten
    sentiment_distribution: Dict[str, int] = field(default_factory=dict)
    sentiment_percentages: Dict[str, float] = field(default_factory=dict)
    
    # Emotion-Daten
    emotion_distribution: Dict[str, int] = field(default_factory=dict)
    emotion_percentages: Dict[str, float] = field(default_factory=dict)
    emotion_statistics: Optional[EnhancedEmotionStatistics] = None
    
    # Smart Labels
    related_smart_labels: List[str] = field(default_factory=list)
    top_smart_labels: List[Tuple[str, int]] = field(default_factory=list)
    
    # Sample-Kommentare
    sample_comments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Zusätzliche Metriken
    average_comment_length: float = 0.0
    unique_smart_labels_count: int = 0
    
    @property
    def dominant_sentiment(self) -> str:
        return max(self.sentiment_distribution.items(), key=lambda x: x[1])[0] if self.sentiment_distribution else "unknown"
    
    @property
    def dominant_emotion(self) -> str:
        return max(self.emotion_distribution.items(), key=lambda x: x[1])[0] if self.emotion_distribution else "unknown"
    
    @property
    def engagement_score(self) -> float:
        """Berechnet Engagement-Score basierend auf Kommentar-Anzahl"""
        return min(100, (self.matching_comments_count / 10) * 100)


@dataclass
class EnhancedThemeSearchResult:
    """Erweiterte Ergebnis einer themenbasierten Suche"""
    theme_category: ThemeCategory
    keywords_used: List[str]
    countries_found: List[str]
    total_matching_comments: int
    
    # Pro Land
    country_results: Dict[str, EnhancedCountryThemeResult] = field(default_factory=dict)
    
    # Globale Statistiken
    global_sentiment_distribution: Dict[str, float] = field(default_factory=dict)
    global_emotion_distribution: Dict[str, float] = field(default_factory=dict)
    global_emotion_statistics: Optional[EnhancedEmotionStatistics] = None
    
    # Rankings
    most_discussed_country: Optional[str] = None
    most_positive_country: Optional[str] = None
    most_negative_country: Optional[str] = None
    
    # Insights
    key_insights: List[str] = field(default_factory=list)
    country_comparisons: List[str] = field(default_factory=list)
    
    # DEBUG INFO
    debug_info: Dict[str, Dict] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        return self.total_matching_comments > 0
    
    @property
    def average_comments_per_country(self) -> float:
        return self.total_matching_comments / len(self.countries_found) if self.countries_found else 0


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Enums
    'ThemeCategory',
    'SentimentCategory', 
    'EmotionCategory',
    
    # Constants
    'THEME_KEYWORDS',
    'EMOTION_CATEGORIES',
    'THEME_COLORS',
    'DEFAULT_CHART_HEIGHT',
    'COMPACT_CHART_HEIGHT',
    'MAX_SAMPLE_COMMENTS',
    'MAX_COUNTRIES_DISPLAY',
    
    # Data Models
    'EnhancedEmotionStatistics',
    'EnhancedCountryThemeResult',
    'EnhancedThemeSearchResult'
]