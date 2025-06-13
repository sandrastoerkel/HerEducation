"""
05_Kommentaranalyse_deutsch.py - Konservativ Modernisierte Version mit Storage-Integration
GEÄNDERT: Nur CSS-Duplikation entfernt, Pfade repariert, Storage-System integriert
BEIBEHALTEN: Komplette ursprüngliche Logik und Struktur
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import traceback
import os
import json
import pickle
from datetime import datetime
from pathlib import Path
import sys

# ===== MODERNE PAGE-SETUP (ersetzt 40+ Zeilen CSS) =====
from utils.shared_components import setup_standard_page, display_standard_footer

# ===== PFAD-KONFIGURATION MIT RELATIVEN PFADEN (repariert) =====
APP_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = APP_ROOT / "data" / "comments"
RESULTS_DIR = APP_ROOT / "saved_results"

# Erstelle Verzeichnisse falls sie nicht existieren
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ===== IMPORT MODULES (unverändert) =====
from utils.kommentaranalyse_persistence import KommentaranalysePersistence
from utils.kommentaranalyse_file_handler import KommentaranalyseFileHandler
from utils.kommentaranalyse_youtube import KommentaranalyseYouTube
from utils.kommentaranalyse_ui import KommentaranalyseUI

# ===== STORAGE-SYSTEM INTEGRATION =====
try:
    from analysis_storage_system import add_save_button_to_analysis
    STORAGE_SYSTEM_AVAILABLE = True
except ImportError:
    STORAGE_SYSTEM_AVAILABLE = False

try:
    from utils.country_analysis_storage_deutsch import CountryAnalysisStorageDeutsch
    COUNTRY_STORAGE_AVAILABLE = True
except ImportError:
    COUNTRY_STORAGE_AVAILABLE = False
# ===== INITIALISIERE MANAGER (unverändert) =====
persistence_manager = KommentaranalysePersistence(RESULTS_DIR)
file_handler = KommentaranalyseFileHandler(DATA_DIR)
youtube_manager = KommentaranalyseYouTube()
ui_manager = KommentaranalyseUI()

# Suppress tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ===== PAGE CONFIG wird von setup_standard_page() übernommen =====
# Kein separates st.set_page_config() mehr nötig!

# ================================================================================
# PERSISTENCE FUNCTIONS (unverändert - verwenden Manager)
# ================================================================================

def get_results_dir():
    """Creates and returns the directory for saved results - USING RELATIVE PATHS"""
    return RESULTS_DIR

def save_analysis_results(filename, df, additional_data=None):
    """Speichert Analyseergebnisse mit Persistence Manager"""
    return persistence_manager.save_analysis_results(filename, df, additional_data)

def load_analysis_results(filename):
    """Lädt gespeicherte Analyseergebnisse mit Persistence Manager"""
    return persistence_manager.load_analysis_results(filename)

def get_available_analyses():
    """Gibt eine Liste der verfügbaren gespeicherten Analysen zurück"""
    return persistence_manager.get_available_analyses()

# ================================================================================
# FILE HANDLING FUNCTIONS (unverändert - verwenden File Handler)
# ================================================================================

def get_files_from_data_folder():
    """Returns a list of all CSV files in the specified data folder"""
    return file_handler.get_files_from_data_folder()

def clean_csv_data(file_content):
    """Cleans the CSV file and extracts the comment column"""
    return file_handler.clean_csv_data(file_content)

def clean_text(text):
    """Clean text for topic analysis"""
    return file_handler.clean_text(text)

def load_and_clean_data(uploaded_file):
    """Loads and cleans the uploaded file"""
    return file_handler.load_and_clean_data(uploaded_file)

# ================================================================================
# YOUTUBE INFO FUNCTIONS (unverändert - verwenden YouTube Manager)
# ================================================================================

def extract_video_id(filename):
    """Extracts the YouTube video ID from the filename"""
    return file_handler.extract_video_id(filename)

def get_video_info(video_id):
    """Retrieves information about a YouTube video based on its ID"""
    return youtube_manager.get_video_info(video_id)

def display_youtube_info(video_id):
    """Shows YouTube video information"""
    youtube_manager.display_youtube_info(video_id)

# ================================================================================
# UI COMPONENTS (unverändert - verwenden UI Manager)
# ================================================================================

def display_model_info(model_type):
    """Displays information about the models used"""
    ui_manager.display_model_info(model_type)

# ================================================================================
# ENHANCED SAVE SECTION WITH STORAGE INTEGRATION
# ================================================================================

def add_enhanced_save_section(filename, df, additional_data=None):
    """Erweiterte Speicher-Sektion mit Storage-System-Integration"""
    
    # Bestehende Download-Funktionalität beibehalten
    st.download_button(
        label="💾 Daten als CSV speichern",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"{Path(filename).stem}_analyse.csv",
        mime='text/csv'
    )
    
    # Save options in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Bestehende Speicher-Funktionalität
        if st.button("💾 Analyseergebnisse speichern", key=f"save_legacy_{filename}"):
            if save_analysis_results(filename, df, additional_data):
                st.success(f"✅ Analyseergebnisse für '{filename}' wurden erfolgreich gespeichert!")
                st.rerun()
    
    with col2:
        # NEUE STORAGE-SYSTEM-INTEGRATION
        if STORAGE_SYSTEM_AVAILABLE:
            # Video-Info für Metadaten extrahieren (falls verfügbar)
            video_info = {}
            try:
                video_id = extract_video_id(filename)
                if video_id:
                    video_data = get_video_info(video_id)
                    if video_data:
                        video_info = {
                            "title": video_data.get('title'),
                            "channel": video_data.get('author')
                        }
            except:
                pass  # Falls Video-Info nicht verfügbar ist
            
            # Storage-System Save-Button hinzufügen
            add_save_button_to_analysis(
                df=df,
                analysis_type="sentiment_emotion_topic_german",
                language="de",
                video_info=video_info
            )
        else:
            st.info("💡 Storage-System für Länder-Analyse nicht verfügbar")

    if COUNTRY_STORAGE_AVAILABLE:
        if st.button("🌍 Für Länder-Analyse speichern", key=f"country_export_{filename}"):
            with st.spinner("Speichere für Länder-Analyse..."):
                storage = CountryAnalysisStorageDeutsch()
                result = storage.export_with_smart_labels(df, filename, additional_data)
                
                if result.success:
                    st.success("✅ Erfolgreich für Länder-Analyse gespeichert!")
                    st.info(f"📁 Datei: `{result.file_path.name}`")
                    st.info(f"🌍 Land: **{result.country_detected}**")
                    st.info(f"🏷️ Smart Labels: {result.smart_labels_added} hinzugefügt")
                    if result.warnings:
                        st.warning("⚠️ Hinweise: " + ", ".join(result.warnings))
                else:
                    st.error(f"❌ Fehler beim Speichern: {result.error_message}")
    else:
        st.info("💡 Country Analysis Storage nicht verfügbar")

# ================================================================================
# MODEL LOADING AND DEPENDENCY CHECKS (KOMPLETT UNVERÄNDERT)
# ================================================================================

# Try to import necessary libraries with error handling
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly ist nicht installiert. Einige Visualisierungen werden nicht verfügbar sein.")

# Try to import utility modules with detailed error handling
try:
    # Import from the parent directory (since we're in pages/)
    sys.path.append(str(Path(__file__).parent.parent))
    
    from models.model_loader import load_sentiment_model, load_emotion_model, load_bertopic_model
    MODELS_AVAILABLE = True
except ImportError as e:
    MODELS_AVAILABLE = False
    st.warning(f"Modelle konnten nicht geladen werden: {e}")

# Check if BERTopic is available
try:
    from utils.check_dependencies import is_bertopic_available
    BERTOPIC_CHECKED = True
    BERTOPIC_AVAILABLE = is_bertopic_available()
except ImportError:
    BERTOPIC_CHECKED = False
    BERTOPIC_AVAILABLE = False
    st.warning("BERTopic-Abhängigkeitsprüfung konnte nicht geladen werden.")

# Try to import analysis modules
try:
    from utils.sentiment_analysis import analyze_sentiment, display_sentiment_results
    SENTIMENT_ANALYSIS_AVAILABLE = True
except ImportError as e:
    SENTIMENT_ANALYSIS_AVAILABLE = False
    st.warning(f"Sentiment-Analyse-Modul nicht verfügbar: {e}")

try:
    from utils.topic_analysis import prepare_topic_analysis, display_topic_analysis
    TOPIC_ANALYSIS_AVAILABLE = True
except ImportError as e:
    TOPIC_ANALYSIS_AVAILABLE = False
    st.warning(f"Themen-Analyse-Modul nicht verfügbar: {e}")

try:
    from utils.emotion_analysis import prepare_emotion_analysis, display_emotion_analysis
    EMOTION_ANALYSIS_AVAILABLE = True
except ImportError as e:
    EMOTION_ANALYSIS_AVAILABLE = False
    st.warning(f"Emotions-Analyse-Modul nicht verfügbar: {e}")

try:
    from utils.emotion_comparison import display_emotion_comparison
    EMOTION_COMPARISON_AVAILABLE = True
except ImportError as e:
    EMOTION_COMPARISON_AVAILABLE = False
    st.warning(f"Emotions-Vergleichs-Modul nicht verfügbar: {e}")

try:
    from utils.special_analysis import display_special_analysis
    SPECIAL_ANALYSIS_AVAILABLE = True
except ImportError as e:
    SPECIAL_ANALYSIS_AVAILABLE = False
    st.warning(f"Spezial-Analyse-Modul nicht verfügbar: {e}")

# ================================================================================
# DEBUG SECTION (unverändert)
# ================================================================================

def add_debug_section():
    """Debug section for testing - USING UI MANAGER"""
    ui_manager.show_debug_section(persistence_manager, RESULTS_DIR)

# ================================================================================
# MAIN APPLICATION (KOMPLETTE URSPRÜNGLICHE LOGIK BEIBEHALTEN)
# ================================================================================

def main():
    # ===== MODERNER HEADER (ersetzt CSS-Duplikation) =====
    # Page-Config wird bereits von setup_standard_page() gesetzt
    setup_standard_page("Kommentaranalyse (Deutsch)", "🗣️")
    st.title("Kommentaranalyse (Deutsch)")
    st.markdown("""
    Diese Seite ermöglicht die Analyse von deutschen Kommentaren hinsichtlich:
    - 💭 **Sentiment** (positiv/negativ/neutral)
    - 😊 **Emotionen** (Freude, Trauer, Angst, etc.)
    - 🏷️ **Themen** und Schlüsselkonzepte
    
    Laden Sie eine CSV-Datei mit Kommentaren hoch, um die Analyse zu starten.
    """)
    
    # Initialize Session State for persistent data (UNVERÄNDERT)
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
        
    if 'df' not in st.session_state:
        st.session_state.df = None
        
    if 'additional_data' not in st.session_state:
        st.session_state.additional_data = {}
        
    if 'text_column' not in st.session_state:
        st.session_state.text_column = None
    
    # Container for previous analyses (UNVERÄNDERT)
    with st.expander("📁 Gespeicherte Analysen", expanded=False):
        try:
            available_analyses = get_available_analyses()
            
            if not available_analyses:
                st.info("Keine gespeicherten Analysen gefunden.")
            else:
                # Show table with saved analyses
                analyses_df = pd.DataFrame(available_analyses)
                try:
                    analyses_df['date'] = pd.to_datetime(analyses_df['date'])
                    analyses_df = analyses_df.sort_values('date', ascending=False)
                except Exception as e:
                    st.warning(f"Fehler beim Verarbeiten der Datumsangaben: {e}")
                
                st.dataframe(analyses_df)
                
                # Ensure the options list is never empty
                if len(analyses_df) > 0:
                    filenames = analyses_df['filename'].tolist()
                    if filenames:  # Additional safety check
                        # Safe call to selectbox with default index
                        selected_file = st.selectbox(
                            "Gespeicherte Analyse laden:",
                            options=filenames,
                            index=0  # The first entry is selected by default
                        )
                        
                        if st.button("Analyse laden"):
                            with st.spinner(f"Lade Analyse für '{selected_file}'..."):
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
                                    
                                    st.success(f"Analyse für '{selected_file}' erfolgreich geladen!")
                                    st.rerun()
                                else:
                                    st.error(f"Konnte keine Daten für '{selected_file}' laden.")
        except Exception as e:
            st.error(f"Fehler beim Laden der gespeicherten Analysen: {e}")
            st.info("Sie können trotzdem eine neue Analyse durchführen, indem Sie eine Datei hochladen.")
    
    # Display current file (UNVERÄNDERT)
    if st.session_state.current_file:
        st.info(f"📄 Aktuelle Analyse: {st.session_state.current_file}")
        
        # Option to reset
        if st.button("🔄 Neue Analyse starten"):
            st.session_state.current_file = None
            st.session_state.df = None
            st.session_state.text_column = None
            st.session_state.additional_data = {}
            st.rerun()
    
    # Load sentiment model if available (UNVERÄNDERT)
    sentiment_pipeline = None
    emotion_classifier = None
    
    if MODELS_AVAILABLE:
        with st.spinner("Lade Sentiment-Modell..."):
            try:
                sentiment_pipeline = load_sentiment_model()
                st.success("✅ Sentiment-Modell erfolgreich geladen!")
            except Exception as e:
                st.error(f"❌ Fehler beim Laden des Sentiment-Modells: {e}")
        
        with st.spinner("Lade Emotions-Modell..."):
            try:
                emotion_classifier = load_emotion_model()
                if emotion_classifier:
                    st.success("✅ Emotions-Modell erfolgreich geladen!")
            except Exception as e:
                st.error(f"❌ Fehler beim Laden des Emotions-Modells: {e}")
    
    # CASE 1: Display existing analysis (KOMPLETTE URSPRÜNGLICHE LOGIK)
    if st.session_state.current_file and st.session_state.df is not None:
        df = st.session_state.df
        text_column = st.session_state.text_column
        
        # Extract YouTube ID from filename
        filename = st.session_state.current_file
        video_id = file_handler.extract_video_id(filename)
        
        # Show YouTube information
        if video_id:
            display_youtube_info(video_id)
        
        # Create app tabs based on available data in df
        tabs_to_create = ["📊 Sentiment-Analyse"]
        
        # Check which analysis results are present in the data
        if 'topic' in df.columns:
            tabs_to_create.append("🏷️ Themen-Analyse")
        
        if 'dominant_emotion' in df.columns:
            tabs_to_create.append("😊 Emotions-Analyse")
            
            # More tabs depending on available data
            if EMOTION_COMPARISON_AVAILABLE:
                tabs_to_create.append("⚖️ Emotionsmodell-Vergleich")
        
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE:
            tabs_to_create.append("🔍 Spezial-Analysen")
        
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
                st.warning("Sentiment-Analyse-Modul nicht verfügbar.")
        
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
                    st.warning("Themenanalyse konnte nicht angezeigt werden. Erforderliche Daten fehlen.")
            
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
                    st.warning("Emotionsanalyse konnte nicht angezeigt werden. Erforderliches Modul nicht verfügbar.")
            
            tab_index += 1
        
        # Show emotion model comparison when data is available
        if 'dominant_emotion' in df.columns and EMOTION_COMPARISON_AVAILABLE and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                # Display model information (same as emotion, since it's comparing emotion models)
                display_model_info("emotion")
                
                if emotion_classifier is not None:
                    display_emotion_comparison(df, emotion_classifier)
                else:
                    st.warning("Emotionsmodell-Vergleich konnte nicht angezeigt werden. Emotions-Modell nicht verfügbar.")
            
            tab_index += 1
        
        # Show special analyses when data is available
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                topic_labels = st.session_state.additional_data.get('topic_labels')
                if topic_labels:
                    display_special_analysis(df, text_column, topic_labels)
                else:
                    st.warning("Spezialanalysen erfordern Themen-Daten, die nicht vollständig verfügbar sind.")
        
        # Show data preview
        st.subheader("📋 Datenvorschau")
        st.dataframe(df.head())
        
        # ERWEITERTE SAVE-SEKTION MIT STORAGE-INTEGRATION
        add_enhanced_save_section(
            st.session_state.current_file, 
            df, 
            st.session_state.additional_data
        )
    
    # CASE 2: Perform new analysis (KOMPLETTE URSPRÜNGLICHE LOGIK)
    else:
        # Get CSV files from the specified data folder
        available_csv_files = get_files_from_data_folder()
        
        # Flag for file processing
        processed_file = None
        
        # Container for file selection
        file_selection_container = st.container()
        
        with file_selection_container:
            # Option 1: Select file from data folder
            if available_csv_files:
                st.write("### 📁 Datei aus dem Datenordner auswählen")
                selected_csv_path = st.selectbox(
                    "CSV-Datei aus dem Ordner auswählen:",
                    options=available_csv_files,
                    format_func=lambda x: Path(x).name
                )
                
                if st.button("🔍 Ausgewählte Datei analysieren"):
                    try:
                        # Load file from data folder
                        with open(selected_csv_path, 'rb') as f:
                            file_content = f.read()
                            
                        # Convert to BytesIO object (simulates an uploaded file)
                        from io import BytesIO
                        processed_file = BytesIO(file_content)
                        processed_file.name = Path(selected_csv_path).name
                    except Exception as e:
                        st.error(f"Fehler beim Lesen der ausgewählten Datei: {e}")
            else:
                st.warning(f"❌ Keine CSV-Dateien im Datenordner gefunden.")
                st.info("📝 Bitte legen Sie CSV-Dateien in diesem Ordner ab oder nutzen Sie die Upload-Option unten.")
            
            # Option 2: Upload file
            st.write("### 📤 Datei hochladen")
            uploaded_file = st.file_uploader("CSV- oder JSON-Datei mit Kommentaren hochladen:", type=["csv", "json", "jsonl"])
            
            if uploaded_file is not None:
                processed_file = uploaded_file
        
        # Process the selected file (KOMPLETTE URSPRÜNGLICHE LOGIK)
        if processed_file is not None:
            try:
                # Filename for YouTube ID extraction
                filename = processed_file.name
                st.write(f"🔄 Verarbeite Datei: **{filename}**")
                
                # Extract YouTube video ID if present in filename
                video_id = file_handler.extract_video_id(filename)
                
                # Show YouTube information if video ID was found
                if video_id:
                    youtube_manager.display_youtube_info(video_id)
                
                # Load and clean data
                with st.spinner("Lade und bereinige Daten..."):
                    df, text_column = load_and_clean_data(processed_file)
                    
                    # Clean text for further analysis
                    df['clean_text'] = df[text_column].apply(clean_text)
                
                # Save in Session State
                st.session_state.current_file = filename
                st.session_state.df = df
                st.session_state.text_column = text_column
                
                # Create app tabs based on available modules
                tabs_to_create = ["📊 Sentiment-Analyse"]
                
                if BERTOPIC_AVAILABLE and TOPIC_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("🏷️ Themen-Analyse")
                
                if EMOTION_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("😊 Emotions-Analyse")
                
                if EMOTION_COMPARISON_AVAILABLE:
                    tabs_to_create.append("⚖️ Emotionsmodell-Vergleich")
                
                if SPECIAL_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("🔍 Spezial-Analysen")
                
                # Create tabs
                if len(tabs_to_create) > 1:
                    main_tabs = st.tabs(tabs_to_create)
                else:
                    main_tabs = [st]
                
                # Tab 1: Sentiment Analysis
                with main_tabs[0]:
                    # Display model information
                    display_model_info("sentiment")
                    
                    with st.spinner("Führe Sentiment-Analyse durch..."):
                        if SENTIMENT_ANALYSIS_AVAILABLE and sentiment_pipeline:
                            df = analyze_sentiment(df, text_column, sentiment_pipeline)
                            display_sentiment_results(df, text_column)
                        else:
                            st.warning("Sentiment-Analyse nicht verfügbar. Module fehlen.")
                
                # Check if more tabs can be displayed
                tab_index = 1
                
                # Additional data for persistent storage
                additional_data = {}
                
                # Continue with extended analysis if modules are available
                if BERTOPIC_AVAILABLE and TOPIC_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
                    try:
                        # Prepare text for topic modeling
                        with st.spinner("Führe Themenanalyse durch..."):
                            df, topic_model, topic_info, topic_df, topic_labels = prepare_topic_analysis(df, text_column)
                            
                            # Save topic model and information for later use
                            additional_data['topic_model'] = topic_model
                            additional_data['topic_info'] = topic_info
                            additional_data['topic_df'] = topic_df
                            additional_data['topic_labels'] = topic_labels
                        
                        # Analyze emotions if model is available
                        if EMOTION_ANALYSIS_AVAILABLE and emotion_classifier is not None:
                            with st.spinner("Führe Emotionsanalyse durch..."):
                                # Hole empfohlene Parameter (falls verfügbar)
                                from utils.emotion_analysis import get_optimized_parameters
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
                                    st.warning("Emotionsanalyse konnte nicht durchgeführt werden. Emotions-Modell nicht verfügbar.")
                            
                            tab_index += 1
                        
                        # Tab 4: Emotion model comparison (if available)
                        if EMOTION_COMPARISON_AVAILABLE and tab_index < len(main_tabs):
                            with main_tabs[tab_index]:
                                # Display model information
                                display_model_info("emotion")
                                
                                if emotion_classifier is not None:
                                    display_emotion_comparison(df, emotion_classifier)
                                else:
                                    st.warning("Emotionsmodell-Vergleich konnte nicht durchgeführt werden. Emotions-Modell nicht verfügbar.")
                            
                            tab_index += 1
                        
                        # Tab 5: Special analyses (if available)
                        if SPECIAL_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
                            with main_tabs[tab_index]:
                                if 'topic' in df.columns:
                                    display_special_analysis(df, text_column, topic_labels)
                                else:
                                    st.warning("Spezialanalysen erfordern Themen-Daten, die nicht verfügbar sind.")
                    
                    except Exception as e:
                        st.error(f"Fehler bei der erweiterten Analyse: {e}")
                        st.error(traceback.format_exc())
                
                # Update DataFrame in Session State
                st.session_state.df = df
                
                # Save additional data in Session State
                st.session_state.additional_data = additional_data
                
                # Show data preview
                st.subheader("📋 Datenvorschau")
                st.dataframe(df.head())
                
                # ERWEITERTE SAVE-SEKTION MIT STORAGE-INTEGRATION
                add_enhanced_save_section(filename, df, additional_data)
                
            except Exception as e:
                st.error(f"❌ Fehler beim Laden oder Verarbeiten der Datei: {e}")
                st.error(traceback.format_exc())
    
    # Debug section (UNVERÄNDERT)
    add_debug_section()
    
    # ===== MODERNER FOOTER (ersetzt CSS-Duplikation) =====
    display_standard_footer()

# ===== AUSFÜHRUNG =====
if __name__ == "__main__":
    main()
else:
    # Wird ausgeführt wenn als Streamlit Page importiert
    main()