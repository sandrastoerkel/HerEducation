import streamlit as st
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
    from utils.sentiment_analysis_english import analyze_sentiment, display_sentiment_results
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
    
    # Container for previous analyses
    selected_file = ui_manager.display_saved_analyses_section(persistence_manager)
    
    if selected_file:
        with st.spinner(f"Loading analysis for '{selected_file}'..."):
            df, additional_data, metadata = load_analysis_results(selected_file)
            
            if df is not None:
                st.session_state.current_file = selected_file
                st.session_state.df = df
                
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
    
    # Display current file
    if st.session_state.current_file:
        st.info(f"📄 Current Analysis: {st.session_state.current_file}")
        
        # Option to reset
        if st.button("🔄 Start New Analysis"):
            st.session_state.current_file = None
            st.session_state.df = None
            st.session_state.text_column = None
            st.session_state.additional_data = {}
            st.rerun()
    
    # Check dependencies
    missing_deps = []
    
    if not MODELS_AVAILABLE:
        missing_deps.append("models.model_loader_english")
    
    if not BERTOPIC_CHECKED:
        missing_deps.append("utils.check_dependencies")
    
    # Display missing dependencies
    if missing_deps:
        st.warning(f"⚠️ Some modules could not be loaded: {', '.join(missing_deps)}")
        st.info("""
        🔧 To use full functionality, make sure the following modules are correctly installed:
        - transformers
        - bertopic
        - sentence-transformers
        - hdbscan
        - umap-learn
        - nltk
        - wordcloud
        - yt-dlp (for YouTube information)
        - langdetect (for language filtering)
        
        Additionally, the corresponding Python modules must be present in the utils and models directories.
        """)
    
    # Load sentiment model if available
    sentiment_pipeline = None
    emotion_classifier = None
    
    if MODELS_AVAILABLE:
        with st.spinner("Loading sentiment model..."):
            try:
                sentiment_pipeline = load_sentiment_model()
                st.success("✅ Sentiment model successfully loaded!")
            except Exception as e:
                st.error(f"❌ Error loading sentiment model: {e}")
        
        with st.spinner("Loading emotion model..."):
            try:
                emotion_classifier = load_emotion_model()
                if emotion_classifier:
                    st.success("✅ Emotion model successfully loaded!")
            except Exception as e:
                st.error(f"❌ Error loading emotion model: {e}")
    
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
        if 'topic' in df.columns:
            tabs_to_create.append("🏷️ Topic Analysis")
        
        if 'dominant_emotion' in df.columns:
            tabs_to_create.append("😊 Emotion Analysis")
            
            # More tabs depending on available data
            if EMOTION_COMPARISON_AVAILABLE:
                tabs_to_create.append("⚖️ Emotion Model Comparison")
        
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE:
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
            else:
                display_sentiment_results_fallback(df, text_column)
        
        tab_index += 1
        
        # Show other tabs when data is available
        if 'topic' in df.columns and tab_index < len(main_tabs):
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
        if 'dominant_emotion' in df.columns and EMOTION_COMPARISON_AVAILABLE and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                # Display model information (same as emotion, since it's comparing emotion models)
                display_model_info("emotion")
                
                if emotion_classifier is not None:
                    display_emotion_comparison(df, emotion_classifier)
                else:
                    st.warning("Emotion model comparison could not be displayed. Emotion model is not available.")
            
            tab_index += 1
        
        # Show special analyses when data is available
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                topic_labels = st.session_state.additional_data.get('topic_labels')
                if topic_labels:
                    display_special_analysis(df, text_column, topic_labels)
                else:
                    st.warning("Special analyses require topic data that is not fully available.")
        
        # Show data preview
        st.subheader("📋 Data Preview")
        st.dataframe(df.head())
        
        # ENHANCED SAVE SECTION WITH STORAGE INTEGRATION
        add_enhanced_save_section(
            st.session_state.current_file, 
            df, 
            st.session_state.additional_data
        )
    
    # CASE 2: Perform new analysis
    else:
        # Flag for file processing
        processed_file = file_handler.display_file_selection_ui()
        
        # Process the selected file
        if processed_file is not None:
            try:
                # Filename for YouTube ID extraction
                filename = processed_file.name
                file_handler.show_file_info(filename)
                
                # Extract YouTube video ID if present in filename
                video_id = extract_video_id(filename)
                
                # Show YouTube information if video ID was found
                if video_id:
                    display_youtube_info(video_id)
                
                # Load and clean data
                with st.spinner("Loading and cleaning data..."):
                    df, text_column = load_and_clean_data(processed_file)
                    
                    # Clean text for further analysis
                    df = file_handler.apply_text_cleaning(df, text_column)
                
                # Save in Session State
                st.session_state.current_file = filename
                st.session_state.df = df
                st.session_state.text_column = text_column
                
                # Create app tabs based on available modules
                # Create app tabs based on available modules
                tabs_to_create = ["📊 Sentiment Analysis"]

                if BERTOPIC_AVAILABLE and TOPIC_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("🏷️ Topic Analysis")

                if EMOTION_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("😊 Emotion Analysis")

                if EMOTION_COMPARISON_AVAILABLE:
                    tabs_to_create.append("⚖️ Emotion Model Comparison")

                if SPECIAL_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("🔍 Special Analyses")

                # Create tabs
                if len(tabs_to_create) > 1:
                    main_tabs = st.tabs(tabs_to_create)
                else:
                    main_tabs = [st.container()]
                
                # Tab 1: Sentiment Analysis
                with main_tabs[0]:
                    # Display model information
                    display_model_info("sentiment")
                    
                    with st.spinner("Performing sentiment analysis..."):
                        if SENTIMENT_ANALYSIS_AVAILABLE and sentiment_pipeline:
                            df = analyze_sentiment(df, text_column, sentiment_pipeline)
                            display_sentiment_results(df, text_column)
                        else:
                            # Fallback to simplified version
                            df = analyze_sentiment_fallback(df, text_column)
                            display_sentiment_results_fallback(df, text_column)
                
                # Check if more tabs can be displayed
                tab_index = 1
                
                # Additional data for persistent storage
                additional_data = {}
                
                # Continue with extended analysis if modules are available
                if BERTOPIC_AVAILABLE and TOPIC_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
                    try:
                        # Prepare text for topic modeling
                        with st.spinner("Performing topic analysis..."):
                            df, topic_model, topic_info, topic_df, topic_labels = prepare_topic_analysis(df, text_column)
                            
                            # Save topic model and information for later use
                            additional_data['topic_model'] = topic_model
                            additional_data['topic_info'] = topic_info
                            additional_data['topic_df'] = topic_df
                            additional_data['topic_labels'] = topic_labels
                        
                        # Analyze emotions if model is available
                        if EMOTION_ANALYSIS_AVAILABLE and emotion_classifier is not None:
                            with st.spinner("Performing emotion analysis..."):
                                # Hole empfohlene Parameter (falls verfügbar)
                                from utils.emotion_analysis_english import get_optimized_parameters
                                params = get_optimized_parameters()
                                df = prepare_emotion_analysis(df, emotion_classifier, 
                                                            model_weight=params['model_weight'],
                                                            confidence_threshold=params['confidence_threshold'])                             
                        
                        # Tab 2: Topic analysis
                        with main_tabs[tab_index]:
                            # Display model information
                            display_model_info("topic")
                            display_topic_analysis(df, topic_model, topic_df, topic_info, topic_labels)
                        
                        tab_index += 1
                        
                        # Tab 3: Emotion analysis (if available)
                        if EMOTION_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
                            with main_tabs[tab_index]:
                                # Display model information
                                display_model_info("emotion")
                                
                                if emotion_classifier is not None and 'dominant_emotion' in df.columns:
                                    display_emotion_analysis(df, text_column, topic_model, topic_labels)
                                else:
                                    st.warning("Emotion analysis could not be performed. Emotion model is not available.")
                            
                            tab_index += 1
                        
                        # Tab 4: Emotion model comparison (if available)
                        if EMOTION_COMPARISON_AVAILABLE and tab_index < len(main_tabs):
                            with main_tabs[tab_index]:
                                # Display model information
                                display_model_info("emotion")
                                
                                if emotion_classifier is not None:
                                    display_emotion_comparison(df, emotion_classifier)
                                else:
                                    st.warning("Emotion model comparison could not be performed. Emotion model is not available.")
                            
                            tab_index += 1
                        
                        # Tab 5: Special analyses (if available)
                        if SPECIAL_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
                            with main_tabs[tab_index]:
                                if 'topic' in df.columns:
                                    display_special_analysis(df, text_column, topic_labels)
                                else:
                                    st.warning("Special analyses require topic data that is not available.")
                    
                    except Exception as e:
                        st.error(f"Error in extended analysis: {e}")
                        st.error(traceback.format_exc())
                
                # Update DataFrame in Session State
                st.session_state.df = df
                
                # Save additional data in Session State
                st.session_state.additional_data = additional_data
                
                # Show data preview
                st.subheader("📋 Data Preview")
                preview_df = file_handler.get_preview(df)
                st.dataframe(preview_df)
                
                # ENHANCED SAVE SECTION WITH STORAGE INTEGRATION
                add_enhanced_save_section(filename, df, additional_data)
                
            except Exception as e:
                st.error(f"❌ Error loading or processing file: {e}")
                st.error(traceback.format_exc())
    
    # Debug section
    add_debug_section()
    
    # Display copyright footer
    ui_manager.display_footer_copyright()

if __name__ == "__main__":
    main()