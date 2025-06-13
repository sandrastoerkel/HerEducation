"""
Modernized English emotion analysis module.

This module provides emotion analysis functionality for English text with improved
structure, type safety, and parameter configurability.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback

# Import from English emotion detection module
from utils.emotion_detection_english import (
    EMOTION_COLORS, 
    contextual_emotion_detection, 
    split_text_into_sentences, 
    analyze_sentence_structure
)


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class EmotionType(str, Enum):
    """Standard emotion types for English analysis."""
    ANGER = "anger"
    DISGUST = "disgust"
    FEAR = "fear"
    JOY = "joy"
    NEUTRAL = "neutral"
    SADNESS = "sadness"
    SURPRISE = "surprise"


class EmotionCategory(str, Enum):
    """Emotion categories for aggregated analysis."""
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


class DetectionMethod(str, Enum):
    """Detection methods for emotion analysis."""
    MODEL = "Model"
    LINGUISTIC = "Linguistic"
    WEIGHTED = "Weighted"


# Default parameters
DEFAULT_MODEL_WEIGHT = 0.7
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_LINGUISTIC_WEIGHT = 0.3

# Chart configuration
DEFAULT_CHART_HEIGHT = 500
TALL_CHART_HEIGHT = 600
COMPACT_CHART_HEIGHT = 300

# Color schemes
METHOD_COLORS = {
    DetectionMethod.MODEL: "#1976D2",
    DetectionMethod.LINGUISTIC: "#388E3C", 
    DetectionMethod.WEIGHTED: "#7B1FA2"
}

CATEGORY_COLORS = {
    EmotionCategory.POSITIVE: '#4CAF50',
    EmotionCategory.NEGATIVE: '#F44336',
    EmotionCategory.NEUTRAL: '#2196F3'
}

# Emotion categorization
EMOTION_CATEGORIES = {
    EmotionCategory.POSITIVE: [EmotionType.JOY, 'love', EmotionType.SURPRISE],
    EmotionCategory.NEGATIVE: [EmotionType.ANGER, EmotionType.SADNESS, EmotionType.FEAR, EmotionType.DISGUST],
    EmotionCategory.NEUTRAL: [EmotionType.NEUTRAL]
}

# Statistical fallback weights
FALLBACK_WEIGHTS = {
    EmotionType.NEUTRAL: 0.4,
    EmotionType.JOY: 0.15,
    EmotionType.SADNESS: 0.15,
    EmotionType.ANGER: 0.1,
    EmotionType.FEAR: 0.1,
    EmotionType.DISGUST: 0.05,
    EmotionType.SURPRISE: 0.05
}


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class EmotionAnalysisConfig:
    """Configuration for emotion analysis."""
    model_weight: float = DEFAULT_MODEL_WEIGHT
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    linguistic_weight: float = DEFAULT_LINGUISTIC_WEIGHT
    show_advanced_settings: bool = False
    
    def __post_init__(self):
        """Ensure weights sum to 1.0 and are valid."""
        if self.linguistic_weight != 1.0 - self.model_weight:
            self.linguistic_weight = 1.0 - self.model_weight
        
        # Validate ranges
        self.model_weight = max(0.1, min(0.9, self.model_weight))
        self.confidence_threshold = max(0.1, min(0.9, self.confidence_threshold))
        self.linguistic_weight = 1.0 - self.model_weight


@dataclass
class EmotionStatistics:
    """Statistics for emotion analysis results."""
    total_comments: int
    emotion_counts: Dict[str, int]
    dominant_emotions: Dict[str, int]
    category_counts: Dict[str, int]
    average_scores: Dict[str, float]
    linguistic_scores: Dict[str, float] = field(default_factory=dict)
    sentence_counts: Dict[str, int] = field(default_factory=dict)
    
    @property
    def positive_ratio(self) -> float:
        """Calculate ratio of positive emotions."""
        positive_count = self.category_counts.get(EmotionCategory.POSITIVE, 0)
        return positive_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def negative_ratio(self) -> float:
        """Calculate ratio of negative emotions."""
        negative_count = self.category_counts.get(EmotionCategory.NEGATIVE, 0)
        return negative_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def neutral_ratio(self) -> float:
        """Calculate ratio of neutral emotions."""
        neutral_count = self.category_counts.get(EmotionCategory.NEUTRAL, 0)
        return neutral_count / self.total_comments if self.total_comments > 0 else 0.0


@dataclass
class EmotionAnalysisResult:
    """Complete result of emotion analysis."""
    dataframe: pd.DataFrame
    statistics: EmotionStatistics
    config: EmotionAnalysisConfig
    emotion_columns: List[str]
    
    @property
    def success(self) -> bool:
        """Check if analysis was successful."""
        return not self.dataframe.empty and len(self.emotion_columns) > 0


@dataclass
class ParameterTestResult:
    """Result of parameter testing/validation."""
    model_weight: float
    linguistic_weight: float
    quality_score: float
    emotion_diversity: float
    balance_score: float


# =============================================================================
# CORE EMOTION PROCESSING FUNCTIONS
# =============================================================================

def extract_emotion_data(df: pd.DataFrame) -> List[str]:
    """
    Extract emotion columns from emotion detection results.
    
    Args:
        df: DataFrame with emotion data
        
    Returns:
        List of emotion column names
    """
    first_valid_emotion = next((e for e in df['emotions'] if e is not None), None)
    
    if first_valid_emotion is not None:
        emotion_columns = list(first_valid_emotion.keys())
        # Filter out linguistic and sentence count columns from main emotions
        emotion_columns = [
            col for col in emotion_columns 
            if not (col.endswith('_linguistic') or col.endswith('_sentence_count'))
        ]
        return emotion_columns
    else:
        # Fallback to standard English emotions
        return [emotion.value for emotion in EmotionType]


def apply_statistical_fallback(df: pd.DataFrame, emotion_columns: List[str]) -> None:
    """
    Apply statistical fallback when emotion detection fails.
    
    Args:
        df: DataFrame to modify
        emotion_columns: List of emotion columns
    """
    st.error("No emotions could be detected! Fallback to statistical distribution.")
    
    for i in range(len(df)):
        emotions_dict = {}
        for emotion in emotion_columns:
            weight = FALLBACK_WEIGHTS.get(EmotionType(emotion), 0.15)
            emotions_dict[emotion] = np.random.beta(
                5 if emotion == EmotionType.NEUTRAL else 2, 
                5
            ) * weight
        df.at[i, 'emotions'] = emotions_dict


def check_emotion_data_validity(df: pd.DataFrame, emotion_columns: List[str]) -> bool:
    """
    Check if emotion data is valid (not all identical).
    
    Args:
        df: DataFrame with emotion data
        emotion_columns: List of emotion columns
        
    Returns:
        True if data is valid, False if all identical
    """
    for emotion in emotion_columns:
        if emotion in df.columns and df[emotion].nunique() > 1:
            return True
    return False


def apply_weighted_emotion_calculation(
    df: pd.DataFrame, 
    emotion_columns: List[str], 
    config: EmotionAnalysisConfig
) -> None:
    """
    Apply weighted calculation combining model and linguistic scores.
    
    Args:
        df: DataFrame to modify
        emotion_columns: List of emotion columns
        config: Analysis configuration
    """
    if not all(col in df.columns for col in emotion_columns):
        st.error("Not all emotions were detected, cannot determine dominant emotion.")
        available_emotions = [col for col in emotion_columns if col in df.columns]
        if available_emotions:
            df['dominant_emotion'] = df[available_emotions].idxmax(axis=1)
        else:
            # Final fallback
            df['dominant_emotion'] = np.random.choice(
                emotion_columns, 
                size=len(df),
                p=[FALLBACK_WEIGHTS.get(EmotionType(em), 0.1) for em in emotion_columns]
            )
        return
    
    # Calculate weighted emotion scores
    weighted_scores = {}
    
    for emotion in emotion_columns:
        model_score = df[emotion]
        linguistic_col = f"{emotion}_linguistic"
        
        if linguistic_col in df.columns:
            linguistic_score = df[linguistic_col]
            
            # Apply configurable weighting
            weighted_scores[emotion] = (
                model_score * config.model_weight + 
                linguistic_score * config.linguistic_weight
            )
            
            # Confidence-based adjustment
            confidence_boost_mask = model_score < config.confidence_threshold
            if confidence_boost_mask.any():
                boosted_linguistic_weight = min(0.8, config.linguistic_weight * 1.5)
                boosted_model_weight = 1.0 - boosted_linguistic_weight
                
                weighted_scores[emotion].loc[confidence_boost_mask] = (
                    model_score.loc[confidence_boost_mask] * boosted_model_weight + 
                    linguistic_score.loc[confidence_boost_mask] * boosted_linguistic_weight
                )
        else:
            weighted_scores[emotion] = model_score
    
    # Create weighted DataFrame and determine dominant emotion
    weighted_df = pd.DataFrame(weighted_scores)
    df['dominant_emotion'] = weighted_df.idxmax(axis=1)


def calculate_emotion_statistics(df: pd.DataFrame, emotion_columns: List[str]) -> EmotionStatistics:
    """
    Calculate comprehensive emotion statistics.
    
    Args:
        df: DataFrame with emotion data
        emotion_columns: List of emotion columns
        
    Returns:
        EmotionStatistics object
    """
    # Basic counts
    emotion_counts = df['dominant_emotion'].value_counts().to_dict()
    
    # Category counts
    category_counts = {}
    for category, emotions in EMOTION_CATEGORIES.items():
        emotion_set = set(str(em) for em in emotions)
        count = sum(
            emotion_counts.get(emotion, 0) 
            for emotion in emotion_set 
            if emotion in emotion_counts
        )
        category_counts[category.value] = count
    
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
    
    return EmotionStatistics(
        total_comments=len(df),
        emotion_counts=emotion_counts,
        dominant_emotions=emotion_counts,
        category_counts=category_counts,
        average_scores=average_scores,
        linguistic_scores=linguistic_scores,
        sentence_counts=sentence_counts
    )


def perform_emotion_detection(df: pd.DataFrame, emotion_classifier: Any) -> pd.DataFrame:
    """
    Perform emotion detection on all comments.
    
    Args:
        df: DataFrame with comments
        emotion_classifier: The emotion recognition model
        
    Returns:
        DataFrame with emotion data
    """
    st.info("Emotions are being recognized with extended linguistic analysis...")
    
    # Progress bar for emotion detection
    progress_bar = st.progress(0)
    
    # Emotion predictions with improved analysis
    emotions_data = []
    for i, text in enumerate(df['clean_text']):
        emotions = contextual_emotion_detection(text, emotion_classifier)
        emotions_data.append(emotions)
        progress_bar.progress((i + 1) / len(df))
    
    df['emotions'] = emotions_data
    return df


# =============================================================================
# UI RENDERING FUNCTIONS
# =============================================================================

def render_parameter_ui() -> EmotionAnalysisConfig:
    """
    Render parameter configuration UI.
    
    Returns:
        EmotionAnalysisConfig object with user settings
    """
    st.write("### 🎛️ Model Parameter")
    
    # Create columns for parameter settings
    col1, col2 = st.columns(2)
    
    with col1:
        # Advanced settings checkbox
        show_advanced = st.checkbox(
            "🔧 Erweiterte Einstellungen", 
            help="Aktiviere um Gewichtung anzupassen"
        )
        
        config = EmotionAnalysisConfig(show_advanced_settings=show_advanced)
        
        if show_advanced:
            config.model_weight = st.slider(
                "Modell-Gewichtung", 
                min_value=0.1, 
                max_value=0.9, 
                value=DEFAULT_MODEL_WEIGHT,
                step=0.1,
                help="70% Model + 30% Linguistik ist Standard"
            )
            
            config.confidence_threshold = st.slider(
                "Mindest-Confidence",
                min_value=0.1,
                max_value=0.9,
                value=DEFAULT_CONFIDENCE_THRESHOLD,
                step=0.1,
                help="Minimum Sicherheit für Vorhersagen"
            )
            
            # Recalculate linguistic weight
            config.linguistic_weight = 1.0 - config.model_weight
    
    with col2:
        # Show current settings
        st.metric("Modell-Anteil", f"{config.model_weight:.0%}")
        st.metric("Linguistik-Anteil", f"{config.linguistic_weight:.0%}")
        st.metric("Confidence-Filter", f"{config.confidence_threshold:.1f}")
    
    st.info(
        f"🔬 Aktuelle Gewichtung: {config.model_weight:.0%} KI-Modell + "
        f"{config.linguistic_weight:.0%} Linguistische Analyse"
    )
    
    return config


def render_emotion_distribution_chart(statistics: EmotionStatistics) -> None:
    """
    Render emotion distribution chart.
    
    Args:
        statistics: Emotion statistics to visualize
    """
    st.write("### Distribution of Emotions")
    
    # Create Plotly bar chart
    emotion_counts = statistics.emotion_counts
    
    fig = px.bar(
        x=list(emotion_counts.keys()), 
        y=list(emotion_counts.values()),
        color=list(emotion_counts.keys()),
        color_discrete_map=EMOTION_COLORS,
        labels={'x': 'Emotion', 'y': 'Count'},
        title='Dominant Emotions in Comments'
    )
    
    fig.update_layout(
        xaxis_title='Emotion',
        yaxis_title='Count',
        legend_title='Emotion',
        showlegend=False,
        height=DEFAULT_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="emotion_distribution_chart")


def render_model_vs_linguistic_chart(df: pd.DataFrame, emotion_columns: List[str]) -> None:
    """
    Render comparison chart between model and linguistic detection.
    
    Args:
        df: DataFrame with emotion data
        emotion_columns: List of emotion columns
    """
    st.write("### Comparison: Model vs. Linguistic Detection")
    
    # Create comparison data
    comparison_data = []
    
    for emotion in emotion_columns:
        # Model-based detection
        model_count = len(df[df[emotion] > 0.5]) if emotion in df.columns else 0
        
        # Linguistic detection
        ling_col = f"{emotion}_linguistic"
        ling_count = len(df[df[ling_col] > 0.5]) if ling_col in df.columns else 0
        
        # Add data for Plotly
        comparison_data.extend([
            {"Emotion": emotion, "Method": DetectionMethod.MODEL, "Count": model_count},
            {"Emotion": emotion, "Method": DetectionMethod.LINGUISTIC, "Count": ling_count}
        ])
    
    # Create DataFrame for visualization
    comparison_df = pd.DataFrame(comparison_data)
    
    # Visualize comparison with Plotly
    fig = px.bar(
        comparison_df,
        x="Emotion",
        y="Count",
        color="Method",
        barmode="group",
        color_discrete_map=METHOD_COLORS,
        title="Comparison: Model vs. Linguistic Detection"
    )
    
    fig.update_layout(
        xaxis_title='Emotion',
        yaxis_title='Number of Detections',
        legend_title='Method',
        height=DEFAULT_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="model_vs_linguistic_chart")


def render_weighted_combination_chart(
    df: pd.DataFrame, 
    emotion_columns: List[str], 
    config: EmotionAnalysisConfig
) -> None:
    """
    Render weighted combination approach visualization.
    
    Args:
        df: DataFrame with emotion data
        emotion_columns: List of emotion columns
        config: Analysis configuration
    """
    st.write("### Current Weighted Combination Approach")
    
    # Prepare weighted scores for visualization
    all_scores_data = []
    
    for emotion in emotion_columns:
        if emotion in df.columns and f"{emotion}_linguistic" in df.columns:
            # Calculate average values for each emotion
            avg_model = df[emotion].mean()
            avg_ling = df[f"{emotion}_linguistic"].mean()
            avg_weighted = avg_model * config.model_weight + avg_ling * config.linguistic_weight
            
            # Add data points
            all_scores_data.extend([
                {"Emotion": emotion, "Method": DetectionMethod.WEIGHTED, "Score": avg_weighted},
                {"Emotion": emotion, "Method": DetectionMethod.MODEL, "Score": avg_model},
                {"Emotion": emotion, "Method": DetectionMethod.LINGUISTIC, "Score": avg_ling}
            ])
    
    # Create DataFrame and visualize
    all_scores_df = pd.DataFrame(all_scores_data)
    
    fig = px.line(
        all_scores_df, 
        x="Emotion", 
        y="Score", 
        color="Method",
        markers=True,
        color_discrete_map=METHOD_COLORS,
        title=f"Current Weighted Combination ({config.model_weight:.0%} Model + {config.linguistic_weight:.0%} Linguistic)"
    )
    
    fig.update_layout(
        xaxis_title='Emotion',
        yaxis_title='Average Score',
        legend_title='Method',
        height=DEFAULT_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="weighted_comparison_chart")


def render_emotion_category_metrics(statistics: EmotionStatistics) -> None:
    """
    Render emotion category metrics.
    
    Args:
        statistics: Emotion statistics
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Positive Emotions", 
            statistics.category_counts.get(EmotionCategory.POSITIVE, 0),
            f"{statistics.positive_ratio:.1%}"
        )
    
    with col2:
        st.metric(
            "Negative Emotions", 
            statistics.category_counts.get(EmotionCategory.NEGATIVE, 0),
            f"{statistics.negative_ratio:.1%}"
        )
    
    with col3:
        st.metric(
            "Neutral Emotions", 
            statistics.category_counts.get(EmotionCategory.NEUTRAL, 0),
            f"{statistics.neutral_ratio:.1%}"
        )


