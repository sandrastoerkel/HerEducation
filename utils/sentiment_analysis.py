import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from collections import Counter
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass

# ==========================================
# 📊 KONSTANTEN (statt Magic Numbers)
# ==========================================

# Text Processing Konstanten
DEFAULT_CHUNK_SIZE: int = 512
MIN_TEXT_LENGTH: int = 0
MAX_TEXT_LENGTH: int = 100
DEFAULT_MIN_LENGTH: int = 0

# Confidence Analysis
DEFAULT_MIN_CONFIDENCE: float = 0.5
MIN_CONFIDENCE_RANGE: float = 0.0
MAX_CONFIDENCE_RANGE: float = 1.0

# Validation
MIN_VALIDATION_SAMPLES: int = 3
MAX_VALIDATION_SAMPLES: int = 10
DEFAULT_VALIDATION_SAMPLES: int = 5

# UI Configuration
CHART_HEIGHT: int = 500
HISTOGRAM_BINS: int = 20
MAX_EXAMPLES_PER_SENTIMENT: int = 3

# Sentiment Labels
SENTIMENT_LABELS: List[str] = ['positive', 'neutral', 'negative']

# Sentiment Colors
SENTIMENT_COLORS: Dict[str, str] = {
    'positive': '#4CAF50',  # Green
    'neutral': '#9E9E9E',   # Gray
    'negative': '#F44336'   # Red
}

# Fallback Values
FALLBACK_SENTIMENT: str = "neutral"
FALLBACK_CONFIDENCE: float = 0.0

# ==========================================
# 🎛️ DATA CLASSES
# ==========================================

@dataclass
class SentimentAnalysisConfig:
    """Konfiguration für Sentiment-Analyse"""
    min_comment_length: int = DEFAULT_MIN_LENGTH
    chunk_size: int = DEFAULT_CHUNK_SIZE
    min_confidence_threshold: float = DEFAULT_MIN_CONFIDENCE
    validation_samples: int = DEFAULT_VALIDATION_SAMPLES

@dataclass
class SentimentResult:
    """Ergebnis einer einzelnen Sentiment-Analyse"""
    sentiment: str
    confidence: float
    text_length: int
    
    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= DEFAULT_MIN_CONFIDENCE

@dataclass
class SentimentStatistics:
    """Statistiken für Sentiment-Analyse"""
    total_comments: int
    positive_count: int
    neutral_count: int  
    negative_count: int
    average_confidence: float
    high_confidence_count: int
    
    @property
    def positive_percentage(self) -> float:
        return self.positive_count / self.total_comments if self.total_comments > 0 else 0
    
    @property
    def neutral_percentage(self) -> float:
        return self.neutral_count / self.total_comments if self.total_comments > 0 else 0
    
    @property
    def negative_percentage(self) -> float:
        return self.negative_count / self.total_comments if self.total_comments > 0 else 0
    
    @property
    def high_confidence_percentage(self) -> float:
        return self.high_confidence_count / self.total_comments if self.total_comments > 0 else 0

@dataclass
class ValidationResult:
    """Ergebnis der User-Validation"""
    total_samples: int
    matches: int
    accuracy: float
    agreement_details: List[Dict[str, Any]]
    
    @property
    def accuracy_percentage(self) -> str:
        return f"{self.accuracy:.0%}"

# ==========================================
# 🔬 BUSINESS LOGIC FUNCTIONS
# ==========================================

