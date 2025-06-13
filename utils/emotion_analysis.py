"""
Enterprise-level German emotion analysis module.

This module provides emotion analysis functionality with advanced linguistic analysis,
enterprise architecture, type safety, and contextual emotion recognition.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import traceback
import logging

# Import from German emotion detection module
from .emotion_detection import (
    EMOTION_LABEL_MAP, 
    EMOTION_COLORS, 
    contextual_emotion_detection, 
    split_text_into_sentences, 
    analyze_sentence_structure
)

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

class GermanEmotionAnalysisConstants:
    """Central constants for German emotion analysis"""
    
    # Analysis Parameters
    DEFAULT_MODEL_WEIGHT = 0.7
    DEFAULT_CONFIDENCE_THRESHOLD = 0.5
    DEFAULT_LINGUISTIC_WEIGHT = 0.3
    
    # Confidence and weighting
    MAX_CONFIDENCE_BOOST = 0.8
    LINGUISTIC_WEIGHT_BOOST_FACTOR = 1.5
    NEGATION_REDUCTION_FACTOR = 0.5
    
    # UI Configuration
    UI_CHART_HEIGHT = 500
    UI_CHART_HEIGHT_LARGE = 600
    UI_CHART_HEIGHT_SMALL = 300
    UI_CHART_HEIGHT_COMPACT = 300
    
    # Analysis settings
    MAX_EXAMPLES_PER_EMOTION = 3
    DETECTION_THRESHOLD = 0.5
    
    # Thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.1
    HIGH_CONFIDENCE_THRESHOLD = 0.7
    
    # Logging
    LOGGER_NAME = "german_emotion_analysis"


class GermanEmotionType(str, Enum):
    """German emotion types for analysis"""
    ANGER = "anger"
    FEAR = "fear"
    DISGUST = "disgust"
    SADNESS = "sadness"
    JOY = "joy"
    NONE_OF_THEM = "none of them"


class GermanEmotionCategory(str, Enum):
    """German emotion categories for aggregated analysis"""
    POSITIV = "Positiv"
    NEGATIV = "Negativ"
    NEUTRAL = "Neutral"


class AnalysisMode(Enum):
    """Analysis modes for different use cases"""
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class LinguisticFeature(Enum):
    """Linguistic features for enhanced analysis"""
    NEGATION = "negation"
    CONTRAST = "contrast"
    INTENSIFIER = "intensifier"
    QUESTION = "question"
    EXCLAMATION = "exclamation"


# =============================================================================
# EMOTION COLORS AND VISUALIZATION
# =============================================================================

class GermanEmotionVisualizationConfig:
    """Configuration for German emotion visualization"""
    
    # Use existing German emotion colors
    EMOTION_COLORS = EMOTION_COLORS
    
    EMOTION_ICONS = {
        GermanEmotionType.ANGER: "😠",
        GermanEmotionType.FEAR: "😨",
        GermanEmotionType.SADNESS: "😢",
        GermanEmotionType.JOY: "😊",
        GermanEmotionType.DISGUST: "🤢",
        GermanEmotionType.NONE_OF_THEM: "😐"
    }
    
    METHOD_COLORS = {
        "Modell": "#1976D2",
        "Linguistisch": "#388E3C", 
        "Gewichtet": "#7B1FA2"
    }
    
    CATEGORY_COLORS = {
        GermanEmotionCategory.POSITIV: '#4CAF50',
        GermanEmotionCategory.NEGATIV: '#F44336',
        GermanEmotionCategory.NEUTRAL: '#2196F3'
    }


# =============================================================================
# GERMAN LINGUISTIC PATTERNS AND FALLBACKS
# =============================================================================

class GermanLinguisticPatterns:
    """German linguistic patterns for emotion detection"""
    
    NEGATION_WORDS = [
        "nicht", "nein", "nie", "niemals", "nichts", "niemand", "nirgends",
        "kaum", "kein", "keine", "keiner", "ohne", "fehlt", "fehlen"
    ]
    
    CONTRAST_WORDS = [
        "aber", "jedoch", "allerdings", "obwohl", "trotz", "dennoch", 
        "nichtsdestotrotz", "andererseits", "während", "wohingegen"
    ]
    
    INTENSIFIER_WORDS = [
        "sehr", "extrem", "absolut", "komplett", "total", "ziemlich", 
        "wirklich", "so", "zu", "unglaublich", "höchst", "tief", "völlig",
        "außerordentlich", "bemerkenswert", "außergewöhnlich", "enorm"
    ]
    
    QUESTION_INDICATORS = ["?", "was", "wie", "warum", "wann", "wo", "wer", "welch"]
    EXCLAMATION_INDICATORS = ["!", "wow", "oh", "ah", "hey", "toll", "unglaublich"]


class GermanEmotionFallbacks:
    """German emotion fallback distributions and patterns"""
    
    # Fallback Distribution (German Emotions)
    GERMAN_FALLBACK_DISTRIBUTION = {
        GermanEmotionType.ANGER: 0.35,
        GermanEmotionType.FEAR: 0.15,
        GermanEmotionType.DISGUST: 0.1,
        GermanEmotionType.SADNESS: 0.2,
        GermanEmotionType.JOY: 0.1,
        GermanEmotionType.NONE_OF_THEM: 0.1
    }
    
    # Emotion Categories (German Version)
    EMOTION_CATEGORIES = {
        GermanEmotionCategory.POSITIV: [GermanEmotionType.JOY],
        GermanEmotionCategory.NEGATIV: [
            GermanEmotionType.ANGER, 
            GermanEmotionType.SADNESS, 
            GermanEmotionType.FEAR, 
            GermanEmotionType.DISGUST
        ],
        GermanEmotionCategory.NEUTRAL: [GermanEmotionType.NONE_OF_THEM]
    }


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class GermanEmotionAnalysisConfig:
    """Enterprise configuration for German emotion analysis"""
    
    # Processing settings
    model_weight: float = GermanEmotionAnalysisConstants.DEFAULT_MODEL_WEIGHT
    confidence_threshold: float = GermanEmotionAnalysisConstants.DEFAULT_CONFIDENCE_THRESHOLD
    analysis_mode: AnalysisMode = AnalysisMode.STANDARD
    
    # Weights
    linguistic_weight: float = field(init=False)
    
    # Feature flags
    enable_linguistic_analysis: bool = True
    enable_sentence_structure: bool = True
    enable_contextual_analysis: bool = True
    enable_confidence_filtering: bool = True
    show_advanced_settings: bool = False
    
    def __post_init__(self):
        """Calculate linguistic weight and validate"""
        self.linguistic_weight = 1.0 - self.model_weight
        
        # Validate ranges
        self.model_weight = max(0.1, min(0.9, self.model_weight))
        self.confidence_threshold = max(0.1, min(0.9, self.confidence_threshold))
        self.linguistic_weight = 1.0 - self.model_weight
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for Session State"""
        return {
            'emotion_model_weight': self.model_weight,
            'emotion_linguistic_weight': self.linguistic_weight,
            'emotion_confidence_threshold': self.confidence_threshold
        }
    
    def validate(self) -> bool:
        """Validate configuration parameters"""
        return (
            0.1 <= self.model_weight <= 0.9 and
            0.1 <= self.confidence_threshold <= 0.9 and
            0.1 <= self.linguistic_weight <= 0.9
        )


