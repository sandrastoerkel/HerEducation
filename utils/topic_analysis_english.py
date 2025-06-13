"""
Modernized English topic analysis module.

This module provides topic analysis functionality using BERTopic with improved
structure, type safety, and interactive visualizations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import re
import ast
import traceback
from wordcloud import WordCloud
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# CONSTANTS AND ENUMS  
# =============================================================================

# Text processing constants
MIN_TEXT_LENGTH = 10
MIN_WORD_LENGTH = 2
MIN_COMMENTS_FOR_ANALYSIS = 10

# Topic analysis constants  
DEFAULT_N_WORDS = 5
DEFAULT_LABEL_WORDS = 3
TOP_TOPICS_DISPLAY = 5
TOP_TOPICS_TABLE = 10
WORDCLOUD_WIDTH = 400
WORDCLOUD_HEIGHT = 400

# UI constants
TEXTAREA_HEIGHT = 300
MAX_LABEL_WORDS = 5
MIN_LABEL_WORDS = 1

# Chart configuration
CHART_HEIGHT = 600
FIGURE_SIZE = (14, 7)

# Sentiment colors for topic analysis
SENTIMENT_COLORS = {
    'positive': 'green',
    'neutral': 'gray', 
    'negative': 'red'
}

PLOTLY_SENTIMENT_COLORS = {
    'positive': '#4CAF50',
    'neutral': '#9E9E9E',
    'negative': '#F44336'
}

# Error messages
ERROR_INSUFFICIENT_DATA = "Too few comments for meaningful topic analysis. At least 10 longer comments are needed."
ERROR_MODEL_LOADING = "BERTopic model could not be loaded. Topic analysis will be skipped."
ERROR_TOPIC_ANALYSIS = "Topic analysis could not be performed."


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class TopicAnalysisConfig:
    """Configuration for topic analysis."""
    min_text_length: int = MIN_TEXT_LENGTH
    min_word_length: int = MIN_WORD_LENGTH
    n_words: int = DEFAULT_N_WORDS
    label_words: int = DEFAULT_LABEL_WORDS
    top_topics_display: int = TOP_TOPICS_DISPLAY


@dataclass
class TopicData:
    """Data structure for topic information."""
    topic_id: int
    count: int
    name: str
    top_words: str
    smart_label: str
    manual_designation: str = ""
    
    @property
    def display_name(self) -> str:
        """Get the best available name for display."""
        return self.manual_designation or self.smart_label or self.name or f"Topic {self.topic_id}"


@dataclass 
class TopicAnalysisResult:
    """Complete result of topic analysis."""
    dataframe: pd.DataFrame
    topic_model: Any
    topic_info: pd.DataFrame
    topic_df: pd.DataFrame
    topic_labels: Dict[int, str]
    topic_data: List[TopicData] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if analysis was successful."""
        return (
            self.topic_model is not None and 
            self.topic_info is not None and 
            not self.topic_df.empty
        )
    
    @property
    def valid_topics(self) -> List[int]:
        """Get list of valid topic IDs (excluding -1)."""
        return [topic.topic_id for topic in self.topic_data if topic.topic_id != -1]


@dataclass
class WordCloudData:
    """Data for WordCloud generation."""
    topic_id: int
    word_frequencies: Dict[str, float]
    label: str


# =============================================================================
# TEXT PROCESSING FUNCTIONS
# =============================================================================

def clean_text_for_topics(text: Any) -> str:
    """
    Clean text for topic analysis with robust error handling.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text string
    """
    if pd.isna(text) or text is None or text == "":
        return ""
    
    text = str(text)
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    # Convert to lowercase
    text = text.lower()
    
    # Try to remove stop words if NLTK is available
    try:
        import nltk
        from nltk.corpus import stopwords
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        stop_words = set(stopwords.words('english'))
        text = ' '.join([
            word for word in text.split() 
            if word not in stop_words and len(word) > MIN_WORD_LENGTH
        ])
        
    except Exception:
        # If NLTK is not available, just filter short words
        text = ' '.join([
            word for word in text.split() 
            if len(word) > MIN_WORD_LENGTH
        ])
            
    return text


