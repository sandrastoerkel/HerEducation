"""
Modernized English special analysis module.

This module provides specialized analysis functionality for education, gender, and technology
topics with improved structure, type safety, and eliminated code duplication.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class AnalysisType(str, Enum):
    """Types of special analysis."""
    EDUCATION = "Education Topics"
    GENDER = "Gender Topics" 
    TECHNOLOGY = "Technology Topics"
    CUSTOM = "Custom Analysis"


class EmotionCategory(str, Enum):
    """Emotion categories for analysis."""
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


# Predefined keyword sets
EDUCATION_KEYWORDS = [
    "education", "school", "teacher", "teaching", "learning", "homework", 
    "classroom", "student", "university", "college", "curriculum", "academic"
]

GENDER_KEYWORDS = [
    "women", "girls", "equality", "gender", "discrimination", 
    "sexism", "feminism", "women's rights", "glass ceiling", "wage gap"
]

TECHNOLOGY_KEYWORDS = [
    "AI", "artificial intelligence", "ChatGPT", "GPT", "machine learning", 
    "technology", "computer", "algorithm", "automation", "robot", "digital"
]

# Emotion categorization
EMOTION_CATEGORIES = {
    EmotionCategory.POSITIVE: ['joy', 'love', 'surprise'],
    EmotionCategory.NEGATIVE: ['anger', 'sadness', 'fear', 'disgust'],
    EmotionCategory.NEUTRAL: ['neutral']
}

# Color schemes for consistent visualization
EMOTION_COLORS = {
    "anger": "#FF4444",      # Red
    "sadness": "#666666",    # Dark gray
    "disgust": "#808000",    # Olive
    "fear": "#FFA500",       # Orange
    "joy": "#FFD700",        # Gold
    "neutral": "#87CEEB",    # Light blue
    "surprise": "#800080",   # Purple
    "love": "#FFC0CB"        # Pink
}

PLOTLY_EMOTION_COLORS = {
    "anger": "#FF4444",
    "sadness": "#666666", 
    "disgust": "#808000",
    "fear": "#FFA500",
    "joy": "#FFD700",
    "neutral": "#87CEEB",
    "surprise": "#800080",
    "love": "#FFC0CB"
}

CATEGORY_COLORS = {
    EmotionCategory.POSITIVE: '#4CAF50',
    EmotionCategory.NEGATIVE: '#F44336',
    EmotionCategory.NEUTRAL: '#2196F3'
}

# Chart configuration
DEFAULT_CHART_HEIGHT = 500
COMPACT_CHART_HEIGHT = 400
FIGURE_SIZE = (10, 6)
LARGE_FIGURE_SIZE = (12, 6)
SMALL_FIGURE_SIZE = (6, 4)

# Display limits
MAX_SAMPLE_COMMENTS = 15
MAX_EDUCATION_COMMENTS = 10


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class EmotionStatistics:
    """Statistics for emotion analysis results."""
    total_comments: int
    positive_count: int
    negative_count: int
    neutral_count: int
    emotion_distribution: Dict[str, float]
    
    @property
    def positive_ratio(self) -> float:
        """Calculate ratio of positive emotions."""
        return self.positive_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def negative_ratio(self) -> float:
        """Calculate ratio of negative emotions."""
        return self.negative_count / self.total_comments if self.total_comments > 0 else 0.0
    
    @property
    def neutral_ratio(self) -> float:
        """Calculate ratio of neutral emotions."""
        return self.neutral_count / self.total_comments if self.total_comments > 0 else 0.0


@dataclass
class TopicDistribution:
    """Distribution of comments across topics."""
    topic_counts: Dict[int, int]
    topic_labels: Dict[int, str]
    
    @property
    def labeled_distribution(self) -> Dict[str, int]:
        """Get distribution with topic labels."""
        return {
            self.topic_labels.get(topic_id, f'Topic {topic_id}'): count 
            for topic_id, count in self.topic_counts.items()
        }


@dataclass
class AnalysisResult:
    """Complete result of special analysis."""
    analysis_type: AnalysisType
    keywords: List[str]
    filtered_data: pd.DataFrame
    emotion_stats: EmotionStatistics
    topic_distribution: TopicDistribution
    sample_comments: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if analysis found results."""
        return not self.filtered_data.empty
    
    @property
    def comment_count(self) -> int:
        """Get total number of comments found."""
        return len(self.filtered_data)


