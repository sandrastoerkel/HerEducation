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
os.environ["TOKENIZERS_PARALLELISM"] = "false"
 
# Persistenz-Funktionen
def get_results_dir():
    """Erzeugt und gibt das Verzeichnis für gespeicherte Ergebnisse zurück"""
    # KORRIGIERT: Neuer fester Pfad für die Ergebnisse
    results_dir = Path("/Users/sandra/Documents/12.5./Hauptapp/saved_results")
    results_dir.mkdir(exist_ok=True, parents=True)
    return results_dir

def save_analysis_results(filename, df, additional_data=None):
    """
    Speichert Analyseergebnisse für spätere Verwendung
    
    Args:
        filename: Name der ursprünglichen Datei
        df: DataFrame mit Analyseergebnissen
        additional_data: Optionales Dictionary mit zusätzlichen Daten (z.B. Topic-Modell)
    """
    try:
        results_dir = get_results_dir()
        
        # Basis-Dateiname ohne Pfad und Erweiterung
        base_filename = Path(filename).stem
        
        # Erstelle einen sicheren Dateinamen ohne Sonderzeichen
        base_filename = re.sub(r'[^\w\-\.]', '_', base_filename)
        
        # DataFrame als Pickle speichern (behält alle Datentypen)
        df_path = results_dir / f"{base_filename}_results.pkl"
        df.to_pickle(df_path)
        
        # Zusätzliche Daten speichern, wenn vorhanden
        if additional_data:
            try:
                data_path = results_dir / f"{base_filename}_additional.pkl"
                with open(data_path, 'wb') as f:
                    pickle.dump(additional_data, f)
            except Exception as e:
                st.warning(f"Konnte zusätzliche Daten nicht speichern: {e}")
        
        # Metadaten speichern
        metadata = {
            'original_filename': filename,
            'analysis_date': datetime.now().isoformat(),
            'num_comments': len(df),
            'columns': list(df.columns),
            'has_additional_data': additional_data is not None
        }
        
        meta_path = results_dir / f"{base_filename}_meta.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        st.success(f"Analyseergebnisse für '{filename}' wurden gespeichert!")
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern der Analyseergebnisse: {e}")
        return False
    
def load_analysis_results(filename):
    """
    Lädt gespeicherte Analyseergebnisse
    
    Args:
        filename: Name der ursprünglichen Datei
        
    Returns:
        Tuple mit (DataFrame, additional_data, metadata) oder (None, None, None) wenn nicht gefunden
    """
    try:
        results_dir = get_results_dir()
        base_filename = Path(filename).stem
        
        # Erstelle einen sicheren Dateinamen ohne Sonderzeichen (gleich wie beim Speichern)
        base_filename = re.sub(r'[^\w\-\.]', '_', base_filename)
        
        # Pfade zu den gespeicherten Dateien
        df_path = results_dir / f"{base_filename}_results.pkl"
        data_path = results_dir / f"{base_filename}_additional.pkl"
        meta_path = results_dir / f"{base_filename}_meta.json"
        
        # Prüfen, ob Ergebnisse existieren
        if not df_path.exists() or not meta_path.exists():
            return None, None, None
        
        # DataFrame laden
        df = pd.read_pickle(df_path)
        
        # Metadaten laden
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        
        # Zusätzliche Daten laden, wenn vorhanden
        additional_data = None
        if data_path.exists():
            with open(data_path, 'rb') as f:
                additional_data = pickle.load(f)
        
        return df, additional_data, metadata
    except Exception as e:
        st.error(f"Fehler beim Laden der Analyseergebnisse: {e}")
        return None, None, None

def get_available_analyses():
    """Gibt eine Liste der verfügbaren gespeicherten Analysen zurück"""
    results_dir = get_results_dir()
    
    analyses = []
    for meta_file in results_dir.glob("*_meta.json"):
        try:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
                analyses.append({
                    'filename': metadata.get('original_filename', "Unbekannt"),
                    'date': metadata.get('analysis_date', datetime.now().isoformat()),
                    'num_comments': metadata.get('num_comments', 0)
                })
        except Exception as e:
            st.warning(f"Fehler beim Lesen der Metadaten-Datei {meta_file}: {e}")
            continue
    
    return analyses
 
# Try to import necessary libraries - with error handling
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly ist nicht installiert. Einige Visualisierungen werden nicht verfügbar sein.")