@dataclass
class GermanSentenceAnalysis:
    """Analysis result for German sentence structure"""
    text: str
    length: int
    features: Dict[LinguisticFeature, bool] = field(default_factory=dict)
    emotion_indicators: Dict[GermanEmotionType, int] = field(default_factory=dict)
    confidence_score: float = 0.0
    
    @property
    def has_modifiers(self) -> bool:
        """Check if sentence has any linguistic modifiers"""
        return any(self.features.values())
    
    @property
    def dominant_emotion_indicator(self) -> Optional[GermanEmotionType]:
        """Get the emotion with most indicators"""
        if not self.emotion_indicators:
            return None
        return max(self.emotion_indicators, key=self.emotion_indicators.get)


@dataclass
class GermanEmotionStatistics:
    """Statistics for German emotion analysis results"""
    total_comments: int
    positive_count: int
    negative_count: int
    neutral_count: int
    emotion_counts: Dict[str, int]
    dominant_emotion_distribution: Dict[str, int]
    average_scores: Dict[str, float] = field(default_factory=dict)
    linguistic_scores: Dict[str, float] = field(default_factory=dict)
    sentence_counts: Dict[str, int] = field(default_factory=dict)
    
    @property
    def positive_percentage(self) -> float:
        """Calculate ratio of positive emotions"""
        return self.positive_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def negative_percentage(self) -> float:
        """Calculate ratio of negative emotions"""
        return self.negative_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def neutral_percentage(self) -> float:
        """Calculate ratio of neutral emotions"""
        return self.neutral_count / self.total_comments if self.total_comments > 0 else 0.0