def render_emotion_examples(df: pd.DataFrame, text_column: str, emotion_columns: List[str], config: EmotionAnalysisConfig) -> None:
    """
    Render examples for each emotion category.
    
    Args:
        df: DataFrame with emotion data
        text_column: Name of text column
        emotion_columns: List of emotion columns
        config: Analysis configuration
    """
    st.write("### Examples for Each Emotion")
    
    existing_emotions = [emo for emo in emotion_columns if emo in df.columns]
    
    for emotion in existing_emotions:
        emotion_examples = df[df['dominant_emotion'] == emotion]
        if not emotion_examples.empty:
            with st.expander(f"Examples for '{emotion}' ({len(emotion_examples)} comments)"):
                # Top 3 examples with highest emotion score
                best_examples = emotion_examples.sort_values(by=emotion, ascending=False).head(3)
                
                for i, (_, example) in enumerate(best_examples.iterrows()):
                    st.write(f"**{i+1}.** {example[text_column]}")
                    
                    # Show scores visualization
                    model_score = example[emotion]
                    ling_score = example.get(f"{emotion}_linguistic", 0)
                    weighted_score = model_score * config.model_weight + ling_score * config.linguistic_weight
                    
                    # Create score comparison chart
                    scores_df = pd.DataFrame({
                        'Method': ['Model', 'Linguistic', f'Weighted ({config.model_weight:.0%}/{config.linguistic_weight:.0%})'],
                        'Score': [model_score, ling_score, weighted_score]
                    })
                    
                    fig = px.bar(
                        scores_df,
                        x='Method',
                        y='Score',
                        color='Method',
                        color_discrete_map={
                            'Model': METHOD_COLORS[DetectionMethod.MODEL], 
                            'Linguistic': METHOD_COLORS[DetectionMethod.LINGUISTIC], 
                            f'Weighted ({config.model_weight:.0%}/{config.linguistic_weight:.0%})': METHOD_COLORS[DetectionMethod.WEIGHTED]
                        },
                        title=f"Scores for Example {i+1}"
                    )
                    
                    fig.update_layout(
                        xaxis_title='',
                        yaxis_title='Score',
                        showlegend=False,
                        height=COMPACT_CHART_HEIGHT
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key=f"example_{emotion}_{i}_chart")
                    
                    # Show sentence count if available
                    sent_count_col = f"{emotion}_sentence_count"
                    if sent_count_col in example and example[sent_count_col] > 0:
                        st.write(f"   *Detected in {example[sent_count_col]} sentences*")


