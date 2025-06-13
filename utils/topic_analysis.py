import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import re
import ast
from wordcloud import WordCloud
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from collections import Counter
import traceback

# Relative Imports - modernisiert
try:
    from ..models.model_loader import load_bertopic_model
    from .topic_labeling import generate_smart_topic_labels
except ImportError:
    # Fallback für direkten Import (Kompatibilität)
    try:
        from models.model_loader import load_bertopic_model
        from utils.topic_labeling import generate_smart_topic_labels
    except ImportError:
        load_bertopic_model = None
        generate_smart_topic_labels = None

# ==========================================
# 📊 KONSTANTEN (statt Magic Numbers)
# ==========================================

# Text Processing
MIN_TEXT_LENGTH_FOR_TOPIC: int = 10
MIN_COMMENTS_FOR_ANALYSIS: int = 10
DEFAULT_N_WORDS: int = 5
DEFAULT_LABEL_WORDS: int = 3
MAX_LABEL_WORDS: int = 5
MIN_LABEL_WORDS: int = 1

# Topic Analysis Configuration
OUTLIER_TOPIC_ID: int = -1
DEFAULT_TOP_TOPICS: int = 10
MAX_TOP_TOPICS_WORDCLOUD: int = 5
WORDCLOUD_WIDTH: int = 400
WORDCLOUD_HEIGHT: int = 400

# UI Configuration
TOPIC_DICT_HEIGHT: int = 300
CHART_HEIGHT: int = 500
LARGE_CHART_HEIGHT: int = 600

# German Stopwords (fallback)
GERMAN_STOPWORDS_FALLBACK: List[str] = [
    'und', 'der', 'die', 'das', 'ist', 'ich', 'zu', 'auf', 'ein', 'eine', 'mit', 
    'nicht', 'es', 'sich', 'auch', 'als', 'an', 'nach', 'wie', 'im', 'für',
    'man', 'aber', 'aus', 'durch', 'wenn', 'nur', 'war', 'noch', 'werden',
    'bei', 'hat', 'wir', 'was', 'wird', 'sein', 'einen', 'oder', 'zur', 'um',
    'haben', 'einer', 'er', 'über', 'sie', 'so', 'bis', 'mehr', 'diese',
    'einem', 'seit', 'ohne', 'ihn', 'wo', 'vor', 'einer', 'zwischen', 'immer'
]

# Sentiment Colors
SENTIMENT_COLORS: Dict[str, str] = {
    'positive': '#4CAF50',  # Green
    'neutral': '#9E9E9E',   # Gray  
    'negative': '#F44336'   # Red
}

# ==========================================
# 🎛️ DATA CLASSES
# ==========================================

@dataclass
class TopicAnalysisConfig:
    """Konfiguration für Topic-Analyse"""
    min_text_length: int = MIN_TEXT_LENGTH_FOR_TOPIC
    min_comments: int = MIN_COMMENTS_FOR_ANALYSIS
    n_keywords: int = DEFAULT_N_WORDS
    label_words: int = DEFAULT_LABEL_WORDS
    top_topics_display: int = DEFAULT_TOP_TOPICS

@dataclass
class TopicInfo:
    """Information über ein einzelnes Topic"""
    topic_id: int
    count: int
    name: str
    keywords: str
    smart_label: str
    custom_label: Optional[str] = None
    
    @property
    def display_label(self) -> str:
        """Gibt das beste verfügbare Label zurück"""
        return self.custom_label or self.smart_label or self.name or f"Topic {self.topic_id}"

@dataclass
class TopicAnalysisResult:
    """Ergebnis der Topic-Analyse"""
    topic_model: Any
    topic_info_df: pd.DataFrame
    topic_labels: Dict[int, str]
    processed_df: pd.DataFrame
    topics_list: List[TopicInfo]
    
    @property
    def valid_topics(self) -> List[TopicInfo]:
        """Gibt Topics ohne Outlier zurück"""
        return [topic for topic in self.topics_list if topic.topic_id != OUTLIER_TOPIC_ID]