# =============================================================================
# CORE ANALYSIS FUNCTIONS
# =============================================================================

def get_topic_labels_for_analysis(topic_labels: Dict[int, str]) -> Dict[int, str]:
    """
    Get topic labels for analysis, preferring combined labels from session state.
    
    Args:
        topic_labels: Base topic labels
        
    Returns:
        Topic labels to use for analysis
    """
    if hasattr(st.session_state, 'combined_topic_labels'):
        return st.session_state.combined_topic_labels
    return topic_labels


def calculate_emotion_statistics(df: pd.DataFrame) -> EmotionStatistics:
    """
    Calculate comprehensive emotion statistics.
    
    Args:
        df: DataFrame with emotion data
        
    Returns:
        EmotionStatistics object
    """
    if df.empty:
        return EmotionStatistics(
            total_comments=0,
            positive_count=0,
            negative_count=0,
            neutral_count=0,
            emotion_distribution={}
        )
    
    total = len(df)
    
    # Calculate emotion distribution
    emotion_distribution = (df['dominant_emotion'].value_counts(normalize=True) * 100).to_dict()
    
    # Calculate category counts
    positive_count = sum(
        len(df[df['dominant_emotion'].isin(emotions)]) 
        for emotions in [EMOTION_CATEGORIES[EmotionCategory.POSITIVE]]
    )
    
    negative_count = sum(
        len(df[df['dominant_emotion'].isin(emotions)]) 
        for emotions in [EMOTION_CATEGORIES[EmotionCategory.NEGATIVE]]
    )
    
    neutral_count = sum(
        len(df[df['dominant_emotion'].isin(emotions)]) 
        for emotions in [EMOTION_CATEGORIES[EmotionCategory.NEUTRAL]]
    )
    
    return EmotionStatistics(
        total_comments=total,
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count,
        emotion_distribution=emotion_distribution
    )


def calculate_topic_distribution(df: pd.DataFrame, topic_labels: Dict[int, str]) -> TopicDistribution:
    """
    Calculate distribution of comments across topics.
    
    Args:
        df: DataFrame with topic data
        topic_labels: Dictionary with topic labels
        
    Returns:
        TopicDistribution object
    """
    if df.empty or 'topic' not in df.columns:
        return TopicDistribution(topic_counts={}, topic_labels=topic_labels)
    
    topic_counts = df['topic'].value_counts().to_dict()
    
    return TopicDistribution(
        topic_counts=topic_counts,
        topic_labels=topic_labels
    )


def filter_by_keywords(df: pd.DataFrame, keywords: List[str], text_column: str = 'clean_text') -> pd.DataFrame:
    """
    Filter DataFrame by keywords in text column.
    
    Args:
        df: DataFrame to filter
        keywords: List of keywords to search for
        text_column: Name of text column to search in
        
    Returns:
        Filtered DataFrame
    """
    if not keywords or df.empty:
        return pd.DataFrame()
    
    # Create regex pattern for keywords
    pattern = "|".join([kw.strip().lower() for kw in keywords])
    
    # Filter comments containing these terms
    return df[df[text_column].str.contains(pattern, case=False, na=False)]


def filter_by_topic_selection(df: pd.DataFrame, topic_ids: List[int]) -> pd.DataFrame:
    """
    Filter DataFrame by selected topic IDs.
    
    Args:
        df: DataFrame to filter
        topic_ids: List of topic IDs to include
        
    Returns:
        Filtered DataFrame
    """
    if not topic_ids or df.empty:
        return pd.DataFrame()
    
    return df[df['topic'].isin(topic_ids)]