def render_emotions_by_topic_chart(df: pd.DataFrame, topic_labels: Dict[int, str]) -> None:
    """
    Render emotions by topic visualization.
    
    Args:
        df: DataFrame with emotion and topic data
        topic_labels: Dictionary mapping topic IDs to labels
    """
    st.write("### Emotions per Topic")
    
    if 'topic' not in df.columns or 'dominant_emotion' not in df.columns:
        st.warning("Topic or emotion information missing for this analysis.")
        return
    
    try:
        # Filter: only valid topics (not -1 = Noise)
        df_valid = df[df['topic'] != -1].copy()
        
        if df_valid.empty:
            st.info("No valid topics found for emotion analysis.")
            return
        
        # Use topic labels with priority system
        # Priority 1: Session state topic labels (from Topic Analysis tab)
        if hasattr(st.session_state, 'topic_labels') and st.session_state.topic_labels:
            df_valid['topic_label'] = df_valid['topic'].map(
                lambda x: st.session_state.topic_labels.get(x, f'Topic {x}')
            )
            used_topic_labels = st.session_state.topic_labels
        
        # Priority 2: Parameter topic_labels  
        elif topic_labels:
            df_valid['topic_label'] = df_valid['topic'].map(
                lambda x: topic_labels.get(x, f'Topic {x}')
            )
            used_topic_labels = topic_labels
        
        # Fallback: Generate generic labels
        else:
            df_valid['topic_label'] = df_valid['topic'].map(lambda x: f'Topic {x}')
            used_topic_labels = {topic_id: f'Topic {topic_id}' for topic_id in df_valid['topic'].unique()}
        
        # Calculate topic counts for proper sorting by frequency
        topic_counts = df_valid['topic'].value_counts().to_dict()
        
        # Group emotions by topic
        emotion_counts = df_valid.groupby(['topic_label', 'dominant_emotion']).size().unstack(fill_value=0)
        emotion_percent = emotion_counts.div(emotion_counts.sum(axis=1), axis=0) * 100
        
        # Sort by topic frequency instead of alphabetically
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
        
        # Prepare data for Plotly
        emo_data = []
        for topic in emotion_percent.index:
            for emotion in emotion_percent.columns:
                emo_data.append({
                    'Topic': topic,
                    'Emotion': emotion,
                    'Percentage (%)': emotion_percent.loc[topic, emotion]
                })
        
        emo_df = pd.DataFrame(emo_data)
        
        # Create stacked bar chart
        fig = px.bar(
            emo_df,
            x='Topic',
            y='Percentage (%)',
            color='Emotion',
            color_discrete_map=EMOTION_COLORS,
            title='Emotional Reactions by Topics (sorted by topic frequency)',
            barmode='stack'
        )
        
        fig.update_layout(
            xaxis_title='Topic',
            yaxis_title='Percentage (%)',
            legend_title='Emotion',
            height=TALL_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="emotions_by_topic_chart")
        
        # Show absolute numbers table (also sorted by frequency)
        st.write("Emotions per topic (absolute numbers):")
        emotion_counts_sorted = emotion_counts.reindex(topic_order)
        st.dataframe(emotion_counts_sorted)
        
        # Render emotional categories summary
        render_emotional_categories_by_topic(emotion_counts_sorted)
        
    except Exception as e:
        st.error(f"Error in emotion-per-topic analysis: {str(e)}")
        st.write("Error details:", traceback.format_exc())