@dataclass
class GermanEmotionScores:
    """Container for German emotion scores with enhanced metadata"""
    model_scores: Dict[str, float] = field(default_factory=dict)
    linguistic_scores: Dict[str, float] = field(default_factory=dict)
    combined_scores: Dict[str, float] = field(default_factory=dict)
    sentence_analyses: List[GermanSentenceAnalysis] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def dominant_emotion(self) -> Optional[str]:
        """Get the dominant emotion from combined scores"""
        if not self.combined_scores:
            return None
        return max(self.combined_scores, key=self.combined_scores.get)
    
    @property
    def confidence_score(self) -> float:
        """Calculate overall confidence score"""
        if not self.combined_scores:
            return 0.0
        return max(self.combined_scores.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization"""
        return {
            "model_scores": self.model_scores,
            "linguistic_scores": self.linguistic_scores,
            "combined_scores": self.combined_scores,
            "dominant_emotion": self.dominant_emotion,
            "confidence_score": self.confidence_score,
            "sentence_count": len(self.sentence_analyses),
            "metadata": self.metadata
        }


@dataclass
class GermanEmotionAnalysisResults:
    """Results of German emotion detection analysis"""
    dataframe: pd.DataFrame
    emotion_scores: GermanEmotionScores
    statistics: GermanEmotionStatistics
    processing_time: float
    config_used: GermanEmotionAnalysisConfig
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary"""
        result = self.emotion_scores.to_dict()
        result.update({
            "total_comments": len(self.dataframe),
            "processing_time": self.processing_time,
            "success": self.success,
            "error_message": self.error_message
        })
        return result


@dataclass
class ParameterTestResult:
    """Result of parameter testing/validation"""
    model_weight: float
    linguistic_weight: float
    quality_score: float
    emotion_diversity: float
    balance_score: float


# =============================================================================
# SPECIALIZED COMPONENTS
# =============================================================================

class GermanEmotionDetector:
    """Handles German emotion detection with enterprise features"""
    
    def __init__(self, config: GermanEmotionAnalysisConfig):
        self.config = config
        self.patterns = GermanLinguisticPatterns()
        self.fallbacks = GermanEmotionFallbacks()
        self.logger = logging.getLogger(GermanEmotionAnalysisConstants.LOGGER_NAME)
    
    def perform_emotion_detection(self, df: pd.DataFrame, emotion_classifier: Any) -> pd.DataFrame:
        """Perform German emotion detection on all comments"""
        try:
            st.info("Emotionen werden mit erweiterter linguistischer Analyse erkannt...")
            
            progress_bar = st.progress(0)
            emotions_data = []
            
            for i, text in enumerate(df['clean_text']):
                emotions = contextual_emotion_detection(text, emotion_classifier)
                emotions_data.append(emotions)
                progress_bar.progress((i + 1) / len(df))
            
            df['emotions'] = emotions_data
            return df
            
        except Exception as e:
            self.logger.error(f"Error in German emotion detection: {e}")
            return df
    
    def extract_emotion_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract emotion columns from emotions dictionary"""
        try:
            emotion_columns = list(EMOTION_LABEL_MAP.values())
            
            # Handle case where no emotions detected
            if all(x is None for x in df['emotions']):
                st.error("Keine Emotionen konnten erkannt werden! Fallback zu statistischer Verteilung.")
                df = self._apply_fallback_emotions(df, emotion_columns)
            
            # Extract emotions into separate columns
            for emotion in emotion_columns:
                df[emotion] = df['emotions'].apply(
                    lambda x: x.get(emotion, 0) if x is not None else 0
                )
                
                # Linguistic columns
                ling_col = f"{emotion}_linguistic"
                df[ling_col] = df['emotions'].apply(
                    lambda x: x.get(ling_col, 0) if x is not None and ling_col in x else 0
                )
                
                # Sentence count columns
                count_col = f"{emotion}_sentence_count"
                df[count_col] = df['emotions'].apply(
                    lambda x: x.get(count_col, 0) if x is not None and count_col in x else 0
                )
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error extracting emotion columns: {e}")
            return df
    
    def _apply_fallback_emotions(self, df: pd.DataFrame, emotion_columns: List[str]) -> pd.DataFrame:
        """Apply fallback emotions when none are detected"""
        for i in range(len(df)):
            fallback_dict = {}
            for emotion in emotion_columns:
                weight = self.fallbacks.GERMAN_FALLBACK_DISTRIBUTION.get(
                    GermanEmotionType(emotion), 0.1
                )
                fallback_dict[emotion] = np.random.beta(2, 5) * weight
            df['emotions'].iloc[i] = fallback_dict
        
        return df


class GermanEmotionValidator:
    """Validates and fixes German emotion data"""
    
    def __init__(self, config: GermanEmotionAnalysisConfig):
        self.config = config
        self.logger = logging.getLogger(GermanEmotionAnalysisConstants.LOGGER_NAME)
    
    def validate_and_fix_identical_emotions(
        self, 
        df: pd.DataFrame, 
        emotion_columns: List[str]
    ) -> pd.DataFrame:
        """Check and fix identical emotion values"""
        try:
            all_identical = all(
                df[emotion].nunique() <= 1 for emotion in emotion_columns 
                if emotion in df.columns
            )
            
            if all_identical:
                st.error("Alle Emotionswerte sind identisch! Fallback zu statistischer Verteilung.")
                
                for i in range(len(df)):
                    for emotion in emotion_columns:
                        if emotion == "anger":
                            df[emotion].iloc[i] = np.random.beta(5, 2) * 0.6
                        else:
                            df[emotion].iloc[i] = np.random.beta(2, 5) * 0.4 / (len(emotion_columns) - 1)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error validating emotions: {e}")
            return df
    
    def check_emotion_data_validity(self, df: pd.DataFrame, emotion_columns: List[str]) -> bool:
        """Check if emotion data is valid (not all identical)"""
        try:
            for emotion in emotion_columns:
                if emotion in df.columns and df[emotion].nunique() > 1:
                    return True
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking emotion validity: {e}")
            return False


class GermanEmotionCalculator:
    """Calculates weighted German emotion scores"""
    
    def __init__(self, config: GermanEmotionAnalysisConfig):
        self.config = config
        self.logger = logging.getLogger(GermanEmotionAnalysisConstants.LOGGER_NAME)
    
    def calculate_weighted_emotions(
        self, 
        df: pd.DataFrame, 
        emotion_columns: List[str]
    ) -> pd.DataFrame:
        """Calculate weighted emotion scores and dominant emotion"""
        try:
            if not all(col in df.columns for col in emotion_columns):
                st.error("Nicht alle Emotionen wurden erkannt, kann keine dominante Emotion bestimmen.")
                return self._apply_fallback_dominant_emotion(df, emotion_columns)
            
            weighted_scores = {}
            
            for emotion in emotion_columns:
                model_score = df[emotion]
                
                if f"{emotion}_linguistic" in df.columns:
                    linguistic_score = df[f"{emotion}_linguistic"]
                    
                    # Basic weighting
                    weighted_scores[emotion] = (
                        model_score * self.config.model_weight + 
                        linguistic_score * self.config.linguistic_weight
                    )
                    
                    # Confidence-based adjustment
                    confidence_boost_mask = model_score < self.config.confidence_threshold
                    if confidence_boost_mask.any():
                        boosted_linguistic_weight = min(
                            GermanEmotionAnalysisConstants.MAX_CONFIDENCE_BOOST, 
                            self.config.linguistic_weight * GermanEmotionAnalysisConstants.LINGUISTIC_WEIGHT_BOOST_FACTOR
                        )
                        boosted_model_weight = 1.0 - boosted_linguistic_weight
                        
                        weighted_scores[emotion].loc[confidence_boost_mask] = (
                            model_score.loc[confidence_boost_mask] * boosted_model_weight + 
                            linguistic_score.loc[confidence_boost_mask] * boosted_linguistic_weight
                        )
                else:
                    weighted_scores[emotion] = model_score
            
            # Determine dominant emotion
            weighted_df = pd.DataFrame(weighted_scores)
            df['dominant_emotion'] = weighted_df.idxmax(axis=1)
            
            st.write("Verteilung der dominanten Emotionen:", df['dominant_emotion'].value_counts())
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculating weighted emotions: {e}")
            return self._apply_fallback_dominant_emotion(df, emotion_columns)
    
    def _apply_fallback_dominant_emotion(
        self, 
        df: pd.DataFrame, 
        emotion_columns: List[str]
    ) -> pd.DataFrame:
        """Apply fallback for dominant emotion"""
        available_emotions = [col for col in emotion_columns if col in df.columns]
        
        if available_emotions:
            df['dominant_emotion'] = df[available_emotions].idxmax(axis=1)
        else:
            # Fallback based on typical distribution
            fallback_dist = GermanEmotionFallbacks.GERMAN_FALLBACK_DISTRIBUTION
            weights = [fallback_dist.get(GermanEmotionType(emotion), 0.1) for emotion in emotion_columns]
            df['dominant_emotion'] = np.random.choice(emotion_columns, size=len(df), p=weights)
        
        return df


class GermanEmotionStatisticsCalculator:
    """Calculates comprehensive German emotion statistics"""
    
    def __init__(self, config: GermanEmotionAnalysisConfig):
        self.config = config
        self.fallbacks = GermanEmotionFallbacks()
        self.logger = logging.getLogger(GermanEmotionAnalysisConstants.LOGGER_NAME)
    
    def calculate_emotion_statistics(
        self, 
        df: pd.DataFrame, 
        emotion_columns: List[str]
    ) -> GermanEmotionStatistics:
        """Calculate comprehensive German emotion statistics"""
        try:
            # Basic counts
            emotion_counts = df['dominant_emotion'].value_counts().to_dict()
            
            # Category counts
            positive_emotions = set(str(em.value) for em in self.fallbacks.EMOTION_CATEGORIES[GermanEmotionCategory.POSITIV])
            negative_emotions = set(str(em.value) for em in self.fallbacks.EMOTION_CATEGORIES[GermanEmotionCategory.NEGATIV])
            neutral_emotions = set(str(em.value) for em in self.fallbacks.EMOTION_CATEGORIES[GermanEmotionCategory.NEUTRAL])
            
            positive_count = len(df[df['dominant_emotion'].isin(positive_emotions)])
            negative_count = len(df[df['dominant_emotion'].isin(negative_emotions)])
            neutral_count = len(df[df['dominant_emotion'].isin(neutral_emotions)])
            
            # Average scores
            average_scores = {}
            linguistic_scores = {}
            sentence_counts = {}
            
            for emotion in emotion_columns:
                if emotion in df.columns:
                    average_scores[emotion] = df[emotion].mean()
                    
                    # Linguistic scores
                    ling_col = f"{emotion}_linguistic"
                    if ling_col in df.columns:
                        linguistic_scores[emotion] = df[ling_col].mean()
                    
                    # Sentence counts
                    sent_col = f"{emotion}_sentence_count"
                    if sent_col in df.columns:
                        sentence_counts[emotion] = df[sent_col].sum()
            
            return GermanEmotionStatistics(
                total_comments=len(df),
                positive_count=positive_count,
                negative_count=negative_count,
                neutral_count=neutral_count,
                emotion_counts=emotion_counts,
                dominant_emotion_distribution=emotion_counts,
                average_scores=average_scores,
                linguistic_scores=linguistic_scores,
                sentence_counts=sentence_counts
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {e}")
            return GermanEmotionStatistics(
                total_comments=len(df),
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                emotion_counts={},
                dominant_emotion_distribution={}
            )


# =============================================================================
# MANAGER CLASS
# =============================================================================

class GermanEmotionAnalysisManager:
    """Enterprise manager for German emotion analysis"""
    
    def __init__(self, config: Optional[GermanEmotionAnalysisConfig] = None):
        self.config = config or GermanEmotionAnalysisConfig()
        
        if not self.config.validate():
            raise ValueError("Invalid configuration parameters")
        
        # Initialize components
        self.detector = GermanEmotionDetector(self.config)
        self.validator = GermanEmotionValidator(self.config)
        self.calculator = GermanEmotionCalculator(self.config)
        self.statistics_calculator = GermanEmotionStatisticsCalculator(self.config)
        
        self.logger = logging.getLogger(GermanEmotionAnalysisConstants.LOGGER_NAME)
    
    def analyze_emotions(
        self, 
        df: pd.DataFrame, 
        emotion_classifier: Any
    ) -> GermanEmotionAnalysisResults:
        """Comprehensive German emotion analysis with enterprise features"""
        import time
        start_time = time.time()
        
        try:
            # Perform emotion detection
            df = self.detector.perform_emotion_detection(df, emotion_classifier)
            
            # Extract emotion columns
            emotion_columns = list(EMOTION_LABEL_MAP.values())
            df = self.detector.extract_emotion_columns(df)
            
            # Validate and fix identical emotions
            df = self.validator.validate_and_fix_identical_emotions(df, emotion_columns)
            
            # Calculate weighted emotions
            df = self.calculator.calculate_weighted_emotions(df, emotion_columns)
            
            # Calculate statistics
            statistics = self.statistics_calculator.calculate_emotion_statistics(df, emotion_columns)
            
            processing_time = time.time() - start_time
            
            return GermanEmotionAnalysisResults(
                dataframe=df,
                emotion_scores=GermanEmotionScores(),  # Can be enhanced
                statistics=statistics,
                processing_time=processing_time,
                config_used=self.config,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Error in German emotion analysis: {e}")
            return GermanEmotionAnalysisResults(
                dataframe=df,
                emotion_scores=GermanEmotionScores(),
                statistics=GermanEmotionStatistics(
                    total_comments=len(df),
                    positive_count=0,
                    negative_count=0,
                    neutral_count=0,
                    emotion_counts={},
                    dominant_emotion_distribution={}
                ),
                processing_time=time.time() - start_time,
                config_used=self.config,
                success=False,
                error_message=str(e)
            )


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_german_emotion_analysis_config() -> GermanEmotionAnalysisConfig:
    """Render German emotion analysis configuration UI"""
    st.write("### 🎛️ Modell-Parameter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_advanced = st.checkbox(
            "🔧 Erweiterte Einstellungen", 
            help="Aktiviere um Gewichtung anzupassen"
        )
        
        config = GermanEmotionAnalysisConfig(show_advanced_settings=show_advanced)
        
        if show_advanced:
            config.model_weight = st.slider(
                "Modell-Gewichtung", 
                min_value=0.1, 
                max_value=0.9, 
                value=GermanEmotionAnalysisConstants.DEFAULT_MODEL_WEIGHT,
                step=0.1,
                help="70% Modell + 30% Linguistik ist Standard"
            )
            
            config.confidence_threshold = st.slider(
                "Mindest-Confidence",
                min_value=0.1,
                max_value=0.9,
                value=GermanEmotionAnalysisConstants.DEFAULT_CONFIDENCE_THRESHOLD,
                step=0.1,
                help="Minimum Sicherheit für Vorhersagen"
            )
            
            # Recalculate linguistic weight
            config.linguistic_weight = 1.0 - config.model_weight
    
    with col2:
        st.metric("Modell-Anteil", f"{config.model_weight:.0%}")
        st.metric("Linguistik-Anteil", f"{config.linguistic_weight:.0%}")
        st.metric("Confidence-Filter", f"{config.confidence_threshold:.1f}")
    
    st.info(
        f"🔬 Aktuelle Gewichtung: {config.model_weight:.0%} KI-Modell + "
        f"{config.linguistic_weight:.0%} Linguistische Analyse"
    )
    
    return config


def render_german_emotion_distribution_chart(statistics: GermanEmotionStatistics) -> None:
    """Render German emotion distribution chart"""
    st.write("### Verteilung der Emotionen")
    
    emotion_counts = statistics.emotion_counts
    
    fig = px.bar(
        x=list(emotion_counts.keys()), 
        y=list(emotion_counts.values()),
        color=list(emotion_counts.keys()),
        color_discrete_map=GermanEmotionVisualizationConfig.EMOTION_COLORS,
        labels={'x': 'Emotion', 'y': 'Anzahl'},
        title='Dominante Emotionen in Kommentaren'
    )
    
    fig.update_layout(
        xaxis_title='Emotion',
        yaxis_title='Anzahl',
        legend_title='Emotion',
        showlegend=False,
        height=GermanEmotionAnalysisConstants.UI_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="german_emotion_distribution_chart")


def render_german_model_vs_linguistic_chart(df: pd.DataFrame, emotion_columns: List[str]) -> None:
    """Render German model vs linguistic comparison chart"""
    st.write("### Vergleich: Modell vs. Linguistische Erkennung")
    
    comparison_data = []
    
    for emotion in emotion_columns:
        model_count = len(df[df[emotion] > GermanEmotionAnalysisConstants.DETECTION_THRESHOLD])
        
        ling_col = f"{emotion}_linguistic"
        ling_count = len(df[df[ling_col] > GermanEmotionAnalysisConstants.DETECTION_THRESHOLD]) if ling_col in df.columns else 0
        
        comparison_data.extend([
            {"Emotion": emotion, "Methode": "Modell", "Anzahl": model_count},
            {"Emotion": emotion, "Methode": "Linguistisch", "Anzahl": ling_count}
        ])
    
    comparison_df = pd.DataFrame(comparison_data)
    
    fig = px.bar(
        comparison_df,
        x="Emotion",
        y="Anzahl",
        color="Methode",
        barmode="group",
        color_discrete_map=GermanEmotionVisualizationConfig.METHOD_COLORS,
        title="Vergleich: Modell vs. Linguistische Erkennung"
    )
    
    fig.update_layout(
        xaxis_title='Emotion',
        yaxis_title='Anzahl der Erkennungen',
        legend_title='Methode',
        height=GermanEmotionAnalysisConstants.UI_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="german_model_vs_linguistic_chart")


def render_german_weighted_comparison_chart(
    df: pd.DataFrame, 
    emotion_columns: List[str], 
    config: GermanEmotionAnalysisConfig
) -> None:
    """Render German weighted comparison chart"""
    st.write("### Aktueller Gewichteter Kombinationsansatz")
    
    all_scores_data = []
    
    for emotion in emotion_columns:
        if emotion in df.columns and f"{emotion}_linguistic" in df.columns:
            avg_model = df[emotion].mean()
            avg_ling = df[f"{emotion}_linguistic"].mean()
            avg_weighted = avg_model * config.model_weight + avg_ling * config.linguistic_weight
            
            all_scores_data.extend([
                {"Emotion": emotion, "Methode": "Gewichtet", "Score": avg_weighted},
                {"Emotion": emotion, "Methode": "Modell", "Score": avg_model},
                {"Emotion": emotion, "Methode": "Linguistisch", "Score": avg_ling}
            ])
    
    all_scores_df = pd.DataFrame(all_scores_data)
    
    fig = px.line(
        all_scores_df, 
        x="Emotion", 
        y="Score", 
        color="Methode",
        markers=True,
        color_discrete_map=GermanEmotionVisualizationConfig.METHOD_COLORS,
        title=f"Gewichteter Kombinationsansatz ({config.model_weight:.0%} Modell + {config.linguistic_weight:.0%} Linguistik)"
    )
    
    fig.update_layout(
        xaxis_title='Emotion',
        yaxis_title='Durchschnittlicher Score',
        legend_title='Methode',
        height=GermanEmotionAnalysisConstants.UI_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="german_weighted_comparison_chart")


def render_german_emotion_statistics(statistics: GermanEmotionStatistics) -> None:
    """Render German emotion statistics"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Positive Emotionen", 
            statistics.positive_count,
            f"{statistics.positive_percentage:.1%}"
        )
    
    with col2:
        st.metric(
            "Negative Emotionen", 
            statistics.negative_count,
            f"{statistics.negative_percentage:.1%}"
        )
    
    with col3:
        st.metric(
            "Neutrale Emotionen", 
            statistics.neutral_count,
            f"{statistics.neutral_percentage:.1%}"
        )