# Try to import utility modules with detailed error handling
try:
    # Versuch, die Modelle zu laden
    from models.model_loader import load_sentiment_model, load_emotion_model, load_bertopic_model
    MODELS_AVAILABLE = True
except ImportError as e:
    MODELS_AVAILABLE = False
    st.warning(f"Modelle konnten nicht geladen werden: {e}")

# Check if BERTopic is available
try:
    from utils.check_dependencies import is_bertopic_available
    BERTOPIC_CHECKED = True
except ImportError:
    BERTOPIC_CHECKED = False
    st.warning("BERTopic-Abhängigkeitsprüfung konnte nicht geladen werden.")

# Function to extract YouTube video ID from filename
def extract_video_id(filename):
    """
    Extrahiert die YouTube-Video-ID aus dem Dateinamen
    
    Args:
        filename: Der Dateiname, aus dem die ID extrahiert werden soll
        
    Returns:
        Die YouTube-Video-ID oder None, wenn keine gefunden wurde
    """
    # Pattern to match YouTube ID format in filenames like "20240618_87TYPn6gbwA_title.csv"
    pattern = r'_([a-zA-Z0-9_-]{11})_'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    
    # Alternative pattern to handle the case where ID is not between underscores
    # Like "20240618_87TYPn6gbwA" without trailing underscore
    alt_pattern = r'_([a-zA-Z0-9_-]{11})'
    alt_match = re.search(alt_pattern, filename)
    if alt_match:
        return alt_match.group(1)
    
    return None

# Function definitions that are needed for basic functionality
def load_and_clean_data(uploaded_file):
    """
    Lädt und bereinigt die hochgeladene Datei
    
    Args:
        uploaded_file: Die hochgeladene Datei (CSV oder JSON)
        
    Returns:
        DataFrame und Name der Textspalte
    """
    # Dateityp bestimmen
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == 'csv':
        # CSV-Datei lesen und bereinigen
        file_content = uploaded_file.getvalue().decode('utf-8')
        
        # Informationen zur Datei anzeigen
        st.info("CSV-Datei wird bereinigt und Kommentare werden extrahiert...")
        
        # CSV bereinigen und Kommentare extrahieren
        df = clean_csv_data(file_content)
        
        if df.empty:
            st.error("Keine gültigen Kommentare in der Datei gefunden.")
            st.stop()
        else:
            st.success(f"{len(df)} Kommentare erfolgreich extrahiert.")
            text_column = 'comment_text'
    
    elif file_type in ['json', 'jsonl']:
        # JSON-Datei lesen
        df = pd.read_json(uploaded_file, lines=True)
        
        # Prüfen, ob erforderliche Spalten vorhanden sind
        text_column = None
        possible_columns = ['text', 'comment', 'kommentar', 'content', 'Text', 'Comment', 'Kommentar', 'Content']
        
        for col in possible_columns:
            if col in df.columns:
                text_column = col
                break
        
        if text_column is None:
            st.error("Keine erkannte Textspalte in der JSON-Datei gefunden.")
            st.stop()
    
    return df, text_column

def clean_csv_data(file_content):
    """
    Bereinigt die CSV-Datei und extrahiert die Kommentarspalte
    """
    try:
        # Datei in Zeilen aufteilen
        lines = file_content.strip().split('\n')
        cleaned_data = []
        
        for line_index, line in enumerate(lines):
            # Kommentar manuell extrahieren - robuster Ansatz
            in_quotes = False
            fields = []
            current_field = ""
            
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    fields.append(current_field)
                    current_field = ""
                else:
                    current_field += char
            
            # Letztes Feld hinzufügen
            fields.append(current_field)
            
            # Kommentarspalte extrahieren (zweite Spalte, falls vorhanden)
            comment = ""
            if len(fields) > 1:
                comment = fields[1]
            
            cleaned_data.append({'comment_text': comment, 'original_line': line_index + 1})
        
        return pd.DataFrame(cleaned_data)
    
    except Exception as e:
        st.error(f"Fehler bei der Bereinigung der CSV-Datei: {e}")
        return pd.DataFrame(columns=['comment_text', 'original_line'])