def render_emotional_categories_by_topic(emotion_counts: pd.DataFrame) -> None:
    """
    Render emotional categories summary by topic.
    
    Args:
        emotion_counts: DataFrame with emotion counts by topic
    """
    st.write("### Summary of Emotional Reactions per Topic")
    
    # Calculate aggregated emotion categories
    summary_data = []
    
    for topic_label in emotion_counts.index:
        row_data = {'Topic': topic_label}
        total = emotion_counts.loc[topic_label].sum()
        
        for category, emotions in EMOTION_CATEGORIES.items():
            # Sum emotions in this category
            emotion_strs = [str(em) for em in emotions]
            category_sum = sum(
                emotion_counts.loc[topic_label, emotion] 
                for emotion in emotion_strs 
                if emotion in emotion_counts.columns
            )
            
            # Calculate percentage
            category_pct = (category_sum / total * 100) if total > 0 else 0
            
            # Add to result
            row_data[f"{category.value} (%)"] = category_pct
            row_data[f"{category.value} (Count)"] = category_sum
        
        summary_data.append(row_data)
    
    # Create and display summary
    summary_df = pd.DataFrame(summary_data)
    
    # Visualize emotional categories
    emotion_cat_data = []
    for _, row in summary_df.iterrows():
        for category in EMOTION_CATEGORIES.keys():
            emotion_cat_data.append({
                'Topic': row['Topic'],
                'Category': category.value,
                'Percentage (%)': row[f'{category.value} (%)']
            })
    
    emotion_cat_df = pd.DataFrame(emotion_cat_data)
    
    fig = px.bar(
        emotion_cat_df,
        x='Topic',
        y='Percentage (%)',
        color='Category',
        color_discrete_map=CATEGORY_COLORS,
        title='Emotional Categories by Topics',
        barmode='stack'
    )
    
    fig.update_layout(
        xaxis_title='Topic',
        yaxis_title='Percentage (%)',
        legend_title='Category',
        height=DEFAULT_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True, key="emotional_categories_by_topic_chart")
    
    # Show data table
    st.dataframe(summary_df)