def create_sample_comments(df: pd.DataFrame, text_column: str, topic_labels: Dict[int, str], max_comments: int = MAX_SAMPLE_COMMENTS) -> List[Dict[str, Any]]:
    """
    Create sample comments for display.
    
    Args:
        df: DataFrame with comments
        text_column: Name of text column
        topic_labels: Dictionary with topic labels
        max_comments: Maximum number of comments to return
        
    Returns:
        List of comment dictionaries
    """
    if df.empty:
        return []
    
    sample_comments = []
    
    for i, (_, row) in enumerate(df.head(max_comments).iterrows()):
        sample_comments.append({
            'index': i + 1,
            'text': row[text_column],
            'emotion': row['dominant_emotion'],
            'topic_id': row['topic'],
            'topic_label': topic_labels.get(row['topic'], 'Unnamed')
        })
    
    return sample_comments


def perform_keyword_analysis(
    df: pd.DataFrame, 
    keywords: List[str], 
    text_column: str, 
    topic_labels: Dict[int, str],
    analysis_type: AnalysisType
) -> AnalysisResult:
    """
    Perform keyword-based analysis.
    
    Args:
        df: DataFrame with data
        keywords: List of keywords to search for
        text_column: Name of text column
        topic_labels: Dictionary with topic labels
        analysis_type: Type of analysis
        
    Returns:
        AnalysisResult object
    """
    # Filter data by keywords
    filtered_df = filter_by_keywords(df, keywords, text_column)
    
    # Calculate statistics
    emotion_stats = calculate_emotion_statistics(filtered_df)
    topic_distribution = calculate_topic_distribution(filtered_df, topic_labels)
    sample_comments = create_sample_comments(filtered_df, text_column, topic_labels)
    
    return AnalysisResult(
        analysis_type=analysis_type,
        keywords=keywords,
        filtered_data=filtered_df,
        emotion_stats=emotion_stats,
        topic_distribution=topic_distribution,
        sample_comments=sample_comments
    )


def perform_topic_based_analysis(
    df: pd.DataFrame,
    topic_ids: List[int],
    text_column: str,
    topic_labels: Dict[int, str],
    analysis_type: AnalysisType
) -> AnalysisResult:
    """
    Perform topic-based analysis.
    
    Args:
        df: DataFrame with data
        topic_ids: List of topic IDs to analyze
        text_column: Name of text column
        topic_labels: Dictionary with topic labels
        analysis_type: Type of analysis
        
    Returns:
        AnalysisResult object
    """
    # Filter data by topics
    filtered_df = filter_by_topic_selection(df, topic_ids)
    
    # Calculate statistics
    emotion_stats = calculate_emotion_statistics(filtered_df)
    topic_distribution = calculate_topic_distribution(filtered_df, topic_labels)
    sample_comments = create_sample_comments(filtered_df, text_column, topic_labels, MAX_EDUCATION_COMMENTS)
    
    return AnalysisResult(
        analysis_type=analysis_type,
        keywords=[],  # No keywords for topic-based analysis
        filtered_data=filtered_df,
        emotion_stats=emotion_stats,
        topic_distribution=topic_distribution,
        sample_comments=sample_comments
    )


# =============================================================================
# CHART RENDERING FUNCTIONS
# =============================================================================