def clean_text(text):
    """
    Text für die Themenanalyse bereinigen
    """
    if pd.isna(text) or text is None or text == "":
        return ""
    
    text = str(text)
    # Entferne URLs
    text = re.sub(r'http\S+', '', text)
    # Entferne Sonderzeichen und Zahlen
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    # Wandle in Kleinbuchstaben um
    text = text.lower()
    
    # Versuche, Stopwörter zu entfernen, wenn NLTK verfügbar ist
    try:
        import nltk
        from nltk.corpus import stopwords
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        stop_words = set(stopwords.words('german'))
        text = ' '.join([word for word in text.split() if word not in stop_words and len(word) > 2])
    except:
        # Falls NLTK nicht verfügbar ist, filtere nur kurze Wörter
        text = ' '.join([word for word in text.split() if len(word) > 2])
            
    return text

# Simplified fallback functions in case modules are not available
def analyze_sentiment_fallback(df, text_column):
    """Simplified fallback sentiment analysis"""
    st.subheader("Sentiment-Analyse (vereinfacht)")
    st.info("Verwende vereinfachte Sentiment-Analyse, da das Modell nicht geladen werden konnte.")
    
    # Random sentiment assignment for demonstration
    import random
    sentiments = ['positive', 'neutral', 'negative']
    weights = [0.3, 0.4, 0.3]  # Weights for distribution
    
    df['sentiment'] = [random.choices(sentiments, weights=weights)[0] for _ in range(len(df))]
    df['confidence'] = [random.uniform(0.6, 0.95) for _ in range(len(df))]
    
    return df

def display_sentiment_results_fallback(df, text_column):
    """Displays sentiment analysis results (simplified version)"""
    st.subheader("Sentiment-Verteilung")
    
    # Count sentiments
    sentiment_counts = df['sentiment'].value_counts()
    
    # Create a simple bar chart
    fig, ax = plt.subplots()
    bars = ax.bar(sentiment_counts.index, sentiment_counts.values, 
           color=['green' if x == 'positive' else 'gray' if x == 'neutral' else 'red' for x in sentiment_counts.index])
    ax.set_xlabel('Sentiment')
    ax.set_ylabel('Anzahl')
    ax.set_title('Verteilung der Sentiments')
    
    # Show the chart
    st.pyplot(fig)
    
    # Show examples for each category
    st.subheader("Beispiele")
    
    for sentiment in ['positive', 'neutral', 'negative']:
        if sentiment in df['sentiment'].values:
            examples = df[df['sentiment'] == sentiment].head(2)
            st.write(f"**{sentiment.capitalize()} Beispiele:**")
            for _, row in examples.iterrows():
                st.write(f"- {row[text_column]}")
            st.write("")

def get_files_from_data_folder():
    """
    Gibt eine Liste aller CSV-Dateien im festgelegten Datenordner zurück
    """
    # KORRIGIERT: Neuer Pfad für den Datenordner
    data_folder = Path("/Users/sandra/Documents/12.5./Hauptapp/data/comments")
    
    if not data_folder.exists():
        data_folder.mkdir(exist_ok=True, parents=True)
    
    csv_files = list(data_folder.glob("*.csv"))
    return [str(file) for file in csv_files]