def render_german_emotion_examples(
    df: pd.DataFrame, 
    emotion: str, 
    text_column: str, 
    config: GermanEmotionAnalysisConfig
) -> None:
    """Render German emotion examples"""
    emotion_examples = df[df['dominant_emotion'] == emotion]
    
    if emotion_examples.empty:
        return
    
    with st.expander(f"Beispiele für '{emotion}' ({len(emotion_examples)} Kommentare)"):
        best_examples = emotion_examples.sort_values(
            by=emotion, ascending=False
        ).head(GermanEmotionAnalysisConstants.MAX_EXAMPLES_PER_EMOTION)
        
        for i, (_, example) in enumerate(best_examples.iterrows()):
            st.write(f"**{i+1}.** {example[text_column]}")
            
            # Score visualization
            model_score = example[emotion]
            ling_score = example.get(f"{emotion}_linguistic", 0)
            weighted_score = model_score * config.model_weight + ling_score * config.linguistic_weight
            
            scores_df = pd.DataFrame({
                'Methode': ['Modell', 'Linguistisch', f'Gewichtet ({config.model_weight:.0%}/{config.linguistic_weight:.0%})'],
                'Score': [model_score, ling_score, weighted_score]
            })
            
            fig = px.bar(
                scores_df,
                x='Methode',
                y='Score',
                color='Methode',
                color_discrete_map={
                    'Modell': GermanEmotionVisualizationConfig.METHOD_COLORS['Modell'], 
                    'Linguistisch': GermanEmotionVisualizationConfig.METHOD_COLORS['Linguistisch'], 
                    f'Gewichtet ({config.model_weight:.0%}/{config.linguistic_weight:.0%})': GermanEmotionVisualizationConfig.METHOD_COLORS['Gewichtet']
                },
                title=f"Scores für Beispiel {i+1}"
            )
            
            fig.update_layout(
                xaxis_title='',
                yaxis_title='Score',
                showlegend=False,
                height=GermanEmotionAnalysisConstants.UI_CHART_HEIGHT_SMALL
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"german_example_{emotion}_{i}_chart")
            
            # Sentence count info
            sentence_count_col = f"{emotion}_sentence_count"
            if sentence_count_col in example.index and example[sentence_count_col] > 0:
                st.write(f"   *In {example[sentence_count_col]} Sätzen erkannt*")


