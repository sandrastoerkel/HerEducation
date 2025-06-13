"""
Modernized English sentiment analysis module.

This module provides sentiment analysis functionality for English text with improved
structure, type safety, and interactive visualizations using Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from collections import Counter
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

# Configuration constants
DEFAULT_CHUNK_SIZE = 512
DEFAULT_MIN_LENGTH = 0
MAX_MIN_LENGTH = 100
DEFAULT_MIN_CONFIDENCE = 0.5
DEFAULT_VALIDATION_SAMPLES = 5
MIN_VALIDATION_SAMPLES = 3
MAX_VALIDATION_SAMPLES = 10
EXAMPLE_COMMENTS_LIMIT = 5
TOP_EXAMPLES_LIMIT = 3

# Sentiment values as strings (keep it simple - don't break what works!)
SENTIMENT_POSITIVE = 'positive'
SENTIMENT_NEUTRAL = 'neutral' 
SENTIMENT_NEGATIVE = 'negative'

# Color schemes for consistent visualization
SENTIMENT_COLORS = {
    SENTIMENT_POSITIVE: '#4CAF50',  # Green
    SENTIMENT_NEUTRAL: '#9E9E9E',   # Gray
    SENTIMENT_NEGATIVE: '#F44336'   # Red
}

# Chart configuration
DEFAULT_CHART_HEIGHT = 500
COMPACT_CHART_HEIGHT = 400
HISTOGRAM_BINS = 20


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class SentimentAnalysisConfig:
    """Configuration for sentiment analysis."""
    min_length: int = DEFAULT_MIN_LENGTH
    chunk_size: int = DEFAULT_CHUNK_SIZE
    min_confidence: float = DEFAULT_MIN_CONFIDENCE
    validation_samples: int = DEFAULT_VALIDATION_SAMPLES


@dataclass
class SentimentStatistics:
    """Statistics for sentiment analysis results."""
    total_comments: int
    positive_count: int
    neutral_count: int
    negative_count: int
    average_confidence: float
    high_confidence_count: int
    
    @property
    def positive_ratio(self) -> float:
        """Calculate ratio of positive comments."""
        return self.positive_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def neutral_ratio(self) -> float:
        """Calculate ratio of neutral comments."""
        return self.neutral_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def negative_ratio(self) -> float:
        """Calculate ratio of negative comments."""
        return self.negative_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def high_confidence_ratio(self) -> float:
        """Calculate ratio of high confidence predictions."""
        return self.high_confidence_count / self.total_comments if self.total_comments > 0 else 0.0


@dataclass
class ValidationResult:
    """Result of manual validation."""
    total_samples: int
    matches: int
    accuracy: float
    detailed_results: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def agreement_percentage(self) -> str:
        """Get agreement as formatted percentage."""
        return f"{self.accuracy:.0%}"


@dataclass
class SentimentAnalysisResult:
    """Complete result of sentiment analysis."""
    dataframe: pd.DataFrame
    statistics: SentimentStatistics
    config: SentimentAnalysisConfig
    
    @property
    def success(self) -> bool:
        """Check if analysis was successful."""
        return not self.dataframe.empty and 'sentiment' in self.dataframe.columns


# =============================================================================
# CORE SENTIMENT PROCESSING FUNCTIONS
# =============================================================================

def process_text_chunks(text: Any, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
    """
    Split text into manageable chunks for processing.
    
    Args:
        text: Input text (can be various types)
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of text chunks
    """
    if pd.isna(text) or text is None or text == "":
        return []
    
    text_str = str(text)
    return [text_str[i:i+chunk_size] for i in range(0, len(text_str), chunk_size)]


def map_cardiff_labels(result_label: str) -> str:
    """
    Map CardiffNLP model labels to standard sentiment types.
    
    Args:
        result_label: Raw label from Cardiff model
        
    Returns:
        Mapped sentiment type as string
    """
    # Use original stable mapping - don't break what works!
    label_mapping = {
        'LABEL_0': 'negative',
        'LABEL_1': 'neutral',
        'LABEL_2': 'positive'
    }
    return label_mapping.get(result_label, result_label.lower())


def analyze_text_sentiment(text: Any, sentiment_pipeline: Callable, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """
    Analyze sentiment of a single text by splitting into chunks.
    
    Args:
        text: Input text to analyze
        sentiment_pipeline: Sentiment analysis pipeline
        chunk_size: Size of chunks for processing
        
    Returns:
        Most common sentiment across all chunks as string
    """
    chunks = process_text_chunks(text, chunk_size)
    
    if not chunks:
        return "neutral"
    
    try:
        # Analyze each chunk - use original logic that works!
        results = [sentiment_pipeline(chunk)[0] for chunk in chunks]
        
        # Map labels and find most common sentiment
        sentiments = [map_cardiff_labels(result["label"]) for result in results]
        most_common = Counter(sentiments).most_common(1)[0][0]
        return most_common
        
    except Exception:
        return "neutral"


def calculate_text_confidence(text: Any, sentiment_pipeline: Callable, chunk_size: int = DEFAULT_CHUNK_SIZE) -> float:
    """
    Calculate average confidence score for a text.
    
    Args:
        text: Input text to analyze
        sentiment_pipeline: Sentiment analysis pipeline
        chunk_size: Size of chunks for processing
        
    Returns:
        Average confidence score
    """
    chunks = process_text_chunks(text, chunk_size)
    
    if not chunks:
        return 0.0
    
    try:
        results = [sentiment_pipeline(chunk)[0] for chunk in chunks]
        scores = [result["score"] for result in results]
        return sum(scores) / len(scores) if scores else 0.0
        
    except Exception:
        return 0.0


def calculate_sentiment_statistics(df: pd.DataFrame, min_confidence: float = DEFAULT_MIN_CONFIDENCE) -> SentimentStatistics:
    """
    Calculate comprehensive sentiment statistics.
    
    Args:
        df: DataFrame with sentiment data
        min_confidence: Minimum confidence threshold
        
    Returns:
        SentimentStatistics object
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