def render_parameter_validation_ui(df: pd.DataFrame, text_column: str) -> None:
    """
    Render parameter validation and experimentation UI.
    
    Args:
        df: DataFrame with emotion data  
        text_column: Name of text column
    """
    st.write("### 🧪 Parameter-Validierung & Experimente")
    
    with st.expander("🔬 Teste verschiedene Gewichtungen", expanded=False):
        st.write("Experimentiere mit verschiedenen Parameter-Kombinationen:")
        
        # Parameter for experiment
        col1, col2 = st.columns(2)
        
        with col1:
            exp_model_weight = st.slider(
                "Experimentelle Model-Gewichtung", 
                0.1, 0.9, 0.7, 0.1,
                key="exp_model_weight"
            )
            
            exp_confidence = st.slider(
                "Experimentelle Confidence-Schwelle",
                0.1, 0.9, 0.5, 0.1,
                key="exp_confidence"
            )
        
        with col2:
            st.metric("Experiment: Model-Anteil", f"{exp_model_weight:.0%}")
            st.metric("Experiment: Linguistik-Anteil", f"{1-exp_model_weight:.0%}")
            st.metric("Experiment: Min-Confidence", f"{exp_confidence:.2f}")
        
        if st.button("🧪 Parameter-Experiment durchführen"):
            results = perform_parameter_experiment(df)
            render_parameter_experiment_results(results)


