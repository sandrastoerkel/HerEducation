# utils/language_switcher_config.py
import streamlit as st

# Sprachkonfiguration
LANGUAGES = {
    "DE": "🇩🇪 Deutsch",
    "EN": "🇬🇧 English"
}

# Übersetzungs-Dictionary für die gesamte App
TRANSLATIONS = {
    "DE": {
        # === MAIN PAGE ===
        "app_title": "HerEducation",
        "app_subtitle": "Analyseplattform von Bildungsgleichberechtigung weltweit auf Grundlage des UNESCO HerAtlas",
        "app_description": "Social Media-Analysen von YouTube-Videos um international ein umfassendes Bild von Mediendiskussionen zeichnen zu können",
        "project_structure": "Projektstruktur ansehen",
        
        # === NAVIGATION ===
        "language_select": "Sprache wählen:",
        "projektidee": "Projektidee",
        "unesco_atlas": "UNESCO HerAtlas Dashboard", 
        "indicators": "Indikatoren & Entwicklung",
        "youtube_tools": "YouTube Analyzer",
        "comment_analysis_de": "Kommentaranalyse (Deutsch)",
        "comment_analysis_en": "Kommentaranalyse (English)",
        "global_analysis": "Globale Diskurs-Analyse",
        
        # === PROJEKTIDEE PAGE ===
        "project_origin": "Der Ursprung der App",
        "project_origin_text": "Diese Präsentation fokussiert sich auf die Förderung der Mädchenbildung und den Kampf gegen die Diskriminierung von Frauen weltweit.",
        "malaysia_tab": "Malaysia",
        "women_rights_tab": "Mißachtung der Frauenrechte",
        "mixed_marriages_tab": "Kinder aus Mischehen",
        "education_ethnicity_tab": "Bildung & Religion nach Ethnien",
        "education_key_tab": "Bildung als Schlüssel",
        "global_perspectives_tab": "Globale Perspektiven",
        "emotional_dynamics_tab": "Emotionale Dynamiken",
        
        # === UNESCO DASHBOARD ===
        "unesco_dashboard_title": "HerAtlas Unesco Dashboard",
        "unesco_description": "Diese interaktive Anwendung ermöglicht die Analyse des rechtlichen Rahmens und der Bildungspolitik in 196 Ländern weltweit.",
        "data_processing_info": "Informationen zur Datenverarbeitung",
        "education_indicators": "Vorhandene Bildungsindikatoren",
        "world_map": "Weltkarte: Ergebnisse pro Land",
        "overview_tab": "Übersicht",
        "country_comparison_tab": "Ländervergleich", 
        "data_table_tab": "Datentabelle",
        "global_overview": "Globaler Überblick",
        "select_indicator": "Indikator auswählen",
        "select_year": "Jahr auswählen",
        "select_country": "Land auswählen",
        "summary": "Zusammenfassung",
        "result_distribution": "Verteilung der Ergebnisse",
        "detailed_statistics": "Detaillierte Statistiken",
        "country_comparison": "Ländervergleich",
        "data_table": "Datentabelle",
        "download_csv": "Download als CSV",
        "no_data_available": "Keine Daten verfügbar",
        "loading_data": "Lade Daten...",
        "countries_analyzed": "Länder analysiert",
        "total_comments": "Gesamt Kommentare",
        "data_last_update": "Daten zuletzt aktualisiert",
        
        # === YOUTUBE ANALYZER ===
        "download_videos": "Videos Herunterladen",
        "transcribe_audio": "Audio Transkribieren", 
        "save_comments": "Kommentare Speichern",
        "search_download": "Nach Themen suchen",
        "url_download": "Video-URL eingeben",
        "cookie_upload": "Cookie-Datei (Optional)",
        "search_query": "Suchanfrage:",
        "download_button": "Suchen und Herunterladen",
        "existing_audio": "Vorhandene Audio-Dateien",
        "transcription_title": "Audio Transkribieren",
        "comments_title": "Kommentare Speichern",
        
        # === COMMENT ANALYSIS ===
        "sentiment_analysis": "Sentiment-Analyse",
        "topic_analysis": "Themen-Analyse", 
        "emotion_analysis": "Emotions-Analyse",
        "special_analysis": "Spezial-Analysen",
        "data_preview": "Datenvorschau",
        "save_results": "Analyseergebnisse speichern",
        "load_analysis": "Gespeicherte Analysen",
        "file_upload": "CSV- oder JSON-Datei mit Kommentaren hochladen:",
        "emotion_model_comparison": "Emotionsmodell-Vergleich",
        
        # === GLOBAL DISCOURSE ===
        "global_discourse_title": "Globale Diskurs-Analyse",
        "sentiment_worldmap": "Sentiment & Weltkarte",
        "topic_comparison": "Topic-Vergleich",
        "emotion_analysis_global": "Emotion-Analyse",
        "advanced_insights": "Erweiterte Insights",
        "theme_search": "Enhanced Themen-Suche",
        
        # === INDICATORS & DEVELOPMENT ===
        "indicators_title": "Indikatoren & Entwicklung",
        "data_analysis": "Datenanalyse",
        "country_ranking": "Länderranking 2019-2025",
        "regional_distribution": "Regionale Verteilung",
        "time_development": "Entwicklung über Zeit",
        "loading_education_data": "Lade Bildungsdaten...",
        "data_load_error": "Die Daten konnten nicht geladen werden. Bitte überprüfen Sie die Datei 'heraltas1_updated.csv'.",
        "no_indicators_found": "Keine gültigen Indikatoren gefunden.",
        
        # === COMMON ELEMENTS ===
        "year_select": "Jahr auswählen:",
        "indicator_select": "Indikator auswählen:",
        "country_select": "Land auswählen:",
        "file_select": "Datei auswählen:",
        "loading": "Lade...",
        "error": "Fehler",
        "success": "Erfolgreich",
        "warning": "Warnung",
        "info": "Information",
        "download": "Herunterladen",
        "upload": "Hochladen",
        "save": "Speichern",
        "load": "Laden",
        "search": "Suchen",
        "filter": "Filter",
        "export": "Exportieren",
        "analyze": "Analysieren",
        "back": "Zurück",
        "next": "Weiter",
        "cancel": "Abbrechen",
        "confirm": "Bestätigen",
        "close": "Schließen",
        "start_analysis": "Analyse starten",
        "new_analysis": "Neue Analyse starten",
        "processing_data": "Verarbeite Daten...",
        "no_data_for_selection": "Keine Daten für die ausgewählte Kombination verfügbar.",
        "show_all": "Alle anzeigen",
        "number_of_entries": "Anzahl der Einträge",
        
        # === DEBUG & UI HELPERS ===
        "current_language": "Aktuelle Sprache",
        "available_languages": "Verfügbare Sprachen",
        "session_state_keys": "Session State Keys",
        "debug_info": "Debug-Informationen"
    },
    
    "EN": {
        # === MAIN PAGE ===
        "app_title": "HerEducation",
        "app_subtitle": "Analysis platform for educational equality worldwide based on UNESCO HerAtlas",
        "app_description": "Social media analysis of YouTube videos to draw a comprehensive picture of media discussions internationally",
        "project_structure": "View project structure",
        
        # === NAVIGATION ===
        "language_select": "Choose language:",
        "projektidee": "Project Idea",
        "unesco_atlas": "UNESCO HerAtlas Dashboard",
        "indicators": "Indicators & Development", 
        "youtube_tools": "YouTube Analyzer",
        "comment_analysis_de": "Comment Analysis (German)",
        "comment_analysis_en": "Comment Analysis (English)",
        "global_analysis": "Global Discourse Analysis",
        
        # === PROJEKTIDEE PAGE ===
        "project_origin": "The Origin of the App",
        "project_origin_text": "This presentation focuses on promoting girls' education and fighting discrimination against women worldwide.",
        "malaysia_tab": "Malaysia",
        "women_rights_tab": "Disregard for Women's Rights",
        "mixed_marriages_tab": "Children from Mixed Marriages",
        "education_ethnicity_tab": "Education & Religion by Ethnicity",
        "education_key_tab": "Education as Key",
        "global_perspectives_tab": "Global Perspectives",
        "emotional_dynamics_tab": "Emotional Dynamics",
        
        # === UNESCO DASHBOARD ===
        "unesco_dashboard_title": "HerAtlas UNESCO Dashboard",
        "unesco_description": "This interactive application enables analysis of the legal framework and education policy in 196 countries worldwide.",
        "data_processing_info": "Data processing information",
        "education_indicators": "Available education indicators",
        "world_map": "World map: Results per country",
        "overview_tab": "Overview",
        "country_comparison_tab": "Country Comparison",
        "data_table_tab": "Data Table",
        "global_overview": "Global Overview",
        "select_indicator": "Select Indicator",
        "select_year": "Select Year",
        "select_country": "Select Country",
        "summary": "Summary",
        "result_distribution": "Distribution of Results",
        "detailed_statistics": "Detailed Statistics",
        "country_comparison": "Country Comparison", 
        "data_table": "Data Table",
        "download_csv": "Download as CSV",
        "no_data_available": "No data available",
        "loading_data": "Loading data...",
        "countries_analyzed": "Countries analyzed",
        "total_comments": "Total comments",
        "data_last_update": "Data last updated",
        
        # === YOUTUBE ANALYZER ===
        "download_videos": "Download Videos",
        "transcribe_audio": "Transcribe Audio",
        "save_comments": "Save Comments", 
        "search_download": "Search by topics",
        "url_download": "Enter video URL",
        "cookie_upload": "Cookie file (Optional)",
        "search_query": "Search query:",
        "download_button": "Search and Download",
        "existing_audio": "Existing Audio Files",
        "transcription_title": "Transcribe Audio",
        "comments_title": "Save Comments",
        
        # === COMMENT ANALYSIS ===
        "sentiment_analysis": "Sentiment Analysis",
        "topic_analysis": "Topic Analysis",
        "emotion_analysis": "Emotion Analysis", 
        "special_analysis": "Special Analysis",
        "data_preview": "Data Preview",
        "save_results": "Save analysis results",
        "load_analysis": "Saved analyses",
        "file_upload": "Upload CSV or JSON file with comments:",
        "emotion_model_comparison": "Emotion Model Comparison",
        
        # === GLOBAL DISCOURSE ===
        "global_discourse_title": "Global Discourse Analysis",
        "sentiment_worldmap": "Sentiment & World Map",
        "topic_comparison": "Topic Comparison",
        "emotion_analysis_global": "Emotion Analysis", 
        "advanced_insights": "Advanced Insights",
        "theme_search": "Enhanced Theme Search",
        
        # === INDICATORS & DEVELOPMENT ===
        "indicators_title": "Indicators & Development",
        "data_analysis": "Data Analysis",
        "country_ranking": "Country Ranking 2019-2025",
        "regional_distribution": "Regional Distribution",
        "time_development": "Development over Time",
        "loading_education_data": "Loading education data...",
        "data_load_error": "The data could not be loaded. Please check the file 'heraltas1_updated.csv'.",
        "no_indicators_found": "No valid indicators found.",
        
        # === COMMON ELEMENTS ===
        "year_select": "Select year:",
        "indicator_select": "Select indicator:",
        "country_select": "Select country:",
        "file_select": "Select file:",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "warning": "Warning", 
        "info": "Information",
        "download": "Download",
        "upload": "Upload",
        "save": "Save",
        "load": "Load",
        "search": "Search",
        "filter": "Filter",
        "export": "Export",
        "analyze": "Analyze",
        "back": "Back",
        "next": "Next",
        "cancel": "Cancel",
        "confirm": "Confirm",
        "close": "Close",
        "start_analysis": "Start Analysis",
        "new_analysis": "Start New Analysis",
        "processing_data": "Processing data...",
        "no_data_for_selection": "No data available for the selected combination.",
        "show_all": "Show all",
        "number_of_entries": "Number of entries",
        
        # === DEBUG & UI HELPERS ===
        "current_language": "Current Language", 
        "available_languages": "Available Languages",
        "session_state_keys": "Session State Keys",
        "debug_info": "Debug Information"
    }
}

def init_language():
    """Initialisiert die Sprache im Session State"""
    if "language" not in st.session_state:
        st.session_state.language = "DE"  # Standard: Deutsch

def get_text(key, default=None):
    """
    Holt den übersetzten Text für den aktuellen Sprachschlüssel
    
    Args:
        key: Der Übersetzungsschlüssel
        default: Fallback-Text wenn Schlüssel nicht gefunden wird
    
    Returns:
        Übersetzter Text oder Fallback
    """
    if default is None:
        default = key  # Schlüssel als Fallback verwenden
    
    return TRANSLATIONS[st.session_state.language].get(key, default)

def t(key, default=None):
    """Kurze Alias-Funktion für get_text"""
    return get_text(key, default)