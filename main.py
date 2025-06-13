import streamlit as st
from pathlib import Path

# === SPRACHSYSTEM IMPORTIEREN ===
from utils.language_switcher_config import init_language, get_text, t
from utils.language_switcher_ui import language_switcher, display_main_footer

# ===== SETUP IN KORREKTER REIHENFOLGE =====
try:
    # 1. SPRACHE INITIALISIEREN (vor allem anderen!)
    init_language()
    
    # 2. PAGE CONFIG (kann jetzt Übersetzungen verwenden)
    st.set_page_config(
        page_title=t("app_title"),
        page_icon="👩‍🎓",
        layout="wide"
    )
except Exception as e:
    st.error(f"Fehler beim Setzen der Seitenkonfiguration: {str(e)}")
    st.info("Versuchen Sie, die App neu zu laden oder kontaktieren Sie den Support.")

# 3. SPRACHSCHALTER HINZUFÜGEN (nach page config)
language_switcher()

# ===== SIDEBAR SETUP =====
# Aktiviere Sidebar
st.sidebar.write("")

# Copyright fest am Boden der Navigation (bestehender Stil beibehalten)
st.sidebar.markdown("""
<style>
.sidebar-copyright-fixed-bottom {
    position: fixed;
    bottom: 10px;
    left: 10px;
    right: 10px;
    max-width: 224px;
    padding: 15px 10px;
    margin: 10px 0;
    background: rgba(255, 107, 152, 0.1);
    border-left: 3px solid #FF6B98;
    border-radius: 8px;
    text-align: center;
    font-size: 0.75rem;
    z-index: 999;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.sidebar-copyright-fixed-bottom .author {
    color: #FF6B98;
    font-weight: 600;
    font-size: 0.8rem;
    margin-bottom: 3px;
}

.sidebar-copyright-fixed-bottom .project {
    color: #666666;
    font-size: 0.65rem;
}

section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 80px;
}
</style>

<div class="sidebar-copyright-fixed-bottom">
    <div class="author">© Sandra Störkel</div>
    <div class="project">HerEducation 2025</div>
</div>
""", unsafe_allow_html=True)

# ===== CSS STYLING =====
# CSS für einheitlichen Footer
st.markdown("""
<style>
/* Professional Copyright Footer */
.copyright-footer {
    margin-top: 50px;
    padding: 25px 20px;
    border-top: 2px solid #FF6B98;
    text-align: center;
    color: #666666;
    font-size: 0.9rem;
    background-color: #f8f9fa;
    border-radius: 10px;
}
.author-name {
    color: #FF6B98;
    font-weight: 600;
}
.app-title {
    color: #FF6B98;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# Disable the default radio button navigation
try:
    hide_radio_buttons = """
    <style>
    /* Verstecke nur Radio Buttons AUSSERHALB der Sidebar */
    div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] {
        display: none;
    }
    
    /* Lass Radio Buttons in der Sidebar sichtbar (für Sprachschalter) */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] {
        display: block !important;
    }
    </style>
    """
    st.markdown(hide_radio_buttons, unsafe_allow_html=True)
except Exception as e:
    # Nicht kritisch, kann ohne Fehlermeldung ignoriert werden
    pass

# ===== VERZEICHNISSE ERSTELLEN =====
# Erstelle saved_results Verzeichnis relativ zur main.py
saved_results_dir = Path(__file__).parent / "saved_results"
saved_results_dir.mkdir(exist_ok=True, parents=True)

# ===== HAUPTINHALT MIT ÜBERSETZUNGEN =====
# Haupttitel mit Übersetzung
st.title(f"👩‍🎓 {t('app_title')}")

# Beschreibung mit Übersetzungen
st.markdown(f"""
### {t('app_subtitle')}
            