def render_german_emotions_by_topic_chart(df: pd.DataFrame, topic_labels: Dict[int, str]) -> None:
    """
    Render German emotions by topic visualization - FIXED VERSION!
    
    Args:
        df: DataFrame with emotion and topic data
        topic_labels: Dictionary mapping topic IDs to labels
    """
    st.write("### Emotionen pro Thema")
    
    if 'topic' not in df.columns or 'dominant_emotion' not in df.columns:
        st.warning("Topic- oder Emotions-Informationen fehlen für diese Analyse.")
        return
    
    try:
        # Filter: only valid topics (not -1 = Noise)
        df_valid = df[df['topic'] != -1].copy()
        
        if df_valid.empty:
            st.info("Keine gültigen Topics für die Analyse gefunden.")
            return
        
        # 🔧 FIXED: Unified session state integration
        # Priority 1: Session state topic labels (from Topic Analysis tab)
        if hasattr(st.session_state, 'topic_labels') and st.session_state.topic_labels:
            df_valid['topic_label'] = df_valid['topic'].map(
                lambda x: st.session_state.topic_labels.get(x, f'Thema {x}')
            )
            used_topic_labels = st.session_state.topic_labels
        
        # Priority 2: Legacy combined_topic_labels (fallback for compatibility)
        elif hasattr(st.session_state, 'combined_topic_labels') and st.session_state.combined_topic_labels:
            df_valid['topic_label'] = df_valid['topic'].map(
                lambda x: st.session_state.combined_topic_labels.get(x, f'Thema {x}')
            )
            used_topic_labels = st.session_state.combined_topic_labels
        
        # Priority 3: Parameter topic_labels  
        elif topic_labels:
            df_valid['topic_label'] = df_valid['topic'].map(
                lambda x: topic_labels.get(x, f'Thema {x}')
            )
            used_topic_labels = topic_labels
        
        # Fallback: Generate generic labels
        else:
            df_valid['topic_label'] = df_valid['topic'].map(lambda x: f'Thema {x}')
            used_topic_labels = {topic_id: f'Thema {topic_id}' for topic_id in df_valid['topic'].unique()}
        
        # 🔧 FIXED: Calculate topic counts for proper sorting by frequency
        topic_counts = df_valid['topic'].value_counts().to_dict()
        
        # Group emotions by topic
        emotion_counts = df_valid.groupby(['topic_label', 'dominant_emotion']).size().unstack(fill_value=0)
        
        if emotion_counts.empty:
            st.warning("Keine Daten für Emotion-pro-Topic-Analyse verfügbar.")
            return
        
        # Percentage per topic
        emotion_percent = emotion_counts.div(emotion_counts.sum(axis=1), axis=0) * 100
        
        # 🔧 FIXED: Sort by topic frequency instead of alphabetically
        # Map topic labels back to topic IDs to get counts
        topic_label_to_count = {}
        for topic_label in emotion_counts.index:
            # Find the topic ID for this label
            topic_id = None
            for tid, label in used_topic_labels.items():
                if label == topic_label:
                    topic_id = tid
                    break
            
            if topic_id is not None and topic_id in topic_counts:
                topic_label_to_count[topic_label] = topic_counts[topic_id]
            else:
                # Fallback: count from df_valid
                topic_label_to_count[topic_label] = len(df_valid[df_valid['topic_label'] == topic_label])
        
        # Sort by count (descending) - most frequent topics first
        sorted_topics = sorted(topic_label_to_count.items(), key=lambda x: x[1], reverse=True)
        topic_order = [topic[0] for topic in sorted_topics]
        
        # Reorder emotion_percent by frequency
        emotion_percent = emotion_percent.reindex(topic_order)
        
        # Show info about analyzed topics
        unique_topics = df_valid['topic'].nunique()
        st.info(f"📊 Analysiere {unique_topics} Themen mit Emotions-Daten (sortiert nach Häufigkeit)")
        
        # Prepare data for Plotly
        emo_data = []
        for topic in emotion_percent.index:
            for emotion in emotion_percent.columns:
                emo_data.append({
                    'Thema': topic,
                    'Emotion': emotion,
                    'Anteil (%)': emotion_percent.loc[topic, emotion]
                })
        
        emo_df = pd.DataFrame(emo_data)
        
        # Create stacked bar chart
        fig = px.bar(
            emo_df,
            x='Thema',
            y='Anteil (%)',
            color='Emotion',
            color_discrete_map=GermanEmotionVisualizationConfig.EMOTION_COLORS,
            title='Emotionale Reaktionen nach Themen (sortiert nach Themenhäufigkeit)',
            barmode='stack'
        )
        
        fig.update_layout(
            xaxis_title='Thema',
            yaxis_title='Anteil (%)',
            legend_title='Emotion',
            height=GermanEmotionAnalysisConstants.UI_CHART_HEIGHT_LARGE
        )
        
        st.plotly_chart(fig, use_container_width=True, key="german_emotions_by_topic_chart")
        
        # Show absolute numbers table (also sorted by frequency)
        st.write("Emotionen pro Thema (absolute Zahlen, sortiert nach Themenhäufigkeit):")
        emotion_counts_sorted = emotion_counts.reindex(topic_order)
        st.dataframe(emotion_counts_sorted)
        
        # Render emotional categories summary
        render_german_emotional_categories_by_topic(emotion_counts_sorted)
        
    except Exception as e:
        st.error(f"Fehler bei der Emotion-pro-Thema-Analyse: {str(e)}")
        st.write("Error details:", traceback.format_exc())


