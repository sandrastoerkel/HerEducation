import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import logging

from utils.emotion_detection import (
    EMOTION_LABEL_MAP, EMOTION_COLORS, 
    get_emotion_keywords, split_text_into_sentences, 
    analyze_sentence_structure
)

# =====================================================================================
# CONSTANTS
# =====================================================================================

# Visualization Constants
DEFAULT_CHART_HEIGHT = 500
SMALL_CHART_HEIGHT = 300
PREVIEW_LENGTH = 100

# Color Schemes
MODEL_COLOR = "#1976D2"
LINGUISTIC_COLOR = "#388E3C"
WEIGHTED_COLOR = "#7B1FA2"

COLOR_DISCRETE_MAP = {
    "Model": MODEL_COLOR,
    "Linguistic": LINGUISTIC_COLOR,
    "Weighted": WEIGHTED_COLOR
}

# Default Weights
DEFAULT_MODEL_WEIGHT = 0.7
DEFAULT_LINGUISTIC_WEIGHT = 0.3

# Evaluation Criteria Colors
EVALUATION_COLORS = {
    "Excellent": "background-color: #D5F5E3",
    "Good": "background-color: #D5F5E3; opacity: 0.7",
    "Average": "background-color: #FCF3CF",
    "Limited": "background-color: #FADBD8; opacity: 0.7",
    "Low": "background-color: #FADBD8",
    "Easy": "background-color: #D5F5E3",
    "Complex": "background-color: #FADBD8"
}

# =====================================================================================
# CONFIGURATION
# =====================================================================================

@dataclass
class EmotionComparisonConfig:
    """Configuration for emotion comparison analysis."""
    model_weight: float = DEFAULT_MODEL_WEIGHT
    linguistic_weight: float = DEFAULT_LINGUISTIC_WEIGHT
    preview_length: int = PREVIEW_LENGTH
    chart_height: int = DEFAULT_CHART_HEIGHT
    small_chart_height: int = SMALL_CHART_HEIGHT
    
    @property
    def total_weight(self) -> float:
        """Ensure weights sum to 1.0."""
        return self.model_weight + self.linguistic_weight
    
    @property
    def normalized_model_weight(self) -> float:
        """Get normalized model weight."""
        return self.model_weight / self.total_weight if self.total_weight > 0 else 0.5
    
    @property
    def normalized_linguistic_weight(self) -> float:
        """Get normalized linguistic weight."""
        return self.linguistic_weight / self.total_weight if self.total_weight > 0 else 0.5

# =====================================================================================
# DATA PROCESSING FUNCTIONS
# =====================================================================================

def calculate_emotion_counts(df: pd.DataFrame, emotion_columns: List[str]) -> List[Dict[str, Any]]:
    """
    Calculate emotion counts for model and linguistic approaches.
    
    Args:
        df: DataFrame with emotion data
        emotion_columns: List of emotion column names
        
    Returns:
        List of dictionaries with comparison data
    """
    comparison_data = []
    
    try:
        for emotion in emotion_columns:
            # Only process if column exists
            if emotion not in df.columns:
                continue
                
            # Model-based detection
            model_count = len(df[df[emotion] > 0.5])
            
            # Linguistic detection
            ling_col = f"{emotion}_linguistic"
            ling_count = len(df[df[ling_col] > 0.5]) if ling_col in df.columns else 0
            
            comparison_data.extend([
                {"Emotion": emotion, "Method": "Model", "Count": model_count},
                {"Emotion": emotion, "Method": "Linguistic", "Count": ling_count}
            ])
            
    except Exception as e:
        logging.error(f"Error calculating emotion counts: {e}")
        
    return comparison_data

