import streamlit as st
from utils.debug_flag import is_debug
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import traceback
import os
import sys
from pathlib import Path
from datetime import datetime

# Suppress tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# === RELATIVE PATH CONFIGURATION ===
# Determine the App-Root directory automatically
APP_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = APP_ROOT / "data" / "comments"
RESULTS_DIR = APP_ROOT / "saved_results_english"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# === IMPORT STORAGE SYSTEM ===
# Try to import storage system for country analysis
try:
    sys.path.append(str(APP_ROOT))
    from analysis_storage_system import add_save_button_to_analysis
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False

try:
    from utils.country_analysis_storage_english import CountryAnalysisStorageEnglish
    COUNTRY_STORAGE_AVAILABLE = True
except ImportError:
    COUNTRY_STORAGE_AVAILABLE = False

# === IMPORT MODULES ===
from utils.commentanalysis_english_persistence import CommentAnalysisPersistence
from utils.commentanalysis_english_file_handler import CommentAnalysisFileHandler
from utils.commentanalysis_english_youtube import CommentAnalysisYouTube
from utils.commentanalysis_english_ui import CommentAnalysisUI
from utils.example_analyses import render_example_picker
from utils.live_comment_analysis import (
    LiveAnalysisError, is_cloud, is_live_result, limit_comments, live_max_comments,
    render_live_section, render_result_download, render_status, run_pending_analysis)
from models.pipeline_adapters import CachedPipeline

# === INITIALIZE MANAGERS ===
persistence_manager = CommentAnalysisPersistence(RESULTS_DIR)
file_handler = CommentAnalysisFileHandler(DATA_DIR)
youtube_manager = CommentAnalysisYouTube()
ui_manager = CommentAnalysisUI()

# === WRAPPER FUNCTIONS FOR BACKWARD COMPATIBILITY ===
def save_analysis_results(filename, df, additional_data=None):
    """Saves analysis results using persistence manager"""
    return persistence_manager.save_analysis_results(filename, df, additional_data)

def load_analysis_results(filename):
    """Loads saved analysis results using persistence manager"""
    return persistence_manager.load_analysis_results(filename)

def get_available_analyses():
    """Returns a list of available saved analyses"""
    return persistence_manager.get_available_analyses()

def get_files_from_data_folder():
    """Returns a list of all CSV files in the data folder"""
    return file_handler.get_files_from_data_folder()

def clean_csv_data(file_content):
    """Cleans the CSV file and extracts the comment column"""
    return file_handler.clean_csv_data(file_content)

def clean_text(text):
    """Cleans text for topic analysis"""
    return file_handler.clean_text(text)

def load_and_clean_data(uploaded_file):
    """Loads and cleans the uploaded file with English language filtering"""
    return file_handler.load_and_clean_data(uploaded_file)

def extract_video_id(filename):
    """Extracts the YouTube video ID from the filename"""
    return file_handler.extract_video_id(filename)

def get_video_info(video_id):
    """Retrieves information about a YouTube video"""
    return youtube_manager.get_video_info(video_id)

def display_youtube_info(video_id):
    """Shows YouTube video information"""
    youtube_manager.display_youtube_info(video_id)

def display_model_info(model_type):
    """Displays information about the models used in the analysis"""
    ui_manager.display_model_info(model_type)

def add_debug_section():
    """Adds debug section to Streamlit app"""
    ui_manager.show_debug_section(persistence_manager, RESULTS_DIR)

# ================================================================================
# IMPORT AND DEPENDENCY MANAGEMENT
# ================================================================================

# Try to import necessary libraries with error handling
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not installed. Some visualizations will not be available.")

# Try to import utility modules with detailed error handling
try:
    # Import from the parent directory (since we're in pages/)
    sys.path.append(str(Path(__file__).parent.parent))
    
    from models.model_loader_english import load_sentiment_model, load_emotion_model, load_bertopic_model
    MODELS_AVAILABLE = True
except ImportError as e:
    MODELS_AVAILABLE = False
    st.warning(f"Models could not be loaded: {e}")