def analyze_text_sentiment(text: str, sentiment_pipeline: Any, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """
    🎯 MODERNISIERT: Analysiert Sentiment eines Textes mit Chunk-basiertem Ansatz
    
    Args:
        text: Zu analysierender Text
        sentiment_pipeline: Sentiment-Analyse-Pipeline
        chunk_size: Größe der Text-Chunks
        
    Returns:
        Sentiment-Label als String
    """
    if not _validate_text_input(text):
        return FALLBACK_SENTIMENT
    
    text_str = str(text)
    chunks = _create_text_chunks(text_str, chunk_size)
    
    if not chunks:
        return FALLBACK_SENTIMENT
    
    try:
        sentiments = []
        for chunk in chunks:
            result = sentiment_pipeline(chunk)
            if result and len(result) > 0 and 'label' in result[0]:
                sentiments.append(result[0]['label'])
        
        if not sentiments:
            return FALLBACK_SENTIMENT
            
        # Verwende den häufigsten Sentiment
        most_common = Counter(sentiments).most_common(1)[0][0]
        return most_common
        
    except Exception as e:
        # Logging könnte hier hinzugefügt werden
        return FALLBACK_SENTIMENT

def calculate_text_confidence(text: str, sentiment_pipeline: Any, chunk_size: int = DEFAULT_CHUNK_SIZE) -> float:
    """
    🎯 MODERNISIERT: Berechnet Konfidenz des Sentiment-Modells
    
    Args:
        text: Zu analysierender Text
        sentiment_pipeline: Sentiment-Analyse-Pipeline
        chunk_size: Größe der Text-Chunks
        
    Returns:
        Durchschnittliche Konfidenz als Float
    """
    if not _validate_text_input(text):
        return FALLBACK_CONFIDENCE
    
    text_str = str(text)
    chunks = _create_text_chunks(text_str, chunk_size)
    
    if not chunks:
        return FALLBACK_CONFIDENCE
    
    try:
        scores = []
        for chunk in chunks:
            result = sentiment_pipeline(chunk)
            if result and len(result) > 0 and 'score' in result[0]:
                scores.append(result[0]['score'])
        
        if not scores:
            return FALLBACK_CONFIDENCE
            
        return sum(scores) / len(scores)
        
    except Exception as e:
        # Logging könnte hier hinzugefügt werden
        return FALLBACK_CONFIDENCE

def _validate_text_input(text: Any) -> bool:
    """Validiert Text-Input"""
    return not (pd.isna(text) or text is None or text == "")

def _create_text_chunks(text: str, chunk_size: int) -> List[str]:
    """Erstellt Text-Chunks"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def perform_sentiment_analysis(df: pd.DataFrame, text_column: str, sentiment_pipeline: Any, config: SentimentAnalysisConfig) -> pd.DataFrame:
    """
    🎯 BUSINESS: Führt Sentiment-Analyse für alle Kommentare durch
    
    Args:
        df: DataFrame mit Kommentaren
        text_column: Name der Text-Spalte
        sentiment_pipeline: Sentiment-Pipeline
        config: Analyse-Konfiguration
        
    Returns:
        DataFrame mit Sentiment-Informationen
    """
    # Daten vorbereiten
    df = _prepare_text_data(df, text_column, config.min_comment_length)
    
    if len(df) == 0:
        st.warning("Nach Filterung sind keine Kommentare übrig.")
        st.stop()
    
    # Progress tracking
    progress_bar = st.progress(0)
    total_rows = len(df)
    
    # Sentiment-Analyse durchführen
    results = []
    for i, text in enumerate(df[text_column]):
        sentiment = analyze_text_sentiment(text, sentiment_pipeline, config.chunk_size)
        confidence = calculate_text_confidence(text, sentiment_pipeline, config.chunk_size)
        
        results.append(SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            text_length=len(str(text))
        ))
        
        progress_bar.progress((i+1)/total_rows)
    
    # Ergebnisse in DataFrame integrieren
    df['sentiment'] = [r.sentiment for r in results]
    df['confidence'] = [r.confidence for r in results]
    df['text_length'] = [r.text_length for r in results]
    
    # Index zurücksetzen für sicheren Zugriff
    df = df.reset_index(drop=True)
    
    return df

def _prepare_text_data(df: pd.DataFrame, text_column: str, min_length: int) -> pd.DataFrame:
    """Bereitet Text-Daten vor"""
    # Text-Daten bereinigen
    df[text_column] = df[text_column].fillna("").astype(str)
    
    # Nach Länge filtern
    df_filtered = df[df[text_column].str.len() > min_length].copy()
    
    return df_filtered

def calculate_sentiment_statistics(df: pd.DataFrame, min_confidence: float = DEFAULT_MIN_CONFIDENCE) -> SentimentStatistics:
    """
    🎯 BUSINESS: Berechnet Sentiment-Statistiken
    
    Args:
        df: DataFrame mit Sentiment-Daten
        min_confidence: Mindest-Konfidenz für "hohe Konfidenz"
        
    Returns:
        SentimentStatistics Objekt
    """
    sentiment_counts = df['sentiment'].value_counts()
    
    return SentimentStatistics(
        total_comments=len(df),
        positive_count=sentiment_counts.get('positive', 0),
        neutral_count=sentiment_counts.get('neutral', 0),
        negative_count=sentiment_counts.get('negative', 0),
        average_confidence=df['confidence'].mean(),
        high_confidence_count=len(df[df['confidence'] >= min_confidence])
    )

def filter_by_confidence(df: pd.DataFrame, min_confidence: float) -> pd.DataFrame:
    """
    🎯 BUSINESS: Filtert DataFrame nach Mindest-Konfidenz
    """
    return df[df['confidence'] >= min_confidence].copy()

def get_sentiment_examples(df: pd.DataFrame, sentiment_type: str, max_examples: int = MAX_EXAMPLES_PER_SENTIMENT) -> pd.DataFrame:
    """
    🎯 BUSINESS: Holt Beispiele für einen Sentiment-Typ
    """
    sentiment_examples = df[df['sentiment'] == sentiment_type]
    if sentiment_examples.empty:
        return pd.DataFrame()
    
    # Sortiere nach Konfidenz und nimm die besten Beispiele
    return sentiment_examples.sort_values(by='confidence', ascending=False).head(max_examples)

# ==========================================
# 🎨 UI FUNCTIONS (Streamlit Components)
# ==========================================

def render_analysis_config_ui() -> SentimentAnalysisConfig:
    """
    🎯 UI: Rendert Analyse-Konfiguration
    
    Returns:
        SentimentAnalysisConfig Objekt
    """
    st.subheader("Analyse der Kommentare")
    
    min_length = st.slider(
        "Minimale Kommentarlänge (Zeichen)", 
        MIN_TEXT_LENGTH, 
        MAX_TEXT_LENGTH, 
        DEFAULT_MIN_LENGTH
    )
    
    return SentimentAnalysisConfig(min_comment_length=min_length)

def render_data_preview(df: pd.DataFrame, text_column: str) -> None:
    """
    🎯 UI: Zeigt Daten-Vorschau
    """
    st.write("Beispiele für extrahierte Kommentare:")
    
    preview_columns = [text_column]
    if 'original_line' in df.columns:
        preview_columns.append('original_line')
    
    st.dataframe(df.head(5)[preview_columns])

def render_sentiment_distribution_chart(sentiment_counts: pd.Series) -> None:
    """
    🎯 UI: Rendert Sentiment-Verteilungs-Chart mit Plotly
    """
    fig = px.bar(
        x=sentiment_counts.index,
        y=sentiment_counts.values,
        color=sentiment_counts.index,
        color_discrete_map=SENTIMENT_COLORS,
        labels={'x': 'Sentiment', 'y': 'Anzahl'},
        title='Sentiment-Verteilung'
    )
    
    fig.update_layout(
        xaxis_title='Sentiment',
        yaxis_title='Anzahl',
        showlegend=False,
        height=CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="sentiment_distribution_chart")

def render_confidence_histogram(confidence_data: pd.Series) -> None:
    """
    🎯 UI: Rendert Konfidenz-Histogramm mit Plotly
    """
    fig = px.histogram(
        x=confidence_data,
        nbins=HISTOGRAM_BINS,
        labels={'x': 'Konfidenz', 'y': 'Anzahl'},
        title='Verteilung der Modell-Konfidenz'
    )
    
    fig.update_layout(
        xaxis_title='Konfidenz',
        yaxis_title='Anzahl',
        height=CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="confidence_histogram_chart")

def render_sentiment_statistics(stats: SentimentStatistics) -> None:
    """
    🎯 UI: Rendert Sentiment-Statistiken
    """
    st.write(f"Durchschnittliche Modell-Konfidenz: {stats.average_confidence:.2f}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Positive Kommentare", stats.positive_count, f"{stats.positive_percentage:.1%}")
    col2.metric("Neutrale Kommentare", stats.neutral_count, f"{stats.neutral_percentage:.1%}")
    col3.metric("Negative Kommentare", stats.negative_count, f"{stats.negative_percentage:.1%}")

def render_confidence_filter_ui(df: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """
    🎯 UI: Rendert Konfidenz-Filter UI
    
    Returns:
        Tuple von (min_confidence, filtered_dataframe)
    """
    st.subheader("Filtern nach Konfidenz")
    
    min_confidence = st.slider(
        "Minimale Konfidenz", 
        MIN_CONFIDENCE_RANGE, 
        MAX_CONFIDENCE_RANGE, 
        DEFAULT_MIN_CONFIDENCE
    )
    
    high_confidence_df = filter_by_confidence(df, min_confidence)
    
    st.write(f"**{len(high_confidence_df)} von {len(df)}** Kommentaren haben eine Konfidenz ≥ {min_confidence:.2f}")
    
    return min_confidence, high_confidence_df

def render_high_confidence_sentiment_chart(high_confidence_df: pd.DataFrame) -> None:
    """
    🎯 UI: Rendert Sentiment-Chart für hohe Konfidenz
    """
    if len(high_confidence_df) == 0:
        st.warning("Keine Kommentare mit ausreichender Konfidenz gefunden.")
        return
    
    st.write("### Sentiment-Verteilung (nur hohe Konfidenz)")
    
    sentiment_counts = high_confidence_df['sentiment'].value_counts()
    
    fig = px.bar(
        x=sentiment_counts.index,
        y=sentiment_counts.values,
        color=sentiment_counts.index,
        color_discrete_map=SENTIMENT_COLORS,
        labels={'x': 'Sentiment', 'y': 'Anzahl'},
        title='Sentiment-Verteilung (Hohe Konfidenz)'
    )
    
    fig.update_layout(
        xaxis_title='Sentiment',
        yaxis_title='Anzahl',
        showlegend=False,
        height=CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="high_confidence_sentiment_chart")

def render_sentiment_examples(df: pd.DataFrame, text_column: str) -> None:
    """
    🎯 UI: Rendert Beispiele für jede Sentiment-Kategorie
    """
    st.subheader("Beispiele für jede Sentiment-Kategorie")
    
    for sentiment_type in SENTIMENT_LABELS:
        examples = get_sentiment_examples(df, sentiment_type)
        
        if not examples.empty:
            st.write(f"### Beispiele für {sentiment_type} Kommentare:")
            
            for i, (_, example) in enumerate(examples.iterrows()):
                st.write(f"**{i+1}.** {example[text_column]} *(Konfidenz: {example['confidence']:.2f})*")
                
                if 'original_line' in example.index:
                    st.write(f"   *(Originale Zeile: {example['original_line']})*")

# ==========================================
# 🧪 VALIDATION FUNCTIONS
# ==========================================

def initialize_validation_session(df: pd.DataFrame, num_samples: int) -> None:
    """
    🎯 BUSINESS: Initialisiert Validierungs-Session
    """
    if len(df) == 0:
        st.warning("Keine Kommentare für die Stichprobe verfügbar.")
        return
    
    sample_size = min(num_samples, len(df))
    sample_indices = random.sample(range(len(df)), sample_size)
    
    st.session_state.random_indices = sample_indices
    st.session_state.user_ratings = {}

def render_validation_ui(df: pd.DataFrame, text_column: str) -> None:
    """
    🎯 UI: Rendert Validierungs-Interface
    """
    st.subheader("Modell-Überprüfung")
    st.write("Hier können Sie die Qualität des Modells überprüfen, indem Sie zufällige Kommentare manuell bewerten.")
    
    # Anzahl der Stichproben
    num_samples = st.slider(
        "Anzahl der Stichproben", 
        MIN_VALIDATION_SAMPLES, 
        MAX_VALIDATION_SAMPLES, 
        DEFAULT_VALIDATION_SAMPLES
    )
    
    # Button für zufällige Auswahl
    if st.button("Zufällige Kommentare zur Überprüfung auswählen"):
        initialize_validation_session(df, num_samples)
    
    # Validierungs-Formular anzeigen
    if hasattr(st.session_state, 'random_indices'):
        validation_result = render_validation_form(df, text_column)
        
        if validation_result:
            render_validation_results(validation_result)

def render_validation_form(df: pd.DataFrame, text_column: str) -> Optional[ValidationResult]:
    """
    🎯 UI: Rendert Validierungs-Formular
    
    Returns:
        ValidationResult oder None
    """
    with st.form("validation_form"):
        valid_samples = 0
        
        for i, idx in enumerate(st.session_state.random_indices):
            if idx < len(df):
                valid_samples += 1
                comment = df.iloc[idx][text_column]
                model_sentiment = df.iloc[idx]['sentiment']
                model_confidence = df.iloc[idx]['confidence']
                
                st.write(f"**Kommentar {valid_samples}:** {comment}")
                st.write(f"*Modell-Sentiment:* {model_sentiment} (Konfidenz: {model_confidence:.2f})")
                
                user_sentiment = st.radio(
                    f"Ihr Sentiment für Kommentar {valid_samples}:",
                    SENTIMENT_LABELS,
                    key=f"sentiment_{i}"
                )
                st.session_state.user_ratings[idx] = user_sentiment
                st.markdown("---")
        
        submit_button = st.form_submit_button("Bewertungen abschicken")
        
        if submit_button and valid_samples > 0:
            return calculate_validation_results(df, text_column)
    
    return None

def calculate_validation_results(df: pd.DataFrame, text_column: str) -> ValidationResult:
    """
    🎯 BUSINESS: Berechnet Validierungs-Ergebnisse
    """
    matches = 0
    agreement_details = []
    
    for idx, user_rating in st.session_state.user_ratings.items():
        if idx < len(df):
            model_sentiment = df.iloc[idx]['sentiment']
            is_match = user_rating == model_sentiment
            
            if is_match:
                matches += 1
            
            agreement_details.append({
                'Kommentar': df.iloc[idx][text_column],
                'Modell-Sentiment': model_sentiment,
                'Ihre Bewertung': user_rating,
                'Übereinstimmung': is_match
            })
    
    total_ratings = len(st.session_state.user_ratings)
    accuracy = matches / total_ratings if total_ratings > 0 else 0
    
    return ValidationResult(
        total_samples=total_ratings,
        matches=matches,
        accuracy=accuracy,
        agreement_details=agreement_details
    )

def render_validation_results(result: ValidationResult) -> None:
    """
    🎯 UI: Rendert Validierungs-Ergebnisse
    """
    st.success(f"Übereinstimmung: {result.matches} von {result.total_samples} ({result.accuracy_percentage})")
    
    # Detaillierte Analyse
    if result.agreement_details:
        st.write("### Detaillierte Übereinstimmungsanalyse")
        agreement_df = pd.DataFrame(result.agreement_details)
        st.dataframe(agreement_df)

# ==========================================
# 🎯 MAIN API FUNCTIONS (Backward Compatible)
# ==========================================

def split_and_analyze(text: str, sentiment_pipeline: Any, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """
    🎯 LEGACY: Backward compatible function
    Teilt langen Text in Chunks und analysiert das Sentiment
    """
    return analyze_text_sentiment(text, sentiment_pipeline, chunk_size)

def calculate_confidence(text: str, sentiment_pipeline: Any, chunk_size: int = DEFAULT_CHUNK_SIZE) -> float:
    """
    🎯 LEGACY: Backward compatible function  
    Berechnet die Konfidenz des Sentiment-Modells
    """
    return calculate_text_confidence(text, sentiment_pipeline, chunk_size)

def analyze_sentiment(df: pd.DataFrame, text_column: str, sentiment_pipeline: Any) -> pd.DataFrame:
    """
    🎯 MODERNISIERT: Führt die Sentiment-Analyse für alle Kommentare durch
    
    Args:
        df: DataFrame mit den Kommentaren
        text_column: Name der Spalte mit den Texten
        sentiment_pipeline: Sentiment-Analyse-Pipeline
        
    Returns:
        DataFrame mit Sentiment-Informationen
    """
    
    # === UI: Konfiguration ===
    config = render_analysis_config_ui()
    
    # === UI: Daten-Vorschau ===
    render_data_preview(df, text_column)
    
    # === BUSINESS: Sentiment-Analyse ===
    df_analyzed = perform_sentiment_analysis(df, text_column, sentiment_pipeline, config)
    
    return df_analyzed

def display_sentiment_results(df: pd.DataFrame, text_column: str) -> None:
    """
    🎯 MODERNISIERT: Zeigt die Ergebnisse der Sentiment-Analyse an
    
    Args:
        df: DataFrame mit Sentiment-Informationen
        text_column: Name der Spalte mit den Texten
    """
    st.subheader("Analyseergebnisse")
    
    # === BUSINESS: Statistiken berechnen ===
    stats = calculate_sentiment_statistics(df)
    
    # === UI: Statistiken anzeigen ===
    render_sentiment_statistics(stats)
    
    # === UI: Sentiment-Verteilung ===
    st.write("### Sentiment-Verteilung")
    sentiment_counts = df['sentiment'].value_counts()
    render_sentiment_distribution_chart(sentiment_counts)
    
    # === UI: Konfidenz-Histogramm ===
    st.write("### Verteilung der Modell-Konfidenz")
    render_confidence_histogram(df['confidence'])
    
    # === UI: Validierung ===
    render_validation_ui(df, text_column)
    
    # === UI: Konfidenz-Filter ===
    min_confidence, high_confidence_df = render_confidence_filter_ui(df)
    
    # === UI: Hohe Konfidenz Chart ===
    render_high_confidence_sentiment_chart(high_confidence_df)
    
    # === UI: Beispiele ===
    render_sentiment_examples(df, text_column)

# ==========================================
# 📊 EXPORT
# ==========================================

__all__ = [
    # Main API Functions (Backward Compatible)
    'split_and_analyze',
    'calculate_confidence', 
    'analyze_sentiment',
    'display_sentiment_results',
    
    # New Classes and Functions
    'SentimentAnalysisConfig',
    'SentimentResult',
    'SentimentStatistics',
    'ValidationResult',
    'calculate_sentiment_statistics',
    'filter_by_confidence',
    
    # Constants
    'DEFAULT_CHUNK_SIZE',
    'SENTIMENT_LABELS',
    'SENTIMENT_COLORS'
]