def render_emotion_distribution_chart(emotion_stats: EmotionStatistics, title: str, use_plotly: bool = True) -> Optional[go.Figure]:
    """
    Render emotion distribution chart.
    
    Args:
        emotion_stats: Emotion statistics
        title: Chart title
        use_plotly: Whether to use Plotly (True) or Matplotlib (False)
        
    Returns:
        Plotly figure or None if using Matplotlib
    """
    if emotion_stats.total_comments == 0:
        st.info("No data to display.")
        return None
    
    emotions = list(emotion_stats.emotion_distribution.keys())
    percentages = list(emotion_stats.emotion_distribution.values())
    
    if use_plotly:
        try:
            colors = [PLOTLY_EMOTION_COLORS.get(emotion, '#1f77b4') for emotion in emotions]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=emotions,
                    y=percentages,
                    marker_color=colors,
                    text=[f"{p:.1f}%" for p in percentages],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title=title,
                xaxis_title='Emotion',
                yaxis_title='Percentage (%)',
                height=DEFAULT_CHART_HEIGHT,
                showlegend=False
            )
            
            return fig
            
        except Exception:
            use_plotly = False
    
    if not use_plotly:
        # Fallback to Matplotlib
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        colors = [EMOTION_COLORS.get(emotion, 'blue') for emotion in emotions]
        
        ax.bar(emotions, percentages, color=colors)
        ax.set_title(title)
        ax.set_xlabel('Emotion')
        ax.set_ylabel('Percentage (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)  # Memory management
        
        return None


def render_topic_distribution_chart(topic_distribution: TopicDistribution, title: str, use_plotly: bool = True) -> Optional[go.Figure]:
    """
    Render topic distribution chart.
    
    Args:
        topic_distribution: Topic distribution data
        title: Chart title
        use_plotly: Whether to use Plotly (True) or Matplotlib (False)
        
    Returns:
        Plotly figure or None if using Matplotlib
    """
    labeled_dist = topic_distribution.labeled_distribution
    
    if not labeled_dist:
        st.info("No topic distribution data to display.")
        return None
    
    topics = list(labeled_dist.keys())
    counts = list(labeled_dist.values())
    
    if use_plotly:
        try:
            fig = go.Figure(data=[
                go.Bar(
                    x=topics,
                    y=counts,
                    text=counts,
                    textposition='auto',
                    marker_color='#1f77b4'
                )
            ])
            
            fig.update_layout(
                title=title,
                xaxis_title='Topic',
                yaxis_title='Number of Comments',
                height=DEFAULT_CHART_HEIGHT,
                xaxis={'categoryorder': 'total descending'}
            )
            
            return fig
            
        except Exception:
            use_plotly = False
    
    if not use_plotly:
        # Fallback to Matplotlib
        fig, ax = plt.subplots(figsize=LARGE_FIGURE_SIZE)
        ax.bar(topics, counts)
        ax.set_title(title)
        ax.set_xlabel('Topic')
        ax.set_ylabel('Number of Comments')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)  # Memory management
        
        return None


# =============================================================================
# UI RENDERING FUNCTIONS
# =============================================================================

