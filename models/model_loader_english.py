import streamlit as st
import warnings
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from utils.check_dependencies import is_bertopic_available

# Suppress PyTorch warnings regarding '__path__._path'
warnings.filterwarnings("ignore", message=".*Tried to instantiate class '__path__._path'.*")

# Reduce log level for transformers library
logging.getLogger("transformers").setLevel(logging.ERROR)

@st.cache_resource
def load_sentiment_model():
    """
    Loads the English sentiment analysis model
    """
    # Using a robust English sentiment model
    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

@st.cache_resource
def load_emotion_model():
    """
    Loads the English emotion analysis model
    """
    try:
        # Load emotion classification pipeline (English model)
        emotion_classifier = pipeline("text-classification", 
                                     model="j-hartmann/emotion-english-distilroberta-base", 
                                     return_all_scores=True)
        return emotion_classifier
    except Exception as e:
        st.error(f"Error loading emotion recognition model: {str(e)}")
        return None

@st.cache_resource
def load_bertopic_model():
    """
    Loads the BERTopic model with adjusted parameters for English
    """
    if not is_bertopic_available():
        return None
    
    try:
        from sentence_transformers import SentenceTransformer
        from bertopic import BERTopic
        
        # Imports for adjusted parameters
        try:
            from hdbscan import HDBSCAN
        except ImportError:
            st.warning("HDBSCAN could not be imported. Default parameters will be used.")
            HDBSCAN = None
        
        # English-optimized sentence transformer model
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # BERTopic with adjusted parameters for more topics
        if HDBSCAN is not None:
            # HDBSCAN with adjusted parameters
            hdbscan_model = HDBSCAN(
                min_cluster_size=5,  # Allow smaller clusters
                min_samples=2,       # Fewer samples needed per cluster
                metric='euclidean',
                cluster_selection_method='eom',
                prediction_data=True
            )
            
            # BERTopic with adjusted parameters
            topic_model = BERTopic(
                embedding_model=embedding_model,
                language="english",
                hdbscan_model=hdbscan_model,
                nr_topics="auto"  # Automatic topic count
            )
        else:
            # Fallback to default parameters
            topic_model = BERTopic(embedding_model=embedding_model, language="english")
            
        return topic_model
    except Exception as e:
        st.error(f"Error loading BERTopic model: {str(e)}")
        return None