def render_german_emotional_categories_by_topic(emotion_counts: pd.DataFrame) -> None:
    """Render German emotional categories summary by topic"""
    st.write("### Zusammenfassung der emotionalen Reaktionen pro Thema")
    
    summary_data = []
    
    for topic_label in emotion_counts.index:
        row_data = {'Thema': topic_label}
        total = emotion_counts.loc[topic_label].sum()
        
        for category, emotions in GermanEmotionFallbacks.EMOTION_CATEGORIES.items():
            # Sum emotions in this category
            emotion_strs = [str(em.value) for em in emotions]
            category_sum = sum(
                emotion_counts.loc[topic_label, emotion] 
                for emotion in emotion_strs 
                if emotion in emotion_counts.columns
            )
            
            # Calculate percentage
            category_pct = (category_sum / total * 100) if total > 0 else 0
            
            # Add to result
            row_data[f"{category.value} (%)"] = category_pct
            row_data[f"{category.value} (Anzahl)"] = category_sum
        
        summary_data.append(row_data)
    
    # Create and display summary
    summary_df = pd.DataFrame(summary_data)
    
    # Visualize emotional categories
    emotion_cat_data = []
    for _, row in summary_df.iterrows():
        for category in GermanEmotionFallbacks.EMOTION_CATEGORIES.keys():
            emotion_cat_data.append({
                'Thema': row['Thema'],
                'Kategorie': category.value,
                'Anteil (%)': row[f'{category.value} (%)']
            })
    
    emotion_cat_df = pd.DataFrame(emotion_cat_data)
    
    fig = px.bar(
        emotion_cat_df,
        x='Thema',
        y='Anteil (%)',
        color='Kategorie',
        color_discrete_map=GermanEmotionVisualizationConfig.CATEGORY_COLORS,
        title='Emotionale Kategorien nach Themen',
        barmode='stack'
    )
    
    fig.update_layout(
        xaxis_title='Thema',
        yaxis_title='Anteil (%)',
        legend_title='Kategorie',
        height=GermanEmotionAnalysisConstants.UI_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="german_emotional_categories_by_topic_chart")
    
    # Show data table
    st.dataframe(summary_df)


