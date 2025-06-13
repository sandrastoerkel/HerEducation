"""
🌍 GLOBAL DISCOURSE MODELS - Data Models & Constants
Zentrale Datenmodelle und Konstanten für die globale Diskurs-Analyse
"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

class GlobalAnalysisConstants:
    """Zentrale Konstanten für globale Diskurs-Analyse"""
    
    # Verzeichnisse
    GERMAN_RESULTS_DIR = "saved_results/country_analysis"
    ENGLISH_RESULTS_DIR = "saved_results_english/country_analysis"
    
    # CSV-Spalten (aus Storage-System)
    SMART_LABELS_COLUMN = "smart_topic_labels"
    COUNTRY_COLUMN = "detected_country"
    ANALYSIS_SOURCE_COLUMN = "analysis_source"
    SENTIMENT_COLUMN = "sentiment"
    EMOTION_COLUMN = "dominant_emotion"
    TOPIC_COLUMN = "topic"
    TEXT_COLUMN = "comment_text"
    
    # Analyse-Konfiguration
    MIN_COMMENTS_PER_COUNTRY = 10
    MAX_COUNTRIES_COMPARISON = 8
    TOP_TOPICS_DISPLAY = 15
    TOP_EMOTIONS_DISPLAY = 10
    SAMPLE_COMMENTS_COUNT = 5
    
    # Visualisierung
    CHART_HEIGHT = 500
    LARGE_CHART_HEIGHT = 700
    SMALL_CHART_HEIGHT = 400
    
    # Farb-Schemas
    SENTIMENT_COLORS = {
        'positive': '#2E8B57',   # Sea Green
        'neutral': '#FFD700',    # Gold
        'negative': '#DC143C'    # Crimson
    }
    
    EMOTION_COLORS = {
        'anger': '#FF4444',      # Red
        'joy': '#FFD700',        # Gold
        'sadness': '#666666',    # Dark Gray
        'fear': '#FFA500',       # Orange
        'disgust': '#808000',    # Olive
        'surprise': '#800080',   # Purple
        'neutral': '#87CEEB',    # Sky Blue
        'none of them': '#87CEEB' # Sky Blue (German model)
    }
    
    # Logging
    LOGGER_NAME = "global_discourse_analysis"


class AnalysisType(Enum):
    """Verfügbare Analyse-Typen"""
    SENTIMENT_COMPARISON = "sentiment_comparison"
    TOPIC_COMPARISON = "topic_comparison"
    EMOTION_COMPARISON = "emotion_comparison"
    ADVANCED_INSIGHTS = "advanced_insights"


class CountryGrouping(Enum):
    """Länder-Gruppierungsoptionen"""
    INDIVIDUAL = "individual"
    LINGUISTIC = "linguistic"
    REGIONAL = "regional"
    CUSTOM = "custom"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class AnalysisFile:
    """Information über eine Analyse-Datei"""
    file_path: Path
    filename: str
    country: str
    language: str
    analysis_date: datetime
    file_size: int
    row_count: Optional[int] = None
    has_smart_labels: bool = False
    source_analysis: Optional[str] = None
    
    @property
    def display_name(self) -> str:
        """Benutzerfreundlicher Anzeigename"""
        return f"{self.country}: {self.filename[:50]}{'...' if len(self.filename) > 50 else ''}"


@dataclass
class CountryData:
    """Aggregierte Daten für ein Land"""
    country: str
    language: str
    total_comments: int
    analysis_files: List[AnalysisFile]
    
    # Sentiment-Daten
    sentiment_distribution: Dict[str, int] = field(default_factory=dict)
    sentiment_percentages: Dict[str, float] = field(default_factory=dict)
    
    # Topic-Daten (Smart Labels)
    topic_distribution: Dict[str, int] = field(default_factory=dict)
    topic_percentages: Dict[str, float] = field(default_factory=dict)
    
    # Emotion-Daten
    emotion_distribution: Dict[str, int] = field(default_factory=dict)
    emotion_percentages: Dict[str, float] = field(default_factory=dict)
    
    # Topic-Emotion-Kombinationen
    topic_emotion_matrix: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # Topic-Sentiment-Kombinationen
    topic_sentiment_matrix: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # Metadaten
    date_range: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now(), datetime.now()))
    analysis_sources: Set[str] = field(default_factory=set)
    
    @property
    def top_topics(self) -> List[Tuple[str, int]]:
        """Top Topics nach Häufigkeit"""
        return sorted(self.topic_distribution.items(), key=lambda x: x[1], reverse=True)
    
    @property
    def dominant_sentiment(self) -> str:
        """Dominierendes Sentiment"""
        return max(self.sentiment_distribution.items(), key=lambda x: x[1])[0] if self.sentiment_distribution else "unknown"
    
    @property
    def dominant_emotion(self) -> str:
        """Dominierende Emotion"""
        return max(self.emotion_distribution.items(), key=lambda x: x[1])[0] if self.emotion_distribution else "unknown"


@dataclass
class ComparisonResult:
    """Ergebnis einer Länder-Vergleichsanalyse"""
    countries: List[str]
    analysis_type: AnalysisType
    country_data: Dict[str, CountryData]
    
    # Vergleichsmetriken
    total_comments: int
    date_range: Tuple[datetime, datetime]
    languages: Set[str]
    
    # Sentiment-Vergleich
    sentiment_comparison: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Topic-Vergleich
    common_topics: List[str] = field(default_factory=list)
    unique_topics_per_country: Dict[str, List[str]] = field(default_factory=dict)
    topic_similarity_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Emotion-Vergleich
    emotion_comparison: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Insights
    insights: List[str] = field(default_factory=list)
    
    @property
    def summary(self) -> str:
        """Zusammenfassung des Vergleichs"""
        return f"Vergleich von {len(self.countries)} Ländern mit {self.total_comments:,} Kommentaren"


@dataclass
class VisualizationConfig:
    """Konfiguration für Visualisierungen"""
    chart_type: str = "bar"
    color_scheme: str = "default"
    show_percentages: bool = True
    show_labels: bool = True
    height: int = GlobalAnalysisConstants.CHART_HEIGHT
    title_prefix: str = ""
    
    # Interaktivität
    enable_hover: bool = True
    enable_zoom: bool = True
    enable_selection: bool = False


# =============================================================================
# THEME SEARCH DATA MODELS
# =============================================================================

@dataclass
class ThemeSearchResult:
    """Ergebnis einer themenbasierten Suche"""
    theme_keywords: List[str]
    countries_found: List[str] 
    total_matching_comments: int
    
    # Pro Land
    country_results: Dict[str, 'CountryThemeResult'] = field(default_factory=dict)
    
    # Globale Insights
    global_sentiment_distribution: Dict[str, float] = field(default_factory=dict)
    global_emotion_distribution: Dict[str, float] = field(default_factory=dict)
    most_discussed_country: Optional[str] = None
    sample_comments: List[Dict] = field(default_factory=list)


@dataclass 
class CountryThemeResult:
    """Themen-Ergebnis für ein spezifisches Land"""
    country: str
    matching_comments_count: int
    
    # Sentiment für dieses Thema in diesem Land
    sentiment_distribution: Dict[str, int] = field(default_factory=dict)
    sentiment_percentages: Dict[str, float] = field(default_factory=dict)
    
    # Emotionen für dieses Thema in diesem Land  
    emotion_distribution: Dict[str, int] = field(default_factory=dict)
    emotion_percentages: Dict[str, float] = field(default_factory=dict)
    
    # Smart Labels die das Thema enthalten
    related_smart_labels: List[str] = field(default_factory=list)
    
    # Sample-Kommentare für dieses Thema
    sample_comments: List[Dict] = field(default_factory=list)
    
    @property
    def dominant_sentiment(self) -> str:
        """Dominierendes Sentiment für dieses Thema"""
        return max(self.sentiment_distribution.items(), key=lambda x: x[1])[0] if self.sentiment_distribution else "unknown"
    
    @property 
    def dominant_emotion(self) -> str:
        """Dominierende Emotion für dieses Thema"""
        return max(self.emotion_distribution.items(), key=lambda x: x[1])[0] if self.emotion_distribution else "unknown"


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Constants
    'GlobalAnalysisConstants',
    'AnalysisType',
    'CountryGrouping',
    
    # Main Data Models
    'AnalysisFile',
    'CountryData', 
    'ComparisonResult',
    'VisualizationConfig',
    
    # Theme Search Models
    'ThemeSearchResult',
    'CountryThemeResult'
]