"""
05_Kommentaranalyse_deutsch.py - Konservativ Modernisierte Version mit Storage-Integration
GEÄNDERT: Nur CSS-Duplikation entfernt, Pfade repariert, Storage-System integriert
BEIBEHALTEN: Komplette ursprüngliche Logik und Struktur
"""

import streamlit as st
from utils.debug_flag import is_debug
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
from utils.example_analyses import render_example_picker, known_source_names, repo_files_for_language
from utils.comment_file_reader import CommentFileError, error_message, read_comments
from utils.live_comment_analysis import (
    LiveAnalysisError, check_sentiment_result, free_other_language_models, is_cloud, is_live_result,
    limit_comments, live_max_comments, render_live_section, render_result_download, render_status,
    run_pending_analysis, sample_note)
from utils.safe_log import log_exception
from utils.live_comment_analysis import fmt_int
from utils.video_info import render_video, video_id_for_display
from models.pipeline_adapters import CachedPipeline

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
    from utils.sentiment_analysis import (analyze_sentiment, display_sentiment_results,
                                          perform_sentiment_analysis, SentimentAnalysisConfig)
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
# LIVE-ANALYSE (Ablauf ohne Bedienelemente; Steuerung in utils/live_comment_analysis.py)
# ================================================================================

LIVE_STEPS_DE = [
    "Datei lesen und bereinigen",
    "Sentiment-Modell laden und Kommentare bewerten",
    "Themen finden (BERTopic)",
    "Emotions-Modell laden und Emotionen erkennen",
]


EMOTION_RESULT_COLUMNS = ['emotions', 'dominant_emotion']


def _drop_emotion_columns(df):
    """Alle Emotions-Spalten entfernen (nichts erkannt -> keine Werte im Export, Review H1)."""
    from utils.emotion_analysis import EMOTION_LABEL_MAP
    names = list(EMOTION_LABEL_MAP.values())
    cols = [c for c in df.columns
            if c in EMOTION_RESULT_COLUMNS or c in names
            or any(c == f"{n}_linguistic" or c == f"{n}_sentence_count" for n in names)]
    return df.drop(columns=cols, errors='ignore')