@dataclass
class WordCloudData:
    """Daten für WordCloud"""
    topic_id: int
    word_frequencies: Dict[str, float]
    label: str

@dataclass
class SentimentByTopicData:
    """Sentiment-Daten pro Topic"""
    topic_sentiment_counts: pd.DataFrame
    topic_sentiment_percentages: pd.DataFrame
    display_labels: Dict[int, str]

# ==========================================
# 🔬 TEXT PROCESSING FUNCTIONS
# ==========================================

def clean_text_for_topics(text: str) -> str:
    """
    🎯 MODERNISIERT: Text für die Themenanalyse bereinigen
    
    Args:
        text: Zu bereinigender Text
        
    Returns:
        Bereinigter Text
    """
    if not _validate_text_input(text):
        return ""
    
    text_str = str(text)
    
    # URL-Entfernung
    text_str = re.sub(r'http\S+', '', text_str)
    
    # Sonderzeichen und Zahlen entfernen
    text_str = re.sub(r'[^\w\s]', '', text_str)
    text_str = re.sub(r'\d+', '', text_str)
    
    # Kleinbuchstaben
    text_str = text_str.lower()
    
    # Stopwort-Entfernung
    return _remove_stopwords(text_str)

def _validate_text_input(text: Any) -> bool:
    """Validiert Text-Input"""
    return not (pd.isna(text) or text is None or text == "")

def _remove_stopwords(text: str) -> str:
    """Entfernt Stopwörter aus Text"""
    try:
        stopwords = _get_german_stopwords()
        words = [word for word in text.split() 
                if word not in stopwords and len(word) > 2]
        return ' '.join(words)
    except Exception:
        # Fallback: nur kurze Wörter filtern
        words = [word for word in text.split() if len(word) > 2]
        return ' '.join(words)

def _get_german_stopwords() -> set:
    """Holt deutsche Stopwörter"""
    try:
        import nltk
        from nltk.corpus import stopwords
        
        # Prüfe ob Stopwords verfügbar sind
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        return set(stopwords.words('german'))
    except Exception:
        # Fallback zu manueller Liste
        return set(GERMAN_STOPWORDS_FALLBACK)

# ==========================================
# 🔍 TOPIC MODEL FUNCTIONS
# ==========================================

def get_topic_keywords(topic_id: int, topic_model: Any, n_words: int = DEFAULT_N_WORDS) -> str:
    """
    🎯 MODERNISIERT: Holt die Top-Wörter für ein bestimmtes Thema
    
    Args:
        topic_id: ID des Topics
        topic_model: BERTopic Model
        n_words: Anzahl der Wörter
        
    Returns:
        Komma-separierte Keywords
    """
    try:
        words = topic_model.get_topic(topic_id)
        if not words:
            return f"Topic {topic_id}"
        return ", ".join([word for word, _ in words[:n_words]])
    except Exception as e:
        return f"Fehler: {str(e)}"

def generate_topic_label_from_words(topic_id: int, topic_model: Any, n_words: int = DEFAULT_LABEL_WORDS) -> str:
    """
    🎯 MODERNISIERT: Erzeugt ein Label für ein Thema basierend auf den Top-Wörtern
    
    Args:
        topic_id: ID des Topics
        topic_model: BERTopic Model  
        n_words: Anzahl der Wörter für Label
        
    Returns:
        Topic-Label
    """
    try:
        top_words = topic_model.get_topic(topic_id)
        if not top_words:
            return "Sonstiges"
        return " / ".join([word for word, _ in top_words[:n_words]])
    except Exception:
        return f"Topic {topic_id}"