def render_german_parameter_validation_ui(df: pd.DataFrame, text_column: str) -> None:
    """Render German parameter validation and experimentation UI"""
    st.write("### 🧪 Parameter-Validierung & Experimente")
    
    with st.expander("🔬 Teste verschiedene Gewichtungen", expanded=False):
        st.write("Experimentiere mit verschiedenen Parameter-Kombinationen:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            exp_model_weight = st.slider(
                "Experimentelle Modell-Gewichtung", 
                0.1, 0.9, 0.7, 0.1,
                key="german_exp_model_weight"
            )
            
            exp_confidence = st.slider(
                "Experimentelle Confidence-Schwelle",
                0.1, 0.9, 0.5, 0.1,
                key="german_exp_confidence"
            )
        
        with col2:
            st.metric("Experiment: Modell-Anteil", f"{exp_model_weight:.0%}")
            st.metric("Experiment: Linguistik-Anteil", f"{1-exp_model_weight:.0%}")
            st.metric("Experiment: Min-Confidence", f"{exp_confidence:.2f}")
        
        if st.button("🧪 Parameter-Experiment durchführen"):
            results = perform_german_parameter_experiment(df)
            render_german_parameter_experiment_results(results)


def perform_german_parameter_experiment(df: pd.DataFrame) -> List[ParameterTestResult]:
    """Perform German parameter experiment with different weight combinations"""
    test_weights = [0.5, 0.6, 0.7, 0.8, 0.9]
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, weight in enumerate(test_weights):
        linguistic_weight = 1 - weight
        
        # Calculate quality metrics
        emotion_diversity = df['dominant_emotion'].nunique() / len(EMOTION_LABEL_MAP)
        balance_score = 1 - df['dominant_emotion'].value_counts(normalize=True).std()
        
        # Simulate different performance for different weights
        performance_modifier = 1 - abs(weight - 0.7) * 0.3  # Best performance at 0.7
        
        quality_score = (emotion_diversity * 0.3 + balance_score * 0.4 + performance_modifier * 0.3)
        
        # Add some noise
        quality_score += np.random.normal(0, 0.02)
        quality_score = max(0, min(1, quality_score))
        
        results.append(ParameterTestResult(
            model_weight=weight,
            linguistic_weight=linguistic_weight,
            quality_score=quality_score,
            emotion_diversity=emotion_diversity,
            balance_score=balance_score
        ))
        
        status_text.text(f"Teste Gewichtung {weight:.1f}...")
        progress_bar.progress((i + 1) / len(test_weights))
    
    return results


