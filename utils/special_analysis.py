"""
🎯 MODERNISIERTE SPECIAL ANALYSIS (Domain-spezifische Analysen)
Strukturierte Analysen für Bildungs- und Gender-Themen mit Type Hints
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# ==========================================
# 📊 KONSTANTEN (statt Magic Numbers)
# ==========================================

# UI Configuration
CHART_HEIGHT: int = 500
LARGE_CHART_HEIGHT: int = 600
MAX_EXAMPLE_COMMENTS: int = 15
MAX_SAMPLE_COMMENTS: int = 10

# Analysis Categories
class EmotionCategory(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative" 
    NEUTRAL = "neutral"

# Emotion Colors (Konsistent mit anderen Modulen)
EMOTION_COLORS: Dict[str, str] = {
    "anger": "#F44336",        # Red
    "sadness": "#424242",      # Dark Gray
    "disgust": "#689F38",      # Olive Green
    "fear": "#FF9800",         # Orange
    "joy": "#FFD700",          # Gold
    "none of them": "#81D4FA"  # Light Blue
}

# Emotion Categorization
EMOTION_MAPPING: Dict[str, List[str]] = {
    EmotionCategory.POSITIVE.value: ['joy'],
    EmotionCategory.NEGATIVE.value: ['anger', 'sadness', 'fear', 'disgust'],
    EmotionCategory.NEUTRAL.value: ['none of them']
}

# Default Keywords
DEFAULT_EDUCATION_KEYWORDS: List[str] = [
    "bildung", "schule", "lehrer", "unterricht", "lernen", 
    "hausaufgaben", "bildungssystem", "ausbildung", "studium"
]

DEFAULT_GENDER_KEYWORDS: List[str] = [
    "mädchen", "frauen", "gleichberechtigung", "gender", "benachteiligung", 
    "diskriminierung", "geschlecht", "feminismus", "diversität", "inklusion"
]

# ==========================================
# 🎛️ DATA CLASSES
# ==========================================

@dataclass
class AnalysisKeywords:
    """Schlüsselwörter für verschiedene Analyse-Typen"""
    education: List[str] = field(default_factory=lambda: DEFAULT_EDUCATION_KEYWORDS.copy())
    gender: List[str] = field(default_factory=lambda: DEFAULT_GENDER_KEYWORDS.copy())
    custom: List[str] = field(default_factory=list)
    
    def get_keywords(self, analysis_type: str) -> List[str]:
        """Gibt Keywords für einen Analyse-Typ zurück"""
        return getattr(self, analysis_type, [])

@dataclass
class AnalysisResult:
    """Ergebnis einer spezialisierten Analyse"""
    analysis_type: str
    keywords_used: List[str]
    total_comments: int
    filtered_df: pd.DataFrame
    emotion_distribution: pd.Series
    emotion_percentages: pd.Series
    topic_distribution: pd.Series
    emotion_categories: Dict[str, Tuple[int, float]]
    
    @property
    def has_results(self) -> bool:
        """Prüft ob Ergebnisse vorhanden sind"""
        return self.total_comments > 0
    
    @property
    def positive_percentage(self) -> float:
        """Gibt Anteil positiver Emotionen zurück"""
        return self.emotion_categories.get(EmotionCategory.POSITIVE.value, (0, 0.0))[1]
    
    @property
    def negative_percentage(self) -> float:
        """Gibt Anteil negativer Emotionen zurück"""
        return self.emotion_categories.get(EmotionCategory.NEGATIVE.value, (0, 0.0))[1]
    
    @property
    def neutral_percentage(self) -> float:
        """Gibt Anteil neutraler Emotionen zurück"""
        return self.emotion_categories.get(EmotionCategory.NEUTRAL.value, (0, 0.0))[1]

@dataclass
class TopicAnalysisInfo:
    """Information über Topic-Analyse für Spezial-Analysen"""
    topic_labels: Dict[int, str]
    has_topics: bool
    has_emotions: bool
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, topic_labels: Dict[int, str]) -> 'TopicAnalysisInfo':
        """Erstellt TopicAnalysisInfo aus DataFrame"""
        return cls(
            topic_labels=topic_labels,
            has_topics='topic' in df.columns,
            has_emotions='dominant_emotion' in df.columns
        )

# ==========================================
# 🔬 BUSINESS LOGIC FUNCTIONS
# ==========================================

def get_effective_topic_labels(topic_labels: Dict[int, str]) -> Dict[int, str]:
    """
    🎯 BUSINESS: Gibt die effektiven Topic-Labels zurück
    
    Args:
        topic_labels: Original Topic-Labels
        
    Returns:
        Effektive Topic-Labels (combined wenn verfügbar)
    """
    if hasattr(st.session_state, 'combined_topic_labels'):
        return st.session_state.combined_topic_labels
    return topic_labels

def filter_comments_by_keywords(df: pd.DataFrame, keywords: List[str], search_column: str = 'clean_text') -> pd.DataFrame:
    """
    🎯 BUSINESS: Filtert Kommentare basierend auf Schlüsselwörtern
    
    Args:
        df: DataFrame mit Kommentaren
        keywords: Liste von Schlüsselwörtern
        search_column: Spalte zum Durchsuchen
        
    Returns:
        Gefilterter DataFrame
    """
    if not keywords:
        return pd.DataFrame()
    
    if search_column not in df.columns:
        st.warning(f"Spalte '{search_column}' nicht gefunden. Fallback zu Text-Suche.")
        # Fallback: Suche in allen verfügbaren Text-Spalten
        text_columns = [col for col in df.columns if df[col].dtype == 'object']
        if not text_columns:
            return pd.DataFrame()
        search_column = text_columns[0]
    
    # Erstelle Regex-Pattern für Schlüsselwörter
    pattern = "|".join([kw.strip().lower() for kw in keywords if kw.strip()])
    
    if not pattern:
        return pd.DataFrame()
    
    try:
        filtered_df = df[df[search_column].str.contains(pattern, case=False, na=False)]
        return filtered_df
    except Exception as e:
        st.error(f"Fehler beim Filtern: {str(e)}")
        return pd.DataFrame()

def filter_comments_by_topics(df: pd.DataFrame, topic_ids: List[int]) -> pd.DataFrame:
    """
    🎯 BUSINESS: Filtert Kommentare basierend auf Topic-IDs
    
    Args:
        df: DataFrame mit Kommentaren
        topic_ids: Liste von Topic-IDs
        
    Returns:
        Gefilterter DataFrame
    """
    if not topic_ids or 'topic' not in df.columns:
        return pd.DataFrame()
    
    return df[df['topic'].isin(topic_ids)]

def calculate_emotion_statistics(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, Dict[str, Tuple[int, float]]]:
    """
    🎯 BUSINESS: Berechnet Emotions-Statistiken
    
    Args:
        df: DataFrame mit Emotions-Daten
        
    Returns:
        Tuple von (emotion_counts, emotion_percentages, emotion_categories)
    """
    if df.empty or 'dominant_emotion' not in df.columns:
        return pd.Series(), pd.Series(), {}
    
    emotion_counts = df['dominant_emotion'].value_counts()
    emotion_percentages = emotion_counts / len(df) * 100
    
    # Berechne Kategorien
    emotion_categories = {}
    for category, emotions in EMOTION_MAPPING.items():
        category_count = df['dominant_emotion'].isin(emotions).sum()
        category_percentage = category_count / len(df) * 100 if len(df) > 0 else 0
        emotion_categories[category] = (category_count, category_percentage)
    
    return emotion_counts, emotion_percentages, emotion_categories

def calculate_topic_distribution(df: pd.DataFrame, topic_labels: Dict[int, str]) -> pd.Series:
    """
    🎯 BUSINESS: Berechnet Topic-Verteilung
    
    Args:
        df: DataFrame mit Topic-Daten
        topic_labels: Topic-Labels Dictionary
        
    Returns:
        Topic-Verteilung mit Labels
    """
    if df.empty or 'topic' not in df.columns:
        return pd.Series()
    
    topic_counts = df['topic'].value_counts()
    
    # Wende Labels an
    topic_counts_labeled = topic_counts.copy()
    topic_counts_labeled.index = topic_counts_labeled.index.map(
        lambda x: topic_labels.get(x, f'Topic {x}')
    )
    
    return topic_counts_labeled

def create_analysis_result(
    analysis_type: str,
    keywords: List[str],
    filtered_df: pd.DataFrame,
    topic_labels: Dict[int, str]
) -> AnalysisResult:
    """
    🎯 BUSINESS: Erstellt AnalysisResult-Objekt
    
    Args:
        analysis_type: Typ der Analyse
        keywords: Verwendete Schlüsselwörter
        filtered_df: Gefilterte Daten
        topic_labels: Topic-Labels
        
    Returns:
        AnalysisResult-Objekt
    """
    emotion_counts, emotion_percentages, emotion_categories = calculate_emotion_statistics(filtered_df)
    topic_distribution = calculate_topic_distribution(filtered_df, topic_labels)
    
    return AnalysisResult(
        analysis_type=analysis_type,
        keywords_used=keywords,
        total_comments=len(filtered_df),
        filtered_df=filtered_df,
        emotion_distribution=emotion_counts,
        emotion_percentages=emotion_percentages,
        topic_distribution=topic_distribution,
        emotion_categories=emotion_categories
    )

def find_education_topics_automatically(topic_labels: Dict[int, str], keywords: List[str]) -> List[int]:
    """
    🎯 BUSINESS: Findet Bildungs-Topics automatisch
    
    Args:
        topic_labels: Topic-Labels Dictionary
        keywords: Bildungs-Schlüsselwörter
        
    Returns:
        Liste von Topic-IDs
    """
    education_topic_ids = []
    
    for topic_id, label in topic_labels.items():
        if any(keyword in label.lower() for keyword in keywords):
            education_topic_ids.append(topic_id)
    
    return education_topic_ids

# ==========================================
# 🎨 UI FUNCTIONS (Streamlit Components)
# ==========================================

def render_emotion_distribution_chart(result: AnalysisResult) -> None:
    """
    🎯 UI: Rendert Emotions-Verteilungs-Chart
    """
    if result.emotion_percentages.empty:
        st.warning("Keine Emotions-Daten für Chart verfügbar.")
        return
    
    fig = px.bar(
        x=result.emotion_percentages.index,
        y=result.emotion_percentages.values,
        color=result.emotion_percentages.index,
        color_discrete_map=EMOTION_COLORS,
        labels={'x': 'Emotion', 'y': 'Anteil (%)'},
        title=f'Emotionale Reaktion zu: {result.analysis_type.title()}'
    )
    
    fig.update_layout(
        xaxis_title='Emotion',
        yaxis_title='Anteil (%)',
        showlegend=False,
        height=CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"emotion_chart_{result.analysis_type}")

def render_topic_distribution_chart(result: AnalysisResult) -> None:
    """
    🎯 UI: Rendert Topic-Verteilungs-Chart
    """
    if result.topic_distribution.empty:
        st.warning("Keine Topic-Daten für Chart verfügbar.")
        return
    
    st.write("### Verteilung auf Themen")
    
    fig = px.bar(
        x=result.topic_distribution.values,
        y=result.topic_distribution.index,
        orientation='h',
        labels={'x': 'Anzahl Kommentare', 'y': 'Thema'},
        title=f'Verteilung der {result.analysis_type.title()}-Kommentare auf Themen'
    )
    
    fig.update_layout(
        xaxis_title='Anzahl der Kommentare',
        yaxis_title='Thema',
        height=max(CHART_HEIGHT, len(result.topic_distribution) * 30)  # Dynamische Höhe
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"topic_chart_{result.analysis_type}")

def render_emotion_category_metrics(result: AnalysisResult) -> None:
    """
    🎯 UI: Rendert Emotions-Kategorie-Metriken
    """
    st.write("### Zusammenfassung der emotionalen Reaktionen")
    
    col1, col2, col3 = st.columns(3)
    
    pos_count, pos_pct = result.emotion_categories.get(EmotionCategory.POSITIVE.value, (0, 0.0))
    neg_count, neg_pct = result.emotion_categories.get(EmotionCategory.NEGATIVE.value, (0, 0.0))
    neu_count, neu_pct = result.emotion_categories.get(EmotionCategory.NEUTRAL.value, (0, 0.0))
    
    col1.metric("Positiv", f"{pos_count}", f"{pos_pct:.1f}%")
    col2.metric("Negativ", f"{neg_count}", f"{neg_pct:.1f}%")
    col3.metric("Neutral", f"{neu_count}", f"{neu_pct:.1f}%")

def render_example_comments(result: AnalysisResult, text_column: str, topic_labels: Dict[int, str]) -> None:
    """
    🎯 UI: Rendert Beispiel-Kommentare
    """
    if result.filtered_df.empty:
        return
    
    st.write(f"### Beispiele für {result.analysis_type.title()}-Kommentare")
    
    with st.expander("Kommentare anzeigen"):
        sample_df = result.filtered_df.head(MAX_EXAMPLE_COMMENTS)
        
        for i, (_, row) in enumerate(sample_df.iterrows()):
            st.write(f"**Kommentar {i + 1}:**")
            st.write(f"🗨️ \"{row[text_column]}\"")
            st.write(f"😐 Emotion: {row['dominant_emotion']}")
            
            if 'topic' in row.index:
                topic_label = topic_labels.get(row['topic'], f"Topic {row['topic']}")
                st.write(f"🏷️ Thema: {topic_label}")
            
            st.write("---")

def render_keywords_input(label: str, default_keywords: List[str], key: str) -> List[str]:
    """
    🎯 UI: Rendert Schlüsselwort-Eingabe
    
    Args:
        label: Label für Input
        default_keywords: Standard-Schlüsselwörter
        key: Unique key für Streamlit
        
    Returns:
        Liste von Schlüsselwörtern
    """
    keywords_str = st.text_input(
        label,
        value=", ".join(default_keywords),
        key=key
    )
    
    if keywords_str:
        return [kw.strip().lower() for kw in keywords_str.split(",") if kw.strip()]
    
    return []

def render_topic_selection(topic_labels: Dict[int, str], default_topics: List[int], key: str) -> List[int]:
    """
    🎯 UI: Rendert Topic-Auswahl
    
    Args:
        topic_labels: Topic-Labels Dictionary
        default_topics: Vorausgewählte Topics
        key: Unique key für Streamlit
        
    Returns:
        Liste von gewählten Topic-IDs
    """
    all_topics = sorted(list(topic_labels.keys()))
    
    selected_topics = st.multiselect(
        "Relevante Themen auswählen:",
        options=all_topics,
        default=default_topics,
        format_func=lambda x: topic_labels.get(x, f'Topic {x}'),
        key=key
    )
    
    return selected_topics

# ==========================================
# 🔍 SPECIALIZED ANALYSIS FUNCTIONS
# ==========================================

def perform_education_analysis(df: pd.DataFrame, text_column: str, topic_labels: Dict[int, str]) -> None:
    """
    🎯 ANALYSIS: Führt Bildungsthemen-Analyse durch
    
    Args:
        df: DataFrame mit Kommentar-Daten
        text_column: Name der Text-Spalte
        topic_labels: Topic-Labels Dictionary
    """
    st.write("### Emotionale Reaktion auf Bildungsthemen")
    
    keywords = AnalysisKeywords()
    effective_labels = get_effective_topic_labels(topic_labels)
    
    # Automatische Topic-Erkennung
    education_topic_ids = find_education_topics_automatically(effective_labels, keywords.education)
    
    if not education_topic_ids:
        st.warning("Keine Bildungsthemen automatisch erkannt. Bitte wählen Sie relevante Themen aus.")
    
    # Topic-Auswahl UI
    selected_topics = render_topic_selection(
        effective_labels, 
        education_topic_ids, 
        "education_topics"
    )
    
    if not selected_topics:
        st.warning("Bitte wählen Sie mindestens ein Bildungsthema aus.")
        return
    
    # Analysis durchführen
    filtered_df = filter_comments_by_topics(df, selected_topics)
    
    if filtered_df.empty:
        st.warning("Keine Kommentare zu den ausgewählten Bildungsthemen gefunden.")
        return
    
    # Ergebnis erstellen
    result = create_analysis_result("Bildung", [], filtered_df, effective_labels)
    
    # UI rendern
    st.write(f"Gefundene Kommentare zu Bildungsthemen: {result.total_comments}")
    
    render_emotion_distribution_chart(result)
    render_emotion_category_metrics(result)
    render_example_comments(result, text_column, effective_labels)

def perform_gender_analysis(df: pd.DataFrame, text_column: str, topic_labels: Dict[int, str]) -> None:
    """
    🎯 ANALYSIS: Führt Gender-Themen-Analyse durch
    
    Args:
        df: DataFrame mit Kommentar-Daten
        text_column: Name der Text-Spalte
        topic_labels: Topic-Labels Dictionary
    """
    st.write("### Analyse zu Gender-Themen")
    
    keywords = AnalysisKeywords()
    effective_labels = get_effective_topic_labels(topic_labels)
    
    # Keywords-Input
    st.write(f"Standard-Schlüsselwörter: {', '.join(keywords.gender)}")
    
    custom_keywords = render_keywords_input(
        "Passen Sie die Schlüsselwörter an (durch Komma getrennt):",
        keywords.gender,
        "gender_keywords"
    )
    
    if not custom_keywords:
        st.warning("Bitte geben Sie mindestens ein Schlüsselwort ein.")
        return
    
    # Analysis durchführen
    filtered_df = filter_comments_by_keywords(df, custom_keywords)
    
    if filtered_df.empty:
        st.warning("Keine Kommentare zu Gender-Themen gefunden.")
        return
    
    # Ergebnis erstellen
    result = create_analysis_result("Gender", custom_keywords, filtered_df, effective_labels)
    
    # UI rendern
    st.write(f"Gefundene Kommentare zu Gender-Themen: {result.total_comments}")
    
    render_emotion_distribution_chart(result)
    render_emotion_category_metrics(result)
    render_topic_distribution_chart(result)
    render_example_comments(result, text_column, effective_labels)

def perform_custom_analysis(df: pd.DataFrame, text_column: str, topic_labels: Dict[int, str]) -> None:
    """
    🎯 ANALYSIS: Führt benutzerdefinierte Analyse durch
    
    Args:
        df: DataFrame mit Kommentar-Daten
        text_column: Name der Text-Spalte
        topic_labels: Topic-Labels Dictionary
    """
    st.write("### Benutzerdefinierte Analyse")
    st.write("Wählen Sie Ihre eigenen Kriterien für eine spezifische Analyse.")
    
    effective_labels = get_effective_topic_labels(topic_labels)
    
    # Keywords-Input
    custom_search = st.text_input("Geben Sie Schlüsselwörter ein (durch Komma getrennt):")
    
    if not custom_search:
        st.info("Geben Sie Schlüsselwörter ein, um die Analyse zu starten.")
        return
    
    # Keywords verarbeiten
    custom_keywords = [kw.strip().lower() for kw in custom_search.split(",") if kw.strip()]
    
    if not custom_keywords:
        st.warning("Bitte geben Sie gültige Schlüsselwörter ein.")
        return
    
    # Analysis durchführen
    filtered_df = filter_comments_by_keywords(df, custom_keywords)
    
    if filtered_df.empty:
        st.warning(f"Keine Kommentare zu '{custom_search}' gefunden.")
        return
    
    # Ergebnis erstellen
    result = create_analysis_result("Custom", custom_keywords, filtered_df, effective_labels)
    
    # UI rendern
    st.write(f"Gefundene Kommentare: {result.total_comments}")
    
    render_emotion_distribution_chart(result)
    render_topic_distribution_chart(result)
    render_emotion_category_metrics(result)
    render_example_comments(result, text_column, effective_labels)

# ==========================================
# 🎯 MAIN API FUNCTIONS (Backward Compatible)
# ==========================================

def display_special_analysis(df: pd.DataFrame, text_column: str, topic_labels: Dict[int, str]) -> None:
    """
    🎯 MODERNISIERT: Zeigt die speziellen Analysen für Bildungs- und Gender-Themen an
    
    Args:
        df: DataFrame mit Kommentar-Daten
        text_column: Name der Spalte mit den Texten
        topic_labels: Dictionary mit Themen-Labels
    """
    st.subheader("Spezielle Analysen zu bestimmten Themen")
    
    # Prüfe verfügbare Daten
    analysis_info = TopicAnalysisInfo.from_dataframe(df, topic_labels)
    
    if not analysis_info.has_topics or not analysis_info.has_emotions:
        st.warning("Spezialanalysen erfordern sowohl Topic- als auch Emotionsdaten, die nicht verfügbar sind.")
        
        missing_data = []
        if not analysis_info.has_topics:
            missing_data.append("Topic-Daten")
        if not analysis_info.has_emotions:
            missing_data.append("Emotions-Daten")
        
        st.write(f"Fehlende Daten: {', '.join(missing_data)}")
        return
    
    # Tab-basierte UI
    analysis_tabs = st.tabs(["Bildungsthemen", "Gender-Themen", "Benutzerdefinierte Analyse"])
    
    with analysis_tabs[0]:
        perform_education_analysis(df, text_column, analysis_info.topic_labels)
    
    with analysis_tabs[1]:
        perform_gender_analysis(df, text_column, analysis_info.topic_labels)
    
    with analysis_tabs[2]:
        perform_custom_analysis(df, text_column, analysis_info.topic_labels)

# Legacy Functions for backward compatibility
def display_education_analysis(df: pd.DataFrame, text_column: str, topic_labels_for_analysis: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """🎯 LEGACY: Backward compatible function"""
    perform_education_analysis(df, text_column, topic_labels_for_analysis)

def display_gender_analysis(df: pd.DataFrame, text_column: str, topic_labels_for_analysis: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """🎯 LEGACY: Backward compatible function"""
    perform_gender_analysis(df, text_column, topic_labels_for_analysis)

def display_custom_analysis(df: pd.DataFrame, text_column: str, topic_labels_for_analysis: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """🎯 LEGACY: Backward compatible function"""
    perform_custom_analysis(df, text_column, topic_labels_for_analysis)

# ==========================================
# 📊 EXPORT
# ==========================================

__all__ = [
    # Main API Functions (Backward Compatible)
    'display_special_analysis',
    'display_education_analysis',
    'display_gender_analysis', 
    'display_custom_analysis',
    
    # New Classes and Functions
    'AnalysisKeywords',
    'AnalysisResult',
    'TopicAnalysisInfo',
    'EmotionCategory',
    'filter_comments_by_keywords',
    'filter_comments_by_topics',
    'create_analysis_result',
    
    # Constants
    'DEFAULT_EDUCATION_KEYWORDS',
    'DEFAULT_GENDER_KEYWORDS',
    'EMOTION_COLORS',
    'EMOTION_MAPPING'
]