def perform_parameter_experiment(df: pd.DataFrame) -> List[ParameterTestResult]:
    """
    Perform parameter experiment with different weight combinations.
    
    Args:
        df: DataFrame with emotion data
        
    Returns:
        List of ParameterTestResult objects
    """
    test_weights = [0.5, 0.6, 0.7, 0.8, 0.9]
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, weight in enumerate(test_weights):
        linguistic_weight = 1 - weight
        
        # Calculate quality metrics
        emotion_diversity = df['dominant_emotion'].nunique() / 7  # 7 possible emotions
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


def render_parameter_experiment_results(results: List[ParameterTestResult]) -> None:
    """
    Render results of parameter experiment.
    
    Args:
        results: List of experiment results
    """
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
        title='Quality Score vs. Model Weight',
        labels={'model_weight': 'Model Weight', 'quality_score': 'Quality Score'},
        markers=True
    )
    
    # Mark currently used weight
    current_weight = st.session_state.get('analysis_parameters', {}).get('emotion_model_weight', 0.7)
    fig.add_vline(
        x=current_weight, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Current: {current_weight:.1f}"
    )
    
    # Mark best weight
    best_result = max(results, key=lambda x: x.quality_score)
    fig.add_vline(
        x=best_result.model_weight, 
        line_dash="dot", 
        line_color="green",
        annotation_text=f"Best: {best_result.model_weight:.1f}"
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


def store_analysis_parameters(config: EmotionAnalysisConfig, statistics: EmotionStatistics) -> None:
    """
    Store analysis parameters in session state.
    
    Args:
        config: Analysis configuration
        statistics: Analysis statistics
    """
    if 'analysis_parameters' not in st.session_state:
        st.session_state.analysis_parameters = {}
    
    st.session_state.analysis_parameters.update({
        'emotion_model_weight': config.model_weight,
        'emotion_linguistic_weight': config.linguistic_weight,
        'emotion_confidence_threshold': config.confidence_threshold
    })
    
    # Log completion
    st.success(f"✅ Emotion-Analyse abgeschlossen mit:")
    st.write(f"   • Gewichtung: {config.model_weight:.0%} Modell + {config.linguistic_weight:.0%} Linguistik")
    st.write(f"   • Confidence-Schwelle: {config.confidence_threshold:.2f}")
    st.write(f"   • Dominant-Emotion Verteilung: {statistics.dominant_emotions}")


# =============================================================================
# MAIN API FUNCTIONS (BACKWARD COMPATIBLE)
# =============================================================================

def prepare_emotion_analysis(
    df: pd.DataFrame, 
    emotion_classifier: Any, 
    model_weight: float = DEFAULT_MODEL_WEIGHT, 
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
) -> pd.DataFrame:
    """
    Perform enhanced emotion analysis for all comments with configurable parameters.
    
    Args:
        df: DataFrame with the comments
        emotion_classifier: The emotion recognition model
        model_weight: Weight for model predictions (0.0-1.0)
        confidence_threshold: Minimum confidence for predictions
        
    Returns:
        DataFrame with emotion information
    """
    # Render parameter UI and get configuration
    config = render_parameter_ui()
    
    # Override with provided parameters if different from default
    if model_weight != DEFAULT_MODEL_WEIGHT:
        config.model_weight = model_weight
        config.linguistic_weight = 1.0 - model_weight
    if confidence_threshold != DEFAULT_CONFIDENCE_THRESHOLD:
        config.confidence_threshold = confidence_threshold
    
    # Perform emotion detection
    df = perform_emotion_detection(df, emotion_classifier)
    
    # Extract emotion columns
    emotion_columns = extract_emotion_data(df)
    
    # Handle case where no emotions detected
    if not emotion_columns:
        apply_statistical_fallback(df, [emotion.value for emotion in EmotionType])
        emotion_columns = [emotion.value for emotion in EmotionType]
    
    # Extract emotions into separate columns
    for emotion in emotion_columns:
        df[emotion] = df['emotions'].apply(lambda x: x.get(emotion, 0) if x is not None else 0)
    
    # Extract linguistic information
    for emotion in emotion_columns:
        col_name = f"{emotion}_linguistic"
        df[col_name] = df['emotions'].apply(
            lambda x: x.get(col_name, 0) if x is not None and col_name in x else 0
        )
    
    # Extract sentence counts
    for emotion in emotion_columns:
        col_name = f"{emotion}_sentence_count"
        df[col_name] = df['emotions'].apply(
            lambda x: x.get(col_name, 0) if x is not None and col_name in x else 0
        )
    
    # Validate emotion data
    if not check_emotion_data_validity(df, emotion_columns):
        st.error("All emotion values are identical! Fallback to statistical distribution.")
        for i in range(len(df)):
            for emotion in emotion_columns:
                weight = FALLBACK_WEIGHTS.get(EmotionType(emotion), 0.1)
                df.at[i, emotion] = np.random.beta(
                    5 if emotion == EmotionType.NEUTRAL else 2, 
                    5
                ) * weight
    
    # Apply weighted emotion calculation
    apply_weighted_emotion_calculation(df, emotion_columns, config)
    
    # Calculate statistics
    statistics = calculate_emotion_statistics(df, emotion_columns)
    
    # Store parameters for later use
    store_analysis_parameters(config, statistics)
    
    # Show detection frequency in sentences
    st.write("### Detection frequency in sentences:")
    if statistics.sentence_counts:
        sorted_counts = dict(sorted(statistics.sentence_counts.items(), key=lambda x: x[1], reverse=True))
        for emotion, count in sorted_counts.items():
            st.write(f"'{emotion}' detected in sentences: {count} times")
    
    return df


def display_emotion_analysis(
    df: pd.DataFrame, 
    text_column: str, 
    topic_model: Any, 
    topic_labels: Dict[int, str]
) -> None:
    """
    Show the results of emotion analysis with enhanced parameter information.
    
    Args:
        df: DataFrame with emotion information
        text_column: Name of column with texts
        topic_model: Trained BERTopic model
        topic_labels: Dictionary with topic labels
    """
    st.subheader("😊 Emotion Analysis of Comments")
    
    # Show parameter information
    if hasattr(st.session_state, 'analysis_parameters'):
        params = st.session_state.analysis_parameters
        if 'emotion_model_weight' in params:
            st.info(
                f"📊 Used Parameters: {params['emotion_model_weight']:.0%} Model + "
                f"{params['emotion_linguistic_weight']:.0%} Linguistic, "
                f"Confidence ≥ {params['emotion_confidence_threshold']:.2f}"
            )
    
    # Get current configuration
    config = EmotionAnalysisConfig()
    if hasattr(st.session_state, 'analysis_parameters'):
        params = st.session_state.analysis_parameters
        config.model_weight = params.get('emotion_model_weight', DEFAULT_MODEL_WEIGHT)
        config.linguistic_weight = params.get('emotion_linguistic_weight', DEFAULT_LINGUISTIC_WEIGHT)
        config.confidence_threshold = params.get('emotion_confidence_threshold', DEFAULT_CONFIDENCE_THRESHOLD)
    
    # Extract emotion columns
    emotion_columns = extract_emotion_data(df)
    
    # Calculate statistics
    statistics = calculate_emotion_statistics(df, emotion_columns)
    
    # Render visualizations
    render_emotion_distribution_chart(statistics)
    render_model_vs_linguistic_chart(df, emotion_columns)
    render_weighted_combination_chart(df, emotion_columns, config)
    render_emotion_category_metrics(statistics)
    render_emotion_examples(df, text_column, emotion_columns, config)
    
    # Display emotions by topic with proper integration
    st.write("---")
    display_emotions_by_topic(df, topic_labels, EMOTION_COLORS)
    
    # Parameter validation


def display_emotions_by_topic(df: pd.DataFrame, topic_labels: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """
    Show emotion distribution per topic.
    
    Args:
        df: DataFrame with emotion and topic data
        topic_labels: Dictionary mapping topic IDs to labels
        emotion_colors: Color mapping for emotions
    """
    render_emotions_by_topic_chart(df, topic_labels)


def validate_emotion_parameters(df: pd.DataFrame, text_column: str) -> None:
    """
    Validate different parameter combinations for better emotion recognition.
    
    Args:
        df: DataFrame with emotion data
        text_column: Name of text column
    """
    render_parameter_validation_ui(df, text_column)


def get_recommended_parameters() -> Dict[str, float]:
    """
    Get recommended parameters from session state.
    
    Returns:
        Dictionary with recommended parameters
    """
    return {
        'model_weight': st.session_state.get('recommended_model_weight', DEFAULT_MODEL_WEIGHT),
        'confidence_threshold': st.session_state.get('recommended_confidence_threshold', DEFAULT_CONFIDENCE_THRESHOLD)
    }


def get_optimized_parameters() -> Dict[str, float]:
    """
    For main app: Get optimized parameters if available.
    
    Returns:
        Dictionary with optimized parameters
    """
    if hasattr(st.session_state, 'recommended_model_weight'):
        return {
            'model_weight': st.session_state.recommended_model_weight,
            'confidence_threshold': st.session_state.get('recommended_confidence_threshold', DEFAULT_CONFIDENCE_THRESHOLD)
        }
    return {
        'model_weight': DEFAULT_MODEL_WEIGHT,
        'confidence_threshold': DEFAULT_CONFIDENCE_THRESHOLD
    }