def render_emotion_category_metrics(emotion_stats: EmotionStatistics) -> None:
    """
    Render emotion category metrics.
    
    Args:
        emotion_stats: Emotion statistics
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Positive", 
            f"{emotion_stats.positive_count} ({emotion_stats.positive_ratio:.1%})"
        )
    
    with col2:
        st.metric(
            "Negative", 
            f"{emotion_stats.negative_count} ({emotion_stats.negative_ratio:.1%})"
        )
    
    with col3:
        st.metric(
            "Neutral", 
            f"{emotion_stats.neutral_count} ({emotion_stats.neutral_ratio:.1%})"
        )


def render_sample_comments(sample_comments: List[Dict[str, Any]], title: str = "Sample Comments") -> None:
    """
    Render sample comments in an expandable section.
    
    Args:
        sample_comments: List of comment dictionaries
        title: Title for the section
    """
    if not sample_comments:
        st.info("No sample comments available.")
        return
    
    st.write(f"### {title}")
    
    with st.expander("Show comments"):
        for comment in sample_comments:
            st.write(f"**Comment {comment['index']}:**")
            st.write(f"💬  \"{comment['text']}\"")
            st.write(f"😐 Emotion: {comment['emotion']}")
            st.write(f"🏷️  Topic: {comment['topic_label']}")
            st.write("---")


def render_analysis_result(result: AnalysisResult) -> None:
    """
    Render complete analysis result.
    
    Args:
        result: AnalysisResult object
    """
    if not result.success:
        if result.keywords:
            st.warning(f"No comments found for keywords: {', '.join(result.keywords)}")
        else:
            st.warning("No comments found for the selected criteria.")
        return
    
    # Display comment count
    st.write(f"Found comments: **{result.comment_count}**")
    
    # Render emotion distribution chart
    chart_title = f'Emotional Response to {result.analysis_type.value}'
    if result.keywords:
        chart_title = f'Emotional Response to: {", ".join(result.keywords)}'
    
    fig = render_emotion_distribution_chart(result.emotion_stats, chart_title)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Render emotion category metrics
    st.write("### Summary of Emotional Responses")
    render_emotion_category_metrics(result.emotion_stats)
    
    # Render topic distribution if available
    if result.topic_distribution.topic_counts:
        topic_title = f'Distribution across Topics'
        if result.keywords:
            topic_title = f'Distribution of Comments about "{", ".join(result.keywords)}" across Topics'
        
        st.write("### Distribution across Topics")
        fig_topic = render_topic_distribution_chart(result.topic_distribution, topic_title)
        if fig_topic:
            st.plotly_chart(fig_topic, use_container_width=True)
    
    # Render sample comments
    render_sample_comments(result.sample_comments)


def render_keyword_input(
    label: str, 
    default_keywords: List[str], 
    key: Optional[str] = None
) -> List[str]:
    """
    Render keyword input field.
    
    Args:
        label: Label for input field
        default_keywords: Default keywords to display
        key: Unique key for widget
        
    Returns:
        List of keywords entered by user
    """
    st.write(f"Keywords for search: {', '.join(default_keywords)}")
    
    custom_keywords_str = st.text_input(
        label,
        value=", ".join(default_keywords),
        key=key
    )
    
    if custom_keywords_str:
        return [kw.strip().lower() for kw in custom_keywords_str.split(",")]
    
    return default_keywords


def render_topic_multiselect(
    topic_labels: Dict[int, str],
    detected_topics: List[int],
    keywords: List[str]
) -> List[int]:
    """
    Render topic multiselect widget.
    
    Args:
        topic_labels: Dictionary with topic labels
        detected_topics: Automatically detected topic IDs
        keywords: Keywords used for detection
        
    Returns:
        List of selected topic IDs
    """
    if not detected_topics:
        st.warning(f"No topics automatically detected for keywords: {', '.join(keywords)}. Please select relevant topics.")
    
    all_topics = sorted(list(topic_labels.keys()))
    
    selected_topics = st.multiselect(
        "Select relevant topics:",
        options=all_topics,
        default=detected_topics,
        format_func=lambda x: topic_labels.get(x, 'Unnamed')
    )
    
    return selected_topics


# =============================================================================
# SPECIALIZED ANALYSIS FUNCTIONS
# =============================================================================

def analyze_education_topics(
    df: pd.DataFrame,
    text_column: str,
    topic_labels_for_analysis: Dict[int, str]
) -> None:
    """
    Analyze education-related topics.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of text column
        topic_labels_for_analysis: Topic labels for analysis
    """
    st.write("### Emotional Response to Education Topics")
    
    # Identify education-related topics automatically
    education_topic_ids = []
    for topic_id, label in topic_labels_for_analysis.items():
        if any(keyword in label.lower() for keyword in EDUCATION_KEYWORDS):
            education_topic_ids.append(topic_id)
    
    # Allow manual topic selection
    selected_topics = render_topic_multiselect(
        topic_labels_for_analysis, 
        education_topic_ids, 
        EDUCATION_KEYWORDS
    )
    
    if selected_topics:
        # Perform analysis
        result = perform_topic_based_analysis(
            df, 
            selected_topics, 
            text_column, 
            topic_labels_for_analysis,
            AnalysisType.EDUCATION
        )
        
        # Render results
        render_analysis_result(result)
    else:
        st.warning("Please select at least one education topic.")


def analyze_gender_topics(
    df: pd.DataFrame,
    text_column: str,
    topic_labels_for_analysis: Dict[int, str]
) -> None:
    """
    Analyze gender-related topics.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of text column
        topic_labels_for_analysis: Topic labels for analysis
    """
    st.write("### Analysis of Gender Topics")
    
    # Render keyword input
    keywords = render_keyword_input(
        "Adjust keywords (comma-separated):",
        GENDER_KEYWORDS
    )
    
    if keywords:
        # Perform analysis
        result = perform_keyword_analysis(
            df,
            keywords,
            text_column,
            topic_labels_for_analysis,
            AnalysisType.GENDER
        )
        
        # Render results
        render_analysis_result(result)


def analyze_technology_topics(
    df: pd.DataFrame,
    text_column: str,
    topic_labels_for_analysis: Dict[int, str]
) -> None:
    """
    Analyze technology-related topics.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of text column
        topic_labels_for_analysis: Topic labels for analysis
    """
    st.write("### Analysis of Technology Topics")
    
    # Render keyword input
    keywords = render_keyword_input(
        "Adjust keywords (comma-separated):",
        TECHNOLOGY_KEYWORDS,
        key="tech_keywords"
    )
    
    if keywords:
        # Perform analysis
        result = perform_keyword_analysis(
            df,
            keywords,
            text_column,
            topic_labels_for_analysis,
            AnalysisType.TECHNOLOGY
        )
        
        # Render results
        render_analysis_result(result)


def analyze_custom_topics(
    df: pd.DataFrame,
    text_column: str,
    topic_labels_for_analysis: Dict[int, str]
) -> None:
    """
    Perform custom analysis based on user input.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of text column
        topic_labels_for_analysis: Topic labels for analysis
    """
    st.write("### Custom Analysis")
    st.write("Select your own criteria for a specific analysis.")
    
    # Input field for keywords
    custom_search = st.text_input("Enter keywords (comma-separated):")
    
    if custom_search:
        # Convert keywords to list
        custom_keywords = [kw.strip().lower() for kw in custom_search.split(",")]
        
        # Perform analysis
        result = perform_keyword_analysis(
            df,
            custom_keywords,
            text_column,
            topic_labels_for_analysis,
            AnalysisType.CUSTOM
        )
        
        # Render results
        render_analysis_result(result)


# =============================================================================
# MAIN API FUNCTIONS (BACKWARD COMPATIBLE)
# =============================================================================

def display_special_analysis(df: pd.DataFrame, text_column: str, topic_labels: Dict[int, str]) -> None:
    """
    Show special analyses for education and gender topics.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of column with texts
        topic_labels: Dictionary with topic labels
    """
    st.subheader("Special Analyses for Specific Topics")
    
    # Check required columns
    if 'topic' not in df.columns or 'dominant_emotion' not in df.columns:
        st.warning("Special analyses require both topic and emotion data, which are not available.")
        return
    
    # Get topic labels for analysis
    topic_labels_for_analysis = get_topic_labels_for_analysis(topic_labels)
    
    # Create analysis tabs
    analysis_tabs = st.tabs([
        AnalysisType.EDUCATION.value,
        AnalysisType.GENDER.value, 
        AnalysisType.TECHNOLOGY.value,
        AnalysisType.CUSTOM.value
    ])
    
    # Education topics analysis
    with analysis_tabs[0]:
        analyze_education_topics(df, text_column, topic_labels_for_analysis)
    
    # Gender topics analysis
    with analysis_tabs[1]:
        analyze_gender_topics(df, text_column, topic_labels_for_analysis)
    
    # Technology topics analysis
    with analysis_tabs[2]:
        analyze_technology_topics(df, text_column, topic_labels_for_analysis)
    
    # Custom analysis
    with analysis_tabs[3]:
        analyze_custom_topics(df, text_column, topic_labels_for_analysis)


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

def display_education_analysis(df: pd.DataFrame, text_column: str, topic_labels_for_analysis: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """
    Legacy function for backward compatibility.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of text column
        topic_labels_for_analysis: Topic labels for analysis
        emotion_colors: Emotion colors (ignored in modernized version)
    """
    analyze_education_topics(df, text_column, topic_labels_for_analysis)


def display_gender_analysis(df: pd.DataFrame, text_column: str, topic_labels_for_analysis: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """
    Legacy function for backward compatibility.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of text column
        topic_labels_for_analysis: Topic labels for analysis
        emotion_colors: Emotion colors (ignored in modernized version)
    """
    analyze_gender_topics(df, text_column, topic_labels_for_analysis)


def display_technology_analysis(df: pd.DataFrame, text_column: str, topic_labels_for_analysis: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """
    Legacy function for backward compatibility.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of text column
        topic_labels_for_analysis: Topic labels for analysis
        emotion_colors: Emotion colors (ignored in modernized version)
    """
    analyze_technology_topics(df, text_column, topic_labels_for_analysis)


def display_custom_analysis(df: pd.DataFrame, text_column: str, topic_labels_for_analysis: Dict[int, str], emotion_colors: Dict[str, str]) -> None:
    """
    Legacy function for backward compatibility.
    
    Args:
        df: DataFrame with comment data
        text_column: Name of text column
        topic_labels_for_analysis: Topic labels for analysis
        emotion_colors: Emotion colors (ignored in modernized version)
    """
    analyze_custom_topics(df, text_column, topic_labels_for_analysis)