def run_live_analysis_de(file_obj, request, progress):
    """Komplette Analyse in der bisherigen Reihenfolge (Sentiment → Themen → Emotionen), ohne Regler.

    Es gelten die Standardwerte der Oberfläche. Das Ergebnis wird erst nach dem vollständigen
    Lauf von run_pending_analysis() in die Sitzung geschrieben. Keine st.stop()/Bedienelemente.
    """
    notes = []

    progress.step(0)
    # Gemeinsamer Leser (Review H2): Format am Inhalt erkennen, Textspalte am Namen, kein Präfix
    try:
        df = read_comments(request["data"], request.get("name", ""))
    except CommentFileError as error:
        raise LiveAnalysisError(error_message(error, "de"))
    text_column = 'comment_text'
    df, total = limit_comments(df, live_max_comments())
    if len(df) < total:
        notes.append(sample_note('de', total, len(df)))
    df['clean_text'] = df[text_column].apply(clean_text)

    progress.step(1)
    if not (MODELS_AVAILABLE and SENTIMENT_ANALYSIS_AVAILABLE):
        raise LiveAnalysisError("Das Sentiment-Modell ist auf diesem Server nicht installiert.")
    free_other_language_models('de')   # Review M3: englische Modelle vorher freigeben
    try:
        sentiment_model = load_sentiment_model()
    except Exception as error:  # noqa: BLE001
        log_exception("live-analysis de", error, "Sentiment-Modell laden")
        raise LiveAnalysisError("Das Sentiment-Modell konnte nicht geladen werden. Bitte später erneut versuchen.")
    sentiment_pipeline = CachedPipeline(sentiment_model)
    df = perform_sentiment_analysis(df, text_column, sentiment_pipeline, SentimentAnalysisConfig())
    check_sentiment_result(df, 'de', notes)   # Review M6

    additional_data = {}
    progress.step(2)
    if BERTOPIC_AVAILABLE and TOPIC_ANALYSIS_AVAILABLE:
        df, topic_model, topic_info, topic_df, topic_labels = prepare_topic_analysis(df, text_column)
        if topic_model is not None:
            additional_data = {'topic_model': topic_model, 'topic_info': topic_info,
                               'topic_df': topic_df, 'topic_labels': topic_labels}
        else:
            notes.append("Themenanalyse übersprungen (zu wenige längere Kommentare oder Modell nicht verfügbar).")
    else:
        notes.append("Themenanalyse nicht verfügbar (BERTopic nicht installiert).")

    progress.step(3)
    if EMOTION_ANALYSIS_AVAILABLE and MODELS_AVAILABLE:
        try:
            emotion_classifier = load_emotion_model()
        except Exception as error:  # noqa: BLE001 – Review M2: Fehler wird nicht mehr gecacht
            log_exception("live-analysis de", error, "Emotions-Modell laden")
            emotion_classifier = None
        if emotion_classifier is not None:
            df = prepare_emotion_analysis(df, emotion_classifier, show_config_ui=False)
            recognized = int(df['emotions'].notna().sum()) if 'emotions' in df.columns else 0
            if recognized == 0:
                # keine erfundenen Ersatzwerte anzeigen oder exportieren
                df = _drop_emotion_columns(df)
                notes.append("Emotionen konnten nicht erkannt werden – der Emotions-Tab wird ausgeblendet.")
            elif recognized < len(df):
                notes.append(f"Emotionen erkannt für {fmt_int(recognized, 'de')} von {fmt_int(len(df), 'de')} "
                             f"Kommentaren (sehr kurze Kommentare werden nicht bewertet).")
        else:
            notes.append("Emotions-Modell konnte nicht geladen werden – der Emotions-Tab wird ausgeblendet.")

    return {"df": df, "text_column": text_column, "additional_data": additional_data, "notes": notes}


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
    
    """)
    st.markdown("Oben sehen Sie eine fertige Beispielanalyse, weiter unten können Sie eine eigene Analyse starten.")
    
    # Initialize Session State for persistent data (UNVERÄNDERT)
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
        
    if 'df' not in st.session_state:
        st.session_state.df = None
        
    if 'additional_data' not in st.session_state:
        st.session_state.additional_data = {}
        
    if 'text_column' not in st.session_state:
        st.session_state.text_column = None
    
    # Live-Analyse: angeforderten Lauf ausführen (zeigt nur den Fortschritt, danach Neustart der Seite)
    run_pending_analysis('de', run_live_analysis_de, LIVE_STEPS_DE)
    render_status('de')
    
    # Beispielanalysen immer oben (bzw. Info zur eigenen Analyse)
    render_example_picker('de')
    
    # Gespeicherte Analysen – nur lokal (die Cloud speichert nichts dauerhaft)
    if not is_cloud():
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
                                        st.session_state.result_source = "saved"
                                        st.session_state.example_lang = "de"
                                    
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
    
    # Emotionsmodell nur für den Modellvergleich einer eigenen Analyse (ist dann schon geladen).
    # Modelle werden sonst erst beim Start einer Live-Analyse geladen, nicht bei jedem Seitenaufruf.
    emotion_classifier = None
    if MODELS_AVAILABLE and is_live_result('de'):
        try:
            emotion_classifier = load_emotion_model()
        except Exception:
            emotion_classifier = None
    
    # CASE 1: Display existing analysis (KOMPLETTE URSPRÜNGLICHE LOGIK)
    if st.session_state.current_file and st.session_state.df is not None:
        df = st.session_state.df
        text_column = st.session_state.text_column
        
        # YouTube-Video nur für mitgelieferte Dateien/Beispiele (Review N6); Infos gecacht,
        # in der Cloud nur eingebettetes Video (Review M4)
        filename = st.session_state.current_file
        video_id = video_id_for_display(filename, known_source_names('de') + repo_files_for_language('de'))
        render_video(video_id, 'de', youtube_manager)
        
        # Create app tabs based on available data in df
        tabs_to_create = ["📊 Sentiment-Analyse"]
        
        # Check which analysis results are present in the data
        has_topic_model = st.session_state.additional_data.get('topic_model') is not None
        has_topic_labels = bool(st.session_state.additional_data.get('topic_labels'))
        if 'topic' in df.columns and has_topic_model:
            tabs_to_create.append("🏷️ Themen-Analyse")
        
        if 'dominant_emotion' in df.columns:
            tabs_to_create.append("😊 Emotions-Analyse")
            
            # More tabs depending on available data
            if EMOTION_COMPARISON_AVAILABLE and emotion_classifier is not None:
                tabs_to_create.append("⚖️ Emotionsmodell-Vergleich")
        
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE and has_topic_labels:
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
            elif 'sentiment' not in df.columns:
                # früher irreführend „Modul nicht verfügbar“ – tatsächlich fehlen die Ergebnisse
                st.warning("Für diese Daten liegt keine Sentiment-Analyse vor. Bitte unten eine Analyse starten.")
            else:
                st.warning("Sentiment-Analyse-Modul nicht verfügbar.")
        
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
        if 'dominant_emotion' in df.columns and EMOTION_COMPARISON_AVAILABLE and emotion_classifier is not None and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                # Display model information (same as emotion, since it's comparing emotion models)
                display_model_info("emotion")
                
                if emotion_classifier is not None:
                    display_emotion_comparison(df, emotion_classifier)
                else:
                    st.warning("Emotionsmodell-Vergleich konnte nicht angezeigt werden. Emotions-Modell nicht verfügbar.")
            
            tab_index += 1
        
        # Show special analyses when data is available
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE and has_topic_labels and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                topic_labels = st.session_state.additional_data.get('topic_labels')
                if topic_labels:
                    display_special_analysis(df, text_column, topic_labels)
                else:
                    st.warning("Spezialanalysen erfordern Themen-Daten, die nicht vollständig verfügbar sind.")
        
        # Show data preview
        st.subheader("📋 Datenvorschau")
        st.dataframe(df.head())
        render_result_download('de')
        
        # ERWEITERTE SAVE-SEKTION MIT STORAGE-INTEGRATION (nur lokal)
        if not is_cloud(): add_enhanced_save_section(
            st.session_state.current_file, 
            df, 
            st.session_state.additional_data
        )
    
    # Eigene Analyse starten (unter den Beispielen) – ersetzt den früheren CASE 2
    render_live_section('de', repo_files_for_language('de'))   # Review N5: nur deutsche Dateien
    
    # Debug section (nur mit HEREDUCATION_DEBUG=1 oder secrets debug=true)
    if is_debug():
        add_debug_section()
    
    # ===== MODERNER FOOTER (ersetzt CSS-Duplikation) =====
    display_standard_footer()

# ===== AUSFÜHRUNG =====
if __name__ == "__main__":
    main()
else:
    # Wird ausgeführt wenn als Streamlit Page importiert
    main()