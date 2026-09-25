import streamlit as st
import warnings
import logging
from utils.check_dependencies import is_bertopic_available
from models.pipeline_adapters import AllScoresPipeline

# Unterdrücke PyTorch-Warnungen bezüglich '__path__._path'
warnings.filterwarnings("ignore", message=".*Tried to instantiate class '__path__._path'.*")

# Reduziere das Log-Level für Transformers-Bibliothek
logging.getLogger("transformers").setLevel(logging.ERROR)

# Gecachte Modelle verfallen 30 Min. nach dem Laden (Review M3; Streamlit-ttl zaehlt ab dem Laden);
# Neuladen kostet ca. 14 s (MESS1). Die kostenlose Streamlit-Cloud hat wenig RAM.
MODEL_TTL_SECONDS = 1800

# transformers/torch werden erst beim ersten Laden eines Modells importiert
# (nicht schon beim Seitenaufruf) – spart Zeit und Arbeitsspeicher, solange
# niemand eine Live-Analyse startet.


@st.cache_resource(show_spinner=False, ttl=MODEL_TTL_SECONDS)
def load_sentiment_model():
    """
    Lädt das Sentiment-Analyse-Modell
    """
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    model_name = "oliverguhr/german-sentiment-bert"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


@st.cache_resource(show_spinner=False, ttl=MODEL_TTL_SECONDS)
def load_emotion_model():
    """
    Lädt das Emotions-Analyse-Modell (deutsch).
    Rueckgabe: AllScoresPipeline – liefert immer alle Emotions-Scores
    (return_all_scores wirkt in transformers 5.x nicht mehr, siehe pipeline_adapters.py).
    """
    # Fehler werden NICHT abgefangen (Review M2): unter cache_resource wuerde sonst None
    # gecacht und das Modell bis zum Neustart der App nie wieder geladen.
    from transformers import pipeline
    emotion_classifier = pipeline("text-classification",
                                  model="visegradmedia-emotion/Emotion_RoBERTa_german6_v7")
    return AllScoresPipeline(emotion_classifier)


@st.cache_resource(show_spinner=False, ttl=MODEL_TTL_SECONDS)
def load_embedding_model():
    """Satz-Embedding-Modell fuer BERTopic (einmal laden, von allen Laeufen geteilt)."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("distiluse-base-multilingual-cased-v1")


def load_bertopic_model():
    """
    Erstellt das BERTopic-Modell mit angepassten Parametern.
    Jeder Aufruf liefert ein NEUES BERTopic-Objekt (nicht gecacht): fit_transform veraendert
    das Objekt, ein geteiltes Objekt wuerde sonst von gleichzeitigen Laeufen ueberschrieben.
    Nur das Embedding-Modell wird geteilt.
    """
    if not is_bertopic_available():
        return None

    try:
        from bertopic import BERTopic

        try:
            from hdbscan import HDBSCAN
        except ImportError:
            st.warning("HDBSCAN konnte nicht importiert werden. Standardparameter werden verwendet.")
            HDBSCAN = None

        embedding_model = load_embedding_model()

        if HDBSCAN is not None:
            hdbscan_model = HDBSCAN(
                min_cluster_size=5,
                min_samples=2,
                metric='euclidean',
                cluster_selection_method='eom',
                prediction_data=True
            )
            topic_model = BERTopic(
                embedding_model=embedding_model,
                language="german",
                hdbscan_model=hdbscan_model,
                nr_topics="auto"
            )
        else:
            topic_model = BERTopic(embedding_model=embedding_model, language="german")

        return topic_model
    except Exception as e:
        st.error(f"Fehler beim Laden des BERTopic-Modells: {str(e)}")
        return None


def clear_models() -> None:
    """Gibt alle gecachten Modelle dieser Sprache frei (vor dem Laden der anderen Sprache, Review M3)."""
    for loader in (load_sentiment_model, load_emotion_model, load_embedding_model):
        try:
            loader.clear()
        except Exception:  # noqa: BLE001
            pass