def validate_text_data(df: pd.DataFrame, text_column: str) -> Tuple[pd.DataFrame, bool]:
    """
    Validate and prepare text data for topic analysis.
    
    Args:
        df: Input DataFrame
        text_column: Name of text column
        
    Returns:
        Tuple of (filtered_df, is_valid)
    """
    # Clean text for topic modeling
    df['clean_text'] = df[text_column].apply(clean_text_for_topics)
    
    # Extract valid texts for topic modeling
    topic_df = df[df['clean_text'].str.len() > MIN_TEXT_LENGTH].reset_index(drop=True)
    
    is_valid = len(topic_df) >= MIN_COMMENTS_FOR_ANALYSIS
    
    return topic_df, is_valid


# =============================================================================
# TOPIC MODEL FUNCTIONS
# =============================================================================

def load_topic_model():
    """
    Load BERTopic model with error handling.
    
    Returns:
        Loaded model or None if failed
    """
    try:
        from models.model_loader_english import load_bertopic_model
        return load_bertopic_model()
    except Exception as e:
        st.error(f"Error loading BERTopic model: {str(e)}")
        return None


def train_topic_model(topic_model: Any, texts: List[str]) -> Tuple[List[int], Any]:
    """
    Train topic model on texts.
    
    Args:
        topic_model: BERTopic model instance
        texts: List of texts to train on
        
    Returns:
        Tuple of (topics, probabilities)
    """
    try:
        topics, probs = topic_model.fit_transform(texts)
        return topics, probs
    except Exception as e:
        st.error(f"Error training BERTopic model: {str(e)}")
        st.error(traceback.format_exc())
        raise


def extract_topic_keywords(topic_id: int, topic_model: Any, n_words: int = DEFAULT_N_WORDS) -> str:
    """
    Extract top keywords for a specific topic.
    
    Args:
        topic_id: ID of the topic
        topic_model: Trained topic model
        n_words: Number of words to extract
        
    Returns:
        Comma-separated string of keywords
    """
    try:
        words = topic_model.get_topic(topic_id)
        return ", ".join([word for word, _ in words[:n_words]])
    except Exception as e:
        return f"Error: {str(e)}"


def generate_topic_label(topic_id: int, topic_model: Any, n_words: int = DEFAULT_LABEL_WORDS) -> str:
    """
    Generate a readable label for a topic based on top words.
    
    Args:
        topic_id: ID of the topic
        topic_model: Trained topic model
        n_words: Number of words to include in label
        
    Returns:
        Generated topic label
    """
    try:
        top_words = topic_model.get_topic(topic_id)
        if not top_words:
            return "Other"
        return " / ".join([word for word, _ in top_words[:n_words]])
    except Exception:
        return f"Topic {topic_id}"


def load_smart_topic_labels(topic_model: Any) -> Dict[int, str]:
    """
    Load smart topic labels using external labeling module.
    
    Args:
        topic_model: Trained topic model
        
    Returns:
        Dictionary mapping topic IDs to smart labels
    """
    try:
        from utils.topic_labeling_english import generate_smart_topic_labels
        return generate_smart_topic_labels(topic_model)
    except Exception as e:
        st.warning(f"Could not load smart topic labels: {str(e)}")
        return {}


# =============================================================================
# WORDCLOUD FUNCTIONS
# =============================================================================

def create_wordcloud_data(topic_id: int, topic_model: Any, label: str) -> Optional[WordCloudData]:
    """
    Create WordCloud data for a topic.
    
    Args:
        topic_id: ID of the topic
        topic_model: Trained topic model
        label: Topic label
        
    Returns:
        WordCloudData object or None if failed
    """
    try:
        words = topic_model.get_topic(topic_id)
        word_frequencies = {word: weight for word, weight in words}
        
        return WordCloudData(
            topic_id=topic_id,
            word_frequencies=word_frequencies,
            label=label
        )
    except Exception as e:
        st.error(f"Error creating WordCloud data for topic {topic_id}: {str(e)}")
        return None


def generate_wordcloud_image(wordcloud_data: WordCloudData) -> Optional[WordCloud]:
    """
    Generate WordCloud image from data.
    
    Args:
        wordcloud_data: WordCloud data
        
    Returns:
        WordCloud object or None if failed
    """
    try:
        wc = WordCloud(
            width=WORDCLOUD_WIDTH, 
            height=WORDCLOUD_HEIGHT, 
            background_color='white'
        )
        wc.generate_from_frequencies(wordcloud_data.word_frequencies)
        return wc
    except Exception as e:
        st.error(f"Error generating WordCloud: {str(e)}")
        return None


# =============================================================================
# DATA PROCESSING FUNCTIONS
# =============================================================================