def calculate_weighted_scores(df: pd.DataFrame, emotion_columns: List[str], 
                            config: EmotionComparisonConfig) -> List[Dict[str, Any]]:
    """
    Calculate weighted scores for all approaches.
    
    Args:
        df: DataFrame with emotion data
        emotion_columns: List of emotion column names
        config: Configuration object
        
    Returns:
        List of dictionaries with score data
    """
    all_scores = []
    
    try:
        for emotion in emotion_columns:
            # Only process if column exists
            if emotion not in df.columns:
                continue
                
            ling_col = f"{emotion}_linguistic"
            if ling_col not in df.columns:
                # Only add model score if linguistic is missing
                avg_model = df[emotion].mean()
                all_scores.append({"Emotion": emotion, "Score": avg_model, "Type": "Model"})
                continue
                
            avg_model = df[emotion].mean()
            avg_ling = df[ling_col].mean()
            avg_weighted = (avg_model * config.normalized_model_weight + 
                          avg_ling * config.normalized_linguistic_weight)
            
            all_scores.extend([
                {"Emotion": emotion, "Score": avg_weighted, "Type": "Weighted"},
                {"Emotion": emotion, "Score": avg_model, "Type": "Model"},
                {"Emotion": emotion, "Score": avg_ling, "Type": "Linguistic"}
            ])
                
    except Exception as e:
        logging.error(f"Error calculating weighted scores: {e}")
        
    return all_scores

def calculate_example_scores(df: pd.DataFrame, example_idx: int, 
                           emotion_columns: List[str], 
                           config: EmotionComparisonConfig) -> List[Dict[str, Any]]:
    """
    Calculate scores for a specific example comment.
    
    Args:
        df: DataFrame with emotion data
        example_idx: Index of the example comment
        emotion_columns: List of emotion column names
        config: Configuration object
        
    Returns:
        List of dictionaries with example score data
    """
    example_data = []
    
    try:
        for emotion in emotion_columns:
            # Only process if column exists
            if emotion not in df.columns:
                continue
                
            model_score = df.loc[example_idx, emotion]
            
            ling_col = f"{emotion}_linguistic"
            if ling_col not in df.columns:
                # Only add model score if linguistic is missing
                example_data.append({"Emotion": emotion, "Method": "Model", "Score": model_score})
                continue
                
            ling_score = df.loc[example_idx, ling_col]
            weighted_score = (model_score * config.normalized_model_weight + 
                            ling_score * config.normalized_linguistic_weight)
            
            example_data.extend([
                {"Emotion": emotion, "Method": "Model", "Score": model_score},
                {"Emotion": emotion, "Method": "Linguistic", "Score": ling_score},
                {"Emotion": emotion, "Method": "Weighted", "Score": weighted_score}
            ])
                
    except Exception as e:
        logging.error(f"Error calculating example scores: {e}")
        
    return example_data

def get_comment_previews(df: pd.DataFrame, preview_length: int = PREVIEW_LENGTH) -> Dict[str, int]:
    """
    Create comment previews for selection.
    
    Args:
        df: DataFrame with comments
        preview_length: Length of preview text
        
    Returns:
        Dictionary mapping previews to indices
    """
    try:
        if "clean_text" not in df.columns or len(df) == 0:
            return {}
            
        sample_comments = df["clean_text"].values
        comment_previews = [
            f"{comment[:preview_length]}..." if len(comment) > preview_length else comment 
            for comment in sample_comments
        ]
        
        return {preview: idx for preview, idx in zip(comment_previews, range(len(df)))}
        
    except Exception as e:
        logging.error(f"Error creating comment previews: {e}")
        return {}

# =====================================================================================
# VISUALIZATION FUNCTIONS
# =====================================================================================

def render_main_comparison_chart(comparison_df: pd.DataFrame) -> None:
    """Render the main comparison chart between model and linguistic approaches."""
    try:
        fig = px.bar(
            comparison_df,
            x="Emotion",
            y="Count",
            color="Method",
            barmode="group",
            color_discrete_map=COLOR_DISCRETE_MAP,
            title="Comparison: Model vs. Linguistic Recognition"
        )
        
        fig.update_layout(
            xaxis_title='Emotion',
            yaxis_title='Number of Detections',
            legend_title='Method',
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="comparison_main_chart_en")
        
    except Exception as e:
        logging.error(f"Error rendering main comparison chart: {e}")
        st.error("Error creating main comparison chart.")