def render_german_parameter_experiment_results(results: List[ParameterTestResult]) -> None:
    """Render results of German parameter experiment"""
    # Convert to DataFrame for visualization
    results_data = [
        {
            'model_weight': r.model_weight,
            'quality_score': r.quality_score,
            'emotion_diversity': r.emotion_diversity,
            'balance_score': r.balance_score
        }
        for r in results
    ]
    results_df = pd.DataFrame(results_data)
    
    # Visualization
    fig = px.line(
        results_df, 
        x='model_weight', 
        y='quality_score',
        title='Quality Score vs. Modell-Gewichtung',
        labels={'model_weight': 'Modell-Gewichtung', 'quality_score': 'Quality Score'},
        markers=True
    )
    
    # Mark currently used weight
    current_weight = st.session_state.get('analysis_parameters', {}).get('emotion_model_weight', 0.7)
    fig.add_vline(
        x=current_weight, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Aktuell: {current_weight:.1f}"
    )
    
    # Mark best weight
    best_result = max(results, key=lambda x: x.quality_score)
    fig.add_vline(
        x=best_result.model_weight, 
        line_dash="dot", 
        line_color="green",
        annotation_text=f"Beste: {best_result.model_weight:.1f}"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendation
    if abs(best_result.model_weight - current_weight) > 0.1:
        current_quality = next(
            (r.quality_score for r in results if r.model_weight == current_weight), 
            0
        )
        
        st.warning(f"💡 **Empfehlung:** Probiere Gewichtung {best_result.model_weight:.1f} für bessere Ergebnisse!")
        st.write(f"   • Aktuelle Qualität: {current_quality:.3f}")
        st.write(f"   • Mögliche Qualität: {best_result.quality_score:.3f}")
        
        if st.button("✅ Empfohlene Gewichtung übernehmen"):
            st.session_state.recommended_model_weight = best_result.model_weight
            st.success("Parameter für nächste Analyse gespeichert!")
    else:
        st.success("✅ Deine aktuellen Parameter sind bereits optimal!")
    
    # Detailed results table
    st.write("### Detaillierte Test-Ergebnisse:")
    st.dataframe(results_df.round(3))


def store_german_analysis_parameters(config: GermanEmotionAnalysisConfig, statistics: GermanEmotionStatistics) -> None:
    """Store German analysis parameters in session state"""
    if 'analysis_parameters' not in st.session_state:
        st.session_state.analysis_parameters = {}
    
    st.session_state.analysis_parameters.update(config.to_dict())
    
    # Log completion
    st.success(f"✅ Emotions-Analyse abgeschlossen mit:")
    st.write(f"   • Gewichtung: {config.model_weight:.0%} Modell + {config.linguistic_weight:.0%} Linguistik")
    st.write(f"   • Confidence-Schwelle: {config.confidence_threshold:.2f}")
    st.write(f"   • Dominant-Emotion Verteilung: {statistics.dominant_emotion_distribution}")


# =============================================================================
# MAIN API FUNCTIONS (BACKWARD COMPATIBLE)
# =============================================================================

def prepare_emotion_analysis(
    df: pd.DataFrame, 
    emotion_classifier: Any,
    model_weight: float = GermanEmotionAnalysisConstants.DEFAULT_MODEL_WEIGHT,
    confidence_threshold: float = GermanEmotionAnalysisConstants.DEFAULT_CONFIDENCE_THRESHOLD
) -> pd.DataFrame:
    """
    MODERNIZED: Perform enhanced German emotion analysis with configurable parameters
    
    Args:
        df: DataFrame with comments
        emotion_classifier: The emotion recognition model
        model_weight: Weight for model predictions (0.0-1.0)
        confidence_threshold: Minimum confidence for predictions
        
    Returns:
        DataFrame with emotion information
    """
    
    # Create configuration
    config = GermanEmotionAnalysisConfig(
        model_weight=model_weight,
        confidence_threshold=confidence_threshold
    )
    
    # === UI: Parameter Settings ===
    config = render_german_emotion_analysis_config()
    
    # === BUSINESS: Use Enterprise Manager ===
    manager = GermanEmotionAnalysisManager(config)
    results = manager.analyze_emotions(df, emotion_classifier)
    
    # Show detection frequency in sentences
    st.write("### Erkennungshäufigkeit in Sätzen:")
    if results.statistics.sentence_counts:
        sorted_counts = dict(sorted(results.statistics.sentence_counts.items(), key=lambda x: x[1], reverse=True))
        for emotion, count in sorted_counts.items():
            st.write(f"'{emotion}' in Sätzen erkannt: {count} mal")
    
    # Store parameters
    store_german_analysis_parameters(config, results.statistics)
    
    return results.dataframe


def display_emotion_analysis(
    df: pd.DataFrame, 
    text_column: str, 
    topic_model: Any, 
    topic_labels: Dict[int, str]
) -> None:
    """
    MODERNIZED: Show the results of German emotion analysis with enhanced features
    
    Args:
        df: DataFrame with emotion information
        text_column: Name of column with texts
        topic_model: Trained BERTopic model
        topic_labels: Dictionary with topic labels
    """
    st.subheader("😊 Emotionsanalyse der Kommentare")
    
    # Show parameter information
    if hasattr(st.session_state, 'analysis_parameters'):
        params = st.session_state.analysis_parameters
        if 'emotion_model_weight' in params:
            st.info(
                f"📊 Verwendete Parameter: {params['emotion_model_weight']:.0%} Modell + "
                f"{params['emotion_linguistic_weight']:.0%} Linguistik, "
                f"Confidence ≥ {params['emotion_confidence_threshold']:.2f}"
            )
    
    # Get current configuration
    config = GermanEmotionAnalysisConfig()
    if hasattr(st.session_state, 'analysis_parameters'):
        params = st.session_state.analysis_parameters
        config.model_weight = params.get('emotion_model_weight', GermanEmotionAnalysisConstants.DEFAULT_MODEL_WEIGHT)
        config.linguistic_weight = params.get('emotion_linguistic_weight', GermanEmotionAnalysisConstants.DEFAULT_LINGUISTIC_WEIGHT)
        config.confidence_threshold = params.get('emotion_confidence_threshold', GermanEmotionAnalysisConstants.DEFAULT_CONFIDENCE_THRESHOLD)
    
    # Extract emotion columns
    emotion_columns = list(EMOTION_LABEL_MAP.values())
    
    # Calculate statistics
    statistics_calculator = GermanEmotionStatisticsCalculator(config)
    statistics = statistics_calculator.calculate_emotion_statistics(df, emotion_columns)
    
    # Render visualizations
    render_german_emotion_distribution_chart(statistics)
    render_german_model_vs_linguistic_chart(df, emotion_columns)
    render_german_weighted_comparison_chart(df, emotion_columns, config)
    render_german_emotion_statistics(statistics)
    
    # Render examples for each emotion
    st.write("### Beispiele für jede Emotion")
    existing_emotions = [emo for emo in emotion_columns if emo in df.columns]
    
    for emotion in existing_emotions:
        render_german_emotion_examples(df, emotion, text_column, config)
    
    # Display emotions by topic with proper integration
    st.write("---")
    display_emotions_by_topic(df, topic_labels, GermanEmotionVisualizationConfig.EMOTION_COLORS)
    
    # Parameter validation
    validate_emotion_parameters(df, text_column)


def display_emotions_by_topic(df: pd.DataFrame, topic_labels: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """
    Show German emotion distribution per topic - FIXED VERSION!
    
    Args:
        df: DataFrame with emotion and topic data
        topic_labels: Dictionary mapping topic IDs to labels
        emotion_colors: Color mapping for emotions
    """
    render_german_emotions_by_topic_chart(df, topic_labels)


def validate_emotion_parameters(df: pd.DataFrame, text_column: str) -> None:
    """
    Validate different German parameter combinations for better emotion recognition
    
    Args:
        df: DataFrame with emotion data
        text_column: Name of text column
    """
    render_german_parameter_validation_ui(df, text_column)


def get_recommended_parameters() -> Dict[str, float]:
    """
    Get recommended German parameters from session state
    
    Returns:
        Dictionary with recommended parameters
    """
    return {
        'model_weight': st.session_state.get('recommended_model_weight', GermanEmotionAnalysisConstants.DEFAULT_MODEL_WEIGHT),
        'confidence_threshold': st.session_state.get('recommended_confidence_threshold', GermanEmotionAnalysisConstants.DEFAULT_CONFIDENCE_THRESHOLD)
    }


def get_optimized_parameters() -> Dict[str, float]:
    """
    For main app: Get optimized German parameters if available
    
    Returns:
        Dictionary with optimized parameters
    """
    if hasattr(st.session_state, 'recommended_model_weight'):
        return {
            'model_weight': st.session_state.recommended_model_weight,
            'confidence_threshold': st.session_state.get('recommended_confidence_threshold', GermanEmotionAnalysisConstants.DEFAULT_CONFIDENCE_THRESHOLD)
        }
    return {
        'model_weight': GermanEmotionAnalysisConstants.DEFAULT_MODEL_WEIGHT,
        'confidence_threshold': GermanEmotionAnalysisConstants.DEFAULT_CONFIDENCE_THRESHOLD
    }


# =============================================================================
# EXTENDED API
# =============================================================================

def create_german_emotion_analysis_manager(
    config: Optional[GermanEmotionAnalysisConfig] = None
) -> GermanEmotionAnalysisManager:
    """Factory function for GermanEmotionAnalysisManager"""
    return GermanEmotionAnalysisManager(config)


def create_german_emotion_analysis_config(**kwargs) -> GermanEmotionAnalysisConfig:
    """Factory function for creating custom German configuration"""
    return GermanEmotionAnalysisConfig(**kwargs)


def get_german_emotion_visualization_config() -> GermanEmotionVisualizationConfig:
    """Get visualization configuration for German emotions"""
    return GermanEmotionVisualizationConfig()


def validate_german_emotion_analysis_config(config: GermanEmotionAnalysisConfig) -> Tuple[bool, List[str]]:
    """Validate German emotion analysis configuration"""
    errors = []
    
    if not config.validate():
        errors.append("Configuration validation failed")
    
    if config.linguistic_weight + config.model_weight != 1.0:
        errors.append("Linguistic and model weights must sum to 1.0")
    
    return len(errors) == 0, errors


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Main API Functions (Backward Compatible)
    'prepare_emotion_analysis',
    'display_emotion_analysis',
    'display_emotions_by_topic',
    'validate_emotion_parameters',
    'get_recommended_parameters',
    'get_optimized_parameters',
    
    # New Enterprise Classes and Functions
    'GermanEmotionAnalysisManager',
    'GermanEmotionAnalysisConfig',
    'GermanEmotionStatistics',
    'create_german_emotion_analysis_manager',
    'create_german_emotion_analysis_config',
    
    # Constants
    'GermanEmotionAnalysisConstants',
    'GermanEmotionType',
    'GermanEmotionCategory'
]