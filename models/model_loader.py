import streamlit as st
import warnings
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from utils.check_dependencies import is_bertopic_available

# Unterdrücke PyTorch-Warnungen bezüglich '__path__._path'
warnings.filterwarnings("ignore", message=".*Tried to instantiate class '__path__._path'.*")

# Reduziere das Log-Level für Transformers-Bibliothek
logging.getLogger("transformers").setLevel(logging.ERROR)

@st.cache_resource
def load_sentiment_model():
    """
    Lädt das Sentiment-Analyse-Modell
    """
    model_name = "oliverguhr/german-sentiment-bert"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

@st.cache_resource
def load_emotion_model():
    """
    Lädt das Emotions-Analyse-Modell
    """
    try:
        # Emotionserkennungs-Pipeline laden (deutsches Modell)
        emotion_classifier = pipeline("text-classification", 
                                     model="visegradmedia-emotion/Emotion_RoBERTa_german6_v7", 
                                     return_all_scores=True)
        return emotion_classifier
    except Exception as e:
        st.error(f"Fehler beim Laden des Emotionserkennungsmodells: {str(e)}")
        return None

@st.cache_resource
def load_bertopic_model():
    """
    Lädt das BERTopic-Modell mit angepassten Parametern
    """
    if not is_bertopic_available():
        return None
    
    try:
        from sentence_transformers import SentenceTransformer
        from bertopic import BERTopic
        
        # Imports für angepasste Parameter
        try:
            from hdbscan import HDBSCAN
        except ImportError:
            st.warning("HDBSCAN konnte nicht importiert werden. Standardparameter werden verwendet.")
            HDBSCAN = None
        
        # Multilinguales Modell (gut für deutsche Texte)
        embedding_model = SentenceTransformer("distiluse-base-multilingual-cased-v1")
        
        # BERTopic mit angepassten Parametern für mehr Themen
        if HDBSCAN is not None:
            # HDBSCAN mit angepassten Parametern
            hdbscan_model = HDBSCAN(
                min_cluster_size=5,  # Kleinere Cluster erlauben
                min_samples=2,       # Weniger Samples pro Cluster benötigt
                metric='euclidean',
                cluster_selection_method='eom',
                prediction_data=True
            )
            
            # BERTopic mit angepassten Parametern
            topic_model = BERTopic(
                embedding_model=embedding_model,
                language="german",
                hdbscan_model=hdbscan_model,
                nr_topics="auto"  # Automatische Themenanzahl
            )
        else:
            # Fallback zu Standardparametern
            topic_model = BERTopic(embedding_model=embedding_model, language="german")
            
        return topic_model
    except Exception as e:
        st.error(f"Fehler beim Laden des BERTopic-Modells: {str(e)}")
        return None