def render_keyword_treemap() -> None:
    """Render keyword treemap visualization."""
    try:
        emotion_keywords = get_emotion_keywords()
        keyword_data = []
        
        for emotion, words in emotion_keywords.items():
            for word in words[:10]:  # First 10 words for clarity
                keyword_data.append({"Emotion": emotion, "Word": word})
        
        if not keyword_data:
            st.warning("No emotion keywords available for visualization.")
            return
            
        keyword_df = pd.DataFrame(keyword_data)
        
        fig = px.treemap(
            keyword_df,
            path=[px.Constant("Emotions"), "Emotion", "Word"],
            color="Emotion",
            color_discrete_map=EMOTION_COLORS,
            title="Emotional Keywords for Linguistic Analysis"
        )
        
        fig.update_layout(
            margin=dict(t=50, l=25, r=25, b=25),
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="keyword_treemap_en")
        
    except Exception as e:
        logging.error(f"Error rendering keyword treemap: {e}")
        st.error("Error creating keyword visualization.")

def render_weighted_approach_chart(all_scores_df: pd.DataFrame) -> None:
    """Render weighted approach comparison chart."""
    try:
        fig = px.line(
            all_scores_df, 
            x="Emotion", 
            y="Score", 
            color="Type",
            markers=True,
            color_discrete_map={
                "Weighted": WEIGHTED_COLOR, 
                "Model": MODEL_COLOR, 
                "Linguistic": LINGUISTIC_COLOR
            },
            title="Weighted Combination Approach Comparison"
        )
        
        fig.update_layout(
            xaxis_title='Emotion',
            yaxis_title='Average Score',
            legend_title='Method',
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="weighted_approach_en")
        
    except Exception as e:
        logging.error(f"Error rendering weighted approach chart: {e}")
        st.error("Error creating weighted comparison chart.")

def render_example_analysis_chart(example_df: pd.DataFrame) -> None:
    """Render example analysis chart."""
    try:
        fig = px.bar(
            example_df,
            x="Emotion",
            y="Score",
            color="Method",
            barmode="group",
            color_discrete_map=COLOR_DISCRETE_MAP,
            title="Emotion Scores for Example Comment"
        )
        
        fig.update_layout(
            xaxis_title='Emotion',
            yaxis_title='Score',
            legend_title='Method',
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="example_analysis_en")
        
    except Exception as e:
        logging.error(f"Error rendering example analysis chart: {e}")
        st.error("Error creating example analysis chart.")

def render_sentence_structure_chart(structure: Dict[str, bool], sentence_idx: int) -> None:
    """Render sentence structure analysis chart."""
    try:
        structure_data = [
            {"Feature": key.replace("_present", ""), "Value": 1} 
            for key, value in structure.items() if value
        ]
        
        if not structure_data:
            st.write("No special structural features detected.")
            return
            
        structure_df = pd.DataFrame(structure_data)
        
        fig = px.bar(
            structure_df,
            x="Feature",
            y="Value",
            color="Feature",
            title=f"Sentence Structure - Sentence {sentence_idx + 1}",
            height=SMALL_CHART_HEIGHT
        )
        
        fig.update_layout(
            showlegend=False,
            yaxis=dict(showticklabels=False, title=""),
            xaxis_title=""
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"sentence_structure_en_{sentence_idx}")
        
    except Exception as e:
        logging.error(f"Error rendering sentence structure chart: {e}")
        st.error("Error creating sentence structure chart.")

def render_adjusted_weights_chart(adjusted_df: pd.DataFrame, model_weight: float, 
                                linguistic_weight: float) -> None:
    """Render adjusted weights comparison chart."""
    try:
        fig = px.bar(
            adjusted_df,
            x="Emotion",
            y="Score",
            color="Weighting",
            barmode="group",
            title=f"Weighting Comparison for Example Comment"
        )
        
        fig.update_layout(
            xaxis_title='Emotion',
            yaxis_title='Score',
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="adjusted_weights_en")
        
    except Exception as e:
        logging.error(f"Error rendering adjusted weights chart: {e}")
        st.error("Error creating weighting comparison chart.")