### {t('app_description')}
""")

# Sprachabhängige zusätzliche Beschreibung
if st.session_state.language == "DE":
    st.markdown("""
    Diese App bietet einen umfassenden Rahmen für das Verständnis von Publikumsreaktionen auf YouTube 
    und kombiniert mehrere hochmoderne NLP-Modelle mit Analyseansätzen, die speziell auf deutsche und englische 
    YouTube-Kommentare zugeschnitten sind.
    """)
else:
    st.markdown("""
    This app provides a comprehensive framework for understanding audience reactions on YouTube 
    and combines multiple state-of-the-art NLP models with analytical approaches specifically 
    tailored for German and English YouTube comments.
    """)

# ===== PROJEKTSTRUKTUR MIT ÜBERSETZUNG =====
with st.expander(f"📋 {t('project_structure')}"):
    st.markdown("""
    ```
    HerEducation/
    ├── main.py                     # Haupteinstiegspunkt der Streamlit-App
    ├── requirements.txt            # Python-Abhängigkeiten
    ├── README.md                   # Projektdokumentation
    ├── pages/                      # Multi-Page-Struktur
    │   ├── 01_Projektidee.py       # Projektkontext (Malaysia/Mädchenbildung)
    │   ├── 02_Heratlas_unesco.py   # UNESCO-Datenvisualisierung
    │   ├── 03_Indikatoren_Entwicklung.py # Zeitreihenanalysen
    │   ├── 04_YouTube_Analyzer.py  # YouTube-Tools
    │   ├── 05_Kommentaranalyse_deutsch.py # Deutsche Kommentaranalyse
    │   ├── 06_Kommentaranalyse_english.py # Englische Kommentaranalyse
    │   └── 07_Globale_Diskurs_Analyse.py  # Ländervergleiche
    ├── models/                     # ML-Modell-Loader
    │   ├── model_loader.py         # Deutsche Modelle
    │   └── model_loader_english.py # Englische Modelle
    ├── utils/                      # Hilfsfunktionen
    │   ├── language_switcher_config.py    # Sprachkonfiguration
    │   ├── language_switcher_ui.py        # Sprachschalter UI
    │   ├── language_switcher_migration.py # Migration Tools
    │   ├── check_dependencies.py   # Dependency-Check
    │   ├── comment_saver_improved.py # Kommentar-Extraktion
    │   ├── data_loader.py          # Datenlade-Funktionen
    │   ├── downloader.py           # Download-Utilities
    │   ├── emotion_analysis.py     # Emotionsanalyse
    │   ├── emotion_analysis_english.py # Emotionsanalyse (EN)
    │   ├── sentiment_analysis.py   # Sentiment-Verarbeitung
    │   ├── topic_analysis.py       # Themenanalyse
    │   ├── visualizations.py       # Visualisierungs-Utils
    │   └── ... weitere Utils
    ├── data/                       # Datenverzeichnisse
    │   ├── audio/                  # Audio-Dateien
    │   ├── transcripts/            # Transkripte
    │   ├── comments/               # YouTube-Kommentare
    │   └── heraltas1_updated.csv   # UNESCO-Bildungsdaten
    └── saved_results/              # Persistente Analyseergebnisse
        └── saved_results_english/  # Englische Analysen
    ```
    """)

# ===== HAUPTSEKTIONEN MIT ÜBERSETZUNGEN =====
# Sprachabhängige Hauptsektionen
if st.session_state.language == "DE":
    st.markdown("""
    ### 📊 Projektidee
    Entdecken Sie die Motivation hinter diesem Projekt und erhalten Sie Einblicke in die aktuelle Situation 
    der Mädchenbildung weltweit.

    ### 🌍 UNESCO Bildungsatlas (HerAtlas)
    Analysieren Sie den rechtlichen Rahmen und die Bildungspolitik in 196 Ländern mit Fokus auf Grundlage der Daten des UNESCO-HerAtlas:
    - Geschlechtergerechte Bildungspolitik
    - Internationale Abkommen zur Mädchenbildung
    - Verfassungsrechtliche Verankerung des Bildungsrechts
    - Schulpflicht und Geschlechtergerechtigkeit

    ### 📈 Indikatoren-Entwicklung
    Verfolgen Sie die zeitliche Entwicklung wichtiger Bildungsindikatoren mit besonderem Augenmerk auf:
    - Länderranking
    - Regionale Unterschiede 
    - Fortschritte und Rückschritte

    ### 🎬 YouTube-Analyse 
    Spezialisierte Tools zur Analyse bildungsbezogener Inhalte:
    - Suche und Download von Videos aus YouTube - alle Themen möglich
    - Transkription für weitere Analysen verfügbar
    - Speichern der Kommentare der Videos

    ### 💬 Kommentaranalyse (Deutsch & Englisch)
    Umfassende Analyse von YouTube-Kommentaren:
    1. Extrahieren von YouTube-Videoinformationen 
    2. Stimmungsanalyse der Kommentare durchführen
    3. Identifizierung der in den Kommentaren diskutierten Themen (Themenmodellierung)
    4. Analyse der in den Kommentaren ausgedrückten Emotionen
    5. Durchführung spezieller Analysen für bestimmte Themen wie Bildung und Geschlechterthemen

    ### 🌍 Globale Diskurs-Analyse
    Vergleichende Analyse von Diskursen zwischen verschiedenen Ländern:
    - Cross-Country Sentiment-Vergleiche
    - Internationale Topic-Trends
    - Kulturelle Unterschiede in Emotionsmustern
    - Interaktive Weltkarten-Visualisierung
    """)
else:
    st.markdown("""
    ### 📊 Project Idea
    Discover the motivation behind this project and gain insights into the current situation 
    of girls' education in Malaysia.

    ### 🌍 UNESCO Education Atlas (HerAtlas)
    Analyze the legal framework and education policy in 196 countries based on UNESCO HerAtlas data:
    - Gender-equitable education policy
    - International agreements on girls' education
    - Constitutional anchoring of the right to education
    - Compulsory education and gender equality

    ### 📈 Indicators Development
    Track the temporal development of important education indicators with special focus on:
    - Country rankings
    - Regional differences
    - Progress and setbacks

    ### 🎬 YouTube Analysis
    Specialized tools for analyzing education-related content:
    - Search and download videos from YouTube - all topics possible
    - Transcription available for further analysis
    - Save video comments

    ### 💬 Comment Analysis (German & English)
    Comprehensive analysis of YouTube comments:
    1. Extract YouTube video information
    2. Perform sentiment analysis of comments
    3. Identify topics discussed in comments (topic modeling)
    4. Analyze emotions expressed in comments
    5. Perform special analyses for specific topics like education and gender issues

    ### 🌍 Global Discourse Analysis
    Comparative analysis of discourses between different countries:
    - Cross-country sentiment comparisons
    - International topic trends
    - Cultural differences in emotion patterns
    - Interactive world map visualization
    """)

# ===== INFO-BOX MIT ÜBERSETZUNG =====
if st.session_state.language == "DE":
    st.info(f"""
    📌 **{t('app_title')}** kombiniert UNESCO-Bildungsdaten mit modernen Social Media-Analysen, um ein umfassendes Bild 
    der globalen Mädchenbildung zu zeichnen.
    """)
else:
    st.info(f"""
    📌 **{t('app_title')}** combines UNESCO education data with modern social media analysis to draw a comprehensive picture 
    of global girls' education.
    """)

# ===== TECHNISCHE FEATURES =====
# Sprachabhängige technische Features
if st.session_state.language == "DE":
    st.markdown("""
    ### 🔬 Verwendete ML-Modelle für deutsche Sprache
    1. **Sentiment Analysis Model**
        - Modell: oliverguhr/german-sentiment-bert - ein feinabgestimmtes BERT-Modell für die deutsche Stimmungsanalyse
        - Zweck: kategorisiert Kommentare als positiv, neutral oder negativ
        - Implementierung: Verwendet die Pipeline von Hugging Face zur Stimmungsanalyse

    2. **Emotionsanalyse-Modell**
        - Modell: visegradmedia-emotion/Emotion_RoBERTa_german6_v7 - ein RoBERTa-Modell für deutsche Emotionen
        - Zweck: Erkennung von sechs emotionalen Zuständen: Wut, Furcht, Ekel, Traurigkeit, Freude, Neutral
        - Implementierung: Verwendung einer Textklassifizierungspipeline mit Emotionskennzeichnungen

    3. **Themenanalyse-Modell**
        - Modell: BERTopic mit distiluse-base-multilingual-cased-v1 als Einbettungsmodell
        - Zweck: Identifizierung von Themen und Konzepten in den Kommentaren
        - Implementierung: Satztransformatoren für Einbettungen, HDBSCAN für Clustering, benutzerdefinierte Themenbeschriftung

    ### 🎯 Praktische Anwendungen
    - **Inhaltsersteller**: Verstehen Sie die Stimmung und Reaktionen Ihres Publikums
    - **Marken- und Marketinganalyse**: Bewerten Sie die emotionale Wirkung von Kampagnen
    - **Bildung und Forschung**: Verstehen Sie Feedback und Interesse an Bildungsthemen
    - **Community-Verwaltung**: Verfolgen Sie Engagement-Trends in Ihrer Community
    """)
else:
    st.markdown("""
    ### 🔬 ML Models Used for German Language
    1. **Sentiment Analysis Model**
        - Model: oliverguhr/german-sentiment-bert - a fine-tuned BERT model for German sentiment analysis
        - Purpose: categorizes comments as positive, neutral, or negative
        - Implementation: Uses Hugging Face pipeline for sentiment analysis

    2. **Emotion Analysis Model**
        - Model: visegradmedia-emotion/Emotion_RoBERTa_german6_v7 - a RoBERTa model for German emotions
        - Purpose: Detection of six emotional states: anger, fear, disgust, sadness, joy, neutral
        - Implementation: Uses text classification pipeline with emotion labels

    3. **Topic Analysis Model**
        - Model: BERTopic with distiluse-base-multilingual-cased-v1 as embedding model
        - Purpose: Identification of topics and concepts in comments
        - Implementation: Sentence transformers for embeddings, HDBSCAN for clustering, custom topic labeling

    ### 🎯 Practical Applications
    - **Content Creators**: Understand audience sentiment and reactions
    - **Brand and Marketing Analysis**: Evaluate emotional impact of campaigns
    - **Education and Research**: Understand feedback and interest in educational topics
    - **Community Management**: Track engagement trends in your community
    """)

# ===== MODUL-PROBLEME PRÜFEN =====
# Hinweis zu möglichen Modul-Problemen anzeigen
try:
    # Prüfen auf nltk, da es in einem der Module Probleme gab
    import nltk
    nltk_available = True
except ImportError:
    nltk_available = False

# Prüfen auf pickle und json, die für die Persistenz benötigt werden
try:
    import pickle
    import json
    persistence_available = True
except ImportError:
    persistence_available = False

# Informationen zu fehlenden Modulen anzeigen
missing_modules = []
if not nltk_available:
    missing_modules.append("nltk")
if not persistence_available:
    missing_modules.append("pickle und/oder json")

if missing_modules:
    with st.expander("⚠️ Hinweis zu möglichen Modul-Problemen", expanded=False):
        if st.session_state.language == "DE":
            st.warning(f"Einige Module scheinen zu fehlen oder nicht korrekt installiert zu sein: {', '.join(missing_modules)}")
            st.info("""
            **Installation**: Verwenden Sie die `requirements.txt` Datei für eine einfache Installation aller benötigten Abhängigkeiten:
            
            ```bash
            pip install -r requirements.txt
            ```
            
            Sollten auf einer Seite dennoch Fehler auftreten, stellen Sie sicher, dass alle NLTK-Daten heruntergeladen wurden.
            """)
        else:
            st.warning(f"Some modules seem to be missing or not correctly installed: {', '.join(missing_modules)}")
            st.info("""
            **Installation**: Use the `requirements.txt` file for easy installation of all required dependencies:
            
            ```bash
            pip install -r requirements.txt
            ```
            
            If errors still occur on a page, make sure all NLTK data has been downloaded.
            """)

# ===== SPRACHSCHALTER DEBUG INFO (OPTIONAL) =====
# Uncomment for debugging
# with st.expander("🔧 Language Switcher Debug", expanded=False):
#     st.write(f"Current Language: {st.session_state.language}")
#     st.write(f"Available Languages: {list(LANGUAGES.keys())}")
#     st.write(f"Session State: {dict(st.session_state)}")

# ===== FOOTER MIT ÜBERSETZUNG =====
display_main_footer()