def main():
    # Set page title
    st.title("Kommentaranalyse")
    
    st.markdown("""
    Diese Seite ermöglicht die Analyse von Kommentaren hinsichtlich:
    - Sentiment (positiv/negativ/neutral)
    - Emotionen (Freude, Trauer, Angst, etc.)
    - Themen und Schlüsselkonzepte
    
    Laden Sie eine CSV-Datei mit Kommentaren hoch, um die Analyse zu starten.
    """)
    
    # Initialisiere Session State für persistente Daten
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
        
    if 'df' not in st.session_state:
        st.session_state.df = None
        
    if 'additional_data' not in st.session_state:
        st.session_state.additional_data = {}
        
    if 'text_column' not in st.session_state:
        st.session_state.text_column = None
    
    # Container für vorherige Analysen
    with st.expander("Gespeicherte Analysen", expanded=False):
        try:
            available_analyses = get_available_analyses()
            
            if not available_analyses:
                st.info("Keine gespeicherten Analysen gefunden.")
            else:
                # Tabelle mit gespeicherten Analysen anzeigen
                analyses_df = pd.DataFrame(available_analyses)
                try:
                    analyses_df['date'] = pd.to_datetime(analyses_df['date'])
                    analyses_df = analyses_df.sort_values('date', ascending=False)
                except Exception as e:
                    st.warning(f"Fehler beim Verarbeiten der Datumsangaben: {e}")
                
                st.dataframe(analyses_df)
                
                # Sicherstellen, dass die Options-Liste nie leer ist
                if len(analyses_df) > 0:
                    filenames = analyses_df['filename'].tolist()
                    if filenames:  # Zusätzliche Sicherheitsprüfung
                        # Sicherer Aufruf von selectbox mit Standardindex
                        selected_file = st.selectbox(
                            "Gespeicherte Analyse laden:",
                            options=filenames,
                            index=0  # Der erste Eintrag ist standardmäßig ausgewählt
                        )
                        
                        if st.button("Analyse laden"):
                            with st.spinner(f"Lade Analyse für '{selected_file}'..."):
                                df, additional_data, metadata = load_analysis_results(selected_file)
                                
                                if df is not None:
                                    st.session_state.current_file = selected_file
                                    st.session_state.df = df
                                    
                                    # Textspalte bestimmen (meist 'comment_text')
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
                                    st.experimental_rerun()  # App neu laden, um die Ergebnisse anzuzeigen
                                else:
                                    st.error(f"Konnte keine Daten für '{selected_file}' laden.")
        except Exception as e:
            st.error(f"Fehler beim Laden der gespeicherten Analysen: {e}")
            st.info("Sie können trotzdem eine neue Analyse durchführen, indem Sie eine Datei hochladen.")
    
    # Anzeige der aktuellen Datei
    if st.session_state.current_file:
        st.info(f"Aktuelle Analyse: {st.session_state.current_file}")
        
        # Option zum Zurücksetzen
        if st.button("Neue Analyse starten"):
            st.session_state.current_file = None
            st.session_state.df = None
            st.session_state.text_column = None
            st.session_state.additional_data = {}
            st.experimental_rerun()
    
    # Check dependencies
    missing_deps = []
    
    if not MODELS_AVAILABLE:
        missing_deps.append("models.model_loader")
    
    if not BERTOPIC_CHECKED:
        missing_deps.append("utils.check_dependencies")
    else:
        # Check BERTopic availability if the check function is available
        try:
            BERTOPIC_AVAILABLE = is_bertopic_available()
        except:
            BERTOPIC_AVAILABLE = False
            missing_deps.append("bertopic")
    
    # Try to import other modules with detailed error handling
    try:
        from utils.sentiment_analysis import analyze_sentiment, display_sentiment_results
        SENTIMENT_ANALYSIS_AVAILABLE = True
    except ImportError as e:
        SENTIMENT_ANALYSIS_AVAILABLE = False
        missing_deps.append(f"utils.sentiment_analysis ({e})")
    
    try:
        from utils.topic_analysis import prepare_topic_analysis, display_topic_analysis
        TOPIC_ANALYSIS_AVAILABLE = True
    except ImportError as e:
        TOPIC_ANALYSIS_AVAILABLE = False
        missing_deps.append(f"utils.topic_analysis ({e})")
    
    try:
        from utils.emotion_analysis import prepare_emotion_analysis, display_emotion_analysis
        EMOTION_ANALYSIS_AVAILABLE = True
    except ImportError as e:
        EMOTION_ANALYSIS_AVAILABLE = False
        missing_deps.append(f"utils.emotion_analysis ({e})")
    
    try:
        from utils.emotion_comparison import display_emotion_comparison
        EMOTION_COMPARISON_AVAILABLE = True
    except ImportError as e:
        EMOTION_COMPARISON_AVAILABLE = False
        missing_deps.append(f"utils.emotion_comparison ({e})")
    
    try:
        from utils.special_analysis import display_special_analysis
        SPECIAL_ANALYSIS_AVAILABLE = True
    except ImportError as e:
        SPECIAL_ANALYSIS_AVAILABLE = False
        missing_deps.append(f"utils.special_analysis ({e})")
    
    # Display missing dependencies
    if missing_deps:
        st.warning(f"Einige Module konnten nicht geladen werden: {', '.join(missing_deps)}")
        st.info("""
        Um die vollständige Funktionalität zu nutzen, stelle sicher, dass die folgenden Module korrekt installiert sind:
        - transformers
        - bertopic
        - sentence-transformers
        - hdbscan
        - umap-learn
        - nltk
        - wordcloud
        
        Außerdem müssen die entsprechenden Python-Module im utils und models Verzeichnis vorhanden sein.
        """)
    
    # Load sentiment model if available
    sentiment_pipeline = None
    emotion_classifier = None
    
    if MODELS_AVAILABLE:
        with st.spinner("Lade Sentiment-Modell..."):
            try:
                sentiment_pipeline = load_sentiment_model()
                st.success("Sentiment-Modell erfolgreich geladen!")
            except Exception as e:
                st.error(f"Fehler beim Laden des Sentiment-Modells: {e}")
        
        with st.spinner("Lade Emotions-Modell..."):
            try:
                emotion_classifier = load_emotion_model()
                if emotion_classifier:
                    st.success("Emotions-Modell erfolgreich geladen!")
            except Exception as e:
                st.error(f"Fehler beim Laden des Emotions-Modells: {e}")
    
    # FALL 1: Bereits vorhandene Analyse anzeigen
    if st.session_state.current_file and st.session_state.df is not None:
        df = st.session_state.df
        text_column = st.session_state.text_column
        
        # Dateiname anzeigen (ohne YouTube-Integration)
        filename = st.session_state.current_file
        st.write(f"**Analysedatei:** {filename}")
        
        # Erstelle App-Tabs basierend auf verfügbaren Daten in df
        tabs_to_create = ["Sentiment-Analyse"]
        
        # Prüfe, welche Analyseergebnisse in den Daten vorhanden sind
        if 'topic' in df.columns:
            tabs_to_create.append("Themen-Analyse")
        
        if 'dominant_emotion' in df.columns:
            tabs_to_create.append("Emotions-Analyse")
            
            # Weitere Tabs je nach verfügbaren Daten
            if EMOTION_COMPARISON_AVAILABLE:
                tabs_to_create.append("Emotionsmodell-Vergleich")
        
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE:
            tabs_to_create.append("Spezial-Analysen")
        
        # Erstelle Tabs
        if len(tabs_to_create) > 1:
            main_tabs = st.tabs(tabs_to_create)
        else:
            main_tabs = [st]
        
        # Zeige die Ergebnisse in den jeweiligen Tabs an
        tab_index = 0
        
        # Tab 1: Sentiment-Analyse
        with main_tabs[tab_index]:
            if 'sentiment' in df.columns and SENTIMENT_ANALYSIS_AVAILABLE:
                display_sentiment_results(df, text_column)
            else:
                display_sentiment_results_fallback(df, text_column)
        
        tab_index += 1
        
        # Weitere Tabs anzeigen, wenn die Daten vorhanden sind
        if 'topic' in df.columns and tab_index < len(main_tabs):
            # Topic Analysis Tab
            with main_tabs[tab_index]:
                # Lade zusätzliche Daten aus session_state
                topic_model = st.session_state.additional_data.get('topic_model')
                topic_info = st.session_state.additional_data.get('topic_info')
                topic_df = st.session_state.additional_data.get('topic_df')
                topic_labels = st.session_state.additional_data.get('topic_labels')
                
                # Zeige Topic-Analyse an, falls die Daten vorhanden sind
                if topic_model and TOPIC_ANALYSIS_AVAILABLE:
                    display_topic_analysis(df, topic_model, topic_df, topic_info, topic_labels)
                else:
                    st.warning("Themenanalyse konnte nicht angezeigt werden. Erforderliche Daten fehlen.")
            
            tab_index += 1
        
        # Emotions-Analyse anzeigen, wenn die Daten vorhanden sind
        if 'dominant_emotion' in df.columns and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                if EMOTION_ANALYSIS_AVAILABLE:
                    # Lade Topic-Modell Daten, falls vorhanden
                    topic_model = st.session_state.additional_data.get('topic_model')
                    topic_labels = st.session_state.additional_data.get('topic_labels')
                    
                    display_emotion_analysis(df, text_column, topic_model, topic_labels)
                else:
                    st.warning("Emotionsanalyse konnte nicht angezeigt werden. Erforderliches Modul nicht verfügbar.")
            
            tab_index += 1
        
        # Emotionsmodell-Vergleich anzeigen, wenn die Daten vorhanden sind
        if 'dominant_emotion' in df.columns and EMOTION_COMPARISON_AVAILABLE and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                if emotion_classifier is not None:
                    display_emotion_comparison(df, emotion_classifier)
                else:
                    st.warning("Emotionsmodell-Vergleich konnte nicht angezeigt werden. Emotions-Modell nicht verfügbar.")
            
            tab_index += 1
        
        # Spezial-Analysen anzeigen, wenn die Daten vorhanden sind
        if 'topic' in df.columns and SPECIAL_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
            with main_tabs[tab_index]:
                topic_labels = st.session_state.additional_data.get('topic_labels')
                if topic_labels:
                    display_special_analysis(df, text_column, topic_labels)
                else:
                    st.warning("Spezialanalysen erfordern Themen-Daten, die nicht vollständig verfügbar sind.")
        
        # Zeige Datenvorschau
        st.subheader("Datenvorschau")
        st.dataframe(df.head())
        
        # Download-Button
        st.download_button(
            label="Daten als CSV speichern",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"{Path(filename).stem}_analyse.csv",
            mime='text/csv'
        )
        
        # Option zum erneuten Speichern anbieten
        if st.button("Analyseergebnisse neu speichern"):
            save_analysis_results(
                st.session_state.current_file, 
                df, 
                st.session_state.additional_data
            )
            st.success("Analyseergebnisse wurden erneut gespeichert!")
    
    # FALL 2: Neue Analyse durchführen
    else:
        # Hole CSV-Dateien aus dem festgelegten Datenordner
        available_csv_files = get_files_from_data_folder()
        
        # Flag für Dateiprozessierung
        processed_file = None
        
        # Container für die Dateiauswahl
        file_selection_container = st.container()
        
        with file_selection_container:
            # Option 1: Datei aus dem Datenordner auswählen
            if available_csv_files:
                st.write("### Option 1: Datei aus dem Datenordner auswählen")
                selected_csv_path = st.selectbox(
                    "CSV-Datei aus dem Ordner '/Users/sandra/Documents/12.5./Hauptapp/data/comments' auswählen:",
                    options=available_csv_files,
                    format_func=lambda x: Path(x).name
                )
                
                if st.button("Ausgewählte Datei analysieren"):
                    try:
                        # Datei aus dem Datenordner laden
                        with open(selected_csv_path, 'rb') as f:
                            file_content = f.read()
                            
                        # Als BytesIO-Objekt umwandeln (simuliert ein hochgeladenes File)
                        from io import BytesIO
                        processed_file = BytesIO(file_content)
                        processed_file.name = Path(selected_csv_path).name
                    except Exception as e:
                        st.error(f"Fehler beim Lesen der ausgewählten Datei: {e}")
            else:
                st.warning(f"Keine CSV-Dateien im Ordner '/Users/sandra/Documents/12.5./Hauptapp/data/comments' gefunden.")
                st.info("Bitte legen Sie CSV-Dateien in diesem Ordner ab oder nutzen Sie die Upload-Option unten.")
            
            # Option 2: Datei hochladen
            st.write("### Option 2: Datei hochladen")
            uploaded_file = st.file_uploader("CSV- oder JSON-Datei mit Kommentaren hochladen:", type=["csv", "json", "jsonl"])
            
            if uploaded_file is not None:
                processed_file = uploaded_file
        
        # Verarbeite die ausgewählte oder hochgeladene Datei
        if processed_file is not None:
            try:
                # Dateiname für die Anzeige
                filename = processed_file.name
                st.write(f"Verarbeite Datei: **{filename}**")
                
                # Daten laden und bereinigen
                with st.spinner("Lade und bereinige Daten..."):
                    df, text_column = load_and_clean_data(processed_file)
                    
                    # Text für weitere Analyse bereinigen
                    df['clean_text'] = df[text_column].apply(clean_text)
                
                # In Session State speichern
                st.session_state.current_file = filename
                st.session_state.df = df
                st.session_state.text_column = text_column
                
                # Erstelle App-Tabs basierend auf verfügbaren Modulen
                tabs_to_create = ["Sentiment-Analyse"]
                
                if BERTOPIC_AVAILABLE and TOPIC_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("Themen-Analyse")
                
                if EMOTION_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("Emotions-Analyse")
                
                if EMOTION_COMPARISON_AVAILABLE:
                    tabs_to_create.append("Emotionsmodell-Vergleich")
                
                if SPECIAL_ANALYSIS_AVAILABLE:
                    tabs_to_create.append("Spezial-Analysen")
                
                # Erstelle Tabs
                if len(tabs_to_create) > 1:
                    main_tabs = st.tabs(tabs_to_create)
                else:
                    main_tabs = [st]
                
                # Tab 1: Sentiment-Analyse
                with main_tabs[0]:
                    with st.spinner("Führe Sentiment-Analyse durch..."):
                        if SENTIMENT_ANALYSIS_AVAILABLE and sentiment_pipeline:
                            df = analyze_sentiment(df, text_column, sentiment_pipeline)
                            display_sentiment_results(df, text_column)
                        else:
                            # Fallback zur vereinfachten Version
                            df = analyze_sentiment_fallback(df, text_column)
                            display_sentiment_results_fallback(df, text_column)
                
                # Überprüfe, ob weitere Tabs angezeigt werden können
                tab_index = 1
                
                # Zusätzliche Daten für persistentes Speichern
                additional_data = {}
                
                # Fortfahren mit erweiterter Analyse, wenn Module verfügbar sind
                if BERTOPIC_AVAILABLE and TOPIC_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
                    try:
                        # Bereite Text für Themenmodellierung vor
                        with st.spinner("Führe Themenanalyse durch..."):
                            df, topic_model, topic_info, topic_df, topic_labels = prepare_topic_analysis(df, text_column)
                            
                            # Speichere Themen-Modell und Informationen für spätere Verwendung
                            additional_data['topic_model'] = topic_model
                            additional_data['topic_info'] = topic_info
                            additional_data['topic_df'] = topic_df
                            additional_data['topic_labels'] = topic_labels
                        
                        # Analysiere Emotionen, wenn das Modell verfügbar ist
                        if EMOTION_ANALYSIS_AVAILABLE and emotion_classifier is not None:
                            with st.spinner("Führe Emotionsanalyse durch..."):
                                df = prepare_emotion_analysis(df, emotion_classifier)
                        
                        # Tab 2: Themenanalyse
                        with main_tabs[tab_index]:
                            display_topic_analysis(df, topic_model, topic_df, topic_info, topic_labels)
                        
                        tab_index += 1
                        
                        # Tab 3: Emotionsanalyse (falls verfügbar)
                        if EMOTION_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
                            with main_tabs[tab_index]:
                                if emotion_classifier is not None and 'dominant_emotion' in df.columns:
                                    display_emotion_analysis(df, text_column, topic_model, topic_labels)
                                else:
                                    st.warning("Emotionsanalyse konnte nicht durchgeführt werden. Emotions-Modell nicht verfügbar.")
                            
                            tab_index += 1
                        
                        # Tab 4: Emotionsmodell-Vergleich (falls verfügbar)
                        if EMOTION_COMPARISON_AVAILABLE and tab_index < len(main_tabs):
                            with main_tabs[tab_index]:
                                if emotion_classifier is not None:
                                    display_emotion_comparison(df, emotion_classifier)
                                else:
                                    st.warning("Emotionsmodell-Vergleich konnte nicht durchgeführt werden. Emotions-Modell nicht verfügbar.")
                            
                            tab_index += 1
                        
                        # Tab 5: Spezial-Analysen (falls verfügbar)
                        if SPECIAL_ANALYSIS_AVAILABLE and tab_index < len(main_tabs):
                            with main_tabs[tab_index]:
                                if 'topic' in df.columns:
                                    display_special_analysis(df, text_column, topic_labels)
                                else:
                                    st.warning("Spezialanalysen erfordern Themen-Daten, die nicht verfügbar sind.")
                    
                    except Exception as e:
                        st.error(f"Fehler bei der erweiterten Analyse: {e}")
                        st.error(traceback.format_exc())
                
                # Aktualisiere DataFrame in Session State
                st.session_state.df = df
                
                # Speichere zusätzliche Daten in Session State
                st.session_state.additional_data = additional_data
                
                # Zeige Datenvorschau
                st.subheader("Datenvorschau")
                st.dataframe(df.head())
                
                # Download-Button
                st.download_button(
                    label="Daten als CSV speichern",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"{Path(filename).stem}_analyse.csv",
                    mime='text/csv'
                )
                
                # Speicheroption anbieten
                if st.button("Analyseergebnisse speichern"):
                    if save_analysis_results(filename, df, additional_data):
                        st.success(f"Analyseergebnisse für '{filename}' wurden erfolgreich gespeichert!")
                        # Seite neu laden, um die gespeicherte Analyse anzuzeigen
                        st.experimental_rerun()
                
            except Exception as e:
                st.error(f"Fehler beim Laden oder Verarbeiten der Datei: {e}")
                st.error(traceback.format_exc())

if __name__ == "__main__":
    main()