# =====================================================================================
# CONTENT RENDERING FUNCTIONS
# =====================================================================================

def render_introduction() -> None:
    """Render introduction section."""
    st.subheader("Emotion Model Comparison: AI Model vs. Linguistic Analysis")
    
    st.markdown("""
    This tab compares two approaches to emotion recognition in texts:
    
    1. **Model-based Emotion Recognition**: Uses the pre-trained `RoBERTa` model (`visegradmedia-emotion/Emotion_RoBERTa_german6_v7`), which was trained on German texts for recognizing six emotions.
    
    2. **Linguistic Emotion Recognition**: A rule-based approach that analyzes keywords, sentence structures, negations, and intensifiers.
    
    The app combines both approaches with a **weighted combination (70% Model, 30% Linguistic)** for more precise results.
    """)

def render_approach_details() -> None:
    """Render detailed information about both approaches."""
    st.write("## 2. How the Recognition Approaches Work")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Model-based Emotion Recognition
        
        - **Model**: `visegradmedia-emotion/Emotion_RoBERTa_german6_v7`
        - **Architecture**: RoBERTa (Robustly Optimized BERT)
        - **Training**: Fine-tuned on German texts
        - **Emotions**: 6 categories
        - **Weight**: 70% in final result
        
        #### Advantages:
        - Context understanding through Deep Learning
        - Detects implicit emotions
        - Considers sentence semantics
        - Less susceptible to individual words
        """)
    
    with col2:
        st.markdown("""
        ### Linguistic Emotion Recognition
        
        - **Approach**: Rule-based text analysis
        - **Methodology**: Word lists + sentence structure analysis
        - **Focus**: Explicit emotional expressions
        - **Features**: Considers negations, intensifiers
        - **Weight**: 30% in final result
        
        #### Advantages:
        - Transparent process
        - Considers linguistic nuances
        - Detects sentence structures (questions, exclamations)
        - Explicit negation recognition
        """)
    
    # Explain emotion concepts
    st.write("### 🎯 Understanding Emotion Concepts")
    
    st.markdown("""
    **Important distinction between emotion categories:**
    
    | **Category** | **Meaning** | **Example** |
    |--------------|-------------|-------------|
    | **"neutral"** | 🔵 *Real emotion: Factuality, emotional neutrality* | *"The meeting is at 2:00 PM."* |
    | **"none of them"** | ⚪ *Non-classification: None of the other emotions* | *"Hmm, hard to say..."* |
    | **"surprise"** | 😮 *Basic emotion: Surprise, astonishment* | *"Wow, I didn't expect that!"* |
    
    **→ "Neutral" is an independent, valuable emotion category, not just absence of emotion!**
    """)

def render_weighted_combination_explanation() -> None:
    """Render explanation of weighted combination approach."""
    st.write("## 4. Weighted Combination Approach (70% Model + 30% Linguistic)")
    
    st.markdown("""
    The app combines both recognition approaches into an overall result:
    
    ```python
    weighted_score = model_score * 0.7 + linguistic_score * 0.3
    ```
    
    This leads to more robust results through:
    - Utilizing the strengths of both approaches
    - Compensating for respective weaknesses
    - Better recognition of implicit and explicit emotions
    """)

def render_comparison_table() -> None:
    """Render comparison table of approaches."""
    st.write("## 6. Comparison: Advantages and Disadvantages of Approaches")
    
    comparison_data = {
        "Criterion": [
            "Context Understanding", "Negation Recognition", "Implicit Emotions", 
            "Explicit Emotions", "Transparency", "Training Effort",
            "Adaptability", "Language-Specific Nuances", "Computational Cost", "Emotion Transitions"
        ],
        "Model": [
            "Excellent", "Good", "Excellent", "Good", "Low (Black Box)",
            "High", "Complex", "Model-dependent", "High", "Average"
        ],
        "Linguistic": [
            "Limited", "Excellent", "Limited", "Excellent", "High (Rule-based)",
            "Low", "Easy", "Excellent", "Low", "Good"
        ],
        "Combined": [
            "Excellent", "Excellent", "Excellent", "Excellent", "Average",
            "Average", "Average", "Excellent", "Average", "Excellent"
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    
    def color_values(val):
        """Apply color coding to comparison values."""
        return EVALUATION_COLORS.get(val, "")
    
    st.dataframe(
        comparison_df.style.applymap(
            color_values, 
            subset=["Model", "Linguistic", "Combined"]
        )
    )

def render_conclusion() -> None:
    """Render conclusion section."""
    st.write("## 8. Conclusion")
    st.markdown("""
    The combination of both approaches offers significant advantages:
    
    - **Increased Accuracy**: By combining the strengths of both methods.
    - **Better Robustness**: Linguistic analysis compensates for model weaknesses and vice versa.
    - **Transparency and Context**: Combines the transparency of rule-based systems with the contextual capability of Deep Learning.
    - **Differentiated Analysis Results**: Enables more detailed insights into emotional structures.
    
    The optimal weighting is application-specific and can be determined experimentally. For this app, a standard weighting of 70% model and 30% linguistic analysis was chosen, but this can be adjusted to achieve better results for specific use cases.
    """)

# =====================================================================================
# SECTION HANDLERS
# =====================================================================================

def handle_main_comparison(df: pd.DataFrame, emotion_columns: List[str]) -> None:
    """Handle main comparison section."""
    st.write("## 1. Comparison of Recognition Approaches")
    
    try:
        comparison_data = calculate_emotion_counts(df, emotion_columns)
        if not comparison_data:
            st.warning("No comparison data available.")
            return
            
        comparison_df = pd.DataFrame(comparison_data)
        render_main_comparison_chart(comparison_df)
        
    except Exception as e:
        logging.error(f"Error in main comparison section: {e}")
        st.error("Error creating main comparison.")

def handle_weighted_approach(df: pd.DataFrame, emotion_columns: List[str], 
                           config: EmotionComparisonConfig) -> None:
    """Handle weighted approach section."""
    render_weighted_combination_explanation()
    
    try:
        all_scores_data = calculate_weighted_scores(df, emotion_columns, config)
        if not all_scores_data:
            st.warning("No weighting data available.")
            return
            
        all_scores_df = pd.DataFrame(all_scores_data)
        render_weighted_approach_chart(all_scores_df)
        
    except Exception as e:
        logging.error(f"Error in weighted approach section: {e}")
        st.error("Error creating weighted analysis.")

def handle_example_analysis(df: pd.DataFrame, emotion_columns: List[str], 
                          config: EmotionComparisonConfig) -> Optional[int]:
    """Handle example analysis section."""
    st.write("## 5. Example Analysis of a Comment")
    
    try:
        comment_options = get_comment_previews(df, config.preview_length)
        if not comment_options:
            st.warning("No comments available for example analysis.")
            return None
            
        selected_preview = st.selectbox(
            "Choose a comment for analysis:",
            options=list(comment_options.keys()),
            key="comment_selection_en"
        )
        
        example_idx = comment_options[selected_preview]
        example_comment = df.loc[example_idx, "clean_text"]
        
        st.subheader("Example Comment")
        st.info(example_comment)
        
        st.subheader("Emotion Analysis")
        
        example_data = calculate_example_scores(df, example_idx, emotion_columns, config)
        if not example_data:
            st.warning("No example data available.")
            return example_idx
            
        example_df = pd.DataFrame(example_data)
        render_example_analysis_chart(example_df)
        
        # Display dominant emotion
        if "dominant_emotion" in df.columns:
            dominant_emotion = df.loc[example_idx, "dominant_emotion"]
            st.success(f"The dominant emotion for this comment is: **{dominant_emotion}**")
        
        # Detailed linguistic analysis
        handle_linguistic_analysis_details(example_comment)
        
        return example_idx
        
    except Exception as e:
        logging.error(f"Error in example analysis section: {e}")
        st.error("Error in example analysis.")
        return None

def handle_linguistic_analysis_details(example_comment: str) -> None:
    """Handle detailed linguistic analysis section."""
    st.subheader("Linguistic Analysis Details")
    
    try:
        sentences = split_text_into_sentences(example_comment)
        
        if not sentences:
            st.write("No sentences found for analysis.")
            return
            
        for i, sentence in enumerate(sentences):
            st.write(f"**Sentence {i+1}:** {sentence}")
            
            structure = analyze_sentence_structure(sentence)
            render_sentence_structure_chart(structure, i)
            
    except Exception as e:
        logging.error(f"Error in linguistic analysis details: {e}")
        st.error("Error in detailed linguistic analysis.")

def handle_weight_adjustment(df: pd.DataFrame, emotion_columns: List[str], 
                           example_idx: Optional[int]) -> None:
    """Handle weight adjustment section."""
    st.write("## 7. Adjust Weighting")
    st.write("You can experiment with how different weightings of both approaches affect the results:")
    
    try:
        model_weight = st.slider(
            "AI Model Weight",
            min_value=0.0,
            max_value=1.0,
            value=DEFAULT_MODEL_WEIGHT,
            step=0.05,
            key="model_weight_slider_en"
        )
        
        linguistic_weight = 1.0 - model_weight
        
        st.write(f"Current weighting: **{model_weight:.0%} Model**, **{linguistic_weight:.0%} Linguistic**")
        
        st.info("""
        To use this weighting throughout the app, you would need to adjust the weighting factors in the `emotion_analysis.py` file accordingly.
        
        Currently, the weighting is only changed in this visualization, not in the actual analysis.
        """)
        
        # Show impact of adjusted weighting if example is available
        if example_idx is not None:
            handle_adjusted_weighting_impact(df, emotion_columns, example_idx, model_weight, linguistic_weight)
            
    except Exception as e:
        logging.error(f"Error in weight adjustment section: {e}")
        st.error("Error in weight adjustment.")

def handle_adjusted_weighting_impact(df: pd.DataFrame, emotion_columns: List[str], 
                                   example_idx: int, model_weight: float, 
                                   linguistic_weight: float) -> None:
    """Handle adjusted weighting impact visualization."""
    st.write("### Impact of Adjusted Weighting on Example Comment")
    
    try:
        adjusted_example_data = []
        new_weighted_scores = {}
        
        for emotion in emotion_columns:
            if emotion in df.columns and f"{emotion}_linguistic" in df.columns:
                model_score = df.loc[example_idx, emotion]
                ling_score = df.loc[example_idx, f"{emotion}_linguistic"]
                
                new_weighted_score = model_score * model_weight + ling_score * linguistic_weight
                new_weighted_scores[emotion] = new_weighted_score
                
                adjusted_example_data.extend([
                    {
                        "Emotion": emotion,
                        "Score": new_weighted_score,
                        "Weighting": f"{model_weight:.0%} Model, {linguistic_weight:.0%} Linguistic"
                    },
                    {
                        "Emotion": emotion,
                        "Score": model_score * DEFAULT_MODEL_WEIGHT + ling_score * DEFAULT_LINGUISTIC_WEIGHT,
                        "Weighting": "70% Model, 30% Linguistic (Standard)"
                    }
                ])
        
        if adjusted_example_data:
            adjusted_df = pd.DataFrame(adjusted_example_data)
            render_adjusted_weights_chart(adjusted_df, model_weight, linguistic_weight)
            
            # Compare dominant emotions
            if new_weighted_scores and "dominant_emotion" in df.columns:
                new_dominant_emotion = max(new_weighted_scores.items(), key=lambda x: x[1])[0]
                old_dominant_emotion = df.loc[example_idx, "dominant_emotion"]
                
                if new_dominant_emotion != old_dominant_emotion:
                    st.warning(f"""
                    With the new weighting, the dominant emotion changes from **{old_dominant_emotion}** to **{new_dominant_emotion}**!
                    
                    This shows how strongly the weighting can influence the final result.
                    """)
                else:
                    st.success(f"""
                    The dominant emotion **{new_dominant_emotion}** remains the same even with the new weighting.
                    
                    This emotion is robust against changes in weighting.
                    """)
        
    except Exception as e:
        logging.error(f"Error in adjusted weighting impact: {e}")
        st.error("Error in weighting impact analysis.")

# =====================================================================================
# MAIN API FUNCTION
# =====================================================================================

def display_emotion_comparison(df: pd.DataFrame, emotion_classifier: Any) -> None:
    """
    Shows a detailed comparison between model-based and linguistic emotion recognition
    
    Args:
        df: DataFrame with comments and emotion data
        emotion_classifier: The emotion recognition model
    """
    try:
        # Configuration
        config = EmotionComparisonConfig()
        
        # Validate input data
        emotion_columns = list(EMOTION_LABEL_MAP.values())
        
        # Debug info for development - show available columns
        with st.expander("🔍 Debug Info - DataFrame Columns", expanded=False):
            available_emotions = [col for col in emotion_columns if col in df.columns]
            missing_emotions = [col for col in emotion_columns if col not in df.columns]
            
            st.write(f"**Available Emotion Columns ({len(available_emotions)}):** {available_emotions}")
            if missing_emotions:
                st.write(f"**Missing Emotion Columns ({len(missing_emotions)}):** {missing_emotions}")
            
            st.write(f"**DataFrame Shape:** {df.shape}")
            st.write(f"**All DataFrame Columns:** {list(df.columns)}")
        
        # Less strict validation - at least one emotion must be present
        if not any(emotion in df.columns for emotion in emotion_columns):
            st.warning("No emotion data found in DataFrame.")
            return
        
        if len(df) == 0:
            st.warning("No data available for analysis.")
            return
        
        # Use only available emotion columns
        emotion_columns = available_emotions
        
        # Warning if not all features are available
        if missing_emotions:
            st.info(f"""
            ℹ️ **Note:** Not all emotion columns are available. 
            
            **Missing emotions:** {', '.join(missing_emotions)}
            
            The analysis will be performed with the available emotions ({', '.join(available_emotions)}).
            """)
        
        # Check if linguistic data is available
        linguistic_columns = [f"{emotion}_linguistic" for emotion in emotion_columns]
        has_linguistic_data = any(col in df.columns for col in linguistic_columns)
        
        if not has_linguistic_data:
            st.warning("""
            ⚠️ **Important Note:** No linguistic emotion data found!
            
            The comparison will only be performed with available model data.
            For the complete comparison, the `*_linguistic` columns should also be present.
            """)
        
        # Render sections
        render_introduction()
        
        handle_main_comparison(df, emotion_columns)
        
        render_approach_details()
        
        st.write("## 3. Emotional Word Lists for Linguistic Analysis")
        st.write("Linguistic analysis uses extensive word lists for each emotion (abbreviated here for clarity):")
        render_keyword_treemap()
        
        handle_weighted_approach(df, emotion_columns, config)
        
        example_idx = handle_example_analysis(df, emotion_columns, config)
        
        render_comparison_table()
        
        handle_weight_adjustment(df, emotion_columns, example_idx)
        
        render_conclusion()
        
    except Exception as e:
        logging.error(f"Error in display_emotion_comparison: {e}")
        st.error("An unexpected error occurred in emotion comparison analysis.")
        st.error(f"Details: {str(e)}")

# =====================================================================================
# BACKWARDS COMPATIBILITY
# =====================================================================================

# Export main function for backwards compatibility
__all__ = ['display_emotion_comparison']