def create_topic_data_list(topic_info: pd.DataFrame, topic_model: Any, topic_labels: Dict[int, str]) -> List[TopicData]:
    """
    Create list of TopicData objects from topic information.
    
    Args:
        topic_info: DataFrame with topic information
        topic_model: Trained topic model
        topic_labels: Dictionary with smart labels
        
    Returns:
        List of TopicData objects
    """
    topic_data = []
    
    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        
        topic_data.append(TopicData(
            topic_id=topic_id,
            count=row["Count"],
            name=row["Name"],
            top_words=extract_topic_keywords(topic_id, topic_model),
            smart_label=topic_labels.get(topic_id, "Unnamed")
        ))
    
    return topic_data


def merge_topics_to_dataframe(df: pd.DataFrame, topic_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge topic assignments back to original DataFrame.
    
    Args:
        df: Original DataFrame
        topic_df: DataFrame with topic assignments
        
    Returns:
        DataFrame with topic information
    """
    # Create topic mapping
    topic_map = dict(zip(topic_df.index, topic_df['topic']))
    df['topic'] = df.index.map(lambda x: topic_map.get(x, -1))
    
    return df


def parse_topic_dictionary(dict_string: str) -> Optional[Dict[int, str]]:
    """
    Parse topic dictionary from string input.
    
    Args:
        dict_string: String representation of dictionary
        
    Returns:
        Parsed dictionary or None if failed
    """
    try:
        custom_topic_labels = ast.literal_eval(dict_string)
        
        if isinstance(custom_topic_labels, dict):
            # Convert all keys to integers
            return {int(k): v for k, v in custom_topic_labels.items()}
        else:
            st.error("Input is not a valid dictionary.")
            return None
            
    except Exception as e:
        st.error(f"Error parsing dictionary: {str(e)}")
        st.error(traceback.format_exc())
        return None


# =============================================================================
# CHART RENDERING FUNCTIONS
# =============================================================================

def render_topic_overview_table(topic_data: List[TopicData], max_rows: int = TOP_TOPICS_TABLE) -> None:
    """
    Render topic overview table.
    
    Args:
        topic_data: List of topic data
        max_rows: Maximum number of rows to display
    """
    # Create DataFrame for display
    display_data = []
    
    for topic in sorted(topic_data, key=lambda x: x.count, reverse=True):
        if topic.topic_id != -1:  # Filter outliers
            display_data.append({
                "Topic": topic.topic_id,
                "Count": topic.count,
                "Name": topic.name,
                "Top Words": topic.top_words,
                "Smart Label": topic.smart_label,
                "Manual Designation": topic.manual_designation
            })
    
    # Convert to DataFrame and display
    if display_data:
        df_display = pd.DataFrame(display_data)
        st.dataframe(df_display.head(max_rows))
    else:
        st.info("No topics to display.")


def render_wordclouds(topic_data: List[TopicData], topic_model: Any, max_topics: int = TOP_TOPICS_DISPLAY) -> None:
    """
    Render WordClouds for top topics.
    
    Args:
        topic_data: List of topic data
        topic_model: Trained topic model
        max_topics: Maximum number of WordClouds to display
    """
    # Get top topics (excluding outliers)
    valid_topics = [t for t in topic_data if t.topic_id != -1]
    top_topics = sorted(valid_topics, key=lambda x: x.count, reverse=True)[:max_topics]
    
    if not top_topics:
        st.info("No topics available for WordCloud generation.")
        return
    
    # Create columns for WordClouds
    cols = st.columns(min(len(top_topics), max_topics))
    
    for i, topic in enumerate(top_topics):
        with cols[i % len(cols)]:
            st.write(f"**{topic.display_name}**")
            
            # Create WordCloud data
            wc_data = create_wordcloud_data(topic.topic_id, topic_model, topic.display_name)
            
            if wc_data:
                # Generate WordCloud
                wc = generate_wordcloud_image(wc_data)
                
                if wc:
                    # Display WordCloud
                    fig, ax = plt.subplots()
                    ax.imshow(wc, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
                    plt.close(fig)  # Memory management


def render_label_suggestions_table(topic_data: List[TopicData], topic_model: Any, n_words: int) -> None:
    """
    Render table with label suggestions.
    
    Args:
        topic_data: List of topic data
        topic_model: Trained topic model
        n_words: Number of words for label generation
    """
    # Create DataFrame for label suggestions
    display_data = []
    
    for topic in sorted(topic_data, key=lambda x: x.count, reverse=True):
        if topic.topic_id != -1:  # Filter outliers
            display_data.append({
                "Topic": topic.topic_id,
                "Count": topic.count,
                "Label Suggestion": generate_topic_label(topic.topic_id, topic_model, n_words),
                "Smart Label": topic.smart_label
            })
    
    if display_data:
        df_display = pd.DataFrame(display_data)
        st.dataframe(df_display)
    else:
        st.info("No topics available for label suggestions.")


def render_sentiment_by_topic_chart(df: pd.DataFrame, topic_labels: Dict[int, str]) -> None:
    """
    Render sentiment distribution by topic chart.
    
    Args:
        df: DataFrame with sentiment and topic data
        topic_labels: Dictionary with topic labels
    """
    if 'sentiment' not in df.columns or 'topic' not in df.columns:
        st.warning("Sentiment or topic information missing for this analysis.")
        return
    
    try:
        # Filter out outlier topics
        topic_sentiment_df = df[df['topic'] != -1]
        
        if topic_sentiment_df.empty:
            st.info("No valid topics found for sentiment analysis.")
            return
        
        # Aggregate sentiment per topic
        sentiment_by_topic = topic_sentiment_df.groupby('topic')['sentiment'].value_counts().unstack(fill_value=0)
        
        # Normalize to percentages
        sentiment_by_topic_pct = sentiment_by_topic.div(sentiment_by_topic.sum(axis=1), axis=0) * 100
        
        # Apply topic labels
        combined_labels = get_combined_topic_labels(topic_labels)
        new_index = [combined_labels.get(idx, f'Topic {idx}') for idx in sentiment_by_topic_pct.index]
        sentiment_by_topic_pct.index = new_index
        
        # Create Plotly visualization
        try:
            plot_data = []
            for topic in sentiment_by_topic_pct.index:
                for sentiment, value in sentiment_by_topic_pct.loc[topic].items():
                    plot_data.append({
                        'Topic': topic,
                        'Sentiment': sentiment,
                        'Percent': value
                    })
            
            plot_df = pd.DataFrame(plot_data)
            
            fig = px.bar(
                plot_df,
                x='Topic',
                y='Percent',
                color='Sentiment',
                color_discrete_map=PLOTLY_SENTIMENT_COLORS,
                title='Sentiment Distribution by Topics'
            )
            
            fig.update_layout(
                height=CHART_HEIGHT,
                xaxis={'categoryorder': 'total descending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception:
            # Fallback to Matplotlib
            fig, ax = plt.subplots(figsize=FIGURE_SIZE)
            sentiment_by_topic_pct.plot(
                kind='bar', 
                stacked=True, 
                ax=ax,
                color=[SENTIMENT_COLORS[col] for col in sentiment_by_topic_pct.columns if col in SENTIMENT_COLORS]
            )
            plt.title('Sentiment Distribution by Topics')
            plt.xlabel('Topic')
            plt.ylabel('Percentage (%)')
            plt.xticks(rotation=45, ha='right')
            plt.legend(title='Sentiment')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)  # Memory management
        
        # Display data table
        st.write("Sentiment distribution by topics (absolute):")
        sentiment_by_topic_display = sentiment_by_topic.copy()
        sentiment_by_topic_display.index = new_index
        st.dataframe(sentiment_by_topic_display)
        
    except Exception as e:
        st.error(f"Error in sentiment-per-topic analysis: {str(e)}")
        st.error(traceback.format_exc())


# =============================================================================
# UI RENDERING FUNCTIONS
# =============================================================================

def render_topic_dictionary_editor(topic_data: List[TopicData]) -> None:
    """
    Render topic dictionary editor UI.
    
    Args:
        topic_data: List of topic data
    """
    st.write("### Predefined Topic Dictionary")
    
    # Generate topic labels for the combined session state
    combined_labels = get_combined_topic_labels({t.topic_id: t.smart_label for t in topic_data})
    
    # Generate code for dictionary
    topic_dict_str = "topic_labels = {\n"
    for topic in sorted(topic_data, key=lambda x: x.topic_id):
        if topic.topic_id != -1:  # Ignore outlier topic
            label = combined_labels.get(topic.topic_id, topic.smart_label)
            topic_dict_str += f"    {topic.topic_id}: \"{label}\",\n"
    topic_dict_str += "}"
    
    # Show example dictionary
    st.code(topic_dict_str)
    
    # Input field for dictionary
    user_topic_dict_str = st.text_area(
        "Enter topic dictionary (Python format):", 
        value=topic_dict_str, 
        height=TEXTAREA_HEIGHT
    )
    
    if st.button("Accept Topic Dictionary"):
        parsed_dict = parse_topic_dictionary(user_topic_dict_str)
        if parsed_dict:
            st.session_state.custom_topic_labels = parsed_dict
            st.success("Topic dictionary successfully accepted!")


def render_individual_topic_editor(topic_data: List[TopicData]) -> None:
    """
    Render individual topic editor form.
    
    Args:
        topic_data: List of topic data
    """
    # Get valid topics for selection
    valid_topics = [t for t in topic_data if t.topic_id != -1]
    
    if not valid_topics:
        st.info("No topics available for editing.")
        return
    
    with st.form("topic_naming_form"):
        # Topic selection dropdown
        topic_options = [t.topic_id for t in valid_topics]
        
        selected_topic = st.selectbox(
            "Select topic:",
            options=topic_options,
            format_func=lambda x: f"Topic {x}: {next((t.display_name for t in valid_topics if t.topic_id == x), 'Unknown')}"
        )
        
        # Get current label
        current_label = ""
        if hasattr(st.session_state, 'custom_topic_labels'):
            current_label = st.session_state.custom_topic_labels.get(selected_topic, "")
        
        if not current_label:
            # Use smart label as default
            current_label = next((t.smart_label for t in valid_topics if t.topic_id == selected_topic), "")
        
        # Input field for custom designation
        custom_label = st.text_input("Custom designation:", value=current_label)
        
        # Submit button
        submit_button = st.form_submit_button("Save designation")
        
        if submit_button:
            # Initialize custom labels if not exists
            if not hasattr(st.session_state, 'custom_topic_labels'):
                st.session_state.custom_topic_labels = {}
            
            st.session_state.custom_topic_labels[selected_topic] = custom_label
            st.success(f"Designation for Topic {selected_topic} saved!")


def render_custom_designations_table(topic_data: List[TopicData], topic_model: Any) -> None:
    """
    Render table showing custom designations.
    
    Args:
        topic_data: List of topic data
        topic_model: Trained topic model
    """
    if not hasattr(st.session_state, 'custom_topic_labels') or not st.session_state.custom_topic_labels:
        return
    
    st.write("### Saved Designations")
    
    # Create DataFrame for display
    custom_labels_data = []
    
    for topic in topic_data:
        if topic.topic_id in st.session_state.custom_topic_labels and topic.topic_id != -1:
            custom_labels_data.append({
                "Topic": topic.topic_id,
                "Label Suggestion": generate_topic_label(topic.topic_id, topic_model, DEFAULT_LABEL_WORDS),
                "Smart Label": topic.smart_label,
                "Custom Designation": st.session_state.custom_topic_labels[topic.topic_id]
            })
    
    if custom_labels_data:
        custom_labels_df = pd.DataFrame(custom_labels_data)
        st.dataframe(custom_labels_df)
        
        # Update combined labels in session state
        update_combined_topic_labels({t.topic_id: t.smart_label for t in topic_data})


def get_combined_topic_labels(base_labels: Dict[int, str]) -> Dict[int, str]:
    """
    Get combined topic labels from base labels and custom labels.
    
    Args:
        base_labels: Base topic labels
        
    Returns:
        Combined labels dictionary
    """
    combined_labels = base_labels.copy()
    
    if hasattr(st.session_state, 'custom_topic_labels'):
        combined_labels.update(st.session_state.custom_topic_labels)
    
    return combined_labels


def update_combined_topic_labels(base_labels: Dict[int, str]) -> None:
    """
    Update combined topic labels in session state.
    
    Args:
        base_labels: Base topic labels
    """
    combined_labels = get_combined_topic_labels(base_labels)
    st.session_state.combined_topic_labels = combined_labels


# =============================================================================
# MAIN API FUNCTIONS (BACKWARD COMPATIBLE)
# =============================================================================

def prepare_topic_analysis(df: pd.DataFrame, text_column: str) -> Tuple[pd.DataFrame, Any, Any, Any, Dict[int, str]]:
    """
    Prepare data for topic analysis and train the topic model.
    
    Args:
        df: DataFrame with the comments
        text_column: Name of column with texts
        
    Returns:
        Tuple with (df, topic_model, topic_info, topic_df, topic_labels)
    """
    try:
        with st.spinner("Texts are being prepared for topic and emotion analysis..."):
            # Validate and prepare text data
            topic_df, is_valid = validate_text_data(df, text_column)
            
            if not is_valid:
                st.warning(ERROR_INSUFFICIENT_DATA)
                return df, None, None, None, None
            
            # Load topic model
            topic_model = load_topic_model()
            
            if topic_model is None:
                st.warning(ERROR_MODEL_LOADING)
                return df, None, None, None, None
            
            with st.spinner("BERTopic model is being trained..."):
                try:
                    # Train model
                    topics, probs = train_topic_model(topic_model, topic_df['clean_text'])
                    
                    # Add topics to data structure
                    topic_df['topic'] = topics
                    
                    # Merge topics back to original DataFrame
                    df = merge_topics_to_dataframe(df, topic_df)
                    
                    # Get topic info
                    topic_info = topic_model.get_topic_info()
                    
                    # Generate smart topic labels
                    topic_labels = load_smart_topic_labels(topic_model)
                    
                    return df, topic_model, topic_info, topic_df, topic_labels
                    
                except Exception as e:
                    st.error(f"Error training BERTopic model: {str(e)}")
                    st.error(traceback.format_exc())
                    return df, None, None, None, None
                    
    except Exception as e:
        st.error(f"Error preparing topic analysis: {str(e)}")
        st.error(traceback.format_exc())
        return df, None, None, None, None


def display_topic_analysis(
    df: pd.DataFrame, 
    topic_model: Any, 
    topic_df: pd.DataFrame, 
    topic_info: pd.DataFrame, 
    topic_labels: Dict[int, str]
) -> None:
    """
    Show the results of topic analysis.
    
    Args:
        df: DataFrame with the comments
        topic_model: Trained BERTopic model
        topic_df: DataFrame with topics
        topic_info: Topic information
        topic_labels: Dictionary with topic labels
    """
    st.subheader("Topic Analysis with BERTopic")
    
    if topic_model is None or topic_df is None or topic_info is None:
        st.warning(ERROR_TOPIC_ANALYSIS)
        return
    
    # Create topic data structure
    topic_data = create_topic_data_list(topic_info, topic_model, topic_labels)
    
    # 1. Topic Overview
    st.write("### Topic Overview")
    render_topic_overview_table(topic_data)
    
    # 2. WordClouds for top topics
    st.write("### WordClouds for Top Topics")
    render_wordclouds(topic_data, topic_model)
    
    # 3. Topic label suggestions
    st.write("### Label Suggestions for Topics")
    
    # Number of words slider
    top_n_words = st.slider(
        "Number of words for label", 
        MIN_LABEL_WORDS, 
        MAX_LABEL_WORDS, 
        DEFAULT_LABEL_WORDS
    )
    
    render_label_suggestions_table(topic_data, topic_model, top_n_words)
    
    # 4. Manual naming of topics
    st.write("### Manual Naming of Topics")
    st.write("You can manually name topics here and use these names for further analyses.")
    
    # Topic dictionary editor
    render_topic_dictionary_editor(topic_data)
    
    # Individual topic editor
    render_individual_topic_editor(topic_data)
    
    # Display custom designations
    render_custom_designations_table(topic_data, topic_model)
    
    # 5. Sentiment per topic
    display_sentiment_by_topic(df, topic_labels)


def display_sentiment_by_topic(df: pd.DataFrame, topic_labels: Dict[int, str]) -> None:
    """
    Show sentiment distribution per topic.
    
    Args:
        df: DataFrame with sentiment and topic data
        topic_labels: Dictionary with topic labels
    """
    st.write("### Sentiment per Topic")
    render_sentiment_by_topic_chart(df, topic_labels)


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

def clean_text(text: Any) -> str:
    """
    Legacy function for backward compatibility.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text string
    """
    return clean_text_for_topics(text)


def get_keywords(topic_id: int, topic_model: Any, n_words: int = DEFAULT_N_WORDS) -> str:
    """
    Legacy function for backward compatibility.
    
    Args:
        topic_id: ID of the topic
        topic_model: Trained topic model
        n_words: Number of words to extract
        
    Returns:
        Comma-separated string of keywords
    """
    return extract_topic_keywords(topic_id, topic_model, n_words)


def generate_wordcloud(topic_id: int, topic_model: Any) -> Optional[WordCloud]:
    """
    Legacy function for backward compatibility.
    
    Args:
        topic_id: ID of the topic
        topic_model: Trained topic model
        
    Returns:
        WordCloud object or None if failed
    """
    wc_data = create_wordcloud_data(topic_id, topic_model, f"Topic {topic_id}")
    if wc_data:
        return generate_wordcloud_image(wc_data)
    return None