def create_wordcloud_data(topic_id: int, topic_model: Any, label: str) -> Optional[WordCloudData]:
    """
    🎯 MODERNISIERT: Bereitet WordCloud-Daten vor
    
    Args:
        topic_id: ID des Topics
        topic_model: BERTopic Model
        label: Label für das Topic
        
    Returns:
        WordCloudData oder None
    """
    try:
        words = topic_model.get_topic(topic_id)
        if not words:
            return None
            
        word_frequencies = {word: weight for word, weight in words}
        
        return WordCloudData(
            topic_id=topic_id,
            word_frequencies=word_frequencies,
            label=label
        )
    except Exception as e:
        st.error(f"Fehler bei der WordCloud-Vorbereitung für Topic {topic_id}: {str(e)}")
        return None

def generate_wordcloud_from_data(wordcloud_data: WordCloudData) -> Optional[WordCloud]:
    """
    🎯 BUSINESS: Erzeugt WordCloud aus Daten
    
    Args:
        wordcloud_data: WordCloud-Daten
        
    Returns:
        WordCloud-Objekt oder None
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
        st.error(f"Fehler bei der WordCloud-Generierung: {str(e)}")
        return None

# ==========================================
# 🔬 BUSINESS LOGIC FUNCTIONS
# ==========================================

def prepare_data_for_topic_analysis(df: pd.DataFrame, text_column: str, config: TopicAnalysisConfig) -> pd.DataFrame:
    """
    🎯 BUSINESS: Bereitet Daten für Topic-Analyse vor
    
    Args:
        df: Original DataFrame
        text_column: Name der Text-Spalte
        config: Analyse-Konfiguration
        
    Returns:
        Vorbereiteter DataFrame
    """
    # Text bereinigen
    df['clean_text'] = df[text_column].apply(clean_text_for_topics)
    
    # Gültige Texte filtern
    topic_df = df[df['clean_text'].str.len() > config.min_text_length].reset_index(drop=True)
    
    return topic_df

def train_topic_model(texts: List[str]) -> Optional[Any]:
    """
    🎯 BUSINESS: Trainiert Topic-Model
    
    Args:
        texts: Liste von Texten
        
    Returns:
        Trainiertes Topic-Model oder None
    """
    if load_bertopic_model is None:
        st.error("BERTopic-Model Loader nicht verfügbar")
        return None
    
    try:
        topic_model = load_bertopic_model()
        if topic_model is None:
            return None
        
        # Modell trainieren
        topics, probs = topic_model.fit_transform(texts)
        return topic_model
    except Exception as e:
        st.error(f"Fehler beim Training des BERTopic-Modells: {str(e)}")
        st.error(traceback.format_exc())
        return None

def extract_topic_information(topic_model: Any, config: TopicAnalysisConfig) -> Tuple[pd.DataFrame, Dict[int, str], List[TopicInfo]]:
    """
    🎯 BUSINESS: Extrahiert Topic-Informationen
    
    Args:
        topic_model: Trainiertes Topic-Model
        config: Analyse-Konfiguration
        
    Returns:
        Tuple von (topic_info_df, topic_labels, topics_list)
    """
    # Basis-Info vom Model
    topic_info = topic_model.get_topic_info()
    
    # Smart Labels generieren
    if generate_smart_topic_labels is not None:
        try:
            smart_labels = generate_smart_topic_labels(topic_model)
        except Exception as e:
            st.warning(f"Smart Labels konnten nicht generiert werden: {str(e)}")
            smart_labels = {}
    else:
        smart_labels = {}
    
    # TopicInfo-Objekte erstellen
    topics_list = []
    for _, row in topic_info.iterrows():
        topic_id = row['Topic']
        
        topic_obj = TopicInfo(
            topic_id=topic_id,
            count=row['Count'],
            name=row['Name'],
            keywords=get_topic_keywords(topic_id, topic_model, config.n_keywords),
            smart_label=smart_labels.get(topic_id, f"Topic {topic_id}")
        )
        topics_list.append(topic_obj)
    
    # Labels-Dictionary erstellen
    topic_labels = {topic.topic_id: topic.smart_label for topic in topics_list}
    
    return topic_info, topic_labels, topics_list

def calculate_sentiment_by_topic(df: pd.DataFrame, topic_labels: Dict[int, str]) -> Optional[SentimentByTopicData]:
    """
    🎯 BUSINESS: Berechnet Sentiment pro Topic
    
    Args:
        df: DataFrame mit Topics und Sentiment
        topic_labels: Topic-Labels
        
    Returns:
        SentimentByTopicData oder None
    """
    if 'sentiment' not in df.columns or 'topic' not in df.columns:
        return None
    
    try:
        # Outliers ignorieren
        topic_sentiment_df = df[df['topic'] != OUTLIER_TOPIC_ID]
        
        if topic_sentiment_df.empty:
            return None
        
        # Sentiment pro Topic aggregieren
        sentiment_counts = topic_sentiment_df.groupby('topic')['sentiment'].value_counts().unstack().fillna(0)
        sentiment_percentages = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0) * 100
        
        # Display-Labels erstellen
        display_labels = {}
        if hasattr(st.session_state, 'combined_topic_labels'):
            display_labels = st.session_state.combined_topic_labels
        else:
            display_labels = topic_labels
        
        return SentimentByTopicData(
            topic_sentiment_counts=sentiment_counts,
            topic_sentiment_percentages=sentiment_percentages,
            display_labels=display_labels
        )
        
    except Exception as e:
        st.error(f"Fehler bei der Sentiment-pro-Topic-Analyse: {str(e)}")
        return None

def parse_topic_dictionary(dict_string: str) -> Optional[Dict[int, str]]:
    """
    🎯 BUSINESS: Parst Topic-Dictionary String
    
    Args:
        dict_string: String mit Dictionary-Inhalt
        
    Returns:
        Geparste Dictionary oder None
    """
    try:
        parsed_dict = ast.literal_eval(dict_string)
        
        if not isinstance(parsed_dict, dict):
            return None
        
        # Konvertiere alle Keys zu Integers
        return {int(k): str(v) for k, v in parsed_dict.items()}
        
    except Exception as e:
        st.error(f"Fehler beim Parsen des Dictionaries: {str(e)}")
        return None

# ==========================================
# 🎨 UI FUNCTIONS (Streamlit Components)
# ==========================================

def render_topic_overview_table(topics_list: List[TopicInfo], config: TopicAnalysisConfig) -> None:
    """
    🎯 UI: Rendert Topic-Übersichtstabelle
    """
    st.write("### Themenübersicht")
    
    # Filtere Outliers und sortiere nach Count
    valid_topics = [t for t in topics_list if t.topic_id != OUTLIER_TOPIC_ID]
    valid_topics.sort(key=lambda x: x.count, reverse=True)
    
    # Erstelle Display-DataFrame
    display_data = []
    for topic in valid_topics[:config.top_topics_display]:
        display_data.append({
            "Topic": topic.topic_id,
            "Count": topic.count,
            "Name": topic.name,
            "Top-Wörter": topic.keywords,
            "Smart Label": topic.smart_label,
            "Manuelle Bezeichnung": ""
        })
    
    if display_data:
        display_df = pd.DataFrame(display_data)
        st.dataframe(display_df)
    else:
        st.warning("Keine gültigen Topics gefunden.")

def render_wordclouds(topics_list: List[TopicInfo], topic_model: Any) -> None:
    """
    🎯 UI: Rendert WordClouds für Top-Topics
    """
    st.write("### WordClouds für Top-Themen")
    
    # Top Topics ohne Outliers
    valid_topics = [t for t in topics_list if t.topic_id != OUTLIER_TOPIC_ID]
    valid_topics.sort(key=lambda x: x.count, reverse=True)
    top_topics = valid_topics[:MAX_TOP_TOPICS_WORDCLOUD]
    
    if not top_topics:
        st.warning("Keine Topics für WordClouds verfügbar.")
        return
    
    # Erstelle Spalten für WordClouds
    cols = st.columns(min(len(top_topics), MAX_TOP_TOPICS_WORDCLOUD))
    
    for i, topic in enumerate(top_topics):
        with cols[i % len(cols)]:
            st.write(f"**{topic.display_label}**")
            
            # WordCloud-Daten vorbereiten
            wordcloud_data = create_wordcloud_data(topic.topic_id, topic_model, topic.display_label)
            
            if wordcloud_data:
                # WordCloud generieren
                wc = generate_wordcloud_from_data(wordcloud_data)
                
                if wc:
                    # WordCloud anzeigen
                    fig, ax = plt.subplots(figsize=(4, 4))
                    ax.imshow(wc, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
                    plt.close(fig)  # Memory cleanup

def render_topic_label_suggestions(topics_list: List[TopicInfo], topic_model: Any) -> None:
    """
    🎯 UI: Rendert Label-Vorschläge
    """
    st.write("### Label-Vorschläge für Themen")
    
    # Anzahl der Wörter für Labels
    label_words = st.slider(
        "Anzahl der Wörter für Label", 
        MIN_LABEL_WORDS, 
        MAX_LABEL_WORDS, 
        DEFAULT_LABEL_WORDS
    )
    
    # Erstelle Labels mit gewählter Wortanzahl
    valid_topics = [t for t in topics_list if t.topic_id != OUTLIER_TOPIC_ID]
    valid_topics.sort(key=lambda x: x.count, reverse=True)
    
    display_data = []
    for topic in valid_topics:
        new_label = generate_topic_label_from_words(topic.topic_id, topic_model, label_words)
        display_data.append({
            "Topic": topic.topic_id,
            "Count": topic.count,
            "Label-Vorschlag": new_label,
            "Smart Label": topic.smart_label
        })
    
    if display_data:
        labels_df = pd.DataFrame(display_data)
        st.dataframe(labels_df)

def render_predefined_topic_dictionary(topic_labels: Dict[int, str]) -> None:
    """
    🎯 UI: Rendert vordefiniertes Topic-Dictionary
    """
    st.write("### Vordefiniertes Topic-Dictionary")
    
    # Generiere Code für Dictionary
    topic_dict_lines = ["topic_labels = {"]
    for topic_id in sorted(topic_labels.keys()):
        if topic_id != OUTLIER_TOPIC_ID:
            topic_dict_lines.append(f"    {topic_id}: \"{topic_labels[topic_id]}\",")
    topic_dict_lines.append("}")
    
    topic_dict_str = "\n".join(topic_dict_lines)
    
    # Code anzeigen
    st.code(topic_dict_str, language='python')
    
    return topic_dict_str

def render_topic_dictionary_editor(default_dict_str: str) -> None:
    """
    🎯 UI: Rendert Topic-Dictionary Editor
    """
    # Text-Editor für Dictionary
    user_dict_str = st.text_area(
        "Topic-Dictionary eingeben (Python-Format):", 
        value=default_dict_str, 
        height=TOPIC_DICT_HEIGHT
    )
    
    if st.button("Topic-Dictionary übernehmen"):
        parsed_dict = parse_topic_dictionary(user_dict_str)
        
        if parsed_dict:
            st.session_state.custom_topic_labels = parsed_dict
            st.success("Topic-Dictionary erfolgreich übernommen!")
        else:
            st.error("Eingabe ist kein gültiges Dictionary.")

def render_manual_topic_naming(topics_list: List[TopicInfo]) -> None:
    """
    🎯 UI: Rendert manuelles Topic-Naming Interface
    """
    st.write("### Manuelle Benennung von Themen")
    st.write("Sie können hier manuell Themen benennen und diese Benennungen für weitere Analysen verwenden.")
    
    # Nur gültige Topics
    valid_topics = [t for t in topics_list if t.topic_id != OUTLIER_TOPIC_ID]
    
    if not valid_topics:
        st.warning("Keine Topics zum Benennen verfügbar.")
        return
    
    with st.form("topic_naming_form"):
        # Topic-Auswahl
        topic_options = [t.topic_id for t in valid_topics]
        
        selected_topic = st.selectbox(
            "Thema auswählen:",
            options=topic_options,
            format_func=lambda x: f"Topic {x}: {next(t.display_label for t in valid_topics if t.topic_id == x)}"
        )
        
        # Aktuelles Label finden
        current_label = ""
        if hasattr(st.session_state, 'custom_topic_labels'):
            current_label = st.session_state.custom_topic_labels.get(selected_topic, "")
        if not current_label:
            current_label = next(t.smart_label for t in valid_topics if t.topic_id == selected_topic)
        
        # Eingabefeld
        custom_label = st.text_input("Benutzerdefinierte Bezeichnung:", value=current_label)
        
        # Submit Button
        if st.form_submit_button("Bezeichnung speichern"):
            if not hasattr(st.session_state, 'custom_topic_labels'):
                st.session_state.custom_topic_labels = {}
            
            st.session_state.custom_topic_labels[selected_topic] = custom_label
            st.success(f"Bezeichnung für Topic {selected_topic} gespeichert!")

def render_saved_topic_labels(topics_list: List[TopicInfo], topic_labels: Dict[int, str]) -> None:
    """
    🎯 UI: Rendert gespeicherte Topic-Labels
    """
    if not hasattr(st.session_state, 'custom_topic_labels') or not st.session_state.custom_topic_labels:
        return
    
    st.write("### Gespeicherte Bezeichnungen")
    
    # Erstelle Display-DataFrame
    custom_labels_data = []
    valid_topics = [t for t in topics_list if t.topic_id != OUTLIER_TOPIC_ID]
    
    for topic_id, custom_label in st.session_state.custom_topic_labels.items():
        # Finde Topic-Info
        topic_obj = next((t for t in valid_topics if t.topic_id == topic_id), None)
        
        if topic_obj:
            custom_labels_data.append({
                "Topic": topic_id,
                "Label-Vorschlag": generate_topic_label_from_words(topic_id, None, DEFAULT_LABEL_WORDS),
                "Smart Label": topic_labels.get(topic_id, "Unbenannt"),
                "Benutzerdefinierte Bezeichnung": custom_label
            })
    
    if custom_labels_data:
        custom_labels_df = pd.DataFrame(custom_labels_data)
        st.dataframe(custom_labels_df)
        
        # Kombinierte Labels für Session State
        combined_labels = topic_labels.copy()
        combined_labels.update(st.session_state.custom_topic_labels)
        st.session_state.combined_topic_labels = combined_labels

def render_sentiment_by_topic_chart(sentiment_data: SentimentByTopicData) -> None:
    """
    🎯 UI: Rendert Sentiment-per-Topic Chart
    """
    st.write("### Sentiment pro Thema")
    
    # Display-Labels anwenden
    display_percentages = sentiment_data.topic_sentiment_percentages.copy()
    display_counts = sentiment_data.topic_sentiment_counts.copy()
    
    # Labels für Index setzen
    new_index = [sentiment_data.display_labels.get(idx, f"Topic {idx}") 
                 for idx in display_percentages.index]
    display_percentages.index = new_index
    display_counts.index = new_index
    
    # Plotly-Visualisierung
    try:
        plot_data = []
        for topic in display_percentages.index:
            for sentiment, value in display_percentages.loc[topic].items():
                plot_data.append({
                    'Thema': topic,
                    'Sentiment': sentiment,
                    'Prozent': value
                })
        
        plot_df = pd.DataFrame(plot_data)
        
        fig = px.bar(
            plot_df,
            x='Thema',
            y='Prozent',
            color='Sentiment',
            color_discrete_map=SENTIMENT_COLORS,
            title='Sentiment-Verteilung nach Themen',
            height=LARGE_CHART_HEIGHT
        )
        
        fig.update_layout(
            xaxis_title='Thema',
            yaxis_title='Anteil (%)',
            xaxis={'categoryorder': 'total descending'}
        )
        
        st.plotly_chart(fig, use_container_width=True, key="sentiment_by_topic_chart")
        
    except Exception as e:
        st.error(f"Fehler bei der Plotly-Visualisierung: {str(e)}")
        
        # Fallback zu Matplotlib
        try:
            fig, ax = plt.subplots(figsize=(14, 7))
            display_percentages.plot(
                kind='bar', 
                stacked=True, 
                ax=ax,
                color=[SENTIMENT_COLORS.get(col, 'blue') for col in display_percentages.columns]
            )
            plt.title('Sentiment-Verteilung nach Themen')
            plt.xlabel('Thema')
            plt.ylabel('Anteil (%)')
            plt.xticks(rotation=45, ha='right')
            plt.legend(title='Sentiment')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        except Exception as fallback_error:
            st.error(f"Auch Matplotlib-Fallback fehlgeschlagen: {str(fallback_error)}")
    
    # Tabelle anzeigen
    st.write("Sentiment-Verteilung nach Themen (absolut):")
    st.dataframe(display_counts)

# ==========================================
# 🎯 MAIN API FUNCTIONS (Backward Compatible)
# ==========================================

def clean_text(text: str) -> str:
    """
    🎯 LEGACY: Backward compatible function
    Text für die Themenanalyse bereinigen
    """
    return clean_text_for_topics(text)

def get_keywords(topic_id: int, topic_model: Any, n_words: int = DEFAULT_N_WORDS) -> str:
    """
    🎯 LEGACY: Backward compatible function
    Holt die Top-Wörter für ein bestimmtes Thema
    """
    return get_topic_keywords(topic_id, topic_model, n_words)

def generate_topic_label(topic_id: int, topic_model: Any, n_words: int = DEFAULT_LABEL_WORDS) -> str:
    """
    🎯 LEGACY: Backward compatible function
    Erzeugt ein Label für ein Thema basierend auf den Top-Wörtern
    """
    return generate_topic_label_from_words(topic_id, topic_model, n_words)

def generate_wordcloud(topic_id: int, topic_model: Any) -> Optional[WordCloud]:
    """
    🎯 LEGACY: Backward compatible function
    Erzeugt eine WordCloud für ein Thema
    """
    label = get_topic_keywords(topic_id, topic_model, 3)
    wordcloud_data = create_wordcloud_data(topic_id, topic_model, label)
    
    if wordcloud_data:
        return generate_wordcloud_from_data(wordcloud_data)
    return None

def prepare_topic_analysis(df: pd.DataFrame, text_column: str) -> Tuple[pd.DataFrame, Any, Any, Any, Dict[int, str]]:
    """
    🎯 MODERNISIERT: Bereitet die Daten für die Themenanalyse vor und trainiert das Topic-Modell
    
    Args:
        df: DataFrame mit den Kommentaren
        text_column: Name der Spalte mit den Texten
        
    Returns:
        Tuple mit (df, topic_model, topic_info, topic_df, topic_labels)
    """
    config = TopicAnalysisConfig()
    
    try:
        with st.spinner("Texte werden für die Themen- und Emotionsanalyse vorbereitet..."):
            # === BUSINESS: Daten vorbereiten ===
            topic_df = prepare_data_for_topic_analysis(df, text_column, config)
            
            if len(topic_df) < config.min_comments:
                st.warning(f"Zu wenige Kommentare für eine sinnvolle Themenanalyse. Es werden mindestens {config.min_comments} längere Kommentare benötigt.")
                return df, None, None, None, None
            
            # === BUSINESS: Topic-Model trainieren ===
            with st.spinner("BERTopic-Modell wird trainiert..."):
                topic_model = train_topic_model(topic_df['clean_text'].tolist())
                
                if topic_model is None:
                    st.warning("BERTopic-Modell konnte nicht geladen werden. Die thematische Analyse wird übersprungen.")
                    return df, None, None, None, None
                
                # Topics zuweisen
                topics, _ = topic_model.fit_transform(topic_df['clean_text'])
                topic_df['topic'] = topics
                
                # Topics zurück in Original-DataFrame übertragen
                topic_map = dict(zip(topic_df.index, topic_df['topic']))
                df['topic'] = df.index.map(lambda x: topic_map.get(x, OUTLIER_TOPIC_ID))
                
                # === BUSINESS: Topic-Informationen extrahieren ===
                topic_info, topic_labels, topics_list = extract_topic_information(topic_model, config)
                
                return df, topic_model, topic_info, topic_df, topic_labels
                
    except Exception as e:
        st.error(f"Fehler bei der Vorbereitung der Themenanalyse: {str(e)}")
        st.error(traceback.format_exc())
        return df, None, None, None, None

def display_topic_analysis(df: pd.DataFrame, topic_model: Any, topic_df: pd.DataFrame, topic_info: pd.DataFrame, topic_labels: Dict[int, str]) -> None:
    """
    🎯 MODERNISIERT: Zeigt die Ergebnisse der Themenanalyse an
    
    Args:
        df: DataFrame mit den Kommentaren
        topic_model: Trainiertes BERTopic-Modell
        topic_df: DataFrame mit den Themen
        topic_info: Themeninformationen
        topic_labels: Dictionary mit Themen-Labels
    """
    st.subheader("Themen-Analyse mit BERTopic")
    
    if topic_model is None or topic_df is None or topic_info is None:
        st.warning("Themenanalyse konnte nicht durchgeführt werden.")
        return
    
    config = TopicAnalysisConfig()
    
    # === BUSINESS: Topic-Informationen extrahieren ===
    _, _, topics_list = extract_topic_information(topic_model, config)
    
    # === UI: Topic-Übersicht ===
    render_topic_overview_table(topics_list, config)
    
    # === UI: WordClouds ===
    render_wordclouds(topics_list, topic_model)
    
    # === UI: Label-Vorschläge ===
    render_topic_label_suggestions(topics_list, topic_model)
    
    # === UI: Vordefiniertes Dictionary ===
    default_dict_str = render_predefined_topic_dictionary(topic_labels)
    
    # === UI: Dictionary Editor ===
    render_topic_dictionary_editor(default_dict_str)
    
    # === UI: Manuelles Naming ===
    render_manual_topic_naming(topics_list)
    
    # === UI: Gespeicherte Labels ===
    render_saved_topic_labels(topics_list, topic_labels)
    
    # === UI: Sentiment pro Topic ===
    display_sentiment_by_topic(df, topic_labels)

def display_sentiment_by_topic(df: pd.DataFrame, topic_labels: Dict[int, str]) -> None:
    """
    🎯 MODERNISIERT: Zeigt die Sentiment-Verteilung pro Topic an
    
    Args:
        df: DataFrame mit Topics und Sentiment
        topic_labels: Topic-Labels Dictionary
    """
    # === BUSINESS: Sentiment-Daten berechnen ===
    sentiment_data = calculate_sentiment_by_topic(df, topic_labels)
    
    if sentiment_data is None:
        st.warning("Sentiment- oder Topic-Informationen fehlen für diese Analyse.")
        return
    
    # === UI: Chart anzeigen ===
    render_sentiment_by_topic_chart(sentiment_data)

# ==========================================
# 📊 EXPORT
# ==========================================

__all__ = [
    # Main API Functions (Backward Compatible)
    'clean_text',
    'get_keywords', 
    'generate_topic_label',
    'generate_wordcloud',
    'prepare_topic_analysis',
    'display_topic_analysis',
    'display_sentiment_by_topic',
    
    # New Classes and Functions
    'TopicAnalysisConfig',
    'TopicInfo',
    'TopicAnalysisResult',
    'WordCloudData',
    'SentimentByTopicData',
    'clean_text_for_topics',
    'get_topic_keywords',
    
    # Constants
    'MIN_TEXT_LENGTH_FOR_TOPIC',
    'MIN_COMMENTS_FOR_ANALYSIS',
    'DEFAULT_N_WORDS',
    'OUTLIER_TOPIC_ID'
]