# Check if BERTopic is available
try:
    from utils.check_dependencies import is_bertopic_available
    BERTOPIC_CHECKED = True
    BERTOPIC_AVAILABLE = is_bertopic_available()
except ImportError:
    BERTOPIC_CHECKED = False
    BERTOPIC_AVAILABLE = False
    st.warning("BERTopic dependency check could not be loaded.")

# Try to import analysis modules
try:
    from utils.sentiment_analysis_english import (analyze_sentiment, display_sentiment_results,
                                                  perform_batch_sentiment_analysis, SentimentAnalysisConfig)
    SENTIMENT_ANALYSIS_AVAILABLE = True
except ImportError as e:
    SENTIMENT_ANALYSIS_AVAILABLE = False
    st.warning(f"Sentiment analysis module not available: {e}")

try:
    from utils.topic_analysis_english import prepare_topic_analysis, display_topic_analysis
    TOPIC_ANALYSIS_AVAILABLE = True
except ImportError as e:
    TOPIC_ANALYSIS_AVAILABLE = False
    st.warning(f"Topic analysis module not available: {e}")

try:
    from utils.emotion_analysis_english import prepare_emotion_analysis, display_emotion_analysis
    EMOTION_ANALYSIS_AVAILABLE = True
except ImportError as e:
    EMOTION_ANALYSIS_AVAILABLE = False
    st.warning(f"Emotion analysis module not available: {e}")

try:
    from utils.emotion_comparison_english import display_emotion_comparison
    EMOTION_COMPARISON_AVAILABLE = True
except ImportError as e:
    EMOTION_COMPARISON_AVAILABLE = False
    st.warning(f"Emotion comparison module not available: {e}")

try:
    from utils.special_analysis_english import display_special_analysis
    SPECIAL_ANALYSIS_AVAILABLE = True
except ImportError as e:
    SPECIAL_ANALYSIS_AVAILABLE = False
    st.warning(f"Special analysis module not available: {e}")

# Language detection import is now handled by the file handler module

# ================================================================================
# ENHANCED SAVE SECTION WITH STORAGE INTEGRATION
# ================================================================================

def add_enhanced_save_section(filename, df, additional_data=None):
    """Enhanced save section with storage system integration"""
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Original download functionality
        st.download_button(
            label="💾 Save data as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"{Path(filename).stem}_analysis.csv",
            mime='text/csv'
        )
        
        # Original save functionality
        if st.button("💾 Save Analysis Results", key=f"save_legacy_{filename}"):
            if save_analysis_results(filename, df, additional_data):
                st.success(f"✅ Analysis results for '{filename}' have been successfully saved!")
                st.rerun()
    
    with col2:
        # NEW STORAGE SYSTEM INTEGRATION
        if STORAGE_AVAILABLE:
            # Extract video info for metadata (if available)
            video_info = {}
            try:
                video_id = extract_video_id(filename)
                if video_id:
                    video_data = get_video_info(video_id)
                    if video_data:
                        video_info = {
                            "title": video_data.get('title'),
                            "channel": video_data.get('uploader')
                        }
            except:
                pass  # If video info is not available
            
            # Add storage system save button
            add_save_button_to_analysis(
                df=df,
                analysis_type="sentiment_emotion_topic",
                language="en",
                video_info=video_info
            )
        else:
            st.info("💡 Storage system for country analysis not available")
    # Country Analysis Export
    if COUNTRY_STORAGE_AVAILABLE:
        if st.button("🌍 Save for Country Analysis", key=f"country_export_{filename}"):
            with st.spinner("Saving for Country Analysis..."):
                storage = CountryAnalysisStorageEnglish()
                result = storage.export_with_smart_labels(df, filename, additional_data)
                
                if result.success:
                    st.success("✅ Successfully saved for Country Analysis!")
                    st.info(f"📁 File: `{result.file_path.name}`")
                    st.info(f"🌍 Country: **{result.country_detected}**")
                    st.info(f"🏷️ Smart Labels: {result.smart_labels_added} added")
                    if result.warnings:
                        st.warning("⚠️ Notes: " + ", ".join(result.warnings))
                else:
                    st.error(f"❌ Error saving: {result.error_message}")
    else:
        st.info("💡 Country Analysis Storage not available")