def perform_batch_sentiment_analysis(df: pd.DataFrame, text_column: str, sentiment_pipeline: Callable, config: SentimentAnalysisConfig) -> pd.DataFrame:
    """
    Perform sentiment analysis on a batch of texts.
    
    Args:
        df: DataFrame with texts
        text_column: Name of the text column
        sentiment_pipeline: Sentiment analysis pipeline
        config: Analysis configuration
        
    Returns:
        DataFrame with sentiment results
    """
    progress_bar = st.progress(0)
    total_rows = len(df)
    
    # Ensure text column is string type and handle NaN
    df[text_column] = df[text_column].fillna("").astype(str)
    
    sentiments = []
    confidences = []
    
    for i, text in enumerate(df[text_column]):
        sentiment = analyze_text_sentiment(text, sentiment_pipeline, config.chunk_size)
        confidence = calculate_text_confidence(text, sentiment_pipeline, config.chunk_size)
        
        sentiments.append(sentiment)  # sentiment is already a string now
        confidences.append(confidence)
        
        progress_bar.progress((i + 1) / total_rows)
    
    df['sentiment'] = sentiments
    df['confidence'] = confidences
    
    return df.reset_index(drop=True)


# =============================================================================
# CHART RENDERING FUNCTIONS
# =============================================================================