# ================================================================================
# FALLBACK FUNCTIONS
# ================================================================================

def analyze_sentiment_fallback(df, text_column):
    """Simplified fallback sentiment analysis"""
    st.subheader("Sentiment Analysis (simplified)")
    st.info("Using simplified sentiment analysis as the model could not be loaded.")
    
    # Random sentiment assignment for demonstration
    import random
    sentiments = ['positive', 'neutral', 'negative']
    weights = [0.3, 0.4, 0.3]  # Weights for distribution
    
    df['sentiment'] = [random.choices(sentiments, weights=weights)[0] for _ in range(len(df))]
    df['confidence'] = [random.uniform(0.6, 0.95) for _ in range(len(df))]
    
    return df

def display_sentiment_results_fallback(df, text_column):
    """Displays sentiment analysis results (simplified version)"""
    st.subheader("Sentiment Distribution")
    
    # Count sentiments
    sentiment_counts = df['sentiment'].value_counts()
    
    # Create a simple bar chart
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(sentiment_counts.index, sentiment_counts.values, 
           color=['green' if x == 'positive' else 'gray' if x == 'neutral' else 'red' for x in sentiment_counts.index])
    ax.set_xlabel('Sentiment')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Sentiments')
    
    # Show the chart
    st.pyplot(fig)
    
    # Show examples for each category
    st.subheader("Examples")
    
    for sentiment in ['positive', 'neutral', 'negative']:
        if sentiment in df['sentiment'].values:
            examples = df[df['sentiment'] == sentiment].head(2)
            st.write(f"**{sentiment.capitalize()} Examples:**")
            for _, row in examples.iterrows():
                st.write(f"- {row[text_column]}")
            st.write("")

# ================================================================================
# LIVE ANALYSIS (runs without widgets; control flow in utils/live_comment_analysis.py)
# ================================================================================

LIVE_STEPS_EN = [
    "Read and clean the file (English comments only)",
    "Load the sentiment model and rate the comments",
    "Find topics (BERTopic)",
    "Load the emotion model and detect emotions",
]


def run_live_analysis_en(file_obj, request, progress):
    """Full analysis in the previous order (sentiment -> topics -> emotions), without widgets.

    Uses the UI default values. The result is written to the session by run_pending_analysis()
    only after the complete run.
    """
    notes = []

    progress.step(0)
    df, text_column = load_and_clean_data(file_obj)
    if df is None or text_column is None or len(df) == 0:
        raise LiveAnalysisError("No English comments were found in the file.")
    df[text_column] = df[text_column].fillna("").astype(str)
    df = df[df[text_column].str.len() > 0].reset_index(drop=True)
    if len(df) == 0:
        raise LiveAnalysisError("No English comments were found in the file.")
    df, total = limit_comments(df, live_max_comments())
    if len(df) < total:
        notes.append(f"The file contains {total:,} comments – a fixed sample of {len(df):,} was analysed.")
    df = file_handler.apply_text_cleaning(df, text_column)

    progress.step(1)
    if not (MODELS_AVAILABLE and SENTIMENT_ANALYSIS_AVAILABLE):
        raise LiveAnalysisError("The sentiment model is not installed on this server.")
    sentiment_pipeline = CachedPipeline(load_sentiment_model())
    df = perform_batch_sentiment_analysis(df.copy(), text_column, sentiment_pipeline, SentimentAnalysisConfig())

    additional_data = {}
    progress.step(2)
    if BERTOPIC_AVAILABLE and TOPIC_ANALYSIS_AVAILABLE:
        df, topic_model, topic_info, topic_df, topic_labels = prepare_topic_analysis(df, text_column)
        if topic_model is not None:
            additional_data = {'topic_model': topic_model, 'topic_info': topic_info,
                               'topic_df': topic_df, 'topic_labels': topic_labels}
        else:
            notes.append("Topic analysis skipped (too few longer comments or model not available).")
    else:
        notes.append("Topic analysis not available (BERTopic not installed).")

    progress.step(3)
    if EMOTION_ANALYSIS_AVAILABLE and MODELS_AVAILABLE:
        emotion_classifier = load_emotion_model()
        if emotion_classifier is not None:
            df = prepare_emotion_analysis(df, emotion_classifier, show_config_ui=False)
            recognized = int(df['emotions'].notna().sum()) if 'emotions' in df.columns else 0
            if recognized == 0:
                # do not show invented fallback values
                df = df.drop(columns=['dominant_emotion'], errors='ignore')
                notes.append("Emotions could not be detected – the emotion tab is hidden.")
            elif recognized < len(df):
                notes.append(f"Emotions detected for {recognized:,} of {len(df):,} comments "
                             f"(very short comments are not rated).")
        else:
            notes.append("The emotion model could not be loaded.")

    return {"df": df, "text_column": text_column, "additional_data": additional_data, "notes": notes}


# ================================================================================
# MAIN APPLICATION
# ================================================================================

def main():
    # Set up page configuration and UI
    ui_manager.setup_page_config()
    ui_manager.setup_sidebar_copyright()
    ui_manager.display_header()
    

    # Initialize Session State for persistent data
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
        
    if 'df' not in st.session_state:
        st.session_state.df = None
        
    if 'additional_data' not in st.session_state:
        st.session_state.additional_data = {}
        
    if 'text_column' not in st.session_state:
        st.session_state.text_column = None
    
    # Live analysis: run a requested analysis (shows only the progress, then reruns the page)
    run_pending_analysis('en', run_live_analysis_en, LIVE_STEPS_EN)
    render_status('en')
    
    # Example analyses always on top (or info about your own analysis)
    render_example_picker('en')
    
    # Saved analyses – local only (the cloud does not store anything permanently)
    selected_file = ui_manager.display_saved_analyses_section(persistence_manager) if not is_cloud() else None
    
    if selected_file:
        with st.spinner(f"Loading analysis for '{selected_file}'..."):
            df, additional_data, metadata = load_analysis_results(selected_file)
            
            if df is not None:
                st.session_state.current_file = selected_file
                st.session_state.df = df
                st.session_state.result_source = "saved"
                st.session_state.example_lang = "en"
                
                # Determine text column
                possible_columns = ['comment_text', 'text', 'comment', 'kommentar', 'content', 'Text', 'Comment', 'Kommentar', 'Content']
                text_column = None
                for col in possible_columns:
                    if col in df.columns:
                        text_column = col
                        break
                
                st.session_state.text_column = text_column
                
                if additional_data:
                    st.session_state.additional_data = additional_data
                
                st.success(f"Analysis for '{selected_file}' successfully loaded!")
                st.rerun()
            else:
                st.error(f"Could not load data for '{selected_file}'.")
    
    # Emotion model only for the model comparison of your own analysis (already loaded then).
    # Otherwise models are loaded only when a live analysis starts, not on every page view.
    emotion_classifier = None
    if MODELS_AVAILABLE and is_live_result('en'):
        try:
            emotion_classifier = load_emotion_model()
        except Exception:
            emotion_classifier = None
    
    # CASE 1: Display existing analysis
    if st.session_state.current_file and st.session_state.df is not None:
        df = st.session_state.df
        text_column = st.session_state.text_column
        
        # Extract YouTube ID from filename
        filename = st.session_state.current_file
        video_id = extract_video_id(filename)
        
        # Show YouTube information
        if video_id:
            display_youtube_info(video_id)
        
        # Create app tabs based on available data in df
        tabs_to_create = ["📊 Sentiment Analysis"]
        
        # Check which analysis results are present in the data
        # (example analyses have topic assignments but no topic model -> no topic/special tab)
        has_topic_model = st.session_state.additional_data.get('topic_model') is not None
        has_topic_labels = bool(st.session_state.additional_data.get('topic_labels'))
        if 'topic' in df.columns and has_topic_model:
            tabs_to_create.append("🏷️ Topic Analysis")
        
        if 'dominant_emotion' in df.columns:
            tabs_to_create.append("😊 Emotion Analysis")
            
            # More tabs depending on available data
            if EMOTION_COMPARISON_AVAILABLE and emotion_classifier is not None:
                tabs_to_create.append("⚖️ Emotion Model Comparison")
        
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE and has_topic_labels:
            tabs_to_create.append("🔍 Special Analyses")
        
        # Create tabs
        if len(tabs_to_create) > 1:
            main_tabs = st.tabs(tabs_to_create)
        else:
            main_tabs = [st.container()]
        
        # Show results in respective tabs
        tab_index = 0
        
        # Tab 1: Sentiment Analysis
        with main_tabs[tab_index]:
            # Display model information
            display_model_info("sentiment")
            
            if 'sentiment' in df.columns and SENTIMENT_ANALYSIS_AVAILABLE:
                display_sentiment_results(df, text_column)
            elif 'sentiment' in df.columns:
                display_sentiment_results_fallback(df, text_column)
            else:
                st.warning("No sentiment analysis is available for this data. Please start an analysis below.")
        
        tab_index += 1
        
        # Show other tabs when data is available
        if 'topic' in df.columns and has_topic_model and tab_index < len(main_tabs):
            # Topic Analysis Tab
            with main_tabs[tab_index]:
                # Display model information
                display_model_info("topic")
                
                # Load additional data from session_state
                topic_model = st.session_state.additional_data.get('topic_model')
                topic_info = st.session_state.additional_data.get('topic_info')
                topic_df = st.session_state.additional_data.get('topic_df')
                topic_labels = st.session_state.additional_data.get('topic_labels')
                
                # Show topic analysis if data is available
                if topic_model and TOPIC_ANALYSIS_AVAILABLE:
                    display_topic_analysis(df, topic_model, topic_df, topic_info, topic_labels)
                else:
                    st.warning("Topic analysis could not be displayed. Required data is missing.")
            
            tab_index += 1
        
        # Show emotion analysis when data is available
        if 'dominant_emotion' in df.columns and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                # Display model information
                display_model_info("emotion")
                
                if EMOTION_ANALYSIS_AVAILABLE:
                    # Load topic model data if available
                    topic_model = st.session_state.additional_data.get('topic_model')
                    topic_labels = st.session_state.additional_data.get('topic_labels')
                    
                    display_emotion_analysis(df, text_column, topic_model, topic_labels)
                else:
                    st.warning("Emotion analysis could not be displayed. Required module is not available.")
            
            tab_index += 1
        
        # Show emotion model comparison when data is available
        if 'dominant_emotion' in df.columns and EMOTION_COMPARISON_AVAILABLE and emotion_classifier is not None and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                # Display model information (same as emotion, since it's comparing emotion models)
                display_model_info("emotion")
                
                if emotion_classifier is not None:
                    display_emotion_comparison(df, emotion_classifier)
                else:
                    st.warning("Emotion model comparison could not be displayed. Emotion model is not available.")
            
            tab_index += 1
        
        # Show special analyses when data is available
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE and has_topic_labels and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                topic_labels = st.session_state.additional_data.get('topic_labels')
                if topic_labels:
                    display_special_analysis(df, text_column, topic_labels)
                else:
                    st.warning("Special analyses require topic data that is not fully available.")
        
        # Show data preview
        st.subheader("📋 Data Preview")
        st.dataframe(df.head())
        render_result_download('en')
        
        # ENHANCED SAVE SECTION WITH STORAGE INTEGRATION (local only)
        if not is_cloud(): add_enhanced_save_section(
            st.session_state.current_file, 
            df, 
            st.session_state.additional_data
        )
    
    # Run your own analysis (below the examples) – replaces the former CASE 2
    render_live_section('en', get_files_from_data_folder())
    
    # Debug section (only with HEREDUCATION_DEBUG=1 or secrets debug=true)
    if is_debug():
        add_debug_section()
    
    # Display copyright footer
    ui_manager.display_footer_copyright()

if __name__ == "__main__":
    main()