def render_sentiment_distribution_chart(statistics: SentimentStatistics, title: str = "Sentiment Distribution") -> go.Figure:
    """
    Create sentiment distribution bar chart.
    
    Args:
        statistics: Sentiment statistics
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    sentiments = ['positive', 'neutral', 'negative']
    counts = [statistics.positive_count, statistics.neutral_count, statistics.negative_count]
    colors = ['#4CAF50', '#9E9E9E', '#F44336']  # Green, Gray, Red
    
    fig = go.Figure(data=[
        go.Bar(
            x=sentiments,
            y=counts,
            marker_color=colors,
            text=counts,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title='Sentiment',
        yaxis_title='Count',
        height=DEFAULT_CHART_HEIGHT,
        showlegend=False
    )
    
    return fig


def render_confidence_histogram(df: pd.DataFrame, title: str = "Distribution of Model Confidence") -> go.Figure:
    """
    Create confidence distribution histogram.
    
    Args:
        df: DataFrame with confidence data
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure(data=[
        go.Histogram(
            x=df['confidence'],
            nbinsx=HISTOGRAM_BINS,
            marker_color='skyblue',
            opacity=0.7
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title='Confidence',
        yaxis_title='Count',
        height=COMPACT_CHART_HEIGHT
    )
    
    return fig


def render_confidence_vs_sentiment_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot of confidence vs sentiment.
    
    Args:
        df: DataFrame with sentiment and confidence data
        
    Returns:
        Plotly figure object
    """
    # Use original string-based mapping for colors
    color_map = {
        'positive': '#4CAF50',
        'neutral': '#9E9E9E', 
        'negative': '#F44336'
    }
    
    fig = px.box(
        df, 
        x='sentiment', 
        y='confidence',
        color='sentiment',
        color_discrete_map=color_map,
        title='Confidence Distribution by Sentiment'
    )
    
    fig.update_layout(
        height=COMPACT_CHART_HEIGHT,
        showlegend=False
    )
    
    return fig


# =============================================================================
# UI RENDERING FUNCTIONS
# =============================================================================

def render_analysis_config_ui() -> SentimentAnalysisConfig:
    """
    Render configuration UI for sentiment analysis.
    
    Returns:
        SentimentAnalysisConfig object
    """
    st.subheader("Analysis Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_length = st.slider(
            "Minimum comment length (characters)", 
            0, MAX_MIN_LENGTH, DEFAULT_MIN_LENGTH
        )
    
    with col2:
        validation_samples = st.slider(
            "Validation samples", 
            MIN_VALIDATION_SAMPLES, MAX_VALIDATION_SAMPLES, DEFAULT_VALIDATION_SAMPLES
        )
    
    return SentimentAnalysisConfig(
        min_length=min_length,
        validation_samples=validation_samples
    )


def render_data_preview(df: pd.DataFrame, text_column: str) -> None:
    """
    Render preview of the data to be analyzed.
    
    Args:
        df: DataFrame to preview
        text_column: Name of text column
    """
    st.write("Examples of extracted comments:")
    
    # Show relevant columns
    preview_columns = [text_column]
    if 'original_line' in df.columns:
        preview_columns.append('original_line')
    
    st.dataframe(df.head(EXAMPLE_COMMENTS_LIMIT)[preview_columns])


def render_sentiment_metrics(statistics: SentimentStatistics) -> None:
    """
    Render sentiment metrics in columns.
    
    Args:
        statistics: Sentiment statistics to display
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Positive Comments", 
            statistics.positive_count,
            f"{statistics.positive_ratio:.1%}"
        )
    
    with col2:
        st.metric(
            "Neutral Comments", 
            statistics.neutral_count,
            f"{statistics.neutral_ratio:.1%}"
        )
    
    with col3:
        st.metric(
            "Negative Comments", 
            statistics.negative_count,
            f"{statistics.negative_ratio:.1%}"
        )


def render_confidence_metrics(statistics: SentimentStatistics) -> None:
    """
    Render confidence-related metrics.
    
    Args:
        statistics: Sentiment statistics
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Average Confidence", 
            f"{statistics.average_confidence:.3f}",
            f"{statistics.average_confidence:.1%}"
        )
    
    with col2:
        st.metric(
            "High Confidence Predictions",
            statistics.high_confidence_count,
            f"{statistics.high_confidence_ratio:.1%}"
        )


def render_sentiment_examples(df: pd.DataFrame, text_column: str) -> None:
    """
    Render examples for each sentiment category.
    
    Args:
        df: DataFrame with sentiment data
        text_column: Name of text column
    """
    st.subheader("Examples for each Sentiment Category")
    
    for sentiment_type in ['positive', 'neutral', 'negative']:
        sentiment_examples = df[df['sentiment'] == sentiment_type]
        
        if not sentiment_examples.empty:
            # Get top examples by confidence
            examples = sentiment_examples.sort_values(by='confidence', ascending=False).head(TOP_EXAMPLES_LIMIT)
            
            with st.expander(f"Examples for {sentiment_type} comments ({len(sentiment_examples)} total)"):
                for i, (_, example) in enumerate(examples.iterrows()):
                    st.write(f"**{i+1}.** {example[text_column]}")
                    st.write(f"   *Confidence: {example['confidence']:.3f}*")
                    
                    if 'original_line' in example and pd.notna(example['original_line']):
                        st.write(f"   *Original line: {example['original_line']}*")
                    
                    st.markdown("---")


def render_validation_ui(df: pd.DataFrame, text_column: str, config: SentimentAnalysisConfig) -> Optional[ValidationResult]:
    """
    Render validation UI for manual sentiment rating.
    
    Args:
        df: DataFrame with sentiment data
        text_column: Name of text column
        config: Analysis configuration
        
    Returns:
        ValidationResult if validation completed, None otherwise
    """
    st.subheader("Model Validation")
    st.write("Here you can verify the model quality by manually rating random comments.")
    
    # Button to select random comments
    if st.button("Select random comments for validation"):
        if len(df) > 0:
            sample_size = min(config.validation_samples, len(df))
            sample_indices = random.sample(range(len(df)), sample_size)
            st.session_state.random_indices = sample_indices
            st.session_state.user_ratings = {}
            st.rerun()
        else:
            st.warning("No comments available for sampling.")
            return None
    
    # Show validation form if samples selected
    if hasattr(st.session_state, 'random_indices'):
        return render_validation_form(df, text_column, st.session_state.random_indices)
    
    return None


def render_validation_form(df: pd.DataFrame, text_column: str, sample_indices: List[int]) -> Optional[ValidationResult]:
    """
    Render the validation form with random samples.
    
    Args:
        df: DataFrame with sentiment data
        text_column: Name of text column  
        sample_indices: List of sample indices
        
    Returns:
        ValidationResult if form submitted, None otherwise
    """
    with st.form("validation_form"):
        valid_samples = 0
        
        for i, idx in enumerate(sample_indices):
            if idx < len(df):
                valid_samples += 1
                comment = df.iloc[idx][text_column]
                model_sentiment = df.iloc[idx]['sentiment']
                model_confidence = df.iloc[idx]['confidence']
                
                st.write(f"**Comment {valid_samples}:** {comment}")
                st.write(f"*Model Sentiment:* {model_sentiment} (Confidence: {model_confidence:.3f})")
                
                user_sentiment = st.radio(
                    f"Your sentiment for comment {valid_samples}:",
                    ['positive', 'neutral', 'negative'],  # Use strings instead of enum values
                    key=f"sentiment_{i}"
                )
                st.session_state.user_ratings[idx] = user_sentiment
                st.markdown("---")
        
        submit_button = st.form_submit_button("Submit ratings")
        
        if submit_button and valid_samples > 0:
            return process_validation_results(df, text_column, st.session_state.user_ratings)
    
    return None


def process_validation_results(df: pd.DataFrame, text_column: str, user_ratings: Dict[int, str]) -> ValidationResult:
    """
    Process validation results and calculate accuracy.
    
    Args:
        df: DataFrame with sentiment data
        text_column: Name of text column
        user_ratings: Dictionary of user ratings by index
        
    Returns:
        ValidationResult object
    """
    matches = 0
    detailed_results = []
    
    for idx, user_rating in user_ratings.items():
        if idx < len(df):
            model_sentiment = df.iloc[idx]['sentiment']
            is_match = user_rating == model_sentiment
            
            if is_match:
                matches += 1
            
            detailed_results.append({
                'Comment': df.iloc[idx][text_column],
                'Model Sentiment': model_sentiment,
                'Your Rating': user_rating,
                'Agreement': is_match
            })
    
    accuracy = matches / len(user_ratings) if user_ratings else 0.0
    
    return ValidationResult(
        total_samples=len(user_ratings),
        matches=matches,
        accuracy=accuracy,
        detailed_results=detailed_results
    )


def render_validation_results(validation_result: ValidationResult) -> None:
    """
    Render validation results.
    
    Args:
        validation_result: Validation results to display
    """
    st.success(
        f"Agreement: {validation_result.matches} of {validation_result.total_samples} "
        f"({validation_result.agreement_percentage})"
    )
    
    # Show detailed results
    if validation_result.detailed_results:
        st.write("### Detailed Agreement Analysis")
        agreement_df = pd.DataFrame(validation_result.detailed_results)
        st.dataframe(agreement_df)


def render_confidence_filter_ui(df: pd.DataFrame, statistics: SentimentStatistics) -> pd.DataFrame:
    """
    Render confidence filtering UI and return filtered DataFrame.
    
    Args:
        df: DataFrame to filter
        statistics: Current statistics
        
    Returns:
        Filtered DataFrame
    """
    st.subheader("Filter by Confidence")
    
    min_confidence = st.slider(
        "Minimum confidence", 
        0.0, 1.0, DEFAULT_MIN_CONFIDENCE, 
        step=0.05
    )
    
    high_confidence_df = df[df['confidence'] >= min_confidence]
    
    st.write(
        f"**{len(high_confidence_df)} of {len(df)}** comments have confidence ≥ {min_confidence:.2f}"
    )
    
    # Show filtered sentiment distribution
    if len(high_confidence_df) > 0:
        st.write("### Sentiment Distribution (high confidence only)")
        filtered_stats = calculate_sentiment_statistics(high_confidence_df, min_confidence)
        fig = render_sentiment_distribution_chart(filtered_stats, "High Confidence Sentiment Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    return high_confidence_df


# =============================================================================
# MAIN API FUNCTIONS (BACKWARD COMPATIBLE)
# =============================================================================

def analyze_sentiment(df: pd.DataFrame, text_column: str, sentiment_pipeline: Callable) -> pd.DataFrame:
    """
    Perform sentiment analysis for all comments.
    
    Args:
        df: DataFrame with the comments
        text_column: Name of the column with the texts
        sentiment_pipeline: Sentiment analysis pipeline
        
    Returns:
        DataFrame with sentiment information
    """
    st.subheader("Analysis of Comments")
    
    # Render configuration UI
    config = render_analysis_config_ui()
    
    # Show data preview
    render_data_preview(df, text_column)
    
    # Filter by length
    df_filtered = df[df[text_column].fillna("").astype(str).str.len() > config.min_length]
    
    if len(df_filtered) == 0:
        st.warning("No comments remain after filtering.")
        st.stop()
    
    # Perform batch sentiment analysis
    result_df = perform_batch_sentiment_analysis(df_filtered, text_column, sentiment_pipeline, config)
    
    return result_df


def display_sentiment_results(df: pd.DataFrame, text_column: str) -> None:
    """
    Display the results of sentiment analysis.
    
    Args:
        df: DataFrame with sentiment information
        text_column: Name of the column with the texts
    """
    st.subheader("Analysis Results")
    
    # Calculate statistics
    statistics = calculate_sentiment_statistics(df)
    
    # Render confidence metrics
    render_confidence_metrics(statistics)
    
    # Render sentiment distribution
    st.write("### Sentiment Distribution")
    fig_sentiment = render_sentiment_distribution_chart(statistics)
    st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Render sentiment metrics
    render_sentiment_metrics(statistics)
    
    # Render confidence histogram
    st.write("### Distribution of Model Confidence")
    fig_confidence = render_confidence_histogram(df)
    st.plotly_chart(fig_confidence, use_container_width=True)
    
    # Render confidence vs sentiment analysis
    st.write("### Confidence by Sentiment Type")
    fig_box = render_confidence_vs_sentiment_chart(df)
    st.plotly_chart(fig_box, use_container_width=True)
    
    # Model validation
    config = SentimentAnalysisConfig()  # Use defaults for validation
    validation_result = render_validation_ui(df, text_column, config)
    
    if validation_result:
        render_validation_results(validation_result)
    
    # Confidence filtering
    filtered_df = render_confidence_filter_ui(df, statistics)
    
    # Examples for each category
    render_sentiment_examples(df, text_column)


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

def split_and_analyze(text: Any, sentiment_pipeline: Callable, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """
    Legacy function for backward compatibility.
    
    Args:
        text: Input text
        sentiment_pipeline: Sentiment pipeline
        chunk_size: Chunk size for processing
        
    Returns:
        Sentiment as string
    """
    return analyze_text_sentiment(text, sentiment_pipeline, chunk_size)


def calculate_confidence(text: Any, sentiment_pipeline: Callable, chunk_size: int = DEFAULT_CHUNK_SIZE) -> float:
    """
    Legacy function for backward compatibility.
    
    Args:
        text: Input text
        sentiment_pipeline: Sentiment pipeline
        chunk_size: Chunk size for processing
        
    Returns:
        Confidence score
    """
    return calculate_text_confidence(text, sentiment_pipeline, chunk_size)